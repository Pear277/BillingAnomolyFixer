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
        file_path = os.path.join(os.path.dirname(__file__), "data", "anomaly_explanations.json")
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Transform data to match frontend expectations
        if isinstance(data, list):
            transformed = []
            for item in data:
                transformed.append({
                    "account_number": item.get("account_number", ""),
                    "issue": "Billing Anomaly",
                    "explanation": item.get("explanation", item.get("reason", "")),
                    "fix": item.get("suggested_fix", item.get("fix", ""))
                })
            return transformed
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading anomalies: {str(e)}")

@app.get("/api/autofixes")
async def get_autofixes():
    """Get all autofix changes"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "data", "cleaned_billing_streetfix_autofix_changes.json")
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
        raise HTTPException(status_code=500, detail=f"Error reading autofixes: {str(e)}")

@app.delete("/api/anomalies/{index}")
async def delete_anomaly(index: int):
    """Delete an anomaly by index"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "data", "anomaly_explanations.json")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Anomalies file not found")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or index < 0 or index >= len(data):
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        data.pop(index)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Anomaly deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting anomaly: {str(e)}")

@app.delete("/api/autofixes/{index}")
async def delete_autofix(index: int):
    """Delete an autofix by index"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "data", "cleaned_billing_streetfix_autofix_changes.json")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Autofixes file not found")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or index < 0 or index >= len(data):
            raise HTTPException(status_code=404, detail="Autofix not found")
        
        data.pop(index)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Autofix deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting autofix: {str(e)}")

@app.get("/api/test")
async def test():
    return {"status": "API is working"}

if __name__ == "__main__":
    import uvicorn
    print("Starting API server on http://localhost:8000")
    print("Test endpoint: http://localhost:8000/api/test")
    uvicorn.run(app, host="0.0.0.0", port=8000)