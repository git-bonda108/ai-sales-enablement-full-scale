#!/usr/bin/env python3
"""
Training MCP Server - Handles transcript processing, entity extraction, and feedback
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sqlite3
import os

# Initialize database for training data
DB_PATH = "training_data.db"

def init_training_db():
    """Initialize training database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Transcripts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            processed_at TIMESTAMP,
            source TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

    # Extracted entities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript_id INTEGER,
            entity_type TEXT,
            entity_value TEXT,
            confidence REAL,
            context TEXT,
            FOREIGN KEY(transcript_id) REFERENCES transcripts(id)
        )
    """)

    # Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER,
            original_value TEXT,
            corrected_value TEXT,
            feedback_type TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY(entity_id) REFERENCES extracted_entities(id)
        )
    """)

    # Training suggestions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript_id INTEGER,
            suggestion_type TEXT,
            suggestion_data JSON,
            confidence REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP,
            FOREIGN KEY(transcript_id) REFERENCES transcripts(id)
        )
    """)

    conn.commit()
    conn.close()

# Initialize database
init_training_db()

# Entity extraction patterns (simplified for demo)
ENTITY_PATTERNS = {
    "company": [
        r"(?:company|client|customer|account)(?:\s+(?:is|called|named))?\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)",
        r"([A-Z][A-Za-z]+(?:\s+(?:Corp|Inc|LLC|Ltd|Corporation|Company|Industries|Tech|Technologies))?)",
        r"(?:at|with|from)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
    ],
    "person": [
        r"(?:speaking with|talking to|meeting with|contact is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:is the|from|at)",
        r"(?:I'm|I am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
    ],
    "amount": [
        r"\$([0-9,]+(?:\.[0-9]{2})?)[kKmM]?",
        r"([0-9,]+(?:\.[0-9]{2})?)\s*(?:dollars|USD)",
        r"(?:budget|deal size|opportunity).*?\$([0-9,]+(?:\.[0-9]{2})?)[kKmM]?"
    ],
    "timeline": [
        r"(?:by|before|in)\s+(Q[1-4]\s+20\d{2})",
        r"(?:timeline|timeframe|deadline).*?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+20\d{2})",
        r"(?:next|this|coming)\s+(quarter|month|year)"
    ],
    "email": [
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r"email.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    ],
    "phone": [
        r"(\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})",
        r"(?:phone|call|mobile|cell).*?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})"
    ]
}

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract entities from text using regex patterns"""
    entities = []

    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1)
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                # Calculate confidence based on pattern strength
                confidence = 0.85 if match.group(0).lower() in text.lower() else 0.65

                entities.append({
                    "type": entity_type,
                    "value": value.strip(),
                    "confidence": confidence,
                    "context": context.strip()
                })

    # Deduplicate entities
    seen = set()
    unique_entities = []
    for entity in entities:
        key = (entity["type"], entity["value"].lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)

    return unique_entities

def generate_crm_suggestions(transcript_id: int, entities: List[Dict]) -> List[Dict]:
    """Generate CRM update suggestions based on extracted entities"""
    suggestions = []

    # Group entities by type
    companies = [e for e in entities if e["type"] == "company"]
    people = [e for e in entities if e["type"] == "person"]
    amounts = [e for e in entities if e["type"] == "amount"]
    timelines = [e for e in entities if e["type"] == "timeline"]
    emails = [e for e in entities if e["type"] == "email"]

    # Suggest account creation/update
    for company in companies:
        if company["confidence"] > 0.7:
            suggestions.append({
                "type": "create_account",
                "data": {
                    "name": company["value"],
                    "source": "transcript",
                    "confidence": company["confidence"]
                },
                "confidence": company["confidence"]
            })

    # Suggest contact creation
    for i, person in enumerate(people):
        if person["confidence"] > 0.6:
            # Try to match with company
            matched_company = companies[0]["value"] if companies else "Unknown"

            # Check for associated email
            person_email = emails[i]["value"] if i < len(emails) else None

            suggestions.append({
                "type": "create_contact",
                "data": {
                    "name": person["value"],
                    "company": matched_company,
                    "email": person_email,
                    "confidence": person["confidence"]
                },
                "confidence": person["confidence"]
            })

    # Suggest deal creation
    if amounts and companies:
        deal_amount = amounts[0]["value"].replace(",", "").replace("$", "")
        # Convert k/m to actual numbers
        multiplier = 1
        if deal_amount.lower().endswith('k'):
            multiplier = 1000
            deal_amount = deal_amount[:-1]
        elif deal_amount.lower().endswith('m'):
            multiplier = 1000000
            deal_amount = deal_amount[:-1]

        try:
            amount_value = float(deal_amount) * multiplier

            suggestions.append({
                "type": "create_deal",
                "data": {
                    "name": f"{companies[0]['value']} Opportunity",
                    "amount": amount_value,
                    "company": companies[0]["value"],
                    "timeline": timelines[0]["value"] if timelines else "Q2 2024",
                    "confidence": min(companies[0]["confidence"], amounts[0]["confidence"])
                },
                "confidence": min(companies[0]["confidence"], amounts[0]["confidence"])
            })
        except ValueError:
            pass

    return suggestions

# MCP Server setup
server = stdio_server()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available training tools"""
    return [
        Tool(
            name="process_transcript",
            description="Process a sales transcript and extract entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Transcript content"},
                    "source": {"type": "string", "description": "Source of transcript (upload/audio)"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="get_suggestions",
            description="Get CRM update suggestions for a transcript",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_id": {"type": "integer", "description": "ID of processed transcript"}
                },
                "required": ["transcript_id"]
            }
        ),
        Tool(
            name="submit_feedback",
            description="Submit feedback on entity extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "integer", "description": "ID of entity"},
                    "corrected_value": {"type": "string", "description": "Corrected value"},
                    "feedback_type": {"type": "string", "description": "Type of feedback"}
                },
                "required": ["entity_id", "corrected_value"]
            }
        ),
        Tool(
            name="get_training_metrics",
            description="Get training pipeline metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        if name == "process_transcript":
            # Store transcript
            cursor.execute(
                "INSERT INTO transcripts (content, source, processed_at, status) VALUES (?, ?, ?, ?)",
                (arguments["content"], arguments.get("source", "upload"), datetime.now(), "processing")
            )
            transcript_id = cursor.lastrowid

            # Extract entities
            entities = extract_entities(arguments["content"])

            # Store entities
            for entity in entities:
                cursor.execute(
                    "INSERT INTO extracted_entities (transcript_id, entity_type, entity_value, confidence, context) VALUES (?, ?, ?, ?, ?)",
                    (transcript_id, entity["type"], entity["value"], entity["confidence"], entity["context"])
                )

            # Generate CRM suggestions
            suggestions = generate_crm_suggestions(transcript_id, entities)

            # Store suggestions
            for suggestion in suggestions:
                cursor.execute(
                    "INSERT INTO crm_suggestions (transcript_id, suggestion_type, suggestion_data, confidence, created_at) VALUES (?, ?, ?, ?, ?)",
                    (transcript_id, suggestion["type"], json.dumps(suggestion["data"]), suggestion["confidence"], datetime.now())
                )

            # Update transcript status
            cursor.execute(
                "UPDATE transcripts SET status = ? WHERE id = ?",
                ("processed", transcript_id)
            )

            conn.commit()

            result = {
                "transcript_id": transcript_id,
                "entities_found": len(entities),
                "suggestions_generated": len(suggestions),
                "entities": entities,
                "suggestions": suggestions
            }

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_suggestions":
            transcript_id = arguments["transcript_id"]

            # Get suggestions
            cursor.execute(
                "SELECT * FROM crm_suggestions WHERE transcript_id = ?",
                (transcript_id,)
            )
            suggestions = []
            for row in cursor.fetchall():
                suggestions.append({
                    "id": row["id"],
                    "type": row["suggestion_type"],
                    "data": json.loads(row["suggestion_data"]),
                    "confidence": row["confidence"],
                    "status": row["status"]
                })

            return [TextContent(type="text", text=json.dumps(suggestions, indent=2))]

        elif name == "submit_feedback":
            # Store feedback
            cursor.execute(
                "INSERT INTO feedback (entity_id, original_value, corrected_value, feedback_type, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    arguments["entity_id"],
                    arguments.get("original_value", ""),
                    arguments["corrected_value"],
                    arguments.get("feedback_type", "correction"),
                    datetime.now()
                )
            )
            conn.commit()

            return [TextContent(type="text", text=json.dumps({"status": "feedback_recorded"}))]

        elif name == "get_training_metrics":
            # Get metrics
            cursor.execute("SELECT COUNT(*) as count FROM transcripts WHERE status = 'processed'")
            transcripts_processed = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM extracted_entities")
            entities_extracted = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM feedback")
            feedback_count = cursor.fetchone()["count"]

            cursor.execute("SELECT AVG(confidence) as avg_conf FROM extracted_entities")
            avg_confidence = cursor.fetchone()["avg_conf"] or 0

            metrics = {
                "transcripts_processed": transcripts_processed,
                "entities_extracted": entities_extracted,
                "feedback_received": feedback_count,
                "average_confidence": round(avg_confidence, 2),
                "model_version": "v1.0"
            }

            return [TextContent(type="text", text=json.dumps(metrics, indent=2))]

    finally:
        conn.close()

async def main():
    """Run the training server"""
    async with server:
        init_options = InitializationOptions(
            server_name="training-server",
            server_version="0.1.0"
        )
        await server.run(init_options)

if __name__ == "__main__":
    asyncio.run(main())
