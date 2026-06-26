# META 结果加载指南

## 支持的结果文件格式

META 支持多种求解器的结果文件格式：

| 求解器 | 文件扩展名 | Deck 常量 |
|--------|----------|-----------|
| Abaqus | `.odb` | `ABAQUS` |
| Nastran | `.op2`, `.xdb`, `.h5` | `NASTRAN` |
| LS-DYNA | `.d3plot`, `.binout` | `DYNA` |
| ANSYS | `.rst`, `.rth` | `ANSYS` |
| PAM-CRASH | `.erf`, `.DSY` | `PAMCRASH` |
| RADIOSS | `.h3d`, `A001` | `RADIOSS` |

## 加载结果文件

### 方式 1: MetaCommand（session 命令）

```python
from meta import utils

# 加载结果文件
utils.MetaCommand('read file "F:/results/model.odb"')

# 加载几何模型
utils.MetaCommand('read geometry "F:/results/model.inp"')
```

### 方式 2: results 模块 API

```python
from meta import results

# 加载标量结果
results.LoadScalar(model_id, filename, deck, state_id, data_expression)

# 加载向量结果
results.LoadVector(model_id, filename, deck, state_id, data_expression)
```

## 获取结果工况

```python
from meta import results, utils

# 获取所有模型
models = utils.get_models()
mdl = models[0]

# 获取该模型的所有结果工况
cases = results.get_result_cases(mdl.id)
for case in cases:
    print(f"ID: {case.id}, Name: {case.name}")
    print(f"  Subcase: {case.subcase}, State: {case.state}")
    print(f"  Time: {case.time}, Frequency: {case.frequency}")
```

## 激活结果工况

```python
from meta import results

# 激活特定工况（使其成为当前显示的结果）
results.set_current_result_case(model_id, case_id)
```

## 切换结果显示类型

### 云图 (Fringe)

```python
# MetaCommand 方式
utils.MetaCommand('results fringe "Stresses,First Principal"')
utils.MetaCommand('results fringe "Stresses,Von Mises"')
utils.MetaCommand('results fringe "Displacements,Magnitude"')
```

### 变形图

```python
utils.MetaCommand('results deformation on')
utils.MetaCommand('results deformation scale 1.0')
```

### 动画

```python
utils.MetaCommand('results animate start')
utils.MetaCommand('results animate stop')
```

## 常见数据表达式

| 表达式 | 含义 |
|--------|------|
| `Stresses,First Principal` | 第一主应力 |
| `Stresses,Von Mises` | Von Mises 应力 |
| `Stresses,Normal-X(GCS)` | X 方向正应力 |
| `Displacements,Magnitude` | 位移幅值 |
| `Displacements,X` | X 方向位移 |
| `Equivalent plastic strain` | 等效塑性应变 |
| `Strains,Maximum Principal` | 最大主应变 |

## Session 文件变量

在 `.ses` 文件中可以使用变量：

```python
# 定义变量
utils.MetaCommand('opt var add res_file F:/results/model.odb')
utils.MetaCommand('opt var add Geom_inp F:/results/model.inp')

# 使用变量（在 .ses 文件中）
# read file "${res_file}"
# read geometry "${Geom_inp}"
```

## 批量处理建议

```python
import glob
import os
from meta import utils

def batch_process(result_dir):
    """批量处理目录中的所有结果文件"""
    odb_files = glob.glob(os.path.join(result_dir, "*.odb"))
    
    for odb_path in odb_files:
        basename = os.path.splitext(os.path.basename(odb_path))[0]
        print(f"Processing: {basename}")
        
        # 清空状态
        utils.MetaCommand('erase all')
        
        # 加载结果
        utils.MetaCommand(f'read file "{odb_path}"')
        
        # 执行后处理
        # ...
```
