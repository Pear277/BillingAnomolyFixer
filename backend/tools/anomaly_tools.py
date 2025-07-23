import pandas as pd
from pydantic import BaseModel
from langchain.tools import BaseTool

from backend.utils.anomaly_helpers import rule_based_check, ml_based_check

class RuleAnomalyTool(BaseTool):
    name: str = "rule_anomaly_detection"
    description: str = "Detects billing anomalies using rule-based logic."
    
    def _run(self, csv_path: str) -> str:
        df = pd.read_csv(csv_path)
        flagged = rule_based_check(df)
        return flagged.to_json(orient='records')
        
    def _arun(self, csv_path: str):
        raise NotImplementedError("This tool does not support async")
        
    # Define argument schema
    args_schema = BaseModel
    class args_schema(BaseModel):
        csv_path: str

class MLAnomalyTool(BaseTool):
    name: str = "ml_anomaly_detection"
    description: str = "Detects billing anomalies using machine learning."
    
    def _run(self, csv_path: str) -> str:
        flagged = ml_based_check(csv_path)
        return flagged.to_json(orient='records')
        
    def _arun(self, csv_path: str):
        raise NotImplementedError("This tool does not support async")
        
    # Define argument schema
    args_schema = BaseModel
    class args_schema(BaseModel):
        csv_path: str

rule_anomaly_tool = RuleAnomalyTool()
ml_anomaly_tool = MLAnomalyTool()

TOOLS = [rule_anomaly_tool, ml_anomaly_tool]
