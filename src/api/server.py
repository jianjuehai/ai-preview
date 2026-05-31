"""
FastAPI server for the AI PR Review Dashboard.
Usage: python -m uvicorn src.api.server:app --reload --port 8000
"""

from pathlib import Path
from dataclasses import asdict

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.github.pr_capture import capture_pr_diff
from src.ai.reviewer import review_pr_diff

app = FastAPI(title="AI PR Review Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
_SPA_AVAILABLE = (_FRONTEND_DIST / "index.html").exists()

if _SPA_AVAILABLE:
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")


@app.get("/api/diff")
async def api_diff(owner: str, repo: str, pr: int):
    """Return structured diff data for a PR (auto mock fallback)."""
    result = capture_pr_diff(owner, repo, pr)
    return JSONResponse(content=result.to_dict())


@app.get("/api/review")
async def api_review(owner: str, repo: str, pr: int):
    """Return AI review result for a PR (auto mock fallback)."""
    result = review_pr_diff(owner, repo, pr)
    return JSONResponse(content=asdict(result))


_PLACEHOLDER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI PR Review</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
      display:flex;align-items:center;justify-content:center;height:100vh;
      background:#0d1117;color:#c9d1d9}
    .card{text-align:center;padding:3rem;border:1px solid #30363d;
      border-radius:8px;background:#161b22;max-width:480px}
    h1{color:#58a6ff;margin-bottom:1rem}
    p{margin:.5rem 0;color:#8b949e}
    a{color:#58a6ff}
    .badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:.75rem;margin:0 2px}
    .badge-api{background:#23863622;color:#3fb950;border:1px solid #23863644}
  </style>
</head>
<body>
  <div class="card">
    <h1>AI PR Review Dashboard</h1>
    <p>Loading dashboard...</p>
    <p style="margin-top:1.5rem">
      <span class="badge badge-api">API</span>
      <a href="/docs">/docs</a> &mdash; OpenAPI
    </p>
    <p>
      <span class="badge badge-api">GET</span>
      <a href="/api/diff?owner=jianjuehai&repo=ai-preview&pr=1">/api/diff</a>
    </p>
    <p>
      <span class="badge badge-api">GET</span>
      <a href="/api/review?owner=jianjuehai&repo=ai-preview&pr=1">/api/review</a>
    </p>
  </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    if _SPA_AVAILABLE:
        return HTMLResponse(content=(_FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    return HTMLResponse(content=_PLACEHOLDER_HTML)


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str):
    if _SPA_AVAILABLE and "." not in full_path.rsplit("/", 1)[-1]:
        return HTMLResponse(content=(_FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    return JSONResponse({"detail": "Not found"}, status_code=404)
