# ANSA Deck 常量参考

## 支持的求解器接口

ANSA 支持多种求解器格式，通过 `ansa.constants` 模块访问。

### 常用 Deck 常量

```python
from ansa import constants

# 结构分析
constants.LSDYNA       # LS-DYNA 显式动力学
constants.NASTRAN      # MSC/NEi Nastran
constants.ABAQUS       # Abaqus/Standard
constants.PAMCRASH     # PAM-CRASH
constants.RADIOSS      # Altair RADIOSS
constants.ANSYS        # ANSYS Mechanical
constants.PERMAS       # PERMAS

# CFD
constants.FLUENT       # ANSYS Fluent
constants.OPENFOAM     # OpenFOAM
constants.STARCCM      # STAR-CCM+

# 通用
constants.GENERIC      # 通用格式
```

### 获取当前 Deck

```python
from ansa import base

# 方法1：获取当前激活的 Deck
current_deck = base.CurrentDeck()

# 方法2：从实体获取
entity = base.GetEntity(constants.NASTRAN, "SHELL", 1)
deck = entity.deck()  # 获取实体的 Deck
```

### Deck 相关函数

```python
# 获取所有可用 Deck
deck_list = base.GetDeckList()

# 设置当前 Deck
base.SetCurrentDeck(constants.ABAQUS)

# 获取 Deck 名称
deck_name = base.GetDeckName(constants.NASTRAN)  # 返回 "NASTRAN"
```

### Deck 类型映射

| 求解器 | 文件扩展名 | 常用场景 |
|--------|----------|---------|
| LSDYNA | `.k`, `.key`, `.dyn` | 碰撞、冲击、爆炸 |
| NASTRAN | `.bdf`, `.nas`, `.dat` | 静力、模态、频响 |
| ABAQUS | `.inp` | 非线性、接触 |
| PAMCRASH | `.pc` | 碰撞安全 |
| RADIOSS | `.rad`, `.0000` | 碰撞、NVH |
| ANSYS | `.cdb`, `.inp` | 多物理场 |

### 注意事项

1. **Deck 必须匹配** — 所有 `CollectEntities`、`GetEntity`、`CreateEntity` 等操作必须使用与模型一致的 Deck 常量
2. **Deck 大小写敏感** — 常量名全大写，如 `constants.LSDYNA`
3. **跨 Deck 操作** — 不同 Deck 的实体类型可能不同（如 LSDYNA 使用 `*PART`，NASTRAN 使用 `PSHELL`）
4. **默认 Deck** — 如果使用 `None` 作为 Deck 参数，某些函数会使用当前激活的 Deck
