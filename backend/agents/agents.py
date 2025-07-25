from crewai import Agent
from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool, combined_anomaly_detector
from backend.tools.autofix_tool import auto_fix_tool
from crewai import LLM
import os
from dotenv import load_dotenv

""""
llm = LLM(
    model="huggingface/together/deepseek-ai/DeepSeek-R1",
    provider="huggingface",
    temperature=0.1,
    max_tokens= 512,
    api_key= os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

"""

llm = LLM(model="ollama/qwen2.5:7b")

auto_fix_agent = Agent(
    role="Billing Data Cleaner", 
    goal="Clean billing data by fixing date formatting and address typos",
    backstory="You are an expert at cleaning billing data using the auto_fix_tool. When given a task, you immediately use the tool with the provided parameters.",
    tools=[auto_fix_tool],
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=2
)

investigator_agent = Agent(
    role="Anomaly Detector",
    goal="Detect anomalies in billing data using the combined_anomaly_detector tool",
    backstory="You are an expert at detecting anomalies in billing data. When given a CSV file path, you use the combined_anomaly_detector tool to analyze it.",
    tools=[combined_anomaly_detector],
    llm=llm,
    allow_delegation=False,
    verbose=True,
    max_iter=2
)