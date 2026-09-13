# Evaluation

An honest account of what is tested in this repository, what defensive behavior the code actually contains, and — since no harness exists — a proposed evaluation design.

## What automated tests exist

**None.** The repository contains:

- no test files (`*.test.*`, `*.spec.*`) anywhere,
- no test runner configuration (no Jest, Vitest, or Playwright config; no test-related dependencies in `app/package.json`),
- no `scripts` block in `app/package.json` at all, so there is no `test` script to run,
- no CI (`.github/` does not exist; no pipeline configuration of any kind),
- no linting gate (an `.eslintrc.json` exists and `eslint`/`eslint-config-next` are devDependencies, but nothing invokes them).

Two earlier documents claim otherwise and should not be relied on: the root-level design writeups reference `pytest tests/` and a `tests/{unit,integration,e2e}` tree. No Python and no `tests/` directory exist in this repository.

No performance or quality metrics are recorded anywhere in the code. Numbers that appear in the UI (win rate, model accuracy, ingestion counts) are fixture values from `app/lib/mock-data.ts`, not measurements.

## Edge cases the code visibly handles

Enumerated from the source, with file references — this is the complete list:

**Chat client — `app/app/chat/page.tsx`**
- Empty-input and double-submit guard: `if (!input.trim() || isLoading) return` (line 31).
- Non-2xx response from `/api/chat` throws and is caught; the UI appends a fixed error message ("Sorry, I encountered an error. Please try again.") instead of crashing (lines 55–57, 105–112).
- `isLoading` is reset in a `finally` block, so the composer cannot get stuck disabled (lines 113–115).
- Stream termination on `data: [DONE]` (lines 83–86).
- Malformed JSON stream lines are skipped via an empty `catch` (lines 98–100) — the UI never breaks on a bad frame, but dropped tokens are invisible.
- Enter submits, Shift+Enter inserts a newline (lines 118–123).

**Chat route — `app/app/api/chat/route.ts`**
- Upstream non-2xx: `if (!response.ok) throw` → caught → generic `500 {"error": "Failed to process request"}` JSON response (lines 45–47, 102–110).
- Missing upstream body: explicit `throw new Error('No response body')` (lines 56–58).
- Malformed upstream JSON frames skipped via an empty `catch` (lines 82–84).
- Streaming errors are logged (`console.error`) and propagated with `controller.error` (lines 88–91).

**What is visibly *not* handled** (verified absent from the code):
- No request timeout or `AbortController` anywhere — a hung upstream hangs the request indefinitely.
- No retry on transient failure.
- No rate limiting and no authentication on the API route.
- No validation of the client-supplied `messages` array (roles, count, size) before it is forwarded upstream.
- No cross-chunk buffering in either stream parser — an SSE frame split across network reads is silently lost on both sides.
- No React error boundaries, `error.tsx`, `loading.tsx`, or `not-found.tsx`.
- No empty-state rendering: every list renders from a non-empty fixture, so empty states are unreachable and were never built.

## Proposed evaluation harness

> **Proposed — none of the following exists yet.** This section specifies what this system should have, sized to what the code actually is (a UI over fixtures plus one streaming proxy route).

### 1. Deterministic tests (no model calls)

**Stream-protocol contract tests** for `route.ts` — the highest-value target, because both known correctness gaps live here. Mock the upstream `fetch` with SSE fixtures and assert on the re-encoded output stream:
- happy path: N delta frames → N `{"content"}` frames + `[DONE]`;
- a frame **split across two chunks** (currently fails — this test pins the bug and its fix);
- malformed JSON frames interleaved with valid ones — assert no valid token is lost and the failure is observable (counter or log), not silent;
- upstream 401/429/500 → route returns 500 today; the test suite should assert the *chosen* mapping once error handling is hardened;
- missing body → clean error, no hang.

**Component tests** (React Testing Library) for logic that already exists in the UI: CRM search + stage filtering over a fixture list (including the zero-results rendering), chat composer guards (empty input, disabled while loading, Enter vs Shift+Enter), and incremental message rendering fed by a mocked stream.

**Static gates**: `tsc --noEmit` and `next lint` wired into a `test`/`check` script (which first requires adding a `scripts` block to `app/package.json`) and a CI workflow that runs on every push.

### 2. Model-response evaluation (requires an API key)

The assistant's job, per its system prompt, is sales analysis and next-step advice. A minimal golden-set harness:

- **Golden dataset shape**: JSONL records of `{ id, messages (conversation so far), rubric }`, seeded from realistic sales scenarios — the ~25-turn scripted transcript in `mock-data.ts` is a ready first source; 20–50 cases covering the four quick-action intents on the chat page (pipeline analysis, follow-up priorities, call concerns, next best actions).
- **Rubric per case**: required elements (e.g. "names at least one concrete next step", "references only figures present in the supplied context"), forbidden elements (e.g. invented customer names or numbers), and a length band. Score with cheap assertions first (regex/structural), an LLM judge only for the subjective residue.
- **Metrics**: pass rate per intent; hallucinated-figure rate (any number not present in the prompt context — directly measurable once step 2 of ARCHITECTURE's extension plan injects real context); stream health (tokens dropped vs received, time-to-first-token, total latency).
- **Gates**: deterministic suite green on every PR; golden-set pass rate above an agreed floor (start at 80%, ratchet) on a nightly run, since it costs tokens; zero hallucinated figures on cases whose context contains the ground truth.

### 3. When the simulated flows become real

The transcript-upload and training flows are currently simulations; once wired to real backends (ARCHITECTURE, extension steps 2–3), each needs: schema validation of analysis output against the existing `aiInsights` interface (sentiment enum, non-empty `nextSteps`), an end-to-end smoke test through the upload route with a fixture transcript, and latency/error-rate tracking on the new routes.
