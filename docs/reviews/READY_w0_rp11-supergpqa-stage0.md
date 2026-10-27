# READY REVIEW — w0 RP11 SUPERGPQA-STAGE0 at 8c1e54d (adversarial reviewer; zero calls; no real-data statistic)

## VERDICT: NOT READY

The build is faithful to most of the registration, and its own 105 checks and 18 mutants pass. It is still not ready, for four reasons:

- **B1 (BLOCKER).** A run as registered ends at the A4 STOP. That STOP outcome would print the stored correctness counts of every model over the whole corpus, EVAL included, into a write-once file. Those counts are the per-model accuracies the seal exists to keep out.
- **H1 (HIGH).** `mode_run` is never executed by the selftest. All 12 of the reviewer's mutants survive. Some are decisive: X12 decides C1 from the i.i.d. draws, and X4 computes R on TRAIN cells.
- **B2 (BLOCKER for the run).** A registered precondition is unmet: DATASET-SURVEY has not been run.
- **Open ruling.** The A4 STOP has been CONFIRMED to the digit: 1,251 of 26,529 items = 4.7156%, against a bar of at most 2.0%. The registrar and research-lead must rule on whether the stage runs to a STOP or is re-registered, and must also rule on the two missing descriptive readouts (M1).

**Merge status by path:**
- MERGEABLE now: `tools/analysis/supergpqa_fetch.py` (blob:23ce0903…) and `experiment_configs/supergpqa_stage0_split.json` (blob:a443ffbc…). The split re-derives exactly and was committed before any response file was parsed.
- NOT MERGEABLE: `tools/analysis/supergpqa_stage0.py` and `experiment_configs/supergpqa_stage0_whitelist.json`. The whitelist is fixed only at a READY.

**Hygiene of this review:**
- Zero judge or Azure calls. `--run` was not executed and no stored correctness was read.
- No aggregate file was fetched or opened. `find TaxoArena_data \( -iname '*results_*' -o -iname '*.xlsx' \) | grep -ci supergpqa` returns 0, and the SuperGPQA tree holds 53 files: 52 in the manifest plus the manifest itself.
- The text stores were read with `mode=ro&immutable=1` only after checking that the -wal and -journal files were empty. The only JVMs running were idle daemons (Gradle PID 44840, Kotlin PID 49188; CPU time unchanged over 3 s), so no construction was running. The DB mtimes were unchanged afterwards (mmlu_pro_dataset_cache_v2.db 2026-09-19 16:30:10.1069748; multicorpus_cache_v1.db 2026-09-13 11:44:29.6842757).
- All Python ran single-threaded (OMP/MKL/OPENBLAS=1). Scratch files are in `scratchpad/rv11/`.

## Identity (checked against `git hash-object` and the LF / CRLF renderings of `git show 8c1e54d:<path>`)

| path | blob | sha256-lf16 | sha256-crlf16 | claimed |
|---|---|---|---|---|
| tools/analysis/supergpqa_stage0.py | 18856a8feb78511e69637a4c004d8c18a2b1fc6d | 288851ee2d362df4 | 749d343f1a6f375a | = |
| tools/analysis/supergpqa_fetch.py | 23ce090309824604dfffd706dcb06f498dc3b6d6 | 21eed87c13ff6cee | f1d794a455198c72 | = |
| experiment_configs/supergpqa_stage0_split.json | a443ffbc7f61158aacefcfe21c246df93b45ecb9 | 1db5c7c4366b1a0d | 20379ba018cc44a1 | = |
| experiment_configs/supergpqa_stage0_whitelist.json | f86123f80e5a7d1721304b8d16f0d90c1f9125f4 | 14c8acd1c4cae81f | 9cf98b2c0b83bf0b | = |

- **Commit contents.** 8c1e54d has parent 7676eab, and `git merge-base --is-ancestor 7676eab 8c1e54d` succeeds. `git diff --name-status 7676eab 8c1e54d` returns 4 lines, all of status A (proved by counting with `| awk '{print $1}' | sort | uniq -c`). No existing path is touched.
- **Dependencies unchanged.** The blobs on main are identical to those the dry-run printed: split_side 05224b5a, content_closure 1533cb5a, profile_reliability_interaction c9f99c1b.

## Per-claim table

| # | claim | result | command / script | reviewer's number vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Selftest: 105 checks, 0 failed, under `python` and `python -O` | CONFIRMED | `--selftest` and `python -O --selftest` | 105/0 and 105/0 | — |
| 2 | Mutants: 18/18 killed, under both interpreters | CONFIRMED | `--mutants` and `python -O --mutants` | 18/18 and 18/18 | — |
| 3 | Fetch selftest: 11/11 | CONFIRMED | `supergpqa_fetch.py --selftest` | 11/11 | — |
| 4 | Split sg893684444c6df3e9, EVAL 7,961 / TRAIN 18,568, 2 twin families, none straddling, drawn from the question file (sha 28b998e7) | CONFIRMED | `rv11/split.py`: reviewer's own R1 implementation (families by stem_key; fields sorted; one Random(int(sha256(seed))); shuffle; round-half-up 0.30 prefix) | exact eval and train lists; split id equal; straddle 0; twin families 2; sha256-lf16 1db5c7c4366b1a0d | — |
| 5 | A4: 1,251 items (4.7156%) collide; source is MMLU-Pro and the stores containing it; LCB/BFCL/JudgeBench 0 | CONFIRMED | `rv11/a4.py`, an independent store reader (text recomputed with `split_side.stem_key`; v2 stores checked both from stored item.stem_key and from variant.stem text) | 1,251 / 26,529 = 4.7156% to the digit. Per store: mmlu 1,251, union 1,251, v2 split-1 and split-2 mmlu/union 1,251 each (text-recomputed and stored-key hits both 1,251), lcb 0, lcb-eval 0, bfcl 0, jb 0. On EVAL: 370 of the 1,251 (881 on TRAIN) | — |
| 6 | Of the 1,243 `mmlu_pro.question` hits, 1,092 have an identical normalised option set; median stem 203 chars; 369 on EVAL | CONFIRMED | `rv11/a4.py` plus an inline check | 1,243 / 1,092 / 203 / 369 | — |
| 7 | 20NG and ag_news BLOCKED by non-empty WAL files (708,672 B and 206,032 B) | CONFIRMED | `stat` | 708,672 and 206,032. The A4 verdict does not depend on them: the readable-store share of 4.7156% is a LOWER bound, so no content of the blocked stores can bring A4 under 2.0% | — |
| 8 | A6: 10 scored disciplines; 18 of 72 fields reach 120 EVAL items | CONFIRMED | `rv11/split.py` | 10 (Agronomy 145 … Science 2,792 EVAL after exclusion); 18 of 72 fields (19 before exclusion); corpus has 13 / 72 / 285 cells | — |
| 9 | A5: odc-by on both cards | CONFIRMED (front matter) | reviewer's `grep` and `sed` | Both cards read `license: odc-by`. The SuperGPQA card body adds that it is "a composite dataset … portions of data derived from other sources", which agrees with row 5 | — |
| 10 | Fetch: 52 files, both revisions pinned, every file checked against its LFS sha256; aggregates excluded by name | CONFIRMED | reviewer re-hashed all 52 files from disk (bytes only, no parsing) | 52/52 match the manifest; lfs_oid = sha256 on 50 of 50 LFS files (the 2 cards are non-LFS); manifest sha256 2f8cd653b95bb20f; 0 sealed names in the whitelist; largest file 853,814,205 B, under the 900 MB cap | — |
| 11 | Extractor is a verbatim copy of upstream eval.py L32-L105 @ e31e8bf | CONFIRMED independently | reviewer fetched raw eval.py at e31e8bf3 (945 lines) and compared bytes | Block sha256 24d32e05… equals upstream L32-L105 byte for byte; `reextract` matches upstream L131-L135. The builder's selftest only compared the file with its own constant; this check is against upstream | — |
| 12 | "Every registered criterion, prediction and falsifier has a print branch" | PARTLY | reading L1015-L1054 | P1b has two parts, "zero collisions: 0.60" and "(<= 2.0%: 0.90)". Only the first has a print branch | M2 |
| 13 | Registered descriptive readouts (two-roster contrast, BoN floor) | PARTLY / NOT BUILT | L1330-L1331 | They print "NOT READ". The registration declares them | M1 |
| 14 | `--run` wiring as registered | UNDETERMINED by the builder's tests; REFUTED as tested | `rv11/mut.py`: 12 reviewer mutants, plus a control mutant that is killed | 12 of 12 SURVIVE (list below) | H1 |
| 15 | STOP outcome reads no criterion | REFUTED in substance | `rv11/runfix.py stop` executes `mode_run` on a synthetic fixture (22 models, 200 collided items) | The STOP outcome contains one line per model with its `statuses {'correct': …, 'incorrect': …}` over ALL corpus items, EVAL included (L543-L544, L1222-L1224) | B1 |
| 16 | Support arithmetic (registration L21790-L21829, (a)-(g)) | CONFIRMED (plan); re-derived at the real denominator | inline python | d = 0.00491² × 6,482 = 0.156269. SE_iid at 7,959 = 0.0044311; × √1.312 = 0.0050754 (registered 0.005076); × √1.443 = 0.0053228 (registered 0.005323); MDE80 1.42pp. At the post-exclusion scored-EVAL n = 7,396 (key-free count; 7,395 components; measured component Kish 1.00027, the low end of the declared 1.0-1.1): SE 0.005265 at DEFF 1.312, MDE80 1.474pp, n_eff 5,637. The C1 verdict line DESCRIPTIVE-ONLY is unchanged. C2 0.0665 / 1.96 = 0.0339 and MDE 0.095 reproduce | M3 |
| 17 | Dry-run reads no stored correctness and computes no statistic | CONFIRMED | reading L1143-L1192; `scan_model(want_key=False)` counts only which fields are present | Holds (records are json-parsed; status values are never accessed) | — |
| 18 | EVAL id file committed before any response file was opened | CONFIRMED (timestamps) | `ls --full-time` on the logs; commit time | fetch 06:02:18 (sha256 only); split.log 06:07:22; commit 06:08:07; dryrun.log (first parse of any response file) 06:08:46 | — |
| 19 | "Not mostly solved" (DeepSeek-R1 0.6182) | UNDETERMINED | none possible without the key or the sealed aggregate | Not verified, by design. The figure is a plan citation (rev row 19) and has not entered the record. The registered answer is P7 of a run that passes A1-A6 | — |

**Reviewer mutants, all against the builder's selftest.** The harness was validated by a control mutant, A4_BAR 0.02 → 0.021, which was KILLED.

| mutant | effect | selftest |
|---|---|---|
| X1_run_a4_skipped | run never STOPs at A4 | SURVIVED |
| X2_run_excl_not_applied | the 1,251 collided items enter the key matrix | SURVIVED |
| X3_run_a2_sample_on_eval | A2 audit reads EVAL correctness (hygiene) | SURVIVED |
| X4_r_cells_on_train | C2 R computed on TRAIN items (decisive) | SURVIVED |
| X5_placebo_permutes_eval_too | placebo permutes EVAL labels too | SURVIVED |
| X6_p1b_share_not_zero | P1b scored on the 2.0% bar instead of zero | SURVIVED |
| X7_run_blocked_ignored | run proceeds with BLOCKED stores | SURVIVED |
| X8_maxacc_over_all_items | P7 over all items, not EVAL | SURVIVED |
| X9_boot_eval_iid_not_components | EVAL bootstrap draws one component repeatedly | SURVIVED |
| X10_train_resample_unstratified | TRAIN resample ignores discipline strata | SURVIVED |
| X11_a6_floor_121 | A6 floor 121 | SURVIVED |
| X12_c1_interval_iid | C1 decided from the i.i.d. draws, not the two-stage draws (decisive) | SURVIVED |

`rv11/runfix.py pass` shows that `mode_run` does run end to end on a fixture (C1, C2, placebo, dominance, P1-P7, F1; B = 40, well under a minute). A fixture-level test is therefore cheap, and none exists.

## Defects

**B1 (BLOCKER). A STOP outcome leaks per-model accuracy over the whole corpus, EVAL included.**
- **Where.** `scan_model(want_key=True)` reads the stored correctness of every uuid (L538-L547). `mode_run` then prints `statuses` per model (L1222-L1224) before any admission leg is decided, and writes it into the write-once outcome on every STOP (L1262-L1268).
- **Why it matters.** As registered the run is expected to STOP at A4 (row 5), so this is the expected path, and it is irreversible. It writes 49 per-model accuracies over EVAL and TRAIN into the record. This is the content the seal protects ("per-model … accuracies … include EVAL and would leak G and R"), and it would answer P7 outside its gate.
- **Fix.** While the legs are decided, access stored correctness only for (i) the 200-uuid A2 TRAIN sample and (ii) uuids that carry duplicate records (the R3 conflict check; the dry-run found 0 duplicates in all 49 files). Build the full key only after A6 passes. The per-model line prints presence, duplicates and conflicts only. The miss + error share is printed only in the post-A6 block. Add a selftest check that a STOP outcome contains no "correct" count.

**B2 (BLOCKER for the run, not for the build). Registered run preconditions are unmet.**
1. DATASET-SURVEY's SuperGPQA row must ADMIT. `docs/agents/results/DATASET-SURVEY.json` shows state "registered", script "NOT BUILT", and `experiment_results/dataset_survey/` does not exist.
2. The data-steward's A5 confirmation.
3. The data-steward checkpoints the 20NG and ag_news WALs; otherwise `--run` refuses, correctly, as a failed precondition.
4. A rule-7 window: the run opens `mmlu_pro_dataset_cache_v2.db`, which carries the reserved_pool tables, and the script has no W1-W5 probe. The run-operator must announce the window.

**H1 (HIGH). The deciding wiring is untested.**
- **Where.** The selftest never calls `mode_run`, and 12 of 12 reviewer mutants survive. X12 and X4 are decisive for C1 and C2; X2, X3 and X7 are hygiene failures.
- **Fix.** Add a fixture-level `mode_run` test with exact-line assertions on both paths:
  - STOP path: the A4 STOP line, no key counts (B1), and P1b FAILED on both clauses.
  - PASS path: C1 SE equals the SD of the two-stage draws, not the i.i.d. draws; the R cells are EVAL uuids only; excluded uuids are absent from the key DB; the A2 sample is a subset of TRAIN; P7 is taken over EVAL only.
  - A BLOCKED store refuses.
- **Then.** Re-run X1-X12, and they must all be KILLED. `rv11/runfix.py` is a working template.

**Ruling owed (registrar and research-lead, before any READY that certifies a run).**
- **A4 STOP as registered.** Reconciliation (ii) (L21535-L21555, item 21) was "open to a pre-data bracket BEFORE the READY". The count is now known, so a change to the bar or the key is POST-COUNT. It is still PRE-KEY, though: A4 is key-free, and no correctness has been read. The options are:
  - (a) run as registered, after B1 and H1 are fixed, and record the STOP;
  - (b) a new registration (for example SUPERGPQA-STAGE0b) that excludes the 1,251 items without the bar, labelled post-count / pre-key, with the 4.7156% disclosed.
- **Substance for SQ5.** 4.7% of SuperGPQA (1,092 items with identical option sets) are MMLU-Pro copies. The "second corpus" is therefore not content-independent of MMLU-Pro unless those items are excluded.
- **Not the reviewer's call.** This review does not choose between (a) and (b).

**M1 (MEDIUM). Two registered descriptive readouts are not built.**
- The two-roster contrast needs the 26 five-shot files, the fetcher's `--with-five-shot`, and a whitelist amendment.
- The best-of-N floor has no definition.
- **Fix.** A pre-key ruling: define and build both, or strike them by bracket. They may not be silently absent.

**M2 (MEDIUM). P1b's second clause has no print branch.** The clause is "(<= 2.0%: 0.90)". Add it; under the expected STOP it reads FAILED. P1a reads "complete == 49", while the registration says "finds 49"; state this as a reading.

**M3 (MEDIUM). The C2 SE is transported from a different cell structure.**
- The SE 0.0339 comes from PROFILE-RELIABILITY-INTERACTION's K12 half-width.
- Here there are 10 very unequal cells (Science 2,792 vs Education 142 EVAL items). A LODO jackknife over these can be much wider; a 5-cell synthetic fixture gave SE 0.56, which is not evidence about the real data.
- The post-run review must print the measured jackknife SE and MDE beside the decision. SCOREABLE rests on this transport.

**L1 (LOW). The split id is not the first printed line.** Reading R2 and CONTEXT section 6 both say it should be. In the script's dry-run output the SPLIT line is the 6th line (it comes after 4 pin lines and the extractor check; it is line 8 of `dryrun.log`, whose first 2 lines were added by the builder's wrapper). Print it first.

**L2 (LOW). Split provenance rests on re-derivation.** The split was drawn by uncommitted blob 2343d573. The committed blob re-derives it exactly (row 4), so provenance holds by re-derivation only; record this.

**L3 (LOW). The A2 sample can include items that A4 later excludes.** A2 comes before A4 in the registered order. State this as a reading.

**L4 (LOW). A2 can crash on an unmatched extractor result.** In the upstream code, `options.index(predict)` raises ValueError if `extract_option_content` returns a match that is not an option; the port does the same. This fails closed (nothing is written). Catch it and count it as a re-extraction miss, and say so in R4.

## Readings R1-R7, size cap, whitelist

- **R1:** CONFIRMED by independent re-implementation.
- **R2:** ACCEPTED, subject to L1.
- **R3:** ACCEPTED, subject to B1: the conflict check touches correctness only for duplicated uuids.
- **R4:** ACCEPTED (seed string, largest-remainder allocation, verbatim extractor verified against upstream), subject to L3 and L4.
- **R5:** ACCEPTED (sorted disciplines; the re-halved jackknife is the bound of record).
- **R6:** ACCEPTED. The FAMILY map was checked on all 49 names and gives 16 families, including OpenAI 8 and Qwen 10.
- **R7:** ACCEPTED.
- **Size cap 900,000,000 B and the 49-file whitelist:** ACCEPTABLE as proposed, but fixed only at the READY that follows the fixes.

## Merge and run procedure (after B1, H1, M1 and M2 are fixed and the A4 ruling is recorded)

1. The engine-coder fixes B1, H1, M2, L1 and L4 on the branch, then re-runs the selftest and mutants under `python` and `python -O`, plus reviewer mutants X1-X12, which must all be KILLED.
2. A delta READY pins the new blob (LF and CRLF) and fixes the whitelist and size cap.
3. Merge by path: `git add <the 4 paths>` then `git commit -- <paths>`, followed by the ancestry check.
4. Preconditions (B2): the DATASET-SURVEY SuperGPQA row ADMITS; the data-steward confirms A5; the data-steward checkpoints the 20NG and ag_news WALs; the orchestrator announces a rule-7 window.
5. The run-operator runs `--dry-run`: A4 must print all 13 stores readable. Then `--run` single-threaded, then the post-run review re-measures DEFF, n_eff and MDE from the key DB, then the registrar records the outcome.

## Scratch (reviewer's scripts; read-only against data)
`C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/rv11/` — `a4.py`, `split.py`, `mut.py`, `runfix.py`, `eval_upstream.py`, `excl.json`.
