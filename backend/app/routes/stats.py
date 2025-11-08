from fastapi import APIRouter, HTTPException
from app.models import ProjectStats
from app.services.github_service import GitHubService
from app.services.jira_service import JiraService

router = APIRouter()

github_service = GitHubService()
jira_service = JiraService()

@router.get("/stats", response_model=ProjectStats)
async def get_project_stats():
    """
    Get project statistics (total issues, open, closed, in progress)
    """
    try:
        # For now, return mock data
        # TODO: Calculate actual stats from GitHub and Jira
        stats = {
            "totalIssues": 25,
            "openIssues": 12,
            "closedIssues": 10,
            "inProgress": 3,
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

