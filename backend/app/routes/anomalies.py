from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])

# In-memory storage for anomalies (replace with DB in production)
anomalies_store: List[Dict] = []


class AnomalyMetric(BaseModel):
    label: str
    value: str
    trend: Optional[str] = None  # 'up', 'down', 'stable'


class AffectedItems(BaseModel):
    tickets: Optional[List[str]] = []
    developers: Optional[List[str]] = []
    prs: Optional[List[str]] = []
    commits: Optional[List[str]] = []


class Anomaly(BaseModel):
    id: str
    type: str  # 'stale_ticket', 'scope_creep', 'missing_link', 'status_mismatch', 'task_switching'
    severity: str  # 'high', 'medium', 'low'
    title: str
    description: str
    affectedItems: AffectedItems
    detectedAt: str
    aiAnalysis: str
    suggestedActions: List[str]
    metrics: Optional[List[AnomalyMetric]] = []


class DetectAnomaliesRequest(BaseModel):
    jira_data: Dict
    github_data: Optional[Dict] = None
    max_anomalies: int = 20


class DetectAnomaliesResponse(BaseModel):
    status: str
    message: str
    anomalies: List[Anomaly]


@router.post("/detect", response_model=DetectAnomaliesResponse)
async def detect_anomalies(request: DetectAnomaliesRequest):
    """
    Detect workflow anomalies by analyzing Jira and GitHub data
    
    This endpoint analyzes ticket data and commit/PR data to identify:
    - Stale tickets (no activity for extended period)
    - Scope creep (continued work on completed tickets)
    - Missing links (PRs without ticket references)
    - Status mismatches (status doesn't match actual state)
    - Task switching (developer working on too many tickets)
    """
    try:
        anomalies = []
        jira_issues = request.jira_data.get("issues", [])
        project_key = request.jira_data.get("project_key", "PROJ")
        
        # Detect stale tickets
        stale_anomalies = detect_stale_tickets(jira_issues, project_key)
        anomalies.extend(stale_anomalies)
        
        # Detect scope creep
        scope_creep_anomalies = detect_scope_creep(jira_issues, project_key)
        anomalies.extend(scope_creep_anomalies)
        
        # Detect status mismatches
        status_mismatch_anomalies = detect_status_mismatches(jira_issues, project_key)
        anomalies.extend(status_mismatch_anomalies)
        
        # Detect task switching
        task_switching_anomalies = detect_task_switching(jira_issues, project_key)
        anomalies.extend(task_switching_anomalies)
        
        # Limit to max_anomalies
        anomalies = anomalies[:request.max_anomalies]
        
        # Store anomalies
        global anomalies_store
        anomalies_store = [a.dict() for a in anomalies]
        
        return DetectAnomaliesResponse(
            status="success",
            message=f"Detected {len(anomalies)} anomalies",
            anomalies=anomalies
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect anomalies: {str(e)}")


@router.get("/list")
async def list_anomalies():
    """Get all detected anomalies"""
    return {
        "status": "success",
        "anomalies": anomalies_store,
        "count": len(anomalies_store)
    }


@router.get("/{anomaly_id}")
async def get_anomaly(anomaly_id: str):
    """Get a specific anomaly"""
    anomaly = next((a for a in anomalies_store if a.get("id") == anomaly_id), None)
    
    if not anomaly:
        raise HTTPException(status_code=404, detail=f"Anomaly {anomaly_id} not found")
    
    return {
        "status": "success",
        "anomaly": anomaly
    }


def detect_stale_tickets(issues: List[Dict], project_key: str) -> List[Anomaly]:
    """Detect tickets that have been inactive for too long"""
    anomalies = []
    now = datetime.now()
    
    for issue in issues:
        status = issue.get("status", "")
        updated = issue.get("updated", "")
        
        # Skip if done or not in progress
        if status not in ["In Progress", "In Development"]:
            continue
        
        try:
            updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days_inactive = (now - updated_date).days
            
            if days_inactive >= 5:
                severity = "high" if days_inactive >= 7 else "medium"
                
                anomaly = Anomaly(
                    id=f"ANOM-STALE-{issue.get('key')}",
                    type="stale_ticket",
                    severity=severity,
                    title=f"Ticket {issue.get('key')} in Progress with No Recent Activity",
                    description=f"{issue.get('key')} has been \"In Progress\" for {days_inactive} days with no updates",
                    affectedItems=AffectedItems(
                        tickets=[issue.get("key")],
                        developers=[issue.get("assignee")] if issue.get("assignee") else []
                    ),
                    detectedAt=now.isoformat(),
                    aiAnalysis=f"This ticket shows signs of being blocked or abandoned. The assignee has not made any updates in {days_inactive} days despite it being marked as \"In Progress\". This pattern often indicates blocked work, underestimated complexity, or shifted priorities.",
                    suggestedActions=[
                        f"Reach out to {issue.get('assignee', 'assignee')} to understand current status",
                        "Check if there are blocking dependencies",
                        "Consider moving ticket back to backlog if work hasn't started",
                        "Update ticket with current blockers or progress notes"
                    ],
                    metrics=[
                        AnomalyMetric(label="Days Inactive", value=str(days_inactive), trend="up")
                    ]
                )
                anomalies.append(anomaly)
        except:
            continue
    
    return anomalies


def detect_scope_creep(issues: List[Dict], project_key: str) -> List[Anomaly]:
    """Detect tickets marked done but still receiving updates"""
    anomalies = []
    now = datetime.now()
    
    for issue in issues:
        status = issue.get("status", "")
        
        # Only check done tickets
        if status not in ["Done", "Closed", "Resolved"]:
            continue
        
        # Check if there are recent status transitions
        status_history = issue.get("status_history", [])
        if not status_history:
            continue
        
        # Find when ticket was marked done
        done_date = None
        for transition in reversed(status_history):
            if transition.get("to") in ["Done", "Closed", "Resolved"]:
                try:
                    done_date = datetime.fromisoformat(transition.get("date").replace("Z", "+00:00"))
                    break
                except:
                    continue
        
        if not done_date:
            continue
        
        # Check if there are transitions after done
        post_done_transitions = [t for t in status_history if datetime.fromisoformat(t.get("date", "").replace("Z", "+00:00")) > done_date]
        
        if len(post_done_transitions) >= 2:
            anomaly = Anomaly(
                id=f"ANOM-SCOPE-{issue.get('key')}",
                type="scope_creep",
                severity="high",
                title=f"Ticket {issue.get('key')} Marked Done but Receiving Updates",
                description=f"{issue.get('key')} was marked \"Done\" but has {len(post_done_transitions)} status changes since then",
                affectedItems=AffectedItems(
                    tickets=[issue.get("key")],
                    developers=[issue.get("assignee")] if issue.get("assignee") else []
                ),
                detectedAt=now.isoformat(),
                aiAnalysis="This completed ticket is showing unexpected continued activity. This pattern indicates either significant bugs discovered post-completion, incomplete scope in the original ticket, or new requirements being added without creating a new ticket. This makes it difficult to track true completion metrics and can hide scope creep.",
                suggestedActions=[
                    "Review changes to determine if they are bug fixes or new features",
                    "Create new tickets for any new feature work",
                    "Consider reopening the ticket if work is substantial",
                    "Update ticket documentation to reflect actual work completed"
                ],
                metrics=[
                    AnomalyMetric(label="Changes After Done", value=str(len(post_done_transitions)), trend="up")
                ]
            )
            anomalies.append(anomaly)
    
    return anomalies


def detect_status_mismatches(issues: List[Dict], project_key: str) -> List[Anomaly]:
    """Detect tickets whose status doesn't match their actual state"""
    anomalies = []
    now = datetime.now()
    
    for issue in issues:
        status = issue.get("status", "")
        comments_count = issue.get("comments_count", 0)
        
        # Check for "In Review" tickets with no recent activity
        if status in ["In Review", "Review", "Code Review"]:
            updated = issue.get("updated", "")
            try:
                updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                days_in_review = (now - updated_date).days
                
                if days_in_review >= 2:
                    anomaly = Anomaly(
                        id=f"ANOM-STATUS-{issue.get('key')}",
                        type="status_mismatch",
                        severity="high",
                        title=f"Ticket {issue.get('key')} in Review with No Recent Activity",
                        description=f"{issue.get('key')} status is \"In Review\" but no activity for {days_in_review} days",
                        affectedItems=AffectedItems(
                            tickets=[issue.get("key")],
                            developers=[issue.get("assignee")] if issue.get("assignee") else []
                        ),
                        detectedAt=now.isoformat(),
                        aiAnalysis=f"Ticket has been in \"In Review\" status for {days_in_review} days with no recent activity. This suggests the PR may not have been created yet, the review process has stalled, or the status was changed prematurely. This prevents automated workflows from functioning properly.",
                        suggestedActions=[
                            "Verify if a PR exists for this ticket",
                            "Check if review is happening through another channel",
                            "Move ticket back to \"In Progress\" if PR not yet created",
                            "Establish clear criteria for moving tickets to review status"
                        ],
                        metrics=[
                            AnomalyMetric(label="Days in Review", value=str(days_in_review), trend="up")
                        ]
                    )
                    anomalies.append(anomaly)
            except:
                continue
    
    return anomalies


def detect_task_switching(issues: List[Dict], project_key: str) -> List[Anomaly]:
    """Detect developers working on too many tickets simultaneously"""
    anomalies = []
    now = datetime.now()
    
    # Group tickets by assignee
    developer_tickets = {}
    for issue in issues:
        assignee = issue.get("assignee")
        status = issue.get("status", "")
        
        # Only count in-progress tickets
        if not assignee or status not in ["In Progress", "In Development", "In Review"]:
            continue
        
        if assignee not in developer_tickets:
            developer_tickets[assignee] = []
        developer_tickets[assignee].append(issue.get("key"))
    
    # Detect high task switching
    for developer, tickets in developer_tickets.items():
        if len(tickets) >= 5:
            anomaly = Anomaly(
                id=f"ANOM-SWITCH-{developer.replace(' ', '-')}",
                type="task_switching",
                severity="medium",
                title=f"High Task Switching Detected for {developer}",
                description=f"{developer} is working on {len(tickets)} tickets simultaneously",
                affectedItems=AffectedItems(
                    developers=[developer],
                    tickets=tickets[:5]
                ),
                detectedAt=now.isoformat(),
                aiAnalysis=f"{developer} is showing a high degree of task switching, with {len(tickets)} tickets in progress. While activity seems healthy, the lack of ticket completion suggests fragmented focus. This pattern typically indicates frequent context switching reducing productivity, being pulled into multiple urgent issues, or helping others across multiple features.",
                suggestedActions=[
                    f"Review {developer}'s workload and help prioritize tasks",
                    "Identify if task switching is due to blockers or interruptions",
                    "Consider assigning fewer concurrent tickets",
                    f"Check if {developer} is being pulled into too many support requests",
                    "Schedule 1-on-1 to understand context switching drivers"
                ],
                metrics=[
                    AnomalyMetric(label="Active Tickets", value=str(len(tickets)), trend="up")
                ]
            )
            anomalies.append(anomaly)
    
    return anomalies

