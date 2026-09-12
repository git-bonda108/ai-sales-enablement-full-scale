# Architecture

## Component map

| Component | File(s) | Responsibility |
|---|---|---|
| Streamlit UI | `beautiful_streamlit_app.py` (primary), `ui/streamlit_app.py`, `streamlit_fixed.py`, `streamlit_ui_fixed.py` (variants) | Dashboard, AI chat, CRM forms, Gmail panel, transcript upload. Talks HTTP to `http://localhost:8000`. |
| Demo gateway | `api_gateway_quick_fix.py` | Self-contained FastAPI app returning mock data for every endpoint the UI calls (`/health`, `/api/metrics`, `/crm/*`, `/v1/chat/completions`, `/integrations/gmail/*`, `/ai/process-transcript`). |
| MCP gateway | `api/api_gateway.py` | FastAPI app that spawns the CRM and Analytics MCP servers as stdio subprocesses at startup and forwards HTTP requests as MCP tool calls. Also exposes an OpenAI-compatible `/v1/chat/completions` with keyword routing. |
| CRM MCP server | `servers/crm_server.py` (copies: `crm_server.py`, `src/crm_server.py`) | FastMCP server, 6 tools: `search_accounts`, `get_account_details`, `create_deal`, `update_deal_stage`, `get_pipeline_summary`, `list_all_accounts`. SQLite at `data/sales_crm.db`. |
| Analytics MCP server | `servers/analytics_server.py` (copies at root and `src/`) | FastMCP server, 5 tools: `generate_sales_forecast`, `analyze_conversion_rates`, `calculate_deal_scoring`, `get_activity_analytics`, `get_performance_metrics`. Shares `data/sales_crm.db` with the CRM server. |
| RAG MCP server | `rag_server.py` | Low-level MCP stdio server, 5 tools: `store_transcript`, `search_similar`, `get_automation_decision`, `store_outcome`, `get_context_for_chat`. ChromaDB persistent store at `./chroma_db`, embeddings via SentenceTransformers `all-MiniLM-L6-v2`. |
| Training MCP server | `training_server.py` | Low-level MCP stdio server, 4 tools: `process_transcript`, `get_suggestions`, `submit_feedback`, `get_training_metrics`. Regex-based entity extraction; SQLite at `training_data.db`. |
| Basic MCP server | `servers/basic_server.py` | Proof-of-concept FastMCP server (`greet_user`, `calculate_commission`, `list_demo_features`) used to validate the MCP toolchain. |
| MCP client library | `client/mcp_client.py` | `MCPSalesClient`: manages stdio sessions to the CRM and Analytics servers and composes multi-server reads (`get_account_360`, `get_pipeline_dashboard`, `create_and_score_deal`, `get_sales_insights`). Module-level singleton via `get_client()`. |
| LLM integration | `ai_integration.py` | OpenAI `gpt-3.5-turbo` wrapper with context-typed system prompts (`deal_analysis`, `email_generation`, `transcript_analysis`), token/cost accounting, and a deterministic fallback mode. |
| Gmail integration | `gmail_client.py`, `gmail_integration.py`, `config/gmail_config.py`, `gmail_streamlit_cloud.py` | Google OAuth (InstalledAppFlow, `credentials.json` + cached token), unread fetch, send, mark-read. The Streamlit-Cloud variant reads OAuth material from `st.secrets`. |
| Email analysis | `email_analyzer.py` | Rule-based buying-signal scoring, intent classification (hot/warm/lukewarm/cold), question and objection extraction, response suggestion. |
| Voice mock | `voice_mock.py` (copy: `src/voice_gateway.py`) | Scripted "live call" transcript generator with keyword sentiment and call analytics — a stand-in for a real telephony/STT gateway. |
| Integrations API | `src/integration_server.py` | FastAPI endpoints wiring Gmail, the email analyzer, and the voice mock (`/integrations/gmail/*`, `/integrations/voice/*`, `/integrations/status|health|debug`). |
| Data seeding | `init_crm_db.py`, `generate_demo_data.py`, `story_demo_data_generator.py`, `demo_scenario.py` | Create and populate the demo SQLite databases with fictional accounts, deals, and activities. |

## Data flow, end to end

1. **User action** in the Streamlit UI produces an HTTP request to the gateway on port 8000 (`requests.get/post` in `beautiful_streamlit_app.py`).
2. **Gateway routing.** In `api/api_gateway.py`, CRM and analytics routes call `MCPClient.call_tool(...)`, which serializes the request over stdio to the subprocess MCP server. In the quickstart demo gateway, the same routes return canned mock payloads.
3. **Tool execution.** The MCP server runs a parameterized SQLite query (CRM/Analytics) or a ChromaDB similarity query (RAG) and returns JSON `TextContent`.
4. **Chat path.** `/v1/chat/completions` inspects the last user message with keyword checks (`account`, `forecast`, `pipeline`, `email` + `draft`, …) and either returns a canned response block or — through `ai_integration.py` when configured — calls `gpt-3.5-turbo` with a context-typed system prompt.
5. **Transcript path.** A transcript is stored in `training_data.db`, run through the regex extractors (`company`, `person`, `amount`, `timeline`, `email`, `phone`), and turned into `crm_suggestions` rows (create-account / create-contact / create-deal) with per-entity confidence. The RAG server can then embed the transcript and its entities into ChromaDB, where they become retrieval context for later chat and automation decisions.
6. **Feedback loop.** `submit_feedback` records corrections against extracted entities; `store_outcome` writes action outcomes into the `knowledge` collection, where the success rate of similar past cases boosts future confidence (up to +10%) in `get_automation_decision`.

## Orchestration analysis: what runs where, and why

- **Process topology.** One HTTP gateway process; each MCP server is a separate OS subprocess speaking MCP over stdio. This is MCP's standard local topology and gives clean crash isolation between tool domains at zero network cost.
- **Sequential composition.** Composite operations in `client/mcp_client.py` await each tool call in turn — `get_account_360` fetches CRM details, then deal scores; `get_pipeline_dashboard` fetches pipeline, then forecast, then metrics. The calls are independent and could run under `asyncio.gather`, but sequential awaits keep the demo simple and make failures attributable to a single step.
- **Async where it matters.** The gateway and MCP servers are `async` end to end (FastAPI + MCP async sessions), so the single gateway process can multiplex UI requests while a tool call is in flight.
- **No agent loop.** There is no planner, no multi-turn tool-use loop, and no model-driven tool selection: routing is keyword-based in the gateway, and each LLM call is single-shot. The "agentic" element is the progressive-autonomy gate in `rag_server.py`, which decides — from numeric confidence plus retrieved historical outcomes — whether an action is auto-executed, suggested for review, or deferred to a human.

## State and context engineering

- **Stores.** `data/sales_crm.db` (accounts, contacts, deals, activities) is shared by the CRM and Analytics servers — one source of truth, two tool surfaces. `training_data.db` holds transcripts, extracted entities, feedback, and CRM suggestions. `./chroma_db` persists the three vector collections. Root-level `sales_platform.db` / `sales_ai_platform.db` are committed demo snapshots from earlier iterations.
- **Context assembly.** `ai_integration.py` builds the LLM prompt from a static role prompt plus a context-type section; for deal analysis it inlines a one-line-per-deal digest of the cached CRM context. `rag_server.get_context_for_chat` bounds retrieval context explicitly: top-3 transcript hits truncated to 500 characters each, plus top-2 deal hits.
- **Bounded generation.** `max_tokens=1000` (chat), `temperature=0.7`, with per-call token counts and a rough cost estimate returned alongside every response.
- **Statelessness.** Neither gateway keeps conversation history; the UI holds transient state in Streamlit session state. This is a deliberate demo simplification — see "Extending this system".

## Design decisions and trade-offs visible in the code

1. **Mock-first demo path.** `api_gateway_quick_fix.py` duplicates the gateway surface with static data so the UI demos without subprocess management, a seeded database, or an API key. Trade-off: two gateway implementations to keep in sync, and the quickstart exercises none of the real MCP wiring.
2. **Graceful LLM degradation.** `ai_integration.py` tests the OpenAI connection at startup and downgrades to keyword-matched fallback responses on any failure, tagging every response with `available`/`fallback` status. The demo never hard-fails on a missing key; the cost is that fallback output can be mistaken for model output if the status field is ignored.
3. **Two MCP server styles.** CRM/Analytics use FastMCP decorators (concise, typed, auto-schema); RAG/Training use the low-level `mcp.server` API with hand-written `Tool` schemas. The contrast is instructive, but the low-level pair registers handlers on the object returned by `stdio_server()` at module import — a wiring that diverges from the documented low-level pattern and is not exercised by any committed gateway or test (see EVALUATION).
4. **Regex before ML.** Entity extraction is deliberately rule-based with per-pattern confidence, and the schema (`feedback`, `crm_suggestions`, confidence thresholds) is designed so a learned extractor can replace the regexes without changing the pipeline contract.
5. **Duplicated modules over packaging.** Byte-identical copies of servers/clients exist at the root, in `servers/`, and in `src/` to satisfy flat-import deployment (Streamlit Cloud) without wheel installation. Trade-off accepted for demo portability; consolidation is a known cleanup.
6. **Shared SQLite between two servers.** CRM writes and Analytics reads target the same file. Fine at demo scale under SQLite's locking; a real deployment would move to a served database (the `docker-compose.yml` sketch already names PostgreSQL).

## Extending this system

Grounded next steps that the current structure makes straightforward:

1. **Wire the RAG and Training servers into the gateway.** `api/api_gateway.py` already demonstrates the `MCPClient` pattern for CRM/Analytics; registering the other two servers the same way (after porting them to FastMCP, which CRM/Analytics prove out) would replace the mock `/ai/process-transcript` endpoint with the real pipeline in one place.
2. **Replace keyword chat routing with model-driven tool use.** The MCP servers already publish typed tool schemas; passing those schemas to the LLM as function/tool definitions would turn the gateway's `if "forecast" in message` blocks into genuine tool selection, with `client/mcp_client.py` as the execution layer.
3. **Parallelize composite reads.** `get_pipeline_dashboard` and `get_sales_insights` issue independent tool calls; converting sequential awaits to `asyncio.gather` is a contained change with immediate latency benefit once real servers back the endpoints.
4. **Close the autonomy loop end to end.** `get_automation_decision` and `store_outcome` exist but nothing calls them from the request path. Routing high-confidence `crm_suggestions` through the autonomy gate — auto-applying only above the 0.90 threshold and logging the audit entry it already produces — would make the progressive-autonomy design operational rather than latent.
5. **Promote the feedback data into a trained extractor.** The `feedback` and `extracted_entities` tables accumulate exactly the labeled pairs needed to fine-tune or few-shot an NER replacement for the regex patterns; the confidence field already flows through suggestions, so a better extractor improves automation rates without schema changes.
