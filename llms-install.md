# Deep Research MCP

多源深度调研MCP Server

## Claude Desktop

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

## Cursor

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

## Remote (Streamable HTTP)

```json
{
  "mcpServers": {
    "deep-research": {
      "url": "http://your-server:8080/deep-research"
    }
  }
}
```

## Windsurf

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

## 功能

- `deep_research` - 深度调研（搜索+抓取+分析+报告）
- `quick_search` - 快速多源搜索
- `search_news` - 新闻搜索
- `search_academic` - 学术搜索（arXiv）
- `analyze_topic` - 话题多角度分析
- `generate_report` - 结构化报告生成
