"""分析器模块

提供文本分析、信息提取、观点聚合等功能
"""

import re
from typing import List, Dict
from collections import Counter


class TextAnalyzer:
    """文本分析器"""

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[tuple]:
        """提取关键词（简单TF统计）"""
        # 清理文本
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', text.lower())
        # 停用词
        stopwords = set([
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "may", "new", "now", "old", "see", "two", "who", "boy", "did", "she", "use", "her", "way", "many", "oil", "sit", "set", "run", "eat", "far", "sea", "eye", "ago", "off", "too", "any", "say", "man", "try", "ask", "end", "why", "let", "put", "say", "she", "try", "way", "own", "say", "too", "old", "tell", "very", "when", "much", "would", "there", "their", "what", "said", "have", "each", "which", "will", "about", "could", "other", "after", "first", "never", "these", "think", "where", "being", "every", "great", "might", "shall", "still", "those", "while", "this", "that", "with", "from", "they", "know", "want", "been", "good", "much", "some", "time", "than", "them", "well", "were",
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "我们", "来", "这个", "可以", "为", "什么", "想", "现在", "就是", "它", "如果", "可能", "但", "因为", "或者", "这里", "那里", "然后", "之后", "之前", "已经", "开始", "进行", "使用", "通过", "作为", "需要", "成为", "包括", "根据", "由于", "以及", "等等"
        ])
        filtered = [w for w in words if w not in stopwords and len(w) > 1]
        return Counter(filtered).most_common(top_n)

    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """简单实体提取（基于大写词和引号内容）"""
        entities = {
            "organizations": re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b', text),
            "quoted": re.findall(r'[""]([^""]+)[""]', text),
            "numbers": re.findall(r'\$?[\d,]+(?:\.\d+)?(?:\s*%|\s*billion|\s*million|\s*万|\s*亿)?', text),
        }
        return entities

    @staticmethod
    def summarize_text(text: str, max_sentences: int = 5) -> str:
        """简单文本摘要（基于句子位置和关键词）"""
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        if len(sentences) <= max_sentences:
            return text

        # 提取关键词
        keywords = dict(TextAnalyzer.extract_keywords(text, 20))

        # 给每个句子打分
        def score_sentence(sent):
            words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', sent.lower())
            return sum(keywords.get(w, 0) for w in words) + (1 if sent == sentences[0] else 0)

        scored = [(i, score_sentence(s)) for i, s in enumerate(sentences)]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_indices = sorted([i for i, _ in scored[:max_sentences]])
        return " ".join(sentences[i] for i in top_indices)


class SentimentAnalyzer:
    """简单情感分析"""

    POSITIVE = ["good", "great", "excellent", "positive", "strong", "growth", "increase", "success", "benefit", "advantage", "opportunity", "improve", "boost", "rise", "gain", "profit", "win", "best", "leading", "innovative", "promising", "optimistic", "bullish", "好", "优秀", "增长", "成功", "机会", "优势", "提升", "盈利", "乐观", "积极", "看好"]
    NEGATIVE = ["bad", "poor", "negative", "weak", "decline", "decrease", "fail", "risk", "disadvantage", "problem", "issue", "concern", "drop", "fall", "loss", "lose", "worst", "struggle", "crisis", "threat", "bearish", "pessimistic", "差", "下滑", "失败", "风险", "问题", "亏损", "下降", "悲观", "担忧", "威胁"]

    @staticmethod
    def analyze(text: str) -> dict:
        """分析文本情感"""
        text_lower = text.lower()
        pos_count = sum(1 for w in SentimentAnalyzer.POSITIVE if w in text_lower)
        neg_count = sum(1 for w in SentimentAnalyzer.NEGATIVE if w in text_lower)
        total = pos_count + neg_count

        if total == 0:
            sentiment = "neutral"
            score = 50
        else:
            score = int((pos_count / total) * 100)
            if score >= 60:
                sentiment = "positive"
            elif score <= 40:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_signals": pos_count,
            "negative_signals": neg_count,
        }


class PerspectiveAnalyzer:
    """多角度分析器"""

    PERSPECTIVES = {
        "market": ["market", "industry", "sector", "competition", "demand", "supply", "price", "growth", "trend", "market share", "市场规模", "行业", "竞争", "需求", "趋势"],
        "financial": ["revenue", "profit", "cost", "investment", "funding", "valuation", "margin", "roi", "revenue", "盈利", "成本", "投资", "估值", "收入"],
        "technology": ["technology", "innovation", "patent", "r&d", "ai", "algorithm", "platform", "tech", "技术", "创新", "专利", "研发", "算法"],
        "policy": ["policy", "regulation", "law", "government", "compliance", "legal", "政策", "法规", "监管", "政府", "合规"],
        "risk": ["risk", "challenge", "threat", "uncertainty", "crisis", "risk", "风险", "挑战", "威胁", "不确定性", "危机"],
    }

    @staticmethod
    def analyze_perspectives(text: str) -> Dict[str, dict]:
        """从多角度分析文本"""
        text_lower = text.lower()
        results = {}
        for perspective, keywords in PerspectiveAnalyzer.PERSPECTIVES.items():
            matches = [k for k in keywords if k in text_lower]
            relevance = len(matches) / len(keywords)
            results[perspective] = {
                "relevance": round(relevance, 2),
                "keywords_found": matches[:5],
                "level": "high" if relevance > 0.3 else "medium" if relevance > 0.1 else "low",
            }
        return results
