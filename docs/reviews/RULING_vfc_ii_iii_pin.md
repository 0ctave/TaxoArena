# RULING (2026-09-25, adversarial-reviewer): the build and pin of VFC-FIXES-2 delta checks (ii) and (iii)

## 0. Ruling

**(b2): re-issue R2.6 against the merge commit f76a93b.** Do not use 930ccc7, and do not use a9d8d7d.

- **Pin of record for (ii) and (iii).** `tools/analysis/vote_frame_cert.py` blob:1a3d0bb5576b5c18c15c42e3ee8da09967303dca / sha256-lf16:b45b75db7d98103e.
  - The CRLF rendering, sha256-crlf16:3b44739e161d0d86, is what the main working tree holds. It is **not** printed by any leg: the archive is LF by construction.
  - Every `--expect-lf` becomes `b45b75db7d98103e`.
- **R2.6 as written is also defective, independently of this ruling.** Its (iii) TIE-MECHANICS expectation of "0 differing lines" is unreachable from an LF archive. Its L1 / L2 CRLF halves are wrong.
  - Section 3 re-issues the commands and expected diffs. Section 4 lists the harness change this forces.
- **Zero calls.** I ran no suite, no leg, no `--dry-run` and no `--selftest`. I opened no DB. I ran only git objects, sha256, `diff`, and the harness's text-only `score-vfc` scorer on four synthetic text variants (section 5, P1).

### Why b2 and not b1
- **Reuse is proven on the bytes that will be reused.**
  - What will be reused is main's `vote_frame_cert.py`, blob 1a3d0bb5.
  - Under b2, C-ii-1 REFUSES unless the archived file IS those bytes.
  - Under b1, (ii)/(iii) would certify blob c99fb126 (lf16 211112d41eed0b77), which is on no ref of main. It would reach main's file only through an argument (the selftest-only diff).
  - The argument is true (section 1), but an argument is not the bytes.
  - b1 would also leave a scratch certificate whose L1 names a writer sha that main does not carry.
- **b2 loses nothing of the READY's scope.** In all three legs the code that runs is byte-identical under b1 and b2 (section 1):
  - the harness passes `selftest_ok=True`, so `selftest()` never executes in a leg;
  - lines 1-2258 and the `__main__` block are identical.
- **b2 costs one thing, and it is a precondition.** E3 must be executed on b45b75db.
  - The harness prints "[E3] ... rests on part (i)'s selftest of the same LF sha". Under b2 that sentence is false unless a selftest of b45b75db is ON RECORD.
  - Today there are only RELAYED counts (the engine-coder's R2-L1 run and the orchestrator's pre-merge tests), and no log was read (programme L20127-L20162, items 3-4).
  - See P3.
- **Why f76a93b and not a9d8d7d.**
  - Both carry blob 1a3d0bb5.
  - a9d8d7d and 930ccc7 are reachable ONLY through the worktree branch `worktree-agent-ad89ebf95e36802f5` (`git branch -a --contains a9d8d7d` and `... 930ccc7` each print only that branch). Removing the worktree makes the archived commit collectable.
  - f76a93b is an ancestor of main (`git merge-base --is-ancestor f76a93b HEAD` rc 0).
  - The archive trees differ, but not in anything a leg reads. `git diff --name-only 930ccc7 f76a93b -- tools/analysis src/main/kotlin experiment_configs | wc -l` = 27. Of these, `grep -cE` over the legs' read closure (15 modules: the 3 instruments, rejudge_grok, rejudge_reasoning, rejudge_reference, judge_free_tests, pool_guard, split_side, arena13, placebo_entry, rubric_p8, rubric_512, stack_judge, prompt_v2) = 1, and that 1 is vote_frame_cert.py itself.
  - How the closure was built:
    - the direct imports of the 3 instruments (rejudge_grok, rejudge_reasoning, pool_guard, split_side via pool_guard);
    - the ast-only source reads `source_constant` (arena13.py NEW, placebo_entry.py GEM) and the imports of those sources;
    - the H3 writers and the transitive scan read git history in REPO, not the archive.
  - The run-operator re-checks this closure mechanically before the legs (section 3, step 0c).

## 1. The delta 930ccc7 -> a9d8d7d is inside selftest() only: CONFIRMED

| check | command | got |
|---|---|---|
| parent | `git rev-parse a9d8d7d^` | 930ccc762d346b0da7ede17d1e86a70bb3cb0028 |
| scope, whole tree | `git diff --name-only 930ccc7 a9d8d7d \| wc -l` | 1 |
| size | `git diff --numstat 930ccc7 a9d8d7d` | `9 8 tools/analysis/vote_frame_cert.py` |
| changed lines | `diff vfc_930ccc7.py vfc_a9d8d7d.py \| grep -c '^[<>]'` | 17 (8 removed + 9 added). Hunks at 930ccc7 L2534-2536, 2539-2540, 2565, 2567, 2571 |
| selftest span | `grep -n "^def selftest\|^if __name__"` on both | 930ccc7: L2259 / L2754 (2766 lines); a9d8d7d: L2259 / L2755 (2767 lines) |
| bytes before selftest() | `diff <(sed -n '1,2258p' A) <(sed -n '1,2258p' B)` | identical (PRE_SAME) |
| bytes after selftest() | `diff <(sed -n '2754,2766p' A) <(sed -n '2755,2767p' B)` | identical (POST_SAME) |
| new name resolves | `grep -n "^from collections"` | L231 `from collections import Counter, defaultdict` at both (the new `SD` lambda uses an existing import) |
| a9d8d7d = f76a93b = HEAD for the file | `git rev-parse <c>:tools/analysis/vote_frame_cert.py` | 1a3d0bb5576b5c18c15c42e3ee8da09967303dca at all three |

- A and B are `git show 930ccc7:` / `git show a9d8d7d:tools/analysis/vote_frame_cert.py`.
- The instrument reads its own bytes in one place only: `script_shas()` (L879-L882), which gives the printed identity (L1, and the JSON `script_sha256_16_lf/_crlf`). Nothing else reads its own source.

### Pins, recomputed from the blobs (sha256 over `git cat-file blob`; CRLF = every LF -> CRLF)

| commit | file | blob | sha256-lf16 | sha256-crlf16 | CR in blob |
|---|---|---|---|---|---|
| 930ccc7 | vote_frame_cert.py | c99fb126 | 211112d41eed0b77 | ec3e9a34f042068f | 0 |
| a9d8d7d / f76a93b / HEAD | vote_frame_cert.py | 1a3d0bb5 | b45b75db7d98103e | 3b44739e161d0d86 | 0 |
| all four | position_index_all.py | bcbaf609 | 9c78d485f37f442a | 50bb9285e9068f0b | 0 |
| f76a93b | tie_mechanics.py | 7f88d2ac | d6a1a0409a0fc06e | 4a18124878801487 (the working tree's raw sha256) | 0 |

- **Main working tree.** `git hash-object tools/analysis/vote_frame_cert.py` = 1a3d0bb5 (raw sha256-16 3b44739e161d0d86, 2,767 CR bytes).
- **Registrar's pins.** All agree to the digit (4b85aff, item 4).
- **Outputs of record at HEAD, unchanged:**
  - vote_frame_cert.txt 8db4403f (404 lines);
  - vote_frame_cert.json 5ec19826;
  - position_index_all_outcome.txt bb1578ca;
  - x12_crossdomain/tie_mechanics_outcome.txt a2df609d.

## 2. Per-claim table (the claims of the decision as framed)

| claim | verdict | evidence | severity / fix |
|---|---|---|---|
| 930ccc7 and a9d8d7d differ only inside selftest(), +9/-8 | CONFIRMED | section 1 | none |
| Under b2 every --expect-lf becomes b45b75db7d98103e | CONFIRMED | harness L120-L122 compares `raw16` of the archived file to `--expect-lf`, and refuses any CR byte | none |
| Under b2 the (ii) expected diff at L1 becomes "b45b75db / 3b44739e" | **REFUTED** (the CRLF half) | `script_shas()` returns (LF16, sha256 of the bytes AS READ). The archive has 0 CR bytes (C-ii-1 refuses otherwise), so L1 prints `... LF bytes b45b75db7d98103e (of the CRLF rendering b45b75db7d98103e) ===`. The JSON has `script_sha256_16_lf` = `script_sha256_16_crlf` = b45b75db7d98103e. 3b44739e can never appear | MEDIUM. The same error is in R2.6 as written (L1 "211112d41eed0b77 / ec3e9a34f042068f" would print 211112d41eed0b77 twice). The scorer hides it: score-vfc L1 accepts ANY line starting "=== VOTE-FRAME-CERT" without 72ceddfe. FIX: section 3 text, section 4 H2 |
| (iii) is unaffected either way (position_index_all.py has the same blob everywhere) | **PARTLY** | The (iii) expected diffs do not depend on b1/b2, true. But both (iii) legs IMPORT vote_frame_cert.py from the archive (position_index_all.py L101, tie_mechanics.py L63) and pass the same `--expect-lf`, so under b2 (iii) exercises b45b75db | LOW. Wording only: (iii) is pinned by the ruling too |
| R2.6 (iii) TIE-MECHANICS: "0 differing lines" (this reviewer's own READY, f387d58) | **REFUTED** (under b1 AND b2) | The record's L14 reads `... LF bytes d6a1a0409a0fc06e (of the CRLF rendering 4a18124878801487) ===`, written from the CRLF working tree. From an LF archive, `vfc.script_shas(__file__)` (tie_mechanics.py L451) prints `(of the CRLF rendering d6a1a0409a0fc06e)`: sha256 of the LF blob, recomputed = d6a1a0409a0fc06e, with no .gitattributes at f76a93b. score-tm exits rc 3 on ANY differing line | HIGH. A certain false FINDING that would block (iii), or invite an operator to explain an rc 3 away. FIX: section 3 expected diff, section 4 H1 |
| R2.6 (iii) POSITION-INDEX-ALL L2 "-> 9c78d485f37f442a / 50bb9285e9068f0b" | **REFUTED** (the CRLF half) | By the same mechanism L2 prints `9c78d485f37f442a (of the CRLF rendering 9c78d485f37f442a)`. score-pia accepts any change at L2, so it passes, and it would also pass a wrong sha | MEDIUM. FIX: section 3, section 4 H2 |
| R2-M1 scorer fix present in vf2/rerun_vf3.py 5b2de8a3... | CONFIRMED present, and **the variant-C re-run is now EXECUTED** (by me; not yet recorded by the registrar) | `sha256sum` of the scratchpad copy = sha256 of the archive copy `TaxoArena_data/evidence_2026-09-25/scratchpad_rest/vf2/rerun_vf3.py` = 5b2de8a394f7ef5ea65a5c4c49cb70aefa992c1e728e5c581680d81010fd2170 (15,177 bytes, 0 CR). The fix is at L78-L80. See P1 for the runs | the harness must still change (section 4), so the pin of record is the NEW harness's, not 5b2de8a3 |
| The harness's E3 line under b2 | **REFUTED as it would print** | rerun_vf3.py leg vfc prints "[E3] selftest_ok=True is PASSED, not executed here: E3 rests on part (i)'s selftest of the same LF sha b45b75db...". Part (i)'s selftests (rv2/r2st_*.txt) ran on 211112d41eed0b77. The certificate text's L3 "selftest (E3), executed in-process before the census: PASS" is ALSO printed unexecuted (vote_frame_cert.py L1565-L1567 with selftest_ok=True), in both b1 and b2 | MEDIUM. FIX: P3 (a recorded selftest of b45b75db) and harness H3 |

## 3. R2.6 re-issued (R2.6-b2). Replaces R2.6 of f387d58 for (ii) and (iii); everything not named here stands.

**When.**
- After P1-P5 of section 5.
- In a rule-7 window: W1-W5, 12 GB free RAM, no construction, no writer to the 62 caches or `mmlu_pro_dataset_cache_v2.db`.
- Use Git Bash. `M=Z:/FAC/TUBerlin/THESIS/TaxoArena`. `<S>` is a scratch directory OUTSIDE the repository. `<H>` is the directory of the harness v4 (section 4), pinned by the registrar.

```
# 0a. the build: the MERGE COMMIT on main, LF
mkdir -p <S>/T && git -C $M -c core.autocrlf=false archive f76a93b tools/analysis src/main/kotlin experiment_configs | tar -x -C <S>/T
sha256sum <S>/T/tools/analysis/vote_frame_cert.py      # must print b45b75db7d98103e...
sha256sum <S>/T/tools/analysis/position_index_all.py   # must print 9c78d485f37f442a...
sha256sum <S>/T/tools/analysis/tie_mechanics.py        # must print d6a1a0409a0fc06e...
cat <S>/T/tools/analysis/{vote_frame_cert,position_index_all,tie_mechanics}.py | tr -cd '\r' | wc -c   # must print 0
# 0b. the records of reference
for f in vote_frame_cert.txt vote_frame_cert.json position_index_all_outcome.txt x12_crossdomain/tie_mechanics_outcome.txt; do
  git -C $M show HEAD:experiment_results/$f > <S>/rec_$(basename $f); done
git -C $M rev-parse HEAD:experiment_results/vote_frame_cert.txt   # must print 8db4403f... (and .json 5ec19826, pia bb1578ca, tm a2df609d)
# 0c. the read closure is unchanged between the READY'd build and f76a93b except the instrument
git -C $M diff --name-only 930ccc7 f76a93b -- tools/analysis/{vote_frame_cert,position_index_all,tie_mechanics,rejudge_grok,rejudge_reasoning,rejudge_reference,judge_free_tests,pool_guard,split_side,arena13,placebo_entry,rubric_p8,rubric_512,stack_judge,prompt_v2}.py
#     must print exactly one line: tools/analysis/vote_frame_cert.py
# E3. selftests ON THE ARCHIVE of f76a93b (admitted under rule 7 as selftests); save every transcript
cd <S>/T && python tools/analysis/vote_frame_cert.py --selftest    > <S>/e3_vfc_py.txt 2>&1   # 472/0
            python -O tools/analysis/vote_frame_cert.py --selftest > <S>/e3_vfc_O.txt  2>&1   # 472/0
            python tools/analysis/position_index_all.py --selftest > <S>/e3_pia_py.txt 2>&1   # 55/0 +1 INFO
            python tools/analysis/tie_mechanics.py --selftest      > <S>/e3_tm_py.txt  2>&1   # 29/0
# (ii)
python <H>/rerun_vf4.py vfc --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --e3-log <S>/e3_vfc_py.txt --repo $M --out <S>/ii
python <H>/rerun_vf4.py score-vfc --expect-lf b45b75db7d98103e --rec <S>/rec_vote_frame_cert.txt --new <S>/ii/vote_frame_cert.txt --rec-json <S>/rec_vote_frame_cert.json --new-json <S>/ii/vote_frame_cert.json
# (iii)
python <H>/rerun_vf4.py pia --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --repo $M --out <S>/iii_pia
python <H>/rerun_vf4.py score-pia --rec <S>/rec_position_index_all_outcome.txt --new <S>/iii_pia/position_index_all_outcome.txt
python <H>/rerun_vf4.py tm --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --repo $M --out <S>/iii_tm
python <H>/rerun_vf4.py score-tm --rec <S>/rec_tie_mechanics_outcome.txt --new <S>/iii_tm/tie_mechanics_outcome.txt
```

Each leg must print:
- `[C-ii-3] ... unchanged`;
- vfc: `[PRE] 62 of 62` and `[POST] 62 of 62 caches unchanged`;
- the admitted PIDs and the wall time (rule 7).

### EXPECTED DIFFS, (ii), against c731836 (404 lines). Only these may differ. They are as in R2.6 except L1.

- **L1**, exactly: `=== VOTE-FRAME-CERT (zero calls) | registration docs/judge_v2_program.md L13032-L13109 (8adae39) | script sha256[:16] of the LF bytes b45b75db7d98103e (of the CRLF rendering b45b75db7d98103e) ===`.
  - The parenthetical is the instrument's mislabel of "the bytes as read" when run from an LF file. It is NOT a CRLF sha. 3b44739e161d0d86 must NOT appear.
- **JSON** (not scored, read): `script_sha256_16_lf` = `script_sha256_16_crlf` = `b45b75db7d98103e`.
- **L3**, `selftest (E3), executed in-process before the census: PASS`, does not move, and is NOT evidence. E3 is the transcript `<S>/e3_vfc_py.txt` of step E3.
- **Unchanged from R2.6 (f387d58):**
  - L4, L388, L154-L157 (C3), L345, L350, L389, L400;
  - the six secondaries L176, L180, L184, L188, L245, L275 with n of m;
  - L402, L403 (removed), L404.
- Anything else is a FINDING, as R2.6 lists. R2.5 routing applies unchanged.

### EXPECTED DIFFS, (iii)

- **position_index_all_outcome.txt:** L2 only, exactly: `=== POSITION-INDEX-ALL (zero calls) | registration docs/judge_v2_program.md L13111-L13227 (b25bde0) | script sha256[:16] of the LF bytes 9c78d485f37f442a (of the CRLF rendering 9c78d485f37f442a) ===`.
  - L3 does not move (certificate writer 72ceddfe; entered 50, excluded 12).
  - `[WITNESS]` shows 4 content resolutions.
- **tie_mechanics_outcome.txt:** ONE line, L14, exactly: `=== TIE-MECHANICS (zero calls) | registration docs/judge_v2_program.md L12911-L13030 (3c2fcab) | script sha256[:16] of the LF bytes d6a1a0409a0fc06e (of the CRLF rendering d6a1a0409a0fc06e) ===`.
  - The record has `4a18124878801487` in the parenthetical. Every other line: 0 differences.
  - UNDETERMINED risk, not an expected diff: the record eb6fc9c (2026-09-23 16:06) predates pool_guard d30c19e (16:57). If a pool-guard line moves, it is a FINDING to report, never an expected diff.
- A `[FRAME] REFUSED (R-8)` in either leg is a FINDING (drift).

## 4. Harness v4 (required; the pin of record is v4's, not 5b2de8a3)

Built from vf2/rerun_vf3.py 5b2de8a3 by the engine-coder. Only these changes:
- **H1.** `score-tm` admits exactly one differing line: record L14 -> the exact string of section 3. Any other line, or any other L14 text, is a FINDING (rc 3).
- **H2.** `score-vfc` L1 and `score-pia` L2 check the exact expected strings of section 3 (the LF16 from a new `--expect-lf` on score-vfc; the constant for pia). This replaces the current "starts with ... and no 72ceddfe" and "any change at L2", which accept any sha.
- **H3.** The leg C-ii-1 check also pins the archived `position_index_all.py` (9c78d485f37f442a) and `tie_mechanics.py` (d6a1a0409a0fc06e) by LF16, with 0 CR. Today nothing pins them before a run.
- **H3 (continued).** The vfc leg takes `--e3-log <file>`. It refuses unless the file exists and contains the vote_frame_cert selftest total line with 472 passed and 0 failed. It prints the sha256 of that log in place of "rests on part (i)'s selftest of the same LF sha".
- **Verification before the pin** (text-only; the reviewer re-executes):
  - score-vfc on rv2/scor_{A,C,D,H}_*.txt gives rc 0 / 3 / 3 / 3. The L1 of those synthetic files is `211112d41eed0b77 (of the CRLF rendering 9d86e3fba063ef5d)`, so under H2 variant A must be regenerated with the section-3 L1 before it can give rc 0.
  - score-tm on the record with L14 replaced by the section-3 string gives rc 0.
  - score-tm with L14 carrying any other sha gives rc 3.
  - score-tm with a second changed line gives rc 3.
- **Commit.** Commit v4 by pathspec to a path OUTSIDE `tools/` and `src/` (for example `docs/reviews/evidence/vfc_fixes_2/rerun_vf4.py`; the registrar chooses). Pin it as blob / sha256-lf16 / sha256-crlf16.

## 5. Preconditions before (ii) can be scored (all must be recorded by the registrar, by insertion, before the first leg)

- **P1. R2-M1.**
  - The scorer fix is shown to work on harness v3 by my execution, text-only:
    - `python vf2/rerun_vf3.py score-vfc --rec <git show HEAD:experiment_results/vote_frame_cert.txt> --new rv2/scor_<v>.txt`;
    - A_expected_only rc 0 (FINDINGS 0); C_inserted_indented_note **rc 3** (finding: "LNone an unexpected inserted / deleted line: R6 stored labels unresolvable: 3 unresolvable label(s) on the deciding tally"); D_ladder_class_move rc 3; H_inserted_cache_header rc 3;
    - transcripts in this session's scratchpad `rul/score_*.out`.
  - This discharges "variant C must give rc 3" FOR v3.
  - Because v4 is required (section 4), the re-pin and commit of record are v4's. The variant runs of section 4 must be recorded for v4.
  - Until v4 is committed and pinned, R2-M1 stays OPEN.
- **P2. Harness v4.** Built, verified as in section 4, committed by pathspec, pinned (three hash kinds). The scratch v3 (5b2de8a3, also archived on the evidence disk) is evidence only.
- **P3. E3 on the bytes reused.** Step E3 of section 3 is executed on the LF archive of f76a93b, and its four transcripts are saved and hashed:
  - vote_frame_cert --selftest 472/0 under python AND -O;
  - position_index_all 55/0 +1 INFO;
  - tie_mechanics 29/0.
  - The relayed pre-merge counts and the relayed R2-L1 count are NOT substitutes: no log was read (4b85aff items 3-4).
- **P4. R2.5 routing.**
  - The arena-specialist is named as the owner of the "is '' NULL?" question BEFORE the legs run.
  - The F1 readout (score-vfc with `--rec-json/--new-json`) is part of (ii).
  - If any unit of record moves to R6 and its `unresolvable_values` are ALL '', (ii) is NOT scored until the arena-specialist rules. Neither the builder nor the run-operator defaults it.
  - Any other label is an ordinary R6 finding under R-5.
- **P5. This ruling recorded** by the registrar in the programme, VFC-FIXES-2.json (open_decisions), and the queue item VFC-FIXES-2-DELTA-II-III:
  - `ready_file` -> R2.6-b2 of this file;
  - blocker (b) closed;
  - blocker (a) re-stated as P1-P2.
- **Standing, unchanged:**
  - the F5 freeze is MET (38ec2f3);
  - C-ii-3 and the 62-of-62 [PRE]/[POST] check;
  - "Anything else is a FINDING";
  - V-C5;
  - the certificate of record stays c731836, VFC_PIN_LF 72ceddfe (no new certificate, no output of record written).

## 6. Cost (zero calls) and the rule-7 window

- **Data read by (ii).** The 62 recorded caches total **614.0 MB** (sum of `size` in `git show HEAD:experiment_results/vote_frame_cert.json`; largest 82.5 MB).
  - The vfc leg hashes them before, during (the certificate's own sha256_16) and after (about 1.8 GB of sha256), and reads every row of every table (the census).
- **CPU estimate (UNMEASURED: the programme records no wall time for the c731836 run, pia b472d40 or tm eb6fc9c):**
  - E3 selftests: about 2-4 CPU min (the 6 round-2 selftest transcripts rv2/r2st_*.txt carry mtimes within 05:56:11-05:57:45);
  - (ii) vfc: about 5-15 min;
  - (iii) pia: about 2-5 min;
  - (iii) tm: about 1-3 min;
  - scoring: seconds.
  - **Total about 10-27 CPU min, single-threaded, 0 calls.**
- **Rule 7.**
  - The E3 selftests are admitted at any time while the pool DBs are FREE.
  - The three legs are non-selftest tools/analysis readers (the 62 caches, `mmlu_pro_dataset_cache_v2.db`, pool_guard). They need a window: W1-W5 exclusive-open probe, 12 GB free RAM before each leg, no construction, no writer, no git write under src/, admitted PIDs and wall time printed per leg.
  - They fit in ONE window of 45 min with margin. Run the legs sequentially, not beside another reader.
  - The other reviewer's CPU selftests may coexist (selftests are admitted), at a wall-time cost only.
- **Agent time (estimate):**
  - engine-coder 0.5 h (v4);
  - reviewer 0.5 h (v4 verification and pin check) + 0.5-1 h (scoring (ii)/(iii));
  - run-operator 0.5-1 h;
  - registrar 0.5 h.

## 7. Defects list

| id | severity | defect | fix |
|---|---|---|---|
| RP-1 | HIGH | R2.6 (f387d58) expects 0 differing lines in tie_mechanics_outcome.txt. From an LF archive, L14's CRLF parenthetical moves 4a18124878801487 -> d6a1a0409a0fc06e, so score-tm gives rc 3 under b1 and b2 alike | section 3 expected diff; harness H1 |
| RP-2 | MEDIUM | R2.6 (ii) L1 "211112d41eed0b77 / ec3e9a34f042068f" and (iii) L2 "9c78d485f37f442a / 50bb9285e9068f0b": the CRLF halves cannot print from an LF archive. The framed b2 L1 "b45b75db / 3b44739e" repeats the error | section 3 exact strings |
| RP-3 | MEDIUM | The scorers accept any sha at vfc L1 and pia L2. Nothing pins the archived position_index_all.py / tie_mechanics.py before a leg | harness H2, H3 |
| RP-4 | MEDIUM | E3 is PASSED, not executed, in the vfc leg. The certificate's L3 then says "executed in-process". Under b2 the harness's E3 sentence names a selftest that was never run on those bytes | P3; harness H3 (`--e3-log`) |
| RP-5 | LOW | The builds 930ccc7 / a9d8d7d are reachable only through the worktree branch worktree-agent-ad89ebf95e36802f5 | keep the branch until the delta is recorded; the evidence of part (i) cites them |
| RP-6 | LOW | `script_shas()` labels "the bytes as read" as "the CRLF rendering". It is correct only when run from a CRLF working tree | documented; no instrument change inside this delta (it would move the pin again) |

## 8. What this ruling does not show

- It does not show (ii) or (iii), or whether any unit moves under F1 or on '' labels.
- It does not show that the selftests of b45b75db pass: those counts are RELAYED until P3.
- It does not show that no pool-guard line moves in the tm output (UNDETERMINED risk, section 3).
- The CPU minutes are an estimate, not a measurement.
- The read-closure list in step 0c is from my inspection of direct imports and ast reads of the three instruments at f76a93b. The step re-checks it by count; it does not prove that no dynamic import exists (V-C5 stays).
