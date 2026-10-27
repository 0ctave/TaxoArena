# READY review: OOS-BASELINES (oos_baselines.py) and GOLD-LEVEL-EMB (gold_level_emb.py)

Reviewer: adversarial-reviewer, 2026-10-02. Branch oos-gold, tip a625a957 (worktree .claude/worktrees/oos-gold); main at af3def2a
(the registrar's 1a922a80 and d635fec5 are ancestors of main; neither script exists on main yet). Zero calls; nothing run of record.
Registrations: prog L23342-L23375 (OOS-BASELINES) and L23377-L23422 (GOLD-LEVEL-EMB), _as_of a625a957, headings re-grepped
(2 line-anchored hits on main). Records docs/agents/results/{OOS-BASELINES,GOLD-LEVEL-EMB}.json (state registered).

## Verdict

- **oos_baselines.py blob:7e74108dedcb2d921be0da4cf8ddc842deb24d72 (LF; working tree LF, no CRLF rendering): READY for --run**,
  conditions C-1, C-2, C-5.
- **gold_level_emb.py blob:867657643886b5efff37bd7dec0a813bdace6e33 (LF; working tree LF): READY for --run**, conditions C-1, C-3..C-6.
- Pre-data brackets owed by the registrar BEFORE either --run (insertion only): R-1 (OB-d Support arithmetic), R-2 (seen-carried
  family verdicts), R-3 (the builder's readings OB1, GB1, GB2 confirmed). None moves a criterion, a bar or a verdict line.

## Per-claim table (deciding claims)

| # | claim | my number / evidence | status | sev |
|---|---|---|---|---|
| 1 | OOS denominators n_in 6,672 / 6,672 comp., n_OOS 1,350 / 1,350, Kish 1.0000 / 1.0000 | own SQL on the ingest DB (ro, immutable): 6,672 / 6,672; 1,350 / 1,350 (all side EVAL; hash sides 408 EVAL / 136 GATE / 806 TRAIN); dry-run MATCH | CONFIRMED | - |
| 2 | OOS identity: S0 A 0.97437 / 0.97263 / 0.97601 / 0.97446 / 0.97649, A(a) 0.97640, FPR95 0.1578 at 0.74326 | my dry-run: all reproduced to the digit, by c2 AND by this script's refits | CONFIRMED | - |
| 3 | OB1: c2 called unchanged with the qwen3 Space in the nomic / gemma slots; those values discarded | ITS.c2 L868-L873 fits K 150 s0 on spaces[e] -> other_emb; compute() pops other_emb before any use; never printed; c2's draws asserted == S0 seed-0 draws | CONFIRMED (cost: 2 redundant qwen3 fits labelled "nomic"/"gemma" in FIT_LOG, counted in the 22-fit audit; LOW, D-4) | LOW |
| 4 | the four OOS detectors as registered, incl. (d) label-free marginal Mahalanobis | (a) centroids_by_label; (b) LW(assume_centered) on pooled within-class residuals, means not renormalised, -min_c; (c) k-th largest cos to TRAIN, k 10 fixed, 1/5/25/50 DESCRIPTIVE; (d) marginal_fit(X) only, signature asserted, non-float refused, one mean, LW of x - mu; every fit through fit_rows (TRAIN only) | CONFIRMED | - |
| 5 | OOS criteria: Delta vs 5-seed mean; SE_total = sqrt(SD(paired draws)^2 + var_seed/5); EQUIVALENT strict 90% inside +/-0.010; DIFFERENT |D|>0.010 AND 95% excludes 0; reading tables; F-OB | code L365-L431 line by line against L23363-L23367; own mutants OM1 (S0 draw = seed 0 only), OM3 (one-sided TOST) KILLED | CONFIRMED | - |
| 6 | OOS Support (d)-(f): SE 0.00288, reach 0.00284 / 0.01242 | recomputed: SE_total 0.002882; EQ reach 0.00283; DIFF reach 0.01243; var_seed 2.3323e-6 (sum sq 9.329e-6); margin ratios 5.05 / 2.59 / 0.397 | CONFIRMED | - |
| 7 | OOS Support (d') OB-d: SE_boot 0.00368, SE_total 0.00374, reach 0.00070 / 0.01315 | 0.00198^2 + 0.00313^2 = 1.372e-5 (registration prints 1.353e-5): SE_boot 0.00370 (0.003704 with HM 0.00313), SE_total 0.00377, reach 0.00062 / 0.01318. Verdict lines unchanged (OB-d DIFFERENT side SCOREABLE at -0.030) | PARTLY (arithmetic slip) | LOW |
| 8 | GOLD denominators MASSIVE 4,946 / 4,923 (Kish 1.0093), CLINC 6,672 / 6,672, Banking77 3,908 / 3,905 (1.0015) | own SQL: 4,946 / 4,923 / 1.009300; 6,672 / 6,672 / 1.0; 3,908 / 3,905 / 1.001535; dry-run MATCH | CONFIRMED | - |
| 9 | GOLD identity on the non-nomic arms | my dry-run --identity: q4 130 NMI + 32 H, q8 15, qcard 15, g 40 + 8 H, gcard 15; max dev 4.98e-07; REPRODUCED x5; nomic target count on main s0_c1.csv = 50 (2 slices x 25), checked only in --run (GB2) | CONFIRMED | - |
| 10 | GB1: "to 5 dp" read as |value - CSV| <= 5e-6 | half a unit in the 5th decimal is 5e-6; the CSVs carry 6 dp (rounding 5e-7); observed max 4.98e-07, 10x inside; mutant "tolerance 1e-3" KILLED | CONFIRMED | - |
| 11 | GB2: nomic_selection.json written (mode xb, hashed) before ANY nomic EVAL read, incl. the 256/512 identity reads | eval_idx refuses src "n" while PHASE["nomic_sel"] is None; selftest asserts min(EVAL n event) > SELECTION event by execution; dry-run "no nomic EVAL read"; rule = EDS.pick verbatim (score = mean over 3 corpora of seed-mean GATE fine NMI, TIE 0.001 to smaller d) | CONFIRMED (stricter than the registration's "at that slice") | - |
| 12 | GOLD copied-arm fixtures give SE 0 | selftest prints e.g. A GL1 qcard-q1024 massive D 0 SE 0 EQUIVALENT = oracle; no division by SE anywhere (EQ.status compares bounds); non-zero-SE cases exist (A q8-q1024 SE 0.00545; A n* SE 0.01002; A q256 clinc SE 0.01087) and carry the SE mutants | CONFIRMED | - |
| 13 | GOLD GL1: D = 30-seed mean diff; SE_total = sqrt(SD(paired)^2 + var(nA-nB)/n_s); stream = S0 C1 (BOOT_SEED + 10 corpus + level, = ITS L1392); TOST as EQ.status; family count asserted 6/2/4/4; reading order LEVEL > TRANSFORMATION > NO-LEVEL-ADVANTAGE > MIXED; F-GL / F-GL' | code L506-L577 against L23387-L23397; own GM3 (TRANSFORMATION on EMBEDDER != INVARIANT), GM4 (D over seeds 0-4) KILLED | CONFIRMED | - |
| 14 | GOLD Support (d)-(e) SE_total per contrast and reaches | recomputed all 16: equal to the registration to 4 dp (MASSIVE 0.0062-0.0068, CLINC 0.0062-0.0085; EQ reach CLINC 0.0038 (n*) - 0.0097 (q512); DIFF 0.0302-0.0322); DEFF Kish measured (S0), SE_boot TRANSPORTED (named), seed SDs measured, q8/qcard/gcard/n* SDs TRANSPORTED (named) | CONFIRMED | - |
| 15 | 30 coarse seeds, 5 fine; margins 0.010 AUROC / 0.025 NMI | SEEDS_C = range(30), selftest asserts 30/5 per arm and 540 coarse TRAIN fits; MARGIN constants asserted (ST-CONST) | CONFIRMED | - |
| 16 | 8 of 16 coarse contrasts SEEN at 5 seeds, disclosed | P1 SEEN flags True exactly on q256/q512/q4096/g768 x 2 corpora (8); printed "(SEEN: never a confirmation)"; but the FAMILY lines do not say when a verdict is carried only by SEEN statuses (DIM: all 6 SEEN) | PARTLY | LOW (R-2) |
| 17 | write-once outputs; read-only DBs | both refuse on any existing output before any read; mode "x"/"xb"; sha256 + mtime of all 7 DBs and selection.json byte-identical before/after my 3 dry-runs, 2 selftests, 2 mutant suites; no -wal/-journal; worktree clean, no output dir created | CONFIRMED | - |
| 18 | oos_plus note | SPLIT_NOTE printed in the outcome header (oos_plus, hash sides, never like-for-like with published numbers) | CONFIRMED | - |
| 19 | builder's suites | OOS --selftest 279 checks passed; --mutants 49 of 49 KILLED. GOLD --selftest 398 passed (8m18s); --mutants 49 of 49 KILLED (35 in the first pass, cut by my shell's 30-min limit, the remaining 14 re-run by name: 14 of 14) | CONFIRMED | - |
| 20 | imported readers unchanged | main and worktree blobs equal: intent_transfer_s0 f662ceb1, embed_dim_slice 068550b4, embed_quant 3930cf4b, card_protocol cdcc1dbb, split_side 05224b5a, data_v2/ro 1fdf7d75, writers 1b2abdc8 / 2788d721; identity CSVs tracked, main == worktree (nmi_matrix 1056bad9 pinned; h_table 4017c28f, nmi_q 78d58ce8, nmi_card 404d93d1, s0_c1 9bb91a80 printed, not pinned) | CONFIRMED | - |

## Own mutants (8; one line each)

- OM1 oos: S0 draw = seed-0 only, not the 5-seed mean -> KILLED (P OB-a SE_total oracle). Decisive.
- OM2 oos: identity ignores thr -> KILLED. Guard.
- OM3 oos: one-sided TOST (`or`) -> KILLED. Decisive.
- OM4 oos: kNN reference set includes GATE rows (self-match for GATE queries) -> KILLED (W OB-c Delta). Decisive.
- GM1 gold: EVAL-rows pairing guard in eval_idx off -> SURVIVED. Guard, non-decisive on these data (every DB complete, 53,148 of 53,148; the guard ran ON in my dry-run and passed). D-2.
- GM2 gold: identity accepts n == 0 compared values -> SURVIVED. Vacuity guard; non-decisive (counts printed per line). D-3, C-4.
- GM3 gold: TRANSFORMATION on EMBEDDER != INVARIANT -> KILLED. Decisive.
- GM4 gold: D over seeds 0-4 only -> KILLED. Decisive.

## Defects and conditions

- C-1 (process): merge a625a957 into main first; on main re-check `git hash-object` of both scripts = the blobs above, then run each
  --dry-run from main (it must print PIN OK, MATCH, REPRODUCED) before its --run. One heavy process: OOS first (about 0.5 min),
  then GOLD (fits priced 63 min; my dry-run took 16 min wall for a 5-seed identity pass, so allow 1.5-3 h; peak about 2.5 GB). No JVM,
  no construction, no Ollama in the window (both refuse beside a JVM).
- C-2 / R-1 (LOW, OOS Support (d')): bracket the slip: 0.00198^2 + 0.00313^2 = 1.372e-5 (not 1.353e-5); SE_boot(Delta_d) <= 0.00370,
  SE_total 0.00377; OB-d reaches 0.00062 / 0.01318. The script prints the registered 0.00374 as "planned" beside the MEASURED SE; no
  code change; no verdict line moves.
- C-3 / R-2 (LOW, GOLD seen points): bracket that a family verdict carried only by statuses whose P1 point is SEEN (DIM: all 6; EMBEDDER
  g768 x 2) is quoted with "carried by contrasts seen at 5 seeds (G-4)", and a NOT-INVARIANT via a SEEN status alone is never called a
  confirmation. The registrar applies it from the printed P1 SEEN marks and the FAMILY lines; no code change.
- C-4 (post-run reviewer): count, do not read, the identity lines: q4 130 + 32 H, q8 15, qcard 15, g 40 + 8 H, gcard 15, nomic 50
  (GM2 survives, so a vacuous identity is caught only by these counts).
- C-5 / R-3: the registrar records OB1, GB1 and GB2 as reviewer-CONFIRMED readings (rows 3, 10, 11).
- C-6 (operator, GOLD): nomic_selection.json is written before the nomic identity and after_check; a refusal there leaves it on disk and
  the next --run refuses (write-once). Its content is deterministic (GATE only, no EVAL); the operator moves it aside, quoting its sha256,
  and records the refusal in the run log; never delete silently.
- D-2 (LOW): GM1 survives: add a fixture with one EVAL vector missing in one source and assert the refusal. Not required for this run.
- D-3 (LOW): GM2 survives: add an empty-target identity case asserting the refusal. Not required for this run.
- D-4 (LOW): the two discarded c2 fits are logged as "C2 k-means nomic/gemma s0" though they are qwen3; the outcome's READINGS line
  states OB1, so no action beyond C-5.

## Exact --run commands (from the main checkout, after C-1)

```
python tools/analysis/oos_baselines.py --dry-run && python tools/analysis/oos_baselines.py --run
python tools/analysis/gold_level_emb.py --dry-run --identity && python tools/analysis/gold_level_emb.py --run
```

## Commands that show each result

```
git -C .claude/worktrees/oos-gold hash-object tools/analysis/oos_baselines.py tools/analysis/gold_level_emb.py   # 7e74108d / 86765764
sha256sum intent_*.db experiment_results/embed_dim_slice/selection.json; ls -la --time-style=full-iso intent_*.db*  # before = after (diff empty)
python - (sqlite3 file:intent_transfer_corpora_v1.db?mode=ro&immutable=1): GROUP BY corpus, side, is_oos; Kish = sum m^2 / sum m over stem_key
python - : Support arithmetic (OOS: var_seed, sqrt2 x 0.00198, Hanley-McNeil at 0.945, reaches; GOLD: 16 SE_total and reaches)
(worktree) python tools/analysis/oos_baselines.py --selftest | --mutants          # 279 ok; 49/49
(worktree) python tools/analysis/gold_level_emb.py --selftest | --mutants          # 398 ok; 35/35 + run_mutants(only=names[35:]) 14/14
(worktree) TAXOARENA_DATA_ROOT=<main> python tools/analysis/oos_baselines.py --dry-run
(worktree) TAXOARENA_DATA_ROOT=<main> python tools/analysis/gold_level_emb.py --dry-run --identity
python scratchpad/oosgold/mut.py oos_baselines | gold_level_emb                    # own mutants OM1-OM4, GM1-GM4 (full selftest each)
```
