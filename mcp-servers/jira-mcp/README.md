# Jira MCP Server

MCP server for Jira API integration.

## Setup

### Quick Setup

```bash
cd mcp-servers/jira-mcp
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

1. Get Jira API token:
   - For Cloud: https://id.atlassian.com/manage-profile/security/api-tokens
   - For Server/DC: Profile → Personal Access Tokens

2. Create `.env` file:
   ```
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your_email@example.com
   JIRA_API_TOKEN=your_api_token_here
   ```

   Or for Server/Data Center:
   ```
   JIRA_URL=https://jira.your-company.com
   JIRA_PERSONAL_TOKEN=your_personal_token_here
   ```

3. Add to Cursor MCP config (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["-m", "jira_mcp.cli"],
      "cwd": "/path/to/HackASU/mcp-servers/jira-mcp",
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your_email@example.com",
        "JIRA_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

4. Restart Cursor

## Tools

### Project Management
- `list_projects` - List all Jira projects
- `get_project` - Get project details

### Issue Management
- `get_issue` - Get issue details with changelog
- `search_issues` - Search issues using JQL
- `get_issue_changelog` - Get issue status transitions
- `get_issue_comments` - Get issue comments

### Agile/Boards
- `get_boards` - Get agile boards
- `get_board_sprints` - Get sprints for a board

## Use Cases

### Anomaly Detection
Use `search_issues` with JQL to find:
- Issues in "In Progress" status
- Issues marked "Done" with recent activity
- Issues without linked commits/PRs

### Commit-to-Ticket Narrative
Use `get_issue` with expand="changelog" and `get_issue_comments` to:
- Get status transitions
- Get comments and discussions
- Generate narratives from ticket activity

## Requirements

- Python 3.10+
- Jira Cloud or Server/Data Center 8.14+
- Jira API token (Cloud) or Personal Access Token (Server/DC)

## Authentication

### Jira Cloud
- `JIRA_URL`: Your Atlassian domain (e.g., `https://your-domain.atlassian.net`)
- `JIRA_EMAIL`: Your Atlassian account email
- `JIRA_API_TOKEN`: API token from https://id.atlassian.com/manage-profile/security/api-tokens

### Jira Server/Data Center
- `JIRA_URL`: Your Jira instance URL
- `JIRA_PERSONAL_TOKEN`: Personal Access Token from your Jira profile

## Test

Ask Cursor: "List all projects from Jira"

