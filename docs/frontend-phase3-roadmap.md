# 前端 Phase 3 路线图 — 设置、Org Admin、Corpus 与后端骨架

> 补齐 Phase 1-7 中发现的关键缺口。Phase 8 覆盖用户设置和组织管理员视图；Phase 9 覆盖核心产品能力——私有库管理——以及后端 API 骨架。

## 模块 FE-16: 用户设置

**Scope**: 修改密码（含首次登录强制改密）、编辑个人信息、通知偏好、数据隐私管理。

**页面**: `/settings`

**首次登录强制改密流程**:
```
Admin 创建用户（生成临时密码）
  → 用户首次登录 → 检测 must_change_password 标志
  → 强制跳转 /settings/password → 改密后清除标志 → 正常使用
```

**设置页 Tab 结构**:
- 个人信息：姓名、邮箱（只读）、机构（只读，由 admin 管理）
- 安全：修改密码（当前密码 + 新密码 + 确认）
- 通知：每种通知类型的开关（处理完成/配额告警/工单回复/系统公告）
- 数据隐私：已上传的 PDF/Figure 列表 + "请求删除"入口（创建 ticket）

---

## 模块 FE-17: Org Admin 视图

**Scope**: 组织管理员（实验室 PI）自助管理团队、查看组织报告汇总、监控组织用量。

**前提**: 用户角色为 `org_admin`，已归属某组织。

**路由**: 复用用户端 dashboard 布局，侧边栏增加"我的团队"分组。

**页面**:
- `/team` — 组织概览（成员数、本月报告、用量摘要）
- `/team/members` — 成员管理（邀请/移除、角色切换）
- `/team/reports` — 组织内所有成员的报告列表
- `/team/usage` — 组织配额用量详情
- `/team/corpus` — 组织私有库管理入口（链接到 FE-18）

**成员管理**:
- org_admin 可邀请已存在的 active 用户加入组织（不能创建新用户，创建仍由 admin）
- org_admin 可将成员角色在 user ↔ org_admin 间切换
- org_admin 可从组织移除成员

---

## 模块 FE-18: Corpus / 私有库管理

**Scope**: 创建和管理私有历史论文库、批量导入、PubMed Topic 管理、项目中关联已有库。

**核心概念**:

| 概念 | 说明 |
|------|------|
| Corpus | 一个论文集合（私有库或 PubMed Topic 库） |
| Corpus Type | `private`（用户上传）/ `pubmed_topic`（PubMed 检索建库）|
| Corpus Status | `empty` / `importing` / `indexing` / `ready` / `error` |

**页面**:
- `/corpus` — Corpus 列表（我的库 + 组织共享库）
- `/corpus/new` — 创建新 Corpus
- `/corpus/[id]` — Corpus 详情（统计、文章列表、导入历史）
- `/corpus/[id]/import` — 批量导入页面

**创建 Corpus 流程**:
```
选择类型（私有库 / PubMed Topic）
  → 私有库：填写名称和描述 → 创建成功 → 跳转导入页
  → PubMed Topic：填写检索策略（关键词、MeSH 术语、年份范围）
    → 预览匹配文章数 → 确认 → 后端异步建库
```

**批量导入方式**:
1. PDF 批量上传（复用 tus，支持多文件拖拽）
2. PMID/DOI 列表导入（文本框粘贴或 CSV 上传）
3. 从现有项目的 reference 迁移

**Corpus 详情页**:
- 统计卡片：article 数、figure 数、panel 数、索引状态
- 文章列表（表格：标题、来源、page/figure/panel 数、导入时间）
- 导入历史（批次、状态、成功/失败数）
- 操作：重建索引、删除 corpus

**项目中关联 Corpus（FE-03 扩展）**:
- 上传页 Reference 区域新增第三个入口："选择已有库"
- 弹出 Corpus 选择器（列出当前用户和组织的 ready 状态 corpus）
- 选择后 corpus 中的 panel 自动作为 reference 参与筛查

---

## 模块 FE-19: Admin 审计日志

**Scope**: 管理员查看系统操作日志——用户管理、配额变更、工单处理等关键操作的审计记录。

**页面**: `/admin/audit-log`

**日志条目**:
- 操作者（admin 姓名）
- 操作类型：`user_created` / `user_activated` / `user_suspended` / `quota_assigned` / `org_created` / `ticket_resolved` / `corpus_created`
- 操作目标（用户名/组织名/工单 ID）
- 时间戳
- 详情（JSON 快照：变更前/变更后）

---

## 模块 BE-01: 后端 API 骨架 (FastAPI)

**Scope**: 为前端提供最小可用的 REST API 层，替代 MSW mock。

**技术栈**:
- FastAPI + Pydantic v2
- SQLite (dev) / PostgreSQL (prod)
- SQLAlchemy 2.0 (async)
- python-jose (JWT)
- tusd 或 tus-py (上传服务)

**API 分层**:
```
src/paper_image/
  api/
    __init__.py
    app.py           # FastAPI app factory
    deps.py          # 依赖注入（db session, current_user）
    middleware.py     # CORS, auth, error handling
    routes/
      auth.py        # register, login, refresh, me
      projects.py    # CRUD + status
      figures.py     # 列表
      panels.py      # 列表, confirm
      reports.py     # 获取, 导出
      pubmed.py      # search proxy
      chat.py        # SSE stream
      tickets.py     # 用户端工单
      notifications.py
      admin/
        users.py     # 用户管理
        organizations.py
        quotas.py
        tickets.py   # 管理端工单
        audit.py
    schemas/         # Pydantic request/response models
```

**交付范围**:
- BE-01-01: FastAPI 骨架 + Auth（register/login/refresh/me）+ JWT + 角色中间件
- BE-01-02: Projects CRUD + tus 上传服务端集成
- BE-01-03: Figure/Panel 查询 + Panel 确认 + 报告查询
- BE-01-04: Admin 端 API（用户管理 + 组织 + 配额 + 工单）
- BE-01-05: PubMed 代理 + AI Chat SSE + 通知

## Issue List

### Phase 8: Settings & Org Admin (FE-16 + FE-17 + FE-19)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-16-01 | 用户设置页（个人信息 + 修改密码 + 首次登录强制改密） | FE-16 | FE-02-04 | 3h |
| FE-16-02 | 通知偏好设置 + 数据隐私管理（查看数据 + 请求删除） | FE-16 | FE-16-01, FE-14-01 | 2h |
| FE-17-01 | Org Admin 组织概览 + 成员管理页 | FE-17 | FE-10-03 | 4h |
| FE-17-02 | Org Admin 组织报告列表 + 组织用量详情 | FE-17 | FE-17-01, FE-11-03 | 3h |
| FE-19-01 | Admin 审计日志页（列表 + 过滤 + 详情展开） | FE-19 | FE-09-01 | 3h |

### Phase 9: Corpus & Backend (FE-18 + BE-01)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-18-01 | Corpus 列表页 + 创建 Corpus（私有库 / PubMed Topic） | FE-18 | FE-01-03 | 4h |
| FE-18-02 | Corpus 详情页（统计 + 文章列表 + 导入历史） | FE-18 | FE-18-01 | 3h |
| FE-18-03 | Corpus 批量导入（PDF 多文件上传 + PMID/DOI 列表导入） | FE-18 | FE-18-01, FE-03-03 | 4h |
| FE-18-04 | 项目 Reference 区关联已有 Corpus + Corpus 选择器 | FE-18 | FE-18-01, FE-03-04 | 3h |
| BE-01-01 | FastAPI 骨架 + Auth API（register/login/refresh/me + JWT + 角色） | BE-01 | — | 4h |
| BE-01-02 | Projects CRUD + tus 上传服务端 | BE-01 | BE-01-01 | 4h |
| BE-01-03 | Figure/Panel/Report 查询 API + Panel 确认 | BE-01 | BE-01-02 | 3h |
| BE-01-04 | Admin API（用户/组织/配额/工单 CRUD） | BE-01 | BE-01-01 | 4h |
| BE-01-05 | PubMed 代理 + AI Chat SSE + 通知 API | BE-01 | BE-01-01 | 4h |
