"""Tests for the MCP server search engine."""

from __future__ import annotations

import json
import os
import tempfile
import pytest

from tools.mcp_server import MetaApiSearcher, _tokenize


# ---------------------------------------------------------------------------
# Tokenizer tests
# ---------------------------------------------------------------------------

def test_tokenize_english():
    tokens = _tokenize("get_elements model")
    assert "get_elements" in tokens or ("get" in tokens and "elements" in tokens)


def test_tokenize_chinese():
    tokens = _tokenize("获取节点")
    assert "获" in tokens or "获取" in tokens


def test_tokenize_mixed():
    tokens = _tokenize("get 元素 elements")
    assert len(tokens) > 0


# ---------------------------------------------------------------------------
# Searcher tests (using a synthetic mini-index)
# ---------------------------------------------------------------------------

MINI_INDEX = {
    "metadata": {
        "api_version": "v25.1.4",
        "total_functions": 3,
        "modules": ["meta.elements", "meta.models"],
        "categories": ["elements_query", "models_query"],
    },
    "functions": [
        {
            "name": "GetElements",
            "module": "meta.elements",
            "category": "elements_query",
            "signature": "meta.elements.GetElements(model_id: int) -> list[Element]",
            "description": "Returns all elements of a given model.",
            "parameters": [{"name": "model_id", "type": "int", "desc": "Id of the model."}],
            "returns": "list[Element]",
            "examples": "elems = elements.GetElements(0)",
            "deprecated": "",
            "keywords": ["get", "elements", "获取", "单元", "model"],
        },
        {
            "name": "CreateModel",
            "module": "meta.models",
            "category": "models_query",
            "signature": "meta.models.CreateModel(name: str) -> Model",
            "description": "Creates a new model.",
            "parameters": [{"name": "name", "type": "str", "desc": "Name of the model."}],
            "returns": "Model",
            "examples": "mdl = models.CreateModel('my_model')",
            "deprecated": "",
            "keywords": ["create", "model", "创建", "模型"],
        },
        {
            "name": "OldFunction",
            "module": "meta.elements",
            "category": "elements_query",
            "signature": "meta.elements.OldFunction() -> None",
            "description": "An old deprecated function.",
            "parameters": [],
            "returns": "",
            "examples": "",
            "deprecated": "Use GetElements instead.",
            "keywords": ["old", "deprecated"],
        },
    ]
}


@pytest.fixture
def searcher(tmp_path):
    index_file = tmp_path / "test_index.json"
    index_file.write_text(json.dumps(MINI_INDEX), encoding="utf-8")
    return MetaApiSearcher(str(index_file))


def test_search_by_keyword(searcher):
    results = searcher.search("get elements")
    assert len(results) >= 1
    assert results[0]["name"] == "GetElements"


def test_search_chinese(searcher):
    results = searcher.search("获取单元")
    names = [r["name"] for r in results]
    assert "GetElements" in names


def test_deprecated_excluded_by_default(searcher):
    results = searcher.search("old deprecated", include_deprecated=False)
    names = [r["name"] for r in results]
    assert "OldFunction" not in names


def test_deprecated_included_when_requested(searcher):
    results = searcher.search("old deprecated", include_deprecated=True)
    names = [r["name"] for r in results]
    assert "OldFunction" in names


def test_module_filter(searcher):
    results = searcher.search("model", module="meta.models")
    for r in results:
        assert r["module"] == "meta.models"


def test_module_filter_short_name(searcher):
    """Module filter should work with or without 'meta.' prefix."""
    results = searcher.search("model", module="models")
    for r in results:
        assert r["module"] == "meta.models"


def test_top_n_limit(searcher):
    results = searcher.search("elements", top_n=1)
    assert len(results) <= 1


def test_empty_query(searcher):
    results = searcher.search("")
    assert results == []


def test_list_modules(searcher):
    modules = searcher.list_modules()
    assert "meta.elements" in modules
    assert "meta.models" in modules
