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
from typing import Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np

from momentum.database.models import Driver
from momentum.engine.track_physics import (
    TrackCorner,
    TrackSection,
    RacingLine,
)
from momentum.services.driver_attributes import (
    get_safe_attribute,
    get_driver_aggression,
    get_driver_bravery,
)


DEFAULT_LOGISTIC_SLOPES = {
    "straight": 3.8,
    "braking": 3.4,
    "outside": 3.2,
    "switch": 3.0,
    "risk": 3.4,
}

_ACTIVE_LOGISTIC_SLOPES = dict(DEFAULT_LOGISTIC_SLOPES)


def _effective_logistic_slopes(
    logistic_slopes: Optional[dict] = None,
) -> Dict[str, float]:
    """Return validated slope map merged with defaults."""
    if not logistic_slopes:
        return dict(DEFAULT_LOGISTIC_SLOPES)

    updated = dict(DEFAULT_LOGISTIC_SLOPES)
    for key, value in logistic_slopes.items():
        if key in updated and value is not None:
            updated[key] = float(value)
    return updated


def set_logistic_slopes(slopes: Optional[dict]) -> None:
    """Set active logistic slopes used by overtake and incident models.

    A slope controls how sensitive probability is to the latent signal:
    - lower slope => smoother, less reactive probability changes
    - higher slope => sharper threshold-like behaviour
    """
    global _ACTIVE_LOGISTIC_SLOPES
    _ACTIVE_LOGISTIC_SLOPES = _effective_logistic_slopes(slopes)


def get_logistic_slopes() -> dict:
    """Return current logistic slope configuration."""
    return dict(_ACTIVE_LOGISTIC_SLOPES)


# Simpler policy: use canonical `racecraft` where previously derived
# aggregates were used. This keeps logic straightforward and avoids
# creating additional computed signals.
def get_racecraft(drv: Driver) -> float:
    return get_safe_attribute(drv, "racecraft")


def _logistic_probability(signal: float, slope: float = 4.0) -> float:
    """Return bounded probability from a latent competition signal.

    "signal" is a weighted advantage score (attacker factors minus defender
    factors, plus context terms like speed/track). Logistic mapping converts
    that score into a stable 0..1 probability.
    """
    z = np.clip(float(signal) * float(slope), -12.0, 12.0)
    return float(1.0 / (1.0 + np.exp(-z)))


def _apply_generic_commitment_nudge(
    should_attempt: bool,
    success_prob: float,
    gap_m: float,
    speed_advantage: float,
    push: float,
    overtake: float,
) -> Tuple[bool, float]:
    """Apply non-player aggressive commitment nudge when setup is strong."""
    if push >= 0.85 and overtake >= 0.80 and speed_advantage >= 5.0 and gap_m <= 10.0:
        return True, max(success_prob, 0.65)
    return should_attempt, success_prob


def _apply_player_max_commitment(
    success_prob: float,
    attempt_type: "OvertakeAttemptType",
    section: TrackSection,
    gap_m: float,
    speed_advantage: float,
    push: float,
    overtake: float,
    racing_mode: str,
) -> Optional[Tuple[bool, float, "OvertakeAttemptType"]]:
    """Return forced player-commitment decision when max controls are active."""
    if not (push >= 0.95 and overtake >= 0.90 and racing_mode == "attack"):
        return None
    if section == TrackSection.STRAIGHT and speed_advantage >= 8.0 and gap_m <= 28.0:
        return True, max(success_prob, 0.93), OvertakeAttemptType.SLIPSTREAM_STRAIGHT
    if section == TrackSection.BRAKING_ZONE and speed_advantage >= 1.0 and gap_m <= 7.0:
        return True, max(success_prob, 0.84), OvertakeAttemptType.LATE_BRAKING
    if gap_m <= 7.0 and speed_advantage >= 0.5:
        return True, max(success_prob, 0.76), attempt_type
    return None


def _apply_attack_commitment_override(
    should_attempt: bool,
    success_prob: float,
    attempt_type: "OvertakeAttemptType",
    section: TrackSection,
    gap_m: float,
    speed_advantage: float,
    attack_context: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, float, "OvertakeAttemptType"]:
    """Apply commitment-aware overrides to prevent gearbox lock-ups.

    This keeps tactical logic in the overtaking module (not only the race
    engine) so decisioning and resolution remain coherent.
    """
    if not isinstance(attack_context, dict):
        return should_attempt, success_prob, attempt_type

    push = float(attack_context.get("push_intensity", 0.5) or 0.5)
    overtake = float(attack_context.get("overtake_intensity", 0.5) or 0.5)
    is_player = bool(attack_context.get("is_player_controlled", False))
    racing_mode = str(attack_context.get("racing_mode", "") or "").lower()

    should_attempt, success_prob = _apply_generic_commitment_nudge(
        should_attempt=should_attempt,
        success_prob=success_prob,
        gap_m=gap_m,
        speed_advantage=speed_advantage,
        push=push,
        overtake=overtake,
    )

    if is_player:
        player_decision = _apply_player_max_commitment(
            success_prob=success_prob,
            attempt_type=attempt_type,
            section=section,
            gap_m=gap_m,
            speed_advantage=speed_advantage,
            push=push,
            overtake=overtake,
            racing_mode=racing_mode,
        )
        if player_decision is not None:
            return player_decision

    return should_attempt, success_prob, attempt_type


class OvertakeAttemptType(Enum):
    """Type of overtaking maneuver"""

    SLIPSTREAM_STRAIGHT = "slipstream_straight"  # DRS/draft pass on straight
    LATE_BRAKING = "late_braking"  # Divebomb into braking zone
    SWITCHBACK = "switchback"  # Counter after defensive move
    AROUND_OUTSIDE = "around_outside"  # Outside line overtake
    UNDERCUT = "undercut"  # Early pit stop advantage


class DefensiveAction(Enum):
    """Defensive driving maneuvers"""

    HOLD_LINE = "hold_line"  # Stay on ideal line
    COVER_INSIDE = "cover_inside"  # Defend inside into corner
    SQUEEZE = "squeeze"  # Push attacker toward edge
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
    lateral_overlap: float = 0.0  # 0.0=behind, 1.0=fully alongside
    speed_advantage_kmh: float = 0.0  # Speed difference
    gap_m: float = 2.0  # Gap between cars

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
    track_width_m: float = 12.0,
    logistic_slopes: Optional[dict] = None,
    attack_context: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, float, OvertakeAttemptType]:
    """
    Evaluate if overtaking attempt should be initiated

    Returns:
        - should_attempt: Boolean if driver decides to try
        - success_probability: 0.0-1.0 estimated success chance
        - attempt_type: Type of maneuver to use
    """

    slopes = _effective_logistic_slopes(logistic_slopes)

    # Can't overtake if too far behind
    if gap_m > 50.0:
        return False, 0.0, OvertakeAttemptType.SLIPSTREAM_STRAIGHT

    # Calculate speed advantage
    speed_advantage = attacker_speed_kmh - defender_speed_kmh

    # === STRAIGHT OVERTAKING ===
    if section == TrackSection.STRAIGHT:
        # Make slipstream/DRS attempts more common on longer straights
        # by widening the gap and lowering the required speed advantage.
        if gap_m < 20.0 and speed_advantage > 1.5:
            # Attacker mix: racecraft, aggression and bravery help here
            attacker_score = (
                0.50 * (get_racecraft(attacker) / 100.0)
                + 0.30 * (get_driver_aggression(attacker) / 100.0)
                + 0.20 * (get_driver_bravery(attacker) / 100.0)
            )

            defender_score = 0.60 * (get_racecraft(defender) / 100.0) + 0.40 * (
                get_safe_attribute(defender, "reactions") / 100.0
            )

            # Speed advantage scales the chance (larger advantage -> easier pass)
            speed_factor = min(max(speed_advantage / 12.0, 0.0), 1.0)

            latent = (
                (1.15 * attacker_score)
                - (0.85 * defender_score)
                + (0.95 * speed_factor)
                - 0.55
            )
            success_prob = _logistic_probability(latent, slope=slopes["straight"])
            success_prob = np.clip(success_prob, 0.03, 0.97)

            # Aggressive or brave drivers try earlier
            threshold = (
                0.45
                - (get_driver_aggression(attacker) / 100.0) * 0.25
                - (get_driver_bravery(attacker) / 100.0) * 0.10
            )

            should_attempt = success_prob > threshold
            return _apply_attack_commitment_override(
                should_attempt=bool(should_attempt),
                success_prob=float(success_prob),
                attempt_type=OvertakeAttemptType.SLIPSTREAM_STRAIGHT,
                section=section,
                gap_m=float(gap_m),
                speed_advantage=float(speed_advantage),
                attack_context=attack_context,
            )

    # === BRAKING ZONE OVERTAKING ===
    elif section == TrackSection.BRAKING_ZONE and corner:
        # Late braking divebomb
        # Reduce frequency of divebombs: require closer gap and use
        # aggregated signals (bravery/aggression) rather than repeating
        # `racecraft` which inflated earlier probability calculations.
        if gap_m < 8.0:
            # Attacker skill mix: bravery, aggression and reactions
            attacker_score = (
                0.50 * (get_driver_bravery(attacker) / 100.0)
                + 0.30 * (get_driver_aggression(attacker) / 100.0)
                + 0.20 * (get_safe_attribute(attacker, "reactions") / 100.0)
            )

            # Defender awareness: professionalism and reactions
            defender_score = 0.60 * (
                get_safe_attribute(defender, "reactions") / 100.0
            ) + 0.40 * (get_safe_attribute(defender, "racecraft") / 100.0)

            # Corner difficulty reduces overtaking chance when high
            difficulty_factor = max(
                0.0, 1.0 - getattr(corner, "overtaking_difficulty", 0.5)
            )

            latent = (
                (1.20 * attacker_score)
                - (0.90 * defender_score)
                + (0.70 * difficulty_factor)
                - 0.75
            )
            success_prob = _logistic_probability(latent, slope=slopes["braking"])
            success_prob = np.clip(success_prob, 0.02, 0.85)

            # Risk tolerance driven by aggression (not raw racecraft)
            risk_tolerance = (get_driver_aggression(attacker) / 100.0) * 0.25
            threshold = 0.5 - risk_tolerance

            should_attempt = success_prob > threshold
            return _apply_attack_commitment_override(
                should_attempt=bool(should_attempt),
                success_prob=float(success_prob),
                attempt_type=OvertakeAttemptType.LATE_BRAKING,
                section=section,
                gap_m=float(gap_m),
                speed_advantage=float(speed_advantage),
                attack_context=attack_context,
            )

    # === CORNER OVERTAKING ===
    elif section in [TrackSection.SLOW_CORNER, TrackSection.MEDIUM_CORNER] and corner:
        # Consider both Around-Outside and Switchback attempts and choose
        # the maneuver with the better odds. This increases variety.
        if gap_m < 7.0 and corner.has_overtaking_opportunity:
            # Wide track enables side-by-side
            width_factor = min(track_width_m / 10.0, 1.2)

            # Common defender score
            defender_score = 0.50 * (
                get_safe_attribute(defender, "reactions") / 100.0
            ) + 0.50 * (get_racecraft(defender) / 100.0)

            # Outside attempt (requires space and racecraft)
            attacker_outside = (
                0.55 * (get_racecraft(attacker) / 100.0)
                + 0.25 * (get_driver_aggression(attacker) / 100.0)
                + 0.20 * (get_driver_bravery(attacker) / 100.0)
            )
            outside_latent = (
                (1.00 * attacker_outside)
                - (0.82 * defender_score)
                + (0.35 * width_factor)
                - 0.70
            )
            outside_success = _logistic_probability(
                outside_latent, slope=slopes["outside"]
            )
            outside_success = np.clip(outside_success, 0.02, 0.80)

            # Switchback attempt (requires patience and racecraft to set up)
            attacker_switch = (
                0.60 * (get_racecraft(attacker) / 100.0)
                + 0.25 * (get_safe_attribute(attacker, "patience") / 100.0)
                + 0.15 * (get_driver_bravery(attacker) / 100.0)
            )
            switch_latent = (
                (1.05 * attacker_switch)
                - (0.78 * defender_score)
                + (0.30 * width_factor)
                - 0.72
            )
            switch_success = _logistic_probability(
                switch_latent, slope=slopes["switch"]
            )
            switch_success = np.clip(switch_success, 0.02, 0.78)

            # Choose the maneuver with higher success probability but require
            # a modest minimum to avoid spamming very unlikely moves.
            candidates = [
                (outside_success, OvertakeAttemptType.AROUND_OUTSIDE),
                (switch_success, OvertakeAttemptType.SWITCHBACK),
            ]

            # Pick best candidate
            best_prob, best_type = max(candidates, key=lambda x: x[0])

            # Threshold depends on attacker's aggression/patience
            threshold = (
                0.4
                - (get_driver_aggression(attacker) / 100.0) * 0.1
                + (get_safe_attribute(attacker, "patience") / 100.0) * -0.05
            )

            should_attempt = best_prob > threshold and get_racecraft(attacker) > 30
            return _apply_attack_commitment_override(
                should_attempt=bool(should_attempt),
                success_prob=float(best_prob),
                attempt_type=best_type,
                section=section,
                gap_m=float(gap_m),
                speed_advantage=float(speed_advantage),
                attack_context=attack_context,
            )

    # No good opportunity
    return False, 0.0, OvertakeAttemptType.SLIPSTREAM_STRAIGHT


def _get_straight_defense(
    defender: Driver, attacker: Driver, gap_m: float
) -> Tuple[DefensiveAction, RacingLine]:
    """Evaluate defensive action on straights"""
    if gap_m < 10.0:
        # Stronger attackers force more aggressive defense
        attacker_threat = get_racecraft(attacker) / 100.0
        defender_skill = get_racecraft(defender) / 100.0

        # If attacker is significantly better, need active defense; if defender is better, can relax
        defense_intensity = (attacker_threat - defender_skill) * 0.5 + defender_skill

        if defense_intensity > 0.65:
            # Aggressive defense against strong attackers
            if get_racecraft(defender) < 50:
                return DefensiveAction.WEAVING, RacingLine.DEFENSIVE
            else:
                return DefensiveAction.SQUEEZE, RacingLine.DEFENSIVE
        else:
            # Hold line against weaker attackers
            return DefensiveAction.HOLD_LINE, RacingLine.IDEAL
    return DefensiveAction.HOLD_LINE, RacingLine.IDEAL


def _get_braking_zone_defense(
    defender: Driver, attacker: Driver, gap_m: float
) -> Tuple[DefensiveAction, RacingLine]:
    """Evaluate defensive action in braking zones"""
    if gap_m < 15.0:
        # Defender awareness vs attacker threat determines response
        awareness = get_racecraft(defender) / 100.0
        attacker_aggression = get_driver_aggression(attacker) / 100.0

        # Adjust awareness threshold based on attacker's aggressiveness
        effective_threshold = 0.6 - (attacker_aggression * 0.2)

        if awareness > effective_threshold:
            # Defend inside against aggressive attackers
            return DefensiveAction.COVER_INSIDE, RacingLine.DEFENSIVE
        elif awareness > 0.35:
            # Late brake to preserve position
            return DefensiveAction.LATE_BRAKE_DEFENSE, RacingLine.IDEAL
        else:
            # Caught unaware - try to maintain ideal line
            return DefensiveAction.HOLD_LINE, RacingLine.IDEAL
    return DefensiveAction.HOLD_LINE, RacingLine.IDEAL


def _get_corner_defense(
    defender: Driver, attacker: Driver, gap_m: float
) -> Tuple[DefensiveAction, RacingLine]:
    """Evaluate defensive action in corners"""
    if gap_m < 5.0:
        # Side-by-side situation - intensity depends on matchup
        defender_corner_speed = get_racecraft(defender) / 100.0
        attacker_corner_speed = get_racecraft(attacker) / 100.0
        attacker_bravery = get_driver_bravery(attacker) / 100.0

        # Brave attackers need firmer defense; skill matchup determines squeeze intensity
        defense_needed = defender_corner_speed > (
            attacker_corner_speed - attacker_bravery * 0.3
        )

        if defense_needed and get_racecraft(defender) > 55:
            # Assertive defense against competitive attackers
            return DefensiveAction.SQUEEZE, RacingLine.DEFENSIVE
        else:
            # Hold line - either defender is skilled or attacker too weak to squeeze against
            return DefensiveAction.HOLD_LINE, RacingLine.DEFENSIVE
    return DefensiveAction.HOLD_LINE, RacingLine.IDEAL


def calculate_defensive_action(
    defender: Driver,
    attacker: Driver,
    gap_m: float,
    section: TrackSection,
    corner: Optional[TrackCorner],
) -> Tuple[DefensiveAction, RacingLine]:
    """
    Determine defensive strategy based on situation

    Returns:
        - action: Defensive maneuver to execute
        - line: Racing line to take
    """
    # Dispatch to section-specific helper based on track section
    if section == TrackSection.STRAIGHT:
        return _get_straight_defense(defender, attacker, gap_m)
    elif section == TrackSection.BRAKING_ZONE and corner:
        return _get_braking_zone_defense(defender, attacker, gap_m)
    elif section in [TrackSection.SLOW_CORNER, TrackSection.MEDIUM_CORNER]:
        return _get_corner_defense(defender, attacker, gap_m)

    # Default: hold optimal line
    return DefensiveAction.HOLD_LINE, RacingLine.IDEAL


def calculate_incident_risk(
    attacker: Driver,
    defender: Driver,
    overtake_attempt: OvertakeAttempt,
    section: TrackSection,
    logistic_slopes: Optional[dict] = None,
) -> float:
    """
    Calculate probability of incident during overtake

    Returns probability (0.0-1.0) of contact/crash
    """
    slopes = _effective_logistic_slopes(logistic_slopes)

    # === TEMPORARY: COLLISION TESTING DISABLED ===
    # Base risks set to near-zero for testing car movement and positioning.
    # Note: Realistic collision rates (0.10-0.40 range) require verification of visual
    # car rendering and overlap calculations before they can be re-enabled safely.
    base_risks = {
        TrackSection.STRAIGHT: 0.0001,  # 0.01% - testing only
        TrackSection.BRAKING_ZONE: 0.0001,  # 0.01% - testing only
        TrackSection.SLOW_CORNER: 0.0001,  # 0.01% - testing only
        TrackSection.MEDIUM_CORNER: 0.0001,  # 0.01% - testing only
        TrackSection.FAST_CORNER: 0.0002,  # 0.02% - testing only
        TrackSection.ACCELERATION_ZONE: 0.0001,  # 0.01% - testing only
    }

    base_risk = base_risks.get(section, 0.0001)  # 0.01% default for testing

    # Skill mitigates risk.
    attacker_control = get_racecraft(attacker) / 100.0
    defender_control = get_racecraft(defender) / 100.0
    combined_skill = (attacker_control + defender_control) / 2.0

    # Aggression/bravery increase risk pressure.
    aggression_factor = (
        get_driver_aggression(attacker) + get_driver_aggression(defender)
    ) / 200.0
    bravery_factor = (
        get_driver_bravery(attacker) + get_driver_bravery(defender)
    ) / 200.0

    # Overlap affects risk (most dangerous at 0.5 = side-by-side)
    overlap_risk = 1.0 - abs(1.0 - 2.0 * overtake_attempt.lateral_overlap)

    # Logistic risk pressure keeps probability bounded and realistic.
    risk_pressure = (
        (1.35 * aggression_factor)
        + (0.90 * bravery_factor)
        - (1.10 * combined_skill)
        + (0.75 * overlap_risk)
        - 0.45
    )
    risk_multiplier = 0.45 + (
        1.8 * _logistic_probability(risk_pressure, slope=slopes["risk"])
    )
    incident_prob = base_risk * risk_multiplier * overlap_risk

    return np.clip(incident_prob, 0.0, 0.30)


def resolve_overtake_outcome(
    attacker: Driver,
    defender: Driver,
    overtake_attempt: OvertakeAttempt,
    rng: np.random.Generator,
    logistic_slopes: Optional[dict] = None,
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
        attacker,
        defender,
        overtake_attempt,
        section,
        logistic_slopes=logistic_slopes,
    )

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
