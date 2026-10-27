# DELTA-3 READY review w0 (branch w0-delta3, tip 5a93ecc on 481b613) + POST-RUN SUPERGPQA-STAGE0b (2026-09-29)

Reviewer: adversarial-reviewer. Zero judge / Azure / Ollama calls. Part 1: no real-data mode (no --dry-run, --run, --analyze, --go).
Part 2: stored files only (key DB `mode=ro&immutable=1`, question jsonl, split and exclusion json).
Part 1 scope: `git diff 481b613..5a93ecc` (7 files, +538/-55) plus regression. Prior review: READY_w0_delta2.md (b2ad5ef). Code the delta does not touch is taken from that review.
DB checks: the main *.db stat (mtime, size) was EQUAL before and after. The worktree snapshots_frozen.db sha256-lf16 was 3f7f5e9a470baba3 before and after. `git status --porcelain | wc -l` = 0 in the worktree after every leg.
Scratch: `scratchpad/rev_delta3/` (logs, rp05_my.py, rp08_my.py, harness34.py, mut06.py, run_proof_d3.sh, sg_recompute{,2}.py).

## PART 1: VERDICTS (delta-3)

| build | commit | merge | --run / --go |
|---|---|---|---|
| RP05 FLAT-GENERALITY | df936fa | MERGEABLE | **READY**. C5-1 and C5-2 discharged. Rule-7 window and operator preconditions as usual |
| RP03/04 V2-DECLARED-CELLS / K46-KEY-READ | d517b31 | MERGEABLE | **READY** (C34-3 discharged). P5 stays known FAILED at 544 (scored in the outcome) |
| RP06 CERT-REDRAW-R512 | 0486555 | MERGEABLE | **READY** (ruling 13 built). N6-1 LOW is for the registrar |
| RP07 THREAD-CAP | 5a93ecc | MERGEABLE | B1 **READY** (C7-3 discharged). B4 still waits for its C7-2 witness. M1/M4 carried |
| RP08 EMBEDDER-PLUMBING arms | 65cde94 | MERGEABLE | gemma `--embed-missing gemma_raw --go` **READY-WITH-CONDITIONS**: C8-5 CLOSED (no -wal), C8-4 LOW still open. The C8-1 P-2 witness is still owed (see N7-1) |

MERGE: `git merge-tree --write-tree main w0-delta3` gives 0 CONFLICT. main moved 481b613..f0e5fc9 on docs/ only, and 0 of the 7 branch paths (full `--name-only` lists, not truncated). Merge by path, then `git commit -- <paths>`.

## PART 1: PER-CLAIM TABLE

| # | claim | verdict | mine vs claimed | sev |
|---|---|---|---|---|
| 5.1 | C5-1: FG-E2E-RANDOM runs the deciding path on random labels | CONFIRMED | selftest 95 PASS: V_A M1 max 0.3625 <= chance 0.3625 + 0.1; recompute equal (A0 145/145 ... A4 131/131); R3 oracle 1.0000 >= 0.9. FG-E2E equal (A0-A4 237/237/237/230/237) | - |
| 5.2 | Y5-B and Y5-C (delta-2 SURVIVED) now killed | CONFIRMED | Own rp05_my.py, full selftest (9 groups). **Y5-B KILLED** (A0 400/237 against the recompute). **Y5-C KILLED** (73/237). Builder --mutants: 40/40 | - |
| 5.3 | C5-2 VA_FIT_SIZES = steward pin | CONFIRMED | Tuple equal to the registrar's bracket (prog L21898): sum 8,125 = fit_n. FG-PIN checks the value. Off-by-one and swap mutants are KILLED | - |
| 34.1 | C34-3 PRECONDITIONS from 5572465 / e09e551 | CONFIRMED | The values match rulings 3, 4, 6, 7 and 8 (prog L21873). k46: 50 PASS, 14/14 (plain and -O). v2dc: 80 PASS, 22/22 (plain and -O). Delta-1 harness: **13/13 KILLED**, both identity controls PASS | - |
| 34.2 | PLAN at ruling 9 | CONFIRMED | Re-derived: 0.00562 x sqrt(6482/5907) x sqrt(1.3115) = **0.006742**; MDE80 2.80 x 0.006742 = 0.01888, which prints as 1.89pp; n_eff 5907/1.3115 = **4504.0**. C2 0.0339 / 0.095 as ruled | - |
| 34.3 | (beyond brief) load_residual hashes the LF rendering | CONFIRMED, sound | Worktree file raw 9d66ec944b62f1b7 (CRLF), `tr -d '\r'` b35b3e03b9bcda48 = the pin = `git show HEAD:` bytes. LF is of record (rule 8), the raw sha is printed beside, and a one-id addition REFUSES (selftest). V-c is killed | - |
| 34.4 | (beyond brief) the ruling-10 USE line | CONFIRMED, not a substitution | Ruling 10 (prog L21873) requires that under T1 the outcome print "USE clause NOT licensed as content-closed". It is printed only under T1 (selftest checks both directions; V-e killed) | - |
| 6.1 | ruling 13: a mismatch REFUSES before any output | CONFIRMED | Selftest 10 checks, 19/19 KILLED (ic_soft by st5b and st6). Delta-1 X1-X12, Y6-1 and Y6-2 re-run on the tip: **14/14 KILLED** | - |
| 6.2 | VOID left unchanged ("not a mismatch") | PARTLY | Ruling 13 names only a mismatch. A VOID s42 hierarchical leg therefore runs uncompared | LOW (N6-1) |
| 7.1 | C7-3: heap guard before the embedder guard, witnessed | CONFIRMED | sitenull_heapguard_leg.sh **5/5**. Own discriminator: the same leg with 481b613's SeparationNullBySizeTest.kt gives HEAP-line/HEAP-refused MISSING and EMB-GUARD refusing first; restored, 5/5 again (the changed code executed both ways). noemb 4/4 | - |
| 7.2 | run_proof_delta 13/13 | PARTLY | Own copy: **11/13 with no stub cache** (GUARD legs take the Assumption skip, because the heap guard sits after the cache-presence check). **13/13 with an empty stub** (stub sha unchanged, removed). The committed heap leg is self-contained, so it is the witness of record | LOW (N7-2) |
| 7.3 | suite | CONFIRMED | `gradlew test --offline`: **470 tests, 2 failed**, the known two (MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest). Counted from the result XMLs | - |
| 7.4 | no production change | CONFIRMED | `git diff --name-only 481b613 w0-delta3 \| grep -c ^src/main` = 0. The Kotlin diff moves one block and edits comments | - |
| 8.1 | connect-guard admits exactly the selected arm file | CONFIRMED | Selftest 38 PASS (plain and -O); --mutants **27/27** (the output has 28 KILLED lines: one extra is a log line); embedder_guard untouched. "every arm file admitted" is killed by a NotADirectoryError inside the DURING-admission check, not by its assertion message (still a kill) | - |
| 8.2 | "C8-5 unchanged" (builder) | REFUTED (stale) | `ls ...embeddinggemma_latest.db-wal/-journal \| wc -l` = **0**. The live DB and the backup dir both have mtime **2026-09-29 11:52:07-08**; the 09-27 is only the backup folder's name. The live DB mtime is earlier than 481b613 (12:30), so the refused attempt wrote nothing. C8-5 was CLOSED at f0e5fc9 | LOW |

REVIEWER MUTANTS (delta-3; decisive marked *):
- RP05:
  - Y5-B* KILLED. Y5-C* KILLED.
  - Y5-F: tree_measures heldout rule d1_nearest (C-7). KILLED by the recompute.
  - Y5-G: the random-label bound loosened to +0.5. SURVIVED. This is a test-of-test: the equality leg still kills Y5-B. Not decisive.
- RP07:
  - Y7-3a*: 481b613 order. KILLED (own run).
- RP08:
  - Y8-H: admission not restored when the open raises (try/finally removed). SURVIVED. LOW: the process refuses and exits anyway.
  - Y8-I: open_arm_ro bypasses pool_guard.open_ro. SURVIVED. Equivalent: the flat_mix guard's own -wal rule binds the admitted file.

## PART 1: DEFECTS AND CONDITIONS (each with its fix)
- **N6-1 LOW, registrar.** A VOID s42 hierarchical leg is printed "cannot be compared" and the run continues. Rule whether VOID refuses as well. Code for either reading is one line: instrument_check's VOID branch. R-g is already killed for the current reading.
- **N7-1 NOTE for C8-1 (carried).** On the heap-refusal path siteNull no longer prints any [EMB-GUARD] line (the discriminator of C7-3). So P-2's [EMB-GUARD] witness must be taken on a run whose heap FITS.
- **N7-2 LOW.** run_proof_delta.sh's GUARD leg needs a stub embeddings_cache.db. Cite sitenull_heapguard_leg.sh (self-contained) as the C7-3 witness of record, or add the stub creation to the proof script.
- **C8-4 LOW (carried, open).** route_parity still zips `rows, new` (embedder_arms L275) without checking `len(new) == n`. Add the refusal before the gemma `--go`, or record why it is not needed: the production ollama_embed refuses a count mismatch.
- **Y8-H LOW.** The try/finally restore in `_admit_arm_file` is correct as built, but no test covers it (the mutant that removes it survives). Add one selftest leg in which the admitted open raises (-wal present) and the guard tuple is asserted restored afterwards.
- Carried unchanged: C7-2 B4 witness; M1/M4; C11-5 LOW (unreachable on real data: dup 0 in all 49 files, confirmed again by the STAGE0b outcome).

## PINS (blob LF of record; sha256-lf16 / sha256-crlf16 of the working tree), tip 5a93ecc
- flat_generality.py: 44ca378e00b6d0661cedaf958f0b7489ba8b6bcd, b2adc3f1e58c8d3c / ac268966627772c5.
- k46_key_read.py: c6a6729bb0256d394072ae844120867d2fa5c652, 3e31d4e28640f835 / 99f6c1eff4a8ec08.
- v2_declared_cells.py: f7f30ebea2b2f729743e682cf2fa6cae0f16b0e9, f7103c36bc7ff273 / 16d1aeb1d58410ac.
- cert_redraw_r512.py: 9258bc8f938a135c9d89d98606551bb05d41dd9b, e88199b2ebf14215 / 4dad6a002356f71c.
- embedder_arms.py: 4f56e79d32a97ad04d7e2b1582c3660d471e0c57, c9cb36eaf71e7e03 / 6529bf10827993ee.
- SeparationNullBySizeTest.kt: 22b1c1cfc672e502185341bdbdf3a3011803663e, 8033bdde37a940c1 / 7c66f5bfd281176a.
- sitenull_heapguard_leg.sh: cc461f37f75bf514e91ab9d266e3d4053e4ba703, e6f017f42be98aa4 (the working tree is LF).
- Residual file: blob 7a3b0440ffcbaab76d5cf90f1c617d222691b6f8, sha256-bytes LF b35b3e03..., working-tree CRLF 9d66ec94...

## PART 2: POST-RUN SUPERGPQA-STAGE0b (main, run on 481b613; outcome = run.log byte-for-byte after CR strip, diff empty)
Data object:
- Key DB `experiment_results/supergpqa/supergpqa_stage0b_key.db`: sha256 9898d91a... equals the printed value. 1,238,622 rows = 25,278 uuids x 49 models.
- 0 excluded uuids in the key. 0 side mismatches against the split json.
- Excluded 1,251 = 370 EVAL / 881 TRAIN. Recounted from the exclusion json against the split: EQUAL.
- Script blob 35b11858 is equal at 481b613 and at HEAD, and equals the delta-2 pin. The outcome is untracked (the registrar commits it); outcome sha256-lf16 7e464a61421fe69a, blob 1eaf9d19c1fc83bc67d3528ad527da570228b289.

| # | claim (outcome) | verdict | mine (own code, own RNG) vs claimed | sev |
|---|---|---|---|---|
| S1 | population: 25,278 non-excluded; C1 n 7,396 in 7,395 components; 10 scored | CONFIRMED | 25,278; scored EVAL 7,396; components 7,395 (2 twin families); 10 scored of 13; all EVAL 7,591 | - |
| S2 | policy, best single | CONFIRMED | Best single DeepSeek-R1 (pooled TRAIN argmax). The policy is identical in all 10 disciplines. Equal to best single in 3 (P5 observed 3) | - |
| S3 | C1 G +0.65pp | CONFIRMED | 0.6195 - 0.6130 = **+0.6490pp** | - |
| S4 | two-stage SE 0.00309, 95% [+0.04, +1.25] | CONFIRMED within MC | B 2,000 (TRAIN re-fit within discipline + EVAL components within discipline), default_rng(20260929). **SE 0.00306, [+0.05, +1.25]**. MC SD of the lower end is about 0.01pp, so the lower end stays above 0 | - |
| S5 | C1 HELD | CONFIRMED by the rule of record, FRAGILE | The rule is point +/- 1.96 SE_2stage (script L46-L49, inherited from ROUTER-CLEAN-POLICY L81-L82). The lower end is **0.04pp from the bar**. The percentile interval, printed beside, CONTAINS 0: [-0.05, +1.16]; mine [-0.07, +1.11] | MEDIUM (S-1) |
| S6 | Support measured: SE_iid 0.00280, DEFF 1.218, n_eff 6,074, MDE80 0.86pp | CONFIRMED (descriptive spot) | Analytic SE_iid 0.00286 (theirs is a bootstrap). DEFF 1.145 / n_eff 6,460 on mine, a ratio of MC quantities. MDE80 **0.86pp** | - |
| S7 | C2 R 0.6413; jackknife [0.4382, 0.8444] (SE 0.1036) | CONFIRMED to the digit | Own two-way demeaning, 40 halvings Random(7) over sorted disciplines, LODO re-halved: **0.6413; SE 0.1036; [0.4382, 0.8444]**. Halving SD of r 0.0306. R over 10 other halving seeds 0.6297-0.6468 | - |
| S8 | null p95 (19th of 20) 0.0995 | CONFIRMED to the digit | Own logit-additive fit + simulation, seeds 1..20: **0.0995**, all 20 sorted values equal. Own seeds 1000+: p95 0.1151, max 0.1444. The lower end 0.4382 clears either value by > 0.29 | - |
| S9 | placebo +0.28pp, does not fire | CONFIRMED (point) | Random(42) over the sorted-uuid TRAIN label list: **+0.2839pp**. The interval was not recomputed; it only needs to contain 0 not to fire | - |
| S10 | P7 0.6119 (DeepSeek-R1, 7,591 EVAL) | CONFIRMED | 0.6119 | - |
| S11 | wording | CONFIRMED | The C1/C2/F1 lines match registration L17-L18 (prog L21790ff). The population sentence is printed beside every number, as CHANGES (4) requires. "Recorded as notable" matches verdict line (f). P4 FAILED, P5 FAILED. Rows STRUCK per ruling 20 | - |

POST-RUN VERDICT: **VALID**. C1 HELD (notable; DESCRIPTIVE-ONLY by plan) and C2 HELD, both reproduced. F1 does not fire.
**S-1 MEDIUM (registrar, wording):**
- Record C1 as "HELD by the normal two-stage interval of record, lower end +0.04pp; the percentile interval printed beside contains 0 [-0.05, +1.16]; verdict line DESCRIPTIVE-ONLY".
- Never write "C1 HELD" without that bracket.
- Do not quote +0.65pp as a gain of SuperGPQA as a whole: the population sentence binds.

## COMMANDS (compact)
```
python tools/analysis/{embedder_arms,k46_key_read,v2_declared_cells,flat_generality,cert_redraw_r512}.py --selftest [+ -O] ; embedder_arms/flat_generality --mutants
python rev_delta3/rp05_my.py ; python rev_delta3/harness34.py ; python rev_delta3/mut06.py ; python rev_delta3/rp08_my.py
sh tools/threadcap/sitenull_heapguard_leg.sh (tip 5/5; with 481b613's test file: HEAP-line/HEAP-refused MISSING; restored 5/5) ; sh tools/threadcap/sitenull_noemb_leg.sh (4/4)
sh rev_delta3/run_proof_d3.sh (11/13 no stub; 13/13 with an empty stub) ; ./gradlew test --offline (470 / 2 known)
git merge-tree --write-tree --name-only main w0-delta3 | grep -c CONFLICT   # 0
python rev_delta3/sg_recompute.py ; python rev_delta3/sg_recompute2.py      # S1-S10
```
