# Frontend Learning

**Last Updated**: 2025-12-02
**Purpose**: Accumulated knowledge about the Quoted frontend codebase

---

## Architecture

### Stack
- Vanilla HTML/CSS/JS (no framework)
- Single-page app in `frontend/index.html` (~31K tokens)
- Landing page in `frontend/landing.html`
- Mobile-first responsive design

### Design System
- Dark premium aesthetic
- Primary color: Blue (#3B82F6)
- Background: Dark grays (#111827, #1F2937)
- Font: System fonts with sans-serif fallback
- Border radius: 8px (standard), 12px (cards)

---

## Key Learnings

| Date | Learning | Context |
|------|----------|---------|
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
| `frontend/index.html` | Main app (auth, quotes, history) | ~31K tokens |
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
