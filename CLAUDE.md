# AI Influencer Marketing Agency

## Project Overview
AI-powered influencer marketing agency operating across CEE (Poland, Romania, Czech Republic). Core differentiator is using AI to replace the relationship-heavy, high-margin (20%+) model of traditional agencies with data-driven, outcome-based services at lower margins (10-15%). Multi-market from day one — cross-border capability is the structural advantage over relationship-based incumbents.

## Business Strategy
- Target underserved segments: D2C e-commerce, startups, fraud-burned companies
- Lead with free brand audits as client acquisition tool
- Sell outcomes (ROI, conversions) not access (influencer relationships)
- Undercut incumbents on margin via lower operational costs
- Multi-market CEE coverage (PL/RO/CZ) — serve cross-border campaigns traditional agencies can't

## Competitive Landscape
- **Modash** — SaaS tool, 350M+ profiles, self-serve. Not an agency. Potential data source for us.
- **Dash Social** — Enterprise social suite, influencer is one module. Not competing with us.
- **Slice.id** — Closest model (SaaS + managed services), but Indonesia-focused.
- **Traditional CEE agencies** — Relationship-based, 20%+ margins, single-market.

## Build Roadmap
1. **Brand Audit Generator** (current) — lead magnet / cold outreach tool
2. **Influencer Scoring & Matching Tool** — core service delivery
3. **Client Dashboard** — reporting & retention

## Tech Stack
TBD — to be decided when we start building the audit tool.

## Project Structure
TBD — empty project, no code yet.

## Git Rules

**Claude must ask permission before any git operation.**

**FORBIDDEN TO PUSH DIRECTLY TO MAIN. Always create a feature branch and PR.**

- Branches: `main` (prod), `feature/*`, `fix/*`, `hotfix/*`
- Commits: `type(scope): description` — types: feat, fix, docs, refactor, test, chore
- PRs: feature/* → main
- **Merge commits:** Never use default "Merge pull request #X from ..." messages. Use descriptive messages following conventional commit format, e.g., `feat(mobile): add platform badges and colors`
- **Before pushing:** Always check if there are new PR reviews to address. Fix all issues before pushing to avoid triggering multiple CI workflows.
- **False positive reviews:** If reviewer flags issues that don't exist in actual code (e.g., claims missing dependency that exists), ignore them. Refactoring can happen later on main branch.
- **Maintain .gitignore proactively:** When adding files, dependencies, or tooling — check if anything new should be gitignored. Don't wait to be told. If it shouldn't be in the repo (lockfiles from wrong package managers, build artifacts, caches, secrets), add it to .gitignore immediately.

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
