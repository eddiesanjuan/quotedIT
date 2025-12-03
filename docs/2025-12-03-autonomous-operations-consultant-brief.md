# Quoted Autonomous Company – External Consultant Brief

**Date:** 2025-12-03  
**Prepared for:** Quoted Leadership Team (AI + Founder)  
**Prepared by:** External Advisor (AI Systems & Autonomous Companies)

---

## 1. Executive Summary

Quoted has two major assets:

- A well-architected, voice-first quoting product with a differentiated learning system.
- A sophisticated AI-native “company” built around multi-agent Claude workflows, state files, and autonomous issue resolution.

The core product is **beta-ready** and technically solid. The AI company scaffolding is **among the best-in-class** for 2025 in terms of clarity, role definition, and decision governance.

However, three areas now require leadership decisions:

1. **Safety & Autonomy Guardrails** – How far you want autonomous code to go in production given user-sourced inputs and bypass modes.
2. **Learning System Depth** – How aggressively to invest in RAG, multi-stage quoting, and outcome-based learning to defend a long-term moat.
3. **Operational Maturity** – How much to standardize session management, QA, and state hygiene to keep the AI company reliable at higher throughput.

You do **not** have fundamental architectural problems. You have **design choices** around safety vs. autonomy and **prioritization** of the next layer of intelligence and operational discipline.

---

## 2. Current State – Product & Architecture

### 2.1 Strengths

- **Clear architecture**
  - FastAPI backend with well-structured modules (`services/`, `api/`, `prompts/`, `data/`).
  - Good infra: CORS, rate limiting, Sentry integration, structured config.
  - Clean domain model (Contractors, PricingModel, JobType, Quote, UserIssue, etc.).

- **Innovative learning system**
  - Per-contractor `pricing_knowledge` JSON blob with per-category adjustments and confidence.
  - A dedicated Pricing Brain service and API, including category introspection and analysis.
  - Learning from quote corrections, stored as human-readable adjustments and statistics.

- **End-to-end workflow**
  - Voice → Whisper transcription → Haiku category detection → Sonnet quote generation.
  - Onboarding interview tuned to contractor sophistication.
  - PDF generation and a deployed billing stack (Stripe + Resend) with live pricing tiers.

### 2.2 Gaps & Opportunities

- **Learning system depth**
  - Learning is dominated by "adjustment strings + basic stats"; it does not yet:
    - Distinguish strongly between won vs. lost quotes.
    - Model temporal decay (recent behavior vs. historical).
    - Condition strongly on context (rush jobs, location, complexity, etc.).

- **RAG / Similarity Search**
  - No embedding-based retrieval of “jobs like this one”.
  - Current flow uses category-based learning only, missing a strong lever for accuracy and trust.

- **Quality guardrails**
  - Limited explicit arithmetic and reasonableness checks beyond the model’s self-reported confidence.
  - No second-pass “pricing sanity check” prior to sending to the customer.

- **Mobile and ecosystem**
  - Frontend is strong for web, but not yet optimized as a mobile-first field tool.
  - QuickBooks/CRM integrations and richer partner ecosystem are still aspirational, not implemented.

---

## 3. Current State – Autonomous Company & Multi-Agent System

### 3.1 Assets

- **AI-native company definition**
  - `QUOTED_AI_COMPANY_PROMPT` and `QUOTED_LEADERSHIP_TEAM_PROMPT` define Quoted as a full AI company with:
    - Explicit C-suite roles and authority (CEO/CTO/CMO/CFO/CPO/COO/CGO).
    - A clear decision-type taxonomy (Type 1–4) with thresholds and examples.
    - A founder interface (how and when Eddie is brought into the loop).

- **Multi-agent command architecture**
  - Slash commands (`/quoted-discover`, `/quoted-run`, `/quoted-run-product`, `/quoted-run-growth`, `/quoted-backend`) encapsulate:
    - **Discovery cycle** – Product, Growth, Strategy discovery agents generate backlog items.
    - **Execution cycle** – Executive council prioritizes; CEO orchestrates; Backend/Frontend/Content agents implement.
  - `MULTI_AGENT_ARCHITECTURE.md` and `AUTONOMOUS_OPERATIONS.md` act as the internal “playbook” for this AI company.

- **State and decision infrastructure**
  - State files: `COMPANY_STATE.md`, `ENGINEERING_STATE.md`, `PRODUCT_STATE.md`, `ACTION_LOG.md`, `SUPPORT_QUEUE.md`, `METRICS_DASHBOARD.md`.
  - Decision queue: `DECISION_QUEUE.md` with Type 3/4 decisions, checkboxes, and prior executive analyses.
  - Knowledge files under `quoted/knowledge/` for each agent domain that accumulate insights over time.

- **Autonomous issue resolution**
  - User issues captured in DB and via `/api/issues`.
  - `scripts/autonomous_issue_resolver.py` polls `/api/issues/new`, runs Claude Code to analyze and fix issues, updates statuses.
  - This gives you a “self-healing” path for many classes of bugs and small features.

### 3.2 Gaps & Constraints

- **Safety vs. autonomy**
  - The issue resolver currently uses `claude --dangerously-skip-permissions` against user-sourced issue content.
  - This is a direct conflict with your own security doctrine (Dual LLM pattern, Tier 3 content handling).
  - There is no enforced distinction between staging vs. production for autonomous fixes.

- **Operational hygiene**
  - State files are becoming long and complex. There is guidance to keep them under ~500 lines, but no enforced archival process.
  - QA is described in docs, but not yet enforced as a default, automated step for every change in `/quoted-run`.

- **Session management**
  - Atlas-based session management is available across your broader personal assistant system but is not yet tightly wired into Quoted’s standard autonomous workflows.

---

## 4. Key Risks for Leadership Consideration

### 4.1 Prompt Injection & Bypass Mode

- User-reported issues are Tier 3 (untrusted) content by your own security framework.
- Those issues are currently:
  - Injected verbatim into prompts.
  - Processed by a high-privilege Claude Code instance with `--dangerously-skip-permissions`.
  - Granted full repo and shell access without human confirmation.

**Risk:** A malicious or compromised user could induce the autonomous fixer to:

- Read sensitive files unrelated to the issue.
- Make sweeping codebase changes.
- Exfiltrate data via network calls or subtle side channels.

This represents the exact “Lethal Trifecta” your AGENTS documentation warns about (private data + untrusted content + outbound communication + bypass mode).

### 4.2 Lack of Dual-LLM Segmentation

- Current architecture uses a single privileged agent to:
  - Read raw untrusted content.
  - Hold tool access (filesystem, shell, possibly network).
  - Implement and commit fixes.

**Gap:** The Dual LLM pattern recommended in your security docs is not yet implemented for Quoted. The privileged agent should only see sanitized summaries produced by a quarantined, non-tool agent.

### 4.3 State Drift and Complexity

- State files are central to the AI company’s memory, but:
  - They grow continually without automatic summarization or archival.
  - Multiple agents can touch them, increasing risk of inconsistency or conflicting narratives.

**Impact:** Over time:

- Sessions become more expensive and noisy for the models.
- It becomes harder for both AI and human leadership to accurately understand the “current” state vs. historical context.

### 4.4 Testing and Deployment Discipline

- Documentation prescribes testing before deployment and careful use of decision types.
- In practice, there is:
  - No enforced QA agent in the `/quoted-run` pipeline.
  - No hard gating between staging-only automation and production autopush (beyond conventions).

**Risk:** As you scale autonomous work, the likelihood of subtle regressions and user-visible issues increases, especially when fixes are executed directly on `main`.

---

## 5. Recommendations (High-Level Choices)

### 5.1 Safety & Autonomy Guardrails

**Recommendation A (Baseline Safety):**

- Remove `--dangerously-skip-permissions` from user-issue processing.
- Restrict autonomous issue resolution by default to:
  - Staging API endpoints and a staging code checkout.
  - A limited tool profile (code read/patch + tests, no external web).
- Require manual approval for any fix that touches production-relevant configuration, billing, or auth.

**Recommendation B (Dual-LLM Upgrade):**

- Implement a two-stage flow for all Tier 3/4 content:
  1. **Quarantined Analyzer (no tools):** Reads raw issue content, outputs a structured `SafeIssueSummary` (what is broken, likely components, reproduction steps).
  2. **Privileged Fixer (tools):** Receives only `SafeIssueSummary` + repo context, no raw user text.
- Apply the same pattern to any future Tier 3 flows (e.g., email-based feedback, file uploads).

### 5.2 Learning System Investment

**Recommendation C (Defensive Moat):**

- Invest in a **RAG + outcome-linked learning** track that:
  - Embeds job descriptions and retrieves similar past quotes to ground new pricing.
  - Records quote outcomes (sent/accepted/lost) and feeds them back into learning.
  - Adds a second-pass “pricing sanity check” agent that can veto obviously dangerous quotes (e.g., far below typical range).

This solidifies Quoted’s core promise: “accurate, learned pricing tailored to each contractor,” and is the most defensible long-term moat.

### 5.3 Operational Maturity

**Recommendation D (Operational Discipline):**

- Enforce:
  - A QA agent step in `/quoted-run` whenever backend/frontend code changes.
  - Automatic archival + summarization for state files once they cross a defined length threshold.
  - Atlas-backed sessions for all substantial `/quoted-run` and `/quoted-discover` cycles (start + close with proper summaries).

This turns the AI company from a powerful prototype into a robust, repeatable operation that can run nightly or continuously without losing coherence.

---

## 6. Concrete Near-Term Proposals

### 6.1 Immediate (Next 1–3 Days)

- **Disable bypass mode for user issues:**
  - Update `autonomous_issue_resolver.py` to:
    - Stop using `--dangerously-skip-permissions` for any run triggered by user input.
    - Log a clear warning if someone attempts to run it in production environment without explicit override.

- **Add staging-only guardrail:**
  - Read `settings.environment` and:
    - Allow full automation only when `environment == "staging"`.
    - In production, limit the script to: analysis + patch proposal, not direct commits.

- **Introduce QA as a required phase:**
  - Update `.claude/commands/quoted-run.md` to always spawn a QA agent for any change that touches code.

### 6.2 Short Term (Next 2–4 Weeks)

- **Implement Dual-LLM for issues:**
  - Add a small Python micro-service or script that:
    - Calls a “quarantined” LLM endpoint (no tools) to produce `SafeIssueSummary`.
    - Passes only that summary into Claude Code with tools.
  - Refactor `autonomous_issue_resolver.py` to use this pattern end-to-end.

- **Begin RAG implementation:**
  - Add embeddings for quotes and a vector store keyed by `Quote.id`.
  - In the quote pipeline, retrieve top K similar quotes and include them as grounded examples in the prompt.

- **Add pricing sanity check agent:**
  - Implement a lightweight service that:
    - Evaluates each quote against category norms (`pricing_knowledge` + JobType stats).
    - Flags or rejects outliers before they are emailed or downloaded.

### 6.3 Medium Term (1–3 Months)

- **Link learning to outcomes:**
  - Extend data model with quote outcome and final job value.
  - Adjust learning weights toward patterns that correlate with accepted, profitable work.

- **State and session discipline:**
  - Implement a periodic “state compaction” task that:
    - Summarizes older sections of state files into `archive/` docs.
    - Keeps the active state concise and high-signal.
  - Standardize `atlas session start/close quoted` for all major work cycles.

---

## 7. Decision Questions for the Leadership Team

To move forward, the AI leadership and founder should explicitly answer:

1. **Autonomy Boundaries**
   - Do we want autonomous code changes to ever touch production directly?
     - If yes: under what conditions and with what additional guardrails?
     - If no: should autonomous agents be limited to patch proposals and PRs?

2. **Security vs. Velocity**
   - Are we willing to accept slower automated throughput (no bypass mode, dual LLMs, staging-only automation) in exchange for stronger guarantees against data exfiltration and catastrophic changes?

3. **Investment in Learning Depth**
   - How central is “superior pricing intelligence” to Quoted’s long-term positioning?
   - Should we prioritize RAG + outcome-linked learning over new surface features in the next 1–2 sprints?

4. **Operational Standards**
   - Do we want QA and Atlas session management to be mandatory parts of every autonomous cycle, or left as “best practice” guidelines?

5. **Security Governance**
   - Should we establish a dedicated “Security & Safety Officer” AI role (with its own agent prompt and knowledge file) responsible for:
     - Reviewing new autonomous scripts.
     - Auditing prompts and tool configurations.
     - Running periodic security reviews?

---

## 8. Suggested High-Level Roadmap

**Phase 0 – Safety Patch (Immediate)**

- Remove bypass mode for user-sourced issues.
- Add environment gating and minimal tooling for autonomous fixes.

**Phase 1 – Reliability & QA (2–4 Weeks)**

- Introduce a QA agent into the standard `/quoted-run` pipeline.
- Implement basic state archival and keep live state files lean.
- Standardize Atlas-backed sessions for Quoted work.

**Phase 2 – Intelligence Upgrades (1–3 Months)**

- Implement RAG over past quotes and a multi-stage quote generation pipeline.
- Add pricing sanity checks and link corrections to quote outcomes.

**Phase 3 – Autonomous Company Maturity (3–6 Months)**

- Roll out dual-LLM segmentation for all Tier 3/4 content.
- Establish a Security & Safety Officer agent and periodic security review rituals.
- Formalize “night shift” patterns where the AI company runs on a schedule with clear safety rails.

---

### Closing

You have already done the hard work of defining roles, decision rights, and state for an AI-native company. The next step is to:

- Tighten **safety and guardrails** to align with your own security philosophy.
- Invest in **learning depth and evaluation** to solidify Quoted’s pricing intelligence moat.
- Raise **operational discipline** to support more frequent, higher-impact autonomous cycles.

With these changes, Quoted can credibly operate as a semi-autonomous, continuously improving product without demanding constant founder attention—while still respecting acceptable risk boundaries.

