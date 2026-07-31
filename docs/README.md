# TaxoArena — documentation index and triage

**TaxoArena** induces a hierarchical taxonomy over MMLU-Pro queries from their embeddings,
so that each terminal cell can host an LLM-judge pairwise arena with a rubric specific to
that cell.

> **The system is a TREE, not a DAG.** Cross-linking was removed and polyhierarchy is
> reported as a negative result. The word "DAG" survives in file names, `DagMode` and
> `computeDagSeparationJ`; read it as "the induced hierarchy".

---

## The current state, in one place

Everything below is triaged against this. Where a document disagrees with it, the document
is wrong.

**Five paired arena runs are the results.** Every run: 12-model roster, both arms — MAIN
(per-leaf rubrics) and C5 (a generic MT-Bench prompt) — on an identical question set, arms
matched by construction, complete 66-pair coverage in every cell, confidence gate disabled.
`Delta rho` = MAIN - C5; positive favours per-leaf. Decisive threshold `|Delta rho| >= 0.007`,
two steps of the 0.0035 Spearman grid at M = 12. Both tie conventions always reported.

| domain | rho MAIN | rho C5 | half | drop | steps | n/arm |
|---|---:|---:|---:|---:|---:|---:|
| philosophy | 0.9441 | 0.8951 | +0.0490 | +0.0490 | **+14.00** | 966 / 966 |
| history | 0.8671 | 0.8531 | +0.0140 | +0.0140 | **+4.00** | 839 / 837 |
| engineering | 0.9895 | 0.9790 | +0.0105 | +0.0105 | **+3.01** | 649 / 649 |
| psychology | 0.8811 | 0.8741 | +0.0070 | +0.0070 | **+2.00** | 2405 / 2397 |
| mathematics | 0.9301 | 0.9371 | -0.0070 | 0.0000 | **-2.00** | 2328 / 2328 |

Four of five favour the per-leaf arm. Mean rho 0.9224 MAIN against 0.9077 C5. Answer-key
agreement MAIN / C5: philosophy 83.5/83.8, history 78.6/76.4, psychology 80.7/78.2,
mathematics **81.8/86.0** (the only gap clearing its own noise, at 2.4 SE, favouring C5),
engineering 92.0/91.4.

**Six things this batch must carry, every time.** (1) **Nothing in it is registered** —
every prediction in `prereg_generic_judge_baseline.md` was written against the superseded
M = 12 batch, and Addendum 4's registered mathematics re-run is the *old-logic* run.
(2) **Five of eight domains** — physics running, computer science not attempted, law failed
twice at 3x slower than comparable domains, unexplained. (3) **Engineering is unresolved**:
it was the old batch's one clean registered null (+1.00 / -1.00) and is now +3.01, and
nothing distinguishes "the new logic favours per-leaf" from "the old run was too broken to
see it". (4) **Absolute rho is not stable to three decimals** across analysis conventions.
(5) **No Bradley-Terry interval exists anywhere and none may be added.** (6) Mathematics is
two grid steps — closer to a tie than a loss, and still the one domain where the partition
does not help. The code is also **uncommitted**: 567 inserted lines across six files, no
hash to cite.

**The superseded M = 12 batch.** Eight domains, and not a baseline. Its bootstrap counted
the 66-pair floor over the whole domain and scheduled every bootstrap match on the largest
leaf, so exactly one cell per domain reached complete coverage and the rest sat at 4 to 33
pairs of 66; three runs also had arm imbalance down to 0.833. `Delta rho` on pooled domain
verdicts survives that; **no per-cell quantity from it does.** It is kept because every
pre-registration was written against it and because two registered nulls failed in it, in
opposite directions — computer science +2.00 / +8.00, the registered mathematics re-run
-23.04 / -29.05. Both must still be reported. Full record and numbers:
`batch-M12-complete-record.md`.

**The bound on every positive.** Per-leaf rankings are near-identical to the domain ranking:
on law, leaf-vs-domain Spearman runs 0.895 to 0.993, against 0.873 to 0.970 for ground truth
against itself. A positive `Delta rho` is a **precision gain on one shared ranking**, not
discovered specialisation. This must appear wherever a positive is claimed.

**The screen is not a clean predictor.** It predicts the domain aggregate, not within-domain
sub-structure; the correlation between screen p and within-domain between-leaf agreement is
**+0.072**. Philosophy was not flagged and gave the largest advantage.

**Three standing prohibitions.**

1. **No confidence interval, anywhere.** The Bradley-Terry variance correction used `1/K`
   instead of `1/K^2`; the intervals were never recomputed.
2. **The reliability constant 7.66 is wrong**, by 3.04x. Use `c = 2.52` at the 11-band, and
   two-sided disattenuation (`rho_obs / r`, not `rho_obs / sqrt(r)`).
3. **Six figures may never be restated.** See `void-results.md` §3.

---

## Triage — one line per file

`CURRENT` — trust it. `STALE-BUT-FIXABLE` — the design holds, named parts are out of date.
`SUPERSEDED` — do not write from it; a named replacement exists. `HISTORICAL-KEEP` — kept as
record, never as evidence.

### Start here

| file | triage | one line |
|---|---|---|
| [`newlogic-rerun-record.md`](newlogic-rerun-record.md) | **CURRENT** | The five-domain revised-scheduler batch — the results, with every qualification they carry. Rewritten 2026-07-31; the 2026-07-30 version covered three domains and its headline was false. |
| [`batch-M12-complete-record.md`](batch-M12-complete-record.md) | **SUPERSEDED as results; CURRENT as the registered record** | The eight-domain M = 12 batch. Not a baseline — one complete cell per domain, three runs with unequal arms. Kept because the pre-registrations point at it and two registered nulls failed in it. |
| [`stale-results-audit.md`](stale-results-audit.md) | **CURRENT** | Where every superseded per-domain number still sits in `report/` and `docs/`, per `file:line`, with what replaces it. The working list for the `report/` pass. |
| [`void-results.md`](void-results.md) | **CURRENT** | The quarantine list. Three sections: void after `c381211`, withdrawn, and never-restate. **Read before quoting any number in this project.** |
| [`known-defects.md`](known-defects.md) | **CURRENT** | Defects documented rather than fixed, each with its citation rule. Routing ECE entry corrected 2026-07-30. |
| [`measurement-discipline.md`](measurement-discipline.md) | **CURRENT** | Six rules, each learned by getting it wrong. Appendix carries the corrected reliability constant and both errors that produced 7.66. |
| [`frozen-artifact.md`](frozen-artifact.md) | **CURRENT** | The artifact every downstream number belongs to, and why each parameter has the value it has. Reliability figures corrected. |
| [`evidence-audit-2026-07-30.md`](evidence-audit-2026-07-30.md) | **CURRENT** | The evidence-to-text ledger and the `file:line` action list. Five corrections in its banner; B-12, B-13 and B-16 must not be implemented as written. |
| [`gap-analysis-final.md`](gap-analysis-final.md) | **CURRENT** | Paragraph-level gap analysis of every `.tex` in `report/`, ranked. The working list. |
| [`figures-plan-v3.md`](figures-plan-v3.md) | **CURRENT** | The authoritative figure set: 8 figures, 6 main + 2 appendix. Two corrections in its banner (six arenas -> eight; the `trace_strata` warning is already resolved). |
| [`transferable-findings.md`](transferable-findings.md) | **CURRENT** | The results that generalise beyond this system. Untouched by the arena; its finding 4 predicted the pseudo-leaf null defect. |

### Pre-registrations — append-only, never edited

| file | triage | one line |
|---|---|---|
| [`prereg_generic_judge_baseline.md`](prereg_generic_judge_baseline.md) | **CURRENT** | The C5 design, the 0.007 threshold, the disattenuation rule. Body + 6 addenda; **Addendum 4** is the mathematics confound, **Addendum 5** is the eight-run outcome table, **Addendum 6** closes the batch and records that the reported results are unregistered. |
| [`prereg_rubric_specificity.md`](prereg_rubric_specificity.md) | **CURRENT** | Rubric specificity against a random-cell null. Result: p = 1.21e-6, 0.138 vs 0.012, terms in >= 90% of rubrics 0 vs 6. Artifacts untracked. |
| [`prereg_discriminative_power.md`](prereg_discriminative_power.md) | **CURRENT** | Flat between-cell agreement across granularity. Its disattenuated column and centred-residual quartet are **withdrawn** in the 2026-07-30 addendum. |
| [`prereg_arena_launch.md`](prereg_arena_launch.md) | **CURRENT** | The cut/budget registration. Its constant-allocation warning **fired** — it predicted the mathematics confound before the run. |

### Construction and mechanism

| file | triage | one line |
|---|---|---|
| [`dag-logic-and-math.md`](dag-logic-and-math.md) | **CURRENT** | The authoritative mathematical specification of the construction pipeline as implemented. |
| [`dag-construction-mechanisms.md`](dag-construction-mechanisms.md) | **CURRENT** | Why each mechanism has its shape and the failure it answers. Includes the polyhierarchy negative result. |
| [`incremental-taxonomy.md`](incremental-taxonomy.md) | **CURRENT** | The batch artifact as the stationary limit of an incremental system. Discussion / future-work material. |
| [`router-shared-kappa-correction.md`](router-shared-kappa-correction.md) | **CURRENT** | The headline correction; why `minClusterSize` was not the binding constraint on granularity. |
| [`separation_null_by_size.md`](separation_null_by_size.md) | **STALE-BUT-FIXABLE** | Where the separation bar sits between two measured nulls. Self-labelled: the isotropic table is current, the within-node half needs re-deriving on the mcs=55 artifact. |
| [`dag-chain-formation-handoff.md`](dag-chain-formation-handoff.md) | **HISTORICAL-KEEP** | Six failed single-child-chain fixes, recorded so they are not retried. Its `ECE=1.0` diagnosis is struck. |

### Reviews and plans

| file | triage | one line |
|---|---|---|
| [`thesis-plan-v2.md`](thesis-plan-v2.md) | **STALE-BUT-FIXABLE** | Chapter architecture and corrections ledger still right. §5.0 describes one 8-model run where there are eight paired runs; §5.2.4's screen table is superseded; the roster ledger is backwards. |
| [`argument-flow-review.md`](argument-flow-review.md) | **STALE-BUT-FIXABLE** | The only reading-order review, and its placement diagnoses still hold. Line numbers predate a ~176-line move; it models a two-domain thesis. |
| [`report-quality-style-analysis.md`](report-quality-style-analysis.md) | **STALE-BUT-FIXABLE** | The de-duplication table and style list are still the right instructions. Its stub arithmetic, figure count and DAG-promotion suggestion are dead. |
| [`report-gap-analysis.md`](report-gap-analysis.md) | **HISTORICAL-KEEP** | A closed structural punch-list with its own fix log. Its routing-ECE directive is struck; do not re-apply it. |
| [`arena-math-findings.md`](arena-math-findings.md) | **HISTORICAL-KEEP** | The 8-model mathematics pilot log, with three self-retracted reversals. Sole provenance for the reliability-constant derivation. Never cite it for a screen p, a rho magnitude, or a domain recommendation. |
| [`reconciled-argument.md`](reconciled-argument.md) | **SUPERSEDED as an argument; HISTORICAL-KEEP for Parts 0-1** | Its Rung 8 conclusion is contradicted by the eight-run result. Part 0 found the routing-ECE error and verified the rubric-specificity result; Part 1 is the only code/doc/report reconciliation table. |
| [`reframed-argument.md`](reframed-argument.md) | **SUPERSEDED** | Argues for dropping `Delta rho` and for reporting a negative result. Both inverted. Only the three-link decomposition survives. |
| [`peer-review-2026-07-28.md`](peer-review-2026-07-28.md) | **SUPERSEDED on facts; HISTORICAL-KEEP for §(d) and §(e)** | Absorbed by `evidence-audit-2026-07-30.md`. Its defense questions and slop audit exist nowhere else. Its `Delta rho` signs are printed backwards. |
| [`figures-plan-v2.md`](figures-plan-v2.md) | **SUPERSEDED** | 12 figures. Replaced by v3's 8. |
| [`figures-plan.md`](figures-plan.md) | **SUPERSEDED** | 16 figures. Two supersessions behind v3. |
| [`report-visualization-plan.md`](report-visualization-plan.md) | **SUPERSEDED** | The original 16-candidate plan, on a superseded experiment (C1/C2/C3 arms, `Delta tau`, three seeds). Its §B conventions are worth salvaging. |
| [`compass_artifact_wf-...md`](compass_artifact_wf-2770ccdb-fcfa-5ac5-8cbf-d32a3b78bcc5_text_markdown.md) | **SUPERSEDED** | Externally generated, no provenance, wrong about ECE in four places, and describes gates that no longer exist. Banner added 2026-07-30. |
| [`thesis-template-guide.md`](thesis-template-guide.md) | **CURRENT** | How to build `report/` and where each chapter lives. Infrastructure, orthogonal to the results. |

### Subdirectories

**[`core-concepts/`](core-concepts/)**

| file | triage | one line |
|---|---|---|
| `taxonomy-dag.md` | **HISTORICAL-KEEP** | Banner is exemplary and already states the tree result. §1's union-based framing is still live; §2-3 describe removed machinery. |
| `data-representations.md` | **STALE-BUT-FIXABLE** | Data models accurate. `crossLinkChildren` is still described as live, and several TOML knobs no longer exist. |

**[`evolutionary-pipeline/`](evolutionary-pipeline/)**

| file | triage | one line |
|---|---|---|
| `fitting-vmf.md` | **CURRENT** | vMF/NiW numerics, kappa approximations, `d = 256`. Orthogonal to everything that changed. |
| `overview.md` | **STALE-BUT-FIXABLE** | Six-phase skeleton still accurate; its cross-linking and transitive-reduction steps are not, and the banner does not cover them. |
| `trickle-routing.md` | **HISTORICAL-KEEP** | Banner routes readers to `dag-logic-and-math.md` §4. The shared-kappa rule is the one thing still right. |
| `discovery-optimization.md` | **SUPERSEDED** | Every acceptance rule in it is dead; its banner enumerates which and why. |

**[`arena-evaluations/`](arena-evaluations/)**

| file | triage | one line |
|---|---|---|
| `bradley-terry-fit.md` | **CURRENT (corrected 2026-07-30)** | Was documenting the `1/K` variance bug as spec. Corrected to `1/K^2`, with the no-confidence-interval rule banner. |
| `judge-design.md` | **STALE-BUT-FIXABLE** | Pairwise judging and contrastive rubric synthesis. Its expert-trace passage reads as if the gold trace is supplied at judging time; it is not. |
| `active-matchmaking.md` | **STALE-BUT-FIXABLE** | Entropy scheduling and KDE valley detection. Its claimed 10% budget saving came from cross-links, which are gone. |

**[`metrics-validation/`](metrics-validation/)**

| file | triage | one line |
|---|---|---|
| `structural-metrics.md` | **STALE-BUT-FIXABLE (§1 superseded)** | §1's AvgMatch is now an invariant check at 1.0; its "observed 1.1-1.3" claim is dead. §2-3 stand. |
| `clustering-metrics.md` | **STALE-BUT-FIXABLE** | Spherical silhouette, overlap-tolerant NMI, Dasgupta. The overlap the NMI variant tolerates cannot occur in a tree. |
| `classification-metrics.md` | **STALE-BUT-FIXABLE** | Hierarchical F1 and EMAR. One cross-link clause corrected. |
| `TaxoArena_Parameter_Guide.md` | **SUPERSEDED** | For parameter values and derivations. Current table: `dag-logic-and-math.md` §10; current derivations: `frozen-artifact.md`. |

**[`system-architecture/`](system-architecture/)**

| file | triage | one line |
|---|---|---|
| `spring-integration.md` | **CURRENT** | DI topology, coroutine execution, scheduling. |
| `database-concurrency.md` | **CURRENT** | SQLite WAL configuration, schema, write-collision synchronisation. |
| `tui-dashboard.md` | **CURRENT** | TUI panel layout and hotkeys. |
| `headless-experimentation.md` | **STALE-BUT-FIXABLE** | The CLI is accurate. Its "4-condition matrix" lists five rows and predates the paired MAIN-vs-C5 design. |

**[`paper/`](paper/)**

| file | triage | one line |
|---|---|---|
| `EVALUATION_METRICS.md` | **STALE-BUT-FIXABLE** | Metric-to-table status index. Routing ECE inverted 2026-07-30 from "never measured" to measured-with-defect. |
| `EMPIRICAL_PLAN.md` | **STALE-BUT-FIXABLE** | Experiment matrix. Same ECE inversion applied; its three-seed mandate contradicts its own single-seed amendment. |
| `MATHEMATICAL_FOUNDATIONS.md` | **STALE-BUT-FIXABLE** | vMF/NiW basis. Its reliability table rests on a 165-leaf distribution; the frozen artifact has 87. It also asks for confidence intervals. |
| `PUBLICATION_HYGIENE.md` | **STALE-BUT-FIXABLE** | Citation, licensing, ethics, limitations. Its limitations list omits all four of the project's named corrections. |
| `REPRODUCIBILITY.md` | **STALE-BUT-FIXABLE** | Artifact checklist. Marks seeds as clean; the multi-seed routing defect says otherwise. |

**[`guides/`](guides/)**

| file | triage | one line |
|---|---|---|
| `eval-results-zip-schema.md` | **CURRENT** | On-disk schema for the precomputed MMLU-Pro eval files the arena replays. |
| `thesis-reproduction.md` | **STALE-BUT-FIXABLE** | End-to-end protocol; banner is strong. ECE bullet inverted and the no-interval rule added 2026-07-30. |

**[`data/`](data/)** — `within_node_null_splits.csv`, `within_node_null_leaves.csv`.
**CURRENT as artifacts**, computed on the pre-`c381211` tree: the method survives, the values
need re-deriving.

**[`archive/`](archive/)** — history only. Not authoritative under any circumstances.

---

## What changed in this pass (2026-07-31)

* **The M = 12 batch stopped being the results.** Its bootstrap starved every cell but one
  in every domain, and three of its runs had unequal arms. Five domains were re-run under a
  revised scheduler and stopping rule; those are the results.
  `newlogic-rerun-record.md` was rewritten to hold them — it previously covered three
  domains and opened with "Every domain moved", which is false (philosophy held at +14.00
  exactly). `batch-M12-complete-record.md` was reframed as superseded, with the per-cell
  defect recorded as caveat 7 and its one per-cell claim withdrawn. No number in it changed.
* **Answer-key agreement under the revised scheduler was computed for the first time.**
  Mathematics is the only gap in either batch that clears its own noise, and it favours C5.
  The philosophy dissociation survives in sign only: the gap falls from 1.3 points to 0.3.
* **Addendum 6** was appended to `prereg_generic_judge_baseline.md`, closing computer
  science and the mathematics re-run against their registrations and recording that the
  reported batch is unregistered. No registered text was edited.
* `stale-results-audit.md` was reframed: its `file:line` inventory stands, its instruction
  inverted.

## What changed in the previous pass (2026-07-30)

* `known-defects.md` — the routing-ECE entry was **false**. It is measured, exported at
  0.2114; the defect is `maxOf` leaf-share aggregation at
  `HeadlessBenchmarkRunner.kt:884-885` and `BatchTrickleEvaluator.kt:195-196`.
* `measurement-discipline.md` — the reliability constant was published as 7.66 and is 3.04x
  too large. Corrected to `c = 2.52`, with both errors derived and the refit reproduced.
* `void-results.md` — grew two sections. It was the designated quarantine list and was
  quarantining none of the 2026-07-28 to 07-30 defects.
* `arena-evaluations/bradley-terry-fit.md` — was documenting the `1/K` variance bug as the
  specification.
* Four pre-registrations received dated addenda. No prior text was edited.
* Eleven documents received status banners naming what in them is still true.

---

## Codebase quick reference

**Construction** — `TaxonomyEngine` (lifecycle), `TaxonomyFitter` (vMF fitting, shrinkage),
`TaxonomyTrickler` (descent gate, shared-kappa sibling competition), `TaxonomySplitter`
(PCA + vMF k-means proposal, separation bar), `TaxonomyOperations` (`tryProposal`, the
z-gate, the k-fallback loop, the proposal memo), `TaxonomyMerger` (fusion, dissolution),
`TaxonomyStabilizer` (convergence).

**Arena** — `TaxonomyBenchmarkService`, `TaxonomyRankingService`, `BtMatchScheduler`,
`BtStoppingPolicy`, `BtMmFitter`, `HeadlessBenchmarkRunner`.

**Statistics** — `StatisticsUtils` (vMF, log-Bessel ratios, chance-corrected separation,
PCA), `JBootstrap` (paired `SE(dJ)`), `TaxonomyMetrics`, `AdditionalMetrics`
(`computeRoutingECE`).

**Analysis scripts** — `tools/analysis/reliability_constant.py` (the `c` refit),
`leaf_substructure_null.py` (the corrected permutation null),
`rubric_specificity_null.py`, `domain_reorder_screen.py`, `discriminative_flatness.py`,
`tie_policy_sweep.py`.

**Configuration** — `experiment_configs/freeze_mcs55.toml` is the frozen artifact. Its
header is a provenance record: rewrite it when deriving, do not `sed` it.
