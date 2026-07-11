# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
from sympy import *
from typing import Callable

from rich import print
from rich.text import Text


# ============================================================
# GET NODE AT PATH
# ============================================================

def get_at(expr, path):
    node = expr

    for i in path:
        node = node.args[i]

    return node


# ============================================================
# REPLACE SUBTREE AT PATH
# ============================================================

def replace_at(expr, path, fn):
    """
    Replace subtree at path using fn(node) -> new_node
    """

    if len(path) == 0:
        return fn(expr)

    args = list(expr.args)

    i = path[0]

    args[i] = replace_at(args[i], path[1:], fn)

    return expr.func(*args, evaluate=False)


