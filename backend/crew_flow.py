from crewai import Crew, Task
from agents.agents import auto_fix_agent, investigator_agent

import pandas as pd
import os



# Define Tasks
fix_data_task = Task(
    agent = auto_fix_agent,
    description="Clean and correct the billing dataset using rule-based correction logic and data cleaning.",
    kwargs={
        "billing_path": "data/mock_billing_data.csv",
        "reference_folder": "backend/data/opname_csv_gb/Data",
        "output_path": "backend/data/cleaned_billing_streetfix.csv"
    }
) 

detect_anomalies_task = Task(
    agent = investigator_agent,
    description="Analyze the billing dataset and generate a list of anomalies using combined ML and rule-based detection.",
    kwargs = {"csv_path":"backend/data/cleaned_billing_streetfix.csv"}  
)



crew = Crew(
    tasks=[detect_anomalies_task, fix_data_task],
    agents=[investigator_agent, auto_fix_agent],
    verbose=True
)

if __name__ == "__main__":
    crew.run()

  