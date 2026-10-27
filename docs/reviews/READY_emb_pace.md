# READY_emb_pace — delta review of emb-pace f0dda20 (base 6885f92)

Reviewer: adversarial-reviewer, 2026-09-30. Zero judge calls. Local embeddings: the `--dry-run` transport preflight only
(3 x 20 parity texts + 3 x 500 timed-probe texts). No `--embed --go`. Delta = `git diff 6885f92..f0dda20` (3 files, 195+/10-);
main 7ea9ec1 touches none of the three files since 6885f92 (count 0), so a merge by path is clean.

## VERDICT

- **MERGEABLE** (f0dda20, by path: `tools/analysis/embedder_arms.py`, `tools/analysis/embedder_cross_flat.py`,
  `tools/analysis/intent_transfer_s0.py`).
- **READY for the three `--embed <e> --go` runs (qwen3, nomic, gemma), serial, under conditions C-EP-1..C-EP-4.**

## PINS (reviewed blobs; LF of record = `git rev-parse f0dda20:<path>` = `git hash-object` of the worktree file; worktree is LF)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/embedder_arms.py | 2073d1315981a30464037913b85ce2bf8838aa00 | 82836509285bde16 | 401d5ce99549532e |
| tools/analysis/intent_transfer_s0.py | f662ceb19738f515972871f5963f5dcfc764a271 | 0c71d9dd1bb37f17 | 01ac56bfdac49724 |
| tools/analysis/embedder_cross_flat.py | 7868e8589fee107b15d3c535966b840cd648f771 | 97283df70012e7d4 | d87e0234dd451a0f |

IMPORT_PINS in embedder_cross_flat (2073d131 / 82836509285bde16) = the embedder_arms row above: CONFIRMED.

## PER-CLAIM TABLE (deciding claims)

| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| 1 | WSAENOBUFS 400 is transient, same bounded whole-batch retry (5 retries, refuse after) | CONFIRMED | `ollama_embed` L359-381: retry loop wraps only `client.post`; refuse at attempt 5 before any sleep; EA-PACE (a) ok; mutant "PACE WSAENOBUFS fatal" KILLED | - |
| 2 | retry never re-sends after a partial write | CONFIRMED | the loop is inside `ollama_embed`, which returns before `write_vectors` inserts anything (L657); a batch is committed whole (L664) or not at all (refuse -> `finally: con.close()` without commit) | - |
| 3 | a count or dimension mismatch is never retried | CONFIRMED | count check L382-384 after the loop -> refuse; dimension check L659-660 in `write_vectors` -> refuse; neither is in the retry path; suite mutant "CONN count mismatch retried" KILLED | - |
| 4 | no other HTTP error made transient | CONFIRMED (LOW caveat D-EP-1) | own OM2 (add "error" to TRANSIENT_BODY) KILLED by EA-CONN; but "10055" is a bare substring and ports 10000-65534 are now dynamic | LOW |
| 5 | absent flags: byte-identical, and the proof executes the new code | CONFIRMED | own script `inert.py`: old 6885f92 module vs new, same stub, one transient fault: DB sha256 805df342... both, rows hash e7ff2293aed4b90e both (100 rows), request sequence identical (5), sleeps [2.0] both, 0 TIME_WAIT probes; line trace: `if PACE_S > 0` executed 4x, `if TW_DRAIN is not None` 1x in the new leg. Builder's EA-PACE no-flag legs also discriminated by mutants "pause/drain without the flag" KILLED | - |
| 6 | pacing/drain bounded | CONFIRMED | drain capped at TW_MAX_S 600 s per retry (mutant "drain uncapped" KILLED); unreadable count -> one 600 s wait (own OM3 KILLED); worst case per batch 220 s + 5 x 600 s | - |
| 7 | `--pace-s/--tw-drain` only with `--embed`, values restored after | CONFIRMED | 3 suite mutants KILLED; selftest asserts `(PACE_S, TW_DRAIN) == (0.0, None)` after the run | - |
| 8 | IMPORT_PINS re-pin keeps d749347 (E0b embed outcome) reproducible | CONFIRMED | `e0b_embed_outcome.txt` L3-4 records script blob:f8581aab and embedder_arms blob:0546800f; `git rev-parse d749347:<both>` = exactly those, and d749347's IMPORT_PINS pins 0546800f: the recorded run reproduces from its own tree (worktree at d749347). At the new tip a rerun prints new pins = a new run, not a reproduction; a mixed checkout (new script, old arms) REFUSES (pin check L163-166): fail-closed. Non-error path of embedder_arms is byte-identical (claim 5) | - |
| 9 | the partial `intent_emb_qwen3.db` (sha 3ac9814e...) refuses to resume and must be discarded | CONFIRMED | my read-only look (`immutable=1`): sha256 3ac9814e7baf03b0..., 16,960 rows (530 batches x 32), all 4096-d, intent_meta pins embedder_arms 0546800f / script c5346ce2; `--embed qwen3` (no --go) at f0dda20 REFUSES "intent_meta mismatch on ['embedder_arms_blob_lf', 'script_blob_lf']", rc 1, sha unchanged; own OM1 (resume ignoring *_blob_lf) KILLED by ST-EMBED | - |
| 10 | selftests / mutants | CONFIRMED | EA selftest 101 PASSED; EA mutants 78/78 KILLED; intent selftest 136 PASSED (133 + 3); intent mutants 81/81 KILLED (78 + 3); own OM1-OM3 3/3 KILLED | - |
| 11 | dry-run transport preflight | CONFIRMED (with an empty scratch `--emb-dir`) | 3/3 PASS: qwen3 min 0.999196 (bar 0.998), nomic 1.000000, gemma 0.999995 (bar 0.9999); probes qwen3 51.7 t/s, nomic 221.5, gemma 151.5; total 29.1 min. With the default emb-dir the dry-run REFUSES on the partial file (C-EP-1). 5 DB file shas identical before/after | - |

## DEFECTS

- **D-EP-1 (LOW).** `TRANSIENT_BODY` holds the bare substring "10055". With the dynamic range now 10000-65534, a
  genuinely fatal 400/500 whose body names `127.0.0.1:10055` (or any id containing 10055) is retried 5x (220 s + drains)
  before refusing. Harm = delay only (bounded, nothing written). Fix: match "WSAENOBUFS" / "10055)" / "error 10055"
  only, or drop "10055" (the English body already matches "lacked sufficient buffer space"). Not blocking.
- **D-EP-2 (LOW, record).** The intent_s0 docstring says the operator "moves it aside" without saying where. Under
  `experiment_results/` a `*.db` is RE-INCLUDED by .gitignore L145 (`!experiment_results/**/*.db`, checked with
  `git check-ignore -v --no-index`): a 287 MB partial there becomes trackable. Fix: C-EP-1 below names the place.
- **D-EP-3 (LOW, forward).** EMBEDDER-CROSS-FLAT E1's READY must pin embedder_cross_flat blob:7868e858 and
  embedder_arms blob:2073d131 (not the E0b pins f8581aab / 0546800f).

## CONDITIONS for the three --go runs

- **C-EP-1 (BLOCKER until done) discard the partial by MOVE, never delete, never resume, never re-pin.** Before any
  qwen3 step: record `sha256sum intent_emb_qwen3.db` (= 3ac9814e7baf03b03e0eea9cd70f5c220323e8877608880c56b04bdcf1306181),
  confirm no `intent_emb_qwen3.db-journal/-wal/-shm`, then `mv` (same volume, a rename) to an incident folder OUTSIDE
  `experiment_results/`, e.g. `Z:\FAC\TUBerlin\THESIS\TaxoArena\_incident\intent_s0_qwen3_2026-09-30\intent_emb_qwen3.db`
  (ignored by .gitignore L58 `*.db`); re-hash at the new path (must equal), `ls` the old path (must be absent), and log
  both lines beside `embed_qwen3_go.log`. Then re-run `--dry-run` with the default emb-dir: it must print 3/3 PASS
  (it REFUSES while the partial sits in DATA_ROOT). Cost of discarding: 16,960 texts, ~5.5 min at 51.7 t/s.
- **C-EP-2 one heavy process.** The dry-run printed foreign `java.exe` PIDs 51256, 46248; `--go` refuses under them
  (as at bee8da3). The step WAITS; kill by PID only if they are the operator's own, never by image name.
- **C-EP-3 TIME_WAIT gate between runs.** Before each of the three launches, TIME_WAIT (Get-NetTCPConnection
  -State TimeWait count) < 20,000; serial, qwen3 -> nomic -> gemma (or any order), never concurrent.
- **C-EP-4 flags (recommended; DESCRIPTIVE sizing, see below):**
  `--embed qwen3 --go --pace-s 0.25 --tw-drain 20000`;
  `--embed nomic --go --pace-s 0.5 --tw-drain 20000`;
  `--embed gemma --go --pace-s 0.5 --tw-drain 20000`.

Sizing (one incident, so DESCRIPTIVE): the qwen3 run exhausted ~10.3k free ports (16,384 range minus 6,059 TIME_WAIT
at 02:47) at the probe's ~24 t/s, i.e. up to ~3.6 dials per text held 120 s. With 55,535 ports (`netsh int ipv4 show
dynamicport tcp`: start 10000, 55535) and ~6k baseline, ~49.5k free -> a sustained ceiling of ~115 texts/s; a 2x margin
is ~57 t/s. Batch 32: qwen3 0.62 s/batch (51.7 t/s) + 0.25 -> 37 t/s, +7.5 min; nomic 0.14 s + 0.5 -> 49 t/s,
+15 min; gemma 0.21 s + 0.5 -> 45 t/s, +15 min. Unpaced nomic (221 t/s) and gemma (152 t/s) exceed the ceiling.
`--tw-drain 20000` = 36% of the range, 3.3x the observed baseline, so it is reachable; it acts only after a transient
error. Pacing never enters intent_meta (vectors unchanged), so the flags may differ per embedder and per resume.

## MUTANTS (own; deciding paths)

- OM1 `check_meta` ignores `*_blob_lf` keys (partial file would resume) -> KILLED (ST-EMBED assert). Decisive.
- OM2 `TRANSIENT_BODY` += "error" (every 400 retried) -> KILLED (EA-CONN non-transient 400). Decisive.
- OM3 `drain_time_wait` without the None branch -> KILLED (TypeError). Decisive for boundedness.

## COMMANDS

```
git diff 6885f92..f0dda20 ; git diff --name-only 6885f92..main -- <3 files> | wc -l            # 0
cd .claude/worktrees/emb-pace
python tools/analysis/embedder_arms.py --selftest        # 101 PASSED
python tools/analysis/embedder_arms.py --mutants         # 78 of 78 KILLED
python tools/analysis/intent_transfer_s0.py --selftest   # 136 PASSED
python tools/analysis/intent_transfer_s0.py --mutants    # 81 of 81 KILLED
python <scratch>/own_mut.py                              # OM1-OM3 KILLED (MUTANTS tables replaced in-process)
python <scratch>/inert.py <scratch>/old/embedder_arms_old.py   # old vs new: sha 805df342 both; trace pace 4 / drain 1
git rev-parse f0dda20:<f>; git hash-object <f>; git show f0dda20:<f> | sha256sum; ... | sed 's/$/\r/' | sha256sum
git rev-parse d749347:tools/analysis/embedder_cross_flat.py d749347:tools/analysis/embedder_arms.py   # f8581aab, 0546800f
grep -n "blob" experiment_results/embedder_cross_flat/e0b_embed_outcome.txt                           # L3-4
python -c "sqlite3 file:intent_emb_qwen3.db?mode=ro&immutable=1: count, dims, intent_meta"            # 16960, 4096, 0546800f/c5346ce2
TAXOARENA_DATA_ROOT=<main> python tools/analysis/intent_transfer_s0.py --embed qwen3   # REFUSED mismatch, rc 1
TAXOARENA_DATA_ROOT=<main> python tools/analysis/intent_transfer_s0.py --dry-run       # REFUSED (partial in DATA_ROOT)
TAXOARENA_DATA_ROOT=<main> python tools/analysis/intent_transfer_s0.py --dry-run --emb-dir <scratch>/embdir   # 3/3 PASS
sha256sum embeddings_cache*.db intent_transfer_corpora_v1.db intent_emb_qwen3.db (before/after)       # unchanged
git check-ignore -v --no-index <candidate incident paths> ; netsh int ipv4 show dynamicport tcp
```
