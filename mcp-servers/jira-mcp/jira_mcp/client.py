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

