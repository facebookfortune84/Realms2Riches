import os
from dotenv import load_dotenv

load_dotenv(".env.prod")
smtp_pass = os.getenv("SMTP_PASS")
print(f"SMTP_PASS Length: {len(smtp_pass) if smtp_pass else 'NONE'}")
if smtp_pass:
    print(f"SMTP_PASS First 2: {smtp_pass[:2]}")
