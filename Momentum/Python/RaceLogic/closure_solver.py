"""Closure solver for assembling primitives into a closed loop.

This module provides a pragmatic least-squares solver which adjusts
scale multipliers for straight lengths and corner angles to satisfy
closure constraints (dx, dy, dtheta = 2*pi).

It relies on SciPy for the nonlinear least-squares solver. The solver
operates on a small set of multipliers so solves are fast. The approach
keeps radii and clothoid lengths fixed and only scales straight lengths
and corner angles (preserving primitive character while achieving
closure in one pass).
"""
from typing import List, Tuple, Any
import math
import numpy as np
try:
    from scipy.optimize import least_squares
    from scipy import integrate
    from scipy.optimize import minimize
except Exception as e:
    raise ImportError("scipy is required for closure_solver. Install scipy in the environment.") from e


CLOSURE_PARAM_MIN = 0.2
CLOSURE_PARAM_MAX = 5.0
CLOSURE_REGULARIZATION_WEIGHT = 0.1
CLOSURE_PRIMARY_MINIMIZE_METHOD = 'Powell'
CLOSURE_FALLBACK_MINIMIZE_METHOD = 'Nelder-Mead'
CLOSURE_PRIMARY_MINIMIZE_OPTIONS = {
    'maxiter': 5000,
    'xtol': 1e-4,
    'ftol': 1e-4,
}
CLOSURE_FALLBACK_MINIMIZE_OPTIONS = {
    'maxiter': 5000,
    'xatol': 1e-4,
    'fatol': 1e-4,
}
CLOSURE_POSITION_TOLERANCE_M = 1e-2
CLOSURE_ANGLE_TOLERANCE_RAD = 0.6


def _minimize_discrete_with_fallback(obj_fn, p_init):
    """Run discrete minimization with Powell primary and Nelder-Mead fallback."""
    res = minimize(
        obj_fn,
        p_init,
        method=CLOSURE_PRIMARY_MINIMIZE_METHOD,
        options=CLOSURE_PRIMARY_MINIMIZE_OPTIONS,
    )
    if res.success:
        return res, CLOSURE_PRIMARY_MINIMIZE_METHOD

    fallback_res = minimize(
        obj_fn,
        p_init,
        method=CLOSURE_FALLBACK_MINIMIZE_METHOD,
        options=CLOSURE_FALLBACK_MINIMIZE_OPTIONS,
    )
    return fallback_res, CLOSURE_FALLBACK_MINIMIZE_METHOD


def _wrap_angle(a: float) -> float:
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def _simulate_primitives(instructions: List[Any], multipliers: List[float]) -> Tuple[float, float, float]:
    """Simulate forward kinematics matching CircuitGenerator semantics.

    This uses the same discrete-step integration as the GUI generator:
    - straights advance by unit steps along current theta
    - corners are composed of clothoid entry, circular arc, and clothoid exit

    Multipliers are applied to straight lengths and corner angles.
    """
    return _simulate_primitives_impl(instructions, multipliers)


def _integrate_clothoid_discrete(length: int, k_clothoid: float, sign: int, theta0: float, reverse: bool = False) -> Tuple[float, float, float]:
    """Discrete-step clothoid integration matching generator semantics."""
    x_loc = 0.0
    y_loc = 0.0
    theta_loc = theta0
    for i in range(int(length)):
        curvature = k_clothoid * ((int(length) - i) if reverse else i) * sign
        theta_loc += curvature
        x_loc += math.cos(theta_loc)
        y_loc += math.sin(theta_loc)
    dtheta = theta_loc - theta0
    return x_loc, y_loc, dtheta


def _integrate_clothoid_continuous(length: float, k_clothoid: float, sign: int, theta0: float) -> Tuple[float, float, float]:
    """Continuous clothoid integration using quadrature."""
    a = k_clothoid * sign
    fx = lambda t: math.cos(theta0 + 0.5 * a * t * t)
    fy = lambda t: math.sin(theta0 + 0.5 * a * t * t)
    ix = integrate.quad(fx, 0.0, length, epsabs=1e-6, epsrel=1e-6)[0]
    iy = integrate.quad(fy, 0.0, length, epsabs=1e-6, epsrel=1e-6)[0]
    dtheta = 0.5 * a * length * length
    return ix, iy, dtheta


def _apply_tuple_instruction_discrete(instr: Any, multipliers: List[float], param_idx: int, x: float, y: float, theta: float) -> Tuple[float, float, float, int]:
    typ = instr[0]
    if typ == 'S':
        L = float(instr[1]) * multipliers[param_idx]
        return x + L * math.cos(theta), y + L * math.sin(theta), theta, param_idx + 1
    if typ != 'C':
        return x, y, theta, param_idx

    angle_deg, radius, clothoid_len, k = instr[1:5]
    angle = math.radians(float(angle_deg)) * multipliers[param_idx]
    sign = 1 if angle > 0 else -1
    entry_start = theta
    ix, iy, dtheta1 = _integrate_clothoid_discrete(int(clothoid_len), float(k), sign, theta, reverse=False)
    x += ix
    y += iy
    theta += dtheta1

    arc_angle = angle - 2 * (theta - entry_start)
    arc_curvature = sign / float(radius)
    arc_length = int(abs(float(radius) * arc_angle))
    for _ in range(arc_length):
        theta += arc_curvature
        x += math.cos(theta)
        y += math.sin(theta)

    ix2, iy2, dtheta2 = _integrate_clothoid_discrete(int(clothoid_len), float(k), sign, theta, reverse=True)
    x += ix2
    y += iy2
    theta += dtheta2
    return x, y, theta, param_idx + 1


def _apply_dict_instruction_discrete(instr: dict, multipliers: List[float], param_idx: int, x: float, y: float, theta: float) -> Tuple[float, float, float, int]:
    typ = instr.get('type', '').upper()
    if typ == 'S':
        L = float(instr.get('length_m', 50)) * multipliers[param_idx]
        return x + L * math.cos(theta), y + L * math.sin(theta), theta, param_idx + 1
    if typ != 'C':
        return x, y, theta, param_idx

    angle = math.radians(float(instr.get('angle_deg', 45))) * multipliers[param_idx]
    radius = float(instr.get('radius_m', 80))
    clothoid = float(instr.get('clothoid_len', 50))
    k = float(instr.get('k', 0.00009))
    sign = 1 if angle > 0 else -1
    ix, iy, dtheta1 = _integrate_clothoid_continuous(clothoid, k, sign, theta)
    x += ix
    y += iy
    theta += dtheta1
    x += radius * (math.sin(theta + angle) - math.sin(theta))
    y += -radius * (math.cos(theta + angle) - math.cos(theta))
    theta += angle
    ix2, iy2, dtheta2 = _integrate_clothoid_continuous(clothoid, k, sign, theta)
    x += ix2
    y += iy2
    theta += dtheta2
    return x, y, theta, param_idx + 1


def _apply_tuple_instruction_continuous(instr: Any, multipliers: List[float], param_idx: int, x: float, y: float, theta: float) -> Tuple[float, float, float, int]:
    typ = instr[0]
    if typ == 'S':
        L = float(instr[1]) * multipliers[param_idx]
        return x + L * math.cos(theta), y + L * math.sin(theta), theta, param_idx + 1
    if typ != 'C':
        return x, y, theta, param_idx

    angle_deg, radius, clothoid_len, k = instr[1:5]
    angle = math.radians(float(angle_deg)) * multipliers[param_idx]
    sign = 1 if angle > 0 else -1
    ix, iy, dtheta1 = _integrate_clothoid_continuous(float(clothoid_len), float(k), sign, theta)
    x += ix
    y += iy
    theta += dtheta1
    x += float(radius) * (math.sin(theta + angle) - math.sin(theta))
    y += -float(radius) * (math.cos(theta + angle) - math.cos(theta))
    theta += angle
    ix2, iy2, dtheta2 = _integrate_clothoid_continuous(float(clothoid_len), float(k), sign, theta)
    x += ix2
    y += iy2
    theta += dtheta2
    return x, y, theta, param_idx + 1


def _apply_dict_instruction_continuous(instr: dict, multipliers: List[float], param_idx: int, x: float, y: float, theta: float) -> Tuple[float, float, float, int]:
    typ = instr.get('type', '').upper()
    if typ == 'S':
        L = float(instr.get('length_m', 50)) * multipliers[param_idx]
        return x + L * math.cos(theta), y + L * math.sin(theta), theta, param_idx + 1
    if typ != 'C':
        return x, y, theta, param_idx

    angle = math.radians(float(instr.get('angle_deg', 45))) * multipliers[param_idx]
    radius = float(instr.get('radius_m', 80))
    clothoid = float(instr.get('clothoid_len', 50))
    k = float(instr.get('k', 0.00009))
    sign = 1 if angle > 0 else -1
    ix, iy, dtheta1 = _integrate_clothoid_continuous(clothoid, k, sign, theta)
    x += ix
    y += iy
    theta += dtheta1
    x += radius * (math.sin(theta + angle) - math.sin(theta))
    y += -radius * (math.cos(theta + angle) - math.cos(theta))
    theta += angle
    ix2, iy2, dtheta2 = _integrate_clothoid_continuous(clothoid, k, sign, theta)
    x += ix2
    y += iy2
    theta += dtheta2
    return x, y, theta, param_idx + 1


def _simulate_primitives_impl(instructions: List[Any], multipliers: List[float]) -> Tuple[float, float, float]:
    """Implementation body extracted for lower cognitive complexity at entrypoint."""
    x = 0.0
    y = 0.0
    theta = 0.0
    param_idx = 0

    for instr in instructions:
        if isinstance(instr, (list, tuple)):
            x, y, theta, param_idx = _apply_tuple_instruction_discrete(instr, multipliers, param_idx, x, y, theta)
        elif isinstance(instr, dict):
            x, y, theta, param_idx = _apply_dict_instruction_discrete(instr, multipliers, param_idx, x, y, theta)
        else:
            continue

    theta = _wrap_angle(theta)
    return x, y, theta


def _simulate_primitives_continuous(instructions: List[Any], multipliers: List[float]) -> Tuple[float, float, float]:
    """Continuous integral simulation for initial solve (uses quad)."""
    return _simulate_primitives_continuous_impl(instructions, multipliers)


def _simulate_primitives_continuous_impl(instructions: List[Any], multipliers: List[float]) -> Tuple[float, float, float]:
    """Implementation body extracted for lower cognitive complexity at entrypoint."""
    x = 0.0
    y = 0.0
    theta = 0.0
    param_idx = 0

    for instr in instructions:
        if isinstance(instr, (list, tuple)):
            x, y, theta, param_idx = _apply_tuple_instruction_continuous(instr, multipliers, param_idx, x, y, theta)
        elif isinstance(instr, dict):
            x, y, theta, param_idx = _apply_dict_instruction_continuous(instr, multipliers, param_idx, x, y, theta)
        else:
            continue

    theta = _wrap_angle(theta)
    return x, y, theta


def _build_param_list(instructions: List[Any]) -> Tuple[List[int], List[float]]:
    """Return indices of adjustable instructions and initial multipliers.

    We create one multiplier per S or C primitive in order.
    """
    indices = []
    inits = []
    for i, instr in enumerate(instructions):
        if isinstance(instr, (list, tuple)):
            typ = instr[0]
            if typ in ('S', 'C'):
                indices.append(i)
                inits.append(1.0)
        elif isinstance(instr, dict):
            typ = instr.get('type', '').upper()
            if typ in ('S', 'C'):
                indices.append(i)
                inits.append(1.0)
    return indices, inits


def solve_closure(instructions: List[Any], max_nfev: int = 500) -> Tuple[bool, List[float], dict]:
    """Solve for multipliers that close the instruction sequence.

    Returns success flag, multipliers list (same length as number of adjustable
    primitives), and diagnostics.
    """
    indices, inits = _build_param_list(instructions)
    if not indices:
        return False, [], {'reason': 'no adjustable primitives'}

    def residuals_discrete(p):
        muls = list(p)
        x, y, theta = _simulate_primitives(instructions, muls)
        r1 = x
        r2 = y
        r3 = _wrap_angle(theta - 2 * math.pi)
        return [r1, r2, r3]

    # Stage 1: continuous least-squares to get a good initial guess
    p0 = np.array(inits)
    lower = np.maximum(CLOSURE_PARAM_MIN, p0 * 0.2)
    upper = np.minimum(CLOSURE_PARAM_MAX, p0 * 5.0)

    def residuals_continuous(p):
        muls = list(p)
        x, y, theta = _simulate_primitives_continuous(instructions, muls)
        r1 = x
        r2 = y
        r3 = _wrap_angle(theta - 2 * math.pi)
        reg = [(m - 1.0) * CLOSURE_REGULARIZATION_WEIGHT for m in muls]
        return [r1, r2, r3] + reg

    try:
        res_cont = least_squares(residuals_continuous, p0, bounds=(lower, upper), max_nfev=max_nfev)
    except Exception:
        res_cont = None

    if res_cont is not None and res_cont.success:
        p_init = np.array(res_cont.x)
    else:
        p_init = p0

    # Stage 2: refine using discrete simulation with a derivative-free optimizer
    def obj_discrete(p):
        r = residuals_discrete(p)
        return float(np.linalg.norm(r))

    # Try a more robust derivative-free optimizer (Powell), with Nelder-Mead fallback
    try:
        res2, method_used = _minimize_discrete_with_fallback(obj_discrete, p_init)
    except Exception as e:
        diagnostics = {'reason': 'minimize failed', 'error': str(e)}
        return False, list(p_init), diagnostics

    final_params = np.clip(res2.x, CLOSURE_PARAM_MIN, CLOSURE_PARAM_MAX)
    x, y, theta = _simulate_primitives(instructions, list(final_params))
    pos_norm = float(np.linalg.norm([x, y]))
    ang_err = abs(_wrap_angle(theta - 2 * math.pi))
    # Success if position is closed tightly and heading error is reasonable
    success = (pos_norm < CLOSURE_POSITION_TOLERANCE_M) and (ang_err < CLOSURE_ANGLE_TOLERANCE_RAD)
    diagnostics = {
        'cont_success': bool(res_cont.success) if res_cont is not None else False,
        'minimize_success': res2.success,
        'minimize_method': method_used,
        'minimize_nit': int(getattr(res2, 'nit', 0)),
        'minimize_fun': float(res2.fun),
        'pos_norm': pos_norm,
        'ang_err_rad': ang_err
    }
    return success, list(final_params), diagnostics


def apply_multipliers_to_instructions(instructions: List[Any], multipliers: List[float]) -> None:
    """Mutate instructions in place applying multipliers to S lengths and C angles."""
    param_idx = 0
    for i, instr in enumerate(instructions):
        if isinstance(instr, (list, tuple)):
            typ = instr[0]
            if typ == 'S':
                L = int(float(instr[1]) * multipliers[param_idx])
                instructions[i] = ('S', L)
                param_idx += 1
            elif typ == 'C':
                angle_deg, radius, clothoid_len, k = instr[1:5]
                new_angle = float(angle_deg) * multipliers[param_idx]
                instructions[i] = ('C', new_angle, radius, clothoid_len, k)
                param_idx += 1
        elif isinstance(instr, dict):
            typ = instr.get('type', '').upper()
            if typ == 'S':
                L = float(instr.get('length_m', 50)) * multipliers[param_idx]
                instr['length_m'] = float(L)
                param_idx += 1
            elif typ == 'C':
                ang = float(instr.get('angle_deg', 45)) * multipliers[param_idx]
                instr['angle_deg'] = float(ang)
                param_idx += 1
