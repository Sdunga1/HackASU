from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues, stats, ai, dashboard
from app.config import settings

app = FastAPI(
    title="DevAI Manager API",
    description="AI-powered project management API for GitHub and Jira",
    version="0.1.0",
)

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
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

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

