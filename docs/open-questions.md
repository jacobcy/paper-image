# Open Questions

> 本文档记录需要显式决策的问题。执行任务时不得在实现里偷偷替这些问题做产品级决定。

## OQ-1：公开库来源与授权

- **Question**：公开数据库约 1000 篇文章从哪里来，是否允许本地存储 PDF、figure、panel？
- **Why it matters**：版权和数据授权会影响 storage 设计、报告展示、是否保存原图。
- **Decision**：公开库采用两种来源：客户提供相关公开论文，或由系统按 PubMed 检索式建立领域相关论文库。PubMed 只处理公开可访问数据，系统不做全量 PubMed/全网扫描。
- **Default direction**：先支持用户提供的本地 PDF corpus；PubMed 定向检索作为增强服务，记录 query、PMID/DOI、source_url、license、retrieval_date、公开可访问性、reference_type 和入库失败原因。
- **Blocks**：M1 corpus schema 最终字段、M2 批量导入策略、报价中 corpus setup 规则。

## OQ-2：Figure 还是 Panel 作为主检索单位

- **Question**：报告中首要展示 figure 级结果还是 panel 级结果？
- **Why it matters**：panel 是查重更准确的单位，但用户阅读论文时通常按 figure 编号定位。
- **Default direction**：检索和分析以 panel 为主，报告以 figure 分组展示 panel evidence。
- **Blocks**：M2 panel 输出、M6 report schema。

## OQ-3：首个真实 PDF 提取器

- **Question**：首个真实 adapter 选择 Modern Figure Extractor/PDFFigures2、PyMuPDF、PicAxe 还是 PDF-Extract-Kit？
- **Why it matters**：不同工具对 caption、bbox、扫描 PDF 和矢量图的支持差异很大。
- **Default direction**：PDFFigures2 系作为首选，PyMuPDF page-level fallback 必须同时存在。
- **Blocks**：M2 PDF adapter。

## OQ-4：首个 panel detector

- **Question**：优先接 `researchintegrity/panel-extractor` 还是 `figpanel`？
- **Why it matters**：许可、模型下载、类别粒度和安装复杂度不同。
- **Default direction**：先实现 full-figure fallback，真实 adapter 在小 fixture 比较后确定。
- **Blocks**：M2 panel adapter。

## OQ-5：Embedding 模型选择

- **Question**：首个真实 embedding 模型用 CLIP ViT-B-32、SigLIP，还是领域模型？
- **Why it matters**：不同模型影响召回质量、速度、索引维度和阈值。
- **Default direction**：M3 先用 deterministic fake extractor 固定 contract，再接一个 CPU 可跑的小 CLIP adapter。
- **Blocks**：M3 real embedding adapter。

## OQ-6：Forensic 模型许可与部署

- **Question**：TruFor、ManTraNet、Forgeryscope 是否满足项目许可和部署约束？
- **Why it matters**：forensic 模型常有权重下载、GPU、研究用途或依赖限制。
- **Default direction**：M5 先用 fake analyzer 固定输出结构，真实模型 adapter 作为可选 profile。
- **Blocks**：M5 real forensic adapter。

## OQ-7：相似和篡改阈值如何设定

- **Question**：exact/near/partial/possible_manipulation 的阈值是固定默认、可配置，还是由 gold set 调参？
- **Why it matters**：阈值直接影响误报和漏报，不能写死成不可审计逻辑。
- **Default direction**：阈值进入 config，并在 finding 中记录实际使用的 threshold。
- **Blocks**：M4/M5 evidence merger。

## OQ-8：报告是否导出 PDF

- **Question**：MVP 报告只做 HTML/JSON，还是必须导出 PDF？
- **Why it matters**：PDF 导出会引入额外渲染依赖和版式验证。
- **Default direction**：MVP 只做 HTML/JSON；PDF 导出作为 M6 后续切片。
- **Blocks**：M6 report renderer。

## OQ-9：是否需要多用户权限

- **Question**：MVP 是否区分用户、实验室、机构级权限？
- **Why it matters**：权限会影响 private corpus、annotation 和报告访问。
- **Default direction**：MVP 单用户/单机构本地部署；保留 owner 字段，不实现复杂权限。
- **Blocks**：M1 schema、M6 UI。

## OQ-10：计费单位采用 panel

- **Question**：个人单次扫描和实验室报告如何按目标 panel 与参考 panel 分别计费？
- **Why it matters**：panel 更接近计算成本和审查工作量；复合图如果只按 top-level figure 计费，会低估复杂生物医学论文成本。
- **Decision**：对外和对内均按 panel 计费，但 target panel、internal reference panel、external reference panel、PubMed reference panel 分开计价。个人单次扫描限单篇目标 PDF，可附 3-5 篇公开参考论文，参考库总量不超过 100 reference panel。
- **Blocks**：报价页面、订单校验、report usage summary。

## OQ-11：专家审核责任边界

- **Question**：专家审核是审核 AI 报告和证据，还是重新做完整人工审查？
- **Why it matters**：这会影响专家成本、SLA、责任边界和报告措辞。
- **Decision**：专家审核负责对 AI 科研诚信报告提供人工核查与咨询服务，包括 finding 复核、误报判断、风险解释、措辞修订和修改建议；不承诺重新完成独立人工全量审查，不出具“无学术不端证明”。
- **Blocks**：专家审核 SOP、报告签署口径、专家加购价格。

## OQ-12：AI 咨询边界

- **Question**：AI 专家咨询可以回答哪些问题，如何避免越界承诺？
- **Why it matters**：产品高度 AI 化后，AI 咨询会直接影响用户信任和合规风险。
- **Decision**：AI 咨询只能基于本次报告 finding、图像证据、阈值、模型版本和 review-safe language 回答；可以解释风险、提示误报可能和建议补充材料，但不能保证”无问题”、替代人工专家结论或承诺投稿结果。
- **Blocks**：M6 report schema、M6 UI、review/annotation 咨询记录。

## OQ-13：LLM 部署模式与数据流

- **Question**：LLM 使用云端 API（OpenAI/Anthropic）还是本地部署（ollama/vLLM），以及哪些数据允许发送给 LLM？
- **Why it matters**：未发表论文的图像和内容不能随意发送给第三方模型 API。本地部署成本更高但隐私更好。数据过滤规则直接影响 AI 功能的质量和用户信任。
- **Default direction**：MVP 先支持云端 API + 严格隐私过滤（不发送原始图像像素、不发送完整论文文本，只发送结构化 finding 数据和裁剪后的 panel 缩略图）；本地部署作为企业版能力。所有 LLM 调用记录模型版本、prompt 模板 ID、输入引用和响应 hash。
- **Blocks**：core/ai gateway protocol、privacy filter 规则、M6 report 和 consultation 功能。

## OQ-14：个人单篇与年度套餐的升级衔接

- **Question**：已购买单篇服务的用户后续购买年度套餐时，已消费的单篇费用是否抵扣？已消费的 panel 和报告是否计入年度额度？
- **Why it matters**：如果不处理，实验室可能先试用几篇单篇服务再决定购买年度包，但发现已消费的费用完全沉没，产生被坑的感觉。或者反过来，已有年度套餐的用户偶尔超额时，单篇加购与年度超额价哪个更划算不明确。
- **Default direction**：购买年度套餐 30 天内可抵扣同期已购买的单篇报告费用（限本人/本机构账户）。年度套餐用户超额时自动使用套餐超额价，不需要单独购买单篇服务。
- **Blocks**：计费系统、订单管理、pricing 页面措辞。
