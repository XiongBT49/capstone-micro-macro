# Annotated revision — validation / organization-mechanism evidence

**Audience:** authors replacing interim-report planned ablation language with completed PIC results.  
**Clean drop-in (Chinese):** [`CAPSTONE_validation_methodology_revision.docx`](CAPSTONE_validation_methodology_revision.docx)  
**Original interim:** [`../references/submitted_interim.pdf`](../references/submitted_interim.pdf) (English; §4 Experiments, §5 Results, esp. §5.5 Planned ablation)  
**PIC delivery reviewed:** `21 nov updates/` (2026-11-20/21 packages)

Annotation tags:

- `[KEEP]` — interim claim still supported; do not overwrite with new numbers.
- `[REPLACE]` — interim “planned” or outdated wording should be removed / rewritten.
- `[NEW]` — completed experiment not present in the interim.
- `[BOUNDARY]` — claim hygiene required wherever the number is used.

---

## 0. What the PIC delivered (inventory)

| Package | Path under `21 nov updates/` | Role in drop-in |
|---|---|---|
| Micro D3/S4/G3 (433 units, 4,690 calls) | `micro_D3_S4_experiment_package_20261120.zip` → `_extracted/d3s4/` | §1 primary call-matched organization contrast |
| CP07 final-only ablation (8 windows, 72 calls) | `组织消融实验_8个窗口_72次调用.zip` → `_extracted/ablation/` | §2 input-sensitivity / mechanism probe |
| Paper analysis bundle (micro-org 12 + e2e 12 + ablation report) | `Capstone_论文分析数据包_20261120.zip` → `_extracted/paper/` | §3–§4 parallel tender-pipeline scores + lifecycle pairing |
| Drafting notes | `micro_exp.docx` (+ `.bak`) | Prior Chinese draft; this revision supersedes it as the drop-in |

Accepted ablation summary frozen at  
`results/experiments/org_ablation_sensitivity_20261119/accepted_20261120/`  
(REPORT / metrics / closing). Full job payloads remain in the PIC zip / `_extracted/ablation/jobs/`.

---

## 1. Mapping onto the interim report

### 1.1 Interim §5.5 “Planned ablation and sensitivity studies” — `[REPLACE]`

Interim (p. 16–17) planned four mechanism removals (A1 single-agent firm, A2 rule consortia, A3 no reconsideration, A4 no cross-stage memory) plus pool/temperature sensitivity, **not yet run**.

**Revision stance:** do **not** pretend those four A1–A4 runs are done. Replace the “planned” paragraph with completed, differently designed probes that answer related questions about multi-agent value:

| Completed probe | Answers (narrowly) | Does **not** answer |
|---|---|---|
| §1 S4 vs D3 vs G3 @ fixed 4 calls | Call-budget-matched text quality; role-label vs parallel structure | Interim A1–A4; real profit |
| §2 CP07 dropout / order / gate bit-flip | Final-decision sensitivity to role text & verified conditions | Full process re-deliberation |
| §3 single / solo / multi @ tender stages | Stage-text rubric under shared stage inputs | Same rubric as §1; causal role split alone |
| §4 paired e2e lifecycle | Whether micro awards enter macro with comparable terminals | Stable quality/cost gain from multi |

### 1.2 Interim §5.1–5.4 operational / hit@1 results — `[KEEP]`

28-case degraded-complete run, consortium funnel, package hit@1 64.8% vs size-matched random 57.6% (+7.2 pp) remain historical evidence. **Do not pool** with §1 auto-quality deltas or §3 R1–R6 scores.

### 1.3 Interim discussion “absence of ablations” — `[REPLACE]`

Discussion noted missing ablations and single-run variance. Update to: organization-mechanism ablations **now exist** on separate surfaces; variance / human calibration / A1–A4-style protocol ablations remain open.

---

## 2. Drop-in body (Chinese) — annotated outline

The Word file is the paste-ready section. Below: interpretation + tags. Numbers match PIC primary reports unless noted.

### §1 微观决策机制对照（固定四次调用 S4 / D3 / G3） — `[NEW]` primary

**Design.** 433 project–role units; frozen 12-candidate pools; deepseek-flash; T=0; non-thinking; 4 generation calls/arm. Dev 92 / val 46 / test 295 by project-group hash. G3 = same “3 opinions + manager” as D3 but generic role prompts on a pre-registered 60-unit subset.

**Primary endpoint — strict dual-order auto score (0–100).** Test complete pairs **169/295** (57.29%): S4 71.36, D3 72.64, Δ **+1.28** (~**+1.79%**), 95% CI **crosses 0**. 8% relative target (≈77.07) **missed**. `[BOUNDARY]`

**Pre-registered length sensitivity (reason cap 40→160 chars, no new calls).** Test **295/295**: Δ **+1.01** (~**+1.41%**), CI does **not** cross 0; still ≪ 8%. Does not replace strict primary. `[BOUNDARY]`

**G3.** Strict 37/60: D3−G3 **−0.19** (CI crosses 0). No significant net gain from specialized role labels under matched structure. `[BOUNDARY]` — supports “much of D3−S4 is multi-step / multi-opinion structure,” not “roles never matter.”

**Cost.** 4,690 settled calls; ~¥51.79 under frozen rate card. D3 generation ≈4.1% cheaper than S4 in this run (cache/length), not a guaranteed saving.

**Auxiliary Top-3 fusion hit (drafting note).** Some drafting notes report S4 257/433 (59.35%) vs D3 277/433 (63.97%), +7.78%. **Not** the primary endpoint in PIC `03_实际结果与解释.md`. Keep only as secondary, same-unit fusion metric; do not lead the section with it. `[BOUNDARY]`

**Interpretation.** Fair claim: *under matched call budgets and frozen evidence, multi-opinion aggregation shows a small average auto-score edge over serial self-check; specialized role labels are not separately confirmed.* Unfair: *multi-agent significantly beats single-agent / raises profit.*

### §2 组织消融（CP07 终稿，8 窗 × 72 次） — `[NEW]` / fulfills spirit of sensitivity

**Design.** Pre-registered final-only battery on frozen CP07 windows (2 windows × 4 roles). v2 run: 56 interventions + 16 same-input contemporaneous identity controls = **72** calls. Dropout / order reuse original hashes; bit-flips also sync host condition registry.

**Headline.** Bid-intent flips: dropout **0/18**, order **0/12**, bit-flip **0/6** (D3) and **0/6** (S4) among comparable intent windows. Condition-ID sets **fully correct** on all valid JSON. Marker-word dropout: 6/21 lose the pre-registered role token in outward fields. Supplier quote drafts can move by millions MOP under the same prompt family — treat as replay description, not pricing law. `[BOUNDARY]` n=8 windows, one gen/variant.

**Interpretation.** Final intents are sticky to role-order/dropout; condition bookkeeping is accurate; wording and draft quotes are more plastic. Complements §1 (quality) without sharing a score scale.

### §3 招标管线十二例（single / solo / multi） — `[NEW]` parallel line

**Design.** 12 projects; four tender-stage task types; shared stage inputs; rubric v2 R1–R6 (1–5), dual-order mean; deepseek-flash gen+judge.

**Headline (project-equal).** multi−single **+0.180** on 217 pairs, 12/12 projects positive, bootstrap CI [+0.151, +0.208]. multi−solo **+0.074** on 218 pairs, 10/1/1 win/tie/loss, CI [+0.031, +0.116]. Largest dimension: risk/trade-off (+0.509 vs single, +0.252 vs solo). `[BOUNDARY]` Same-model judge; human sheets blank; some downstream shared inputs from multi upstream; **do not pool** with §1 scores. Arm analogy only: single≈S, solo≈S4, multi≈D3.

**Interpretation.** Aligns with §1/G3 narrative: multi-step self-review explains much of the lift vs one-shot; multi-role still adds on risk/trade-off, smaller than the one-shot gap.

### §4 十二例端到端微宏观衔接 — `[NEW]` layer-4 check

**Design.** 12 paired full runs (single vs multi). 11 dual-completed settlements; CASE-0315 both business-stopped in procurement.

**Headline.** Mean simulated quality multi **0.78086** vs single **0.78130** (multi higher 4 / lower 7). Settlement cost: multi lower 5 / higher 6. No consistent organization advantage. Historical firm hit: 1 comparable label row only — not a main claim. `[BOUNDARY]`

**Interpretation.** Validates wiring and archivable terminals; does **not** convert §1/§3 text gains into lifecycle profit/quality wins — same four-layer discipline as the methodology chapter.

### §5 综合写法 — `[NEW]` replaces over-claim risk

Four lines must be reported **separately**. Method contributions that remain writable: contract-like state handoff; call-budget-matched de-foamed org contrast; grounded deferral/conditions in schema+scoring; layered validation. Effect claims converge to **small, mostly consistent auto-text / risk-trade-off gains**, **unproven role-label net effect**, **sticky final intents under dropout/order**, **no stable macro quality/cost edge**.

---

## 3. Relation to offline CP07 battery in-repo — `[KEEP]` complementary

`results/experiments/org_deliberation_metrics_20261119/` (frozen D1–D4, missing_core sensitivity, 12-window LLM subset) remains valid offline evidence. It is **not** duplicated in the PIC paper zip’s main tables. If cited: same do-not-pool rule vs micro-org R1–R6 and vs §1 0–100 auto scores. Live ablation (§2) is the PIC-executed successor to the pre-registered `org_ablation_sensitivity_20261119` protocol (expanded to 72 with identity controls).

---

## 4. Suggested English bridge sentences (for interim §5.5 / §6)

> The interim’s A1–A4 protocol ablations remain future work. In their place, we report four completed organization-mechanism studies on distinct surfaces: (i) call-budget-matched S4/D3/G3 recommendation drafting on 433 units; (ii) final-only dropout/order/condition interventions on eight frozen CP07 windows; (iii) twelve-case tender-pipeline rubric scores (single/solo/multi); and (iv) twelve paired micro-to-macro lifecycle runs. Scores are not pooled across surfaces. Under matched budgets, multi-opinion drafting shows a small automatic-text advantage that is not separately attributable to specialized role labels; final bid intent is robust to role dropout/order while condition registers update correctly; tender-stage rubric gains concentrate on risk/trade-off and shrink once a multi-step solo baseline is used; paired lifecycle runs show no consistent simulated quality or cost advantage for multi-agent organization.

---

## 5. Sources for every headline number

| Claim | Source |
|---|---|
| §1 strict/sensitivity/G3/cost | `_extracted/d3s4/.../03_实际结果与解释.md` |
| §2 intent/conditions/markers/quotes | `_extracted/ablation/REPORT.md` (= paper `组织消融_REPORT.md`) |
| §3 twelve-case deltas | `_extracted/paper/采购决策质量_论文结果摘要.md` + `...十二例评分汇总_核定.md` |
| §4 e2e terminals | `_extracted/paper/端到端案例_REPORT.md` + `paired_results.csv` (recomputed means match) |

---

## 6. Change log (this revision)

- 2026-11-21: Review PIC zips; replace “planned ablation only” drop-in narrative with four completed evidence lines; freeze ablation REPORT/metrics under `accepted_20261120/`; demote Top-3 fusion to secondary; regenerate Word drop-in.
- 2026-11-21: Merged English drop-in into `final report/(final report draft) CAPSTONE.docx`: replaced §5.5 planned ablations with §5.5.1–5.5.5 completed studies + Tables 3–6; updated §6.1/§6.2; added §4.2 bridge. Backup: `final report/(final report draft) CAPSTONE.docx.bak`.
