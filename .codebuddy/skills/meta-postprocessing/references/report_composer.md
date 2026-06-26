# META Report Composer 命令参考

## 概述

META Report Composer 用于通过 Python 脚本自动生成 PPT/PDF 报告。所有操作通过 `utils.MetaCommand()` 调用。

---

## Slide 管理

### 创建 Slide

```python
# 创建空白 slide
utils.MetaCommand('report presentation nameaddslide "Slide name"')

# 复制 slide
utils.MetaCommand('report presentation dupslide "Source Slide" "Target Slide"')
```

### 删除 Slide

```python
utils.MetaCommand('report presentation delslide "Slide name"')
```

### 重命名 Slide

```python
utils.MetaCommand('report presentation renameslide "Old Name" "New Name"')
```

### 导航

```python
# 下一页
utils.MetaCommand('report presentation nextslide')

# 上一页
utils.MetaCommand('report presentation previousslide')
```

---

## 图片操作

### 粘贴截图

```python
# 从剪贴板粘贴（需先 clipboard copy image）
utils.MetaCommand('report presentation slide clipboard pasteimage "Slide 1"')
```

### 调整大小和位置

```python
# 归一化坐标 (x, y, width, height)，范围 0.0 - 1.0
utils.MetaCommand(
    'report presentation slide element resize "Slide 1" "Image 1" 0.05 0.05 0.90 0.70'
)
```

### 图片编号

图片自动按创建顺序编号：`Image 1`, `Image 2`, `Image 3` ...
删除后编号不会重排，新图片使用下一个可用编号。

---

## 表格操作

### 创建表格

```python
# addtable size fontsize <slide> <table_name> <rows> <cols> <font_size>
utils.MetaCommand(
    'report presentation slide addtable size fontsize "Slide 1" "Table 1" 5 3 12.0000'
)
```

### 编辑单元格

```python
# edittable cell text <slide> <table> <row> <col> <html_content>
# ⚠️ HTML 中的双引号必须用 &quot; 编码！
utils.MetaCommand(
    'report presentation slide edittable cell text "Slide 1" "Table 1" 1 1 '
    '"<body style=&quot; font-family:\'SimSun\'; font-size:12pt; font-weight:600;&quot;>'
    '<p style=&quot; margin-top:0px; margin-bottom:0px;&quot;>'
    'Header Text'
    '</p></body>"'
)
```

### 列宽调整

```python
# 自动调整列宽
utils.MetaCommand(
    'report presentation slide edittable column adjust "Slide 1" "Table 1" 1'
)
```

### 单元格合并

```python
utils.MetaCommand(
    'report presentation slide edittable cell merge "Slide 1" "Table 1" 1 1 1 3'
)
```

---

## 文本框操作

### 添加文本框

```python
utils.MetaCommand(
    'report presentation slide addtextbox "Slide 1" "Textbox 1" "initial text"'
)
```

### 编辑文本框（HTML 格式）

```python
utils.MetaCommand(
    'report presentation slide edittextbox "Slide 1" "Textbox 1" '
    '"<body style=&quot; font-family:\'SimSun\'; font-size:16pt; font-weight:400;&quot;>'
    '<p style=&quot; margin-top:0px; margin-bottom:0px;&quot;>'
    '工况名称 - Max Stress: 123.456 MPa'
    '</p></body>"'
)
```

### 调整文本框大小

```python
utils.MetaCommand(
    'report presentation slide element resize "Slide 1" "Textbox 1" 0.05 0.80 0.90 0.15'
)
```

---

## 显示控制

### 截图前优化显示

```python
# 关闭彩条和标题（让截图更干净）
utils.MetaCommand('options fringebar off')
utils.MetaCommand('options title off')

# ... 截图操作 ...

# 恢复显示
utils.MetaCommand('options fringebar on')
utils.MetaCommand('options title on')
```

---

## HTML 格式参考

### 字体样式

| 属性 | 可选值 | 示例 |
|------|--------|------|
| font-family | 'SimSun', 'Arial', 'Times New Roman' | `font-family:'SimSun'` |
| font-size | 数字 + pt | `font-size:12pt` |
| font-weight | 400 (正常), 600 (粗体) | `font-weight:600` |
| font-style | normal, italic | `font-style:normal` |
| color | 颜色名或十六进制 | `color:#FF0000` |

### 段落样式

| 属性 | 说明 |
|------|------|
| margin-top | 上边距 (px) |
| margin-bottom | 下边距 (px) |
| margin-left | 左边距 (px) |
| margin-right | 右边距 (px) |
| text-indent | 首行缩进 (px) |

### 完整 HTML 模板

```html
<body style=" font-family:'SimSun'; font-size:12pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
Text content here
</p>
</body>
```

⚠️ **关键注意事项**：HTML 属性中的双引号必须编码为 `&quot;`，否则 MetaCommand 会解析失败。

---

## 常见问题

### Q: 表格中显示中文乱码？
A: 确保使用 `font-family:'SimSun'`（宋体），并正确编码 HTML 中的引号。

### Q: 图片编号不连续？
A: Report Composer 的图片编号是累加的，删除后不会重用。使用 `Image 1` 通常安全（新 slide 的第一张图片）。

### Q: 如何导出 PDF？
A: 通过 META GUI 的 Report Composer 界面导出，或使用：
```python
utils.MetaCommand('report presentation export pdf "output.pdf"')
```
