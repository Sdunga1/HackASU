"""Jira MCP Server - Model Context Protocol integration for Jira API."""

__version__ = "0.1.0"
__author__ = "HackASU Team"

from .client import JiraClient
from . import server

__all__ = ["JiraClient", "server", "__version__"]

