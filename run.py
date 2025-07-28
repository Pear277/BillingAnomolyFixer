import subprocess
import sys
import os

def main():
    print("🚀 Starting Billing Anomaly Fixer...")
    
    # Run the full crew workflow
    print("1. Running data cleaning and anomaly detection...")
    subprocess.run([sys.executable, "backend/crew_flow.py"])
    
    print("2. Starting API server...")
    # Start API server in background
    api_process = subprocess.Popen([sys.executable, "backend/api_server.py"])
    
    print("✅ API server running on http://localhost:8000")
    print("📋 API endpoint: http://localhost:8000/api/anomalies")
    print("")
    print("🎨 To start frontend:")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("   Then visit http://localhost:5173")
    print("")
    print("Press Ctrl+C to stop the API server")
    
    try:
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping API server...")
        api_process.terminate()

if __name__ == "__main__":
    main()