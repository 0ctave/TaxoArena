# DELTA READY review: HARNESS-EXTRACTOR, the B-1 / L-1 fix of READY_HARNESS-EXTRACTOR.md (c953775e), against rulings HX-R4/R1/R2 (da1ef992)

Reviewed: `git diff 703b198b..5f5acab5 -- tools/analysis/harness_extractor.py` (+172 / -11), branch `hx-busyfix` (worktree
`.claude/worktrees/hx-busyfix`), tip 5f5acab5, one commit on 703b198b (`merge-base --is-ancestor` OK; `git diff --name-only 703b198b
5f5acab5 | wc -l` = 1; worktree `status --porcelain | wc -l` = 0).
Blob: blob:06f569f8f8b918f2e9cd959c0c2d6f0d6da7fc1b (`git rev-parse` = `git hash-object`), sha256-lf16:d23a7fc0632542de (= the builder's),
sha256-crlf16:c6f1452a8a6e7bd4. The worktree holds the CRLF rendering (Python: 2,166 CR in 138,826 bytes); the script's identity line printed
the same. Replaces blob:947edb12. Code outside the delta: cited from c953775e, not re-derived.

## VERDICT: NOT READY / BLOCKED for --run on B-2 (HX-R4 not implemented). B-1 and L-1 are fixed (CONFIRMED); --dry-run is executable.

## Per-claim table (deciding claims only)

| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | B-1 fixed: real `--dry-run` passes rule 7, read-only | busy.ps1 rc 1 first; `--dry-run --data-root <main>` rc 0, 39 lines; `rule 7: ... exit 1 (free) ...; own process chain excluded: PIDs 47448,3184,80020,79040,8564,42032,23300,12700` (python, launcher, bash x2, claude.exe, pwsh, idea64, explorer); busy_check (L989/L1006) precedes `assert_pool_of_record` (L562). No HX/PREDICTION/SUPPORT/SENSITIVITY line (count 0). multicorpus ad66e30a0eb4abd6 and checker_answers_v2 6cfaf74d647829d1 EQUAL before/after; no output dir | CONFIRMED | - |
| 2 | Only the caller's chain is hidden | sibling python `peer_saturation_irt_sibling` alive -> real `--dry-run` rc 1, `REFUSED: rule 7 ... exited 0`. Own R3 (chain's children hidden) KILLED | CONFIRMED | - |
| 3 | L-1: closing line discloses the IFEval parse | dry-run last line = the new text, verbatim; X82 KILLED | CONFIRMED | - |
| 4 | Selftest 9/9; mutants 82/82, control survives | re-run: 9/9 (busyself 8.9 s); 9 chunks: 9+7x10+3 = 82 KILLED, SURVIVED only X00 | CONFIRMED | - |
| 5 | Prior decisive mutants still die | c953775e's O1-O8 (re-pointed) all KILLED, X00 SURVIVED | CONFIRMED | - |
| 6 | No other path changed | diff = docstring, BUSY_WRAP/busy_probe/busy_check, the dry-run closing line, st_dry_run assertion, st_busyself, CASES, X51 re-anchored, X74-X82 | CONFIRMED | - |
| 7 | H pin present (C-1) | prog L25355 "H TABLE PIN OF RECORD" 6b010fa6...d1d1; CSV sha256 equal; script H_SHA L234 equal | CONFIRMED (C-1 MET) | - |
| 8 | HX-R2 implemented | ck db via `PG.open_ro` + KeyTripwire sealing non_terminated in the dry-run (L659); `--run` SELECTs non_terminated only (L668); REFUSE.NT on a missing row | CONFIRMED | - |
| 9 | HX-R1 consistent | IS/IL from the per-model sample files, file name + sha printed as the "version" (docstring L64-L70); HX3 over {I0, IS, IL} with I0 = IS gives the IS-vs-IL pair's tau-b / shift (identical pair: tau 1, shift 0) | CONFIRMED (the row-by-row I0 = IS check is the post-run review's) | - |
| 10 | HX-R4 implemented (rule 8 refutes RANKS-MOVE iff all tau-b >= 0.85 AND max shift <= 2) | `rule8_hx1` L353 still `hx["max_shift"] < reg["move_bar"]` (3.0); docstring [HX-R4] "NOT resolved here"; at shift 2.5 it prints "RULE 8 (HX1): RANKS-MOVE is REFUTED" plus "REGISTRATION DEFECT HX-R4 REACHED", contrary to prog L25258 bracket / L25366. Own RH1 (the ruled form `<= reg["shift_bar"]`) is KILLED by the suite: the selftest (and X13) enforce the superseded rule | REFUTED | BLOCKER (B-2) |

Reviewer's mutants (sandbox via scratch_dir; R0 control SURVIVED): R1 CreationDate guard removed SURVIVED (not decisive; LOW, disclosed by the
builder); R3 children of chain members hidden KILLED (decisive, rule 7); RH1 rule 8 per HX-R4 KILLED (decisive: proves the shipped rule is the
superseded one, B-2).

## Defects and fixes

- **B-2 BLOCKER (registration as amended not implemented; outcome is write-once).** Fix: `rule8_hx1` -> `... and hx["max_shift"] <= reg["shift_bar"]`;
  RULE 8 texts "no model moves more than 2 ranks" / "a model moving more than 2 ranks"; drop the `HX1.DEFECT_R4` branch (now unreachable) from
  `run` and from the branch cover; docstring [HX-R4] -> "RESOLVED by the registrar (da1ef992, prog L25366): ..."; replace X13 by a mutant that
  restores `< reg["move_bar"]`, and add a fixture with every tau-b >= 0.85 and max shift 2.5 asserting "RANKS-MOVE is not refuted" so that
  mutant dies. Then a delta READY on the new blob (small: this fix plus regression).
- **L-A LOW.** Same as READY_SATURATION-IRT_delta3.md L-A: an ancestor matching busy.ps1's pattern is hidden (own probe: child rc 1, unexcluded
  rc 0). Launch only directly or via `scratch_dir.py --run --`; check the printed excluded PIDs.
- **L-B LOW (record).** c953775e said "the working tree is LF, 0 CR bytes"; the present worktree is CRLF (Python count) and git-bash
  `grep -c $'\r'` reports 0 on it. Pins above are by Python and git.

## Commands (read-only; busy.ps1 rc 1 before every pool-touching step; zero calls; scratch E:/TaxoArena_tmp/rev_busyfix)
```
git diff --name-only 703b198b 5f5acab5 | wc -l                                                      # 1
git rev-parse 5f5acab5:tools/analysis/harness_extractor.py ; git hash-object <worktree path>         # 06f569f8 both
git show 5f5acab5:<path> | sha256sum ; | sed 's/$/\r/' | sha256sum                                   # d23a7fc0632542de ; c6f1452a8a6e7bd4
busy.ps1 -> 1 ; (worktree) python tools/analysis/harness_extractor.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0; hx_dry.log sha16 1e78dcbece90d609
sha256sum multicorpus_cache_v1.db experiment_results/multicorpus/checker_answers_v2.db before/after  # EQUAL
python -c "sleep" peer_saturation_irt_sibling & ; --dry-run                                          # rc 1 REFUSED rule 7
scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest                       # 9/9
for i in 0..8: scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants --only X$i # 82 KILLED, X00 SURVIVED
scratch_dir.py --run -- python rev_busyfix/own_mut.py hx                                             # R1 SURVIVED; R3, RH1 KILLED
scratch_dir.py --run -- python rev_busyfix/prior_mut_hx.py                                           # O1-O8 KILLED
grep -n "max_shift\"\] < reg\|move_bar" tools/analysis/harness_extractor.py                          # L353 rule 8 at < 3 (B-2)
```

## Run commands (ONLY after the B-2 fix and its delta READY; busy.ps1 must exit 1 first; launch directly, L-A)
```
powershell -NoProfile -ExecutionPolicy Bypass -File E:/TaxoArena_tmp/busy.ps1        # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest
python tools/analysis/harness_extractor.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/harness_extractor.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome + figure json to E:/TaxoArena_backup_20261009_harness_extractor with SHA256SUMS.txt; never commit
```
