# P4 (VFC-FIXES-2 (ii)/(iii)): ownership of "is '' NULL?", and the pre-data ruling

arena-specialist, 2026-09-26. Zero calls. No DB opened except `file:<abs>?mode=ro&immutable=1` with `PRAGMA query_only=1` (read back). Nothing of record written.
Sources: READY_vfc_fixes_2.md R2.5 (f387d58); RULING_vfc_ii_iii_pin.md P4 (93cc7de); READY_vfc_harness_v4.md step 5 (e256c23).
Code read at main b19b8fb: `tools/analysis/vote_frame_cert.py` blob:1a3d0bb5 (the f76a93b merge blob, sha256-lf16:b45b75db7d98103e per 93cc7de; not re-hashed here), `tools/analysis/rejudge_grok.py` blob:939de7c7, `src/main/kotlin/taxonomy/service/JudgeCallStore.kt` blob:785031c3.

## 1. Acknowledgement

I, the arena-specialist, am the named owner of the R2.5 question "is '' NULL?" for VFC-FIXES-2 (ii)/(iii). I accept it BEFORE any leg runs (P4, first bullet).
The builder and the run-operator do not default it. This file gives the answer before the data (section 2). So the "ALL ''" branch of R2.5 has an answer before the F1 readout is read, and (ii) never waits on me.

## 2. Ruling (pre-data, binding for (ii) and (iii))

**R-P4-1. '' is NOT NULL.** A stored label equal to the empty string is a real stored value outside every label space of record. It is therefore an UNRESOLVABLE label under R-1's letter.
- A unit whose deciding tally carries one or more '' labels is UNCERTIFIABLE (R6), as the build already does. `to_order1_frame('')` returns None (vote_frame_cert.py L1084-L1091); only `None` maps to INVALID (L1088).
- It is NOT mapped to INVALID. It is NOT dropped from the unit's row count.

**R-P4-2. Routing.** If the F1 readout shows a unit of record moving to R6 and its `unresolvable_values` are all '', the move is an ORDINARY R6 finding under R-5, scored like any other R6 move.
- (ii) is scored. It is NOT held for a further ruling: this file is that ruling.
- The finding line names: the unit (cache, table); the '' count on the deciding tally; how many of those rows have both votes decisive (`unresolvable_inf`); and the first 10 row keys.
- The finding goes to the data-steward, descriptively, to identify the writer path that stored ''. No cache is rewritten.

**R-P4-3. '' appearing at all is a second finding.** The census in section 3 finds zero '' today in every label-bearing column of every cache of record, and of every other SQLite file under experiment_results/** and the repository root.
- A '' in the legs' readout therefore means the enumerated bytes changed after 2026-09-26. That is a finding for the registrar against the F5 freeze (38ec2f3), in addition to R-P4-2.
- It does not change the class rule.

### Why '' is not NULL (evidence)

1. **No writer of record can emit '' as a label.**
   - The one parser, `rejudge_grok.parse_judge` (rejudge_grok.py L168-L197), returns only "Model A" / "Model B" / "TIE" / "INVALID": the default at L170, and the two `.get(raw, "INVALID")` maps at L179-L180 and L189-L190.
   - `combine_orders` (L200-L206) returns only those values.
   - Kotlin: `parsed_winner TEXT NOT NULL` (JudgeCallStore.kt L88) is filled from `res.winner` (TaxonomyArenaService.kt L572). The field is documented as the four values (JudgeCallStore.kt L32). Only `rawContent` defaults to "" (L572), which is raw text, not a label; `parse_judge("")` gives INVALID.
   - The name-labelled writers (arena13, placebo, newcomer_placement(_steps)) map these four values through the order's contestant map. They cannot produce ''.
   - So '' is not a value any recipe emits. Where it appears, a writer stored something outside its own vocabulary: a defect or placeholder that the instrument cannot interpret. That is exactly R6's meaning ("instrument knowledge, not frame").
2. **NULL and '' differ in what they record.**
   - NULL means the writer stored nothing. The instrument maps it to INVALID (L1088), not informative, and counted.
   - '' means the writer stored a value. Reading it as NULL is a new equivalence that no writer documents.
3. **Mapping '' to NULL fails open.** R2.5 already records the cost: on a row with both votes decisive, INVALID silently removes an informative row. That is the abf4db5 D4 denominator shrink again, and this arena's standing rule is that a row that errored is never absent from a denominator.
   - R6 is the fail-closed direction: the unit is excluded from every index by class (R-4), counted in P4 (R-5), and never certified on a subset (R-6).
   - The permissive reading could certify a unit on a subset. The conservative one cannot.
4. **Mapping it only on rows that are not decisive** would be a new rule, not in VFC-RX-RULING (R2.5, last bullet). I do not introduce one.

### Stated, NOT ruled here (outside the question: these are per-order votes, not the deciding label)
- vote_frame_cert.py L1215 `full = lambda v: v not in (None, "")` treats '' as ABSENT when it decides whether a WIDE row carries both orders (the NOT-DUAL-ORDER row-level rule). This ruling concerns labels on the deciding tally only and does not change L1215.
- A '' stored per-order vote under E-RAW (Tally.order1 / order2, L1108-L1129) equals neither the re-parse nor its transpose. It is therefore a contradiction under both hypotheses, so the table reads MIXED. That also fails closed.
- Both are moot on today's bytes (census: 0).

## 3. Census (read-only, 2026-09-26, main checkout)

Denominators: the 62 caches / 67 units of the certificate of record (`experiment_results/vote_frame_cert.json`, c731836), and every file under experiment_results/** (including _backup/) and the repository root whose first 16 bytes are the SQLite header (199 files).

| object | columns examined | '' | whitespace-only | NULL |
|---|---|---|---|---|
| 67 units of record (WIDE: combined column + vote1 + vote2(_raw); LONG: the vote column) | every label column of every unit, e.g. rubric_ladder winner/vote1/vote2_raw 4,000 rows; rubric_swap 4,200; rubric_contrast 11,124; the six E-RAW secondaries (causal_length x4, arxiask, oracle) | **0** in every column | 0 | 0 |
| 137 SQLite files not in the record (incl. new canary_baseline_pass3/4.db, multicorpus/trace_truncation.db, r8/x8/x12 ratings match_history) | every column whose name contains winner / vote / verdict (88 files carry one) | **0** in every column | not examined | not examined |

So the R2.5 branch "moved labels ALL ''" is UNREACHABLE on today's bytes. The unresolvable labels that the six secondaries carry in the record (913 / 861 / 811 / 832 / 250 / 252) are contestant NAMES (e.g. 'gemini-3.1-pro_5-shots', 'iask_pro', 'arx_0314'). None is ''.
- Any move to R6 under F1 on those names is the "any other label" branch: an ordinary R6 finding under R-5.
- Whether a unit resolves them is the legs' job, not this census's.

## 4. What this does NOT show

- It does not show whether any unit of record moves to R6 under F1. That is the F1 readout in (ii). My census applies no name profile, so it cannot predict R6 on names.
- It does not read -wal tails: immutable=1 reads the checkpointed file only.
  - The non-empty -wal files found are `_backup/embeddings_cache_2026-09-22.db-wal`, `_backup/embeddings_cache_prewal_checkpoint_2026-09-23/embeddings_cache.db-wal`, and worktree copies under .claude/worktrees/.
  - None is a cache of record. The worktrees are outside the enumeration rule.
- Whitespace-only strings were checked only on the 67 units of record, not on the 137 other files.
- It does not rule on L1215 or on per-order '' votes (section 2, "Stated, NOT ruled here").
- It does not certify, re-classify or score anything, and writes no output of record.

## 5. Commands that reproduce section 3

Both scripts open each DB `file:<abs>?mode=ro&immutable=1`, set and read back `PRAGMA query_only=1`, and write nothing.
- (a) Units of record: for each unit in vote_frame_cert.json, for each label column c (WIDE: win, v1, v2; LONG: the column among vote / winner / parsed_winner / verdict), run:
  `SELECT COUNT(*), SUM(c = ''), SUM(TRIM(c) = '' AND c <> ''), SUM(c IS NULL) FROM <table>`
- (b) The other files: walk experiment_results/** and the root; keep files whose first 16 bytes are `SQLite format 3\0` and whose path is not in the record; for every table column whose name matches `(winner|vote|verdict)`, run:
  `SELECT COUNT(*), SUM(c = '') FROM <table>`

The scripts used were `p4_empty.py` (a) and `p4_new.py` (b) in the session scratchpad. Output lines as quoted:
- (a): "units 67 | label columns carrying '' or whitespace-only: 0"
- (b): "sqlite files 199 | record caches 62 | non-record files with a vote/winner/verdict-like column 88 | such columns carrying '' 0"
