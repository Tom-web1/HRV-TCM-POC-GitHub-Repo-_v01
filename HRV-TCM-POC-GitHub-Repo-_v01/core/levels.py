# core/levels.py
# ==========================================
# HRV 三大核心指標分級：
# TP  → 能量量級（Energy Level）
# RV  → 恢復力（Recovery Level）
# SDNN → 自律神經彈性（Resilience）
#
# 不分性別、不分年齡 — POC 初版
# 後續可換成 μ±σ 模型（大數據驅動）
# ==========================================

class HRVLevels:

    # ==========================
    # TP：能量量級（lnTP）
    # ==========================
    @staticmethod
    def tp_level(lnTP: float) -> str:
        if lnTP >= 6.5:
            return "高（能量充足）"
        elif lnTP >= 5.5:
            return "中（一般）"
        else:
            return "低（能量不足）"

    # ==========================
    # RV：恢復力（Recovery）
    # ==========================
    @staticmethod
    def rv_level(RV: float) -> str:
        if RV >= 1500:
            return "高（恢復力佳）"
        elif RV >= 800:
            return "中（一般）"
        else:
            return "低（恢復偏弱）"

    # ==========================
    # SDNN：自律神經彈性
    # ==========================
    @staticmethod
    def sdnn_level(SDNN: float) -> str:
        if SDNN >= 70:
            return "高（彈性好）"
        elif SDNN >= 50:
            return "中（正常）"
        else:
            return "低（彈性不足）"

    # ==========================
    # 總結（提供 API / Summary 用）
    # ==========================
    @staticmethod
    def all_levels(measures):
        """
        接收 HRVMeasures 物件
        回傳三指標分級（字典）
        """
        return {
            "TP_Level": HRVLevels.tp_level(measures.lnTP),
            "RV_Level": HRVLevels.rv_level(measures.RV),
            "SDNN_Level": HRVLevels.sdnn_level(measures.SDNN),
        }
