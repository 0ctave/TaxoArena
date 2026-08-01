# Implementation — the system as built

State as of 2026-08-01, matching the code that produced the settled batch
(`experiment_results/r8/`). Chapter 3 of the thesis is the authoritative description; this
is the repository-level map of where each piece lives and what it actually does.

## 1. Data and id-spaces

- **Corpus**: MMLU-Pro, cached in `mmlu_pro_dataset_cache_v2.db`. Model outputs live in
  its `eval_results` table; embeddings (Qwen3) in `embeddings_cache.db`.
- **Three id-spaces coexist and must never be joined by id across sources**:
  snapshot queries use `q_<hash>` ids; `eval_results` uses numeric eval ids;
  `mmlu_pro.id` is a third space. In `embeddings_cache.queries` the column names are
  reversed (`id` holds the hash, `query_id` the numeric id). Categories are capitalized
  in `embeddings_cache` but lowercase in `eval_results`. **Join by question text only.**
- `Meta-Llama-3-70B-Instruct` (not to be confused with the clean
  `Meta-Llama-3_1-70B-Instruct`) sits in a foreign id-space and is excluded; its ids
  contaminate intersections (it once collapsed law from 287 questions to 20).
- The dataset ingest path guards two envelope defects
  (`TraceEnvelopeUnwrapTest`, `EvalIngestValidator`); the measured 99.4% format-preference
  result that motivated them is recorded in `archive/docs/arena-math-findings.md` and, in
  settled form, in the thesis (Appendix D exclusion policy).

## 2. Tree construction

Entry point: `HeadlessBenchmarkRunner` with a TOML config (`runPipeline = true`).
The construction is a J-gated loop over vMF-based splits:

- **Splitting** (`TaxonomySplitter`): seed-guided spherical k-means / von Mises-Fisher
  soft splits. A split is accepted only if its chance-corrected separation score clears a
  bar calibrated against a within-domain null (`separation_null_by_size.md`; the
  per-size p95 constants are tabulated in the splitter itself).
- **Acceptance** is a four-stage path with a proposal gate; proposals are fingerprinted
  and memoized (including no-proposal outcomes).
- **A global merge pass** removes phantom near-duplicate siblings.
- **Stopping**: the loop runs to a certified structural fixed point (certificate at
  iteration 10 for the frozen artifact; a twenty-seed sweep found only a period-2
  oscillation, documented in the thesis, Appendix E).
- **Cross-linking / polyhierarchy is removed.** The operator exists and was measured; the
  thesis reports it as a negative result. The canonical mode is tree-only.

**The frozen artifact** (`experiment_configs/freeze_mcs55.toml`): snapshot
`20260727_042523_Headless_Run_Auto_ge` in `snapshots.db` — 154 nodes, 87 leaves,
14 anchors, max depth 6, J = 0.253129, certified at iteration 10. Every settled run
loads this snapshot (`runPipeline = false`, `snapshotId` set).

## 3. Routing

Held-out (reserved) questions are routed to leaves by a gate/beam/floor scheme over vMF
log-likelihoods (thresholds 0.0486 / 0.0647, ratio 1.85×; derivation in the thesis,
Appendix E). Routing quality on the settled batch: 77.8% of routed questions land
on-subject; judged agreement on off-subject questions is indistinguishable from
on-subject (27 cells, permutation p = 1.0).

**Reserved-set separation is enforced at rubric induction, not at tree construction** —
the tree's leaf regions do contain reserved-split texts; the build-failing assertion
guarantees only that no judged question's text entered any rubric's induction pool
(verified by direct measurement: 0 of 1,569 judged texts appear in any pool).

## 4. Rubric (judge) generation

`TaxonomyJudgeService.generateJudgeForNode`: a leaf's rubric is induced from its **entire**
filtered construction pool, chunked into batches of 25 (a prompt-length batch size, not a
sample size), map-reduced into one rubric. The synthesis instruction separates WHAT
(leaf-specific criteria) from HOW (verdict format, tie policy — fixed globally); the
constraint text is quoted in the thesis, Appendix B. Rubrics are generated once per
frozen snapshot and reused. The induction model is the same model as the arena judge
(a stated limitation: self-written rubrics weaken the rubric-vs-generic contrast).

## 5. The arena

`TaxonomyArenaService` / `TaxonomyBenchmarkService`:

- **Paired design**: MAIN (per-leaf rubric, structured JSON verdicts) vs C5 (verbatim
  MT-Bench pairwise prompt, `[[A]]/[[B]]/[[C]]` parsing) replaying the identical
  comparison set under the same cells. The arms differ as a bundle (prompt, user
  template, output format, fixed confidence) — differences attribute to the bundle, not
  the rubric text alone.
- **Option mode RESOLVED** (the settled mode): the multiple-choice options block is
  withheld; each model's own selected answer is attached to its trace as text
  (attachment success 93.2–99.8% by domain). The judge never sees the reference answer.
- **Dual-call position reversal**: every logical comparison is two judge calls with
  positions swapped; disagreement scores as a tie.
- **Decidable agreement**: the exported judge-vs-key agreement counts decidable
  comparisons only (patched and verified: export 0.7520 == independent recomputation on
  the philosophy re-run).
- **Ratings**: Bradley–Terry fit per run, stored in the run's own `ratings_*.db`
  (`match_history`, `ratings`).
- **Judge model**: `Mistral-Large-3` in every reported run; it appears in no roster, so
  there is no self-preference confound.
- **Exclusion policy**: a hard-coded raise-on-load list (10 models: id-space mismatch,
  empty archives, mixed-format emitters). The operative threshold is format
  *consistency*; the policy is a ratchet on known failures, not a general guard.

## 6. Known defects that bound claims

- **Bradley–Terry confidence intervals are wrong** (the variance correction used `1/K`
  for `1/K²`) and have not been recomputed. No CI is rendered anywhere; do not report
  the `*CiLow/High` export fields.
- **`routingECE` export** aggregates a domain's leaf shares with `maxOf` instead of
  summing at both export sites.
- **The reliability constant** c = 2.52 was fitted on an eleven-model band that no
  longer matches any roster (and replaced the earlier r = n/(n+7.66), which was 3.04×
  too large).
- **Scheduler-seed spread**: the seed moves the MAIN-C5 rank-correlation difference by
  six grid steps (history, seeds 42/137); only per-verdict statistics carry decisions.
- The tests once wrote to production databases (`ratings.db`, the reserved pool);
  fixed 2026-07-26 — new tests must keep using temp copies.
