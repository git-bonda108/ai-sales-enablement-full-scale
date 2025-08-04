"""
Test script for Analytics MCP Server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
import json

async def test_analytics_server():
    """Test the Analytics MCP server"""

    print("🧪 Testing Analytics MCP Server")
    print("=" * 50)

    # Create server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "servers.analytics_server"],
        env=None
    )

    # Connect to the server
    async with ClientSession(server_params) as session:
        # Initialize the connection
        await session.initialize()

        print("✅ Connected to Analytics MCP server!")
        print()

        # Test 1: Sales Forecast
        print("Test 1: Generate Sales Forecast")
        result = await session.call_tool("generate_sales_forecast", {
            "period": "next_quarter",
            "method": "weighted_pipeline"
        })
        forecast = json.loads(result.content[0].text)
        print(f"   Expected revenue: ${forecast['forecast']['expected']:,.2f}")
        print(f"   Confidence range: ${forecast['forecast']['low']:,.2f} - ${forecast['forecast']['high']:,.2f}")
        print()

        # Test 2: Conversion Rates
        print("Test 2: Analyze Conversion Rates")
        result = await session.call_tool("analyze_conversion_rates", {
            "time_period": "last_quarter"
        })
        conversions = json.loads(result.content[0].text)
        print(f"   Overall win rate: {conversions['overall_metrics']['win_rate']}%")
        print(f"   Total deals analyzed: {conversions['overall_metrics']['total_deals']}")
        print()

        # Test 3: Deal Scoring
        print("Test 3: Calculate Deal Scoring")
        result = await session.call_tool("calculate_deal_scoring", {
            "include_all_open": True
        })
        scores = json.loads(result.content[0].text)
        if scores:
            print(f"   Top deal: {scores[0]['deal_name']}")
            print(f"   Score: {scores[0]['score']}/100")
            print(f"   Priority: {scores[0]['priority']}")
            print(f"   Action: {scores[0]['recommended_action']}")
        print()

        # Test 4: Activity Analytics
        print("Test 4: Activity Analytics")
        result = await session.call_tool("get_activity_analytics", {
            "time_period": "last_30_days",
            "group_by": "activity_type"
        })
        activities = json.loads(result.content[0].text)
        print(f"   Total activities: {activities['summary']['total_activities']}")
        print(f"   Accounts touched: {activities['summary']['accounts_touched']}")
        print()

        # Test 5: Performance Metrics
        print("Test 5: Performance Metrics")
        result = await session.call_tool("get_performance_metrics", {
            "metric_type": "summary"
        })
        metrics = json.loads(result.content[0].text)
        print(f"   Closed revenue: ${metrics['revenue_metrics']['closed_revenue']:,.2f}")
        print(f"   Pipeline value: ${metrics['revenue_metrics']['pipeline_value']:,.2f}")
        print(f"   Win rate: {metrics['conversion_metrics']['win_rate']}%")

        print()
        print("✅ All Analytics tests passed!")
        print()
        print("🎯 Analytics Server is ready for the demo!")

if __name__ == "__main__":
    asyncio.run(test_analytics_server())
