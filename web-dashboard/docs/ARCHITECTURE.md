# Architecture

This document describes the system **as implemented** in this repository. The other documents in `docs/` (voice gateway, CRM integrations, training pipeline, AI/ML architecture, Gmail integration, monitoring) are design specifications for a target system whose components do not exist in this codebase; they are useful as forward-looking design work but must not be read as descriptions of the code.

## System shape

The application is a Next.js 14 App Router project rooted at `app/`. It has two kinds of behavior:

1. **Static presentation** — five dashboard pages rendered entirely from a hardcoded fixture module, with client-side filtering and animation but no server data fetching.
2. **One live path** — a chat page that POSTs the conversation to a route handler, which proxies to an external OpenAI-compatible chat-completions API and streams the reply back.

There is no database, no ORM, no authentication layer, no background jobs, and no external integration other than the chat completions endpoint.

## Component map

| Component | File(s) | Type | Role |
|---|---|---|---|
| Root layout | `app/app/layout.tsx` | Server | HTML shell, metadata title ("AI Sales-Enablement Platform"), gradient background, mounts `Navigation` |
| Navigation | `app/components/navigation.tsx` | Client | Fixed sidebar; active-link state via `usePathname`; hardcoded version label and a static "System Operational" badge (not wired to any health check) |
| Dashboard | `app/app/page.tsx` | Server | KPI grid of `MetricsCard`s plus charts and activity feed; a "Quick Actions" button grid is presentational only (no handlers) |
| Analytics | `app/app/analytics/page.tsx` | Client | Recharts line/bar/pie/area charts; reads `mockDashboardData` plus additional literals defined inline in the page |
| CRM | `app/app/crm/page.tsx` | Client | Contact list + detail pane; client-side search by name/company/email and deal-stage filter over `mockContacts` |
| Transcripts | `app/app/transcripts/page.tsx` | Client | Drag-and-drop upload zone and transcript viewer with AI-insight panels; the upload is simulated (`// Simulate file upload and processing`) — no file is read or transmitted |
| Training | `app/app/training/page.tsx` | Client | Training-pipeline dashboard; the "start training" control drives a `setInterval` progress bar, not a real job |
| Chat | `app/app/chat/page.tsx` | Client | Message list + composer; POSTs to `/api/chat`; incrementally renders the streamed reply |
| Chat API | `app/app/api/chat/route.ts` | Route handler | The entire backend — see "The live path" below |
| Fixtures | `app/lib/mock-data.ts` | Module | Typed interfaces (`Contact`, `CallTranscript`, `ChatMessage`) and fixture exports (`mockContacts`, `mockTranscripts`, `mockDashboardData`, `mockTrainingPipeline`, `mockChatMessages`) |
| Chart/feed components | `app/components/{pipeline-chart,revenue-chart,recent-activity,metrics-card}.tsx` | Client | Recharts wrappers and animated KPI cards; the chart and feed components import `mockDashboardData` directly rather than receiving props |
| UI primitives | `app/components/ui/*.tsx` | Client | Seven shadcn/Radix primitives (avatar, badge, button, card, input, progress, textarea) |
| Utilities | `app/lib/utils.ts` | Module | `cn` class merging and formatting helpers |

Outside `app/`:

- `demo/` — an abandoned partial scaffold: configs and an older fork of the mock-data module, with no pages, components, or `package.json`. It cannot build and nothing references it.
- Root `package.json` + `vercel.json` — deployment shims (see "Deployment configuration" below).

## Data flow

### Static pages

```
app/lib/mock-data.ts ──import──▶ page / chart components ──render──▶ browser
```

All interactivity (CRM filtering, chart tooltips, count-up animations, simulated progress) happens client-side over the imported fixtures. No page performs a fetch. Because every list is a non-empty literal, no loading, empty, or error state exists anywhere in the UI, and none can occur.

### The live path (chat), end to end

1. **Compose** — `chat/page.tsx` guards against empty input and double-submit, appends the user message to React state, and POSTs `{ messages }` to `/api/chat`, where `messages` is the **full conversation history** mapped to `{ role, content }` pairs.
2. **Proxy** — `route.ts` prepends a static system prompt and forwards the payload to `https://apps.abacus.ai/v1/chat/completions` (an OpenAI-compatible API) with `model: 'gpt-4.1-mini'`, `stream: true`, `max_tokens: 3000`, `temperature: 0.7`, authenticated by the `ABACUSAI_API_KEY` bearer token — the only environment variable the code reads.
3. **Re-encode** — the handler reads the upstream SSE stream, extracts each delta's `content`, and re-emits it as its own simplified stream: `data: {"content": "..."}` lines terminated by `data: [DONE]` (served as `text/plain`, not `text/event-stream`).
4. **Render** — the client reads the stream with a `ReadableStream` reader, accumulates deltas into a buffer, and rewrites the last assistant message in state on every delta, producing the typing effect. `[DONE]` ends the loop.
5. **Failure** — any route-level error returns a generic `500 {"error": "Failed to process request"}`; the client catches any failure and appends a fixed apology message. Malformed JSON lines are silently skipped on **both** sides (empty `catch` blocks).

## Orchestration analysis: parallel vs sequential vs async

- **Everything is sequential.** There is one request path and it is a linear pipeline. No fan-out, no queues, no workers, no scheduled jobs.
- **The only true asynchrony is the stream.** The route handler and the chat client both run incremental async read loops over the completion stream; this is streaming I/O, not concurrency between tasks.
- **Apparent asynchrony that is simulated:** the training page's progress bar (`setInterval`, +2% per 100 ms) and the transcripts page's upload/processing states are timers over local state, deliberately imitating long-running work that has no backend.
- Server components (`layout.tsx`, `page.tsx`) render synchronously from imported fixtures; there is no `async` data fetching to parallelize.

This is the correct minimal shape for what the app does: one upstream dependency, one hop, streamed to keep perceived latency low. Nothing in the code needs parallelism yet.

## State and context engineering

- **Server state: none.** No session store, no cache, no persistence of any kind. Every request to `/api/chat` is self-contained.
- **Client state:** plain `useState` per page. Chat history, CRM filters, and simulated progress all live in component state and are lost on refresh. No global state library.
- **Context assembly for the model:** the prompt is `[static system prompt] + [entire client-supplied history]`.
  - The system prompt defines the assistant's persona (sales analysis, coaching, next-best-action advice) and embeds a snapshot of the dashboard's mock KPIs as "current platform metrics". This means the assistant asserts fixture numbers as facts — acceptable for a demo, a defect for anything more (see HARDENING).
  - **Bounding:** there is none on the input side. History grows without truncation or token counting; only the upstream model's context limit and the `max_tokens: 3000` output cap bound the exchange. A long conversation will eventually fail upstream.
  - **Trust boundary:** the client-supplied `messages` array is spread into the upstream payload without validation of roles, sizes, or count — the server does not distinguish its own system prompt from whatever the client sends after it.

## Design decisions visible in the code, and their trade-offs

1. **Server-side proxy for the model call.** The API key stays in a server environment variable and is never shipped to the browser. The cost is that the route is an open relay: unauthenticated callers can spend the key's quota (see HARDENING).
2. **Re-encoding the upstream stream** instead of piping it raw. This decouples the client from the provider's wire format — the client only knows `{"content"}` frames — making a provider swap invisible to the UI. The cost is a hand-rolled parser on both sides; neither side buffers across chunk boundaries, so an SSE frame split across TCP reads is silently dropped (visible as occasional missing tokens).
3. **A single typed fixture module** as the data source. `mock-data.ts` centralizes the domain model (`Contact`, `CallTranscript` with its `aiInsights` shape) and makes the future data-layer contract explicit. The trade-off taken: chart and feed components import the fixtures directly instead of taking props, so components are wired to the mock module rather than reusable over arbitrary data.
4. **Hardcoded model, endpoint, and generation parameters** in the route handler. Zero configuration surface — nothing to misconfigure in a demo — at the cost of requiring a code change to alter model, provider, or temperature.
5. **Simulated workflows in the UI** (training run, transcript upload) rather than stub backends. The pages demonstrate the intended UX honestly (the simulation is even commented), and the insight-panel rendering already consumes the real `aiInsights` schema — so wiring a real analysis backend later changes data flow, not UI.
6. **Optimistic, fixed-copy error handling.** Errors never surface status codes or upstream messages. Good demo polish; poor operability (see EVALUATION and HARDENING).

## Deployment configuration

The repository carries two conflicting deployment mechanisms:

- Root `vercel.json` uses the legacy `builds`/`routes` schema pointing `@vercel/next` at `app/package.json`, with a `/(.*) → /app/$1` rewrite.
- `VERCEL_DEPLOYMENT.md` instructs setting the project's Root Directory to `app` in the Vercel dashboard — in which case the root `vercel.json` is ignored.

Additionally, the root `package.json` scripts call `npm run build` inside `app/`, but `app/package.json` has **no `scripts` block**, so those commands fail as written; and the app pins `yarn@4.9.2` (`packageManager` field, `yarn.lock`) while the root scripts invoke `npm`. Local development works by invoking Next.js directly (`yarn next dev`). Reconciling these is a hardening step, not a documentation choice — see HARDENING stage 3.

`app/.next/` build output and `app/tsconfig.tsbuildinfo` are committed to version control; they are reproducible artifacts and should be untracked.

## Extending this system

The next steps that this codebase specifically makes easy, in dependency order:

1. **Introduce a data layer behind the existing types.** `mock-data.ts` already defines the domain contract (`Contact`, `CallTranscript`, `aiInsights`). Add route handlers (`/api/contacts`, `/api/transcripts`) that return those exact shapes — first serving the fixtures, then a real store — and convert the chart/feed components from direct fixture imports to props. The UI then works unchanged against either source, and empty/loading states become reachable and testable for the first time.
2. **Ground the assistant in live data.** Replace the KPI-embedding static system prompt with server-side context assembly: the route handler queries the data layer for current pipeline numbers (and, later, the selected contact or transcript) and injects them per request. This turns the chat from a persona demo into the analysis tool the UI already advertises, and moves prompt truth out of a string literal.
3. **Make transcript upload real.** The drag-and-drop surface, progress states, and insight panels are already built against the `aiInsights` schema. Wire the drop handler to an upload route, run the completion call over the transcript server-side, and validate the response against that schema. This is the shortest path from "one live path" to two, and it reuses the streaming proxy pattern already in `route.ts`.
4. **Extract a hardened streaming client.** Both sides hand-parse the stream with known gaps (no cross-chunk buffering, silent JSON drops, no timeout). Factor the route's read loop into a small utility with buffered line parsing, an `AbortController` timeout, and surfaced errors — then both the chat route and the transcript-analysis route (step 3) share it.
5. **Lift provider configuration into the environment.** The endpoint URL and model name are the only hardcoded integration constants. Reading them from env vars (alongside the existing `ABACUSAI_API_KEY`) makes the OpenAI-compatible surface an actual abstraction: any conforming provider becomes a config change, which also unblocks A/B-ing models — the future the design specs in this directory describe.
