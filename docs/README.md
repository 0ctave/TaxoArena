# TaxoArena documentation

TaxoArena induces a semantic **tree** over MMLU-Pro questions from their embeddings, writes
a judging rubric for every terminal cell, and runs an LLM-as-a-judge pairwise arena inside
those cells. The partition is the instrument; the thesis result is a measurement of the
judge. The full account is the thesis in `report/`; these docs are the repository-level
summary.

> The system is a tree, not a DAG. Cross-linking was removed and polyhierarchy is reported
> as a negative result. Where "DAG" survives in file or symbol names (`DagMode`,
> `computeDagSeparationJ`), read it as "the induced hierarchy".

## The three documents

| file | contents |
|---|---|
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | The system as built: data and id-spaces, tree construction, routing, rubric generation, the arena, and the known defects that bound what its outputs may claim. |
| [RESULTS.md](RESULTS.md) | The settled results: the 8-domain / 8-model RESOLVED batch every thesis number comes from, with the offline analyses and pointers to the raw artifacts. |
| this file | Orientation and how to run things. |

Also kept, because code and analyses reference them by path:

- `prereg_*.md` — the four pre-registration documents (registered text, preserved
  unedited; their outcomes are recorded in the thesis, Appendix A).
- `separation_null_by_size.md` + `data/` — the within-domain separation-null calibration
  whose tabulated constants live in `TaxonomySplitter`; the CSVs are written by
  `SeparationNullBySizeTest`.

Everything else that used to live here (working notes, superseded run records, review
reports, legacy architecture docs) is on disk under `archive/docs/`, untracked and
documented in `archive/ARCHIVE_MANIFEST.md`.

## Where things are

- `experiment_results/r8/` — the settled batch: per-domain ratings databases and exports,
  with its own README describing the layout.
- `experiment_configs/` — the run configs; `r8_*.toml` are the settled batch,
  `freeze_mcs55.toml` built the frozen taxonomy.
- `snapshots_frozen.db` (committed, 16 MB) — the frozen taxonomy snapshot the settled
  batch uses (`20260727_042523_Headless_Run_Auto_ge`, 154 nodes, 87 leaves, max depth 6)
  plus the two granularity-analysis snapshots. The full local `snapshots.db` is not in
  git; every script that reads it falls back to the extract automatically.
- `report/` — the LaTeX thesis.

## Running

**Arena / construction runs** go through the headless runner:

```bash
./gradlew bootRun --args="--config experiment_configs/r8_math.toml"
```

Judge and labeling calls need the `AZURE_AI_*` variables from `.env` in the environment —
without them a run completes with endpoint errors on every call and produces a void
result. Never pass a `seeds = [...]` list: only the first seed routes held-out queries;
run one config per seed.

**Tests**: `./gradlew test` (~30 s). The slow calibration harnesses are split out into
`./gradlew calibration`.

**The thesis**: `cd report && arara main.tex`. Plain `pdflatex` silently skips the
nomenclature step. If nomenclature *entries* change, regenerate manually first:
`makeindex -s "$(kpsewhich nomencl.ist)" -o main.nls main.nlo` (arara's makeindex
directive ignores its options and processes `main.idx` instead).

`config/application.yml` carries local credentials and is never committed.

## Replication from a clean clone

Results checking needs the repository alone: the settled batch's record
(`experiment_results/r8/`), the frozen snapshot extract (`snapshots_frozen.db`), the
rubric-null artifacts (`experiment_results/rubric_null/`), and the analysis inputs
(`reserved_leaf_assignments.csv`, `model_domain_scores.csv`,
`*_secured/MAIN_thesis_metrics.csv`, `docs/data/`) are all committed, and every
`report/Figures/make_*.py` script asserts its published numbers before drawing.
Scripts that read per-question ground truth, and any re-run of construction or the
arena, additionally need the two local caches (not in git; construction replication
from them verified 2026-08-02):

```
sha256(mmlu_pro_dataset_cache_v2.db) = 9e3328ec4707a44303b2f3e6484face237e86ef13f0986693b670c4e6bd5b8e5
sha256(embeddings_cache.db)          = a416980286a3a0a5065b58e9c661cd0a2898ccb902ca62b9d6f0415ebe6f8891
```
