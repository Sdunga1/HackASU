# Quick Start Guide

Get up and running with DevAI Manager in minutes.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

## Setup Steps

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with API URL (default: http://localhost:8000)
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Verify Setup

1. Open `http://localhost:3000` in your browser
2. You should see the dashboard with mock data
3. Check `http://localhost:8000/docs` for API documentation

## Environment Variables

### Backend (.env)
```
CLAUDE_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_token_here
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

1. Configure your GitHub and Jira credentials
2. Connect your repositories
3. Start using AI-powered issue assignment
4. Explore the dashboard features

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python version (3.11+)
- Ensure all dependencies are installed

### Frontend won't start
- Check if port 3000 is available
- Verify Node.js version (18+)
- Run `npm install` again

### API connection issues
- Verify backend is running on port 8000
- Check `.env.local` has correct API URL
- Check browser console for errors

## Development Tips

- Backend auto-reloads on file changes (--reload flag)
- Frontend has hot reload enabled
- API docs available at `/docs` endpoint
- Use browser DevTools for debugging

