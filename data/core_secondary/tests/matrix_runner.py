import sys
import hashlib
import time
from pathlib import Path
import subprocess
import json
from datetime import datetime

# --- Pomp & Circumstance Terminal Colors ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MATRIX_DIR = Path("tests/matrix")
INDEX_FILE = Path("tests/.matrix_index.json")

def print_banner():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("===================================================================")
    print("||       R E A L M S   2   R I C H E S   M A T R I X         ||")
    print("||                 UNIVERSAL TEST ORCHESTRATOR                   ||")
    print("===================================================================")
    print(f"{Colors.ENDC}")

def calculate_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_index(index):
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=4)

def run_matrix():
    print_banner()
    print(f"{Colors.HEADER}Scanning testing grid across {MATRIX_DIR}...{Colors.ENDC}\n")
    
    if not MATRIX_DIR.exists():
        MATRIX_DIR.mkdir(parents=True)
        print(f"{Colors.WARNING}Matrix directory not found. Initialized empty grid at {MATRIX_DIR}{Colors.ENDC}")
        return 0

    test_files = list(MATRIX_DIR.glob("test_*.py"))
    
    if not test_files:
        print(f"{Colors.OKBLUE}No matrix tests found yet. Grid is clear.{Colors.ENDC}")
        return 0

    index = load_index()
    run_count = 0
    pass_count = 0
    fail_count = 0
    
    start_time = time.time()

    for test_file in test_files:
        current_hash = calculate_hash(test_file)
        rel_path = str(test_file)
        
        print(f"Aligning {Colors.OKBLUE}{test_file.name}{Colors.ENDC}... ", end="", flush=True)
        
        # Check if file has changed or if it failed last time
        if rel_path in index and index[rel_path]['hash'] == current_hash and index[rel_path]['status'] == 'passed':
            print(f"[{Colors.OKGREEN}VERIFIED (Cached){Colors.ENDC}]")
            pass_count += 1
            continue

        # Execute Test via Pytest
        print(f"[{Colors.WARNING}EXECUTING{Colors.ENDC}]", end="\r", flush=True)
        
        result = subprocess.run(["pytest", str(test_file), "-q", "--tb=short"], capture_output=True, text=True)
        
        run_count += 1
        
        if result.returncode == 0:
            print(f"Aligning {Colors.OKBLUE}{test_file.name}{Colors.ENDC}... [{Colors.OKGREEN}PASSED{Colors.ENDC}]")
            index[rel_path] = {'hash': current_hash, 'status': 'passed', 'last_run': datetime.now().isoformat()}
            pass_count += 1
        else:
            print(f"Aligning {Colors.OKBLUE}{test_file.name}{Colors.ENDC}... [{Colors.FAIL}FAILED{Colors.ENDC}]")
            print(f"\n{Colors.FAIL}--- ERROR TRACE ---{Colors.ENDC}")
            print(result.stdout)
            print(f"{Colors.FAIL}-------------------{Colors.ENDC}\n")
            index[rel_path] = {'hash': current_hash, 'status': 'failed', 'last_run': datetime.now().isoformat()}
            fail_count += 1

    save_index(index)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n===================================================================")
    print(f"MATRIX DIAGNOSTIC COMPLETE ({duration:.2f}s)")
    print(f"Total Files: {len(test_files)} | Executed: {run_count}")
    print(f"{Colors.OKGREEN}Stable Nodes: {pass_count}{Colors.ENDC} | {Colors.FAIL}Fractured Nodes: {fail_count}{Colors.ENDC}")
    print("===================================================================")
    
    return 1 if fail_count > 0 else 0

if __name__ == "__main__":
    sys.exit(run_matrix())