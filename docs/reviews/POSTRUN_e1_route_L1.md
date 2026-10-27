# POSTRUN E1-ROUTE L0/L1/L2 (operator logs a96c7ae6): C1-C5 scored by the reviewer

Adversarial-reviewer, 2026-10-02. Zero calls; no JVM, no Gradle; every DB read `mode=ro&immutable=1` or from a scratch copy.
Registration: prog L22182-L22206 (heading "## Registered 2026-09-30 (before any code or call) — E1-ROUTE: ..."). Gate review:
READY_e1_route2.md (29e19199). Launcher at main = blob:ba865deb (LF; `git hash-object` and the LF-normalised sha1 agree) = the
READY pin; the 3 src/main files, the test, build.gradle.kts and the L1 TOML = the READY's blobs (2e2b125e, 3a544b1d, b7559c73,
a8d74266, 11235f68, 073a7ddf; HEAD and working tree equal). L1's run_manifest: commit bcd4a88f, dirty_src false.

## VERDICT

- **E1-ROUTE: C1 HELD, C2 HELD, C3 HELD (the vmfMu reading supplied by this review, not by the run; see D-PR-1), C4 HELD,
  C5 HELD (4 of 4 KILLED, re-run here). F1 NOT fired. P6 (wall <= 10 min) HELD.** VALID for the record.
- **E1 N-raw / N-card: MAY LAUNCH** under READY_e1_route2's conditional READY (E1-ROUTE C1-C5 HELD: now met; C-E1R-4: E1
  configs merged 2b6591bb, blobs edace9f9 / 67bcdc2b, outputDirs absent on disk), subject to C-PR-1..C-PR-3 below.

## Per-claim table (deciding claims)

| # | claim (operator / criterion) | mine | status | sev |
|---|---|---|---|---|
| 1 | selftest 15/15; dry-run passed | main selftest re-run: 15 / 15; dry-run rc 0 in operator.log (all checks printed, nothing copied) | CONFIRMED | - |
| 2 | C1 PIN-BEFORE | operator ran it in the selftest fixture only. My real leg: one-byte XOR mutant of a copy of the L1 scratch copy, `--dry-run`: `REFUSED: (i) the registrar's pin check failed before any copy or launch` (sha ac2d25fd.. != 53d1540a..), rc 2; java PIDs before [], after 0; e1_route_work dirs 1 before, 1 after (no working file). Unmutated copy ADMITTED = the L1 leg itself ((i) and (ii) lines) | HELD | - |
| 3 | L1 rc 0, "P and DIR unchanged" | launcher (v) line present; my re-hash now: all 9 members + the scratch copy equal the pins (main 52229e1e, nomic src 53d1540a, gemma src 3e9ce577, 4 DIR files 53d1540a / 90754dfd / 28f2e3a4 / 24820836, frozen 3f7f5e9a, scratch 53d1540a); sidecars beside P = **0** (count, `ls ... \| wc -l`); manifest embedding_cache_file = the working path | CONFIRMED | - |
| 4 | L2 refused 9/9 | second pass: 9 `== target` blocks (4 DIR files, 2 source DBs, main, frozen, the DIR itself), each `REFUSED: (iii) ... no launch`, rc 2; 15 blocks in total, first pass 6/6 refused too (disclosed mis-built paths, no launch) | CONFIRMED | - |
| 5 | C2 | L1: 9 files x 2 moments equal, 0 sidecars, manifest path = working path; L2 9 of 9 refused. Structural leg (g): the construction's cache writes landed in the working copy, not in P (row 7) | HELD | - |
| 6 | C3 "all 8,125 cached, 768 dims" | stronger than the log line: working copy embeddings 11,769 -> 11,769, 0 new keys, 0 changed vectors (whole run, not only phase 1) => misses 0; all 11,769 vectors length 768 in both the arm file and the copy | CONFIRMED | - |
| 7 | queries 8,299 -> 10,718; copy not of record | 10,718 - 8,299 = 2,419 new ids, 0 lost, 0 source rows modified, 0 new rows without an embedding; the 2,419 = exactly the tree's TRAIN members absent from the arm's queries table (set equality, 8,125 members). The copy is R1 (vi)'s per-run throwaway under experiment_results/e1_route_work, not in P, untracked: growth EXPECTED (construction-writes-cache-DBs) | CONFIRMED | - |
| 8 | C3 vmfMu cos "NOT printed" | true: the construction path has no [EMB-GUARD] (it lives in the FLAT readers). Computed read-only with `embedder_guard.guard_file` on snapshot 20261002_033703 (7 nodes, 2 split sites n00000001 / n00000005, sliceDim 256): working copy **min 1.0000** (8,125 / 8,125 ids, raw dims {768}); the pinned nomic_raw arm file **min 0.9999** (5,706 / 8,125 ids join: the 2,419 of row 7); wrong-embedder control (qwen3 DB of record) min 0.0104 -> REFUSE (discriminator) | HELD (reviewer read) | MEDIUM (D-PR-1) |
| 9 | C3 manifest source sha = pin | run_manifest embedding_cache_source_sha256 = 53d1540a...; true by construction (C-E1R-6), proves forwarding | HELD | - |
| 10 | C4 | merge 96d6ca1e src/main diff = 3 declared files (count 3); EmbeddingCacheManifestTest 4/4 executed, 0 skipped: taken from READY_e1_route2 D7 (artefacts; not re-run: no Gradle in main); positive branch now executed (keys present in L1's manifest) | HELD | - |
| 11 | C5 | my re-run on a scratch copy of tools/analysis (control R0 = 14/15, the 1 failure environmental: L1 TOML resolved off ROOT): R1 pin check removed 13/15, R2 re-hash removed 12/15, R3 target-in-P removed 13/15, R4 JVM given the DIR path 7/15: 4 of 4 KILLED; bytes restored (equal) | HELD | - |
| 12 | 3 DB hashes unchanged | my sha256: 52229e1e / 3e9ce577 / 53d1540a | CONFIRMED | - |
| 13 | leftover JVMs killed by PID | 48952 (Kotlin daemon), 50100 (Gradle daemon), both absent from "before: []"; kill by PID (rule); `gradlew.bat` not found = invoked without `.\`/path; java.exe now 0 | CONFIRMED | LOW (D-PR-4) |
| 14 | P6 wall | launch 03:36:05, JVM exit by 03:37:35 (manifest duration 53.5 s) | HELD | - |

## Defects and conditions

- **D-PR-1 (MEDIUM, registration wording).** C3 names "the vmfMu guard prints" in L1, but no guard runs on the construction
  path; the run cannot satisfy that clause as written. Scored HELD on this review's read-only reading (row 8). Fix: the registrar
  brackets C3's first check as "reviewer's embedder_guard.guard_file reading on the L1 snapshot" for L1 and for E1; E1's FLAT
  readout prints [EMB-GUARD] itself (embedding_guard_flat).
- **C-PR-1 (MEDIUM, operator, before any pool reader).** L1 left an 8,272 B `-wal` (2 frames) beside
  mmlu_pro_dataset_cache_v2.db (not in P): it rewrites only reserved_pool_meta's p2dca row timestamp (1789824498957 ->
  1790905001001; every other table identical by content hash). `pool_guard.open_ro` REFUSES on a non-empty -wal, so every
  pool reader (pool_guard --pool, FLAT dry-runs) refuses until the data-steward checkpoints it. Do not delete it. E1 builds will
  write it again (expected); hand the checkpoint to the steward after E1, before the FLAT readout.
- **C-PR-2 (LOW).** The L1 working copy keeps a 4.14 MB uncheckpointed -wal; anyone reading it must copy db + wal (an
  immutable=1 read hides the tail; pool_guard refuses). Keep the copy as L1 evidence; never use it as an arm input.
- **C-PR-3 (LOW, E1).** L1 exercised nomic_raw only; N-card's file-name resolution (`__card` twin) runs first in E1. Its own
  (v) re-hash is its detector (Support (e)); a PIN BREACH there is C2's class, scored, never cleaned.
- **D-PR-4 (LOW).** Hygiene: the dry-run and L2 legs used the real nomic_raw DIR file as "DIR under test" (Python hash-read,
  no copy, no launch; hashes unchanged), against the registration's "proof legs never point the launcher at a pinned file".
  Use `--dir-file <scratch copy>` in such legs. Run `.\gradlew.bat --stop` from the repo root after each E1 build.
- **Note.** L1 appended snapshot 20261002_033703_Headless_Run_Auto_ge to snapshots.db (not in P; expected); E1 adds two more.

## Commands (bash; R = repo root, S = scratchpad)

```
sha256sum R/{embeddings_cache.db,embeddings_cache_*_latest.db,snapshots_frozen.db} R/experiment_results/embedder_cross/*.db S/e1l1/*.db
ls R/embeddings_cache.db-* R/embeddings_cache_*_latest.db-* R/snapshots_frozen.db-* R/experiment_results/embedder_cross/*.db-* | wc -l   # 0
cp work copy db + wal -> S/rv; python S/rv/db.py      # emb 11769/11769, 0 new, 0 changed; queries 8299 -> 10718 (+2419, 0 lost/modified)
python S/rv/ids.py                                    # new ids == TRAIN members missing from the arm (2419, set equality)
python S/rv/vmf.py                                    # EMB-GUARD: copy 1.0000, arm 0.9999, qwen3 control 0.0104 REFUSE
python tools/analysis/e1_route_launch.py --selftest   # 15/15
python tools/analysis/e1_route_launch.py --arm nomic_raw --config experiment_configs/e1_route/L1_short_af_clean_s42.toml \
   --dir-file S/rv/mut/<one-byte mutant> --dry-run    # REFUSED (i), rc 2, 0 java, 0 new work dir
python S/rv/mut.py                                    # R0 14/15; R1 13, R2 12, R3 13, R4 7 -> 4/4 KILLED; restored True
grep -c '^== target' L2_refusals.log                  # 15 (6 first pass + 9 second)
cp mmlu_pro_dataset_cache_v2.db{,-wal} -> S; python S/rv/mm.py; python S/rv/mm2.py   # WAL frames 181405,182314; reserved_pool_meta row diff only
git diff --name-only 96d6ca1e^1 96d6ca1e -- src/main | wc -l                         # 3
git rev-parse HEAD:<f> / git hash-object <f> for the 6 merged files                 # = READY pins
```
