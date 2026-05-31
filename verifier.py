"""
verifier.py
Verifies the particular solution by back-substitution into the original ODE.
"""

import sympy as sp


def verify_solution(eq: sp.Eq, particular_sol: sp.Eq,
                    x: sp.Symbol, y) -> bool:
    """
    Substitute the particular solution into the original ODE and check
    whether the resulting expression simplifies to an identity (0 == 0).

    Returns
    -------
    True   – solution is verified
    False  – verification failed
    """
    y_fn     = y(x)
    sol_expr = particular_sol.rhs   # the explicit y(x) expression

    # Build substitution: replace y(x) and its derivatives
    ode_expr = eq.lhs - eq.rhs

    # Substitute derivatives first (higher order first to avoid partial match)
    d2 = sp.diff(sol_expr, x, 2)
    d1 = sp.diff(sol_expr, x)

    substituted = ode_expr
    substituted = substituted.subs(y_fn.diff(x, 2), d2)
    substituted = substituted.subs(y_fn.diff(x),    d1)
    substituted = substituted.subs(y_fn,             sol_expr)

    # Simplify the result
    residual = sp.simplify(substituted)

    return residual == 0
