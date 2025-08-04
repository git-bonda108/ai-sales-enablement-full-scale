"""
AI Sales Intelligence Platform
Professional Streamlit UI
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Page config
st.set_page_config(
    page_title="AI Sales Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Headers */
    .dashboard-header {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 10px;
    }

    .section-header {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Metrics */
    .big-metric {
        font-size: 36px;
        font-weight: 700;
        color: #10b981;
    }

    .metric-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
    }

    /* Status badges */
    .hot-badge {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    .warm-badge {
        background-color: #f59e0b;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Insights box */
    .insight-box {
        background: #e0f2fe;
        border-left: 4px solid #0ea5e9;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }

    /* Success message */
    .success-box {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE = "http://localhost:8000"

# Session state initialization
if 'selected_account' not in st.session_state:
    st.session_state.selected_account = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'dashboard'

# Helper functions
@st.cache_data(ttl=30)
def fetch_dashboard_data():
    """Fetch dashboard data from API"""
    try:
        response = requests.get(f"{API_BASE}/api/analytics/dashboard")
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=30)
def fetch_accounts():
    """Fetch accounts from API"""
    try:
        response = requests.get(f"{API_BASE}/api/accounts")
        return response.json()['accounts'] if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=30)
def fetch_hot_deals():
    """Fetch hot deals from API"""
    try:
        response = requests.get(f"{API_BASE}/api/analytics/hot-deals")
        return response.json()['deals'] if response.status_code == 200 else []
    except:
        return []

# Sidebar
with st.sidebar:
    st.markdown("## 🚀 AI Sales Platform")
    st.markdown("---")

    # Navigation
    menu_items = {
        'dashboard': '📊 Dashboard',
        'accounts': '🏢 Accounts',
        'deals': '💼 Deals',
        'insights': '🧠 AI Insights',
        'forecast': '📈 Forecasting'
    }

    for key, label in menu_items.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.view_mode = key

    st.markdown("---")

    # Quick stats
    st.markdown("### Quick Stats")
    dashboard_data = fetch_dashboard_data()
    if dashboard_data:
        st.metric("Total Pipeline", f"${dashboard_data['pipeline']['total_pipeline_value']:,.0f}")
        st.metric("Win Rate", f"{dashboard_data['metrics']['conversion_metrics']['win_rate']}%")
        st.metric("Avg Deal Size", f"${dashboard_data['metrics']['revenue_metrics']['avg_deal_size']:,.0f}")

    st.markdown("---")
    st.markdown("### System Status")
    st.success("✅ All systems operational")
    st.info("🤖 AI models active")

# Main content area
if st.session_state.view_mode == 'dashboard':
    # Dashboard View
    st.markdown('<h1 class="dashboard-header">AI Sales Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Real-time insights powered by AI")

    # Fetch data
    dashboard_data = fetch_dashboard_data()
    hot_deals = fetch_hot_deals()

    if dashboard_data:
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Q1 Revenue Closed</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-metric">${dashboard_data["metrics"]["revenue_metrics"]["closed_revenue"]:,.0f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Pipeline Value</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-metric">${dashboard_data["pipeline"]["total_pipeline_value"]:,.0f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">AI Forecast (Next Q)</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-metric">${dashboard_data["forecast"]["forecast"]["expected"]:,.0f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Win Rate</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-metric">{dashboard_data["metrics"]["conversion_metrics"]["win_rate"]}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Charts row
        st.markdown('<h2 class="section-header">📊 Pipeline Analytics</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # Pipeline by stage chart
            if dashboard_data['pipeline']['pipeline_stages']:
                stages_df = pd.DataFrame(dashboard_data['pipeline']['pipeline_stages'])
                fig = px.bar(stages_df, x='stage', y='total_value', 
                            title='Pipeline by Stage',
                            color='total_value',
                            color_continuous_scale='Blues')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Forecast confidence chart
            forecast = dashboard_data['forecast']['forecast']
            fig = go.Figure()

            # Add forecast range
            fig.add_trace(go.Bar(
                x=['Low', 'Expected', 'High'],
                y=[forecast['low'], forecast['expected'], forecast['high']],
                marker_color=['lightblue', 'blue', 'darkblue'],
                text=[f"${v:,.0f}" for v in [forecast['low'], forecast['expected'], forecast['high']]],
                textposition='auto'
            ))

            fig.update_layout(
                title='Q2 Revenue Forecast (AI)',
                yaxis_title='Revenue ($)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # Hot deals section
        st.markdown('<h2 class="section-header">🔥 AI-Prioritized Hot Deals</h2>', unsafe_allow_html=True)

        if hot_deals:
            for deal in hot_deals[:3]:  # Show top 3
                col1, col2, col3, col4 = st.columns([3, 2, 1, 2])

                with col1:
                    st.markdown(f"**{deal['account_name']}** - ${deal['amount']:,.0f}")

                with col2:
                    if "🔥" in deal['priority']:
                        st.markdown('<span class="hot-badge">HOT</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="warm-badge">WARM</span>', unsafe_allow_html=True)

                with col3:
                    st.markdown(f"Score: **{deal['score']}/100**")

                with col4:
                    st.markdown(f"_{deal['recommended_action']}_")

        # AI Insights
        st.markdown('<h2 class="section-header">🧠 AI Insights</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("**🎯 Conversion Optimization**")
            st.markdown("AI detected 15% drop in Qualification → Proposal conversion. Recommend sales training on value proposition.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("**📈 Revenue Opportunity**")
            st.markdown("3 deals totaling $450K show high engagement but slow progress. AI recommends executive involvement.")
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == 'accounts':
    # Accounts View
    st.markdown('<h1 class="dashboard-header">Account Management</h1>', unsafe_allow_html=True)

    accounts = fetch_accounts()

    if accounts:
        # Search and filters
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search accounts", placeholder="Type to search...")
        with col2:
            industry_filter = st.selectbox("Industry", ["All", "Technology", "Healthcare", "Finance", "Manufacturing"])

        # Accounts table
        accounts_df = pd.DataFrame(accounts)

        if search:
            accounts_df = accounts_df[accounts_df['name'].str.contains(search, case=False)]

        if industry_filter != "All":
            accounts_df = accounts_df[accounts_df['industry'] == industry_filter]

        st.dataframe(
            accounts_df[['name', 'industry', 'annual_revenue']],
            column_config={
                "name": "Account Name",
                "industry": "Industry",
                "annual_revenue": st.column_config.NumberColumn("Annual Revenue", format="$%d")
            },
            use_container_width=True,
            hide_index=True
        )

        # Quick actions
        st.markdown("### Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("➕ Create New Deal", use_container_width=True):
                st.session_state.view_mode = 'deals'

        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.view_mode = 'insights'

        with col3:
            if st.button("📧 Bulk Email Campaign", use_container_width=True):
                st.info("Campaign wizard would open here")

elif st.session_state.view_mode == 'deals':
    # Deals Management
    st.markdown('<h1 class="dashboard-header">Deal Management</h1>', unsafe_allow_html=True)

    # Create new deal form
    with st.expander("➕ Create New Deal", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            account_id = st.number_input("Account ID", min_value=1, value=1)
            deal_name = st.text_input("Deal Name", placeholder="Q1 Enterprise License")
            amount = st.number_input("Deal Amount ($)", min_value=0, value=100000, step=1000)

        with col2:
            stage = st.selectbox("Stage", ["Prospecting", "Qualification", "Proposal", "Negotiation"])
            close_date = st.date_input("Expected Close Date", datetime.now() + timedelta(days=90))

        if st.button("🚀 Create Deal with AI Scoring", type="primary"):
            # Mock API call
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("✅ **Deal created successfully!**")
            st.markdown(f"AI Score: **85/100** 🔥")
            st.markdown("Priority: **Hot Deal**")
            st.markdown("Recommended Action: Schedule demo within 3 days")
            st.markdown('</div>', unsafe_allow_html=True)

    # Existing deals
    hot_deals = fetch_hot_deals()
    if hot_deals:
        st.markdown("### 📋 Active Deals (AI-Scored)")

        deals_df = pd.DataFrame(hot_deals)
        st.dataframe(
            deals_df[['account_name', 'amount', 'score', 'priority', 'recommended_action']],
            column_config={
                "account_name": "Account",
                "amount": st.column_config.NumberColumn("Amount", format="$%d"),
                "score": st.column_config.ProgressColumn("AI Score", min_value=0, max_value=100),
                "priority": "Priority",
                "recommended_action": "AI Recommendation"
            },
            use_container_width=True,
            hide_index=True
        )

elif st.session_state.view_mode == 'insights':
    # AI Insights View
    st.markdown('<h1 class="dashboard-header">AI-Powered Sales Insights</h1>', unsafe_allow_html=True)

    # Conversion funnel
    st.markdown('<h2 class="section-header">🔄 Conversion Funnel Analysis</h2>', unsafe_allow_html=True)

    # Create funnel chart
    stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won']
    values = [100, 65, 40, 25, 15]  # Example conversion rates

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#3b82f6", "#60a5fa", "#93bbfd", "#c3d9fe", "#e0ecff"]}
    ))

    fig.update_layout(title="Sales Funnel Conversion Rates", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # AI recommendations
    st.markdown('<h2 class="section-header">🎯 AI Recommendations</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Revenue Acceleration")
        recommendations = [
            "Focus on 3 deals in Negotiation stage - 85% close probability",
            "Schedule follow-ups for 5 stalled Qualification deals",
            "Engage decision makers at TechCorp and GlobalSoft"
        ]
        for rec in recommendations:
            st.markdown(f"• {rec}")

    with col2:
        st.markdown("### ⚡ Process Optimization")
        optimizations = [
            "Reduce Proposal creation time by using templates",
            "Automate follow-up emails for Prospecting stage",
            "Implement qualification scorecard for faster decisions"
        ]
        for opt in optimizations:
            st.markdown(f"• {opt}")

    # Activity effectiveness
    st.markdown('<h2 class="section-header">📊 Activity Effectiveness</h2>', unsafe_allow_html=True)

    # Create activity chart
    activities_df = pd.DataFrame({
        'Activity Type': ['Email', 'Call', 'Meeting', 'Demo', 'Proposal'],
        'Count': [245, 123, 45, 23, 18],
        'Conversion Rate': [5, 12, 35, 65, 78]
    })

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Activity Volume', 'Conversion Rate by Activity')
    )

    fig.add_trace(
        go.Bar(x=activities_df['Activity Type'], y=activities_df['Count'], name='Count'),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=activities_df['Activity Type'], y=activities_df['Conversion Rate'], 
               name='Conversion %', marker_color='green'),
        row=1, col=2
    )

    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.view_mode == 'forecast':
    # Forecasting View
    st.markdown('<h1 class="dashboard-header">AI Sales Forecasting</h1>', unsafe_allow_html=True)

    # Forecast controls
    col1, col2, col3 = st.columns(3)

    with col1:
        period = st.selectbox("Forecast Period", ["Next Month", "Next Quarter", "Next Year"])

    with col2:
        method = st.selectbox("AI Method", ["Weighted Pipeline", "Historical Trend", "Hybrid AI"])

    with col3:
        confidence = st.selectbox("Confidence Level", ["80%", "90%", "95%"])

    # Generate forecast button
    if st.button("🤖 Generate AI Forecast", type="primary"):
        # Mock forecast data
        st.markdown('<h2 class="section-header">📈 Forecast Results</h2>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Low Estimate", "$680,000", "-20%")

        with col2:
            st.metric("Expected Revenue", "$850,000", "+15%", delta_color="normal")

        with col3:
            st.metric("High Estimate", "$1,020,000", "+20%")

        # Time series forecast chart
        dates = pd.date_range(start=datetime.now(), periods=12, freq='M')
        historical = [450000, 480000, 520000, 550000, 600000, 650000]
        forecast_expected = [680000, 720000, 780000, 850000, 900000, 950000]
        forecast_low = [x * 0.8 for x in forecast_expected]
        forecast_high = [x * 1.2 for x in forecast_expected]

        fig = go.Figure()

        # Historical data
        fig.add_trace(go.Scatter(
            x=dates[:6], y=historical,
            mode='lines+markers',
            name='Historical',
            line=dict(color='blue', width=2)
        ))

        # Forecast
        fig.add_trace(go.Scatter(
            x=dates[5:], y=forecast_expected,
            mode='lines+markers',
            name='AI Forecast',
            line=dict(color='green', width=2, dash='dash')
        ))

        # Confidence bands
        fig.add_trace(go.Scatter(
            x=dates[5:], y=forecast_high,
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0)',
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=dates[5:], y=forecast_low,
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0)',
            name='Confidence Band'
        ))

        fig.update_layout(
            title='12-Month Revenue Forecast',
            xaxis_title='Month',
            yaxis_title='Revenue ($)',
            hovermode='x'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Factors
        st.markdown('<h3 class="section-header">📊 AI Factors Considered</h3>', unsafe_allow_html=True)

        factors = {
            "Current Pipeline": "85%",
            "Historical Patterns": "92%",
            "Seasonality": "78%",
            "Market Conditions": "81%",
            "Deal Velocity": "88%"
        }

        cols = st.columns(len(factors))
        for col, (factor, weight) in zip(cols, factors.items()):
            with col:
                st.metric(factor, weight)

# Footer
st.markdown("---")
st.markdown("🚀 **AI Sales Intelligence Platform** | MCP Demo | Built with ❤️ using Streamlit")
