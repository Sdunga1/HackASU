# DevAI Manager Backend

FastAPI backend server for DevAI Manager.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Update `.env` with your API keys:
- Claude API key
- GitHub token
- Jira credentials (optional)

5. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## API Endpoints

### Issues
- `GET /api/issues` - Get all issues
- `GET /api/issues/{issue_id}` - Get specific issue
- `POST /api/issues/{issue_id}/assign` - Assign issue

### Stats
- `GET /api/stats` - Get project statistics

### AI
- `GET /api/ai/recommend-assignment/{issue_id}` - Get AI recommendation for issue assignment
- `POST /api/ai/analyze-issue` - Analyze issue with AI

## Development

The backend uses FastAPI with:
- Pydantic for data validation
- httpx for external API calls
- Python-dotenv for environment variables

## Project Structure

```
backend/
├── app/
│   ├── routes/       # API route handlers
│   ├── services/     # Business logic and external API clients
│   ├── models.py     # Pydantic models
│   └── config.py     # Configuration settings
└── main.py           # FastAPI application entry point
```

