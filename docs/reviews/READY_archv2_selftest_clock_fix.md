# READY review: ARCHV2-SELFTEST-CLOCK-FIX (2026-09-26, adversarial reviewer; zero calls)

## Verdict

**READY. MERGEABLE, by path, `tools/analysis/archv2_pilot/selftest.py` only.** One MEDIUM defect (D1): the selftest has no discriminator for real-clock reads, so 3 of my 4 selftest-side mutants survive at 282/0. That is a follow-up item. It does not block this merge, because the change is correct and strictly better than the base. The worktree's modified `docs/agents/queue.json` is excluded by the by-path merge and should be DISCARDED along with the worktree (section 4).

Identity of the change (hash kinds named; the LF rendering is of record; the CRLF rendering is shown because the working trees differ):

| object | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| selftest.py BEFORE (3bee93b, = main HEAD 31d092e) | blob:82ee9cde74c196970b16d12a57d685bc21ef3e1d | 8e23ad5f15833b23 | 9e8649b7ff55845e (main's working tree) |
| selftest.py AFTER (43c047d6a9fd50ffde3797a2c9a4d3ea2dbb5337) | blob:34743f1ed2dd1b30dd2e097a4cb7660f0c1939c2 | bcaf589f8c9a755e | 02d1cdd8995f43e7 (worktree file) |
| archv2_pilot package (common.PACKAGE_FILES, 8 files) | n/a | 00bce6429d6dea64 at 3bee93b, at 43c047d and in the worktree | n/a |

Commands: `git rev-parse 43c047d:tools/analysis/archv2_pilot/selftest.py`; `git hash-object <worktree file>`; `git show <c>:<path> | sha256sum`; `git show <c>:<path> | sed 's/$/\r/' | sha256sum`. The package hash was recomputed in bash as common.package_lf16 computes it: rel + NUL + CRLF->LF bytes, over the 8 PACKAGE_FILES in order.

## Merge procedure (main checkout Z:\FAC\TUBerlin\THESIS\TaxoArena)

1. Preconditions:
   - `git status --porcelain tools/analysis/archv2_pilot/selftest.py` prints nothing.
   - `git rev-parse HEAD:tools/analysis/archv2_pilot/selftest.py` = 82ee9cde74c196970b16d12a57d685bc21ef3e1d.
   - `git diff --cached --name-only | wc -l` = 0, or only paths you own.
   - Main moved to 31d092e after the branch base. It touches 7 files and 0 under tools/, so a fast-forward is no longer possible and a by-path merge is the procedure.
2. `git checkout 43c047d6a9fd50ffde3797a2c9a4d3ea2dbb5337 -- tools/analysis/archv2_pilot/selftest.py`
3. `git commit -m "<msg>" -- tools/analysis/archv2_pilot/selftest.py`, pathspec only.
4. Verify:
   - `git rev-parse HEAD:tools/analysis/archv2_pilot/selftest.py` = 34743f1ed2dd1b30dd2e097a4cb7660f0c1939c2.
   - `git diff --name-only HEAD~1 HEAD | wc -l` = 1.
   - `git merge-base --is-ancestor <pre-merge HEAD> HEAD` succeeds.
   - The working file's sha256 prefix = 02d1cdd8995f43e7 (CRLF; core.autocrlf=true).
   - `git diff HEAD -- docs/agents/queue.json | wc -l` = 0.
5. Post-merge run in main: `python tools/analysis/archv2_pilot/selftest.py` must print `282 checks, 0 failed`, rc 0, on any date.
6. Discard the worktree: `git worktree remove --force .claude/worktrees/archv2-clock-fix`, then `git branch -D archv2-clock-fix`. `-D` is needed because the merge is by content, not by ancestry. `--force` discards the queue.json modification, which is intended.

## Per-claim table

| # | claim | ruling | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| C1 | The diff is one line at L886 (`clock=lambda: TODAY`) plus a 2-line comment | CONFIRMED | `git diff 3bee93b 43c047d` shows 3 insertions and 1 deletion in 1 file; `git diff --name-only 3bee93b 43c047d \| wc -l` = 1 | 1 file, +3/-1 | - |
| C2 | Pins before 82ee9cde / 8e23ad5f15833b23; after 34743f1e / bcaf589f8c9a755e / crlf 02d1cdd8995f43e7 | CONFIRMED | rev-parse, hash-object, sha256 of the LF and CRLF renderings (identity table) | all to the digit; base crlf16 9e8649b7ff55845e = the record's L20019 | - |
| C3 | L886 is the only real-clock site the selftest reaches; PL.launch turns today=TODAY into a clock (pilot.py L1304-L1305); guard_day / append / pending get day=TODAY | CONFIRMED (dynamic, all parts) | Static: grep over the reachable modules. The day-valued real-clock sources are time.strftime("%Y-%m-%d") via accounting.local_day L138, guard_day L103, pilot.posting_day_ok L1079 and accepted_tests_ledger.day_ledger_path L46. The timestamp sources (not day-valued) are accounting._now L144, data_v2/verdicts.py L180, judge_v2/writer.py L179 and the ledger row ts at accepted_tests_ledger L134. Dynamic: my own harness (below) fakes EVERY wall-clock entry point, not just the two the builder faked, and logs each read by caller. | At the tip: 0 day-valued reads in every run (--part all under python and -O; stage1; supply; pool). The only reads are the 4 timestamp sites (9,049 / 9,006 / 31 / 27 under --part all). | - |
| C4 | Faked 2026-10-31 and 2031-02-28 give 282/0 with 0 reads | CONFIRMED (independent dates) | rv_fakeclock.py at 2026-12-31 (py), 2027-01-01 (py and -O, the year boundary), 2028-02-29 (-O, leap day), plus a REAL-clock run today 2026-09-26 without a harness | 282/0, rc 0 in every run; parts at 2027-01-01: stage1 24/0, supply 30/0, pool 103/0 | - |
| C5 | Mutant (L886 without clock=) gives 148 and DAY ROLLOVER; control at 2026-09-25 gives 282/0 with 4 reads | CONFIRMED | Base blob 82ee9cde loaded from `git show 3bee93b:...`, and the in-memory revert of the tip | base and revert at 2027-01-01: 148 executed, 0 FAIL, SystemExit DAY ROLLOVER (posting day 2026-09-25 vs 2027-01-01), 1 read at accounting.py:138; base at 2026-09-25: 282/0 with 4 reads at accounting.py:138 | - |
| C6 | selftest.py is not in common.PACKAGE_FILES (common.py L209-L211), so the package lf16 stays 00bce6429d6dea64 | CONFIRMED | `git show 43c047d:.../common.py \| sed -n 209,211p \| grep -c selftest` = 0; package hash recomputed at 3bee93b, 43c047d and in the worktree | 00bce6429d6dea64 three times | - |
| C7 | No runtime pin cites selftest.py | CONFIRMED | `git grep -c 82ee9cde 43c047d -- tools src experiment_configs \| wc -l` = 0 (same for 8e23ad5f). The only runtime reference is judge_v2/pool_selftest.py I5, which RUNS `selftest.py --part pool --main-ref HEAD` and checks its tail line; it pins no hash, and --part pool returns before part_k1_journal (L886). Doc citations of 82ee9cde (programme L19391, L20019, L20547; READY_jv2_parallel_posting*.md; results JSONs; queue.json) are historical records, not runtime. | 0 runtime pins | - |
| C8 | Selftest 282/0 under python and -O; judge_v2 selftest 174; pool_selftest rc_wire 16/0 | CONFIRMED | Real-clock tip run: 282/0 rc 0. -O under fake clocks: 282/0. `judge_v2/selftest.py`: ALL PASS (174 checks). `pool_selftest.py --only rc_wire`: 16 checks, 0 failed, 8 of 8 mutants killed. I also ran `pool_selftest.py --only i5`: 4 checks, 0 failed; the inner `--part pool` gave 103/0. | as claimed | - |
| C9 | The worktree queue.json modification is a re-run of a3df39a's bracket patch and does not travel with a by-path merge | CONFIRMED | Worktree `git diff --numstat` = 6/6 on queue.json. Per-line length deltas 778 / 126 / 158 / 314 / 901 / 439 are EXACTLY a3df39a's own per-line insertions on the same 6 lines. `ab90e24` occurs 8 times at HEAD and 16 in the worktree file. The modification is UNCOMMITTED, so it is in no commit on the branch (`git diff --name-only 3bee93b 43c047d` = selftest.py only). Main's queue.json = HEAD (blob 338a06ef). | a duplicate, excluded | - |

## My harness (scratch, not of record)

`C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\rv_clock\rv_fakeclock.py`

- **What it fakes.** Before any project import it replaces time.strftime (no tuple, any format), time.localtime/gmtime/ctime/asctime (no argument), datetime.datetime.now/today/utcnow and datetime.date.today with a clock shifted by a constant offset. Every read is logged with its first caller frame under tools/analysis.
- **How mutants are applied.** In memory: each needle is asserted to occur once in the source, then the source is exec'd as archv2_pilot.selftest or archv2_pilot.pilot. No file is written.
- **What it ran on.** The worktree files, read-only, with PYTHONDONTWRITEBYTECODE=1.
- **Worktree untouched.** After all runs, `find <worktree> -newer marker_start` (excluding .git and __pycache__) counts 0. `git status --porcelain` is unchanged (only ` M docs/agents/queue.json`), and HEAD is still 43c047d.
- **Resource cap.** At most 2 python processes at once. The pool I5 run, which spawns a child, ran alone.

Outputs are in the same directory: real_tip_py.txt, fk_tip_*.txt, base_*.txt, mrevert_*.txt, m_*.txt, mp_clock_*.txt, jv2.txt, pool_rcwire.txt, pool_i5.txt.

## Mutants of my own

| mutant (in memory) | date | result | read site | killed? |
|---|---|---|---|---|
| M-revert: L886 without clock= | 2027-01-01 | 148 executed, DAY ROLLOVER, rc 1 | accounting.py:138 x1 | KILLED |
| M-launch-r1: `today=TODAY` dropped from the r1 pilot PL.launch (L762) | 2027-01-01 and 2026-09-25 | 282/0, rc 0 | accounting.py:138 x24, pilot.py:1079 x1 | SURVIVED |
| M-launch-pool: `today=TODAY` dropped from the part_pool pilot launch (L1780) | 2027-01-01 | 282/0, rc 0 | accounting.py:138 x24, pilot.py:1079 x1 | SURVIVED |
| M-guard: `day=TODAY` dropped from ACC.guard_day (L730) | 2027-01-01 | 282/0, rc 0 | accounting.py:103 x1 | SURVIVED |
| M-append: `day=TODAY` dropped from ACC.append OTHER-TEST 13,990 (L737) | 2027-01-01 | 282 / 1 FAIL ("the posting-day cap 14,000 -> REFUSED": no refusal), rc 1 | accepted_tests_ledger.py:46 x1 | KILLED |
| MP-clock (production, pilot.py): `clock = ACC.local_day` regardless of today | 2027-01-01 / 2026-09-25 | 106 / 155 executed, DAY ROLLOVER | accounting.py:138 | KILLED |

## Defects

- **D1 (MEDIUM, follow-up; not blocking).** The selftest's own verdict is not a witness of clock independence. When a launch loses `today=`, it takes its posting day AND its clock from the same real clock, so the two agree. The run reads the real clock 25 times and still passes 282/0 on any date: M-launch-r1, M-launch-pool and M-guard all SURVIVE. Such a regression would surface only as a flake when a run crosses local midnight. The fix is correct, but its date independence is proved by this review's external read counter, not by the selftest.
  - Fix (own small registration, selftest-only): inside `selftest()`, install a trap clock. Replace `ACC.local_day` and the day-format strftime with functions that count their calls. Add one check that the count is 0 outside the explicit clock tests (the `_rollover_clock` cases, which inject their own clock). Then my three surviving mutants become FAILs.
- **D2 (LOW, scope of the builder's proof).** The builder's wrapper faked only `time.strftime("%Y-%m-%d")` without a tuple and `accounting.local_day`, so "0 real-clock reads" was scoped to those two entry points. My harness covers every wall-clock entry point. It finds the same zero for day-valued reads, plus about 18k timestamp reads (the journal / verdict / writer / ledger ts). No check compares those to a day: 282/0 at 4 shifted dates and at the real date. No fix needed beyond this disclosure.
- **D3 (LOW, process).** A patch script was re-run with the worktree as its working directory and doubled a3df39a's 6 brackets in the worktree's queue.json (C9). Record of record unaffected: main's queue.json = HEAD. Fix: discard it with the worktree (merge step 6); never `git add -A` there.

## How future reviews cite the selftest

Cite `tools/analysis/archv2_pilot/selftest.py` as blob:34743f1ed2dd1b30dd2e097a4cb7660f0c1939c2 / sha256-lf16:bcaf589f8c9a755e. Add sha256-crlf16:02d1cdd8995f43e7 only when quoting a CRLF working tree.

The selftest is not a package file: it never enters the package lf16 00bce6429d6dea64, and no runtime pin checks it. So a READY that relies on it must state the blob it ran, not just the package hash.

Until D1 is fixed, a READY that needs date independence cannot read it from the selftest's 282/0. It must run a fake-clock pass itself, at a date other than 2026-09-25, and report the day-valued read count.
