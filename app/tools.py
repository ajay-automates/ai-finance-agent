"""
Finance tools for the AI agent.
Uses yfinance (free, no API key) for real-time market data.
"""

import yfinance as yf
from datetime import datetime, timedelta
import json


def get_stock_price(ticker: str) -> dict:
    """Get current stock price, change, and key trading metrics."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="5d")

        if hist.empty:
            return {"error": f"No data found for ticker '{ticker}'"}

        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = current - prev
        change_pct = (change / prev) * 100

        return {
            "ticker": ticker.upper(),
            "price": round(current, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "day_high": round(hist['High'].iloc[-1], 2),
            "day_low": round(hist['Low'].iloc[-1], 2),
            "volume": int(hist['Volume'].iloc[-1]),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "N/A"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


def get_company_fundamentals(ticker: str) -> dict:
    """Get company financials: revenue, earnings, margins, P/E, debt."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "employees": info.get("fullTimeEmployees"),
            "financials": {
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "gross_margins": round(info.get("grossMargins", 0) * 100, 2),
                "operating_margins": round(info.get("operatingMargins", 0) * 100, 2),
                "profit_margins": round(info.get("profitMargins", 0) * 100, 2),
                "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 2),
                "earnings_growth": round(info.get("earningsGrowth", 0) * 100, 2) if info.get("earningsGrowth") else None,
            },
            "valuation": {
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "enterprise_value": info.get("enterpriseValue"),
                "ev_to_ebitda": info.get("enterpriseToEbitda"),
            },
            "dividends": {
                "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
                "payout_ratio": round(info.get("payoutRatio", 0) * 100, 2) if info.get("payoutRatio") else 0,
            },
            "debt": {
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
            }
        }
    except Exception as e:
        return {"error": str(e)}


def get_price_history(ticker: str, period: str = "1mo") -> dict:
    """Get historical price data for charting and trend analysis."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No history for '{ticker}'"}

        prices = []
        for date, row in hist.iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })

        closes = [p["close"] for p in prices]
        return {
            "ticker": ticker.upper(),
            "period": period,
            "data_points": len(prices),
            "prices": prices,
            "summary": {
                "start_price": closes[0],
                "end_price": closes[-1],
                "change_percent": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2),
                "high": max(closes),
                "low": min(closes),
                "avg_volume": int(sum(p["volume"] for p in prices) / len(prices))
            }
        }
    except Exception as e:
        return {"error": str(e)}


def get_analyst_recommendations(ticker: str) -> dict:
    """Get analyst ratings, price targets, and recommendations."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        recs = stock.recommendations
        recent_recs = []
        if recs is not None and not recs.empty:
            recent = recs.tail(10)
            for _, row in recent.iterrows():
                rec = {}
                for col in recent.columns:
                    val = row[col]
                    if hasattr(val, 'isoformat'):
                        rec[col] = val.isoformat()
                    else:
                        rec[str(col)] = str(val)
                recent_recs.append(rec)

        return {
            "ticker": ticker.upper(),
            "target_prices": {
                "current_price": info.get("currentPrice"),
                "target_high": info.get("targetHighPrice"),
                "target_low": info.get("targetLowPrice"),
                "target_mean": info.get("targetMeanPrice"),
                "target_median": info.get("targetMedianPrice"),
                "number_of_analysts": info.get("numberOfAnalystOpinions"),
            },
            "recommendation": info.get("recommendationKey", "N/A"),
            "recommendation_mean": info.get("recommendationMean"),
            "recent_recommendations": recent_recs[-5:] if recent_recs else []
        }
    except Exception as e:
        return {"error": str(e)}


def compare_stocks(tickers: list) -> dict:
    """Compare multiple stocks side by side on key metrics."""
    try:
        comparisons = []
        for ticker in tickers[:5]:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")

            month_change = 0
            if not hist.empty and len(hist) > 1:
                month_change = round(((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100, 2)

            comparisons.append({
                "ticker": ticker.upper(),
                "name": info.get("longName", "N/A"),
                "price": info.get("currentPrice") or (round(hist['Close'].iloc[-1], 2) if not hist.empty else None),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
                "profit_margins": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
                "1mo_change": month_change,
                "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
            })

        return {
            "stocks_compared": len(comparisons),
            "comparisons": comparisons
        }
    except Exception as e:
        return {"error": str(e)}


TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price, daily change, volume, and key trading metrics for a given ticker symbol. Use this when the user asks about current price, how a stock is doing today, or wants real-time market data.",
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
        "description": "Get detailed company financials including revenue, earnings, margins, P/E ratio, debt levels, and valuation metrics. Use this when the user asks about a company's financial health, fundamentals, or valuation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, GOOGL, NVDA)"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_price_history",
        "description": "Get historical price data for trend analysis. Supports periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "period": {"type": "string", "description": "Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max", "default": "1mo"}
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
        "description": "Compare multiple stocks side by side on key metrics like price, market cap, P/E ratio, growth, and margins.",
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
