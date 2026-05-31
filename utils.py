"""
utils.py
Domain-of-existence analysis for the particular solution.
"""

import sympy as sp


def find_domain(particular_sol: sp.Eq, x: sp.Symbol, x0):
    """
    Determine the maximal interval of existence centred around x0.

    Strategy
    --------
    1. Find real singularities of the solution expression.
    2. The valid interval is bounded by the nearest singularities on
       either side of x0.
    3. If no singularities exist → domain is (-∞, ∞).

    Returns
    -------
    domain_str : str   – human-readable interval, e.g. "(-oo, 3)"
    a, b       : sympy expressions for the endpoints
    """
    expr = particular_sol.rhs

    # Collect all potential singular points
    singularities = set()

    # 1. Denominators of rational sub-expressions
    _collect_denom_zeros(expr, x, singularities)

    # 2. Arguments of log must be > 0; find zeros of log arguments
    _collect_log_zeros(expr, x, singularities)

    # 3. Square-root arguments must be ≥ 0; find zeros
    _collect_sqrt_zeros(expr, x, singularities)

    # Filter to real finite singularities
    real_sings = []
    for s in singularities:
        try:
            s_val = complex(s)
            if abs(s_val.imag) < 1e-12:          # real
                real_sings.append(sp.re(s))
        except Exception:
            # symbolic – attempt is_real check
            if s.is_real or s.is_real is None:
                real_sings.append(s)

    if not real_sings:
        return "(-oo, oo)", -sp.oo, sp.oo

    # Sort
    try:
        real_sings = sorted(real_sings, key=lambda s: float(s.evalf()))
    except Exception:
        real_sings = sorted(real_sings, key=lambda s: s)

    x0_float = float(sp.sympify(x0).evalf())

    a = -sp.oo
    b =  sp.oo

    for s in real_sings:
        try:
            s_float = float(s.evalf())
        except Exception:
            continue
        if s_float < x0_float:
            a = s
        elif s_float > x0_float:
            b = s
            break

    # Format
    a_str = str(a) if a != -sp.oo else "-oo"
    b_str = str(b) if b !=  sp.oo else  "oo"
    domain_str = f"({a_str}, {b_str})"
    return domain_str, a, b


# ── helpers ────────────────────────────────────────────────────────────────

def _collect_denom_zeros(expr, x, out: set):
    for sub in sp.preorder_traversal(expr):
        if isinstance(sub, sp.Pow) and sub.exp.is_negative:
            base = sub.base
            zeros = sp.solve(base, x)
            for z in zeros:
                out.add(z)


def _collect_log_zeros(expr, x, out: set):
    for sub in sp.preorder_traversal(expr):
        if isinstance(sub, sp.log):
            arg = sub.args[0]
            zeros = sp.solve(arg, x)
            for z in zeros:
                out.add(z)


def _collect_sqrt_zeros(expr, x, out: set):
    for sub in sp.preorder_traversal(expr):
        if isinstance(sub, sp.Pow):
            exp = sub.exp
            base = sub.base
            # Fractional power with even denominator (square-root-like)
            if exp.is_Rational and exp.q % 2 == 0 and exp.p > 0:
                zeros = sp.solve(base, x)
                for z in zeros:
                    out.add(z)
