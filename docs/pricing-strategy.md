# 报价策略与商业化方案

日期：2026-06-01  
适用阶段：商业 Beta 前后  
关联文档：[competitive-analysis.md](competitive-analysis.md)、[product-plan.md](product-plan.md)、[open-questions.md](open-questions.md)

## 1. 定价结论

价格体系需要保持个人版和实验室版一致：所有输入先由 AI 切分为 panel，再按 panel 计费。区别不在计费口径，而在额度、数据来源、是否长期保存私有库、是否包含 AI 咨询和赠送的基础专家服务。

统一商业公式：

```text
报告价格 = 目标文章 target panel 阶梯
        + 参考文章 reference panel 阶梯
        + PubMed 公开数据检索/建库费用
        + AI 专家咨询额度
        + 人工专家审核加购
```

核心判断：

- 我们没有大规模公开库，因此基础价应低于 FigScan 深度专家审查，也应避免与 ImageTwin 全网 scan 正面比较。
- 我们的卖点是“目标文章 + 用户指定参考文章 + 实验室内部历史库 + PubMed 公开相关库”的科研诚信报告。
- 个人版是轻量入口，实验室版是主产品。
- 人工专家审核是额外收费，但实验室基础包可以赠送少量“基础专家确认与咨询”次数。
- 产品应高度 AI 化：AI 自动切 panel、AI 生成报告、AI 解释 finding、AI 咨询问答；人工专家只处理确认、咨询和高风险报告复核。

## 2. Panel 与数据角色定义

### 2.1 目标 panel

**目标 panel** 指本次要审查的目标文章或目标 figure 中的 panel。它们进入报告主体，是主要计费对象。

来源：

- 单篇目标 PDF。
- 用户直接上传的目标 figure。
- Word/图片文件中的目标图像。

如果一张复合图包含 A/B/C/D 四个子图，则按 4 个 target panel 计费。

### 2.2 参考 panel

**参考 panel** 指用于对比的背景库 panel。它们用于相似检索和证据来源，不是本次报告的被审查主体。

参考 panel 分三类：

- **内部 reference panel**：实验室历史文章、历史投稿、用户私有库、同组前作。
- **外部 reference panel**：客户提供的公开论文、公开 figure、DOI/PMID 清单或 PDF。
- **PubMed reference panel**：系统按 PubMed 检索式从公开可访问数据中获得的相关论文 panel。

### 2.3 用户直接提供 figure

用户可以不提供完整 PDF，而是直接提供若干 figure。系统仍使用 AI panel detector 切分，并要求用户声明这些 figure 的角色：

- 作为目标图：计入 target panel。
- 作为参考图：计入 reference panel。
- 角色不明确：默认按目标图计费，避免把待审查图像误放入参考库。

### 2.4 计费原则

- 对外和对内均按 panel 计费。
- 目标 panel 与 reference panel 分开计价。
- 内部 reference panel 最便宜，因为它属于实验室长期私有库。
- 外部 reference panel 次之，因为客户已给出范围。
- PubMed reference panel 最贵，因为包含检索、公开可访问性判断、下载、解析失败记录。
- 报告展示仍以 figure 分组，避免用户阅读困难。
- AI 切分结果必须允许用户确认；明显误切应支持人工修正或重新计数。

### 2.5 AI 咨询 token 计费

AI 咨询统一按实际消耗的 token 计量，以"万 token"为计费单位。

参考换算：

- 一次典型对话约消耗 0.3 万 token（含输入 finding 上下文 + 问题 + 回答）。
- 复杂咨询（多条 finding、长上下文）可能消耗 0.5-1.0 万 token。
- 报告中 AI 生成的叙述段落约消耗 1-3 万 token，已包含在报告基础价中，不单独计量。

计费规则：

- 每个套餐包含基础 AI 咨询 token 额度。
- 超出额度的部分按客户类型阶梯价计费。
- UI 上以"剩余约 X 次对话"展示，内部按实际 token 扣减。
- 所有 AI 调用通过 core/ai 网关记录 token 消耗、模型版本和 prompt 模板 ID。

统一超额价：

| 客户类型 | 超额单价 | 约等于 |
| --- | ---: | ---: |
| 个人 / 单篇加购 | ¥2 / 万 token | ~¥0.6 / 次对话 |
| 实验室单篇超额 | ¥1.5 / 万 token | ~¥0.45 / 次对话 |
| Lab Starter 年度超额 | ¥0.8 / 万 token | ~¥0.24 / 次对话 |
| Lab Standard 年度超额 | ¥0.5 / 万 token | ~¥0.15 / 次对话 |
| Lab Pro 年度超额 | ¥0.3 / 万 token | ~¥0.09 / 次对话 |

个人到 Lab Pro 超额倍率：6.7 倍（旧方案按"次问答"计费时为 38 倍）。

## 3. 产品是否支撑

当前模块设计基本支撑该价格体系，但需要明确几个产品能力：

- `extract/panel` 支撑所有 PDF/figure 统一换算为 panel。
- `core/corpus` 支撑 target/internal/external/pubmed 的语料角色和隔离。
- `analysis/retrieval` 支撑目标 panel 对内部库、外部库、PubMed 公开库分别检索。
- `review/report` 支撑 AI 科研诚信报告、证据解释、AI 咨询上下文。
- `review/annotation` 支撑人工专家确认、咨询记录、误报标记和审计。
- `app/ui` 需要支持 panel 计数确认、费用预估、AI 咨询和专家服务加购。

不建议为了 AI 咨询新增模块。MVP 阶段可由 `review/report` 生成解释和建议，由 `review/annotation` 保存 AI/人工咨询记录；等咨询功能变复杂后再评估是否拆成独立 `review/consultation` 模块。

## 4. 个人单次扫描

个人版只支持单篇目标文章，不提供长期私有库。可附少量公开参考文章，适合投稿前初筛。

限制：

- 仅限 1 篇目标 PDF 或一组目标 figure。
- 可提供 3-5 篇公开参考论文。
- reference panel 总量不超过 100。
- PubMed 轻量检索最多补足到 100 reference panel。
- 不保存长期私有库。

### 4.1 个人基础包

| 套餐 | target panel | included reference panel | AI 咨询 token | 建议价格 |
| --- | ---: | ---: | ---: | ---: |
| Personal S | 1-25 | ≤100 | 1 万（约 3 次对话） | ¥129 / 篇 |
| Personal M | 26-50 | ≤100 | 2 万（约 6 次对话） | ¥199 / 篇 |
| Personal L | 51-100 | ≤100 | 3 万（约 10 次对话） | ¥299 / 篇 |
| 超过 100 target panel | 转实验室单篇 | 定制 | 定制 | 不建议个人入口承接 |

个人 AI 咨询说明：

- AI 可解释 finding、提示可能误报、建议用户回看哪些图。
- AI 咨询不得给出”保证无问题”结论。
- 个人版默认不含人工专家服务。
- AI 咨询按实际消耗 token 计量，UI 显示”剩余约 X 次对话”。
- 基础 token 额度用完后，可按 ¥2 / 万 token 加购（见 2.5 节）。

### 4.2 个人加购

| 项目 | 建议价格 | 限制 |
| --- | ---: | --- |
| target panel 超额 | ¥4 / panel | 仅适用于 101-150 target panel，再高转实验室单篇 |
| PubMed 轻量补足 | +¥99 / 篇 | 最多补足到 100 reference panel，只查公开可访问数据 |
| AI 咨询 token 加量 | ¥2 / 万 token（约 ¥0.6 / 次对话） | 仅围绕本报告 |
| 人工专家快速确认 | +¥399 / 篇 | ≤50 target panel，48 小时 |
| 人工专家标准咨询 | +¥699 / 篇 | ≤100 target panel，48-72 小时 |

## 5. 实验室单篇科研诚信报告

实验室单篇报告与个人版使用同一计费单位，但允许更大的 reference panel，支持内部私有库、外部公开参考库和 PubMed 公开数据补足。

### 5.1 target panel 阶梯

| target panel | 使用已有内部库 | 外部参考增强 | PubMed 补足增强 | AI 咨询 token | 建议价格 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1-50 | 包含 | ≤500 reference panel | ≤500 reference panel | 3 万（约 10 次） | ¥199 / 篇起 |
| 51-100 | 包含 | ≤500 reference panel | ≤500 reference panel | 5 万（约 16 次） | ¥299 / 篇起 |
| 101-200 | 包含 | ≤1,000 reference panel | ≤1,000 reference panel | 8 万（约 26 次） | ¥499 / 篇起 |
| 201-300 | 包含 | ≤1,000 reference panel | ≤1,000 reference panel | 12 万（约 40 次） | ¥699 / 篇起 |
| 301-500 | 包含 | ≤2,000 reference panel | ≤2,000 reference panel | 20 万（约 66 次） | ¥999 / 篇起 |
| 超过 500 | 定制 | 定制 | 定制 | 定制 | 先评估 |

上表为目标文章基础报告价，不包含超出额度的 reference panel、PubMed topic 建库和人工专家审核。

### 5.2 reference panel 阶梯

| reference panel 类型 | 1-100 | 101-500 | 501-2,000 | 2,001-5,000 | 超过 5,000 |
| --- | ---: | ---: | ---: | ---: | --- |
| 内部 reference panel | 包含在实验室库 | ¥0.1 / panel | ¥0.08 / panel | ¥0.05 / panel | 年度库报价 |
| 外部 reference panel | 包含在单篇基础额度 | ¥0.5 / panel | ¥0.3 / panel | ¥0.2 / panel | corpus 建库报价 |
| PubMed reference panel | +¥99 / 篇 | ¥0.8 / panel | ¥0.5 / panel | ¥0.35 / panel | topic 建库报价 |

解释：

- 内部 reference panel 应尽量通过年度套餐覆盖，单篇临时计费只是兜底。
- 外部 reference panel 因客户提供了范围，成本低于 PubMed。
- PubMed reference panel 只限公开可访问数据，价格包含检索和失败记录。

### 5.3 价格示例

示例 A：个人用户，目标文章 42 target panel，提供 4 篇参考论文共 80 reference panel。  
报价：Personal M，¥199。

示例 B：实验室用户，目标文章 86 target panel，使用已有内部库，并临时提供 300 外部 reference panel。  
报价：基础 ¥299，外部 reference panel 在 500 内包含，总价 ¥299。

示例 C：实验室用户，目标文章 160 target panel，需要 PubMed 补足 1,200 reference panel。  
报价：基础 ¥499，前 1,000 reference panel 包含，超出 200 按 ¥0.5/panel 计 ¥100，总价 ¥599。

示例 D：复杂文章 420 target panel，参考库 3,000 外部 reference panel。  
报价：基础 ¥999，前 2,000 reference panel 包含，超出 1,000 按 ¥0.2/panel 计 ¥200，总价 ¥1,199。

## 6. 相关库与 corpus 建库

### 6.1 内部私有库

内部私有库是实验室版的核心卖点，不建议个人版开放。

| 规模 | 建议价格 | 说明 |
| --- | ---: | --- |
| ≤20,000 internal reference panel | 包含在 Starter | 实验室历史库起步 |
| 20,001-100,000 internal reference panel | ¥0.08 / panel | 按成功入库 panel 计费 |
| 超过 100,000 internal reference panel | 定制 | 需要评估部署与索引策略 |

### 6.2 外部公开参考库

| 规模 | 建议价格 | 说明 |
| --- | ---: | --- |
| ≤1,000 篇或 ≤20,000 external reference panel | ¥1,500 / corpus | 客户提供 PDF/DOI/PMID 清单 |
| 20,001-100,000 external reference panel | ¥0.15 / panel | 按成功入库 panel 计费 |
| 超过 100,000 external reference panel | 定制 | 建议转年度或机构方案 |

### 6.3 PubMed 公开数据 topic

| 项目 | 建议价格 | 说明 |
| --- | ---: | --- |
| 检索策略设计 | ¥800 / topic | query、MeSH、关键词、范围确认 |
| ≤1,000 篇或 ≤20,000 PubMed reference panel | ¥3,000 / topic | 公开数据检索、入库、失败记录 |
| 20,001-100,000 PubMed reference panel | ¥0.25 / panel | 按成功入库 panel 计费 |
| 定期刷新 | ¥800 / 次 / topic | 最多 1,000 篇新增候选 |

## 7. AI 咨询与人工专家服务

### 7.1 AI 专家咨询

AI 专家咨询是产品的默认能力，包含在个人和实验室基础报告中。AI 咨询按实际消耗的 token 计量（万 token 为计费单位），每个套餐包含基础 token 额度，超出部分按 2.5 节阶梯价计费。一次典型对话约消耗 0.3 万 token；报告生成消耗的 token 已包含在报告基础价中，不单独计量。

AI 咨询可回答：

- 某条 finding 为什么被标记。
- 哪些相似图最值得人工复核。
- 哪些 finding 可能是误报。
- 如何补充原始实验记录或图片来源说明。
- 报告中的风险等级如何理解。

AI 咨询不能回答：

- 保证论文没有问题。
- 替代人工专家最终确认。
- 给出法律、伦理或投稿结果保证。

### 7.2 人工专家服务

人工专家负责对 AI 科研诚信报告提供人工核查与咨询服务，包括 finding 复核、误报判断、风险解释、措辞修订和修改建议。

| 服务 | 建议价格 | 适用范围 | 交付 |
| --- | ---: | --- | --- |
| 基础专家确认 | +¥199 / 次 | ≤3 条 finding 或 ≤30 target panel | 简短确认与咨询 |
| 专家快速审核 | +¥399 / 篇 | ≤50 target panel | 48 小时 |
| 专家标准审核 | +¥699 / 篇 | ≤100 target panel | 48-72 小时 |
| 专家深度审核 | +¥999 / 篇 | ≤300 target panel 或 ≤500 total reviewed panel | 3-5 个工作日 |
| 超复杂专家审核 | 定制 | >300 target panel 或争议样本较多 | 单独评估 |

## 8. 实验室年度套餐

年度套餐是主销售模式。它把内部库、外部相关库、PubMed topic、AI 咨询和少量基础专家服务打包，弥补没有大规模公开库的短板。

| 套餐 | 年费 | 报告额度 | target panel 额度 | reference panel 额度 | PubMed topic | AI 咨询 token | 赠送基础专家服务 | 用户数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Lab Starter | ¥9,800 / 年 | 100 篇 | 5,000 | 20,000 | 1 | 300 万（约 1,000 次） | 2 次/年 | 2 |
| Lab Standard | ¥24,800 / 年 | 400 篇 | 25,000 | 100,000 | 3 | 1,500 万（约 5,000 次） | 8 次/年 | 5 |
| Lab Pro | ¥49,800 / 年 | 1,000 篇 | 75,000 | 300,000 | 5 | 5,000 万（约 16,000 次） | 20 次/年 | 10 |
| Institution Pilot | ¥98,000 起 / 年 | 定制 | 定制 | 定制 | 定制 | 定制 | 定制 | 定制 |

赠送基础专家服务说明：

- 仅用于确认和咨询，不等同于完整专家审核。
- 每次限 3 条 finding 或 30 target panel 以内。
- 超出后按基础专家确认或专家审核加购。

套餐超额建议：

| 超额项 | Starter | Standard | Pro |
| --- | ---: | ---: | ---: |
| target panel 超额 | ¥1.2 / panel | ¥0.8 / panel | ¥0.5 / panel |
| reference panel 超额 | ¥0.2 / panel | ¥0.15 / panel | ¥0.1 / panel |
| AI 咨询 token 超额 | ¥0.8 / 万 token | ¥0.5 / 万 token | ¥0.3 / 万 token |
| 新增 PubMed topic | ¥3,000 / topic | ¥2,500 / topic | ¥2,000 / topic |
| 完整专家审核 | 9 折 | 85 折 | 8 折 |

## 9. 私有化与机构报价

如果客户要求本地部署或私有化，应单独报价，不进入普通年度套餐。

建议报价：

- 私有化部署初始化：¥30,000-80,000 / 次。
- 年度维护：部署费的 20%-30%。
- GPU/服务器由客户提供时，价格下限可降低。
- API/SSO/审计日志：按模块另行报价。
- 大规模历史库导入：按 reference panel 计费，建议 ¥0.05-0.2 / panel，取决于 PDF 可用性和解析成功率。

## 10. 价格体系评估

这套价格体系整体合理，原因是：

- 与 Proofig 一样按 panel 反映真实处理成本，但通过基础包和阶梯价降低用户焦虑。
- 与 FigScan 相比，AI 报告价格明显更低，专家深度审核才接近 ¥999。
- 与 ImageTwin 相比，我们承认没有全网大库，因此用相关库、内部库和 PubMed 定向公开数据补足，并给出折扣。
- 个人版和实验室版口径一致，便于系统实现和销售解释。
- 实验室套餐把内部历史库和 AI 咨询打包，符合主目标客户需求。

需要谨慎的地方：

- Panel 自动切分必须提供用户确认，否则误切会直接影响价格信任。
- AI 咨询的回答要严格引用报告 finding 和证据，不能自由发挥。
- 赠送基础专家服务要限制范围，否则会被用成完整人工审核。
- PubMed 只能说“公开可访问相关数据”，不能说“PubMed 全库查重”。

## 11. 推荐首发 SKU

首发建议只保留三个 SKU：

1. **个人 AI 初筛**：¥129 / 篇，最多 25 target panel，最多 100 reference panel，参考论文限 3-5 篇公开论文，含 1 万 AI 咨询 token（约 3 次对话），超额 ¥2 / 万 token。
2. **实验室 AI 科研诚信报告**：¥199 / 篇起，按 target panel 阶梯计费，基础包含 100-500 reference panel 和 3-20 万 AI 咨询 token，超额 ¥1.5 / 万 token。
3. **实验室年度 Starter**：¥9,800 / 年，100 篇报告、5,000 target panel、20,000 reference panel、1 个 PubMed topic、300 万 AI 咨询 token（约 1,000 次对话）、2 次基础专家确认。

首发阶段不要同时推出太多套餐。先验证客户是否愿意为“内部库 + 外部相关库 + PubMed 公开补足 + AI 科研诚信报告 + AI 咨询”付费，再决定是否扩展 Standard、Pro 和机构版。
