# Add this to your streamlit_app.py

import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd

# Add to your navigation menu
def show_integrations_page():
    """Integrations page for Gmail and Voice"""
    st.title("🔌 Integrations Hub")

    # Get integration status
    try:
        response = requests.get(f"{API_URL}/integrations/status")
        status = response.json()
    except:
        status = None

    # Status indicators
    col1, col2, col3 = st.columns(3)

    with col1:
        gmail_status = status.get('gmail', {}) if status else {}
        if gmail_status.get('connected'):
            st.success("✅ Gmail Connected")
        else:
            st.error("❌ Gmail Disconnected")
            if st.button("Connect Gmail", key="connect_gmail"):
                with st.spinner("Authenticating..."):
                    try:
                        response = requests.post(f"{API_URL}/integrations/gmail/auth")
                        if response.status_code == 200:
                            st.success("Gmail connected successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to connect: {str(e)}")

    with col2:
        voice_status = status.get('voice', {}) if status else {}
        st.info(f"📞 Voice: {voice_status.get('status', 'Unknown')}")

    with col3:
        crm_status = status.get('crm', {}) if status else {}
        st.success(f"💼 CRM: {crm_status.get('status', 'Unknown')}")

    st.divider()

    # Integration tabs
    tab1, tab2 = st.tabs(["📧 Email Intelligence", "🎙️ Voice Coaching"])

    # Email Intelligence Tab
    with tab1:
        show_email_intelligence()

    # Voice Coaching Tab
    with tab2:
        show_voice_coaching()

def show_email_intelligence():
    """Email intelligence interface"""
    st.header("Email Intelligence & Analysis")

    if st.button("🔄 Refresh Emails", key="refresh_emails"):
        with st.spinner("Fetching emails..."):
            try:
                response = requests.get(f"{API_URL}/integrations/gmail/unread")
                if response.status_code == 200:
                    emails = response.json().get('emails', [])
                    st.session_state['emails'] = emails
                    st.success(f"Found {len(emails)} unread emails")
            except Exception as e:
                st.error(f"Failed to fetch emails: {str(e)}")

    # Display emails
    if 'emails' in st.session_state:
        for email in st.session_state['emails']:
            with st.expander(f"📧 {email['subject']} - From: {email['from']}"):
                # Email content
                st.write("**Date:**", email['date'])
                st.write("**Body:**")
                st.text(email['body'][:500] + "..." if len(email['body']) > 500 else email['body'])

                # Analysis results
                analysis = email.get('analysis', {})

                col1, col2 = st.columns(2)
                with col1:
                    intent = analysis.get('intent_level', 'Unknown')
                    score = analysis.get('signal_score', 0)

                    if intent == "HIGH":
                        st.metric("Intent Level", intent, f"Score: {score}", delta_color="normal")
                    elif intent == "MEDIUM":
                        st.metric("Intent Level", intent, f"Score: {score}", delta_color="normal")
                    else:
                        st.metric("Intent Level", intent, f"Score: {score}", delta_color="off")

                with col2:
                    st.write("**Key Points:**")
                    for point in analysis.get('key_points', [])[:3]:
                        st.write(f"• {point}")

                # AI Response
                if st.button(f"🤖 Generate AI Response", key=f"gen_{email['id']}"):
                    with st.spinner("Generating response..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/integrations/gmail/generate-response/{email['id']}"
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.write("**Suggested Response:**")
                                st.text_area(
                                    "Edit before sending:", 
                                    value=data['suggested_response'],
                                    height=200,
                                    key=f"response_{email['id']}"
                                )

                                if st.button(f"📤 Send", key=f"send_{email['id']}"):
                                    # Implementation for sending would go here
                                    st.success("Email sent!")
                        except Exception as e:
                            st.error(f"Failed to generate response: {str(e)}")

                # Next steps
                st.write("**Recommended Next Steps:**")
                for step in analysis.get('next_steps', [])[:3]:
                    st.write(f"• {step}")

def show_voice_coaching():
    """Voice coaching interface"""
    st.header("AI Voice Coaching")

    col1, col2 = st.columns([2, 1])

    with col1:
        participant = st.text_input("Participant Name:", value="John from TechCorp")

    with col2:
        if st.button("📞 Start Mock Call", type="primary"):
            try:
                response = requests.post(
                    f"{API_URL}/integrations/voice/start-call",
                    json={"participant": participant}
                )
                if response.status_code == 200:
                    call_data = response.json()
                    st.session_state['active_call'] = call_data
                    st.success("Call started!")
            except Exception as e:
                st.error(f"Failed to start call: {str(e)}")

    # Active call interface
    if 'active_call' in st.session_state:
        call_id = st.session_state['active_call']['call_id']

        # Real-time transcript
        transcript_container = st.container()
        coaching_container = st.container()

        # End call button
        if st.button("🔴 End Call"):
            try:
                response = requests.post(f"{API_URL}/integrations/voice/end-call/{call_id}")
                if response.status_code == 200:
                    analytics = response.json()
                    st.session_state['call_analytics'] = analytics
                    del st.session_state['active_call']
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to end call: {str(e)}")

        # Poll for updates
        if 'last_index' not in st.session_state:
            st.session_state['last_index'] = 0

        # Auto-refresh transcript
        placeholder = st.empty()

        while 'active_call' in st.session_state:
            try:
                response = requests.get(
                    f"{API_URL}/integrations/voice/transcript/{call_id}",
                    params={"last_index": st.session_state['last_index']}
                )

                if response.status_code == 200:
                    data = response.json()

                    with placeholder.container():
                        col1, col2 = st.columns([3, 2])

                        with col1:
                            st.subheader("📝 Real-time Transcript")

                            # Display new messages
                            for msg in data.get('new_messages', []):
                                if msg['speaker'] == 'Customer':
                                    st.write(f"**{msg['speaker']}:** {msg['text']}")
                                else:
                                    st.info(f"**You:** {msg['text']}")

                        with col2:
                            st.subheader("💡 AI Coaching")

                            # Sentiment score
                            sentiment = data.get('sentiment_score', 0.5)
                            st.metric(
                                "Call Sentiment", 
                                f"{sentiment:.1%}",
                                delta=f"{(sentiment-0.5)*100:.1f}%"
                            )

                            # AI suggestion
                            if data.get('ai_suggestion'):
                                st.success(f"💡 {data['ai_suggestion']}")

                            # Duration
                            st.metric("Duration", f"{data.get('elapsed_time', 0)}s")

                    st.session_state['last_index'] = data.get('elapsed_time', 0)

            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                break

            time.sleep(1)  # Poll every second

    # Show analytics if available
    if 'call_analytics' in st.session_state:
        st.divider()
        st.subheader("📊 Call Analytics")

        analytics = st.session_state['call_analytics']['analytics']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Duration", f"{analytics['duration']}s")
            st.metric("Sentiment Score", f"{analytics['sentiment_score']:.1%}")

        with col2:
            st.metric("Talk Ratio", f"{analytics['talk_ratio']:.1%}")
            st.write("**Topics Discussed:**")
            for topic in analytics['topics_discussed']:
                st.write(f"• {topic.replace('_', ' ').title()}")

        with col3:
            st.write("**Recommendations:**")
            for rec in analytics['recommendations']:
                st.write(f"• {rec}")

        # Key moments
        st.write("**Key Moments:**")
        for moment in analytics['key_moments']:
            icon = "✅" if moment['type'] == 'buying_signal' else "⚠️"
            st.write(f"{icon} [{moment['timestamp']}s] {moment['speaker']}: {moment['text']}")

        # Next steps
        st.write("**Suggested Next Steps:**")
        for step in analytics['next_steps']:
            st.write(f"• {step}")

# Add this to your main navigation
if page == "Integrations":
    show_integrations_page()
