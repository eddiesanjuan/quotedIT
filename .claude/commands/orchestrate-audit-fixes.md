# Orchestrate Audit Fixes

## Command Definition
```yaml
name: orchestrate-audit-fixes
description: Comprehensive 8-phase orchestrator to fix all 115 issues from the Audit & Innovation report
trigger: /orchestrate-audit-fixes
```

## Overview

This orchestrator deploys up to **25 specialized agents** across **8 phases** to systematically fix every issue identified in the comprehensive audit. Each phase has verification checkpoints and rollback procedures.

**Source**: `.claude/audit-innovation-outputs/FINAL_REPORT.md`
**State File**: `.claude/audit-fixes-state.md`

---

## Quick Start

```bash
# Check status and continue from where you left off
/orchestrate-audit-fixes

# Run specific phase
/orchestrate-audit-fixes --phase=3

# Status only (no execution)
/orchestrate-audit-fixes --status

# Reset and start fresh
/orchestrate-audit-fixes --reset
```

---

## THIN ORCHESTRATOR PATTERN (MANDATORY)

**This orchestrator MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator ONLY:
- Read/update state file (`.claude/audit-fixes-state.md`)
- Spawn Task agents with detailed prompts
- Collect TaskOutput and synthesize
- Decide phase transitions

### Orchestrator MUST NOT:
- Write/modify code directly (spawn agent)
- Run tests directly (spawn agent)
- Create commits directly (spawn agent)
- Make browser interactions directly (spawn agent)
- Fix bugs directly (spawn agent)

### Correct Execution Pattern:
```
1. Read state file → determine current phase
2. Spawn Task agent(s) with detailed prompt(s)
3. If parallel: spawn multiple agents, use run_in_background: true
4. Wait for TaskOutput (blocking or polling)
5. Update state file with findings/results
6. Repeat for next agent/phase
```

---

## Browser Automation for QA Subagents

**Subagents have different MCP tool availability than main context.**

### Working Tools for Subagents:
```
mcp__claude-in-chrome__tabs_context_mcp    # Get tab context (ALWAYS FIRST)
mcp__claude-in-chrome__navigate            # Go to URL (requires tabId)
mcp__claude-in-chrome__computer            # Screenshots (action: "screenshot"), clicks, typing
mcp__claude-in-chrome__resize_window       # Viewport testing
mcp__claude-in-chrome__read_console_messages  # JS errors
mcp__claude-in-chrome__read_network_requests  # API calls
mcp__claude-in-chrome__find                # Find elements by description
mcp__claude-in-chrome__form_input          # Fill form fields
mcp__claude-in-chrome__read_page           # Read page accessibility tree
mcp__claude-in-chrome__get_page_text       # Extract page text
```

### DO NOT USE in Subagents:
```
mcp__claude-in-chrome__browser_snapshot    # NOT available to subagents
mcp__plugin_playwright_playwright__*       # Conflicts with Claude-in-Chrome
```

### Screenshot Pattern for Subagent Prompts:
```markdown
BROWSER SETUP:
1. Call mcp__claude-in-chrome__tabs_context_mcp to get available tabs
2. Use an existing tab or note if you need to create one
3. For screenshots, use: mcp__claude-in-chrome__computer with action: "screenshot"
4. DO NOT use browser_snapshot (not available to subagents)
5. If browser tools fail, fall back to code inspection using Read/Grep
```

---

## Phase Structure

| Phase | Name | Agents | Focus |
|-------|------|--------|-------|
| 0 | Context Loading | 1 | Load state, determine resume point |
| 1 | Critical Security | 3 | Rate limiting, XSS, JWT security |
| 2 | API & Database | 4 | Undefined vars, race conditions, indexes |
| 3 | Copy & Docs | 2 | Pricing sync, terminology |
| 4 | Loading & Feedback | 4 | PDF states, toasts, errors, actions |
| 5 | Mobile & Accessibility | 3 | Touch targets, empty states, timing |
| 6 | Error Handling | 4 | Retry logic, messages, offline, voice |
| 7 | UX Polish | 4 | Help text, confirmations, validation |
| 8 | Verification | 3 | Security, functional, UX testing |

**Total**: Up to 25 agents, deployed in parallel within phases

---

## Execution Instructions

### Phase 0: Context Loading (Required First)

**Agent Count**: 1 (orchestrator itself)

Read and understand current state:

```
MANDATORY FIRST STEPS:
1. Read `.claude/audit-fixes-state.md` (if exists)
2. Read `.claude/audit-innovation-outputs/FINAL_REPORT.md`
3. Read `.claude/audit-innovation-outputs/phase1-holes.md`
4. Read `.claude/audit-innovation-outputs/phase2-polish.md`
5. Check git status for any uncommitted work
6. Determine resume point (Phase 1 if fresh start)
```

If state file doesn't exist, create it:

```markdown
# Audit Fixes State

## Status
Phase: 1
Started: [TIMESTAMP]
Last Updated: [TIMESTAMP]

## Phase Completion
- [ ] Phase 1: Critical Security Fixes
- [ ] Phase 2: API & Database Fixes
- [ ] Phase 3: Copy & Documentation Sync
- [ ] Phase 4: Loading & Feedback States
- [ ] Phase 5: Mobile & Accessibility
- [ ] Phase 6: Error Handling & Recovery
- [ ] Phase 7: UX Polish
- [ ] Phase 8: Verification & Testing

## Active Agents
None

## Commits
(Will be updated after each phase)

## Issues Fixed
0/115
```

---

### Phase 1: Critical Security Fixes

**Agent Count**: 3 parallel agents
**Priority**: CRITICAL - These are security vulnerabilities

#### Agent 1A: Rate Limiting Implementation

**Target**: `backend/api/auth.py`
**Issue**: SEC-001 - No rate limiting on auth endpoints

```
TASK: Implement rate limiting on all /api/auth/* endpoints

IMPLEMENTATION:
1. Install slowapi: Add to requirements.txt
2. Create rate limiter in backend/api/auth.py:
   - Import: from slowapi import Limiter
   - Import: from slowapi.util import get_remote_address
   - Create: limiter = Limiter(key_func=get_remote_address)
3. Add decorator to auth endpoints:
   - /api/auth/magic-link: @limiter.limit("5/minute")
   - /api/auth/verify: @limiter.limit("10/minute")
   - /api/auth/refresh: @limiter.limit("20/minute")
4. Add limiter to FastAPI app in main.py:
   - app.state.limiter = limiter
   - app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

VERIFICATION:
- Test: Call /api/auth/magic-link 6 times rapidly
- Expected: 429 Too Many Requests on 6th call
```

#### Agent 1B: XSS Vulnerability Fix

**Target**: `frontend/index.html:12077-12093`
**Issue**: FE-001 - User data rendered via unsafe DOM methods

```
TASK: Replace all unsafe DOM rendering with safe alternatives

SEARCH FOR patterns that directly inject user data into DOM:
- Unsafe string concatenation into HTML
- Dynamic code execution with user data
- Direct DOM property assignment with untrusted content

REPLACE WITH:
- element.textContent = userData (for text content)
- document.createElement() + appendChild() (for HTML structure)
- DOMPurify.sanitize() if HTML rendering is absolutely required

SPECIFIC LOCATIONS (from audit):
- index.html:12077-12093 - Quote display area
- Any location where user names, quote content, or customer data is rendered

VERIFICATION:
- Test: Create quote with content containing script tags
- Expected: Script tags rendered as text, not executed
```

#### Agent 1C: JWT Security Hardening

**Target**: `backend/api/auth.py`
**Issue**: SEC-003 - JWT refresh unlimited

```
TASK: Implement JWT refresh token rotation and limits

IMPLEMENTATION:
1. Add refresh_count to token payload
2. Track token lineage (parent token ID)
3. Limit refresh chain to 10 rotations max
4. Implement token revocation on suspicious activity

CHANGES:
- Add to token payload: "refresh_count": int
- On refresh: increment count, reject if > 10
- Add token_family tracking for rotation
- Invalidate all tokens in family on reuse detection

VERIFICATION:
- Test: Refresh same token 11 times
- Expected: 401 on 11th refresh with "max refreshes exceeded"
```

**Phase 1 Completion Checklist**:
```
[ ] Rate limiting installed and tested
[ ] XSS vulnerabilities patched
[ ] JWT refresh limits implemented
[ ] All changes committed: "fix: Critical security patches (SEC-001, FE-001, SEC-003)"
[ ] State file updated
```

---

### Phase 2: API & Database Fixes

**Agent Count**: 4 parallel agents
**Priority**: CRITICAL/HIGH - These cause crashes and data corruption

#### Agent 2A: API Undefined Variable Fix

**Target**: `backend/api/quotes.py:~756`
**Issue**: API-001 - `auth_db` undefined variable

```
TASK: Fix undefined auth_db variable in quotes.py

SEARCH: Find all uses of `auth_db` in quotes.py
VERIFY: Ensure Depends(get_db) is properly imported and used

LIKELY FIX:
- Change: auth_db → db (if db is the correct session variable)
- OR: Add missing parameter: auth_db: Session = Depends(get_db)

VERIFICATION:
- Test: Call the affected endpoint
- Expected: 200 OK (not 500 NameError)
```

#### Agent 2B: Race Condition Fixes

**Targets**:
- `backend/services/billing.py:187`
- `backend/api/referral.py:168-169`

**Issues**: DB-001, DB-002 - Race conditions in counters

```
TASK: Replace read-modify-write with atomic SQL UPDATE

BILLING (billing.py:187):
BEFORE (vulnerable):
  usage = db.query(Usage).filter(...).first()
  usage.count = usage.count + 1
  db.commit()

AFTER (atomic):
  db.execute(
    update(Usage)
    .where(Usage.id == usage_id)
    .values(count=Usage.count + 1)
  )
  db.commit()

REFERRAL (referral.py:168-169):
Same pattern - replace read-modify-write with atomic UPDATE

VERIFICATION:
- Simulate concurrent requests (10 parallel calls)
- Expected: Final count matches request count exactly
```

#### Agent 2C: Database Indexes

**Target**: `backend/models/database.py` or migration file
**Issue**: DB-004 - Missing indexes on hot paths

```
TASK: Add composite indexes for frequently queried columns

INDEXES TO ADD:
1. quotes table: (contractor_id, created_at DESC)
2. quotes table: (contractor_id, status)
3. customers table: (contractor_id, name)
4. learning_statements table: (contractor_id, category)

IMPLEMENTATION:
Option A (SQLAlchemy model):
  __table_args__ = (
    Index('ix_quotes_contractor_created', 'contractor_id', 'created_at'),
  )

Option B (Alembic migration):
  op.create_index('ix_quotes_contractor_created', 'quotes', ['contractor_id', 'created_at'])

VERIFICATION:
- Run EXPLAIN on common queries
- Expected: Index scans instead of sequential scans
```

#### Agent 2D: Cascade Delete Review

**Target**: `backend/models/`
**Issue**: DB-003 - No cascade delete enforcement

```
TASK: Review and fix foreign key cascade rules

CHECK RELATIONSHIPS:
1. contractor -> quotes (should cascade delete)
2. contractor -> customers (should cascade delete)
3. quote -> line_items (should cascade delete)
4. customer -> quotes (should SET NULL or restrict)

FOR EACH RELATIONSHIP:
- Verify cascade behavior is intentional
- Add explicit cascade="all, delete-orphan" where appropriate
- Add ondelete="CASCADE" to foreign key definitions

VERIFICATION:
- Delete test contractor
- Expected: Related quotes and customers deleted (or proper error)
```

**Phase 2 Completion Checklist**:
```
[ ] auth_db undefined fixed
[ ] Race conditions eliminated with atomic updates
[ ] Database indexes added
[ ] Cascade delete rules reviewed
[ ] All changes committed: "fix: API and database stability fixes (API-001, DB-001-004)"
[ ] State file updated
```

---

### Phase 3: Copy & Documentation Sync

**Agent Count**: 2 parallel agents
**Priority**: CRITICAL - Legal/trust issue

#### Agent 3A: Pricing Sync

**Targets**:
- `frontend/terms.html:273-278`
- `frontend/help.html:561`, `help.html:680`

**Issues**: CP-001, CP-002 - Pricing and plan name discrepancies

```
TASK: Sync all documents to current pricing ($9/$19/$39 structure)

CORRECT PRICING (from landing.html):
- Starter: $9/mo (75 quotes)
- Pro: $19/mo (200 quotes)
- Team: $39/mo (unlimited)

TERMS.HTML FIXES:
- Line ~273-278: Update pricing table to match
- Remove any references to $19/$39/$79

HELP.HTML FIXES:
- Line ~561: Update quote limits if mentioned
- Line ~680: Change "Pro/Business" to "Pro/Team"
- Search for any other plan name references

ALSO CHECK:
- privacy.html (any pricing mentions)
- Any email templates with pricing

VERIFICATION:
- Search all frontend files for: $19, $39, $79, "Business"
- Expected: Only correct values remain
```

#### Agent 3B: Terminology Standardization

**Targets**: Multiple frontend files
**Issues**: CP-003, CP-004 - Quote/Estimate and Client/Customer inconsistency

```
TASK: Standardize terminology across all files

RULES:
1. "Quote" for the document, "Estimate" only for the total price line
2. "Customer" everywhere (not "Client")

SEARCH AND REPLACE:
- "client" → "customer" (case-insensitive, excluding code variables)
- "estimate" → "quote" (where referring to document, not price)

FILES TO CHECK:
- landing.html
- try.html (demo)
- help.html
- index.html (UI strings)
- quote-view.html

EXCLUSIONS:
- Don't change code variable names (clientId, etc.)
- Keep "Estimated Total" as-is (this is correct)

VERIFICATION:
- Search for "client" in user-visible strings
- Expected: All instances say "customer"
```

**Phase 3 Completion Checklist**:
```
[ ] Pricing synced across all documents
[ ] Plan names updated (Pro/Team not Pro/Business)
[ ] Terminology standardized (customer, not client)
[ ] All changes committed: "fix: Documentation and terminology sync (CP-001-004)"
[ ] State file updated
```

---

### Phase 4: Loading & Feedback States

**Agent Count**: 4 parallel agents
**Priority**: HIGH - User experience

#### Agent 4A: PDF Download Loading States

**Target**: `frontend/index.html:8521,11305,12465`
**Issue**: LF-001 - PDF download has no loading state

```
TASK: Add loading indicators to all PDF download buttons

IMPLEMENTATION:
1. Find all PDF download buttons/links
2. Add click handler that:
   - Shows "Generating PDF..." text
   - Disables button
   - Shows spinner icon
3. On complete:
   - Restore button text
   - Re-enable button

PATTERN:
  async function downloadPDF(quoteId) {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Generating...';
    btn.disabled = true;
    try {
      // existing download logic
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

VERIFICATION:
- Click PDF download button
- Expected: Button shows loading state during generation
```

#### Agent 4B: Replace Browser Alerts with Toasts

**Target**: Multiple locations (~15 alert() calls)
**Issue**: CP-006 - Generic browser alerts instead of toasts

```
TASK: Replace all browser alert dialogs with toast system

SEARCH FOR:
- alert( function calls
- window.alert( function calls

REPLACE WITH:
- showError(message) for errors
- showSuccess(message) for success
- showWarning(message) for warnings

TOAST FUNCTIONS (verify these exist):
- showError(message)
- showSuccess(message)
- showWarning(message) or create if missing

VERIFICATION:
- Trigger each replaced alert scenario
- Expected: Toast notification appears, not browser dialog
```

#### Agent 4C: Error State Distinction

**Target**: `loadQuotes()`, `loadCustomers()` in index.html
**Issue**: LF-002 - Error states indistinguishable from empty states

```
TASK: Make error states visually distinct with retry button

IMPLEMENTATION:
For each list loading function:

1. Create error state HTML:
   <div class="error-state">
     <span class="error-icon">⚠️</span>
     <p>Failed to load. Please try again.</p>
     <button onclick="retry()">Retry</button>
   </div>

2. Style differently from empty state:
   - Different icon (warning vs empty folder)
   - Different color (red/orange vs gray)
   - Includes retry button

3. Show error state on catch, not empty state

VERIFICATION:
- Simulate network error (disconnect or mock failure)
- Expected: Error state with retry button, not "No quotes yet"
```

#### Agent 4D: Quick Action Feedback

**Target**: Duplicate/delete quote, add note/tag actions
**Issue**: LF-003 - Quick actions feel laggy (no feedback)

```
TASK: Add instant visual feedback to quick actions

FOR EACH QUICK ACTION:
1. On click: immediate visual change (button state, opacity)
2. Show micro-loading indicator
3. On success: brief success feedback
4. On error: show error, revert visual state

ACTIONS TO UPDATE:
- Duplicate quote
- Delete quote
- Add note
- Add/remove tag
- Quick status change

PATTERN:
  async function duplicateQuote(id) {
    const btn = event.target;
    btn.classList.add('loading');
    try {
      await api.duplicateQuote(id);
      btn.classList.remove('loading');
      btn.classList.add('success');
      setTimeout(() => btn.classList.remove('success'), 1000);
    } catch (e) {
      btn.classList.remove('loading');
      showError('Failed to duplicate');
    }
  }

VERIFICATION:
- Click duplicate quote
- Expected: Immediate visual feedback, then success state
```

**Phase 4 Completion Checklist**:
```
[ ] PDF download shows loading state
[ ] All alerts replaced with toasts
[ ] Error states distinct from empty states
[ ] Quick actions have loading feedback
[ ] All changes committed: "fix: Loading states and user feedback (LF-001-003, CP-006)"
[ ] State file updated
```

---

### Phase 5: Mobile & Accessibility

**Agent Count**: 3 parallel agents
**Priority**: HIGH - Usability

#### Agent 5A: Touch Target Fixes

**Targets**:
- `frontend/index.html:2476` (nav labels)
- `frontend/demo.html:463,388,180,267` (various elements)

**Issues**: MOB-001 through MOB-005

```
TASK: Fix all mobile touch target and font size issues

FIXES:
1. Mobile nav label: 10px → 12px (0.75rem)
   - index.html:2476 - .mobile-nav-label font-size

2. Demo brain category value: 11px → 12px
   - demo.html:463 - .brain-category-value

3. Learn value padding: 4px → 8px 12px
   - demo.html:388 - .learn-value padding

4. Icon containers: ensure min-height 44px
   - demo.html:180,267 - parent containers of 24px icons

5. Account tabs: add scroll indicators
   - index.html:2618 - add gradient fade hints

CSS ADDITIONS:
  .mobile-nav-label { font-size: 0.75rem; }
  .brain-category-value { font-size: 0.75rem; }
  .learn-value { padding: 8px 12px; }
  .icon-button { min-height: 44px; min-width: 44px; }

VERIFICATION:
- Test on 375px viewport
- Expected: All text readable, all buttons easily tappable
```

#### Agent 5B: Empty State Improvements

**Targets**:
- Customer search results
- Dashboard tasks
- Customer detail quotes

**Issues**: ES-001, ES-002, ES-003

```
TASK: Improve empty state messaging and CTAs

FIXES:

1. Search empty state (ES-001):
   <div class="empty-state">
     <span class="empty-icon">🔍</span>
     <p>No customers match your search</p>
     <button onclick="clearSearch()">Clear Search</button>
   </div>

2. Dashboard "No tasks" (ES-002):
   - Add icon (📋 or similar)
   - Add helpful CTA link
   - Change: "No tasks" → "All caught up! No pending tasks."

3. Customer detail quotes (ES-003):
   - Add context: "No quotes for [Customer Name] yet"
   - Add CTA: "Create First Quote" button

VERIFICATION:
- Trigger each empty state
- Expected: Helpful message with clear next action
```

#### Agent 5C: Toast Duration Fix

**Target**: `showLearningToast()` function
**Issue**: LF-004 - Learning toast disappears too fast (4s)

```
TASK: Extend learning toast duration

FIND: showLearningToast function
CHANGE: 4000ms → 6000ms

ALSO CHECK:
- Is toast clickable? If yes, 6s is minimum
- Other toast durations for consistency
- Consider making duration configurable by toast type

RECOMMENDED DURATIONS:
- Success (non-clickable): 3s
- Info/Learning (clickable): 6s
- Error: 8s or until dismissed
- Warning: 5s

VERIFICATION:
- Trigger learning toast
- Expected: Stays visible for 6 seconds
```

**Phase 5 Completion Checklist**:
```
[ ] Mobile fonts increased to readable sizes
[ ] Touch targets meet 44px minimum
[ ] Empty states have helpful CTAs
[ ] Toast duration extended to 6s
[ ] All changes committed: "fix: Mobile accessibility and empty states (MOB-001-005, ES-001-003, LF-004)"
[ ] State file updated
```

---

### Phase 6: Error Handling & Recovery

**Agent Count**: 4 parallel agents
**Priority**: MEDIUM-HIGH

#### Agent 6A: Retry Logic Implementation

**Target**: All API call error handlers
**Issue**: Error states need retry buttons

```
TASK: Add retry functionality to all failed API calls

PATTERN:
  async function loadData(retryCount = 0) {
    try {
      const data = await api.getData();
      renderData(data);
    } catch (e) {
      if (retryCount < 3) {
        // Auto-retry with exponential backoff
        setTimeout(() => loadData(retryCount + 1), 1000 * Math.pow(2, retryCount));
      } else {
        showErrorWithRetry('Failed to load data', () => loadData(0));
      }
    }
  }

FUNCTIONS TO UPDATE:
- loadQuotes()
- loadCustomers()
- loadDashboard()
- loadSettings()
- Any data fetching function

VERIFICATION:
- Simulate 4 consecutive failures
- Expected: 3 auto-retries, then error with manual retry button
```

#### Agent 6B: User-Friendly Error Messages

**Targets**:
- `index.html:11240,11336`
- `quote-view.html:1139,1180`

**Issue**: CP-005 - Raw error.message exposed to users

```
TASK: Wrap technical errors in user-friendly messages

FIND: catch blocks that display error.message directly

REPLACE WITH:
  catch (error) {
    console.error('API Error:', error); // Log for debugging
    const userMessage = getUserFriendlyMessage(error);
    showError(userMessage);
  }

CREATE HELPER:
  function getUserFriendlyMessage(error) {
    const messages = {
      'NetworkError': 'Unable to connect. Check your internet.',
      'TimeoutError': 'Request timed out. Please try again.',
      '401': 'Session expired. Please log in again.',
      '403': 'You don\'t have permission for this action.',
      '404': 'Item not found. It may have been deleted.',
      '500': 'Something went wrong. Please try again.',
    };
    return messages[error.code] || messages[error.status] ||
           'Something went wrong. Please try again.';
  }

VERIFICATION:
- Trigger various error types
- Expected: Friendly messages, not technical stack traces
```

#### Agent 6C: Offline Detection

**Target**: Global application state
**Issue**: FE-002 - No offline handling

```
TASK: Add offline detection and user notification

IMPLEMENTATION:

1. Add connectivity listener:
  window.addEventListener('online', () => {
    hideOfflineBanner();
    retryQueuedActions();
  });
  window.addEventListener('offline', () => {
    showOfflineBanner();
  });

2. Create offline banner:
  <div id="offline-banner" class="hidden">
    <span>⚠️ You're offline. Changes will sync when connected.</span>
  </div>

3. Queue actions when offline:
  - Store failed writes in localStorage
  - Retry when back online
  - Show pending count in banner

VERIFICATION:
- Toggle airplane mode / disconnect network
- Expected: Banner appears, actions queue, resume on reconnect
```

#### Agent 6D: Voice Recording Recovery

**Target**: Voice recording functionality
**Issue**: Voice recording stuck state possible

```
TASK: Add stuck state detection and recovery for voice recording

IMPLEMENTATION:

1. Add recording timeout (5 minutes max):
  setTimeout(() => {
    if (isRecording) {
      stopRecording();
      showWarning('Recording stopped after 5 minutes');
    }
  }, 5 * 60 * 1000);

2. Add stuck state detection:
  - If no audio data for 30 seconds, prompt user
  - If mediaRecorder errors, show recovery options

3. Add recovery UI:
  <button onclick="resetRecording()">Reset Recording</button>

4. Clear all recording state on reset:
  - Stop media tracks
  - Clear buffers
  - Reset UI to initial state

VERIFICATION:
- Start recording, wait 30 seconds with no audio
- Expected: Warning prompt, option to reset
```

**Phase 6 Completion Checklist**:
```
[ ] Retry logic with exponential backoff
[ ] User-friendly error messages
[ ] Offline detection and banner
[ ] Voice recording recovery
[ ] All changes committed: "fix: Error handling and recovery (FE-002, CP-005)"
[ ] State file updated
```

---

### Phase 7: UX Polish

**Agent Count**: 4 parallel agents
**Priority**: MEDIUM

#### Agent 7A: Help Tooltips

**Target**: Pricing settings, onboarding flows
**Issue**: Missing help tooltips

```
TASK: Add contextual help tooltips

LOCATIONS:
1. Pricing settings page
   - Base rate field: "Your starting hourly or daily rate"
   - Markup field: "Percentage added for materials"

2. Onboarding steps
   - Each step should have "?" icon with tooltip

3. Complex features
   - Learning system: "How the AI improves over time"
   - Voice templates: "Pre-set phrases for common jobs"

IMPLEMENTATION:
  <span class="help-tooltip" data-tooltip="Your explanation here">
    <span class="help-icon">?</span>
  </span>

CSS for tooltip:
  .help-tooltip[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    background: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    max-width: 200px;
  }

VERIFICATION:
- Hover over ? icons
- Expected: Helpful tooltip appears
```

#### Agent 7B: Confirmation Messages

**Target**: Destructive and important actions
**Issue**: Missing confirmation for important actions

```
TASK: Add confirmation dialogs for important actions

ACTIONS NEEDING CONFIRMATION:
1. Delete quote (already has? verify)
2. Delete customer
3. Cancel subscription
4. Clear all learning data
5. Bulk delete operations

IMPLEMENTATION:
  function confirmDelete(itemName, onConfirm) {
    const modal = showModal({
      title: 'Delete ' + itemName + '?',
      message: 'This action cannot be undone.',
      buttons: [
        { text: 'Cancel', onClick: closeModal },
        { text: 'Delete', onClick: onConfirm, class: 'danger' }
      ]
    });
  }

VERIFICATION:
- Click delete on quote
- Expected: Confirmation modal before deletion
```

#### Agent 7C: Inline Form Validation

**Target**: All forms
**Issue**: Validation only on submit, not inline

```
TASK: Add inline validation to forms

FORMS TO UPDATE:
1. Quote creation (customer name, job description)
2. Settings (email, phone formats)
3. Onboarding inputs

IMPLEMENTATION:
  <input type="email"
         oninput="validateField(this)"
         pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
  <span class="validation-message"></span>

  function validateField(input) {
    const valid = input.checkValidity();
    input.classList.toggle('invalid', !valid);
    input.nextElementSibling.textContent =
      valid ? '' : input.validationMessage;
  }

CSS:
  input.invalid { border-color: #e74c3c; }
  .validation-message { color: #e74c3c; font-size: 0.875rem; }

VERIFICATION:
- Enter invalid email
- Expected: Immediate red border and error message
```

#### Agent 7D: Legal Copy Softening

**Target**: `terms.html`, `privacy.html`
**Issue**: Harsh ALL CAPS disclaimers

```
TASK: Soften legal copy while maintaining accuracy

CHANGES:
1. Replace ALL CAPS sections with sentence case
2. Add plain-language summaries before legal sections
3. Use friendlier formatting (bullet points vs walls of text)

EXAMPLE BEFORE:
  "YOU AGREE THAT WE SHALL NOT BE LIABLE FOR ANY DAMAGES..."

EXAMPLE AFTER:
  "In plain English: If something goes wrong, our liability
   is limited to what you've paid us.

   Legal version: You agree that we shall not be liable
   for any damages..."

SECTIONS TO UPDATE:
- Limitation of liability
- Warranty disclaimers
- Indemnification

VERIFICATION:
- Read terms page
- Expected: Readable, not intimidating
```

**Phase 7 Completion Checklist**:
```
[ ] Help tooltips added to complex settings
[ ] Confirmation dialogs for destructive actions
[ ] Inline form validation
[ ] Legal copy softened
[ ] All changes committed: "fix: UX polish and help text"
[ ] State file updated
```

---

### Phase 8: Verification & Testing

**Agent Count**: 3 parallel agents
**Priority**: REQUIRED - Validates all fixes

#### Agent 8A: Security Verification

```
TASK: Verify all security fixes

TESTS:
1. Rate Limiting:
   - Call /api/auth/magic-link 10 times rapidly
   - Expected: 429 after limit reached

2. XSS Prevention:
   - Create quote with script tag content
   - View quote
   - Expected: Script rendered as text, not executed

3. JWT Security:
   - Get refresh token
   - Use it 11 times
   - Expected: Rejection after 10 uses

4. CSRF Protection (if applicable):
   - Verify all mutation endpoints have CSRF tokens

REPORT FORMAT:
| Test | Status | Notes |
|------|--------|-------|
| Rate Limiting | PASS/FAIL | Details |
| XSS Prevention | PASS/FAIL | Details |
| JWT Limits | PASS/FAIL | Details |
```

#### Agent 8B: Functional Verification

```
TASK: Verify all functional fixes

TESTS:
1. API Stability:
   - Call previously broken endpoint
   - Expected: 200 OK, not 500

2. Race Conditions:
   - Concurrent billing updates
   - Expected: Correct final count

3. Cascade Deletes:
   - Delete contractor with quotes
   - Expected: Related records handled correctly

4. All Loading States:
   - Trigger each loading scenario
   - Expected: Visual feedback present

5. Error States:
   - Simulate failures
   - Expected: Error state with retry, not empty state

REPORT FORMAT:
| Test | Status | Notes |
|------|--------|-------|
| API Stability | PASS/FAIL | Details |
```

#### Agent 8C: UX Verification

```
TASK: Verify all UX fixes

TESTS (Mobile 375px):
1. Font Sizes:
   - All text readable without zoom

2. Touch Targets:
   - All buttons easily tappable

3. Empty States:
   - Each empty state has icon, message, CTA

TESTS (General):
4. Toasts:
   - No browser alerts remain
   - Learning toast visible for 6s

5. Terminology:
   - "Customer" used consistently
   - Pricing correct everywhere

6. Help Text:
   - Tooltips appear on hover
   - Helpful and accurate

REPORT FORMAT:
| Test | Status | Notes |
|------|--------|-------|
| Font Sizes | PASS/FAIL | Details |
```

**Phase 8 Completion Checklist**:
```
[ ] All security fixes verified
[ ] All functional fixes verified
[ ] All UX fixes verified
[ ] Test reports generated
[ ] Final commit: "verify: All 115 audit fixes complete"
[ ] State file updated to COMPLETE
```

---

## Rollback Procedures

### If Phase Introduces Bugs

```bash
# Check current phase commit
git log --oneline -5

# Revert last phase commit
git revert HEAD

# Update state file to previous phase
# Re-run phase with fixes
```

### If Security Issue Discovered

```bash
# Immediate rollback
git revert [security-commit-hash]
git push origin main

# Railway will auto-deploy the revert
# Then investigate and fix properly
```

---

## Resume Procedures

### After Context Reset

```
1. Read `.claude/audit-fixes-state.md`
2. Identify current phase and completed agents
3. Continue from next incomplete agent
4. Don't repeat completed work
```

### After Partial Phase Completion

```
1. Check git log for partial commits
2. Read state file for agent completion
3. Launch only remaining agents in current phase
```

---

## Issue Reference

### Phase 1 (Critical Security)
- SEC-001: Rate limiting (/api/auth/*)
- FE-001: XSS vulnerability (unsafe DOM methods)
- SEC-003: JWT refresh unlimited

### Phase 2 (API & Database)
- API-001: auth_db undefined
- DB-001: Race condition (billing)
- DB-002: Race condition (referral)
- DB-003: Cascade delete
- DB-004: Missing indexes

### Phase 3 (Copy & Docs)
- CP-001: Pricing discrepancy
- CP-002: Plan name mismatch
- CP-003: Quote vs Estimate
- CP-004: Client vs Customer

### Phase 4 (Loading & Feedback)
- LF-001: PDF loading state
- LF-002: Error vs empty state
- LF-003: Quick action feedback
- CP-006: Alerts to toasts

### Phase 5 (Mobile & Accessibility)
- MOB-001-005: Font sizes, touch targets
- ES-001-003: Empty state improvements
- LF-004: Toast duration

### Phase 6 (Error Handling)
- FE-002: Offline handling
- CP-005: Raw error messages
- Voice stuck state recovery
- Retry logic

### Phase 7 (UX Polish)
- Help tooltips
- Confirmation dialogs
- Inline validation
- Legal copy

### Phase 8 (Verification)
- Security tests
- Functional tests
- UX tests

---

## Success Metrics

At completion:
- **0 critical issues remaining**
- **0 high priority issues remaining**
- **All 115 issues addressed**
- **Security scan passing**
- **Mobile UX score improved**
- **User-friendly error handling throughout**

---

## Execution Command

To start or continue:

```
/orchestrate-audit-fixes
```

The orchestrator will:
1. Check state file
2. Determine current phase
3. Launch appropriate agents
4. Track progress
5. Commit changes
6. Update state
7. Proceed to next phase

**Estimated total execution time**: 2-4 hours across all phases
**Agents deployed**: Up to 25 (parallel within phases)
**Commits generated**: 8 (one per phase)
