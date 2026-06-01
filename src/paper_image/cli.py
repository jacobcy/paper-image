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
