# READY review: RESP-PROFILE-INFO, CELL-DIFFICULTY, CELL-STRATA-EVAL (branch resp-structure-trio, 8c36f3fb)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Registrations: prog L24388-L24428 (_as_of 633255f2).
Reviewed blobs (LF, `git hash-object` = `git rev-parse 8c36f3fb:<path>`; the working tree is LF, so there is no separate CRLF rendering):
resp_structure_common.py blob:ba67f78f, resp_profile_info.py blob:1817ec8a, cell_difficulty.py blob:bfc0c615,
cell_strata_eval.py blob:f0c41862. All scratch files were written under E:/TaxoArena_tmp/rev_resp.

## Verdicts

| test | verdict | conditions |
|---|---|---|
| RESP-PROFILE-INFO | **READY** | B-RP (bracket the readings); post-run duties R-1, R-2 |
| CELL-DIFFICULTY | **READY for CD1; CD2 NOT READY until the B-CD2 pre-data bracket is committed** | B-CD2 (pre-data fix of the CD2 reading); CD-R7 bracketed as DESCRIPTIVE |
| CELL-STRATA-EVAL | **NOT READY** | D-CS1 (BLOCKER): change the CS-R1 cell order, then a delta review; B-CS brackets |

The real dry-runs: see the DRY-RUN section at the end.

## Per-claim table (deciding claims only)

| # | claim | reviewer's result | status | sev |
|---|---|---|---|---|
| 1 | IRT on TRAIN only: theta comes from the TRAIN key; EVAL item (a, b) are fitted with theta fixed; every cell mean / bbar comes from TRAIN | Read in `irt_point` (assert_train on D.T), `prepass` (TRAIN key only, printed before the EVAL view), `boot` hook (TRAIN rows by multiplicity), `loo_irt`, `eta2` (TRAIN b means). Builder mutants X03/X04/X05/X33/X34/X36, Y01/Y34, Z17/Z18/Z36 are all KILLED in my re-run | CONFIRMED | - |
| 2 | Identity precondition: C1 +2.67pp, G_AF +1.52pp (best 0.6049 / declared 0.6316 / AF-U 0.6201); RP also checks the two-stage [+1.46, +3.89] | The constants equal the record (L21931: G 0.6316 - 0.6049 = +2.67pp [+1.46, +3.89]; L23682: best 0.6049, declared 0.6316, AF 0.6201; outcome sha e50a8e0f at L23679). Own O1 (compare C1 only) is KILLED | CONFIRMED | - |
| 3 | Builder point (3) ID-R1: identity is checked at the point | The registered digits are points, so a point check is the registered check. RP's interval check is extra, and it is safe: the RP2 hook draws no RNG, so `run_boot`'s draws equal the un-hooked reader's | CONFIRMED | - |
| 4 | Builder point (4) RWS-R1 = ROUTE-SOURCE-NULL | Execution check: `rws_profile` / `rws_cells` from 8c36f3fb against c9b982d9:tools/analysis/union_route_common.py (blob:d5473976) on 20 random layouts x 10 seeds. **200 of 200 draws are identical** (same profile, same grouping array) | CONFIRMED | - |
| 5 | Comparators: RWS within source (preserves source, as RP1 / CD1 condition); K_0 s0-4 mean; SRC; declared [DECL] never ranked | The null is within source, not global (check 4 satisfied). K_s are read from the manifest-pinned k_cells_s1-4 | CONFIRMED | - |
| 6 | Write-once (mode "x"), B1 marker, write-once checked in the prelude, dry-run writes nothing | X30/X31, Y30, Z29 are KILLED; each script's `refusals` case runs the second run REFUSED with the outcome unchanged | CONFIRMED | - |
| 7 | Support arithmetic RP / CD | 5,907 / 1.6 = 3,691.9 (registered 3,690); 0.05 / sqrt(3,690) = 0.000823 (reg. 0.0008); MDE80 0.002305 (reg. 0.0023). DEFF 1.6 has a source (U1 1.595, L23682) and is declared a pilot assumption. RP measures the two-stage DEFF, n_eff and MDE80 beside D (RP-R5) | CONFIRMED | - |
| 8 | Support arithmetic CS | 0.10 / sqrt(18) = 0.02357 (reg. 0.024); MDE80 0.0660 (reg. 0.066); CS2 vs SRC DESCRIPTIVE-ONLY is stated | CONFIRMED | - |
| 9 | Builder point (2): ridge lambda 1.0 can falsely mark CD2 cells MULTIDIM | My simulation (true 1-D 3PL, 18 models, theta fixed, 101 cells of n 27-59, floors 0 / 0.1 / 0.25). Cell-difficulty SD 1.2: CD p < 0.05 in 6 of 101 unselected cells at lambda 1.0 and 6 of 101 at 1e-3. Cell-difficulty SD 2.0: **18 of 101 at lambda 1.0 against 7 of 101 at 1e-3**. The direction is confirmed and is material when cells are extreme | CONFIRMED (conditional on extremity) | HIGH |
| 10 | CD2 tests the flips "beyond 1-D" | **Mechanical.** The 7 cells were selected by CELL-FLIPS on the same EVAL D_c (p 0.0001-0.0029 against a D = 0 null). Under any 1-D model with theta_ch <= theta_g the null mean is <= 0, so the 1-D null is at least as strict as CELL-FLIPS' null. Simulation with interaction planted in 15% of cells, 8 replicates, CELL-FLIPS-style BH over 101 then CD BH over the selected: **33 of 33 selected cells MULTIDIM; p_CD <= p_CF in 30 of 33**. CD2 = 7 is therefore close to guaranteed given CF1, and F-CD (CD2 = 0) is reachable only through misfit of the fitted null's variance. CD-R7 runs on UNSELECTED cells and cannot measure this | REFUTED as evidence beyond CF1 | HIGH |
| 11 | CD2's null represents "guessing" | The registered floors are 0 for BBH and MUSR (fixed now). 5 of the 7 flip cells are BBH multiple-choice tasks: hyperbaton has 2 options, movie_recommendation 4-5, logical_deduction 3/5/7, date_understanding 6 (standard BBH formats; not re-read in the repo). The guessing route F-CD names cannot be represented in the very cells tested | PARTLY | MEDIUM |
| 12 | Builder point (3) CS-R1: systematic rounding + HT is "proportional allocation over AF-U cells" | HT is unbiased (E n_h = e_h; the selftest's population case holds). But at n 100 over 123 cells most e_h < 1, so the design is systematic sampling over the **cell index order**. AF-U keys sort by node id, and node-id order carries tree adjacency. On TRAIN (no outcome read): adjacent AF-U cells share their majority declared class 0.333 of the time against 0.077 for random pairs (centroid cosine 0.691 vs 0.556); K_0 shows 0.137 vs 0.147 (0.568 vs 0.564). Proxy on TRAIN label shares at the same e_h: AF index order MAE 0.00430 / 0.00433 / 0.00429 against within-source-shuffled 0.00445 / 0.00442 / 0.00442 (2.0-3.4% lower; 3 seeds), and K_0 0.00436 vs 0.00434 (no gain). This unregistered implicit hierarchical stratification goes to STRAT-AF only, and is the size of CS2's registered prediction (ratio 0.97) | REFUTED as like with like | BLOCKER |
| 13 | CS-R4 gp-IRT lambda = b2 / (b2 + v) | Its direction matches tinyBenchmarks' heuristic: more weight on the sample estimate when the IRT bias is large. b2 is the other-17 models' in-sample bias, so lambda leans to p-IRT. The arm is DESCRIPTIVE and no criterion reads it. Label it "gp-IRT-style (reading)" | PARTLY | LOW |
| 14 | Guessing floors key on the view's source names | union_cells_io `member_alias={"MMLU_PRO_LB": "MMLU_PRO"}`; declared keys "MMLU_PRO/..." confirm the view says MMLU_PRO, so `FLOOR` matches. No run prints a per-floor item count | CONFIRMED (presence only) | MEDIUM |
| 15 | Selftests and mutants | My re-run: selftest 8/8 for each script. Builder mutants: RP 44/44, CD 37/37, CS 39/39 KILLED; every C00 control survived (= 120/120 as claimed) | CONFIRMED | - |

## Own mutants (deciding paths; harness `RSC.run_mutants`, my table in E:/TaxoArena_tmp/rev_resp/own_mutants.py)
- O1 common: identity compares C1 only -> KILLED (refusals) - decisive
- O2 RP: RP1 percentile taken from the raw-y RWS values -> KILLED (e2e, null_e2e) - decisive
- O3 RP: raw-y arm R2 computed on residuals -> KILLED (e2e) - descriptive
- O4 CD: flip null with the challenger / g probabilities swapped -> KILLED (e2e, null_e2e) - decisive
- O5 CS: cluster bootstrap with independent draw indices per arm -> KILLED (e2e) - decisive
- O6 CS: CS1 ratio from NEYMAN -> KILLED (e2e) - decisive
- O7 CD: CD1 composition bar 0.5 -> 0.4 -> KILLED (branches) - decisive
- O8 common: B3 ignores the K0 picks -> **SURVIVED** - not decisive (no criterion of these three reads the K0 picks; the identity point is unaffected). D-8 below.

## Defects and fixes
- **D-CS1 (BLOCKER, CELL-STRATA-EVAL).** The cell order in `strat_draws` / `systematic` gives STRAT-AF tree-ordered implicit stratification that K_s do not get (claim 12). Fix: in every stratified arm, per draw, keep the source blocks in sorted order and apply a uniform random permutation of the cells within each source before the systematic start (same stream discipline: the permutation first, then u, then the keys). The HT pi is unchanged. Update the oracle `_o_draws` and add a selftest showing that index order no longer changes the estimate's distribution. Delta review: the diff, plus the builder's Z mutants, plus O5 and O6.
- **B-CD2 (HIGH, pre-data, registrar; CD2 needs it before the run).** A pre-data bracket on CD2 / F-CD stating that the 7 cells are selected on the same EVAL D_c, and that a 1-D null with theta_ch <= theta_g has mean <= 0. CD2 therefore cannot add evidence of multidimensionality beyond CF1, and F-CD is reachable only through null misfit. The CD2 count is reported as a CONSISTENCY CHECK of CF1 under a 3PL null, not as "evidence of more than one ability dimension". P2 (>= 4 of 7) is scored with that qualifier. Two optional additions, each needing a code delta and a delta review: (a) a calibration gate: if CD-R7's p < 0.05 rate on non-flip cells exceeds 0.10, CD2 prints MISCALIBRATED-NULL; (b) a lambda = 0.01 sensitivity line beside the flip table. The author decides whether BBH/MUSR per-task floors (claim 11) enter as a descriptive sensitivity; the registered floors stay "fixed now".
- **B-CD7 (LOW, registrar).** CD-R7 is unregistered: bracket it as DESCRIPTIVE, with no verdict reading it (as the code already does).
- **B-RP (LOW, registrar).** Bracket RP-R1..R9 as the readings of record (shrink sum / (n_c + 20); R2 can be negative; interval D +- 1.96 SE_2stage; strict percentile; pre-pass form; P4 share). No code change.
- **B-CS (LOW, registrar).** Bracket CS-R1 (as amended by D-CS1), CS-R3 (IRT-ANCHOR k-means on (a, b)), CS-R4 ("gp-IRT-style", not tinyBenchmarks' exact estimator), CS-R5 and CS-R7.
- **D-5 (MEDIUM; post-run duty R-1, RESP-PROFILE-INFO).** Pearson residuals are heavy-tailed where the floor is 0 (BBH / MATH / MUSR / IFEVAL): a correct answer at P ~ 1e-4 gives e^2 ~ 1e4 against a total sum of about 1e5 terms of order 1. The post-run reviewer prints the share of sum e^2 (EVAL) carried by the top 0.1% of item-model cells, and R2_int(AF-U) and the RWS p97.5 with those cells dropped, beside RP1 (descriptive; the criterion stays as registered).
- **D-6 (MEDIUM; post-run duty R-2, all three).** The post-run reviewer counts the TRAIN / EVAL items per floor value (expect GPQA and MMLU_PRO non-zero at 0.25 / 0.10) from the outcome or by recompute. A presence check is not enough (claim 14).
- **D-7 (LOW).** The `assert_train(D_, T[w > 0])` in the RP2 hook is vacuous: its positions are D.T by construction. The binding guard is `irt_point`'s. No fix needed; do not cite the hook as a guard.
- **D-8 (LOW).** O8 survives: no refusal case changes only a K0 pick. Optional: add `expect(..., "[B3]", pol_mut=K0 pick)`.
- **D-9 (LOW, CD1 reading).** The composition share uses EVAL item parameters fitted on the same EVAL y, so V_pred is in-sample at the item level and the share leans above 0.5. Record this in the post-run qualifier, not as a defect of the code.
- Disclosure (633255f2): the exploratory union look computed no cell quantity. The IRT choices (3PL, fixed floors, lambda 1.0) followed a 1PL parallel analysis over both sides. That is acceptable as disclosed; it is not a preview of any registered statistic.

## Registrar brackets needed
B-CD2 (pre-data; before the CELL-DIFFICULTY run), B-CD7, B-RP, B-CS (after D-CS1 is fixed). Post-run duties R-1 and R-2 go in the brackets.

## Commands
```
# pins
cd .claude/worktrees/resp-structure-trio; for f in resp_structure_common resp_profile_info cell_difficulty cell_strata_eval; do git hash-object tools/analysis/$f.py; git rev-parse HEAD:tools/analysis/$f.py; done; file tools/analysis/*.py   # LF
# selftests / builder mutants (logs E:/TaxoArena_tmp/rev_resp/*.selftest.log, *.mutants.log)
python tools/analysis/{resp_profile_info,cell_difficulty,cell_strata_eval}.py --selftest | --mutants
# own mutants
python E:/TaxoArena_tmp/rev_resp/own_mutants.py rp|cd|cs
# RWS equality vs ROUTE-SOURCE-NULL (ast-extracted functions from both commits; 200/200 identical)
git show 8c36f3fb:tools/analysis/resp_structure_common.py > rsc.py; git show c9b982d9:tools/analysis/union_route_common.py > urc.py; (inline script)
# CD2 simulation (ridge and selection): python E:/TaxoArena_tmp/rev_resp/sim_cd2.py 1 [1.2]; python ... sim_cd2.py 2 2.0
# cell-order adjacency (TRAIN centroids / majority declared class from af_u_bundle_256.npz + af_cells.tsv / k_cells_s0,s1.tsv): inline script
# cell-order proxy: python E:/TaxoArena_tmp/rev_resp/order_sim.py <seed>   (TRAIN label shares; systematic over index vs within-source shuffled order)
# identity constants: grep -n "0\.6201\|1\.46pp" docs/judge_v2_program.md   (L21931, L23682)
```

## DRY-RUN (real data; run at 16:29 after polling every 5 min until no java.exe ran; `--data-root` = main checkout)
All three: rc 0. The POOL line `pv2_1575de61bb20e977: B0-2 pool check rc 0` comes first. TRAIN SET 11,841 of 12,351 (10,781 components),
EVAL SET 5,907 / 5,404 (= registered). DENOMINATOR AF-U 123 cells, K0-K3 123, K4 122; EVAL items without a cell 0 in every arm.
CELL-DIFFICULTY: the CELL-FLIPS outcome sha256 03383314... = the pin, and its 7 FLIP AF-U lines = the registered list. "No key
column selected; nothing written". No outcome directory was created (`ls experiment_results/archv2 | grep -cE
"resp_profile|cell_difficulty|cell_strata"` = 0). The data_v2 SPLIT-2 view DBs keep the same mtime and size before and after (`stat` diff
empty). Logs: E:/TaxoArena_tmp/rev_resp/*.dry.log.

## DELTA REVIEW 2026-10-04: resp-structure-fix1 b2d05f34 (cut from c7506ede); answers D-CS1, B-CD2 / claim 11, and the brackets of 0e34eb56

### Verdicts (delta)
| test | verdict | conditions |
|---|---|---|
| RESP-PROFILE-INFO | **READY (unchanged)** | blob:1817ec8a at b2d05f34 = main = c7506ede (LF; working tree = blob). The delta touches 2 files, neither this one nor resp_structure_common (blob:ba67f78f unchanged) |
| CELL-DIFFICULTY | **READY** (CD1 decides alone) | C-CD1 (MEDIUM): fix the TASK_OPTIONS table before the run, or the per-task-floor sensitivity lines are NOT REPORTABLE; T-CD2 (test gap on the deciding path, code correct); R-3 post-run duty |
| CELL-STRATA-EVAL | **READY** (D-CS1 fixed) | B-CS bracket owed before the run (LOW, wording) |

Pins of the reviewed blobs (git hash-object = git rev-parse b2d05f34:<path>; LF; the worktree has no CRLF rendering): cell_strata_eval blob:e76f9a6d, cell_difficulty blob:20f0d98d, resp_profile_info blob:1817ec8a, resp_structure_common blob:ba67f78f. main's tools/analysis changes since c7506ede (cert_k2_deflated, site_support, tree_like, zc_common) touch no import of the trio.

### Per-claim table (delta)
| # | claim | reviewer's result | status | sev |
|---|---|---|---|---|
| D1 | D-CS1: every stratified arm shuffles cells within source on each draw | All 7 `strat_draws` call sites in `model_errors` pass a block vector: STRAT-AF, K0-K4 and SRC use `bl[...]` (the modal stratum source of the cell's EVAL items), NEYMAN uses `bl["AF-U"]`, RAND has one stratum. IRT-ANCHOR draws no systematic sample. STRAT-AF+IRT reuses STRAT-AF's samples. No other `systematic` / `strat_draws` caller exists in tools/analysis (git grep at b2d05f34: 18 lines, all read). `cells_E` re-indexes EVAL-occupied cells only, so no empty cell falls into block 0 | CONFIRMED | - |
| D2 | the tree-order bias is removed | TRAIN-only proxy (52 declared-class shares, n 209, 1,000 draws, the b2d05f34 sampler). AF: index order (old) 0.00434 / 0.00434 / 0.00431 -> within-source shuffle (new) 0.00447 / 0.00446 / 0.00444. K0: 0.00439 / 0.00436 / 0.00436 -> 0.00439 / 0.00437 / 0.00438 (seeds 1-3). AF's 2-3% implicit advantage is gone; K0 is unchanged. Source blocks stay contiguous for every stratified arm alike (like with like; STRAT-SRC stratifies on source explicitly) | CONFIRMED | - |
| D3 | stream order is permutation, then u, then keys; oracle updated | `st_order` checks it against an independent replay. Z43 (u first) and Z45 (no map-back) are KILLED. `_o_draws` is re-written with loops and `_o_blocks` (ties to the sorted-first source) | CONFIRMED | - |
| D4 | CD1 decides alone; CD2 and F-CD's CD2 leg print as DESCRIPTIVE; P2 carries the qualifier | `ds = a and b` reads only eta2_b vs the RWS p97.5 and the composition bar. The CD2 and F-CD lines say DESCRIPTIVE / "no falsifier verdict". P2 carries the B-CD2 qualifier. Support (f) is re-worded. BUT own mutant E1 (CD1 also requires CD2 > 0) SURVIVES: no test case asserts CD1 with CD2 = 0 | CONFIRMED (code); test gap | MEDIUM (T-CD2) |
| D5 | F-CD is re-tied to CD1 (the registrar's completion, flagged) | The instrument prints no F-CD-of-record line. The CD1 NOT line says "FAILS for DIFFICULTY-STRATA, rule 8". The CD2-leg line "no falsifier verdict" must not be read as F-CD having no verdict | PARTLY | LOW (R-3) |
| D6 | the per-task floor table equals the standard formats | Checked against multicorpus_cache_v1.db corpus_questions (mode=ro&immutable=1): the count of distinct "(X)" option letters in each item's text, all items of each task. The table keys match the split's stratum_domain (24 BBH + 3 MUSR present; expected unlisted count 0). These agree: boolean_expressions, causal_judgement, formal_fallacies, navigate, sports_understanding and web_of_lies 2 (text yes/no); hyperbaton 2 (250/250); snarks 2 (177; 1 item reads as 1); disambiguation_qa 3 (247; 3 items at 4); logical_deduction and tracking 3/5/7 (250 each); penguins 5 (145); ruin_names 4 (248); salient 6; temporal 4; MUSR murder 2, team 3, object_placements variable -> 0. **Wrong:** movie_recommendation is 5 in the table, but 232 / 250 items have 4 options (18 have 5): the floor is 0.20 where it should be 0.25. Flip cells BBH:n00000066 (39 / 39 EVAL items) and n00000067 (36 / 36) are exactly this task (2 of the 7; SPLIT-2 eval view). reasoning_about_colored_objects is 18 in the table, but the option count varies: 18 options on 118 items, 17 on 57, 7 on 48, 2 on 27 (by the table's own rule, variable -> 0). date_understanding has 6 options on 212 items and 5 on 38 (flip cell n00000105: 33 items). geometric_shapes is listed as 0 although it is MC with 10-11 options (conservative, consistent with the rule) | REFUTED for 2 tasks | MEDIUM (C-CD1) |
| D7 | the sensitivity is isolated from the registered CD2 | Own stream flip_seed + 2, local I2, TRAIN-only theta (Y41, Y45 and E2 KILLED). Own E3 (the sensitivity count overwrites st["cd2"]) SURVIVES because the fixtures give equal counts. The code reads correctly; CD2 is descriptive | CONFIRMED (code); test gap | LOW |
| D8 | selftests and mutants | cell_strata_eval 9/9, cell_difficulty 8/8, resp_profile_info 8/8. Builder mutants: CS 45/45 and CD 45/45 KILLED, C00 controls survived. Prior decisive O5 and O6: KILLED | CONFIRMED | - |

### Own mutants (delta; `E:/TaxoArena_tmp/rev_resp_d/own_mutants_d.py`, in-memory harness RSC.run_mutants)
- O5 / O6 (prior decisive, re-run) -> KILLED (e2e) - decisive
- D1 CS: NEYMAN passes np.arange(H) (escapes the shuffle) -> KILLED (e2e) - descriptive arm
- D2 CS: STRAT-AF passes np.arange(H) -> KILLED (e2e) - decisive
- D3 CS: cell_blocks returns the cell id (the shuffle is inert) -> KILLED (order, e2e) - decisive
- E1 CD: CD1 also requires CD2 > 0 -> **SURVIVED** - decisive path (T-CD2)
- E2 CD: the sensitivity's TRAIN theta uses the registered floors -> KILLED (e2e, null_e2e) - descriptive
- E3 CD: the sensitivity count overwrites st["cd2"] -> **SURVIVED** - not decisive (CD2 is descriptive)

### Defects and fixes (delta)
- **C-CD1 (MEDIUM, before the run).** TASK_OPTIONS: movie_recommendation 5 -> 4; reasoning_about_colored_objects 18 -> 0 (variable); state date_understanding as 6 on 212 items and 5 on 38. Better: take each item's option count from its own "(X)" lines (this reads no outcome). Update the by-value asserts in st_branches. If this is not fixed, the TASKFLOOR lines are NOT REPORTABLE and the outcome says why.
- **T-CD2 (MEDIUM, test gap on the deciding path).** Add `RSC.need(J(_syn(cd2=0)), "CD1: DIFFICULTY-STRATA")` to st_branches (this kills E1).
- **T-CD3 (LOW).** Assert `st["cd2"] == sum(r["multi"] for r in st["flips"])` in e2e, or give the fixture unequal counts (this kills E3).
- **R-3 (LOW, post-run duty).** F-CD of record (the registrar's completion, flagged) is read from the CD1 line: it FIRES iff CD1 reads NOT-DIFFICULTY-STRATA. The printed "no falsifier verdict" refers to the CD2 leg only.
- These fixes are small. A delta check of C-CD1 + T-CD2 (the diff plus mutants E1 and Y40) is enough.

### Registrar brackets owed
- **B-CS (CELL-STRATA-EVAL, before the run):** CS-R1 as amended by D-CS1 (on each draw: source blocks in sorted order; a uniform permutation of the cells within each block; block = the modal stratum source of the cell's EVAL items, ties to the sorted-first; stream permutation -> u -> keys; HT pi unchanged; CS-R2 seeds unchanged). CS-R3 (IRT-ANCHOR = k-means on (a, b)). CS-R4 ("gp-IRT-style (reading)", not tinyBenchmarks' exact estimator). CS-R5 (NEYMAN: S_h floor 0.05, cap and re-allocation). CS-R7 (two-level model x draw bootstrap with draw indices shared across arms).
- **B-CD9 (CELL-DIFFICULTY):** CD-R8 (CD2 and F-CD's CD2 leg printed as descriptive) and CD-R9 (per-task floors DESCRIPTIVE on stream flip_seed + 2, with the table or per-item counts corrected under C-CD1) as readings of record; R-3 as a post-run duty.

### Commands (delta)
```
git diff --stat c7506ede..b2d05f34; git diff --name-only c7506ede..b2d05f34 | wc -l            # 2 files
cd .claude/worktrees/resp-structure-trio; for f in resp_structure_common resp_profile_info cell_difficulty cell_strata_eval; do git hash-object tools/analysis/$f.py; git rev-parse b2d05f34:tools/analysis/$f.py main:tools/analysis/$f.py; done
git grep -n 'strat_draws\|systematic(' b2d05f34 -- tools/analysis                                 # every caller
TMP=TEMP=TMPDIR=E:/TaxoArena_tmp/rev_resp_d/sbx python tools/analysis/{cell_strata_eval,cell_difficulty,resp_profile_info}.py --selftest | --mutants   # logs E:/TaxoArena_tmp/rev_resp_d/*.log
python E:/TaxoArena_tmp/rev_resp_d/own_mutants_d.py cs|cd
python E:/TaxoArena_tmp/rev_resp_d/order_sim_d.py 1|2|3                                          # TRAIN-only order proxy
# option counts: corpus_questions (mode=ro&immutable=1), len(set(re.findall(r'\(([A-R])\)', text))) per item, by (source, domain)
# flip-cell tasks: af_cells.tsv x data_v2/REG_ARCHV2-SPLIT-2_*/eval_view_REG.db side.stratum_domain (EVAL)
```
This delta has no real-data run: the changed code runs only after the EVAL key is read, the dry-run path is unchanged, and RESP-PROFILE-INFO was running. Zero calls.
