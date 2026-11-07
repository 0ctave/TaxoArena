# REVIEW: benchzoom branch review-fixes-2026-11-06 (selftest pins and plan brackets owed by tests 1-3)

Authority: D-2026-11-06-1 item 3 (`docs/agents/author_decisions/2026-11-06.md`; the small review fixes go ahead) and the
brief under D-2026-11-06-3. Reviewer: adversarial reviewer, 2026-11-06. Zero LLM calls; no response, vault, RESERVED or
sealed row read (the only run output read is `E:/benchzoom_demo/followups/skill-backoff/readouts.csv`, a committed run's
WORK-row readout, for the Q2 spot check). At most 3 processes, BLAS 1. My trees, sandboxes and pytest basetemp:
`E:/TaxoArena_tmp/rv_review-fixes-2026-11-06/` (TMP / TEMP / TMPDIR / BZ_SANDBOX redirected; nothing deleted).
Reviewed: `Z:/FAC/TUBerlin/benchzoom_wt_review-fixes`, 4d08a3d..06456b2 (6 commits: c964f95, 1a4bf00, 9919fe1, 9dc5453,
b622e19, 06456b2); 10 files (`git diff --name-only 4d08a3d..06456b2 | wc -l` = 10), 0 under `src/` (`... -- src | wc -l`
= 0), so `docs/execution_graph.md` owes nothing. Master = 4d08a3d; `rev-list --count` master..branch 6, branch..master 0
(fast-forward); `git merge-tree --write-tree master review-fixes-2026-11-06` clean; no remote, no upstream; worktree
`status --porcelain | wc -l` = 0 before and after my runs.

Pins at tip 06456b2 (LF of record = the blob; this worktree is CRLF, core.autocrlf true, so the CRLF rendering is beside):

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working file) | base at 4d08a3d (= POSTRUN pin) |
|---|---|---|---|---|
| examples/nest-meter.py | 1e9ad820 | e59351ce1922f630 | 3be8d5b853d5672a | e2d58f2a |
| examples/bbh-hier.py | 88b88938 | 315b3f39fdcd9eda | 172178bcfbeccbf3 | b6be8cfd |
| examples/skill-backoff.py | fead2e0c | 8d97c563fae583f6 | b8a28cf89a946eb2 | a09bebfa |
| docs/nest-meter.md | 43e57e43 | 9886865a2b6d0422 | b7aa9df9a26039cf | e62f2db6 |
| docs/bbh-hier.md | 7dce0841 | 43e73e34f4e4b708 | db635a1ce70a074b | 550a0914 |
| docs/skill-backoff.md | 34a54003 | 376c6ea631a95c7b | 750d3aa91f790a6c | a682dfab |
| examples/nest-meter_mutants.json | ea53688f | 75e4b957074d2889 | 4cf2896fa7437e85 | 51b06f98 |
| examples/skill-backoff_mutants.json | 16dfb311 | 477b4f3e0f70e613 | 3978e62f1dbe5f4e | bd063ea3 |
| tests/test_nest_meter.py | bc8a40ea | 78d448a397f1c698 | 80f1061652a54b30 | b243e33f |
| tests/test_skill_backoff.py | 91224fce | d3984e9e9fd624bd | bec456947123fc56 | e18d3222 |

`git hash-object` of each working file = `git rev-parse 06456b2:<path>`; the runner blobs at the fix commits (c964f95,
9919fe1, b622e19) equal the tip's (later commits touch docs only).

## Verdict

- **MERGEABLE: YES** (fast-forward, 6 commits, 0 `src/`). Every builder claim reproduces with my own commands; one new
  LOW selftest gap (D-1, my OM2) and three LOW record slips (D-2..D-4). None blocks the merge: no run path changed and the
  runs of record were reproduced independently by their POSTRUNs.
- Owed items discharged: NEST-METER Q2 (N2) and [P2]; BBH-HIER T-1 (R3, R5) and [P3]; SKILL-BACKOFF Q5 (R2-R4) and [P3]
  with the registrar's Q2 correction. Every item on the registrars' "BRACKETS AND FIXES OWED" lists (prog L25864-L25872,
  L25873-L25883) is present.
- No BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | 11 target mutants SURVIVE on master 4d08a3d and are KILLED on the branch | own runner on `git archive` trees of 4d08a3d and 06456b2 (LF blobs, not the working tree), one exact replacement each (count 1 checked in both trees): master 11/11 SURVIVED (N2, N2b; R3, R5, R3b; R2, R2b, R2c, R3, R4, R4b), tip 11/11 killed, each by the new check it names; controls N0 / B0 / S0 pass on both | CONFIRMED | - |
| 2 | The new checks execute (not vacuous) | discriminator: on master the new check names appear 0 times, on the tip in every run; PASS lines of the control 7 -> 8 (nest-meter), 118 -> 121 (bbh-hier), 8 -> 10 (skill-backoff); printed values: S5 clusterings 132 + 176 + 132 = 440 statistics (n_leaf 12 / 32 / 12 vs n_clusters 474 / 792 / 474); S3 unseen task {u0: 11}, harness {u0: 12}; seeded cstat by hand 6 entries, MC 0.0239-0.0504 (> 0) | CONFIRMED | - |
| 3 | Runners identical outside docstrings and `selftest()` | `ast.dump` of every top-level node except the module docstring and `selftest` equal, master vs tip (114 / 162 / 122 nodes); `selftest` signature equal; module docstrings 0 lines deleted or replaced; line level `git diff --numstat` runners 50/0, 68/0, 121/0 (master is a line subsequence of the tip) | CONFIRMED | - |
| 4 | Brackets insertion only | `--numstat` docs 38/0, 50/0, 45/0, one hunk each at end of file; mutant specs 14/0, 46/0 (valid JSON, 77 / 124 entries, 0 duplicate ids, every new entry's `old` occurs once in its target at tip); tests 1/1 each (the SELFTEST line count 7 -> 8, 8 -> 10: matches item 2) | CONFIRMED | - |
| 5 | Brackets quote the reviews faithfully | read against POSTRUN_NEST-METER (2f84191d) Q1-Q6, POSTRUN_BBH-HIER (19ab0e0a) Q1-Q6, T-1, POSTRUN_SKILL-BACKOFF (59520e3f) Q1-Q7 and both registrars' records: every figure equals the review's digit (e.g. P3 +0.0042 (0.004248; SE_leaf 0.0295, z 0.14); meter z 3.18 / 4.07; D draws centre 0.4263, D / SE 15.2; V_kf KF-cell z 3.11 / 3.03); the only paraphrase (SB Q2 "nesting's effect is not detected under one common tau") prints the POSTRUN wording beside it. Two row citations point at the wrong row (D-3) | CONFIRMED (D-3) | LOW |
| 6 | Registrar's Q2 correction: MMLU label-only shrinkage +1.97 is below Z_bo +2.55 | from `readouts.csv` (outputs `sha256sum -c` 11/11): MMLU rate TREE-BL - TREE-RAW 1.97217, Z_bo 2.54664, TREE-BO - TREE-BL 0.574464 (SE_word 0.299309); 1.97217 + 0.574464 = 2.54663 (the identity); MATH 10.686 vs 10.2755 (internal -0.41053, 0.151342); MMLU-Pro 1.73472 (0.3209) vs 1.1674; BBH 2.56642 = 2.56642. "At least" holds on 3 of 4, not on MMLU: the correction and the bracket are right | CONFIRMED | - |
| 7 | Suite 1034 passed, 1 skipped, 0 failed | own run of the default suite on the tip: 1,034 passed, 1 skipped, 14 deselected, 0 failed (972 s), equal to the claim. BUT the default `addopts -m 'not slow and not network'` deselects both changed tests (`test_full_selftest_passes` in test_nest_meter / test_skill_backoff are `@pytest.mark.slow`), so the claim does not cover the change; my run of the three affected files with `-m "slow or not slow"`: 18 passed, 0 failed (162 s) | PARTLY (D-2) | LOW |
| 8 | Nothing under `src/` or `E:/benchzoom_demo` changed | `git diff --name-only 4d08a3d..06456b2 -- src \| wc -l` = 0; `find E:/benchzoom_demo E:/benchzoom_cache -newer <builder's stamp_start 13:20:47> -type f \| wc -l` = 0, and 0 again after my runs (`-newer` my stamp) | CONFIRMED | - |
| 9 | T-1 fix pins "FLAT's seed pairing" (commit 9919fe1 title) | R5 (FLAT read as unseeded) is killed, but my OM2 (contrast sides paired in reverse, `zip(pa, pb[::-1])`) SURVIVES at the tip: in the S8 fixture BKM's three seeds give the same best cut (G1 bm [1.0, 1.0, 1.0], G2 [0.919954 x 3]; diagnostic print in a sandbox copy), so the A-to-B seed pairing of D1-D4 is not pinned | PARTLY (D-1) | LOW |

## Own mutants (sandbox copies of the git-archive trees; the copy's `--selftest`, BZ_MUTANT_NO_POOL=1; 3 at a time)

| id | change (one exact replacement) | master 4d08a3d | tip 06456b2 | decisive |
|---|---|---|---|---|
| OM1 | nest-meter `part_stats`: words' grouping = `np.asarray(g.leaf)[::-1]` (same n_leaf, wrong values: tests "by value", not "by count") | SURVIVED | killed (S5 clusterings) | yes (every SE_leaf word) |
| OM2 | bbh-hier `analyze_core` CONTRASTS: `per = ... zip(pa, pb[::-1])` (seed pairing of the two sides reversed) | SURVIVED | **SURVIVED** | yes on reuse (D1-D4 MC term and SE); no on the run of record (POSTRUN_BBH-HIER row 9 reproduced D4 per seed by independent code) |
| OM3 | skill-backoff `_task`: `unseen[f"u{u}"] = 0` (the guard always prints the run's own value) | SURVIVED | killed (S3 unseen cells) | yes (the unseen guard) |

## Defects (each with its fix)

- **D-1 (LOW, selftest gap, new).** OM2 survives: no fixture has a seeded B side whose seeds differ, so `zip(pa, pb)`'s
  index pairing in `analyze_core`'s CONTRASTS loop is unpinned (R5 pins only that FLAT is read by index). Fix before the
  bbh-hier runner is reused: in S8 (b) also give BKM differing seeds (e.g. swap two BKM seed hierarchies, or relabel a
  share of one seed's leaves on a fixed stream), assert `max(bm) - min(bm) > 1e-6`, keep the per-seed equality, and record
  OM2 in the runner's docstring table. Wording until then: "FLAT's seed indexing pinned", not "seed pairing pinned".
- **D-2 (LOW, test claim).** "Suite 1034 passed" is the default suite, which deselects the two changed slow selftest
  tests; the hand-back should name the slow run separately (`-m "slow or not slow"` on the affected files: 18 passed). No
  code change.
- **D-3 (LOW, citations in the brackets).** nest-meter [P2] Q2 cites "POSTRUN row 12" for "TREE@L equals the saved leaf
  array ... 2.2e-16": that sentence is POSTRUN Q2's (row 12 is the mutant row). skill-backoff [P3] Q5 cites "row 6: the MC
  term recomputed and matched": the sentence is the POSTRUN's mutant-table R3 line (row 6 recomputes every SE to its digit,
  so the substance holds). Fix: a one-line insertion bracket on each when the files are next touched; no number changes.
- **D-4 (LOW, reproducibility).** bbh-hier has no committed mutant spec: R3, R5, R3b's replacement strings exist only in
  the scratch runner `E:/TaxoArena_tmp/review-fixes-2026-11-06/mutants.py` (the docstring table names them in words;
  nest-meter and skill-backoff got spec entries). Fix (optional): quote the three `old` / `new` strings in the docstring
  table or add `examples/bbh-hier_mutants.json`. (The scratch runner also labels R3b "V0m side unweighted"; the committed
  docstring's "the B side read at its point value" is the correct description of the replacement.)

## Commands (my scripts in the session scratchpad and `E:/TaxoArena_tmp/rv_review-fixes-2026-11-06/`; read-only on the worktree)

```
git -C <wt> diff --numstat 4d08a3d..06456b2 ; git -C <wt> diff --name-only 4d08a3d..06456b2 | wc -l ; ... -- src | wc -l   # 10 ; 0
git -C <wt> rev-parse 4d08a3d:<path> / 06456b2:<path> ; git -C <wt> hash-object <path> ; git show 06456b2:<path> | sha256sum ; sha256sum < <path>
git -C benchzoom rev-list --count master..review-fixes-2026-11-06 / reverse   # 6 / 0 ; merge-tree --write-tree clean ; remote -v | wc -l  # 0
git -c core.autocrlf=false archive 4d08a3d|06456b2 examples src tests | tar -x -C <R>/trees/{master,tip}       # CR bytes 0, blobs equal
python -I rv_ast.py        # AST outside module docstring + selftest equal (3/3); docstring lines deleted 0
python rv_mut.py master ; python rv_mut.py tip   # 17 specs x 2 trees -> mut_master.json / mut_tip.json (table above)
diag/OM2: sandbox copy with a print after the S8 D4 check -> bm constant over BKM's 3 seeds; selftest PASS
grep -E '^(math|mmlu_pro|bbh|mmlu),rate,' readouts.csv (Z_bo, TREE-BL - TREE-RAW, TREE-BO - TREE-BL) ; sha256sum -c SHA256SUMS  # 11/11
PYTHONPATH=src pytest -q -p no:cacheprovider -m "slow or not slow" --basetemp <R>/pt_slow tests/test_nest_meter.py tests/test_skill_backoff.py tests/test_bbh_hier.py   # 18 passed
PYTHONPATH=src pytest -q -p no:cacheprovider --basetemp <R>/pt_full      # 1,034 passed, 1 skipped, 14 deselected, 0 failed (972 s)
find E:/benchzoom_demo E:/benchzoom_cache -newer <stamp> -type f | wc -l   # 0 (builder's stamp and mine)
sed -n 25864,25883p docs/judge_v2_program.md (registrars' records; owed lists) ; grep "\[registrar's note" in both spans  # 0 / 1
```
(`<wt>` = `Z:/FAC/TUBerlin/benchzoom_wt_review-fixes`; `<R>` = `E:/TaxoArena_tmp/rv_review-fixes-2026-11-06`.)
