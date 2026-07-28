"""FastAPI application entry point for Trial Assistant."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.experiment import router as experiment_router
from app.api.quotation import router as quotation_router
from app.core.config import settings

# ── Logging configuration ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-6s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Trial Assistant - AI Agent Platform for Third-party Testing Laboratories",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────
app.include_router(chat_router, prefix=settings.api_prefix, tags=["Chat"])
app.include_router(experiment_router, prefix=settings.api_prefix, tags=["Experiment"])
app.include_router(quotation_router, prefix=settings.api_prefix, tags=["Quotation"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": settings.app_version}


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application services on startup."""
    logger.info(f"{settings.app_name} v{settings.app_version} starting up...")

    # Initialize LangGraph workflow
    from app.workflows.main_workflow import get_workflow
    get_workflow()
    logger.info("LangGraph workflow initialized successfully")

    # Initialize knowledge base (RAG)
    try:
        from app.services.rag_service import initialize_knowledge_base
        result = initialize_knowledge_base()
        logger.info(f"Knowledge base initialized: {result}")
    except Exception as e:
        logger.warning(f"Knowledge base initialization skipped: {e}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up application services on shutdown."""
    logger.info(f"{settings.app_name} shutting down...")
