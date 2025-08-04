"""
UI Components and Helpers
Reusable components for Streamlit app
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Optional

def create_metric_card(label: str, value: str, delta: Optional[str] = None, delta_color: str = "normal"):
    """Create a styled metric card"""
    html = f"""
    <div class="metric-card">
        <p class="metric-label">{label}</p>
        <p class="big-metric">{value}</p>
        {f'<p class="metric-delta" style="color: {"green" if delta_color == "normal" else "red"}">{delta}</p>' if delta else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def create_gauge_chart(value: int, title: str, max_value: int = 100):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(height=250)
    return fig

def create_activity_timeline(activities: List[Dict]):
    """Create an activity timeline"""
    if not activities:
        st.info("No recent activities")
        return

    for activity in activities:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**{activity['time']}**")
        with col2:
            icon = activity.get('icon', '📌')
            st.markdown(f"{icon} {activity['description']}")
            if activity.get('outcome'):
                st.caption(f"→ {activity['outcome']}")

def create_deal_card(deal: Dict):
    """Create a deal card with scoring"""
    score_color = "green" if deal['score'] >= 75 else "orange" if deal['score'] >= 50 else "red"

    st.markdown(f"""
    <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">{deal['name']}</h4>
                <p style="color: #6b7280; margin: 5px 0;">{deal['account_name']} • ${deal['amount']:,.0f}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: bold; color: {score_color};">{deal['score']}</div>
                <div style="font-size: 12px; color: #6b7280;">AI Score</div>
            </div>
        </div>
        <div style="margin-top: 10px;">
            <span class="{deal['priority'].lower()}-badge">{deal['priority']}</span>
            <span style="margin-left: 10px; color: #6b7280;">{deal['recommended_action']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_loading_animation(message: str = "Loading AI insights..."):
    """Show a loading animation"""
    with st.spinner(message):
        import time
        time.sleep(1)  # Simulate processing
