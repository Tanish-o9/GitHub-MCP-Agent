import asyncio
import os
import shutil
from textwrap import dedent

import mcp.shared.exceptions
import mcp.types
import fastmcp

if not hasattr(mcp.shared.exceptions, "MCPError"):
    mcp.shared.exceptions.MCPError = mcp.shared.exceptions.McpError

_orig_client_init = fastmcp.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs.pop("mode", None)
    return _orig_client_init(self, *args, **kwargs)
fastmcp.Client.__init__ = _patched_client_init

if not hasattr(mcp.types.Tool, "input_schema"):
    mcp.types.Tool.input_schema = property(lambda self: getattr(self, "inputSchema", {}))

from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters


async def run_github_agent(message: str, runner_type: str = "npx (Node.js)") -> str:
    """
    Executes the GitHub MCP Agent query using either NPX or Docker runner.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GitHub token not provided. Please set it in the sidebar or environment."
    
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OpenAI API key not provided. Please set it in the sidebar or environment."
    
    try:
        env_vars = {
            **os.environ,
            "GITHUB_PERSONAL_ACCESS_TOKEN": token,
            "GITHUB_TOOLSETS": "repos,issues,pull_requests"
        }
        
        if "Docker" in runner_type:
            docker_cmd = shutil.which("docker") or "docker"
            server_params = StdioServerParameters(
                command=docker_cmd,
                args=[
                    "run", "-i", "--rm",
                    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "-e", "GITHUB_TOOLSETS",
                    "ghcr.io/github/github-mcp-server"
                ],
                env=env_vars
            )
        else:
            npx_cmd = shutil.which("npx") or "npx"
            server_params = StdioServerParameters(
                command=npx_cmd,
                args=["-y", "@modelcontextprotocol/server-github"],
                env=env_vars
            )
        
        async with MCPTools(server_params=server_params) as mcp_tools:
            agent = Agent(
                tools=[mcp_tools],
                instructions=dedent("""\
                    You are a GitHub assistant. Help users explore repositories and their activity.
                    - Provide organized, concise insights about the repository
                    - Focus on facts and data from the GitHub API
                    - Use markdown formatting for better readability
                    - Present numerical data in tables when appropriate
                    - Include links to relevant GitHub pages when helpful
                """),
                markdown=True,
            )
            
            response: RunOutput = await asyncio.wait_for(agent.arun(message), timeout=120.0)
            return response.content or "No content returned from agent."
                
    except asyncio.TimeoutError:
        return "Error: Request timed out after 120 seconds"
    except Exception as e:
        return f"Error: {str(e)}"
