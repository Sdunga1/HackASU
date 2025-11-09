from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/narratives", tags=["narratives"])

# In-memory storage for narratives (replace with DB in production)
narratives_store: List[Dict] = []


class CommitEvent(BaseModel):
    timestamp: str
    type: str  # 'commit', 'pr', 'review', 'status', 'comment'
    author: str
    title: str
    description: str
    details: Optional[str] = None


class NarrativeInsights(BaseModel):
    delays: List[str] = []
    blockers: List[str] = []
    resolutions: List[str] = []


class TicketNarrative(BaseModel):
    ticketId: str
    ticketTitle: str
    estimatedDays: int = 0
    actualDays: int = 0
    status: str
    narrative: str
    timeline: List[CommitEvent] = []
    insights: NarrativeInsights


class GenerateNarrativesRequest(BaseModel):
    repository: str
    tickets: List[Dict]


class GenerateNarrativesResponse(BaseModel):
    status: str
    message: str
    narratives: List[TicketNarrative]


@router.post("/generate", response_model=GenerateNarrativesResponse)
async def generate_narratives(request: GenerateNarrativesRequest):
    """
    Generate AI-powered commit-to-ticket narratives
    
    This endpoint receives raw ticket data with commits, PRs, reviews, and comments,
    then generates human-readable narratives explaining what happened during development.
    """
    try:
        narratives = []
        
        for ticket_data in request.tickets:
            ticket_id = ticket_data.get("ticketId")
            commits = ticket_data.get("commits", [])
            prs = ticket_data.get("prs", [])
            reviews = ticket_data.get("reviews", [])
            comments = ticket_data.get("comments", [])
            
            # Build timeline
            timeline = []
            
            # Add commits to timeline
            for commit in commits:
                timeline.append({
                    "timestamp": commit.get("date", ""),
                    "type": "commit",
                    "author": commit.get("author_login") or commit.get("author", "Unknown"),
                    "title": commit.get("message", "").split("\n")[0][:100],
                    "description": commit.get("message", "").split("\n")[0],
                    "details": f"Commit: {commit.get('sha', '')[:7]}"
                })
            
            # Add PRs to timeline
            for pr in prs:
                timeline.append({
                    "timestamp": pr.get("created_at", ""),
                    "type": "pr",
                    "author": pr.get("author", "Unknown"),
                    "title": f"PR #{pr.get('number')} {'merged' if pr.get('merged_at') else 'opened'}",
                    "description": pr.get("title", ""),
                    "details": f"{pr.get('additions', 0)} additions, {pr.get('deletions', 0)} deletions"
                })
                
                # Add merge event if merged
                if pr.get("merged_at"):
                    timeline.append({
                        "timestamp": pr.get("merged_at"),
                        "type": "pr",
                        "author": pr.get("author", "Unknown"),
                        "title": f"PR #{pr.get('number')} merged",
                        "description": f"Merged to {pr.get('base', {}).get('ref', 'main')}",
                        "details": ""
                    })
            
            # Add reviews to timeline
            for review in reviews:
                timeline.append({
                    "timestamp": review.get("submitted_at", ""),
                    "type": "review",
                    "author": review.get("author", "Unknown"),
                    "title": f"PR #{review.get('pr_number')} review: {review.get('state', '')}",
                    "description": review.get("body", "Review submitted")[:200],
                    "details": f"State: {review.get('state')}"
                })
            
            # Add comments to timeline
            for comment in comments:
                timeline.append({
                    "timestamp": comment.get("created_at", ""),
                    "type": "comment",
                    "author": comment.get("author", "Unknown"),
                    "title": f"Comment on PR #{comment.get('pr_number')}",
                    "description": comment.get("body", "")[:200],
                    "details": ""
                })
            
            # Sort timeline by timestamp
            timeline.sort(key=lambda x: x.get("timestamp", ""))
            
            # Generate narrative (AI would be used here in production)
            narrative = generate_narrative_text(ticket_id, commits, prs, reviews, timeline)
            
            # Calculate days (simplified)
            estimated_days = 5  # Would come from Jira
            actual_days = len(commits) if commits else 0
            
            # Extract insights
            insights = extract_insights(commits, prs, reviews, comments)
            
            # Determine status
            status = "Done" if any(pr.get("merged_at") for pr in prs) else "In Progress"
            
            # Create narrative object
            narrative_obj = TicketNarrative(
                ticketId=ticket_id,
                ticketTitle=prs[0].get("title") if prs else f"Development for {ticket_id}",
                estimatedDays=estimated_days,
                actualDays=actual_days,
                status=status,
                narrative=narrative,
                timeline=[CommitEvent(**event) for event in timeline],
                insights=NarrativeInsights(**insights)
            )
            
            narratives.append(narrative_obj)
        
        # Store narratives
        global narratives_store
        narratives_store = [n.dict() for n in narratives]
        
        return GenerateNarrativesResponse(
            status="success",
            message=f"Generated narratives for {len(narratives)} tickets",
            narratives=narratives
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate narratives: {str(e)}")


@router.get("/list")
async def list_narratives():
    """Get all stored narratives"""
    return {
        "status": "success",
        "narratives": narratives_store,
        "count": len(narratives_store)
    }


@router.get("/{ticket_id}")
async def get_narrative(ticket_id: str):
    """Get narrative for a specific ticket"""
    narrative = next((n for n in narratives_store if n.get("ticketId") == ticket_id), None)
    
    if not narrative:
        raise HTTPException(status_code=404, detail=f"Narrative for {ticket_id} not found")
    
    return {
        "status": "success",
        "narrative": narrative
    }


def generate_narrative_text(ticket_id: str, commits: List[Dict], prs: List[Dict], reviews: List[Dict], timeline: List[Dict]) -> str:
    """
    Generate a human-readable narrative from the timeline
    (In production, this would use AI/LLM to generate more sophisticated narratives)
    """
    if not timeline:
        return f"No activity found for {ticket_id}."
    
    narrative_parts = []
    
    # Count events
    commit_count = len(commits)
    pr_count = len(prs)
    review_count = len(reviews)
    
    # Check if work is done
    merged_prs = [pr for pr in prs if pr.get("merged_at")]
    is_done = len(merged_prs) > 0
    
    # Start narrative
    if is_done:
        narrative_parts.append(f"This ticket was completed with {commit_count} commits across {pr_count} pull request(s).")
    else:
        narrative_parts.append(f"This ticket is in progress with {commit_count} commits so far.")
    
    # Describe development
    if commits:
        authors = list(set([c.get("author_login") or c.get("author") for c in commits if c.get("author_login") or c.get("author")]))
        if len(authors) == 1:
            narrative_parts.append(f"Development was handled by {authors[0]}.")
        else:
            narrative_parts.append(f"Development involved {len(authors)} contributors: {', '.join(authors[:3])}")
    
    # Describe reviews
    if reviews:
        approved = [r for r in reviews if r.get("state") == "APPROVED"]
        changes_requested = [r for r in reviews if r.get("state") == "CHANGES_REQUESTED"]
        
        if changes_requested:
            narrative_parts.append(f"Code review requested {len(changes_requested)} round(s) of changes before approval.")
        elif approved:
            narrative_parts.append(f"Code review approved with {len(approved)} approval(s).")
    
    # Describe completion
    if merged_prs:
        merge_date = merged_prs[0].get("merged_at", "")
        narrative_parts.append(f"Work was merged and completed on {merge_date[:10]}.")
    
    return " ".join(narrative_parts)


def extract_insights(commits: List[Dict], prs: List[Dict], reviews: List[Dict], comments: List[Dict]) -> Dict:
    """Extract insights about delays, blockers, and resolutions"""
    insights = {
        "delays": [],
        "blockers": [],
        "resolutions": []
    }
    
    # Detect delays from review cycles
    changes_requested = [r for r in reviews if r.get("state") == "CHANGES_REQUESTED"]
    if len(changes_requested) > 1:
        insights["delays"].append(f"Multiple review cycles ({len(changes_requested)}) required changes")
    
    # Detect blockers from PR comments
    for comment in comments:
        body = comment.get("body", "").lower()
        if any(word in body for word in ["blocked", "blocker", "waiting", "dependency"]):
            insights["blockers"].append(f"Potential blocker mentioned in PR comments")
            break
    
    # Detect resolutions from merged PRs
    merged_prs = [pr for pr in prs if pr.get("merged_at")]
    if merged_prs:
        insights["resolutions"].append(f"Successfully merged {len(merged_prs)} pull request(s)")
    
    return insights

