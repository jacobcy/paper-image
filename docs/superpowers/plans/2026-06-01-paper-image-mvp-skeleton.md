# Paper Image MVP Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimal project skeleton for a paper image integrity screening system with stable domain models, pluggable module boundaries, and a CLI smoke path.

**Architecture:** The first implementation keeps product truth in small hand-written Python modules while leaving algorithm-heavy work behind explicit adapter interfaces. The skeleton supports two corpus scopes, article/figure/panel metadata, feature records, evidence records, and report summaries without binding the project to any single extraction or forensic backend.

**Tech Stack:** Python 3.11+, pytest, dataclasses, argparse, SQLite/FAISS-ready interfaces, filesystem storage.

---

## File Structure

- `pyproject.toml`: project metadata, Python version, pytest configuration.
- `src/paper_image/__init__.py`: package version and public package marker.
- `src/paper_image/domain.py`: typed domain dataclasses and enums that define system truth.
- `src/paper_image/pipeline.py`: orchestration contracts and no-op demo pipeline for smoke testing.
- `src/paper_image/cli.py`: CLI entrypoint for validating skeleton wiring.
- `tests/test_domain.py`: tests for corpus scope, stable IDs, and review-safe wording.
- `tests/test_pipeline.py`: tests for demo pipeline output and module boundaries.

### Task 1: Project Metadata

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create pytest configuration**

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "paper-image"
version = "0.1.0"
description = "Paper image integrity screening MVP skeleton"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
paper-image = "paper_image.cli:main"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add python project metadata"
```

### Task 2: Domain Model

**Files:**
- Create: `tests/test_domain.py`
- Create: `src/paper_image/__init__.py`
- Create: `src/paper_image/domain.py`

- [ ] **Step 1: Write failing domain tests**

```python
from paper_image.domain import (
    AnalysisFinding,
    ArticleRecord,
    CorpusScope,
    EvidenceLevel,
    FigureRecord,
    PanelRecord,
    make_stable_id,
)


def test_stable_id_is_repeatable_and_namespaced():
    first = make_stable_id("article", "private", "sha256:abc")
    second = make_stable_id("article", "private", "sha256:abc")
    other = make_stable_id("article", "public", "sha256:abc")

    assert first == second
    assert first.startswith("article_")
    assert first != other


def test_article_figure_panel_records_keep_corpus_boundaries():
    article = ArticleRecord(
        article_id="article_1",
        scope=CorpusScope.PRIVATE,
        title="Submitted manuscript",
        source_path="uploads/paper.pdf",
        source_sha256="abc",
    )
    figure = FigureRecord(
        figure_id="figure_1",
        article_id=article.article_id,
        page=3,
        caption="Figure 1",
        image_path="storage/figure_1.png",
        bbox=(10.0, 20.0, 300.0, 400.0),
    )
    panel = PanelRecord(
        panel_id="panel_1",
        figure_id=figure.figure_id,
        label="A",
        image_path="storage/panel_1.png",
        bbox=(12.0, 22.0, 140.0, 180.0),
    )

    assert article.scope is CorpusScope.PRIVATE
    assert figure.article_id == article.article_id
    assert panel.figure_id == figure.figure_id


def test_finding_summary_uses_review_safe_language():
    finding = AnalysisFinding(
        finding_id="finding_1",
        level=EvidenceLevel.NEEDS_REVIEW,
        target_panel_id="panel_1",
        message="No high-confidence evidence found",
        score=0.0,
        algorithm="demo",
    )

    assert "No high-confidence evidence found" in finding.review_summary()
    assert "no problem" not in finding.review_summary().lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_domain.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'paper_image'`.

- [ ] **Step 3: Implement minimal domain model**

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum


class CorpusScope(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SUBMISSION = "submission"


class EvidenceLevel(str, Enum):
    EXACT_DUPLICATE = "exact_duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    PARTIAL_REUSE = "partial_reuse"
    POSSIBLE_MANIPULATION = "possible_manipulation"
    NEEDS_REVIEW = "needs_review"


def make_stable_id(prefix: str, *parts: str) -> str:
    payload = "\x1f".join(parts).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"{prefix}_{digest}"


@dataclass(frozen=True)
class ArticleRecord:
    article_id: str
    scope: CorpusScope
    title: str
    source_path: str
    source_sha256: str


@dataclass(frozen=True)
class FigureRecord:
    figure_id: str
    article_id: str
    page: int
    caption: str
    image_path: str
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class PanelRecord:
    panel_id: str
    figure_id: str
    label: str
    image_path: str
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class AnalysisFinding:
    finding_id: str
    level: EvidenceLevel
    target_panel_id: str
    message: str
    score: float
    algorithm: str
    source_panel_id: str | None = None

    def review_summary(self) -> str:
        return f"{self.level.value}: {self.message} via {self.algorithm} (score={self.score:.3f})"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_domain.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/paper_image/__init__.py src/paper_image/domain.py tests/test_domain.py
git commit -m "feat: add paper image domain model"
```

### Task 3: Pipeline Contracts

**Files:**
- Create: `tests/test_pipeline.py`
- Create: `src/paper_image/pipeline.py`

- [ ] **Step 1: Write failing pipeline tests**

```python
from paper_image.domain import CorpusScope, EvidenceLevel
from paper_image.pipeline import DemoScreeningPipeline, ScreeningRequest


def test_demo_pipeline_returns_review_safe_submission_report():
    pipeline = DemoScreeningPipeline()
    request = ScreeningRequest(
        pdf_path="uploads/submission.pdf",
        scope=CorpusScope.SUBMISSION,
        compare_scopes=(CorpusScope.PUBLIC, CorpusScope.PRIVATE),
    )

    report = pipeline.screen_submission(request)

    assert report.article.scope is CorpusScope.SUBMISSION
    assert report.figures
    assert report.panels
    assert report.findings
    assert report.findings[0].level is EvidenceLevel.NEEDS_REVIEW
    assert "No high-confidence evidence found" in report.findings[0].message


def test_demo_pipeline_records_compare_scopes():
    request = ScreeningRequest(
        pdf_path="uploads/submission.pdf",
        scope=CorpusScope.SUBMISSION,
        compare_scopes=(CorpusScope.PUBLIC, CorpusScope.PRIVATE),
    )

    assert request.compare_scopes == (CorpusScope.PUBLIC, CorpusScope.PRIVATE)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -q`

Expected: FAIL with `ModuleNotFoundError` or missing `paper_image.pipeline`.

- [ ] **Step 3: Implement minimal pipeline contracts**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from paper_image.domain import (
    AnalysisFinding,
    ArticleRecord,
    CorpusScope,
    EvidenceLevel,
    FigureRecord,
    PanelRecord,
    make_stable_id,
)


@dataclass(frozen=True)
class ScreeningRequest:
    pdf_path: str
    scope: CorpusScope
    compare_scopes: tuple[CorpusScope, ...]


@dataclass(frozen=True)
class ScreeningReport:
    article: ArticleRecord
    figures: tuple[FigureRecord, ...]
    panels: tuple[PanelRecord, ...]
    findings: tuple[AnalysisFinding, ...]


class DemoScreeningPipeline:
    def screen_submission(self, request: ScreeningRequest) -> ScreeningReport:
        pdf_name = Path(request.pdf_path).name
        article_id = make_stable_id("article", request.scope.value, pdf_name)
        article = ArticleRecord(
            article_id=article_id,
            scope=request.scope,
            title=Path(pdf_name).stem or "submission",
            source_path=request.pdf_path,
            source_sha256="demo",
        )
        figure = FigureRecord(
            figure_id=make_stable_id("figure", article_id, "1"),
            article_id=article_id,
            page=1,
            caption="Demo extracted figure",
            image_path="storage/demo/figure_1.png",
            bbox=(0.0, 0.0, 1.0, 1.0),
        )
        panel = PanelRecord(
            panel_id=make_stable_id("panel", figure.figure_id, "A"),
            figure_id=figure.figure_id,
            label="A",
            image_path="storage/demo/panel_1A.png",
            bbox=(0.0, 0.0, 1.0, 1.0),
        )
        finding = AnalysisFinding(
            finding_id=make_stable_id("finding", panel.panel_id, "demo"),
            level=EvidenceLevel.NEEDS_REVIEW,
            target_panel_id=panel.panel_id,
            message="No high-confidence evidence found in demo pipeline",
            score=0.0,
            algorithm="demo",
        )
        return ScreeningReport(
            article=article,
            figures=(figure,),
            panels=(panel,),
            findings=(finding,),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/paper_image/pipeline.py tests/test_pipeline.py
git commit -m "feat: add screening pipeline contracts"
```

### Task 4: CLI Smoke Path

**Files:**
- Create: `src/paper_image/cli.py`
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing CLI test**

```python
from paper_image.cli import build_demo_report


def test_cli_demo_report_contains_counts_and_safe_wording():
    output = build_demo_report("uploads/submission.pdf")

    assert "article=" in output
    assert "figures=1" in output
    assert "panels=1" in output
    assert "findings=1" in output
    assert "No high-confidence evidence found" in output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py::test_cli_demo_report_contains_counts_and_safe_wording -q`

Expected: FAIL with missing `paper_image.cli`.

- [ ] **Step 3: Implement CLI helper and entrypoint**

```python
from __future__ import annotations

import argparse

from paper_image.domain import CorpusScope
from paper_image.pipeline import DemoScreeningPipeline, ScreeningRequest


def build_demo_report(pdf_path: str) -> str:
    pipeline = DemoScreeningPipeline()
    report = pipeline.screen_submission(
        ScreeningRequest(
            pdf_path=pdf_path,
            scope=CorpusScope.SUBMISSION,
            compare_scopes=(CorpusScope.PUBLIC, CorpusScope.PRIVATE),
        )
    )
    first_finding = report.findings[0].review_summary()
    return (
        f"article={report.article.article_id} "
        f"figures={len(report.figures)} "
        f"panels={len(report.panels)} "
        f"findings={len(report.findings)} "
        f"summary={first_finding}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paper image screening demo")
    parser.add_argument("pdf_path", help="Path to a submission PDF")
    args = parser.parse_args(argv)
    print(build_demo_report(args.pdf_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and CLI smoke**

Run: `pytest -q`

Expected: PASS.

Run: `python -m paper_image.cli uploads/submission.pdf`

Expected: output contains `figures=1 panels=1 findings=1`.

- [ ] **Step 5: Commit**

```bash
git add src/paper_image/cli.py tests/test_pipeline.py
git commit -m "feat: add screening cli smoke path"
```

## Self-Review

- Spec coverage: The plan implements the initial skeleton only: domain truth, module boundaries, and smoke execution. Algorithm integrations are intentionally outside this skeleton and should be planned as separate tasks.
- Placeholder scan: No implementation step depends on unspecified code.
- Type consistency: `CorpusScope`, `EvidenceLevel`, `ScreeningRequest`, `ScreeningReport`, and `AnalysisFinding` are named consistently across tasks.
