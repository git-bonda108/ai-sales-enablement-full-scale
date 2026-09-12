# Hardening

Current security and operational posture, and a staged ladder to production. Grounded in what the code is: a local-first demo with mock surfaces.

## Current posture

**Authentication / authorization**
- No authentication on either FastAPI gateway; every endpoint is anonymous. CORS is `allow_origins=["*"]` with `allow_credentials=True` in both gateways.
- Gmail uses per-user Google OAuth (InstalledAppFlow) with git-ignored `credentials.json` and cached token files — the one correctly-scoped credential flow in the repo.
- `pyjwt` and `bcrypt` are declared in `pyproject.toml`, and `sales_ai_platform.db` contains empty `users`/`sessions` tables, but no auth code path uses them yet.

**Secrets handling**
- `OPENAI_API_KEY` is read from the environment via `python-dotenv`; `.env`, `credentials.json`, `*.key`, and `*.pem` are git-ignored. No real credential is committed at HEAD (verified by scan; see the note at the bottom).
- `docker-compose.yml` embeds default database credentials (`postgres://user:pass@...`, `POSTGRES_USER: user`, `POSTGRES_PASSWORD: pass`). These are generic placeholders, not live secrets — but the file establishes a pattern of inline credentials that must become environment/secret references before the compose sketch is ever built out.

**Input handling**
- CRM/Analytics SQL uses parameterized queries throughout, with two exceptions worth closing: `LIMIT {limit}` is f-string-interpolated in `crm_server.search_accounts`, and `analytics_server` interpolates a date-range value derived from an enum-like parameter. Exploitability today is low (typed int / fixed mapping), but the pattern invites regressions.
- The demo gateway accepts raw `dict` bodies (no Pydantic validation); `api/api_gateway.py` does define Pydantic models for its CRM routes.

**Error handling**
- Structured degradation in the LLM layer (fallback mode) and structured error payloads in the RAG server; CRM tools return `{"error": ...}` for missing rows. No global exception handler on the gateways; stack traces will surface as FastAPI 500s.

**Observability**
- `logging` in `client/mcp_client.py`, `ai_integration.py`, and the Gmail modules; print statements elsewhere. No structured logs, no metrics endpoint, no tracing. The RAG server's `get_automation_decision` already emits a per-decision audit record — the natural seed of an audit log — but nothing persists it.

**Data at rest**
- SQLite files, including three committed demo databases (`sales_platform.db`, `sales_ai_platform.db`, `training_data.db`) containing only fictional records. `.gitignore` covers `data/*.db` but not root-level `*.db`, which is how the snapshots got committed.

**Deployment artifacts**
- `docker-compose.yml` and `nginx.conf` are sketches: the compose file references build contexts (`./model-server`, `./frontend`, an `./api` Dockerfile) that do not exist, and nginx upstreams (`dashboard:8501`, `orchestrator:8888`) match no committed service. Neither is runnable as-is.

## Ladder to production

**Stage 1 — Identity and keys**
1. Put the gateway behind authentication: API keys or OAuth2 bearer tokens via FastAPI dependencies; the declared `pyjwt`/`bcrypt` dependencies and the empty `users`/`sessions` tables indicate the intended shape.
2. Restrict CORS to the actual UI origin; drop `allow_credentials` with a wildcard origin (browsers reject the combination, so today it silently means "no credentialed cross-origin use").
3. Move all credentials in `docker-compose.yml` to env-file/secret references; extend `.gitignore` with root `*.db` and remove the committed database snapshots from the tree (they are regenerable via `init_crm_db.py` / `generate_demo_data.py`).
4. Close the two SQL-interpolation spots (bind `LIMIT ?`; whitelist the date-range mapping).
5. Fix the dependency manifests so one install command yields a complete environment (add `sentence-transformers`, `chromadb`, `fastapi`, `uvicorn`, `httpx`, `requests`, `python-dotenv` to `pyproject.toml`; retire the divergent `requirements*.txt` or generate them from the lock).

**Stage 2 — Monitoring**
1. Replace prints with structured logging (request ID, tool name, latency) at the gateway and in `MCPClient.call_tool`.
2. Persist the autonomy audit records (`get_automation_decision` already builds them) and every auto-executed action — this is the compliance trail for progressive autonomy.
3. Health checks that verify dependencies, not just process liveness: MCP session connected, SQLite writable, ChromaDB reachable, OpenAI status (`ai_integration.get_status` already computes it).
4. Track LLM token counts and the existing per-call cost estimate as metrics; alert on fallback-mode activation, which currently degrades silently.

**Stage 3 — Deployment**
1. Make the container story real: one Dockerfile per service that actually exists (gateway, UI), compose them, and delete the aspirational services from `docker-compose.yml` until they have code behind them.
2. Single gateway: retire `api_gateway_quick_fix.py` in favor of the MCP-wired gateway once its routes are aligned with the real CRM tool set (see EVALUATION for the current mismatches), keeping mock mode as a flag rather than a separate file.
3. Move shared state off local SQLite to a served database when more than one gateway replica is needed; the compose sketch already names PostgreSQL, and Qdrant or a managed vector store replaces the local ChromaDB directory.
4. TLS at the edge (the nginx sketch's HTTPS redirect is the right instinct); pin dependency versions from `uv.lock` in CI.

**Stage 4 — Compliance and data governance**
1. Real CRM data and Gmail content are personal data: define retention for transcripts, embeddings, and email bodies; deletion must reach ChromaDB (embeddings of a deleted transcript persist today) and the training tables.
2. Gmail scopes: the code already requests a split scope set (`gmail.send` + `gmail.readonly`, plus `gmail.compose` in `gmail_client.py`) rather than a broad one — keep it minimal as features grow (note `gmail_client.mark_as_read` mutates labels, which the current scopes do not cover), and document the OAuth consent posture.
3. Human-in-the-loop policy: codify the autonomy thresholds (0.90/0.70/0.50 in `rag_server.AUTONOMY_CONFIG`) as reviewed configuration, with the audit trail from Stage 2 as evidence.
4. Third-party data flow: transcript and email text leaves the boundary to OpenAI when a key is configured; that flow needs a documented processor agreement and a redaction pass (the regex entity extractor is a usable pre-filter for masking emails/phones before the LLM call).

## Secrets removed from HEAD — rotate these credentials and purge history

None. A scan of HEAD (key/token/password patterns, connection strings, committed key material, and the contents of the committed SQLite databases) found no real credentials. The credential-like strings in `docker-compose.yml` (`user`/`pass` for PostgreSQL) are generic placeholders and were left in place; treat them as defaults that must be overridden, never used, in any real deployment.
