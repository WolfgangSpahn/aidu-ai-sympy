from sympy import symbols, Rational, pi, sin, Add, Mul, Pow, cos, srepr
from src.aidu.ai.sympy.ast.pretty.linear import cleanup_ast, rich_linear_ast

x, y = symbols('x y')

# Test specifically for fraction-like Mul
expr = Mul(pi, Rational(1, 2), evaluate=False)
print("Mul(pi, 1/2):")
print(f"  srepr: {srepr(expr)}")
rich_linear_ast(expr)

expr2 = Mul(1, pi, Pow(2, -1, evaluate=False), evaluate=False)
print("\nMul(1, pi, 2^-1):")
print(f"  srepr: {srepr(expr2)}")
rich_linear_ast(expr2)

cleaned2 = cleanup_ast(expr2)
print("\nAfter cleanup:")
print(f"  srepr: {srepr(cleaned2)}")
rich_linear_ast(cleaned2)
