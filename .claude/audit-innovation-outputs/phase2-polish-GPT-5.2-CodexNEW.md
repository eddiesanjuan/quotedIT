# Phase 2: UX and Polish Audit - GPT-5.2-CodexNEW

## 2A Mobile Experience
- Mobile navigation omits Help and Sign Out, and the desktop nav is hidden on mobile, so support paths are effectively buried. Evidence: frontend/index.html:2589, frontend/index.html:5813. Fix: add Help/Support and Sign Out to the mobile nav or surface them in Account.
- Account tabs turn into hidden horizontal scroll with no visual affordance, reducing discoverability of settings on small screens. Evidence: frontend/index.html:2615. Fix: add a fade gradient + chevron or explicit "More" control.
- Long onboarding industry list has no search/filter; on mobile it is heavy to scroll and increases drop-off. Evidence: frontend/index.html:8942. Fix: add search and typeahead filtering.

## 2B Copy and Messaging
- Pricing FAQ still references a legacy Starter plan (30 quotes/month) that no longer exists, which conflicts with the single-tier unlimited model. Evidence: frontend/help.html:560. Fix: update plan language and remove legacy limits.
- "Email Direct (coming soon)" is outdated because share-by-email is already implemented. Evidence: frontend/help.html:621, backend/api/share.py:101. Fix: update copy to match current feature state.
- Email templates link to quoted.it while app and config use quoted.it.com, causing brand and URL inconsistencies. Evidence: backend/services/email.py:205, backend/config.py:26. Fix: use a single canonical domain.

## 2C Loading and Feedback States
- Share email uses blocking alert() popups instead of the app's toast system, creating inconsistent UX and poor mobile flow. Evidence: frontend/index.html:14467. Fix: replace alerts with showSuccess/showError.
- Share link generation failures only log to console; the user gets no inline error or retry CTA. Evidence: frontend/index.html:14421. Fix: show an inline error and disable the copy button until a link exists.

## 2D Empty and Error States
- Customer quotes empty state is a single line of text with no CTA to create a quote. Evidence: frontend/index.html:12857. Fix: add a primary action and short guidance.
- Shared quote error state has no recovery action (contact, help, or return link), leaving customers stranded. Evidence: frontend/quote-view.html:928. Fix: include a contact CTA and link to the contractor or help.
