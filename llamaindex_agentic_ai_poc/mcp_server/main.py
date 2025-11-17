from mcp.server.fastmcp.server import FastMCP

from tools.risk_assessment_recorder_tool import RiskAssesmentToolSpec
ppe_risk_assessment_tool_spec = RiskAssesmentToolSpec()
tools = ppe_risk_assessment_tool_spec.to_tool_list(
    spec_functions=RiskAssesmentToolSpec.spec_functions,
func_to_metadata_mapping=RiskAssesmentToolSpec.func_to_metadata_mapping)
app = FastMCP(name="PPE Risk Assessment Tool",host='127.0.0.1',port=8100)
print("Hello from my-mcp-server!")

for tool in tools:
    app.tool(
        name=tool.metadata.name,
        description=tool.metadata.description
    )(tool.fn)

if __name__ == '__main__':
    app.run(transport="streamable-http")


