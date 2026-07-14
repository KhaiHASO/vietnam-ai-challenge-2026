# AI Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a template-aligned AI workspace where authorized experts can ingest TXT/CSV knowledge, follow its RAG job status, and return to a domain-correct Copilot.

**Architecture:** Keep ingestion state authoritative in Mongo jobs and expose a tenant-scoped read endpoint. Add a small, typed frontend knowledge API over `authorizedFetch`; focused client components render the upload, job-detail and read-only operations views. Focus Canvas remains the AI workspace and passes the selected domain through the existing streaming API.

**Tech Stack:** FastAPI, Motor/PyMongo-style Mongo repository, Next.js 16 App Router, React 19, Tailwind CSS 4, Phosphor icons, Vitest, pytest.

## Global Constraints

- Reuse the existing Velzon shell/component conventions and Focus Canvas visual language; do not migrate legacy screens.
- Add no third-party dependencies; `@phosphor-icons/react`, `framer-motion`, Tailwind 4 and testing tools are already installed.
- UI accepts only `.txt` and `.csv` until binary document extraction is verified end to end.
- Memory is never presented as a source of truth; dashboard metrics must not be invented.
- Every API job lookup is scoped by `principal.tenant_id` and exposes no storage path or raw payload.
- Do not stage, commit or discard unrelated dirty-worktree changes.

---

### Task 1: Tenant-scoped ingestion status API

**Files:**
- Modify: `backend/app/workers/main.py`
- Modify: `backend/app/knowledge/routes.py`
- Modify: `backend/app/knowledge/service.py`
- Modify: `backend/tests/knowledge/test_ingestion_routes.py`

**Interfaces:**
- Produces `MongoJobRepository.get_for_tenant(job_id: str, tenant_id: str) -> Job | None`.
- Produces `GET /api/v1/knowledge/ingestions/{job_id}` with response keys `job_id`, `status`, `attempts`, `last_error`.

- [ ] **Step 1: Write the failing route test**

```python
class FakeIngestionService:
    async def get_status(self, *, job_id: str, principal: Principal) -> dict[str, object] | None:
        return {"job_id": job_id, "status": "completed", "attempts": 1, "last_error": None}

def test_ingestion_status_is_available_only_to_authorized_tenant() -> None:
    app = create_app()
    app.dependency_overrides[get_ingestion_service] = lambda: FakeIngestionService()
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id="expert", tenant_id="t1", roles=frozenset([Role.EXPERT])
    )
    response = TestClient(app).get("/api/v1/knowledge/ingestions/job-1")
    assert response.status_code == 200
    assert response.json() == {"job_id": "job-1", "status": "completed", "attempts": 1, "last_error": None}
```

- [ ] **Step 2: Run the test to verify RED**

Run: `python -m pytest backend/tests/knowledge/test_ingestion_routes.py -k ingestion_status -q`

Expected: FAIL with `404 Not Found` because the GET route does not exist.

- [ ] **Step 3: Add minimal repository, service and route code**

```python
# backend/app/workers/main.py
async def get_for_tenant(self, job_id: str, tenant_id: str) -> Job | None:
    document = await self.collection.find_one({
        "job_id": job_id,
        "payload.tenant_id": tenant_id,
    })
    return self._job(document) if document else None

# backend/app/knowledge/service.py
async def get_status(self, *, job_id: str, principal: Principal) -> dict[str, object] | None:
    job = await self.jobs.get_for_tenant(job_id, principal.tenant_id)
    if job is None:
        return None
    return {"job_id": job.job_id, "status": job.status, "attempts": job.attempts, "last_error": job.last_error}

# backend/app/knowledge/routes.py
@router.get("/ingestions/{job_id}")
async def get_ingestion_status(
    job_id: str,
    principal: Principal = Depends(require_roles([Role.ADMIN, Role.EXPERT])),
    service: KnowledgeIngestionService = Depends(get_ingestion_service),
) -> dict[str, object]:
    result = await service.get_status(job_id=job_id, principal=principal)
    if result is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return result
```

- [ ] **Step 4: Run the focused backend test to verify GREEN**

Run: `python -m pytest backend/tests/knowledge/test_ingestion_routes.py -q`

Expected: PASS, including the new authorized lookup test.

### Task 2: Typed browser client for ingestion

**Files:**
- Create: `frontend/src/features/knowledge/knowledge-api.ts`
- Create: `frontend/src/features/knowledge/__tests__/knowledge-api.test.ts`

**Interfaces:**
- Produces `uploadKnowledgeDocument(authorizedFetch, { file, domainId })`.
- Produces `getKnowledgeIngestion(authorizedFetch, jobId)`.
- Both return `KnowledgeIngestion` with `job_id`, `status`, `attempts`, `last_error`.

- [ ] **Step 1: Write failing API tests**

```ts
test("submits a selected document as multipart without forcing Content-Type", async () => {
  const authorizedFetch = vi.fn().mockResolvedValue(jsonResponse({ job_id: "job-1", status: "queued" }, 202));
  const file = new File(["VietGAP"], "policy.txt", { type: "text/plain" });
  await uploadKnowledgeDocument(authorizedFetch, { file, domainId: "agriculture" });
  const [, init] = authorizedFetch.mock.calls[0];
  expect(init.headers).toBeUndefined();
  expect((init.body as FormData).get("domain_id")).toBe("agriculture");
  expect((init.body as FormData).get("file")).toBe(file);
});
```

- [ ] **Step 2: Run the test to verify RED**

Run: `npx vitest run src/features/knowledge/__tests__/knowledge-api.test.ts`

Expected: FAIL with module-not-found for `knowledge-api`.

- [ ] **Step 3: Implement only the typed request helpers**

```ts
export async function uploadKnowledgeDocument(
  authorizedFetch: AuthorizedFetch,
  input: UploadKnowledgeInput
): Promise<KnowledgeIngestion> {
  const body = new FormData();
  body.set("file", input.file);
  body.set("domain_id", input.domainId);
  const response = await authorizedFetch("/api/v1/knowledge/ingestions", { method: "POST", body });
  return readIngestion(response);
}
```

- [ ] **Step 4: Run the focused frontend API test to verify GREEN**

Run: `npx vitest run src/features/knowledge/__tests__/knowledge-api.test.ts`

Expected: PASS.

### Task 3: Knowledge Base and job-detail screens

**Files:**
- Create: `frontend/src/features/knowledge/knowledge-base-workspace.tsx`
- Create: `frontend/src/features/knowledge/knowledge-job-detail.tsx`
- Create: `frontend/src/features/knowledge/__tests__/knowledge-base-workspace.test.tsx`
- Create: `frontend/src/app/knowledge/page.tsx`
- Create: `frontend/src/app/knowledge/[jobId]/page.tsx`
- Modify: `frontend/src/config/product-routes.ts`

**Interfaces:**
- Consumes `useAuth().authorizedFetch`, `useAuth().hasRole`, and `KnowledgeIngestion`.
- Produces routes `/knowledge` and `/knowledge/{jobId}`.

- [ ] **Step 1: Write failing component tests**

```tsx
test("explains upload access to an operator instead of showing a broken submit control", async () => {
  renderWithOperator(<KnowledgeBaseWorkspace />);
  expect(await screen.findByText("Chỉ chuyên gia hoặc quản trị viên mới có thể nạp tri thức.")).toBeVisible();
  expect(screen.queryByRole("button", { name: "Bắt đầu index" })).not.toBeInTheDocument();
});

test("uploads a TXT document and shows the queued job", async () => {
  renderWithExpert(<KnowledgeBaseWorkspace />);
  await userEvent.upload(screen.getByLabelText("Tệp tri thức"), new File(["VietGAP"], "policy.txt"));
  await userEvent.click(screen.getByRole("button", { name: "Bắt đầu index" }));
  expect(await screen.findByText("Đang chờ worker index")).toBeVisible();
});
```

- [ ] **Step 2: Run the screen tests to verify RED**

Run: `npx vitest run src/features/knowledge/__tests__/knowledge-base-workspace.test.tsx`

Expected: FAIL with module-not-found for `knowledge-base-workspace`.

- [ ] **Step 3: Implement focused client components and thin route pages**

```tsx
// component behavior
const mayIngest = hasRole("admin", "expert");
const acceptedFile = file && ["text/plain", "text/csv"].includes(file.type);
// render one upload workspace, a labeled file input, status panel and links
// poll only while status is queued/running/retrying; clear the interval on unmount
```

- [ ] **Step 4: Add product route coverage for `/knowledge`**

```ts
const PRODUCT_ROUTE_PATTERNS = [
  /^\/$/,
  /^\/(login|logout|ai-copilot|ai-operations|dashboard|profile|reminders|knowledge)\/?$/,
  /^\/knowledge\/(diseases|ipm|[^/]+)(\/|$)/,
];
```

- [ ] **Step 5: Run screen tests and route tests to verify GREEN**

Run: `npx vitest run src/features/knowledge/__tests__/knowledge-base-workspace.test.tsx src/config/__tests__/product-routes.test.ts`

Expected: PASS.

### Task 4: Template-aligned read-only AI Operations screen

**Files:**
- Create: `frontend/src/features/ai-operations/ai-operations-workspace.tsx`
- Create: `frontend/src/features/ai-operations/__tests__/ai-operations-workspace.test.tsx`
- Create: `frontend/src/app/ai-operations/page.tsx`

**Interfaces:**
- Produces `/ai-operations`, a static/read-only capability statement.
- Does not call an unimplemented observability endpoint or fabricate metrics.

- [ ] **Step 1: Write a failing render test**

```tsx
test("shows verified controls and an honest unavailable-observability state", () => {
  render(<AiOperationsWorkspace />);
  expect(screen.getByRole("heading", { name: "AI Operations" })).toBeVisible();
  expect(screen.getByText("Không có số liệu vận hành trực tiếp trong phiên này.")).toBeVisible();
  expect(screen.getByText("Memory không phải bằng chứng chuyên môn")).toBeVisible();
});
```

- [ ] **Step 2: Run the test to verify RED**

Run: `npx vitest run src/features/ai-operations/__tests__/ai-operations-workspace.test.tsx`

Expected: FAIL with module-not-found for `ai-operations-workspace`.

- [ ] **Step 3: Implement the static, accessible operations workspace**

```tsx
// Use existing Phosphor icons and Tailwind surface tokens.
// Render verified policy controls, typed abstention behavior and an explicit
// "no live metrics" empty state. Do not render fake counts or charts.
```

- [ ] **Step 4: Run the render test to verify GREEN**

Run: `npx vitest run src/features/ai-operations/__tests__/ai-operations-workspace.test.tsx`

Expected: PASS.

### Task 5: Focus Canvas navigation and domain propagation

**Files:**
- Modify: `frontend/src/features/copilot/copilot-api.ts`
- Modify: `frontend/src/features/copilot/focus-canvas.tsx`
- Modify: `frontend/src/features/copilot/__tests__/copilot-api.test.ts`
- Modify: `frontend/src/features/copilot/__tests__/focus-canvas.test.tsx`

**Interfaces:**
- Extends `StreamCopilotMessageOptions` with `domainId: string`.
- Sends JSON body key `domain_id`.
- Produces links to `/knowledge` and `/ai-operations` from Focus Canvas.

- [ ] **Step 1: Add the desired domain assertion to the API test**

```ts
expect(JSON.parse(fetchImpl.mock.calls[0][1].body)).toEqual({
  query: "Đạo ôn?",
  expected_conversation_revision: 2,
  domain_id: "agriculture",
});
```

- [ ] **Step 2: Run the test to verify RED**

Run: `npx vitest run src/features/copilot/__tests__/copilot-api.test.ts`

Expected: FAIL because the stream body does not include `domain_id`.

- [ ] **Step 3: Implement minimal propagation and navigation**

```tsx
// copilot-api.ts body
{ query: options.query, expected_conversation_revision: options.expectedRevision, domain_id: options.domainId }

// focus-canvas.tsx send call
await send({
  sessionId,
  accessToken,
  idempotencyKey: crypto.randomUUID(),
  expectedRevision: state.conversationRevision,
  query: cleanQuery,
  domainId: domain,
});

// retain only the configured agriculture domain and add semantic Link actions.
```

- [ ] **Step 4: Run Focus Canvas and API tests to verify GREEN**

Run: `npx vitest run src/features/copilot/__tests__/copilot-api.test.ts src/features/copilot/__tests__/focus-canvas.test.tsx`

Expected: PASS.

### Task 6: Formatting and verification

**Files:**
- Modify: `README.md` only if the current run guide omits the new Knowledge Base path.

- [ ] **Step 1: Run targeted automated checks**

Run: `npx vitest run src/features/knowledge src/features/ai-operations src/features/copilot/__tests__/copilot-api.test.ts src/features/copilot/__tests__/focus-canvas.test.tsx`

Expected: PASS with zero failing tests.

- [ ] **Step 2: Run static checks**

Run: `npm run type-check && npm run lint && npm run format:check`

Expected: all commands exit 0.

- [ ] **Step 3: Run backend test and diff check**

Run: `python -m pytest backend/tests/knowledge/test_ingestion_routes.py -q; git diff --check -- backend/app/knowledge backend/app/workers frontend/src docs/superpowers README.md`

Expected: focused backend test passes and no whitespace errors in files changed by this plan.

- [ ] **Step 4: Report limits honestly**

Document Docker/browser smoke-test availability. Do not claim end-to-end upload/indexing verification without a live Docker daemon, worker and browser access.
