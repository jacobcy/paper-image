# 前端 Phase 2 路线图 — 运营支撑体系

> 本文档是 `frontend-demo-spec.md` 的补充。Phase 1 (FE-01 ~ FE-08) 覆盖了终端用户核心流程，本文档补充运营、管理和服务支撑所需的缺失模块。

## 1. 缺口分析

### 1.1 当前覆盖 vs 缺失

| 能力 | 当前状态 | 缺口说明 |
|------|----------|----------|
| 用户认证 | FE-02 ✅ 已有登录/注册 | 需调整：注册后不自动开通服务，进入"待激活"状态 |
| 项目管理 | FE-03 ✅ | - |
| PDF 上传 | FE-03 ✅ | - |
| Figure/Panel | FE-04 ✅ | - |
| PubMed | FE-05 ✅ | - |
| AI 咨询 | FE-06 ✅ | - |
| 报告 | FE-07 ✅ | - |
| 人工标注 | FE-08 ✅ | - |
| **管理后台** | ❌ 缺失 | 创建/管理用户、分配配额、查看系统使用情况 |
| **组织/实验室管理** | ❌ 缺失 | 实验室实体、团队成员、共享 corpus |
| **配额与套餐管理** | ❌ 缺失 | 套餐分配、用量追踪、超额提醒（无支付） |
| **客服系统** | ❌ 缺失 | 工单、服务开通申请、在线咨询 |
| **落地页 / 公开展示** | ❌ 缺失 | 产品介绍、定价展示、联系/试用申请 |
| **通知系统** | ❌ 缺失 | 处理完成、配额告警、系统公告 |
| **操作审计** | ❌ 缺失 | 管理员操作日志、用户行为统计 |
| **帮助中心** | ❌ 缺失 | FAQ、使用指南、联系方式 |

### 1.2 商业模式对架构的影响

根据产品方案和定价策略，本系统的用户获取模式是 **B2B 为主 + B2C 辅助**：

```
实验室/机构路径:
  签订合作协议 → 管理员创建组织 → 分配套餐配额
    → 管理员创建用户账号 → 用户收到激活邮件 → 登录使用

个人用户路径:
  用户在销售平台购买 → 客服确认订单 → 管理员创建账号
    → 用户收到激活邮件 → 登录使用

自助注册路径（保留）:
  用户自行注册 → 状态为"待激活" → 联系客服开通
    → 管理员激活并分配套餐 → 用户可使用
```

**关键约束**：
- 不接支付接口
- 注册不等于开通服务
- 配额由管理员手动分配
- 计费按 panel 统计，由管理员在后台查看用量报表

## 2. 补充模块 Spec

---

### 模块 FE-09: 管理后台框架

**Scope**: 管理后台独立布局、管理员认证、Dashboard 首页、导航体系。

**Anti-scope**: 不含具体管理功能（用户/配额/组织管理在各自模块实现）。

**设计决策**:
- 管理后台路由统一前缀 `/admin`
- 管理后台使用独立布局（与用户端 dashboard 区分），侧边栏项不同
- 复用 shadcn/ui 组件，风格保持一致
- 仅 `role: admin` 可访问

**页面**:
- `/admin` — 管理面板首页（系统概览）
- 侧边栏：用户管理、组织管理、配额管理、工单管理、系统设置、操作日志

**管理面板首页内容**:
- 统计卡片：总用户数、活跃组织数、本月报告数、本月 panel 消耗量
- 最近注册/待激活用户列表
- 最近工单列表
- 配额告警列表（接近上限的组织）

**API 契约**:

```typescript
// GET /api/admin/dashboard
interface AdminDashboard {
  totalUsers: number;
  activeOrganizations: number;
  monthlyReports: number;
  monthlyPanelUsage: number;
  pendingActivations: User[];
  recentTickets: Ticket[];
  quotaAlerts: QuotaAlert[];
}
```

**交付物**:
- `/admin` 布局 + 路由守卫（admin only）
- Admin Dashboard 首页
- Admin 侧边栏导航

---

### 模块 FE-10: 用户与组织管理

**Scope**: 管理员创建/编辑/禁用用户，创建/管理组织（实验室），将用户归属到组织。

**Anti-scope**: 不含配额分配（FE-11）、不含支付。

**核心概念**:

| 概念 | 说明 |
|------|------|
| User | 系统用户，可属于一个组织 |
| Organization | 实验室/机构实体，拥有多个用户和共享 corpus |
| Account Status | `pending`(待激活) / `active`(已激活) / `suspended`(已暂停) / `expired`(已过期) |
| Role | `admin`(管理员) / `org_admin`(组织管理员) / `user`(普通用户) |

**页面**:
- `/admin/users` — 用户列表（搜索、过滤、创建）
- `/admin/users/[id]` — 用户详情（编辑、状态变更、关联组织）
- `/admin/organizations` — 组织列表
- `/admin/organizations/[id]` — 组织详情（成员列表、基本信息）

**创建用户流程**:

```
管理员点击"创建用户"
  → 填写：email、姓名、组织（可选）、角色、初始状态（active/pending）
  → 系统生成临时密码或激活链接
  → 可选：发送激活邮件
  → 用户首次登录时修改密码
```

**自助注册用户激活流程**:

```
用户自行注册 → status = "pending"
  → 管理员在待激活列表看到
  → 管理员选择：激活（分配组织 + 套餐） / 拒绝
  → 激活后用户可使用
```

**API 契约**:

```typescript
interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: "admin" | "org_admin" | "user";
  status: "pending" | "active" | "suspended" | "expired";
  organizationId: string | null;
  organizationName: string | null;
  quotaPlan: string | null;
  lastLoginAt: string | null;
  createdAt: string;
  createdBy: string;  // 创建者（admin ID 或 "self-register"）
}

interface Organization {
  id: string;
  name: string;
  contactEmail: string;
  contactName: string;
  agreementType: "trial" | "starter" | "standard" | "pro" | "institution" | "custom";
  agreementStartDate: string;
  agreementEndDate: string | null;
  memberCount: number;
  maxMembers: number;
  createdAt: string;
  notes: string;
}

// POST /api/admin/users           — 创建用户
// PATCH /api/admin/users/:id      — 编辑用户
// POST /api/admin/users/:id/activate   — 激活用户
// POST /api/admin/users/:id/suspend    — 暂停用户
// POST /api/admin/organizations   — 创建组织
// PATCH /api/admin/organizations/:id — 编辑组织
// POST /api/admin/organizations/:id/members — 添加成员
```

**交付物**:
- 用户列表页（表格 + 搜索 + 状态过滤）
- 创建用户 Dialog
- 用户详情页（编辑 + 状态操作）
- 待激活用户快速操作列表
- 组织列表页
- 创建组织 Dialog
- 组织详情页（成员管理）

---

### 模块 FE-11: 配额与套餐管理

**Scope**: 管理员为用户/组织分配套餐、查看用量、配额告警。

**Anti-scope**: 不含支付接口、不含自动扣费、不含发票。

**套餐类型（对齐 `pricing-strategy.md`）**:

| 套餐 ID | 名称 | 适用对象 |
|---------|------|----------|
| `personal_s` | 个人 S | 个人用户 |
| `personal_m` | 个人 M | 个人用户 |
| `personal_l` | 个人 L | 个人用户 |
| `lab_single` | 实验室单篇 | 实验室用户 |
| `lab_starter` | Lab Starter 年度 | 组织 |
| `lab_standard` | Lab Standard 年度 | 组织 |
| `lab_pro` | Lab Pro 年度 | 组织 |
| `institution` | 机构定制 | 组织 |
| `custom` | 自定义 | 任意 |

**页面**:
- `/admin/quotas` — 配额总览（所有用户/组织的配额状态）
- `/admin/quotas/assign` — 分配套餐
- `/admin/organizations/[id]/usage` — 组织用量详情

**配额分配流程**:

```
管理员选择用户或组织
  → 选择套餐类型
  → 设置有效期（开始/结束日期）
  → 可自定义覆盖额度（reports、target panels、reference panels、AI tokens、expert reviews）
  → 保存分配记录
```

**用量追踪 Dashboard**:
- 各维度已用 / 总额度柱状图：
  - 报告数
  - Target panel 数
  - Reference panel 数
  - AI 咨询 token
  - 专家确认次数
- 用量趋势折线图（按月）
- 超额组织告警列表

**API 契约**:

```typescript
interface QuotaAssignment {
  id: string;
  targetType: "user" | "organization";
  targetId: string;
  targetName: string;
  planId: string;
  planName: string;
  validFrom: string;
  validTo: string | null;
  limits: QuotaLimits;
  usage: QuotaUsage;
  status: "active" | "expired" | "exhausted";
}

interface QuotaLimits {
  maxReports: number;
  maxTargetPanels: number;
  maxReferencePanels: number;
  maxAiTokens: number;        // 万 token
  maxExpertReviews: number;
  maxPubmedTopics: number;
  maxMembers: number;
}

interface QuotaUsage {
  usedReports: number;
  usedTargetPanels: number;
  usedReferencePanels: number;
  usedAiTokens: number;
  usedExpertReviews: number;
  usedPubmedTopics: number;
}

interface QuotaAlert {
  organizationId: string;
  organizationName: string;
  dimension: string;           // "target_panels" | "ai_tokens" 等
  usagePercent: number;
  message: string;
}
```

**交付物**:
- 配额分配页面（套餐选择 + 自定义额度 + 有效期）
- 配额总览页（全局视图）
- 组织用量详情页（图表 + 明细）
- 配额告警列表
- 用户端：侧边栏底部配额摘要组件

---

### 模块 FE-12: 客服与工单系统

**Scope**: 用户提交服务开通申请/问题工单，管理员处理工单，在线消息沟通。

**Anti-scope**: 不含实时语音/视频、不含第三方客服平台集成（后续可扩展）。

**工单类型**:

| 类型 | 说明 | 触发场景 |
|------|------|----------|
| `activation` | 服务开通申请 | 自助注册后申请开通 |
| `quota_increase` | 配额增加请求 | 配额不足时申请 |
| `expert_review` | 专家复核请求 | 报告页提交专家请求 |
| `technical` | 技术问题 | 使用中遇到问题 |
| `general` | 一般咨询 | 价格、合作等咨询 |

**工单状态流转**:

```
open → in_progress → resolved → closed
     → waiting_user (等待用户回复)
     → waiting_admin (等待管理员回复)
```

**用户端页面**:
- `/support` — 我的工单列表 + 新建工单
- `/support/[id]` — 工单详情（消息时间线 + 回复）
- 全局右下角"帮助与支持"浮窗按钮

**管理端页面**:
- `/admin/tickets` — 工单列表（按状态/类型/紧急度过滤）
- `/admin/tickets/[id]` — 工单处理（回复 + 状态变更 + 关联操作）

**服务开通申请工单**（特殊流程）:

```
用户注册后状态为 pending
  → 用户看到"您的账号待激活，请提交服务开通申请"提示
  → 用户点击提交开通申请 → 自动创建 activation 类型工单
  → 管理员看到工单 → 确认信息（姓名、机构、用途）
  → 管理员操作：激活用户 + 分配套餐
  → 工单自动关闭 → 用户收到通知
```

**API 契约**:

```typescript
interface Ticket {
  id: string;
  type: "activation" | "quota_increase" | "expert_review" | "technical" | "general";
  subject: string;
  status: "open" | "in_progress" | "waiting_user" | "waiting_admin" | "resolved" | "closed";
  priority: "low" | "medium" | "high";
  userId: string;
  userName: string;
  organizationId: string | null;
  messages: TicketMessage[];
  createdAt: string;
  updatedAt: string;
  resolvedAt: string | null;
}

interface TicketMessage {
  id: string;
  senderId: string;
  senderName: string;
  senderRole: "user" | "admin";
  content: string;
  createdAt: string;
}

// POST /api/tickets           — 创建工单
// GET  /api/tickets           — 我的工单列表（用户）
// GET  /api/admin/tickets     — 全部工单列表（管理员）
// POST /api/tickets/:id/reply — 回复工单
// PATCH /api/tickets/:id/status — 变更状态
```

**交付物**:
- 用户端：工单列表 + 新建工单 Dialog + 工单详情（消息时间线）
- 管理端：工单列表（过滤/排序）+ 工单处理页（回复 + 状态操作 + 快速关联操作）
- 全局帮助浮窗按钮
- 自助注册后的"待激活"引导页

---

### 模块 FE-13: 落地页与公开展示

**Scope**: 产品介绍页、定价展示、联系/试用申请表单，未登录可见。

**Anti-scope**: 不含 CMS、不含博客、不含 SEO 优化。

**页面**:
- `/` — 首页（产品介绍 + 核心功能 + CTA）
- `/pricing` — 定价页（对齐 `pricing-strategy.md` 中的 SKU）
- `/contact` — 联系我们 / 申请试用

**首页结构**:
- Hero 区：标题 + 副标题 + "申请试用" / "登录" 按钮
- 核心功能区（4 个卡片）：图像复用检测 / Panel 级精细分析 / AI 科研诚信报告 / 私有库管理
- 工作流程图：上传 → 提取 → 分析 → 报告
- 信任标记：review-safe language 声明
- Footer：联系方式、法律声明

**定价页结构**:
- 三个首发 SKU 卡片（个人 AI 初筛 / 实验室单篇 / Lab Starter 年度）
- 功能对比表
- "联系我们获取定制方案" CTA
- FAQ 折叠区

**联系/申请表**:
- 姓名、邮箱、机构、用途描述
- 提交后创建 `general` 类型工单
- 显示"我们将在 1 个工作日内联系您"

**交付物**:
- `/` 首页（响应式）
- `/pricing` 定价页
- `/contact` 联系/申请页
- 公共 layout（TopNav 不含用户菜单，显示"登录"按钮）

---

### 模块 FE-14: 通知系统

**Scope**: 站内通知（铃铛 icon + 通知列表），覆盖处理完成、配额告警、工单回复、系统公告。

**Anti-scope**: 不含邮件发送（后端负责）、不含 Push Notification。

**通知类型**:

| 类型 | 触发场景 | 接收者 |
|------|----------|--------|
| `processing_complete` | PDF/报告处理完成 | 用户 |
| `quota_warning` | 配额使用超 80% | 用户 + 组织管理员 |
| `quota_exhausted` | 配额耗尽 | 用户 + 组织管理员 |
| `ticket_reply` | 工单有新回复 | 工单发起者 |
| `account_activated` | 账号已激活 | 用户 |
| `system_announcement` | 系统维护/功能更新 | 所有用户 |

**UI 组件**:
- TopNav 右侧铃铛 icon + 未读数 badge
- 点击展开通知下拉面板（最近 20 条）
- "查看全部"跳转通知列表页
- 每条通知：图标 + 标题 + 时间 + 已读/未读
- 点击通知跳转到对应页面（项目/工单/配额）

**API 契约**:

```typescript
interface Notification {
  id: string;
  type: string;
  title: string;
  body: string;
  read: boolean;
  link: string | null;     // 跳转 URL
  createdAt: string;
}

// GET  /api/notifications        — 通知列表
// PATCH /api/notifications/:id/read — 标记已读
// POST /api/notifications/read-all  — 全部标记已读
```

**交付物**:
- 通知铃铛 + 下拉面板组件
- 通知列表页 `/notifications`
- `useNotifications` hook（轮询 + 未读计数）
- 集成进 TopNav

---

### 模块 FE-15: 帮助中心

**Scope**: 静态 FAQ 页面、使用指南、联系方式展示。

**Anti-scope**: 不含动态内容管理、不含搜索引擎。

**页面**:
- `/help` — 帮助中心首页
- `/help/guide` — 使用指南（分步骤）
- `/help/faq` — 常见问题（折叠 Accordion）

**FAQ 内容（初始）**:
- 如何上传论文？
- Target PDF 和 Reference PDF 有什么区别？
- Panel 切分结果不正确怎么办？
- 报告中的证据等级是什么意思？
- 如何使用 AI 咨询？
- 如何申请专家复核？
- 配额用完了怎么办？
- 如何联系客服？

**交付物**:
- `/help` 首页
- `/help/guide` 使用指南
- `/help/faq` FAQ 页

---

## 3. 对现有模块的修改

### FE-02 Auth 模块调整

当前 FE-02 的注册流程默认注册即开通。根据新业务模型需要调整：

| 变更 | 说明 |
|------|------|
| 注册后状态 | 默认 `status: "pending"`，不是 `"active"` |
| 注册成功页 | 不跳转 `/projects`，而是显示"待激活"引导页 |
| 待激活引导页 | 告知用户：联系客服开通 / 提交服务开通申请 / 显示客服联系方式 |
| 登录后检查 | `status === "pending"` 时只能看到待激活页和工单页，不能使用筛查功能 |
| 中间件更新 | 增加 `active` 状态检查：pending 用户只能访问 `/pending`, `/support`, `/help` |

**新增 Issue**: FE-02-05（Auth 状态流调整）

### FE-08 标注模块调整

当前 FE-08-03（专家复核请求）是纯 UI 占位。需要与工单系统联动：

| 变更 | 说明 |
|------|------|
| 提交专家请求 | 同时创建 `expert_review` 类型工单 |
| 工单关联 | 专家请求状态与工单状态联动 |

**不新增 Issue**：在 FE-12 工单系统中处理此联动。

## 4. 用户角色与权限矩阵

| 页面/功能 | admin | org_admin | user (active) | user (pending) |
|-----------|-------|-----------|---------------|----------------|
| 落地页 `/`, `/pricing`, `/contact` | ✅ | ✅ | ✅ | ✅ |
| 帮助中心 `/help` | ✅ | ✅ | ✅ | ✅ |
| 工单系统 `/support` | ✅ | ✅ | ✅ | ✅ |
| Dashboard + 筛查功能 | ✅ | ✅ | ✅ | ❌ |
| 组织成员管理 | ✅ | ✅ (本组织) | ❌ | ❌ |
| 管理后台 `/admin` | ✅ | ❌ | ❌ | ❌ |

## 5. 补充 Issue List

### Phase 5: 管理后台基础 (FE-09 + FE-10)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-09-01 | 管理后台布局 + 路由守卫 + Dashboard 首页 | FE-09 | FE-02-04 | 3h |
| FE-10-01 | 用户列表页（表格 + 搜索 + 状态过滤） | FE-10 | FE-09-01 | 3h |
| FE-10-02 | 创建用户 Dialog + 激活/暂停操作 | FE-10 | FE-10-01 | 3h |
| FE-10-03 | 组织列表页 + 创建组织 + 组织详情（成员管理） | FE-10 | FE-10-01 | 4h |
| FE-02-05 | Auth 状态流调整（pending 状态 + 待激活引导页） | FE-02 | FE-02-04 | 3h |

### Phase 6: 配额与客服 (FE-11 + FE-12)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-11-01 | 套餐分配页面 + 配额自定义表单 | FE-11 | FE-10-03 | 4h |
| FE-11-02 | 配额总览 + 用量图表 + 告警列表 | FE-11 | FE-11-01 | 4h |
| FE-11-03 | 用户端配额摘要组件（侧边栏 + 配额详情页） | FE-11 | FE-11-01 | 2h |
| FE-12-01 | 工单系统 — 用户端（创建 + 列表 + 详情 + 消息回复） | FE-12 | FE-01-03 | 4h |
| FE-12-02 | 工单系统 — 管理端（列表 + 处理 + 状态变更 + 快速关联操作） | FE-12 | FE-12-01, FE-09-01 | 4h |
| FE-12-03 | 服务开通申请流程（注册 → 待激活 → 提交申请 → 管理员处理） | FE-12 | FE-12-01, FE-02-05 | 3h |

### Phase 7: 公开页面与通知 (FE-13 + FE-14 + FE-15)

| Issue ID | 标题 | 模块 | 依赖 | 预估 |
|----------|------|------|------|------|
| FE-13-01 | 落地页首页（Hero + 功能介绍 + 工作流程图） | FE-13 | FE-01-01 | 4h |
| FE-13-02 | 定价页（三个 SKU 卡片 + 功能对比表 + FAQ） | FE-13 | FE-13-01 | 3h |
| FE-13-03 | 联系/申请页（表单 + 工单联动） | FE-13 | FE-13-01, FE-12-01 | 2h |
| FE-14-01 | 通知铃铛 + 下拉面板 + 通知列表页 | FE-14 | FE-01-02 | 3h |
| FE-15-01 | 帮助中心（首页 + 使用指南 + FAQ） | FE-15 | FE-01-01 | 3h |

### Phase 2 汇总

| Phase | Issue 数 | 预估总时间 |
|-------|----------|-----------|
| Phase 5: 管理后台基础 | 5 | ~16h |
| Phase 6: 配额与客服 | 6 | ~21h |
| Phase 7: 公开页面与通知 | 5 | ~15h |
| **Phase 2 总计** | **16** | **~52h** |

## 6. 全局依赖图更新

```
Phase 1 (FE-01~08) ──────────────────────────────
  [现有 31 issues, ~93h]

Phase 5 (管理后台) ───────────────────────────────
  FE-02-04 → FE-09-01 (管理后台布局)
           → FE-10-01 → FE-10-02 (用户管理)
                      → FE-10-03 (组织管理)
  FE-02-04 → FE-02-05 (Auth 状态流调整)

Phase 6 (配额与客服) ─────────────────────────────
  FE-10-03 → FE-11-01 → FE-11-02 (配额管理)
                       → FE-11-03 (用户端配额)
  FE-01-03 → FE-12-01 → FE-12-02 (工单管理端)
                       → FE-12-03 (开通流程)
  FE-02-05 → FE-12-03

Phase 7 (公开页面) ───────────────────────────────
  FE-01-01 → FE-13-01 → FE-13-02
                       → FE-13-03
  FE-01-02 → FE-14-01
  FE-01-01 → FE-15-01
```

## 7. Milestone 规划

| Milestone | 内容 | 建议截止 |
|-----------|------|---------|
| Phase 5: Admin Foundation | FE-09 + FE-10 + FE-02-05 | 2026-07-15 |
| Phase 6: Quota & Support | FE-11 + FE-12 | 2026-07-31 |
| Phase 7: Public & Notifications | FE-13 + FE-14 + FE-15 | 2026-08-15 |

## 8. 对后端 API 的额外需求

Phase 2 补充模块需要后端新增以下 API（前端先用 MSW mock）：

| 端点 | 说明 | 优先级 |
|------|------|--------|
| `GET /admin/dashboard` | 管理面板概览 | P0 |
| `GET/POST/PATCH /admin/users` | 用户 CRUD + 状态变更 | P0 |
| `POST /admin/users/:id/activate` | 激活用户 | P0 |
| `GET/POST/PATCH /admin/organizations` | 组织 CRUD | P0 |
| `POST /admin/organizations/:id/members` | 添加成员 | P0 |
| `GET/POST /admin/quotas` | 配额分配 | P0 |
| `GET /admin/quotas/:id/usage` | 用量查询 | P1 |
| `GET/POST /tickets` | 工单 CRUD | P1 |
| `POST /tickets/:id/reply` | 工单回复 | P1 |
| `GET/PATCH /notifications` | 通知 CRUD | P2 |
