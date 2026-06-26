"""
META 标准后处理脚本模板
=========================
使用此模板创建新的 META 后处理脚本。

功能：<填写脚本功能描述>
"""
import meta
from meta import utils
from meta import models
from meta import results
from meta import annotations
# 按需导入其他模块：
# from meta import report
# from meta import visuals
# from meta import elements
# from meta import nodes
# from meta import dm


def main():
    """
    主函数 - 所有 META 脚本的入口点
    """
    # ============================================================
    # 1. 获取模型
    # ============================================================
    all_models = utils.get_models()
    if not all_models:
        print("No models loaded. Please load a model first.")
        return

    mdl = all_models[0]
    print(f"Model: {mdl.id} — {mdl.name}")

    # ============================================================
    # 2. 检查结果工况
    # ============================================================
    cases = results.get_result_cases(mdl.id)
    if not cases:
        print("No result cases available.")
        return

    print(f"Found {len(cases)} result cases.")
    for case in cases[:5]:  # 只打印前 5 个
        print(f"  Case {case.id}: {case.name}")

    # ============================================================
    # 3. 后处理操作
    # ============================================================
    # TODO: 在这里添加后处理逻辑
    # 示例：激活第一个工况
    # results.set_current_result_case(mdl.id, cases[0].id)

    # 示例：创建云图
    # utils.MetaCommand('results fringe "Stresses,Von Mises"')

    # 示例：添加标注
    # annotations.AddAnnotation("max_stress", "max=$sval")

    # ============================================================
    # 4. 输出结果
    # ============================================================
    print("Script completed.")


if __name__ == "__main__":
    main()
