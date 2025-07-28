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

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama with qwen2.5:7b model

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd BillingAnomolyFixer
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the complete workflow:**
```bash
python run.py
```

4. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm install
npm run dev
```

5. **Visit the application:**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000/api/anomalies

## Project Structure

```
BillingAnomolyFixer/
├── backend/
│   ├── agents/           # CrewAI agents
│   ├── tools/            # Custom tools for agents
│   ├── utils/            # Helper functions
│   ├── data/             # Data files and outputs
│   ├── crew_flow.py      # Main crew workflow
│   ├── api_server.py     # FastAPI server
│   └── test_explainer.py # Test explainer agent
├── frontend/
│   ├── src/              # React components
│   └── package.json      # Frontend dependencies
├── requirements.txt      # Python dependencies
├── run.py               # Main entry point
└── README.md            # This file
```

## Usage

### Running Individual Components

**Data cleaning and anomaly detection:**
```bash
python backend/crew_flow.py
```

**API server only:**
```bash
python backend/api_server.py
```

**Test explainer only:**
```bash
python backend/test_explainer.py
```

### API Endpoints

- `GET /api/anomalies` - Get all anomaly explanations

## Development

The system uses a multi-agent approach:

1. **Auto-fix Agent** - Cleans billing data
2. **Investigator Agent** - Detects anomalies using rules + ML
3. **Explainer Agent** - Provides intelligent explanations using RAG

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License