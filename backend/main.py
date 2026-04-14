import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.auth_routes import router as auth_router
from config import APP_TITLE, APP_VERSION
from rag.loader import initialize_rag
from auth.models import create_tables

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="FinAgent - AI-powered financial assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Original routes (all existing features)
app.include_router(router, prefix="/api")

# New auth routes — /api/auth/register, /api/auth/login, /api/auth/me
app.include_router(auth_router, prefix="/api/auth")


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and RAG on startup."""
    print("[Startup] Creating database tables if not exist...")
    create_tables()
    print("[Startup] Database ready!")
    print("[Startup] Initializing RAG system...")
    initialize_rag()
    print("[Startup] RAG system ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)



    