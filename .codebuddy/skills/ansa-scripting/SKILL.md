---
name: ansa-scripting
description: >
  ANSA Python 脚本开发助手。当用户需要编写、调试或理解 ANSA (BETA CAE Systems 前处理软件)
  的 Python 脚本时使用此 Skill。触发场景包括：批量网格划分、几何清理、连接创建 (焊点/螺栓/胶粘)、
  中面抽取、质量检查、CAD 导入导出、Batch Mesh 脚本、实体增删改查、GUI 插件开发等。
  即使用户没有明确说 "ANSA 脚本"，只要涉及 ANSA API 调用、ansa.base、ansa.mesh、
  ansa.connections、ansa.morph、ansa.batchmesh 等模块，也应触发此 Skill。
allowed-tools:
  - search_ansa_api
disable: false
---

# ANSA Python 脚本开发助手

## 概述

此 Skill 提供 ANSA Python API 脚本开发的标准化工作流和最佳实践。适用于从简单实体操作到复杂批量处理的各类场景。

## 核心工作流

当用户需要编写 ANSA 脚本时，按以下步骤进行：

### Step 1: 明确需求

- 确认目标 Deck 类型（`LSDYNA`, `NASTRAN`, `ABAQUS`, `PAMCRASH`, `RADIOSS` 等）
- 确认操作范围（可见实体 / 全部实体 / 指定 PID / 指定 Part）
- 确认是否需要批量处理

### Step 2: 搜索 API

使用 `search_ansa_api` MCP 工具查找相关函数：
```
search_ansa_api("用户用中文或英文描述的需求", module="可选的模块过滤", top_n=5)
```

常用模块映射：
| 需求 | 推荐搜索关键词 | 相关模块 |
|------|---------------|---------|
| 查询/收集实体 | `collect entities` | `ansa.base` |
| 创建/删除实体 | `create delete` | `ansa.base` |
| 网格划分 | `mesh generate` | `ansa.mesh` |
| 网格编辑 | `mesh edit split` | `ansa.mesh` |
| 网格质量 | `quality check` | `ansa.base.checks.mesh` |
| 连接/焊点 | `connection spotweld` | `ansa.connections` |
| 中面抽取 | `mid surface` | `ansa.morph` |
| 批量网格 | `batch mesh` | `ansa.batchmesh` |
| 几何操作 | `cad geometry` | `ansa.cad` |

### Step 3: 获取完整文档

对关键函数使用 `get_meta_function` / `search_ansa_api` 获取参数详情和代码示例。

### Step 4: 编写脚本

遵循标准模板（见 assets/ 目录中的模板文件）。

## ANSA 脚本标准模板

```python
"""
脚本功能描述
"""
import ansa
from ansa import base
from ansa import constants


def main():
    # 1. 获取当前 Deck 类型
    deck = constants.LSDYNA  # 或 base.CurrentDeck()
    
    # 2. 收集目标实体
    entities = base.CollectEntities(deck, None, "SHELL")
    
    # 3. 对实体执行操作
    # ...
    
    # 4. 更新显示（如需要）
    # base.UpdateDisplay()


if __name__ == "__main__":
    main()
```

## 关键约定

### 实体类型命名

ANSA 使用字符串标识实体类型，以下是常用类型：

| 类型字符串 | 含义 | 对应模块 |
|-----------|------|---------|
| `SHELL` | 壳单元 | mesh |
| `SOLID` | 体单元 | mesh |
| `NODE` | 节点 | base |
| `PSHELL` | 壳属性 | base |
| `PSOLID` | 体属性 | base |
| `ANSAPART` | ANSA 部件 | base |
| `SET` | 集合 | base |
| `FACE` | 面 | base |
| `CONS` | 连接线 | connections |
| `INCLUDE` | 包含文件 | base |
| `GEB_BC` | 通用实体边界条件 | base |

### Deck 常量

```python
from ansa import constants

constants.LSDYNA     # LS-DYNA
constants.NASTRAN    # Nastran
constants.ABAQUS     # Abaqus
constants.PAMCRASH   # PAM-CRASH
constants.RADIOSS    # RADIOSS
constants.ANSYS      # ANSYS
```

### 实体过滤

```python
# 只收集可见实体
entities = base.CollectEntities(deck, None, "SHELL", filter_visible=True)

# 收集某 Part 下的实体
part = base.GetPartFromModuleId("100")
entities = base.CollectEntities(deck, part, "SHELL")

# 收集多个类型
entities = base.CollectEntities(deck, None, ("SHELL", "SOLID"))
```

## 常见模式

### 模式 1: 批量遍历并修改

```python
def modify_all_shells():
    deck = constants.LSDYNA
    shells = base.CollectEntities(deck, None, "SHELL")
    for shell in shells:
        # 获取属性
        pid = base.GetEntityCardValues(deck, shell, "PID")
        # 修改属性
        # base.SetEntityCardValues(deck, shell, {"PID": new_pid})
```

### 模式 2: 网格质量检查

```python
from ansa import base
from ansa import constants

def check_mesh_quality():
    deck = constants.NASTRAN
    # 获取所有 shell 的 off elements 统计
    off_dict = base.CalculateOffElements("Shells", details=True)
    print(f"Total off elements: {off_dict['TOTAL OFF']}")
    
    # 对每个 Part 单独检查
    parts = base.CollectEntities(deck, None, "ANSAPART")
    for part in parts:
        off = base.CalculateOffElements(part)
        if off.get("TOTAL OFF", 0) > 0:
            print(f"Part {part._id}: {off['TOTAL OFF']} off elements")
```

### 模式 3: 创建新实体

```python
def create_new_part():
    deck = constants.NASTRAN
    # 创建新 Part
    new_part = base.NewPart("MyPart", "1001")
    # 创建属性
    prop = base.CreateEntity(deck, "PSHELL", {"NAME": "prop1", "T": 2.0})
```

### 模式 4: 删除实体

```python
def delete_bad_shells(quality_threshold=0.3):
    deck = constants.NASTRAN
    shells = base.CollectEntities(deck, None, "SHELL")
    bad_shells = []
    for shell in shells:
        quality = compute_quality(shell)  # 自定义质量函数
        if quality < quality_threshold:
            bad_shells.append(shell)
    if bad_shells:
        base.DeleteEntities(bad_shells)
```

## 调试技巧

1. **使用 `print` 输出进度** — ANSA 脚本编辑器会在控制台显示输出
2. **分步测试** — 先在小范围实体上测试，确认无误后再扩大范围
3. **检查返回值** — 大多数 API 返回 0/1 表示失败/成功，或返回 None 表示无效
4. **使用 `filter_visible=True`** — 调试时先处理可见实体，避免误操作隐藏实体
5. **保存前备份** — 在批量操作前保存当前模型

## 性能优化

- 批量收集实体后用列表一次性处理，避免循环内反复查询
- 大量实体操作时考虑使用 `batchmesh` 模块
- 显示更新（`UpdateDisplay`）只在必要时调用，不要在循环内调用

## 参考资源

- `references/entity_types.md` — ANSA 实体类型完整对照表
- `references/deck_constants.md` — Deck 常量参考
- `assets/ansa_template.py` — 标准脚本模板
- `assets/gui_template.py` — GUI 插件模板
- `assets/batchmesh_template.py` — Batch Mesh 脚本模板

## MCP 工具使用

此 Skill 依赖以下 MCP 工具：
- `search_ansa_api` — 搜索 ANSA API 函数文档
