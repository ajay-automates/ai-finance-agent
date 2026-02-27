<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=170&section=header&text=AI%20Finance%20Agent&fontSize=52&fontAlignY=35&animation=twinkling&fontColor=ffffff&desc=Claude-Powered%20Stock%20Analysis%20with%20Autonomous%20Tool%20Calling&descAlignY=55&descSize=18" width="100%" />

[![Claude](https://img.shields.io/badge/Claude_Sonnet-Tool_Use-8B5CF6?style=for-the-badge&logo=anthropic&logoColor=white)](.)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](.)
[![Yahoo Finance](https://img.shields.io/badge/Yahoo_Finance-Real_Time-6001D2?style=for-the-badge&logo=yahoo&logoColor=white)](.)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![Railway](https://img.shields.io/badge/Railway-Deploy-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Ask any stock question. Claude autonomously decides which tools to call, fetches real-time data, and delivers structured analysis.**

</div>

---

## Why This Exists

Most "AI finance" projects are just prompt wrappers — they send your question to an LLM and hope the training data has the answer. This agent is fundamentally different: Claude has access to **5 real-time financial tools** and autonomously decides which combination to use based on your question.

Ask "Is NVIDIA overvalued?" and Claude calls `get_stock_price`, `get_company_fundamentals`, AND `get_analyst_recommendations` on its own — then synthesizes everything into actionable analysis. The agent reasons about what data it needs before fetching it.

---

## Architecture

```
User asks "Compare AAPL vs GOOGL"
        │
        ▼
FastAPI receives query
        │
        ▼
Claude analyzes the question
        │
        ├──→ Decides: "I need compare_stocks tool"
        │    (autonomous tool selection)
        │
        ▼
Claude calls compare_stocks(["AAPL", "GOOGL"])
        │
        ├──→ yfinance fetches real-time data for both
        │
        ▼
Claude receives raw data
        │
        ├──→ Decides: "I also need analyst data"
        │    (multi-step reasoning)
        │
        ▼
Claude calls get_analyst_recommendations("AAPL")
Claude calls get_analyst_recommendations("GOOGL")
        │
        ▼
Claude synthesizes ALL data into final analysis
        │
        ▼
Structured response with metrics + tool trace
```

**Key insight:** Claude decides the tool calls, not hardcoded logic. For "What's AAPL's price?" it calls 1 tool. For "Full analysis of NVDA" it calls 3-4 tools. The agent adapts to the complexity of the question.

---

## Available Tools

| Tool | What It Fetches | When Claude Uses It |
|------|----------------|---------------------|
| `get_stock_price` | Current price, change, volume, market cap | "How is X doing today?" |
| `get_company_fundamentals` | Revenue, margins, P/E, debt, valuation | "Is X overvalued?" "Financials of X" |
| `get_price_history` | Historical prices for any period (1d–5y) | "How has X performed this month?" |
| `get_analyst_recommendations` | Price targets, buy/sell ratings | "Should I buy X?" "What do analysts say?" |
| `compare_stocks` | Side-by-side comparison of up to 5 stocks | "Compare X vs Y" "Which is better?" |

---

## Quick Start

```bash
git clone https://github.com/ajay-automates/ai-finance-agent.git
cd ai-finance-agent
pip install -r requirements.txt

export ANTHROPIC_API_KEY="your-key"
python main.py
# Open http://localhost:8000
```

### Deploy on Railway

1. Connect this repo to Railway
2. Set `ANTHROPIC_API_KEY` as environment variable
3. Deploy — Railway auto-detects Python via Procfile

---

## Example Queries

| Query | Tools Claude Calls |
|-------|-------------------|
| "What's AAPL's price?" | `get_stock_price` (1 tool) |
| "Is NVDA overvalued?" | `get_stock_price` + `get_company_fundamentals` + `get_analyst_recommendations` (3 tools) |
| "Compare AAPL vs MSFT vs GOOGL" | `compare_stocks` + `get_analyst_recommendations` × 3 (4 tools) |
| "How has TSLA performed over 6 months?" | `get_price_history` + `get_stock_price` (2 tools) |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Claude tool_use (not function calling wrapper)** | Native tool_use API — Claude sees all tools and reasons about which to call |
| **Multi-step agent loop** | Claude can call tools, review results, then call MORE tools if needed |
| **yfinance over paid APIs** | Free, no API key needed, reliable for real-time data |
| **FastAPI over Flask** | Async support for concurrent requests, automatic OpenAPI docs |
| **No database** | Stateless design — each query is independent, easy to scale |
| **Cost tracking per request** | Token counting + USD estimate shown to user |

---

## Project Structure

```
ai-finance-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Claude tool-calling agent loop
│   └── tools.py          # 5 finance tools + definitions
├── templates/
│   └── index.html        # Clean dark-theme web UI
├── main.py               # FastAPI server
├── requirements.txt
├── Procfile              # Railway deployment
├── .env.example
└── README.md
```

---

## Tech Stack

`Python` `FastAPI` `Anthropic Claude` `Tool Use API` `yfinance` `Jinja2` `Railway` `Uvicorn`

---

## What This Demonstrates

| AI Engineering Skill | Implementation |
|---------------------|----------------|
| **Tool Calling / Function Calling** | Claude's native tool_use with 5 custom tools |
| **Autonomous Agent Reasoning** | Claude decides which tools to call and in what order |
| **Multi-Step Agent Loop** | Agent calls tools → reviews → calls more tools if needed |
| **Structured Output** | Clean JSON responses with metrics and tool traces |
| **Real-Time API Integration** | Live market data via yfinance |
| **Production Deployment** | FastAPI + Railway + error handling + cost monitoring |

---

## Related Projects

| Project | Description |
|---------|-------------|
| [AI Support Agent](https://github.com/ajay-automates/ai-support-agent) | RAG chatbot with LangSmith observability |
| [AI Code Review Bot](https://github.com/ajay-automates/ai-code-review-bot) | Automated PR reviews with Claude + GitHub Actions |
| [AI Voice Agent](https://github.com/ajay-automates/ai-voice-agent) | Real-time voice conversations with documents |

---

<div align="center">

**Built by [Ajay Kumar Reddy Nelavetla](https://github.com/ajay-automates)** · February 2026

*Real-time financial analysis powered by autonomous AI tool calling.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=100&section=footer" width="100%" />

</div>
