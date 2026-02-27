<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=170&section=header&text=AI%20Finance%20Agent&fontSize=52&fontAlignY=35&animation=twinkling&fontColor=ffffff&desc=Claude-Powered%20Stock%20Analysis%20with%20Autonomous%20Tool%20Calling&descAlignY=55&descSize=18" width="100%" />

[![Claude](https://img.shields.io/badge/Claude_Sonnet-Tool_Use-8B5CF6?style=for-the-badge&logo=anthropic&logoColor=white)](.)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](.)
[![FMP API](https://img.shields.io/badge/FMP-Real_Time_Data-0066CC?style=for-the-badge)](.)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Ask any stock question. Claude autonomously decides which tools to call, fetches real-time market data, and delivers structured analysis.**

</div>

---

## Why This Exists

Most "AI finance" projects are just prompt wrappers that hope the LLM's training data has the answer. This agent is fundamentally different: Claude has access to **5 real-time financial tools** and autonomously decides which combination to use based on your question.

Ask "Is NVIDIA overvalued?" and Claude calls `get_stock_price`, `get_company_fundamentals`, AND `get_stock_news` on its own, then synthesizes everything into actionable analysis. The agent reasons about what data it needs before fetching it.

---

## Architecture

```
User asks "Analyze NVDA"
        │
        ▼
FastAPI receives query
        │
        ▼
Claude analyzes the question (with 5 tool definitions)
        │
        ├──→ Decides: "I need price, fundamentals, and news"
        │    (autonomous tool selection)
        │
        ▼
Claude calls get_stock_price("NVDA")         → $128.34, +2.1%
Claude calls get_company_fundamentals("NVDA") → Semiconductor, 32K employees
Claude calls get_stock_news("NVDA")           → 5 latest articles
Claude calls get_price_history("NVDA")        → 1-month trend data
        │
        ▼
Claude synthesizes ALL real data into final analysis
        │
        ▼
Structured response with analysis + tool trace + cost metrics
```

**Key insight:** Claude decides the tool calls, not hardcoded logic. Simple questions use 1 tool. Complex analysis uses 3-4 tools. The agent adapts to query complexity.

---

## Available Tools

| Tool | What It Fetches | When Claude Uses It |
|------|----------------|---------------------|
| `get_stock_price` | Live price, change %, volume, market cap, 52-week range, moving averages | "How is X doing today?" |
| `get_company_fundamentals` | Company profile, sector, industry, CEO, employees, beta, description | "Tell me about X" "What does X do?" |
| `get_price_history` | Historical daily prices for any period (1d to 5y) with trend summary | "How has X performed this month?" |
| `get_stock_news` | 5 most recent news articles with titles, sources, and summaries | "What's happening with X?" |
| `compare_stocks` | Side-by-side comparison of up to 5 stocks on all key metrics | "Compare AAPL vs MSFT vs GOOGL" |

---

## How It Works

| Step | What Happens | Technology |
|------|-------------|------------|
| **1** | User types a financial question | HTML/JS frontend |
| **2** | Query sent to FastAPI backend | FastAPI |
| **3** | Claude receives query + 5 tool definitions | Anthropic Tool Use API |
| **4** | Claude autonomously selects which tools to call | Claude Sonnet reasoning |
| **5** | Tools execute and return real-time data | FMP Stable API |
| **6** | Claude may call MORE tools based on initial results | Multi-step agent loop |
| **7** | Claude synthesizes final analysis from all data | Structured output |
| **8** | Response returned with analysis + tool trace + cost | JSON response |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Claude native tool_use** | Not a function-calling wrapper. Claude sees all tools and reasons about which to call |
| **Multi-step agent loop** | Claude can call tools, review results, then decide to call more |
| **FMP Stable API** | Free tier with 250 req/day, works from cloud servers (unlike yfinance which gets 429'd) |
| **FastAPI over Flask** | Async support, automatic OpenAPI docs at /docs |
| **Stateless design** | No database. Each query is independent. Easy to scale |
| **Cost tracking per request** | Token counting + USD estimate shown in every response |

---

## Quick Start

```bash
git clone https://github.com/ajay-automates/ai-finance-agent.git
cd ai-finance-agent
pip install -r requirements.txt

export ANTHROPIC_API_KEY="your-key"
export FMP_API_KEY="your-key"    # Free at financialmodelingprep.com/developer
python main.py
# Open http://localhost:8000
```

### Deploy on Railway

1. Connect this repo to Railway
2. Set `ANTHROPIC_API_KEY` and `FMP_API_KEY` as environment variables
3. Deploy — Railway auto-detects Python via Procfile

---

## Example Queries

| Query | Tools Claude Calls |
|-------|-------------------|
| "What's AAPL's price?" | `get_stock_price` (1 tool) |
| "Full analysis of NVDA" | `get_stock_price` + `get_company_fundamentals` + `get_stock_news` + `get_price_history` (4 tools) |
| "Compare AAPL vs MSFT vs GOOGL" | `compare_stocks` + `get_stock_price` x3 (4 tools) |
| "How has TSLA performed over 6 months?" | `get_price_history` + `get_stock_price` (2 tools) |
| "What's the latest news on META?" | `get_stock_news` + `get_stock_price` (2 tools) |

---

## Project Structure

```
ai-finance-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Claude tool-calling agent with multi-step loop
│   └── tools.py          # 5 finance tools using FMP Stable API
├── templates/
│   └── index.html        # Dark-theme web UI with tool trace display
├── main.py               # FastAPI server + debug endpoint
├── requirements.txt
├── Procfile              # Railway deployment
├── .env.example
└── README.md
```

---

## What This Demonstrates

| AI Engineering Skill | Implementation |
|---------------------|----------------|
| **Tool Calling / Function Calling** | Claude's native tool_use with 5 custom tools |
| **Autonomous Agent Reasoning** | Claude decides which tools to call and in what order |
| **Multi-Step Agent Loop** | Agent calls tools, reviews, calls more tools if needed |
| **Structured Output** | Clean JSON responses with metrics and tool traces |
| **Real-Time API Integration** | Live market data via FMP Stable API |
| **Production Deployment** | FastAPI + Railway + error handling + cost monitoring |

---

## Tech Stack

`Python` `FastAPI` `Anthropic Claude` `Tool Use API` `FMP Stable API` `Jinja2` `Railway`

---

## Related Projects

| Project | Description |
|---------|-------------|
| [Multi-Agent Research Team](https://github.com/ajay-automates/multi-agent-research-team) | 4 CrewAI agents for content creation |
| [Agentic RAG Pipeline](https://github.com/ajay-automates/agentic-rag-pipeline) | Self-correcting RAG with hallucination detection |
| [AI Support Agent](https://github.com/ajay-automates/ai-support-agent) | RAG chatbot with LangSmith observability |

---

<div align="center">

**Built by [Ajay Kumar Reddy Nelavetla](https://github.com/ajay-automates)** · February 2026

*Real-time financial analysis powered by autonomous AI tool calling.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=100&section=footer" width="100%" />

</div>
