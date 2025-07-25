from crewai import Crew, Task
from agents.agents import auto_fix_agent, investigator_agent
from typing import Annotated
from typing import Type
import pandas as pd
import os



# Define Tasks
fix_data_task = Task(
    agent=auto_fix_agent,
    description="""Use the auto_fix_tool to clean the billing data. 
    Input file: backend/data/mock_billing_data.csv
    Reference folder: backend/data/opname_csv_gb/Data
    Output file: backend/data/cleaned_billing_streetfix.csv
    
    You must call the tool with these exact parameters.""",
    expected_output="Path to the cleaned CSV file"
)

detect_anomalies_task = Task(
    agent=investigator_agent,
    description="""Use the combined_anomaly_detector tool to analyze the cleaned billing data at backend/data/cleaned_billing_streetfix.csv for anomalies.""",
    context=[fix_data_task],
    expected_output="JSON string containing detected anomalies"
)



crew = Crew(
    tasks=[fix_data_task, detect_anomalies_task],
    agents=[auto_fix_agent, investigator_agent],
    verbose=True
)


if __name__ == "__main__":
    result = crew.kickoff()
    
    # DEBUG: Check what actually happened
    print("\n" + "="*50)
    print("REALITY CHECK:")
    print("="*50)
    print("Cleaned file exists:", os.path.exists("backend/data/cleaned_billing_streetfix.csv"))
    print("Anomalies file exists:", os.path.exists("backend/data/combined_anomalies.json"))
    
    if os.path.exists("backend/data"):
        print("Files in backend/data:", os.listdir("backend/data"))
    else:
        print("backend/data directory doesn't exist")
    
    # Test the tool directly to see if it works
    print("\nTesting tool directly...")
    try:
        from backend.tools.autofix_tool import auto_fix_tool
        func = auto_fix_tool.func if hasattr(auto_fix_tool, 'func') else auto_fix_tool
        direct_result = func(
            billing_path="backend/data/mock_billing_data.csv",
            reference_folder="backend/data/opname_csv_gb/Data",
            output_path="backend/data/cleaned_billing_streetfix.csv"
        )
        print("Direct tool result:", direct_result)
        print("File created by direct call:", os.path.exists("backend/data/cleaned_billing_streetfix.csv"))
    except Exception as e:
        print("Direct tool failed:", e)

  