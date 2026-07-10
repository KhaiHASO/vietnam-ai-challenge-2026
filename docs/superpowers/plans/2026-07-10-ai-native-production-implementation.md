# AI-Native Production Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing CropDoctor platform into a production-oriented AI-native vertical release with authenticated FastAPI APIs, a defensive `ai_layer/rag` core, versioned knowledge retrieval, and a Focus Canvas Copilot.

**Architecture:** Preserve the existing modular monolith and migrate through stable facades. FastAPI owns identity, application workflows, sessions, approvals, and persistence; it may access AI only through `ai_layer.rag.service.RAGService`. The RAG package owns contracts, memory/cache, registries, validation, agentic orchestration, providers, retrieval, ingestion, evaluation, and AI observability.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, MongoDB/Motor, Redis, Chroma client/server, LangGraph, PyJWT, Argon2id, pytest; Next.js 16.1.6, React 19.2.3, TypeScript 5, Tailwind CSS v4, Framer Motion, Phosphor Icons, Vitest, Testing Library, Playwright; Docker Compose and GitHub Actions-compatible CI.

## Global Constraints

- Target one single-tenant Docker/VPS deployment first; retain `tenant_id` and `domain_id` in all state and evidence contracts.
- Roles are exactly `admin`, `expert`, and `operator`; there is no public signup.
- Access JWT lifetime is 15 minutes; opaque refresh token maximum lifetime is 7 days with rotation and reuse detection.
- FPT AI Factory is the preferred competition gateway when `FPT_AI_FACTORY_API_KEY` is configured, serving the selected DeepSeek/Qwen-class model plus embedding/rerank capabilities; direct DeepSeek is the next production provider, Ollama is a policy-controlled local fallback, and OpenAI/Gemini remain optional adapters.
- Business state is MongoDB; working memory/cache/job transport is Redis; vector search is persistent ChromaDB; source files use `ObjectStorage` with local-volume and S3-compatible adapters.
- `Memory != Evidence`; memory facts never satisfy evidence or citation requirements.
- No backend module may import ChromaDB, LangGraph, embedding providers, or provider SDKs directly; use `RAGService` only.
- No mutable global active domain. Resolve domain pack and capability versions for every request.
- Never cache errors, partial streams, PII, high-risk actions, approval-required answers, abstentions, or answers that have not passed validators.
- Agent retries and reflection are bounded. Exhaustion routes to typed abstention, never fabricated success.
- Focus Canvas uses one emerald accent, Geist sans typography, no AI-purple, no emoji, asymmetric desktop, strict single-column mobile, and distinct loading/empty/error/degraded/approval/abstain states.
- Every behavior change follows Red → Green → Refactor. No production code is written before its failing test has been observed.
- Existing RAG work is preserved behind characterization tests before replacement or deletion.

---

## File Structure Map

### Backend

```text
backend/app/
├── auth/
│   ├── contracts.py
│   ├── dependencies.py
│   ├── repository.py
│   ├── routes.py
│   ├── service.py
│   └── tokens.py
├── copilot/
│   ├── repository.py
│   ├── routes.py
│   ├── service.py
│   └── sse.py
├── approvals/routes.py
├── core/config.py
├── core/errors.py
├── core/security.py
├── middleware/request_context.py
├── storage/object_storage.py
├── storage/local_storage.py
├── workers/main.py
└── main.py
```

### AI Layer

```text
ai_layer/rag/
├── service.py
├── contracts/
│   ├── answer.py
│   ├── events.py
│   ├── memory.py
│   └── request.py
├── cache/
│   ├── backend.py
│   ├── keys.py
│   └── policy.py
├── memory/
│   ├── repository.py
│   └── service.py
├── registries/
│   ├── base.py
│   ├── catalog.py
│   └── manifests.py
├── validation/
│   ├── citations.py
│   ├── evidence.py
│   ├── input.py
│   └── pipeline.py
├── agentic/
│   ├── graph.py
│   ├── nodes.py
│   └── state.py
├── providers/gateway.py
├── retrieval/hybrid.py
├── ingestion/service.py
└── observability/trace.py
```

### Frontend

```text
frontend/src/features/
├── auth/
│   ├── AuthProvider.tsx
│   ├── auth-api.ts
│   └── auth.types.ts
└── copilot/
    ├── CopilotShell.tsx
    ├── ConversationRail.tsx
    ├── MessageList.tsx
    ├── MessageBubble.tsx
    ├── EvidencePanel.tsx
    ├── ApprovalAction.tsx
    ├── AbstentionState.tsx
    ├── CopilotComposer.tsx
    ├── copilot-api.ts
    ├── copilot-reducer.ts
    ├── copilot.types.ts
    └── useCopilotStream.ts
```

---

## Milestone A — Reproducible Foundations and Security

### Task 1: Establish the Python and frontend test gates

**Files:**
- Create: `backend/requirements.in`
- Create: `backend/requirements-dev.in`
- Create: `pytest.ini`
- Create: `backend/tests/conftest.py`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/test/harness.test.ts`
- Modify: `frontend/package.json`

**Interfaces:**
- Consumes: current FastAPI app factory and Next.js project.
- Produces: reproducible `python -m pytest` and `npm run test` harnesses. Existing compiler/lint/build debt is closed explicitly in Task 17.

- [ ] **Step 1: Write the failing backend smoke test**

```python
# backend/tests/test_app_smoke.py
from app.main import create_app


def test_application_factory_builds_the_existing_api() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert app.title == "CropDoctor AI Backend"
    assert "/health" in paths
```

- [ ] **Step 2: Run the backend test and verify RED**

Run: `python -m pytest backend/tests/test_app_smoke.py -q`

Expected: FAIL with `ModuleNotFoundError` because the test dependencies are not reproducibly installed in a clean Python environment.

- [ ] **Step 3: Add explicit dependency inputs and test configuration**

```text
# backend/requirements.in
fastapi>=0.115,<1
uvicorn[standard]>=0.30,<1
pydantic>=2.10,<3
pydantic-settings>=2.7,<3
motor>=3.6,<4
redis>=5.2,<7
chromadb>=1,<2
langgraph>=0.4,<2
openai>=1.60,<3
PyJWT[crypto]>=2.10,<3
argon2-cffi>=23.1,<26
python-multipart>=0.0.20,<1
python-dotenv>=1,<2
httpx>=0.28,<1
PyYAML>=6,<7
PyMuPDF>=1.25,<2
openpyxl>=3.1,<4
python-docx>=1.1,<2
langchain-text-splitters>=0.3,<2
numpy>=1.26,<3
requests>=2.32,<3
sentence-transformers>=3,<6
torch>=2.6,<3
torchvision>=0.21,<1
scikit-learn>=1.6,<2
pandas>=2.2,<3
Pillow>=11,<13
transformers>=4.48,<6
streamlit>=1.46,<2
matplotlib>=3.10,<4
```

```text
# backend/requirements-dev.in
-r requirements.in
pytest>=8.3,<9
pytest-asyncio>=0.25,<2
pytest-cov>=6,<8
pip-tools>=7.4,<8
```

```ini
# pytest.ini
[pytest]
pythonpath = . backend
testpaths = backend/tests tests
asyncio_mode = auto
addopts = -ra --strict-markers
```

- [ ] **Step 4: Add frontend unit-test scripts and a harness test**

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "verify:unit": "npm run test"
  }
}
```

Configure Vitest with `environment: "jsdom"`, alias `@` to `frontend/src`, and load `src/test/setup.ts` containing `import "@testing-library/jest-dom/vitest"`. Add this test so the test command has a deterministic green baseline:

```typescript
import { expect, test } from "vitest";

test("runs the frontend test harness", () => {
  expect(true).toBe(true);
});
```

- [ ] **Step 5: Install and lock dependencies**

Run:

```text
python -m pip install -r backend/requirements-dev.in
python -m piptools compile backend/requirements.in --output-file backend/requirements.txt
python -m piptools compile backend/requirements-dev.in --output-file backend/requirements-dev.txt
npm install --save-dev vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Expected: generated Python lock files, updated `frontend/package-lock.json`, and no dependency resolution error.

- [ ] **Step 6: Run the smoke test and verify GREEN**

Run:

```text
python -m pytest backend/tests/test_app_smoke.py -q
cd frontend
npm run test -- src/test/harness.test.ts
```

Expected: both commands PASS; the app factory imports in a clean environment and Vitest executes one test.

- [ ] **Step 7: Commit the harness checkpoint**

```text
git add backend/requirements.in backend/requirements-dev.in backend/requirements.txt backend/requirements-dev.txt pytest.ini backend/tests frontend/package.json frontend/package-lock.json frontend/vitest.config.ts frontend/src/test
git commit -m "test: establish reproducible backend and frontend gates"
```

### Task 2: Add production-safe settings, request context, errors, and health

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/core/errors.py`
- Create: `backend/app/middleware/request_context.py`
- Modify: `backend/app/routes/health.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/core/test_config.py`
- Test: `backend/tests/core/test_errors.py`
- Test: `backend/tests/test_app_smoke.py`

**Interfaces:**
- Produces: `Settings.validate_runtime()`, `request.state.trace_id`, `/health/live`, `/health/ready`, and error shape `{code,message,trace_id,retryable}`.

- [ ] **Step 1: Write failing config and trace tests**

```python
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_wildcard_cors_and_demo_mode() -> None:
    try:
        Settings(environment="production", cors_origins="*", demo_mode=True, jwt_secret="short")
    except ValidationError as exc:
        assert "production" in str(exc).lower()
    else:
        raise AssertionError("insecure production settings were accepted")
```

```python
def test_error_payload_contains_trace_and_retryability(client) -> None:
    response = client.get("/api/test/missing", headers={"X-Request-ID": "trace-7"})
    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "HTTP_404",
        "message": "Not Found",
        "trace_id": "trace-7",
        "retryable": False,
    }
```

```python
def test_liveness_is_public_and_typed(client) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m pytest backend/tests/core backend/tests/test_app_smoke.py -q`

Expected: FAIL because the settings validators, request context middleware, typed error fields, and split health endpoints do not exist.

- [ ] **Step 3: Implement minimal secure settings**

Use a `Literal["development", "test", "production"]` environment, `SecretStr` JWT secret, explicit `cors_origin_list`, Redis/Chroma URLs, upload limits, access/refresh TTL, and a Pydantic `model_validator(mode="after")` that rejects production wildcard CORS, `demo_mode=True`, missing/short JWT secret, and missing DeepSeek credentials when DeepSeek is required.

- [ ] **Step 4: Implement trace middleware and typed errors**

```python
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = trace_id
        return response
```

Change `error_payload()` to accept `trace_id` and `retryable`; exception handlers read `request.state.trace_id`. Mark 429 and transient 5xx errors retryable, validation/auth/policy errors non-retryable.

- [ ] **Step 5: Implement liveness/readiness**

`/health/live` returns only process health. `/health/ready` reports Mongo, Redis, Chroma, registry, and configured primary provider; unavailable required dependencies return HTTP 503 with a typed dependency list.

- [ ] **Step 6: Run tests and verify GREEN**

Run: `python -m pytest backend/tests/core backend/tests/test_app_smoke.py -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```text
git add backend/app/core backend/app/middleware backend/app/routes/health.py backend/app/main.py backend/tests
git commit -m "feat: add production settings and request tracing"
```

### Task 3: Implement authentication, refresh rotation, RBAC, and audit

**Files:**
- Create: `backend/app/auth/contracts.py`
- Create: `backend/app/auth/repository.py`
- Create: `backend/app/auth/tokens.py`
- Create: `backend/app/auth/service.py`
- Create: `backend/app/auth/dependencies.py`
- Create: `backend/app/auth/routes.py`
- Create: `backend/app/core/security.py`
- Modify: `backend/app/db/schema.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/auth/test_tokens.py`
- Test: `backend/tests/auth/test_auth_service.py`
- Test: `backend/tests/auth/test_auth_routes.py`

**Interfaces:**
- Produces: `Principal`, `Role`, `AuthService.login()`, `AuthService.rotate_refresh()`, `require_roles()`, and `/api/v1/auth/*`.

- [ ] **Step 1: Write failing token and reuse-detection tests**

```python
def test_access_token_round_trip(token_service, principal) -> None:
    encoded = token_service.create_access_token(principal)
    decoded = token_service.decode_access_token(encoded)
    assert decoded.user_id == principal.user_id
    assert decoded.roles == principal.roles


async def test_refresh_reuse_revokes_the_token_family(auth_service, refresh_repo, user) -> None:
    first = await auth_service.issue_session(user)
    second = await auth_service.rotate_refresh(first.refresh_token)
    await auth_service.rotate_refresh(first.refresh_token)
    assert await refresh_repo.is_family_revoked(second.family_id)
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest backend/tests/auth -q`

Expected: FAIL because auth contracts and services do not exist.

- [ ] **Step 3: Implement contracts and token service**

```python
class Role(StrEnum):
    ADMIN = "admin"
    EXPERT = "expert"
    OPERATOR = "operator"


class Principal(BaseModel):
    user_id: str
    tenant_id: str = "single"
    roles: frozenset[Role]
```

Use Argon2id for password hashing. Sign access JWT with `sub`, `tenant_id`, `roles`, `jti`, `iat`, and `exp`. Generate refresh tokens with `secrets.token_urlsafe(48)` and store only SHA-256 hashes.

- [ ] **Step 4: Implement repositories and auth service**

Define protocols for user and refresh-session persistence, plus Mongo implementations. Rotation marks the previous token consumed and inserts the next token in one family. A second use of a consumed token revokes every active token in that family and emits an audit event.

- [ ] **Step 5: Implement routes and role dependencies**

Routes:

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
POST /api/v1/admin/users
PATCH /api/v1/admin/users/{user_id}/status
```

Return access token in JSON. Set refresh token in `HttpOnly; Secure; SameSite=Strict` cookie in production. Admin user routes require `Role.ADMIN`.

- [ ] **Step 6: Add Mongo schemas and indexes**

Add `users`, `refresh_sessions`, and `audit_events`; unique indexes on normalized username/email and refresh token hash; TTL index on refresh expiry; query indexes on family/user/audit timestamp.

- [ ] **Step 7: Run tests and verify GREEN**

Run: `python -m pytest backend/tests/auth -q`

Expected: PASS, including expired token, wrong password, disabled user, role denial, rotation, and reuse tests.

- [ ] **Step 8: Commit**

```text
git add backend/app/auth backend/app/core/security.py backend/app/db/schema.py backend/app/main.py backend/tests/auth
git commit -m "feat: add rotating authentication and RBAC"
```

---

## Milestone B — Defensive AI Core

### Task 4: Define RAG request, answer, citation, abstention, and event contracts

**Files:**
- Create: `ai_layer/rag/contracts/__init__.py`
- Create: `ai_layer/rag/contracts/request.py`
- Create: `ai_layer/rag/contracts/answer.py`
- Create: `ai_layer/rag/contracts/events.py`
- Create: `ai_layer/rag/contracts/memory.py`
- Test: `tests/ai_layer/rag/contracts/test_contracts.py`

**Interfaces:**
- Produces: `CopilotRequest`, `Evidence`, `Citation`, `ModelSignal`, `VersionSet`, `CopilotAnswer`, `Abstention`, `CopilotEvent`.

- [ ] **Step 1: Write failing invariant tests**

```python
from pydantic import ValidationError

from ai_layer.rag.contracts import AnswerStatus, CopilotAnswer, CopilotRequest


def test_request_rejects_blank_query() -> None:
    with pytest.raises(ValidationError):
        CopilotRequest(
            session_id="s1", user_id="u1", tenant_id="single",
            domain_id="agriculture", query="   ",
            expected_conversation_revision=0, idempotency_key="k1",
        )


def test_abstained_answer_requires_abstention_and_no_answer() -> None:
    with pytest.raises(ValidationError):
        CopilotAnswer(status=AnswerStatus.ABSTAINED, answer="guessed")
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/contracts -q`

Expected: FAIL because the contracts package does not exist.

- [ ] **Step 3: Implement strict contracts**

Use `extra="forbid"` on external contracts. `AnswerStatus` values are exactly `answered`, `abstained`, `approval_required`, `error`. `AbstentionCode` values are exactly the six codes in the design spec. Enforce answer/status invariants in model validators. `confidence_band` is an enum, not a free-form float.

Keep `validators_passed: bool` as an internal `Field(exclude=True)` on the assured answer model so cache policy can enforce it without leaking implementation detail onto the public wire contract.

- [ ] **Step 4: Implement version and provenance fields**

`VersionSet` includes `domain_pack`, `knowledge_index`, `prompt`, `policy`, `provider_model`, and `validator_bundle`. `Evidence` includes chunk/document/source/checksum, tenant/domain/index scope, score, content, page/section, and source title. `Citation` may only reference an evidence `chunk_id` later verified by the assurance pipeline.

`ModelSignal` carries typed non-evidence signals such as PyTorch `risk_level`, `priority`, `requires_review`, confidence, model version, latency, and engine status. It is displayed/audited separately and never inserted into citations.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/contracts -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```text
git add ai_layer/rag/contracts tests/ai_layer/rag/contracts
git commit -m "feat: define typed RAG boundary contracts"
```

### Task 5: Replace mutable capability globals with fail-fast registries

**Files:**
- Create: `ai_layer/rag/registries/manifests.py`
- Create: `ai_layer/rag/registries/base.py`
- Create: `ai_layer/rag/registries/catalog.py`
- Modify: `ai_layer/rag/registries/__init__.py`
- Modify: `ai_layer/rag/registries/capability_registry.py`
- Modify: `ai_layer/config.py`
- Create: `domains/agriculture/domain.yaml`
- Test: `tests/ai_layer/rag/registries/test_registry.py`
- Test: `tests/ai_layer/rag/registries/test_domain_catalog.py`

**Interfaces:**
- Produces: immutable `Registry[T]`, `CapabilityManifest`, `DomainManifest`, and `RegistryCatalog.resolve_request_context()`.

- [ ] **Step 1: Write failing duplicate/freeze/domain tests**

```python
def test_registry_rejects_duplicate_id_and_version() -> None:
    registry = Registry[object]("provider")
    registry.register(manifest("deepseek", "1"), object())
    with pytest.raises(DuplicateRegistrationError):
        registry.register(manifest("deepseek", "1"), object())


def test_registry_cannot_mutate_after_freeze() -> None:
    registry = Registry[object]("provider")
    registry.freeze()
    with pytest.raises(FrozenRegistryError):
        registry.register(manifest("ollama", "1"), object())
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/registries -q`

Expected: FAIL because typed registries are absent.

- [ ] **Step 3: Implement generic registry and manifests**

Each registration has `id`, `version`, `capabilities`, `supported_domains`, `config_schema`, `risk_class`, and a healthcheck. `freeze()` validates duplicates, references, health requirements, and schema compatibility before exposing an immutable mapping.

- [ ] **Step 4: Implement per-request domain resolution**

`RegistryCatalog.resolve_request_context(domain_id, tenant_id)` returns immutable versions and selected adapters. Remove import-time `load_capabilities()` side effects; keep the old function as a deprecation shim that delegates to the catalog without mutating global active state.

Remove `ACTIVE_DOMAIN` and `domain_dir` derivation from `AISettings`. Replace them with immutable `domains_root`; callers must pass `domain_id` into catalog resolution and storage/index path builders.

- [ ] **Step 5: Add agriculture domain manifest**

The manifest declares version `1.0.0`, Vietnamese locale, prompt/policy/validator bundle versions, allowed memory fact fields, retrieval thresholds, provider order, max reflect count `2`, and tool risk classes.

- [ ] **Step 6: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/registries -q`

Expected: PASS, including missing capability, incompatible version, unhealthy required provider, and no global active-domain leakage.

- [ ] **Step 7: Commit**

```text
git add ai_layer/config.py ai_layer/rag/registries domains/agriculture/domain.yaml tests/ai_layer/rag/registries
git commit -m "feat: add immutable AI capability registries"
```

### Task 6: Implement scoped conversation memory and poison-resistant fact memory

**Files:**
- Create: `ai_layer/rag/memory/repository.py`
- Create: `ai_layer/rag/memory/service.py`
- Modify: `ai_layer/rag/memory/__init__.py`
- Deprecate: `ai_layer/rag/memory/database.py`
- Test: `tests/ai_layer/rag/memory/test_memory_service.py`
- Test: `tests/ai_layer/rag/memory/test_memory_isolation.py`

**Interfaces:**
- Produces: `MemoryRepository`, `MemoryService.load_context()`, `MemoryService.propose_fact()`, `MemoryService.confirm_fact()`, `MemoryContext`.

- [ ] **Step 1: Write failing scope and poisoning tests**

```python
async def test_memory_never_crosses_user_scope(memory_service) -> None:
    await memory_service.append_turn(scope("user-a"), user_turn("Ruộng của tôi ở Đồng Tháp"))
    context = await memory_service.load_context(scope("user-b"))
    assert context.recent_turns == []


async def test_retrieved_document_cannot_write_user_fact(memory_service) -> None:
    proposal = await memory_service.propose_fact(
        scope("user-a"), key="farm_location", value="Đồng Tháp",
        source_type="retrieved_document", source_id="chunk-7",
    )
    assert proposal.status == "rejected"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/memory -q`

Expected: FAIL because scoped memory service does not exist.

- [ ] **Step 3: Implement repository protocol and in-memory test adapter**

Repository keys include tenant, user, session, domain, and conversation revision. Operations are append event, fetch recent turns, get/set rolling summary, list facts, propose fact, confirm fact, supersede fact, and forget facts.

- [ ] **Step 4: Implement memory policy**

Only explicit user messages may propose facts. Keys must be in the domain allowlist. Every fact stores source message, trust level, consent, created/expiry timestamps, and status. Sensitive/action-affecting facts remain `pending_confirmation` until explicit confirmation. Memory context exposes facts separately from evidence.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/memory -q`

Expected: PASS for isolation, expiry, confirmation, supersede, forget, allowlist, and retrieved-content poisoning cases.

- [ ] **Step 6: Commit**

```text
git add ai_layer/rag/memory tests/ai_layer/rag/memory
git commit -m "feat: add scoped and poison-resistant RAG memory"
```

### Task 7: Implement versioned cache keys, eligibility policy, and Redis adapter

**Files:**
- Create: `ai_layer/rag/cache/backend.py`
- Create: `ai_layer/rag/cache/keys.py`
- Create: `ai_layer/rag/cache/policy.py`
- Create: `ai_layer/rag/cache/__init__.py`
- Test: `tests/ai_layer/rag/cache/test_cache_keys.py`
- Test: `tests/ai_layer/rag/cache/test_cache_policy.py`

**Interfaces:**
- Produces: `CacheBackend`, `InMemoryCacheBackend`, `RedisCacheBackend`, `build_response_cache_key()`, `ResponseCachePolicy`.

- [ ] **Step 1: Write failing version and eligibility tests**

```python
def test_prompt_version_changes_response_cache_key(cache_input) -> None:
    original = build_response_cache_key(cache_input)
    changed = build_response_cache_key(cache_input.model_copy(update={"prompt_version": "p2"}))
    assert original != changed


@pytest.mark.parametrize("reason", ["pii", "high_risk", "approval", "abstained", "unvalidated"])
def test_unsafe_answers_are_not_cacheable(cache_policy, answer_for_reason, reason) -> None:
    assert cache_policy.is_eligible(answer_for_reason(reason)) is False
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/cache -q`

Expected: FAIL because cache package does not exist.

- [ ] **Step 3: Implement deterministic keys**

Canonicalize Unicode/query whitespace, hash normalized query, and include tenant scope, domain pack, index, prompt, policy, provider model, validator bundle, and stateless/session+conversation revision marker. Never place raw query or user PII in Redis keys.

- [ ] **Step 4: Implement cache policy and adapters**

Eligibility requires `status=answered`, completed stream, no PII, no high-risk/approval action, `validators_passed=True`, and public-stateless or exact session revision scope. Redis values include schema version and expiry; decoding failure is a miss and emits an invalidation metric.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/cache -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```text
git add ai_layer/rag/cache tests/ai_layer/rag/cache
git commit -m "feat: add versioned safe RAG caching"
```

### Task 8: Build deterministic assurance validators and typed abstention

**Files:**
- Create: `ai_layer/rag/validation/input.py`
- Create: `ai_layer/rag/validation/evidence.py`
- Create: `ai_layer/rag/validation/citations.py`
- Create: `ai_layer/rag/validation/pipeline.py`
- Create: `ai_layer/rag/validation/__init__.py`
- Test: `tests/ai_layer/rag/validation/test_input.py`
- Test: `tests/ai_layer/rag/validation/test_evidence.py`
- Test: `tests/ai_layer/rag/validation/test_citations.py`

**Interfaces:**
- Produces: `ValidationResult`, `InputValidator`, `EvidenceValidator`, `CitationValidator`, `AssurancePipeline`.

- [ ] **Step 1: Write failing evidence and citation tests**

```python
def test_memory_fact_does_not_make_empty_evidence_sufficient(evidence_validator, request) -> None:
    result = evidence_validator.validate(request=request, evidence=[], memory_facts=["crop=rice"])
    assert result.passed is False
    assert result.code == "INSUFFICIENT_EVIDENCE"


def test_citation_from_another_tenant_is_rejected(citation_validator, answer, evidence) -> None:
    foreign = evidence.model_copy(update={"tenant_id": "other"})
    result = citation_validator.validate(answer, [foreign], tenant_id="single", domain_id="agriculture")
    assert result.passed is False
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/validation -q`

Expected: FAIL because validators do not exist.

- [ ] **Step 3: Implement Tier-0 validators**

Input validation covers length, PII classification, injection patterns, and normalized query. Evidence validation covers tenant/domain/index scope, minimum score, active status, checksum, source diversity, freshness, and contradiction flags. Citation validation covers chunk existence, source span, scope, citation uniqueness, and factual claim coverage.

- [ ] **Step 4: Implement pipeline outcomes**

`AssurancePipeline` returns pass, retryable repair, retrieval rewrite, policy approval, or typed abstention. It never throws normal quality failures as infrastructure errors. Tier-1/2 graders are injected optional adapters and run only for ambiguous/high-risk cases.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/validation -q`

Expected: PASS for empty, weak, cross-scope, stale, contradictory, unsupported claim, prompt injection, and valid evidence cases.

- [ ] **Step 6: Commit**

```text
git add ai_layer/rag/validation tests/ai_layer/rag/validation
git commit -m "feat: add RAG assurance and abstention gates"
```

### Task 9: Implement provider gateway, bounded agentic runner, and RAGService facade

**Files:**
- Create: `ai_layer/rag/providers/gateway.py`
- Create: `ai_layer/rag/providers/fpt_ai_factory.py`
- Create: `ai_layer/rag/embeddings/fpt_ai_factory.py`
- Create: `ai_layer/rag/rerankers/fpt_ai_factory.py`
- Create: `ai_layer/rag/tools/pytorch_triage.py`
- Rewrite: `ai_layer/rag/agentic/state.py`
- Rewrite: `ai_layer/rag/agentic/nodes.py`
- Rewrite: `ai_layer/rag/agentic/graph.py`
- Create: `ai_layer/rag/service.py`
- Modify: `ai_layer/rag/core/dependencies.py`
- Modify: `ai_layer/rag/app_context.py`
- Test: `tests/ai_layer/rag/test_service.py`
- Test: `tests/ai_layer/rag/agentic/test_graph.py`
- Test: `tests/ai_layer/rag/providers/test_gateway.py`
- Test: `tests/ai_layer/rag/providers/test_fpt_ai_factory.py`
- Test: `tests/ai_layer/rag/tools/test_pytorch_triage.py`

**Interfaces:**
- Produces: `ProviderGateway.generate()`, `AgenticRAGRunner.run()`, `RAGService.ask()`, `RAGService.stream()`, `RAGService.ingest()`.

- [ ] **Step 1: Write failing facade behavior tests**

```python
async def test_service_abstains_when_retrieval_remains_insufficient(rag_service, request) -> None:
    answer = await rag_service.ask(request)
    assert answer.status == "abstained"
    assert answer.abstention.code == "INSUFFICIENT_EVIDENCE"
    assert rag_service.generator.calls == 0


async def test_memory_cannot_bypass_retrieval(rag_service, request, memory_with_domain_fact) -> None:
    answer = await rag_service.ask(request)
    assert answer.status == "abstained"
    assert answer.citations == []


async def test_only_validated_answer_is_written_to_cache(rag_service, request) -> None:
    answer = await rag_service.ask(request)
    assert answer.status == "answered"
    assert rag_service.cache.write_count == 1
    assert answer.validators_passed is True
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/test_service.py tests/ai_layer/rag/agentic tests/ai_layer/rag/providers -q`

Expected: FAIL because the facade and bounded runner do not exist.

- [ ] **Step 3: Implement provider gateway**

Use an OpenAI-compatible async adapter for DeepSeek/OpenAI/Ollama-compatible endpoints. Provider exceptions remain exceptions, never returned as answer text. Gateway enforces capability/risk policy, timeout, bounded transient retry, circuit state, and explicit `degraded` metadata. High-risk calls may not fall back to a weaker provider unless the domain policy permits it.

Add a server-only FPT AI Factory adapter using Bearer authentication and configured model IDs. Register independent chat, embedding, and rerank capabilities so RAG can prove more than a single chat API call. Never serialize the key, include it in cache keys, or expose it through `NEXT_PUBLIC_*`. Trace only provider name, model/version, token counts, latency, cache savings, status code class, and request ID.

Wrap `ai_layer.pytorch_engine.inference.predict_triage` as a typed `pytorch_triage` capability. Its `ModelSignal` affects route class, action risk, queue priority, and HITL requirement; heuristic fallback must set `engine_status="fallback"` and cannot be presented as a PyTorch prediction.

- [ ] **Step 4: Implement typed agent state and bounded graph**

State includes request, memory context, route class, evidence, rewrite/reflect counts, generated draft, validation verdicts, versions, degraded state, and trace ID. Fast path skips planner/reflect but retains all safety/evidence/citation/output gates. Standard path permits one repair; complex path permits maximum two reflect/retrieve loops.

- [ ] **Step 5: Implement RAGService orchestration**

Order: validate input → resolve registries → load scoped memory/cache candidate → obtain PyTorch triage signal → route → retrieve/agent loop → evidence gate → structured generate → citation/claim gate → action policy using the triage signal → cache eligibility → append memory/conversation event → answer. `stream()` emits typed lifecycle/model-signal events and token deltas only after safe draft validation; it never emits chain-of-thought.

- [ ] **Step 6: Keep compatibility shims**

`app_context` and old dependency functions delegate to the catalog/facade with deprecation warnings. Do not delete `knowledge_base.py`, `vector_db.py`, or current graph until characterization and parity tests pass.

- [ ] **Step 7: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag -q`

Expected: PASS for fast/standard/complex route, retry bounds, provider failure, degraded policy, cache hit/miss, insufficient evidence, unsupported citation, and memory isolation.

- [ ] **Step 8: Commit**

```text
git add ai_layer/rag tests/ai_layer/rag
git commit -m "feat: expose defensive agentic RAG service"
```

---

## Milestone C — Versioned Knowledge and Copilot API

### Task 10: Implement versioned ingestion, provenance, and hybrid retrieval

**Files:**
- Rewrite: `ai_layer/rag/models.py`
- Fix: `ai_layer/rag/chunkers/langchain_chunker.py`
- Modify: `ai_layer/rag/vectorstores/chroma_store.py`
- Create: `ai_layer/rag/retrieval/lexical.py`
- Create: `ai_layer/rag/retrieval/hybrid.py`
- Create: `ai_layer/rag/ingestion/service.py`
- Create: `backend/app/storage/object_storage.py`
- Create: `backend/app/storage/local_storage.py`
- Test: `tests/ai_layer/rag/ingestion/test_ingestion.py`
- Test: `tests/ai_layer/rag/retrieval/test_hybrid.py`
- Test: `backend/tests/storage/test_local_storage.py`

**Interfaces:**
- Produces: canonical `Chunk`, `IngestionService.ingest()`, `HybridRetriever.retrieve()`, `ObjectStorage`.

- [ ] **Step 1: Add characterization tests for current model mismatches**

```python
def test_chunker_emits_canonical_chunk_metadata(chunker, document) -> None:
    chunk = chunker.split([document])[0]
    assert chunk.metadata.source_id == document.id
    assert chunk.metadata.chunk_index == 0
    assert chunk.metadata.extra["knowledge_item_id"] == document.knowledge_item_id


def test_chroma_round_trip_preserves_scope_and_provenance(chroma_store, scoped_chunk) -> None:
    assert chroma_store.add_chunks([scoped_chunk])
    result = chroma_store.similarity_search(scoped_chunk.embedding, filters={"tenant_id": "single"})[0]
    assert result.metadata.extra["domain_id"] == "agriculture"
    assert result.metadata.extra["index_revision"] == "idx-2"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/ingestion tests/ai_layer/rag/retrieval backend/tests/storage -q`

Expected: FAIL on the existing chunk constructor mismatch, missing scope preservation, and missing storage abstraction.

- [ ] **Step 3: Fix canonical models and Chroma adapter**

Use only `ChunkMetadataModel`; remove calls that pass nonexistent `document_id`, `knowledge_item_id`, or `chunk_index` directly to `Chunk`. Chroma uses HTTP client in production and in-memory/local test adapter under tests. Store scalar tenant/domain/document/index/checksum metadata and reconstruct it losslessly.

- [ ] **Step 4: Implement secure ObjectStorage**

Server-generated UUID paths, magic-number/MIME/size validation, streaming writes, SHA-256 checksum, no raw filename path segments, and atomic rename from quarantine to active storage. Local adapter enforces resolved paths remain inside its configured root.

- [ ] **Step 5: Implement versioned ingestion**

Checksum is idempotency key. Parse → normalize → chunk → validate metadata → embed → dense+lexical staging indexes → retrieval smoke test → atomic active-revision switch. Failure leaves previous revision active. Store parser/chunker/embedding versions and provenance.

- [ ] **Step 6: Implement hybrid retrieval**

Combine dense and persistent BM25 rankings with reciprocal-rank fusion, then versioned reranking. Apply tenant/domain/active-revision/document-status filters before evidence validation. One document contributes once to source-diversity count.

- [ ] **Step 7: Run tests and verify GREEN**

Run: `python -m pytest tests/ai_layer/rag/ingestion tests/ai_layer/rag/retrieval backend/tests/storage -q`

Expected: PASS for idempotency, partial failure, atomic revision, traversal/type spoofing, cross-tenant filter, dense+lexical fusion, and provenance round trip.

- [ ] **Step 8: Commit**

```text
git add ai_layer/rag backend/app/storage tests/ai_layer/rag backend/tests/storage
git commit -m "feat: add versioned hybrid knowledge ingestion"
```

### Task 11: Add durable Copilot sessions, idempotency, SSE resume, and RAG bridge

**Files:**
- Create: `backend/app/copilot/repository.py`
- Create: `backend/app/copilot/sse.py`
- Create: `backend/app/copilot/service.py`
- Create: `backend/app/copilot/routes.py`
- Create: `backend/app/copilot/memory_routes.py`
- Modify: `backend/app/db/schema.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/routes/chat.py`
- Modify: `backend/app/services/chat_service.py`
- Test: `backend/tests/copilot/test_service.py`
- Test: `backend/tests/copilot/test_routes.py`
- Test: `backend/tests/copilot/test_sse.py`

**Interfaces:**
- Produces: `/api/v1/copilot/sessions`, `/messages`, typed SSE, optimistic conversation revision, and compatibility `/api/chat` adapter.

- [ ] **Step 1: Write failing concurrency/idempotency/resume tests**

```python
async def test_same_idempotency_key_runs_model_once(copilot_service, request) -> None:
    first = await copilot_service.send(request)
    second = await copilot_service.send(request)
    assert first.message_id == second.message_id
    assert copilot_service.rag.calls == 1


async def test_stale_revision_is_rejected(copilot_service, request) -> None:
    await copilot_service.send(request)
    with pytest.raises(ConversationRevisionConflict):
        await copilot_service.send(request)


def test_sse_resume_starts_after_last_event(client, auth_header) -> None:
    response = client.post(
        "/api/v1/copilot/sessions/s1/messages",
        headers={**auth_header, "Idempotency-Key": "k1", "Last-Event-ID": "evt-2"},
        json={"query": "Triệu chứng đạo ôn?", "expected_conversation_revision": 0},
    )
    assert "id: evt-1\n" not in response.text
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest backend/tests/copilot -q`

Expected: FAIL because Copilot service/routes do not exist.

- [ ] **Step 3: Implement repositories and Mongo schema**

Add `copilot_sessions`, `copilot_messages`, `copilot_events`, and `idempotency_records`. Session append uses atomic compare-and-set on monotonic revision. Same key+request hash returns the same operation; same key+different hash raises `409 IDEMPOTENCY_CONFLICT`.

Expose authenticated `GET /api/v1/copilot/memory`, `PATCH /api/v1/copilot/memory/{fact_id}`, and `DELETE /api/v1/copilot/memory/{fact_id}`. Users may access only their own facts; every correction/forget operation creates an audit event and delegates to `MemoryService`.

- [ ] **Step 4: Implement service and SSE formatting**

Translate authenticated principal and request body into `CopilotRequest`; call only `RAGService`. Every event has `event_id`, sequence, message, timestamp, trace, and typed payload. Active deltas remain in Redis TTL; final answer and coarse lifecycle events persist in Mongo. Reconnect resumes or returns final snapshot without another provider call.

- [ ] **Step 5: Protect routes and bridge legacy chat**

All Copilot routes require access token. Compatibility `/api/chat` constructs a scoped request and delegates to the service; it must stop returning `success=True` with fabricated provider error text.

- [ ] **Step 6: Run tests and verify GREEN**

Run: `python -m pytest backend/tests/copilot -q`

Expected: PASS for auth denial, answered, abstained, approval, error, idempotency conflict, revision conflict, disconnect/resume, and no chain-of-thought event.

- [ ] **Step 7: Commit**

```text
git add backend/app/copilot backend/app/db/schema.py backend/app/main.py backend/app/routes/chat.py backend/app/services/chat_service.py backend/tests/copilot
git commit -m "feat: add durable streaming Copilot API"
```

### Task 12: Make HITL durable and protect all legacy API routes

**Files:**
- Create: `backend/app/approvals/routes.py`
- Create: `backend/app/approvals/service.py`
- Create: `backend/app/approvals/repository.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/routes/approvals.py`
- Modify: `backend/app/routes/domain.py`
- Modify: `backend/app/services/domain_service.py`
- Create: `backend/app/middleware/rate_limit.py`
- Test: `backend/tests/approvals/test_approval_service.py`
- Test: `backend/tests/security/test_route_protection.py`
- Test: `backend/tests/security/test_rate_limit.py`

**Interfaces:**
- Produces: durable `ApprovalService`, role-protected approve/reject, and global API authentication policy.

- [ ] **Step 1: Write failing authorization and restart tests**

```python
def test_state_changing_legacy_routes_reject_anonymous_access(client) -> None:
    for method, path in [("post", "/api/approvals/a1/approve"), ("post", "/api/domain/switch")]:
        response = getattr(client, method)(path, json={})
        assert response.status_code == 401


async def test_pending_approval_survives_service_recreation(repository, approval) -> None:
    await ApprovalService(repository).create(approval)
    loaded = await ApprovalService(repository).get(approval.approval_id)
    assert loaded.status == "pending"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest backend/tests/approvals backend/tests/security -q`

Expected: FAIL because approvals are process-local and legacy routes are open.

- [ ] **Step 3: Implement durable approvals**

Mongo approval record includes policy/risk, proposed action, evidence, requester, required roles, status, decision actor/time/reason, idempotency key, and trace. Use atomic status transition; a second decision returns conflict. Worker executes only approved records.

- [ ] **Step 4: Protect API surface**

Apply access-token authentication to every `/api/*` route except `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/health/live`, and readiness policy. Require admin/expert for approval and ingestion, admin for user/domain config, and any authenticated role for Copilot/case reads.

The compatibility domain route stops mutating process-global state: it validates/returns a requested domain selection for the caller/session only. Add Redis-backed fixed-window limits with distinct auth, Copilot, upload, and admin buckets; return typed `429` with `Retry-After`. Production fails closed when the limiter is unavailable for auth/admin mutation, while ordinary read health endpoints remain available.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest backend/tests/approvals backend/tests/security -q`

Expected: PASS, including operator denial, expert approval, concurrent double decision, anonymous legacy mutation, and audit records.

- [ ] **Step 6: Commit**

```text
git add backend/app/approvals backend/app/routes/approvals.py backend/app/routes/domain.py backend/app/services/domain_service.py backend/app/middleware/rate_limit.py backend/app/main.py backend/tests/approvals backend/tests/security
git commit -m "feat: persist HITL approvals and protect APIs"
```

---

## Milestone D — Focus Canvas

### Task 13: Install and verify the Focus Canvas UI toolchain

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/postcss.config.mjs`
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/app/layout.tsx`
- Test: `frontend/src/features/copilot/__tests__/toolchain.test.tsx`

**Interfaces:**
- Produces: Tailwind v4 utilities, Geist, Framer Motion, and `@phosphor-icons/react` available to Copilot leaf components.

- [ ] **Step 1: Write failing toolchain render test**

```tsx
import { render, screen } from "@testing-library/react";
import { Leaf } from "@phosphor-icons/react";

test("renders the approved icon system", () => {
  render(<Leaf aria-label="Nông nghiệp" size={20} weight="regular" />);
  expect(screen.getByLabelText("Nông nghiệp")).toBeVisible();
});
```

- [ ] **Step 2: Verify RED**

Run: `npm run test -- src/features/copilot/__tests__/toolchain.test.tsx`

Expected: FAIL because Phosphor Icons and frontend test toolchain are not installed/configured.

- [ ] **Step 3: Install approved UI dependencies**

Run:

```text
npm install @phosphor-icons/react framer-motion
npm install --save-dev tailwindcss @tailwindcss/postcss postcss
```

Create PostCSS config using only `@tailwindcss/postcss`; add `@import "tailwindcss";` to `globals.css`. Import Geist using `next/font/google`; set Vietnamese `<html lang="vi">`. Do not introduce Lucide, emoji, Inter, or a second accent.

- [ ] **Step 4: Run test and verify GREEN**

Run: `npm run test -- src/features/copilot/__tests__/toolchain.test.tsx`

Expected: PASS.

- [ ] **Step 5: Commit**

```text
git add frontend/package.json frontend/package-lock.json frontend/postcss.config.mjs frontend/src/app/globals.css frontend/src/app/layout.tsx frontend/src/features/copilot/__tests__/toolchain.test.tsx
git commit -m "build: add Focus Canvas UI toolchain"
```

### Task 14: Implement typed Copilot stream reducer and API client

**Files:**
- Create: `frontend/src/features/copilot/copilot.types.ts`
- Create: `frontend/src/features/copilot/copilot-reducer.ts`
- Create: `frontend/src/features/copilot/copilot-api.ts`
- Create: `frontend/src/features/copilot/useCopilotStream.ts`
- Test: `frontend/src/features/copilot/__tests__/copilot-reducer.test.ts`
- Test: `frontend/src/features/copilot/__tests__/copilot-api.test.ts`

**Interfaces:**
- Produces: `CopilotState`, `copilotReducer`, `streamCopilotMessage()`, `useCopilotStream()`.

- [ ] **Step 1: Write failing state-machine tests**

```typescript
test("turns typed abstention into a recoverable terminal state", () => {
  const state = copilotReducer(initialState, {
    type: "message.abstained",
    eventId: "evt-5",
    payload: {
      code: "INSUFFICIENT_EVIDENCE",
      user_message: "Tôi chưa có đủ nguồn đáng tin cậy để kết luận.",
      recovery_actions: ["refine_question", "ask_expert"],
    },
  });
  expect(state.phase).toBe("abstained");
  expect(state.error).toBeNull();
});


test("ignores duplicate SSE events after reconnect", () => {
  const once = copilotReducer(initialState, tokenEvent("evt-3", "Lúa"));
  const twice = copilotReducer(once, tokenEvent("evt-3", "Lúa"));
  expect(twice.draft).toBe("Lúa");
});
```

- [ ] **Step 2: Verify RED**

Run: `npm run test -- src/features/copilot/__tests__/copilot-reducer.test.ts src/features/copilot/__tests__/copilot-api.test.ts`

Expected: FAIL because typed stream modules do not exist.

- [ ] **Step 3: Implement types and pure reducer**

Model all SSE event types from the backend contract. State phases are `idle`, `connecting`, `retrieving`, `streaming`, `completed`, `abstained`, `approval`, `degraded`, and `error`. Deduplicate by event ID and maintain last sequence/event ID for resume. Raw chain-of-thought is not a type.

- [ ] **Step 4: Implement fetch-based SSE client**

POST JSON with bearer token, idempotency key, expected revision, and optional `Last-Event-ID`; parse streamed event frames, reject malformed typed payloads, reconnect once on network interruption, and reuse the same key. AbortController cleanup is mandatory on unmount/new request.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `npm run test -- src/features/copilot/__tests__/copilot-reducer.test.ts src/features/copilot/__tests__/copilot-api.test.ts`

Expected: PASS for event ordering, duplicate events, abstain, approval, malformed payload, retry, cancel, and final snapshot.

- [ ] **Step 6: Commit**

```text
git add frontend/src/features/copilot
git commit -m "feat: add typed Copilot streaming state"
```

### Task 15: Build the responsive Focus Canvas and replace the template page

**Files:**
- Create: `frontend/src/features/copilot/CopilotShell.tsx`
- Create: `frontend/src/features/copilot/ConversationRail.tsx`
- Create: `frontend/src/features/copilot/MessageList.tsx`
- Create: `frontend/src/features/copilot/MessageBubble.tsx`
- Create: `frontend/src/features/copilot/EvidencePanel.tsx`
- Create: `frontend/src/features/copilot/ApprovalAction.tsx`
- Create: `frontend/src/features/copilot/AbstentionState.tsx`
- Create: `frontend/src/features/copilot/CopilotComposer.tsx`
- Create: `frontend/src/features/copilot/MagneticSendButton.tsx`
- Delete: `frontend/src/app/(with-layout)/ai-copilot/page.tsx`
- Create: `frontend/src/app/ai-copilot/page.tsx`
- Test: `frontend/src/features/copilot/__tests__/CopilotShell.test.tsx`
- Test: `frontend/src/features/copilot/__tests__/AbstentionState.test.tsx`

**Interfaces:**
- Consumes: `useCopilotStream()` and auth access token.
- Produces: approved Focus Canvas UI with evidence and recovery workflows.

- [ ] **Step 1: Write failing interaction and accessibility tests**

```tsx
test("submits a question and exposes citation evidence", async () => {
  render(<CopilotShell client={fakeAnsweredClient()} />);
  await userEvent.type(screen.getByLabelText("Câu hỏi cho Copilot"), "Dấu hiệu đạo ôn là gì?");
  await userEvent.click(screen.getByRole("button", { name: "Gửi câu hỏi" }));
  expect(await screen.findByText("Bằng chứng tham khảo")).toBeVisible();
  expect(screen.getByRole("button", { name: /Mở nguồn/ })).toBeEnabled();
});


test("abstention offers expert handoff without presenting an error", () => {
  render(<AbstentionState abstention={insufficientEvidence} onAction={vi.fn()} />);
  expect(screen.getByText("Chưa đủ bằng chứng để kết luận")).toBeVisible();
  expect(screen.getByRole("button", { name: "Chuyển chuyên gia" })).toBeEnabled();
  expect(screen.queryByRole("alert")).not.toHaveTextContent("Lỗi");
});
```

- [ ] **Step 2: Verify RED**

Run: `npm run test -- src/features/copilot/__tests__/CopilotShell.test.tsx src/features/copilot/__tests__/AbstentionState.test.tsx`

Expected: FAIL because Focus Canvas components do not exist.

- [ ] **Step 3: Implement shell and responsive layout**

Desktop uses an asymmetric grid with a slim conversation rail, dominant message canvas, and collapsible evidence/action panel. Below `md`, render one column and move rail/evidence into accessible sheets. Use `min-h-[100dvh]`, never `h-screen`, and avoid generic equal-card grids.

- [ ] **Step 4: Implement complete UI states**

Add layout-matched skeletons, actionable empty state, inline network error, visible degraded provider badge, approval panel, and neutral abstention panel with at most three recovery actions. Preserve the composer value after error/abstain. Citation click focuses the exact source item.

Show a compact “Decision signals” disclosure for FPT provider/model latency and PyTorch risk/priority/model version. Label heuristic fallback explicitly; do not mix model signals into the evidence/citation panel.

- [ ] **Step 5: Implement restrained motion and icons**

Use only `@phosphor-icons/react`, consistent weight/stroke, no emoji. Isolate the Framer Motion magnetic send button as a client leaf using `useMotionValue`/`useTransform`; use transform/opacity only, spring `{stiffness: 100, damping: 20}`, and respect reduced motion. No outer glow, pure black, purple, or infinite parent re-renders.

- [ ] **Step 6: Replace template page**

The top-level route page becomes a small server/client boundary that renders `CopilotShell` without inheriting the template's `(with-layout)` shell. Remove the conflicting grouped route and its mixed SME/education/database/agent blueprint cockpit; operations remain in dedicated screens.

- [ ] **Step 7: Run tests and verify GREEN**

Run: `npm run test -- src/features/copilot -q`

Expected: PASS for empty/loading/streaming/answered/evidence/abstain/approval/degraded/error, keyboard submit, abort cleanup, and mobile drawer labels.

- [ ] **Step 8: Run browser visual verification**

Run: `npm run dev` and inspect `/ai-copilot` at 1440×900, 1024×768, 768×1024, and 390×844. Verify no horizontal overflow, no hidden composer, evidence focus, reduced-motion mode, and readable contrast.

- [ ] **Step 9: Commit**

```text
git add frontend/src/features/copilot frontend/src/app/ai-copilot 'frontend/src/app/(with-layout)/ai-copilot/page.tsx'
git commit -m "feat: replace Copilot template with Focus Canvas"
```

### Task 16: Implement frontend auth session and protect Focus Canvas

**Files:**
- Create: `frontend/src/features/auth/auth.types.ts`
- Create: `frontend/src/features/auth/auth-api.ts`
- Create: `frontend/src/features/auth/AuthProvider.tsx`
- Modify: `frontend/src/components/ClientProviders.tsx`
- Rewrite: `frontend/src/app/(auth)/login/page.tsx`
- Test: `frontend/src/features/auth/__tests__/AuthProvider.test.tsx`
- Test: `frontend/src/features/auth/__tests__/login.test.tsx`

**Interfaces:**
- Produces: in-memory access token, automatic single-flight refresh, authenticated fetch wrapper, and login redirect.

- [ ] **Step 1: Write failing session tests**

```tsx
test("keeps the access token out of localStorage", async () => {
  render(<AuthProvider client={successfulAuthClient()}><Probe /></AuthProvider>);
  await screen.findByText("authenticated");
  expect(localStorage.getItem("access_token")).toBeNull();
});


test("coalesces concurrent refresh requests", async () => {
  const client = expiringAuthClient();
  await Promise.all([client.authorizedFetch("/one"), client.authorizedFetch("/two")]);
  expect(client.refreshCalls).toBe(1);
});
```

- [ ] **Step 2: Verify RED**

Run: `npm run test -- src/features/auth -q`

Expected: FAIL because production auth context does not exist.

- [ ] **Step 3: Implement auth client/provider**

Store access token only in React memory. Refresh uses same-origin credentials cookie and one shared in-flight promise. On refresh reuse/401, clear principal and redirect to login. Expose role checks for UI convenience while retaining backend enforcement.

- [ ] **Step 4: Implement login UI**

No registration link. Use labeled username/password fields, inline validation/error, disabled/loading submit, keyboard flow, and concrete Vietnamese copy. Preserve one emerald accent and Geist. Do not expose whether a username exists.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `npm run test -- src/features/auth -q`

Expected: PASS for login, wrong credentials, disabled user, refresh, concurrent refresh, logout, role view, and no persistent access token.

- [ ] **Step 6: Commit**

```text
git add frontend/src/features/auth frontend/src/components/ClientProviders.tsx 'frontend/src/app/(auth)/login/page.tsx'
git commit -m "feat: add secure frontend authentication session"
```

---

### Task 17: Close frontend compiler debt and quarantine template-only routes

**Files:**
- Create: `frontend/src/lib/error-message.ts`
- Create: `frontend/src/lib/__tests__/error-message.test.ts`
- Create: `frontend/src/config/product-routes.ts`
- Create: `frontend/src/config/__tests__/product-routes.test.ts`
- Create: `frontend/proxy.ts`
- Delete: `frontend/middleware.ts`
- Modify: `frontend/src/slices/auth/authSlice.ts`
- Modify: `frontend/src/slices/users/usersSlice.ts`
- Modify: `frontend/src/slices/settings/settingsSlice.ts`
- Modify: `frontend/src/components/Dashboard/UsersByDevice.tsx`
- Modify: `frontend/src/components/Dashboard/LiveUsers.tsx`
- Modify: `frontend/src/components/DashboardBlog/DashboardBlogCharts.tsx`
- Modify: `frontend/next.config.js`
- Modify: `frontend/eslint.config.mjs`
- Modify: `frontend/.prettierignore`
- Modify: `frontend/package.json`

**Interfaces:**
- Produces: full TypeScript/build success without `ignoreBuildErrors`, ESLint CLI for Next.js 16, explicit production route allowlist, and isolated formatting gates for the maintained product surface.

- [ ] **Step 1: Capture the failing compiler gate**

Run: `npm run type-check`

Expected: FAIL with 14 diagnostics in the six listed slice/dashboard files: eight unknown-catch errors, four untyped thunk dispatch errors, and two incompatible Apex option errors.

- [ ] **Step 2: Write failing error-normalization and route tests**

```typescript
test("normalizes an unknown thrown value without unsafe property access", () => {
  expect(toErrorMessage(new Error("Mất kết nối"))).toBe("Mất kết nối");
  expect(toErrorMessage("timeout")).toBe("timeout");
  expect(toErrorMessage({ unexpected: true })).toBe("Đã xảy ra lỗi không xác định");
});


test("denies template-only routes from the production surface", () => {
  expect(isProductRoute("/ai-copilot")).toBe(true);
  expect(isProductRoute("/diagnosis/history")).toBe(true);
  expect(isProductRoute("/apps-crypto-wallet")).toBe(false);
  expect(isProductRoute("/ui/buttons")).toBe(false);
});
```

- [ ] **Step 3: Run tests and verify RED**

Run: `npm run test -- src/lib/__tests__/error-message.test.ts src/config/__tests__/product-routes.test.ts`

Expected: FAIL because the utilities do not exist.

- [ ] **Step 4: Fix the 14 compiler errors minimally**

Use `toErrorMessage(error: unknown)` in the three slices. Replace plain Redux `useDispatch()` with the existing `useAppDispatch()` hook in `UsersByDevice` and `LiveUsers`. Type chart options from `ComponentProps<typeof ReactApexChart>["options"]` and accept optional legend formatter options instead of maintaining a conflicting handwritten Apex type.

- [ ] **Step 5: Implement the production route allowlist and Next.js 16 proxy**

Allow only `/`, auth/login/logout, `/ai-copilot`, dashboard, farms, farm logs, diagnosis new/history/follow-up, expert review, knowledge diseases/IPM, cooperative map, model report, agent logs, profile, reminders, Next internals, and public assets. `proxy.ts` returns 404 for template-only application routes; it does not pretend to replace backend authorization.

- [ ] **Step 6: Enable honest frontend gates**

Remove `typescript.ignoreBuildErrors`. Change `lint` to `eslint . --max-warnings=0`; remove the Prettier-as-ESLint rule and keep formatting as its own check. `.prettierignore` excludes generated artifacts and quarantined template-only sources while explicitly re-including the maintained product routes/features/configuration.

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "type-check": "tsc --noEmit",
    "format:check": "prettier --check .",
    "verify": "npm run test && npm run type-check && npm run lint && npm run format:check && npm run build"
  }
}
```

- [ ] **Step 7: Run frontend gates and verify GREEN**

Run:

```text
npm run test
npm run type-check
npm run lint
npm run format:check
npm run build
```

Expected: every command exits 0; Next build performs type validation and template-only routes return 404 through the production proxy.

- [ ] **Step 8: Commit**

```text
git add frontend
git commit -m "fix: enforce honest frontend production gates"
```

---

## Milestone E — Runtime, Evaluation, and Release Gates

### Task 18: Add Redis/Mongo/Chroma-backed adapters, worker, and production Compose

**Files:**
- Create: `backend/app/copilot/mongo_repository.py`
- Create: `backend/app/auth/mongo_repository.py`
- Create: `backend/app/approvals/mongo_repository.py`
- Create: `backend/app/auth/bootstrap.py`
- Create: `backend/app/knowledge/service.py`
- Create: `backend/app/knowledge/routes.py`
- Create: `ai_layer/rag/memory/mongo_redis_repository.py`
- Create: `backend/app/workers/main.py`
- Create: `deploy/nginx.conf`
- Modify: `backend/Dockerfile`
- Modify: `frontend/Dockerfile`
- Rewrite: `docker-compose.yml`
- Modify: `.env.example`
- Test: `backend/tests/integration/test_adapters.py`
- Test: `backend/tests/integration/test_worker_retry.py`
- Test: `backend/tests/knowledge/test_ingestion_routes.py`
- Test: `backend/tests/auth/test_bootstrap.py`

**Interfaces:**
- Produces: production dependency wiring and `python -m app.workers.main`.

- [ ] **Step 1: Write failing adapter contract tests**

Run the same repository contract suite against in-memory adapters and container-backed Mongo/Redis/Chroma. Add a worker test proving transient failure retries within budget and permanent failure enters dead-letter state without duplicate side effects.

```python
def test_ingestion_requires_expert_and_returns_a_job(client, operator_header, expert_header, pdf_fixture) -> None:
    denied = client.post("/api/v1/knowledge/ingestions", headers=operator_header, files={"file": pdf_fixture})
    accepted = client.post("/api/v1/knowledge/ingestions", headers=expert_header, files={"file": pdf_fixture})
    assert denied.status_code == 403
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "queued"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest backend/tests/integration -q`

Expected: FAIL because production adapters/worker wiring are missing.

- [ ] **Step 3: Implement adapters**

Mongo uses majority write concern for auth/approval/session state. Redis keys are namespace/version scoped and have TTL. Chroma uses `HttpClient`/`AsyncHttpClient` against the server container and a persistent `/data` volume. Dependency wiring selects in-memory adapters only in tests.

- [ ] **Step 4: Implement worker semantics**

Jobs contain idempotency key, type, payload reference, attempts, next run, trace, and status. Acquire a Redis lease, heartbeat long jobs, retry transient errors with bounded exponential backoff+jitter, and persist dead-letter state. Ingestion activates index only after smoke validation.

Knowledge routes validate/store uploads through `ObjectStorage`, enqueue ingestion, expose job status, and require admin/expert roles. `auth.bootstrap` creates the first admin only when the users collection is empty and explicit bootstrap credentials are supplied; reruns are idempotent and audited.

- [ ] **Step 5: Rewrite production containers**

Use Node 20.9+ and Python 3.11 slim. Compose services are nginx, frontend, backend, worker, redis, mongodb, and chromadb with healthchecks, internal network, persistent volumes, `DEMO_MODE=false`, same-origin public URL, and no public Mongo/Redis/Chroma ports in production profile. Resolve and pin the Chroma image digest after pulling the official `chromadb/chroma` image; commit the digest rather than a floating tag. Nginx enforces TLS redirect, body limits, security headers, request IDs, and same-origin `/api` proxying.

- [ ] **Step 6: Run integration tests and Compose smoke; verify GREEN**

Run:

```text
docker compose config
docker compose up --build -d
python -m pytest backend/tests/integration -q
docker compose ps
```

Expected: config valid, every required service healthy, integration suite PASS, and only edge ports exposed.

- [ ] **Step 7: Commit**

```text
git add backend ai_layer/rag/memory frontend/Dockerfile deploy docker-compose.yml .env.example
git commit -m "ops: add production adapters worker and compose stack"
```

### Task 19: Add evaluation, observability, CI, and final production gates

**Files:**
- Create: `ai_layer/rag/evaluation/runner.py`
- Replace: `ai_layer/rag/evaluation/golden_dataset.json`
- Create: `ai_layer/rag/observability/trace.py`
- Create: `backend/app/observability/metrics.py`
- Create: `backend/app/observability/routes.py`
- Create: `.github/workflows/ci.yml`
- Create: `scripts/verify_release.ps1`
- Create: `scripts/backup.ps1`
- Create: `scripts/restore_verify.ps1`
- Create: `docs/runbooks/ai-native-production.md`
- Create: `docs/competition/fpt-ai-factory-integration.md`
- Create: `docs/competition/pytorch-award-evidence.md`
- Test: `tests/ai_layer/rag/evaluation/test_runner.py`
- Test: `backend/tests/observability/test_redaction.py`

**Interfaces:**
- Produces: versioned scorecard, redacted traces/metrics, CI gates, and release verification command.

- [ ] **Step 1: Write failing evaluation and redaction tests**

```python
def test_unanswerable_case_requires_abstention(evaluator, unanswerable_case) -> None:
    result = evaluator.score(unanswerable_case, answered_without_evidence())
    assert result.passed is False
    assert result.failures == ["expected_abstention"]


def test_trace_redacts_prompt_pii(trace_recorder) -> None:
    event = trace_recorder.record({"query": "Gọi tôi qua 0912345678", "token": "secret"})
    assert "0912345678" not in event.serialized
    assert "secret" not in event.serialized
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/ai_layer/rag/evaluation backend/tests/observability -q`

Expected: FAIL because the evaluator and redaction layer do not exist.

- [ ] **Step 3: Implement golden-set evaluation**

Dataset includes answerable, unanswerable, conflicting, injection, cross-scope, stale, and high-risk approval cases. Score retrieval recall@k, citation precision/support, unsupported claim rate, abstain precision/recall, policy violations, latency, and token/cost. Judge model/version is metadata only and cannot override deterministic failures.

Add an FPT AI Factory scorecard covering live-key health, chat/embedding/rerank usage, latency, token/cost, cache savings, and controlled provider fallback. Add a PyTorch ablation comparing triage against heuristic and LLM-only baselines with macro-F1, high-risk recall, calibration, p95 CPU latency, throughput, model size, `torch.compile` result where supported, ONNX parity, and the number of workflow decisions changed by the model.

- [ ] **Step 4: Implement redacted observability**

Trace spans include route, versions, cache/memory decisions, retrieval scores, validator verdicts, provider/degraded state, token/cost, and queue lifecycle. Never log chain-of-thought, secrets, raw refresh tokens, or unredacted PII.

Expose authenticated admin/expert metrics and trace summaries without raw prompt/response content. Backup script snapshots MongoDB, Chroma data, object storage, and version manifests into a timestamped directory after resolving and verifying the destination remains inside the configured backup root. Restore verification restores into isolated temporary service volumes, runs readiness and retrieval fixtures, then removes only the verified temporary volumes.

- [ ] **Step 5: Add CI and release verification**

CI jobs run Python unit/integration/security/evaluation tests, frontend test/type-check/lint/format/build, Docker build/config/smoke, dependency audit, and secret scan. `scripts/verify_release.ps1` runs the same gates locally and exits nonzero on the first failure.

- [ ] **Step 6: Run all release gates and verify GREEN**

Run:

```text
python -m pytest -q
cd frontend
npm run test
npm run type-check
npm run lint
npm run format:check
npm run build
cd ..
docker compose config
powershell -ExecutionPolicy Bypass -File scripts/verify_release.ps1
```

Expected: every command exits 0, no warnings treated as release blockers, and evaluation thresholds pass.

- [ ] **Step 7: Perform browser acceptance**

Verify login → Copilot → citation → abstain recovery → expert handoff → approval at desktop/mobile sizes. Confirm refresh behavior, reconnect without duplicate model call, no anonymous mutation, and no chain-of-thought/raw secret in browser network/log output.

- [ ] **Step 8: Commit**

```text
git add ai_layer/rag/evaluation ai_layer/rag/observability backend/app/observability .github/workflows/ci.yml scripts/verify_release.ps1 docs/runbooks tests backend/tests
git commit -m "test: enforce AI-native production release gates"
```

---

## Plan Completion Checklist

- [ ] Every production behavior was preceded by a test observed failing for the intended missing behavior.
- [ ] Every task-specific suite is green before its task commit.
- [ ] Full backend and frontend regression gates pass after every milestone.
- [ ] No unfinished implementation marker, hidden type-check bypass, demo-mode production default, wildcard production CORS, or public state-changing route remains.
- [ ] `git grep` confirms backend imports AI only through `ai_layer.rag.service` outside compatibility tests.
- [ ] Memory facts never appear in evidence/citation arrays.
- [ ] Cache invalidation changes with domain/index/prompt/policy/model/validator versions.
- [ ] Registry startup fails on broken references or required unhealthy capabilities.
- [ ] Insufficient/conflicting/unsupported answers produce typed abstention and graceful Focus Canvas recovery.
- [ ] Production Compose survives backend/worker restart without losing users, sessions, conversations, approvals, knowledge revisions, or source documents.
- [ ] Final verification uses `superpowers:verification-before-completion`, followed by `superpowers:finishing-a-development-branch`.
