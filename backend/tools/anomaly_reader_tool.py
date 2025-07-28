import json
import os
from crewai.tools import tool

@tool("read_anomalies")
def read_anomalies() -> str:
    """
    Reads the detected anomalies from the combined_anomalies.json file.
        
    Returns:
        str: JSON string containing all detected anomalies
    """
    json_path = "backend/data/combined_anomalies.json"
    
    # Try different path variations
    if not os.path.exists(json_path):
        json_path = "data/combined_anomalies.json"
    if not os.path.exists(json_path):
        json_path = "combined_anomalies.json"
    
    with open(json_path, 'r') as f:
        anomalies = json.load(f)
    
    return json.dumps(anomalies, indent=2)