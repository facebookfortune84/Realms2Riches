import os
import re

# --- CONFIGURATION ---
OUTPUT_FILE = "sovereign_bundle.txt"
EXCLUDE_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", ".pytest_cache", "dist", "build", "_repo_bundle"}
EXCLUDE_FILES = {".env", ".env.prod", ".env.local", "env_files.txt", "env_dump.txt", "secrets.txt", "sovereign_bundle.txt", "test_orchestrator.db", "orchestrator.db"}
INCLUDE_EXTENSIONS = {".py", ".md", ".json", ".js", ".jsx", ".ts", ".tsx", ".yaml", ".yml", ".txt", ".ps1", ".sh"}

# Redaction patterns
REDACT_PATTERNS = [
    r'(?i)(API_KEY|SECRET|PASSWORD|PASS|TOKEN|PRIVATE_KEY|LICENSE_KEY)\s*[:=]\s*["\'].*?["\']',
    r'(?i)(API_KEY|SECRET|PASSWORD|PASS|TOKEN|PRIVATE_KEY|LICENSE_KEY)\s*[:=]\s*[^\s,]+'
]

def redact_content(content):
    for pattern in REDACT_PATTERNS:
        content = re.sub(pattern, r'\1: [REDACTED]', content)
    return content

def create_bundle():
    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as bundle:
        for root, dirs, files in os.walk("."):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in sorted(files):
                if file in EXCLUDE_FILES:
                    continue
                
                ext = os.path.splitext(file)[1].lower()
                if ext in INCLUDE_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, ".")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            redacted = redact_content(content)
                            
                            bundle.write(f"\n{'='*80}\n")
                            bundle.write(f"FILE: {rel_path}\n")
                            bundle.write(f"{'='*80}\n\n")
                            bundle.write(redacted)
                            bundle.write("\n")
                            count += 1
                    except Exception as e:
                        bundle.write(f"\nERROR READING {rel_path}: {str(e)}\n")

    print(f"✅ Created {OUTPUT_FILE} with {count} files.")

if __name__ == "__main__":
    create_bundle()
