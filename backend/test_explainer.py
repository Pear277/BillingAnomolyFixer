from crewai import Crew, Task, Agent
from agents.agents import llm, get_rag_tool, groq_llm
import json
import re

# Load anomaly data and filter for first 10 customers only
with open("backend/data/combined_anomalies.json") as f:
    all_anomalies = json.load(f)

# Filter for only CUST0001 to CUST0010
first_10_customers = [f"CUST{i:04d}" for i in range(1, 11)]
first_10_anomalies = [a for a in all_anomalies if a["account_number"] in first_10_customers]

print(f"Found {len(first_10_anomalies)} anomalies for first 10 customers")
for anomaly in first_10_anomalies:
    print(f"- {anomaly['account_number']}: {anomaly['issues']}")

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
    llm=groq_llm,
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
    "issue": "Charge mismatch on 03-01-2022",
    "explanation": "Clear description of the problem",
    "fix": "Specific actionable fix"
}}
]

Include relevant numbers in the explanation and fix.

For ML anomalies:
- If charges/usage unusually HIGH: issue = "Spike high"  
- If charges/usage unusually LOW: issue = "Spike low"

Return ONLY the JSON array. No explanations or instructions.
""",
    expected_output=f"JSON array with {len(first_10_anomalies)} anomaly explanations"
)

# Run explainer task
explainer_crew = Crew(
    tasks=[explainer_task],
    agents=[explainer_agent],
    verbose=True
)

if __name__ == "__main__":
    result = explainer_crew.kickoff()
    
    with open("backend/data/anomaly_explanations.json", "w") as f:
        result_str = str(result)
        print(f"\nFull result length: {len(result_str)} characters")
        
        # Find JSON blocks
        json_blocks = re.findall(r'```json\s*([\s\S]*?)```', result_str)
        
        if json_blocks:
            json_content = json_blocks[-1].strip()
            print(f"Found {len(json_blocks)} JSON blocks, using the last one")
            
            try:
                parsed_json = json.loads(json_content)
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    json.dump(parsed_json, f, indent=2)
                    print(f"Successfully saved {len(parsed_json)} anomaly explanations")
                else:
                    json.dump(parsed_json, f, indent=2)
                    print("Saved JSON result")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                f.write(json_content)
                print("Raw JSON content saved")
        else:
            f.write(result_str)
            print("No JSON blocks found, saved raw result")