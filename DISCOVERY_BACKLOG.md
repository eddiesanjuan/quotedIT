# Discovery Backlog

**Last Updated**: 2025-12-05
**Source**: `/quoted-discover` autonomous discovery cycles

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **DEPLOYED** | Implemented and live in production |
| **COMPLETE** | Implemented, pending deploy |
| **READY** | Approved, ready for implementation |
| **DISCOVERED** | Proposed, awaiting founder review |

To approve: Change status from DISCOVERED → READY

---

## Summary

| Status | Count |
|--------|-------|
| DEPLOYED | 23 |
| COMPLETE | 0 |
| READY | 2 |
| DISCOVERED | 22 |
| **Total** | **47** |

**Phase II Voice Control**: 8 tickets (DISC-042 through DISC-049) awaiting executive review

---

## Ready for Implementation

### DISC-014: Buildxact Competitive Defense (READY) ⚠️ Strategic

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: Long-term - existential threat if not addressed in 2025

**Problem**: Main competitor Buildxact could add voice interface in 6-12 months.

**Proposed Work**:
1. Accelerate learning system development: move RAG from backlog to Q1 priority
2. After 100 users, plan vertical integrations (QuickBooks, Jobber) for lock-in
3. Emphasize "learns YOUR pricing" (personal moat) over "has voice" (replicable)

**Success Metric**: RAG implemented Q1 2025; at least 1 integration partnership

---

### DISC-033: Reddit Contractor Launch Post 🚀 FOUNDER ACTION (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: 410K+ contractors on Reddit, single post could deliver 20%+ of beta goal

**Problem**: 410K+ contractors on Reddit, zero awareness of Quoted. Warm audience that complains daily about quoting friction. Demo ready but not distributed.

**Proposed Work**:
1. Craft founder-story Reddit post for r/contractors, r/Construction, r/smallbusiness
2. Format: "I built a voice-to-quote tool because I was tired of 30-minute spreadsheets - would love beta feedback"
3. Include demo link, emphasize learning system
4. Post during peak hours (Tuesday-Thursday 9am-11am EST)
5. Respond to every comment within 1 hour

**Success Metric**: 5,000+ impressions; 3% click demo (150 views); 15% convert = 22 signups

---

## Discovered (Awaiting Review)

### DISC-023: Contractor Community Outreach Plan 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: Product built but no distribution strategy. 5 users, need 95 more.

**Proposed Work (FOUNDER REQUIRED)**:
1. Reddit: Post in r/contractors, r/Construction, r/smallbusiness
2. Facebook Groups: 5 contractor groups
3. Blog/SEO: Create contractor-focused landing page

**Success Metric**: 200+ demo views; 20+ signups from community posts

---

### DISC-025: Landing Page Segment A/B Test 🧪 STRATEGIC

**Source**: Strategy Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0

**Problem**: Segment B (ballpark-only) beats Segment A on every metric, but messaging serves neither.

**Proposed**: Create TWO landing pages, split 80/20 Segment B/A, measure and pick winner.

---

### DISC-026: Pricing A/B Test ($19 vs $49) 🧪 STRATEGIC

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: Recent price drop signals value perception uncertainty. At 90%+ margin, pricing = positioning.

**Proposed**: A/B test value-based ($49) vs impulse ($19) pricing.

---

### DISC-027: LinkedIn Founder Content Blitz 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Proposed**: 6 daily LinkedIn posts with demo video, customer stories, urgency messaging.

**Success Metric**: 5,000+ impressions; 15-20 signups from LinkedIn

---

### DISC-029: Demo Quote Screenshot Sharing ⚡ QUICK WIN (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Converts 300+ demo sessions into viral acquisition channel

**Problem**: Demo users generate quotes but have no way to share them. Zero viral coefficient from demo sessions. Demo quotes disappear without creating any word-of-mouth.

**Proposed Work**:
1. Add "Share This Quote" button to demo results
2. Pre-populated social text: "Just generated a $X quote in 30 seconds with @QuotedApp - voice to quote is wild"
3. Screenshot preview for sharing
4. One-click share to LinkedIn, Twitter, or copy shareable image
5. Track shares via utm_source=demo_share

**Success Metric**: 20%+ demo users share (60 shares from 300 demos); 10% click-through = 6 additional signups

---

### DISC-030: Email Signature Viral Acceleration ⚡ QUICK WIN (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Activates existing 5 users as acquisition channel, multiplies founder network reach 10x

**Problem**: Email signature referral exists (DISC-021) but requires users to manually find it. Too much friction = low adoption. Referral program exists but not connected to daily workflow.

**Proposed Work**:
1. Auto-generate HTML email signature on first quote creation (not just available in settings)
2. Show preview modal: "Want more referrals? Add this to your email signature"
3. One-click "Copy to Clipboard" with instructions for Gmail/Outlook
4. Include in onboarding celebration
5. Pre-fill with user's referral code automatically

**Success Metric**: 60%+ users copy signature (vs current ~5%); each active user sends 20-50 emails/week = 300-500 signature impressions; 2-3% click-through = 6-15 signups from existing 5 users

---

### DISC-031: Voice Recording Fallback & Recovery (READY)

**Source**: Product Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Voice failure is likely top cause of demo/first-quote abandonment. Fixing this could increase activation to 60% target.

**Problem**: Voice input has no error recovery or fallback when browser Speech API fails (iOS Safari, privacy-blocked microphones, network issues). Users hit dead-end and abandon if voice fails.

**Proposed Work**:
1. Pre-check Speech API availability with friendly warning if unsupported
2. "Having trouble? Switch to text input" button during voice recording
3. Auto-detect 10s silence or errors and offer text alternative
4. Add browser compatibility badge ("Voice works best on Chrome/Edge")

**Success Metric**: Reduce quote-generation-started → quote-abandoned rate by 20%; voice-attempt → text-fallback conversion rate 40%+

---

### DISC-032: Autosave Quote Drafts (Local Storage) (READY)

**Source**: Product Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Removes anxiety around losing work, reduces rage-quit abandonment during critical first-quote experience

**Problem**: Users lose entire quote if they accidentally close tab, navigate away, or experience browser crash during editing. No draft recovery means they must restart from voice/text input.

**Proposed Work**:
1. Implement localStorage autosave every 10 seconds during quote generation/editing
2. On app load, detect unsaved draft and show recovery modal: "You have an unsaved quote from 15 minutes ago. Restore it?"
3. Store transcription text, generated quote data, and edit state
4. Clear draft after successful PDF download or explicit "Discard" action

**Success Metric**: Recovery modal shown 5-10% of sessions (proves value); quote-edit → PDF-download completion rate increases 15%

---

### DISC-033: Reddit Contractor Launch Post 🚀 FOUNDER ACTION (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: 410K+ contractors on Reddit, single post could deliver 20%+ of beta goal

**Problem**: 410K+ contractors on Reddit, zero awareness of Quoted. Warm audience that complains daily about quoting friction. Demo ready but not distributed.

**Proposed Work**:
1. Craft founder-story Reddit post for r/contractors, r/Construction, r/smallbusiness
2. Format: "I built a voice-to-quote tool because I was tired of 30-minute spreadsheets - would love beta feedback"
3. Include demo link, emphasize learning system
4. Post during peak hours (Tuesday-Thursday 9am-11am EST)
5. Respond to every comment within 1 hour

**Success Metric**: 5,000+ impressions; 3% click demo (150 views); 15% convert = 22 signups

---

### DISC-035: Learning System Trust Indicators (READY)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Critical for retention post-beta. Without this, users subscribing in Week 1-2 will churn in Week 3-4 when they realize learning hasn't kicked in yet.

**Problem**: With <10 corrections per user in beta, learning system can't demonstrate value before subscription decision. Users paying for "AI that learns YOUR pricing" but won't see meaningful improvement until months in.

**Proposed Work**:
1. Track category-level correction count in backend
2. Visual indicator on quotes: "High Confidence (12 corrections)" vs "Learning (2 corrections)"
3. Make learning progress transparent to set realistic expectations
4. Show learning dashboard in Pricing Brain section

**Success Metric**: NPS correlation with correction count; "Trust in pricing accuracy" survey score improvement; Reduced churn for users with <5 total corrections

---

### DISC-036: Keyboard Shortcuts for Power Users (READY)

**Source**: Product Discovery Agent
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Quick win that delights power users and positions product as professional tool

**Problem**: Quote generation workflow requires multiple mouse clicks through UI. No keyboard-driven workflow for users who generate 5-10 quotes/day. Extra clicks slow down expert users.

**Proposed Work**:
1. Add 5 essential shortcuts: Cmd/Ctrl+N = New quote, Cmd/Ctrl+E = Edit, Cmd/Ctrl+D = Download PDF, Cmd/Ctrl+S = Save, Cmd/Ctrl+Enter = Generate
2. Display shortcut hints on hover for discoverability
3. Add "Keyboard Shortcuts" help modal (Cmd/Ctrl+?)

**Success Metric**: Power users (5+ quotes/week) adopt shortcuts at 40%+ rate; avg time-per-quote decreases 20% for shortcut users

---

### DISC-037: Demo-to-Referral Incentive Bridge (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Combines "Demo Conversion" + "Referral Viral Loop" strategies. Highest potential user acquisition from single feature.

**Problem**: Demo users see value but have low urgency to sign up. Referral program exists but demo users can't participate. Missing conversion bridge between "this is cool" and "I need this now".

**Proposed Work**:
1. After demo quote generated, show modal: "Love it? Get 14 days free (instead of 7) + refer 3 contractors for permanent 50% off"
2. Pre-fill referral targets with "Who would benefit from this?" text inputs (3 email fields)
3. On signup, automatically send referral invites to those 3 emails
4. Creates immediate viral loop from demo conversion moment

**Success Metric**: 40% of demo signups submit referral emails; 30% of referrals sign up = 3.6x viral coefficient

---

### DISC-038: Duplicate Quote Template Feature (READY)

**Source**: Product Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Increases engagement and retention for repeat users who quote similar jobs

**Problem**: Contractors often quote similar jobs (same customer repeat work, similar scope projects). Currently must re-record or re-type entire job description each time.

**Proposed Work**:
1. Add "Duplicate" button to quote detail view and quote history items
2. Creates new quote pre-filled with: customer info, job type, line items structure, notes template
3. User makes quick adjustments and regenerates
4. Track duplicate_source_quote_id for learning insights

**Success Metric**: 25%+ of quotes marked as duplicates within 30 days; users who duplicate generate 2.5x more quotes

---

### DISC-039: "Voice Quote" Category Positioning (DISCOVERED)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: 6-12 month strategic horizon. Prevents Buildxact from stealing category in 2025.

**Problem**: "Voice-first contractor quotes" is an unclaimed category. Once Buildxact adds voice (6-12 months), first-mover advantage in category naming is lost.

**Proposed Work**:
1. Register voicequote.com domain, redirect to Quoted
2. Create "Voice Quote" buyer's guide comparing traditional estimating vs voice
3. SEO strategy around "voice quote software", "voice estimating", "voice bidding"
4. PR outreach: "Quoted Launches First Voice-Based Quoting Platform for Contractors"

**Success Metric**: Quoted ranks #1 for "voice quote software" within 90 days; Contractor survey: "When I think 'voice quote', I think ____" (target: 60%+ say Quoted)

---

### DISC-040: QuickBooks Integration for Lock-In (DISCOVERED)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: XL | **Score**: 0.75
**Sprint Alignment**: Post-beta (Q1 2025). Critical for defensibility - creates switching costs.

**Problem**: Learning system is defensible but copyable. Integrations create real switching costs. Contractor using Quoted→QuickBooks sync won't switch to competitor without migration pain.

**Proposed Work**:
1. Prioritize ONE strategic integration for Q1 2025 (after 100-user beta)
2. Start with QuickBooks Online API integration
3. Auto-create invoice from accepted quote
4. This becomes "reason not to switch" even if competitor launches voice

**Success Metric**: 40%+ of Pro tier users enable QuickBooks sync; Users with integration active have 3x lower churn

---

### DISC-041: Prompt Injection Learning Optimization 🧠 BRAINSTORM (READY)

**Source**: Founder Request (Eddie)
**Impact**: HIGH | **Effort**: M | **Score**: 0.85
**Sprint Alignment**: Core learning system enhancement. Next strategic R&D cycle.

**Problem**: Current learning system uses prompt injection to teach Claude about contractor pricing patterns. This works but could be significantly smarter. Need executive brainstorm on:
1. How to better structure injected context for model comprehension
2. Optimal format for learned adjustments (JSON vs natural language)
3. Memory efficiency - which patterns provide most signal per token
4. Feedback loop optimization - getting better faster with less data

**Proposed Work**:
1. Executive team brainstorm session on prompt engineering improvements
2. Research latest Claude prompt optimization techniques
3. A/B test different context injection formats
4. Measure quote accuracy delta per approach
5. Document optimal patterns for Quoted learning system

**Success Metric**: 15% improvement in quote accuracy; 20% reduction in prompt tokens needed

---

## 🎯 Phase II: Voice-Controlled Professional's Paradise

**Status**: READY -
**Source**: Founder Vision (Eddie, 2025-12-05)
**Theme**: Transform Quoted from "voice input" to "fully voice-controlled" professional tool
**Timeline**: Post-beta (Q1-Q2 2025)

**Core Insight**: Contractors work from trucks and job sites, not desks. The natural evolution of Quoted is complete hands-free operation where complex workflows happen through natural language. Voice input was Phase I. Voice control is Phase II.

**Strategic Value**: This creates a moat that's nearly impossible to replicate quickly. Competitors can copy "voice-to-text". They can't easily copy "understands 'add more fluff for a difficult customer' and modifies quote tone accordingly."

---

### DISC-042: Voice Command Interpreter Engine 🧠 PHASE II FOUNDATION (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: CRITICAL | **Effort**: XL | **Score**: Strategic
**Sprint Alignment**: Foundation for all Phase II features. Must be robust before other voice features.
**Dependencies**: None (foundational)

**Problem**: Current voice input is transcription-only. User speaks, AI transcribes, generates quote. No interpretation of commands or intent. Can't say "increase the deck by 10 feet" and have it actually happen.

**Vision**: Natural language command processing that understands contractor intent and executes complex multi-step actions.

**Example Commands to Support**:
- CREATE: "Go ahead and make another quote for John Smith at 1234 Prospect Promenade"
- MODIFY PARAMETERS: "Increase the size of his deck by 10 feet in each direction"
- MODIFY TONE: "Edit this quote so it has a little bit more fluff because this customer is going to be difficult"
- SEARCH: "Pull up the quote I did for the Johnsons last week"
- DUPLICATE: "Clone this quote but change the address to 456 Oak Street"
- SHARE: "Email this to the customer"

**Technical Architecture**:
1. **Intent Classification Layer**: Determine action type (create, edit, search, share, regenerate)
2. **Entity Extraction**: Parse names, addresses, measurements, materials, descriptors
3. **Context Resolution**: "His deck" refers to current quote's deck line item
4. **Action Router**: Map intent + entities to specific backend actions
5. **Confirmation Generation**: Create natural language confirmation before execution

**Proposed Work**:
1. Design intent taxonomy (10-15 core intents covering 95% of use cases)
2. Build entity extraction pipeline (names, addresses, numbers with units, materials)
3. Create context resolution system (current quote, recent history, customer relationships)
4. Implement action router with confirmation loop
5. Train/prompt-engineer Claude for command interpretation
6. Build fallback to clarifying questions when intent is ambiguous

**Success Metric**: 90% intent classification accuracy; <3% false-positive command execution; users prefer voice commands over clicking for 60%+ of actions

**Executive Review Questions**:
- Should we use Claude for interpretation or a dedicated NLU model?
- What's minimum viable intent set for Phase II launch?
- Latency budget: How long can users wait between command and action?

---

### DISC-043: Continuous Listening Mode 🎤 PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: Enables true hands-free operation for on-the-go professionals
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Current voice requires clicking record button, speaking, clicking stop. This is fine for initial quote creation but terrible for editing workflow. Contractors with dirty hands, driving between jobs, or walking a job site can't keep clicking buttons.

**Vision**: True hands-free operation where the app listens continuously and responds to voice commands.

**User Experience**:
1. User enables "Hands-Free Mode" (toggle or voice command)
2. App displays listening indicator
3. User speaks naturally: "Quoted, increase the deck price by $500"
4. App confirms: "Increase deck from $2,400 to $2,900. Confirm?"
5. User: "Yes" or "No, make it $2,800"
6. App executes and provides audio/visual confirmation

**Proposed Work**:
1. Implement wake word detection ("Quoted", "Hey Quote", or custom)
2. Add push-to-talk alternative for noisy environments
3. Visual listening state indicator (pulsing mic, waveform)
4. Audio feedback option (voice confirmations for eyes-free use)
5. Timeout and auto-sleep after inactivity
6. Battery optimization for mobile PWA/native

**Success Metric**: 40% of power users (5+ quotes/week) enable continuous mode; average session uses 3+ voice commands

**Executive Review Questions**:
- Wake word vs push-to-talk vs always-listening? (Privacy/battery implications)
- Should confirmations be voice, visual, or user-configurable?
- PWA limitations: Is native app required for background listening?

---

### DISC-044: Quote Modification via Natural Language ✏️ PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: The "magic" of Phase II - speak changes, watch them happen
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Editing quotes currently requires finding the right field, clicking, typing. For simple changes like "add $200 to the labor line", this is friction. For complex changes like "make this quote less aggressive because the customer seemed price-sensitive", there's no way to do it at all.

**Vision**: Natural language modifications that AI interprets and applies to quotes.

**Modification Categories**:

1. **Parameter Changes** (quantitative):
   - "Increase the deck size by 10 feet in each direction"
   - "Add $500 to the labor line item"
   - "Change the total to $15,000" (AI adjusts line items proportionally)
   - "Apply a 15% discount"

2. **Scope Changes** (structural):
   - "Add a pergola to this quote"
   - "Remove the lighting package"
   - "Split the deck into two phases"
   - "Combine these three items into one 'Materials' line"

3. **Tone/Style Changes** (qualitative):
   - "Add more fluff because this customer is going to be difficult"
   - "Make it more professional - this is a commercial client"
   - "Simplify the descriptions - customer said they don't need details"
   - "Add more technical specs - customer is an engineer"

4. **Customer Context Changes**:
   - "This is a repeat customer, add our loyal customer discount"
   - "They mentioned budget constraints, show value emphasis"
   - "They're in a hurry, emphasize quick turnaround"

**Proposed Work**:
1. Build modification intent classifier (parameter/scope/tone/context)
2. Create parameter change executor (understands units, percentages, relative changes)
3. Implement scope change handler (add/remove/restructure line items)
4. Develop tone modification prompts (regenerate with style guidance)
5. Add preview/diff view before applying changes
6. Maintain edit history for undo capability

**Success Metric**: 80% of voice modification commands execute correctly; users make 2x more edits per quote with voice vs click

**Executive Review Questions**:
- How much regeneration is acceptable? (Tone changes require AI rewrite)
- Should we show AI confidence before applying changes?
- Undo depth: How many modifications should be reversible?

---

### DISC-045: Customer & Address Memory System 📇 PHASE II ENABLER (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Required for "make a quote for John Smith" to work
**Dependencies**: Builds on DISC-022 (Customer Autocomplete)

**Problem**: Voice commands like "make another quote for John Smith" require the system to know who John Smith is, his address, and his history. Current customer autocomplete (DISC-022) is search-based, not voice-command-ready.

**Vision**: Rich customer database that voice commands can reference naturally.

**Required Capabilities**:
1. **Name Resolution**: "John Smith" → correct John Smith from database (handle duplicates)
2. **Address Book**: Store multiple addresses per customer ("his office", "the rental property")
3. **History Context**: Know what quotes were done for customer previously
4. **Relationship Memory**: "Repeat customer", "referred by Mike", "always negotiates"
5. **Preference Storage**: "Prefers detailed quotes", "always asks for military discount"

**Voice Commands Enabled**:
- "Make another quote for John Smith at the usual address"
- "Quote the same job we did for the Hendersons, but for the Wilsons"
- "What was our last quote for the customer on Elm Street?"
- "Add John's wife Mary as a contact on this quote"

**Proposed Work**:
1. Extend customer model: multiple addresses, relationship notes, preferences
2. Build fuzzy name matching for voice (handles "Jon" vs "John", nicknames)
3. Create disambiguation flow: "I found 2 John Smiths. Oak Street or Maple Avenue?"
4. Implement quote history per customer with searchable context
5. Add customer preference storage with voice-settable fields
6. Design customer merge/dedup workflow

**Success Metric**: 95% correct customer resolution on voice commands; customers with 2+ quotes have 40% faster quote creation

**Executive Review Questions**:
- How to handle common names? (Voice disambiguation vs visual list?)
- Customer data import from contacts/CRM?
- Privacy: How long to retain customer history?

---

### DISC-046: Prompt Tweaking & Quote Regeneration 🔄 PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Enables iterative refinement without re-recording
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: User generates a quote but it's not quite right. Currently must either manually edit every field OR re-record the entire job description. No middle ground. User can't say "regenerate with more emphasis on quality materials" or "redo this assuming premium pricing".

**Vision**: Expose and allow modification of the prompt that generated the quote, then regenerate.

**Two User Paths**:

1. **Voice-Guided Regeneration** (most common):
   - "Regenerate this quote with more detail on materials"
   - "Redo assuming the customer wants premium everything"
   - "Make this quote 20% higher and justify the pricing"
   - "Regenerate but assume we're competing on price"

2. **Prompt Template Editing** (power users):
   - Show the actual prompt that was sent to Claude
   - Allow direct editing of prompt text
   - Save as template for future quotes
   - Per-category prompt customization

**User Experience - Voice Path**:
1. User views generated quote
2. User: "Regenerate this with more emphasis on durability"
3. System shows: "I'll regenerate emphasizing durability and quality materials. The new quote may have different pricing."
4. User: "Go ahead"
5. System regenerates, shows diff from original
6. User: "Keep the new version" or "Undo, go back to original"

**Proposed Work**:
1. Store generation prompt with each quote (not just output)
2. Build prompt modification interpreter ("more detail" → specific prompt additions)
3. Create regeneration pipeline with original context + modifications
4. Implement side-by-side or diff view for comparing versions
5. Add version history (keep last 3 generations per quote)
6. Build prompt template library for common scenarios

**Success Metric**: 30% of quotes regenerated at least once; regenerated quotes have 20% fewer manual edits

**Executive Review Questions**:
- Token cost: Regeneration = 2x API cost. Acceptable?
- Should original quote be preserved or replaced?
- Prompt template sharing between users? (Marketplace opportunity?)

---

### DISC-047: Voice Interpretation Correction UI 🎯 PHASE II POLISH (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Critical for trust - users must be able to fix misheard commands
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Voice recognition will sometimes fail. "John Smith" becomes "Jon Smyth". "$2,500" becomes "$25,000". If users can't quickly correct these errors, trust in the system collapses. The founder specifically noted: "there will inevitably be some text interpretation problems here and there that a quick fix would be nice on."

**Vision**: Seamless correction flow where misheard commands are easy to fix without starting over.

**Correction Flow**:
1. User speaks command
2. System shows interpretation BEFORE executing:
   ```
   I heard: "Make a quote for Jon Smyth at 1234 Prospect Road"
   → Creating quote for Jon Smyth at 1234 Prospect Road

   [Execute] [Edit] [Cancel]
   ```
3. User taps "Edit" → inline editing of interpreted text
4. System re-parses corrected text
5. User confirms, system executes

**Quick Fix Patterns**:
- **Tap-to-correct**: Tap any word to edit just that word
- **Voice correction**: "No, I said Smith, not Smyth"
- **Suggestions**: "Did you mean 'John Smith' from your contacts?"
- **History learn**: Remember corrections to improve future recognition

**Proposed Work**:
1. Always show interpretation before execution (no silent actions)
2. Build inline word-level editing UI
3. Implement "Did you mean...?" suggestions from context
4. Add voice-based correction path ("No, I said...")
5. Create correction learning system (user-specific improvements)
6. Track correction rate as quality metric

**Success Metric**: <5% of commands need correction; corrections take <3 seconds; correction rate decreases 50% over first month of use

**Executive Review Questions**:
- How much friction is acceptable? (Always confirm vs trust mode?)
- Should corrections feed back to improve recognition? (Privacy implications)
- Voice-only correction or must have visual? (Accessibility for eyes-free use)

---

### DISC-048: Multi-Turn Conversational Interface 💬 PHASE II ADVANCED (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: MEDIUM | **Effort**: XL | **Score**: 0.5
**Sprint Alignment**: Advanced capability after core voice features stable
**Dependencies**: DISC-042, DISC-043, DISC-044 (all core voice features)

**Problem**: Complex workflows currently require multiple separate commands or clicking through UI. No conversational flow. User can't have a back-and-forth dialogue to refine a quote.

**Vision**: Natural multi-turn conversations where context carries forward.

**Example Conversation**:
```
User: "Start a new deck quote"
Quoted: "Sure, who's the customer?"
User: "The Hendersons on Oak Street"
Quoted: "Got it - Mike Henderson, 456 Oak Street. What size deck?"
User: "About 400 square feet, pressure-treated lumber"
Quoted: "400 sq ft deck, pressure-treated. Should I include railing?"
User: "Yeah, and add stairs"
Quoted: "Here's a $12,500 estimate for a 400 sq ft deck with pressure-treated lumber, railing, and stairs. Would you like to see the breakdown?"
User: "That's high - can you do it closer to $10k?"
Quoted: "I can bring it to $10,200 by switching to standard lumber and simpler railing. Want me to make that change?"
User: "Show me both options"
Quoted: [Shows comparison view]
```

**Key Capabilities**:
1. **Context Persistence**: Remember what was discussed in current session
2. **Clarifying Questions**: AI asks for missing info instead of guessing
3. **Progressive Refinement**: Build quote through dialogue, not single command
4. **Negotiation Assistance**: Help contractor think through pricing options
5. **Teaching Moments**: "Based on similar jobs, you might want to consider..."

**Proposed Work**:
1. Build conversation state management (session memory)
2. Create guided quote creation flow (required fields as questions)
3. Implement clarifying question generation
4. Add comparison/option generation for negotiation
5. Build conversation history UI
6. Design graceful handoff between voice and visual editing

**Success Metric**: Users complete 25% of quotes through conversation; conversational quotes have 15% higher customer conversion

**Executive Review Questions**:
- How much "personality" should Quoted have in conversations?
- Conversation history retention: Per session or persistent?
- This is a major UX shift - A/B test or full rollout?

---

### DISC-049: Phase II Architecture & Technical Spike 🏗️ (DISCOVERED)

**Source**: Engineering Planning
**Impact**: CRITICAL | **Effort**: L | **Score**: Strategic
**Sprint Alignment**: Must complete before any Phase II development begins
**Dependencies**: None (planning activity)

**Problem**: Phase II features require significant architectural decisions. Current system is request-response; Phase II is stateful and conversational. Need technical spike before committing to implementation.

**Questions to Answer**:
1. **Voice Processing**: Web Speech API vs Whisper vs Deepgram vs Assembly AI?
   - Accuracy comparison for contractor terminology
   - Latency requirements for conversational flow
   - Cost at scale (1000+ users, 10+ commands/day)
   - Offline capability for job site use

2. **Intent Classification**: Claude prompt engineering vs fine-tuned model vs hybrid?
   - Latency budget (user speaks → action)
   - Cost per command
   - Accuracy on edge cases
   - Ability to improve over time

3. **State Management**: How to maintain conversation context?
   - Session storage architecture
   - Context window management for long conversations
   - Multi-device sync (start on phone, continue on desktop?)

4. **Native vs PWA**: Can Phase II work as PWA or does continuous listening require native?
   - iOS/Android audio API limitations
   - Background processing requirements
   - Push notification for async operations

**Proposed Work**:
1. Prototype voice command pipeline with 3 different speech-to-text services
2. Benchmark intent classification approaches (latency, accuracy, cost)
3. Design state management architecture for conversational UI
4. PWA feasibility assessment for continuous listening
5. Cost model at 1000 users × 50 commands/day
6. Deliver technical recommendation document

**Success Metric**: Clear go/no-go decision on architecture; cost model within 2x of estimates; all technical risks identified

**Executive Review Questions**:
- Budget for Phase II technical spike? (Estimate: 40-80 engineering hours)
- Is native app acceptable if PWA can't support Phase II?
- Latency requirement: What's acceptable for voice command response?

---

## Completed & Deployed

<details>
<summary>Click to expand completed items (23 items)</summary>

### DISC-013: Animation Walkthrough Distribution Strategy ✅
**Commit**: 856f051 | Demo-promo landing page with UTM tracking, PostHog events, pre-written social copy

### DISC-028: PDF Quote Template Library ✅
**Commit**: 2e88a94 | 8 templates (classic, modern, bold, elegant, technical, friendly, craftsman, corporate) + accent colors, tier-gated

### DISC-001: First Quote Activation Flow ✅
**Commit**: 8628869 | Post-onboarding modal with voice/text paths

### DISC-002: Referral Program Early Visibility ✅
**Commit**: 5c1ebc3 | Referral section in celebration modal

### DISC-003: Landing Page CTA Clarity ✅
**Commit**: fd82e2f | Demo primary, signup secondary

### DISC-004: Analytics Funnel Gaps ✅
**Commit**: 9607ccf | Full conversion tracking events

### DISC-005: Trial→Upgrade Journey Friction ✅
**Commit**: 412f5da | Single-click upgrade from banner

### DISC-006: Animation Walkthrough→Signup Flow ✅
**Commit**: c8addfa | Conversion modal after animation

### DISC-007: Onboarding Path A/B Testing ✅
**Commit**: b5d55b1 | Track path selection and outcomes

### DISC-008: Learning System Visibility ✅
**Commit**: 57c3aff | Learning progress section in Pricing Brain

### DISC-009: First Quote Celebration Enhancement ✅
**Commit**: dd5c41e | Enhanced celebration with share/referral

### DISC-010: Testimonial Collection System ✅
**Commit**: fabe2c6 | 5-star rating modal after 3rd quote

### DISC-011: Voice-First Assumption Validation ✅
**Commits**: f1053b8, ecc2be1 | Text-first option, voice as enhancement

### DISC-012: Learning System Analytics ✅
**Commit**: 412f5da | Track correction patterns

### DISC-015: Social Proof Scarcity ✅
**Commit**: 3d8f8fa | Beta spots counter

### DISC-016: Premium PDF Branding (Logo) ✅
**Commit**: 94ba6dc | Custom logo upload

### DISC-017: Trial Abuse Prevention ✅
**Commit**: 8c88de2 | Email normalization + disposable blocking

### DISC-018: Trial Grace Period ✅
**Commit**: 136d244 | Soft warnings + 3 grace quotes

### DISC-019: "Try It First" Fast Activation ✅
**Commit**: 0ade9e9 | Skip interview, use industry defaults

### DISC-020: Exit-Intent Survey ✅
**Commit**: 048d173 | Capture why visitors leave

### DISC-021: Email Signature Referral Hack ✅
**Commit**: 8672a3e | Pre-written signature with referral link

### DISC-022: Customer Memory (Autocomplete) ✅
**Commit**: e3c8786 | Autofill returning customers

### DISC-024: Viral Footer Enhancement ✅
**Commit**: 1c3d0d3 | CTA in shared quote footer

### DISC-034: Pricing Sanity Check ✅
**Commit**: 926c135 | Statistical bounds on quote generation to prevent hallucinations

</details>

---

## Discovery Process

New discoveries are generated by `/quoted-discover` which spawns 3 parallel agents:
1. **Product Discovery Agent** - UX friction, feature gaps
2. **Growth Discovery Agent** - Acquisition, activation, retention opportunities
3. **Strategy Discovery Agent** - Competitive threats, market positioning

Each discovery is scored: **Impact/Effort Ratio** (higher = better)
- Impact: HIGH=3, MEDIUM=2, LOW=1
- Effort: S=1, M=2, L=3, XL=4
