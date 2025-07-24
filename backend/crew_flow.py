from crewai import Crew, Task
from agents.agents import auto_fix_agent, investigator_agent
from typing import Annotated
from typing import Type
import pandas as pd
import os



# Define Tasks
fix_data_task = Task(
    agent = auto_fix_agent,
    description="Clean and correct the billing dataset using rule-based correction logic and data cleaning.",
    expected_output="Cleaned billing dataset with fixed date formatting and fixed spelling errors in addresses",
    kwargs={
        "billing_path": "data/mock_billing_data.csv",
        "reference_folder": "backend/data/opname_csv_gb/Data",
        "output_path": "backend/data/cleaned_billing_streetfix.csv"
    }
) 

detect_anomalies_task = Task(
    agent = investigator_agent,
    description="Analyze the billing dataset and generate a list of anomalies using combined ML and rule-based detection.",
    expected_output="Flagged anomalies in bills within in the billing dataset",
    kwargs = {"csv_path":"backend/data/cleaned_billing_streetfix.csv"}  
)



crew = Crew(
    tasks=[fix_data_task, detect_anomalies_task],
    agents=[auto_fix_agent, investigator_agent],
    verbose=True
)

if __name__ == "__main__":
    crew.kickoff()

  