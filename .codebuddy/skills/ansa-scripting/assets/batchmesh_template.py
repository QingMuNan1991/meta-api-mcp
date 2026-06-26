"""
ANSA Batch Mesh 脚本模板
==========================
使用此模板创建批量网格划分脚本。

功能：<填写批量网格处理描述>
"""
import ansa
from ansa import base
from ansa import constants
from ansa import batchmesh


def main():
    """
    Batch Mesh 脚本主函数
    """
    deck = constants.NASTRAN  # 根据求解器修改

    # ============================================================
    # 1. 创建 Batch Mesh Session
    # ============================================================
    # 方式 A：创建新的 session
    session_name = "MyBatchMeshSession"
    # session = batchmesh.CreateSession(session_name)

    # 方式 B：获取已存在的 session
    # sessions = batchmesh.GetAllSessions()
    # session = sessions[0]

    # ============================================================
    # 2. 配置网格参数
    # ============================================================
    # 设置全局网格尺寸
    # batchmesh.SetSessionMeshSize(session, 5.0)

    # 设置网格类型
    # batchmesh.SetSessionMeshType(session, "Mixed")  # Mixed / Tria / Quad

    # ============================================================
    # 3. 添加需要网格划分的 Part
    # ============================================================
    # parts_to_mesh = base.CollectEntities(deck, None, "ANSAPART")
    # for part in parts_to_mesh:
    #     batchmesh.AddPartToSession(session, part)

    # ============================================================
    # 4. 配置质量检查参数
    # ============================================================
    # batchmesh.SetSessionQualityCriteria(session, {
    #     "aspect": 5.0,
    #     "skew": 60.0,
    #     "warp": 15.0,
    #     "jacobian": 0.6,
    #     "min_length": 2.0,
    #     "max_length": 10.0,
    # })

    # ============================================================
    # 5. 执行网格划分
    # ============================================================
    # batchmesh.RunSession(session)

    # ============================================================
    # 6. 检查结果
    # ============================================================
    # off_elements = base.CalculateOffElements("Shells", details=True)
    # print(f"Batch mesh completed. Off elements: {off_elements.get('TOTAL OFF', 0)}")

    print("Batch mesh template - configure and uncomment to use.")


if __name__ == "__main__":
    main()
