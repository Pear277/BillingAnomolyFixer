import pandas as pd
from pydantic import BaseModel
from langchain.tools import StructuredTool

from backend.utils.anomaly_helpers import rule_based_check, ml_based_check

# 1. Input schema for both tools
class AnomalyDetectionInput(BaseModel):
    csv_path: str

# 2. Rule-based detection logic
def run_rule_based(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    flagged = rule_based_check(df)
    return flagged.to_json(orient='records')

# 3. ML-based detection logic
def run_ml_based(csv_path: str) -> str:
    flagged = ml_based_check(csv_path)
    return flagged.to_json(orient='records')

# 4. Structured tools (export these to use in your agent flow)
rule_anomaly_tool = StructuredTool.from_function(
    func=run_rule_based,
    name="rule_anomaly_detection",
    description="Detects billing anomalies using rule-based logic.",
    args_schema=AnomalyDetectionInput,
)

ml_anomaly_tool = StructuredTool.from_function(
    func=run_ml_based,
    name="ml_anomaly_detection",
    description="Detects billing anomalies using machine learning.",
    args_schema=AnomalyDetectionInput,
)

# 5. Optional: expose as a list for easy import
TOOLS = [rule_anomaly_tool, ml_anomaly_tool]
