# Hardening

Current security and operational posture of the code as it exists, followed by a staged ladder to production. Grounded in the actual system: a Next.js UI over fixtures plus one unauthenticated streaming proxy route (`app/app/api/chat/route.ts`).

## Current posture

**Authentication & authorization**
- None. Every page and the API route are public. `/api/chat` is an open relay to a paid model endpoint: any unauthenticated caller can submit arbitrary `messages` and spend the configured key's quota. There are no users, roles, or sessions to authorize.

**Secrets handling**
- The route reads its bearer token from a server-side environment variable (`ABACUSAI_API_KEY`) — the correct pattern; the key never reaches the browser.
- Historically this repository committed a real key in `app/.env` (see the rotation section at the bottom). That file has been deleted at HEAD and `.env` files are now gitignored at both the repository root and `app/`; `.env.example` contains placeholders only.
- The committed `app/.next/` build output was checked and does not contain the key (env access is at runtime via `process.env`).

**Input validation & abuse resistance**
- The client-supplied `messages` array is spread directly into the upstream payload — no validation of role values, message count, or payload size. Oversized or hostile histories pass straight through; the caller effectively controls everything after the system prompt.
- No rate limiting, no CORS policy, no request-size cap beyond framework defaults.

**Error handling & resilience**
- No timeout on the upstream call; a hung provider hangs the request.
- No retry for transient upstream failures.
- All failures collapse to a generic `500 {"error": "Failed to process request"}`; the UI shows one fixed apology string. Status codes and upstream error details are never surfaced or recorded.
- Malformed stream frames are swallowed by empty `catch` blocks on both server and client; neither side buffers across chunk boundaries, so split frames drop tokens silently.

**Observability**
- Two `console.error` calls in the route handler are the entire telemetry surface. No structured logging, no error tracker, no metrics, no tracing, no health endpoint. The sidebar's "System Operational" badge is a hardcoded string, not a health check.

**Build & repository hygiene**
- `app/.next/` (including development webpack caches) and `app/tsconfig.tsbuildinfo` are committed; build artifacts in history bloat the repository and can leak paths of the build machine.
- `app/package.json` has no `scripts` block, the root `package.json` drives it with `npm` while the app pins `yarn@4.9.2`, and the root `vercel.json` (legacy `builds`/`routes` schema) conflicts with the dashboard-based deployment described in `VERCEL_DEPLOYMENT.md`.
- No `LICENSE` file; reuse terms are undefined.

## Staged ladder to production

### Stage 1 — Identity, keys, and the front door
1. **Rotate the exposed key and purge history** (details in the rotation section below). Do this first; everything else assumes the key is no longer public.
2. Store the replacement key only in the deployment platform's encrypted environment variables (per-environment values; never in the repo).
3. Put authentication in front of `/api/chat` — for this stack, NextAuth or a middleware-verified session/token — so quota spend is attributable to a user.
4. Add per-user rate limiting and payload validation at the route boundary: allowed roles (`user`/`assistant`), a message-count cap, a per-message and total size cap. Reject anything else with a 400.

### Stage 2 — Resilience and observability
1. Wrap the upstream call in an `AbortController` timeout (the streaming read loop must also honor it) and add one bounded retry for connect-phase failures only — never retry mid-stream.
2. Replace the hand-rolled parsers with buffered line parsing on both sides (carry partial frames across reads); count and log dropped frames instead of swallowing them.
3. Map upstream failures to distinct statuses (401/403 config error, 429 backpressure, 5xx upstream outage) and surface a matching user-visible message instead of one fixed string.
4. Add structured request logging (request id, latency, token counts, upstream status) and an error tracker; add a real `/api/health` and drive the sidebar status badge from it — today it hardcodes "System Operational".

### Stage 3 — Build, deployment, and repo hygiene
1. Add a `scripts` block to `app/package.json` (`dev`, `build`, `start`, `lint`, `test`) and standardize on the pinned yarn; fix or delete the root `package.json` shim.
2. Resolve the deployment conflict: either the dashboard Root-Directory approach from `VERCEL_DEPLOYMENT.md` **or** the root `vercel.json` — not both; the legacy `builds`/`routes` schema should go regardless.
3. Untrack build artifacts: remove `app/.next/` and `app/tsconfig.tsbuildinfo` from version control and add them to `.gitignore`.
4. CI on every push: type-check, lint, and the deterministic test suite from [EVALUATION](./EVALUATION.md); block merges on red.
5. Add a `LICENSE` file to make reuse terms explicit.

### Stage 4 — Data protection and compliance (when real data arrives)
The current app holds no real data, so compliance work is premature today — but the moment the fixtures are replaced by a real CRM store and uploaded call transcripts (ARCHITECTURE, extension steps 1–3), the data becomes personal data:
1. Encrypt the data store at rest; TLS is already implied by the platform.
2. Define retention and deletion for transcripts and chat logs (transcripts of real calls are the most sensitive asset this design ever touches).
3. Review the model provider's data-processing terms before sending customer transcripts upstream; add a data-processing agreement and, if required, redaction of PII before the completion call.
4. Add audit logging for data access, and an account-deletion path once users exist.
5. Only then do certification frameworks (SOC 2 and similar) become meaningful; claims of compliance belong after controls exist, not before.

---

## Secrets removed from HEAD — rotate these credentials and purge history

| Secret | Where it was | Action taken at HEAD | Required follow-up |
|---|---|---|---|
| `ABACUSAI_API_KEY` (32-hex API key for the OpenAI-compatible chat endpoint) | `app/.env` (committed; the file's only content) | File deleted; `.env` patterns added to root and `app/` `.gitignore` | **Rotate the key at the provider immediately** — it remains in git history and must be treated as public. Then purge history (e.g. `git filter-repo --invert-paths --path app/.env`) and force-push, or rotate and accept the historical exposure of a dead key. |

Verified during the sweep: the key value appears nowhere else in tracked files (including the committed `app/.next/` build output), and `.env.example` contains placeholders only.
