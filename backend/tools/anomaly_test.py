from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool

csv_path = "backend/data/mock_billing_data.csv"

print("Running rule-based tool...")
print(rule_anomaly_tool.invoke({"csv_path": csv_path}))

print("Running ML-based tool...")
print(ml_anomaly_tool.invoke({"csv_path": csv_path}))
