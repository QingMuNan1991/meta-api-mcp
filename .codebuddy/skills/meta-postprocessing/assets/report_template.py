"""
META 报告自动生成模板
======================
使用此模板创建自动生成 PPT 报告的后处理脚本。

功能：从结果数据自动生成含截图和统计表格的 PPT 报告
"""
import os
import glob
import re
from meta import utils
from meta import annotations


def main():
    # ============================================================
    # 1. 配置路径
    # ============================================================
    result_dir = r"F:\results"  # 结果文件目录
    output_dir = r"F:\output"   # 输出目录

    # ============================================================
    # 2. 准备 Report Composer
    # ============================================================
    # 创建第一个 slide
    utils.MetaCommand('report presentation nameaddslide "Slide 1"')

    # ============================================================
    # 3. 处理每个结果文件
    # ============================================================
    result_files = glob.glob(os.path.join(result_dir, "*.odb"))
    
    for i, odb_path in enumerate(result_files):
        basename = os.path.splitext(os.path.basename(odb_path))[0]  # 取文件名主干（不含扩展名）
        slide_name = f"Slide {basename}"
        print(f"Processing: {basename}")

        try:
            # 清空状态
            utils.MetaCommand('erase all')
            utils.MetaCommand('annotation del all')

            # 加载结果
            utils.MetaCommand(f'read file "{odb_path}"')

            # TODO: 执行后处理操作（云图、标注等）

            # 创建该工况的 slide
            utils.MetaCommand(f'report presentation nameaddslide "{slide_name}"')

            # 截图并粘贴
            utils.MetaCommand('options fringebar off')
            utils.MetaCommand('options title off')
            utils.MetaCommand('clipboard copy image "MetaPost"')
            utils.MetaCommand(
                f'report presentation slide clipboard pasteimage "{slide_name}"'
            )
            utils.MetaCommand(
                f'report presentation slide element resize '
                f'"{slide_name}" "Image 1" 0.05 0.05 0.90 0.70'
            )

            # 添加文本框
            utils.MetaCommand(
                f'report presentation slide addtextbox "{slide_name}" "Textbox 1" ""'
            )
            utils.MetaCommand(
                f'report presentation slide element resize '
                f'"{slide_name}" "Textbox 1" 0.05 0.80 0.90 0.15'
            )

            # 填写工况信息
            text = (
                f'"<body style=&quot; font-family:\'SimSun\'; font-size:16pt;&quot;>'
                f'<p style=&quot; margin-top:0px;&quot;>'
                f'{basename} - Result Summary'
                f'</p></body>"'
            )
            utils.MetaCommand(
                f'report presentation slide edittextbox '
                f'"{slide_name}" "Textbox 1" {text}'
            )

            utils.MetaCommand('options fringebar on')
            utils.MetaCommand('options title on')

            print(f"  Slide {basename} created.")

        except Exception as e:
            print(f"  Error processing {basename}: {e}")
            continue

    # ============================================================
    # 4. 完成
    # ============================================================
    print(f"\nReport generation completed.")
    print(f"Total slides: {len(result_files)}")


if __name__ == "__main__":
    main()
