# ROUTER-CLEAN-POLICY: post-run numbers review (adversarial-reviewer, zero calls)

Object: `experiment_results/multicorpus/router_clean_policy_outcome.txt` (commit 2f53675, sha256 29fbea6cfa9c9f5c..., 145 lines), produced by `tools/analysis/router_clean_policy.py` at main 44806d2, blob:2a7265299d945bac (working tree unmodified: `git status --short` on the path is empty). READY-WITH-CONDITIONS d0a2304 (`docs/reviews/READY_router_clean_policy.md`). This review discharges READY condition C4 and recomputes every number.

Method: my own code, importing nothing from `tools/analysis/` (scratch: session scratchpad `rcp_post/`: `load.py`, `analyse.py`, `dedup.py`, `extra.py`, `placebo_dist.py`, `contrib.py`). Both DBs opened `mode=ro&immutable=1`. Both `-wal` sidecars were 0 bytes before and after. The `stat` size and mtime of both DBs and both sidecars were identical before and after. `multicorpus_cache_v1.db` sha256[:16] was ad66e30a0eb4abd6 before and after. `pool_guard.py --pool paeec37aa28063c75` printed OK: 52 keys, 6,482 ids, all 6 members OK. The live processes were an idle Gradle daemon, a Kotlin compile daemon and `cert_under_filter.py --selftest`. No construction or null was running. My bootstrap seed is 20260923, not the instrument's 42, so agreement in the SEs is a genuine Monte-Carlo check.

## Per-claim table

| # | claim (outcome) | verdict | command / script | mine vs claimed | severity |
|---|---|---|---|---|---|
| 1 | Split: TRAIN 15,124, EVAL 6,482, TRAIN∩EVAL = 0, 52 strata, 18 models, Meta-Llama absent | CONFIRMED (ids) | `load.py`, `analyse.py` | 15,124 / 6,482 / 0 / 52 / 18 / absent; EVAL == pool id set; sum n² 1,279,118; mathfix changed 5,181 cells, 0 without a base cell | see D2: disjoint by id, NOT by content |
| 2 | G1 routing 0.962 / 0.813 | CONFIRMED | `analyse.py` | 0.9618 / 0.8133 (21,606); EVAL 0.9546 / 0.8112 | - |
| 3 | G2 legacy seed-42 +0.0437 on n = 1,946 | CONFIRMED | `extra.py` (my re-implementation of MC-E2E L86-L118) | +0.0437, n 1,946; the legacy train holds 4,536 EVAL ids | - |
| 4 | C0: best single Qwen2.5-72B-Instruct 0.5912, TRUE s/d 0.6220 | CONFIRMED | `analyse.py`; cost_axes_ingest.txt L211-L213 | Qwen2.5-72B-Instruct, 0.5912 / 0.6220 | - |
| 5 | Arms: 0.5912 / 0.6052 / 0.6220 / 0.6017 / 0.6203 / 0.6194 / 0.9185 / 0.5853 | CONFIRMED | `analyse.py` | identical to 4 dp | - |
| 6 | C1 point G = +2.92pp | CONFIRMED | `analyse.py` | +2.9158pp | - |
| 7 | C1 two-stage SE 0.00562, [+1.81, +4.02], HELD | CONFIRMED | `analyse.py 2000` | SE 0.00575, [+1.79, +4.04]; the gap of 0.00013 is about 1 MC SE (relative MC SE of a B=2000 SD is 1.6%, so the difference of two independent runs has SE ≈ 0.00013); HELD | - |
| 8 | C1 i.i.d. SE 0.00491; clustered 0.00729 | CONFIRMED | `analyse.py 2000` | i.i.d. 0.00491 (analytic 0.00495; within-stratum analytic 0.00491); clustered 0.00711 | - |
| 9 | C1 support: DEFF 1.312, n_eff 4,941, MDE +1.57pp (READY C4) | CONFIRMED within MC | `analyse.py 2000` | DEFF₂ 1.371, n_eff 4,728, MDE 2.80×0.00575 = 1.61pp; arithmetic of the outcome reproduces: (0.00562/0.00491)² = 1.310, 6,482/1.312 = 4,941, 2.80×0.562 = 1.57. Registered plan 1.5 / 4,321 / 1.75pp. Measured is below plan, so SCOREABLE stands (2.92 > 1.61) | - |
| 10 | C4 placebo point −0.59pp, [−1.51, +0.33], HELD | CONFIRMED | `analyse.py 2000` | −0.5862pp; SE 0.00458 (claimed 0.00470); [−1.48, +0.31]; interval straddles 0; HELD | - |
| 11 | C4 support: DEFF 2.114, n_eff 3,067, MDE 1.32pp (READY C4) | CONFIRMED within MC | `analyse.py 2000` | DEFF₂ 1.993, n_eff 3,253, MDE 1.28pp; clustered DEFF 1.32 (claimed 1.39) | - |
| 12 | Placebo is the registered permutation and keeps stratum sizes | CONFIRMED | `analyse.py` | `random.Random(42).shuffle` over the sorted-qid label list, which is position-only and so independent of the label coding; sizes kept over the 21,606: True; placebo label equals the true label on 2.78%. The EVAL-side pseudo-stratum sizes differ from the true EVAL sizes, as the registration allows ("every pseudo-stratum keeps its size" over all 21,606) | see D5 |
| 13 | C2 +1.87pp [+0.82, +2.91], DESCRIPTIVE (above 0) | CONFIRMED | `analyse.py 2000` | +1.8667pp; SE 0.00533, [+0.82, +2.91] | - |
| 14 | C3 −0.09pp [−1.09, +0.91], DESCRIPTIVE (contains 0) | CONFIRMED, with a caveat | `analyse.py 2000` | −0.0926pp; SE 0.00521, [−1.11, +0.93]; the replicate MEAN is −0.78pp (see D3) | D3 |
| 15 | R3 phi 0.3065 (MC SE 0.0139), HELD | CONFIRMED | `analyse.py 2000` | 0.3028 (MC SE 0.0110 by resampling replicates); < 0.5 | D1 (display) |
| 16 | R4 M = +0.17pp [−0.61, +0.95] | CONFIRMED | `analyse.py 2000` | +0.1697pp; SE 0.00396, [−0.61, +0.95] | - |
| 17 | R4 MMLU-Pro subset G = +0.86pp [−0.54, +2.26], n 3,609 | CONFIRMED | `analyse.py 2000` | +0.8590pp, n 3,609; [−0.55, +2.27] | - |
| 18 | ORC (TRUE s/d − best single) +3.09pp [+1.98, +4.19] | CONFIRMED | `analyse.py 2000` | +3.0855pp; [+1.99, +4.18] | - |
| 19 | P1-P7 all HELD | CONFIRMED | arithmetic on the points above | P1 2.92 ∈ [1.0, 3.6]; P2 1.87 ∈ [0.3, 2.5]; P3 −0.09 ∈ [−1.5, 0.2]; P4 −0.59 ∈ [−1.0, 0.2]; P5 0.31 ∈ [0.03, 0.40]; P6 C0 HELD; P7 0.17 ∈ [−0.3, 1.6] | - |
| 20 | Outcome = the run's own output | CONFIRMED | `diff` of run.log (minus START/WROTE/RC) against the outcome | differs only by those three wrapper lines; the selftest (and the one under -O) passed 343 checks and 54/54 branches; legacy block IDENTICAL; RC=0 | - |
| 21 | READY C2: identity line LF blob 2a7265299d945bac | CONFIRMED | outcome L4 | "LF blob sha16 2a7265299d945bac ... CRLF rendering sha16 1ea6eddbcd05860d, working tree holds CRLF" | - |

## Support, re-measured (READY condition C4; mine at B = 2000, seed 20260923; the outcome's numbers in brackets)

| contrast | point | SE_2stage | SE_iid | DEFF₂ | n_eff | MDE80 | clustered SE / DEFF_cl | class |
|---|---|---|---|---|---|---|---|---|
| C1 | +2.92pp | 0.00575 (0.00562) | 0.00491 (0.00491) | 1.37 (1.31) | 4,728 (4,941) | 1.61pp (1.57) | 0.00711 / 2.09 (0.00729 / 2.20) | SCOREABLE: 2.92 > 1.61 |
| C4 | −0.59pp | 0.00458 (0.00470) | 0.00324 (0.00323) | 1.99 (2.11) | 3,253 (3,067) | 1.28pp (1.32) | 0.00373 / 1.32 (0.00381 / 1.39) | negative control, guards a gain ≥ 1.3pp |
| C2 | +1.87pp | 0.00533 | 0.00393 | 1.84 | 3,531 | 1.49pp | 0.00866 / 4.85 | DESCRIPTIVE-ONLY as registered |
| C3 | −0.09pp | 0.00521 | 0.00307 | 2.88 | 2,254 | 1.46pp | 0.00351 / 1.31 | DESCRIPTIVE-ONLY |
| M | +0.17pp | 0.00396 | 0.00276 | 2.06 | 3,143 | 1.11pp | 0.00274 / 0.99 | DESCRIPTIVE |

A third view of the clustered leg, from the cache's own cluster sizes (`extra.py`): Kish m̄ = 1,279,118 / 6,482 = 197.3. The ANOVA ICC of C1's paired difference over the 52 strata is 0.0148, so the Kish DEFF is 1 + 196.3 × 0.0148 = 3.90 and n_eff is 1,662. The design-based clustered bootstrap gives 2.09 / 2.20. The two disagree because the heterogeneity sits in the small cells (BBH at 75, MuSR at 75-77), and the pooled-ICC formula weights it as if it were spread evenly. The registered pilot of 4.0 matched the formula, not the design. This is descriptive only, and the clustered interval [+1.49, +4.34] lies above 0 but decides nothing.

## Defects

- **D1 (LOW, display).** The R3 line prints "0.00001 / 0.00003 = 0.3065". At 5 dp the variances read as a ratio of 0.33. The actual values are 0.00311² = 9.67e-6 and 0.00562² = 3.16e-5. Fix: print the variances in scientific notation in the registrar's outcome section.
- **D2 (MEDIUM, record; no verdict moves).** The disjointness the instrument asserts is by id only. Of the EVAL questions, 471 by exact text (478 whitespace- and case-normalised; 427 distinct exact texts) have a text twin on TRAIN, and 543 TRAIN questions have an EVAL twin. By source that is GPQA 288 of 358, MMLU-Pro 185, MATH 3 and BBH 2 (`dups.py`, `dedup.py`). The 427 equals blocker A1's exact-text count, so A1's contamination is this content duplication, and it reaches the POLICY FIT as well as the tree. The twins are weak copies: the 18-model correctness vectors agree on only 74.7% of cells and are identical for only 18.6% of twins. Content-level sensitivity at B = 400 (see the table after this list): no reading brings C1's interval near 0, so the A1 worst-case bound (6.66%) is not needed for C1. Fix: carry the content-twin sensitivity beside C1 in the outcome section. Any future split assert should use the content key (norm-v1), not the id.
- **D3 (MEDIUM, interpretation).** Re-fitting the policy on a resampled TRAIN makes it worse on average, so the two-stage replicate mean sits below the point. For C1 it is +2.59pp against +2.92 (a bias of −0.33pp); for C3 it is −0.78pp against −0.09 (−0.69pp); for C2 it is +1.65 against +1.87. The deciding interval is centred on the point, as registered, and C1's percentile interval [+1.47, +3.72] also excludes 0, so no verdict moves. C3's point, however, is the leaf policy's most favourable reading; its percentile interval is [−1.87, +0.19]. Fix: print the replicate mean and bias beside each contrast in the outcome section. Do not read C3's point as parity.
- **D4 (LOW).** READY C4 said the re-measurement would come "from the outcome's replicates". The instrument does not persist replicates, so DEFF, n_eff and MDE were re-measured from my independent replicates. They agree within MC error.
- **D5 (LOW-MEDIUM, control scope).** The placebo null is not centred at 0. Over 200 permutation seeds (`placebo_dist.py`) P has mean −0.52pp, SD 0.31, range [−1.48, +0.28], and 4% of seeds come out above 0. Seed 42's −0.59 is typical. So the rule "HELD unless wholly above 0" tolerates a manufactured gain of about 0.5pp beyond its MDE. The placebo also permutes the TRUE labels and so bypasses the router: it certifies the fit-and-score pipeline, not the routing path. Router-side leakage is covered by D2's sensitivity, not by C4. Fix: state this scope in the outcome section.
- **D6 (MEDIUM, for the sentence).** The gain is concentrated (`contrib.py`). BBH contributes +1.96 of the +2.92pp (+7.35pp inside BBH, n 1,728). MuSR adds +0.46 (+13.2pp inside, n 227), MMLU-Pro +0.48 (+0.86pp inside, n 3,609, interval contains 0), IFEval +0.15, GPQA −0.08 and MATH −0.06. The sentence must not read as a gain that is broad across corpora.

| TRAIN / EVAL | C1 two-stage (B = 400) |
|---|---|
| of record | +2.92 [+1.81, +4.02] |
| EVAL minus twins (n 6,004), the A1 "exclude" form | +3.28 [+2.12, +4.44] |
| TRAIN minus twins (14,581), full EVAL | +2.68 [+1.62, +3.75] |
| both sides minus twins | +3.40 [+2.26, +4.54] |

Under both-sides removal M is +0.13 [−0.55, +0.81], C3 is −0.35 [−1.37, +0.67] and C4 is −0.62 [−1.51, +0.28].

## Verdict

All outcome claims are CONFIRMED: C0 HELD, C1 HELD, C2 and C3 DESCRIPTIVE, C4 HELD, R3 HELD, R4 as printed, P1-P7 HELD, no trigger. The points match to printed precision and every SE is within MC error. READY condition C4 is DISCHARGED (table above). Conditions C1 and C3 are moot or held: T2 did not fire, and the WAL was 0 B at the run and at this review. C2 is HELD (the identity line reads blob 2a7265299d945bac). No defect moves a verdict. D2, D3, D5 and D6 constrain the sentence of record.

## Proposed sentence of record

"ROUTER-CLEAN-POLICY (2f53675; recomputed independently in this review). On the split of record, the per-cell model policies were fitted on the 15,124 TRAIN questions outside pool paeec37aa28063c75 and scored on all 6,482 EVAL questions in the 52 fixed (source, domain) strata: 18 open-weight leaderboard models, key-scored, MATH-FIX labels. Choosing the TRAIN-best model for the (source, domain) cell PREDICTED by the federated union tree beats the single TRAIN-best model (Qwen2.5-72B-Instruct, 0.5912 → 0.6203) by +2.92pp. The two-stage 95% interval is [+1.81, +4.02]; it re-fits the policy on every replicate (measured DEFF 1.31-1.37, n_eff ≈ 4,700-4,900, MDE 1.6pp). The tree reads that cell from the nearest of 143 leaf centroids, and its depth-1/2 anchors ARE the 52 designed strata. The same policy on the TRUE labels gains +3.09pp [+1.98, +4.19], so the gain is the per-cell model choice over SUPPLIED cells. Reading the cell from the tree instead of the declared label changes accuracy by M = +0.17pp [−0.61, +0.95]. That is not distinguishable from zero at this support (MDE ≈ 1.1pp), and neither a cost nor parity is shown. About two thirds of the gain comes from BBH (+1.96 of +2.92pp), and on the MMLU-Pro source alone it is +0.86pp [−0.54, +2.26]. It survives removing the 478 EVAL questions with a TRAIN text twin (+3.28 [+2.12, +4.44]). It replaces MC-E2E's +3.38pp and +0.71pp, whose policies were fitted partly on reserved questions."

### Does not show

1. **Discovery, or that "the taxonomy earns its place".** The 52 cells are supplied as registered anchors (mc6_s42.toml L4-5; union_s42_flatleaf.toml L10-12). C1 measures filing arrivals into a given address space plus a per-cell argmax. The test of discovery is UNION-AF-ROUTE, which has not run.
2. **"Inferring the cell costs nothing."** M's interval contains 0 but reaches +0.95pp, and the MDE is about 1.1pp. A cost below about 1pp is neither excluded nor shown.
3. **"Leaves match domains" or "leaves lose".** C3 is DESCRIPTIVE with an interval that contains 0, and its replicate mean is −0.78pp (D3). MC-LEAF's −0.9 ± 0.3pp (i.i.d., [FLAG 2026-09-15]) is not reproduced as a decided result. Policies stay indexed by (source, domain).
4. **That domain-level policies beat source-level ones as a decided result.** C2 is DESCRIPTIVE-ONLY by support, even though its interval lies above 0.
5. **A gain that is broad across corpora.** BBH carries about 67% of G, and MMLU-Pro, GPQA and MATH do not individually show a gain.
6. **Generalisation to new benchmark cells.** The 52-cell clustered reading is DESCRIPTIVE-ONLY and structurally floored.
7. **Seed stability.** The split is pinned. R3 says the policy's resampling variance is about 30% of the total (phi 0.30-0.31 < 0.5); that is a different question from seed stability.
8. **A tree built clean.** The A1 content twins remain in the tree. The sensitivity above bounds their effect on C1 empirically, but it is not a clean rebuild.
9. **Any judged, preference, cost, latency or frontier claim.** Nor any claim against models outside this 18-model roster.

### Correction to the earlier restatement

FRAMEWORK L180 (the [RESTATED 2026-09-23] bracket) and `docs/agents/plans/2026-09-18_reframing_and_next.md` §1.1(a) (the L25 bracket) both carry these sentences:

- "against the corpus's own metadata the tree COSTS a mean +0.71pp (per seed −0.46 / +1.22 / +1.36) ... worse than reading the declared label on 2 of 3 seeds"
- "routing on that prediction beats best-single by a mean +3.38pp at a mean +0.71pp cost against the label"
- "the magnitude is not seed-stable"

Their evidence is MC-E2E's split. On that split 4,536 / 4,509 / 4,568 of the 6,482 EVAL ids were on the policy-fitting side, and each seed scored only 30% of the pool. Proposed bracket, by insertion:

> [CORRECTED 2026-09-23 by ROUTER-CLEAN-POLICY (2f53675; numbers review docs/reviews/2026-09-23_router_clean_policy_post.md): on the split of record the deployed gain over the best single model is +2.92pp, two-stage [+1.81, +4.02] (replacing +3.38pp), and the metadata cost is M = +0.17pp [−0.61, +0.95] (replacing +0.71pp). The tree is NOT shown to cost against the label, and it is NOT shown to match it: the difference is indistinguishable from zero at this support (MDE ≈ 1.1pp). "Worse than the label on 2 of 3 seeds" and the per-seed −0.46 / +1.22 / +1.36 are withdrawn as evidence (contaminated-fit split, 30% support per seed). "Not seed-stable" is replaced by: no seed statement is made on the pinned split; the policy-variance share is phi = 0.31 (R3 HELD). The rest of each sentence stands: the filing-not-discovery qualifier, the 81.3% / 96.2% routing rates and their A1 bound, and "what the tree adds beyond the label is the split discipline and the per-cell support, not accuracy". The leaf sentence (MC-LEAF −0.9 ± 0.3) keeps its flag; C3 re-reads it as −0.09pp [−1.09, +0.91], DESCRIPTIVE.]
