import json
import os
import time
import base64
from typing import Dict, List, Optional
from loguru import logger
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REQUEST_TIMEOUT_SECONDS = 30

logger.info("HackASU MCP Server - GitHub Client initialized")


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
            })
        else:
            logger.warning("No GitHub token provided. Some operations may be rate-limited.")
    
    def _ensure_token(self):
        """Ensure token is available for authenticated requests."""
        if not self.token:
            raise Exception(
                "GitHub token required. Set GITHUB_TOKEN environment variable or pass token to client."
            )
    
    def _handle_api_response(self, response: requests.Response, operation_name: str) -> Dict:
        """Handle API response and provide meaningful error messages."""
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 401:
            raise Exception(
                f"Authentication failed: Invalid or expired token.\n"
                f"Set GITHUB_TOKEN environment variable with a valid GitHub Personal Access Token."
            )
        elif response.status_code == 403:
            # Check if it's rate limiting
            if "rate limit" in response.text.lower():
                raise Exception(
                    f"Rate limit exceeded. Please wait before making more requests.\n"
                    f"Unauthenticated requests: 60/hour\n"
                    f"Authenticated requests: 5,000/hour"
                )
            raise Exception(
                f"Access denied: You don't have permission to {operation_name}.\n"
                f"Check repository permissions and token scopes."
            )
        elif response.status_code == 404:
            raise Exception(
                f"Resource not found: {operation_name} failed.\n"
                f"Check repository owner, name, and resource ID."
            )
        else:
            raise Exception(
                f"API error {response.status_code}: {response.text}"
            )
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to GitHub API."""
        url = f"{GITHUB_API_BASE}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request to GitHub API."""
        url = f"{GITHUB_API_BASE}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Repository methods
    def list_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        author: Optional[str] = None,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict]:
        """List commits from a repository."""
        endpoint = f"/repos/{owner}/{repo}/commits"
        params = {
            "page": page,
            "per_page": min(per_page, 100),  # GitHub max is 100
        }
        if sha:
            params["sha"] = sha
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if author:
            params["author"] = author
        
        return self._get(endpoint, params)
    
    def get_commit(self, owner: str, repo: str, sha: str) -> Dict:
        """Get a specific commit."""
        endpoint = f"/repos/{owner}/{repo}/commits/{sha}"
        return self._get(endpoint)
    
    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        head: Optional[str] = None,
        base: Optional[str] = None,
        sort: str = "created",
        direction: str = "desc",
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict]:
        """List pull requests."""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "page": page,
            "per_page": min(per_page, 100),
        }
        if head:
            params["head"] = head
        if base:
            params["base"] = base
        
        return self._get(endpoint, params)
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Get a specific pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return self._get(endpoint)
    
    def list_pull_request_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[Dict]:
        """List reviews for a pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self._get(endpoint)
    
    def list_pull_request_comments(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[Dict]:
        """List review comments for a pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        return self._get(endpoint)
    
    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[str] = None,
        assignee: Optional[str] = None,
        creator: Optional[str] = None,
        since: Optional[str] = None,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict]:
        """List issues."""
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "page": page,
            "per_page": min(per_page, 100),
        }
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
        if creator:
            params["creator"] = creator
        if since:
            params["since"] = since
        
        return self._get(endpoint, params)
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Get a specific issue."""
        endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}"
        return self._get(endpoint)
    
    def search_code(
        self,
        query: str,
        sort: Optional[str] = None,
        order: str = "desc",
        page: int = 1,
        per_page: int = 30
    ) -> Dict:
        """Search code."""
        endpoint = "/search/code"
        params = {
            "q": query,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100),
        }
        if sort:
            params["sort"] = sort
        
        return self._get(endpoint, params)
    
    def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None
    ) -> Dict:
        """Get file contents."""
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {}
        if ref:
            params["ref"] = ref
        
        return self._get(endpoint, params)


# Jira API configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL") or os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PERSONAL_TOKEN = os.getenv("JIRA_PERSONAL_TOKEN")

logger.info("HackASU MCP Server - Jira Client initialized")


class JiraClient:
    def __init__(self, url: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None, personal_token: Optional[str] = None):
        self.url = url or JIRA_URL
        self.email = email or JIRA_EMAIL
        self.api_token = api_token or JIRA_API_TOKEN
        self.personal_token = personal_token or JIRA_PERSONAL_TOKEN
        self.session = requests.Session()
        
        if not self.url:
            logger.warning("No JIRA_URL found. Please set JIRA_URL environment variable.")
        else:
            # Determine authentication method
            if self.personal_token:
                # Personal Access Token (Server/Data Center)
                self.session.headers.update({
                    "Authorization": f"Bearer {self.personal_token}",
                    "Content-Type": "application/json",
                })
            elif self.email and self.api_token:
                # API Token (Cloud) - Basic Auth
                credentials = f"{self.email}:{self.api_token}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                self.session.headers.update({
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/json",
                })
            else:
                logger.warning("No Jira credentials found. Some operations may fail.")
    
    def _ensure_auth(self):
        """Ensure authentication is configured."""
        if not self.url:
            raise Exception("JIRA_URL is required. Set JIRA_URL environment variable.")
        if not self.personal_token and not (self.email and self.api_token):
            raise Exception(
                "Jira authentication required. Set either:\n"
                "- JIRA_EMAIL and JIRA_API_TOKEN (for Cloud)\n"
                "- JIRA_PERSONAL_TOKEN (for Server/Data Center)"
            )
    
    def _handle_api_response(self, response: requests.Response, operation_name: str) -> Dict:
        """Handle API response and provide meaningful error messages."""
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 401:
            raise Exception(
                f"Authentication failed: Invalid credentials.\n"
                f"Check JIRA_EMAIL, JIRA_API_TOKEN, or JIRA_PERSONAL_TOKEN environment variables."
            )
        elif response.status_code == 403:
            raise Exception(
                f"Access denied: You don't have permission to {operation_name}.\n"
                f"Check your Jira permissions and token scopes."
            )
        elif response.status_code == 404:
            raise Exception(
                f"Resource not found: {operation_name} failed.\n"
                f"Check the resource ID or key."
            )
        else:
            try:
                error_msg = response.json().get("errorMessages", [])
                if error_msg:
                    raise Exception(f"Jira API error {response.status_code}: {', '.join(error_msg)}")
            except:
                pass
            raise Exception(f"API error {response.status_code}: {response.text}")
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to Jira API."""
        self._ensure_auth()
        url = f"{self.url}/rest/api/3{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request to Jira API."""
        self._ensure_auth()
        url = f"{self.url}/rest/api/3{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make PUT request to Jira API."""
        self._ensure_auth()
        url = f"{self.url}/rest/api/3{endpoint}"
        try:
            response = self.session.put(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.status_code in [200, 204]:
                return response.json() if response.text else {"status": "success"}
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _delete(self, endpoint: str) -> Dict:
        """Make DELETE request to Jira API."""
        self._ensure_auth()
        url = f"{self.url}/rest/api/3{endpoint}"
        try:
            response = self.session.delete(url, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.status_code in [200, 204]:
                return {"status": "success"}
            return self._handle_api_response(response, endpoint)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Project methods
    def list_projects(self, include_archived: bool = False) -> List[Dict]:
        """List all projects."""
        params = {}
        if include_archived:
            params["includeArchived"] = "true"
        return self._get("/project", params=params)
    
    def get_project(self, project_key: str) -> Dict:
        """Get project by key."""
        return self._get(f"/project/{project_key}")
    
    # Issue methods
    def get_issue(self, issue_key: str, expand: Optional[str] = None) -> Dict:
        """Get issue by key with optional expansion."""
        params = {}
        if expand:
            params["expand"] = expand
        return self._get(f"/issue/{issue_key}", params=params)
    
    def get_issue_changelog(self, issue_key: str, start_at: int = 0, max_results: int = 100) -> Dict:
        """Get issue changelog (status transitions)."""
        params = {
            "startAt": start_at,
            "maxResults": max_results,
        }
        return self._get(f"/issue/{issue_key}/changelog", params=params)
    
    def get_issue_comments(self, issue_key: str, start_at: int = 0, max_results: int = 100) -> Dict:
        """Get issue comments."""
        params = {
            "startAt": start_at,
            "maxResults": max_results,
        }
        return self._get(f"/issue/{issue_key}/comment", params=params)
    
    def search_issues(self, jql: str, start_at: int = 0, max_results: int = 50, fields: Optional[List[str]] = None, expand: Optional[str] = None) -> Dict:
        """Search issues using JQL."""
        data = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": min(max_results, 100),
        }
        if fields:
            data["fields"] = fields if isinstance(fields, list) else [fields]
        if expand:
            data["expand"] = expand
        return self._post("/search", data=data)
    
    # Agile/Board methods
    def get_boards(self, project_key: Optional[str] = None, board_type: Optional[str] = None) -> Dict:
        """Get agile boards."""
        self._ensure_auth()
        params = {}
        if project_key:
            params["projectKeyOrId"] = project_key
        if board_type:
            params["type"] = board_type
        url = f"{self.url}/rest/agile/1.0/board"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, "/board")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_board_sprints(self, board_id: int, state: Optional[str] = None) -> Dict:
        """Get sprints for a board."""
        self._ensure_auth()
        params = {}
        if state:
            params["state"] = state
        url = f"{self.url}/rest/agile/1.0/board/{board_id}/sprint"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, f"/board/{board_id}/sprint")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def create_sprint(self, board_id: int, name: str, start_date: str, end_date: str, goal: Optional[str] = None) -> Dict:
        """Create a new sprint in Jira.
        
        Args:
            board_id: Board ID
            name: Sprint name
            start_date: Start date in ISO format (e.g., "2024-01-01T00:00:00.000Z")
            end_date: End date in ISO format (e.g., "2024-01-14T23:59:59.999Z")
            goal: Optional sprint goal
            
        Returns:
            Created sprint details
        """
        self._ensure_auth()
        url = f"{self.url}/rest/agile/1.0/sprint"
        data = {
            "name": name,
            "boardId": board_id,
            "startDate": start_date,
            "endDate": end_date
        }
        if goal:
            data["goal"] = goal
        
        try:
            response = self.session.post(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, "/sprint")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def update_sprint(self, sprint_id: int, name: Optional[str] = None, state: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None, goal: Optional[str] = None) -> Dict:
        """Update an existing sprint in Jira.
        
        Args:
            sprint_id: Sprint ID
            name: New sprint name (optional)
            state: New state - "future", "active", or "closed" (optional)
            start_date: New start date in ISO format (optional)
            end_date: New end date in ISO format (optional)
            goal: New sprint goal (optional)
            
        Returns:
            Updated sprint details
        """
        self._ensure_auth()
        url = f"{self.url}/rest/agile/1.0/sprint/{sprint_id}"
        data = {}
        if name:
            data["name"] = name
        if state:
            if state not in ["future", "active", "closed"]:
                raise ValueError("State must be one of: future, active, closed")
            data["state"] = state
        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date
        if goal:
            data["goal"] = goal
        
        if not data:
            raise ValueError("At least one field must be provided for update")
        
        try:
            response = self.session.put(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, f"/sprint/{sprint_id}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def move_issue_to_sprint(self, issue_key: str, sprint_id: int) -> Dict:
        """Move an issue to a sprint.
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            sprint_id: Sprint ID
            
        Returns:
            Success response
        """
        self._ensure_auth()
        # Use Agile API to move issue to sprint
        url = f"{self.url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        data = {
            "issues": [issue_key]
        }
        
        try:
            response = self.session.post(url, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.status_code in [200, 204]:
                return {"status": "success", "message": f"Issue {issue_key} moved to sprint {sprint_id}"}
            # If not 200/204, try to get error message
            try:
                error_data = response.json()
                raise Exception(f"Failed to move issue: {error_data}")
            except:
                raise Exception(f"Failed to move issue: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_board_issues(self, board_id: int, jql: Optional[str] = None, start_at: int = 0, max_results: int = 50) -> Dict:
        """Get issues for a board using the Agile API."""
        self._ensure_auth()
        params = {
            "startAt": start_at,
            "maxResults": max_results,
        }
        if jql:
            params["jql"] = jql
        url = f"{self.url}/rest/agile/1.0/board/{board_id}/issue"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            return self._handle_api_response(response, f"/board/{board_id}/issue")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Write methods
    def create_issue(self, project_key: str, summary: str, issue_type: str, description: Optional[str] = None, 
                    assignee: Optional[str] = None, priority: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict:
        """Create a new Jira issue."""
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
        }
        
        if description:
            data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
        
        if assignee:
            data["fields"]["assignee"] = {"accountId": assignee} if "@" not in assignee else {"name": assignee}
        
        if priority:
            data["fields"]["priority"] = {"name": priority}
        
        if labels:
            data["fields"]["labels"] = labels
        
        return self._post("/issue", data=data)
    
    def update_issue(self, issue_key: str, summary: Optional[str] = None, description: Optional[str] = None,
                    assignee: Optional[str] = None, priority: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict:
        """Update an existing Jira issue."""
        data = {"fields": {}}
        
        if summary:
            data["fields"]["summary"] = summary
        
        if description:
            data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
        
        if assignee:
            data["fields"]["assignee"] = {"accountId": assignee} if "@" not in assignee else {"name": assignee}
        
        if priority:
            data["fields"]["priority"] = {"name": priority}
        
        if labels:
            data["fields"]["labels"] = labels
        
        return self._put(f"/issue/{issue_key}", data=data)
    
    def delete_issue(self, issue_key: str) -> Dict:
        """Delete a Jira issue."""
        return self._delete(f"/issue/{issue_key}")
    
    def add_comment(self, issue_key: str, comment_text: str) -> Dict:
        """Add a comment to a Jira issue."""
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment_text
                            }
                        ]
                    }
                ]
            }
        }
        return self._post(f"/issue/{issue_key}/comment", data=data)
    
    def transition_issue(self, issue_key: str, transition_id: str, comment: Optional[str] = None) -> Dict:
        """Transition an issue to a new status."""
        data = {
            "transition": {"id": transition_id}
        }
        
        if comment:
            data["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": comment
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        
        return self._post(f"/issue/{issue_key}/transitions", data=data)
    
    def get_transitions(self, issue_key: str) -> Dict:
        """Get available transitions for an issue."""
        return self._get(f"/issue/{issue_key}/transitions")
    
    def batch_create_issues(self, issues: List[Dict]) -> Dict:
        """Create multiple issues in a single request."""
        data = {"issueUpdates": []}
        
        for issue in issues:
            issue_data = {
                "fields": {
                    "project": {"key": issue["project_key"]},
                    "summary": issue["summary"],
                    "issuetype": {"name": issue["issue_type"]},
                }
            }
            
            if issue.get("description"):
                issue_data["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": issue["description"]
                                }
                            ]
                        }
                    ]
                }
            
            if issue.get("assignee"):
                issue_data["fields"]["assignee"] = {"accountId": issue["assignee"]} if "@" not in issue["assignee"] else {"name": issue["assignee"]}
            
            if issue.get("priority"):
                issue_data["fields"]["priority"] = {"name": issue["priority"]}
            
            if issue.get("labels"):
                issue_data["fields"]["labels"] = issue["labels"]
            
            data["issueUpdates"].append(issue_data)
        
        return self._post("/issue/bulk", data=data)

