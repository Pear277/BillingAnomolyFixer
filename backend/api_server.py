from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI(title="Billing Anomaly API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/anomalies")
async def get_anomalies():
    """Get all anomaly explanations"""
    try:
        file_path = "backend/data/anomaly_explanations.json"
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Ensure data is a list
        if isinstance(data, list):
            return data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading anomalies: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)