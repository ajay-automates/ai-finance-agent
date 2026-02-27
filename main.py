"""
AI Finance Agent — FastAPI Server
Serves the web UI and handles agent requests.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
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
        if len(query) > 1000:
            return JSONResponse({"error": "Query too long (max 1000 chars)"}, status_code=400)
        result = await get_agent().analyze(query)
        return JSONResponse(result)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Analysis failed: {str(e)}"}, status_code=500)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "api_key_set": bool(os.getenv("ANTHROPIC_API_KEY")), "model": "claude-sonnet-4-20250514"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
