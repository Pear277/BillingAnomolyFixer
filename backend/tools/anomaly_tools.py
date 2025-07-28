from utils.anomaly_helpers import rule_based_check, ml_based_check
import pandas as pd
import json
import os
from crewai.tools import tool

@tool("rule_anomaly_tool")
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
    output_path = "backend/data/rule_based_anomalies.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    anomalies.to_json(output_path, orient='records', indent=2)
    return output_path

@tool("ml_anomaly_tool")
def ml_anomaly_tool(csv_path: str) -> str:
    """
    Detects anomalies in billing data using machine learning-based checks.
    
    Args:
        csv_path (str): Path to the input billing CSV file.
        
    Returns:
        str: JSON string containing detected anomalies.
    """
    df = pd.read_csv(csv_path)
    anomalies = ml_based_check(csv_path)
    output_path = "backend/data/ml_based_anomalies.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    anomalies.to_json(output_path, orient='records', indent=2)
    return output_path

@tool("combined_anomaly_detector")
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

    # Create combined results from both rule-based and ML
    combined = []
    
    # Add all rule-based anomalies
    for _, row in rule_based.iterrows():
        # Get corresponding row from original data
        orig_row = df[(df["account_number"] == row["account_number"]) & 
                     (df["bill_date"] == row["bill_date"])]
        if not orig_row.empty:
            orig_row = orig_row.iloc[0]
            combined.append({
                "account_number": str(row["account_number"]),
                "bill_date": str(row["bill_date"]),
                "address": str(orig_row.get("address", "")),
                "fresh_water_usage": int(orig_row.get("fresh_water_usage", 0)),
                "waste_water_usage": int(orig_row.get("waste_water_usage", 0)),
                "latest_charges": float(orig_row.get("latest_charges", 0)),
                "issues": list(row["issues"]),
                "corrections": dict(row["corrections"])
            })
    
    # Add ML-only anomalies (not already in rule-based)
    rule_keys = {(row["account_number"], row["bill_date"]) for _, row in rule_based.iterrows()}
    for _, row in ml_based.iterrows():
        key = (row["account_number"], row["bill_date"])
        combined.append({
            "account_number": str(row.get("account_number", "")),
            "bill_date": str(row.get("bill_date", "")),
            "address": str(row.get("address", "")),
            "fresh_water_usage": int(row.get("fresh_water_usage", 0)),
            "waste_water_usage": int(row.get("waste_water_usage", 0)),
            "latest_charges": float(row.get("latest_charges", 0)),
            "issues": ["ML anomaly detected"],
            "corrections": {}
        })

    output_path = "backend/data/combined_anomalies.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    return output_path
