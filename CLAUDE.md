# LeadSync — Claude Code Agent Instructions
> Read this entirely before writing any code. Production-grade discipline required — scope creep kills quality.

---

## 1. Project Identity

**LeadSync** is an agentic context engine: Jira webhook fires → CrewAI agents enrich the ticket → a paste-ready AI prompt is attached back to Jira → dev copies it into their coding environment.

**Stack:** FastAPI · CrewAI · Composio (Jira, GitHub, Slack only) · Gemini via LiteLLM · Python 3.11+
**Deploy target:** ngrok + Railway

---

## 2. Project Structure

```
leadsync/
├── src/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── shared.py            # LLM factory, env helpers, Composio client
│   ├── leadsync_crew.py     # Workflow 1 wrapper
│   ├── digest_crew.py       # Workflow 2 wrapper
│   ├── slack_crew.py        # Workflow 3 wrapper
│   ├── pr_review_crew.py    # Workflow 4 wrapper
│   ├── memory_store.py      # SQLite memory facade
│   ├── jira_history.py      # Same-label ticket context facade
│   ├── prefs.py             # Local-file preference loading facade
│   ├── workflow1/           # Ticket Enrichment internals
│   ├── workflow2/           # End-of-Day Digest internals
│   ├── workflow3/           # Slack Q&A internals
│   ├── workflow4/           # PR Auto-Description internals
│   ├── common/              # Model retry, tool helpers, text extraction
│   ├── memory/              # SQLite schema, read/write/query
│   ├── integrations/        # Composio provider wrapper
│   └── tools/               # Jira tool builder
├── config/
│   ├── tech-lead-context.md
│   ├── backend-ruleset.md
│   ├── frontend-ruleset.md
│   └── database-ruleset.md
├── tests/
├── requirements.txt
└── .env
```

Never create files outside this structure without a strong reason.

---

## 3. Four Workflows — Keep Them Separate

| Workflow | Trigger | Agents | Output |
|----------|---------|--------|--------|
| 1 — Ticket Enrichment | `POST /webhooks/jira` | Context Gatherer → Intent Reasoner → Propagator | `prompt-[ticket-key].md` attached to Jira + enriched description + comment |
| 2 — End-of-Day Digest | `POST /digest/trigger` | GitHub Scanner → Digest Writer → Slack Poster | One Slack message with grouped commit summary |
| 3 — Slack Q&A | `POST /slack/commands` | Context Retriever → Tech Lead Reasoner → Slack Responder | Threaded Slack reply with reasoned answer |
| 4 — PR Auto-Description | `POST /webhooks/github` | PR Description Writer (1 agent + rule engine) | Enriched PR description on GitHub with summary, implementation details, files changed, and validation steps |

**Never conflate these into one crew. Four separate files, four separate crews.**

Workflow 1 output is **one file only**: `prompt-[ticket-key].md`. It contains Task + Context + Constraints + Implementation Rules + Expected Output in a single paste-ready document.

---

## 4. Implementation Rules

### Agents
- Max 3 agents per crew. No exceptions.
- `verbose=True` on every agent and crew — logs are the observability layer.
- Only give each agent the tools it needs. Reasoner agents get no tools.
- LLM via env var `LEADSYNC_GEMINI_MODEL`. Default constant: `gemini/gemini-2.5-flash`. Never hardcode beyond the default.

### Composio (locked pattern — do not change)
- All Jira, GitHub, Slack interactions go through Composio. No raw API calls.
- Use `Composio(provider=CrewAIProvider())` + `composio.tools.get(user_id=..., toolkits=[...])`.
- See `src/shared.py:build_tools` for the reference implementation.
- ❌ Do NOT use `ComposioToolSet` or `toolset.get_tools(actions=[...])` — different pattern, not used here.
- `COMPOSIO_USER_ID` from env (default: `"default"`). Only toolkits: `JIRA`, `GITHUB`, `SLACK`. No Google Docs toolkit.

### Config
- Load rulesets at runtime from `config/`. Select by ticket label (`backend-ruleset.md`, `frontend-ruleset.md`, `database-ruleset.md`).
- Load tech lead context at runtime from `config/tech-lead-context.md`.
- Never hardcode ruleset content inline in agent prompts. Edit the files in `config/` directly.

### Shared Utilities
- `src/shared.py` exports: `_required_env()`, `build_llm()`, `build_tools()`, `CrewRunResult`, `memory_enabled()`, `build_memory_db_path()`.
- `src/memory_store.py` facade exports: `init_memory_db`, `record_event`, `record_memory_item`, `query_slack_memory_context`.
- `src/common/model_retry.py` exports: `kickoff_with_model_fallback()` — handles `-latest` stripping and flash-lite→flash fallback.
- All crew files import from `shared.py`. Never duplicate these helpers.

### FastAPI
- All endpoints in `src/main.py`. No router splitting.
- Extract payload fields with `.get()` and safe defaults.
- Return `{"status": "processed", "model": ..., "result": ...}` on success.
- Raise `HTTPException(400)` for missing env vars, `HTTPException(500)` for crew failures.

### Jira Automation Webhooks
- Always use **"Issue data (Jira format)"** as the web request body in Jira automation rules — never "Custom data" templates. Custom data embeds raw field values into a JSON string, which breaks on multi-line descriptions, quotes, and control characters.
- "Issue data (Jira format)" sends the issue as a top-level object (no `"issue"` wrapper, no `changelog`). Add a dedicated endpoint (e.g. `/webhooks/jira/done`) that wraps the payload before passing it to `parse_issue_context`:
  ```python
  wrapped = {"issue": payload, "changelog": {"items": [{"field": "status", "toString": "Done"}]}}
  ```
- The Jira automation condition (e.g. "Status = Done") replaces the need for changelog detection in code.

---

## 5. Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `GEMINI_API_KEY` | Yes | — |
| `COMPOSIO_API_KEY` | Yes | — |
| `SLACK_CHANNEL_ID` | Yes (WF2+3) | — |
| `COMPOSIO_USER_ID` | No | `"default"` |
| `LEADSYNC_GEMINI_MODEL` | No | `gemini/gemini-2.5-flash` |
| `LEADSYNC_GITHUB_REPO_OWNER` | Yes (WF1+2) | — |
| `LEADSYNC_GITHUB_REPO_NAME` | Yes (WF1+2) | — |
| `LEADSYNC_MEMORY_ENABLED` | No | `"true"` |
| `LEADSYNC_MEMORY_DB_PATH` | No | `data/leadsync.db` |
| `LEADSYNC_DIGEST_WINDOW_MINUTES` | No | `60` |
| `LEADSYNC_TRIGGER_TOKEN` | No (WF2 security) | — |

`_required_env(name)` in `shared.py` raises `RuntimeError` with a clear message when a required var is absent.

---

## 6. Error Handling

- Wrap every `crew.kickoff()` in try/except. Log before re-raising.
- If model name contains `-latest` and error contains `NOT_FOUND`: retry with `-latest` stripped.
- Never silently swallow errors — readable logs are essential for debugging.

---

## 7. Shell & Environment

**This project runs on Windows. Use Windows shell syntax for all commands.**

- Use `venv\Scripts\activate` (not `source venv/bin/activate`) to activate the virtual environment.
- Before running any Python command (`python`, `pytest`, `pip`, `uvicorn`, etc.), activate the venv first:
  ```
  venv\Scripts\activate && python ...
  ```
- Use backslashes for paths in shell commands, or quote forward-slash paths. Use `set VAR=value` not `export`.
- Never use Unix-only constructs (`&&` chaining works in cmd/PowerShell, but avoid `source`, `/dev/null`, etc.).

**When finishing work on a worktree and it's ready for developer handoff, always offer to push the changes to `main`** (e.g., merge or fast-forward the worktree branch into main and push). Present this as a clear yes/no option before doing so.

---

## 8. Coding Standards

- All logic in `src/`. No root-level scripts.
- `@dataclass` for return types (e.g., `CrewRunResult`). Type hints on all function signatures.
- Every file: module docstring at top naming its workflow and exports.
- Every function: docstring with args, return value, side effects.
- Files under 150 lines. No `print()` — use `verbose=True` and FastAPI logging.
- Never commit secrets. All secrets in `.env`, loaded via `python-dotenv`.
- Agent backstories and task descriptions: ≤3 sentences, bullet points preferred.

---

## 9. Testing

- Write tests before implementation (TDD).
- Tests in `tests/` mirroring `src/` structure.
- Mock Composio and `crew.kickoff()` — no real API calls in tests.
- Target ≥60% line coverage: `pytest --cov=src --cov-report=term-missing -q`
- All tests must pass before any handoff.

---

## 10. Out of Scope — Do Not Add

- ❌ Two output files per ticket — one `prompt-[ticket-key].md` only
- ❌ PR review/approval automation — WF4 enriches descriptions only, does not approve or merge
- ❌ Any UI or dashboard
- ❌ External managed database — local SQLite memory only
- ❌ More than 3 agents per crew
- ❌ One mega-crew for multiple workflows
- ❌ Any toolkit besides `JIRA`, `GITHUB`, `SLACK`

Only build features explicitly described in these instructions.
