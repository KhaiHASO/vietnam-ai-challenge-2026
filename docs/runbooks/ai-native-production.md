# AI-native production runbook

## Release gate

Run `powershell -ExecutionPolicy Bypass -File scripts/verify_release.ps1`. A release is blocked on any failing unit, evaluation, frontend type/build, lint, format, or Compose configuration gate.

Before running Compose, copy `.env.example` to `.env` and replace every placeholder. `BOOTSTRAP_ADMIN_*` is optional as a pair; when supplied, it creates the first admin only on an empty database and records an audit event. Never commit `.env`.

Start the production topology with `docker compose up --build -d`, then verify `docker compose ps`, `curl http://localhost/health/live`, and an authenticated Copilot request. MongoDB, Redis, ChromaDB, the backend, worker, and frontend are internal-only; Nginx is the sole public service.

Run `powershell -ExecutionPolicy Bypass -File scripts/backup.ps1` before a release and retain the created directory as an immutable artifact. Test a backup with `powershell -ExecutionPolicy Bypass -File scripts/restore_verify.ps1 -BackupDirectory <path>`; it restores into an isolated Compose project and removes only that temporary project's volumes after readiness and retrieval checks.

## Safety invariants

- Memory is contextual only; it is never evidence.
- An unavailable provider, missing evidence, invalid citation, or exhausted retry must return typed abstention.
- Refresh tokens are HttpOnly cookies. Do not inspect, log, or persist raw tokens.
- Traces hold redacted metadata only: no raw prompts, secrets, or chain-of-thought.
- In production, unavailable MongoDB or Redis aborts startup. The application must never silently downgrade Copilot memory/cache or request limiting to an in-process store.

## Frontend migration boundary

`npm run lint` validates the maintained application surface: Focus Canvas, auth, product routes, shared feature code, and tests. The inherited Velzon demo routes/components are explicitly excluded until they are removed or migrated; they are not a production quality signal. `npm run type-check` still compiles the complete repository, including that legacy surface.

The full Next.js production build compiles every legacy template route. On constrained developer machines it may exceed the local command timeout; run the release script in CI or Docker before shipping and treat a timeout as an incomplete release gate, not as a passing build.

## Incident response

If validator or provider health degrades, keep write actions behind approval, invalidate affected version-scoped cache keys, and route users to abstention/expert handoff. Preserve the trace ID and dependency health state for diagnosis.
