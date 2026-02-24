import re
import requests
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class SocialPostValidator:
    """
    Strict Pre-Flight Check for Social Media Dispatches.
    Industrial-grade, no-hallucination validation.
    """
    
    CTA_REGEX = r"(checkout\.stripe\.com|buy\.stripe\.com|glowfly-sizeable-lazaro\.ngrok-free\.dev/api/checkout)"

    @staticmethod
    def validate(message: str, link: str, media_url: str = None) -> Tuple[bool, str]:
        if not link:
            return False, "CRITICAL: No Link provided."
            
        # 1. Monetization Link Validation
        has_revenue_pattern = re.search(SocialPostValidator.CTA_REGEX, link)
        if not has_revenue_pattern:
            return False, f"CRITICAL: Link '{link}' is not a verified revenue pattern."

        # 2. Bit-Level Link Reachability
        try:
            res = requests.head(link, timeout=5, allow_redirects=True)
            if res.status_code >= 400:
                return False, f"CRITICAL: Monetization link unreachable (HTTP {res.status_code})."
        except Exception as e:
            return False, f"CRITICAL: Link validation exception: {e}"

        # 3. Media Integrity Check
        if media_url:
            try:
                m_res = requests.head(media_url, timeout=5, headers={"ngrok-skip-browser-warning": "true"})
                if m_res.status_code >= 400:
                    return False, f"CRITICAL: Media asset unreachable (HTTP {m_res.status_code})."
            except Exception as e:
                return False, f"CRITICAL: Media validation exception: {e}"

        # 4. Action Verb Check
        action_verbs = r"(Secure|Acquire|Access|Buy|Join|Initialize|Deploy|Get)"
        if not re.search(action_verbs, message, re.IGNORECASE):
            return False, "CRITICAL: Post lacks high-authority action verb."

        return True, "VERIFIED"
