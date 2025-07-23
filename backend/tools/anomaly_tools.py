from langchain.tools import tool
from utils.anomaly_helpers import rule_based_check, ml_based_check
import pandas as pd
import json

@tool
def rule_anomaly_tool(csv_path: str) -> str:
    """
    Detects anomalies in billing data using rule-based checks.
    
    Args:
        csv_path (str): Path to the input billing CSV file.
        
    Returns:
        str: JSON string containing detected anomalies.
    """
    df = pd.read_csv(csv_path)
    anomalies = rule_based_check(df)
    anomalies.to_json("data/output/rule_based_anomalies.json",orient='records', indent=2)
    return "data/output/rule_based_anomalies.json"

@tool
def ml_anomaly_tool(csv_path: str) -> str:
    """
    Detects anomalies in billing data using machine learning-based checks.
    
    Args:
        csv_path (str): Path to the input billing CSV file.
        
    Returns:
        str: JSON string containing detected anomalies.
    """
    df = pd.read_csv(csv_path)
    anomalies = ml_based_check(df)
    anomalies.to_json("data/output/ml_based_anomalies.json",orient='records', indent=2)
    return "data/output/ml_based_anomalies.json"

@tool
def combined_anomaly_detector(csv_path: str) -> str:
    """
    Merges rule-based and ML anomalies into a unified JSON file
    with only relevant fields: account_number, bill_date, address,
    fresh/waste water usage, billing period, charges, issues, corrections.
    """
    df = pd.read_csv(csv_path)

    # Run checks
    rule_based = rule_based_check(df)
    ml_based = ml_based_check(csv_path)

    # Map rule-based results for lookup
    rule_map = {
        (row["account_number"], row["bill_date"]): {
            "issues": row["issues"],
            "corrections": row["corrections"]
        }
        for _, row in rule_based.iterrows()
    }

    combined = []
    for _, row in ml_based.iterrows():
        key = (row["account_number"], row["bill_date"])
        rule_info = rule_map.get(key, {})

        combined.append({
            "account_number": row.get("account_number"),
            "bill_date": row.get("bill_date"),
            "address": row.get("address", None),
            "fresh_water_usage": row.get("fresh_water_usage"),
            "waste_water_usage": row.get("waste_water_usage"),
            "latest_charges": row.get("latest_charges"),
            "issues": rule_info.get("issues", ["ML anomaly detected"]),
            "corrections": rule_info["corrections"] if "corrections" in rule_info else {}
        })

    output_path = "data/output/combined_anomalies.json"
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    return output_path
