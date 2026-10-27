# TaxoArena

<!-- Repo tidy, D-2026-10-27-1 (docs/agents/author_decisions/2026-10-27.md). Every factual line carries a
source comment: a ledger row id (docs/test_ledger.html, the last bracket wins), a record JSON
(docs/agents/results/<ID>.json) or a programme span (docs/judge_v2_program.md, "prog"), _as_of 70c61579.
This file quotes no [P-FAM] number. The History paragraph is the text the author chose (D-2026-10-27-6 A1). -->

TaxoArena studies cell-conditional evaluation of language models.
It asks when scoring models per cell of a benchmark changes which model an evaluator should use, or which pairwise comparison it may trust, compared with one pooled leaderboard.
The code is a Kotlin and Spring Boot engine with Python analysis tools.
<!-- src: prog L21446 (central question); build.gradle.kts L5, L9 -->

The arena's cells are a corpus's declared labels.
Where labels are missing, a taxonomy tree built from question embeddings on the TRAIN side of a split supplies the cells.
The record audits that tree as a filing device, a partition and a certificate.
Every claim names its verification instrument: an answer key, an executed checker, or one frozen judge recipe with its reference policy stated.
<!-- src: prog L21446 (last sentence: "Cells are declared labels for the arena, and are read by a TRAIN-only
embedding taxonomy where labels are missing"; the instrument clause); prog L21448 S1 ("the tree is audited as
filing G11/G13, M G14, partition FLAT and certificate G12") -->

Judge accuracy in this repository always means agreement with an answer key or a checker (verification fidelity).
It never means human preference.
<!-- src: prog L21448 S2 "verification fidelity only"; docs/agents/KNOWLEDGE.md section 1 (framing pins) -->

## Framing of record

The framing of record is "Cell-conditional evaluation", adopted by the author on 2026-09-27.
Its texts are [the framing](docs/agents/plans/2026-09-26_framing_of_record.md) and [the research plan, revision 2](docs/agents/plans/2026-09-27_research_plan_rev2.md); where they differ, the plan's section A1 governs.
<!-- src: prog L21435-L21445 (heading, objects of record, "the PLAN's A1 governs"), _as_of 70c61579 -->

The central question, verbatim:

> For a fixed roster, a corpus split content-closed under CK-CLOSE, and a fixed verification instrument named per claim (an answer key, an executed checker, or one frozen judge recipe with its reference policy stated): when does evaluating per cell change which model an evaluator should use, or which pairwise comparison it may trust, compared with one pooled leaderboard? What does that cost, and which answers survive a second embedder, a second tree draw and a second corpus? Cells are declared labels for the arena, and are read by a TRAIN-only embedding taxonomy where labels are missing.

<!-- src: prog L21446, verbatim, _as_of 70c61579 -->

| | sub-question (verbatim) |
|---|---|
| SQ1 USE | Does a per-cell policy fitted on TRAIN beat the best single model on content-closed EVAL, and on which (roster, corpus) pairs? |
| SQ2 TRUST | At which grain are per-cell comparisons reliable on the key and on the judge, and what sets the judge's fidelity in a cell? |
| SQ3 TAXONOMY | What does a TRAIN-only tree add beyond declared labels (filing, M, partition, certificate, label-free cells)? |
| SQ4 PRICE | What does judged trust cost as rosters grow, newcomers arrive and corpora are added, and at what realised error rate? |
| SQ5 INVARIANCE | Which answers to SQ1-SQ3 belong to the method rather than to qwen3, seed 42 and MMLU-Pro? |

<!-- src: prog L21447, verbatim, _as_of 70c61579 -->

Five scope rules bind every claim.
S1: arena cells are declared.
S2: only verification fidelity is measured.
S3: every object carries its split word.
S4: recipes are never joined.
S5: closed lines stay closed.
<!-- src: prog L21448 (S1-S5 as written there), _as_of 70c61579; docs/agents/KNOWLEDGE.md section 1 -->

## Split words

No split is called clean, disjoint or held-out unless it passed a content-key check under CK-CLOSE.
A split checked by id only is written "id-disjoint only".
<!-- src: docs/agents/CONTEXT.md section 4 rule 12 -->

| object | split word |
|---|---|
| v2 split, draw 5a3e756: pool pv2_41dbd3dbcd399df0 (MMLU-Pro, 3,492 EVAL items in 3,400 components) and pool pv2_1575de61bb20e977 (all corpora, 6,153 EVAL items in 5,642 components) | content-closed under CK-CLOSE-v2, residual disclosed |
| af_clean_s42 (anchor-free tree, R256) | content-closed |
| p2dca21ab5f4ef3ae (MMLU-Pro, 3,445 judgeable questions; the split of the tree bareq512_s42) | id-disjoint only |
| paeec37aa28063c75 (six-corpus union, 6,482 judgeable questions) | id-disjoint only |

<!-- src: docs/agents/KNOWLEDGE.md section 1 (split words); prog L21448 S3, _as_of 70c61579;
experiment_configs/reserved_pools.json (judgeable 3445 / 6482); prog L16198 _as_of 70c61579 (v2 pools: 3,400
components / 3,492 items; 5,642 components / 6,153 items; the record's counts; the pin files' counts.eval differ,
see experiment_configs/README.md; REVIEW_REPO-TIDY E11) -->

## Where the record stands

These are selected pointers, not a summary.
The record governs: each line names its ledger row, and the last bracket of that row wins.
Each result below comes from a registered test that made zero LLM calls; its ledger row says when it was registered.
<!-- src: ledger rows named below (REGISTERED chips or registration headings; "0 calls" / "zero calls" in each
sentence of record); ROUTER-REGRET-MMLU registration heading "## Registered 2026-09-11 01:30 (zero calls)";
RECORD-RECIPE-EDGE-AUDIT part 1 is a recorded fact (prog L20822) -->

**SQ1 USE**

- `V2-DECLARED-CELLS` (content-closed v2 union split).
  A per-cell policy on declared (source, domain) cells, fitted on TRAIN, beats the best single model by +2.67pp, two-stage 95% [+1.46, +3.89] (n 5,907 items in 5,404 components).
  BBH carries 0.728 of that gain.
  Leave-BBH-out (+1.03pp [-0.27, +2.32]) and the MMLU-Pro part (+0.18pp [-1.18, +1.54]) contain 0; both are descriptive.
  The record calls this a sensitivity, not a replication.
  <!-- src: ledger V2-DECLARED-CELLS (chips VALID POST-RUN 80ce082; "C1 HELD ON THE UNION'S DECLARED CELLS (n 5,907);
  BBH CARRIES 0.728 OF G; LEAVE-BBH-OUT AND MMLU-PRO CONTAIN 0 (DESCRIPTIVE)"; "A SENSITIVITY, NOT A
  REPLICATION"); V2-DECLARED-CELLS.json numbers_of_record C1_G, sentence_of_record -->
- `UNION-AF-ROUTE` (same split).
  The cells of a fresh anchor-free tree, built separately within each source, beat the best single model by +1.52pp [+0.14, +2.91] (thin; percentile interval [-0.03, +2.73]; 5,907 / 5,404).
  These cells are source-conditioned [SC], not label-free.
  Against declared labels the difference is -1.15pp [-2.19, -0.12]: a measured shortfall (descriptive), never parity.
  Against per-source k-means at matched cell counts it is -0.45pp [-1.31, +0.41], so the tree is not shown better.
  On filing, falsifier F-AK fires: the tree is not better than unsupervised per-source k-means at matched k, beyond its seed spread (under the mirrored filing fixed before the data; the registered rule would miss by 0.0002).
  One draw, one roster.
  <!-- src: ledger UNION-AF-ROUTE: bracket [CORRECTED 2026-10-04 ... SOURCE-CONDITIONED [SC], not label-free]
  (latest); [OUTCOME 2026-10-03 ...] (U1, U3b, U2, F-AK, Q1); chips "VALID (POST-RUN 589c04ae): U1 HELD (THIN);
  F-AK FIRES (MIRRORED FILING)" and "U3b SHORTFALL -1.15pp VS DECLARED, NEVER PARITY; U2 / L-1 NOT FIRED BY
  SUPPORT"; UNION-AF-ROUTE.json numbers_of_record U1, U2, U3b; does_not_show "one draw, one recipe, one roster" -->
- `ROUTE-SOURCE-NULL` (same split).
  Over a 6-cell policy that routes by source alone, those cells gain +0.51pp [-0.67, +1.68] (5,907 / 5,404): UNDETERMINED (realised MDE80 1.68pp).
  The +1.52pp lies above the 97.5th percentile (+0.49pp) of 200 random within-source cell sets (profile 183 blocks, not the registered 123), so source identity alone does not explain it either.
  <!-- src: ledger ROUTE-SOURCE-NULL: chips "VALID (POST-RUN b5ed5e96): RS1 UNDETERMINED (D_S +0.51pp [-0.67, +1.68];
  G_AF ABOVE RWS p97.5)", "RWS 183 BLOCKS, NOT THE REGISTERED 123 ... [SC], NEVER LABEL-FREE"; [OUTCOME 2026-10-04]
  (MDE80 1.68pp); ROUTE-SOURCE-NULL.json does_not_show "that source explains the gain (G_AF above the RWS band)" -->
- `ROUTER-REGRET-MMLU` (a registered descriptive baseline).
  On MMLU-Pro alone, one model (gemini-3.1-pro) is best in all 14 anchors (the MMLU-Pro categories) on both rosters, 12 and 46 models.
  The routing gain is 0.000 at anchor level and -0.002 at leaf level (bootstrap SE 0.007; 3,130 reserved keyed questions).
  Pool p2dca21ab5f4ef3ae, id-disjoint only; leaves filed by a qwen3 tree (bareq512_s42).
  <!-- src: ledger ROUTER-REGRET-MMLU (chip NOTHING TO ROUTE; "gemini is best in all 14 anchors on both rosters;
  routing gain 0.000 (anchor) and -0.002 (leaf)"); ROUTER-REGRET-MMLU.json run.pool p2dca21ab5f4ef3ae (reserved
  3,130), criteria value (+0.000 +- 0.007 / -0.002 +- 0.007); key-only on p2dca: "id-disjoint only" and "filed by a
  qwen3 tree" per RULING_w0_p2dca_family.md (prog L21480) -->

**SQ2 TRUST**

- The judged half of SQ2 is OPEN.
  The first-iteration judged numbers (the p2dca judged family) are history, never evidence, and content-closed replacements were registered or drafted.
  Which judged instrument SQ2's content-closed claims are stated under is still the author's decision.
  <!-- src: prog L21500 ("the judged half of SQ2 is OPEN"), L21486 ("Content-closed replacements are registered or
  drafted"), L21453 item (6), L25108 ("SQ2's instrument (the author's, open"), _as_of 70c61579 -->
- `V2-DECLARED-CELLS`, criterion C3 (key half; content-closed v2 split, MMLU-Pro EVAL).
  Over MMLU-Pro's 13 declared categories, the key profile's interaction-only reliability R is 0.8761 [0.8036, 0.9486] for 12 models (null p95 0.5070; 3,244 items).
  For 37 models it is 0.8184 [0.7130, 0.9238] (null p95 0.3502; 3,243 items).
  <!-- src: ledger V2-DECLARED-CELLS chip "C0 C1 C2 C3 (K12, K37) HELD"; V2-DECLARED-CELLS.json numbers_of_record
  C3_K12, C3_K37; brackets 2026-09-29 (leg M key-complete of 3,492 = pv2_41dbd3dbcd399df0) -->

**SQ3 TAXONOMY**

- `RECORD-RECIPE-EDGE-AUDIT` (part 1, a recorded fact).
  The tree of record bareq512_s42 (snapshot 20260909_212117, 87 leaves, R512) is not a certified fixed point.
  Its certificate reads CERTIFIED false at iteration 18, a GED-quiescence stop.
  Its split is id-disjoint only.
  <!-- src: ledger RECORD-RECIPE-EDGE-AUDIT chip "RECORDED: bareq512_s42 CERTIFIED FALSE AT ITERATION 18
  (GED-QUIESCENCE STOP); NOT A FIXED POINT"; prog L20817-L20844 (F1, F6), _as_of 70c61579; KNOWLEDGE.md section 1
  (Trees: 87 leaves, R512, id-disjoint only) -->
- `CERT-RESOLUTION`.
  Only Chemistry n00000006 and Engineering n00000015 may be called "certified at per-family FDR q = 0.05 (hierarchical BH over nested sites, 300 reps, bareq512_s42, R512)".
  The other 8 of its 10 site-certified splits pass "their own site-null p95 (per-site, uncorrected)" only.
  The control is per family, not tree-wide: BY rejects nothing, and 53 of the 70 sites were never tested because their ancestors were not rejected (untested, not unreal).
  What is certified is the split at the site, not the anchor category.
  R512 counts are never set against R256 counts.
  <!-- src: KNOWLEDGE.md section 1 (Trees; the required wording); ledger CERT-RESOLUTION chips "C1 HELD: R512
  HIERARCHICAL BH = 2 (CHEMISTRY, ENGINEERING; k = 0; NOT MC-MARGINAL)" and "PER-FAMILY FDR ONLY: BY 0 ON EVERY
  TREE; 53/70 UNTESTED, NOT UNREAL; 300 REPS; OTHER 8 R512 SITES E3 WORDS ONLY"; CERT-RESOLUTION.json
  sentence_of_record ("what is certified is the split at the site, not the anchor category"; "never set against
  the R256 trees' counts") -->
- `FLAT-MIX-MMLU`.
  On MMLU-Pro, the anchor-free tree af_clean_s42 (82 leaves) is a measurably worse partition than a flat vMF mixture at k = 82.
  Tree minus mixture, leaf purity is -4.3pp [-5.6, -2.9] and key information is -1.5e-3 (interval [-2.2, -0.8] in units of 1e-3), both beyond the seed spread.
  Purity is read on the 3,445 judgeable questions of p2dca21ab5f4ef3ae, content-closed at norm-v1 only (37 of 3,445 have a near-copy at cos >= 0.98); key information is read on the 10,925 keyed questions of both sides.
  The mechanism is not identified; one tree, one comparator, one corpus.
  <!-- src: ledger FLAT-MIX-MMLU chips "VALID (POST-RUN 643995a) ... C1 FAILED, C2 FAILED ... F1 FIRES (A
  LIMITATION): PURITY -4.3 PP [-5.6, -2.9], F6 -1.5e-3 [-2.2, -0.8] VS FLAT vMF V0 AT k = 82", "HELD-OUT =
  CONTENT-CLOSED AT NORM-V1 ONLY: 37/3,445 FIT NEAR-COPIES AT COS >= 0.98", "T-4 MECHANISM NOT IDENTIFIED ... ONE
  TREE / ONE COMPARATOR / ONE CORPUS"; prog L21121, _as_of 70c61579; FLAT-MIX-MMLU.json sentence_of_record
  ("beyond the seed spread"; "key information = F6 key-only LOO Brier on the 10,925 keyed questions of both sides") -->

**SQ4 PRICE**

- `CELL-STRATA-EVAL` (content-closed v2 union split; 5,907 items / 5,404 components).
  Sampling 100 items by tree cell estimates a left-out model's accuracy with less error than simple random sampling: MAE ratio 0.9447 [0.9206, 0.9676] (18 models x 500 draws).
  It is not separated from sampling by source (UNDETERMINED, below the MDE) and not better than per-source k-means strata.
  The record therefore writes no "the tree cuts evaluation cost" sentence.
  <!-- src: ledger CELL-STRATA-EVAL chips "VALID (POST-RUN a6daf4a9): CS1 BEATS-RAND (MAE RATIO 0.9447 [0.9206,
  0.9676])" and "CS2 UNDETERMINED VS SRC (BELOW THE MDE), AF-NOT-BETTER VS K_0; R-CS-K: NO SQ4 'THE TREE CUTS
  EVALUATION COST' SENTENCE"; CELL-STRATA-EVAL.json criteria CS1 denominator (18 models x 500 draws at n 100) -->
- The size of a judged board is not decided; that choice is the author's.
  <!-- src: ledger ARCH-V2-PILOT-K46 chip "BOARD SIZE NOT DECIDED (THE AUTHOR'S)" -->

**SQ5 INVARIANCE**

- `SUPERGPQA-STAGE0b` (key only).
  On a second corpus, SuperGPQA minus its 1,251 MMLU-Pro collisions (4.7156% of 26,529 items), the discipline interaction profile is above its null.
  R is 0.6413 [0.4382, 0.8444] against a null p95 of 0.0995 (10 disciplines, 49 models).
  The per-discipline policy's gain over the best single model, +0.65pp [+0.04, +1.25] (n 7,396), is descriptive only: the percentile interval [-0.05, +1.16] contains 0.
  Nothing is claimed for SuperGPQA as a whole.
  <!-- src: ledger SUPERGPQA-STAGE0b chips "C2 HELD: R 0.6413 [0.4382, 0.8444] > NULL p95 0.0995", "VALID (POST-RUN
  3da93fc); C1 HELD BY THE NORMAL TWO-STAGE INTERVAL, LOWER END +0.04PP; PERCENTILE [-0.05, +1.16] CONTAINS 0;
  VERDICT LINE DESCRIPTIVE-ONLY", "POPULATION = SUPERGPQA MINUS 1,251 MMLU-PRO COLLISIONS (4.7156%); NOT A GAIN OF
  SUPERGPQA AS A WHOLE"; SUPERGPQA-STAGE0b.json numbers_of_record C2_R (10 disciplines x 49 models), population
  (26,529), sentence_of_record (+0.65pp [+0.04, +1.25], n 7,396) -->

**Scoring**

- `HARNESS-EXTRACTOR`.
  On MATH (1,309 of 1,324 questions, 18 models), three scorers (the stored scorer, MATH-FIX and an audit hybrid) reorder the models.
  The minimum pairwise Kendall tau-b is -0.0473 and the maximum rank shift is 15 (RANKS-MOVE).
  This confirms a disclosed pilot; it is not a blind test.
  Pool paeec37aa28063c75, id-disjoint only; the result is relative to these 18 models.
  <!-- src: ledger HARNESS-EXTRACTOR chip "VALID (POST-RUN e313f1d8): HX1 RANKS-MOVE (MIN TAU-B -0.0473, SHIFT 15);
  ... CONFIRMS A DISCLOSED PILOT"; HARNESS-EXTRACTOR.json sentence_of_record bracket ("confirms a disclosed pilot,
  not a blind test"; "pool paeec37aa28063c75 id-disjoint only; relative to these 18 models"); prog L25461,
  _as_of 70c61579 -->

**Closed lines (negative results)**

These lines are closed and stay closed without a new registration: rubric text at every granularity; rubric-shaped references; reference ensembles, gating, confidence and two-reference variants; sub-anchor profiles; the order inside the frontier band; escalation to a reasoning judge on the residue; the proposal memo; single and selective order; temperature 0.
On LiveCodeBench, falsifier F1 of the stage-0 interaction test fired (STOP) at its 26-model roster and tree recipe, so the judged stage is not registered there; power is unverified, and this closes nothing elsewhere.
The Gaussian-mixture likelihood-ratio / BIC test of the site certificate is closed negative: it cannot discriminate, which is not evidence that the certified splits lack modes; the dip half stays open.
The judge-side lines were closed on the first-iteration sample.
This is stated as design provenance, not as a finding, and the family ruling is not a reason to reopen them.
<!-- src: docs/agents/CONTEXT.md section 5 (list; [ADDED 2026-09-25 by LCB-STAGE0-INTERACTION] "F1 FIRED (STOP) at
this 26-model roster and tree recipe; the judged stage is not registered on LCB. It does NOT close the question
elsewhere ... Power is unverified" (REVIEW_REPO-TIDY E7); [ADDED 2026-09-26 by MIX-LRT-SITE] qualifier;
[P-FAM pointer 2026-09-27] "they STAY CLOSED; P-FAM is not a reopening reason"); docs/reviews/RULING_w0_p2dca_family.md
USE (2) design provenance (prog L21489), section 3.2 -->

## History

A first iteration (the r8 batch and the judged runs of its era: x8, x12 v1, the R2 atlas) was judged on pool p2dca21ab5f4ef3ae while the frozen tree withheld p8a29d8f3ff75aa55. Of that pool's 3,445 judgeable questions, 2,437 (70.7%) lay on the frozen tree's train side, and its cell rubrics were induced over them. Its split was id-only; its judge and rubric recipe have since been replaced; on re-score its rubric-value claims were withdrawn, and its 22 per-leaf position fits were contaminated by a since-removed correction, while its eight pooled leaderboards reproduce. No result of that iteration is used in this thesis.
<!-- src: D-2026-10-27-6 A1 (docs/agents/author_decisions/2026-10-27.md): the paragraph of
docs/agents/plans/2026-09-27_research_plan_rev2.md L270 (section "## A4. How r8 and the p2dca judged family are
disclosed"), verbatim, with its [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C1)] fix applied ("its anchor
rubrics" -> "its cell rubrics"); nothing else reworded. The rule it discloses: prog L21449 "(2) r8 AND THE p2dca
JUDGED FAMILY ARE HISTORY (one disclosure), NEVER EVIDENCE", _as_of 70c61579. -->

## Layout

| path | contents |
|---|---|
| `src/` | Kotlin sources of the engine (construction, routing, arena) and their tests |
| `tools/` | Python analysis tools, guards, ingest and run chains; see [tools/README.md](tools/README.md) |
| `experiment_configs/` | run configs (TOML) and pool pins; see [experiment_configs/README.md](experiment_configs/README.md) |
| `experiment_results/` | committed outputs and readouts; see [experiment_results/README.md](experiment_results/README.md) |
| `docs/` | the record, the design and older documents; index in [docs/README.md](docs/README.md) |
| `report/` | the thesis sources (LaTeX), the author's. Its "certified fixed point" sentences hold for the frozen artefact 20260727_042523 only, not for the tree of record bareq512_s42 (docs/judge_v2_program.md L20860, item (e)). Rewriting it is the author's alone (docs/judge_v2_program.md L21453) |
| `data_v2/manifests/` | manifests of the registered v2 split draws (ARCHV2-SPLIT-1, ARCHV2-SPLIT-2) and a development draw |
| `archive/` | files moved out of the active workspace; [archive/ARCHIVE_MANIFEST.md](archive/ARCHIVE_MANIFEST.md) gives each entry's reason |
| `tuning/`, `tune.bat` | the L9 screening record of the construction parameters (harness in `tools/tuning/`) |
| `snapshots_frozen.db` (not in the public copy) | extract of the frozen tree 20260727_042523 (154 nodes, 87 leaves) and two granularity snapshots; geometry only, never modified |
| `frozen_triples_20260727_042523_Headless_Run_Auto_ge_MAIN.json` | engine input; restore it from HEAD after any MAIN construction |
| `reserved_leaf_assignments.csv`, `model_domain_scores.csv`, `*_secured/` | inputs that older analyses and figure checks read by path |
| `scripts/`, `figures/` | older analysis scripts and an exploratory figure, kept because records cite them |
| `.claude/agents/` | role definitions of the agents that maintain the record |
| `.github/workflows/ci.yml` | compile-only CI |
| `config/application.yml` | Spring configuration, author-owned |

<!-- report/ row: A6 default (D-2026-10-27-6), the plan's neutral line made visible (REVIEW_REPO-TIDY E4); prog
L20860 (e) (the "certified fixed point" sentences: true of the frozen artefact 20260727_042523, NOT of the tree of
record bareq512_s42) and L21453 ("any rewrite of report/ ... is the author's alone"), _as_of 70c61579. -->
<!-- src: data_v2/manifests file names; archive/ARCHIVE_MANIFEST.md L376 (tune.bat + tools/tuning/ + tuning/ "the
L9 screening record"), L373 (*_secured/ read by report/Figures/make_frozen_tree.py), L378
(reserved_leaf_assignments.csv, model_domain_scores.csv); KNOWLEDGE.md section 1 (frozen 20260727_042523: 154
nodes / 87 leaves, snapshots_frozen.db, never modified, geometry-only); docs/README.md L39-L42 _as_of 70c61579
(extract plus two granularity-analysis snapshots); CONTEXT.md section 4 rule 6 (restore frozen_triples_*_MAIN.json from HEAD after
any MAIN construction; never modify snapshots_frozen.db; application.yml never committed by agents);
.github/workflows/ci.yml L1-L2 -->

## Build and check

- Toolchain: JDK 21, Gradle 8.10 through the wrapper (`./gradlew`), Kotlin 2.1.10, Spring Boot 3.4.3.
- `./gradlew compileKotlin compileTestKotlin` compiles the main and test sources. That is all CI runs.
- `./gradlew test` runs the default suite. Two tests need a local cache or a local configuration value that are not in the repository (`MrlRoutingTest.testMrlConfigDefaults` and the blank-trace check of `TraceEnvelopeUnwrapTest`); on a checkout without them they are skipped, not failed, and the rest of the suite passes. In a copy without git metadata (such as GitHub's "Download ZIP") the refusal check of `RatingsDbGuardTest`, which needs git to tell tracked from untracked files, is skipped as well.
- A headless run: `./gradlew bootRun --args="--config experiment_configs/<run>.toml"`. Runs that call a judge or labeller need credentials in a `.env` file (copy [.env.example](.env.example); `.env` is never committed).
- Before any reader opens a pool: `python tools/analysis/pool_guard.py --pool <id>`.
- The ledger is edited only through `tools/analysis/ledger_patch.py`; `tools/analysis/results_index.py` regenerates `docs/agents/results/INDEX.md`.

<!-- src: build.gradle.kts L5 (Kotlin 2.1.10), L9 (Spring Boot 3.4.3), L18 (JavaLanguageVersion.of(21));
gradle/wrapper/gradle-wrapper.properties L3 (gradle-8.10); .github/workflows/ci.yml L1-L2, L38;
docs/reviews/REVIEW_REPO-TIDY.md claim 3 (before the A7 guards: 2 tests failed, both environmental) and E10; the A7
commit on branch repo-tidy (D-2026-10-27-6 A7: both tests guarded by JUnit assumptions; full clean checkout of the
branch: 0 failed, these 2 skipped; the runs are in that commit's message); README.md L53 _as_of 70c61579 (bootRun --config); .env.example L1-L2; KNOWLEDGE.md section 1 (pool_guard), section 1
ledger conventions (ledger_patch.py only), section 4 table (INDEX.md via results_index.py) -->

## Caches and local state

The data caches are not in the repository: the dataset cache `mmlu_pro_dataset_cache_v2.db`, the embedding cache `embeddings_cache.db` (qwen3-embedding) and the local snapshot database.
A construction writes to both caches by design: table `queries` in the embedding cache and table `reserved_pool_meta` in the dataset cache.
Back both up before any construction.

The public GitHub copy is a snapshot of this repository without its development history (commit hashes cited in the record refer to that history; only its early part, up to the `v1.0.x-thesis` release tags of August 2026, is on GitHub); bulky and binary outputs (databases, arrays), the data caches, raw model and judge outputs, third-party benchmark text, files containing GPQA text and unpublished drafts are not included.
Files of those kinds that this README or the record names, such as `snapshots_frozen.db`, are therefore not in that copy.
<!-- src: docs/reviews/2026-09-20_cache_writes_by_construction.md L7 ("A construction WRITES to both files by design,
on every run"; (a) queries, (b) reserved_pool_meta); KNOWLEDGE.md section 1 (Embedders: qwen3-embedding of record,
embeddings_cache.db) and section 2 rule 7 ("Back up before any construction"); docs/README.md L41-L42 _as_of
70c61579 (local snapshots.db not in git). Public copy: D-2026-10-27-4 (1) (one snapshot commit excluding GPQA-bearing
files, raw model/judge outputs, binary outputs, third-party benchmark text dumps and unpublished drafts) and
D-2026-10-27-6 A2 (docs/agents/author_decisions/2026-10-27.md); the snapshot without the history, local main and its full history unchanged (so cited commit hashes resolve only in that history): D-2026-10-27-4 (1); published as the main session's snapshot commit with this prepared version as a child commit of it, no second force-push: D-2026-10-27-7. The clean-clone replication sentence was deleted
(REVIEW_REPO-TIDY E3; plan 3a(6)). -->

## Where the record lives

- [docs/judge_v2_program.md](docs/judge_v2_program.md): the programme. Every registration, outcome, ruling and author decision, appended in order.
- [docs/test_ledger.html](docs/test_ledger.html): the ledger, one row per test. [docs/test_ledger_distilled.html](docs/test_ledger_distilled.html) is a curated view at ledger v110 (2026-09-17).
- [docs/agents/results/INDEX.md](docs/agents/results/INDEX.md): one record per experiment.
- [docs/agents/queue.md](docs/agents/queue.md): a readable view of `queue.json`, the queue of record.
- [docs/agents/author_decisions/](docs/agents/author_decisions/): the author's decisions, by date.
- [docs/plan_2026-09-15.md](docs/plan_2026-09-15.md): the plan and its numbered amendments.
- [docs/reviews/](docs/reviews/): READY reviews before a run, POSTRUN reviews after it, and rulings, among them [the p2dca family ruling](docs/reviews/RULING_w0_p2dca_family.md).
- [docs/design/FRAMEWORK.md](docs/design/FRAMEWORK.md): the design of record; read its dated brackets.
- [docs/agents/KNOWLEDGE.md](docs/agents/KNOWLEDGE.md): a digest of pins and rules with pointers into the record.

Every test is registered in the programme before any code or call.
Corrections are made by insertion only, as dated brackets, and the last bracket wins.
A wrong count is written wrong(established); judge accuracies are given under both tie conventions.
<!-- src: KNOWLEDGE.md section 4 (where things live), section 1 (ledger and record conventions: insertion only, last
bracket wins, wrong(established), conventions A and B); CONTEXT.md section 4 rules 2-3; distilled L60-L61 (v110,
record at 2026-09-17) -->

## Licence

The repository is released under the MIT licence; see [LICENSE](LICENSE).
The exception is the thesis text in `report/`, which is all rights reserved.
<!-- src: D-2026-10-27-6 A5 (docs/agents/author_decisions/2026-10-27.md): "MIT licence for the repository; the README
notes that the thesis text in report/ is all rights reserved"; copyright holder = the git user name (0ctave). -->
