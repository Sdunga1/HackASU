# Quick Start: MCP → Dashboard Real-Time Sync

## What You Just Got

A new MCP tool that lets you ask me (Claude) to fetch GitHub issues and push them to your dashboard in real-time.

## 3-Step Setup

### Step 1: Start Your Servers

**Terminal 1 - Backend:**
```bash
cd ~/Desktop/HackASU/backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd ~/Desktop/HackASU/frontend
npm run dev
```

### Step 2: Update MCP Config (if not already done)

Your Cursor MCP config should have `BACKEND_API_URL` environment variable. Check `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "/Users/ashishthanga/Desktop/HackASU/mcp-servers/github-mcp/venv/bin/github-mcp",
      "args": [],
      "cwd": "/Users/ashishthanga/Desktop/HackASU/mcp-servers/github-mcp",
      "env": {
        "GITHUB_TOKEN": "your_token",
        "BACKEND_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

If you added `BACKEND_API_URL`, restart Cursor.

### Step 3: Test It!

**In this Cursor chat, ask me:**

```
"Use send_issues_to_dashboard to get issues from facebook/react"
```

Or with your dummy repo:

```
"Send issues from [your-username]/[your-repo] to the dashboard"
```

## What Happens

1. ✅ I fetch real issues from GitHub
2. ✅ I send them to `http://localhost:8000/api/dashboard/sync-issues`
3. ✅ Backend broadcasts to frontend via WebSocket
4. ✅ Your dashboard at `http://localhost:3000` updates instantly!

## Check if It's Working

**Backend running?**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Frontend running?**
```bash
# Open browser to http://localhost:3000
# Should see dashboard
```

**Dashboard receiving data?**
```bash
curl http://localhost:8000/api/dashboard/issues
# Should return current synced issues
```

## Example Queries

Ask me any of these:

1. **"Get issues from microsoft/vscode and send to dashboard"**
2. **"Show me closed issues from facebook/react on my dashboard"**
3. **"What issues does torvalds/linux have? Put them on dashboard"**
4. **"Send all open issues from your-username/your-test-repo to dashboard"**

## Troubleshooting

**"Backend API is unreachable"**
- Make sure backend is running: `uvicorn main:app --reload`
- Check URL: `curl http://localhost:8000/health`

**"Dashboard not updating"**
- Check browser console for WebSocket errors
- Make sure frontend is running: `npm run dev`
- Refresh the page

**"Tool not found"**
- Restart Cursor to reload MCP tools
- Check MCP config has the github server configured

## Files Changed

- ✅ `mcp-servers/github-mcp/github_mcp/server.py` - New tool added
- ✅ `backend/app/routes/dashboard.py` - New routes
- ✅ `backend/main.py` - Dashboard router added
- ✅ `frontend/src/lib/api.ts` - Fetch from dashboard endpoint
- ✅ `frontend/src/components/Dashboard.tsx` - WebSocket support

## You're Ready!

Just start the servers and ask me to fetch issues. Watch them appear on your dashboard in real-time! 🚀

