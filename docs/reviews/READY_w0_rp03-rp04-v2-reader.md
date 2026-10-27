# READY review: rp03-rp04-v2-reader (V2-DECLARED-CELLS legs U and M; K46-KEY-READ) — 2026-09-27

## VERDICT: NOT READY

The code is careful. Every count the builder reported reproduces, and the pins, the view seals, B3 order, B1 markers and write-once all hold. It is still NOT READY, for two HIGH defects:
- **D1:** all three key reads pull key values from rows that ruling c5a8cb6 §2 lists as "never" into the process. The script filters them out in Python, after SQLite has already returned them.
- **D2:** 11 of the reviewer's 11 mutants survive both selftests, including four on deciding paths.

The script cannot run in any case: 8 preconditions are None. Every fix below therefore lands in the same delta that sets those preconditions, and that delta gets a delta-READY.

Reviewer: adversarial-reviewer. Zero judge calls. No JVM. Single-threaded (OMP / MKL / OPENBLAS = 1). No run of the test on real data: no `--c0` and no `--run`.

The reviewer's own reads were key-free only. The SQL was asserted free of is_correct / correct / output_zlib / gt_raw / answer_text / pred. The DBs were opened `mode=ro&immutable=1`:
- the K46 store;
- eval_view_REG.db, opened directly and not through `open_eval`: structure counts for mc6 and mmlu-pro-v2 only;
- gen_view_REG.db;
- multicorpus_cache_v1.db (count of questions × models only).

The sha256-bytes of the three v2 objects were equal before and after (e35b7518… / c2930c60… / 44724d25…). Scratch lives in `scratchpad/rev_rp0304/`.

## Object under review
- Branch `w0-rp03-rp04-v2-reader`, tip b31c31d, parent a357ef0. `git merge-base --is-ancestor a357ef0 b31c31d` passes.
- `git diff --name-status a357ef0 b31c31d`: 3 lines, 0 not "A". No existing file is touched.
- Main HEAD is still a357ef0. The worktree is clean: `status --porcelain | wc -l` = 0.

| file | blob (LF, `git hash-object`) | sha256-lf16 | sha256-crlf16 | result |
|---|---|---|---|---|
| tools/analysis/v2_declared_cells.py | d60dee1fd57eaee867719592b064f9f505afc3e1 | b4da6e748be2183f | e4a6b7ae4d862aa5 | CONFIRMED (recomputed from `git show b31c31d:<path>`) |
| tools/analysis/k46_key_read.py | 349a691f3ba9fc4a9f50e0de7c0030d52dc01afd | 88acb49e89e36f8e | f137f7e02be2d46d | CONFIRMED |
| tools/analysis/v2_reader_guards.py | 24f0ac4d7dd943d145721aea0cc2bf68dbfab8e9 | 295a4e9b41dfe848 | 9996ddfdef1e6a4e | CONFIRMED |

The working tree holds the LF rendering (`file`: UTF-8, no CRLF). **These pins are superseded by the fix delta**, and no run may use them.

## Per-claim table

| # | claim | result | command / script | got vs claimed |
|---|---|---|---|---|
| 1 | RP03 selftest: 61 checks, 0 failed, 21/21 mutants killed, 43/43 branches, plain and -O | CONFIRMED | `python [-O] tools/analysis/v2_declared_cells.py --selftest` | rc 0 / 0; 61, 0 failed, 21/21, 43/43 |
| 2 | RP04 selftest: 33 checks, 0 failed, 13/13 mutants killed, 24/24 branches | CONFIRMED | `python [-O] tools/analysis/k46_key_read.py --selftest` | rc 0 / 0; 33, 0 failed, 13/13, 24/24 |
| 3 | The selftests kill mutants of the deciding logic | **REFUTED** (11/11 reviewer mutants survive) | `scratchpad/rev_rp0304/mut/harness.py`; controls in `harness_ctrl.py` | see D2. The positive controls (r_verdict `>=`; K46 bar `>`) are KILLED, so the harness is live |
| 4 | Pins: gen c2930c60…, eval e35b7518…, store 44724d25… equal the pins and are unchanged after the read | CONFIRMED | `sha256sum` before / after the reviewer's reads | equal |
| 5 | Leg U: pool 5,642 components / 6,153 items; roster 18; Meta-Llama absent | CONFIRMED | `indep2.py` / `indep3.py` | 5,642 / 6,153; 18 ACTIVE, 0 non-ACTIVE |
| 6 | Leg U TRAIN: 12,351 mc6 items (of 12,358 side rows); GATE 2,033; 9,085 multi-response cells; key-complete 11,841 (UNUSABLE) / 12,346 (AGREE) | CONFIRMED | `indep2.py` | 12,351; GATE 2,033 items / 38,808 response_lite rows; 9,085; 11,841 / 12,346 |
| 7 | Leg U EVAL: 14 strata ≥ 120 (IFEVAL + 13 MMLU-Pro) | CONFIRMED, and extended | `indep3.py` (key-free cell existence) | 14 under BOTH rules. Scored N = 5,907 in 5,404 components (Kish 1.3115) under UNUSABLE_CELL; 6,153 / 5,642 (Kish 1.3036) under AGREE; 4,428 EVAL multi cells |
| 8 | Leg M: 3,400 / 3,492; K37 sha 3a3204cc…; multi cells 3,771 (K37) / 1,221 (K12); key-complete K12 3,351 / K37 3,350 (UNUSABLE), 3,453 / 3,452 (AGREE); 13 categories | CONFIRMED | `indep2.py` | identical; 13 in all four cases; smallest is computer science at 128 |
| 9 | RP04 identity gate PASS on every line | CONFIRMED | `indep.py` | 2,664 / 5,328 rows; stop 5,328; grok-4-1-fast-non-reasoning 5,328; A 1,039, B 1,022, TIE 600, INVALID 3 (all NONE); ONE 818 / NONE 1,846; 566 variants; ONE-only stems 174, NONE-only 392; ONE components 173 |
| 10 | run_id `ARCH-V2-PILOT-K46-run1` inside the run2 file | CONFIRMED benign | `archv2_pilot_k46_outcome.txt` L2: "run ARCH-V2-PILOT-K46-run1 \| store pilot_k46_verdicts_run2.db" | matches the record; see D8 |
| 11 | Side join: every scheduled side has exactly one response row (so "refused" is expected to be 0) | CONFIRMED | key-free join (model, seen_ck) over the 4,491 distinct sides | {1: 4,491} |
| 12 | C0-U inputs reachable | CONFIRMED (counts only; values not computed) | key-free count on multicorpus_cache_v1.db | complete 21,606 / EVAL 6,482 / TRAIN 15,124, equal to REG |
| 13 | Inertness: no existing code modified | CONFIRMED | diff count above | 3 files added, 0 modified. No Kotlin, so Gradle is not required |
| 14 | "Dry-runs print no statistic" | CONFIRMED by code and by the builder's logs | the tripwire seals the key in dry mode; the `dry_reads_key` mutant is killed | — |
| 15 | Only the key is read, from the ruled rows | **REFUTED** | `indep2.py` | D1 |
| 16 | V2-DECLARED-CELLS Support C1 arithmetic | CONFIRMED | hand re-derivation | 0.00562 × sqrt(6482/6153) = 1.02639 × sqrt(1.304) = 1.14193 → SE 0.006587, MDE80 1.844pp, n_eff 3,596, break-even DEFF 4.526. Kish recomputed as 8,021 / 6,153 = 1.3036 |
| 17 | C1 Support at the object that will actually run | PARTLY | as 16, at N 5,907 and Kish 1.3115 (UNUSABLE_CELL) | SE 0.00674, MDE80 1.89pp, break-even DEFF 4.35: still SCOREABLE; the registered N 6,153 is not the scored N under UNUSABLE |
| 18 | C2 Support | **PARTLY** | registration Support (b) / (d) | The SE is transported from a 52-stratum instrument (UNION-PROFILE-HOME) while the deciding denominator is 14 strata (D3). Transporting PRI K12 at 14 anchors instead gives SE 0.0339 and MDE 0.095: still SCOREABLE at a null p95 ≤ 0.60 |
| 19 | K46-KEY-READ Support arithmetic | CONFIRMED | hand re-derivation | n 390.2; sqrt(0.86 × 0.14 / 390) = 0.017570 × 1.4142 = 0.024848; MDE 0.0696; break-even DEFF 1.4875 |

## Defects

**D1: HIGH. The key SELECTs read rows the ruling never admits (letter of c5a8cb6 §2 and note (c)).** The filtering happens in Python after SQLite has returned the row. Counts, all key-free (`indep2.py`):
- **Leg U fit** (`read_key(tw, "response_lite", …)`, v2_declared_cells.py L327): `SELECT … is_correct, is_correct_mathfix FROM response_lite WHERE corpus_version=?` returns **38,808 GATE rows** (2,033 GATE items). The ruling's §2 "never" column for leg U lists GATE.
- **Leg M** (same function, table `response`): returns **34,188 rows from 10 models outside K37**. These include Meta-Llama-3-70B-Instruct (CONTEXT rule 6: excluded) and the 9 dropped / BANNED models (W10). The ruling admits only "response (model, item_id, is_correct) for K12 and K37".
- **RP04** (`read_keys`, k46_key_read.py L328 and L349):
  - `response` returns **140,977 is_correct values outside the 566 variants**, out of 167,308 in total. They include the five fresh stage-1 anchors, which S1 requires to stay key-sealed until the stop decision.
  - `reference` returns **853 v0 `correct` values outside the 174 ONE variants** (1,027 in total).
  - Ruling note (c) states that "RP04 reads no key cell outside that set" (the 37 × the store's items); §2 says "never: any eval_view row outside the 566".

No value leaves memory. But the ruling governs what is read, not what is kept, and the tripwire log would record the unfiltered statement as the run's evidence.

FIX: put every filter in the SQL.
- Leg U: `JOIN side s ON s.item_id = r.item_id AND s.side = 'TRAIN'`.
- Leg M: `AND model IN (<K37>)`.
- RP04: `AND model IN (<the 37>) AND seen_ck IN (<566 variant ids>)`, and `AND variant_id IN (<174 ONE variants>)`, both as bound parameters.

Also add a selftest check: the number of key rows fetched must equal the in-scope count on a fixture that carries out-of-scope rows (a GATE row, a non-roster model row, a non-scheduled variant row). A mutant that drops the SQL filter must then be killed.

**D2: HIGH. Mutation adequacy.** The reviewer applied 11 single-edit mutants to the scripts; all 11 SURVIVE (rc 0, SELFTEST PASS). Script: `scratchpad/rev_rp0304/mut/harness.py`.

| mutant | what it breaks | severity |
|---|---|---|
| R1_c1_percentile_decides | C1 decides on the percentile interval instead of the registered point ± 1.96 SE_2stage | HIGH (deciding) |
| R2_eval_unstratified | EVAL components resampled across strata instead of within stratum | HIGH (deciding SE) |
| R6_c1_hi_le | C1 FAILED fires at hi ≤ 0.01 instead of hi < 0 | HIGH (deciding) |
| K3_gate_invalid_none_dropped | the identity-gate row "INVALID with NONE" deleted | MEDIUM (a gate row with no check) |
| R3_null_seeds_shift | null RandomState seeds 2..21 instead of 1..20 | MEDIUM |
| R4_residual_subset_inverted | "G without the 422" scores ONLY the 422 | MEDIUM (declared printed-beside) |
| R5_p2_unweighted | P2 contribution without the n_BBH / N weight | MEDIUM (P2) |
| K1_c2_sign | C2 printed as NONE − ONE | MEDIUM |
| K2_v0_not_joined | reference.correct never joined (the v0 split prints None) | MEDIUM |
| K4_ref_read_all_vintages | the vintage assert removed | LOW |
| K5_a12_one_side | ARENA12 sub-board admits a match with one ARENA12 side | LOW |

FIX: add checks until each is killed. Required:
- the C1 interval equals point ± 1.96 × sd(two-stage contrast);
- each EVAL stratum's resampled unit count equals its unit count, in every replicate;
- C1 boundary cases hi = −1e−9 → FAILED and hi = 0 → UNDETERMINED;
- each identity row perturbed in turn → refusal;
- `null_seeds == (1..20)` asserted in the reads;
- the NO_RESIDUAL n equals N − |residual ∩ EVAL|;
- P2 contribution against a hand value;
- the C2 sign against the naive per-class accuracies;
- the v0 split against the fixture truth;
- a wrong-vintage reference refused;
- A12 counted against a hand count.

**D3: MEDIUM. The C2 Support object differs from the deciding object.** The registration transports its SE from UNION-PROFILE-HOME's 52-stratum interval (half-width ≤ 0.06). At the v2 floor only 14 strata qualify: IFEval plus 13 MMLU-Pro categories, under both variant rules (`indep3.py`, key-free). C2 therefore reads almost the same 13 categories as leg M's C3, with the 18-model OLL roster.

FIX: a registrar bracket before the read, containing:
- C2's Support re-derived at 14 strata: e.g. PRI K12 at 14 anchors, SE 0.0339, MDE 0.095, SCOREABLE while the null p95 ≤ 0.60 (break-even about 0.745);
- C1's Support restated at the scored N once the variant rule is fixed (5,907 / Kish 1.3115 under UNUSABLE_CELL → SE 0.00674, MDE 1.89pp, SCOREABLE);
- the outcome printing "14 of the 52 union strata (13 MMLU-Pro + IFEval)" beside C2 and beside F3, whose licence it tests (0.8537, 52 strata).

**D4: MEDIUM. The trigger scope is inferred by the builder.** The registration says only that "its interval wholly above 0 VOIDs C1". The builder's reading (a) extends this: P1, P2, P3 and P7 read UNDETERMINED (BY TRIGGER), and F1 is NOT EVALUATED. That scope is carried over from ROUTER-CLEAN-POLICY's *registered* T1 (d6b5ca8), and that same ruling states "which triggers exist is REGISTERED, never inferred by a builder (CERT-UNDER-FILTER R2)".

FIX: a registrar bracket before the read, ruling:
- T1's scope, including that C2, P4 and F3 are not pre-empted;
- the closed-interval scoring of predictions (reading (b)).

Reviewer's position: admit the builder's scope, with one addition. Under T1 the outcome must also print that the USE clause is NOT licensed as content-closed, because a VOID C1 is not a HELD, even though F1's "withdrawn" is not fired.

**D5: MEDIUM. K46-KEY-READ's pre-read verdict-line bracket is not constructible as worded.** Support (f) says: "the census and the measured DEFF re-derive this line in a pre-read bracket". A measured component DEFF of the C1 estimand needs right_A, which is the verdict × key join, which is the read itself.

The census (key-decidable n per class × anchor × v0-correct) does read is_correct and reference.correct. That is admissible under R2 / note (a), provided it selects no verdict column.

FIX: the bracket must do three things:
- name a pre-read DEFF from cluster sizes only (e.g. the Kish m̄ of key-decidable ONE matches per component, an upper bound at ρ = 1), never the post-read one;
- state that the census joins no `vote`, `combined` or `match_status` column;
- land in the same delta as the script's PLAN dict (deff, n, n_eff, se, mde, verdict), which is currently hard-coded to the registration's pilot numbers.

**D6: LOW. The beta_len line cites the wrong bracket.** `st["beta_bracket"] = cfg.pre["census_bracket"]` (k46_key_read.py L607), so the outcome would say beta_len was "struck … by the registrar's bracket <census bracket>". FIX: `beta_len = ("STRUCK", <striking bracket ref>)`, and print that reference.

**D7: LOW. The W12 thread guard only warns.** `main()` prints a warning when OMP / MKL / OPENBLAS ≠ "1", and numpy is imported at module top before the check. FIX: in `--c0` and `--run`, refuse unless all three are "1" (the run-operator exports them before starting python).

**D8: LOW. The identity gate prints run_id but does not assert it.** FIX: assert `run_ids == ["ARCH-V2-PILOT-K46-run1"]` (outcome L2).

**D9: LOW. The C0 gates do not exercise the v2 read path.** C0-U runs through RCP's loader and C0-M through PRI's `load_record`. They test the fit, the key builder and the profile wrapper, not `read_key`, the variant rule or the is_correct_mathfix overlay; the selftest alone covers those. By code inspection, C0-U will reproduce 0.5912 / 0.6220 whenever the loader does, because the fit and fallbacks are identical to RCP L431-L471. FIX: disclose one line in each outcome.

**D10: LOW. The KeyTripwire is a word match.** `SELECT *` would bypass it; neither script uses one, and no SQL views exist in either view DB. FIX: refuse `*` in the select list.

**D11: LOW. Some mutants are "killed" by completing.** `m_k37`, `m_marker`, `m_write` and `m_c0` count as killed when the mutated call simply finishes. That is only sound if an unmutated negative check exists. It does for B1, write-once and C0; it does not for a wrong K37 sha. FIX: add "a wrong K37 sha refuses".

**D12: LOW (note).** The placebo's TRAIN pseudo-strata depend on the set of key-complete EVAL items (the shuffle runs over TRAIN plus EVAL). Under AGREE_OR_UNUSABLE that set depends on EVAL values. The placebo is not part of the B3 file and is only a trigger, and this is the carried RCP form. FIX: disclose one line.

## Builder's open parameters and readings

All 8 preconditions are confirmed as genuinely open. None may be chosen by the builder.
- **A1** (`train_unit`) is a real ambiguity. The registered DEFF composition, 1.312 (RCP, item-level TRAIN) × 1.304 (EVAL-component Kish), is consistent with "item", but the words "clusters = CK-CLOSE components" leave it open.
- **A2** (`p2_measure`) is real.
- **K1** (`interval_form`) is real. For consistency, RP03's C1 carries the RCP normal form.
- **K2** (`beta_len`) is real: no estimand is registered and the ruling admits no length column. Striking it needs a registrar bracket before the read.
- The steward items (`variant_rule`, `steward_bracket`, `residual_file`, `census_bracket`) are owed by the data-steward.

RP03 readings:
- (a): D4.
- (b) closed interval: CONFIRMED, pending the same bracket.
- (c) P6 joined by the registrar: CONFIRMED.
- (d) leave-BBH-out and per-source use the all-TRAIN policy, restricted on EVAL: CONFIRMED (the paeec precedent +1.305 on 4,754).
- (e) floors on the structural count before the read, the post-read count printed and never used to re-select: CONFIRMED.
- (f) C0-M uses the p2dca judged question set only to reproduce a key number: CONFIRMED, because the registration requires it.

RP04 readings:
- (a) the same opener and column as 86e88d2, and not its (model, item) lookup: CONFIRMED, conditional on D1. The same path also means the same row scope.
- (b) unstratified component bootstrap: CONFIRMED as admissible. Anchors are fixed design strata, so unstratified resampling is conservative. A stratified form is not registered.

## Merge and run procedure (after the fixes)
1. The engine-coder fixes D1, D2 and D6-D11 on the branch. The selftests must kill all 21 + 13 builder mutants and all 11 reviewer mutants, plain and -O, single-threaded.
2. The registrar brackets, before any read:
   - the steward's half (variant rule, coverage, the 422 list pinned by sha256-bytes, the 422-in-pv2_41dbd count, the RP04 census with no verdict column);
   - A1, A2, K1;
   - K2 struck;
   - T1 scope and closed-interval scoring (D4);
   - the C1 / C2 Support at the scored objects (D3);
   - RP04's pre-read DEFF and verdict line (D5).
3. The engine-coder sets the 8 preconditions and the RP04 PLAN by a delta that cites those brackets, then re-pins (blob / sha256-lf16 / sha256-crlf16).
4. The adversarial-reviewer does a delta-READY on that blob. Only after it may the coordinator merge by path: `git add` the three new files, then `git commit -- <paths>`, then the ancestry check.
5. The run-operator works in the MAIN checkout, inside one W1 rule-7 window: the W1-W5 probe shows every pool DB FREE, at least 12 GB RAM free, no construction, no JVM, one process, OMP / MKL / OPENBLAS = 1. In order:
   - `--selftest` for both scripts;
   - `--dry-run` for both;
   - `v2_declared_cells.py --c0 --leg U`, then `--c0 --leg M` (a miss VOIDs the leg as a READY defect);
   - `--run --leg U`, then `--run --leg M`, then `k46_key_read.py --run`.

   Each run prints its shas before and after. The write-once outcomes and B1 markers must not pre-exist.
6. The adversarial-reviewer checks the numbers: it re-measures DEFF, n_eff and MDE from the outcome, and recomputes C1, C2, C3 and RP04 C1 from the aggregates.
7. The registrar records the outcome, then the ledger via ledger_patch.
