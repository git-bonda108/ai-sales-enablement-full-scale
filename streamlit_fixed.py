import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Page config
st.set_page_config(
    page_title="AI Sales Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)

# Mock data for standalone functionality
MOCK_ACCOUNTS = [
    {
        "id": "acc_001",
        "name": "Acme Corporation",
        "industry": "Technology",
        "revenue": 5000000,
        "status": "Active",
        "health_score": 85,
        "last_contact": "2024-08-01"
    },
    {
        "id": "acc_002", 
        "name": "Global Dynamics",
        "industry": "Manufacturing",
        "revenue": 10000000,
        "status": "Active",
        "health_score": 72,
        "last_contact": "2024-07-28"
    },
    {
        "id": "acc_003",
        "name": "TechStart Inc",
        "industry": "Software",
        "revenue": 2500000,
        "status": "Active",
        "health_score": 91,
        "last_contact": "2024-08-03"
    }
]

MOCK_DEALS = [
    {
        "id": "deal_001",
        "name": "Enterprise Software License",
        "account": "Acme Corporation",
        "value": 125000,
        "stage": "Negotiation",
        "probability": 75,
        "close_date": "2024-09-15",
        "owner": "Sarah Johnson"
    },
    {
        "id": "deal_002",
        "name": "Cloud Migration Project",
        "account": "Global Dynamics",
        "value": 250000,
        "stage": "Proposal",
        "probability": 60,
        "close_date": "2024-10-20",
        "owner": "Mike Chen"
    },
    {
        "id": "deal_003",
        "name": "AI Implementation",
        "account": "TechStart Inc",
        "value": 180000,
        "stage": "Qualification",
        "probability": 40,
        "close_date": "2024-11-05",
        "owner": "Lisa Rodriguez"
    }
]

MOCK_METRICS = {
    "sales_performance": {
        "total_revenue": 1250000,
        "deals_closed": 47,
        "conversion_rate": 24.5,
        "average_deal_size": 26595
    },
    "activity_metrics": {
        "calls_made": 342,
        "emails_sent": 1058,
        "meetings_scheduled": 89,
        "proposals_sent": 34
    }
}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("🚀 AI Sales Intelligence Platform")
st.markdown("Empowering sales teams with real-time AI insights and automation")

# Navigation tabs
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
    st.header("📊 Key Performance Metrics")
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${MOCK_METRICS['sales_performance']['total_revenue']:,.0f}")
    with col2:
        st.metric("Deals Closed", MOCK_METRICS['sales_performance']['deals_closed'])
    with col3:
        st.metric("Conversion Rate", f"{MOCK_METRICS['sales_performance']['conversion_rate']}%")
    with col4:
        st.metric("Avg Deal Size", f"${MOCK_METRICS['sales_performance']['average_deal_size']:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        dates = pd.date_range(start='2024-01-01', end='2024-08-01', freq='M')
        revenue_data = [800000, 950000, 1100000, 1250000, 1300000, 1350000, 1400000, 1450000]
        
        fig = px.line(x=dates, y=revenue_data, title="Monthly Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Deal Pipeline")
        stages = ['Qualification', 'Discovery', 'Proposal', 'Negotiation', 'Closed']
        values = [320000, 450000, 380000, 125000, 0]
        
        fig = px.bar(x=stages, y=values, title="Deal Pipeline by Stage")
        st.plotly_chart(fig, use_container_width=True)

# Accounts Tab
with tab2:
    st.header("🏢 Account Management")
    
    # Account metrics
    total_accounts = len(MOCK_ACCOUNTS)
    active_accounts = len([acc for acc in MOCK_ACCOUNTS if acc["status"] == "Active"])
    avg_health_score = np.mean([acc["health_score"] for acc in MOCK_ACCOUNTS])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Accounts", total_accounts)
    with col2:
        st.metric("Active Accounts", active_accounts)
    with col3:
        st.metric("Avg Health Score", f"{avg_health_score:.1f}")
    
    # Accounts table
    st.subheader("📋 Account Details")
    accounts_df = pd.DataFrame(MOCK_ACCOUNTS)
    accounts_df["revenue"] = accounts_df["revenue"].apply(lambda x: f"${x:,.0f}")
    accounts_df["health_score"] = accounts_df["health_score"].apply(lambda x: f"{x}%")
    
    st.dataframe(
        accounts_df[["name", "industry", "revenue", "status", "health_score", "last_contact"]],
        use_container_width=True
    )

# Deals Tab
with tab3:
    st.header("💼 Deal Pipeline")
    
    # Deal metrics
    total_deals = len(MOCK_DEALS)
    total_value = sum([deal["value"] for deal in MOCK_DEALS])
    avg_probability = np.mean([deal["probability"] for deal in MOCK_DEALS])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Deals", total_deals)
    with col2:
        st.metric("Total Value", f"${total_value:,.0f}")
    with col3:
        st.metric("Avg Probability", f"{avg_probability:.1f}%")
    
    # Deals table
    st.subheader("📋 Deal Details")
    deals_df = pd.DataFrame(MOCK_DEALS)
    deals_df["value"] = deals_df["value"].apply(lambda x: f"${x:,.0f}")
    deals_df["probability"] = deals_df["probability"].apply(lambda x: f"{x}%")
    
    st.dataframe(
        deals_df[["name", "account", "value", "stage", "probability", "close_date", "owner"]],
        use_container_width=True
    )

# AI Assistant Tab
with tab4:
    st.header("🤖 AI Sales Assistant")
    
    # Chat interface
    st.subheader("💬 Chat with AI")
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**AI:** {message['content']}")
    
    # Chat input
    user_message = st.text_input("Ask me anything about your sales data:")
    
    if st.button("Send Message"):
        if user_message:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            # Mock AI response
            responses = [
                "Based on your sales data, I recommend focusing on the high-value deals in the negotiation stage.",
                "Your conversion rate is above industry average. Consider upselling opportunities with existing clients.",
                "I've analyzed your pipeline and identified 3 deals that need immediate attention.",
                "The AI insights show positive sentiment across your customer base.",
                "Consider scheduling follow-up calls with accounts that haven't been contacted recently."
            ]
            ai_response = np.random.choice(responses)
            
            # Add AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            st.rerun()

# Gmail Integration Tab
with tab5:
    st.header("📧 Gmail Integration")
    
    # Mock email data
    emails = [
        {
            "id": "email_001",
            "subject": "Follow-up on proposal",
            "from": "john.doe@acme.com",
            "snippet": "Hi, I wanted to follow up on the proposal you sent last week...",
            "sentiment": "positive"
        },
        {
            "id": "email_002",
            "subject": "Meeting request",
            "from": "sarah.smith@global.com",
            "snippet": "Would you be available for a call this week to discuss...",
            "sentiment": "neutral"
        }
    ]
    
    st.subheader("📬 Recent Emails")
    
    for email in emails:
        with st.expander(f"📧 {email['subject']} - {email['from']}"):
            st.write(f"**From:** {email['from']}")
            st.write(f"**Subject:** {email['subject']}")
            st.write(f"**Snippet:** {email['snippet']}")
            st.write(f"**Sentiment:** {email['sentiment']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Generate Response", key=f"respond_{email['id']}"):
                    st.info("AI is generating a response...")
            with col2:
                if st.button(f"Analyze", key=f"analyze_{email['id']}"):
                    st.success("Email analyzed for insights and opportunities")

# AI Feedback Tab
with tab6:
    st.header("🎯 AI Feedback & Insights")
    
    # Mock AI insights
    insights = [
        {
            "type": "Opportunity",
            "message": "High-value deal in negotiation stage needs immediate attention",
            "priority": "High",
            "action": "Schedule follow-up call"
        },
        {
            "type": "Risk",
            "message": "Account health score dropping for Global Dynamics",
            "priority": "Medium",
            "action": "Review account strategy"
        },
        {
            "type": "Recommendation",
            "message": "Consider upselling opportunities with TechStart Inc",
            "priority": "Low",
            "action": "Prepare upsell proposal"
        }
    ]
    
    for insight in insights:
        with st.expander(f"🔍 {insight['type']}: {insight['message']}"):
            st.write(f"**Priority:** {insight['priority']}")
            st.write(f"**Recommended Action:** {insight['action']}")
            
            if st.button(f"Take Action", key=f"action_{insight['type']}"):
                st.success("Action logged and scheduled!")

# Training Pipeline Tab
with tab7:
    st.header("🎓 Training Feedback and Pipeline")
    
    # Mock training data
    training_metrics = {
        "transcripts_processed": 45,
        "entities_extracted": 234,
        "feedback_items": 12,
        "model_accuracy": 87.5
    }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Transcripts Processed", training_metrics["transcripts_processed"])
    with col2:
        st.metric("Entities Extracted", training_metrics["entities_extracted"])
    with col3:
        st.metric("Feedback Items", training_metrics["feedback_items"])
    with col4:
        st.metric("Model Accuracy", f"{training_metrics['model_accuracy']}%")
    
    # Training pipeline status
    st.subheader("🔄 Training Pipeline Status")
    
    pipeline_stages = [
        {"stage": "Data Collection", "status": "✅ Complete", "progress": 100},
        {"stage": "Entity Extraction", "status": "✅ Complete", "progress": 100},
        {"stage": "Model Training", "status": "🔄 In Progress", "progress": 75},
        {"stage": "Validation", "status": "⏳ Pending", "progress": 0},
        {"stage": "Deployment", "status": "⏳ Pending", "progress": 0}
    ]
    
    for stage in pipeline_stages:
        st.write(f"**{stage['stage']}:** {stage['status']} ({stage['progress']}%)")
        st.progress(stage['progress'] / 100)
    
    # Upload transcript for training
    st.subheader("📝 Upload Transcript for Training")
    uploaded_file = st.file_uploader("Choose a transcript file", type=['txt', 'pdf'])
    
    if uploaded_file is not None:
        st.success("Transcript uploaded successfully!")
        st.info("Processing transcript for entity extraction and training...")
        
        if st.button("Process Transcript"):
            st.success("✅ Transcript processed! Entities extracted and added to training data.")

# Footer
st.markdown("---")
st.markdown("AI Sales Intelligence Platform | Powered by Streamlit") 