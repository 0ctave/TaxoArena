# READY review: ADAPTIVE-PROFILE (tools/analysis/adaptive_profile.py)

Reviewed: branch `worktree-wf_ac4a49b3-e38-2` tip 6555d5e7 (parent 160bc01a), file blob:7e2949bb39de32b4986f91e22a0a0e85b5dcc499
(LF, of record; sha256-lf16:4caf7d6bfa01d8d7, sha256-crlf16:d3e9c7d5a52f8900; the worktree holds LF). Registration
docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — ADAPTIVE-PROFILE: ..." L25133-L25145 (_as_of d999e689).
Zero calls. Read-only: selftest and mutants in the scratch_dir sandbox; one real --dry-run (pool reader; see P-1).

## VERDICT: NOT READY (one BLOCKER, B1; a registrar's ruling, then a small delta)

The deciding path is to the registration: LOMO truly leaves the target out, no EVAL answer fits theta, a node offset, tau^2, s_max, q or
d*, shrinkage and the rule are as registered, F_bis runs rule A, twins are masked, the bootstrap resamples CK-CLOSE components then
seeds, and the selftest is non-vacuous. But the real data cannot reach an outcome: the real dry-run counts **115 R1 twin items on the
scored EVAL side**, and `--run` REFUSES at [R1-EVAL] for any EVAL twin with an AF cell (af_cells: no_routing_row_eval = 0, so all
115 have one). The registration both says "dropped wherever they fall" and fixes EVAL at 5,907. The builder saw this conflict and
refused rather than choose (AP-R0), which is correct. The hand-back still said "AUTHOR DECISIONS NEEDED: none". It is a registrar's
ruling, and the run is unreachable until it is made.

## Per-claim table (deciding claims)

| # | Claim | My evidence | Result | Sev |
|---|---|---|---|---|
| 1 | LOMO b excludes the target model | `lomo_b` fits `Y[:, others]`; the selftest asserts column m is unchanged when m's answers are flipped and moves when another model's are; X24 kills; my Y7 (theta read with the next model's LOMO b) KILLED | CONFIRMED | - |
| 2 | No EVAL answers in theta, node fits, tau^2, s_max/q, d* | `tr = (side=="T") & keep` feeds theta_fit, node_fit, leaf_mle; s_max/q are constants; d* = argmin of the GATE Brier (YG). Only LOMO b reads other models' EVAL answers (the declared "calibrated items" setting). X26/X27/X52 and my Y6 (GATE in TRAIN fits) KILLED | CONFIRMED | - |
| 3 | Shrinkage as registered | d = U/(I+1/tau_l^2), SE = (I+1/tau_l^2)^-1/2 at the parent's linear predictor; tau_l^2 = max(0, mean (U/I)^2 - 1/I) over models x non-pseudo nodes with I>0. My Y5 (sampling SE instead of posterior SE) and Y8 (one tau for every depth) KILLED | CONFIRMED | - |
| 4 | Adaptive rule as registered | Start at depth 1; descend iff SE < 0.20 (strict) AND BH q 0.05 within the sibling family with a defined SE; stop at the first failure. Hand cases cover |z| 1.97/1.95, no skipping, SE = s_max. A one-member family certifies at |z| >= 1.95996, against "> 1.96" (AP-R6; z gap 4e-5) | CONFIRMED (L-1) | LOW |
| 5 | Same rule on F_bis | Code: `stops_rule(fb, nb[E], c["s_max"], certify(fb, c["q"]))`. My Y1 (F_bis q=None) KILLED, but my **Y2 (F_bis s_max = inf) SURVIVED**: no fixture has a certified F_bis child with SE >= 0.20 | PARTLY | MEDIUM (D-2) |
| 6 | AP-R4: benchmark node = depth-1 ancestor | Real dry-run: AF-U has 231 nodes, 123 filing leaves (+2 pseudo), max depth 8. Depth 1 is one node per member (6 members; IFEVAL one-cell). So "d = 1 is C" is one node per (model, member); OWN-SOURCE beside. member_alias maps MMLU_PRO_LB to MMLU_PRO, so OWN-SOURCE is not emptied | CONFIRMED | - |
| 7 | Twins dropped (R1 471 / 427) | Real dry-run 471 ids / 427 texts, 427 v2 items; my own script gives 471 / 427 / 427, of which 380 have an AF cell. By side: **TRAIN 265, GATE 47, EVAL 115**. The keep mask covers LOMO, theta, node fits and GATE; my Y3 (twins in LOMO) KILLED. EVAL twins: REFUSE (B1) | PARTLY | BLOCKER (B1) |
| 8 | Cluster bootstrap over components, then seeds | `iid_and_two`: components (np.unique of comp) with replacement, then 5 seeds, on one stream default_rng(20261008); unstratified (AP-R11; the registration names no strata, so accepted). X18/X20 and my Y4 (stream +1) KILLED | CONFIRMED | - |
| 9 | Criteria AP1-AP4, F-AP, rule 8, P1-P9 | Clauses, order, bands and probabilities match L25133-L25145 to the digit (PRED dict vs text). P9 prints NOT SCORED (D-3) | CONFIRMED | - |
| 10 | Support (a)-(g) reproduces | 0.000865 x 0.17 = 0.000147; x 1.5 = 0.000221; MDE80 0.000618 / 0.000412; 2.487 x 0.000147 = 0.000366; sqrt(0.000865^2+0.000861^2) x 0.17 = 0.000207, MDE80 0.000581, PARITY needs 0.000516; n_eff 5907/2.118 = 2,789; 106,326 predictions; prediction (0.052744-0.045400) x 0.17 = 0.00125. DEFF 2.118 is sourced in RESP-PROFILE-INFO.json ("MEASURED two-stage 2.118"; SE 0.000865, spread_K 0.000861). NON-VACUOUS; the run re-measures DEFF, n_eff and MDE80 beside every contrast | CONFIRMED | - |
| 11 | Selftest non-vacuous | 11 / 11 in 61 s. Planted: every planted (model, node) certified with its sign and reached; A differs from q 0.10 / 0.01 / none. Null: tau^2 = 0, no descent, D_C = 0 exactly, TOO-SMALL, no fingerprint certified | CONFIRMED | - |
| 12 | Mutants 70 / 70 + control | Not re-run in full (shards ~70 min). My 8 on the deciding paths: 7 KILLED, Y2 SURVIVED; control survived | PARTLY | see D-2 |
| 13 | Dry-run is read-only, zero calls | gen_view sha before = after (c2930c60...); eval_view NOT opened; nothing written (no outcome dir, no export dir, worktree `git status --short` empty); DB mtimes unchanged (embeddings_cache.db 2026-10-03 16:58, multicorpus_cache_v1.db 2026-09-13) | CONFIRMED | - |
| 14 | Pins and commit hygiene | 9 imports equal on main and in the worktree (git hash-object); the commit touches 1 path (`--stat`: 1 file changed); main has moved 1 commit (443cf9ff, a review doc), so no conflict | CONFIRMED | - |

## Defects and fixes

- **B1 (BLOCKER): --run is unreachable on the real data.** 115 R1 twin items lie on the scored EVAL side, and the [R1-EVAL] pre-check
  refuses. Fix: a registrar's ruling, then a delta. Either (a) drop the 115 and re-register EVAL as 5,792 items with the components
  recounted (the instrument prints them), keeping the Support check: SE AP1 0.000222, MDE80 0.000622, so AP1 stays SCOREABLE narrowly
  (0.0007 > 0.000622); or (b) rule R1 not applicable on the content-closed v2 EVAL side (an item keyed by stem has no TRAIN twin in v2)
  and keep 5,907. The builder then switches [R1-EVAL] from a refusal to the ruled branch and adds a mutant for it.
- **D-2 (MEDIUM): F_bis's SE gate is untested** (my Y2 survives). Fix: add a planted F_bis case with a certified child at SE >= 0.20
  that must not be descended (and one at SE < 0.20 that must be), then re-run the mutant suite.
- **D-3 (condition, registrar): the AP-R14 deviation.** The af_clean_s42 descriptive leg (P9) is not built. Accept or reject it as a
  declared deviation. Nothing deciding depends on it.
- **L-1 (LOW): one-member family at |z| >= 1.95996, against "|z| > 1.96".** Accept the declared reading (AP-R6) or pin 1.96.
- **L-2 (LOW): R1 twin TRAIN rows still enter the F_bis clustering vectors** (no answers; AF-U and K_s are used as of record). Disclose
  in the outcome.
- **P-1 (process, mine):** busy.ps1 returned 0 at the instant the dry-run started, after two FREE polls (16:56, 17:12). Right after the
  run no java process and no matching pool reader was listed (only benchzoom processes). At most this was a reader overlapping a reader.
  No construction was observed.

## Commands

```
git hash-object tools/analysis/adaptive_profile.py                          # 7e2949bb...; LF/CRLF sha256-16 by script: 4caf7d6b / d3e9c7d5
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest     # 11/11, 61 s
python tools/analysis/scratch_dir.py --run -- python <scratchpad>/own_mut.py   # AP.MUTANTS := X00 + Y1..Y8; AP.run_mutants(): 7/8, Y2 survived
  Y1 F_bis certify(fb, None) K | Y2 F_bis stops_rule(..., INF, ...) S | Y3 lomo_b(Dt.Y, ones) K | Y4 default_rng(seed+1) K
  Y5 s = 1/sqrt(I) K | Y6 tr = (side != "E") & keep K | Y7 bb = roll(Bm[rows], 1) K | Y8 tau2[l] := tau2[1] K
python - : AP.twin_items_real() -> 471 / 427 / 427 items; intersect af_cells.tsv -> 380; vs validation_merged held-out 115 / train 265
powershell -File E:/TaxoArena_tmp/busy.ps1 ; python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
  -> "R1 twin items by split side ...: {'EVAL': 115, 'GATE': 47, 'TRAIN': 265}"; TRAIN key-complete 11841; GATE with row 2033; AF-U 231/123/depth 8
python -c Support arithmetic (row 10) and post-drop SE: 5907-115 = 5792; 0.00022*sqrt(5907/5792) = 0.000222; x2.8 = 0.000622
```

Run command after B1 is ruled and the delta is READY (busy.ps1 must exit 1 first; a pool reader):
`python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`, then `--run` with the same root.
