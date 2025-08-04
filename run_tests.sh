#!/bin/bash
# Test Runner - Execute all tests and demo

echo "🧪 AI Sales Platform - Test Runner"
echo "=================================="

# Quick validation
echo -e "\n📋 Running quick validation..."
python quick_test.py

if [ $? -ne 0 ]; then
    echo "❌ Quick validation failed. Please fix issues before running full tests."
    exit 1
fi

# Ask user what to run
echo -e "\n🚀 What would you like to run?"
echo "1) Full Test Suite (comprehensive)"
echo "2) Demo Scenario (interactive)"
echo "3) Both"
echo -n "Enter choice (1-3): "
read choice

case $choice in
    1)
        echo -e "\n🧪 Running full test suite..."
        python test_suite.py
        ;;
    2)
        echo -e "\n🎬 Starting demo scenario..."
        python demo_scenario.py
        ;;
    3)
        echo -e "\n🧪 Running full test suite..."
        python test_suite.py
        echo -e "\n🎬 Starting demo scenario..."
        python demo_scenario.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
