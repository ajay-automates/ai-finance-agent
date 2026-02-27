"""
Finance tools for the AI agent.
Uses Financial Modeling Prep API (free tier only).
Free endpoints: /quote, /profile, /historical-price-full, /stock_news
Get your free API key at: https://financialmodelingprep.com/developer
"""

import os
import time
import requests
from datetime import datetime, timedelta

FMP_KEY = os.getenv("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com/api/v3"


def _fmp_get(endpoint, params=None):
    """Make a request to FMP API with error handling."""
    if not FMP_KEY:
        return {"error": "FMP_API_KEY not set. Get a free key at financialmodelingprep.com/developer"}
    if not params:
        params = {}
    params["apikey"] = FMP_KEY
    try:
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=15)
        if r.status_code == 403:
            return {"error": "FMP API access denied. Check your API key or endpoint access."}
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "Error Message" in data:
            return {"error": data["Error Message"]}
        return data
    except Exception as e:
        return {"error": str(e)}


def get_stock_price(ticker):
    """Get current stock price, change, and key trading metrics."""
    data = _fmp_get(f"quote/{ticker.upper()}")
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"error": f"No data found for ticker '{ticker}'"}

    q = data[0]
    return {
        "ticker": ticker.upper(),
        "name": q.get("name", "N/A"),
        "price": q.get("price"),
        "change": q.get("change"),
        "change_percent": q.get("changesPercentage"),
        "day_high": q.get("dayHigh"),
        "day_low": q.get("dayLow"),
        "year_high": q.get("yearHigh"),
        "year_low": q.get("yearLow"),
        "volume": q.get("volume"),
        "avg_volume": q.get("avgVolume"),
        "market_cap": q.get("marketCap"),
        "pe_ratio": q.get("pe"),
        "eps": q.get("eps"),
        "open": q.get("open"),
        "previous_close": q.get("previousClose"),
        "exchange": q.get("exchange", "N/A"),
        "shares_outstanding": q.get("sharesOutstanding"),
        "fifty_day_avg": q.get("priceAvg50"),
        "two_hundred_day_avg": q.get("priceAvg200"),
    }


def get_company_fundamentals(ticker):
    """Get company profile with financials from the free /profile endpoint."""
    data = _fmp_get(f"profile/{ticker.upper()}")
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"error": f"No profile data for '{ticker}'"}

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
        "financials": {
            "market_cap": p.get("mktCap"),
            "price": p.get("price"),
            "beta": p.get("beta"),
            "volume_avg": p.get("volAvg"),
            "last_dividend": p.get("lastDiv"),
            "range": p.get("range"),
        },
        "is_etf": p.get("isEtf", False),
        "is_actively_trading": p.get("isActivelyTrading", True),
    }


def get_price_history(ticker, period="1mo"):
    """Get historical price data for trend analysis (free endpoint)."""
    period_map = {
        "1d": 2, "5d": 7, "1mo": 35, "3mo": 95,
        "6mo": 185, "1y": 370, "2y": 740, "5y": 1830
    }
    days = period_map.get(period, 35)
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    data = _fmp_get(f"historical-price-full/{ticker.upper()}", {
        "from": start, "to": end
    })

    if isinstance(data, dict) and "error" in data:
        return data

    historical = data.get("historical", []) if isinstance(data, dict) else []
    if not historical:
        return {"error": f"No price history for '{ticker}'"}

    historical.reverse()

    prices = []
    for d in historical:
        prices.append({
            "date": d.get("date"),
            "open": d.get("open"),
            "high": d.get("high"),
            "low": d.get("low"),
            "close": d.get("close"),
            "volume": d.get("volume"),
            "change_percent": d.get("changePercent"),
        })

    closes = [p["close"] for p in prices if p["close"] is not None]
    if not closes:
        return {"error": f"No valid closing prices for '{ticker}'"}

    return {
        "ticker": ticker.upper(),
        "period": period,
        "data_points": len(prices),
        "prices": prices[-15:],
        "summary": {
            "start_price": closes[0],
            "end_price": closes[-1],
            "change_percent": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2),
            "period_high": round(max(closes), 2),
            "period_low": round(min(closes), 2),
            "avg_volume": int(sum(p["volume"] for p in prices if p["volume"]) / max(len(prices), 1))
        }
    }


def get_stock_news(ticker):
    """Get latest news for a stock (free endpoint)."""
    data = _fmp_get(f"stock_news", {"tickers": ticker.upper(), "limit": 5})
    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list):
        return {"ticker": ticker.upper(), "news": [], "message": "No recent news found"}

    articles = []
    for article in data[:5]:
        articles.append({
            "title": article.get("title", "N/A"),
            "source": article.get("site", "N/A"),
            "date": article.get("publishedDate", "N/A"),
            "summary": (article.get("text", "") or "")[:200],
            "url": article.get("url", ""),
        })

    return {
        "ticker": ticker.upper(),
        "news_count": len(articles),
        "articles": articles
    }


def compare_stocks(tickers):
    """Compare multiple stocks side by side using the free /quote endpoint."""
    ticker_str = ",".join([t.upper() for t in tickers[:5]])
    data = _fmp_get(f"quote/{ticker_str}")

    if isinstance(data, dict) and "error" in data:
        return data
    if not data or not isinstance(data, list):
        return {"error": "No data returned for comparison"}

    comparisons = []
    for q in data:
        comparisons.append({
            "ticker": q.get("symbol", "N/A"),
            "name": q.get("name", "N/A"),
            "price": q.get("price"),
            "change_percent": q.get("changesPercentage"),
            "market_cap": q.get("marketCap"),
            "pe_ratio": q.get("pe"),
            "eps": q.get("eps"),
            "volume": q.get("volume"),
            "avg_volume": q.get("avgVolume"),
            "year_high": q.get("yearHigh"),
            "year_low": q.get("yearLow"),
            "fifty_day_avg": q.get("priceAvg50"),
            "two_hundred_day_avg": q.get("priceAvg200"),
        })

    return {
        "stocks_compared": len(comparisons),
        "comparisons": comparisons
    }


TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Get current stock price, daily change, volume, market cap, P/E, EPS, 52-week range, and moving averages for a ticker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, GOOGL, NVDA, TSLA)"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_company_fundamentals",
        "description": "Get company profile: sector, industry, CEO, employees, description, market cap, beta, and key business info.",
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
        "description": "Get historical daily prices for trend analysis. Supports: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "period": {"type": "string", "description": "Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y", "default": "1mo"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_stock_news",
        "description": "Get the 5 most recent news articles about a stock. Use for sentiment and recent developments.",
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
        "description": "Compare up to 5 stocks side by side on price, market cap, P/E, EPS, volume, and 52-week range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {"type": "array", "items": {"type": "string"}, "description": "List of ticker symbols to compare (max 5)"}
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
