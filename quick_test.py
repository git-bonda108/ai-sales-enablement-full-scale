#!/usr/bin/env python3
"""
Quick validation test - ensures everything is working for the demo
"""

import requests
import sys
from colorama import init, Fore, Style

init()

API_BASE = "http://localhost:8000"

def check_service(name, url, expected_keys=None):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            if expected_keys:
                data = response.json()
                if all(key in str(data) for key in expected_keys):
                    print(f"{Fore.GREEN}✓ {name}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.YELLOW}⚠ {name} - Incomplete response{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.GREEN}✓ {name}{Style.RESET_ALL}")
                return True
        else:
            print(f"{Fore.RED}✗ {name} - Status: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ {name} - {str(e)}{Style.RESET_ALL}")
        return False

def main():
    print(f"{Fore.CYAN}AI Sales Platform - Quick Validation Test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

    all_good = True

    # Check core services
    all_good &= check_service("API Gateway", f"{API_BASE}/health", ["crm", "analytics"])
    all_good &= check_service("CRM Service", f"{API_BASE}/crm/accounts")
    all_good &= check_service("Analytics Service", f"{API_BASE}/analytics/performance")
    all_good &= check_service("AI Chat", f"{API_BASE}/v1/models")

    # Check UI
    ui_available = check_service("Streamlit UI", "http://localhost:8501")

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    if all_good and ui_available:
        print(f"{Fore.GREEN}✅ All systems operational!{Style.RESET_ALL}")
        print(f"\n📍 Access the platform at: {Fore.BLUE}http://localhost:8501{Style.RESET_ALL}")
        print(f"\n🚀 Ready for demo! Run: {Fore.YELLOW}python demo_scenario.py{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}❌ Some services are not ready{Style.RESET_ALL}")
        print(f"\nTroubleshooting:")
        print(f"1. Check Docker: {Fore.YELLOW}docker ps{Style.RESET_ALL}")
        print(f"2. View logs: {Fore.YELLOW}docker-compose logs{Style.RESET_ALL}")
        print(f"3. Restart: {Fore.YELLOW}docker-compose restart{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
