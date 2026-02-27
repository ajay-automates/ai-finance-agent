"""
Finance tools for the AI agent.
Uses Financial Modeling Prep API (free tier, 250 req/day).
Works reliably from cloud servers unlike yfinance.
Get your free API key at: https://financialmodelingprep.com/developer
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta

FMP_KEY = os.getenv("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com/api/v3"


def _fmp_get(endpoint, params=None):
    """Make a request to FMP API."""
    if not params:
        params = {}
    params["apikey"] = FMP_KEY
    try:
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
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
        "timestamp": q.get("timestamp") or datetime.now().isoformat()
    }


def get_company_fundamentals(ticker):
    """Get company financials: revenue, earnings, margins, P/E, debt."""
    profile = _fmp_get(f"profile/{ticker.upper()}")
    ratios = _fmp_get(f"ratios-ttm/{ticker.upper()}")
    metrics = _fmp_get(f"key-metrics-ttm/{ticker.upper()}")

    if isinstance(profile, dict) and "error" in profile:
        return profile

    p = profile[0] if isinstance(profile, list) and profile else {}
    r = ratios[0] if isinstance(ratios, list) and ratios else {}
    m = metrics[0] if isinstance(metrics, list) and metrics else {}

    return {
        "ticker": ticker.upper(),
        "name": p.get("companyName", "N/A"),
        "sector": p.get("sector", "N/A"),
        "industry": p.get("industry", "N/A"),
        "country": p.get("country", "N/A"),
        "employees": p.get("fullTimeEmployees"),
        "description": (p.get("description", "") or "")[:300],
        "financials": {
            "revenue_per_share": m.get("revenuePerShareTTM"),
            "net_income_per_share": m.get("netIncomePerShareTTM"),
            "gross_margin": round((r.get("grossProfitMarginTTM") or 0) * 100, 2),
            "operating_margin": round((r.get("operatingProfitMarginTTM") or 0) * 100, 2),
            "net_margin": round((r.get("netProfitMarginTTM") or 0) * 100, 2),
            "roe": round((r.get("returnOnEquityTTM") or 0) * 100, 2),
            "roa": round((r.get("returnOnAssetsTTM") or 0) * 100, 2),
        },
        "valuation": {
            "pe_ratio": r.get("peRatioTTM"),
            "forward_pe": p.get("forwardPE"),
            "peg_ratio": r.get("pegRatioTTM"),
            "price_to_book": r.get("priceToBookRatioTTM"),
            "price_to_sales": r.get("priceToSalesRatioTTM"),
            "ev_to_ebitda": m.get("enterpriseValueOverEBITDATTM"),
            "market_cap": p.get("mktCap"),
        },
        "dividends": {
            "dividend_yield": round((r.get("dividendYielTTM") or 0) * 100, 2),
            "payout_ratio": round((r.get("payoutRatioTTM") or 0) * 100, 2),
        },
        "debt": {
            "debt_to_equity": r.get("debtEquityRatioTTM"),
            "current_ratio": r.get("currentRatioTTM"),
            "cash_per_share": m.get("cashPerShareTTM"),
        }
    }


def get_price_history(ticker, period="1mo"):
    """Get historical price data for trend analysis."""
    period_map = {
        "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
        "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
    }
    days = period_map.get(period, 30)
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    data = _fmp_get(f"historical-price-full/{ticker.upper()}", {
        "from": start, "to": end
    })

    if isinstance(data, dict) and "error" in data:
        return data

    historical = data.get("historical", []) if isinstance(data, dict) else []
    if not historical:
        return {"error": f"No history for '{ticker}'"}

    historical.reverse()
    prices = [{
        "date": d["date"],
        "open": d.get("open"),
        "high": d.get("high"),
        "low": d.get("low"),
        "close": d.get("close"),
        "volume": d.get("volume")
    } for d in historical]

    closes = [p["close"] for p in prices if p["close"]]
    return {
        "ticker": ticker.upper(),
        "period": period,
        "data_points": len(prices),
        "prices": prices[-20:] if len(prices) > 20 else prices,
        "summary": {
            "start_price": closes[0] if closes else None,
            "end_price": closes[-1] if closes else None,
            "change_percent": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2) if len(closes) >= 2 else 0,
            "high": max(closes) if closes else None,
            "low": min(closes) if closes else None,
            "avg_volume": int(sum(p["volume"] for p in prices if p["volume"]) / max(len(prices), 1))
        }
    }


def get_analyst_recommendations(ticker):
    """Get analyst ratings, price targets, and recommendations."""
    consensus = _fmp_get(f"analyst-estimates/{ticker.upper()}", {"limit": 1})
    targets = _fmp_get(f"price-target-consensus/{ticker.upper()}")
    grade = _fmp_get(f"grade/{ticker.upper()}", {"limit": 5})

    t = targets[0] if isinstance(targets, list) and targets else (targets if isinstance(targets, dict) else {})

    recent_grades = []
    if isinstance(grade, list):
        for g in grade[:5]:
            recent_grades.append({
                "firm": g.get("gradingCompany", "N/A"),
                "action": g.get("newGrade", "N/A"),
                "date": g.get("date", "N/A")
            })

    return {
        "ticker": ticker.upper(),
        "target_prices": {
            "target_high": t.get("targetHigh"),
            "target_low": t.get("targetLow"),
            "target_mean": t.get("targetConsensus"),
            "target_median": t.get("targetMedian"),
        },
        "recent_analyst_grades": recent_grades
    }


def compare_stocks(tickers):
    """Compare multiple stocks side by side on key metrics."""
    comparisons = []
    for ticker in tickers[:5]:
        data = _fmp_get(f"quote/{ticker.upper()}")
        if isinstance(data, list) and data:
            q = data[0]
            comparisons.append({
                "ticker": ticker.upper(),
                "name": q.get("name", "N/A"),
                "price": q.get("price"),
                "change_percent": q.get("changesPercentage"),
                "market_cap": q.get("marketCap"),
                "pe_ratio": q.get("pe"),
                "eps": q.get("eps"),
                "volume": q.get("volume"),
                "year_high": q.get("yearHigh"),
                "year_low": q.get("yearLow"),
            })
        time.sleep(0.3)

    return {
        "stocks_compared": len(comparisons),
        "comparisons": comparisons
    }


TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price, daily change, volume, and key trading metrics for a given ticker symbol.",
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
        "description": "Get detailed company financials including revenue, earnings, margins, P/E ratio, debt levels, and valuation metrics.",
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
        "description": "Get historical price data for trend analysis. Supports periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y.",
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
        "name": "get_analyst_recommendations",
        "description": "Get analyst ratings, price targets, and buy/sell/hold recommendations.",
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
        "description": "Compare multiple stocks side by side on key metrics like price, market cap, P/E ratio, and more.",
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
    "get_analyst_recommendations": lambda args: get_analyst_recommendations(args["ticker"]),
    "compare_stocks": lambda args: compare_stocks(args["tickers"]),
}
