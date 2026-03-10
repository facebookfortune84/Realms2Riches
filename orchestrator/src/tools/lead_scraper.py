import requests
import json
import logging
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation

logger = logging.getLogger(__name__)

class HackerNewsLeadScraper(BaseTool):
    """
    Open-source lead generation via HN Algolia API.
    Targets "Show HN" and "Who is Hiring" for B2B SaaS leads.
    """
    
    def execute(self, invocation: Any) -> Dict[str, Any]:
        # Algolia API for HN: https://hn.algolia.com/api
        # Search for "Show HN" posts in the last 24 hours
        yesterday = int((datetime.utcnow() - timedelta(days=1)).timestamp())
        url = f"https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&numericFilters=created_at_i>{yesterday}&hitsPerPage=50"
        
        leads = []
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            for hit in data.get("hits", []):
                author = hit.get("author")
                title = hit.get("title")
                url = hit.get("url")
                text = hit.get("story_text") or ""
                
                # Extract potential emails or domains from text/url
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                email = email_match.group(0) if email_match else f"{author}@news.ycombinator.com"
                
                leads.append({
                    "name": author,
                    "email": email,
                    "source": "HackerNews_ShowHN",
                    "interest": title,
                    "url": url,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            # Deduplicate and save to leads.json
            self._save_leads(leads)
            
            return {
                "status": "success",
                "leads_found": len(leads),
                "message": f"Harvested {len(leads)} leads from HackerNews."
            }
        except Exception as e:
            logger.error(f"HN Scraper Failed: {e}")
            return {"status": "error", "reason": str(e)}

    def _save_leads(self, new_leads: List[Dict[str, Any]]):
        lead_path = "data/customers/leads.json"
        existing_leads = []
        if os.path.exists(lead_path):
            try:
                with open(lead_path, "r", encoding="utf-8") as f:
                    existing_leads = json.load(f)
            except: pass
        
        existing_emails = {l.get("email") for l in existing_leads}
        added_count = 0
        for lead in new_leads:
            if lead["email"] not in existing_emails:
                existing_leads.append(lead)
                existing_emails.add(lead["email"])
                added_count += 1
                
        with open(lead_path, "w", encoding="utf-8") as f:
            json.dump(existing_leads, f, indent=2)
        
        logger.info(f"💾 Lead Scraper: Added {added_count} new leads to {lead_path}")

class JobBoardLeadScraper(BaseTool):
    """
    Agentic Replacement Scraper.
    Targets companies hiring for 'Sales' or 'SDR' roles.
    Pitches the Sovereign Swarm as a $0/hr alternative.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        # Using an open API for job searches (e.g., Search API or GitHub Jobs style fallback)
        # We target specific keywords: SDR, Sales, Lead Generation
        query = "SDR"
        url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story"
        
        leads = []
        try:
            # For this industrial build, we reuse the HN Algolia but search for job posts
            response = requests.get(url, timeout=10)
            data = response.json()
            
            for hit in data.get("hits", []):
                text = hit.get("story_text") or ""
                if any(k in text.lower() for k in ["hiring", "job", "recruiting"]):
                    author = hit.get("author")
                    title = hit.get("title")
                    
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                    email = email_match.group(0) if email_match else f"{author}@news.ycombinator.com"
                    
                    leads.append({
                        "name": author,
                        "email": email,
                        "source": "JobBoard_AgenticReplacement",
                        "interest": f"Hiring for: {title[:50]}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            HackerNewsLeadScraper(ToolConfig(tool_id="tmp", name="tmp", description="tmp", parameters_schema={}, allowed_agents=["*"]))._save_leads(leads)
            
            return {"status": "success", "leads_found": len(leads)}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

def get_lead_tools() -> List[BaseTool]:
    return [
        HackerNewsLeadScraper(ToolConfig(
            tool_id="hn_scraper",
            name="HN Scraper",
            description="Extracts leads from HackerNews Show HN",
            parameters_schema={},
            allowed_agents=["*"]
        )),
        JobBoardLeadScraper(ToolConfig(
            tool_id="job_scraper",
            name="Job Scraper",
            description="Targets companies hiring SDRs",
            parameters_schema={},
            allowed_agents=["*"]
        ))
    ]

import os # Ensure os is imported for _save_leads
