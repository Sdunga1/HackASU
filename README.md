# DevAI Manager

An AI-powered project management tool that intelligently manages GitHub and Jira workflows, providing intelligent issue assignment, project insights, and real-time visualization for development teams.

## Features

- 🤖 AI-powered issue assignment using Claude API
- 📊 Interactive dashboard for project visualization
- 🔗 GitHub and Jira integration via MCP
- 📈 Real-time project health monitoring
- 🎯 Intelligent dependency tracking

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI
- **AI**: Claude API
- **Integrations**: GitHub API, Jira API
- **Protocol**: MCP (Model Context Protocol)

## Project Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend server
├── mcp-servers/       # MCP server implementations
│   ├── github-mcp/   # GitHub MCP server
│   └── jira-mcp/     # Jira MCP server
└── docs/             # Documentation
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- GitHub personal access token
- Jira API token (optional for initial setup)
- Claude API key

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API endpoints
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
```

Backend API will be available at `http://localhost:8000`

### MCP Servers

MCP servers are currently in development. Setup instructions will be added soon.

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
CLAUDE_API_KEY=your_claude_api_key
GITHUB_TOKEN=your_github_token
JIRA_URL=your_jira_url
JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_api_token
```

## Development

### Running the full stack

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`

### API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT License

## Team

Built for HackASU 2025

