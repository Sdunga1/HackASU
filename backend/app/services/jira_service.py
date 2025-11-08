import httpx
from app.config import settings
from typing import List, Optional
import base64

class JiraService:
    def __init__(self):
        self.url = settings.JIRA_URL
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        
        if self.email and self.api_token:
            credentials = f"{self.email}:{self.api_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        else:
            self.headers = {}

    async def get_issues(self, project_key: str) -> List[dict]:
        """
        Fetch issues from a Jira project
        """
        if not self.url or not self.email or not self.api_token:
            return []
        
        jql = f"project = {project_key}"
        url = f"{self.url}/rest/api/3/search"
        params = {"jql": jql, "maxResults": 50}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("issues", [])
            except Exception as e:
                print(f"Error fetching Jira issues: {e}")
                return []

    async def assign_issue(self, issue_key: str, assignee: str) -> bool:
        """
        Assign a Jira issue to a user
        """
        if not self.url or not self.email or not self.api_token:
            return False
        
        url = f"{self.url}/rest/api/3/issue/{issue_key}/assignee"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, headers=self.headers, json={"accountId": assignee})
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Error assigning Jira issue: {e}")
                return False

    async def get_project_info(self, project_key: str) -> Optional[dict]:
        """
        Get Jira project information
        """
        if not self.url or not self.email or not self.api_token:
            return None
        
        url = f"{self.url}/rest/api/3/project/{project_key}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching Jira project info: {e}")
                return None

