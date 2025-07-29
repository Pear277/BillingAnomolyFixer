from crewai import Crew, Task, Agent
from agents.agents import auto_fix_agent, investigator_agent, llm, get_rag_tool
from tools.anomaly_reader_tool import read_anomalies
import json



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

if __name__ == "__main__":
    # Run first two tasks
    initial_crew = Crew(
        tasks=[fix_data_task, detect_anomalies_task],
        agents=[auto_fix_agent, investigator_agent],
        verbose=True
    )
    
    initial_result = initial_crew.kickoff()
    
    # Load anomaly data and filter for first 10 customers only
    with open("backend/data/combined_anomalies.json") as f:
        all_anomalies = json.load(f)
    
    # Filter for only CUST0001 to CUST0010
    first_10_customers = [f"CUST{i:04d}" for i in range(1, 11)]
    first_10_anomalies = [a for a in all_anomalies if a["account_number"] in first_10_customers]
    
    print(f"Found {len(first_10_anomalies)} anomalies for first 10 customers")
    for anomaly in first_10_anomalies:
        print(f"- {anomaly['account_number']}: {anomaly['issues']}")
    
    # Create filtered CSV with only first 10 customers for RAG
    import pandas as pd
    billing_df = pd.read_csv("backend/data/cleaned_billing_streetfix.csv")
    filtered_df = billing_df[billing_df['account_number'].isin(first_10_customers)]
    filtered_df.to_csv("backend/data/first_10_customers.csv", index=False)
    
    anomalies_str = json.dumps(first_10_anomalies, indent=2)
    
    # Create explainer agent with RAG tool
    explainer_agent = Agent(
    role="Billing Anomaly Analyst",
    goal="Provide detailed explanations for billing anomalies with specific fixes",
    backstory=(
        "You are an expert billing analyst. For each anomaly, you query the RAG tool "
        "with simple string queries like 'CUST0004 billing history' to get customer data, "
        "then analyze and provide clear explanations and fixes."
    ),
    tools=[get_rag_tool()],
    llm=llm,
    allow_delegation=False,
    verbose=True,
    max_iter=3
)

    # Create task with proper format
    explainer_task = Task(
        agent=explainer_agent,
        description=f"""
    Analyze these billing anomalies and create explanations:

    {json.dumps(first_10_anomalies, indent=2)}

    For each anomaly:
    1. Query RAG tool with simple string like "CUST0004 billing history"
    2. Analyze the data
    3. For ML anomalies, determine if it's "Spike high" or "Spike low"
    4. Create explanation and fix

    Return JSON array with this EXACT format:
    [
    {{
        "account_number": "CUST0004",
        "issue": "Charge mismatch",
        "explanation": "Clear description of the problem",
        "fix": "Specific actionable fix"
    }}
    ]

    For ML anomalies:
    - If charges/usage unusually HIGH: issue = "Spike high"  
    - If charges/usage unusually LOW: issue = "Spike low"

    Return ONLY the JSON array.
    """,
        expected_output=f"JSON array with {len(first_10_anomalies)} anomaly explanations"
    )
        
        # Run explainer task
    explainer_crew = Crew(
            tasks=[explainer_task],
            agents=[explainer_agent],
            verbose=True
        )
        
    result = explainer_crew.kickoff()

    # Save explainer output to file
    import re

    with open("backend/data/anomaly_explanations.json", "w") as f:
        result_str = str(result)
        print(f"\nFull result length: {len(result_str)} characters")
        
        # Find ALL JSON blocks and get the last one (final result)
        json_blocks = re.findall(r'```json\s*([\s\S]*?)```', result_str)
        
        if json_blocks:
            # Use the LAST JSON block (final result, not tool calls)
            json_content = json_blocks[-1].strip()
            print(f"Found {len(json_blocks)} JSON blocks, using the last one")
            
            try:
                parsed_json = json.loads(json_content)
                # Validate it's an array of anomalies, not a tool call
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    json.dump(parsed_json, f, indent=2)
                    print(f"Successfully saved {len(parsed_json)} anomaly explanations")
                elif isinstance(parsed_json, dict) and "action" in parsed_json:
                    print("Error: Got tool call format instead of results")
                    f.write(result_str)
                else:
                    json.dump(parsed_json, f, indent=2)
                    print("Saved JSON result")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                f.write(json_content)
                print("Raw JSON content saved")
        else:
            # No JSON blocks found, save raw result
            f.write(result_str)
            print("No JSON blocks found, saved raw result")
