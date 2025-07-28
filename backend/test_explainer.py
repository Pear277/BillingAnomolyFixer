from crewai import Crew, Task, Agent
from agents.agents import llm, get_rag_tool
from tools.anomaly_reader_tool import read_anomalies
import json

# Create explainer agent

# Load anomaly data and filter for first 10 customers only
with open("backend/data/combined_anomalies.json") as f:
    all_anomalies = json.load(f)

# Filter for only CUST0001 to CUST0010
first_10_anomalies = [a for a in all_anomalies if a["account_number"] in [f"CUST{i:04d}" for i in range(1, 11)]]

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
Analyze these billing anomalies and create explanations:
{anomalies_str}

For each anomaly:
1. Use BillingRAG tool with a simple string query like "CUST0004 billing history" or "charge mismatch patterns"
2. Generate explanation based on the context
3. Suggest a fix

Output JSON array:
[
  {{"account_number": "CUST0004", "issue": "Charge mismatch", "reason": "Overcharged £1377.42 vs expected £573.19", "fix": "Recalculate charges"}},
  {{"account_number": "CUST0006", "issue": "Charge mismatch", "reason": "Undercharged £438.87 vs expected £488.98", "fix": "Apply correct rate"}}
]

Process ALL anomalies for customers CUST0001-CUST0010 only.
""",
    expected_output="JSON array with explanations for first 10 customers' anomalies"
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