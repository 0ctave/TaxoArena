# READY review — ARCH-V2-E-J (the v2 judge layer) at c7525db

## DELTA 3 2026-09-24 — a1826cd (on 2c43ead = main c640e17's judge_v2). INSERTED; everything below is unchanged

**DELTA-3 VERDICT: MERGEABLE by path (`tools/analysis/judge_v2/` only). The judged path is READY: E1 (HIGH) and E2 of d429c4b are closed, and each is witnessed by execution.**

- The LOW record items still stand; none blocks G24:
  - E3: the provenance token is integrity only; `loader._sign` is reachable (P3b) and the lint misses dynamic access;
  - E4: the registrar never records a "DEV-" material-NONE run;
  - the E-D `schedule` column for the ordering key, before the first board.
- Zero calls. Everything ran on `git archive a1826cd` in temporary directories, single process, with no DB query.

### Identity

- `git diff --name-status 2c43ead a1826cd` shows 3 files, all M. Blobs and sha256-lf16 equal the coordinator's table:
  - loader: blob da4fcbbf… / lf16 98f0142efd76346d
  - writer: blob 6db4ab32… / lf16 7bdb6fe536da71d3
  - selftest: blob 7fd34bff… / lf16 fa5856d08bf84a07
- `git diff --name-only 2c43ead c640e17 -- tools/analysis/judge_v2` = 0 lines: main's merged judge_v2 is 2c43ead's.
- data_v2 and the shared modules show 0 lines of diff between a1826cd and main.

### Claims

| # | claim | result | evidence |
|---|---|---|---|
| 1 | selftest 169/169 under python and -O | CONFIRMED | rc 0 both; 169 PASS, 0 FAIL each. `lint_opens` still reports 0 findings on the checkout |
| 2 | EXCLUSION_CODES holds only the ruling's two codes; choose_reference has no try/except; every refusal refuses the whole load | CONFIRMED | `EXCLUSION_CODES = ("excluded_MIXED_referenced", "excluded_ordering_differs_from_solver")`. `grep -n "except SystemExit\|try:"` on loader.py matches one line, L262, the connection's try/finally. `choose_reference` is called bare. `exclude(` has ONE call site (L387), with the two literal codes |
| 3 | expected_exclusions must match exactly; 0 loaded refuses | CONFIRMED | selftest L110-L114 cover all five cases: an unexpected exclusion; the wrong class; an expected exclusion that does not happen; a class outside EXCLUSION_CODES; 0 loaded even when expected. Each refuses the whole load |
| 4 | create and open refuse an empty Loaded | CONFIRMED | `_check_loaded` refuses "the Loaded carries 0 matches" (selftest L133). `open` runs `_check_loaded` too |
| 5 | E1a-E1f, E2a, E2b killed; E1g survives as equivalent | CONFIRMED | builder's `mut_e_python_a1826cd.txt` and `mut_e_pythonO_a1826cd.txt`: 8 KILLED and E1g SURVIVED in both. **E1g is EQUIVALENT:** its guard inside `exclude()` is unreachable, because the only call site passes one of the two literal codes. `mut_d_regress_a1826cd.txt`: every applied D mutant is still KILLED; N5b and N22b were not applied, since their anchors are gone |
| 6 | probe3 P1/P2 and probe4 refuse; P3b gets through (E3) | CONFIRMED | Reviewer's `probe3.py` on ej4: P1 item mismatch → REFUSED; P1 ">1 row" → REFUSED "more than one is REFUSED, never tie-broken"; P2 broken solver join → REFUSED "the SOLVER's ordering … is unknown". P3a (public sign) and P3c (material NONE "anything") → REFUSED. P3b (private `_sign`) → NOT REFUSED (2 slots): the recorded E3 limit. P4: run_meta UPDATE and REPLACE both refused. `probe4.py`: the load itself now refuses on the broken join, so no empty run is reached; the writer's own empty-Loaded refusal is witnessed by selftest L133 |
| 7 | E2: BBH source case-insensitive; mixed_strata checks schema_id | CONFIRMED | `refused_source()` uses `.strip().upper()`, and E2a (case-sensitive) is KILLED. mixed_strata checks for the run_meta table and schema_id before reading, and E2b is KILLED |

### Ruling

- E1 is closed as specified:
  - per-match exclusion happens only by reason code, for the ruling's two ordering classes;
  - every other defect refuses the whole load;
  - the scheduler's expected exclusions must equal the realised ones, ids and classes;
  - neither the loader nor the writer can produce an empty run.
- The builder's choice (b) of d429c4b is withdrawn in code.
- Choice (a) remains, as ACCEPTED: it is one of the two codes, and it must now be expected by the scheduler.

### Disclosure

- The ED3 count query from the first delta (reviewer's, `mode=ro&immutable=1`) has ENDED: no Python process remains, and the task reports exit 0.
- It printed only the five figures already reported; the last two joins produced no output.
- Afterwards the file showed the same sha256 prefix (3cb04769f36eeae6) and the same mtime (2026-09-24 09:55:28.878842400).
- No DB was opened for this delta.

---

## DELTA 2 2026-09-24 — 2c43ead (branch worktree-agent-a549c1b2890aa2a8a; 312bdfb, 612cdae, 2c43ead on 8ef0b75). INSERTED; everything below is unchanged

**DELTA-2 VERDICT: MERGEABLE by path (`tools/analysis/judge_v2/` only). READY-WITH-CONDITIONS for the judged path: E1 (HIGH) must be closed, with an execution witness, before G24 or any judged call; E2–E4 are LOW / record items.**

- D1–D6 of 16212c4 and the D5 MIXED ruling (7bf7256, programme L15732-L15739) are implemented, and each is witnessed by execution.
- One of the builder's two choices beyond the ruling breaks fail-closed behaviour:
  - (b) is **NOT ACCEPTED as built**.
  - (a) is ACCEPTED, conditional on E1.
- A load in which every request is excluded produces an empty run that "completes" with 0 posts and no refusal (probe 4).
- Zero calls. All runs used `git archive 2c43ead` in temporary directories.

### Identity

- `git diff --name-status 8ef0b75 2c43ead` shows 6 files, all M: leakage, lint_opens, loader, payload, selftest, writer. 5199539 is an ancestor.
- `git diff --name-only 2c43ead main(fb6e2e2) --` over data_v2 and the shared judge modules gives 0 lines, so the data_v2 pins still match main.
- New blobs (blob / sha256-lf16):

  | file | blob | sha256-lf16 |
  |---|---|---|
  | leakage | d4c4d6b3b83576ca3ded5e6eca44a48a74755bf3 | 51062599a0331f39 |
  | lint_opens | 774e76e04f845944de44a73b92d058392edd61cd | ce29e57a4da0a61a |
  | loader | 92eab02a1573bc6e3356df233368b768d360e9ca | 0160ec098450b296 |
  | payload | 4b0af34decc3a34fb6ec42f1477a09fcee6593db | 64495031b39f805f |
  | selftest | 2e3b18dd90b7184cd615d3ed0b2c2607193bc71e | cb06db84e9259865 |
  | writer | 8dc001766ccbbb915288e825b1b25dd791187995 | 513d3ddd002d29ed |

- The other four files are unchanged from 8ef0b75.

### Claims

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | selftest 155/155 under python and -O | CONFIRMED | `python[-O] tools/analysis/judge_v2/selftest.py`; rc 0 both | 155 / 0 FAIL, both |
| 2 | lint_opens: 4 hits on the reviewer's lintroot, 0 on the checkout | CONFIRMED | lintroot: REFUSED a.py R1, b.py R2, c.py R1, d.py R3 (rc 1); checkout: 217 files, 0 findings, 10 allowlisted. The allowlist is printed and each entry is named (selftest scratch, two writer read-only readers, the `_sign_for_selftest` hook, the `sign` refusal test) | 4 / 0 |
| 3 | all new D mutants killed | CONFIRMED by count; 23, not 26, in the -O transcript at 2c43ead | builder's `mut_d_pythonO_2c43ead.txt`: 23 MUTANT lines, 23 KILLED (N2, N2b, N4, N4b-d, N5, N5b, N7, N13-N23, N22b, N3r, N11r). The remaining 3 are the 612cdae witness mutants in `mut_d_python_612cdae.txt` | 23/23 at 2c43ead |
| 4 | my N2, N3, N4, N5, N11 re-anchored and killed | CONFIRMED independently | `muts5.json` on ej3 (mine, own anchors): N2 (trace from gt_raw) KILLED "D1: each trace's … letter is the contestant's pred"; N4 (no-ref MIXED never flagged), N4e (exclusion checks A only) and N4f (referenced MIXED demoted to NONE) KILLED; N5 (unknown solver → NONE) KILLED; N24 (ordering key without strip) KILLED; N25 (row refusal made whole-load) KILLED | killed |
| 5 | probes refuse; H1 stops at the private sign | CONFIRMED, with a note | `probe3.py`: public `loader.sign` REFUSED; "anything" as material NONE REFUSED. But `loader._sign` is still reachable, and a hand-built TRAIN spec signed with it is accepted by `JudgeWriter.create` (2 slots). The token is an integrity guard, as ruled (E3) | as ruled |

### The five checks you asked for

- **D1 fixture.** Every trace letter comes from `pred` (`probe3.py`, all 8 contestant traces).
  - mA: pred B = gt B.
  - mB: pred A ≠ gt B on m1–m4 (Q2, Q6, Q8, Q15).
  - The letter in "[This model's selected answer: (X)" equals the contestant's pred in 8/8.
  - N2 is killed. **CONFIRMED.**
- **D3 key material per mcq slot, at create and before each call. CONFIRMED.**
  - `_check_loaded` refuses "N mcq slot(s) carry no KEY material" (selftest L109).
  - `_payload_for` refuses "an mcq slot without KEY material (checked before any call)" (L137, the 612cdae witness: key material removed after create).
  - The scan line prints key / side / other counts separately.
- **D4 registry. CONFIRMED.** `MATERIAL_NONE_REGISTRATIONS = {}`; "anything" is REFUSED; a "DEV-" id is admitted and recorded in run_meta as "(DEV, NOT OF RECORD)". Note: a DEV- declaration switches off the material and key checks for the whole run. That is acceptable for DEV runs only, and the registrar must refuse to record any run whose `material_policy` says DEV.
- **D5 implementation. CONFIRMED for each leg:**
  - `ordering_key` = sha256 of the `str(x).strip()` list (N24 killed);
  - a reference-bearing match where either contestant differs from the solver is excluded per match, never NONE (N4e, N4f killed);
  - a no-reference MIXED match is loaded, flagged `MIXED:a|b` and counted (N4 killed);
  - BBH is refused by `response.source` and by the harness-shaped backstop, each leg witnessed alone (selftest L116-L117).
  - LOW: the source test is case-sensitive (`"BBH"`) and was checked only on the fixture's label. The real ED3 `source` string was not re-read (the CPU rule), so the harness-shaped backstop is the only cover if the case differs. Make the comparison case-insensitive.
- **Accepted survivors. STILL HOLD.**
  - L3x is equivalent: the scan still runs.
  - C2b and C3b are redundant with partners that are killed at 2c43ead: L3 ("the posted payload was not scanned"), N12, L1, L4.
  - C4c is defence in depth, as before.

### The builder's two choices beyond the ruling — ruled

- **(a) Both contestants agree with each other but differ from the solver → excluded per match: ACCEPTED, with E1.**
  - Ruling (2) schedules a reference-bearing pair only if BOTH contestants' orderings equal the solver's, so such a pair should never have been scheduled.
  - Excluding it (counted per model and variant, never rendered, never NONE) is the ruling's own class.
- **(b) A defective reference row → excluded per match: NOT ACCEPTED as built. It weakens fail-closed behaviour.**
  - The loader wraps `choose_reference` in `except SystemExit` and turns EVERY row-level refusal into a per-match exclusion. The class is picked by matching words in the message ("ordering" and "unknown").
  - `probe3.py` P1, with choose_reference forced to raise:
    - a data-integrity refusal ("reference item i:AAA != the slot's item i:BBB") → NOT REFUSED; 4/4 matches `excluded_reference_defect`, 0 loaded;
    - the ruling's own ">1 row → REFUSE, never guess" → NOT REFUSED, same result.
  - P2: a broken solver join (SOLVER_MODEL renamed) → NOT REFUSED; 4/4 `excluded_unknown_solver_ordering`, 0 loaded.
  - Probe 4: that empty load goes into `JudgeWriter.create` → a run is CREATED with 0 pending, `run` posts 0, prints the scan line and returns. No refusal anywhere.
  - A systematic defect therefore shrinks the board silently (a printed count is a presence check, not a count check).
  - This also departs from the MIXED ruling's text, "The loader's refusal stays as the fail-closed backstop" and "A referenced variant whose solver row is missing REFUSES".

### Deviation: the MIXED key in `run_meta.question_options_json`, not a verdict column — ruled

- **ADEQUATE for E-J; record it as a deviation from the ruling's wording ("every verdict row carries its MIXED flag").**
  - `probe3.py` P4: the key is written at create, before any call, as one JSON map keyed by match_id.
  - `run_meta` is append-only: UPDATE is refused "append-only: UPDATE on run_meta"; `INSERT OR REPLACE` is refused "key already present in run_meta (REPLACE refused)".
  - A per-match fact fixed at schedule time is better placed there than repeated per verdict row.
  - `writer.mixed_strata()` gives the stratified readout, but it returns only match_status class counts. The ruling's accuracy / agreement under both tie conventions still needs the readout script.
- **E-D follow-up (LOW, before the first board):**
  - add the key as a `schedule` column (not `verdict`), with a `verdict_equals_schedule`-style guard;
  - pooled readouts across runs must join on (run_id, match_id), not match_id.

### Conditions

- **E1 HIGH. Restore fail-closed around per-match exclusion.**
  - `load_matches` takes the scheduler's `expected_exclusions` (default: none). It REFUSES THE WHOLE LOAD when the realised excluded set, with its classes, differs from it. It also refuses when 0 matches are loaded.
  - `JudgeWriter.create` refuses an empty `Loaded`.
  - Narrow the per-match path to the ruling's classes, by reason code, never by message text:
    - `excluded_MIXED_referenced` and `excluded_ordering_differs_from_solver` (ruling (2));
    - `excluded_unknown_solver_ordering` only if a registration adopts it (the ruling says REFUSES).
  - Every other `choose_reference` refusal refuses the whole load: >1 row, item / stem mismatch, empty or out-of-range answer, NON_TERMINATED, length / content_filter.
  - Witnesses: P1, P2 and probe 4 must refuse.
- **E2 LOW.**
  - Compare the BBH source case-insensitively.
  - `mixed_strata` should check `schema_id` before reading `run_meta`, as `match_verdicts` does.
- **E3 LOW (recorded limit).** The provenance token is an integrity guard only:
  - `loader._sign` is reachable (P3b);
  - `_sign_for_selftest` gates on the caller's `__name__`;
  - lint_opens (R1-R3) misses dynamic access. `lintroot2`: an env-var path passed to `sqlite3.connect`, `getattr(ro, "open_"+"ro")` and `getattr(loader, "_si"+"gn")` give 0 findings.

  This is acceptable as an accident guard; the record must not call it authentication.
- **E4 LOW (record).** A "DEV-" material-NONE run is never of record; the registrar checks `run_meta.material_policy`.

### CPU note

- No new DB query was started for this delta.
- The read-only ED3 count query of the previous delta (PID 14982, `mode=ro&immutable=1`, started 12:22) was still running when this was written; it had printed nothing beyond the five figures already reported. It is read-only on a read-only file.

### Commands

- **Setup:** `git archive 2c43ead tools/analysis <kt> experiment_configs/reserved_pool_frozen_p2dca.json` into the scratchpad `ej3/`.
- **Tests:** `python[-O] tools/analysis/judge_v2/selftest.py`; `python tools/analysis/judge_v2/lint_opens.py [--root lintroot|lintroot2]`.
- **Mutants and probes:** `mut.py ej3 muts5.json`; `probe3.py ej3`; `probe4.py ej3`.
- **Builder's transcripts:** `scratchpad/arch_v2_ej/mut_*_2c43ead.txt`.

---

## DELTA 2026-09-24 — 8ef0b75 (branch worktree-agent-a549c1b2890aa2a8a). INSERTED; the c7525db review below is unchanged

**DELTA VERDICT: MERGEABLE by path (`tools/analysis/judge_v2/` only). READY-WITH-CONDITIONS for the v2 judged path. D1–D6 must be closed, and each needs an execution witness, before the first v2 pilot (G24) or any judged call.**

- C1–C8 of 2aba3ab are met in code, and each is witnessed by execution. The exceptions are C3 and C4, which are met in mechanism but leave gaps D1–D4.
- Nothing in the remaining findings makes merging the package unsafe. It is additive (10 new files), posts nothing, and no run script exists yet.
- The remaining findings are coverage and provenance gaps on the path to a judged run.
- Zero calls. Everything ran in fresh temporary directories.
- One read-only count on the ED3 DEV eval_view (`mode=ro&immutable=1`; sha256 3cb04769f36eeae6… before; file is read-only on disk) — see the CPU note at the end.

### Identity (pin kinds named; the LF rendering is of record; the working tree was not used — every run is on `git archive 8ef0b75`)

- `git diff --name-status 165ffb8 8ef0b75` lists 10 lines, all `A tools/analysis/judge_v2/*`: `__init__`, `_base`, `combiner`, `induction`, `leakage`, `lint_opens`, `loader`, `payload`, `selftest`, `writer`. **CONFIRMED.**
- 165ffb8 and d98b247 are both ancestors of 8ef0b75. The coordinator's note is correct: fb70139's message names 2aba3ab, but the merge brought in 165ffb8.
- judge_v2 blobs at 8ef0b75 (blob / sha256-lf16):

  | file | blob | sha256-lf16 |
  |---|---|---|
  | _base | f88fefa7cdbfea9505a79f4b9e4c0eb12127af54 | f533bc5a7726e8dc |
  | payload | d6b7456a0c5c90931cf570fd1e5c2e9c8f7b7ed1 | c79aac4de18182ca |
  | leakage | f23f5813cc206a4a20194c65d584cd36258bf4e6 | 024ccf854b8e23e1 |
  | combiner | 19c7c5667f697ff370c7a9e8b34dc86406669303 | 3925da82db64cb11 (unchanged) |
  | writer | a0efdc54d4a631071afd727d35412e6fc1ca046b | a668d69234cf7116 |
  | induction | ae17ba25567fd07a2ba4cb5b6d8a558610dd0435 | 6af6a8b2531451c1 |
  | loader | 756afaef7e2bc997e83dda42cf2d7c30b11b6452 | 0b51b814a782301d |
  | lint_opens | 8e53f2c7cf138382aa5fe724effc67cb86ad5f8a | ab63e9df3dc9bfbd |
  | selftest | 917a78c7d9e047642ed113693e9775853f84b243 | 6f2fd4dfc4542fce |
  | __init__ | 9420a5d6f658b59778f069cdadcee79f9ca12a25 | 2ce9384b96559554 |

- **Pins against main.** Every data_v2 file judge_v2 imports is pinned, and each pin equals `git rev-parse 56751fa:tools/analysis/data_v2/<f>`:
  - ro 1fdf7d75…
  - views fe75c7c8…
  - verdicts 10138042…
  - common 1e140335…
  - `__init__` 225c4c49…
  - ingest fd76b439…

  `git diff --name-only d98b247 56751fa -- tools/analysis/data_v2 | wc -l` = 0, so d98b247 and 56751fa carry the same data_v2. The unpinned `gates`, `split` and `ingest` imports appear only in the selftest's fixture builder.
- **Shared modules.** `git diff --name-only 56751fa 8ef0b75 --` over rejudge_reasoning, prompt_v2, rejudge_grok, rubric_value_contrast, rejudge_reference and TaxonomyArenaService.kt gives 0 lines.
- **Induction seed.** The registered seed `ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b` equals `REGISTERED_SEEDS["ARCH-V2-INDUCE-SELECT-1"]` in induction.py, and `git cat-file -t 5abb79f5…` = commit. The version strings `jv2-induce-1/2/3` are refused, and unregistered seeds must start with `DEV-`.

### The builder's claims

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | selftest 131/131 under python and -O | CONFIRMED | `git archive 8ef0b75` → `python[-O] tools/analysis/judge_v2/selftest.py`; rc 0 both | 131 PASS / 0 FAIL, both |
| 2 | E-D gates 143/143 | CONFIRMED | `python tools/analysis/data_v2/gates.py --selftest` | "ALL PASS (143 checks)" |
| 3 | lint 0 findings | CONFIRMED on the repo; the lint itself is WEAK (D4) | `python tools/analysis/judge_v2/lint_opens.py` → 217 files, 0 findings, 5 allowlisted | 0 |
| 4 | 44 of 47 mutants killed | CONFIRMED by count from the builder's transcripts, python and -O | `grep -c KILLED` on the builder's `mut_python_8ef0b75.txt` / `mut_pythonO_8ef0b75.txt` = 44 / 44; survivors C2b, C3b, C4c | 44/47 |
| 4b | my L1–L4, I5/I5b, S1/S2, R2/R4 now killed | CONFIRMED, including the five whose anchors moved | The builder's run of my original file applied only 20 of 25: I5, I6, P1, L3 and O1 were "NOT APPLIED". I re-anchored them on 8ef0b75 (`muts3.json`, `muts4.json`). L3 (poster scan removed) is KILLED with "the posted payload was not scanned"; I5x, I6x and I7x (options dropped from assert_not_eval) and I8x (check_inputs_bound removed) are KILLED | killed |
| 5 | Probes A–D refused, 0 posts | B, C, D CONFIRMED and faithful. A is **WEAKENED** in the re-expression (below); my faithful A1 is REFUSED | builder's `probe_ej.py` rerun on 8ef0b75: A, B1, B2, B3, D REFUSED with posted 0; C REFUSED (REPLACE aborted, vote unchanged) | see below |

**Probe fidelity:**

- **Probe A (weakened).** My probe A tested the material leg: a spec reaching the writer with no material. The re-expression builds a hand-made spec, so the provenance-token check refuses it before the material leg is reached.
  - Faithful version, A1: loader-built specs with valid tokens and the material removed, with no NONE declaration. **REFUSED**, "4 slot(s) carry no leak material", posted 0 (`probe2.py`).
  - Result: C3's refusal holds. The builder's A does not show it.
- **Probes B, C and D** are faithful. B is split into loader and hand-built paths, and both are refused. C is the same SQL. D uses the same smuggled option.

### Survivors (the builder's three) — ruled

- **C2b** (run-level poster check removed alone): **ACCEPTED as redundant.** L3 dies on the per-post check.
- **C3b** (run-level without-material check removed alone): **ACCEPTED as redundant.** N12 (the create-time and slot-time checks removed) is KILLED.
- **C4c** (loader side check off): **ACCEPTED as defence in depth.** `open_eval` refuses a non-eval view by its meta, and `build_view` writes only EVAL items into eval_view, so the second barrier cannot be exercised without forging a sealed view. It is recorded as untested.

### My delta mutants on 8ef0b75 (`muts3.json`, `muts4.json`; python)

| mutant | result |
|---|---|
| I5x, I6x, I7x, I8x, L3, L3b, N6 (key forms emptied), N8 (token check off), N9 (reference ordering check off), N10 (side_v2 check off), N11 (answer range off), N12 (material-required checks off) | KILLED |
| N3 (reference rendered in contestant A's ordering) | SURVIVED. It is EQUIVALENT: the ordering check forces solver ordering = question ordering whenever a reference is used |
| L3x (per-post and run-level poster checks removed, scan kept) | SURVIVED. EQUIVALENT: the scan still runs |
| **N2** (trace built with the KEY `gt_raw` instead of the contestant's `pred`) | SURVIVED. Not equivalent in general: on the fixture `pred == gt_raw` for all 4 loaded matches (mA: B/B on m1–m4), so the path is untested → **D1** |
| **N4** (MIXED ordering never flagged) | SURVIVED → **D5** |
| **N5** (the NONE-by-unknown-solver branch widened to skip choose_reference whenever there is no solver row) | SURVIVED → **D6** |
| **N7** (other-reference material never collected) | SURVIVED. The selftest's check reads `len(other_references) >= 0`, which is always true → **D2** |
| C4c | SURVIVED (ruled above) |

### Probes (reviewer's `probe2.py`, fixture only)

- **A2, material adequacy.** Each rendering is injected into trace A of loader-built m1 and scanned with the loader's own material (key 8, side 2+2, other 0):
  - `"gt_raw": "B"` → key_material
  - `answer_text: x2` / `answer_text=x2` / `"answer_text": "x2"` → key_material
  - `mA.is_correct=1` / `mA is_correct: 1` → marker + side_material
  - **`gt_raw: B` → PASS, `gt_raw=B` → PASS** (the two forms dropped as < 12 characters; no marker rule names `gt_raw`)
  - `The answer key is B.` → PASS; `gold: B` → PASS (natural language: the recorded limit of ruling 4)
- **N2 on the fixture.** The key-for-pred trace equals the pred trace on every loaded match (`trace differs False`), and the scan passes. The fixture cannot tell the two apart.
- **H1 / H2, provenance.** A hand-built MatchInputs of a TRAIN item, passed through the public `loader.sign()`, is ACCEPTED by the writer:
  - with `material_none_registration="anything"`: posted 2;
  - with m1's material attached: posted 2.
- **Lint.** `lint_opens.py --root <tmp>` over four files reports 0 findings. It misses all four bypasses:
  - (a) `import data_v2.ro; data_v2.ro.open_ro(p)` (dotted, no alias);
  - (b) `EV = …"eval_view_DEV.db"` on one line, then `sqlite3.connect("file:%s?mode=ro" % EV)` on the next;
  - (c) `opener = ro.open_ro; opener(p)`;
  - (d) `loader.sign(inp)` from another module.

### Rulings on the builder's four open items

1. **MIXED → refuse any match with a reference: CORRECT IN DIRECTION, NOT SUFFICIENT.**
   - Never render a letter in an ordering that one contestant did not see; ruling (3) indexes the SOLVER's ordering, and the judged block must match it.
   - Three conditions attach:
     - (a) The rule is untested: N4 survives. Add a fixture pair with two orderings and a reference, and require the refusal.
     - (b) One MIXED request refuses the WHOLE load. That is fail-closed, but it makes the scheduler (E-A) responsible for excluding them, and the exclusion must be counted.
     - (c) **Exposure is large, and the record must see it before G24.** On ED3 DEV, 5,473 of the 6,262 variants with ≥ 2 ACTIVE responses carry more than one `options_ordered_sha` among those responses (read-only count). Many pairs will therefore be MIXED.
   - Before the schedule is fixed, the judge-design-specialist must rule what a MIXED referenced match is: excluded, NONE, or a registered text-only rendering. Silent NONE is not acceptable.
   - The pair-level MIXED rate among v0-referenced variants is owed from the real split. My count of it was stopped by the CPU rule (note below).
2. **NONE when the solver's ordering is unknown: NOT ACCEPTED; it must REFUSE.**
   - The ruling's NONE covers only "no row of the board's vintage". A row that exists but cannot be rendered in the solver's ordering cannot pass the ruling's own check ("a letter inside the variant's option range" of the solver's ordering). By the ruling's "never guess", it is a refusal.
   - The branch also runs before `choose_reference`, so on that path the v1-without-registration refusal and the NON_TERMINATED / length / content_filter / empty-answer refusals are skipped, and a defective row becomes NONE (N5 survives).
   - Cost of refusing: zero on DEV. On ED3 DEV, reference rows by vintage and resolution are v0 `solver_row` 1,036 and v1 `solver_row` 63, and the v0 rows without a solver row number **0**.
   - If the real split produces such rows, a registration may adopt a counted NONE class explicitly.
3. **MATERIAL_FORMS: adequate for machine fields only after two fixes; never adequate for natural language (the recorded limit).**
   - Dropping the 16 of 64 short renderings removes exactly the bare single-letter key forms (`gt_raw: B`, `gt_raw=B`). Nothing else covers them: probe A2 passes both.
   - Fix (D3): add `gt_raw`, `answer_text` and `is_correct_mathfix` as machine-field marker rules. The field names do not occur in legitimate task text, and `is_correct(_mathfix)` already has a rule.
   - The side material duplicates the `is_correct` marker rule, and it alone makes `_has_material` true. The "with material" count therefore does not show that KEY material exists. For mcq, require at least one key string per slot and print the key, side and other counts separately.
   - The most plausible key leak is not a machine field. A positional swap of `pred` and `gt_raw` in the loader's response tuple renders as legitimate content, "[This model's selected answer: (X) …]", which no material can see. Only a fixture test can cover it (D1).
4. **Per-process HMAC token: ENOUGH AS AN INTEGRITY / ACCIDENT GUARD, NOT AS PROVENANCE, while `sign` is public.**
   - Per-process is the right scope. The token is never persisted (`git grep provenance` in writer.py: check-only). A relaunch re-loads from eval_view, and the schedule-reproduction check binds it to the first launch.
   - But `loader.sign` is a public function. Probe H1 shows one call re-opens probe B, and a free-text `material_none_registration` switches C3 off. The record must call this token integrity, not authentication, as with E-A's seal.
   - Fix (D4): make signing private to `load_matches`; the selftest's one use (L481) goes through a test hook. Add a lint rule counting references to it outside loader.py (0 expected). Validate `material_none_registration` against a registry, as `REGISTERED_SEEDS` does.

### Defects and conditions (before any judged call; none blocks the path merge)

- **D1 HIGH. A key-for-pred substitution is untested.**
  - Add fixture contestants whose `pred ≠ gt_raw` on loaded matches.
  - Check that each trace's "[This model's selected answer: (X) …]" letter is the contestant's `pred` and the reference is the v0 `answer`, never `gt_raw`.
  - N2 must die.
- **D2 MEDIUM. The other-reference material is untested.**
  - Replace `len(other_references) >= 0` with a fixture item that has an other-vintage or other-variant reference, and require its block in the material.
  - Add a wrong_reference refusal on a loader-built match. N7 must die.
- **D3 MEDIUM. Marker rules and per-kind material counts.**
  - Add the machine-field marker rules for `gt_raw`, `answer_text` and `is_correct_mathfix`. Probe A2's `gt_raw: B` and `gt_raw=B` must refuse.
  - For mcq, require key material per slot and print the key, side and other counts separately.
- **D4 MEDIUM. Provenance token and lint.**
  - Make `sign` private to the loader.
  - Validate `material_none_registration` against a registry.
  - Widen lint_opens so that all four bypasses above are REFUSED: dotted `data_v2.ro.*` attribute chains, any reference (not only calls) to a ro opener, a connect in a file that names a corpus_v2 / gen_view / eval_view `.db` anywhere, and references to the signing function outside loader.py.
  - Probe H1 must refuse, and the lint probe must report 4 findings.
- **D5 MEDIUM (ruling 1).**
  - Add a fixture for the MIXED refusal; N4 must die.
  - Count the pair-level MIXED rate among v0-referenced pairs on the real split.
  - The judge-design-specialist rules the class before the schedule is fixed.
- **D6 MEDIUM (ruling 2).**
  - The unknown-solver-ordering branch REFUSES.
  - `choose_reference` runs on every path, so the vintage and defect refusals cannot be skipped.
  - N5 must die.
- **Carried, LOW:**
  - C4c is untested defence in depth.
  - N3 and L3x are equivalent mutants.
  - The builder's `probe_ej.py` probe A should be replaced by A1 as its faithful form.

### CPU note (disclosure)

- One read-only count query on the ED3 DEV eval_view (`sqlite3` `mode=ro&immutable=1`, single process) printed its first five results in under 300 s.
- Its last two queries were heavy joins, and they were still running when this delta was written. The reviewer's request to stop that process was refused by the permission system as interference with workloads, so it runs to completion on its own. It is read-only, the file is read-only on disk, and no second query was started.
- The pair-level MIXED rate is therefore not reported here (D5 owes it on the real split).

### Commands

- **Setup:** `git archive 8ef0b75 tools/analysis <kt> experiment_configs/reserved_pool_frozen_p2dca.json` into the scratchpad `ej2/`.
- **Tests:** in `ej2/`, run `python[-O] tools/analysis/judge_v2/selftest.py`, `python tools/analysis/data_v2/gates.py --selftest` and `python tools/analysis/judge_v2/lint_opens.py [--root <tmp>]`.
- **Mutants and probes:** `scratchpad/mut.py ej2 muts3.json|muts4.json`; `scratchpad/probe2.py ej2`; the builder's `scratchpad/arch_v2_ej/probe_ej.py ej2`.

---

Adversarial reviewer, 2026-09-24. Zero calls. Selftests, fixture runs and mutants only, all in temporary directories; no DB of record opened; single process (a v1 validity run at R = 1,000 was running).

## VERDICT: NOT READY (to merge c7525db onto main). READY-WITH-CONDITIONS once C1–C4 are met and C5–C6 are either met or ruled on. The code's core is sound; the gaps are in coverage and provenance.

The core holds, and each item below was executed:
- the payload;
- the fixed persona;
- the rubric slot only;
- the reference-variant refusal;
- the six-way enum;
- the combiner;
- temperature omitted;
- the relaunch identity checks.

It fails READY on four points:

1. **(BLOCKER)** E-J pins the DEV data layer, and main's layer refuses at import.
   - 3 of the 5 pinned data_v2 blobs differ on main (d98b247).
   - The branch carries its own copies of data_v2: 6 of 8 differ from main's.
   - Its pinned DEV `verdicts.py` accepts `INSERT OR REPLACE` over a stored verdict (probe C).
2. **(HIGH)** The "full-payload scan on 100% of payloads" has no count witness. Removing the scan for one order, or from the poster, leaves the selftest at 73/73.
3. **(HIGH)** The scan's material legs are vacuous by default. Nothing produces `LeakMaterial`, and a launch with a key annotation in a trace posts.
4. **(HIGH, the E-D residual)** The eval_view → MatchInputs loader is NOT BUILT. The writer admits a TRAIN item and a routing-only sentinel as matches. The lint does not refuse a corpus_v2 open outside data_v2.

This is an engineering READY. There is no deciding statistic, so the Support section (rule 8) is N/A.

## Identity (pin kinds named)

- Branch `worktree-agent-a549c1b2890aa2a8a`, commit c7525db (HEAD of the worktree; `git status --short | wc -l` = 0).
- The worktree's files equal the LF rendering: working-tree sha256 = sha256-lf16 for all 8 files.

| file | blob | sha256-lf16 |
|---|---|---|
| judge_v2/_base.py | 4b6585515925c54479b3e9463119d611869f8093 | bbdea69fdca6253c |
| judge_v2/payload.py | 5415f4c33057f8c36c74e384cc334d037c1ec090 | 04cb81e416c22f23 |
| judge_v2/leakage.py | 3692575ab5c2d800c41a8702bb94f41a2a71ca2c | a0cb9109cef9cca9 |
| judge_v2/combiner.py | 19c7c5667f697ff370c7a9e8b34dc86406669303 | 3925da82db64cb11 |
| judge_v2/writer.py | 4a2ebea210989ddad650173b393dc9fc83a63f1e | 4273287bce2b4b44 |
| judge_v2/induction.py | 87b50da2c5e22c344823bec530e197599144257d | e3300309c2ec99b5 |
| judge_v2/selftest.py | fedf61fd695e2044d0421b924de9755f28a2a8ea | 7ed996e0b97457dd |
| judge_v2/__init__.py | 255d4c7e7a6bda9dc5e4ab0cd12b0094efd2bea0 | adb66b3f702ee10c |

- **Diff from the merge base:** 16 files, all status A (`git diff --name-status $(git merge-base main c7525db) c7525db | awk '{print $1}' | sort | uniq -c` → `16 A`). No existing file is modified, so v1 is untouched by construction.
- **Shared modules:** same blob on c7525db and on main for each of:
  - rejudge_reasoning 1339592a;
  - prompt_v2 52b36965;
  - rejudge_grok 939de7c7;
  - rubric_value_contrast 9e1541a7;
  - rejudge_reference 7640f800.
- **TaxonomyArenaService.kt:** `git diff --name-only c7525db main -- <kt> | wc -l` = 0.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | selftest 73/73 under python | CONFIRMED | `python tools/analysis/judge_v2/selftest.py` in the worktree; rc 0 | 73 PASS, 0 FAIL vs 73/73 | — |
| 2 | selftest 73/73 under -O | CONFIRMED | `python -O …/selftest.py`; rc 0 | 73 PASS vs 73/73 | — |
| 3 | persona = `rubric_value_contrast.GENERIC_SYSTEM`, sha256 3a5e223c…53ddb9 | CONFIRMED | sha256 of the literal recomputed: 3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9 | equal to the digit | — |
| 4 | persona altered → refused | CONFIRMED | mutant P2 (constant altered in _base): refused at import by the template pin. Mutant P1 (altered in build_system, pin intact): KILLED, 3 checks fail (GOLDEN o1, o2, persona-slot check) | killed ×2 | — |
| 5 | rubric slot only (induced artefact never fills $systemPrompt) | CONFIRMED | these refusals are executed in S1/S5: `load_rubric` with a system_prompt field; an unknown field; an induce reply carrying system_prompt; a forged artefact carrying one on load | executed | — |
| 6 | "GOLDEN re-pin moved ONLY the persona slot" (inertness claim) | CONFIRMED, with an execution witness | the old persona substituted into the new builder reproduces 9d993cc's GOLDEN (`git show 9d993cc:…/selftest.py` L59-60 = 3f66740e… / c4b3809f…); P1 shows the check discriminates | witnessed | — |
| 7 | rubric induced from gen_view ONLY | CONFIRMED on the default path, PARTLY on the caller-supplied path | mutants killed: I1 (open_eval), I2 (ro.open_ro bypass), I3 (GATE admitted), I4 (side filter off), I6 (assert_not_eval removed). **Probe D:** a TRAIN stem whose `options` carry an EVAL stem is ADMITTED, and the EVAL text reaches the induction prompt (True). Options are never content-key checked (`texts_stem` only, induction.py L175). The docstring's "they pass the SAME content-key assert" is false for options | leak on the `inputs=` path | MEDIUM (C5) |
| 8 | GATE excluded from induction | CONFIRMED (single barrier plus assert) | I3 and I4 killed; I5b (assert skipped on the selected path only) SURVIVES, so that assert is untested redundancy | — | LOW |
| 9 | a reference from another variant refused (R9) | CONFIRMED | mutant R1 KILLED (2 fails) | killed | — |
| 9b | reference stem_key mismatch / unknown kind refused | UNTESTED | R2 (stem_key check removed) and R4 (kind check removed) SURVIVE | 73/73 with the guard gone | LOW (C7) |
| 10 | verdict store append-only | REFUTED as built; CONFIRMED on main | **Probe C:** `INSERT OR REPLACE INTO verdict` on a stored slot through `ro.open_run_writer`. On E-J's pinned DEV verdicts.py (bb3e83d1): ACCEPTED, vote FIRST → SECOND. On main's verdicts.py (10138042, no-rekey triggers): REFUSED "key already present in verdict (REPLACE refused)", vote unchanged. E-J's own selftest has no overwrite check (the pin is its only protection) | branch vulnerable; main safe | BLOCKER (C1) |
| 11 | six-way enum; NON_TERMINATED / CONTENT_FILTER never TIE | CONFIRMED | V1–V6 KILLED under python and -O. V1, V2 and V6 are killed by the store's CHECK constraint (IntegrityError), the others by selftest checks. Recomputed: combiner vs rejudge_grok.combine_orders 16/16 equal; AST pin holds; 0 of the 20 NT/CF pairs combine to anything but NT/CF | 16/16, 0 | — |
| 12 | full-payload leakage scan on 100% of the bodies about to be posted | PARTLY | leak classes are refused on a single payload (S2, 12 cases). **Coverage has no witness.** These mutants SURVIVE at 73/73: L1 (scan skipped for order-1 slots), L2 (order-2 slots), L3 (scan removed from the poster; prescan only). The `[LEAK-SCAN]` line prints `scanned N` but nothing compares N with 2 × matches × draws | presence check, not a count check | HIGH (C2) |
| 13 | scan refuses side / key / wrong-reference material | PARTLY (vacuous by default) | L4 (materials never passed) SURVIVES. **Probe A:** a writer launch with no `materials` and the traces carrying "Answer key for this question: (A) Mercury" plus another variant's reference: posted 2, `[LEAK-SCAN] refused 0`. No code in judge_v2 builds a `LeakMaterial`; `self.materials.get(mid)` → None → empty | silent pass | HIGH (C3) |
| 14 | a random stream pinned | UNTESTED | E-J has one stream: induction input selection (sha256(seed ‖ variant_id); default seed = the version string "jv2-induce-2", not a registered seed). S1 (random shuffle) and S2 (seed ignored) SURVIVE. There is no golden of `input_variant_ids_sha256`. The judge path has no random stream (both orders are always scheduled; the grep for `random` in judge_v2 finds 0 hits outside the selftest) | determinism unwitnessed | MEDIUM (C6) |
| 15 | temperature omitted | CONFIRMED | T1 KILLED; body keys = [model, max_tokens, messages] | — | — |
| 16 | relaunch posts only PENDING slots; identity check | CONFIRMED | W1 and W2 KILLED; S3 relaunch checks executed | — | — |
| 17 | zero calls / no live default poster | CONFIRMED | `writer.run` refuses a non-callable. `git grep call_judge_full` in judge_v2: only docstrings and the refusal message, no call site | — | — |
| 18 | G6 is a hook, never a pass | CONFIRMED (read) | `g6_kotlin_parity(…, None)` returns status TODO; PASS requires a non-empty set with every sha equal | — | — |
| 19 | E-J uses data_v2's openers and verdict store | CONFIRMED for induction (`open_generation("induce")`), the store (`VerdictStore`) and `open_run_writer`; NOT APPLICABLE for `open_eval`: no production code opens eval_view (only the selftest's `eval_variants`) | `git grep -n "open_eval\|open_generation\|open_ro(" c7525db -- tools/analysis/judge_v2` | — | — |
| 20 | compatible with main's data_v2 (d98b247) | REFUTED as built; CONFIRMED after 3 re-pins | c7525db's tools/analysis/judge_v2 overlaid on main's tools/analysis (scratch copy via `git archive`) → `[JUDGE-V2] data_v2/views.py is blob:fe75c7c8…, not the pinned blob:f829009b…`. Changing ED_PINS to main's views fe75c7c8 / verdicts 10138042 / common 1e140335 (ro 1fdf7d75 and __init__ 225c4c49 are unchanged) → 73/73 under python and -O. There is no API drift in the calls E-J makes. Main's new `verdict_equals_schedule` trigger is satisfied, because the writer passes the slot's stem_key / reference row / vintage | pin drift only | BLOCKER (C1) |
| 21 | loader eval_view → MatchInputs through `open_eval` only (E-D residual, READY_archv2_ED L250) | NOT BUILT | no function in judge_v2 builds MatchInputs from a view. **Probe B:** `JudgeWriter.create` + `run` with a TRAIN gen_view item and an EVAL routing-only sentinel as matches: posted 4, no refusal. `check_inputs` checks only internal consistency (question re-keys to stem_key; ref variant = match variant), never provenance | the writer judges any text | HIGH (C4) |
| 22 | lint refuses a corpus_v2 opening outside data_v2 | NOT BUILT | main's `data_v2/lint_connect.py` counts only `sqlite3.connect`. `grep -c "open_ro\|corpus_v2" lint_connect.py` = 0. `ro.open_ro` has no view_kind gate. judge_v2 itself has 0 `sqlite3.connect`: the one lint hit named judge_v2 is `tools/analysis/judge_v2_free_checks.py`, a different file | — | HIGH (C4) |
| 23 | selftest writes nothing of record | CONFIRMED, with one LOW | all DBs are under `tempfile.gettempdir()`. On main's data_v2, `build_corpus` without `repo_root` reads the checkout's `experiment_configs/reserved_pool_frozen_p2dca.json` (read-only JSON; the scratch run failed until that file was present). Pass the fixture's `repo_root`, as data_v2's own selftest does | read of a real file | LOW |

## Mutation suite (the reviewer's; scratch `mut.py`, `muts.py`; identical under python and -O)

| id | mutation | result |
|---|---|---|
| I1 | induction opens via open_eval('judge') | KILLED |
| I2 | induction opens via ro.open_ro (gate bypassed) | KILLED |
| I3 | DEFAULT_SIDES = TRAIN + GATE | KILLED |
| I4 | select_inputs ignores sides | KILLED (by the content-key assert) |
| I5 / I5b | sides ignored + assert skipped on the selected path / the assert alone skipped | SURVIVED / SURVIVED |
| I6 | assert_not_eval removed | KILLED |
| P1 / P2 | persona altered in build_system / in _base | KILLED / KILLED |
| R1 | other-variant reference admitted | KILLED |
| R2 | reference stem_key check removed | SURVIVED |
| R3 | response-bound reference admitted | KILLED |
| R4 | reference kind check removed | SURVIVED |
| L1 / L2 | writer scan skipped for order 1 / order 2 | SURVIVED / SURVIVED |
| L3 | scan removed from the poster (prescan only) | SURVIVED |
| L4 | materials never passed to the scan | SURVIVED |
| V1–V6 | NT→INVALID, CF→NT, combiner NT→INVALID, CF/NT precedence swapped, unparsed→TIE, length-with-content parsed | all KILLED |
| S1 / S2 | induction selection shuffled / seed ignored | SURVIVED / SURVIVED |
| T1 | temperature 0.0 | KILLED |
| W1 / W2 | relaunch identity / schedule check dropped | KILLED / KILLED |
| O1 | options through leg (b) (control) | KILLED: leg (b) cannot key options, so leg (a) must be used for them |

Verdict overwrite as a mutant: E-J issues no SQL of its own (the writer writes only through `VerdictStore.drain`), so the overwrite path was tested by direct probe C instead (row 10).

## Defects and conditions

- **C1 BLOCKER. Re-pin, and merge by path only.**
  - Set ED_PINS in `judge_v2/_base.py` to main's blobs:
    - views fe75c7c8db233823078f3161e877546703c13c92
    - verdicts 1013804233b7ccfc0df699acdcaf518b089ad526
    - common 1e140335e04d616ab9e4d5d4c1f5e3217328471a
    - ro 1fdf7d75… and __init__ 225c4c49… unchanged
  - Merge **only `tools/analysis/judge_v2/`** by pathspec. Never merge the branch's `data_v2/` copies: 6 of 8 differ from main, and its verdicts.py accepts REPLACE.
  - Add an E-J selftest check that an `INSERT OR REPLACE` / `UPDATE` / `DELETE` on a stored verdict aborts, so the store's append-only property is witnessed from E-J's side.
  - Executed: the three re-pins give 73/73 under python and -O on main's data_v2.
- **C2 HIGH. Scan coverage by count.**
  - `prescan` must refuse unless `stats.scanned` equals `len(pending)`.
  - The poster must scan every posted payload, and `run` must refuse unless the in-poster scan count equals posts.
  - Print both on every run.
  - Add a selftest leak in the order-2 payload only (and one in the last slot only) that must refuse; L1, L2 and L3 must die.
- **C3 HIGH. Material legs must not pass silently.**
  - `JudgeWriter.create` / `run` must refuse a slot with no `LeakMaterial` unless the registration declares material = NONE for that corpus.
  - `[LEAK-SCAN]` must print the number of slots scanned with material and without it.
  - The loader (C4) builds the material from eval_view: the key fields (gt_raw, answer_text, is_correct as rendered), the other variants' references, and the per-side checker outcomes.
  - L4 must die.
- **C4 HIGH. The loader, and the lint (E-D residual).**
  - Build `load_matches(eval_view_path, …)` that opens through `data_v2.views.open_eval("judge")` only. It returns MatchInputs whose question, stem_key, variant, options and reference come from eval_view rows; it refuses sentinels and non-judgeable variants.
  - `JudgeWriter.create` must refuse specs that did not come from the loader (for example a loader token, or a re-check of every spec against eval_view by variant_id → stem_key → side EVAL).
  - Probe B must be refused.
  - Extend `lint_connect.py`, or add a lint, that refuses any `ro.open_ro` / connect on a corpus_v2 or view file outside `data_v2/`.
  - A registered rule is needed for which of several `reference` rows (PK variant_id, vintage, source_key) is the ONE reference. Render only `answer`, never `gt` or `correct`.
  - Map `side_at_mint` explicitly.
- **C5 MEDIUM. Induction options.**
  - Run `assert_not_eval` on option texts too; leg (a) can key them, and O1 shows leg (b) cannot.
  - For caller-supplied `inputs`, require each input's stem and options to equal gen_view's row for that variant_id.
  - Correct the docstring by insertion. Probe D must be refused.
- **C6 MEDIUM. Induction stream.**
  - Register the induction seed; the default is the version string.
  - Pin a golden `input_variant_ids_sha256` on the fixture, so that S1 and S2 die.
- **C7 LOW.** Add refusal tests for a reference stem_key mismatch (R2) and an unknown kind (R4). Optionally make I5b die with a selected-path GATE fixture.
- **C8 LOW.**
  - `writer.match_verdicts` omits run_id and reads the INNER-JOIN `match_verdict`. Denominators must come from main's `match_status`, which lists PENDING.
  - Pass `repo_root` into `build_corpus` in `selftest.build_views`.
- **Recorded limits, not defects:**
  - The `structure` leg recomputes the system turn with the same `build_system` the builder uses, so it detects tampering after the build, not a builder error. The GOLDEN shas plus the template pins cover the builder.
  - Natural-language leakage is covered by the post-run full-payload review scan (ruling 4, L15159).

## Inertness claims and their witnesses

- **"Only the persona slot changed"**: witnessed. The old persona substituted into the new builder reproduces the 9d993cc shas, and P1 shows the check discriminates.
- **v1 untouched**: by construction. All 16 files are new; `--name-status` count = 16 A.
- **Zero calls**: by construction. There is no live default; a non-callable is refused.
- **"100% of payloads scanned"**: NOT witnessed. L1, L2 and L3 survive (C2).

## Commands

- **Selftests:**
  - `python[-O] tools/analysis/judge_v2/selftest.py` in `.claude/worktrees/agent-a549c1b2890aa2a8a`.
  - The composite: `git archive main tools/analysis <kt> experiment_configs/reserved_pool_frozen_p2dca.json` plus `git archive c7525db tools/analysis/judge_v2`, in the session scratchpad `comp/`.
- **Mutants:** `scratchpad/mut.py <base> <muts.json> [-O]`; base = `git archive c7525db` in `scratchpad/ejbase/`.
- **Probes A–D:** `scratchpad/probe.py <root>`, run on ejbase (as built) and on comp (main data_v2, re-pinned).
- **Scratch location:** the session scratchpad under `%LOCALAPPDATA%\Temp\claude\…\7c10e5cb…\scratchpad`, not committed. Everything ran in fresh temporary directories.
