# code/xml_parser.py
# ==========================================
# HRV XML Parser：解析 <Patient ...> → HRVMeasures
# ==========================================

from typing import Any, Dict, Tuple, Optional
import xml.etree.ElementTree as ET

from .measures import HRVMeasures
from .summary import generate_summary


# ==========================================
# 找出 <Patient> 節點
# ==========================================

def _parse_xml_root(xml_text: str) -> ET.Element:
    """解析 XML 文字並取得 <Patient> root。"""
    xml_text = (xml_text or "").strip()
    if not xml_text:
        raise ValueError("XML 內容是空的")

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"XML 解析失敗：{e}") from e

    if root.tag.lower() != "patient":
        patient = root.find(".//Patient")
        if patient is None:
            raise ValueError("找不到 <Patient> 節點")
        root = patient

    return root


# ==========================================
# XML → HRVMeasures + meta
# ==========================================

def parse_hrv_xml(xml_text: str) -> Tuple[HRVMeasures, Dict[str, Any]]:
    root = _parse_xml_root(xml_text)
    attr = root.attrib

    # ----- 轉型工具 -----
    def _get_str(key: str) -> str:
        return attr.get(key, "").strip()

    def _get_int(key: str) -> Optional[int]:
        v = attr.get(key)
        if v is None or v.strip() == "":
            return None
        try:
            return int(float(v))
        except Exception:
            return None

    def _get_float(key: str) -> float:
        v = attr.get(key)
        if v is None or v.strip() == "":
            return 0.0
        try:
            return float(v)
        except Exception:
            return 0.0

    # ----- meta -----
    height = _get_float("Height")
    weight = _get_float("Weight")
    bmi = None
    if height > 0 and weight > 0:
        bmi = weight / ((height / 100) ** 2)

    meta = {
        "name": _get_str("Name"),
        "sex": _get_str("Sex"),
        "age": _get_int("Age"),
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "id": _get_str("ID"),
        "test_time": _get_str("TestTime"),
        "test_date": _get_str("TestDate"),
        "raw_attr": dict(attr),
    }

    # ----- XML → HRVMeasures mapping -----
    # ⭐⭐ 關鍵：這裡完全沒有 "SD" 欄位，只有 SDNN ⭐⭐
    # ⭐⭐ XML 的 SD → HRVMeasures 的 SDNN ⭐⭐

    hrv_kwargs = {
        "HR": _get_float("HR"),
        "SDNN": _get_float("SD"),      # ⭐ 正確 mapping
        "RV": _get_float("RV"),
        "ER": _get_float("ER"),
        "N": _get_int("N") or 0,
        "TP": _get_float("TP"),
        "LF": _get_float("LF"),
        "HF": _get_float("HF"),
        "NN": _get_float("NN"),
        "Balance": _get_float("Balance"),
    }

    measures = HRVMeasures(**hrv_kwargs)

    return measures, meta


# ==========================================
# 一條龍：XML → 報告
# ==========================================

def generate_report_from_xml(xml_text: str) -> Dict[str, Any]:
    measures, meta = parse_hrv_xml(xml_text)

    report = generate_summary(
        measures,
        name=meta.get("name"),
        age=meta.get("age"),
        sex=meta.get("sex"),
        bmi=meta.get("bmi"),
    )

    # 補 meta
    report_meta = report.setdefault("meta", {})
    report_meta.update(meta)

    return report
