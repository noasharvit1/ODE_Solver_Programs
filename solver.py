"""
solver.py
Solves the ODE symbolically using SymPy's dsolve.
"""

import sympy as sp


def solve_ode(eq: sp.Eq, y, x: sp.Symbol, hint: str, ics: dict):
    """
    Compute the general solution and then the particular solution.

    Parameters
    ----------
    eq   : sp.Eq     – the ODE
    y    : Function  – the unknown function symbol
    x    : Symbol
    hint : str       – dsolve hint from classifier
    ics  : dict      – initial conditions {y(x0): y0, ...}

    Returns
    -------
    general_sol   : sp.Eq   – solution with free constants
    particular_sol: sp.Eq   – solution with constants resolved
    """
    y_fn = y(x)

    # ── General solution ───────────────────────────────────────────────────
    try:
        general_sol = sp.dsolve(eq, y_fn, hint=hint)
    except Exception:
        # Fall back to SymPy's automatic choice
        general_sol = sp.dsolve(eq, y_fn)

    # ── Particular solution ────────────────────────────────────────────────
    try:
        particular_sol = sp.dsolve(eq, y_fn, hint=hint, ics=ics)
    except Exception:
        # Manual constant substitution as fallback
        particular_sol = _apply_ics_manually(general_sol, ics, x, y_fn)

    return general_sol, particular_sol


def _apply_ics_manually(general_sol: sp.Eq, ics: dict, x, y_fn):
    """
    Substitute ICs manually to solve for integration constants.
    """
    rhs = general_sol.rhs

    # Find free constants (C1, C2, …)
    free_consts = [s for s in rhs.free_symbols
                   if str(s).startswith('C') and str(s)[1:].isdigit()]

    equations = []
    for lhs_key, rhs_val in ics.items():
        # lhs_key is either y(x0) or Derivative(y(x), x).subs(x, x0)
        if isinstance(lhs_key, sp.core.function.AppliedUndef):
            # y(x0) = y0  →  substitute x = x0 into rhs
            x0 = lhs_key.args[0]
            expr = rhs.subs(x, x0) - rhs_val
        else:
            # Derivative condition
            x0 = lhs_key.args[1][1]   # extract x0 from Subs/Derivative
            drhs = sp.diff(rhs, x)
            expr = drhs.subs(x, x0) - rhs_val
        equations.append(expr)

    sol = sp.solve(equations, free_consts)
    particular_rhs = rhs.subs(sol)
    particular_rhs = sp.simplify(particular_rhs)
    return sp.Eq(y_fn, particular_rhs)
