# GitHub MCP Server

MCP server for GitHub API integration.

## Setup

### Quick Setup

```bash
cd mcp-servers/github-mcp
./setup.sh
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Configure

1. Get GitHub token from https://github.com/settings/tokens
2. Create `.env` file: `GITHUB_TOKEN=your_token_here`
3. Add to Cursor MCP config (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["-m", "github_mcp.cli"],
      "cwd": "/path/to/HackASU/mcp-servers/github-mcp",
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

4. Restart Cursor

## Tools

- `list_commits` - List commits
- `get_commit` - Get commit details
- `list_pull_requests` - List PRs
- `get_pull_request` - Get PR details
- `list_issues` - List issues
- `get_issue` - Get issue details

## Requirements

- Python 3.10+
- GitHub Personal Access Token
