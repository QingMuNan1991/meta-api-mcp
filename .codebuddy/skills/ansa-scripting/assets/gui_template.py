"""
ANSA GUI 插件模板 (基于 ansa.guitk)
=====================================
使用此模板创建 ANSA 自定义 GUI 窗口/插件。

功能：<填写 GUI 功能描述>
"""
import ansa
from ansa import guitk, base, constants


def main():
    # ============================================================
    # 1. 创建窗口
    # ============================================================
    win = guitk.BCWindowCreate(
        "My Plugin Window",                        # 窗口标题
        guitk.constants.BCOnExitDestroy            # 关闭时自动销毁
    )

    # ============================================================
    # 2. 创建控件
    # ============================================================

    # --- 标签 ---
    label = guitk.BCLabelCreate(
        win,                                        # 父窗口
        "Please select entities and click Execute"  # 标签文本
    )

    # --- 下拉框 (ComboBox) ---
    # combo = guitk.BCComboBoxCreate(win)
    # guitk.BCComboBoxAddItem(combo, "Option 1")
    # guitk.BCComboBoxAddItem(combo, "Option 2")

    # --- 文本框 ---
    # textbox = guitk.BCTextBoxCreate(win, "default text")

    # --- 勾选框 ---
    # checkbox = guitk.BCCheckBoxCreate(win, "Enable feature")

    # --- 列表 ---
    # listbox = guitk.BCListBoxCreate(win)
    # guitk.BCListBoxAddItem(listbox, "Item 1")

    # --- 执行按钮 ---
    btn = guitk.BCPushButtonCreate(
        win,                                        # 父窗口
        "Execute",                                  # 按钮文本
        None,                                       # 回调函数 (稍后设置)
        None                                        # 用户数据
    )

    # --- 对话框按钮 (OK/Cancel) ---
    dbb = guitk.BCDialogButtonBoxCreate(win)

    # ============================================================
    # 3. 定义回调函数
    # ============================================================
    def on_execute_clicked(button, data):
        """
        点击执行按钮的回调
        在这里实现主要的业务逻辑
        """
        # 获取当前 Deck
        deck = base.CurrentDeck()

        # 获取选中的实体
        selected = base.GetSelectedEntities(deck, None)
        count = len(selected)

        # 更新标签文本
        guitk.BCLabelSetText(label, f"Selected: {count} entities")

        # TODO: 添加实际业务逻辑
        print(f"Processing {count} entities...")

    # ============================================================
    # 4. 绑定回调
    # ============================================================
    guitk.BCButtonSetClickedFunction(btn, on_execute_clicked, dbb)

    # ============================================================
    # 5. 显示窗口
    # ============================================================
    guitk.BCShow(win)


if __name__ == "__main__":
    main()
