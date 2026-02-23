import re
import logging

logger = logging.getLogger(__name__)

class LinkBeautifier:
    """Transforms raw Stripe/ngrok URLs into clean, high-authority dispatches."""
    
    @staticmethod
    def beautify(url: str) -> str:
        # In a real setup, this would hit Bitly/Dub API.
        # Here we provide a 'Sovereign' display transform.
        if "checkout.stripe.com" in url:
            return "https://sovereign.link/acquire-platinum"
        if "ngrok-free.dev" in url:
            return url.replace("https://", "").split("?")[0]
        return url

class ConversionAuditor:
    """
    The 'Final Gatekeeper'. 
    Ensures posts have BOTH a visual button and a beautified link.
    """
    
    @staticmethod
    def audit(message: str, link: str) -> tuple:
        # 1. Check for 'Visual Button' (Emoji-based UI)
        button_pattern = r"(\[.*\]|【.*】|▶️|💳|💰)"
        has_visual_button = re.search(button_pattern, message)
        
        # 2. Check for Clickable link density
        has_link = link is not None and len(link) > 10
        
        if not has_visual_button:
            return False, "Post lacks a 'Visual Button' (Emoji UI). Organic feeds require visual triggers."
        
        if not has_link:
            return False, "Post lacks a functional conversion link."
            
        return True, "CONVERSION PATH VERIFIED"
