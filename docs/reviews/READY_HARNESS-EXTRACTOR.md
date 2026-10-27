# READY review: HARNESS-EXTRACTOR (amended; MATH + IFEval scorer gap; HF post 3)

Reviewed: `tools/analysis/harness_extractor.py` at 703b198b (branch worktree-wf_d795fd62-e28-8, a fast-forward of main 9af2c14a; 1 file changed),
blob:947edb12cb05b5e9f08b480401db65baeee0092c, sha256-lf16:07e5f9917f4a7817 (the working tree is LF, 0 CR bytes, so there is no separate CRLF rendering on disk;
the script prints sha256-crlf16:fad97127b07a1791). Registration L25229-L25315 (as of 16ff6d0d); D-5 brackets L25317-L25327 (authority:
docs/agents/author_decisions/2026-10-08.md, 5211616a). This is a first review (a new file), not a delta. Zero calls. Pool reads happened only in windows where busy.ps1 exited 1.

## Verdict

**NOT READY / BLOCKED** on one item, B-1: the in-script rule-7 check can never pass, so the real `--dry-run` and `--run` always refuse.
Apart from B-1, the instrument is sound. With an exclude-self busy check substituted (review-only; see below), the real dry-run passed read-only and
every deciding pre-run count reproduces to the digit. After the B-1 fix and a delta READY, `--run` also needs C-1 and C-2.

## Per-claim table (deciding claims)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | Scorer of record: X0 = official `eval_results.is_correct`, no overlay (D-5) | CONFIRMED | L553 selects `e.is_correct` from `eval_results`; `sqlite_master` type = 'table' (not a view); the header line at dry-run L8 is verbatim to deviation (1) | - |
| 2 | H is read from the pinned table, sha-checked, recomputed per row | CONFIRMED | H_SHA = 6b010fa6...d1d1 = `sha256sum` of the table on disk; load_h refuses on CR, sha, header, count (23,832); per-row `h_score` vs the table and route vs X0 refuse (X36-X38, X40 killed); the math_scorer_h pin blob:3ab51e3f = HEAD 9af2c14a | - |
| 3 | Nothing else changed: 1 file, helper pins match main | CONFIRMED | `git diff --name-only 9af2c14a 703b198b \| wc -l` = 1; the 5 MY_PINS = `git rev-parse HEAD:<f>` and the LF blob of the working copy, all 5 equal | - |
| 4 | Selftest 8/8 | CONFIRMED | 8 / 8 passed (24 s) | - |
| 5 | Mutants 73/73, control survives | CONFIRMED | 73 of 73 KILLED; control SURVIVED; 0 not applied | - |
| 6 | R1 twins 471 / 427 | CONFIRMED | independent script: 471 / 427 (GPQA 288, MMLU_PRO 179, BBH 2, MATH 2); the dry-run prints the same | - |
| 7 | Denominators: MATH kept 1,309 of 1,324, IFEval 541 of 541; 18 models, 1,324 MATH rows each; Llama-3-70B 0 rows | CONFIRMED | independent: 1309 / 1324, 541 / 541, rows/model {1324}, 18 models, 0 excluded rows | - |
| 8 | Rule-7 gate: "the script runs busy.ps1 itself and refuses on exit 0" | **REFUTED (vacuous)** | busy.ps1 matches the CALLER's own command line (`harness_extractor` is in its regex); probe: own pid 48216 → matched [48216] "SELF MATCHED"; control argv → []. Real `--dry-run` → "REFUSED: rule 7 ... exited 0". The selftest only exercises stub busy scripts | **BLOCKER** |
| 9 | Dry-run is read-only | CONFIRMED | stat (size, mtime) of multicorpus_cache_v1.db*, checker_answers_v2.db, embeddings_cache.db* plus sha256 of checker DB and H table: before = after; the script's own DB sha256 before = after (ad66e30a...); no output dir created | - |
| 10 | Support arithmetic (registered) | CONFIRMED | 0.0275·√(590/1324) = 0.01836; 0.0251·√(1.2·590/1324) = 0.01836; HX3 0.0275·√(590/541) = 0.02872; HX4 √(0.099/1324)·√1.2 = 0.00947; HX5 √(0.09/1727) = 0.00722; MDE80 0.051/0.080/0.027/0.020. At the real n = 1,309: SE 0.0185, MDE 0.052 (unchanged). DEFF source: G13 1.214, transported; the real Kish is 1.0000 (1,309 components on 1,309 questions), so the transported 1.2 is conservative | - |
| 11 | HX-R4 registration defect (mid-rank shift 2.5) | CONFIRMED | HX1 holds iff shift ≤ 2, while rule 8 refutes MOVE iff shift < 3. Mid-ranks give multiples of 0.5, so 2.5 reads MOVE and refuted at once. The script prints both lines and keeps the HX1 word (pure + edge fixture) | MEDIUM (C-2) |
| 12 | HX-R1: IS / IL = the harness's own per-sample verdicts | PARTLY | one sample file per model (count 18 of 18 dirs = 1); joined and checked row by row. But I0 was ingested from the same field, so the I0-IS pair is identical by construction and HX3's 3-scorer set reduces to IS vs IL. Descriptive-only | MEDIUM (C-2) |
| 13 | H table pin recorded by the registrar (deviation (2)) | NOT YET | `grep -c 6b010fa6 docs/judge_v2_program.md` = 0 | condition C-1 |

Own mutants (deciding paths; via `run_mutants` with my own table; control survived):
O1 duplicates not collapsed: killed. O2 Llama-3-70B kept in --run: killed. O3 HX4 interval from the i.i.d. replicates: killed, decisive.
O4 S_w from the i.i.d. replicates: killed. O5 weighted accuracy divided by n, not by sum(w): killed, decisive for every interval. O6 dry-run skips busy: killed.
O7 run skips busy: killed. O8 IFEval joined on question_id, not upstream_id: killed. 8 of 8.

## Defects and fixes

- **B-1 (BLOCKER): the busy check matches its own process.** `busy_check` runs the shared `E:/TaxoArena_tmp/busy.ps1`, which lists every python.exe
  whose command line matches a regex that includes `harness_extractor`, and that includes the calling script. Exit 0 is therefore certain at every
  real launch, and the gate refuses forever. The same pattern sits in saturation_irt.py L924-L932, and a peer `saturation_irt.py --dry-run` was observed
  respawning (PIDs 36252, 91080) while this review ran. FIX: give busy.ps1 a backward-compatible `param([int[]]$ExcludePid=@())` and the filter
  `Where-Object { $_.ProcessId -notin $ExcludePid }`. `busy_check` passes `-ExcludePid <os.getpid()>,<os.getppid()>`. Add a selftest case that runs the
  REAL busy.ps1 from a child whose argv contains `harness_extractor` and asserts that its own PID is not matched. Do NOT work around B-1 by launching
  under another name: that hides the reader from every peer's rule-7 check. busy.ps1 is shared, so its change belongs to the operator or orchestrator,
  with every in-script caller re-checked.
- **C-1 (condition for --run):** the registrar records the H table pin sha256-lf 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1
  (deviation (2), L25321) before --run.
- **C-2 (condition for --run; pre-data registrar rulings):** HX-R4 (suggested: rule 8 refutes RANKS-MOVE iff every tau-b ≥ 0.85 and max shift ≤ 2,
  the exact complement of HX1); HX-R1 (accept the harness's per-sample verdicts as "the official checks", and state that I0 ≡ IS by ingestion, so
  HX3 = IS vs IL); HX-R2 (add checker_answers_v2.db, read-only, `non_terminated` only, to DATA OBJECTS).
- LOW L-1: the dry-run's closing line says "no scorer column was selected". Yet `raw_ifeval` parses the IFEval strict and loose verdict fields into
  memory during the dry-run (they are not printed). Reword the line, or defer the parse to --run.
- LOW L-2: on real data, components = questions (Kish 1.0000), so the "component" bootstrap equals a question bootstrap. The run prints it. No change needed.

## Run commands (after the B-1 fix and its delta READY, then C-1 and C-2 recorded)

```
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants
powershell -NoProfile -ExecutionPolicy Bypass -File E:/TaxoArena_tmp/busy.ps1   # must exit 1
python tools/analysis/harness_extractor.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/harness_extractor.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up the outcome + figure json to E:/TaxoArena_backup_20261009_harness_extractor with SHA256SUMS.txt; never commit
```

## Commands / scripts (scratch on E:/TaxoArena_tmp/hxrev; nothing committed except this file)

```
git show 703b198b:tools/analysis/harness_extractor.py | git hash-object --stdin          # 947edb12
git diff --name-only 9af2c14a 703b198b | wc -l                                          # 1
for f in pool_guard split_side v2_reader_guards math_fix math_scorer_h: git rev-parse HEAD:tools/analysis/$f.py vs LF blob of the working copy
sha256sum experiment_results/math_scorer_h/math_h_table.csv                             # 6b010fa6...d1d1
grep -c 6b010fa6 docs/judge_v2_program.md                                               # 0
(worktree) scratch_dir.py --run -- harness_extractor.py --selftest | --mutants           # 8/8; 73/73 (log sha256-16 0cc565bbdadb2b94)
hxrev/own_mut.py (8 mutants via hx.run_mutants)                                          # 8/8 killed (log cedf218107f7d266)
hxrev/probe_self.py tools/analysis/harness_extractor.py --dry-run                        # SELF MATCHED (B-1)
real --dry-run with the shipped busy.ps1                                                 # REFUSED rule 7 exit 0
hxrev/harness_extractor_review_dry.py: hx.main(["--dry-run"], cfg=real_cfg() with busy=hxrev/busy_exclself.ps1, which excludes the parent and grandparent PID)
  run only after the shipped busy.ps1 exited 1; rc 0; 40 lines (log sha256-16 0ee1d182115a6043); stat+sha before = after
hxrev/indep_r1.py (mode=ro&immutable=1; pool_guard.judgeable)                            # 471/427; MATH 1309/1324; IFEVAL 541/541; 18 x 1324; table
```
