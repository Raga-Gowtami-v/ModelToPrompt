from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routes import scan, prompt, model
from app.routes import sanitize, automated_ml

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Secure Data & Automated ML Pipeline",
    description="PII detection, masking, and prompt-driven ML model training",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing API routes
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(prompt.router, prefix="/api/prompt", tags=["Prompt"])
app.include_router(model.router, prefix="/api/model", tags=["Model"])

# New top-level endpoints
app.include_router(sanitize.router, tags=["Sanitize"])
app.include_router(automated_ml.router, tags=["Automated ML"])


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page with buttons for Sanitize and Train Model."""
    return templates.TemplateResponse("index.html", {"request": request})
