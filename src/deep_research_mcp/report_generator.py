"""报告生成器

生成结构化调研报告（Markdown格式）
"""

from typing import List, Dict
from .analyzers import TextAnalyzer, SentimentAnalyzer, PerspectiveAnalyzer


class ReportGenerator:
    """调研报告生成器"""

    @staticmethod
    def generate_research_report(
        topic: str,
        search_results: Dict[str, List],
        fetched_contents: Dict[str, str],
        depth: str = "standard",
    ) -> str:
        """
        生成深度调研报告

        Args:
            topic: 调研主题
            search_results: 多源搜索结果 {source: [SearchResult]}
            fetched_contents: 抓取的页面内容 {url: content}
            depth: 报告深度 (brief/standard/comprehensive)
        """
        # 合并所有文本用于分析
        all_text = ""
        for source, results in search_results.items():
            for r in results:
                all_text += f"{r.title}. {r.snippet}. "
        for content in fetched_contents.values():
            if not content.startswith("抓取失败"):
                all_text += content[:1000] + " "

        # 分析
        keywords = TextAnalyzer.extract_keywords(all_text, 15)
        sentiment = SentimentAnalyzer.analyze(all_text)
        perspectives = PerspectiveAnalyzer.analyze_perspectives(all_text)

        lines = []
        lines.append(f"# {topic} 深度调研报告")
        lines.append("")
        lines.append(f"> 调研深度: {depth} | 信息源: {len(search_results)}类 | 页面分析: {len(fetched_contents)}篇")
        lines.append("")

        # 执行摘要
        lines.append("## 执行摘要")
        lines.append("")
        summary = TextAnalyzer.summarize_text(all_text, 5)
        lines.append(summary)
        lines.append("")

        # 情感倾向
        emoji_map = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}
        lines.append(f"**整体情感倾向**: {emoji_map.get(sentiment['sentiment'], '⚪')} {sentiment['sentiment'].upper()} ({sentiment['score']}/100)")
        lines.append(f"- 积极信号: {sentiment['positive_signals']} | 消极信号: {sentiment['negative_signals']}")
        lines.append("")

        # 核心关键词
        lines.append("## 核心关键词")
        lines.append("")
        lines.append(" | ".join([f"**{k}**({v})" for k, v in keywords[:10]]))
        lines.append("")

        # 多维度分析
        lines.append("## 多维度分析")
        lines.append("")
        for perspective, data in perspectives.items():
            level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            lines.append(f"### {perspective.upper()} ({level_emoji.get(data['level'], '⚪')} {data['level']})")
            lines.append(f"- 相关度: {data['relevance']*100:.0f}%")
            if data['keywords_found']:
                lines.append(f"- 关键信号: {', '.join(data['keywords_found'])}")
            lines.append("")

        # 搜索结果汇总
        lines.append("## 信息源汇总")
        lines.append("")
        for source, results in search_results.items():
            lines.append(f"### {source.upper()} ({len(results)}条)")
            for i, r in enumerate(results[:5], 1):
                lines.append(f"{i}. **[{r.title}]({r.url})**")
                lines.append(f"   - {r.snippet[:200]}...")
                if r.date:
                    lines.append(f"   - 日期: {r.date}")
                lines.append("")

        # 深度页面分析
        if fetched_contents:
            lines.append("## 关键页面分析")
            lines.append("")
            for url, content in list(fetched_contents.items())[:3]:
                if not content.startswith("抓取失败"):
                    lines.append(f"### {url}")
                    lines.append(content[:800])
                    lines.append("")

        # 结论与建议
        lines.append("## 结论与建议")
        lines.append("")
        # 根据情感和多维度分析生成建议
        high_perspectives = [p for p, d in perspectives.items() if d["level"] == "high"]
        if high_perspectives:
            lines.append(f"**重点关注领域**: {', '.join(high_perspectives)}")
        if sentiment["sentiment"] == "positive":
            lines.append("**整体判断**: 信息面偏积极，建议持续关注相关动态。")
        elif sentiment["sentiment"] == "negative":
            lines.append("**整体判断**: 信息面偏谨慎，建议深入评估风险因素。")
        else:
            lines.append("**整体判断**: 信息面中性，建议持续跟踪多维度信号。")
        lines.append("")
        lines.append("> ⚠️ 本报告基于公开信息自动生成，仅供参考，不构成投资或决策建议。")

        return "\n".join(lines)

    @staticmethod
    def generate_comparison_report(
        topic: str,
        items: List[str],
        item_results: Dict[str, Dict],
    ) -> str:
        """生成对比分析报告"""
        lines = []
        lines.append(f"# {topic} 对比分析报告")
        lines.append("")
        lines.append(f"对比对象: {', '.join(items)}")
        lines.append("")

        # 对比表格
        lines.append("## 关键指标对比")
        lines.append("")
        lines.append("| 维度 | " + " | ".join(items) + " |")
        lines.append("|------|" + "|".join(["------"] * len(items)) + "|")

        # 情感对比
        sentiment_row = "| 情感倾向 |"
        for item in items:
            s = item_results.get(item, {}).get("sentiment", {})
            sentiment_row += f" {s.get('sentiment', 'N/A')} ({s.get('score', 0)}) |"
        lines.append(sentiment_row)

        # 关键词对比
        for item in items:
            keywords = item_results.get(item, {}).get("keywords", [])
            lines.append(f"\n### {item} 关键词")
            lines.append(", ".join([f"{k}({v})" for k, v in keywords[:10]]))

        lines.append("")
        lines.append("> ⚠️ 对比报告基于公开信息自动生成，仅供参考。")

        return "\n".join(lines)
