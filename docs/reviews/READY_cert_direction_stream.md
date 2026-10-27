# READY review: CERT-DIRECTION-STREAM instrument (adversarial reviewer, zero calls, read-only)

Date 2026-09-23. Registration: docs/judge_v2_program.md L14758-L14792 (46889ea). Registrar's rulings 60ddf85 (L14843-L14865). Builds reviewed: f645271, then the delta 9176bbc (branch worktree-agent-add099a1f602d057a). Scratch: `scratchpad/cds_ready/` (equiv.py sha256-16 99551eab3efb53d2, mut.py cecd6762fdba5c24, fp.sh 6b87d5034463c642; outputs equiv_all.out e7cf10ebeb326345, mutants_reviewer.out e00c5c3443246a77, dryrun_w8.out 79d0cb388e232115).

## VERDICT

**NOT READY at blob:11ead7be86d89e12adfaf105e817cca6bb1b1e23**, because of ONE HIGH defect (D1). The outcome file cannot be used to recompute C3's two-stage percentile interval, and that interval is the statistic that decides P3. No mutant in the selftest pins it either: my mutant X4b collapses the stream dimension and survives. D1 is a fix to what the readout prints and to the selftest; it does not touch the arms. Everything else is CONFIRMED on real data: the equivalence to CERT holds bit for bit, C0 legs 1 and 2 reproduce to the digit (20 of 20 streams), and the seed path, the hygiene, the Support arithmetic and the runtime all check out. If the fix commit's diff touches only `readout` / `main_run` printing and `selftest`, a delta check is enough and the real-data evidence below carries over unchanged.

## Pins (kinds named; the gate checks the LF rendering)

| object | blob (git, LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| cert_direction_stream.py @9176bbc (reviewed final) | 11ead7be86d89e12adfaf105e817cca6bb1b1e23 | 6553d8857ca7a9e7 | 23390b2dc8f91724 |
| cert_direction_stream.py @f645271 (dry-run / equivalence build) | f6884ec387f9891efd207977b6d5bae24dc96ea1 | bd1e91bbc4472829 | (worktree LF) |
| cert_under_filter.py (imported, unedited, both commits) | f7d59019c3d65128687df46aebdcb798b43c3062 | 0db2026f17b559a1 | b144a7d4377acfd3 (main working tree) |
| CERT outcome of record b4b1688 | 91ad6fa8df9565a123b195e6997bb81b746142e2 | | |

Commands: `git rev-parse <c>:<path>`, `git show <c>:<path> | sha256sum`, `git show <c>:<path> | sed 's/$/\r/' | sha256sum`, `git hash-object`. `git show 9176bbc --name-only --format= | wc -l` = 1. The main checkout's CRLF CERT file hashes to blob f7d59019 after LF normalisation; the script's header also printed MATCH.

## Per-claim table

| # | claim | result | evidence (command / script) | got vs claimed |
|---|---|---|---|---|
| 1 | imports CERT unedited; the seed reaches arm_edges only as a keyword | CONFIRMED | whole-file grep `cub\.X(=|+=)`, `setattr`, `__dict__`, `vars(cub`: 0 hits; header EXECUTION WITNESS printed blob f7d59019 MATCH before and after the import | 0 assignments = 0 |
| 2 | the 22 arms are built as prepare()/run_arms() build them | CONFIRMED, real data | equiv.py: `cub.run_arms(S, 8)` compared with the builder's stream-42 arms | F_A and R_A_01..20 bit-identical 21 of 21; fixed-mode U = discovery U on 920 of 920 edges |
| 3 | SEED-PATH 1 / SEED-PATH 2 gates | CONFIRMED (the run); PARTLY (the dry-run, D2) | the dry-run printed SEED-PATH (1) on 920 edges; equiv.py: fingerprints distinct across 4 and across 17 streams for all 22 arms | in the dry-run, (2) is vacuous at 1 stream but printed "the knob moved" |
| 4 | load_real runs once in the parent; workers open nothing | CONFIRMED | the dry-run CONNECTION LOG shows the stack cache opened exactly once (immutable URI), 4 connects in the parent, 22 jobs with 0 new connections; the equiv runs show 3 connects and 88 + 374 jobs witnessed | 0 worker opens |
| 5 | selftest 43/43 (f645271) and 41/41 (9176bbc), plain and -O | CONFIRMED | selftest_plain/_O.out, selftest9176/-O.out, all exit 0; `sys.flags.optimize` printed as 0 / 1; fixture h = 5/7 | 43/43, 41/41 |
| 6 | builder mutants M1, M1b, M2a, M2b, M3, M4 killed | CONFIRMED | cds_build/mutants.out: each is killed by its specific message (SEED-PATH, h = 1/200, STREAMS, wilson) | 6 of 6 |
| 7 | my mutants (on 9176bbc, run in a scratch copy of tools/analysis; an unmutated control copy passes 41/41) | 18 of 24 KILLED | mut.py | see the mutant table |
| 8 | C0 leg 1: s = 42 reproduces the outcome of record to the digit | CONFIRMED, real data | `--dry-run --workers 8` (f645271, main checkout) and my own C1 arithmetic in equiv.py (my own d_a and my own default_rng(42) B 2000 bootstrap) | W_U 26, W_F 17, W_R 24.15 (all 20 draws `23 28 20 21 24 26 27 22 25 20 24 28 21 28 24 21 24 25 25 27` = record), Delta -7.15, SE 3.606, [-14.22, -0.08], percentile [-14.80, -0.65], per-anchor d_a = record's 13 values, n 752 / 13, HELD. Every field equal |
| 9 | C0 leg 2: the review's 20 streams reproduce | CONFIRMED, real data | equiv.py streams 1..20 through the builder's `build_streams` / `_stream_job`; compared with REVIEW_TABLE and with the review's own independent arm pickles `cert_post/arms_seed{s}_K20.pkl` | per-stream digit match 20 of 20; W_F 16-19; Delta -8.05 to -4.75; upper end >= 0 on 15 of 20; arm p values bit-equal 331,632 of 331,632 (21 arms x 752 edges x 21 streams incl. 42) |
| 10 | d3: s = 1..20 are the review's seeds (registrar's precision) | CONFIRMED | recompute_seed.py L133 `random.Random(int(os.environ.get('ARMSEED','42')))` in arm_table (F and R arms; U discovery stays at Random(42)); L252 names the pickle `arms_seed%s` from ARMSEED; pickles exist for 1..20 and 42; row 9 shows those pickles are bit-equal to the script's arms at seed = s | the review did not vary U; W_U does not enter Delta_W, so Delta, SE, lo and hi are identical (row 9) |
| 11 | no write anywhere except the one write-once outcome; CERT's verdict cannot move | CONFIRMED | whole-file grep of `open(`, `.write(`, `shutil`, `remove`: the only non-selftest write is `write_once(OUT)` with mode "x" (L807), after `check_unchanged` (L910; write at L912) and after the pre-existence refusal before computing; the CERT functions used are all readers (`run_arms` only in the selftest); CERT's OUT is never referenced | 1 write path |
| 12 | DBs untouched | CONFIRMED | fp.sh before, mid and after, across 3 real-data legs (dry-run, equiv 1-3+42, equiv 4-20): sha256-16 / size / mtime of x12 eb0bec2795f3e5a0, mmlu 4f65414f7625a1e7, snapshots 390c313e5a40e0a7, the two -wal files (0 bytes) and the -shm files. `sort -u` of before+after = 7 lines | unchanged |
| 13 | rule-7 reader state | CONFIRMED at launch | Win32_Process: no python process; one java.exe, PID 49416 = an idle GradleDaemon (started 11:35, 110 s CPU); no construction; free RAM 34.3 GB / 66.2 GB | see condition C3 |
| 14 | the 9176bbc delta changes only P1/P3 scoring, text and selftest | CONFIRMED | `git diff f645271 9176bbc`: hunks are the docstring d7 bracket, REGISTERED_BRANCHES (P1.CONFLICT and FALSIFIER.P1_CONFLICT removed), the new `p1_held` / `p3_score`, the readout P1/P3/falsifier, the header and the selftest. `_stream_job`, `build_streams`, `stream_stats`, `arm_rowsets`, `c0_check`, `check_seed_path`, `two_stage`, `main_dry` and `main_run` are untouched | the real-data equivalence carries over |
| 15 | ruling (1): P1 HELD iff 36 <= k < 90 | CONFIRMED | selftest asserts p1_held at 35/36/89/90 = F/T/T/F and runs the readout at k = 90, 89, 36, 35; mutant X8 (<= at 90) killed | - |
| 16 | ruling (3) d7: P3 on the PERCENTILE upper end | CONFIRMED in code; its value is unpinned and not recomputable (D1) | `p3_score` reads `ts["phi"]`, with `zhi` printed beside | - |
| 17 | Support re-derived (gate 8) | CONFIRMED | own script from the review's seed-42 pickle (752 edges / 13 anchors): sum d_e -7.1500, SE_iid 2.8892, Kish 57.989, ANOVA ICC 0.01117, DEFF 1.6365, n_eff 459.5, SE 3.6960, MDE 10.349 | registered: 2.889 / 57.99 / 0.0112 / 1.636 / 459.5 / 3.695 / 10.35. The printed n_eff 459.5 comes from the unrounded DEFF (752/1.636 = 459.66): immaterial. The ratio form is 3.606²/2.889² = 1.558 (registered 1.558). |DW| 7.15 is below the MDE 10.35, so the registration's DESCRIPTIVE-ONLY label is correct and non-vacuous |
| 18 | MC SE of h and the P5 stream count | CONFIRMED | own Wilson solver | sqrt(.21/200) = 0.0324 (registered 0.032); n* = 320 at p 0.30 (registered "about 320"), 381 at 0.50, 311 at 0.286 |
| 19 | runtime about 2.2 h at 8 workers | PARTLY (under-priced) | dry-run: 22 arms in 48.2 s wall at 8 workers, mean 15.0 s per arm; equiv at 8 workers, no other load: 88 arms in 179.1 s, mean 15.32 s per arm (13.94-17.84); equiv at 12 workers with my mutant harness running beside it: 374 arms in 588.3 s, mean 18.54 s per arm | projection at 8 workers: 4,400 x 15.32 / 8 = 8,426 s = 2.34 h (ideal packing); from the measured wall per stream, 44.8 s x 200 = 2.49 h; add about 15 s prepare and seconds of readout. At 12 workers: 34.6 s per stream (under load) x 200 = 1.92 h |
| 20 | RAM per worker | MEASURED | peak working set: workers 97-98 MB each (8 and 12 pids); parent 262 MB | 8 workers: about 1.05 GB total; 12 workers: about 1.45 GB |

## Mutant table (mine, on 9176bbc; `mut.py`, plain and -O; killed = nonzero exit with the stated message)

Harness note: my first pass reported 24 of 24 "KILLED". Every one of those was a FileNotFoundError: the scratch copy lacked src/main/kotlin/taxonomy/service/TaxonomyArenaService.kt, which CERT reads at import. Those kills were vacuous. I added the file, the unmutated control then passed 41/41, and the table below comes from the second pass. The builder's harness has no control either, but its logs show a specific refusal message for each kill, so its kills are real.

| mutant | result | message |
|---|---|---|
| X1 seed passed to the R arms only | KILLED | [SEED-PATH] U, F_A repeat across streams |
| X1b seed to F and R, U at 42 | KILLED | [SEED-PATH] U repeats |
| X2 reference stream counted twice in k | KILLED | h = 1/200 check got (2, 200) |
| X2b reference twice in the plan | KILLED | [STREAMS] 201 streams (a first version died on a NameError; rewritten; kill real) |
| X3 streams drawn with replacement | KILLED | [STREAMS] refused |
| X3b two-stage: anchors not resampled | KILLED | branches C3.TWO_STAGE_CROSSES_0 and P3.HELD never executed |
| X4a two-stage: reference stream only | KILLED | P3.HELD never executed |
| **X4b two-stage: anchors resampled from the stream-MEAN d_a (ignores the stream dimension)** | **SURVIVED** | D1 |
| X4c mixture SE without the between term | KILLED | P3.HELD never executed |
| X5a Wilson z 1.645 / X5b z 2.0 / X5c half-width z 1.645 | KILLED (3) | wilson(60,200) / half width |
| X6 C0 leg 2 cross counted as `hi > 0` | SURVIVED | D3 (no fixture hi == 0) |
| X7 C0 leg 1 ignored | KILLED | validity failure |
| X8 P1 inclusive at k = 90 | KILLED | p1_held edges |
| X9 two-stage percentile 95 not 97.5 | KILLED | P3.HELD / C3 branch |
| X10 DB fingerprint: size only / X11 sha only | SURVIVED (2) | D3 (the selftest only appends a byte) |
| X12 spawned-worker log unchecked | KILLED | non-empty log not refused |
| X13 held = hi <= 0 instead of the verdict | SURVIVED | D3 (no fixture hi == 0) |
| X14 wrongF read from U | KILLED | fixture regression pin |
| X15 SEED-PATH distinct check off | KILLED | F_A identical not refused |
| X16 between variance ddof 0 / X17 sd ddof 0 | SURVIVED (2) | D3 (reading d4 not pinned) |

## Defects

- **D1 HIGH — C3 / P3 cannot be recomputed and are not pinned.** The outcome's PER STREAM block (L902, the only per-stream print; whole-file grep) prints only `W_U W_F mean_W_R Delta_W SE lo hi verdict`. The two-stage replicates need each stream's 13 d_a values. The post-run review therefore cannot re-derive C3's percentile interval, which is the statistic that decides P3 (ruling (3)), except by rebuilding 200 streams in a second 2.5 h window. X4b survives, so the selftest does not pin it either. FIX: (a) print each stream's 13 d_a values in the PER STREAM line. They are multiples of 0.05, so `%.2f` is exact. Print the anchor order once. (b) Add a selftest pin: the two-stage percentile interval on a fixture whose streams differ in their d_a profile, with the expected (plo, phi) pinned, so that X4b is killed. This is a readout-only change; the delta READY checks that the diff leaves the arm path alone.
- **D2 MEDIUM — the dry-run's SEED-PATH (2) passes without checking.** At one stream the "distinct across streams" test is trivially true (1 == 1), yet the dry-run prints "(the knob moved in every arm build)". FIX: at one stream, print "(2) NOT TESTED at 1 stream". Better: build s = 1 in the dry-run too (about 45 s at 8 workers), run SEED-PATH (2) on 2 streams, and print C0 leg 2's s = 1 row against REVIEW_TABLE[1].
- **D3 LOW — gaps in the selftest (X6, X10/X11, X13, X16/X17).** Add these fixtures: a stream with hi == 0.0 exactly (it must count as crossing, and must not read HELD); a same-size rewrite of the DB with its mtime restored by os.utime (must refuse by sha), and a touch-only change (must refuse by mtime); a pinned sd / between value (ddof 1).
- **D4 LOW — cost under-priced.** The registration says about 2.2 h wall at 8 workers with a 2.5 h window. Measured: 2.34-2.49 h at 8 workers, which leaves no margin in a 2.5 h window. The run cannot resume.
- **D5 LOW — run location.** CERT's ROOT is derived from its own file. Run from the worktree, INPUT_DBS resolves to the worktree, where the x12 file is a tracked copy (same sha eb0bec27) and mmlu_pro_dataset_cache_v2.db and snapshots.db are absent. The run must be launched from the main checkout after a pathspec merge.
- **D6 LOW (process) — the builder's mutation harness wrote mutant files into the worktree's tools/analysis** (it removed them afterwards). Use a scratch copy with an unmutated control.

## Conditions (to apply at the D1-fix pins after the delta check)

- C1. Merge by pathspec, then launch from the main checkout: `python tools/analysis/cert_direction_stream.py --run --workers 8` (or 12). The header must print the new pins, CERT blob:f7d59019 / sha256-lf16:0db2026f17b559a1 MATCH (crlf b144a7d4377acfd3), the build pin 128baa007a44a219, and the `before:` lines eb0bec2795f3e5a0 / 4f65414f7625a1e7 / 390c313e5a40e0a7 with the sizes and mtimes above.
- C2. The outcome must print `per-stream digit match: 20 of 20`, C0 HELD, and s = 42 exactly as in row 8. Anything else is an instrument fault to investigate before any readout is read, because this review reproduced all 21 rows on the same data.
- C3. Rule-7 window of at least 3.0 h at 8 workers (or at least 2.5 h at 12 workers). The >= 12 GB free check applies; the run needs about 1.1-1.5 GB. No --dry-run, construction, pool_guard or foreign Gradle worker may run during the window; the idle GradleDaemon PID 49416 is to be handled by the orchestrator under W1-W5. Sharing the window with SPLIT-EXPOSURE-SENSITIVITY cell (f) needs its own RAM and CPU check: both are CPU-bound, and 12 + 8 workers on 24 cores stretches both runs.
- C4. `experiment_results/x12_crossdomain/cert_direction_stream_outcome.txt` is absent at review time (`ls`: No such file). It must still be absent at launch.

## Dry-run numbers (f645271, main checkout, --workers 8, 66 s total)

reserved_pool_id=p2dca21ab5f4ef3ae. G2: 6066/9142 (A), 5276/8352 (B). G1: U 920 / 809 / 26. Anchors: 14, Business removed, 13 remain, 752 established edges. SEED-PATH (1) holds on 920 edges. C0 leg 1: every field equals the record. 22 arm builds in 48.2 s wall, mean 15.0 s per arm. The script's own extrapolation is 18.3 CPU-h, 2.29 h at 8 workers (2.68 h as stream wall x 200). Peak working set per worker 97-98 MB. The stack cache was opened once; DB fingerprints unchanged.

## Projected runtime

8 workers: 2.34-2.49 h (measured on an otherwise idle machine). 12 workers: about 1.9 h (measured while my mutant harness ran beside it). Memory: parent 262 MB plus 98 MB per worker. The run is not resumable, so an interruption means a new window.
