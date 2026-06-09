# meta-api-mcp

**MCP Server for META Python API** — BETA CAE Systems 后处理工具的 AI 辅助开发工具。

基于 [`ansa-api-mcp`](https://github.com/your/ansa-api-mcp) 的架构，针对 META API Python stubs 重新构建，支持：

- 🔍 三层搜索（关键词 → 模糊 → 全文回退）
- 🌐 中英文双语检索
- 📦 4 个 MCP 工具：搜索函数、列出模块、列出分类、精确查找
- ⚡ 无需 LLM 即可完成索引构建（规则式关键词生成）

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
python -m tools build-index

# 方式二：指定 META stubs 目录
python -m tools build-index "D:\path\to\pydev_meta\meta"

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

| 模块 | 说明 |
|------|------|
| `meta.elements` | 单元操作（增删改查、变换）|
| `meta.nodes` | 节点操作 |
| `meta.models` | 模型管理 |
| `meta.parts` | 零件/部件 |
| `meta.groups` | 分组管理 |
| `meta.materials` | 材料定义 |
| `meta.connections` | 连接关系 |
| `meta.boundaries` | 边界条件 |
| `meta.results` | 结果后处理 |
| `meta.report` | 报告生成 |
| `meta.utils` | 通用工具函数 |
| `meta.visuals` | 可视化控制 |
| `meta.session` | 会话/工作区 |
| `meta.dm` | 数据管理 |
| ... | 共约 36 个模块 |

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
