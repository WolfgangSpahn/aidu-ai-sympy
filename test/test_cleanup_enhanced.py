from sympy import symbols, Rational, pi, sin, Add, Mul, Pow, cos
from src.aidu.ai.sympy.ast.pretty.linear import cleanup_ast, rich_linear_ast

x, y = symbols('x y')

# Test the user's pattern: -1*pi*2^-1 should become -pi/2
expr_parts = Mul(Rational(-1, 1), pi, Pow(2, -1, evaluate=False), evaluate=False)
print("Pattern: -1*pi*2^-1")
print(f"  Original: {expr_parts}")
cleaned = cleanup_ast(expr_parts)
print(f"  Cleaned:  {cleaned}")

# Full expression from user's comment
expr = y**2 + cos(Rational(1,3)*(1 + x) + Mul(Rational(-1, 2), pi, evaluate=False))
print("\nFull expression rendering:")
rich_linear_ast(expr)
