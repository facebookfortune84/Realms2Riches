import os
import json
import re

CAMPAIGNS = [
    {
        "id": "cf_trial",
        "name": "ClickFunnels Free 14 Day Trial",
        "link": "https://www.clickfunnels.com/signup-flow?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
        "email_dir": "data/assets/Click_Funnels_Free_14_Day_Trial_Assets/Email_Swipes"
    },
    {
        "id": "ofa_challenge",
        "name": "One Funnel Away Challenge",
        "link": "https://www.onefunnelaway.com/?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
        "email_dir": "data/assets/OFA_Assets/OFA_Email_Swipes"
    },
    {
        "id": "plr_funnels",
        "name": "PLR Funnels",
        "link": "https://www.plrfunnels.com/plr?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
        "email_dir": "data/assets/PLR_Funnel_Assets/PLR_Email_Assets"
    },
    {
        "id": "cf_99_bundle",
        "name": "3 Months of ClickFunnels for $99",
        "link": "https://www.clickfunnels.com/3-months-for-99?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
        "email_dir": "data/assets/3_Months_for_99_Assets/Email_Assets"
    },
    {
        "id": "all_in_secrets",
        "name": "I'm All In - Funnel Builder Secrets",
        "link": "https://www.imallin.com/?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
        "email_dir": "data/assets/Im_All_In_Assets/Email_Assets"
    }
]

def generate_workflows():
    all_sequences = {}

    for camp in CAMPAIGNS:
        sequence = []
        email_dir = camp["email_dir"]
        
        if os.path.exists(email_dir):
            for file in sorted(os.listdir(email_dir)):
                if file.endswith(".md"):
                    with open(os.path.join(email_dir, file), "r", encoding="utf-8") as f:
                        raw_content = f.read()
                        
                        # Split by common markers if multiple emails in one file
                        raw_emails = re.split(r'#+ Email|--- Email|Email \d+', raw_content)
                        for idx, email in enumerate(raw_emails):
                            clean_email = email.strip()
                            if not clean_email: continue
                            
                            # Inject Link
                            processed = clean_email.replace("[AFFILIATE_LINK]", camp["link"])
                            processed = processed.replace("YOUR LINK HERE", camp["link"])
                            processed = processed.replace("{{LINK}}", camp["link"])
                            
                            sequence.append({
                                "step": len(sequence) + 1,
                                "subject": f"[{camp['name']}] Message {len(sequence) + 1}",
                                "body": processed
                            })
        
        all_sequences[camp["id"]] = sequence

    output_path = "data/affiliates/Click_Funnels/workflows_automated.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(all_sequences, out, indent=2)
    
    print(f"✅ Automated Workflows Generated: {output_path}")

if __name__ == "__main__":
    generate_workflows()
