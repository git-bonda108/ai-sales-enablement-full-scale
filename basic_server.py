"""
Basic MCP Server - Proof of Concept
This demonstrates how MCP servers work before we build the full demo
"""

from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime

# Initialize MCP server
mcp = FastMCP("AI Sales Demo - Basic Server")

# Test tool 1: Simple greeting
@mcp.tool()
def greet_user(name: str) -> str:
    """
    Greets a user by name - tests basic tool functionality

    Args:
        name: The name to greet

    Returns:
        A friendly greeting message
    """
    return f"Hello {name}! Welcome to the AI Sales MCP Demo. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Test tool 2: Basic calculation
@mcp.tool()
def calculate_commission(sale_amount: float, commission_rate: float = 0.1) -> dict:
    """
    Calculates sales commission - tests returning structured data

    Args:
        sale_amount: The sale amount in dollars
        commission_rate: Commission rate (default 10%)

    Returns:
        Dictionary with commission details
    """
    commission = sale_amount * commission_rate
    return {
        "sale_amount": sale_amount,
        "commission_rate": commission_rate,
        "commission": round(commission, 2),
        "net_amount": round(sale_amount - commission, 2)
    }

# Test tool 3: List capabilities
@mcp.tool()
def list_demo_features() -> list:
    """
    Lists the features of our AI Sales demo - tests returning lists

    Returns:
        List of demo features
    """
    return [
        "Private CRM data access",
        "AI-powered deal scoring",
        "Sales forecasting",
        "Pipeline analytics",
        "Activity tracking",
        "No external API calls - fully private"
    ]

# Run the server
if __name__ == "__main__":
    print("🚀 Starting Basic MCP Server...")
    print("📍 Server: AI Sales Demo - Basic Server")
    print("🛠️  Tools available:")
    print("   - greet_user(name)")
    print("   - calculate_commission(sale_amount, commission_rate)")
    print("   - list_demo_features()")
    print()
    print("Ready to accept MCP connections!")
    print("Test with: uv run python tests/test_basic_server.py")

    # Run the MCP server
    mcp.run()
