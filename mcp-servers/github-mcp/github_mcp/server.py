import json
import os
from typing import Optional
from loguru import logger
from mcp.server.fastmcp import FastMCP
from .client import GitHubClient
import requests

# Create an MCP server
mcp = FastMCP("GitHub-MCP-Server")

# Global GitHub client instance
github_client = GitHubClient()

@mcp.tool()
def list_commits(
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
def get_commit(owner: str, repo: str, sha: str) -> str:
    """Get detailed information about a specific commit"""
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
def list_pull_requests(
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
def get_pull_request(owner: str, repo: str, pr_number: int) -> str:
    """Get detailed information about a specific pull request"""
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
def list_issues(
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
def get_issue(owner: str, repo: str, issue_number: int) -> str:
    """Get detailed information about a specific issue"""
    try:
        logger.info(f"Getting issue #{issue_number} from {owner}/{repo}")
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
def send_issues_to_dashboard(owner: str, repo: str, state: str = "open") -> str:
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

def run():
    """Run the MCP server"""
    if not github_client.token:
        logger.warning("No GITHUB_TOKEN found. Some operations may be rate-limited.")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run()

