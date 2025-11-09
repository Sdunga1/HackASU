# Dashboard Real-Time Sync via MCP

This feature allows you to send GitHub issues directly from Claude (with MCP tools) to your frontend dashboard in real-time.

## How It Works

```
You in Cursor Chat: "Show me issues from owner/repo and send to dashboard"
  ↓
Claude uses MCP tool: send_issues_to_dashboard("owner", "repo")
  ↓
MCP server fetches issues from GitHub
  ↓
MCP server POSTs to backend API
  ↓
Backend stores issues and broadcasts via WebSocket
  ↓
Frontend dashboard updates in real-time
```

## Setup

### 1. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Configure MCP Server

Make sure your MCP server has the backend URL configured:

```bash
cd mcp-servers/github-mcp
# Add to .env
echo "BACKEND_API_URL=http://localhost:8000" >> .env
```

### 4. Restart Cursor

Restart Cursor so it picks up the new MCP tool: `send_issues_to_dashboard`

## Usage

### In Cursor Chat (with Claude):

**Example 1: Send issues to dashboard**
```
You: "Get all open issues from facebook/react and send them to my dashboard"
Claude: *uses send_issues_to_dashboard("facebook", "react", "open")*
Claude: "Successfully sent 47 issues to your dashboard!"
```

**Example 2: Check specific repo**
```
You: "What issues does my-username/my-repo have? Send them to dashboard"
Claude: *uses send_issues_to_dashboard("my-username", "my-repo")*
Claude: "Found 5 open issues and sent them to your dashboard."
```

**Example 3: Closed issues**
```
You: "Show me all closed issues from microsoft/vscode and display on dashboard"
Claude: *uses send_issues_to_dashboard("microsoft", "vscode", "closed")*
```

### What Happens

1. **Immediate**: Claude confirms the issues were sent
2. **Real-time**: Your dashboard (localhost:3000) updates automatically
3. **Persistent**: Issues remain in dashboard until you sync new ones

## API Endpoints

### Backend Endpoints

- `POST /api/dashboard/sync-issues` - Receive issues from MCP
- `GET /api/dashboard/issues` - Get currently synced issues
- `WS /api/dashboard/ws` - WebSocket for real-time updates

### Frontend

- Dashboard automatically connects to WebSocket on load
- Falls back to regular API if no synced data available
- Shows repository name and last updated timestamp

## Testing

### Test the MCP Tool Directly

In Cursor chat, ask me:
```
"Use the send_issues_to_dashboard tool to fetch issues from torvalds/linux and send them to the dashboard"
```

I'll fetch the issues and push them to your dashboard in real-time.

### Test the Backend API

```bash
curl -X POST http://localhost:8000/api/dashboard/sync-issues \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "test/repo",
    "issues": [
      {
        "id": "1",
        "title": "Test Issue",
        "status": "open",
        "priority": "high",
        "createdAt": "2025-01-09T00:00:00Z"
      }
    ]
  }'
```

### Check Current Dashboard Data

```bash
curl http://localhost:8000/api/dashboard/issues
```

## Architecture

**Traditional API Flow:**
```
Frontend → Backend → GitHub API → Response
```

**MCP-Powered Flow:**
```
You ask Claude → Claude uses MCP tools → Fetches from GitHub
                                        ↓
Frontend ← WebSocket ← Backend ← HTTP POST from MCP server
```

**Key Difference:** 
- You control data sync through conversation with AI
- AI can aggregate/analyze before sending
- Real-time updates without frontend polling

## Benefits

1. **Conversational Data Sync**: "Show me react issues" vs writing API calls
2. **AI Analysis**: Claude can filter/summarize before sending
3. **Real-time**: Dashboard updates instantly via WebSocket
4. **Flexible**: Ask for any repo, any state, any time
5. **Context-Aware**: Claude knows what you're working on

## Next Steps

Add more MCP tools to send:
- `send_commits_to_dashboard` - Show commit history
- `send_pr_summary_to_dashboard` - Show PR analysis
- `send_ai_recommendations_to_dashboard` - Show AI insights

This bridges the gap between conversational AI and your dashboard UI!

