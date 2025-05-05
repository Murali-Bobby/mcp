import os
from typing import Dict, List
import requests
from jira import JIRA
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize MCP Server
mcp = FastMCP("testrail-mcp")

# Jira Configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def get_jira_client() -> JIRA:
    """
    Get authenticated Jira client
    """
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

@mcp.tool()
async def get_jira_projects() -> dict:
    """
    Get list of accessible Jira projects
    """
    try:
        jira = get_jira_client()
        projects = jira.projects()
        return {
            "projects": [
                {
                    "id": project.id,
                    "key": project.key,
                    "name": project.name
                }
                for project in projects
            ]
        }
    except Exception as e:
        return {"error": f"Jira API error: {str(e)}"}

@mcp.tool()
async def get_project_issues(project_key: str) -> dict:
    """
    Get issues and metrics for a specific Jira project
    Args:
        project_key: Key of the Jira project (e.g., 'PROJ')
    """
    try:
        jira = get_jira_client()
        
        # Get all issues for the project
        issues = jira.search_issues(f'project={project_key}', maxResults=1000)
        
        # Calculate metrics
        total_issues = len(issues)
        open_issues = sum(1 for issue in issues if issue.fields.status.name.lower() not in ['done', 'closed'])
        completed_issues = total_issues - open_issues
        
        return {
            "total_issues": total_issues,
            "open_issues": open_issues,
            "completed_issues": completed_issues,
            "completion_rate": f"{(completed_issues / total_issues) * 100:.2f}%" if total_issues else "0%"
        }
    except Exception as e:
        return {"error": f"Jira API error: {str(e)}"}

@mcp.tool()
async def get_sprint_metrics(project_key: str, board_id: int) -> dict:
    """
    Get sprint metrics for a specific board
    Args:
        project_key: Key of the Jira project
        board_id: ID of the Jira board
    """
    try:
        jira = get_jira_client()
        
        # Get active and recently closed sprints
        sprints = jira.sprints(board_id, state='active,closed')
        active_sprints = [sprint for sprint in sprints if sprint.state == 'active']
        
        if not active_sprints:
            return {"error": "No active sprints found"}
            
        current_sprint = active_sprints[0]
        sprint_issues = jira.search_issues(f'sprint={current_sprint.id}')
        
        # Calculate sprint metrics
        total_issues = len(sprint_issues)
        completed_issues = sum(1 for issue in sprint_issues 
                             if issue.fields.status.name.lower() in ['done', 'closed'])
        
        return {
            "sprint_name": current_sprint.name,
            "total_issues": total_issues,
            "completed_issues": completed_issues,
            "remaining_issues": total_issues - completed_issues,
            "completion_rate": f"{(completed_issues / total_issues) * 100:.2f}%" if total_issues else "0%"
        }
    except Exception as e:
        return {"error": f"Jira API error: {str(e)}"}
    

@mcp.tool()
async def get_jira_ticket_details(ticket_id_or_key: str) -> dict:
    """
    Fetch details of a specific JIRA ticket by ID or key.

    Args:
        ticket_id_or_key: The ID or key of the JIRA ticket (e.g., 'PROJ-123').

    Returns:
        Dictionary with key ticket fields or an error.
    """
    try:
        jira = get_jira_client()
        issue = jira.issue(ticket_id_or_key)

        return {
            "ticket_key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "reporter": issue.fields.reporter.displayName,
            "created": issue.fields.created,
            "updated": issue.fields.updated,
            "priority": issue.fields.priority.name if issue.fields.priority else "Not set",
            "labels": issue.fields.labels,
            "project": {
                "key": issue.fields.project.key,
                "name": issue.fields.project.name
            }
        }

    except Exception as e:
        return {"error": f"Failed to fetch ticket details: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
