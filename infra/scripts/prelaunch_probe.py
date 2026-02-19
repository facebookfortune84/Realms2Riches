import os
import requests
import sys
from sqlalchemy import create_engine, text
from groq import Groq

# Load .env.prod manually to ensure we use those exact values
env_path = os.path.join(os.path.dirname(__file__), "../../.env.prod")
print(f"DEBUG: Looking for env at {os.path.abspath(env_path)}")
config = {}
if os.path.exists(env_path):
    # Try multiple encodings, focusing on utf-16 as primary for .env.prod
    content = ""
    for enc in ["utf-16", "utf-8", "utf-8-sig"]:
        try:
            with open(env_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except Exception:
            continue
            
    for line in content.splitlines():
        if line.strip() and not line.startswith("#"):
                try:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        key, val = parts
                        config[key] = val.strip('"').strip("'")
                except ValueError:
                    pass
else:
    print("DEBUG: File NOT found")

print(f"DEBUG: Loaded {len(config)} keys")

print("--- PRELAUNCH PROBE STARTED ---")

# 1. Backend Probe
backend_url = config.get("BACKEND_URL")
print(f"\n[Backend] Probing {backend_url}...")
try:
    # Try health endpoint
    resp = requests.get(f"{backend_url}/health", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:100]}...")
    if resp.status_code == 200:
        print("✅ Backend Reachable")
    else:
        print("⚠️ Backend Reachable but non-200")
except Exception as e:
    print(f"❌ Backend Unreachable: {e}")

# 2. Frontend Probe
frontend_url = config.get("FRONTEND_URL")
print(f"\n[Frontend] Probing {frontend_url}...")
try:
    resp = requests.get(frontend_url, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Frontend Reachable")
        if "Realms2Riches" in resp.text:
            print("✅ Brand content found")
        else:
            print("⚠️ Brand content NOT found")
    else:
        print("❌ Frontend Unreachable/Error")
except Exception as e:
    print(f"❌ Frontend Error: {e}")

# 3. Database Probe
db_url = config.get("DATABASE_URL")
print(f"\n[Database] Probing {db_url}...")
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM products")).scalar()
        print(f"✅ Database Connected. Product count: {result}")
except Exception as e:
    print(f"❌ Database Connection Failed: {e}")

# 4. Groq Probe
groq_key = config.get("GROQ_API_KEY")
groq_model = config.get("FAST_LLM_MODEL", "llama-3.1-8b-instant")
print(f"\n[Groq] Probing model {groq_model}...")
try:
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Ping"}],
        model=groq_model,
    )
    print(f"✅ Groq Response: {chat_completion.choices[0].message.content[:50]}...")
except Exception as e:
    print(f"❌ Groq Failed: {e}")

# 5. Voice Probe (ElevenLabs)
xi_key = config.get("ELEVENLABS_API_KEY")
print(f"\n[Voice] Probing ElevenLabs...")
try:
    headers = {"xi-api-key": xi_key}
    resp = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=5)
    if resp.status_code == 200:
        voices = resp.json().get("voices", [])
        print(f"✅ ElevenLabs Reachable. Found {len(voices)} voices.")
    else:
        print(f"❌ ElevenLabs Error {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"❌ ElevenLabs Failed: {e}")

print("\n--- PRELAUNCH PROBE FINISHED ---")
