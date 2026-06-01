---
name: project-frontend-demo
description: Frontend demo phase — React/Next.js 15 + Tailwind + shadcn/ui, 8 modules, 31 issues, image dedup API is separate
metadata:
  type: project
---

Frontend demo development started 2026-06-01. Tech stack: Next.js 15 (App Router) + Tailwind CSS 4 + shadcn/ui + TanStack Query + Zustand + tus-js-client + Vercel AI SDK.

8 frontend modules: scaffold (FE-01), auth (FE-02), upload/project (FE-03), figure/panel (FE-04), PubMed (FE-05), AI consultation (FE-06), report (FE-07), annotation (FE-08).

**Why:** Backend is still at M0 (spec baseline), so frontend uses MSW mock data to develop independently. Image dedup service is a separate API — frontend reserves type definitions but returns mock data for dedup calls.

**How to apply:** All frontend work lives in `frontend/` directory. API contracts defined in spec drive both MSW mocks and eventual FastAPI implementation. User executes each issue via agent dispatch. Respect review-safe language in all report UI text.

Related: [[project-backend-roadmap]]
