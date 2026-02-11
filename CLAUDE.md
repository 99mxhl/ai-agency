# AI Influencer Marketing Agency

## Project Overview
AI-powered influencer marketing agency operating across CEE (Poland, Romania, Czech Republic). Core differentiator is using AI to replace the relationship-heavy, high-margin (20%+) model of traditional agencies with data-driven, outcome-based services at lower margins (10-15%). Multi-market from day one — cross-border capability is the structural advantage over relationship-based incumbents.

## Business Strategy
- Target underserved segments: D2C e-commerce, startups, fraud-burned companies
- Lead with free brand audits as client acquisition tool
- Sell outcomes (ROI, conversions) not access (influencer relationships)
- Undercut incumbents on margin via lower operational costs
- Multi-market CEE coverage (PL/RO/CZ) — serve cross-border campaigns traditional agencies can't

## Monetization & Service Delivery
1. **Acquire leads:** Free brand audit via cold outreach — reveals fake followers, engagement gaps, missed opportunities
2. **Convert to paid client:** Audit reveals problems → offer to run their influencer campaigns
3. **Run campaigns, take margin:** Client provides campaign budget, we find influencers (scoring/matching tool), negotiate, manage execution. Revenue = 10-15% margin on campaign spend
4. **Retain with dashboard:** Client dashboard shows ROI, conversions, fraud scores — proves value, drives rebooking

## Competitive Landscape
- **Modash** — SaaS tool, 350M+ profiles, self-serve. Not an agency. Has Discovery API ($16,200/yr) we plan to evaluate as primary data source. Confirmed CEE coverage (PL/RO/CZ).
- **Influencers.Club** — 340M+ profiles across 12 platforms, API from $249/mo. Potential lower-cost data source alternative to Modash.
- **Dash Social** — Enterprise social suite, influencer is one module. Not competing with us.
- **Slice.id** — Closest model (SaaS + managed services), but Indonesia-focused.
- **Traditional CEE agencies** — Relationship-based, 20%+ margins, single-market.

## Build Roadmap
1. **Brand Audit Generator** (current) — lead magnet / cold outreach tool
2. **Influencer Scoring & Matching Tool** — core service delivery
3. **Client Dashboard** — reporting & retention

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL 16, Alembic, Pydantic
- **Frontend:** Next.js 16, Tailwind CSS 4, shadcn/ui, TanStack Query
- **Data:** Apify (Instagram scraping), Anthropic Claude API (narrative generation)
- **Infra:** Docker Compose, uvicorn
- **Testing:** pytest, pytest-asyncio, httpx

## Project Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app with CORS + lifespan
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # SQLAlchemy async engine + sessions
│   ├── api/v1/              # REST endpoints (audits, health)
│   ├── models/              # SQLAlchemy models (Brand, Influencer, Audit, etc.)
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic (AuditOrchestrator)
│   ├── data_sources/        # External integrations (Instagram/Apify)
│   ├── workers/             # Background task runners
│   └── utils/
├── tests/
├── alembic/                 # DB migrations
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
├── Dockerfile
└── package.json
```

## Git Rules

**Claude must ask permission before any git operation. NEVER push without explicit user approval.**

**FORBIDDEN TO PUSH DIRECTLY TO MAIN. Always create a feature branch and PR.**

- Branches: `main` (prod), `feature/*`, `fix/*`, `hotfix/*`
- Commits: `type(scope): description` — types: feat, fix, docs, refactor, test, chore
- PRs: feature/* → main
- **Merge commits:** Never use default "Merge pull request #X from ..." messages. Use descriptive messages following conventional commit format, e.g., `feat(mobile): add platform badges and colors`
- **Before pushing:** Always check if there are new PR reviews to address. Fix all issues before pushing to avoid triggering multiple CI workflows.
- **False positive reviews:** If reviewer flags issues that don't exist in actual code (e.g., claims missing dependency that exists), point it out.
- **Maintain .gitignore proactively:** When adding files, dependencies, or tooling — check if anything new should be gitignored. Don't wait to be told. If it shouldn't be in the repo (lockfiles from wrong package managers, build artifacts, caches, secrets), add it to .gitignore immediately.
- **Deferred PR review items → GitHub issues:** When a PR review flags a valid improvement but it's deferred (e.g., "nice to have at this scale"), immediately create a GitHub issue so it enters the backlog. Don't let deferred work get lost in PR comments.
  - **Re-read the exact review comment** before writing the issue — never go from memory
  - **Issue titles are not commits.** Use plain language describing the problem (e.g., "Profile cache may cause memory issues at scale"), not conventional commit format (`perf(scoring): optimize ...`)
  - **Use precise terminology.** Don't misapply patterns (e.g., "N+1" is a DB-specific anti-pattern, not any sequential loop)

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- **SESSION START: IMMEDIATELY read `tasks/lessons.md` before doing anything else** - this is mandatory, not optional
- After ANY correction from the user: update 'tasks/lessons.md' with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Bug Fixing Workflow
- Don't start by trying to fix a bug - first write a failing test that reproduces it
- Use subagents to implement the fix and verify it passes the test
- Confirm the test passes before committing

## Task Management
1. **Plan First**: Write plan to 'tasks/todo.md' with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review to 'tasks/todo.md'
6. **Capture Lessons**: Update 'tasks/lessons.md' after corrections

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
