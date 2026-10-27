# READY (delta) — UNION-AF-ROUTE "one cell per unsplit member": union-af-single-cell 43979bce

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls, no JVM, no construction. Amendment of record: prog L23660-L23667
(89cfdb70), with its brackets at L22633, L22638, L22649 and L23098. Base: main's reviewed reader a99bcee5
(READY_union_af_route_delta.md); the delta is `git diff 89cfdb70 43979bce` = 2 files (union_af_route.py +526/−34, new
union_af_route_ops.py +492); no Kotlin change. What READY_union_af_route(_delta) CONFIRMED on untouched code is cited, not
re-derived.

## Verdict

- **BUILD RESUMPTION: READY**, with the sequence below. Preconditions P1-P6 of READY_union_af_route still bind, with fresh DB
  copies.
- **READER `--run`: NOT READY until C-S1 is decided and implemented.** C-S1 is the AK1/AK2 filing asymmetry the one-cell rule
  creates. It is material to F-AK: a proxy gives +0.0077 in AF's favour, above F-AK's 80% firing point of 0.0062. The build,
  `--dry-run` and `--build-inputs` may proceed. The decision must be fixed pre-data, i.e. before any AK number is computed.

## Pins (LF of record; working trees LF)

| file | blob | sha256-lf16 / sha256-crlf16 |
|---|---|---|
| tools/analysis/union_af_route.py (a99bcee5 →) | f569d6f471fe793ebe0641bef576fe4f576c6d41 | 81069f9da6f9b93d / 47c1c49f64399c58 |
| tools/analysis/union_af_route_ops.py (new) | 5a020d2990b43c16ced727959c474c9a19ac6568 | fa9ef59d014a2d15 / deb856a1aa964d25 |
| v2_declared_cells.py (unchanged) | f0f568057995b5d0231da6e3d0d48755a7cf8386 | — |

## Rulings on the builder's checklist

| # | item | finding | verdict | sev |
|---|---|---|---|---|
| 1 | S1-S6 evidence + the teed console build.log | `single_evidence`: S1 manifest anchor_free + config_sha256_lf = the TOML's LF sha. S2 the console refusal carries a siteId, and no "Snapshot ID:" appears in either log. S3 no ACCEPTED/REJECTED row. S4 one GROW site with the source's label, cross-checked against the console siteId. S5 every row NO_PROPOSAL `min_pair_sep_below_bar` with bar = 0.025 and sep < bar. The engine prints the IllegalStateException only to the console (ops build_ifeval.log L232; headless_run.log lacks it), so the tee requirement is right. I ran it on a temp copy of the REAL ifeval evidence: root n00000001, best 0.02111, n 325, 15 rows, matching my own read of proposals.csv (15 × NO_PROPOSAL, one site GROW/n00000001/IFEVAL/325, max sep 0.02111, bar 0.02500). The S2 regex does not cross a line break, so a console line wrapped by PowerShell 5.1 stops at rc 1 (fail-closed, not vacuous): use the tee form the ifeval evidence used (UTF-8, one line) | CONFIRMED | — |
| 2 | Filing one-cell items by source, plus the disclosure | Filing by source is forced, because the graft has no leaf for an unsplit member. **U2/U3a: symmetric** (K_s files by true source as registered). **AK1/AK2: asymmetric.** AF-U gets a source oracle on the one-cell source (its items cannot be misfiled; no other item can be filed into it), while AK2's registered US_s files to the nearest of ALL centroids. Proxy (B0 bundle, 256-d truncation, US_0 at B0's k with IFEVAL at k = 1): 46 of 162 IFEVAL EVAL items go to a non-IFEVAL centroid and 2 others go to the IFEVAL centroid; the mirrored filing raises P(US_0) 0.7231 → 0.7307 (**+0.0077**). That is 1/3 of the planning spread 0.0233 and above F-AK's 80% firing point 0.0062. The disclosure's "like with like" is true of k only, not of filing → C-S1, C-S2 | REFUTED as worded | HIGH |
| 3 | k = 1 for K_s / US_s | `afu_state` sets ksrc = 1 and the single cell id; `us_fit` at k = 1 is the source centroid. AK1's total k counts 1 (amendment (3)). X72 KILLED | CONFIRMED | — |
| 4 | Merged CSV naming, pinning, refusal | `merged_validation` first refuses any graft row or leaf of a one-cell source (X71), then writes `inputs/validation_merged/{queries,train_queries,leaves}` write-once, adding one row per side item (EVAL+GATE held-out, TRAIN). Name = TRAIN-majority declared class of the source's TRAIN side items, tie to the smaller name. My O8 (naming from TRAIN+EVAL, a leak) is KILLED. All three files are sha256-lf pinned in inputs_manifest (`inputs` + `single`) | CONFIRMED | — |
| 5 | Exact --fill text | `fill`: writes once to graft_flatleaf.toml; re-verifies the one-cell evidence; refuses on D-8 and on a BUILT member without a snapshot; template order = corpora = the registered sources; keeps BUILT ids in template order; removes the one-cell placeholder and its corpus; adds a `# FILLED ...` head line naming BUILT ids, ONE-CELL sources and the build commit. Cases fill / fill_real (the committed template, ifeval one-cell) pass; Q08-Q10 KILLED. The engine's `checkUnionMembers` (V2EnginePool.kt L222-L249) checks members one by one, with no coverage requirement | CONFIRMED | — |
| 6 | Refusal if the set falls short of 6,153 / 5,642 | `build_inputs` loads the bundle with expect = (pool, 6153, 5642); `--run` refuses unless 6,139 / 5,628. X73 (one-cell held-out rows not added) KILLED by that refusal | CONFIRMED | — |
| 7 | Rebuild every member, ifeval included, at one commit | D-8 holds in `fill` and in the reader (`build_commits` over all 6 member manifests + the graft; a refused build still writes run_manifest with its commit, as the incident manifest shows: de06ddf3, anchor_free true). The ifeval incident (de06ddf3) cannot be reused: rebuild in a NEW worktree at the merge commit. The old rp13-afu-run copies are dirty (+216 reserved_pool / +1 meta), so make fresh DB copies (P4) | CONFIRMED | — |
| 8 | Continuing replaces STOP only as the amendment says | `classify` returns rc 3 only when the console carries the single-leaf refusal AND S1-S6 verify. Every other failure, an unverifiable refusal, or a declared member that later has a snapshot gives rc 1 STOP (st_classify ×4). The declaration is append-only. An all-one-cell declaration is refused (X77; the amendment does not cover it). Same reason, same handling, best separation printed: amendment (2) | CONFIRMED | — |

## Re-runs

- Reader: `selftest: 12 / 12 passed`; `MUTANTS: 86 of 86 KILLED; control survived`.
- Ops: `selftest: 4 / 4 passed`; `MUTANTS: 11 of 11 KILLED`.
- Dry-run against main's data: AK-IDENTITY reproduced; `ONE-CELL members: none declared`; `REFUSED: AF-U build outputs ABSENT
  (16 of 16)`; rc 1; nothing written (only `ops_20261003/` under union_af_route/).
- Own mutants: O8 (naming leak) KILLED; O9 (S2 snapshot clause dropped) KILLED; O10 (S4 site-label clause dropped) SURVIVED,
  not decisive (S1's TOML sha binds the member to its source); O12 (declared n_site not compared) SURVIVED, not decisive (the
  outcome prints the evidence's n, not the declaration's).

## Conditions

- **C-S1 (HIGH; AUTHOR / registrar decision, pre-data; gates `--run`)**: for a one-cell source, choose which AK filing decides.
  (a) MIRROR (recommended; the like-with-like reading of amendment (3)): in AK1's U_s and AK2's US_s, the one-cell source's
  items are filed by source to its centroid, and that centroid is excluded from every other item's nearest search. The
  registered rule is printed beside. (b) REGISTERED: keep "nearest of ALL centroids" and print the mirrored value beside, with
  the bias named (it favours AF). Either way the outcome prints both, and the per-source D for the one-cell source.
  Implementation plus selftest plus mutants, then a delta READY.
- **C-S2 (MEDIUM, gates `--run`)**: `single_lines`' DISCLOSURE must read "like with like in k; in filing, the one-cell source
  is filed by source for AF-U, which [is mirrored | is not mirrored] in AK1 / AK2 (C-S1)", instead of claiming like with like
  outright.
- **L-1 (LOW)**: add cases for O10 and O12.

## Exact build sequence (operator)

1. Merge union-af-single-cell (43979bce) into main by path (only the 2 tools/analysis files). Then
   `git worktree add --detach .claude/worktrees/rp13-afu-run2 <merge commit C>`; nothing is committed in it until the graft
   has run (D-8).
2. P1-P6 of READY_union_af_route: rule 7 W1-W5; root `*.db-wal` at 0 B or absent; dated backups; per-table hashes of main's
   embeddings_cache.db and mmlu_pro_dataset_cache_v2.db in both views; FRESH copies of embeddings_cache.db,
   multicorpus_cache_v1.db, mmlu_pro_dataset_cache_v2.db and snapshots.db into rp13-afu-run2, each sha256 = main's; the
   B0-2 pool check with `TAXOARENA_DATA_ROOT=<main>`.
3. In rp13-afu-run2, for m in ifeval, gpqa, musr, math, bbh, mmlu_pro_lb, one at a time:
   `mkdir -p experiment_results/archv2/union_af_route/AF-U/<m>`, then
   `./gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args="--config experiment_configs/union_af_route/AF-U/<m>.toml" 2>&1 | tee experiment_results/archv2/union_af_route/AF-U/<m>/build.log`
   (or the ops `--plan` PowerShell `Tee-Object` form; the refusal line must not be wrapped). Then
   `python tools/analysis/union_af_route_ops.py --member <m>`. On rc 0 or rc 3, go to the next member; on **rc 1, STOP** and
   report. The JVM's exit code does not decide. A refused member's outputDir stays as evidence.
4. `python tools/analysis/union_af_route_ops.py --fill`, then
   `./gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args="--config experiment_configs/union_af_route/AF-U/graft_flatleaf.toml" 2>&1 | tee experiment_results/archv2/union_af_route/AF-U/graft_flatleaf/build.log`.
5. Post-build checks per READY_union_af_route step 3: main's DBs unchanged; worktree copies with only the expected deltas;
   copy `AF-U/` to main (including build.log, proposals.csv, single_cell_members.json), sha256 equal per file; by-path commit of
   the filled graft TOML, the declaration and the operator log.
6. Reader, from main: `--dry-run`, then `--build-inputs`, then `--dry-run`. **`--run` only after C-S1 / C-S2 and their delta
   READY.**

## Commands

```
git diff --stat 89cfdb70 43979bce ; git diff 89cfdb70 43979bce -- tools/analysis/union_af_route.py
(worktree) python tools/analysis/union_af_route.py --selftest | --mutants ; python tools/analysis/union_af_route_ops.py --selftest | --mutants
python -c "U._ROOT[0]=<temp copy of incident_ifeval + build_ifeval.log + ifeval.toml>; U.single_evidence('ifeval','IFEVAL')"
python -c "csv proposals.csv: 15 NO_PROPOSAL, one site, max sep 0.02111, bar 0.02500"
python - (B0 bundle, 256-d, us_fit seed 0 with IFEVAL k=1: primary 0.7231 vs mirrored 0.7307)        # C-S1 size
python scratchpad/rp13m/own_mutants4.py                                                               # O8 O9 killed; O10 O12 survived
TAXOARENA_DATA_ROOT=<main> TAXOARENA_RESULTS_ROOT=<main> python tools/analysis/union_af_route.py --dry-run   # rc 1, AF-U ABSENT
grep -n "fun checkUnionMembers" -A30 src/main/kotlin/taxonomy/dataset/V2EnginePool.kt
```
