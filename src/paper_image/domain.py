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
        return (
            f"{self.level.value}: {self.message} "
            f"via {self.algorithm} (score={self.score:.3f})"
        )


@dataclass(frozen=True)
class AICallRecord:
    call_id: str
    purpose: str
    model_id: str
    model_version: str
    prompt_template_id: str
    input_refs: tuple[str, ...]
    response_hash: str
    token_count: int
    privacy_filter_applied: bool
