# POSTRUN review: NEST-METER (test 1: tree cut vs nested and flat k-means at matched granularity, on the meter; exploratory, WORK rows)

Authority: D-2026-11-02-1 (`docs/agents/author_decisions/2026-11-02.md`, 9dff0985; read by the main session as tests 1
and 3, exploratory WORK-row readouts, zero LLM calls, no reserved/vault side, CPU only). Reviewer: adversarial reviewer,
2026-11-02. Zero LLM calls by me; responses read by me: only the saved per-item arrays of the run (WORK rows); RESERVED /
vault rows read by me 0. At most 3 worker processes, BLAS 1; outputs and the benchzoom worktree read-only; my scripts in
the session scratchpad, my mutant sandboxes and pytest basetemp in `E:/TaxoArena_tmp/rv_nest-meter`.
Reviewed: benchzoom branch `nest-meter` (local, worktree `Z:/FAC/TUBerlin/benchzoom_wt_nest-meter`), fb39598..0581fb3:
4 new files (`docs/nest-meter.md`, `examples/nest-meter.py`, `examples/nest-meter_mutants.json`,
`tests/test_nest_meter.py`; `git diff --name-only fb39598..0581fb3 | wc -l` = 4), 0 under `src/` (`... -- src | wc -l` = 0),
so `docs/execution_graph.md` owes nothing; master = fb39598 (ancestor; fast-forward); `git merge-tree` against `bbh-hier`
c764409: clean (disjoint files).
- Pins (LF of record; `git hash-object` of the working file = `git rev-parse 0581fb3:<path>`; 0 CR bytes in each working
  file, counted in Python): plan `blob:e62f2db6` (sha256-lf16:33fcce36a2764041), runner `blob:e2d58f2a`
  (sha256-lf16:23ba288e0cb48521), mutant spec `blob:51b06f98` (sha256-lf16:24f6ae79fd8cc9b8), tests `blob:b243e33f`
  (sha256-lf16:146c58093dee6204). Run of record: runner `blob:1b14f621` at 64f9b8f, `dirty ""` in all four parts and in
  `analyze_code` (meta.json); the tip runner is AST-identical to 1b14f621 outside the module docstring (`ast.dump` equal;
  `git diff 64f9b8f..0581fb3 -- examples/nest-meter.py`: +8 / -0, docstring).
- Outputs: `sha256sum -c SHA256SUMS` 11/11 (summary 8833f577, SHA256SUMS 79b50290); backup
  `E:/TaxoArena_backup_2026-11-02_nest-meter`: SHA256SUMS_backup sha256 ae0e9843, 18/18 OK in the backup AND 18/18 against
  the source dir (18 files there), the inner SHA256SUMS 11/11.

## Verdict

- **NEST-METER: OUTCOME CONFIRMED (exploratory, WORK rows, cont regime, SE clustered by V0 leaf), with qualifiers Q1, Q2
  (MEDIUM) and Q3-Q6 (LOW).** Every deciding number reproduces from the saved per-item arrays with my own code (max |diff|
  over every G and SE of every arm and contrast, both regimes, both clusterings, 4 datasets: 2.2e-16); every one of the 42
  words (30 below the anchors NEITHER, 15 of them (UNDERPOWERED); 12 at the anchors IDENTICAL) follows the plan's section
  8 rule (0 mismatches against meta.json); P1-P6 re-scored identically; reproduction re-checked by my own comparison.
- **merge_ok: YES (MERGEABLE)**, fast-forward, 4 new files, 0 `src/`; the corrections below go into a [P2] (insertion only)
  and the Q2 test fix into a new commit (a selftest change, no rerun needed: the run's numbers are confirmed independently).
- No BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table (deciding claims; WORK rows: MATH 2,949 x 69, MMLU-Pro 7,197 x 23, BBH 3,457 x 128, MMLU 8,425 x 79)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 27b14de committed before any code and any statistic | 27b14de 14:19:54 (plan only, parent fb39598); code e4c6768 14:43:31; first nest-meter artefact anywhere `E:/TaxoArena_tmp/nest-meter/mutants.py` 14:49; output dir born 15:32:00, after 64f9b8f 15:31:48; 0 nest-meter files in `E:/benchzoom_demo/followups` or `E:/TaxoArena_tmp` (maxdepth 2) dated 11:00-14:20 (only bbh-hier's); plan edits after 27b14de `--numstat` 89 / 0 ([P1], insertion only) | CONFIRMED | - |
| 2 | Levels of record (MATH 7/14/25/36, MMLU-Pro 14/28/51/80, MMLU 17/33/58/100, BBH 24/40; depth 5 dropped) | part JSON levels equal plan section 3 incl. per-anchor min-max; on WORK rows every arm has exactly the level's cell count in every seed (my count); dropping depth 5 follows the stated "at most 4 levels" rule | CONFIRMED | - |
| 3 | Partitions: TREE / BKM-A / BKM nested, BKM-A inside anchors, RND = tree sizes, 69 / 26 unique | from the saved `part:u*` arrays (my own canon / nesting code): TREE@L = V0 leaf array; BKM-A nested across levels in 5/5 seeds and inside the anchors; BKM nested, crosses anchors; KF not nested (MATH, MMLU-Pro, MMLU; nested on BBH's 2 levels trivially); RND per-anchor sizes = TREE's at every level; unique ids pairwise distinct partitions; identity flags = my recomputation (only the 4 contrasts at A) | CONFIRMED | - |
| 4 | Reproduction: RF 11/11, RT 12/12 (MATH, MMLU-Pro, MMLU), RB 16/16 (BBH) | my own loader of the comparators: sha256 = their SHA256SUMS, clusters equal; TREE, KF_0-4, RND_0-4 at L bit-equal (max |diff| 0.0) to FLAT-COMPARE f2 11/11 x 3, TAU-CONT-ALL cont 11/11 x 3 plus V0 leaves equal, BBH-WORK f2 11/11; controls (BKM-A_0 vs V0, KF_1 vs KM_0) differ. RB's 5 all-items K[s] lines: builder's (all-items labels not saved; the bit-equal KM readers imply the WORK-row partitions) | CONFIRMED | - |
| 5 | Words: all 30 cells below the anchors NEITHER at 3 SE_leaf; anchors IDENTICAL | 30/30 NEITHER, 15 (UNDERPOWERED) (MMLU-Pro C, L; BBH L; MMLU C, L); max |z| 2.98 (MATH L D_flat +0.1540, SE_leaf 0.0518); MATH C D_flat +0.1037 (0.0426, z 2.43), L D_nest +0.0813 (0.0409, z 1.98), L D_cost +0.0728 (0.0374, z 1.94); every D, SE, z, MDE80 in [P1]'s table equal to the printed digit | CONFIRMED | - |
| 6 | Support: DEFF_leaf 0.49-2.66, n_eff 1,107-12,459, SE ratio 0.75-1.60, MDE80 ranges | re-measured from the saved `leaf` array: DEFF 0.49 (MATH B D_cost) - 2.66 (MATH L D_nest); n_eff 1,107-12,459; ratio 0.75-1.60; leaf clusters 36 / 80 / 40 / 100; MDE80 MATH 0.012-0.199, MMLU 0.008-0.073, MMLU-Pro 0.003-0.074, BBH 0.139-0.247; planning SE of section 10 reproduced at L (0.0518 / 0.0132 / 0.0128) | CONFIRMED (Q5) | LOW |
| 7 | Beside: meter SE flips MATH C D_flat, L D_nest, L D_flat to BETTER (z 3.07 / 3.19 / 4.06); f2 MATH L D_flat BETTER z 3.41 | z 3.07 / **3.18** / **4.07** (3.19 and 4.06 are ratios of rounded values); f2 +0.1652, z 3.41; no other cell flips under either | CONFIRMED (Q4) | LOW |
| 8 | Predictions P1, P2, P4, P6 HELD; P3 HELD by 0.0043; P5 FAILED | re-scored identically; P3 margin **0.0042** (0.004248), SE_leaf 0.0295, z 0.14; P4 L - C step +0.0174 (SE 0.0260, z 0.67), C - B +0.1080 (0.0431, z 2.50); P5 -0.0366 (SE 0.0642, z -0.57) | CONFIRMED (Q1, Q4) | MEDIUM |
| 9 | COUNT, taus, fallbacks, guard | ledger made = cont per family: chain 50, control 50, cell 1,725 (= 69 x 25) on MATH, MMLU-Pro, MMLU; 650 (= 26 x 25) on BBH; cell choices at the bound 0; BBH chain L1/L0 2 at the bound; fallbacks 0 / 0; `guard_reads_end` [0], [0], [0], [0, 0]; logs print guard reads 0 at load and end of every part | CONFIRMED | - |
| 10 | 0 LLM calls; no vault / RESERVED response; BBH-HIER read no response | runner: 0 network / LLM-client imports (grep); Ollama `server.log` 0 request lines dated 2026/11/02 (`grep -c`); responses only through the reused guarded loaders; partitions read all items' TEXT (disclosed, plan section 2, as V0 / FLAT-COMPARE); nest-meter has 0 references to bbh-hier; BBH-HIER's own check is POSTRUN_BBH-HIER row 15 (19ab0e0a, CONFIRMED) | CONFIRMED | - |
| 11 | Selftest 7/7; mutants 73/73; suite 1,023 passed | selftest via `tests/test_nest_meter.py -m "slow or not slow"`: 6 passed (87 s); my control N0 passes; mutants: r1 72/73 on blob 8d3b64d4 (before the S2 hardening), r2 X71 + 2 controls on 00ec8f91 (= run logic); full suite 1,023 passed, 1 skipped, 13 deselected, 0 failed (886 s, my run) | CONFIRMED (Q6) | LOW |
| 12 | Own mutants (deciding paths) | 6 mutants: 5 killed, **N2 SURVIVED** (words' SE clustered by content cluster in `part_stats`; would flip 3 MATH words to BETTER) | Q2 | MEDIUM |

## Own mutants (sandbox copies of tip 0581fb3 under `E:/TaxoArena_tmp/rv_nest-meter/mut/<id>`, TMP/TEMP/TMPDIR redirected)

| id | change | result | decisive on the real data |
|---|---|---|---|
| N0 | control (unmutated) | passes | - |
| N1 | `cstat`: seeded side reads seed 0 only (`v = terms[0]`) | killed (S3) | yes (every seeded D) |
| N2 | `part_stats`: `"leaf"` grouping = `g.clusters` | **SURVIVED** | yes: MATH C D_flat, L D_nest, L D_flat -> BETTER |
| N3 | predictions read C1 from the f2 regime | killed (S6) | no (P4 HELD, P5 FAILED under f2 too) |
| N4 | reproduction drops the RND arm | killed (S4) | no (vacuity) |
| N5 | word SE without the MC term (`se_items`) | killed (REFUSED at A) | yes: MATH L D_flat z 3.04 -> BETTER |
| N6 | P3 on the f2 D | killed (S6) | no (f2 margin +0.0095, HELD) |

## Qualifiers and defects (each with its fix)

- **Q1 (MEDIUM, reading of P3-P5 and of [P1] readings 2-4).** The point-estimate predictions are scored by their rule,
  but their margins are noise: P3 +0.0042 (z 0.14), P4's L - C step z 0.67, P5 z -0.57. Reading (2) "about half of flat
  k-means' lead survives nesting" is the same z 0.14 margin (D_flat = D_nest + D_cost identically); reading (3) "the
  tree's C1 peaks before its leaves": MATH L - C -0.0108 (SE 0.0197, z -0.55), MMLU L - B -0.0407 (0.0259, z -1.57);
  reading (4) "BKM at 7 cells as much as KF at 36": +0.0001 (SE 0.0640). Fix: [P2] prints these SE_leaf / z beside P3-P5
  and readings 2-4 and says "the share of the MATH lead that survives nesting is 0.53 with an SE of about 0.19 even
  holding D_flat fixed (0.0295 / 0.1540), and D_flat itself is z 2.98";
  the hand-back's "P3 HELD by 0.0043" is never quoted without "z 0.14".
- **Q2 (MEDIUM, test gap on a deciding path).** N2 survives: no selftest check pins that `part_stats` clusters the
  words' SE by the V0 leaf (S3 checks `cstat` given leaf groups; X29 swaps only inside `word_entry`). The run itself is
  unaffected: TREE@L equals the saved `leaf` array and my SE_leaf from it equals the part JSON to 2.2e-16. Fix (new
  commit, no rerun): in S5 assert every `stats[reg][*][*]["leaf"]["clusters"] == rec["n_leaf"]` on a fixture where
  `n_leaf != n_clusters`, and add N2 to `nest-meter_mutants.json`.
- **Q3 (LOW, knife edge).** MATH L D_flat reads NEITHER at z 2.98, 0.02 SE under the bar; it reads BETTER under the meter
  SE (4.07), f2 (3.41) or without the pre-specified MC term (3.04, N5). The word follows the rule; it is a reproduction of
  TAU-CONT-ALL known before the plan (section 7), not new evidence. Fix: [P2] quotes it "NEITHER at z 2.98 (reproduced)".
- **Q4 (LOW, transcription).** [P1] meter z 3.19 / 4.06 -> 3.18 / 4.07; P3 margin 0.0043 -> 0.0042 (0.004248). Fix: [P2].
- **Q5 (LOW, SE calibration).** SE_leaf clusters on the tree's leaves; for D_cost neither arm's cells are the clusters,
  and DEFF_leaf 0.49 on MATH B D_cost (below iid) says the leaf clusters do not track that contrast's dependence. An
  understated SE cannot change a NEITHER, so no word moves; the D_cost MDE80s are lower bounds. Fix: [P2] states it.
- **Q6 (LOW, mutant provenance).** "73/73" joins two blobs: r1 (72 killed) ran on 8d3b64d4 before the S2 hardening, r2
  (X71) on 00ec8f91; the hardening only adds a refusal check, so r1's kills carry over. Fix: [P2] names both blobs.
- Disclosed and fine: one partial readout (`summary_partial_20261102T151839Z.txt`, three parts) was written before the
  MMLU part ran; the MMLU part ran at the same clean blob 1b14f621, so nothing could adapt.

## What the result licenses (exploratory, WORK rows only)

Licensed: on these WORK rows, under the cont regime and the V0-leaf SE, at the tree's own per-anchor cell counts (levels
B, C, L; the anchors identical by construction), no contrast among the tree cut, nested within-anchor bisecting k-means
and flat within-anchor k-means separates at 3 SE_leaf on MATH, MMLU-Pro, MMLU or BBH (MDE80 up to 0.199 / 0.074 / 0.073 /
0.247; 15 of 30 cells UNDERPOWERED by the plan's flag). In words: a nested k-means hierarchy is not detectably worse
than the tree at any level, and the price of nesting relative to flat k-means is not detected.
Not licensed: "equal", "equivalent" or "nesting is free" (P1, P2, P6 were low-power NEITHER predictions); any ordering of
BKM-A, TREE and KF at any level (every point estimate is under 2.5 SE_leaf, MATH L D_flat a reproduction); the "half"
decomposition; any vault / RESERVED / fresh-item claim, any other embedder, corpus or a TaxoAdapt-style generalisation;
anything that replaces V0 for BZ-AXIS-CONFIRM-FRESH or switches a deciding estimator.

## Commands (all read-only on outputs and the worktree)

```
git -C <wt> log --format='%h %p %ci' ; git show --name-only 27b14de e4c6768 64f9b8f 0581fb3
git -C <wt> diff --numstat 27b14de..0581fb3 -- docs/nest-meter.md          # 89 0
git -C <wt> diff --name-only fb39598..0581fb3 | wc -l ; ... -- src | wc -l  # 4 ; 0
git -C Z:/FAC/TUBerlin/benchzoom merge-tree --write-tree master nest-meter / bbh-hier nest-meter   # clean
python: ast.dump(1b14f621 minus docstring) == ast.dump(tip minus docstring)  # True ; CR bytes 0 in all 4 files
cd E:/benchzoom_demo/followups/nest-meter && sha256sum -c SHA256SUMS                     # 11/11
sha256sum -c E:/TaxoArena_backup_2026-11-02_nest-meter/SHA256SUMS_backup (in backup and in source)  # 18/18, 18/18
stat -c '%w %y' outputs and logs ; find E:/benchzoom_demo/followups E:/TaxoArena_tmp -maxdepth 2 -newermt 11:00 ! -newermt 14:20
<scratchpad>/rv_nest.py     # own CR1 leaf/content SE, MC, words, flags, predictions, partition checks: max|diff| 2.2e-16, 0 word mismatches
<scratchpad>/rv_repro.py    # own comparator check: 11/11 x 7 bit-equal, sha / clusters / leaf equal, 2 negative controls differ
<scratchpad>/rv_margins.py  # SE_leaf of P3-P5 margins and readings 2-4
<scratchpad>/rv_mut.py      # N0-N6 in sandbox copies, 3 at a time
grep -c 'GIN\] 2026/11/02' C:/Users/octav/AppData/Local/Ollama/server.log                  # 0
PYTHONPATH=src pytest -q -p no:cacheprovider -m "slow or not slow" --basetemp <sandbox> tests/test_nest_meter.py  # 6 passed
PYTHONPATH=src pytest -q -p no:cacheprovider --basetemp <sandbox>          # 1,023 passed, 1 skipped, 13 deselected, 0 failed (886 s)
```
(`<wt>` = `Z:/FAC/TUBerlin/benchzoom_wt_nest-meter`; `<scratchpad>` = this session's scratchpad, not committed.)
