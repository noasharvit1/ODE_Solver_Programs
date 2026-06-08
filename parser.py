"""
parser.py
Parses the user-entered ODE string and initial conditions into SymPy objects.
"""
 
import re
import sympy as sp
 
 
def _fix_implicit_multiplication(s: str) -> str:
    """
    Insert missing '*' operators before SymPy substitution happens.
    Works on the raw user string where y, x are still single letters.
 
    Rules applied (in order):
      1. digit immediately before a letter or '(':  2x → 2*x,  3( → 3*(
      2. 'x' immediately before 'y':                xy → x*y
      3. 'y' immediately before 'x':                yx → y*x
    """
    # Rule 1: digit → letter / open-paren
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    # Rule 2 & 3: adjacent x and y (with optional whitespace)
    s = re.sub(r'\bx\s+y\b', 'x*y', s)
    s = re.sub(r'\by\s+x\b', 'y*x', s)
    # Direct adjacency without space (after rule 1 digits are already separated)
    s = re.sub(r'(?<!\w)x(?=y)', 'x*', s)
    s = re.sub(r'(?<!\w)y(?=x)', 'y*', s)
    return s
 
 
def parse_ode(equation_str: str):
    """
    Parse an ODE string like "y'' + 2*y' + y = 0" into a SymPy Eq.
 
    Returns
    -------
    eq      : sp.Eq          – the equation as a SymPy equality
    order   : int            – 1 or 2
    x       : sp.Symbol
    y       : sp.Function
    """
    x = sp.Symbol('x')
    y = sp.Function('y')

    # Handle plain dy/dx notation before the differential form block
    equation_str = re.sub(r'\bdy\s*/\s*dx\b', "y'", equation_str)

    # ── 0. Pre-processing for differential form (M*dx + N*dy = 0) ──
    if 'dx' in equation_str and 'dy' in equation_str:
        # Add multiplication sign (*) if missing before dx or dy 
        # (e.g., 'y dx' becomes 'y*dx', or ')dy' becomes ')*dy')
        equation_str = re.sub(r'([\)\w])\s*d([xy])', r'\1*d\2', equation_str)
        
        # Mathematical conversion to the standard derivative format the code already solves
        # Dividing the entire equation by dx: M + N*(dy/dx) = 0 -> M*1 + N*y' = 0
        equation_str = equation_str.replace('dx', '1')
        equation_str = equation_str.replace('dy', "y'")
    
    equation_str = equation_str.replace('^', '**')

    # ── 1. Check for unsupported high-order derivatives FIRST ──────────────
    max_primes = max(
        (len(m.group(1)) for m in re.finditer(r"y(''+)", equation_str)),
        default=0
    )
    if max_primes >= 3:
        raise ValueError(
            f"Equations of order {max_primes} are not supported.\n"
            "This program only handles 1st and 2nd order ODEs."
        )
 
    # ── 2. Auto-fix implicit multiplication on the raw string ──────────────
    expr_str = _fix_implicit_multiplication(equation_str)
 
    # ── 3. Determine order ─────────────────────────────────────────────────
    if "y''" in expr_str:
        order = 2
    elif "y'" in expr_str:
        order = 1
    else:
        raise ValueError("No derivative found. Make sure you use y' or y''.")
 
    # ── 4. Replace derivative / variable notation ──────────────────────────
    # Must replace y'' before y' to avoid partial matches
    expr_str = expr_str.replace("y''", "Derivative(y(x), x, 2)")
    expr_str = expr_str.replace("y'",  "Derivative(y(x), x)")
    # Bare 'y' (not part of another word / not already followed by '(') → y(x)
    expr_str = re.sub(r'(?<![a-zA-Z_])y(?!\s*\()', 'y(x)', expr_str)
 
    # ── 5. Split on '=' ────────────────────────────────────────────────────
    if '=' not in expr_str:
        raise ValueError("Equation must contain '='.")
 
    lhs_str, rhs_str = expr_str.split('=', 1)
 
    local_dict = {
        'x': x, 'y': y,
        'Derivative': sp.Derivative,
        'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos,
        'tan': sp.tan, 'log': sp.log, 'sqrt': sp.sqrt,
        'pi': sp.pi, 'E': sp.E,
    }
 
    # ── 6. Sympify ─────────────────────────────────────────────────────────
    try:
        lhs = sp.sympify(lhs_str.strip(), locals=local_dict)
        rhs = sp.sympify(rhs_str.strip(), locals=local_dict)
    except Exception as e:
        raise ValueError(
            "Could not parse the equation. Please check your syntax:\n"
            "  • Use ** or ^ for powers:  x**2  or  x^2\n"
            "  • Use y' and y'' for derivatives\n"
            f"  (Detail: {e})"
        )
 
    eq = sp.Eq(lhs, rhs)
    return eq, order, x, y
 
 
def parse_initial_conditions(order: int):
    """
    Prompt the user for initial conditions and return them as a dict
    suitable for dsolve's ics parameter.
    """
    x = sp.Symbol('x')
    y = sp.Function('y')
 
    x0 = sp.sympify(input("Enter the initial value for x (x0): ").strip())
    y0 = sp.sympify(input("Enter the initial value for y (y0): ").strip())
 
    ics = {y(x0): y0}
 
    if order == 2:
        dy0 = sp.sympify(input("Enter the initial value for y' (y'0): ").strip())
        ics[y(x).diff(x).subs(x, x0)] = dy0
 
    return ics, x0
 