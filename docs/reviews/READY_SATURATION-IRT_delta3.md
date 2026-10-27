# DELTA READY review 3: SATURATION-IRT, the B1 / B2 / L-1 / L-2 fix of READY_SATURATION-IRT_delta2.md

Reviewed: `git diff 04b1e5aa..0463e92a -- tools/analysis/saturation_irt.py` (+180 / -13), branch `sat-irt-busyfix` (worktree
`.claude/worktrees/sat-irt-busyfix`), tip 0463e92a, one commit on 04b1e5aa (`merge-base --is-ancestor` OK; `git diff --name-only 04b1e5aa
0463e92a | wc -l` = 1; `git rev-list --count` = 1; worktree `status --porcelain | wc -l` = 0).
Blob: blob:2a50e83395c94a71113df14021eab1607f51fb9d (`git rev-parse 0463e92a:<path>` = `git hash-object <worktree path>`), sha256-lf16:a87fdb7ea86a29e5
(= the builder's), sha256-crlf16:6ae4629a019b8745. The worktree holds the CRLF rendering (python byte count: 2,575 CR in 154,867 bytes;
core.autocrlf true); the script's own identity line printed the same three values. Replaces READY-candidate blob:436f57f5.
Prior: READY_SATURATION-IRT.md, _delta.md, _delta2.md (code outside this delta is cited there, not re-derived). Authority D-2026-10-08-5.

## VERDICT: READY (for --dry-run, --pilot and --run), with conditions C2 (pilot before --run) and L-A (launch form).

## Per-claim table (deciding claims only)

| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | B2 fixed: the real `--dry-run` passes rule 7 and runs read-only | busy.ps1 rc 1 first; `--dry-run --data-root <main>` rc 0, 32 lines; line 2 `rule 7: ... exit 1 (free) ...; own process chain excluded: PIDs 84272,78552,18380,51904,8564,42032,23300,12700`. busy_check is called before `assert_pool_of_record` (L1280/L1301 vs L1153 path). multicorpus_cache_v1.db sha256 ad66e30a0eb4abd6 and checker_answers_v2.db 6cfaf74d647829d1 EQUAL before/after; `experiment_results/hf_blog` absent after | CONFIRMED | - |
| 2 | The fix hides only the caller's chain; peers still refuse | Own check: a SIBLING python with `peer_saturation_irt_sibling` in argv alive -> real `--dry-run` rc 1, `REFUSED: rule 7: busy.ps1 exited 0`. Java is read by busy.ps1's own `Get-Process java`, which the wrapper does not override. Own mutant R3 (the chain's children hidden too) KILLED | CONFIRMED | - |
| 3 | busy.ps1 unchanged | sha256 167422d8c3af5c12, mtime 2026-10-08 16:27:39 (= delta2's mtime); one `-match` pattern, names saturation_irt | CONFIRMED | - |
| 4 | B1 fixed: micro vs macro top-4 discriminated; X94 (= prior Y2) killed | X94 KILLED (43 s); prior Y2 (delta2's prior_mut.py re-pointed) KILLED; Y4 KILLED. Own RS1 (SAT4 alone on the micro top 4) KILLED; RS2 (theta_top4 alone on the micro top 4) KILLED | CONFIRMED | - |
| 5 | Selftest 17/17 | re-run (scratch_dir): `[SI] selftest: 17 / 17 passed` (busyself 9.1 s) | CONFIRMED | - |
| 6 | Mutants 102/102 killed, X00 survives | 10 chunks `--only X0..X9`: 9+13+8x10 = 102 KILLED; SURVIVED only X00; NOT APPLIED none | CONFIRMED | - |
| 7 | L-1 / L-2 done; no other path changed | diff = docstring brackets, BUSY_WRAP/busy_probe/busy_check, st_run_e2e skew + assertion, `_mm_skew`, `H_SHA_OF_RECORD` assert in st_labels, st_busyself, CASES, X41 re-anchored, X94-X102. No verdict, fit or print path outside busy_check changed (read of the full diff) | CONFIRMED | - |
| 8 | H pin of record present (delta2 C1) | `grep -n 6b010fa60dde7278... docs/judge_v2_program.md`: L25322 (deviation template) and L25355 "H TABLE PIN OF RECORD" (registrar 40cd6d41); CSV sha256 = H_SHA = H_SHA_OF_RECORD; the dry-run printed the scorer line with that sha | CONFIRMED (C1 MET) | - |

Reviewer's mutants (sandbox via scratch_dir; R0 control SURVIVED):
- R1 the parent CreationDate guard removed: SURVIVED. Not decisive (only a reused PID exercises it; it can only shrink the exclusion). LOW, as the builder disclosed.
- R3 children of chain members hidden (siblings of the caller vanish): KILLED. Decisive (rule 7).
- RS1 SAT4 on the micro top 4: KILLED. Decisive (SAT4).
- RS2 theta_top4 on the micro top 4: KILLED. Decisive (SI2 NEFF).

## Defects / conditions

- **C2 CONDITION (carried from delta2).** `--pilot 3` first; a REFUSE.HTABLE in the pilot stops the line before `--run`.
- **L-A LOW (both busy-fixed scripts).** The chain exclusion hides any ANCESTOR, including one whose argv matches busy.ps1's pattern. Own probe:
  a parent python with `win_map_fake_reader` in argv, child `busy_probe(BUSY_PS1, os.getpid())` -> rc 1 (free), while `busy_probe(..., -1)` -> rc 0.
  Fix (operator now; builder optional): launch only directly from a shell or via `scratch_dir.py --run --`, never from another pool-reading
  script; read the printed excluded PIDs (in my run: python, bash x2, claude.exe, pwsh, idea64, explorer). Optional code fix: refuse when an
  excluded ancestor other than the caller and a scratch_dir wrapper matches the pattern.
- **L-B LOW (record).** A git-bash `grep -c $'\r'` reports 0 on these CRLF files (it was 0 here; Python counts 2,575). Earlier reviews that
  stated "0 CR, LF on disk" from that command should be read with this caveat; the pins above are by Python and git.

## Commands (read-only; busy.ps1 rc 1 before every pool-touching step; zero calls; scratch E:/TaxoArena_tmp/rev_busyfix)
```
git diff --name-only 04b1e5aa 0463e92a | wc -l ; git rev-list --count 04b1e5aa..0463e92a          # 1 ; 1
git rev-parse 0463e92a:tools/analysis/saturation_irt.py ; git hash-object <worktree>/tools/analysis/saturation_irt.py   # 2a50e833 both
git show 0463e92a:<path> | sha256sum ; ... | sed 's/$/\r/' | sha256sum                            # a87fdb7ea86a29e5 ; 6ae4629a019b8745
python -c "open(p,'rb').read().count(b'\r')"                                                       # 2575 (CRLF working tree)
sha256sum E:/TaxoArena_tmp/busy.ps1                                                                 # 167422d8c3af5c12
busy.ps1 -> 1 ; (worktree) python tools/analysis/saturation_irt.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0; log sat_dry.log sha16 21a739072ae97d46
sha256sum multicorpus_cache_v1.db experiment_results/multicorpus/checker_answers_v2.db  before/after # EQUAL
python -c "sleep" peer_saturation_irt_sibling & ; --dry-run                                         # rc 1 REFUSED rule 7 (saturation_irt_sibling.log)
scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest                         # 17/17
for i in 0..9: scratch_dir.py --run -- python tools/analysis/saturation_irt.py --mutants --only X$i  # 102 KILLED, X00 SURVIVED
scratch_dir.py --run -- python rev_busyfix/own_mut.py sat                                           # R1 SURVIVED; R3, RS1, RS2 KILLED
scratch_dir.py --run -- python rev_busyfix/prior_mut_sat.py                                         # Y2, Y4 KILLED
python rev_busyfix/anc.py win_map_fake_reader                                                       # child rc 1 / unexcluded rc 0 (L-A)
grep -n 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1 docs/judge_v2_program.md   # L25322, L25355
```

## Run commands (operator; from the worktree until merged, or from main after a by-path merge of blob 2a50e833; busy.ps1 must exit 1 first; launch directly, L-A)
```
powershell -NoProfile -ExecutionPolicy Bypass -File E:/TaxoArena_tmp/busy.ps1        # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest
python tools/analysis/saturation_irt.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/saturation_irt.py --pilot 3 --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # C2: must pass before --run
python tools/analysis/saturation_irt.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena       # detached + Monitor (~3.5-4.5 h)
# back up the outcome to E:/TaxoArena_backup_20261009_saturation_irt with SHA256SUMS; never commit
```
