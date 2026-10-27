# DELTA READY review w0 delta1: RP07, RP08, RP03/04, RP06, RP05, RP11 (2026-09-28)

Reviewer: adversarial-reviewer. Zero judge / Azure calls. No real-data mode (no --dry-run, --c0, --run, --analyze, --identity-check, --plan, --embed-*).
Two proof legs touched a DB: RP07's siteNull SKIP and GUARD legs, which read the rp07 WORKTREE's 4 KB stub and its snapshots_frozen.db copy. The worktree DB sha256 were equal before and after.
Main DB mtimes were unchanged (embeddings_cache / ratings / snapshots / snapshots_frozen).
All six worktrees: `status --porcelain | wc -l` = 0 after the review.
One process at a time; OMP / MKL / OPENBLAS = 1; Gradle with `--max-workers=2` and `JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=12`.
Scope: `git diff <reviewed tip>..<new tip>` plus regression. The prior reviews' CONFIRMED rows on untouched code are cited, not redone.
Scratch: `scratchpad/rev_delta1/` (rp07/, rp08/, rp0304/, rp05 va_oracle.py, rp06/, rp11/).

## VERDICTS

| build | tip (delta from) | verdict | merge | run / window |
|---|---|---|---|---|
| RP07 THREAD-CAP | d09f8c8 (87c3670) | READY-WITH-CONDITIONS | MERGEABLE (1st) | B1-B3 after C7-1; B4 NOT READY until C7-2 |
| RP08 EMBEDDER-PLUMBING + arms | 1ddbdfa (5172047) | READY-WITH-CONDITIONS | MERGEABLE (2nd, resolve conflict R-M) | P-1/P-2 window and embedder_arms `--go` NOT READY until C8-1..C8-3 |
| RP03/04 v2 readers | db10f08 (b31c31d) | READY-WITH-CONDITIONS (tool only) | MERGEABLE (any order) | NOT READY: preconditions None by design; C34-1, C34-2 |
| RP06 CERT-REDRAW-R512 | 3152d15 (73e5a04) | READY-WITH-CONDITIONS | MERGEABLE (any order) | `--run` after C6-1 |
| RP05 FLAT-GENERALITY | 2650b34 (731cbbe; rebased on RP08) | **NOT READY** | NOT MERGEABLE at this blob (B5-1) | none |
| RP11 STAGE0b + DATASET-SURVEY | 505b34b (8c1e54d) | READY-WITH-CONDITIONS (tool only) | MERGEABLE (any order) | NOT READY: C11-1..C11-4 |

**MERGE ORDER.**
1. RP07.
2. RP08. `build.gradle.kts` conflicts at the siteNull block, and the conflict is the only one. Resolution R-M: keep BOTH hunks, `applyThreadCap()` then the two `embeddingCacheFile` / `embeddingModel` forwards. Result: blob:226229c99caa3a8eebbc28268fb7acfd26329f45 (sha256-lf16:a26a6bb51d816206).
   - `SeparationNullBySizeTest.kt` auto-merges to blob:b11986ad9563773a9f344b39ea5ba70f0cac41d3. The H2 print stays the FIRST statement, ahead of the RP08 lines.
   - After the merge: full suite, expect 453 + RP08's tests with the 2 known env failures; then RP07's `run_proof_delta.sh`.
3. RP03/04, RP06, RP11 in any order (disjoint paths; main has touched none of their paths since their bases, counted per branch = 0).
4. RP05 last, only after B5-1 is fixed and a delta re-review is done (it carries RP08's commits; merge RP08 first).

Merge each by path, then `git commit -- <paths>` and `merge-base --is-ancestor <prev HEAD> HEAD`.

## PER-CLAIM TABLE (deciding claims only)

| # | claim (builder) | verdict | mine vs claimed | sev |
|---|---|---|---|---|
| 7.1 | H1: ProcessAot / ProcessTestAot capped; absent flag inert (I0 over 4 tasks) | CONFIRMED | proof 13/13 OK; I0 8 lines identical to 4f5e03d; PAOT12 `requested=12 availableProcessors=12` executed | - |
| 7.2 | H2: siteNull line printed on skip paths | PARTLY | printed on the snapshot-skip path (SKIP-line OK, skipped=1). The FIRST Assumption path (no embeddings_cache.db) has no leg: reviewer mutant Y1 (print moved after the first assumeTrue) SURVIVES | MEDIUM (C7-1) |
| 7.3 | mutants 8/8 | CONFIRMED | X2-X9 8/8 KILLED; Y1 survives (above) | - |
| 7.4 | suite 453 / 2 env failures | CONFIRMED | 453 tests, 2 failed: MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest (the known two) | - |
| 7.5 | M2 "ruled route (ii)" | REFUTED as a record claim | `grep -c 'route (ii)\|ollama_affinity' docs/judge_v2_program.md` = 0; R1-R5 and (a)-(c) (prog L21834-L21844) do not rule it. The script itself: -SelfTest PASS 7/7; dry run printed masks and set nothing; -Threads 25 refused | MEDIUM (C7-2) |
| 7.6 | M3 B1 reference committed byte-exact | CONFIRMED | wt sha256 aec4b517...a665 = claimed; blob:ab6929dd (git-bytes = CRLF bytes, `-text`) | - |
| 8.1 | F1 multi-site gate executed in both twins | CONFIRMED | embedder_guard selftest 37, --mutants 22/22; Kotlin EmbedderReadGuardTest 14/14 + routing 3/3 (`--rerun`, 14:21 UTC); Kotlin X1K/X2K/X4K/X6K/X7K 5/5 KILLED | - |
| 8.2 | reviewer mutants 11/11 (were 4 survivors) | CONFIRMED | rp08rev/rev_mutants.py X1-X11 all KILLED; reviewer Y8-A (NaN site dropped from the min) KILLED | - |
| 8.3 | F3 fit_set reads the configured cache | CONFIRMED | X10 KILLED; flat_mix_mmlu selftest 91, --mutants 39/39 | - |
| 8.4 | embedder_arms (new): only --go posts or writes | PARTLY | selftest 18, mutants 12/12. Reviewer mutant Y8-D (embed_card ignores --go) SURVIVES: the card path's dry gate executes in no check | MEDIUM (C8-2) |
| 8.5 | R2 is what is built; A2 / A3 / L3 / F4 | UNDETERMINED | R2 is built as ruled. A2, A3, L3 and F4 are still unruled (prog L21841 "owed") | cond. C8-1 |
| 34.1 | D1: key scope filtered in SQL, counted | CONFIRMED | reviewer mutants Y3-1 (leg U item filter dropped) and Y3-2 (reference variant filter dropped) both KILLED by the fetched-row count checks | - |
| 34.2 | D2: 11/11 reviewer mutants killed | CONFIRMED | original harness rev_rp0304/mut/harness.py: R1-R6, K1-K5 11/11 KILLED; selftests 75 / 22 of 22 and 44 / 14 of 14, plain and -O | - |
| 34.3 | D7: --run refuses unless threads = 1 | CONFIRMED | `OMP_NUM_THREADS=4 k46_key_read.py --run` refuses before any read | - |
| 34.4 | PLAN dict unchanged (D5) | CONFIRMED, now STALE | PLAN n=390, n_eff 195 (DEFF 2.0). The steward's census at 5572465 gives ONE key-decidable 544 in 160 components, Kish 4.934, so n_eff = 544/4.934 = 110.3, not 195. Illustrative SE at p=0.86: 0.0331 (MDE80 0.093) against the registered 0.02485 / 0.0696 | HIGH (C34-2) |
| 6.1 | R1 built: OPEN_RULINGS {}, P4 "A", UNREACHABLE words | CONFIRMED | matches prog L21840; selftest 18/18 builder mutants; reviewer X1-X12 12/12 KILLED (X4 retargeted to fwer_word: accepted) | - |
| 6.2 | H1 (X3) killed through analyze() | CONFIRMED | X3 KILLED by st4b; reviewer mutants Y6-1 (unreachable := untested) and Y6-2 (every unrejected exhibit printed UNREACHABLE) KILLED | - |
| 5.1 | R3 built: declared_label / declared_label / nearest | CONFIRMED as built; **REFUTED as sound** | V_A files EVAL rows by their MMLU-Pro category, and M1 (score_cells) scores exactly that category. Witness (synthetic, labels drawn AT RANDOM): V_A M1 = **1.0000 (210/210)**; the same fit routed label-free (leaf_ancestor) gives 0.3524 (chance 0.333) | **BLOCKER (B5-1)** |
| 5.2 | N3: RV1-RV9 killed | CONFIRMED | 9/9 KILLED (RV5 retargeted to the labels line: accepted); selftest 80, mutants 26/26; flat_mix_mmlu 97 / 43 of 43 | - |
| 5.3 | rebase onto RP08 | CONFIRMED | flat_generality.py identical 4b3489e vs 731cbbe; the flat_mix_mmlu diff-of-diffs is table_pins' signature and the assert_fit_count stub only; mix_lrt_site unchanged | - |
| 11.1 | A4b identity gate on the pinned 1,251 | CONFIRMED (list) / PARTLY (gate) | pinned list = review rv11/excl.json, 1,251/1,251 set-equal; sha256-lf 89d17b0d = EXCL_SHA256. Reviewer mutant Y11-2 (gate on counts, not set equality) SURVIVES | MEDIUM (C11-3) |
| 11.2 | B1: correctness accessed only for the A2 sample and duplicates until A6 | PARTLY | the STOP path prints no key count (selftest). Reviewer mutant Y11-1 (A1 scan reads the FULL key, key_scope=None) SURVIVES: the scope is untested, though nothing prints | MEDIUM (C11-3) |
| 11.3 | H1: mode_run executed; X1-X12 killed | CONFIRMED | 11/11 runnable KILLED (X6 retired: STAGE0b has no P1b, accepted); selftest 136/0 plain and -O; builder 18/18 both; reviewer Y11-3 (A2 drawn before exclusion) KILLED | - |
| 11.4 | STAGE0b Support (prog L21848ff (a)-(f)) | CONFIRMED | d 0.15627; SE_iid 0.004597; SE 0.005265; n_eff 5,637.2; MDE80 1.474pp; d=0.25: 0.006659 / 1.865pp; C2 0.0339 / 0.095. **But** PLAN_C1 in the script still prints STAGE0's 7,959 / 1.42pp line (sg.py L226) | LOW (C11-4) |
| 11.5 | dataset_survey validates and scores the table | PARTLY | selftest 13, mutants 4/4. It trusts the steward's status word: a SuperGPQA row with models value 12 and support value 0, both marked PASS, scores **ADMIT** (reviewer witness Y-DS1) | MEDIUM (C11-2) |

## DEFECTS AND CONDITIONS (each with its fix)

**B5-1 BLOCKER (RP05): arm (a) is a label oracle.**
- Built as `heldout_anchor="declared_label"`, which routes each EVAL and keyed question by its MMLU-Pro category. M1 then scores held-out category against cell majority, and M2 reads the same labels, so A0's M1 is 1 by construction.
- R3's words ("each question is assigned to its declared anchor") do not settle whether "question" includes held-out rows. The prior review's recommendation was TRAIN-side labels only.
- Fix:
  - an orchestrator / registrar pre-data bracket ruling held-out routing label-free (leaf_ancestor or d1_nearest), with fit filing staying declared_label;
  - VA_RULINGS re-set, and a selftest that fails when V_A's M1 on random labels exceeds chance + 0.1;
  - N1 (d) and (e) ruled in the same bracket;
  - then a delta re-review.

**C7-1 MEDIUM (RP07, before B1).** Add a proof leg that runs siteNull in a directory with NO `embeddings_cache.db`: the line prints and the test skips. Y1 must then be KILLED. After the RP08 merge, run it without `-DembeddingCacheFile`.

**C7-2 MEDIUM (RP07, before B4).** The registrar records the Ollama route (ii) (tools/ollama_affinity.ps1) in a bracket. B4 then runs its witness procedure. Also carried: M1 (other forks ignore `-PjvmThreads`, so the JAVA_TOOL_OPTIONS rule stands) and M4 (heap guard at 12).

**C8-1 (RP08, before the P-1/P-2 window).** The registrar rules A2, A3 and L3, and pre-states F4 (the score if the RIGHT embedder is refused).
- X8-K (the siteNull guard block deleted) is still killed by no test: P-2 (i)/(ii) must print the `[EMB-GUARD]` line from siteNull.
- The nomic WAL is now checkpointed in place. `ls` finds no `-wal` for nomic, 20NG or ag_news (coordinator's report of equal content not re-verified).

**C8-2 MEDIUM (RP08, before any `--embed-card --go`).** Add a selftest that `embed_card(go=False)` posts and writes nothing (kills Y8-D).

**C8-3 MEDIUM (RP08, before `--embed-missing gemma_raw --go`).** Route parity.
- The 3,520 new vectors come from `/api/embed`, while the existing gemma rows came through the engine's langchain4j route.
- Before `--go`, re-embed 20 texts already in the DB through `ollama_embed` and require cos >= 0.9999 after slice-and-renormalise. Print it.
- Also LOW: `write_vectors` opens with `sqlite3.connect._raw`, bypassing the harness's read-only patch. State this in the docstring.

**C34-1 (RP03/04, before any read).** The run is blocked until these brackets exist: the registrar's census_bracket, interval_form (K1), beta_len struck with its bracket (K2), A1 train_unit, A2 p2_measure, and D3 / D4 / D5. The steward's half is now at 5572465.

**C34-2 HIGH (RP04, before the read).** Re-derive Support (f) at the census: n = 544 in 160 components, Kish 4.934, so n_eff 110.3, not the registered 390 / 195. Then:
- the SE and MDE at the registered prediction;
- the verdict line (DESCRIPTIVE-ONLY vs SCOREABLE) re-stated;
- the PLAN dict updated from that bracket, then a delta re-pin.

**C6-1 (RP06, before `--run`).**
- D3: the steward archives the s137 / s2048 dag_snapshots.jsonl with SHA256SUMS.
- M-3: the soft instrument-check mismatch is ruled or disclosed.
- M-2 stays forward (RP50).
- LOW: st4b's `assert A == B if cond else True` is non-vacuous only because Law is an anchor here (witnessed). Parenthesise it.

**C11-1 (RP11, run).**
- M1 is owed: the two-roster contrast and the best-of-N floor print UNDEFINED. STAGE0b's own preconditions require M1 fixed, so this needs a pre-key strike or definition bracket.
- A5 (steward) and a rule-7 window are also needed.

**C11-2 MEDIUM (DATASET-SURVEY).**
- Cross-check value against status for the numeric legs: models >= 20 and support value >= 1 stratum (plus the registered per-stratum floor), else REFUSE the table. Add Y-DS1 as a mutant or check.
- The steward's table does not exist yet, so B2 is unmet.

**C11-3 MEDIUM (RP11).** Add a same-size, different-set fixture to leg_a4b (kills Y11-2). Add an assertion that the A1 scan's `key` holds only sample and duplicate uuids (kills Y11-1).

**C11-4 LOW (RP11).** PLAN_C1 prints STAGE0's 7,959 / 1.42pp plan line. Replace it with STAGE0b's (7,396 / 5,637 / 0.005265 / 1.47pp) before the run.

## PINS (blob, LF of record; sha256-lf16 / sha256-crlf16 rendering)
- RP07 d09f8c8:
  - build.gradle.kts c0506d28600244a5a6506a9f50333416b83583f8 7f0d6ffbfa473010 (wt 6e1feba2ec0300d6);
  - SeparationNullBySizeTest.kt 30c32a0a4050064c2c80c94250402079c9224d62 1f2dffcba763a39c (wt 04e27d7e09fe7064);
  - ollama_affinity.ps1 6e943572c4e4ca8fe3150f0bbd4f35a0add34e2d 28b37f171867193d;
  - threadcap/.gitattributes 1b33999c 0f5ef29dde3bb8d9;
  - reference CSV ab6929dddbbe3c579c61c730900e37dafae2d484 (bytes sha256 aec4b517...a665);
  - unchanged since 7676eab: ThreadCap.kt 812fbc6b, Application.kt dbfb2561.
- RP08 1ddbdfa:
  - EmbedderReadGuardTest.kt 9594b9d017d60da546389b37f9f0ca1fe3f8d20b 91c5d3e1d6887c7d / 3e1fec39f105c90b;
  - embedder_arms.py 6ed7c4b753a067ae81b8ecdaf768796651a7a8c7 d0d8fe016f03f239 / 89587a7e5fadcb6f;
  - embedder_guard.py 3fd9aea5b220828f7e6bcb3f115c43aa6743218d 9393c820af557fb2 / 8ee96c2aef9aef7d (equals flat_mix_mmlu's IMPORT_PINS);
  - flat_mix_mmlu.py a55e50da40f63f7fc89274428a67f79ca02db58a 4d4be38ce1cfe4ba / 7bf10f7afe0925d4;
  - EmbedderReadGuard.kt f242bc4d.
- RP03/04 db10f08:
  - k46_key_read.py 2d6347f6b1c1f70f81b9036c5426de81b491c156 95da9ff94f7f74f2 / bf17fd6522e9bfe4;
  - v2_declared_cells.py 13938c1324a64f057f237da33d225ca8cb1a561e c1e8ac08057cbe36 / d29cc44134032433;
  - v2_reader_guards.py 14d10ff8a4a03afd0e4edf4beae6281bd8c69982 9591a5b7f1ec989c / cc3c257ba69988fe.
- RP06 3152d15: cert_redraw_r512.py d611b3acbeeab2c94931e71731366b1b8b180f9f dd4c6a2347c32b6d / 918da16ae6e753b3.
- RP05 2650b34 (NOT READY; for the record):
  - flat_generality.py df785c125cacacaeddf73664fd3c3351e6158cd1 c65d464f1f8eba51 / 9def9f92eaee59e0;
  - flat_mix_mmlu.py cdb354f162605fdce0156c1363b393147203b5a9 4e5fec853e3ec463 / de095184c1c843b1 (equals FLAT_MIX_PIN);
  - mix_lrt_site.py fbb480ca (unchanged).
- RP11 505b34b:
  - supergpqa_stage0.py c1e8175ebfc6eb81486206828df06a3286557951 dd0e34dbca17623d / 0377c1a276d8c192;
  - dataset_survey.py 696154e8502f9bdbffe3e40857ce2d62c558b4c4 40e05526391d0642 / c2083bac52f39b0f;
  - stage0b exclusion json 11839fa36aad567acfd1d3ed7e2c7ffc9b261a21 89d17b0df027728e / 6f4b62d099495a43.

## REVIEWER MUTANTS (12 of mine, on deciding paths)
- RP07:
  - Y1: siteNull print moved after the first assumeTrue. SURVIVED. Decisive for H2 "every run".
- RP08:
  - Y8-A: min over finite sites only. KILLED.
  - Y8-D: embed_card ignores --go. SURVIVED. Decisive for write safety.
- RP03/04:
  - Y3-1: leg U SQL without the item filter. KILLED.
  - Y3-2: reference SQL without the variant filter. KILLED.
- RP06:
  - Y6-1: unreachable := untested. KILLED.
  - Y6-2: every unrejected exhibit reads UNREACHABLE. KILLED.
- RP05:
  - Y-VA: witness, not a mutant. The shipped rulings give M1 = 1.0000 on random labels. Decisive.
- RP11:
  - Y11-1: A1 full key read. SURVIVED. Seal scope.
  - Y11-2: A4b on counts only. SURVIVED.
  - Y11-3: A2 sample before exclusion. KILLED.
  - Y-DS1: PASS status with a failing value ADMITS. Witness.

## COMMANDS (compact)
```
sh rev_delta1/rp07/run_proof_delta.sh ; sh rev_delta1/rp07/run_mutants_delta.sh      # 13/13 ; 8 killed + Y1 survives
JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=12 ./gradlew.bat test --offline --no-daemon --max-workers=2   # rp07: 453, 2 known
powershell -File tools/ollama_affinity.ps1 -SelfTest | -Threads 12 | -Threads 25
python tools/analysis/{embedder_guard,embedder_arms,flat_mix_mmlu}.py --selftest/--mutants ; python rp08rev/rev_mutants.py ; python rev_delta1/rp08/my_mut.py ; sh rev_delta1/rp08/kt_mutants.sh
python [-O] tools/analysis/{v2_declared_cells,k46_key_read}.py --selftest ; python rev_delta1/rp0304/harness.py
python tools/analysis/cert_redraw_r512.py --selftest ; python rev_delta1/rp06/mut.py
python tools/analysis/{flat_generality,flat_mix_mmlu}.py --selftest/--mutants ; python w0_logs/rp05-flat-generality/rev_mut_copy.py ; python rev_delta1/va_oracle.py
python [-O] tools/analysis/supergpqa_stage0.py --selftest/--mutants ; python rev_delta1/rp11/mut.py <wt> <dir> ; python tools/analysis/dataset_survey.py --selftest/--mutants
git merge-tree --write-tree d09f8c8 1ddbdfa    # sole conflict build.gradle.kts siteNull block
```
