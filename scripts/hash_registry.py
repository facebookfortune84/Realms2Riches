import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

REGISTRY_FILE = "data/lineage/hash_registry.json"

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_registry():
    """Update the file hash registry."""
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                registry = json.load(f)
        except json.JSONDecodeError:
            pass

    current_snapshot = {}
    changed_files = []
    new_files = []

    # Walk through the project directory
    for root, dirs, files in os.walk("."):
        if ".git" in root or "__pycache__" in root or "venv" in root or "node_modules" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Skip registry file itself and large/binary files if needed
            if file_path == REGISTRY_FILE:
                continue
                
            try:
                file_hash = calculate_hash(file_path)
                current_snapshot[file_path] = file_hash
                
                if file_path not in registry:
                    new_files.append(file_path)
                elif registry[file_path] != file_hash:
                    changed_files.append(file_path)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    # Save the new snapshot
    timestamp = datetime.now().isoformat()
    record = {
        "timestamp": timestamp,
        "files": current_snapshot,
        "changes": {
            "modified": changed_files,
            "new": new_files
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    
    with open(REGISTRY_FILE, "w") as f:
        json.dump(record, f, indent=2)
        
    print(f"Lineage locked at {timestamp}")
    print(f"New files: {len(new_files)}")
    print(f"Modified files: {len(changed_files)}")

if __name__ == "__main__":
    update_registry()
