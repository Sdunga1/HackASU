# DevAI Manager

AI-powered project management tool for GitHub and Jira workflows.

## Quick Start

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# MCP Server
cd mcp-servers/hackasu_mcp && pip install -r requirements.txt && pip install -e .
```

## Environment Variables

**Backend (.env):**
```
CLAUDE_API_KEY=your_key
GITHUB_TOKEN=your_token
JIRA_URL=your_jira_url
JIRA_EMAIL=your_email
JIRA_API_TOKEN=your_token
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

- Unified GitHub & Jira MCP server
- AI-powered sprint generation from SRS documents
- Real-time dashboard with WebSocket updates
- Cross-platform issue sync and project health monitoring

Built for HackASU 2025
