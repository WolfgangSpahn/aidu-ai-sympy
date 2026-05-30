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
        # Pass a custom local dict to avoid name conflicts with built-ins if necessary
        # but the query asks how the current parse_expr behaves.
        parsed = parse_expr(expr_str)
        print(f"Input: {expr_str}")
        print(f"Repr:  {repr(parsed)}")
    except Exception as e:
        print(f"Input: {expr_str}")
        print(f"Error: {type(e).__name__}: {e}")
    print("-" * 20)

print("\n--- Testing structural_match ---")
try:
    # Use evaluate=False as requested for the structural match part
    expr = parse_expr('(x*y)/(x*z)', evaluate=False)
    pattern = parse_expr('(A*B)/(A*C)', evaluate=False)
    match = structural_match(expr, pattern)
    print(f"Expr: {repr(expr)}")
    print(f"Pattern: {repr(pattern)}")
    print(f"Match result: {match}")
except Exception as e:
    print(f"Structural Match Error: {type(e).__name__}: {e}")
