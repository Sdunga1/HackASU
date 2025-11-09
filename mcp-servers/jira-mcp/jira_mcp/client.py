import json
import os
import base64
from typing import Dict, List, Optional
from loguru import logger
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Jira API configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL") or os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PERSONAL_TOKEN = os.getenv("JIRA_PERSONAL_TOKEN")
REQUEST_TIMEOUT_SECONDS = 30

logger.info("Jira MCP Server - Client initialized")


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
            "maxResults": max_results,
        }
        if fields:
            data["fields"] = fields
        if expand:
            data["expand"] = expand
        return self._post("/search", data=data)
    
    # Agile/Board methods (for sprints)
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

