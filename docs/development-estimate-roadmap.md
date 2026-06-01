# 接近竞品水平的开发难度与路线图

日期：2026-06-01  
关联文档：[competitive-analysis.md](competitive-analysis.md)、[roadmap.md](roadmap.md)、[module-catalog.md](module-catalog.md)

## 1. 结论先行

如果目标是做出一个**可演示、能处理我们当前 2 万张图规模、支持私有库和基础相似检索的 MVP**，开发难度中等，预计 **8-12 周**可以完成。

如果目标是做出一个**可对外试用、接近 ImageTwin 自助查重体验、但外部数据库规模远小于 ImageTwin 的商业 Beta**，开发难度中高，预计 **4-6 个月**。

如果目标是做出一个**接近 Proofig/FigScan 的可信商业产品**，包括稳定 panel 切分、较低误报、可复核报告、专家复核 SOP、隐私安全和机构部署能力，开发难度高，预计 **6-12 个月**。

如果目标是全面接近 ImageTwin 的全球数据库和出版商集成能力，单靠开发无法完成，需要数据合作、出版平台合作和长期运营，周期应按 **18-36 个月**评估。

## 2. 关键假设

本估算基于以下假设：

- 初始数据规模：公开库约 1000 篇文章，私有库约 100 篇文章，原始 figure 约 20,000 张，切 panel 后约 50,000-100,000 个 panel。
- 技术路线：系统真源手写，算法能力拼接，不从零训练大模型。
- 第一阶段部署：单机或小型服务器，本地文件系统 + SQLite + FAISS。
- 团队基准：2 名 Python/CV 工程师、1 名前端/产品工程师、1 名兼职生命科学专家、1 名兼职产品/运营。
- 不承诺 1 亿级全网库，不承诺 99% 以上准确率，直到 M7 评估集支持。

如果团队只有 1 名全栈工程师，周期通常需要乘以 2 至 2.5。如果团队有 5-7 名稳定工程师和领域专家，MVP 可压缩到 6-8 周，但 M5/M7 的质量验证仍很难压缩。

## 3. 难度拆解

| 能力 | 对标竞品 | 难度 | 主要难点 | 预计周期 |
| --- | --- | --- | --- | --- |
| PDF 上传与 figure 提取 | 三家都有 | 中 | PDF 格式差异、caption/bbox 追溯、失败回退 | 2-4 周 |
| Panel 自动切分 | Proofig/FigScan 强依赖 | 高 | 复合图样式复杂、标签识别、误切漏切影响后续全部结果 | 4-8 周起步，长期迭代 |
| 私有库入库与索引 | ImageTwin 私有库、Proofig My Database | 中 | public/private/submission 边界、稳定 ID、重建索引 | 2-4 周 |
| pHash/embedding 相似召回 | ImageTwin 核心 | 中 | 多路召回融合、阈值、跨库 scope、去重 | 3-5 周 |
| 几何验证 | ImageTwin/Proofig 核心 | 中高 | 裁剪、旋转、翻转、局部复用、低纹理图像失败 | 4-8 周 |
| 拼接/PS 痕迹检测 | Proofig/FigScan 卖点 | 很高 | 误报高、图像类型差异大、模型许可证与部署 | 8-16 周起步，长期迭代 |
| 报告与人工复核 UI | Proofig/FigScan 核心体验 | 中高 | 证据可解释、side-by-side、overlay、人工标记、审计 | 4-8 周 |
| 评估集与准确率口径 | 商业可信度基础 | 高 | 需要人工标注、误报样例、指标定义 | 4-12 周，贯穿全程 |
| 隐私与机构部署 | FigScan/ImageTwin 机构版 | 高 | 数据隔离、删除策略、权限、审计、离线部署 | 4-12 周 |
| 专家复核服务 | FigScan 高价模式 | 高 | SOP、专家供给、报告责任边界、SLA | 6-12 周建立，长期运营 |
| 1 亿级公开库 | ImageTwin/FigScan 壁垒 | 极高 | 数据授权、版权、爬取、存储、索引、持续更新 | 18-36 个月 |

## 4. 竞品水平分层

### Level 1：内部 MVP，接近“可用原型”

目标：能处理本项目自有数据，跑通 private/public/internal 相似检索和基础报告。

预计周期：8-12 周。  
团队：2 名工程师 + 兼职领域专家。  
接近对象：ImageTwin 的最小查重闭环，但不接近其数据库规模。

可交付：

- public/private/submission 三库。
- PDF figure 提取和简单 panel 切分。
- pHash + embedding 特征。
- FAISS Flat 和 hash near duplicate index。
- internal/public/private Top-K 召回。
- SIFT/ORB 几何验证。
- HTML/JSON 报告。

还不能承诺：

- 高质量拼接/PS 痕迹检测。
- 低误报商业级准确率。
- 专家复核。
- 大规模公开库。

### Level 2：自助 Beta，接近“ImageTwin 低配版”

目标：用户上传一篇 PDF，可以即时得到结构化报告；对 1000 篇公开相关库和私有库有可解释查重结果。

预计周期：4-6 个月。  
团队：3-5 人。  
接近对象：ImageTwin 的自助 scan 体验，但公开库和出版平台集成远弱于 ImageTwin。

新增能力：

- 更稳定的 PDF/figure/panel pipeline。
- 支持失败重试、任务状态、批量入库。
- 报告展示 source/target、bbox、overlay、相似分数、几何参数。
- Streamlit 或轻量 Web UI。
- 初版 gold set，能评估 retrieval top-k recall 和几何验证 precision。
- 基础隐私策略：不把 submission 自动加入 public，不把私有库外泄。

商业可试点场景：

- 实验室历史图像自查。
- 个人投稿前相似图筛查。
- 机构内部 100-1000 篇小规模库筛查。

### Level 3：商业可用版，接近“Proofig/FigScan 的部分能力”

目标：不仅能查相似，还能支持人工复核、报告留档、误报管理和基础取证 heatmap。

预计周期：6-12 个月。  
团队：5-7 人，包括至少 1 名领域专家或专家顾问。  
接近对象：Proofig 的审查工具体验、FigScan 的可复核报告体验，但不一定达到其销售声称准确率。

新增能力：

- 较稳定的 panel detector，支持人工修正。
- forensic adapter：TruFor/ManTraNet 等模型接入，输出 heatmap 和 unsupported reason。
- review annotation：confirmed、false_positive、needs_more_review。
- 专家可读报告模板。
- 审计日志和版本记录。
- 更完整的 evaluation suite。
- 基础账号、项目、权限和数据隔离。

商业可试点场景：

- ¥99-399/篇自助报告。
- ¥699-999/篇专家复核报告。
- 小机构/实验室年度私有库服务。

### Level 4：机构版，接近“可采购系统”

目标：支持机构部署、批量处理、可审计流程、稳定 SLA。

预计周期：9-18 个月。  
团队：7-10 人，包含工程、产品、运维、安全和专家网络。  
接近对象：Proofig/ FigScan 的机构客户能力，ImageTwin 的私有库能力。

新增能力：

- 多用户、多项目、多角色权限。
- SSO 或机构账号体系。
- API 和批量任务。
- 私有化部署包。
- 数据删除、保留、脱敏和审计策略。
- 专家复核工单系统。
- 模型和索引版本管理。
- 机构级 SLA 与运维监控。

仍然不一定具备：

- ImageTwin 级别的 150M+ 全球库。
- 大出版商投稿系统深度集成。
- 可公开宣称的行业最高准确率。

### Level 5：行业级平台

目标：与 ImageTwin/Proofig 在数据库、出版商集成和品牌信任上正面竞争。

预计周期：18-36 个月以上。  
团队：工程 + 数据 + BD + 法务 + 专家网络。  
关键不再只是开发，而是数据授权与渠道合作。

必须具备：

- 千万至亿级公开图像指纹库。
- 持续数据更新管道。
- 出版社、期刊或高校合作。
- 高质量 benchmark 和公开可信案例。
- API、SSO、审计、安全认证。
- 完整专家复核和申诉流程。

## 5. 推荐路线图

### Phase 0：规格与验证基线

周期：已开始，建议 1 周内封版。  
目标：把产品边界、竞品定位、模块目录、验收标准固定下来。

交付：

- 产品方案。
- 模块目录。
- 竞品分析。
- 本开发估算与路线图。
- gold set 设计草案。

验收标准：

- 所有模块都有 scope / anti-scope。
- 明确哪些能力手写，哪些拼接。
- 不再把“全网大库”和“专家准确率”放入 MVP 承诺。

### Phase 1：Corpus Truth 与本地对象存储

周期：2-3 周。  
目标：建立系统真源，为后续所有算法输出提供可追溯状态。

任务：

- SQLite schema：article、figure、panel、artifact、feature、finding、job。
- 文件对象存储规则。
- public/private/submission scope。
- CLI：创建库、导入文章、列出记录。
- 基础测试：稳定 ID、路径校验、scope 隔离。

难度：中。  
主要风险：真源设计不稳会导致后续索引、报告、复核全部返工。

### Phase 2：PDF Figure 与 Panel 结构化

周期：3-6 周。  
目标：从 PDF 到 figure/panel 的可追溯结构化数据。

任务：

- PdfFigureExtractor protocol。
- Modern Figure Extractor/PDFFigures2 adapter。
- PyMuPDF fallback。
- PanelDetector protocol。
- simple panel detector 和一个真实 detector adapter。
- 提取失败记录 job failure，不污染 corpus。

难度：高。  
主要风险：PDF 格式、图片压缩、图表与照片混杂、panel 漏切误切。

里程碑：

- 第 4 周：能处理 10 篇 fixture PDF。
- 第 6 周：能批量处理 100 篇文档并生成结构化记录。

### Phase 3：Feature 与 Index

周期：3-5 周。  
目标：为所有 figure/panel 建立可查询特征。

任务：

- image normalization。
- sha256/pHash。
- open_clip 或 SigLIP embedding adapter。
- deterministic fake extractor，保证无 GPU 测试。
- FAISS Flat index。
- hash near-duplicate index。
- index rebuild CLI。

难度：中。  
主要风险：特征版本不稳定、索引和元数据错位、GPU/CPU 环境差异。

里程碑：

- 能在 20,000 figure 或 100,000 panel 规模下完成本地索引。
- 查询延迟达到单篇筛查可接受水平。

### Phase 4：Similarity Retrieval 与 Geometry Verification

周期：4-8 周。  
目标：做出接近 ImageTwin 核心查重闭环的第一版。

任务：

- CandidateRetriever：合并 pHash 与 embedding 候选。
- scope 查询：internal/public/private。
- OpenCV SIFT/ORB 局部特征。
- RANSAC/MAGSAC 几何验证。
- 输出 bbox、inlier 数、homography、verification score。
- Evidence merger：exact_duplicate、near_duplicate、partial_reuse、needs_review。

难度：中高。  
主要风险：低纹理图像、WB 条带、裁剪过小、重复背景导致误报。

里程碑：

- 对 crop/rotate/flip/resize synthetic fixtures 稳定命中。
- 对 100 篇私有库 + 1000 篇公开库支持单篇筛查。
- 报告中能解释为什么判为相似，而不只是给分数。

### Phase 5：Review Report 与自助 UI

周期：4-6 周。  
目标：把算法结果变成用户可以理解和复核的报告。

任务：

- Report JSON schema。
- HTML report renderer。
- source/target side-by-side。
- bbox、overlay、matched keypoints。
- finding filter：internal/public/private、risk level、figure type。
- Streamlit MVP UI。
- review-safe language 文案。

难度：中。  
主要风险：报告不清楚会让算法价值被低估，误报也更难被用户接受。

里程碑：

- 一篇论文上传后 10-30 分钟内出报告，具体取决于硬件和模型。
- 非技术用户能根据报告完成人工复核。

### Phase 6：Forensic Analysis

周期：8-16 周。  
目标：加入疑似拼接/PS 痕迹检测，但保持谨慎表述。

任务：

- ForensicAnalyzer protocol。
- TruFor 或 ManTraNet adapter。
- heatmap artifact contract。
- reliability score。
- unsupported reason。
- 与 similarity finding 分离展示。
- 小型真实/合成篡改评估集。

难度：很高。  
主要风险：误报、模型泛化、不同图像类型差异、商业许可证。

里程碑：

- 对明确 synthetic splice/clone case 能输出 heatmap。
- 对 unsupported 图像类型给出明确状态。
- 报告文案只写“疑似”“需复核”，不写自动定罪结论。

### Phase 7：Evaluation、隐私与商业 Beta

周期：6-10 周，可与 Phase 5/6 部分并行。  
目标：达到可对外试点的可信度。

任务：

- Gold fixture corpus。
- extraction coverage 指标。
- panel segmentation precision/recall。
- retrieval top-k recall。
- geometry verification precision。
- forensic false-positive smoke。
- privacy policy draft。
- data retention/delete policy。
- beta onboarding 文档。

难度：高。  
主要风险：没有评估证据就无法支撑销售承诺。

里程碑：

- 能给出内部准确率和误报率口径。
- 能明确哪些图像类型支持、哪些不支持。
- 能开始小范围付费试点。

### Phase 8：专家复核与机构能力

周期：8-16 周。  
目标：接近 FigScan 的服务化能力和 Proofig 的机构工作流。

任务：

- 专家复核 SOP。
- finding 分派和复核记录。
- confirmed / false_positive / needs_more_review 标注。
- 专家报告模板。
- 多用户权限。
- 批量导入和批量筛查。
- API 草案。
- 私有部署安装文档。

难度：高。  
主要风险：专家供给、SLA、责任边界、报告质量一致性。

里程碑：

- 可提供专家复核包。
- 可支持小机构年度私有库服务。
- 可开始谈机构试点。

## 6. 人员与周期方案

### 方案 A：精简团队

团队：2 名工程师 + 1 名兼职产品/前端 + 1 名兼职专家。  
周期：

- MVP：10-14 周。
- 自助 Beta：5-7 个月。
- 商业可用：9-12 个月。

优点：成本低，方向可控。  
缺点：panel、forensic、UI 和评估不能并行太多，进度慢。

### 方案 B：推荐团队

团队：2 名后端/CV、1 名前端、1 名数据/评估、1 名产品/运营、1 名兼职专家。  
周期：

- MVP：8-12 周。
- 自助 Beta：4-6 个月。
- 商业可用：6-9 个月。

优点：工程、评估、产品报告可以并行，是最平衡方案。  
缺点：需要较强模块边界和任务管理，否则容易变成“大 pipeline 一锅粥”。

### 方案 C：加速团队

团队：4 名工程、1 名前端、1 名数据工程、1 名 QA/评估、1 名产品、专家池。  
周期：

- MVP：6-8 周。
- 自助 Beta：3-4 个月。
- 商业可用：6 个月左右。

优点：能快速形成试点产品。  
缺点：早期需求还不完全稳定，过早扩人可能造成返工。

## 7. 成本与算力粗估

初始 20,000 figure / 100,000 panel 规模不需要复杂云架构：

- 元数据：SQLite 足够。
- 对象存储：本地文件系统足够。
- 向量索引：FAISS Flat 足够。
- embedding 生成：单张 GPU 可显著加速；CPU 也可跑，但批量入库慢。
- 在线筛查：单机服务可支持早期试点。

真正成本不在存储，而在：

- 人工标注 gold set。
- 专家复核时间。
- PDF/panel 异常 case 调试。
- 商业模型许可和 GPU 环境。
- 后续公开库扩张的数据授权。

## 8. 第一版成功标准

建议把第一版成功标准定义为：

- 能导入 1000 篇公开文章和 100 篇私有文章。
- 能处理单篇投稿 PDF，提取 figure/panel 并入库。
- 能在 internal/public/private 三个范围内找出 Top-K 相似候选。
- 能对候选做几何验证，输出可解释证据。
- 能生成 HTML/JSON 报告。
- 能让人工复核者标记误报或确认问题。
- 对 gold set 有基础指标，而不是只有个别 demo。

第一版不应承诺：

- 全网查重。
- 99% 准确率。
- 所有图像类型都支持 PS 痕迹检测。
- 自动判定学术不端。
- 8 小时专家 SLA。

## 9. 推荐近期 30 天计划

第 1 周：

- 封版产品边界和模块目录。
- 设计 SQLite schema。
- 设计文件对象路径规则。
- 准备 10 篇 fixture PDF 和 20-50 个标注样例。

第 2 周：

- 实现 corpus/store/storage。
- 实现 article/figure/panel CRUD。
- 建立 job lifecycle。
- CLI 支持导入和列出。

第 3 周：

- 接 PDF figure extractor protocol。
- 实现 PyMuPDF fallback。
- 生成 figure artifact。
- 保存 caption/page/bbox。

第 4 周：

- 接 simple panel detector。
- 生成 panel artifact。
- 建立 pHash 特征。
- 输出第一版 “PDF -> figure -> panel -> hash” 报告。

30 天结束时应具备的证明：

- 一个真实 PDF 能被导入、拆图、切 panel、生成稳定记录。
- 相同 PDF 重跑不会产生不一致 ID。
- 所有 artifact 可追溯回 article/figure/panel。
- 测试覆盖 corpus、storage、extract fallback、hash。

## 10. 最终判断

我们可以在短期内接近竞品的**工作流形态**，但不能短期接近 ImageTwin 的**数据库护城河**，也不能在没有评估集前接近 Proofig/FigScan 对外表达的**可信准确率**。

最务实的路径是：

1. 用 8-12 周做出私有库优先 MVP。
2. 用 4-6 个月做出可收费自助 Beta。
3. 用 6-12 个月补齐评估、取证、人工复核和机构能力。
4. 用 18 个月以上通过数据合作和机构试点扩大护城河。

这条路径不追求一开始“看起来像竞品”，而是先在我们的目标客户最在意的三个点上赢：私有数据安全、证据可复核、价格和交付可控。
