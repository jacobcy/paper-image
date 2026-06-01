# 实施切片目录

> 本文档把路线图拆成可派发工作项。每个切片都应该能独立进入 plan/run/review，而不是让一个执行者一次做完整系统。

## 命名规则

切片 ID 使用 `PI-M<milestone>-<module>-<number>`。

示例：

- `PI-M1-CORPUS-01`
- `PI-M2-PDF-02`
- `PI-M4-GEOM-01`

每个切片记录：

- **Goal**：该切片完成什么。
- **Module**：主要所属模块。
- **Inputs**：依赖哪些已有产物。
- **Deliverables**：输出文件、接口或命令。
- **Verification**：如何证明完成。
- **Implementation mode**：手写、拼接、混合。

## M0 — Spec Baseline

### PI-M0-SPEC-01：模块纪律与目录

- **Goal**：建立模块纪律和模块封闭目录。
- **Module**：quality/module_checks
- **Inputs**：产品方案。
- **Deliverables**：`docs/module-discipline.md`、`docs/module-catalog.md`。
- **Verification**：文档包含所有 MVP 模块的 scope、anti-scope、implementation、first deliverable。
- **Implementation mode**：手写文档。

### PI-M0-SPEC-02：阶段路线图与实施切片

- **Goal**：把 MVP 拆成可派发阶段。
- **Module**：quality/module_checks
- **Inputs**：模块目录。
- **Deliverables**：`docs/roadmap.md`、`docs/implementation-slices.md`。
- **Verification**：每个阶段有退出标准，每个切片有 verification。
- **Implementation mode**：手写文档。

## M1 — Corpus Truth 与本地存储

### PI-M1-CORPUS-01：Corpus protocol 与 domain model

- **Goal**：定义 article、figure、panel、artifact、job 的核心模型。
- **Module**：core/corpus
- **Inputs**：`src/paper_image/domain.py` 现有骨架。
- **Deliverables**：`src/paper_image/core/corpus/protocol.py`、`models.py`、协议测试。
- **Verification**：pytest 验证稳定 ID、scope 隔离、record round-trip。
- **Implementation mode**：手写。

### PI-M1-CORPUS-02：SQLite corpus store

- **Goal**：实现元数据真源。
- **Module**：core/corpus
- **Inputs**：PI-M1-CORPUS-01。
- **Deliverables**：SQLite schema、migration 初始化、CRUD 实现。
- **Verification**：临时数据库中 article/figure/panel 创建、查询、scope 过滤通过测试。
- **Implementation mode**：手写。

### PI-M1-STORAGE-01：Filesystem artifact store

- **Goal**：定义文件对象路径和 sha256 校验。
- **Module**：core/storage
- **Inputs**：Corpus artifact model。
- **Deliverables**：artifact key 规则、本地 filesystem implementation。
- **Verification**：相同内容 sha256 稳定，路径不依赖原始文件名，非法路径不能逃逸 storage root。
- **Implementation mode**：手写。

### PI-M1-JOBS-01：Job lifecycle

- **Goal**：记录 ingestion/index/search/report 等任务状态。
- **Module**：core/jobs
- **Inputs**：SQLite corpus store。
- **Deliverables**：job model、job store、状态转换。
- **Verification**：queued → running → succeeded/failed 转换测试，失败记录 error message。
- **Implementation mode**：手写。

## M2 — PDF Figure 与 Panel 结构化（含 AI Gateway）

### PI-M2-AI-01：LLM gateway protocol 与 fake responder

- **Goal**：定义统一 LLM 调用接口，包含隐私过滤、审计日志和成本追踪。
- **Module**：core/ai
- **Inputs**：core/config（模型选择、隐私策略）。
- **Deliverables**：`LLMGatewayProtocol`、`AICallRecord` 审计模型、privacy filter、deterministic fake responder。
- **Verification**：fake responder 调用产生完整审计记录；隐私过滤器阻止敏感字段发送；相同输入产生稳定输出。
- **Implementation mode**：手写。

### PI-M2-PDF-01：PDF extractor protocol

- **Goal**：定义 PDF 到 figure 的稳定输出结构。
- **Module**：extract/pdf
- **Inputs**：Corpus figure model、storage。
- **Deliverables**：`PdfFigureExtractorProtocol`、`ExtractedFigure` model、fake extractor。
- **Verification**：fake extractor 输出能被 corpus ingest。
- **Implementation mode**：手写。

### PI-M2-PDF-02：PDFFigures2 adapter

- **Goal**：拼接 Modern Figure Extractor 或 PDFFigures2。
- **Module**：extract/pdf
- **Inputs**：PI-M2-PDF-01。
- **Deliverables**：adapter、配置项、fixture smoke。
- **Verification**：fixture PDF 生成 figure image + caption + page + bbox。
- **Implementation mode**：拼接。

### PI-M2-PDF-03：PyMuPDF fallback

- **Goal**：为 PDFFigures2 失败场景提供页面渲染 fallback。
- **Module**：extract/pdf
- **Inputs**：PI-M2-PDF-01。
- **Deliverables**：PyMuPDF adapter。
- **Verification**：对无 caption 或复杂 PDF 至少生成 page-level image artifact，并标记 extraction_mode。
- **Implementation mode**：拼接。

### PI-M2-PANEL-01：Panel detector protocol

- **Goal**：定义 figure 到 panel 的稳定输出。
- **Module**：extract/panel
- **Inputs**：figure artifact。
- **Deliverables**：`PanelDetectorProtocol`、`DetectedPanel` model、simple full-figure fallback。
- **Verification**：无真实 detector 时，每张 figure 至少产生一个 full panel。
- **Implementation mode**：手写。

### PI-M2-PANEL-02：真实 panel detector adapter

- **Goal**：拼接 panel-extractor 或 figpanel。
- **Module**：extract/panel
- **Inputs**：PI-M2-PANEL-01。
- **Deliverables**：adapter、模型配置、fixture smoke。
- **Verification**：复合 figure fixture 产生多个 panel，bbox 在 figure 范围内。
- **Implementation mode**：拼接。

### PI-M2-PANEL-03：Panel 切分 LLM 校验

- **Goal**：使用 LLM 校验 detector 输出的 panel 切分结果，识别 A/B/C/D 子图结构和明显误切。
- **Module**：extract/panel（调用 core/ai）
- **Inputs**：PI-M2-PANEL-01、PI-M2-AI-01。
- **Deliverables**：LLM 校验 prompt 模板、校验结果模型、用户确认 UI 数据结构。
- **Verification**：已知 A/B/C/D 复合图经 LLM 校验后 label 正确；审计记录包含模型版本和 prompt 模板 ID。
- **Implementation mode**：混合。

## M3 — Feature 与 Index

### PI-M3-HASH-01：pHash feature extractor

- **Goal**：生成稳定 pHash 和 sha256。
- **Module**：features/hash
- **Inputs**：normalized panel image。
- **Deliverables**：hash protocol、imagehash adapter。
- **Verification**：相同图片 hash 相同，轻微 resize pHash 距离低于阈值。
- **Implementation mode**：混合。

### PI-M3-EMBED-01：Embedding protocol 与 fake extractor

- **Goal**：先固定 embedding 输出 contract。
- **Module**：features/embedding
- **Inputs**：panel image。
- **Deliverables**：embedding protocol、fake deterministic extractor。
- **Verification**：同一 panel 输出相同向量，维度写入 feature metadata。
- **Implementation mode**：手写。

### PI-M3-EMBED-02：open_clip 或 SigLIP adapter

- **Goal**：接入真实深度特征。
- **Module**：features/embedding
- **Inputs**：PI-M3-EMBED-01。
- **Deliverables**：模型 adapter、batch extraction。
- **Verification**：可选 GPU/CPU smoke；模型版本写入 metadata。
- **Implementation mode**：拼接。

### PI-M3-INDEX-01：FAISS Flat index

- **Goal**：建立按 panel_id 映射的向量索引。
- **Module**：index/faiss
- **Inputs**：embedding feature records。
- **Deliverables**：build/rebuild/query API。
- **Verification**：Top-K 查询返回 panel_id 和距离，scope filter 正确。
- **Implementation mode**：混合。

### PI-M3-INDEX-02：Hash index

- **Goal**：建立 pHash 近邻查询。
- **Module**：index/hash_index
- **Inputs**：hash feature records。
- **Deliverables**：Hamming distance 查询。
- **Verification**：exact duplicate 排第一，scope filter 正确。
- **Implementation mode**：手写。

## M4 — Similarity Retrieval 与 Geometry Verification

### PI-M4-RETRIEVAL-01：Candidate retrieval

- **Goal**：合并 hash 和 embedding 候选。
- **Module**：analysis/retrieval
- **Inputs**：FAISS index、hash index。
- **Deliverables**：候选合并、去重、scope 标记。
- **Verification**：同一 source panel 不重复出现，internal/public/private 结果分开。
- **Implementation mode**：手写。

### PI-M4-GEOM-01：Geometry verifier protocol

- **Goal**：定义局部复用验证输出。
- **Module**：analysis/geometry
- **Inputs**：candidate pair。
- **Deliverables**：protocol、models、fake verifier。
- **Verification**：fake verifier 输出可被 evidence merger 消费。
- **Implementation mode**：手写。

### PI-M4-GEOM-02：OpenCV SIFT/ORB verifier

- **Goal**：验证裁剪、旋转、翻转、缩放候选。
- **Module**：analysis/geometry
- **Inputs**：PI-M4-GEOM-01。
- **Deliverables**：OpenCV implementation、synthetic fixtures。
- **Verification**：已知 transformed pair 的 inlier 数和 shared bbox 达到阈值。
- **Implementation mode**：拼接。

### PI-M4-EVIDENCE-01：Similarity evidence merger

- **Goal**：将 retrieval + geometry 转为 review-safe finding。
- **Module**：analysis/evidence
- **Inputs**：candidate result、geometry result。
- **Deliverables**：evidence level 规则。
- **Verification**：exact hash match、near embedding match、partial geometry match 分别映射到正确 level。
- **Implementation mode**：手写。

## M5 — Forensic Analysis

### PI-M5-FORENSICS-01：Forensic protocol 与 fake analyzer

- **Goal**：固定 PS/拼接检测输出 contract。
- **Module**：analysis/forensics
- **Inputs**：panel artifact。
- **Deliverables**：protocol、finding model、fake heatmap writer、unsupported/not_run 状态。
- **Verification**：fake analyzer 生成明确标记为 fake 的 heatmap artifact；unsupported 输入返回 unsupported，不生成真实风险结论。
- **Implementation mode**：手写。

### PI-M5-FORENSICS-02：TruFor adapter

- **Goal**：接入真实 forensic heatmap 模型。
- **Module**：analysis/forensics
- **Inputs**：PI-M5-FORENSICS-01。
- **Deliverables**：TruFor adapter、模型配置、optional GPU smoke。
- **Verification**：输出 integrity score、heatmap、model version；失败时返回 explicit unsupported/failed 状态。
- **Implementation mode**：拼接。

### PI-M5-EVIDENCE-01：Forensic evidence merger

- **Goal**：将 forensic 输出并入 evidence。
- **Module**：analysis/evidence
- **Inputs**：forensic finding。
- **Deliverables**：possible_manipulation 规则和 report payload。
- **Verification**：forensic 结果不影响 similarity finding 原始证据。
- **Implementation mode**：手写。

## M6 — Review Report 与 UI

### PI-M6-REPORT-01：Report data model

- **Goal**：定义报告 JSON 结构，包含 evidence 和用量摘要。
- **Module**：review/report
- **Inputs**：article、panel、finding、artifact。
- **Deliverables**：report schema、serializer、target/reference panel usage summary、AI consultation context。
- **Verification**：单篇 submission report JSON snapshot 包含 target panel、internal/external/pubmed reference panel、finding、model version。
- **Implementation mode**：手写。

### PI-M6-AI-01：LLM 报告撰写与 AI 咨询

- **Goal**：接入真实 LLM 生成报告叙述段落和 AI 咨询回答。
- **Module**：core/ai + review/report + review/annotation
- **Inputs**：PI-M2-AI-01、PI-M6-REPORT-01。
- **Deliverables**：报告撰写 prompt 模板、咨询问答 prompt 模板、咨询额度追踪、审计记录。
- **Verification**：LLM 生成的叙述段落引用 finding ID 和证据来源，不出现"保证无问题"表述；咨询回答受 review-safe language 约束；所有调用有完整 AICallRecord。
- **Implementation mode**：混合。

### PI-M6-REPORT-02：HTML report renderer

- **Goal**：生成可人工复核、专家可继续判断的 HTML。
- **Module**：review/report
- **Inputs**：PI-M6-REPORT-01。
- **Deliverables**：Jinja2 template、asset copy、expert-review-ready evidence packet。
- **Verification**：HTML 包含 source/target image、overlay、score、algorithm、model version、threshold、safe wording。
- **Implementation mode**：手写。

### PI-M6-ANNOTATION-01：Review annotation

- **Goal**：保存人工复核、AI 咨询和专家确认状态。
- **Module**：review/annotation
- **Inputs**：finding id。
- **Deliverables**：annotation store、audit fields、finding-level review history、consultation transcript。
- **Verification**：人工标记和 AI 咨询不修改原 finding；同一 finding 的多次复核记录可追溯操作者、时间和来源类型。
- **Implementation mode**：手写。

### PI-M6-UI-01：Streamlit report viewer

- **Goal**：快速浏览报告、确认 panel 计数、使用 AI 咨询并标记 finding。
- **Module**：app/ui
- **Inputs**：report JSON、annotation store。
- **Deliverables**：Streamlit MVP。
- **Verification**：能打开单篇报告、查看图像和 heatmap、展示 panel 用量、记录 AI 咨询、保存人工标记。
- **Implementation mode**：拼接。

## M7 — Evaluation 与 Hardening

### PI-M7-EVAL-01：Gold fixture corpus

- **Goal**：建立小型可回归评估集。
- **Module**：quality/evaluation
- **Inputs**：若干公开 PDF 和人工标注。
- **Deliverables**：fixture manifest、expected outputs。
- **Verification**：CI 可读取 fixture manifest，不要求下载大模型。
- **Implementation mode**：手写。

### PI-M7-EVAL-02：Similarity smoke metrics

- **Goal**：跟踪 Top-K 召回和误报趋势。
- **Module**：quality/evaluation
- **Inputs**：gold fixture corpus。
- **Deliverables**：evaluation CLI。
- **Verification**：输出 precision-like smoke 指标和失败 case 列表。
- **Implementation mode**：手写。

### PI-M7-EVAL-03：Commercial confidence metrics

- **Goal**：建立商业承诺前的内部证据口径。
- **Module**：quality/evaluation
- **Inputs**：gold fixture corpus、report JSON、forensic output。
- **Deliverables**：metrics summary JSON，区分 supported、experimental、unsupported 能力。
- **Verification**：没有 gold set 指标的能力不能出现在 supported 列表；forensic fake output 必须标记 experimental 或 unsupported。
- **Implementation mode**：手写。

### PI-M7-PRIVACY-01：Privacy 与 data retention checks

- **Goal**：验证 submission/private/public 数据边界和删除策略。
- **Module**：quality/module_checks
- **Inputs**：core/config、corpus records、artifact store。
- **Deliverables**：privacy policy draft、retention config、boundary check。
- **Verification**：submission 不会自动写入 public corpus；private artifact 删除后索引重建不会返回已删除 panel。
- **Implementation mode**：手写。

### PI-M7-CHECKS-01：Module boundary checks

- **Goal**：防止跨模块导入 `_impl` 和新增未登记模块。
- **Module**：quality/module_checks
- **Inputs**：module catalog。
- **Deliverables**：check script。
- **Verification**：故意违规 fixture 会失败，当前代码通过。
- **Implementation mode**：手写。
