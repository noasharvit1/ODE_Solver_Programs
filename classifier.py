"""
classifier.py
Classifies a parsed ODE into one of the supported types.
"""

import sympy as sp


class UnsupportedEquationError(Exception):
    """Raised when the equation type is not supported."""
    pass


def classify_ode(eq: sp.Eq, order: int, x: sp.Symbol, y):
    """
    Attempt to classify the ODE.

    Returns
    -------
    label : str   – human-readable classification
    hint  : str   – dsolve hint to use

    Raises
    ------
    UnsupportedEquationError  – if no supported classification is found.
    """
    y_fn = y(x)
    expr = sp.expand(eq.lhs - eq.rhs)   # bring everything to one side

    if order == 1:
        return _classify_first_order(eq, expr, x, y_fn)
    elif order == 2:
        return _classify_second_order(eq, expr, x, y_fn)
    else:
        raise UnsupportedEquationError(
            "Only 1st and 2nd order ODEs are supported."
        )


# ── First-order classifiers ────────────────────────────────────────────────

def _classify_first_order(eq, expr, x, y_fn):
    dydx = y_fn.diff(x)

    # --- Separable ----------------------------------------------------------
    # Try SymPy's built-in hint detection
    try:
        hints = sp.classify_ode(eq, y_fn)
        if 'separable' in hints:
            return "First-order separable equation", "separable"
    except Exception:
        pass

    # --- Bernoulli ----------------------------------------------------------
    # y' + P(x)*y = Q(x)*y^n  with n≠0,1
    try:
        hints = sp.classify_ode(eq, y_fn)
        if 'Bernoulli' in hints:
            return "First-order Bernoulli equation", "Bernoulli"
    except Exception:
        pass

    # --- Linear  ------------------------------------------------------------
    # Rewrite as y' = f(x,y); check linearity in y
    try:
        hints = sp.classify_ode(eq, y_fn)
        if '1st_linear' in hints:
            return "First-order linear equation", "1st_linear"
    except Exception:
        pass

    # --- Exact  -------------------------------------------------------------
    try:
        hints = sp.classify_ode(eq, y_fn)
        if '1st_exact' in hints:
            return "First-order exact equation", "1st_exact"
    except Exception:
        pass

    # --- Fallback: ask SymPy for any hint it can handle -------------------
    try:
        hints = sp.classify_ode(eq, y_fn)
        # Filter to hints we consider "supported"
        supported_hints = {
            'separable', '1st_linear', '1st_exact',
            'Bernoulli', '1st_homogeneous_coeff_best',
        }
        usable = [h for h in hints if h in supported_hints]
        if usable:
            label_map = {
                'separable': 'First-order separable equation',
                '1st_linear': 'First-order linear equation',
                '1st_exact': 'First-order exact equation',
                'Bernoulli': 'First-order Bernoulli equation',
                '1st_homogeneous_coeff_best': 'First-order homogeneous equation',
            }
            h = usable[0]
            return label_map.get(h, f"First-order equation ({h})"), h
    except Exception:
        pass

    raise UnsupportedEquationError(
        "This first-order equation does not match any supported type "
        "(separable, linear, exact, Bernoulli)."
    )


# ── Second-order classifiers ───────────────────────────────────────────────

def _classify_second_order(eq, expr, x, y_fn):
    """
    Supported: linear with constant coefficients (homogeneous or with
    undetermined-coefficients / variation-of-parameters RHS).
    """
    d2ydx2 = y_fn.diff(x, 2)
    dydx   = y_fn.diff(x)

    # Check linearity: coefficients of y'', y', y must be constants (no y)
    try:
        # Collect coefficients
        a_coeff = expr.coeff(d2ydx2)
        # Remove the second-derivative term and collect the rest
        remainder = sp.expand(expr - a_coeff * d2ydx2)
        b_coeff = remainder.coeff(dydx)
        remainder2 = sp.expand(remainder - b_coeff * dydx)
        c_coeff = remainder2.coeff(y_fn)
        g_expr  = sp.expand(remainder2 - c_coeff * y_fn)

        # All coefficients must be independent of x *and* y for const-coeff
        for coeff in (a_coeff, b_coeff, c_coeff):
            if coeff.has(x) or coeff.has(y_fn):
                raise UnsupportedEquationError(
                    "Second-order equations with variable coefficients are not supported."
                )

        if a_coeff == 0:
            raise UnsupportedEquationError(
                "The leading coefficient of y'' is zero."
            )

        # g_expr is the forcing term; must not contain y or derivatives
        if g_expr.has(y_fn) or g_expr.has(dydx):
            raise UnsupportedEquationError(
                "This second-order equation appears to be nonlinear."
            )

        # Try SymPy hints
        hints = sp.classify_ode(eq, y_fn)
        preferred = [
            'nth_linear_constant_coeff_homogeneous',
            'nth_linear_constant_coeff_undetermined_coefficients',
            'nth_linear_constant_coeff_variation_of_parameters',
        ]
        for h in preferred:
            if h in hints:
                label = "Second-order linear ODE with constant coefficients"
                if g_expr == 0:
                    label += " (homogeneous)"
                else:
                    label += " (non-homogeneous)"
                return label, h

        # If SymPy can classify it under any nth_linear_constant_coeff hint
        usable = [h for h in hints if 'nth_linear_constant_coeff' in h]
        if usable:
            label = "Second-order linear ODE with constant coefficients"
            return label, usable[0]

    except UnsupportedEquationError:
        raise
    except Exception:
        pass

    raise UnsupportedEquationError(
        "This second-order equation does not match any supported type "
        "(linear with constant coefficients)."
    )
