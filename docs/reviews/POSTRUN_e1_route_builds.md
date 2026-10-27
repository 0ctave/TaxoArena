# POSTRUN E1 builds N-raw / N-card (EMBEDDER-CROSS-FLAT E1-minimal, via the E1-ROUTE launcher; operator logs db471f1f)

Adversarial-reviewer, 2026-10-02. Zero calls; no JVM, no Gradle; DBs read `mode=ro&immutable=1` or from scratch copies
(db + wal copied, sha256 of the originals equal before and after the copy). Registration: EMBEDDER-CROSS-FLAT prog
L21705-L21730 (heading "## Registered 2026-09-27 (before any code or call) — EMBEDDER-CROSS-FLAT: ...", E1-minimal line and
its C-E1R-4 bracket); route: E1-ROUTE (POSTRUN_e1_route_L1.md, C1-C5 HELD). Run commit c2468c2a, dirty_src false; between
96d6ca1e (the reviewed merge) and c2468c2a the only changed files in src/main, build.gradle.kts, the launcher, embedder_arms,
embedder_cross_flat and experiment_configs/e1_route are the two E1 configs (count 2), blob:edace9f9 / blob:67bcdc2b
(`git hash-object` of the working files = `git rev-parse c2468c2a:<path>`; the manifests' config_sha256 83a1e2af / 42d4b251
are the CRLF working renderings, LF sha 3e1373b3 / bd5200ef).

## VERDICT

- **N-raw: VALID** (build). **N-card: VALID** (build); its in-run JVM validation block (3,599 routed, Top-1 62.91%,
  NoMatchRate 1.31%) is BRACKETED by the 47 (below) and is not a registered readout.
- E1's registered criteria (FLAT C1 / C2 / L1 for N-raw at its own k; FILING paired McNemar on the 3,445; F-E1; P3, P4, P7)
  are **NOT YET SCORED**: no E1 readout exists (embedder_cross_flat.py L11 / L651: "E1 ... out of scope"). The builds are its
  inputs only.
- **The 47 void nothing registered**: all 47 are sentinel (unlinked, non-judgeable) pool ids; 0 of the 3,445 held-out and 0 of
  the 8,125 fit texts are missing from the card file.

## Per-claim table (deciding claims)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| 1 | both rc 0; protected hashes unchanged; no sidecars; no java | launcher (iv) rc 0 and (v) "P and the DIR file unchanged ... main cache per table" in both transcripts; my sha256 now: the 8 files = pins (52229e1e, 3e9ce577, 53d1540a, 3f7f5e9a, 28f2e3a4, 24820836, 53d1540a, 90754dfd); sidecars beside them **0** (count); java.exe 0 | CONFIRMED | - |
| 2 | witness: the opened cache | manifest embedding_cache_file = each run's working path; embedding_cache_source_sha256 = 53d1540a (raw) / 90754dfd (card) = pins; (i) and (ii) lines equal the pin | HELD | - |
| 3 | witness: vector length, misses | "All 8125 requested embeddings are already cached" + dimension check 768 in both; working copies: embeddings 11,769 -> 11,769 (raw), 11,687 -> 11,687 (card), 0 new, 0 changed => 0 Ollama embeddings | HELD | - |
| 4 | witness: vmfMu cosines (redone read-only, `embedder_guard.guard_file`, slice 256) | N-raw snapshot 20261002_035009 (148 nodes, 84 leaves, 64 sites): own working copy **min 0.9997** (n00000052, n=130), median 0.9999, 8,125/8,125 ids; pinned raw arm min 0.9971 (5,706/8,125 ids join). N-card snapshot 20261002_035237 (148 nodes, 77 leaves, 71 sites): own working copy **min 0.9999**, median 1.0000; pinned card arm min 0.9990 (5,706/8,125). Discriminator: cross-arm reads REFUSE (raw tree on card vectors min 0.9603; card tree on raw vectors min 0.9631) | HELD | - |
| 5 | construction | both FIXED-POINT certified=true (iteration 13 / 14), exit completed, 2 depth-1 nodes, 8,125 root-placed, train_size 8,230 / pool p2dca as af_clean_s42 | CONFIRMED | - |
| 6 | 47 "no vector in the card file" in N-card, 0 in raw | 47 log lines (count), all inside the post-construction "Routing 3599 test queries" block; NoMatchRate 0.013059 x 3,599 = 47.0 | CONFIRMED | - |
| 7 | the 47 diagnosis | p2dca's frozen file lists 3,599 ids, 154 sentinel (<= 0, UNLINKED_QUERY_ID_BASE - rowid; texts via mmlu_pro.id). The 47 missing texts = 47 distinct, **47 sentinel, 0 judgeable**; categories health 26, law 20, chemistry 1; sha256-16 of the sorted texts 48d53aea0a4c9536; ids in S/rv/miss47_ids.json. All 47 are present in the raw file | CONFIRMED | - |
| 8 | why the card lacks them | the card file was written over E0b's REGISTERED read set (provenance: vectors_written 11,687 = fit 8,125 ∪ held-out 3,445 ∪ keyed; data-steward bracket in the E0b-EMBED line), the raw file over the whole corpus (11,769). raw - card = 82 texts: 81 unlinked mmlu_pro rows (47 of them the sentinel pool ids, 34 outside the pool) + 1 eval-linked text outside fit ∪ held-out; card - raw = 0. The JVM refuses to embed a card text (correct, fail-closed: no card prefix / layer_norm on its route) | DESIGN, not a fault | - |
| 9 | corpus DB -wal (C-PR-1) now | see C-PB-1 | - | MEDIUM |

## Defects and conditions

- **B-PB-1 (bracket on N-card's in-run metrics; LOW).** Never quote N-card's JVM validation numbers (3,599 denominator, 47
  forced no-matches) or contrast them with N-raw's. They are not registered readouts. For any in-run comparison, restrict both
  arms to the 3,445 judgeable. Remedy for the 47: **none needed** for E1. Embedding them would create a new card file with a new
  pin and is not justified (sentinel ids never enter the arena or the 3,445).
- **C-PB-1 (MEDIUM, data-steward, before any pool reader / the E1 readout).** mmlu_pro_dataset_cache_v2.db: the main file was
  written (mtime 03:50:36: the N-raw build's p2dca reserved_pool_meta timestamp 1790905708265, checkpointed into the file),
  and an 8,272 B -wal remains (sha256-16 77dc05a4907a3d5f, written 03:50:54 by N-card: the same row, timestamp 1790905854354).
  Every other table is identical by content hash to the L1-time state (mmlu_pro ca216b53.., reserved_pool 0ed26484..,
  eval_question_link da91df8a.., active_reserved_pool 429f9373..). pool_guard.open_ro REFUSES on the non-empty -wal, so the
  steward checkpoints it (a write to a corpus DB; the steward's call). The drift touches a created_at value only, not the pool
  id or its rows.
- **C-PB-2 (MEDIUM, the E1 readout's builder).** Both pinned arm files' `queries` tables resolve only 5,706 of the 8,125 fit
  ids (the missing 2,419 rows exist only in the working copies, written by each build). flat_mix_mmlu.fit_set would REFUSE
  ("2419 fit-set ids have no queries row") on an arm file. That is fail-closed, but the E1 readout has to resolve id -> text
  from a source holding all 8,125 (main's queries, read-only, or the run's own snapshot texts) and read vectors from the pinned
  arm by text. It must never read a working copy as an arm input.
- **C-PB-3 (LOW).** Working copies keep 4.14 MB -wal files (both). Keep them as evidence; any read copies db + wal first.
- **Note.** snapshots.db gained 20261002_035009 and 20261002_035237 (not in P; expected).

## Next step

Data-steward: C-PB-1 checkpoint. Engine-coder: the E1 readout (FLAT C1 / C2 / L1 for N-raw at its own k, FILING paired McNemar
on the 3,445 against af_clean_s42; leaf count, root axis and ARI printed; [EMB-GUARD] printed per arm; C-PB-2). Then a READY,
then the readout run, with N-card SECONDARY. Registrar: record both builds VALID with B-PB-1.

## Commands (bash; R = repo root, S = scratchpad)

```
grep -c 'Routing query failed' R/experiment_results/e1_route/E1_ops_20261002/E1_nomic_{raw,card}_transcript.log   # 0 / 47
sha256sum <8 protected files>; ls <their -wal/-shm/-journal> | wc -l (0); tasklist java.exe | grep -c (0)
git diff --name-only 96d6ca1e c2468c2a -- src/main build.gradle.kts tools/analysis/{e1_route_launch,embedder_arms,embedder_cross_flat}.py experiment_configs/e1_route   # 2 configs
python S/rv/miss47.py     # 3,599 ids / 154 sentinel; 47 missing in card, 47 sentinel, 0 judgeable, 0 missing in raw
python S/rv/r82.py        # raw - card 82: 81 unlinked + 1 linked; card - raw 0
python S/rv/wc2.py        # embeddings 11769->11769 / 11687->11687, 0 new, 0 changed
python S/rv/vmf2.py       # own 0.9997 / 0.9999 ADMIT; arms 0.9971 / 0.9990; cross-arm 0.9603 / 0.9631 REFUSE
cp mmlu_pro_dataset_cache_v2.db{,-wal} -> S; python S/rv/mm2.py   # reserved_pool_meta p2dca timestamp only
```
