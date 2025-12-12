# DISC-085: Voice/Chat-Operated Simple CRM - Design Document

**Created**: 2025-12-11
**Status**: Design Complete - Awaiting Implementation Tickets
**Source**: Founder Request (Eddie)

---

## Executive Summary

Quoted currently generates quotes with customer information (name, phone, address) that exists in isolation per-quote. This design proposes a simple, voice-operated CRM layer that aggregates customers from quotes and enables voice/chat interactions for customer management.

**Core Insight**: Contractors already have customer data in their quotes - we're not asking them to enter data manually. We're organizing what they already have and making it queryable.

---

## Design Principles

1. **Voice-first**: Matches Quoted's core UX - contractors in trucks, hands-free
2. **Auto-populated**: Customers created automatically from quotes - zero data entry
3. **Simple**: Not Salesforce. Basic: contact info, quote history, notes, status
4. **Conversational**: Natural language queries and updates, not forms and clicks
5. **Non-blocking**: CRM is additive - doesn't change core quoting flow

---

## Data Model

### New Table: `Customer`

```sql
CREATE TABLE customers (
    id VARCHAR PRIMARY KEY,
    contractor_id VARCHAR NOT NULL REFERENCES contractors(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Core Info (aggregated from quotes)
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,

    -- Computed fields (updated on quote changes)
    total_quoted FLOAT DEFAULT 0,      -- Sum of all quotes
    total_won FLOAT DEFAULT 0,         -- Sum of won quotes
    quote_count INTEGER DEFAULT 0,     -- Number of quotes
    first_quote_at TIMESTAMP,          -- First interaction
    last_quote_at TIMESTAMP,           -- Most recent interaction

    -- CRM-specific fields
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, lead, vip
    notes TEXT,                           -- Free-form notes
    tags JSON DEFAULT '[]',               -- User-defined tags

    -- Source tracking
    source VARCHAR(100),                  -- How they found us (optional)

    -- Deduplication
    normalized_name VARCHAR(255),         -- Lowercase, no punctuation
    normalized_phone VARCHAR(20),         -- Digits only

    UNIQUE(contractor_id, normalized_name, normalized_phone)
);
```

### Modifications to `Quote`

Add foreign key to link quotes to customers:

```sql
ALTER TABLE quotes ADD COLUMN customer_id VARCHAR REFERENCES customers(id);
```

### Customer Deduplication Strategy

When a quote is created/updated with customer info:

1. Normalize name: lowercase, strip punctuation, collapse whitespace
2. Normalize phone: digits only
3. Look for existing customer with same (contractor_id, normalized_name) OR (contractor_id, normalized_phone)
4. If match: link quote to existing customer, update customer fields if newer
5. If no match: create new customer

**Edge cases**:
- No name or phone → Don't create customer (insufficient data)
- Name only → Create customer, may merge later if phone added
- Phone only → Create customer with "Unknown" name
- Conflicting data → Prefer most recent quote's data

---

## Voice Command Interface

### Natural Language Processing

The CRM will reuse the existing Claude service for voice command parsing. Commands are routed to a new CRM intent handler.

### Supported Commands (MVP)

| Category | Example Commands | Intent |
|----------|------------------|--------|
| **Search** | "Show me John Smith" | `customer_search` |
|  | "Find customers in Austin" | `customer_search` |
|  | "Who did I quote last week?" | `customer_search` |
| **View** | "What's the history with Johnson Electric?" | `customer_detail` |
|  | "How much have I quoted the Hendersons?" | `customer_stats` |
| **Update** | "Add a note to Mike Wilson: Prefers morning appointments" | `add_note` |
|  | "Tag Sarah's Bakery as VIP" | `add_tag` |
|  | "Mark Smith Corp as inactive" | `update_status` |
| **Insights** | "Which customers haven't had a quote in 6 months?" | `dormant_customers` |
|  | "Show my top customers by revenue" | `top_customers` |
|  | "How many leads do I have?" | `customer_count` |

### Command Parsing Flow

```
Voice Input → Whisper Transcription
           → Claude Intent Detection
           → Route to Handler:
               - quote_generation (existing)
               - crm_command (NEW)
           → Execute CRM Operation
           → Generate Natural Language Response
```

### Response Format

Voice responses will be concise and natural:

- "Found 3 customers matching 'Smith'. John Smith with 5 quotes totaling $12,400. Sarah Smith with 2 quotes..."
- "Mike Wilson: 3 quotes, $8,200 total, last quoted October 15th. Notes: Prefers morning appointments."
- "Added note to Mike Wilson's profile."
- "You have 12 customers who haven't been quoted in 6 months."

---

## UI Components

### 1. Customers Tab (New Navigation)

Add "Customers" to main navigation alongside "New Quote", "My Quotes", "Invoices", "Account".

### 2. Customer List View

```
┌─────────────────────────────────────────────────────────────┐
│ Customers (42)                              [Search...] [+] │
├─────────────────────────────────────────────────────────────┤
│ Filter: [All ▼] [Active ▼] [Sort: Last Quoted ▼]           │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────┐│
│ │ John Smith                                    5 quotes   ││
│ │ 512-555-1234                             $12,400 total   ││
│ │ Last: Oct 15, 2025                          [VIP] [...]  ││
│ └──────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Henderson Electric                           3 quotes   ││
│ │ 512-555-5678                              $8,200 total   ││
│ │ Last: Nov 2, 2025                               [...]    ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 3. Customer Detail View

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Customers                                         │
├─────────────────────────────────────────────────────────────┤
│ John Smith                                          [Edit]  │
│ 512-555-1234 | john@example.com                            │
│ 123 Main St, Austin TX 78701                               │
├─────────────────────────────────────────────────────────────┤
│ Summary                                                      │
│ ┌──────────┬──────────┬──────────┬──────────┐              │
│ │ 5 Quotes │ $12,400  │ $8,500   │ Oct 2024 │              │
│ │          │ Quoted   │ Won      │ Customer │              │
│ │          │          │          │ Since    │              │
│ └──────────┴──────────┴──────────┴──────────┘              │
├─────────────────────────────────────────────────────────────┤
│ Notes                                          [Add Note]   │
│ • Prefers morning appointments (Dec 11, 2025)              │
│ • Has large backyard, potential for fence project          │
├─────────────────────────────────────────────────────────────┤
│ Quote History                                               │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Deck Refinishing              $2,400     Oct 15, 2025   ││
│ │ Status: Won                                    [View]    ││
│ └──────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Pergola Installation          $4,800     Sep 3, 2025    ││
│ │ Status: Won                                    [View]    ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 4. Voice/Chat Input (Reuse Existing)

The existing voice input can be extended:
- If input starts with CRM-related intent, route to CRM handler
- Otherwise, proceed with quote generation as normal

Alternatively, add a mode toggle:
```
[🎤 New Quote] [💬 Ask about customers]
```

---

## Implementation Phases

### Phase 1: Data Foundation (MVP)

**Tickets**:
1. Create `Customer` model and migration
2. Add `customer_id` to `Quote` model
3. Build customer aggregation service (extract from existing quotes)
4. Create customer deduplication logic
5. Add API endpoints: `GET /customers`, `GET /customers/{id}`, `PATCH /customers/{id}`
6. Backfill existing quotes to create customer records

**Deliverable**: Customers auto-created from quotes, viewable via API

### Phase 2: Basic UI

**Tickets**:
1. Add Customers navigation tab
2. Build customer list view with search/filter
3. Build customer detail view with quote history
4. Add inline note editing
5. Add tag management

**Deliverable**: Users can view and manage customers in UI

### Phase 3: Voice Commands

**Tickets**:
1. Add CRM intent detection to Claude service
2. Implement customer search voice command
3. Implement customer detail voice command
4. Implement add note voice command
5. Implement insights voice commands (dormant, top customers)
6. Add voice response generation

**Deliverable**: Full voice-operated CRM

### Phase 4: Enhancements (Future)

- Follow-up reminders
- Pipeline stages (Lead → Quoted → Won → Complete)
- Revenue forecasting
- Customer timeline view
- Bulk actions (tag multiple, export)

---

## Technical Considerations

### Performance

- Index on `customers(contractor_id, normalized_name)`
- Index on `customers(contractor_id, last_quote_at)` for recent customer queries
- Materialized stats (total_quoted, quote_count) updated on quote save, not computed on read

### Migration Strategy

1. Deploy Phase 1 with feature flag `crm_enabled = false`
2. Run backfill job to create customers from existing quotes
3. Enable for Eddie first (validate data quality)
4. Enable for all users

### Voice Command Routing

Modify `claude_service.py` to detect CRM intents:

```python
# In analyze_voice_input or similar
if detected_intent in CRM_INTENTS:
    return await handle_crm_command(intent, entities, contractor_id)
else:
    return await generate_quote(...)  # existing flow
```

CRM intents are distinguished by keywords: "customer", "who did I", "show me", "find", "add note to", etc.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Customer records created from quotes | 100% (auto-populated) |
| Voice command success rate | 90%+ correct intent detection |
| Customer lookup time | <2 seconds |
| User adoption (% using Customers tab) | Track via PostHog |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Customer deduplication errors | Manual merge capability; err toward not merging |
| Voice command misinterpretation | Confirm destructive actions; easy undo |
| Feature bloat | Strict MVP scope; defer complexity to Phase 4 |
| Performance at scale | Indexed queries; computed stats; pagination |

---

## Open Questions

1. **Quote creation flow**: Should we show customer autocomplete when entering customer name on quotes?
   - Pro: Reduces duplicate entries, fills address/phone automatically
   - Con: Adds complexity to quote flow
   - Recommendation: Phase 2 enhancement, not MVP

2. **Customer without quotes**: Can users manually create customers (leads)?
   - Recommendation: Yes, in Phase 2 UI. Voice command: "Add a new lead: Mike Johnson, 512-555-9999"

3. **Multiple contacts per customer**: Commercial customers may have multiple contacts.
   - Recommendation: Defer to Phase 4. MVP = one contact per customer.

---

## Appendix: Claude Prompt for CRM Commands

```
You are a CRM assistant for a contractor. Parse the user's voice command and extract:
1. Intent: customer_search, customer_detail, add_note, add_tag, update_status, insights
2. Entities: customer_name, note_text, tag_name, status, filter_criteria

Examples:
- "Show me John Smith" → {intent: customer_search, customer_name: "John Smith"}
- "Add a note to Mike: prefers morning" → {intent: add_note, customer_name: "Mike", note_text: "prefers morning"}
- "Who haven't I quoted in 3 months?" → {intent: insights, filter: dormant, period: "3 months"}

Return JSON with intent and entities.
```

---

## Next Steps

1. Review design with founder
2. Create implementation tickets as DISCOVERED
3. Prioritize Phase 1 for next sprint
4. Assign to `/quoted-run` for implementation
