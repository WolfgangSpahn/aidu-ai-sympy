# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
import logging
import readchar

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .tree import rich_ast
from ..navigation.cursor import cursor_down, cursor_next, cursor_prev, cursor_up, resolve_cursor_path
from ..operations.db import RULES
from ..operations.transform import parse_typed_pattern, structural_match, transform
from ..transforms.transform import replace_at


logger = logging.getLogger(__name__)
console = Console(force_terminal=True)


def cleanup_ast(expr):
    """Conservative display cleanup that avoids changing math semantics."""
    from sympy import Add, Basic, Mul, Pow

    if not isinstance(expr, Basic):
        return expr

    cleaned_args = [cleanup_ast(arg) for arg in expr.args]

    if expr.is_Pow:
        base, exp = cleaned_args
        if exp == 0:
            return 1
        if exp == 1:
            return base
        return Pow(base, exp, evaluate=False)

    if expr.is_Mul:
        filtered = [arg for arg in cleaned_args if arg != 1]
        if not filtered:
            return 1
        if len(filtered) == 1:
            return filtered[0]
        return Mul(*filtered, evaluate=False)

    if expr.is_Add:
        if len(cleaned_args) == 1:
            return cleaned_args[0]
        return Add(*cleaned_args, evaluate=False)

    if cleaned_args:
        return expr.func(*cleaned_args, evaluate=False)

    return expr


def available_operations(node):
    ops = []
    for name, rule in RULES.items():
        if "->" not in rule:
            continue
        lhs_source = rule.split("->", 1)[0].strip()

        # Equation/context rules need full equations, not a subtree node.
        if "=" in lhs_source or "|" in lhs_source:
            continue

        try:
            typed = parse_typed_pattern(lhs_source)
            if structural_match(typed.ast, node, typed.metavars) is not None:
                ops.append(
                    {
                        "name": name,
                        "rule": rule,
                        "apply": (lambda n, rule=rule: transform(n, rule)),
                    }
                )
        except Exception:
            continue

    return ops


def matching_operations(node):
    """Return operation names whose LHS structurally matches node."""
    return [op["name"] for op in available_operations(node)]


def render_operations(console_obj, ops):
    if not ops:
        console_obj.print("possible operations: none", style="dim", justify="center")
        return

    table = Table(title="Possible Operations", show_header=True, header_style="bold cyan")
    table.add_column("Key", style="bold yellow", width=4)
    table.add_column("Operation", style="bold green")
    table.add_column("Rule", style="white")

    for idx, op in enumerate(ops, start=1):
        key_label = str(idx) if idx <= 9 else "-"
        table.add_row(key_label, op["name"], op["rule"])

    console_obj.print(table, justify="center")
    console_obj.print("Press 1-9 to apply an operation to the current cursor node.", style="dim", justify="center")


def rich_linear_ast(expr, cursor=None):
    """Linear pretty renderer with cursor-path highlighting."""
    expr = cleanup_ast(expr)
    logger.debug("Rendering linear AST with cursor=%s:\n%s", cursor, expr)

    if cursor is not None:
        try:
            resolve_cursor_path(expr, cursor)
        except (IndexError, TypeError):
            logger.warning("Cursor path %s is not present in expression tree; rendering without highlight", cursor)
            cursor = None

    def style_for(path):
        if cursor == path:
            return "black on white"
        if cursor is not None and path == cursor[: len(path)]:
            return "bold bright_green"
        return None

    def rec(node, path=()):
        style = style_for(path)

        if not node.args:
            out = Text(str(node))
            if style:
                out.stylize(style)
            return out

        if node.is_Add:
            out = Text()
            for i, arg in enumerate(node.args):
                if i > 0:
                    out.append(" + ")
                out.append_text(rec(arg, path + (i,)))

            if len(node.args) > 1 and path != ():
                out = Text("(") + out + Text(")")

            if style:
                out.stylize(style)
            return out

        if node.is_Mul:
            out = Text()
            for i, arg in enumerate(node.args):
                if i > 0:
                    out.append("*")
                out.append_text(rec(arg, path + (i,)))

            if style:
                out.stylize(style)
            return out

        if node.is_Pow:
            base = rec(node.args[0], path + (0,))
            exp = rec(node.args[1], path + (1,))
            out = base + Text("^") + exp
            if style:
                out.stylize(style)
            return out

        out = Text(f"{node.func.__name__}(")
        for i, arg in enumerate(node.args):
            if i > 0:
                out.append(", ")
            out.append_text(rec(arg, path + (i,)))
        out.append(")")

        if style:
            out.stylize(style)
        return out

    panel = Panel(
        rec(expr),
        box=ROUNDED,
        padding=(1, 2),
        title="Expression",
        border_style="bold cyan",
        expand=False,
    )
    console.print(panel, justify="center")


def smoke_test():
    from sympy import sin, symbols

    x, y = symbols("x y")
    expr = sin((x + 1) / 3) + y**2
    rich_linear_ast(expr, cursor=(0, 0))


def cursor_test(console_obj):
    from sympy import sin, symbols

    x, y = symbols("x y")
    expr = sin((x + 1) / 3) + y**2

    cursor = ()
    status = ""

    while True:
        console_obj.clear()

        rich_ast(console_obj, expr, cursor=cursor)
        rich_linear_ast(expr, cursor=cursor)

        console_obj.print()
        console_obj.print("cursor =", cursor)

        node = resolve_cursor_path(expr, cursor)[0]
        console_obj.print("subtree at cursor:", node)

        ops = available_operations(node)
        render_operations(console_obj, ops)

        if status:
            console_obj.print(status)
            status = ""

        key = readchar.readkey()

        if key == "q":
            break

        if key.isdigit() and key != "0":
            idx = int(key) - 1
            if idx < len(ops):
                op = ops[idx]
                try:
                    expr = replace_at(expr, cursor, op["apply"])
                    status = f"[green]Applied:[/green] {idx + 1}: {op['name']}"
                    try:
                        resolve_cursor_path(expr, cursor)
                    except Exception:
                        cursor = ()
                except Exception as exc:
                    status = f"[red]Failed:[/red] {op['name']} ({exc})"
            else:
                status = f"[yellow]No operation bound to key {key}[/yellow]"
            continue

        if key == "\x1b[A":
            cursor = cursor_up(expr, cursor)
        elif key == "\x1b[B":
            cursor = cursor_down(expr, cursor)
        elif key == "\x1b[C":
            cursor = cursor_next(expr, cursor)
        elif key == "\x1b[D":
            cursor = cursor_prev(expr, cursor)


if __name__ == "__main__":
    cursor_test(console)