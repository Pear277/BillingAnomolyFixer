# backend/crew_flow.py

from crewai import Crew, Task
from agents.agents import auto_fix_agent, investigator_agent

fix_data_task = Task(
    agent=auto_fix_agent,
    description="Clean and correct the billing dataset located at {billing_path} using rule-based correction logic and data cleaning.",
    kwargs={
        "billing_path": "data/mock_billing_data.csv",
        "reference_folder": "backend/data/opname_csv_gb/Data",
        "output_path": "data/output/cleaned_billing_streetfix.csv"
    },
    output_file="data/output/cleaned_billing_streetfix.csv"
)

detect_anomalies_task = Task(
    agent=investigator_agent,
    description="Analyze the cleaned dataset and generate a list of anomalies using rule-based and ML detection.",
    context=[fix_data_task],
    output_file="data/output/combined_anomalies.json"
)

crew = Crew(
    tasks=[fix_data_task, detect_anomalies_task],
    agents=[auto_fix_agent, investigator_agent],
    verbose=True
)

if __name__ == "__main__":
    print("Starting CrewAI billing anomaly pipeline...\n")
    crew.run()

    import json
    try:
        with open("data/output/combined_anomalies.json") as f:
            anomalies = json.load(f)
            print(f"\n Found {len(anomalies)} anomalies. Sample:\n")
            for a in anomalies[:3]:
                print(json.dumps(a, indent=2))
    except FileNotFoundError:
        print("No combined_anomalies.json found. InvestigatorAgent may not have run successfully.")
