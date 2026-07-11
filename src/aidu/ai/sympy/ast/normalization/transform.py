# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
"""Minimal local rewrite helpers for SymPy school-math transformations."""


def cleanup(expr):
    if expr.args:
        expr = expr.func(*[cleanup(a) for a in expr.args], evaluate=False)

    if expr.is_Mul:
        numer, denom = [], []
        for a in expr.args:
            if a == 0:
                return Integer(0)
            if a == 1:
                continue
            if a.is_Pow and a.args[1].is_integer and a.args[1] < 0:
                base, exp = a.args[0], -a.args[1]
                denom.append(base if exp == 1 else Pow(base, exp, evaluate=False))
                continue
            numer.append(a)

        numer_expr = Integer(1) if not numer else numer[0] if len(numer) == 1 else Mul(*numer, evaluate=False)
        if not denom:
            return numer_expr
        denom_expr = denom[0] if len(denom) == 1 else Mul(*denom, evaluate=False)
        return Mul(numer_expr, Pow(denom_expr, Integer(-1), evaluate=False), evaluate=False)

    if expr.is_Add:
        args = [a for a in expr.args if a != 0]
        if not args:
            return Integer(0)
        return args[0] if len(args) == 1 else Add(*args, evaluate=False)

    if expr.is_Pow:
        base, exp = expr.args
        if exp == 1:
            return base
        if exp == 0:
            return Integer(1)

    return expr


def find_matches(expr, rules):
    matches = []
    for path, node in walk(expr):
        for rule in rules:
            if rule.match(node):
                matches.append((path, rule.name, node))
    return matches


def apply_rule(expr, path, rule):
    target = get_at(expr, path)
    if not rule.match(target):
        raise ValueError(f"Rule '{rule.name}' does not match node at {path}")
    return replace_at(expr, path, rule.apply)


if __name__ == "__main__":
    x = symbols("x")
    expr = parse_expr("sin(1/3*(x + 1))", evaluate=False)

    print("\n================================================")
    print("ORIGINAL EXPRESSION")
    print("================================================\n")
    print(expr)

    print("\n================================================")
    print("AST")
    print("================================================\n")
    rich_ast(expr, cursor=(0, 1))
    expr = cleanup(expr)
    rich_linear_ast(expr, cursor=(0, 1))

    sys.exit(0)

    distribute, factor = DistributeRule(), FactorRule()
    rules = [distribute, factor]

    print("\n================================================")
    print("MATCHES")
    print("================================================\n")
    for path, rule_name, node in find_matches(expr, rules):
        print(f"path={path}  rule={rule_name}  node={node}")

    print("\n================================================")
    print("APPLY DISTRIBUTE AT PATH (0,)")
    print("================================================\n")
    new_expr = apply_rule(expr, (0,), distribute)
    print(new_expr)

    print("\n================================================")
    print("NEW AST")
    print("================================================\n")
    rich_ast(new_expr)