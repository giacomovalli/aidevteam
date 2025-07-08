from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field
import json
from crewai_tools import MCPServerAdapter
from mcp.types import Tool as MCPTool


class MCPToolInput(BaseModel):
    """Input schema for MCP Tool."""
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the MCP tool")

class MCPAdapterTool(BaseTool):
    name: str = "MCP Adapter Tool"
    description: str = (
        "Execute tools from an MCP server using MCPServerAdapter. Specify the tool name and arguments to call any available MCP tool."
    )
    args_schema: Type[BaseModel] = MCPToolInput
    
    def __init__(self, server_adapter: MCPServerAdapter):
        super().__init__()
        self.server_adapter = server_adapter
        self._available_tools: Dict[str, MCPTool] = {}
    
    def _get_available_tools(self) -> Dict[str, MCPTool]:
        """Get available tools from MCP server adapter"""
        if not self._available_tools:
            try:
                tools_result = self.server_adapter.list_tools()
                self._available_tools = {tool.name: tool for tool in tools_result.tools}
            except Exception as e:
                return {}
        return self._available_tools
    
    def _run(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Execute MCP tool call"""
        if arguments is None:
            arguments = {}
        
        try:
            # Get available tools first
            available_tools = self._get_available_tools()
            
            if tool_name not in available_tools:
                available_names = list(available_tools.keys())
                return f"Tool '{tool_name}' not found. Available tools: {available_names}"
            
            # Call the tool using the adapter
            result = self.server_adapter.call_tool(tool_name, arguments)
            
            # Format the result
            if hasattr(result, 'content'):
                return json.dumps(result.content, indent=2)
            else:
                return str(result)
                
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

class HumanInquiryTool(BaseTool):
    name: str = "Human Inquiry Tool"
    description: str = (
        "Use this tool to ask the user clarifying questions "
        "when critical information is missing or ambiguous. "
        "This is your ONLY way to get more details from the user."
    )

    def _run(self, question: str) -> str:
        """Prompts the user for input with a specific question."""
        print("\n" + "="*30 + "\n")
        print(f"🤔 The agent needs your input! 🤔")
        print(f"Question: {question}")
        response = input("Your answer: ")
        print("\n" + "="*30 + "\n")
        return response
