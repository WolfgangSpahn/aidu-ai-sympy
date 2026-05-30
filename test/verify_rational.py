from sympy import symbols, cos, Rational, pi
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast

x, y = symbols('x y')
# Expression with -pi/2 term
expr = y**2 + cos(Rational(1,3)*(1 + x) + -pi/2)
print("Testing improved rational coefficient rendering:")
rich_linear_ast(expr)
print("\n")

# Also test simple case
expr2 = x + -pi/2
print("Simple -pi/2 case:")
rich_linear_ast(expr2)
