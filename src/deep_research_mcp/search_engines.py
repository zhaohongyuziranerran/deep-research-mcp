"""多源搜索引擎模块

支持:
- DuckDuckGo (免费，无需API Key)
- 网页抓取 (requests + BeautifulSoup)
- 新闻搜索聚合
- 学术搜索 (arXiv/Google Scholar)
"""

import asyncio
import re
import urllib.parse
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup


class SearchResult:
    """统一搜索结果格式"""
    def __init__(self, title: str, url: str, snippet: str, source: str, date: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.date = date

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "date": self.date,
        }


class DuckDuckGoSearch:
    """DuckDuckGo搜索（免费，无需API Key）"""

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """执行DuckDuckGo搜索"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                return [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="DuckDuckGo",
                    )
                    for r in results
                ]
        except Exception as e:
            # 降级：用DuckDuckGo HTML搜索
            return await self._html_search(query, max_results)

    async def _html_search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """DuckDuckGo HTML搜索降级方案"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for result in soup.select(".result")[:max_results]:
                    a = result.select_one(".result__a")
                    snippet_elem = result.select_one(".result__snippet")
                    if a and snippet_elem:
                        results.append(SearchResult(
                            title=a.get_text(strip=True),
                            url=a.get("href", ""),
                            snippet=snippet_elem.get_text(strip=True),
                            source="DuckDuckGo",
                        ))
                return results
        except Exception:
            return []

    async def search_news(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """DuckDuckGo新闻搜索"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = ddgs.news(query, max_results=max_results)
                return [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("body", ""),
                        source=f"News: {r.get('source', 'Unknown')}",
                        date=r.get("date", ""),
                    )
                    for r in results
                ]
        except Exception:
            return []


class WebScraper:
    """网页内容抓取"""

    async def fetch_page(self, url: str, max_length: int = 5000) -> str:
        """抓取网页正文内容"""
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                soup = BeautifulSoup(resp.text, "html.parser")

                # 移除脚本和样式
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                # 提取正文
                text = soup.get_text(separator="\n", strip=True)
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = "\n".join(lines)
                return text[:max_length] + ("..." if len(text) > max_length else "")
        except Exception as e:
            return f"抓取失败: {str(e)}"

    async def fetch_multiple(self, urls: List[str], max_length: int = 3000) -> Dict[str, str]:
        """并行抓取多个网页"""
        tasks = [self.fetch_page(url, max_length) for url in urls]
        contents = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            url: content if isinstance(content, str) else str(content)
            for url, content in zip(urls, contents)
        }


class AcademicSearch:
    """学术搜索"""

    async def search_arxiv(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """arXiv论文搜索"""
        try:
            url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_results}&sortBy=relevance"
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url)
                soup = BeautifulSoup(resp.text, "xml")
                results = []
                for entry in soup.find_all("entry"):
                    title = entry.find("title")
                    summary = entry.find("summary")
                    link = entry.find("link", {"rel": "alternate"})
                    published = entry.find("published")
                    if title and summary:
                        results.append(SearchResult(
                            title=title.get_text(strip=True),
                            url=link.get("href") if link else "",
                            snippet=summary.get_text(strip=True)[:500],
                            source="arXiv",
                            date=published.get_text(strip=True)[:10] if published else "",
                        ))
                return results
        except Exception:
            return []


class SearchAggregator:
    """搜索聚合器 - 统一接口调用多源搜索"""

    def __init__(self):
        self.ddg = DuckDuckGoSearch()
        self.scraper = WebScraper()
        self.academic = AcademicSearch()

    async def search_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_per_source: int = 10,
    ) -> Dict[str, List[SearchResult]]:
        """
        多源聚合搜索

        Args:
            query: 搜索查询
            sources: 搜索源列表 ["web", "news", "academic"]，默认全部
            max_per_source: 每源最大结果数
        """
        sources = sources or ["web", "news", "academic"]
        results = {}

        if "web" in sources:
            results["web"] = await self.ddg.search(query, max_per_source)
        if "news" in sources:
            results["news"] = await self.ddg.search_news(query, max_per_source)
        if "academic" in sources:
            results["academic"] = await self.academic.search_arxiv(query, max_per_source)

        return results

    async def deep_fetch(
        self,
        search_results: List[SearchResult],
        max_pages: int = 5,
        max_length: int = 3000,
    ) -> Dict[str, str]:
        """深度抓取搜索结果的前N个页面"""
        urls = [r.url for r in search_results[:max_pages] if r.url]
        return await self.scraper.fetch_multiple(urls, max_length)
