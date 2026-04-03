"""
main.py
-------
FastAPI application entry point.

Run locally with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.mods import router as mods_router

app = FastAPI(
    title="PoE Craft Regex API",
    description="Backend API for the Path of Exile crafting bench regex builder.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the React frontend to call this API in development.
# In production, restrict origins to your deployed frontend URL.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mods_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Simple liveness check — used by deployment platforms."""
    return {"status": "ok"}
