# Final 28-case results (2026-08-17)

This directory contains the 28 usable cases selected for the final experiment report.

- `cases/` contains one complete result directory per selected case.
- Each case contains all 12 standard workflow outputs plus status, recovery, and audit files.
- `CASE-0140` and `CASE-0157` are excluded because they were not part of the final 28-case analysis.
- A selected run can have `status: degraded`; this indicates recovery was used, not that the result is excluded.
- The complete selected result is versioned; `*.jsonl` and `*.log` files are tracked through Git LFS.

Selected cases:

`0001, 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0011, 0014, 0015, 0020, 0026, 0032, 0144, 0145, 0150, 0156, 0160, 0164, 0167, 0170, 0186, 0195, 0196, 0198, 0202, 0279`

Current consumers:

- `scripts/compute_direct_hit28_20260817.py`
- `scripts/build_experiment_ppt_20260817.py`
