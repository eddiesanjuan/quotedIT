# Quoted Audit & Innovation Report (GPT-5.2-Codex)

**Date**: 2025-12-25  
**Prepared by**: GPT-5.2-Codex  
**Inputs**:
- `.claude/commands/audit-and-innovate.md` (command analyzed and applied)
- Repository source code (backend + frontend)

---

## Executive summary

Quoted has strong product direction (voice-first quoting + learning + CRM). The biggest risks are not “idea-level” — they’re **deployment realities**:
- an **in-process scheduler** running under **multi-worker** execution (duplicate jobs and emails)
- an **import-time DB engine config** that **crashes** under SQLite (blocks dev/CI)
- **public demo endpoints** shipping in a production router surface
- **unauthenticated onboarding session** read/continue endpoints (privacy + cost)
- rate limiting that is **process-local** and likely **proxy-IP-naive**

These are solvable, but they must be prioritized before scaling users.

---

## Part 1: Critical fixes (do these first)

1) **Stop duplicate schedulers across workers** (`Procfile:1`, `backend/main.py:109`)  
2) **Fix SQLite engine config + avoid import-time engine creation** (`backend/services/database.py:27`, `backend/services/__init__.py:11`)  
3) **Remove or gate public contractor demo endpoints** (`backend/api/contractors.py:183`, `backend/api/contractors.py:219`, `backend/api/contractors.py:467`)  
4) **Secure onboarding session endpoints + add rate limits** (`backend/api/onboarding.py:161`, `backend/api/onboarding.py:549`, `backend/api/onboarding.py:561`)  
5) **Make rate limiting real under multi-worker + proxies** (`backend/services/rate_limiting.py:142`, `Procfile:1`)

---

## Part 2: High priority improvements (next 1–2 weeks)

- Fix invoice numbering concurrency + add uniqueness guard (`backend/api/invoices.py:161`, `backend/models/database.py:468`)
- Lock down testimonials admin access (`backend/api/testimonials.py:87`)
- Validate task.customer_id ownership (`backend/api/tasks.py:382`)
- Add explicit audio upload size limits (`backend/api/quotes.py:781`)
- Upgrade vulnerable dependencies (see `requirements.txt:5`)

---

## Part 3: Innovation roadmap (what to build once foundations are stable)

### Immediate (this month)
- Outcome Intelligence v1 (win/loss + reasons)
- Clarification-first quoting
- Voice commands for quote editing

### Next quarter
- One-click acceptance → deposit → schedule
- Follow-up sequences productization
- QuickBooks/Jobber integrations

### Future vision
- Site visit copilot
- Interactive options-driven quotes (good/better/best)

---

## Part 4: Recommended next steps (concrete)

1. Decide on background jobs architecture (single worker / queue / locking) and implement it.
2. Make backend importable in a default local environment (SQLite) to unblock CI and developer velocity.
3. Audit unauthenticated endpoints and explicitly classify each as:
   - public by design (with a token/secret)
   - internal/admin
   - accidental exposure
4. Add a lightweight “security + reliability” CI loop:
   - `pip-audit`
   - import smoke test
   - unit tests

---

## Appendix: Detailed outputs

- `.claude/audit-innovation-outputs-gpt-5.2-codex/GPT-5.2-Codex_phase1-holes.md`
- `.claude/audit-innovation-outputs-gpt-5.2-codex/GPT-5.2-Codex_phase2-polish.md`
- `.claude/audit-innovation-outputs-gpt-5.2-codex/GPT-5.2-Codex_phase3-innovations.md`

