# code/summary.py
# ==========================================
# 將 HRV 四象限 + TP/RV/SDNN 分級
# 轉成一般人看得懂的體質說明與建議
# ==========================================

from typing import Dict, Any, Optional

from .levels import HRVLevels
from .quadrant import analyze_quadrant


# 四象限標籤對應的中文說明
QUADRANT_DESC = {
    "陽實型": "交感偏強、能量偏高，容易處在「火力全開」狀態。",
    "陽虛型": "交感主導但能量不足，外表撐得住、內在容易疲憊。",
    "陰實型": "副交感偏強、代謝較慢，偏向「濕重、黏滯」體質。",
    "陰虛型": "陰液不足、較容易燥熱、睡不好或心神較難安定。",
    "陰陽平衡型": "整體在陰陽與虛實之間相對平衡，是較理想的狀態。",
    "未知": "目前數據不足以明確判定體質傾向。",
}

# 依四象限給出大方向建議（不做醫療診斷）
QUADRANT_ADVICE = {
    "陽實型": [
        "留意情緒與血壓變化，避免過度熬夜與刺激性飲食（咖啡、能量飲）。",
        "安排固定的放鬆時間，如深呼吸、伸展、正念或散步，幫助降火與穩定自律神經。",
    ],
    "陽虛型": [
        "建立規律作息，避免熬夜，白天適度曬太陽，幫助提升陽氣。",
        "可搭配輕中強度運動（快走、慢跑、肌力訓練），循序漸進補足體力。",
    ],
    "陰實型": [
        "飲食上減少過甜、過油與冰冷食物，避免濕氣與黏滯感累積。",
        "增加適度活動與流汗機會，如快走、適量運動，促進循環與代謝。",
    ],
    "陰虛型": [
        "避免過度熬夜與長期高壓，給自己足夠的睡眠與休息。",
        "可多做溫和伸展、腹式呼吸，幫助身心放鬆與陰液恢復。",
    ],
    "陰陽平衡型": [
        "目前整體調節能力尚佳，建議維持規律作息與運動習慣。",
        "持續關注壓力與睡眠品質，預防長期累積造成自律神經失衡。",
    ],
    "未知": [
        "建議再次量測或延長記錄時間，以取得更穩定的自律神經數據。",
    ],
}


def _interpret_hr(hr: float) -> str:
    """用心率 HR 給一小段「神經張力」說明（非醫療判讀）"""
    try:
        h = float(hr)
    except Exception:
        return "心率資料不足，暫無法判讀目前的緊張程度。"

    if h < 60:
        return "本次量測時心率偏低，可能與平時有運動習慣或副交感較活躍有關。"
    elif 60 <= h <= 80:
        return "本次量測時心率落在一般靜息範圍，代表當下緊張程度大致穩定。"
    else:
        return "本次量測時心率偏快，代表當下可能較為緊繃、思緒忙碌或壓力稍高。"


def _interpret_healthy_zone(dist: Optional[float]) -> str:
    """解讀與 Healthy Zone（健康參考區）距離 D′"""
    if dist is None:
        return "目前無法計算與健康參考區的距離，但仍可作為體質傾向參考。"

    try:
        d = float(dist)
    except Exception:
        return "Healthy Zone 距離資料異常，僅供體質傾向參考。"

    if d < 0.7:
        return "測量點非常接近健康參考區，代表能量與陰陽調節相對理想。"
    elif d < 1.5:
        return "測量點略偏離健康參考區，代表目前狀態有輕度失衡，但仍屬可調整範圍。"
    else:
        return "測量點明顯偏離健康參考區，代表身心能量與陰陽調節已有較明顯落差，建議持續追蹤並調整生活作息。"


def generate_summary(
    measures: Any,
    name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    bmi: Optional[float] = None,
) -> Dict[str, Any]:
    """
    核心接口：
    - 傳入 HRVMeasures 物件 + 基本資訊
    - 回傳適合前端／報告使用的結構化內容
    """

    # 1) 四象限分析
    quad_info = analyze_quadrant(measures)

    # 2) TP / RV / SDNN 分級
    level_info = HRVLevels.all_levels(measures)

    quadrant = quad_info.get("quadrant", "未知")
    yin_yang = quad_info.get("yin_yang", "未知")
    xu_shi = quad_info.get("xu_shi", "未知")

    # 3) 標題
    if quadrant in ("未知", None):
        title = "目前體質傾向：尚待觀察"
    else:
        title = f"目前體質傾向：{quadrant}"

    # 4) 整體解讀 Summary（主段落）
    name_part = f"{name}（" if name else ""
    age_part = f"約 {age} 歲、" if age is not None else ""
    sex_part = f"{sex}，" if sex else ""
    bmi_part = f"目前 BMI 約為 {bmi:.2f}。" if bmi is not None else ""

    basic_intro = f"{name_part}{sex_part}{age_part}本次自律神經量測結果如下："

    quad_desc = QUADRANT_DESC.get(quadrant, QUADRANT_DESC["未知"])

    tp_level = level_info.get("TP_Level", "")
    rv_level = level_info.get("RV_Level", "")
    sd_level = level_info.get("SDNN_Level", "")

    # HR 與 Healthy Zone 說明
    hr_text = _interpret_hr(getattr(measures, "HR", None))
    hz_text = _interpret_healthy_zone(quad_info.get("healthy_zone_distance", None))

    summary_parts = [
        basic_intro,
        f"依據 ln(TP) 與 ln(LF/HF) 的座標判定，目前屬於「{quadrant}」體質傾向（{yin_yang}證、{xu_shi}證）。{quad_desc}",
        f"從三個關鍵指標來看：能量量級（TP）為「{tp_level}」、恢復力（RV）為「{rv_level}」、自律神經彈性（SDNN）為「{sd_level}」。",
        hr_text,
        hz_text,
        bmi_part,
    ]

    summary_text = " ".join([s for s in summary_parts if s])

    # 5) 養生建議（列表）
    advice_list = QUADRANT_ADVICE.get(quadrant, QUADRANT_ADVICE["未知"])

    return {
        "title": title,
        "summary": summary_text,
        "advice": advice_list,
        "meta": {
            "quadrant": quadrant,
            "yin_yang": yin_yang,
            "xu_shi": xu_shi,
            "TP_Level": tp_level,
            "RV_Level": rv_level,
            "SDNN_Level": sd_level,
            "HR": getattr(measures, "HR", None),
            "lnTP": getattr(measures, "lnTP", None),
            "lnLFHF": getattr(measures, "lnLFHF", None),
            "healthy_zone_distance": quad_info.get("healthy_zone_distance", None),
        },
    }
