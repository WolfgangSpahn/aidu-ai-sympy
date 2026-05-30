import sympy
from src.aidu.ai.sympy.ast.operations.transform import parse_expr, structural_match

test_expressions = [
    'N * X',
    '(A * B) ** N',
    'not(not(p))',
    '(x*y)/(x*z)',
    'eval(A + B)',
    'repeat(X,N,"+")',
    'A = B | + C'
]

print("--- Testing parse_expr ---")
for expr_str in test_expressions:
    try:
        parsed = parse_expr(expr_str)
        print(f"Input: {expr_str}")
        print(f"Repr:  {repr(parsed)}")
    except Exception as e:
        print(f"Input: {expr_str}")
        print(f"Error: {type(e).__name__}: {e}")
    print("-" * 20)

print("\n--- Testing structural_match ---")
try:
    expr = parse_expr('(x*y)/(x*z)', evaluate=False)
    pattern = parse_expr('(A*B)/(A*C)', evaluate=False)
    # Assuming structural_match(expr, pattern) exists or similar signature
    match = structural_match(expr, pattern)
    print(f"Expr: {repr(expr)}")
    print(f"Pattern: {repr(pattern)}")
    print(f"Match result: {match}")
except Exception as e:
    print(f"Structural Match Error: {type(e).__name__}: {e}")

