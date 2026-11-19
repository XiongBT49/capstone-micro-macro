# Generation validation enhancements

Forward tooling for items 1–6. Complements frozen author-assisted scoring; does not replace `business-result-rubric.v2` or overwrite historical grades.

## Pipeline

1. **Mechanical gates** — readable / required sections / invented-fact heuristics / D1 taxonomy pattern flags. Codes only; never auto D1–D4.
2. **Structured score sheet** — blank sheet with `draft` (second-model family) and `adjudication` (official author-assisted). Agreement is draft–adjudicator, not inter-rater κ.
3. **Discrimination anchors** — 24 held-out constructed exemplars across six challenge classes × four roles. Recalibrate forward only if drift appears.
4. **Blinding** — single-answer packets before pairs; strip arm/version fields; optional length budget; sealed order-swap mapping; leak flags. Not true independent blind review.
5. **Coverage matrix** — role × materials × condition × tradeoff cells plus challenge-class claim gate. Empty challenge classes → narrow claims, do not hunt items post hoc.
6. **Expert slice** — fixed-hash stratified sample of 24–48 answers for external credibility; expert labels stored separately.

## CLI

```bash
uv run python scripts/enhance_generation_validation_20261117.py init-assets
uv run python scripts/enhance_generation_validation_20261117.py freeze-demo
uv run python scripts/enhance_generation_validation_20261117.py gates --response <path> --task-card <path> --window-id <id>
uv run python scripts/enhance_generation_validation_20261117.py coverage --task-cards Capstone报告/验证体系/实验/2026-11-13_CP08全量微观扩样/task_cards.json
```

Frozen demo index: `results/experiments/generation_validation_enhancement_20261117/`.

## Hard rules

- No paid model calls from these commands.
- Soft pattern hits are not grades.
- Do not rewrite frozen `business_review/` JSON; append revisions under new paths.
- Denominators must keep unread / unscored / gate-blocked counts visible.
