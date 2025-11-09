# Testing SRS Processing

## Quick Test Steps

### 1. Make sure backend is running

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Process SRS using the test script

```bash
cd /Users/sarathkumardunga/Desktop/HackASU
./test_srs_processing.sh
```

### 3. Or use Cursor with MCP (Recommended)

In Cursor, ask:

```
"Read the SRS document from Google Docs at https://docs.google.com/document/d/1rMsinj_SC8dcTViQslZul4EapgHgk4npu1arQOIECZo/edit and send sprints to the dashboard"
```

## Troubleshooting

### If you get "404 Not Found" error:

1. Check if backend server is running: `curl http://localhost:8000/health`
2. Restart the backend server to pick up code changes
3. Verify Claude API key is set in `backend/.env`

### If you get "model not found" error:

- The model name in `backend/app/services/srs_service.py` should be `claude-3-5-sonnet-20240620`

### If sprints don't appear in dashboard:

1. Check browser console for errors
2. Verify WebSocket connection is working
3. Check backend logs for processing errors
4. Verify sprints were created: `curl http://localhost:8000/api/srs/sprints`

## Expected Result

After successful processing, you should see:

- Sprints section with sprint cards below Issues
- User stories section with all user stories
- Click on a sprint to see its user stories
- Real-time updates via WebSocket
