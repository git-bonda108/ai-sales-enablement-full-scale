# Evaluation

An honest account of what is tested today, what the code visibly handles, and what a real evaluation harness for this system should look like.

## What exists

### Test files

| File | How to run | What it actually covers |
|---|---|---|
| `tests/simple_test.py` | `uv run python tests/simple_test.py` | Spawns `servers.basic_server` as a subprocess and checks it starts and stays alive; prints the expected tool list. |
| `tests/test_basic_server.py` | `uv run python tests/test_basic_server.py` | Same start-up smoke test for the basic server via an MCP client session. |
| `tests/working_test.py` | `uv run python tests/working_test.py` | Three checks: server process starts, stays running, and the module imports cleanly. |
| `tests/working_crm_test.py` | `uv run python tests/working_crm_test.py` | Spawns `servers.crm_server`, confirms it starts, then *simulates* the six CRM tools' logic in-process (direct SQLite calls mirroring the tool bodies). |
| `tests/working_analytics_test.py` | `uv run python tests/working_analytics_test.py` | Same pattern for the analytics server. |
| `tests/test_crm_server.py`, `tests/test_analytics_server.py` | `uv run python tests/<file>` | MCP-client-based tool invocation scripts for the two FastMCP servers. |
| `tests/test_integration.py` | `uv run python tests/test_integration.py` (needs a gateway on :8000) | `assert`-based HTTP checks of gateway endpoints (`/health`, `/api/accounts`, `/api/analytics/dashboard`, …). |
| `tests/uv_test.py` | `uv run python tests/uv_test.py` | Environment sanity check for the uv toolchain. |
| `quick_test.py` | `uv run python quick_test.py` | Pre-demo probe: checks gateway endpoints respond on :8000 with expected keys. |
| `run_tests.sh` | `./run_tests.sh` | Interactive runner: quick validation, then full suite and/or demo scenario. |

There is no pytest suite, no CI configuration, and no coverage measurement in the repository. The test scripts are runnable demos with print-based verification; only `test_integration.py` uses hard `assert`s.

### Known mismatches (found by reading, worth fixing before trusting any green run)

- `tests/test_integration.py` asserts `health["connected"]` and `accounts["count"]`, but neither committed gateway returns those keys (`api_gateway_quick_fix.py` returns `{status, timestamp}` from `/health`; `api/api_gateway.py` returns `{status, services}`). The integration test was written against an earlier gateway surface.
- `api/api_gateway.py` line ~242 has an over-indented `return` in `/v1/models` — the file does not import as committed. `api/api_gateway_backup.py` and the quick-fix gateway are unaffected.
- `api/api_gateway.py` calls CRM tools `create_account` and `get_deals`, which `servers/crm_server.py` does not define (its six tools are listed in ARCHITECTURE.md). Those two routes would fail against the real server.
- `rag_server.py` and `training_server.py` register handlers on the object returned by `stdio_server()` at import time; this diverges from the documented low-level MCP server pattern, and no committed test or gateway exercises either server over the protocol.
- `sentence-transformers` (imported by `rag_server.py`) is not declared in `pyproject.toml` or any `requirements*.txt`; `chromadb` appears only in `requirements.txt`, not in `pyproject.toml`. `uv sync` alone does not produce an environment that can run the RAG server.

### Metrics that appear in the repo

The historical `*_REPORT.md` / `*_SUMMARY.md` files and the old README quoted figures such as response times, uptime percentages, and forecast accuracy. No committed benchmark or instrumentation produces those numbers, so they are not repeated here. The only measured values in code are the ones computed at runtime (e.g. token counts and the cost estimate in `ai_integration.py`, average extraction confidence in `training_server.get_training_metrics`).

## Edge cases the code visibly handles

Enumerated from the source, not from intention:

- **Missing LLM key / API failure:** `ai_integration.py` catches import errors, missing `OPENAI_API_KEY`, and per-call exceptions, downgrading to a keyword fallback and tagging responses with `status: fallback` (`_initialize_client`, `_test_connection`, `chat_completion`).
- **Malformed LLM output:** `process_transcript` wraps `json.loads` of the model response and substitutes a neutral default analysis on `JSONDecodeError`.
- **Timeouts:** `quick_test.py` uses a 3-second HTTP timeout per probe; `email_analyzer`/UI paths rely on `requests` defaults.
- **Empty / missing rows:** CRM `get_account_details` and `update_deal_stage` return `{"error": ...}` for unknown IDs; `get_pipeline_summary` guards divide-by-zero on win rate; analytics guards `statistics.variance` on single-sample data and `or 0` on NULL aggregates.
- **Entity parsing failures:** `generate_crm_suggestions` wraps amount parsing (`$1.2M` → float) in `try/except ValueError` and drops the suggestion rather than crashing; extraction results are deduplicated by `(type, value)`.
- **ChromaDB collection races:** `rag_server.py` wraps `create_collection` in try/except and falls back to `get_collection` for all three collections.
- **RAG tool errors:** every tool call in `rag_server.handle_call_tool` is wrapped, returning a structured `{"error", "tool"}` payload instead of raising.
- **Gmail token refresh:** `gmail_client.py` and `gmail_integration.py` refresh expired credentials when a refresh token exists, and surface an explicit error when `credentials.json` is absent rather than crashing.

Not handled (also visible in code): no retry/backoff anywhere, no request-level timeout on gateway→MCP calls, no circuit breaker around OpenAI beyond the one-shot fallback, and no input validation on the mock gateway's `dict`-typed POST bodies.

## Proposed evaluation harness

No harness exists today. The one this system should have, sized to what the code does:

**1. Golden dataset**
- ~50 fictional sales-call transcripts with hand-labeled entities (`company`, `person`, `amount`, `timeline`, `email`, `phone`) and the expected `crm_suggestions` (type + normalized amount). Shape: JSONL, one record per transcript — `{transcript, entities: [...], suggestions: [...]}` — stored under `tests/golden/`.
- ~30 chat prompts with the expected route (CRM lookup / forecast / email draft / fallback) to pin the gateway's routing behavior.
- ~20 retrieval queries against a fixed seeded ChromaDB with expected top-k document IDs.

**2. Deterministic unit layer (pytest)**
- Direct calls to the CRM/Analytics tool functions against a fixture SQLite database (the FastMCP tools are plain functions — no protocol needed).
- `extract_entities` and `generate_crm_suggestions` against the golden transcripts: precision/recall per entity type; amount-normalization exactness.
- `EmailAnalyzer` intent classification against labeled emails.

**3. Protocol layer**
- Spawn each MCP server over stdio, `list_tools`, and round-trip one call per tool, asserting schema-conformant JSON. This layer would have caught every mismatch listed above.

**4. Gates and metrics**
- CI (e.g. GitHub Actions) running layers 2–3 on every push; a green run requires: import of every committed Python module, entity extraction F1 ≥ a recorded baseline (measure first, then ratchet — do not invent a target), 100% of gateway routes returning the documented shape, retrieval hit-rate@5 ≥ baseline on the fixed corpus.
- LLM-dependent paths tested with recorded responses (or the built-in fallback mode, which is deterministic by design) so CI needs no API key; a separate opt-in job with a real key samples live-model behavior.
