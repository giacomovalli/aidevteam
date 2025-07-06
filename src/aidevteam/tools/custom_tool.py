from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolInput(BaseModel):
    """Input schema for MCP Tool."""
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the MCP tool")

class MCPTool(BaseTool):
    name: str = "MCP Tool"
    description: str = (
        "Execute tools from an MCP server. Specify the tool name and arguments to call any available MCP tool."
    )
    args_schema: Type[BaseModel] = MCPToolInput
    
    def __init__(self, server_command: str, server_args: Optional[list] = None):
        super().__init__()
        self.server_command = server_command
        self.server_args = server_args or []
        self._available_tools = {}
        self._client_session = None
    
    async def _get_client_session(self):
        """Get or create MCP client session"""
        if self._client_session is None:
            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args
            )
            self._client_session = await stdio_client(server_params)
        return self._client_session
    
    async def _list_tools(self):
        """List available tools from MCP server"""
        async with await self._get_client_session() as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return {tool.name: tool for tool in tools.tools}
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a specific tool on the MCP server"""
        async with await self._get_client_session() as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result

    def _run(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Execute MCP tool call"""
        if arguments is None:
            arguments = {}
        
        try:
            # Run async code in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self._call_tool(tool_name, arguments))
                return json.dumps(result.content, indent=2)
            finally:
                loop.close()
                
        except Exception as e:
            return f"Error calling MCP tool '{tool_name}': {str(e)}"


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
