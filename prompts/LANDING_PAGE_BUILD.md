# quoted.it Landing Page Build Prompt

Build a landing page for quoted.it using the exact design system from `frontend/index.html` (dark charcoal, Playfair Display + Inter, minimal aesthetic).

---

## Core Message

**What it is:** Voice-to-quote tool for trade contractors. Speak about a job, get a budgetary estimate with line items in seconds.

**What it's NOT:**
- Not a detailed takeoff tool
- Not a binding contract generator
- Not replacing estimating software

**Position:** The quick ballpark number you give BEFORE pulling out the measuring tape. Qualifies leads fast, saves hours on tire-kickers.

---

## Target Audience

Solo trade contractors (deck builders, painters, roofers, fencers, GCs) who:
- Give 10+ estimates to close 2-3 jobs
- Hate evening paperwork
- Want to qualify leads on-site instantly

---

## Page Structure

### 1. Hero
- Logo: `quoted.it` (italic .it)
- Headline: **"Stop guessing. Start quoting."**
- Subhead: "Turn job site voice notes into budgetary estimates in seconds."
- CTA: "Start Quoting Free" → links to `/app` or sign-up

### 2. How It Works (3 steps)
1. **Speak** - "Describe the job naturally"
2. **Review** - "Get a structured quote with line items"
3. **Send** - "Export PDF or share the number"

### 3. The "Budgetary" Distinction
Headline: **"Ballpark quotes. Not blueprints."**

Make clear: This is for quick lead qualification, not final proposals. You still do detailed takeoffs for real jobs. This saves hours getting to that point.

### 4. Who It's For
Simple grid: Deck Builders, Painters, Roofers, Fence Installers, General Contractors, Landscapers

Copy: "If you give estimates and hate paperwork, this is for you."

### 5. Learning System
Headline: **"Gets smarter with every job."**

When you adjust quotes, the system learns your pricing patterns.

### 6. CTA Section
Headline: "Ready to stop writing quotes at midnight?"
Button: "Start Quoting Free"
Reassurance: "No credit card required."

---

## Technical

- Create `frontend/landing.html`
- Update backend to serve landing at `/` (logged-out) and app at `/app`
- Single HTML file, self-contained CSS
- Mobile-first, fast-loading
- Subtle scroll animations (fade-in, 0.4s ease-out)

---

## Copy Tone

- Direct, confident, practical
- NOT startup-y or hype-y
- Respect their time
- Clear about limitations

---

## Design Reference

Use exact variables from index.html:
```css
--bg-primary: #0a0a0a
--bg-secondary: #141414
--text-primary: #ffffff
--text-secondary: #a0a0a0
--font-serif: 'Playfair Display'
--font-sans: 'Inter'
```

Match the minimal, premium feel we established. Full-bleed sections, generous whitespace, elegant typography.
