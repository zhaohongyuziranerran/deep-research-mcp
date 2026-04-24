# Deep Research MCP

多源深度调研MCP Server - 智能搜索+分析+报告生成

覆盖 **Web搜索 / 新闻 / 学术论文** 多源信息聚合，支持中文和英文内容分析。

## 功能

| 工具 | 功能 | 适用场景 |
|------|------|----------|
| `deep_research` | 深度调研（搜索+抓取+分析+报告） | 行业研究、竞品分析、市场趋势 |
| `quick_search` | 快速多源搜索 | 快速信息核实、热点追踪 |
| `search_news` | 新闻搜索 | 时效性事件、行业动态 |
| `search_academic` | 学术搜索（arXiv） | 技术调研、论文综述 |
| `analyze_topic` | 话题多角度分析 | 投资前分析、风险评估 |
| `generate_report` | 结构化报告生成 | Markdown/JSON格式输出 |

## 安装

```bash
pip install deep-research-mcp
```

## 使用

### Claude Desktop

```json
{
  "mcpServers": {
    "deep-research": {
      "command": "python",
      "args": ["-m", "deep_research_mcp"]
    }
  }
}
```

### 远程部署（Streamable HTTP）

```bash
deep-research-mcp --transport http --port 8080 --path /deep-research
```

客户端配置：
```json
{
  "mcpServers": {
    "deep-research": {
      "url": "http://your-server:8080/deep-research"
    }
  }
}
```

## 工具示例

### 深度调研
```
主题: "AI Agent市场趋势2026"
深度: comprehensive
信息源: ["web", "news", "academic"]
```

### 话题分析
```
话题: "人形机器人产业化"
维度: ["market", "technology", "risk"]
```

## 技术栈

- **FastMCP 3.x** - MCP协议框架
- **DuckDuckGo Search** - 免费Web/新闻搜索
- **arXiv API** - 学术论文搜索
- **BeautifulSoup** - 网页内容抓取
- **httpx** - 异步HTTP客户端

## 数据来源

- Web搜索: DuckDuckGo（免费，无需API Key）
- 新闻: DuckDuckGo News
- 学术: arXiv.org

## 定价

| 层级 | 价格 | 限制 |
|------|------|------|
| **Free** | $0 | 20次调研/天 |
| **Pro** | $19/月 | 200次调研/天 + 优先搜索 |
| **Enterprise** | 定制 | 无限 + 私有部署 |

## License

MIT
