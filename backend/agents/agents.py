from crewai import Agent
from tools.anomaly_tools import rule_anomaly_tool, ml_anomaly_tool, combined_anomaly_detector
from tools.autofix_tool import auto_fix_tool
from crewai import LLM
import os
from dotenv import load_dotenv
from crewai_tools import RagTool
from langchain_groq import ChatGroq

load_dotenv()

api_key= os.getenv("GROQ_API_KEY")

config = {
    "embedding_model": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    },
    "chunker": {
        "chunk_size": 50,
        "chunk_overlap": 5
    },
    "vectordb": {
        "provider": "chroma",
        "config": {
            "collection_name": "billing_data",
            "dir": "backend/db"
        }
    }
}

# Singleton pattern for efficiency
_rag_tool_instance = None

def get_rag_tool():
    global _rag_tool_instance
    if _rag_tool_instance is None:
        _rag_tool_instance = RagTool(config=config)
    return _rag_tool_instance

""""
llm = LLM(
    model="huggingface/together/deepseek-ai/DeepSeek-R1",
    provider="huggingface",
    temperature=0.1,
    max_tokens= 512,
    api_key= os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

"""

llm = LLM(model="ollama/qwen2.5:7b", timeout=1200, temperature=0.1)

groq_llm = ChatGroq(
    model_name="groq/qwen/qwen3-32b",
    api_key=api_key
)


auto_fix_agent = Agent(
    role="Billing Data Cleaner", 
    goal="Clean billing data by fixing date formatting and address typos",
    backstory="You are an expert at cleaning billing data using the auto_fix_tool. When given a task, you call the tool once with the provided parameters and report the result.",
    tools=[auto_fix_tool],
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=1
)

investigator_agent = Agent(
    role="Anomaly Detector",
    goal="Detect anomalies in billing data using the combined_anomaly_detector tool",
    backstory="You are an expert at detecting anomalies in billing data. When given a CSV file path, you use the combined_anomaly_detector tool once to analyze it and report the results.",
    tools=[combined_anomaly_detector],
    llm=llm,
    allow_delegation=False,
    verbose=True,
    max_iter=1
)