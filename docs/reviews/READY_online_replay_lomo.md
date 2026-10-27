# READY review: ONLINE-REPLAY-LOMO stage 1 (tools/analysis/online_replay_lomo.py)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. Branch online-replay-lomo, tip 69cd6d4c; script
`blob:8fe228ebb57edd981c848803ed2ba9216f221f54` (`git hash-object`, LF; working tree LF, 0 CR bytes; sha256-lf16:bd9f29a03daf42b3).
Registration: prog L23944-L23958 (964511fd), with the L23941 bracket (OT1 EQUIVALENT, so the OOS legs are read as written).
Imports asserted before import and checked on main: union_af_route.py `blob:bf3f17db…`, g13_breakdown.py `blob:c29fa1c3…`.

## Verdict: NOT READY as built. Two HIGH findings on deciding paths; both are cheap to fix.

The replay is honest on the split. Its two comparators are not neutral. Both asymmetries push towards the predicted outcome:
**C-1** makes the online leaf about 1.45x stiffer than the registered sequential mean (OL2 drifts towards STABLE, so F-OL is less
likely to fire). **C-2** gives the batch arm a source oracle on IFEVAL worth about -0.008 of pooled D (OL1 drifts towards LOSS).
The script becomes READY after either path:
(a) **Recommended.** A code delta that fixes C-1 and adds C-2's symmetric line, then a delta review (selftest, mutants, O3/O8 below).
(b) The registrar brackets, pre-data, the builder's readings OL-R1 and OL-R3 as of record, with the bias direction written into
both brackets.
Everything else is CONFIRMED: the selftest, 44/44 mutants, the real dry-run, the pins, the copied rules and the Support arithmetic.

## Per-claim table (deciding claims)

| # | claim | builder | mine | status | sev |
|---|---|---|---|---|---|
| H1 | Held-out member never enters the five trees' fit | per-member AF-U trees, own TRAIN; 256-d bundle | 256-d = rp12_pairing `vectors()` truncation `[:dim]` + renorm, no fitted projection. us_fit is per source. Mutant O1 (thresholds over all six arms' cells) KILLED. The trees' own-TRAIN fit is taken from POSTRUN_union_af_route (not re-derived). Residual: 15 TRAIN / 14 EVAL multi-class items (MATH and MMLU_PRO_LB/math share text) leave the bundle but stay in the MMLU_PRO_LB tree's fit | CONFIRMED (residual disclosed, D-5) | LOW |
| H2 | Thresholds from GATE only | in-members' GATE vs five-member cells | dry-run: 876-1,975 in-member GATE items per replay (total GATE 2,028 = bundle `held_gate_rows_dropped` 2,028). M10 / M41 / O1 / O7 KILLED | CONFIRMED | - |
| H3 | Online sequential leaf-mean update | `mbar` initialised at the UNIT vmfMu (norm 1.000000 on all 122 leaves), weight n = directQueries | The sequential mean of unit rows has norm r < 1. Measured r of each leaf's TRAIN rows (256-d): min 0.576, **median 0.691**, max 0.964. So the incumbent mean carries **1/r = 1.447x** (median) its registered weight. The leaf moves less, churn is understated, and F-OL is protected. The oracle shares the convention: O8 (mbar = 0.69 x mu0) is KILLED **against** the oracle, and O3 (renormalise every step) SURVIVES | **REFUTED as the registered "sequential mean"** | **HIGH (C-1)** |
| H4 | Batch comparator like with like (OL1) | BATCH AF-U as built, mirrored by-source IFEVAL filing (C-S1); online = flatLeaf over all cells (OL-R1, disclosed) | Batch nearest-of-all P_fl **0.7265** vs mirrored **0.7346** (**-0.0081**). In batch, 48 of 162 IFEVAL EVAL items are nearest to a non-IFEVAL cell (pooled **-0.0078**). Only 2 non-IFEVAL items are nearest to the IFEVAL cell. IFEVAL has 1 declared class, so its mirrored batch P_fl is 1.0 by construction. Online filing gets no oracle, so D is pushed negative by up to about 0.008 = 40% of the 0.020 margin, larger than the TOST reach 0.0064 | **PARTLY** (disclosed; not neutral) | **HIGH (C-2)** |
| H5 | k-means arm like with like | K_0 = us_fit seed 0 at ksrc, same online procedure | Same filing rules, thresholds per arm, same order and rule. The identity P(US_0) 0.7368 is reproduced in the dry-run. C-1 and C-2 apply to both arms equally, so tree-minus-k-means is fair (descriptive) | CONFIRMED | - |
| D2 | Copied OOS rules equal oos_baselines (blob 7e74108d) | threshold, ob_status copied | `threshold`: `sort(sg)[floor((1-TPR) n)]` = `order_stat(g_max, 1-TPR)`. `ob_status` has the same four-line form. Z90 1.645 and Z95 1.96 match. TPR 0.95 matches. Margin 0.020 is the registered one (OB has 0.010) | CONFIRMED | - |
| D1 | fitset_faithful's batch labelled refit not used | WILL-NOT-SHOW | The registration's INSTRUMENT names only union_af_route and g13_breakdown. The online sequential update is the registered operation | CONFIRMED | - |
| R5 | Naming (OL-R5) | an incumbent keeps its name unless absorbed m-TRAIN strictly exceeds its majority count; buffer cells use TRAIN majority (tie: smaller name, GB.majority); an EVAL-only buffer cell is `<empty>`, never correct | `cdom` = round(profile_size x purity). profile_size = TRAIN count on 22/122 leaves (median ratio 0.990). M14 / M33 / M42 / O4 KILLED | CONFIRMED as code; the reading needs a bracket | MEDIUM |
| R8 | Churn (OL-R8) | all cells after the stream (buffer moves = churn) is deciding; means-only beside; [ORL-OL2-BOTH] refuses when both rules hold | The registration says "the five-member graft before and after". F-OL's text attributes firing to "mean refit". With buffer moves counted, F-OL can fire on buffer capture alone, and then "needs mean-freezing" does not follow. ORL-OL2-BOTH can only trigger when a percentile upper lies below its point (essentially never). It is a safe refusal, not a criterion | PARTLY | MEDIUM (C-3) |
| S | Support | SE 0.00547, DEFF 1.223 (DSC C-DB, transported), n_eff 5,020, reach 0.0064 / 0.0246 | sqrt(0.15 x 1.223 / 6,139) = **0.005467**. 6,139 / 1.223 = 5,020. 0.020 - 2.487 SE = **0.00640**; 0.020 + 0.842 SE = **0.02460**. Mean cluster size here is 1.091 (6,139 / 5,628). OL2's "about 5,100 per replay" is really **2,661** (-MMLU_PRO_LB) to 5,977. At n 2,661 and p 0.005 the upper bound is 0.0077 < 0.020, so OL2 is still SCOREABLE. The script prints DEFF, n_eff and MDE as measured | CONFIRMED (OL2 n restated) | LOW |
| DR | Real --dry-run | - | Run with tasklist java.exe = 0 (CERT-PC-K2 had ended; one reader python, fitset_intent, beside). rc 0. The POOL line comes first; the B0-2 check is rc 0; WAL 0 bytes. Manifest 53021e26… has 18 + 11 files EQUAL. GATE 2,028. Bundle rows reproduced to 5.55e-17. I3 6,139/6,139; P_fl 0.7346; K_0 labels 12,334/12,334; P(US_0) 0.7368. 123 cells per arm. 12 threshold lines; no statistic printed. DB sizes and mtimes are unchanged (diff empty). Output dir absent; worktree `git status` clean | CONFIRMED | - |
| T | Selftest / mutants | 12 cases; 44/44 | SELFTEST PASSED (12 cases); MUTANTS 44 of 44 KILLED, control SURVIVED | CONFIRMED | - |
| G | Commit hygiene | - | 69cd6d4c touches 1 path (`git show --name-only --format= 69cd6d4c \| grep -c .` = 1, the script). No yml / .env / .gitignore | CONFIRMED | - |

## Own mutants (deciding paths)

O1 thresholds over all six members' cells: KILLED (decisive: leakage of m into tau).
O2 `n += 0` (count frozen): KILLED (decisive).
O3 running mean renormalised every step: **SURVIVED** (decisive: the update rule is pinned only through discrete outcomes; see D-3).
O4 renaming of existing cells disabled: KILLED (decisive, OL1).
O5 order seed not fresh per replay: KILLED.
O6 OOS buffering `<=` instead of `<`: SURVIVED (not decisive: equality with a GATE order statistic has measure zero).
O7 tau_m from the max-cos order statistic: KILLED (decisive).
O8 mbar initialised at 0.69 x mu0: KILLED, because the oracle shares the unit initialisation. This is evidence for C-1, not a defect of the test.

## Registrar brackets needed (OL-R1..R11)

- **OL-R1: YES.** The C-2 asymmetry, and n = directQueries (equal to the TRAIN count on 20 of 122 leaves; median ratio 1.027).
- OL-R2: yes (LOW). "GATE p20" is read as `sort(margin)[floor(0.20 n)]`. Thresholds are per arm; the strict inequality buffers.
- **OL-R3: YES**, unless C-1 is fixed in code. It sets the initial weight of the running mean.
- OL-R4: yes (LOW). k = min(L_m, buffer size); ukm seed 0; no buffer means no cell.
- **OL-R5: YES (MEDIUM).** The online naming rules (incumbent renaming, buffer TRAIN-majority, `<empty>` never correct) are not in the registration.
- **OL-R8: YES (MEDIUM).** Which churn decides, and F-OL's attribution (C-3). Also the [ORL-OL2-BOTH] refusal.
- OL-R9: yes (LOW). Brier over the named outcomes with GAIN 0.00 implied; P2 "per replay" means all six in band.
- OL-R6, OL-R7, OL-R10, OL-R11: no. They are as registered (R7 is OOS-BASELINES' form; R10 and R11 are descriptive).

## Defects and fixes

- **C-1 (HIGH, H3).** In `replay()`, initialise `mbar[j] = r_j * mu0[j]`, keeping `n_j`. For the tree arm, r_j = |mean of the
  cell's TRAIN rows| (af_cells.tsv rows; the direction is unchanged, so `before` and the identities are unchanged). For K_0, use
  the unnormalised TRAIN mean of its members. For the one-cell member, use |mean of TRAIN|. Make that the deciding rule. Print the
  unit-initialised churn and D beside (descriptive). Make the oracle follow the fix, and add a direct test that
  `mbar` = (r n mu + sum x) / (n + k) after k absorptions, which kills O3.
- **C-2 (HIGH, H4).** Print beside OL1 (descriptive) the D and OL1 word against the batch arm filed by nearest-of-all, the same
  flatLeaf rule as the online arm (batch P_fl 0.7265). Also print D pooled over the five non-IFEVAL replays. Before the run, the
  registrar names which comparator decides. My recommendation: the symmetric one, with the mirrored one beside.
- **C-3 (MEDIUM, R8).** The F-OL line must print both churns (all cells / means only). It must say "beyond 2% by buffer capture"
  when only the all-cells churn exceeds 0.020. The registrar brackets which churn decides OL2.
- D-3 (MEDIUM): O3 survives. The fix is folded into C-1.
- D-4 (LOW): restate OL2's denominator. It is 2,661-5,977 per replay, not "about 5,100"; still SCOREABLE.
- D-5 (LOW, wording): the online arm is transductive on m's EVAL (registered: m's EVAL is streamed and is in the buffer
  k-means). An EQUIVALENT never reads "as good as a rebuild on unseen items". Disclose the 15/14 MATH-MMLU_PRO_LB text-shared
  multi-class items as the residual of "never touched".

## Launch (after path (a) and its delta READY, or path (b))

From main after the merge (`Z:\FAC\TUBerlin\THESIS\TaxoArena`), no env prefix:
`python tools/analysis/online_replay_lomo.py --run`
From the worktree instead: append `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`. Never beside a construction (rule 7). Write
outputs once and never commit them: pin by sha256 and back up to E:.

## Commands

```
git hash-object tools/analysis/online_replay_lomo.py            # 8fe228eb (worktree); grep -c $'\r' = 0
git hash-object tools/analysis/{union_af_route,g13_breakdown}.py # bf3f17db / c29fa1c3 (main); oos_baselines.py 7e74108d
python tools/analysis/online_replay_lomo.py --selftest           # SELFTEST PASSED (12 cases)
python tools/analysis/online_replay_lomo.py --mutants            # 44 of 44 KILLED; control SURVIVED
python $TEMP/orl/own_mutants.py ; own_o5.py                      # O1-O8 as listed
python $TEMP/orl/stiff.py   # vmfMu norms 1.000000; dq==TRAIN 20/122; profile==TRAIN 22/122; r median 0.691, 1/r 1.447
python $TEMP/orl/sym.py     # batch nearest-of-all 0.7265 vs 0.7346; IFEVAL 48/162 outside -> -0.0078; 2 into IFEVAL
python tools/analysis/online_replay_lomo.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0 (tasklist java = 0)
ls -l --time-style=full-iso *.db*  before/after -> diff empty; git status --porcelain (worktree) = 0 lines
```
