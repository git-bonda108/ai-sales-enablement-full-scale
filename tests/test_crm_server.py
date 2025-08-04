"""
Test script for CRM MCP Server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
import json

async def test_crm_server():
    """Test the CRM MCP server"""

    print("🧪 Testing CRM MCP Server")
    print("=" * 50)

    # Create server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "servers.crm_server"],
        env=None
    )

    # Connect to the server
    async with ClientSession(server_params) as session:
        # Initialize the connection
        await session.initialize()

        print("✅ Connected to CRM MCP server!")
        print()

        # Test 1: List all accounts
        print("Test 1: List all accounts")
        result = await session.call_tool("list_all_accounts", {})
        accounts = json.loads(result.content[0].text)
        print(f"   Found {len(accounts)} accounts")
        if accounts:
            print(f"   Top account: {accounts[0]['name']} (${accounts[0]['annual_revenue']:,.0f})")
        print()

        # Test 2: Search accounts
        print("Test 2: Search accounts in Technology")
        result = await session.call_tool("search_accounts", {"industry": "Technology", "limit": 3})
        tech_accounts = json.loads(result.content[0].text)
        print(f"   Found {len(tech_accounts)} technology accounts")
        print()

        # Test 3: Get account details
        if accounts:
            print(f"Test 3: Get details for {accounts[0]['name']}")
            result = await session.call_tool("get_account_details", {"account_id": accounts[0]['id']})
            details = json.loads(result.content[0].text)
            print(f"   Contacts: {len(details['contacts'])}")
            print(f"   Deals: {len(details['deals'])}")
            print(f"   Total deal value: ${details['total_deal_value']:,.2f}")
            print()

        # Test 4: Create a new deal
        print("Test 4: Create new deal")
        result = await session.call_tool("create_deal", {
            "account_id": 1,
            "deal_name": "Q4 Enterprise License",
            "amount": 125000,
            "stage": "Qualification"
        })
        new_deal = json.loads(result.content[0].text)
        print(f"   Created deal ID: {new_deal['deal_id']}")
        print(f"   Amount: ${new_deal['amount']:,.2f}")
        print()

        # Test 5: Update deal stage
        print("Test 5: Update deal stage")
        result = await session.call_tool("update_deal_stage", {
            "deal_id": new_deal['deal_id'],
            "new_stage": "Proposal",
            "notes": "Customer interested, preparing proposal"
        })
        update = json.loads(result.content[0].text)
        print(f"   {update['message']}")
        print(f"   New probability: {update['probability']}%")
        print()

        # Test 6: Get pipeline summary
        print("Test 6: Pipeline summary")
        result = await session.call_tool("get_pipeline_summary", {})
        pipeline = json.loads(result.content[0].text)
        print(f"   Total pipeline: ${pipeline['total_pipeline_value']:,.2f}")
        print(f"   Weighted value: ${pipeline['weighted_pipeline_value']:,.2f}")
        print(f"   Win rate: {pipeline['win_rate']:.1f}%")
        print()

        print("✅ All CRM tests passed!")
        print()
        print("🎯 CRM Server is ready for the demo!")

if __name__ == "__main__":
    asyncio.run(test_crm_server())
