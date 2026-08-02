# Results — the settled batch

Every number the thesis reports comes from one run generation: the **8-domain, 8-model
RESOLVED batch** of 2026-07-31 (`experiment_results/r8/`, snapshot
`20260727_042523_Headless_Run_Auto_ge`, seed 42). Two earlier generations — the Run-A
pilot and the 12-model paired campaign — are withdrawn (broken scheduler coverage,
collinear formats) and contribute no numbers; their record is the registration appendix
of the thesis (Appendix A) and `archive/docs/`. Chapter 5 of the thesis carries every
qualification; this file is the list.

## Run record

- 8 domains (math, physics, law, engineering, psychology, philosophy, history, cs),
  8 models, both arms (MAIN per-leaf rubric vs C5 generic MT-Bench) replaying the same
  comparisons; 1,637 reserved questions routed, 52 cells with arena activity,
  5,161 logical comparisons per arm; zero crashes, zero rate-limit failures.
- Roster (ground-truth accuracy spread 16.5%–90.5%, factor 5.5, chosen to buy key
  decidability): gemini-3.1-pro_5-shots, arx_0314, gpt-4o-2024-08-06,
  Meta-Llama-3_1-70B-Instruct, Qwen1.5-72B-Chat, Meta-Llama-3_1-8B, Yi-6b-Chat,
  Llama-2-7b-hf. Not length-matched (median output 220–1,494 chars); arx_0314 is 21.4%
  bare-answer; the gemini entry is a 5-shot condition.
- `verify_agree_philosophy/` is a ninth run only to verify the agreement-export patch:
  exported 0.7520 == independent recomputation.

## RQ1 — what the judge's verdict tracks

The verdict is produced **jointly by answer verification and a competence prior**:

- **Key recovery**: 196/200 key-decidable pairs (98.0%); agreement with the key on
  86.0% of decidable comparisons where the judge commits.
- **One ordering, eight times**: seven of eight domains share an identical ground-truth
  ordering (law differs by one adjacent swap of two near-tied models), so this is one
  ordering recovered on eight disjoint question samples, not eight independent results.
- **Tie signature**: tie rate 13.0% on key-decidable vs 24.0% on key-undecidable
  comparisons, in all eight domains. Decomposition: both-correct 28.7% vs both-wrong
  20.8% tie rate.
- **Competence split (the boundary of verification)**: agreement is 91.1% when the
  correct model is the pair's stronger (n = 2,208) but 56.5% when it is the pair's
  weaker (n = 382). An always-pick-the-pair-stronger baseline scores 83.5% by itself.
- **Off-subject control**: off-subject questions are judged at on-subject agreement
  rates (27 cells, permutation p = 1.0) — the rubric's domain criteria are not what
  decides.
- Mechanism: responses state their own selected answer (97.6% of traces, range
  93.2–99.8%), so a judge able to solve the item verifies both sides without the key.

## RQ2 — what the cell rubric changes

- **Same ranking**: MAIN and C5 produce the same domain ordering in 7/8 domains, one
  adjacent transposition in the eighth — within the measured seed-to-seed spread.
- **Different decisiveness**: MAIN abstains on 13.0% of decidable comparisons vs 10.9%
  for C5, in all eight domains. Unconditional agreement 74.8% vs 77.7%; conditional on
  committing 86.0% vs 87.2% (both-committed disagreements split 11 vs 26, sign test
  p = 0.020; no single domain significant).
- Attribution is to the **arm bundle** (prompt + template + output format + fixed
  confidence), not the rubric text alone. Replay overlap 100% in four domains, 99.6% in
  law and engineering.

## Construction and the three links

- **Link 1 (construction)**: certified fixed point at iteration 10; 87 leaves, median
  size 88; acceptance gate measured stability-neutral and J-neutral.
- **Link 2 (rubric specificity)**: positive. Induced rubrics are cell-specific against
  13 size-matched random cells, p = 1.21 × 10⁻⁶, all four pre-registered discriminators
  in their predicted directions (lexical measure only).
- **Link 3 (evaluative sub-structure)**: premise refused under pre-registration, before
  the arena ran. Between-cell rank agreement is flat across an elevenfold granularity
  change; the overlap-matched permutation null is exceptionless at the settled roster —
  no domain and 0 of 293 leaf pairs survive correction (min p = 0.122). The three
  mathematics pairs that once passed belonged to the superseded 12-model roster.

## Offline analyses (8-model refits)

- **Screen saturation**: the cheap accuracy screen reproduces the arena ordering at
  ρ = 1.000 in 12 of 14 domain/router combinations (law 0.994 p = 0.003, chemistry
  0.976 p < 0.001) — at this roster spread the screen is already sufficient.
- **Ceilings**: law per-leaf ceilings 0.929–1.000 vs split-half reliability
  0.922–1.000; minimum aggregate accuracy gap between adjacent models 7.9 pp.
- **Budget**: identification (which model is better overall) needs 7–10 comparisons per
  cell (median 7, the spanning-tree floor). Resolution (per-cell rankings) would need
  ~143 comparisons per pair; the batch achieves 1.6–5.1.
- **Routing**: 77.8% on-subject; cell over-sampling 28.6–30.9% vs 25% uniform.

## Where the artifacts are

| artifact | path |
|---|---|
| per-domain ratings + exports | `experiment_results/r8/<domain>/` (see its README) |
| frozen taxonomy | `snapshots_frozen.db` (committed extract), snapshot `20260727_042523_Headless_Run_Auto_ge` |
| rubric-null artifacts | `experiment_results/rubric_null/` (committed) |
| frozen MAIN comparison triples | `frozen_triples_20260727_042523_Headless_Run_Auto_ge_MAIN.json` |
| run configs | `experiment_configs/r8_*.toml`, `verify_agree.toml`, `freeze_mcs55.toml` |
| construction/freeze record | `experiment_results/freeze_mcs55/`, `canonical_freeze/` |
| pre-registrations | `docs/prereg_*.md`; outcomes in thesis Appendix A |
| figures (generated from these artifacts) | `report/Figures/make_*.py` |

## Standing caveats

Selected domains (8 of 14), one seed, one judge model; no confidence intervals anywhere
(known-wrong variance correction); the roster is not length-matched; all results sit on
the middle rung of the options-mode ladder (responses state their own answers) — the
registered options-blind arm is future work, blocked on a trace-complete roster.
