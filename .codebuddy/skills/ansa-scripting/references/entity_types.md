# ANSA 实体类型完整对照表

## 通用实体类型 (所有 Deck)

| 类型字符串 | 中文名称 | 说明 | 对应 API 模块 |
|-----------|---------|------|-------------|
| `NODE` | 节点 | 有限元网格节点 | base |
| `SHELL` | 壳单元 | 2D 壳单元 (Tria3/Quad4 等) | mesh |
| `SOLID` | 体单元 | 3D 体单元 (Tetra4/Hexa8 等) | mesh |
| `BEAM` | 梁单元 | 1D 梁单元 | mesh |
| `BAR` | 杆单元 | 1D 杆单元 | mesh |
| `SPRING` | 弹簧单元 | 1D 弹簧单元 | mesh |
| `MASS` | 质量单元 | 0D 质量单元 | mesh |
| `FACE` | 面 | 几何面 | base |
| `CURVE` | 曲线 | 几何曲线 | base |
| `POINT` | 点 | 几何点 | base |
| `ANSAPART` | ANSA 部件 | 组织管理单元 | base |
| `SET` | 集合 | 实体集合 | base |
| `INCLUDE` | 包含文件 | 模型文件引用 | base |
| `GRID` | 网格点 | Nastran 格式节点 | base |

## 属性类型

| 类型字符串 | 中文名称 | 对应单元类型 |
|-----------|---------|------------|
| `PSHELL` | 壳属性 | SHELL |
| `PSOLID` | 体属性 | SOLID |
| `PBEAM` | 梁属性 | BEAM |
| `PBAR` | 杆属性 | BAR |
| `PMASS` | 质量属性 | MASS |
| `MAT1` | 材料 (各向同性) | - |
| `MAT8` | 材料 (正交各向异性) | - |
| `MAT24` | 材料 (弹塑性) | - |

## 连接类型

| 类型字符串 | 中文名称 | 说明 |
|-----------|---------|------|
| `CONS` | 连接线 | 用于定义连接关系 |
| `SPOTWELD` | 焊点 | 点焊连接 |
| `BOLT` | 螺栓 | 螺栓连接 |
| `ADHESIVE` | 胶粘 | 胶粘连接 |
| `SEAMWELD` | 焊缝 | 焊缝连接 |
| `RBE2` | 刚性单元 | 刚性连接 |
| `RBE3` | 插值单元 | 载荷分配连接 |

## 边界条件类型

| 类型字符串 | 中文名称 | 说明 |
|-----------|---------|------|
| `SPC` | 单点约束 | 固定边界 |
| `LOAD` | 载荷 | 集中力/压力等 |
| `BOUNDARY` | 边界条件 | 通用边界 |

## 通用实体类型 (GEB)

| 类型字符串 | 说明 |
|-----------|------|
| `GEB_BC` | 通用实体 - 边界条件 |
| `GEB_GN` | 通用实体 - 组 |
| `GEB_MT` | 通用实体 - 材料 |
| `GEB_OR` | 通用实体 - 方向 |
| `GEB_SB` | 通用实体 - 子边界 |

## Morph 相关类型

| 类型字符串 | 说明 |
|-----------|------|
| `MORPHBOX` | 变形盒 |
| `MORPHEDGE` | 变形边 |
| `MORPHFACE` | 变形面 |
| `MORPHPARAM` | 变形参数 |

## 使用示例

```python
from ansa import base
from ansa import constants

# 收集多种类型实体
deck = constants.NASTRAN
types = ("SHELL", "SOLID", "BEAM")
entities = base.CollectEntities(deck, None, types)

# 获取实体类型
entity_type = base.GetEntityType(entity)

# 判断实体类型
if base.IsShell(entity):
    print("这是一个壳单元")
```
