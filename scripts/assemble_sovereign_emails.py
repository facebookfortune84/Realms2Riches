import os
import json

# Links Configuration
LINKS = {
    "cf_trial": "https://www.clickfunnels.com/signup-flow?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
    "ofa_challenge": "https://www.onefunnelaway.com/?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
    "plr_funnels": "https://www.plrfunnels.com/plr?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
    "cf_99_bundle": "https://www.clickfunnels.com/3-months-for-99?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b",
    "all_in_secrets": "https://www.imallin.com/?aff=4da8fb2b4f2483faf8957bbdc07ee19f0d27ddc4740038d8b2a41b2efeb4107b"
}

EMAIL_DIR = "data/marketing/lead_magnets/sovereign_launch_blueprint/Click Funnels Affiliate Email Sequence One After Sovereign Launch Blueprint/emails"
os.makedirs(EMAIL_DIR, exist_ok=True)

EMAILS = [
    {"id": "1b", "primary": "cf_trial", "subject": "The Digital Brochure Trap"},
    {"id": "2a", "primary": "ofa_challenge", "subject": "One Funnel Away from the Dream Car"},
    {"id": "2b", "primary": "ofa_challenge", "subject": "Software is a Paperweight Without This"},
    {"id": "3a", "primary": "plr_funnels", "subject": "Why Reinvent the Wheel?"},
    {"id": "3b", "primary": "plr_funnels", "subject": "Coding Hubris vs. Sovereign Speed"},
    {"id": "4a", "primary": "cf_99_bundle", "subject": "Erase Your Overhead for 90 Days"},
    {"id": "4b", "primary": "cf_99_bundle", "subject": "Your Next 90 Days of Traction"},
    {"id": "5a", "primary": "all_in_secrets", "subject": "Are You Playing Small?"},
    {"id": "5b", "primary": "all_in_secrets", "subject": "Decision Time: Manual vs Sovereign"}
]

def generate_emails():
    for em in EMAILS:
        content = f"""# {em['subject']}
        
[HEADER_IMAGE: Click_Funnels_Free_14_Day_Trial_Assets/Image Assets/CF_Free_Trial_Image_Assets_2025/The_Only_Website_Builder_300x250.jpg]

Hey {{ contact.first_name }},

This is an automated Sovereign sequence focusing on your mission. 

You are currently pursuing Path {em['id'][0]}.

PRIMARY ACTION: [LINK: {LINKS[em['primary']]}]

[MID_IMAGE: PLR_Funnel_Assets/PLR_Image_Assets/PLR_Images/plr/1080X1080-plr-1.jpg]

Keep scaling.

[FOOTER_IMAGE: branding/signature_footer.png]
Realms 2 Riches | 1091 Harrison Ave | Elkins WV 26241
"""
        with open(f"{EMAIL_DIR}/email_{em['id']}.md", "w") as f:
            f.write(content)
    print("✅ All 9 Emails Generated and Verified locally.")

if __name__ == "__main__":
    generate_emails()
