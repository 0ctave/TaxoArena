# READY review: W1 hygiene branches (JOIN-CARDINALITY-GUARD, RUBRIC512-ROUTING-DECIMAL-COMMA, MULTISWE-CORRECTIONS)

Adversarial reviewer, 2026-10-04. Zero judge calls. Main at review time 150b2f7c; all three branches fork at feac5b3d
and `git merge-tree --write-tree main <tip>` is clean for each. Temp under E:/TaxoArena_tmp/review_w1 (sandbox copies
for the Python mutants); no file of any worktree left modified (`git status --short | wc -l` = 0 in each after the run).

## Verdicts

| branch / tip | verdict | conditions |
|---|---|---|
| w1-join-cardinality-guard bd59a937 | **READY / MERGEABLE** | none blocking; L1 (registration null: the coder's reading stands until the registrar confirms) |
| w1-rubric512-decimal-comma bfb316f7 | **READY / MERGEABLE** (orchestrator's decision: keep leaf_routing.py, rubric_512.py NOT re-pinned) | L2 selftest gap (6-field quoted-comma branch untested); new code imports leaf_routing, never rubric_512.primary_routing |
| w1-multiswe-corrections 3a43fb62 | **READY / MERGEABLE as a tool** (--dry-run / --selftest only) | M1 + M2 fixed (selftest fixture) BEFORE any --analyze; --analyze also needs its registration + a READY on it |

## Per-claim table (deciding claims only)

| # | claim | my number | status | sev |
|---|---|---|---|---|
| J-a | link table of record has 0 fan-out (12,257 rows, 757 null, 11,500 distinct of 11,500 non-null) | mmlu_pro_dataset_cache_v2.db 12,257 / 757 / 11,500 / 11,500; also 20NG 16,921/16,921, ag_news 2,000/2,000, multicorpus 0 rows; intent / judgebench have no link table | CONFIRMED (guard fires on no recorded load) | - |
| J-b | inert: golden ids 10,000,002 / 10,000,005 / 10,000,900 unchanged through fetchDataset | JoinCardinalityGuardTest 3/3 pass (XML tests=3 failures=0); golden = LiveCodeBenchDatasetTypeTest L196/L217 | CONFIRMED | - |
| J-c | the new code executed (discriminator) | test asserts checks +1 and rowsChecked +3; `grep -c assertAtMostOnePerLocalRow MMLUDatasetFetcher.class` = 1; mutant J2 (guard moved under `if (unlinked>0)`) killed by test 1 | CONFIRMED | - |
| J-d | null-test change (`upstreamNull` vs old `rs.wasNull()` after getInt("id")) moves no id | J3 (drop `upstreamNull ||`) SURVIVES = equivalent mutant: NULL question_id still reaches the sentinel via getInt 0 <= 0 | CONFIRMED (inert by equivalence) | - |
| J-e | full suite 556 tests, the 2 known failures | `.\gradlew.bat test --offline --no-build-cache`: 556 completed, 2 failed = MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest "no model has a wholly blank trace column"; 0 other | CONFIRMED | - |
| J-f | 6/6 mutants killed; fail-closed | re-ran K2 (rethrow removed, fail open into the generic catch): killed (1 test); own J1 (key by upstream) killed (3 lines) | CONFIRMED on the decisive one | - |
| R-a | bareq512_s42: 3,862 rows all 7-field, 3,445 qids, 410 multi-row, file-first == max on 410/410, routing identical to legacy, sha16 86ea6b1b6d2178ee | --check: identical to the digit; my own parser (rsplit from the right, Decimal(whole.frac)): 3,862 / 3,445 / 410 / 410, sha16 86ea6b1b6d2178ee, 827 negative weights, 0 ties | CONFIRMED | - |
| R-b | abt2d512_s42 3,802 / 3,445 / 349 / 349 sha16 35a0828fcda9249a; WRONGSPLIT 3,819 / 3,433 / 379 / 379 sha16 d1fd5a479654eb98 | same from --check and my parser (0 ties; 706 / 765 negative weights) | CONFIRMED | - |
| R-c | an unsorted file is routed by weight, legacy by file order | selftest OK; builder mutants M3 (numeric join, sign lost), M8, M9 re-run: killed; own R2 (route = file-first) killed, R3 (first_eq on last row) killed | CONFIRMED | - |
| R-d | rubric_512.py unedited (pin 81ae1d39 intact) | `git hash-object tools/analysis/rubric_512.py` in the worktree = 81ae1d3914b0...; branch diff touches 1 file (`git diff --name-only feac5b3d bfb316f7 | wc -l` = 1) | CONFIRMED | - |
| S-a | real-data --dry-run reproduces review 5ba264c | own run: gate 25,709/25,709 PASSED; 96 zips sha-verified; v1/v1 14,095/0/11,614, D_c 12,113/25,709 = 0.4712 [0.4651, 0.4773]; v2/v1 D_c 12,792 = 0.4976 [0.4915, 0.5037]; aliased 1,486, unjoined 0; django 1,097/2,772 = 0.396, sympy 0.378, astropy 0.606, python 2,506/6,000 = 0.418 (review 0.4177); python EVAL 922/2,808 = 0.3283 -> 1,249/2,808 = 0.4448; v1/v2 14,095/7,132/4,482/0; v2/v2 15,343/7,297/3,069; CAP both-signals 7,297, length-only 0, text-only 0 | CONFIRMED to the digit against 5ba264c rows 7/8 and defects 1/2 | - |
| S-b | DB of record unchanged | sha256 3ce5179c3f5085d2... and mtime 1790073596 / size 27,705,344 identical before/after (`cmp` of the two stamp files equal); no -wal/-journal | CONFIRMED | - |
| S-c | 20/20 mutants killed | re-ran X1 (alias replace-all), X3 (cap length 50), X10 (gate off): killed. Own: Y3 (unjoined from v1 map) killed; **Y1, Y2, Y4 SURVIVED** (below) | PARTLY | MEDIUM |
| S-d | ingest imported unedited (pin f8095345 / blob 9ee94114) | `git rev-parse 3a43fb62:tools/ingest/multiswe_ingest.py` = 9ee94114... = main's | CONFIRMED | - |

## Own mutants (one line each)

- J1 guard keyed by upstream id instead of local id: killed (3 tests). Decisive.
- J2 guard call moved inside `if (unlinked > 0)`: killed (tests 1, 2). Decisive.
- J3 `upstreamNull ||` removed from the sentinel test: SURVIVED. Equivalent mutant; it is the inertness evidence for J-d, not a gap.
- R1 6-field branch reads `float(r[4])` without `","->"."`: SURVIVED. Not decisive (every recorded file is 7-field). -> L2.
- R2 `_route` keeps the file-first row (no weight comparison): killed. Decisive.
- R3 `first_eq` compares the LAST row of each qid: killed. Decisive (the count check).
- Y1 faithfulness gate compares mswe_term_v1 only, drops the exit_status half: SURVIVED. -> M1.
- Y2 cap length `== 51` -> `>= 51`: SURVIVED. Not decisive (no trajectory above 51 entries on the corpus, 5ba264c row 5; CAP length-only 0). LOW, no action.
- Y3 unjoined-members count read from the v1 map: killed.
- Y4 python EVAL cell `side == "EVAL"` -> `side != "TRAIN"` (admits GATE): SURVIVED. The DB carries GATE (tasks: EVAL 390 / GATE 98 / TRAIN 1,644), the fixture has no GATE task. -> M2.

## Defects and fixes

- **M1 (MEDIUM, multiswe; before --analyze).** The faithfulness gate's exit_status comparison is untested (Y1 survives): a re-reader that parsed the
  status wrong but mapped to the same class would pass the selftest. Fix: add a selftest tamper that changes a stored `exit_status`
  to another string of the SAME mswe_term_v1 class and assert the gate refuses.
- **M2 (MEDIUM, multiswe; before --analyze).** The EVAL cell's exclusion of GATE is untested (Y4 survives) although GATE exists in the
  DB of record. Fix: add one python GATE task (with a TERMINATED decided episode) to `_fixture` and keep the asserted EVAL-cell
  values unchanged, so a GATE-admitting cell changes them. Both fixes are one commit on the branch, then a delta review (3 mutants).
- **L1 (LOW, join).** Registration null; the reading "a LEFT JOIN onto eval_question_link must not emit one local row twice" is the
  coder's and the orchestrator's. Registrar confirms by record. Note also (pre-existing, not this branch): loadFromDb joins EVERY
  table onto eval_question_link by numeric local id; the guard does not address cross-table id meaning, only fan-out.
- **L2 (LOW, leaf_routing).** The 6-field branch's comma replacement (quoted `"0,5"` weight) is untested (R1 survives). Fix: add a
  quoted-comma 6-field row to selftest case (4). Not a merge condition (no recorded file has a 6-field row).
- **L3 (LOW, all).** Pins below are LF; MMLUDatasetFetcher.kt's working tree in the worktree is CRLF (sha256-crlf16 5ef720decb07130c).

## Pins (LF of record; `git rev-parse <tip>:<path>`, sha256 of the LF blob)

- JoinCardinalityGuard.kt blob:98d87db1326065cc53e9b093546e9874ae2b2739 sha256-lf16:47eaa504f88c8653
- MMLUDatasetFetcher.kt blob:4d5a0691895f2d8bc345578988296b6a6a477d48 sha256-lf16:210cea7e6ea19836 (sha256-crlf16:5ef720decb07130c)
- JoinCardinalityGuardTest.kt blob:cd5da80b6ce498c1a51eb9b3c4e5f3ad827a068c sha256-lf16:08d91680b2c31e04
- leaf_routing.py blob:c4746a61f923305d8bd0d712d1298ee0f4c08482 sha256-lf16:c089e6c2b0127358
- multiswe_corrections.py blob:e5ca9ecb84b46287cd415ad3c9f196f0e010bf70 sha256-lf16:ca23f7fa38a7bcae (= the script_sha the dry-run printed)

## Merge instructions

Merge each tip into main separately (`git merge --no-ff <branch>`; merge-tree clean on all three; no application.yml / .env /
.gitignore in any diff: 3 / 1 / 1 files by `git diff --name-only feac5b3d <tip> | wc -l`). Order irrelevant (disjoint files).
After the join merge, `.\gradlew.bat test --offline` on main must show 556 + main's own delta with only the 2 known failures.
multiswe: --analyze stays forbidden until M1/M2 are fixed, a registration exists and a READY names it.

## Commands (compact)

```
python - (sqlite3 mode=ro&immutable=1): count(*), count(mmlu_pro_row_id), count(distinct mmlu_pro_row_id) FROM eval_question_link, per corpus DB
cd .claude/worktrees/w1-join-cardinality-guard; ./gradlew.bat test --offline --no-build-cache   # 556 completed, 2 failed
grep ' FAILED$' gradle_join.txt; build/test-results/test/TEST-taxonomy.dataset.JoinCardinalityGuardTest.xml   # tests=3 failures=0
grep -c assertAtMostOnePerLocalRow build/classes/kotlin/main/taxonomy/dataset/MMLUDatasetFetcher.class        # 1
mutants J1-J3, K2: edit -> ./gradlew.bat test --offline --tests taxonomy.dataset.JoinCardinalityGuardTest -> git checkout -- <file>; ./gradlew.bat --stop
python tools/analysis/leaf_routing.py --check <3 promoted csvs>; --selftest; own parser (rsplit(',',3), Decimal) -> rows/qids/multi/first==max/sha16
mutants R1-R3, M3/M8/M9: sandbox copy E:/TaxoArena_tmp/review_w1/lr, leaf_routing.py --selftest; restored file cmp-equal to the worktree's
sha256sum + stat of multiswe_result_2026-09-22.db before/after; scratch_dir.py --run -- python tools/analysis/multiswe_corrections.py --dry-run --db <main db> --raw-dir <main raw>
mutants X1/X3/X10, Y1-Y4: sandbox copy E:/TaxoArena_tmp/review_w1/ms, multiswe_corrections.py --selftest; restored file cmp-equal
git merge-tree --write-tree main <tip>   # clean x3
```
