# 论文图像完整性筛查系统产品方案

> 本文档是产品与架构入口。模块边界、阶段路线图和实施切片分别见：
>
> - [module-discipline.md](module-discipline.md)
> - [module-catalog.md](module-catalog.md)
> - [roadmap.md](roadmap.md)
> - [implementation-slices.md](implementation-slices.md)
> - [competitive-analysis.md](competitive-analysis.md)
> - [development-estimate-roadmap.md](development-estimate-roadmap.md)
> - [pricing-strategy.md](pricing-strategy.md)

## 1. 产品定位

本项目建设一个面向论文投稿、内部审查和历史库复核的图像完整性筛查系统。系统不自动判定学术不端，而是对论文中的图像和子图进行自动筛查，输出可解释、可追溯、可人工复核的证据报告。

市场定位采用“私有库优先、投稿前自查、证据可复核、AI 咨询默认可用、专家复核可扩展”的路线。第一阶段不追求 ImageTwin 级别的全网大库，也不做全量 PubMed/全网扫描，而是先在用户最敏感的三个点上形成差异化：未发表稿件隐私、实验室/机构历史库、可用于人工判断的证据报告。

核心价值是把人工审查中最耗时的三类线索自动前置：

- 跨库图像复用：当前论文图像是否与公开库或私有历史库中的图像相似。
- 同文内部重复：同一篇论文内部是否存在重复、裁剪、旋转、翻转或局部复用。
- 拼接/PS 痕迹：图像中是否存在疑似局部篡改、拼接、噪声不一致或压缩异常区域。
- 复核与留档：把算法输出转为审稿人、专家或机构管理员可以复核、标记、留档的证据包。
- AI 咨询：围绕报告 finding、相似证据、误报可能性和修改建议提供受控问答。

## 2. 数据规模与约束

目标规模：

- 公开数据库：约 1000 篇相似文章。
- 私有数据库：约 100 篇个人或机构提交文章。
- 单篇论文：约 20 张图。
- 初始图像规模：约 20000 至 22000 张 figure，经过 panel 切分后预计增长到 50000 至 100000 个 panel。
- 商业计费：按 panel 计费，区分 target panel、内部 reference panel、外部 reference panel 和 PubMed reference panel；个人单次扫描限单篇目标 PDF，可附 3-5 篇公开参考论文且不超过 100 个 reference panel。

工程判断：

- 当前规模适合本地或单机服务架构。
- SQLite 可承担元数据真源。
- FAISS Flat 索引足以支撑初始规模，后续百万级再迁移到 IVF/HNSW。
- 文件系统可作为原始 PDF、figure、panel、heatmap、报告的对象存储。

## 3. 用户与使用场景

主要用户：

- 论文作者：提交论文前自查图像完整性。
- 实验室或机构管理员：维护私有历史库，审查新提交论文。
- 审稿或编辑人员：查看系统报告并进行人工判断。

典型流程：

1. 用户上传一篇 PDF。
2. 系统提取 figure、caption、page、bbox。
3. 系统将复合 figure 切分为 panel。
4. 系统生成 pHash、深度 embedding、局部特征。
5. 系统与公开库、私有库、本文内部进行候选召回。
6. 系统用几何验证确认疑似复用区域。
7. 若启用 forensic 模块，系统对图像运行拼接/PS 痕迹检测，生成 heatmap 和 unsupported/reliability 信息。
8. AI 生成科研诚信报告，并提供围绕报告证据的 AI 咨询。
9. 用户在报告中查看证据并标记人工结论，必要时加购人工专家确认或咨询。

## 4. 架构原则

本项目采用“系统真源手写、算法能力拼接”的架构。主系统负责状态、边界、调度、证据解释和报告；外部开源项目只作为可替换 adapter，不拥有产品语义。

原则：

- **内部真源优先**：article、figure、panel、feature、finding、review 的状态以 SQLite 元数据为真源，外部文件、FAISS 索引、模型输出都是投影或派生产物。
- **Protocol-first**：每个模块先定义输入输出协议和数据模型，再接具体实现。
- **模块可替换**：PDF 提取器、panel detector、embedding model、forensic model 都必须能替换，不能把某个开源项目写死成系统核心。
- **证据不判罪**：系统只输出 evidence 和 review 状态，不自动宣称造假、抄袭或无问题。
- **隐私优先**：submission 与 private corpus 默认不进入 public corpus，不用于训练，不自动外传到第三方服务。
- **承诺受评估约束**：准确率、召回率、误报率和专家复核 SLA 必须由评估集或运营能力支持，不能用竞品销售口径替代自己的证据。
- **AI 输出受证据约束**：AI 报告和 AI 咨询只能基于本次 finding、来源图、阈值、模型版本和报告证据生成，不得自由承诺“无问题”。
- **分阶段实施**：每个阶段只关闭一类能力，前一阶段的真源和 contract 稳定后再接算法。
- **AI 角色分层**：大模型适合做版面理解辅助、panel 切分校验、figure 类型识别、报告撰写、AI 咨询和专家审核辅助；不适合单独承担高精度查重和图像取证。正确架构是 CV/检索系统产生证据，大模型解释证据，专家审核高风险结论。所有 LLM 调用通过 core/ai 网关统一管理，记录模型版本、prompt 模板、输入引用和响应 hash。
- **LLM 隐私约束**：未发表论文图像和完整内容不能无条件发送给第三方 LLM API。core/ai 网关负责隐私过滤，控制哪些字段和图像可以发送，并在每次调用中记录是否应用了隐私过滤。

## 5. 模块拆解摘要

完整模块目录见 [module-catalog.md](module-catalog.md)。这里保留面向产品理解的摘要。

### 5.1 Corpus Manager

职责：

- 管理 `public`、`private`、`submission` 三类语料库。
- 记录 article、figure、panel、feature、analysis run 的元数据。
- 提供稳定 ID、文件路径、来源信息和状态流转。
- 强制执行语料边界：submission 不自动进入 public，private 不跨租户或跨项目泄露。

实现方式：手写。

原因：这是系统真源，不能依赖外部算法库的临时目录或私有状态。

### 5.2 PDF Ingestion Pipeline

职责：

- 接收 PDF。
- 生成 article 记录。
- 调用 PDF figure 提取器。
- 保存 figure 图片、caption、page、bbox。
- 对提取失败的 PDF 使用页面渲染 fallback。

实现方式：手写编排，拼接提取器。

候选组件：

- 首选：Modern Figure Extractor / PDFFigures2。
- fallback：PyMuPDF 页面渲染与图像块提取。
- 备选：PicAxe 或 PDF-Extract-Kit。

### 5.3 Panel Pipeline

职责：

- 将复合 figure 切分为独立 panel。
- 保存 panel bbox、label、来源 figure。
- 为查重和篡改检测提供更细粒度输入。
- 为报价提供 target/reference panel 计数，并支持用户确认或修正明显误切。

实现方式：拼接优先，必要时手写 fallback。

候选组件：

- `researchintegrity/panel-extractor`
- `figpanel`

### 5.4 Feature Pipeline

职责：

- 为每个 figure/panel 生成多路特征。
- 特征包括 `sha256`、`pHash`、深度 embedding、可选局部 descriptor。
- 将 embedding 写入 FAISS，将元数据写入 SQLite。

实现方式：手写统一接口，底层算法拼接。

候选组件：

- pHash：`imagehash`
- 深度特征：`open_clip`、SigLIP 或 sentence-transformers 图像模型
- 向量库：FAISS
- 局部特征：OpenCV SIFT/ORB

### 5.5 Similarity Search

职责：

- 对单篇论文的 figure/panel 进行 Top-K 候选召回。
- 支持三个检索范围：本文内部、公开库、私有库。
- 合并 pHash 与 embedding 召回结果。

实现方式：手写。

原因：召回策略、库边界、去重、结果解释和阈值都属于产品逻辑。

### 5.6 Geometric Verification

职责：

- 对候选相似图进行局部匹配。
- 验证裁剪、旋转、翻转、缩放、局部复用。
- 输出匹配点、单应性、inlier 数、共享区域 bbox 和验证分数。

实现方式：手写封装，底层算法拼接。

候选组件：

- OpenCV SIFT/ORB + RANSAC/MAGSAC
- LightGlue
- `researchintegrity/provenance-analysis` 的思路和参数

### 5.7 Forensic Analysis

职责：

- 对单图或 panel 检测疑似拼接、PS、局部篡改。
- 输出 heatmap、integrity score、reliability map、异常区域。

实现方式：拼接模型。

候选组件：

- TruFor
- ManTraNet
- Forgeryscope 的 panel/matcher 思路

### 5.8 Evidence Scoring

职责：

- 将多路证据合并为人工可读结果。
- 输出等级：`exact_duplicate`、`near_duplicate`、`partial_reuse`、`possible_manipulation`、`needs_review`。
- 保留所有原始分数，避免黑箱判定。

实现方式：手写。

原因：证据解释是产品核心，必须可控、可审计。

### 5.9 Review UI 与 Report

职责：

- 展示上传论文、图像、候选相似来源、匹配区域、heatmap。
- 支持人工标记：确认问题、误报、需要进一步调查。
- 导出 HTML/PDF 报告。
- 支持专家复核友好的证据包：source/target 并排、overlay、bbox、算法参数、模型版本、人工审计记录。
- 支持 AI 咨询：围绕报告 finding 解释风险、提示可能误报、生成修改建议，并记录问答。
- 支持人工专家服务加购：基础确认、快速审核、标准审核、深度审核。

实现方式：

- MVP：Streamlit 或 Gradio。
- 正式版：FastAPI + 前端应用。

## 6. MVP 范围

第一阶段只做三个必达闭环和一个 contract 闭环：

1. 上传单篇 PDF 并完成 figure/panel 提取。
2. 将公开库和私有库入库，生成特征索引。
3. 对上传论文进行相似图检索与几何验证。
4. 固定拼接/PS 痕迹检测输出 contract；未接真实模型时必须明确标记 fake、unsupported 或 not_run。

第一阶段不做：

- 自动判定学术不端。
- 复杂多租户权限。
- 自训练模型。
- 百万级分布式索引。
- 在线多人审稿协作。
- 真实专家复核 SLA。
- 对外宣称固定准确率或 99% 级别检测能力。
- 不受证据约束的开放式 AI 聊天。

## 7. 技术栈建议

- 语言：Python 3.11+
- API：FastAPI
- 原型 UI：Streamlit
- PDF/figure：Modern Figure Extractor、PDFFigures2、PyMuPDF
- Panel：panel-extractor、figpanel
- 图像处理：Pillow、OpenCV、imagehash
- 深度模型：PyTorch、open_clip、SigLIP
- 向量索引：FAISS
- 元数据：SQLite
- 报告：Jinja2 HTML，后续可转 PDF
- 测试：pytest

## 8. 开源拼接清单

建议拼接：

- Modern Figure Extractor / PDFFigures2：PDF figure 提取。
- PyMuPDF：fallback 提取和页面渲染。
- panel-extractor 或 figpanel：复合图切 panel。
- imagehash：pHash。
- open_clip 或 SigLIP：深度 embedding。
- FAISS：向量检索。
- OpenCV：SIFT/ORB/RANSAC。
- TruFor 或 ManTraNet：拼接/PS 痕迹检测。

建议只参考，不直接作为底座：

- ELIS：架构和模块划分值得参考，但整套系统复杂且 AGPL 约束明显。
- provenance-analysis：几何验证和 provenance graph 设计值得借鉴。
- imageplag：论文图像查重思路有价值，但 Python2/Caffe 栈过老。
- imagededup：可参考去重接口，不适合作论文图像审查底座。

## 9. 手写模块清单

必须手写：

- 语料库边界与元数据模型。
- 入库任务状态和文件命名规范。
- 多路特征统一接口。
- 相似检索调度与候选合并。
- 几何验证结果的数据结构。
- 证据分级和报告结构。
- UI/API 编排。
- 隐私边界、报告措辞和人工复核审计。
- 计费 panel 统计、AI 咨询记录和专家服务使用记录。

可以拼接：

- PDF figure 提取算法。
- panel 检测模型。
- pHash 与 embedding 计算。
- FAISS 索引。
- PS/拼接检测模型。

## 10. 成功标准

MVP 成功标准：

- 能导入公开库和私有库。
- 能上传单篇 PDF 并生成 figure/panel。
- 能为每个 panel 生成稳定 ID 和特征。
- 能在四类范围内检索相似图：本文内部、实验室内部库、外部参考库、PubMed 公开库。
- 能输出至少一种几何验证证据。
- 能输出 PS/拼接检测 heatmap artifact；未接真实模型时必须标记为 fake 或 unsupported。
- 能生成一份可人工复核、专家可继续判断的 HTML 报告。
- 能记录人工标记：confirmed、false_positive、needs_more_review。
- 能生成 target/reference panel 用量摘要，用于报价和套餐额度核算。
- 能围绕报告提供受证据约束的 AI 咨询记录。

质量标准：

- 每个证据结论必须保留来源图、目标图、分数、算法名称和参数。
- 没有检测证据时，不得声称“无问题”，只能输出“未发现高置信证据”。
- 所有算法模块都必须可替换，主系统不绑定单一开源项目。
- 所有商业承诺必须能追溯到 gold set 指标、模型版本或专家复核记录。
