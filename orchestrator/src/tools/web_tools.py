import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class WebSearchTool(BaseTool):
    """Searches the web for information using a search provider (or mock)."""
    def __init__(self, config: ToolConfig, api_key: str = None):
        super().__init__(config)
        self.api_key = api_key

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        logger.info(f"Searching web for: {query}")
        
        # In production, use Serper.dev or Google Search API
        # For now, we simulate finding relevant results
        return {
            "results": [
                {"title": f"Recent developments in {query}", "url": "https://example.com/ai-news", "snippet": "Breakthroughs in agentic swarms..."},
                {"title": f"The evolution of {query}", "url": "https://techcrunch.com/agents", "snippet": "New MPC server standards released..."}
            ]
        }

class WebScraperTool(BaseTool):
    """Scrapes content from a URL and extracts text."""
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        url = input_data.get("url", "")
        logger.info(f"Scraping URL: {url}")
        
        try:
            # Simulate scraping
            if "example.com" in url:
                return {
                    "text": "Autonomous swarms are the next frontier. We see a shift towards multi-orchestrator models and shared memory pools.",
                    "metadata": {"source": url, "extracted": "2026-02-20"}
                }
            
            # Real attempt if URL is provided
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Extract text from p tags
            text = " ".join([p.get_text() for p in soup.find_all('p')])
            return {"text": text[:2000], "metadata": {"source": url}}
        except Exception as e:
            return {"error": str(e)}
