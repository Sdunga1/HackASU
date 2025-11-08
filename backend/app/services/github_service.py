import httpx
from app.config import settings
from typing import List, Optional

class GitHubService:
    def __init__(self):
        self.token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        } if self.token else {}

    async def get_issues(self, owner: str, repo: str) -> List[dict]:
        """
        Fetch issues from a GitHub repository
        """
        if not self.token:
            return []
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching GitHub issues: {e}")
                return []

    async def get_repository_info(self, owner: str, repo: str) -> Optional[dict]:
        """
        Get repository information
        """
        if not self.token:
            return None
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching repository info: {e}")
                return None

    async def assign_issue(self, owner: str, repo: str, issue_number: int, assignee: str) -> bool:
        """
        Assign an issue to a user
        """
        if not self.token:
            return False
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/assignees"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json={"assignees": [assignee]})
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Error assigning issue: {e}")
                return False

