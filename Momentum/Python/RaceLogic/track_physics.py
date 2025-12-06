"""
Advanced Racing Physics Engine - Track-Aware Agent-Based Simulation

This module implements a sophisticated racing simulation that uses:
1. Track corner analysis and racing lines
2. Overtaking opportunity zones based on track geometry
3. Defensive positioning and blocking
4. All 50+ driver attributes properly weighted
5. Real-time spatial combat (side-by-side, slipstream, divebombs)

Authors: Final Year Project - Computer Science
Date: December 2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np

from database.models import Driver, Track, Team
from services.driver_attributes import get_driver_bravery


class TrackSection(Enum):
    """Type of track section"""
    STRAIGHT = "straight"
    SLOW_CORNER = "slow_corner"       # < 80 km/h
    MEDIUM_CORNER = "medium_corner"   # 80-150 km/h
    FAST_CORNER = "fast_corner"       # > 150 km/h
    BRAKING_ZONE = "braking_zone"
    ACCELERATION_ZONE = "acceleration_zone"


class RacingLine(Enum):
    """Racing line position"""
    IDEAL = "ideal"           # Optimal racing line
    DEFENSIVE = "defensive"   # Inside line to defend
    ATTACKING = "attacking"   # Alternative line for overtaking
    OFF_LINE = "off_line"     # Sub-optimal line (dirty, less grip)


@dataclass
class TrackCorner:
    """
    Detailed corner analysis for racing simulation

    Each corner has multiple racing lines and overtaking characteristics.
    """
    corner_number: int
    position_m: float               # Distance from start line
    radius_m: float                 # Corner radius
    angle_deg: float                # Corner angle (degrees)
    direction: str                  # "left" or "right"

    # Speed characteristics
    entry_speed_kmh: float          # Typical entry speed
    apex_speed_kmh: float           # Speed at apex
    exit_speed_kmh: float           # Speed on exit

    # Overtaking potential
    has_overtaking_opportunity: bool
    overtaking_difficulty: float    # 0.0-1.0 (0=easy, 1=impossible)
    defensive_line_advantage: float  # Advantage for inside line

    # Track conditions
    grip_level: float = 1.0         # 0.0-1.0 (1.0 = perfect grip)
    runoff_area: bool = True        # Safe runoff if mistake
    barrier_proximity_m: float = 5.0  # Distance to barriers

    def get_ideal_line_speed(self, driver: Driver,
                             tire_condition: float) -> float:
        """Calculate optimal corner speed for driver"""
        # Base corner speed
        base_speed = self.apex_speed_kmh

        # Driver skill influence
        skill_factor = (
            0.30 * (driver.cornering_skill / 100.0) +
            0.25 * (driver.vehicle_control / 100.0) +
            0.20 * (driver.spatial_awareness / 100.0) +
            0.15 * (driver.braking_technique / 100.0) +
            0.10 * (driver.coordination / 100.0)
        )

        # Corner-specific skills
        from services.driver_attributes import get_driver_patience
        if self.angle_deg > 120:  # Hairpin
            skill_factor *= (1.0 + (get_driver_patience(driver) / 200.0))
        elif self.radius_m > 100:  # Fast corner
            skill_factor *= (1.0 + (get_driver_bravery(driver) / 200.0))

        # Tire degradation impact
        tire_factor = 0.7 + (0.3 * tire_condition)

        # Grip level
        grip_factor = self.grip_level

        return base_speed * (0.85 + 0.15 * skill_factor) * \
            tire_factor * grip_factor


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
        default_factory=list)  # (start_m, end_m)

    def __post_init__(self):
        """Generate track map from Track data"""
        if not self.corners:
            self._generate_corners()
        if not self.drs_zones and self.track.drs_zones > 0:
            self._generate_drs_zones()

    def _generate_corners(self):
        """Generate corner analysis from track data"""
        track_length_m = self.track.length_km * 1000
        num_corners = self.track.turns

        # Distribute corners around track
        for i in range(num_corners):
            # Position (roughly evenly distributed)
            position_m = (i / num_corners) * track_length_m

            # Vary corner types based on track characteristics
            corner_type = self._determine_corner_type(i, num_corners)

            # Corner characteristics
            if corner_type == "slow":
                radius_m = self.track.tightest_corner_radius_m * \
                    np.random.uniform(0.8, 1.2)
                apex_speed_kmh = self.track.avg_speed_kmh * 0.4
                overtaking_diff = 0.3  # Easier to overtake at slow corners
            elif corner_type == "medium":
                radius_m = self.track.tightest_corner_radius_m * \
                    np.random.uniform(2.0, 4.0)
                apex_speed_kmh = self.track.avg_speed_kmh * 0.7
                overtaking_diff = 0.6
            else:  # fast
                radius_m = self.track.tightest_corner_radius_m * \
                    np.random.uniform(5.0, 10.0)
                apex_speed_kmh = self.track.avg_speed_kmh * 0.85
                overtaking_diff = 0.9  # Very difficult

            # Direction (alternate with bias from track data)
            direction = "left" if (
                i %
                2 == 0 and self.track.left_turns >= self.track.right_turns) else "right"

            # Angle based on radius
            angle_deg = 90 if corner_type == "medium" else (
                45 if corner_type == "fast" else 120)

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
                grip_level=1.0 if self.track.surface == "asphalt" else 0.9
            )

            self.corners.append(corner)

    def _determine_corner_type(self, corner_index: int,
                               total_corners: int) -> str:
        """Determine if corner is slow/medium/fast"""
        # Mix of corner types based on track characteristics
        ratio = corner_index / total_corners

        if self.track.avg_speed_kmh > 220:  # Fast track
            return "fast" if ratio > 0.3 else (
                "medium" if ratio > 0.15 else "slow")
        elif self.track.avg_speed_kmh < 160:  # Slow/twisty track
            return "slow" if ratio > 0.5 else (
                "medium" if ratio > 0.25 else "fast")
        else:  # Balanced
            return "medium" if 0.3 < ratio < 0.7 else (
                "slow" if ratio < 0.3 else "fast")

    def _generate_drs_zones(self):
        """Generate DRS activation zones"""
        track_length_m = self.track.length_km * 1000

        # Place DRS zones on longest straights
        straight_positions = []
        for i in range(self.track.drs_zones):
            # DRS typically after slow corners leading to straights
            start_fraction = (i + 0.5) / self.track.drs_zones
            start_m = start_fraction * track_length_m
            end_m = start_m + (self.track.longest_straight_m * 0.8)

            self.drs_zones.append((start_m, end_m))

    def get_section_at_position(
            self, position_m: float) -> Tuple[TrackSection, Optional[TrackCorner]]:
        """Get track section type and nearest corner at position"""
        # Find nearest corner
        nearest_corner = None
        min_distance = float('inf')

        for corner in self.corners:
            distance = abs(corner.position_m - position_m)
            if distance < min_distance:
                min_distance = distance
                nearest_corner = corner

        # Determine section type based on proximity to corner
        if nearest_corner and min_distance < 50:  # Within 50m of corner
            if nearest_corner.apex_speed_kmh < 80:
                return TrackSection.SLOW_CORNER, nearest_corner
            elif nearest_corner.apex_speed_kmh < 150:
                return TrackSection.MEDIUM_CORNER, nearest_corner
            else:
                return TrackSection.FAST_CORNER, nearest_corner
        elif nearest_corner and min_distance < 150:  # Braking/acceleration zone
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
    tire_condition: float,
    racing_line: RacingLine,
    cars_nearby: int = 0
) -> Dict[str, float]:
    """
    Calculate driver performance through a specific corner

    Returns time loss/gain and exit speed based on:
    - Driver cornering skills
    - Chosen racing line
    - Tire condition
    - Traffic (dirty air, blocking)
    """
    # Base corner time (perfect conditions, ideal line)
    base_time_s = (corner.angle_deg / 360.0) * (2 * np.pi *
                                                corner.radius_m) / (corner.apex_speed_kmh / 3.6)

    # Driver skill multiplier
    skill_factor = corner.get_ideal_line_speed(
        driver, tire_condition) / corner.apex_speed_kmh

    # Racing line impact
    line_factors = {
        RacingLine.IDEAL: 1.0,
        RacingLine.DEFENSIVE: 0.97,      # Slightly slower but protects position
        RacingLine.ATTACKING: 0.95,      # Compromised line for overtake
        RacingLine.OFF_LINE: 0.85        # Dirty track, less grip
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
        "grip_used": (1.0 - tire_condition) * 0.5 + 0.5  # Tire wear indicator
    }
