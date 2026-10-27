# tools/

Python tools around the Kotlin engine, plus a few shell and PowerShell scripts: readouts, guards, ingest and run chains.

| path | contents |
|---|---|
| `analysis/` | the registered readout scripts and the shared guards and helpers listed below |
| `ingest/` | ingest of external corpora: Open LLM Leaderboard details, BFCL, Multi-SWE-bench, JudgeBench, the intent-transfer corpora, 20 Newsgroups, and the multi-corpus database |
| `chains/` | shell and PowerShell chains that sequence runs (anchor-free certification and re-draw, k selection, topic partition, sweeps, the split-function check) |
| `ops/` | a WAL checkpoint tool for one allow-listed cache at a time, and its mutant tests |
| `threadcap/` | the site-null legs of the THREAD-CAP test |
| `tuning/` | the L9 tuning harness (see its own README) |
| `figures/` | a radial figure of an adaptive-bar tree, and its plan |
| `ollama_affinity.ps1` | sets the CPU affinity of the Ollama server for THREAD-CAP |

<!-- src: file names and docstrings: ingest/leaderboard_details.py L1, ingest/intent_ingest.py L1, the other ingest
file names; chains/ file names; ops/wal_checkpoint.py L1; threadcap/ file names (sitenull_*_leg.sh);
tuning/README.md L1; figures/fig_adaptive_tree.py L1; ollama_affinity.ps1 L1-L3 -->

## Shared guards and helpers in `analysis/`

| script | role |
|---|---|
| `pool_guard.py` | verifies a pool by id (`--pool <id>`) before any reader; refuses on a non-empty `-wal` or `-journal` |
| `ledger_patch.py` | the only way the ledger is edited (`insert_outcome`, `add_row_before`, `replace_chip`, `stamp`, `audit`, `write`) |
| `results_index.py` | regenerates `docs/agents/results/INDEX.md` |
| `split_side.py` | the split side of an item, the Python half of a two-language function; `stem_key` is the CK-CLOSE-v1 content key |
| `accepted_tests_ledger.py` | the call accounting guard: per-test ceilings, the 4,000-match rule and the day cap, checked before every posting launch |
| `systematic_budget.py` | includes `mcnemar_edge`, the exact McNemar count behind wrong(established) |
| `scratch_dir.py` | puts temporary files under a scratch base outside the repository and removes them at exit |

<!-- src: KNOWLEDGE.md section 0 (reuse list), section 1 (pool_guard refusal; CK-CLOSE-v1 key = split_side.stem_key;
ledger_patch.py functions), section 1 ledger conventions (wrong(established) by systematic_budget.mcnemar_edge),
section 4 (INDEX.md via results_index.py); split_side.py L1-L4; accepted_tests_ledger.py L1-L14; scratch_dir.py L1-L16 -->

## Rules

- A registered script is pinned by its blob at its READY review; the record's `script` field names the pin. A changed script passes a delta READY before it runs again.
- By convention a script's docstring states its registration, launch sequence, cache and guard. `--dry-run` posts nothing, the first printed line is the pool id, outcome files are written only from complete caches, and pilots write `*_PILOT.txt`.
- Code that deletes, moves or overwrites files is self-tested and mutated only inside a sandbox; on real paths it runs as a dry run only.
- Scripts that other scripts pin by blob are not edited to import `scratch_dir.py`; they run under it as `python tools/analysis/scratch_dir.py --run -- python tools/analysis/<script>.py --selftest`.

<!-- src: KNOWLEDGE.md section 2 standard flow (READY mandatory before any pilot); e.g. CERT-RESOLUTION.json and
HARNESS-EXTRACTOR.json script / brackets (blob pins; "READY delta 4 (eba84716) ... merged by path"); prog L20834
_as_of 70c61579 ("pinned at the READY"); CONTEXT.md section 6 (script conventions); KNOWLEDGE.md "Temp files and
destructive code (2026-10-04)" (sandbox rule; wrapper command); scratch_dir.py L22-L24 -->
