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
