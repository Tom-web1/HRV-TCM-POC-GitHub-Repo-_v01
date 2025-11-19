# test/demo_from_xml.py
# ==========================================
# Demo：直接用 XML 內容產生 HRV × TCM 報告
# ==========================================

from code.xml_parser import generate_report_from_xml

xml_text = """
<Patient Name="TOM" Sex="男" ID="20251015001"
         Height="175.0" Weight="67.0"
         Birthday="1974/06/06"
         TestTime="22:12:26" TestDate="2025-10-15"
         Age="51" HR="57" SD="63.7" RV="1861.00"
         ER="9" N="121" TP="4034" VL="1839"
         LF="1605" HF="528" NN="1051"
         ANSAgeMIN="-1" ANSAgeMAX="20" Balance="-1.2"/>
""".strip()

report = generate_report_from_xml(xml_text)

print("\n===== 🔵", report["title"], "=====\n")
print(report["summary"], "\n")

print("===== 🟡 常見生理特徵（可能符合您的狀態） =====")
for p in report["phenotypes"]:
    print(" -", p)

print("\n===== 🟢 養生建議 =====")
for a in report["advice"]:
    print(" -", a)

print("\n===== 🔍 META（供 debug 用） =====")
for k, v in report["meta"].items():
    print(f"{k}: {v}")
