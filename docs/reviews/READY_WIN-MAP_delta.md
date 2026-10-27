# Delta READY review: WIN-MAP fix 43ff4f09 (after the blocked review 12f42190)

Scope: `git diff 12f42190..43ff4f09` (one file, `tools/analysis/win_map.py`, +137/-10) plus regression. Reviewed blob
`tools/analysis/win_map.py` blob:74f2e234d74291ba0e453da90fb81eff94afe8d4 (LF, of record; `git hash-object` = `git rev-parse
43ff4f09:...`); working-tree CRLF rendering sha256-crlf16 9dcc3f1805f79291 (the script's own PIN line). Was 62b88e52.
Everything the review 12f42190 CONFIRMED on code the delta does not touch (criteria, R1 471/427, denominators 5,907/5,404,
no text in the release, Support arithmetic, zero calls) is cited, not re-derived. Zero calls; one real --dry-run (busy.ps1 exit 1).

## VERDICT: READY (both blockers closed), conditions C1-C3

## Per-claim table (deciding claims of the delta)

| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| 1 | selftest 10/10 | CONFIRMED | scratch sandbox re-run: 10/10, rc 0 | - |
| 2 | 72/72 mutants KILLED, control survives | CONFIRMED | `--mutants` re-run: "72 of 72 KILLED; control survived; survivors none" (72 KILLED lines + summary, counted with grep -c) | - |
| 3 | B1: reviewer R2/R3/R4/R8 now killed | CONFIRMED | prior reviewer script re-run with ALL = the 10 CASES (incl. rs2): R2 KILLED [rs2], R3 KILLED [rs2], R4 KILLED [e2e, unstable, luck, refusals, branch_cover], R8 KILLED [branches, branch_cover]; R1/R5/R6/R7 still KILLED | - |
| 4 | rs2 family discriminates BH q 0.05 vs 0.10; region 0 STABLE, BH-rejected, 15/25 -> no caption | CONFIRMED | read st_regions_rs2: p = {1/2000, .025, .035, .07, 1/2000}; m=5, sorted .0005 .0005 .025 .035 .07: q .05 thresholds .01-.05 -> rank 4 (.035 <= .04) is the largest, rank 5 .07 > .05 -> rejects {0,1,2,4}; q .10 -> .07 <= .10 rejects all 5. Assertions are against an independent plain-loop BH | - |
| 5 | W-C MMLU refusal non-vacuous on the REAL data | CONFIRMED | the guard keys on E["meta"][i][1] = side.stratum_source; real side export: stratum_source of every MMLU item is `MMLU_PRO` (EVAL 3,492 / TRAIN 7,001 / GATE 1,157; no `MMLU_PRO_LB` row), in MMLU_NAMES; corpus source in the chance table `MMLU_PRO MC 11641` (real dry-run). So mm_ev > 0 on the run and mm_mc = mm_ev is expected | - |
| 6 | B2: winner null unless caption_licensed; argmax moved to eval_argmax_descriptive | CONFIRMED (code) / PARTLY (tests) | export L1063-1067 uses the consensus winner r["win"] under cap; e2e/unstable assertions read. Own mutant N2 (licensed winner = own argmax instead of consensus) SURVIVES: fixture has own == win in every licensed region | D-1 |
| 7 | Data object / denominators unchanged | CONFIRMED | real dry-run: POOL first, rc 0; gen/eval view sha EQUAL before/after; EVAL 5907/5404; twins 471/427; scored-EVAL twins 0; map 20108 (EVAL 6038, GATE 1986, TRAIN 12084) = the 12f42190 lines; multicorpus_cache_v1.db sha256 ad66e30a0eb4abd6 before = after | - |
| 8 | Import pins | CONFIRMED | dry-run PIN lines and `git rev-parse main:tools/analysis/<f>.py`: union_cells_io 92a04543, union_af_route bf3f17db, v2_declared_cells f0f56805, cell_flips 998d39a7 (main = branch) | - |
| 9 | Insertion-only docstring edits; D-3, D-6 fixed | CONFIRMED | diff: docstring hunks are pure `+` brackets; README benchmark "the corpus source: MMLU_PRO, ..."; item_id membership note | - |

Own mutants (in-memory, all 10 cases, scratch sandbox):
N1 W-C MC count `>= 0` (guard vacuous): KILLED [refusals] (decisive, W-C).
N2 licensed `winner` = P0's own argmax instead of the 20/25 consensus winner: SURVIVED (release column; not a criterion; D-1).
N3 licence = STABLE-MAP only, RS2 caption ignored: KILLED [e2e] (decisive, B2).

## Defects

- D-1 MEDIUM (test gap, release path; code correct as read). No fixture region is licensed with own argmax != consensus
  winner, so N2 survives. Fix: in rs2 or e2e, one licensed region where P0 is among the <= 5 dissenting partitions
  (own != win); assert the exported winner = models[win]. Not blocking: the B2 rule (null unless licensed) is guarded by
  B2a/B2b/N3, and the shipped column is read correct at L1066.
- D-2 LOW. Comment at L195 calls `MMLU_PRO_LB` "the stratum label"; the real side export's stratum_source is `MMLU_PRO`
  (`MMLU_PRO_LB` appears only in the k_cells header k_per_source). Harmless (both names are in MMLU_NAMES); fix the comment.
- D-3 LOW. The W-C MMLU EVAL line is printed by --run only (dry_run never calls the guard). The operator checks on the run
  that "MMLU items N, of them MC N" has N > 0 and the two equal; a mismatch is a stop, not an outcome.
- D-4, D-5 of 12f42190 (BBH free-form class empty; RS2 in-sample challenger) still to be disclosed in the outcome (no code).

## Conditions

C1 Merge by path: branch lacks main (ancestor 375cbcc9 confirmed in main); main has no win_map.py (`git ls-tree main` count 0);
   diff 375cbcc9..43ff4f09 = win_map.py + READY_WIN-MAP.md (+ this file) only. Check `merge-base --is-ancestor` after.
C2 busy.ps1 exit 1 immediately before --run (rule 7). C3 D-3's W-C line read on the run's log before the outcome is cited.

## Commands (read-only; zero calls)

```
git -C <wt> diff 12f42190..43ff4f09 -- tools/analysis/win_map.py ; git -C <wt> hash-object tools/analysis/win_map.py   # 74f2e234
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --selftest   # 10/10
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --mutants    # 72/72 KILLED, C00 survived
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/wm_delta_rev_mut.py    # R1-R8 KILLED, N1/N3 KILLED, N2 SURVIVED
python - (side export REG_ARCHV2-SPLIT-2_..._side.tsv: Counter((side, stratum_source)) for MMLU*)  # only MMLU_PRO
powershell -File E:/TaxoArena_tmp/busy.ps1 (exit 1); python tools/analysis/win_map.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
   # rc 0; log E:/TaxoArena_tmp/wm_delta_dry.log; view shas EQUAL; cache sha ad66e30a0eb4abd6 before = after
git merge-base --is-ancestor 375cbcc9 main ; git ls-tree main --name-only tools/analysis/ | grep -c '^tools/analysis/win_map.py$'  # 0
```

## Run command (after the merge, from main)

```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1    # must exit 1
python tools/analysis/win_map.py --run                    # ~30-60 min; outcome + release write-once; back up to E:
```
