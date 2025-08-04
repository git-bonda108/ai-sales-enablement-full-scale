import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Import Gmail integration if credentials exist
if os.path.exists('credentials.json'):
    from gmail_integration import GmailIntegration
    gmail = GmailIntegration()
else:
    gmail = None

st.set_page_config(
    page_title="AI Sales Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .deal-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🚀 AI Sales Enablement Platform")

    # Sidebar with AI Assistant
    with st.sidebar:
        st.header("🤖 AI Sales Assistant")

        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        user_input = st.text_input("Ask me anything about your sales data...")

        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Process with AI (this actually creates records!)
            if "create account" in user_input.lower():
                # Extract account name
                words = user_input.split()
                if "called" in words:
                    idx = words.index("called")
                    if idx + 1 < len(words):
                        account_name = " ".join(words[idx+1:])
                        # Actually create the account
                        resp = requests.post(f"{API_BASE}/crm/accounts", 
                            json={"name": account_name, "industry": "Technology"})
                        if resp.status_code == 200:
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": f"✅ Created account '{account_name}'! You can see it in the Accounts tab."
                            })
                        else:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "❌ Failed to create account. Please try again."
                            })

            elif "create deal" in user_input.lower():
                # Create a deal
                if "for" in user_input and "$" in user_input:
                    # Extract value
                    import re
                    value_match = re.search(r'\$([\d,]+)', user_input)
                    if value_match:
                        value = int(value_match.group(1).replace(',', ''))
                        resp = requests.post(f"{API_BASE}/crm/deals",
                            json={
                                "title": "New Deal from Chat",
                                "value": value,
                                "stage": "Qualification"
                            })
                        if resp.status_code == 200:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"✅ Created deal for ${value:,}! Check the Deals tab."
                            })

            else:
                # Regular query
                resp = requests.post(f"{API_BASE}/analytics/chat", 
                    json={"query": user_input})
                if resp.status_code == 200:
                    response = resp.json().get("response", "I'll help you with that...")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

        # Display chat history
        for msg in st.session_state.messages[-5:]:  # Show last 5 messages
            if msg["role"] == "user":
                st.info(f"You: {msg['content']}")
            else:
                st.success(f"AI: {msg['content']}")

        st.divider()

        # Quick Actions
        st.subheader("Quick Actions")
        if st.button("📊 Generate Weekly Report"):
            st.info("Generating report...")

        if st.button("📧 Draft Follow-up Emails"):
            st.info("Drafting emails...")

    # Main content tabs
    tabs = st.tabs(["📊 Dashboard", "🏢 Accounts", "💼 Deals", "📧 Email Hub", 
                    "🎯 Training Pipeline", "⚙️ Settings"])

    # Dashboard Tab
    with tabs[0]:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        # Fetch metrics
        forecast_resp = requests.get(f"{API_BASE}/analytics/forecast")
        if forecast_resp.status_code == 200:
            forecast_data = forecast_resp.json()

            with col1:
                st.metric("Q2 Forecast", 
                         f"${forecast_data.get('total_weighted', 0):,.0f}",
                         f"{forecast_data.get('growth', 15)}% ↑")

            with col2:
                st.metric("Win Rate", "68%", "5% ↑")

            with col3:
                st.metric("Avg Deal Size", "$125,000", "12% ↑")

            with col4:
                st.metric("Pipeline Value", "$3.2M", "23% ↑")

        # Charts
        st.subheader("Pipeline Overview")
        # Add your charts here

    # Accounts Tab
    with tabs[1]:
        st.header("Accounts Management")

        col1, col2 = st.columns([3, 1])

        with col2:
            st.subheader("Add New Account")
            with st.form("new_account"):
                name = st.text_input("Company Name")
                industry = st.selectbox("Industry", 
                    ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"])
                revenue = st.number_input("Annual Revenue", min_value=0, step=100000)
                employees = st.number_input("Employees", min_value=1, step=10)

                if st.form_submit_button("Create Account"):
                    resp = requests.post(f"{API_BASE}/crm/accounts", 
                        json={
                            "name": name,
                            "industry": industry,
                            "revenue": revenue,
                            "employees": employees
                        })
                    if resp.status_code == 200:
                        st.success(f"✅ Account '{name}' created!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to create account")

        with col1:
            # List accounts
            accounts_resp = requests.get(f"{API_BASE}/crm/accounts")
            if accounts_resp.status_code == 200:
                accounts = accounts_resp.json()

                for account in accounts:
                    with st.expander(f"🏢 {account['name']} - {account['industry']}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Revenue", f"${account.get('revenue', 0):,}")
                        col2.metric("Employees", account.get('employees', 0))
                        col3.metric("Deals", account.get('deal_count', 0))

                        # Gmail integration button
                        if gmail:
                            if st.button(f"📧 Send Email", key=f"email_{account['id']}"):
                                st.session_state[f"compose_{account['id']}"] = True

                            if st.session_state.get(f"compose_{account['id']}", False):
                                with st.form(f"email_form_{account['id']}"):
                                    to_email = st.text_input("To:", value=account.get('email', ''))
                                    subject = st.text_input("Subject:", 
                                        value=f"Following up - {account['name']}")
                                    body = st.text_area("Message:", height=150,
                                        value=f"Hi {account['name']} team,\n\n")

                                    if st.form_submit_button("Send Email"):
                                        success, msg = gmail.send_email(to_email, subject, body)
                                        if success:
                                            st.success(msg)
                                            st.session_state[f"compose_{account['id']}"] = False
                                        else:
                                            st.error(msg)

    # Deals Tab
    with tabs[2]:
        st.header("Deals Pipeline")

        # Create new deal
        with st.expander("➕ Create New Deal"):
            with st.form("new_deal"):
                title = st.text_input("Deal Title")
                account_id = st.selectbox("Account", 
                    options=[a['id'] for a in accounts],
                    format_func=lambda x: next(a['name'] for a in accounts if a['id'] == x))
                value = st.number_input("Deal Value", min_value=0, step=1000)
                stage = st.selectbox("Stage", 
                    ["Qualification", "Discovery", "Proposal", "Negotiation", "Closed Won", "Closed Lost"])

                if st.form_submit_button("Create Deal"):
                    resp = requests.post(f"{API_BASE}/crm/deals",
                        json={
                            "title": title,
                            "account_id": account_id,
                            "value": value,
                            "stage": stage
                        })
                    if resp.status_code == 200:
                        st.success("✅ Deal created!")
                        st.experimental_rerun()

    # Email Hub Tab
    with tabs[3]:
        st.header("📧 Email Hub")

        if gmail:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Recent Emails")
                emails = gmail.get_recent_emails()
                for email in emails:
                    with st.expander(f"📧 {email['subject'][:50]}..."):
                        st.write(f"**From:** {email['from']}")
                        st.write(f"**Preview:** {email['snippet']}")

                        if st.button(f"Generate Reply", key=f"reply_{email['id']}"):
                            # Generate AI reply
                            st.info("AI is drafting a reply...")

            with col2:
                st.subheader("Quick Compose")
                with st.form("quick_email"):
                    to = st.text_input("To:")
                    subject = st.text_input("Subject:")
                    template = st.selectbox("Template", 
                        ["Custom", "Follow-up", "Introduction", "Proposal", "Thank you"])
                    body = st.text_area("Message:", height=200)

                    if st.form_submit_button("📤 Send"):
                        if gmail:
                            success, msg = gmail.send_email(to, subject, body)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        else:
            st.warning("⚠️ Gmail not configured. Please add credentials.json file.")
            st.info("Steps to enable Gmail:")
            st.code("""
1. Go to Google Cloud Console
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download as credentials.json
5. Place in project root directory
6. Restart the application
            """)

    # Training Pipeline Tab
    with tabs[4]:
        st.header("Training Pipeline")

        transcript = st.text_area("Paste call transcript here:", height=200)

        if st.button("Process Transcript"):
            if transcript:
                resp = requests.post(f"{API_BASE}/analytics/process-transcript",
                    json={"transcript": transcript})
                if resp.status_code == 200:
                    result = resp.json()
                    st.success("✅ Transcript processed!")
                    st.json(result)

if __name__ == "__main__":
    main()
