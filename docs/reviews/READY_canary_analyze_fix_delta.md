# READY (delta) — CANARY-ANALYZE-FIX fixes 5e9455b3 (canary-fix-2) and d6c54231 (canary-fix-3)

adversarial-reviewer, 2026-10-01, zero calls, HEAD 28b4032b. Delta = `git diff ad65d094..665a739a` (fix-2) and `665a739a..94b25a28`
(fix-3), plus regression at the current blobs. The prior READY ad65d094 (`READY_canary_analyze_fix_and_leaf.md`) is cited for everything
the delta does not touch. Post-fix changes to these files (CANARY-EPOCH2-RUNG: write-once mode "x", `ensure()`, `check_write_once`) were
reviewed in `READY_canary_epoch2_rung.md` (delta 3, 613da05); they are re-executed here, not re-derived.

## Verdict

**READY (with conditions C1-C3)** for `tools/analysis/canary_baseline.py` blob:71d3f308c9b19d452e2276a1f0bbb230efaefb25
(sha256-lf16 32236c62be50038c; sha256-crlf16 2fdda255921943b1 = the main working tree, which is what `script_hash()` prints there) and
`tools/analysis/canary_baseline_selftest.py` blob:abf72936422ddbf26a8f57eeb65f3af2078cdb59 (sha256-lf16 8efbb91f7c750cf4; sha256-crlf16
fa6294738786c4b7 = working tree). `git hash-object` on the working tree = the HEAD blob for both. ad65d094 blocker 1 and defects 2, 3, 4, 7, 8
are CLOSED. The selftest is not vacuous: 8 of 9 own mutants are killed. M7 survives (D1 below).

**Scope correction (the record's wording is stale).** "Before the fix gates epoch 2" no longer applies. Epoch 2 has already run with these
exact blobs. READY_canary_epoch2_rung delta 3 pinned blob:71d3f308, the post-run review is `2026-09-24_canary_epoch2_post.md`, and
`canary_epoch2_outcome.txt` is committed. Epoch 2 is read by `--analyze-epoch2`, not by `--analyze`. Phase B of ad65d094 was also executed
once already: d37a82f8 regenerated the epoch-1 outcome, changing 2 lines (`git diff --numstat 4178a7c6 d37a82f8` = 2/2), after d6c54231.
What this READY gates is any future v1 `--analyze` readout. It does NOT gate RP21: RP21 v1 epoch 3 needs new pass ids (`--pass`
choices are 1-4, L1808), so it is new code and needs its own READY. RP20 and RP19 do not import this instrument (not built), and the record
(item (5) in the span L22621-L22717) names only the two RP21 legs.

## Per-claim table (deciding claims)

| # | claim (commit) | verdict | reviewer's evidence vs claim | sev |
|---|---|---|---|---|
| 1 | fixture expects 296 / 4 with the convention asymmetry asserted (fix-2, ad65 blocker 1) | CONFIRMED | `[OK]` prints n=296, floor 0.088, A 34/300 = 0.113. Mutant M5 (B also drops non-terminated) KILLED | - |
| 2 | `write()` refuses OUT without an `ALARM STATE:` line and diverts to the partial file (fix-2, ad65 D2) | CONFIRMED | `[WRITE-GUARD] REFUSING` printed in the guard case. M1 (guard off), M8 (divert to OUT) and M9 (guard tests OUT_PARTIAL) all KILLED | - |
| 3 | rule (ii) at 3 dp; 0.1144 / 0.1146 pinned (fix-2, ad65 D3) | CONFIRMED | 9 unit cases pass. M2 (unrounded), M3 (`<` bar) and M4 (one convention suffices) KILLED | - |
| 4 | rule (ii) is decided under BOTH conventions **inside `analyze()`** | PARTLY | `alarm_state()` is pinned at unit level only. M7 (pass convention B's floor as both arguments) SURVIVES with 8/8 OK, although the `conv` fixture already discriminates: current code prints `ALARM STATE: UNDETERMINED` (A contested 21/150 = 0.140) and M7 would print NO ALARM. Not deciding on the record (epoch 1 has A = B, 0 bad rows) | MEDIUM |
| 5 | fix-3: the failure was Windows text mode (CRLF), not a state leak; fixture reads lines back | CONFIRMED | `lines_of()` uses universal newlines. The suite is green under `python` and `python -O` (8 `[OK]` each, rc 0) | - |
| 6 | fix-3: every case owns its state; the real outcome and partial are watched on existence + mtime + sha256 | CONFIRMED | `assert_owns` is called before `analyze()` and in each case. The real outcome, partial, epoch-2 outcome and pass-1/2 caches have identical sha256 + mtime before and after all runs (`cmp` of the two stamp files) | - |
| 7 | fix-3 touches only the selftest | CONFIRMED | `git show --stat d6c54231`: 1 file, 49+/5- | - |
| 8 | PHASE-B guard: `--analyze` cannot alter the epoch-1 outcome of record | CONFIRMED (by execution on a scratch copy) | `analyze()` was run at blob 71d3f308 on scratch copies of pass1/pass2 and of the CRLF outcome, with `install_db_guard()` and the EVAL DB read through the ro/immutable guard (size + mtime unchanged). Results: copy byte-identical, `[WRITE-ONCE]` refusal printed, no partial created, `ALARM STATE: NO ALARM`. The readout equals the record line for line except the header `script sha256[:16]` (1 line each way) | - |
| 9 | the epoch-1 deciding numbers | CONFIRMED to the digit | own script on the caches (immutable): A = B, contested 13/150 = 0.087, cross 13/150, all 26/300, 0 dropped. This matches outcome L27 | - |
| 10 | A9 `points_refusal` (fix-2, ad65 D8) | CONFIRMED | `--selftest` and `--selftest --level leaf` rc 0. 2x12 refuses, 5x12 clears, 2x46 clears | - |

## Defects (with fix)

- **D1 MEDIUM (M7 survivor; the selftest misses one deciding wire).** In `check_conventions_differ`, add
  `ensure(ls[find(ls, "ALARM (Stage 9 arm A") + 1] == "ALARM STATE: UNDETERMINED")`, with the comment "A contested 21/150 = 0.140 > 0.114
  while B is 13/146 = 0.089: rule (ii) needs both". This kills M7. It is not deciding for any recorded outcome. It binds before any new
  `--analyze` readout in which bad rows can occur.
- **D2 LOW (vacuous-by-construction check).** Since write-once, `check_idempotent` compares a file with itself: the second `analyze()` does
  not rewrite it. The docstring (item 6) says so. Either rename the check to "re-run leaves the file untouched" or drop it, because
  `check_write_once` already covers this. It must not be cited as an idempotence proof.
- **D3 LOW (degraded-path target).** Degraded readouts still open `OUT_PARTIAL` in mode "w". On main that file is the real untracked
  2026-09-22 pilot partial (sha256 f0ea2a3e85bbe779), so a degraded `--analyze` on the real tree would overwrite it. It is not of record, but
  to keep it, back it up or write `*_partial.<ts>.txt`.
- **D4 LOW.** The selftest's `finally` restores OUT, OUT_PARTIAL and EVAL_DB, but not `cb.cache_path` or `cb.freeze_set`. This is harmless
  for a single-process run. Restore them if the module is ever imported by another test.
- **D5 LOW.** `canary_baseline.py` L1154 `assert state in ALARM_STATES` and `leaf_selftest`'s bare `assert`s vanish under `-O`. This is the
  same class as READY_canary_epoch2_rung D5; convert them to explicit raises.
- **D6 LOW (record wording).** `script_hash()` hashes the on-disk file. On main that is the CRLF rendering (2fdda255921943b1), while the pin
  of record is LF (32236c62be50038c). A header sha read on main must be compared with the CRLF16 shown here.

## Conditions

- **C1.** Before the next `--analyze` readout of record: D1 is fixed and the selftest is re-run green under `python` and `python -O`. A delta
  review of the one added line suffices.
- **C2.** The PHASE-B hazard stands as procedure: never run `--analyze` against the real epoch-1 outcome as a test. Prove it on a scratch
  copy, as row 8 does. Mode "x" now makes a real run inert on OUT, but not on OUT_PARTIAL (D3).
- **C3.** RP21 (v1 epoch 3 and the v2 canary) is NOT covered by this READY. New pass ids and a new instrument need their own registration
  Support and READY.

## Own mutants (deciding paths; harness = scratch copies; canary_baseline loaded from scratch; selftest run against it)

M1 guard `if False and ...`: KILLED (decisive) · M2 alarm_state unrounded: KILLED (decisive) · M3 `<=` to `<`: KILLED · M4 `len(fs)>=1`:
KILLED (decisive) · M5 conv B drops bad_row: KILLED (decisive) · M6 write-once "x" to "w": KILLED (decisive) · M7 analyze passes conv B
twice: **SURVIVED** (decisive, D1) · M8 divert target OUT: KILLED · M9 guard tests OUT_PARTIAL: KILLED. Baseline harness green (8 OK).

## Commands

```
git show --stat fcd200ea 5e9455b3 d6c54231 ; git diff ad65d094 665a739a -- tools/analysis/ ; git diff 665a739a 94b25a28 -- tools/analysis/
git hash-object tools/analysis/canary_baseline*.py ; git rev-parse HEAD:<same>        # = 71d3f308 / abf72936
git show HEAD:<f> | sha256sum ; (sed 's/$/\r/') | sha256sum                           # lf16 / crlf16 above
python [-O] tools/analysis/canary_baseline_selftest.py                                 # rc 0, 8 [OK] each
python tools/analysis/canary_baseline.py --selftest-epoch2                             # rc 0, 41 of 41 branches
python tools/analysis/profile_reliability_interaction.py --selftest [--level leaf]     # rc 0 both
sha256sum + stat of canary_baseline_outcome{,_partial}.txt, canary_epoch2_outcome.txt, pass1/2.db before vs after: cmp identical
scratchpad/mut/mut.py, mut2.py (M1-M9); scratchpad/phaseb/pb.py (row 8); inline immutable recount (row 9)
git log -- experiment_results/x12_crossdomain/canary_baseline_outcome.txt ; git diff --numstat 4178a7c6 d37a82f8 -- <same>   # 2/2
```

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G2eTaTRL4d3ohsmSQnuwsE
