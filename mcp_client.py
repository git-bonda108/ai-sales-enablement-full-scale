"""
MCP Client - Connects to both CRM and Analytics servers
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MCPSalesClient:
    """Client that manages connections to both MCP servers"""

    def __init__(self):
        self.crm_session = None
        self.analytics_session = None
        self.connected = False

    async def connect(self):
        """Connect to both MCP servers"""
        try:
            # CRM Server connection
            crm_params = StdioServerParameters(
                command="uv",
                args=["run", "python", "-m", "servers.crm_server"],
                env=None
            )

            # Analytics Server connection
            analytics_params = StdioServerParameters(
                command="uv",
                args=["run", "python", "-m", "servers.analytics_server"],
                env=None
            )

            # Create sessions
            self.crm_session = ClientSession(crm_params)
            self.analytics_session = ClientSession(analytics_params)

            # Connect to both
            await self.crm_session.__aenter__()
            await self.analytics_session.__aenter__()

            # Initialize both
            await self.crm_session.initialize()
            await self.analytics_session.initialize()

            self.connected = True
            logger.info("✅ Connected to both MCP servers")

            return True

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from servers"""
        if self.crm_session:
            await self.crm_session.__aexit__(None, None, None)
        if self.analytics_session:
            await self.analytics_session.__aexit__(None, None, None)
        self.connected = False

    async def call_crm_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Call a tool on the CRM server"""
        if not self.connected:
            raise Exception("Not connected to servers")

        try:
            result = await self.crm_session.call_tool(tool_name, arguments)
            return json.loads(result.content[0].text)
        except Exception as e:
            logger.error(f"CRM tool error: {e}")
            raise

    async def call_analytics_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Call a tool on the Analytics server"""
        if not self.connected:
            raise Exception("Not connected to servers")

        try:
            result = await self.analytics_session.call_tool(tool_name, arguments)
            return json.loads(result.content[0].text)
        except Exception as e:
            logger.error(f"Analytics tool error: {e}")
            raise

    # Convenience methods for common operations

    async def get_accounts(self, query: Optional[str] = None, industry: Optional[str] = None) -> List[Dict]:
        """Get list of accounts"""
        return await self.call_crm_tool("search_accounts", {
            "query": query,
            "industry": industry,
            "limit": 20
        })

    async def get_account_360(self, account_id: int) -> Dict:
        """Get complete account view with analytics"""
        # Get account details from CRM
        account_details = await self.call_crm_tool("get_account_details", {
            "account_id": account_id
        })

        # Get deal scores for this account
        deal_scores = await self.call_analytics_tool("calculate_deal_scoring", {
            "account_id": account_id,
            "include_all_open": False
        })

        # Combine data
        account_details["deal_scores"] = deal_scores
        return account_details

    async def get_pipeline_dashboard(self) -> Dict:
        """Get complete pipeline dashboard"""
        # Get pipeline from CRM
        pipeline = await self.call_crm_tool("get_pipeline_summary", {})

        # Get forecast from Analytics
        forecast = await self.call_analytics_tool("generate_sales_forecast", {
            "period": "next_quarter",
            "method": "hybrid"
        })

        # Get performance metrics
        metrics = await self.call_analytics_tool("get_performance_metrics", {
            "metric_type": "summary"
        })

        return {
            "pipeline": pipeline,
            "forecast": forecast,
            "metrics": metrics
        }

    async def create_and_score_deal(self, account_id: int, deal_data: Dict) -> Dict:
        """Create a deal and get its AI score"""
        # Create deal in CRM
        new_deal = await self.call_crm_tool("create_deal", {
            "account_id": account_id,
            "deal_name": deal_data["name"],
            "amount": deal_data["amount"],
            "stage": deal_data.get("stage", "Prospecting"),
            "close_date": deal_data.get("close_date")
        })

        # Get AI score for new deal
        scores = await self.call_analytics_tool("calculate_deal_scoring", {
            "account_id": account_id,
            "include_all_open": True
        })

        # Find score for new deal
        deal_score = next((s for s in scores if s["deal_id"] == new_deal["deal_id"]), None)

        return {
            "deal": new_deal,
            "score": deal_score
        }

    async def get_sales_insights(self) -> Dict:
        """Get AI-powered sales insights"""
        # Get conversion rates
        conversions = await self.call_analytics_tool("analyze_conversion_rates", {
            "time_period": "last_quarter"
        })

        # Get activity analytics
        activities = await self.call_analytics_tool("get_activity_analytics", {
            "time_period": "last_30_days",
            "group_by": "activity_type"
        })

        # Get top deals to focus on
        hot_deals = await self.call_analytics_tool("calculate_deal_scoring", {
            "include_all_open": True
        })

        return {
            "conversions": conversions,
            "activities": activities,
            "hot_deals": hot_deals[:5]  # Top 5
        }

# Singleton instance
_client_instance = None

async def get_client() -> MCPSalesClient:
    """Get or create the MCP client instance"""
    global _client_instance

    if _client_instance is None:
        _client_instance = MCPSalesClient()
        await _client_instance.connect()

    return _client_instance

# Example usage
if __name__ == "__main__":
    async def test_client():
        client = await get_client()

        # Test getting accounts
        accounts = await client.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # Test pipeline dashboard
        dashboard = await client.get_pipeline_dashboard()
        print(f"Pipeline value: ${dashboard['pipeline']['total_pipeline_value']:,.2f}")
        print(f"Forecast: ${dashboard['forecast']['forecast']['expected']:,.2f}")

        await client.disconnect()

    asyncio.run(test_client())
