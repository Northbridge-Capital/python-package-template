"""Docstrings follow the convention in CONTRIBUTING.md (NumPy style, no types).

`ruff` checks the section formatting; this checks what it cannot: that every definition has a
docstring, that private ones are one-liners, and that the sections of public ones list exactly
the parameters, attributes and methods that exist.
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

import pytest

import package_name as package

SOURCE = Path(package.__file__).parent
PUBLIC = set(package.__all__) - {"__version__"}
FUNCTION_SECTIONS = ["Parameters", "Returns", "Yields", "Raises"]
CLASS_SECTIONS = ["Attributes", "Methods"]

Definition = ast.FunctionDef | ast.ClassDef


def package_errors() -> set[str]:
    """The exception classes the package defines in its ``errors`` module."""
    path = SOURCE / "errors.py"
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text())
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def is_exception(name: str) -> bool:
    """Whether a ``Raises`` entry names a package error or a built-in exception."""
    builtin = getattr(builtins, name, None)
    return name in package_errors() or (
        isinstance(builtin, type) and issubclass(builtin, BaseException)
    )


def sections(docstring: str) -> dict[str, list[str]]:
    """Map each section title to its unindented lines (entry names, or prose for Returns)."""
    lines = docstring.splitlines()
    found: dict[str, list[str]] = {}
    current: str | None = None
    for index, line in enumerate(lines):
        underline = lines[index + 1] if index + 1 < len(lines) else ""
        if line and underline and set(underline) == {"-"} and len(underline) == len(line):
            current = line
            found[current] = []
        elif current and line and not line.startswith(" ") and set(line) != {"-"}:
            found[current].append(line)
    return found


def parameters(function: ast.FunctionDef) -> list[str]:
    """The parameter names of a function, without ``self`` and ``cls``."""
    args = function.args
    names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
    names += [a.arg for a in (args.vararg, args.kwarg) if a is not None]
    return [name for name in names if name not in {"self", "cls"}]


def is_generator(function: ast.FunctionDef) -> bool:
    """Whether the function body yields (not counting nested functions)."""
    stack: list[ast.AST] = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, ast.Yield | ast.YieldFrom):
            return True
        if not isinstance(node, ast.FunctionDef | ast.Lambda | ast.ClassDef):
            stack.extend(ast.iter_child_nodes(node))
    return False


def returns_a_value(function: ast.FunctionDef) -> bool:
    """Whether the return annotation is something other than ``None``."""
    annotation = function.returns
    return not (isinstance(annotation, ast.Constant) and annotation.value is None)


def is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def is_property(function: ast.FunctionDef) -> bool:
    return any(isinstance(d, ast.Name) and d.id == "property" for d in function.decorator_list)


def collect() -> list[tuple[str, Definition, bool]]:
    """Every module-level function and class, and the methods of classes: (id, node, public)."""
    found: list[tuple[str, Definition, bool]] = []
    for path in sorted(SOURCE.glob("*.py")):
        for node in ast.parse(path.read_text()).body:
            if not isinstance(node, Definition):
                continue
            public = node.name in PUBLIC
            found.append((f"{path.name}::{node.name}", node, public))
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, ast.FunctionDef) and not is_dunder(member.name):
                        member_public = public and not member.name.startswith("_")
                        found.append(
                            (f"{path.name}::{node.name}.{member.name}", member, member_public)
                        )
    return found


def check_private(docstring: str | None) -> list[str]:
    if docstring is None:
        return ["has no docstring"]
    problems = []
    if len(docstring.splitlines()) != 1:
        problems.append("private names get a one-line docstring")
    if not docstring.endswith("."):
        problems.append("the summary must end with a period")
    return problems


def check_property(docstring: str | None) -> list[str]:
    """A property is documented as an attribute: a one-line noun phrase, no sections."""
    if docstring is None:
        return ["has no docstring"]
    if len(docstring.splitlines()) != 1 or not docstring.endswith("."):
        return ["a property gets a one-line docstring ending with a period"]
    return []


def check_function(node: ast.FunctionDef, docstring: str) -> list[str]:
    found = sections(docstring)
    problems = [f"unknown section {name!r}" for name in found if name not in FUNCTION_SECTIONS]
    order = [name for name in found if name in FUNCTION_SECTIONS]
    if order != [name for name in FUNCTION_SECTIONS if name in found]:
        problems.append(f"sections must be in the order {FUNCTION_SECTIONS}, got {order}")
    if found.get("Parameters", []) != parameters(node):
        problems.append(f"Parameters {found.get('Parameters', [])} != signature {parameters(node)}")
    expected = "Yields" if is_generator(node) else "Returns" if returns_a_value(node) else None
    present = [name for name in ("Returns", "Yields") if name in found]
    if present != ([expected] if expected else []):
        problems.append(f"expected {expected or 'no Returns or Yields'}, found {present}")
    unknown = [name for name in found.get("Raises", []) if not is_exception(name)]
    if unknown:
        problems.append(f"Raises lists unknown exceptions {unknown}")
    problems += [f"{e!r} must not state a type" for e in found.get("Parameters", []) if " : " in e]
    return problems


def check_class(node: ast.ClassDef, docstring: str) -> list[str]:
    found = sections(docstring)
    problems = [f"unknown section {name!r}" for name in found if name not in CLASS_SECTIONS]
    order = [name for name in found if name in CLASS_SECTIONS]
    if order != [name for name in CLASS_SECTIONS if name in found]:
        problems.append(f"sections must be in the order {CLASS_SECTIONS}, got {order}")
    attributes: list[str] = []
    for member in node.body:
        if isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
            attributes.append(member.target.id)
        elif (
            isinstance(member, ast.FunctionDef)
            and is_property(member)
            and not member.name.startswith("_")
        ):
            attributes.append(member.name)
    methods = [
        member.name
        for member in node.body
        if isinstance(member, ast.FunctionDef)
        and not member.name.startswith("_")
        and not is_property(member)
    ]
    if found.get("Attributes", []) != attributes:
        problems.append(f"Attributes {found.get('Attributes', [])} != {attributes}")
    if found.get("Methods", []) != methods:
        problems.append(f"Methods {found.get('Methods', [])} != public methods {methods}")
    return problems


@pytest.mark.parametrize("module", sorted(SOURCE.glob("*.py")), ids=lambda path: path.name)
def test_every_module_has_a_docstring(module: Path):
    assert ast.get_docstring(ast.parse(module.read_text())), "add a module docstring"


@pytest.mark.parametrize(
    ("name", "node", "public"),
    [pytest.param(name, node, public, id=name) for name, node, public in collect()],
)
def test_definition_follows_the_convention(name: str, node: Definition, public: bool):
    docstring = ast.get_docstring(node)
    if isinstance(node, ast.FunctionDef) and is_property(node):
        assert not check_property(docstring), f"{name}: {check_property(docstring)}"
    elif not public:
        assert not check_private(docstring), f"{name}: {check_private(docstring)}"
    else:
        assert docstring, f"{name} has no docstring"
        problems = (
            check_class(node, docstring)
            if isinstance(node, ast.ClassDef)
            else check_function(node, docstring)
        )
        assert not problems, f"{name}: {problems}"
