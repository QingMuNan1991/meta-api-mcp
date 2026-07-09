# meta-api-mcp

**MCP Server for META Python API** — BETA CAE Systems 后处理工具的 AI 辅助开发工具。

基于 [`ansa-api-mcp`](https://github.com/your/ansa-api-mcp) 的架构，针对 META API Python stubs 重新构建，支持：

- 🔍 三层搜索（关键词 → 模糊 → 全文回退）
- 🌐 中英文双语检索
- 📦 4 个 MCP 工具：搜索函数、列出模块、列出分类、精确查找
- ⚡ 无需 LLM 即可完成索引构建（规则式关键词生成）

> **当前索引（enriched @ 2026-07-09）**：基于 **ANSA/META v25.1.4** 的 `pydev_meta` 桩文件重建，
> 共 **3366** 个 API 符号 / **36** 个模块。除顶层函数外，还纳入了
> **类公共方法**（如 `meta.nodes.Node.get_coordinates`）与 **模块级常量**
> （如 `meta.constants.ABAQUS_FASTENER`），覆盖率 100%，与 v25.1.4 桩完全一致、无旧版本残留。

---

## 快速上手

### 1. 安装依赖

```bash
cd meta-api-mcp
pip install -e .
```

### 2. 构建索引

```bash
# 方式一：使用默认路径（D:\Programs\BETA_CAE_Systems\ansa_v25.1.4\...）
python -m meta_tools generate_index

# 方式二：指定 META stubs 目录
python -m meta_tools generate_index "D:\path\to\pydev_meta\meta"

# 方式三：通过已安装的可执行文件（需先 pip install -e .）
meta-api-mcp build-index

# 方式三：指定输入和输出路径
python -m tools build-index "D:\path\to\meta" ".\tools\meta_api_index.json"
```

索引构建完成后，会在 `tools/meta_api_index.json` 生成索引文件。

### 3. 注册到 WorkBuddy（推荐）

```bash
meta-api-mcp install
# 或注册到 Claude Code
meta-api-mcp install claude
```

### 4. 手动配置（WorkBuddy / Claude Code）

在配置文件中添加：

```json
{
  "mcpServers": {
    "meta-api": {
      "type": "stdio",
      "command": "meta-api-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

---

## MCP 工具一览

| 工具 | 用途 |
|------|------|
| `search_meta_api` | 搜索 META API 函数（支持中英文） |
| `list_meta_modules` | 列出所有 META 模块及函数数量 |
| `list_meta_categories` | 列出所有分类 |
| `get_meta_function` | 按精确函数名获取完整文档 |

### `search_meta_api` 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | str | 搜索词（中英文均可）|
| `module` | str? | 限定模块，如 `"meta.elements"` 或 `"elements"` |
| `category` | str? | 限定分类，如 `"elements_query"` |
| `include_deprecated` | bool | 是否包含已废弃函数（默认 False）|
| `top_n` | int | 返回数量上限（默认 5，最大 20）|

---

## 项目结构

```
meta-api-mcp/
├── tools/
│   ├── parse_meta_stubs.py   # 解析 pydev_meta/meta/*.py stubs
│   ├── generate_index.py     # 构建搜索索引
│   ├── mcp_server.py         # FastMCP 服务端 + 4个工具
│   ├── meta_api_index.json   # 预构建索引（构建后生成）
│   └── __init__.py
├── tests/
│   ├── test_parse_meta_stubs.py
│   └── test_mcp_server.py
├── demo/
│   ├── get_nodes.py          # 示例：获取节点坐标
│   └── fringe_plot.py        # 示例：云图结果
├── pyproject.toml
└── README.md
```

---

## META API 模块覆盖范围

当前索引共 **3366** 个 API 符号，分布在 **36** 个模块（已纳入类方法与常量）：

| 模块 | 数量 | 说明 |
|------|-----:|------|
| `meta.elements` | 213 | 单元操作（增删改查、变换）|
| `meta.nodes` | 133 | 节点操作（含 `Node.*` 方法）|
| `meta.models` | 185 | 模型管理（含 `Model.*` 方法）|
| `meta.parts` | 198 | 零件/部件 |
| `meta.groups` | 168 | 分组管理（含 `Group.*` 方法）|
| `meta.materials` | 122 | 材料定义 |
| `meta.connections` | 87 | 连接关系 |
| `meta.boundaries` | 102 | 边界条件（含 `Boundary.*` 方法）|
| `meta.results` | 229 | 结果后处理 |
| `meta.report` | 399 | 报告生成（含 `Report.*` 方法）|
| `meta.utils` | 123 | 通用工具函数 |
| `meta.visuals` | 115 | 可视化控制 |
| `meta.windows` | 210 | 窗口管理（含 `Window.*` 方法）|
| `meta.session` | 12 | 会话/工作区 |
| `meta.dm` | 95 | 数据管理（Data Manager）|
| `meta.constants` | 190 | 求解器/实体类型等常量枚举 |
| `meta.tdk` | 85 | 工具栏控件（`Toolbar`/`CheckBox` 等类方法）|
| `meta.vr` | 15 | 虚拟现实（`VR.*` 方法）|
| `meta.spdrm` | 14 | SPDM 工作流（`process.*` 方法）|
| `meta.em` | 8 | 电磁（Farfield 等）|
| `meta.coordsystems` | 62 | 坐标系 |
| `meta.planes` | 84 | 平面 |
| `meta.sections` | 22 | 截面 |
| `meta.calc` | 18 | 计算 |
| `meta.nvh` | 27 | NVH |
| `meta.isofunctions` | 53 | 等值面/等值线 |
| `meta.overlay` | 28 | 叠加层 |
| `meta.pages` | 50 | 页面 |
| `meta.spreadsheet` | 61 | 表格 |
| `meta.annotations` | 154 | 标注 |
| `meta.toolbars` | 30 | 工具栏 |
| `meta.collaboration` | 2 | 协同 |
| `meta.betascript` | 9 | BetaScript 脚本 |
| `meta.betavisibility` | 1 | Beta 可见性 |
| `meta.base` | 55 | 基础/通用 |
| `meta.__init__` | 7 | 包初始化/重导出 |

> **命名约定**：类方法以 `ClassName.method` 入库（例如 `meta.nodes.Node.get_coordinates`），
> 常量以 `meta.constants.NAME` 入库（例如 `meta.constants.ABAQUS_FASTENER`）；
> 搜索时可用类名/方法名/常量名直接命中。
>
> `guitk.py`（GUI 工具包，94k 行）和 `plot2d.py` 默认跳过，可在 `parse_meta_stubs.py` 中修改 `skip_modules` 启用。

---

## 开发

```bash
# 运行测试
pytest tests/ -v

# 仅运行不需要 META stubs 的测试
pytest tests/test_mcp_server.py -v

# 手动测试服务器（在标准输入输出上启动）
python -m tools
```

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `META_API_INDEX_PATH` | 覆盖默认索引文件路径 |
