# 模块纪律

> 本文档规定模块如何拆分、如何暴露 API、如何接入开源实现。目标是避免把所有能力塞进一个巨型 pipeline，也避免让外部库成为系统真源。

## 1. 为什么需要模块纪律

论文图像筛查系统天然会吸引“胶水式堆叠”：PDF 提取、panel 检测、pHash、CLIP、FAISS、SIFT、TruFor、报告生成都可以很快串起来。但如果没有模块边界，后续会出现四类问题：

- 更换 PDF 提取器会影响入库、检索、报告。
- 替换 embedding 模型会导致 FAISS、阈值、报告解释一起漂移。
- PS/拼接检测模型输出格式不同，前端和报告被迫跟着改。
- 某个开源库的临时目录、文件名或内部分数变成产品真源。

因此本项目从第一阶段开始执行模块纪律：主系统只依赖本项目定义的 protocol、model 和 error；具体算法实现只能作为 adapter。

## 2. 模块布局

每个正式模块使用以下结构：

```text
src/paper_image/<module>/
  __init__.py        # 仅导出 public API
  protocol.py        # Protocol 或抽象接口
  models.py          # dataclass / pydantic model
  errors.py          # 模块专属异常
  _impl/             # 私有实现，外部模块不得导入
    __init__.py
    <impl>.py
  tests/
    test_protocol.py # 协议一致性测试
    test_<impl>.py   # 具体实现测试
```

当前已有的 `domain.py`、`pipeline.py` 是 M0/M1 骨架文件。进入正式模块阶段时，应逐步拆入上述结构，而不是继续扩展单文件。

## 3. Public API 规则

跨模块导入只能从模块根导入：

```python
from paper_image.corpus import CorpusStoreProtocol, ArticleRecord
from paper_image.features import FeatureExtractorProtocol, FeatureBundle
```

禁止跨模块访问 `_impl`：

```python
from paper_image.features._impl.open_clip import OpenClipExtractor  # 禁止
from paper_image.corpus._impl.sqlite import SQLiteCorpusStore       # 禁止
```

允许模块内部自由访问自己的 `_impl`。模块外只能通过 `build_*` factory 或配置装配具体实现。

## 4. Protocol-first 顺序

每个模块的实施顺序必须是：

1. 在 [module-catalog.md](module-catalog.md) 声明模块 scope、anti-scope、实现策略。
2. 写 `protocol.py` 和 `models.py`。
3. 写协议测试，定义任何实现都必须满足的行为。
4. 写第一个实现。
5. 接入上层 orchestration。

如果没有 protocol，不能先接真实开源库。开源库接入只发生在 adapter 层。

## 5. Scope 与 Anti-scope

每个模块必须声明：

- **Scope**：它负责什么。
- **Anti-scope**：它明确不负责什么。
- **Implementation**：手写、拼接、还是混合。
- **First deliverable**：第一个可验证交付物。

当一个变更不符合模块 scope 时，优先移动到正确模块；不能默默扩大模块职责。

## 6. 禁止顶层 utils

不创建 `utils/` 或 `common/` 顶层模块。

规则：

- 只服务一个模块的 helper 放进该模块 `_impl/`。
- 真正跨模块的能力必须成为独立模块，并进入 [module-catalog.md](module-catalog.md)。
- 如果 helper 看似通用但没有清晰 protocol，先在消费者模块内重复，等边界稳定再抽象。

## 7. 文件规模

目标：

- 单文件目标：200 至 300 行。
- 单文件软上限：500 行，需要在 PR 中解释。
- 单文件硬上限：800 行，除非有明确 allowlist 和拆分计划。

模块可以有多个小文件。宁愿多几个边界清晰的小文件，也不要一个巨大 service。

## 8. 开源拼接规则

开源库只能以 adapter 形式接入：

- PDF 提取器 adapter 输出本项目 `ExtractedFigure`，不能让 PDFFigures JSON 直接流入后续模块。
- Panel detector adapter 输出本项目 `DetectedPanel`，不能让 YOLO/figpanel 原始结构成为系统数据模型。
- Feature extractor adapter 输出本项目 `FeatureBundle`，不能让 open_clip tensor 形状泄漏到检索层。
- Forensic adapter 输出本项目 `ForensicFinding`，不能让 TruFor/ManTraNet 分数直接成为最终结论。

## 9. 验证规则

每个模块至少有三层验证：

- Protocol test：任何实现必须通过。
- Implementation test：当前实现的细节行为。
- Integration smoke：与上下游模块的最小闭环。

不能用“模型能跑”替代系统验证。模型输出必须被转成稳定的本项目证据结构。
