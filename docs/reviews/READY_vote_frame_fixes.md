# READY delta review: vote_frame_cert fixes VFC-DC-PRIME and VFC-NAME-PROFILE-BY-CONTENT at 97d830c (adversarial reviewer, 2026-09-24, zero calls, read-only)

## VERDICT

**READY-WITH-CONDITIONS (C1-C5). MERGEABLE by pathspec.**

- VFC-NAME-PROFILE-BY-CONTENT (abf4db5 D1 / D6): **CONFIRMED.** The fix does what it claims, and it is witnessed by execution on the real data.
- VFC-DC-PRIME (ae88d3a D-C'): **PARTLY.**
  - The 15 listed vectors are closed: 0 of 15 false certificates, where 10 of 15 were false before.
  - The class is NOT closed. 7 new vectors of mine give 7 false certificates (D1). Two of them sit inside the fix's own scope (f), the transitive local-import scan (D2).
  - So the commit subject "D-C' closed" overstates. V-C5 stays in force.
- **Outputs of record: none is rewritten by the merge, but the instrument's output of record WOULD CHANGE if re-derived.** In `experiment_results/vote_frame_cert.txt` (c731836, LF) these lines move: L1, L154-L157, L345, L350, L389, L400, L403-L404. Details in section 2.
  - Every criterion and prediction verdict stays as recorded (E1-E4 HELD; P1-P5 HELD).
  - P4's printed count goes from 2 to 1.
  - The classes go from 54/4/0/0/2/2 to 54/5/0/0/1/2.
  - The registrar must record this by insertion (C3).
- **POSITION-INDEX-ALL and TIE-MECHANICS outcomes are byte-identical** when re-derived with the new build as the imported module. The index run carries an execution witness: the content branch ran 4 times.

Pins (the LF rendering is of record; the worktree renders CRLF):

| file | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/vote_frame_cert.py @97d830c | blob:aab89f37eb3ee7c50a8ff888c05d1409f64522a2 | sha256-lf16:a985eff263414fd9 | sha256-crlf16:e42ab00a95d931be (worktree `git hash-object` = aab89f37; the worktree has 2,260 CR bytes) |
| the same file at base eba09f3 = main HEAD 48de7b4 | blob:8e1fbf6a7d557c2a82f5769ecea89c1d03f10705 | sha256-lf16:72ceddfe919a982e | sha256-crlf16:9d86e3fba063ef5d |
| position_index_all.py, tie_mechanics.py | unchanged: blob:9c2ae419... and blob:7f88d2ac... at 1722df7, eba09f3, 97d830c and main | | |

## 1. Per-claim table

| # | claim (commit 97d830c) | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | one file touched; the docstring edit is insertion-only; no registered sentence edited | CONFIRMED | `git diff --name-only eba09f3 97d830c \| wc -l` = 1; `git diff -U0 ... \| grep '^-' \| grep -vc '^---'` = 11 | All 11 deleted lines are code: the two `name_resolver_long` signatures and call sites, `unit_votes` sig/call, H3_T/H3_TS, two fixture tuples, one D-C check string that was made MORE specific. 0 docstring lines deleted. Added lines grep for 0.80 / 25-60 / score_* / DEFF / MDE / P1-5 / E1-4: 0 | - |
| 2 | selftest passes (python and -O) | CONFIRMED | `python [-O] guard.py vote_frame_cert.py --selftest` on an LF `git archive` of 97d830c (audit hook: every sqlite connect under temp) | 325 checks, 0 failed, in both modes; 604 connects, all under temp. Base eba09f3: 240/0. Old check lines absent from the new run: 2, and both are the same checks with larger fixture counts (72 -> 99 fixtures; E-COMB not-verified 28 -> 51). No check was dropped | - |
| 3 | importers' selftests unchanged | CONFIRMED | position_index_all / tie_mechanics `--selftest` in both trees, python and -O | 52/0 and 29/0 in all 8 runs. Outputs byte-identical old vs new, except the index's INFO line "the imported vote_frame_cert.py ... a985eff263414fd9 (DIFFERENT; a mismatch refuses every real run)" (D5) | - |
| 4 | the listed tamper_adv vectors: 0 of 15 false certificates (was 10) | CONFIRMED | rr3 `tamper_adv.py` vectors (extended as `tamper_adv2.py`) against both builds | new build: t0 correct; t1 (reload, inert) a conservative false FAIL (R2); t2-t10 and t14 UNCERTIFIABLE R2; t11 / t13 MIXED; t12 R3. **0 of 15 false.** Base: 10 of 15 false (reproduces ae88d3a) | - |
| 5 | callsite_adv / rj_history / h3_adv unchanged | CONFIRMED | rr3 scripts under guard.py on the new build | callsite_adv 1 of 11 false = x2 (the ruled stated limit); rj_history 0 of 2 (both UNCERTIFIABLE R2); h3_adv 0 of 9 false passes (C6 a conservative false fail) | - |
| 6 | "D-C' closed" (subject line) | **REFUTED as worded / PARTLY** | 7 new reviewer vectors u1-u7 (`tamper_adv2.py`) | **7 of 7 FALSE-CERT on the new build** (and on the base): u1 `pkgutil.resolve_name('rejudge_grok').combine_orders = ...` via a Name; u2 `inspect.currentframe().f_globals` held in a Name, then `_g['rj'] = _R()`; u3 a `gc.get_objects()` module walk, then `_m.combine_orders = ...`; u4 `import rj_patcher_untracked` (a local module on disk, never committed); u5 `from tools.analysis import rj_patcher` (a committed patcher reached through a package path); u6 `types.FunctionType(compile('...r.combine_orders = _n...'), {})()`; u7 `operator.setitem(inspect.currentframe().f_globals, 'rj', _R())` | MEDIUM (D1, D2) |
| 7 | the three real writers unchanged: ladder f03cb302 and swap 3ebf4f4a PASS + PASS; contrast R2 on pin timing | CONFIRMED | full re-derivation (section 2) | V-C2'' counts on the new build: COMBINER CHECK 3, CALL-SITE PASS 2, not reached 1, "is NOT AST-identical to the recipe" 0, "AST-equivalent" 0, "rebinds or patches rejudge_grok" 0, PIN TIMING 1, and the P4 reason line "(2) E-COMB, combiner not verified 1 [of which pin timing 1" present. Identical to the record. Transitive scan at the pin: ladder -> rejudge_grok.py@fb8fb5bd2f1a, rubric_value_contrast.py@70370357d100; swap -> the same plus bias_audit.py@d76b1db5880f. That equals rr3's independent writer_tamper_scan.py | - |
| 8 | the _backup copy of newcomer_placement_steps.db reads CERTIFIED-CONTESTANT 387/387, 380/380 (was RX) | CONFIRMED | full re-derivation, JSON unit compare | order-1 387/387; order-2 informative 380: contestant 380, positional 0; unresolvable 767 -> 0; label_space positions -> names. **The copy's unit equals the original's in every field (0 differing keys).** This matches abf4db5's independent recompute (fwd 387/387, rev 380/380) | - |
| 9 | NAME_PROFILE_CONTENT = the four certified originals' full sha256 | CONFIRMED | `sha256sum` of the files (read as bytes, no DB opened) | 4 of 4 equal: arena13 594742e0..., placebo 8c0ac804..., newcomer_placement 755a1f4f..., newcomer_placement_steps 292fdf09... The _backup copy is 292fdf09... too. Each 16-char prefix equals the certificate's sha256_16. On the real run, all 5 name-labelled LONG units report `name_profile` "content sha256 ..." (execution witness); the 10 other LONG units report None | - |
| 10 | the selftest EXECUTES RX on an unmapped name-labelled table (D6) | CONFIRMED | `[PASS] D6: ... reaches RX` in the selftest log; mutant rx_to_ambiguous KILLED | as claimed | - |
| 11 | "RX is unchanged in code (the registrar rules on it)" | CONFIRMED (code); **the ruling is still OPEN** | `grep -n '\bRX\b' docs/judge_v2_program.md`: last mention L14626-L14630, no ruling | The queue item VFC-NAME-PROFILE-BY-CONTENT names "blocker: a registrar ruling on RX, then engine-coder". The code was built before that ruling. This is harmless to the code, because RX's semantics are untouched, but the reuse condition stands (C2) | LOW (process) |
| 12 | merge safety | CONFIRMED | `git rev-list --count eba09f3..97d830c` = 1; `git rev-list --count eba09f3..main -- <3 files>` = 0; main blob of vote_frame_cert.py = 8e1fbf6a = base; main working tree `git status --short` on the file: 0 lines | A pathspec checkout of the one file clobbers nothing: main has not touched the file since the base (50 commits ahead, none on these three paths) | - |

### Reviewer mutants (`mutate_vff.py`; each mutation is an exact replacement with its count asserted, followed by the selftest on a copy)

**34 applied: 32 KILLED, 2 SURVIVED.**

- **Killed.** Mutants that re-introduce D1 (content lookup off; basename first; certify ignores the content ctx; unit_votes ignores the content map) and every D-C' route. The D-C' routes:
  - the prime scan not called; the transitive scan not called;
  - the transitive pin at the writer's commit time instead of the first write;
  - vars or globals dropped from DYN_ANY;
  - store-through-call off; store-through-rj off; alias-as-value off;
  - dunder off; `__builtins__` whitelisted;
  - referenced-not-called off; attribute-named off; sys.modules off; importlib off; `from sys import modules` off; star import off;
  - def / param / except / match rebinding off; import-twice off;
  - rj_self_bindings off; relative import passes; unpinnable local passes; no recursion;
  - the dependency scan with only D-C, or with only D-C';
  - RX renamed.
- **Survived.**
  - `dep_unparseable_passes`: no fixture has a pinned local module that fails to parse (D3).
  - `wrong_content_sha`: the selftest checks the shape of NAME_PROFILE_CONTENT, not its values. The values were verified directly (claim 9) and by the real-run witness.

## 2. Recorded outputs: re-derived, read-only

**Method.** `rerun_vfc.py` imports each build from an LF `git archive` (base eba09f3, fix 97d830c) and calls `run()` with the outputs redirected to the scratchpad. The scan is restricted to the 62 recorded paths, so the in-flight `trace_truncation.db` is never opened. Settings: `comb_ctx=dict(repo=<main>)` and `selftest_ok=True`.

**Safeguards.**
- An audit hook refuses any non-`mode=ro&immutable=1` connect and any write-open inside the repo.
- Preconditions, for 62 of 62 caches: no non-empty -wal or -journal, and size, mtime_ns and sha256_16 equal to the record.
- After all runs, 62 of 62 caches are still identical (sha256_16, size, mtime_ns), and the eval DB mtime is unchanged.

**Harness validation.** The base build reproduces the recorded .txt with only 3 line differences, all caused by the harness:
- L1 prints the CRLF sha of an LF export;
- L4 prints 62 files scanned instead of 184;
- L388 prints "0 other scanned".

The recorded JSON reproduces except `written` and the CRLF sha.

**VOTE-FRAME-CERT: lines of `experiment_results/vote_frame_cert.txt` (c731836, LF numbering) that MOVE under the fix build.** 20 changed diff lines against the base re-run:

| record line | record | fix build |
|---|---|---|
| L1 | script LF 72ceddfe919a982e | a985eff263414fd9 |
| L154-L157 | `_backup/newcomer_placement_steps_2026-09-19_complete.db -> UNCERTIFIABLE`; order-1 0/0, order-2 0, unresolvable 767; note "767 stored labels are neither positions nor resolvable names (no name profile for this writer)" | `-> CERTIFIED-CONTESTANT`; order-1 387/387, order-2 informative 380: positional 0, contestant 380, unresolvable 0; contestant-labelled ['winner (arm=rev)']; names: schedule.newcomer / schedule.opponent (3 lines) |
| L345, L350 | H3 COMBINER CHECK PASS (ladder, swap) | same verdict; the evidence list gains "local imports scanned transitively at the run-time pin ... (D-C' (f)): ..." |
| L389 | SUMMARY: POSITIONAL 54, CONTESTANT 4, MIXED 0, AMBIGUOUS 0, UNCERTIFIABLE 2, NOT-DUAL-ORDER 2 | CONTESTANT 5, UNCERTIFIABLE 1 |
| L400 | P4 HELD: 2 UNCERTIFIABLE among the 60 | P4 HELD: 1 UNCERTIFIABLE among the 60 |
| L403-L404 | "P4 reason OUTSIDE the five: OTHER (stored labels unresolvable) ... 1"; "P4 is carried by: ['E-COMB, combiner not verified', 'OTHER ...']" | the outside-five line is gone; "P4 is carried by: ['E-COMB, combiner not verified']" |

**VOTE-FRAME-CERT: lines that do NOT move.**
- E1-E4 HELD;
- P1 60, P2 54/60, P3 0, P4 HELD (the count is now 1 >= 1, carried by rubric_contrast's pin-timing exclusion alone, so D3 of abf4db5 stands unchanged), P5;
- every other cache's class and counts.

**VOTE-FRAME-CERT: JSON changes.**
- caches[4] (the copy): class and unit fields as above; `uncert_reason` 'RX' removed.
- 15 LONG units gain the key `name_profile` (5 by content, 10 None).
- The 2 E-COMB evidence lists change.
- The script shas change.

**The fix therefore changes the instrument's output of record in content, not only in text**: 1 class, P4's printed count, and the SUMMARY. The outcome file is write-once and is NOT rewritten. The change must be disclosed by insertion (C3). It resolves exactly the artefact the record already brackets (programme L14626; the sentence of record calls the RX class "an INSTRUMENT ARTEFACT").

**POSITION-INDEX-ALL** (imports vfc; uses `vfc.unit_votes`, whose name resolution changed). I ran `rerun_pia.py`: `analyze(root=<main>, out_path=<scratch>, eval_db=<main>/mmlu_pro_dataset_cache_v2.db)`, with a counting wrapper on `vfc.name_profile_of`.
- **Base-reader vs fix-reader outputs: byte-identical** (0 diff lines).
- Base re-run vs `experiment_results/position_index_all_outcome.txt` (b472d40): 1 line, the harness's CRLF sha on L2.
- **Execution witness:** the fix build called `name_profile_of` 7 times, 4 of them resolved BY CONTENT (the four CONTESTANT originals). The base build has no such function (0 calls). So the changed code ran and the output is identical.
- 55 connects, all ro+immutable.

**TIE-MECHANICS** (`rerun_tm.py`).
- Base vs fix outputs: byte-identical. Record vs base: 1 line (the harness's CRLF sha on L14).
- No discriminator is possible here, because no changed code is on its path. It uses only connect_trap, open_ro, rel, script_shas and stat_of, which are AST-identical in both builds (changed top-level defs: build_comb_repo, build_fixtures, certify_table, combiner_check, name_resolver_long, selftest, unit_votes). The identity is shown by AST, not claimed.

## 3. Defects

| id | sev | defect | fix |
|---|---|---|---|
| D1 | MEDIUM (latent; the record is unaffected: COMB_WRITER is closed and no reuse is planned). It would be HIGH if read as discharging V-C5 | The D-C' denylist still passes 5 dynamic-rebinding routes that are visible in the source: u1 pkgutil.resolve_name, u2 / u7 frame globals (inspect / operator), u3 a gc module walk, u6 compile + types.FunctionType. The docstring's STATED LIMITS list does not name them. The commit subject says "D-C' closed" | Record D-C' as PARTLY closed (15 of 15 listed vectors, not the class). Keep V-C5 in force. Either an allowlist (the writer module may import only the stdlib modules it needs, with names outside a fixed set failing R2) or an expanded STATED LIMITS naming these routes |
| D2 | MEDIUM | Fail-open inside the fix's own scope (f). `transitive_tampering` treats any import with no git history under tools/analysis as "not local" and skips it silently (`if rc != 0 or not h.strip(): continue`). An untracked local module (u4) and a package-path import of a committed patcher (`from tools.analysis import X`, whose top-level name is `tools`: u5) both pass | Fail closed: count as local any name with a file `tools/analysis/<mod>.py` on disk or in history, and any dotted import rooted at `tools`, resolving `from tools.analysis import X` to X. Refuse (R2) any import that is neither in `sys.stdlib_module_names` nor an installed distribution. Add u4 / u5 as fixtures |
| D3 | LOW | Mutant `dep_unparseable_passes` survives: no fixture has a pinned local module that fails to parse | Add one fixture (a committed local module with a syntax error at the pin) |
| D4 | LOW | NAME_PROFILE_CONTENT's four values are not checked by the selftest (mutant `wrong_content_sha` survives). A wrong hash silently falls back to basename | Verified here 4 of 4 against the files, and by the real-run witness. Optionally print, on every real run, the count of CONTESTANT units resolved by content (expected 4 plus copies) |
| D5 | LOW | After the merge, position_index_all's selftest INFO says "(DIFFERENT; a mismatch refuses every real run)". That is false: `load_cert` compares the certificate JSON's writer sha, not the imported module's, and a real run proceeds with the new reader. So the index at main imports a vfc reader its READY (f32c526) did not cover | Registrar note by insertion: the index's outcome re-derives byte-identically with the a985eff2 reader (section 2, witness 4 content resolutions). Do NOT bump VFC_PIN_LF (it pins the certificate of record's writer) unless a new certificate is written |
| D6 | LOW (carried, not claimed) | abf4db5 D4 (partial-unresolvable LONG / WIDE tables certify on the resolved subset) and D5 (label_space descriptor) are not addressed by this commit | Stays queued; no claim was made |

## 4. Conditions

- **C1.** V-C5 stays in force. Its clause "unless D-C' is fixed first" is NOT met (D1, D2: 7 of 7 new vectors are false certificates). Any addition to COMB_WRITER or reuse on another E-COMB cache still requires the battery (tamper_adv2.py, callsite_adv.py, rj_history.py, writer_tamper_scan.py) with 0 false certificates outside the ruled limits.
- **C2.** RX is still unruled. The fix removes RX's only instance on record but not the branch. Any reuse of the instrument requires the registrar's RX ruling first (programme L14626).
- **C3.** Disclosure by insertion. The registrar records that under build blob:aab89f37 / sha256-lf16:a985eff263414fd9 the certificate's output would move at record lines L1, L154-L157, L345, L350, L389, L400 and L403-L404:
  - classes 54 / 5 / 0 / 0 / 1 / 2;
  - P4 count 1, still HELD, on pin timing alone;
  - the copy CERTIFIED-CONTESTANT, with a unit identical to its original's.

  No criterion or prediction verdict moves. The outcome file of record (c731836) is not rewritten.
- **C4.** The merge is the single path `tools/analysis/vote_frame_cert.py` from 97d830c. The merge commit's blob must read aab89f37 (`git rev-parse HEAD:tools/analysis/vote_frame_cert.py`), and nothing else may be staged.
- **C5.** Any READY or record citing the new build names all three hash kinds: blob:aab89f37eb3ee7c50a8ff888c05d1409f64522a2 / sha256-lf16:a985eff263414fd9 / sha256-crlf16:e42ab00a95d931be.

## 5. What this review does not show

- It does not show that no dynamic route beyond u1-u7 exists. An AST denylist cannot show that.
- It does not re-run `--run` against the full 184-file scan. The scan was restricted to the 62 recorded caches to avoid the in-flight trace_truncation.db. The 3 harness lines are identified above.
- It does not re-run the `--dry-run` or the pool guard as an operator would. The index re-run did call its pool verification, read-only.
- It runs no Gradle tests: there is no Kotlin change.

## Commands (reproduce; scratch = the session scratchpad `vff/`)

```
git -c core.autocrlf=false archive <eba09f3|97d830c> tools/analysis src/main/kotlin experiment_configs | tar -x -C vff/t_<c>
(cd vff/t_<c>/tools/analysis; PYTHONDONTWRITEBYTECODE=1 python [-O] vff/guard.py <vote_frame_cert|position_index_all|tie_mechanics>.py --selftest)
python vff/mutate_vff.py vff/t_97d830c vff/guard.py                      # 34 applied, 32 killed, 2 survived
python vff/guard.py vff/tamper_adv2.py vff/t_<c>/tools/analysis           # new: 7 of 22 false (u1-u7); base: 17 of 22
python vff/guard.py vote_frame_rr3/{callsite_adv,rj_history,h3_adv}.py vff/t_97d830c/tools/analysis
python vff/rerun_vfc.py vff/t_<c> vff/rr_<old|new>; diff rec.txt rr_old.txt; diff rr_old.txt rr_new.txt; python vff/jdiff.py ...
python vff/rerun_pia.py vff/t_<c> vff/pia2_<c>; python vff/rerun_tm.py vff/t_<c> vff/tm_<c>
git -c core.autocrlf=false show 97d830c:tools/analysis/vote_frame_cert.py | sha256sum     # a985eff263414fd9...
```
