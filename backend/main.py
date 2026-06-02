"""
AgriGuard / FloraScope â€” unified FastAPI entry point

Keeps your existing architecture intact:
  - backend.routers.predict  â†’ handles /api/v1/predict
  - backend.routers.history  â†’ handles /api/v1/history
  - backend.models.inference â†’ your EfficientNet-B3 dual-head model
  - backend.database.postgres â†’ your postgres DB

Adds on top:
  - /api/v1/auth/login       â†’ FloraScope frontend login
  - /api/v1/agent-report     â†’ Ollama treatment report (no API key needed)
  - Static file serving      â†’ serves login / dashboard / result HTML
  - Prometheus metrics       â†’ unchanged
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from backend.config import get_settings
from backend.database.postgres import init_db
from backend.models.inference import model
from backend.routers import history, predict

settings = get_settings()

# â”€â”€â”€ FRONTEND DIR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Expects:  <project_root>/frontend/login.html
#                                   dashboard.html
#                                   result.html
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LIFESPAN â€” startup / shutdown
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip model loading at startup - loads lazily on first request
    try:
        await init_db()
        print("âœ… Database connected!")
    except Exception as e:
        print(f"âš ï¸ Database not available: {e} - continuing without DB")
    print("âœ… AgriGuard / FloraScope ready!")
    yield
    print("ðŸ›‘ Shutting down...")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# APP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# â”€â”€â”€ CORS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# â”€â”€â”€ PROMETHEUS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

Instrumentator().instrument(app).expose(app)

# â”€â”€â”€ YOUR EXISTING ROUTERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# predict router  â†’ already exposes  POST /api/v1/predict
# history router  â†’ already exposes  GET  /api/v1/history

app.include_router(predict.router)
app.include_router(history.router)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# AUTH  (FloraScope frontend needs this)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_SECRET_KEY  = getattr(settings, "SECRET_KEY",  "change-me")
_ALGORITHM   = "HS256"
_EXPIRE_MINS = 60 * 24   # 24 h

# Demo credentials â€” override in .env via DEMO_EMAIL / DEMO_PASSWORD
_DEMO_EMAIL    = getattr(settings, "DEMO_EMAIL",    "admin@agriguard.com")
_DEMO_PASSWORD = getattr(settings, "DEMO_PASSWORD", "admin")
_DEMO_NAME     = getattr(settings, "DEMO_NAME",     "AgriGuard Admin")


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/v1/auth/login")
async def login(body: LoginRequest):
    if body.email != _DEMO_EMAIL or body.password != _DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.utcnow() + timedelta(minutes=_EXPIRE_MINS)
    token  = jwt.encode(
        {"sub": body.email, "exp": expire},
        _SECRET_KEY,
        algorithm=_ALGORITHM,
    )
    return {"token": token, "name": _DEMO_NAME, "email": body.email}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# OLLAMA AGENT REPORT  (replaces Anthropic â€” no key needed)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class AgentRequest(BaseModel):
    plant: str
    disease: str
    is_healthy: bool


@app.post("/api/v1/agent-report")
async def agent_report(body: AgentRequest):
    """
    Called by the predict router (or directly) to get a treatment report.
    Uses Ollama running locally â€” make sure `ollama serve` is running
    and the model (default llama3) is pulled:
        ollama pull llama3
    """
    ollama_url   = getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model = getattr(settings, "OLLAMA_MODEL",    "llama3:latest")

    if body.is_healthy:
        prompt = (
            f"The plant '{body.plant}' appears healthy. "
            f"Give 4 short bullet-point care tips for keeping it healthy. "
            f"Be concise and practical for a home gardener."
        )
    else:
        prompt = (
            f"A plant identified as '{body.plant}' has been diagnosed with '{body.disease}'. "
            f"Provide:\n"
            f"1. A one-sentence explanation of the disease\n"
            f"2. Five numbered treatment steps\n"
            f"3. Two prevention tips\n"
            f"Be concise and practical for a home gardener."
        )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            report = resp.json().get("response", "").strip()
    except Exception as e:
        # Graceful fallback â€” never crash the prediction response
        report = _fallback_report(body.plant, body.disease, body.is_healthy)
        print(f"[WARN] Ollama unavailable ({e}), using fallback report")

    return {"agent_report": report}


def _fallback_report(plant: str, disease: str, is_healthy: bool) -> str:
    """Returned when Ollama is offline."""
    if is_healthy:
        return (
            f"## {plant} â€” Healthy âœ…\n\n"
            "**Care tips:**\n"
            "1. Water when the top inch of soil is dry.\n"
            "2. Ensure adequate sunlight for the species.\n"
            "3. Fertilise monthly during the growing season.\n"
            "4. Inspect regularly for early signs of pests."
        )
    return (
        f"## {plant} â€” {disease}\n\n"
        "**Treatment steps:**\n"
        "1. Remove and dispose of all visibly infected leaves immediately.\n"
        "2. Apply a copper-based fungicide or neem oil every 7â€“10 days.\n"
        "3. Improve air circulation â€” space plants adequately.\n"
        "4. Avoid overhead watering; water at the base in the morning.\n"
        "5. Monitor closely for two weeks; repeat treatment if needed.\n\n"
        "**Prevention:**\n"
        "- Rotate crops each season.\n"
        "- Keep tools clean and disinfected between plants."
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HEALTH CHECK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@app.get("/health")
async def health_detail():
    return {
        "status":       "healthy",
        "version":      settings.API_VERSION,
        "model_loaded": model is not None,
        "ollama_url":   getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    }

@app.get("/api/v1/health")
async def api_health():
    return {"status": "ok", "version": settings.API_VERSION}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SERVE FLORASCOPE FRONTEND  (must be LAST â€” catches all remaining routes)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if FRONTEND_DIR.exists():
    @app.get("/login")
    async def serve_login():
        return FileResponse(FRONTEND_DIR / "login.html")

    @app.get("/dashboard")
    async def serve_dashboard():
        return FileResponse(FRONTEND_DIR / "dashboard.html")

    @app.get("/result")
    async def serve_result():
        return FileResponse(FRONTEND_DIR / "result.html")

    # Root â†’ redirect to login
    @app.get("/")
    async def root():
        return FileResponse(FRONTEND_DIR / "login.html")

    # Static assets (CSS, JS, images if any)
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )

else:
    # Frontend not present â€” plain health check at root
    @app.get("/")
    async def root_no_frontend():
        return {
            "status":  "healthy",
            "version": settings.API_VERSION,
            "note":    "Frontend not found. Place HTML files in /frontend/",
        }