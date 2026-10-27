On main as 91ea66e: the reviewed files were merged by path from 4450dfd (12 paths). Reviewer-verified: `git diff --name-only 4450dfd 91ea66e` over the reviewed paths | wc -l = 0; on main `runner_pins()` gives blob 90cf17a7 / lf16 e0474092 / package 61eea0337e9ec8bc / instrument 876d01413318bd7b; `archv2_stage1_anchor_draw.py --selftest` passes 20/20.

## VERDICT: READY for the stage-1 re-draw ARCH-V2-STAGE1-ANCHOR-DRAW-2 at 4450dfd (branch archv2-pilot-k46)
Scope: the draw tool, stage1.py, common.py and the supply pins. The pilot's own READY is not ruled on here (judge_v2 `_base` pins are a known blocker). No blocker and no HIGH finding. One MEDIUM finding (the sha256-bytes pin kind for the stage-1 JSON, which is CRLF-fragile). It has to be settled before the registrar fills `pilot.py` STAGE1_RECORD_SHA256, not before the draw.

I did not write a review file. `docs/agents/reviews/` does not exist, and the established place is `docs/reviews/`, so this report comes back as text. I made zero calls and zero writes to the repo; `git status --short | wc -l` gives 0. `eval_view_REG.db` size and mtime are the same before and after (454049792 bytes, 2026-09-24 20:23:51.2227734).

**I did one dry-run, into my scratch dir only.** This was `archv2_stage1_anchor_draw.py --dry-run --eval-view <main view> --transcript <scratchpad>/dry_T.txt`. It exited 0 and wrote nothing of record. The scratch transcript's sha256 is 20288268cdc0a3d8…; that transcript contains an absolute path, so the operator's will differ.

**My own independent draw gives the same 7 anchors as the tool's dry-run.** I wrote a script (`scratchpad/indep.py`, immutable=1) that does its own SQL, digest, seed and PCG64 choice and does not import `design`. It agrees with the tool on every value:
- **Counts:** 3,492 EVAL items, 14 anchors. math 405, physics 387, chemistry 346, law 289, engineering 288, other 277, economics 250, psychology 239, business 234, health 204, biology 189, philosophy 148, computer science 128, history 108. No ties, at a group boundary or anywhere else.
- **counts_digest:** 08bc48d1a27b896074549128fbcf639b81da3addd9a85e893dbefe20d7cd8a4f
- **Seed:** 4030866750177695589. streams_digest 359096bcbe6c74b0f9be31941a94365614517de9e9302eb362df66dcdd9db082.
- **Groups and picks:** [math,physics]→math, [chemistry,law]→chemistry, [engineering,other]→other, [economics,psychology]→economics, [business,health]→health, [biology,philosophy]→philosophy, [computer science,history]→computer science.
- **Predicted 7 (sorted):** chemistry, computer science, economics, health, math, other, philosophy.

These are my prediction for the post-draw check; the tool's output of record is still the record.

## Pins the registrar should record
Hash kinds are named. The working tree is LF, so its bytes equal the LF rendering.

| file | blob (git hash-object = 4450dfd:path) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| `tools/analysis/archv2_stage1_anchor_draw.py` | 90cf17a7f17d4be32fda000ad95474957039be9b | e0474092c8708940 | 7408ea5585a854ba |
| `tools/analysis/archv2_pilot/stage1.py` | cfae76b06fb74919ee7b10b9dbad94817403a787 | 1e81e58fc7dfc4bb | b9291bf6a70e4802 |
| `tools/analysis/archv2_pilot/common.py` | 467d0efb4bc13b386f655a7980b830a78f44280f | e7dc47adc40fb081 | 9ef19dd64d9131c3 |
| `tools/analysis/archv2_pilot/supply.py` | 22fc9a059f8082202579cf1a60999e200764a1eb | f449b422b3475432 | ac1b2105e6397ce0 |
| `tools/analysis/archv2_pilot/pilot.py` (context only) | c713d79ee876bc879b5149e03090717a20c2f1cd | a2e1c6fde9ba76c6 | d84460b930d37142 |
| `tools/analysis/archv2_arena/design.py` (unchanged since 2296877, and = main) | 4959cb525c8d07a26d19358c3f98342d5b28b3d2 | becd63768eedb8fc | – |
| `tools/analysis/archv2_arena/streams.py` (unchanged, and = main) | 30c23f9700a1309cda059c76bfe6fcbc6c41d64b | 315a30993d340650 | – |

Other pins:
- package_lf16 61eea0337e9ec8bc
- frozen instrument_lf16 876d01413318bd7b
- eval_view sha256-bytes e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369
- pool pv2_41dbd3dbcd399df0: 3,400 components, 3,492 items
- master "ARCHV2-STAGE1-ANCHORS-2:e2623b4b69e664a9f222abc8b1121dc19d92cceb", stream "stage1-anchors", seed 4030866750177695589

After the run, the registrar should check that the JSON's `runner` block equals the CLI blob, package lf16 and instrument lf16 above. If the tool is run from main after the merge, the merge must not change these files.

## Per-claim table
| # | claim | result | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1a | common.py pins = record | CONFIRMED | `indep.py` on the view of record (immutable=1): full-file sha256, meta, pool rows | sha e35b7518…5e369 = pin. meta.seed 'ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2' = SPLIT_SEED. Pools: ('pv2_41dbd3dbcd399df0','mmlu-pro-v2',3400,{"mmlu-pro-v2":3492}) and ('pv2_1575de61bb20e977','all corpora + mc6-2026-09-11',5642,{…mc6:6153}). All match the R4 record at L16193-16200. |
| 1b | pool_of reads both schemas | CONFIRMED | real view has `n_items_by_scope` (PRAGMA). Dry-run found exactly 1 row for mmlu-pro-v2. Supply dry-run read the merged scope, mc6 = 6153. Selftest "pool_of reads…" covers the old `n_items` schema in memory. | 3492 / 6153 = meta |
| 1c | refuses a view whose meta seed ≠ split seed | PARTLY | `common.py` L95-97: the guard fires only when expect_sha == EVAL_VIEW_SHA256. The pinned bytes already fix the seed, so it can never fire on the record path. `grep -c "meta seed" selftest.py` = 0, so no selftest covers it. | redundant, untested (LOW-1) |
| 1d | SPLIT1_* kept for disclosure only | CONFIRMED | grep across `archv2_pilot`, `archv2_pilot_k46.py`, the draw CLI and supply CLI: 7c284b15 / 6f78 / 4cce / SPLIT1_ appear only in docstrings and the L45-47 definitions. No code reads them. | – |
| 2a | REGISTRATION / MASTER as registered | CONFIRMED | `stage1.py` L36-37 vs `judge_v2_program.md` L16200 | exact strings |
| 2b | draw() refuses MASTER_1 | CONFIRMED | L52-53. Live: `--master ARCHV2-STAGE1-ANCHORS-1:…` exits 1 at the CLI record guard. Selftest check "the first draw's master is never reused" covers draw() directly. | – |
| 2c | rule and stream unchanged | CONFIRMED | `git diff fb3a893 4450dfd -- stage1.py`: only the constants, the MASTER_1 guard, runner_pins and the record fields change. `groups_of` and `draw` logic are untouched. `git diff 2296877 4450dfd --stat -- tools/analysis/archv2_arena/` is empty. `choose_strata` (`design.py` L71) sorts (-n, name), `array_split` into 7, one `rng.choice` per group, as in the ruling at L15985-15994. | – |
| 2d | output carries runner and split_of_record | CONFIRMED | `make_record` L90. The dry-run printed the runner dict; selftest "the record pins the RUNNER". | blob 90cf17a7 / lf16 e0474092 / pkg 61eea033 / instr 876d0141 |
| 3a | --transcript is write-once | CONFIRMED | Second dry-run with the same transcript path: "[CHECK] … exists: a transcript is written once", exit 1, before any read. `report.write_once` uses mode "x" and `newline="\n"`, so the file is LF (`file` shows ASCII with no CRLF). | – |
| 3b | header prints pins | CONFIRMED | dry-run lines 1-4: registration, master, split label, runner, instrument, package, view sha "(= the pinned sha)", meta seed, pool | – |
| 3c | proposed paths | ACCEPTABLE | `git check-ignore` reports none of the 3 paths ignored. `experiment_results/archv2/stage1_anchor_draw_2` does not exist yet. `find experiment_results -name "archv2_stage1_anchors_2*" \| wc -l` = 0. Mirrors the first draw's committed layout. | directory must be created first (LOW-2) |
| 4a | stage-1 selftest 20/20, supply 26/26, python and -O | CONFIRMED | 4 runs, all exit 0. "20 checks, 0 failed" ×2 and "26 checks, 0 failed" ×2. `grep -c PASS` = 20 / 26. | exact |
| 4b | U witness is real | CONFIRMED | `scratchpad/uwit.py` rebuilt the fixture. The U item_id is in the split's `excluded_u` (1 row) with 0 side rows. The check needs nc ≥ 1 in the corpus. `views.build_view` refuses a side-less item that is not in `excluded_u`, so absence from the views comes from the U skip, not from a missing row. | nc 1, eval 0, gen 0, side 0 |
| 4c | fixture changes weaken nothing | CONFIRMED for stage1/supply; UNDETERMINED for the "all" part (not run; needs the judge_v2 re-pin, out of scope) | Reversed options went 3→8 per category and reference coverage 1/2→2/3. Neither changes item membership or counts, so no stage-1 or supply check depends on them. They reach only `selftest.py` L394 ("the fixture schedules excluded matches (MIXED referenced)…", predicate `len(plan.expected)>0` unchanged) and L740 (K5 MIXED projection). No check predicate was relaxed. The old record-mode sha-mismatch refusal was replaced by "not pinned yet" (LOW-3). | – |
| 5 | instrument, lint, package, pin table | CONFIRMED | `python -c` on `check_instrument()` / `package_lf16()`. `lint_opens.py --root .` exits 0: "240 .py files…; 0 finding(s); 10 allowlisted". `git hash-object` plus sha256 of `git show 4450dfd:<path>` for the table above. | 876d01413318bd7b / 61eea0337e9ec8bc / e7dc47ad, 1e81e58f, f449b422, e0474092 all sha256-lf16, match to the digit |
| 6 | hunt | see below | – | – |

**Hunt (claim 6):**
- **Could the draw read something other than the view of record?** Only through `--eval-view` or `TAXOARENA_DATA_ROOT`. Both still go through `open_eval` → `ro.open_ro(expect_sha256=e35b…, require_sealed)`, and the pool id is also required, so no other view can be read.
- **Could it depend on RNG state other than the master?** No. `Streams.np` builds a fresh `Generator(PCG64(seed))`, there is no global RNG, and `choose_strata` sorts its input, so dict order does not matter.
- **Could it be run twice silently?** A record run to a second `--out` path is not blocked, because write-once works per path. The output has no timestamp and is a pure function of the view, master and code, so a second run is byte-identical and cannot fork the draw. That is benign. The first draw's file cannot be read as the re-draw: `verify()` needs REGISTRATION ARCH-V2-STAGE1-ANCHOR-DRAW-2.
- **Does the pilot refuse a record run until the stage-1 draw is pinned?** Yes, in substance. The only callers of `make_plan` are `archv2_pilot_k46.py` L112 and `outcome.py` L128 (grep). `make_plan` always calls `check_stage1_file` (`pilot.py` L655), which refuses in record mode while STAGE1_RECORD_SHA256 or STAGE1_ANCHORS_OF_RECORD is None (L242-244). The anchors are compared as a tuple at L658.

## Defects
- **MEDIUM-1 (pin kind for the stage-1 JSON; fix before the post-draw pin, not a draw blocker).** `check_stage1_file` compares the file's raw-bytes sha256. System `core.autocrlf=true` and there is no `.gitattributes`. Evidence: the first record in this worktree checkout is sha256 680ab4978a9e1410… with 98 CRLF. The pinned 08cdff0e… is correct only in main, where the file was written LF.
  - **Consequence:** the re-draw's pin will refuse in any fresh checkout, or after any re-checkout of main.
  - **Fix:** the registrar records the pin as sha256-lf (the LF bytes the tool writes) plus the blob, with crlf16 beside them. The engine-coder then either makes `check_stage1_file` hash LF-normalised bytes or adds a `.gitattributes` `-text`/`eol=lf` rule for `experiment_results/archv2/**/*.json`.
- **LOW-1:** the meta-seed guard in `open_view` is redundant under the sha pin and untested (0 selftest hits). It is harmless. Fix: a mutant selftest (a DEV view with the pinned sha monkeypatched) or a comment calling it defence in depth.
- **LOW-2:** `write_once` refuses when the directory is missing, and the launch sequence in the CLI docstring does not create it. Both files share the directory, so the record run fails closed with no partial record. Fix: the operator runs `mkdir -p experiment_results/archv2/stage1_anchor_draw_2` before the dry-run.
- **LOW-3:** when a run refuses, the transcript is still written from `finally`, but it omits the refusal message: the SystemExit text goes to stderr only. It also contains no trailing "TRANSCRIPT" line (by design). Fix: catch SystemExit in `main`, append its text to the lines, then re-raise.
- **LOW-4:** there is no longer any record-mode sha-mismatch selftest (replaced by "not pinned yet"). The "not pinned yet" check will fail once the pins are filled, so the pin commit must add the mismatch test back.
- **LOW-5:** some text is stale but bracketed, which is acceptable under insertion-only:
  - the draw CLI docstring L5-6 still names split 1's pool and master, superseded by the L20-27 bracket;
  - the supply CLI's `--only-anchors` example still points to `experiment_configs/archv2_stage1_anchors.json`;
  - KIND is still "archv2-stage1-anchor-draw-1" (verify keys on REGISTRATION, so it is safe).

## Launch sequence for the operator (unchanged from the tool, with LOW-2)
1. `mkdir -p experiment_results/archv2/stage1_anchor_draw_2`
2. `python tools/analysis/archv2_stage1_anchor_draw.py --dry-run --transcript experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2_dryrun.txt`, then commit the transcript.
3. Once: `python tools/analysis/archv2_stage1_anchor_draw.py --out experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json --transcript experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2_run.txt`
4. Post-draw: the 7 anchors must equal the predicted 7 and counts_digest must be 08bc48d1….

Run steps 2 and 3 from a checkout whose DATA_ROOT resolves to main's `data_v2`, or pass `--eval-view`. The worktree has no `data_v2/REG_ARCHV2-SPLIT-2_*` directory.

Scripts are in the scratchpad (C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\):
- `indep.py` (independent draw)
- `uwit.py` (U witness)
- `dry_T.txt` (dry-run transcript)
- `s1.txt`, `s1-O.txt`, `sup.txt`, `sup-O.txt`, `lint.txt`
