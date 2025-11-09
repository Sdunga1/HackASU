"""GitHub MCP Server - Model Context Protocol integration for GitHub API."""

__version__ = "0.1.0"
__author__ = "HackASU Team"

from .client import GitHubClient

# Import server to ensure tools are registered
from . import server

__all__ = ["GitHubClient", "server", "__version__"]

