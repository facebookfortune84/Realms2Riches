import uvicorn
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("🚀 Starting Sovereign Backend Server...")
    uvicorn.run("orchestrator.src.core.api:app", host="127.0.0.1", port=8000, reload=False)
