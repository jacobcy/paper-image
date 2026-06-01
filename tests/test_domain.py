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
