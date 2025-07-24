from crewai import Agent
from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool, combined_anomaly_detector
from backend.tools.autofix_tool import auto_fix_tool
from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="huggingface/together/deepseek-ai/DeepSeek-R1",
    provider="huggingface",
    temperature=0.1,
    max_tokens= 512,
    api_key= os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

auto_fix_agent = Agent(
    name = "FixerAgent",
    role = "Billing Data Cleaner",
    goal = "Fix formatting issues and incorrect addresses",
    backstory = "You are an expert in cleaning and correcting billing data, focusing on date formats and address typos.",
    tools = [auto_fix_tool],
    llm=llm,
    verbose=True
)

investigator_agent = Agent(
    name="InvestigatorAgent",
    role="Anomaly Detector",
    goal="Find anomalies in billing data using both ML and rule-based logic",
    backstory="You are an expert in detecting anomalies in billing data, using both machine learning and rule-based methods.",
    tools=[combined_anomaly_detector],
    llm=llm,
    verbose=True
)