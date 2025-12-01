# quoted.it Logo Spinner Feature

## Concept

On the landing page, the logo area cycles through different "quoted.[thing]" variations before landing on the final brand name. Creates a visual demonstration of versatility while reinforcing the brand.

## Behavior

1. On page load (or scroll trigger), logo starts spinning through examples:
   - `quoted.decks`
   - `quoted.fences`
   - `quoted.roofs`
   - `quoted.paint`
   - `quoted.kitchens`
   - `quoted.patios`
   - `quoted.driveways`
   - `quoted.siding`
   - ... (more trade examples)

2. Spin slows down like a slot machine
3. Lands on `quoted.it` as the final, definitive brand

## Design Notes

- Keep the Playfair Display serif font
- The `.suffix` part stays italic (matching current logo style)
- Subtle easing - fast at start, decelerates naturally
- Maybe 1.5-2 seconds total animation
- Could trigger on scroll into view, or on page load with slight delay

## Placement Options

1. **Hero area** - Replace static logo with animated version
2. **Dedicated section** - "One tool for every trade" with the spinner as centerpiece
3. **Both** - Subtle version in nav, bigger version in a section

## Technical Approach

CSS animation with keyframes, or JS-driven text replacement with easing. Single element with text content swapping + CSS transition on opacity/transform.

## Why It Works

- Shows versatility without listing everything
- Memorable brand moment
- Reinforces that ".it" means "whatever you do"
- Differentiator - no one else does this

---

*Captured: 2025-12-01 - implement when ready*
