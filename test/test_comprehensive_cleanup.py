from sympy import symbols, Rational, pi, sin, Add, Mul, Pow, cos, srepr
from src.aidu.ai.sympy.ast.pretty.linear import cleanup_ast, rich_linear_ast

x, y = symbols('x y')

print("=== Comprehensive Cleanup Test ===\n")

# Reconstruct the exact pattern from user's comment:
# y^2 + cos((1/3*(1 + x) + -1*pi*2^-1))
# Where -1*pi*2^-1 should become -pi/2

inner_term = Mul(Rational(-1, 1), pi, Pow(2, -1, evaluate=False), evaluate=False)
cos_arg = Add(Mul(Rational(1, 3), 1 + x, evaluate=False), inner_term, evaluate=False)
expr = Add(y**2, cos(cos_arg, evaluate=False), evaluate=False)

print("Original pattern (user's comment):")
print(f"  y^2 + cos((1/3*(1 + x) + -1*pi*2^-1))")
print(f"  srepr: {srepr(expr)}")
print(f"  Rendered:")
rich_linear_ast(expr)

print("\n" + "="*50)
print("After cleanup_ast:")
cleaned_expr = cleanup_ast(expr)
print(f"  srepr: {srepr(cleaned_expr)}")
rich_linear_ast(cleaned_expr)

print("\n" + "="*50)
print("Simulating improvement: Mul(pi, 1/2) instead of Mul(-1, pi, 1/2)")
improved_inner = Mul(pi, Rational(-1, 2), evaluate=False)
improved_cos_arg = Add(Mul(Rational(1, 3), 1 + x, evaluate=False), improved_inner, evaluate=False)
improved_expr = Add(y**2, cos(improved_cos_arg, evaluate=False), evaluate=False)
print(f"  srepr: {srepr(improved_expr)}")
rich_linear_ast(improved_expr)
