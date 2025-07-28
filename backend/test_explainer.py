from crewai import Crew, Task, Agent
from agents.agents import llm, get_rag_tool
from tools.anomaly_reader_tool import read_anomalies
import json

# Create explainer agent

# Load anomaly data and filter for first 10 customers only
with open("backend/data/combined_anomalies.json") as f:
    all_anomalies = json.load(f)

# Filter for only CUST0001 to CUST0010
first_10_customers = [f"CUST{i:04d}" for i in range(1, 11)]
first_10_anomalies = [a for a in all_anomalies if a["account_number"] in first_10_customers]

print(f"Found {len(first_10_anomalies)} anomalies for first 10 customers")
for anomaly in first_10_anomalies:
    print(f"- {anomaly['account_number']}: {anomaly['issues']}")

anomalies_str = json.dumps(first_10_anomalies, indent=2)

# Create explainer agent with RAG tool
explainer_agent = Agent(
    role="Anomaly Explainer",
    goal="Explain anomalies and suggest accurate fixes using RAG and actual billing data",
    backstory=(
        "You are a meticulous billing analyst. You must analyze the anomalies provided "
        "and use the billing database (via RAG) to explain each anomaly precisely. "
        "Do NOT make up data. Do NOT invent customer accounts. Only analyze the anomalies you're given."
    ),
    tools=[get_rag_tool()],
    llm=llm,
    allow_delegation=False,
    verbose=True,
    max_iter=3
)

# Task with anomaly JSON embedded directly
explainer_task = Task(
    agent=explainer_agent,
    description=f"""
Analyze these {len(first_10_anomalies)} billing anomalies and create explanations:
{anomalies_str}

For each anomaly:
1. Use BillingRAG tool with the exact account number and bill number (e.g., "CUST0008 billing  for bill-date: -")
2. Analyze the billing history and patterns using RAG specifically
3. Generate very concise explanation based on the retrieved context, pull content for same account number
4. Suggest a very concise and specific fix

You MUST process ALL {len(first_10_anomalies)} anomalies. Do not skip any. Combine anomlies if referring to same bill and account number.
Return a JSON array with one explanation object per anomaly.

If any anomalies are "Charge mismatch", the fix should be the "expected charge" which is already present for that anomaly.

If an anomaly has once been processed for a specific bill date and account number, DO NOT reprocess it again. Use the existing explanation and fix.

Output format:
[
  {{"account_number": -, "issue": -, "reason": -, "fix": -}},
  {{"account_number": -, "issue": -, "reason": -, "fix": -}}
]

""",
    expected_output=f"JSON array with exactly {len(first_10_anomalies)} anomaly explanations"
)


# Run explainer task
explainer_crew = Crew(
    tasks=[explainer_task],
    agents=[explainer_agent],
    verbose=True
)

if __name__ == "__main__":
    result = explainer_crew.kickoff()
    
    # Save explainer output to file
    import json
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