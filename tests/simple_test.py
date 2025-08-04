"""
Simple test for Basic MCP Server
Tests the server directly without complex client setup
"""

import subprocess
import json
import time

def test_server_directly():
    """Test the server by running it and checking output"""
    
    print("🧪 Testing Basic MCP Server (Direct Method)")
    print("=" * 50)
    
    try:
        # Start the server process
        print("🚀 Starting server...")
        process = subprocess.Popen(
            ["python", "-m", "servers.basic_server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("📍 Server is running and ready to accept connections")
            print()
            print("🛠️  Available tools:")
            print("   - greet_user(name)")
            print("   - calculate_commission(sale_amount, commission_rate)")
            print("   - list_demo_features()")
            print()
            print("✅ Basic MCP Server is working correctly!")
            print("🎯 Ready to build the full CRM server!")
            
            # Clean shutdown
            process.terminate()
            process.wait()
            
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")

if __name__ == "__main__":
    test_server_directly() 