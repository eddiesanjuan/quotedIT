# Demo Sample Prompts Redesign

**Date**: 2026-01-12
**Ticket**: DISC-162 v2
**Status**: Approved for implementation

## Problem

The original DISC-162 implementation created a parallel static experience:
- Specialty buttons showed pre-generated fake quotes
- Users saw results without experiencing the actual product
- 96% demo drop-off rate persists because users don't see the magic

## Solution

Replace static sample quotes with **job-focused prompt cards** that trigger the **real demo flow**.

Users tap a relatable job description → see the transcript ("You'd say...") → generate a real quote through the API → experience full editing, PDF download, all features.

## Design

### 1. Sample Prompt Cards

**Layout**: Grid of 5 cards, each showing:
- **Job title** (prominent): e.g., "Furniture Assembly"
- **Brief preview** (secondary): e.g., "2 IKEA chairs + bookshelf setup"
- No trade labels - jobs are universal

**Cards**:

| Job Title | Preview | Full Transcript |
|-----------|---------|-----------------|
| Furniture Assembly | 2 IKEA chairs + bookshelf setup | "I need help assembling 2 IKEA chairs and a bookshelf. Customer is providing the furniture, I just need my tools. Should take about 2 hours." |
| Strategy Workshop | Half-day session for leadership team | "Strategy workshop for a tech startup. Half-day session with their leadership team, 6 people. Need to cover market positioning and Q2 planning." |
| Birthday Party | Setup and cleanup for 30 guests | "Birthday party setup for a 10-year-old. Backyard party, about 30 kids. Need balloon arch, table setup, and cleanup after. 4 hours total." |
| Door Installation | Interior door with frame and hardware | "Interior door installation. Customer bought a pre-hung door from Home Depot. Need to remove old door, install new one with new hardware. Standard 32-inch doorway." |
| Logo Design | Brand package with 3 concepts | "Logo design for a new coffee shop called Morning Ritual. They want something modern but warm. I'll provide 3 initial concepts with 2 rounds of revisions." |

**Mobile**: 2-column grid, large touch targets (min 48px)

### 2. Header Reminder

Above the cards:
> "See instant sample quotes below. When you sign up, Quoted interviews you to learn YOUR pricing."

Sets expectation: samples use general pricing, real product learns their rates.

### 3. Tap Flow

1. **User taps card** → Card expands or modal shows full transcript
2. **Transcript display**: Speech bubble style with mic icon
   - "You'd say: [full transcript text]"
3. **Generate button**: Prominent CTA below transcript
4. **Subtle escape**: "or describe your own job →" link

### 4. Generation Flow

After tapping "Generate Quote":
1. Transcript auto-fills the text input (or sends directly)
2. Real API call to `/api/demo/generate`
3. Standard progress UI (analyzing, calculating, etc.)
4. Quote appears with full features:
   - Line items (editable)
   - Total
   - Clarifying questions
   - PDF download
   - Share link

User experiences the actual product, not a mockup.

### 5. What Gets Removed

From current DISC-162 implementation:
- `sampleQuotes` static JavaScript object
- `.sample-quote-display` section
- `.sample-quote-header`, `.sample-line-items`, etc.
- "Try YOUR job" CTA (redundant after real experience)

### 6. CSS Changes

- Keep: `.specialty-grid` base layout (rename to `.sample-cards`)
- Keep: Card hover/active states
- Add: Job title + preview text styling
- Add: Transcript reveal animation
- Add: Speech bubble styling for "You'd say"

## Technical Notes

- Reuse existing `generateQuoteFromText()` function
- Sample transcripts stored as data attributes or small JS object
- No new API endpoints needed
- PostHog events: `sample_card_viewed`, `sample_transcript_shown`, `sample_quote_generated`

## Success Metrics

- Demo completion rate: 4.4% → 25%+
- Time to first quote: < 30 seconds (tap + generate)
- Sample-to-signup conversion tracked via PostHog funnel

## Implementation Approach

1. Remove static sample quote display
2. Redesign specialty buttons → job cards with previews
3. Add transcript reveal on tap
4. Wire "Generate" to existing demo flow
5. Test on mobile (375px)
6. Verify full flow works end-to-end
