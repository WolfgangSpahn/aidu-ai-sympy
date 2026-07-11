# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
import logging


from rich.console import Console
from rich.logging import RichHandler
from rich.tree import Tree

from ..navigation.cursor import resolve_cursor_path


logger = logging.getLogger(__name__)

# ============================================================
# RICH AST TREE
# ============================================================

def rich_ast(console, expr, cursor=None):
    """
    Render SymPy AST using rich.Tree

    Parameters
    ----------
    expr:
        SymPy expression

    cursor:
        tuple path to highlight

        Example:
            cursor=(0,1)

    Example output:

    Mul ()
    ├── Integer (0,0)
    │   └── 3
    └── Add (0,1)   <-- highlighted
        ├── Symbol (0,1,0)
        │   └── x
        └── One (0,1,1)
            └── 1
    """
    logger.debug(f"Rendering AST with cursor={cursor}:\n{expr}")

    # --------------------------------------------------------
    # node label
    # --------------------------------------------------------

    def label(node, path):

        if len(node.args) == 0:
            leaf = f"{node.func.__name__}({node})"

            if cursor == path:
                return (
                    f"[black on bright_yellow]"
                    f"{leaf} {path}"
                    f"[/black on bright_yellow]"
                )

            return (
                f"[bold cyan]"
                f"{leaf}"
                f"[/bold cyan] "
                f"[yellow]{path}[/yellow]"
            )

        # highlighted cursor node
        if cursor == path:

            return (
                f"[black on bright_yellow]"
                f"{node.func.__name__} {path}"
                f"[/black on bright_yellow]"
            )

        # ancestor path highlighting
        elif cursor is not None and path == cursor[:len(path)]:

            return (
                f"[bold bright_cyan]"
                f"{node.func.__name__} {path}"
                f"[/bold bright_cyan]"
            )

        # normal node
        return (
            f"[bold cyan]"
            f"{node.func.__name__}"
            f"[/bold cyan] "
            f"[yellow]{path}[/yellow]"
        )

    # --------------------------------------------------------
    # recursion
    # --------------------------------------------------------

    def rec(node, path=()):

        tree = Tree(label(node, path))

        if len(node.args) == 0:
            return tree

        # recurse children
        for i, arg in enumerate(node.args):

            subtree = rec(arg, path + (i,))

            tree.add(subtree)

        return tree
    
    # check cursor validity
    if cursor is not None:
        try:
            resolve_cursor_path(expr, cursor)
        except (IndexError, TypeError):
            logger.warning(
                "Cursor path %s is not present in expression tree; rendering without cursor highlight",
                cursor,
            )
            cursor = None

    console.print(rec(expr))


def smoke_test(console):
    from sympy import symbols

    x, y = symbols("x y")

    expr = 3 * (x + 1)

    rich_ast(console, expr, cursor=(0,))


if __name__ == "__main__":
    # setup rich handler for logging
    console = Console()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        handlers=[RichHandler(console=console)]
    )

    logger.info("Starting rich AST tree demo...")

    console = Console()

    smoke_test(console)