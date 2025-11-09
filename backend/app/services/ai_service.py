import httpx
import logging
from app.config import settings
from typing import Optional, List

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY or settings.ANTHROPIC_API_KEY
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "anthropic-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        } if self.api_key else {}
        
        # Log API key status (first 10 chars only for security)
        if self.api_key:
            logger.info(f"Claude API key configured: {self.api_key[:10]}...")
        else:
            logger.warning("Claude API key not configured")

    async def get_assignment_recommendation(
        self,
        issue_title: str,
        issue_description: Optional[str] = None,
        developers: Optional[List[dict]] = None,
    ) -> dict:
        """
        Use Claude API to recommend the best developer for an issue
        """
        if not self.api_key:
            return {
                "assignee": "developer1",
                "reasoning": "AI service not configured. Default assignment.",
            }
        
        # Build prompt for Claude
        prompt = f"""Analyze the following issue and recommend the best developer to assign it to.

Issue Title: {issue_title}
Issue Description: {issue_description or "No description provided"}

Available Developers:
{self._format_developers(developers) if developers else "No developer data available"}

Please recommend the best developer based on:
1. Their expertise and past work on similar issues
2. Their current workload
3. The complexity and requirements of the issue

Respond in JSON format with:
- "assignee": the recommended developer's name/ID
- "reasoning": a brief explanation of why this developer is recommended
"""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1024,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse Claude's response
                content = data.get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    # TODO: Parse JSON from Claude's response
                    # For now, return a simple recommendation
                    return {
                        "assignee": "developer1",
                        "reasoning": text[:200] if text else "Recommended based on AI analysis",
                    }
                
                return {
                    "assignee": "developer1",
                    "reasoning": "AI analysis completed",
                }
            except Exception as e:
                print(f"Error calling Claude API: {e}")
                return {
                    "assignee": "developer1",
                    "reasoning": f"AI service error: {str(e)}",
                }

    def _format_developers(self, developers: List[dict]) -> str:
        """Format developer list for prompt"""
        if not developers:
            return "No developers available"
        
        formatted = []
        for dev in developers:
            name = dev.get("name", "Unknown")
            workload = dev.get("workload", "Unknown")
            skills = dev.get("skills", [])
            formatted.append(f"- {name}: Workload: {workload}, Skills: {', '.join(skills)}")
        
        return "\n".join(formatted)

