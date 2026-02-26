import os
import json
import asyncio
import re
from typing import Dict, Any, List, Optional
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class BrowserAgentTool(BaseTool):
    """
    Sovereign Browser Agent (Playwright High-Fidelity).
    Implements real web automation for lead scraping and traffic generation.
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
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

    async def execute_async(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        action = params.get("action")
        url = params.get("url")
        selector = params.get("selector")
        text = params.get("text")
        
        await self._ensure_browser()
        page = await self.context.new_page()
        
        try:
            if action == "navigate":
                logger.info(f"Browsing to {url}...")
                await page.goto(url, wait_until="networkidle")
                title = await page.title()
                return {"status": "success", "url": url, "title": title}
                
            elif action == "scrape_leads":
                logger.info(f"Scraping leads from {url}...")
                await page.goto(url, wait_until="networkidle")
                # Basic lead extraction logic for common directories
                content = await page.content()
                emails = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)))
                return {"status": "success", "emails_found": emails, "count": len(emails)}

            elif action == "click":
                await page.click(selector)
                return {"status": "success", "action": "click", "selector": selector}
                
            elif action == "type":
                await page.fill(selector, text)
                return {"status": "success", "action": "type", "selector": selector}

            return {"status": "error", "reason": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Browser action {action} failed: {e}")
            return {"status": "error", "reason": str(e)}
        finally:
            await page.close()

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        """Bridge to async execution for the synchronous orchestrator logic."""
        try:
            # We use a nested event loop or run_until_complete if not in an existing loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in a loop (like the API), we need to run this differently
                # or ensure the orchestrator call is async.
                # For now, we'll try to run it in a thread or separate process if needed.
                return asyncio.run_coroutine_threadsafe(self.execute_async(invocation), loop).result()
            else:
                return asyncio.run(self.execute_async(invocation))
        except Exception as e:
            return {"status": "error", "reason": f"Async bridge failure: {e}"}

    async def close(self):
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
