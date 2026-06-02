# Plan: BE-01-02 — Projects CRUD + tus Upload Server Integration

## Plan Summary

Add Project and PdfFile ORM models, Projects CRUD API (5 endpoints), and a minimal tus-compatible upload server embedded in FastAPI. Assumes BE-01-01 (#57) has already delivered the FastAPI app factory, SQLAlchemy async database setup, auth dependencies, User model, and middleware.

## Dependency Status

**Hard dependency: Issue #57 (BE-01-01) — FastAPI skeleton + Auth + DB**

BE-01-01 must deliver before this plan can execute:
- `src/paper_image/api/app.py` — FastAPI app factory with CORS, auth middleware, error handling
- `src/paper_image/api/db/` — SQLAlchemy async engine, session factory, Base declarative model
- `src/paper_image/api/db/models.py` — User ORM model (id, email, name, role, organization_id, hashed_password)
- `src/paper_image/api/deps.py` — `get_db()` async session dependency, `get_current_user()` auth dependency
- `src/paper_image/api/routes/auth.py` — register/login/refresh/me endpoints
- `src/paper_image/api/schemas/auth.py` — Pydantic request/response schemas for auth
- `src/paper_image/api/middleware.py` — CORS, auth, error handling middleware
- Alembic setup with initial migration for User table
- `pyproject.toml` updated with fastapi, sqlalchemy, alembic, python-jose, passlib dependencies

If BE-01-01 is not yet complete, this plan is blocked at Step 1.

## Key Design Decisions

### tus Upload: Embedded FastAPI Implementation

**Decision**: Implement a minimal tus-compatible upload server directly in FastAPI rather than deploying tusd as a separate process.

**Rationale**:
- Demo phase — no need for production tusd deployment complexity
- Avoids Go binary dependency and inter-process hook communication
- The tus core protocol (POST creation, PATCH chunk upload, HEAD resume, OPTIONS discovery) is straightforward to implement
- Clear interface boundary means swapping to tusd later is a clean replacement of `routes/upload.py`

**Protocol support**:
- Creation (POST) — creates upload session with metadata
- Creation With Upload (POST + body) — creates and uploads first chunk in one request
- Chunk upload (PATCH) — append chunk to existing upload
- Resume (HEAD) — query upload offset for resume
- Concatenation not supported (not needed for single PDF upload)

### API Response Envelope

Follows the frontend spec convention: `{ code, data, message, timestamp }`.

## Steps

### Step 1: Add Project and PdfFile ORM Models + Migration

**Files**:
- `src/paper_image/api/db/models.py` — modify (add Project, PdfFile classes)

**Changes**:
- `Project` model: id (UUID), name, description, status (Enum: draft/uploading/processing/ready/completed), owner_id (FK → users), organization_id (FK → organizations, nullable), target_pdf_id (FK → pdf_files, nullable), created_at, updated_at
- `PdfFile` model: id (UUID), project_id (FK → projects), filename, file_size, role (Enum: target/reference), source (Enum: upload/pubmed), upload_progress (int 0-100), processing_status (Enum: pending/extracting/completed/failed), figure_count (nullable int), panel_count (nullable int), storage_path, sha256, uploaded_at
- `project_pdf_files` relationship: Project.pdf_files → list[PdfFile], PdfFile.project → Project
- Project cascade delete to PdfFile records
- Alembic migration: `alembic revision --autogenerate -m "add_project_and_pdfile"`

**Enums** (defined in models.py as SQLAlchemy/Python enums):
- `ProjectStatus`: draft, uploading, processing, ready, completed
- `PdfRole`: target, reference
- `PdfSource`: upload, pubmed
- `PdfProcessingStatus`: pending, extracting, completed, failed

**Validation**:
```bash
uv run alembic upgrade head
uv run python -c "from paper_image.api.db.models import Project, PdfFile; print('Models importable')"
uv run pytest tests/ -q  # existing tests still pass
```

**Effort**: S | **Dependencies**: Step 0 (BE-01-01 complete)

---

### Step 2: Add Pydantic Schemas for Projects and Uploads

**Files**:
- `src/paper_image/api/schemas/projects.py` — create

**Changes**:
- `ProjectCreate` (request): name (str, required), description (str, optional)
- `ProjectUpdate` (request): name (str, optional), description (str, optional), status (optional)
- `ProjectResponse` (response): id, name, description, status, owner_id, organization_id, target_pdf_id, created_at, updated_at
- `ProjectDetailResponse` (extends ProjectResponse): pdf_files list
- `ProjectListResponse` (response): items list, total, page, page_size
- `PdfFileResponse` (response): id, filename, file_size, role, source, upload_progress, processing_status, figure_count, panel_count, uploaded_at
- `UploadInitRequest` (request): project_id (UUID), filename (str), file_size (int), role (PdfRole)
- `UploadInitResponse` (response): upload_id (str), tus_endpoint (str), metadata (dict)

**Validation**:
```bash
uv run python -c "from paper_image.api.schemas.projects import ProjectCreate, ProjectResponse; print('Schemas importable')"
```

**Effort**: S | **Dependencies**: Step 1

---

### Step 3: Implement Projects CRUD Routes

**Files**:
- `src/paper_image/api/routes/projects.py` — create
- `src/paper_image/api/app.py` — modify (register projects router)

**Endpoints**:
- `GET /api/projects` — paginated list of current user's projects (query params: page, page_size), ordered by updated_at desc
- `POST /api/projects` — create project (name required, description optional, status defaults to draft)
- `GET /api/projects/{id}` — project detail with pdf_files eagerly loaded; 404 if not found or not owner
- `PATCH /api/projects/{id}` — update name/description/status; 404 if not found or not owner
- `DELETE /api/projects/{id}` — soft delete (set status to deleted) or hard delete with cascade; spec says "项目删除时关联的文件记录也被清理" so cascade delete PdfFile records

**Auth**: All endpoints require authenticated user via `get_current_user` dependency. Only project owner can access/modify.

**Validation**:
```bash
# Manual API test via curl or httpie after server startup
uv run uvicorn paper_image.api.app:app --reload
# Create project
curl -X POST http://localhost:8000/api/projects -H "Authorization: Bearer $TOKEN" -d '{"name":"test"}'
# List projects
curl http://localhost:8000/api/projects -H "Authorization: Bearer $TOKEN"
```

**Effort**: M | **Dependencies**: Steps 1, 2

---

### Step 4: Implement tus Upload Server (Minimal Protocol)

**Files**:
- `src/paper_image/api/routes/upload.py` — create
- `src/paper_image/api/app.py` — modify (register upload router)

**Implementation**:

tus protocol endpoints mounted at `/api/upload/`:

1. **OPTIONS /api/upload/** — Return tus protocol capabilities via response headers:
   - `Tus-Resumable: 1.0.0`
   - `Tus-Version: 1.0.0`
   - `Tus-Extension: creation,creation-with-upload`

2. **POST /api/upload/** — Create upload session:
   - Read `Upload-Length` header for total file size
   - Read `Upload-Metadata` header for filename, project_id, role (base64 encoded key-value pairs)
   - Generate unique upload_id
   - Store session state (upload_id, offset=0, length, metadata, chunks_path) in a temporary dict or SQLite table
   - Return `201 Created` with `Location: /api/upload/{upload_id}` header
   - If request has body (Creation With Upload): write body to temp file, update offset, return `200` or `201` based on completion

3. **PATCH /api/upload/{upload_id}** — Upload chunk:
   - Validate `Content-Type: application/offset+octet-stream`
   - Validate `Upload-Offset` header matches current stored offset
   - Append body to temp file at `storage/uploads/{upload_id}.tmp`
   - Update stored offset
   - Return `204 No Content` with `Upload-Offset` header showing new offset

4. **HEAD /api/upload/{upload_id}** — Query upload progress:
   - Return `Upload-Offset` and `Upload-Length` headers
   - Used by client to resume interrupted uploads

**Upload completion logic** (triggered when offset == length):
- Move temp file to final path: `storage/uploads/{project_id}/{upload_id}.pdf`
- Compute sha256 of completed file
- Create PdfFile record in database with all metadata
- If role is target: update Project.target_pdf_id and Project.status to 'uploading'
- Return completion signal via response

**Session storage**: In-memory dict for demo phase (upload_sessions: dict[str, UploadSession]). A production version would use Redis or a DB table. Sessions expire after 24h of inactivity.

**File storage path**: `storage/uploads/{project_id}/{filename}` — created on upload completion.

**Validation**:
```bash
# Test tus creation
curl -X POST http://localhost:8000/api/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Upload-Length: 10485760" \
  -H "Upload-Metadata: filename dGVzdC5wZGY=,project_id <uuid>,role dGFyZ2V0" \
  -H "Tus-Resumable: 1.0.0"
# Expect: 201 with Location header

# Test chunk upload
curl -X PATCH http://localhost:8000/api/upload/<upload_id> \
  -H "Content-Type: application/offset+octet-stream" \
  -H "Upload-Offset: 0" \
  -H "Tus-Resumable: 1.0.0" \
  --data-binary @chunk.bin
# Expect: 204 with Upload-Offset header

# Test resume query
curl -I http://localhost:8000/api/upload/<upload_id> \
  -H "Tus-Resumable: 1.0.0"
# Expect: 200 with Upload-Offset and Upload-Length headers
```

**Effort**: L | **Dependencies**: Steps 1, 2

---

### Step 5: Upload Init API Endpoint

**Files**:
- `src/paper_image/api/routes/upload.py` — modify (add init endpoint)

**Endpoint**: `POST /api/upload/init`
- Accept `UploadInitRequest` body (project_id, filename, file_size, role)
- Validate: project exists, user owns project, role=target only if project has no target_pdf yet
- Create upload session and return `UploadInitResponse` with:
  - `upload_id`
  - `tus_endpoint`: `/api/upload/{upload_id}` (the tus URL for the client)
  - `metadata`: pre-formatted tus metadata string for the client to use

This endpoint bridges the REST API and tus protocol — the frontend calls `/api/upload/init` first to get the tus URL, then uses tus-js-client to upload directly.

**Validation**:
```bash
curl -X POST http://localhost:8000/api/upload/init \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":"<uuid>","filename":"test.pdf","file_size":10485760,"role":"target"}'
# Expect: 200 with upload_id and tus_endpoint
```

**Effort**: S | **Dependencies**: Steps 3, 4

---

### Step 6: Integration Tests

**Files**:
- `tests/test_api_projects.py` — create
- `tests/test_api_upload.py` — create
- `conftest.py` or `tests/conftest.py` — modify (add async test client fixture)

**Test coverage**:

Projects CRUD tests:
- Create project → 201, verify response fields
- List projects → returns only current user's projects
- Get project detail → includes pdf_files list (empty initially)
- Update project → name/description change reflected
- Delete project → 204, subsequent GET returns 404
- Delete project cascade → associated PdfFile records removed
- Unauthorized access → 401
- Access another user's project → 404

Upload tests:
- Upload init → returns valid tus endpoint
- Upload init for target when target exists → 409 conflict
- Full upload flow: init → create tus session → upload chunk → verify PdfFile created
- Resume flow: partial upload → query offset → upload remaining chunk
- Upload 10MB file → verify file on disk, sha256 matches, PdfFile record correct

Test infrastructure:
- Use `httpx.AsyncClient` with FastAPI's `TestClient` (async mode)
- In-memory SQLite for test database
- Override `get_db` dependency with test session
- Override `get_current_user` with mock user
- Temp directory for file storage

**Validation**:
```bash
uv run pytest tests/test_api_projects.py tests/test_api_upload.py -v
```

**Effort**: M | **Dependencies**: Steps 3, 4, 5

---

### Step 7: Storage Directory Setup + Configuration

**Files**:
- `src/paper_image/api/config.py` — create (or modify if BE-01-01 provides it)
- `.gitignore` — modify (add storage/uploads/)

**Changes**:
- Define upload storage path config (default: `storage/uploads/`)
- Ensure storage directory is created on app startup
- Add `storage/uploads/` to `.gitignore`
- Define max upload size config (default: 500MB)
- Define upload session TTL config (default: 24h)

**Validation**:
```bash
uv run python -c "from paper_image.api.config import get_settings; s = get_settings(); print(s.upload_dir)"
```

**Effort**: S | **Dependencies**: Step 1

---

## Risks

### 1. Dependency on Issue #57 (BE-01-01)
- **Risk**: BE-01-01 is not yet implemented. All steps in this plan are blocked until it delivers the FastAPI skeleton, auth, and database.
- **Mitigation**: This plan assumes BE-01-01 interfaces. If BE-01-01's actual interfaces differ, adjust accordingly.
- **Verification**: Check `src/paper_image/api/app.py` and `src/paper_image/api/deps.py` exist and provide expected interfaces before starting.

### 2. tus Protocol Compatibility
- **Risk**: Embedded tus implementation may not be fully compatible with tus-js-client expectations (e.g., CORS preflight handling, exact header behavior).
- **Mitigation**: tus protocol v1.0.0 is small and well-specified. Implement only the required subset (creation, PATCH, HEAD). Test with actual tus-js-client in browser.
- **Verification**: Step 6 tests should include a test simulating the tus-js-client request sequence.

### 3. In-Memory Upload Session Storage
- **Risk**: Server restart loses active upload sessions, breaking in-progress uploads.
- **Mitigation**: Acceptable for demo phase. Document as known limitation. For production, swap to Redis or SQLite-backed sessions.
- **Impact**: Medium — only affects uploads in progress at time of restart.

### 4. File Storage on Local Disk
- **Risk**: `storage/uploads/` grows unbounded; no cleanup on project deletion (only DB records cascade).
- **Mitigation**: Project delete should also delete associated files from disk. Add this to Step 3 implementation detail.
- **Impact**: Low for demo phase.

### 5. Module Catalog Registration
- **Risk**: The `api` module is defined in the roadmap spec but not yet in `docs/module-catalog.md`. Adding routes/models without catalog registration may violate module discipline.
- **Mitigation**: BE-01-01 should register the api module. If not, flag as a finding during execution.

## Notes

- **API path convention**: All endpoints use `/api/` prefix, matching the frontend spec.
- **tus endpoint convention**: tus endpoints at `/api/upload/` (with trailing slash for collection). Individual upload at `/api/upload/{upload_id}`.
- **Frontend integration**: The frontend expects the API envelope `{ code, data, message, timestamp }`. This should be implemented as a response wrapper in BE-01-01's middleware or a shared utility.
- **The module catalog** currently lists `app/ui` with Streamlit. The new `api/` module serves the FastAPI backend. BE-01-01 should establish this module's entry in the catalog.
- **Test strategy**: Strategy B (targeted). Tests in `tests/test_api_projects.py` and `tests/test_api_upload.py` directly cover the new routes. No changes to existing `tests/test_domain.py` or `tests/test_pipeline.py`. Integration test fixtures in `tests/conftest.py`.
