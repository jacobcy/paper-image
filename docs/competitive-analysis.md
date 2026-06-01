# 论文图像完整性筛查竞品分析报告

日期：2026-06-01  
对象：ImageTwin、Proofig、FigScan  
用途：为本项目的产品定位、技术底座、阶段路线和报价策略提供决策依据。

## 1. 结论摘要

本赛道已经形成三种清晰产品范式：

- **ImageTwin**：低门槛、按篇/按 scan、全球大库、即时自动报告。它的护城河是 150M+ 公开/合作数据库和出版流程集成，适合做“投稿前自动筛查入口”和出版平台批量 screening。
- **Proofig**：按 sub-image 精细计费，强调像素级操纵、PubMed 源查重、手工复核工具和机构/出版商流程。它适合对准确度和审稿工作流要求更高的机构客户，但个人复杂组图论文的成本压力明显。
- **FigScan**：AI 预筛加专家复核，卖点不是最低价或最大库，而是降低误报焦虑、给用户“有人看过”的安全感。该模式特别贴合中国科研作者投稿前的风险规避心理。

对我们当前项目，最佳切入不是复制 ImageTwin 的全球库，也不是一开始做 Proofig 式重取证平台，而是做一个**私有库优先、证据可复核、可本地部署、报告可信**的中间型产品。我们的初始规模约 20,000 张 figure、切 panel 后约 50,000 至 100,000 个 panel，用手写系统骨架拼接开源算法足够支撑 MVP，不需要一开始上分布式大数据架构。

## 2. 证据分级与复核口径

本报告把信息分为三类：

- **公开可证实**：官网、公开新闻、产品页或价格页可直接看到。
- **销售来源证实**：来自对方销售沟通，可用于我们内部商业决策，但不宜在对外材料中作为公开引用。
- **推断/待验证**：由公开材料和产品逻辑推断，进入执行前需要再次验证。

| 项目 | 关键说法 | 复核结果 | 证据级别 |
| --- | --- | --- | --- |
| ImageTwin 单次 scan 约 ¥226 | 官网单次 €29，按 2026-06-01 近似汇率可折算到约 ¥226 | 可采信 | 公开可证实 |
| ImageTwin 年度团队版单篇约 ¥27-¥39 | 官网年度计划 €999/200、€1,999/500、€3,499/1000，对应 €5、€4、€3.5/scan | 可采信 | 公开可证实 |
| ImageTwin 私有库全系标配 | 官网显示单次和 bundle 有 100 MB private repository，年度版 500 MB 至 10 GB | 可采信 | 公开可证实 |
| ImageTwin 150M+ 图片库 | 官网和 Wiley 集成新闻均提到 150M+ scientific/academic images | 可采信 | 公开可证实 |
| Proofig 按 sub-image 计费 | 官网价格页按 120/320/620/1020 sub-images 售卖 | 可采信 | 公开可证实 |
| Proofig 起步 ¥713，均价 ¥4.3-¥6/sub-image | 官网 $99/120、$230/320、$400/620、$610/1020，按约 7.2 汇率折算 | 可采信 | 公开可证实 |
| Proofig 零售版无私有库 | 官网说明 My Database 当前面向 enterprise licenses | 可采信 | 公开可证实 |
| Proofig 文件限制 50 MB、100 页、500 sub-images | 官网 FAQ 明示 | 可采信 | 公开可证实 |
| FigScan AI + 专家复核 | figscan.cn 和 figscan.org 均强调 expert-reviewed / 专家复核 | 可采信 | 公开可证实 |
| FigScan ¥999/篇、25 页、500 小图、30 MB、8 工作小时 | 用户确认来自对方销售报价 | 内部可采信，对外引用需谨慎 | 销售来源证实 |
| FigScan 99.9% 准确率 | 销售说法可用于竞品定位判断，但公开站点更常见为 >99% 或 reviewable findings | 内部可采信，不建议对外复述为事实 | 销售来源证实 |

## 3. 竞品画像

### 3.1 ImageTwin：低门槛流量入口

**产品定位**  
ImageTwin 是最像“论文图像查重 SaaS”的产品：用户上传一篇 PDF 或一组图片，系统自动提取 figure/sub-image，和大规模公开/合作库及私有库比较，快速返回报告。它的优势在于流程轻、价格门槛低、外部数据库强。

**计费与限制**  
公开价格页显示：

- Single Scan：€29/scan。
- 10 Scan Bundle：€199，约 €20/scan。
- 20 Scan Bundle：€299，约 €15/scan。
- 50 Scan Bundle：€499，约 €10/scan。
- 年度 Essentials：€999/200 scans，约 €5/scan。
- 年度 Advanced：€1,999/500 scans，约 €4/scan。
- 年度 Pro：€3,499/1000 scans，约 €3.5/scan。
- 一个 scan 可检查一篇 PDF 或最多 25 张单图，复合图内 sub-images 不额外收费。

这验证了“按篇/PDF 计费”和“复杂组图文章友好”的判断。它不是按 panel 逐张加价，因此对生物医学多 panel 论文很有价格优势。

**技术与能力推断**  
公开材料显示其检测范围包括：

- 跨论文图像复用。
- 同文或跨文重复。
- 裁剪、旋转、翻转、缩放、亮度/对比度变化后的复用。
- 局部克隆区域。
- AI-generated image detection。
- DOI、PubMed、PMC 等来源追踪。

从技术上看，ImageTwin 大概率是“深度特征召回 + 局部几何验证 + 证据报告”的架构。它未公开模型细节，但产品能力与我们的 M3/M4/M6 路线高度一致。

**核心护城河**  
ImageTwin 真正难复制的是数据库和工作流集成。Wiley 在 2026-05-26 宣布将 Imagetwin 集成到 Research Exchange，公开新闻提到其已筛查 500,000+ manuscripts，并基于 150M+ academic images。这个级别不是开源技术短期可追平的。

**对我们的启示**  
我们不应在第一阶段宣称“对标 150M+ 全网库”。更现实的策略是：

- 先把 public 1000 篇相似文章和 private 100 篇文章做成高质量私有索引。
- 每个相似结果必须有 source citation、bbox、相似分数、几何验证证据。
- 对多 panel 论文采用按篇或按额度计费，而不是按小图无限加价。
- 私有库应作为默认能力，不应像 Proofig 那样只放到企业版。

### 3.2 Proofig：机构级精度与审稿工具

**产品定位**  
Proofig 的核心不是低价入口，而是机构级 image integrity workflow。它强调 PubMed source plagiarism、duplication/reuse、alteration/manipulation、AI-generated image detection、forensic tools/manual review 和报告组合。

**计费与限制**  
公开价格页显示个人版按 sub-image 购买：

- 120 sub-images：$99，约 $0.825/sub-image。
- 320 sub-images：$230，约 $0.719/sub-image。
- 620 sub-images：$400，约 $0.645/sub-image。
- 1020 sub-images：$610，约 $0.598/sub-image。

按 1 USD ≈ 7.2 RMB 粗略折算，对应约 ¥4.3 至 ¥5.9/sub-image。复杂生物医学论文如果拆出 100 至 300 个 panel，单篇成本可能明显高于 ImageTwin。

官网 FAQ 同时给出文件限制：最大 50 MB、不超过 100 页、最多 500 sub-images。My Database 在公开价格页中仅面向 enterprise licenses，这验证了“零售版无私有库”的判断。

**技术与能力推断**  
Proofig 公开说明可以识别：

- direct reuse、modified reuse、self-plagiarism、cross-paper overlaps。
- full/partial duplication、rotation、flipping、scaling、cloning。
- splicing、cropping、insertion、erasing。
- 面向 microscopy、histology、western blot、gel、flow cytometry 等生命科学图像。

它的产品形态更接近“AI 检出 + 人工判断工具”。这对我们的报告和 UI 有直接参考价值：不能只输出一个相似度数字，要给审查者 side-by-side、overlay、heatmap、筛选和人工标记。

**核心护城河**  
Proofig 的优势在审稿组织流程、检测类别完整度、人工复核工具和出版商/机构信任。它的弱点是个人用户价格心理门槛高，私有库能力不够下沉。

**对我们的启示**  
我们的产品应避免“无上限逐 sub-image 扣费”的体验。由于复合图真实成本来自 panel，合理方案不是回到 top-level figure 计费，而是采用“基础 panel 包 + 目标 panel 阶梯 + 参考 panel 低价阶梯”的方式，让复杂论文价格可预期。

### 3.3 FigScan：高溢价专家审查模式

**产品定位**  
FigScan 的核心卖点是“AI + 专家复核”。它抓住的是用户对误报、漏报、撤稿和投稿风险的焦虑。对科研作者而言，专家复核不是单纯多一道流程，而是把黑箱 AI 结果转化为“我可以拿来改稿、沟通和留档的证据”。

**计费与限制**  
用户确认的销售报价为：

- 专家深度审查：¥999/篇。
- 单次最多 25 页 PDF、500 张小图、文件不超过 30 MB。
- 交付时效：8 个工作小时。
- 流程：上传、加密/隐私沙箱、专家复核、出具结果。

公开站点可验证其强调：

- 1 亿+科研数据库。
- AI + 专家复核。
- 检出准确率 >99%。
- SM4 + PrivacySandbox。
- 三位生物医学专家复核。
- 24 小时内自动删除记录。
- 支持组内对比、全网检测、专业报告。

因此，“专家审查 + 高溢价 + 安全感”这个竞品判断成立。具体价格和 SLA 属于销售来源，内部决策可采用，对外引用应表述为“市场销售报价显示”。

**技术与能力推断**  
FigScan 的公开描述覆盖：

- 文献图片切割到最小对比单元。
- 图像相似度计算。
- 生命科学大模型分类。
- 重复、旋转、翻转、缩放、克隆、拼接、裁剪识别。
- PubMed、PubPeer 等文献库构建的大规模图片库。

它不像 ImageTwin 那样强调开放透明的 scan 定价，也不像 Proofig 那样清晰展示 sub-image 套餐，更像“服务化交付 + 销售驱动”的模式。

**对我们的启示**  
FigScan 证明专家复核可以显著提高客单价。但我们不应在技术未验证前承诺 99% 或 99.9% 准确率。更稳妥的路径是先把系统报告做成专家可复核格式，再把专家复核作为付费增值层，而不是把“专家”硬塞进 MVP。

## 4. 横向对比

| 维度 | ImageTwin | Proofig | FigScan | 我们的建议定位 |
| --- | --- | --- | --- | --- |
| 主计费单位 | scan/PDF | sub-image | paper + expert service | panel package，区分目标 panel 与参考 panel |
| 零售门槛 | 低 | 中高 | 高 | 中低自助 + 高价专家复核 |
| 私有库 | 全计划均有基础 private repository | 企业版为主 | 销售/机构场景强调 | MVP 默认内置 public/private/submission 三库 |
| 外部库 | 150M+ published images | PubMed OA tens of millions | 中文站称 1 亿+ | 初期不追全网，先做 1000 篇公开相关库 |
| 强项 | 大库、低价、自动化、出版平台集成 | 像素级取证、审稿工具、机构流程 | 专家复核、安全感、本土服务 | 私有库、本地化、可解释证据、可复核报告 |
| 弱项 | 数据库护城河难复制；低价压缩服务空间 | 复杂组图零售成本高；私有库不下沉 | 价格高；公开证据透明度较弱 | 需要通过评估集证明准确率和误报控制 |
| 交付方式 | 即时 AI 报告 | 即时 AI 报告 + manual review tools | AI + 专家，销售 SLA | 自助即时报告，专家复核作为第二层 |
| 最适合客户 | 个人作者、出版社批量筛查 | 出版商、机构、严肃审稿团队 | 高焦虑投稿作者、机构合规 | 实验室、机构私有库、投稿前自查 |

## 5. 对我们项目的产品策略

### 5.1 一句话定位

面向论文作者、实验室和机构的**私有库优先图像完整性筛查系统**，自动发现跨库复用、同文重复和疑似拼接/PS 痕迹，并输出可人工复核、可留档、可迭代的证据报告。

### 5.2 不建议的方向

- 不建议第一阶段承诺“全网 1 亿级图片库”。这个承诺会把项目拖入数据授权、爬取、版权、存储和召回质量的长期战场。
- 不建议直接照搬 Proofig 的无上限 sub-image 消耗体验。我们的用户场景里一篇论文 20 张图可能切成数百 panel，因此应采用 panel 阶梯包和超额规则，而不是零碎扣费。
- 不建议把“自动判定学术不端”作为卖点。系统应输出 evidence，不替代审稿或专家结论。
- 不建议一开始自研大模型。初期价值在数据真源、检索闭环、证据报告和私有库，而不是训练一个不可解释模型。

### 5.3 建议的差异化

1. **私有库默认能力**  
   从第一版就支持 public/private/submission 三类 corpus。ImageTwin 有私有库但容量随套餐变化，Proofig 私有库偏 enterprise，我们可以把“实验室/机构历史库”作为核心卖点。

2. **本地部署/私有化优先**  
   对未发表论文，用户最敏感的是数据泄露。我们可以把“不上传第三方、不用于训练、不进入公共库”写入产品原则，并在架构上支持离线部署。

3. **证据可复核，而非黑箱分数**  
   每条 finding 应包含来源、目标、裁剪区域、几何匹配、pHash/embedding 分数、模型版本、阈值和人工标记。这个方向同时吸收 Proofig 和 FigScan 的优点。

4. **专家复核作为高价增值层**  
   MVP 先做自助报告。等评估集和 UI 稳定后，提供专家复核包，目标不是“专家重新跑算法”，而是“专家确认系统证据、过滤误报、给出修改建议”。

5. **按 panel 阶梯计费，区分目标与参考成本**  
   参考 Proofig 的成本口径和 FigScan 的封顶限制，建议我们采用“基础 panel 包 + 目标 panel 阶梯 + 参考 panel 低价阶梯”的方式，而不是无上限逐 panel 扣费。

## 6. 技术底座建议

我们的技术路线应继续沿用当前文档中的原则：**系统真源手写，算法能力拼接**。

### 6.1 必须手写的模块

- `core/corpus`：article、figure、panel、feature、finding、review 的真源状态。
- `core/storage`：PDF、figure、panel、heatmap、report 的对象路径和校验。
- `core/jobs`：异步任务状态、失败重试、可追踪日志。
- `analysis/retrieval`：public/private/internal 三个 scope 的召回合并和去重。
- `analysis/evidence`：证据等级、阈值、审查语言和可解释输出。
- `review/report`：报告结构、source citation、side-by-side、overlay、heatmap。
- `review/annotation`：人工复核结论和审计记录。

这些模块是产品语义和合规边界，不能交给外部开源项目拥有。

### 6.2 可以拼接的能力

- PDF 提取：Modern Figure Extractor / PDFFigures2，fallback 使用 PyMuPDF。
- Panel 切分：panel-extractor、figpanel，必要时用简单 bbox fallback。
- pHash：`imagehash`。
- 深度 embedding：`open_clip`、SigLIP 或 sentence-transformers 图像模型。
- 向量索引：FAISS Flat 起步，规模扩大后再切 IVF/HNSW。
- 局部几何：OpenCV SIFT/ORB + RANSAC/MAGSAC，后续可接 LightGlue。
- 取证模型：TruFor、ManTraNet、Forgeryscope 思路，先 adapter 化，不把模型写死。

### 6.3 开源底座选择

不建议把 `gipplab/imageplag`、`fanghon/antiplag`、`idealo/imagededup` 任何一个作为“整系统底座”。更合理的方式是吸收其局部思想：

- `imagededup` 适合作为近重复检测参考，但它面向通用图片去重，不具备论文 PDF、panel、来源追踪、报告和人工复核语义。
- `imageplag`/`antiplag` 可参考图像抄袭检测思路，但不应继承其系统边界。
- 我们的底座应是自己的 corpus、pipeline、evidence、report，外部项目只作为 extractor/model/index adapter。

## 7. 阶段路线建议

### M1-M2：先超过“能跑 demo”的门槛

目标不是准确率，而是结构化真源：

- 建立 public/private/submission 三库。
- 导入 1000 篇公开相似文章和 100 篇私有文章。
- 从 PDF 提取 figure、caption、page、bbox。
- 将 figure 切成 panel，并保留回溯关系。

退出标准：任一 finding 都能追溯到 PDF 页码、figure、panel、原始文件和处理参数。

### M3-M4：做出竞品最基础的相似检索闭环

目标是覆盖 ImageTwin/Proofig/FigScan 都具备的核心能力：

- pHash 召回 exact/near duplicate。
- embedding 召回语义/视觉相似候选。
- SIFT/ORB + RANSAC 做几何验证。
- 输出 internal/public/private 三类相似证据。

退出标准：对 crop、rotate、flip、resize、brightness 变化的 synthetic fixtures 有稳定命中。

### M5：单图取证不要过早承诺

拼接/PS 痕迹检测是最容易误报的模块。建议先做三层输出：

- 明确支持的图像类型。
- heatmap 和异常区域，而不是直接判定“造假”。
- reliability score 和 unsupported reason。

退出标准：报告中能区分 duplicate evidence 和 forensic evidence，且 forensic 不影响 similarity 结果。

### M6：把报告做成产品核心

竞品共同证明：用户买的不是算法本身，而是“能不能降低投稿和审查风险”。报告必须包含：

- 摘要页：总风险、待复核数量、最高风险 finding。
- 证据页：source/target 并排、overlay、bbox、相似分数、几何参数。
- 取证页：heatmap、异常区域、模型版本、局限说明。
- 审计页：人工标记、时间、操作者、结论。

退出标准：非技术用户能根据报告完成复核，不需要看日志或原始模型输出。

### M7：用评估集建立可信度

不要在没有评估集前宣传准确率。建议维护小型 gold set：

- 10 篇 PDF。
- 50 张 figure。
- 若干 crop/rotate/flip/clone/splice synthetic cases。
- 若干真实误报样例。

评估指标：

- figure extraction coverage。
- panel segmentation precision/recall。
- retrieval top-k recall。
- geometry verification precision。
- forensic false-positive rate。
- report review completion time。

## 8. 商业化建议

### 8.1 自助版

建议按 panel 阶梯收费，适合作者投稿前自查：

- 个人基础：¥129/篇起，最多 25 个 target panel 和 100 个 reference panel。
- 实验室报告：¥199/篇起，按 target panel 阶梯；reference panel 使用低价阶梯或年度额度。
- 超额规则：超过 target panel、reference panel、页数或 PDF 大小后按阶梯加价或转定制。

这一路线避开 Proofig 的复杂 sub-image 心智，也不和 ImageTwin 的低价 scan 直接硬碰硬。

### 8.2 实验室/机构版

建议主打私有库：

- 小实验室：¥5,000-20,000/年，支持历史论文库、成员提交、年度额度。
- 学院/医院科室：¥30,000-100,000/年，支持多用户、私有部署、批量导入。
- 机构级：定制报价，支持 SSO、审计、API、私有模型/索引节点。

核心卖点是“避免同组/同院历史图片误用”，这比“全网最大库”更容易早期交付。

### 8.3 专家复核版

参考 FigScan 的销售报价，专家复核可以作为高价增值服务：

- 专家复核：¥699-999/篇。
- SLA：8-24 工作小时，具体取决于专家资源。
- 交付：系统报告 + 专家确认 + 修改建议 + 风险分级。

但上线前必须先定义专家复核 SOP，避免服务质量不可控。

## 9. 风险与应对

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| 公开库规模不足 | 与 ImageTwin 比外部查重弱 | 明确定位为私有库/机构历史库优先，公开库只做 related corpus |
| Panel 切分误差 | 影响 Proofig 式 sub-image 级检测 | 保留手动修正入口，报告显示切分置信度 |
| Forensic 误报 | 损害用户信任 | 不自动判罪，输出 heatmap + needs_review |
| 未发表稿件隐私 | 直接影响付费转化 | 支持本地部署，默认不上传第三方、不入公共库 |
| 销售承诺过高 | 后续交付风险 | 所有准确率承诺必须来自 gold set，不复述竞品销售口径 |
| 开源模型许可证 | 商业化受限 | 每个 adapter 登记 license、模型版本和可商用状态 |

## 10. 对当前项目文档的修订建议

建议在现有路线图中补充三项产品级要求：

- 在 M1 增加 `quote-safe privacy policy draft`：明确上传论文、私有库和公共库的边界。
- 在 M6 增加 `expert-review-ready report`：报告结构必须能被外部专家直接复核。
- 在 M7 增加 `pricing confidence metrics`：用评估集结果决定是否开放专家复核和准确率表述。

建议在 `module-catalog.md` 中保持现有 22 个模块，不新增竞品相关模块。竞品分析只影响各模块验收标准，不改变模块边界。

## 11. 参考来源

公开来源：

- ImageTwin pricing: https://imagetwin.ai/pricing/
- ImageTwin plagiarism detection: https://imagetwin.ai/image-plagiarism-detection/
- ImageTwin duplication detection: https://imagetwin.ai/image-duplication-detection/
- Wiley / Imagetwin integration news: https://www.researchinformation.info/news/wiley-adds-ai-image-fraud-detection-to-research-exchange/
- Proofig pricing: https://www.proofig.com/pricing-page/
- Proofig PubMed source plagiarism: https://www.proofig.com/image-plagiarism-detection/
- Proofig My Database: https://www.proofig.com/image-self-plagiarism-prevention-my-database/
- FigScan China: https://figscan.cn/
- FigScan International: https://figscan.org/

内部来源：

- FigScan 销售报价：¥999/篇，25 页 PDF、500 张小图、30 MB、8 个工作小时。
