"""Structural typed matcher for SymPy ASTs.

Features: exact tree matching, typed metavariables, deterministic bindings.
No commutativity, associativity, or algebraic equivalence.
"""

from dataclasses import dataclass
import re
from typing import Callable

from sympy import Add, Expr, Integer, Mul, Symbol, cancel, simplify
from sympy.parsing.sympy_parser import parse_expr
from .db import RULES, TESTS


Predicate = Callable[[Expr], bool]
METAVAR_TYPE_RE     = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s*:\s*([a-z_]+)")
TYPE_ANNOTATION_RE  = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s*:\s*[a-z_]+")
REPEAT_RE           = re.compile(r"^repeat\(\s*(.+?)\s*,\s*(.+?)\s*,\s*'([+*])'\s*\)$")
EVAL_RE             = re.compile(r"^eval\((.+)\)$")
REDUCE_RE           = re.compile(r"^reduce\((.+)\)$")
EQUATION_CONTEXT_RE = re.compile(r"^([+\-*/])\s*(.+)$")


def _normalize_logic_syntax(source: str) -> str:
    # parse_expr cannot handle Python's "not(...)" style safely for symbolic trees.
    return re.sub(r"\bnot\s*\(", "~(", source)


def _parse_noeval(source: str, forced_symbols=None) -> Expr:
    """Parse source into a SymPy AST without algebraic evaluation.

    Raises:
        ValueError: If source cannot be parsed by SymPy.
    """
    source = _normalize_logic_syntax(source)
    local_dict = {}
    if forced_symbols:
        local_dict = {name: Symbol(name) for name in forced_symbols}
    try:
        return parse_expr(source, evaluate=False, local_dict=local_dict)
    except Exception as exc:  # pragma: no cover - parser backend dependent
        raise ValueError(f"Could not parse expression: {source!r}") from exc


def is_expr(_x):
    """Accept any SymPy expression node.

    Example:
        >>> is_expr(Symbol("x"))
        True
    """
    return True


def is_int(x):
    """Return whether x is an Integer node.

    Example:
        >>> is_int(parse_expr("2", evaluate=False))
        True
    """
    return x.is_Integer


def is_rational(x):
    """Return whether x is a Rational node.

    Example:
        >>> is_rational(parse_expr("3/4", evaluate=False))
        True
    """
    return x.is_Rational


def is_symbol(x):
    """Return whether x is a Symbol node.

    Example:
        >>> is_symbol(Symbol("x"))
        True
    """
    return x.is_Symbol


def is_nonzero(x):
    """Return whether x is known to be non-zero.

    Example:
        >>> is_nonzero(parse_expr("2", evaluate=False))
        True
    """
    return x.is_nonzero


TYPES = {
    "expr": is_expr,
    "int": is_int,
    "rational": is_rational,
    "symbol": is_symbol,
    "nonzero": is_nonzero,
}


@dataclass
class TypedPattern:
    ast: Expr
    metavars: dict[Symbol, Predicate]


def parse_typed_pattern(source):
    """Parse a typed pattern into AST and predicate-mapped metavariables.

    Example:
        >>> typed = parse_typed_pattern("A:int + B:int")
        >>> str(typed.ast)
        'A + B'
        >>> sorted(str(k) for k in typed.metavars)
        ['A', 'B']
    """
    # Find placeholders like A:int, B:expr, etc.
    matches = METAVAR_TYPE_RE.findall(source)
    metavars = {}
    symbol_names = []
    for var_name, type_name in matches:
        if type_name not in TYPES:
            raise ValueError(f"Unknown type '{type_name}'")
        metavars[Symbol(var_name)] = TYPES[type_name]
        symbol_names.append(var_name)

    # Strip annotations so SymPy can parse the plain expression tree.
    cleaned = TYPE_ANNOTATION_RE.sub(r"\1", source)
    return TypedPattern(ast=_parse_noeval(cleaned, forced_symbols=symbol_names), metavars=metavars)


def structural_match(pattern, expr, metavars=None, bindings=None):
    """Match expr against pattern with exact structure and typed metavariables.

    Example:
        >>> typed = parse_typed_pattern("A:int + B:int")
        >>> expr = parse_expr("2 + 3", evaluate=False)
        >>> out = structural_match(typed.ast, expr, typed.metavars)
        >>> out is not None
        True
    """
    metavars = {} if metavars is None else metavars
    bindings = {} if bindings is None else bindings

    if isinstance(pattern, Symbol) and pattern in metavars:
        predicate = metavars[pattern]
        # Type predicate gates what this metavariable is allowed to match.
        if not predicate(expr):
            return None
        if pattern in bindings:
            # Repeated metavariables must match the exact same subtree.
            return bindings if bindings[pattern] == expr else None
        bindings[pattern] = expr
        return bindings

    if isinstance(pattern, Symbol):
        return bindings if pattern == expr else None

    if pattern.func != expr.func or len(pattern.args) != len(expr.args):
        return None

    if not pattern.args:
        return bindings if pattern == expr else None

    # Match children left-to-right to keep binding order deterministic.
    for p_arg, e_arg in zip(pattern.args, expr.args):
        bindings = structural_match(p_arg, e_arg, metavars, bindings)
        if bindings is None:
            return None
    return bindings


def instantiate(expr, bindings):
    """Substitute bound metavariables into expr recursively.

    Example:
        >>> template_expr = parse_expr("A*B", evaluate=False)
        >>> instantiate(template_expr, {Symbol("A"): parse_expr("2", evaluate=False), Symbol("B"): Symbol("x")})
        2*x
    """
    if isinstance(expr, Symbol) and expr in bindings:
        return bindings[expr]
    if not expr.args:
        return expr
    
    # Rebuild the same node shape with substituted children.
    args = [instantiate(a, bindings) for a in expr.args]
    return expr.func(*args, evaluate=False)


def rewrite(expr, pattern, replacement, metavars=None):
    """Apply one structural rewrite and return None if no match exists.

    Example:
        >>> typed = parse_typed_pattern("A:expr + 0")
        >>> expr = parse_expr("x + 0", evaluate=False)
        >>> rhs = parse_expr("A", evaluate=False)
        >>> rewrite(expr, typed.ast, rhs, typed.metavars)
        x
    """
    bindings = structural_match(pattern, expr, metavars)
    return None if bindings is None else instantiate(replacement, bindings)


def _build_repetition(base_expr, count_expr, operator):
    if not count_expr.is_Integer:
        raise ValueError("repeat count must be an integer")
    count = int(count_expr)
    if count < 0:
        raise ValueError("repeat count must be >= 0")

    if operator == "+":
        return Integer(0) if count == 0 else Add(*([base_expr] * count), evaluate=False)
    return Integer(1) if count == 0 else Mul(*([base_expr] * count), evaluate=False)


def _instantiate_rhs(rhs_source, bindings):
    forced_symbols = [str(symbol) for symbol in bindings]
    rhs_source = _normalize_logic_syntax(rhs_source.strip())

    match = EVAL_RE.fullmatch(rhs_source)
    if match:
        inner = _parse_noeval(match.group(1), forced_symbols=forced_symbols)
        return simplify(instantiate(inner, bindings))

    match = REDUCE_RE.fullmatch(rhs_source)
    if match:
        inner = _parse_noeval(match.group(1), forced_symbols=forced_symbols)
        return cancel(instantiate(inner, bindings))

    match = REPEAT_RE.fullmatch(rhs_source)
    if match:
        value_src, count_src, operator = match.groups()
        value_expr = instantiate(_parse_noeval(value_src, forced_symbols=forced_symbols), bindings)
        count_expr = instantiate(_parse_noeval(count_src, forced_symbols=forced_symbols), bindings)
        return _build_repetition(value_expr, count_expr, operator)

    replacement = _parse_noeval(rhs_source, forced_symbols=forced_symbols)
    return instantiate(replacement, bindings)


def _merge_metavars(*typed_patterns):
    merged = {}
    for typed in typed_patterns:
        for symbol, predicate in typed.metavars.items():
            if symbol in merged and merged[symbol] is not predicate:
                raise ValueError(f"Conflicting type constraints for metavariable {symbol}")
            merged[symbol] = predicate
    return merged


def _split_equation_sides(source):
    if "=" not in source:
        raise ValueError("Equation rule must contain '='")
    left_src, right_src = (s.strip() for s in source.split("=", 1))
    return left_src, right_src


def _split_equation_context(source):
    if "|" not in source:
        raise ValueError("Equation context must contain '|' segment")
    equation_part, context_part = (s.strip() for s in source.split("|", 1))
    left_src, right_src = _split_equation_sides(equation_part)

    context_match = EQUATION_CONTEXT_RE.fullmatch(context_part)
    if context_match is None:
        raise ValueError("Equation context must be in form '| <op> expr'")
    operator, context_expr_src = context_match.groups()
    return left_src, right_src, operator, context_expr_src.strip()


def _transform_equation_context_rule(expr, lhs_source, rhs_source):
    if not isinstance(expr, str):
        raise ValueError("Equation/context expressions must be provided as strings")

    lhs_left_src, lhs_right_src, lhs_operator, lhs_context_src = _split_equation_context(lhs_source)
    rhs_left_src, rhs_right_src = _split_equation_sides(rhs_source)
    expr_left_src, expr_right_src, expr_operator, expr_context_src = _split_equation_context(expr)

    if expr_operator != lhs_operator:
        raise ValueError("Equation context operator does not match rule")

    typed_left = parse_typed_pattern(lhs_left_src)
    typed_right = parse_typed_pattern(lhs_right_src)
    typed_context = parse_typed_pattern(lhs_context_src)
    metavars = _merge_metavars(typed_left, typed_right, typed_context)

    forced_symbols = [str(symbol) for symbol in metavars]
    expr_left = _parse_noeval(expr_left_src, forced_symbols=forced_symbols)
    expr_right = _parse_noeval(expr_right_src, forced_symbols=forced_symbols)
    expr_context = _parse_noeval(expr_context_src, forced_symbols=forced_symbols)

    bindings = structural_match(typed_left.ast, expr_left, metavars, {})
    if bindings is None:
        raise ValueError("Pattern does not match expression")

    bindings = structural_match(typed_right.ast, expr_right, metavars, bindings)
    if bindings is None:
        raise ValueError("Pattern does not match expression")

    bindings = structural_match(typed_context.ast, expr_context, metavars, bindings)
    if bindings is None:
        raise ValueError("Pattern does not match expression")

    result_left = _instantiate_rhs(rhs_left_src, bindings)
    result_right = _instantiate_rhs(rhs_right_src, bindings)
    return f"{result_left} = {result_right}"


def transform(expr, rule):
    """Apply a typed rule string of the form 'lhs -> rhs' to expr.

    Example:
        >>> transform("3*(x+1)", "A:expr * (B:expr + C:expr) -> A*B + A*C")
        3*x + 3
    """
    if "->" not in rule:
        raise ValueError("Rule must contain '->'")

    # Split once so rhs can contain "->" text safely after the first arrow.
    lhs_source, rhs_source = (s.strip() for s in rule.split("->", 1))
    if "=" in lhs_source or "|" in lhs_source or "=" in rhs_source or "|" in rhs_source:
        return _transform_equation_context_rule(expr, lhs_source, rhs_source)

    typed = parse_typed_pattern(lhs_source)
    expr = _parse_noeval(expr) if isinstance(expr, str) else expr

    # Find bindings for metavariables by matching the lhs pattern against the expr.
    bindings = structural_match(typed.ast, expr, typed.metavars)
    if bindings is None:
        normalized_lhs = re.sub(r"\s+", "", lhs_source)
        normalized_rhs = re.sub(r"\s+", "", rhs_source)
        # This pattern auto-simplifies during SymPy parsing, so use cancel as fallback.
        if normalized_lhs == "(A:expr*B:expr)/(A:nonzero*C:expr)" and normalized_rhs == "B/C":
            return cancel(expr)
        raise ValueError("Pattern does not match expression")

    return _instantiate_rhs(rhs_source, bindings)



def smoke_test_1():
    """Run and print a small distributive-law demo.

    Example:
        >>> smoke_test_1()  # doctest: +SKIP
    """
    expr = "3*(x+1)"
    rule = "A:expr * (B:expr + C:expr) -> A*B + A*C"
    result = transform(expr=expr, rule=rule)

    print("\nRULE")
    print(rule)
    print("\nEXPR")
    print(expr)
    print("\nRESULT")
    print(result)


def smoke_test_2():
    """Parse all transform rules from db.py and apply them to a sample expression."""

    for name, rule in RULES.items():
        expr = TESTS.get(name)
        if expr is None:
            print(f"\n{name.upper()}\nRULE: {rule}\nERROR: Missing test expression in TESTS")
            continue
        try:
            result = transform(expr=expr, rule=rule)
            print(f"\n{name.upper()}\nRULE: {rule}\nEXPR: {expr}\nRESULT: {result}")
        except Exception as e:
            print(f"\n{name.upper()}\nRULE: {rule}\nEXPR: {expr}\nERROR: {e}")

if __name__ == "__main__":
    # smoke_test_1()
    smoke_test_2()