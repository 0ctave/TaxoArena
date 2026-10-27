# POSTRUN review: ROUTE-SOURCE-NULL, KNN-ROUTE, KEY-INFO-V2 (2026-10-04, adversarial reviewer, 0 calls)

Registrations: prog L24265-L24302 (_as_of 0e34eb56/2fc67857), brackets C1-C5 from READY_route_readouts.md (blob 54b99df4).
Outcomes (write-once, never committed, `git ls-files` count 0): route_source_null 2ae71b01..., knn_route 119ee310..., key_info_v2 bb365d2a....

## Verdict

| test | validity | deciding reading | condition |
|---|---|---|---|
| ROUTE-SOURCE-NULL | **VALID** | RS1 **UNDETERMINED**; F-RS NOT FIRED; rule 8: ABOVE-SOURCE REFUTED (D_S interval contains 0) | P1 NOT SCORED (C2), not "HELD" as the outcome prints |
| KNN-ROUTE | **VALID** | KN1 **UNDETERMINED** on D_N = +0.12pp [-1.16, +1.40]; F-KN NOT FIRED | the deciding number is D_N, not G_KNN-ALL +1.69pp (a descriptive [LF] floor) |
| KEY-INFO-V2 | **VALID** | KI2 **BEYOND-SOURCE** (robust); KI1 **K0-BETTER, with a qualifier**: half of D comes from AF-U's 191 cross-source filings (D-4); on the 5,716 own-source-filed items D reads NEITHER (descriptive) | qualifier R-KI1 owed on every quote of K0-BETTER |

Running at the same time as GRANULARITY-GT does **not affect validity**. All four are zero-call CPU readers. GRANULARITY-GT reads a different object (the MASSIVE intent tree, from the worktree intent-s1-run), and none of the four is a construction or a site null, so rule 7 is not engaged. Each run prints its view sha256 before and after as EQUAL to the pins. My recomputation also reproduces every deciding digit from an independent read of the views, which rules out any cross-talk.

## Per-claim table (deciding claims; mine vs outcome)

| # | claim | status | mine | outcome | sev |
|---|---|---|---|---|---|
| 1 | data object: TRAIN 12,351 → 11,841 kc; EVAL 6,153 → 5,907 kc / 5,404 comps; 18 models, Llama absent | CONFIRMED | 11841 / 5907 / 5404 / 18 | same | — |
| 2 | identity: best 0.6049, SRC 0.6150, AF 0.6201, K0 0.6271, decl 0.6316; C1 +2.675pp; G_AF +1.524pp [+0.138, +2.909] | CONFIRMED to the digit | same (two-stage reproduced with run_boot's seed-42 order) | same | — |
| 3 | RS1 D_S = +0.508pp, two-stage SE 0.599pp, [-0.666, +1.682]; DEFF 1.847, n_eff 3,198, MDE80 1.68pp | CONFIRMED to the digit | +0.00508, SE 0.00599, [-0.00666, +0.01682], DEFF 1.847, n_eff 3198, MDE 0.01677 | same | — |
| 4 | G_SRC +1.02pp [-0.20, +2.23]; G_decl − G_SRC +1.66pp [+0.71, +2.60] (descriptive) | CONFIRMED | +0.01016 [-0.00196, +0.02227]; +0.01659 [+0.00713, +0.02605] | same | — |
| 5 | RWS band (200 draws, seeds 20261004+r): p2.5 -0.80pp, median -0.12pp, p97.5 +0.49pp; G_AF ABOVE p97.5 | CONFIRMED to the digit | -0.00797 / -0.00119 / +0.00492; max +0.00660 | same | — |
| 6 | RWS profile = AF-U's per-source partition on the scored TRAIN items (183 blocks, including foreign-leaf blocks) instead of the registered "leaf count" (123) | PARTLY (deviation, not decisive) | own-leaf variant (36/4/1/10/69/3 blocks, largest remainder): p97.5 +0.643pp, max +0.863pp; G_AF still above the band; KI p97.5 0.1388 | not run | LOW |
| 7 | KN1 D_N = G_KNN-SC(50) − G_AF = +0.119pp; G_KNN-SC 25/50/100 = +1.422/+1.642/+1.591; KNN-ALL +1.422/+1.693/+1.676; backoff shares | CONFIRMED to the digit (points) | same, backoff 0.7279 (SC50) | same | — |
| 8 | KN1 interval [-1.161, +1.398], SE 0.653pp | UNDETERMINED by me (kNN refit bootstrap not re-run); spot check: i.i.d. SE 0.478pp vs 0.484pp printed; the verdict needs lo95 > 0 or hi95 < 0, and neither holds at any SE ≥ 0.07pp | — | — | — |
| 9 | KI points: AF 0.438381, K0..K4 0.470172/0.464005/0.469174/0.460022/0.452532, SRC 0.170501, decl 0.469521 | CONFIRMED to 1e-6 (own ki, independent of loo_imp) | same | same | — |
| 10 | KI1 D = -0.024800, spread_K 0.017640, interval [-0.04345, -0.00615] | CONFIRMED (point to the digit); own two-stage B 1000, seed 777: SE 0.00967, [-0.04375, -0.00585], DEFF 1.59, n_eff 3,714, MDE80 0.0271 (outcome: SE 0.00952, DEFF 1.468, MDE 0.0266) | | | — |
| 11 | KI2: KI(AF) 0.438 > RWS p97.5 0.123399 (min 0.0891, median 0.1101, max 0.1258) | CONFIRMED to the digit | same | same | — |
| 12 | C5: KI = 18 × loo_imp mean | CONFIRMED: my KI (weighted bincount, held-out branch) equals the printed values. The outcome's [KI-F6] line checks every arm and every RWS draw against loo_imp to 1e-9 | | | — |
| 13 | C1 duty: cross-source filings on the scored 5,907 | **191** EVAL items (MMLU_PRO 128, MATH 51, GPQA 12) + 311 scored TRAIN items; on the 191, acc AF 0.4450 vs SRC 0.4921 (against AF-U, as D-4 says) | 223 was the 6,139-bundle count | — | HIGH for KI1 (below) |
| 14 | Support re-derivation (registered arithmetic) | CONFIRMED arithmetic: 1.72/3.92 = 0.439; 2.8 × 0.44 = 1.23; 5907/2.867 = 2060; 0.5 − 1.645 × 0.44 = −0.22; 0.10/√3690 = 0.00165. REALISED: D_S SE 0.60 (1.36× registered); D_N SE 0.65; KI SE 0.0095 (**5.8×** the registered 0.0016, from an unsourced SD of 0.10, READY D5) | | | MEDIUM |
| 15 | pins: route_source_null 9fc280ef, knn_route ec5fbc41, key_info_v2 37f5935c, union_route_common d5473976, escalation_rc 8f99db7d, union_cells_io 92a04543, union_af_route bf3f17db, free_tests_f4_f7 f0749d61 | CONFIRMED: `git rev-parse HEAD:<f>` = the outcome's blob:, which is the LF hash (`git hash-object`) at 2fc67857 = the READY's reviewed blobs (L16-L22) | | | — |
| 16 | words [SC]/[LF] | CONFIRMED: AF-U / SRC / RWS / K_0 / KNN-SC are [SC]; KNN-ALL is the only [LF] arm, marked floor/cross; no split word (clean/disjoint/held-out count 0 in all three); no wrong(established) arises (key-scored) | | | — |

## C1: does any verdict depend on the cross-source filings? (sensitivity on the 5,716 own-source-filed items; unregistered, descriptive)
- RS1: D_S +0.682pp, approx two-stage [-0.52, +1.88] (i.i.d. × √1.847); G_AF +1.98pp, still above the RWS p97.5. **UNDETERMINED unchanged.**
- KN1: D_N −0.280pp; the interval contains 0 at SE ~0.65. **UNDETERMINED unchanged.**
- KI2: KI(AF) 0.4517 against p97.5 ~0.12. **BEYOND-SOURCE unchanged.**
- **KI1: D −0.01288 against a subset spread_K of 0.02175, so |D| < spread_K and the reading is NEITHER.** On the 191 items, KI(AF) is 0.0393 against a K mean of 0.4209. They contribute 191/5907 × (−0.382) = −0.0123 of the −0.0248. K0-BETTER is a true statement about AF-U **as built** (flatLeaf over every grafted leaf, D-4). It is not a statement about AF-U's partition against K_0's when both file by source. No falsifier fired, so the registered post-run duty (direction printed beside a fired falsifier) does not formally trigger, but the KI1 word needs the qualifier R-KI1.

## Defects and fixes
- **R-KI1 (HIGH, words):** append to KI1 wherever it is quoted: "K0-BETTER for AF-U as built; about half of D (−0.0123 of −0.0248) comes from the 191 EVAL items AF-U files into another source's leaf (D-4), which K_0 files by source. On the 5,716 own-source-filed items D = −0.0129 < spread_K 0.0218 (NEITHER; unregistered, descriptive)."
- **R-RS-P1 (MEDIUM, record):** the outcome prints RSN P1 G_SRC / D_S "HELD"; per C2 the registrar records **P1 NOT SCORED** (seen data). P2's Brier (0.5850) is recorded with its C2 disclosure.
- **R-KN-HEAD (LOW, words):** the headline "KN1 UNDETERMINED (G_KNN-ALL +1.69pp)" pairs the verdict with a descriptive floor. The deciding number of record is D_N +0.12pp [-1.16, +1.40] (SE 0.65pp, DEFF 1.82, n_eff 3,253, MDE80 1.83pp).
- **R-KN-TS (LOW, words):** the [TS] "ceiling" reads −28.1pp below declared (P3 FAILED). It is not a ceiling at this filing (EVAL filed by embedding neighbours to correctness-pattern cells), so quote it as "the correctness-pattern arm (registered as a ceiling; it is not one here)".
- **R-RWS (LOW, disclosure):** the RWS profile uses AF-U's induced per-source partition (183 blocks) instead of the registered leaf count (123). The own-leaf variant leaves RS1 and KI2 unchanged (row 6). Disclose it beside the band.
- **R-SUP (MEDIUM, support):** the KI Support (d) SE was 5.8× too small, and RSN/KNN Support (a) calls the plain mean (1.093) "Kish". The Kish sum n²/sum n is 1.311, as the outcomes print. KI1 still decides at the realised SE. Record the realised SE / DEFF / n_eff / MDE beside each deciding statistic (rows 3, 10 and R-KN-HEAD).
- **R-ABS (note):** ABOVE-SOURCE is unreachable at the realised SE of D_S (it needs D_S ≥ 1.17pp). This is consistent with C2.

## Process notes
- Brief headline "D_S +0.51pp": CONFIRMED. "KI1 K0-BETTER": CONFIRMED with R-KI1. "KI2 BEYOND-SOURCE": CONFIRMED.
- Java during my checks: at the first check, four java.exe were present and then exited. Later a Gradle daemon (PID 68508, started 16:45, another agent's) appeared. I waited and did not kill it. My checks are deterministic read-only Python, and they reproduce every digit with the view sha equal before and after, so the daemon has no effect on them. Python peers running at the same time: granularity_gt --run (PID 64700) and tree_like --mutants (another agent's), both CPU-only.
- No mutants. This is a post-run numbers review, and the deciding paths were re-implemented independently. The decisive mutants of READY_route_readouts.md stand.
- Backup: E:/TaxoArena_backup_2026-10-04_route_trio (3 outcome dirs: outcome.txt + READ_STARTED markers, plus the 3 run logs). SHA256SUMS.txt has 9 files, `sha256sum -c` gives 9 OK, and the 6 originals in the repo give 6 OK against it.

## Commands (scratch E:/TaxoArena_tmp/rev_route_trio; views opened `mode=ro&immutable=1`, sha256 before = after = the pins)
```
python load.py        # own SQL read: side JOIN item, model_registry ACTIVE, response(_lite) is_correct / is_correct_mathfix overlay,
                      # UNUSABLE_CELL (single-row cells only), key-complete -> 11841 / 5907; af/k cells; bundle 256-d vectors
python rs.py 2000     # arms, identity, D_S / G_SRC / C1 / G_decl-G_SRC two-stage (run_boot order, seed 42), DEFF, cross-source 191/311
python rws_ki.py 1000 # KI arms, KI1 D / spread, RWS 200 draws (run's profile and own-leaf variant), KI1 two-stage (seed 777)
python knn.py         # kNN SC/ALL k 25/50/100 points, D_N, D_N without the 191
python ki_x.py; python rs_x.py   # KI1 / RS1 on the 5,716 own-source-filed items
git rev-parse HEAD:tools/analysis/<f>.py ; git hash-object <f> ; tr -d '\r' < <f> | git hash-object --stdin   # pins (all equal)
grep -ciE '\bclean\b|disjoint|held-out' <outcome>   # 0 x3
sha256sum -c SHA256SUMS.txt | grep -c OK            # 9
```
