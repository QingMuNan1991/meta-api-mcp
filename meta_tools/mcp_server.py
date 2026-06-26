"""MCP Server for searching META Python API documentation.

META is the post-processing tool from BETA CAE Systems.
This server provides three-layer search (keyword → fuzzy → text fallback)
over a pre-built index of META API functions parsed from the pydev_meta stubs.
"""


import json
import os
import re
import unicodedata
from pathlib import Path

from mcp.server.fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Text tokenizer
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Split text into tokens.

    For ASCII text: split on non-alphanumeric boundaries.
    For CJK text: keep consecutive CJK chars as one token AND also
                  emit single-char tokens for fallback matching.
    """
    tokens: list[str] = []
    current_ascii: list[str] = []
    current_cjk: list[str] = []

    def _flush_ascii():
        if current_ascii:
            tokens.append("".join(current_ascii).lower())
            current_ascii.clear()

    def _flush_cjk():
        if current_cjk:
            word = "".join(current_cjk)
            tokens.append(word)            # full CJK phrase
            if len(word) > 1:
                tokens.extend(list(word))  # individual chars for fallback
            current_cjk.clear()

    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf":
            _flush_ascii()
            current_cjk.append(ch)
        elif ch.isalnum() or ch == "_":
            _flush_cjk()
            current_ascii.append(ch)
        else:
            _flush_ascii()
            _flush_cjk()

    _flush_ascii()
    _flush_cjk()
    return [t for t in tokens if t]


# ---------------------------------------------------------------------------
# Search engine
# ---------------------------------------------------------------------------

class MetaApiSearcher:
    """Search META API functions using a pre-built index.

    Search strategy (three layers):
    1. Keyword index match  — fast, uses pre-generated keywords per function
    2. Fuzzy text match     — searches description / signature / notes fields
    3. TXT full-text search — scans the raw .txt stub files in txt_docs/
                              (catches edge cases missed by layers 1 & 2)
    """

    def __init__(self, index_path: str):
        with open(index_path, encoding="utf-8") as f:
            data = json.load(f)
        self.metadata: dict = data.get("metadata", {})
        self.functions: list[dict] = data.get("functions", [])
        # Pre-compute lowercased keywords
        for func in self.functions:
            func["_kw_lower"] = [kw.lower() for kw in func.get("keywords", [])]

        # Locate txt_docs directory (same folder as the index file)
        self._txt_docs_dir = Path(index_path).parent / "txt_docs"
        self._txt_cache: dict[str, str] = {}  # stem -> file content

    # ------------------------------------------------------------------
    def _load_txt(self, stem: str) -> str:
        """Load and cache a txt_docs/<stem>.txt file."""
        if stem not in self._txt_cache:
            p = self._txt_docs_dir / f"{stem}.txt"
            if p.exists():
                self._txt_cache[stem] = p.read_text(encoding="utf-8")
            else:
                self._txt_cache[stem] = ""
        return self._txt_cache[stem]

    def _txt_search(
        self,
        query_tokens: list[str],
        module_filter: str | None,
        include_deprecated: bool,
        max_results: int,
    ) -> list[dict]:
        """Layer 3: scan txt stub files and extract matching function blocks."""
        # Decide which txt files to search
        if module_filter:
            bare = module_filter[5:] if module_filter.startswith("meta.") else module_filter
            stems_to_search = [bare]
        else:
            stems_to_search = [p.stem for p in self._txt_docs_dir.glob("*.txt")]

        found: list[dict] = []

        for stem in stems_to_search:
            content = self._load_txt(stem)
            if not content:
                continue

            # Normalize line endings (handle \r\n on Windows)
            content = content.replace("\r\n", "\n").replace("\r", "\n")

            # Split content into function blocks (delimited by "\nFUNCTION: " lines)
            blocks = content.split("\nFUNCTION: ")
            for block in blocks[1:]:  # skip file header
                # Check if any query token appears in the block
                block_lower = block.lower()
                if not any(tok in block_lower for tok in query_tokens):
                    continue

                # Parse the block header lines
                lines = block.splitlines()
                func_name = lines[0].strip() if lines else ""
                mod_line = next((l for l in lines if l.startswith("MODULE:")), "")
                dep_line = next((l for l in lines if l.startswith("DEPRECATED:")), "")
                sig_line = next((l for l in lines if l.startswith("SIGNATURE:")), "")

                if not include_deprecated and dep_line:
                    continue

                module_name = mod_line.replace("MODULE:", "").strip()
                deprecated  = dep_line.replace("DEPRECATED:", "").strip()
                signature   = sig_line.replace("SIGNATURE:", "").strip()

                # Extract docstring (everything after DOCSTRING: until next dashes)
                doc_start = block.find("DOCSTRING:\n")
                doc_end   = block.find("\n" + "-" * 10)
                raw_doc   = ""
                if doc_start >= 0:
                    raw_doc = block[doc_start + len("DOCSTRING:\n"):]
                    if doc_end > doc_start:
                        raw_doc = block[doc_start + len("DOCSTRING:\n"):doc_end]
                # Strip leading 2-space indent
                doc_lines = [l[2:] if l.startswith("  ") else l for l in raw_doc.splitlines()]
                description = " ".join(l.strip() for l in doc_lines if l.strip())[:300]

                found.append({
                    "name": func_name,
                    "module": module_name,
                    "signature": signature,
                    "description": description,
                    "parameters": [],
                    "returns": "",
                    "deprecated": deprecated,
                    "category": stem,
                    "_from_txt": True,
                })

                if len(found) >= max_results:
                    return found

        return found

    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        module: str | None = None,
        category: str | None = None,
        include_deprecated: bool = False,
        top_n: int = 5,
    ) -> list[dict]:
        """Three-layer search: keyword → fuzzy → txt full-text."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # Apply filters
        candidates = self.functions
        if not include_deprecated:
            candidates = [f for f in candidates if not f.get("deprecated")]
        if module:
            mod_filter = _normalize_module(module)
            candidates = [f for f in candidates if f.get("module") == mod_filter]
        else:
            mod_filter = None
        if category:
            exact = [f for f in candidates if f.get("category") == category]
            if exact:
                candidates = exact
            elif any(f.get("category") == category for f in self.functions):
                # Category exists in index but no candidates matched → return empty
                candidates = exact
            else:
                # Category not found; try prefix match (e.g. "elements" → "elements_*")
                candidates = [f for f in candidates
                              if (f.get("category") or "").startswith(category + "_")
                              or (f.get("category") or "") == category]

        query_lower = query.lower()

        # If filters eliminated all candidates, return early
        if not candidates:
            return []

        # --- Layer 1: keyword match ---
        scored: list[tuple[int, dict]] = []
        for func in candidates:
            kw_lower = func["_kw_lower"]
            score_a = sum(1 for tok in query_tokens if tok in kw_lower)
            score_b = sum(1 for kw in kw_lower if kw in query_lower)
            match_count = score_a + score_b
            if match_count > 0:
                scored.append((match_count, func))
        scored.sort(key=lambda x: -x[0])
        results = [func for _, func in scored]

        # --- Layer 2: fuzzy fallback (description + signature + notes) ---
        if len(results) < top_n:
            seen = {(f.get("module"), f.get("name")) for f in results}
            for func in candidates:
                if (func.get("module"), func.get("name")) in seen:
                    continue
                searchable = " ".join([
                    func.get("description", ""),
                    func.get("signature", ""),
                    func.get("notes", ""),
                ]).lower()
                if any(tok in searchable for tok in query_tokens):
                    results.append(func)
                    if len(results) >= top_n * 3:
                        break

        # --- Layer 3: txt full-text search (stub file fallback) ---
        # Only use when no category filter (txt search doesn't support category filtering)
        if len(results) < top_n and self._txt_docs_dir.exists() and not category:
            already_names = {f.get("name") for f in results}
            txt_results = self._txt_search(
                query_tokens,
                module_filter=mod_filter,
                include_deprecated=include_deprecated,
                max_results=(top_n - len(results)) * 3,
            )
            for tf in txt_results:
                if tf["name"] not in already_names:
                    results.append(tf)
                    already_names.add(tf["name"])
                    if len(results) >= top_n:
                        break

        # Trim & clean
        results = results[:top_n]
        clean: list[dict] = []
        for func in results:
            clean.append({k: v for k, v in func.items() if not k.startswith("_")})
        return clean

    # ------------------------------------------------------------------
    def list_modules(self) -> list[str]:
        return self.metadata.get("modules", [])

    def list_categories(self) -> list[str]:
        return self.metadata.get("categories", [])


# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

# --- helpers ---

def _normalize_module(module: str | None) -> str | None:
    """Ensure module name has 'meta.' prefix.

    >>> _normalize_module("elements")    # → "meta.elements"
    >>> _normalize_module("meta.models") # → "meta.models"
    >>> _normalize_module(None)          # → None
    """
    if module is None:
        return None
    return module if module.startswith("meta.") else f"meta.{module}"


# --- server ---

_PKG_DIR = Path(__file__).parent
_INDEX_PATH = str(_PKG_DIR / "meta_api_index.json")
_INDEX_PATH = os.environ.get("META_API_INDEX_PATH", _INDEX_PATH)

mcp = FastMCP(
    "meta-api",
    instructions="""This server provides search access to META Python API documentation.
META is the post-processing / visualization tool from BETA CAE Systems.

Available tools:
- search_meta_api(query, module?, category?, include_deprecated?, top_n?): Search the META API docs
- list_meta_modules(): List all available META API modules
- list_meta_categories(): List all META API function categories
- get_meta_function(function_name, module?): Get full docs for a specific function

Always use these tools when the user asks about META API, post-processing, CAE visualization, or result extraction."""
)
_searcher: MetaApiSearcher | None = None


def _get_searcher() -> MetaApiSearcher:
    global _searcher
    if _searcher is None:
        if not os.path.exists(_INDEX_PATH):
            raise FileNotFoundError(
                f"META API index not found: {_INDEX_PATH}\n"
                "Run `python -m meta_tools.generate_index` to build it first."
            )
        _searcher = MetaApiSearcher(_INDEX_PATH)
    return _searcher


# ---------------------------------------------------------------------------
# Result formatting
# ---------------------------------------------------------------------------

def _format_result(func: dict) -> str:
    """Format a single function as Markdown."""
    lines: list[str] = []

    sig = func.get("signature", func.get("name", ""))
    lines.append(f"### `{sig}`")

    module   = func.get("module", "N/A")
    category = func.get("category", "N/A")
    lines.append(f"**Module:** `{module}`  |  **Category:** `{category}`")

    if func.get("deprecated"):
        lines.append(f"\n> ⚠️ **Deprecated:** {func['deprecated']}")

    lines.append("")
    desc = func.get("description", "").strip()
    if desc:
        lines.append(desc)
    lines.append("")

    params = func.get("parameters", [])
    if params:
        lines.append("**Parameters:**")
        for p in params:
            pname = p.get("name", "")
            ptype = p.get("type", "")
            pdesc = p.get("desc", "")
            type_str = f" `{ptype}`" if ptype else ""
            lines.append(f"- **`{pname}`**{type_str}: {pdesc}")
        lines.append("")

    ret = func.get("returns", "").strip()
    if ret:
        lines.append(f"**Returns:** {ret}")
        lines.append("")

    notes = func.get("notes", "").strip()
    if notes:
        lines.append(f"**Notes:** {notes}")
        lines.append("")

    examples = func.get("examples", "").strip()
    if examples:
        lines.append("**Example:**")
        lines.append("```python")
        lines.append(examples)
        lines.append("```")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_meta_api(
    query: str,
    module: str | None = None,
    category: str | None = None,
    include_deprecated: bool = False,
    top_n: int = 5,
) -> str:
    """Search the META Python API documentation.

    META is the post-processing / visualization tool from BETA CAE Systems.
    Use this tool to find META API functions for scripting and automation.

    Args:
        query: Search query. Supports English and Chinese keywords.
               Examples: "get elements", "获取节点", "create model", "boundary condition"
        module: Optional filter by module name.
                Examples: "meta.elements", "meta.models", "elements" (prefix optional)
        category: Optional filter by category.
                  Examples: "elements_query", "models_modify", "results", "report"
        include_deprecated: Set True to also include deprecated functions (default False)
        top_n: Maximum number of results to return (default 5, max 20)
    """
    try:
        searcher = _get_searcher()
    except FileNotFoundError as e:
        return f"❌ {e}"

    top_n = min(max(1, top_n), 20)
    results = searcher.search(
        query,
        module=module,
        category=category,
        include_deprecated=include_deprecated,
        top_n=top_n,
    )

    if not results:
        msg = f"No META API results found for: `{query}`"
        if module:
            msg += f" (module: `{module}`)"
        if category:
            msg += f" (category: `{category}`)"
        return msg

    header = f"## META API Search Results for `{query}`\n"
    if module or category:
        filters: list[str] = []
        if module:
            filters.append(f"module=`{module}`")
        if category:
            filters.append(f"category=`{category}`")
        header += f"*Filters: {', '.join(filters)}*\n"

    parts = [header]
    for i, func in enumerate(results, 1):
        parts.append(f"---\n\n**Result {i}: `{func['name']}`**\n")
        parts.append(_format_result(func))
        parts.append("")

    return "\n".join(parts)


@mcp.tool()
def list_meta_modules() -> str:
    """List all available META API modules.

    Returns a summary of all modules in the META Python API,
    useful for filtering searches with the `module` parameter.
    """
    try:
        searcher = _get_searcher()
    except FileNotFoundError as e:
        return f"❌ {e}"

    modules = searcher.list_modules()
    metadata = searcher.metadata

    lines = [
        "## META API Modules",
        f"*Total functions: {metadata.get('total_functions', '?')}  |  "
        f"API version: {metadata.get('api_version', '?')}*",
        "",
    ]
    for mod in modules:
        bare = mod[5:] if mod.startswith("meta.") else mod
        count = sum(1 for f in searcher.functions if f.get("module") == mod)
        lines.append(f"- `{mod}` — {count} functions")

    return "\n".join(lines)


@mcp.tool()
def list_meta_categories() -> str:
    """List all available META API categories.

    Categories group functions by their purpose within a module.
    Use these as the `category` filter in search_meta_api.
    """
    try:
        searcher = _get_searcher()
    except FileNotFoundError as e:
        return f"❌ {e}"

    categories = searcher.list_categories()
    lines = ["## META API Categories", ""]
    for cat in categories:
        count = sum(
            1 for f in searcher.functions if f.get("category") == cat
        )
        lines.append(f"- `{cat}` — {count} functions")

    return "\n".join(lines)


@mcp.tool()
def get_meta_function(function_name: str, module: str | None = None) -> str:
    """Get full documentation for a specific META API function by exact name.

    Args:
        function_name: Exact function name (case-sensitive).
                       Examples: "GetElements", "CreateModel", "ImportFile"
        module: Optional module to narrow the search (e.g. "meta.elements")
    """
    try:
        searcher = _get_searcher()
    except FileNotFoundError as e:
        return f"❌ {e}"

    candidates = searcher.functions
    mod_filter = _normalize_module(module)
    if mod_filter:
        candidates = [f for f in candidates if f.get("module") == mod_filter]

    matches = [f for f in candidates if f.get("name") == function_name]

    if not matches:
        # Try case-insensitive
        matches = [f for f in candidates if f.get("name", "").lower() == function_name.lower()]

    if not matches:
        return f"Function `{function_name}` not found in META API index."

    parts = [f"## `{function_name}` — META API\n"]
    for func in matches:
        clean = {k: v for k, v in func.items() if not k.startswith("_")}
        parts.append(_format_result(clean))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Install helper
# ---------------------------------------------------------------------------

def _install_mcp(config_file: str = "codebuddy") -> bool:
    """Register this MCP server in the AI assistant config."""
    import json as _json
    import shutil

    # Support Claude Code / WorkBuddy / CodeBuddy
    config_paths = {
        "claude": Path.home() / ".claude.json",
        "workbuddy": Path.home() / ".workbuddy" / "mcp.json",
        "codebuddy": Path.home() / ".codebuddy" / "mcp.json",
    }
    config_path = config_paths.get(config_file, config_paths["codebuddy"])

    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = _json.load(f)
    else:
        config = {}
        config_path.parent.mkdir(parents=True, exist_ok=True)

    servers = config.setdefault("mcpServers", {})

    if "meta-api" in servers:
        print(f"meta-api MCP server is already registered in {config_path}")
        return True

    exe = shutil.which("meta-api-mcp")
    if not exe:
        print("Error: meta-api-mcp executable not found in PATH.")
        print("  Run:  pip install -e .")
        return False

    servers["meta-api"] = {
        "type": "stdio",
        "command": exe,
        "args": [],
        "env": {},
    }

    with open(config_path, "w", encoding="utf-8") as f:
        _json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Registered meta-api MCP server → {config_path}")
    print(f"   Command: {exe}")
    print("\nRestart your AI assistant to activate.")
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point.

    Usage:
        meta-api-mcp                    Start the MCP server
        meta-api-mcp install            Register in ~/.codebuddy/mcp.json (default)
        meta-api-mcp install workbuddy  Register in ~/.workbuddy/mcp.json
        meta-api-mcp install claude     Register in ~/.claude.json
        meta-api-mcp build-index        Rebuild the function index
    """
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "install":
            target = sys.argv[2] if len(sys.argv) > 2 else "codebuddy"
            success = _install_mcp(target)
            sys.exit(0 if success else 1)

        if cmd == "build-index":
            from meta_tools.generate_index import build_index, save_index
            meta_dir = (
                sys.argv[2] if len(sys.argv) > 2 else
                r"D:\Programs\BETA_CAE_Systems\ansa_v25.1.4\docs\extending"
                r"\python_api\html\_downloads\autocomplete\py_dev\pydev_meta\meta"
            )
            output = sys.argv[3] if len(sys.argv) > 3 else _INDEX_PATH
            functions = build_index(meta_dir)
            save_index(functions, output)
            sys.exit(0)

    try:
        mcp.run()
    except (BrokenPipeError, EOFError, KeyboardInterrupt):
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
