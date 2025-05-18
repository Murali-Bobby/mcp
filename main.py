from src.fastMpc_instance import mcp
import src.jira_integration
import src.testrail

if __name__ == "__main__":
    mcp.run(transport="sse")
