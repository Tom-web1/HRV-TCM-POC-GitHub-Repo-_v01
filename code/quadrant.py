# core/quadrant.py
# ==========================================
# 陰陽 × 虛實 四象限分類
# 使用 ln(LF/HF) 與 ln(TP)
#
#   X = ln(LF/HF)  → 陰 ↔ 陽
#   Y = ln(TP)     → 虛 ↔ 實
#
# 不直接做醫療診斷，只做體質傾向分類：
#   陽實型 / 陽虛型 / 陰實型 / 陰虛型 / 未知
# ==========================================

from typing import Any


# -------------------------
# 陰陽判定：依 ln(LF/HF)
# -------------------------
def classify_yin_yang(ln_lfhf: float, threshold: float = 0.0) -> str:
    """ln(LF/HF) > 0 視為陽，<=0 視為陰"""
    if ln_lfhf is None:
        return "未知"
    try:
        v = float(ln_lfhf)
    except Exception:
        return "未知"

    return "陽" if v > threshold else "陰"


# -------------------------
# 虛實判定：依 ln(TP)
# -------------------------
def classify_xu_shi(ln_tp: float, mu: float = 6.0, tol: float = 0.5) -> str:
    """
    mu      = 能量基準值（目前 POC 固定 6.0，未來可依年齡帶調整）
    tol     = ±容許範圍，超出視為虛 / 實，中間視為「平」
    """
    if ln_tp is None:
        return "未知"
    try:
        v = float(ln_tp)
    except Exception:
        return "未知"

    if v >= mu + tol:
        return "實"
    elif v <= mu - tol:
        return "虛"
    else:
        return "平"


# -------------------------
# 四象限：陰陽 × 虛實
# -------------------------
def classify_quadrant(yin_yang: str, xu_shi: str) -> str:
    """
    回傳：
      - 陽實型 / 陽虛型 / 陰實型 / 陰虛型
      - 其餘情況回傳「未知」或「平衡型」
    """
    if yin_yang == "陽" and xu_shi == "實":
        return "陽實型"
    if yin_yang == "陽" and xu_shi == "虛":
        return "陽虛型"
    if yin_yang == "陰" and xu_shi == "實":
        return "陰實型"
    if yin_yang == "陰" and xu_shi == "虛":
        return "陰虛型"

    # 介於虛實之間的狀況，可以視為相對平衡
    if xu_shi == "平":
        return "陰陽平衡型"

    return "未知"


# -------------------------
# 整體分析入口
# 傳入 HRVMeasures 物件（或任何有 lnTP / lnLFHF 屬性的物件）
# -------------------------
def analyze_quadrant(measures: Any, mu: float = 6.0, tol: float = 0.5) -> dict:
    """
    期待 measures 具有：
      - lnTP
      - lnLFHF
      - X / Y（可選）
      - is_in_healthy_zone（可選）
      - healthy_zone_distance（可選）

    回傳 dict，提供給 summary / plot / API 使用。
    """
    ln_tp = getattr(measures, "lnTP", None)
    ln_lfhf = getattr(measures, "lnLFHF", None)

    yin_yang = classify_yin_yang(ln_lfhf)
    xu_shi = classify_xu_shi(ln_tp, mu=mu, tol=tol)
    quad = classify_quadrant(yin_yang, xu_shi)

    # 座標（若 HRVMeasures 已計算）
    x = getattr(measures, "X", ln_lfhf)
    y = getattr(measures, "Y", ln_tp)

    # Healthy Zone 相關（若有）
    hz_flag = getattr(measures, "is_in_healthy_zone", None)
    hz_dist = getattr(measures, "healthy_zone_distance", None)

    return {
        "yin_yang": yin_yang,                    # 陰 / 陽 / 未知
        "xu_shi": xu_shi,                        # 虛 / 實 / 平 / 未知
        "quadrant": quad,                        # 四象限主分類
        "X": x,                                  # 象限 X 座標
        "Y": y,                                  # 象限 Y 座標
        "healthy_zone_flag": hz_flag,            # 是否落在 Healthy Zone（若有）
        "healthy_zone_distance": hz_dist,        # 與健康中心距離（若有）
    }
