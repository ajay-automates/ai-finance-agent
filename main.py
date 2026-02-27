"""
AI Finance Agent - FastAPI Server
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import uvicorn

from app.agent import FinanceAgent

app = FastAPI(title="AI Finance Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
agent = None


def get_agent():
    global agent
    if agent is None:
        agent = FinanceAgent()
    return agent


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze(request: Request):
    try:
        body = await request.json()
        query = body.get("query", "").strip()
        if not query:
            return JSONResponse({"error": "Query is required"}, status_code=400)
        result = await get_agent().analyze(query)
        return JSONResponse(result)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Analysis failed: {str(e)}"}, status_code=500)


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "anthropic_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
        "fmp_key_set": bool(os.getenv("FMP_API_KEY")),
        "fmp_key_preview": (os.getenv("FMP_API_KEY", "")[:8] + "...") if os.getenv("FMP_API_KEY") else "NOT SET",
    }


@app.get("/api/test-fmp")
async def test_fmp():
    """Debug: test FMP API directly to see what works."""
    fmp_key = os.getenv("FMP_API_KEY", "")
    if not fmp_key:
        return JSONResponse({"error": "FMP_API_KEY not set"})

    results = {}
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={fmp_key}", timeout=10)
        results["v3_quote_status"] = r.status_code
        results["v3_quote_response"] = r.text[:500]
    except Exception as e:
        results["v3_quote_error"] = str(e)

    try:
        r = requests.get(f"https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey={fmp_key}", timeout=10)
        results["stable_quote_status"] = r.status_code
        results["stable_quote_response"] = r.text[:500]
    except Exception as e:
        results["stable_quote_error"] = str(e)

    return JSONResponse(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
