# TaxoArena documentation index

The documents under `docs/` are listed below by section. <!-- A2 (D-2026-10-27-6): the record goes into the public copy as it is; docs/drafts/ stays out and is not listed. The drafted registrations docs/registrations/*_DRAFT.md are not listed (A9 default: no). -->
Sections 1 to 3 are the record and govern; the rest is design, history or a digest.
Where a digest disagrees with the record, the record wins.

## 0. Older documents

r8 and the p2dca judged family are history, never evidence (judge_v2_program.md L21449, _as_of 70c61579).
Documents written for the r8-era system carry a HISTORY banner on their first line; the thesis sources in `report/` are author-owned.

## 1. Start here

| file | contents |
|---|---|
| [agents/KNOWLEDGE.md](agents/KNOWLEDGE.md) | digest of pins, split words and standing rules, with pointers into the record |
| [agents/plans/2026-09-26_framing_of_record.md](agents/plans/2026-09-26_framing_of_record.md) | the framing of record, "Cell-conditional evaluation" (adopted 2026-09-27) |
| [agents/plans/2026-09-27_research_plan_rev2.md](agents/plans/2026-09-27_research_plan_rev2.md) | the research plan, revision 2; its section A1 governs where it differs from the framing |
| [agents/CONTEXT.md](agents/CONTEXT.md) | binding text of the standing rules (section 4) and the closed lines (section 5) |

## 2. The record

| file | contents |
|---|---|
| [judge_v2_program.md](judge_v2_program.md) | the programme: registrations, outcomes, rulings and author decisions, appended in order (grep it) |
| [test_ledger.html](test_ledger.html) | the ledger, one row per test; edited only through `tools/analysis/ledger_patch.py` |
| [test_ledger_distilled.html](test_ledger_distilled.html) | a curated view at ledger v110 (2026-09-17); later brackets in the full ledger win |
| [agents/results/INDEX.md](agents/results/INDEX.md) | one JSON record per experiment, and their index |
| [agents/queue.md](agents/queue.md) | a readable view of `agents/queue.json`, the queue of record |
| [agents/author_decisions/](agents/author_decisions/) | the author's decisions, by date |
| [plan_2026-09-15.md](plan_2026-09-15.md) | the execution plan and its numbered amendments |
| [agents/plans/](agents/plans/), [agents/leads/](agents/leads/) | dated plans, schedules and lead notes behind the record |

## 3. Reviews and rulings

| file | contents |
|---|---|
| [reviews/](reviews/) | READY reviews before a run, POSTRUN reviews after it, rulings and dated reviews |
| [reviews/RULING_w0_p2dca_family.md](reviews/RULING_w0_p2dca_family.md) | the [P-FAM] ruling: which judged readouts are history |

## 4. Design

| file | contents |
|---|---|
| [design/FRAMEWORK.md](design/FRAMEWORK.md) | the design of record; read its dated brackets |
| [design/RESOLVE.md](design/RESOLVE.md), [RESOLVE_budget.md](design/RESOLVE_budget.md), [RESOLVE_stress_operations.md](design/RESOLVE_stress_operations.md), [RESOLVE_stress_statistics.md](design/RESOLVE_stress_statistics.md) | RESOLVE, a design (v1) for a standing capability service, with its budget and stress reviews; design history, not maintained |
| [multi_corpus_design.md](multi_corpus_design.md), [v2_construction_proposals.md](v2_construction_proposals.md), [v2_validation_plan.md](v2_validation_plan.md), [rubric_v2_design.md](rubric_v2_design.md) | earlier design documents; not maintained |

## 5. Literature notes

[literature/](literature/): dated literature scans and method reviews (related work, tree uses, structure tests, hierarchy evaluation, testing logic).

## 6. Figures and data

| file | contents |
|---|---|
| [figures/](figures/) | figures made from record values by `tools/analysis/make_thesis_figures.py`; each caption names its record ids, and where a caption and a later record bracket differ the record wins (fig1's caption labels AF-U [LF]; the record reads [SC]) |
| [separation_null_by_size.md](separation_null_by_size.md), [data/](data/) | the within-domain separation-null calibration; its constants live in `TaxonomySplitter` |

## 7. Campaign history: [P-FAM] history ([docs/reviews/RULING_w0_p2dca_family.md](reviews/RULING_w0_p2dca_family.md))

| file | contents |
|---|---|
| [incident_reserved_pool_mismatch_2026-09-09.md](incident_reserved_pool_mismatch_2026-09-09.md) | the incident of 2026-09-09: the arena judged a pool that was not the frozen tree's reserved split (p8a29d8f3ff75aa55) |
| [campaign_review_2026-09-10.md](campaign_review_2026-09-10.md), [perf_review_2026-09-09.md](perf_review_2026-09-09.md), [review_session_2026-09-14.md](review_session_2026-09-14.md) | dated campaign, performance and session reviews |
| [judge_improvement_proposals.md](judge_improvement_proposals.md), [f_series_free_tests.md](f_series_free_tests.md), [m_series_registration.md](m_series_registration.md), [s_l_series_registration.md](s_l_series_registration.md) | early test series and proposals (J, F, M, S / L) of 2026-09-08 and 2026-09-09 |

## 8. r8-era documents

| file | contents |
|---|---|
| [IMPLEMENTATION.md](IMPLEMENTATION.md), [RESULTS.md](RESULTS.md) | the system as built and the batch as reported in the r8 era (bannered) |
| `prereg_*.md` | four r8-era pre-registrations, preserved unedited |
| [test_catalogue.md](test_catalogue.md) | plain-language entries copied from the records' descriptions on 2026-10-07; counts not maintained |

## 9. Replication (as of 2026-08-02) and running

As of 2026-08-02, results checking for the r8-era thesis needed the repository alone, and every `report/Figures/make_*.py` asserted its numbers before drawing; construction replication from the two local caches was verified that day:

```
sha256(mmlu_pro_dataset_cache_v2.db) = 9e3328ec4707a44303b2f3e6484face237e86ef13f0986693b670c4e6bd5b8e5
sha256(embeddings_cache.db)          = a416980286a3a0a5065b58e9c661cd0a2898ccb902ca62b9d6f0415ebe6f8891
```

These whole-file hashes are not pins: later builds and checkpoints have changed both files.
A construction writes to both caches by design, so back them up before any construction.

Arena and construction runs go through `./gradlew bootRun --args="--config experiment_configs/<run>.toml"`.
Never pass a `seeds = [...]` list: only the first seed routes the reserved queries, so run one config per seed.
The thesis builds with `cd report && arara main.tex`; regenerate the nomenclature manually only if its entries change.

<!-- Repo tidy, D-2026-10-27-1. The two sha256 lines above must stay at L81-L82:
docs/reviews/2026-09-20_cache_writes_by_construction.md L65 ("docs/README.md:81-82") and L120 ("README L81-82
style") cite them there. Programme ("prog") spans are _as_of 70c61579. -->
<!-- Sources, by section:
intro: docs/agents/KNOWLEDGE.md L7-L8 (the record wins over a digest).
0: prog L21449; banners added in this commit on IMPLEMENTATION.md, RESULTS.md, experiment_results/r8/README.md;
   KNOWLEDGE.md section 2 (report/ author-owned).
1: prog L21435-L21445 (framing adopted 2026-09-27; "the PLAN's A1 governs"); CONTEXT.md sections 4, 5 headings.
2: KNOWLEDGE.md section 4 table and section 1 ledger conventions (ledger_patch.py only; queue.json of record,
   queue.md view; INDEX.md); test_ledger_distilled.html L60-L61 (v110, record at 2026-09-17).
3: KNOWLEDGE.md section 4 (READY_*, POSTRUN_*, RULING_*); prog L21459-L21504 (the [P-FAM] ruling).
4: KNOWLEDGE.md section 4 ("design of record ... check the brackets"); headings of the listed files.
5: headings of docs/literature/*.md.
6: docs/figures/fig1_sq1_routing_gain.caption.txt L5, L23 (record ids; make_thesis_figures.py); docs/README.md
   L25-L27 _as_of 70c61579 (separation_null_by_size.md + data/; constants in TaxonomySplitter).
7: A8 default (D-2026-10-27-6), the [P-FAM] history label, no number quoted; incident doc L1-L5 (reserved pool
   p8a29d8f3ff75aa55); headings of the listed files (incident 2026-09-09; J-series 2026-09-08; F-series registered 2026-09-08;
   M-series registered 2026-09-09; S1 / L1 registered 2026-09-09).
8: IMPLEMENTATION.md L3 and RESULTS.md L3-L4 (r8-era state); docs/README.md L23-L24 _as_of 70c61579 (four
   pre-registration documents, preserved unedited); test_catalogue.md L3 (copied 2026-10-07).
9: docs/README.md L68-L83 _as_of 70c61579 (the replication block, verbatim hashes; the false sentence of its L66
   about config/application.yml is dropped: the file is tracked); review 2026-09-20 L117 (STALE bracket: tables
   grew, WAL checkpointed) and L120 ("is NOT a pin: it moves on every build and on every checkpoint"); review
   2026-09-20 L7 (construction writes both caches); KNOWLEDGE.md section 2 rule 7 (back up before any construction);
   docs/README.md L50, L55-L56, L61-L64 _as_of 70c61579 (bootRun --config; seeds rule; arara and nomenclature);
   CONTEXT.md section 4 rule 6 (never seeds = [...]). -->
