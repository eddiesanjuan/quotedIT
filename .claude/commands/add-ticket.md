# Add Ticket to Discovery Backlog

Add a new ticket to the Quoted discovery backlog. Auto-approved (READY status) since founder is requesting it directly.

**Arguments**: $ARGUMENTS (ticket description - can be brief or detailed)

---

## CRITICAL INSTRUCTIONS

**DO NOT** start working on the ticket after adding it. Your job is ONLY to:
1. Capture the ticket in proper format
2. Add it to the backlog as READY
3. Confirm it was added
4. STOP

If the user wants implementation, they will explicitly ask or approve it in a subsequent message.

---

## Process

### Step 1: Parse the Request

Analyze the description provided: `$ARGUMENTS`

If the description is empty or unclear, ask ONE clarifying question. Otherwise, proceed.

### Step 2: Determine Next Ticket Number

Read `DISCOVERY_BACKLOG.md` and find the highest DISC-XXX number. The new ticket will be DISC-{highest + 1}.

### Step 3: Classify the Ticket

Determine the category based on content:
- **Product**: UX improvements, feature gaps, user experience
- **Growth**: Acquisition, activation, retention, viral loops
- **Strategy**: Competitive positioning, market, long-term
- **Infrastructure**: Technical debt, architecture, performance

### Step 4: Estimate Impact/Effort

Based on scope, assign:
- **Impact**: LOW (nice-to-have) | MEDIUM (meaningful improvement) | HIGH (critical path)
- **Effort**: S (hours) | M (1-2 days) | L (3-5 days) | XL (1+ weeks)

If uncertain, default to MEDIUM impact, M effort.

### Step 5: Create the Ticket

Use this format:

```markdown
### DISC-XXX: [Title] (READY)

**Source**: Founder Request (Eddie, YYYY-MM-DD)
**Impact**: [HIGH|MEDIUM|LOW] | **Effort**: [S|M|L|XL] | **Score**: [Impact/Effort ratio]
**Sprint Alignment**: [How this fits current goals, or "Queued for next cycle"]

**Problem**: [1-2 sentences on what problem this solves]

**Proposed Work**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Success Metric**: [How we know it worked - can be TBD if unclear]

---
```

### Step 6: Add to Backlog

Insert the ticket in the "Ready for Implementation" section of `DISCOVERY_BACKLOG.md`, after existing READY tickets.

Update the summary counts:
- Increment READY count by 1
- Increment Total count by 1

### Step 7: Confirm (Then STOP)

Output a brief confirmation:

```
Added DISC-XXX: [Title] to backlog (READY)
Impact: [X] | Effort: [X] | Score: [X]

Ready for next autonomous cycle to pick up.
```

**DO NOT** proceed to implementation. Your work is done.

---

## Examples

**Input**: `/add-ticket voice command to duplicate a quote`

**Output**:
```
Added DISC-050: Voice Command for Quote Duplication to backlog (READY)
Impact: MEDIUM | Effort: M | Score: 1.0

Ready for next autonomous cycle to pick up.
```

**Input**: `/add-ticket the PDF footer looks cramped on mobile, needs more padding`

**Output**:
```
Added DISC-051: PDF Footer Mobile Spacing to backlog (READY)
Impact: LOW | Effort: S | Score: 1.0

Ready for next autonomous cycle to pick up.
```

---

## Edge Cases

- **Multiple tickets in one request**: Create separate tickets for each distinct item
- **Vague description**: Ask ONE clarifying question before proceeding
- **Already exists**: Check if similar ticket exists; if so, note it and ask if user wants duplicate or update
- **Phase II related**: Add to Phase II section if it's clearly voice-control related
