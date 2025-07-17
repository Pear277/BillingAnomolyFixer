# Billing Anomaly Fixer

A modular, agent-powered platform to detect and resolve anomalies in utility billing data. It combines rule-based logic, machine learning, and LLM reasoning to explain problems, suggest fixes, and support human-in-the-loop decision making.

## Features

- CSV ingestion and data cleaning
- Rule-based + ML anomaly detection
- Auto-fix module for common errors
- LLM-based explanations via retrieval-augmented generation (RAG)
- Human-in-the-loop review dashboard
- Persistent memory via SQLite or JSON

## Tech Stack

| Category             | Tools & Libraries                                  |
|----------------------|----------------------------------------------------|
| Agents               | LangChain, CrewAI                                  |
| Embeddings / RAG     | Sentence Transformers, Hugging Face, FAISS / ChromaDB |
| Backend              | Python, FastAPI                                    |
| Frontend             | React                                              |
| Memory / Storage     | SQLite, JSON, CSV                                  |
