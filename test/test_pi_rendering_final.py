from sympy import symbols, Rational, pi, sin, Add
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast

x, y = symbols('x y')

# Construct the expression manually to avoid sin(z - pi/2) -> -cos(z) simplification
inner = Add(Rational(1,3)*(1 + x), -pi/2, evaluate=False)
expr = y**2 + sin(inner, evaluate=False)

print("Expression:", expr)
print("Rendering with -pi/2:")
rich_linear_ast(expr)
