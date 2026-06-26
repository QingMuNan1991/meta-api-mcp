# META 图片获取方法对比

在 META 后处理脚本中，将 3D 窗口画面插入 PPT 有三种方法。本文档详细对比各方法的原理、优缺点和适用场景。

---

## 方法 1: clipboard copy + paste（两步法）⭐ 推荐

### 原理
先通过 MetaCommand 将当前 3D 窗口（如 `"MetaPost"`）画面复制到系统剪贴板，再通过 Report Composer 的粘贴命令插入 PPT。

### 代码示例

```python
from meta import utils

# Step 1: 截图到剪贴板
utils.MetaCommand('clipboard copy image "MetaPost"')

# Step 2: 粘贴到指定 slide
utils.MetaCommand('report presentation slide clipboard pasteimage "Slide 1"')

# Step 3: 调整图片位置和大小 (x, y, width, height 归一化 0-1)
utils.MetaCommand(
    'report presentation slide element resize "Slide 1" "Image 1" 0.05 0.05 0.90 0.70'
)
```

### 特点

| 维度 | 说明 |
|------|------|
| 步骤数 | 2 步 (copy + paste) |
| 中间介质 | 系统剪贴板（位图） |
| 剪贴板污染 | 会覆盖剪贴板内容 |
| 可复用性 | copy 一次可 paste 多次到不同 slide |
| Batch Mode | ❌ 不支持 |
| API 暴露 | 仅 MetaCommand 命令 |

### 适用场景
- 需要将同一截图粘贴到多个 slide
- 需要灵活控制粘贴时机

---

## 方法 2: imagedrop（一步法）

### 原理
META session 录制命令，直接将指定窗口截图"拖放"到 Report Composer slide 中，一步完成。

### 代码示例

```python
from meta import utils

# 一步完成：截图 + 插入 PPT
utils.MetaCommand('report presentation slide imagedrop "Slide 1" "MetaPost"')
```

### 特点

| 维度 | 说明 |
|------|------|
| 步骤数 | 1 步 |
| 中间介质 | 无（直接渲染到 Report Composer） |
| 剪贴板污染 | 不影响 |
| 可复用性 | 每次调用重新渲染 |
| Batch Mode | ❌ 不支持 |
| API 暴露 | 仅 MetaCommand 命令 |

### 适用场景
- 简单场景，不需要重复使用同一截图
- 希望保持剪贴板内容不被覆盖

### 注意事项
- `imagedrop` 是 META 内部命令，未在 Python API 中作为独立函数暴露
- 只能通过 `utils.MetaCommand()` 调用

---

## 方法 3: write jpeg + 文件（磁盘保存法）

### 原理
先将窗口截图保存为 JPEG 文件到磁盘，后续可通过其他方式使用该文件。

### 代码示例

```python
from meta import utils

# 保存为 JPEG 文件（85 为质量参数 1-100）
utils.MetaCommand('write jpeg "F:/output/screenshot.jpeg" 85')

# 也可用 PNG 格式
# utils.MetaCommand('write png "F:/output/screenshot.png"')
```

### 特点

| 维度 | 说明 |
|------|------|
| 步骤数 | 1 步（保存文件） |
| 中间介质 | 磁盘文件 |
| 剪贴板污染 | 不影响 |
| 可复用性 | 文件可长期保存和复用 |
| Batch Mode | ❌ 不支持 |
| API 暴露 | 仅 MetaCommand 命令 |

### 适用场景
- 需要将截图保存为独立文件用于其他用途
- 需要生成图片报告而非 PPT
- 需要存档截图

---

## 方法 4: SnapShotWindow API

### 原理
使用文档化的 Python API 函数 `utils.SnapShotWindow()` 保存截图。

### 代码示例

```python
from meta import utils

# 保存窗口截图为文件
result = utils.SnapShotWindow(
    "F:/output/screenshot.jpeg",  # 文件名
    "JPEG",                         # 图片格式
    "MetaPost"                      # 窗口标题
)
# result: 1 = 成功, 0 = 失败
```

### 特点

| 维度 | 说明 |
|------|------|
| 步骤数 | 1 步 |
| 中间介质 | 磁盘文件 |
| 返回值 | int (1 成功 / 0 失败) |
| Batch Mode | ❌ 不支持 |
| API 暴露 | 文档化的 Python API 函数 |

### 适用场景
- 需要在脚本中进行错误处理（检查返回值）
- 偏好使用文档化 API 而非 MetaCommand

---

## 方法对比总表

| 维度 | clipboard 两步法 | imagedrop 一步法 | write jpeg | SnapShotWindow |
|------|:---:|:---:|:---:|:---:|
| 步骤数 | 2 | 1 | 1 | 1 |
| 输出目标 | PPT slide | PPT slide | 磁盘文件 | 磁盘文件 |
| 剪贴板污染 | ✅ 会 | ❌ 不会 | ❌ 不会 | ❌ 不会 |
| 可多次粘贴 | ✅ 可以 | ❌ 不可以 | N/A | N/A |
| 错误处理 | 无返回值 | 无返回值 | 无返回值 | 返回 0/1 |
| 文档化 API | ❌ | ❌ | ❌ | ✅ |
| Batch Mode | ❌ | ❌ | ❌ | ❌ |

---

## 推荐策略

1. **PPT 报告** → 使用 clipboard 两步法（最灵活）
2. **简单单次截图** → 使用 imagedrop（简洁）
3. **需要保存文件** → 使用 SnapShotWindow（有返回值，可错误处理）
4. **所有方法都需要 GUI 环境**，Batch Mode 不可用
