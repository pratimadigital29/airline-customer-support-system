"""Liveness / readiness probes for Docker, K8s and uptime monitors."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "env": settings.env, "llm_provider": settings.llm_provider}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ready": True}
