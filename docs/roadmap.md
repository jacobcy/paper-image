# 阶段路线图

> 本路线图把项目拆成可独立派发、独立验证的阶段。每个阶段都应产出可运行软件或可审查规格，不允许用一个总 pipeline 一次性完成所有任务。
>
> 竞品水平、开发难度、人力周期和商业 Beta 路线详见 [development-estimate-roadmap.md](development-estimate-roadmap.md)。
>
> 市场分析后的优先级：先交付私有库相似检索和可复核报告，再逐步强化 forensic 模型、专家复核和机构能力。MVP 不承诺全网大库、99% 准确率或专家 SLA。

## M0 — Spec Baseline

目标：建立产品规格、模块纪律、模块目录和实施切片。

关键交付：

- `docs/product-plan.md`
- `docs/module-discipline.md`
- `docs/module-catalog.md`
- `docs/roadmap.md`
- `docs/implementation-slices.md`
- `docs/competitive-analysis.md`
- `docs/development-estimate-roadmap.md`

退出标准：

- 每个模块有 scope / anti-scope / implementation / first deliverable。
- MVP 阶段不依赖未登记模块。
- 手写模块与拼接模块边界清楚。

## M1 — Corpus Truth 与本地存储

目标：把 public/private/submission 三类数据边界落为系统真源。

关键交付：

- SQLite schema：article、figure、panel、artifact、job。
- 文件对象存储规则：PDF、figure、panel、heatmap、report。
- CorpusStore protocol 和本地实现。
- CLI：创建 corpus、导入 article metadata、列出 article。

退出标准：

- 不接任何真实模型也能创建 article/figure/panel 记录。
- 相同输入生成稳定 ID。
- 所有文件路径可由 storage 模块反推和校验。

## M2 — PDF Figure 与 Panel 结构化

目标：从 PDF 中得到可追溯 figure/panel 结构；建立 LLM 网关基础设施。

关键交付：

- PdfFigureExtractor protocol。
- PDFFigures2/Modern Figure Extractor adapter。
- PyMuPDF fallback adapter。
- PanelDetector protocol。
- simple fallback panel detector 和一个真实 detector adapter。
- LLM gateway protocol 和 deterministic fake responder（core/ai）。
- Panel 切分 LLM 校验接口和 prompt 模板。

退出标准：

- 对 fixture PDF 能保存 figure image、caption、page、bbox。
- 对复合 figure 能生成 panel 记录。
- 提取失败以 job failure 记录，不污染 corpus 真源。
- LLM gateway fake responder 可运行，审计记录完整。
- Panel 切分校验产生 AICallRecord，隐私过滤器正常工作。

## M3 — Feature 与 Index

目标：为 figure/panel 生成可查询特征，建立索引。

关键交付：

- pHash feature extractor。
- embedding extractor protocol 与 fake extractor。
- 可选 open_clip/SigLIP adapter。
- FAISS Flat index wrapper。
- hash near-duplicate index。

退出标准：

- 能对 corpus 中所有 panel build features。
- 能重建索引。
- 索引条目与 panel_id 一一映射。
- 不同 corpus scope 查询边界正确。

## M4 — Similarity Retrieval 与 Geometry Verification

目标：完成跨库复用和同文内部重复的证据链。

关键交付：

- CandidateRetriever：合并 hash 与 embedding 召回。
- GeometricVerifier：SIFT/ORB + RANSAC 验证。
- Evidence merger：输出 duplicate / partial reuse / needs review。
- CLI：`screen-similarity <article_id>`。

退出标准：

- 能分别查询 internal/public/private。
- 对 synthetic crop/rotate/flip fixture 能给出几何验证结果。
- 报告中保留来源图、目标图、分数、算法、参数。

## M5 — Forensic Analysis

目标：先固定拼接/PS 痕迹检测的独立证据通道 contract，再逐步接入真实模型。

关键交付：

- ForensicAnalyzer protocol。
- fake analyzer 用于稳定测试。
- TruFor adapter 或 ManTraNet adapter，作为商业 Beta 前的增强项。
- heatmap artifact contract。
- CLI：`screen-forensics <article_id>`。

退出标准：

- 每个 panel 能生成 forensic finding、not_run、fake 或明确的 unsupported 状态。
- heatmap 路径、分数、模型版本和参数写入报告数据。
- Forensic 模块不影响 similarity 模块结果。
- 未接真实模型时，报告不得把 fake analyzer 输出表述为真实检测结论。

## M6 — Review Report 与人工复核

目标：生成可审查、专家复核友好的报告，并保存人工复核结论。该阶段是商业 Beta 的核心门槛，应与 M4/M5 部分并行推进。

关键交付：

- HTML/JSON report renderer。
- Review annotation store。
- Streamlit MVP UI。
- Evidence drill-down：source/target/overlay/heatmap。
- Review-safe language、模型版本、阈值、人工标记和审计 trail。
- LLM 报告撰写 adapter 和结构化 prompt。
- AI 咨询问答 protocol、审计记录和额度追踪。

退出标准：

- 单篇提交能生成完整报告和 expert-review-ready evidence packet。
- 人工标记不会覆盖原始算法证据。
- 报告文案使用 review-safe language。
- 非技术用户能根据报告完成一次复核，不需要查看原始日志。

## M7 — Evaluation、Privacy 与 Hardening

目标：用小型 gold set 固化质量底线，并补齐隐私、数据保留和商业承诺口径，为后续真实数据迭代和付费试点做准备。

关键交付：

- Gold fixture corpus。
- Extraction coverage evaluation。
- Retrieval precision smoke。
- Geometry verification synthetic suite。
- Report review completion evaluation。
- Privacy policy draft 和 data retention/delete policy。
- Commercial confidence metrics：哪些能力可对外承诺，哪些必须标记为实验性。
- Module layout check。
- Import boundary check。

退出标准：

- CI 能跑不依赖 GPU 的核心测试。
- GPU/模型测试可作为 optional profile。
- 每个模块有至少一个协议测试。
- 对外准确率、召回率、误报率表述必须能追溯到 gold set 或明确标为实验性。
- submission/private/public 的数据边界有自动化测试或审计检查。

## 分布实施原则

每个阶段拆成 3 至 8 个 issue/任务；每个任务只触碰一个模块或一个清晰的 adapter。允许跨模块集成任务，但不能在集成任务中首次定义底层模块行为。

实施顺序：

1. Catalog/spec task。
2. Protocol/model task。
3. Fake/no-op implementation task。
4. Real adapter task。
5. Integration/report task。
6. Evaluation/hardening task。

如果某阶段发现边界不够清晰，先回到 M0 文档更新，再继续实现。
