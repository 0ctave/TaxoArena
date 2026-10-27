# READY review: E1-REPLICATES build (branch e1-replicates, ee68eed7) — NOT READY (B-1)

Reviewer: adversarial-reviewer, 2026-10-02, zero calls. Registration L23694-L23720 with the pre-data re-bracket 484b9129
(record L23760-L23765). Reviewed blobs (LF of record; working tree has no CRLF, so the CRLF rendering is only listed):
`tools/analysis/e1_replicates.py` blob:abdf147f (sha256-lf16:5622bbf98ef935c4, crlf16:e3e9aeea088aed87),
`tools/analysis/e1_replicates_qlaunch.py` blob:471762cd (sha256-lf16:946011bc9e1c1c1d, crlf16:3dcd36e8c7db78a4); 8 TOMLs
N_o1..4 6ac40aa1 / d5735019 / 7c30209d / e60112c3, Q_o1..4 c040ac00 / 92ba9155 / fb0a8ae3 / 8e0beef7 (== qlaunch DECLARED).
Imported pins on main: e1_readout.py 88f7990c, e1_route_launch.py ba865deb (both equal).

## Verdict

**NOT READY.** One BLOCKER (B-1: the NON-INERT gate is vacuous on real data) and one HIGH Support finding for the registrar
(S-1). Everything else checked is CONFIRMED. READY after: B-1 fixed by the builder (delta re-review, <150 lines, 3 mutants) OR
replaced by a registrar pre-data ruling on a zero spread; S-1 bracketed by the registrar; C-1..C-5 carried by the operator.

## Per-claim table (deciding paths)

| # | claim | my evidence | result | sev |
|---|---|---|---|---|
| 1 | constructionOrderShuffleSeed is parsed and reaches construction | parser HeadlessBenchmarkRunner.kt L2327 (`toLong`), refusal off runPipeline L207, TOML-only guard L388-L393 (sets `config.formalism`); use sites ConstructionOrder.of(config) in TaxonomyOperations.kt L179 (split pass) and TaxonomyMerger.kt L577 / L842 / L929 / L996 (merge passes); manifest stamp V2EnginePool L207; ConfigParsesTest L76-L103 | CONFIRMED (by code, not by form) | - |
| 2 | R4 af_s42_o1 produced a different tree from af/seed_42 | the R4 log carries `[H9-ORDER] ... ACTIVE, seed=1` and the certificate "order shuffle : seed 1" (the shuffle RAN). Final snapshots compared id-invariantly: 81 vs 81 leaves, nearest-leaf map injective, min best cosine 0.99999999 over all 150 nodes, max abs mu delta 3.4e-5, leaf (depth, size) multiset EQUAL, all-node (depth, size, n-children) multiset EQUAL, matched kappa delta 0. Node ids differ only (assigned in visiting order) | **REFUTED: the same partition** (relabelled; float noise only) | BLOCKER via B-1 |
| 3 | NON-INERT gate refuses an inert shuffle | the builder's own `fingerprint()` (round 1e-6) on the R4 pair: s42 ce5cf0c55f5fa5f3 vs o1 6700c25c07d14ff1 -> DISTINCT. The gate ADMITS a partition-identical pair; selftest ST-I certifies "same hits, different geometry: admitted" with spread_N == 0.0 (fixture jitter 1e-4) | **REFUTED (vacuous)** | **BLOCKER** |
| 4 | identity precondition 0.6813 / 0.7269, b 327 / c 484 | `--identity-check` on main data: "top1 N-raw 0.6813, af_clean_s42 0.7269, b 327 / c 484 == the record -> HOLDS"; independent recompute of the same figures in POSTRUN_e1_readout rows 1-2 (cited, code untouched by this delta); DB size/mtime before == after | CONFIRMED to the digit | - |
| 5 | per-arm embedder guards | code L193-L213: every tree in its OWN space, discriminators N_o1 x qwen3 / Q_o1 x nomic must REFUSE; live run: N42 ADMIT (min cos 0.9997, 64 sites), Q42 ADMIT (0.9990, 69), both discriminators REFUSE (median cos 0.016 / 0.013); mutants X31 / X32 killed | CONFIRMED | - |
| 6 | ER1 / F-ER over the 4 shuffled arms only; s42 descriptive | compute() L370-L382 uses ORDERS only; s42 enter only identity / ER2; X13 / X14 killed; my R1 (`<=` at the WORSE boundary), R4 (F-ER strict `<`), R3 (seed term not /4), R2 (ddof 0) all KILLED | CONFIRMED | - |
| 7 | Support (d)-(f) arithmetic | sqrt(2) x 0.008 / 2 = 0.00566; sqrt(0.00823^2 + 0.00566^2) = 0.00999; MDE80 0.0280; measured Kish m-bar 1.0000 on 3,445 components (n_eff 3,445) | CONFIRMED (arithmetic) | - |
| 8 | Support (d): "the record holds no measured o1 FILING delta"; pilot SD 0.008 | R4 (row 2) is partition-identical on p8a29 => its filing delta is 0; H9-REM order arms (prog L4206ff) measured Top-1 0.7719 / 0.7735 / 0.7735 / 0.7744: range 0.0025, SD 0.00104. At SD 0.00104: SE_total 0.00826, MDE80 0.0231 | **PARTLY: arithmetic right, input contradicted by the record** | HIGH (S-1) |
| 9 | qwen3 launcher backup / refuse | backup sha256 == live for both caches else REFUSE (L141-L154); P' no sidecar at all; caches: no NON-EMPTY -wal/-journal (0 B admitted); per-table views before/after, only dataset `reserved_pool_meta` admitted; rc 3 on a WAL tail -> checkpoint -> `--verify`; `-PjvmThreads=12`; `-Dranking.db.path` forwarded (build.gradle.kts L374); selftest 19/19, mutants 16/16 KILLED | CONFIRMED | - |
| 10 | readout selftest / mutants | 61 checks PASSED; 35/35 KILLED (re-run here) | CONFIRMED | - |
| 11 | commit hygiene | `git show ee68eed7 --name-only --format= \| grep -c .` = 10; `grep -c '^src/'` = 0 (no Kotlin: gradle test not required); application.yml/.env/.gitignore/experiment_results = 0; 484b9129 ancestor | CONFIRMED | - |

## Defects and conditions

- **B-1 (BLOCKER, builder or registrar).** NON-INERT fingerprints leaf mu at 1e-6, but float noise between two
  partition-identical builds is 3.4e-5 (R4), so the gate passes on noise. If the shuffle is filing-inert (the record's only
  anchor-free data point says it is), all 4 hit vectors per embedder are equal, both spreads are 0, F-ER can fire only at G = 0
  and ER1's spread conjunct is empty: the vacuity the re-bracket was made to remove (record L23760, rule 8). The gate's own
  docstring ("spreads would be 0 by construction") is not what it tests. FIX (one of): (a) gate on FILING: refuse unless, per
  embedder, the 4 shuffled arms carry >= 2 distinct held-out hit vectors (the X21 form becomes the code; ST-I "same hits,
  different geometry" flips to REFUSED; X21 inverted to "non-inert by geometry" and must be KILLED; keep the fingerprint line
  descriptive, plus a partition line: sorted leaf (depth, size) multiset); or (b) the registrar rules pre-data that a measured
  zero spread is a scoreable outcome (the shuffle ran: path-independence measured) and the gate is dropped. (a) is the default.
- **S-1 (HIGH, registrar, pre-data bracket).** The declared order SD 0.008 is ~8x the record's measurement (row 8). Effects:
  ER1 gets more scoreable (MDE80 0.0231), P2's lower ends (0.004 / 0.005) likely FAIL, P4 (0.35) is overstated and F-ER is
  near-unreachable unless |G| collapses. Bracket the Support input and P2 / P4 before data; no criterion needs to move.
- **C-1 (HIGH, operator; pilot gate).** Build N_o1 and N_o2 first, then (zero calls) compare them with E1 N-raw by the row-2
  method (leaf count, injective nearest-leaf map, leaf (depth, size) multiset). If all three are the same partition: STOP before
  the other 6 builds and hand to the registrar (with fix (a) the full run would refuse anyway).
- **C-2 (BLOCKING for N_o1; operator) = the 0-byte -wal ruling.** Moving the sidecars to a dated backup, never deleting, IS
  the standard remedy (READY_e1_route2 C-E1R-1). It must cover BOTH `embeddings_cache.db-wal` (0 B) and
  `embeddings_cache.db-shm` (32,768 B, mtime 2026-10-02 15:36: a non-immutable reader opened it today): e1_route_launch
  refuses ANY -wal/-shm/-journal (L250-L256), so moving the -wal alone still refuses. Preconditions in one rule-7 window: no
  java (at review time PIDs 47392 Gradle daemon and 47440 Kotlin daemon were alive: a peer's build, not a construction; WAIT,
  never kill), exclusive-open probe FREE on the DB and both sidecars, -wal = 0 B (if > 0: STOP, data-steward), sha256 of the DB
  before == after the move, then `e1_route_launch.py --dry-run` must print no sidecars. The dataset cache's 0 B -wal / -shm do
  not block (not in P; qlaunch admits 0 B).
- **C-3 (BLOCKING for the Q legs and the readout; AUTHOR) = the checkpoint ruling.** The readout cannot avoid it:
  `e1_replicates.py` has no copy mode (`grep -c eval_db_copy` = 0); e1_readout's `--eval-db-copy` is `--dry-run` only by its
  reviewed design (L395, L1228) and covers only the dataset DB, while qwen3 vectors are read in place from embeddings_cache.db
  through open_ro, which refuses a non-empty -wal. And EmbeddingCache never closes its connection (memory
  construction-writes-cache-dbs), so EVERY qwen3 build leaves a WAL tail: qlaunch returns rc 3 and refuses the next Q build
  until a checkpoint. Expect up to 5 checkpoints (dataset cache after the nomic legs; both caches after each Q build). The
  author runs them (rw open/close or `PRAGMA wal_checkpoint(TRUNCATE)`, no JVM running, after the fresh backup). Avoiding them
  needs a new builder delta (copy-and-checkpoint-the-copy views in qlaunch and an admitted copy mode for `--run` over BOTH
  caches, originals re-hashed) and its own review: an AUTHOR DECISION, not recommended for 8 builds.
- **C-4 (MEDIUM, operator).** `gradlew --stop` after every leg (no `--no-daemon` in either launcher; C-E1R-3 precedent);
  a fresh backup per Q build (a checkpoint changes the file bytes, so the previous backup fails qlaunch's sha check).
- **C-5 (LOW).** e1_route_launch admits any config with a fresh outputDir; the nomic config blob is checked only at readout
  (diagnostics/config.toml == committed blob). Operator: launch exactly N_o1..4 by path.

## Launch sequence (valid only after B-1 and S-1 are resolved and the branch is merged by path; main checkout; zero calls)

```
python tools/analysis/e1_replicates.py --selftest ; python tools/analysis/e1_replicates.py --mutants
python tools/analysis/e1_replicates_qlaunch.py --selftest ; python tools/analysis/e1_replicates_qlaunch.py --mutants
python tools/analysis/e1_replicates.py --identity-check                       # HOLDS today
# rule-7 window, no java, probe FREE: backup both caches to E:/TaxoArena_backup_<date>_e1rep (SHA256SUMS.txt);
# move embeddings_cache.db-wal and -shm into it (C-2); re-hash the DB
for o in 1 2: python tools/analysis/e1_route_launch.py --arm nomic_raw --config experiment_configs/e1_replicates/N_o$o.toml ; gradlew --stop
# C-1 pilot gate (zero calls): N_o1 / N_o2 / E1 N-raw partitions; identical -> STOP, registrar
for o in 3 4: (same nomic line)
# AUTHOR: checkpoint mmlu_pro_dataset_cache_v2.db if its -wal > 0 (C-3)
for o in 1 2 3 4: fresh backup of both caches -> <backup_o>;
   python tools/analysis/e1_replicates_qlaunch.py --config experiment_configs/e1_replicates/Q_o$o.toml --backup-dir <backup_o>
   rc 3 -> AUTHOR checkpoints both caches -> python tools/analysis/e1_replicates_qlaunch.py --verify --backup-dir <backup_o> ; gradlew --stop
python tools/analysis/e1_replicates.py --dry-run ; python tools/analysis/e1_replicates.py --run
```

## Own mutants (deciding paths; e1_replicates.py selftest)

R1 WORSE `G < -maxs` -> `<=`: KILLED. R2 var_seed ddof 1 -> 0: KILLED. R3 SE_total seed term not /4: KILLED. R4 F-ER `<=`
-> `<`: KILLED. R5 fingerprint rounding 1e-6 -> 1e-3: KILLED, but only because ST-I REQUIRES the noise-only admission (decisive
for B-1: the selftest enforces the vacuous behaviour). Decisive real-data probe: row 3.

## Commands

```
grep -n constructionOrderShuffleSeed src/main/kotlin -r ; grep -n "ConstructionOrder.of" src/main/kotlin -r
python (id-invariant compare of last dag_snapshots.jsonl: experiment_results/anchorfree/af/seed_42 vs redraw/af_s42_o1/seed_42:
  leaf mu cos matrix, injective argmax, (depth,size) multisets, kappa)                                   -> row 2
python -c "<the builder's fingerprint() on AF.load_tree of both dirs>"                                   -> row 3: DISTINCT
grep -c H9-ORDER redraw/af_s42_o1/seed_42/headless_run.log (1) ; grep "order shuffle" .../fixed_point_certificate.txt
TAXOARENA_DATA_ROOT=<main> python tools/analysis/e1_replicates.py --identity-check                       -> row 4
python tools/analysis/e1_replicates.py --selftest | --mutants ; python tools/analysis/e1_replicates_qlaunch.py --selftest | --mutants
python -c "sqrt(0.00823**2+(sqrt(2)*sd/2)**2) for sd in (0.008, std([.7719,.7735,.7735,.7744],ddof=1))" -> rows 7-8
ls -la embeddings_cache.db* mmlu_pro_dataset_cache_v2.db* snapshots.db* ; tasklist java/python (Get-CimInstance cmd lines)
git show ee68eed7 --name-only --format= | grep -c . / grep -c '^src/' ; git hash-object <2 scripts + 8 TOMLs>
```
