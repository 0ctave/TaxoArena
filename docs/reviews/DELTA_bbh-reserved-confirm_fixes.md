# DELTA review: BBH-RESERVED-CONFIRM fixes of READY 814bafa6 C1-C6 and the author's choices (D-2026-11-07-1)

Reviewer: adversarial-reviewer, 2026-11-07. Zero LLM calls. Read-only on both repositories and on every data file, except for
this file. benchzoom `bbh-reserved-prep` a922fe7..727cc67 (01d9c79 plan [P3], f87461a tree runner + shared module, 6fab746
[P4], 727cc67 sealed runner; 7 files, 0 under `src/`, not merged: `merge-base --is-ancestor 727cc67 master` false). TaxoArena
draft v2 79becdd4 (1 file added). Reviewed blobs (LF, `git hash-object` = `HEAD:`): `examples/bbh-reserved-confirm.py`
`blob:5acb0671` (LF tree); `examples/bbh_reserved_common.py` `blob:fe5530b0` (LF); `examples/bbh-reserved-tree.py`
`blob:cc955d59` (LF; unchanged since f87461a, the run of record); `tests/test_bbh_reserved_confirm.py` `blob:877e9cc7` (LF);
`docs/bbh-reserved-prep.md` `blob:bc6fb750` (LF); `examples/bbh-reserved-prep.py` `blob:dafd9eda` (working tree CRLF,
`blob:aaad88f4`, 1,919 CR; unchanged). Draft v2 `blob:b24aadf0` (= HEAD). No RESERVED response, text or vector was read.

## Verdict

- **READY-FOR-REGISTRATION: yes**, with D1 (MEDIUM) and D6 (LOW) worded into the registration by the registrar. C1-C6
  of READY 814bafa6 are fixed and confirmed (table). The tree arm's WORK estimate reproduces to the float wherever it is
  deterministic, and within Monte Carlo error where it is not. The draft v2 matches the code and quotes the author's three
  choices verbatim; O3 stays open. The sealed side is unread.
- **`freeze` / `open`: NOT READY** (unchanged gate). They need the registration, the constants commit, a delta READY on
  that commit with a real `reserved --dry-run --roster 342 --text work`, and D2 (MEDIUM) fixed or carried as an
  operator check. D3-D5 (LOW) go into that delta.
- **Support:** present and NON-VACUOUS. DEFF has a source (MEASURED by design B / B'). n_eff and SE re-derive for C1 / C2.
  For C3 the SE re-derives only under design B''s per-row variance, and the word sits 0.35pp below its MDE80 (2.22 against 2.57; D1).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | C1 fixed: open / freeze refuse a dirty tree, incl. the opening script (OM6) | Sandbox clones at 727cc67, real `code_check()` of the clone. Control: PASS, manifest 31 files, sha256 36543d3d (= the dry run's line). **OM6** (confirm script, one line appended, uncommitted): REFUSED, 2 findings (` M`, blob a0ae0e67 != 5acb0671). Also REFUSED: common module, test file, `src/benchzoom/tree.py`, plan, an untracked `examples/zz_untracked.py`, an `--assume-unchanged` edit (1 finding, blob compare only). A COMMITTED edit passes (manifest 18c5cca9): D2 | CONFIRMED | - |
| 2 | C2 fixed: C3's SE from the exact identity, 0.917pp | Identity on the builder's SE_proj (1.2267 / 1.3387 / 1.0364): 0.9173pp to the digit. Own two-stage draws on the 20 pseudo-splits (own stream, B = 200): SE_proj G_DEC 1.337, G_AFI 1.249, M_AFI 1.014 -> identity 0.921; direct 0.925 [0.922]. DEFF2 3.38 / 3.49 / 4.79 / 4.17 [3.42 / 3.39 / 4.99 / 4.14]. No bound or approximation is printed | CONFIRMED (gap <= 2.1 %, MC) | - |
| 3 | C3 fixed: REG_COMMIT exists, is on main, programme AT it has exactly 1 heading | `registration_check` L603-621. Programme at HEAD and main: 0 of 25,895 lines match `REG_HEADING`, so the registration makes it 1. The draft's heading matches the pattern. Z12-Z19 and own RV1 killed (Tests) | CONFIRMED | - |
| 4 | C4: AF-I decides C2 / C3; FK-I beside, labelled | `FREE_ARM = "AFI"` L258. `verdicts` C2 = G[free], C3 = L(free) (L540-542, L861). The FK-I line carries "k set to the declared count" (L929). Z20-Z23 killed | CONFIRMED | - |
| 5 | C5 / C6: Support words; G4 before T1 | `support_word` L624-629 has only SCOREABLE / DESCRIPTIVE-ONLY ("THIN" occurs only in the docstring and test text, 4 of 4). `verdicts` L534-537 runs G4 on G_DEC, G_AFI, G_PLACEBO and L before T1. The draft says the same (L110-112) | CONFIRMED | - |
| 6 | plan [P3] before the new statistic; brackets insertion only | P3 01d9c79 05:08:33. Builder scratch dir born 05:17:16. f87461a 05:28:01. Run 05:28:22-05:53:07 (meta 1485 s). `tree/` and `tree/af/` born 05:51:34; no `summary_partial`; af built 20 / cached 0. Plan numstat 60 / 0 and 37 / 0 | CONFIRMED | - |
| 7 | tree arm, design A' (R342): G_DEC +5.38 (0.60), G_AFI +4.91 (0.57), M_AFI -0.47 (0.24), L_AFI +2.22 (0.32), S 0.913 | Own loader, policies and cross-fit on the record's 25 fold caches (rows_sha 25 / 25 equal to own folds). Points FLOAT-EQUAL to `readouts.csv`: 0.053803876193231126, 0.04911773213769164, -0.004686144055539485, 0.02221579404107608, S 0.9129032258064516. Own SEs (B = 2,000, own stream): 0.611 / 0.572 / 0.242 / 0.316 | CONFIRMED | - |
| 8 | design B': 20 trees, leaves 15-19; G_AFI mean +4.25, SE_proj 1.23; L mean +1.96, SE_proj 0.92 | Own pseudo-split code: rows_sha 20 / 20 equal to `tree/af/b_*.npz`. Leaves list equal. Mean points float-equal (G_AFI 0.042538912970572926, L 0.019619971991363883). SE_proj 1.249 / 0.925. Share of splits above 0 for L: 0.35 [0.25] (MC) | CONFIRMED | - |
| 9 | Support R342: C1 SCOREABLE (5.38 > 3.75), C2 SCOREABLE (4.91 > 3.43), C3 DESCRIPTIVE-ONLY (2.22 < 2.57); P5 0.68 | Own: 5.38 > 3.74; 4.91 > 3.50; 2.22 < 2.58 (power 0.675). Same words. P2 [3.665, 7.096] and P8 [1.046, 3.397]: the draft's rounded ranges and `PREDICTIONS` agree | CONFIRMED (D1) | - |
| 10 | Support: SE from the stated DEFF and n | n_eff 2,304 / DEFF2 = 674.2 / 679.6 / 556.6 [674 / 680 / 557]. Per-row SD implied by SE_proj, DEFF2 and n: 0.348 / 0.320 / 0.2175. Design A' per-row SD: 0.332 / 0.325 / **0.1825**. Design B' per-row SD: 0.357 / 0.337 / 0.228. G_DEC and G_AFI reproduce under either (<= 5 %). L reproduces only under B'. Under A' (trees on 2,766 rows; the sealed tree uses 3,457): SE_L 0.773pp, MDE80 2.17 < 2.22, i.e. SCOREABLE by 0.06pp, power 0.82 | PARTLY | MEDIUM (D1) |
| 11 | data object | Own read: WORK 3,457 / RESERVED 2,304 ids (pins 3d4d644a / 9ef05cc2, LF). 342 KEPT; ids sha256 71c12468cd49b0dca1004233ea0ee7fae393eb06039b7114d1af37e0ba192b9c (full, own). 1,182,294 values, 0 NaN, binary. Off-majority (KEPT, WORK) pairs 0. Clusters 2,662, Kish 4.416 (own scipy components on own WORK-only vectors) | CONFIRMED | - |
| 12 | cells from WORK texts only; roster 342 | `build_freeze`: AF L402 and FK L398 on `w.X512` / `w.text` (WORK); placebo = subtask labels (metadata). `reserved_cells` uses only the frozen centroids and descent table. RESERVED vectors feed only cell filing, the content clusters of the SE and the twin line. `check_cli` ROSTERS (342,), TEXTS ("work",); the R342_SHA gate (L262, L651); no FKT / AFT in the frozen object (S11 check); Z30-Z33 killed | CONFIRMED | - |
| 13 | draft v2 = code and the author's choices | Instrument blobs 6 / 6 equal. `PREDICTIONS` L270-278 and `SUPPORT_PLAN` L282-285 equal the table and Support (d) / (e). The dry run's frozen sha256 5320b328 also appears in the 11-06 dry run (`grep` of that log). O1, O2 and C4 quoted verbatim; O3 open. H2 lists 2 deviations; the shared module's AF pool is a third (D6) | CONFIRMED | LOW (D6) |
| 14 | sealed side unread (code, logs, files) | Code: `SealedReader(` is constructed at 1 production site (`cmd_open` L813, after `open_refusals`); count 3 in confirm.py (2 selftest units on a fixture guard), 0 in tree / common / prep / tests / src. REG_COMMIT PENDING refuses in `reg_refusals`. Logs: `tree/meta.json` audit 343 reads, RESERVED in filters 0, returned 0, SplitGuard RESERVED 0; `dry_342.log` constructed 0. Files: `find E:/benchzoom_demo` OPENED.json + freeze_R*.json = 0; `followups/bbh-reserved-confirm` absent. The builder's 9 scratch `.py` files read no part and no npz; `explore/s9.py` runs `cmd_freeze` / `cmd_open` on fixtures with an injected `cs`. Own reader: 0 RESERVED ids in a filter or a result | CONFIRMED (Q1) | - |
| 15 | tests: selftests 156 / 71 PASS; 13 pytest; mutants 97 / 98 (Z7 equivalent), 46 / 46; OM6 refuses | Own sandbox runs at 727cc67: confirm selftest 156 PASS / 0 FAIL (49 s), tree 71 / 0 (9 s); `pytest tests/test_bbh_reserved_confirm.py` 13 passed. The builder's mutants re-run: confirm 97 of 98 killed, control passes, Z7 survives (equivalent: an untracked executed module is `??` in porcelain or has no HEAD blob); tree 46 of 46, control passes. Own RV1-RV4 killed, RV5 / RV6 survive (not decisive, below). Full suite not re-run (the delta is `examples/` + one test file; the builder's 1047 / 1 / 0 log taken as given) | CONFIRMED | - |

## Defects and conditions (each with its fix)

- **D1 MEDIUM (registration wording; the registrar's, H3):** C3's DESCRIPTIVE-ONLY depends on the analogue. Design B''s trees
  (about 2,040 rows, 15-19 leaves) inflate the per-row variance of M = AFI - DEC (0.232 against 0.127 in design A') and so
  of L (0.228 against 0.1825). The sealed tree (3,457 rows, 22 leaves) is closer to design A'. Fix: keep the projected SE
  (the conservative reading) as the registered planning SE, and add one sensitivity line to Support (f): "at design A''s
  per-row SD and DEFF2 4.14: SE_L 0.77pp, MDE80 2.17pp, SCOREABLE by 0.06pp, power 0.82". P5 then carries the range
  0.68-0.82, and the registrar fixes the confidence. Nothing in the code changes.
- **D2 MEDIUM (before `open`):** the code check certifies "clean and committed", not "reviewed": a committed edit passes
  with a new manifest sha (case c8). READY C1's pinned-blob leg was not built (a self-pin in the same file would be circular).
  Fix: `open` requires `--manifest <sha256>` equal to the computed `manifest_sha` (the operator copies it from the
  committed delta READY on the constants commit), with a selftest count check. Or, as a minimum, the run-operator compares
  the dry run's manifest line with the READY's pin before `open`, as a written step.
- **D3 LOW:** "modules executed after the code check" is printed only, and after the sealed read (`cc.after_lines`, L865).
  The residual is narrow: porcelain covers `examples/` and `src/` whole. Fix: evaluate it after `work_side` and before the
  `SealedReader` is constructed, and refuse on a NOT CLEAN module.
- **D4 LOW:** "FREEZE_SHA bracketed into this registration BEFORE the opening" is not checked by the runner, which compares
  only its own constant. Fix: `open` counts FREEZE_SHA in `main`'s programme (>= 1, at or after REG_COMMIT). Or the delta
  READY verifies the bracket by hand and says so.
- **D5 LOW:** "RESERVED texts read 0; RESERVED vectors read 0" are string literals (confirm L710-711, tree L555), not counts.
  The audit counts texts; vectors are not counted (`np.load` decompresses the whole `X`, Q1). Fix: count the RESERVED keys
  indexed in `load_vectors` and print that count, or mark the line "(by construction; Q1)".
- **D6 LOW:** ruling (ii) / H2 names two deviations. The build added a third: `bbh_reserved_common.py`'s AF pool replaces
  `prep.run_af` for the tree runner (plan [P3] (b) says the runner imports prep's core). That is functionally the same
  (`af_recipe` / `af_cells` / rows_sha), but it is unrecorded. Fix: a [P5] bracket and H2 item (c) in the registration.
- **Q1 (carried, no fix):** the seal is API-level for the builder's loaders. The reviewer's own loader memory-mapped the
  stored (uncompressed) npz member and indexed only the 3,454 distinct WORK rows. Parquet reads are filtered inside pyarrow.

## Own mutants (sandbox copies; the confirm selftest)

| id | change | result | decisive |
|---|---|---|---|
| OM6 | (prior review) confirm script modified, uncommitted, at the code check | killed (REFUSED, 2 findings; real check on a sandbox clone, row 1) | yes |
| RV1 | `merge-base --is-ancestor` arguments swapped (main ancestor of REG_COMMIT) | killed (the registered commit refused: "the dry run prints the heading it found") | yes |
| RV2 | a sealed reader / ledger constructed before the frozen-bytes identity check | killed ("no refusal constructed the reader") | yes |
| RV3 | deciding SE2: RESERVED clusters resampled without subtask strata | killed (G_DEC SE2 0.057608 vs the loop's 0.060796) | yes |
| RV4 | G4 without L (a degenerate L interval reaches C3) | killed ("G4 on L's SE refuses") | yes |
| RV5 | an examples-named module loaded from outside the checkout not flagged | SURVIVED: test gap, not decisive (`HERE` is first on `sys.path`, so the CLI cannot load an examples module from elsewhere; S12 covers a foreign `benchzoom` module only) | no |
| RV6 | no `benchzoom` package module preloaded before the check | SURVIVED: equivalent for the refusal (porcelain covers `src/` whole); only the manifest's listing shrinks | no |

## Commands (scripts and logs: `E:/TaxoArena_backup_2026-11-07_review-bbh-reserved-fixes`, 14 files + SHA256SUMS, its sha256 1617666956700978..., 14 / 14 OK)

```
git diff --name-only a922fe7..727cc67 | wc -l   # 7;  | grep -c '^src/'  # 0;  git diff --numstat (plan): 60/0, 37/0
git hash-object <path> vs git rev-parse HEAD:<path>  (6 instrument files; --no-filters for prep: aaad88f4)
python -I recompute.py   # own WORK-only loader (pyarrow filter + id assert; memmap of the stored npz member), own
                         # clusters, folds and pseudo-splits checked by rows_sha against the record's AF caches,
                         # own policies, cross-fit and two-stage bootstraps; 20.9 s; log recompute.log (rows 2, 7-11)
bash om6_run.sh          # 9 sandbox clones at 727cc67: real code_check() (row 1); log om6.log
python mutants_rv.py examples/bbh-reserved-confirm_mutants.json rv_confirm --jobs 3   # the builder's 98 + control
python mutants_rv.py examples/bbh-reserved-tree_mutants.json rv_tree --jobs 3         # the builder's 46 + control
python mutants_rv.py rv_spec.json rv_own --jobs 3                                     # RV0 control, RV1-RV6
TMP/TEMP/TMPDIR/BZ_SANDBOX=E:/TaxoArena_tmp/review-bbh-reserved-fixes/st/*: confirm --selftest (156/0), tree --selftest (71/0);
pytest tests/test_bbh_reserved_confirm.py -p no:cacheprovider --basetemp <sandbox>   # 13 passed; worktree porcelain 0 after
find /e/benchzoom_demo \( -name OPENED.json -o -name 'freeze_R*.json' \) | wc -l   # 0
grep -rc 'SealedReader(' examples tests src   # confirm.py:3 only
```

The reviewer ran no real dry run, `freeze` or `open`. The only real-data process was `recompute.py`: WORK ids only, one
single-threaded process, while no other python or java process was running.
