import json
import os
import time
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

logger.info("GitHub MCP Server - Client initialized")


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

