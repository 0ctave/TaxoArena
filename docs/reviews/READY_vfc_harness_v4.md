# READY review (2026-09-25, adversarial-reviewer): VFC-FIXES-2 (ii)/(iii) harness v4, branch vfc-harness-v4 at bf8e76c, against RULING 93cc7de (P2: H1-H3)

## 0. Verdict

**NOT READY at bf8e76c. READY on a one-defect delta (RV4-1) that needs no re-review: re-running the driver confirms it.**

- **H1, H2 and H3 are implemented exactly as ruled.** Every section-3 string is verbatim. My re-run of the driver in a fresh scratch dir gives 53/53 cases and 23/23 mutants killed. My 4 own mutants are all killed.
- **RV4-1 (MEDIUM, fail-open):** the harness does not enforce the ruling's pin. The pin lives only in `prep`, and prep is optional.
  - Given an LF archive of **930ccc7** (the build the ruling rejected), `--expect-lf 211112d41eed0b77`, and the round-2 transcript of 930ccc7's selftest as `--e3-log`, the vfc leg passes every pre-check. It reached `FileNotFoundError` on my empty fake repo, i.e. past C-ii-1, H3 and E3.
  - `score-vfc --expect-lf 211112d41eed0b77` on an L1 carrying 211112d41eed0b77 twice gives `SCORE: PASS`, rc 0.
  - So a b1 run is indistinguishable from a b2 run by exit code. That is the thing the ruling exists to prevent ("reuse must be proven on the bytes that will be reused").
- **P1 (R2-M1) is MET in substance.** Variant C gives rc 3 on v4 (case S-vfc-C-v4, in my run and the builder's). A reversal of the R2-M1 window is killed (my mutant R1). The registrar still has to record it.
- **P2 is NOT MET** until RV4-1 is fixed and the fixed file is merged and pinned.
- **Zero calls.** No DB was opened, and no leg ran past its pre-checks: every leg ran against an empty fake repo. No selftest ran. The only git access was read-only (archive / show / rev-parse / diff / merge-base).

## 1. Pins (hash kind named; LF of record; the worktree holds LF, so no CRLF rendering differs on disk)

| file (experiment_results/vfc_fixes_2/harness/) at bf8e76c | blob | sha256-lf16 | sha256-crlf16 | CR in blob | lines |
|---|---|---|---|---|---|
| rerun_vf4.py | 32c8f7ff | a9fea8d20cf5446f | 386b72376dd09288 | 0 | 314 |
| rerun_vf3.py (the v3 evidence copy) | 30ac2929 | 5b2de8a394f7ef5e (full: 5b2de8a394f7ef5ea65a5c4c49cb70aefa992c1e728e5c581680d81010fd2170 = scratchpad and evidence-disk copies) | - | 0 | 189 |
| test_rerun_vf4.py | 968f1a02 | 39fb6e4e041f2140 | - | 0 | 375 |
| transcripts/SUMMARY.txt | 7470d5dd | e7f14367d0b1d975 | - | 0 | 128 |

- **Branch.** `git merge-base --is-ancestor 93cc7de bf8e76c` rc 0.
- **Scope.** `git diff --name-only 93cc7de bf8e76c | wc -l` = 100. The same list filtered by `grep -v '^experiment_results/vfc_fixes_2/harness/'` has 0 lines. `--stat` shows 4182 insertions and 0 deletions.
- **No DB files.** `git ls-tree ... | grep -ciE '\.(db|sqlite|sqlite3)$'` = 0, so nothing under the harness can enter a VOTE-FRAME-CERT enumeration.
- **Worktree.** `git status --short | wc -l` = 0 before and after my run.
- **Builder's pins.** Claimed 32c8f7ff / a9fea8d20cf5446f, 968f1a02 / 39fb6e4e041f2140 and 7470d5dd. All CONFIRMED.

## 2. Per-claim table

| claim | verdict | command / evidence | got |
|---|---|---|---|
| H1: score-tm admits exactly one differing line, L14 (4a18124878801487 -> d6a1a0409a0fc06e) | CONFIRMED | rerun_vf4.py L165-L173. Positional `exact_line(new, 14, TM_L14_NEW)`, plus the record-side `exact_line(rec, 14, TM_L14_REC)`. Every other paired diff is a FINDING | driver: tm expected rc 0; 3b44739e / 0000 / unmoved / second line / inserted line / record L14 altered all rc 3 |
| H2: exact vfc L1 (from `--expect-lf`) and pia L2 | CONFIRMED | L103-L104, L125, L160-L162. Driver [CONST]: VFC_L1, PIA_L2 and TM_L14_NEW are verbatim in 93cc7de; TM_L14_REC equals the record's L14; 3b44739e is in no constant | A_v4 rc 0; A orig / b2-framed 3b44739e / L1 unmoved / L1 deleted / wrong expect-lf rc 3; pia expected rc 0, unmoved / 50bb9285 half / second line rc 3 |
| H3: legs pin pia and tm by LF16 with 0 CR; `--e3-log` required, form-checked and hashed | CONFIRMED, with RV4-1 | L220-L243 | driver L-cases all as expected. BUT vote_frame_cert.py is pinned to the operator's `--expect-lf`, not to the ruling's constant (RV4-1) |
| 53/53 cases, 23/23 mutants killed | CONFIRMED | `python test_rerun_vf4.py --repo <main> --work <SP>/v4r/work --transcripts <SP>/v4r/tr`, fresh dirs, python 3.11.1, 8.7 s wall, rc 0 | `[SUMMARY] cases 53, meeting expectation 53, failing 0`; `mutants 23, killed 23, survived 0; 2 listed as equivalent / not run`; 91 harness runs, every leg against the empty fake repo |
| Fixtures are the rv2 originals (stored LF, CRLF round-trip checked) | CONFIRMED | my `sha256sum` of scratchpad rv2/scor_{A,C,D,H}_*.txt and r2st_vote_frame_cert_py.txt: b43be9bb / 77de3900 / c714839e / b3bb666f / 02339bfd | equal to the driver's [FIXTURE] CRLF shas, all OK |
| Variant C rc 3 on v4 (P1) | CONFIRMED | case S-vfc-C-v4 | rc 3, the single finding "LNone an unexpected inserted / deleted line: R6 stored labels unresolvable ..." |
| CRLF rendering of the archived vfc file = 3b44739e161d0d86 | CONFIRMED (agrees with ruling section 1) | earlier `git cat-file blob 1a3d0bb5 \| sed 's/$/\r/' \| sha256sum` | 3b44739e161d0d86 |
| Two mutants not run: MP-CR equivalent under the sha gate; MP-inside-repo not run to avoid extracting into the worktree | ACCEPTED | A CR byte changes the sha256, so the prefix gate refuses first; the inside-repo refusal branch is itself executed (P-prep-out-inside-repo, rc 1, nothing created) | - |
| Limit: `--e3-log` checks form and hash, not which bytes produced it | CONFIRMED, and it is real | my probe: the 930ccc7 selftest transcript (fixture r2st_vote_frame_cert_py.txt, a selftest of 211112d41eed0b77) PASSES the E3 check on a b2 build and on a b1 build | the tie is procedural (section 5, step 3); see RV4-1 for the half that CAN be closed in code |

### My own mutants (rv4 scratch v4r/mine/rmut.py; transcript v4r/mine/rmut_out.txt; exact count-asserted replacements in a copy)

| id | what it removes | kill case(s) (base rc -> mutant rc) | result | caught by the builder's driver? |
|---|---|---|---|---|
| R1-M1-window | the R2-M1 fix: the C3 window admits any insertion (`0 <= x[3] <= 10**6`) | S-vfc-C-v4 3 -> 0; S-vfc-H-v4 3 -> 0 | KILLED | yes by its cases (not in its mutant list) |
| R2-prefix | H2/H1 exactness weakened to a 60-char prefix match (v3-style laxness) | S-vfc-A-orig 3 -> 0; S-pia-crlf-half 3 -> 0 | KILLED | yes by its cases |
| R3-tm-skip-window | the H1 positional skip widened to L13-L15 | NEW cases tm expected + L15 changed 3 -> 0; + L13 changed 3 -> 0 | KILLED | **no**: the driver's "second line" is L1 and its insert is at the end, so this mutant survives the driver (RV4-3) |
| R4-e3-anyheader | the E3 header accepted on any line, not only line 1 | NEW case: a transcript with one preamble line: base REFUSED -> mutant passes the pre-checks | KILLED | **no**: the driver's bad-header case has no header anywhere, so this mutant survives the driver (RV4-3) |

## 3. Defects

| id | severity | defect | fix |
|---|---|---|---|
| RV4-1 | MEDIUM (fail-open; blocks the pin) | `vfc` / `pia` / `tm` legs and `score-vfc` take the vote_frame_cert pin from the operator (`--expect-lf`). The ruling's constant `PIN_LF["vote_frame_cert.py"]` = b45b75db7d98103e is enforced only in `prep`, which the docstring calls optional ("the operator may still run 0a / 0c by hand"). Probe: a 930ccc7 archive plus `--expect-lf 211112d41eed0b77` plus the 930ccc7 selftest log passes C-ii-1, H3 and E3. score-vfc with 211112d41eed0b77 gives rc 0 | At L70, refuse unless `a.expect_lf == PIN_LF["vote_frame_cert.py"]` (keep the flag, so the command states the pin). Add driver cases: (i) the vfc leg on an LF archive of 930ccc7 with `--expect-lf 211112d41eed0b77` gives rc 2 or 1 with the pin message; (ii) score-vfc with `--expect-lf 211112d41eed0b77` refuses. Add one mutant removing the new check. Confirmation: the driver re-run, all cases MEET and all mutants KILLED |
| RV4-2 | LOW (fail-closed) | `prep`'s inside-repo test and the legs' audit `inside()` use a bare `startswith` on normcased paths. A scratch dir under `Z:\FAC\TUBerlin\THESIS\TaxoArena_data\...` counts as "inside" `...\TaxoArena`: prep refuses it, and a leg's hook refuses the steward-file write and aborts | Either compare against `REPO_N + os.sep`, or state in the step list (done in section 5) that `<S>` must not start with the repo path string. Not required for the pin |
| RV4-3 | LOW (coverage) | The driver lacks cases for a changed line adjacent to L14 and for an E3 header off line 1. My R3 and R4 survive the builder's driver | Add my two cases (tm + L13, tm + L15; e3 with one preamble line) and my R1-R4 mutants to the driver in the RV4-1 delta. Recommended, not blocking |

## 4. Rulings on the builder's additions (a)-(e)

- **(a) `prep` (steps 0a + 0c in memory, ancestry, --out outside --repo): KEEP, and make it the REQUIRED path.** Its gates are all executed and killed (MP-pin-gate, MP-closure-0c, MP-ancestor, MP-out-exists). The hand path skips the ancestry check. With RV4-1 fixed the legs also refuse a non-b2 build, so prep and the legs become two independent gates on the same pin.
- **(b) Record-side L14 check: KEEP.** It turns "the record is the record" from an assumption into a check (MH1-rec-L14 killed). It also costs nothing on the real run: `<S>/rec_tie_mechanics_outcome.txt` comes from `git show HEAD:`.
- **(c) `--expect-lf` required on every leg and on score-vfc: KEEP, and tighten it per RV4-1.** Reading rerun_vf3.py L120-L122, a v3 leg without the flag compares raw16 to None and exits through the C-ii-1 message naming "None". That is not the crash the builder describes, but it is not a refusal by name either; I did not execute it. Required-and-equal-to-the-ruling's-pin is the fail-closed form.
- **(d) pia and tm refuse `--e3-log`: KEEP.** It prevents a transcript being attributed to a leg that does not use it (MH3-e3-vfc-only killed). It does not restrict anything the ruling asks for.
- **(e) The E3 header plus exact total plus `[PASS]` / `[FAIL]` line counts: KEEP.**
  - The format matches the instrument. `vote_frame_cert.py` L2749 prints the header, L2751 the total. The rv2 transcript has 472 lines starting `  [PASS]`, 0 starting `  [FAIL]`, and "SELFTEST PASS: 472 checks, 0 failed" at L474.
  - The declared limit stands: the check proves FORM, not provenance. My probe shows the 930ccc7 transcript passes.
  - The tie to b45b75db is therefore procedural. Step 3 below produces the log in the same step as the archive hash, and the registrar records the leg's printed log sha256 beside the E3 transcript's sha256 (they must be equal).
  - The `-O` transcript is not checked by the harness. The reviewer reads it.

## 5. Step list for the run-operator (after section 6's preconditions)

`M=Z:/FAC/TUBerlin/THESIS/TaxoArena`. The paths are constrained as follows:
- `<S>` is a NEW scratch directory whose path does NOT start with the string `Z:\FAC\TUBerlin\THESIS\TaxoArena` (so not `...\TaxoArena_data\...`; RV4-2). For example, the session scratchpad under `C:\Users\octav\AppData\Local\Temp\...`.
- `<H>` is a directory holding the PINNED, RV4-1-fixed `rerun_vf4.py`: `git -C $M show <merge commit>:experiment_results/vfc_fixes_2/harness/rerun_vf4.py > <H>/rerun_vf4.py`, then `sha256sum` equals the registrar's lf pin.

Use Git Bash. Print the admitted PIDs and the wall time of each leg (rule 7).

```
# 1. build (steps 0a + 0c; git objects only; refuses before extracting anything)
python <H>/rerun_vf4.py prep --repo $M --out <S>/T
#    must print: [PREP] ... is-ancestor ... rc 0; [0a] ... b45b75db7d98103e OK / 9c78d485f37f442a OK / d6a1a0409a0fc06e OK; CR 0;
#    [0c] ... 1 line(s): ['tools/analysis/vote_frame_cert.py']; [PREP] extracted
# 2. records of reference
for f in vote_frame_cert.txt vote_frame_cert.json position_index_all_outcome.txt x12_crossdomain/tie_mechanics_outcome.txt; do
  git -C $M show HEAD:experiment_results/$f > <S>/rec_$(basename $f); done
git -C $M rev-parse HEAD:experiment_results/vote_frame_cert.txt HEAD:experiment_results/vote_frame_cert.json \
  HEAD:experiment_results/position_index_all_outcome.txt HEAD:experiment_results/x12_crossdomain/tie_mechanics_outcome.txt
#    must print 8db4403f... 5ec19826... bb1578ca... a2df609d...
# 3. E3 (P3): selftests on THIS archive, in one step, with the archive's hash in the same record (selftests are admitted under rule 7)
sha256sum <S>/T/tools/analysis/vote_frame_cert.py <S>/T/tools/analysis/position_index_all.py <S>/T/tools/analysis/tie_mechanics.py > <S>/e3_archive_sha.txt
cd <S>/T && python    tools/analysis/vote_frame_cert.py    --selftest > <S>/e3_vfc_py.txt 2>&1   # SELFTEST PASS: 472 checks, 0 failed
            python -O tools/analysis/vote_frame_cert.py    --selftest > <S>/e3_vfc_O.txt  2>&1   # 472 / 0
            python    tools/analysis/position_index_all.py --selftest > <S>/e3_pia_py.txt 2>&1   # 55 / 0, +1 INFO
            python    tools/analysis/tie_mechanics.py      --selftest > <S>/e3_tm_py.txt  2>&1   # 29 / 0
sha256sum <S>/e3_*.txt
#    STOP if any count differs: that is a FINDING, not a leg precondition to work around.
# 4. the legs: ONE rule-7 window (W1-W5 probe FREE, >= 12 GB free RAM, no construction, no writer, no git write under src/), sequential
python <H>/rerun_vf4.py vfc --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --e3-log <S>/e3_vfc_py.txt --repo $M --out <S>/ii
python <H>/rerun_vf4.py pia --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --repo $M --out <S>/iii_pia
python <H>/rerun_vf4.py tm  --build <S>/T/tools/analysis --expect-lf b45b75db7d98103e --repo $M --out <S>/iii_tm
#    each: [BUILD] x3 with 0 CR; vfc: [E3] sha256 == the step-3 sha of e3_vfc_py.txt, [PRE] 62 of 62, [POST] 62 of 62 caches unchanged;
#    every leg: [C-ii-3] ... unchanged. A pool_guard refusal (non-empty -wal / -journal) is a FAILED PRECONDITION, never an outcome.
# 5. scoring (text only)
python <H>/rerun_vf4.py score-vfc --expect-lf b45b75db7d98103e --rec <S>/rec_vote_frame_cert.txt --new <S>/ii/vote_frame_cert.txt \
       --rec-json <S>/rec_vote_frame_cert.json --new-json <S>/ii/vote_frame_cert.json
python <H>/rerun_vf4.py score-pia --rec <S>/rec_position_index_all_outcome.txt --new <S>/iii_pia/position_index_all_outcome.txt
python <H>/rerun_vf4.py score-tm  --rec <S>/rec_tie_mechanics_outcome.txt --new <S>/iii_tm/tie_mechanics_outcome.txt
```

What the run-operator does with the results:
- Hand to the reviewer, raw: every transcript, every rc, `<S>/e3_archive_sha.txt`, and the F1 READOUT block.
- **If the F1 readout shows any unit moving to R6 and its `unresolvable_values` are all '':** stop. It goes to the arena-specialist (R2.5), and (ii) is not scored.
- **Any rc 3** is a FINDING for the reviewer and the registrar. It is not to be re-run until it passes.

## 6. What remains before the legs (step 4)

1. **RV4-1 fixed** on the branch, plus the RV4-3 cases and mutants (recommended). The driver re-run shows all cases MEET and all mutants KILLED, confirmed by me or any reviewer (about 10 s). No re-review.
2. **Merge by path** of the 100 (or more) files under `experiment_results/vfc_fixes_2/harness/`, then the ancestry check. **The registrar's pin of the FIXED rerun_vf4.py**: blob / sha256-lf16 / sha256-crlf16. a9fea8d20cf5446f is superseded by the fix and must not be pinned.
3. **P1 recorded** (variant C rc 3 on v4: S-vfc-C-v4) and **P2 recorded**, both by the registrar.
4. **P3, E3:** step 3 executed, with its transcripts and hashes recorded. It may run before the window.
5. **P4:** the arena-specialist's acknowledgement recorded, as owner of "is '' NULL?", before step 4.
6. **P5:** the registrar's record of this review. The queue item VFC-FIXES-2-DELTA-II-III gets script = the pinned v4 and ready_file = this file plus the confirmation of the RV4-1 delta.

## 7. Evidence (session scratchpad; zero calls)

- `v4r/driver.out`: my driver run.
- `v4r/tr/`: its 53 case and 38 mutant transcripts, plus SUMMARY.txt.
- `v4r/work/`: its variants, the prep archive T and the fake repo.
- `v4r/mine/rmut.py` and `rmut_out.txt`: my mutants R1-R4 and the new cases.
- `v4r/mine/b1/`: the RV4-1 probe (a 930ccc7 archive of the 3 instruments, the vfc leg's pre-check transcript, and `A_b1.txt` scored rc 0).

## 8. What this review does not show

- It does not show (ii) or (iii).
- It does not show that the E3 selftests of b45b75db pass: P3 has not run.
- It does not show that the audit hook refuses a real write during a leg. No leg passed rec_shas; the hook's code is unchanged from v3, whose refusals were executed in round 2.
- It does not show that the legs' C-ii-3 and [PRE]/[POST] behave on the real repo. They are unchanged from v3 and are exercised only by step 4.
