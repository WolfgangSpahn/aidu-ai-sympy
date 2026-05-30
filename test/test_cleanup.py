from sympy import symbols, Rational, pi, sin, Mul, Pow
from src.aidu.ai.sympy.ast.pretty.linear import cleanup_ast
from rich.console import Console

x, y = symbols('x y')

print("=== Improved Cleanup Test ===\n")

# Test 1: Remove all 1s
expr1 = Mul(1, x, 1, y, 1, evaluate=False)
cleaned1 = cleanup_ast(expr1)
print(f"Test 1 - Remove 1s:")
print(f"  Input:  Mul(1, x, 1, y, 1)")
print(f"  Output: {cleaned1}\n")

# Test 2: Rational coefficient preservation
expr2 = Mul(Rational(-1, 2), pi, evaluate=False)
cleaned2 = cleanup_ast(expr2)
print(f"Test 2 - Rational coefficients:")
print(f"  Input:  Mul(Rational(-1,2), pi)")
print(f"  Output: {cleaned2}\n")

# Test 3: Pattern -1*pi*2^-1
expr3 = Mul(Rational(-1, 1), pi, Pow(2, -1, evaluate=False), evaluate=False)
cleaned3 = cleanup_ast(expr3)
print(f"Test 3 - Pattern -1*pi*2^-1:")
print(f"  Input:  Mul(-1, pi, Pow(2, -1))")
print(f"  Output: {cleaned3}\n")
