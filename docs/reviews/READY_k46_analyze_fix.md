READY (analysis only) + MERGEABLE (by path): k46-analyze-fix 2d9e83e8, tools/analysis/k46_repost.py sha256-lf16 011682b96d8d419f
(blob 74d5fd68de5f46bd3ed3ded26f9c675b56fe32a2, LF of record; worktree CRLF rendering sha256-crlf16 c74ce4896bb437df)

# Delta review of the --analyze fix for incident aaf12c77 (registrar 74683c20); zero calls

Scope: `git diff aaf12c77 2d9e83e8` (2 files, +43/-5). main has not touched either file since aaf12c77
(`git diff aaf12c77 main --stat -- tools/` empty), so the merge by path has no conflict. Deciding paths: C0 (d) in
analyze_pair (the voiding check), and RP20 C1 / ONE C1 / RP21 C1-v2 as printed by the re-analysis.

## Verdicts
- MERGEABLE by path (`git checkout k46-analyze-fix -- tools/analysis/k46_repost.py tools/analysis/k46_repost_selftest.py`).
- The RP20 + ONE re-analysis with lf16 011682b96d8d419f is READY. Run it into OUT_DIR only after the registrar has moved the void
  outcome files aside (they are write-once, so a re-run refuses until then). The live run must print `ledgers 7384` / `ledgers 3272`
  (on scratch these read 0 because the ledger dir was empty; see D2).
- Gate entry inserted into READY_k46_repost.md (insertion only): analysis-only, lf16 011682b96d8d419f. `--go` stays on dd8152585fd7f0d7.

## Per-claim table (deciding claims)
| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| 1 | the diff touches no posting path | CONFIRMED | 4 hunks: MUTANTS tuple (+"analyze_no_configure"), analyze_canary L1283, analyze_pair L1433 and the T re-check loop + (d) detail text L1456-L1480. The posting path already called configure_rr() at L1028 and is unchanged. launch/ready_gate/order_gate/poster untouched | - |
| 2 | the diff touches no deciding statistic | CONFIRMED | (d)'s boolean `t_ok == len(t_rows) == 2*len(mids)` is unchanged; only its detail string gained a "first mismatch" suffix. The SystemExit branch is now recorded and no longer `pass`; t_ok is incremented exactly as before. Re-analysis diff vs the void outcomes (below): only sha header, (d), the C1 word, P-words, the falsifier line and the ledger count change | - |
| 3 | C0 (d) passes on the posted caches | CONFIRMED | RP20 `PASS 3692 of 3692`; ONE `PASS 1636 of 1636` (process started at rr model grok-4-1-fast-reasoning, printed). 0 [BODY-RECHECK] lines in 3 logs (count) | - |
| 4 | RP20 C1 reproduces the disclosed value | CONFIRMED to the digit | 1258 kd in 360 comps: 0.7719 - 0.7576 = +0.0143, 90% normal [+0.0006, +0.0280] (disclosed +0.0143 [+0.0006, +0.0280]); inside +-0.040 -> C1 EQUIVALENT. Support: DEFF 1.114 analytic, n_eff 1129.6, SE 0.0083 | - |
| 5 | ONE C1 reproduces the disclosed value | CONFIRMED to the digit | 544 kd in 160 comps: 0.7169 - 0.8768 = -0.1599, 90% normal [-0.2015, -0.1183], SE 0.0253 (disclosed -0.1599 [-0.2015, -0.1183]) -> C1 LOSS; falsifier NOT FIRED | - |
| 6 | RP21 v2 analysis still reproduces | CONFIRMED | --analyze-canary vs the outcome of record (dd815258) differs in 3 lines only: sha header, SUPPORT (the analytic-DEFF line already reviewed in READY_k46_deff 0c34ebf1), and ledgers 1200 -> 0 (scratch). C1-v2 lines are byte-identical | - |
| 7 | builder's selftest | CONFIRMED | 89 [OK], 0 [FAIL], rc 0; python -O rc 0; K14 and K15 [OK] | - |
| 8 | full mutant table | CONFIRMED | `--mutants`: KILLED 23 of 23 (the 22 of record + analyze_no_configure, killed by K14) | - |
| 9 | no write to objects of record | CONFIRMED | sha256 of 9 files before == after (cmp equal): backup caches c8364702 / 7f5d599c, live caches (same), canary v21 e24df0c5 / v22 f2db9fa0, store 44724d25, set ab000a83, eval_view_REG | - |
| 10 | pins | CONFIRMED | `git rev-parse k46-analyze-fix:tools/analysis/k46_repost.py` = 74d5fd68; LF sha16 011682b96d8d419f (from the blob and from the worktree file with CRLF folded); CRLF16 c74ce4896bb437df (1746 CRLF lines in the worktree) | - |

## Own mutants (3; delta < 150 lines)
- M1 analyze_canary's configure_rr() -> pass: SURVIVED. Not decisive: the canary readout rebuilds no body through rr (no rr. call in
  analyze_canary; the pre-fix dd815258 canary outcome was VALID without it). See D1.
- M2 `if t_bad:` -> `if False:` (the [BODY-RECHECK] print removed): KILLED by K15. Decisive for the "not swallowed" claim.
- M3 (d) condition with `t_ok ==` dropped (counts only): KILLED by K15 (the C1 UNDETERMINED BY VALIDITY assertion). Decisive.

## Defects
- D1 LOW: K14 covers analyze_pair only. The canary's configure_rr() is untested and currently inert. Fix (optional): no action is needed
  for RP20/ONE. If a future canary check rebuilds bodies through rr, add a K14-style canary test.
- D2 LOW (operator note, not code): the ACCOUNTING line reads the day ledgers from LEDGER_DIR. A scratch run prints `ledgers 0`. The
  outcome of record must come from the real OUT_DIR / LEDGER_DIR run and show 7384 / 3272 (the void outcomes show those counts).
- D3 LOW (record): the P-word readout of the re-analysis is RP20 P1-P4, P6 HELD, P5 FAILED (max per-contestant movement 0.1194 over
  37); ONE P1 FAILED, P2 FAILED (+0.0789, n 38). These are the registrar's to record. They are not disclosed in 74683c20, which gave
  C1 only.

## Commands (zero calls)
```
git diff aaf12c77 2d9e83e8 ; git diff aaf12c77 main --stat -- tools/          # (empty)
git rev-parse k46-analyze-fix:tools/analysis/k46_repost.py ; python sha16 LF/CRLF of the worktree file
(worktree) python tools/analysis/k46_repost.py --selftest ; python -O ... --selftest ; ... --mutants   # 89 OK rc 0; rc 0; 23/23
sha256sum <9 files> > sha_before ; cp backup caches + canary caches + store + set + eval_view_REG -> scratchpad/ana
scratchpad/ana/drive.py <rp20|one|canary>: imports the worktree's k46_repost, real_cfg() with out_dir / store_path / eval_path /
   set_file / ledger_dir redirected to the scratch copies; calls analyze_pair / analyze_canary
diff experiment_results/archv2/k46_repost/{rp20_outcome,ref_paired_v2_outcome,g17_v2_canary_outcome}.txt scratch/out/<same>
grep -c BODY-RECHECK scratch/*.log                                             # 0, 0, 0
sha256sum <9 files> | cmp sha_before                                            # EQUAL 9
git archive 2d9e83e8 src/main tools docs/plan_2026-09-15.md docs/reviews/READY_k46_repost.md | tar -x -C scratch/M{0..3}; edit; --selftest
parse_ready(text, dd81...) -> [] ; parse_ready(text, 0116...) -> refuses (no --go) ; transport_check.py --ready ... -> (c) PASS
```
