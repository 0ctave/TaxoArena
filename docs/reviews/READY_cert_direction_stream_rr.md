# READY delta review: CERT-DIRECTION-STREAM at 1c9c739 (adversarial reviewer, zero calls, read-only)

Date 2026-09-23. This review closes the findings of READY 751cf57 (docs/reviews/READY_cert_direction_stream.md, which found the build NOT READY at 9176bbc). Registration L14758-L14792 (46889ea); rulings 60ddf85 (L14843-L14865). Fix commit 1c9c739 on branch worktree-agent-add099a1f602d057a. Scratch `scratchpad/cds_ready/`: mut.py sha256-16 cecd6762fdba5c24; mutants_reviewer_1c9.out c578f80595af8d1c; dryrun1c9_w8.out 2963a4b46abd1fb0; selftest1c9.out 8fa0b9c5d66c5aec; selftest1c9-O.out eb698405adee69a3.

## VERDICT

**READY-WITH-CONDITIONS at blob:a4be06c34aa7df18b7e50db754309f9911d007e0** (tools/analysis/cert_direction_stream.py @1c9c739). D1, D2 and D3 of 751cf57 are closed. The arm, seed and statistic path is AST-identical to the build whose real-data equivalence 751cf57 proved: bit for bit against CERT's run_arms, the outcome of record b4b1688, and the review's 20 streams. That equivalence therefore carries over. The conditions are C1-C5 below. C3 (the window) is set by a new measurement and is stricter than the 3.0 h the coordinator proposed.

## Pins (kinds named; the gate checks the LF rendering)

| object | blob (git, LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| cert_direction_stream.py @1c9c739 (FINAL) | a4be06c34aa7df18b7e50db754309f9911d007e0 | b9164a0457affbd1 | 62f34cd56026ec0e |
| cert_under_filter.py (imported unedited; unchanged at 1c9c739) | f7d59019c3d65128687df46aebdcb798b43c3062 | 0db2026f17b559a1 | b144a7d4377acfd3 (main working tree) |
| systematic_budget.build source (CERT's check_build_pin) | - | LF source sha16 128baa007a44a219 | - |

Commands: `git rev-parse 1c9c739:<path>`; `git show 1c9c739:<path> | sha256sum`; `... | sed 's/$/\r/' | sha256sum`; the worktree's `git hash-object` = a4be06c3. `git show 1c9c739 --name-only --format= | wc -l` = 1. The dry-run header printed the LF identity blob a4be06c3 / b9164a0457affbd1 and CERT MATCH.

## Per-claim table (delta)

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | arm, seed and statistic functions source-identical to 9176bbc | CONFIRMED | my own `ast.dump` comparison of every top-level def and assignment, `git show 9176bbc:` vs `1c9c739:` (old.py / new.py) | 82 of 86 identical; CHANGED = check_seed_path, main_dry, main_run, selftest; ADDED = DRY_STREAMS, TS_PIN, _two_stage_fixture, d_a_text; REMOVED = none. Identical among them: _stream_job, build_streams, arm_rowsets, u_min, stream_stats, denominators, two_stage, dist, wilson, held_share, band, p1_held, p3_score, c0_check, readout, fingerprint, check_unchanged, check_worker_witness, write_once |
| 2 | check_seed_path changed in its message only | CONFIRMED | diff hunk @@-498: only the return string; `stuck` / `same` and the refusal are untouched | (2) prints NOT TESTED below 2 streams |
| 3 | D1: per-stream d_a printed, exact | CONFIRMED | main_run prints the anchor order plus `d_a_text(results[s])` in every PER STREAM line; d_a_text refuses a value that is not exact at %.2f. Each d_a = integer - (sum of 20 integers)/20 is a multiple of 0.05, so a refusal is impossible on real data (the dry-run printed s = 42's 13 d_a equal to the record's) | C3 is now recomputable from the outcome |
| 4 | D1: the two-stage fixture is pinned | CONFIRMED independently | own numpy reimplementation of the fixture formula and of the d5 RNG order (no import): plo -5.2000, phi +3.8500, point 0.4625, mixture SE 2.0926393495, between 2.9191394472, sd 1.7085489303; the stream-mean mutant gives [-0.5495, +0.9890] | equal to TS_PIN to printed precision |
| 5 | D3 fixtures (hi == 0; same-size rewrite with mtime restored; touch only; ddof pins; held = c1_verdict under the trigger) | CONFIRMED | selftest lines HI == 0, DB-CHANGED, TWO-STAGE PIN, HELD = c1_verdict | - |
| 6 | selftest 41/41 under python and -O | CONFIRMED | selftest1c9.out (optimize = 0) and selftest1c9-O.out (optimize = 1), both exit 0; control copy in scratch exit 0 | 41/41 |
| 7 | my mutants all killed | CONFIRMED | mut.py on a scratch copy of tools/analysis (unmutated control passes 41/41); `grep -c KILLED` = 24, `grep -c SURVIVED` = 0 | 24 of 24, plain and -O, each with its specific message. The 6 survivors at 9176bbc are now killed: X4b by the TS_PIN mismatch, X6 by the hi = 0.0 crossing check, X10 by the same-size rewrite, X11 by the touch-only change, X13 by held = c1_verdict, X16/X17 by the TS_PIN mismatch |
| 8 | the real-data --dry-run builds s = 1 and 42; s = 1 reads MATCH | CONFIRMED | `python tools/analysis/_ready_cds_1c9c739.py --dry-run --workers 8` in the main checkout (a temporary copy, blob a4be06c3; removed with its .pyc afterwards; `git status --short tools/ \| wc -l` = 0) | SEED-PATH (1) on 920 edges; (2) distinct on 2 streams for all 22 arms; C0 leg 1 every field = record (W_U 26, W_F 17, W_R 24.15, Delta -7.15, SE 3.606, [-14.22, -0.08], 752 / 13, HELD); s = 1: `19 24.00 -5.00 3.859 -12.56 +2.56 UNDETERMINED`, MATCH with the review; 44 jobs, 0 worker opens; the stack cache opened once (immutable URI) |
| 9 | DBs untouched | CONFIRMED | fp.sh before and after this dry-run (db_before2 / db_after2), also equal to 751cf57's db_before | x12 eb0bec2795f3e5a0, mmlu 4f65414f7625a1e7, snapshots 390c313e5a40e0a7; -wal files 0 bytes; -shm unchanged |
| 10 | rule-7 state at launch | CONFIRMED | Win32_Process: one transient python PID, gone at re-check; no java or Gradle process; FLIP-RESEED finished (6dca538) | - |

## Runtime and RAM (re-measured; this sets condition C3)

- The dry-run at 1c9c739, 8 workers: 44 arm builds, 61.2 s wall per stream, mean **20.1 s per arm**. The script extrapolates to 24.5 CPU-h, **3.07 h** ideal at 8 workers and **3.40 h** from wall x 200.
- 751cf57 measured, at 8 workers: 15.0 s per arm (dry-run) and 15.32 s per arm (88 arms), which projects to 2.34-2.49 h.
- The difference is machine load. During this leg a `find` process with 25,587 CPU-s of accumulated CPU time, plus IDE and docker processes, was present.
- The spread across legs is 15.0 to 20.1 s per arm, so an 8-worker run needs **2.3 to 3.4 h**.
- RAM per worker: 97-98 MB. Parent: 262 MB (751cf57).

## Conditions

- **C1.** Merge by pathspec. Launch from the MAIN checkout (not from the worktree: CERT's ROOT resolves the inputs from its own location): `python tools/analysis/cert_direction_stream.py --run --workers 8`. The header must print:
  - blob:a4be06c34aa7df18b7e50db754309f9911d007e0 / sha256-lf16:b9164a0457affbd1 (LF);
  - CERT MATCH f7d59019 / 0db2026f17b559a1;
  - build pin 128baa007a44a219;
  - `before:` eb0bec2795f3e5a0 / 4f65414f7625a1e7 / 390c313e5a40e0a7.
- **C2.** The outcome must read `per-stream digit match: 20 of 20` and C0 HELD, and s = 42 exactly as in row 8. Anything else is an instrument or environment fault: this review and 751cf57 reproduced all 21 rows on the same data.
- **C3. WINDOW.** At least **3.5 h at 8 workers**, or at least 3.0 h at 12 workers. The coordinator's 3.0 h at 8 workers is NOT sufficient on the machine as measured today (3.07-3.40 h). A 3.0 h window at 8 workers is admissible only if a --dry-run in the same window, immediately before the run, prints an extrapolation of at most 2.7 h (stream wall x 200). The run cannot resume. Rule 7 W1-W5 applies, with at least 12 GB free: the run needs about 1.1 GB at 8 workers and 1.45 GB at 12. No other CPU-heavy reader or construction may run in the window.
- **C4.** `experiment_results/x12_crossdomain/cert_direction_stream_outcome.txt` must still be absent at launch. It is absent now: `ls` returns No such file.
- **C5.** The post-run review recomputes C3 (plo, phi, mixture SE) and P1-P3 from the outcome's PER STREAM d_a lines alone, before any readout is recorded.

## Residual notes (LOW, no action required for the run)

- The d_a exactness `need` is evaluated after the 2.3-3.4 h of computation. It cannot fire on real data (the arithmetic is above), so this is noted only.
- The dry-run's `MEASURED` line now reports wall per stream, averaged over 2 streams including worker spawn. Its extrapolation depends on load and should be read beside C3.
