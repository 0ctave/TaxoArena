# READY review — ARCH-V2-INDUCE-RUBRIC-1, the live rubric inducer, at af2a6a8

## DELTA 2026-09-24 (split-2 re-pin) — 4b60b60 (2713f45 merge of main 5b89159, 4b60b60 re-pin). INSERTED; everything below is unchanged

**DELTA VERDICT: READY for `--run`.** Two record items (R1, R2 below) are registrar insertions owed before the launch. They are zero-call and change no code.

- **Instrument:** `tools/analysis/judge_v2/induce_run.py` sha256-lf16 **add7df769d1c7efd** (blob:4c9c0a20…).
- **Payload sha256 to pin:** **`cce432e1353e7c27e913862da0215322c279fe71aca9d9b174d3ab178963c7c4`**.
- **Selection:** sorted-set sha256 99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50.
- Zero calls; `--run` never invoked.
- The SPLIT-2 views were read-only: the directory listing (sizes, mtimes) and the sha256 of both views are identical before and after (`diff` empty ×2), no `-wal` / `-journal`, and `experiment_results/archv2/induce_rubric_1/` does not exist.
- Single process, light: two selftests ×2, one dry-run, one 8-gram scan (< 1 s), two mutants.

### Identity (pin kinds named)

| file | blob | sha256-lf16 | vs claim |
|---|---|---|---|
| induce_run.py | 4c9c0a20 | add7df769d1c7efd | = |
| induce_overlap_audit.py | a5ad80c1 | f469809f14af4347 | = (and = the list's own `audit_blob`) |
| _base.py | 6f25e4ce | 36f386ccc8c45782 | = |
| induction.py | f4d65f59 | ab0db179a8380a5d | byte-identical 634dba5 → 4b60b60 (`git diff --quiet`: no change) |
| accepted_tests_ledger.py | cd308834 | 81b10b4861333274 | `CEILINGS["ARCH-V2-INDUCE-RUBRIC-1"] = 6`: **still 6**; `git diff 5b89159 4b60b60` on the file shows only that line |
| overlap_exclusions_split2.json | 8060308f | 0f42a5719848f753 (file bytes) | its `list_sha256` 68c0b960a4a7bedc… is the in-file content sha, which `OA.load` RECOMPUTES and compares to the pin (not read on trust) |

- View pins: gen c2930c609c67d6c7… and eval e35b7518878205837… = the SPLIT-2 manifest of record (manifest L475, L560) = `sha256sum` of the files. The dry-run's manifest check passes.

### Claims

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | dry-run: sorted-set 99484486…, 35 kept / 5 replaced / last rank 47, payload cce432e1…, 1,095 EVAL references, 8-token overlap 0 of 6,156 | CONFIRMED to the digit | `TAXOARENA_DATA_ROOT=Z:/…/TaxoArena induce_run.py --dry-run` on `git archive 4b60b60` (`ir3_dry.txt`) | Population mmlu-pro-v2 × MC_LETTER; excluded by corpus mc6 acc_norm 4,259 / mc6 MC_LETTER 7,143; candidates 7,441 = distinct 7,441; GATE 1,929; 40 = 40 = 40 = 40; content-key check 40 stems + 392 options, 0 / 0. Payload 29,882 bytes; V2: 25,126 key renderings, 2,704 answer texts, 1,095 references (all renderable) → 1,407 strings |
| 2 | audit list: candidates 7,441, excluded 679, run ≥ 50: 0 | CONFIRMED BY AN INDEPENDENT RECOMPUTE | reviewer's `indep_audit.py`: own queries, own tokenizer (`\w+` casefold), 8-gram SET per EVAL text (stems and every option of all 9,899 eval_view variants = 89,110 texts, as the list), candidates = gen_view mmlu-pro-v2 MC_LETTER variants on TRAIN items | candidates 7,441 = list; excluded **679 = 679, symmetric difference 0** |
| 3 | the 40 inputs are clean against the new EVAL | CONFIRMED independently | same script and a content-key pass (data_v2 KeyCache vs eval_view `item.stem_key`) | 40 TRAIN, 40 distinct; 0 in the exclusion list; **0** sharing an 8-gram with any EVAL stem or option; stems keyed into EVAL 0, item ids 0, option texts 0 (6,153 EVAL items); `overlap.py` on the user turn: 0 EVAL stems with a shared ≥ 8-token run |
| 4 | selftests | CONFIRMED | `python[-O]` on both | E-J 174 / 0 FAIL ×2; inducer **61** / 0 FAIL ×2 |
| 5 | D1 mutants | CONFIRMED by the builder's transcripts, python and -O | `scratchpad/arch_v2_ej/mut_d1_python{,O}_16.txt`: 8/8 KILLED each (list ignored; skip removed; threshold 7; threshold 9; list sha not checked; list eval sha not checked; eval_view opened pre-call; dropped rather than replaced) | 8/8 |

### Deviations ruled

1. **A merge of main instead of a fast-forward: ACCEPTED.**
   - `git diff --name-only 634dba5 2713f45 -- tools/analysis/judge_v2 tools/analysis/accepted_tests_ledger.py tools/analysis/data_v2` lists only data_v2 files (main's CK-CLOSE-v2 code). **The merge changed no judge_v2 file and not the ledger.** Every judge_v2 change is in 4b60b60 and was reviewed here.
   - Main has not moved on these paths since 5b89159 (`git diff --name-only 5b89159 main -- …` empty).
   - The merge into main must still be **by path** (the 11 judge_v2 / ledger / audit-list paths), never the branch.
2. **`_base.py` pins views.py 7a0f0ab3 and common.py 462ffef3: ACCEPTED; the openers are unchanged.**
   - `git diff fe75c7c8 7a0f0ab3` (views) touches only `build_view`: CK-CLOSE-v2 U-excluded items are left out of both views and counted, and an unsided non-U item is still refused. `_open`, `open_generation`, `open_eval` and `assert_not_eval` are untouched.
   - `git diff 1e140335 462ffef3` (common) adds the blob-pinned `passage_closure` loader (003d5d4e…). KeyCache and stem keying are unchanged.
3. **Selftest changes from the new fixture: NONE WEAKENS A TEST.**
   - **(a) S5 goldens re-derived, the old values kept in a bracket: HONEST.**
     - Reviewer's `golden.py`, independently: the pre-ruling `select_inputs` (induction.py blob ae17ba25, loaded as a separate module) on the NEW fixture gives ordered 47ea219bab083540 / sorted 447c6b211682c830 = the new GOLDEN_INDUCE_V1.
     - The current induction.py gives 25a97ec2477e04ff / cb524315558a27d8 = the new GOLDEN_INDUCE.
     - Note: on the new fixture the pre-ruling rule yields 40 distinct ids, so the golden pair no longer shows the duplicate defect. The finding-1 unit tests on their own scratch shape (identical-duplicate collapse, differing-duplicate refusal, one variant per component) still carry that discrimination.
   - **(b) The BBH lookup now requires a variant answered by both models: CORRECT.** Otherwise an earlier refusal ("not judgeable") would fire and the BBH refusal would be exercised by the wrong check. The source-leg and backstop-leg witnesses stand.
   - **(c) The D1 assertion re-scoped, plus the brute-force completeness check: STRONGER overall.**
     - The old `ex_ids == with8` became `(ex_ids & extra) == with8`, with the `with7`-not-excluded clause kept (threshold-7 discrimination intact: D1b KILLED).
     - The new O(n·m) longest-common-substring brute force, independent of the 8-gram index, requires `{brute ≥ 8} == ex_ids` and exact run equality over EVERY candidate.
     - Reviewer's mutants: M2 (a spurious exclusion of a run-0 candidate) → KILLED by the re-scoped check. M3 (every excluded run reported as 8) → KILLED **only by the brute-force check**, so the new check adds discrimination the old one lacked.

### Record items owed before `--run` (registrar; zero calls)

- **R1.** The re-pin to SPLIT-2 supersedes the D1 ruling's selection of record (sorted-set 2dfd2d78…, SPLIT-1) and the list pin a4f6e2b7…. Record, as forced by the author's redraw and not a re-selection (seed, sort key, population, dedup, component rule, n and threshold unchanged):
  - the selection of record 99484486d75774b3…;
  - the payload cce432e1…;
  - the list `overlap_exclusions_split2.json` (list_sha256 68c0b960…; file blob 8060308f / sha256-lf16 0f42a5719848f753);
  - the new counts (candidates 7,441; excluded 679; ≥ 50: 0; 35 kept / 5 replaced / last rank 47; 8-token overlap 0 of 6,156).

  The D1 disclosure line becomes "5 inputs … excluded and replaced".
- **R2.** The induction.py replacement pin of L15969 (last set at d49af83f… for 23e56e7) moves to **blob:f4d65f59 / sha256-lf16:ab0db179a8380a5d**: the D1 amendment (fb36233), byte-identical through 4b60b60.
- **Carried:** the COST bracket (D2 of abd4255) is in place (L16057: ≤ 6 invocations); the ledger ceiling is 6 (row above).

### Commands (scratch, not committed)

- **Build:** `git archive 4b60b60 tools/analysis <kt> experiment_configs/reserved_pool_frozen_p2dca.json data_v2/manifests experiment_results/archv2/induce_rubric_1_audit` into `ir3/`.
- **Dry-run:** `induce_run.py --dry-run`.
- **Scans:** `indep_audit.py <list> <ids>`, an inline content-key pass, `overlap.py`.
- **Goldens and selftests:** `golden.py` with the ae17ba25 blob; both selftests under python and -O.
- **Mutants:** `mutir.py ir3 muts_split2.json` (M2, M3).

---

## DELTA 2026-09-24 — 23e56e7 (fc8cfac, 23e56e7 on af2a6a8). INSERTED; the af2a6a8 review below is unchanged

**DELTA VERDICT: READY-WITH-CONDITIONS for `--run`.**

- **Instrument:** `tools/analysis/judge_v2/induce_run.py` sha256-lf16 **907f3a1db7959548** (blob:cf7770c8…).
- **Payload sha256 to pin:** **`c0443981d0bbbfc3a6750077b22f6e1c8c90738a0e777a1754d7f895bb3c7655`**.
- **Selection of record:** sorted-set sha256 16c0733b303cbae18e2a28ddbb265a05fd19b6d38f7f3baff081530ec32ccef2.
- C1–C5 of 6b65efe and the C4 narrowing ruling (d49ab22, L16043-L16051) are implemented, and each is witnessed by execution.
- Two conditions stand before `--run`. Both are zero-call rulings or brackets, and neither changes code unless the ruling asks for it:
  - **D1 (HIGH, new):** one of the 40 inputs shares a 215-token passage with an EVAL item (below). The judge-design-specialist must rule on it before `--run`.
  - **D2 (record):** the ceiling of 6 needs a registrar bracket on the registration's COST line.
- Zero calls; `--run` never invoked.
- Both views were read-only: sha256 and mtime identical before and after (`diff` empty both), no `-wal` / `-journal`, and `experiment_results/archv2/induce_rubric_1/` does not exist.

### Identity

- `git diff --stat af2a6a8 23e56e7` shows 6 files: accepted_tests_ledger, induce_cache, induce_run, induce_run_selftest, induction, selftest. Pins:

  | file | blob | sha256-lf16 | vs the builder's claim |
  |---|---|---|---|
  | induce_run.py | cf7770c8 | 907f3a1db7959548 | = claim |
  | induction.py | 0de6153f | d49af83f2d3ff633 | = claim; **this is the replacement pin for L15969** |
  | accepted_tests_ledger.py | cd308834 | 81b10b4861333274 | = claim; L28 reads `CEILINGS["ARCH-V2-INDUCE-RUBRIC-1"] = 6` |
  | induce_cache.py | a143c286 | 5e2aaa8937e31cd1 | — |
  | induce_run_selftest.py | 41c0d44c | 642c4ea39af80e2f | — |

### Claims

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | selftests E-J 174, inducer 53, python and -O | CONFIRMED | `git archive 23e56e7` → both selftests under both interpreters; rc 0 ×4 | 174/0 FAIL ×2, 53/0 FAIL ×2 |
| 2 | dry-run: population mmlu-pro-v2 / MC_LETTER, 40 = 40 = 40 = 40, sorted-set 16c0733b…, payload c0443981…, 1,073 EVAL references in V2 | CONFIRMED to the digit | `TAXOARENA_DATA_ROOT=<checkout> induce_run.py --dry-run` (`ir2_dry.txt`) | Excluded: mc6 acc_norm 4,233, mc6 MC_LETTER 7,098. Candidate rows 7,927 = distinct 7,927 (0 collapsed, 0 skipped); GATE refused 2,017. Content-key check: 40 stems + 375 options, EVAL hits 0. Sorted-set 16c0733b303cbae1…; payload 30,586 bytes, c0443981d0bbbfc3…. V2: 26,728 key renderings, 2,893 answer texts, 1,073 reference rows (all renderable) → 1,426 reference strings |
| 3 | 8-token overlap now 62 of 6,426 | CONFIRMED; **one of the 62 is not boilerplate** (D1) | `indscan.py` / `overlap.py` (eval_view_REG `immutable=1`, own tokenizer). By content key: stems keyed into EVAL **0**, item ids **0**, option texts **0**; 40 × MC_LETTER; harness options 0. Longest shared run per EVAL stem: 52 stems in the 8-9 band, 9 in 10-14 (clinical and history boilerplate: "…shows no abnormalities which of the following is the most likely…", "this question refers to the following information…"), and **1 at 215 tokens of a 236-token EVAL stem** | 62 = 62 |
| 4 | C1 write-ahead: PENDING rows, pre-post triggers, orphans counted as transport, holder read in the `finally`, ledger = invocations | CONFIRMED | Code: `_write_ahead` commits the invocation row BEFORE `posted["n"] += 1` and the call. The triggers sit on `invocation` (after-valid, attempt cap 3, transport cap 3, no orphan, in order). `run` refuses unless `atl.ledger_calls(TEST) == n_invocations`, and the shared guard's (i) now REFUSES. Reviewer's probes (`probe_ir.py`): **L1** (3 on the ledger, fresh cache) → REFUSED "(0 calls posted): the day ledgers hold 3 … the cache records 0". **L2** (post then crash, 4 launches) → 3 posts, ledger rows [1, 1, 1] (every post ledgered), 0 attempts, 3 transport rows marked ORPHAN, and the 4th launch **posts nothing** and writes the outcome (UNDETERMINED BY INSTRUMENT). Builder's IR1 / IR4 / IR5 die with "the attempt cache REFUSES invocation k BEFORE any post" (`mut_c_python_23e56e7.txt`) | bounded at 3 + 3; posts = ledger |
| 5 | mutants 13 of 14 killed; C1e survives (equivalent); IR11r survives (redundant) | CONFIRMED by the builder's transcripts, ruled below | `mut_c_python_23e56e7.txt` / `mut_c_pythonO_23e56e7.txt`; `mut_regress_23e56e7.txt` (the F1, IR, F2, F3 series killed; IR10r now dies on its own check, not a KeyError, i.e. C3 applied) | — |

### Rulings asked for

- **The ceiling of 6 against the registration's "at most 3 calls": CONSISTENT IN SUBSTANCE; A REGISTRAR BRACKET IS REQUIRED before `--run` (D2).**
  - The finding-2 ruling (L15996-L16007) made transport errors a separate class with its own limit of 3, counted on the posting-day ledger. The registered "at most 3" survives as the cap on attempts (invocations with a reply).
  - The worst case is therefore 6 logical invocations: 3 attempts plus 3 transport errors or orphans. Transport errors return no model reply and cannot steer the artefact.
  - The registration's COST line still reads "At most 3 calls (1 expected)". Bracket it by insertion: "≤ 3 attempts + ≤ 3 transport errors (incl. orphans) = ≤ 6 invocations on the day ledger; the ledger ceiling is 6".
  - The bill is immaterial against the 14,000 posting-day cap.
- **C1e (the shared guard's (i) filtered): EQUIVALENT, accepted.**
  - Under the ledger equality, own = n_invocations = attempts + transport + orphans, and planned = 3 − attempts.
  - (i) breaches only if own + planned > 6, i.e. transport + orphans > 3, which `_launch_state` refuses first (`n_transport >= 3`, `n_transport + orphans > 3`). So (i) cannot bind.
  - It stays as defence in depth. The mutant that matters, C1d (ledger equality off), is KILLED.
- **IR11r (the attempt-after-valid trigger removed): EQUIVALENT, accepted.**
  - An attempt must resolve an unresolved invocation (`attempt_resolves`), only one invocation can be unresolved at a time (`invocation_no_orphan`), and no invocation can be created after a valid reply (`invocation_after_valid`, killed as C1f).
  - So after a valid reply no insertable attempt exists, and the old trigger is unreachable.

### D1 HIGH (new; a zero-call ruling needed before `--run`): an EVAL near-duplicate passage in the induction prompt

- Input `v:f9db3640718d1945…` (component `c:0ebd23d700b2af52…`, TRAIN) is an MMLU-Pro history item quoting Ibn Battuta's *Voyages* ("the Chinese are all infidels, they worship images…"). Its question is about Mongol administration of Russia.
- EVAL variant `v:7b2116683f1c17416c…` (component `c:55deec036bd5629b…`) quotes the same passage. Its question is "Which of the following conclusions about the period 600 C.E.–1450 C.E. is most directly supported by the passage?"
- **215 consecutive tokens of that EVAL stem's 236 (91%) appear verbatim in the user turn.**
- The two stem_keys differ, so CK-CLOSE-v1 placed them in different components on opposite sides. Every content-key check passes, correctly by its definition.
- gen_view carries 4 variants with the passage and eval_view 2.
- This is a passage FAMILY split across TRAIN and EVAL: a split-level property of the content key, not an inducer bug.
- For the inducer it means the rubric induction sees 91% of an EVAL question's text (not its question sentence or its options). Rule 1 says induction never sees EVAL questions.
- The V1 audit already refuses a rubric that copies any 8-token run of an input, so the artefact cannot carry the passage. The harm is to the letter of rule 1, not a channel into the artefact.
- **Asked of the judge-design-specialist:** accept it with disclosure; or exclude, as a pre-call correction with the seed kept, every input sharing an N-token run with any EVAL stem (the reviewer suggests N = 50: it catches this one and none of the boilerplate, whose longest run is 14); and record which.
- **Queued for the data-steward, beyond this test:** count passage families across TRAIN / GATE / EVAL on the split of record. The same property touches construction and the judged pool, not only induction.

### Remaining record items

- Disclose C5 as implemented (the dry-run's eval_view open) — the builder's C5a mutant is KILLED, so the line is in the outcome.
- The pilot's READY pins this run's artefact_sha256 / rubric_sha256 as the ruling requires. The registration's population amendment and the disclosure lines are in the outcome (C4 and finding-1 text, witnessed by C5a and the selftest).

### Commands (scratch, not committed)

- **Build:** `git archive 23e56e7 …` into `ir2/`.
- **Selftests:** `induce_run_selftest.py` / `selftest.py`, under python and -O.
- **Dry-run:** `induce_run.py --dry-run` with `TAXOARENA_DATA_ROOT=Z:/…/TaxoArena`.
- **Scans and probes:** `indscan.py`, `overlap.py` (longest shared run per EVAL stem), `probe_ir.py`. The passage pair was identified by an inline script (gen_view and eval_view, `immutable=1`).
- **Builder's transcripts:** `scratchpad/arch_v2_ej/mut_{c,regress}_*23e56e7.txt`.

---

Adversarial reviewer, 2026-09-24. **Zero calls.** Selftests, mutants, probes and the dry-run only. `--run` was never invoked.
- Everything ran on `git archive af2a6a8`.
- The two view files of record were read `mode=ro` / `immutable=1` through the instrument's own openers, plus one independent scan.
- Their sha256 and mtime are identical before and after (`diff` of both listings: empty). No `-wal` or `-journal` exists.
- `experiment_results/archv2/induce_rubric_1/` does not exist, so nothing was written.
- Single process throughout.

## VERDICT: NOT READY. The instrument becomes READY once C1–C3 are fixed and witnessed, and C4 is ruled.

- **Pin for the run: payload sha256 `3c0a0b08b796f7a9a502d344e4712388599f6207cd9472d88e7b4525714fd7b3`.**
  - Reproduced by the reviewer's dry-run and again by an independent build (below).
  - None of the fixes asked for below touches the selection, the prompt or the body, so this sha stays the one to pin.
- **Reviewed instrument:** `tools/analysis/judge_v2/induce_run.py`, blob:4c83a906f35eaf45900e190f4122bb1db10ea092 / **sha256-lf16:64152b0bd9a0a4f6**. The working tree is not used.
  - The C1–C2 fixes change this file. The delta READY must name the new sha256-lf16; the one above certifies only the reviewed state.
- **Amended `induction.py` (for the registrar's replacement pin):** blob:e2c2157b4fa03357d48c19b3aa494890ebe501f0 / sha256-lf16:85971d068e71841c. **CONFIRMED.** The pin it replaces is ae17ba25…, the merge base's blob.

The happy path is sound:
- one post of the pinned body;
- the first valid reply is of record;
- no edit path;
- V2 after the reply, with the order witnessed;
- the artefact write-once.

The failure paths are not:
- the call ceiling is enforced only from a cache that can lose or miss a posted call;
- the one independent witness, the day ledger, is read and then ignored (C1);
- a registered V2 leg is missing (C2).

## Identity

- Branch `archv2-induce-rubric-1`, HEAD af2a6a8 (403f897, 624c420, af2a6a8).
- `git diff --stat $(git merge-base main af2a6a8) af2a6a8` lists exactly the 7 files named:
  - `accepted_tests_ledger.py`: +1, the ceiling line only;
  - `lint_opens.py`: +2, the selftest allowlist;
  - `induce_cache.py`, `induce_run.py`, `induce_run_selftest.py`: new;
  - `induction.py`, `selftest.py`.
- View shas (sha256 of the bytes):
  - gen_view_REG 690d06b8fc108ccf… = the registered one;
  - eval_view_REG 7c284b15c45aa381… = the manifest of record's.
- Prompt pins printed by the dry-run and equal to the registration: INDUCTION_SYSTEM 4c4bf36f…23e7 (429 chars) and USER_TEMPLATE 7ed21eba…f7481 (139 chars).

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | E-J selftest 174/174, python and -O | CONFIRMED | `python[-O] tools/analysis/judge_v2/selftest.py` on the archive; rc 0 both | 174 / 0 FAIL, both | — |
| 2 | inducer selftest 41/41, python and -O | CONFIRMED | `python[-O] tools/analysis/judge_v2/induce_run_selftest.py`; rc 0 both | 41 / 0 FAIL, both | — |
| 3 | real-data dry-run: sorted-set sha 32e9c7ca…, payload 3c0a0b08b796f7a9…, witness 19,258 / 12,160 / 7,098 / 0, 40 = 40 = 40 = 40 | CONFIRMED to the digit | `TAXOARENA_DATA_ROOT=<checkout> python tools/analysis/judge_v2/induce_run.py --dry-run` (1.6 s); scratch `ir_dry.txt` | sorted 32e9c7ca0fe3e14c0b72853de032eeae5620f24137c2eca9f0185ee88f721c69, ordered 2201942633620f0d…, payload 3c0a0b08b796f7a9a502d344e4712388599f6207cd9472d88e7b4525714fd7b3 (28,028 bytes), candidate rows 19,258, distinct 12,160, collapsed 7,098, skipped 0, 40 inputs = variants = items = components | — |
| 4 | the payload carries no EVAL content | CONFIRMED by content key; see C4 for the population | independent scan `indscan.py`: eval_view_REG `item` read `immutable=1`, keyed with data_v2's own KeyCache, not the gen_view salted set | 6,419 EVAL items / 6,419 stem_keys. Input stems keyed into EVAL: **0**; input item ids in EVAL: **0**; option texts keyed into EVAL stems: **0**. Harness-shaped options ('arg_0'): 0. Also: **505 of 6,426** EVAL variant stems share an 8-token run with the user turn. All samples are BBH / MuSR task TEMPLATES ("In the following sentences, explain the antecedent of the pronoun…", "Today, X went to … Between what times…"): boilerplate shared by TRAIN and EVAL items of the same task, not an EVAL item | 0 item-level hits | see C4 |
| 5 | 12 ruling mutants killed; IR10r only by a KeyError | CONFIRMED, and the weak kill is FIXED in scratch (C3) | reviewer's `mutir.py`: IR10r (the backstop off) → `KeyError: 'candidate_rows'`. The selftest's stand-in `select_inputs` never fills the witness, so `select()` crashes before the backstop is reached, and the check's `ck.refused` never sees a refusal | killed by a crash, not by the backstop | LOW |
| 6 | fixture golden re-pin honest (the old value reproduces under the old rule) | CONFIRMED independently | `golden.py`: the merge base's induction.py (blob ae17ba25, loaded as a separate module) on today's fixture gives ordered 16d06e309050ff6a / sorted 0318506ec494cb2f = GOLDEN_INDUCE_V1 (40 ids, only **39 distinct**, the defect). af2a6a8's gives 28634d528df4f79e / 8631576c0d68e2c5 = GOLDEN_INDUCE (40 distinct) | both equal | — |
| 7 | no best-of-n, no edit, no retry on a valid reply, no 4th attempt | CONFIRMED in code; **PARTLY in effect** | The loop is `range(n_attempts+1, 4)` with `break` on the first valid reply; `classify` does `json.loads` on the verbatim reply. BUT the builder's own IR1 (best-of-n), IR4 (retry on a valid reply) and IR5 (a 4th attempt) die by `sqlite3.IntegrityError` from the cache trigger, raised on the INSERT **after** the extra `call_full` has returned. In a live run each of those mutants would have posted a real extra call. The triggers record after the fact; they prevent nothing | the backstop is post-call | HIGH (C1) |
| 8 | no 4th transport launch | CONFIRMED | `_launch_state` refuses at `n_transport >= 3` before any post; selftest F: a 4th launch is refused "reached its outcome" | — | — |
| 9 | the V2 check never causes a re-post; eval_view never opened before the reply is written | CONFIRMED for the run; LOW note on the dry-run | In `run`, eval_view is opened only inside `finish()`, after `attempts()` returned and the reply row and its `reply_committed` event are committed. The flag `_EVAL_OPENED` refuses any later `call_full` (F3a, F3b killed). No code path loops back from `finish`. **Note:** `--dry-run` opens eval_view before any reply exists (a separate process, zero calls, counts printed only: 5,164 pairs → 26,728 renderings, 2,893 texts). Ruling 3 (i) binds the run's process, so this is acceptable as a pre-flight, but the outcome should disclose it | — | LOW (C5) |
| 10 | the day-ledger append is in a `finally`, including on a stop | **PARTLY** | It is in `run`'s `finally` and fires on a transport stop (selftest E) and on a refusal inside `finish`. BUT the count it appends is the RETURN value of `attempts()`. If anything raises between the post and the return, `posts` stays 0 and nothing is appended. **Probe L2** (`probe_ir.py`): a poster whose return makes the bookkeeping raise AFTER the post, launched 4 times → **4 invocations posted, 0 attempts in the cache, 0 rows on the day ledger**, and each relaunch is admitted as "relaunch". Real triggers of that window: a kill or Ctrl-C (KeyboardInterrupt is not an Exception), a disk error on the cache insert, a malformed provider return | unbounded posts, unledgered | HIGH (C1) |
| 11 | ledger check (i) read per kind (≤ 3 each) while (ii) and (iii) still refuse | **NOT ACCEPTED as built** (ruling below) | **Probe L1:** the day ledger already holds 3 calls for the test, and the launch is fresh (new out dir, i.e. a lost or moved cache). The guard computes the (i) breach, the runner discards it, and the launch **posts** (ledger for the test becomes [3, 1]) | the independent witness ignored | HIGH (C1) |
| 12 | V2 = gt + answer text + other-variant references (the registration) | **PARTLY: a registered leg is missing** | `eval_material` builds `gt_raw` / `answer_text` renderings, answer texts ≥ 12 characters, the marker rules and the reference MARKER. It includes no reference row. eval_view_REG holds **1,073** EVAL reference rows (v0 1,014, v1 59; `SELECT vintage, COUNT(*) FROM reference`, immutable). A wrong reference's option text is in no V2 material. The docstring describes V2 without the leg and does not flag the substitution (C-7) | leg absent | MEDIUM (C2) |

## Rulings asked for

1. **The per-kind reading of the shared guard's (i): the READING is right, the IMPLEMENTATION is not.**
   - The ruling on finding 2 gives attempts and transport errors separate limits of 3, so a single ceiling of 3 over their sum is the wrong statement.
   - But the runner replaces (i) with nothing ledger-based. It enforces the per-kind limits only from `attempts.db`, and a deleted, moved or never-written cache row resets them (L1, L2).
   - Required (C1):
     - (a) Write the ledger ceiling as it is ruled, 6 (3 attempts + 3 transport errors), with the comment naming the ruling. Keep the shared guard's (i) REFUSING, not filtered out.
     - (b) Add a per-launch equality: the day ledger's count for this test must equal the invocations recorded in the cache. On a fresh launch that count must be 0. Refuse otherwise.
2. **The V2 order witness and the stage label:** as ruled (finding 3). Confirmed above, with C5 as a disclosure.

## Conditions

- **C1 HIGH — write-ahead invocation record, ledger that cannot miss a post.**
  - Before each `call_full`, insert an `invocation` row (seq, payload sha, "PENDING") and commit it.
  - Move the triggers onto that row, so a 4th attempt, a call after a valid reply and a 4th transport error ABORT **before** the post, not on the reply's insert.
  - The reply's row, or the transport row, then references it. A PENDING row found on relaunch counts as a transport error ("no reply recorded"): it consumes the transport limit, is disclosed, and never lets the body post unrecorded.
  - Count posts in a holder the `finally` reads, so the day ledger gets every post even when `attempts()` raises (KeyboardInterrupt included).
  - Implement ruling 1 (a) and (b) above.
  - Witnesses:
    - IR1, IR4 and IR5 die with **0 extra stub calls**;
    - probe L1 refuses with 0 posts;
    - probe L2's second launch refuses or counts the orphan, and the ledger shows every post.
- **C2 MEDIUM — the registered V2 leg.**
  - Add the EVAL reference rows to V2's material: each row's rendered block in its solver's ordering, and its option text ≥ 12 characters, as in loader.py.
  - Or have the registrar record the leg's removal before the run.
  - The docstring must describe what V2 checks.
- **C3 LOW — the IR10r weak kill: FIXED AND VERIFIED in scratch (not committed to the branch, which is the builder's). The builder applies it.**
  - The patch (`scratchpad/ir10r_fix.patch`, 6+/1−) replaces the stand-in `select_inputs` in `induce_run_selftest.py` (block "the backstop: a selection repeating a variant…") with `_dup_sel`. `_dup_sel` first calls the real selection on the same connection, so the witness is filled exactly as in production, and then returns the doubled list.
  - Verified:
    - unmutated selftest 41/41 under python and -O;
    - IR10r now dies with `FAIL a selection with repeated variants refuses the run before any post`, i.e. by the check's own assertion, not a crash.
- **C4 MEDIUM (ruling needed, zero cost, before `--run`) — the population of "MCQ".**
  - The 40 inputs are 27 MC_LETTER and 13 `IMPORTED:acc_norm`.
  - By gen_view `source_row`: MMLU_PRO 26, **BBH 10**, GPQA 2, MUSR 1, MATH 1.
  - This follows the record: E-J choice 3 maps acc_norm to mcq, and the registration says "corpus type MCQ".
  - But the rubric fills the slot of an MMLU-Pro-only pilot (the finding-1 ruling's pool note), and BBH is refused from the judged path (EJ-BBH-REFUSE).
  - The judge-design-specialist must confirm the population as selected, or narrow it as another pre-call correction with the seed kept. Either way the registrar records it.
  - The 505 template overlaps (row 4) are disclosed, not refused: they are TRAIN boilerplate identical to EVAL boilerplate, and V1's 8-shingle audit already refuses a rubric that copies them.
- **C5 LOW — disclosure.** The outcome states that the dry-run process opened eval_view, before any call, to size V2's material (counts only), and that ruling 3 (i) binds the run's process.

## Checks that pass without checking (the brief's item 6)

- IR1 / IR4 / IR5 are "killed" by a cache trigger AFTER the extra post (row 7). IR10r is killed by a KeyError (row 5).
- The inducer selftest's F1 mutants (F1b–F1d) survive it and die only in E-J's selftest, as the builder states. Both selftests are required for any future READY.
- `order[0] < order[1]` compares ISO strings from one clock format. It holds for this code (both come from `_now()`), and the selftest's frozen-clock case exercises the refusal.

## Commands (scratch, not committed)

- **Build:** `git archive af2a6a8 tools/analysis <kt> experiment_configs/reserved_pool_frozen_p2dca.json data_v2/manifests` into `ir/`.
- **Selftests:** `induce_run_selftest.py` and `selftest.py`, under python and -O.
- **Dry-run:** `induce_run.py --dry-run` with `TAXOARENA_DATA_ROOT=<checkout>`.
- **Scans, mutants and probes:** `indscan.py`, `golden.py`, `mutir.py` with `muts_ir10.json`, `probe_ir.py` (L1, L2).
- **IR10r fix:** `irfix/` with `ir10r_fix.patch`.
- **Builder's transcripts:** `scratchpad/arch_v2_ej/mut_ir_regress_af2a6a8.txt`, `mut_ind3_induce_python.txt`.
