"""Main entry point for the MCP server.

This module initializes and runs the FastMCP server that provides
PPE risk assessment tools via the Model Context Protocol (MCP).
The server exposes tools for recording and managing PPE incidents.
"""

from mcp.server.fastmcp.server import FastMCP

from tools.risk_assessment_recorder_tool import RiskAssesmentToolSpec

# Initialize the risk assessment tool specification
ppe_risk_assessment_tool_spec = RiskAssesmentToolSpec()

# Convert tool specification to tool list for MCP server
tools = ppe_risk_assessment_tool_spec.to_tool_list(
    spec_functions=RiskAssesmentToolSpec.spec_functions,
    func_to_metadata_mapping=RiskAssesmentToolSpec.func_to_metadata_mapping
)

# Create FastMCP server instance
app = FastMCP(name="PPE Risk Assessment Tool", host='127.0.0.1', port=8100)
print("Hello from my-mcp-server!")

# Register all tools with the MCP server
for tool in tools:
    app.tool(
        name=tool.metadata.name,
        description=tool.metadata.description
    )(tool.fn)


if __name__ == '__main__':
    """Run the MCP server when executed directly."""
    app.run(transport="streamable-http")
