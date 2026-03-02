# Backend Ruleset

## API Design
- Every new endpoint requires a rate limit annotation.
- Third-party API calls must use retry logic with exponential backoff.
- All endpoint handlers must be async. No blocking I/O in handlers.
- Validate at the boundary — return 400 with `{"detail": "..."}` for bad input.

## Code Standards
- Thin controllers, fat services. No business logic in `main.py`.
- Explicit dependencies — pass everything via factory functions, no magic globals.
- HTTP clients: use `httpx` with a shared client instance, not `requests`.
- Background tasks: FastAPI `BackgroundTasks` for lightweight work.

## Testing
- Every new endpoint needs a test covering happy path and at least one error case.
- Mock all external API calls. No real network calls in tests.
- Coverage must not drop on merge.

## Non-Negotiables
- No raw SQL strings — use parameterized queries or ORM.
- No `print()` in production code — use Python `logging`.
- No new mutable module-level globals.
