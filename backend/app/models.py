from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Issue(BaseModel):
    id: str
    title: str
    status: str
    assignee: Optional[str] = None
    priority: str = "medium"
    createdAt: str
    description: Optional[str] = None
    labels: Optional[list[str]] = None

class ProjectStats(BaseModel):
    totalIssues: int
    openIssues: int
    closedIssues: int
    inProgress: int

class IssueAssignment(BaseModel):
    assignee: str
    reasoning: str

class AIRecommendationRequest(BaseModel):
    issue_id: str
    issue_title: str
    issue_description: Optional[str] = None
    available_developers: Optional[list[str]] = None

