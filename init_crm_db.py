"""
Initialize CRM database with schema and sample data
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Database path
DB_PATH = os.path.join("data", "sales_crm.db")

def init_database():
    """Initialize database with schema and sample data"""

    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            annual_revenue REAL,
            employees INTEGER,
            website TEXT,
            created_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            name TEXT NOT NULL,
            title TEXT,
            email TEXT,
            phone TEXT,
            is_primary BOOLEAN,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            name TEXT NOT NULL,
            amount REAL,
            stage TEXT,
            close_date TEXT,
            probability INTEGER,
            created_date TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            activity_type TEXT,
            description TEXT,
            activity_date TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)

    # Sample data
    accounts = [
        ("Acme Corporation", "Technology", 50000000, 500, "acme.com"),
        ("Global Dynamics", "Manufacturing", 100000000, 2000, "globaldynamics.com"),
        ("TechStart Inc", "Software", 5000000, 50, "techstart.io"),
        ("Enterprise Solutions", "Consulting", 25000000, 200, "enterprise-sol.com"),
        ("CloudFirst", "Cloud Services", 15000000, 150, "cloudfirst.com"),
        ("DataDrive Systems", "Analytics", 30000000, 300, "datadrive.com"),
        ("SecureNet", "Cybersecurity", 20000000, 180, "securenet.com"),
        ("InnovateTech", "AI/ML", 8000000, 80, "innovatetech.ai"),
        ("FinanceForward", "Financial Services", 75000000, 1000, "financeforward.com"),
        ("HealthTech Solutions", "Healthcare", 40000000, 400, "healthtech.com")
    ]

    # Insert accounts
    for account in accounts:
        cursor.execute("""
            INSERT INTO accounts (name, industry, annual_revenue, employees, website, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (*account, datetime.now().strftime("%Y-%m-%d")))

    # Insert contacts (2-3 per account)
    titles = ["CEO", "CTO", "VP Sales", "Director of IT", "CFO", "Head of Operations"]
    for i in range(1, 11):  # 10 accounts
        for j in range(random.randint(2, 3)):
            cursor.execute("""
                INSERT INTO contacts (account_id, name, title, email, phone, is_primary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                i,
                f"Contact {i}-{j+1}",
                random.choice(titles),
                f"contact{i}{j}@{accounts[i-1][4]}",
                f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                j == 0
            ))

    # Insert deals
    stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    deal_names = ["Software License", "Implementation Services", "Annual Subscription", "Consulting Project", "Platform Migration", "Security Audit"]

    for i in range(1, 11):  # For each account
        num_deals = random.randint(1, 4)
        for j in range(num_deals):
            stage = random.choice(stages)
            amount = random.randint(10000, 500000)
            probability = {
                "Prospecting": 10,
                "Qualification": 20,
                "Proposal": 40,
                "Negotiation": 60,
                "Closed Won": 100,
                "Closed Lost": 0
            }.get(stage, 50)

            close_date = datetime.now() + timedelta(days=random.randint(30, 180))

            cursor.execute("""
                INSERT INTO deals (account_id, name, amount, stage, close_date, probability, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                i,
                f"{random.choice(deal_names)} - Q{random.randint(1,4)}",
                amount,
                stage,
                close_date.strftime("%Y-%m-%d"),
                probability,
                (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
            ))

    # Insert activities
    activity_types = ["Email", "Call", "Meeting", "Demo", "Proposal Sent", "Follow-up"]

    for i in range(1, 11):  # For each account
        num_activities = random.randint(3, 8)
        for j in range(num_activities):
            cursor.execute("""
                INSERT INTO activities (account_id, activity_type, description, activity_date)
                VALUES (?, ?, ?, ?)
            """, (
                i,
                random.choice(activity_types),
                f"Sales activity for {accounts[i-1][0]}",
                (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
            ))

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")
    print(f"📍 Location: {DB_PATH}")
    print(f"📊 Data created:")
    print(f"   - 10 Accounts")
    print(f"   - ~25 Contacts")
    print(f"   - ~20 Deals")
    print(f"   - ~50 Activities")

if __name__ == "__main__":
    init_database()
