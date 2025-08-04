#!/usr/bin/env python3
"""
RAG MCP Server - Handles embeddings, vector search, and knowledge retrieval
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False)
)

# Initialize embedding model
print("Loading embedding model...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")

# Create collections
try:
    transcripts_collection = chroma_client.create_collection(
        name="transcripts",
        metadata={"description": "Sales call transcripts and extracted entities"}
    )
except:
    transcripts_collection = chroma_client.get_collection("transcripts")

try:
    deals_collection = chroma_client.create_collection(
        name="deals",
        metadata={"description": "Historical deals and outcomes"}
    )
except:
    deals_collection = chroma_client.get_collection("deals")

try:
    knowledge_collection = chroma_client.create_collection(
        name="knowledge",
        metadata={"description": "Sales knowledge and best practices"}
    )
except:
    knowledge_collection = chroma_client.get_collection("knowledge")

# Progressive autonomy configuration
AUTONOMY_CONFIG = {
    "high_confidence_threshold": 0.90,      # Auto-execute
    "medium_confidence_threshold": 0.70,    # Suggest with review
    "low_confidence_threshold": 0.50,       # Human required
    "similarity_threshold": 0.85            # For finding similar deals
}

# MCP Server setup
server = stdio_server()

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text"""
    embedding = embedder.encode(text)
    return embedding.tolist()

def calculate_confidence_with_context(base_confidence: float, similar_cases: List[Dict]) -> float:
    """Adjust confidence based on similar historical cases"""
    if not similar_cases:
        return base_confidence

    # Boost confidence if we have successful similar cases
    success_rate = sum(1 for case in similar_cases if case.get("outcome") == "success") / len(similar_cases)
    context_boost = success_rate * 0.1  # Max 10% boost

    return min(base_confidence + context_boost, 1.0)

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available RAG tools"""
    return [
        Tool(
            name="store_transcript",
            description="Store a transcript with embeddings in the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_id": {"type": "integer"},
                    "content": {"type": "string"},
                    "entities": {"type": "array"},
                    "metadata": {"type": "object"}
                },
                "required": ["transcript_id", "content"]
            }
        ),
        Tool(
            name="search_similar",
            description="Search for similar transcripts or deals",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "collection": {"type": "string", "enum": ["transcripts", "deals", "knowledge"]},
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_automation_decision",
            description="Get automation decision based on confidence and context",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "context": {"type": "string"},
                    "similar_cases": {"type": "array"}
                },
                "required": ["action_type", "confidence", "context"]
            }
        ),
        Tool(
            name="store_outcome",
            description="Store the outcome of an action for learning",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_id": {"type": "string"},
                    "action_type": {"type": "string"},
                    "outcome": {"type": "string", "enum": ["success", "failure", "partial"]},
                    "feedback": {"type": "string"}
                },
                "required": ["action_id", "outcome"]
            }
        ),
        Tool(
            name="get_context_for_chat",
            description="Get relevant context for AI chat responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "include_transcripts": {"type": "boolean", "default": True},
                    "include_deals": {"type": "boolean", "default": True}
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "store_transcript":
            # Generate embedding for transcript
            embedding = generate_embedding(arguments["content"])

            # Store in ChromaDB
            transcripts_collection.add(
                embeddings=[embedding],
                documents=[arguments["content"]],
                metadatas=[{
                    "transcript_id": arguments["transcript_id"],
                    "entities": json.dumps(arguments.get("entities", [])),
                    "timestamp": datetime.now().isoformat(),
                    **arguments.get("metadata", {})
                }],
                ids=[f"transcript_{arguments['transcript_id']}"]
            )

            # Extract and store individual entities
            for entity in arguments.get("entities", []):
                entity_text = f"{entity['type']}: {entity['value']} (context: {entity.get('context', '')})"
                entity_embedding = generate_embedding(entity_text)

                knowledge_collection.add(
                    embeddings=[entity_embedding],
                    documents=[entity_text],
                    metadatas=[{
                        "transcript_id": arguments["transcript_id"],
                        "entity_type": entity["type"],
                        "entity_value": entity["value"],
                        "confidence": entity.get("confidence", 0.5)
                    }],
                    ids=[f"entity_{arguments['transcript_id']}_{entity['type']}_{entity['value']}"]
                )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "stored",
                    "transcript_id": arguments["transcript_id"],
                    "entities_stored": len(arguments.get("entities", []))
                })
            )]

        elif name == "search_similar":
            # Generate embedding for query
            query_embedding = generate_embedding(arguments["query"])

            # Search in specified collection
            collection_name = arguments.get("collection", "transcripts")
            collection = {
                "transcripts": transcripts_collection,
                "deals": deals_collection,
                "knowledge": knowledge_collection
            }[collection_name]

            # Perform similarity search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=arguments.get("top_k", 5)
            )

            # Format results
            similar_items = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    similar_items.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "similarity": 1 - (results["distances"][0][i] if results["distances"] else 0)
                    })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "query": arguments["query"],
                    "collection": collection_name,
                    "results": similar_items,
                    "count": len(similar_items)
                })
            )]

        elif name == "get_automation_decision":
            base_confidence = arguments["confidence"]
            similar_cases = arguments.get("similar_cases", [])

            # Adjust confidence based on historical context
            adjusted_confidence = calculate_confidence_with_context(base_confidence, similar_cases)

            # Determine automation level
            if adjusted_confidence >= AUTONOMY_CONFIG["high_confidence_threshold"]:
                decision = "auto_execute"
                reason = f"High confidence ({adjusted_confidence:.0%}) with {len(similar_cases)} similar successful cases"
            elif adjusted_confidence >= AUTONOMY_CONFIG["medium_confidence_threshold"]:
                decision = "suggest_review"
                reason = f"Medium confidence ({adjusted_confidence:.0%}) - human review recommended"
            else:
                decision = "human_required"
                reason = f"Low confidence ({adjusted_confidence:.0%}) - human decision required"

            # Create audit entry
            audit_entry = {
                "action_type": arguments["action_type"],
                "base_confidence": base_confidence,
                "adjusted_confidence": adjusted_confidence,
                "similar_cases_count": len(similar_cases),
                "decision": decision,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }

            return [TextContent(
                type="text",
                text=json.dumps({
                    "decision": decision,
                    "confidence": adjusted_confidence,
                    "reason": reason,
                    "audit": audit_entry
                })
            )]

        elif name == "store_outcome":
            # Store outcome for future learning
            outcome_text = f"Action: {arguments.get('action_type', 'unknown')} - Outcome: {arguments['outcome']}"
            outcome_embedding = generate_embedding(outcome_text)

            knowledge_collection.add(
                embeddings=[outcome_embedding],
                documents=[outcome_text],
                metadatas=[{
                    "action_id": arguments["action_id"],
                    "action_type": arguments.get("action_type", "unknown"),
                    "outcome": arguments["outcome"],
                    "feedback": arguments.get("feedback", ""),
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[f"outcome_{arguments['action_id']}"]
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "outcome_stored",
                    "action_id": arguments["action_id"]
                })
            )]

        elif name == "get_context_for_chat":
            # Get relevant context for AI chat
            query_embedding = generate_embedding(arguments["query"])

            context_items = []

            # Search transcripts
            if arguments.get("include_transcripts", True):
                transcript_results = transcripts_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )

                if transcript_results["documents"] and transcript_results["documents"][0]:
                    for i, doc in enumerate(transcript_results["documents"][0]):
                        context_items.append({
                            "type": "transcript",
                            "content": doc[:500] + "..." if len(doc) > 500 else doc,
                            "metadata": transcript_results["metadatas"][0][i] if transcript_results["metadatas"] else {}
                        })

            # Search deals
            if arguments.get("include_deals", True):
                deal_results = deals_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=2
                )

                if deal_results["documents"] and deal_results["documents"][0]:
                    for i, doc in enumerate(deal_results["documents"][0]):
                        context_items.append({
                            "type": "deal",
                            "content": doc,
                            "metadata": deal_results["metadatas"][0][i] if deal_results["metadatas"] else {}
                        })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "query": arguments["query"],
                    "context_items": context_items,
                    "total_items": len(context_items)
                })
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name
            })
        )]

async def main():
    """Run the RAG server"""
    async with server:
        init_options = InitializationOptions(
            server_name="rag-server",
            server_version="0.1.0"
        )
        await server.run(init_options)

if __name__ == "__main__":
    asyncio.run(main())
