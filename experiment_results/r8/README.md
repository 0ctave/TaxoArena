# r8 — the settled 8-domain, 8-model batch (thesis evidence base)

All runs in this folder are the final batch cited by the thesis: 8 models x 8 MMLU-Pro
domains, paired MAIN (leaf-rubric judge) vs C5 (generic MT-Bench judge), RESOLVED mode,
seed 42, all against the frozen taxonomy snapshot
`20260727_042523_Headless_Run_Auto_ge` (in root `snapshots.db`).

Each domain folder contains the run's own Bradley-Terry ratings store
(`ratings_r8_<domain>.db`, tables `match_history`, `ratings`) next to its CSV/JSON
exports (`seed_42/` with `manifest.json`, `judging/`, `validation/`, `diagnostics/`).
All runs executed on 2026-07-31; configs are in `experiment_configs/`.

| folder | config | run start (UTC) | logical comparisons (per arm) |
|---|---|---|---|
| `math/` | `r8_math.toml` | 12:46 | 1030 |
| `physics/` | `r8_physics.toml` | 13:04 | 455 |
| `law/` | `r8_law.toml` | 13:52 | 811 |
| `engineering/` | `r8_engineering.toml` | 14:08 | 283 |
| `psychology/` | `r8_psychology.toml` | 15:08 | 1130 |
| `philosophy/` | `r8_philosophy.toml` | 15:32 | 431 |
| `history/` | `r8_history.toml` | 15:53 | 495 |
| `cs/` | `r8_cs.toml` | 16:16 | 526 |
| `verify_agree_philosophy/` | `verify_agree.toml` | 17:04 | 434 |

`verify_agree_philosophy/` is not a ninth domain: it re-runs philosophy after the
judge-agreement export fix to verify the recorded agreement rate, and is kept beside
the batch it validates. Its ratings store is `ratings_verify_agree.db`.

The 8-model roster (identical in every run): gemini-3.1-pro_5-shots, arx_0314,
gpt-4o-2024-08-06, Meta-Llama-3_1-70B-Instruct, Qwen1.5-72B-Chat, Meta-Llama-3_1-8B,
Yi-6b-Chat, Llama-2-7b-hf — the maximal-separation 8-subset of the candidate pool
(see the config headers for the selection rationale).

Note for reproducers: the `r8_*.toml` configs write fresh exports to
`experiment_results/r8_<domain>/` (the pre-cleanup layout) and a fresh
`ratings_r8_<domain>.db` at the repository root; they will not overwrite this folder.
`report/Figures/make_routing_provenance.py` and `make_rubric_reach.py` read the
databases from this folder's layout.
