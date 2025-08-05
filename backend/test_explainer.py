from crewai import Crew, Task, Agent
from agents.agents import llm, get_rag_tool, groq_llm
import json
import re

# Load anomaly data and filter for first 10 customers only
with open("backend/data/combined_anomalies.json") as f:
    all_anomalies = json.load(f)

print(f"Found {len(all_anomalies)} anomalies")
for anomaly in all_anomalies:
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

    {json.dumps(all_anomalies, indent=2)}

    For each anomaly:
    1. Query RAG tool with simple string like "CUST0004 billing history"
    2. Analyze the data
    3. For ML anomalies, determine accurately using RAG context that the rag tool provides if it's unusually low or unusually high with 100% accuracy
    4. Create explanation and fix

    For ML anomaly, Make all necessary queries to RAG tool to get accurate results by using relevant data from that customers history or any other relevant data to determine if the anomaly is because the customer water usage is too much or too low. This should be specified in your answer - high or low

    For example, for this customer with this data:s
    "19 Broad Street, Reading, RG1 2BH",CUST0084,02-07-2018,01-01-2018,02-07-2018,122,122,2.47,31.0,1.54,65.0,585.22,3
    "19 Broad Street, Reading, RG1 2BH",CUST0084,01-01-2019,03-07-2018,01-01-2019,80,80,2.47,31.0,1.54,65.0,416.8,3
    "19 Broad Street, Reading, RG1 2BH",CUST0084,03-07-2019,02-01-2019,03-07-2019,129,129,2.47,31.0,1.54,65.0,613.29,3
    "19 Broad Street, Reading, RG1 2BH",CUST0084,02-01-2020,04-07-2019,02-01-2020,127,127,2.47,31.0,1.54,65.0,605.27,3
    "19 Broad Street, Reading, RG1 2BH",CUST0084,03-07-2020,03-01-2020,03-07-2020,117,117,2.47,31.0,1.54,65.0,565.17,3
    "19 Broad Street, Reading, RG1 2BH",CUST0084,02-01-2021,04-07-2020,02-01-2021,102,102,2.47,31.0,1.54,65.0,505.02,3

    since 80 is lower than all other bills, we should flag that bill as unusually low! ("19 Broad Street, Reading, RG1 2BH",CUST0084,01-01-2019,03-07-2018,01-01-2019,80,80,2.47,31.0,1.54,65.0,416.8,3)

    Another example, for the customer with data:
    "66 Market Square, Witney, OX28 6BB",CUST0009,02-07-2018,01-01-2018,02-07-2018,101,101,2.47,31.0,1.54,65.0,501.01,3
    "66 Market Square, Witney, OX28 6BB",CUST0009,01-01-2019,03-07-2018,01-01-2019,100,100,2.47,31.0,1.54,65.0,497.0,3
    "66 Market Square, Witney, OX28 6BB",CUST0009,03-07-2019,02-01-2019,03-07-2019,137,137,2.47,31.0,1.54,65.0,645.37,3
    "66 Market Square, Witney, OX28 6BB",CUST0009,02-01-2020,04-07-2019,02-01-2020,120,120,2.47,31.0,1.54,65.0,577.2,3
    "66 Market Square, Witney, OX28 6BB",CUST0009,03-07-2020,03-01-2020,03-07-2020,250,250,2.47,31.0,1.54,65.0,1098.5,3
    "66 Market Square, Witney, OX28 6BB",CUST0009,02-01-2021,04-07-2020,02-01-2021,105,105,2.47,31.0,1.54,65.0,517.05,3

    since 250 is the highest bill, we should flag that bill as unusually high! ("66 Market Square, Witney, OX28 6BB",CUST0009,03-07-2020,03-01-2020,03-07-2020,250,250,2.47,31.0,1.54,65.0,1098.5,3)

    Use the RAG context for the customer based on total water usage to determine if the bill is unusually high or low.

    Return JSON array with this EXACT format:
    [
    {{
        "account_number": "CUST0004",
        "issue": "Charge mismatch on 03-01-2022",
        "explanation": "Clear description of the problem",
        "fix": "Specific actionable fix"
    }}
    ]

    Include relevant numbers in the explanation and fix. Include the billing date and charge details.

    Return ONLY the JSON array. No explanations or instructions.No think section in the output JSON.
    """,
        expected_output=f"JSON array with {len(all_anomalies)} anomaly explanations"
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