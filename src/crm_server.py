"""
CRM MCP Server - Full Implementation
Provides account management, deal tracking, and pipeline analytics
"""

from mcp.server.fastmcp import FastMCP
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# Initialize MCP server
mcp = FastMCP("AI Sales CRM Server")

# Database path
DB_PATH = os.path.join("data", "sales_crm.db")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def search_accounts(
    query: Optional[str] = None,
    industry: Optional[str] = None,
    min_revenue: Optional[float] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Search for customer accounts with filters

    Args:
        query: Search term for account name
        industry: Filter by industry
        min_revenue: Minimum annual revenue
        limit: Maximum results to return

    Returns:
        List of matching accounts
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM accounts WHERE 1=1"
    params = []

    if query:
        sql += " AND name LIKE ?"
        params.append(f"%{query}%")

    if industry:
        sql += " AND industry = ?"
        params.append(industry)

    if min_revenue:
        sql += " AND annual_revenue >= ?"
        params.append(min_revenue)

    sql += f" ORDER BY annual_revenue DESC LIMIT {limit}"

    cursor.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    results = []

    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    conn.close()
    return results

@mcp.tool()
def get_account_details(account_id: int) -> Dict:
    """
    Get detailed information about a specific account

    Args:
        account_id: The account ID

    Returns:
        Account details including contacts and deals
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get account info
    cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    account_row = cursor.fetchone()
    if not account_row:
        return {"error": "Account not found"}

    columns = [desc[0] for desc in cursor.description]
    account = dict(zip(columns, account_row))

    # Get contacts
    cursor.execute("SELECT * FROM contacts WHERE account_id = ?", (account_id,))
    contacts = []
    contact_columns = [desc[0] for desc in cursor.description]
    for row in cursor.fetchall():
        contacts.append(dict(zip(contact_columns, row)))

    # Get deals
    cursor.execute("SELECT * FROM deals WHERE account_id = ?", (account_id,))
    deals = []
    deal_columns = [desc[0] for desc in cursor.description]
    for row in cursor.fetchall():
        deals.append(dict(zip(deal_columns, row)))

    # Get activities
    cursor.execute(
        "SELECT * FROM activities WHERE account_id = ? ORDER BY activity_date DESC LIMIT 10",
        (account_id,)
    )
    activities = []
    activity_columns = [desc[0] for desc in cursor.description]
    for row in cursor.fetchall():
        activities.append(dict(zip(activity_columns, row)))

    conn.close()

    return {
        "account": account,
        "contacts": contacts,
        "deals": deals,
        "recent_activities": activities,
        "total_deal_value": sum(d["amount"] for d in deals),
        "open_deals": len([d for d in deals if d["stage"] != "Closed Won" and d["stage"] != "Closed Lost"])
    }

@mcp.tool()
def create_deal(
    account_id: int,
    deal_name: str,
    amount: float,
    stage: str = "Prospecting",
    close_date: Optional[str] = None,
    probability: int = 10
) -> Dict:
    """
    Create a new deal in the pipeline

    Args:
        account_id: Account this deal belongs to
        deal_name: Name of the deal
        amount: Deal value in dollars
        stage: Current stage (Prospecting, Qualification, Proposal, Negotiation, Closed Won/Lost)
        close_date: Expected close date (YYYY-MM-DD)
        probability: Win probability percentage

    Returns:
        Created deal information
    """
    conn = get_db()
    cursor = conn.cursor()

    if not close_date:
        close_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO deals (account_id, name, amount, stage, close_date, probability, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (account_id, deal_name, amount, stage, close_date, probability, datetime.now().strftime("%Y-%m-%d")))

    deal_id = cursor.lastrowid

    # Log activity
    cursor.execute("""
        INSERT INTO activities (account_id, activity_type, description, activity_date)
        VALUES (?, ?, ?, ?)
    """, (account_id, "Deal Created", f"New deal '{deal_name}' created for ${amount:,.2f}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return {
        "deal_id": deal_id,
        "account_id": account_id,
        "name": deal_name,
        "amount": amount,
        "stage": stage,
        "close_date": close_date,
        "probability": probability,
        "message": "Deal created successfully"
    }

@mcp.tool()
def update_deal_stage(
    deal_id: int,
    new_stage: str,
    probability: Optional[int] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Update deal stage in the pipeline

    Args:
        deal_id: ID of the deal to update
        new_stage: New stage name
        probability: Updated win probability
        notes: Optional notes about the update

    Returns:
        Updated deal information
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get current deal
    cursor.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
    deal = cursor.fetchone()
    if not deal:
        return {"error": "Deal not found"}

    # Update deal
    if probability is None:
        stage_probabilities = {
            "Prospecting": 10,
            "Qualification": 20,
            "Proposal": 40,
            "Negotiation": 60,
            "Closed Won": 100,
            "Closed Lost": 0
        }
        probability = stage_probabilities.get(new_stage, 50)

    cursor.execute("""
        UPDATE deals SET stage = ?, probability = ? WHERE id = ?
    """, (new_stage, probability, deal_id))

    # Log activity
    cursor.execute("""
        INSERT INTO activities (account_id, activity_type, description, activity_date)
        VALUES (?, ?, ?, ?)
    """, (
        deal[1],  # account_id
        "Deal Updated",
        f"Deal moved to {new_stage} stage. {notes or ''}",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return {
        "deal_id": deal_id,
        "new_stage": new_stage,
        "probability": probability,
        "message": f"Deal moved to {new_stage}"
    }

@mcp.tool()
def get_pipeline_summary(
    date_range: str = "this_quarter"
) -> Dict:
    """
    Get pipeline analytics and summary

    Args:
        date_range: Time period (this_quarter, last_quarter, this_year)

    Returns:
        Pipeline summary with metrics by stage
    """
    conn = get_db()
    cursor = conn.cursor()

    # Pipeline by stage
    cursor.execute("""
        SELECT stage, COUNT(*) as count, SUM(amount) as total_value, AVG(probability) as avg_probability
        FROM deals
        WHERE stage NOT IN ('Closed Won', 'Closed Lost')
        GROUP BY stage
    """)

    pipeline_stages = []
    for row in cursor.fetchall():
        pipeline_stages.append({
            "stage": row[0],
            "deal_count": row[1],
            "total_value": row[2] or 0,
            "avg_probability": row[3] or 0,
            "weighted_value": (row[2] or 0) * (row[3] or 0) / 100
        })

    # Closed deals
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN stage = 'Closed Won' THEN 1 END) as won_count,
            COUNT(CASE WHEN stage = 'Closed Lost' THEN 1 END) as lost_count,
            SUM(CASE WHEN stage = 'Closed Won' THEN amount ELSE 0 END) as won_value
        FROM deals
        WHERE created_date >= date('now', '-90 days')
    """)

    closed = cursor.fetchone()

    # Top accounts by pipeline value
    cursor.execute("""
        SELECT a.name, COUNT(d.id) as deal_count, SUM(d.amount) as total_pipeline
        FROM accounts a
        JOIN deals d ON a.id = d.account_id
        WHERE d.stage NOT IN ('Closed Won', 'Closed Lost')
        GROUP BY a.id
        ORDER BY total_pipeline DESC
        LIMIT 5
    """)

    top_accounts = []
    for row in cursor.fetchall():
        top_accounts.append({
            "account": row[0],
            "deal_count": row[1],
            "pipeline_value": row[2]
        })

    conn.close()

    total_pipeline = sum(s["total_value"] for s in pipeline_stages)
    weighted_pipeline = sum(s["weighted_value"] for s in pipeline_stages)

    return {
        "pipeline_stages": pipeline_stages,
        "total_pipeline_value": total_pipeline,
        "weighted_pipeline_value": weighted_pipeline,
        "closed_won_count": closed[0] or 0,
        "closed_lost_count": closed[1] or 0,
        "closed_won_value": closed[2] or 0,
        "win_rate": (closed[0] / (closed[0] + closed[1]) * 100) if (closed[0] + closed[1]) > 0 else 0,
        "top_accounts": top_accounts
    }

@mcp.tool()
def list_all_accounts() -> List[Dict]:
    """
    List all accounts in the CRM

    Returns:
        List of all accounts with basic information
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.*, COUNT(d.id) as deal_count, SUM(d.amount) as total_deal_value
        FROM accounts a
        LEFT JOIN deals d ON a.id = d.account_id
        GROUP BY a.id
        ORDER BY a.annual_revenue DESC
    """)

    columns = ["id", "name", "industry", "annual_revenue", "employees", "website", "created_date", "deal_count", "total_deal_value"]
    results = []

    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    conn.close()
    return results

# Run the server
if __name__ == "__main__":
    print("🚀 Starting CRM MCP Server...")
    print("📍 Server: AI Sales CRM Server")
    print("💾 Database: data/sales_crm.db")
    print("🛠️  Tools available:")
    print("   - search_accounts(query, industry, min_revenue)")
    print("   - get_account_details(account_id)")
    print("   - create_deal(account_id, name, amount)")
    print("   - update_deal_stage(deal_id, new_stage)")
    print("   - get_pipeline_summary()")
    print("   - list_all_accounts()")
    print()
    print("Ready for MCP connections!")

    # Run the MCP server
    mcp.run()
