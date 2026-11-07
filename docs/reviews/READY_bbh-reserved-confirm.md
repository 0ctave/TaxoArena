# READY review: BBH-RESERVED-CONFIRM preparation (lead #4; D-2026-11-06-3 item 3; benchzoom `bbh-reserved-prep` 4d08a3d..a922fe7; TaxoArena draft b1baa4cb)

Reviewer: adversarial-reviewer, 2026-11-06. Zero LLM calls. Read-only on both repositories and on every data file, except
for this file. No RESERVED value was read: the reviewer's own loader filtered on WORK ids and returned 0 RESERVED rows.
Reviewed blobs (LF, from `git hash-object`): `examples/bbh-reserved-confirm.py` `blob:e0a6d70e` (the working tree is LF);
`examples/bbh-reserved-prep.py` `blob:dafd9eda` (its CRLF working-tree rendering is `blob:aaad88f4`, 1,919 CR);
`docs/bbh-reserved-prep.md` `blob:e19f0d0b`; `tests/test_bbh_reserved_confirm.py` `blob:f46fe171`. The TaxoArena draft
`docs/agents/plans/2026-11-06_bbh-reserved-confirm_registration_draft.md` is `blob:18c2f8c2` (LF, equal to HEAD).

## Verdict

- **Preparation: READY to go to the author.** The sealed RESERVED responses are unread. The WORK estimate reproduces to
  the digit wherever the arm is deterministic. The draft states the author's three choices as options, and the runner
  refuses to open without the flag and with PENDING constants.
- **`freeze` / `open`: NOT READY.** C1 (HIGH) must be fixed, C2-C6 must go into the registration, and a delta READY is
  needed on the commit that sets the four constants. That delta must include a real `reserved --dry-run` under the
  registered roster and text option: the `--text all` path (O2 (b)) has never run on real data, because it refuses
  while REG_TEXT is PENDING.
- **Merge:** not asked. The branch has 6 new files, 0 under `src/`, and master is still 4d08a3d, so the execution graph
  owes nothing.
- **Support:** present and NON-VACUOUS. DEFF has a stated source: it was MEASURED by design B. The SE re-derives from
  that DEFF and n to within 0.02pp. C3's SE is an avoidable approximation (C2 below).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | sealed RESERVED responses never read (code) | `SealedReader(` is constructed once in the code, in `cmd_open` L712, after `open_refusals` (L705) and after the frozen-bytes identity check (L710). Every parquet read is wrapped by `AccessAudit` (pd.read_parquet), and no `pq.read_table` path is reachable from either runner (`im.load_items` is never called). `SplitGuard.read_scores` refuses RESERVED ids before opening a file | CONFIRMED | - |
| 2 | ... (logs, files, outputs) | WORK run `meta.json`/summary: 343 reads, 1,185,751 ids, RESERVED in a filter 0, returned 0, SplitGuard 0. Dry runs R128 (×2, identical apart from times) and R342: 445,953 = 128×3,457+3,457 and 1,185,751 = 342×3,457+3,457 ids; RESERVED 0/0; reader constructed 0. `find E:/benchzoom_demo` for OPENED.json and freeze_R*.json gives 0; `followups/bbh-reserved-confirm` does not exist. The only OPENED.json (`E:/TaxoArena_tmp/.../sand/dbgc`) is a fixture: roster 6, 540 values = 90×6. All 28 of the builder's scratch `.py` files are covered. 22 are patch, spec or table writers that edit code and read no data. 3 debug runs (`dbg_*`) use fixture paths only. The mutant runner works on sandbox copies, and `ast_eq` reads git. `time_af.py` reads text only and asserts WORK-only. Last-access times cannot tell the sides apart: each part holds both | CONFIRMED (qualifier Q1) | - |
| 3 | data object: WORK 3,457 / 24 subtasks; 2,662 clusters, Kish 4.416; R128 sha c47b3eb5, R342 71c12468; 442,496 / 1,182,294 values | Own reader: 3,457; 2,662; 4.416; c47b3eb5 / 71c12468; 1,182,294 rows returned, 0 RESERVED, 0 duplicates, 0 NaN, binary; off-majority (KEPT, WORK) pairs 0 | CONFIRMED | - |
| 4 | design A G_DEC +3.27 (SE 0.59) / +5.38 (0.60) | +3.269 (0.577) / +5.380 (0.605). Own draws; the SE gap is about 1 MC SD at B = 2,000 | CONFIRMED | - |
| 5 | G_FAM +3.56/+5.67; G_PLACEBO −2.69/−3.30; BS 0.7382 | +3.558/+5.670; −2.690/−3.298; 0.7382 | CONFIRMED | - |
| 6 | G_FKI +3.29 / +5.33 (share 1.01 / 0.99) | With an independent k-means (sklearn, n_init 10): +3.329 / +5.417; M_FKI +0.06 / +0.04 against +0.03 / −0.05 | CONFIRMED (gap ≤ 0.09pp, implementation) | - |
| 7 | design B DEC: mean point +2.82 / +4.58; SE_proj 1.24 / 1.34; power C1 0.75 / 0.98; 9 / 19 of 20 above 0 | Exact pseudo-splits: +2.823 / +4.584, SD 0.68 / 0.82, 9 / 19; own two-stage draws: SE_proj 1.221 / 1.349, DEFF2 2.92 / 3.49, power 0.763 / 0.979 | CONFIRMED | - |
| 8 | C2 power 0.87 / 0.995 (SE_proj FKI 1.07 / 1.17) | Own k-means: SE_proj 1.149 / 1.252, power 0.826 / 0.991. The value depends on the k-means; the registered instrument is the builder's | CONFIRMED (implementation-sensitive) | LOW |
| 9 | Support arithmetic: n_eff 763 / 674; MDE80 3.47 / 3.75, 2.99 / 3.28; P2 ranges; P7 | 762.4 / 674.3; 3.47 / 3.75, 2.99 / 3.28; P2 [+1.68, +4.86] / [+3.67, +7.10]; Φ(2.635) = 0.996. SE from the stated DEFF and n: per-row SD 0.347 (from DEFF2 and mean SE2 at n_E 1,419), so 0.347/√762 = 1.257pp against 1.240 (R128) and 1.356 against 1.339 (R342) | CONFIRMED (gap 0.017pp) | - |
| 10 | C3: SE_L ≈ 0.74 / 0.80 (equal-variance approximation), power 0.61 / 0.91, upper bound 0.86 / 0.93 | The exact identity Var L = 0.5 Var G_F − 0.25 Var G_D + 0.5 Var M, applied to the draft's own projected SEs, gives SE_L 0.635-0.656 / 0.693-0.712 (power 0.72-0.74 / 0.96-0.97; MDE80 1.78-1.84 / 1.94-1.99). The direct two-stage SE_L with the reviewer's k-means is 0.730 / 0.776. The "upper bound" bounds nothing that the identity leaves open | PARTLY | MEDIUM (C2) |
| 11 | the author's choices written as options | O1 (R128 / R342), O2 ((a) WORK texts / (b) all 5,761), O3 (whether, when, which words). Each option carries numbers for both sides, and no option is pre-selected or marked "Recommended". D-2026-11-06-3 (3) is quoted verbatim | CONFIRMED (qualifier C4) | - |
| 12 | `open` refuses without the flag (tried) | Real CLI, 3 forms without the flag: exit 1, "opened only with --open-sealed-reserved". Tripwired real CLI WITH the flag and PENDING constants (every reader, real_paths, load_split, np.load and work_side raise if reached): "REG_COMMIT is PENDING" ×2; constructed 0. `freeze`: "REG_COMMIT is PENDING". The output directory does not exist before or after | CONFIRMED | - |
| 13 | open refuses on a dirty tree | `pr.check_clean` → `code_state` deps list prep, bbh-work, census, flat-compare, meter_test, identifiable_map, granularity_work, the plan and `src`, but NOT `examples/bbh-reserved-confirm.py`. In a sandbox clone at a922fe7, a modified confirm script passes `check_clean` (dirty ''), while a modified prep script refuses (OM6) | REFUTED | HIGH (C1) |
| 14 | tests: selftests PASS; 9 pytest; mutants 61/61 (confirm), 60/61 (prep); suite 1043/1/0 | confirm selftest PASS (108 PASS lines, 0 FAIL); prep PASS (117, 0); pytest file 9 passed; own OM1-OM5 5/5 killed; suite log `dry/suite.log` 1043 passed, 1 skipped (pre-a922fe7; a922fe7 is AST-identical to fa37758 outside the module docstring: own AST check) | CONFIRMED | - |
| 15 | plan before any statistic; brackets insertion only | 4675b56 at 14:30:27, runner b4a3057 at 14:58:44, run 14:59-15:47. Plan diffs 4675b56..b4a3057 and b4a3057..fa37758 remove 0 lines (add 15 and 45). prep.py is unchanged after b4a3057. 0 network/LLM call paths in either runner | CONFIRMED | - |

## Defects and conditions (each with its fix)

- **C1 HIGH (blocks `freeze`/`open`):** the clean-tree refusal of the opening does not cover the opening script itself. Fix:
  add `examples/bbh-reserved-confirm.py` (and the test file) to the dirty check that `open` and `freeze` use, e.g. a
  `code_state` in the confirm runner. Have `open` print and require the confirm blob equal to a pinned `CONFIRM_BLOB`,
  and add a selftest that edits a sandbox copy of the confirm script and expects a refusal (count check, not a presence check).
- **C2 MEDIUM:** C3's Support uses an equal-variance approximation where an exact identity exists. Fix: print SE_L from
  the identity (0.64-0.66 / 0.69-0.71). Re-derive P5 (0.72-0.74 / 0.96-0.97) and P8 ([+0.85, +2.47] / [+1.75, +3.53]),
  or keep the approximation, labelled conservative, beside the reviewer's direct 0.730 / 0.776. Drop "Cauchy-Schwarz
  upper bound". R128's C3 stays below MDE80 (1.66 < 1.78).
- **C3 MEDIUM:** `REG_COMMIT` is checked for presence only: any string set in the runner and passed as `--registration`
  passes. Fix: `open` verifies `git -C <TaxoArena> cat-file -e <REG_COMMIT>` and greps the heading
  `## Registered ... — BBH-RESERVED-CONFIRM` in `docs/judge_v2_program.md` at that commit (count == 1).
- **C4 MEDIUM (wording; feeds O3):** C2/C3's "label-free" arm is k-means at k = 24, the declared subtask count. That is
  one integer of label information, and the framing's clause speaks of "where labels are missing". Fix: C2/C3 carry
  "k set to the declared count". The anchor-free arm (leaf count chosen by the recipe, 22 on WORK; WORK S_AFI 1.044 /
  0.913) is the label-free reading: printed beside, or deciding if the author prefers.
- **C5 LOW:** "THIN" is not a Support word. Fix: R128 C1 / C3 read SCOREABLE (power 0.75 / 0.72-0.74, below 0.80) or
  DESCRIPTIVE-ONLY. The registrar decides, not the coder.
- **C6 LOW:** `verdicts` checks G4 before T1, while the draft and the docstring say "T1 evaluated first". Fix: reorder the code
  or state "G4 (refusal) before T1" in the registration.
- **Q1 (qualifier, no fix):** the seal is enforced at the API level. pyarrow decodes row groups and then filters on ids
  inside the reader, and `np.load` decompresses the whole npz `X` (RESERVED vectors included) before indexing WORK
  rows. No RESERVED value reaches the analysis. The census's structural NaN / non-binary counts over 5,761 rows ([C-3])
  are the record's convention. RESERVED texts were read earlier by the embedding and by BBH-WORK V0 (BBH-WORK L3).
- **L1 LOW:** `test_open_refuses_without_the_flag_and_with_pending_constants` calls `cmd_open(..., True, tmp_path)` with
  default (REAL) paths. It is safe today only through the refusals. Pass fixture paths, or a tripwire `paths`.
- **L2 LOW:** the placebo of the sealed read is permuted over all 5,761 (stream 8). The WORK estimate permuted it
  within WORK (stream 3). So P6's basis is the analogue design; say so in the registration.

## Own mutants (sandbox copies; synthetic selftest only)

| id | change | result | decisive |
|---|---|---|---|
| OM1 | `if not registration or registration != reg.commit` → `if registration and ...` (a missing --registration accepted) | killed ("--registration absent refuses") | yes |
| OM2 | C3 evaluated unless C1 FAILED (gate `!= "HELD"` → `== "FAILED"`) | killed (boundary C1 UNDETERMINED) | yes |
| OM3 | T1 on the placebo point, not its interval | killed (null fixture) | yes |
| OM4 | deciding interval from the one-stage SE (C-7 substitution) | killed ("point ± 1.96 SE2") | yes |
| OM5 | placebo policy = the DEC policy | killed (frozen-policy identity refusal) | yes |
| OM6 | confirm script modified and uncommitted at `open` | SURVIVED (`check_clean` passes; see C1) | yes |

## Commands (reviewer's scripts and logs: `E:/TaxoArena_backup_2026-11-06_review-bbh-reserved-confirm`, 10 files + SHA256SUMS `sha256-lf16:2b4325df1e43ea9c`, 10/10 OK)

```
git -C benchzoom_wt diff --stat 4d08a3d..HEAD               # 6 files, 4,476 insertions, 0 under src/
git show --name-only --format= <c> | wc -l                   # 4675b56 1, b4a3057 4, fa37758 4, a922fe7 1; TaxoArena b1baa4cb 1
python asteq.py                                              # fa37758 vs a922fe7 confirm.py: AST equal outside docstring
sha256sum -c work/SHA256SUMS (3/3); backup SHA256SUMS.backup 35/35; cmp backup vs sources: 4 records + 26 af npz equal
grep -n 'SealedReader(\|read_parquet\|pq\.\|read_table' examples/*.py   # one construction site; no pq path reachable
find /e/benchzoom_demo \( -name OPENED.json -o -name 'freeze_R*.json' \) | wc -l     # 0
venv/python -I recompute.py          # own loaders/clusters/policies/bootstrap/k-means: claims 3-9 (log recompute_full.log, 349 s)
python examples/bbh-reserved-confirm.py open --roster 128 --text work [...]          # exit 1 x3, no flag
python tripwire.py                   # real CLI with --open-sealed-reserved, tripwired: REG_COMMIT PENDING; constructed 0
python dirtycheck.py <sandbox clone> # confirm.py modified: check_clean PASSES; prep.py modified: REFUSED (C1)
selftests (sandbox TMP/BZ_SANDBOX): confirm PASS 5 s, prep PASS 6 s; pytest tests/test_bbh_reserved_confirm.py: 9 passed
python om.py                         # OM0 control survives; OM1-OM5 killed
```

The CPU run happened while another agent's `roster-structure-meter.py` (MATH, 3 workers) was running. The reviewer used
one single-threaded process and read no file of that run.
