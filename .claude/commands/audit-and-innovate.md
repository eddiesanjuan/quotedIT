# Quoted Audit & Innovation Command

**Purpose**: Comprehensive app audit followed by creative innovation sprint. Find every hole before users do, then wildly reimagine every feature.

**Usage**: `/audit-and-innovate [--phase=N] [--focus=area] [--status]`

---

## Command Protocol

When invoked, follow this exact protocol:

### Step 1: Load State

```bash
# Check for existing state
STATE_FILE=".claude/audit-innovation-state.md"
```

Read the state file if it exists. If `--status` flag, just report current phase and findings count, then stop.

### Step 2: Execute Current Phase

Progress through phases sequentially. Each phase uses parallel agents for thoroughness.

---

## Phase 1: Technical Hole-Poking (The Skeptic)

**Mindset**: "I'm a user who will find every edge case, a hacker who will probe every weakness, a reviewer who will judge every inconsistency."

### 1A: API Stress Test (Parallel Agents)

Launch 4 agents simultaneously:

**Agent 1: Auth & Security Prober**
```
Probe the authentication system for holes:
1. Read backend/api/auth.py and backend/services/auth.py
2. Test edge cases: expired tokens, malformed tokens, missing tokens
3. Check rate limiting on sensitive endpoints
4. Look for any endpoint that should require auth but doesn't
5. Check for information leakage in error messages
6. Verify JWT secret strength and token expiration

Output: List of vulnerabilities ranked by severity (CRITICAL/HIGH/MEDIUM/LOW)
```

**Agent 2: API Contract Auditor**
```
Audit every API endpoint for consistency and correctness:
1. Read all files in backend/api/
2. For each endpoint, verify:
   - Proper error handling (what happens on bad input?)
   - Consistent response format
   - Appropriate HTTP status codes
   - Input validation present
   - Documentation matches behavior
3. Look for endpoints that could fail silently
4. Check for N+1 query patterns
5. Verify pagination on list endpoints

Output: Table of endpoints with issues found
```

**Agent 3: Database & Data Integrity**
```
Audit data layer for integrity issues:
1. Read backend/models/database.py
2. Check for:
   - Missing foreign key constraints
   - Nullable fields that shouldn't be
   - Missing indexes on frequently queried columns
   - Orphan record possibilities
   - Race condition vulnerabilities in concurrent operations
3. Review backend/services/database.py for:
   - Unbounded queries (.all() without limits)
   - Missing transaction handling
   - Error recovery patterns

Output: List of data integrity risks
```

**Agent 4: Frontend Resilience**
```
Audit frontend for failure modes:
1. Read frontend/index.html thoroughly
2. Check for:
   - API calls without error handling
   - Loading states that could hang
   - Empty states that look broken
   - Mobile breakpoint issues (375px, 414px, 768px)
   - Accessibility issues (missing labels, contrast, keyboard nav)
   - XSS vulnerabilities in dynamic content
3. Trace each user flow for failure points

Output: List of frontend fragility points
```

### 1B: User Journey Hole-Poking (Serial)

Walk through each critical user journey looking for holes:

**Journey 1: Brand New User**
```
Simulate: Someone just heard about Quoted, lands on landing.html
- Is the value prop clear in 5 seconds?
- Can they try before signing up? (demo.html)
- What happens if they have questions? (help.html)
- Sign up flow: What could confuse them?
- Onboarding: What if they abandon mid-interview?
- First quote: What if transcription fails? What if they hate the result?

Document every moment of potential friction or confusion.
```

**Journey 2: Active User Creating Quote**
```
Simulate: Contractor opens app to quote a job
- App load time and responsiveness
- Voice recording: What if mic fails? What if it's too quiet?
- Processing time: Is feedback clear?
- Quote review: Can they understand what to edit?
- Quote save: What if network drops mid-save?
- Quote send: What if customer email bounces?

Document every failure mode.
```

**Journey 3: Customer Receiving Quote**
```
Simulate: Customer gets quote email, clicks link
- Email deliverability (spam folder risk?)
- Link click: Does it work on all devices?
- Quote view: Is it professional? Mobile-friendly?
- Accept/Reject: Is the flow obvious?
- What if link expires? What if they have questions?

Document the customer-facing experience gaps.
```

**Journey 4: Learning & Improvement**
```
Simulate: User corrects quotes over time
- Is it obvious their corrections matter?
- Can they see what the AI learned? (Pricing Brain)
- Is the confidence feedback meaningful?
- What if they want to undo a learning?
- Cross-category learning: Is it visible?

Document learning system UX gaps.
```

### Phase 1 Output

Create `.claude/audit-innovation-outputs/phase1-holes.md`:
```markdown
# Phase 1: Technical Audit Findings

## Critical (Fix Before Launch)
[List with file:line references]

## High (Fix Within 1 Week)
[List with file:line references]

## Medium (Fix Within 1 Month)
[List with file:line references]

## Low (Backlog)
[List with file:line references]

## User Journey Friction Points
[Detailed journey analysis]
```

---

## Phase 2: UX & Polish Audit (The Perfectionist)

**Mindset**: "Every pixel matters. Every word matters. Every millisecond matters."

### 2A: Visual & Interaction Polish (Parallel Agents)

**Agent 1: Mobile Experience**
```
Audit mobile experience ruthlessly:
1. Check every screen at 375px width
2. Look for:
   - Tap targets too small (<44px)
   - Text too small to read
   - Horizontal scroll issues
   - Bottom nav overlaps
   - Forms that are painful on mobile
   - Modals that don't fit

Output: Screenshot descriptions of every mobile issue
```

**Agent 2: Copy & Messaging**
```
Audit all user-facing copy:
1. Scan all HTML files and JS strings
2. Check for:
   - Inconsistent terminology
   - Jargon users won't understand
   - Error messages that don't help
   - Missing help text
   - Tone inconsistencies
   - Typos and grammar issues

Output: Copy improvement recommendations
```

**Agent 3: Loading & Feedback States**
```
Audit perceived performance:
1. Find every loading state
2. Check for:
   - Spinners without context
   - Operations without progress feedback
   - Success confirmations that disappear too fast
   - Error states that don't explain what to do
   - Skeleton loaders vs spinners consistency

Output: Loading/feedback state improvements
```

**Agent 4: Empty & Error States**
```
Audit edge case UI:
1. Find every empty state (no quotes, no customers, etc.)
2. Find every error state
3. Check for:
   - Empty states that just say "No data"
   - Error states without recovery actions
   - States that look broken vs intentionally empty
   - First-time user guidance

Output: Empty/error state redesign recommendations
```

### Phase 2 Output

Create `.claude/audit-innovation-outputs/phase2-polish.md`

---

## Phase 3: Creative Innovation Sprint (The Visionary)

**Mindset**: "What if we had unlimited resources and no constraints? What would make this 10x better?"

### 3A: Feature Moonshots (Parallel Creative Agents)

Launch 5 creative agents, each focused on reimagining a core area:

**Creative Agent 1: Voice Experience Revolution**
```
Reimagine the voice-to-quote experience:

Current: User records audio → transcription → AI generates quote

Wild ideas to explore:
- Real-time transcription with live preview
- Voice commands during quote review ("Make the demo higher")
- Conversational quote building ("What about the railing?" "Cable, about 40 feet")
- Voice templates ("Use my deck template")
- Multi-language support
- Ambient noise cancellation feedback
- Voice-to-voice: AI reads back the quote for approval

For each idea:
1. Describe the user experience
2. Technical feasibility (1-5 scale)
3. Impact potential (1-5 scale)
4. Implementation complexity (1-5 scale)

Output: Ranked list of voice experience innovations
```

**Creative Agent 2: Quote Presentation Revolution**
```
Reimagine how quotes look and feel:

Current: PDF with line items and terms

Wild ideas to explore:
- Interactive web quotes (customer can toggle options)
- Video quote walkthroughs (AI-generated explainer)
- 3D/AR visualization ("Here's what your deck will look like")
- Comparison quotes ("Good/Better/Best" options)
- Dynamic pricing ("Price drops if you book this week")
- Social proof ("43 deck projects completed")
- Financing integration ("$X/month with Affirm")
- Digital signatures built-in
- Quote chat (customer can ask questions inline)

For each idea: Experience, Feasibility, Impact, Complexity scores

Output: Ranked list of quote presentation innovations
```

**Creative Agent 3: Learning System Revolution**
```
Reimagine how the AI learns and shows its work:

Current: Corrections update learnings, shown in Pricing Brain

Wild ideas to explore:
- "Explain this price" button on every line item
- Learning suggestions ("I noticed you always increase demo by 20%...")
- Competitor price benchmarking
- Seasonal adjustment learning ("You charge more in summer")
- Customer-specific pricing memory
- "What would [successful contractor] charge?" benchmarks
- Pricing simulation ("If you raised labor rate 10%...")
- Learning export/import between contractors
- Industry learning pools (anonymized)

For each idea: Experience, Feasibility, Impact, Complexity scores

Output: Ranked list of learning system innovations
```

**Creative Agent 4: Automation & Workflow Revolution**
```
Reimagine automation possibilities:

Current: Voice → Quote → Manual send → Manual follow-up

Wild ideas to explore:
- Auto-send quotes after X minutes if not edited
- Smart follow-up sequences (email, text, call reminder)
- Calendar integration (auto-schedule site visits)
- Lead scoring ("This customer is 80% likely to accept")
- Batch quoting ("Quote all 5 leads from Yelp")
- Integration marketplace (QuickBooks, Jobber, etc.)
- Receipt/invoice scanning to build pricing model
- Photo-to-quote (snap a photo, get a quote)
- Customer portal (all their quotes, invoices, history)

For each idea: Experience, Feasibility, Impact, Complexity scores

Output: Ranked list of automation innovations
```

**Creative Agent 5: Business Intelligence Revolution**
```
Reimagine data and insights:

Current: Basic quote history and Pricing Brain

Wild ideas to explore:
- Win/loss analytics with reasons
- Revenue forecasting based on pipeline
- Profitability analysis by job type
- Customer lifetime value tracking
- Market rate comparisons
- "You're leaving money on the table" alerts
- Capacity planning ("You're 80% booked next month")
- Referral tracking and optimization
- Review/reputation integration

For each idea: Experience, Feasibility, Impact, Complexity scores

Output: Ranked list of intelligence innovations
```

### 3B: Synthesize Innovation Report

Combine all creative agent outputs into a prioritized innovation roadmap:

```markdown
# Innovation Report: Quoted 2.0 Vision

## Immediate Wins (High Impact, Low Complexity)
[Top 5 innovations we could ship in weeks]

## Next Quarter Bets (High Impact, Medium Complexity)
[Top 5 innovations for Q1 roadmap]

## Moonshots (Highest Impact, High Complexity)
[Top 5 game-changers that would take months]

## Creative Sparks (Interesting but Uncertain)
[Ideas worth exploring further]

## Each Innovation Includes:
- User story
- Technical approach
- Estimated effort
- Success metrics
- Dependencies
```

### Phase 3 Output

Create `.claude/audit-innovation-outputs/phase3-innovations.md`

---

## Phase 4: Final Report & Recommendations

Synthesize all findings into executive summary:

Create `.claude/audit-innovation-outputs/AUDIT_INNOVATION_REPORT.md`:

```markdown
# Quoted Audit & Innovation Report
Generated: [timestamp]

## Executive Summary
[2-3 paragraph overview of findings and opportunities]

## Part 1: Critical Fixes (Before More Users)
[Prioritized list from Phase 1, max 10 items]

## Part 2: Polish & UX Improvements
[Prioritized list from Phase 2, max 10 items]

## Part 3: Innovation Roadmap
[Prioritized list from Phase 3]

### Immediate (This Month)
### Next Quarter
### Future Vision

## Part 4: Recommended Next Steps
[Concrete actions to take]

## Appendix: Full Findings
[Links to detailed phase outputs]
```

---

## State Management

After each phase, update `.claude/audit-innovation-state.md`:

```markdown
# Audit & Innovation State

## Status
Phase: [1-4]
Started: [timestamp]
Last Updated: [timestamp]

## Phase Completion
- [ ] Phase 1: Technical Audit
- [ ] Phase 2: UX & Polish Audit
- [ ] Phase 3: Creative Innovation Sprint
- [ ] Phase 4: Final Report

## Key Findings Count
- Critical: X
- High: X
- Medium: X
- Innovation Ideas: X

## Notes
[Any context for continuation]
```

---

## Invocation Examples

```bash
# Start fresh audit
/audit-and-innovate

# Check status
/audit-and-innovate --status

# Resume from specific phase
/audit-and-innovate --phase=3

# Focus on specific area
/audit-and-innovate --focus=voice
/audit-and-innovate --focus=mobile
/audit-and-innovate --focus=learning
```

---

## Success Criteria

This audit is complete when:
1. Every API endpoint has been reviewed for edge cases
2. Every user journey has been walked for friction
3. Every feature has been reimagined for 10x improvement
4. A prioritized, actionable report exists
5. The founder has clear next steps

**Goal**: Leave no stone unturned. Find what users would find. Dream what users would love.
