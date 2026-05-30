from sympy import symbols, sin, Rational
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast

x, y = symbols('x y')
expr = y**2 + sin(Rational(1,3)*x + Rational(1,3))
print("Testing cleaned up parentheses:")
rich_linear_ast(expr)
