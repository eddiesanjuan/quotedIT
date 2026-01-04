# UX Excellence (Playwright) — State (GPT-5.2-Codex)

**Last Updated**: 2025-12-27

## Latest Run

- **Artifacts**: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/`
- **Report**: `reports/UX_EXCELLENCE_AUDIT_GPT52_CODEX.md`
- **Script**: `scripts/ux_audit_playwright/ux-excellence.spec.js`

## Scope

- Public pages + demo (`/`, `/try`, `/use-cases`, `/blog`, `/help`, `/for-customers`, `/terms`, `/privacy`)
- Authenticated product flows not executed (no credentials used)

## Key Findings (Top)

### P0
- Mobile tap targets below 44×44 on landing nav links and hero secondary link  
  Evidence: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-target-size-summary.json`
- Mobile horizontal overflow on landing and use-cases (page wider than viewport)  
  Evidence: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-overflow.json`  
  Evidence: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/use-cases-overflow.json`

### P1
- Landing social proof gap near hero (trust/conversion).
- `/app` transfer size ~746KB (optimize entry payload).

### P2
- Demo sharing shares `/try` URL, not the generated quote output (missed viral peak).

## How to Re-run

```bash
UX_AUDIT_RUN_ID=$(date +%F)-gpt52-codex \
UX_AUDIT_OUTPUT_DIR=reports/ux-excellence-playwright/$(date +%F)-gpt52-codex \
npx playwright test scripts/ux_audit_playwright/ux-excellence.spec.js --workers=1 --reporter=line
```

