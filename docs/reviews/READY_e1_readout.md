# READY review: E1-ROUTE / EMBEDDER-CROSS-FLAT E1 readout (tools/analysis/e1_readout.py)

Adversarial-reviewer, 2026-10-02. Zero calls. Branch e1-readout, tip d7906d5e (parent 40d4b6cd, `merge-base --is-ancestor` OK;
the commit touches 1 file, counted with `git show --name-only | wc -l`; 0 of application.yml / .env / .gitignore). Reviewed blob
**blob:88f7990c** (LF, = `git rev-parse d7906d5e:tools/analysis/e1_readout.py` = `git hash-object` of the working file; working tree
LF, 0 CR bytes) / sha256-lf16:e3494d10ebc1294b / sha256-crlf16:db5987d7ece3adce (a computed rendering, not in any tree). The 7 imported
modules' LF blobs equal main 40d4b6cd and main 502191e7 (no tools/analysis change in 40d4b6cd..502191e7, counted). Registration:
EMBEDDER-CROSS-FLAT L21705-L21730 (E1-minimal + C-E1R-4, E1 criteria, READING TABLE, SUPPORT, P3/P4, F-E1 at L22177); FLAT
criteria FLAT-MIX-MMLU L20672-L20735; D-PR-1 bracket in E1-ROUTE C3 (L22192); POSTRUN_e1_route_builds.md (ba32fbc6).

## VERDICT

**READY-WITH-CONDITIONS for `--run`** (`--dry-run` on a scratch copy executed here, rc 0). `--run` may start only after:
- **P-1 (precondition, AUTHOR / data-steward):** checkpoint of `mmlu_pro_dataset_cache_v2.db-wal` (C-PB-1; 8,272 B, sha256-16
  77dc05a4907a3d5f, unchanged by this review). Not a defect: `--run` is fail-closed on it (pool_guard.open_ro refuses a non-empty -wal).
- **R-1 (MEDIUM, registrar, PRE-DATA):** one bracket recording D1, D2 and D5 as the readings of record (below), before any E1 number exists.
- R-2..R-4 LOW (below) do not gate the run.

## Per-claim table (deciding claims)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| 1 | fit 8,125 | own read of snapshots.db (immutable): root region of 20261002_035009 / _035237 / af 20260917_201353 = 8,125 ids each -> 8,125 distinct texts via main queries, 0 unresolved; the three text sets EQUAL, sha256-16 7a7cd5d7113427b9 (= script) | CONFIRMED | - |
| 2 | held-out 3,445 | own count of reserved_pool_frozen_p2dca.json: 3,599 ids, 3,445 judgeable (>0), 154 sentinel; script: 3,445, 3,445 twin groups, Kish m-bar 1.0000 | CONFIRMED | - |
| 3 | keyed 10,925 | dry-run (free_tests_f4_f7.keyed_questions, pinned blob:f0749d61, on the scratch copy): 10,925. Spot only: same pinned instrument, not an independent count | CONFIRMED (spot) | - |
| 4 | filing 3,445 paired | n = len(held-out hits) (code: `mcnemar` n = len(hn)); dry-run "FILING n = held-out 3445 paired"; selftest ST-A asserts n = held-out, not b + c (M05 killed) | CONFIRMED | - |
| 5 | k 84 / 77 / 82 | own count of childless nodes: 84 (148 nodes), 77 (148), 82 (151); script equal; 64 / 71 split sites = 148 - 84 / 148 - 77 | CONFIRMED | - |
| 6 | `--selftest` 42 | re-run: "SELFTEST PASSED (42 checks)" | CONFIRMED | - |
| 7 | `--mutants` 25 | re-run: "MUTANTS 25 of 25 KILLED" (each with its failing check) | CONFIRMED | - |
| 8 | guard discriminator refuses | dry-run: N-raw tree on nomic_card min **0.9603** (n00000052, median 0.9701) -> REFUSE; own numpy recompute (all internal nodes, unit 256-slices, by text): min 0.96026 (64 sites), N-card tree on raw 0.96311; own arms 0.99974 / 0.99991 ADMIT (script 0.9997 / 0.9999). Refuse branch EXECUTED by my mutant R1 (discriminator fed the raw blobs -> "REFUSED: the guard admits ... does not discriminate") | CONFIRMED | - |
| 9 | no working copy / validation/ read | source: `e1_route_work` occurs only in the docstring (grep); vectors only via EA.open_arm_reader on experiment_results/embedder_cross (printed path = pinned DIR file, sha = pin); run dirs read: diagnostics/run_manifest.json, diagnostics/config.toml, dag_snapshots.jsonl (consensus_tree.last_snapshot); "validation" in the 6 imported modules: 1 docstring line + 1 print string, no path; ST-F asserts no quoted validation path. Working copies' sha256 + mtime (12 files incl. -wal/-shm) equal before / after | CONFIRMED | - |
| 10 | `--eval-db-copy` dry-run-only, originals untouched | `--run --eval-db-copy` REFUSED in main() before any read (executed); load_real(run_mode=True) refuses (ST-F); an existing target file / the data root REFUSED (executed). Originals: sha256 + full-iso mtime of the corpus DB, its -wal and -shm, main embeddings_cache.db, snapshots.db, both pinned nomic arms: IDENTICAL before / after (two diffs, after the dry-run and after my mutant dry-run); 0 sidecars beside the arm files; no e1_readout_* written | CONFIRMED | - |
| 11 | criteria = FLAT's verbatim | compute() calls flat_mix_mmlu.criterion (`diff > spr and lo > 0`) / loss (`diff < -spr and hi < 0`), spread = max - min over V0-V4, comparator V0, twin bootstrap seed of record: matches L20672-L20735 | CONFIRMED | - |
| 12 | Support (filing) | DEFF 1.0 MEASURED (3,445 singleton groups); n_eff 3,445; SE sqrt(0.15 / 3,445) = sqrt(4.354e-5) = 0.006599 -> 0.00660; MDE80 2.80 x 0.006599 = 0.01848 -> 0.0185; P4 \|-0.04\| > 0.0185 SCOREABLE; the script prints realised SE / MDE80 beside and the tightening-only tag | CONFIRMED, NON-VACUOUS | - |
| 13 | FLAT-GENERALITY k | file LF sha256 ffcb416d… (= pin; blob:cbbd2f6b tracked), L81 "D2: the loss appears in 2 of 3 qwen3 re-draws (L1_r fired: af_s137, af_s42_o1)"; FLAT-GENERALITY.json k = 2 on M1 only | CONFIRMED | - |

## Rulings on the builder's declarations (docstring D1-D7)

- **D1 (flatLeaf top-1 = FLAT's M1 per question, majority from the 8,324 readout train texts): ACCEPTED; PRE-DATA BRACKET NEEDED.**
  It is the record's meaning (ANCHOR-FREE instrument, L4289-L4291: flatLeaf rule, leaf majority TRAIN category, held-out top-1), but
  the E1 line never defines it and E0b's D2 ruling (C-E0B2-1) made "M1'" (fit-text majority) a competing reading. It defines F-E1's
  observable, so the registrar fixes it before data. Each tree in its own embedder (N-raw nomic, af_clean_s42 qwen3) is implied by the
  trees' vmfMu spaces and is printed by the script; include it in the same bracket.
- **D2 (Wald paired interval decides; exact McNemar p and bootstrap beside): ACCEPTED; PRE-DATA BRACKET NEEDED (MEDIUM).** "Paired
  McNemar interval" admits Wald, exact-conditional and score forms; they agree to the 4th decimal at n 3,445 except near 0, which is
  exactly where FILING's verdict and F-E1 are decided. Wald is the form Support (d) plans (sqrt(d / n)); the bracket must also say the
  exact p never decides when it and the interval disagree.
- **D3 (N-card's M1 majority from the 8,242 train texts with a card vector): ACCEPTED; NO pre-data bracket needed.** N-card scores
  nothing (never F-E1 / P3 / P4 / P7 / reading table: code + M04 / M24). Dry-run: 82 missing card texts (sha256-16 83fa072c0ee12b2c),
  all train-only (any fit / held-out / keyed miss REFUSES; N-raw misses 0 and has no allowance). The registrar records N-card's FLAT
  and FILING numbers with the label "D3 majority, 8,242 of 8,324; not FLAT verbatim" at the outcome.
- **D5 (P4 endpoints inclusive): ACCEPTED; PRE-DATA BRACKET NEEDED (LOW).** Only the 0.00 endpoint is reachable (b = c); -0.08 is not a
  multiple of 1/3,445. A scoring convention for a registered prediction is fixed before data.
- D4, D6, D7: accepted as stated (unregistered measures not computed; tie conventions / wrong(established) not applicable to 0/1 hits
  with no model pairs; ARI and root axis descriptive).

## Own mutants (4; deciding paths and guards)

- R1 discriminator fed the raw blobs (should ADMIT) -> dry-run REFUSED "does not discriminate": KILLED; decisive (item 8's refuse branch).
- R2 hygiene refusal disabled -> selftest PASSES: SURVIVED; not decisive (real counts 0 / 0 / 0 in the dry-run).
- R3 post-run pin after-check disabled -> selftest PASSES: SURVIVED; not decisive (R-3).
- R4 D3 allowance applied to the PRIMARY too -> selftest PASSES: SURVIVED; not decisive (N-raw misses 0 in the dry-run; R-4).

## Defects / conditions

- **R-1 (MEDIUM, registrar, pre-data):** bracket D1 (incl. own-embedder reading), D2 (Wald decides; exact p beside, never deciding)
  and D5 (inclusive endpoints) into the E1 line, before `--run`.
- **R-2 (LOW, registrar, at the outcome):** the READING TABLE sentence is printed bare; quote it with FLAT-GENERALITY's qualifiers
  (k = 2 on M1 only; af_s42_o1 not independent of af/seed_42; re-draws id-disjoint only) and state which measure N-raw's L1 fired on.
- **R-3 (LOW, builder, optional):** the pin after-check's refuse branch and the hygiene refusal are never executed (R2 / R3 survive);
  rule 11 wants both branches. Fix: a selftest leg with a pins_fn that changes one value and a fixture with one held-out text in the
  fit. Not gating: the run-operator re-hashes the inputs before / after the run (sha256 + mtime, as in item 10).
- **R-4 (LOW, builder, docstring):** ST-F's docstring claims "a fixture missing a held-out vector (D3 allowance)"; no such check exists
  (R4 survives). Fix the docstring or add the leg.
- **N-1 (note, run-operator):** under `--run`, free_tests_f4_f7.keyed_questions opens the corpus DB with plain `mode=ro` (the FLAT path of
  record); after the checkpoint it may leave a 0-byte -wal / a -shm. take_pins covers the main file only: list the sidecars before / after.
- **N-2 (note):** transitive imports (consensus_tree, pool_guard, split_side, profile_reliability, rejudge path) are not in IMPORT_PINS,
  the convention of flat_mix_mmlu / embedder_cross_flat; record their blobs at the run commit in the operator log.
- Spot difference (descriptive): discriminator median 0.9701 (script) vs 0.9698 (mine); minima agree to 4 decimals.

## Commands (bash; R = repo root, W = R/.claude/worktrees/e1-readout, S = scratchpad; TAXOARENA_DATA_ROOT=R)

```
git -C W rev-parse d7906d5e:tools/analysis/e1_readout.py; git -C W hash-object tools/analysis/e1_readout.py; grep -c $'\r' ...   # 88f7990c x2; 0
for f in <7 imports>; do git hash-object W/tools/analysis/$f.py; git rev-parse main:tools/analysis/$f.py; done       # equal
python W/tools/analysis/e1_readout.py --selftest            # 42 checks PASSED
python W/tools/analysis/e1_readout.py --mutants             # 25 of 25 KILLED (S/mut.log)
sha256sum + ls --full-iso <corpus db, -wal, -shm, embeddings_cache.db, snapshots.db, 2 arms, 12 work files> > S/before.txt
python W/tools/analysis/e1_readout.py --dry-run --eval-db-copy S/evalcopy    # rc 0; S/dry.log (68 lines)
(same) > S/after.txt; diff S/before.txt S/after.txt          # IDENTICAL (and S/after2.txt after R1: IDENTICAL)
python S/rv/indep.py      # leaves 84/77/82; fit 8,125 x3, text sets equal 7a7cd5d7; p2dca 3,599/3,445/154; guard 0.99974/0.99991; cross 0.96026/0.96311
python S/rv/mymut.py S    # R1 KILLED (dry-run), R2-R4 SURVIVED (selftest)
python W/tools/analysis/e1_readout.py --run --eval-db-copy C:/x   # REFUSED (dry-run only); existing target / data root: REFUSED
tr -d '\r' < R/experiment_results/flat_generality/flat_generality_outcome.txt | sha256sum; grep -n '^D2: the loss' ...   # ffcb416d; k 2
```
