from sympy import symbols, sin, Rational
from src.aidu.ai.sympy.ast.pretty.linear import rich_linear_ast, available_operations
from src.aidu.ai.sympy.ast.navigation.cursor import resolve_cursor_path
from src.aidu.ai.sympy.ast.transforms.transform import replace_at
from rich.console import Console

console = Console()

x, y = symbols('x y')
# Using Rational(1, 3) to avoid float conversion issues in some environments
expr = y**2 + sin(Rational(1,3)*x + Rational(1,3))
console.print("Original expression:")
rich_linear_ast(expr)

cursor = (1, 0)  # cursor on sin(...) argument
node = resolve_cursor_path(expr, cursor)[0]
console.print(f"\nNode at cursor (1,0): {node}")

# Let's inspect what available_operations returns exactly
ops = available_operations(node)
console.print(f"Available operations (raw): {ops}")

# Apply factoring
# Looking for 'factor_common_rational_sympy' or others
op_name = 'factor_common_rational_sympy'
op = next((o for o in ops if o['name'] == op_name), None)

if not op:
    # try the other rational factoring rules
    op = next((o for o in ops if o['name'] in ['factor_common_rational', 'factor_common_rational_rev']), None)
    if op:
        op_name = op['name']

if op:
    console.print(f"Applying operation: {op_name}")
    updated = replace_at(expr, cursor, op['apply'])
    console.print("\nAfter factoring:")
    rich_linear_ast(updated)
else:
    console.print("Operation not found in available operations.")
