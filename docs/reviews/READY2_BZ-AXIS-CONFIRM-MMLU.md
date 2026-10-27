REVIEW: READY-2
REGISTRATION: BZ-AXIS-CONFIRM-MMLU
REGISTRATION-COMMIT: f53ec853
VERDICT: READY

# READY-2 review (delta, the gate before the ONE vault read): BZ-AXIS-CONFIRM-MMLU

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena `_as_of f6402011`; benchzoom master dfeb0aa (tree clean: `git status
--porcelain | wc -l` = 0 before and after). Zero LLM calls. The vault was NOT opened: every real-data read below went
through `guard.masked()` and ended with guard reads helm 0 / tinyb 0. Nothing was written under E:/benchzoom_demo or in the
benchzoom checkout; all stubs ran in the sandbox E:/TaxoArena_tmp/ready2_mmlu_review (clone at dfeb0aa, fake TaxoArena repo).
Delta scope: `git diff d17fba1 dfeb0aa` = 1 line (SECTION_SHA "PENDING" -> 8a39c2e7...). Library and fetch code are covered
by DELTA_BZ-AXIS-CONFIRM-MMLU-WORK1 (590937f2), FETCH (0e1333c2), FETCH2 (70c674dd) and READY1 (62ca27c1); not re-derived.

Pins (git blobs, LF of record; the working tree is LF, so `hash-object --no-filters` gives the same value):
runner `examples/axis_confirm_mmlu.py` blob:aec30584c6b3f787857cf62cce673efa6655956f (= `rev-parse dfeb0aa:`);
`src/benchzoom/irt.py` blob:57ccac737e1172f1265db2cbf0d1333d25f8a520; library tree `dfeb0aa:src/benchzoom` = `d17fba1:src/benchzoom`
= c9809e9898198093a61755b47ec1c1b7c2e72026; programme `docs/judge_v2_program.md` blob:d6a383e0 at f6402011 (working tree = HEAD).

## Verdict

**READY** (READY-2): authorises ONE vault read with `axis_confirm_mmlu.py vault`, at benchzoom dfeb0aa, into
E:/benchzoom_demo/mmlu_confirm/vault_read. Conditions V1-V4 below bind the operator and the post-run review. C1 of READY-1 and
of 590937f2 (synthetic gate on the merged library at the vault-time blob) is CLOSED (row 4). C2 of READY-1 (SECTION_SHA,
insertion only) is CLOSED (rows 1-2). C3 (settlements 1-3, D4, D6; DEFF / n_eff / MDE80 beside C-M1) is CLOSED (rows 3, 7).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | SECTION_SHA 8a39c2e7...a294a162 reproduces from the committed section | own cutter (heading to the line before the next `## `, LF, trailing LF), not the runner's: f6402011 = HEAD = working tree = 8a39c2e71850187cdb55e23c39d2779ba31144d523db0369f4d17e226294a162, 72 lines, L25503-L25574 (L25574 blank); f53ec853 = 47d6f4c3 (59 lines), as READY-1 recorded; results JSON line 12 carries the same sha | CONFIRMED (digit) | - |
| 2 | [A1] is insertion-only vs f53ec853 | section diff: 0 lines removed, 13 added (hunks 2a3, 27a29, 41a44, 58a62-71); programme `git diff --numstat f53ec853 f6402011` = 13 / 0; f6402011 is the only commit on the programme in that range | CONFIRMED | - |
| 3 | [A1] faithful to work_run.log | log L1: 09:33:00, blob 01e40f15, benchzoom d17fba1, irt 57ccac73, threads 1; L2: 79 kept, E5 (v) none, E5 (vi) 0, the 4 ids; tau^2 line, Spearman +0.2219, 15 re-cut lines, condition (f) line, `vault response reads: 0` (L22), HARNESS PASSED (L26/L33), nulls 200 (L27-29), exit 0 at 10:17:40 (L61): every [A1] number equals the log. C2 disclosures present (7 HELM + 6 tinyB raised, 1 + 2 at 1 ulp, weak models named) | CONFIRMED | - |
| 4 | synthetic gate PASSED at the vault-time blob on the merged library | `calibration_synthetic_aec30584c6b3/`: gate.txt PASSED, `runner blob aec30584...`; 4/4 meta `runner_blob` = aec30584; outcome.json written 10:26:17-10:28:28, after commit dfeb0aa (10:26:01), library tree c9809e98; `sha256sum -c SHA256SUMS` 21/21 OK; the 4 outcome.json = a0d7fd1a / 20f6133c / 921dfc15 / 5f3d14d4, byte-identical to the 01e40f15 gate (expected: the damped Newton takes full steps on the fixtures, 590937f2 row 2) | CONFIRMED | - |
| 5 | vault refusals hold and refuse a bad state | sandbox stubs on `vault_refusals` (real runner blob, patched TAXOARENA / OUT_VAULT): good state passes; REFUSED on VERDICT NOT READY, READY WITH EDITS, two VERDICT lines, trailing text, REVIEW READY-1, READY2 modified vs HEAD, READY2 untracked; section with one inserted line; uncommitted edit in src, untracked file in src, edit to fetch_zoom_data.py; synthetic meta of a foreign blob, planted outcome not SUPPORTED, synthetic dir absent, changed runner blob; no support_recut.json; vault_read/outcome.json present; `confirm_core` on an existing outcome.json (write-once). PASSES (gaps, see D2): a COMMITTED library change after the gate; an edit outside the section (by design, READY-1 D4) | CONFIRMED with D2 | LOW |
| 6 | vault read applies the WORK-selected tau^2 | code: vault mode re-selects with `prevault_fit` (the same call as `run_work`'s full-WORK fit) and does NOT compare with support_recut.json (D1). Execution: `load_real` + `prevault_fit` at aec30584 / c9809e98, threads 1: readers {L3a 0.02, L3a1 0.08, diff 0.16, len 0.005, L3ac 0.01, grp 0.04, L1g 0.08} == [A1] (dict equality True); WORK Spearman 0.22192954941737622, |diff| 0.0 vs the record (the vault mode's 1e-12 check would pass); fit rows 8,425, scored rows 5,530, guard reads 0 | CONFIRMED (by execution) | MEDIUM (D1) |
| 7 | DESCRIPTIVE-ONLY applied as registered | `main` vault: `descriptive_only=bool(rec["condition_f"]["fired"])`, support_recut.json fired True; render prints "C-M1 is DESCRIPTIVE-ONLY (Support condition (f) fired before the vault opened): its word ... decides nothing" and suppresses the FAILS line; PM1-PM6 still scored (as [A1]); C-M1 Support line prints DEFF, n_eff, MDE80. Deviation: the FALSIFIER line is suppressed too ([A1]: "printed and overturns nothing") and the C-M1 word carries no "(DESCRIPTIVE-ONLY by support)" suffix (D4) | PARTLY | LOW (D4) |
| 8 | condition (f) arithmetic | support_recut.json: vault SE = SE x sqrt(n_pseudo / 5,530), MDE80 = 3.84 x vault SE: 0.107665 / 0.112232 / 0.112348 / 0.110124 / 0.112532 (= file to 6 dp); median 0.112232 >= 0.10 -> FIRED; DEFF 1.8805-2.0437, n_eff = n / DEFF reproduces (1777.1 ... 1652.7) | CONFIRMED (digit) | - |
| 9 | vault id set and exclusions match the census | census/vault_ids.txt 5,614 d3a0b5ce, work 8,428 0ad5fd11, dropped 83 4ad91d7b (all = PINS); V and W disjoint, union 14,042, dropped within vault; the 4 not-one-correct ids sha c8c2edad (= PIN): vault 1 (international_law/51), WORK 3, none among the 83; kept scored vault = 5,614 - 83 - 1 = 5,530 = `n_vault_kept` | CONFIRMED (digit) | - |
| 10 | WORK touched no vault response | support_recut.json `vault_reads` 0; log L22; `run_work` asserts `guard.reads == 0` on every roster before returning (exit 0); my own masked re-read: reads 0 / 0; E:/benchzoom_demo/mmlu_confirm/vault_read absent | CONFIRMED | - |
| 11 | fetch pins verify | `sha256sum -c SHA256SUMS_fetch3` (in E:/benchzoom_cache/mmlu_confirm): 86 / 86 OK, 0 not OK (79 HELM parts + 3 csv + tinyB parquet, lb.pickle, cais parquet 74a41822, ref); written 07:57, before the WORK run (09:33) | CONFIRMED | - |
| 12 | WORK outputs unchanged | `sha256sum -c SHA256SUMS_work1rerun` 9 / 9 OK; work_exploratory SHA256SUMS and SHA256SUMS_recut OK | CONFIRMED | - |
| 13 | suite | benchzoom .venv, BLAS 1 thread, TMP in sandbox: test_axis_confirm_mmlu + test_execution_graph_sync + test_helm_part_names + test_irt_slope_damped + test_fetch_more: 172 passed, 1 skipped; sandbox baseline test_axis_confirm_mmlu 64 passed | CONFIRMED | - |

## Conditions (bind the operator and the post-run review)

- **V1 (code state):** run at benchzoom HEAD dfeb0aa with `HEAD:src/benchzoom` = c9809e98 and runner blob aec30584; print both
  (`git rev-parse HEAD HEAD:src/benchzoom`) at the top of the run log. A committed library change would pass the gate (D2).
- **V2 (threads / tau^2):** run with OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1 (as the WORK run and row 6).
  The post-run review checks the logged "[helm] WORK-side tau^2 ... readers" line and meta.json `rosters.helm.tau2.readers`
  equal the [A1] values exactly; a mismatch voids the read as the registered one (D1).
- **V3 (inputs):** immediately before the run, `sha256sum -c SHA256SUMS_fetch3` in E:/benchzoom_cache/mmlu_confirm prints 86
  OK and 0 FAILED (the vault mode does not hash the parts, D3).
- **V4 (record):** no insertion into the registration section (L25503-L25574) before the vault read completes: any edit there
  changes the section sha and refuses the read (row 5). The outcome record quotes C-M1's word with "(DESCRIPTIVE-ONLY by
  support)" and states the falsifier from the C-M1 word as "overturns nothing" (D4).

## Defects (none blocks READY-2)

- **D1 (MEDIUM)** the vault mode re-selects tau^2 and never compares it with support_recut.json `tau2_full_work` before arming
  the guard; the read is one-shot. Row 6 shows the recomputation is identical today. Fix (next runner revision; changes the
  blob, so the synthetic gate would re-run): refuse in `main` vault if `pre["helm"]["readers"] != rec["tau2_full_work"]`,
  checked before `guard.arm()`. Until then: V2.
- **D2 (LOW)** = open D-M1 of 590937f2: the synthetic gate binds the runner blob only (stub G1: a committed src change passes).
  Fix: record `HEAD:src/benchzoom` in the synthetic meta and refuse on mismatch. Until then: V1.
- **D3 (LOW)** `load_real` opens every `*.parquet` under helm_parts without checking them against SHA256SUMS_fetch3. Fix: verify
  the 79 part shas (or the file) in `vault_refusals`. Until then: V3.
- **D4 (LOW, wording)** under DESCRIPTIVE-ONLY, `render` drops the FALSIFIER line, and the C-M1 line prints the bare word. No
  decision changes (the word decides nothing). Fix: print "FALSIFIER: <fired/not fired> (C-M1 <word>, DESCRIPTIVE-ONLY by
  support): overturns nothing" and add the suffix. Until then: V4.
- **Note** `calibration_synthetic_167e58074ceb/` (an intermediate runner blob, not pinned anywhere) PASSED too; it binds nothing,
  because the gate is keyed on aec30584.

## Own mutants (sandbox clone at dfeb0aa; tests/test_axis_confirm_mmlu.py, baseline 64 passed)

M1 READY-2 exact-line check `rstrip() !=` -> `startswith`: killed (decisive). M2 section-sha check disabled: killed
(decisive). M3 vault `descriptive_only` -> False: killed (decisive). M4 vault outcome-exists refusal disabled: killed
(decisive). 4 / 4 killed; sandbox restored (porcelain 0 lines).

## Operator command (benchzoom master, Git Bash)

```
cd Z:/FAC/TUBerlin/benchzoom && git rev-parse HEAD HEAD:src/benchzoom && git status --porcelain | wc -l   # dfeb0aa, c9809e98, 0
(cd E:/benchzoom_cache/mmlu_confirm && sha256sum -c E:/benchzoom_demo/mmlu_confirm/SHA256SUMS_fetch3 | grep -vc ': OK$')  # 0
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/Scripts/python examples/axis_confirm_mmlu.py vault \
  --registration Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/reviews/READY1_BZ-AXIS-CONFIRM-MMLU.md \
  --ready2 Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/reviews/READY2_BZ-AXIS-CONFIRM-MMLU.md 2>&1 | tee E:/benchzoom_demo/mmlu_confirm/vault_run.log
```
Then SHA256SUMS of vault_read/ and the backup to E:/TaxoArena_backup_<date>_axis_confirm_mmlu (registration GUARD).

## Commands (read-only on every object of record)

```
git -C benchzoom diff d17fba1 dfeb0aa; hash-object / rev-parse dfeb0aa:{runner,src/benchzoom}; d17fba1:src/benchzoom
python -I scratchpad/sec.py f53ec853 f6402011 HEAD WT; diff sec_f53ec853.txt sec_f6402011.txt | grep -c '^<'   # 0 (13 '>')
git diff --numstat f53ec853 f6402011 -- docs/judge_v2_program.md                                                # 13 0
grep -n ... E:/benchzoom_demo/mmlu_confirm/work_run.log (61 lines, read whole)
sha256sum -c calibration_synthetic_aec30584c6b3/SHA256SUMS | grep -c ': OK'  # 21 of 21; meta runner_blob x4
python -I -c "<support_recut.json: vault SE, MDE80, median, n_eff>"; python -I -c "<census id files: shas, overlaps, 5,530>"
sha256sum -c SHA256SUMS_fetch3 (86 OK, 0 not OK); sha256sum -c SHA256SUMS_work1rerun (9 OK)
E:/TaxoArena_tmp/ready2_mmlu_review/stubs.py   # row 5 (sandbox clone + fake TaxoArena git repo)
E:/TaxoArena_tmp/ready2_mmlu_review/tau.py     # row 6 (load_real + prevault_fit, guard.masked only, reads 0/0; 519 s)
E:/TaxoArena_tmp/ready2_mmlu_review/mut.sh     # M1-M4
.venv/Scripts/python -m pytest -q -p no:cacheprovider tests/test_{axis_confirm_mmlu,execution_graph_sync,helm_part_names,irt_slope_damped,fetch_more}.py
```
