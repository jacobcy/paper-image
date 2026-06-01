from paper_image.cli import build_demo_report
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


def test_cli_demo_report_contains_counts_and_safe_wording():
    output = build_demo_report("uploads/submission.pdf")

    assert "article=" in output
    assert "figures=1" in output
    assert "panels=1" in output
    assert "findings=1" in output
    assert "No high-confidence evidence found" in output
