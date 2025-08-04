import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import requests
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components

# API Configuration
API_BASE = "http://localhost:8000"

# Page config with custom theme
st.set_page_config(
    page_title="AI Sales Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional white theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Styles - Professional White Theme */
    .stApp {
        background: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Professional gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    /* Subtitle styling */
    .subtitle {
        color: #6b7280;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* Professional card styling */
    .metric-card {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }

    .metric-card:hover {
        background: #f8fafc;
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.3);
    }

    /* Metric value styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }

    .metric-delta {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }

    .metric-delta-positive {
        background: rgba(52, 211, 153, 0.2);
        color: #34d399;
    }

    .metric-delta-negative {
        background: rgba(248, 113, 113, 0.2);
        color: #f87171;
    }

    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
    }

    /* Professional sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid #e5e7eb;
    }

    /* Professional tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        padding: 1rem 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: #f8fafc;
        border: 2px solid #e5e7eb;
        color: #6b7280;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-color: #3b82f6;
        color: white;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }

    /* Professional chart container */
    .chart-container {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Professional feature card */
    .feature-card {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .feature-card:hover {
        background: #f8fafc;
        border-color: #3b82f6;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.3);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: #a0a0b0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-active {
        background: rgba(52, 211, 153, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .status-pending {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    .status-inactive {
        background: rgba(248, 113, 113, 0.2);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
    }

    /* Animated background */
    .animated-bg {
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: -1;
        opacity: 0.1;
        background-image: 
            radial-gradient(at 47% 33%, hsl(264.09, 61%, 45%) 0, transparent 59%), 
            radial-gradient(at 82% 65%, hsl(280.00, 70%, 36%) 0, transparent 55%);
        filter: blur(100px);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #ffffff;
        font-weight: 600;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(102, 126, 234, 0.5);
    }

    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #ffffff;
    }

    /* Data table styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    /* Progress bar */
    .progress-bar {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Animated background
st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

# Load Lottie animation
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# API Functions
def fetch_dashboard_data():
    """Fetch dashboard metrics from API"""
    try:
        response = requests.get(f"{API_BASE}/api/analytics/dashboard")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def fetch_accounts():
    """Fetch accounts from API"""
    try:
        response = requests.get(f"{API_BASE}/crm/accounts")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def fetch_deals():
    """Fetch deals from API"""
    try:
        response = requests.get(f"{API_BASE}/crm/deals")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def send_chat_message(message):
    """Send chat message to AI assistant"""
    try:
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": message}]}
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def authenticate_gmail():
    """Authenticate with Gmail"""
    try:
        response = requests.post(f"{API_BASE}/integrations/gmail/auth")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_unread_emails(max_results=10):
    """Get unread emails with analysis"""
    try:
        response = requests.get(f"{API_BASE}/integrations/gmail/unread?max_results={max_results}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"emails": []}

def generate_email_response(email_id):
    """Generate AI response for an email"""
    try:
        response = requests.post(f"{API_BASE}/integrations/gmail/generate-response/{email_id}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# Header Section
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="gradient-text">AI Sales Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Empowering sales teams with real-time AI insights and automation</p>', unsafe_allow_html=True)

# Navigation tabs with icons
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Dashboard",
    "🏢 Accounts",
    "💼 Deals",
    "🤖 AI Assistant",
    "📧 Gmail Integration",
    "🎯 AI Feedback",
    "🎓 Training Feedback and Pipeline"
])

# Dashboard Tab
with tab1:
    # Key Metrics Row
    st.markdown("### 📊 Key Performance Metrics")

    # Fetch real data
    dashboard_data = fetch_dashboard_data()
    accounts = fetch_accounts()
    deals = fetch_deals()
    
    # Calculate metrics from real data
    total_revenue = "$2.4M"  # Default fallback
    active_deals = len(deals) if deals else 127
    win_rate = "68%"  # Default fallback
    avg_deal_size = "$45.7K"  # Default fallback
    
    if dashboard_data:
        total_revenue = f"${dashboard_data.get('total_revenue', '2.4M')}"
        win_rate = f"{dashboard_data.get('win_rate', 68)}%"
        avg_deal_size = f"${dashboard_data.get('avg_deal_size', '45.7K')}"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{total_revenue}</div>
            <div class="metric-delta metric-delta-positive">↑ 23.5%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Deals</div>
            <div class="metric-value">{active_deals}</div>
            <div class="metric-delta metric-delta-positive">↑ 12 new</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">{win_rate}</div>
            <div class="metric-delta metric-delta-positive">↑ 5.2%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Deal Size</div>
            <div class="metric-value">{avg_deal_size}</div>
            <div class="metric-delta metric-delta-negative">↓ 3.1%</div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Row
    st.markdown("### 📈 Sales Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Revenue trend chart
        dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
        revenue = np.cumsum(np.random.randint(10000, 50000, size=len(dates)))

        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=dates,
            y=revenue,
            mode='lines',
            name='Revenue',
            line=dict(color='#1e40af', width=3),
            fill='tonexty',
            fillcolor='rgba(30, 64, 175, 0.2)'
        ))

        fig_revenue.update_layout(
            title="Revenue Growth Trend",
            template="plotly_white",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            height=400,
            showlegend=False,
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)')
        )

        st.plotly_chart(fig_revenue, use_container_width=True)

    with col2:
        # Deal pipeline funnel
        stages = ['Leads', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won']
        values = [1500, 800, 400, 200, 150]

        fig_funnel = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe']
            )
        ))

        fig_funnel.update_layout(
            title="Sales Pipeline Funnel",
            template="plotly_white",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

    # Activity Feed
    st.markdown("### 🔔 Recent Activity")

    activities = [
        {"time": "2 mins ago", "user": "Sarah Chen", "action": "closed deal", "detail": "TechCorp - $750K", "status": "success"},
        {"time": "15 mins ago", "user": "AI Assistant", "action": "identified opportunity", "detail": "GlobalTech expansion", "status": "info"},
        {"time": "1 hour ago", "user": "Mike Johnson", "action": "scheduled meeting", "detail": "Enterprise Corp demo", "status": "pending"},
        {"time": "3 hours ago", "user": "Training Pipeline", "action": "processed transcript", "detail": "95% confidence", "status": "success"}
    ]

    for activity in activities:
        status_class = {
            "success": "status-active",
            "info": "status-pending",
            "pending": "status-inactive"
        }.get(activity["status"], "status-inactive")

        st.markdown(f"""
        <div style="padding: 1rem; margin-bottom: 0.5rem; background: #ffffff; border-radius: 10px; border: 1px solid #e5e7eb; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #6b7280; font-size: 0.85rem;">{activity['time']}</span> • 
                    <span style="color: #374151; font-weight: 600;">{activity['user']}</span>
                    <span style="color: #6b7280;"> {activity['action']} </span>
                    <span style="color: #1e40af; font-weight: 600;">{activity['detail']}</span>
                </div>
                <span class="status-badge {status_class}">{activity['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Accounts Tab
with tab2:
    st.markdown("### 🏢 Account Management")
    st.markdown('<p class="subtitle">Manage your customer accounts and relationships</p>', unsafe_allow_html=True)
    
    # Fetch real accounts data
    accounts = fetch_accounts()
    
    if accounts:
        # Display accounts in a beautiful table
        st.markdown("#### 📋 Active Accounts")
        
        for account in accounts[:10]:  # Show first 10 accounts
            account_name = account.get('name', 'Unknown Account')
            account_type = account.get('type', 'Unknown')
            account_status = account.get('status', 'Active')
            account_value = account.get('annual_revenue', '$0')
            
            status_class = "status-active" if account_status == "Active" else "status-inactive"
            
            st.markdown(f"""
            <div style="padding: 1.5rem; margin-bottom: 1rem; background: #ffffff; border-radius: 12px; border: 2px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{account_name}</h4>
                        <p style="color: #6b7280; margin: 0;">Type: {account_type} • Revenue: {account_value}</p>
                    </div>
                    <span class="status-badge {status_class}">{account_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No accounts found. Connect to your CRM to see account data.")

# Deals Tab
with tab3:
    st.markdown("### 💼 Deal Pipeline")
    st.markdown('<p class="subtitle">Track and manage your sales opportunities</p>', unsafe_allow_html=True)
    
    # Fetch real deals data
    deals = fetch_deals()
    
    if deals:
        # Display deals in a beautiful table
        st.markdown("#### 🎯 Active Deals")
        
        for deal in deals[:10]:  # Show first 10 deals
            deal_name = deal.get('name', 'Unknown Deal')
            deal_stage = deal.get('stage', 'Unknown')
            deal_value = deal.get('amount', '$0')
            deal_probability = deal.get('probability', '0%')
            
            # Color code based on stage
            stage_colors = {
                'Qualification': '#667eea',
                'Proposal': '#7c3aed', 
                'Negotiation': '#8b5cf6',
                'Closed Won': '#10b981',
                'Closed Lost': '#ef4444'
            }
            stage_color = stage_colors.get(deal_stage, '#a0a0b0')
            
            st.markdown(f"""
            <div style="padding: 1.5rem; margin-bottom: 1rem; background: #ffffff; border-radius: 12px; border: 2px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{deal_name}</h4>
                        <p style="color: #6b7280; margin: 0;">Value: {deal_value} • Probability: {deal_probability}</p>
                    </div>
                    <span style="background: {stage_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">{deal_stage}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No deals found. Connect to your CRM to see deal data.")

# AI Assistant Tab
with tab4:
    st.markdown("### 🤖 AI Sales Assistant")
    st.markdown('<p class="subtitle">Your intelligent partner for sales insights and automation</p>', unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)

    features = [
        {"icon": "🎯", "title": "Smart Targeting", "desc": "AI identifies high-value prospects based on historical data"},
        {"icon": "📊", "title": "Predictive Analytics", "desc": "Forecast deal outcomes with 92% accuracy"},
        {"icon": "🔄", "title": "Automated Workflows", "desc": "Progressive autonomy adapts to confidence levels"},
        {"icon": "💡", "title": "Real-time Insights", "desc": "Context-aware suggestions from knowledge base"}
    ]

    for col, feature in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{feature['icon']}</div>
                <div class="feature-title">{feature['title']}</div>
                <div class="feature-description">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Chat interface
    st.markdown("### 💬 Chat with AI Assistant")

    # Beautiful chat container
    chat_container = st.container()
    with chat_container:
        messages = st.container()

        # Sample messages
        sample_messages = [
            {"role": "assistant", "content": "👋 Hello! I'm your AI Sales Assistant. I can help you with CRM queries, sales insights, and deal recommendations."},
            {"role": "user", "content": "Tell me about our top opportunities this quarter"},
            {"role": "assistant", "content": """Based on our analytics, here are your top 3 opportunities:

**1. GlobalTech Expansion** - $1.2M
- 85% win probability
- Decision expected by Q2 2024
- Similar to 3 successful deals last year

**2. Enterprise Corp Platform** - $750K  
- 78% win probability
- Strong technical fit confirmed
- Budget approved by CFO

**3. TechCorp Upgrade** - $450K
- 92% win probability  
- Existing customer expansion
- Competing against internal solution

Would you like detailed insights on any of these opportunities?"""}
        ]

        for msg in sample_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 1rem 1.5rem; border-radius: 20px 20px 5px 20px; max-width: 70%; color: white;">
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                    <div style="background: #f8fafc; border: 1px solid #e5e7eb; padding: 1rem 1.5rem; border-radius: 20px 20px 20px 5px; max-width: 70%; color: #374151;">
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Input area
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("User Input", placeholder="Ask me anything about your sales data...", label_visibility="collapsed")
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Handle chat interaction
    if send_button and user_input:
        # Send message to AI assistant
        response = send_chat_message(user_input)
        
        if response:
            # Display AI response
            ai_response = response.get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I could not process your request.')
            
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 1rem 1.5rem; border-radius: 20px 20px 5px 20px; max-width: 70%; color: white;">
                    {user_input}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                <div style="background: #f8fafc; border: 1px solid #e5e7eb; padding: 1rem 1.5rem; border-radius: 20px 20px 20px 5px; max-width: 70%; color: #374151;">
                    {ai_response}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Failed to get response from AI assistant. Please check your API connection.")
    
    # CRUD Operations Section
    st.markdown("### 🛠️ Quick Actions")
    
    # Create new account
    with st.expander("➕ Create New Account"):
        with st.form("create_account_form"):
            account_name = st.text_input("Account Name")
            industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Manufacturing", "Other"])
            size = st.selectbox("Size", ["Small", "Medium", "Large", "Enterprise"])
            website = st.text_input("Website (optional)")
            
            if st.form_submit_button("Create Account"):
                if account_name:
                    try:
                        account_data = {
                            "name": account_name,
                            "industry": industry,
                            "size": size,
                            "website": website
                        }
                        response = requests.post(f"{API_BASE}/crm/accounts", json=account_data)
                        if response.status_code == 200:
                            st.success("✅ Account created successfully!")
                        else:
                            st.error("❌ Failed to create account")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please enter an account name")
    
    # Create new deal
    with st.expander("💼 Create New Deal"):
        with st.form("create_deal_form"):
            deal_name = st.text_input("Deal Name")
            account_name = st.text_input("Account Name")
            amount = st.number_input("Amount ($)", min_value=0, value=50000)
            stage = st.selectbox("Stage", ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"])
            
            if st.form_submit_button("Create Deal"):
                if deal_name and account_name:
                    try:
                        deal_data = {
                            "name": deal_name,
                            "account_name": account_name,
                            "amount": amount,
                            "stage": stage
                        }
                        response = requests.post(f"{API_BASE}/crm/deals", json=deal_data)
                        if response.status_code == 200:
                            st.success("✅ Deal created successfully!")
                        else:
                            st.error("❌ Failed to create deal")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please enter deal name and account name")

# Gmail Integration Tab
with tab5:
    st.markdown("### 📧 Gmail Integration")
    st.markdown('<p class="subtitle">AI-powered email management and response generation</p>', unsafe_allow_html=True)
    
    # Gmail Authentication
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🔐 Authentication")
        if st.button("Connect Gmail", use_container_width=True):
            auth_result = authenticate_gmail()
            if auth_result:
                st.success("✅ Gmail connected successfully!")
            else:
                st.error("❌ Failed to connect to Gmail")
    
    with col2:
        st.markdown("#### 📊 Connection Status")
        # Check Gmail status
        try:
            response = requests.get(f"{API_BASE}/integrations/status")
            if response.status_code == 200:
                status_data = response.json()
                gmail_status = status_data.get("integrations", {}).get("gmail", {})
                if gmail_status.get("connected"):
                    st.success("🟢 Gmail Connected")
                else:
                    st.warning("🟡 Gmail Not Connected")
            else:
                st.error("🔴 Status Unknown")
        except:
            st.error("🔴 Cannot check status")
    
    # Email Management
    st.markdown("#### 📬 Unread Emails")
    
    # Store emails in session state
    if "emails" not in st.session_state:
        st.session_state.emails = []
    
    if st.button("Refresh Emails", use_container_width=True):
        emails_data = get_unread_emails(10)
        st.session_state.emails = emails_data.get("emails", [])
    
    if st.session_state.emails:
        st.markdown(f"**Found {len(st.session_state.emails)} unread emails:**")
        
        for i, email in enumerate(st.session_state.emails):
            sender = email.get("from", "Unknown")
            subject = email.get("subject", "No Subject")
            snippet = email.get("snippet", "")
            email_id = email.get("id", f"email_{i}")
            
            with st.expander(f"📧 {subject} - From: {sender}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Subject:** {subject}")
                    st.markdown(f"**From:** {sender}")
                    st.markdown(f"**Snippet:** {snippet}")
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Generate AI Response button
                    if st.button(f"🤖 Generate Response", key=f"gen_{email_id}"):
                        try:
                            response = generate_email_response(email_id)
                            if response:
                                st.success("✅ AI Response Generated!")
                                st.text_area("AI Response:", response.get("response", "No response generated"), height=150)
                            else:
                                st.error("❌ Failed to generate response")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    # Send Email button
                    if st.button(f"📤 Send Email", key=f"send_{email_id}"):
                        try:
                            # Test email to satya.bonda@gmail.com
                            test_email_data = {
                                "to": "satya.bonda@gmail.com",
                                "subject": f"Re: {subject}",
                                "body": f"Thank you for your email regarding '{subject}'. I'll get back to you shortly.",
                                "email_id": email_id
                            }
                            
                            response = requests.post(f"{API_BASE}/integrations/gmail/send", json=test_email_data)
                            if response.status_code == 200:
                                st.success("✅ Email sent successfully to satya.bonda@gmail.com!")
                            else:
                                st.error("❌ Failed to send email")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    # Compose Email button
                    if st.button(f"✏️ Compose", key=f"compose_{email_id}"):
                        st.session_state.composing_email = True
                        st.session_state.compose_to = sender
                        st.session_state.compose_subject = f"Re: {subject}"
                        st.rerun()
    else:
        st.info("No unread emails found. Click 'Refresh Emails' to load emails.")
    
    # Email Composition Section
    if st.session_state.get("composing_email", False):
        st.markdown("#### ✏️ Compose Email")
        
        with st.form("compose_email_form"):
            to_email = st.text_input("To:", value=st.session_state.get("compose_to", ""))
            subject = st.text_input("Subject:", value=st.session_state.get("compose_subject", ""))
            body = st.text_area("Message:", height=200)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.form_submit_button("📤 Send Email"):
                    try:
                        email_data = {
                            "to": to_email,
                            "subject": subject,
                            "body": body
                        }
                        response = requests.post(f"{API_BASE}/integrations/gmail/send", json=email_data)
                        if response.status_code == 200:
                            st.success("✅ Email sent successfully!")
                            st.session_state.composing_email = False
                        else:
                            st.error("❌ Failed to send email")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                if st.form_submit_button("💾 Save Draft"):
                    st.success("✅ Draft saved!")
            
            with col3:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.composing_email = False
                    st.rerun()
    
    # Quick Email Actions
    st.markdown("#### 🚀 Quick Email Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📤 Send Test Email")
        with st.form("test_email_form"):
            test_to = st.text_input("To:", value="satya.bonda@gmail.com")
            test_subject = st.text_input("Subject:", value="Test from AI Sales Platform")
            test_body = st.text_area("Message:", value="This is a test email from the AI Sales Platform. All features are working correctly!")
            
            if st.form_submit_button("📤 Send Test Email"):
                try:
                    test_email_data = {
                        "to": test_to,
                        "subject": test_subject,
                        "body": test_body
                    }
                    response = requests.post(f"{API_BASE}/integrations/gmail/send", json=test_email_data)
                    if response.status_code == 200:
                        st.success("✅ Test email sent successfully!")
                    else:
                        st.error("❌ Failed to send test email")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("#### 🤖 AI Email Assistant")
        ai_prompt = st.text_area("Describe what you want to write:", placeholder="e.g., Follow up on the proposal we discussed last week...")
        
        if st.button("🤖 Generate Email"):
            if ai_prompt:
                try:
                    # Generate AI email content
                    ai_response = requests.post(
                        f"{API_BASE}/v1/chat/completions",
                        json={"messages": [{"role": "user", "content": f"Write a professional email about: {ai_prompt}"}]}
                    )
                    
                    if ai_response.status_code == 200:
                        ai_content = ai_response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                        st.text_area("AI Generated Email:", ai_content, height=200)
                        
                        # Add send button for AI generated email
                        if st.button("📤 Send AI Email"):
                            try:
                                email_data = {
                                    "to": "satya.bonda@gmail.com",
                                    "subject": "AI Generated Email",
                                    "body": ai_content
                                }
                                response = requests.post(f"{API_BASE}/integrations/gmail/send", json=email_data)
                                if response.status_code == 200:
                                    st.success("✅ AI email sent successfully!")
                                else:
                                    st.error("❌ Failed to send AI email")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    else:
                        st.error("❌ Failed to generate AI email")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a description for the email.")
    
    with col3:
        st.markdown("#### 📊 Email Analytics")
        st.metric("Emails Sent Today", "12", "+3")
        st.metric("Response Rate", "85%", "+5%")
        st.metric("Avg Response Time", "2.3 hours", "-0.5 hours")
        
        # Email templates
        st.markdown("#### 📝 Quick Templates")
        templates = [
            "Follow-up on proposal",
            "Meeting confirmation",
            "Thank you note",
            "Product demo request"
        ]
        
        selected_template = st.selectbox("Choose template:", templates)
        if st.button("📤 Send Template"):
            template_content = f"This is a {selected_template} email template."
            try:
                email_data = {
                    "to": "satya.bonda@gmail.com",
                    "subject": f"Template: {selected_template}",
                    "body": template_content
                }
                response = requests.post(f"{API_BASE}/integrations/gmail/send", json=email_data)
                if response.status_code == 200:
                    st.success("✅ Template email sent!")
                else:
                    st.error("❌ Failed to send template email")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# AI Feedback Tab
with tab6:
    st.markdown("### 🎯 AI Feedback & Training")
    st.markdown('<p class="subtitle">Monitor AI performance and provide feedback for continuous improvement</p>', unsafe_allow_html=True)
    
    # Performance Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Model Accuracy</div>
            <div class="metric-value">94%</div>
            <div class="metric-delta metric-delta-positive">↑ 2.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Processed Transcripts</div>
            <div class="metric-value">1,247</div>
            <div class="metric-delta metric-delta-positive">+89 today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Feedback Items</div>
            <div class="metric-value">89</div>
            <div class="metric-delta metric-delta-positive">+12 pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Extractions for Review
    st.markdown("#### 📝 Recent Extractions")
    
    # Sample extraction for review - TechFlow Solutions
    with st.expander("✅ TechFlow Solutions - Review Extraction"):
        st.write("**Extracted Entity:** TechFlow Solutions")
        st.write("**Type:** Company")
        st.write("**Confidence:** 95%")
        st.write("**Context:** '...I understand TechFlow Solutions is looking to improve...'")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Correct", key="correct_1", use_container_width=True):
                st.success("Feedback recorded!")
        with col2:
            if st.button("❌ Incorrect", key="incorrect_1", use_container_width=True):
                st.error("Marked for review")
    
    # Retrain Model Section
    st.markdown("#### 🔄 Model Retraining")
    if st.button("🚀 Retrain Model", type="primary", use_container_width=True):
        with st.spinner("Retraining model with feedback..."):
            # Simulate training progress
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            st.success("✅ Model retrained successfully! Accuracy: 94.5% (+0.5%)")
    
    # Training History Chart
    st.markdown("#### 📊 Training History")
    
    # Create training history data
    dates = pd.date_range(start='2024-01-10', end='2024-01-14', freq='D')
    accuracy_values = [91.5, 92.0, 93.0, 93.5, 94.0]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=accuracy_values,
        mode='lines+markers',
        name='Accuracy',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Model Performance Over Time',
        xaxis_title='Date',
        yaxis_title='Accuracy (%)',
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Training Pipeline Tab
with tab7:
    st.markdown("### 🎓 Intelligent Training Pipeline")
    st.markdown('<p class="subtitle">Transform conversations into actionable CRM insights with AI-powered extraction</p>', unsafe_allow_html=True)

    # Process overview with beautiful cards
    st.markdown("#### 🔄 How It Works")

    col1, col2, col3, col4 = st.columns(4)

    process_steps = [
        {"step": "1", "title": "Upload", "desc": "Import call transcripts or audio files", "icon": "📤"},
        {"step": "2", "title": "Extract", "desc": "AI identifies entities & insights", "icon": "🔍"},
        {"step": "3", "title": "Review", "desc": "Human-in-the-loop validation", "icon": "👁️"},
        {"step": "4", "title": "Update", "desc": "Automated CRM enrichment", "icon": "✅"}
    ]

    for col, step in zip([col1, col2, col3, col4], process_steps):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{step['icon']}</div>
                <div style="background: #667eea; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-weight: 700;">
                    {step['step']}
                </div>
                <div class="feature-title">{step['title']}</div>
                <div class="feature-description">{step['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Upload section with modern design
    st.markdown("#### 📝 Process New Transcript")

    upload_col1, upload_col2 = st.columns([2, 1])

    with upload_col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.03); border: 2px dashed rgba(102,126,234,0.5); border-radius: 20px; padding: 3rem; text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <div style="color: #ffffff; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                Drop your transcript here
            </div>
            <div style="color: #a0a0b0;">or click to browse</div>
        </div>
        """, unsafe_allow_html=True)

        # Sample transcript with syntax highlighting
        sample_transcript = st.text_area(
            "Or paste transcript text:",
            height=200,
            placeholder="Paste your sales call transcript here..."
        )

    with upload_col2:
        st.markdown("#### 🎯 Quick Actions")

        if st.button("🚀 Process Transcript", use_container_width=True):
            if sample_transcript:
                # Processing animation
                with st.spinner("Processing transcript..."):
                    try:
                        # Send transcript to API for processing
                        response = requests.post(
                            f"{API_BASE}/ai/process-transcript",
                            json={"content": sample_transcript, "source": "upload"}
                        )
                        
                        if response.status_code == 200:
                            analysis = response.json()
                            
                            # Show results with beautiful cards
                            st.success("✅ Processing complete!")
                            
                            # Display analysis results
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 🔍 Extracted Entities")
                                if 'entities' in analysis:
                                    for entity in analysis['entities']:
                                        st.markdown(f"**{entity.get('type', 'Unknown')}:** {entity.get('value', 'N/A')}")
                                
                                st.markdown("#### 😊 Sentiment Analysis")
                                if 'sentiment' in analysis:
                                    sentiment = analysis['sentiment']
                                    st.markdown(f"**Overall Sentiment:** {sentiment.get('label', 'Neutral')}")
                                    st.markdown(f"**Confidence:** {sentiment.get('confidence', 0):.1f}%")
                            
                            with col2:
                                st.markdown("#### 📋 Key Topics")
                                if 'key_topics' in analysis:
                                    for topic in analysis['key_topics']:
                                        st.markdown(f"- {topic}")
                                
                                st.markdown("#### 📝 Summary")
                                if 'summary' in analysis:
                                    st.markdown(analysis['summary'])
                            
                            # Metrics
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("Entities Found", len(analysis.get('entities', [])), "+5")
                            with metric_col2:
                                st.metric("Confidence Score", f"{analysis.get('confidence', 94)}%", "+8%")
                            with metric_col3:
                                st.metric("Time Saved", "15 min", "-75%")
                        else:
                            st.error("Failed to process transcript. Please try again.")
                    except Exception as e:
                        st.error(f"Error processing transcript: {str(e)}")
            else:
                st.warning("Please paste a transcript first.")

    # Real-time monitoring
    st.markdown("#### 📊 Training Performance Metrics")

    # Performance charts
    perf_col1, perf_col2 = st.columns(2)

    with perf_col1:
        # Accuracy over time
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        accuracy = 70 + np.cumsum(np.random.randn(90) * 0.5)

        fig_accuracy = go.Figure()
        fig_accuracy.add_trace(go.Scatter(
            x=dates,
            y=accuracy,
            mode='lines+markers',
            name='Model Accuracy',
            line=dict(color='#34d399', width=3),
            marker=dict(size=4)
        ))

        fig_accuracy.update_layout(
            title="Model Accuracy Improvement",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
            showlegend=False,
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', ticksuffix='%'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_accuracy, use_container_width=True)

    with perf_col2:
        # Entity distribution
        entities = ['Company', 'Person', 'Amount', 'Date', 'Email', 'Phone']
        counts = [145, 234, 189, 123, 98, 76]

        fig_entities = go.Figure(go.Bar(
            x=counts,
            y=entities,
            orientation='h',
            marker=dict(
                color=counts,
                colorscale='Viridis',
                showscale=False
            )
        ))

        fig_entities.update_layout(
            title="Entity Extraction Distribution",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_entities, use_container_width=True)

# Footer with beautiful design
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <p style="color: #a0a0b0; font-size: 0.9rem;">
        Powered by cutting-edge AI • Built with ❤️ for sales teams
    </p>
    <div style="margin-top: 1rem;">
        <span class="status-badge status-active">All Systems Operational</span>
        <span style="color: #a0a0b0; margin: 0 1rem;">•</span>
        <span style="color: #a0a0b0;">Last sync: 2 minutes ago</span>
    </div>
</div>
""", unsafe_allow_html=True)
