import re
import logging

logger = logging.getLogger(__name__)

class LinkBeautifier:
    @staticmethod
    def beautify(url: str) -> str:
        if not url: return ""
        return url.split("?")[0]

class ConversionAuditor:
    """
    The 'Final Gatekeeper'. 
    Ensures posts have BOTH a visual button and a beautified link.
    """
    @staticmethod
    def audit(message: str, link: str) -> tuple:
        # 1. Check for 'Visual Button' (Emoji-based UI)
        # More inclusive pattern: checks for any bracketed text with or without emojis
        button_pattern = r"(\[.*\]|【.*】|▶️|💳|💰|🛒)"
        has_visual_button = re.search(button_pattern, message)
        
        # 2. Check for the link in the message body
        # Many social platforms need the link in the text to be clickable
        has_link_in_text = link.lower() in message.lower() if link else False
        
        if not has_visual_button:
            logger.warning(f"Auditor: Missing visual button in msg: {message[:100]}...")
            return False, "Post lacks a 'Visual Button' (Emoji UI)."
        
        if not has_link_in_text and link:
            logger.warning(f"Auditor: Link {link} not found in msg.")
            return False, "Post lacks the direct conversion link in the text."
            
        return True, "CONVERSION PATH VERIFIED"
