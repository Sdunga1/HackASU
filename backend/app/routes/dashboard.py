from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter()

# Store for dashboard data (in production, use Redis or a database)
dashboard_data = {
    "issues": [],
    "last_updated": None,
    "repository": None
}

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


class DashboardIssue(BaseModel):
    id: str
    title: str
    status: str
    assignee: Optional[str] = None
    priority: str
    createdAt: str
    labels: Optional[List[str]] = []
    url: Optional[str] = None


class DashboardSyncRequest(BaseModel):
    repository: str
    issues: List[DashboardIssue]
    timestamp: Optional[str] = None


@router.post("/sync-issues")
async def sync_issues(request: DashboardSyncRequest):
    """
    Receive issues from MCP server and store them for dashboard
    """
    try:
        # Store the data
        dashboard_data["issues"] = [issue.dict() for issue in request.issues]
        dashboard_data["last_updated"] = datetime.utcnow().isoformat()
        dashboard_data["repository"] = request.repository
        
        # Broadcast to all connected WebSocket clients
        await manager.broadcast({
            "type": "issues_update",
            "data": dashboard_data
        })
        
        return {
            "status": "success",
            "message": f"Received {len(request.issues)} issues from {request.repository}",
            "count": len(request.issues),
            "timestamp": dashboard_data["last_updated"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/issues")
async def get_dashboard_issues():
    """
    Get current issues stored for dashboard
    """
    if not dashboard_data["issues"]:
        return {
            "issues": [],
            "message": "No issues loaded yet. Use MCP tool 'send_issues_to_dashboard' to load issues.",
            "last_updated": None
        }
    
    return {
        "issues": dashboard_data["issues"],
        "repository": dashboard_data["repository"],
        "last_updated": dashboard_data["last_updated"],
        "count": len(dashboard_data["issues"])
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates
    """
    await manager.connect(websocket)
    try:
        # Send current data on connection
        await websocket.send_json({
            "type": "initial_data",
            "data": dashboard_data
        })
        
        # Keep connection alive
        while True:
            # Wait for any messages (ping/pong)
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

