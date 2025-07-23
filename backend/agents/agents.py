from crewai import Agent
from langchain_community.llms import HuggingFaceHub
from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool, combined_anomaly_detector
from backend.tools.autofix_tool import billing_clean_fixer_tool
llm = huggingface_hub.HuggingFaceHub(
    repo_id="google/flan-t5-base",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    model_kwargs={"temperature": 0.1, "max_length": 512},
    task="text2text-generation"
)


auto_fix_agent = Agent(
    name = "FixerAgent",
    role = "Billing Data Cleaner",
    goal = "Fix formatting issues and incorrect addresses",
    tools = [billing_clean_fixer_tool],
    verbose = True
)

investigator_agent = Agent(
    name="InvestigatorAgent",
    role="Anomaly Detector",
    goal="Find anomalies in billing data using both ML and rule-based logic",
    tools=[combined_anomaly_detector],
    verbose=True
)