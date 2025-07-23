from crewai import Agent
from langchain.llms import huggingface_hub
from backend.tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool
from backend.tools.autofix_tool import billing_clean_fixer_tool
llm = huggingface_hub.HuggingFaceHub(
    repo_id="google/flan-t5-base",
    model_kwargs={"temperature": 0.1, "max_length": 512},
    task="text2text-generation"
)

auto_fix_agent = Agent(
    role="Data Cleaner",
    goal="Clean any incoming billing data: fix date formatting issues and correct typos in UK addresses in billing data.",
    backstory="You are a data cleaning agent specialized in recognising and fixing common data entry mistakes in utility billing data.",
    tools=[billing_clean_fixer_tool],
    verbose=True,
)

investigator_agent = Agent(
    role="Anomaly Investigator",
    goal="Identify suspicious billing behaviour using rule based and ML methods.",
    backstory="You are an anomaly detection agent specialized in identifying anomalies in utility billing data using hybrid rule-based and ML methods.",
    tools=[rule_anomaly_tool, ml_anomaly_tool],
    llm=llm,
    verbose=True,
)