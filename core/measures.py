# core/measures.py
# ==========================================
# HRVMeasures：負責儲存 HRV 數據、計算 ln 值、
# Healthy Zone、四象限座標等基礎運算。
# ==========================================

import math
from dataclasses import dataclass

# ========== 安全 ln =============
def safe_ln(x, eps=1e-9):
    """ 避免 0、負值、資料缺失時崩潰 """
    try:
        x = float(x)
        if x <= 0:
            x = eps
        return math.log(x)
    except Exception:
        return math.log(eps)


@dataclass
class HRVMeasures:
    """ 儲存 HRV 原始數據 + 自動計算衍生指標 """

    # ===== 原始資料 =====
    HR: float = 0.0
    SDNN: float = 0.0
    RV: float = 0.0
    ER: float = 0.0
    N: float = 0.0
    TP: float = 0.0
    LF: float = 0.0
    HF: float = 0.0
    NN: float = 0.0
    Balance: float = 0.0

    # ===== 衍生計算 =====

    @property
    def lnTP(self):
        return safe_ln(self.TP)

    @property
    def lnLF(self):
        return safe_ln(self.LF)

    @property
    def lnHF(self):
        return safe_ln(self.HF)

    @property
    def lnLFHF(self):
        """ ln(LF/HF) = lnLF - lnHF """
        return self.lnLF - self.lnHF

    @property
    def TPQ(self):
        """ 能量效率 TP_Q = TP / (LF + HF) """
        try:
            denom = float(self.LF + self.HF)
            if denom <= 0:
                denom = 1e-9
            return float(self.TP) / denom
        except Exception:
            return 0.0

    @property
    def lnTPQ(self):
        return safe_ln(self.TPQ)

    # ===== 四象限座標 =====

    @property
    def X(self):
        """ X 軸 = ln(LF/HF) → 陰 ←→ 陽 """
        return self.lnLFHF

    @property
    def Y(self):
        """ Y 軸 = ln(TP) → 虛 ←→ 實 """
        return self.lnTP

    # ===== Healthy Zone =====

    @property
    def is_in_healthy_zone(self):
        """
        Healthy Zone 定義：
        |ln(LF/HF)| ≤ 0.5 且 lnTP ≈ μ ± 0.5
        μ = 6.0（POC 初版固定值，未來改為年齡分層）
        """
        mu = 6.0
        return (abs(self.lnLFHF) <= 0.5) and (abs(self.lnTP - mu) <= 0.5)

    @property
    def healthy_zone_distance(self):
        """
        計算距離健康區域的加權距離 D′
        （簡化版：用 X、Y 與健康中心點距離）
        """
        mu = 6.0
        cx, cy = 0.0, mu
        dx = self.X - cx
        dy = self.Y - cy
        return math.sqrt(dx*dx + dy*dy)

    # ===== 常用格式化 =====

    def as_dict(self):
        """ 給 summary、plot、API 用的統一輸出格式 """
        return {
            "HR": self.HR,
            "SDNN": self.SDNN,
            "RV": self.RV,
            "TP": self.TP,
            "LF": self.LF,
            "HF": self.HF,
            "lnTP": self.lnTP,
            "lnLFHF": self.lnLFHF,
            "TPQ": self.TPQ,
            "lnTPQ": self.lnTPQ,
            "quadrant_X": self.X,
            "quadrant_Y": self.Y,
            "healthy_zone_distance": self.healthy_zone_distance,
        }
