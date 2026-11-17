# Generation validation enhancement (2026-11-17)

Implements validation process items 1–6 as offline tooling and frozen assets.

- Mechanical gates triage readable/schema/section/pattern issues without assigning D1–D4.
- Structured score sheets separate second-model draft from adjudication.
- Discrimination anchors: 24 held-out constructed exemplars.
- Blinding + order-swap selection (stratified or all pairs).
- Coverage matrix over CP08 task cards with claim acceptance gate.
- Expert slice sampler for a 24–48 answer external credibility set.

`new_model_calls: 0`. Does not overwrite frozen `business_review` grades.

CLI: `uv run python scripts/enhance_generation_validation_20261117.py --help`

## Adjudication batch 2026-11-17

Added 84 citation-backed business reviews (36 expert-slice + 48 additional CP08). Expert-slice mirrors are same-assistant, not independent experts. See `adjudication_progress_20261117.json`.
