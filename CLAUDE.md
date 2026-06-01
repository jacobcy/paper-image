# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

论文图像完整性筛查系统 — 面向论文 PDF 的图像复用、局部重复、拼接/PS 痕迹筛查与人工复核报告。系统不自动判定学术不端，而是生成可解释、可追溯、可人工复核的证据报告。

**当前阶段**: M0 (Spec baseline) — 仅有骨架代码，正式模块从 M1 开始。路线图见 `docs/roadmap.md`。

## Commands

```bash
# 运行测试
uv run --python 3.11 --with pytest pytest -q

# 运行单个测试
uv run --python 3.11 --with pytest pytest tests/test_domain.py -q

# CLI smoke
uv run --python 3.11 python -m paper_image.cli uploads/submission.pdf
```

无额外 lint/format 配置。无运行时依赖，dev 依赖仅 pytest。

## Architecture

### 六层模块体系 (22 个模块，全部 planned)

- **Layer 1 — 真源与配置**: `core/corpus`, `core/storage`, `core/config`, `core/jobs`, `core/ai`
- **Layer 2 — 文档与图像结构化**: `extract/pdf`, `extract/panel`, `extract/normalization`
- **Layer 3 — 特征与索引**: `features/hash`, `features/embedding`, `features/local`, `index/faiss`, `index/hash_index`
- **Layer 4 — 检索、验证与证据**: `analysis/retrieval`, `analysis/geometry`, `analysis/forensics`, `analysis/evidence`
- **Layer 5 — 审查与报告**: `review/report`, `review/annotation`, `app/cli`, `app/ui`
- **Layer 6 — 质量与治理**: `quality/evaluation`, `quality/module_checks`

完整模块 scope/anti-scope 定义见 `docs/module-catalog.md`。

### 当前骨架 (M0)

- `src/paper_image/domain.py` — 核心领域模型: `CorpusScope`, `EvidenceLevel`, `ArticleRecord`, `FigureRecord`, `PanelRecord`, `AnalysisFinding`, `make_stable_id()`
- `src/paper_image/pipeline.py` — Demo pipeline: `ScreeningRequest`, `ScreeningReport`, `DemoScreeningPipeline`
- `src/paper_image/cli.py` — CLI 入口

### 关键设计约束

1. **Protocol-first**: 每个模块必须先写 `protocol.py` + `models.py`，再写实现。开源库只能以 adapter 形式接入 `_impl/` 目录。
2. **Corpus scope 隔离**: public/private/submission 三类数据边界是一等公民，查询必须尊重 scope 边界。
3. **Runtime truth 归本项目所有**: 外部库（PDFFigures、YOLO、TruFor 等）的原始输出不能直接流入后续模块，必须转为本项目的 domain model。
4. **跨模块导入只从模块根**: `from paper_image.corpus import CorpusStoreProtocol` 合法；`from paper_image.corpus._impl.sqlite import ...` 禁止。
5. **禁止顶层 utils/common**: helper 放消费者模块 `_impl/`，真正跨模块的能力必须成为独立模块（如 `core/ai`）。
6. **Review-safe language**: 报告文案不得使用定性判断（如"存在问题"），只输出证据和分数。
7. **所有 domain dataclass 使用 `frozen=True`**，保持不可变。
8. **AI 角色分层**: LLM 做理解、校验、报告和咨询；CV/专用模型做提取、特征、检索、取证；人工专家做高风险复核。所有 LLM 调用通过 `core/ai` 网关统一管理，记录 `AICallRecord` 审计信息。

### 正式模块目录结构 (M1 起)

```
src/paper_image/<module>/
  __init__.py        # 仅导出 public API
  protocol.py        # Protocol 或抽象接口
  models.py          # dataclass / pydantic model
  errors.py          # 模块专属异常
  _impl/             # 私有实现
```

### 文件规模

目标 200-300 行，软上限 500 行，硬上限 800 行。

## Key References

- `docs/module-discipline.md` — 模块拆分规则、adapter 规则、验证规则
- `docs/module-catalog.md` — 封闭模块目录 (22 个模块)
- `docs/implementation-slices.md` — 可派发实施切片
- `features/catalog.yaml` — 机器可读的模块/里程碑/feature 目录
