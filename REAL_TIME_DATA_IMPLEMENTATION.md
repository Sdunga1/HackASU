# Real-Time Data Implementation for Commit Narratives & Anomaly Detection

## Overview
This implementation adds **real-time data capabilities** to the Commit Narratives and Anomaly Detection features while **preserving all existing mockup data** for your hackathon demo.

## ✅ What Was Implemented

### 1. GitHub MCP Tool: `generate_commit_narratives`
**Location:** `/mcp-servers/github-mcp/github_mcp/server.py`

**Purpose:** Fetches real commits, PRs, reviews, and comments from GitHub, correlates them with Jira tickets, and generates AI-powered narratives.

**Usage Example:**
```python
# In Cursor, use the MCP tool:
generate_commit_narratives(
    owner="your-org",
    repo="your-repo",
    since="2024-01-01T00:00:00Z",
    max_tickets=10
)
```

**What it does:**
- ✅ Fetches commits from GitHub
- ✅ Gets all PRs (open and closed)
- ✅ Retrieves PR reviews and comments
- ✅ Groups everything by Jira ticket ID (e.g., PROJ-123)
- ✅ Sends to backend API for AI narrative generation
- ✅ Returns structured timeline data

---

### 2. Jira MCP Tool: `detect_workflow_anomalies`
**Location:** `/mcp-servers/jira-mcp/jira_mcp/server.py`

**Purpose:** Analyzes Jira tickets and detects workflow issues like stale tickets, scope creep, status mismatches, and task switching.

**Usage Example:**
```python
# In Cursor, use the MCP tool:
detect_workflow_anomalies(
    project_key="PROJ",
    github_owner="your-org",  # optional
    github_repo="your-repo",  # optional
    days_back=30,
    max_anomalies=20
)
```

**What it does:**
- ✅ Fetches Jira issues from the last N days
- ✅ Analyzes status history and transitions
- ✅ Gets comment counts and activity metrics
- ✅ Detects 5 types of anomalies:
  - 🔴 Stale tickets (no activity for 5+ days)
  - 🔴 Scope creep (work after "Done")
  - 🟡 Status mismatches (status doesn't match reality)
  - 🟡 Task switching (developer on too many tickets)
  - 🔵 Other workflow issues
- ✅ Sends to backend for AI analysis

---

### 3. Backend API Endpoints

#### Narratives API
**Location:** `/backend/app/routes/narratives.py`

**Endpoints:**
- `POST /api/narratives/generate` - Generate narratives from GitHub data
- `GET /api/narratives/list` - Get all stored narratives
- `GET /api/narratives/{ticket_id}` - Get specific ticket narrative

**What it does:**
- ✅ Receives raw commit/PR/review data
- ✅ Builds chronological timeline
- ✅ Generates human-readable narrative
- ✅ Extracts insights (delays, blockers, resolutions)
- ✅ Stores in memory (can be replaced with DB)

#### Anomalies API
**Location:** `/backend/app/routes/anomalies.py`

**Endpoints:**
- `POST /api/anomalies/detect` - Detect anomalies from Jira data
- `GET /api/anomalies/list` - Get all detected anomalies
- `GET /api/anomalies/{anomaly_id}` - Get specific anomaly

**What it does:**
- ✅ Analyzes ticket status and activity patterns
- ✅ Detects stale tickets, scope creep, etc.
- ✅ Generates AI analysis and suggested actions
- ✅ Calculates metrics and trends
- ✅ Stores in memory (can be replaced with DB)

---

### 4. Frontend Components with Data Toggle

#### Commit Narratives Component
**Location:** `/frontend/src/components/CommitNarrative.tsx`

**New Features:**
- ✅ **Mock Data / Real-Time Data toggle buttons** at the top
- ✅ **Fetches real narratives** from backend on button click
- ✅ **Error handling** with user-friendly messages
- ✅ **Loading states** while fetching data
- ✅ **100% backwards compatible** - all mockup data preserved!

**How to Use:**
1. Click "Mock Data" button → Shows existing mockup narratives
2. Click "Real-Time Data" button → Fetches from backend API
3. Toggle between them anytime during demo

#### Anomaly Detection Component
**Location:** `/frontend/src/components/AnomalyDetector.tsx`

**New Features:**
- ✅ **Mock Data / Real-Time Data toggle buttons**
- ✅ **Fetches real anomalies** from backend
- ✅ **Updates statistics** dynamically (high/medium/low counts)
- ✅ **Filter support** works with both data sources
- ✅ **All mockup data preserved!**

**How to Use:**
1. Click "Mock Data" → Shows 6 example anomalies
2. Click "Real-Time Data" → Loads detected anomalies from backend
3. Use filters (severity/type) with either data source

---

## 🚀 How to Demo This

### Option 1: Mock Data (Safe for Demo)
1. Open the dashboard
2. Navigate to "Commit Narratives" tab
3. Click **"Mock Data"** button (default)
4. Show the beautiful mockup narratives
5. Same for "Anomaly Detection" tab

**Advantage:** Always works, looks polished, no backend needed

---

### Option 2: Real-Time Data (Show Live Integration)

#### Prerequisites:
1. Backend must be running: `cd backend && uvicorn main:app --reload`
2. MCP servers must be configured in Cursor

#### Steps for Commit Narratives:
```bash
# 1. In Cursor, call the GitHub MCP tool:
generate_commit_narratives(
    owner="your-github-org",
    repo="your-repo",
    since="2024-01-01T00:00:00Z",
    max_tickets=5
)

# 2. In frontend, click "Real-Time Data" button
# 3. Real narratives will load from backend!
```

#### Steps for Anomaly Detection:
```bash
# 1. In Cursor, call the Jira MCP tool:
detect_workflow_anomalies(
    project_key="SCRUM",  # Your Jira project
    days_back=30,
    max_anomalies=10
)

# 2. In frontend, click "Real-Time Data" button
# 3. Real anomalies will appear!
```

**Advantage:** Shows live integration, real data from your actual projects

---

## 📁 File Changes Summary

### New Files Created:
- `/backend/app/routes/narratives.py` - Narratives API
- `/backend/app/routes/anomalies.py` - Anomalies API
- `/REAL_TIME_DATA_IMPLEMENTATION.md` - This document

### Modified Files:
- `/mcp-servers/github-mcp/github_mcp/server.py` - Added `generate_commit_narratives` tool
- `/mcp-servers/github-mcp/github_mcp/client.py` - Added `list_issue_comments` method
- `/mcp-servers/jira-mcp/jira_mcp/server.py` - Added `detect_workflow_anomalies` tool
- `/backend/main.py` - Registered new API routes
- `/frontend/src/components/CommitNarrative.tsx` - Added real-time data toggle
- `/frontend/src/components/AnomalyDetector.tsx` - Added real-time data toggle

### No Files Deleted:
✅ **All mockup data preserved!** Nothing was removed.

---

## 🎯 Demo Strategy Recommendation

### For Hackathon Judges:

**Part 1: Show Mock Data (2 minutes)**
- Start with mockup data to show the concept
- Explain the AI-generated narratives
- Show the anomaly detection insights

**Part 2: Toggle to Real-Time (3 minutes)**
- Click "Real-Time Data" button
- Explain: "This fetches from our live backend API"
- Show that MCP tools can generate this on-demand
- Demonstrate the data flow:
  ```
  MCP Tool → GitHub/Jira APIs → Backend Processing → Frontend Display
  ```

**Part 3: If Time Allows (2 minutes)**
- Open Cursor
- Run MCP tool live
- Show data appearing in frontend immediately

---

## 🔧 Testing Your Implementation

### Test Backend APIs:
```bash
# Start backend
cd /Users/ashishthanga/Desktop/HackASU/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload

# Test narratives endpoint
curl http://localhost:8000/api/narratives/list

# Test anomalies endpoint
curl http://localhost:8000/api/anomalies/list
```

### Test MCP Tools:
```bash
# In Cursor, open the MCP tools panel and try:
1. generate_commit_narratives - Should return JSON with ticket data
2. detect_workflow_anomalies - Should return JSON with anomalies
```

### Test Frontend:
```bash
cd /Users/ashishthanga/Desktop/HackASU/frontend
npm run dev

# Open http://localhost:3000
# Navigate to Commit Narratives tab
# Click "Real-Time Data" button
# Should either show data or helpful error message
```

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMMIT NARRATIVES FLOW                    │
└─────────────────────────────────────────────────────────────┘

1. User runs MCP tool in Cursor
   ↓
2. GitHub MCP fetches: commits, PRs, reviews, comments
   ↓
3. Groups by Jira ticket ID (PROJ-123)
   ↓
4. Sends to Backend API: POST /api/narratives/generate
   ↓
5. Backend builds timeline, generates narrative, extracts insights
   ↓
6. Stores in memory
   ↓
7. Frontend clicks "Real-Time Data"
   ↓
8. Fetches: GET /api/narratives/list
   ↓
9. Displays in UI with timeline


┌─────────────────────────────────────────────────────────────┐
│                  ANOMALY DETECTION FLOW                      │
└─────────────────────────────────────────────────────────────┘

1. User runs MCP tool in Cursor
   ↓
2. Jira MCP fetches: issues, changelog, comments
   ↓
3. Analyzes status history, activity patterns
   ↓
4. Sends to Backend API: POST /api/anomalies/detect
   ↓
5. Backend detects: stale tickets, scope creep, mismatches, etc.
   ↓
6. Generates AI analysis and suggested actions
   ↓
7. Stores in memory
   ↓
8. Frontend clicks "Real-Time Data"
   ↓
9. Fetches: GET /api/anomalies/list
   ↓
10. Displays with filtering and detail modals
```

---

## 🎨 UI/UX Features

### Data Source Toggle
- **Position:** Top right of each component
- **States:**
  - Mock Data (highlighted in maroon when active)
  - Real-Time Data (highlighted in maroon when active)
- **Loading:** Shows "Loading..." text while fetching
- **Disabled:** Buttons disabled during fetch

### Error Handling
- **Red banner** appears if backend is unreachable
- **User-friendly messages:**
  - "No real-time narratives available. Generate narratives using the MCP tool."
  - "Failed to fetch real-time data. Make sure the backend is running."
- **Auto-clears** when switching back to mock data

### Empty States
- Shows helpful message when no data available
- Prompts user to generate data using MCP tools
- Maintains professional look even with no data

---

## 🔐 Environment Variables

Make sure these are set:

**Backend (.env):**
```bash
BACKEND_API_URL=http://localhost:8000
```

**MCP Servers:**
```bash
# GitHub MCP
GITHUB_TOKEN=your_github_token

# Jira MCP
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token
```

---

## 🚨 Important Notes

### ✅ WHAT WAS PRESERVED:
- **ALL mockup data** in both components
- **All UI styling** and theming
- **All existing functionality**
- **Dark/light mode** support
- **Filtering and sorting** features

### ⚡ WHAT WAS ADDED:
- **Two MCP tools** (generate_commit_narratives, detect_workflow_anomalies)
- **Two API endpoints** (/api/narratives, /api/anomalies)
- **Data source toggles** in both frontend components
- **Error handling** and loading states
- **Real-time data fetching** from backend

### 🎯 FOR THE DEMO:
1. **Default is Mock Data** - Always safe to demo
2. **Real-Time is optional** - Only use if you've generated data
3. **Toggle anytime** - Switch between modes seamlessly
4. **No breaking changes** - Everything still works as before

---

## 🏆 Success Criteria

Your implementation is successful if:

- ✅ Mock data button shows existing narratives/anomalies
- ✅ Real-time button fetches from backend (or shows error)
- ✅ Toggle switches between modes smoothly
- ✅ All original mockup data is preserved
- ✅ MCP tools can generate and send data to backend
- ✅ Backend APIs process and store the data
- ✅ Frontend displays real data when available

---

## 🤝 Need Help?

### Common Issues:

**"Backend API is unreachable"**
- Make sure backend is running: `uvicorn main:app --reload`
- Check URL is `http://localhost:8000`

**"No narratives/anomalies available"**
- Run the MCP tools in Cursor first
- They need to generate data before frontend can fetch it

**"MCP tool not found"**
- Check MCP servers are configured in Cursor settings
- Verify environment variables are set

---

## 📈 Future Enhancements

**For production (after hackathon):**
1. Replace in-memory storage with PostgreSQL/MongoDB
2. Add authentication/authorization
3. Implement real AI/LLM for narrative generation (currently uses templates)
4. Add data caching and refresh intervals
5. WebSocket support for live updates
6. Export narratives/anomalies to PDF/CSV
7. Advanced filtering and search
8. Dashboard for tracking anomaly trends over time

---

## 🎉 You're All Set!

Your Commit Narratives and Anomaly Detection features now support both:
1. **Mock Data** - Beautiful, polished examples for demo
2. **Real-Time Data** - Live integration with GitHub and Jira

Switch between them with a single click. Your mockup data is safe. Your real data is ready when you are.

**Good luck with your hackathon demo! 🚀**

