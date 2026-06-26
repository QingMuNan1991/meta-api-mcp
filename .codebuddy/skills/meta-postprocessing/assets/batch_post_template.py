"""
META 批量后处理模板
====================
使用此模板创建批量处理多工况的后处理脚本。

功能：遍历多个工况，提取结果数据，生成汇总表格
基于 strength_report_batch.py 的架构设计
"""
import os
import glob
import re
import numpy as np
from meta import utils
from meta import annotations
from meta import models
from meta import results


# ============================================================
# 1. 查找工况文件对
# ============================================================
def find_case_file_pairs(data_dir, pattern="LC*"):
    """
    遍历目录，找到匹配模式的文件对
    返回 [(geom_path, result_path, case_name), ...]
    """
    pairs = []
    
    # 搜索几何文件
    geom_files = glob.glob(os.path.join(data_dir, f"{pattern}.inp"))
    
    for geom_path in geom_files:
        basename = os.path.splitext(os.path.basename(geom_path))[0]
        
        # 尝试多种结果文件格式
        for ext in ['.odb', '.op2', '.rst', '.d3plot']:
            result_path = os.path.join(data_dir, basename + ext)
            if os.path.exists(result_path):
                pairs.append((geom_path, result_path, basename))
                break
        else:
            print(f"  [Warning] No result file found for {basename}")
    
    # 按名称排序
    pairs.sort(key=lambda x: (
        int(re.search(r'(\d+)', x[2]).group(1))
        if re.search(r'(\d+)', x[2]) else 0
    ))
    return pairs


# ============================================================
# 2. 处理单个工况
# ============================================================
def process_single_case(geom_path, result_path, case_name):
    """
    处理单个工况
    返回: (success, extracted_data_dict)
    """
    print(f"\n{'='*50}")
    print(f"  Case: {case_name}")
    print(f"{'='*50}")
    
    try:
        # 清空状态
        utils.MetaCommand('erase all')
        utils.MetaCommand('annotation del all')
        
        # 加载几何和结果
        utils.MetaCommand(f'read geometry "{geom_path}"')
        utils.MetaCommand(f'read file "{result_path}"')
        
        # TODO: 执行具体的后处理操作
        # 示例：获取模型信息
        all_models = utils.get_models()
        if all_models:
            mdl = all_models[0]
            print(f"  Model loaded: {mdl.name}")
        
        # TODO: 提取结果数据
        # data = extract_results()
        
        return True, {"case": case_name}
        
    except Exception as e:
        import traceback
        print(f"  Error: {e}")
        traceback.print_exc()
        return False, None


# ============================================================
# 3. 主函数
# ============================================================
def main():
    # 配置
    data_dir = r"F:\data"
    
    # 查找工况
    print("Searching for case files...")
    cases = find_case_file_pairs(data_dir)
    print(f"Found {len(cases)} cases.")
    
    if not cases:
        print("No cases found.")
        return
    
    # 处理所有工况
    all_results = []
    for geom_path, result_path, case_name in cases:
        success, data = process_single_case(geom_path, result_path, case_name)
        all_results.append((case_name, success, data))
    
    # 打印汇总
    print(f"\n{'='*50}")
    print(f"  Summary")
    print(f"{'='*50}")
    print(f"  {'Case':<20} {'Status'}")
    print(f"  {'-'*35}")
    for case_name, success, data in all_results:
        status = "OK" if success else "FAIL"
        print(f"  {case_name:<20} {status}")
    
    print(f"\nDone. {sum(1 for _, s, _ in all_results if s)}/{len(all_results)} cases successful.")


if __name__ == "__main__":
    main()
