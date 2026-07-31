# Evidence-to-text audit — 2026-07-30

> **CURRENT for method and for the `file:line` ledger. Its per-domain arena numbers are
> superseded (2026-07-31).** Every Δρ, absolute ρ and key-agreement figure in this file
> comes from the M = 12 batch, which is no longer the results: its bootstrap starved every
> cell but one in every domain and three of its runs had unequal arms. Five domains were
> re-run and those are the results — `docs/newlogic-rerun-record.md`. Where this file
> names a database per row, that provenance is why it ages well; read the row as "correct
> for a superseded batch". The per-domain replacements and every remaining `file:line`
> site are in `docs/stale-results-audit.md`.
>
> **CURRENT, and the authoritative evidence ledger — with five corrections applied later
> the same day (2026-07-30).** Everything not listed here stands, including the whole
> B-list, the R-table re-runs, and the A7 withdrawn-figures list.
>
> 1. **Six paired runs -> eight.** Physics (+0.0140 / +0.0140, screen p 0.004, registered,
>    met both conventions; GT-agreement 83.8/79.8) is absent from the file entirely, and
>    computer science is RUNNING. Every "six domains" rewrite in B-4 through B-9 needs the
>    eight-run inventory.
> 2. **The A4.1 screen table is the superseded generation.** In force, at the 12-model
>    roster: psychology 0.000, physics 0.004, history 0.009, law 0.011, philosophy 0.053,
>    math 0.289, computer science 0.751, engineering 0.817. Every downstream count inherits
>    the change.
> 3. **The "screen matches the sign of `Delta rho` in 6 of 6" claim is withdrawn.** It is
>    the file's most-promoted finding (B-12 / B-13, "the biggest gain on the list") and it
>    does not hold. The screen predicts the **domain aggregate**; its correlation with
>    within-domain between-leaf agreement is **+0.072**. Philosophy met both conventions and
>    was not flagged. **B-12 and B-13 must not be implemented as written.**
> 4. **B-13 attributes math's negative to mathematics** ("the screen predicted no per-leaf
>    advantage and there was none"). Not licensed. Math is the only paired run predating the
>    scheduler fixes — 20 of 66 pair coverage against 66/66 elsewhere, predating `5e1be09`
>    and `a5c36fd` — and the re-run is registered and pending. The file notes the coverage
>    at A1 but draws no confound from it.
> 5. **A4.3 / B-16 are wrong that "no permutation null was run."** It ran, with
>    overlap-matched pseudo-leaves, and nothing survives correction (economics p = 1.000,
>    health p = 1.000, law p = 0.957). B-16 would insert a **withdrawn** result into
>    Chapter 1. Do not implement it. Relatedly, the §A8 retraction in the implementation log
>    should be reversed: A8 stands as originally written (law leaf-vs-domain rho 0.895-0.993
>    against GT-vs-GT 0.873-0.970), and its reading — a precision gain on a shared ranking,
>    not discovered specialisation — is the thesis's central bound. **B-15 should have been
>    implemented as written.**
>
> Two smaller ones: the file treats 7.66 as a legitimate roster label rather than as wrong
> (it is 3.04x too large; see `measurement-discipline.md`), and it leaves the
> redundancy-inversion conflict open at A5.5 / B-20d. That conflict is moot: 72.2% / 42.2%
> is irreproducible and withdrawn (`void-results.md` §3). And A6.4 correctly identifies the
> routing-ECE state but never names the defect — it is `maxOf` instead of sum at both export
> sites (`known-defects.md`).

Status: **audit only**. No `.tex` was edited, nothing was committed. This file is the sole output.

Scope: every measured result the project holds, its verdict on the thesis's claims, and a
per-file line-cited action list against `report/`.

**Concurrency caveat.** `1_Introduction.tex`, `2_Literature.tex`, `3_System_Architecture.tex` and
`6_Results.tex` were being edited by another agent while this audit ran; Chapter 6 moved by ~176
lines. All Chapter 6 line references were re-verified against the file at the end of the audit and
are accurate to within two lines. Items already corrected during that session are not reported here.
References into Chapters 1–3 were taken mid-session and may have drifted by a few lines; the
quoted text is exact and will locate them.

## What was re-run for this audit (not merely read)

| # | command | purpose | outcome |
|---|---|---|---|
| R1 | ad-hoc BT + Spearman over all six `ratings_*_paired.db` (`.final` where present) | recompute Δρ = MAIN − C5 under both tie policies, and per-arm key agreement | **all twelve Δρ values and all twelve GT-agreement values reproduce exactly** |
| R2 | `tools/analysis/tie_policy_sweep.py` | tie-convention sensitivity, correctness-blind subset | reproduces; see §A3.6, §A7.2 |
| R3 | `tools/analysis/discriminative_flatness.py` | granularity flatness at both rosters | **8-model 87-leaf ρ = 0.884, not 0.922**; 11-band = 0.948 / 0.908, **not 0.973 / 0.936** |
| R4 | `tools/analysis/domain_reorder_screen.py` | the offline reordering screen | reproduces `6_Results` law/Math rows exactly; **flags 8 domains, not 4** |
| R5 | `tools/analysis/reliability_constant.py` | refit of `c` in `r = n/(n+c)` | c(8) = 7.71, c(11) = 5.05, ratio 0.65× |
| R6 | ad-hoc Mann–Whitney over `build/rubric_null/measures*.json` | rubric-specificity p-values | **1.210e-6 / 2.092e-6 / 7.618e-6 — all three reproduce to the digits printed in Ch.6** |
| R7 | ad-hoc capture-gap reconstruction against `mmlu_pro_dataset_cache_v2.db.bak-before-trace-backfill` | Run A trace availability at run time | **4 of 8 models with no text; mixed 896/1736 = 51.6%; judge takes the texted side 863/868 = 99.42%** |
| R8 | ad-hoc within-domain vs between-domain leaf divergence, both rosters | the "cells diverge inside a domain" claim | reproduces on the **12-model arena roster** only; see §A4.3 |
| R9 | ad-hoc pair-coverage / near-clone counts across all runs | scheduler coverage, P2 | reproduces `6_Results` exactly |
| R10 | ad-hoc SE audit of `node_bt_states` and the five secured `*_leaf_leaderboard.csv` | is the "every pre-correction SE was the floor" claim true? | **No — Run A stores 45 of 176 (25.6%) at the floor, median 0.09** |
| R11 | ad-hoc `\label`/`\ref` closure over `report/**/*.tex` | dangling cross-references | 140 labels, 395 refs, **0 dangling** |
| R12 | ad-hoc arm-pairing check on all six paired DBs | is the "identical question set" void condition met? | question sets identical in 6/6; **comparison sets differ in philosophy (10%) and engineering (17%)** |
| R13 | ad-hoc near-clone rank/BT-separation check over the five secured leaf leaderboards | the two **unreported** near-clone predictions (P2-a rank adjacency, P2-c within 2 SE) | **P2-a met 10/10 arms; P2-c met 7/10** — see §A1.16 |
| R14 | ad-hoc trace-format probe of `arx_3` / `arx_0314` in the current corpus | did the side-channel survive into the paired runs? | **no** — median newlines 23 and 22 (against the "median 0" that flagged them), 0 of 400 reserved rows carry a leading confidence code. The repair held |

Convention throughout: **Δρ = MAIN − C5, positive favours per-leaf.** Grid step at M = 12 is
0.0035; the pre-registered decisive threshold is |Δρ| ≥ 0.007.

---

# PART A — THE EVIDENCE LEDGER

Verdict column: **S** supports · **Q** qualifies · **C** contradicts.

## A1. The six paired arena runs — the thesis's primary evidence

All six ran against snapshot `20260727_042523_Headless_Run_Auto_ge`, seed 42, testRatio 0.3,
the same 12-model roster (manifests at `experiment_results/arena_*_paired/seed_42/manifest.json`).

| # | measured | value | source | V | bears on | in the `.tex`? |
|---|---|---|---|---|---|---|
| A1.1 | law Δρ | +0.0000 half / **+0.0210** drop (MAIN 0.9510/0.9650, C5 0.9510/0.9441) | `ratings_law_paired.db.final` (R1) | S | RQ2, P1-law | yes, `6_Results.tex:592` and `:529-533` |
| A1.2 | philosophy Δρ | **+0.0490** / **+0.0420** (0.8601/0.8601 vs 0.8112/0.8182) | `ratings_philosophy_paired.db.final` (R1) | S | RQ2 | yes, `6_Results.tex:593` |
| A1.3 | history Δρ | **+0.0105** / **+0.0105** (0.7951 vs 0.7846, both policies) | `ratings_history_paired.db.final` (R1) | S | RQ2 | yes, `6_Results.tex:594` |
| A1.4 | psychology Δρ | **+0.0210** / **+0.0210** (0.8881 vs 0.8671) | `ratings_psychology_paired.db.final` (R1) | S | RQ2, registered (Addendum 2) | yes, `6_Results.tex:595` |
| A1.5 | engineering Δρ | +0.0035 / **−0.0035** (0.8983/0.8912 vs 0.8947/0.8947) — one grid step, sign flips | `ratings_engineering_paired.db.final` (R1) | S (as a *null*) | RQ2, registered null #2 | yes, `6_Results.tex:597`, `:609-618` |
| A1.6 | Math Δρ | **−0.0637** / **−0.0070** (0.8873/0.9161 vs 0.9510/0.9231) | `ratings_math_paired.db` (R1) | **C** | RQ2, registered null #1 — **failed prediction** | yes, `6_Results.tex:598`, `:484-503` |
| A1.7 | key agreement, MAIN vs C5, per domain | math 94.18/94.65 · law 87.99/86.15 · philosophy 92.93/94.22 · history 83.28/79.43 · psychology 85.25/84.30 · engineering 89.02/88.52 | R1, joined to `eval_results.is_correct` | S/Q | RQ1, RQ2 high-power statistic | yes, `6_Results.tex:592-598` right-hand columns |
| A1.8 | **philosophy dissociates**: largest +Δρ, but key agreement leans to C5 by 1.3 pts | ρ +0.049 vs agreement −1.3 pts | R1 | **Q** | RQ2 — Δρ and key agreement are not the same construct | yes, `6_Results.tex:620-630` |
| A1.9 | tie rates per arm | math 22.0/26.6 · law 19.8/17.8 · phil 22.3/21.1 · hist 17.6/16.5 · psych 17.6/18.0 · eng **23.5/31.4** | R1 | Q | tie-convention sensitivity (D5) | partly — eng at `6_Results.tex:609-618`, law at `:525-529`; the other four arms' tie rates are not stated |
| A1.10 | comparison counts per arm | math 2640/2638 · law 2499/2479 · phil **1319/1188** · hist 1448/1448 · psych 3300/3288 · eng **792/660** | R1, manifests | **Q** | "four void conditions" — identical question sets | **NO.** `6_Results.tex:96-105` gives only the 660–3300 range |
| A1.11 | arm pairing granularity | held-out **question** sets identical in 6/6 (overlap 1.000); **(question, model-pair)** sets overlap 99.9 math / 99.2 law / **89.9 philosophy** / 99.9 history / 99.6 psychology / **83.3 engineering** | R12 | **Q** | the pairing claim at `5_Experimental_Design.tex:311-315` | **NO — nowhere** |
| A1.12 | scheduler pair coverage | law/phil/hist/psych/eng: **66 of 66 pairs, all ≥ 2**. Math (Run B): **20 of 66, 46 pairs never compared**, top model in 55.0% of comparisons. Run A: 28/28 at 8 models | R9 | S (post-law) / **C** (Run B) | RQ2 estimator identifiability | partly — `6_Results.tex:88-93` states it for law and Run B; **not stated that the other four also carry the floor** |
| A1.13 | top-model share of comparisons | law 51.0 · phil 50.2 · **hist 67.9** · psych 43.2 (`iask_pro`) · **eng 61.4** · math 55.0 | R9 | Q | scheduler-bias caveat (`6_Results.tex:29-32`) | **NO** |
| A1.14 | near-clone P2 (`claude-3.5-sonnet` vs `claude-3-5-sonnet-20241022`) | law 11/24 tied = 45.8% vs 19.8% arm avg · psychology 7/18 = 38.9% and 8/18 = 44.4% vs 17.6/18.0 · **history MAIN 4/35 = 11.4% vs its own 17.6%** (C5 13/35 = 37.1%) · philosophy 2 direct · **engineering 2 direct** | R9 | **Q** — mixed | P2 | yes for four domains, `6_Results.tex:632-652`; **engineering's 2-comparison unevaluability is not stated** |
| A1.15 | BT standard errors in the five secured runs | median 0.31–0.48, min 0.149, **0 of 288 at the 0.01 floor** | `*_secured/*_leaf_leaderboard.csv` (R10) | **S** | the corrections register's "Runs B and C ran with measured standard errors" | **NO — the positive evidence is nowhere** |
| A1.16 | near-clone predictions **1 and 3**, never reported | P1 "adjacent or ≤ 1 intervening": **met in 10 of 10 arms** (max 1 intervening). P3 "BT difference within 2 SE of zero": **met in 7 of 10**; fails law MAIN (2.38 SE), psychology MAIN (2.76 SE), philosophy C5 (2.22 SE). *Indicative — computed as mean-of-leaf-BT with a naive combined SE, not the pooled MM fit the thesis uses* | R13 over the five secured leaf leaderboards; predictions registered at `docs/arena-math-findings.md:703-706` | **S** for P1, **Q** for P3 | P2 (the near-clone check) — currently only its tie-rate leg is reported | **NO — two of the three registered predictions are unreported** |
| A1.17 | the `arx` side-channel did not reach the paired runs | `arx_3` median newlines **23**, `arx_0314` **22** in the current corpus (the flag was "median 0 where every other model showed 8–24"); **0 of 400** sampled reserved rows carry a leading confidence code | R14 | **S** | `7_Discussion.tex:109-114` "Neither system entered any arena run as stored" | the claim is in the `.tex`; **the verification is not** |

## A2. Run A — the 8-model pilot and its capture-gap defect

| # | measured | value | source | V | bears on | in the `.tex`? |
|---|---|---|---|---|---|---|
| A2.1 | models with no stored response text at run time | **4 of 8** (`Llama-2-13b-hf`, `Llama-2-70b-hf`, `Meta-Llama-3_1-70B-Instruct`, `Qwen1.5-72B-Chat`) — text rate 0.0000 in `…bak-before-trace-backfill`, 0.99+ in the current corpus | R7 | **C** | RQ1 pilot | yes, `6_Results.tex:253-256` |
| A2.2 | mixed (text × no-text) comparisons | **896 of 1736 = 51.6%** (868 decisive) | R7 | **C** | RQ1 | yes as "868/1736 = 50%", `6_Results.tex:283` |
| A2.3 | judge picks the side that has text | **863/868 = 99.42%** (MAIN) | R7 | **C** | RQ1 | yes, `6_Results.tex:274-283` |
| A2.4 | Run A key agreement on the discriminable stratum | **1030/1160 decisive → 88.82%** MAIN, 88.38% GENERIC | R7/strata | S (as measured) / Q (support is format-purchased) | RQ1 headline 88.8% | yes, `6_Results.tex:119-124` |
| A2.5 | tie rate by correctness stratum, MAIN | exactly-one-correct **11.29%** · both-correct **37.98%** · neither-correct **33.11%** (GENERIC: 10.95 / 32.56 / 34.90) | R7 | **S** | RQ1 "the tie rate triples where the key stops discriminating" | yes, `6_Results.tex:140-142` |
| A2.6 | Run A stored BT standard errors | n = 176, median 0.0907 (MAIN) / 0.1003 (GENERIC), **45 at the 0.01 floor = 25.6%**, max 0.3155. Fit timestamps 2026-07-27 05:15–05:21Z; fix `a92a3ed` committed 2026-07-27 15:27Z → **pre-fix, confirmed** | `ratings.db.node_bt_states` (R10) + `git log a92a3ed` | **C** — of the thesis's own wording | the "every pre-correction SE was the floor constant" claim | **stated as an absolute in three places and the artifact refutes the absolute** (see B-1) |
| A2.7 | Run A scheduler consequence | 28 of 28 pairs covered at 8 models; allocation still near-uniform-entropy because `U_resolve`'s variance divisor was constant | R9 + A2.6 | Q | Run A readings must not lean on adaptive allocation | yes, `7_Discussion.tex:256-269` |

## A3. The judge — what actually decides a verdict

| # | measured | value | source | V | bears on | in the `.tex`? |
|---|---|---|---|---|---|---|
| A3.1 | rubric-free (GENERIC) vs rubric-scoped (MAIN) winner agreement | **10 winner flips**; 1301/1311 = **99.24%** on comparisons decisive in *both* arms; 1726/1736 = **99.42%** if tie/decisive mismatches are counted as agreement | R7 | **C** (of link 3's mechanism) | RQ2, link 2→3 | yes as 99.4%, `6_Results.tex:346-350`; the **denominator convention is not named** |
| A3.2 | overall verdict identity MAIN vs GENERIC | 1529/1736 = 88.08%; 207 disagreements, 197 of them a TIE on one side | R7 | S | same | yes, `6_Results.tex:346-350` |
| A3.3 | rubric specificity vs a size-matched randomised null | Mann–Whitney U one-sided **p = 1.210e-6** (`measures_all`), **2.092e-6** (`measures_hash`), **7.618e-6** (`measures_induction`); medians 0.1384 vs 0.0123 | R6 over `build/rubric_null/measures*.json` | **S** | link 2 / R1 | yes, `6_Results.tex:906-914` — **and every digit reproduces** |
| A3.4 | the four pre-registered discriminators | own-cell specificity 0.1384 vs 0.0123 · pairwise Jaccard 0.0754 vs 0.1187 · terms in ≥90% of rubrics **0 vs 6** · cells with positive specificity **81/87 (93%) vs 7/13** | `measures_all.json` (R6) | **S** | link 2 | yes, `6_Results.tex:929-932` — all four reproduce |
| A3.5 | rubric-null artifacts version status | `build/rubric_null/` is **untracked** (`build/` is in `.gitignore:7`); `git ls-files build/` returns nothing | R6 + `git ls-files` | **Q** | reproducibility of link 2 | yes, `6_Results.tex:967-980`, `5_Experimental_Design.tex:390-392` |
| A3.6 | tie-convention sensitivity of ρ | Run A MAIN 0.9762 → 1.0000 (+0.0238); Run B MAIN 0.8873 → 0.9161 (+0.0287); Run B C5 0.9510 → 0.9231 (**−0.0280**) — direction not consistent | R2 | **Q** | rule D5; the Math verdict | yes, `6_Results.tex:395-399`, `4_Methodology.tex:345-350` |
| A3.7 | judge is answer-key-blind but not answer-blind | 94.8% of stored traces state the model's own selected option; the options block is shown | `4_Methodology.tex:88-90` provenance; corpus | **C** (of the blinding claim's reach) | RQ1 | yes, `4_Methodology.tex:88-90`, `6_Results.tex:154-157` |

## A4. Ground truth, screens, and structure

| # | measured | value | source | V | bears on | in the `.tex`? |
|---|---|---|---|---|---|---|
| A4.1 | the offline reordering screen, fixed 11-model band, 1500-draw null, seed 42 | biology .342 · business .730 · chemistry .213 · comp-sci .535 · **economics .003** · engineering .706 · **health .001** · **history .003** · **law .008** · math **1.000** · **other .041** · **philosophy .046** · **physics .017** · **psychology .000** | R4 | **S** | RQ2 domain selection | **partially** — only law (.008) and Math (1.000) are printed, `6_Results.tex:1096-1102` |
| A4.2 | screen-vs-arena concordance | the screen's classification matches the sign of Δρ in **6 of 6 run domains**; the screen flags **8 of 14** domains, of which **4 were run**; it clears 6, of which **2 were run** | R4 + R1 | **S**, with a scope caveat | RQ2 — "the screen predicts in both directions" | yes at `6_Results.tex:654-676`; the **8-of-14 flag count is not stated**, and "the four domains the screen flags" (`1_Introduction.tex:513`) is wrong as written |
| A4.3 | within-domain leaf divergence vs between-domain | **12-model arena roster**: within-domain leaf pairs n = 293, median ρ **0.9066**, IQR [0.8521, 0.9454]; between-domain n = 91, median **0.9422**, IQR [0.9169, 0.9632]. Worst single leaf pair per domain: biology 0.5882, physics 0.7000, math 0.7106, psychology 0.7123. **11-model band gives 0.9314 vs 0.9476** — the ordering survives, the gap halves | R8 | **S**, weakly; **no permutation null was run** | the motivation for sub-domain cells | **NO — nowhere in the thesis** |
| A4.4 | per-model per-domain ground truth | 12 models × 14 domains × {acc, acc_parsed}, reserved and full splits | `model_domain_scores.csv`, generator `tools/analysis/export_gt_scores.py` | S | RQ1/RQ2 denominator | **the file is not cited anywhere in the `.tex`** |
| A4.5 | blank `pred` counted as incorrect | Qwen1.5-72B-Chat 18.78% blank (acc 0.4743 → acc_parsed 0.5840, **+11.0 pts**), Qwen1.5-14B-Chat 17.56% (+7.6), Meta-Llama-3-8B 11.61% (+4.3), Meta-Llama-3-8B-Instruct 8.27% (+3.7); all others < 1%. **Ranking identical 12/12 under both views** | `model_domain_scores.csv` | **Q**, harmless to rank results | every ρ-against-ground-truth number | **NO — nowhere** |
| A4.6 | the 3 "equal on average, opposite at the margin" pairs, of 66 | deepseek-chat-v2_5 / gpt-4o-mini: agg gap +2.4, engineering **+12.4**, health **−9.2**, swing **21.6** · Meta-Llama-3-8B / Qwen1.5-14B-Chat: agg −2.6, philosophy +9.0, business −10.8, swing **19.8** · arx_3 / iask_pro: agg −2.7, history +6.6, math −9.1, swing **15.7**. Thresholds (|Δagg| ≤ 3, reversal ≥ 5) are post hoc | R-ad-hoc over `model_domain_scores.csv` | **S** | the motivating problem, §1.2 | yes, `1_Introduction.tex:162-172` — reproduces exactly, and the post-hoc thresholds are already declared |
| A4.7 | frozen construction artifact | 154 nodes / 87 leaves / maxDepth 6 / J 0.253129 / mass 8299.00 / 87 of 87 rubric-carrying | `docs/frozen-artifact.md`, `experiment_results/freeze_mcs55/seed_42/` | S | R1–R4, link 1 | yes, `6_Results.tex:727-734` |
| A4.8 | fixed-point certificate | certified at **iteration 10**; iterations 8/9/10 identical; edits delta 0; max 1−cos(µ) 1.11e-16; max rel dκ 4.25e-13 vs τ = 1e-6 | `fixed_point_certificate.txt`; convergence rule in `TaxonomyStabilizer.kt` (`requiredConsecutive = 5`, ll. ~24–25 and the streak logic at ~95–120) | S | R3, link 1 | yes, `6_Results.tex:736-741` |
| A4.9 | two certificate fields are not reproducible | trickle delta 1.11e-16 / 3.33e-16 / 2.22e-16; max rel dκ 3.50e-13 / 3.85e-13 / 5.55e-13 across three runs of the same commit | `docs/known-defects.md:9-25`, commit `7d33345` | **Q** | R3 | yes, `6_Results.tex:819-827` |
| A4.10 | certificate tests period 1 only | a 2e-6 alternation reads `CERTIFIED: false` forever | `docs/known-defects.md:36-41` | **Q** | R3 | yes, `3_System_Architecture.tex:138-151` |
| A4.11 | acceptance-gate coherence argument | SE(ΔJ) spans **13.1×** p10→p90; the uncalibrated rule accepted **4 of 52** edits at z < 1, worst z = 0.156 (ΔJ 9.4e-6 vs SE 6.0e-5) | `docs/frozen-artifact.md:89-100` | S | R4 | yes, `6_Results.tex:829-835` |
| A4.12 | both empirical corroborations of the z-gate were refuted | additive offset ≈ 4.4 leaves; corr(reduction, seed deviation) = +0.006; variance ratio 1.05 vs F(4,4) crit 6.39; J higher on 2 of 5 seeds, sign test p = 0.812, median ΔJ = −0.0001 | `docs/frozen-artifact.md:104-117` | S (as a declared negative) | R4 | yes, `6_Results.tex:865-882` |
| A4.13 | the birth floor is not an invariant | 1 of 87 leaves below `minClusterSize = 55` (54 queries); two further instances at other settings | `docs/frozen-artifact.md:149-155` | Q | R2 | yes, `3_System_Architecture.tex:129-136`, `6_Results.tex:750-754` |
| A4.14 | separation bar positioning | isotropic null p95 spans 0.0055–0.0093 over n = 75…900; bar 0.025 is conservative by 2.7–4.5× | `docs/separation_null_by_size.md` via `frozen-artifact.md:129-135` | S | R1 | yes, `6_Results.tex:779-786` |
| A4.15 | the within-node null half of that argument is void | measured on the pre-`c381211` 88-leaf tree | `docs/void-results.md:24` | **Q** | R1 | yes, marked `void as to values`, `6_Results.tex:783-787` |
| A4.16 | polyhierarchy retired | 42 cross-link proposals; r(f, ΔJ) = +0.085; median f 0.802 accepted vs 0.818 rejected; median ΔJ 6.9e-5 cross-link vs 5.3e-4 split; multi-leaf rate 0.1549 vs 0.1518 | `6_Results.tex:1146-1164` provenance | S | the tree-vs-DAG decision | yes, `6_Results.tex:1146-1174` |

## A5. The granularity / discriminative-power result — the load-bearing null

| # | measured | value | source | V | bears on | in the `.tex`? |
|---|---|---|---|---|---|---|
| A5.1 | between-cell Spearman, **8-model roster, c = 7.66** | 14 domains **0.929**, IQR [0.857, 0.970] · **87 leaves 0.884**, IQR [0.806, 0.934] · granularity delta **+0.045** · IQRs overlap | R3 | S for flatness, **C for the printed 0.922** | link 3 premise; `minClusterSize = 55` licensing | `6_Results.tex:1009-1011` prints **0.922** at 87 leaves; footnote `:1016-1023` already records 0.884 as the re-routed reserved-only reading |
| A5.2 | between-cell Spearman, **11-model band, c = 2.52** | 14 domains **0.948** IQR [0.927, 0.964] · 87 leaves **0.908** IQR [0.860, 0.942] · delta +0.040 · IQRs overlap | R3 | **C** | the "re-derived at the corrected band it holds" sentence | `6_Results.tex:1041-1044` prints **0.973 and 0.936** — **these two numbers appear in no script, no doc, and do not reproduce** (`docs/reconciled-argument.md:1173`, `docs/peer-review-2026-07-28.md:352,459`) |
| A5.3 | disattenuated column clips past 1.0 | 8-model 87 leaves: 1.056 at c = 7.66; 11-band 87 leaves: 1.081 at c = 7.66, 0.966 at c = 2.52 | R3 | **Q** | why observed-ρ was pre-registered as primary | yes, `6_Results.tex:982-990`, `5_Experimental_Design.tex:345-351` |
| A5.4 | centred residuals | R3 gives 8-model **+0.024 / −0.024**; 11-band **−0.109 / −0.009**. The printed quartet **−0.119 / −0.024 / −0.024 / −0.024** reproduces under **no single centring convention** | R3 vs `6_Results.tex:1026-1035`, `docs/prereg_discriminative_power.md:76-79` | **C** | the "indistinguishable from the centring null" statement | printed at `6_Results.tex:1026-1035` — **the quartet is not currently reproducible** |
| A5.5 | reliability constant refit | fitted **c = 7.71** at the 8-model roster (published 7.66, SSE 2.4e-4) and **c = 5.05** at the 11-band, ratio **0.65×**; after the post-fit Spearman–Brown correction (×0.50) the 11-band value is **2.52** | R5 | S for the correction, **Q** for the argument it supported | disattenuation, the coarse-cut argument | yes, `5_Experimental_Design.tex:426-433`, `7_Discussion.tex:271-281` |
| A5.6 | the join under the granularity analysis | exact and complete, **11769/11769** | `6_Results.tex:1037-1039` provenance; `docs/known-defects.md:86-87` | S | rule D2 | yes, `6_Results.tex:1037-1039` |
| A5.7 | power bound on the null | per-model per-cell accuracy SE ≈ 2.1 pts at 14 domains, 5.8 at 87 leaves, 6.9 at 152 | `6_Results.tex:1046-1053` provenance | **Q** | link 3 — the null cannot separate "no signal" from "signal < 6 pts" | yes, `6_Results.tex:1046-1053` |
| A5.8 | roster-spread bound | pilot roster spans **54.1** accuracy points | `6_Results.tex:1054-1058` | **Q** | link 3 | yes |
| A5.9 | **the input to the redundancy-inversion arithmetic is contested** | `arena-math-findings.md:934` computes the whole c = 7.66 → 2.52 redundancy inversion from "at a **40.8**-query cell, observed median ρ = **0.823**". `prereg_discriminative_power.md:78` gives the 87-leaf observed median as **0.922** at **74** queries/cell. At ρ = 0.922 and c = 2.52 the disattenuated value is ~0.978 — **above** the 0.90 redundancy threshold, i.e. the inversion does not occur | the two docs; neither reconciles them | **Q — the corrections-register claim rests on the unreconciled value** | the "compresses from 0.219 to 0.088" claim | quoted at `7_Appendix_TuningProtocol.tex:404-408` and `7_Discussion.tex:271-281` **without the conflict** |
| A5.10 | the disattenuation form was corrected but stale numbers remain in the source doc | `arena-math-findings.md:928-932` corrects `ρ/√r` → `ρ/r`; `:386` and `:875-876` still use `√r` | that doc | **Q** | the disattenuation statement | the `.tex` states the corrected two-sided form (`5_Experimental_Design.tex:421-425`) — **the `.tex` is right, the doc is stale** |

## A6. Corrections, defects, and instrument limits

| # | item | state | source | V | in the `.tex`? |
|---|---|---|---|---|---|
| A6.1 | BT variance correction | `1/K` subtracted where `1/K²` is required; over-subtraction (K−1)/K² = 0.109 at K = 8; corrected values 44–209× larger; fix `a92a3ed`, 2026-07-27 15:27Z | `12_Appendix_Numerics.tex:145-157`; `git log`; R10 | **C** for pre-fix intervals | yes, three places |
| A6.2 | scheduler collapse in Run A | `U_resolve` variance divisor constant → pure entropy; α never matured; 3σ resolve rule → fixed \|Δŝ\| ≥ 0.06 | `7_Discussion.tex:256-269` | **C** | yes |
| A6.3 | BT intervals not recomputed | no pre-correction interval is quoted anywhere; the correction is registered rather than applied retroactively | `7_Discussion.tex:249-254` | Q | yes |
| A6.4 | `computeRoutingECE` | returned 0.0 with an "empty ground truth" warning in **every run in project history** per `docs/known-defects.md:63-66`; the six secured runs nevertheless export non-zero values (law 0.0367, philosophy 0.2807, history 0.2806, psychology 0.3082, engineering 0.1657) | `known-defects.md` vs `*_secured/*_thesis_metrics.csv` | **contradiction between doc and artifact** | `7_Discussion.tex:295-300` reports 0.2114 as a diagnostic with the aggregation defect named; the doc's blanket "never measured" is now stale |
| A6.5 | ~4.2% of `mmlu_pro` rows unlinked | ~500 of 12,032, believed sentinel, **not confirmed** | `known-defects.md:81-87` | Q | yes, `5_Experimental_Design.tex:126-130` |
| A6.6 | `wall_ms` never populated | 0 in every row of every bundle | `known-defects.md:60-61` | — | no (correctly absent) |
| A6.7 | three tests wrote to production DBs | fixed 2026-07-26 | project memory | — | no (correctly absent) |
| A6.8 | multi-seed loop corrupts routing | `seeds = [...]` routes held-out queries only for the first seed | project memory | Q — bounds any future multi-seed claim | no |
| A6.9 | **engineering's registered null cites a superseded p-value** | `prereg_generic_judge_baseline.md:415-416` registers engineering as "does NOT reorder under either policy (**p = 0.962** / 0.706)". 0.962 is the **n = 8** screen value from the table `arena-math-findings.md:764-765` says "**should not be cited**". The current arm-(A) value is **p = 0.000** — engineering *does* reorder under the per-domain roster (R4). Only arm (B), p = 0.706, clears it. Question count also differs: 267 registered vs 254/261 measured | R4 + prereg | **Q — materially** | the "second registered null" | **NO.** `6_Results.tex:609-618` presents engineering as a clean registered null with no mention of the half-superseded registration |
| A6.10 | the rubric-specificity null arm was **registered at 87 random cells and run at 13** | `prereg_rubric_specificity.md:35`, `:82-83` specify 87 random + 14 domain inductions; `:133-135` records the run as 13 size-matched cells; `:148-149` "The domain-14 intermediate arm was not run" | prereg doc | **Q** | link 2 | partly — `6_Results.tex:951-958` says "13 random cells is a small null arm", but **not that 87 were registered** |
| A6.11 | screen permutation-null draw count disagrees between sources | `arena-math-findings.md:802` says **1,500** draws for the run that produced law 0.955/p = 0.008 and Math 1.000/p = 1.000; `prereg_generic_judge_baseline.md:172-178` quotes the same two numbers as a **2,000**-draw null | the two docs | **Q** | the screen | `6_Results.tex:1096-1102` prints **1,500**; the prereg says 2,000 — one of them is wrong |
| A6.12 | `rank_history.csv` is structurally empty | the `scores` column is `0.0000;…` in **all 9,906 rows** | `arena-math-findings.md:327` | — | nothing depends on it | no (correctly absent) |
| A6.13 | the `Meta-Llama-3-70B-Instruct` id-space ambiguity **resolves in the thesis's favour** | the 8-model pilot roster contains `Meta-Llama-3_1-70B-Instruct` (verified directly, R7), **not** the excluded `Meta-Llama-3-70B-Instruct`. So `arena-math-findings.md:799-800`'s "it should never have been in the 8-model arena roster either" is **wrong**, and `10_Appendix_ModelRoster.tex:93-94` is right | R7 | S | roster hygiene | the `.tex` is already correct; the **doc** needs the fix |

## A7. Results that are withdrawn, irreproducible, or must not be restated

| # | figure | status | source | must the `.tex` change? |
|---|---|---|---|---|
| A7.1 | redundancy 72.2% / 42.2% | **irreproducible**, withdrawn | `7_Appendix_TuningProtocol.tex:422-428`, `7_Discussion.tex:283-286` | already withdrawn — **do not reintroduce** |
| A7.2 | correctness-blind ρ 0.74–0.76 | **irreproducible**; recomputation on the same verdict set returns 0.90–0.93 (R2 gives Run A MAIN 0.9048 / GENERIC 0.9286 on the 576-comparison blind subset) | R2, `6_Results.tex:180-192` | already withdrawn; the magnitude stays withdrawn |
| A7.3 | leaf-level 0.922 | reproduces only on the snapshot's own construction assignments over the full corpus; the re-routed reserved-only recomputation gives **0.884** (R3) | R3, `6_Results.tex:1016-1023` | footnote exists; the **table cell still prints 0.922 unqualified** |
| A7.4 | centred-residual quartet −0.119/−0.024/−0.024/−0.024 | **reproduces under no single centring convention** (R3 gives +0.024/−0.024 at 8 models, −0.109/−0.009 at the 11-band) | R3 | **BLOCKING** — see B-2 |
| A7.5 | 11-band flatness 0.973 / 0.936 | **no source anywhere**; R3 gives 0.948 / 0.908 | R3, `docs/reconciled-argument.md:1173` | **BLOCKING** — see B-2 |
| A7.6 | everything void after `c381211` | maxK plateau, k-fallback figures, five-seed leaf counts, core/fringe, matched-k ARI, within-node nulls, λ1 proxy, "39 of 42"/"379 of 459" | `docs/void-results.md:15-28` | the `.tex` already marks these `void as to values`; **"39 of 42" is *wrong*, not stale, and must never return** |

## A8. The per-leaf-versus-domain bound — the single most limiting qualifier

| # | measured | value | source | V | in the `.tex`? |
|---|---|---|---|---|---|
| A8.1 | per-leaf rankings vs the domain ranking, law | leaf-vs-domain ρ **0.895–0.993**, against a GT-vs-GT baseline of 0.873–0.970 | law run, per-leaf leaderboards | **Q — the strongest qualifier the project holds** | **NO — nowhere in the thesis** |
| A8.2 | interpretation | the rubric **sharpens the estimate of a common ranking**; it does not reveal specialisation. This bounds what every +Δρ in A1 can mean | derived from A8.1 + A5 | **Q** | **NO** |

---

# IMPLEMENTATION LOG — 2026-07-30

The action list below was implemented in the same session. Status per item:

**Done (BLOCKING):** B-1 (four sites), B-2, B-3, B-4, B-5, B-6, B-7, B-8, B-9.
B-10 restated as an explicit submission blocker in the file's own TODO.

**Done (HIGH):** B-11 (two-convention table), B-12 (full 14-row screen table added,
`tab:domain-screen`), B-13, B-14 (two sites), B-15, B-16, B-17, B-18, B-19, B-20,
B-20a, B-20b, B-20c, B-21, B-22, B-23.

**Done (MEDIUM/POLISH):** B-24, B-25, B-26, B-29, B-30, B-35, B-36, B-37, B-38,
B-39, B-40.

**Not done, and why:**

* **B-20d** (the 0.823-vs-0.922 redundancy-inversion conflict). Needs a decision on
  which cell-size convention governs — constituent queries or held-out per cell.
  That is an authorial call about what the quantity means, not a transcription fix,
  and guessing it would put a number in the thesis that the sources do not settle.
  The passage is left as it stands.
* **B-27, B-28** partially: `model_domain_scores.csv` and its generator are now cited
  in Chapter 5; `reserved_leaf_assignments.csv` is cited in the granularity table note.
* **B-31** is a `docs/` fix (routing-ECE contradiction), not a `.tex` fix.
* **B-32, B-33, B-34, B-41, B-42, B-43, B-44** left: figure placeholders, a stray
  em-dash cell, and author `% TODO` comments that do not render.

**One audit finding was corrected during implementation.** §A8 quoted a
leaf-vs-domain range (law 0.895–0.993 against a GT baseline of 0.873–0.970) taken
from the session brief. Recomputing it gives law 0.874–0.988 against 0.935–0.996 —
and the direction reverses, with the ground-truth baseline *above* the arena
correlation. The aggregation is also mechanically confounded, since the domain-level
score is built as the mean of the leaf scores being correlated against it. Those
numbers were therefore **not** written into the thesis. B-15 was implemented instead
from the granularity result (between-cell ρ 0.884–0.908 at leaf scale), which is
reproducible and carries the same bound.

---

# PART B — THE ACTION LIST

Ranked BLOCKING → HIGH → MEDIUM → POLISH. Every entry cites `file:line` against the **current**
files. Items already corrected this session in `1_Introduction.tex` and `6_Results.tex` are not
re-reported.

## BLOCKING

**B-1 · `report/03_Content/4_Methodology.tex:156-159` — an absolute claim the artifact refutes.**
Says: *"every Bradley--Terry standard error this system reported before the correction was the
floor constant rather than a measurement."* The artifact says otherwise: Run A's own
`node_bt_states` (fit 2026-07-27 05:15–05:21Z, before `a92a3ed` at 15:27Z) holds 176 standard
errors with median 0.0907/0.1003 and **45 at the 0.01 floor — 25.6%, not 100%** (R10).
**Adjust to:** "every pre-correction standard error was either clamped at the floor (25.6% of
Run A's stored values) or under-estimated by the over-subtracted (K−1)/K² = 0.109 at K = 8; none
of them is a valid measurement." The conclusion is unchanged and the sentence becomes true.
*Same sentence, same fix:* `report/03_Content/7_Discussion.tex:249-254` ("so every pre-correction
standard error was the floor constant") and `report/04_Appendix/12_Appendix_Numerics.tex:155-157`
("Every standard error computed under the wrong constant … clamped at the floor of 0.01 rather
than measured"), plus `report/04_Appendix/7_Appendix_TuningProtocol.tex:385-386`.

**B-2 · `report/03_Content/6_Results.tex:1041-1044` — two numbers with no provenance that do not
reproduce.** Says: *"Re-derived at the corrected band it holds: 0.929 and 0.922 at 8 models, and
0.973 and 0.936 at the 11-model band."* `tools/analysis/discriminative_flatness.py` returns
**0.929 / 0.884** at 8 models and **0.948 / 0.908** at the 11-model band (R3). The project's own
review already records 0.973/0.936 as unsourced (`docs/reconciled-argument.md:1173`,
`docs/peer-review-2026-07-28.md:352` and `:459`).
**Adjust to:** replace with the reproduced pair and its script — "0.948 at 14 domains and 0.908 at
87 leaves, IQRs [0.927, 0.964] and [0.860, 0.942], overlapping
(`tools/analysis/discriminative_flatness.py`)". The flatness conclusion survives the substitution;
the delta is +0.040 rather than +0.037.

**B-3 · `report/03_Content/6_Results.tex:1026-1035` — the centred-residual quartet.** Says:
*"Centring out each model's global mean leaves residual correlations of −0.119, −0.024, −0.024 and
−0.024."* R3 returns **+0.024 / −0.024** at the 8-model roster and **−0.109 / −0.009** at the
11-band; no single centring convention returns the printed quartet, and the sign of the first
value flips between rosters. The claim built on it — "indistinguishable from the centring null,
not zero" — is the right claim but is currently resting on numbers that cannot be regenerated.
**Adjust to:** report the two reproducible pairs with their roster named, or mark the quartet
`unresolved` under the convention already declared at `1_Introduction.tex:428-429` ("Where a
number exists but could not be reproduced under a stated convention, it is reported as unresolved
rather than quoted"). Do not restate the quartet.

**B-4 · `report/03_Content/5_Experimental_Design.tex:45-48` — the scope sentence is four domains
out of date.** Says: *"Two domains are reported in this thesis --- Math and law; replications on
philosophy and history were launched under the same protocol and their results are pending."*
Six domains have completed (A1.1–A1.6), all six against the same snapshot, seed and roster, and
Chapter 6 reports all six at `6_Results.tex:592-598`. The chapter that *specifies the experiment*
contradicts the chapter that reports it.
**Adjust to:** six paired domains — law, philosophy, history, psychology (flagged by the screen)
and Math, engineering (cleared by it); four carry a prior registration, two are replications.

**B-5 · `report/03_Content/7_Discussion.tex:152-154` — same staleness, in External Validity.**
Says: *"Every arena result in this thesis is on one corpus, at seed 42, on two domains (Math and
law; replications on philosophy and history are launched with results pending), with rosters of 8
to 12 models."* **Adjust to:** "on six domains of fourteen, at seed 42". This is the single
sentence a reviewer will use to size the contribution, and it currently understates it by a factor
of three while also being false.

**B-6 · `report/03_Content/8_Conclusion.tex:62-66` — same staleness, in the scope paragraph.**
Says: *"two domains (Math and law; replications on philosophy and history are launched with
results pending)."* **Adjust to:** six domains, and re-state which four were registered.

**B-7 · `report/03_Content/8_Conclusion.tex:120-127` — a future-work item that is already done.**
Says: *"Philosophy and history … their replications under the same paired protocol are launched
and their results are pending, and until they land, the law result is a single-domain finding."*
They landed: philosophy +0.0490/+0.0420, history +0.0105/+0.0105 (A1.2, A1.3), plus psychology and
engineering. **Adjust to:** delete the item and replace it with the two future-work items the
six-domain result actually creates — (i) the four domains the screen flags that were **never run**
(economics p = .003, health p = .001, physics p = .017, other p = .041; A4.1); (ii) a
comparison-level rather than question-level pairing (A1.11).

**B-8 · `report/03_Content/8_Conclusion.tex:47-60` — RQ2's answer names only Math and law.** The
paragraph answers RQ2 from two domains. The evidence now answers it from six, and the shape of the
answer changes: it is no longer "one null and one positive" but "**a screen that predicts the sign
of Δρ in 6 of 6 domains**, four positives in the four flagged domains it was run on, a clean null
in the flagged-clear domain (engineering), and one failed registered prediction (Math)".
**Adjust to:** the six-domain formulation, with A4.2's concordance as the headline and the
"screen flags 8 of 14, four were run" caveat attached.

**B-9 · `report/02_Prematter/e_Abstract.tex:51-53` — "the one domain where the roster's models
measurably reorder".** Says: *"On law, the one domain where the roster's models measurably
reorder, the per-leaf arm leads under one tie convention and exactly ties under the other."*
The screen flags **eight** domains at p < 0.05 on the fixed band (A4.1), and four of them were run
and all four came out positive. **Adjust to:** "In the four flagged domains that were run — law,
philosophy, history, psychology — the per-leaf arm leads under both tie conventions and never
reverses; on law it leads under one and exactly ties under the other." This is a strictly stronger
claim and it is the one the evidence supports.

**B-10 · `report/02_Prematter/e_Abstract.tex:15-21` — the German abstract does not exist.**
`% TODO(author): German abstract` with only the `\germankeywords` macro after it. A German
abstract is mandatory for a TU Berlin thesis. BLOCKING on submission, not on argument.

## HIGH

**B-11 · `report/03_Content/6_Results.tex:1009-1011` — the granularity table still prints 0.922
at 87 leaves.** The footnote at `:1016-1023` correctly gives both readings, but the table cell is
unqualified and it is the cell a reader quotes. `discriminative_flatness.py` returns **0.884** on
re-routed reserved-only assignments (R3, A5.1). **Adjust:** print `0.922 / 0.884` in the cell with
a convention marker, or move the governing convention into the column header. The same applies to
the 88-leaf row at `:1010` (0.922) and the 152-leaf row at `:1012` (0.905), neither of which was
regenerable in this audit.

**B-12 · `report/03_Content/6_Results.tex:1096-1102` — the screen is reported on two domains when
it was computed on fourteen.** Only law (n = 287, ρ = 0.955, p = 0.008) and Math (n = 393,
ρ = 1.000, p = 1.000) are printed. Both reproduce exactly (R4). The other twelve rows exist and
are what turn the screen from an anecdote into an instrument. **Adjust:** print the full 14-row
arm-(B) table from `domain_reorder_screen.py`. It costs one table and it is the single cheapest
strengthening available in this document, because it converts "the screen selected law" into "the
screen was computed on all fourteen domains in advance, flagged eight, and its classification
matches the sign of Δρ in all six domains subsequently run".

**B-13 · `report/03_Content/6_Results.tex:654-676` — the concordance claim needs its denominator.**
Says the screen's and the arena's verdicts *"agree in five of six domains"*. On the sign of Δρ they
agree in **six of six**: the screen clears Math, and Math's Δρ is negative — the screen predicted
"no per-leaf advantage" and there was none. What failed in Math was the *pre-registration's null
prediction*, not the screen. **Adjust:** separate the two verdicts explicitly — "the screen's
classification matches the sign of Δρ in six of six; the pre-registration's Math prediction (a
null) failed, because the observed Δρ is decisively negative rather than zero." This is more
favourable to the thesis *and* more accurate.

**B-14 · `report/03_Content/1_Introduction.tex:513-515` and `:56-58` — "the four domains the
screen flags".** The screen flags eight (A4.1). Four flagged domains were run. **Adjust:** "the
four flagged domains that were run" (both sites). Small edit, removes a factual error that a
reviewer who opens `domain_reorder_screen.py` will find immediately.

**B-15 · missing entirely: the per-leaf-versus-domain bound (A8).** The project holds a
measurement — law leaf-vs-domain ρ 0.895–0.993 against a GT-vs-GT baseline of 0.873–0.970 — which
says the rubric **sharpens the estimate of a common ranking rather than revealing specialisation**.
It bounds the meaning of every positive Δρ in A1. It appears nowhere in `report/`. Natural home:
a new paragraph in `6_Results.tex` immediately after the six-domain table at `:603-607`, and one
sentence in `7_Discussion.tex` §disc-rq2 (around `:43-63`). Without it, `6_Results.tex:603-607`
("in all four flagged domains the per-leaf arm leads") reads as a specialisation claim that the
data does not support.

**B-16 · missing entirely: the within-domain-vs-between-domain leaf divergence (A4.3).** Within
one domain, leaf-pair rankings agree *less* (median ρ 0.9066, IQR [0.852, 0.945], 293 pairs) than
whole domains do with each other (0.9422, IQR [0.917, 0.963], 91 pairs), on the 12-model arena
roster. This is the direct empirical motivation for sub-domain cells and it is absent from the
thesis. It also carries a hard caveat: **no permutation null was run**, and the gap halves on the
11-model band (0.9314 vs 0.9476). Natural home: `1_Introduction.tex` §1.2, alongside A4.6 at
`:158-172`. **State it with the missing null named**, or it will be attacked as a comparison of
293 correlated pairs against 91 independent ones.

**B-17 · `report/03_Content/6_Results.tex:96-105` — the four void conditions are not verified per
domain.** The paragraph asserts the paired protocol for the four later domains. R12 shows the
**held-out question sets are identical in all six (overlap 1.000)** — good — but the
(question, model-pair) comparison sets differ: philosophy 89.9% overlap, engineering 83.3%
(A1.10, A1.11). Philosophy carries the **largest** Δρ in the study and 10% of its comparisons are
unmatched between arms; engineering is a **registered null** and 17% are unmatched. **Adjust:**
state the pairing level explicitly ("paired at the question, not at the comparison"), print the
per-arm comparison counts (1319/1188 and 792/660), and say why the arms differ. A reviewer who
finds this unflagged will discount philosophy's headline result.

**B-18 · `report/03_Content/6_Results.tex:88-93` — the bootstrap floor is attributed only to law.**
R9 confirms **all five post-law runs** carry 66 of 66 pairs at ≥ 2, and that Math (Run B) has 46
pairs with no data at all. **Adjust:** say the floor is present in law, philosophy, history,
psychology and engineering, and absent in Runs A and B. As written, a reader cannot tell whether
philosophy's and engineering's estimators were identified.

**B-19 · `report/03_Content/7_Discussion.tex:37-41` — "an inference from the Math and law runs".**
It is now an inference from six runs, and the six-domain pattern is *stronger* evidence for the
same conclusion, because the two domains where the judge's key agreement is highest (Math 94.2/94.7
and engineering 89.0/88.5) are exactly the two where the partition buys nothing. **Adjust:** make
that the argument. It is the best version of the RQ1 thesis available and it currently is not made.

**B-20 · missing: the BT standard errors in the six paired runs are real (A1.15).** The corrections
register at `7_Discussion.tex:256-269` says Runs B and C "ran with measured standard errors" but
offers no evidence. The secured exports do: 288 leaf-level standard errors across five domains,
median 0.31–0.48, minimum 0.149, **zero at the 0.01 floor**. **Adjust:** add one clause with those
numbers at `7_Discussion.tex:268-269`. This converts an assertion into a check.

**B-21 · `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:211` — contradicts the
certificate.** Says *"Canonical runs converge at approximately iteration~15."* The frozen artifact
certifies at **iteration 10** with iterations 8–10 identical
(`7_Appendix_TuningProtocol.tex:43-44`, `6_Results.tex:736-741`, A4.8). **Adjust to** iteration 10,
or scope the sentence to non-canonical configurations and say so.

**B-22 · `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:207-210` vs
`report/03_Content/3_System_Architecture.tex:138-143` — two different convergence rules.** The
appendix gives one rule (edit count zero for five consecutive iterations after a minimum floored
at 5); Chapter 3 gives a disjunction ("unchanged for five consecutive iterations, **or** when the
objective has moved by less than the tolerance for five consecutive iterations"). The source
(`TaxonomyStabilizer.kt`, `requiredConsecutive = 5`, `singleIterConverged = !isFirstIteration &&
(ged == 0)`) implements the **GED-only** form gated on `enableEarlyStopping`. Chapter 3's second
disjunct is not in the stabilizer. **Adjust:** make both files state the implemented rule.

**B-23 · `report/04_Appendix/8_Appendix_JudgeGeneration.tex:35-38` — the judge template section is
empty.** `\label{sec:judge-template-full}` exists with only
`% Full verbatim template goes here — insert the JudgePrompts.kt / GenericPairwiseJudgePrompt.kt
template text`. The judge prompt is the instrument of the thesis's strongest result; an empty
appendix section for it is a reproducibility hole. HIGH rather than BLOCKING only because the
material exists in source.

**B-20a · `report/03_Content/6_Results.tex:609-618` — engineering is presented as a clean registered null, but half its registration is a superseded number.** The text says *"The registered prediction for engineering is met."* The registration
(`docs/prereg_generic_judge_baseline.md:415-416`) reads *"does NOT reorder under either policy (p = 0.962 / 0.706)"*. The
0.962 is the **n = 8** screen value, from the table `docs/arena-math-findings.md:764-765` explicitly says *"should not be
cited"*. Re-run today (R4), engineering is **p = 0.000** under the per-domain roster (A) and p = 0.706 under the fixed band
(B). Under policy (A) engineering **does** reorder. **Adjust:** state that engineering's null is registered against the
fixed-band screen only, that it reorders under the per-domain roster, and that the registration quotes a superseded
per-domain value. The result — a one-grid-step sign-flipping null — is unchanged; the registration's provenance is not.
This is the item most likely to be found by an examiner who opens the prereg, because the thesis sells pre-registration hard.

**B-20b · `report/03_Content/6_Results.tex:906-914` and `:951-958` — the rubric null was registered at 87 random cells and
run at 13.** `docs/prereg_rubric_specificity.md:35` and `:82-83` specify "~174 additional inductions (87 random + 14
domain)"; `:133-135` records "A random-cell arm of **13** size-matched cells (not the 87 originally specified above)";
`:148-149` records "The domain-14 intermediate arm was not run." The thesis states the small-arm caveat at `:951-958` but
not the deviation from the registered design. **Adjust:** name the deviation in one clause. The p-value survives it
(reproduced today at 1.210e-6, R6), and disclosing a registered-design deviation is strictly safer than having it found.

**B-20c · `report/03_Content/6_Results.tex:1096-1102` — the screen's null draw count conflicts with its own
pre-registration.** The text says **1,500**-draw, matching `docs/arena-math-findings.md:802`;
`docs/prereg_generic_judge_baseline.md:172-178` quotes the identical law and Math numbers as a **2,000**-draw null. One is
wrong. **Adjust:** re-run `domain_reorder_screen.py` with the count stated in the text and record it, or reconcile the two
documents. Trivial to fix, and it sits on the instrument B-12 and B-13 want to promote.

**B-20d · `report/04_Appendix/7_Appendix_TuningProtocol.tex:404-408` and `report/03_Content/7_Discussion.tex:271-281` —
the redundancy-compression arithmetic rests on a contested input.** Both quote "at a 40.8-query cell an observed median ρ
of 0.823 corrects to 0.978 … and to 0.874" and the "spread of 0.219 to 0.088" that follows from it. The 0.823-at-40.8
figure comes from `docs/arena-math-findings.md:934`; `docs/prereg_discriminative_power.md:78` gives the same quantity as
**0.922 at 74 queries per cell**. At 0.922 the c = 2.52 correction lands near 0.978 — **above** the 0.90 threshold, so the
inversion the passage describes does not occur. The two sources are never reconciled anywhere in the project. **Adjust:**
resolve which cell-size convention governs (constituent queries vs held-out per cell) before the compression claim is
restated, or scope the claim to the convention that produced it. The conclusion drawn from it — that the reliability leg
of the coarse-cut argument weakens and the identification-cost leg carries it alone — is the one that would change.

## MEDIUM

**B-24 · `report/03_Content/6_Results.tex:346-350` — 99.4% needs its denominator named.** The
measurement is **10 winner flips**. Under "both arms decisive" the rate is 1301/1311 = **99.24%**;
counting the 197 tie/decisive mismatches as agreement gives 1726/1736 = **99.42%** (R7, A3.1). Both
are defensible; the thesis prints 99.4% here and at `:698-708`, `7_Discussion.tex:56-63`,
`8_Conclusion.tex:21-22` and `e_Abstract.tex:44-45`. **Adjust:** name the convention once, at
`6_Results.tex:346-350`, and let the other four sites inherit it. Given rule D5's own logic, an
unnamed denominator on the project's most-quoted number is an avoidable target.

**B-25 · `report/03_Content/5_Experimental_Design.tex:404-405` vs `6_Results.tex:39-42` — two
different grid-step tables.** Ch.5 lists "0.0119 at M = 8, **0.0060 at M = 10**, 0.0035 at M = 12";
Ch.6 lists "0.0119 at M = 8, **0.0046 at M = 11**, 0.0035 at M = 12". Both are arithmetically
right for their own M; no run uses M = 10. **Adjust:** drop the M = 10 row from Ch.5 and use
M = 11 (the screen's and the reliability fit's roster) in both.

**B-26 · missing: the blank-`pred` accounting (A4.5).** Four models lose 3.7–11.0 accuracy points
because a blank prediction is scored incorrect, at blank rates of 8.3–18.8%. The **ranking is
identical 12/12** under `acc` and `acc_parsed`, which is precisely why every rank-based result in
the thesis is unaffected — and that is a defence worth stating rather than leaving for a reviewer
to discover. Natural home: `5_Experimental_Design.tex` §rosters, near `:212-227`, or a footnote at
`4_Methodology.tex:241-245` where ground-truth accuracy is defined. Cite
`tools/analysis/export_gt_scores.py` and `model_domain_scores.csv`.

**B-27 · missing: `model_domain_scores.csv` is never cited.** It is the ground-truth denominator of
every ρ in the thesis and of the A4.6 reversal pairs at `1_Introduction.tex:162-172`. There is no
pointer to it or to its generator anywhere in `report/`. **Adjust:** cite it where the reversal
pairs are stated and where the primary metric is defined (`4_Methodology.tex:241-245`).

**B-28 · missing: `reserved_leaf_assignments.csv` provenance.** 87 leaves, 3,863 assignments; it is
the routing table underneath the granularity result and the A4.3 divergence measurement. Referenced
implicitly by the "re-routed, reserved-only assignments" footnote at `6_Results.tex:1016-1023` but
never named. **Adjust:** name the file in that footnote — it is what makes the 0.922-vs-0.884
distinction checkable.

**B-29 · `report/03_Content/6_Results.tex:632-652` — the near-clone check reports one of its three
registered predictions.** Three were registered (`docs/arena-math-findings.md:703-706`): (1) the pair
ranks adjacently or with at most one model intervening; (2) their pairwise tie rate exceeds the
roster average; (3) their BT difference is within 2 SE of zero. The thesis reports **only (2)**.
(1) and (3) are computable from the five secured leaf leaderboards, which now carry real standard
errors (A1.15). Indicative recomputation (R13, mean-of-leaf-BT with a naive combined SE — **not** the
pooled MM fit the thesis uses): **(1) is met in 10 of 10 arms**, maximum one model intervening;
**(3) is met in 7 of 10**, failing on law MAIN (2.38 SE), psychology MAIN (2.76 SE) and philosophy C5
(2.22 SE). **Adjust:** compute both under the pooled fit and report all three predictions. The check
currently reads as mixed on one leg when it is strong on another, and prediction (3) is the one that
tests over-resolution — a validity failure ρ cannot see, which is exactly why it was registered.
Separately, engineering also ran and gave the pair **2 direct comparisons**, unevaluable as philosophy
was (R9, A1.14); report five domains with two unevaluable so the coverage matches the run inventory.

**B-30 · `report/03_Content/6_Results.tex:29-32` — the scheduler-bias caveat has no measurement.**
"the scheduler over-samples uncertain pairs" is asserted; the measurement exists — top-model share
of comparisons runs 43.2% (psychology) to 67.9% (history) across the six runs (R9, A1.13).
**Adjust:** add the range. It also justifies the BT-θ-never-win-rate rule concretely.

**B-31 · `docs/known-defects.md:63-66` contradicts the secured exports on routing ECE (A6.4).** The
doc says `computeRoutingECE` "returns 0.0 … in every run in the project's history. Do not report
routing ECE"; the six secured `*_thesis_metrics.csv` carry non-zero values (0.0367 to 0.3082), and
`7_Discussion.tex:295-300` reports 0.2114. Two of these three are wrong. This is a docs fix, not a
`.tex` fix, but `7_Discussion.tex:295-300` and
`9_Appendix_MetricDefinitions.tex:144-153` should not be trusted until it is resolved. **Resolve
before submission.**

**B-32 · `report/03_Content/6_Results.tex:39-42` — "differences below one grid step are not
differences" sits one paragraph from engineering's ±0.0035 result.** Engineering's Δρ *is* one grid
step and flips sign (A1.5). The reading is correct and registered, but the two statements are far
enough apart (`:39-42` and `:609-618`) that a reader may take them as contradictory. **Adjust:**
cross-reference at `:609-618`.

**B-33 · `report/03_Content/6_Results.tex:1073-1086` — placeholder figure.** `\fbox` stand-in
labelled "(placeholder)", describing four box plots and a centred-residual panel. Given B-3, the
centred-residual panel must not be drawn from the withdrawn quartet. **Adjust:** either produce the
figure from `discriminative_flatness.py` extended to dump the per-pair distribution, or cut it.

**B-34 · `report/03_Content/6_Results.tex:312` — an empty cell in `tab:capture-survives`.** The
trace × trace / gap ≥ 40 pp cell is `---`. **Adjust:** state "no comparisons in this cell"
explicitly rather than leaving an em-dash a reader will read as a missing measurement.

**B-35 · `report/04_Appendix/7_Appendix_TuningProtocol.tex:443-447` and `:475-482` — two open
`\todo[inline]` blocks that will render into the PDF.** They ask for the correctness-blind ρ
convention (resolved: withdrawn, A7.2) and for recomputation of BT intervals (resolved by policy:
none is quoted, A6.3). **Adjust:** convert both into prose statements of the resolution, or remove.
`main.tex:107` runs `\listoftodos`, so every `\todo` is currently printed.

**B-36 · `report/04_Appendix/10_Appendix_ModelRoster.tex:65-68` — an open `\todo` recording a real
roster mismatch.** "until then c = 2.52 and the law p = 0.008 carry a roster mismatch." This is
true and material: the reliability constant and the screen are fitted at the **11-model band**
while the arena runs the **12-model roster** (R3, R4, R5). **Adjust:** promote it from a `\todo` to
a named limitation in `7_Discussion.tex` §disc-external-validity, because it qualifies the screen —
the instrument B-12/B-13 want to promote.

**B-37 · `report/02_Prematter/g_Nomenclature.tex:8` — nomenclature is empty** (`% No symbols are
defined yet.`) while `main.tex:104` prints it. The thesis defines J, τ, κ, µ, ρ, θ, z*, ε_sep,
n_min, α and Δρ. **Adjust:** populate or suppress the section.

## POLISH

**B-38 · `report/03_Content/3_System_Architecture.tex:15-18`** says "four measurement rules";
`4_Methodology.tex:276-351` defines five (D1–D5). D5 was added by the tie-policy result.

**B-39 · `report/03_Content/3_System_Architecture.tex:47`** ends `…depends on them.vcbn` — stray
characters.

**B-40 · `report/03_Content/2_Literature.tex:667-670`** cites `ch:methodology` twice for two
different pointers ("the system design is specified in Chapter X, and the formal foundations are
derived in Chapter X").

**B-41 · `report/04_Appendix/7_Appendix_TuningProtocol.tex:86`** gives the L9 sweep levels for
`minClusterSize` as {50, 75, 100}; the canonical value is **55** (`:18`), which is not among them.
Say that 55 was chosen after the sweep, on the budget argument of `frozen-artifact.md:72-87`.

**B-42 · `report/04_Appendix/7_Appendix_TuningProtocol.tex:185`, `11_Appendix_…:701`, `:717`** —
three `\fbox` figure placeholders ("Figure A.1", "Figure E.1", "Figure E.2") with hardcoded figure
letters inside the placeholder text.

**B-43 · `report/03_Content/1_Introduction.tex:317`, `:374`, `:383`, `:420`, `:468`, `:479`,
`:489`, `:121`** and `2_Literature.tex:82`, `:656` — author `% TODO` comments questioning the
thesis's own framing. They do not render, but several of them (`:374` "the results are more
mitigated than that", `:383` "Maybe change a bit the thesis claims", `:489`) are pointing at
exactly the staleness B-4 through B-9 fix. Once the six-domain reframing lands, most of them
resolve.

**B-44 · `report/03_Content/1_Introduction.tex:116-127`, `:182-184`** — the synthetic
Model A / Model B table. It is correctly declared illustrative, but A4.6 gives three **real** pairs
with the same shape. Consider replacing the synthetic table with the deepseek / gpt-4o-mini pair
(agg gap 2.4, engineering +12.4, health −9.2). A real example makes the motivating argument
unattackable and the synthetic one does not.

---

# PART C — RESULTS THE THESIS DOES NOT USE, AND CLAIMS WITH NO RESULT

## C.1 Held but unused (ranked by what they would buy)

| result | where it lives | what it would buy | proposed site |
|---|---|---|---|
| **The full 14-row domain screen** (A4.1) | `tools/analysis/domain_reorder_screen.py` | turns the screen from a selection anecdote into an instrument with 6/6 predictive concordance | `6_Results.tex:1096-1102` (B-12) |
| **Screen-vs-arena sign concordance, 6 of 6** (A4.2) | derived, R4 + R1 | the strongest single positive claim available for RQ2 | `6_Results.tex:654-676`, `8_Conclusion.tex:47-60` (B-13, B-8) |
| **Per-leaf vs domain ranking bound** (A8) | law leaf leaderboards | honest bounding of every +Δρ; pre-empts the obvious attack | `6_Results.tex` after `:607`, `7_Discussion.tex` §disc-rq2 (B-15) |
| **Within- vs between-domain leaf divergence** (A4.3) | R8, `reserved_leaf_assignments.csv` | the missing empirical motivation for sub-domain cells | `1_Introduction.tex` §1.2 (B-16) |
| **Real BT standard errors in the six paired runs** (A1.15) | `*_secured/*_leaf_leaderboard.csv` | evidence for a claim currently asserted | `7_Discussion.tex:268-269` (B-20) |
| **Blank-`pred` ranking invariance, 12/12** (A4.5) | `model_domain_scores.csv` | a pre-emptive defence of every rank result | `5_Experimental_Design.tex` §rosters (B-26) |
| **Per-domain tie rates, all twelve arms** (A1.9) | R1 | supports D5 across six domains rather than one | `6_Results.tex:571-598` table |
| **Top-model comparison share, 43.2–67.9%** (A1.13) | R9 | grounds the scheduler-bias caveat | `6_Results.tex:29-32` (B-30) |
| **Reliability refit at both rosters: c = 7.71 / 5.05, ratio 0.65×** (A5.5) | `tools/analysis/reliability_constant.py` | shows the roster dependence was *measured*, not assumed | `5_Experimental_Design.tex:426-433` |
| **All three Mann–Whitney variants reproduce to 2 s.f.** (A3.3) | R6 | robustness of the one unambiguous positive | `6_Results.tex:906-914` already prints them; add "reproduced 2026-07-30" |
| **Near-clone predictions 1 and 3** (A1.16) | R13, secured leaf leaderboards | completes a registered check the thesis reports one-third of | `6_Results.tex:632-652` (B-29) |
| **The `arx` side-channel verifiably did not reach the paired runs** (A1.17) | R14, current corpus | turns an assertion at `7_Discussion.tex:109-114` into a check | same site, one clause |

## C.2 Claims in the thesis with no result behind them

| claim | site | status |
|---|---|---|
| "every pre-correction standard error was the floor constant" | `4_Methodology.tex:156-159`, `7_Discussion.tex:249-254`, `12_Appendix_Numerics.tex:155-157`, `7_Appendix_TuningProtocol.tex:385-386` | **refuted by the artifact** (A2.6) — B-1 |
| 11-band flatness "0.973 and 0.936" | `6_Results.tex:1041-1044` | **no source in any script, doc or db** (A5.2) — B-2 |
| centred residuals "−0.119, −0.024, −0.024, −0.024" | `6_Results.tex:1026-1035` | **reproduces under no convention** (A5.4) — B-3 |
| "Canonical runs converge at approximately iteration 15" | `11_Appendix_DAG…:211` | contradicted by the certificate (A4.8) — B-21 |
| "the one domain where the roster's models measurably reorder" | `e_Abstract.tex:51-53` | eight domains are flagged (A4.1) — B-9 |
| "the four domains the screen flags" | `1_Introduction.tex:56-58`, `:513-515` | eight are flagged, four were run — B-14 |
| "replications … results are pending" ×4 | `5_Exp:45-48`, `7_Disc:152-154`, `8_Concl:62-66`, `8_Concl:120-127` | four completed runs contradict it — B-4…B-7 |
| convergence "or when the objective has moved by less than the tolerance for five consecutive iterations" | `3_System_Architecture.tex:140-143` | second disjunct not in `TaxonomyStabilizer.kt` — B-22 |
| 152-leaf row ρ = 0.905 | `6_Results.tex:1012` | not regenerable in this audit; no 152-leaf artifact was located | verify or mark unresolved |
| 88-leaf (biased router) row ρ = 0.922 | `6_Results.tex:1010` | same convention problem as the 87-leaf cell — B-11 |
| routing ECE 0.2114 | `7_Discussion.tex:295-300`, `9_Appendix_MetricDefinitions.tex:151` | `docs/known-defects.md:63-66` says the metric was never measured; the secured exports disagree with both — B-31 |
| identification cost "7 pairs of 28, 32.9–45 comparisons" | `6_Results.tex:679-694` | measured at 8 models; the thesis says the arithmetic "was not redone" at 11 models / 55 pairs. Self-declared, but it is the surviving leg of the coarse-cut argument after A5.5 |
| "the judge is in no roster … no self-preference confound" | `10_Appendix_ModelRoster.tex:116-118` | true of these runs, enforced by nothing — already stated as such |
| "The registered prediction for engineering is met" | `6_Results.tex:609-618` | half the registration is a superseded p-value (A6.9) — B-20a |
| the rubric-null arm's registered size | `6_Results.tex:906-914` | 87 registered, 13 run (A6.10) — B-20b |
| screen null "1,500-draw" | `6_Results.tex:1096-1102` | the prereg says 2,000 for the same numbers (A6.11) — B-20c |
| "observed median ρ of 0.823 … spread of 0.219 to 0.088" | `7_Appendix_TuningProtocol.tex:404-408`, `7_Discussion.tex:271-281` | the same quantity is 0.922 in the prereg; the inversion may not occur (A5.9) — B-20d |

### Docs that must change, not `.tex`

| doc | line | what is wrong | evidence |
|---|---|---|---|
| `docs/known-defects.md` | `:63-66` | "routing ECE … never measured. Do not report" — the six secured runs export 0.0367–0.3082 | A6.4 |
| `docs/arena-math-findings.md` | `:799-800` | "it should never have been in the 8-model arena roster either" — the pilot roster holds `Meta-Llama-3_1-70B-Instruct`, not the excluded `Meta-Llama-3-70B-Instruct` | A6.13, verified R7 |
| `docs/arena-math-findings.md` | `:386`, `:875-876` | still use the one-sided `√r` disattenuation the same file corrects at `:928-932` | A5.10 |
| `docs/prereg_arena_launch.md` | `:57-58` | attributes a "≤ 0.05 / ≥ 0.10" band to `prereg_rubric_specificity.md`, which has no such band; that doc records the misattribution at `:152-159` but the launch doc was never fixed. The **thesis handles this correctly** at `6_Results.tex:967-980` | prereg cross-read |
| `docs/void-results.md` | `:32-34` | lists `prereg_discriminative_power.md` as "Fully current" and its 0.922 as reproducing identically under both routers; `discriminative_flatness.py` returns 0.884 | A5.1, R3 |

## C.3 Two things a reviewer will ask for that do not exist

1. **A permutation null for A4.3.** The within-vs-between comparison (293 correlated leaf pairs
   against 91 domain pairs) has no null. Until it does, state it as descriptive.
2. **The options-blind arm.** Named as the decisive experiment for RQ1 at `6_Results.tex:714-722`,
   `7_Discussion.tex:37-41` and `8_Conclusion.tex:107-118`; blocked on a trace-complete roster.
   The corpus is now trace-complete for 37 of 47 models (`6_Results.tex:329-334`), so the stated
   blocker may have lifted. Worth re-checking before submission, because it is the one experiment
   that would convert the thesis's headline inference into a demonstration.

---

## A note on what this audit did *not* find

Worth recording, because absence of a problem is also evidence:

* **All twelve Δρ values and all twelve per-arm key-agreement values in `6_Results.tex:592-598`
  reproduce exactly** from the six databases (R1). The six-domain table is sound.
* **All three rubric-specificity p-values reproduce to the printed digits** (R6): 1.210e-6, 2.092e-6,
  7.618e-6. So do all four discriminators and both arm-size controls.
* **The law and Math screen rows reproduce exactly** (R4): n = 287, ρ = 0.955, p = 0.008 and
  n = 393, ρ = 1.000, p = 1.000.
* **The capture-gap numbers reproduce exactly** against the pre-backfill corpus (R7): 4 of 8 models,
  896/1736 mixed, 863/868 = 99.42%.
* **The three reversal pairs and their swings reproduce exactly** (A4.6).
* **The `arx` side-channel did not survive into any paired run** (R14) — the careful wording at
  `7_Discussion.tex:109-114` is correct.
* **No dangling `\ref`**: 140 labels, 395 references, 0 unresolved (R11).
* The six paired runs all cite the same snapshot, seed and roster in their manifests.

The thesis's problems are staleness and provenance, not fabrication. Every number this audit could
not reproduce (A7) is one the thesis has *already* flagged, withdrawn, or footnoted — with the two
exceptions at B-2 and B-3.

## The shortest path through this list

Nine edits move the thesis from "internally contradictory" to "defensible":

1. B-4, B-5, B-6, B-7 — one find-and-replace of the "two domains / results pending" sentence in
   Chapters 5, 7 and 8. Four sites, one fact.
2. B-1 — one clause in four places, turning a false absolute into a true one.
3. B-2, B-3 — replace or withdraw two unreproducible number sets in Chapter 6.
4. B-12 + B-13 — print the 14-row screen and separate "screen classification" from "registered
   prediction". This is the single biggest *gain* on the list.
5. B-15 — add the per-leaf-vs-domain bound, which is the qualifier that makes the rest credible.
6. B-20a — disclose that engineering's registration quotes a superseded p-value, before an examiner
   opens the prereg and finds it.

Everything else is strengthening or hygiene.

---

## Provenance of this audit

Every number above is either (a) recomputed in this session from the databases, CSVs and JSON
artifacts named in the R-table, or (b) quoted from a `docs/` file or `.tex` line with its citation.
Nothing is inferred, estimated, or carried over from memory. Where a figure could not be regenerated
it is marked as such rather than repeated. Where two sources disagree, both are cited and neither is
silently preferred.
