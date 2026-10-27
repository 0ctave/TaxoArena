# READY — UNION-AF-ROUTE (RP13): AF-U build TOMLs (a994a722) + reader (union-af-route 2db6e35c)

Reviewer: adversarial-reviewer, 2026-10-02, at main 40d4b6cd. Zero calls, no JVM, no construction. Registration of record:
prog L22627-L22653 (U1-U3, IDENTITY, Support) + L23093-L23116 (AK1/AK2/F-AK, AK-IDENTITY, Support); results JSON
`docs/agents/results/UNION-AF-ROUTE.json` (state registered). First full review of both branches.

## Verdict

- **BUILD (TOMLs a994a722): READY**, under launch preconditions P1-P6 below. The diff against RP12-R2 B0 is exactly the four
  registered keys; P2 (the pending `mmlu_pro_dataset_cache_v2.db-wal`) **blocks the launch** until the author checkpoints it.
- **READER (2db6e35c): READY for `--dry-run` and `--build-inputs`; `--run` CONDITIONAL** on C-1..C-4 (three survived
  refusal-path mutants plus one ordering fix) and a delta READY on the fixing commit (small: tests plus one moved block).
- Readings R1, R3, R6, R7, R8, R10 CONFIRMED (R3 with a disclosure, R10 with C-1/C-4). The hooks-plus-driver deviation is
  ACCEPTED (not C-7: same statistics, inertness proved by execution). Removing the sqlite guard is ACCEPTED.
  `union_af_route_train_policy.json` may **not** be committed (D-5).
- AF-vs-KMEANS: **like with like for AK2 (the arm that decides F-AK)**. AK1 is not like with like: AF-U carries the source
  partition and U-global does not. The registration says so, and AK1 decides nothing.

## Pins (LF of record)

| object | blob (LF) | sha256-lf16 / sha256-crlf16 | working tree |
|---|---|---|---|
| tools/analysis/union_af_route.py | ce6919194728832e83e9bcea8976fb4b5f26c810 | 6ed7715d06c46634 / 681befe57688a329 | LF |
| tools/analysis/v2_declared_cells.py (from c5b90278) | 1d98888faf4e9ed8cceaa13acd952c3f18539668 | 405c0db8aac81ae6 / 53b523548695603e | LF |
| AF-U/bbh.toml | 1dfa9b87be46ca433ad1cc3e1693e10e4ccdbe99 | — | CRLF on disk (75/75 lines) |
| AF-U/gpqa.toml | 11b09c2e5d860a9ed2ffc33844cd81f21336dd43 | — | CRLF |
| AF-U/ifeval.toml | 05ebd15ebaf221e63d08ec7073485335b4a864ac | — | CRLF |
| AF-U/math.toml | eebc74ce13d595a39afba4052f9757626e5f096b | — | CRLF |
| AF-U/mmlu_pro_lb.toml | 3a57cb09bafc90486316b7fd6c3125e03245b52c | — | CRLF |
| AF-U/musr.toml | 6d14acfb078b9423f11b26c7c11a0895f3663686 | — | CRLF |
| AF-U/graft_flatleaf.toml.tmpl | 9b5d5de17642f04b1d9977576f326646944d9a94 | — | CRLF (84/84) |

The pinned imports g13_breakdown c29fa1c3, g13_comparator 61d83ec7 and rp12_pairing 35214b3f are checked at import, and the
dry-run printed them. The src/ tree has 0 changed files between 50c71784 and main 40d4b6cd (counted with `--name-only | wc -l`),
so a build at a994a722 runs main's engine.

## Per-claim table (deciding claims)

| # | claim | my result | verdict | sev |
|---|---|---|---|---|
| T1 | The TOML diff against B0 is only anchorFree / bar / slice / outputDir | `diff` on all 6 members: header comment, outputDir, `+anchorFree = true`, bar 0.0145->0.025, slice 512->256; nothing else. Template: the same minus anchorFree (the runner refuses anchorFree with unionSnapshots, HeadlessBenchmarkRunner L216-L220). z 2.0 and mcs 55 are unchanged, matching af_clean_s42's config | CONFIRMED | — |
| T2 | enableFinalMetrics true (B0) vs false (af_clean_s42) | TaxonomyEngine L933: a post-construction TaxonomyMetrics report on the returned root (TRAIN groundTruthMap, L284). It does not feed the tree or any file the reader reads. Keeping B0's `true` honours the "only the four keys differ from B0" rule | CONFIRMED (keep true) | LOW |
| T3 | No graft_descent template, so D_fd NOT COMPUTED | True: the R9 branch is exercised by the `desc` case. D_fd is a REGISTERED descriptive (prog L22636), so this is an omission of a registered line → D-3 | PARTLY | LOW |
| T4 | One build commit across the manifests (D-8) | `build_commits` refuses on more than one commit across the 6 member manifests plus the graft manifest; X47 killed. B0's manifests all carry 2703f2c2. Launch consequence: P5 | CONFIRMED | — |
| S1 | Selftest 10/10 | re-run: `[RP13] selftest: 10 / 10 passed` (50 s) | CONFIRMED | — |
| S2 | Mutants 63/63 | re-run: `MUTANTS: 63 of 63 KILLED; control survived; survivors none` | CONFIRMED | — |
| S3 | Inertness case vdc_inert | passes. V06 (an empty xtree_cell frozen when absent) is KILLED by vdc_inert, so the case discriminates (the changed code ran) | CONFIRMED | — |
| S4 | The dry-run reproduces the B0 AK-IDENTITY, then refuses AF-U ABSENT | run against main's data: D_U +0.0738, D_Us +0.0656, spread_U 0.0414, spread_US 0.0233 = g13_breakdown_outcome.txt (blob 3ca9629b) L38-L39; then `REFUSED: AF-U build outputs ABSENT (16 of 16)`, rc 1, nothing written (no union_af_route/ dir; DB listing of the 25 root *.db/-wal files identical before and after). Own spot check: B0 bundle 6,139 / 5,628, P_fl 0.8119 (= registered b0_p_fl); P_fl − D_U = 0.7381 = P(U_0) of record | CONFIRMED | — |
| R1 | AF cell = the item's modal flatLeaf leaf_id, not a TRAIN-majority name | `af_cells` → `GB.item_leaves` → `_modal_leaf`; X37 (naming leak) and X38 KILLED. Naming would fold leaves into declared classes and the AF arm would collapse toward the declared arm, so leaf_id is the label-free reading of "Cells: AF-U leaves" | CONFIRMED | — |
| R3 | K_s cell = nearest centroid among the item's declared source(s) | `file_by_source`, X35/X36 KILLED. This is the registered rule ("EVAL filed by source"). **Disclosure:** flatLeaf files over ALL grafted leaves (UnionRouting.kt L17), so in U2/U3a K_s has a source oracle at filing that AF-U lacks. The bias runs against AF (D_K pushed negative) → D-4 | CONFIRMED + disclose | MEDIUM |
| R6 | U3 = Holm over two TOSTs; smaller p first at 95%, then 90%; stop; strict | `holm_u3` L656-L668 matches Holm at family α 0.05 (α/2 → a 95% interval, α → a 90% interval) and the registration's words. X12-X18 KILLED. The tie order (O5) SURVIVED but is not decisive: equal p values never arise in practice | CONFIRMED | LOW |
| R7 | "by support" iff abs(D_K) ≤ max(MDE80 measured, spread_K) | `bar = max(dk["mde"], spread)`, mde = 2.80 × the measured SE_2stage (`lin`); X20/X21 KILLED | CONFIRMED | — |
| R8 | AK1 k = AF-U's total snapshot leaves; TRAIN-majority naming; EVAL to the nearest of all centroids; AK2 primary has no source oracle | `ak_compute` L420-L462; X29-X33 KILLED; the AK-IDENTITY on B0 reproduces through the same path | CONFIRMED | — |
| R10 | The declared arm's frozen policy = leg U's file, else [RP13-R3] | The code is correct (best_single AND true_source_domain). **O1 SURVIVED:** dropping the true_source_domain clause passes the selftest. The check also runs inside rp13_tail, i.e. AFTER the single EVAL key read, although it needs only TRAIN objects → C-1, C-4 | CONFIRMED (code); test gap | MEDIUM |
| G | Removal of flat_mix_mmlu's sqlite guard | That guard whitelists FLAT-MIX's own 4 DBs and would refuse the v2 views. Every DB open in the chain (union_af_route, v2_declared_cells, rp12_pairing, g13_breakdown) goes through `data_v2.ro.open_ro` (mode=ro & immutable=1, query_only, refuses a non-empty -wal / -journal). `create_new` / `open_scratch_rw` appear only in selftest temp dirs. union_af_route.py's only `sqlite3.connect` reference is the restore at L182 (grep count). The removal is printed in the header | CONFIRMED | LOW |
| H | Hooks-plus-driver deviation | Same fit(), same replicates (an extra grouping draws no random number), same contrast form. Only placement differs: no CLI flag, inert when absent (S3). Not a substitution | ACCEPTED | — |
| LL | AF-vs-KMEANS is like with like on label information | AF-U: source partition (federation) + labels at naming only; flatLeaf over all leaves. US_s (AK2): per-source fits + labels at naming + nearest of ALL centroids, so AK2 is matched exactly. U_s (AK1): no source, so AF-U holds one more rung of information (registration predictions note it; AK1 decides nothing). The "anchored B0" row of the ladder is printed beside only, never ranked | CONFIRMED for AK2 / F-AK | — |
| SUP | Support arithmetic (DEFF and its source, n_eff, SE, MDE) | U1 SE (3.82−1.43)/3.92 = 0.610pp, MDE80 1.707 (DEFF 1.392 measured, G14; n_eff 4,244). U2 0.327pp, MDE80 0.914. Holm half-widths 0.64 / 0.54 (registered 0.65 from the rounded 0.33). AK1 sqrt(0.1634/6139×1.341) = 0.005974, MDE80 0.01673. AK2 0.006091, MDE80 0.01706. F-AK point 0.0233−0.01706 = 0.0062. n_eff 4,578 / 4,237; Kish 1.091. DEFF transported from G13-BREAKDOWN (measured), source named. The reader prints the measured DEFF, n_eff and MDE80 beside every deciding statistic (sup_line, ak support line). The registrar's note "co-occur only if SE < ~0.18pp" does not reproduce as a feasibility bound (1/3.92 = 0.255pp at 95%, 0.277 at 90%), but both clauses are scored anyway, so the note decides nothing | CONFIRMED | LOW |

## Own mutants (deciding / gate paths; run through the builder's harness, `U.MUTANTS` swapped in memory)

| id | change | result | decisive |
|---|---|---|---|
| O1 | R10 compares best_single only | SURVIVED | yes (gate) → C-1 |
| O2 | vdc: the B3 re-fit check of the extra arms disabled (`if False and …`) | SURVIVED | yes (gate) → C-2 |
| O3 | K_s fit seed fixed at 0 (spread_K → 0) | KILLED (builders, ak_e2e, run_e2e) | yes |
| O4 | [RP13-IDENTITY] compares the point only (interval ignored) | SURVIVED | yes (precondition "to the printed digits") → C-3 |
| O5 | Holm tie puts U3b first | SURVIVED | no |

## Defects and conditions

- **C-1 (MEDIUM, before --run)**: add a refusals case in which leg U's file differs from the in-run policy in ONE
  true_source_domain pick (best_single equal), so that O1 is killed.
- **C-2 (MEDIUM, before --run)**: add a case in which a frozen xtree_cell pick differs from the re-fit beside EVAL
  (`[B3] an RP13 extra arm's policy …`), so that O2 is killed.
- **C-3 (MEDIUM, before --run)**: add an [RP13-IDENTITY] case with the point equal and one interval end differing, so that O4
  is killed.
- **C-4 (MEDIUM, before --run)**: move the R10 equality from rp13_tail to before the B1 marker / EVAL key read. It needs only
  the frozen TRAIN policy and leg U's file, so a refusal would no longer burn the single read. Then re-run the selftest and
  mutants plus O1/O2/O4; a delta READY follows.
- **D-3 (LOW)**: either add `graft_descent.toml.tmpl`, derived from B0's by the same changes (a cheap graft, minutes), so the
  registered descriptive D_fd is computed; or have the registrar bracket "D_fd NOT COMPUTED" before the run. Not deciding.
- **D-4 (MEDIUM, outcome text)**: rp13_tail prints one line that U2/U3a's K_s is filed with the true source (registered),
  while AF-U is flatLeaf over all leaves, so D_K carries a filing-information asymmetry against AF.
- **D-5 (rule)**: `experiment_results/archv2/union_af_route/union_af_route_train_policy.json` holds per-leaf model picks for
  AF-U and K0..K4. The registration says "Publishes aggregate G only, no per-leaf model rows (rev2 L680)". Write it (B3 needs
  it) and print its sha256 (v2_declared_cells L1157), but do **not** commit it. It is not gitignored (`git check-ignore` rc 1),
  so the registrar must not `git add` it. G14's committed policy is no precedent here, because RP13 carries the explicit
  clause. The author may override.
- **D-6 (LOW, operational)**: `rp12_build_configs.py --fill` refuses outside the rp12 lanes, and no AF-U fill tool exists
  → P5.

## Build preconditions and exact launch sequence

- **P1 rule 7 / lane**: no construction, site null, Ollama pass (CARD-PROTOCOL) or pool reader running (W1-W5 printed;
  admitted PIDs; ≥ 12 GB free); 12 threads (`-PjvmThreads=12`); CPU lane paused; no git write under src/ in the window.
- **P2 WAL (BLOCKS)**: `mmlu_pro_dataset_cache_v2.db-wal` is 8,272 B (mtime Oct 2 03:50; the other root -wal files are 0 B).
  The JVM would not refuse, but the build writes this DB (`splitByV2Pool` → `recordPool` → `ReservedPool.save`,
  reserved_pool_meta). With a pending tail: the two hash views disagree (immutable=1 hides the tail), so no baseline exists;
  a copy into the build worktree without the -wal is stale; and the reader's B0-2 check does not look at this DB. **The author
  checkpoints it; then `ls -la *.db-wal` must show 0 B (or absent) for embeddings_cache, mmlu_pro_dataset_cache_v2 and
  multicorpus_cache_v1.**
- **P3 backup + per-table hashes** (memory construction-writes-cache-dbs), with no JVM running: dated copies of
  `embeddings_cache.db`, `mmlu_pro_dataset_cache_v2.db` (+ multicorpus_cache_v1.db, snapshots.db) to
  `experiment_results/_backup/*_2026-10-0X.db`. Take a per-table sha256 over `SELECT * FROM t ORDER BY <pk>` (repr rows) in
  BOTH views (immutable=1 and mode=ro); the two must agree.
- **P4 worktree DBs**: the build runs from a detached worktree with relative DB paths. Copy the four DBs into it and check that
  each sha256 equals main's (FLAT R2 incident: a stub mmlu_pro_dataset_cache_v2.db, prog L22507).
- **P5 one commit**: `git worktree add --detach .claude/worktrees/rp13-afu-run <C>`, where C is a994a722 or main after a
  by-path merge of union-af-tomls (src identical either way). All 7 runs from C, and nothing committed inside the worktree
  until the graft has run.
- **P6 pool**: `python tools/analysis/v2_union_pool.py --dry-run --pool pv2_1575de61bb20e977`, BEFORE the window (the B0-2
  form, prog L22165; pool_guard.py holds no pv2 pool).

Sequence, inside the worktree (smallest members first, so an anchor-free refusal costs minutes. TRAIN per source from B0's
bundle: IFEVAL 325, GPQA 331, MUSR 454, MATH 773, BBH 3,474, MMLU_PRO_LB 6,977):
1. `.\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args="--config experiment_configs/union_af_route/AF-U/<m>.toml"`
   for m = ifeval, gpqa, musr, math, bbh, mmlu_pro_lb, one at a time. After each, check: rc 0; the log carries
   `[ANCHOR-FREE] anchor-free construction ACTIVE` and `[SPLIT-V2]` / `[TRAIN-ONLY]`; run_manifest has anchor_free true and
   commit C; record the snapshot id and leaf count. **If a member ends `[ANCHOR-FREE] construction ended with the root as a
   single leaf`, STOP**: the outcome is registered nowhere, so it goes to the registrar, and no per-member bar/mcs change is
   allowed.
2. Fill: copy `graft_flatleaf.toml.tmpl` to `graft_flatleaf.toml` in the worktree, put each `__SNAP_<SRC>__` to its member's id,
   `grep -c __SNAP_` = 0; leave it untracked. Run it with the same command line. (The reader's leaves-CSV-vs-snapshot check,
   X49, catches a wrong fill.)
3. Post-build: main's DBs per-table unchanged (the build wrote the worktree copies). On the worktree copies: embeddings row
   count unchanged (no cache miss, so no embedding call); `queries` delta listed (expected 0, since B0 wrote the same texts);
   reserved_pool_meta: only the build's own row. Copy `experiment_results/archv2/union_af_route/AF-U/` to main (sha256 equal
   per file); by-path commit of the filled graft TOML and the operator log.
4. Reader, from main after the union-af-route merge (C-1..C-4 + delta READY): `--dry-run` → `--build-inputs` → `--dry-run` →
   `--run`.

## Commands

```
for s in bbh gpqa ifeval math mmlu_pro_lb musr; do git show main:experiment_configs/rp12_r2/B0/$s.toml >b0/$s; git show union-af-tomls:experiment_configs/union_af_route/AF-U/$s.toml >af/$s; diff b0/$s af/$s; done   # T1
git diff 50c71784 2db6e35c -- tools/analysis/v2_declared_cells.py ; git diff --name-only 50c71784 main -- src build.gradle.kts gradle | wc -l   # 0
(worktree union-af-route) python tools/analysis/union_af_route.py --selftest     # 10 / 10
(worktree union-af-route) python tools/analysis/union_af_route.py --mutants      # 63 of 63 KILLED, control survived
TAXOARENA_DATA_ROOT=<main> TAXOARENA_RESULTS_ROOT=<main> python tools/analysis/union_af_route.py --dry-run   # AK-IDENTITY reproduced; REFUSED AF-U ABSENT (16 of 16); rc 1
python scratchpad/rp13m/own_mutants.py   # O1-O5 via U.run_mutants with U.MUTANTS swapped; 1 of 5 killed (O3)
python -c "np.load(B0 g13_bundle_flatleaf.npz): eval_fl.mean() 0.8119; 6139 / 5628; TRAIN per source"   # S4, P-order
ls -la --time-style=full-iso *.db *.db-wal  (before/after my runs: identical, 25 lines); git check-ignore -v <policy path> (rc 1)
grep -n "recordPool\|ReservedPool.save" MMLUDatasetFetcher.kt; UnionRouting.kt L17; TaxonomyEngine.kt L284/L785/L933; HeadlessBenchmarkRunner.kt L216
```
