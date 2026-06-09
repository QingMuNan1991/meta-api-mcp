"""Assign categories to META API functions and build the search index."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from tools.parse_meta_stubs import parse_all_stubs


# ---------------------------------------------------------------------------
# Category rules for META modules
# ---------------------------------------------------------------------------

# Maps bare module name (without "meta.") to a base category
_MODULE_CATEGORY_MAP = {
    "elements":     "elements",
    "nodes":        "nodes",
    "models":       "models",
    "parts":        "parts",
    "groups":       "groups",
    "materials":    "materials",
    "connections":  "connections",
    "boundaries":   "boundaries",
    "coordsystems": "coordsystems",
    "planes":       "planes",
    "results":      "results",
    "report":       "report",
    "utils":        "utils",
    "session":      "session",
    "dm":           "dm",
    "calc":         "calc",
    "visuals":      "visuals",
    "windows":      "windows",
    "pages":        "pages",
    "overlay":      "overlay",
    "nvh":          "nvh",
    "spdrm":        "spdrm",
    "tdk":          "tdk",
    "vr":           "vr",
    "em":           "em",
    "sections":     "sections",
    "collaboration":"collaboration",
    "toolbars":     "toolbars",
    "spreadsheet":  "spreadsheet",
    "isofunctions": "isofunctions",
    "annotations":  "annotations",
    "betascript":   "betascript",
    "betavisibility":"betavisibility",
}

# Sub-category keywords for common modules
_GET_KEYWORDS   = ("get", "collect", "find", "filter", "list", "active",
                   "visible", "all", "count", "available", "retrieve")
_SET_KEYWORDS   = ("set", "create", "add", "new", "assign", "define",
                   "insert", "build", "make", "generate")
_DELETE_KEYWORDS = ("delete", "remove", "clear", "reset", "purge", "erase")
_CHECK_KEYWORDS  = ("check", "verify", "validate", "quality", "inspect")
_TRANSFORM_KEYWORDS = ("transform", "move", "rotate", "mirror", "scale",
                        "translate", "copy", "renumber")

_ELEMENTS_SUBCATEGORY = {
    _GET_KEYWORDS:       "elements_query",
    _SET_KEYWORDS:       "elements_modify",
    _DELETE_KEYWORDS:    "elements_delete",
    _CHECK_KEYWORDS:     "elements_check",
    _TRANSFORM_KEYWORDS: "elements_transform",
}

_MODELS_SUBCATEGORY = {
    _GET_KEYWORDS:       "models_query",
    _SET_KEYWORDS:       "models_modify",
    _DELETE_KEYWORDS:    "models_delete",
}


def _match_subcategory(name: str, rules: dict) -> str | None:
    lower = name.lower()
    for keywords, cat in rules.items():
        if any(kw in lower for kw in keywords):
            return cat
    return None


def assign_categories(functions: list[dict]) -> None:
    """Assign a ``category`` field to each function dict in-place."""
    for func in functions:
        module: str = func.get("module", "")
        name: str = func.get("name", "")

        # Strip "meta." prefix to get bare module name
        bare = module[5:] if module.startswith("meta.") else module

        if bare == "elements":
            sub = _match_subcategory(name, _ELEMENTS_SUBCATEGORY)
            func["category"] = sub or "elements_other"

        elif bare == "models":
            sub = _match_subcategory(name, _MODELS_SUBCATEGORY)
            func["category"] = sub or "models_other"

        elif bare in _MODULE_CATEGORY_MAP:
            func["category"] = _MODULE_CATEGORY_MAP[bare]

        else:
            func["category"] = bare if bare else "other"


# ---------------------------------------------------------------------------
# Keyword generation (rule-based, no LLM required)
# ---------------------------------------------------------------------------

# Common English→Chinese tech vocabulary for META/FEA domain
_EN_TO_CN: dict[str, list[str]] = {
    "element": ["单元", "有限元"],
    "node": ["节点"],
    "model": ["模型"],
    "part": ["零件", "部件"],
    "group": ["组", "分组"],
    "material": ["材料", "材质"],
    "connection": ["连接"],
    "boundary": ["边界", "边界条件"],
    "coordinate": ["坐标", "坐标系"],
    "result": ["结果", "后处理"],
    "report": ["报告", "报表"],
    "mesh": ["网格"],
    "shell": ["壳单元", "壳"],
    "solid": ["体单元", "实体"],
    "beam": ["梁单元", "梁"],
    "rigid": ["刚性", "rigid body"],
    "contact": ["接触"],
    "load": ["载荷", "荷载"],
    "force": ["力", "力载荷"],
    "spc": ["约束", "单点约束"],
    "section": ["截面", "截面属性"],
    "create": ["创建", "新建"],
    "delete": ["删除", "移除"],
    "get": ["获取", "得到"],
    "set": ["设置", "设定"],
    "find": ["查找", "搜索"],
    "collect": ["收集", "获取列表"],
    "visible": ["可见", "显示"],
    "active": ["激活", "活动"],
    "import": ["导入"],
    "export": ["导出"],
    "open": ["打开", "读取"],
    "save": ["保存", "写入"],
    "session": ["会话", "工作区"],
    "script": ["脚本"],
    "check": ["检查", "校验"],
    "quality": ["质量", "品质"],
    "transform": ["变换", "转换"],
    "move": ["移动"],
    "rotate": ["旋转"],
    "mirror": ["镜像"],
    "copy": ["复制"],
    "renumber": ["重新编号", "重编号"],
    "name": ["名称", "命名"],
    "id": ["编号", "ID", "标识"],
    "type": ["类型"],
    "color": ["颜色"],
    "display": ["显示", "展示"],
    "plot": ["绘图", "曲线图"],
    "stress": ["应力"],
    "strain": ["应变"],
    "displacement": ["位移"],
    "frequency": ["频率"],
    "modal": ["模态"],
    "animation": ["动画", "动态"],
    "fringe": ["云图"],
    "legend": ["图例"],
    "iso": ["等值面", "等值线"],
    "cut": ["截面", "剖切"],
    "measure": ["测量"],
    "distance": ["距离"],
    "angle": ["角度"],
    "area": ["面积"],
    "volume": ["体积"],
    "mass": ["质量"],
}


def _generate_keywords_for_function(func: dict) -> list[str]:
    """Generate search keywords from a function dict (rule-based, no LLM)."""
    name: str = func.get("name", "")
    description: str = func.get("description", "")
    module: str = func.get("module", "")

    keywords: set[str] = set()

    # 1. Split function name by camelCase / underscore into tokens
    # Insert underscore at case transitions, then split:
    #   GetElements   → Get_Elements  → ["get", "elements"]
    #   HTMLReport    → HTML_Report   → ["html", "report"]
    #   ISO_FUNCTION  → (unchanged)   → ["iso", "function"]
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)   # lower → UPPER
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)  # XML → Parser
    raw_tokens = s.lower().split("_")
    tokens = [t for t in raw_tokens if t and len(t) >= 2]
    keywords.update(tokens)

    # 2. Add the bare function name and full module.name
    keywords.add(name.lower())
    bare_module = module[5:] if module.startswith("meta.") else module
    keywords.add(bare_module)

    # 3. Map to Chinese equivalents
    for tok in list(keywords):
        for en, cns in _EN_TO_CN.items():
            if en in tok:
                keywords.update(cns)

    # 4. Extract key nouns from description (first sentence)
    first_sentence = description.split("\n")[0].split(".")[0].lower()
    desc_tokens = re.findall(r"[a-z]{3,}", first_sentence)
    keywords.update(desc_tokens[:8])

    # 5. Add deprecation hint
    if func.get("deprecated"):
        keywords.add("deprecated")
        keywords.add("废弃")

    return sorted(keywords)


def generate_keywords_for_functions(functions: list[dict]) -> list[dict]:
    """Enrich each function dict with a ``keywords`` field."""
    for func in functions:
        func["keywords"] = _generate_keywords_for_function(func)
    return functions


# ---------------------------------------------------------------------------
# Index building & saving
# ---------------------------------------------------------------------------

def build_index(meta_dir: str) -> list[dict]:
    """Full pipeline: parse stubs → assign categories → generate keywords.

    Args:
        meta_dir: Path to the pydev_meta/meta/ directory.

    Returns:
        Enriched list of function dicts ready for serialization.
    """
    print(f"Parsing META stubs from: {meta_dir}")
    functions = parse_all_stubs(meta_dir)
    print(f"  Found {len(functions)} functions.")

    print("Assigning categories ...")
    assign_categories(functions)

    print("Generating keywords ...")
    generate_keywords_for_functions(functions)

    return functions


def save_index(functions: list[dict], output_path: str, api_version: str = "v25.1.4") -> None:
    """Serialize the function index to JSON.

    Args:
        functions: Enriched function dicts.
        output_path: Destination JSON file path.
        api_version: META version label to embed in metadata.
    """
    modules = sorted({func["module"] for func in functions})
    categories = sorted({func.get("category", "") for func in functions})

    data = {
        "metadata": {
            "api_version": api_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_functions": len(functions),
            "modules": modules,
            "categories": categories,
        },
        "functions": functions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Index saved → {output_path}  ({len(functions)} functions)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, os

    META_DIR = (
        r"D:\Programs\BETA_CAE_Systems\ansa_v25.1.4\docs\extending"
        r"\python_api\html\_downloads\autocomplete\py_dev\pydev_meta\meta"
    )
    OUTPUT = os.path.join(os.path.dirname(__file__), "meta_api_index.json")

    if len(sys.argv) > 1:
        META_DIR = sys.argv[1]
    if len(sys.argv) > 2:
        OUTPUT = sys.argv[2]

    functions = build_index(META_DIR)
    save_index(functions, OUTPUT)
