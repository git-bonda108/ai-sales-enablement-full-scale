"""
Integration test for complete MCP system
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_api_gateway():
    """Test the API gateway with all endpoints"""

    print("🧪 Testing AI Sales MCP Platform Integration")
    print("=" * 60)

    # Test 1: Health check
    print("Test 1: Health Check")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    health = response.json()
    print(f"   Status: {health['status']}")
    print(f"   Connected: {health['connected']}")
    print()

    # Test 2: List accounts
    print("Test 2: List Accounts")
    response = requests.get(f"{API_BASE}/api/accounts")
    assert response.status_code == 200
    accounts = response.json()
    print(f"   Found {accounts['count']} accounts")
    print()

    # Test 3: Get dashboard
    print("Test 3: Sales Dashboard")
    response = requests.get(f"{API_BASE}/api/analytics/dashboard")
    assert response.status_code == 200
    dashboard = response.json()
    print(f"   Pipeline: ${dashboard['pipeline']['total_pipeline_value']:,.0f}")
    print(f"   Forecast: ${dashboard['forecast']['forecast']['expected']:,.0f}")
    print(f"   Win Rate: {dashboard['metrics']['conversion_metrics']['win_rate']}%")
    print()

    # Test 4: Create deal
    print("Test 4: Create Deal with AI Scoring")
    deal_data = {
        "account_id": 1,
        "name": "Q1 Cloud Migration",
        "amount": 125000,
        "stage": "Qualification"
    }
    response = requests.post(f"{API_BASE}/api/deals", json=deal_data)
    assert response.status_code == 200
    result = response.json()
    print(f"   Deal created: {result['deal']['name']}")
    print(f"   AI Score: {result['score']['score']}/100")
    print(f"   Priority: {result['score']['priority']}")
    print()

    # Test 5: Get hot deals
    print("Test 5: AI Hot Deals")
    response = requests.get(f"{API_BASE}/api/analytics/hot-deals")
    assert response.status_code == 200
    hot_deals = response.json()
    print(f"   Found {hot_deals['count']} hot deals")
    if hot_deals['deals']:
        print(f"   #1: {hot_deals['deals'][0]['account_name']} - Score: {hot_deals['deals'][0]['score']}")
    print()

    # Test 6: Conversion analytics
    print("Test 6: Conversion Analytics")
    response = requests.get(f"{API_BASE}/api/analytics/conversions")
    assert response.status_code == 200
    conversions = response.json()
    print(f"   Win rate: {conversions['overall_metrics']['win_rate']}%")
    print(f"   Funnel stages analyzed: {len(conversions['funnel_stages'])}")
    print()

    print("✅ All integration tests passed!")
    print()
    print("🎯 System Integration Verified!")
    print("   - API Gateway: ✅")
    print("   - CRM Endpoints: ✅")
    print("   - Analytics Endpoints: ✅")
    print("   - AI Features: ✅")
    print()
    print("Ready for Streamlit UI (Batch 6)!")

if __name__ == "__main__":
    try:
        test_api_gateway()
    except requests.exceptions.ConnectionError:
        print("❌ Error: API Gateway not running!")
        print("   Please start it with: uv run python api/api_gateway.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
