from sympy import symbols, Rational, pi, Mul
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast

x, y = symbols('x y')

# Test: -pi/2
neg_pi_over_2 = Mul(Rational(-1, 2), pi, evaluate=False)

print("Testing -pi/2 rendering (evaluate=False):")
rich_linear_ast(neg_pi_over_2)

# Test: x - pi/2
expr = x + neg_pi_over_2
print("\nTesting x - pi/2 rendering:")
rich_linear_ast(expr)
