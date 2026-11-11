"""
Advanced Racing Physics Engine - Track-Aware Agent-Based Simulation

This module implements a sophisticated racing simulation that uses:
1. Track corner analysis and racing lines
2. Overtaking opportunity zones based on track geometry
3. Defensive positioning and blocking
4. All 50+ driver attributes properly weighted
5. Real-time spatial combat (side-by-side, slipstream, divebombs)

Authors: Eoin Fitzsimons
Date: December 2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np

from momentum.database.models import Driver, Track
from momentum.services.driver_attributes import get_safe_attribute


class TrackSection(Enum):
    """Type of track section"""

    STRAIGHT = "straight"
    SLOW_CORNER = "slow_corner"  # < 80 km/h
    MEDIUM_CORNER = "medium_corner"  # 80-150 km/h
    FAST_CORNER = "fast_corner"  # > 150 km/h
    BRAKING_ZONE = "braking_zone"
    ACCELERATION_ZONE = "acceleration_zone"


class RacingLine(Enum):
    """Racing line position"""

    IDEAL = "ideal"  # Optimal racing line
    DEFENSIVE = "defensive"  # Inside line to defend
    ATTACKING = "attacking"  # Alternative line for overtaking
    OFF_LINE = "off_line"  # Sub-optimal line (dirty, less grip)


@dataclass
class TrackCorner:
    """
    Detailed corner analysis for racing simulation

    Each corner has multiple racing lines and overtaking characteristics.
    """

    corner_number: int
    position_m: float  # Distance from start line
    radius_m: float  # Corner radius
    angle_deg: float  # Corner angle (degrees)
    direction: str  # "left" or "right"

    # Speed characteristics
    entry_speed_kmh: float  # Typical entry speed
    apex_speed_kmh: float  # Speed at apex
    exit_speed_kmh: float  # Speed on exit

    # Overtaking potential
    has_overtaking_opportunity: bool
    overtaking_difficulty: float  # 0.0-1.0 (0=easy, 1=impossible)
    defensive_line_advantage: float  # Advantage for inside line

    # Track conditions
    grip_level: float = 1.0  # 0.0-1.0 (1.0 = perfect grip)
    runoff_area: bool = True  # Safe runoff if mistake
    barrier_proximity_m: float = 5.0  # Distance to barriers

    def get_ideal_line_speed(self, driver: Driver, tyre_condition: float) -> float:
        """Calculate optimal corner speed for driver"""
        # Base corner speed
        base_speed = self.apex_speed_kmh

        # Driver skill influence (use canonical attributes only)
        # Prefer `racecraft` as the primary skill, with consistency,
        # setup knowledge and reactions contributing to cornering.
        racecraft = get_safe_attribute(driver, "racecraft") / 100.0
        consistency = get_safe_attribute(driver, "consistency") / 100.0
        setup = get_safe_attribute(driver, "setup_knowledge") / 100.0
        reactions = get_safe_attribute(driver, "reactions") / 100.0

        skill_factor = (
            0.50 * racecraft + 0.25 * consistency + 0.15 * setup + 0.10 * reactions
        )

        # Corner-specific adjustments using canonical attributes
        # Hairpins reward racecraft/precision; fast corners reward consistency
        if self.angle_deg > 120:  # Hairpin
            skill_factor *= 1.0 + (racecraft / 2.0)
        elif self.radius_m > 100:  # Fast corner
            skill_factor *= 1.0 + (consistency / 2.0)

        # Tyre degradation impact
        tyre_factor = 0.7 + (0.3 * tyre_condition)

        # Grip level
        grip_factor = self.grip_level

        return base_speed * (0.85 + 0.15 * skill_factor) * tyre_factor * grip_factor


@dataclass
class TrackMap:
    """
    Complete track analysis for racing simulation

    Breaks track into sectors with corner analysis, overtaking zones,
    and racing line options.
    """

    track: Track
    corners: List[TrackCorner] = field(default_factory=list)
    drs_zones: List[Tuple[float, float]] = field(
        default_factory=list
    )  # (start_m, end_m)
    # Whether the cars in this race may open the wing: a rule of the discipline
    # and the tier (``RaceFormat.allows_drs``). The circuit only records where
    # its zones are; a field that may not use DRS races with none.
    drs_allowed: bool = True

    CORNER_RADIUS_M = 50.0  # within this of a corner's position the car is in the corner
    STRAIGHT_CLEARANCE_M = 150.0  # beyond this of any corner the section is a straight

    def __post_init__(self):
        """Generate track map from Track data"""
        if not self.corners:
            self._generate_corners()
        if not self.drs_allowed:
            self.drs_zones = []
        elif not self.drs_zones and self.track.drs_zones > 0:
            self._generate_drs_zones()

    def _generate_corners(self):
        """Generate corner analysis from track data"""
        self._generate_corners_impl()

    def _generate_corners_impl(self):
        """Implementation body extracted to keep entrypoint complexity low."""
        track_length_m = self.track.length_km * 1000
        num_corners = max(1, int(self.track.turns or 0))
        rng = np.random.default_rng(seed=42)  # Create random generator with seed

        # The start/finish straight is the circuit's longest; the corners share
        # the rest of the lap evenly, so the stored straight exists in the model.
        main_straight_m = min(
            max(0.0, float(self.track.longest_straight_m or 0.0)), 0.5 * track_length_m
        )
        corner_span_m = track_length_m - main_straight_m

        for i in range(num_corners):
            position_m = main_straight_m + (i / num_corners) * corner_span_m

            # Vary corner types based on track characteristics
            corner_type = self._determine_corner_type(i, num_corners)
            radius_m, apex_speed_kmh, overtaking_diff = self._corner_characteristics(
                corner_type, rng
            )

            # Direction (alternate with bias from track data)
            direction = (
                "left"
                if (i % 2 == 0 and self.track.left_turns >= self.track.right_turns)
                else "right"
            )

            # Angle based on corner type
            if corner_type == "medium":
                angle_deg = 90
            elif corner_type == "fast":
                angle_deg = 45
            else:
                angle_deg = 120

            grip_level_val = self._resolve_track_grip_level()

            corner = TrackCorner(
                corner_number=i + 1,
                position_m=position_m,
                radius_m=radius_m,
                angle_deg=angle_deg,
                direction=direction,
                entry_speed_kmh=apex_speed_kmh * 1.3,
                apex_speed_kmh=apex_speed_kmh,
                exit_speed_kmh=apex_speed_kmh * 1.2,
                has_overtaking_opportunity=(overtaking_diff < 0.5),
                overtaking_difficulty=overtaking_diff,
                defensive_line_advantage=0.2 if overtaking_diff < 0.5 else 0.4,
                grip_level=grip_level_val,
            )

            self.corners.append(corner)

    def _corner_characteristics(
        self, corner_type: str, rng
    ) -> Tuple[float, float, float]:
        """Return (radius_m, apex_speed_kmh, overtaking_difficulty) for corner class."""
        if corner_type == "slow":
            radius_m = self.track.tightest_corner_radius_m * rng.uniform(0.8, 1.2)
            return radius_m, self.track.avg_speed_kmh * 0.4, 0.3
        if corner_type == "medium":
            radius_m = self.track.tightest_corner_radius_m * rng.uniform(2.0, 4.0)
            return radius_m, self.track.avg_speed_kmh * 0.7, 0.6
        radius_m = self.track.tightest_corner_radius_m * rng.uniform(5.0, 10.0)
        return radius_m, self.track.avg_speed_kmh * 0.85, 0.9

    def _resolve_track_grip_level(self) -> float:
        """Resolve normalized grip level from explicit or surface-derived values."""
        raw_surface_grip = getattr(self.track, "surface_grip", None)
        if raw_surface_grip is not None:
            try:
                if raw_surface_grip > 1.0:
                    return min(1.0, float(raw_surface_grip) / 20.0)
                return float(raw_surface_grip)
            except Exception:
                return 1.0

        surface_name = getattr(self.track, "surface", "") or getattr(
            self.track, "surface_type", ""
        )
        surface_map = {
            "asphalt": 1.0,
            "tarmac": 1.0,
            "concrete": 0.95,
            "gravel": 0.6,
            "mixed": 0.75,
            "dirt": 0.55,
            "grassy": 0.65,
        }
        return surface_map.get(surface_name.lower(), 0.9)

    def _determine_corner_type(self, corner_index: int, total_corners: int) -> str:
        """Determine if corner is slow/medium/fast"""
        # Mix of corner types based on track characteristics
        ratio = corner_index / total_corners

        if self.track.avg_speed_kmh > 220:  # Fast track
            if ratio > 0.3:
                return "fast"
            elif ratio > 0.15:
                return "medium"
            else:
                return "slow"
        elif self.track.avg_speed_kmh < 160:  # Slow/twisty track
            if ratio > 0.5:
                return "slow"
            elif ratio > 0.25:
                return "medium"
            else:
                return "fast"
        else:  # Balanced
            if 0.3 < ratio < 0.7:
                return "medium"
            elif ratio < 0.3:
                return "slow"
            else:
                return "fast"

    def _generate_drs_zones(self):
        """Place the DRS zones on the longest corner-free stretches.

        A zone is the straight part of a gap between corners (clear of the
        braking and acceleration sections ``get_section_at_position`` marks),
        ends at the braking point and runs at most 80% of the longest straight.
        The stretch over the start line is stored unwrapped, so its ``end`` may
        exceed the lap length; callers compare positions modulo the lap.
        """
        track_length_m = max(1.0, float(self.track.length_km) * 1000.0)
        positions = sorted(c.position_m for c in self.corners)
        if not positions:
            return
        gaps = []
        for i, start in enumerate(positions):
            end = positions[(i + 1) % len(positions)]
            if end <= start:
                end += track_length_m
            gaps.append((end - start, start, end))
        zone_cap_m = 0.8 * float(self.track.longest_straight_m or 0.0)
        for _, corner_a, corner_b in sorted(gaps, reverse=True)[: self.track.drs_zones]:
            straight_start = corner_a + self.STRAIGHT_CLEARANCE_M
            straight_end = corner_b - self.STRAIGHT_CLEARANCE_M
            if straight_end <= straight_start:
                continue
            zone_start = max(straight_start, straight_end - zone_cap_m)
            if straight_end > zone_start:
                self.drs_zones.append((zone_start % track_length_m, straight_end - (zone_start - zone_start % track_length_m)))
        self.drs_zones.sort()

    def in_drs_zone(self, position_m: float) -> bool:
        """Whether a lap position (any lap) lies in a DRS zone, wrapping over the start line."""
        track_length_m = max(1.0, float(self.track.length_km) * 1000.0)
        return any(
            (position_m - start) % track_length_m <= end - start
            for start, end in self.drs_zones
        )

    def get_section_at_position(
        self, position_m: float
    ) -> Tuple[TrackSection, Optional[TrackCorner]]:
        """Get track section type and nearest corner at position"""
        track_length_m = max(1.0, float(self.track.length_km) * 1000.0)
        position_m = float(position_m) % track_length_m
        # Find nearest corner
        nearest_corner = None
        min_distance = float("inf")

        for corner in self.corners:
            direct_distance = abs(corner.position_m - position_m)
            distance = min(direct_distance, track_length_m - direct_distance)
            if distance < min_distance:
                min_distance = distance
                nearest_corner = corner

        # Determine section type based on proximity to corner
        if nearest_corner and min_distance < self.CORNER_RADIUS_M:
            if nearest_corner.apex_speed_kmh < 80:
                return TrackSection.SLOW_CORNER, nearest_corner
            elif nearest_corner.apex_speed_kmh < 150:
                return TrackSection.MEDIUM_CORNER, nearest_corner
            else:
                return TrackSection.FAST_CORNER, nearest_corner
        elif nearest_corner and min_distance < self.STRAIGHT_CLEARANCE_M:  # Braking/acceleration zone
            # Check if approaching or exiting corner
            if position_m < nearest_corner.position_m:
                return TrackSection.BRAKING_ZONE, nearest_corner
            else:
                return TrackSection.ACCELERATION_ZONE, nearest_corner
        else:
            return TrackSection.STRAIGHT, None

    def is_overtaking_zone(self, position_m: float) -> Tuple[bool, float]:
        """Check if position is in overtaking opportunity zone"""
        section, corner = self.get_section_at_position(position_m)

        if corner and corner.has_overtaking_opportunity:
            # Higher opportunity in braking zones before slow corners
            if section == TrackSection.BRAKING_ZONE:
                return True, 1.0 - corner.overtaking_difficulty
            elif section == TrackSection.SLOW_CORNER:
                return True, (1.0 - corner.overtaking_difficulty) * 0.7

        # Straights are always overtaking opportunities (with DRS/slipstream)
        if section == TrackSection.STRAIGHT:
            return True, 0.6

        return False, 0.0


def calculate_corner_performance(
    driver: Driver,
    corner: TrackCorner,
    tyre_condition: float,
    racing_line: RacingLine,
    cars_nearby: int = 0,
) -> Dict[str, float]:
    """
    Calculate driver performance through a specific corner

    Returns time loss/gain and exit speed based on:
    - Driver cornering skills
    - Chosen racing line
    - Tyre condition
    - Traffic (dirty air, blocking)
    """
    # Base corner time (perfect conditions, ideal line)
    base_time_s = (
        (corner.angle_deg / 360.0)
        * (2 * np.pi * corner.radius_m)
        / (corner.apex_speed_kmh / 3.6)
    )

    # Driver skill multiplier
    skill_factor = (
        corner.get_ideal_line_speed(driver, tyre_condition) / corner.apex_speed_kmh
    )

    # Racing line impact
    line_factors = {
        RacingLine.IDEAL: 1.0,
        RacingLine.DEFENSIVE: 0.97,  # Slightly slower but protects position
        RacingLine.ATTACKING: 0.95,  # Compromised line for overtake
        RacingLine.OFF_LINE: 0.85,  # Dirty track, less grip
    }
    line_factor = line_factors[racing_line]

    # Traffic impact (dirty air in corners)
    traffic_factor = 1.0 - (cars_nearby * 0.02)  # 2% loss per nearby car

    # Calculate actual corner time
    actual_time_s = base_time_s / (skill_factor * line_factor * traffic_factor)

    # Exit speed (crucial for overtaking)
    exit_speed_kmh = corner.exit_speed_kmh * skill_factor * line_factor

    return {
        "time_s": actual_time_s,
        "time_delta": actual_time_s - base_time_s,
        "exit_speed_kmh": exit_speed_kmh,
        "grip_used": (1.0 - tyre_condition) * 0.5 + 0.5,  # Tyre wear indicator
    }
