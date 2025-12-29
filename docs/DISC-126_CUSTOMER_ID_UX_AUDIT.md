# DISC-126: Customer Identification UX Deep Audit

**Status**: COMPLETE
**Date**: 2025-12-28
**Type**: Audit/Research
**Author**: AI Audit System

---

## Executive Summary

The current customer identification flow in Quoted has significant UX friction. Customer matching happens **after** quote generation, missing opportunities to:
1. Confirm customer identity during voice input
2. Apply repeat customer pricing automatically
3. Pre-fill customer details from history

The system is technically capable but the UX doesn't expose these capabilities at the right moment.

---

## Current State Analysis

### Voice-to-Quote Flow

```
Voice Input → Transcription → Claude AI Extraction → Quote Generation → Customer Linking (POST-HOC)
                                    ↓
                        Extracts: customer_name
                                  customer_address
                                  customer_phone
```

**Key Finding**: Customer linking occurs in `link_quote_to_customer()` AFTER the quote is already generated. This means:
- No real-time customer suggestions during voice input
- No confirmation "Is this John Smith from 123 Oak St?"
- Repeat customer pricing signals are detected but not actioned

### Customer Deduplication Strategy

**File**: `backend/services/customer_service.py:68-154`

```python
# Priority: Phone > Name
1. If phone provided: match on (contractor_id, normalized_phone)
2. If no phone match: match on (contractor_id, normalized_name)
3. If no match: create new customer
```

**Normalization**:
- `normalized_name`: Lowercase, no punctuation (e.g., "john smith")
- `normalized_phone`: Digits only, no country code (e.g., "5551234567")

**Weakness**: Exact match only. "John Smith" matches "john smith" but not "Johnny Smith" or "J. Smith".

### Voice Signal Extraction

**File**: `backend/services/voice_signal_extractor.py`

The system detects relationship signals:

| Signal | Pattern | Impact |
|--------|---------|--------|
| Repeat Customer | `repeat\s+customer` | -5% price |
| Referral | `referred\s+by|referral\s+from|friend\s+of` | -5% price |
| Neighbor | `neighbor|next\s+door` | -3% price |
| New Client | `new\s+client|first\s+time|new\s+customer` | Neutral |

**Problem**: These signals affect pricing calculations but don't trigger customer lookup. The voice signal extraction runs in parallel with quote generation, not before it.

### Existing Autocomplete (DISC-022)

**Location**: Edit Customer Modal only

Customer autocomplete exists but is only available when editing a quote post-generation:

```javascript
// frontend/index.html:16370-16440
async function fetchCustomerSuggestions(query) {
    const response = await fetch(`${API_BASE}/quotes/customers?q=${query}`)
    // ... renders in dropdown
}
```

**Backend**: `GET /api/quotes/customers?q={query}`
- Searches by name, email, phone
- Returns deduplicated customer list
- Works well for manual editing, unavailable during voice flow

---

## Friction Points Identified

### 1. No Pre-Quote Customer Confirmation

**Severity**: HIGH

When a user says "Quote for the Hendersons on Oak Street", the system:
- Extracts "Hendersons" as customer_name
- Extracts "Oak Street" as partial address
- Generates quote
- Links to customer record (may create duplicate)

**Better UX**: Before generating, show: "Is this the Hendersons at 456 Oak St (3 previous quotes)? [Yes] [New Customer]"

### 2. Phone as Underutilized Identifier

**Severity**: MEDIUM

Phone numbers are normalized and used for matching, but:
- Not prominently requested in voice prompts
- Voice extraction uses pattern `customer_phone` but many transcriptions omit it
- Phone matching is exact (digits only) - works well when present

**Data**: Phone is the most reliable deduplication key but least frequently captured.

### 3. Address Not Used for Matching

**Severity**: MEDIUM

Addresses are stored (`customer_address`) but never used for deduplication:
- No `normalized_address` field
- Address matching is complex (123 Oak St vs 123 Oak Street)
- Could serve as secondary confirmation signal

### 4. Repeat Customer Signal Not Triggering Lookup

**Severity**: HIGH

When voice input contains "repeat customer" or "she's a regular":
- VoiceSignalExtractor detects it (confidence 0.9)
- Applies -5% price adjustment
- Does NOT search for matching customer
- Does NOT surface "Which customer? [list of regulars]"

### 5. INNOV-8 (Auto-Quote) Not Integrated

**Severity**: MEDIUM

The codebase has INNOV-8 infrastructure for repeat customer auto-quoting:

```python
# backend/services/customer_service.py:719
async def get_auto_quote_suggestion(...)
    """INNOV-8: Get auto-quote suggestions for a repeat customer."""
```

This feature exists but is not exposed in the UI flow.

---

## Identifier Effectiveness Analysis

### Phone Number

| Aspect | Rating | Notes |
|--------|--------|-------|
| Uniqueness | **EXCELLENT** | Near-unique per person |
| Capture Rate | **LOW** | Rarely mentioned in voice |
| Matching Reliability | **HIGH** | Digits-only normalization works well |
| False Positives | **VERY LOW** | Almost never matches wrong person |

**Recommendation**: Prompt for phone when "repeat customer" signal detected.

### Customer Name

| Aspect | Rating | Notes |
|--------|--------|-------|
| Uniqueness | **MEDIUM** | Common names cause collisions |
| Capture Rate | **HIGH** | Almost always mentioned |
| Matching Reliability | **MEDIUM** | Exact match only, no fuzzy |
| False Positives | **MEDIUM** | "John Smith" may match wrong John Smith |

**Recommendation**: Use as primary search key but require confirmation.

### Address

| Aspect | Rating | Notes |
|--------|--------|-------|
| Uniqueness | **HIGH** | Unique per property |
| Capture Rate | **MEDIUM** | Often mentioned for job site |
| Matching Reliability | **LOW** | Format variations, no normalization |
| False Positives | **LOW** | Rare but possible (multi-unit) |

**Recommendation**: Add lightweight address normalization, use as secondary signal.

---

## Recommended UX Improvements

### Tier 1: Quick Wins (Low Effort, High Impact)

#### 1.1 Post-Extraction Customer Confirmation

After Claude extracts customer data but BEFORE generating quote:

```
"I found a customer 'Smith Family' at '123 Oak St' in your records.
Is this the same customer? [Yes, use their info] [No, new customer]"
```

**Implementation**: Add API endpoint that takes extracted customer_name and returns potential matches. Insert confirmation step in frontend between transcription and generation.

#### 1.2 "Repeat Customer" Signal → Customer Picker

When VoiceSignalExtractor detects "repeat customer" pattern:

```
"You mentioned this is a repeat customer. Who is it?
[Recent: Hendersons (2 quotes)] [Recent: Johnson (5 quotes)] [Search...]"
```

**Implementation**: Check voice signals before quote generation. If relationship signal detected, show customer picker instead of generating immediately.

### Tier 2: Medium Effort Improvements

#### 2.1 Phone Number Prompt on Ambiguous Match

When name matches multiple customers:

```
"Found 3 customers named 'Smith':
- Smith at 123 Oak (phone ending 1234)
- Smith at 456 Elm (phone ending 5678)
- Smith at 789 Pine (no phone)

Which one? Or say the phone number to confirm."
```

#### 2.2 Lightweight Address Normalization

Add `normalized_address` to Customer model:
- Remove common suffixes (St/Street, Ave/Avenue)
- Normalize numbers (123 vs one-twenty-three)
- Use as secondary matching signal (not primary)

#### 2.3 Expose INNOV-8 Auto-Quote

When repeat customer confirmed, show:

```
"Last quote for Hendersons was 'Fence repair' for $2,400.
[Copy that quote] [Start fresh] [Similar job, different scope]"
```

### Tier 3: Future Considerations

#### 3.1 Real-Time Voice Customer Matching

Stream transcription → partial customer name extraction → live suggestions

**Complexity**: High (requires streaming transcription, partial parsing)

#### 3.2 Fuzzy Name Matching

Implement Levenshtein distance or phonetic matching:
- "John Smith" matches "Jon Smith" (spelling variant)
- "Johnson" matches "Johnston" (similar sound)

**Complexity**: Medium (requires algorithm selection, threshold tuning)

#### 3.3 Customer Verification Flow

After quote sent, track if customer confirmed identity:
- Link clicked from correct email?
- Phone number verified via SMS?

Use verification data to improve future matching confidence.

---

## Implementation Priority Matrix

| Improvement | Effort | Impact | Priority |
|-------------|--------|--------|----------|
| Post-extraction confirmation | LOW | HIGH | **P1** |
| Repeat customer → picker | LOW | HIGH | **P1** |
| Phone prompt on ambiguous | MEDIUM | MEDIUM | P2 |
| Address normalization | MEDIUM | MEDIUM | P2 |
| INNOV-8 UI exposure | MEDIUM | HIGH | P2 |
| Real-time voice matching | HIGH | MEDIUM | P3 |
| Fuzzy name matching | MEDIUM | MEDIUM | P3 |

---

## Technical Notes

### Key Files for Implementation

| File | Purpose |
|------|---------|
| `backend/services/customer_service.py` | Customer matching logic |
| `backend/services/voice_signal_extractor.py` | Relationship signal detection |
| `backend/services/quote_generator.py` | Quote generation with Claude |
| `backend/api/quotes.py:generate_quote()` | Main generation endpoint |
| `frontend/index.html:sendAudioForProcessing()` | Voice processing entry point |

### Suggested New Endpoints

```python
# POST /api/customers/match
# Request: { "name": str, "phone": str?, "address": str? }
# Response: { "matches": [...], "confidence": float, "suggestion": str }

# GET /api/customers/recent?limit=5
# Response: Most recently quoted customers for quick picker
```

### Database Changes

```python
# Optional: Add to Customer model
class Customer(Base):
    normalized_address = Column(String(255), index=True)  # NEW
    match_confidence = Column(Float)  # NEW: last match confidence
```

---

## Conclusion

The customer identification system has good backend foundations but poor UX integration. The highest-impact improvements are:

1. **Confirmation before generation** - Simple yes/no when customer likely matches
2. **Repeat customer signal → picker** - Leverage existing signal detection

Both are achievable with minimal backend changes and frontend modifications to the voice processing flow.

---

## Appendix: Related Tickets

- **DISC-022**: Customer Memory (autocomplete in edit modal) - DEPLOYED
- **INNOV-8**: Repeat Customer Auto-Quote - Backend ready, no UI
- **DISC-091**: Link quote to customer record - DEPLOYED

## Appendix: Code References

- Customer normalization: `customer_service.py:36-66`
- Customer matching: `customer_service.py:68-154`
- Voice signals: `voice_signal_extractor.py:93-169`
- Quote generation tool schema: `quote_generator.py:95-130`
- Customer linking: `quotes.py:572`, `quotes.py:878`, `quotes.py:1169`
