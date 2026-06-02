# BE-01-02: Projects CRUD + tus 上传服务端集成

> Issue: #58
> Branch: task/issue-58
> Depends on: #57 (BE-01-01 — FastAPI 骨架 + Auth + 数据库)

## Plan Summary

实现 Projects CRUD API 和 tus 协议 PDF 断点续传上传。由于 #57 尚未实现（分支无差异提交），本 plan 前两步将包含 BE-01-01 的最小可行骨架（FastAPI app factory、SQLite + SQLAlchemy async、JWT auth stub、Alembic migration 基础），使 #58 可独立交付。tus 上传方案选用 `tuspy-server`（纯 Python ASGI 兼容）内嵌 FastAPI，避免外部 tusd 进程依赖。

## Key Findings

### F1: #57 未实现
- `task/issue-57` 分支存在但与 main 完全一致（无差异提交）。
- 结论：本 plan 必须自建 FastAPI 骨架，不能假设 #57 已交付。
- 影响步骤：Step 1-2 需覆盖 #57 的最小范围。

### F2: tus 方案选型 — tuspy-server
- `tuspy-server` 是纯 Python ASGI 实现，可直接 mount 到 FastAPI。
- 无需外部 tusd 二进制，开发环境和 CI 均可运行。
- 支持 tus v1 协议核心（创建、分片、断点续传、HEAD 查询偏移）。
- 替代方案 `tusd` 需要 Go runtime 或 Docker，增加部署复杂度。
- 依赖：`tuspy-server>=1.0`。

### F3: API 契约对齐
- `frontend-demo-spec.md` § FE-03 定义了 Project/PdfFile 类型和 REST 契约。
- 本 plan 的 schema 和路由必须与前端 TypeScript 类型对齐。
- 统一响应 envelope：`{ code, data, message, timestamp }`。

### F4: domain.py 复用
- 现有 `domain.py` 的 `CorpusScope` 枚举对应 PdfFile 的 `role` 概念但语义不同（scope vs role）。
- ORM model 独立于 domain dataclass，通过 schema 层做映射。
- 不修改 `domain.py`。

## Steps

### Step 1: FastAPI 骨架 + 依赖安装（覆盖 #57 最小范围）

建立 FastAPI app factory、配置加载、数据库连接、健康检查端点。

- **Files**:
  - Modify: `pyproject.toml` — 添加 `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `aiosqlite`, `alembic`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `pydantic-settings` 依赖
  - Create: `src/paper_image/api/__init__.py`
  - Create: `src/paper_image/api/app.py` — FastAPI app factory, CORS, lifespan (DB init)
  - Create: `src/paper_image/api/config.py` — `Settings` (pydantic-settings, DATABASE_URL, SECRET_KEY, STORAGE_PATH, TUS_UPLOAD_PATH)
  - Create: `src/paper_image/api/db/__init__.py`
  - Create: `src/paper_image/api/db/engine.py` — async engine + sessionmaker
  - Create: `src/paper_image/api/db/base.py` — SQLAlchemy `DeclarativeBase`
  - Create: `src/paper_image/api/routes/__init__.py`
  - Create: `src/paper_image/api/routes/health.py` — `GET /api/health`
  - Create: `alembic.ini`
  - Create: `src/paper_image/api/db/migrations/env.py` — Alembic async env
  - Create: `src/paper_image/api/db/migrations/versions/` — 空 versions 目录
- **Effort**: M
- **Dependencies**: none
- **Verification**:
  ```bash
  uv run uvicorn paper_image.api.app:app --port 8000 &
  curl http://localhost:8000/api/health  # → {"status": "ok"}
  kill %1
  uv run python -c "from paper_image.api.app import create_app; print('OK')"
  uv run python -c "from paper_image.api.config import get_settings; print('OK')"
  uv run python -c "from paper_image.api.db.engine import get_session; print('OK')"
  ```

### Step 2: Auth stub + User ORM Model（覆盖 #57 最小范围）

建立最小 JWT auth（注册/登录/token 刷新），支持后续 Projects API 的用户鉴权。

- **Files**:
  - Create: `src/paper_image/api/db/models/user.py` — `User` ORM model (id, email, name, hashed_password, role, organization, created_at)
  - Create: `src/paper_image/api/schemas/auth.py` — RegisterRequest, LoginRequest, AuthResponse, UserResponse
  - Create: `src/paper_image/api/routes/auth.py` — `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`
  - Create: `src/paper_image/api/deps.py` — `get_current_user` dependency (JWT decode + DB lookup)
  - Modify: `src/paper_image/api/app.py` — 注册 auth router
  - Modify: `src/paper_image/api/db/__init__.py` — 导出所有 models
- **Effort**: M
- **Dependencies**: Step 1
- **Verification**:
  ```bash
  # 注册
  curl -X POST http://localhost:8000/api/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email":"test@example.com","password":"secret123","name":"Test"}'
  # → {"code":0,"data":{"user":{...},"accessToken":"..."},"message":"ok","timestamp":...}

  # 登录
  curl -X POST http://localhost:8000/api/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"test@example.com","password":"secret123"}'
  # → {"code":0,"data":{"user":{...},"accessToken":"..."},"message":"ok","timestamp":...}

  # 受保护端点
  curl http://localhost:8000/api/auth/me -H 'Authorization: Bearer <token>'
  # → {"code":0,"data":{...}}
  ```

### Step 3: Project + PdfFile ORM Models

定义 SQLAlchemy ORM models 和 Alembic migration。

- **Files**:
  - Create: `src/paper_image/api/db/models/project.py` — `Project` ORM model
    - `id` (UUID, PK), `name` (str), `description` (str, nullable), `status` (Enum: draft/uploading/processing/ready/completed, default draft)
    - `owner_id` (FK → users.id), `organization_id` (str, nullable)
    - `target_pdf_id` (FK → pdf_files.id, nullable)
    - `created_at`, `updated_at` (datetime, server default)
  - Create: `src/paper_image/api/db/models/pdf_file.py` — `PdfFile` ORM model
    - `id` (UUID, PK), `project_id` (FK → projects.id, cascade delete)
    - `filename` (str), `file_size` (bigint), `role` (Enum: target/reference), `source` (Enum: upload/pubmed)
    - `upload_progress` (int, 0-100, default 0), `processing_status` (Enum: pending/extracting/completed/failed, default pending)
    - `figure_count` (int, nullable), `panel_count` (int, nullable)
    - `storage_path` (str), `sha256` (str, nullable), `uploaded_at` (datetime, nullable)
  - Modify: `src/paper_image/api/db/models/__init__.py` — 导出所有 models
  - Generate: Alembic migration (auto-generate)
- **Effort**: S
- **Dependencies**: Step 2
- **Verification**:
  ```bash
  uv run alembic upgrade head
  uv run python -c "
  from paper_image.api.db.models.project import Project
  from paper_image.api.db.models.pdf_file import PdfFile
  print('Models imported OK')
  "
  # 验证 migration 创建了 projects 和 pdf_files 表
  uv run python -c "
  import sqlite3
  conn = sqlite3.connect('paper_image.db')
  tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
  assert ('projects',) in tables
  assert ('pdf_files',) in tables
  print('Tables verified OK')
  "
  ```

### Step 4: Projects CRUD API

实现项目增删改查路由，含分页、权限检查、级联删除。

- **Files**:
  - Create: `src/paper_image/api/schemas/projects.py` — Pydantic schemas
    - `ProjectCreate` (name, description?), `ProjectUpdate` (name?, description?, status?)
    - `ProjectResponse` (含 target_pdf, reference_pdfs 列表)
    - `ProjectListResponse` (分页: items, total, page, page_size)
    - `PdfFileResponse`
    - 统一 envelope: `ApiResponse[T]`
  - Create: `src/paper_image/api/routes/projects.py`
    - `GET /api/projects` — 分页列表，默认 page=1, page_size=20
    - `POST /api/projects` — 创建项目，owner=current_user
    - `GET /api/projects/{id}` — 项目详情（含 PDF 列表）
    - `PATCH /api/projects/{id}` — 更新项目（仅 owner 可操作）
    - `DELETE /api/projects/{id}` — 删除项目及关联 PdfFile 记录（cascade）
  - Modify: `src/paper_image/api/app.py` — 注册 projects router
- **Effort**: M
- **Dependencies**: Step 3
- **Verification**:
  ```bash
  # 创建项目
  curl -X POST http://localhost:8000/api/projects \
    -H 'Authorization: Bearer <token>' \
    -H 'Content-Type: application/json' \
    -d '{"name":"Test Project","description":"A test"}'
  # → {"code":0,"data":{"id":"...","name":"Test Project","status":"draft",...}}

  # 列表
  curl http://localhost:8000/api/projects -H 'Authorization: Bearer <token>'
  # → {"code":0,"data":{"items":[...],"total":1,"page":1,"page_size":20}}

  # 详情
  curl http://localhost:8000/api/projects/<id> -H 'Authorization: Bearer <token>'
  # → {"code":0,"data":{"id":"...","targetPdf":null,"referencePdfs":[],...}}

  # 更新
  curl -X PATCH http://localhost:8000/api/projects/<id> \
    -H 'Authorization: Bearer <token>' \
    -H 'Content-Type: application/json' \
    -d '{"description":"Updated"}'

  # 删除
  curl -X DELETE http://localhost:8000/api/projects/<id> -H 'Authorization: Bearer <token>'
  # → {"code":0,"data":null,"message":"deleted"}
  ```

### Step 5: tus 上传集成（tuspy-server）

将 tuspy-server 集成到 FastAPI，实现上传初始化和文件接收。

- **Files**:
  - Create: `src/paper_image/api/routes/upload.py`
    - `POST /api/upload/init` — 初始化上传，创建 PdfFile 记录 (status=pending, progress=0)，返回 tus endpoint URL + metadata
    - tus ASGI app mount 到 `/api/upload/files/` 路径
    - 上传完成回调：更新 PdfFile 的 storage_path, file_size, sha256, upload_progress=100, uploaded_at
  - Modify: `src/paper_image/api/app.py` — mount tus ASGI sub-app
  - Modify: `src/paper_image/api/config.py` — TUS_UPLOAD_PATH, STORAGE_PATH 配置
  - Create: `src/paper_image/api/services/upload.py` — 上传完成处理逻辑
    - 计算 sha256
    - 移动文件到最终 storage_path (`storage/uploads/{project_id}/{pdf_file_id}.pdf`)
    - 更新 PdfFile 记录
    - 更新 Project 状态（如有 target_pdf 且上传完成 → status=uploading → ready when target uploaded）
- **Effort**: L
- **Dependencies**: Step 4
- **Verification**:
  ```bash
  # 初始化上传
  curl -X POST http://localhost:8000/api/upload/init \
    -H 'Authorization: Bearer <token>' \
    -H 'Content-Type: application/json' \
    -d '{"projectId":"<id>","role":"target","filename":"test.pdf","fileSize":10485760}'
  # → {"code":0,"data":{"uploadUrl":"/api/upload/files/<tus-id>","metadata":{...}}}

  # tus 创建上传
  curl -X POST http://localhost:8000/api/upload/files/ \
    -H 'Tus-Resumable: 1.0.0' \
    -H 'Upload-Length: 10485760' \
    -H 'Upload-Metadata: filename dGVzdC5wZGY='
  # → 201 Created, Location header

  # tus 分片上传
  curl -X PATCH http://localhost:8000/api/upload/files/<tus-id> \
    -H 'Tus-Resumable: 1.0.0' \
    -H 'Content-Type: application/offset+octet-stream' \
    -H 'Upload-Offset: 0' \
    --data-binary @test.pdf
  # → 204 No Content

  # 断点续传
  curl -I http://localhost:8000/api/upload/files/<tus-id> \
    -H 'Tus-Resumable: 1.0.0'
  # → Upload-Offset: <bytes received>
  ```
- **Notes**: 如果 `tuspy-server` 不满足需求（如缺少 ASGI 兼容），回退方案为手动实现 tus v1 核心协议（POST 创建 + HEAD 查询 + PATCH 分片），代码量约 150-200 行。

### Step 6: 测试

编写单元测试和集成测试，覆盖 CRUD、上传流程、断点续传、级联删除。

- **Files**:
  - Create: `tests/api/__init__.py`
  - Create: `tests/api/conftest.py` — 测试 fixtures (async client, test DB, auth token)
  - Create: `tests/api/test_auth.py` — 注册/登录/refresh 测试
  - Create: `tests/api/test_projects.py` — CRUD 测试
  - Create: `tests/api/test_upload.py` — 上传初始化 + tus 流程测试
- **Effort**: M
- **Dependencies**: Step 5
- **Verification**:
  ```bash
  uv run pytest tests/api/ -v
  # 所有测试通过
  uv run pytest tests/ -v
  # 确认不破坏现有 domain/pipeline 测试
  ```

### Step 7: 存储目录与 .gitignore

确保上传存储目录存在且被 gitignore。

- **Files**:
  - Modify: `.gitignore` — 确认 `uploads/`, `storage/`, `paper_image.db` 已被忽略（当前已有 `uploads/`）
  - Create: `storage/.gitkeep` — 确保 storage 目录存在
- **Effort**: XS
- **Dependencies**: Step 1
- **Verification**:
  ```bash
  git status  # storage/.gitkeep 应出现，数据库文件和上传文件不应被跟踪
  ```

## Risks

### R1: #57 骨架可能重复（Medium）
- **风险**: 如果 #57 独立实现并先于 #58 合并，Step 1-2 的骨架代码可能与 #57 冲突。
- **缓解**: Step 1-2 保持最小（app factory + config + DB engine + auth stub），不引入多余抽象。合并时通过 rebase 解决冲突。
- **验证**: 合并前对比 #57 分支。

### R2: tuspy-server ASGI 兼容性（Medium）
- **风险**: `tuspy-server` 的 ASGI 集成可能有坑（不完全兼容 FastAPI 的 middleware 链）。
- **缓解**: Step 5 包含回退方案（手动实现 tus v1 核心，约 150-200 行）。如 tuspy-server 不可用，直接走回退。
- **验证**: Step 5 的 verification 命令覆盖 tus 协议核心交互。

### R3: 文件存储路径安全（High）
- **风险**: 上传路径可能被路径遍历攻击利用（`../../etc/passwd`）。
- **缓解**: storage_path 由服务端生成（UUID-based），不接受用户输入的路径组件。文件操作前验证 resolved path 在 storage root 内。
- **验证**: 测试中包含恶意文件名用例。

### R4: 大文件上传内存占用（Low）
- **风险**: 如果 tus 实现将整个文件缓存在内存中，大 PDF（100MB+）会导致 OOM。
- **缓解**: tuspy-server 和手动实现均使用文件流式写入，不在内存中缓存完整文件。
- **验证**: 使用 10MB+ 文件测试上传，监控内存使用。

### R5: SQLite 并发写入限制（Low）
- **风险**: SQLite 在高并发写入时可能出现锁竞争。
- **缓解**: MVP 阶段单用户或低并发，SQLite 足够。配置 WAL 模式优化并发读。
- **验证**: 当前阶段不需要压力测试，但 plan 应记录此限制。

## Notes

- **tus 协议版本**: 实现 tus v1.0.0 核心协议（creation, concatenation 可选）。
- **认证方式**: Bearer token（JWT），通过 `Authorization` header 传递。tus 上传请求通过自定义 header `X-Upload-Token` 传递短期上传凭证（避免在 tus 客户端暴露用户 JWT）。
- **统一响应格式**: 所有 API 返回 `{ code: int, data: T | null, message: str, timestamp: str }`，与 frontend spec 对齐。
- **CORS**: 开发环境允许 `localhost:3000`（Next.js dev server）。
- **数据库**: SQLite + aiosqlite（async），Alembic 管理 migration。生产环境可切换到 PostgreSQL。
