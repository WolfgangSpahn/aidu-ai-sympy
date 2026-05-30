import logging
from rich.logging import RichHandler

import re
from sympy import symbols, solve, diff, latex, nsimplify
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

logger = logging.getLogger(__name__)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

SUPERSCRIPT_MAP = str.maketrans({
    '⁰': '0',
    '¹': '1',
    '²': '2',
    '³': '3',
    '⁴': '4',
    '⁵': '5',
    '⁶': '6',
    '⁷': '7',
    '⁸': '8',
    '⁹': '9',
    '⁺': '+',
    '⁻': '-',
})

DERIVATIVE_PREFIXES = (
    "derivate ",
    "derive ",
    "differentiate ",
    "derivative of ",
)


def _preprocess(expr_str: str) -> str:
    """Convert implicit math notation to Python-compatible syntax."""
    expr_str = expr_str.translate(SUPERSCRIPT_MAP)
    expr_str = expr_str.replace('^', '**')
    expr_str = expr_str.replace('×', '*')
    expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
    return expr_str


def _normalize_problem(problem: str) -> str:
    """Normalize casual math phrasing into the compact forms handled below."""
    normalized = problem.strip().translate(SUPERSCRIPT_MAP)
    lowered = normalized.lower()

    for prefix in DERIVATIVE_PREFIXES:
        if lowered.startswith(prefix):
            expression = normalized[len(prefix):].strip()
            return f"diff({expression}, x)"

    return normalized


def _parse_math(expr_str: str):
    """Parse a math expression and raise a user-facing error on failure."""
    prepared = _preprocess(expr_str)

    try:
        return parse_expr(prepared, transformations=TRANSFORMATIONS)
    except Exception as exc:
        raise ValueError(
            "I couldn't parse that math expression. Use forms like '4x^3', "
            "'diff(4x^3, x)', or '2x + 3 = 7'."
        ) from exc

def parse_math_problem(problem: str) -> dict:
    """
    Solves a mathematical problem using SymPy and formats with natural wording and LaTeX.
    
    Supports multiple syntaxes:
    - "diff(expr,x)" for derivatives (e.g., "diff(7x^2 + 3x - 5, x)")
    - "solve(expr,x)" to solve for x in an expression (e.g., "solve(2x + 3, x)")
    - "2x + 3 = 7" for equations
    
    Args:
        problem (str): The math problem string
        
    Returns:
        dict: Contains 'type', 'expression', 'result', 'latex', and 'message' keys
        
    Raises:
        ValueError: If the syntax is invalid
    """
    problem = _normalize_problem(problem)

    # Create symbolic variable 'x' - tells SymPy that 'x' is a mathematical variable
    x = symbols('x')  # Default variable
    
    # CASE 1: Derivative using diff(expr, variable)
    if problem.startswith('diff('):
        # Extract expression and variable using regex pattern: diff(..., ...)
        match = re.match(r'diff\((.+),\s*(\w+)\)', problem)
        if match:
            # Get expression string and variable name from the regex match
            expr_str, var_name = match.groups()
            # Create symbolic variable for differentiation
            var = symbols(var_name)
            # Parse string into SymPy expression (e.g., "7x^2" -> mathematical object)
            expr = _parse_math(expr_str)
            # 
            return 'diff', expr, var

        else:
            raise ValueError("Invalid diff syntax. Use: diff(expression, variable)")
    # CASE 2: Solve using solve(expr, variable) - finds where expr = 0
    elif problem.startswith('solve('):
        # Extract expression and variable using regex pattern
        match = re.match(r'solve\((.+),\s*(\w+)\)', problem)
        if match:
            # Get expression and variable from regex match
            expr_str, var_name = match.groups()
            # Create symbolic variable
            var = symbols(var_name)
            # Parse expression string into SymPy object
            expr = _parse_math(expr_str)
            # Keep coefficients exact so symbolic roots (e.g., sqrt(3)) are preserved.
            expr = nsimplify(expr, rational=True)
            # Solve: find all values of 'var' that make expr = 0
            return 'solve', expr, var

        else:
            raise ValueError("Invalid solve syntax. Use: solve(expression, variable)")
    # CASE 3: Equation solving (contains = sign, e.g., "2x + 3 = 7")
    elif '=' in problem:
        # Split at = sign to get left and right sides
        lhs, rhs = problem.split('=')
        # Rearrange to standard form: lhs - rhs = 0 for solving
        lhs_expr = _parse_math(lhs.strip())
        rhs_expr = _parse_math(rhs.strip())
        expr = lhs_expr - rhs_expr
        # Solve the rearranged equation
        return 'solve', expr, x

    # CASE 4: Expression formatting (no operation, just format the math)
    else:
        # in case no operation is detected, and we see the variable x, we interpret it as 'solve',expr,x
        expr = _parse_math(problem)
        if expr.has(x):
            logger.warning("No operation detected, but variable 'x' found. Treating as solve(expr, x).")
            return 'solve', expr, x
        else:
            logger.warning("No operation detected, treating as expression formatting.")

def smoke_test():
    """Run a quick test of the parsing logic."""
    test_cases = [
        "diff(7x^2 + 3x - 5, x)",
        "solve((2x + 3)*3, x)",
        "2x + 3 = 7",
        "4x^3 + 2x - 1"
    ]
    
    for problem in test_cases:
        try:
            result = parse_math_problem(problem)
            print(f"Problem: {problem}\nParsed Result: {result}\n")
        except ValueError as e:
            print(f"Problem: {problem}\nError: {e}\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        handlers=[RichHandler()]    )
    smoke_test()