# POST-RUN review: ADAPTIVE-PROFILE (run 2026-10-09, main 980c3982, blob aff80c1d), adversarial reviewer

Zero calls. Read-only: the gen view was opened `mode=ro&immutable=1`, with sha256 checked before and after (EQUAL). The EVAL view was NOT opened. busy.ps1 rc 1 before the read.
Registration: prog L25133ff (`## Registered 2026-10-08 (before any code or call) — ADAPTIVE-PROFILE: ...`). Scorer authority: D-2026-10-08-5 (L25317ff). H pin: L25352ff.

## Verdict

**NO OUTCOME: a failed precondition (a fail-closed refusal), not a result.**
- The refusal is VALID. [AP-DENOM] fired correctly against a registered denominator that I reproduce to the digit.
- AP1 (D_C, LB95, MDE80 0.00062) is **NOT RECOMPUTABLE, and I did not compute it.**
  - No fit ran, so there is no number to check.
  - Computing D_C myself would be an EVAL fit outside the registered single read. It would spend the information the slot protects.
- The H line does not exist; the run refused before `h_lines`. The scorer-is-official check is CONFIRMED by its count-gated code path, not by any word printed in the log.
- Nothing here is of record. Condition for a re-run: R-1..R-3 below, plus the author's decision on the marker (A-1).

## Per-claim table (deciding claims only)

| # | Claim (operator) | Finding | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Registered TRAIN 11,841 items / 10,781 components is the correct target | CONFIRMED | Own count over the gen view: TRAIN 12,351 items (11,275 comp). Structurally key-complete (all 18 ACTIVE cells single): **11,841 items / 10,781 components**. GATE 1,944 / 1,794. Roster 18, Llama-3-70B absent. To the digit. | - |
| 2 | Script counted TRAIN by item (11,841 / 11,841) | CONFIRMED | `union_route_common.py` L232 passes `cfg.pre["train_unit"]`. `v2_declared_cells.py` L228 sets PRECONDITIONS `train_unit="item"` (ruling 3), and its `build_ud` L585-589 builds `train_units` by item. `adaptive_profile.py` L1476 compares `train_units["n_units"]` to `comp_train` 10781. | BLOCKER (code) |
| 3 | Why the review missed it: "the fixture derives comp_train from itself" | PARTLY | The fixture's own counts are **1,101 items / 934 components**, so self-derivation alone would have tripped the check. The real cause: the fixture config `v2_declared_cells._fixture_cfg` L1599 sets `train_unit="component"` while the real config (L228) has `"item"`. The selftest ran a different unit from the run. The mutants X61 / L2700-2701 test the check, but only under the fixture's unit. | HIGH |
| 4 | `train_units` decides nothing else in AP | CONFIRMED | grep `train_units` in adaptive_profile.py: L1476, L1479, L1498 only (the check and two prints). The bootstrap resamples EVAL components (`Dt.comp`, L821). So the fix touches no deciding statistic. | - |
| 5 | Scorer = official, no MATH-FIX overlay | CONFIRMED (code + log) | Scorer.read_key (L1226-1236) forces overlay False and refuses if a caller passes anything else. scorer_keys L1246 refuses on any `overlay_rows`. Log: TRAIN overlay rows 0, EVAL 0. The GATE count is not printed but is gated by the L1246 refusal. | - |
| 6 | H table pin 6b010fa6 matched; 2 hits in the programme | CONFIRMED | sha256 of `math_h_table.csv` = 6b010fa60dde7278…eb1d1 (LF and the CRLF-stripped renderings agree). `grep -c 6b010fa6 docs/judge_v2_program.md` = 2. | - |
| 7 | H line descriptive only | UNDETERMINED (not reached) | The run refused before `h_lines`, so there is no H line. Its code (L1252-1269) prints "DESCRIPTIVE, decides nothing"; prior delta2 review covers it. | - |
| 8 | Blob aff80c1d, LF of record | CONFIRMED | `git rev-parse HEAD:tools/analysis/adaptive_profile.py` = `git hash-object` = aff80c1d0798b49b…; log prints sha256-lf16 f35a50f400ec9216 / crlf16 a38dc2aaca9c2c8a; no tools/ change in 980c3982..HEAD (1 commit, da1ef992). | - |
| 9 | Views unchanged; 0 calls | CONFIRMED | run.log: gen_view c2930c60… BEFORE = AFTER (TRAIN and GATE); eval_view e35b7518… BEFORE = AFTER. My own read: gen view sha EQUAL before/after. | - |
| 10 | EVAL key was read; no fit ran; no outcome | CONFIRMED | `experiment_results/archv2/adaptive_profile/` holds 1 file (`find -type f \| wc -l` = 1), the marker. No outcome.txt. run.log is 78 lines (whole file read). `grep -ci 'brier\|accura\|theta\|D_C\|LB95'` = 2, and both are pre-read header lines (L17 PLANNED, L19 DISCLOSED). **No EVAL-derived statistic was printed.** The EVAL lines are structural counts only (cells single/multi, overlay rows). | - |
| 11 | Backup intact | CONFIRMED | `sha256sum -c SHA256SUMS` in E:/TaxoArena_backup_20261009_adaptive_profile_incident: 4/4 OK. run.log is identical to E:/TaxoArena_tmp/ap_run/run.log. | - |
| 12 | `docs/judge_v2_program.md` modified in the working tree (operator note) | REFUTED (now) | At review time, `git status --short docs/judge_v2_program.md` is empty. | LOW |

## Support (re-measure after the run)

Not applicable. No EVAL fit exists, so DEFF, n_eff and the MDE cannot be re-measured. The registered Support (EVAL 5,907 / 5,404, DEFF 2.118, n_eff 2,789, MDE80 0.00062) is unchanged. The TRAIN component count is a precondition, not a support term.

## Defects and fixes

- **R-1 BLOCKER (engine-coder).** Make [AP-DENOM] count TRAIN components from the data, independent of `train_unit`: `len(set(D.comp[k] for k in D.T))` against `comp_train`. Do the same in the L1498 print.
  - Do NOT flip PRECONDITIONS `train_unit`: it is ruling 3 of record for other consumers, and AP never resamples TRAIN.
  - Pinned modules are left unedited.
- **R-2 HIGH (engine-coder).** Make the selftest run the REAL `train_unit` ("item"), or run both units.
  - Add a mutant that restores the item-count form. It must be killed under the real unit (fixture: 1,101 items vs 934 components).
  - This closes the fixture/real divergence (claim 3).
- **R-3 (reviewer).** A delta READY on the new blob before any re-run, plus a re-pin of the blob in briefs.
  - The delta READY must re-run the real `--dry-run` and show `TRAIN 11841 (10781 components)` printed from the data path.
  - Today that line is unreachable in a dry-run (`build_ud` runs only after the EVAL read). The builder should therefore add a dry-run TRAIN component count (structural, pre-key, as in my script) so the precondition is checked BEFORE the marker is written.
- **R-4 MEDIUM (process).** The ordering defect behind the incident: a precondition that the dry-run can evaluate (TRAIN units) was checked only after the write-once marker and the EVAL read.
  - Every denominator check that needs no EVAL data must run before `G.read_marker`.

## Author decision needed

**A-1.** Does the slot count as used?
- Reviewer's evidence for the decision: the EVAL key was read into memory and discarded, with 0 fits.
- No EVAL statistic was computed or printed (claim 10). The only EVAL facts emitted are structural counts already known from the dry-run and UNION-AF-ROUTE (5,907 / 5,404).
- Technically, a re-run after R-1..R-3 sees nothing a first run would not have seen. Clearing the marker is the author's call (or a registrar's ruling on the author's words): move it, with its sha, into the incident backup, and record the clearance as a declared deviation.

## Commands / scripts (backup E:/TaxoArena_backup_20261009_ap_postrun, SHA256SUMS)

```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   -> rc 1 (free), before the gen-view read
python E:/TaxoArena_tmp/ap_review/comp.py   # gen_view_REG.db mode=ro&immutable=1, side JOIN item (cv mc6-2026-09-11),
   # response_lite cell counts, 18 ACTIVE, all ==1 -> TRAIN 11841 / 10781; GATE 1944 / 1794; sha before = after c2930c60...
python E:/TaxoArena_tmp/ap_review/fx.py     # AP.build_base(tmp on E:) -> fixture n_train 1101, comp_train 934
grep -n 'train_unit' tools/analysis/{union_route_common,v2_declared_cells}.py   # L232; L228 "item"; L585-589; L1599 "component"
grep -n 'train_units' tools/analysis/adaptive_profile.py                          # L1476, L1479, L1498 only
sed -n 1208,1249p tools/analysis/adaptive_profile.py                              # Scorer / scorer_keys refusals
git rev-parse HEAD:tools/analysis/adaptive_profile.py ; git hash-object tools/analysis/adaptive_profile.py   # aff80c1d both
sha256sum experiment_results/math_scorer_h/math_h_table.csv ; grep -c 6b010fa6 docs/judge_v2_program.md      # pin; 2
find experiment_results/archv2/adaptive_profile -type f | wc -l                   # 1 (the marker)
wc -l run.log ; grep -ci 'brier|accura|theta|D_C|LB95' run.log                    # 78; 2 (header lines 17, 19)
sha256sum -c SHA256SUMS   (incident backup)                                         # 4/4 OK
```

## Own mutants (deciding path: the denominator gate)

- M1: fixture with the real unit ("item"). Derived from fx.py rather than executed: n_units 1101 != comp_train 934, so [AP-DENOM] would refuse. This shows the selftest only passed because its unit differed from the run's. Decisive for claim 3.
