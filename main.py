"""
main.py
Entry point for the Symbolic ODE Solver.
"""
 
import sympy as sp
from parser     import parse_ode, parse_initial_conditions
from classifier import classify_ode, UnsupportedEquationError
from solver     import solve_ode
from utils      import find_domain
from verifier   import verify_solution
from plotter    import plot_solution
 
UNSUPPORTED_MSG = (
    "\nThis program supports only the following equation types:\n"
    "  1. First-order separable equations\n"
    "  2. First-order linear equations\n"
    "  3. First-order exact equations\n"
    "  4. First-order Bernoulli equations\n"
    "  5. Second-order linear ODEs with constant coefficients"
)
 
 
def _print_solution(label: str, sol):
    """
    Print a solution (sp.Eq or list of sp.Eq) dynamically by showing
    both LHS and RHS to support both explicit and implicit solutions.
    """
    print(f"{label}:")
    if isinstance(sol, list):
        for i, s in enumerate(sol, 1):
            lhs = sp.simplify(s.lhs)
            rhs = sp.simplify(s.rhs)
            print(f"  {lhs} = {rhs}")
    else:
        lhs = sp.simplify(sol.lhs)
        rhs = sp.simplify(sol.rhs)
        print(f"  {lhs} = {rhs}")
    print()
 
 
def main():
    print("=" * 60)
    print("       Symbolic ODE Solver")
    print("=" * 60)
    print("Supported types:")
    print("  • 1st-order: separable, linear, exact, Bernoulli")
    print("  • 2nd-order: linear with constant coefficients")
    print()
 
    # ── 1. Input ────────────────────────────────────────────────────────────
    equation_str = input("Please enter the differential equation: ").strip()
 
    try:
        eq, order, x, y = parse_ode(equation_str)
    except ValueError as e:
        msg = str(e)
        if "not supported" in msg:
            print(f"\n[UNSUPPORTED] {msg}")
            print(UNSUPPORTED_MSG)
        else:
            print(f"\n[ERROR] {msg}")
        return
 
    ics, x0 = parse_initial_conditions(order)
 
    print()
 
    # ── 2. Classify ─────────────────────────────────────────────────────────
    try:
        label, hint = classify_ode(eq, order, x, y)
    except UnsupportedEquationError as e:
        print(f"[UNSUPPORTED] {e}")
        print(UNSUPPORTED_MSG)
        return
 
    print(f"Equation type: {label}")
    print()
 
    # ── 3. Solve ────────────────────────────────────────────────────────────
    try:
        general_sol, particular_sol = solve_ode(eq, y, x, hint, ics)
    except Exception as e:
        print(f"[ERROR] Could not solve the equation: {e}")
        return
 
    _print_solution("General solution", general_sol)
    _print_solution("Particular solution", particular_sol)
 
    # ── Check for Implicit Solution ─────────────────────────────────────────
    sol_to_check = particular_sol[0] if isinstance(particular_sol, list) else particular_sol
    
    # A solution is implicit if the LHS is not strictly y(x) OR the RHS still contains y(x)
    is_implicit = (sol_to_check.lhs != y(x)) or sol_to_check.rhs.has(y(x))
 
    if is_implicit:
        print("Domain:")
        print("  Analysis skipped for implicit solutions.\n")
        
        print("Verification:")
        print("  Cannot automatically verify the solution because an implicit solution was obtained. [FALSE]\n")
        
        print("[WARNING] Cannot plot the function because an implicit solution was obtained.")
        return  # Gracefully exit since further explicit analysis/plotting is impossible
 
    # ── 4. Domain (Only executed if explicit) ───────────────────────────────
    part_for_domain = particular_sol[0] if isinstance(particular_sol, list) else particular_sol
    try:
        domain_str, a, b = find_domain(part_for_domain, x, x0)
    except Exception:
        domain_str, a, b = "(-oo, oo)", -sp.oo, sp.oo
 
    print(f"Domain:\n  {domain_str}\n")
 
    # ── 5. Verify (Only executed if explicit) ───────────────────────────────
    try:
        verified = verify_solution(eq, part_for_domain, x, y)
    except Exception:
        verified = False
 
    print("Verification:")
    if verified:
        print("  The solution satisfies the differential equation. [TRUE]\n")
    else:
        print("  Could not automatically verify the solution. [FALSE]\n")
 
    # ── 6. Plot (Only executed if explicit) ──────────────────────────────────
    try:
        plot_solution(part_for_domain, x, x0, a, b, equation_str)
    except Exception as e:
        print(f"[WARNING] Could not generate plot: {e}")
 
 
if __name__ == "__main__":
    main()