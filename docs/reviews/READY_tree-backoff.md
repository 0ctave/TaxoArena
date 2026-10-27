# READY review: TREE-BACKOFF (branch tree-backoff, tip e787a555)

Reviewer: adversarial-reviewer, 2026-10-06. Zero calls. Registration: docs/judge_v2_program.md "## Registered 2026-10-06 (before
any code or call) — TREE-BACKOFF: ..." L24814-L24826 (_as_of 9bff7e39). Instrument reviewed: tools/analysis/tree_backoff.py
**blob:da80c57e927c6ebf8a1db9e2f0420c96c1514519** (LF, of record; sha256-lf16:420538b917e9c2c6; the CRLF rendering is
sha256-crlf16:6615742b83315791; the worktree holds LF, so the two views agree).

## VERDICT: READY (no blocker)

Conditions (none blocks the run):
- C-1 (D-1): D_TK and D_B - D_KB are read post-run as shape-confounded and filing-asymmetric (words below). Descriptive only.
- C-2 (D-2): the post-run review prints the realised DEFF, n_eff and MDE80 beside BO1 (the code already prints them in the
  "support D_B" line) and states them against the registered 1.302 / 4,537 / 0.71pp.
- C-3 (D-3): the post-run review reconciles the printed NO_XSRC count with the registered 191.

Readings left open by the registration, ruled here:
- R1 (pseudo-cells under the union root): CONFIRMED. On the real data it barely matters: af_cells.tsv header
  `no_routing_row_eval=0 no_routing_row_train=2`, and 2 lines of the file carry a `<...>` cell (awk count). So no EVAL item is filed to a
  pseudo-leaf; the 2 TRAIN items enter only the union-root statistics. Shrinking toward the global accuracy is the neutral choice.
  Mutant R7 (pseudo-leaves under a source root) is killed.
- R4 (GATE cell = modal AF leaf; K cells by declared source): CONFIRMED. These are the readings of record: ESCALATION-RC R5 and
  UNION-AF-ROUTE R3. Builder mutant X61 kills filing among all sources.
- R10 (weak regions: no minimum node size; ties go to the larger node, then by name): CONFIRMED. It applies only to the optional
  descriptive arm and decides nothing.

## Per-claim table (deciding claims)

| # | claim | reviewer's result | verdict | sev |
|---|---|---|---|---|
| 1 | blob da80c57e LF; lf16 420538b9; crlf16 6615742b | `git hash-object` da80c57e…; python LF/CRLF sha256 420538b917e9c2c6 / 6615742b83315791; no CR in the file | CONFIRMED | — |
| 2 | imports unchanged at the registered blobs (d5473976, 92a04543, bf3f17db, f0f56805, 0acfb0cc) | all 5 equal (`git hash-object`); the script also refuses at import time on any other blob (MY_PINS) | CONFIRMED | — |
| 3 | commit touches only the new script | `git show --name-only --format= e787a555 \| wc -l` = 1; `git diff --name-only 9bff7e39 e787a555 \| wc -l` = 1; worktree `status --porcelain \| wc -l` = 0 | CONFIRMED | — |
| 4 | --selftest 7/7 | my run: 7 / 7 passed (60 s, scratch on E:, entries before = after 145) | CONFIRMED | — |
| 5 | mutants 64/64 killed, control X00 survived | my re-run, in two passes: 45 + 19 = 64 KILLED; X00 SURVIVED in both | CONFIRMED | — |
| 6 | real --dry-run clean | busy.ps1 rc 1 (free), then rc 0. POOL line first; B0-2 rc 0; manifest 53021e26 and 18+11 files equal; policy 8d68018c; AF-U 231 nodes / 123 leaves (+2 pseudo) / depth 8; K-WARD K0-K4 243 nodes / depth 10, each re-filed = k_cells_s*.tsv; vectors = bundle on 18,473; GATE with a routing row 2,033; TRAIN 11,841 key-complete; gen_view sha before = after (c2930c60); eval_view NOT opened; `experiment_results/archv2/tree_backoff` absent before and after | CONFIRMED | — |
| 7 | code = registration on the deciding path | read L329-L568 against L24818-L24822. p_root = S_root/n_root over every scored TRAIN item (pseudo included); top-down p_v = (s_v + tau p_parent)/(n_v + tau); argmax gives the first model on the sorted roster; tau=0 is V.fit (mass < 1 goes to the best single), and [TB-MIRROR] checks this against run_boot's TREE/K_s/BS arms at the point and in every i.i.d. and two-stage replicate. Grid {0..1000}, first maximum (ties to the smaller tau); one tau per arm and per K seed; B 2,000, rng 42; BO1 on point ± 1.96 SE_2stage (`U.interval`), i.i.d. and percentile printed beside; tau*=0 → NEITHER + words; rule 8; F-BO iff HURTS | CONFIRMED | — |
| 8 | the deciding interval respects the design | D_B is item-paired inside each two-stage replicate (`two[:, j, :] @ w_db`, one replicate for both arms). TRAIN units are resampled and every node re-fitted (hook receives run_boot's `wt`); EVAL components are resampled within stratum (run_boot's `v`). tau is held fixed (stated in the registration). One tree, so no seed term (Support (a)). There are no triplets (the STABILITY-VS-KMEANS B-1 trap does not apply). tau is chosen on GATE, never on EVAL (no DRIFT-REPLAY self-calibration) | CONFIRMED | — |
| 9 | no leakage | node fits refuse any EVAL weight ([TB-G3]). choose_tau uses only `V.train_full` and the GATE key. [TB-GATE-SIDE] refuses a GATE item that is among the scored items. AF-U and K_s were built on TRAIN (prior reviewed objects). Mutant R5 (EVAL correctness leaking into node stats) is killed | CONFIRMED | — |
| 10 | Support (b)-(e) arithmetic | source POSTRUN_escalation_rc.md L34: SE_2stage 0.00255, i.i.d. 0.00224, DEFF 1.302. Check: 0.00224 × √1.302 = 0.00256; 0.00255/√1.302 = 0.00223; n_eff 5907/1.302 = 4,536.9 → 4,537; MDE80 2.8 × 0.255 = 0.714pp. The verdict line (DESCRIPTIVE-ONLY at the predicted +0.30pp) reproduces | CONFIRMED (see D-2) | LOW |
| 11 | identity before any new number | `after_boot` refuses [TB-IDENTITY] before tb_lines prints. tau* is computed earlier but not printed until after the identity. X49 is killed | CONFIRMED | — |

## Mutants

Builder suite (`--mutants`, sandbox fixtures, scratch on E:): **64 of 64 KILLED, control X00 SURVIVED. CONFIRMED.**
- Pass 1 was stopped at the 30-min background limit after X45. It had killed X01-X45 (45, counted by `grep KILLED | awk`), and X00
  survived.
- Pass 2 ran `--only X00 X46..X64`: 19 of 19 KILLED, X00 survived.
- The killed pass 1 left its scratch dir E:/TaxoArena_tmp/run_66244_20261006135509_fx00tozm behind. I did not delete it (real path).
  It is for the data-steward's purge.
- Decisive mutants of the builder's suite: X01-X06 (verdict), X07/X08 (sign, arm), X09-X11 (tau), X13-X19 (recursion), X24/X26
  (TB column, mirror), X42/X43 (rule 8), X49 (identity), X56/X57 (hook resampling).

Reviewer's mutants (`rev_mut.py` sets `MUTANTS` and calls the module's own `run_mutants`; sandbox only): 8 of 8 KILLED, control
SURVIVED.
- R1: deciding interval at z 1.645 (90%). KILLED. Decisive.
- R2: tau = 0 never selectable. KILLED. Decisive.
- R3: back-off run bottom-up (levels reversed). KILLED. Decisive.
- R4: deepest level never shrunk (`levels` range off by one). KILLED. Decisive.
- R5: node stats unweighted, so EVAL correctness leaks into the fit. KILLED. Decisive (leakage).
- R6: deciding D_B read on NON_BBH (wrong population). KILLED. Decisive.
- R7: pseudo-leaves hung under the first source root (reading R1). KILLED. Not decisive on the real data (0 EVAL pseudo items).
- R8: GATE counted at tau-0 picks for every tau. KILLED. Decisive.

## Defects

- **D-1 MEDIUM (descriptive lines; the CONSTRUCTION-ARMS shape lesson).** D_TK and "D_B - D_KB (hierarchy dividend, AF-U minus
  K-WARD)" compare two hierarchies of different shape. AF-U is multiway: depth 8, 106 internal nodes. K-WARD is binary: depth 10,
  118 internal nodes. One common tau per arm shrinks through a different number of levels in each, and the filing is asymmetric
  (AF-U uses flatLeaf with 191 cross-source filings; K_s is mirrored by true source; UNION-AF-ROUTE D-4). The outcome line carries
  neither caveat. Fix: a registrar bracket before the run, so that the post-run reading of D_TK and D_B - D_KB carries "shape-confounded
  (multiway depth 8 vs binary depth 10) and filing-asymmetric (D-4); not a comparison of hierarchy quality". No code change is needed,
  and BO1 (TB vs TF, same cells and same filing) is untouched.
- **D-2 LOW (Support source).** DEFF 1.302 is RC1's seed-42 realisation. The same review reports 1.29-1.46 across seeds 1-9
  (POSTRUN_escalation_rc L38), and a cluster-only DEFF of about 0.99 (L36), so 1.302 is mostly variance from re-fitting the TRAIN policy.
  At 1.46: SE 0.00224 × √1.46 = 0.271pp, MDE80 0.76pp. The verdict line does not change (DESCRIPTIVE-ONLY either way). The transport
  also comes from a contrast with share e 0.226, while the predicted TB share is 0.15, which likely gives a smaller SE (conservative).
  Fix: C-2.
- **D-3 LOW (count check).** `n_xsrc` is printed beside "registered 191" but never compared with it. On the real data EVAL has no
  pseudo cell (af_cells header), so the mask is exactly the cross-source set. Fix: C-3, or `refuse` on a mismatch in a later
  revision (descriptive, not deciding).

## Commands (all read-only; zero calls)

```
cd .claude/worktrees/tree-backoff
git hash-object tools/analysis/tree_backoff.py; python -c "<sha256 of LF and CRLF renderings; b'\r\n' in data>"
for f in union_route_common union_cells_io union_af_route v2_declared_cells escalation_curve; do git hash-object tools/analysis/$f.py; done
git show --name-only --format= e787a555 | wc -l; git diff --name-only 9bff7e39 e787a555 | wc -l; git status --porcelain | wc -l
python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_backoff.py --selftest
python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_backoff.py --mutants
python tools/analysis/scratch_dir.py --run -- python <scratchpad>/rev_mut.py      # R1-R8 above
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # rc 1
python tools/analysis/tree_backoff.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0, 55 lines
ls experiment_results/archv2/tree_backoff   # absent before and after
head -1 experiment_results/archv2/union_af_route/inputs/af_cells.tsv; awk -F'\t' 'NR>1{print $NF}' .../af_cells.tsv | grep -c '^<'   # 2
grep -n 'DEFF\|0.00255' docs/reviews/POSTRUN_escalation_rc.md   # L34, L36, L38
```

## Brackets owed (registrar)
1. INSTRUMENT: tools/analysis/tree_backoff.py blob:da80c57e (LF; crlf16 6615742b) at branch tree-backoff e787a555 is the instrument of
   L24814-L24826; READY at this review's commit.
2. Readings R1, R4 and R10 CONFIRMED as stated in the docstring (L41-L72).
3. D-1 words for the post-run reading of D_TK and D_B - D_KB (shape-confounded, filing-asymmetric; not a comparison of hierarchy quality).
4. Post-run duties: realised DEFF / n_eff / MDE80 beside BO1 against 1.302 / 4,537 / 0.71pp (C-2); NO_XSRC count against 191 (C-3).
