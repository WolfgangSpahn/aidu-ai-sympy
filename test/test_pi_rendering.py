from sympy import symbols, Rational, pi, sin, parse_expr
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast
from sympy import Mul, Pow

x, y = symbols('x y')

# Test: -1*pi*2^-1 should render as -pi/2
# Build it programmatically
neg_pi_over_2 = Mul(Rational(-1, 2), pi)
expr = y**2 + sin(Rational(1,3)*(1 + x) + neg_pi_over_2)

print("Testing -pi/2 rendering:")
rich_linear_ast(expr)
