"""
Finance tools for the AI agent.
Uses Financial Modeling Prep STABLE API (new endpoints as of Aug 2025).
Get your free API key at: https://financialmodelingprep.com/developer
"""

import os
import time
import requests
from datetime import datetime, timedelta

FMP_KEY = os.getenv("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com/stable"


def _fmp_get(endpoint, params=None):
    """Make a request to FMP stable API."""
    if not FMP_KEY:
        return {"error": "FMP_API_KEY not set"}
    if not params:
        params = {}
    params["apikey"] = FMP_KEY
    try:
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=15)
        if r.status_code == 403:
            return {"error": f"FMP 403 on {endpoint}: {r.text[:200]}"}
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "Error Message" in data:
            return {"error": data["Error Message"]}
        return data
    except Exception as e:
        return {"error": str(e)}


def get_stock_price(ticker):
    """Get current stock price, change, and key trading metrics."""
    data = _fmp_get("quote", {"symbol": ticker.upper()})
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"error": f"No data found for '{ticker}'"}

    q = data[0]
    return {
        "ticker": ticker.upper(),
        "name": q.get("name", "N/A"),
        "price": q.get("price"),
        "change": q.get("change"),
        "change_percent": q.get("changePercentage"),
        "day_high": q.get("dayHigh"),
        "day_low": q.get("dayLow"),
        "year_high": q.get("yearHigh"),
        "year_low": q.get("yearLow"),
        "volume": q.get("volume"),
        "market_cap": q.get("marketCap"),
        "open": q.get("open"),
        "previous_close": q.get("previousClose"),
        "exchange": q.get("exchange", "N/A"),
        "fifty_day_avg": q.get("priceAvg50"),
        "two_hundred_day_avg": q.get("priceAvg200"),
    }


def get_company_fundamentals(ticker):
    """Get company profile."""
    data = _fmp_get("profile", {"symbol": ticker.upper()})
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"error": f"No profile for '{ticker}'"}

    p = data[0]
    return {
        "ticker": ticker.upper(),
        "name": p.get("companyName", "N/A"),
        "sector": p.get("sector", "N/A"),
        "industry": p.get("industry", "N/A"),
        "country": p.get("country", "N/A"),
        "exchange": p.get("exchangeShortName", "N/A"),
        "employees": p.get("fullTimeEmployees"),
        "ceo": p.get("ceo", "N/A"),
        "website": p.get("website", "N/A"),
        "description": (p.get("description", "") or "")[:500],
        "ipo_date": p.get("ipoDate"),
        "market_cap": p.get("mktCap"),
        "price": p.get("price"),
        "beta": p.get("beta"),
        "last_dividend": p.get("lastDiv"),
        "range": p.get("range"),
    }


def get_price_history(ticker, period="1mo"):
    """Get historical prices."""
    period_map = {
        "1d": 2, "5d": 7, "1mo": 35, "3mo": 95,
        "6mo": 185, "1y": 370, "2y": 740, "5y": 1830
    }
    days = period_map.get(period, 35)
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    data = _fmp_get("historical-price-full", {
        "symbol": ticker.upper(), "from": start, "to": end
    })

    if isinstance(data, dict) and "error" in data:
        return data

    historical = data.get("historical", []) if isinstance(data, dict) else []
    if not historical:
        return {"error": f"No history for '{ticker}'"}

    historical.reverse()
    prices = [{"date": d.get("date"), "close": d.get("close"), "volume": d.get("volume")} for d in historical]
    closes = [p["close"] for p in prices if p["close"] is not None]

    if not closes:
        return {"error": f"No closing prices for '{ticker}'"}

    return {
        "ticker": ticker.upper(),
        "period": period,
        "data_points": len(prices),
        "recent_prices": prices[-10:],
        "summary": {
            "start_price": closes[0],
            "end_price": closes[-1],
            "change_percent": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2),
            "period_high": round(max(closes), 2),
            "period_low": round(min(closes), 2),
        }
    }


def get_stock_news(ticker):
    """Get latest news."""
    data = _fmp_get("stock-news", {"symbol": ticker.upper(), "limit": 5})
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list):
        return {"ticker": ticker.upper(), "news": [], "message": "No recent news"}

    articles = []
    for a in data[:5]:
        articles.append({
            "title": a.get("title", "N/A"),
            "source": a.get("site", "N/A"),
            "date": a.get("publishedDate", "N/A"),
            "summary": (a.get("text", "") or "")[:200],
        })

    return {"ticker": ticker.upper(), "news_count": len(articles), "articles": articles}


def compare_stocks(tickers):
    """Compare stocks side by side."""
    comparisons = []
    for t in tickers[:5]:
        data = _fmp_get("quote", {"symbol": t.upper()})
        if isinstance(data, list) and data:
            q = data[0]
            comparisons.append({
                "ticker": q.get("symbol", t.upper()),
                "name": q.get("name", "N/A"),
                "price": q.get("price"),
                "change_percent": q.get("changePercentage"),
                "market_cap": q.get("marketCap"),
                "volume": q.get("volume"),
                "year_high": q.get("yearHigh"),
                "year_low": q.get("yearLow"),
            })
        time.sleep(0.2)

    return {"stocks_compared": len(comparisons), "comparisons": comparisons}


TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Get current stock price, daily change, volume, market cap, 52-week range, and moving averages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, GOOGL, NVDA)"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_company_fundamentals",
        "description": "Get company profile: sector, industry, CEO, employees, description, market cap, beta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_price_history",
        "description": "Get historical daily prices. Supports: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "period": {"type": "string", "description": "Time period", "default": "1mo"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_stock_news",
        "description": "Get 5 most recent news articles about a stock for sentiment analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "compare_stocks",
        "description": "Compare up to 5 stocks on price, market cap, volume, and 52-week range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {"type": "array", "items": {"type": "string"}, "description": "Ticker symbols to compare (max 5)"}
            },
            "required": ["tickers"]
        }
    }
]

TOOL_FUNCTIONS = {
    "get_stock_price": lambda args: get_stock_price(args["ticker"]),
    "get_company_fundamentals": lambda args: get_company_fundamentals(args["ticker"]),
    "get_price_history": lambda args: get_price_history(args["ticker"], args.get("period", "1mo")),
    "get_stock_news": lambda args: get_stock_news(args["ticker"]),
    "compare_stocks": lambda args: compare_stocks(args["tickers"]),
}
