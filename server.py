"""Deep Research MCP Server - Root Entry Point

Compatible with MCPize auto-detection.
"""

from fastmcp import FastMCP

mcp = FastMCP(
    "deep-research-mcp",
    version="1.0.0",
    instructions="多源深度调研MCP Server - 覆盖Web搜索/新闻/学术论文多源信息聚合",
)

# Import and re-export all tools
from deep_research_mcp.server import (
    deep_research,
    quick_search,
    search_news,
    search_academic,
    analyze_topic,
    generate_report,
)

if __name__ == "__main__":
    mcp.run()
