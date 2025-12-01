# quoted.it Landing Page Build Prompt

## Context

You are building a landing page for **quoted.it** - a voice-to-quote tool for trade contractors. The landing page should use the existing design system (dark charcoal background, Playfair Display + Inter fonts, minimal aesthetic) and clearly communicate what the product does, who it's for, and why they should use it.

---

## Product Definition

### What quoted.it Does

**Core function:** Converts voice notes into budgetary estimates in seconds.

A contractor visits a job site, records a quick voice note describing what they see ("20 by 16 composite deck, Trex in Pebble Grey, need to demo the old deck, about 40 feet of railing..."), and receives a structured quote with line items and a total.

**Key capabilities:**
1. **Voice → Quote**: Speak naturally, get a professional estimate
2. **AI-Powered Pricing**: Learns the contractor's pricing patterns over time
3. **Job Type Intelligence**: Understands decks vs. fences vs. paint jobs
4. **Correction Learning**: When contractors adjust quotes, the system learns
5. **PDF Export**: Professional output ready to share with customers

### What quoted.it is NOT

**This is critical messaging:**

- **NOT a detailed takeoff tool** - doesn't measure from blueprints
- **NOT a binding contract generator** - these are ballpark estimates
- **NOT for final proposals** - it's the first-pass number
- **NOT replacing estimating software** - it's the quick qualifier before that

**Position clearly:** This is for giving customers a ballpark number in 30 seconds, not replacing your detailed estimating process.

---

## Target Audience

### Primary: Solo Trade Contractors

**Who they are:**
- Deck builders, painters, roofers, fence installers, general contractors
- 1-10 person operations
- Do their own sales and estimating
- Constantly balancing field work with office work

**Their pain points:**
- Hate paperwork and spreadsheets
- Give 10+ estimates to close 2-3 jobs
- Tire kickers waste their time
- Evening/weekend quote writing steals family time
- Inconsistent pricing because they're quoting from memory

**What they want:**
- More time on profitable work, less on admin
- Quick way to qualify or disqualify leads
- Professional appearance without the overhead
- Consistent pricing they don't have to think about

### Use Case Scenarios

**Scenario 1: The Job Site Visit**
> Contractor is at a potential customer's house looking at a deck project. Instead of saying "I'll get back to you with a number," they record a 30-second voice note and hand the customer a ballpark before leaving.

**Scenario 2: The Phone Inquiry**
> Someone calls asking "How much for a 300 sq ft deck?" Instead of guessing or saying "I'd have to see it," contractor quickly speaks the details and gives a confident range.

**Scenario 3: The Evening Follow-Up**
> Contractor saw 4 potential jobs today. Instead of spending 2 hours writing quotes at night, they record 4 voice notes in 10 minutes and have budgetary numbers ready.

---

## Value Proposition

### Headline Options (pick one or iterate)

**Primary recommendation:**
> "Stop guessing. Start quoting."

**Alternatives:**
> "Voice to quote in 30 seconds."
> "Your pricing brain, always on."
> "Ballpark quotes without the ballpark guessing."
> "The estimate before the estimate."

### Subheadline

> Speak naturally about a job. Get a budgetary quote with line items. Learn from every correction. Built for contractors who'd rather be building.

### The Core Promise

**Before quoted.it:**
- Write quotes at night after long days
- Inconsistent pricing based on mood/memory
- Lose deals waiting to "get back to them"
- Tire kickers waste hours of your time

**After quoted.it:**
- Quote on-site in 30 seconds
- Consistent pricing every time
- Qualify leads instantly
- More time for actual work

---

## Landing Page Structure

### Section 1: Hero

**Elements:**
- Logo: `quoted.it` (with italic .it)
- Headline: Large serif, impactful
- Subheadline: 1-2 sentences explaining the core value
- CTA: "Start Quoting Free" or "Try It Now"
- Optional: Simple animation or visual of voice → quote transformation

**Tone:** Confident, minimal, professional. Not salesy or startup-y.

### Section 2: How It Works

**Three steps, visually simple:**

1. **Speak**
   > Describe the job naturally. "It's a 20x16 composite deck with Trex Select..."

2. **Review**
   > Get a structured quote with line items. Adjust if needed.

3. **Send**
   > Export a clean PDF or share the ballpark number directly.

**Visual approach:** Show actual UI screenshots or simplified representations. Keep it clean - no cluttered feature screenshots.

### Section 3: The "Budgetary" Distinction

**This section is critical for setting expectations.**

**Headline:** "Ballpark quotes. Not blueprints."

**Copy:**
> quoted.it generates budgetary estimates - the number you give before you pull out the measuring tape. It's designed to help you:
>
> - Qualify leads faster
> - Give customers a confident range on the spot
> - Stop wasting time on tire kickers
>
> For detailed takeoffs and final proposals, you'll still do what you do. This is the quick qualifier that saves you hours every week.

### Section 4: Who It's For

**Visual:** Grid or simple list of trade types

- Deck Builders
- Painters
- Roofers
- Fence Installers
- General Contractors
- Landscapers
- And more...

**Copy:**
> If you give estimates and hate paperwork, quoted.it is for you.

### Section 5: The Learning System

**Headline:** "Gets smarter with every job."

**Copy:**
> When you adjust a quote, quoted.it learns. Over time, it understands your pricing patterns - your labor rates, your material markups, your style of quoting. The more you use it, the closer it gets to how you actually price.

**Visual:** Simple diagram showing correction → learning → better future quotes

### Section 6: Pricing

**Keep it simple. One tier to start:**

**Free during beta** or simple pricing like:
- Free: 10 quotes/month
- Pro: $29/month unlimited

**Avoid feature matrix complexity.** This is a simple tool.

### Section 7: CTA / Sign Up

**Headline:** "Ready to stop writing quotes at midnight?"

**CTA Button:** "Start Quoting Free"

**Reassurance:** "No credit card required. Set up in 2 minutes."

---

## Design Guidelines

### Use the existing design system:

```css
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #141414;
    --bg-card: #1a1a1a;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
    --text-muted: #666666;
    --border: rgba(255, 255, 255, 0.1);
    --font-serif: 'Playfair Display', Georgia, serif;
    --font-sans: 'Inter', -apple-system, sans-serif;
}
```

### Typography:
- Headlines: Playfair Display, large, light weight
- Body: Inter, clean, readable
- All caps sparingly for labels

### Layout:
- Generous whitespace
- Max-width container (~1200px)
- Full-bleed sections with contained content
- Mobile-first responsive

### Imagery:
- Minimal or none
- If used: High-contrast, black and white aesthetic
- Consider simple iconography over photos
- UI screenshots should be clean, not cluttered

### Interactions:
- Subtle fade-in animations on scroll
- Smooth scroll to sections
- Hover states that feel premium, not flashy

---

## Copy Guidelines

### Voice and Tone

**Be:**
- Direct and confident
- Practical, not hype-y
- Respectful of the contractor's time
- Clear about what this is (and isn't)

**Avoid:**
- Startup jargon ("disrupt," "revolutionize")
- Overpromising ("never write a quote again")
- Condescension ("even you can use it")
- Feature dumps (focus on outcomes)

### Key Phrases to Use

- "Budgetary quote" / "Ballpark estimate"
- "Qualify leads"
- "On-site pricing"
- "Voice to quote"
- "Learn from corrections"

### Key Phrases to Avoid

- "AI-powered" as a selling point (it's a means, not the value)
- "Instant" (30 seconds is fast enough, don't oversell)
- "Accurate" (it's a ballpark, accuracy comes with detailed takeoffs)
- "Replace your estimating" (it complements, doesn't replace)

---

## Technical Requirements

### Page should be:
- Single HTML file (like the app)
- Self-contained CSS
- Minimal JavaScript (scroll animations only)
- Fast-loading (no heavy assets)
- Mobile responsive
- Accessible (semantic HTML, contrast ratios)

### Integration:
- CTA should link to `/app` or the main application
- Consider separate route (`/` for landing, `/app` for application)
- Or: Landing page replaces auth view for logged-out users

### SEO Basics:
- Proper meta title and description
- Open Graph tags for social sharing
- Semantic heading hierarchy

---

## Success Metrics

The landing page should:

1. **Communicate clearly** - Visitor understands what this is in <10 seconds
2. **Set expectations** - Clear that this is for budgetary quotes, not detailed estimates
3. **Feel premium** - Design matches the professional positioning
4. **Convert** - Clear path to sign up / try it
5. **Load fast** - Under 2 seconds on mobile

---

## Example Copy Blocks

### Hero

```
quoted.it

Stop guessing.
Start quoting.

Turn job site voice notes into budgetary estimates in seconds.
Your pricing. Your style. Gets smarter with every job.

[Start Quoting Free]
```

### How It Works

```
How it works

1. Speak naturally
   "20 by 16 composite deck, Trex Select, demo the old wood deck,
   40 feet of aluminum railing, three steps down..."

2. Review the quote
   Get a structured estimate with line items. Adjust anything that
   doesn't look right.

3. Share or save
   Export a clean PDF or just share the ballpark number.
   Move on to the next lead.
```

### The Distinction

```
Ballpark quotes.
Not blueprints.

This isn't detailed estimating software. It's the quick number you
give before you pull out the measuring tape.

Use it to:
• Qualify leads on the spot
• Give confident ranges during phone calls
• Stop wasting evenings on tire-kicker quotes

For final proposals, you'll still do your detailed takeoff.
This just saves you hours getting to that point.
```

---

## Implementation Notes

When building:

1. Start with mobile layout, scale up
2. Test with real contractor language in the examples
3. Keep animations subtle (0.3s-0.6s, ease-out)
4. Ensure CTA is visible without scrolling on mobile
5. Add skip-to-content for accessibility
6. Test in Safari, Chrome, Firefox at minimum

---

## Files to Create/Modify

**Option A: Separate landing page**
- Create `frontend/landing.html`
- Modify backend to serve landing at `/` and app at `/app`

**Option B: Integrated landing**
- Modify `frontend/index.html` to show landing for logged-out users
- App view for logged-in users

Recommend **Option A** for cleaner separation.
