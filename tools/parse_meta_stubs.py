"""Parse META Python API stub files into structured function/class dicts.

META API stubs are located in pydev_meta/meta/*.py and use NumPy-style docstrings.
This module parses them with Python's ast module — no HTML parsing required.
"""

from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Docstring section parser (NumPy style)
# ---------------------------------------------------------------------------

_SECTION_HEADERS = {
    "Parameters", "Returns", "Raises", "Notes",
    "Examples", "See Also", "Attributes", "Methods",
}

_DEPRECATED_RE = re.compile(
    r"@typing_extensions\.deprecated\(['\"](.+?)['\"]\)",
    re.DOTALL,
)


def _parse_numpy_docstring(raw: str) -> dict[str, Any]:
    """Parse a NumPy-style docstring into a structured dict.

    Returns:
        {
            "summary": str,
            "parameters": [{"name": str, "type": str, "desc": str}, ...],
            "returns": str,
            "raises": str,
            "notes": str,
            "examples": str,
            "deprecated": str,   # non-empty if function is deprecated
        }
    """
    if not raw:
        return {
            "summary": "", "parameters": [], "returns": "",
            "raises": "", "notes": "", "examples": "", "deprecated": "",
        }

    # Clean leading/trailing blank lines
    lines = textwrap.dedent(raw).splitlines()
    # Strip leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    # Strip trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    # Split into sections
    sections: dict[str, list[str]] = {"__preamble__": []}
    current_section = "__preamble__"

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect section header: a line whose stripped form is a known header,
        # optionally followed by a dashes line
        if stripped in _SECTION_HEADERS and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r"^-+$", next_line):
                current_section = stripped
                sections[current_section] = []
                i += 2  # skip the dashes line
                continue

        sections[current_section].append(line)
        i += 1

    # --- Summary ---
    preamble = "\n".join(sections.get("__preamble__", []))
    # Handle '.. deprecated::' RST directive in preamble
    deprecated_from_docstring = ""
    dep_match = re.search(r"\.\. deprecated::[^\n]*\n\s+(.+)", preamble)
    if dep_match:
        deprecated_from_docstring = dep_match.group(1).strip()
        # Remove the deprecated block from preamble for clean summary
        preamble = re.sub(r"\.\. deprecated::.*?(?=\n\n|\Z)", "", preamble, flags=re.DOTALL)

    summary = preamble.strip()

    # --- Parameters ---
    parameters: list[dict] = []
    param_lines = sections.get("Parameters", [])
    param_text = "\n".join(param_lines)
    # Each param block:  "name : type\n    description"
    for m in re.finditer(
        r"^(\*{0,2}\w[\w.*\[\], ]*?)\s*:\s*(.*?)\n((?:[ \t]+.*\n?)*)",
        param_text,
        re.MULTILINE,
    ):
        pname = m.group(1).strip()
        ptype = m.group(2).strip()
        pdesc = textwrap.dedent(m.group(3)).strip()
        parameters.append({"name": pname, "type": ptype, "desc": pdesc})

    # --- Returns ---
    ret_lines = sections.get("Returns", [])
    ret_text = "\n".join(ret_lines).strip()
    # Extract just the description (skip type annotation line)
    ret_desc = ""
    ret_block_match = re.search(r"\n([ \t]+.+)", ret_text)
    if ret_block_match:
        ret_desc = textwrap.dedent(ret_block_match.group(0)).strip()
    else:
        ret_desc = ret_text

    # --- Examples ---
    example_lines = sections.get("Examples", [])
    # Strip leading "::" markers
    cleaned_examples: list[str] = []
    for ln in example_lines:
        if ln.strip() == "::":
            continue
        cleaned_examples.append(ln)
    examples = textwrap.dedent("\n".join(cleaned_examples)).strip()

    # --- Notes ---
    notes = "\n".join(sections.get("Notes", [])).strip()

    # --- Raises ---
    raises = "\n".join(sections.get("Raises", [])).strip()

    return {
        "summary": summary,
        "parameters": parameters,
        "returns": ret_desc,
        "raises": raises,
        "notes": notes,
        "examples": examples,
        "deprecated": deprecated_from_docstring,
    }


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _build_signature(func_def: ast.FunctionDef | ast.AsyncFunctionDef, module_name: str) -> str:
    """Reconstruct a human-readable signature string from an AST node."""
    args = func_def.args
    param_parts: list[str] = []

    # Positional-only args (before /)
    n_posonlyargs = len(args.posonlyargs)
    for i, arg in enumerate(args.posonlyargs):
        ann = _annotation_str(arg.annotation)
        param_parts.append(f"{arg.arg}: {ann}" if ann else arg.arg)
    if n_posonlyargs:
        param_parts.append("/")

    # Regular args
    n_args = len(args.args)
    n_defaults = len(args.defaults)
    default_offset = n_args - n_defaults
    for i, arg in enumerate(args.args):
        ann = _annotation_str(arg.annotation)
        part = f"{arg.arg}: {ann}" if ann else arg.arg
        default_idx = i - default_offset
        if default_idx >= 0:
            default_val = _expr_str(args.defaults[default_idx])
            part += f"={default_val}"
        param_parts.append(part)

    # *args
    if args.vararg:
        ann = _annotation_str(args.vararg.annotation)
        param_parts.append(f"*{args.vararg.arg}: {ann}" if ann else f"*{args.vararg.arg}")
    elif args.kwonlyargs:
        param_parts.append("*")

    # Keyword-only args
    kw_defaults = args.kw_defaults
    for i, arg in enumerate(args.kwonlyargs):
        ann = _annotation_str(arg.annotation)
        part = f"{arg.arg}: {ann}" if ann else arg.arg
        if kw_defaults[i] is not None:
            part += f"={_expr_str(kw_defaults[i])}"
        param_parts.append(part)

    # **kwargs
    if args.kwarg:
        ann = _annotation_str(args.kwarg.annotation)
        param_parts.append(f"**{args.kwarg.arg}: {ann}" if ann else f"**{args.kwarg.arg}")

    ret = _annotation_str(func_def.returns)
    sig = f"{module_name}.{func_def.name}({', '.join(param_parts)})"
    if ret:
        sig += f" -> {ret}"
    return sig


def _annotation_str(node: ast.expr | None) -> str:
    """Convert an AST annotation node to a string."""
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _expr_str(node: ast.expr | None) -> str:
    """Convert an AST expression node to a string."""
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _is_deprecated(decorator_list: list[ast.expr]) -> str:
    """Return the deprecation message if the function is decorated with @deprecated.

    Handles both bare ``@deprecated("msg")`` and qualified forms like
    ``@typing_extensions.deprecated("msg")``.
    """
    for dec in decorator_list:
        if not isinstance(dec, ast.Call) or not dec.args:
            continue
        func = dec.func
        # Normal case: @deprecated("msg")
        if isinstance(func, ast.Name) and func.id == "deprecated":
            return _expr_str(dec.args[0]).strip("'\"")
        # Qualified case: @typing_extensions.deprecated("msg")
        if isinstance(func, ast.Attribute) and func.attr == "deprecated":
            return _expr_str(dec.args[0]).strip("'\"")
    return ""


# ---------------------------------------------------------------------------
# Public parse functions
# ---------------------------------------------------------------------------

def parse_stub_file(stub_path: str) -> list[dict]:
    """Parse a single META API stub .py file into a list of function dicts.

    Each function dict contains:
        name, module, signature, description, parameters,
        returns, raises, notes, examples, deprecated

    Args:
        stub_path: Absolute path to a meta/*.py stub file.

    Returns:
        List of function dicts (one per top-level function).
    """
    path = Path(stub_path)
    # Derive module name: "elements.py" -> "meta.elements"
    module_name = f"meta.{path.stem}"

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as exc:
        return []

    results: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Only top-level functions (parent is Module)
        # We'll filter by checking the node is directly in tree.body
        if node not in tree.body:
            continue

        raw_doc = ast.get_docstring(node, clean=False) or ""
        parsed = _parse_numpy_docstring(raw_doc)

        # Prefer deprecation info from decorator over docstring
        deprecated = _is_deprecated(node.decorator_list) or parsed["deprecated"]

        signature = _build_signature(node, module_name)

        results.append({
            "name": node.name,
            "module": module_name,
            "signature": signature,
            "description": parsed["summary"],
            "parameters": parsed["parameters"],
            "returns": parsed["returns"],
            "raises": parsed["raises"],
            "notes": parsed["notes"],
            "examples": parsed["examples"],
            "deprecated": deprecated,
        })

    return results


def parse_all_stubs(meta_dir: str) -> list[dict]:
    """Parse all META stub files in the given directory.

    Args:
        meta_dir: Path to the pydev_meta/meta/ directory.

    Returns:
        Combined list of function dicts from all stub files.
    """
    results: list[dict] = []
    dir_path = Path(meta_dir)

    # Skip guitk.py by default (94k lines, GUI toolkit, rarely needed for scripting)
    skip_modules = {"guitk", "plot2d", "__pycache__"}

    for stub_file in sorted(dir_path.glob("*.py")):
        if stub_file.stem in skip_modules:
            continue
        funcs = parse_stub_file(str(stub_file))
        results.extend(funcs)

    return results
