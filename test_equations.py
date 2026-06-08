"""
test_equations.py
Unit tests for the Symbolic ODE Solver project.
"""

import unittest
import sympy as sp

# Importing components directly from your project modules
from parser     import parse_ode
from classifier import classify_ode, UnsupportedEquationError
from solver     import solve_ode


class TestODESolverFramework(unittest.TestCase):

    # ============================================================
    # 1. TEST CASES FOR SUPPORTED EQUATIONS & NOTATIONS
    # ============================================================

    def test_separable_equations_standard(self):
        """Test 1st-Order Separable Equations with standard notation."""
        # Example A: y' = 2xy (Implicit multiplication check)
        eq_str_1 = "y' = 2xy"
        eq1, order1, x1, y1 = parse_ode(eq_str_1)
        label1, _ = classify_ode(eq1, order1, x1, y1)
        self.assertEqual(label1, "First-order separable equation")

        # Example B: y' = x**2/y**2 (Standard Python power notation)
        eq_str_2 = "y' = x**2/y**2"
        eq2, order2, x2, y2 = parse_ode(eq_str_2)
        label2, _ = classify_ode(eq2, order2, x2, y2)
        self.assertEqual(label2, "First-order separable equation")

    def test_power_caret_notation(self):
        """Test that the caret symbol (^) is correctly handled as a power."""
        # Example: y' = x^2 (As documented in the updated README)
        eq_str = "y' = x^2"
        eq, order, x, y = parse_ode(eq_str)
        label, _ = classify_ode(eq, order, x, y)
        self.assertEqual(label, "First-order separable equation")

    def test_leibniz_notation_first_order(self):
        """Test that Leibniz notation (dy/dx) is fully supported for 1st-order."""
        # Example: dy/dx + 2xy = x
        eq_str = "dy/dx + 2xy = x"
        eq, order, x, y = parse_ode(eq_str)
        label, _ = classify_ode(eq, order, x, y)
        self.assertEqual(label, "First-order separable equation")

    def test_linear_first_order_equations(self):
        """Test 1st-Order Linear Equations (Evaluating classification hierarchy)."""
        # Example: y' + y/x = sin(x)/x
        eq_str = "y' + y/x = sin(x)/x"
        eq, order, x, y = parse_ode(eq_str)
        label, _ = classify_ode(eq, order, x, y)
        # Note: Handled as Bernoulli since it matches the general case where n=0
        self.assertEqual(label, "First-order Bernoulli equation")

    def test_exact_equations(self):
        """Test 1st-Order Exact Equations."""
        # Example: exp(y) + (x*exp(y) + 2y)*y' = 0
        eq_str = "exp(y) + (x*exp(y) + 2y)*y' = 0"
        eq, order, x, y = parse_ode(eq_str)
        label, _ = classify_ode(eq, order, x, y)
        self.assertEqual(label, "First-order exact equation")

    def test_bernoulli_equations(self):
        """Test 1st-Order Bernoulli Equations."""
        # Example A: y' + y/x = x*y**2
        eq_str_1 = "y' + y/x = x*y**2"
        eq1, order1, x1, y1 = parse_ode(eq_str_1)
        label1, _ = classify_ode(eq1, order1, x1, y1)
        self.assertEqual(label1, "First-order Bernoulli equation")

        # Example B: y' - y = x*y**5
        eq_str_2 = "y' - y = x*y**5"
        eq2, order2, x2, y2 = parse_ode(eq_str_2)
        label2, _ = classify_ode(eq2, order2, x2, y2)
        self.assertEqual(label2, "First-order Bernoulli equation")
    
    def test_second_order_linear_constant_coefficients(self):
        """Test 2nd-Order Linear ODEs with Constant Coefficients (Homogeneous)."""
        # Example: y'' + 2y' + y = 0
        eq_str = "y'' + 2y' + y = 0"
        eq, order, x, y = parse_ode(eq_str)
        label, _ = classify_ode(eq, order, x, y)
        self.assertEqual(label, "Second-order linear ODE with constant coefficients (homogeneous)")

    # ============================================================
    # 2. TEST CASES FOR UNSUPPORTED / EDGE CASES
    # ============================================================

    def test_nonlinear_second_order_unsupported(self):
        """Verify that nonlinear 2nd-order equations raise UnsupportedEquationError."""
        eq_str = "y'' + sin(y) = 0"
        eq, order, x, y = parse_ode(eq_str)
        
        with self.assertRaises(UnsupportedEquationError):
            classify_ode(eq, order, x, y)

    def test_unsupported_first_order_type(self):
        """Verify that an arbitrary unsupported 1st-order equation triggers UnsupportedEquationError."""
        eq_str = "y' + y/x = x**(y**2)"
        eq, order, x, y = parse_ode(eq_str)
        
        with self.assertRaises(UnsupportedEquationError):
            classify_ode(eq, order, x, y)

    def test_invalid_syntax_handling(self):
        """Verify that severe syntax errors (e.g., '^^') are caught during parsing and raise a ValueError."""
        invalid_eq = "y' = x^^2/y**2"
        
        with self.assertRaises(ValueError) as context:
            parse_ode(invalid_eq)
        
        self.assertIn("Could not parse the equation", str(context.exception))


if __name__ == '__main__':
    unittest.main()