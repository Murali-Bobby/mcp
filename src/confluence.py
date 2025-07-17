import os
from atlassian import Confluence
from dotenv import load_dotenv
from typing import List, Dict
from src.fastMpc_instance import mcp

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def get_confluence_client() -> Confluence:
    return Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_EMAIL,
        password=CONFLUENCE_API_TOKEN,
        cloud=True
    )

@mcp.tool()
async def get_confluence_spaces() -> dict:
    """
    Fetch list of accessible Confluence spaces.
    """
    try:
        confluence = get_confluence_client()
        spaces = confluence.get_all_spaces(start=0, limit=100)
        return {
            "spaces": [
                {"key": space["key"], "name": space["name"]}
                for space in spaces["results"]
            ]
        }
    except Exception as e:
        return {"error": f"Confluence API error: {str(e)}"}

@mcp.tool()
async def get_confluence_pages(space_key: str) -> dict:
    """
    Fetch pages from a Confluence space.

    Args:
        space_key: Key of the space to retrieve pages from.
    """
    try:
        confluence = get_confluence_client()
        pages = confluence.get_all_pages_from_space(space=space_key, start=0, limit=50)
        return {
            "pages": [
                {"id": page["id"], "title": page["title"]}
                for page in pages
            ]
        }
    except Exception as e:
        return {"error": f"Failed to get pages from space '{space_key}': {str(e)}"}

@mcp.tool()
async def get_page_content(page_id: str) -> dict:
    """
    Fetch the content of a Confluence page.

    Args:
        page_id: ID of the Confluence page.
    """
    try:
        confluence = get_confluence_client()
        page = confluence.get_page_by_id(page_id, expand='body.storage')
        if not page:
            return {"error": f"No page found for ID {page_id}"}
        
        return {
            "title": page["title"],
            "content_html": page["body"]["storage"]["value"]
        }
    except Exception as e:
        return {"error": f"Failed to fetch page content: {str(e)}"}

@mcp.tool()
async def get_page_by_title(title: str, space_key: str = None) -> dict:
    """
    Fetch a Confluence page by its title (optionally within a space).

    Args:
        title: The title (name) of the Confluence page.
        space_key: (Optional) The space key to limit the search.

    Returns:
        The page content or an error message.
    """
    try:
        confluence = get_confluence_client()
        
        page = confluence.get_page_by_title(space=space_key, title=title) if space_key \
            else confluence.get_page(title=title)
        
        if not page:
            return {"error": f"No page found with title '{title}'"}

        return {
            "id": page["id"],
            "title": page["title"],
            "space": page["space"]["key"],
            "content_html": page["body"]["storage"]["value"]
        }
    except Exception as e:
        return {"error": f"Confluence API error: {str(e)}"}
