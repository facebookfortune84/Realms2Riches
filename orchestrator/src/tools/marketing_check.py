from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

def check_marketing_readiness():
    """Validates that marketing and social configurations are non-placeholder."""
    config = settings.marketing_config
    placeholders = ["My Brand", "My Product", "example.com", "mybrand"]
    
    issues = []
    
    if config.brand_name in placeholders:
        issues.append("BRAND_NAME is still a placeholder")
    if "example.com" in config.website_url:
        issues.append("MARKETING_SITE_URL is still a placeholder")
    if config.twitter_handle in placeholders:
        issues.append("SOCIAL_TWITTER_HANDLE is still a placeholder")
        
    if not issues:
        logger.info("Marketing readiness check: SUCCESS - Real-world values detected.")
        return True
    else:
        for issue in issues:
            logger.warning(f"Marketing readiness check: PENDING - {issue}")
        return False

if __name__ == "__main__":
    check_marketing_readiness()
