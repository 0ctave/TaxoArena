# READY review: RP05 FLAT-GENERALITY (+ MIX-FLAT-SELFTEST-GAPS) at 4b3489e (adversarial reviewer, 2026-09-27, zero calls, no real-data statistic)

## VERDICT

**FLAT-GENERALITY: NOT READY. No `--run` is licensed.**

**Merge: MERGEABLE by pathspec at the pins below (all three files), as tools only.**
- Merging closes MIX-FLAT-SELFTEST-GAPS, which is a registered precondition.
- `flat_generality.py` refuses `--analyze` while `VA_RULINGS` is unruled, so merging it licenses nothing.

Why NOT READY:
- **N1 BLOCKER.** The registration defines arm (a)'s V_A in words that do not fix it (L21653), and the build refuses to choose.
  - The registration requires a change to V_A to be a **pre-data bracket before the READY**. No such bracket exists: `grep -n "V_A" docs/judge_v2_program.md` gives 3 hits, all inside the registration (L21653, L21660, L21674).
  - `ensure_meta` writes `VA_RULINGS` and the script pins into every tree's `meta.json`, and `--analyze` requires every partition to carry the same script identity. So a ruled build is a new blob, and every partition written by this blob is orphaned.
  - Consequence: no run of blob 2115887c can produce an outcome.
- **N2 HIGH.** Registered arm (c), the size-floor V (L21655), is neither built nor mentioned. `grep -c -i "size-floor\|size floor\|arm (c)\|arm c" tools/analysis/flat_generality.py` = 0, counted over the whole file.
- **N3 HIGH.** The selftest does not pin the readout wiring. I wrote 9 mutants and all 9 SURVIVE the full selftest, FG-E2E included. They include the reference arm of the deciding rule D1 / L1_r, A2's seed and A2's spread leg, and the run-path hygiene refusal. FG-E2E checks that text is present, not what the values are.

What I did NOT run: `--run`, `--analyze` or `--identity-check` on real data. I printed no M1, M2, M3 or M4 on real data.
- My real-data reads were counts only: pools, fit sets, the anchor filing, twin groups, and stem_key / exact overlaps.
- I also ran one byte-equality check of the parameterised fit path against FLAT-MIX-MMLU's recorded state bodies. It prints only equal / not equal.
- All reads used `mode=ro&immutable=1` or the instrument's guard.
- Before and after my reads, the full-file sha256 of the three DBs (snapshots.db 390c313e5a40e0a7, mmlu_pro_dataset_cache_v2.db 4f65414f7625a1e7, embeddings_cache.db 52229e1ebfdda76e), their mtimes and sizes were identical, and their -wal files were 0 bytes.
- No JVM was running and no construction was open (`Get-CimInstance Win32_Process` listed only ollama). I ran one Python process at a time, with BLAS pinned to 1 thread.

### Pins (the LF rendering is of record; the worktree has 0 CR bytes in all three files; `git hash-object` = blob at 4b3489e)

| file @ 4b3489e (branch w0-rp05-flat-generality, worktree clean, parent a357ef0) | blob | sha256-lf16 | sha256-crlf16 (reference) |
|---|---|---|---|
| tools/analysis/flat_generality.py (new, 1,471 lines) | blob:2115887c813af62c680d75a93bf5dc33e9a46e2c | sha256-lf16:b324311d7c0d7ce4 | sha256-crlf16:6e8ebcd70d9b63fd |
| tools/analysis/flat_mix_mmlu.py (was c5cc7934, 1,480 lines) | blob:4e6418e110de3c92bb6c0c5ac48d6ff97b99782e | sha256-lf16:006f04a821629be1 | sha256-crlf16:be5ca19404cb3c4f |
| tools/analysis/mix_lrt_site.py (was 3e6a682c, 2,648 lines) | blob:fbb480cac2bc7a8035c8ac954c264fe263d5720f | sha256-lf16:6dc57dd7b864986c | sha256-crlf16:6c304f8cdad11b91 |

Scope and ancestry:
- `git diff --name-only a357ef0 4b3489e | wc -l` = 3, the three files above.
- The same list grepped for `config/|\.env|\.gitignore|report/` = 0.
- `git merge-base --is-ancestor a357ef0 4b3489e` is true, so the registration (a357ef0) precedes the code.
- The imports are identical between main and the worktree: anchor_free_readout.py 514e74da, free_tests_f4_f7.py f0749d61, split_side.py 05224b5a, pool_guard.py 6521b51a.
- No state exists: `experiment_results/flat_generality` is absent in both main and the worktree.

## 1. Per-claim table

Scripts live in scratchpad `rv_rp05/`: census.py, census2.py, twins.py, param_repro.py, my_mutants.py, harness_ctl.py, and the *.log files.

| # | claim (builder) | status | command / script | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Pools: each snapshot's reserved_queries hash to the tree's pool, and the DB rows agree | CONFIRMED | census.py (pool_guard.judgeable / compute_pool_id / pool_rows, immutable) | pd610c9ad05255f16 3,448; p19d9f473b5a610a0 3,446; p8a29d8f3ff75aa55 3,437; p2dca 3,445 (o0 and af_clean); DB rows set-equal on all 5 | - |
| 2 | Fit sets 8,126 / 8,130 / 8,133 / 8,125 (8,125 for af_clean) | CONFIRMED | census.py, my own DFS over the snapshot graph | 8,126 / 8,130 / 8,133 / 8,125 / 8,125 ids = texts; 0 ids missing in queries; all fit texts are mmlu_pro.question rows (census2.py: 8,126/8,126 and 8,125/8,125), so exact-text hygiene is not vacuous | - |
| 3 | No fit text equals or shares a stem_key with an EVAL text | CONFIRMED (for judgeable EVAL only) | census.py, census2.py | 0 exact and 0 stem_key on all 5 trees. The 151 / 154 non-judgeable (sentinel) reserved ids have no eval_question_link text, so they cannot be keyed here: the steward's 9073a8a-form check (sentinels in the key set) is still owed | precondition |
| 4 | O: 14 anchors, leaf counts [11,9,5,6,5,6,3,8,5,6,7,5,5,3]; 7,746 fit texts under one anchor, 378 under two, 1 under three | CONFIRMED | census.py (graph leaves per depth-1 region) | identical; 379 of 8,125 = 4.66% multiply filed. The registration's "(one anchor per text)" is false for O's graph filing | feeds N1 |
| 5 | Kish m-bar 1.0006 / 1.0000 / 1.0000 / 1.0000 (1.0000 for af_clean) | CONFIRMED | twins.py (stem_key on the eval_question_link texts of the judgeable ids) | s137: 3,448 questions in 3,447 groups, m-bar 1.0006, n_eff 3,446; the others have singleton groups (n_eff 3,446 / 3,437 / 3,445 / 3,445) | - |
| 6 | The Support SE / MDE figures re-derive | CONFIRMED | arithmetic on flat_mix_mmlu_outcome.txt L21-L22, L47 | SE_M1 = sqrt((0.1533 - 0.0430^2)/3445) = 0.006630 (registered 0.00663); MDE 2.80 x 0.00663 = 0.01856 (registered 0.0186). SE_M2 from the F6 CI [-2.230, -0.826]: 1.404e-3 / 3.92 = 0.358e-3 (registered 0.357e-3; gap 0.001e-3, a percentile-CI asymmetry); MDE 1.00e-3. Bars max(MDE, spread): 0.0305 and 1.00e-3; P2 margin 0.035 - 0.0305 = 0.0045. DEFF 1.0 source: measured on af_clean_s42 (row 5); the re-draws' m-bar now measured (row 5) | - |
| 7 | flat_generality selftest 63 checks | CONFIRMED | `python tools/analysis/flat_generality.py --selftest` (fg_self.log) | 63 checks, PASSED, 12 s | - |
| 8 | flat_generality mutants 22/22 killed | CONFIRMED, but INCOMPLETE | `--mutants` (fg_mut.log), then my_mutants.py (full selftest per mutant) | 22 of 22 KILLED; **reviewer mutants 0 of 9 KILLED** (section 3). Harness controls: the builder's "D2 counts wins" mutant is killed in my harness, and a mutant that breaks fit_va fails FG-E2E, so FG-E2E does execute mutant code | HIGH (N3) |
| 9 | flat_mix_mmlu selftest 81, mutants 32/32 | CONFIRMED | fm_self.log, fm_mut.log | 81 PASSED; 32 of 32 KILLED | - |
| 10 | mix_lrt_site selftest 158 (417 s), mutants 60/60 | CONFIRMED | mix_self.log, mix_mut.log (TAXOARENA_DATA_ROOT = main) | 158 PASSED (401 s); 60 of 60 KILLED. From a worktree without TAXOARENA_DATA_ROOT the selftest fails (rc 1 after 19 s): ST-REG reads embeddings_cache.db. The selftest is not synthetic-only; this is known (dd2477e D2, record only) | LOW (known) |
| 11 | Inertness of flat_mix_mmlu.py's default path vs c5cc7934, with execution witness and sensitivity control | CONFIRMED | `--inertness` (fg_inert.log) | all 7 comparisons IDENTICAL (state 13 files, outcome 4,281 B, CSV 1,528 B); 9 [PIN before] lines = 9 [PIN after]; witness: assemble_res 1 call, k=None defaults 12, leg A has no assemble_res; BOOT_SEED control: the outcome DIFFERS | - |
| 12 | The parameterised path is the FLAT-MIX-MMLU instrument | CONFIRMED (beyond the builder) | param_repro.py: FM.fit_set(snapshot, fit_n) + fit_matrix(dim) + fit_partition(k, tree_kw) on real data, compared to experiment_results/flat_mix_mmlu/state/part_*.json | V0 and K0 bodies byte-identical (script / cpu / wall dropped). T and O identical except the `run_dir` string, and the default path shows the same one-key difference: my TAXOARENA_DATA_ROOT used forward slashes. o0_clean_s42's own fit text set == af_clean_s42's. 7.7 CPU-s | LOW (run_dir spelling) |
| 13 | D6 escalation_tasks: behaviour unchanged | CONFIRMED | read `git show a357ef0:tools/analysis/mix_lrt_site.py` L920-L932 against the new L966-L972 and L994-L1005 | the same three `break` conditions, in the same order; `site_q` returns None unless all B draws are present (`len(lrs) != B`, L1020), so the builder's "no mutant for the 199-present guard" is correct (an equivalent mutant) | - |
| 14 | D3 cost lines / measured CPU | PARTLY | read measured_cpu L1002-L1016 | total correct; the docstring says p10 = "observed cells (all legs of the observed fit)", but the code files the observed cells' p5 / p20 CPU under desc | LOW |
| 15 | The --dry-run prints no statistic | CONFIRMED | builder log flat_generality_dry_run.log (51 lines) read in full | counts, pins and synthetic timing only | - |
| 16 | V_A ambiguities are real | CONFIRMED | registration L21653; plan rev2 L779 ("one anchor per text, held-out routed by O's own filing"), L898, L900 | the plan settles none of the three. There is also a reading the builder did not list (N1 below) | BLOCKER (N1) |
| 17 | Identity check (P6) to be run by the delta READY | NOT RUN (UNDETERMINED) | - | not run by the builder or by me (the orchestrator forbade real-data runs). Row 12 covers the fit path; the M1 / M2 path (`tree_pool` -> `corpus_for` -> `identity(dim)`) is still owed | condition |
| 18 | Machine cap respected | REFUTED (the builder's own disclosure) | builder report | twice, two single-threaded Python processes ran at once (a breach of one heavy process per agent); no effect on any artefact | LOW (process) |

## 2. Fidelity to the registration (L21646-L21678)

- Arms V and K, and the measures M1-M4: called from flat_mix_mmlu with keywords, nothing re-implemented. Row 12 shows the fit bodies reproduce the record. Twin-group bootstrap: seed 20260926. OK.
- D1: C1_r / C2_r / L1_r against V0_r with spread_V over V0-V4; the point decides the spread leg and the CI decides the CI leg; the seed-wise all-5 rule is printed. OK by reading, but the V0 choice is untested (RV1).
- D2: k is printed, never rounded, and the reading words carry k. OK.
- A1: M2 in the L1 form against spread_V at k 84. OK.
- A2: V_A0 minus O against spread_V_A, positive CI. OK by reading, but untested (RV2, RV3).
- P1-P7: scored as registered. P2 and P7 are scored per re-draw, which the registration does not aggregate; the build discloses this. It needs the pre-data bracket (N1 item e).
- F1 (k = 0) and F2 (A2 fires): OK.
- Split words (rule 12): "EVAL side" for every tree; "id-disjoint only" for the re-draws; content-closed for o0 / af_clean. OK.
- af_s42_o1's non-independence is disclosed in the outcome's info line.
- M2 is read on the same 10,925 keyed questions as FLAT-MIX-MMLU. These include every tree's own fit texts; this is registered ("as in FLAT-MIX-MMLU"), not a new leak.
- Support: the render prints the measured m-bar, n_eff and an observed-discordance SE / MDE beside the registered ones.
  - Its SE formula is sqrt(disc / n_eff). The registered SE is sqrt((disc - d^2) / n): 0.00667 vs 0.00663 on FLAT-MIX-MMLU's numbers. LOW, label or align.
  - Reachability: P7's 80% band [0.015, 0.045] includes spreads above the predicted loss of 0.035. Where spread_V_r > 0.035, L1_r is unreachable at the predicted effect at any budget (leg (g)). The render prints the effective bar per tree; it should also print, per re-draw, "reachable at the predicted -0.035: yes / no". LOW.
- Preconditions (L21678):
  - MIX-FLAT-SELFTEST-GAPS: built here (D3, D4, D5, D6, D7 and delta-READY D1, D4 are all present and mutant-covered), and merged by this review's procedure.
  - Parameterisation delta READY: this review, NOT READY.
  - Steward closure check: owed.

## 3. Reviewer mutants (my_mutants.py; each run against ALL of FG-THREADS, FG-RENDER, FG-POOL, FG-VA, FG-STATE, FG-E2E; original PASS)

| id | mutation | result |
|---|---|---|
| RV1 | `d1_verdict` reads `paired["K0"]` instead of `["V0"]` (the deciding rule's reference arm) | SURVIVED (st_render sets K0 = a copy of V0; FG-E2E checks presence only) |
| RV2 | `spread_VA` computed over the V seeds | SURVIVED |
| RV3 | A2 reads V_A seed 1 (`arm="A1"`) instead of seed 0 | SURVIVED |
| RV4 | `run()`'s `hygiene(...)` call removed (the "no EVAL question in any fit" refusal) | SURVIVED (the function is tested, its call is not; the replica has no overlap) |
| RV5 | `va_assign` ignores the held-out-anchor ruling (always leaf_ancestor) | SURVIVED |
| RV6 | `analyze()`'s check that every partition carries one script identity removed | SURVIVED |
| RV7 | `corpus_for`'s p2dca id-file cross-check removed | SURVIVED |
| RV8 | support discordance computed against K0 | SURVIVED |
| RV9 | routed filing ignores the ruling (always d1_nearest) | SURVIVED |

## 4. Defects

- **N1 BLOCKER: V_A is unruled, and the build is un-runnable by design.** Fix: a pre-data bracket (the tree-construction-specialist rules, the registrar records, before any READY) on the following.
  - (a) Fit filing. Offer a third option beside graph-exclusive and routed: **declared-label**, where each fit text is filed to the anchor whose label equals its MMLU-Pro category. O's 14 anchor labels are exactly the 14 categories (flat_generality_dry_run.log L42). It is the only reading that makes the registration's "(one anchor per text)" true without exclusion, and it fits the name "label-anchored". Labels are TRAIN-side, and the held-out routing stays label-free.
  - (b) Held-out anchor: leaf_ancestor or d1_nearest.
  - (c) Assignment: MAP or nearest mean.
  - (d) One seed s for every anchor's EM.
  - (e) P2 and P7 scored per re-draw; M4 NA for V_A; the census fit sizes pinned.

  Then the engine-coder sets `VA_RULINGS` (a new blob) and a delta READY follows.
- **N2 HIGH: arm (c) is missing.** Fix: either build it, with a pre-data bracket fixing "merged into their nearest neighbour after convergence" (neighbour by the cosine of the component means; members re-assigned without a refit, or with a refit), or record a pre-data registrar bracket deferring or striking arm (c) with its reason. The outcome must not omit a registered arm silently.
- **N3 HIGH: the selftest does not pin the readout wiring (RV1-RV9 survive).** Fix:
  - FG-E2E asserts values, not presence. For the replica, recompute independently from the written state:
    - `paired["V0"]["d1"] == mean(per1_T - per1_V0)`;
    - spread_V_A over A0-A4;
    - `va["T"]` is A0 minus T;
    - the discordance against V0.
  - A replica with one injected fit/EVAL exact overlap must make `run()` REFUSE.
  - One partition with a foreign script identity must make `analyze()` REFUSE.
  - Both V_A rulings must change the cells (heldout_anchor, and routed filing).
  - K0 must differ from V0 in st_render's synthetic readouts.
- **LOW:**
  - The SE formula label (section 2).
  - The reachability print (section 2).
  - The measured_cpu docstring (row 14).
  - The `run_dir` string depends on the DATA_ROOT spelling (row 12): run from main with TAXOARENA_DATA_ROOT unset.
  - The machine-cap breach (row 18).
  - The mix_lrt_site selftest needs TAXOARENA_DATA_ROOT in a worktree (row 10, known).

## 5. Merge and run procedure

1. **Merge now (optional, tools only):** in the main checkout, check out the three paths from 4b3489e by pathspec and verify each against the pins table (`git hash-object`). Then `git commit -- tools/analysis/flat_generality.py tools/analysis/flat_mix_mmlu.py tools/analysis/mix_lrt_site.py` and `git merge-base --is-ancestor <prev HEAD> HEAD`. After the merge, the FLAT-MIX-MMLU outcome is reproduced from `git show c5cc7934...:tools/analysis/flat_mix_mmlu.py`, not the working file. Mark queue MIX-FLAT-SELFTEST-GAPS done at the registrar.
2. **Pre-data bracket** (N1, and N2 either way), by the registrar, before any code change.
3. **Engine-coder:**
   - set `VA_RULINGS`;
   - arm (c) per the bracket;
   - the N3 tests, which must kill RV1-RV9;
   - the LOW fixes;
   - a new blob, and FLAT_MIX_PIN unchanged if flat_mix_mmlu.py is untouched.
4. **Data-steward:** the 9073a8a-form CK-CLOSE check on pd610c9a / p19d9f47 / p8a29 (W0 RP02), with sentinels in the key set. Until it passes, the re-draws stay "id-disjoint only".
5. **Delta READY:**
   - pins;
   - selftest and mutants, the reviewer's included;
   - `--dry-run` pins equal to this review's (embeddings n = 39,631 / queries n = 31,986 / eval_results n = 560,379; five graph sha256 and five dag_snapshots sha256 as in flat_generality_dry_run.log);
   - **`--identity-check` must print REPRODUCED (M1 0.727 [0.712, 0.741], M2 +12.785); a miss is a READY defect.**
6. **Run** (run-operator):
   - from the MAIN checkout after the merge;
   - no construction or W-window open, and the rule-7 exclusive-open probe FREE;
   - a single Python process, BLAS 1;
   - `--dry-run`, then `--run` (chunked, write-once), then `--analyze` once.
7. **Post-run review:** re-measure m-bar and n_eff from the EVAL twin groups, and print the MDE beside each D1 / A1 / A2 statistic.
