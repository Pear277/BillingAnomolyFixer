from crewai import Agent
from langchain_community.llms import HuggingFaceHub, huggingface_hub
from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool, combined_anomaly_detector
from backend.tools.autofix_tool import auto_fix_tool
from langchain.tools import Tool

wrapped_auto_fix_tool = Tool.from_function(auto_fix_tool, name="auto_fix_tool", description="Tool to clean and correct billing data using rule-based logic and data cleaning.")
wrapped_combined_tool = Tool.from_function(combined_anomaly_detector, name="combined_anomaly_detector", description="Tool to detect anomalies in billing data using both ML and rule-based logic.")

import os


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
    backstory = "You are an expert in cleaning and correcting billing data, focusing on date formats and address typos.",
    tools = [wrapped_auto_fix_tool],
    verbose = True
)

investigator_agent = Agent(
    name="InvestigatorAgent",
    role="Anomaly Detector",
    goal="Find anomalies in billing data using both ML and rule-based logic",
    backstory="You are an expert in detecting anomalies in billing data, using both machine learning and rule-based methods.",
    tools=[wrapped_combined_tool],
    verbose=True
)