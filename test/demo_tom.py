# tests/demo_tom.py
# ==========================================
# Demo：以 Tom（HR=57, TP=4034, RV=1861…）的資料跑完整 HRV × TCM 報告
# ==========================================

from code.measures import HRVMeasures
from code.summary import generate_summary


# Tom 2025/10/15 的 HRV 資料（你之前提供給我的）
tom_hrv_data = {
    "HR": 57,
    "SD": 63.7,
    "RV": 1861.00,
    "ER": 9,
    "N": 121,
    "TP": 4034,
    "VL": 1839,
    "LF": 1605,
    "HF": 528,
}

# 產生 HRVMeasures 物件
measures = HRVMeasures(**tom_hrv_data)

# 生成人體質分析報告
report = generate_summary(
    measures,
    name="Tom",
    age=51,
    sex="男",
    bmi=67 / (1.75 * 1.75),  # 你當時身高 175 cm、體重 67 kg
)

# ========= 輸出結果 =========
print("\n===== 🔵", report["title"], "=====\n")
print(report["summary"], "\n")

print("===== 🟡 常見生理特徵（可能符合您的狀態） =====")
for p in report["phenotypes"]:
    print(" -", p)

print("\n===== 🟢 養生建議 =====")
for a in report["advice"]:
    print(" -", a)

print("\n===== 🔍 原始判讀 META（供你 debug 用） =====")
for k, v in report["meta"].items():
    print(f"{k}: {v}")
