from sympy import parse_expr
from src.aidu.ai.sympy.ast.pretty.linear import matching_operations, replace_at, transform, RULES

node = parse_expr('x/3 + 1/3', evaluate=False)
ops = matching_operations(node)
op_names = [op['name'] for op in ops]
print(f"Available operations: {op_names}")

if 'factor_common_rational' in op_names:
    result = replace_at(node, (), lambda n: transform(n, RULES['factor_common_rational']))
    print(f"Result: {result}")
else:
    print("factor_common_rational not found")
