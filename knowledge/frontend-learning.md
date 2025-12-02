# Frontend Learning

**Last Updated**: 2025-12-02
**Purpose**: Accumulated knowledge about the Quoted frontend codebase

---

## Architecture

### Stack
- Vanilla HTML/CSS/JS (no framework)
- Single-page app in `frontend/index.html` (~35K tokens after billing UI)
- Landing page in `frontend/landing.html`
- Mobile-first responsive design

### Design System
- Dark premium aesthetic (#0a0a0a background, not blue)
- Accent: White text with amber/warning for CTAs
- Background: Dark grays (#0a0a0a, #141414, #1a1a1a)
- Font: Playfair Display (serif) for headings, Inter (sans) for body
- Border radius: 8px (inputs), 12px (cards), 16px (pricing cards), 100px (pills)

---

## Key Learnings

| Date | Learning | Context |
|------|----------|---------|
| 2025-12-02 | Tab navigation pattern for multi-view sections | Account section uses tabs (Billing + Pricing Brain) with active state management and lazy loading |
| 2025-12-02 | Safe DOM construction prevents XSS in dynamic cards | Category cards built with createElement/textContent, avoiding innerHTML with user data |
| 2025-12-02 | Modal pattern with backdrop-filter and outside-click close | Edit Category modal follows established pattern from Edit Customer modal |
| 2025-12-02 | Empty states use dashed borders and emoji icons | Empty category state shows 📚 icon with encouraging message |
| 2025-12-02 | Grid auto-fill for responsive card layouts | category-cards-grid uses repeat(auto-fill, minmax(300px, 1fr)) for flexible layout |
| 2025-12-02 | Confidence badges use conditional color classes | high-confidence=green, medium-confidence=yellow, low=gray for visual hierarchy |
| 2025-12-02 | Pattern hints vs AI analysis: instant vs on-demand | Pattern hints load instantly from stored data, AI analysis costs ~$0.001 per request |
| 2025-12-02 | Fisher-Yates shuffle for slot animation randomization | Landing page slot machine now shows random industry order on each load |
| 2025-12-02 | Customer info edit modal follows upgrade modal pattern | Reusable modal-overlay + modal-content structure with outside-click close |
| 2025-12-02 | Customer info section uses grid layout for responsive display | auto-fit minmax(200px, 1fr) adapts to mobile/tablet/desktop |
| 2025-12-02 | Edit icons use inline SVG for crisp rendering | 16x16 pencil icon scales perfectly at any screen resolution |
| 2025-12-02 | Billing UI built with safe DOM methods (no innerHTML) | XSS prevention - used createElement/textContent instead of innerHTML |
| 2025-12-02 | Global fetch wrapper intercepts 402 responses | Automatically shows upgrade modal when quote limit reached |
| 2025-12-02 | Usage widget uses gradient fill with color-coded warnings | Green→Yellow at 80%, Red at 90% usage |
| 2025-12-02 | Pricing cards use flexbox with flex-grow for equal height | Features list grows to fill space, CTA always at bottom |
| 2025-12-02 | Modal overlays use backdrop-filter: blur(8px) | Modern glassmorphism effect for upgrade modal |
| 2025-12-02 | Trial banner shows days remaining with gradient background | Warning/amber gradient (#fbbf24) for urgency |
| 2025-12-02 | Executive-approved messaging emphasizes "Right Estimate for Right Stage" | Replaces "Ballpark quotes. Not blueprints." - addresses fuzzy early project stage |
| 2025-12-02 | "Qualify faster. Close more." becomes key tagline | Approved by exec team after messaging audit |
| 2025-12-02 | Learning section leads with "Gets smarter with every correction" | Emphasizes continuous improvement and user-specific training |
| 2025-12-02 | Legal pages match landing design with serif headings | Consistent brand across legal content |
| 2025-12-02 | Legal content uses readable typography with line-height 1.8 | Optimized for dense legal text |
| 2025-12-01 | Inline styles keep the single-file approach manageable | No build step, easy deployment |
| 2025-12-01 | Mobile-first: Contractors use phones on job sites | Touch targets minimum 44px |
| 2025-12-01 | Dark mode matches professional tool aesthetic | Contractors already use dark mode in shop apps |
| 2025-12-01 | Industry spinner on landing page creates engagement | Personalization before signup |

---

## CSS Patterns

### Card Style
```css
background: #1F2937;
border: 1px solid #374151;
border-radius: 8px;
padding: 16px;
```

### Button Primary
```css
background: #3B82F6;
color: white;
border: none;
border-radius: 8px;
padding: 12px 24px;
cursor: pointer;
transition: background 0.2s;
```

### Form Input
```css
background: #111827;
border: 1px solid #374151;
color: white;
padding: 12px;
border-radius: 8px;
```

---

## Common Gotchas

1. **Single file**: index.html is large, use search to navigate
2. **No hot reload**: Refresh browser to see changes
3. **API base URL**: Uses relative paths (/api/...)
4. **Mobile viewport**: Always test at 375px width
5. **Touch targets**: Minimum 44x44px for buttons

---

## Landing Page Structure

1. Hero: Bold headline + industry spinner + CTA
2. How it works: 3-step visual flow
3. Features: Speed, learning, simple
4. Social proof: Placeholder for testimonials
5. CTA: Final signup push

---

## Files to Know

| File | Purpose | Size |
|------|---------|------|
| `frontend/index.html` | Main app (auth, quotes, history, billing, pricing brain) | ~38K tokens |
| `frontend/landing.html` | Marketing landing page | ~4K tokens |
| `frontend/terms.html` | Terms of Service legal page | ~400 lines |
| `frontend/privacy.html` | Privacy Policy legal page | ~450 lines |
| `frontend/static/` | Static assets | Minimal |

---

## Pending Improvements

- [ ] Extract CSS to separate file
- [ ] Add loading skeletons
- [ ] Improve quote editing mobile UX
- [ ] Add offline indicator
