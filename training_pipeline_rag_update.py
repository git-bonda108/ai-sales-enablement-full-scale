
# ========== UPDATE TRAINING PIPELINE TO STORE IN RAG ==========

# Add this to the process_transcript endpoint in api_gateway.py:

@app.post("/training/process-transcript")
async def process_transcript(request: TranscriptRequest):
    """Process a transcript and extract entities"""
    try:
        # First, process with training server
        result = await mcp_training.call_tool(
            "process_transcript",
            {
                "content": request.content,
                "source": request.source
            }
        )
        training_result = json.loads(result) if isinstance(result, str) else result

        # Then, store in RAG system
        try:
            rag_result = await mcp_rag.call_tool(
                "store_transcript",
                {
                    "transcript_id": training_result["transcript_id"],
                    "content": request.content,
                    "entities": training_result["entities"],
                    "metadata": {
                        "source": request.source,
                        "suggestions_count": len(training_result["suggestions"])
                    }
                }
            )
            training_result["rag_stored"] = True
        except:
            training_result["rag_stored"] = False

        return training_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
