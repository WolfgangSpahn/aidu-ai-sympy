from sympy import parse_expr
from src.aidu.ai.sympy.ast.pretty.linear import matching_operations, replace_at, transform, RULES

# Test 1: x + x
expr1 = parse_expr('x + x', evaluate=False)
cursor1 = ()
ops1 = matching_operations(expr1)
print(f"Ops for 'x + x': {ops1}")

if 'combine_like_terms' in ops1:
    result1 = replace_at(expr1, cursor1, lambda n: transform(n, RULES['combine_like_terms']))
    print(f"Result for 'x + x': {result1}")
else:
    print("combine_like_terms not found for 'x + x'")

# Test 2: x*(y*z)
expr2 = parse_expr('x*(y*z)', evaluate=False)
cursor2 = ()
ops2 = matching_operations(expr2)
print(f"Ops for 'x*(y*z)': {ops2}")

if 'associate_mul_right' in ops2:
    result2 = replace_at(expr2, cursor2, lambda n: transform(n, RULES['associate_mul_right']))
    print(f"Result for 'x*(y*z)': {result2}")
else:
    print("associate_mul_right not found for 'x*(y*z)'")
