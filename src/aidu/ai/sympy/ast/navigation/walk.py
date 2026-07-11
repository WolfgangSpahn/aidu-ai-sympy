# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
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



