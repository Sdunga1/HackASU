"""HackASU MCP Server - Unified GitHub and Jira integration."""

__version__ = "0.1.0"
__author__ = "HackASU Team"

from client import GitHubClient, JiraClient

# Import server to ensure tools are registered
import server

__all__ = ["GitHubClient", "JiraClient", "server", "__version__"]

