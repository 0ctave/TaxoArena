# DELTA-2 READY review w0: RP07, RP08, RP05, RP03/04, RP11, RP06 (2026-09-29)

Reviewer: adversarial-reviewer. Zero judge / Azure / Ollama calls. No real-data mode was run (no --dry-run, --run, --analyze or --go).
Scope: the delta over the delta1 tips of READY_w0_delta1.md (fd6a349), plus regression. Every branch was rebased onto e09e551, so each delta is `git diff <delta1 tip> <new tip> -- <branch paths>`. Main is at 8c2b846 (the steward's commit, docs/ + one csv only).
DB checks: the main DB mtimes (embeddings_cache / ratings / snapshots / snapshots_frozen) were equal before and after. The rp07 worktree stub DB and snapshots_frozen.db sha256 were equal before and after. `status --porcelain | wc -l` = 0 in all six worktrees after the review.
Scratch: `scratchpad/rev_delta2/` (rp07/run.sh + run.log, rp08/my_mut.py, rp05_my.py, rp05_e2e.py, rp05_mut.log, rp11/, rp0304_harness.log).

## VERDICTS

| build | tip (delta over) | verdict | merge | run / window |
|---|---|---|---|---|
| RP07 THREAD-CAP | c812919 (d09f8c8; content already in main via cfcec54) | READY-WITH-CONDITIONS | MERGEABLE (the one new .sh) | B1 after C7-3; B4 after its witness (C7-2 ruled) |
| RP08 EMBEDDER-PLUMBING arms | 3bc3f3d (1ddbdfa) | READY-WITH-CONDITIONS | MERGEABLE | P-2 [EMB-GUARD] (C8-1) still owed; gemma `--go` needs the gemma WAL checkpoint first |
| RP05 FLAT-GENERALITY | 5ab4d89 (2650b34) | **READY-WITH-CONDITIONS** (B5-1 CLOSED as built) | MERGEABLE (last) | `--run` NOT READY: C5-1 (HIGH) and the VA_FIT_SIZES pin (C5-2) |
| RP03/04 v2 readers | 622a989 (db10f08) | READY-WITH-CONDITIONS (tool only) | MERGEABLE | `--run` NOT READY: C34-3 (PRECONDITIONS None in both scripts; RP03 PLAN not at ruling 9) |
| RP11 STAGE0b + DATASET-SURVEY | 639e60f (505b34b) | READY-WITH-CONDITIONS (tool only) | MERGEABLE | `--run` after a rule-7 window; C11-5 LOW; survey `--analyze` HAZARD (14 rows owed) |
| RP06 CERT-REDRAW-R512 | fdf2d90 (3152d15; blob d611b3ac unchanged) | READY-WITH-CONDITIONS | MERGEABLE | `--run` NOT READY: ruling 13 (mismatch REFUSES) unbuilt, L437 still prints "suspect" and continues; D3 DONE |

**MERGE ORDER.** Every tip merges into main 8c2b846 with 0 conflicts (`git merge-tree --write-tree`). Since e09e551, main has touched no branch path (it changed only docs/reviews/STEWARD_w0_preconditions.md and one experiment_configs csv).
1. RP07 c812919: one new file.
2. RP08 3bc3f3d: embedder_arms.py.
3. RP03/04, RP06, RP11: any order (disjoint paths).
4. RP05 last.

Merge each by path, then `git commit -- <paths>` and `merge-base --is-ancestor <prev HEAD> HEAD`. After merge 1, run `sh tools/threadcap/sitenull_noemb_leg.sh` in a worktree.

## PER-CLAIM TABLE (deciding claims only)

| # | claim (builder) | verdict | mine vs claimed | sev |
|---|---|---|---|---|
| 7.1 | C7-1: the no-embeddings leg kills Y1 | CONFIRMED | Tip: NOEMB 4/4 OK, stub sha256 f1c1d714... equal. Y1 (delta1 y1.sed): OK=2 MISSING=2, KILLED. Own Y7-2 (cap print moved after the EMB-GUARD print): the order leg is MISSING, KILLED | - |
| 7.2 | post-merge regression (owed by fd6a349) | PARTLY | Suite at main+sh: **470 tests, 2 failed**, the known two (MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest), so 453 + 17 of RP08. run_proof_delta.sh: **11/13**. GUARD-line and GUARD-refused are MISSING: siteNull now reaches `[EMB-GUARD] REFUSING before any replicate: raw vector dimensions {} != {4096}` on the 4 KB stub BEFORE the heap guard, so the heap-guard refusal has no executed witness on the merged code | MEDIUM (C7-3) |
| 8.1 | C8-2: Y8-D killed | CONFIRMED | selftest 29 PASS. --mutants 22/22 KILLED, Y8-D "embed_card ignores --go" among them via EA-CARD. embedder_guard 37 / 22 of 22 | - |
| 8.2 | C8-3: route parity (min cos >= 0.9999, 20 texts, slice-256) runs before any write | CONFIRMED | EA-PARITY value checks read; open_ro refuses a non-empty -wal. Own Y8-F (write before parity) KILLED. Own witness Y8-G: an embed_fn that returns 1 vector for 20 texts is ACCEPTED (it prints "1 texts ... PASS"). The production ollama_embed refuses on a count mismatch (L154), so this is defence in depth only | LOW (C8-4) |
| 5.1 | B5-1: V_A on random labels scores 0.3143 | CONFIRMED | FG-VA-ORACLE printed **0.3143 (66/210)** <= chance 0.3619 + 0.1; R3 reading 1.0000 on the same fixture. delta1 witness va_oracle.py (both sides label-free) 0.3524. Selftest 90 PASS; --mutants **34/34 KILLED** | - |
| 5.2 | the deciding path (tree_measures) is label-free on the EVAL side and keyed | CONFIRMED as built, **UNGUARDED** | Code: lab_t = TRAIN only; va_cell_fn(b, otree, rul, Qt, lab_t); m1_block/m2_block pass Qt by identity. E2E replica through tree_measures: shipped V_A M1 0.5925 (A0) vs **1.0000** under own mutant Y5-B (Qh filed on the fit side with its labels). Y5-B SURVIVES the full selftest, and so does own Y5-C (lab_t row order reversed). The oracle check covers the helper wiring, not the run's | HIGH (C5-1) |
| 5.3 | ruling 12 (sizes printed; pin OWED: no V_A fit; mismatch refuses) | CONFIRMED | E2E legs and 2 mutants KILLED. Steward pin at 8c2b846: sum 8,125 = fit_n | cond. C5-2 |
| 34.1 | K46 plan re-derived: SE 0.03305, DESCRIPTIVE-ONLY | CONFIRMED | Mine: se_iid 0.014877, SE 0.03305, half-width 0.0648, MDE80 0.0925, n_eff 110.3, break-even DEFF 2.075, FAILED below 0.7075. Pilot 390/2.0 gives 0.02485 / 0.0696 / 1.487 / 0.7304. Gap 0.060 < MDE 0.0925, so DESCRIPTIVE-ONLY. All to the digit | - |
| 34.2 | selftests / mutants | CONFIRMED | k46 48 PASS, 14/14; v2_declared_cells 75 PASS, 22/22 (plain and -O). delta1 harness R1-R6, K1-K5, Y3-1, Y3-2: **13/13 KILLED** (0 SURVIVED, by count). Own Y4-A (SE on p = bar) and Y4-B (census p 0.85) both KILLED | - |
| 34.3 | "C34-1 all brackets now exist" | PARTLY | The brackets exist (e09e551). But `PRECONDITIONS = dict(census_bracket=None, interval_form=None, beta_len=None)` (k46 L123), and a selftest asserts that it is None (L901). --run still refuses | cond. C34-3 |
| 11.1 | Y11-2 killed (A4b set equality) | CONFIRMED | a4b_counts_only KILLED ("same-size, same-side-count, DIFFERENT collision set") | - |
| 11.2 | Y11-1 killed (A1 scan scoped to the A2 sample) | CONFIRMED | a1_full_key KILLED through mode_run (135 checks, 14 failed). Own Y11-4 (R3 conflict pass reads the full key) SURVIVES, and so does Y11-5 (Y11-4 plus the R3 seal removed): the mode_run fixture has no duplicate uuid, so the R3 seal never executes. The steward counts 0 duplicates in all 49 real files, so the branch is unreachable on the data of record | LOW (C11-5) |
| 11.3 | C11-4 PLAN_C1 = STAGE0b's | CONFIRMED | Mine: SE 0.005265, MDE80 1.474pp, n_eff 5,637.2; d 0.25: 1.865pp (printed "1.86pp") | - |
| 11.4 | C11-2 value-vs-status | CONFIRMED | survey selftest 21 PASS, --mutants 5/5 (status_trusted KILLED); stage0 selftest 139 PASS plain and -O, --mutants 20/20 | - |
| 6.1 | RP06 unchanged | CONFIRMED | blob d611b3ac, same as the delta1 pin; `git diff 3152d15 HEAD -- cert_redraw_r512.py` = 0 files. Selftest mutants 18/18; delta1 Y6-1 and Y6-2 KILLED. D3: `sha256sum -c SHA256SUMS` OK x2 (sums file 9e8e70453df94dbf) | - |

## DEFECTS AND CONDITIONS (each with its fix)

**C5-1 HIGH (RP05, before `--run`). The oracle guard does not cover the deciding path.**
- Add a FG-E2E leg: the replica with declared categories drawn AT RANDOM, run through run() -> tree_measures, must give V_A M1 <= chance + 0.1.
- Or assert, on the existing replica, that tree_measures' V_A M1 equals a recomputation through va_cell_fn(Qt, lab_t).
- Either way it must kill Y5-B (EVAL side filed with its labels in tree_measures) and Y5-C (lab_t misaligned with Qt).

**C5-2 (RP05, before `--run`). Pin VA_FIT_SIZES.**
- The registrar brackets the steward's pin: o0_clean_s42 (944, 905, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348), sum 8,125.
- Then a builder delta sets VA_FIT_SIZES, and a delta re-pin follows.

**C7-3 MEDIUM (RP07, before B1 / any real siteNull).** The heap-guard refusal lost its execution witness when RP08 merged: the EMB-GUARD refuses first on the stub.
- Fix (a): a fixture DB with 4096-d vectors for the frozen tree's site members, so that the GUARD leg reaches the heap guard.
- Or fix (b): move the heap guard ahead of the EMB-GUARD read. It needs only site sizes, and the order is the builder's to argue.
- Then re-run run_proof_delta.sh to 13/13.

**C7-2 (carried).** The route is ruled (e09e551). B4's witness procedure is still owed, and M1 and M4 are carried.

**C8-1 (carried).** P-2 (i)/(ii) must print `[EMB-GUARD]` from siteNull; X8-K is still killed by no test.

**C8-5 (precondition).** Before `--embed-missing gemma_raw --go`, embeddings_cache_embeddinggemma_latest.db needs its WAL checkpointed (-wal 4,643,272 B per e09e551). route_parity and write_vectors refuse until then (fail-closed).

**C8-4 LOW (RP08).** In route_parity, refuse when `len(new) != n` (zip truncates silently). This kills witness Y8-G.

**C34-3 (RP03/04, before `--run`).**
- A builder delta sets PRECONDITIONS from the e09e551 brackets:
  - census_bracket = 5572465 / e09e551;
  - interval_form = "both_agree" (ruling 6);
  - beta_len = ("STRUCK", the e09e551 bracket) (ruling 7).
- In v2_declared_cells.py (blob 13938c13, unchanged), four PRECONDITIONS are still None: steward_bracket, residual_file, train_unit and p2_measure. Set them from 5572465 and from rulings 3 ("item") and 4 ("contribution").
- Its PLAN also still carries C1 DEFF 1.711 / n_eff 3,596 / SE 0.00659. Ruling 9 adopted scored N 5,907, Kish 1.3115, SE 0.00674, MDE 1.89pp: re-pin PLAN to that, with a value check.
- The L901 "all None" check is retargeted.
- LOW: --run prints the read's key-decidable ONE n and components beside the census 544 / 160 and flags a mismatch. P5 (330-450) is known FAILED at 544.
- Then a delta re-pin.

**C11-5 LOW (RP11).** Add one duplicated uuid to the st_mode_run fixture so that the R3 conflict pass and its B1 seal execute. This kills Y11-4 and Y11-5.

**C11-1 (carried).** A rule-7 window is needed for `--run`. A5 was confirmed by the steward (8c2b846).

**DATASET-SURVEY HAZARD.** `--analyze` is write-once. With 14 candidate rows owed it would record C1 FAILED of record. Do not run it before B2 is complete.

**C6-1 (carried).**
- M-3 ruled (13): an instrument-check mismatch must REFUSE. At d611b3ac the check is still the soft one of delta1, so this needs a builder delta, then a delta re-review.
- LOW: parenthesise st4b.
- M-2 forward (RP50).

## PINS (blob LF of record; sha256-lf16 / sha256-crlf16 of the working tree)
- RP07 c812919: tools/threadcap/sitenull_noemb_leg.sh 7fe212982b3c94d2cd78d83ae0b7cd89acc7c493 231e330e1aad33f5 / 91ec7ba922d24d6d.
- RP08 3bc3f3d: embedder_arms.py 4c85e2e03eae61b26952fa245064f7691f3d64ca 80345066cceaea08 / 6e8b2b75fef41e76.
- RP05 5ab4d89: flat_generality.py 2920358b847f01f024889a8dafbea17cdc942b80 c458d4d856880377 / 3f9aa53456bc4ce7. flat_mix_mmlu.py cdb354f1 and mix_lrt_site.py fbb480ca are unchanged.
- RP03/04 622a989: k46_key_read.py 3aa10f25ed263aedb3aeb987b9304a12d3b1e082 512e6b12a3642f0c / f5b39bc59404aade. v2_declared_cells.py 13938c13 and v2_reader_guards.py 14d10ff8 are unchanged.
- RP11 639e60f:
  - supergpqa_stage0.py 35b11858eab0cc20fe0982fe4af14a471a0fb6b1 271528ead60f5279 / b452cdc1bde89218;
  - dataset_survey.py d83f382485c3c3a5051f80176b855d3ca7e970ed 573f4058cd1e4294 / bbe721df3017d2ec;
  - the exclusion json 11839fa3 is unchanged.
- RP06 fdf2d90: cert_redraw_r512.py d611b3ac (unchanged).

## REVIEWER MUTANTS (this delta; decisive ones marked)
- RP07:
  - Y7-2: cap print after the EMB-GUARD print. KILLED (NOEMB-order).
  - Y1 (delta1): KILLED. Decisive.
- RP08:
  - Y8-F: write before parity. KILLED.
  - Y8-G: witness; a short response is accepted. LOW.
- RP05:
  - Y5-B: tree_measures files Qh on the fit side with its labels. SURVIVED (M1 1.0000 vs 0.5925). **Decisive.**
  - Y5-C: lab_t reversed. SURVIVED.
- RP03/04:
  - Y4-A: SE on p = bar. KILLED.
  - Y4-B: census p 0.85. KILLED.
- RP11:
  - Y11-4: R3 pass over the full key. SURVIVED (unreachable on real data: 0 duplicates).
  - Y11-5: Y11-4 plus the seal removed. SURVIVED.

## COMMANDS (compact)
```
sh rev_delta2/rp07/run.sh      # NOEMB tip 4/4; Y1 2 MISSING; Y7-2 1 MISSING; run_proof_delta 11/13; suite 470 / 2 known; WTDB_EQUAL
python tools/analysis/embedder_arms.py --selftest | --mutants ; python rev_delta2/rp08/my_mut.py   # 29 ; 22/22 ; Y8-F KILLED, Y8-G accepted
python tools/analysis/flat_generality.py --selftest | --mutants     # 90, ORACLE 0.3143 (66/210) ; 34/34
python rev_delta2/rp05_my.py ; python rev_delta2/rp05_e2e.py         # Y5-B, Y5-C SURVIVED ; A0 M1 0.5925 vs 1.0 under Y5-B
python [-O] tools/analysis/{k46_key_read,v2_declared_cells}.py --selftest ; python rev_delta1/rp0304/harness.py > rev_delta2/rp0304_harness.log
python -c "import math; si=math.sqrt(.86*.14/544); print(si*math.sqrt(4.934), 2.8*si*math.sqrt(4.934), (0.06/(2.8*si))**2)"
python [-O] tools/analysis/supergpqa_stage0.py --selftest | --mutants ; python tools/analysis/dataset_survey.py --selftest | --mutants
python tools/analysis/cert_redraw_r512.py --selftest ; python rev_delta1/rp06/mut.py ; (cd TaxoArena_data/evidence_2026-09-25/redraw_r512_dag_snapshots && sha256sum -c SHA256SUMS)
for t in c812919 3bc3f3d 5ab4d89 622a989 639e60f fdf2d90; do git merge-tree --write-tree --name-only main $t | grep -c CONFLICT; done   # 0 x6
```
