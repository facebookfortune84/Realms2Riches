import os
from pathlib import Path

ROOT = Path(r"C:\Realms2Riches")
ENV_FILE = ROOT / ".env"

REQUIRED_VARS = [
    "POSTGRES_URL",
    "REALMS2RICHES_CORE_KEY",
    "AI_GATEWAY_API_KEY",
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "STRIPE_PUBLISHABLE_KEY",
    "STRIPE_TEST_MODE",
    "FAST_LLM_MODEL",
    "SMART_LLM_MODEL",
    "VITE_API_URL",
    "VITE_BACKEND_URL",
]

def load_env(path):
    if not path.exists():
        print(f"[WARNING] {path} does not exist.")
        return {}

    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                env[key] = value
    return env

def main():
    print(f"\nValidating environment: {ENV_FILE}")

    env = load_env(ENV_FILE)

    missing = [var for var in REQUIRED_VARS if var not in env]

    if missing:
        print("\nMissing required environment variables:\n")
        for var in missing:
            print(f"  - {var}")
    else:
        print("\nAll required environment variables are present.")

if __name__ == "__main__":
    main()