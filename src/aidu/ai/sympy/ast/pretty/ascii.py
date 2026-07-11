# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.

from rich import print
from rich.tree import Tree

# ============================================================
# PRETTY PRINT TREE
# ============================================================

def print_ast(expr):
    def rec(node, path=(), indent=""):
        print(f"{indent}{path} : {node} [{node.func.__name__}]")

        for i, arg in enumerate(node.args):
            rec(arg, path + (i,), indent + "    ")

    rec(expr)

