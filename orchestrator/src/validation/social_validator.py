import re
import logging

logger = logging.getLogger(__name__)

class SocialPostValidator:
    """
    Strict Pre-Flight Check for Social Media Dispatches.
    Ensures every post has a verifiable monetization path.
    """
    
    # Robust Regex for all Stripe and local checkout patterns
    CTA_REGEX = r"(checkout\.stripe\.com|buy\.stripe\.com|glowfly-sizeable-lazaro\.ngrok-free\.dev/api/checkout)"

    @staticmethod
    def validate(message: str, link: str) -> tuple:
        """
        Validates the post and returns (is_valid, error_reason).
        """
        if not link:
            return False, "No Link provided for CTA."
            
        # 1. Monetization Link Check
        has_revenue_link = re.search(SocialPostValidator.CTA_REGEX, link) or \
                          "frontend-two-xi" in link or "ngrok-free.dev" in link
        
        if not has_revenue_link:
            return False, f"Link '{link}' is not a verified revenue pattern."

        # 2. Action Verb Check
        action_verbs = r"(Secure|Acquire|Access|Buy|Join|Initialize|Deploy|Get)"
        if not re.search(action_verbs, message, re.IGNORECASE):
            return False, "Post lacks a direct action verb (Secure, Buy, etc.)."

        return True, ""
