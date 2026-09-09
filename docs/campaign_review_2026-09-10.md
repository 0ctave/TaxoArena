# TaxoArena campaign review — 2026-09-10

Read-only review of the publication campaign as of 2026-09-10 01:10 (local). Sources: the
ledger (docs/test_ledger.html v21), the registration/outcome documents under docs/, the
outcome files under experiment_results/, and `git log` (741f6ad … 2034c9f). Nothing was run,
no DB was opened, and nothing without a recorded outcome is adjudicated here. Five judged runs
were in flight while this was written (STACK, J2-D, FORMAT, L1-V2, RUBRIC-512-R); their state
is reported in §5.1 exactly as their logs showed it.

Conventions: "pp" = percentage points; McNemar counts are written cell-only:generic-only
(discordant pairs); every number carries its file. Where a number is not on disk it is said
to be missing rather than reconstructed.

---

## 1. State of the evidence (one page)

### 1a. Construction and geometry

| claim | number | registered test / file |
|---|---|---|
| Structure is bit-reproducible at fixed (config, seed, code); the evaluation path is not | dag_snapshots.jsonl hash-identical across two builds; 7 files differ (JBootstrap SE 4th digit, validation float drift, timestamps) | P7 SPLIT — v2_validation_plan.md §P7; experiment_results/p7_det_{1,2} |
| Seed variance floor at the frozen config | 4 rebuilds: Top-1 spread 1.6pp (bar 2.5), anchor drift ≤0.42pp, leaves 72–87, μ-match 62–74/87; n=20: spread 2.6pp, leaves 72–92, drift ≤0.59pp | H9-1 α+β PASS — h9_arm1_outcome.txt; H9-EXT — experiment_configs/h9_sweep/REGISTRATION.md |
| The flat bar 0.025 sits below the whole honest within-node null | anchor-level p95 band 0.029 (Psychology) – 0.075 (Law); site-level certification on the frozen tree 6/66 (9%): Chemistry, Biology, Math, Engineering, Business depth-1 + one depth-4 Math site | H9b; P2 FALSIFIED ×2 — docs/separation_null_by_size.md "Where the frozen bar sits", "SITE-LEVEL (2026-09-08)" |
| Bar/mcs/beam sensitivity | bar 0.045/0.07 collapse the tree to 16–20 leaves at −2 to −4.6pp Top-1 (0.728–0.739); beam and descent-margin INERT (bit-identical); z=0 → 90 vs 87 leaves | H9-EXT — h9_sweep/REGISTRATION.md OUTCOME |
| Consensus over seed builds does not stabilise leaf identity | half-consensus ARI 0.653 vs bar 0.90 (falsifier <0.80); pairwise build ARI 0.663 (0.585–0.704) | P1 FALSIFIED — consensus_p1_report.txt |
| Overlap is real but soft routing already carries it; no structural response helps | E1 top-10 pair share 17.8% vs null 5.1%, p=0.0005; E2 D=−0.014 [−0.024,−0.004], sign p=0.043 (real bridges < placebo); P6 fusion F−T −0.728, Pf−T −0.927, sign p=0.092 (conjunctive criterion fails) | e1_overlap_concentration.txt; experiment_configs/e2_registration.md; v2_validation_plan.md §P6 |
| Certify-by-construction curve | p95 bars → 35 leaves / Top-1 0.742; p90 → 45 / 0.737; p50 → 70 / 0.755 | ADAPT — ledger row (3922070), experiment_results/h9_adaptive* |
| Second embedder | nomic: 75 leaves, Top-1 0.716 (qwen3 better by ~4pp), Philosophy splits ×4; gemma parked (Ollama fault) | EMBED — ledger row (99dce12), h9_embed_nomic |
| Slice width: 512 improves certifiable granularity, 128 loses, whitening collapses | d512 13/54 & 13/57 certified vs d256 7/60 & 9/65, Top-1 0.747/0.771, ARI 0.679; d128 5/75 & 3/76, ARI 0.580; abt2 17/27 & 18/25 but ARI 0.657 (misses clause by 0.001); white 20/17 leaves | D1 — dimsweep/report.txt; v2_validation_plan.md §D1 |
| The width effect is not a bar artefact; bareq512 is the tree to promote | bareq512 (bar 0.0145): 84/88 leaves, 11/67 & 11/71 certified, Top-1 0.747/0.771, ARI 0.688, F6 leaf loss −0.10/−0.23 (×1000, CIs include 0); abt2d512 35/34 leaves, F6 −2.68/−3.13; abt1 ARI 0.461 | D2 (i) PASS (ii) FAIL as predicted — dimsweep2/report.txt; v2_validation_plan.md §D2 |
| Certifiable structure peaks at 512 | bareq1024 (bar 0.0087; iso p95 0.0115/0.0069/0.0040/0.0024 at 128/256/512/1024): 6/66 & 6/73 certified, depth-1 4 & 3; Top-1 0.765/0.776, ARI 0.697, F6 −0.49/+0.24 | D3 TURNED — dimsweep3/report.txt; v2_validation_plan.md §D3 |
| An unseeded domain is recovered by routing, not by certification or anchor birth | Philosophy: 4 regions 77–81% pure, largest 35% of held-out, not certified (0.022 vs p95 0.038). Law: 12 regions 90–100% pure, 89% of held-out Law into Law-dominated structure, no region ≥50% (45%/44%; Other site exactly 50.0%, 0.027 vs p95 0.073), no Law site certifies | D4 both ABSORBED — dimsweep4/d4_outcome.txt; v2_validation_plan.md §D4 |
| The arena pool's routing is not inflated by being in-sample | frozen tree on its true held-out p8a29: 74.0% [72.5,75.5] vs arena pool p2dca 73.6%; train-side 72.2% vs clean 76.8%; routing deterministic on the 1,020 overlap (100%) | T3 FAIL (no inflation) — dimsweep4/t3_outcome.txt |
| Promoted trees exist on the pool of record | bareq512_s42: 87 leaves, Top-1 0.784, 87/87 rubrics (snapshot 20260909_212117); abt2d512_s42: 47 leaves, 0.760 | PROMOTED — ledger row; experiment_results/promoted/ |
| Sub-anchor cells carry capability information the 14 labels miss — but anchors do not | LOO Brier improvement ×1000: category +10.53, anchor +10.67 (tie, +0.14 [−0.53,+0.83]), stratum +11.59 (+1.06 [+0.30,+1.81]), leaf +13.68 (+3.15 [+2.07,+4.20]); uncertified leaves +2.18 [+1.01,+3.28]; the depth-4 Math site +31.45 | F2 primary FAIL / secondaries WIN; F5 PASS — docs/f_series_free_tests.md OUTCOMES |
| Key-only validation of the variants | d512 no loss (−0.45, −0.27); abt2 loses (−1.49, −1.66); nomic −1.89 | F6 — f_series_free_tests.md |
| Performance | phase 4 235.9 s → 76.0 s (−68%), build wall 360 → 125 s at 512; DAG and every routing readout bit-identical; residual diffs are P7's class. Note: perf_replay/diff.txt on disk prints `GATE: FAIL` for both arms because it predates the narrowing of the STRUCTURE list to the DAG files (perf_review_2026-09-09.md "Gate outcome") | perf_review_2026-09-09.md; perf_replay/diff.txt |

### 1b. Judge behaviour

| claim | number | registered test / file |
|---|---|---|
| Verbosity coefficient, rubric-invariant and cross-family | β_len +0.394/1k (z 14.6) cell, +0.395 generic, grok +0.339; on the clean subset +0.284 (z 6.7) | H3 — bias_audit_report.txt; clean_subset_reanalysis.txt |
| An "ignore length" clause does nothing | β +0.278 vs +0.285, Δ −0.007 CI [+0.000,+0.021] | H7 secondary — rubric_swap_outcome.txt |
| The length effect is heterogeneous: negligible where correctness separates, dominant in the top cluster | global LC-BT β +0.082 (R2), top-4-only +1.32/1k (z 26.4); gap-tier β_narrow +0.447 vs β_wide −0.036; key-status β_nondisc +0.162 vs +0.028; no global/tiered covariate fixes R2's top-4 | J4 (letter pass, non-discriminating), J4b primary PASS, J4c FAIL — judge_free_tests_output.txt |
| Order aggregation changes nothing at the board | R2 ρ 0.951 both, same violations; second-shown wins 55.1% of single-order votes; flips 19–28% at GT gaps <0.20 vs 7% above | J5 NULL — judge_free_tests_output.txt |
| The frontier divergence is a judge-capability ceiling | grok-4-1-fast-reasoning vs Mistral, top cluster key-decidable (n 266): 0.647 vs 0.526 (+12.0pp, 47:15, p=0.0001; grok non-reasoning 0.568); all pairs 0.847 vs 0.772 (96:25); ties 13.2% vs 19.9%; board 2→1 violations | J1 PASS — j1_grok_reasoning_outcome.txt |
| The judge is weaker than the contestants on the questions | solve accuracy Mistral 0.663 / grok 0.579 / grok-reasoning 0.856; Mistral below the top-4 contestants in 14/14 anchors (Math 0.522 vs 0.902) | S1 map — judge_solve/s1_outcome.txt |
| Rubric gain tracks judge COMPETENCE, not weakness | ρ(rubric gain, Mistral solve acc) = +0.516, perm p=0.032 (Philosophy +6.0 at 0.67, Biology +5.4 at 0.86; Math +1.3, Engineering 0.0) — note the gains are the contaminated x12 per-anchor gains, see §3.1 | S1 primary FAIL (opposite sign) — s1_outcome.txt |
| Length bias is elaboration-as-evidence, not bytes | truncating the correct answer's reasoning 0.766 → 0.259 (183:1); padding the wrong answer 0.769 (10:11, null); reasoning judge: truncation 0.772 → 0.471 (drop 0.301), padding 0.808 (penalised, 3:16, p=0.004) | L1 PASS / L1-R — causal_length/l1_outcome.txt, l1r_outcome.txt |
| A fallible independent reference helps, and the judge follows it both ways | Mistral's own S1 answer (66% correct): all decidable 0.806 vs 0.772 (+3.4, 66:34, p=0.0018); top cluster +6.0 (p=0.029); ref-correct +9.7 (60:3), ref-wrong −7.1 (6:31) | J2 PASS — x12_crossdomain/j2_outcome.txt |
| A reasoning reference makes the cheap judge equal to the reasoning judge | grok-reasoning reference (85.6% correct): 0.849 vs 0.772 (+7.6, 88:16); top cluster 0.665 vs 0.526 (+13.9, 45:8); ref-correct +9.4 (82:5), ref-wrong −3.9 (6:11, p=0.33); ties 15.3%, flips 12.8% | J2-R PASS as predicted — j2r_outcome.txt |
| Never gate the reference on solver agreement | agree (63%): ref 92% correct, +8.1pp; disagree (37%): ref 77% correct, +6.9pp; gating scores 0.823 < 0.849 | free — judge_v2_program.md |
| Prompt v2 (verify-first, no depth criteria) is a second-order, directionally positive lever | 0.862 vs 0.849 (+1.4, 26:13, p=0.053); ref-correct +2.2 (25:7, p=0.002); ref-wrong −3.9 (1:6); long-wrong preference 0.241 vs 0.259; decidable tie rate 5.9% under both | J3-R letter FAIL, guards OK — j3r_outcome.txt |
| The reference dents but does not disarm elaboration | with reference: original 0.772, truncate 0.350, pad 0.783; drop 0.421 (142:0) vs L1's 0.507; registered ≤0.25 / ≥0.55 missed | L1-V FAIL — causal_length/l1v_outcome.txt |
| Position sensitivity is not reduced by the reference | flips 12.8% (J2-R) vs 9.7% (v1, J1 record) | free — judge_v2_program.md |
| Confidence is informative and calibrated; the bias lives at mid-confidence | AUC 0.752 [0.738,0.764], ECE 0.039; top-4 β_len by band <0.85 +1.02, 0.85–0.95 +2.61, ≥0.95 +0.68; ≥0.95-gated top-4 = gemini > iask > arx > gpt-4o (1 violation) | F3 PASS; F7 letter FAIL (by 0.011), substance — f_series_free_tests.md |
| No per-model rubric favouritism; no key leakage; order bias bounded | H1 0/12 CIs exclude 0 (max +0.138); H2 0 hits over 87 rubrics; H4 5.0% flagged vs 3.0% chance (R2) | bias_audit_report.txt |
| Cell rubrics: the honest value for a non-reasoning judge on keyed questions | contaminated: +1.5pp p=0.0001 (Mistral), +2.4 p=0.021 (grok) — WITHDRAWN. Clean subset: +0.9 (52:41, p=0.30), grok +2.3 (14:8, p=0.29). RUBRIC-P8 (frozen tree's true held-out pool, same session): 0.823 vs 0.823, 20:20, p=1.0. RUBRIC-512 (clean bareq512_s42 leaf rubric vs cached generic): +1.8 (42:25, p=0.0498); discursive +3.7 (34:15, p=0.009), quantitative −0.5. RUBRIC-512-SS (same-session generic): +1.0 (35:26, p=0.31); drift alone +0.8 (27:19); discursive +2.5 (26:13, p=0.053); Philosophy +23.3 (7:0, n=30) | rubric_contrast_outcome.md; clean_subset_reanalysis.txt; rubric_p8/outcome.txt; rubric_512/outcome.txt; rubric_512/generic_ss_outcome.txt |
| Rubric specificity ladder is not monotone; the knee is at or before anchor | generic 0.761 < anchor 0.774 > stratum 0.757 < leaf 0.770 (n 967); leaf vs anchor 35:38, p=0.68; on the clean 280: leaf −1.4, stratum −1.8, generic −1.1 vs anchor, all p>0.35 | LADDER primary FAIL — rubric_ladder_outcome.txt; clean_subset_reanalysis.txt |
| Wrong-cell rubric harm is not shown on clean data | H7 cell vs random-anchor: was +2.1pp p=0.006 (39:19); clean +0.7 (11:9, p=0.82); cell vs sibling clean 0.0 (5:5) | H7 primary WITHDRAWN — rubric_swap_outcome.txt; clean_subset_reanalysis.txt |

### 1c. Arena and matchmaking

| claim | number | registered test / file |
|---|---|---|
| The model×domain interaction is real and the judge recovers it | X8-DEEP registered per-pair null, post-hoc pooled LRT p=0.003; X8-CONF LRT 18.60 p=0.003 (arx +0.451, Llama-2-7b −0.548); X12 LRT 39.48 p=0.001, ρ=0.951 τ=0.848 vs key, 5/5 clauses; R2 LRT 60.24 p=0.001 (36,871 verdicts, 2/4 direction signs) | ledger rows X8-DEEP/X8-CONF/X12/R2 (6433111, 6861ea8, 17de9b7/5fae41f, 2aba5ee/e17162c) |
| It survives question clustering and the pool incident | R2-QP p=0.002 (null p95 −16.3→+24.8); clean 1,020 questions: LRT 38.83 vs null p95 21.01, p=0.002; ρ 0.951 with the identical top-4 in every subset | atlas_question_perm.py (a8bfcb8); clean_subset_reanalysis.txt |
| The board is not judge-family specific | grok non-reasoning re-judge: 97.8% decisive agreement, board ρ=0.993, one adjacent swap | R3 — ledger row (fb8fb5b) |
| Board is invariant to cell weighting; support is the binding budget | H6 ρ 1.0000 under 4 weightings; H6b design effect median 2.0×, worst 3.7×; rule q ≥ k/S² (~120–190 questions per stratum for SE 0.15) | bias_audit_report.txt; ledger H6b (ee56c74) |
| Match budget: ~1–2k matches for a 12-model board; beyond that spend on the judge | ρ ≥0.93 in 100% of draws at 2,000 for every Mistral run; Mistral plateau ρ 0.951 from ~1,000 (gemini first in 0% of draws); reasoning judge on R3: 0.965 at 500, 0.974 at 1,980 (gemini first 86% / 100%); confidence weighting 0.958 | M2 PASS — m2_match_budget_output.txt |
| Online profile: anchor level carries the signal; leaf level hurts; routing value on this roster is small | hier(κ=30) vs global log-loss −0.0078 [−0.0102,−0.0055] (FAIL); anchor +0.0062 [+0.0041,+0.0084]; cell −0.0251; router utility hier 0.851 vs global 0.844 (130:73, p=0.0001); cell-ORACLE 0.870 → ceiling +2.6 points, achievable +0.7 | M1 — m1_online_replay_output.txt |
| Placement cost is flat in roster size; noise, not roster, sets the bill | oracle @400: median rank error 0/0/1/1 at 16/24/32/46, within ±1 98→61%; noisy @400 ρ 0.947→0.975 (more models help under noise); noisy needs >4× the oracle's matches (clause iii FAIL); joint round-robin 0.994/0.971 ≈ sequential 0.989/0.975 | M3 (i)(ii) PASS (iii) FAIL — m3_synthetic_arena_output.txt |

### 1d. Infrastructure and hygiene

| item | fact | file |
|---|---|---|
| Reserved-pool incident | frozen tree withheld p8a29 (3,437); every judged run used p2dca (3,445); overlap 1,020 (29.6%); 2,437/3,445 (71%) of the arena pool on the tree's train side and inside rubric induction. Cause: process-global split file + no save-time check + concurrent 2026-07-27 runs | incident_reserved_pool_mismatch_2026-09-09.md |
| Audit scope | 132 snapshot rows, 65 checkable: 63 OK, 2 MISMATCH — both the frozen snapshot 20260727_042523; every seed-42 build since 2026-09-08 produced p8a29 | m_series_registration.md AUDIT; snapshot_pool_audit.txt |
| Guards | save-time FATAL pool check; `reservedPoolFile` (pool of record exported as experiment_configs/reserved_pool_frozen_p2dca.json); pool_guard.py --activate + assertion in every is_reserved analysis; [POOL-PIN] in the runner, benchmark pinned, manifest records the pool id; rule: never two constructions in one repo root | incident doc §Guards; ledger POOL-PIN (368b6b5) |
| Harness defects disclosed | D4 first run VOID (withheld queries never entered the DAG; guard checked the label map, d69c429/dbfde01); D4 lowercase keys aborted at the membership check, nothing built (01912f5); site-null Gradle test-results collision in the overlapped chain (serialised, d25fc35); session confound old-vs-fresh arms (ladder, RUBRIC-512 → SS control); eval_results.question_text pollution from one excluded model (F2 first run VOID; options-key join rule); J1 DNS outage (308 matches, resumed from cache, 0 errors); DeepSeek-R1 attempt died at 402 after 3 matches | v2_validation_plan.md §D4; f_series_free_tests.md DATA NOTE; judge_improvement_proposals.md J1 |
| Determinism debt | JBootstrap SE column not order-stable; trickle/routing validation float accumulation; the perf gate's STRUCTURE list narrowed to the DAG files | P7; perf_review §Gate outcome |
| Earlier hygiene (not re-verified here) | position-bias correction bug fixed 2026-09-05 with PairStatsLedger/PairStatsInvariantTest; tests that wrote to production DBs fixed 2026-07-26 | memory notes only; outside the documents read for this review |

---

## 2. Falsified or withdrawn, and the honest replacement claim

1. **"Cell rubrics beat a generic judge (+1.5pp, p=0.0001; grok +2.4, p=0.02)."** WITHDRAWN — 71% of the judged questions were inside the rubric-induction corpora (incident doc). Replacement: *a cell rubric induced without the judged question is worth about +1pp to a non-reasoning judge on keyed questions and is not distinguishable from zero at n≈950* — three clean tests: RUBRIC-P8 0.0pp (20:20, p=1.0), RUBRIC-512 +1.8 (p=0.0498, session-confounded), RUBRIC-512-SS +1.0 (p=0.31). The discursive concentration (Philosophy +16.7 / +23.3 on n=30) is a repeatable pattern in two of three tests and a hypothesis, not a claim (rubric_p8/outcome.txt, rubric_512/outcome.txt, generic_ss_outcome.txt).
2. **"Cell rubric beats a random-anchor rubric (p=0.006); wrong specificity harms."** WITHDRAWN — clean +0.7pp, 11:9, p=0.82; sibling 0.0 (5:5). Replacement: no clean evidence that a wrong rubric harms; the placebo objection to rubric specificity is *open*, not closed (clean_subset_reanalysis.txt).
3. **"The finer the rubric, the better."** FALSIFIED — ladder not monotone, leaf vs anchor p=0.68; on clean questions anchor is numerically best. Replacement: *anchor-level induced rubrics are as good as anything finer*; P3 (functional twig gate) has no premise and is dropped (rubric_ladder_outcome.txt).
4. **"Rubric gain tracks judge weakness."** FALSIFIED with the opposite sign, ρ=+0.516, p=0.032. Replacement: *a rubric is a checklist for competence the judge already has* — but see §3.1: the gains in that correlation are the contaminated ones (s1_outcome.txt).
5. **"The width gain continues / saturates at 1024" (D3 prediction SATURATED, ±2).** TURNED on certification (6/66, 6/73 vs 11/11; prediction off by −5), while Top-1 (0.765/0.776), ARI (0.697) and F6 do not turn. Replacement: *certifiable structure peaks at 512; routing and capability information are flat-to-better beyond it* (dimsweep3/report.txt).
6. **"Law ARRIVES as a certified split."** ABSORBED. Replacement: *routing recovers an unseeded domain (89% of held-out Law lands in 90–100%-Law regions), but the construction never births an anchor and no Law site clears its within-node null* (d4_outcome.txt).
7. **"In-sample routing inflates the arena pool's purity by ≥3pp" (T3 prediction 68–70%).** FAIL — −0.5pp; train-side questions route *worse* (72.2% vs 76.8%). Replacement: H5's 73.6% stands as an honest held-out figure (t3_outcome.txt).
8. **Structural responses to overlap.** P1 consensus FALSIFIED (ARI 0.653); P2 trunk FALSIFIED (6/66; deflated null cannot separate CS from Philosophy at 300 reps, both q≈0.05); E2 bridges underperform placebo; P6 fusion hurts. Replacement: *soft routing carries the overlap; the polyhierarchy and consensus programs are closed negative results* (v2_validation_plan.md OUTCOMES; e2_registration.md).
9. **abt2 "improves"** — misses the ARI clause by 0.001 (D1); abt2d512 certifies 11/11 but loses 2.7–3.1/1000 of capability information (D2, F6). Replacement: *dropping top PCs trades profile resolution and stability for certifiability; it is a ladder instrument, not a profile tree*.
10. **Free refits of the board (J5, J4, J4b, J4c).** J5 NULL (a flip contributes ½ under either rule); J4 letter pass but non-discriminating; J4b primary PASS but R2 top-4 unchanged; J4c FAIL. Replacement: *no global or tiered length covariate corrects R2's top cluster; the corrections that work are a within-cluster fit (a per-tier board, not a correction), the ≥0.95 confidence gate, or a stronger judge/reference* (judge_free_tests_output.txt).
11. **"A judge that can solve the question resists truncation (drop <15 points)."** Wrong on magnitude: reasoning judge drop 0.301 (l1r_outcome.txt). Replacement: *even a solving judge leans on shown reasoning, half as much*.
12. **"The reference disarms the elaboration heuristic" (L1-V: drop ≤0.25, truncate ≥0.55).** FAIL — drop 0.421, truncate 0.350. Replacement: *J2-R's +7.6pp comes from pairs where the length heuristic points the wrong way; the heuristic itself survives the reference* (l1v_outcome.txt).
13. **Prompt v2 as a registered improvement (J3-R).** Letter FAIL, p=0.053 (+1.4pp, 26:13); guards OK. Replacement: *directionally positive, +2.2pp where the reference is right (p=0.002), −3.9 where it is wrong; second-order next to the reference; STACK runs v1 by registration* (j3r_outcome.txt).
14. **"Hierarchical (leaf-shrunk) profile beats the global board online" (M1).** FAIL at κ=30 (−0.0078); κ=200 post-hoc is a tie. Replacement: *the anchor-level profile beats global (+0.0062); leaf-level priors inject noise* (m1_online_replay_output.txt).
15. **"A noisy judge costs ≤3× the matches" (M3 iii).** FAIL — >4× at roster 46 (m3_synthetic_arena_output.txt).
16. **"Embedding anchors beat MMLU-Pro categories on capability prediction" (F2 primary).** FAIL — tie (+0.14 [−0.53,+0.83]). Replacement: *strata (+1.06) and leaves (+3.15/1000) beat the labels; anchors do not* (f_series_free_tests.md).
17. **F1/F4 (certified-vs-uncertified rubric gain)** — UNDERPOWERED (2:0, 3:1 discordant), not null. **F7** letter fail by 0.011 with the substantive non-monotone finding.
18. **X8-DEEP registered per-pair Q/df test** — NULL; the interaction claim rests on the *pooled LRT*, registered from X8-CONF onward (ledger).
19. **"The frontier top-cluster anomaly is sampling"** → judge-level (R2); **"…is a shared verbosity/style preference"** → a capability ceiling (J1) whose observable signature is elaboration-as-evidence (L1). The thesis' Chapter-5 sentence should be the J1/L1 version.

Nothing in the settled r8 batch (docs/RESULTS.md: RQ1 verification + competence prior, RQ2 same ranking / different decisiveness, Link 3 premise refused) is contradicted by the campaign; the campaign's honest rubric claim now *agrees* with RESULTS.md's "same ranking, different decisiveness".

---

## 3. Contradictions and tensions

### 3.1 S1's "gain tracks competence" rests on contaminated gains, and the clean tests disagree with each other
S1's registered primary correlates Mistral's per-anchor solve accuracy with the per-anchor cell-over-generic gain from `rubric_value_contrast` — the x12 contrast that the incident then withdrew (s_l_series_registration.md §S1; incident doc lists S1 as unaffected, which is true of the *solve map*, not of the gain vector). The two clean measurements then split on the anchor pattern: RUBRIC-P8 finds discursive −0.5 / quantitative +0.8 (secondary FAIL; Psychology −5.6, Chemistry/Health +4.2), RUBRIC-512 and 512-SS find discursive +3.7 / +2.5 vs quantitative −0.5 / −0.9 (secondary PASS, Philosophy +16.7 / +23.3 on n=30). The P8 sample is uniform over decidable pairs (verdict rate 0.82), the 512 sample is the R3 top-cluster-oversampled schedule (0.77); the rubrics also differ (frozen tree's vs the promoted tree's). The competence reading is therefore *consistent with* two of three clean tests but not established by a clean registered test. Honest wording: "where a rubric gain appears, it appears in discursive anchors where the judge can already solve the question".

### 3.2 The reference helps (+7.6) but does not change how the judge reads
J2-R equals the reasoning judge on accuracy; L1-V shows the truncate arm still loses 65% of verdicts with the reference in hand, position flips rise (9.7% → 12.8%), and J3-R's verify-first mechanics add only +1.4. So "verify-then-judge" is the right *cost* design but the mechanism claim ("the judge verifies rather than counts steps") is only partly supported: the reference re-anchors the *answer*, not the *reading*. L1-V2 and STACK check (6) are the tests that decide whether the mechanics can be fixed by prompt; if not, the elaboration heuristic is structural for this judge tier and should be reported as such.

### 3.3 Certification is rare everywhere, yet routing and capability information are intact
6/66 on the frozen tree (P2), 11/67–71 on bareq512 (D2), 6/66–73 at 1024 (D3), 10–11/72–84 in D4 — while F5 finds capability structure in *uncertified* leaves (+2.18/1000), F2 finds leaves beat the labels, D4 finds Law routed 89% into near-pure regions, and D3 finds the *highest* ARI and Top-1 on the tree with the *fewest* certified sites. Three different notions of "real structure" are in play: geometric (site null), capability-relevant (key-only Brier), rubric-relevant (paired McNemar). They do not coincide, and the ladder says rubric-relevant structure ends at the anchor. The promotion of bareq512 over bareq1024 uses certification as the tie-breaker; a reader who weights routing/ARI would promote 1024. State the criterion explicitly.

### 3.4 Law arrives as content, not as structure — and the test is the wrong instrument
Twelve 90–100%-Law regions do not certify because the within-node null is run on a population that is itself 94–97% Law, i.e. it measures Law-internal structure; the Law-vs-host boundary at the anchor site (0.052 vs p95 0.072) is the relevant test and it also fails. The certification criterion cannot see an arrival that splits itself across two hosts (Philosophy 94% Law, Other 72%). "Evolving tree" is true at the routing/cell level and false at the anchor level for a mechanistic reason (the root is never a split candidate), not an empirical one.

### 3.5 Arena vs router narratives pull apart
M2: the Mistral board saturates at ~1,000 matches and 36,871 verdicts do not move it; 500 reasoning-judge matches beat it. M1: a perfect cell-level router gains +2.6 points over "always pick the best model" on this roster, +0.7 achievable. The arena is *judge-limited*; the router is *roster-limited*. The "reference-free router for agents" motivation therefore needs a heterogeneous roster to have any measurable value, which none of the campaign data contain.

### 3.6 The board-level J1 secondary is not unique to reasoning
Non-reasoning grok also produced gemini > iask > arx > gpt-4o on the R3 sample (1 violation); the *accuracy* gain (+8pp over grok, +12 over Mistral) is unique. Cite J1 for accuracy, not for the board order.

### 3.7 Verbosity "bias" is judge-tier dependent
Mistral is indifferent to padding (L1), the reasoning judge penalises it (L1-R, p=0.004), and the observational β is cross-family (H3). The cross-family observational coefficient and the causal tier-dependence are both true; the paper should not call β_len a "verbosity bias" without the L1 qualification.

### 3.8 Interaction confirmed vs Link 3 refused
RESULTS.md refuses "evaluative sub-structure" between *leaf cells* (0/293 pairs survive); X8/X12/R2 confirm model×domain interaction at the *group* level (math / law+psych / other). Both stand; the thesis must say granularity matters: interaction at domain-group level, none resolvable at leaf level with this budget (H6b: q ≥ k/S²).

### 3.9 The tree that certifies everything profiles worst
abt2d512 (11/11 certified) loses 2.7–3.1/1000 of capability information; whitening (the limit of that trade) leaves a stump. "Certifiable" and "useful for profiles" are anti-correlated along the PC-dropping axis.

---

## 4. Recommended direction

### 4.1 Judge (system design)
Adopt, pending STACK: **cheap non-reasoning judge + one reasoning-model reference per question ("[Reference — may be wrong]") + anchor-level induced rubric + dual order + confidence field.** Evidence: J2-R (+7.6 / +13.9), J2 (value scales with reference accuracy; ref-wrong penalty −7.1 at 66% → −3.9 at 85.6%), ladder + RUBRIC-P8/512/SS (anchor rubric ≈ leaf ≈ +1pp), F3/F7 (confidence calibrated; ≥0.95 gate removes the divergence), free test (never gate the reference on agreement). Cost: one reasoning call per question amortised over ~6.5 judge calls, plus two cheap calls per match (judge_v2_program.md). Keep v1 mechanics until L1-V2/STACK say otherwise; report the confidence-gated board as the corrected board; report β_len per tier alongside.

### 4.2 Tree
Promote **bareq512_s42** (512-dim slice, bar 0.0145, splitSeed 42 / reservedPoolFile p2dca; 87 leaves; Top-1 0.784; 87/87 rubrics). Report certification as a *geometric-reality diagnostic* (6–11 sites per tree), the honest null band, and the ADAPT curve; use F2/F5-style key-only Brier as the *profile* criterion and the paired McNemar as the *rubric* criterion, and say which one each claim uses (§3.3). Keep 1024 as the disclosed "routing-equal, certification-worse" arm.

### 4.3 What "evolving tree" and "router" can honestly be
- Evolving tree: *anchors and routing are seed-invariant (drift ≤0.59pp over 20 seeds) while leaf identity is a sample draw (ARI ~0.66–0.69); an unseeded domain is recovered as near-pure cells and its held-out questions route into them (Law 89%); the loop cannot birth an anchor* (D4). Not: "certified arrival", not "stable leaves".
- Router: *an anchor-level profile predicts the next verdict better than the global board (+0.006 log-loss) and picks the key-correct model slightly more often (0.851 vs 0.844); ~400 matches place a newcomer at any roster size; 1–2k matches give a 12-model board; the ceiling for cell-level routing on a homogeneous LLM roster is +2.6 points.* Not: "reference-free router for agents" as a result — that stays a motivation with a measured ceiling.

### 4.4 Headline results, ranked
1. **The judge recovers a real model×domain interaction and the key ranking** — X8-CONF p=0.003, X12 LRT 39.48 p=0.001 with ρ=0.951/τ=0.848, R2 LRT 60.24 p=0.001; survives question clustering (p=0.002) and the clean subset (p=0.002); board robust across judge families (R3 ρ=0.993) and cell weightings (H6).
2. **Judge accuracy is a capability ceiling whose signature is elaboration-as-evidence** — J1 +12pp top cluster (p=0.0001), S1 Mistral below the top-4 in 14/14 anchors, L1 0.766 → 0.259 on truncation with padding null, L1-R halves the drop and penalises padding.
3. **Verify-then-judge: a reasoning reference makes a cheap judge equal to a reasoning judge** — J2-R 0.849 vs J1 0.847 (all pairs), 0.665 vs 0.647 (top cluster); J2 shows the dependence on reference accuracy; the free test shows gating must not be used.
4. **Slice width sets certifiable granularity, peaking at 512** — D1 (13 vs 7–9), D2 bar-equalised 11/11 with ARI 0.688 and no key-only loss, D3 turned at 1024; T3 confirms routing figures are honest; D4 bounds what "evolving" means.
5. **Sub-anchor cells carry capability information the labels miss, even though rubric value ends at the anchor** — F2 leaf +3.15/1000 vs categories, F5 uncertified +2.18, the depth-4 Math site +31; ladder p=0.68; three clean rubric tests ≈ +1pp.
6. **Measurement economics** — M2 (2k matches; budget buys stability, the judge buys accuracy), M3 (~400 matches/newcomer, noise >4×, more models help under noise), H6b (DEFF 2.0×; q ≥ k/S²), F3/F7 (confidence as a legitimate weight/gate).
7. (Methodological) **Honest nulls and the pool-hygiene incident** — the within-node band, site-level certification, the incident with its clean-subset re-analysis and guards. This is a contribution about how to run such a campaign; keep it in the paper.

### 4.5 Drop or demote
- The contaminated rubric p=0.0001 and H7 random-anchor p=0.006 — never cite; the +1pp n.s. statement replaces them.
- "Finer is better", P3, the certified-twig gate — one sentence each.
- DAG/bridges/fusion/consensus — one negative-result paragraph with E1/E2/P6/P1 numbers.
- J5/J4/J4b/J4c — appendix; the informative line is "no global covariate corrects the top cluster".
- "Rubric gain tracks judge weakness" (rubric_contrast_outcome.md exploratory) — replace with the §3.1 wording.
- X16 — deprioritised (ledger); H10 as designed — superseded by a clean run on the promoted tree (§5.3).
- Underpowered F1/F4 — a footnote pointing to the abt2d512 ladder if it is ever run.

---

## 5. Future experiments (ranked)

### 5.1 First: land the five running tests (0 new calls; analysis only)
State at 01:10 on 2026-09-10 (logs only; not adjudicated):
- **STACK** — 400/1977 jobs ok, 1 skip, 0 err (x12_crossdomain/stack_v2.log; cache written 01:10). Registered: (1) all-decidable ≥ 0.849−1pp; (2) top cluster ≥ 0.665−2pp; (3) top-4 board ≤1 violation; (4) decidable tie rate ≤15%; (5) flips ≤12.8%; (6) long-wrong preference < v1's (judge_v2_program.md). *Pass all six* → the production judge changes with the B1–B8 before/after table. *Fail (1)/(2)* → the anchor rubric or same-session drift cost accuracy; re-run the leaf-rubric arm on the same matches before concluding. *Fail (3)* → report the confidence-gated board and the reasoning-judge board; the cheap-judge design cannot resolve the 1.7pp iask/arx gap. *Fail (6)* → expected without v2; wait for L1-V2.
- **RUBRIC-512-R** — 2500/3956 jobs, 0 err (rubric_512/grok_reasoning.log). Registered: cell > generic, p<0.05; secondary gain > +1.8pp; prediction +0 to +2 n.s. *Significant* → rubric value is judge-tier dependent and the headline revives for reasoning judges; then run the same-session leaf re-judge on the promoted tree (~4k calls) and J6. *Null* → B4 closes for both tiers: "cell rubrics are not the lever"; drop J6 and the abt2d512 ladder.
- **J2-D** — 450/650 jobs, 0 err (j2d_two_refs.log). Registered: disagree-stratum accuracy vs J2-R's 0.774, either direction. Prediction NULL. *Positive* → two-reference design for the disagree stratum only (37% of questions, +1 reasoning call). *Null/negative* → single reference; branch closed.
- **L1-V2** — the queue log shows `L1-V2 exit=-1` at 00:59:17 and its cache (mistral_refgrok_v2.db, 110 KB) has not been written since; the queue restarted "waiting for the FORMAT step" (judge_v2_queue.log). Treat as running per the author but **verify the relaunch** before waiting on it. Registered: truncate arm > 0.350 (p<0.05); original ≥ 0.752; pad within ±0.03. *≥0.55* → v2 enters STACK as a second arm (~4k calls). *0.45–0.55* → prompt moves but does not cure; report. *<0.45* → the elaboration heuristic is structural for this tier; the fix is the judge tier, not the prompt.
- **FORMAT** — only the prevalence file exists (rejudge_mistral_format_stripped.db, 16 KB, 23:52); 383 eligible pairs, formatted side correct in 70%. Registered: a format bias exists iff correct-verdict rate changes >3pp, p<0.05; prediction no effect. *Effect* → add B5 to the bias table and a strip-formatting arm to STACK. *Null* → close B5 with the L1 pad result.

### 5.2 Clean arena run on the promoted tree — is it needed?
**Question.** Do the board, the interaction and the per-stratum profiles hold on questions the tree and its rubrics never saw, with the assembled judge?
**What is already clean.** The 12-model ρ (0.951, identical in every subset), the interaction (p=0.002 on 1,020 clean questions), the verbosity β, the anchor knee, and every rubric-value number since RUBRIC-P8. What is *not* clean: the R2 atlas's per-stratum precision (22–38% clean questions per stratum) and every per-cell profile number (clean_subset_reanalysis.txt).
**Verdict.** Not needed for the board or the interaction claims. **Needed iff the paper publishes per-stratum/per-cell capability profiles or the STACK judge's board at scale.** If so, run it once, in profile mode, on bareq512_s42 with the STACK configuration, strata rebuilt under P5's floor (both halves ≥240 reserved), targeting query-level SE ≤0.15 per stratum (H6b: q ≥ k/S²). Budget from M2/H6b rather than R2: ~20 strata × ~150 questions × ~3 matches ≈ 9k matches ≈ 18k Mistral calls + ~3.4k reasoning reference calls (one per reserved question in the sample), i.e. x12-scale, not R2-scale. Registered readouts: ρ vs key ≥0.95 with gemini first (M2 says the reasoning-reference board should), interaction LRT p<0.01 under question-level permutation, every stratum SE ≤0.15 at ≤1.25× budget (P5 rider). This run also replaces H10 (the promoted tree *is* the counterfactual tree) and gives P5 its data. Dependencies: STACK pass; P5 strata file; pool re-pinned (pool_guard.py) before launch.

### 5.3 Anchor birth: a root-level split proposal (D4 follow-up)
**Question.** Can the construction promote a foreign-dominated region to a depth-1 anchor without labels?
**Design.** Engine change: allow the root as a split candidate for any depth-2+ region R under host anchor A whose separation from A's remainder exceeds A's own depth-1 separation from the root (label-free criterion), then certify R against the *root-level* honest null (population = root corpus), not A's within-node null. Rerun the D4 Law and Philosophy arms (seed 137, bareq512 recipe) and re-adjudicate with D4's registered ARRIVES clause (a certified ≥60%-excluded-domain split that ≥50% of held-out routes to). Add a placebo: the same rule on a tree with no exclusion must birth no anchor (or the rule over-splits).
**Cost.** Local compute only: ~2–5 min per build at 512 with the perf fixes, 15–20 min per site-null; ~2 h total with the placebo.
**Decision.** Law births a certified anchor → "evolving tree" extends to anchor-level structure. Law does not (the anchor-site test failed at 0.052 vs 0.072 in D4) → state that anchor birth needs a looser criterion than the honest null and keep the routing-level claim. Depends on: a registered amendment to the D4 plan; the P7 STRUCTURE gate to prove the change is a no-op without `excludeFromAnchoring`.

### 5.4 Cross-iteration proposal memo (perf review item #8)
**Question.** Are iterations 6–10 (the J-stationarity streak; 486 identical proposals re-evaluated each) removable bit-identically? **Design.** Stop clearing `rejectedProposalsCache` on re-route (keep clearing on accepted edits); replay two finished configs (bareq512_s137 and one seed-42 build) and diff with replay_diff.py's STRUCTURE list; proposals.csv rows will change (MEMOIZED vs NO_PROPOSAL) — accept only if the DAG is identical. **Cost.** Two builds (~5 min) + review; saving ≈37% of phase 4 at 1024, ≈100 s at 512. **Decision.** Identical → adopt; enables #5.3 and larger seed sweeps. Differs → the memo's false-hit incident recurs; leave the streak as is. **Dependency.** The perf gate; note the P7 bootstrap-SE non-determinism must be excluded from the diff list (it already is).

### 5.5 Agent-trace adaptation (first datum for the "for agents" motivation)
**Question.** Does verify-then-judge with a *verifier* as the reference transfer to agent traces, and does the anchor rubric add anything there?
**Design.** A task set with executable ground truth (unit-tested code tasks or tool-use tasks with checkable end states; ~1,000 tasks). Embed task descriptions with the same embedder, build a bareq512-recipe tree with `reservedPoolFile`, route a held-out third. Contestants: 6–8 agents/models producing traces. Judge arms, paired on the same trace pairs, key-decidable by the verifier: generic; anchor rubric; generic + verifier outcome as "[Reference — may be wrong]" (a verifier is a reference with known accuracy, the J2 covariate); plus the L1 truncation control (agent traces vary in length far more than answers).
**Cost.** Embedding ~1k tasks; ~1,000 matches × 2 orders × 3 arms ≈ 6k cheap judge calls; verifier runs (compute, not LLM).
**Decision.** Verifier-reference gain of J2-R size (≥+5pp decidable) → the design transfers and the "for agents" motivation has a measurement. Anchor-rubric gain >+1pp p<0.05 → rubrics matter more on process-heavy tasks than on keyed questions (the thesis' original bet). Both null → the system is a keyed-question instrument; say so. **Dependency.** A trace-complete roster (RESULTS.md standing caveat) and a dataset licence; nothing from the running tests.

### 5.6 Harder datasets (the ceiling moves)
**Question.** How does the verify-then-judge design behave when the reference generator's accuracy falls toward the contestants'? On MMLU-Pro the reasoning reference is 85.6% correct and the best contestant 0.913; J2's strata arithmetic (+9.7×acc − 7.1×(1−acc)) predicts the net gain goes to zero near acc ≈ 0.42 with a 66%-class penalty, or ≈ 0.29 with the −3.9 penalty.
**Design.** A 500-question stratified sample of a harder keyed set (GPQA-Diamond-class or a hard math set), 12-model roster subset with traces, S1 solve map for the three judge tiers (1.5k calls), then J1 and J2-R on ~1,000 stratified matches (~2k reasoning + ~4k Mistral calls). Registered: per-stratum J2-R gain vs reference accuracy follows the J2 arithmetic within ±3pp; key-decidable fraction reported.
**Decision.** Reference accuracy <70% and net gain <+3 → the design needs a reference-confidence gate *on hard sets* (the free test forbade it at 85.6%; it may be required lower) and the paper's cost claim gets a domain condition. Gain holds → the design generalises. **Dependency.** Contestant traces for the new set; the S1 harness.

### 5.7 Same-session leaf re-judge on the promoted tree (P3's replacement)
Only if RUBRIC-512-R is positive. ~4k Mistral calls on R3's matches: promoted-tree leaf vs anchor rubric, same session. Decision: leaf > anchor p<0.05 → the knee moves below anchor on the clean tree; else the ladder result is final. Otherwise skip.

### 5.8 Certified-leaf ladder on abt2d512_s42 (F1/F4 power fix)
~4k calls; registered as F1 with an instrument that certifies every leaf. Decision: leaf-over-anchor gain on certified leaves >0 p<0.05 → certification predicts rubric value; else certification is geometric only. Given +1pp overall rubric value the expected effect is small; run only behind 5.7.

### 5.9 Blind insertion of two new models (ledger "LADDER" queued row; renamed LADDER-INSERT here)
~2–6k calls. M3 predicts ~400 matches for ±1 rank at 12 models; register the point prediction and the ±1 hit. This is the one *real-judge* confirmation of the placement-cost claim and a good demo for the router narrative. Medium priority; run with the STACK judge.

### 5.10 Not planned by the author, suggested by the results
- **Solvability-weighted board (0 calls).** The S1 caches give a per-question "judge can solve it" covariate for every past verdict; refit BT weighting or gating on it and compare with the F7 confidence gate. If the two gates agree on gemini-first, the paper has a key-free correction with a mechanism.
- **Reference-agreement as a key-free weight (0 calls).** Mistral/reasoning-solver agreement predicts reference correctness (92% vs 77%); use agreement as a per-verdict weight in BT (not as a gate) and report the board.
- **Where do the extra flips come from (0 calls)?** Flips rose 9.7% → 12.8% under the reference; test whether they concentrate on ref-wrong questions (J2-R cache). If yes, position sensitivity is reference-following in disguise (B3), not B2.
- **Non-discriminative-pair audit and κ (J9; 0 calls).** 8,264 both-correct R2 pairs: the verdict rate there is the bias signature; report Cohen's κ vs the key instead of raw agreement for every judge condition.
- **Per-cell profiles are unattainable at this budget — say so.** H6b's q ≥ k/S² gives ~120–190 questions per stratum for SE 0.15; the promoted tree's 87 leaves cannot each be profiled; profile at strata/anchor level and make that a stated design rule (it is also what M1 found online).
- **P5 strata rebuild on the promoted tree (0 calls)** — the R2 strata are frozen-tree strata; rebuild before 5.2.
- **Determinism CI (P7 work items).** Sort the JBootstrap capture iteration and make the trickle accumulation deterministic so the perf/structure gate can be strict; local work.
- **Label-free replica of the promoted build (local, ~3 min).** Verify that bareq512_s42 with labeling off reproduces the labeled build's DAG hash — labeling should not touch structure; a cheap guard against a silent coupling.
- **Session-drift as a first-class covariate.** Two of the campaign's boundary results (+1.8 → +1.0; ladder) moved by the size of the same-session drift (+0.8pp, 27:19). Every future paired judge test should re-judge both arms in one session by default (the RUBRIC-512-R design already does).

---

## Appendix — evidence index used
docs/test_ledger.html (v21) · docs/v2_validation_plan.md · docs/judge_improvement_proposals.md · docs/judge_v2_program.md · docs/incident_reserved_pool_mismatch_2026-09-09.md · docs/f_series_free_tests.md · docs/s_l_series_registration.md · docs/m_series_registration.md · docs/perf_review_2026-09-09.md · docs/separation_null_by_size.md · docs/RESULTS.md · experiment_configs/e2_registration.md · experiment_configs/h9_sweep/REGISTRATION.md · experiment_results/{bias_audit_report, clean_subset_reanalysis, contamination_recheck, consensus_p1_report, e1_overlap_concentration, h9_arm1_outcome, judge_free_tests_output, m1_online_replay_output, m2_match_budget_output, m3_synthetic_arena_output, judge_v2_queue.log}.txt · experiment_results/x12_crossdomain/{rubric_contrast_outcome.md, rubric_swap_outcome, rubric_ladder_outcome, j1_grok_reasoning_outcome, j2_outcome, j2r_outcome, j3r_outcome, stack_v2.log, j2d_two_refs.log} · experiment_results/causal_length/{l1,l1r,l1v}_outcome.txt · experiment_results/judge_solve/s1_outcome.txt · experiment_results/rubric_p8/outcome.txt · experiment_results/rubric_512/{outcome, generic_ss_outcome}.txt, grok_reasoning.log · experiment_results/dimsweep{,2,3}/report.txt · experiment_results/dimsweep4/{d4,t3}_outcome.txt · experiment_results/perf_replay/diff.txt · git log 741f6ad…2034c9f.
