# paper-image

> 论文图像完整性筛查系统：面向论文 PDF 的图像复用、局部重复、拼接/PS 痕迹筛查与人工复核报告。

## Status

- **Phase**: M0 — Spec baseline
- **Maturity**: Draft / MVP skeleton
- **Current focus**: 建立模块边界、阶段路线图和第一批可派发实施切片

## Product Position

本项目不自动判定学术不端，而是生成可解释、可追溯、可人工复核的证据报告。系统核心任务：

- 跨库图像复用：与公开库、私有库中的历史论文图像比较。
- 同文内部重复：检测同一论文内重复、裁剪、旋转、翻转或局部复用。
- 拼接/PS 痕迹：输出疑似篡改区域、heatmap 和模型分数。

## Architecture Commitments

- Runtime truth lives in project-owned metadata, not in external extractor output or model-specific files.
- Public/private/submission corpus boundaries are first-class.
- Algorithm-heavy dependencies are adapters, not product truth.
- Modules are Protocol-first and listed in `docs/module-catalog.md`.
- Work is implemented by milestone slices, not one giant pipeline task.

## Documents

| Document | Purpose |
|---|---|
| [docs/product-plan.md](docs/product-plan.md) | 产品定位、MVP 范围、技术栈与手写/拼接边界 |
| [docs/module-discipline.md](docs/module-discipline.md) | 模块布局、Protocol-first、禁止 `_impl` 泄漏、拼接规则 |
| [docs/module-catalog.md](docs/module-catalog.md) | 封闭模块目录，包含 scope / anti-scope / first deliverable |
| [docs/roadmap.md](docs/roadmap.md) | M0-M7 阶段路线图和退出标准 |
| [docs/implementation-slices.md](docs/implementation-slices.md) | 可派发实施切片目录 |
| [docs/open-questions.md](docs/open-questions.md) | 执行前需要显式决策的问题 |
| [features/catalog.yaml](features/catalog.yaml) | 模块、里程碑、feature 的机器可读目录 |
| [docs/superpowers/plans/2026-06-01-paper-image-mvp-skeleton.md](docs/superpowers/plans/2026-06-01-paper-image-mvp-skeleton.md) | 已完成的初始骨架计划 |

## Current Skeleton

Current code is intentionally small:

- `src/paper_image/domain.py`: initial domain records and evidence levels
- `src/paper_image/pipeline.py`: demo screening pipeline contract
- `src/paper_image/cli.py`: CLI smoke path
- `tests/`: smoke tests for current skeleton

This is not the final module layout. Formal modules begin in M1 following [docs/module-discipline.md](docs/module-discipline.md).

## Verification

```bash
uv run --python 3.11 --with pytest pytest -q
uv run --python 3.11 python -m paper_image.cli uploads/submission.pdf
```

Expected current smoke output includes:

```text
figures=1 panels=1 findings=1
```
