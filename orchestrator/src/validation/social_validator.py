import re
import logging

logger = logging.getLogger(__name__)

class SocialPostValidator:
    """
    Strict Pre-Flight Check for Social Media Dispatches.
    Ensures every post has a verifiable monetization path.
    """
    
    # Regex to match Stripe or local checkout API links
    CTA_REGEX = r"(https://checkout\.stripe\.com/c/pay/|https://glowfly-sizeable-lazaro\.ngrok-free\.dev/api/checkout/)"

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

        # 2. Action Verb Check (The 'Button' in text)
        action_verbs = r"(Secure|Acquire|Access|Buy|Join|Initialize|Deploy|Get)"
        if not re.search(action_verbs, message, re.IGNORECASE):
            return False, "Post lacks a clear action verb (Secure, Acquire, etc.). Post must be a direct driver."

        return True, ""
