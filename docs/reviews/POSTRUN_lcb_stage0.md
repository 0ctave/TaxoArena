# POST-RUN REVIEW: LCB-STAGE0-INTERACTION, the analysis of record (3bcc9ab, branch lcb-build-2, NOT MERGED)

Reviewer: adversarial-reviewer, 2026-09-25. Zero LLM calls. All evidence was read read-only: every DB was opened `mode=ro&immutable=1`, and the one tool run was pool_guard, which is itself immutable. Before and after my reads, `ls -la --full-time` of the worktree caches, the dag file and every DB under TAXOARENA_LCB_ROOT is IDENTICAL (diff empty), and the worktree `git status --short | wc -l` = 0.

## VERDICT: VALID. The STOP stands as registered. It is recorded with 1 MEDIUM disclosure addendum (D1), 1 MEDIUM power/scope bracket (D2) and LOW items D3-D8. The outcome file is not re-run and not edited.

- The deciding numbers reproduce from my own code:
  - G1: T 96.689, p_T 0.0300. This is exact on the registered stream. With an independent seed at B 20,000, p_T is 0.0308 (MC SE 0.0012).
  - G2: X2 = 1, and p_X2 0.7101 is reproduced exactly by the sum formula on the registered stream. In exact rational arithmetic p_X2 is 0.7111 (D3). Either way G2 fails its 0.05 bar.
  - Support: DEFF 1.0108, n_eff 542.2 and MDE80 12.62pp all reproduce.
- The verdict does not move under any recomputation I ran.
- STOP applies ONLY within the stated scope and power (D2). It is never "no interaction". The data carry weak evidence of a small interaction: p_T 0.030, S1 0.0095, Z1 0.0225, and the joint-fit diagnostic 0.0195.
- Merge: the outcome is MERGEABLE AS RECORDS BY PATH (item 5). The Kotlin, its tests and `experiment_configs/lcb_stage0/*.toml` are NOT MERGEABLE: D9 is open (d7eca94), and the toml would fail main's ConfigParsesTest.

## Objects and pins (hash kind named)

| object | pin |
|---|---|
| outcome `experiment_results/lcb_stage0/lcb_stage0_outcome.txt` | blob:8fbdb07f7d6d6e62abfe60396ad66edff554fc1c; sha256 b18c6f8bb20d5178... (0 CR, so LF = file bytes) |
| `analysis_run/pins.json` | sha256 bd9770fce36e0946... (LF, 0 CR); blob dd330fc10356 |
| `analysis_run/analysis_stdout.txt` | sha256 e9f954f3c336c1a5... |
| `analysis_run/analysis.log` | byte-identical to the stdout; NOT committed, because `.gitignore:111 .claude/` covers it |
| commit | 3bcc9ab (parent 087e43d), 3 files; `git merge-base --is-ancestor 3bcc9ab main` rc 1 |

- **Code executed.** All 10 files of `tools/analysis/lcb_stage0/*.py` are blob-equal to the READY'd 4497373 (`git hash-object` vs `git rev-parse 4497373:<path>`: 10/10). `git diff --name-only 4497373 3bcc9ab -- tools/ | wc -l` = 0.
- **Ordering (R8).** The analysis ran 16:08:01-16:08:11. D9's S12 ended at 15:55:21 (docs/reviews/POSTRUN_lcb_d9.md L50-L51), so the analysis started after S12, as required.

## Per-claim table

My scripts are in the session scratchpad `pr_lcb/`, all run with `python -B`. Each is listed with the first 16 hex of the sha256 of its file bytes:
- `indep.py` 7904227b42ba7c73. Own loaders, own P6 region rule, own marginal fit (scipy L-BFGS plus Newton polish on the penalised marginal quasi-likelihood, NOT EM), own Rasch fit, own strata, own family permuter, own G2 loop, own DEFF.
- `x2gap.py` b53d049f6b71efa4. X2* three ways: my loop, the sum formula, and exact Fractions.
- `sens.py` 625126fed54a97f2.
- `comp.py` 1e4e264f256835bd.
- `ties.py` 490278048c4dce6b.

| # | claim (outcome) | result | command | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | G1 T = 96.689 at the family-majority labelling; own-region 100.057; 3 split families of 510; 10 strata | CONFIRMED | indep.py | 96.689 / 100.057 / 3 / 510 / 10 | - |
| 2 | p_T = 0.0300, B 2000, registered stream "LCB-STAGE0-PERM:cc7a6d7f..." | CONFIRMED to the digit; independent seed CONFIRMED | `indep.py 2000 20000 "POSTRUN-LCB-S0-INDEP:reviewer-2026-09-25"` | 0.0300 exact. Independent seed, B 20,000: **0.0308**, MC SE 0.0012. Null mean / sd of T* 83.140 / 6.587 | - |
| 3 | Rasch T 108.862, p 0.0750 | CONFIRMED | indep.py | 108.862; 0.0750 exact; independent seed 0.0728 | - |
| 4 | G2 X2 = 1, pair (O3-Mini-2025-01-31 (High), XBai-o4-medium); null median 1.0; X1 3; X2 over n = 10 pairs 0; X2 without frontier-frontier pairs 0 | CONFIRMED | indep.py | 1 / same pair / 1.0 / 3 / 0 / 0 | - |
| 5 | p_X2 = 0.7101 | PARTLY | x2gap.py | Sum formula (the build's) **0.7101**. My float loop **0.7031**. EXACT rational **0.7111**. The three disagree on 64 of 2,000 permutations: legs at exactly the 0.05 floor are resolved by rounding. The verdict is unaffected (bar 0.05) | LOW (D3) |
| 6 | 548 informative of 630 TRAIN (all-pass 61, all-fail 21); M 26; cells 14,248 | CONFIRMED | indep.py | 548 / 61 / 21; 26 x 548 = 14,248 | - |
| 7 | K = 3 regions [n00000004, n00000010, n00000011]; TRAIN [264, 229, 137]; GATE [48, 36, 27]; informative [238, 208, 102]; merges as printed | CONFIRMED (own P6) | indep.py | identical, including merge order 26(57) -> 8, 20(65) -> 10, 9(100) -> 4 | - |
| 8 | TRAIN-ONLY: 630 distinct leaf queryIds, 630 TRAIN, 0 GATE / EVAL, 0 unresolved | CONFIRMED | indep.py | 630 / 630 / 0 / 0 | - |
| 9 | Routing agreement 608 / 630 | CONFIRMED, with a note | indep.py | 608 when "routed leaf is ANY member leaf". The snapshot graph lists 643 leaf memberships for 630 distinct ids: **13 TRAIN texts sit in two leaves**. A single-leaf reading gives 603 | LOW (D8) |
| 10 | Null fit converged, max \|grad\| 9.49e-07, 198 EM iterations, max s 4.232 | CONFIRMED (different optimiser, same optimum) | indep.py; the build's `ST.fit_null` on the same Y as a cross-check | My max \|grad\| (a, s) 1.4e-13, max s 4.232. pihat max \|diff\| vs the build's EM fit **6.0e-08** | - |
| 11 | Measured DEFF median 1.011 (q90 1.045, max 1.152, 325 pairs; Kish 1.241); n_eff 542.2; v 0.1834; MDE80 12.6pp | CONFIRMED (re-measured from the cache's own family sizes, own loop) | indep.py | 1.0108 / 1.0447 / 1.1519 / 325 / 1.2409; n_eff 548 / 1.0108 = 542.2; v 0.1834. SE(DiD) = sqrt(1.0108 x 0.1834 x 2 x 3 / 548) = 0.04505, so MDE80 = 2.80 x 0.04505 = **12.62pp** | - |
| 12 | Single-contrast class (9 n = 10 models, 36 pairs, median v 0.1765): MDE80 12.4pp, DESCRIPTIVE-ONLY | CONFIRMED | indep.py | v10 0.1765; MDE80 12.37pp > 10pp, so DESCRIPTIVE-ONLY. The registered synthetic v for this class was 0.0675 (MDE 8.6pp). Measured is 2.6x that | feeds D2 |
| 13 | Sensitivities: S1 p_T 0.0095 (517), S3 0.0325 (548), Z1 0.0225 (548) | CONFIRMED (G1 only) | sens.py | 0.0095 / 0.0325 / 0.0225 exact. NOT recomputed: Z2, S2, the sensitivities' p_X2, R-REP, Delta-D, the joint p_T | - |
| 14 | Comparators (descriptive): tree z 7.35, excess 1.1625; C-FD z 3.66, excess 0.4878; C-KM median excess 0.9320 | CONFIRMED with the build's dhat; PARTLY with mine | comp.py; the build's `common_null_summary` on my pihat | With the build's dhat: 7.3516 / 1.1625, exact. With my dhat: tree 7.51 / 1.1644, C-FD 3.86 / 0.4959, C-KM median 0.9324. The cause is tie-breaking among exactly tied dhat (D7). Q6 is unaffected: 1.16 > 0.49, and 1.16 > 0.93 | LOW (D7) |
| 15 | Q7: the root does not certify | CONFIRMED | comp.py (site-null CSV) | root n00000001: observed_sep 0.063907 < p95 0.102432, cert false; 0 of 6 sites certified | - |
| 16 | Q1: depth-1 split = input format at >= 90% purity | CONFIRMED | indep.py | n00000004: 261 functional / 3 stdin. n00000005: 363 stdin / 3 functional. Purity **0.9905** | - |
| 17 | Q1-Q8, F1-F4 scored | CONFIRMED against section 7 / section 8 and the registrar's rule-8 reading (L17974) | read score() L614-L650 against the numbers above | Q1 H, Q2a H, Q2b F, Q3a F, Q3b F, Q4a F, Q4b F, Q4c H, Q4d F, Q5 UND (not GO), Q6a H, Q6b H, Q7 F, Q8 H. F1 FIRED; F2-F4 NOT FIRED. All as printed | - |
| 18 | STOP wording = the amended registered sentence; "Never 'no interaction'" | CONFIRMED | a string test against docs/judge_v2_program.md | The amended L17772 sentence is present verbatim in both the programme and the outcome, and the "Never" clause is present. Section 12 "does NOT show": 8/8 lines verbatim | - |
| 19 | F1 text | PARTLY | `grep -c "at the stated power" lcb_stage0_outcome.txt` = 0 | FALS_TEXT drops the registered "namely the web survey's reading that LCB is a corpus where models excel on different branches of a text-derived partition **(at the stated power)**" (programme L17844, the verbatim text) | LOW (D4) |
| 20 | pins.json faithful to the window's [OUTPUT PINS] | CONFIRMED | `grep -n "OUTPUT PINS" -A5 window_rerun/00_window.txt` (L229-L233) vs pins.json | snapshot id and 4/4 values equal. dag 1fa662d5 (LF = file). snapshots.db af75292a. embeddings ea422039. Site null 5db716c2 = the CRLF file bytes (LF 65f50739..., blob cf90314e), as L19275 7(d) states. Every on-disk input re-hashes equal now | - |
| 21 | Every hashed input matches; no unpinned input read | CONFIRMED | `sha256sum` of the TAXOARENA_LCB_ROOT DBs and the manifests; read of load_inputs / load_tree / load_vectors (analysis.py L124-L262) | texts DB 5f8ae5d8 = manifest; train_gate 7ac91273 = outcomes manifest; the manifests are those committed (status 0). Read: the texts DB (all 1,055 texts, EVAL texts hashed for the membership check only, as the READY allows); train_gate; the 5 manifests; the build dag / snapshots / embeddings; the site null. `cat analysis.py stats.py common.py \| grep -c eval_sealed` = 0 and `grep -c eval_texts` = 0. The construction DB is not read by the analysis | - |
| 22 | Sealed EVAL untouched (H3; the delta READY's re-check) | CONFIRMED | `sha256sum lcb_v6_eval_sealed_266d26872c31ce00.db` | 74ea30e5898384bd... = ingest_outcomes_manifest "eval_sealed.sha256"; mtime 08:20:33, before the window and the analysis; unchanged across this review | - |
| 23 | GATE export pool p94b63cd78524813b | CONFIRMED | `python -B tools/analysis/pool_guard.py --pool p94b63cd78524813b --db <construction db> --id-file window_rerun/gate_export_...json` | rc 0: "OK ... reserved_pool rows ... agree; keys=3 ids=111 judgeable=111 sentinels=0". The construction DB sha is d621f277... before and after | - |
| 24 | Split words | PARTLY | outcome DENOMINATOR line | The outcome prints "(words: id-disjoint only until R4)". R4 was MET at dfeb9b3 (programme L18545), so the words of record are "content-closed under CK-CLOSE-v2 (R = 6 policy)". This is a stale hard-coded string. It understates; it does not overclaim | LOW (D6) |

## Q4: the missing R10 / 7(b) / 8 disclosures (operator's deviation 2)

- **Absence proved by count** (`grep -c <term> lcb_stage0_outcome.txt`). Each of the following terms reads 0:
  - "115023", "35a92b94", "aborted", "fbd96139", "6b9fc7c";
  - "embedded twice", "data-steward", "lcb$B", "foreign selftest", "11:48".
- The DISCLOSURES block has exactly 4 bullets (`grep -c "^  - "` = 4): the D8 EVAL read, the one-shot limit, SAFE_AFTER, and the (vii) leg.
- **Cause.** This is not a render() bug that drops supplied input. There is no input path at all:
  - `DISCLOSURES` is a module-level constant tuple (analysis.py L85-L98);
  - render() appends it plus the (vii) line (L797-L801);
  - `main()` has no `--disclosure` argument (L862-L870).
- **Why nobody caught it.**
  - The RERUN READY (docs/reviews/READY_lcb_stage0.md, section 2, R10), written by this reviewer role, required "The outcome carries a DISCLOSURES line" on an analysis whose renderer was already READY'd and pinned at 4497373. It did not check that the pinned renderer could emit it, and it did not prescribe a mechanism.
  - The registrar's 087e43d record (L19273ff, item 9) carried R10 forward and added 7(b) and 8. It did not check either.
  - Both are READY-side misses: a requirement placed on a write-once object that its fixed code cannot satisfy.
- **Severity: MEDIUM.**
  - No number or verdict is affected.
  - The facts are of record in the programme (L19241ff items 1-4, L19273ff items 7(b), 8, 9) and in the committed window logs (b3e8c94 `window/`; 087e43d `window_rerun/00_window.txt`).
  - But the outcome of record is silent on an aborted construction of the same arm, a restored DB, and a re-embedding. A reader of the outcome alone cannot see that the tree of record is the SECOND build.
- **Remedy.** Do not edit the write-once file. Do not re-run the analysis: a second outcome would be a second analysis.
  - (a) THE REGISTRAR'S OUTCOME RECORD carries a dated block "DISCLOSURES ADDENDUM TO lcb_stage0_outcome.txt (blob:8fbdb07f; the renderer had no input path)" with every R10 item, 7(b) and 8, each with its source line:
    - the aborted window 11:48-11:50, snapshot 20260925_115023_Headless_Run_Auto_ge, dag sha256 35a92b94c0b4b62d...;
    - the cause: the guard re-ran at the trickle's second fetch; the refusal was swallowed at HeadlessBenchmarkRunner L922 and surfaced at L1344;
    - the construction DB renamed as evidence and restored to fbd96139... from the L3 backup;
    - the rerun from a fresh worktree at 6b9fc7c;
    - the TRAIN texts embedded twice, locally, by the same Ollama model, with only the rerun's cache read;
    - the first window's foreign selftest (PIDs 56164 / 44576);
    - 7(b): the run-operator, not the data-steward, checkpointed the construction DB (d621f277...);
    - 8: the stray empty 'lcb$B' file created and removed at 12:20:44 / 12:21:48.
  - (b) The ledger row's chip carries "disclosures: see addendum".
  - (c) Optional: an addendum file beside the outcome under a NEW name (e.g. `lcb_stage0_outcome_DISCLOSURES_ADDENDUM.txt`), committed by path and referenced by the record. It never overwrites the outcome.
  - (d) For any future write-once renderer: a READY that adds an outcome-text requirement after the renderer is pinned must name the mechanism (an input file hashed into the outcome, or a registrar addendum) in the same ruling.

## Q5: deviation 1 (ran from the worktree; the outcome sits on the branch)

- **ACCEPTABLE, and forced.**
  - `git ls-tree -r --name-only HEAD | grep -c lcb_stage0` on main = 7 files, none of them the analysis code or the manifests. main holds only 2 reviews and 5 D9 helpers.
  - `load_side` refuses uncommitted manifests.
  - So the analysis can run only in a checkout holding the branch.
- **What ran is what was READY'd.**
  - The code is blob-equal to 4497373 (10/10).
  - The inputs equal the window pins (claim 20).
  - The outcome path is `C.ROOT/experiment_results/...` of the checkout that ran it. The READY's R9 command form, with paths relative to main, could not have run on main.
- **Landing it on main while the LCB code merge is NOT READY (D9 open; d7eca94: C1 FAILED, non-determinism, D9b recommended):**
  1. **The result lands through the registrar's outcome record on main**, which is the record of truth. It cites 3bcc9ab, blob 8fbdb07f and sha256 b18c6f8b, and includes the D1 addendum and the D2 bracket. This needs no code merge.
  2. **Evidence by path, records only.** Use `git checkout 3bcc9ab -- <explicit file list>` from the main checkout, then `git commit -- <paths>`. The paths:
     - `experiment_results/lcb_stage0/{lcb_stage0_outcome.txt, analysis_run/pins.json, analysis_run/analysis_stdout.txt, site_null_lcb_af512.csv, manifests/*, window_rerun/*, window/*, lcb_af_bareq512_s42/**, ingest_*_transcript.txt}`.
     - Optionally `tools/analysis/lcb_stage0/*.py`: Python, not D9's object, blob-checked against the 4497373 pins.
     - After the commit, verify every landed blob equals `git rev-parse 3bcc9ab:<path>`.
     - Main's 5 `experiment_results/lcb_stage0/d9/helpers/*` must survive: they are absent on the branch. A path checkout does not delete them; a directory copy with delete, or a reverse diff, would.
  3. **NOT to main until D9 (or D9b) is discharged:**
     - `src/main/**` (4 files) and `src/test/**` (3 files);
     - `experiment_configs/lcb_stage0/lcb_af_bareq512_s42.toml`. `ConfigParsesTest."every committed config parses with no unknown keys"` (L33-L48) walks every `experiment_configs/**/*.toml`. On main, `datasetType = "LIVECODEBENCH"` is an unknown value, and configs are fail-closed, so landing the toml alone would break main's suite.
     - The `.toml.template` and `lcb_gate_ids.json` are not walked, but should travel with the toml.
  4. **Protect 3bcc9ab** until the path merge lands, e.g. with a tag. That is the orchestrator's call, because it is a git write. A worktree removal plus branch deletion would otherwise leave the outcome commit unreachable.

## Q6: what F1 means for the framework (scope, stated carefully)

- **What is overturned.** On LiveCodeBench v6, with this 26-model roster (16 n = 1, 9 n = 10, 1 n = 4 files), the 548 informative TRAIN problems of the one registered draw, and ONE tree recipe (anchor-free, label-free, 512 / 0.0145 / mcs 55 / seed 42), the premise is overturned that models excel on different text-derived branches beyond difficulty slope and input format at the registered strength. So the judged stage (~8.5k cce) is NOT registered on LCB. F1 is correctly FIRED.
- **What this partition actually tested.** It is narrower than "K = 3 regions":
  - TRAIN by region x format: region 0 = 261 functional + 3 stdin; region 1 = 227 stdin + 2 functional; region 2 = 136 stdin + 1 functional.
  - Informative: 235 + 3 / 206 + 2 / 101 + 1.
  - In the 5 functional strata, 226 of 229 families carry region 0. The permutation is nearly degenerate there, so LeetCode contributes almost nothing to T - T*.
  - G1 is therefore, in effect, ONE text-derived binary split of the AtCoder / Codeforces problems (206 vs 101 informative), plus 6 stragglers. TREE=FORMAT reads "no" only because of those 6 stragglers and that one stdin split.
  - The negative is about that split. It says nothing about finer or other partitions of LCB.
- **What the power supports.**
  - Stated power (synthetic, real-roster ruling): G1 alone 0.91-0.99 at tau 0.20 and 0.55-0.75 at tau 0.15; GO 0.57-0.85 at tau 0.20.
  - The STOP therefore bounds an interaction of about 0.2 logit SD or more. It does NOT exclude tau of about 0.15, which is missed 25-45% of the time.
  - The observed p_T 0.030 (independent 0.0308) is compatible with a small true interaction, and so are S1 0.0095 (below 0.01), Z1 0.0225 and the joint-fit diagnostic 0.0195.
  - These are sensitivities and diagnostics: none moves the verdict, and G1 is read at 0.01 by registration, where the ruling measured it mildly liberal at 0.05 (0.075).
  - G2: X2 = 1 against a null median of 1, so there is no excess of practical (10pp) reversals.
  - A single 10pp DiD cannot be scored: MDE80 is 12.4pp for two n = 10 models and 12.6pp for the median pair.
- **What is NOT overturned:**
  - the specialised-vs-generic-judge question as such: no judge was involved (section 12, line 1);
  - any other corpus. The MMLU-Pro R2 atlas model x domain interaction (p_perm 0.002; designed domains; judged board) stands;
  - EVAL, other rosters, other trees or recipes of LCB (A8: one arm; the boilerplate-stripping arm was left for a later registration);
  - interactions below about 0.2 logit SD;
  - model x FORMAT structure. Under the common null (no format strata), C-FD z is 3.66 and the tree's is 7.35. These are descriptive only, but they show that the model x region structure the tree carries is largely format, which the registered null absorbs by design.
- **Words for the synthesis.** "STOP on LCB v6 at the stated power: no model x text-region interaction of about 0.2 logit SD or more beyond difficulty slope and input format, on the one within-stdin split the tree produced (p_T 0.030 against the 0.01 bar; S1 0.0095). Never 'no interaction'. The judged stage is not registered on LCB."

## Defects

- **D1 MEDIUM: the R10 / 7(b) / 8 disclosures are absent from the write-once outcome.**
  - The renderer's disclosure block is a constant with no input path.
  - The RERUN READY's R10 and the registrar's 087e43d item 9 imposed the requirement without a mechanism.
  - Fix: see Q4 (registrar addendum; no edit, no re-run).
- **D2 MEDIUM: the power and scope statement is synthetic and was not re-derived at readout.**
  - (i) The single-contrast v was measured at 0.1765 against the synthetic 0.0675, 2.6x. The median-pair v, 0.1834 against 0.19-0.20, is close. The registration's U6 ("every synthetic size and power figure, re-read at the real M, v, DEFF and informative count") was never discharged for G1 power. "~0.2 logit SD at 80%" is therefore UNVERIFIED at the measured variance and likely optimistic.
  - (ii) The effective design is one within-stdin split (Q6), not the K = 3-4 geometry of the synthetic worlds.
  - Fix:
    - the registrar's outcome record brackets the STOP sentence as "synthetic power; not re-derived at the measured v; effective contrast one within-stdin split";
    - it prints the independent p_T 0.0308 ± 0.0012 and the S1 / Z1 / joint values beside it;
    - optionally, before the sentence is quoted in the thesis or paper, a zero-call re-simulation of G1 power at the measured design (the real region x format composition, the measured v per n-class).
- **D3 LOW: p_X2 depends on floating-point tie resolution at the 0.05 leg floor.**
  - Build 0.7101; exact 0.7111; my float loop 0.7031. The three disagree on 64 of 2,000 permutations.
  - Cause: Y is k/n with n in {1, 4, 10}, so pair differences are multiples of 1/20 and a region gap of exactly 0.05 occurs.
  - The observed X2 is 1 in all three. The verdict is unaffected.
  - Fix: in any reuse, compute the G2 legs in integer arithmetic (x20) and compare squared SEs exactly.
- **D4 LOW: the F1 falsifier text drops a registered qualifier.**
  - FALS_TEXT["F1"] (analysis.py L670-L671) omits "namely the web survey's reading ... (at the stated power)".
  - Rule 3 requires the chip to carry the narrative's qualifier.
  - Fix: the registrar quotes F1 in full in the outcome record and the ledger chip.
- **D5 LOW: the outcome's hash kinds are unlabelled and mixed (rule 8).**
  - INPUTS prints split_side.tsv as its LF sha, f0a694b2 (from the manifest).
  - It prints split_manifest.json ab350c13, ingest_texts_manifest 4d3b4633, ingest_outcomes_manifest 5d09cc53, construction_manifest b720d912 and the site null 5db716c2 as CRLF file bytes.
  - The LF renderings of record are, in the same order: 8a655d58, 7ec76d95 (= the READY's pin), 009938c1, bf5531e3 and 65f50739. The blobs are 43485850, 3410f7f4, 40587941, effdcce2 and cf90314e.
  - dag_snapshots.jsonl and the outcome itself have 0 CR.
  - Fix: the registrar record names each kind and prints the LF rendering beside it.
- **D6 LOW: stale split words** in the DENOMINATOR line ("id-disjoint only until R4"; R4 was met at dfeb9b3).
  - Fix: the registrar's record uses "content-closed under CK-CLOSE-v2 (R = 6 policy)".
- **D7 LOW: dhat ties are broken by fit-convergence noise.**
  - The Rasch problem effect is a function of the column total, so 431 of 548 informative problems sit in 113 exactly tied groups.
  - The build's dhat differs from mine by at most 4.3e-10. That noise, not the surrogate order stats.py L469 intends, decides which tied problem falls on which side of a quantile cut.
  - Primary strata: 0 bins differ between the float order, exact ties by surrogate order, and the column-total order. Across 20 random tie-breaks, p_T ranges 0.0265-0.0380 (median 0.0330), and 0/20 fall at or below 0.01. The G1 FAIL is robust.
  - Common null (descriptive): tree z 7.35 vs 7.51, C-FD 3.66 vs 3.86. Q6 is unaffected.
  - Fix: round dhat, or bin on the column total, with an explicit surrogate tie-break.
- **D8 LOW, note: 13 TRAIN texts are members of two leaves** in the snapshot graph (643 memberships, 630 distinct ids).
  - The routing agreement 608 counts "any member leaf".
  - Regions come from argmax routing, which is a partition, so no statistic is affected.
  - Fix: disclose in the record.

Also noted, not a defect: the R-REP line says "power as registered at M ~35". That is accurate as a pointer, and it is an annotation only.

## Commands (reproduction)

| check | command |
|---|---|
| code identity | `git hash-object tools/analysis/lcb_stage0/<f>.py` vs `git rev-parse 4497373:<path>` (10/10) |
| G1 / G2 / DEFF / MDE | `python -B pr_lcb/indep.py 2000 20000 "POSTRUN-LCB-S0-INDEP:reviewer-2026-09-25"` (output `pr_lcb/run1.out`) |
| p_X2 gap | `python -B pr_lcb/x2gap.py` |
| sensitivities | `python -B pr_lcb/sens.py` |
| comparators, Q7 | `python -B pr_lcb/comp.py`; `comp_r.py` (rounded dhat); the build's `common_null_summary` on my pihat |
| tie robustness | `python -B pr_lcb/ties.py` |
| input pins | `sha256sum` of the pinned files and DBs; `tr -d '\r' \| sha256sum` for the LF renderings; `git hash-object` |
| sealed EVAL | `sha256sum lcb_v6_eval_sealed_266d26872c31ce00.db` = the manifest; `cat analysis.py stats.py common.py \| grep -c eval_sealed` = 0 |
| pool | `python -B tools/analysis/pool_guard.py --pool p94b63cd78524813b --db <construction db> --id-file <gate export>` rc 0 |
| disclosure absence | `grep -c <term> lcb_stage0_outcome.txt` for 11 terms, each 0; `grep -c "^  - "` = 4 |
| no write | `ls -la --full-time` before and after, diff empty; `git -C .claude/worktrees/lcb-build-2 status --short \| wc -l` = 0; no `__pycache__` created |
| toml on main | `src/test/kotlin/taxonomy/runner/ConfigParsesTest.kt` L33-L48 walks `experiment_configs/**/*.toml` |
