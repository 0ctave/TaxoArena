# POSTRUN review: TAU-CONT-ALL (FLAT-COMPARE re-read with every tau^2 chosen continuously; EXPLORATORY, WORK rows only)

Authority: D-2026-10-27-2 (TaxoArena 2e2513a5, `docs/agents/author_decisions/2026-10-27.md`, incl. the main session's
reading). Reviewer: adversarial reviewer, 2026-10-27. Zero LLM calls. My loads read no vault or reserved response (guard
reads MATH [0], MMLU [0, 0], at start and at end). At most 3 heavy processes, BLAS 1; two read-only helper scripts of a
few seconds each overlapped a 3-process run.
Reviewed: benchzoom branch `tau-cont-all` (local; no remote), 35b2724..7f87477. 35b2724 is master's tip, so the merge is
a fast-forward.
- Plan 3803853 (committer 15:39:37); runner + tests 1be267a (18:46:43).
  - Run of record: runner `blob:15c4e95fdda66c77fea4fc4275d232d331eac9c5` (LF; sha256-lf16:7d8aa62fda2e4acd). All 3
    parts and meta carry head 1be267a and `dirty ""`.
  - Tip 7f87477: runner `blob:c5ace4e1` (sha256-lf16:0fd90be2db8e603a), plan `blob:e38b8435` (decd7a1cefe49910), test
    `blob:b3387811` (04eb8853dff8b91b). The three working-tree files have 0 CR bytes, so there is no CRLF rendering.
- Outputs `E:/benchzoom_demo/followups/tau-cont-all`: summary.txt sha256 020f0ad97b606535, SHA256SUMS c5ee2b4ce39884da;
  `sha256sum -c` 9/9. Backup `E:/TaxoArena_backup_2026-10-27_tau-cont-all`: 9/9 and 14/14; both SHA256SUMS files
  `cmp`-identical to the originals.

## Verdict

**OUTCOME CONFIRMED (exploratory).**
- **Rule words after review:** ORDERING STANDS; PM FAILED, PU FAILED, PP HELD; CAUSE 2 NOT SUPPORTED (UNDERPOWERED).
- **Branch MERGEABLE (merge_ok).** No BLOCKER. Two record conditions (C1, C2), one record relay (C3), four LOW items.

**Recomputation.** I recomputed every deciding number, two ways.
- From the parts npz, with my own SE code: each rule-O leg, each prediction change and the cause-2 difference. All
  equal the json: 0 difference in g, at most 7e-18 in SE.
- From library primitives, with my own harness: own fold loop, S-TAU criterion, 2-d sums, g4 grid, golden section and
  strict-improvement rule. The runner supplies only the data object.
  - MATH, all 25 tasks: 800 / 800 per-task taus bit-equal; all 32 per-item arrays equal (max|diff| 0).
  - MMLU, fold seed 0: 160 / 160 taus bit-equal; every per-fold-seed pooled value equal (4.4e-16).

**Process checks.**
- My own comparisons reproduce: 60 + 60 + 60 FLAT-COMPARE arrays, 3 TAU-GRID arrays and 1 FRESH-RULES array, all at
  max|diff| 0; each comparator sha equals its SHA256SUMS entry. The plan preceded every statistic. No src change; the
  branch touches only its 3 new files.
- The words follow the plan's rules, and each rule had a reachable second arm (rule O: the MMLU V0 - N knife edge,
  0.025 z from the bar, named in plan section 7; C2: SUPPORTED needs D2 >= 0.076).

**In substance.**
- With every tau^2 chosen continuously on its own S-TAU criterion, no task hit the bound. The golden-section step was
  taken in every task whose tau^2 is not 0.
- The grid moves C1(V0) by +0.0068 on MATH and -0.0101 on MMLU. On MMLU that is the tau_L2 move (l2c -0.0104), and it
  is 23% of the f2 value.
- The flat-vs-tree ordering does not depend on the grid. No sign changes, and no leg moves by more than 0.67 of its
  SE. The 3-SE statuses do depend on the clustering (C1).
- Cause 2 stays open: D2 +0.0170 (0.0382). Power at the full scenario D2* is 0.78, just below the 0.80 that the
  UNDERPOWERED tag uses.

## Per-claim table (deciding claims; x 1e-3 nats per cell; WORK rows only)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 3803853 before any statistic; [P1] and the post-run runner edit insertion-only | D-2026-10-27-2 15:25:28; plan 15:39:37; runner 18:46:43; parts MATH 19:19:46, MMLU-Pro 19:38:15, MMLU 21:20:15; analyze 21:20:40; 7f87477 21:23:29. numstat plan 61/0, runner 8/0 (hunk L41-48, inside the docstring that closes at L162). Files older than 15:39:37 in the output dir and in `E:/TaxoArena_tmp/tau-cont-all` outside `mut*`: 225, all mtime-preserving src copies under `pytest/bt*/.../benchzoom/`; any other file: 0 (`find ! -newermt \| grep -v -c /pytest/`) | CONFIRMED | - |
| 2 | STEM map fixed before any statistic | Plan (15:39) lists 6 subcategories / 18 subjects. `mmlu_confirm_items.py` last changed f44c4e0 (2026-10-22). `group_of` over its GROUPS gives the same 18 subjects (count) and 17 anchors. n_S 1,810 / 8,425 = 0.2148 | CONFIRMED | LOW (L1) |
| 3 | RF / RT / RN REPRODUCED (per item 0.0) | Own script. Comparator npz sha256 = their SHA256SUMS (3 + 3 + 1); clusters equal. f2 vs FLAT-COMPARE: 60 arrays, max\|diff\| 0 on all three datasets. l2c C1(V0) vs TAU-GRID `cont__1__C1`: 0 (MATH +0.1091, MMLU +0.0331, MMLU-Pro -0.0078). f2 C1(N512) vs FRESH-RULES: 0, +0.2771 (0.0514) | CONFIRMED | - |
| 4 | cont uses the same criterion as the factor-2 grid | Code: `TG.Criterion` sums `meter._loss_sum` over the scored rows of `ctxs[1:]` in context order, which is `meter.step` / `gw.step2d`'s loss vector. In each of the 75 tasks the run asserts that the f2 choices and outputs for L1, L2, diff, V0\|C1 and N\|C1 equal the library's bit for bit. g4 contains g2 (same floats), so crit(cont) <= crit(f2) by construction. Own harness, MATH (25 tasks x 32 readers: the chain, V0, KM0-4, RND0-4 and N on C1, f2 and cont): 800 / 800 taus bit-equal. In 75 dense scans (cont L2, V0\|C1, N\|C1; 61-point log grid + 0), crit(cont) is below every grid point (max -2.8e-6 nats) and below crit(f2) by >= 0.0030 nats. MMLU fold seed 0 (5 tasks x 32 readers): 160 / 160 taus bit-equal; per-fold-seed pooled values of all 32 keys equal the run's fold series (max\|diff\| 4.4e-16). In 15 dense scans crit(cont) is below every grid point (max -4.6e-8) and below crit(f2) by >= 0.023 nats | CONFIRMED | - |
| 5 | Rule O: ORDERING STANDS | Own SE code from the npz (pandas cluster sums, G/(G-1), MC over 5 seeds). z f2 -> cont: MATH V0-K -4.612 -> -4.067, V0-N -4.442 -> -4.795, V0-random +3.630 -> +3.755; MMLU -0.582 -> -0.458, -2.975 -> -2.875, +2.443 -> +2.218. Signs and statuses keep: STANDS. Every g and SE equals the json (0 / 7e-18). Leg changes cont - f2 (paired SE): MATH +0.0112 (0.0042), -0.0025 (0.0059), +0.0067 (0.0023); MMLU +0.0028 (0.0028), +0.0031 (0.0035), -0.0102 (0.0033), i.e. at most 0.30 (MATH) / 0.67 (MMLU) of a leg SE. Own harness, MATH: legs recomputed from my own per-item arrays are identical | CONFIRMED | MEDIUM (C1) |
| 6 | PM FAILED, PU FAILED, PP HELD | d = C1_cont(V0) - C1_f2(V0): MATH +0.006776 (0.002255), MMLU -0.010144 (0.003291), MMLU-Pro -0.005121 (0.003519). MDE80 0.0063 / 0.0092 / 0.0099. The words follow the closed bounds. Distance to the band edge: PM 0.79 SE outside, PU 0.56 SE short. Own harness, MATH: +0.006776 (0.002255) | CONFIRMED | MEDIUM (C2) |
| 7 | CAUSE 2 NOT SUPPORTED (UNDERPOWERED) | G_S +0.0468, G_N +0.0297, D2 +0.0170 (SE 0.0382, z 0.45). D2* = (0.116101 - 0.033384) / (1 - 0.214837) = 0.1053. MDE80 = 2.8416 x 0.0382 = 0.1086 > D2*, so UNDERPOWERED. Power at D2* = Phi(0.756) = 0.78: a near-boundary tag. sh_S - w_S = 0.0860 = w_S (1 - w_S) D2 / G_all. Own: the run's per-item C1(V0) with the STEM mask from my own MMLU load (17 anchors; STEM = biology, chemistry, computer science, engineering, math, physics = GROUPS["STEM"]) gives D2 +0.017027 (0.038218) and sh_S 0.300868, equal to the json. Descriptive: SE 0.0622 clustered by anchor (17 clusters), 0.0577 by V0 leaf. Under f2, D2 is +0.0004 (0.0446), so the grid alone moves D2 by +0.0166 (0.43 SE) | CONFIRMED | LOW (L4) |
| 8 | No src change; only its own files; execution_graph not owed; no writes outside the outputs | `git diff --name-only 35b2724..7f87477 -- src docs/execution_graph.md \| wc -l` = 0. Files outside the 3 new ones: 0 (count). Master tip = merge base. The runner writes only write-once parts, the files of record and the selftest sandbox (grep). `find /e/benchzoom_cache -newermt '2026-10-27 18:46' \| wc -l` = 0 | CONFIRMED | - |
| 9 | Selftest 23/23, mutants 97/97, suite 902 with 2 env failures | Full selftest with the 2-worker pool: rc 0, 23 / 23 PASS (count of `^SELFTEST .*: PASS$`), 0 FAIL. `PYTHONPATH=src pytest` on test_tau_cont_all, test_tau_grid, test_reread_steps and test_execution_graph_sync: 44 passed, 1 deselected (the slow selftest, run directly). The two "env failures" pass with PYTHONPATH=src. I did not re-run the full 902-test suite (the branch adds 3 files and no src). Builder mutant table: 97 killed + 2 controls (count). Own mutants R1-R5 (below): 5 / 5 killed; control R0 rc 0 with 22 / 22 PASS (pool check skipped). Worktree porcelain: 0 lines before and after | CONFIRMED | - |
| 10 | Support: DEFF 0.999-1.007, n_eff 2,944-8,428 | Reproduces from content clusters. But content clusters hold at most 2 items (2,946 clusters / 2,949 items; 8,375 / 8,425), so this DEFF is about 1 by construction. Re-measured by V0 leaf (36 / 100 clusters; sizes 45-138 / 46-163): DEFF on the MATH legs 1.89 / 1.48 / 3.22 (f2) and 1.95 / 1.55 / 3.34 (cont), n_eff 883-1,998; MMLU 1.13-2.63, n_eff 3,208-7,445. 3-SE MDE80 under the leaf SE (cont): MATH 0.199 / 0.243 / 0.227, MMLU 0.051 / 0.108 / 0.088 | PARTLY | MEDIUM (C1) |
| 11 | Descriptive: dims, K2 on MMLU under cont, decomposition | K4096 - K, MATH: -0.0591 (0.0243) f2 / -0.0580 (0.0254) cont. N - N512, MATH: +0.0729 (0.0321) / +0.0574 (0.0297). MMLU and MMLU-Pro: all \|z\| <= 1.0. Equal to [P1] (spot check). l2c - f2 on MMLU -0.0104, against cont - f2 -0.0101 | CONFIRMED (spot) | LOW (L2) |

Own mutants (sandbox copies under `E:/TaxoArena_tmp/tau-cont-all-review/mut/`, TMP/TEMP/TMPDIR/BZ_SANDBOX redirected,
`BZ_MUTANT_NO_POOL=1`; killed = rc != 0 plus a `^SELFTEST .*: FAIL$` line. My runner's label "killed" for R0 is wrong,
caused by fixture lines containing "FAILED"; R0 has rc 0 and no FAIL line):
- R1, cont searches the g2 bracket instead of g4 (`select_cont(crit, fine=GRID_F2)`): killed (S1, S3). Decisive: it
  defines the regime.
- R2, the cont C1 arms read the f2 controls (cross-regime parent): killed (S4). Decisive: every cont C1 arm.
- R3, the anchor -> group map built in sorted order (misaligned with the cat codes): killed (S6, S7, S8). Decisive: the
  C2 mask.
- R4, rule O compares f2 with f2 (vacuous STANDS): killed (S6). Decisive: the word.
- R5, the rule-O leg V0 - N reads V0 - N512: killed (S6). Not decisive on the run (V0 - N512 also keeps).

## What it licenses / does not

- **Licenses** (exploratory; WORK-side selection):
  - FLAT-COMPARE's V0 vs K / N / random signs, and the arms' C1 rank order on MATH and MMLU, are not products of
    S-TAU's factor-2 grid.
  - The grid moves C1(V0) by +0.0068 on MATH and -0.0101 on MMLU (all of it tau_L2's move).
  - MMLU-gap cause 2 is not settled at this power.
  - It supplies the WORK cont readout that the FRESH draft's D note lists as missing (C3).
- **Does NOT license:** switching `meter.TAU_GRID` / S-TAU or any deciding estimator (the author's; D-2026-10-27-5 (D)
  fixes the continuous fit for the FRESH test only); replacing V0 or any arm for BZ-AXIS-CONFIRM-FRESH; any statement
  about fresh data, the vault or a reserved side; any registered or confirmatory word; reading the 3-SE statuses as
  robust to the clustering (C1); reading PM / PU FAILED as evidence against the predicted magnitudes (C2).

## Defects and conditions

- **C1 (record condition; MEDIUM): the 3-SE statuses depend on the SE convention; the signs do not.**
  - Rule O is pre-specified on content clusters (FLAT-COMPARE's convention; already flagged in POSTRUN_FLAT-COMPARE
    81a99d9b D2). Those clusters hold at most 2 items, so the printed Support (DEFF 0.999-1.007) is item-iid by
    construction.
  - Re-measured by V0 leaf, DEFF is 1.5-3.3 on the MATH legs.
  - Under that clustering the same arithmetic reads ORDERING CHANGES: MATH V0 - K goes -3.41 -> -2.98 (class
    "marginal"). MATH V0 - random is within 3 SE in both regimes (+2.02 / +2.06).
  - The word stands, because the plan pre-specified content clusters.
  - What the clustering cannot move is the size of the grid's effect: no leg changes by more than 0.30 of its SE on
    MATH or 0.67 on MMLU, under either SE.
  - Fix (registrar): quote "ORDERING STANDS (content-cluster SE; under V0-leaf SE the MATH V0 - K status flips,
    marginal; signs and C1 rank order unchanged under both)", with the leaf DEFF / n_eff of row 10 beside it.
  - Any FRESH registration that reads these legs names the leaf DEFF and its source (this review). That matches
    D-2026-10-27-5 (B), "cell-aware beside".
- **C2 (record condition; MEDIUM): PM and PU FAILED are point-estimate words less than 1 SE from the band edge.**
  - PM is 0.79 SE outside |d| <= 0.005; PU is 0.56 SE short of -0.012.
  - The words are correct by the plan's rule, but they do NOT show that the moves differ from the predicted magnitudes.
  - Fix: print "FAILED (point estimate; 0.79 / 0.56 paired SE from the edge)" in the record. PP HELD is 1.39 SE
    inside its edge.
- **C3 (record relay to the registrar; LOW): the FRESH draft's D note cites a tau_L2-only number.**
  - The BZ-AXIS-CONFIRM-FRESH draft note under D-2026-10-27-5 (D) says: "reader tau^2 under cont has no WORK readout
    yet (TAU-CONT-ALL); PF points not revised (MATH WORK cont - g2 -0.0004, POSTRUN_TAU-GRID PR4)".
  - That -0.0004 is the tau_L2-only move (l2c). Under every-reader cont, the rule that (D) adopts, MATH C1(V0) moves by
    +0.0068 (0.0023).
  - The cont WORK values for PF1-PF7 (prog L25717 points) are -0.1540 / -0.2431 / +0.0072 / +0.2585 / +0.1161 /
    +0.2701 / +0.3592, each within 0.017 of its PF point.
  - Fix: bracket the note. Whether to revise the PF points is the registrar's call; planning SEs and n* stay owed from
    FRESH-DESIGN-SURFACE.
- **L1 (LOW): a sha in the plan names the wrong file.** Plan section 6 (b) gives "file sha256 e977fffa..." for
  `examples/mmlu_confirm_items.py`. e977fffa is the sha256 of the upstream hendrycks `categories.py` (that file's
  `CATEGORIES_PY_SHA256`), not of the file itself. The file is sha256-lf16:bf48432fa5460a30 (CRLF working tree
  1af0b528f4072413). The map content is verified (row 2). Fix: bracket the wording.
- **L2 (LOW): the hand-back quotes the dims contrasts at f2 only.** N - N512 is +0.073 (0.032) under f2 and +0.0574
  (0.0297, 1.9 SE) under cont. [P1] has both; the record should too.
- **L3 (LOW; settles the builder's open item): D2 is the share reading.** The plan fixed the reading before any data,
  with D2 as the word. sh_S - w_S = w_S (1 - w_S) D2 / G_all holds exactly (0.08603 both ways), so D2 IS the share
  reading. The G(V0|L2) / G(V0|L1) ratio measures how much leaf gain survives the declared subjects. That is a cause-1
  question, and the ratio is rightly not the word. No action.
- **L4 (LOW; descriptive): cause 2 is a comparison of anchors that differ widely.**
  - It sets 6 STEM anchors against 11 non-STEM ones. Per-anchor cont C1(V0) runs from -0.262 (engineering) to +0.401
    (culture).
  - The pre-specified SE (0.0382, content clusters) treats items as independent. Clustered by anchor (17 clusters) the
    SE is 0.0622; by V0 leaf, 0.0577.
  - Either way the word only moves further into NOT SUPPORTED (UNDERPOWERED). Any follow-up should cluster by anchor;
    it will be DESCRIPTIVE-ONLY at this n.

## Commands (scripts in `E:/TaxoArena_tmp/tau-cont-all-review/`; read-only on every record file)

```
# pins / hygiene (in Z:/FAC/TUBerlin/benchzoom_wt_tau-cont-all)
git log --format='%h %cd %s' --date=iso-strict 35b2724..7f87477; git diff --numstat 3803853 7f87477
git diff 1be267a 7f87477 -- examples/tau-cont-all.py
git diff --name-only 35b2724..7f87477 | grep -v -c -E '^(docs/tau-cont-all.md|examples/tau-cont-all.py|tests/test_tau_cont_all.py)$'   # 0
git diff --name-only 35b2724..7f87477 -- src docs/execution_graph.md | wc -l                                                # 0
for f in <3 files>; do git rev-parse HEAD:$f; tr -cd '\r' < $f | wc -c; git show HEAD:$f | sha256sum; done
find /e/TaxoArena_tmp/tau-cont-all /e/benchzoom_demo/followups/tau-cont-all -path '*/mutsand' -prune -o -path '*/mut' -prune \
     -o ! -newermt '2026-10-27 15:39:37' -print | grep -v -c '/pytest/'                                                   # 0
cd /e/benchzoom_demo/followups/tau-cont-all && sha256sum -c SHA256SUMS; cd /e/TaxoArena_backup_2026-10-27_tau-cont-all && sha256sum -c SHA256SUMS_all
# numbers (own code; no runner import): reproductions, rule O, predictions, leg changes, DEFF, dims, cause 2
python -I indep_npz.py; python -I leafdeff.py; python -I dims.py; python -I c2.py   # c2 reads the MMLU harness output
# own harness from library primitives (own fold loop, criterion, 2-d sums, g4, golden section; runner = data object only)
python indep_harness.py math 2;  python compare.py math math_s01234
python indep_harness.py mmlu 2 0; python compare.py mmlu mmlu_s0 0.116101
# own mutants (sandbox copies; TMP/TEMP/TMPDIR/BZ_SANDBOX redirected; BZ_MUTANT_NO_POOL=1)
python my_mutants.py 2
# tests
PYTHONPATH=src python examples/tau-cont-all.py --selftest      # TMP/TEMP/TMPDIR/BZ_SANDBOX in E:/TaxoArena_tmp
PYTHONPATH=src python -m pytest tests/test_tau_cont_all.py tests/test_tau_grid.py tests/test_reread_steps.py tests/test_execution_graph_sync.py -q -p no:cacheprovider
```
