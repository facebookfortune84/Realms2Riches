import sys
import os
from datetime import datetime

# Ensure we can import from orchestrator
sys.path.append(os.getcwd())

from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.core.outreach.config import outreach_settings
from orchestrator.src.core.config import settings

def main():
    print("📧 SMTP STREAM 12 VERIFICATION")
    print("=================================")
    print(f"OUTREACH_ENABLED: {outreach_settings.OUTREACH_ENABLED}")
    print(f"OUTREACH_DRY_RUN: {outreach_settings.OUTREACH_DRY_RUN}")
    print(f"TEST RECIPIENT: {outreach_settings.OUTREACH_TEST_RECIPIENT}")
    print(f"SMTP USER: {settings.SMTP_USER}")
    
    tool = SMTPOutreachTool(None) # Config not needed for direct instantiation if we don't use the wrapper fully
    
    payload = {
        "target_email": "test_lead@example.com", # Should be rerouted
        "target_name": "Test Lead",
        "subject": f"Stream 12 Verification {datetime.now().isoformat()}",
        "html_body": "<h1>Stream 12 Active</h1><p>This is a verification email from the Sovereign Monetization Engine.</p>"
    }
    
    print("\n🚀 Executing Tool...")
    result = tool.execute(payload)
    print(f"\nRESULT: {result}")
    
    if result.get("status") == "success":
        print("✅ SMTP Tool executed successfully (Mock/Real).")
    elif result.get("status") == "simulated":
         print("⚠️  SMTP Tool simulated (Outreach Disabled).")
    else:
        print("❌ SMTP Tool failed.")

if __name__ == "__main__":
    main()
