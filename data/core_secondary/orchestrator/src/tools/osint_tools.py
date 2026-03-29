import requests
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class OSINTTool(BaseTool):
    """
    Open Source Intelligence (OSINT) Tool for Lead Generation & Reconnaissance.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        domain = params.get("domain")
        action = params.get("action", "full_scan")
        
        if not domain:
            return {"status": "error", "reason": "Missing domain parameter"}

        results = {"domain": domain}

        if action in ["subdomains", "full_scan"]:
            results["subdomains"] = self.query_crtsh(domain)
        
        if action in ["whois", "full_scan"]:
            results["whois"] = self.whois_lookup(domain)

        return {"status": "success", "data": results}

    def query_crtsh(self, domain: str) -> List[str]:
        """Query certificate transparency logs via crt.sh for subdomain discovery."""
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                logger.warning(f"crt.sh query failed for {domain}: {resp.status_code}")
                return []
            entries = resp.json()
            subdomains = set()
            for entry in entries:
                name_value = entry.get("name_value", "")
                for name in name_value.split("\n"):
                    name = name.strip().lower()
                    if name and "*" not in name:
                        subdomains.add(name)
            return sorted(list(subdomains))
        except Exception as e:
            logger.error(f"crt.sh error: {e}")
            return []

    def whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Perform WHOIS lookup via RDAP."""
        try:
            url = f"https://rdap.org/domain/{domain}"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": data.get("status", []),
                    "nameservers": [ns.get("ldhName", "") for ns in data.get("nameservers", [])],
                    "events": [
                        {"action": e["eventAction"], "date": e["eventDate"]}
                        for e in data.get("events", [])
                    ],
                }
            return {"error": resp.status_code}
        except Exception as e:
            logger.error(f"RDAP error: {e}")
            return {"error": str(e)}

def get_osint_tools() -> List[BaseTool]:
    return [
        OSINTTool(ToolConfig(
            tool_id="osint_recon",
            name="OSINT Reconnaissance",
            description="Gather public intelligence (subdomains, WHOIS) on a target domain.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "action": {"type": "string", "enum": ["subdomains", "whois", "full_scan"]}
                },
                "required": ["domain"]
            },
            allowed_agents=["Marketer", "Researcher"]
        ))
    ]
