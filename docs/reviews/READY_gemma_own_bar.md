# READY review: GEMMA-OWN-BAR (branch gemma-own-bar, tip d9f43d19; main d6a8fc0c merged in)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls; no null leg, construction or readout run; nothing written under any
data root. Registration docs/judge_v2_program.md L23915-L23927 (d50c47d4; R1 bracket e1e6c81d at L23923).

## VERDICT: READY, with conditions C1-C3 (operational and registrar, pre-data). No BLOCKER in the code.

Reviewed blobs (LF of record = `git hash-object`; the working tree equals HEAD, `git status --short` 0 lines):

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working tree) |
|---|---|---|---|
| tools/analysis/gemma_own_bar.py | 3d92c811 | 6252d2d11739953c | same (LF in tree) |
| src/test/kotlin/taxonomy/GemmaOwnBarNull.kt | a7c0e9e5 | 271a1368d9e38174 | same |
| src/test/kotlin/taxonomy/GemmaOwnBarArmTest.kt | 883f8c80 | c061503d5e234b91 | same |
| src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt | 0833e99c | 7400e7d2be81b6d7 | 2e26b649c0033e8e |
| build.gradle.kts | 571babeb | 53d0f8d7f7c84b09 | 04291e209c86ad01 |

Pinned instrument: intent_transfer_s1.py 4e9d9d05 and intent_s1_export.py 75310a98 at d9f43d19, equal to main's (the script
refuses otherwise). Source TOML m_af_g.toml blob 53a56948.

## Per-claim table (deciding claims only)

| # | claim | result | evidence (my number vs claimed) | sev |
|---|---|---|---|---|
| 1 | Conflict resolution kept CERT-PC-K2 byte-identical to main | CONFIRMED | `git diff d6a8fc0c d9f43d19`: build.gradle.kts 32+/0-, SeparationNullBySizeTest.kt 147+/0- (0 removed lines in each); the method hunk is inserted at L2876, after certPcK2's closing line; CertPcK2ArmTest.kt and cert_pc_k2.py: 0 diff lines. The gemma lines equal 25814d1a's additions (31/31 and 145/145 `+` lines), except 2 comment lines that now also name certPcK2. 5 files changed in total, 0 under src/main, 0 of application.yml/.env/.gitignore | - |
| 2 | Calibration is TRAIN-only: MASSIVE TRAIN 9,826, table sha 6ce9bdf8 | CONFIRMED | PREFLIGHT re-derivation from the pinned ingest DB (487e0093 PIN OK): 9,826 distinct texts, table 6ce9bdf8494be7d9, the same as export_manifest.json massive_s1 (n_texts TRAIN 9826, n_train_rows 9826, table 6ce9bdf8…). Kotlin loadTrain reads `side = 'TRAIN'` only and refuses any row off TRAIN/GATE, a meta n_train off the count, corpus ≠ massive, salt ≠ 1. calibrate() refuses unless both legs' TRAIN text-set sha, n and table sha equal the re-derivation. K2 (reads GATE) re-run by me: KILLED | - |
| 3 | Bar fixed before the build: 0.025 × p95_g / p95_q; width-only bar beside | CONFIRMED | `bar_g = BAR_OF_RECORD * pg / pq` (L269 of the script); width-only `0.025 × iso[768]/iso[256]` printed, descriptive. The bar file is write-once (mode x). --write-config needs it. --run refuses unless the build's diagnostics/config.toml equals g_af.toml regenerated from the bar file. The engine copies the TOML verbatim: S1's m_af_g diagnostics/config.toml = m_af_g.toml after CR stripping (cmp IDENTICAL). So a build without the 6-dp bar_g cannot pass. Mutants "bar ratio inverted", "legs swapped", "deciding bar from the iso leg" KILLED; own R4 (width bar from 512) KILLED | - |
| 4 | Both nulls moment-matched | CONFIRMED | Both legs call `cpcMoments(vectors)` → `cpcSiteArm` (withinNodeCloud: Gaussian with the population's slice mean and covariance, projected to the sphere; production splitSingleNode; canonicalConfig(55); siteNull seeds cpcSeed(20260908, "MASSIVE_TRAIN_ROOT", rep)). That cpcSiteArm = siteNull's runArm is CONFIRMED in READY_cert_positive_control.md row 12 (not re-derived here). Own KM2 (moments from n−1 vectors) KILLED (E-G, E-Q) | - |
| 5 | "Bit-identical to the reviewed null arm" | CONFIRMED (scope) | E-G and E-Q compare the arm's 8 replicates with an independent cpcSiteArm call on vectors the test decodes itself. This proves the INPUTS (TRAIN-only rows, first-d floats, big-endian, normalisation, seed, site, mcs, slice). It does not prove cpcSiteArm itself, which is covered by claim 4's citation. Write it that way. | LOW |
| 6 | G-AF TOML = m_af_g.toml except the bar and outputDir | CONFIRMED | my difflib + tomllib run on config_text(m_af_g @d9f43d19, "0.012345"): exactly 2 lines and keys ['outputDir', 'proposalSeparationBar']; slice 768, corpusDbPath, pool p9d1bbcd0ee6b8988 unchanged; the trailing newline is kept | - |
| 7 | GO1 = S1's T-C1 rule; degenerate iff L < 10 | CONFIRMED (+C3) | compute_go calls IS1.t_c1 unchanged (blob-pinned): D1 = tree NMI − mean over seeds 0-19; spread_K over seeds 0-4; bar max(MDE80, spread_K); TOST vs GATE delta_c. `degenerate = L < 10`; F-GO leaf clause `L <= 10`, matching the R1 bracket. Mutants "degenerate at <= 10" and "F-GO leaf clause < 10" KILLED; own R1 (GATE not frozen before T-C1) KILLED by S1's GATE-before-EVAL refusal | - |
| 8 | Inertness | CONFIRMED | additions only (claim 1); nullBySize excludes `*gemmaOwnBar*`. The execution discriminator: GemmaOwnBarArmTest drives the new method, and the builder's javap check found 0 pre-existing members changed (cited, not repeated) | - |
| 9 | Tests | CONFIRMED | full suite `gradlew.bat test --offline` in the worktree: 550 tests, 2 failures (the two known: MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank trace), 0 errors. GemmaOwnBarArmTest 6/6, CertPcK2ArmTest 2/2. Python --selftest 68 OK; --mutants 38/38 KILLED | - |
| 10 | Kotlin mutants 26/26 | CONFIRMED (sample) | no runner is committed. I re-ran 4 decisive ones: K2, K3, K25, K19, all KILLED. Control 6/6 after each restore; blobs back to a7c0e9e5 / 0833e99c | - |
| 11 | Support (re-derived) | CONFIRMED | DEFF 1.0093 = Kish with 23 two-item components: (4,900 + 23×4)/4,946 = 4,992/4,946 = 1.00930; n_eff 4,900.4. SE 0.0025 = S1 MASSIVE TOST half-width (0.00444+0.00371)/2 = 0.004075 / 1.645 = 0.00248. Reach 0.017 − 1.645×0.0025 = 0.01289 (registered 0.013); MDE80 = 2.8×0.0025 = 0.0070. SCOREABLE iff L ≥ 10. The script prints the measured values beside the registered ones | - |
| 12 | No writes to DBs | CONFIRMED | intent-s1-run ingest / emb gemma / emb qwen3 / S1 m_af_g.db: sha256-16 487e0093… / b187b82f… / 9e100e04… / 4cd430c6… and mtimes equal before and after my print-only runs; m_af_g.db-wal 379,072 B unchanged; no experiment_results/gemma_own_bar created (count 0) | - |

## Own mutants (deciding paths)

R1 compute_go without `STATE["gate_frozen"]=True`: KILLED (decisive) · R2 iso-leg sepBar check off: SURVIVED (not decisive; iso leg is descriptive) ·
R3 legs-same-TRAIN check off: SURVIVED (not decisive; each leg is already matched to the re-derivation) · R4 width-only bar from iso[512]: KILLED ·
R5 make_arm "M-AF" (qwen3 world) for G-AF: SURVIVED (decisive path, see D-1) · R6 bar_toml/bar_g consistency in load_bar off: SURVIVED (not decisive) ·
KM1 iso cloud at dim 256: KILLED (E-I) · KM2 moments from n−1: KILLED · KM3 redundant 0.025 check in the null leg off: SURVIVED (not decisive; -DsepBar is refused earlier).

## Conditions (before the run)

- **C1 (operational, required): use a FRESH DATA_ROOT, not intent-s1-run.** `intent_s1_export.py --export` refuses an existing
  build DB (`lexists`, L542), and S1's used m_af_g.db carries a non-empty -wal that the null arm refuses. The printed plans default to
  TAXOARENA_DATA_ROOT, so pointing that variable at intent-s1-run fails at step 0. Create a run worktree at the merged commit and copy in the pinned DBs (sequence below).
- **C2 (brief): a fresh `--export M-AF-g` in that root comes first.** Its table sha must be 6ce9bdf8 and it must have EVAL rows 0. The three null legs read
  it BEFORE the build (the build writes reserved-pool state into it).
- **C3 (registrar, pre-data, before --run): bracket GOB-R1 and GOB-K1.** INSTRUMENT says "k-means at k = L … seeds 0-4". The
  verbatim T-C1 that GO1 names averages seeds 0-19 and takes spread_K over 0-4, and the script follows T-C1 verbatim. This is not C-7 substitution, because GO1 is the
  deciding line and names T-C1 verbatim, but the registration's two sentences disagree. Also: both nulls run at bar 0.025, and the registration is silent on that.
  The bar enters the null statistic as the splitter's marginalEps (k choice), so a null at bar_g would differ (GOB-K1; D1 precedent).

## Defects (none blocks READY)

- D-1 MEDIUM: compute_go does not assert the arm's world. R5 survives because the selftest fixture shares vectors across embedders,
  and raw_matrix zero-pads a 512-d qwen3 vector into 768 without a refusal. The code is correct as written (the literal "M-AF-g"). FIX: in compute_go,
  `if A["emb"] != "gemma" or A["corpus"] != "massive" or A["salt"] != 1: refuse(...)`, and give the ST-E2E fixture distinct qwen3 vectors.
- D-2 LOW: R2, R3, R6 and KM3 survive. These are redundant or descriptive guards. FIX: add an iso status case with sepBar 0.02 to ST-CAL (kills R2); accept the rest.
- D-3 LOW: "outcome lexists check off" and "need_km off" are killed only by a crash (TypeError), not by an assertion. Mode-x writes remain as
  a second guard. FIX: assert the refusal text in ST-E2E.
- D-4 LOW: the null runs at canonicalConfig(55) (acceptanceZ 0.0) while the build uses acceptanceZ 2.0. sepKway is stored before the gates,
  so the statistic is unaffected. Disclose the difference with GOB-K1.
- D-5 LOW: no time-order check of bar file vs build. Content equality of the 6-dp bar is the proof. FIX (optional): --run prints the mtimes
  of bar_g.json and run_manifest.json.

## Launch sequence (run-operator; R = Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/gemma-own-bar-run)

```
0. git worktree add R <merge commit of gemma-own-bar>; copy into R (sha256 = pins): intent_transfer_corpora_v1.db 487e0093…,
   intent_emb_qwen3.db 9e100e04…, intent_emb_gemma.db b187b82f…; plus the engine-side DBs as in intent-s1-run's layout
   (embeddings_cache.db, mmlu_pro_dataset_cache_v2.db, snapshots_frozen.db; copies, never the originals). export TAXOARENA_DATA_ROOT=R; cd R.
1. EXPORT: python tools/analysis/intent_s1_export.py --export M-AF-g   # table sha 6ce9bdf8…, EVAL rows 0
   python tools/analysis/gemma_own_bar.py --calibrate-plan             # PREFLIGHT build DB -> MATCHES; 9826/9826 vectors each
2. working copies of both emb DBs -> R/gemma_own_bar_work/cal_<ts>/ (sha256 = pin). Rule 7 W1-W5 per leg; ONE JVM; gradlew --stop after each.
3. NULL iso:    gradlew.bat gemmaOwnBar -PjvmThreads=12 -DgobArm=iso -DoutDir=R/experiment_results/gemma_own_bar/cal/iso
4. NULL qwen3:  gradlew.bat gemmaOwnBar -PjvmThreads=12 -DgobArm=qwen3_256 -DoutDir=R/experiment_results/gemma_own_bar/cal/null_qwen3_256
                -DgobBuildDb=R/intent_s1_build/m_af_g.db -DgobEmbDb=<qwen3 copy> -DgobEmbSha256=9e100e04fc91b137a075b8abedbc87d2b29a6dc2244c5f242b1c587004a4ee74
5. NULL gemma:  gradlew.bat gemmaOwnBar -PjvmThreads=12 -DsiteNullHeap=10g -DgobArm=gemma768 -DoutDir=R/experiment_results/gemma_own_bar/cal/null_gemma768
                -DgobBuildDb=R/intent_s1_build/m_af_g.db -DgobEmbDb=<gemma copy> -DgobEmbSha256=b187b82f90ce98376ba3ffac100157493fd8c5ee52dfa88f707738dde2acf512
   (heap: peak = 12 × 9,826 × 4,608 × 8 B = 4.35 GB at 12 threads, so the 6g default (budget 5.8 GB) holds it with little margin; 10g gives headroom. qwen3 256: 1.69 GB, default 6g)
6. BAR PIN: python tools/analysis/gemma_own_bar.py --calibrate --dry-run ; --calibrate   # bar_g.json written once; record its sha256
   and bar_g in the ops log BEFORE step 7; then --write-config ; --check-config
7. BUILD: backup to E:/TaxoArena_backup_<date>_gemma_own_bar + per-table hashes; --launch-plan steps 1-5 (gemma working copy, bootRun with
   -Dtaxoarena.embeddingCacheFile=<copy> -Dtaxoarena.embeddingCacheSourceSha256=b187b82f… -Dtaxoadapt.llm.embedding-model=embeddinggemma:latest
   -Dranking.db.path=R/experiment_results/gemma_own_bar/g_af/seed_42/ratings_intent_s1.db --args="--config experiment_configs/gemma_own_bar/g_af.toml");
   after exit re-hash pins; '[INTENT] fetched' 9826 / 1676.
8. READOUT (after C3): python tools/analysis/gemma_own_bar.py --run --dry-run --s1-data-root Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/intent-s1-run ;
   then --run (same flags) -> gob_outcome.txt (write-once). Outputs never committed; sha256 + backup to E:.
```

## Commands

```
git diff --numstat d6a8fc0c d9f43d19 -- build.gradle.kts src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt ; ... | grep -c '^-[^-]'   # 0, 0
git diff 25814d1a^ 25814d1a -- <f> | grep '^+[^+]'  vs  git diff d6a8fc0c d9f43d19 -- <f> | grep '^+[^+]'   # 31=31, 145=145 (2 comment lines differ)
git diff --name-only d6a8fc0c d9f43d19 | wc -l   # 5 ; -- src/main | wc -l  # 0
cmp <(tr -d '\r' < intent-s1-run/.../m_af_g/seed_42/diagnostics/config.toml) <(git show d9f43d19:experiment_configs/intent_s1/m_af_g.toml)  # IDENTICAL
TAXOARENA_DATA_ROOT=<intent-s1-run> python tools/analysis/gemma_own_bar.py --calibrate-plan ; --launch-plan   # print-only
python tools/analysis/gemma_own_bar.py --selftest ; --mutants        # 68 OK ; 38/38
./gradlew.bat test --offline                                          # 550, 2 known failures, 0 errors
scratchpad gob/rev_mut.py (R0 control SURVIVED = passes; R1-R6) ; gob/kmut.py, kmut2.py (KM1-3, K2/K3/K25/K19; control 6/6) ; gradlew --stop
sha256sum + ls --full-iso of intent-s1-run DBs before/after           # equal
```
