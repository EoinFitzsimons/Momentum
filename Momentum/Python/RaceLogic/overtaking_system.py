"""
Advanced Overtaking & Combat System

Implements realistic wheel-to-wheel racing including:
- Side-by-side combat through corners
- Divebomb overtaking attempts
- Defensive positioning and blocking
- Slipstream battles on straights
- Contact physics and incidents

All decisions use driver attributes comprehensively.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
import numpy as np

from database.models import Driver
from RaceLogic.track_physics import TrackCorner, TrackSection, RacingLine, calculate_corner_performance
from services.driver_attributes import (
    get_safe_attribute, get_driver_bravery, get_driver_aggression,
    get_driver_wheel_to_wheel_ability, get_driver_confidence
)


class OvertakeAttemptType(Enum):
    """Type of overtaking maneuver"""
    SLIPSTREAM_STRAIGHT = "slipstream_straight"      # DRS/draft pass on straight
    LATE_BRAKING = "late_braking"                    # Divebomb into braking zone
    SWITCHBACK = "switchback"                        # Counter after defensive move
    AROUND_OUTSIDE = "around_outside"                # Outside line overtake
    UNDERCUT = "undercut"                            # Early pit stop advantage


class DefensiveAction(Enum):
    """Defensive driving maneuvers"""
    HOLD_LINE = "hold_line"              # Stay on ideal line
    COVER_INSIDE = "cover_inside"        # Defend inside into corner
    SQUEEZE = "squeeze"                  # Push attacker toward edge
    # Change direction on straight (risky/illegal)
    WEAVING = "weaving"
    LATE_BRAKE_DEFENSE = "late_brake_defense"  # Brake later to stay ahead


@dataclass
class OvertakeAttempt:
    """
    Represents an active overtaking maneuver

    Tracks the entire overtake process from initiation to resolution.
    """
    attacker_id: int
    defender_id: int
    attempt_type: OvertakeAttemptType
    position_m: float

    # Battle state
    lateral_overlap: float = 0.0      # 0.0=behind, 1.0=fully alongside
    speed_advantage_kmh: float = 0.0  # Speed difference
    gap_m: float = 2.0                # Gap between cars

    # Corner context (if in corner)
    corner: Optional[TrackCorner] = None
    attacker_line: RacingLine = RacingLine.IDEAL
    defender_line: RacingLine = RacingLine.IDEAL

    # Outcome tracking
    frames_active: int = 0
    max_frames: int = 90  # 3 seconds at 30 FPS
    success_probability: float = 0.5

    def update(self, timestep: float) -> Optional[str]:
        """
        Update overtake attempt state

        Returns:
            - "success" if overtake completed
            - "failed" if attempt unsuccessful
            - "incident" if contact/crash occurred
            - None if still ongoing
        """
        self.frames_active += 1

        # Check timeout
        if self.frames_active >= self.max_frames:
            return "failed"

        # Update overlap based on speed advantage
        overlap_gain = (self.speed_advantage_kmh / 100.0) * timestep
        self.lateral_overlap += overlap_gain

        # Check for completion
        if self.lateral_overlap >= 1.2:  # Fully past
            return "success"
        elif self.lateral_overlap < -0.2:  # Lost overlap
            return "failed"

        return None  # Still fighting


def evaluate_overtaking_opportunity(
    attacker: Driver,
    defender: Driver,
    attacker_speed_kmh: float,
    defender_speed_kmh: float,
    gap_m: float,
    section: TrackSection,
    corner: Optional[TrackCorner],
    track_width_m: float = 12.0
) -> Tuple[bool, float, OvertakeAttemptType]:
    """
    Evaluate if overtaking attempt should be initiated

    Returns:
        - should_attempt: Boolean if driver decides to try
        - success_probability: 0.0-1.0 estimated success chance
        - attempt_type: Type of maneuver to use
    """

    # Can't overtake if too far behind
    if gap_m > 50.0:
        return False, 0.0, OvertakeAttemptType.SLIPSTREAM_STRAIGHT

    # Calculate speed advantage
    speed_advantage = attacker_speed_kmh - defender_speed_kmh

    # === STRAIGHT OVERTAKING ===
    if section == TrackSection.STRAIGHT:
        # Slipstream/DRS overtake
        if gap_m < 10.0 and speed_advantage > 3.0:
            # Factors affecting success
            attacker_factors = (
                0.25 * (attacker.overtaking / 100.0) +
                0.20 * (attacker.spatial_awareness / 100.0) +
                0.15 * (get_driver_bravery(attacker) / 100.0) +
                0.15 * (attacker.reaction_time / 100.0) +
                0.10 * (get_driver_confidence(attacker) / 100.0) +
                0.10 * (get_driver_aggression(attacker) / 100.0) +
                0.05 * (attacker.racecraft / 100.0)
            )

            defender_factors = (
                0.30 * (defender.defensive_driving / 100.0) +
                0.25 * (defender.spatial_awareness / 100.0) +
                0.20 * (defender.racecraft / 100.0) +
                0.15 * (defender.reaction_time / 100.0) +
                0.10 * (defender.professionalism / 100.0)
            )

            # Speed advantage gives attacker edge
            speed_factor = min(speed_advantage / 15.0, 1.0)

            success_prob = 0.3 + (0.4 * attacker_factors) - \
                (0.2 * defender_factors) + (0.3 * speed_factor)
            success_prob = np.clip(success_prob, 0.05, 0.95)

            # Decision threshold (aggressive drivers attempt earlier)
            threshold = 0.4 - (get_driver_aggression(attacker) / 100.0) * 0.2

            should_attempt = success_prob > threshold
            return should_attempt, success_prob, OvertakeAttemptType.SLIPSTREAM_STRAIGHT

    # === BRAKING ZONE OVERTAKING ===
    elif section == TrackSection.BRAKING_ZONE and corner:
        # Late braking divebomb
        if gap_m < 15.0:
            # Attacker needs brave, late-braking skill
            attacker_factors = (
                0.30 * (attacker.braking_technique / 100.0) +
                0.25 * (get_driver_bravery(attacker) / 100.0) +
                0.20 * (attacker.overtaking / 100.0) +
                0.15 * (attacker.spatial_awareness / 100.0) +
                0.10 * (attacker.vehicle_control / 100.0)
            )

            # Defender awareness of attack
            defender_factors = (
                0.35 * (defender.defensive_driving / 100.0) +
                0.25 * (defender.spatial_awareness / 100.0) +
                0.20 * (defender.braking_technique / 100.0) +
                0.20 * (defender.racecraft / 100.0)
            )

            # Corner difficulty affects success
            difficulty_factor = 1.0 - corner.overtaking_difficulty

            success_prob = 0.2 + (0.5 * attacker_factors) - \
                (0.3 * defender_factors) + (0.3 * difficulty_factor)
            success_prob = np.clip(success_prob, 0.05, 0.85)

            # Divebombs are risky - cautious drivers avoid
            risk_tolerance = (get_driver_bravery(
                attacker) + get_driver_aggression(attacker) - attacker.professionalism * 0.5) / 150.0
            threshold = 0.5 - risk_tolerance

            should_attempt = success_prob > threshold
            return should_attempt, success_prob, OvertakeAttemptType.LATE_BRAKING

    # === CORNER OVERTAKING ===
    elif section in [TrackSection.SLOW_CORNER, TrackSection.MEDIUM_CORNER] and corner:
        # Around outside or switchback
        if gap_m < 5.0 and corner.has_overtaking_opportunity:
            # Wide track enables side-by-side
            width_factor = min(track_width_m / 10.0, 1.2)

            attacker_factors = (
                0.25 * (attacker.cornering_skill / 100.0) +
                0.20 * (attacker.vehicle_control / 100.0) +
                0.20 * (attacker.spatial_awareness / 100.0) +
                0.15 * (get_driver_bravery(attacker) / 100.0) +
                0.10 * (attacker.overtaking / 100.0) +
                0.10 * (get_driver_wheel_to_wheel_ability(attacker) / 100.0)
            )

            defender_factors = (
                0.30 * (defender.cornering_skill / 100.0) +
                0.25 * (defender.defensive_driving / 100.0) +
                0.20 * (defender.spatial_awareness / 100.0) +
                0.15 * (defender.racecraft / 100.0) +
                0.10 * (get_driver_wheel_to_wheel_ability(defender) / 100.0)
            )

            # Defensive line gives advantage
            line_advantage = corner.defensive_line_advantage

            success_prob = 0.1 + (0.4 * attacker_factors) - (
                0.3 * defender_factors) - (0.2 * line_advantage) + (0.1 * width_factor)
            success_prob = np.clip(success_prob, 0.02, 0.70)

            # Patient drivers wait for better opportunity
            from services.driver_attributes import get_driver_patience
            patience_factor = get_driver_patience(attacker) / 100.0
            threshold = 0.4 - (patience_factor * 0.1)

            should_attempt = success_prob > threshold and get_driver_wheel_to_wheel_ability(
                attacker) > 40
            return should_attempt, success_prob, OvertakeAttemptType.AROUND_OUTSIDE

    # No good opportunity
    return False, 0.0, OvertakeAttemptType.SLIPSTREAM_STRAIGHT


def calculate_defensive_action(
    defender: Driver,
    attacker: Driver,
    gap_m: float,
    section: TrackSection,
    corner: Optional[TrackCorner]
) -> Tuple[DefensiveAction, RacingLine]:
    """
    Determine defensive strategy based on situation

    Returns:
        - action: Defensive maneuver to execute
        - line: Racing line to take
    """

    # === STRAIGHT DEFENSE ===
    if section == TrackSection.STRAIGHT:
        if gap_m < 10.0:
            # Defend aggressively if under pressure
            if defender.defensive_driving > 70 and get_driver_aggression(
                    defender) > 60:
                # Weaving (risky, may draw penalty if excessive)
                if defender.professionalism < 50:
                    return DefensiveAction.WEAVING, RacingLine.DEFENSIVE
                else:
                    return DefensiveAction.SQUEEZE, RacingLine.DEFENSIVE
            else:
                # Hold line and let them try
                return DefensiveAction.HOLD_LINE, RacingLine.IDEAL
        else:
            return DefensiveAction.HOLD_LINE, RacingLine.IDEAL

    # === BRAKING ZONE DEFENSE ===
    elif section == TrackSection.BRAKING_ZONE and corner:
        if gap_m < 15.0:
            # Awareness of attack determines response
            awareness = (
                defender.spatial_awareness * 0.4 +
                defender.defensive_driving * 0.3 +
                defender.racecraft * 0.3
            ) / 100.0

            if awareness > 0.6:
                # Cover inside line early
                return DefensiveAction.COVER_INSIDE, RacingLine.DEFENSIVE
            elif awareness > 0.4:
                # Late brake to stay ahead
                return DefensiveAction.LATE_BRAKE_DEFENSE, RacingLine.IDEAL
            else:
                # Unaware - stay on ideal line
                return DefensiveAction.HOLD_LINE, RacingLine.IDEAL
        else:
            return DefensiveAction.HOLD_LINE, RacingLine.IDEAL

    # === CORNER DEFENSE ===
    elif section in [TrackSection.SLOW_CORNER, TrackSection.MEDIUM_CORNER]:
        if gap_m < 5.0:
            # Side-by-side - squeeze but stay legal
            if defender.defensive_driving > 60:
                return DefensiveAction.SQUEEZE, RacingLine.DEFENSIVE
            else:
                return DefensiveAction.HOLD_LINE, RacingLine.DEFENSIVE
        else:
            return DefensiveAction.HOLD_LINE, RacingLine.IDEAL

    # Default: hold optimal line
    return DefensiveAction.HOLD_LINE, RacingLine.IDEAL


def calculate_incident_risk(
    attacker: Driver,
    defender: Driver,
    overtake_attempt: OvertakeAttempt,
    section: TrackSection
) -> float:
    """
    Calculate probability of incident during overtake

    Returns probability (0.0-1.0) of contact/crash
    """
    # === TEMPORARY: COLLISION TESTING DISABLED ===
    # Base risks set to near-zero for testing car movement and positioning
    # TODO: Re-enable realistic collision rates once car rendering is verified
    base_risks = {
        TrackSection.STRAIGHT: 0.0001,        # 0.01% - testing only
        TrackSection.BRAKING_ZONE: 0.0001,    # 0.01% - testing only
        TrackSection.SLOW_CORNER: 0.0001,     # 0.01% - testing only
        TrackSection.MEDIUM_CORNER: 0.0001,   # 0.01% - testing only
        TrackSection.FAST_CORNER: 0.0002,     # 0.02% - testing only
        TrackSection.ACCELERATION_ZONE: 0.0001  # 0.01% - testing only
    }

    base_risk = base_risks.get(section, 0.0001)  # 0.01% default for testing

    # Skill mitigates risk
    attacker_control = (
        attacker.spatial_awareness * 0.30 +
        attacker.vehicle_control * 0.25 +
        get_driver_wheel_to_wheel_ability(attacker) * 0.20 +
        attacker.professionalism * 0.15 +
        attacker.concentration * 0.10
    ) / 100.0

    defender_control = (
        defender.spatial_awareness * 0.30 +
        defender.vehicle_control * 0.25 +
        defender.defensive_driving * 0.20 +
        defender.professionalism * 0.15 +
        get_driver_wheel_to_wheel_ability(defender) * 0.10
    ) / 100.0

    combined_skill = (attacker_control + defender_control) / 2.0

    # Aggression increases risk
    aggression_factor = (get_driver_aggression(
        attacker) + get_driver_aggression(defender)) / 200.0

    # Overlap affects risk (most dangerous at 0.5 = side-by-side)
    overlap_risk = 1.0 - abs(1.0 - 2.0 * overtake_attempt.lateral_overlap)

    # Final calculation
    incident_prob = base_risk * \
        (1.5 - combined_skill) * (1.0 + aggression_factor * 0.5) * overlap_risk

    return np.clip(incident_prob, 0.001, 0.30)


def resolve_overtake_outcome(
    attacker: Driver,
    defender: Driver,
    overtake_attempt: OvertakeAttempt,
    rng: np.random.Generator
) -> Tuple[str, Optional[str]]:
    """
    Resolve overtake attempt outcome

    Returns:
        - result: "success", "failed", or "incident"
        - incident_type: If incident, what type (collision, spin, etc.)
    """
    # Roll for incident
    if overtake_attempt.corner:
        section = TrackSection.SLOW_CORNER  # Simplified
    else:
        section = TrackSection.STRAIGHT

    incident_risk = calculate_incident_risk(
        attacker, defender, overtake_attempt, section)

    if rng.random() < incident_risk:
        # Determine who suffers
        if overtake_attempt.lateral_overlap < 0.3:
            # Attacker at fault (rear-end or divebomb)
            return "incident", "collision_attacker_fault"
        elif overtake_attempt.lateral_overlap > 0.7:
            # Defender at fault (squeeze or late block)
            return "incident", "collision_defender_fault"
        else:
            # Racing incident (both alongside)
            return "incident", "racing_incident"

    # No incident - resolve normally
    if rng.random() < overtake_attempt.success_probability:
        return "success", None
    else:
        return "failed", None
