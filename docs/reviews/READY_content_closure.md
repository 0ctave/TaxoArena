# READY review: CK-CLOSE-v1 Python half, `tools/analysis/content_closure.py`

Reviewer: adversarial-reviewer, 2026-09-23. Zero judge calls, zero builds, no file of record written.

## Verdict

**READY WITH CONDITIONS.** No blocker. Every real-data figure the builder claims reproduces to the digit from my own code: a component-reachability (BFS) closure that does not import the module and reuses only `split_side.stem_key` / `side_hash` / `norm`. The four conditions of 1df2cf1 are implemented as written, and 3,000 random instances agree with the independent closure (0 mismatches). There are three gaps. (1) Two of my mutants SURVIVE the builder's selftest: the fixed point with no family-of-moved step (R6), and a guard call that leaves out the sentinels (R4b, which also survives the p2dca audit). (2) The label-conflict counts 89 / 84 are answer-text differences, not label conflicts. (3) The queue item's READY list names "GPQA one row per stem_key", and the module has nothing for it (0 matches). Conditions C1-C4 are below. The module has no consumer (`git grep -c content_closure 45d31f0` finds only its own file), so a merge changes no pinned behaviour.

## Pins (kind named)

| object | pin |
|---|---|
| module @ 45d31f0 (worktree-agent-a75abd5e20b9d35c0) | blob:5324cbeaaa19cfcd575307a65123ed57070d5cb7 / sha256-lf16:966bc72730b295f2 (the LF rendering; the working tree is byte-identical, so no CRLF pin is needed) |
| commit scope | `git diff --name-only eba09f3 45d31f0 \| wc -l` = 1 (the module only; parent eba09f3) |
| split_side.py (key of record) | blob:05224b5a4b76e74353bc3931ec69f0b14f0e340b, identical on main and at 45d31f0 |
| pool_guard.py (open_ro) | blob:6521b51ac0fce04063563f9e6dcf42554ad86591, identical on main and at 45d31f0 |
| DBs read (sha256 before = after, mtimes unchanged; -wal 0 B, no -journal) | mmlu_pro_dataset_cache_v2.db 4f65414f7625a1e7..., multicorpus_cache_v1.db ad66e30a0eb4abd6..., bfcl_result_2025-12-16.db c5eddd267623f0ff..., multiswe_result_2026-09-22.db 3ce5179c3f5085d2... (full sha256) |
| not opened | snapshots_frozen.db; twenty_newsgroups_cache_v1.db (-wal 708,672 B, 09-23 04:30) |

## Reproduction table (own code: scratchpad `ck_close_ready/repro.py`, `mode=ro&immutable=1` after a -wal / -journal size check)

| figure | claimed | mine | |
|---|---|---|---|
| paeec moved | 543 | 543 | MATCH |
| by corpus GPQA / MMLU-Pro / MATH / BBH | 346 / 185 / 10 / 2 | 346 / 185 / 10 / 2 | MATCH |
| cross-corpus moves | 13 | 13 (MATH 10 twinned to MMLU-Pro reserved ids; MMLU-Pro 3 twinned to MATH reserved ids) | MATCH |
| reserved ids with a gen twin / keys | 478 / 432 | 478 / 432 | MATCH |
| within-reserved ids in twin groups | 215 (104 groups) | 215 (104 groups, 6,371 clusters) | MATCH |
| Kish all / GPQA | 1.0367 / 1.380 | 1.0367 / 1.3799 | MATCH |
| paeec train / gate after closure | 14,581 / 1,487 | 14,581 / 1,487 | MATCH |
| stem-only variants among the moved (no held twin has the same option set) | (not claimed) | 127 (MMLU-Pro 117, MATH 10); 334 moved are option-shuffled twins | moved, as the rule requires |
| p2dca moved | 171 = 75 + 96 | 171 = 75 twins of reserved ids + 96 twins of sentinels only | MATCH |
| p2dca test / train / gate / train excl. gate | 3,770 / 8,230 / 843 / 7,387 | 3,770 / 8,230 / 843 / 7,387 | MATCH |
| p2dca reserved ids with a gen twin | 70 (printed) | 70 | MATCH |
| BFCL p2035 moved; Kish key / family | 0; 3.377 / 4.000 | 0; 3.3772 / 4.0000 (81 key clusters, 57 families; 0 of 200 families span the sides) | MATCH |
| Multi-SWE p79fb moved; Kish family | 0; 37.76 | 0; 37.759 (16 repos; 0 of 51 span the sides) | MATCH |
| 20NG | SKIPPED | not opened (-wal 708,672 B) | as claimed, but see D9 |
| label-conflict groups paeec / p2dca | 89 (212 ids) / 84 (202 ids) | 89 (212) / 84 (202); 49 / 41 span the sides; 15 paeec groups hold two or more reserved ids | count MATCH, meaning REFUTED (D1) |
| guard refuses the unclosed split | paeec 543 ids over 432 keys; p2dca 171 over 151 | 543 / 151 unclosed twin ids / keys | MATCH, but it does not discriminate the sentinel arm (D2) |
| selftest | 26/26 under python and -O | 26/26 under python and -O | MATCH |
| builder's audit output | audit_final_5324cbe.txt | my rerun of `--audit` on all 5 pools is byte-identical to it except for CR (`diff --strip-trailing-cr`, 82/82 lines) and identical across PYTHONHASHSEED 0 and 12345 (`cmp`) | MATCH |

## Per-claim

| claim | result | evidence |
|---|---|---|
| key = `split_side.stem_key` of the stem, reused | CONFIRMED | `ck_key` calls `split_side.stem_key(value)` or `stem_key(value[0])`; options are dropped; the case-sensitive mutant R3 is killed (selftest 18/26; the p2dca audit reports gate 855 against 843 as a MISMATCH) |
| closure GLOBAL across the corpora of a build | CONFIRMED | `build_closure` makes one `closed_complement` call over the union; my synthetic cross-corpus chain moves g1 (A), g2 and g3 (B), g4 (C), while per-corpus calls move only g1; the real paeec figure is 13 cross-corpus moves |
| family closure iterated to a fixed point | CONFIRMED (code), PARTLY (test) | chain r to g1 (key, family F) to g2 (family F) to g3 (key) to g4 (family F2): all four move, with reasons twin_of_reserved / family_of_moved / twin_of_moved / family_of_moved in 5 rounds. 3,000 random instances against an independent BFS: 0 mismatches, 0 guard refusals on the closed side, at most 8 rounds. BUT mutant R6 (the family_of_moved branch deleted) SURVIVES the selftest (26/26, both modes): D3 |
| sentinels in the key set | CONFIRMED (closure), PARTLY (guard) | p2dca 96 sentinel-only moves; mutant R2 (sentinels passed as reserved) is killed by the selftest but SURVIVES the audit; mutant R4b (the audit's guard called without sentinels) SURVIVES both: D2, D5 |
| stem-only variant with another option set is moved | CONFIRMED | selftest g5; my case (d): a `("q?", ["x","y"])` and a list-typed pair both move; real data: 127 stem-only moves |
| reserved twins clustered, none dropped | CONFIRMED | every reserved id gets a cluster id (paeec n = 6,482 over 6,371 clusters); a duplicate-listed input keeps n = 3; mutant R8 (drop twins) killed |
| `assert_content_disjoint` raises SystemExit | CONFIRMED | an explicit `_refuse`, not an `assert`; it holds under -O (the selftest passes under -O, and mutant R9 is killed in both modes); it prints on pass and on fail |
| Kish labelled as an upper bound | CONFIRMED | `stats["bound"] = "DEFF at rho = 1 (upper bound), not a measured DEFF"`, printed on every line; Sum(n^2)/n is the DEFF at ICC 1, so it bounds the DEFF for ICC in [0, 1] |
| label_conflicts | PARTLY | the counts reproduce; what they measure does not (D1) |
| guard refuses the unclosed splits | CONFIRMED, weak | the refusal fires on reserved twins alone, so it proves nothing about the sentinel arm (D2) |
| 6 mutants x 2 modes killed | CONFIRMED | I reran them: `ck_close/mutants.txt` shows 12/12 |
| reviewer mutants (task 4) | 4 of 5 killed; R4b SURVIVES | R1 one round: killed (24/26). R2 sentinels as reserved: killed by the selftest, survives the audit. R3 case-sensitive: killed. R4a guard drops sentinel-convention ids: killed by the selftest, survives the audit. R4b guard call without sentinels: SURVIVES the selftest and the audit. R5 missing text silently skipped: killed. Extra mutants: R6 no family_of_moved: SURVIVES. R7 no twin_of_moved: killed. R8 twins dropped: killed. R9 guard ignores family: killed. R10 no target norm: killed (`ck_close_ready/mutants.out`) |
| safe at import | CONFIRMED | an import with `sqlite3.connect` and `open` instrumented records 0 calls; pool_guard is not imported (it is lazy, `_pg()`); the one side effect is `sys.path.insert(0, tools/analysis)` (D8) |
| deterministic | CONFIRMED for the printed audit; PARTLY for the API | the audit is byte-identical across hash seeds; `moved` (a dict) and `closed_gen` (a frozenset) are unordered for str ids (D8) |
| missing text is a refusal | PARTLY | a missing mapping entry and a callable returning None both refuse; an EMPTY stem is accepted, so every "" collapses to one key (D7) |
| "where to call it" list | UNDETERMINED | it is not in the commit message, the module, or the builder scratch (`grep -c "where to call\|consumer"` = 0 in the module; 0 files in ck_close/). Candidate consumers by grep: router_clean_policy.py (ROUTER-CLEAN-POLICY fit), multicorpus_router_e2e.py (MC-E2E), union_profile_home.py, profile_interval_union.py; part (b) is MMLUDatasetFetcher.finishSplit / TrainOnlyGuard.kt. No consumer is changed |

## Label conflicts (task 3)

Class counts over all groups come from `ck_close_ready/lc_sample.py` and `lc_detail.py`. On paeec, the 89 groups are:

- **2 real conflicts.** Identical BBH causal_judgement prompts with the same options and opposite labels: 1010032 / 1010119 No vs Yes, and 1010036 / 1010104 No vs Yes. Both texts are 763 / 770 characters, full-string equal.
- **4 artefacts from MATH vs MMLU-Pro formatting**, `\dfrac{..}` against `\frac{..}` (7741 / 2010014, 7744 / 2050088, 8170 / 2010114, 8182 / 2050015).
- **7 artefacts from punctuation only** (a trailing period or a comma).
- **76 MMLU-Pro groups whose option sets differ**, so the answer TEXT differs by construction.

On p2dca, the 84 groups are 7 punctuation-only artefacts, 0 groups with the same ordered options, and 77 with different option sets.

Random samples of 10 groups each (seed 20260923):

- **paeec, 0 of 10 real.** 3 artefacts (2 `\dfrac`/`\frac`, 1 trailing period). 7 paraphrases, granularities or synonyms across option sets (for example 'imprinting' against 'the lamb might have imprinted on mary...', and 'sweeping generalization' against 'dicto simpliciter').
- **p2dca, 1 of 10 real.** The cellulitis case: -1006328 has 10 options with key G 'Antibiotic therapy'; 6491 has 9 options, from which 'Antibiotic therapy' was REMOVED, so the key becomes F 'Amputation'. 1 of 10 is a key collision: the generic stem "Which of the following statements is correct?" merges 6 unrelated questions. 8 of 10 are paraphrases.

## Defects

- **D1 (MEDIUM). "Label conflicts" counts answer-text differences.** Of the 89 paeec groups, 11 are normalisation artefacts, 2 are genuine same-prompt contradictions, and the samples put the real rate at 0-1 in 10. Fix:
  - relabel the count as "answer-text differences within a stem key (an upper bound on label conflicts)";
  - print the classes (same ordered options / same option set / different option set; alnum-equal);
  - never record 89 / 84 as conflicts.
- **D2 (MEDIUM). The guard's sentinel arm depends on the caller.** `assert_content_disjoint` takes one merged set, and mutant R4b survives the selftest and the p2dca audit. The unclosed-split refusal fires on the 75 reserved twins either way. Fix:
  - the signature becomes `(train, reserved, sentinels, ...)` with `sentinels` required (an explicit empty set is allowed);
  - add an audit leg on p2dca: train = gen minus the reserved twins must REFUSE with 96.
- **D3 (MEDIUM). The key-twin to family step of the fixed point is untested.** Mutant R6 survives 26/26. The code is correct (the chain test and the property test above). Fix: add the chain r to g1 (key, F) to g2 (F) to g3 (key) to the selftest.
- **D4 (MEDIUM). The queue item CK-CLOSE-V1-IMPL `ready_file` requires the selftest to cover "GPQA one row per stem_key".** The module has no such function and no such test (`grep -c -i "one row\|subset tag\|dedup"` = 0). Fix: implement it with a test, or have the registrar descope it to the ingest owner by a bracket.
- **D5 (LOW). The audit RECORD does not pin p2dca's 75 / 96 split or res_with_gen_twin 70**, so mutant R2 passes the audit. Fix: add both figures.
- **D6 (LOW). `cross_corpus_moves` counts direct key twins only.** Chain moves across corpora count as 0 (the synthetic case (b): 3 moves, 0 reported). Fix: rename the field to "direct", or count by component.
- **D7 (LOW). An empty stem is not refused.** A `text_of` that yields "" collapses every such id into one key. Fix: refuse `norm(stem) == ""`.
- **D8 (LOW). Two API hazards.** `sys.path.insert` at import can shadow a consumer's module names. `moved` and `closed_gen` are unordered for str ids. Fix: document this, or return sorted tuples.
- **D9 (LOW). The 20NG branch returns 3 ("no loader") even when the -wal is clean.** The skip is permanent, not conditional on the WAL. The gate figures printed for BFCL / Multi-SWE come from stem hashes, although the engine hashes the family (the output says so). Fix: say "NOT IMPLEMENTED" for 20NG.
- **D10 (LOW, a property of the adopted rule, not the module). The options-free key merges distinct questions that share a generic stem.** 54 of the 543 paeec moves share no option with any held twin, and 21 of those have stems under 80 characters (for example "which of the following is true?", 4 ids). This errs toward over-closure and slightly inflates Kish. Name it in the rule's limits.

## Conditions

- **C1** (before merge): D3 selftest chain. Show R6 killed.
- **C2** (before merge, or before the first consumer): D2 explicit sentinel argument and the p2dca sentinel leg. Show R4b killed.
- **C3** (before any record cites the numbers): D1 wording and classes.
- **C4** (before the queue item is marked done): D4, implemented or descoped by the registrar.

D5-D10 are optional.

Scratch: `scratchpad/ck_close_ready/` holds repro.py, repro.json, lc_sample.py, lc_detail.py, conditions.py, mutants.py, mutants.out, mut/, and audit_*_{0,12345}.txt. Nothing was placed in the repo's tools/ (`git status --short tools/` is empty).

## Delta re-review 2026-09-23: fix commit 24dcc8c (inserted after the original review; nothing above is edited)

**Verdict: READY. MERGEABLE.** Conditions C1-C4 are lifted, and D5-D10 are addressed. Nothing blocking remains. Two new LOW notes (N1, N2) are optional.

### Pins

| object | pin |
|---|---|
| module @ 24dcc8c | blob:1533cb5a56c8e001ddc65d3e2ec0cc4b56aa87e3 / sha256-lf16:d362aad31f650cc0 (LF; the working tree is byte-identical, so no CRLF pin is needed) |
| scope | `git diff --name-only 45d31f0 24dcc8c` lists only tools/analysis/content_closure.py (+527 / -173); the parent is 45d31f0 |
| dependencies | split_side.py blob:05224b5a…, pool_guard.py blob:6521b51a…, unchanged from the original review |
| DBs | sha256, size and mtime of all four DBs read are unchanged after every run (-shm excluded); the 20NG DB was not opened |

### Checks

| check | result | evidence (scratchpad ck_close_ready/rr/) |
|---|---|---|
| selftest | 36/36 PASS under python and python -O; 0 FAIL lines | selftest_py.txt, selftest_O.txt |
| audits, 5 pools | rc 0/0/0/0 and 4 (20NG NOT IMPLEMENTED; its -wal is 708,672 B and the DB was not opened); 35 MATCH lines, 0 MISMATCH; byte-identical across PYTHONHASHSEED 0 and 999 | audit_*_{0,999}.txt |
| C1 key->family chain | CONFIRMED: a selftest check asserts c1 twin_of_reserved, c2 family_of_moved, c3 twin_of_moved, c4 family_of_moved, and that c5 stays; R6 is KILLED (34/36) | mutants_rr.out |
| C2 sentinel argument | CONFIRMED: `assert_content_disjoint(train, reserved, sentinel_ids, ...)` refuses `sentinel_ids=None`; ContentLeak.counts separates reserved and sentinel-only twins. The p2dca SENTINEL LEG REFUSES with 96 over 81 keys, 0 of them reserved. My own count, independent of the module (gen minus reserved twins, keyed against sentinel keys), is 96 / 81. R4a and R4b are KILLED by the selftest in both modes and by the p2dca audit ("PASSED (WRONG)", sentinel_leg 0 against 96) | repro2.py |
| C3 answer classes | CONFIRMED: my own classifier (repro2.py) gives paeec conflict 2 ([1010032, 1010119], [1010036, 1010104]) / formatting 4 / punctuation 7 / option sets differ 76, and p2dca 0 / 0 / 7 / 77, which matches the audit. A pairwise scan finds NO hidden conflict: no option_sets_differ group on either pool contains a same-option-set pair with a different answer. The count is labelled "an UPPER BOUND on label conflicts". R10 and new R11 (the conflict class never assigned) are KILLED by the selftest and the paeec audit | repro2.py |
| C4 one_row_per_key | CONFIRMED: GPQA 1,192 rows -> 546 stem keys, tag profiles diamond+extended+main 198 / extended+main 250 / extended 98; my count from corpus_questions.task gives the same. It cannot touch a pinned pool: it is a pure function returning a dict; the module has 0 write sites (`grep -cE "open(..'w'..)|INSERT|UPDATE|DELETE|CREATE|.write(|json.dump("` = 0); its only non-test caller is the audit's descriptive line (L843); an untagged copy is refused | grep |
| D5 | CONFIRMED: p2dca 75 / 96 / 70 are pinned and MATCH; R2 is now KILLED by the audit (75 against 171) | |
| D6 | CONFIRMED: direct 13 and component 13 on paeec; the selftest's chain case gives direct B 1 against component B 2, C 1 | |
| D7 | CONFIRMED: an empty stem is refused; new R13 (the check removed) is KILLED | |
| D8 | CONFIRMED: importing the module leaves sys.path unchanged, makes 0 sqlite3.connect calls, and does not load pool_guard; outputs are sorted tuples / dicts in sorted id order | |
| D9 | CONFIRMED: the 20NG audit prints NOT IMPLEMENTED and exits 4 | |
| D10 | CONFIRMED: over-closure paeec 54 / 21 (it matches the original review); p2dca 53 / 28, which my independent count also gives | repro2.py |
| where-to-call list | PARTLY: the sampled line references are accurate (router_clean_policy.py L346-L349 and L455-L458, multicorpus_router_e2e.py L86-L93, router_regret.py L35, MMLUDatasetFetcher.finishSplit L863 with callers L783 / L816, HeadlessBenchmarkRunner L1128). It OMITS TaxonomyJudgeService.kt L55 / L103, which also take getReservedQuestionTexts on the judge-prompt induction path (N2) | sed / grep |

### Mutants, ported by me onto 24dcc8c (mutants_rr.py)

I ported each mutant with an asserted replacement count and ran it in a scratch mirror holding copies of split_side.py, pool_guard.py and the registry and id files. Nothing was placed in the repo.

- **Harness control:** R0 (identity) PASSES 36/36 and the audit.
- **R1-R10:** all KILLED by the selftest under both python and -O.
- **R2, R3, R4a, R4b, R10:** also KILLED by the audit.
- **R6 and R9:** survive the BFCL and Multi-SWE audits only because those pools move 0 ids (no discriminating power there); the selftest kills both.
- **New R11 and R13:** KILLED.
- **New R12 SURVIVES** (the sentinel leg's own verdict `leg_ok` not folded into `ok`). On p2dca it is redundant with the pinned `sentinel_leg` figure, and in the selftest the audit check reads the REFUSED line (N1).

### New notes (LOW, optional)

- **N1:** `ok &= leg_ok` is untested (R12 survives). A new pool without a RECORD entry would rely on it alone. Fix: add a selftest check where the leg is expected to fail (for example, a synthetic pool whose sentinel twins the leg cannot see) and assert the audit returns not-ok.
- **N2:** the where-to-call list omits TaxonomyJudgeService.kt L55 / L103 (getReservedQuestionTexts feeds judge generation). Add it when the Kotlin item is scoped.
- Two untracked files, tools/analysis/split_exposure_child.py and split_exposure_sensitivity.py, are in main's tools/ and are not this reviewer's. My mutants live only in the scratchpad.
