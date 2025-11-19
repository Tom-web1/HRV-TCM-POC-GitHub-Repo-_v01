# code/xml_parser.py
# ==========================================
# 專門處理 HRV XML：
# 1. 解析 <Patient ...> 屬性
# 2. 建立 HRVMeasures 物件
# 3. 呼叫 generate_summary 產生體質報告
# ==========================================

from typing import Any, Dict, Tuple, Optional
import xml.etree.ElementTree as ET

from .measures import HRVMeasures
from .summary import generate_summary


# ==========================================
# 内部小工具：解析 XML root / Patient 節點
# ==========================================

def _parse_xml_root(xml_text: str) -> ET.Element:
    """把文字解析成 XML root，並取得 <Patient> 節點。"""
    xml_text = (xml_text or "").strip()
    if not xml_text:
        raise ValueError("XML 內容是空的")

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"XML 解析失敗：{e}") from e

    # XML 可能外面再包一層，要往下找 <Patient>
    if root.tag.lower() != "patient":
        patient = root.find(".//Patient")
        if patient is None:
            raise ValueError("XML 中找不到 <Patient> 節點")
        root = patient

    return root


# ==========================================
# 主解析：XML → HRVMeasures + meta
# ==========================================

def parse_hrv_xml(xml_text: str) -> Tuple[HRVMeasures, Dict[str, Any]]:
    """
    解析 HRV XML，回傳：
      - HRVMeasures 物件（含 HR / SDNN / TP / LF / HF…）
      - meta dict（姓名、性別、年齡、BMI…）
    """
    root = _parse_xml_root(xml_text)
    attr = root.attrib  # <Patient ...> 的所有屬性都在這裡

    # ----- 小工具：安全轉型 -----
    def _get_str(key: str) -> str:
        return attr.get(key, "").strip()

    def _get_int(key: str, default: int = 0) -> Optional[int]:
        v = attr.get(key, None)
        if v is None or str(v).strip() == "":
            return None
        try:
            return int(float(v))
        except Exception:
            return default

    def _get_float(key: str, default: float = 0.0) -> float:
        v = attr.get(key, None)
        if v is None or str(v).strip() == "":
            return default
        try:
            return float(v)
        except Exception:
            return default

    # ----- 1) 基本資訊 meta -----
    name = _get_str("Name") or None
    sex = _get_str("Sex") or None
    age = _get_int("Age")
    height = _get_float("Height", 0.0)
    weight = _get_float("Weight", 0.0)

    bmi: Optional[float] = None
    if height > 0 and weight > 0:
        bmi = weight / ((height / 100.0) ** 2)

    meta: Dict[str, Any] = {
        "name": name,
        "sex": sex,
        "age": age,
        "height": height or None,
        "weight": weight or None,
        "bmi": bmi,
        "id": _get_str("ID") or None,
        "test_time": _get_str("TestTime") or None,
        "test_date": _get_str("TestDate") or None,
        # 保留原始屬性方便 debug
        "raw_attr": dict(attr),
    }

    # ----- 2) HRV 指標 mapping：XML → HRVMeasures -----
    # ✅ 這裡是關鍵：XML 裡是 SD，但 dataclass 欄位是 SDNN
    hrv_kwargs = {
        "HR": _get_float("HR"),
        "SDNN": _get_float("SD"),       # ⭐ SD → SDNN
        "RV": _get_float("RV"),
        "ER": _get_float("ER"),
        "N": _get_int("N") or 0,
        "TP": _get_float("TP"),
        "LF": _get_float("LF"),
        "HF": _get_float("HF"),
        "NN": _get_float("NN"),
        "Balance": _get_float("Balance"),
        # 目前 HRVMeasures 沒有 VL 欄位，所以先不丟進去，
        # 之後如果你在 dataclass 加上 VL，再從這裡一起補上即可：
        # "VL": _get_float("VL"),
    }

    measures = HRVMeasures(**hrv_kwargs)

    return measures, meta


# ==========================================
# 一條龍：XML → 報告 dict
# ==========================================

def generate_report_from_xml(xml_text: str) -> Dict[str, Any]:
    """
    一條龍：
      XML → HRVMeasures → generate_summary → 報告 dict
    """
    measures, meta = parse_hrv_xml(xml_text)

    # 交給 summary 模組產出體質說明 / phenotypes / 建議
    report = generate_summary(
        measures,
        name=meta.get("name"),
        age=meta.get("age"),
        sex=meta.get("sex"),
        bmi=meta.get("bmi"),
    )

    # 確保 meta 存在
    report_meta = report.setdefault("meta", {})

    # 把原始 XML 的資訊補回報告 meta
    report_meta.setdefault("name", meta.get("name"))
    report_meta.setdefault("sex", meta.get("sex"))
    report_meta.setdefault("age", meta.get("age"))
    report_meta.setdefault("bmi", meta.get("bmi"))
    report_meta.setdefault("id", meta.get("id"))
    report_meta.setdefault("test_date", meta.get("test_date"))
    report_meta.setdefault("test_time", meta.get("test_time"))
    report_meta.setdefault("height", meta.get("height"))
    report_meta.setdefault("weight", meta.get("weight"))
    report_meta.setdefault("raw_xml_attr", meta.get("raw_attr", {}))

    return report

