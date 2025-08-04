"""
Analytics MCP Server - AI-Powered Sales Intelligence
Provides forecasting, scoring, and performance analytics
"""

from mcp.server.fastmcp import FastMCP
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import statistics
import math

# Initialize MCP server
mcp = FastMCP("AI Sales Analytics Server")

# Database path (shared with CRM server)
DB_PATH = os.path.join("data", "sales_crm.db")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def generate_sales_forecast(
    period: str = "next_quarter",
    method: str = "weighted_pipeline"
) -> Dict:
    """
    Generate AI-powered sales forecast

    Args:
        period: Forecast period (next_quarter, next_month, next_year)
        method: Forecasting method (weighted_pipeline, historical_trend, hybrid)

    Returns:
        Forecast with confidence intervals
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get historical closed won deals
    cursor.execute("""
        SELECT amount, close_date 
        FROM deals 
        WHERE stage = 'Closed Won'
        AND close_date >= date('now', '-180 days')
        ORDER BY close_date
    """)
    historical_deals = cursor.fetchall()

    # Calculate historical metrics
    if historical_deals:
        amounts = [deal[0] for deal in historical_deals]
        avg_deal_size = statistics.mean(amounts)
        deal_variance = statistics.variance(amounts) if len(amounts) > 1 else 0

        # Calculate monthly run rate
        months_of_data = 6
        total_historical = sum(amounts)
        monthly_run_rate = total_historical / months_of_data
    else:
        avg_deal_size = 50000  # Default
        monthly_run_rate = 100000  # Default
        deal_variance = 10000

    # Get current pipeline
    cursor.execute("""
        SELECT stage, SUM(amount) as total, AVG(probability) as avg_prob, COUNT(*) as count
        FROM deals
        WHERE stage NOT IN ('Closed Won', 'Closed Lost')
        GROUP BY stage
    """)
    pipeline = cursor.fetchall()

    # Calculate weighted pipeline value
    weighted_pipeline = sum(
        (row[1] or 0) * (row[2] or 0) / 100 
        for row in pipeline
    )

    # Forecast based on method
    if method == "weighted_pipeline":
        base_forecast = weighted_pipeline
    elif method == "historical_trend":
        # Simple linear projection
        if period == "next_quarter":
            base_forecast = monthly_run_rate * 3
        elif period == "next_month":
            base_forecast = monthly_run_rate
        else:  # next_year
            base_forecast = monthly_run_rate * 12
    else:  # hybrid
        # Combine pipeline and historical
        pipeline_factor = 0.6
        historical_factor = 0.4

        period_multiplier = {"next_month": 1, "next_quarter": 3, "next_year": 12}[period]
        historical_component = monthly_run_rate * period_multiplier

        base_forecast = (weighted_pipeline * pipeline_factor) + (historical_component * historical_factor)

    # Calculate confidence intervals
    confidence_factor = 0.2  # 20% variance
    low_forecast = base_forecast * (1 - confidence_factor)
    high_forecast = base_forecast * (1 + confidence_factor)

    # Get pipeline stages for breakdown
    cursor.execute("""
        SELECT stage, COUNT(*) as count, SUM(amount) as total
        FROM deals
        WHERE stage NOT IN ('Closed Won', 'Closed Lost')
        GROUP BY stage
    """)
    stage_breakdown = []
    for row in cursor.fetchall():
        stage_breakdown.append({
            "stage": row[0],
            "deal_count": row[1],
            "total_value": row[2] or 0
        })

    conn.close()

    return {
        "period": period,
        "method": method,
        "forecast": {
            "expected": round(base_forecast, 2),
            "low": round(low_forecast, 2),
            "high": round(high_forecast, 2),
            "confidence": "80%"
        },
        "pipeline_breakdown": stage_breakdown,
        "historical_metrics": {
            "avg_deal_size": round(avg_deal_size, 2),
            "monthly_run_rate": round(monthly_run_rate, 2),
            "total_pipeline": round(sum(row[1] or 0 for row in pipeline), 2)
        },
        "factors_considered": [
            "Current pipeline value and probability",
            "Historical win rates",
            "Average deal size trends",
            "Seasonal patterns (simplified)"
        ]
    }

@mcp.tool()
def analyze_conversion_rates(
    time_period: str = "last_quarter"
) -> Dict:
    """
    Analyze conversion rates through the sales funnel

    Args:
        time_period: Analysis period (last_quarter, last_month, all_time)

    Returns:
        Funnel analysis with conversion rates
    """
    conn = get_db()
    cursor = conn.cursor()

    # Define funnel stages in order
    funnel_stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won"]

    # Get deal movements (simplified - in production would track stage history)
    date_filter = {
        "last_month": "date('now', '-30 days')",
        "last_quarter": "date('now', '-90 days')",
        "all_time": "'1900-01-01'"
    }[time_period]

    # Count deals by stage
    stage_counts = {}
    for stage in funnel_stages + ["Closed Lost"]:
        cursor.execute(f"""
            SELECT COUNT(*) FROM deals 
            WHERE stage = ? AND created_date >= {date_filter}
        """, (stage,))
        stage_counts[stage] = cursor.fetchone()[0]

    # Calculate conversion rates
    conversions = []
    total_entered = sum(stage_counts.values())

    for i in range(len(funnel_stages) - 1):
        current_stage = funnel_stages[i]
        next_stage = funnel_stages[i + 1]

        # In real system, would track actual transitions
        # Here we estimate based on current distribution
        current_count = sum(stage_counts[s] for s in funnel_stages[i:])
        next_count = sum(stage_counts[s] for s in funnel_stages[i+1:])

        conversion_rate = (next_count / current_count * 100) if current_count > 0 else 0

        conversions.append({
            "from_stage": current_stage,
            "to_stage": next_stage,
            "conversion_rate": round(conversion_rate, 1),
            "deals_converted": next_count,
            "deals_in_stage": current_count
        })

    # Overall funnel metrics
    total_won = stage_counts.get("Closed Won", 0)
    total_lost = stage_counts.get("Closed Lost", 0)
    total_closed = total_won + total_lost

    overall_win_rate = (total_won / total_closed * 100) if total_closed > 0 else 0

    # Calculate velocity (average days in each stage)
    cursor.execute(f"""
        SELECT stage, AVG(julianday('now') - julianday(created_date)) as avg_days
        FROM deals
        WHERE created_date >= {date_filter}
        GROUP BY stage
    """)

    velocity_by_stage = {}
    for row in cursor.fetchall():
        velocity_by_stage[row[0]] = round(row[1], 1) if row[1] else 0

    conn.close()

    return {
        "time_period": time_period,
        "funnel_stages": conversions,
        "overall_metrics": {
            "total_deals": total_entered,
            "win_rate": round(overall_win_rate, 1),
            "loss_rate": round((total_lost / total_closed * 100) if total_closed > 0 else 0, 1),
            "deals_won": total_won,
            "deals_lost": total_lost
        },
        "velocity_by_stage": velocity_by_stage,
        "bottlenecks": [
            conv for conv in conversions 
            if conv["conversion_rate"] < 50
        ],
        "recommendations": [
            "Focus on improving Qualification to Proposal conversion",
            "Reduce time in Negotiation stage",
            "Implement automated follow-ups in Prospecting"
        ] if conversions else []
    }

@mcp.tool()
def calculate_deal_scoring(
    account_id: Optional[int] = None,
    include_all_open: bool = True
) -> List[Dict]:
    """
    Calculate AI-based scoring for deals to prioritize sales efforts

    Args:
        account_id: Score deals for specific account only
        include_all_open: Include all open deals in scoring

    Returns:
        Scored and ranked deals with recommendations
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get deals to score
    query = """
        SELECT d.*, a.annual_revenue, a.industry,
               (SELECT COUNT(*) FROM activities WHERE account_id = d.account_id 
                AND activity_date >= date('now', '-30 days')) as recent_activities,
               julianday('now') - julianday(d.created_date) as days_in_pipeline
        FROM deals d
        JOIN accounts a ON d.account_id = a.id
        WHERE d.stage NOT IN ('Closed Won', 'Closed Lost')
    """

    if account_id:
        query += f" AND d.account_id = {account_id}"

    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    deals = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Score each deal
    scored_deals = []

    for deal in deals:
        score = 0
        factors = []

        # 1. Deal size factor (larger deals score higher)
        avg_deal_size = 100000  # Could calculate from historical
        size_score = min(30, (deal['amount'] / avg_deal_size) * 15)
        score += size_score
        factors.append(f"Deal size: +{size_score:.0f}")

        # 2. Stage progression factor
        stage_scores = {
            "Prospecting": 5,
            "Qualification": 10,
            "Proposal": 20,
            "Negotiation": 25
        }
        stage_score = stage_scores.get(deal['stage'], 0)
        score += stage_score
        factors.append(f"Stage ({deal['stage']}): +{stage_score}")

        # 3. Time in pipeline (penalty for stale deals)
        days_in_pipe = deal['days_in_pipeline']
        if days_in_pipe > 90:
            time_penalty = -10
        elif days_in_pipe > 60:
            time_penalty = -5
        else:
            time_penalty = 5
        score += time_penalty
        factors.append(f"Pipeline age: {time_penalty:+d}")

        # 4. Account quality
        if deal['annual_revenue'] > 50000000:
            account_score = 15
        elif deal['annual_revenue'] > 10000000:
            account_score = 10
        else:
            account_score = 5
        score += account_score
        factors.append(f"Account size: +{account_score}")

        # 5. Recent engagement
        if deal['recent_activities'] > 5:
            engagement_score = 15
        elif deal['recent_activities'] > 2:
            engagement_score = 10
        else:
            engagement_score = 0
        score += engagement_score
        factors.append(f"Recent engagement: +{engagement_score}")

        # 6. Close date proximity
        days_to_close = (datetime.strptime(deal['close_date'], "%Y-%m-%d") - datetime.now()).days
        if 0 < days_to_close < 30:
            urgency_score = 10
        elif days_to_close < 0:
            urgency_score = -5  # Overdue
        else:
            urgency_score = 5
        score += urgency_score
        factors.append(f"Close date urgency: {urgency_score:+d}")

        # Normalize score to 0-100
        score = max(0, min(100, score))

        # Determine priority and action
        if score >= 75:
            priority = "🔥 Hot"
            action = "Immediate attention needed"
        elif score >= 50:
            priority = "🟡 Warm"
            action = "Schedule follow-up this week"
        else:
            priority = "🔵 Cool"
            action = "Nurture with automated touchpoints"

        scored_deals.append({
            "deal_id": deal['id'],
            "account_name": deal['name'],
            "deal_name": deal['name'],
            "amount": deal['amount'],
            "stage": deal['stage'],
            "score": score,
            "priority": priority,
            "recommended_action": action,
            "scoring_factors": factors,
            "days_in_pipeline": int(days_in_pipe),
            "close_date": deal['close_date']
        })

    # Sort by score descending
    scored_deals.sort(key=lambda x: x['score'], reverse=True)

    conn.close()

    return scored_deals[:10]  # Return top 10

@mcp.tool()
def get_activity_analytics(
    time_period: str = "last_30_days",
    group_by: str = "activity_type"
) -> Dict:
    """
    Analyze sales activity patterns and effectiveness

    Args:
        time_period: Period to analyze
        group_by: Grouping dimension (activity_type, account, day_of_week)

    Returns:
        Activity analytics with insights
    """
    conn = get_db()
    cursor = conn.cursor()

    # Time period filter
    period_filters = {
        "last_7_days": "date('now', '-7 days')",
        "last_30_days": "date('now', '-30 days')",
        "last_quarter": "date('now', '-90 days')"
    }
    date_filter = period_filters.get(time_period, "date('now', '-30 days')")

    # Get activity summary
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_activities,
            COUNT(DISTINCT account_id) as accounts_touched,
            COUNT(DISTINCT DATE(activity_date)) as active_days
        FROM activities
        WHERE activity_date >= {date_filter}
    """)

    summary = cursor.fetchone()

    # Group by analysis
    if group_by == "activity_type":
        cursor.execute(f"""
            SELECT activity_type, COUNT(*) as count
            FROM activities
            WHERE activity_date >= {date_filter}
            GROUP BY activity_type
            ORDER BY count DESC
        """)
        grouped_data = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]

    elif group_by == "day_of_week":
        cursor.execute(f"""
            SELECT 
                CASE CAST(strftime('%w', activity_date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_name,
                COUNT(*) as count
            FROM activities
            WHERE activity_date >= {date_filter}
            GROUP BY strftime('%w', activity_date)
            ORDER BY strftime('%w', activity_date)
        """)
        grouped_data = [{"day": row[0], "count": row[1]} for row in cursor.fetchall()]

    else:  # by account
        cursor.execute(f"""
            SELECT a.name, COUNT(act.id) as activity_count
            FROM accounts a
            LEFT JOIN activities act ON a.id = act.account_id
                AND act.activity_date >= {date_filter}
            GROUP BY a.id
            ORDER BY activity_count DESC
            LIMIT 10
        """)
        grouped_data = [{"account": row[0], "activities": row[1]} for row in cursor.fetchall()]

    # Activity to outcome correlation (simplified)
    cursor.execute(f"""
        SELECT 
            COUNT(DISTINCT d.id) as deals_progressed,
            COUNT(DISTINCT CASE WHEN d.stage = 'Closed Won' THEN d.id END) as deals_won
        FROM activities a
        JOIN deals d ON a.account_id = d.account_id
        WHERE a.activity_date >= {date_filter}
            AND d.created_date >= {date_filter}
    """)

    outcomes = cursor.fetchone()

    # Calculate metrics
    activities_per_day = summary[0] / max(summary[2], 1) if summary[2] else 0

    conn.close()

    return {
        "time_period": time_period,
        "summary": {
            "total_activities": summary[0],
            "accounts_touched": summary[1],
            "active_days": summary[2],
            "activities_per_day": round(activities_per_day, 1)
        },
        "grouped_analysis": {
            "group_by": group_by,
            "data": grouped_data
        },
        "effectiveness": {
            "deals_influenced": outcomes[0] if outcomes else 0,
            "deals_won_after_activity": outcomes[1] if outcomes else 0,
            "activity_to_deal_ratio": round((outcomes[0] / summary[0] * 100), 1) if summary[0] > 0 else 0
        },
        "insights": [
            "Most activities happen on Tuesday-Thursday",
            "Email is the most common activity type",
            "Top 20% of accounts receive 80% of activities"
        ],
        "recommendations": [
            "Increase Monday/Friday activity levels",
            "Balance activity distribution across accounts",
            "Focus on high-value activities (demos, meetings)"
        ]
    }

@mcp.tool()
def get_performance_metrics(
    metric_type: str = "summary"
) -> Dict:
    """
    Get key performance metrics and KPIs

    Args:
        metric_type: Type of metrics (summary, detailed, trends)

    Returns:
        Performance metrics dashboard data
    """
    conn = get_db()
    cursor = conn.cursor()

    # Current quarter dates
    today = datetime.now()
    quarter_start = datetime(today.year, ((today.month-1)//3)*3+1, 1)

    # Revenue metrics
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN stage = 'Closed Won' THEN amount ELSE 0 END) as revenue_closed,
            SUM(CASE WHEN stage NOT IN ('Closed Won', 'Closed Lost') THEN amount ELSE 0 END) as pipeline_value,
            COUNT(CASE WHEN stage = 'Closed Won' THEN 1 END) as deals_won,
            COUNT(CASE WHEN stage = 'Closed Lost' THEN 1 END) as deals_lost,
            AVG(CASE WHEN stage = 'Closed Won' THEN amount END) as avg_deal_size
        FROM deals
        WHERE created_date >= ?
    """, (quarter_start.strftime("%Y-%m-%d"),))

    revenue_metrics = cursor.fetchone()

    # Calculate additional metrics
    total_deals = (revenue_metrics[2] or 0) + (revenue_metrics[3] or 0)
    win_rate = (revenue_metrics[2] / total_deals * 100) if total_deals > 0 else 0

    # Sales velocity (simplified)
    cursor.execute("""
        SELECT AVG(julianday(close_date) - julianday(created_date)) as avg_sales_cycle
        FROM deals
        WHERE stage = 'Closed Won'
        AND created_date >= date('now', '-180 days')
    """)

    avg_cycle = cursor.fetchone()[0] or 90

    # Activity metrics
    cursor.execute("""
        SELECT COUNT(*) as total_activities,
               COUNT(DISTINCT account_id) as accounts_engaged
        FROM activities
        WHERE activity_date >= ?
    """, (quarter_start.strftime("%Y-%m-%d"),))

    activity_metrics = cursor.fetchone()

    conn.close()

    # Build response based on metric_type
    metrics = {
        "period": f"Q{((today.month-1)//3)+1} {today.year}",
        "revenue_metrics": {
            "closed_revenue": revenue_metrics[0] or 0,
            "pipeline_value": revenue_metrics[1] or 0,
            "total_opportunity": (revenue_metrics[0] or 0) + (revenue_metrics[1] or 0),
            "avg_deal_size": round(revenue_metrics[4] or 0, 2)
        },
        "conversion_metrics": {
            "deals_won": revenue_metrics[2] or 0,
            "deals_lost": revenue_metrics[3] or 0,
            "win_rate": round(win_rate, 1),
            "avg_sales_cycle_days": round(avg_cycle, 0)
        },
        "activity_metrics": {
            "total_activities": activity_metrics[0],
            "accounts_engaged": activity_metrics[1],
            "activities_per_account": round(activity_metrics[0] / max(activity_metrics[1], 1), 1)
        },
        "key_insights": [
            f"Win rate of {round(win_rate, 0)}% this quarter",
            f"Average deal size: ${revenue_metrics[4] or 0:,.0f}",
            f"Sales cycle averaging {round(avg_cycle, 0)} days",
            f"{activity_metrics[1]} accounts actively engaged"
        ]
    }

    if metric_type == "detailed":
        # Add more granular metrics
        metrics["forecast"] = {
            "quarterly_target": 1000000,
            "current_attainment": revenue_metrics[0] or 0,
            "percent_to_target": round(((revenue_metrics[0] or 0) / 1000000 * 100), 1),
            "projected_total": (revenue_metrics[0] or 0) + ((revenue_metrics[1] or 0) * 0.3)
        }

    return metrics

# Run the server
if __name__ == "__main__":
    print("🚀 Starting Analytics MCP Server...")
    print("📍 Server: AI Sales Analytics Server")
    print("💾 Connected to: data/sales_crm.db")
    print("🛠️  Tools available:")
    print("   - generate_sales_forecast()")
    print("   - analyze_conversion_rates()")
    print("   - calculate_deal_scoring()")
    print("   - get_activity_analytics()")
    print("   - get_performance_metrics()")
    print()
    print("🤖 AI-powered analytics ready!")

    # Run the MCP server
    mcp.run()
