import os
from pathlib import Path
import json

root = Path("C:/Realms2Riches")

features = {
    "frontend_components": [],
    "frontend_pages": [],
    "frontend_routes": [],
    "frontend_api_calls": [],
    "backend_endpoints": [],
}

# FRONTEND COMPONENTS
for file in root.joinpath("frontend/src").rglob("*.jsx"):
    features["frontend_components"].append(str(file))

# FRONTEND ROUTES
for file in root.joinpath("frontend/src").rglob("*.jsx"):
    with open(file) as f:
        for line in f:
            if "path:" in line or "Route" in line:
                features["frontend_routes"].append(f"{file}: {line.strip()}")

# FRONTEND API CALLS
for file in root.joinpath("frontend/src").rglob("*.js"):
    with open(file) as f:
        for line in f:
            if "fetch(" in line or "axios" in line:
                features["frontend_api_calls"].append(f"{file}: {line.strip()}")

# BACKEND ENDPOINTS
for file in root.joinpath("core").rglob("*.py"):
    with open(file) as f:
        for line in f:
            if "@app.get" in line or "@app.post" in line:
                features["backend_endpoints"].append(f"{file}: {line.strip()}")

print(json.dumps(features, indent=2))