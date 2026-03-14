import logging
from mcp.server.fastmcp import FastMCP
from orchestrator.src.core.oracle_advisor import OracleAdvisor
from orchestrator.src.memory.vector_store import VectorStore

import sys
# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-oracle")

# Initialize FastMCP Server
mcp = FastMCP("Realms2Riches Oracle Server")
oracle = OracleAdvisor()
vector_store = VectorStore()

@mcp.tool()
async def get_strategic_directives() -> str:
    """Analyze performance and generate new strategic directives."""
    perf = oracle.analyze_performance()
    directives = oracle.generate_new_directives(perf)
    return str({"performance": perf, "directives": directives})

@mcp.tool()
async def search_knowledge(query: str, limit: int = 5) -> str:
    """Search the Sovereign RAG knowledge base."""
    results = vector_store.search(query, limit=limit)
    return str(results)

@mcp.tool()
async def remember_fact(text: str, category: str = "general") -> str:
    """Add a fact to the Sovereign RAG knowledge base."""
    doc_id = vector_store.add(text, {"category": category, "source": "mcp-oracle"})
    return f"Fact remembered with ID: {doc_id}"

if __name__ == "__main__":
    mcp.run()
