# FE-01-01: 初始化 Next.js 15 项目 + Tailwind CSS 4 + shadcn/ui

## Plan Summary
基于已有 `frontend/` 骨架目录完成前端项目初始化：修正无效依赖、安装所有包、通过 shadcn CLI 初始化组件库并安装 16 个核心组件，最终验证 dev server 正常启动。

## Current State (Facts)
- **骨架目录**：`frontend/` 包含完整的路由结构、类型定义、mock fixtures、Tailwind v4 基础配置
- **`tsconfig.json`**：`@/*` 别名已指向 `./src/*`
- **`src/lib/utils.ts`**：`cn()` 函数已存在（shadcn 要求的工具函数）
- **`globals.css`**：使用 `@import "tailwindcss"`（TW4 语法）+ shadcn CSS 变量（`:root` 中定义）
- **`postcss.config.mjs`**：使用 `@tailwindcss/postcss`（TW4 插件）
- **`tailwind.config.ts`**：使用 TW3 风格的 `content` + `theme.extend`，与 TW4 CSS-first 模式可能冲突
- **`node_modules/` 不存在**：依赖未安装
- **`components.json` 不存在**：shadcn 未初始化
- **`src/components/ui/` 不存在**：无 shadcn 组件

## Changes

| File | Action | Reason |
|------|--------|--------|
| `frontend/package.json` | Modify | 移除不存在的 Radix 包，避免 install 失败 |
| `frontend/pnpm-lock.yaml` | Create | `pnpm install` 生成 |
| `frontend/.env.local` | Create | 从 `.env.example` 复制 |
| `frontend/components.json` | Create | `shadcn init` 生成 |
| `frontend/src/components/ui/*.tsx` | Create | `shadcn add` 安装各组件 |
| `frontend/src/app/globals.css` | Possibly modify | shadcn init 可能注入 `@theme` 指令 |
| `frontend/tailwind.config.ts` | Possibly delete/modify | TW4 CSS-first 模式下 shadcn 可能要求调整 |

## Implementation Steps

### Step 1: 修正 package.json 中的无效依赖
- **Files**: `frontend/package.json`
- **Effort**: S
- **Dependencies**: none

从 `dependencies` 中移除以下两个不存在的 npm 包：
- `@radix-ui/react-badge` — shadcn Badge 是纯样式组件，不依赖 Radix 原语
- `@radix-ui/react-sheet` — shadcn Sheet 底层使用 `@radix-ui/react-dialog`，此包不存在

```bash
cd frontend
# 用编辑器移除这两行后验证 JSON 有效
node -e "JSON.parse(require('fs').readFileSync('package.json'))" && echo "valid"
```

**验证**: `grep -c 'react-badge\|react-sheet' package.json` 返回 0

### Step 2: 安装依赖
- **Files**: `frontend/package.json` (unchanged), `frontend/pnpm-lock.yaml` (created)
- **Effort**: S
- **Dependencies**: Step 1

```bash
cd frontend && pnpm install
```

**验证**: `pnpm-lock.yaml` 存在，终端无 error（peer dependency warnings 可接受）

### Step 3: 创建 `.env.local`
- **Files**: `frontend/.env.local`
- **Effort**: S
- **Dependencies**: none (可与 Step 2 并行)

```bash
cd frontend && cp .env.example .env.local
```

**验证**: `diff .env.example .env.local` 无差异

### Step 4: 初始化 shadcn/ui
- **Files**: `frontend/components.json`, `frontend/src/app/globals.css` (可能修改), `frontend/tailwind.config.ts` (可能修改/删除)
- **Effort**: M
- **Dependencies**: Step 2

```bash
cd frontend && pnpm dlx shadcn@latest init
```

交互式配置参考（具体选项取决于 CLI 版本）：
- Style: **New York**（与设计系统 slate 中性色一致）
- Base color: **Slate** 或 **Neutral**
- CSS variables: **Yes**
- 使用现有 `globals.css` 和 `src/lib/utils.ts`

**关键决策点**：
- 如果 shadcn init 询问是否覆盖 `globals.css`：选择保留现有 CSS 变量（已包含完整的 shadcn 颜色体系）
- 如果 shadcn init 报 `tailwind.config.ts` 与 TW4 冲突：按 CLI 建议处理（可能需要删除 `tailwind.config.ts`，将主题配置迁移到 `globals.css` 的 `@theme` 块）
- 如果 shadcn init 要求 `globals.css` 中添加 `@theme inline` 指令：接受，这是 TW4 的正确做法

**回退方案**（如果 CLI 初始化失败）：
1. 手动创建 `components.json`：
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  }
}
```
2. 确保 `src/components/ui/` 目录存在

**验证**: `cat components.json` 显示有效 JSON 配置

### Step 5: 安装核心 shadcn 组件
- **Files**: `frontend/src/components/ui/*.tsx`
- **Effort**: M
- **Dependencies**: Step 4

```bash
cd frontend && pnpm dlx shadcn@latest add button card input label badge avatar separator skeleton toast dialog sheet tabs select popover dropdown-menu scroll-area slider
```

一次性安装 16 个组件。

**关于 Badge 和 Sheet**：
- Badge：纯样式组件，shadcn CLI 会生成不依赖 Radix 原语的组件文件
- Sheet：shadcn 内部使用 `@radix-ui/react-dialog` 实现，CLI 会自动处理依赖

**验证**:
```bash
ls src/components/ui/ | wc -l
# 应 ≥ 16（每个组件一个或多个文件）
ls src/components/ui/button.tsx
# 确认 Button 组件存在
```

### Step 6: 验证 Button 可 import
- **Files**: none (read-only verification)
- **Effort**: S
- **Dependencies**: Step 5

```bash
cd frontend && pnpm exec tsc --noEmit --skipLibCheck
```

或快速验证：
```bash
cd frontend && node -e "require('./src/components/ui/button.tsx')" 2>/dev/null || pnpm exec tsc --noEmit
```

**验证**: TypeScript 编译通过，无 `cannot find module '@/components/ui/button'` 错误

### Step 7: 全量验证
- **Files**: none (read-only verification)
- **Effort**: S
- **Dependencies**: Step 5

```bash
cd frontend
pnpm type-check    # tsc --noEmit
pnpm lint          # next lint
pnpm dev           # next dev --turbopack
```

**验证标准**:
- `pnpm type-check` exit code 0
- `pnpm lint` 无 error（warnings 可接受，记录在 handoff 中）
- `pnpm dev` 启动后访问 `localhost:3000`：
  - 页面加载无白屏
  - 浏览器控制台无 Tailwind/shadcn 相关 error
  - 当前首页 redirect 到 `/login`，login stub 渲染正常即可
  - 验证后可停止 dev server

## Test Scope

**策略 B（定向）**：本任务为基础设施初始化，不涉及业务逻辑测试。

- 无需运行 `vitest` 或 `playwright`
- 验证通过 `pnpm type-check`、`pnpm lint`、`pnpm dev` 完成
- 如果 type-check/lint 暴露其他骨架代码的问题（非本任务引入），用 handoff 记录，不在本任务 scope 内修复

## Risks & Considerations

### Risk 1: Tailwind CSS 4 + shadcn/ui 兼容性 (HIGH)
**问题**: shadcn 传统上基于 TW3 设计。TW4 采用 CSS-first 配置，`tailwind.config.ts` 的 `content` 和 `theme.extend` 语义不同。
**影响**: shadcn init 可能无法正确检测 TW4 配置，或生成的组件样式不生效。
**缓解**: shadcn@latest（2025+）已支持 TW4。如果 init 报错，使用 Step 4 的回退方案手动创建 `components.json`。
**验证**: Step 7 中 `pnpm dev` 启动后检查页面样式是否正确渲染。

### Risk 2: `tailwind.config.ts` 与 TW4 冲突 (MEDIUM)
**问题**: 现有 `tailwind.config.ts` 使用 TW3 风格的 `satisfies Config`、`content` 数组和 `theme.extend`。TW4 使用 `@tailwindcss/postcss` 时可能忽略此文件或产生双重配置冲突。
**影响**: shadcn 组件的样式 token（如 `bg-primary`、`text-muted-foreground`）可能不生效。
**缓解**: shadcn init 时观察是否建议删除或修改 `tailwind.config.ts`。如有需要，将主题配置迁移到 `globals.css` 的 `@theme` 块中。
**验证**: Step 7 中 Button 组件的 `variant="default"` 应显示蓝色背景（`--primary` 定义为 `221.2 83.2% 53.3%`）。

### Risk 3: `@apply` 在 TW4 中的行为 (LOW)
**问题**: `globals.css` 使用 `@apply border-border` 和 `@apply bg-background text-foreground`。TW4 中 `@apply` 行为可能有变化。
**影响**: 全局边框和背景色可能不生效。
**缓解**: Step 7 中检查浏览器渲染是否正常。如有问题，改用原生 CSS 属性引用。

### Risk 4: ESLint flat config 迁移 (LOW)
**问题**: `.eslintrc.json` 使用 ESLint 8 格式，但 `eslint: ^9.17.0` 默认使用 flat config。
**影响**: `pnpm lint` 可能输出 deprecation warning。
**缓解**: `eslint-config-next` 在当前版本仍支持 `.eslintrc.json`。warnings 可接受，用 handoff 记录供后续 issue 处理。

### Risk 5: pnpm install 因其他依赖失败 (LOW)
**问题**: `react-konva`、`react-pdf` 等依赖可能有平台兼容性问题。
**影响**: install 过程中断。
**缓解**: 如果非核心包安装失败，先移除这些包完成本任务，后续 issue 再引入。核心依赖（next、react、tailwind、radix、shadcn 相关）不应有问题。
