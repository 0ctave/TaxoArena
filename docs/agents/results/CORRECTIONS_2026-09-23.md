# Corrections of record, 2026-09-23 (registrar, phase A: text half of INCONSISTENCIES.md)

Scope: classes **2**, **4**, **5** and **9** of `docs/agents/results/INCONSISTENCIES.md` (2026-09-22,
commit 8eeddaf) — the four classes that need **no ledger patch and no new programme registration**.
This document is a worksheet for phase C. It applies nothing. Nothing was run to produce it: the only
commands executed were `git log`, `git show`, `sed`, `grep` and `sha256sum` (read-only); no
`tools/analysis/*.py`, no judge call, no build, no DB of record opened.

Phase A hygiene: `docs/judge_v2_program.md`, `docs/test_ledger.html`, `docs/agents/queue.json` and
`docs/agents/results/*.json` were READ ONLY and are not touched by this commit (another registrar holds
the programme).

[AMENDED 2026-09-23, second commit, same evening: C5-1 (GROK-CALIB) moved from UNDETERMINED to READY,
and the class-5 preamble gained the rendering rule that its settlement forced. The evidence is a
read-only sqlite query on `grok_calib.db` (`mode=ro&immutable=1`) **run by the coordinator, not by the
registrar**, and reported to me; it is not under `tools/analysis/`, so the live construction chain was
not touched. Nothing else in this file changed; the superseded counts are left in place beside the new
ones. Totals moved 23 READY / 3 UNDETERMINED → **24 READY / 2 UNDETERMINED**.]

How to read an item
- **WHERE** — the file to edit.
- **ANCHOR** — the verbatim existing text to insert *after* (never a line number; line numbers drift).
  Line numbers, where given, are as of HEAD `e422daa` and are a hint for grep, not the anchor.
- **TEXT** — the exact bracket / sentence to insert, verbatim, between the quote marks (the marks are
  not part of it).
- **KIND** — PROGRAMME EDIT / RECORD EDIT / PLAN EDIT / NEW FILE / LEDGER EDIT (none of the items below
  is a LEDGER EDIT; the ledger half is phase C's class 6/7/10 work).
- **STATUS** — READY (applies mechanically, every value verified by a command named here) or
  UNDETERMINED (with the evidence that would settle it). No sha or commit below is guessed.

Standing rule kept throughout: correction **by insertion only**; the last bracket wins; nothing is
deleted or rewritten.

---

## Class 2 — registrations that live outside `docs/judge_v2_program.md` (NO-REG)

The backlog's proposed fix is "a pointer ... so a reader grepping the programme is redirected". The
programme is append-ordered, newest last, so the mechanical form is **one dated section appended at the
END of the programme** carrying all seven pointer sentences. That is item **C2-0**; C2-1 … C2-7 are its
lines, each independently verified below.

### C2-0 — the container
- **WHERE**: `docs/judge_v2_program.md`
- **ANCHOR**: the END of the file. At HEAD the last section is
  `## MULTI-SWE-ADMISSION (cheap variant) (2026-09-22, zero LLM calls; network + local ingest) — C1 FAILED:`…
  Append after its last line.
- **TEXT** (heading + the seven lines C2-1 … C2-7 below, in this order):
  `## Registration index, appended 2026-09-23 (registrar, pointer only; no test, no call, no criterion) — where the registrations that are NOT sections of this file actually live`
  `This file is the register of record, but seven lines of work were registered elsewhere or as bullets. Nothing below is new: each line names the file and the heading that holds the registration, so a reader grepping this programme for the id is redirected instead of concluding the test was never registered. [INCONSISTENCIES class 2, docs/agents/results/INCONSISTENCIES.md at 8eeddaf.]`
- **KIND**: PROGRAMME EDIT (one append)
- **STATUS**: READY

### C2-1 — the rubric line (REF-GATED-RUBRIC, LEAF-POWERED, RK-1b, RK-1b-GROK, RK-1c)
- Registrations of record, verified by grep at HEAD:
  - `docs/rubric_v2_design.md` L331 `## Registered 2026-09-14 (before any call) — REF-GATED-RUBRIC: is rubric value conditional on the reference being right?` (registration commit 3770ca5)
  - `docs/rubric_v2_design.md` L213 `### LEAF-POWERED — registered 2026-09-14, before any call (tools/analysis/leaf_powered.py)` (a12cdc6)
  - `docs/rubric_v2_design.md` L124 `### RK-1b / RK-1c — registered 2026-09-10 06:50, before any judged call (tools/analysis/rubric_kit2.py)` (98c580f) — this one heading registers **both** RK-1b and RK-1c
  - `docs/rubric_v2_design.md` L145 `### RK-1b-GROK — registered 2026-09-10 15:10, before any judged call (rubric_kit2.py --judge-model grok)` (cfb28e0)
  - also in that file: L49 `## Registered tests (all on R3's 1,980 matches, Mistral, dual order, one session per test; paired McNemar on key-decidable; arms interleaved)` — the rubric line's registration block
- **TEXT** (one line inside C2-0):
  `- The RUBRIC KIT line is registered in docs/rubric_v2_design.md, which is a registration file of record for it: REF-GATED-RUBRIC at its heading "## Registered 2026-09-14 (before any call) — REF-GATED-RUBRIC: is rubric value conditional on the reference being right?" (3770ca5); LEAF-POWERED at "### LEAF-POWERED — registered 2026-09-14, before any call (tools/analysis/leaf_powered.py)" (a12cdc6); RK-1b AND RK-1c together at "### RK-1b / RK-1c — registered 2026-09-10 06:50, before any judged call (tools/analysis/rubric_kit2.py)" (98c580f); RK-1b-GROK at "### RK-1b-GROK — registered 2026-09-10 15:10, before any judged call (rubric_kit2.py --judge-model grok)" (cfb28e0); the family's shared instrument block at "## Registered tests (all on R3's 1,980 matches, Mistral, dual order, one session per test; paired McNemar on key-decidable; arms interleaved)". Their OUTCOMES are bullets in this programme (RK-1b L347, RK-1b-GROK L431, RK-1c L435 as of HEAD e422daa).`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

### C2-2 — the multi-corpus line (MC-BUILD, MC-FED, MC-ROOT, MC-ROUTER, MC-LEAF, MC-E2E, MATH-FIX, GEN-ARENA, N4-RECONCILED)
- Registrations of record, verified by grep at HEAD in `docs/multi_corpus_design.md`:
  - MC-ROUTER — L247 `## Stage 2 result (2026-09-11, zero calls) — there IS something to route on a multi-corpus union` (a53f57e; the criterion itself fixed in `tools/analysis/multicorpus_router.py`'s docstring before running)
  - MC-BUILD and MC-LEAF — L268 `## Stage 1 build + stage 2b result (2026-09-11, zero calls)` (2bfecdb / d9dfc97; MC-LEAF's readout registered in `multicorpus_leaf_router.py`'s docstring before running)
  - MC-FED — L357 `## Stage 1b result, per-corpus half (2026-09-11 14:15, zero calls) — federated construction recovers certification` and L376 `## Stage 1b result (2026-09-11, zero calls): federated construction + union graft` (511937e / c1eacd2)
  - MC-ROOT — L407 `## Stage 1c result (2026-09-11, zero calls): the union root routing rule` (71d7441)
  - MC-E2E (and MC-SEEDS) — L448 `## Registered 2026-09-13 (before running) — MC-E2E: the deployed router, and MC-SEEDS: its replication` (dc7d1ef)
  - MATH-FIX — L489 `## Registered 2026-09-13 (before recomputing) — MATH-FIX: a tolerant answer extractor for the MATH corpus` (d29f445)
  - GEN-ARENA — L536 `## Registered 2026-09-13 (before any call) — GEN-ARENA: does the deployed judge reproduce the router WITHOUT keys?` (a09b7ee)
  - N4-RECONCILED — L309 `N4 RECONCILED (2026-09-14, zero calls): what the union actually costs is SUPPORT, not separation.` (afc62fb; corrected at L332 `N4 MECHANISM CORRECTED (2026-09-15 ...)`, 4ec8f18)
- **TEXT** (one line inside C2-0):
  `- The MULTI-CORPUS line is registered in docs/multi_corpus_design.md, which is a registration file of record for it: MC-ROUTER at "## Stage 2 result (2026-09-11, zero calls) — there IS something to route on a multi-corpus union" (a53f57e, criterion in multicorpus_router.py's docstring before running); MC-BUILD and MC-LEAF at "## Stage 1 build + stage 2b result (2026-09-11, zero calls)" (2bfecdb / d9dfc97, MC-LEAF's readout in multicorpus_leaf_router.py's docstring before running); MC-FED at "## Stage 1b result, per-corpus half (2026-09-11 14:15, zero calls) — federated construction recovers certification" and "## Stage 1b result (2026-09-11, zero calls): federated construction + union graft" (511937e / c1eacd2); MC-ROOT at "## Stage 1c result (2026-09-11, zero calls): the union root routing rule" (71d7441); MC-E2E and MC-SEEDS at "## Registered 2026-09-13 (before running) — MC-E2E: the deployed router, and MC-SEEDS: its replication" (dc7d1ef), with the "## CORRECTION 2026-09-14 — the reserved side of MC-E2E / MC-SEEDS was not the tree's held-out pool" section in the same file; MATH-FIX at "## Registered 2026-09-13 (before recomputing) — MATH-FIX: a tolerant answer extractor for the MATH corpus" (d29f445); GEN-ARENA at "## Registered 2026-09-13 (before any call) — GEN-ARENA: does the deployed judge reproduce the router WITHOUT keys?" (a09b7ee); N4-RECONCILED at "N4 RECONCILED (2026-09-14, zero calls): what the union actually costs is SUPPORT, not separation." (afc62fb), corrected in place at "N4 MECHANISM CORRECTED (2026-09-15 ...)" (4ec8f18).`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

### C2-3 — RUBRIC-512-R: the missing `## Registered` heading is NOT missing, it is in a third file
- **Finding that corrects the backlog.** INCONSISTENCIES class 2 says "RUBRIC-512-R has only the
  registration commit 1e8203c and an outcome bullet". It has a full registration text. Verified:
  `git show -s 1e8203c` = *"Register J3-R (prompt v2 + reasoning reference) and RUBRIC-512-R (reasoning
  judge, both arms fresh) before launch"*, 2026-09-09 23:37:50 +0200, and `git show 1e8203c --stat`
  shows it touched **exactly one file**, `docs/judge_improvement_proposals.md` (+34 lines). At HEAD the
  text stands at `docs/judge_improvement_proposals.md` L337 under
  `### RUBRIC-512-R — cell rubric value for the REASONING judge (~8k grok-reasoning calls)`, inside the
  block `## Launch records 2026-09-09 (late) — registered before any call` (L314), and it carries
  REGISTERED PRIMARY, SECONDARY and a numeric prediction ("+0 to +2pp, NOT significant").
- **TEXT** (one line inside C2-0):
  `- RUBRIC-512-R's registration is NOT missing and is not in this file: it is docs/judge_improvement_proposals.md L337 (as of HEAD e422daa) "### RUBRIC-512-R — cell rubric value for the REASONING judge (~8k grok-reasoning calls)", inside "## Launch records 2026-09-09 (late) — registered before any call", added by commit 1e8203c (2026-09-09 23:37, the only file that commit touched), with its REGISTERED PRIMARY, SECONDARY and the numeric prediction "+0 to +2pp, NOT significant"; the outcome is the bullet "- **RUBRIC-512-R (2026-09-10 02:20): exactly zero for the reasoning judge — B4 closed for both" in this programme. [CORRECTS docs/agents/results/INCONSISTENCIES.md class 2, which recorded "only the registration commit 1e8203c and an outcome bullet".]`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY
- **Companion RECORD EDIT (phase C)**: `docs/agents/results/RUBRIC-512-R.json`, append to `brackets`:
  `{"date": "2026-09-23", "by": "CORRECTIONS_2026-09-23 (registrar)", "text": "[CORRECTED 2026-09-23 by the registrar: registration.program_lines pointed at the outcome bullet and the B4 table row because the registration text was thought absent. The registration of record is docs/judge_improvement_proposals.md L337 (HEAD e422daa) '### RUBRIC-512-R — cell rubric value for the REASONING judge (~8k grok-reasoning calls)', added by 1e8203c, the only file that commit touched.]"}`
  and add to `sources`: `docs/judge_improvement_proposals.md L337-L346 (registration 1e8203c)`. STATUS: READY.

### C2-4 — MATCH-FILTER (a bullet, not a registration)
- Registration of record: `docs/judge_v2_program.md` L1047 (HEAD e422daa), the bullet
  `- **MATCH FILTER shipped as an option (2026-09-14).**` (commit 7155bea). The rule it ships came from
  the SCHEDULING probe (same file, L894). No `## Registered` section exists and none is to be written.
- **TEXT** (one line inside C2-0):
  `- MATCH-FILTER was never a "## Registered" section: it is the shipped-option bullet "- **MATCH FILTER shipped as an option (2026-09-14).**" in this file (7155bea), and the rule it implements is the SCHEDULING probe's, bullet "- **SCHEDULING (2026-09-13, zero calls): the match scheduler IS the problem, and the fix needs no answer key.**"; the criteria of record are the gates named in that bullet (307 tests green, stage-0a replay bit-identical with the filter off), not a pre-registration.`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

### C2-5 — SCHEDULING (a bullet, not a registration)
- Registration of record: `docs/judge_v2_program.md` L894, the bullet
  `- **SCHEDULING (2026-09-13, zero calls): the match scheduler IS the problem, and the fix needs no answer key.**`
  (commit 3f13911). Zero calls; readout `experiment_results/x12_crossdomain/scheduling_probe.txt`.
- **TEXT** (one line inside C2-0):
  `- SCHEDULING is a zero-call exploratory probe recorded as the bullet "- **SCHEDULING (2026-09-13, zero calls): the match scheduler IS the problem, and the fix needs no answer key.**" (3f13911), output experiment_results/x12_crossdomain/scheduling_probe.txt; it has no pre-registration and none is owed, and its headline was reproduced independently in Kotlin by MATCH-FILTER's plan harness (16.9%) and on the board by FILTER-BOARD.`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

### C2-6 — ABSTAIN (a bullet, not a registration)
- Registration of record: `docs/judge_v2_program.md` L986, the bullet
  `- **ABSTAIN (2026-09-13, zero calls): NEGATIVE - confidence-gated abstention does not beat answering.**`
  (commit a42dd82); output `experiment_results/x12_crossdomain/abstain_outcome.txt`.
- **TEXT** (one line inside C2-0):
  `- ABSTAIN is a zero-call exploratory bullet, "- **ABSTAIN (2026-09-13, zero calls): NEGATIVE - confidence-gated abstention does not beat answering.**" (a42dd82), output experiment_results/x12_crossdomain/abstain_outcome.txt; it carries no pre-registered criterion, and the CLOSED status of confidence gating in CONTEXT.md section 5 rests on it together with REF-CONF and J2-D, not on it alone.`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

### C2-7 — REF-SC (a free check, not a registration)
- Registration of record: `docs/judge_v2_program.md` L534, the bullet
  `- **REF-SC free check (2026-09-10 20:15, zero calls): self-consistency of the same reference model is NOT a`
  (commit 4dfa56c). Output of record `experiment_results/judge_solve/refsc_free_check.txt` (the ledger's
  evidence cell cites the bare file name; that path correction is class 7 and belongs to the ledger pass,
  not here).
- **TEXT** (one line inside C2-0):
  `- REF-SC is a FREE CHECK, not a registered test: the bullet "- **REF-SC free check (2026-09-10 20:15, zero calls): self-consistency of the same reference model is NOT a" (4dfa56c), output of record experiment_results/judge_solve/refsc_free_check.txt; its 0.94 is a two-solve agreement between two DIFFERENT protocols of the same reference model and is quoted as a null elsewhere in this file with that qualification.`
- **KIND**: PROGRAMME EDIT — **STATUS**: READY

**Class 2 tally:** 1 programme append carrying 7 pointer lines + 1 record edit (RUBRIC-512-R bracket) =
**8 corrections, all READY, 0 UNDETERMINED.**

---

## Class 4 — tests with no review file (`docs/reviews/` starts 2026-09-17)

Verified at HEAD: `docs/reviews/` holds 11 post-run review files (earliest
`2026-09-17_zero_call_batch.md`) and 8 `READY_*.md` files; there is **no README**.

Counted over all 142 records in `docs/agents/results/`: **24** cite a file under `docs/reviews/`, **1**
(TOPIC-PARTITION-20NG) is `review: null` because it is registered-and-READY but not yet run, and
**117** are pre-2026-09-17 rows with no dedicated review file. **All 117 already carry a provenance
sentence in `review.file`** — the backfill wrote them. So class 4 needs **zero record edits**; the only
missing artefact is the pointer the backlog asked for.

The 117, grouped by the provenance sentence each record carries (this is the list the backlog asked for;
the sentence is quoted once per group):

**(a) 15 records — "no separate review file; the checker's reading is the Block 1 build-time adversarial check."**
Sentence of record carried by each: `no separate review file (pre-dates docs/reviews/); each Block 1 test was 'adversarially checked' at build time and the checker's number wins where it refutes the builder (Block 1 record header L3662-L3663); the checker-confirmed defects are listed in the bullet`
A-REDEFINE-REFIT, CERT-CORPUS, CHECKER-ANSWER-INGEST, COST-AXES-INGEST, EPOCH-NULL, FOREIGN-GATE-D4,
FRONTIER-FIT, K-RECONCILE, KTD-CHECK, MAXT-MULTIPLICITY, POOLED-RESTATE, PROFILE-INTERVAL-ALL,
REF-QUAL-GATE3-COND, ROUTING-ATTENUATION, UNFILTERED-ADOPT.

**(b) 4 records — "no separate review file; the checker's reading is inside the outcome bullet."**
Sentence of record: `no separate review file (pre-dates docs/reviews/); the independent checker's recomputation recorded inside the outcome bullet (check_*.py scratch scripts named there; 'every number reproduced; verdict labels corrected by the checker where the builder's rested on an unregistered reading')`
ANCHOR-PROFILE-INTERVAL, JUDGE-TRANSFER, KEY-NOISE-CEILING, KEY-SUBANCHOR-SCALE.

**(c) 64 records — "no separate review file; the checker's reading is the named successor test / instrument gate."**
Each carries `no separate review file (pre-dates docs/reviews/); <the successor or gate>` with its own
successor named (e.g. GROK-CALIB → JUDGE-WIRING-BOARD then ITEM-26-POOLED; STACK-NORUBRIC → the Block 2
dry-run review 1e3b1ea; J6 → the pool-pin audit of 2026-09-14):
ABSTAIN, AGGREGATE, ANCHOR-FREE, ANCHOR-FREE-CERT, ANCHOR-FREE-FULL, ANCHOR-FREE-MCS, ANCHOR-FREE-Z,
ARENA-V2-X20, ARENA-V3-COMPILED, ARXIASK, DECOMP, DESIGN-PROBES, ENSEMBLE-REF, ESCALATE-LLAMA-LAW,
FILTER-BOARD, FLIP-PROV, FORMAT-REF, FRONTIER, GEN-ARENA, GPQA-HEADROOM, GROK-CALIB, H9-REM-FLAG, J6,
JUDGE-2x2, JUDGE-FINISH-AUDIT, JUDGE-SWAP, JUDGE-WIRING, JUDGE-WIRING-BOARD, LEAF-POWERED, MATCH-FILTER,
MATH-FIX, MC-LEAF, MC-ROUTER, NEWCOMER-PLACEMENT-LIVE, ORACLE, ORACLE-BOARD, ORDER-1, PERF-8-MEMO,
POINTWISE, POINTWISE-REPL, POSITION-DECOMP, POSITION-FULL, PROMPT-AUDIT, RECIPE-GROK, REF-CHECKLIST,
REF-GATED-RUBRIC, REF-QUAL-KIMI, REF-QUAL-KIMI-JSON, REF-SC, REGEN, RK-1, RK-1c, ROUTER-REGRET-MMLU,
RUBRIC-512-R, RUBRIC-HIDDEN, SCHED, SCHEDULING, SPLIT-FUNCTION-IMPL, SPLIT-RATIO-SEEDS, STACK-NORUBRIC,
STACK-v2, STAGE3-MATH, STAGE3-MATH-CAPFREE, SYSTEMATIC-SIGNAL.

**(d) 14 records — "no separate review file; no checker's reading is recorded anywhere."**
Sentence of record, verbatim and complete: `no separate review file (pre-dates docs/reviews/)`
BOARD-W, FORMAT, HYBRID, J1-R, J2-D, L1-V2, MC-BUILD, MC-FED, MC-ROOT, PAIR-NOREF, REF-CONF,
SELECTIVE-ORDER, STACK, TEMP-0.
These 14 are the honest gap of the programme: nothing independent re-read them. They need no edit (the
sentence is already the truth), but they are the list a reader should be handed when asking "what was
never checked".

**(e) 20 records — no dedicated review file, but a named adversarial instrument other than a successor test.**
Each names the ledger audit of 2026-09-14, `docs/review_session_2026-09-14.md` (ba12200), or its own
in-row correction chain: ARENA-13, ARENA-V2, ARENA-V3, BUDGET-LOMO, BUDGET-TRANSFER, CONSENSUS-FIT,
FRAMEWORK, KEY-TIE-DECLINE, LOW-AGREEMENT, MC-E2E, N4-RECONCILED, PLACEBO-ENTRY, PROFILE-RELIABILITY,
PROFILE-RELIABILITY-X20, PROFILE-TREE-ROBUST, RK-1b, RK-1b-GROK, SPLIT-RATIO, SYSTEMATIC-BUDGET,
TIER-HONEST-X20.
Note for phase C: KEY-TIE-DECLINE's sentence is the one to read twice — it says *"NOT adversarially
checked at outcome time"* and names KTD-CHECK as the independent check of record.

### C4-1 — the pointer file
- **WHERE**: `docs/reviews/README.md` — **does not exist** (verified: `ls docs/reviews/`).
- **ANCHOR**: none; new file.
- **TEXT** (the whole file):
  `# docs/reviews — what is here, and what stands in for it before 2026-09-17`
  ``
  `This directory starts on 2026-09-17. Every post-run review from that date forward is a file here (` `2026-09-DD_<subject>.md` `), and every pre-run reviewer verdict is a` `READY_<subject>.md` `.`
  ``
  `For any row adjudicated BEFORE 2026-09-17 there is no file here, and its absence is not a missing review. The check of record for those rows is one of five things, and each record in` `docs/agents/results/<ID>.json` `names which in its` `review.file` `field:`
  ``
  `1. the Block 1 build-time adversarial check (the checker's number wins where it refutes the builder; programme "Block 1 record header"), 15 rows;`
  `2. the independent checker's recomputation recorded inside the outcome bullet itself (the` `check_*.py` `scratch scripts named there), 4 rows;`
  `3. a named successor test or instrument gate that re-read the number, 64 rows;`
  `4. nothing — no independent re-reading exists; the record says exactly "no separate review file (pre-dates docs/reviews/)" and nothing more, 14 rows (BOARD-W, FORMAT, HYBRID, J1-R, J2-D, L1-V2, MC-BUILD, MC-FED, MC-ROOT, PAIR-NOREF, REF-CONF, SELECTIVE-ORDER, STACK, TEMP-0);`
  `5. the ledger audit of 2026-09-14 or the adversarial review session` `docs/review_session_2026-09-14.md` `(ba12200), 20 rows.`
  ``
  `Do not read "no review file" as "unreviewed": read the record's` `review.file` `sentence, which is the provenance of record. Counted 2026-09-23 over the 142 records then in` `docs/agents/results/` `: 24 cite a file here, 1 is not yet run, 117 fall into the five classes above.`
  ``
  `[Written 2026-09-23 by the registrar as the class-4 pointer of docs/agents/results/INCONSISTENCIES.md (8eeddaf). Pointer only: no number here is new, and no record was changed to create it.]`
- **KIND**: NEW FILE — **STATUS**: READY

**Class 4 tally: 1 correction (the README), READY; 0 record edits needed (117 records verified already
compliant); 0 UNDETERMINED.**

---

## Class 5 — run-time script identity not pinned (PIN)

Method used for every sha below, stated once: the sha of record for a file at a commit is the **LF
(git blob) rendering**, `git show <commit>:<path> | sha256sum`, first 16 hex. A script that hashed its
own bytes at run time hashed them **as they were on disk in the checkout it ran from**, which may be
either rendering; the CRLF one is reproduced by
`git show <commit>:<path> | sed 's/$/\r/' | sha256sum`. Both commands were run read-only to produce the
values below; no file was modified.

**A recorded sha is meaningless without its rendering named, and the rendering is NOT uniform across
this programme.** [ADDED 2026-09-23 after the coordinator settled C5-1.] Three worked examples in this
very class disagree with one another:
- **GROK-CALIB** pinned **e168b41c3e7ca4b8** into its cache — the **LF** rendering of the blob at
  7076615 (whose CRLF rendering is 6556066d3169e8b1, a different value entirely);
- **AGENT-CORPUS-ADMISSION** printed **7108cac91869dc88** — the **CRLF** rendering of the blob at
  33593af (LF: 798c03c2d0a83887);
- **PLACEMENT-CEILING** printed **8fe92a98b789bf7d** — the **CRLF** rendering of the blob at eb5791c
  (LF: fd9a890eb4e552b6).
All three were produced by the same idiom (`sha256(open(__file__, "rb").read())`), so the difference is
the checkout the script ran from, not the code. **Consequence binding on phase C: every bracket that
carries a recorded sha must say which rendering it is, and must not assume CRLF because the platform is
Windows.** The test is cheap and decides it: compute BOTH renderings of the candidate blob and see which
one the record's number equals; if neither matches, the bytes were uncommitted and the bracket says so
(as C5-2's a55f6e72913b95d3 does).

### C5-1 — GROK-CALIB: run-time script version — **READY** [SETTLED 2026-09-23, was UNDETERMINED]
- **[SETTLED 2026-09-23 by the coordinator's read-only query, reported to the registrar and recorded
  here.]** The cache carries the pin after all, and it identifies the blob exactly.
  `sqlite3 "file:experiment_results/x12_crossdomain/grok_calib.db?mode=ro&immutable=1" "select key, value from meta"`
  returns exactly one sha key, `script_sha256_16 = e168b41c3e7ca4b8`, and **no**
  `script_sha256_16_relaunch` (so the file was not edited between first launch and the last resume).
  Matched against every commit of `tools/analysis/grok_calib.py` in both renderings:
  1e3b1ea LF 8396be25d17ef4da / CRLF 0ca57fe88fea355d; **7076615 (2026-09-16 02:31) LF
  e168b41c3e7ca4b8 / CRLF 6556066d3169e8b1**; 13f2142 LF 7a1466c55f550004 / CRLF 0a464a0814b39f65;
  706b381 LF ebc7979c58efa56b / CRLF ec986d1b850f7af9 (= today's working tree).
  **The script of record for GROK-CALIB is the blob at 7076615, and the cache recorded its LF
  rendering** — the same commit that holds STACK-NORUBRIC's posting version (C5-2), which is consistent
  with both runs coming out of the same Block 1/2 window of 2026-09-16.
- Context kept from the first pass: `experiment_results/x12_crossdomain/grok_calib_outcome.txt` prints
  **no** producing-script sha (verified by grep across `experiment_results/x12_crossdomain/*.txt`: only
  escalate_llama_law, newcomer_placement, newcomer_placement_steps, placement_ceiling, ref_checklist and
  stack_norubric print one), which is why the pin had to be read from the cache; `grok_calib.py` L191
  writes `("script_sha256_16", script_sha())` at first launch and L200-L203 would write
  `script_sha256_16_relaunch` on an edit.
- **WHERE**: `docs/agents/results/GROK-CALIB.json`, `brackets` (RECORD EDIT). Do **not** bracket the
  programme: the programme prints no sha for this run, so there is nothing there to qualify.
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar: script.sha16 8396be25d17ef4da is the sha of tools/analysis/grok_calib.py at 1e3b1ea, the Block 2 dry-run commit, and is an IDENTITY, not the run-time pin. The run-time pin was read from the cache at zero calls: sqlite3 "file:experiment_results/x12_crossdomain/grok_calib.db?mode=ro&immutable=1" "select key, value from meta" returns script_sha256_16 = e168b41c3e7ca4b8 and no script_sha256_16_relaunch, i.e. the file did not change between first launch and the last resume. e168b41c3e7ca4b8 is the LF rendering of the blob at commit 7076615 (2026-09-16 02:31; its CRLF rendering is 6556066d3169e8b1, and the LF shas at 1e3b1ea / 13f2142 / 706b381 are 8396be25d17ef4da / 7a1466c55f550004 / ebc7979c58efa56b, none of which match in either rendering). The script of record for the 18,284 calls of GROK-CALIB is therefore tools/analysis/grok_calib.py at 7076615, sha16 e168b41c3e7ca4b8 (LF); the rendering is named because it is not uniform across this programme — the same idiom recorded a CRLF sha for AGENT-CORPUS-ADMISSION and PLACEMENT-CEILING.]`
- **STATUS**: READY

### C5-2 — STACK-NORUBRIC: the stale pin — **READY, and the "current" sha is now identified**
- Established by command. The outcome file line 7 reads:
  `producing script sha256 (pinned at first launch) a55f6e72913b95d3 | current d99610c5ce1c7999   <- STALE: the cache was judged by a different version | started 2026-09-16 02:30:21 | resumed 2026-09-16 02:30:30; 2026-09-16 02:30:46; 2026-09-16 02:31:32`.
  Hashing `tools/analysis/stack_norubric.py` at each candidate commit:
  1e3b1ea → 4ed7d7f5a702083e; **7076615 → d99610c5ce1c7999**; 13f2142 → c851e57ddb7387b4;
  7d11c4e → fd052323d5064135 (all LF, `git show <c>:tools/analysis/stack_norubric.py | sha256sum`).
  So the version that posted every verdict is **exactly the blob at 7076615** (committed 2026-09-16
  02:31:47, sixteen seconds after the last resume). `a55f6e72913b95d3` matches no commit, LF or CRLF —
  it is an uncommitted intermediate, and per the programme's own provenance note it *posted nothing*.
- **WHERE**: `docs/judge_v2_program.md`, the STACK-NORUBRIC outcome section (PROGRAMME EDIT)
- **ANCHOR**: `unaffected; the pin should have been taken at the first launch that posted.`
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar (identification only, no number changes): the "current" sha d99610c5ce1c7999 is now named — it is the LF sha256 of tools/analysis/stack_norubric.py at commit 7076615 (git show 7076615:tools/analysis/stack_norubric.py | sha256sum, first 16 hex), committed 2026-09-16 02:31:47, sixteen seconds after the cache's last resume at 02:31:32. That blob is the script of record for every verdict in stack_norubric.db. The pinned a55f6e72913b95d3 matches no commit in either rendering: it is the uncommitted intermediate whose first launch errored 36 jobs before any call, as this note already records.]`
- **Companion RECORD EDIT**: `docs/agents/results/STACK-NORUBRIC.json` — append to `brackets` the same
  sentence, and note in `sources` that `script.sha16` of the RUN is d99610c5ce1c7999 at 7076615 while the
  4ed7d7f5a702083e currently in the field is the dry-run identity at 1e3b1ea.
- **STATUS**: READY

### C5-3 — CAP-PRUNE: af176a2 vs 415c0fa — **READY, and the direction in the record is the wrong way round**
- Established by command. Commit times: `e803cf4` 2026-09-18 03:00:26 (registration), `415c0fa`
  03:14:06 (the script, dry-run only, `--run` deferred to W2), `af176a2` 03:56:09 (the pre-run review
  brackets, whose own message says *"trunk constant swapped in the script"*), run 2026-09-18 **17:20**,
  outcome `17a4434` 17:51:25. `git log --follow -- tools/analysis/cap_prune.py` returns exactly two
  commits, af176a2 and 415c0fa; af176a2 is the later and the last. Shas:
  415c0fa → **1f6ed45d9ccbcabe**, af176a2 → **77c3e6912b4db3c8** (LF); the working-copy file today is
  77c3e6912b4db3c8 (`sha256sum tools/analysis/cap_prune.py`, CRLF-free in this file's case, equal to the
  af176a2 blob). Therefore the bytes that ran at 17:20 are af176a2's, not 415c0fa's.
- **WHERE**: `docs/judge_v2_program.md`, the CAP-PRUNE outcome section (PROGRAMME EDIT)
- **ANCHOR**: `path; the null's seed stream; builder disclosure): tools/analysis/cap_prune.py --run (415c0fa), 2026-09-18 17:20 in window`
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar (script identity only; no result changes): "--run (415c0fa)" names the commit that ADDED the script, not the bytes that ran. 415c0fa (2026-09-18 03:14:06) is dry-run only; af176a2 (03:56:09) is the later and LAST commit of tools/analysis/cap_prune.py and its own message records that it swapped TRUNK_LITERAL / TRUNK_BESIDE in the script; the run is 17:20, after it. The script of record for this run is therefore the blob at af176a2, sha16 77c3e6912b4db3c8 (git show af176a2:tools/analysis/cap_prune.py | sha256sum), not 1f6ed45d9ccbcabe at 415c0fa. git log --follow on the file returns those two commits and no other, so no third version can be the run's.]`
- **Companion RECORD EDIT**: `docs/agents/results/CAP-PRUNE.json` — append the same bracket; the
  `script` block currently reads sha16 `1f6ed45d9ccbcabe`, commit `415c0fa (run of record; the file's
  last commit af176a2 carries the TRUNK_LITERAL / TRUNK_BESIDE id swap of the pre-run bracket)`, which
  states the two commits correctly but assigns "run of record" to the wrong one.
- **STATUS**: READY

### C5-4 — RECIPE-GROK: first-commit sha carried, run-time version — **UNDETERMINED**
- Established. `tools/analysis/stack_judge.py` history (with commit times):
  55a24c7 2026-09-10 00:51:55 → e9ec2996385aafd8; 83d2484 02:04:33 → bc16651d483a4a03;
  4320056 13:54:16 (*"--judge grok (RECIPE-GROK) and --all-x12 (ARENA-V2)"*) → 92629873df81ec14;
  1802c51 14:22:17 (*"RECIPE-GROK and ARENA-V2 analysis paths"*) → 98c77d260f9e5ac1;
  4cb39ac 2026-09-11 11:26:04. The outcome bullet is timed 15:00; the cache
  `experiment_results/x12_crossdomain/stack_v2_promptv2_grok.db` has mtime 2026-09-10 14:56. The script
  has **no** `meta` table and writes no sha (verified: `grep -n "script_sha\|meta\b\|CREATE TABLE"
  tools/analysis/stack_judge.py` returns only the `verdicts` table), and the outcome file prints none.
- What would settle it: nothing in the record does. Only a launch log with a timestamp for the posting
  run (none is committed for 2026-09-10) or a per-row provenance column in the cache (there is none)
  could. The run cannot have preceded 4320056 (the `--judge grok` flag did not exist before it), so the
  posted bytes are 4320056's or 1802c51's or an uncommitted intermediate.
- **WHERE**: `docs/agents/results/RECIPE-GROK.json`, `brackets` (RECORD EDIT). No programme bracket: the
  programme prints no sha for this run.
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar: run-time script version NOT RECORDED and not recoverable. script.sha16 e9ec2996385aafd8 is the LF sha256 of tools/analysis/stack_judge.py at 55a24c7, the script's FIRST commit, and is an identity only. The --judge grok path did not exist before 4320056 (2026-09-10 13:54:16, sha16 92629873df81ec14), so the run is at or after it; the next commit 1802c51 (14:22:17, sha16 98c77d260f9e5ac1) added the RECIPE-GROK analysis path and precedes the cache's last write (stack_v2_promptv2_grok.db, mtime 2026-09-10 14:56) and the 15:00 outcome. stack_judge.py writes no meta table and no script sha, and the outcome file prints none, so which of those two blobs (or an uncommitted intermediate) posted the verdicts is UNDETERMINED and no further evidence exists in the record.]`
- **STATUS**: UNDETERMINED (bracket itself READY to apply; it records the indeterminacy).

### C5-5 — L1-V2: first-commit sha carried where the run-time sha IS determinate — **READY**
- Established. `tools/analysis/causal_length.py` history: cc8b42c 2026-09-09 15:33:56 →
  **544fc300f6d5aebe**; 2034c9f 2026-09-10 00:58:48 (*"L1-V outcome: reference dents the elaboration
  vulnerability"*, the commit that carries the `--prompt v2` path) → **7a1241ddc3e55067**; 2034c9f is the
  file's **last** commit (`git log --follow`), so the working copy has not changed since. The L1-V2 run
  is 2026-09-10 01:25-01:58 (from the record's own `go` field), entirely after 00:58:48 and with no later
  commit possible. The run-time bytes are therefore 2034c9f's.
- **WHERE**: `docs/agents/results/L1-V2.json` (RECORD EDIT). No programme bracket (no sha printed there).
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar: the script block named commit 2034c9f but carried 544fc300f6d5aebe, which is the sha of tools/analysis/causal_length.py at cc8b42c, the FIRST commit. The run-time sha of record is 7a1241ddc3e55067 = git show 2034c9f:tools/analysis/causal_length.py | sha256sum, first 16 hex. This one is determinate, not an identity: 2034c9f (2026-09-10 00:58:48) carries the --prompt v2 path and is the file's LAST commit, and the run is 01:25-01:58 the same night, so no other version can have posted.]`
- **STATUS**: READY

### C5-6 — STACK: run-time version — **UNDETERMINED, with the timestamps that bound it**
- Established. Cache of record `experiment_results/x12_crossdomain/stack_v2.db` (named in the programme's
  STACK outcome, *"Cache experiment_results/x12_crossdomain/stack_v2.db, output stack_outcome.txt"*),
  filesystem mtime **2026-09-10 02:01**; outcome bullet timed 02:10; script commits 55a24c7 00:51:55
  (sha e9ec2996385aafd8) and 83d2484 02:04:33 (*"--prompt v2 arm (separate cache)"*, sha
  bc16651d483a4a03). The cache's last write precedes 83d2484 by three minutes, so the posted bytes are
  55a24c7's or an uncommitted intermediate between 00:51 and 02:01. A working-copy mtime is weaker
  evidence than a pin and is named as such.
- What would settle it: nothing. `stack_judge.py` has no meta table (same verification as C5-4) and no
  launch log for 2026-09-10 is committed.
- **WHERE**: `docs/agents/results/STACK.json`, `brackets` (RECORD EDIT).
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar: run-time script version not recorded. script.sha16 e9ec2996385aafd8 is the LF sha256 of tools/analysis/stack_judge.py at 55a24c7, its first commit, and is an identity. Bounding evidence, named for what it is: the cache of record experiment_results/x12_crossdomain/stack_v2.db has a working-copy mtime of 2026-09-10 02:01, three minutes before the next commit of the script (83d2484, 02:04:33, sha16 bc16651d483a4a03), and the outcome is timed 02:10; so the posted bytes are 55a24c7's or an uncommitted intermediate between 00:51 and 02:01. stack_judge.py writes no script sha into its cache, so this cannot be closed from the record.]`
- **STATUS**: UNDETERMINED (bracket READY to apply).

### C5-7 — MC-E2E: script edited after the run — **READY**
- Established. `git show 9865009:tools/analysis/multicorpus_router_e2e.py | sha256sum` =
  **84c62136c711f37d**, which is the value the record already carries; the later edits (`--mathfix`, the
  clean-pool restriction, 13f2142) are named in the record's `script.commit` and in `sources`. Zero calls, [ID-ONLY 2026-09-23 (CLAIMS-SWEEP-BRACKETS, registrar): pool union paeec37aa28063c75; verified by id only, not by content; reviewed twins on this pool (reviews 1df2cf1, 8ebfa7a): 471 ids / 427 texts exact, 478 / 432 norm-v1 (GPQA 288, MMLU-Pro 185, MATH 3, BBH 2); see docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT) and L14455-L14487 (SPLIT-FOLLOWUPS).]
  so no cache pin is expected or missing. The correction needed is only that the programme /
  multi_corpus_design.md outcome does not say the file was edited afterwards.
- **WHERE**: `docs/multi_corpus_design.md`, the MC-E2E result section (DESIGN-FILE EDIT — the same class
  as a PROGRAMME EDIT for phase C: insertion only, append the bracket after the anchor sentence)
- **ANCHOR**: the heading line `## MC-E2E + MC-SEEDS result (2026-09-13, zero calls) — the deployed router holds; its magnitude is seed-sensitive`
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar (script identity only; no number changes): the script that produced this result is tools/analysis/multicorpus_router_e2e.py at 9865009, sha16 84c62136c711f37d (git show 9865009:tools/analysis/multicorpus_router_e2e.py | sha256sum). The file was EDITED AFTER this run — the --mathfix extractor and the clean-pool restriction landed later (13f2142) — so re-running today's working copy does NOT reproduce the numbers i [ID-ONLY 2026-09-23 (CLAIMS-SWEEP-BRACKETS, registrar): pool union paeec37aa28063c75; verified by id only, not by content; reviewed twins on this pool (reviews 1df2cf1, 8ebfa7a): 471 ids / 427 texts exact, 478 / 432 norm-v1 (GPQA 288, MMLU-Pro 185, MATH 3, BBH 2); see docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT) and L14455-L14487 (SPLIT-FOLLOWUPS).]n this section; the MATH-FIX section and the 2026-09-14 CORRECTION section below carry what those edits changed. Zero calls, so there is no cache pin to check.]`
- **STATUS**: READY

### C5-8 — AGENT-CORPUS-ADMISSION: the CRLF / LF mismatch — **READY, hypothesis confirmed exactly**
- Established by command. LF blob: `git show 33593af:tools/analysis/agent_admission_pilot.py | sha256sum`
  = **798c03c2d0a83887**. CRLF rendering:
  `git show 33593af:tools/analysis/agent_admission_pilot.py | sed 's/$/\r/' | sha256sum` =
  **7108cac91869dc88**, which is byte-for-byte the sha the programme prints, and equals
  `sha256sum tools/analysis/agent_admission_pilot.py` on the working copy today. So the two shas are the
  same file in two line-ending renderings; there is no second version and no defect in the run.
- **WHERE**: `docs/judge_v2_program.md`, the AGENT-CORPUS-ADMISSION run line (PROGRAMME EDIT)
- **ANCHOR**: `(33593af; script sha 7108cac91869dc88), 2026-09-18 03:20, zero LLM calls;`
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar (rendering, not identity): 7108cac91869dc88 is the sha256 of the file AS ON DISK in this Windows checkout, i.e. the CRLF rendering; the LF (git blob) sha of the same file at 33593af is 798c03c2d0a83887. Verified both ways: git show 33593af:tools/analysis/agent_admission_pilot.py | sha256sum = 798c03c2d0a83887 and the same piped through sed 's/$/\r/' = 7108cac91869dc88, equal to sha256sum of the working copy. One file, two renderings; the convention of record for records is the LF one.]`
- **Companion RECORD EDIT**: none needed — `docs/agents/results/AGENT-CORPUS-ADMISSION.json` already
  carries both values with the right labels; append the confirming bracket only if phase C wants the
  verification command on the record.
- **STATUS**: READY

### C5-9 — PLACEMENT-CEILING: the CRLF / LF mismatch — **READY, hypothesis confirmed exactly**
- Established by command. LF blob: `git show eb5791c:tools/analysis/placement_ceiling.py | sha256sum` =
  **fd9a890eb4e552b6**. CRLF rendering of the same blob = **8fe92a98b789bf7d**, equal to the sha the
  programme prints and to `sha256sum tools/analysis/placement_ceiling.py` today. The outcome file's own
  header confirms the mechanism: `placement_ceiling_outcome.txt` line 2 prints
  `producing script sha e460a379cefd7e2c, this script 8fe92a98b789bf7d` — i.e. the script hashes the
  on-disk bytes of whatever file it is, and `e460a379cefd7e2c` is the *other* script
  (`newcomer_placement.py`, which produced the cache it reads), not a second version of this one.
- **WHERE**: `docs/judge_v2_program.md`, the PLACEMENT-CEILING run line (PROGRAMME EDIT)
- **ANCHOR**: `tools/analysis/placement_ceiling.py --run (eb5791c; script sha 8fe92a98b789bf7d), 2026-09-18 in window W2,`
- **TEXT**: `[CORRECTED 2026-09-23 by the registrar (rendering, not identity): 8fe92a98b789bf7d is the sha256 of the file AS ON DISK (CRLF) in this Windows checkout; the LF (git blob) sha of the same file at eb5791c is fd9a890eb4e552b6. Verified: git show eb5791c:tools/analysis/placement_ceiling.py | sha256sum = fd9a890eb4e552b6, the same piped through sed 's/$/\r/' = 8fe92a98b789bf7d = sha256sum of the working copy. The "producing script sha e460a379cefd7e2c" printed beside it in placement_ceiling_outcome.txt is newcomer_placement.py, the script that produced the cache this one reads, not another version of this script.]`
- **STATUS**: READY

### Not in tonight's scope, named so phase C does not lose them
INCONSISTENCIES class 5 also lists **J6, RK-1, RK-1b** (no pool pin at run time, found by the pool-pin
audit at programme ~L2060) and "Block 2 scripts edited mid-window". Those are pool-identity, not
script-identity, and the task of 2026-09-23 named only the nine items above. They stay open and should be
carried into the phase-C list unchanged.

**Class 5 tally [RECOUNTED 2026-09-23 after C5-1 was settled]: 9 items — 7 READY (C5-1, C5-2, C5-3,
C5-5, C5-7, C5-8, C5-9), 2 UNDETERMINED (C5-4, C5-6), both of which have a READY bracket that records
the indeterminacy and its bounds.** Insertions if all are applied: 5 programme/design-file brackets + 6
record brackets = 11 (unchanged; C5-1's insertion was always one record bracket — only its content
moved from "not read" to the sha).
*Superseded count, kept for the audit trail: the first pass of this file read 6 READY / 3 UNDETERMINED,
with C5-1 UNDETERMINED pending the cache read. The read was done the same evening and is recorded above.*

---

## Class 9 — runs that pre-date the 4,000-match rule (RULE)

The rule, as CONTEXT.md §4 rule 5 states it and as plan Amendment 9 quotes it: *"ask before any judged
run above 4,000 arena **matches** (~8k calls)"*. The denominator is **matches**, and the "~8k calls" is a
parenthetical conversion at two calls per match (dual order), not a second threshold.

**Finding that corrects the backlog.** INCONSISTENCIES class 9 lists RK-1 / RK-1b / RK-1c / RK-1b-GROK /
REF-CONF as *"judged above the 4,000-match rule (~8k each)"*. They are not. Each judged **3,948 matches**
(RK-1b-GROK and REF-CONF: 7,912 calls = 3,956 matches), i.e. **under** 4,000 matches; the ~8k is the call
count, which is what the rule's own parenthetical predicts for a just-under-4,000-match run. The five
records already say "under the 4,000-match rule" and are right; it is the backlog line that is wrong.
Exhaustive check: `grep -l "above the 4,000-match rule" docs/agents/results/*.json` returns exactly four
records — ARENA-V2, ARENA-V2-X20, JUDGE-WIRING-BOARD and (in the negative, "would have needed") ARENA-V3
is separate; of those, JUDGE-WIRING-BOARD carries an explicit go (Amendment 3, the author's *"18000 on
grok should be ok"*), so **only two runs in the whole programme are over-rule without a go, and both
pre-date the rule.**

### C9-1 — ARENA-V2
- **WHERE**: `docs/agents/results/ARENA-V2.json`, field `go` (RECORD EDIT — replace by insertion: the
  existing sentence is kept and the clause appended; the field is a string, so phase C appends, it does
  not rewrite).
- **Go sentence the record should carry, verbatim**:
  `above the 4,000-match rule (9,144 matches / 18,284 calls); launched 2026-09-10 (4320056) before the rule's formal adoption in the plan of 2026-09-15, so NO GO WAS OWED AND NONE IS MISSING: the rule binds from 2026-09-15 forward and is not applied backward (registrar 2026-09-23, per docs/plan_2026-09-15.md and CONTEXT.md section 4 rule 5).`
- **STATUS**: READY

### C9-2 — ARENA-V2-X20
- **WHERE**: `docs/agents/results/ARENA-V2-X20.json`, field `go` (RECORD EDIT)
- **Go sentence, verbatim**:
  `above the 4,000-match rule (12,400 matches / 24.8k calls); registered and launched 2026-09-10 20:45 (e7b086e) before the rule's formal adoption in the plan of 2026-09-15, so NO GO WAS OWED AND NONE IS MISSING: the rule binds from 2026-09-15 forward and is not applied backward (registrar 2026-09-23, per docs/plan_2026-09-15.md and CONTEXT.md section 4 rule 5).`
- **STATUS**: READY

### C9-3 … C9-7 — the "~8k" rubric runs: RK-1, RK-1b, RK-1c, RK-1b-GROK, REF-CONF
- **WHERE**: the five records' `go` fields (RECORD EDIT, append-only).
- **Go sentences, verbatim, one per record** (each keeps the existing sentence and appends the clause):
  - RK-1: `under the 4,000-match rule (~8k calls, both arms fresh); 3,948 matches, i.e. UNDER the rule, whose denominator is matches and whose "~8k calls" is the two-calls-per-match conversion, not a second threshold; no go was owed (registrar 2026-09-23; corrects docs/agents/results/INCONSISTENCIES.md class 8eeddaf item 9, which listed this run as over-rule on its call count).`
  - RK-1b: `under the 4,000-match rule (~8k calls, both arms fresh); 3,948 matches, i.e. UNDER the rule, whose denominator is matches and whose "~8k calls" is the two-calls-per-match conversion, not a second threshold; no go was owed (registrar 2026-09-23; corrects INCONSISTENCIES 8eeddaf item 9).`
  - RK-1c: `under the 4,000-match rule (~8k calls + 1,667 verified solves); 3,948 matches, i.e. UNDER the rule, whose denominator is matches; the 1,667 reference solves are not arena matches and do not enter the count; no go was owed (registrar 2026-09-23; corrects INCONSISTENCIES 8eeddaf item 9).`
  - RK-1b-GROK: `under the 4,000-match rule (7,912 calls); 3,956 matches, i.e. UNDER the rule, whose denominator is matches; no go was owed (registrar 2026-09-23; corrects INCONSISTENCIES 8eeddaf item 9).`
  - REF-CONF: `under the 4,000-match rule (2,812 solves + 7,912 judge calls); 3,956 arena matches, i.e. UNDER the rule, whose denominator is matches; the 2,812 reference solves are not arena matches and do not enter the count; no go was owed (registrar 2026-09-23; corrects INCONSISTENCIES 8eeddaf item 9).`
- **STATUS**: READY (all five). Note for phase C: the five records need no change of substance — the
  appended clause only defends the existing "under" against the backlog line.

### C9-8 — the plan pointer the backlog asked for
- **WHERE**: `docs/plan_2026-09-15.md` (PLAN EDIT, amendments only, numbered and dated; the next free
  number at HEAD e422daa is **10**, Amendment 9 being the last).
- **ANCHOR**: the last line of Amendment 9,
  `experiment-manager schedules under it.`
- **TEXT**:
  `## Amendment 10 (2026-09-23) — the 4,000-match rule binds from 2026-09-15 forward; the two earlier over-rule runs named, so no reader takes them for violations (registrar, pointer only: no test, no call, no budget)`
  `Decided by: the registrar, 2026-09-23, on the class-9 item of docs/agents/results/INCONSISTENCIES.md (8eeddaf). Why: two runs in the record are above 4,000 arena matches with no recorded go, and a reader meeting them without this note would read a violated standing rule.`
  `1. THE RULE AND ITS DATE. "Ask before any judged run above 4,000 arena matches (~8k calls)" (CONTEXT.md section 4 rule 5). Its denominator is MATCHES; the "~8k calls" is the two-calls-per-match conversion under dual order, not a second threshold. It is first treated as standing in this plan, 2026-09-15 (L3-L4: "all 26 tests, including GROK-CALIB (~9,000 matches, above the 4,000-match rule — explicit go recorded here)"). It BINDS FROM 2026-09-15 FORWARD and is not applied backward.`
  `2. THE TWO EARLIER OVER-RULE RUNS, named here and nowhere treated as violations: ARENA-V2 (2026-09-10, 9,144 matches / 18,284 calls, launched at 4320056) and ARENA-V2-X20 (2026-09-10 20:45, 12,400 matches / 24.8k calls, registered and launched at e7b086e). Both pre-date this plan by five days. No go was owed and none is missing.`
  `3. THE OVER-RULE RUNS THAT DID CARRY A GO, for completeness: GROK-CALIB (9,144 matches / ~18,300 calls; the author's go recorded at L3-L4 and L44 of this plan) and JUDGE-WIRING-BOARD (18,246 calls; Amendment 3, the author's "18000 on grok should be ok"). ARENA-V3 (9,144 matches, 4.5x the rule) would have needed a go, never requested one, and was WITHDRAWN 2026-09-14 at zero calls.`
  `4. NOT OVER-RULE, recorded because a backlog line said otherwise: RK-1, RK-1b, RK-1c (3,948 matches each), RK-1b-GROK and REF-CONF (3,956 matches each) are all UNDER 4,000 matches. Their "~8k calls" is the rule's own conversion, not a breach. docs/agents/results/INCONSISTENCIES.md item 9 listed them as over-rule; that reading is corrected here and in the five records.`
  `Total bill of this amendment: 0 cce, 0 calls, 0 machine time. It authorises nothing and changes no standing rule; Amendment 9's ceiling for the night of 2026-09-23 is untouched.`
- **STATUS**: READY

**Class 9 tally: 8 corrections — 7 record `go` edits + 1 plan amendment — all READY, 0 UNDETERMINED.**

---

## Summary for phase C

| class | corrections | READY | UNDETERMINED | kinds |
|---|---|---|---|---|
| 2 (NO-REG) | 8 | 8 | 0 | 1 programme append (7 pointer lines) + 1 record bracket |
| 4 (NO-REVIEW) | 1 | 1 | 0 | 1 new file; 117 records verified already compliant, 0 edits |
| 5 (PIN) | 9 items → 11 insertions | 7 items (C5-1/2/3/5/7/8/9) | 2 items (C5-4, C5-6) | 5 programme/design brackets + 6 record brackets |
| 9 (RULE) | 8 | 8 | 0 | 7 record `go` edits + 1 plan amendment |
| **total** | **26 insertions over 25 items** | **24** | **2** | — |

*[RECOUNTED 2026-09-23: this table read 6 / 3 on class 5 and 23 / 3 on the total in the first pass;
C5-1 was settled the same evening by the coordinator's read-only cache query and moved to READY. The
superseded counts are left here rather than erased.]*

Of the 2 remaining UNDETERMINED: **C5-4 (RECIPE-GROK)** and **C5-6 (STACK)** cannot be settled from the
record at all — `stack_judge.py` writes no sha into its cache and no 2026-09-10 launch log is committed —
and their brackets are written to say so, with the timestamps that bound each, rather than to guess.
Both are "UNDETERMINED sha, READY bracket": phase C applies them without waiting for anything.

Estimated phase-C time to apply, at a registrar working from this file with no re-derivation:
- class 2: **~15 min** (one append, one record bracket, then the record's `sources` line)
- class 4: **~10 min** (one new file, verbatim)
- class 5: **~35 min** (9 anchors to grep, 11 insertions, 6 of them in JSON `brackets` arrays)
- class 9: **~25 min** (7 string appends in JSON, 1 plan amendment)
- `results_index.py` regeneration + `--check`, one commit per record change, `git log --oneline -1` and
  `git status --short` verification after each: **~25 min**
- **total ~1 h 50 min**. [UPDATED 2026-09-23: the "+~5 min for the GROK-CALIB sqlite read" this line
  first carried is spent — the read is done and C5-1 is READY, so the estimate stands at ~1 h 50 min
  with nothing left to look up.]

Nothing in this file is applied. No number here was computed: every sha is the output of the
`git show … | sha256sum` command printed beside it (or, for GROK-CALIB's `e168b41c3e7ca4b8`, the value
the cache's own `meta` table returned to the coordinator's read-only query, quoted in C5-1 with the
query), every timestamp is `git show -s --format='%ci'` or a filesystem mtime named as such, and every
count is a `grep`/`ls` over the files named.

---

## [STATUS 2026-09-23, appended by the registrar after phase C ran — this worksheet is no longer unapplied]

This file said "Nothing in this file is applied." That was true when it was written and is no longer true.
Nothing above this line is deleted or rewritten; this is the status of record, by insertion.

- **APPLIED at commit cd83eac** (insertion only, zero calls, nothing above rewritten, no recorded number
  moved): 22 items — C2-0 (container appended at the END of the programme, after the two BFCL-JUDGED-PILOT
  sections another registrar appended in the meantime) carrying C2-1, C2-2, C2-3, C2-5, C2-6, C2-7; C2-3's
  companion record bracket in RUBRIC-512-R.json; C4-1 (the new docs/reviews/README.md, plus a recount bracket
  at HEAD e962327: 145 records / 27 citing the directory, the 117 and the 15 / 4 / 64 / 14 / 20 classes
  unchanged and re-verified record by record); C5-1, C5-2, C5-3, C5-5, C5-7, C5-8, C5-9; C9-1 … C9-8.
  Every sha, commit and quoted heading was re-verified by command before it was written.
- **C2-4, REFUSED at cd83eac and SETTLED in the follow-up commit.** The worksheet's "(commit 7155bea)" for the
  MATCH FILTER bullet does not reproduce. RULING (coordinator, 2026-09-23): the commit of record is **3535d56**,
  the commit that WROTE the bullet (2026-09-14 00:17:23, ledger v64); 7155bea (2026-09-13 23:51:20) is the
  Kotlin commit that shipped the option (MatchFilter.kt +212, MatchFilterTest.kt +224), and its 17-line hunk in
  docs/judge_v2_program.md is the unrelated Probe B / Probe C section. The registrar's first refusal said
  7155bea "touched no file under docs/ at all"; that clause is WRONG and is superseded in the programme by a
  dated bracket beside the WITHHELD note, which is itself left standing. The seventh pointer line is now
  written, naming both commits in their distinct roles.
- **C5-4 (RECIPE-GROK) and C5-6 (STACK), the two UNDETERMINED items, are now APPLIED** in the follow-up commit,
  verbatim as quoted above and with one clause added on the coordinator's ruling: the gap is a FIXED DEFECT OF
  AN ERA, not bookkeeping — stack_judge.py of 2026-09-10 writes no meta table, no script sha and no per-row
  provenance, while grok_calib.py, canary_baseline.py, bfcl_judged_pilot.py and ifeval_response_oracle.py all
  write their own identity into the cache, which is why C5-1 could be settled and these cannot be.
- **A defect this worksheet created, measured and corrected as a class.** The four class-5 programme brackets
  are mid-file insertions, so they moved this file's line numbers: +0 up to old L3911, +1 to L6535, +2 to
  L6692, +3 to L6949, +4 below. 233 recorded pointers over four sources name a line below old L3911. They are
  corrected AS A CLASS by the programme's "## Line-shift map, appended 2026-09-23" section, by a bracket at the
  end of plan Amendment 10, by ledger stamp **v128** (pointer-only; no row, chip or number touched; audit OK,
  224 rows), and INDIVIDUALLY for the 19 records whose registration pointer the audit could verify against a
  quoted heading (16 off by exactly the map, 3 already stale before tonight: MULTI-SWE-ADMISSION L9801 ->
  L9858, TOPIC-PARTITION-20NG L10030 -> L10093, TOPIC-PARTITION-20NG-T1B-NULL L11525 -> L11542).
- **STILL OPEN, and NOT this file's scope:** INCONSISTENCIES classes **3, 6** (including the
  PROFILE-RELIABILITY-X20 `replace_chip` to PASS (corrected v93)), **7, 8** and **10** — the ledger half, which
  needs its own patch through `tools/analysis/ledger_patch.py`. The v128 stamp above is a pointer stamp only
  and settles none of them. Also still open, named in this file and out of tonight's scope: the pool-identity
  items J6, RK-1, RK-1b and "Block 2 scripts edited mid-window".
- **[UPDATED 2026-09-23 by the registrar, INCONSISTENCIES-PASS ledger half]** classes 3, 6 (incl. the PROFILE-RELIABILITY-X20 chip, appended rather than replaced), 7, 8 and 10 are APPLIED at ledger v132; the pool-identity items J6 / RK-1 / RK-1b are DISCLOSED in their rows with the read-only check left OPEN, and "Block 2 scripts edited mid-window" is identified (0ba096f) and OPEN on the caches' meta sha. Status of record: the STATUS section at the end of docs/agents/results/INCONSISTENCIES.md.
