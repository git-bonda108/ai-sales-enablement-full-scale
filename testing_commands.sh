#!/bin/bash

# AI Sales Platform - Complete Testing Commands
# Run these commands in sequence for full platform validation

echo "🚀 AI Sales Platform - Comprehensive Testing Suite"
echo "=================================================="

# Step 1: Environment Setup
echo "📋 Step 1: Environment Setup"
echo "export OPENAI_API_KEY='your-key-here'"
echo "pip install -r requirements.txt"
echo ""

# Step 2: Start Services
echo "🔄 Step 2: Start All Services"
echo "chmod +x quick_fix.sh"
echo "./quick_fix.sh"
echo "# Wait for services to start..."
echo "sleep 10"
echo ""

# Step 3: Health Checks
echo "🏥 Step 3: Health Checks"
echo "curl http://localhost:8000/health"
echo "curl http://localhost:8000/docs"
echo "open http://localhost:8501"
echo ""

# Step 4: Load Demo Data
echo "📊 Step 4: Load Story Data"
echo "python story_demo_data_generator.py"
echo ""

# Step 5: Test API Endpoints
echo "🧪 Step 5: Test Core APIs"
echo ""
echo "# Test CRM Endpoints"
echo "curl http://localhost:8000/crm/accounts"
echo "curl http://localhost:8000/crm/deals"
echo ""
echo "# Test Analytics"
echo "curl http://localhost:8000/analytics/forecast"
echo ""
echo "# Test Chat"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "What is our pipeline value?"}'"'"
echo ""
echo "# Test Transcript Processing"
echo 'curl -X POST http://localhost:8000/analytics/process-transcript -H "Content-Type: application/json" -d '"'"'{"transcript": "Customer budget is $500K, timeline Q3"}'"'"
echo ""

# Step 6: Integration Tests
echo "🔗 Step 6: Run Integration Tests"
echo "python integration_test_suite.py"
echo ""

# Step 7: UI Testing
echo "🖥️  Step 7: UI Testing Checklist"
echo "□ Dashboard loads with metrics"
echo "□ Accounts tab shows sample data"
echo "□ Deals tab shows pipeline"
echo "□ Training Pipeline processes transcripts"
echo "□ Email Hub connects to Gmail"
echo "□ Chat sidebar responds to queries"
echo ""

# Step 8: End-to-End Scenarios
echo "🎯 Step 8: End-to-End Testing"
echo ""
echo "Scenario 1: Jennifer's Discovery Call"
echo "1. Go to Training Pipeline tab"
echo "2. Paste Jennifer's transcript (from story guide)"
echo "3. Click 'Process Transcript'"
echo "4. Verify entities extracted correctly"
echo "5. Check Deals tab for auto-created deal"
echo "6. Check Dashboard for updated metrics"
echo ""
echo "Scenario 2: Chat Intelligence"
echo "1. Use sidebar chat"
echo "2. Ask: 'What deals need attention?'"
echo "3. Ask: 'Create account called Test Corp'"
echo "4. Ask: 'What is our forecast?'"
echo "5. Verify intelligent responses"
echo ""
echo "Scenario 3: CRUD Operations"
echo "1. Create new account via UI"
echo "2. Create new deal via UI"
echo "3. Edit deal stage"
echo "4. Verify dashboard updates"
echo ""

# Step 9: Performance Testing
echo "⚡ Step 9: Performance Benchmarks"
echo ""
echo "# Test transcript processing speed"
echo 'time curl -X POST http://localhost:8000/analytics/process-transcript -H "Content-Type: application/json" -d '"'"'{"transcript": "Budget $1M timeline Q4"}'"'"
echo ""
echo "# Test dashboard response time"
echo "time curl http://localhost:8000/analytics/forecast"
echo ""
echo "# Test chat response time"
echo 'time curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "Show pipeline"}'"'"
echo ""

# Step 10: User Acceptance Testing
echo "👥 Step 10: User Acceptance Criteria"
echo ""
echo "Functional Requirements:"
echo "□ Transcript processing >90% accuracy"
echo "□ CRM auto-creation works correctly"
echo "□ Gmail integration sends real emails"
echo "□ Dashboard updates in real-time"
echo "□ Chat provides intelligent responses"
echo "□ Human feedback improves accuracy"
echo ""
echo "Performance Requirements:"
echo "□ Transcript processing <30 seconds"
echo "□ CRM updates <5 seconds"
echo "□ Email generation <10 seconds"
echo "□ Dashboard refresh <3 seconds"
echo ""
echo "Business Impact:"
echo "□ Saves 2+ hours per rep daily"
echo "□ Achieves >90% CRM accuracy"
echo "□ Enables <1 hour follow-up time"
echo "□ Delivers 15%+ revenue impact"
echo ""

echo "✅ Testing Complete!"
echo "If all tests pass, platform is ready for demo and production use."
