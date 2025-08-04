"""
Demo Configuration
Settings and mock data for demo
"""

# API Settings
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 10

# UI Settings
PAGE_TITLE = "AI Sales Intelligence Platform"
PAGE_ICON = "🚀"
THEME_COLOR = "#3b82f6"

# Demo accounts for showcase
DEMO_ACCOUNTS = [
    {
        "id": 1,
        "name": "Acme Corporation",
        "industry": "Technology",
        "annual_revenue": 50000000,
        "employee_count": 500,
        "website": "acme.com",
        "description": "Leading provider of cloud solutions"
    },
    {
        "id": 2,
        "name": "Global Dynamics",
        "industry": "Manufacturing",
        "annual_revenue": 100000000,
        "employee_count": 2000,
        "website": "globaldynamics.com",
        "description": "Industrial automation leader"
    },
    {
        "id": 3,
        "name": "TechStart Inc",
        "industry": "Technology",
        "annual_revenue": 10000000,
        "employee_count": 100,
        "website": "techstart.io",
        "description": "Innovative AI startup"
    }
]

# Demo activities
DEMO_ACTIVITIES = [
    {
        "time": "10:30 AM",
        "icon": "📧",
        "description": "Email sent to John Doe at Acme Corp",
        "outcome": "Opened within 5 minutes"
    },
    {
        "time": "2:15 PM",
        "icon": "📞",
        "description": "Discovery call with Global Dynamics",
        "outcome": "Scheduled follow-up demo"
    },
    {
        "time": "3:45 PM",
        "icon": "📄",
        "description": "Proposal sent to TechStart Inc",
        "outcome": "Under review"
    }
]

# Chart color schemes
CHART_COLORS = {
    "primary": ["#3b82f6", "#60a5fa", "#93bbfd", "#c3d9fe", "#e0ecff"],
    "success": ["#10b981", "#34d399", "#6ee7b7", "#a7f3d0", "#d1fae5"],
    "warning": ["#f59e0b", "#fbbf24", "#fcd34d", "#fde68a", "#fef3c7"],
    "danger": ["#ef4444", "#f87171", "#fca5a5", "#fecaca", "#fee2e2"]
}

# AI Insights templates
AI_INSIGHTS = [
    {
        "type": "opportunity",
        "title": "High-Value Deal Alert",
        "message": "3 deals worth $450K show buying signals. AI recommends immediate engagement.",
        "action": "View Deals"
    },
    {
        "type": "risk",
        "title": "Pipeline Risk Detected",
        "message": "5 deals in Negotiation stage for >30 days. Risk of stalling detected.",
        "action": "Review Pipeline"
    },
    {
        "type": "optimization",
        "title": "Process Improvement",
        "message": "Demos converting 65% better than calls. Prioritize demo scheduling.",
        "action": "Update Strategy"
    }
]
