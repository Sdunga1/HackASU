# HackASU MCP Server

Unified MCP server for GitHub and Jira integration.

## Setup

```bash
cd mcp-servers/hackasu_mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Configuration

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "HackASU": {
      "command": "/path/to/hackasu_mcp/venv/bin/python",
      "args": ["/path/to/hackasu_mcp/cli.py"],
      "env": {
        "GITHUB_TOKEN": "your_token",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your_email",
        "JIRA_API_TOKEN": "your_token",
        "BACKEND_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

Restart Cursor.

## Tools

**GitHub:** 7 tools (prefix: `github_`)  
**Jira:** 20 tools (prefix: `jira_`)  
**Unified:** 4 cross-platform tools  
**SRS:** Process SRS documents and create sprints

See code for full tool list.
