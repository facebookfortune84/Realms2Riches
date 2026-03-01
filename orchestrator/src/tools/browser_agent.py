import os
import json
import asyncio
import re
import time
from typing import Dict, Any, List, Optional
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class BrowserAgentTool(BaseTool):
    """
    Industrial Browser Agent (Playwright High-Fidelity).
    Implements intelligent DOM extraction and decoding for high-value leads.
    """
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.browser = None
        self.context = None
        self.playwright = None

    async def _ensure_browser(self):
        if not self.browser:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

    async def _intelligent_extract_emails(self, page) -> List[str]:
        """Uses DOM analysis to find emails even when obscured."""
        emails = []
        
        # 1. Direct mailto: extraction (Highest Quality)
        mailtos = await page.eval_on_selector_all("a[href^='mailto:']", "nodes => nodes.map(n => n.href)")
        for m in mailtos:
            email = m.replace("mailto:", "").split("?")[0]
            emails.append(email)
            
        # 2. Decode Cloudflare Obfuscation
        cf_emails = await page.eval_on_selector_all(".__cf_email__", "nodes => nodes.map(n => n.getAttribute('data-cfemail'))")
        for cf in cf_emails:
            try:
                r = int(cf[:2], 16)
                email = ''.join([chr(int(cf[i:i+2], 16) ^ r) for i in range(2, len(cf), 2)])
                emails.append(email)
            except: pass

        # 3. Regex on visible text (Fallback)
        content = await page.content()
        found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        emails.extend(found)
        
        return list(set(emails))

    async def _deep_scrape_emails(self, page, url: str, depth: int = 1) -> List[str]:
        emails = []
        try:
            logger.info(f"Deep Scrape [Level {depth}]: {url}")
            # Use 'commit' to handle redirects better
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1) 
            
            emails.extend(await self._intelligent_extract_emails(page))
            
            if not emails and depth < 2:
                # Target the most likely pages for contact info
                links = await page.eval_on_selector_all("a", "nodes => nodes.map(n => ({href: n.href, text: n.innerText}))")
                sub_links = []
                for link in links:
                    href = link['href']
                    text = link['text'].lower()
                    if href and any(x in href.lower() or x in text for x in ["contact", "about", "team", "founder", "executive"]):
                        if href.startswith("http"):
                            sub_links.append(href)
                
                for sl in list(set(sub_links))[:2]:
                    emails.extend(await self._deep_scrape_emails(page, sl, depth + 1))
                    
        except Exception as e:
            logger.warning(f"Failed to deep scrape {url}: {e}")
            
        return list(set(emails))

    async def execute_async(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        action = params.get("action")
        url = params.get("url")
        query = params.get("query")
        
        await self._ensure_browser()
        page = await self.context.new_page()
        
        try:
            if action == "industrial_scrape":
                target_urls = [url] if url else []
                if query:
                    logger.info(f"Industrial Search: {query}")
                    # Use DuckDuckGo or alternate to avoid Google captchas if needed
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded")
                    
                    # More robust selector for Google search links
                    links = await page.eval_on_selector_all("h3", "nodes => nodes.map(n => n.parentElement.href)")
                    for link in links:
                        if link and link.startswith("http") and "google.com" not in link:
                            target_urls.append(link)
                
                all_emails = []
                # Limit to top 3 sites for speed/stability
                for target in list(set(target_urls))[:3]:
                    all_emails.extend(await self._deep_scrape_emails(page, target))
                
                clean_emails = [e for e in all_emails if "@" in e and "." in e and len(e) > 5 and not any(x in e.lower() for x in ["example", "domain", "test", "sentry", "git", "bootstrap", "wix", "wordpress"])]
                
                return {
                    "status": "success", 
                    "emails_found": clean_emails, 
                    "count": len(clean_emails),
                    "sources_checked": target_urls[:3]
                }

            return {"status": "error", "reason": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Industrial Browser failed: {e}")
            return {"status": "error", "reason": str(e)}
        finally:
            await page.close()

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        try:
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(self.execute_async(invocation))
        except Exception as e:
            return {"status": "error", "reason": f"Async bridge failure: {e}"}

    async def close(self):
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
