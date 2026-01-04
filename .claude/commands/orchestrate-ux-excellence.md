# Orchestrate UX Excellence - Deep Product Audit

You are initiating a **comprehensive UX excellence audit** for Quoted, Inc. This is NOT a functional test (see `/run-qa` for that). This is a deep user experience analysis by an **expert team of AI auditors**.

## Quick Start

```bash
/orchestrate-ux-excellence              # Start or continue
/orchestrate-ux-excellence --status     # Check progress
/orchestrate-ux-excellence --phase=N    # Jump to phase
/orchestrate-ux-excellence --reset      # Start fresh
```

---

## ⚠️ THIN ORCHESTRATOR PATTERN (MANDATORY)

**This orchestrator MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator Responsibilities (ONLY):
- ✅ Read and update state file (`.claude/ux-excellence-state.md`)
- ✅ Spawn Task agents for each phase using the Task tool
- ✅ Wait for agent completion using TaskOutput
- ✅ Update state file with results
- ✅ Decide phase transitions
- ✅ Synthesize findings across agents

### Orchestrator MUST NOT:
- ❌ Perform audits/testing directly in main context
- ❌ Read code files directly (spawn agent)
- ❌ Make browser interactions directly (spawn agent)
- ❌ Generate reports directly (spawn agent)
- ❌ Analyze logs directly (spawn agent)

### Correct Pattern:
```
1. Read state file → determine current phase
2. Spawn Task agent with detailed prompt
3. Wait for TaskOutput
4. Update state file with findings
5. Repeat for next agent/phase
```

### Anti-Pattern (WRONG):
```
1. Read state file
2. Navigate to landing page myself
3. Take screenshots myself
4. Analyze the page myself
5. Write findings
```

**Why?** Thin orchestration enables:
- Context preservation (main context stays clean)
- Parallel execution (multiple agents simultaneously)
- Resilience (agents can fail/retry independently)
- Better quality (agents get focused prompts)

---

## Purpose

This orchestrator acts as an **expert team of AI auditors** specializing in:
1. **Finding UX issues** - friction, confusion, dead ends
2. **Proposing innovative solutions** - not just fixes, but 10x improvements
3. **Identifying growth opportunities** - conversion optimizations
4. **Ensuring cross-platform excellence** - mobile AND desktop
5. **Learning system excellence** - deep analysis of the AI learning moat

## Critical Philosophy

**Audit as a FRESH USER** - Do not assume knowledge of how things work. Discover the app as a first-time visitor would. Every confusing moment is an issue. Every delightful surprise is an opportunity.

## Recently Deployed Features to Test

- **Interactive Tour** (Shepherd.js v11.2.0) - Dec 26
- **Immediate with Escape Hatch UX** - Voice quotes generate instantly, show transcription with Edit & Regenerate - Dec 26
- **Innovation Features INNOV-1-9** - Outcome Intelligence, Invoice Automation, Smart Reminders - Dec 25
- **Learning Excellence** - Anthropic showcase quality learning system - Dec 24
- **SEO Blog** - 7 industry-specific quoting guides - Dec 24
- **Proposify Domination Wave 1-3** - Invoicing, accept/reject, CRM - Dec 24

## Phase Structure

| Phase | Name | Agents | Focus |
|-------|------|--------|-------|
| 0 | Context Loading | 1 | State files, environment setup |
| 1 | Fresh User Discovery | 2 | Experience app as complete newcomer |
| 2 | Landing & Marketing | 2 | First impressions, conversion flow |
| 3 | Authentication & Onboarding | 3 | Signup friction, tour system, first-run |
| 4 | Core Quote Flow | 3 | Voice recording, AI generation, editing |
| 5 | Dashboard & Quote Management | 2 | Quote cards, filters, actions |
| 6 | CRM & Customers | 2 | Customer management, history |
| 7 | Tasks System | 1 | Task CRUD, automation |
| 8 | Invoicing System | 2 | Quote-to-invoice, payment tracking |
| 9 | Learning System Deep Dive | 3 | Quality scoring, relevance selection, improvements |
| 10 | Settings & Billing | 2 | Account config, subscription |
| 11 | Referral & Sharing | 2 | Share flows, referral program |
| 12 | Mobile Deep Dive | 2 | Touch targets, responsive edge cases |
| 13 | Integration Audit | 1 | Cross-feature flows, data consistency |
| 14 | Innovation Synthesis | 1 | Consolidate opportunities |
| 15 | Report & Tickets | 1 | Final report, create tickets |

---

## Tool Arsenal Reference

**CRITICAL**: Agents MUST use appropriate tools for each task.

### ⚠️ Browser Automation for Subagents (CRITICAL)

**Subagents have different tool availability than the main context.** Follow these patterns:

#### Working Pattern:
```
1. FIRST: Call mcp__claude-in-chrome__tabs_context_mcp to get valid tab IDs
2. REUSE: Navigate existing tabs (don't create new ones if possible)
3. SCREENSHOTS: Use mcp__claude-in-chrome__computer with action: "screenshot"
4. NAVIGATION: Use mcp__claude-in-chrome__navigate with valid tabId
5. FALLBACK: If browser fails, fall back to code inspection
```

#### ❌ DO NOT USE in Subagents:
- `mcp__claude-in-chrome__browser_snapshot` - NOT available to subagents
- `mcp__plugin_playwright_playwright__*` - Conflicts with Claude-in-Chrome

#### ✅ Subagent Browser Tools (Verified Working):
```
mcp__claude-in-chrome__tabs_context_mcp    # Get tab context (ALWAYS FIRST)
mcp__claude-in-chrome__navigate            # Go to URL (requires tabId)
mcp__claude-in-chrome__computer            # Screenshots, clicks, typing
mcp__claude-in-chrome__resize_window       # Viewport testing
mcp__claude-in-chrome__read_console_messages  # JS errors
mcp__claude-in-chrome__read_network_requests  # API calls
mcp__claude-in-chrome__find                # Find elements by description
mcp__claude-in-chrome__form_input          # Fill form fields
mcp__claude-in-chrome__read_page           # Read page accessibility tree
mcp__claude-in-chrome__get_page_text       # Extract page text
```

#### Screenshot Pattern for Subagents:
```
// Correct - use computer tool with screenshot action
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tabId from tabs_context_mcp>
})

// WRONG - browser_snapshot not available to subagents
mcp__claude-in-chrome__browser_snapshot  // ❌ Will fail
```

#### Tab Management:
- Get tabs FIRST before any browser operation
- One tab per subagent (avoid parallel tab creation conflicts)
- Pass tabId explicitly in prompts when orchestrator knows it
- If browser completely fails, fall back to code inspection (Read/Grep tools)

### Railway CLI (Backend Verification)
```bash
railway logs                    # View production logs
railway logs -n 100 --filter "@level:error"  # Error logs
railway variables               # Check environment
railway status                  # Deployment status
```

### GitHub CLI (Issue/PR Management)
```bash
gh issue create --title "..." --body "..."   # Create issue
gh pr create --title "..." --body "..."      # Create PR
gh issue list --label "bug"                  # List issues
```

---

## Phase 0: Context Loading

**CRITICAL**: Read state before ANY testing.

### Agent 0A: Context Loader

```markdown
TASK: Load all context for UX audit

STEPS:
1. Read ENGINEERING_STATE.md - recent deployments, known issues
2. Read COMPANY_STATE.md - current features, strategic context
3. Read DISCOVERY_BACKLOG.md - pending work, completed features
4. Read DISCOVERY_ARCHIVE.md - recently deployed features to verify
5. Read .claude/ux-excellence-state.md - resume if exists

OUTPUT:
- List of all features to test
- Known issues (don't re-report)
- Recent deployments (focus areas)
- Current blockers
- Verification checklist for recent deploys
```

### Environment Setup

```markdown
TASK: Set up browser environment

STEPS:
1. Call mcp__claude-in-chrome__tabs_context_mcp to get tab context
2. Create a fresh tab with mcp__claude-in-chrome__tabs_create_mcp
3. Navigate to https://quoted.it.com
4. Take initial screenshot at 1440px desktop

VERIFY:
- Tab created and responding
- Site loads without errors
- Console shows no critical errors
```

---

## Phase 1: Fresh User Discovery

**CRITICAL**: Experience the app as a COMPLETE NEWCOMER. Pretend you know NOTHING about Quoted.

### Agent 1A: First Impressions Audit (Desktop)

**Persona**: First-time visitor, contractor looking for quoting software

```markdown
TASK: Experience Quoted.it.com as a complete newcomer (desktop)

APPROACH:
1. Navigate to https://quoted.it.com with NO prior knowledge
2. Document your first impressions within 5 seconds
3. Answer: What does this product do? (without scrolling)
4. Scroll through entire landing page, noting confusion points
5. Click "Try Demo" - experience demo as newcomer
6. Generate a test quote in demo mode
7. Note EVERY moment of confusion or friction

DISCOVERY QUESTIONS:
- Can I tell what this does in 5 seconds?
- Is the value proposition clear?
- What would make me want to sign up?
- What questions do I have that aren't answered?
- Where would I click to learn more?
- Does the demo explain itself?

OUTPUT FORMAT:
| Time | What I Did | What I Expected | What Happened | Confusion (1-5) |
|------|-----------|-----------------|---------------|-----------------|
```

### Agent 1B: First Impressions Audit (Mobile)

**Persona**: Contractor on phone at job site, heard about app from friend

```markdown
TASK: Experience Quoted on mobile as complete newcomer (375px)

APPROACH:
1. Resize to 375x667 (iPhone SE)
2. Navigate to https://quoted.it.com
3. Document first 5-second impression
4. Can you figure out what this does on small screen?
5. Try the demo from mobile
6. Experience voice input if possible
7. Note thumb-reachability of all CTAs

DISCOVERY QUESTIONS:
- Can I use this while holding my phone with one hand?
- Is the demo usable on mobile?
- Would I want to sign up from my phone?
- Can I see enough to make a decision?

OUTPUT FORMAT:
| Action | Thumb Zone (Y/N) | Readable | Works as Expected | Notes |
|--------|-----------------|----------|-------------------|-------|
```

---

## Phase 2: Landing & Marketing Audit

### Agent 2A: Desktop Landing Audit

**Target**: https://quoted.it.com at 1440px

```markdown
TASK: Deep UX audit of landing page on desktop

AUDIT CHECKLIST:
[ ] Hero section - clarity of value prop in <3 seconds
[ ] Primary CTA - visibility, contrast, action clarity
[ ] Trust signals - testimonials, social proof placement
[ ] Feature sections - scannable, benefit-focused
[ ] FAQ - accessibility, searchability
[ ] Footer - navigation completeness
[ ] Page speed - time to interactive
[ ] Visual hierarchy - eye flow, spacing
[ ] Typography - readability, contrast
[ ] Animation - purposeful or distracting?

TESTING PROCEDURE:
1. Navigate to landing page
2. Take full-page screenshot
3. Read accessibility tree (browser_snapshot)
4. Check console for errors
5. Test all clickable elements
6. Measure scroll depth engagement points

OUTPUT FORMAT:
| Element | Current State | Issue (if any) | Proposed Improvement | Impact (HIGH/MED/LOW) |
|---------|---------------|----------------|---------------------|----------------------|
```

### Agent 2B: Mobile Landing Audit

**Target**: https://quoted.it.com at 375px (iPhone SE)

```markdown
TASK: Deep UX audit of landing page on mobile

AUDIT CHECKLIST:
[ ] Above-the-fold content - compelling without scroll
[ ] Touch targets - minimum 44x44px
[ ] Mobile menu - accessible, intuitive
[ ] CTA visibility - thumb-reachable
[ ] Text sizing - readable without zoom
[ ] Image optimization - not too large
[ ] Form factor - no horizontal scroll
[ ] Loading - fast on 3G?
[ ] Bottom nav - if exists, reachable

TESTING PROCEDURE:
1. resize_window to 375x667
2. Navigate to landing page
3. Screenshot viewport
4. Test thumb-zone accessibility
5. Test mobile menu
6. Scroll test - content ordering

OUTPUT FORMAT:
| Element | Current State | Issue (if any) | Proposed Improvement | Impact (HIGH/MED/LOW) |
```

---

## Phase 3: Authentication & Onboarding Audit

### Agent 3A: Auth Flow Audit

**Target**: Auth modal, signup, login

```markdown
TASK: Deep UX audit of authentication flows

AUDIT CHECKLIST:
[ ] Modal trigger - clear, prominent
[ ] Email input - validation feedback
[ ] Magic link explanation - clear what happens next
[ ] Error states - helpful, not scary
[ ] Loading states - progress indication
[ ] Terms/Privacy - visible, accessible
[ ] Tab switching (login/signup) - intuitive
[ ] Mobile modal - full-screen or adapted?
[ ] Password-less trust - does user understand?

TESTING PROCEDURE:
1. Click "Start Free Trial" or "Sign Up"
2. Screenshot auth modal
3. Test invalid email handling
4. Test empty submission
5. Verify Terms/Privacy links work
6. Test modal close behavior
7. Test login tab switch

OUTPUT FORMAT:
| Flow Step | Current UX | Issue (if any) | Proposed Improvement | Impact |
```

### Agent 3B: Onboarding Flow Audit

**Target**: Post-signup onboarding experience

```markdown
TASK: Deep UX audit of new user onboarding

NOTE: This requires authenticated state. If no test account available,
document what SHOULD be tested and recommend manual verification.

AUDIT CHECKLIST:
[ ] First-load experience - immediate value or setup?
[ ] Industry selection - comprehensive, intuitive
[ ] Pricing interview - conversational, helpful
[ ] Quick setup option - clearly positioned
[ ] Progress indicators - where am I?
[ ] Skip options - graceful escape hatches
[ ] First quote prompt - guided or abandoned?
[ ] Tour trigger - contextual, not intrusive
[ ] Time to first value - how long?

TESTING PROCEDURE:
1. Simulate new user login (if possible)
2. Document each onboarding step
3. Time the full flow
4. Note friction points
5. Test skip/back navigation

OUTPUT FORMAT:
| Step # | Step Name | Time (sec) | Friction Level (1-5) | Issue | Improvement |
```

### Agent 3C: Interactive Tour System Audit (Shepherd.js)

**Target**: Product tour experience (RECENTLY DEPLOYED - Dec 26, 2025)

```markdown
TASK: Deep UX audit of interactive product tour

TECHNICAL CONTEXT:
- Uses Shepherd.js v11.2.0 via CDN
- Tour triggers for new/returning users who haven't completed it
- Should guide through core features: voice recording, quotes, customers

AUDIT CHECKLIST:
[ ] Tour trigger - does it activate for new users?
[ ] Step progression - smooth, no stuck states
[ ] Highlight accuracy - does it point to right elements?
[ ] Step content - clear, helpful, not overwhelming
[ ] Skip/close - obvious escape hatch
[ ] Resume capability - remembers progress?
[ ] Mobile tour - adapted for touch/small screens
[ ] CSS styling - matches app aesthetic (.shepherd-button, .shepherd-content)
[ ] Menu integration - "Start Tour" option visible
[ ] Completion tracking - prevents re-triggering

TESTING PROCEDURE:
1. Clear tour completion state (localStorage/API)
2. Trigger tour as new user
3. Walk through ALL tour steps
4. Test skip at various points
5. Test mobile viewport tour
6. Verify tour doesn't re-trigger after completion
7. Test "Start Tour" from menu (if available)

KNOWN ISSUES TO VERIFY:
- BUG-002 was CSS class mismatch (.show vs .active) - VERIFY FIXED
- CDN source matters (cdnjs > jsdelivr) - check which is used

OUTPUT FORMAT:
| Tour Step | Element Targeted | Content Quality (1-5) | Works (Y/N) | Mobile Works (Y/N) | Issue |
```

---

## Phase 4: Core Quote Flow Audit

### Agent 4A: Voice Recording Audit

**Target**: Voice input UX

```markdown
TASK: Deep UX audit of voice recording experience

AUDIT CHECKLIST:
[ ] Microphone button - visibility, affordance
[ ] Permission prompt - clear explanation
[ ] Recording state - obvious visual feedback
[ ] Recording time - visible countdown/timer?
[ ] Stop mechanism - clear, accessible
[ ] Audio playback - can user review?
[ ] Re-record option - easy access
[ ] Fallback to text - smooth transition
[ ] Mobile recording - thumb-friendly
[ ] Error states - permission denied, no audio

TESTING PROCEDURE:
1. Navigate to quote creation
2. Click voice input
3. Test recording indicators
4. Test stop/restart
5. Test text fallback
6. Mobile viewport test

OUTPUT FORMAT:
| Interaction | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 4B: Quote Generation Audit

**Target**: AI quote generation experience

```markdown
TASK: Deep UX audit of quote generation

AUDIT CHECKLIST:
[ ] Generation trigger - clear action
[ ] Loading state - engaging, not anxious
[ ] Progress feedback - what's happening?
[ ] Time expectation - set correctly?
[ ] Transcription display - readable, editable
[ ] Edit & Regenerate - discoverable
[ ] Error handling - recoverable
[ ] Confidence display - trustworthy?
[ ] Line item clarity - understandable
[ ] Total calculation - transparent

TESTING PROCEDURE:
1. Submit voice/text input
2. Time generation
3. Observe loading states
4. Review quote display
5. Test edit flow
6. Test regenerate flow

OUTPUT FORMAT:
| Generation Phase | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 4C: Quote Editing Audit

**Target**: Post-generation quote editing

```markdown
TASK: Deep UX audit of quote editing

AUDIT CHECKLIST:
[ ] Edit triggers - obvious, accessible
[ ] Inline editing - smooth, responsive
[ ] Customer info edit - easy access
[ ] Line item edit - clear affordances
[ ] Add/remove items - intuitive
[ ] Price overrides - transparent
[ ] Undo/redo - available?
[ ] Save behavior - auto or manual?
[ ] Validation - helpful errors
[ ] Mobile editing - touch-friendly

TESTING PROCEDURE:
1. Open existing quote for edit
2. Test customer info changes
3. Test line item edits
4. Test add/remove items
5. Test price overrides
6. Mobile viewport test

OUTPUT FORMAT:
| Edit Action | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 5: Dashboard & Quote Management Audit

### Agent 5A: Dashboard Overview Audit

**Target**: Main dashboard view

```markdown
TASK: Deep UX audit of dashboard

AUDIT CHECKLIST:
[ ] First impression - clear purpose
[ ] Navigation - intuitive menu structure
[ ] Quote cards - scannable, actionable
[ ] Status indicators - clear meaning
[ ] View counts - visible, meaningful
[ ] Quick actions - accessible, obvious
[ ] Empty states - helpful, motivating
[ ] Loading states - smooth
[ ] Filters - useful, discoverable
[ ] Search - fast, accurate
[ ] Pagination/scroll - smooth

TESTING PROCEDURE:
1. Load dashboard with quotes
2. Test all navigation items
3. Test quote card interactions
4. Test filter/search
5. Test empty state (if accessible)
6. Mobile dashboard test

OUTPUT FORMAT:
| Dashboard Element | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 5B: Quote Actions Audit

**Target**: Quote card actions (share, download, duplicate, etc.)

```markdown
TASK: Deep UX audit of quote actions

AUDIT CHECKLIST:
[ ] Share action - modal, link generation
[ ] Download PDF - progress, naming
[ ] Duplicate - feedback, navigation
[ ] Delete - confirmation, undo
[ ] Accept/Reject flow - clear status
[ ] Convert to Invoice - discovery
[ ] Quick prefill - visibility
[ ] Outcome tracking - intuitive
[ ] Bulk actions - if available

TESTING PROCEDURE:
1. Test each quote action
2. Verify modal behaviors
3. Test confirmation dialogs
4. Check download behavior
5. Test on mobile

OUTPUT FORMAT:
| Action | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 6: CRM & Customers Audit

### Agent 6A: Customer Management Audit

**Target**: Customer list, create, edit

```markdown
TASK: Deep UX audit of CRM system

AUDIT CHECKLIST:
[ ] Customer list - scannable, sortable
[ ] Search customers - fast, accurate
[ ] Create customer - minimal friction
[ ] Edit customer - easy access
[ ] Customer tags - useful, manageable
[ ] Notes - visible, editable
[ ] Contact info - complete, formatted
[ ] Empty state - motivating

TESTING PROCEDURE:
1. Navigate to customers
2. Test search/filter
3. Test create customer flow
4. Test edit customer
5. Test tag management
6. Mobile customer list

OUTPUT FORMAT:
| CRM Feature | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 6B: Customer History Audit

**Target**: Customer quote history, relationship view

```markdown
TASK: Deep UX audit of customer relationships

AUDIT CHECKLIST:
[ ] Quote history - visible, comprehensive
[ ] Invoice history - linked to quotes
[ ] Total lifetime value - calculated?
[ ] Recent activity - surfaced
[ ] Quick actions from customer - create quote, task
[ ] Customer profile - complete view

TESTING PROCEDURE:
1. Open customer detail
2. Review quote history display
3. Test quick actions
4. Verify data consistency

OUTPUT FORMAT:
| Relationship View | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 7: Tasks System Audit

### Agent 7A: Tasks Full Audit

**Target**: Task creation, management, automation

```markdown
TASK: Deep UX audit of tasks system

AUDIT CHECKLIST:
[ ] Task list - clear, prioritized
[ ] Create task - minimal steps
[ ] Task types - meaningful, useful
[ ] Due dates - calendar picker UX
[ ] Priority levels - visual distinction
[ ] Customer linking - easy association
[ ] Task completion - satisfying toggle
[ ] Overdue handling - visible, actionable
[ ] Auto-reminders - clear schedule
[ ] Automated tasks - understood?
[ ] Empty state - guidance
[ ] Mobile tasks - touch-friendly

TESTING PROCEDURE:
1. Navigate to tasks
2. Create a new task
3. Test all task fields
4. Complete a task
5. Test filter/sort
6. Mobile viewport test

OUTPUT FORMAT:
| Task Feature | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 8: Invoicing System Audit

### Agent 8A: Invoice Creation Audit

**Target**: Quote-to-invoice conversion

```markdown
TASK: Deep UX audit of invoice creation

AUDIT CHECKLIST:
[ ] Convert trigger - discoverable
[ ] Conversion flow - minimal steps
[ ] Invoice numbering - automatic, editable
[ ] Invoice details - pre-filled correctly
[ ] Payment terms - configurable
[ ] Deposit handling - clear
[ ] Invoice preview - accurate
[ ] Success feedback - clear next steps

TESTING PROCEDURE:
1. Find accepted quote
2. Convert to invoice
3. Review invoice details
4. Test invoice editing
5. Verify PDF generation

OUTPUT FORMAT:
| Invoice Creation | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 8B: Invoice Management Audit

**Target**: Invoice list, sharing, payment tracking

```markdown
TASK: Deep UX audit of invoice management

AUDIT CHECKLIST:
[ ] Invoice list - status clarity
[ ] Invoice sharing - link generation
[ ] Public invoice view - customer-friendly
[ ] Mark as paid - easy access
[ ] Payment method capture - simple
[ ] Invoice PDF - professional
[ ] Overdue tracking - visible
[ ] Invoice email - deliverable

TESTING PROCEDURE:
1. Review invoice list
2. Test share flow
3. View public invoice page
4. Test mark as paid
5. Download invoice PDF

OUTPUT FORMAT:
| Invoice Feature | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 9: Learning System Deep Dive

**CRITICAL**: This is Quoted's competitive moat. Deep analysis required.

### Agent 9A: Learning Architecture Audit

**Target**: Backend learning services (learning.py, learning_quality.py, learning_relevance.py)

```markdown
TASK: Deep audit of learning system architecture

ANALYZE:
1. Read backend/services/learning.py - core correction processing
2. Read backend/services/learning_quality.py - quality scoring (4 dimensions)
3. Read backend/services/learning_relevance.py - smart selection (replaces "last 7")
4. Read backend/api/learning.py - API endpoints

CURRENT ARCHITECTURE:
- THREE-LAYER learning: Injection statements, Tailored prompts, Global philosophy
- QUALITY SCORING: Specificity (25%), Actionability (35%), Clarity (25%), Anti-patterns (-15%)
- RELEVANCE SELECTION: Keyword (40%), Recency (30%), Specificity (20%), Foundational (10%)
- QUALITY TIERS: Reject (<40), Review (40-60), Refine (60-70), Accept (>70)

AUDIT QUESTIONS:
- Is quality scoring actually being used in production?
- Is relevance selection being used (or still using "last 7")?
- How are learnings stored? (metadata vs plain strings)
- Are outcome boosts being applied?
- Is cross-category learning implemented?
- What happens to "review" tier learnings?

OUTPUT FORMAT:
| Component | Design Intent | Current Reality | Gap | Improvement |
|-----------|---------------|-----------------|-----|-------------|
```

### Agent 9B: Learning UX Audit

**Target**: User-facing learning experience

```markdown
TASK: Audit how users experience the learning system

AUDIT CHECKLIST:
[ ] Pricing Brain UI - shows learning progress?
[ ] Category management - clear what's learned?
[ ] Correction feedback - user knows impact?
[ ] Confidence badges - trustworthy, helpful?
[ ] Learning explanations - transparent?
[ ] New category detection - clear notification?
[ ] Outcome tracking - user understands?

TESTING PROCEDURE:
1. Navigate to Pricing Brain
2. View existing categories
3. Check what learning data is visible
4. Make a quote edit - verify feedback
5. Check confidence badge display
6. Test outcome tracking UI

INNOVATION QUESTIONS:
- How could users SEE their pricing brain growing smarter?
- Could we show "before/after" accuracy improvements?
- What if users could "teach" the AI explicitly?
- How do we make the learning FEEL magical?

OUTPUT FORMAT:
| Learning Feature | Current UX | User Understanding | Proposed Enhancement |
|-----------------|------------|-------------------|---------------------|
```

### Agent 9C: Learning Improvement Proposals

**Target**: Generate innovative improvements for the learning system

```markdown
TASK: Propose 10x improvements to the learning system

ANTHROPIC SHOWCASE PRINCIPLES:
1. Human-AI collaboration (enhance, never replace)
2. Interpretable AI (explainable pricing)
3. Honest uncertainty (confidence scores)
4. Aligned incentives (optimizes for contractor success)
5. Privacy-preserving intelligence (network effects without exposure)

IMPROVEMENT CATEGORIES:

1. TRANSPARENCY
   - Show users why a price was suggested
   - Display learning statement that influenced quote
   - "Based on your feedback on 3 similar jobs..."

2. ACTIVE LEARNING
   - Let users explicitly teach: "For kitchen faucets, I always..."
   - Capture edge cases proactively
   - Smart questions when confidence is low

3. OUTCOME INTELLIGENCE
   - Learn from won vs lost quotes
   - Adjust for market conditions
   - "Quotes 10% lower tend to win in your area"

4. NETWORK EFFECTS (Privacy-Preserving)
   - Anonymous aggregated insights
   - "Other deck contractors typically..."
   - Industry benchmarks

5. VISUALIZATION
   - Learning progress dashboard
   - Accuracy improvement over time
   - Category mastery levels

OUTPUT FORMAT:
| Innovation | Category | Effort (S/M/L/XL) | Impact | Moat Potential |
|------------|----------|-------------------|--------|----------------|
```

---

## Phase 10: Settings & Billing Audit

### Agent 10A: Account Settings Audit

**Target**: Profile, preferences, defaults

```markdown
TASK: Deep UX audit of account settings

AUDIT CHECKLIST:
[ ] Settings navigation - intuitive
[ ] Profile info - easy edit
[ ] Logo upload - clear process
[ ] Default terms - configurable
[ ] Default timeline - configurable
[ ] PDF templates - preview, selection
[ ] Accent colors - visual picker
[ ] Save behavior - clear feedback
[ ] Mobile settings - accessible

TESTING PROCEDURE:
1. Navigate to settings
2. Test each settings section
3. Test logo upload flow
4. Test template selection
5. Mobile settings test

OUTPUT FORMAT:
| Settings Feature | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 10B: Billing & Subscription Audit

**Target**: Plan management, billing

```markdown
TASK: Deep UX audit of billing

AUDIT CHECKLIST:
[ ] Current plan display - clear
[ ] Plan comparison - easy understand
[ ] Upgrade flow - smooth
[ ] Payment method - Stripe integration
[ ] Billing history - accessible
[ ] Trial status - prominent
[ ] Cancel flow - not hostile
[ ] Annual vs monthly - clear savings

TESTING PROCEDURE:
1. Navigate to billing
2. Review plan display
3. Test plan selection
4. Verify Stripe integration
5. Check trial display

OUTPUT FORMAT:
| Billing Feature | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 11: Referral & Sharing Audit

### Agent 11A: Quote Sharing Audit

**Target**: Share modal, public quote view

```markdown
TASK: Deep UX audit of quote sharing

AUDIT CHECKLIST:
[ ] Share button - visibility
[ ] Share modal - clear options
[ ] Link generation - instant
[ ] Copy link - obvious, confirmed
[ ] Email share - pre-filled, editable
[ ] Public quote view - professional
[ ] Accept/reject buttons - clear
[ ] E-signature flow - trustworthy
[ ] Expiration warning - visible
[ ] Mobile sharing - easy

TESTING PROCEDURE:
1. Open share modal
2. Test link copy
3. Visit public quote URL
4. Test accept flow (if safe)
5. Test reject flow (if safe)
6. Mobile public view test

OUTPUT FORMAT:
| Sharing Feature | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 11B: Referral Program Audit

**Target**: Referral code, sharing, rewards

```markdown
TASK: Deep UX audit of referral program

AUDIT CHECKLIST:
[ ] Referral code - visible, copyable
[ ] Share options - social, email, link
[ ] Referral tracking - transparent
[ ] Reward explanation - clear
[ ] Referral landing - compelling
[ ] Onboarding attribution - captured

TESTING PROCEDURE:
1. Find referral code
2. Test copy mechanisms
3. Visit referral link
4. Verify attribution capture

OUTPUT FORMAT:
| Referral Feature | Current UX | Issue | Proposed Improvement | Impact |
```

---

## Phase 12: Mobile Deep Dive

### Agent 12A: Mobile Navigation Audit

**Target**: All navigation at 375px

```markdown
TASK: Deep mobile navigation audit

AUDIT CHECKLIST:
[ ] Bottom nav - thumb zone
[ ] Menu items - tap targets
[ ] Back navigation - consistent
[ ] Modals - full screen adapted
[ ] Swipe gestures - if applicable
[ ] Orientation - portrait optimized
[ ] Keyboard avoidance - forms scroll

TESTING PROCEDURE:
1. Resize to 375x667
2. Navigate full app
3. Test all touch targets
4. Test form interactions
5. Test modal behaviors

OUTPUT FORMAT:
| Mobile Nav | Current UX | Issue | Proposed Improvement | Impact |
```

### Agent 12B: Mobile Edge Cases Audit

**Target**: Edge cases, error states, offline

```markdown
TASK: Mobile edge case audit

AUDIT CHECKLIST:
[ ] Offline behavior - graceful degradation
[ ] Slow network - loading states
[ ] Large content - scrollable
[ ] Long text - truncation handling
[ ] Error recovery - clear actions
[ ] Keyboard - no content obscured
[ ] Orientation change - handled
[ ] Safe areas - notch/home bar

TESTING PROCEDURE:
1. Test with slow network simulation
2. Test long content scenarios
3. Test keyboard interactions
4. Test orientation changes

OUTPUT FORMAT:
| Edge Case | Current Behavior | Issue | Proposed Improvement | Impact |
```

---

## Phase 13: Integration Audit

### Agent 13A: Cross-Feature Flow Audit

**Target**: Multi-feature user journeys

```markdown
TASK: Cross-feature integration audit

TEST JOURNEYS:
1. Voice quote → Share → Accept → Invoice → Paid
2. New customer → Quote → Task → Follow-up
3. Dashboard → Duplicate quote → Edit → Share
4. Onboarding → First quote → Celebration → Referral
5. Mobile: Full quote creation to share

AUDIT CHECKLIST:
[ ] Data consistency - across features
[ ] Navigation flow - logical progression
[ ] State preservation - no data loss
[ ] Error recovery - graceful fallbacks
[ ] Context awareness - where am I?

TESTING PROCEDURE:
1. Execute each journey end-to-end
2. Note friction points
3. Verify data consistency
4. Time each journey

OUTPUT FORMAT:
| Journey | Steps | Time | Friction Points | Improvement Opportunities |
```

---

## Phase 14: Innovation Synthesis

### Agent 14A: Innovation Auditor

```markdown
TASK: Synthesize all findings into innovation opportunities

CATEGORIES:
1. **Quick Wins** - Low effort, high impact
2. **Strategic Investments** - High effort, high impact
3. **UX Delights** - Small touches that impress
4. **Growth Levers** - Conversion/retention improvements
5. **Competitive Moats** - Hard-to-copy advantages

SYNTHESIS PROCESS:
1. Review all phase outputs
2. Identify patterns across issues
3. Cluster related improvements
4. Prioritize by impact/effort
5. Generate innovative solutions

OUTPUT FORMAT:
| Innovation | Category | Effort | Impact | Competitive Advantage |
```

---

## Phase 15: Report & Tickets

### Agent 15A: Report Generator

```markdown
TASK: Generate final audit report and create tickets

REPORT STRUCTURE:
1. Executive Summary
2. Critical Issues (must fix)
3. High Priority Improvements
4. Innovation Opportunities
5. Mobile-Specific Findings
6. Recommended Roadmap

TICKET CREATION:
- Create GitHub issues for CRITICAL items
- Create DISC-XXX entries for improvements
- Prioritize for next sprint

DELIVERABLES:
1. FINAL_UX_AUDIT_REPORT.md
2. Created GitHub issues
3. Updated DISCOVERY_BACKLOG.md
```

---

## Rollback Procedures

This audit is READ-ONLY. No rollback needed.

If tickets are created incorrectly:
```bash
gh issue close <number> --comment "Created in error"
```

---

## Resume Procedures

If context resets, read `.claude/ux-excellence-state.md` for:
1. Current phase
2. Completed agents
3. Accumulated findings
4. Next steps

State file is updated after each agent completes.

---

## Success Metrics

**Audit Complete When**:
- [ ] All 16 phases (0-15) completed
- [ ] All issues documented with severity
- [ ] All improvements have effort/impact rated
- [ ] Final report generated
- [ ] Tickets created for critical issues
- [ ] State file shows Phase 15 complete

**Quality Bar**:
- Every feature tested on desktop AND mobile
- Every issue has proposed solution
- Every improvement has ROI estimate
- Innovations are genuinely creative (not obvious)
