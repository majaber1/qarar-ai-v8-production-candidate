# Bilingual UX Production-Hardening Release Report

## Summary

This release preserves Qarar's decision lifecycle and backend contracts while completing key Arabic/English parity, responsive navigation, accessibility, and operational-state improvements. It adapts formal dashboard and shadcn composition principles to the existing CSS/React system rather than importing demo pages or sample data.

## UX and design improvements

- Accessible collapsible mobile navigation, active-route semantics, keyboard skip link, and visible focus rings.
- Centralized Arabic/English labels for backend statuses and urgency levels.
- Locale-aware dates and explicit LTR islands for identifiers, costs, tokens, and percentages.
- Complete bilingual cost studio and live decision-run experience.
- Localized case-detail workflow headings, clarification, approval, and footer content.
- Accessible project progress semantics and reduced-motion support.

## Functional fixes and workarounds

- Removed raw backend enums from the main work queue and portfolio cards.
- Preserved transparent offline/error states; no fake API success or sample metrics were introduced.
- Password recovery remains unimplemented because the repository has no secure reset-token/email contract. This is documented instead of represented by a dead control.
- Hosted API-backed workflows remain blocked until production infrastructure and `QARAR_BACKEND_URL` are configured.

## Verification

| Gate | Result |
|---|---|
| Backend compilation/tests | PASS — 59 tests |
| Backend cleanup | Non-failing Windows pytest temp-directory warning |
| Frontend dependency restoration | LOCAL ENVIRONMENT BLOCKED — npm restore exceeded 180 seconds after a stale dev-server lock was removed |
| Frontend type-check/build/audit | PASS — GitHub Actions frontend job, 26 seconds |
| Diff whitespace check | PASS |
| Secrets review | No credentials or environment files added |
| Hosted visual verification | PASS — Arabic and English dashboard content, navigation, offline state, and localized footer on Vercel preview |

## Before/after score

| Area | Before | After |
|---|---:|---:|
| Bilingual parity | 7/10 | 9/10 |
| Mobile navigation | 6/10 | 9/10 |
| Accessibility states | 7/10 | 9/10 |
| Operational transparency | 9/10 | 9/10 |
| Production readiness | 7/10 | 8/10, pending backend hosting |

## Local run

```powershell
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --port 8000

cd ..\frontend
npm ci
npm run typecheck
npm run build
npm run dev
```

Then open `http://localhost:3000`, switch languages from the header, and verify `/project`, `/live/{case-id}`, `/cost`, `/knowledge`, `/executive`, `/login`, and `/profile`.

## Deployment readiness

The frontend is Vercel-compatible with `frontend` as the project root. Full product readiness requires a public backend and the server-only `QARAR_BACKEND_URL`. Never expose backend API keys through `NEXT_PUBLIC_*` variables.

Feature branch: `feat/bilingual-ux-production-hardening`  
Pull request: `https://github.com/majaber1/qarar-ai-v8-production-candidate/pull/2`  
Vercel preview: `https://qarar-ai-v8-production-candidate-5365ygyp2-20262031.vercel.app`  
CI: backend, frontend, and Compose jobs passed. The branch remains a draft until review/merge.
