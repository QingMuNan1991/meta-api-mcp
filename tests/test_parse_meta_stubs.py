"""Tests for the META stub parser."""

from __future__ import annotations

import pytest
from pathlib import Path

META_DIR = (
    r"D:\Programs\BETA_CAE_Systems\ansa_v25.1.4\docs\extending"
    r"\python_api\html\_downloads\autocomplete\py_dev\pydev_meta\meta"
)


def _meta_dir_available() -> bool:
    return Path(META_DIR).is_dir()


@pytest.mark.skipif(not _meta_dir_available(), reason="META stubs not available")
def test_parse_init_file():
    """Parse __init__.py and check known functions are extracted."""
    from tools.parse_meta_stubs import parse_stub_file

    init_path = str(Path(META_DIR) / "__init__.py")
    funcs = parse_stub_file(init_path)

    names = {f["name"] for f in funcs}
    assert "ImportCode" in names
    assert "ScriptCurrentDir" in names
    assert "CompileScript" in names

    # ImportCode should have a parameter
    import_code = next(f for f in funcs if f["name"] == "ImportCode")
    assert len(import_code["parameters"]) >= 1
    assert import_code["parameters"][0]["name"] == "path"
    assert "summary" not in import_code or import_code.get("description")


@pytest.mark.skipif(not _meta_dir_available(), reason="META stubs not available")
def test_deprecated_detected():
    """Functions decorated with @deprecated should have non-empty deprecated field."""
    from tools.parse_meta_stubs import parse_stub_file

    init_path = str(Path(META_DIR) / "__init__.py")
    funcs = parse_stub_file(init_path)

    deprecated = [f for f in funcs if f.get("deprecated")]
    # ScriptHomeDir and ScriptUserDir are deprecated
    deprecated_names = {f["name"] for f in deprecated}
    assert "ScriptHomeDir" in deprecated_names
    assert "ScriptUserDir" in deprecated_names


@pytest.mark.skipif(not _meta_dir_available(), reason="META stubs not available")
def test_parse_all_stubs():
    """Parse all stubs and verify reasonable function count."""
    from tools.parse_meta_stubs import parse_all_stubs

    funcs = parse_all_stubs(META_DIR)
    assert len(funcs) > 100, f"Expected >100 functions, got {len(funcs)}"

    # All functions should have required fields
    for f in funcs[:50]:
        assert "name" in f
        assert "module" in f
        assert f["module"].startswith("meta.")
        assert "signature" in f


@pytest.mark.skipif(not _meta_dir_available(), reason="META stubs not available")
def test_category_assignment():
    """Verify category assignment rules."""
    from tools.parse_meta_stubs import parse_all_stubs
    from tools.generate_index import assign_categories

    funcs = parse_all_stubs(META_DIR)
    assign_categories(funcs)

    for f in funcs:
        assert "category" in f
        assert f["category"]  # non-empty

    # elements module functions should get elements_* category
    elem_funcs = [f for f in funcs if f["module"] == "meta.elements"]
    assert all(f["category"].startswith("elements") for f in elem_funcs)


@pytest.mark.skipif(not _meta_dir_available(), reason="META stubs not available")
def test_keyword_generation():
    """Keywords should be non-empty for most functions."""
    from tools.parse_meta_stubs import parse_all_stubs
    from tools.generate_index import assign_categories, generate_keywords_for_functions

    funcs = parse_all_stubs(META_DIR)
    assign_categories(funcs)
    generate_keywords_for_functions(funcs)

    funcs_with_kw = [f for f in funcs if f.get("keywords")]
    assert len(funcs_with_kw) / len(funcs) > 0.9, "Less than 90% of functions have keywords"
