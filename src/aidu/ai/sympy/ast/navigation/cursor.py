# Copyright (C) 2026 Dr. Wolfgang Spahn, PHBern
#
# MIT License — see LICENSE file for details.
# If you use this software in academic work, citation of the original author is requested.
from ..transforms.transform import get_at, replace_at
from .walk import walk


def resolve_cursor_path(expr, path):
    return get_at(expr, path), False

def cursor_up(path):

    if len(path) == 0:
        return path

    return path[:-1]

def cursor_down(expr, path):

    node = get_at(expr, path)

    if not node.args:
        return path

    return path + (0,)

def cursor_left(expr, path):

    if len(path) == 0:
        return path

    parent = path[:-1]
    idx = path[-1]

    if idx == 0:
        return path

    return parent + (idx - 1,)

def cursor_right(expr, path):

    if len(path) == 0:
        return path

    parent = get_at(expr, path[:-1])

    idx = path[-1]

    if idx + 1 >= len(parent.args):
        return path

    return path[:-1] + (idx + 1,)


def linear_paths(expr):
    return [path for path, _ in walk(expr)]


def cursor_next(expr, cursor):

    paths = linear_paths(expr)

    try:
        idx = paths.index(cursor)
    except ValueError:
        return cursor

    if idx + 1 >= len(paths):
        return cursor

    return paths[idx + 1]

def cursor_prev(expr, cursor):

    paths = linear_paths(expr)

    try:
        idx = paths.index(cursor)
    except ValueError:
        return cursor

    if idx == 0:
        return cursor

    return paths[idx - 1]