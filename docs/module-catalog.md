# 模块目录

> 本文档是项目模块的封闭目录。新增模块前先更新本文档；实现不得引入未登记的顶层模块。

状态说明：

- `planned`：只有规格，未写 protocol。
- `protocol`：protocol/model 已定义，暂无真实实现。
- `alpha`：已有最小实现，协议测试通过。
- `integrated`：已接入端到端流程。
- `stable`：可作为后续模块依赖。

## Layer 1 — 真源与配置

### `core/corpus`

- **Scope**：管理 public/private/submission 语料、article/figure/panel 元数据、文件路径和状态。
- **Anti-scope**：不做 PDF 提取，不计算图像特征，不解释证据。
- **Implementation**：手写，SQLite 为第一实现。
- **First deliverable**：SQLite schema + `CorpusStoreProtocol` + article/figure/panel CRUD。
- **Status**：planned

### `core/storage`

- **Scope**：管理 PDF、figure、panel、heatmap、report 等文件对象的路径、命名和校验。
- **Anti-scope**：不存业务状态，不生成图像内容。
- **Implementation**：手写，本地文件系统为第一实现。
- **First deliverable**：稳定 object key 规则和 sha256 校验。
- **Status**：planned

### `core/config`

- **Scope**：加载路径、阈值、模型开关、索引参数、adapter 选择、报告措辞 profile、数据保留策略、产品套餐限制、AI 咨询额度和专家服务额度。
- **Anti-scope**：不保存运行状态，不做业务判断。
- **Implementation**：手写，TOML + env override。
- **First deliverable**：typed settings、默认开发配置、review-safe report profile、submission/private/public 默认隔离策略。
- **Status**：planned

### `core/jobs`

- **Scope**：记录 ingestion、feature build、search、forensic、report 任务状态。
- **Anti-scope**：不执行具体算法，不保存图像证据。
- **Implementation**：手写，SQLite job 表为第一实现。
- **First deliverable**：job lifecycle：queued/running/succeeded/failed。
- **Status**：planned

### `core/ai`

- **Scope**：统一管理 LLM 调用、prompt 版本控制、隐私过滤（控制哪些字段和图像可以发送给 LLM）、响应解析、审计日志和 token/成本追踪。为 extract/panel（切分校验）、review/report（报告撰写）、review/annotation（AI 咨询）提供统一网关。
- **Anti-scope**：不包含业务判断逻辑，不替代 CV pipeline 做特征提取或相似检索，不直接存储业务状态，不做高精度查重或图像取证。
- **Implementation**：手写网关和审计层；LLM provider adapter 拼接 OpenAI/Anthropic/本地模型 API。
- **First deliverable**：`LLMGatewayProtocol` + deterministic fake responder + `AICallRecord` 审计模型 + privacy filter 规则。
- **Status**：planned

## Layer 2 — 文档与图像结构化

### `extract/pdf`

- **Scope**：从 PDF 中提取 figure 图片、caption、page、bbox。
- **Anti-scope**：不切 panel，不做相似检索，不做篡改分析。
- **Implementation**：混合；本项目定义 protocol，首个 adapter 拼接 Modern Figure Extractor/PDFFigures2，fallback 使用 PyMuPDF。
- **First deliverable**：`PdfFigureExtractorProtocol` + fixture PDF smoke。
- **Status**：planned

### `extract/panel`

- **Scope**：把复合 figure 切分为 panel，并输出 panel label、bbox、image path、confidence 和 target/reference 计数输入。
- **Anti-scope**：不判断 panel 是否重复，不做 PS 痕迹检测。
- **Implementation**：混合；首选 adapter 拼接 panel-extractor 或 figpanel；检测结果通过 core/ai 网关做 LLM 校验后呈现给用户确认。
- **First deliverable**：`PanelDetectorProtocol` + no-op/simple fallback detector + panel count summary。
- **Status**：planned

### `extract/normalization`

- **Scope**：统一图像格式、尺寸、颜色空间、透明背景、EXIF 处理和可重复 hash 输入。
- **Anti-scope**：不生成语义特征，不判断相似。
- **Implementation**：手写，Pillow/OpenCV 作为底层库。
- **First deliverable**：PNG/RGB 归一化和 sha256 稳定性测试。
- **Status**：planned

## Layer 3 — 特征与索引

### `features/hash`

- **Scope**：生成 cryptographic hash、pHash、可选 dHash/aHash。
- **Anti-scope**：不做深度语义检索，不做几何验证。
- **Implementation**：手写 adapter，底层使用 imagehash。
- **First deliverable**：`HashFeatureExtractorProtocol` + pHash fixture tests。
- **Status**：planned

### `features/embedding`

- **Scope**：生成 CLIP/SigLIP 等深度 embedding。
- **Anti-scope**：不保存索引，不决定相似阈值。
- **Implementation**：混合；本项目 adapter 包装 open_clip 或 sentence-transformers。
- **First deliverable**：`EmbeddingExtractorProtocol` + deterministic fake extractor + optional real extractor。
- **Status**：planned

### `features/local`

- **Scope**：生成 SIFT/ORB/ALIKED 等局部特征，用于几何验证。
- **Anti-scope**：不进行候选召回，不输出最终证据等级。
- **Implementation**：混合；OpenCV SIFT/ORB 为第一实现。
- **First deliverable**：`LocalFeatureExtractorProtocol` + keypoint descriptor cache。
- **Status**：planned

### `index/faiss`

- **Scope**：维护 embedding 向量索引，支持按 corpus scope 查询 Top-K。
- **Anti-scope**：不拥有 panel 元数据，不做证据解释。
- **Implementation**：手写封装，FAISS 为底层库。
- **First deliverable**：Flat index + metadata id 映射 + rebuild 命令。
- **Status**：planned

### `index/hash_index`

- **Scope**：维护 pHash 近邻查询，支持快速 exact/near duplicate 候选召回。
- **Anti-scope**：不做深度语义召回，不做几何验证。
- **Implementation**：手写；SQLite 表或内存 BK-tree 作为第一实现。
- **First deliverable**：按 Hamming distance 查询候选。
- **Status**：planned

## Layer 4 — 检索、验证与证据

### `analysis/retrieval`

- **Scope**：合并 pHash 与 embedding 候选，按 submission/internal、internal/private、external/public、pubmed/public 四类范围查询。
- **Anti-scope**：不做几何验证，不做 PS 痕迹检测。
- **Implementation**：手写。
- **First deliverable**：`CandidateRetrieverProtocol` + deterministic fake index tests。
- **Status**：planned

### `analysis/geometry`

- **Scope**：对候选图像做局部匹配、RANSAC/MAGSAC 验证、共享区域计算。
- **Anti-scope**：不负责候选召回，不负责最终报告。
- **Implementation**：混合；OpenCV SIFT/ORB + RANSAC 为第一实现，LightGlue 可作为后续 adapter。
- **First deliverable**：`GeometricVerifierProtocol` + synthetic transform fixture。
- **Status**：planned

### `analysis/forensics`

- **Scope**：检测疑似拼接、PS、局部篡改，输出 heatmap 和异常区域。
- **Anti-scope**：不判断跨库复用，不生成最终审查结论，不对 unsupported 图像类型强行给出风险判断。
- **Implementation**：拼接模型 adapter；TruFor 为优先候选，ManTraNet/Forgeryscope 为备选。
- **First deliverable**：`ForensicAnalyzerProtocol` + fake analyzer + heatmap artifact contract + unsupported/reliability 输出。
- **Status**：planned

### `analysis/evidence`

- **Scope**：将 retrieval、geometry、forensics 输出合并为 evidence finding。
- **Anti-scope**：不调用模型，不查询索引，不渲染 UI。
- **Implementation**：手写。
- **First deliverable**：证据等级规则：exact_duplicate/near_duplicate/partial_reuse/possible_manipulation/needs_review。
- **Status**：planned

## Layer 5 — 审查与报告

### `review/report`

- **Scope**：生成 HTML/JSON 报告，包含图像、来源、bbox、overlay、heatmap、分数、算法、参数、模型版本、panel 用量摘要、AI 咨询上下文和 review-safe language。
- **Anti-scope**：不执行分析，不修改 corpus。
- **Implementation**：手写；结构和模板使用 Jinja2，叙述段落和证据解释通过 core/ai 网关由 LLM 生成。
- **First deliverable**：single submission report fixture + expert-review-ready evidence packet + AI consultation context payload。
- **Status**：planned

### `review/annotation`

- **Scope**：保存人工复核标记、AI 咨询记录、基础专家确认记录、人工专家审核记录，并记录操作者、时间、备注、专家复核来源和审计 trail。
- **Anti-scope**：不改变原始算法结果，不删除证据，不承担专家排班或 SLA 工单系统，不允许 AI 咨询覆盖原始 finding。
- **Implementation**：手写，SQLite 表为第一实现。
- **First deliverable**：annotation CRUD + audit timestamp + finding-level review history + consultation transcript storage。
- **Status**：planned

### `app/cli`

- **Scope**：提供导入、建索引、筛查、生成报告等命令入口。
- **Anti-scope**：不包含业务逻辑，只调用模块 public API。
- **Implementation**：手写，argparse 或 Typer。
- **First deliverable**：`paper-image screen <pdf>` smoke。
- **Status**：alpha

### `app/ui`

- **Scope**：提供上传、任务进度、panel 计数确认、费用预估、报告浏览、AI 咨询、人工标记和专家服务加购界面。
- **Anti-scope**：不拥有状态，不直接调用模型。
- **Implementation**：MVP 拼接 Streamlit；正式版可迁移 FastAPI + 前端。
- **First deliverable**：读取 report JSON 并展示证据、过滤 finding、提交人工标记、展示 panel 用量摘要。
- **Status**：planned

## Layer 6 — 质量与治理

### `quality/evaluation`

- **Scope**：维护小型 gold fixtures，评估 extraction、panel segmentation、retrieval、geometry、forensics、report review completion 的基本质量，并为商业承诺提供内部证据。
- **Anti-scope**：不替代人工审查，不作为学术不端判定，不直接生成营销准确率口径。
- **Implementation**：手写。
- **First deliverable**：10 篇 PDF / 50 图 / 若干人工标注 case 的离线评估命令 + 指标摘要 JSON。
- **Status**：planned

### `quality/module_checks`

- **Scope**：检查模块布局、禁止 `_impl` 跨模块导入、报告文件规模。
- **Anti-scope**：不做业务测试，不跑模型质量评估。
- **Implementation**：手写。
- **First deliverable**：module layout check。
- **Status**：planned

## 模块计数

- 真源与配置：5
- 文档与图像结构化：3
- 特征与索引：5
- 检索、验证与证据：4
- 审查与报告：4
- 质量与治理：2

合计：23 个模块。MVP 不应新增第 24 个模块；如确需新增，应先更新本文档并说明现有模块为何不能承载。
