"""Forward validation enhancements for generation review.

These tools add mechanical gates, structured score sheets, discrimination
anchors, blinding helpers, coverage matrices, and expert-slice sampling.
They never invent D1–D4 grades, overwrite frozen reviews, or issue model calls.
"""

from src.generation_validation.mechanical_gates import run_mechanical_gates
from src.generation_validation.score_sheet import (
    blank_score_sheet,
    validate_score_sheet,
    draft_adjudication_agreement,
)
from src.generation_validation.blinding import (
    blind_single_answer_packet,
    blind_pair_packet,
    select_order_swap_pairs,
)
from src.generation_validation.coverage import build_coverage_matrix
from src.generation_validation.expert_slice import sample_expert_slice
from src.generation_validation.anchors import load_discrimination_anchors

__all__ = [
    "run_mechanical_gates",
    "blank_score_sheet",
    "validate_score_sheet",
    "draft_adjudication_agreement",
    "blind_single_answer_packet",
    "blind_pair_packet",
    "select_order_swap_pairs",
    "build_coverage_matrix",
    "sample_expert_slice",
    "load_discrimination_anchors",
]
