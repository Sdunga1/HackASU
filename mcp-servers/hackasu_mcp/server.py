import json
import os
from datetime import datetime
from typing import Optional, List
from loguru import logger
from mcp.server.fastmcp import FastMCP
from client import GitHubClient, JiraClient
import requests

# Create unified MCP server
mcp = FastMCP("HackASU-MCP-Server")

# Global client instances
github_client = GitHubClient()
jira_client = JiraClient()

# ============================================================================
# GitHub Tools (prefix: github_)
# ============================================================================

@mcp.tool()
def github_list_commits(
    owner: str,
    repo: str,
    sha: Optional[str] = None,
    since: Optional[str] = None,
    author: Optional[str] = None,
    page: int = 1,
    per_page: int = 30
) -> str:
    """List commits from a GitHub repository"""
    try:
        logger.info(f"Listing commits for {owner}/{repo}")
        commits = github_client.list_commits(
            owner=owner,
            repo=repo,
            sha=sha,
            since=since,
            author=author,
            page=page,
            per_page=per_page
        )
        
        # Format response
        formatted_commits = []
        for commit in commits:
            formatted_commits.append({
                "sha": commit.get("sha"),
                "author": commit.get("commit", {}).get("author", {}).get("name"),
                "author_login": commit.get("author", {}).get("login") if commit.get("author") else None,
                "message": commit.get("commit", {}).get("message"),
                "date": commit.get("commit", {}).get("author", {}).get("date"),
                "url": commit.get("html_url"),
                "stats": commit.get("stats", {}),
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_commits)} commits",
            "commits": formatted_commits,
            "count": len(formatted_commits),
            "repository": f"{owner}/{repo}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing commits: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list commits: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_get_commit(owner: str, repo: str, sha: str) -> str:
    """Get detailed information about a specific GitHub commit"""
    try:
        logger.info(f"Getting commit {sha} from {owner}/{repo}")
        commit = github_client.get_commit(owner=owner, repo=repo, sha=sha)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved commit {sha}",
            "commit": {
                "sha": commit.get("sha"),
                "author": commit.get("commit", {}).get("author", {}).get("name"),
                "author_login": commit.get("author", {}).get("login") if commit.get("author") else None,
                "message": commit.get("commit", {}).get("message"),
                "date": commit.get("commit", {}).get("author", {}).get("date"),
                "url": commit.get("html_url"),
                "stats": commit.get("stats", {}),
                "files": [
                    {
                        "filename": f.get("filename"),
                        "status": f.get("status"),
                        "additions": f.get("additions"),
                        "deletions": f.get("deletions"),
                        "changes": f.get("changes"),
                    }
                    for f in commit.get("files", [])
                ],
            },
            "repository": f"{owner}/{repo}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting commit: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get commit: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    base: Optional[str] = None,
    page: int = 1,
    per_page: int = 30
) -> str:
    """List pull requests from a GitHub repository"""
    try:
        logger.info(f"Listing pull requests for {owner}/{repo} (state: {state})")
        prs = github_client.list_pull_requests(
            owner=owner,
            repo=repo,
            state=state,
            base=base,
            page=page,
            per_page=per_page
        )
        
        formatted_prs = []
        for pr in prs:
            formatted_prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "author": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "merged_at": pr.get("merged_at"),
                "mergeable": pr.get("mergeable"),
                "mergeable_state": pr.get("mergeable_state"),
                "draft": pr.get("draft"),
                "url": pr.get("html_url"),
                "head": pr.get("head", {}).get("ref"),
                "base": pr.get("base", {}).get("ref"),
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_prs)} pull requests",
            "pull_requests": formatted_prs,
            "count": len(formatted_prs),
            "repository": f"{owner}/{repo}",
            "state": state
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing pull requests: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list pull requests: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_get_pull_request(owner: str, repo: str, pr_number: int) -> str:
    """Get detailed information about a specific GitHub pull request"""
    try:
        logger.info(f"Getting pull request #{pr_number} from {owner}/{repo}")
        pr = github_client.get_pull_request(owner=owner, repo=repo, pr_number=pr_number)
        
        # Get reviews
        try:
            reviews = github_client.list_pull_request_reviews(owner=owner, repo=repo, pr_number=pr_number)
            review_summary = {
                "total": len(reviews),
                "approved": len([r for r in reviews if r.get("state") == "APPROVED"]),
                "changes_requested": len([r for r in reviews if r.get("state") == "CHANGES_REQUESTED"]),
                "commented": len([r for r in reviews if r.get("state") == "COMMENTED"]),
            }
        except Exception as e:
            logger.warning(f"Could not fetch reviews: {e}")
            review_summary = None
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved pull request #{pr_number}",
            "pull_request": {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "author": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "merged_at": pr.get("merged_at"),
                "mergeable": pr.get("mergeable"),
                "mergeable_state": pr.get("mergeable_state"),
                "draft": pr.get("draft"),
                "additions": pr.get("additions"),
                "deletions": pr.get("deletions"),
                "changed_files": pr.get("changed_files"),
                "url": pr.get("html_url"),
                "head": pr.get("head", {}).get("ref"),
                "base": pr.get("base", {}).get("ref"),
                "reviews": review_summary,
            },
            "repository": f"{owner}/{repo}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting pull request: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get pull request: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    assignee: Optional[str] = None,
    labels: Optional[str] = None,
    page: int = 1,
    per_page: int = 30
) -> str:
    """List issues from a GitHub repository"""
    try:
        logger.info(f"Listing issues for {owner}/{repo} (state: {state})")
        issues = github_client.list_issues(
            owner=owner,
            repo=repo,
            state=state,
            assignee=assignee,
            labels=labels,
            page=page,
            per_page=per_page
        )
        
        formatted_issues = []
        for issue in issues:
            # Skip pull requests (GitHub API returns PRs as issues)
            if issue.get("pull_request"):
                continue
            
            formatted_issues.append({
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "author": issue.get("user", {}).get("login"),
                "assignees": [a.get("login") for a in issue.get("assignees", [])],
                "labels": [l.get("name") for l in issue.get("labels", [])],
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "url": issue.get("html_url"),
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_issues)} issues",
            "issues": formatted_issues,
            "count": len(formatted_issues),
            "repository": f"{owner}/{repo}",
            "state": state
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_get_issue(owner: str, repo: str, issue_number: int) -> str:
    """Get detailed information about a specific GitHub issue"""
    try:
        logger.info(f"Getting GitHub issue #{issue_number} from {owner}/{repo}")
        issue = github_client.get_issue(owner=owner, repo=repo, issue_number=issue_number)
        
        # Skip if it's a pull request
        if issue.get("pull_request"):
            return json.dumps({
                "status": "error",
                "message": f"Issue #{issue_number} is a pull request. Use get_pull_request instead."
            }, indent=2)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved issue #{issue_number}",
            "issue": {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "author": issue.get("user", {}).get("login"),
                "assignees": [a.get("login") for a in issue.get("assignees", [])],
                "labels": [l.get("name") for l in issue.get("labels", [])],
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "body": issue.get("body"),
                "comments": issue.get("comments"),
                "url": issue.get("html_url"),
            },
            "repository": f"{owner}/{repo}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def github_send_issues_to_dashboard(owner: str, repo: str, state: str = "open") -> str:
    """Fetch issues from GitHub and send them to the frontend dashboard via backend API"""
    try:
        logger.info(f"Fetching issues for {owner}/{repo} to send to dashboard")
        
        # Get issues using existing client
        issues = github_client.list_issues(
            owner=owner,
            repo=repo,
            state=state
        )
        
        # Format issues for dashboard
        formatted_issues = []
        for issue in issues:
            if issue.get("pull_request"):
                continue
            
            formatted_issues.append({
                "id": str(issue.get("number")),
                "title": issue.get("title"),
                "status": issue.get("state"),
                "assignee": issue.get("assignees")[0].get("login") if issue.get("assignees") else None,
                "priority": "medium",  # Default priority
                "createdAt": issue.get("created_at"),
                "labels": [l.get("name") for l in issue.get("labels", [])],
                "url": issue.get("html_url"),
            })
        
        # Send to backend API
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        api_endpoint = f"{backend_url}/api/dashboard/sync-issues"
        
        try:
            response = requests.post(
                api_endpoint,
                json={
                    "repository": f"{owner}/{repo}",
                    "issues": formatted_issues,
                    "timestamp": None  # Backend will add timestamp
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return json.dumps({
                    "status": "success",
                    "message": f"Successfully sent {len(formatted_issues)} issues to dashboard",
                    "count": len(formatted_issues),
                    "repository": f"{owner}/{repo}",
                    "dashboard_response": response.json()
                }, indent=2)
            else:
                return json.dumps({
                    "status": "partial_success",
                    "message": f"Fetched {len(formatted_issues)} issues but failed to send to dashboard",
                    "issues": formatted_issues,
                    "error": f"Backend responded with status {response.status_code}"
                }, indent=2)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach backend API: {e}")
            return json.dumps({
                "status": "partial_success",
                "message": f"Fetched {len(formatted_issues)} issues but backend API is unreachable",
                "issues": formatted_issues,
                "error": str(e)
            }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in send_issues_to_dashboard: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to fetch/send issues: {str(e)}"
        }, indent=2)

# ============================================================================
# Jira Tools
# ============================================================================

@mcp.tool()
def jira_list_projects(include_archived: bool = False) -> str:
    """List all Jira projects visible to the user"""
    try:
        logger.info("Listing Jira projects")
        projects = jira_client.list_projects(include_archived=include_archived)
        
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "key": project.get("key"),
                "name": project.get("name"),
                "id": project.get("id"),
                "projectTypeKey": project.get("projectTypeKey"),
                "archived": project.get("archived", False),
                "url": f"{jira_client.url}/browse/{project.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_projects)} projects",
            "projects": formatted_projects,
            "count": len(formatted_projects)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list projects: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_project(project_key: str) -> str:
    """Get detailed information about a specific Jira project"""
    try:
        logger.info(f"Getting project {project_key}")
        project = jira_client.get_project(project_key)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved project {project_key}",
            "project": {
                "key": project.get("key"),
                "name": project.get("name"),
                "id": project.get("id"),
                "projectTypeKey": project.get("projectTypeKey"),
                "archived": project.get("archived", False),
                "description": project.get("description"),
                "lead": project.get("lead", {}).get("displayName") if project.get("lead") else None,
                "url": f"{jira_client.url}/browse/{project.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get project: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_issue(issue_key: str, expand: Optional[str] = None) -> str:
    """Get detailed information about a specific Jira issue"""
    try:
        logger.info(f"Getting Jira issue {issue_key}")
        expand_fields = expand or "changelog,renderedFields"
        issue = jira_client.get_issue(issue_key, expand=expand_fields)
        
        fields = issue.get("fields", {})
        changelog = issue.get("changelog", {})
        
        # Extract status transitions from changelog
        status_transitions = []
        if changelog and changelog.get("histories"):
            for history in changelog.get("histories", []):
                for item in history.get("items", []):
                    if item.get("field") == "status":
                        status_transitions.append({
                            "from": item.get("fromString"),
                            "to": item.get("toString"),
                            "changed_at": history.get("created"),
                            "changed_by": history.get("author", {}).get("displayName") if history.get("author") else None,
                        })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved issue {issue_key}",
            "issue": {
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields.get("summary"),
                "description": fields.get("description"),
                "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                "status_id": fields.get("status", {}).get("id") if fields.get("status") else None,
                "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "assignee_email": fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None,
                "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None,
                "resolution_date": fields.get("resolutiondate"),
                "labels": fields.get("labels", []),
                "components": [c.get("name") for c in fields.get("components", [])],
                "fix_versions": [v.get("name") for v in fields.get("fixVersions", [])],
                "status_transitions": status_transitions,
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_issue_changelog(issue_key: str, max_results: int = 100) -> str:
    """Get Jira issue changelog (status transitions and field changes)"""
    try:
        logger.info(f"Getting changelog for issue {issue_key}")
        changelog = jira_client.get_issue_changelog(issue_key, max_results=max_results)
        
        transitions = []
        for history in changelog.get("values", []):
            changes = []
            for item in history.get("items", []):
                changes.append({
                    "field": item.get("field"),
                    "field_type": item.get("fieldtype"),
                    "from": item.get("fromString"),
                    "to": item.get("toString"),
                    "from_id": item.get("from"),
                    "to_id": item.get("to"),
                })
            
            transitions.append({
                "id": history.get("id"),
                "author": history.get("author", {}).get("displayName") if history.get("author") else None,
                "created": history.get("created"),
                "changes": changes,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved changelog for {issue_key}",
            "issue_key": issue_key,
            "total": changelog.get("total", 0),
            "transitions": transitions,
            "count": len(transitions)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue changelog: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue changelog: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_issue_comments(issue_key: str, max_results: int = 100) -> str:
    """Get comments for a Jira issue"""
    try:
        logger.info(f"Getting comments for issue {issue_key}")
        comments_response = jira_client.get_issue_comments(issue_key, max_results=max_results)
        
        comments = []
        for comment in comments_response.get("comments", []):
            comments.append({
                "id": comment.get("id"),
                "author": comment.get("author", {}).get("displayName") if comment.get("author") else None,
                "author_email": comment.get("author", {}).get("emailAddress") if comment.get("author") else None,
                "body": comment.get("body"),
                "created": comment.get("created"),
                "updated": comment.get("updated"),
                "visibility": comment.get("visibility", {}).get("value") if comment.get("visibility") else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved comments for {issue_key}",
            "issue_key": issue_key,
            "total": comments_response.get("total", 0),
            "comments": comments,
            "count": len(comments)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue comments: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue comments: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_search_issues(
    jql: str,
    max_results: int = 50,
    fields: Optional[str] = None,
    expand: Optional[str] = None
) -> str:
    """Search for Jira issues using JQL (Jira Query Language)"""
    try:
        logger.info(f"Searching issues with JQL: {jql}")
        
        fields_list = None
        if fields:
            fields_list = [f.strip() for f in fields.split(",")]
        
        search_result = jira_client.search_issues(
            jql=jql,
            max_results=min(max_results, 100),
            fields=fields_list,
            expand=expand
        )
        
        issues = []
        for issue in search_result.get("issues", []):
            fields_data = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields_data.get("summary"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "issue_type": fields_data.get("issuetype", {}).get("name") if fields_data.get("issuetype") else None,
                "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                "reporter": fields_data.get("reporter", {}).get("displayName") if fields_data.get("reporter") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
                "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                "labels": fields_data.get("labels", []),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(issues)} issues",
            "jql": jql,
            "total": search_result.get("total", 0),
            "start_at": search_result.get("startAt", 0),
            "max_results": search_result.get("maxResults", 0),
            "issues": issues,
            "count": len(issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error searching issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to search issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_boards(project_key: Optional[str] = None, board_type: Optional[str] = None) -> str:
    """Get agile boards for a Jira project"""
    try:
        logger.info(f"Getting boards (project: {project_key}, type: {board_type})")
        boards_response = jira_client.get_boards(project_key=project_key, board_type=board_type)
        
        boards = []
        for board in boards_response.get("values", []):
            boards.append({
                "id": board.get("id"),
                "name": board.get("name"),
                "type": board.get("type"),
                "location": board.get("location", {}).get("projectName") if board.get("location") else None,
                "url": f"{jira_client.url}/jira/software/projects/{board.get('location', {}).get('projectKey', '')}/boards/{board.get('id')}" if jira_client.url and board.get("location") else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(boards)} boards",
            "boards": boards,
            "count": len(boards)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting boards: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get boards: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_board_sprints(board_id: int, state: Optional[str] = None) -> str:
    """Get sprints for a Jira agile board"""
    try:
        logger.info(f"Getting sprints for board {board_id} (state: {state})")
        sprints_response = jira_client.get_board_sprints(board_id=board_id, state=state)
        
        sprints = []
        for sprint in sprints_response.get("values", []):
            sprints.append({
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "start_date": sprint.get("startDate"),
                "end_date": sprint.get("endDate"),
                "complete_date": sprint.get("completeDate"),
                "goal": sprint.get("goal"),
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(sprints)} sprints",
            "board_id": board_id,
            "sprints": sprints,
            "count": len(sprints)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting board sprints: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get board sprints: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_get_board_issues(board_id: int, jql: Optional[str] = None, max_results: int = 50) -> str:
    """Get issues from a Jira board using the Agile API"""
    try:
        logger.info(f"Getting issues for board {board_id}")
        issues_response = jira_client.get_board_issues(
            board_id=board_id,
            jql=jql,
            max_results=min(max_results, 100)
        )
        
        issues = []
        for issue in issues_response.get("issues", []):
            fields_data = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields_data.get("summary"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "issue_type": fields_data.get("issuetype", {}).get("name") if fields_data.get("issuetype") else None,
                "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                "reporter": fields_data.get("reporter", {}).get("displayName") if fields_data.get("reporter") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
                "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                "labels": fields_data.get("labels", []),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(issues)} issues",
            "board_id": board_id,
            "total": issues_response.get("total", 0),
            "issues": issues,
            "count": len(issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting board issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get board issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[str] = None
) -> str:
    """Create a new Jira issue"""
    try:
        logger.info(f"Creating issue in project {project_key}")
        
        labels_list = None
        if labels:
            labels_list = [l.strip() for l in labels.split(",")]
        
        issue = jira_client.create_issue(
            project_key=project_key,
            summary=summary,
            issue_type=issue_type,
            description=description,
            assignee=assignee,
            priority=priority,
            labels=labels_list
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully created issue {issue.get('key')}",
            "issue": {
                "key": issue.get("key"),
                "id": issue.get("id"),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to create issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_update_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[str] = None
) -> str:
    """Update an existing Jira issue"""
    try:
        logger.info(f"Updating issue {issue_key}")
        
        labels_list = None
        if labels:
            labels_list = [l.strip() for l in labels.split(",")]
        
        jira_client.update_issue(
            issue_key=issue_key,
            summary=summary,
            description=description,
            assignee=assignee,
            priority=priority,
            labels=labels_list
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully updated issue {issue_key}",
            "issue_key": issue_key,
            "url": f"{jira_client.url}/browse/{issue_key}" if jira_client.url else None,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error updating issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to update issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_delete_issue(issue_key: str) -> str:
    """Delete a Jira issue"""
    try:
        logger.info(f"Deleting issue {issue_key}")
        jira_client.delete_issue(issue_key=issue_key)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully deleted issue {issue_key}",
            "issue_key": issue_key
        }, indent=2)
    except Exception as e:
        logger.error(f"Error deleting issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to delete issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_add_comment(issue_key: str, comment: str) -> str:
    """Add a comment to a Jira issue"""
    try:
        logger.info(f"Adding comment to issue {issue_key}")
        result = jira_client.add_comment(issue_key=issue_key, comment_text=comment)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully added comment to issue {issue_key}",
            "comment_id": result.get("id"),
            "issue_key": issue_key
        }, indent=2)
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to add comment: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_transition_issue(issue_key: str, transition_name: str, comment: Optional[str] = None) -> str:
    """Transition a Jira issue to a new status"""
    try:
        logger.info(f"Transitioning issue {issue_key} to {transition_name}")
        
        # Get available transitions
        transitions_response = jira_client.get_transitions(issue_key=issue_key)
        transitions = transitions_response.get("transitions", [])
        
        # Find matching transition
        transition_id = None
        for t in transitions:
            if t.get("name", "").lower() == transition_name.lower() or t.get("to", {}).get("name", "").lower() == transition_name.lower():
                transition_id = t.get("id")
                break
        
        if not transition_id:
            available = [t.get("name") or t.get("to", {}).get("name") for t in transitions]
            return json.dumps({
                "status": "error",
                "message": f"Transition '{transition_name}' not found. Available transitions: {', '.join(available)}"
            }, indent=2)
        
        jira_client.transition_issue(
            issue_key=issue_key,
            transition_id=transition_id,
            comment=comment
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully transitioned issue {issue_key} to {transition_name}",
            "issue_key": issue_key,
            "transition": transition_name
        }, indent=2)
    except Exception as e:
        logger.error(f"Error transitioning issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to transition issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_batch_create_issues(issues_json: str) -> str:
    """Create multiple Jira issues in a single request"""
    try:
        logger.info("Batch creating issues")
        issues = json.loads(issues_json)
        
        result = jira_client.batch_create_issues(issues=issues)
        
        created_issues = []
        errors = []
        
        for item in result.get("issues", []):
            if item:
                created_issues.append({
                    "key": item.get("key"),
                    "id": item.get("id"),
                    "url": f"{jira_client.url}/browse/{item.get('key')}" if jira_client.url else None,
                })
        
        for error in result.get("errors", []):
            errors.append(error)
        
        return json.dumps({
            "status": "success" if not errors else "partial_success",
            "message": f"Created {len(created_issues)} issues" + (f", {len(errors)} failed" if errors else ""),
            "created_issues": created_issues,
            "errors": errors,
            "count": len(created_issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error batch creating issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to batch create issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_create_sprint(
    board_id: int,
    name: str,
    start_date: str,
    end_date: str,
    goal: Optional[str] = None
) -> str:
    """Create a new sprint in Jira"""
    try:
        logger.info(f"Creating sprint '{name}' on board {board_id}")
        
        # Convert dates to ISO format if needed
        # Ensure dates are in proper format (YYYY-MM-DD or ISO format)
        sprint = jira_client.create_sprint(
            board_id=board_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            goal=goal
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully created sprint '{name}'",
            "sprint": {
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "start_date": sprint.get("startDate"),
                "end_date": sprint.get("endDate"),
                "goal": sprint.get("goal"),
                "url": f"{jira_client.url}/jira/software/projects/{sprint.get('originBoardId', '')}/boards/{board_id}/sprint/{sprint.get('id')}" if jira_client.url else None
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error creating sprint: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to create sprint: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_update_sprint(
    sprint_id: int,
    name: Optional[str] = None,
    state: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    goal: Optional[str] = None
) -> str:
    """Update an existing sprint in Jira"""
    try:
        logger.info(f"Updating sprint {sprint_id}")
        
        sprint = jira_client.update_sprint(
            sprint_id=sprint_id,
            name=name,
            state=state,
            start_date=start_date,
            end_date=end_date,
            goal=goal
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully updated sprint {sprint_id}",
            "sprint": sprint
        }, indent=2)
    except Exception as e:
        logger.error(f"Error updating sprint: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to update sprint: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_move_issue_to_sprint(issue_key: str, sprint_id: int) -> str:
    """Move a Jira issue to a sprint"""
    try:
        logger.info(f"Moving issue {issue_key} to sprint {sprint_id}")
        
        result = jira_client.move_issue_to_sprint(issue_key=issue_key, sprint_id=sprint_id)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully moved issue {issue_key} to sprint {sprint_id}",
            "issue_key": issue_key,
            "sprint_id": sprint_id
        }, indent=2)
    except Exception as e:
        logger.error(f"Error moving issue to sprint: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to move issue to sprint: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_create_sprints_from_json(
    sprints_json: str,
    board_id: int,
    project_key: str,
    create_issues: bool = True
) -> str:
    """Create Jira sprints and user stories from JSON data
    
    This tool takes sprints JSON (from SRS processing) and creates:
    1. Sprints in Jira
    2. User stories as Jira issues (optional)
    3. Links user stories to sprints
    
    Args:
        sprints_json: JSON string containing sprints array with user stories
        board_id: Jira board ID to create sprints on
        project_key: Jira project key for creating issues
        create_issues: Whether to create user stories as Jira issues (default: True)
    """
    try:
        logger.info(f"Creating sprints from JSON on board {board_id}")
        
        # Parse sprints JSON
        try:
            sprints_data = json.loads(sprints_json)
            if isinstance(sprints_data, dict):
                sprints = sprints_data.get("sprints", [])
            elif isinstance(sprints_data, list):
                sprints = sprints_data
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Invalid sprints JSON format. Expected array or object with 'sprints' key"
                }, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON format: {str(e)}"
            }, indent=2)
        
        if not sprints or len(sprints) == 0:
            return json.dumps({
                "status": "error",
                "message": "No sprints found in the provided JSON"
            }, indent=2)
        
        created_sprints = []
        created_issues = []
        errors = []
        
        # Create each sprint
        for sprint in sprints:
            try:
                sprint_name = sprint.get("name", f"Sprint {sprints.index(sprint) + 1}")
                start_date = sprint.get("startDate", "")
                end_date = sprint.get("endDate", "")
                goal = sprint.get("goal", "")
                
                # Convert dates to ISO format if needed
                # Handle YYYY-MM-DD format
                if start_date:
                    if "T" not in start_date:
                        # Assume YYYY-MM-DD format, add time
                        start_date = f"{start_date}T00:00:00.000Z"
                    elif not start_date.endswith("Z") and "+" not in start_date:
                        start_date = start_date + "Z"
                
                if end_date:
                    if "T" not in end_date:
                        # Assume YYYY-MM-DD format, add time (end of day)
                        end_date = f"{end_date}T23:59:59.999Z"
                    elif not end_date.endswith("Z") and "+" not in end_date:
                        end_date = end_date + "Z"
                
                # Create sprint in Jira
                jira_sprint = jira_client.create_sprint(
                    board_id=board_id,
                    name=sprint_name,
                    start_date=start_date,
                    end_date=end_date,
                    goal=goal
                )
                
                sprint_id = jira_sprint.get("id")
                created_sprints.append({
                    "sprint_id": sprint_id,
                    "name": sprint_name,
                    "jira_sprint": jira_sprint
                })
                
                # Create user stories as Jira issues if requested
                if create_issues:
                    user_stories = sprint.get("userStories", [])
                    for story in user_stories:
                        try:
                            story_title = story.get("title", "")
                            story_description = story.get("description", "")
                            story_points = story.get("storyPoints", 0)
                            priority = story.get("priority", "Medium").capitalize()
                            
                            # Create acceptance criteria text
                            acceptance_criteria = story.get("acceptanceCriteria", [])
                            criteria_text = "\n".join([f"- {criteria}" for criteria in acceptance_criteria])
                            
                            # Combine description with acceptance criteria
                            full_description = story_description
                            if criteria_text:
                                full_description += f"\n\n**Acceptance Criteria:**\n{criteria_text}"
                            if story_points:
                                full_description += f"\n\n**Story Points:** {story_points}"
                            
                            # Create issue in Jira
                            jira_issue = jira_client.create_issue(
                                project_key=project_key,
                                summary=story_title,
                                issue_type="Story",
                                description=full_description,
                                priority=priority,
                                labels=["user-story"]
                            )
                            
                            issue_key = jira_issue.get("key")
                            
                            # Move issue to sprint
                            try:
                                jira_client.move_issue_to_sprint(issue_key=issue_key, sprint_id=sprint_id)
                                logger.info(f"Created and moved issue {issue_key} to sprint {sprint_id}")
                            except Exception as move_error:
                                logger.warning(f"Created issue {issue_key} but could not move to sprint {sprint_id}: {move_error}")
                            
                            created_issues.append({
                                "issue_key": issue_key,
                                "sprint_id": sprint_id,
                                "title": story_title,
                                "moved_to_sprint": True
                            })
                            
                        except Exception as e:
                            errors.append({
                                "type": "issue_creation",
                                "sprint": sprint_name,
                                "story": story.get("title", "Unknown"),
                                "error": str(e)
                            })
                            logger.error(f"Error creating issue for story: {e}")
                
            except Exception as e:
                errors.append({
                    "type": "sprint_creation",
                    "sprint": sprint.get("name", "Unknown"),
                    "error": str(e)
                })
                logger.error(f"Error creating sprint: {e}")
        
        return json.dumps({
            "status": "success" if not errors else "partial_success",
            "message": f"Created {len(created_sprints)} sprints and {len(created_issues)} issues" + (f", {len(errors)} errors" if errors else ""),
            "created_sprints": created_sprints,
            "created_issues": created_issues,
            "errors": errors,
            "summary": {
                "sprints_created": len(created_sprints),
                "issues_created": len(created_issues),
                "errors": len(errors)
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error creating sprints from JSON: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to create sprints: {str(e)}"
        }, indent=2)

@mcp.tool()
def process_srs_and_create_sprints(
    srs_content: str,
    document_name: Optional[str] = None,
    document_url: Optional[str] = None,
    send_to_dashboard: bool = True,
    create_in_jira: bool = False,
    jira_board_id: Optional[int] = None,
    jira_project_key: Optional[str] = None
) -> str:
    """Process SRS document and create sprints
    
    This tool receives SRS content and provides the expected JSON format for sprints.
    The AI assistant (Cursor/Claude) should analyze the SRS content and generate sprints JSON
    following the format below, then call jira_send_sprints_to_dashboard or jira_create_sprints_from_json.
    
    Args:
        srs_content: SRS document content (from Google Docs MCP)
        document_name: Optional document name
        document_url: Optional document URL
        send_to_dashboard: Whether to send sprints to dashboard (default: True)
        create_in_jira: Whether to create sprints in Jira (default: False)
        jira_board_id: Jira board ID (required if create_in_jira=True)
        jira_project_key: Jira project key (required if create_in_jira=True)
    
    Note: The AI assistant will analyze the SRS content directly (no API call needed)
    and generate the sprints JSON based on the requirements in the document.
    """
    try:
        logger.info(f"Received SRS document: {document_name} ({len(srs_content)} chars)")
        
        # Return the expected format for sprints JSON
        return json.dumps({
            "status": "ready",
            "message": "SRS content received. Please analyze the content and generate sprints JSON in the format below.",
            "srs_info": {
                "length": len(srs_content),
                "document_name": document_name,
                "document_url": document_url,
                "preview": srs_content[:500] + "..." if len(srs_content) > 500 else srs_content
            },
            "expected_sprint_format": {
                "sprints": [
                    {
                        "name": "Sprint 1: Core Features",
                        "goal": "Implement core functionality based on requirements",
                        "startDate": "2024-01-01",
                        "endDate": "2024-01-14",
                        "userStories": [
                            {
                                "title": "User Story Title",
                                "description": "Detailed description of the user story",
                                "storyPoints": 5,
                                "priority": "high",
                                "acceptanceCriteria": [
                                    "Criteria 1",
                                    "Criteria 2"
                                ]
                            }
                        ]
                    }
                ]
            },
            "next_actions": [
                "1. Analyze the SRS content above and extract requirements",
                "2. Generate sprints with user stories based on the requirements",
                f"3. Call jira_send_sprints_to_dashboard with the generated JSON" if send_to_dashboard else "3. Skip dashboard sync",
                f"4. Call jira_create_sprints_from_json with board_id={jira_board_id}, project_key={jira_project_key}" if create_in_jira else "4. Skip Jira creation"
            ]
        }, indent=2)
    except Exception as e:
        logger.error(f"Error processing SRS: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to process SRS: {str(e)}"
        }, indent=2)

@mcp.tool()
def jira_send_sprints_to_dashboard(
    sprints_json: str,
    document_name: Optional[str] = None,
    document_url: Optional[str] = None
) -> str:
    """Send sprints and user stories to the dashboard"""
    try:
        logger.info("Sending sprints to dashboard")
        
        if not sprints_json or not sprints_json.strip():
            return json.dumps({
                "status": "error",
                "message": "Sprints JSON is required"
            }, indent=2)
        
        # Parse sprints JSON
        try:
            sprints_data = json.loads(sprints_json)
            # Handle both direct array and object with "sprints" key
            if isinstance(sprints_data, dict):
                sprints = sprints_data.get("sprints", [])
                srs_document = sprints_data.get("srs_document")
            elif isinstance(sprints_data, list):
                sprints = sprints_data
                srs_document = None
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Invalid sprints JSON format. Expected array or object with 'sprints' key"
                }, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON format: {str(e)}"
            }, indent=2)
        
        if not sprints or len(sprints) == 0:
            return json.dumps({
                "status": "error",
                "message": "No sprints found in the provided JSON"
            }, indent=2)
        
        # Ensure each sprint has required fields and user stories
        for sprint in sprints:
            if "id" not in sprint:
                sprint["id"] = f"sprint-{sprints.index(sprint) + 1}"
            if "userStories" not in sprint:
                sprint["userStories"] = []
            if "totalStoryPoints" not in sprint:
                sprint["totalStoryPoints"] = sum(story.get("storyPoints", 0) for story in sprint.get("userStories", []))
            if "completedStoryPoints" not in sprint:
                sprint["completedStoryPoints"] = 0
            if "progress" not in sprint:
                total = sprint.get("totalStoryPoints", 1)
                sprint["progress"] = int((sprint["completedStoryPoints"] / total) * 100) if total > 0 else 0
            
            # Ensure each user story has required fields
            for story in sprint.get("userStories", []):
                if "id" not in story:
                    story["id"] = f"us-{sprint['id']}-{sprint['userStories'].index(story) + 1}"
                if "status" not in story:
                    story["status"] = "todo"
                if "priority" not in story:
                    story["priority"] = "medium"
                if "acceptanceCriteria" not in story:
                    story["acceptanceCriteria"] = []
        
        # Send to backend API
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        api_endpoint = f"{backend_url}/api/srs/sync-sprints"
        
        try:
            response = requests.post(
                api_endpoint,
                json={
                    "sprints": sprints,
                    "srs_document": srs_document,
                    "document_name": document_name,
                    "document_url": document_url
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.dumps({
                    "status": "success",
                    "message": f"Successfully sent {len(sprints)} sprints to dashboard",
                    "sprints_count": len(sprints),
                    "total_user_stories": sum(len(s.get("userStories", [])) for s in sprints),
                    "dashboard_response": result
                }, indent=2)
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", error_detail)
                except:
                    pass
                
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to send sprints: Backend responded with status {response.status_code}",
                    "error": error_detail
                }, indent=2)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach backend API: {e}")
            return json.dumps({
                "status": "error",
                "message": f"Backend API is unreachable: {str(e)}",
                "error": "Make sure the backend server is running at " + backend_url
            }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in send_sprints_to_dashboard: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to send sprints: {str(e)}"
        }, indent=2)

# ============================================================================
# Unified/Cross-Platform Tools
# ============================================================================

@mcp.tool()
def sync_issue_github_to_jira(
    owner: str,
    repo: str,
    issue_number: int,
    jira_project_key: str,
    issue_type: str = "Task"
) -> str:
    """Sync a GitHub issue to Jira - Create Jira issue from GitHub issue"""
    try:
        logger.info(f"Syncing GitHub issue #{issue_number} to Jira project {jira_project_key}")
        
        # Get GitHub issue
        github_issue = github_client.get_issue(owner=owner, repo=repo, issue_number=issue_number)
        
        if github_issue.get("pull_request"):
            return json.dumps({
                "status": "error",
                "message": f"Issue #{issue_number} is a pull request, not an issue"
            }, indent=2)
        
        # Extract issue data
        title = github_issue.get("title", "")
        body = github_issue.get("body", "") or "No description"
        labels = [l.get("name") for l in github_issue.get("labels", [])]
        assignee = github_issue.get("assignees", [{}])[0].get("login") if github_issue.get("assignees") else None
        
        # Determine priority from labels
        priority = "Medium"
        if any("high" in l.lower() or "critical" in l.lower() for l in labels):
            priority = "High"
        elif any("low" in l.lower() for l in labels):
            priority = "Low"
        
        # Create description with link back to GitHub
        description = f"{body}\n\n---\n**Synced from GitHub:** {github_issue.get('html_url')}"
        
        # Create Jira issue
        jira_issue = jira_client.create_issue(
            project_key=jira_project_key,
            summary=title,
            issue_type=issue_type,
            description=description,
            priority=priority,
            labels=labels
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully synced GitHub issue #{issue_number} to Jira",
            "github_issue": {
                "number": issue_number,
                "url": github_issue.get("html_url")
            },
            "jira_issue": {
                "key": jira_issue.get("key"),
                "url": f"{jira_client.url}/browse/{jira_issue.get('key')}" if jira_client.url else None
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error syncing GitHub issue to Jira: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to sync issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_unified_project_health(
    github_owner: str,
    github_repo: str,
    jira_project_key: str
) -> str:
    """Get combined project health metrics from GitHub and Jira"""
    try:
        logger.info(f"Getting unified project health for {github_owner}/{github_repo} and Jira {jira_project_key}")
        
        # Get GitHub metrics
        github_issues = github_client.list_issues(owner=github_owner, repo=github_repo, state="all")
        github_open = len([i for i in github_issues if i.get("state") == "open" and not i.get("pull_request")])
        github_closed = len([i for i in github_issues if i.get("state") == "closed" and not i.get("pull_request")])
        github_prs_open = len([i for i in github_issues if i.get("pull_request") and i.get("state") == "open"])
        
        # Get Jira metrics
        jira_issues_result = jira_client.search_issues(
            jql=f"project = {jira_project_key}",
            max_results=100
        )
        jira_issues = jira_issues_result.get("issues", [])
        jira_open = len([i for i in jira_issues if i.get("fields", {}).get("status", {}).get("name") not in ["Done", "Closed", "Resolved"]])
        jira_closed = len([i for i in jira_issues if i.get("fields", {}).get("status", {}).get("name") in ["Done", "Closed", "Resolved"]])
        jira_in_progress = len([i for i in jira_issues if "progress" in i.get("fields", {}).get("status", {}).get("name", "").lower()])
        
        # Calculate combined metrics
        total_issues = github_open + github_closed + jira_open + jira_closed
        total_open = github_open + jira_open
        total_closed = github_closed + jira_closed
        completion_rate = (total_closed / total_issues * 100) if total_issues > 0 else 0
        
        return json.dumps({
            "status": "success",
            "message": "Unified project health metrics",
            "github": {
                "open_issues": github_open,
                "closed_issues": github_closed,
                "open_pull_requests": github_prs_open,
                "repository": f"{github_owner}/{github_repo}"
            },
            "jira": {
                "open_issues": jira_open,
                "closed_issues": jira_closed,
                "in_progress": jira_in_progress,
                "project": jira_project_key
            },
            "unified": {
                "total_issues": total_issues,
                "total_open": total_open,
                "total_closed": total_closed,
                "completion_rate": round(completion_rate, 2),
                "health_score": "good" if completion_rate > 70 else "moderate" if completion_rate > 50 else "needs_attention"
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting unified project health: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get project health: {str(e)}"
        }, indent=2)

@mcp.tool()
def find_related_issues(
    github_owner: str,
    github_repo: str,
    jira_project_key: str,
    search_term: str
) -> str:
    """Find related issues across GitHub and Jira platforms"""
    try:
        logger.info(f"Finding related issues for term: {search_term}")
        
        # Search GitHub issues
        github_issues = github_client.list_issues(owner=github_owner, repo=github_repo, state="all")
        github_matches = []
        for issue in github_issues:
            if issue.get("pull_request"):
                continue
            title = issue.get("title", "").lower()
            body = (issue.get("body") or "").lower()
            if search_term.lower() in title or search_term.lower() in body:
                github_matches.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "url": issue.get("html_url")
                })
        
        # Search Jira issues
        jira_issues_result = jira_client.search_issues(
            jql=f"project = {jira_project_key} AND (summary ~ '{search_term}' OR description ~ '{search_term}')",
            max_results=50
        )
        jira_matches = []
        for issue in jira_issues_result.get("issues", []):
            fields = issue.get("fields", {})
            jira_matches.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(github_matches)} GitHub issues and {len(jira_matches)} Jira issues matching '{search_term}'",
            "search_term": search_term,
            "github_issues": github_matches,
            "jira_issues": jira_matches,
            "total_matches": len(github_matches) + len(jira_matches)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error finding related issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to find related issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def generate_cross_platform_report(
    github_owner: str,
    github_repo: str,
    jira_project_key: str
) -> str:
    """Generate unified project report combining GitHub and Jira data"""
    try:
        logger.info(f"Generating cross-platform report for {github_owner}/{github_repo} and {jira_project_key}")
        
        # Get GitHub data
        github_issues = github_client.list_issues(owner=github_owner, repo=github_repo, state="all")
        github_prs = github_client.list_pull_requests(owner=github_owner, repo=github_repo, state="all")
        
        # Get Jira data
        jira_project = jira_client.get_project(jira_project_key)
        jira_issues_result = jira_client.search_issues(
            jql=f"project = {jira_project_key}",
            max_results=100
        )
        jira_issues = jira_issues_result.get("issues", [])
        
        # Calculate statistics
        github_stats = {
            "total_issues": len([i for i in github_issues if not i.get("pull_request")]),
            "open_issues": len([i for i in github_issues if i.get("state") == "open" and not i.get("pull_request")]),
            "closed_issues": len([i for i in github_issues if i.get("state") == "closed" and not i.get("pull_request")]),
            "open_prs": len([pr for pr in github_prs if pr.get("state") == "open"]),
            "merged_prs": len([pr for pr in github_prs if pr.get("state") == "closed" and pr.get("merged_at")])
        }
        
        jira_stats = {
            "total_issues": len(jira_issues),
            "open_issues": len([i for i in jira_issues if i.get("fields", {}).get("status", {}).get("name") not in ["Done", "Closed"]]),
            "closed_issues": len([i for i in jira_issues if i.get("fields", {}).get("status", {}).get("name") in ["Done", "Closed"]])
        }
        
        # Generate report
        report = {
            "status": "success",
            "message": "Cross-platform project report generated",
            "report_date": datetime.utcnow().isoformat(),
            "github": {
                "repository": f"{github_owner}/{github_repo}",
                "statistics": github_stats
            },
            "jira": {
                "project": jira_project_key,
                "project_name": jira_project.get("name"),
                "statistics": jira_stats
            },
            "summary": {
                "total_issues": github_stats["total_issues"] + jira_stats["total_issues"],
                "total_open": github_stats["open_issues"] + jira_stats["open_issues"],
                "total_closed": github_stats["closed_issues"] + jira_stats["closed_issues"],
                "github_contribution": round(github_stats["total_issues"] / (github_stats["total_issues"] + jira_stats["total_issues"]) * 100, 2) if (github_stats["total_issues"] + jira_stats["total_issues"]) > 0 else 0,
                "jira_contribution": round(jira_stats["total_issues"] / (github_stats["total_issues"] + jira_stats["total_issues"]) * 100, 2) if (github_stats["total_issues"] + jira_stats["total_issues"]) > 0 else 0
            }
        }
        
        return json.dumps(report, indent=2)
    except Exception as e:
        logger.error(f"Error generating cross-platform report: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to generate report: {str(e)}"
        }, indent=2)

def run():
    """Run the MCP server"""
    if not github_client.token:
        logger.warning("No GITHUB_TOKEN found. Some operations may be rate-limited.")
    if not jira_client.url:
        logger.warning("No JIRA_URL found. Please set JIRA_URL environment variable.")
    if not jira_client.personal_token and not (jira_client.email and jira_client.api_token):
        logger.warning("No Jira credentials found. Please set JIRA_EMAIL and JIRA_API_TOKEN (Cloud) or JIRA_PERSONAL_TOKEN (Server/DC).")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run()

