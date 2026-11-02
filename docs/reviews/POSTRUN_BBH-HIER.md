# POSTRUN review: BBH-HIER (test 3: BBH known-hierarchy recovery; exploratory, WORK items, text only)

Authority: D-2026-11-02-1 (`docs/agents/author_decisions/2026-11-02.md`, 9dff0985; the main session's reading: tests 1
and 3 as exploratory WORK-row readouts, zero LLM calls, no reserved/vault side, CPU only). Reviewer: adversarial
reviewer, 2026-11-02. Zero LLM calls by me; responses read by me 0; RESERVED rows read by me 0 (my loader reads the 3,457
WORK ids only). At most 3 worker processes, BLAS 1. Outputs and benchzoom read-only (fits.pkl opened after a pickletools
scan: numpy globals only); my scripts and mutant sandboxes in the session scratchpad and `E:/TaxoArena_tmp/bbh-hier-rv`.
Reviewed: benchzoom branch `bbh-hier` (local, no remote), fb39598..c764409: 3 new files (`docs/bbh-hier.md`,
`examples/bbh-hier.py`, `tests/test_bbh_hier.py`), 0 files under `src/` (`git diff --name-only fb39598..c764409 | grep -c
'^src/'` = 0, of 3), so `docs/execution_graph.md` owes nothing; master fb39598 is an ancestor (fast-forward).
- Pins (LF, `git hash-object` = `git rev-parse c764409:<path>`, 0 CR bytes in each working file): plan `blob:550a0914`
  (sha256-lf16:b744ff6784d8ec10), runner `blob:b6be8cfd` (sha256-lf16:d0cf213e023cbfec), tests `blob:09aaba83`
  (sha256-lf16:ecf675a4c6e3fc60). Run of record: runner `blob:a7c41bb7` at a1786c0 (fit and analyze, `dirty ""`, meta.json);
  the tip runner is AST-identical to a7c41bb7 outside the module docstring (`ast.dump` equal; +120/-1 docstring lines).
- Outputs: `sha256sum -c` 5/5 (summary 143cdc68, readouts 6c04fd37, meta 1927179e, fits.pkl 2dce8e37, fits.txt);
  backup `E:/TaxoArena_backup_2026-11-02_bbh-hier` 8/8, SHA256SUMS.backup sha256 d82e5081 as claimed.

## Verdict

- **BBH-HIER: OUTCOME CONFIRMED (exploratory, BBH WORK items, text only, qwen3 512-d), with qualifiers Q1, Q2 (MEDIUM)
  and Q3-Q6, T-1 (LOW).** Every deciding number reproduces to the printed digit from my own code; every word follows its
  pre-specified rule; 11 of 14 predictions held (PH7, PH8, PH12 FAILED), mean Brier 0.1189.
- **merge_ok: YES (MERGEABLE)**, fast-forward, 3 new files, 0 `src/`; the corrections below go into [P3] (insertion only).
- No BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table (deciding claims; WORK items; denominators named)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 2257e61 committed before any fit or statistic | 2257e61 14:37:25; a1786c0 15:04:33 (runner only: PLAN_COMMIT, a no-op `seed_values` refactor, selftest); fits.pkl 15:13:03 (fit 489 s), files of record 15:48:39; 0 fits.pkl > 1 MB under `E:/TaxoArena_tmp/bbh-hier` (fixture pickles only); plan edits after 2257e61: `--numstat` 94 / 0 ([P2], insertion only) | CONFIRMED | - |
| 2 | Data object: 3,457 WORK; G1 20, G2 24; 900 family items; VAR 3, SCN 10, G3 30; clusters 2,662, Kish 4.416, n_eff 783; family 360 clusters, Kish 13.0, n_eff 69 | own loader (census items.csv + KEPT part, text sha 0 mismatches; WORK ids sha = fits `ids_sha`), own scenario keywords (exactly one hit per item; LD 94/85/87/90/94, TSO 91/92/85/92/90), own union-find: 2,662, Kish 4.416, n_eff 783; family 360, Kish 12.996 | CONFIRMED | - |
| 3 | New fits read WORK rows only | refits from the 3,457 rows' 512-d prefix alone identical: FLAT k18 s0, k96 s2, k20 s4; FLATA k15 s1 (both families); BKM s3 by my own bisection (same leaf partition); every saved hierarchy has 3,457 item rows | CONFIRMED | - |
| 4 | Best-cut AMI G1 / G2 (16 values; table) | sklearn AMI over my own depth + split-order cuts: all 16 equal to 4 dp (e.g. AF 0.9305 / 0.8855, BKM 0.9605 / 0.9147, KAL 1.0000 / 0.9517, KWD 0.9837 / 0.9363, FLAT 0.9736 / 0.9265); variant-blind ceiling 0.9517 | CONFIRMED | - |
| 5 | LEVEL words (G1 RECOVERS for AF, BKM, KAL, KWD; G2 RECOVERS for every non-V0) | re-derived from row 4 and the bars; no value within 0.03 of a bar | CONFIRMED (Q6) | LOW |
| 6 | DP / HF ABOVE-RANDOM wherever not anchored (G1, G2) | own DP by leaf-pair enumeration (a different algorithm) and own HF: all 14 equal to 4 dp; own null (200 matched-shape draws, my stream) p97.5 within 0.014 of theirs; closest AF G2 DP 0.7341 vs 0.7141, HF 0.7928 vs 0.7833 | CONFIRMED (Q5) | LOW |
| 7 | "No node is a variant": HF vs VAR 0.500 in both families for every non-V0 hierarchy | own brute-force HF over every node: 0.5000 / 0.5000 for V0m, AF, BKM, BKMA, KAL, KWD (the family node: 2 x 150 / 600); V0 1.000 | CONFIRMED | - |
| 8 | SEPARATION: IN NEITHER for V0m, AF, BKM, KAL, KWD; BKMA IN ONE (TSO 0.5031 at depth 6; LD 0.4936) | seed-mean curves equal to 3-4 dp; BKMA depth 6 per seed: LD 27/27/28/27/27 cells, cAMI 0.4904-0.4946; TSO 26 cells x 5, 0.5027-0.5038; homogeneity 1.000 in all 10 seed x family cells; an equal pure refinement of 3 classes scores ln 3 / ((ln 3 + ln K) / 2) = 0.5043 / 0.5000 / 0.4959 at K 26 / 27 / 28 | CONFIRMED (word) / Q1 | MEDIUM |
| 9 | Contrasts D1-D4 (G1, G2): D, per seed, MC | D and per-seed values equal to 4 dp; MC equal (0.0021-0.0044) | CONFIRMED | - |
| 10 | Contrast SEs and words: D1 BKM, D2 KWD, D3 KAL, D4 FLAT HIGHER (G1, G2) | own replication on the run's stream ([20261102, 7, b], B 200): every boot SD, SE, normal and percentile interval equal to 4 dp (D1 G1 0.0044 / 0.0050 / [+0.0202, +0.0399] / [+0.0214, +0.0379]; D4 G2 0.0030 / 0.0051 / [+0.0019, +0.0218] / [+0.0032, +0.0153]); level boot SDs equal (AF 0.0049 / 0.0089, BKM 0.0020 / 0.0064, ...); z D1 +5.97 / +5.90, D2 -4.76 / -4.38, D3 -6.17 / -6.16, D4 +2.67 / +2.33; n 3,457, Kish 4.416 (re-measured), n_eff 783, realised MDE80 0.0070-0.0142 vs planned 0.05-0.07 (plan's SE source GRANULARITY-GT x sqrt(4,946 / 783) = 2.51 reproduces) | CONFIRMED | - |
| 11 | D4 reading "flat k-means at its best k beats BKM by 0.013" | per-seed FLAT AMI vs k is jagged (independent fits): the best k exceeds the median of its 6 neighbouring k by 0.022-0.057 (G1) and 0.020-0.046 (G2) in every seed, larger than D4; at matched k BKM >= FLAT (k 20: 0.953 vs 0.936 G1; k 24: 0.946 vs 0.942) | PARTLY (Q2) | MEDIUM |
| 12 | D5 / D6 +0.4983 (SE 0.0327) BKMA HIGHER; post hoc (c) "max-over-depth cAMI biased low under resampling" | D +0.4983, per seed, MC 0.0003, SD 0.0327, pct [+0.3601, +0.4851] equal; n 900, 360 clusters, Kish 12.996, n_eff 69, MDE80 0.092; BUT the draws' means: V0m / BKM side 0.1055 (point 0.0000), BKMA 0.5318 (point 0.4983), so each side is biased UP and D's draws centre at 0.4263 | CONFIRMED (word, D/SE 15.2) / REFUTED (the mechanism of (c)) | LOW |
| 13 | Predictions 11 / 14, Brier 0.1189 | re-scored from the re-derived words: same 11, Brier 1.665 / 14 = 0.1189 | CONFIRMED | - |
| 14 | Reproduction vs BBH-WORK / FLAT-COMPARE | V0m's family leaves are the scenarios (SCN 1.000 at depth 4, both families; cAMI vs VAR -0.001 / -0.002 vs BBH-WORK -0.0024 on all 750); FLATA k 15 0.531 / 0.546 on 450 WORK items vs BBH-WORK's k 15 0.574 on 750 (same regime: near the 0.577 product); FLAT-COMPARE's `spherical_kmeans` used unchanged (row 3) | CONFIRMED | - |
| 15 | 0 LLM calls; responses read 0 | Ollama `server.log`: last request line `[GIN] 2026/10/30 03:16:10`, 0 lines dated 2026/11/02 (log written 12:47 today, non-request lines only); runner: no network path (cached npz, a missing text refuses), no response reader imported or called (`load_items` reads the item columns, `score` refused) | CONFIRMED | - |
| 16 | No vault / RESERVED row anywhere | no new fit or statistic touches a RESERVED row (rows 2-3); BUT the plan's pre-plan scenario counts were taken on all 1,500 family items' text (165+156+147+142+140 = 750 per family), and `real_source` loads all 5,761 texts and vectors into memory before restricting | PARTLY (Q4) | LOW |
| 17 | Tests and mutants: selftest PASS, 4 targeted tests, suite 1,022 passed / 1 skipped / 0 failed, 90/90 mutants | `tests/test_bbh_hier.py` 4 passed (15.4 s, selftest included; worktree clean after, `git status --short` 0 lines); full suite 1,022 passed, 1 skipped, 12 deselected (slow / network), 0 failed (937 s, PYTHONPATH=src, BLAS 1); own mutants 6 / 8 killed (table below), survivors R3, R5 are selftest gaps, not run defects (rows 9, 12 reproduce the run's D4 per-seed values and D5 / D6 SD by independent code); the builder's 90-mutant table not re-run (a full first review runs its own) | CONFIRMED (T-1 LOW) | LOW |

## Qualifiers and corrections (each with its fix)

- **Q1 (MEDIUM, word validity).** The SEPARATION bar is granularity-limited: a PURE variant refinement scores below 0.5
  once it has more than 27 equal cells. BKMA's depth-6 cut is pure in the variant in BOTH families (10 / 10); IN ONE
  (TSO) versus not-LD is decided by 26 versus 27-28 cells, not by separation. The pre-specified word stands (IN ONE;
  PH7 FAILED); fix: every quote of it carries "both families' depth-6 cuts are pure in the variant (homogeneity 1.000);
  the family difference is the cell count (26 vs 27-28), not separation", and "ANY HIERARCHY SEPARATES 3/5/7 IN BOTH:
  NO" is quoted with it. The robust 3/5/7 finding is row 7 (no node is a variant) plus BKMA G3 0.988 (scenario x variant
  product beneath the scenario), not the depth word.
- **Q2 (MEDIUM, what D4 licenses).** FLAT's best cut is a maximum over 95 independently seeded fits; the bootstrap holds
  fits fixed and the MC term measures the seed spread of that maximum, not its upward bias (the winner's curse over fit
  noise, 0.02-0.06 per seed, row 11). D4 FLAT HIGHER (and PH11 HELD) stands as the pre-specified word; fix: quote it as
  "FLAT's best single fit among 95 k beats BKM's best nested cut", never as "flat partitions beat nested ones at matched
  granularity" nor as support for TREE-CUT-GRANULARITY's direction; at matched k 20 / 24 BKM is at or above FLAT (post
  hoc (b) already says the matched-k half).
- **Q3 (LOW, post hoc (c) mechanism).** (c) says the max-over-depth cAMI is "biased low under resampling with copies".
  It is biased HIGH on both sides (V0m / BKM 0.0000 -> 0.1055, BKMA 0.4983 -> 0.5318 over the 200 draws): resampling
  the family's large content clusters (up to 35 items) plants scenario-variant association and unequal cell sizes; the
  baseline, floored at 0 by its one-cell depth-1 cut, gains more, so D's draws sit low. The percentile interval is not
  an interval for D here and the SD comes from a shifted distribution; the word is unaffected (D / SE 15). Fix: [P3]
  replaces (c)'s mechanism with these numbers.
- **T-1 (LOW, selftest gaps).** R3 (the within-family bootstrap ignores the weights: D5 / D6 SE collapses to the MC term)
  and R5 (FLAT dropped from SEEDED: D4 reads FLAT seed 0 against every BKM seed) survive the committed selftest. Fix
  before the runner is reused: an S8 check of the D5 bootstrap SD against an expanded-copies recomputation, and a
  `seed_values` check on FLAT with seeds that differ.
- **Q4 (LOW, disclosure).** The plan's scenario counts read RESERVED items' TEXT (no response; consistent with BBH-WORK's
  L3 convention that the trees read all 5,761 texts; D-2026-10-20-4 is the meter's reserved side, untouched). Fix: [P3]
  states it beside "RESERVED rows read 0 by any new fit or statistic".
- **Q5 (LOW, wording).** Reading (1) "above every random arrangement" -> "above the p97.5 of 200 matched-shape random
  trees" (the null is 200 draws, not every arrangement).
- **Q6 (LOW, vacuity, disclosed in the plan).** G2 RECOVERS is reached by variant-blind partitions (V0m, BKMA, KAL exactly
  at the 0.9517 ceiling); never quote "recovers the subtasks". The hand-back's "every hierarchy recovers the family level"
  should read "every anchor-free hierarchy (AF, BKM, KAL, KWD); V0 / V0m / BKMA have it by construction".

## What the result licenses (exploratory, WORK items, text only, one embedder)

Licensed: on BBH's 3,457 WORK texts (qwen3, 512-d prefix), every anchor-free hierarchy tried recovers the 20 families at
some cut (AMI 0.93-1.00) and places them at the node level above matched-shape random trees; no hierarchy other than the
subtask-anchored V0 has a node that is a variant; the text orders the merged families family -> scenario -> variant
(the gold's family -> variant -> scenario is not recovered as a level; the variant appears only as a refinement beneath
the scenario, BKMA G3 0.988); among anchor-free hierarchies at their best cut KAL > KWD > BKM > AF (D1-D3, also at
matched k 20). Not licensed: any statement about models or responses (text only; BBH-WORK's meter is the response-side
evidence); any family difference in 3/5/7 separation (Q1); "flat beats nested" (Q2); "recovers the subtasks" (Q6); any
claim on RESERVED or fresh items, other embedders, or other corpora (the TaxoAdapt generalisation is untested); nothing
replaces V0, and V0 / V0m numbers carry their all-5,761-texts fit.

## Own mutants (sandbox copies of the tip runner; `--selftest`; one at a time)

| id | change (one string replacement in a copy) | result | decisive |
|---|---|---|---|
| R0 | control | passes | - |
| R1 | IN ONE names MERGED[0], not the separating family | killed (S6 overall) | yes (BKMA's word names the family) |
| R2 | contrast: negative branch names A | killed (S6 contrast word) | yes (D2, D3 words) |
| R3 | within-family bootstrap unweighted | SURVIVED | no on this run (row 12 reproduces SD 0.0327 independently) |
| R4 | sep_word BY CONSTRUCTION when anchored at G1 | killed (S7 planted: V0m IN NEITHER) | yes (V0m, BKMA words) |
| R5 | FLAT not in SEEDED | SURVIVED | no on this run (row 9 reproduces D4 per seed independently) |
| R6 | separation null p95 = seed mean, not max | killed (S5 mean curve) | no (the 0.5 bar binds) |
| R7 | D5 / D6 statistic: max over the families | killed (S8 D5 point) | yes (D5 / D6 value) |
| R8 | bootstrap draws half the clusters | killed (S6 bootstrap weights) | yes (every SE) |

## Commands (scripts in the session scratchpad; all read-only)

```
rv_common.py   own loaders: census items.csv + KEPT part (text sha checked), work_ids.txt, own gold (keywords), own Hier/cuts
rv_point.py    -> rows 2, 4, 5, 7-9, 11, 13, 14 (sklearn AMI / homogeneity; BKMA depth-6 per seed; refinement arithmetic)
rv_nodes.py    -> rows 6, 7 (leaf-pair DP, HF, own null 200 draws, stream 987654; brute-force HF vs VAR)
rv_refit.py    -> row 3 (FLAT / FLATA / BKM refits from WORK rows, flat-compare.spherical_kmeans, the run's streams)
rv_boot.py 200 2 -> rows 10, 12 (stream default_rng([20261102, 7, b]); own union-find clusters, canonical = min row; weighted
               AMI by np.repeat; best cut over cuts within 0.04 of the point max, 0 mismatches vs the full family on 4 draws)
rv_mutants.py  -> row 17 (copies under E:/TaxoArena_tmp/bbh-hier-rv, TMP/TEMP/TMPDIR/BZ_SANDBOX redirected, no deletion)
git diff --numstat 2257e61 c764409 -- docs/bbh-hier.md; git diff --name-only fb39598..c764409 | grep -c '^src/'
git merge-base --is-ancestor master c764409; sha256sum -c SHA256SUMS (outputs 5/5; backup SHA256SUMS.backup 8/8)
grep -a '\[GIN\]' %LOCALAPPDATA%/Ollama/server.log | tail -1; grep -a -c '2026/11/02' server*.log  (0 in each)
```
