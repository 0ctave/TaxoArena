# experiment_configs/

Run configurations (TOML) and the pins of the reserved pools.
Configs are fail-closed: an unknown key or an unknown value is fatal.
By convention a config's header comment names its registration, and a test's JSON record in [docs/agents/results/](../docs/agents/results/INDEX.md) names the config it ran.
Most subdirectories are named after the test or programme item that ran them.
<!-- src: CONTEXT.md section 6 ("Configs: TOML, fail-closed (unknown keys and unknown values are fatal); one knob per
arm; header comment states the registration"); e.g. UNION-AF-ROUTE.json script.path (experiment_configs/union_af_route/) -->

Never use a `seeds = [...]` list: only the first seed routes the reserved queries, so run one config per seed.
<!-- src: CONTEXT.md section 4 rule 6; docs/README.md L55-L56 _as_of 70c61579 -->

## Pool pins

| file | pool | split word |
|---|---|---|
| `reserved_pools.json` | the registry that `tools/analysis/pool_guard.py` and the engine's `ReservedPoolRegistry` read | n/a |
| `reserved_pool_frozen_p2dca.json` | p2dca21ab5f4ef3ae: MMLU-Pro, 3,445 judgeable questions; the split of bareq512_s42 | id-disjoint only |
| `reserved_pool_frozen_paeec.json` | paeec37aa28063c75: six-corpus union (MMLU_PRO_LB, BBH, MATH, MUSR, IFEVAL, GPQA), 6,482 judgeable questions | id-disjoint only |
| `engine_pool_pv2_41dbd3dbcd399df0.json` | pv2_41dbd3dbcd399df0: v2 split draw 5a3e756, MMLU-Pro, 3,492 EVAL items in 3,400 components (the record's count; the pin's `counts.eval` reads 3,586) | content-closed under CK-CLOSE-v2, residual disclosed |
| `engine_pool_pv2_1575de61bb20e977.json` | pv2_1575de61bb20e977: v2 split draw 5a3e756, all corpora, 6,153 EVAL items in 5,642 components (the record's count; the pin's `counts.eval` reads 6,466) | content-closed under CK-CLOSE-v2, residual disclosed |
| `reserved_pool_frozen_bfcl_p2035adddedd1becb.json` | p2035adddedd1becb: BFCL EVAL side, 228 ids | not stated here; read the record AGENT-CORPUS-ADMISSION before quoting one |
| `reserved_pool_frozen_multiswe_p79fb71114b5c67c2.json` | p79fb71114b5c67c2: Multi-SWE-bench EVAL export, 390 ids | not stated here; read the record MULTI-SWE-ADMISSION before quoting one |

Verify a pool with `python tools/analysis/pool_guard.py --pool <id>`.
Nothing is "activated".
A refusal on a non-empty `-wal` or `-journal` file is a failed precondition, never an outcome.
<!-- src: reserved_pools.json L2 (_comment: read by pool_guard.py and ReservedPoolRegistry), L4-L31 (pool ids,
corpus sets, judgeable 3445 / 6482, id files); KNOWLEDGE.md section 1 (split words: p2dca id-disjoint only, bareq512_s42's
split; paeec id-disjoint only; v2 draw 5a3e756 pools pv2_41dbd3dbcd399df0 3,492 EVAL items and pv2_1575de61bb20e977
6,153, content-closed under CK-CLOSE-v2 with the residual disclosed; pool_guard and its refusal); engine_pool_*.json
"pool_id" and "counts.eval" fields (3586 / 6466); prog L16198 _as_of 70c61579 ("POOLS OF RECORD pv2_1575de61bb20e977
(... 5,642 components / 6,153 items) and pv2_41dbd3dbcd399df0 (... 3,400 components / 3,492 items)"; REVIEW_REPO-TIDY E11:
not "key-complete", prog L21881 has 3,351 / 3,350 key-complete OF 3,492); AGENT-CORPUS-ADMISSION.json run.pool (p2035adddedd1becb, BFCL EVAL side, 228 ids);
MULTI-SWE-ADMISSION.json run.pool (p79fb71114b5c67c2, this run's own EVAL export, 16 keys / 390 ids). No split word of record was found for the two agent-corpus pins, so none
is written. -->

## Trees

- `promoted/bareq512_s42.toml` configures the tree of record bareq512_s42 (snapshot 20260909_212117, 87 leaves, R512). Its split is id-disjoint only. It is not a certified fixed point: its certificate reads CERTIFIED false at iteration 18.
- `promoted/abt2d512_s42.toml` configures a second tree built on the same pool (47 leaves).
- `freeze_mcs55.toml` built the frozen tree 20260727_042523, which is geometry only.

<!-- src: KNOWLEDGE.md section 1 (Trees: bareq512_s42 = snapshot 20260909_212117, 87 leaves, R512, id-disjoint only,
config experiment_configs/promoted/bareq512_s42.toml, NOT a certified fixed point, CERTIFIED false at iteration 18;
frozen 20260727_042523 geometry-only); prog L20817-L20844 _as_of 70c61579; ledger row PROMOTED (abt2d512_s42: 47
leaves, rebuilt on the pool of record p2dca); docs/README.md L37-L38 _as_of 70c61579 (freeze_mcs55.toml built the
frozen taxonomy) -->

## History

- `r8_*.toml` configure the r8 batch: history, never evidence.
- `x8_*.toml` and `x12_*.toml` configure the x8 and x12 runs of the first iteration. Judged readouts of those runs are in the p2dca judged family: history, not evidence.

<!-- src: docs/README.md L37-L38 _as_of 70c61579 ("r8_*.toml are the settled batch"); prog L21449 _as_of 70c61579;
prog L21476 _as_of 70c61579 (ruling membership (a): "The r8-era runs (x8, x12 v1, R2, the rubric line, the
J-series) are in, and so is the post-incident STACK-v2 work (R3, ARENA-V2 x12 and x20, ...)") -->
