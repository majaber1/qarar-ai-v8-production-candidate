# Baseline before accelerator review

- Local path: `C:\Users\ADMIN\Desktop\Projects\qarar-ai-v8-production-candidate`
- Repository: `https://github.com/majaber1/qarar-ai-v8-production-candidate`
- Branch: `main`
- Local SHA: `fcaf1eead6ed042e6f48a50d3136971eae47eb2b`
- GitHub SHA after `git fetch --all --prune`: `fcaf1eead6ed042e6f48a50d3136971eae47eb2b`
- Sync status: **IDENTICAL** at baseline
- Version: `8.2.0-beta.1` (frontend package)
- Build: PASS (`npm run typecheck`; `npm run build`)
- Tests: PASS, 60 backend tests under declared Pydantic `>=2.12`
- Deployment URL: `https://qarar-ai-v8-production-candidate-5365ygyp2-20262031.vercel.app` (documented; external reachability still requires confirmation)
- Blockers: production backend/database/object-storage credentials and deployed end-to-end path were not available locally.
