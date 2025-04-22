import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict
from mcp.server.fastmcp import FastMCP
load_dotenv()
# Initialize MCP Server
mcp = FastMCP("testrail-mcp")
# TestRail API Configuration
TESTRAIL_URL = "https://platformsciencetest.testrail.io"
def get_testrail_client():
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    session.auth = ("vrnkmrv@gmail.com", "vV@6269436")  # Use your TestRail username and password
    return session
def get_testrail_url(endpoint):
    return f"{TESTRAIL_URL}/index.php?/api/v2/{endpoint}"
@mcp.tool()
async def log_message(message: str) -> str:
    """
    Log a message to the server console.
    """
    print(f"[Log]: {message}")
    return f"Message logged: {message}"
@mcp.tool()
async def get_projects() -> dict:
    """
    Get list of active TestRail projects.
    """
    try:
        client = get_testrail_client()
        url = get_testrail_url("get_projects")
        response = client.get(url)
        if response.status_code == 200:
            return {"projects": response.json()}
        else:
            return {"error": f"Failed to fetch projects: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": f"TestRail API error: {str(e)}"}
@mcp.tool()
async def get_project_metrics(project_id: int) -> dict:
    """
    Get metrics for a specific TestRail project.
    Args:
        project_id: ID of the TestRail project
    """
    try:
        client = get_testrail_client()
        url = get_testrail_url(f"get_runs/{project_id}")
        response = client.get(url)
        if response.status_code != 200:
            return {"error": f"Failed to fetch runs: {response.status_code}"}
        runs = response.json()
        total_runs = len(runs)
        completed_runs = sum(1 for run in runs if run.get("is_completed"))
        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "completion_rate": f"{(completed_runs / total_runs) * 100:.2f}%" if total_runs else "0%"
        }
    except Exception as e:
        return {"error": f"TestRail API error: {str(e)}"}
if __name__ == "__main__":
    mcp.run(transport="stdio")