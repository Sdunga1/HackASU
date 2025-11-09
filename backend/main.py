from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues, stats, dashboard, chat, srs, narratives, anomalies
from app.config import settings
from app.middleware.error_handler import setup_error_handlers

app = FastAPI(
    title="DevAI Manager API",
    description="AI-powered project management API for GitHub and Jira",
    version="0.1.0",
)

# Setup centralized error handling
setup_error_handlers(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(issues.router, prefix="/api", tags=["issues"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(srs.router, prefix="/api/srs", tags=["srs"])
app.include_router(narratives.router, tags=["narratives"])
app.include_router(anomalies.router, tags=["anomalies"])

@app.get("/")
async def root():
    return {
        "message": "DevAI Manager API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
