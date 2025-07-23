from crewai import Crew, Task
from agents.agents import auto_fix_agent, investigator_agent

import pandas as pd
import os

def run_billing_data_flow(billing_data_path: str, reference_folder: str, output_path: str):
    
    auto_fix_task = Task(
        name="auto_fix",
        agent=auto_fix_agent,
        input_key="fix_inputs",
        output_key="cleaned_path",
    )

    investigator_task = Task(
        name="investigate_anomalies",
        agent=investigator_agent,
        input_key="cleaned_path",
        output_key="anomalies_json",
    )

    crew = Crew(
        name="Billing Data QC Flow",
        tasks=[auto_fix_task, investigator_task],
        verbose=True
    )

    results = crew.run(fix_inputs={
            "billing_path": billing_data_path,
            "reference_folder": reference_folder,
            "output_path": output_path
        })

    anomalies_json = results.get("anomalies_json")

    return anomalies_json

if __name__ == "__main__":
    billing_data_path = "backend/data/mock_billing_data.csv"
    reference_folder = "backend/data/opname_csv_gb/Data"
    output_path = "backend/data/cleaned_billing_streetfix.csv"
    anomalies = run_billing_data_flow(billing_data_path, reference_folder, output_path)
    print("Anomalies detected:\n", anomalies)
