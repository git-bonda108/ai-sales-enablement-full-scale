"""
Test script for Basic MCP Server
This shows how to connect to and use MCP servers
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
import json

async def test_basic_server():
    """Test our basic MCP server"""

    print("🧪 Testing Basic MCP Server")
    print("=" * 50)

    # Create server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "servers.basic_server"],
        env=None
    )

    # Connect to the server
    async with ClientSession(server_params) as session:
        # Initialize the connection
        await session.initialize()

        print("✅ Connected to MCP server!")
        print()

        # List available tools
        tools = await session.list_tools()
        print("📋 Available tools:")
        for tool in tools.tools:
            print(f"   - {tool.name}: {tool.description}")
        print()

        # Test 1: Greet user
        print("Test 1: Greeting")
        result = await session.call_tool("greet_user", {"name": "Sales Team"})
        print(f"   Result: {result.content[0].text}")
        print()

        # Test 2: Calculate commission
        print("Test 2: Commission calculation")
        result = await session.call_tool(
            "calculate_commission", 
            {"sale_amount": 10000, "commission_rate": 0.15}
        )
        data = json.loads(result.content[0].text)
        print(f"   Sale: ${data['sale_amount']}")
        print(f"   Rate: {data['commission_rate']*100}%")
        print(f"   Commission: ${data['commission']}")
        print()

        # Test 3: List features
        print("Test 3: Demo features")
        result = await session.call_tool("list_demo_features", {})
        features = json.loads(result.content[0].text)
        for i, feature in enumerate(features, 1):
            print(f"   {i}. {feature}")

        print()
        print("✅ All tests passed!")
        print()
        print("🎯 MCP is working correctly! Ready to build the full demo.")

if __name__ == "__main__":
    asyncio.run(test_basic_server())
