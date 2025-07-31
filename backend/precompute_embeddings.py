from crewai_tools import RagTool

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

rag_tool = RagTool(config=config)
rag_tool.add("backend/data/first_10_customers.csv", data_type="csv")
print("Saved embeddings!")