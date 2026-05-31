"""
plotter.py
Plots the particular solution over its domain of existence.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp


def plot_solution(particular_sol: sp.Eq, x: sp.Symbol,
                  x0, a, b, equation_str: str):
    """
    Plot y(x) over the interval (a, b), centred around x0.

    Parameters
    ----------
    particular_sol : sp.Eq   – particular solution
    x              : Symbol
    x0             : x-value of the initial condition (for marking)
    a, b           : domain endpoints (may be ±∞)
    equation_str   : original equation string (for title)
    """
    expr = particular_sol.rhs
    f    = sp.lambdify(x, expr, modules=['numpy'])

    x0_float = float(sp.sympify(x0).evalf())

    # Determine plot window
    MARGIN = 3.0   # units away from x0 when domain is infinite

    a_float = -np.inf if a == -sp.oo else float(a.evalf())
    b_float =  np.inf if b ==  sp.oo else float(b.evalf())

    plot_a = (x0_float - MARGIN) if np.isinf(a_float) else (a_float + 1e-3)
    plot_b = (x0_float + MARGIN) if np.isinf(b_float) else (b_float - 1e-3)

    # Make sure window is not degenerate
    if plot_b - plot_a < 0.5:
        plot_a = x0_float - MARGIN
        plot_b = x0_float + MARGIN

    xs = np.linspace(plot_a, plot_b, 800)

    with np.errstate(divide='ignore', invalid='ignore'):
        ys = f(xs)
        if np.isscalar(ys):
            ys = np.full_like(xs, ys, dtype=float)
        ys = np.where(np.isfinite(ys), ys, np.nan)

    # Clip extreme values for readability
    y_median = np.nanmedian(ys)
    y_range  = 10 * max(np.nanstd(ys), 1.0)
    ys = np.where(np.abs(ys - y_median) < y_range, ys, np.nan)

    y0_val = float(particular_sol.rhs.subs(x, x0_float).evalf())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, ys, color='royalblue', linewidth=2.0, label='y(x)')
    ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.7, linestyle='--')
    ax.plot(x0_float, y0_val, 'ro', markersize=7, label=f'IC: ({x0_float}, {y0_val:.3g})')

    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y(x)', fontsize=13)
    ax.set_title(f'Solution of: {equation_str}', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()
