"""Deep Research MCP Server

多源深度调研MCP Server - 智能搜索+分析+报告生成
覆盖Web/新闻/学术多源信息聚合

启动方式:
    python -m deep_research_mcp
    python -m deep_research_mcp --transport http --port 8080
"""

import argparse
import asyncio
from typing import Optional, List

from fastmcp import FastMCP

from .search_engines import SearchAggregator
from .analyzers import TextAnalyzer, SentimentAnalyzer, PerspectiveAnalyzer
from .report_generator import ReportGenerator

# ========== 创建MCP Server ==========
mcp = FastMCP(
    "deep-research-mcp",
    version="1.0.0",
    instructions="多源深度调研MCP Server - 覆盖Web搜索/新闻/学术论文多源信息聚合，提供深度调研、快速搜索、新闻追踪、学术搜索、话题分析、报告生成等6个工具。支持中文和英文内容分析。",
)

# 全局搜索聚合器
_searcher: Optional[SearchAggregator] = None


def _get_searcher() -> SearchAggregator:
    global _searcher
    if _searcher is None:
        _searcher = SearchAggregator()
    return _searcher


# ========== MCP工具定义 ==========

@mcp.tool()
async def deep_research(
    topic: str,
    depth: str = "standard",
    sources: Optional[List[str]] = None,
) -> str:
    """深度调研 - 多源搜索+页面抓取+智能分析+结构化报告

    对指定主题进行深度调研，聚合Web/新闻/学术多源信息，
    抓取关键页面内容，进行情感分析、关键词提取、多维度分析，
    最终生成结构化Markdown报告。

    Args:
        topic: 调研主题，如 "AI Agent市场趋势2026", "新能源汽车产业链"
        depth: 调研深度 (brief/standard/comprehensive)
               - brief: 快速调研，抓取2页，约1分钟
               - standard: 标准调研，抓取5页，约2-3分钟
               - comprehensive: 全面调研，抓取10页，约5分钟
        sources: 搜索源列表，如 ["web", "news", "academic"]，默认全部
    """
    searcher = _get_searcher()
    sources = sources or ["web", "news", "academic"]

    # 映射深度到参数
    depth_config = {
        "brief": {"max_per_source": 5, "max_pages": 2, "max_length": 2000},
        "standard": {"max_per_source": 10, "max_pages": 5, "max_length": 3000},
        "comprehensive": {"max_per_source": 15, "max_pages": 10, "max_length": 5000},
    }
    config = depth_config.get(depth, depth_config["standard"])

    # 1. 多源搜索
    search_results = await searcher.search_all(
        topic, sources=sources, max_per_source=config["max_per_source"]
    )

    # 2. 深度抓取
    all_results = []
    for results in search_results.values():
        all_results.extend(results)

    fetched_contents = await searcher.deep_fetch(
        all_results, max_pages=config["max_pages"], max_length=config["max_length"]
    )

    # 3. 生成报告
    report = ReportGenerator.generate_research_report(
        topic=topic,
        search_results=search_results,
        fetched_contents=fetched_contents,
        depth=depth,
    )

    return report


@mcp.tool()
async def quick_search(query: str, max_results: int = 10) -> str:
    """快速搜索 - 多源聚合摘要

    对查询进行快速多源搜索，返回聚合摘要。

    Args:
        query: 搜索查询，如 "最新AI芯片发布"
        max_results: 最大结果数，默认10
    """
    searcher = _get_searcher()
    results = await searcher.search_all(query, max_per_source=max_results)

    lines = [f"## 快速搜索: {query}", ""]

    total = sum(len(r) for r in results.values())
    lines.append(f"共找到 {total} 条结果（来自 {len(results)} 个源）")
    lines.append("")

    for source, items in results.items():
        lines.append(f"### {source.upper()} ({len(items)}条)")
        for i, item in enumerate(items[:5], 1):
            lines.append(f"{i}. **{item.title}**")
            lines.append(f"   {item.snippet[:150]}...")
            lines.append(f"   [{item.url}]({item.url})")
            if item.date:
                lines.append(f"   日期: {item.date}")
            lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def search_news(query: str, max_results: int = 10) -> str:
    """新闻搜索 - 时效性信息追踪

    搜索最新新闻，适合追踪热点事件和行业动态。

    Args:
        query: 新闻查询，如 "美联储降息最新"
        max_results: 最大结果数，默认10
    """
    searcher = _get_searcher()
    results = await searcher.ddg.search_news(query, max_results)

    lines = [f"## 新闻搜索: {query}", ""]

    if not results:
        return f"未找到关于 '{query}' 的新闻。"

    lines.append(f"共找到 {len(results)} 条新闻")
    lines.append("")

    for i, item in enumerate(results, 1):
        lines.append(f"### {i}. {item.title}")
        lines.append(f"- 来源: {item.source}")
        if item.date:
            lines.append(f"- 日期: {item.date}")
        lines.append(f"- 摘要: {item.snippet}")
        lines.append(f"- 链接: {item.url}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def search_academic(query: str, max_results: int = 10) -> str:
    """学术搜索 - 论文/研究报告检索

    搜索学术论文，当前支持arXiv。

    Args:
        query: 学术查询，如 "transformer architecture survey"
        max_results: 最大结果数，默认10
    """
    searcher = _get_searcher()
    results = await searcher.academic.search_arxiv(query, max_results)

    lines = [f"## 学术搜索: {query}", ""]

    if not results:
        return f"未找到关于 '{query}' 的学术论文。"

    lines.append(f"共找到 {len(results)} 篇论文")
    lines.append("")

    for i, item in enumerate(results, 1):
        lines.append(f"### {i}. {item.title}")
        if item.date:
            lines.append(f"- 发布日期: {item.date}")
        lines.append(f"- 摘要: {item.snippet[:300]}...")
        lines.append(f"- 链接: {item.url}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def analyze_topic(
    topic: str,
    perspectives: Optional[List[str]] = None,
) -> str:
    """话题分析 - 多角度拆解与洞察

    对话题进行多角度分析，包括市场、财务、技术、政策、风险等维度。

    Args:
        topic: 分析话题，如 "人形机器人产业化"
        perspectives: 分析维度，如 ["market", "technology", "risk"]
                     可选: market/financial/technology/policy/risk
                     默认全部维度
    """
    searcher = _get_searcher()

    # 搜索相关信息
    search_results = await searcher.search_all(topic, max_per_source=8)

    # 合并文本
    all_text = ""
    for source, results in search_results.items():
        for r in results:
            all_text += f"{r.title}. {r.snippet}. "

    # 提取关键词
    keywords = TextAnalyzer.extract_keywords(all_text, 15)

    # 情感分析
    sentiment = SentimentAnalyzer.analyze(all_text)

    # 多角度分析
    all_perspectives = PerspectiveAnalyzer.analyze_perspectives(all_text)

    # 过滤指定维度
    if perspectives:
        all_perspectives = {k: v for k, v in all_perspectives.items() if k in perspectives}

    lines = [f"# {topic} 话题分析", ""]

    # 关键词云
    lines.append("## 核心关键词")
    lines.append(" | ".join([f"**{k}**({v})" for k, v in keywords[:10]]))
    lines.append("")

    # 情感
    emoji = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}
    lines.append(f"## 情感倾向 {emoji.get(sentiment['sentiment'], '⚪')}")
    lines.append(f"- 整体: {sentiment['sentiment'].upper()} ({sentiment['score']}/100)")
    lines.append(f"- 积极信号: {sentiment['positive_signals']} | 消极信号: {sentiment['negative_signals']}")
    lines.append("")

    # 各维度分析
    lines.append("## 多维度洞察")
    lines.append("")
    for perspective, data in all_perspectives.items():
        level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        lines.append(f"### {perspective.upper()} {level_emoji.get(data['level'], '⚪')}")
        lines.append(f"- 相关度: {data['relevance']*100:.0f}%")
        if data['keywords_found']:
            lines.append(f"- 关键信号: {', '.join(data['keywords_found'])}")

        # 根据相关度生成简单洞察
        if data['level'] == 'high':
            lines.append(f"- **洞察**: 该维度信息密集，是核心关注点")
        elif data['level'] == 'medium':
            lines.append(f"- **洞察**: 该维度有一定信息量，值得关注")
        else:
            lines.append(f"- **洞察**: 该维度信息较少，可能需要深入挖掘")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def generate_report(
    title: str,
    findings: str,
    report_type: str = "markdown",
) -> str:
    """报告生成 - 结构化调研报告

    基于研究发现生成结构化报告。

    Args:
        title: 报告标题
        findings: 研究发现内容（可以是之前的搜索结果、分析结论等）
        report_type: 报告格式 (markdown/json)
    """
    # 分析内容
    keywords = TextAnalyzer.extract_keywords(findings, 10)
    sentiment = SentimentAnalyzer.analyze(findings)
    perspectives = PerspectiveAnalyzer.analyze_perspectives(findings)

    if report_type == "json":
        import json
        return json.dumps({
            "title": title,
            "keywords": dict(keywords),
            "sentiment": sentiment,
            "perspectives": perspectives,
            "content": findings[:5000],
        }, ensure_ascii=False, indent=2)

    # Markdown报告
    lines = [f"# {title}", ""]
    lines.append("## 摘要")
    summary = TextAnalyzer.summarize_text(findings, 5)
    lines.append(summary)
    lines.append("")

    lines.append("## 关键词")
    lines.append(", ".join([f"**{k}**({v})" for k, v in keywords[:10]]))
    lines.append("")

    lines.append("## 情感分析")
    emoji = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}
    lines.append(f"- 倾向: {emoji.get(sentiment['sentiment'], '⚪')} {sentiment['sentiment'].upper()}")
    lines.append(f"- 评分: {sentiment['score']}/100")
    lines.append("")

    lines.append("## 多维度分析")
    for perspective, data in perspectives.items():
        level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        lines.append(f"- **{perspective}**: {level_emoji.get(data['level'], '⚪')} {data['level']} (相关度 {data['relevance']*100:.0f}%)")
    lines.append("")

    lines.append("## 详细内容")
    lines.append(findings[:8000])
    lines.append("")
    lines.append("> ⚠️ 本报告基于AI分析自动生成，仅供参考。")

    return "\n".join(lines)


# ========== 入口 ==========

def main():
    parser = argparse.ArgumentParser(description="Deep Research MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--path", default="/deep-research")

    args = parser.parse_args()

    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port, path=args.path)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
