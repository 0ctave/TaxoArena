# READY review: GAP-FIX-CC (`tools/analysis/gap_fix_cc.py`)

Reviewer: adversarial-reviewer, 2026-10-08. Branch `worktree-wf_fa0ebf63-18c-4`, reviewed tip 4dbb0814 (parent e83b59d5).
Registration: prog "## Registered 2026-10-08 (before any code or call) — GAP-FIX-CC: ..." L25029-L25041 (_as_of e83b59d5).
Reviewed blob: `blob:b83d279082c74f8f76f4a6f0924baa59e35b286e`, LF of record `sha256-lf16:b36fb63ad5df80a7`, CRLF beside
`sha256-crlf16:3f185ebd2f42a77f` (the working tree is LF: 0 CRLF pairs; `git show HEAD:<path> | git hash-object --stdin` = the same blob).
Zero calls: no judge, LLM, embedding or network call; no DB written; nothing run on real data by this review.

## VERDICT: READY (no blocker), with the conditions C-1..C-4

`--nomic-leg e1-guard` (ruling on the registration's EMBEDDER GATE): the nomic leg runs through `e1_split_draws.check_tree`, which
is the E1 readout's own-embedder path with its [EMB-GUARD] vmfMu check and both discriminators. It is the path E1-SPLIT-DRAWS
(VALID 285589ba) used to read these same six trees: its outcome shows ADMIT on the trees' own vectors and REFUSE on both
discriminators for N-raw, N_e1sd1 and N_e1sd2. The V fits read the same `E1R.load_space("nomic_raw")` vectors that the guard
checks. The registration names this path as sufficient ("or after the RP08 merge"), so `not-run` is not required.

## Per-claim table (deciding claims)

| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| 1 | GF1 per tree = GAP-FIX's clause, unchanged | CONFIRMED | `tree_stats` calls `GF.gf1(D_R, UB(D_R), I_R, LB(I_R), bar)` from gap_fix.py blob 7c0691e8 (verified unchanged: `git hash-object` = 7c0691e8); D_T = T-V0, D_R = WP_5-V0, I_R = WP_5-T, I_0 = WP_0-T, I_P = WP_5-WP_0 match the registration's text | - |
| 2 | bar = max(own MDE80, own spread_V over V0..V4) | CONFIRMED | MDE80 = 2.8 sqrt(disc(D_R)/n) (registration Support (e) form, "its own MDE80 from its measured discordance"); spread includes V0 (C-PLANT R11, M08) | - |
| 3 | GAP-SHOWN iff UB(D_T) < 0; NO-GAP not counted | CONFIRMED | `gap = dt["hi"] < 0`; `aggregate`/`closed_refuted` count GAP-SHOWN only; plants at UB exactly 0 | - |
| 4 | GF1-CC: word on >= 2 GAP-SHOWN qwen3 trees; NOT EVALUABLE < 2; MIXED | CONFIRMED | `aggregate`; the CC list is filtered by leg "CC" only, and GF1-N by leg "N" (N_e1sd1 = N1, never counted) | - |
| 5 | F-GFC fires iff GF1-CC CLOSED and LB(I_P) > 0 "on those trees" | PARTLY | Code reads it as all GAP-SHOWN CLOSED trees (B-3) and prints "m of c". The consequence text says ">= 2 of 3", which supports the other reading. Ambiguous pre-data, so the registrar decides: C-1 | MEDIUM |
| 6 | Denominators 3,598 / 3,522 / 3,500; nomic 3,445 / 3,522 / 3,500; leaves 80/87/72, 84/80/71, 28 | CONFIRMED | `REAL_TREES` equal to the registration. The leaf counts match `e1sd_readout_outcome.txt` L14-L20 (sha256-16 052dfcd16a153d86). [GFC-N] / [GFC-LEAVES] refuse on a mismatch | - |
| 7 | I-1 top-1 values of record | CONFIRMED | Rebuilt from E1-SPLIT-DRAWS.json numbers of record: G1 0.5545-0.7268 = -0.1723, G2 0.6860-0.7354 = -0.0494, G3 0.6503-0.7297 = -0.0794, spread_Q 0.0086, spread_N 0.1315. All five agree to the digit; N-raw 0.6813 is the IDENTITY value | - |
| 8 | No EVAL leakage | CONFIRMED | V fits and refinement on X = the fit set only; z0 from leaf_mu on the fit set; M1 majority from the label set (the split's TRAIN). Real-path hygiene: e1sd `e1_split_draws.hygiene` refuses on any not-TRAIN / held-out / shared-stem_key fit text, and `hygiene_core` refuses on held-out or outside-label fit texts. M29/M30/M31 killed by genuine assertion or identity refusal (checked) | - |
| 9 | Support: SE / MDE arithmetic | CONFIRMED | sqrt(0.1388/3500) = 0.006297 → 0.00630; 2.8 x = 0.01763 → 0.0176. sqrt(0.0656/3500) = 0.004329; 2.8 x = 0.01212 → 0.0121. DEFF 1.0 is transported from GAP-FIX PR-1 (Kish 1.0000; source named). The run prints the measured Kish m-bar, n_eff and per-tree discordance/SE/MDE beside the registered values (`support_lines`) | - |
| 10 | Selftest 612 / 612 | CONFIRMED | my run: `SELFTEST: 612 checks passed` (43 s) | - |
| 11 | Mutants 50 / 50 killed | CONFIRMED | my run: 50 of 50 KILLED. Kill reasons spot-checked on M14, M15, M21, M29, M30, M31, M43, M47: all are AssertionError or a [GFC-IDENTITY-GF] refusal, none a crash | - |
| 12 | Zero calls, no DB write | CONFIRMED | grep of requests / urllib / http / call_judge / openai / ollama / sqlite connect / execute / INSERT / UPDATE in gap_fix_cc.py: count 0. Writes = `write_once` (mode x) to `experiment_results/gap_fix_cc/` only. e1_readout.load_space opens via `pool_guard.open_ro` | - |
| 13 | Inertness / commit hygiene | CONFIRMED | `git show 4dbb0814 --name-only --format= \| wc -l` = 1 (the new file). gap_fix.py 7c0691e8, e1_split_draws.py 0414b8fa and flat_mix_mmlu.py 555ae3ac are unchanged (hash-object) | - |
| 14 | Runtime 5-15 CPU-min | PLAUSIBLE | One synthetic `vmf_em` (n 8,200 x 256, k 80) takes 1.3 CPU-s / 53 iterations, so 35 fits at 200 iterations max is about 3 min. Within the registered 1-2 h ceiling | - |

## Own mutants (deciding paths; 8)

| id | change | result | decisive |
|---|---|---|---|
| R1 | GF1 CLOSED on LB(D_R) instead of UB | KILLED | yes |
| R2 | F-GFC tree list drops the GAP-SHOWN filter | SURVIVED | yes (falsifier path; code correct by reading; untested branch: a NO-GAP tree reading CLOSED beside GF1-CC CLOSED) -> C-2 |
| R3 | F-GFC reads I_R instead of I_P | KILLED | yes |
| R4 | nomic-leg reset loop removed (an admitted N tree measured after a peer's refusal) | KILLED | yes |
| R5 | GF1-N FAILS line computed on the CC rows | SURVIVED | no (the GF1-N rule-8 line is scored secondary; its value is never asserted) -> C-2 |
| R6 | z0 from the reversed leaf_mu (misaligned start) | SURVIVED | no in the selftest (the fixture is symmetric between parents, and an M1 cell relabelling is invariant). In the real run, I-2 (GAP-FIX through this path to the digit) refuses it -> D-3 |
| R7 | W-2 sentence on LB(I_P) < 0 strict | KILLED | yes |
| R8 | I_0 sign flipped | KILLED | yes |

## Defects / conditions

- **C-1 (MEDIUM, registrar, before --run; pre-data):** bracket B-3. Decide whether F-GFC's "LB(I_P) > 0 on those trees" means all
  GAP-SHOWN CLOSED qwen3 trees (the code) or >= 2 of them (the consequence text: ">= 2 of 3 content-closed re-draws"). The outcome
  prints "LB(I_P) > 0 on m of c", so either reading can be scored without a code change. If the registrar picks >= 2, the
  post-run review scores F-GFC from that printed line and does not use the FIRES/NOT FIRED line.
- **C-2 (MEDIUM, builder, may follow the run because the code is correct by reading):** add a C-PURE / C-E2E case where a NO-GAP
  tree reads CLOSED with LB(I_P) <= 0 beside GF1-CC CLOSED (kills R2), and an assertion on the GF1-N FAILS line by value with N rows
  that differ from the CC rows (kills R5).
- **C-3 (LOW, run-operator):** if I-2 refuses, it is a failed precondition and not an outcome. Possible causes are a vector-source
  difference (`E1R.load_space` vs GAP-FIX's `FM.fit_matrix`) or a label-set difference (the readout train 8,324 vs GAP-FIX's
  `FG.tree_pool`). The T top-1 already agrees (0.7269 = 2504/3445, E1 identity), so the risk is in WP/V0 only. Return to the
  builder; do not edit the expectations.
- **C-4 (LOW, registrar):** record the declared deviations B-1 (a separate driver instead of an in-place delta), B-6 (D-5 is not
  fixed; this path imports no resp_structure code) and B-5 (I-2, an unregistered stricter precondition). None of them changes a
  registered word.
- D-3 (LOW, note): the N-raw / af_clean_s42 hygiene prints the number of fit texts sharing a held-out stem_key but does not
  refuse on it (FLAT-MIX-MMLU's rule). The registration calls that split content-closed under stem_key, so the post-run review
  must check that printed count = 0.

## Run (run-operator)

```
# merge by path to main first: git checkout worktree-wf_fa0ebf63-18c-4 -- tools/analysis/gap_fix_cc.py; git commit -- <path>; git hash-object = b83d2790
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --selftest      # 612 checks
powershell -File E:/TaxoArena_tmp/busy.ps1    # must exit 1 (no construction / site null / JVM); one heavy process at a time
python tools/analysis/gap_fix_cc.py --dry-run --nomic-leg e1-guard     # pool lines first; ADMIT + 2x REFUSE per tree; HYGIENE 0s
powershell -File E:/TaxoArena_tmp/busy.ps1    # exit 1 again
python tools/analysis/gap_fix_cc.py --run --nomic-leg e1-guard         # after C-1; write-once outputs in experiment_results/gap_fix_cc/
# back up both outputs + SHA256SUMS to E:/TaxoArena_backup_2026-10-08_gap_fix_cc; never commit them
```

## Commands

```
git hash-object tools/analysis/gap_fix_cc.py gap_fix.py e1_split_draws.py flat_mix_mmlu.py   # b83d2790 / 7c0691e8 / 0414b8fa / 555ae3ac
python -c "...sha256 of LF / CRLF renderings"                                                  # b36fb63ad5df80a7 / 3f185ebd2f42a77f
git show 4dbb0814 --name-only --format= | wc -l                                                # 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --selftest --quiet   # 612 passed
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --mutants            # 50 of 50 killed
scratchpad own_mut.py (R1-R8: text replacement above the selftest line, full --selftest per mutant)    # 5 killed, 3 survived
scratchpad why_mut.py M14 M15 M21 M29 M30 M31 M43 M47                                          # kill reasons = assertions / I-2 refusal
grep -cE "requests|urllib|http|call_judge|openai|ollama|sqlite3.connect|\.execute\(|INSERT|UPDATE " gap_fix_cc.py   # 0
grep -n "top-1 N_\|leaves" experiment_results/e1_split_draws/e1sd_readout_outcome.txt          # leaves 28/80/80/87/71/72, N-raw 84
synthetic FM.vmf_em(8200 x 256, k 80) timing                                                   # 1.3 CPU-s, 53 iterations
```
