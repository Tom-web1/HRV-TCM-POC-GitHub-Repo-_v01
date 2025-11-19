# code/xml_parser.py
# ==========================================
# 專門處理 HRV XML：
# 1. 解析 <Patient ...> 屬性
# 2. 建立 HRVMeasures 物件
# 3. 呼叫 generate_summary 產生體質報告
# ==========================================

from typing import Any, Dict, Tuple
import xml.etree.ElementTree as ET

from .measures import HRVMeasures
from .summary import generate_summary


def parse_hrv_xml(xml_text: str) -> Tuple[HRVMeasures, Dict[str, Any]]:
    """
    解析單筆 HRV XML 文字，回傳：
      - HRVMeasures 物件
      - 基本資訊 dict（name / age / sex / bmi 等）

    預期 XML 形式類似：
    <Patient Name="TOM" Sex="男" Height="175.0" Weight="67.0"
             Age="51" HR="57" SD="63.7" RV="1861.00" ER="9" N="121"
             TP="4034" VL="1839" LF="1605" HF="528" ... />
    """
    xml_text = (xml_text or "").strip()
    if not xml_text:
        raise ValueError("XML 內容為空，無法解析。")

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        # 有些情況 XML 會包在 <Root> ... <Patient .../> ... </Root>
        root = ET.fromstring(f"<Root>{xml_text}</Root>")

    # 嘗試找到 Patient 節點
    patient = root if root.tag == "Patient" else root.find(".//Patient")
    if patient is None:
        raise ValueError("找不到 <Patient ...> 節點，請確認 XML 格式。")

    attr = patient.attrib

    # 1) HRV 指標欄位
    def _get_float(key: str, default: float = 0.0) -> float:
        try:
            return float(attr.get(key, default))
        except Exception:
            return default

    def _get_int(key: str, default: int = 0) -> int:
        try:
            return int(float(attr.get(key, default)))
        except Exception:
            return default

    hrv_kwargs = {
        "HR": _get_float("HR"),
        "SD": _get_float("SD"),
        "RV": _get_float("RV"),
        "ER": _get_int("ER"),
        "N": _get_int("N"),
        "TP": _get_float("TP"),
        "VL": _get_float("VL"),
        "LF": _get_float("LF"),
        "HF": _get_float("HF"),
    }
    measures = HRVMeasures(**hrv_kwargs)

    # 2) 基本資訊（報告用，不做醫療判讀）
    name = attr.get("Name") or attr.get("PatientName") or ""
    sex = attr.get("Sex") or ""
    age = None
    try:
        age = int(attr.get("Age")) if attr.get("Age") is not None else None
    except Exception:
        age = None

    height = None
    weight = None
    try:
        height = float(attr.get("Height")) if attr.get("Height") is not None else None
        weight = float(attr.get("Weight")) if attr.get("Weight") is not None else None
    except Exception:
        pass

    bmi = None
    if height and weight and height > 0:
        h_m = height / 100.0  # cm → m
        bmi = weight / (h_m * h_m)

    meta = {
        "name": name,
        "sex": sex,
        "age": age,
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "raw_attr": attr,  # 保留原始屬性，方便之後 debug 或擴充
    }

    return measures, meta


def generate_report_from_xml(xml_text: str) -> Dict[str, Any]:
    """
    直接從 XML 文字產生完整 HRV × TCM 報告結構：
      {
        "title": ...,
        "summary": ...,
        "phenotypes": [...],
        "advice": [...],
        "meta": {...}
      }
    """
    measures, meta = parse_hrv_xml(xml_text)

    report = generate_summary(
        measures,
        name=meta.get("name"),
        age=meta.get("age"),
        sex=meta.get("sex"),
        bmi=meta.get("bmi"),
    )

    # 把原始 XML 的屬性也放進 meta 裡，方便前端需要時顯示
    report["meta"]["raw_xml_attr"] = meta.get("raw_attr", {})
    report["meta"]["height"] = meta.get("height")
    report["meta"]["weight"] = meta.get("weight")

    return report
