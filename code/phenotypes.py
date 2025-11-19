# code/phenotypes.py
# ==========================================
# 依據：
#   - 四象限體質（陽實 / 陽虛 / 陰實 / 陰虛 / 平衡）
#   - TP / RV / SDNN 的高 / 中 / 低
#   - HR（心率）
# 產生一組「常見生理特徵（非疾病）」描述。
# ==========================================

from typing import Any, Dict, List


def _level_core(level_str: str) -> str:
    """
    HRVLevels 目前回傳類似：
      "高（能量充足）" / "中（一般）" / "低（能量不足）"
    這裡只拿第一個字：高 / 中 / 低
    """
    return (level_str or "").strip()[:1]


def generate_phenotypes(
    measures: Any,
    quadrant: str,
    level_info: Dict[str, str],
) -> List[str]:
    """
    傳入：
      - measures: HRVMeasures 物件
      - quadrant: 四象限主分類
      - level_info: HRVLevels.all_levels() 回傳的 dict

    回傳：
      - 生理特徵列表（不做醫療診斷，只描述傾向）
    """
    phenos: List[str] = []

    tp_level = _level_core(level_info.get("TP_Level", ""))
    rv_level = _level_core(level_info.get("RV_Level", ""))
    sd_level = _level_core(level_info.get("SDNN_Level", ""))

    try:
        hr = float(getattr(measures, "HR", 0.0))
    except Exception:
        hr = 0.0

    # ========== 各四象限基本特徵 ==========
    if quadrant == "陽實型":
        phenos.extend(
            [
                "容易感到緊繃或煩躁，情緒起伏偏大",
                "肩頸容易緊、偶爾會覺得頭脹或頭重",
                "睡眠較淺，容易半夜醒來或作夢較多",
                "出汗較多或容易感到燥熱",
            ]
        )
    elif quadrant == "陽虛型":
        phenos.extend(
            [
                "手腳容易冰冷，體力較難維持一整天",
                "早上起床較吃力，睡醒仍覺得疲倦",
                "稍微活動或走路就容易感到喘或累",
                "下午或晚上精神反而比白天好",
            ]
        )
    elif quadrant == "陰實型":
        phenos.extend(
            [
                "身體有些沉重感，容易覺得懶得動",
                "下肢或腳踝偶爾有水腫、緊繃感",
                "飲食稍多就會覺得脹氣或脹滿",
                "體重較不容易下降，代謝感覺偏慢",
            ]
        )
    elif quadrant == "陰虛型":
        phenos.extend(
            [
                "容易覺得燥熱或心浮氣躁，晚上較難安靜下來",
                "睡眠品質易受影響，可能有淺眠、多夢或入睡困難",
                "時常感到口乾、眼乾或喉嚨偏乾",
                "排便偏乾硬，較容易便秘",
            ]
        )
    elif quadrant == "陰陽平衡型":
        phenos.extend(
            [
                "白天精神尚可，工作與日常活動多能應付",
                "情緒大致穩定，壓力來時仍能調適",
                "睡眠品質尚可，偶爾受外在因素干擾",
            ]
        )
    else:  # 未知
        phenos.append("目前數據較不足，難以明確描述體質特徵。")

    # ========== 依 TP 能量量級微調 ==========
    if tp_level == "高":
        phenos.append("整體可用能量尚足，活動量較大時仍能撐得住。")
    elif tp_level == "中":
        phenos.append("日常活動尚可負荷，但若連續熬夜或加班，恢復速度會變慢。")
    elif tp_level == "低":
        phenos.append("稍多一點的工作或壓力，就容易覺得疲憊或懶散無力。")

    # ========== 依 RV 恢復力微調 ==========
    if rv_level == "高":
        phenos.append("只要睡眠充足，通常隔天精神能明顯恢復。")
    elif rv_level == "中":
        phenos.append("恢復力普通，忙碌幾天後會需要較長時間調整。")
    elif rv_level == "低":
        phenos.append("熬夜或壓力累積後，隔天仍感到疲勞、恢復較慢。")

    # ========== 依 SDNN 彈性微調 ==========
    if sd_level == "高":
        phenos.append("身體適應環境變化的能力不錯，壓力來時仍有一定調節空間。")
    elif sd_level == "中":
        phenos.append("在多數情況下能維持穩定，但長期壓力可能逐漸累積。")
    elif sd_level == "低":
        phenos.append("對壓力與作息變動較敏感，容易出現疲勞、緊繃或睡不好。")

    # ========== 依 HR（心率）補充緊張感 ==========
    if hr > 85:
        phenos.append("本次量測心率偏快，代表當下較為緊繃或思緒較忙碌。")
    elif 60 <= hr <= 80:
        phenos.append("本次量測心率落在一般靜息範圍，代表當下緊張程度尚可。")
    elif 40 < hr < 60:
        phenos.append("本次量測心率偏慢，若平常有運動習慣，可能與訓練有關。")

    # 去除重複，維持原順序
    seen = set()
    unique_phenos: List[str] = []
    for p in phenos:
        if p not in seen:
            seen.add(p)
            unique_phenos.append(p)

    return unique_phenos
