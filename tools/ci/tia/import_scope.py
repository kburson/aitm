"""Recognize the small set of dynamic imports the advisory graph can bound."""

import ast

_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_SCOPES = (
    *_FUNCTIONS,
    ast.Lambda,
    ast.ClassDef,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)


def _binds(node, name):
    if isinstance(node, ast.Name):
        return node.id == name and isinstance(node.ctx, (ast.Store, ast.Del))
    if isinstance(node, ast.alias):
        return (node.asname or node.name.partition(".")[0]) == name
    if isinstance(node, (ast.Global, ast.Nonlocal)):
        return name in node.names
    if isinstance(node, ast.arg):
        return node.arg == name
    if isinstance(node, ast.MatchMapping):
        return node.rest == name
    return (
        isinstance(
            node,
            (*_FUNCTIONS, ast.ClassDef, ast.ExceptHandler, ast.MatchAs, ast.MatchStar),
        )
        and node.name == name
    )


def _context(node, parents, tree):
    """Return the enclosing execution scope and its direct body statement."""
    statement = node
    while statement in parents:
        parent = parents[statement]
        if parent is tree or isinstance(parent, _SCOPES):
            if statement in getattr(parent, "body", ()):
                return parent, statement
            return None, None
        statement = parent
    return None, None


def _before(scope, statement):
    if scope is None:
        return ()
    return scope.body[: scope.body.index(statement)]


def _absolute_module(value):
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        if all(part.isidentifier() for part in value.value.split(".")):
            return value.value
    return None


def _module_argument(arg, scope, statement):
    direct = _absolute_module(arg)
    if direct or not isinstance(arg, ast.Name) or not isinstance(scope, _FUNCTIONS):
        return direct
    bindings = [node for node in ast.walk(scope) if _binds(node, arg.id)]
    if len(bindings) != 1:
        return None
    for assignment in _before(scope, statement):
        if isinstance(assignment, ast.Assign) and assignment.targets == bindings:
            return _absolute_module(assignment.value)
    return None


def _registered_loader(scope, statement, tree, parents, nodes, name, module, member):
    bindings = [node for node in nodes if _binds(node, name)]
    if len(bindings) != 1:
        return False
    alias = bindings[0]
    if not isinstance(alias, ast.alias) or alias.asname is not None:
        return False
    declaration = parents[alias]
    if member is None:
        if not isinstance(declaration, ast.Import) or alias.name != module:
            return False
    elif not isinstance(declaration, ast.ImportFrom) or (
        declaration.level or declaration.module != module or alias.name != member
    ):
        return False
    if declaration in _before(scope, statement):
        return True
    if isinstance(scope, _FUNCTIONS) and scope in tree.body:
        return declaration in _before(tree, scope)
    return False


def dynamic_modules(tree):
    """Return possible absolute names, or None for an unproven reader."""
    nodes = tuple(ast.walk(tree))
    parents = {child: node for node in nodes for child in ast.iter_child_nodes(node)}
    names = set()
    for node in nodes:
        if isinstance(node, ast.alias):
            if node.name in {"importlib", "import_module", "find_spec"} and node.asname:
                return None
            if (
                node.name == "__import__"
                or node.name == "*"
                and isinstance(parents[node], ast.ImportFrom)
                and parents[node].module in {"importlib", "builtins"}
            ):
                return None
        if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load):
            continue
        loader = parents[node]
        match node.id:
            case "__import__":
                return None
            case "import_module":
                module, member = "importlib", "import_module"
                loader = node
            case "find_spec":
                # Unrelated hooks with this name cannot prove an import target.
                module, member = "importlib.util", "find_spec"
                loader = node
            case "importlib":
                module, member = "importlib", None
                if isinstance(loader, ast.Attribute) and loader.attr == "util":
                    loader = parents[loader]
                    if (
                        not isinstance(loader, ast.Attribute)
                        or loader.attr != "find_spec"
                    ):
                        return None
                elif (
                    not isinstance(loader, ast.Attribute)
                    or loader.attr != "import_module"
                ):
                    return None
            case _:
                continue
        call = parents[loader]
        if (
            not isinstance(call, ast.Call)
            or call.func != loader
            or len(call.args) != 1
            or call.keywords
        ):
            return None
        scope, statement = _context(call, parents, tree)
        if not _registered_loader(
            scope, statement, tree, parents, nodes, node.id, module, member
        ):
            return None
        name = _module_argument(call.args[0], scope, statement)
        if name is None:
            return None
        names.add(name)
    return tuple(sorted(names)) if names else None
