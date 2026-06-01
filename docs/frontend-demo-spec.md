# 前端 Demo 开发方案

> 本文档定义论文图像完整性筛查系统前端 demo 的架构、模块划分和实施计划。
> 后端图像查重服务由独立 API 提供，前端暂不实现查重接口，仅负责用户端功能。

## 1. 总体架构

### 1.1 技术栈

| 层级 | 选型 | 理由 |
|------|------|------|
| 框架 | Next.js 15 (App Router) | RSC + 文件路由 + API Routes 可充当 BFF |
| 样式 | Tailwind CSS 4 + shadcn/ui | 设计系统开箱即用，组件可定制 |
| 状态 | Zustand (客户端) + TanStack Query v5 (服务端) | 轻量 + 缓存失效自动化 |
| 上传 | tus-js-client | 断点续传，大文件可靠传输 |
| PDF 预览 | react-pdf (PDF.js) | 客户端 PDF 渲染 + 页面标注 |
| 图像标注 | Konva.js (react-konva) | Canvas 上绘制 bbox/overlay/heatmap |
| AI 对话 | Vercel AI SDK | 流式输出 + 工具调用 |
| 表单 | React Hook Form + Zod | 类型安全的表单验证 |
| 认证 | NextAuth.js v5 (Auth.js) | 多 provider + JWT + session |
| 国际化 | next-intl | 中英文切换 |
| 测试 | Vitest + Testing Library + Playwright | 单元 + 集成 + E2E |

### 1.2 项目结构

```
frontend/
  src/
    app/                          # Next.js App Router
      (auth)/                     # 认证相关页面组
        login/page.tsx
        register/page.tsx
      (dashboard)/                # 登录后主面板
        layout.tsx                # 带侧边栏的布局
        page.tsx                  # Dashboard 首页
        projects/                 # 项目管理
          page.tsx
          [projectId]/
            page.tsx              # 项目详情
            upload/page.tsx       # 上传页面
            figures/page.tsx      # Figure 浏览
            panels/page.tsx       # Panel 确认
            report/page.tsx       # 报告查看
            consultation/page.tsx # AI 咨询
        pubmed/page.tsx           # PubMed 搜索
        settings/page.tsx         # 用户设置
      api/                        # BFF API Routes
        auth/[...nextauth]/route.ts
        upload/route.ts
        projects/route.ts
        pubmed/route.ts
        ai/chat/route.ts
    components/
      ui/                         # shadcn/ui 基础组件
      auth/                       # 认证相关组件
      upload/                     # 上传相关组件
      pdf/                        # PDF 预览与标注
      figures/                    # Figure 展示
      panels/                     # Panel 展示与编辑
      report/                     # 报告相关组件
      ai/                         # AI 咨询组件
      pubmed/                     # PubMed 组件
      layout/                     # 布局组件
    lib/
      api-client.ts               # 后端 API 客户端
      auth.ts                     # NextAuth 配置
      upload.ts                   # tus 上传封装
      store/                      # Zustand stores
      hooks/                      # 自定义 hooks
      types/                      # TypeScript 类型定义
      utils/                      # 工具函数
      constants.ts                # 常量定义
    styles/
      globals.css                 # Tailwind 入口
```

### 1.3 与后端交互模型

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                        │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Upload  │  │ Viewer  │  │  Report  │  │ AI Consult    │  │
│  │ Module  │  │ Module  │  │  Module  │  │ Module        │  │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └──────┬────────┘  │
│       │            │            │               │            │
│  ┌────┴────────────┴────────────┴───────────────┴────────┐   │
│  │              API Client Layer (TanStack Query)        │   │
│  └───────────────────────┬───────────────────────────────┘   │
└──────────────────────────┼───────────────────────────────────┘
                           │ REST/SSE
┌──────────────────────────┼───────────────────────────────────┐
│                          │   Backend (FastAPI)               │
│  ┌───────────────────────┴───────────────────────────────┐   │
│  │                   API Gateway                         │   │
│  └──┬──────┬────────┬──────────┬────────┬────────────────┘   │
│     │      │        │          │        │                    │
│  Upload  Extract  PubMed   Report    AI Gateway             │
│  (tus)   Pipeline  Fetch   Generate  (core/ai)              │
│     │      │        │          │        │                    │
│  ┌──┴──────┴────────┴──────────┴────────┴────────────────┐   │
│  │          查重服务 API（独立部署，暂不实现）              │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**关键约定**：
- 前端通过 Next.js API Routes 作为 BFF，代理后端 FastAPI 请求
- PDF 上传使用 tus 协议直传后端，不经过 BFF
- AI 咨询使用 SSE 流式传输
- 所有 API 响应遵循统一 envelope：`{ code, data, message, timestamp }`
- 查重相关接口预留类型定义，但调用方法返回 mock 数据

## 2. 模块划分与 Spec

---

### 模块 FE-01: 项目脚手架与基础设施

**Scope**: 搭建 Next.js 项目骨架、Tailwind 配置、shadcn/ui 安装、路由结构、布局系统、API 客户端基础。

**Anti-scope**: 不含任何业务逻辑，不含认证实现。

**技术决策**:
- pnpm 为包管理器
- TypeScript strict mode
- ESLint + Prettier
- Husky + lint-staged
- 路径别名 `@/` 指向 `src/`

**交付物**:
- `frontend/` 目录完整脚手架
- Tailwind + shadcn/ui 配置
- 全局布局（顶栏、侧边栏、主内容区）
- API 客户端封装（axios instance + interceptors + 类型安全）
- 统一错误边界组件
- 环境变量配置 (`.env.example`)
- 类型定义基础文件：`types/api.ts`, `types/domain.ts`

**验证标准**:
- `pnpm dev` 正常启动
- 访问 `/` 展示带侧边栏的空白 dashboard
- API 客户端能发送请求并处理错误

---

### 模块 FE-02: 用户认证系统

**Scope**: 注册、登录、登出、JWT 管理、受保护路由、角色区分（author/reviewer/admin）。

**Anti-scope**: 不含 OAuth 第三方登录（后续可扩展）、不含复杂 RBAC 权限矩阵。

**页面**:
- `/login` — 邮箱+密码登录
- `/register` — 注册（邮箱、密码、姓名、机构）

**状态管理**:
- `useAuthStore` (Zustand): currentUser, token, isAuthenticated
- JWT 存 httpOnly cookie，refresh token 机制
- 中间件拦截未认证请求，重定向 `/login`

**API 契约** (前端定义，后端实现):

```typescript
// POST /api/auth/register
interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  organization?: string;
}

// POST /api/auth/login
interface LoginRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  organization: string | null;
  role: 'author' | 'reviewer' | 'admin';
  createdAt: string;
}
```

**交付物**:
- NextAuth.js v5 配置（Credentials provider）
- 登录/注册页面（表单验证、错误提示）
- Auth middleware（路由守卫）
- `useAuthStore` + `useSession` hook
- 用户菜单组件（头像、角色标签、登出）

**验证标准**:
- 注册 → 登录 → 访问 dashboard → 登出 → 重定向 login
- 未登录直接访问 `/projects` 被重定向
- token 过期后自动 refresh 或重新登录

---

### 模块 FE-03: PDF 上传与项目管理

**Scope**: 创建筛查项目、区分目标 PDF 和参考 PDF 上传、断点续传、上传进度、文件列表管理。

**Anti-scope**: 不含 PDF 内容解析（后端负责）、不含查重触发。

**核心概念**:

| 概念 | 说明 |
|------|------|
| Project | 一次筛查任务的容器，包含一个 target PDF 和多个 reference PDF |
| Target PDF | 待筛查的目标论文，每个 project 仅一个 |
| Reference PDF | 用于对比的参考论文，分为用户上传和 PubMed 抓取两类 |
| Upload Session | 一次上传行为，支持断点续传 |

**页面**:
- `/projects` — 项目列表（卡片/列表视图切换）
- `/projects/new` — 创建新项目
- `/projects/[id]` — 项目详情总览
- `/projects/[id]/upload` — PDF 上传页

**上传流程**:

```
用户拖拽 PDF → 前端校验（类型/大小）
  → tus 创建上传会话 → 分片上传 → 进度回调
  → 上传完成 → 通知后端开始处理
  → 轮询/SSE 获取处理状态
```

**API 契约**:

```typescript
// Project CRUD
interface Project {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'uploading' | 'processing' | 'ready' | 'completed';
  targetPdf: PdfFile | null;
  referencePdfs: PdfFile[];
  createdAt: string;
  updatedAt: string;
}

interface PdfFile {
  id: string;
  filename: string;
  fileSize: number;
  role: 'target' | 'reference';
  source: 'upload' | 'pubmed';
  uploadProgress: number;      // 0-100
  processingStatus: 'pending' | 'extracting' | 'completed' | 'failed';
  figureCount: number | null;
  panelCount: number | null;
  uploadedAt: string;
}

// POST /api/projects
interface CreateProjectRequest {
  name: string;
  description?: string;
}

// tus upload endpoint: POST /api/upload
// headers: X-Project-Id, X-Pdf-Role (target|reference)
```

**交付物**:
- 项目列表页（创建、删除、状态显示）
- 上传页面：target 区 + reference 区分离
- tus 上传封装（断点续传、并发控制、进度条）
- 文件列表组件（状态标签、文件大小、操作菜单）
- 上传失败重试与错误提示
- `useProjectStore` + `useUploadManager` hooks

**验证标准**:
- 创建项目 → 上传 target PDF → 上传多个 reference PDF
- 刷新页面后续传正常
- 100MB PDF 上传进度条正常更新
- target 区域只允许单个 PDF，reference 区域允许多个

---

### 模块 FE-04: Figure 提取与 Panel 切分展示

**Scope**: 展示从 PDF 中提取的 figure、panel 切分结果、bbox 可视化、panel 确认/修正界面。

**Anti-scope**: 不在前端执行图像处理、不含查重结果展示。

**页面**:
- `/projects/[id]/figures` — Figure 画廊 + PDF 页面对照
- `/projects/[id]/panels` — Panel 切分确认

**Figure 画廊**:
- 按 PDF 分组展示（target / 各 reference）
- 每个 figure 卡片：缩略图、caption、page 号、panel 数量
- 点击 figure 展开：原图 + bbox 标注 + panel 列表
- PDF 页面视图：在页面上叠加 figure bbox

**Panel 确认界面**:
- 左侧：原始 figure 图像 + 检测到的 panel bbox（用 react-konva 绘制）
- 右侧：切分后的 panel 列表
- 操作：确认切分正确 / 标记误切 / 手动调整（拖拽 bbox）
- Panel 统计卡片：target panel 数、reference panel 数、预估费用

**API 契约**:

```typescript
interface Figure {
  id: string;
  articleId: string;
  page: number;
  caption: string;
  imagePath: string;       // 图片 URL
  bbox: [number, number, number, number]; // x0, y0, x1, y1
  panels: Panel[];
}

interface Panel {
  id: string;
  figureId: string;
  label: string;           // "A", "B", "C" 等
  imagePath: string;
  bbox: [number, number, number, number];
  confirmed: boolean;
  confidence: number;       // 0-1 切分置信度
}

// GET /api/projects/:id/figures
// GET /api/projects/:id/panels
// PATCH /api/panels/:id/confirm   { confirmed: boolean }
// PATCH /api/panels/:id/bbox      { bbox: [x0,y0,x1,y1] }

interface PanelSummary {
  targetPanelCount: number;
  referencePanelCount: number;
  confirmedCount: number;
  pendingCount: number;
}
```

**交付物**:
- Figure 画廊组件（卡片/网格视图）
- PDF 页面 + figure bbox overlay (react-pdf + react-konva)
- Panel 切分可视化（原图 + bbox + 缩略图列表）
- Panel 确认交互（确认/拒绝/调整）
- Panel 统计摘要组件
- `useFigures` + `usePanels` hooks (TanStack Query)

**验证标准**:
- 上传 PDF 处理完后，figure 画廊展示正确
- 点击 figure 查看 panel 切分结果
- 确认/拒绝 panel 后状态正确更新
- Panel 统计数据实时更新

---

### 模块 FE-05: PubMed 参考文献抓取

**Scope**: 通过 PubMed 搜索相关论文、选取作为参考 PDF、自动获取 PDF 链接。

**Anti-scope**: 不负责 PDF 内容下载和解析（后端完成）、不负责全文搜索引擎。

**页面**:
- `/pubmed` — 独立 PubMed 搜索页
- `/projects/[id]/upload` 内嵌 PubMed 搜索面板

**搜索流程**:

```
输入关键词/PMID/DOI → 调用 PubMed E-utilities
  → 展示搜索结果列表
  → 用户选择文章 → 检查 PDF 可用性 (PMC/DOI)
  → 添加为 reference → 后端下载并处理
```

**API 契约**:

```typescript
// GET /api/pubmed/search?query=...&page=1&pageSize=20
interface PubMedSearchResult {
  pmid: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  abstract: string;
  doi: string | null;
  pmcId: string | null;         // PMC 可获取全文
  pdfAvailable: boolean;
}

interface PubMedSearchResponse {
  results: PubMedSearchResult[];
  totalCount: number;
  page: number;
}

// POST /api/projects/:id/references/pubmed
interface AddPubMedReferenceRequest {
  pmid: string;
  title: string;
  doi: string | null;
  pmcId: string | null;
}
```

**交付物**:
- PubMed 搜索输入框（支持关键词、PMID、DOI）
- 搜索结果列表（标题、作者、期刊、年份、摘要折叠）
- PDF 可用性标识（PMC 全文 / DOI 链接 / 不可用）
- 批量选择 + 添加到项目
- 已添加参考文献列表
- `usePubMedSearch` hook

**验证标准**:
- 输入关键词搜索到 PubMed 结果
- 选择文章并添加为参考 PDF
- 已添加的参考文献出现在项目 reference 列表中
- PMC 可用的文章标记为可自动获取

---

### 模块 FE-06: AI 咨询窗口

**Scope**: 围绕筛查报告提供受证据约束的 AI 问答、流式输出、咨询历史记录。

**Anti-scope**: 不负责开放式通用 AI 对话、不做不受证据约束的建议、不负责 LLM 调用（后端 core/ai 网关负责）。

**页面**:
- `/projects/[id]/consultation` — 独立 AI 咨询页
- 报告页面内嵌可收起的咨询侧边栏

**对话约束**:
- 每条消息关联当前 project 的 findings 上下文
- AI 回复必须引用具体 finding ID 和证据
- 使用 review-safe language
- 显示"AI 建议仅供参考"提示
- 咨询额度追踪（token/次数限制）

**API 契约**:

```typescript
// POST /api/ai/chat (SSE stream)
interface ChatRequest {
  projectId: string;
  message: string;
  findingIds?: string[];      // 可选关联特定 finding
  sessionId: string;          // 对话会话 ID
}

// SSE stream events:
// event: token     data: { content: "..." }
// event: citation  data: { findingId: "...", text: "..." }
// event: done      data: { messageId: "...", tokenCount: number }
// event: error     data: { code: "...", message: "..." }

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: Citation[];
  createdAt: string;
  tokenCount?: number;
}

interface Citation {
  findingId: string;
  figureId: string;
  text: string;
}

interface ConsultationSession {
  id: string;
  projectId: string;
  messages: ChatMessage[];
  totalTokens: number;
  createdAt: string;
}
```

**交付物**:
- 聊天界面组件（消息列表 + 输入框 + 发送）
- 流式输出渲染（逐 token 显示 + 打字机效果）
- 证据引用卡片（点击跳转到对应 finding）
- 咨询历史侧边栏
- 咨询额度指示器
- 预设问题快捷按钮（如"这个发现是否可能是误报？"）
- `useChatStream` hook (基于 Vercel AI SDK)

**验证标准**:
- 发送消息 → 流式输出回复
- 回复中包含可点击的 finding 引用
- 历史消息正确加载
- 额度用尽后显示提示

---

### 模块 FE-07: 报告生成与查看

**Scope**: 展示筛查报告、evidence 仪表板、finding 详情钻取、source/target 对比、heatmap 叠加、导出。

**Anti-scope**: 不执行分析计算、不修改原始证据数据。

**页面**:
- `/projects/[id]/report` — 报告主页

**报告结构**:

```
报告页面
├── 摘要卡片区（项目信息、总 finding 数、风险等级分布）
├── Finding 列表（可按等级/类型/figure 过滤和排序）
│   ├── Finding 卡片
│   │   ├── 等级标签（exact_duplicate/near_duplicate/...）
│   │   ├── 置信度分数
│   │   ├── Source/Target 缩略图预览
│   │   └── 操作按钮（详情/标记/咨询）
│   └── ...
├── Finding 详情面板（侧边抽屉或弹窗）
│   ├── Source 图 + Target 图并排
│   ├── Overlay 叠加视图
│   ├── Heatmap 展示（forensic 结果）
│   ├── 匹配参数（算法、分数、模型版本）
│   └── 人工标记区
├── Panel 用量摘要
│   ├── Target panel 数量
│   ├── Reference panel 数量（按来源分类）
│   └── 费用预估
└── 导出区（HTML / PDF 下载）
```

**API 契约**:

```typescript
interface ScreeningReport {
  id: string;
  projectId: string;
  generatedAt: string;
  summary: ReportSummary;
  findings: Finding[];
  panelUsage: PanelUsage;
  modelVersions: ModelVersion[];
}

interface ReportSummary {
  totalFindings: number;
  byLevel: Record<EvidenceLevel, number>;
  highestRiskLevel: EvidenceLevel;
  figuresAnalyzed: number;
  panelsAnalyzed: number;
}

type EvidenceLevel =
  | 'exact_duplicate'
  | 'near_duplicate'
  | 'partial_reuse'
  | 'possible_manipulation'
  | 'needs_review';

interface Finding {
  id: string;
  level: EvidenceLevel;
  score: number;
  algorithm: string;
  message: string;
  targetPanel: PanelRef;
  sourcePanel: PanelRef | null;
  heatmapPath: string | null;
  overlayPath: string | null;
  modelVersion: string;
  parameters: Record<string, unknown>;
  reviewStatus: 'pending' | 'confirmed' | 'false_positive' | 'needs_more_review';
  reviewedBy: string | null;
  reviewedAt: string | null;
}

interface PanelRef {
  panelId: string;
  figureId: string;
  articleId: string;
  imagePath: string;
  label: string;
  scope: 'submission' | 'public' | 'private';
}

interface PanelUsage {
  targetPanels: number;
  internalReferencePanels: number;
  externalReferencePanels: number;
  pubmedReferencePanels: number;
  estimatedCost: number | null;
}

// GET /api/projects/:id/report
// GET /api/reports/:id/export?format=html|pdf
```

**交付物**:
- 报告 Dashboard 页面
- 摘要统计卡片组（图表可视化风险分布）
- Finding 列表（过滤/排序/分页）
- Finding 详情抽屉（source/target 对比 + 参数表）
- 图像 Overlay 组件（两图叠加 + 透明度滑块）
- Heatmap 展示组件（热力图叠加在原图上）
- Panel 用量摘要组件
- 报告导出按钮（HTML/PDF）
- `useReport` + `useFindings` hooks

**验证标准**:
- 报告页面加载完整的 finding 列表
- 点击 finding 打开详情，source/target 并排对比
- Heatmap 正确叠加在原图上
- 过滤器正常工作（按等级、类型过滤）
- 导出 HTML 报告可下载

---

### 模块 FE-08: 人工复核与标注

**Scope**: 对 finding 进行人工标记（确认/误报/待进一步审查）、审计记录、专家服务入口。

**Anti-scope**: 不含专家排班系统、不含计费实现。

**交互**:
- 在报告 Finding 详情中内嵌标注控件
- 批量标记模式
- 标记历史时间线

**标注状态流转**:

```
pending → confirmed        (确认问题)
pending → false_positive   (标记误报)
pending → needs_more_review (需进一步审查)
confirmed ↔ false_positive (可修改)
any → expert_review_requested (提交专家复核)
```

**API 契约**:

```typescript
interface Annotation {
  id: string;
  findingId: string;
  status: ReviewStatus;
  note: string;
  reviewerName: string;
  createdAt: string;
}

type ReviewStatus =
  | 'pending'
  | 'confirmed'
  | 'false_positive'
  | 'needs_more_review'
  | 'expert_review_requested';

// PATCH /api/findings/:id/review
interface ReviewRequest {
  status: ReviewStatus;
  note?: string;
}

// GET /api/findings/:id/annotations
// → Annotation[] (审计 trail)
```

**交付物**:
- Finding 标注控件（状态按钮组 + 备注输入）
- 批量标记工具栏
- 标注历史时间线组件
- 专家复核请求对话框
- 复核进度统计（已标记/待标记/待专家确认）
- `useAnnotations` hook

**验证标准**:
- 标记 finding 为 confirmed → 状态更新
- 添加备注 → 历史时间线显示
- 批量选择 → 统一标记
- 已标记 finding 在列表中显示标注标签

---

## 3. Mock 数据策略

由于后端 API 尚未完全就绪，前端 demo 采用以下策略：

| 层级 | 策略 |
|------|------|
| 开发阶段 | MSW (Mock Service Worker) 拦截 API 请求，返回 fixture JSON |
| Mock 数据 | `frontend/src/mocks/` 目录下维护 fixture，与后端 domain model 对齐 |
| 查重接口 | 预留类型定义和 API 调用代码，但 mock 返回空结果或示例数据 |
| 渐进切换 | 通过环境变量 `NEXT_PUBLIC_USE_MOCK=true` 控制 mock 开关 |

Mock fixture 文件:
- `mocks/fixtures/users.json`
- `mocks/fixtures/projects.json`
- `mocks/fixtures/figures.json`
- `mocks/fixtures/panels.json`
- `mocks/fixtures/findings.json`
- `mocks/fixtures/report.json`
- `mocks/fixtures/pubmed-results.json`

## 4. 后端 API 层需求 (FastAPI)

前端 demo 需要后端提供以下最小 API：

| 端点 | 说明 | 优先级 |
|------|------|--------|
| `POST /auth/register` | 用户注册 | P0 |
| `POST /auth/login` | 用户登录 | P0 |
| `POST /auth/refresh` | Token 刷新 | P0 |
| `POST /upload/init` | tus 上传初始化 | P0 |
| `PATCH /upload/:id` | tus 分片上传 | P0 |
| `GET /projects` | 项目列表 | P0 |
| `POST /projects` | 创建项目 | P0 |
| `GET /projects/:id` | 项目详情 | P0 |
| `GET /projects/:id/figures` | Figure 列表 | P1 |
| `GET /projects/:id/panels` | Panel 列表 | P1 |
| `PATCH /panels/:id/confirm` | 确认 Panel | P1 |
| `GET /pubmed/search` | PubMed 搜索 | P1 |
| `POST /projects/:id/references/pubmed` | 添加 PubMed 参考 | P1 |
| `GET /projects/:id/report` | 获取报告 | P1 |
| `POST /ai/chat` | AI 咨询 (SSE) | P2 |
| `PATCH /findings/:id/review` | 标记 Finding | P2 |
| `GET /findings/:id/annotations` | 标注历史 | P2 |
| `GET /reports/:id/export` | 导出报告 | P2 |

**注意**: P0 为 demo 核心流程必须，P1 为核心功能，P2 为增强功能。前端全部使用 MSW mock 先行开发。

## 5. 设计系统

### 5.1 颜色语义

| 用途 | 色值 | 说明 |
|------|------|------|
| 主色 | `blue-600` | 品牌色、主操作 |
| 成功 | `green-600` | 确认、通过 |
| 警告 | `amber-500` | 需注意 |
| 危险 | `red-600` | 高风险 finding |
| 中性 | `slate-*` | 文本、边框、背景 |

### 5.2 Evidence Level 视觉映射

| Level | 颜色 | 图标 | 标签文案 |
|-------|------|------|----------|
| exact_duplicate | `red-600` | AlertCircle | 疑似完全重复 |
| near_duplicate | `orange-500` | AlertTriangle | 疑似近似重复 |
| partial_reuse | `amber-500` | Eye | 疑似局部复用 |
| possible_manipulation | `purple-600` | Shield | 疑似编辑痕迹 |
| needs_review | `blue-500` | HelpCircle | 需人工确认 |

### 5.3 关键 UI 模式

- **卡片模式**: 项目列表、figure 画廊、finding 列表均使用一致的卡片组件
- **侧边抽屉**: Finding 详情、AI 咨询使用右侧抽屉，保持主列表可见
- **分步引导**: 首次使用展示简要操作引导
- **空状态**: 每个列表页有清晰的空状态提示和引导操作
- **加载骨架**: 数据加载使用 Skeleton 而非 Spinner

## 6. Issue List

### Phase 1: 基础设施 (FE-01 + FE-02)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-01-01 | 初始化 Next.js 15 项目 + Tailwind + shadcn/ui | FE-01 | - | 2h |
| FE-01-02 | 全局布局组件（顶栏 + 可折叠侧边栏 + 面包屑） | FE-01 | FE-01-01 | 3h |
| FE-01-03 | API 客户端封装 + 统一错误处理 + 请求/响应拦截器 | FE-01 | FE-01-01 | 2h |
| FE-01-04 | TypeScript 类型定义（domain model + API 契约） | FE-01 | FE-01-01 | 2h |
| FE-01-05 | MSW Mock 服务 + fixture 数据生成 | FE-01 | FE-01-04 | 3h |
| FE-02-01 | NextAuth.js v5 配置 + Credentials provider | FE-02 | FE-01-03 | 3h |
| FE-02-02 | 登录页面 + 表单验证 | FE-02 | FE-02-01 | 2h |
| FE-02-03 | 注册页面 + 表单验证 | FE-02 | FE-02-01 | 2h |
| FE-02-04 | Auth 中间件 + 路由守卫 + 用户菜单组件 | FE-02 | FE-02-01 | 2h |

### Phase 2: 核心上传流程 (FE-03)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-03-01 | 项目列表页（CRUD + 状态展示 + 卡片/列表视图） | FE-03 | FE-02-04 | 3h |
| FE-03-02 | 创建项目对话框 + 项目详情总览页 | FE-03 | FE-03-01 | 2h |
| FE-03-03 | tus 上传封装（断点续传 + 并发控制 + 进度回调） | FE-03 | FE-01-03 | 4h |
| FE-03-04 | PDF 上传页面（Target 区 + Reference 区 + 拖拽上传） | FE-03 | FE-03-03 | 4h |
| FE-03-05 | 上传状态管理 + 处理进度轮询 + 文件列表组件 | FE-03 | FE-03-04 | 3h |

### Phase 3: Figure/Panel 展示 + PubMed (FE-04 + FE-05)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-04-01 | Figure 画廊组件（网格视图 + 分组展示 + 缩略图） | FE-04 | FE-03-05 | 3h |
| FE-04-02 | PDF 页面预览 + Figure bbox overlay (react-pdf + react-konva) | FE-04 | FE-04-01 | 5h |
| FE-04-03 | Panel 切分可视化 + 确认/调整交互 | FE-04 | FE-04-01 | 5h |
| FE-04-04 | Panel 统计摘要组件 + 费用预估 | FE-04 | FE-04-03 | 2h |
| FE-05-01 | PubMed 搜索组件（输入 + 结果列表 + 分页） | FE-05 | FE-01-03 | 3h |
| FE-05-02 | PubMed 文章选取 + 添加为项目 reference | FE-05 | FE-05-01, FE-03-01 | 3h |

### Phase 4: 报告与 AI 咨询 (FE-06 + FE-07 + FE-08)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-07-01 | 报告 Dashboard + 摘要统计卡片 + 风险分布图 | FE-07 | FE-04-03 | 4h |
| FE-07-02 | Finding 列表组件（过滤/排序/分页 + 等级颜色标签） | FE-07 | FE-07-01 | 3h |
| FE-07-03 | Finding 详情抽屉（Source/Target 并排 + 参数表） | FE-07 | FE-07-02 | 4h |
| FE-07-04 | 图像 Overlay + Heatmap 叠加组件 | FE-07 | FE-07-03 | 4h |
| FE-07-05 | 报告导出（HTML/PDF 下载） | FE-07 | FE-07-01 | 3h |
| FE-06-01 | AI 咨询聊天界面 + 流式输出渲染 (Vercel AI SDK) | FE-06 | FE-01-03 | 4h |
| FE-06-02 | 证据引用卡片 + Finding 跳转 + 预设问题按钮 | FE-06 | FE-06-01, FE-07-02 | 3h |
| FE-06-03 | 咨询历史记录 + 额度追踪 | FE-06 | FE-06-01 | 2h |
| FE-08-01 | Finding 标注控件 + 状态流转 + 备注输入 | FE-08 | FE-07-03 | 3h |
| FE-08-02 | 批量标记工具栏 + 标注时间线 + 复核进度统计 | FE-08 | FE-08-01 | 3h |
| FE-08-03 | 专家复核请求对话框 | FE-08 | FE-08-01 | 2h |

### 汇总

| Phase | Issue 数 | 预估总时间 |
|-------|----------|-----------|
| Phase 1: 基础设施 | 9 | ~21h |
| Phase 2: 核心上传 | 5 | ~16h |
| Phase 3: 展示 + PubMed | 6 | ~21h |
| Phase 4: 报告与 AI | 11 | ~35h |
| **总计** | **31** | **~93h** |

## 7. 实施优先级与依赖图

```
Phase 1 ──────────────────────────────────────────
FE-01-01 → FE-01-02
         → FE-01-03 → FE-02-01 → FE-02-02
                                → FE-02-03
                                → FE-02-04
         → FE-01-04 → FE-01-05

Phase 2 ──────────────────────────────────────────
FE-02-04 → FE-03-01 → FE-03-02
FE-01-03 → FE-03-03 → FE-03-04 → FE-03-05

Phase 3 ──────────────────────────────────────────
FE-03-05 → FE-04-01 → FE-04-02
                     → FE-04-03 → FE-04-04
FE-01-03 → FE-05-01 → FE-05-02

Phase 4 ──────────────────────────────────────────
FE-04-03 → FE-07-01 → FE-07-02 → FE-07-03 → FE-07-04
                                            → FE-08-01 → FE-08-02
                                                       → FE-08-03
         → FE-07-05
FE-01-03 → FE-06-01 → FE-06-02
                     → FE-06-03
```

## 8. 注意事项

1. **查重接口预留**: 所有查重相关的类型定义和 API 调用方法在代码中完整定义，但实际调用返回 mock 数据。待独立查重 API 就绪后，只需切换 endpoint 和移除 mock。

2. **与后端 domain model 对齐**: 前端 TypeScript 类型须与 `src/paper_image/domain.py` 中的 `CorpusScope`, `EvidenceLevel`, `ArticleRecord`, `FigureRecord`, `PanelRecord`, `AnalysisFinding`, `AICallRecord` 保持语义一致。

3. **Review-safe language**: 报告 UI 中所有文案不得使用定性判断（如"存在问题"），只展示证据和分数。遵循后端 `review/report` 模块的 language profile。

4. **隐私约束**: 前端不在 URL 参数中暴露论文内容或用户信息。图片通过签名 URL 访问。

5. **响应式设计**: 优先保证 1280px+ 桌面体验，1024px 以上可用。不要求移动端适配。

6. **性能预算**: 首屏 LCP < 2s，TTI < 3s。大图片使用 Next.js Image 组件 + WebP 格式。
