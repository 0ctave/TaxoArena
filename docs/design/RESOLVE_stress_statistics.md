## 1. The per-cell SE the whole product spec rests on is assumed, not measured — and it is understated in 14 of 14 anchors

§2.1 computes every headline number (`0.142` Math / `0.201` median / `0.289` CS, "resolution ~0.5 logits", "5–7 ORDERED-capable anchors", "24/168 cells ≥120") from `SE ≈ sqrt(k/q)` with **k=3** — a constant the campaign wrote down for *questions per anchor* (`docs/judge_v2_program.md:359`, SPLIT-RATIO: "empirical floor sqrt(k/q), k = 3, from R2's real scheduler"; History 78 → 0.196), re-applied here to *questions per (anchor, model) cell*. The design calls the match to R2's 0.141–0.245 band a validation. It is not: `docs/v2_construction_proposals.md:115` gives the campaign's own range as `k ~ 2–4 θ²`, and k=2 → 0.116–0.237, k=4 → 0.164–0.335 — both land inside that band, so the check cannot distinguish them.

I ran the estimator the design says it will use — a 400-resample question-clustered bootstrap of the per-anchor BT fit on the same 9,144 matches (`experiment_results/x12_crossdomain/ratings_x12.db`, mapped through `eval_question_link → mmlu_pro.category`; script at `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\cellse.py`):

| | design claims | measured |
|---|---|---|
| median cell SE | 0.201 | **0.259** |
| Math | 0.142 | 0.179 |
| Computer science | 0.289 | **0.536** |
| implied k = SE²·q | 3 | **median 4.84** (p25 4.01, p75 6.80) |

Measured SE exceeds `sqrt(3/q)` in **14 of 14 anchors**, ratio 1.11–1.84, median 1.27×. k=3 is also below the ~4 floor an *independent* binomial at p≈0.5 imposes on a logit contrast, so it was never physically available. Consequences: the advertised 0.5-logit resolution is really ≥0.74 (1.96 × median contrast SE 0.378); and at k=4.84 the campaign's SE-0.15 target needs q = 215 distinct questions per cell, which **0 of 168 cells reach** (max 194) — against the design's "24 cells ≥120, 20 ≥133". The coverage table, the publication classes and the allocator's "price of the next level" column are all keyed to a threshold that is 1.6× too loose.

**Smallest fix:** delete `sqrt(k/q)` from the spec and re-derive §2.1 and §4(1) from the bootstrap above. It is zero calls and ~10 minutes on data already in the repo. Keep `q ≥ k/S²` only as the allocator's forecast, with k=4.8, not 3.

## 2. The separation certificate is calibrated to a zero-count on 66 pairs, and on the design's own reporting unit it fails at 3.7%

TIER-HONEST's evidence is 64 across-tier pairs with 0 wrong plus **2** within-tier pairs. Fitting one inflation scalar to "zero confident wrong separations" on that is one free parameter against one informative event; by the rule of three, 0/64 bounds the wrong-direction rate only at ≤4.7%.

Measured at the design's own granularity — all 924 within-anchor edges (14 anchors × 66 pairs), arena direction vs the answer key computed on each pair's *own* common question set (`...\scratchpad\edges.py`, `infl.py`):

| inflation f | ORDERED | wrong direction | wrong & key-separated | key-separated edges lost |
|---|---|---|---|---|
| 1.00 | 756 | **28 (3.7%)** | 2 | 57 |
| 1.75 | 610 | 11 | 1 | 137 |
| 3.00 | 382 | 2 | **0** | 285 |
| 3.50 | 308 | 1 | 0 | 344 |

The wrong calls are not hairline: median key-accuracy gap on them is 7.0pp, max **16.4pp**. Reaching the design's stated target costs f ≈ 3.0–3.5, which throws away 285–344 of the 640 edges the key itself separates and moves the published resolution to 1.96 × 3 × 0.378 ≈ **2.2 logits**, not 0.5. F1 inherits the same defect: 8 models × 2 corpora ≈ 56 edges, so a "both zero" pass bounds the wrong rate at 3/56 = 5.4% — which, carried to the union atlas (52 strata × C(18,2) = **7,956 edges**), licenses up to ~430 backwards published claims. The campaign already named this error class in PLACEBO-ENTRY: "a rank test on a point estimate with no resolution check — a flaw in the criterion".

**Smallest fix:** calibrate f on the 924-edge key-decidable slice, not the 66, and state the target as a *rate with an upper confidence bound* (e.g. wrong-direction ≤1%, 95% upper bound) rather than zero; publish the f chosen and the resolution it implies. Re-register F1 with a power calculation instead of a zero-count criterion.

Related and unaddressed: nothing in the design controls multiplicity. The within-anchor simultaneous 95% critical value from the same resamples is **3.21–4.51**, not 1.96 (max-t; it cuts ORDERED 756→605 and wrong 28→14). And because RESOLVE is a *standing* service refitting intervals every 500 verdicts and republishing, every edge gets unbounded repeated looks and is published the first time it crosses — optional stopping with no alpha spending. Fix: take the simultaneous critical value from the resamples you are already drawing, and put an alpha-spending rule on the streaming refits.

## 3. θ is not on a common scale across cells — measured spread 2.0× — and the atlas is a cross-cell object

The only correction the design applies is additive: `B_cell = sqrt(b_retest² + b_ref² + b_comp²)`. A scale error is multiplicative and survives it untouched. Regressing the judged θ gap on the key gap within each anchor over all 66 pairs (`...\scratchpad\atten2.py`, R² 0.72–0.95):

- on the accuracy scale, slope runs **4.76 (Philosophy) → 7.67 (Biology)**, a 1.61× spread;
- on the logit scale, **0.952 (Math) → 1.924 (History)**, a **2.02× spread**.

The same true capability difference is rendered twice as large in one anchor as in another. And it does not track reference accuracy (Math has the best reference at 0.952 and the *smallest* slope; History the worst at 0.727 and the largest), so `b_ref` cannot stand in for it. Everything the atlas exists to sell is cross-cell: a "capability profile" is the claim that a model is relatively stronger in X than Y; the tier map and TIER-ROUTER-U compare cells; §F prints θ per cell side by side. The design's own precedent is decisive against itself — PLACEBO-ENTRY measured filtering widening the θ scale by **13% (SD 1.785 vs 1.574)** and the design rules on that basis that filtered and unfiltered edges "are never mixed in one fit without an explicit scale term". The measured cross-anchor spread is **4.7× larger** than the effect that triggered that rule, and gets no scale term.

**Smallest fix:** estimate one scale parameter per cell (identified off the shared roster) and publish standardised θ/σ_cell plus σ_cell itself; or, if that is too much machinery, delete every cross-cell statement from the product and ship 14 independent within-anchor boards with no tier map.

### Two smaller ones, for the record
- **PREDICTIVE-ONLY has no power as a per-cell test.** M1's anchor gain is +0.0062 nats [+0.0041, +0.0084] pooled over 14,659 decisive verdicts (`experiment_results/m1_online_replay_output.txt`), i.e. SE 0.0011. Split over 168 cells that is ~87 verdicts each → per-cell SE ≈ 0.014, **13× the effect**; you need ~1,700 verdicts per cell. As written, the class that "makes the atlas non-empty" is assigned by coin flip.
- **The ranking instrument was chosen on the wrong unit.** Pointwise is adopted for the *anchor-level* board on a *global* ρ (0.9930 vs 0.9790, Δρ CI [−0.028,+0.035]), while POINTWISE-REPL — the one test at anchor scale — has pairwise winning **8 of 13 anchors** at 0.864 vs 0.808 per pair. Separately, feeding grade-derived pairs and pairwise verdicts into one BT fit, where the edge pass is scheduled *on the realized grade gap*, is outcome-dependent sampling that the question bootstrap does not see.

**Verdict: BUILD WITH CHANGES** — the architecture (anchor granularity, reference-as-capital, FOREIGN gate, pure-function split, the refusals) survives scrutiny, but §2.1, §4(1), §2.5 and §F must be re-derived from the measured bootstrap and the 924-edge calibration — all zero-call work on data already in the repo — before a line of it is written, because as written the resolution is 1.5–4× optimistic, the certificate misses its own target at 3.7%, and the tier map compares numbers that are not on the same scale.