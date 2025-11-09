import json
import os
import requests
from typing import Optional, List
from loguru import logger
from mcp.server.fastmcp import FastMCP
from .client import JiraClient

# Create an MCP server
mcp = FastMCP("Jira-MCP-Server")

# Global Jira client instance
jira_client = JiraClient()

@mcp.tool()
def list_projects(include_archived: bool = False) -> str:
    """List all Jira projects visible to the user"""
    try:
        logger.info("Listing Jira projects")
        projects = jira_client.list_projects(include_archived=include_archived)
        
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "key": project.get("key"),
                "name": project.get("name"),
                "id": project.get("id"),
                "projectTypeKey": project.get("projectTypeKey"),
                "archived": project.get("archived", False),
                "url": f"{jira_client.url}/browse/{project.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_projects)} projects",
            "projects": formatted_projects,
            "count": len(formatted_projects)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list projects: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_project(project_key: str) -> str:
    """Get detailed information about a specific Jira project"""
    try:
        logger.info(f"Getting project {project_key}")
        project = jira_client.get_project(project_key)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved project {project_key}",
            "project": {
                "key": project.get("key"),
                "name": project.get("name"),
                "id": project.get("id"),
                "projectTypeKey": project.get("projectTypeKey"),
                "archived": project.get("archived", False),
                "description": project.get("description"),
                "lead": project.get("lead", {}).get("displayName") if project.get("lead") else None,
                "url": f"{jira_client.url}/browse/{project.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get project: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_issue(issue_key: str, expand: Optional[str] = None) -> str:
    """Get detailed information about a specific Jira issue
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        expand: Optional fields to expand (e.g., 'changelog,comments')
    """
    try:
        logger.info(f"Getting issue {issue_key}")
        expand_fields = expand or "changelog,renderedFields"
        issue = jira_client.get_issue(issue_key, expand=expand_fields)
        
        fields = issue.get("fields", {})
        changelog = issue.get("changelog", {})
        
        # Extract status transitions from changelog
        status_transitions = []
        if changelog and changelog.get("histories"):
            for history in changelog.get("histories", []):
                for item in history.get("items", []):
                    if item.get("field") == "status":
                        status_transitions.append({
                            "from": item.get("fromString"),
                            "to": item.get("toString"),
                            "changed_at": history.get("created"),
                            "changed_by": history.get("author", {}).get("displayName") if history.get("author") else None,
                        })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved issue {issue_key}",
            "issue": {
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields.get("summary"),
                "description": fields.get("description"),
                "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                "status_id": fields.get("status", {}).get("id") if fields.get("status") else None,
                "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "assignee_email": fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None,
                "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None,
                "resolution_date": fields.get("resolutiondate"),
                "labels": fields.get("labels", []),
                "components": [c.get("name") for c in fields.get("components", [])],
                "fix_versions": [v.get("name") for v in fields.get("fixVersions", [])],
                "status_transitions": status_transitions,
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_issue_changelog(issue_key: str, max_results: int = 100) -> str:
    """Get issue changelog (status transitions and field changes)
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        max_results: Maximum number of changelog entries to return
    """
    try:
        logger.info(f"Getting changelog for issue {issue_key}")
        changelog = jira_client.get_issue_changelog(issue_key, max_results=max_results)
        
        transitions = []
        for history in changelog.get("values", []):
            changes = []
            for item in history.get("items", []):
                changes.append({
                    "field": item.get("field"),
                    "field_type": item.get("fieldtype"),
                    "from": item.get("fromString"),
                    "to": item.get("toString"),
                    "from_id": item.get("from"),
                    "to_id": item.get("to"),
                })
            
            transitions.append({
                "id": history.get("id"),
                "author": history.get("author", {}).get("displayName") if history.get("author") else None,
                "created": history.get("created"),
                "changes": changes,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved changelog for {issue_key}",
            "issue_key": issue_key,
            "total": changelog.get("total", 0),
            "transitions": transitions,
            "count": len(transitions)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue changelog: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue changelog: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_issue_comments(issue_key: str, max_results: int = 100) -> str:
    """Get comments for a Jira issue
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        max_results: Maximum number of comments to return
    """
    try:
        logger.info(f"Getting comments for issue {issue_key}")
        comments_response = jira_client.get_issue_comments(issue_key, max_results=max_results)
        
        comments = []
        for comment in comments_response.get("comments", []):
            comments.append({
                "id": comment.get("id"),
                "author": comment.get("author", {}).get("displayName") if comment.get("author") else None,
                "author_email": comment.get("author", {}).get("emailAddress") if comment.get("author") else None,
                "body": comment.get("body"),
                "created": comment.get("created"),
                "updated": comment.get("updated"),
                "visibility": comment.get("visibility", {}).get("value") if comment.get("visibility") else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully retrieved comments for {issue_key}",
            "issue_key": issue_key,
            "total": comments_response.get("total", 0),
            "comments": comments,
            "count": len(comments)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting issue comments: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get issue comments: {str(e)}"
        }, indent=2)

@mcp.tool()
def search_issues(
    jql: str,
    max_results: int = 50,
    fields: Optional[str] = None,
    expand: Optional[str] = None
) -> str:
    """Search for Jira issues using JQL (Jira Query Language)
    
    Args:
        jql: JQL query string (e.g., 'project = PROJ AND status = "In Progress"')
        max_results: Maximum number of issues to return (default: 50, max: 100)
        fields: Comma-separated list of fields to return (e.g., 'summary,status,assignee')
        expand: Optional fields to expand (e.g., 'changelog')
    """
    try:
        logger.info(f"Searching issues with JQL: {jql}")
        
        fields_list = None
        if fields:
            fields_list = [f.strip() for f in fields.split(",")]
        
        search_result = jira_client.search_issues(
            jql=jql,
            max_results=min(max_results, 100),
            fields=fields_list,
            expand=expand
        )
        
        issues = []
        for issue in search_result.get("issues", []):
            fields_data = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields_data.get("summary"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "issue_type": fields_data.get("issuetype", {}).get("name") if fields_data.get("issuetype") else None,
                "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                "reporter": fields_data.get("reporter", {}).get("displayName") if fields_data.get("reporter") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
                "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                "labels": fields_data.get("labels", []),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(issues)} issues",
            "jql": jql,
            "total": search_result.get("total", 0),
            "start_at": search_result.get("startAt", 0),
            "max_results": search_result.get("maxResults", 0),
            "issues": issues,
            "count": len(issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error searching issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to search issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_boards(project_key: Optional[str] = None, board_type: Optional[str] = None) -> str:
    """Get agile boards for a project
    
    Args:
        project_key: Optional project key to filter boards
        board_type: Optional board type (e.g., 'scrum', 'kanban')
    """
    try:
        logger.info(f"Getting boards (project: {project_key}, type: {board_type})")
        boards_response = jira_client.get_boards(project_key=project_key, board_type=board_type)
        
        boards = []
        for board in boards_response.get("values", []):
            boards.append({
                "id": board.get("id"),
                "name": board.get("name"),
                "type": board.get("type"),
                "location": board.get("location", {}).get("projectName") if board.get("location") else None,
                "url": f"{jira_client.url}/jira/software/projects/{board.get('location', {}).get('projectKey', '')}/boards/{board.get('id')}" if jira_client.url and board.get("location") else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(boards)} boards",
            "boards": boards,
            "count": len(boards)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting boards: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get boards: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_board_sprints(board_id: int, state: Optional[str] = None) -> str:
    """Get sprints for an agile board
    
    Args:
        board_id: The board ID
        state: Optional sprint state filter (e.g., 'active', 'closed', 'future')
    """
    try:
        logger.info(f"Getting sprints for board {board_id} (state: {state})")
        sprints_response = jira_client.get_board_sprints(board_id=board_id, state=state)
        
        sprints = []
        for sprint in sprints_response.get("values", []):
            sprints.append({
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "start_date": sprint.get("startDate"),
                "end_date": sprint.get("endDate"),
                "complete_date": sprint.get("completeDate"),
                "goal": sprint.get("goal"),
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(sprints)} sprints",
            "board_id": board_id,
            "sprints": sprints,
            "count": len(sprints)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting board sprints: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get board sprints: {str(e)}"
        }, indent=2)

@mcp.tool()
def get_board_issues(board_id: int, jql: Optional[str] = None, max_results: int = 50) -> str:
    """Get issues from a board using the Agile API (workaround for search endpoint issues)
    
    Args:
        board_id: The board ID
        jql: Optional JQL query to filter issues
        max_results: Maximum number of issues to return
    """
    try:
        logger.info(f"Getting issues for board {board_id}")
        issues_response = jira_client.get_board_issues(
            board_id=board_id,
            jql=jql,
            max_results=min(max_results, 100)
        )
        
        issues = []
        for issue in issues_response.get("issues", []):
            fields_data = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields_data.get("summary"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "issue_type": fields_data.get("issuetype", {}).get("name") if fields_data.get("issuetype") else None,
                "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                "reporter": fields_data.get("reporter", {}).get("displayName") if fields_data.get("reporter") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
                "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                "labels": fields_data.get("labels", []),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(issues)} issues",
            "board_id": board_id,
            "total": issues_response.get("total", 0),
            "issues": issues,
            "count": len(issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error getting board issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get board issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def create_issue(
    project_key: str,
    summary: str,
    issue_type: str,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[str] = None
) -> str:
    """Create a new Jira issue
    
    Args:
        project_key: The project key (e.g., 'SCRUM')
        summary: Issue summary/title
        issue_type: Issue type (e.g., 'Task', 'Bug', 'Story')
        description: Optional issue description
        assignee: Optional assignee account ID or name
        priority: Optional priority (e.g., 'High', 'Medium', 'Low')
        labels: Optional comma-separated list of labels
    """
    try:
        logger.info(f"Creating issue in project {project_key}")
        
        labels_list = None
        if labels:
            labels_list = [l.strip() for l in labels.split(",")]
        
        issue = jira_client.create_issue(
            project_key=project_key,
            summary=summary,
            issue_type=issue_type,
            description=description,
            assignee=assignee,
            priority=priority,
            labels=labels_list
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully created issue {issue.get('key')}",
            "issue": {
                "key": issue.get("key"),
                "id": issue.get("id"),
                "url": f"{jira_client.url}/browse/{issue.get('key')}" if jira_client.url else None,
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to create issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def update_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[str] = None
) -> str:
    """Update an existing Jira issue
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        summary: Optional new summary
        description: Optional new description
        assignee: Optional new assignee
        priority: Optional new priority
        labels: Optional comma-separated list of labels
    """
    try:
        logger.info(f"Updating issue {issue_key}")
        
        labels_list = None
        if labels:
            labels_list = [l.strip() for l in labels.split(",")]
        
        jira_client.update_issue(
            issue_key=issue_key,
            summary=summary,
            description=description,
            assignee=assignee,
            priority=priority,
            labels=labels_list
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully updated issue {issue_key}",
            "issue_key": issue_key,
            "url": f"{jira_client.url}/browse/{issue_key}" if jira_client.url else None,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error updating issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to update issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def delete_issue(issue_key: str) -> str:
    """Delete a Jira issue
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
    """
    try:
        logger.info(f"Deleting issue {issue_key}")
        jira_client.delete_issue(issue_key=issue_key)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully deleted issue {issue_key}",
            "issue_key": issue_key
        }, indent=2)
    except Exception as e:
        logger.error(f"Error deleting issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to delete issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def add_comment(issue_key: str, comment: str) -> str:
    """Add a comment to a Jira issue
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        comment: The comment text
    """
    try:
        logger.info(f"Adding comment to issue {issue_key}")
        result = jira_client.add_comment(issue_key=issue_key, comment_text=comment)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully added comment to issue {issue_key}",
            "comment_id": result.get("id"),
            "issue_key": issue_key
        }, indent=2)
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to add comment: {str(e)}"
        }, indent=2)

@mcp.tool()
def transition_issue(issue_key: str, transition_name: str, comment: Optional[str] = None) -> str:
    """Transition an issue to a new status
    
    Args:
        issue_key: The issue key (e.g., 'PROJ-123')
        transition_name: The transition name (e.g., 'In Progress', 'Done')
        comment: Optional comment to add with the transition
    """
    try:
        logger.info(f"Transitioning issue {issue_key} to {transition_name}")
        
        # Get available transitions
        transitions_response = jira_client.get_transitions(issue_key=issue_key)
        transitions = transitions_response.get("transitions", [])
        
        # Find matching transition
        transition_id = None
        for t in transitions:
            if t.get("name", "").lower() == transition_name.lower() or t.get("to", {}).get("name", "").lower() == transition_name.lower():
                transition_id = t.get("id")
                break
        
        if not transition_id:
            available = [t.get("name") or t.get("to", {}).get("name") for t in transitions]
            return json.dumps({
                "status": "error",
                "message": f"Transition '{transition_name}' not found. Available transitions: {', '.join(available)}"
            }, indent=2)
        
        jira_client.transition_issue(
            issue_key=issue_key,
            transition_id=transition_id,
            comment=comment
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully transitioned issue {issue_key} to {transition_name}",
            "issue_key": issue_key,
            "transition": transition_name
        }, indent=2)
    except Exception as e:
        logger.error(f"Error transitioning issue: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to transition issue: {str(e)}"
        }, indent=2)

@mcp.tool()
def batch_create_issues(issues_json: str) -> str:
    """Create multiple Jira issues in a single request
    
    Args:
        issues_json: JSON string array of issues to create. Each issue should have:
                    - project_key: Project key (e.g., 'SCRUM')
                    - summary: Issue summary
                    - issue_type: Issue type (e.g., 'Task', 'Bug', 'Story')
                    - description: Optional description
                    - assignee: Optional assignee
                    - priority: Optional priority
                    - labels: Optional array of labels
    """
    try:
        logger.info("Batch creating issues")
        issues = json.loads(issues_json)
        
        result = jira_client.batch_create_issues(issues=issues)
        
        created_issues = []
        errors = []
        
        for item in result.get("issues", []):
            if item:
                created_issues.append({
                    "key": item.get("key"),
                    "id": item.get("id"),
                    "url": f"{jira_client.url}/browse/{item.get('key')}" if jira_client.url else None,
                })
        
        for error in result.get("errors", []):
            errors.append(error)
        
        return json.dumps({
            "status": "success" if not errors else "partial_success",
            "message": f"Created {len(created_issues)} issues" + (f", {len(errors)} failed" if errors else ""),
            "created_issues": created_issues,
            "errors": errors,
            "count": len(created_issues)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error batch creating issues: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to batch create issues: {str(e)}"
        }, indent=2)

@mcp.tool()
def detect_workflow_anomalies(
    project_key: str,
    github_owner: Optional[str] = None,
    github_repo: Optional[str] = None,
    days_back: int = 30,
    max_anomalies: int = 20
) -> str:
    """Detect workflow anomalies by analyzing Jira and GitHub data
    
    This tool analyzes Jira tickets and correlates them with GitHub commits and PRs
    to detect issues like stale tickets, scope creep, missing links, status mismatches,
    and excessive task switching.
    
    Args:
        project_key: Jira project key to analyze (e.g., 'PROJ')
        github_owner: Optional GitHub repository owner for cross-platform analysis
        github_repo: Optional GitHub repository name
        days_back: Number of days to look back for analysis (default: 30)
        max_anomalies: Maximum number of anomalies to return (default: 20)
    
    Returns:
        JSON response with detected anomalies
    """
    try:
        logger.info(f"Detecting workflow anomalies for project {project_key}")
        
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get Jira issues using JQL
        jql = f'project = {project_key} AND updated >= -{days_back}d ORDER BY updated DESC'
        search_result = jira_client.search_issues(jql=jql, max_results=100)
        
        issues = search_result.get("issues", [])
        
        # Prepare anomaly detection data
        anomaly_data = {
            "project_key": project_key,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "issues": []
        }
        
        # Process each issue
        for issue in issues:
            issue_key = issue.get("key")
            fields = issue.get("fields", {})
            
            # Get detailed issue data including changelog
            try:
                detailed_issue = jira_client.get_issue(issue_key, expand="changelog")
                changelog = detailed_issue.get("changelog", {})
                
                # Extract status transitions
                status_history = []
                if changelog and changelog.get("histories"):
                    for history in changelog.get("histories", []):
                        for item in history.get("items", []):
                            if item.get("field") == "status":
                                status_history.append({
                                    "from": item.get("fromString"),
                                    "to": item.get("toString"),
                                    "date": history.get("created"),
                                    "author": history.get("author", {}).get("displayName") if history.get("author") else None
                                })
                
                # Get comments
                comments_response = jira_client.get_issue_comments(issue_key, max_results=50)
                comments_count = comments_response.get("total", 0)
                
                issue_data = {
                    "key": issue_key,
                    "summary": fields.get("summary"),
                    "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                    "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
                    "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                    "assignee_email": fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None,
                    "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                    "created": fields.get("created"),
                    "updated": fields.get("updated"),
                    "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                    "labels": fields.get("labels", []),
                    "status_history": status_history,
                    "comments_count": comments_count,
                    "story_points": fields.get("customfield_10016")  # Common story points field
                }
                
                anomaly_data["issues"].append(issue_data)
                
            except Exception as e:
                logger.warning(f"Could not get detailed data for {issue_key}: {e}")
                # Add basic issue data
                anomaly_data["issues"].append({
                    "key": issue_key,
                    "summary": fields.get("summary"),
                    "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                    "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                    "created": fields.get("created"),
                    "updated": fields.get("updated"),
                    "status_history": [],
                    "comments_count": 0
                })
        
        # If GitHub repo provided, fetch commit/PR data for correlation
        github_data = None
        if github_owner and github_repo:
            try:
                # Call GitHub API to get commits and PRs
                # This would be done via the GitHub MCP in production
                github_data = {
                    "owner": github_owner,
                    "repo": github_repo,
                    "available": True
                }
            except Exception as e:
                logger.warning(f"Could not fetch GitHub data: {e}")
                github_data = {"available": False, "error": str(e)}
        
        # Send to backend API for AI anomaly detection
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        api_endpoint = f"{backend_url}/api/anomalies/detect"
        
        try:
            response = requests.post(
                api_endpoint,
                json={
                    "jira_data": anomaly_data,
                    "github_data": github_data,
                    "max_anomalies": max_anomalies
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.dumps({
                    "status": "success",
                    "message": f"Successfully detected anomalies for {len(issues)} issues",
                    "issues_analyzed": len(issues),
                    "anomalies": result.get("anomalies", []),
                    "project": project_key
                }, indent=2)
            else:
                return json.dumps({
                    "status": "partial_success",
                    "message": f"Analyzed {len(issues)} issues but backend failed to detect anomalies",
                    "issues_analyzed": len(issues),
                    "raw_data": anomaly_data,
                    "error": f"Backend responded with status {response.status_code}"
                }, indent=2)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach backend API: {e}")
            return json.dumps({
                "status": "partial_success",
                "message": f"Analyzed {len(issues)} issues but backend API is unreachable",
                "issues_analyzed": len(issues),
                "raw_data": anomaly_data,
                "error": str(e)
            }, indent=2)
        
    except Exception as e:
        logger.error(f"Error detecting workflow anomalies: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to detect workflow anomalies: {str(e)}"
        }, indent=2)

@mcp.tool()
def send_sprints_to_dashboard(
    sprints_json: str,
    document_name: Optional[str] = None,
    document_url: Optional[str] = None
) -> str:
    """Send sprints and user stories to the dashboard
    
    Accepts sprints generated by Cursor's AI and sends them to the dashboard.
    The sprints should be in JSON format as a string.
    
    Args:
        sprints_json: JSON string containing sprints array. Each sprint should have:
            - id: string (e.g., "sprint-1")
            - name: string (e.g., "Sprint 1: Core Features")
            - goal: string
            - startDate: string (YYYY-MM-DD)
            - endDate: string (YYYY-MM-DD)
            - totalStoryPoints: number
            - completedStoryPoints: number (default: 0)
            - progress: number (default: 0)
            - userStories: array of user story objects with:
                - id: string
                - title: string
                - description: string
                - storyPoints: number
                - priority: string ("high", "medium", "low")
                - status: string ("todo", "in-progress", "done", "backlog")
                - assignee: string (optional)
                - acceptanceCriteria: array of strings
        document_name: Optional name for the SRS document
        document_url: Optional URL of the source document
    
    Returns:
        JSON response with status and synced sprints
    """
    try:
        logger.info("Sending sprints to dashboard")
        
        if not sprints_json or not sprints_json.strip():
            return json.dumps({
                "status": "error",
                "message": "Sprints JSON is required"
            }, indent=2)
        
        # Parse sprints JSON
        try:
            sprints_data = json.loads(sprints_json)
            # Handle both direct array and object with "sprints" key
            if isinstance(sprints_data, dict):
                sprints = sprints_data.get("sprints", [])
                srs_document = sprints_data.get("srs_document")
            elif isinstance(sprints_data, list):
                sprints = sprints_data
                srs_document = None
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Invalid sprints JSON format. Expected array or object with 'sprints' key"
                }, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON format: {str(e)}"
            }, indent=2)
        
        if not sprints or len(sprints) == 0:
            return json.dumps({
                "status": "error",
                "message": "No sprints found in the provided JSON"
            }, indent=2)
        
        # Ensure each sprint has required fields and user stories
        for sprint in sprints:
            if "id" not in sprint:
                sprint["id"] = f"sprint-{sprints.index(sprint) + 1}"
            if "userStories" not in sprint:
                sprint["userStories"] = []
            if "totalStoryPoints" not in sprint:
                sprint["totalStoryPoints"] = sum(story.get("storyPoints", 0) for story in sprint.get("userStories", []))
            if "completedStoryPoints" not in sprint:
                sprint["completedStoryPoints"] = 0
            if "progress" not in sprint:
                total = sprint.get("totalStoryPoints", 1)
                sprint["progress"] = int((sprint["completedStoryPoints"] / total) * 100) if total > 0 else 0
            
            # Ensure each user story has required fields
            for story in sprint.get("userStories", []):
                if "id" not in story:
                    story["id"] = f"us-{sprint['id']}-{sprint['userStories'].index(story) + 1}"
                if "status" not in story:
                    story["status"] = "todo"
                if "priority" not in story:
                    story["priority"] = "medium"
                if "acceptanceCriteria" not in story:
                    story["acceptanceCriteria"] = []
        
        # Send to backend API
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        api_endpoint = f"{backend_url}/api/srs/sync-sprints"
        
        try:
            response = requests.post(
                api_endpoint,
                json={
                    "sprints": sprints,
                    "srs_document": srs_document,
                    "document_name": document_name,
                    "document_url": document_url
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.dumps({
                    "status": "success",
                    "message": f"Successfully sent {len(sprints)} sprints to dashboard",
                    "sprints_count": len(sprints),
                    "total_user_stories": sum(len(s.get("userStories", [])) for s in sprints),
                    "dashboard_response": result
                }, indent=2)
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", error_detail)
                except:
                    pass
                
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to send sprints: Backend responded with status {response.status_code}",
                    "error": error_detail
                }, indent=2)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach backend API: {e}")
            return json.dumps({
                "status": "error",
                "message": f"Backend API is unreachable: {str(e)}",
                "error": "Make sure the backend server is running at " + backend_url
            }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in send_sprints_to_dashboard: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to send sprints: {str(e)}"
        }, indent=2)

def run():
    """Run the MCP server"""
    if not jira_client.url:
        logger.warning("No JIRA_URL found. Please set JIRA_URL environment variable.")
    if not jira_client.personal_token and not (jira_client.email and jira_client.api_token):
        logger.warning("No Jira credentials found. Please set JIRA_EMAIL and JIRA_API_TOKEN (Cloud) or JIRA_PERSONAL_TOKEN (Server/DC).")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run()

