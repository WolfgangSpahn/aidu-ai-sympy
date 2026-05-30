import sys

from sympy import *
from typing import Callable

from rich import print
from rich.text import Text

# ============================================================
# AST WALKER
# ============================================================

def walk(expr, path=()):
    yield path, expr

    for i, arg in enumerate(expr.args):
        yield from walk(arg, path + (i,))



