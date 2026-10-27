# READY review: FITSET-INTENT (adversarial-reviewer, 2026-10-03; zero calls)

Reviewed: branch fitset-intent tip 33fb11cb; `tools/analysis/fitset_intent.py` blob:eaa29686f0e783d0d6e8d59797e36a2a3e74f1f4
(LF; `git hash-object` in the worktree, which holds the LF rendering; sha256-lf16:ecdb86ed2baf11d9, sha256-crlf16:5ac77a91d04a5914).
Instrument pins re-hashed: intent_transfer_s1.py blob:4e9d9d05, fitset_faithful.py blob:ed343065 (= the registered blobs).
Registration: docs/judge_v2_program.md L23888-L23899 (d50c47d4). Prior reviews relied on: POSTRUN_fitset_faithful.md
(the refit rule, v_ff1, DEFF 1.052), POSTRUN_intent_s1.md (S1's readers, the AN snapshots, the printed identity numbers).

## Verdict: READY, with conditions C-1..C-3; registrar brackets B-1..B-3 owed before the outcome is recorded

## Per-claim table (deciding paths)

| # | claim | result | mine | sev |
|---|---|---|---|---|
| 1 | A-refit fit sets are TRAIN only | CONFIRMED | own check: every fit index has side TRAIN (M-AN 9,870, C-AN 13,487 rows); script's fit audit 32 fits = 2 arms x (TRAIN + GATE of phase_gate) + 18 + 10 refit fits; the GATE entries are S1's descent/delta_c GATE reads, not refit sets | - |
| 2 | fit sets class-pure (declared coarse class of the anchor) | CONFIRMED | own check: each anchor's set = TRAIN rows with coarse == the anchor's class (anchor label = pretty(coarse), bijection 18/18, 10/10); sets partition TRAIN (sum 9,870 / 13,487 = TRAIN) | - |
| 3 | 2 C-AN leaves receive no item | CONFIRMED | own nearest-leaf-in-anchor assignment: C-AN 2 leaves, n00000154 and n00000353 (= the dry-run's list, Banking and Small Talk 0); M-AN 0. Every anchor is split (18/18, 10/10), so the unsplit-anchor branch never runs on real data | - |
| 4 | bar = in-run k-means spread | CONFIRMED (code) | spread_K = max - min over seeds 0-4 of fine filing precision of S1.phase_gate's own TRAIN k-means at k = L (S1.SEEDS20 = range(20), need_km only at --run); named and filed by the same R3 rule as A. delta_c identity (S1 printed 0.01966 / 0.01414) ties these fits to S1's | - |
| 5 | FI1 form = registered | CONFIRMED | DSC.v_spread: HELD iff lo > 0 AND D > spread_K; REVERSED symmetric; UNDETERMINED else; F-FI iff both corpora UNDETERMINED/REVERSED; BEYOND-MMLU iff >= 1 HELD | - |
| 6 | Support (d)/(e) arithmetic | CONFIRMED | sqrt(0.06 x 1.052 / 4,946) = 0.00357, / 6,672 = 0.00308; MDE80 2.8 SE = 0.0100 / 0.0086; n_eff 4,702 / 6,342. DEFF source: FITSET-FAITHFUL measured 1.052 (POSTRUN #7). Measured DEFF, Kish, n_eff, MDE printed beside FI1 at --run | - |
| 7 | denominators | CONFIRMED | dry-run census MASSIVE 4,946 / 4,923, CLINC 6,672 / 6,672 = registered; re-enforced on FI1's own n / G at --run | - |
| 8 | Deviation (2): identity via S1's printed numbers | CONFIRMED necessary; adequate | s1_items.csv arms {M-AF 4,946, C-AF 6,672}, 0 AN rows (full-file count); sha256 a25c6227 / 0c52a9c3 = script pins. Substitute: Snapshot ID + leaf count + descent ACCEPTED + D_fd, D1, delta_c to 5 dp + P(A) == S1.t_c8 P_flat (1e-12). Not item-level: a flatLeaf change offset in all three aggregates would pass (implausible; deterministic code on pinned snapshots) | MEDIUM (bracket B-1) |
| 9 | Deviation (3): confounds builder-worded | CONFIRMED as disclosed | the registration names none; the three printed are FF W-3 adapted and marked "builder's wording"; content correct | LOW (bracket B-2) |
| 10 | write-once | CONFIRMED | lexists refusal on --run before the java probe and every read; open mode "x"; builder M19-M21 killed | - |
| 11 | java refusal | CONFIRMED | probe (S0._foreign_heavy, any java.exe) refuses before any read in both modes; it refused the builder's dry-run (commit) | - |
| 12 | --data-root flag | CONFIRMED | `ap.add_argument("--data-root")`, `data_root = a.data_root or S1.DATA_ROOT`; real dry-run with the flag and TAXOARENA_DATA_ROOT UNSET printed the intent-s1-run root and PIN OK | - |
| 13 | no writes to DBs | CONFIRMED | sha256-16 and mtime of intent-s1-run snapshots.db, intent_emb_qwen3.db, intent_transfer_corpora_v1.db equal before/after the dry-run + own check; snapshots.db-wal 0 B | - |
| 14 | selftest / mutants | CONFIRMED | --selftest 6/6 rc 0; --mutants 50/50 KILLED, control survived (re-run) | - |

## Own mutants (deciding paths)

- R1 fit set = all TRAIN of the corpus (class purity removed): KILLED (e2e_UH, e2e_RZ). Decisive.
- R2 refit cells keep A's names (no TRAIN re-naming): KILLED. Decisive.
- R3 READING counts REVERSED as HELD: KILLED (e2e_RZ, branches). Decisive.
- R4 java probe on --run only (dry-run beside a java): SURVIVED. Not decisive (code correct; test gap, D-1).
- R5 --data-root ignored (env only): SURVIVED (selftest stubs the loader). Not decisive; the flag is proved by the real dry-run (#12).

## Conditions

- C-1 Run with NO java.exe alive, idle Gradle/Kotlin daemons included (the probe refuses on any; a daemon of another worktree
  is waited out, never killed). Plain-form launch, from the fitset-intent worktree (or main after merge), no env prefix:
  `python tools/analysis/fitset_intent.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/intent-s1-run --s1-dir Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/intent_transfer --out Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/intent_transfer/fitset_intent_outcome.txt`
  (the dry-run ran rc 0 without PYTHONIOENCODING; the outcome file is written utf-8 regardless). Precede it with the same
  command with `--dry-run` in place of `--run` and no `--out`.
- C-2 The run must print IDENTITY PASSED for both arms (D_fd +0.02467 / +0.08019, D1 +0.00714 / +0.00706, delta_c 0.01966 /
  0.01414) before any FI1 line; a refusal is a failed precondition, never an outcome.
- C-3 The post-run review re-measures DEFF from the components (MASSIVE 4,923 clusters of 4,946; CLINC singleton) and reads
  FI1 against spread_K, with the 2 C-AN no-item leaves and the low-count refit cells (C-AN leaves fitted on 1-3 items:
  Meta 1 / 2, Banking 8, Travel 6, Utility 3) as descriptive context.

## Registrar brackets owed

- B-1 (identity): bracket the registered "the as-built trees reproduce S1's flatLeaf assignments (s1_items.csv)": s1_items.csv
  holds no M-AN / C-AN rows; the identity is read through S1's printed D_fd / D1 / delta_c and P(A) = S1.t_c8 P_flat
  (aggregate, not item-level).
- B-2 (confounds): record the three confounds as the builder's wording, plus a fourth: (4) the bar is k-means' seed spread;
  A's construction-seed spread is unmeasured and A-refit is deterministic (FF W-2); DEFF 1.052 is transported from MMLU-Pro.
- B-3 (bookkeeping): C-AN 2 leaves (n00000154, n00000353) receive no declared-class item and keep their vmfMu; every anchor of
  both trees is split.

## Defects

- D-1 (LOW) the dry-run branch of the java refusal is untested (R4 survives). FIX: a refusals case with `--dry-run` and a stubbed heavy probe.
- D-2 (LOW) --data-root never exercised by the selftest (R5 survives). FIX: assert the loader receives `a.data_root`.
- D-3 (LOW) docstring LAUNCH SEQUENCE uses the `TAXOARENA_DATA_ROOT=` prefix; FIX: replace with the C-1 plain form.

## Commands

```
git ls-tree fitset-intent tools/analysis/fitset_intent.py; git hash-object tools/analysis/{fitset_intent,intent_transfer_s1,fitset_faithful}.py
python tools/analysis/fitset_intent.py --selftest            # 6/6 rc 0
python tools/analysis/fitset_intent.py --mutants             # 50/50 KILLED, control survived
python scratchpad/fir/own_mut.py                             # R0 control survived; R1-R3 KILLED; R4, R5 SURVIVED
tasklist java.exe (until none) ; python tools/analysis/fitset_intent.py --dry-run --data-root <intent-s1-run> --s1-dir <main>/experiment_results/intent_transfer   # rc 0, 15 lines
python scratchpad/fir/own_check.py      # own TRAIN-only, class-pure assignment: M-AN 0, C-AN 2 no-item leaves
python -c "csv arm counts of s1_items.csv"   # {M-AF 4946, C-AF 6672}; sha256sum s1_outcome.txt s1_items.csv
sha256sum + ls --full-iso of intent-s1-run DBs before/after   # equal; -wal 0 B
```
