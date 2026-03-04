# LeadSync — Project Vision & Pipeline
> **Status: Ideation** — This doc evolves as ideas solidify. Add new ideas under the right section.

---

## What Is LeadSync?

A **dual-architecture system** that serves two purposes simultaneously:

1. **For humans** — Makes project management effortless. Enriches tickets, keeps status visible, simplifies approvals. Team leads see everything at a glance. Developers get well-structured tasks.
2. **For AI agents** — Creates an autonomous coding environment with full project context (progress history, exact changes, GitHub data, Jira state). Agents work independently on tasks end-to-end.

The core principle: **agents do the heavy lifting, humans stay in control.** Every status transition, every PR, every deployment requires human approval — but approving should be a one-click action because the agent's work is high quality and well-documented.

---

## Dual Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │           HUMAN LAYER                        │
                    │  Full visibility · One-click approvals       │
                    │  Status dashboards · Progress tracking       │
                    │                                              │
                    │  Slack ◂──── notifications / interactions    │
                    │  Jira  ◂──── live status + enriched tickets  │
                    │  GitHub ◂─── PRs ready for review            │
                    └──────────────────┬───────────────────────────┘
                                       │ approve / reject / clarify
                                       ▾
┌──────────────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                         │
│  Autonomous coding environment with full project context                     │
│                                                                              │
│  ┌─────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐              │
│  │ Ticket   │───▸│ Enrichment│───▸│  GitHub   │───▸│  Claude  │              │
│  │ created  │    │ Agent     │    │  Issue    │    │  Coding  │              │
│  │ (short)  │    │ (expand + │    │  created  │    │  Agent   │              │
│  │          │    │  context) │    │           │    │          │              │
│  └─────────┘    └───────────┘    └───────────┘    └────┬─────┘              │
│                                                        │                     │
│       ┌────────────────────────────────────────────────┘                     │
│       │  progress events (commits, status, blockers)                         │
│       ▾                                                                      │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐                              │
│  │ Status   │───▸│  Jira     │───▸│  Slack   │──▸ human notified            │
│  │ Tracker  │    │  updated  │    │  update  │   (approve/clarify)          │
│  └──────────┘    └───────────┘    └──────────┘                              │
│                                                                              │
│  Context available to agents: Jira history, GitHub changes, progress log     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

- **Human approves, agent executes** — No autonomous merges, deployments, or status transitions without human sign-off
- **Approval is trivial** — Because agents produce high-quality work, approval is a quick review + one click, not a bottleneck
- **Full transparency** — Humans can see at any moment: what the agent is doing, what changed, why, and what's next
- **Rich agent context** — Agents have access to project history, related tickets, codebase state, and progress of other tasks
- **Two audiences, one system** — The same enriched tickets that help agents code also help developers understand and review

---

## Pipeline Steps

1. **Dev creates a short Jira ticket** — just a title and a sentence or two
2. **Enrichment agent expands the ticket** — adds context, acceptance criteria, implementation plan, links to related work
3. **GitHub issue auto-created** — all enriched info transferred, cross-linked to Jira
4. **Claude coding agent picks up the issue** — works autonomously with full project context
5. **Status flows back to Jira automatically** — In Progress → In Review → Awaiting Approval
6. **Human notified via Slack** at key moments:
   - PR ready for review → one-click approve
   - Agent blocked or needs clarification → respond in thread
   - Task completed → summary of what changed and why
7. **Human approves** — PR merged, Jira ticket closed

---

## Integrations

| Service | Role |
|---------|------|
| **Jira** | Source of truth for tickets, status tracking, human-visible progress |
| **GitHub** | Issues for AI work items, PRs for code delivery, change history |
| **Slack** | Team notifications, human-AI interaction, approvals, clarifications |
| **Claude** | Autonomous coding agent with full project context |

---

## Central Memory / Context Store (TO DECIDE)

Agents need a shared memory layer that persists across pipeline phases. Every agent (enrichment, coding, status tracking) should read from and write to the same store so context is never lost between steps.

**What it must hold:**
- Task state — current status, who's working on it, blockers
- Enrichment output — expanded descriptions, acceptance criteria, implementation plans
- Progress log — what the coding agent did, commits made, decisions taken
- Cross-references — links between Jira ticket, GitHub issue, PR, Slack threads
- Project knowledge — codebase patterns, past decisions, related ticket history

**What agents need from it:**
- Enrichment agent reads: raw ticket + project knowledge + related ticket history
- Coding agent reads: enriched ticket + codebase context + progress of related tasks
- Status tracker reads: coding agent progress events + current Jira state
- Slack notifier reads: task state + progress log (to summarize for humans)

**Architecture options to evaluate:**
| Option | Pros | Cons |
|--------|------|------|
| **SQLite (local)** | Simple, no infra, fast reads | Single-machine, no concurrent multi-agent writes |
| **PostgreSQL** | Concurrent access, scalable, structured queries | Infra to manage, heavier setup |
| **Redis + persistent store** | Fast reads for active context, pub/sub for events | Two systems to maintain |
| **Vector DB (Pinecone/Chroma)** | Semantic search over project knowledge | Overkill for structured task data, still need relational store alongside |
| **Hybrid: relational + vector** | Best of both — structured task data + semantic project knowledge | Complexity |

> **Decision needed:** Pick the memory architecture before implementation begins. This is foundational — everything reads from and writes to it.

---

## Open Questions
<!-- Add questions here as they come up -->
- How does Claude get assigned issues? (GitHub Actions? Webhook? Polling?)
- What triggers status transitions back to Jira? (Claude events? GitHub PR status?)
- How granular should Slack updates be? (Every commit? Only milestones?)
- What does the "one-click approve" flow look like in Slack? (Button? Reaction? Command?)
- What happens when multiple agents work on related tickets simultaneously?
- **Memory/context store:** Which architecture? How much context is "enough" per agent call? How to handle stale context?

---

## Ideas Backlog
<!-- Drop new ideas here — one bullet per idea -->
- _None yet — add as they come_

---

## Shell & Environment

**This project runs on Windows.**
- Use PowerShell for commands
- Python 3.11+
- Secrets in `.env`, loaded via `python-dotenv`
