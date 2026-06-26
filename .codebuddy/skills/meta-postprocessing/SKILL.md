---
name: meta-postprocessing
description: >
  META 后处理脚本开发助手。当用户需要编写 META (BETA CAE Systems 后处理软件) 的 Python
  脚本时使用此 Skill。触发场景包括：结果读取与可视化 (云图/曲线/动画)、报告自动生成 (PPT/PDF)、
  批量后处理、Annotation 标注、图片导出、session 录制与回放、Report Composer 操作、
  2D Plot 绘制、NVH 分析等。即使用户没有明确说 "META 脚本"，只要涉及 META API 调用、
  meta.results、meta.report、meta.visuals、meta.utils、meta.annotations 等模块，
  也应触发此 Skill。
allowed-tools:
  - search_meta_api
  - list_meta_modules
  - list_meta_categories
  - get_meta_function
disable: false
---

# META 后处理脚本开发助手

## 概述

此 Skill 提供 META Python API 后处理脚本开发的标准化工作流、最佳实践和常见模式参考。涵盖从结果读取到报告生成的全流程。

## 核心工作流

当用户需要编写 META 后处理脚本时，按以下步骤进行：

### Step 1: 明确需求

- 确认输入数据（结果文件类型：`.odb` / `.op2` / `.rst` / `.d3plot` 等）
- 确认后处理类型（云图 / 曲线 / 动画 / 报告 / 数据提取）
- 确认是否需要批量处理多工况
- 确认输出格式（PPT / PDF / 图片 / 数据文件）

### Step 2: 搜索 API

使用 `search_meta_api` MCP 工具查找相关函数：
```
search_meta_api("用户用中文或英文描述的需求", module="可选的模块过滤", top_n=5)
```

常用模块映射：
| 需求 | 推荐搜索关键词 | 相关模块 |
|------|---------------|---------|
| 读取结果文件 | `load read results` | `meta.results` |
| 获取结果工况 | `get result cases` | `meta.results` |
| 创建云图 | `fringe plot contour` | `meta.results`, `meta.visuals` |
| 创建曲线 | `2d plot curve` | `meta.plot2d` |
| 报告生成 | `report presentation slide` | `meta.report` |
| Annotation | `annotation text value` | `meta.annotations` |
| 模型操作 | `model get nodes elements` | `meta.models`, `meta.elements`, `meta.nodes` |
| 截图导出 | `clipboard copy image write jpeg` | `meta.utils` (MetaCommand) |
| Session 录制 | `session record play` | `meta.session` |
| NVH 分析 | `modal response frf` | `meta.nvh` |

### Step 3: 获取完整文档

对关键函数使用 `get_meta_function` 获取参数详情和代码示例。

### Step 4: 编写脚本

遵循标准模板（见 assets/ 目录中的模板文件）。

## META 脚本标准模板

```python
"""
META 后处理脚本 - <功能描述>
"""
import meta
from meta import utils
from meta import models
from meta import results
from meta import annotations
# 按需导入其他模块


def main():
    # 1. 获取已加载的模型
    all_models = utils.get_models()
    if not all_models:
        print("No models loaded.")
        return
    mdl = all_models[0]
    
    # 2. 读取/确认结果
    # cases = results.get_result_cases(mdl.id)
    
    # 3. 创建后处理可视化
    # ...
    
    # 4. 导出或生成报告
    # ...


if __name__ == "__main__":
    main()
```

## 关键约定

### 模块导入方式

META API 支持两种导入方式，推荐使用显式子模块导入：

```python
# 推荐：显式导入子模块
from meta import results
from meta import models
from meta import utils
from meta import annotations
from meta import report
from meta import visuals

# 也可用：通配符导入（不推荐，命名空间污染）
# from meta import *
```

### 模型 ID

大多数 META API 函数需要 `model_id` 参数。获取方式：

```python
# 方式 1：从 get_models() 获取
all_models = utils.get_models()
model_id = all_models[0].id

# 方式 2：从当前活动模型获取
# model_id = utils.get_active_model_id()
```

### 结果工况 (Result Case)

结果文件加载后，每个子工况为一个 Result Case：

```python
cases = results.get_result_cases(model_id)
for case in cases:
    print(f"Case {case.id}: {case.name}")
    # case 对象属性：id, name, subcase, state, step, frequency, time, mode
```

## 常见模式

### 模式 1: 读取结果 + 创建云图

```python
from meta import results, models, utils

def create_fringe_plot():
    mdl = utils.get_models()[0]
    cases = results.get_result_cases(mdl.id)
    if not cases:
        return
    
    # 选择第一个工况
    case = cases[0]
    
    # 激活工况
    results.set_current_result_case(mdl.id, case.id)
    
    # 设置云图显示
    utils.MetaCommand('results fringe "Stresses,First Principal"')
    utils.MetaCommand('options fringebar on')
```

### 模式 2: 批量处理多工况 + 报告生成

这是最常见的后处理自动化模式。参考 `strength_report_batch.py` 的完整实现。

核心流程：
```
遍历工况文件对 → 加载模型 → 执行 session 命令 → 提取数据 → 截图 → 插入 PPT slide
```

### 模式 3: 图片获取与 PPT 插入

三种方式对比（详见 references/image_methods.md）：

| 方式 | MetaCommand | 特点 |
|------|-------------|------|
| clipboard 两步法 | `clipboard copy image` → `slide clipboard pasteimage` | 灵活，可多次粘贴 |
| imagedrop 一步法 | `slide imagedrop "Slide" "Window"` | 简洁，不污染剪贴板 |
| 文件保存法 | `write jpeg "path"` | 可持久化复用 |

```python
# 推荐：clipboard 两步法（最灵活）
utils.MetaCommand('clipboard copy image "MetaPost"')
utils.MetaCommand('report presentation slide clipboard pasteimage "Slide 1"')
utils.MetaCommand('report presentation slide element resize "Slide 1" "Image 1" 0.05 0.05 0.90 0.70')
```

### 模式 4: Annotation 标注

```python
from meta import annotations

def add_stress_annotation():
    # 创建标注
    annotations.AddAnnotation("max_stress", "max=$sval")
    
    # 读取标注值
    visible = annotations.VisibleAnnotations()
    for a in visible:
        print(f"Annotation: {a.text}")
```

### 模式 5: Session 录制回放

```python
from meta import utils

# 回放 .ses 文件中的命令
with open("my_session.ses", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('$'):
            utils.MetaCommand(line)
```

### 模式 6: 数据提取与导出

```python
from meta import elements, nodes, results

def extract_node_data(model_id):
    # 获取节点列表
    all_nodes = nodes.get_nodes(model_id)
    
    # 获取节点结果
    for nd in all_nodes:
        # 获取节点位移/应力等
        pass
```

## Report Composer PPT 操作速查

### Slide 操作
```python
# 创建 slide
utils.MetaCommand('report presentation nameaddslide "Slide name"')

# 删除 slide
utils.MetaCommand('report presentation delslide "Slide name"')
```

### 图片操作
```python
# 粘贴截图
utils.MetaCommand('report presentation slide clipboard pasteimage "Slide 1"')

# 调整图片大小 (x, y, width, height 归一化 0-1)
utils.MetaCommand('report presentation slide element resize "Slide 1" "Image 1" 0.05 0.05 0.90 0.70')
```

### 表格操作
```python
# 创建表格 (行数 列数 字号)
utils.MetaCommand('report presentation slide addtable size fontsize "Slide 1" "Table 1" 5 3 12.0000')

# 编辑单元格 - HTML 中的双引号必须用 &quot; 编码
utils.MetaCommand(
    'report presentation slide edittable cell text "Slide 1" "Table 1" 1 1 '
    '"<body style=&quot; font-family:\'SimSun\'; font-size:12pt;&quot;>'
    '<p style=&quot; margin-top:0px;&quot;>Cell Text</p></body>"'
)

# 调整列宽
utils.MetaCommand('report presentation slide edittable column adjust "Slide 1" "Table 1" 1')
```

### 文本框操作
```python
# 添加文本框
utils.MetaCommand('report presentation slide addtextbox "Slide 1" "Textbox 1" ""')

# 编辑文本框内容
utils.MetaCommand(
    'report presentation slide edittextbox "Slide 1" "Textbox 1" '
    '"<body style=&quot; font-family:\'SimSun\'; font-size:16pt;&quot;>'
    '<p style=&quot; margin-top:0px;&quot;>My Text</p></body>"'
)
```

## 调试技巧

1. **使用 print 输出状态** — META Script Editor 控制台显示
2. **分步执行** — 先测试单工况，确认正确后再批量
3. **`erase all` 清理** — 每个工况开始前清空状态避免残留
4. **try/except 包裹** — 单个工况失败不影响后续处理
5. **路径使用绝对路径** — 避免 Script Editor 运行时的相对路径问题
6. **HTML 双引号编码** — Report Composer 的 HTML 参数中必须用 `&quot;` 代替 `"`
7. **检查 MetaCommand 返回值** — `utils.MetaCommand()` 返回字符串，失败时返回 `"ERROR: ..."` 开头：
   ```python
   result = utils.MetaCommand('results fringe "Stresses,Von Mises"')
   if result and result.startswith("ERROR"):
       print(f"MetaCommand failed: {result}")
   ```

## 性能优化

- 批量处理时，每个工况前后用 `erase all` 清理内存
- 大量数据提取时使用批量 API（如 `get_nodes` 一次获取所有节点）
- 截图前关闭不必要的显示元素（`fringebar off`, `title off`）

## 参考资源

- `references/image_methods.md` — 图片获取三种方法详细对比
- `references/report_composer.md` — Report Composer 完整命令参考
- `references/result_loading.md` — 结果文件加载指南
- `assets/meta_template.py` — META 标准脚本模板
- `assets/report_template.py` — 报告自动生成模板
- `assets/batch_post_template.py` — 批量后处理模板

## MCP 工具使用

此 Skill 依赖以下 MCP 工具：
- `search_meta_api` — 搜索 META API 函数文档
- `list_meta_modules` — 列出所有 META 模块
- `list_meta_categories` — 列出所有分类
- `get_meta_function` — 精确查找函数文档

如需 ANSA 前处理联动，使用 ansa-scripting Skill。
