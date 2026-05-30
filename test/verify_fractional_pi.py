from sympy import symbols, Mul, Rational, pi
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast

# Directly test -pi/2 rendering
expr = Mul(Rational(-1, 2), pi, evaluate=False)
print("Expression:", expr)
rich_linear_ast(expr)

# Test with addition to prevent simplify into sin
x = symbols('x')
expr2 = x - pi/2
print("\nExpression 2:", expr2)
rich_linear_ast(expr2)
