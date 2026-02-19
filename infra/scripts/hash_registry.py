import hashlib
import os
import json
from datetime import datetime

def calculate_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_integrity_manifest():
    manifest = {
        "timestamp": datetime.utcnow().isoformat(),
        "files": {},
        "version": "1.0.0-verified"
    }
    
    # Files to track
    include_dirs = ['orchestrator', 'infra', 'data', 'projects', 'docs', 'tests']
    exclude_extensions = ['.pyc', '.db', '.log', '.vercel', '.lock']
    exclude_dirs = ['venv', 'node_modules', '__pycache__', '.git', '.pytest_cache', 'dist']

    for root_dir in include_dirs:
        for root, dirs, files in os.walk(root_dir):
            # Skip excluded dirs
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, '.')
                manifest["files"][rel_path] = calculate_sha256(filepath)

    manifest_path = "data/lineage/integrity_manifest.json"
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Integrity Manifest generated with {len(manifest['files'])} hashed files.")
    return manifest_path

if __name__ == "__main__":
    generate_integrity_manifest()
