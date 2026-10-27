# Multi-corpus TaxoArena — design for training the taxonomy and the arena on a union of datasets

Status: DESIGN (2026-09-11). Nothing here is implemented. Motivation: ROUTER-REGRET-MMLU (gemini is the best
model in all 14 MMLU-Pro anchors; routing gains 0.000) — a router only has something to route when the argmax
changes across task families. Naming: the code already uses "fusion" for node merging (`E2FusionRunner`,
`TaxonomyMerger.fuseNodes`, `fusionSimilarityThreshold`); this document says **multi-corpus** throughout.

## 0. Constraints that the design must respect

1. **The MMLU-Pro path stays byte-identical.** Every existing TOML, snapshot, pool id (p2dca21ab5f4ef3ae), ratings
   DB and frozen triples file must keep working unchanged; the replay gate (`tools/analysis/replay_diff.py`) is the
   acceptance test of every stage.
2. **Existing databases are immutable inputs.** `mmlu_pro_dataset_cache_v2.db`, `snapshots_frozen.db`, the
   ratings DBs are never migrated in place. Multi-corpus runs use a new dataset DB whose path is a config key.
3. **Generation/arena separation per corpus.** Every corpus gets its own stratified reserved split; the pool id
   stays a content hash; construction, labeling, rubric induction and data cards see train-side rows only.
4. **Zero judge calls until stage 3.** Structural and key-only stages must answer "is there anything to route"
   before any budget is spent.
5. **One config, one command.** A user adds a corpus by listing it; nothing else changes for them.

## 1. Where the current code couples to "one dataset" (from the code map, 2026-09-11)

| Layer | Coupling | File:line |
|---|---|---|
| Dataset | `DatasetType` enum dispatched by two `when` blocks; one table per type, one type per run | `MMLUDatasetFetcher.kt:168-200` |
| Dataset | `MMLUQuery(id, text, category)` has no source; construction receives only `category → List<text>`; identity is the raw string (`QuestionIdRegistry`, `embeddings.query`) | `MMLUDatasetFetcher.kt:1046`, `HeadlessBenchmarkRunner.kt:349`, `TaxonomyEngine.kt:41` |
| Eval | `eval_results PRIMARY KEY (question_id, model_name)` + `INSERT OR IGNORE`: cross-corpus id collisions are silently dropped | `ModelEvalStore.kt:133-195` |
| Eval | literal `mmlu_pro` in SQL, including the rubric-induction leak filter | `ModelEvalLoader.kt:336`, `ModelEvalStore.kt:593-597`, `EvalIngestValidator.kt:637` |
| Eval | `is_correct = (pred == answer)` letter equality, asserted as an invariant | `ModelEvalLoader.kt:262`, `EvalIngestValidator.kt:136-143` |
| Eval | `options_json NOT NULL`, `gt_answer NOT NULL`: MCQ-shaped rows | `ModelEvalStore.kt:133-154` |
| Judge | letter parsing and the three `judgeOptionMode`s assume a lettered candidate set; the prompt text itself is format-neutral | `TaxonomyArenaService.kt:317-348, 666-671`, `TaxonomyConfig.kt:64-100` |
| Induction | corpus items rendered as lettered options; leakage audit built from option letters | `TaxonomyJudgeService.kt:213-226, 259-270` |
| Anchoring | depth-1 anchors = the dataset's category strings; `excludeFromAnchoring` guards assume a flat set | `TaxonomyEngine.kt:174-243` |
| Pool | pool id = hash of `domain:id` lines, no corpus qualifier | `MMLUDatasetFetcher.kt:695-706` |
| Arena | roster from `models = [...]`; `minModelCount = 2` and the ingest validator's quorum exclude models that ran only part of a union | `TaxonomyBenchmarkService.kt:140-191` |
| Config | hand-written TOML parser: one key = three edits, unknown key fatal | `HeadlessBenchmarkRunner.kt:1440-1709` |
| Python | `rejudge_grok.EVAL_DB` literal; ~14 sites parse `[A-J]`; the options-key join | `rejudge_grok.py:51-58`, `free_tests_f4_f7.py:102-128` |
| Already corpus-blind | embeddings cache (text-keyed), `match_history.eval_question_id TEXT`, `reserved_pools_meta.dataset TEXT`, judge templates, BT scheduler/fitter | — |

## 2. Design principles

- **A corpus is a plugin.** One interface, one registry, one TOML list. The MMLU-Pro plugin wraps the existing
  fetcher without touching its behaviour.
- **Identity is qualified at every boundary an id crosses.** Inside the JVM: `CorpusQuery(source, upstreamId,
  text, domain, task)`. In SQLite: an integer namespace per corpus, so the schema and every existing row stay
  byte-identical (MMLU-Pro keeps offset 0).
- **Truth is a verifier, not a letter.** `is_correct` stays a column; how it is computed becomes a per-corpus
  `Verifier` (MC letter, exact match, imported metric). Everything that today assumes letters asks the verifier
  instead.
- **The taxonomy is corpus-aware only at the anchor layer.** Depth-1 anchors become `(source)` and depth-2 the
  corpus's own domains; below that the geometry is unchanged. Certification is reported per source so that
  designed boundaries never inflate the count.
- **Analysis tools read one manifest.** A `corpus.py` helper resolves DB path, corpus filter and verifier so
  that the twenty modules importing `rejudge_grok` inherit multi-corpus support without edits.

## 3. Layer designs (smallest change that keeps MMLU-Pro byte-identical)

### 3.1 Corpus plugin
```kotlin
interface CorpusSource {
    val name: String                 // "MMLU_PRO", "BBH", "MATH", "IFEVAL", "MUSR"
    val tableName: String
    val verifier: Verifier
    fun fetch(maxQueries: Int, domains: Set<String>?): Map<String, List<CorpusQuery>>   // domain -> queries
    fun detailsFor(texts: Collection<String>): Map<String, CorpusItem>                 // for induction/cards
}
data class CorpusQuery(val source: String, val upstreamId: Int, val text: String, val domain: String,
                       val task: String = domain)
```
- `MMLUDatasetFetcher` becomes the `MMLU_PRO` plugin (a thin adapter around the existing methods). The two
  `when` blocks (`:168`, `:185`) turn into registry lookups; the enum stays as the registry's key set for the
  existing five types.
- `MMLUQuery` gets a fourth field `source: String = "MMLU_PRO"` (default keeps every serialised payload and
  `reserved_test_queries.json` identical).
- `HeadlessBenchmarkRunner.kt:349` passes `Map<(source, domain), List<text>>` to the engine; the engine
  builds the two-level anchor layer (§3.5) when more than one source is present and the old flat layer
  otherwise.
- Root label: `corpora.joinToString("+")` when > 1, else `datasetType.name` (unchanged).

### 3.2 Identity and the eval store
- New table `corpus_registry(source TEXT PRIMARY KEY, table_name TEXT, id_offset INTEGER, verifier TEXT)`.
  MMLU_PRO = offset 0; other corpora get disjoint 1,000,000-wide namespaces. `eval_results.question_id` holds
  `offset + upstreamId`; the primary key, the `INSERT OR IGNORE`, the ratings `eval_question_id` and every
  existing row are untouched. (Rejected alternative: a `dataset` column in the PK — SQLite cannot alter a PK
  in place, so it forces a migration of the immutable DB.)
- `EvalIngestValidator` gets a per-corpus id-collision probe (the check it already does for one model) and
  the quorum/orphan checks run **within** a corpus.
- The three literal `mmlu_pro` joins go through `corpusRegistry.tableFor(source)`. The rubric-induction leak
  filter (`getReservedQuestionTexts`) unions over all registered tables; the `check(removed == heldOutInRegion)`
  canary in `TaxonomyJudgeService` stays and now protects every corpus.
- `eval_question_link.mmlu_pro_row_id` is generalised to `(source, row_id)` in a **new** link table
  `corpus_question_link`; the old table is read for MMLU_PRO and never written again.
- Columns `options_json` / `gt_answer` become nullable **in the new DB only** (multi-corpus runs never open
  the v2 DB for writing). A `verifier` column (`TEXT DEFAULT 'MC_LETTER'`) is added there.

### 3.3 Verifier
```kotlin
sealed interface Verifier {
    fun isCorrect(pred: String?, target: String, options: List<String>?): Boolean?
    fun renderItem(text: String, options: List<String>?, target: String): String      // induction / cards
    fun answerNGrams(target: String, options: List<String>?): Set<String>              // leakage audit
    fun candidateSet(options: List<String>?): List<String>?                           // null = no OPTIONS/RESOLVED
}
object McLetter : Verifier          // today's behaviour, byte-identical
object ExactMatch : Verifier        // MATH: normalised numeric/LaTeX equality
class Imported(val metric: String) : Verifier   // leaderboard-v2 acc_norm / prompt_level_strict_acc
```
- `ModelEvalLoader.kt:262` calls `verifier.isCorrect`; the ingest validator asserts the verifier's invariant
  instead of letter equality.
- `judgeOptionMode`: `OPTIONS`/`RESOLVED` apply only where `candidateSet != null`; elsewhere the run logs
  `[ARENA-OPTMODE] not applicable (verifier=…)` per cell so the rate is never misread as a setting effect.
- Induction rendering (`TaxonomyJudgeService.kt:213-226`) and the leakage audit (`:259-270`) call the verifier;
  `JudgePrompts.kt` phrases "multiple-choice" become "$taskFamily problems" filled per source.
- STACK-v2 with a verifier: for verifiable corpora the **reference is the verifier's target** (exact, no
  reasoning call, no ceiling); for MC corpora it stays the reasoning reference. This is the "checker instead of
  solver" answer to the reference-ceiling finding, and it makes stage 3 cheaper (two cheap calls per match).

### 3.4 Loader for Open LLM Leaderboard v2 details
- Layout (checked 2026-09-11 on `Qwen__Qwen2.5-7B-Instruct-details`): `open-llm-leaderboard/<org>__<model>-details`,
  files `<org>__<model>/samples_leaderboard_<task>_<timestamp>.jsonl` (78 JSONL files = one per task per run;
  BBH has one file per sub-task, MATH one per subject; `results_<timestamp>.json` carries the aggregate metrics);
  rows `doc_id, doc, resps, filtered_resps, target, <metric>`. Several runs per model can coexist: take the latest
  timestamp. Some repos are gated (401 without the HF token that `.env` already holds). JSONL, so no parquet
  dependency; `huggingface_hub` is installed, `datasets`/`pyarrow` are not needed.
- Ingest in **Python** (`tools/ingest/leaderboard_details.py`): for each corpus and model, write `eval_results` rows into the new DB with the
  namespaced id, `model_output = filtered_resps[0]`, `pred` per verifier, `is_correct` = imported metric,
  `verifier` set. A `--dry-run` prints the coverage matrix (models × corpora) before writing.
- Roster rule: a model enters a multi-corpus run only if it covers every listed corpus (or the run sets
  `allowPartialCoverage = true`, in which case per-corpus boards are reported separately and the union board
  is not).

### 3.5 Anchoring, certification, split
- Bootstrap: depth-1 = source, depth-2 = the corpus's domains (MMLU-Pro categories, BBH task names, MATH
  subjects); single-corpus runs keep today's flat layer. Site-level nulls run as before; the readout adds
  `certified_within_source` so the designed source boundaries are never counted as discovered structure.
- `excludeFromAnchoring` keys become `source/domain`; a bare domain still matches the single-corpus case.
- Split: `splitTrainTest` stratifies by `(source, domain)`; the pool id canonical line stays `domain:id` for
  MMLU_PRO rows (so p2dca is reproduced) and becomes `source|domain:id` for other sources. One pool per run.
- `MMLUCategories.SUBJECT_TO_DOMAIN` applies only to MMLU-original rows; other corpora pass their domain
  through unchanged.

### 3.6 Arena and scheduler
- Unchanged: `BtMatchScheduler`, `BtStoppingPolicy`, BT fitter, dual-order judge, TIE rule, confidence gate.
- `getResultsMatrix(...)` filters by the run's corpus set and applies `minModelCount` per corpus.
- `maxQueryReuse` stays global; a new `sourceBudgetShare = proportional | equal` decides how the match budget
  is divided across sources (default proportional to reserved questions, which is today's behaviour for one
  source).
- `match_history.eval_question_id` already TEXT: holds the namespaced integer as text; `domain` unchanged.

### 3.7 Config and ease of use
- New keys: `corpora = ["MMLU_PRO", "BBH"]` (list; `datasetType = "X"` remains valid sugar for `corpora = ["X"]`),
  `corpusDbPath` (default `mmlu_pro_dataset_cache_v2.db` for single-corpus MMLU_PRO runs, mandatory otherwise),
  `allowPartialCoverage`, `sourceBudgetShare`, per-corpus `[corpus.BBH] tasks = [...]` blocks.
- Replace the hand-written parser with a TOML library (`tomlkt`) behind the same `HeadlessCliConfig`; the
  unknown-key-is-fatal behaviour is kept (it caught the `tau` bug). This is the single largest ease-of-use win:
  today every key costs three edits.
- `--dry-run` prints: corpora, tables, verifiers, coverage matrix, per-corpus train/reserved counts, pool id.

### 3.8 Python analysis tools
- `tools/analysis/corpus.py`: `EVAL_DB` (env `TAXO_EVAL_DB`), `CORPUS` filter (env `TAXO_CORPUS`, default
  MMLU_PRO), `verifier_for(source)`, `namespaced(source, id)`. `rejudge_grok.py:54` imports its `EVAL_DB` from
  there; the twenty consumers inherit it.
- The options-key join (`free_tests_f4_f7.keyed_questions`) is used only for MMLU_PRO; other corpora join on
  the namespaced id directly (their ingest wrote the link).
- Letter sites (`"ABCDEFGHIJ".find`, `[A-J]` regexes) get `if verifier is McLetter` guards; no rewrite.
- `rubric_kit2.datacard()` (the adopted data-only leaf card) generalises through `verifier.renderItem` and
  `answerNGrams`; its signals (answer form, error signature) are more informative across corpora than within.

## 4. Staging and budget

| Stage | Content | Judge calls | Gate |
|---|---|---|---|
| 0 | registry, namespaced ids, verifier interface, new DB path, TOML library; MMLU-Pro plugin | 0 | `replay_diff.py`: promoted bareq512_s42 replays byte-identical; pool p2dca reproduced; unit suite green |
| 1 | ingest BBH (+ MATH-hard, MuSR, IFEval as available) from leaderboard details; multi-corpus label-free build; site-null; per-source certification | 0 (embeddings on the local Ollama model) | coverage matrix ≥ 12 models × all corpora; anchors = sources at depth 1; within-source certified sites reported |
| 2 | key-only router regret across corpora (routed-by-leaf / by-anchor vs best single vs oracle on the reserved side); model×leaf interaction LRT with question-level permutation | 0 | registered: router gain > 0 at anchor level with query-level bootstrap SE; if ≤ 0, stop — nothing to route |
| 3 | arena: STACK-v2 with verifier references where they exist, reasoning reference elsewhere, data-only leaf card; per-source boards + union board | budgeted; ≈ 2 cheap calls per match, no reasoning call for verifiable corpora | registered per the judge_v2_program conventions |

Effort estimate: stage 0 ≈ 3–4 days (the parser replacement is half of it); stage 1 ≈ 2 days; stage 2 ≈ 1 day
(reuses `router_regret.py` and `leaf_profile_evidence.py`); stage 3 depends on budget.

## 5. Regression gates that must hold at every stage
1. `replay_diff.py` on the promoted config: DAG identical; proposals identical under the P7 caveat.
2. `pool_guard.py`: p2dca21ab5f4ef3ae active and reproducible from the frozen snapshot.
3. `EvalIngestValidator` on the MMLU-Pro DB: unchanged verdicts.
4. Unit suite (262 tests) green; `PairStatsInvariantTest`, `PcaProjectEquivalenceTest` included.
5. The rubric-induction leak canary (`TaxonomyJudgeService` `check`) fires on a deliberately contaminated fixture.

## 6. What this buys the thesis / paper
- A router metric that MMLU-Pro cannot provide (regret vs best single model) and a per-source certification
  readout that tests whether the plateau at ≈ 13–14 sites is a property of exam data.
- A verifier-referenced judge for math/code families that removes the reference ceiling found on the frontier
  cluster (ARENA-V2 / X20).
- All of it as a follow-up chapter; the settled MMLU-Pro campaign and its artefacts are untouched by design.

## Stage 1 progress (2026-09-11)
- Coverage survey (`tools/ingest/leaderboard_details.py --dry-run`, listings only, zero LLM calls): of the current
  MMLU-Pro roster only 5 open models have leaderboard details (Llama-3.1-70B-Instruct, Mixtral-8x7B-Instruct,
  Phi-3-mini, Qwen2.5-7B/72B-Instruct); the closed frontier models have none. Discovery over official orgs found
  85 models with full coverage of all six corpora (BBH 24 sub-tasks, MATH 7 subjects, MuSR 3, IFEval, GPQA 3,
  and the leaderboard's own MMLU-Pro samples), experiment_results/multicorpus/discovery.txt.
- Consequence: the multi-corpus roster is drawn entirely from the leaderboard (consistent prompts, metrics and
  traces across corpora) and is disjoint from the MMLU-Pro campaign roster except for the 5 overlaps. That is
  the right design anyway: the router question needs specialists (Qwen2.5-Math, Qwen2.5-Coder, R1 distills)
  whose argmax changes by family. ROSTER18 in the ingest tool: 3 Llama, 5 Qwen (incl. Math and Coder), 2 R1
  distills, 2 Mistral, Phi-3.5, Yi-1.5, Command-R+, Falcon3, OLMo-2, InternLM2.5.
- Files are downloaded to experiment_results/multicorpus/raw/<model>/ (JSONL, untracked); the ingest into the
  new corpus DB follows once the record structure per task is inspected.

## 7. Stage 0a implemented (2026-09-11)

Plumbing only, MMLU-Pro path byte-identical (gate: `replay_diff.py` on `perf_replay/bareq512_s137_stage0a`
vs `dimsweep2/bareq512_s137`; unit suite 269 green). What exists now, in `src/main/kotlin/taxonomy/dataset/`:

- `Verifier.kt`: the sealed `Verifier` interface (`isCorrect`, `renderItem`, `answerNGrams`, `distractors`,
  `candidateSet`) with `McLetter` only. The three letter sites go through it: `ModelEvalLoader` ingest
  correctness, `TaxonomyJudgeService` induction rendering and the leakage-audit spans.
- `CorpusSource.kt`: `CorpusQuery(source, upstreamId, text, domain, task = domain)`, the `CorpusSource`
  interface and `MmluProCorpusSource`, one adapter per `DatasetType` over the fetcher's existing methods.
  `fetch` takes `domains: List<String>` (not `Set?`) so the selected-domain order the fetcher receives is
  unchanged. `MMLUQuery` gained `source: String = "MMLU_PRO"` (defaults are not serialised).
- `CorpusRegistry.kt`: the Spring bean holding static descriptors (table, id offset, verifier) for the five
  types plus the registered sources; the two former `when (datasetType)` blocks and the three literal
  `mmlu_pro` joins resolve through `tableFor`. `CorpusIds.namespaced/sourceOf/upstreamId` with MMLU_PRO at
  offset 0 and 1,000,000-wide namespaces. `ModelEvalStore` creates `corpus_registry(source, table_name,
  id_offset, verifier)` on open and inserts `(MMLU_PRO, mmlu_pro, 0, MC_LETTER)` if absent.
- Config: `corpora` (list; more than one entry fails at parse time with "multi-corpus runs are not
  supported before stage 1") and `corpusDbPath` in the hand parser. `corpusDbPath` is lifted out of the TOML
  in `Application.main` and published as the existing `taxoadapt.eval.db-path` property, which the fetcher
  now reads too, so all four SQLite beans open the same file; the runner verifies the store opened it.

Not done here (stage 0b/1): the TOML library, `corpus_question_link`, nullable `options_json`/`gt_answer`,
the two-level anchor layer, per-corpus split lines, `TournamentSimulator`'s own literal `mmlu_pro` (TUI-only
path, untouched), and `tools/analysis/corpus.py`.

## Stage 1 finding (2026-09-11): which corpora carry traces
Inspection of the downloaded records (18 models x 39 files, 8.2 GB): BBH, GPQA, MuSR and the leaderboard MMLU-Pro
are LOG-LIKELIHOOD tasks — each record holds one log-probability per answer choice and the metric (acc_norm / acc),
no generated text. Only MATH (exact_match, 7 subjects, level 5) and IFEval (prompt_level_strict_acc) are
generative and carry a real model response. Consequences: stage 1 (taxonomy structure: text only) and stage 2
(key-only router regret: is_correct for all 18 models on all six corpora) are unaffected and free; stage 3
(arena with judged traces) is possible from this source on MATH and IFEval only, plus MMLU-Pro through the
existing TIGER-Lab traces for the 5 overlapping models; BBH / MuSR / GPQA traces would need generation.
The leaderboard MMLU-Pro records carry doc.question_id = the TIGER-Lab id, so the MMLU_PRO namespace (offset 0)
stays aligned with the existing eval DB. Ingest: tools/ingest/multicorpus_db.py -> multicorpus_cache_v1.db
(never the v2 DB); pred for log-likelihood tasks = argmax choice, model_output empty, is_correct = the metric.

## Stage 2 result (2026-09-11, zero calls) — there IS something to route on a multi-corpus union
Criterion fixed in tools/analysis/multicorpus_router.py before running: routed-by-source beats the best single
model by more than 2 query-level bootstrap SE on the reserved side of a per-(source, domain) 0.30 split (seed 42).
Data: multicorpus_cache_v1.db, 21,606 questions x 18 models (MMLU-Pro 12,032; BBH 5,761; MATH 1,324; GPQA 1,192;
MuSR 756; IFEval 541), 52 strata. Best single model on the train side: Qwen2.5-72B-Instruct; best per source:
Qwen2.5-32B (MMLU-Pro), InternLM2.5-20B (BBH), Llama-3.1-70B (MATH), Command-R+ (MuSR), Llama-3.3-70B (IFEval),
Qwen2.5-72B (GPQA); 25 of 52 domains have a best model that differs from their source's best.
Reserved side (n = 6,481): best single 0.553 +- 0.006 | routed by source 0.593 | routed by source/domain 0.604 |
oracle 0.907. Router gain +0.040 +- 0.006 (source) and +0.050 +- 0.005 (domain) -> REAL. Disclosure: the DB
build summary printed best-model-per-corpus before the readout ran; the criterion predates both.
SENSITIVITY (same script, same split rule): the best single model scores 0.008 on MATH under the leaderboard's
strict exact_match extraction (a formatting artefact, not capability), which inflates the gain. Without MATH:
+0.013 +- 0.006 (source) / +0.027 +- 0.005 (domain) -> still REAL, half the size. GPQA's three "domains" are
prompt variants, and routing by them overfits (0.352 vs 0.385 single); merging GPQA changes little (+0.049).
Without MATH and MMLU-Pro (BBH/MuSR/IFEval/GPQA only): +0.042 / +0.069. Headline for the paper: routing by
task family and domain recovers 2.7 to 5.0 points over the best single model depending on the MATH treatment,
real in every variant; on MMLU-Pro alone the same machinery recovers 0.000. The oracle gap (0.30) is the
ceiling for any router. Output experiment_results/multicorpus/router_regret_mc6.txt.
Next: stage 1 (taxonomy structure on the union, Kotlin loader in progress) and, for stage 3, an arena on the
generative corpora only (MATH with a verifier reference, IFEval with the constraint checker) — budgeted.

## Stage 1 build + stage 2b result (2026-09-11, zero calls)
First six-corpus build (experiment_configs/multicorpus/mc6_s42.toml: promoted bareq512 body, label-free, 0.30 split
seed 42 on the union, 52 source/domain anchors): 242 nodes, 147 leaves (MMLU-Pro 88, BBH 25, MATH 16, GPQA 11,
IFEval 4, MuSR 3), embedding of 6,375 new texts on the local qwen3-embedding in 6.5 min, held-out Top-1 0.785
[0.775, 0.795] across 52 anchors (the MMLU-Pro-only tree scores 0.76-0.78 across 14). BBH's 24 sub-tasks barely
split (24 -> 25 leaves: homogeneous templates); MATH 7 -> 16 and GPQA 3 -> 11 do. Site-null certification and the
MMLU-Pro replay gate: see the stage-1 agent report below when it lands.
Stage 2b (tools/analysis/multicorpus_leaf_router.py, readout registered in its docstring before running): does the
GROWN taxonomy route better than the designed (source, domain) strata? Nearest-centroid routing of the reserved
queries: 77.2% land in their designed anchor, 90.6% in their true source; the cross-source flows are semantic
(MMLU-Pro -> MATH 289, MMLU-Pro -> GPQA 159, GPQA -> MMLU-Pro 73). Reserved side (n = 6,479): best single 0.553,
by source 0.591, by domain 0.601, by taxonomy leaf 0.592, oracle 0.906; leaf minus domain = -0.009 +- 0.003 ->
the taxonomy LOSES to the designed strata as a router (prediction: within +-1pp). Per source: GPQA +3.4 (its
questions borrow MMLU-Pro physics/chemistry leaves with more support), MATH -4.5, MMLU-Pro -1.4, BBH / MuSR 0.
Reading, consistent with LEAF-POWER on MMLU-Pro: model strengths live at the task-family / domain level; finer
leaves only dilute support. The router value of the union comes from the family layer (stage 2, +2.7 to +5.0pp),
not from the taxonomy's leaves; the taxonomy's contribution is routing unlabeled queries to that layer (90.6%
source accuracy, 77.2% domain accuracy) and the arena's cells, not finer capability profiles.
Output experiment_results/multicorpus/leaf_router_mc6.txt.

## Stage 1 certification result (2026-09-11) and the design adjustment it forces
Site-level null on the union snapshot (site_null_mc6_s42.csv, 94 sites, 1,032 s): 5 certified — 3 of the 14
MMLU-Pro anchors and 2 deeper sites; BBH 0/1, GPQA 0/3, MATH 0/6, IFEval 0/1, MuSR none. The MMLU-Pro-only build
at the same ratio and seed certifies 8 (11 and 11 at the other seeds). So the union does NOT buy certified
structure; it costs it, on MMLU-Pro itself. The loop stopped at iteration 13 of 50 by the J-stationarity rule (streak 5/5; a known risk from the construction-loop audit): 911 proposals, 816 rejected, 94 accepted (MMLU-Pro anchors 14, MATH 6, GPQA 3, IFEval 1, deeper sites the rest).
Reading: the z-gate accepted 94 splits (14 under MMLU-Pro anchors, 6 MATH, 3 GPQA, 1 IFEval, 1 BBH, the rest
deeper) [corrected 2026-09-14: site_null_mc6_s42.csv has 25 depth-1 sites, not the 24 this list implies -
BBH/formal_fallacies was omitted, so the deeper sites number 69, not 70]
but the site null certifies 5 of them (5%, vs 12% = 8/68 on MMLU-Pro alone)
[CORRECTED 2026-09-14, N4: this sentence originally ended "and MMLU-Pro depth-1 certification roughly halved".
That claim does not survive being paired and is withdrawn. Both site-nulls already existed, so no rerun was
needed - only a correct reading. On the SAME 14 MMLU-Pro depth-1 anchors the union certifies 3 and the solo
build 5, with 4 discordant anchors (1 union-only, 3 solo-only): exact McNemar two-sided p=0.625. Two anchors of
fourteen is not a halving and is not distinguishable from noise. Worse, one of the solo build's 5 is a boundary
case - math certifies with observed_sep 0.0377 against a p95 of 0.0377, margin exactly 0.0000 and q_site exactly
0.0500 on a 0.05 bar - so the baseline the comparison rests on is itself 4-or-5 depending on whether the bar is
strict. See the SUPPORT reading below, which is the effect that is real.] One loop over 52 anchors stops on a GLOBAL stationarity criterion long before each corpus is
refined, and the new corpora (BBH templates, GPQA at 198 x 3, MuSR at 250 x 3) are too small or too homogeneous
to certify a split under the site null at all. The union's routing layer is unaffected (91% source, 77% domain accuracy), and so is
stage 2 (keys only).

N4 RECONCILED (2026-09-14, zero calls): what the union actually costs is SUPPORT, not separation.
The withdrawn "halved" claim pointed at the right conclusion for the wrong reason, and the real mechanism is
both smaller and more specific. Pairing the two site-nulls anchor by anchor:
  - MMLU-Pro loses 1,057 questions of depth-1 support in the union, 8,501 -> 7,444 (-12.4%), because the loop's
    global budget is spent on 25 depth-1 sites instead of 14. The loss is concentrated: math -59.4%,
    biology -15.3%, physics -14.9%, philosophy -12.9%, chemistry -11.5%, other -10.4%; the remaining eight
    anchors move by less than 10% and four of them GAIN.
  - The per-anchor certification margin (observed_sep - site_null_p95) tracks that support loss:
    Pearson r = +0.598 over the 14 anchors (t=2.59, df=12). The six anchors losing more than 10% of their
    support shift by -0.0148 on average; the eight that keep theirs shift by +0.0002 - that is, not at all.
  - Only ONE anchor shows a genuine structural collapse rather than a support effect: chemistry, whose
    observed separation falls 0.0882 -> 0.0478 on only an 11.5% support loss (margin +0.0432 -> -0.0021).
    The other two "lost" anchors were boundary cases that never had a margin to lose - history at +0.0013 and
    math at exactly +0.0000.
So the union does not dissolve MMLU-Pro's structure; it dilutes the evidence for it, by spending one shared
refinement budget across six corpora of wildly different sizes. That is a strictly stronger argument for the
federated design than the withdrawn claim was, because a support effect is predictable and fixable by
construction (each corpus gets its own loop and its own budget) whereas a structural one would not be. It also
explains why the federated build recovers 13 certified sites against the joint loop's 5 without any change to
the separation criterion.
Reproduce: pair experiment_results/multicorpus/site_null_mc6_s42.csv against site_null_mmlu_pro_lb_s42.csv on
the 14 MMLU_PRO_LB/* depth-1 labels; certification is q_site <= 0.05.

N4 MECHANISM CORRECTED (2026-09-15, from the session review, verified in the build logs): the paragraph above
attributes the support loss to "one shared refinement budget ... spent on 25 depth-1 sites instead of 14". That is
NOT what the logs show. Between the first and last tree prints of mc6_s42.build.out the MATH anchors grow from
926 to 1,586 questions (+660) and GPQA from 495 to 762 (+267), while MMLU_PRO_LB falls 8,236 -> 7,444 (-792), with
MMLU_PRO_LB/math alone 945 -> 367 (-578) and physics 906 -> 773 (-133). In the solo build MMLU_PRO_LB/math goes
945 -> 904 and MATH solo 926 -> 962. So the union costs MMLU-Pro depth-1 membership through CROSS-CORPUS ABSORPTION
during the joint loop - MMLU-Pro math and physics questions migrate into the MATH and GPQA anchors - not through a
proposal budget spread thin. Stage 2b had already recorded "MMLU-Pro -> MATH 289" (above). Consequences: the
"same 14 anchors" pairing compares a 367-question math residual against a 904-question anchor, and the r=+0.598
between support change and margin change is carried by that one point (drop math: r=+0.39, t=1.40; drop math and
chemistry: +0.36). Two smaller misstatements in the same paragraph: "four of them GAIN" is two (economics +1.5%,
health +2.4%); "shift by +0.0002, that is, not at all" is a cancelling mean (business +0.0123, history -0.0042).
The withdrawal of "roughly halved" stands. The federated-construction conclusion also stands, for a different
reason than stated: per-corpus loops prevent absorption. And the union's MATH 0/6 site-null rows were computed on
populations roughly 40% MMLU-Pro, which the certification comparison should say.

DESIGN ADJUSTMENT (federated construction, replaces "one loop over the union"): build each corpus with its own
loop, budget and site null (the single-corpus quality is then preserved by construction — the MMLU-Pro tree IS
the promoted bareq512 tree), and assemble the union as a root whose depth-1 children are the per-corpus roots;
the union is only a routing layer plus the arena cells beneath it. This is what the CorpusSource plugin already
allows: `corpora` with >1 entry becomes "graft per-corpus snapshots under a union root", not "re-grow everything".
Certification is then reported per corpus by definition, the reserved pools stay per corpus (hygiene rule intact),
and a new corpus can be added without rebuilding the others — the online-router property the user asked for.
Cost: zero LLM calls (label-free builds; MMLU-Pro reuses the promoted snapshot). Stage 1b = implement the graft.

## Stage 1b result, per-corpus half (2026-09-11 14:15, zero calls) — federated construction recovers certification
Six per-corpus label-free builds on multicorpus_cache_v1.db (promoted bareq512 body, own 0.30 split, seed 42),
each with its own loop and site null (chain wall: builds 24-186 s each; site-nulls 24-1,158 s, serialised):
  corpus       sites certified (depth-1)  leaves  iterations  within-corpus Top-1
  MMLU_PRO_LB   66      8 (5)               81      14         0.758
  BBH           15      4 (4)               39       7         1.000  (24 template sub-tasks; trivially routable)
  MATH           4      0 (0)               11       9         0.683
  GPQA           2      0 (0)                5       7         0.994
  IFEVAL         2      1 (1)                4       7         1.000
  MUSR           0      0 (0)                3       5         1.000
  sum                  13                  143
One-loop union (mc6_s42) for comparison: 94 sites, 5 certified, 147 leaves, 13 iterations. So the federated form
certifies 13 sites where the joint loop certified 5, and MMLU-Pro built alone from the leaderboard DB reproduces
the 8 certified sites of the same recipe on the original database (r30: 8). BBH alone grows 39 leaves with 4
certified anchors where the joint loop gave it 25 leaves and none. MATH, GPQA and MuSR certify nothing on their
own either: they are too small (1,324 / 1,192 / 756 questions) for the site null at minClusterSize 55 — a support
limit, not a union artefact. Conclusion: the design adjustment holds; the union is a routing layer over
per-corpus trees. The graft and its union Top-1 per source follow in the agent report.

## Stage 1b result (2026-09-11, zero calls): federated construction + union graft

Six per-corpus builds (`experiment_configs/multicorpus/<corpus>_s42.toml`, mc6 body, one corpus each, own loop /
split / site null; chain `tools/chains/sweep_chain.ps1`), then the union grafted by the new headless mode
`unionSnapshots = [...]` (`UnionGraft.kt`: ids re-keyed `<SOURCE>:<id>`, depths + 1, per-corpus roots become
depth-1 children of a union root labelled `BBH+MATH+…`; the root gets the engine's single-node vMF fit and the
shrinkages; the union pool = union of the per-corpus pools, recorded + activated on the multi-corpus DB and pinned
by the snapshot). Per-corpus readouts `experiment_results/multicorpus/<corpus>_s42_readout.txt`, union
`union_s42_readout.txt`.

| corpus | queries | build wall | iterations (stop) | nodes / leaves | held-out Top-1 | certified / sites |
|---|---|---|---|---|---|---|
| MMLU_PRO_LB | 12,032 | 186 s | 14 (J-stationarity) | 148 / 81 | 75.8% [74.4, 77.2] | 8 / 66 |
| BBH | 5,761 | 64 s | 7 | 55 / 39 | 100.0% | 4 / 15 |
| MATH | 1,324 | 33 s | 9 | 16 / 11 | 68.3% [63.6, 72.7] | 0 / 4 |
| GPQA | 1,192 | 28 s | 7 | 8 / 5 | 99.4% | 0 / 2 |
| MUSR | 756 | 24 s | 5 | 4 / 3 | 100.0% | 0 / 0 |
| IFEVAL | 541 | 24 s | 7 | 7 / 4 | 100.0% | 1 / 2 |
| **union (graft)** | 21,606 | 101 s | — | 239 / 143 | 72.1% [71.0, 73.2] | **13 / 89** (sum) |

Certification: 13/89 federated vs 5/94 for one loop over the union (stage 1); MMLU_PRO_LB alone certifies 8, the
same as the MMLU-Pro campaign build at this ratio and seed, so the per-corpus quality is preserved by construction.
Routing on the union (6,482 held-out, 0 unrouted): 84.2% land in their true corpus root, 71.5% in their designed
(source, domain) anchor, Top-1 72.1%; per source BBH 91/91, GPQA 88/88, IFEVAL 91/91, MUSR 100/100, MATH 95/66,
MMLU_PRO_LB 78/58 (source/domain). The union's Top-1 is below the one-loop tree (78.5%) and below its members alone
(MMLU_PRO_LB 75.8% -> 59.5% inside the union): the added root level is a six-way vMF softmax under the production
beam/descent gate and sends 22% of MMLU-Pro questions to the adjacent GPQA/MATH/BBH roots (the stage-2b flows);
the flat nearest-centroid sweep over the same 143 leaves scores 81.6%, so the loss sits in the root descent, not
in the leaves. Gates: unit suite green with `UnionGraftTest` (id uniqueness, depth shift, pool-union hash); stage-0a
replay of bareq512_s137 bit-identical on structure after the change; frozen pool p2dca re-pinned.

## Stage 1c result (2026-09-11, zero calls): the union root routing rule

Stage 1b left the union's routing loss localised at the new root level. Stage 1c makes the union ROOT step a
config choice — `unionRootRouting = "descent" | "flatLeaf" | "sourceGate"` (default `descent` = the stage-1b
behaviour verbatim, so nothing changes without the key) — implemented as pure rules in
`src/main/kotlin/taxonomy/service/UnionRouting.kt` and read only by `exportUnionRouting` in the union assembly
path. Single-corpus construction and routing never reach this code; the stage-0a replay gate proves it. All three
rules run over the SAME six per-corpus snapshots (no rebuild; the assembly re-runs only because the union mode
saves its own snapshot). Configs `experiment_configs/multicorpus/union_s42{,_flatleaf,_sourcegate}.toml`,
readouts `experiment_results/multicorpus/union_s42{,_flatleaf,_sourcegate}_readout.txt`.

| rule | union Top-1 (95% Wilson) | source acc | domain acc | MMLU_PRO_LB Top-1 / source | vs descent (paired) |
|---|---|---|---|---|---|
| `descent` (default) | 72.08% [70.97, 73.16] | 84.22% | 71.54% | 59.46% / 78.00% | — |
| `flatLeaf` | **81.58% [80.62, 82.50]** | **95.46%** | **81.12%** | **74.06% / 96.18%** | +9.50pp, 819/203, p = 1.8e-82 |
| `sourceGate` | 72.05% [70.94, 73.12] | 84.20% | 71.52% | 59.49% / 78.05% | -0.03pp, 3/5, p = 0.72 |

`flatLeaf` (nearest leaf centroid over all 143 grafted leaves; source and domain read off the leaf's depth-1 and
depth-2 ancestors) reaches exactly the flat nearest-centroid sweep stage 1b reported (0.8158), so that sweep was a
reachable rule, not an upper bound. It recovers MMLU-Pro almost entirely (source 78.0% -> 96.2%, Top-1 59.5% ->
74.1% against 75.8% for the MMLU-Pro tree routed alone) and takes BBH to 100%; it costs GPQA (88.0% -> 77.7%) and
MATH (65.6% -> 60.8%), which the root descent had been over-feeding from MMLU-Pro's physics/chemistry and word
problems. `sourceGate` (nearest per-corpus root vMF, then the production descent inside that tree) is a NULL — 8
of 6,482 verdicts change — because the descent's first step from the union root is already an argmax over the same
six root directions. That is the informative negative: the 22% MMLU-Pro leak is a property of the per-corpus ROOT
DIRECTIONS (a whole-corpus vMF cannot separate MMLU-Pro from its neighbours), not of the beam width or the descent
gate, and the discriminative signal lives in the leaf centroids. **Recommended default from stage 2 onward:
`flatLeaf` for union runs**, with `descent` kept as the key's default so every existing config replays unchanged.

Readout hardening found on the way: `embeddings_cache.db.queries` is keyed by TEXT and shared across corpora, so an
MMLU_PRO run (the replay gate itself) rewrites the MMLU_PRO_LB category of every shared question to its bare form
and silently zeroes MMLU_PRO_LB Top-1 in a later union readout. `exportUnionRouting` now builds its leaf profiles
from the corpus DB's designed `(source, domain)` keys and only falls back to the rehydrated category, logging how
many disagreed; with that in place the `descent` re-run reproduces stage 1b to the digit (72.08%). The generic
`MAIN_centroid_routing_results.csv` in a union output directory is NOT hardened and is contaminated after any
MMLU-Pro run — read the union numbers from `MAIN_union_routing*.csv` only.

Gates: unit suite green (295 tests) with `UnionRoutingTest` (one test per rule on a tiny synthetic graft, plus
argmax/slice-width/tie-break, tree ancestry, key parsing, Wilson); stage-0a replay of bareq512_s137 bit-identical
on structure; frozen pool p2dca21ab5f4ef3ae re-pinned.

## Registered 2026-09-13 (before running) — MC-E2E: the deployed router, and MC-SEEDS: its replication
Stage 2 measured the router with ORACLE metadata: the policy was indexed by the question's TRUE (source, domain).
A deployed router has to infer the cell. MC-E2E applies the same policies through the taxonomy's own prediction
(stage 1c's flatLeaf rule: nearest centroid over the 143 federated leaves; 95.5% source / 81.1% domain accuracy),
and MC-SEEDS repeats everything at seeds 42 / 137 / 2048.
Arms (all learned on the TRAIN side, evaluated on the reserved side of a per-(source, domain) 0.30 split):
best single; policy by TRUE source; by TRUE (source, domain) [both oracle-metadata, = stage 2]; by PREDICTED
source; by PREDICTED (source, domain); by PREDICTED leaf (train questions also routed, min 20 train per leaf,
else fall back to the predicted domain); per-question oracle. Query-level bootstrap SE, 200 resamples per seed.
REGISTERED: (1) the DEPLOYED router (policy by predicted source/domain) beats best single by more than 2 SE in
ALL THREE seeds; (2) the metadata cost = oracle-cell gain minus predicted-cell gain, reported per seed;
(3) MC-SEEDS: the deployed gain's across-seed spread is smaller than its within-seed SE (i.e. the headline is
seed-stable). Predictions: deployed gain +2 to +4pp (vs +5.0 with oracle metadata), metadata cost 1 to 2pp,
across-seed spread under 1pp. Output experiment_results/multicorpus/router_e2e.txt; script
tools/analysis/multicorpus_router_e2e.py. Zero LLM calls.

## MC-E2E + MC-SEEDS result (2026-09-13, zero calls) — the deployed router holds; its magnitude is seed-sensitive
[CORRECTED 2026-09-23 by the registrar (script identity only; no number changes): the script that produced this result is tools/analysis/multicorpus_router_e2e.py at 9865009, sha16 84c62136c711f37d (git show 9865009:tools/analysis/multicorpus_router_e2e.py | sha256sum). The file was EDITED AFTER this run — the --mathfix extractor and the clean-pool restriction landed later (13f2142) — so re-running today's working copy does NOT reproduce the numbers in this section; the MATH-FIX section and the 2026-09-14 CORRECTION section below carry what those edits changed. Zero calls, so there is no cache pin to check.]
Routing 21,606 questions over the 143 federated leaves (flatLeaf): predicted source 96.2%, predicted
source+domain 81.3%. Reserved side (n = 6,481 per seed), three seeds:

  arm                     seed 42            seed 137           seed 2048
  best single             0.5535 +- 0.0060   0.5629 +- 0.0055   0.5626 +- 0.0063
  TRUE source             0.5931             0.5869             0.5922      <- oracle metadata (stage 2)
  TRUE source/domain      0.6039             0.6056             0.6101      <- oracle metadata
  PRED source             0.5888             0.5829             0.5885      <- deployed
  PRED source/domain      0.6027             0.5965             0.6033      <- deployed
  PRED leaf               0.5982             0.5894             0.5994
  oracle                  0.9067             0.9065             0.9056

REGISTERED (1) PASS: the deployed router beats the best single model by more than 2 SE in all three seeds
(+0.0492 / +0.0336 / +0.0407, SE ~0.0053). REGISTERED (2) METADATA COST = +0.0012 / +0.0091 / +0.0068 — the
taxonomy's own cell prediction costs the router only 0.1 to 0.9pp against knowing the true (source, domain).
That is the headline of the routing chapter: the routing layer is nearly free, so the oracle-metadata numbers of
stage 2 were not an artefact of privileged information. REGISTERED (3) FAIL: the across-seed spread of the
deployed gain (0.0156) exceeds the mean within-seed bootstrap SE (0.0053) — the bootstrap resamples questions
within one split, while a seed change re-draws the split AND re-learns the policy, so the point estimate moves
between +3.4 and +4.9pp. Reporting rule: quote the deployed gain as +4.1pp (range +3.4 to +4.9 over three
seeds), never a single seed's value. PRED leaf (0.598) again loses to PRED source/domain (0.603), consistent
with stage 2b and LEAF-POWER: model strengths live at the family/domain level.
Output experiment_results/multicorpus/router_e2e.txt; script tools/analysis/multicorpus_router_e2e.py.

## Registered 2026-09-13 (before recomputing) — MATH-FIX: a tolerant answer extractor for the MATH corpus
Diagnosis (exploratory, zero calls): the leaderboard's MATH-hard task scores a Minerva-style template and its
exact_match only credits the literal sentence "The final answer is X". Six of the 18 models score EXACTLY 0.000
and three more under 0.035, including Qwen2.5-72B-Instruct (0.012) and Llama-3.3-70B-Instruct (0.002), while
Llama-3.1-70B — which emits both \boxed{} and the sentence — scores 0.280. Inspection of single questions shows
correct values inside \boxed{} or in prose that the extractor discards, and reasoning models (the R1 distills)
truncated mid-derivation by the harness's token limit.
CORRECTION RULE (fixed before any recompute): extract the model's answer as the FIRST match of, in order,
(a) the last \boxed{...} / \fbox{...}, (b) "final answer is ..." up to the sentence end, (c) the last number in
the response; then normalise both sides (strip $ \left \right \!\, \text{} \mbox{} spaces commas trailing period,
drop a leading "x =", unwrap \dfrac/\tfrac/\frac{a}{b} and a/b to a decimal when both parts are numeric); compare
numerically with relative tolerance 1e-6 when both sides parse as numbers, else by exact normalised string.
Correctness is only ever RAISED where the leaderboard said 0 and never lowered where it said 1 (the rule is
audited by reporting disagreements in both directions; a 1 -> 0 disagreement is a bug in the extractor, not a
correction). REGISTERED READOUTS: (1) per-model corrected MATH accuracy and the count of responses with NO
extractable answer (a floor, not a fix — truncation); (2) whether the five models at exactly 0.000 rise above 0.10 [corrected 2026-09-14: five, not six - Llama-3.3-70B at 0.002 was counted both among the zeros and among the near-zeros];
(3) MC-E2E re-run on the corrected data: the deployed router gain over the best single model, three seeds.
Predictions: the zero models rise to 0.3-0.7; MATH's best single rises far above 0.008, so the deployed gain
SHRINKS, to roughly +2 to +3.5pp. Output experiment_results/multicorpus/math_fix.txt; the corrected column is
written to a NEW table `eval_results_mathfix` — the ingested rows are never overwritten.

## MATH-FIX result (2026-09-13, zero calls) — the artefact was large, and the corrected router gain is +2.7pp
Applying the registered extractor to all 23,832 (question, model) MATH rows corrected 5,181 cells (21.7%).
Per-model MATH accuracy, before -> after: Qwen2.5-32B 0.000 -> 0.597, Qwen2.5-72B 0.012 -> 0.582,
Qwen2.5-Math-7B 0.248 -> 0.563, Qwen2.5-7B 0.000 -> 0.489, Llama-3.3-70B 0.002 -> 0.472, internlm2.5-20B
0.000 -> 0.396, Llama-3.1-70B 0.280 -> 0.386, Qwen2.5-Coder-7B 0.034 -> 0.376; the smaller models move by 1-8pp.
REGISTERED READOUT (2) PASS: all models that scored exactly 0.000 rise above 0.10. [CORRECTED 2026-09-14: there are FIVE such models, not six, and THREE clear 0.38, not four - Llama-3.3-70B (0.002) was counted both among the zeros and among the near-zeros. The PASS verdict is unaffected; the criterion's own text was wrong. From math_fix.txt: 0.598, 0.489, 0.397, 0.198, 0.144.]
Two upstream facts found on the way, both documented rather than worked around:
  * the leaderboard's own `doc.answer` stores "\iny" where the source dataset has "\infty" — its unit stripper
    eats the substring "ft" inside the token (verified in the raw JSONL). The extractor repairs this on both
    sides; without the repair every interval-valued answer is unscorable.
  * the two R1 distills are truncated mid-derivation by the harness's generation limit (40 and 27 responses with
    no extractable answer), so their corrected 0.198 and 0.144 are FLOORS, not estimates.
60 rows (0.25%) keep a credit the extractor does not recognise (symbolic equivalence such as
\frac{\ln 8}{\ln 4} = 3/2, or 2^2(3-x)(3+x) = 4(3-x)(3+x)); the rule only ever raises, so those stay correct.
The corrected column lives in a NEW table `eval_results_mathfix`; the ingested rows were never overwritten.
REGISTERED READOUT (3), MC-E2E re-run with the overlay (`--mathfix`), three seeds: best single rises to
0.587 / 0.599 / 0.598 (from 0.554 / 0.563 / 0.563) and the DEPLOYED router gain falls to +3.36 / +2.08 / +2.75pp,
mean +2.7pp, still REAL in every seed (SE ~0.51). The metadata cost collapses to -0.05 / +0.57 / +0.23pp: with
MATH scored properly, inferring the cell costs the router essentially nothing. The seed-stability clause fails
again (spread 1.28pp vs SE 0.51pp).
HEADLINE FOR THE PAPER (supersedes stage 2's +5.0pp): routing over a union of task families gains
**+2.7pp (range +2.1 to +3.4 over three seeds) against the best single model, with the cell inferred by the
taxonomy rather than given**; the per-question oracle is 0.920, so the router closes about 8% of the available
headroom. Every number quoted from MATH must use the corrected column, and the correction must be disclosed.
Output experiment_results/multicorpus/{math_fix.txt, router_e2e_mathfix.txt}; script tools/analysis/math_fix.py.

## Registered 2026-09-13 (before any call) — GEN-ARENA: does the deployed judge reproduce the router WITHOUT keys?
Everything in the routing chapter so far is key-based. The thesis's mechanism is judging without an answer key,
so the open question is whether a judged arena on the union's GENERATIVE corpora recovers the same per-corpus
model ordering — and therefore the same router decisions — that the keys give.
DESIGN. Corpora: MATH and IFEval (the only two of the six that carry model traces). Questions: the RESERVED side
of the per-(source, domain) 0.30 split at seed 42, recomputed in Python exactly as multicorpus_router_e2e.py does,
so the arena and the router analysis share a split by construction. Roster: 8 of the 18 models, chosen before
launch to span the range and to include both key-based per-corpus winners (Qwen2.5-32B-Instruct on MATH after
MATH-FIX, Llama-3.3-70B-Instruct on IFEval): Qwen2.5-32B-Instruct, Qwen2.5-72B-Instruct, Llama-3.3-70B-Instruct,
Qwen2.5-Math-7B-Instruct, Llama-3.1-70B-Instruct, Mistral-Small-Instruct-2409, Phi-3.5-mini-instruct,
Mixtral-8x7B-Instruct-v0.1 (28 pairs). Schedule: 3,000 matches, 1,800 MATH / 1,200 IFEval, dealt round-robin over
the 28 pairs within each corpus and uniformly over that corpus's reserved questions, seed 42.
JUDGE: grok-4-1-fast-non-reasoning (the JUDGE-SWAP choice) with the v2 verify-first mechanics, dual order,
confidence — and NO induced rubric, because the per-corpus trees were built label-free and because the rubric
line closed null. The REFERENCE is the verifier, not a solver: for MATH the corrected target answer, for IFEval
the human-readable list of instruction constraints the response must satisfy. Zero reasoning calls; 6,000 judge
calls total. Correctness for scoring uses the corrected MATH column (eval_results_mathfix) and IFEval's
prompt_level_strict_acc.
REGISTERED: (1) key-decidable accuracy >= 0.75 overall; (2) per-corpus judged BT board Spearman rho vs corrected
key accuracy >= 0.85 on BOTH MATH and IFEval; (3) THE BRIDGE — the judged per-corpus argmax equals the key-based
per-corpus argmax on both corpora, i.e. a router built on judged verdicts alone picks the same model as the
key-based router; (4) decidable tie rate <= 15%. DESCRIPTIVE: accuracy split by corpus; flip rate; whether the
judge does better where the verifier reference is exact (MATH) than where it is a constraint list (IFEval).
Predictions: accuracy 0.78-0.85 (below MMLU-Pro's 0.852: free-form answers are harder to compare than lettered
options), rho 0.88-0.95, the bridge HOLDS on MATH and is the coin-flip on IFEval (only 4 leaves, 162 reserved
questions), ties 8-12%. Output experiment_results/multicorpus/gen_arena*.txt; cache gen_arena_grok.db;
script tools/analysis/generative_arena.py.

## GEN-ARENA result (2026-09-13) — REGISTERED FAIL: the judge ranks the field but cannot pick the winner
3,000 matches, 5,994 calls, 0 errors, 0 invalid verdicts. Judge grok-4-1-fast-non-reasoning, v2 mechanics, dual
order, no rubric, VERIFIER reference (MATH: the corrected target; IFEval: the constraint list).

  corpus   matches  key-decidable  accuracy  decidable ties  flip
  MATH       1800     568 (32%)     0.935        0.055       0.237
  IFEVAL     1200     407 (34%)     0.658        0.256       0.380
  ALL        3000     975 (32%)     0.819        0.138       0.294
  [CORRECTED 2026-09-23 by IFEVAL-RESPONSE-ORACLE's post-run adversarial review (docs/reviews/2026-09-23_ifeval_response_oracle_post.md, eae039e, defect D2; nothing above is rewritten): THE COLUMNS OF THIS TABLE MIX DENOMINATORS AND WERE NOT LABELLED. `matches` is the whole schedule; `key-decidable` is the deciding subset; `accuracy` and `decidable ties` are ON THE KEY-DECIDABLE SUBSET (IFEVAL 407 of 1,200; MATH 568 of 1,800); but `flip` is ON THE WHOLE SCHEDULE for both corpora - MATH 0.237 = 0.23667 over 1,800 and IFEVAL 0.380 over 1,200. On the key-decidable subset the IFEval flip rate of this same cache is 0.228501 (measured read-only from gen_arena_grok.db). ANY FUTURE PREDICTION OR COMPARISON QUOTING THIS TABLE MUST NAME THE DENOMINATOR IT IS ON: IFEVAL-RESPONSE-ORACLE's P4 inherited the ambiguity, was recorded FAILED against the whole-schedule 0.380, and HOLDS at |0.2432 - 0.2285| = 0.015 on the registered key-decidable denominator (programme outcome section, 2026-09-23). IFEVAL-RESPONSE-ORACLE's control arm may be transported onto this IFEVAL cell only as 0.6585 / 0.2555 / 0.2285, never against 0.380.]
  [CORRECTED 2026-09-23 by the IFEVAL RULING (docs/agents/leads/2026-09-23_ifeval_ruling.md, af116f8, judge-design-specialist, zero calls): the IFEVAL row's 0.658 is the SPECIFICATION rung AND IT IS PERMANENT - there is no question-level checker output on IFEval to raise it with, at any price.]

(1) accuracy >= 0.75: 0.819 OK. (4) ties <= 0.15: 0.138 OK. (2) rho >= 0.85: MATH 0.922 OK, IFEval 0.719 FAIL.
(3) BRIDGE: BREAKS on both corpora. Overall: FAIL.

THREE FINDINGS, in order of importance.
1. **An exact verifier reference beats everything we achieved on MMLU-Pro.** MATH key-decidable accuracy 0.935,
   against 0.852 for the deployed judge on MMLU-Pro and 0.757 for the production judge — on FREE-FORM answers,
   which are harder to compare than lettered options. This is the "checker instead of solver" payoff stated in
   the design: where a verifier exists, the reference is exact, costs no reasoning call, and the reference
   ceiling that limits the MMLU-Pro judge (wrong 42-48% on frontier pairs) simply does not arise.
2. **A reference that LISTS what to check is not a reference that CHECKS.** IFEval gives the judge the
   constraint list and it must verify satisfaction itself: accuracy 0.658, decidable ties 25.6%, flips 38.0%
   (MATH: 5.5% and 23.7%). The judge abstains or flips rather than counting constraints. Constraint checking is
   executable code, and a judge should be given the checker's OUTPUT, not its specification.
   [CORRECTED 2026-09-23 by the IFEVAL RULING (docs/agents/leads/2026-09-23_ifeval_ruling.md, af116f8, judge-design-specialist, zero calls, zero execution): THE LADDER'S IFEval RUNG STAYS AT SPECIFICATION 0.658 PERMANENTLY, because IFEval HAS NO QUESTION-LEVEL CHECKER OUTPUT. MATH's verifier emits a canonical answer string that exists BEFORE any response; IFEval's emits a PREDICATE ON A RESPONSE (prompt_level_strict_acc = all(inst_level_strict_acc), the identity asserted row by row at tools/analysis/checker_answer_ingest.py L513 / L528). Its fields split into question-level (instruction_id_list + kwargs = the SPECIFICATION already measured at 0.658) and response-level (inst_level_strict_acc and anything it follows from), and every response-level field DETERMINES THE KEY. So GEN-ARENA finding 2's 'a judge should be given the checker's OUTPUT, not its specification' is UNREALISABLE on this corpus at any price, and a per-response pass vector is an ORACLE-CLASS, RESPONSE-LEVEL object whose accuracy may NEVER be quoted beside MATH's 0.958 (two independent reasons: the reference objects are not the same kind, and no IFEval cap-hit proxy exists - checker_answers_v2.db is MATH-only, v1's non_terminated is the unclosed-<think> proxy, and IFEval's harness cap is 1,280, programme L3741). This is a STRUCTURAL claim about a corpus family whose verifier is a predicate over the response, and REF-FORM-BY-CELL's closure does not cover it: that closure's object throughout was a question WITH a canonical answer.]
3. **The bridge breaks for a structural reason, and it is the same reason three times over.** Both boards order
   the field well (MATH rho 0.922) but invert at the top, where the judged top-two gap is 0.032 (MATH) and
   0.040 (IFEval) logits. A router consumes only the argmax, so it is maximally exposed to exactly the place
   judges are least reliable — the frontier near-tie already seen in ARENA-V2 (iask over gemini by 0.018 logits)
   and ARENA-V2-X20 (4 top-6 violations). Third independent appearance, now on a different corpus family, a
   different judge and free-form answers. On IFEval the failure has a sharper shape still: among its own top two
   the judge ordered the pair correctly, but the key's actual winner (Llama-3.3-70B, 0.870) was ranked fourth.
EXPLORATORY (not registered): the COST of routing on judged verdicts instead of keys is bounded and asymmetric —
MATH -6.3pp +- 3.6 (the judged pick is genuinely the weaker model), IFEval -0.6pp +- 3.8 (free), pooled -4.7pp
(0.649 vs 0.696 over 556 reserved questions). So a judged router is worse than a key router, not useless.
CONCLUSION FOR THE PAPER: judged verdicts substitute for an answer key when the claim is a RANKING (rho 0.92 on
MATH, and the whole MMLU-Pro campaign), and do NOT substitute when the claim is an ARGMAX, which is what routing
needs. State the router result as key-based, and report GEN-ARENA as the measured limit of the reference-free
mechanism plus the verifier-reference finding, which is the positive result of the run.
Output experiment_results/multicorpus/gen_arena_outcome.txt; script tools/analysis/generative_arena.py.

## CORRECTION 2026-09-14 — the reserved side of MC-E2E / MC-SEEDS was not the tree's held-out pool
Found by the ledger audit. `multicorpus_router_e2e.py` re-derives its own per-(source, domain) 0.30 split with
`random.Random(seed)`, while the federated trees that supply `pleaf` / `pdom` / `psrc` were built on the Kotlin
split whose held-out pool is `paeec37aa28063c75`. The two coincide only at chance: 1,946 / 1,973 / 1,914 of
6,481 reserved questions, i.e. 30.0% / 30.4% / 29.5%. So roughly SEVENTY PER CENT of every question these arms
were scored on had been TRAINING data for the taxonomy that routes it. This is the pool-mismatch incident
recurring in the multi-corpus line, and the POOL-PIN ledger row's claim that "Python analyses assert it" is true
of the MMLU-Pro scripts and false here.
RE-RUN ON THE CLEAN SUBSET (`--clean`, zero calls, output router_e2e_mathfix_clean.txt):
    seed   deployed gain (reported -> clean)      metadata cost (reported -> clean)
    42     +3.36pp -> +4.37 +- 0.92pp             -0.05pp -> -0.46pp
    137    +2.08pp -> +2.43 +- 0.98pp             +0.57pp -> +1.22pp
    2048   +2.75pp -> +3.34 +- 0.90pp             +0.23pp -> +1.36pp
    mean   +2.73pp -> +3.38pp                     +0.25pp -> +0.71pp
THE ROUTER HEADLINE SURVIVES AND WAS CONSERVATIVE: the deployed gain is LARGER on clean data in all three seeds
and registered criterion (1) still passes at more than 2 SE in each. Registered criterion (3) fails on the clean
subset and already failed on the contaminated one, so nothing flips there either.
THE SECOND HEADLINE DOES NOT SURVIVE AS WORDED. "Inferring the cell costs the router essentially nothing" was
measured at +0.25pp on data the router's taxonomy had mostly seen; clean it is +0.71pp, three times larger, and
positive in two of three seeds. Requote it as "inferring the cell costs about 0.7pp of the 3.4pp gain, i.e.
roughly a fifth of it" and drop "essentially nothing".
STANDING FIX: every Python analysis that consumes a Kotlin-built artefact must assert the pool it is scoring
against, as the MMLU-Pro scripts do. `--clean` is the option here; the default is left in place so the published
contaminated figures remain reproducible for comparison.

### The same defect in MC-LEAF, and what it does to that conclusion
`multicorpus_leaf_router.py` consumes the union tree's leaves and re-derives its own split the same way, so it
carries the same contamination. `multicorpus_router.py` (stage 2) does NOT: it routes on TRUE (source, domain)
metadata with no tree artefact, so its self-derived split is legitimate and stage 2 needs no correction.
Re-run with `--clean` (reserved side pinned to paeec37aa28063c75, 1,946 of 6,481 kept):
    leaf minus domain, as reported : -0.009 +- 0.003  -> "the taxonomy LOSES vs designed domains"
    leaf minus domain, clean       : -0.011 +- 0.007  -> NOT RESOLVED (within 2 SE)
The point estimate is unchanged in sign and slightly larger, but on data the tree has not seen the difference is
no longer resolved. The honest statement is that taxonomy leaves do not BEAT designed domains as a router, not
that they lose to them. Per source on the clean subset: BBH +0.006, MuSR 0.000, MMLU-Pro -0.011, MATH -0.034,
GPQA -0.053, IFEval -0.055 - the losses are concentrated in the small corpora where a leaf has few train
questions, which is LEAF-POWER's finding again (the binding quantity is distinct questions per cell).
Output leaf_router_clean.txt.
