REVIEW: READY-2
REGISTRATION: BZ-MMLUPRO-MOREMODELS
REGISTRATION-COMMIT: f53ec853
VERDICT: READY

# READY-2 review (delta, the gate before the ONE vault read): BZ-MMLUPRO-MOREMODELS

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena `_as_of e67075f5` (programme blob:065e25c1 = 1aa43079 = HEAD = working tree);
benchzoom master 233b2f3 (tree clean, `git status --porcelain | wc -l` = 0 before and after). Zero LLM calls. The vault was
NOT opened: every real-data read below went through `guard.masked()`, the guard was never armed, reads 0 asserted at the
end of each script. Stubs ran in the sandbox E:/TaxoArena_tmp/ready2_more_review (clone at 233b2f3, fake TaxoArena repo,
copies of the gate and support_recut.json); E:/benchzoom_demo/mmlu_pro_more: 57 files, sha256 list identical before and after.
Delta scope: `git diff dfeb0aa 233b2f3` = 1 line (SECTION_SHA "PENDING" -> b99772da...). Since READY-1 (9f6182f) the code under
the runner's CLEAN_CODE paths changed in 2 files only: src/benchzoom/irt.py (covered by DELTA_BZ-AXIS-CONFIRM-MMLU-WORK1,
590937f2) and src/benchzoom/sources.py (D5 fix; the fetcher, not on the read path). Runner logic otherwise = READY-1 (2a6824cf).

Pins (git blobs; LF is of record; the working tree is CRLF, so both renderings are named):
runner `examples/mmlupro_more.py` blob:306066ea8e6953fe3ad12320da616fefd505de7a (LF, `git hash-object` = `rev-parse
233b2f3:`; CRLF rendering `hash-object --no-filters` = blob:53eda48a088d9d14c7990c09588aa6ac27b7fbef); `src/benchzoom/irt.py`
blob:57ccac737e1172f1265db2cbf0d1333d25f8a520; library tree `233b2f3:src/benchzoom` = `dfeb0aa:` = `d17fba1:` =
c9809e9898198093a61755b47ec1c1b7c2e72026 (9f6182f: 800ca1ba); SECTION_SHA b99772da7906207b2ef9a6d9d29d0f3244703011230032930a19cbb810bf8708.

## Verdict

**READY** (READY-2): authorises ONE vault read, `mmlupro_more.py vault`, at benchzoom 233b2f3, into
E:/benchzoom_demo/mmlu_pro_more/vault_read (absent), with 8 BLAS threads. Conditions V1-V5 bind the operator and the post-run
review. Registrar conditions (1)-(3) of the [A1] block: CLOSED (rows 4, 6, 1). READY-1 C1: CLOSED by this file.

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | SECTION_SHA b99772da reproduces from the committed section; the runner accepts it | own cutter (heading to the line before the next `## `, LF, trailing LF), not the runner's: 1aa43079 = HEAD = working tree (CRLF, normalised) = b99772da...bf8708, 68 lines, L25575-L25642 (L25642 blank); f53ec853 and efd48179 = e4b5111c (54 lines), as the results JSON says; runner constant = results JSON `registration.section_sha256` = same; the runner's own `section_text` on the working tree: equal (True) | CONFIRMED (digit) | - |
| 2 | [A1] is insertion-only vs f53ec853 | section diff f53ec853 -> 1aa43079: 0 lines removed, 14 added (hunks 2a3, 13a15, 20a23, 27a31, 38a43, 53a59-67); programme `git diff --numstat f53ec853 HEAD` = 49 / 0 (f6402011, 663cb7d2, 1aa43079) | CONFIRMED | - |
| 3 | [A1] faithful to work_run.log, incl. the library disclosure and D1/D2 | log read whole (50 lines, sha256 2c3f802e = the record): CMD line (threads 6, blob fc8f5adc, head 9f6182f, 03:43:06Z), tau^2 line verbatim, weak half 160 / 320 / 0.2994, 5 C-P1 lines (DEFF 3.747/3.856/3.839/4.409/3.852, n_eff 769/747/750/653/748, vault SE 0.0132-0.0144, MDE80 0.0507/0.0519/0.0519/0.0555/0.0520), g +0.0398/+0.0468/+0.0330/+0.0361/+0.0138, C-P2 DEFF 4.269-4.944 and MDE80 0.1114-0.1198, condition (f) line, `vault response reads: 0`, EXIT 0 11:04:06Z: every [A1] number equals the log. Disclosure: `rev-parse 9f6182f:src/benchzoom/irt.py` = 0a96771d, `dfeb0aa:` = 57ccac73, runner fc8f5adc at both 9f6182f and dfeb0aa: as written. D1/D2 bracket = READY-1 D1/D2 | CONFIRMED | - |
| 4 | the merged library reproduces the [A1] full-WORK tau^2 | OWN recompute (`rv_tau.py full`, 8 BLAS threads, head 233b2f3, src c9809e98, irt 57ccac73, `load_more` behind the real READY-1 gate, `T.prevault` + `A.axis_fit` on the masked matrix): chain L1=0.04, L2=0.04, L3t=0, fb=0.04, fl=0.01, fk=0.02, fk0=0.02, L3t1=0.01, fb1=0.04, fl1=0.02, fk1=0.04, L2c1=0.04; axis L3a=0.01, L3a1=0.02: string-equal to the [A1] line, dict-equal 14 / 14 (chain True, axis True); 4,738 s; guard reads 0, never armed. The builder's re-check (6 threads, 6,086 s) agrees; its shadow of the pre-fix irt on this fit (1,920 calls: 0 raise, 34 differ by at most 1 ulp) is consistent with it | CONFIRMED (value for value) | - |
| 5 | C-P1 Support lines and condition (f) | arithmetic from support_recut.json (0609ff50): vault SE = SE x sqrt(2880 / 4654), MDE80 = 3.84 x vault SE, n_eff = n / DEFF: all 10 lines equal the file and the log (abs diff 0.0); median 0.051931, min 0.050663, max 0.055457 < 0.10: NOT fired. Merged library, own: pseudo k = 1 at the [A1] tau^2 (`rv_tau.py recut 1`, 8 threads): C-P1 g +0.0398 SE 0.0168 DEFF 3.747 n_eff 769 (n 2880), vault SE 0.0132, MDE80 0.0507 = the log line; max abs(merged - [A1]) over g, SE, DEFF, n_eff, vault SE, MDE80 = 2.1e-17 (g 0.03981550296956248 vs ...246; SE and MDE80 bit-equal); C-P2 5.6e-17 | CONFIRMED (digit) | - |
| 6 | synthetic gate PASSED at the vault-time blob and binds to it | `calibration_synthetic_306066ea8e69/`: gate.txt PASSED (null DEGENERATE g 0 SE 0; planted SUPPORTED g +13.5763 SE 1.7413), `runner blob 306066ea...`; 2 / 2 meta `runner_blob` = 306066ea; written 13:17:27-13:17:45 +0200, after commit 233b2f3 (13:16:48 +0200); `sha256sum -c SHA256SUMS` 13 / 13 OK (file sha 3cd481d5); outcome.json / outcome.txt / nulls.json / harness.json byte-identical to the fc8f5adc gate, meta.json differs in the key `runner_blob` only; `synthetic_refusal(E:/benchzoom_demo/mmlu_pro_more, runner_blob())` = None | CONFIRMED | LOW (READY-1 D4 inherited) |
| 7 | vault refusals hold and refuse bad states | 32 / 32 sandbox stubs as expected (`stubs.py`; real runner code, patched TAXOARENA / OUT_VAULT): good state PASS; REFUSED on VERDICT NOT READY, a second decorated `**Verdict**:` line, `VERDICT: READY with conditions`, REVIEW READY-1, other REGISTRATION, READY2 modified vs HEAD, READY2 untracked; one line inserted in the section, one char changed in the section (committed); uncommitted irt.py edit, untracked file in src, meter_axis.py edit; synthetic meta of a foreign blob, synthetic dir absent, planted outcome not SUPPORTED, changed runner blob; no support_recut.json; vault_read/outcome.json or meta.json present; a PIN or SECTION_SHA PENDING; `more_core` into a dir holding outcome.json (write-once). `main` vault: all good -> loader reached; bad READY-1 -> rc 2; READY2 NOT READY, synthetic absent, `--ready2` omitted, weak half differing from the frozen one -> refused before / at the loader. PASS by design or gap: whole programme CRLF; an edit OUTSIDE the section; a COMMITTED src change (D2) | CONFIRMED with D2 | LOW |
| 8 | the vault read applies the WORK-selected tau^2 | code: `more_core` re-selects with `T.prevault` + `A.axis_fit` (the same calls as `run_work`'s full-WORK fit) before meta.json, then asserts the opened chain's tau^2, WORK-row eta and axis tau^2 equal the WORK-side ones; it never compares with support_recut.json (D1). Execution: row 4 | CONFIRMED (by execution) | MEDIUM (D1) |
| 9 | the registered words exactly | `level_word`: DEGENERATE (tau^2 = 0) > NOT SUPPORTED (g <= q95 or g + 2 SE < 0.10) > SUPPORTED (g >= 3 SE, g > q95, g >= 0.10) > BELOW INTEREST > INCONCLUSIVE, on the POINT; DELTA_MIN 0.10, R_NULL 200, null stream [20261021, 18, r], MDE_K 3.84; CRITERIA (C-P1 all / L3a-L2 / reader L3a, deciding), PP1-PP4 intervals and word sets, C_P1_FAIL_WORDS, falsifier = registration text; `descriptive_only` = support_recut `condition_f.fired` = False, so the FAILS and FALSIFIER lines print (mutant X3 killed). Spot check; the rest is READY-1's | CONFIRMED | - |
| 10 | roster 343 = 23 + 320, 5 exclusions, Hermes-3 kept; weak half frozen | `load_more` (masked): 320 models, ids_sha f7fd0db5, subsets 320 / 160 / 315 / 307; Hermes-3-Llama-3.1-8B in the roster, 0 of the 5 excluded names in it; census.json 2dcc243f, excluded.csv = the 5 names (D2 label "(2)" still printed, bracketed); own weak half (plain mean over WORK rows; 0 NaN on WORK rows; 0 ties at the median): 160 models = weak_half.json list, median 0.299360844796443 bit-equal; weak_half.json sha256 1308ca67 | CONFIRMED (digit) | - |
| 11 | vault item set and part pins | `load_dataset("mmlu_pro")` pin checks passed (atlas, embeddings, parquet, vault ids 5c05640d, dropped 4cd9a0a8); WORK 7,197, kept vault 4,654, clusters 4,625, fit AND score 0, every score row NaN in the masked matrix; `sha256sum -c parts_SHA256SUMS` 343 OK / 0 not OK (320 oll_parts_more + 23 oll_parts); file sha 4e23857f = sha256 of `HEAD:docs/mmlupro_more_parts_SHA256SUMS.txt` (9f6182f); oll_parts_more 320 parquet, 0 files newer than census.json (`find -newer | wc -l`); the vault mode re-hashes each of the 320 parts (`roster_matrix`) | CONFIRMED | - |
| 12 | Support (non-vacuous; check 8) | registration (b)-(e): 3.84 x 0.0183 = 0.0703, 4,654 / 1.1257 = 4,134.3, DEFF source = the 23-model cache [M5]; constant-ICC 1 + 0.005714 x 319 = 2.82 at 320 models; [A1] re-measure reproduces (row 5): realised DEFF 3.75-4.41 > 2.82 projected, but the carried SE 0.0183 > re-measured vault SE 0.0132-0.0144, max MDE80 0.0555 < 0.10: SCOREABLE stands; `render` prints DEFF, n_eff, MDE80 beside C-P1 | CONFIRMED | - |
| 13 | authority covers exactly this read | D-2026-10-21-3 verbatim at author_decisions/2026-10-21.md L22 (ca7728d7): "limited to BZ-MMLUPRO-MOREMODELS on MMLU-Pro"; one read: vault_read write-once (stubs R21, R22, W1); no other MMLU-Pro vault opening since registration (2026-10-22.md L6 "no new reserved-side opening"; POSTRUN_MMLU-GAP-BASELINE: WORK only, reads 0); so this is the 4th | CONFIRMED | - |
| 14 | suite and selftest at 233b2f3 | sandbox clone, 1 BLAS thread: test_mmlupro_more + test_execution_graph_sync + test_irt_slope_damped 107 passed; `--selftest` OK (planted SUPPORTED, null DEGENERATE) | CONFIRMED | - |
| 15 | backups | E:/TaxoArena_backup_2026-10-22_mmlupro_gate2 `sha256sum -c` 22 / 22 OK (top file 6255c604); E:/TaxoArena_backup_20261022_mmlupro_more_work SHA256SUMS_work 11 / 11 OK; record SHA256SUMS_work 11 / 11 OK | CONFIRMED | - |

## Threads (decided): 8 BLAS threads

OMP / OPENBLAS / MKL_NUM_THREADS = 8. Evidence: the full-WORK tau^2 selection (the only discrete choice the read makes
before scoring) is identical at 6 threads ([A1], pre-fix library; builder re-check, merged library) and at 8 threads (row 4,
merged library); the pseudo k = 1 C-P1 / C-P2 statistics move by at most 5.6e-17 between [A1] (6 threads, pre-fix) and my
run (8 threads, merged). 10 threads is untested, so it is not chosen. Dependence: none at the printed precision and none in
any word. OpenBLAS thread count can change the last bits of reductions; a word changes only if g sits within about 1e-12 of
3 SE, q95 or 0.10 - 2 SE, or a CV objective ties on the tau^2 grid at that level; neither happened at 6 vs 8. V2 makes the
tau^2 identity a post-run check. Time: the full-WORK fit took 4,738 s at 8 threads (6,086 s at 6 in the builder's run; other
load not controlled); the read is that fit + the opened-chain fit (about 1.1x, dress rehearsal) + harness + 200 nulls on
11,851 rows: about 3-3.5 h at 8 threads (about 4 h at 6).

## Conditions (bind the operator and the post-run review)

- **V1 (code state):** benchzoom HEAD 233b2f376f859caee2edcfff98207dfbf54564ec, `HEAD:src/benchzoom` c9809e98, runner LF blob
  306066ea, `git status --porcelain` 0 lines; printed on the CMD line of vault_run.log. A committed library change after this
  review passes the runner's gates (D2), so a different HEAD is a failed precondition: do not run, re-gate.
- **V2 (threads / tau^2):** OMP / OPENBLAS / MKL_NUM_THREADS = 8. The post-run review checks that the log line
  "[mmlu_pro_more] WORK-side tau^2: chain ...; axis L3a=0.01, L3a1=0.02" and meta.json `tau2` / `tau2_axis` equal the [A1]
  values reader for reader; a mismatch voids the read as the registered one (D1).
- **V3 (record):** no edit of programme L25575-L25642 (the blank L25642 included) and none of READY1_ / READY2_ files until the
  read has completed: any change refuses the read (stubs R8, R9, R6). The registrar records this review in a new
  "## Registrar's record" section placed after L25642, not inside the section.
- **V4 (interpreter / inputs):** `.venv/Scripts/python` of the benchzoom master checkout (imports Z:/FAC/TUBerlin/benchzoom/src;
  the system python has no benchzoom); vault_run.log and vault_read/ absent before the run.
- **V5 (post-run):** SHA256SUMS over vault_read/ plus vault_run.log, backup to E:/TaxoArena_backup_<date>_mmlupro_more_vault
  verified by `sha256sum -c`; the POSTRUN recomputes C-P1 from outcome.json and quotes DEFF, n_eff and MDE80 beside it; every
  quotation carries "RE-TEST, NOT fresh; 4th opening of the BZ-METER vault items".

## Defects (none blocks READY-2)

- **D1 (MEDIUM)** the vault mode re-selects tau^2 and never compares it with support_recut.json `tau2_chain` /
  `tau2_full_work` before `guard.arm()`; the read is one-shot. Rows 4 and 8 show the recomputation is identical today. Fix
  (next runner revision; changes the blob, re-gate): pass the [A1] values into `more_core` and refuse before meta.json on any
  difference. Until then V2. (Same defect as READY2_BZ-AXIS-CONFIRM-MMLU D1, carried into this runner.)
- **D2 (LOW)** the synthetic gate and the clean-code check bind the runner blob and uncommitted edits only; a COMMITTED src
  change passes (stub R15). Fix: record `HEAD:src/benchzoom` in the synthetic meta and refuse on mismatch. Until then V1.
- **D3 (LOW)** mutant X2 (READY-2 exact-line check `!=` -> `startswith`) SURVIVES the test suite: no test feeds
  "VERDICT: READY <suffix>". The code is right (stub R3 refused). Fix: add that test.
- **D4 (LOW)** `ready2_refusal` accepts `docs/reviews/READY2_<id>.md` of ANY git work tree (not bound to TAXOARENA), and its
  `relative_to` is unguarded (a ValueError traceback instead of a refusal; still fail-closed). Fix: require the work-tree root
  == TAXOARENA.resolve(). The operator command below passes the TaxoArena path.
- **Note** the vault mode reads condition (f) and the weak half from the pre-fix [A1] support_recut.json; the weak half is
  recomputed at vault time and compared (stub M5), and condition (f) sits 0.0445 below the bar at its max (row 5).

## Own mutants (sandbox clone at 233b2f3; tests/test_mmlupro_more.py, baseline 69 passed)

X1 vault section-sha check disabled: killed (decisive). X2 READY-2 exact-line `!=` -> `startswith`: SURVIVED (decisive path,
code correct by stub R3; D3). X3 vault `descriptive_only` -> False: killed (decisive). Sandbox restored (porcelain 0, blob 306066ea).

## Operator command (Git Bash, benchzoom master)

```
cd Z:/FAC/TUBerlin/benchzoom
# pre-checks: each must print the value in the comment; any other value = do not run
git rev-parse HEAD HEAD:src/benchzoom; git hash-object examples/mmlupro_more.py; git status --porcelain | wc -l
#   233b2f376f859caee2edcfff98207dfbf54564ec / c9809e9898198093a61755b47ec1c1b7c2e72026 / 306066ea8e6953fe3ad12320da616fefd505de7a / 0
git -C Z:/FAC/TUBerlin/THESIS/TaxoArena diff --quiet HEAD -- docs/judge_v2_program.md docs/reviews/READY1_BZ-MMLUPRO-MOREMODELS.md docs/reviews/READY2_BZ-MMLUPRO-MOREMODELS.md && echo TA_CLEAN
test ! -e E:/benchzoom_demo/mmlu_pro_more/vault_read && test ! -e E:/benchzoom_demo/mmlu_pro_more/vault_run.log && echo ABSENT
(cd E:/benchzoom_cache/hf && sha256sum -c E:/benchzoom_demo/mmlu_pro_more/census/parts_SHA256SUMS | grep -c ': OK$')   # 343
.venv/Scripts/python -I -c "import sys; sys.path.insert(0,'Z:/FAC/TUBerlin/benchzoom/examples'); import mmlupro_more as C; R='Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/reviews/'; print(C.T.sha256_text(C.section_text(C.TAXOARENA/C.PROGRAMME))==C.SECTION_SHA, C.ready1_gate(R+'READY1_BZ-MMLUPRO-MOREMODELS.md'), C.ready2_refusal(R+'READY2_BZ-MMLUPRO-MOREMODELS.md'), C.synthetic_refusal(C.OUT, C.runner_blob()))"
#   True None None None
# the read (once)
{ echo "CMD: python examples/mmlupro_more.py vault (threads 8; blob $(git hash-object examples/mmlupro_more.py); head $(git rev-parse HEAD); src $(git rev-parse HEAD:src/benchzoom); start $(date -u +%Y-%m-%dT%H:%M:%SZ))"; OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 .venv/Scripts/python examples/mmlupro_more.py vault --registration Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/reviews/READY1_BZ-MMLUPRO-MOREMODELS.md --ready2 Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/reviews/READY2_BZ-MMLUPRO-MOREMODELS.md; echo "EXIT $? end $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } 2>&1 | tee E:/benchzoom_demo/mmlu_pro_more/vault_run.log
```

## Commands (read-only on every object of record; scripts in E:/TaxoArena_tmp/ready2_more_review)

```
git -C benchzoom diff dfeb0aa 233b2f3; rev-parse {9f6182f,dfeb0aa,233b2f3}:{src/benchzoom,src/benchzoom/irt.py,examples/mmlupro_more.py}
git -C benchzoom diff --name-only 9f6182f 233b2f3 -- <CLEAN_CODE paths>              # 2: irt.py, sources.py
python -I sec.py f53ec853 efd48179 1aa43079 HEAD WT; diff sec_f53ec853.txt sec_1aa43079.txt | grep -c '^<'   # 0 (14 '>')
git diff --numstat f53ec853 HEAD -- docs/judge_v2_program.md                                                  # 49 0
cat -A work_run.log (50 lines, whole); sha256sum work_run.log support_recut.json weak_half.json dress/outcome.json
python -I -c "<support_recut.json: vault SE, MDE80, n/DEFF, median>"                                         # row 5
rv_tau.py full  (8 threads; log rv_full_t8.log)  /  rv_tau.py recut 1 (log rv_recut1_t8.log)                   # rows 4, 5, 10, 11
sha256sum -c calibration_synthetic_306066ea8e69/SHA256SUMS | grep -c ': OK$'   # 13; per-file sha vs calibration_synthetic_fc8f5adca587
python -I -c "C.synthetic_refusal(OUT, C.runner_blob()); C.ready1_gate(R1); section sha; A.records_ok()"     # None, None, True, ok
stubs.py  (32 cases)  ;  mutants X1-X3 via one-string replace in bz/examples/mmlupro_more.py + pytest -x
(cd E:/benchzoom_cache/hf && sha256sum -c .../census/parts_SHA256SUMS)  # 343 OK, 0 not OK; find oll_parts_more -newer census.json | wc -l  # 0
pytest -q tests/test_{mmlupro_more,execution_graph_sync,irt_slope_damped}.py   # 107 passed; mmlupro_more.py --selftest OK
sha256sum -c E:/TaxoArena_backup_2026-10-22_mmlupro_gate2/SHA256SUMS (22 OK); find E:/benchzoom_demo/mmlu_pro_more -type f | xargs sha256sum (57, before = after)
```
