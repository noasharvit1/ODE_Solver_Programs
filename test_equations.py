"""
test_equations.py
Automated tests to verify the classification and parsing of various ODE types.
"""

import unittest
import sympy as sp
from parser import parse_ode
from classifier import classify_ode, UnsupportedEquationError

class TestODESolver(unittest.TestCase):

    def check_equation(self, eq_str, expected_label_keyword, expected_hint):
        """
        A helper function to parse and classify an equation, 
        then check if the label and SymPy hint match our expectations.
        """
        eq, order, x, y = parse_ode(eq_str)
        label, hint = classify_ode(eq, order, x, y)

        self.assertIn(expected_label_keyword.lower(), label.lower())
        self.assertEqual(hint, expected_hint)

    # ── 1. Supported First-Order Equations ──────────────────────────────────

    def test_separable(self):
        self.check_equation("y' = y * x", "separable", "separable")

    def test_linear(self):
        self.check_equation("y' + 2*x*y = x", "linear", "1st_linear")

    def test_exact_differential_form(self):
        # Testing the exact equation using the dx/dy format
        eq_str = "(exp(x)*sin(y)-2*y*sin(x))*dx + (exp(x)*cos(y)+2*cos(x))*dy = 0"
        self.check_equation(eq_str, "exact", "1st_exact")

    def test_bernoulli(self):
        self.check_equation("y' + y = x*y**2", "bernoulli", "Bernoulli")

    def test_homogeneous(self):
        # The classification works, even if SymPy struggles to solve it later!
        self.check_equation("y' = (x+3*y)/(x-y)", "homogeneous", "1st_homogeneous_coeff_best")

    # ── 2. Supported Second-Order Equations ─────────────────────────────────

    def test_second_order_homogeneous(self):
        self.check_equation("y'' + 2*y' + y = 0", "homogeneous", "nth_linear_constant_coeff_homogeneous")

    def test_second_order_nonhomogeneous(self):
        self.check_equation("y'' + 4*y = sin(x)", "non-homogeneous", "nth_linear_constant_coeff_undetermined_coefficients")

    # ── 3. Edge Cases & Unsupported Equations ───────────────────────────────

    def test_unsupported_third_order(self):
        # The parser should catch 3rd order derivatives and raise a ValueError
        with self.assertRaises(ValueError) as context:
            parse_ode("y''' + y = 0")
        self.assertIn("Equations of order 3 are not supported", str(context.exception))

    def test_unsupported_nonlinear_second_order(self):
        # Variable coefficients in a 2nd order ODE are unsupported
        eq, order, x, y = parse_ode("y'' + y * y' = 0")
        with self.assertRaises(UnsupportedEquationError):
            classify_ode(eq, order, x, y)

    def test_implicit_multiplication_parser(self):
        # Testing that "2xy" is correctly parsed without crashing
        try:
            eq, order, x, y = parse_ode("y' + 2xy = 0")
            parsed_success = True
        except ValueError:
            parsed_success = False
        
        self.assertTrue(parsed_success, "Parser failed to fix implicit multiplication '2xy'")

    def test_unauthorized_variables(self):
        # Testing that variables other than x and y are rejected
        with self.assertRaises(ValueError) as context:
            parse_ode("y' + 2*t = 0")
        self.assertIn("Unsupported variables found", str(context.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)