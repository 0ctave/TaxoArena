"""VOTE-FRAME-CERT — for every dual-order cache in the record: which stored vote column is POSITIONAL, which (if any) is
CONTESTANT-LABELLED, and is the order key a column ordinal or an `arm` value — asserted ROW BY ROW (engineering, zero calls;
the prerequisite of POSITION-INDEX-ALL).

REGISTRATION OF RECORD: docs/judge_v2_program.md L13032-L13109 (commit 8adae39), heading "## Registered 2026-09-23 (before any
code or call) — VOTE-FRAME-CERT: ..."; record docs/agents/results/VOTE-FRAME-CERT.json. Zero judge calls; nothing is posted.

LAUNCH SEQUENCE (the registration's FLOW):
  python tools/analysis/vote_frame_cert.py --selftest                       (synthetic caches under tempfile.mkdtemp(); no DB of record)
  python tools/analysis/vote_frame_cert.py --dry-run                        (enumeration + schema reading; certifies nothing, writes nothing)
  python tools/analysis/vote_frame_cert.py --run --steward-list <file>      (the certificate; writes experiment_results/vote_frame_cert.txt
                                                                             and .json WRITE-ONCE, mode "x"; refuses if either exists)
  <file> is the data-steward's INDEPENDENT listing from the same enumeration rule (one repository-relative POSIX path per line, '#'
  comments allowed), carried by the READY; criterion E1 compares it file for file. The run executes the selftest in-process first;
  its result IS criterion E3.

HYGIENE. Every SQLite file is opened "file:<path>?mode=ro&immutable=1" by open_ro() below and by nothing else; the URI flags are
asserted and PRAGMA query_only=1 is set and read back on every connection. No script's open_cache() is imported or called (stack_judge
L86-L91 and bfcl_judged_pilot L893-L903 open READ-WRITE and commit a CREATE TABLE; STACK-JUDGE-RO-CACHE). Size and mtime of every scanned
SQLite file and its -wal / -shm are taken before anything is opened and again at the end (criterion E4 on the enumerated files; the
others are printed beside). A non-empty -wal is printed as a WARNING: immutable=1 reads the checkpointed database only. The pools a
cache belongs to are printed from its run_meta / meta table where present (not asserted). No pool is read for its questions.

ENUMERATION RULE (fixed by the registration; the exact name patterns, read from the schema only — PRAGMA table_info, which is the
parsed sqlite_master text — never from rows). A file is enumerated iff it starts with the 16-byte SQLite header, lies under
experiment_results/ (recursively, every file whatever its extension, _backup/ included) or directly in the repository root, and has
at least one table that is
  WIDE  — two or more PER-ORDER VOTE columns, name matching  ^(vote|v|winner|verdict|parsed_winner)_?(1|2|fwd|rev|ab|ba|first|second)(_raw)?$
          (vote1, vote2, vote2_raw, ...), OR two or more PER-ORDER RAW columns, name matching
          ^(raw|raw_content|response|content)_?(1|2|fwd|rev|ab|ba|first|second)$  (raw1, raw2);
  LONG  — otherwise, a column named arm / order / side / presentation_order (the ORDER KEY) together with a single vote column
          (vote / winner / parsed_winner / verdict) or a single raw column (raw / raw_content / response / content).
No file is excluded by hand; exclusion happens only through the class. Case-insensitive on column names.

THE ORDER KEY. WIDE: a COLUMN-ORDINAL key (the suffix 1/fwd/ab/first = order 1, 2/rev/ba/second = order 2); an `arm` column in a WIDE
table is a CONDITION (its values are printed) and the whole table is one unit. LONG: an ARM-VALUE key; its values are read and the
first registered ORDER PAIR present is used, (order-1 value, order-2 value) in this order of preference:
  (fwd, rev)           bfcl_judged_pilot.py L1361, newcomer_placement.py L486-L487, placement_steps.py L459-L460, placebo_entry.py L108
  (ensemble, reversed) arena13.py L101 (NEW shown first) + position_decomp.py L66-L68 (opponent shown first, "stored as arm reversed")
  (1, 2)               JudgeCallStore.kt L14 (presentationOrder 1 = (A, B) as given, 2 = (B, A))
  (ab, ba), (first, second)   (no writer in the tree; carried for completeness)
Arm values outside the pair (arena13's selfref / t0a / t0b) are printed with their counts and excluded. A LONG table with no pair is
NOT DUAL-ORDER: it is classed UNCERTIFIABLE with that reason (single-order arm-conditioned caches: ref_gated_rubric.py arms base/card).
[BUILDER'S READING, reported to the registrar: the registration's five classes have no "not dual-order" class, and its schema-only
enumeration necessarily catches single-order arm-conditioned tables; they are classed UNCERTIFIABLE(NOT-DUAL-ORDER) and counted
separately in the summary so P1 / P4 can be read both ways.]
[CORRECTED 2026-09-23 by the registrar's ruling (4), programme L13691-L13746 (04379d7): a SIXTH class NOT-DUAL-ORDER is admitted, outside
the five and NOT a kind of UNCERTIFIABLE. A table is NOT-DUAL-ORDER iff, ROW LEVEL, no match key has rows under two or more order values
(the order vocabulary is the union of the registered pairs; the match key is the table's mid / match_id, else the Kotlin judge_calls
tuple (snapshot_id, eval_question_id, model_a, model_b), else its primary key without the order key); a WIDE table is NOT-DUAL-ORDER
iff no row carries both orders (both vote columns, or both raw columns, non-empty). A table whose rows do reach two order values but
under no registered pair is UNCERTIFIABLE. The sentences above that class such tables UNCERTIFIABLE are superseded by this bracket.]

THE EVIDENCE (the registration's order of preference).
 E-RAW   the stored raw response of each order is re-parsed with the parser every enumerated writer uses:
         rejudge_grok.parse_judge(rejudge_reasoning.strip_think(raw)) — the writers call rj.parse_judge on raw text that is either
         already think-stripped (bfcl_judged_pilot L1273-L1274, arena13 L117-L118, leaf_powered L103, position_decomp L65-L66,
         temp0 L124-L125, escalate_llama_law, rejudge_reasoning) or carries no <think> block (the non-reasoning judges);
         strip_think is idempotent on both. The Kotlin judge_calls rows (TaxonomyArenaService.parseRecipeCall L498-L506) are
         parseJudgeResponse(stripThink(content)), whose Python port is the same pair (judge_wiring.py L472). The raw text can only name
         POSITIONS, so, on the INFORMATIVE rows of an order (re-parse Model A / Model B, stored vote not INVALID): a stored order-2 vote
         equal to the re-parse on 100% is POSITIONAL, equal to the TRANSPOSED re-parse on 100% is CONTESTANT-LABELLED. Order 1 is
         frame-invariant (its positions ARE its contestants) and must agree with the re-parse on 100% under either hypothesis.
 E-COMB  where no raw text exists, the stored combined winner (and flip, when stored) is re-derived from the two stored votes under
         BOTH hypotheses with the recipe's rule rejudge_grok.combine_orders (positional: order 2 transposed) and its untransposed twin
         (contestant); informative rows are those with both votes decisive and a stored combined value that is not INVALID.
 A stored vote INVALID on a decisive re-parse (the unusable-finish rules: bfcl unusable_vote, Kotlin NON_TERMINATED) is not
 informative and is counted; a stored decisive vote on a non-decisive re-parse is counted as a parser-drift symptom (not frame
 evidence) and printed.
 Where both E-RAW and E-COMB are computable, E-RAW decides and E-COMB is printed beside; if both CERTIFY and disagree the unit is MIXED
 ("evidence conflict").
 LABEL SPACES. Stored votes are position labels ("Model A" / "Model B") everywhere except four name-labelled LONG caches whose writers
 map the vote through the order's own contestant map: arena13.db (arena13.py NEW first in 'ensemble', the opponent first in
 'reversed'), placebo.db (placebo_entry.py GEM first in 'fwd'), newcomer_placement.db and newcomer_placement_steps.db (schedule.newcomer
 first in 'fwd'). For those a stored name is mapped to the ORDER-1 position of that contestant (schedule.opponent is the other) and the
 same two hypotheses are tested: CONTESTANT-LABELLED = names mapped with each order's own map; POSITIONAL = order 2 mapped with order 1's
 map (the sign bug in name form). The constants are read from the writers' source by ast, never by import. A combined winner stored as
 a name (leaf_powered, j6_rubrics) is resolved through the row's model_a / model_b, else the schedule's.

CLASSES. CERTIFIED-POSITIONAL; CERTIFIED-CONTESTANT; MIXED (neither hypothesis on 100% — the contradicting row ids listed); AMBIGUOUS
(no informative order-2 row); UNCERTIFIABLE (neither raw text nor a combined column; or NOT DUAL-ORDER). One class per TABLE; the cache
class is MIXED if any table is MIXED or certified tables disagree, else the certified class if any table is certified, else AMBIGUOUS,
else UNCERTIFIABLE (every table's class printed; POSITION-INDEX-ALL enters CERTIFIED tables only, and only from a cache that is not MIXED).
[CORRECTED 2026-09-23 by the registrar's rulings (04379d7): (a) SIX classes, the sixth NOT-DUAL-ORDER (ruling (4)); a cache is classed on
its DUAL-ORDER tables, its single-order tables LISTED; a cache whose every candidate table is NOT-DUAL-ORDER is NOT-DUAL-ORDER. (b) Order 1
is frame-invariant, so its rows are AMBIGUOUS by construction and DO NOT DECIDE the class (the registrar's recorded reading on P5: the fwd
arm "does not decide the cache's class"); the class is decided on the order-2 rows alone, and an order-1 disagreement with its re-parse
is printed as a WARNING with its row ids. The sentence above "Order 1 ... must agree with the re-parse on 100% under either hypothesis"
is superseded by this bracket. (c) E2 reads "exactly one of the SIX classes"; P1-P4 are read over the dual-order caches only
(enumerated minus NOT-DUAL-ORDER), the raw enumeration count and the NOT-DUAL-ORDER count printed beside; P5 is read on the rev arm.]
[CORRECTED 2026-09-23 by the READY review docs/reviews/NOT_READY_vote_frame_family.md (14edeb4), B1 / B2 / H2 / M1; item (b) of the bracket
above is WITHDRAWN and the original sentence stands: order 1 cannot DISCRIMINATE the two frames, but on order 1 BOTH hypotheses predict
stored == re-parse, so any order-1 contradiction REFUTES both and the table is MIXED, with the contradicting row ids listed (the
registration's "neither hypothesis on 100%"); the builder's demotion to a WARNING certified a table whose order 1 was transposed (index s
0.333 against a truth of 0.750). B2: a raw-only WIDE table (raw text + combined winner, no stored vote) whose combined column reproduces only
the UNTRANSPOSED combine is MIXED ("combined column inconsistent with a positional recipe"): the re-parsed votes are positional by
construction and are NEVER transposed. H2: the Kotlin judge_calls match key is (snapshot_id, eval_question_id, model_a, model_b) plus
judge_model, recipe and node_id where the table carries them, and a LONG table in which any match key carries more than one row under one
order value is REFUSED (UNCERTIFIABLE: the pairing is not unique), its duplicate count printed. M1: open_ro's guards are explicit raises.]
[RULED 2026-09-23 by the registrar, finding H3, programme L13967-L14002 (0104e44): a table certified ONLY through E-COMB (stored votes, no raw
text) is CERTIFIED only if a per-cache SOURCE CHECK of its writer's combiner passes, else it is UNCERTIFIABLE ("E-COMB, combiner not
verified"). combiner_check() below: (a) the writer is COMB_WRITER[basename] (rubric_ladder.db -> rubric_ladder.py, rubric_swap.db ->
rubric_swap.py, rubric_contrast.db -> rubric_value_contrast.py; any other E-COMB cache has no named writer and FAILS); its source is taken at
the blob that wrote the cache: the script sha in the cache's run_meta / meta (script_sha256_16_lf, script_sha256_16, script_sha) matched
against the LF bytes of every commit of the script, else the LAST COMMIT of the script at or before the cache's first write (run_meta
'started', else min(ts) of the table), by read-only git; a blob that cannot be pinned FAILS; (b) every call in the writer whose callee's
name contains "combine" is resolved with ast (never executed): rejudge_grok.combine_orders (through `import rejudge_grok as X` or `from
rejudge_grok import combine_orders`) is checked in rejudge_grok.py at ITS last commit at or before the same pin time; a local def is
checked in place; anything else FAILS; a combiner passes iff it is AST-identical to REF_COMBINE_ORDERS (docstring and parameter names
normalised) or applies EXACTLY ONE transposition dict {"Model A": "Model B", "Model B": "Model A"} and applies it to its order-2 (second)
parameter; zero or two transpositions FAIL; a writer with no combiner call FAILS; (c) the result, the writer, the pinned blobs and the
evidence are printed per table. LIMIT, stated: a combiner reached only through another helper whose name does not contain "combine" is
not seen, so such a writer FAILS (no combiner call found) rather than passing.]
[RULED 2026-09-23 by the registrar, D2 / D4 / D7, programme L14201-L14246 (2c94cab): (D2) an E-COMB-only certificate ADDITIONALLY requires, by ast at
the same pinned writer blob, for every verified combiner call: (i) its SECOND argument is a bare name, and every row tuple built in the same
function with as many elements as the table's columns (the columns read from the writer's own CREATE TABLE text for that table) stores THAT
name at the order-2 column's index; (ii) the name's ONLY binding in that function is the first element of a tuple-unpack of a direct call to
rejudge_grok.parse_judge (no subscript, no wrapping call, no re-assignment; not a parameter). A failure, or a writer the check cannot parse
(no CREATE TABLE for the table, no row tuple of its width), makes the table UNCERTIFIABLE, reason "E-COMB, call-site argument not verified".
(D4) a duplicate-key LONG table is UNCERTIFIABLE, reason "duplicate key" (as implemented). (D7) the pin rule is kept; P4 is scored on the total
UNCERTIFIABLE count among the dual-order caches and ALWAYS printed by reason: (1) the registered definition, (2) E-COMB combiner not verified
(the pin-timing cases counted and named as such), (3) E-COMB call-site argument not verified, (4) duplicate key, (5) a pair outside the
registered pairs; a sixth line appears only if a table is UNCERTIFIABLE for a reason outside the five (stored labels unresolvable), flagged
for the registrar. Each UNCERTIFIABLE table carries its reason code in `uncert_reason`.
[NOT IMPLEMENTED, reported to the registrar (re-review bc2ea7b D1): the coordinator's fix "admit only AST-identity to rj.combine_orders" is
NARROWER than ruling H3 (b), which admits "AST-equivalent to it, i.e. applies exactly one transposition to the order-2 vote before comparing";
the builder was told to stop rather than choose, so combiner_ok() keeps the ruling's two arms unchanged. On the record the second arm never
fires (condition V-C2: 0 "AST-equivalent" lines).]
[AMENDED 2026-09-23 by the registrar, H3(b) narrowed, programme L13994 bracket and L14248-L14278 (94731da); the bracket above is SUPERSEDED: the
"AST-equivalent" arm is WITHDRAWN and REMOVED from combiner_ok(). A combiner is verified ONLY if (1) it is a DIRECT CALL to rejudge_grok.combine_orders
(`X.combine_orders` with `import rejudge_grok as X`, or `from rejudge_grok import combine_orders` unaliased), or (2) it is a local def AST-IDENTICAL
(docstring and parameter names normalised) to rejudge_grok.combine_orders AT THE PINNED rejudge_grok BLOB; anything else is UNCERTIFIABLE, reason
(2) "E-COMB, combiner not verified", printed with a diagnostic (parameter and transposition counts). Consequences of the amended text, implemented as
written and reported to the registrar: a DIRECT call is verified whatever the body of combine_orders was at the pinned rejudge_grok blob (that body's
identity with the recipe's REF_COMBINE_ORDERS is printed beside, not decisive), and a local copy of THAT pinned body is verified. STATED LIMITS
(conservative false FAILS, never false passes): (i) a correct combiner written differently (the re-review's C6) is UNCERTIFIABLE; (ii) an unrelated
helper whose name contains "combine" (combine_text) is taken for a combiner call and fails; (iii) an ALIASED import (`from rejudge_grok import
combine_orders as co`) is not recognised as a direct call, so no combiner call is found and the table fails.]
[CORRECTED 2026-09-23 by the READY delta re-review docs/reviews/READY_vote_frame_family_rr2.md (776a2dd), D-A / D-C / L1 / L2; the two "consequences"
in the bracket above are WITHDRAWN (the reviewer: a narrowing cannot widen the certified set; the reading is within the amendment's text):
(D-A) the pinned rejudge_grok.combine_orders body must itself be AST-identical to the recipe's REF_COMBINE_ORDERS; a DIRECT call is verified only
then, and a local def only if it is AST-identical to that pinned body AND the body is REF; both arms print the pinned body's REF identity;
otherwise R2 "combiner not verified". (D-C) a writer module that stores to the rejudge_grok alias (e.g. `rj = ...`), assigns or deletes an
attribute of it (e.g. `rj.combine_orders = ...`, `rj.parse_judge = ...`), rebinds a name from-imported from rejudge_grok, or calls setattr /
delattr / exec / eval anywhere FAILS R2 before any call is resolved (conservative: a patched or rebound module is not rejudge_grok). (L2) the
pin-timing flag is set from the comparison itself (a first write that precedes the writer's EARLIEST commit), never from a message substring;
an unmatched run_meta sha is not pin timing. (L1, position_index_all.py) the selftest prints its checks and its INFO lines separately.]
[RULED 2026-09-23 by the registrar, D-B, programme L14214 bracket and L14383-L14413 (ae20138): D2's conditions (i) and (ii) apply ALSO to the
combiner's FIRST argument and the ORDER-1 column (bound directly from parse_judge, stored unchanged), else UNCERTIFIABLE reason (3). STATED LIMIT
(x2), not a trigger: an order-2 name parsed from the ORDER-1 raw text passes both conditions; it is visible in the data as a 100% flip rate on
decisive rows. The D-A reading is recorded by the registrar's clarifying bracket at L14260.]
[ENGINEERING 2026-09-23, queue VFC-DC-PRIME (review ae88d3a D-C'; programme L14529-L14549), builder's text, awaiting its delta READY: the D-C
denylist above is WIDENED; each vector below FAILS R2 "combiner not verified" before any call is resolved (conservative false fails possible, never
a false pass by these routes): (a) a subscript or attribute STORE / DELETE whose target chain passes through a call result (globals()[..], vars(x)[..],
__import__(..).x, getattr(..).x, importlib.import_module(..).x), through the rejudge_grok alias or a from-imported rejudge_grok name below the first
attribute (rj.x.y = .., rj.x[k] = ..), through sys.modules, or through ANY dunder attribute (rj.__dict__[..], f.__code__ = ..); (b) ANY reference,
not only a call, to setattr / delattr / exec / eval (a call to these four stays with the D-C line above), and any reference at all to __import__ /
globals / vars; an attribute NAMED one of those seven (builtins.setattr); (c) ANY dunder attribute, loaded or stored (object.__setattr__, .__dict__,
.__code__, .__globals__), and any dunder NAME other than __name__ / __file__ / __doc__ (__builtins__); (d) any reference to sys.modules or
`from sys import modules`, and any import of importlib; (e) the rejudge_grok alias used as a bare VALUE (x = rj; f(rj); importlib.reload(rj)),
and any other binding of the alias or of a from-imported name (def / class / parameter / except-as / match capture / a second import of that name);
(f) TRANSITIVELY, every LOCAL module the writer imports (a module with a history under tools/analysis/), each at its last commit at or before the
SAME run-time pin as rejudge_grok (the first write), scanned with the same rules; a local import that cannot be pinned, or a relative import,
FAILS; rejudge_grok.py itself is scanned and may carry at most one def of combine_orders and of parse_judge and no other binding of them
(no def of combine_orders already fails the combiner check).
STATED LIMITS (not closed): in-place mutation of a rejudge_grok module-level object through its own methods (rj.TABLE.update(..)); patches made by
a non-local (site-packages / stdlib) module or by the interpreter environment (sitecustomize, PYTHONSTARTUP); anything not visible in the source.]
[ENGINEERING 2026-09-23, queue VFC-NAME-PROFILE-BY-CONTENT (post-run review abf4db5 D1 / D6; programme L14601-L14647), builder's text, awaiting its
delta READY: the name profile of a LONG table is found FIRST by CONTENT, the full sha256 of the file matched against NAME_PROFILE_CONTENT (the four
certified CONTESTANT originals of the run of record, c731836), and only then by file basename as before; a byte-identical copy of a certified
original therefore gets its original's profile, and so its class, whatever its path. The key that matched is printed per unit (`name_profile`).
RX is NOT changed, and not ruled here: it stays in the code as the registrar left it; it is no longer reachable for a byte-identical copy of a
certified original, and the selftest now EXECUTES it on a name-labelled table under an unmapped basename with unmatched content (D6).]
[ENGINEERING 2026-09-25, queue VFC-FIXES-2, builder's text, awaiting its delta READY; it implements the VFC-RX-RULING of record (programme
L17171-L17328, f1e9e68; R-1..R-9) and defects D1-D5 of the READY review 9d3e261 (programme L15566-L15584). The RX sentences above (the D7 bracket's
"a sixth line appears only if ... outside the five", and "RX is NOT changed, and not ruled here") are SUPERSEDED by this bracket.
(R-1) RX is the SIXTH registered UNCERTIFIABLE reason, code R6, label "stored labels unresolvable (a name-profile gap: instrument knowledge, not
frame)"; the literal "RX" and the "OTHER ... outside the five" label and line are retired; P4 is printed under SIX reasons.
(R-2) a dual-order unit is UNCERTIFIABLE (R6) if ONE OR MORE stored labels on its DECIDING tally are unresolvable (LONG: the rows under the registered
pair; a WIDE unit decided by E-COMB or E-COMB(re-parsed raw): the combined column), whatever the parse of the row; the count and the resolved-subset
class are printed beside, DESCRIPTIVE. The former `n2_inf == 0` condition is gone.
(R-3) precedence: the resolved rows are classed first; if they are MIXED (an order-1 contradiction, an order-2 contradiction under both hypotheses,
or the raw-only B2 rule) the unit is MIXED; R6 applies only when the resolved rows are consistent (CERTIFIED-* or AMBIGUOUS on the subset). BUILDER'S
READING (not in the ruling's text, reported): on an E-COMB unit R6 is decided on the tally BEFORE the H3 combiner check, which runs only on a unit
that would otherwise certify; an R6 unit therefore carries R6, never R2 / R3.
(R-4 / R-5) R6 is neither AMBIGUOUS, nor MIXED, nor a refusal of the run; an R6 unit is excluded from every index by class, counted in P4's total,
and printed on its own line ("P4 reason (6) ... UNCERTIFIABLE by instrument knowledge, not by frame") when the count is positive.
(R-6) a WIDE SECONDARY (E-COMB beside a deciding E-RAW) with unresolvable labels is printed "UNCERTIFIABLE (R6), secondary, n resolved of m
informative" and stored with klass UNCERTIFIABLE / uncert_reason R6 / resolved_klass; it is NEVER printed CERTIFIED; its resolved rows keep ONE
power, to downgrade (EVIDENCE CONFLICT -> MIXED when they certify the other frame; the WARNING when they are MIXED); a resolved-subset agreement is
never cited as corroboration; the secondary never enters uncert_breakdown or P4 (unchanged).
(R-7) fail closed: an UNCERTIFIABLE unit without a registered reason code is an instrument defect and the run REFUSES before anything is written
(require_reason_codes, called by run() over EVERY unit; uncert_breakdown refuses too); the default `u.get("uncert_reason", "RX")` is removed.
(R-8) unit_votes REFUSES on an unresolvable label of a CERTIFIED unit, naming the unit and the first key (drift between certificate and reading),
where it used to `continue`.
(R-9) an R6 unit's label_space reads "unresolved".
(D1, 9d3e261) the D-C' denylist is WIDENED by the reviewer's five routes (module_tampering_d1; each FAILS R2 before any call is resolved): an import
of inspect / gc / pkgutil / ctypes / types / runpy / code / codeop (Import or ImportFrom); any attribute, or from-imported name, among f_globals /
f_locals / f_builtins / f_back / currentframe / _getframe / resolve_name / get_objects / get_referrers / get_referents / FunctionType / CodeType /
setitem / delitem; a reference to the builtin NAME compile (an attribute .compile, e.g. re.compile, is not a finding); an attribute store / delete
NAMED combine_orders or parse_judge on ANY object other than the alias (the alias is the D-C line); a subscript store / delete under a string key
naming the alias, a from-imported name, rejudge_grok, combine_orders or parse_judge. The reviewer's vectors u1-u7 are fixtures. STATED LIMITS
(still not closed; an AST denylist cannot close the class): a route through a module or attribute not named here; anything not visible in the
source; the allowlist the review offered as the alternative is NOT adopted.
(D2, 9d3e261) the transitive scan fails CLOSED: a top-level import is (1) LOCAL if tools/analysis/<mod>.py has a git history (pinned and scanned as
before), (2) a finding if tools/analysis/<mod>.py or the package tools/analysis/<mod>/ exists on disk with no history ("cannot be pinned"),
(3) skipped if it is in sys.stdlib_module_names or (4) the top-level name of an installed distribution (importlib.metadata; stated limit, not
scanned), else (5) a finding ("neither local, stdlib nor installed"). A package-path import rooted at `tools` is resolved: `import
tools.analysis.X`, `from tools.analysis import X`, `from tools.analysis.X import ..` -> the local module X; any other `tools` form is a finding.
(D3) a committed local module that does not parse at the pin is a fixture. (D4) the selftest pins NAME_PROFILE_CONTENT by the sha256 of its
canonical JSON (NAME_PROFILE_CONTENT_SHA256); the values themselves were verified against the files by the review (9d3e261 claim 9), not here.
(D5) position_index_all.py's selftest INFO line is corrected there. VFC_PIN_LF stays 72ceddfe919a982e (it pins the certificate of record's
writer; no new certificate is written by this build).]
[CORRECTED 2026-09-25 by the READY review docs/reviews/READY_vfc_fixes_2.md (a3da968, NOT READY part (i)), F1-F7, builder's text: (F1, HIGH) the
E-COMB tally counted an unresolvable combined label only on rows with both votes decisive, so a TIE-vote row's unresolvable label certified;
comb_tally now resolves the label BEFORE the decisive-vote gate ("whatever the parse of the row", R-2), counts the total in unresolvable_labels
(which decides R-2 on the primary and R-6 on the secondary) and, separately, the unresolvable labels on rows with both votes decisive, which
alone enter R-6's "n resolved of m informative" (m = resolved + those); the R6 notes and the R6 secondary line print both counts and the most
frequent unresolvable labels (unresolvable_values). The sentence in the bracket above that the secondary's m is "informative" of the resolved and
unresolvable rows reads with this bracket. (F2) the R-7 fixture's refuses() fails BY NAME on any exception other than a SystemExit. (F3) a LONG
fixture with EXACTLY ONE unresolvable label, on order 1. (F4) fixtures: E-COMB with a resolved AMBIGUOUS subset (R6); an R6 secondary whose
resolved subset is MIXED (the WARNING); runpy / code / codeop; a committed local module shadowing a stdlib name (csv.py), scanned. (F5) builtins
is in D1_MODULES (the reviewer's getattr(builtins, ..) and `from builtins import exec` vectors are fixtures). (F6) on an R6 E-COMB unit the H3
combiner check runs DESCRIPTIVELY (combiner_check_descriptive, a notes line); it decides nothing, the class stays R6. (F7) the LONG R6 note
prints the order-1 and order-2 informative counts separately (they were summed).]

CRITERIA (E1-E4, each HELD / FAILED; the certificate is HELD iff all four are) and PREDICTIONS (P1-P5) are printed by score_criteria()
and score_predictions(); every branch of both is executed by --selftest.
"""
import os, sys, re, ast, io, json, time, hashlib, sqlite3, argparse, tempfile, shutil, contextlib, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import rejudge_grok as rj                 # parse_judge, combine_orders (importing opens no DB; the selftest runs under a connect trap)
import rejudge_reasoning as rr            # strip_think

TEST = "VOTE-FRAME-CERT"
REGISTRATION = "docs/judge_v2_program.md L13032-L13109 (8adae39)"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
SQLITE_MAGIC = b"SQLite format 3\x00"
POS = ("Model A", "Model B")
CLASSES = ("CERTIFIED-POSITIONAL", "CERTIFIED-CONTESTANT", "MIXED", "AMBIGUOUS", "UNCERTIFIABLE", "NOT-DUAL-ORDER")   # six: ruling (4), 04379d7
NDO = "NOT-DUAL-ORDER"
CERTIFIED = ("CERTIFIED-POSITIONAL", "CERTIFIED-CONTESTANT")
VOTE_PAIR_RE = re.compile(r"^(vote|v|winner|verdict|parsed_winner)_?(1|2|fwd|rev|ab|ba|first|second)(_raw)?$", re.I)
RAW_PAIR_RE = re.compile(r"^(raw|raw_content|response|content)_?(1|2|fwd|rev|ab|ba|first|second)$", re.I)
ORDER1_SUFFIX = {"1", "fwd", "ab", "first"}
ORDER_KEY_COLS = ("arm", "order", "side", "presentation_order")
SINGLE_VOTE_COLS = ("vote", "winner", "parsed_winner", "verdict")
SINGLE_RAW_COLS = ("raw", "raw_content", "response", "content")
ORDER_PAIRS = (("fwd", "rev"), ("ensemble", "reversed"), ("1", "2"), ("ab", "ba"), ("first", "second"))
ORDER_VOCAB = {v for p in ORDER_PAIRS for v in p}
COMBINED_SPECS = (("winner", "flip"), ("grok_winner", "grok_flip"), ("r1_winner", "r1_flip"), ("ref_winner", "flip"))
FOREIGN_COLS = ("mistral_winner", "mistral_tie", "key_winner", "checker_winner")   # never derived from this cache's two votes
MATCH_KEY_COLS = ("mid", "match_id")
QID_COLS = ("qid", "question_id", "eval_question_id")
# name-labelled LONG caches (source reading; see the docstring). first = ("const", script, NAME) or ("col", column); second = column.
NAME_PROFILES = {
    "arena13.db": dict(sched="schedule", key="mid", first=("const", "arena13.py", "NEW"), second="opponent"),
    "placebo.db": dict(sched="schedule", key="mid", first=("const", "placebo_entry.py", "GEM"), second="opponent"),
    "newcomer_placement.db": dict(sched="schedule", key="mid", first=("col", "newcomer"), second="opponent"),
    "newcomer_placement_steps.db": dict(sched="schedule", key="mid", first=("col", "newcomer"), second="opponent"),
}
# VFC-NAME-PROFILE-BY-CONTENT (abf4db5 D1): the profile is found FIRST by the full sha256 of the file's bytes, matched against the certified
# CONTESTANT originals of the run of record (experiment_results/vote_frame_cert.json at c731836; its sha256_16 is the prefix of each), then by basename.
# {sha256 hex: (NAME_PROFILES key, certified original path)}
NAME_PROFILE_CONTENT = {
    "594742e08e0f9ba1bcde977cc6d7b5a6be61be11949ee67e2708a5dca0cbf2a3": ("arena13.db", "experiment_results/x12_crossdomain/arena13.db"),
    "8c0ac804127926dde2e8b35820e74cc322abc285c4129e126201601168d8479d": ("placebo.db", "experiment_results/x12_crossdomain/placebo.db"),
    "755a1f4f2a6411c5e423769fd28a28a42e12d8d92dbf9b063f5d11577ccab3fe": ("newcomer_placement.db", "experiment_results/x12_crossdomain/newcomer_placement.db"),
    "292fdf095f527ce14915be542a75385f978c89951d6897a48e3a90b984cc1562": ("newcomer_placement_steps.db",
                                                                          "experiment_results/x12_crossdomain/newcomer_placement_steps.db"),
}
# D4 (9d3e261): sha256 of NAME_PROFILE_CONTENT's canonical JSON (sort_keys, separators (",", ":")); the selftest recomputes it, so an edited value
# fails the selftest. The four values were verified against the files by the review (9d3e261, claim 9), not by this pin.
NAME_PROFILE_CONTENT_SHA256 = "616257a6ee77acd76c1b19a6f2f402678d147c7e86ba116273b86b139e6273ec"
# writer of each cache basename, from reading the source (printed for the READY; "UNMAPPED" otherwise). Decides nothing.
WRITER_OF = {
    "aggregate.db": "aggregate_ties.py", "arena13.db": "arena13.py + position_decomp.py + temp0.py", "arenav3.db": "arena_v3_compiled.py",
    "arxiask.db": "arxiask_probe.py", "bfcl_judged_pilot.db": "bfcl_judged_pilot.py", "canary_baseline_pass1.db": "canary_baseline.py",
    "canary_baseline_pass2.db": "canary_baseline.py", "escalate_llama_law.db": "escalate_llama_law.py", "grok_calib.db": "grok_calib.py",
    "leaf_powered.db": "leaf_powered.py", "newcomer_placement.db": "newcomer_placement.py",
    "newcomer_placement_steps.db": "placement_steps.py", "oracle.db": "oracle_ref.py", "pairnoref.db": "pair_noref.py",
    "placebo.db": "placebo_entry.py", "ref_checklist.db": "ref_checklist.py", "refconf_grok.db": "refconf.py",
    "refgated.db": "ref_gated_rubric.py", "rejudge_grok.db": "rejudge_grok.py", "rejudge_deepseek_r1_0528.db": "rejudge_reasoning.py",
    "rejudge_grok_4_1_fast_reasoning.db": "rejudge_reasoning.py",
    "rejudge_grok_4_1_fast_reasoning_refgrok.db": "rejudge_reasoning.py / escalate_llama_law.py",
    "rejudge_mistral_format_stripped.db": "format_perturbation.py", "rejudge_mistral_reference.db": "rejudge_reference.py",
    "rejudge_mistral_reference_grok_reasoning.db": "rejudge_reference.py", "rejudge_mistral_two_refs.db": "j2d_two_refs.py",
    "rejudge_mistral_v2_refgrok.db": "prompt_v2.py", "rubric_contrast.db": "rubric_value_contrast.py", "rubric_j6.db": "j6_rubrics.py",
    "rubric_kit.db": "rubric_kit.py", "rubric_ladder.db": "rubric_ladder.py", "rubric_swap.db": "rubric_swap.py",
    "stack_norubric.db": "stack_norubric.py", "stack_v2.db": "stack_judge.py", "stack_v2_promptv2.db": "stack_judge.py",
    "stack_v2_promptv2_grok.db": "stack_judge.py --judge grok", "stack_v2_promptv2_x12all.db": "stack_judge.py (ALL_X12)",
    "stack_v2_promptv2_x20.db": "arena_v2_x20.py", "stack_v2_kit.db": "rubric_kit.py", "stack_v2_kit2.db": "rubric_kit2.py",
    "stack_v2_kit2_grok.db": "rubric_kit2.py", "gen_arena_grok.db": "generative_arena.py",
    "ifeval_response_oracle.db": "ifeval_response_oracle.py", "stage3_math_grok_v2_capfree.db": "stage3_math.py",
    "bareq512_s42.db": "rubric_512.py", "generic_ss.db": "rubric_512_ss.py", "grok_reasoning_cell.db": "rubric_512_r.py",
    "grok_reasoning_generic.db": "rubric_512_r.py", "grok-reasoning.db": "causal_length.py", "mistral.db": "causal_length.py / rubric_p8.py",
    "mistral_refgrok.db": "causal_length.py", "mistral_refgrok_v2.db": "causal_length.py",
}
PARSER_NAME = "rejudge_grok.parse_judge(rejudge_reasoning.strip_think(raw))"
# P4 by reason (D7, 2c94cab): the code carried by every UNCERTIFIABLE table
UNCERT_REASONS = (("R1", "the registered definition (neither raw text nor a combined column)"),
                  ("R2", "E-COMB, combiner not verified"),
                  ("R3", "E-COMB, call-site argument not verified"),
                  ("R4", "duplicate key"),
                  ("R5", "a pair outside the registered pairs"),
                  ("R6", "stored labels unresolvable (a name-profile gap: instrument knowledge, not frame)"))     # R-1, VFC-RX-RULING (f1e9e68)
UNCERT_CODES = tuple(k for k, _ in UNCERT_REASONS)
# H3 (0104e44): the writers of the E-COMB-only caches (no raw text stored), read from the source; any other E-COMB cache FAILS the check
COMB_WRITER = {"rubric_ladder.db": "rubric_ladder.py", "rubric_swap.db": "rubric_swap.py", "rubric_contrast.db": "rubric_value_contrast.py"}
WRITER_DIR = "tools/analysis"
RUN_META_SHA_KEYS = ("script_sha256_16_lf", "script_sha256_16", "script_sha")
REF_COMBINE_ORDERS = '''
def combine_orders(vote1_raw, vote2_raw):
    vote2 = {"Model A": "Model B", "Model B": "Model A"}.get(vote2_raw, vote2_raw)
    invalid = vote1_raw == "INVALID" or vote2 == "INVALID"
    flip = (not invalid) and vote1_raw != vote2
    winner = "INVALID" if invalid else ("TIE" if flip else vote1_raw)
    return winner, flip, invalid
'''


# ─────────────────────────────────────────────── H3: the E-COMB combiner source check ───────────────────────────────────────────────

def _git(repo, *args):
    import subprocess
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def _norm_fn(fn):
    """ast.dump of a FunctionDef with its docstring dropped and its parameters renamed p0, p1, ... (never executed)."""
    import copy
    fn = copy.deepcopy(fn)
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(getattr(fn.body[0], "value", None), ast.Constant) and isinstance(fn.body[0].value.value, str):
        fn.body = fn.body[1:]
    ren = {a.arg: "p%d" % i for i, a in enumerate(fn.args.args)}
    for a in fn.args.args: a.arg = ren[a.arg]
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and n.id in ren: n.id = ren[n.id]
    fn.name = "f"
    return ast.dump(fn, annotate_fields=False)


def _is_transposition(node):
    if not isinstance(node, ast.Dict) or len(node.keys) != 2: return False
    try:
        kv = {k.value: v.value for k, v in zip(node.keys, node.values)}
    except AttributeError:
        return False
    return kv == {"Model A": "Model B", "Model B": "Model A"}


def combiner_ok(fn, ref_fn=None):
    """(ok, why) for a combiner FunctionDef, H3(b) as amended at 94731da: verified ONLY IF AST-IDENTICAL (docstring and parameter names
    normalised) to the reference combine_orders: rejudge_grok.combine_orders at the pinned blob when given, else REF_COMBINE_ORDERS. No
    equivalence arm. The diagnostic printed on a failure (parameters, transposition dicts) decides nothing."""
    ref = ref_fn or next(n for n in ast.parse(REF_COMBINE_ORDERS).body if isinstance(n, ast.FunctionDef))
    if _norm_fn(fn) == _norm_fn(ref):
        return True, "AST-identical to rejudge_grok.combine_orders"
    return False, ("not AST-identical to rejudge_grok.combine_orders at the pinned blob (identity is the only arm, 94731da; diagnostic: %d "
                   "parameters, %d transposition dicts)" % (len(fn.args.args), sum(1 for n in ast.walk(fn) if _is_transposition(n))))


def _pin_commit(repo, relpath, when_iso):
    rc, out = _git(repo, "log", "-1", "--format=%H %cI", "--before=" + when_iso, "--", relpath)
    return (out.split() if rc == 0 and out.strip() else None)


def combiner_check(con, path, spec, rows, ctx=None):
    """H3 (0104e44). -> dict(ok, writer, pin, evidence, result). Read-only git; ast only; nothing executed."""
    ctx = ctx or {}
    repo = ctx.get("repo", ROOT); writers = ctx.get("writers", COMB_WRITER)
    out = dict(ok=False, writer=None, pin=None, evidence=[], result=[])
    w = writers.get(os.path.basename(path))
    if not w:
        out["result"].append("no writer named for %s in COMB_WRITER" % os.path.basename(path)); return out
    out["writer"] = w; relw = "%s/%s" % (WRITER_DIR, w); relrj = "%s/rejudge_grok.py" % WRITER_DIR
    msha = next(((k, meta_value(con, k)) for k in RUN_META_SHA_KEYS if meta_value(con, k)), None)
    pin = None; when = None
    started = meta_value(con, "started")
    t0 = None
    if started:
        try:
            t0 = time.mktime(time.strptime(str(started)[:19], "%Y-%m-%d %H:%M:%S")); src_t = "run_meta started %s (local time)" % started
        except ValueError:
            src_t = "run_meta started %r unparseable" % started
    else:
        ts = [r.get("ts") for r in rows if isinstance(r.get("ts"), (int, float))]
        t0 = min(ts) if ts else None
        src_t = ("min(%s.ts) = %.0f" % (spec["table"], t0)) if t0 is not None else "no run_meta started and no ts column"
    when_iso = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(t0)) if t0 is not None else None
    if msha:
        rc, log = _git(repo, "log", "--format=%H %cI", "--", relw)
        for line in (log.splitlines() if rc == 0 else []):
            h, ci = line.split()
            rc2, src = _git(repo, "show", "%s:%s" % (h, relw))
            b = src.encode("utf-8").replace(b"\r\n", b"\n")
            if rc2 == 0 and str(msha[1]).startswith(hashlib.sha256(b).hexdigest()[:len(str(msha[1]))]):
                pin, when = h, ci; break
        out["evidence"].append("run_meta %s = %s -> %s" % (msha[0], msha[1], ("commit %s (%s)" % (pin[:12], when)) if pin else "NO commit of %s has that sha" % relw))
    else:
        if t0 is not None:
            pc = _pin_commit(repo, relw, when_iso)
            if pc: pin, when = pc
            else:
                rcf, first = _git(repo, "log", "--reverse", "--format=%cI", "--", relw)
                first = first.split()[0] if rcf == 0 and first.split() else None
                out["pin_timing"] = first is not None      # the writer HAS commits and the first write precedes the earliest one
                if first: out["evidence"].append("the writer's earliest commit is %s, after the first write: PIN TIMING" % first)
            out["evidence"].append("first write %s = %s UTC -> last commit of %s at or before it: %s" % (src_t, when_iso, relw, ("%s (%s)" % (pin[:12], when)) if pin else "NONE"))
        else:
            out["evidence"].append("first write unknown (%s)" % src_t)
    if not pin:
        out["result"].append("the writer's run-time blob cannot be pinned"); return out
    out["pin"] = pin
    rj_when = when_iso or when          # rejudge_grok at the SAME run-time pin: the first write; the writer's commit time only if unknown
    out["evidence"].append("run-time pin for rejudge_grok: %s (%s)" % (rj_when, "the first write, %s" % src_t if when_iso else "the writer's commit time; first write unknown"))
    rc, src = _git(repo, "show", "%s:%s" % (pin, relw))
    if rc != 0:
        out["result"].append("git show %s:%s failed" % (pin[:12], relw)); return out
    tree = ast.parse(src)
    alias = {}; from_rj = set(); local = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: alias[a.asname or a.name] = a.name
        elif isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok":
            for a in n.names:
                if a.name == "combine_orders": from_rj.add(a.asname or a.name)
    tamper = module_tampering(tree, alias, from_rj)
    if tamper:
        out["result"].append("the writer rebinds or patches rejudge_grok, or runs dynamic code (D-C, 776a2dd): %s" % "; ".join(tamper[:6])); return out
    tamper_p = module_tampering_prime(tree, alias, from_rj)
    if tamper_p:
        out["result"].append("the writer rebinds or patches rejudge_grok, or runs dynamic code (D-C', VFC-DC-PRIME): %s" % "; ".join(tamper_p[:6])); return out
    tamper_d1 = module_tampering_d1(tree, alias, from_rj)
    if tamper_d1:
        out["result"].append("the writer rebinds or patches rejudge_grok, or runs dynamic code (D1 routes, VFC-FIXES-2): %s" % "; ".join(tamper_d1[:6])); return out
    tamper_t, scanned = transitive_tampering(repo, tree, rj_when, relw)
    out["evidence"].append("local imports scanned transitively at the run-time pin %s (D-C' (f)): %s" % (rj_when, ", ".join(scanned) or "none"))
    if tamper_t:
        out["result"].append("a local module the writer imports rebinds or patches rejudge_grok, or runs dynamic code (D-C' (f), VFC-DC-PRIME): %s"
                             % "; ".join(tamper_t[:6])); return out
    calls = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and (
             (isinstance(c.func, ast.Attribute) and "combine" in c.func.attr) or (isinstance(c.func, ast.Name) and "combine" in c.func.id))]
    if not calls:
        out["result"].append("no combiner call found in %s at %s" % (w, pin[:12])); return out
    rj_box = []
    def pinned_rj():
        """rejudge_grok.combine_orders at the run-time pin (the reference of the amended H3(b)); None if it cannot be pinned."""
        if not rj_box:
            pr = _pin_commit(repo, relrj, rj_when)
            fn = None
            if pr:
                rc3, rsrc = _git(repo, "show", "%s:%s" % (pr[0], relrj))
                fn = next((n for n in ast.parse(rsrc).body if isinstance(n, ast.FunctionDef) and n.name == "combine_orders"), None) if rc3 == 0 else None
                out["evidence"].append("rejudge_grok.py pinned at %s (%s)" % (pr[0][:12], pr[1]))
            else:
                out["evidence"].append("rejudge_grok.py cannot be pinned at or before %s" % rj_when)
            rj_box.append(fn)
        return rj_box[0]
    oks = []
    for c in calls:
        if isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) and alias.get(c.func.value.id) == "rejudge_grok" and c.func.attr == "combine_orders" \
                or isinstance(c.func, ast.Name) and c.func.id in from_rj:
            rfn = pinned_rj()
            if rfn is None:
                oks.append(False); out["result"].append("L%d rejudge_grok.combine_orders: rejudge_grok.py cannot be pinned at or before %s, or has no "
                                                        "combine_orders there" % (c.lineno, rj_when)); continue
            same, _ = combiner_ok(rfn)          # D-A (776a2dd): the pinned body must be the recipe's REF for a direct call to verify
            oks.append(same)
            out["result"].append(("L%d rejudge_grok.combine_orders: AST-identical to rejudge_grok.combine_orders (a direct call)" % c.lineno) if same else
                                 ("L%d rejudge_grok.combine_orders: a direct call, but the pinned rejudge_grok body is NOT AST-identical to the recipe's "
                                  "combine_orders (REF): not verified" % c.lineno))
        elif isinstance(c.func, ast.Name) and c.func.id in local:
            rfn = pinned_rj()
            if rfn is None:
                oks.append(False); out["result"].append("L%d local %s: no pinned rejudge_grok.combine_orders to compare with" % (c.lineno, c.func.id)); continue
            ok, why = combiner_ok(local[c.func.id], rfn)
            ref_same, _ = combiner_ok(rfn)
            oks.append(ok and ref_same)
            out["result"].append("L%d local %s: %s; the pinned rejudge_grok body %s the recipe's combine_orders (REF)%s"
                                 % (c.lineno, c.func.id, why, "IS AST-identical to" if ref_same else "is NOT AST-identical to",
                                    "" if ref_same else ": not verified"))
        else:
            oks.append(False); out["result"].append("L%d %s: a combiner that is neither rejudge_grok.combine_orders nor a local def cannot be verified"
                                                    % (c.lineno, ast.dump(c.func)[:60]))
    out["ok"] = bool(oks) and all(oks)
    out["callsite_ok"] = False; out["callsite"] = []
    if out["ok"]:
        out["callsite_ok"], out["callsite"] = callsite_check(tree, calls, spec, alias, from_pj(tree))
    return out


def module_tampering(tree, alias, from_rj):
    """D-C (776a2dd): every place the writer module stores to the rejudge_grok alias, assigns / deletes an attribute of it, rebinds a name
    from-imported from rejudge_grok, or calls setattr / delattr / exec / eval. -> list of findings (empty when clean). ast only."""
    rj_names = {k for k, v in alias.items() if v == "rejudge_grok"}
    from_names = set(from_rj) | {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok" for a in n.names}
    found = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)) and n.id in rj_names:
            found.append("L%d the alias %r is rebound" % (n.lineno, n.id))
        elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)) and n.id in from_names:
            found.append("L%d the from-imported name %r is rebound" % (n.lineno, n.id))
        elif isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)) and isinstance(n.value, ast.Name) and n.value.id in rj_names:
            found.append("L%d %s.%s is assigned" % (n.lineno, n.value.id, n.attr))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("setattr", "delattr", "exec", "eval"):
            found.append("L%d %s(...) is called" % (n.lineno, n.func.id))
    return found


DYN_CALLED = tuple("setattr delattr exec eval".split())   # a CALL to one of these is the D-C line of module_tampering
DYN_ANY = ("__import__", "globals", "vars")                # any reference at all (D-C' (b))
DUNDER_NAMES_OK = ("__name__", "__file__", "__doc__")


def _dunder(s):
    return len(s) > 4 and s.startswith("__") and s.endswith("__")


def module_tampering_prime(tree, alias, from_rj=()):
    """D-C' (VFC-DC-PRIME, review ae88d3a): the dynamic-rebinding routes the D-C denylist (module_tampering) does not see; disjoint from it, so
    each route is decided here or there, never both. -> list of findings (empty when clean). ast only, nothing executed. Conservative: a
    finding may be harmless (a false FAIL), never the reverse by these routes."""
    rj_names = {k for k, v in alias.items() if v == "rejudge_grok"}
    from_names = set(from_rj) | {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok" for a in n.names}
    sys_names = {k for k, v in alias.items() if v == "sys"}
    par = {}
    for n in ast.walk(tree):
        for ch in ast.iter_child_nodes(n): par[ch] = n
    found = []
    for n in ast.walk(tree):
        # (b) a reference that is not a call to setattr / delattr / exec / eval; any reference to __import__ / globals / vars
        if isinstance(n, ast.Name) and n.id in DYN_CALLED and not (isinstance(par.get(n), ast.Call) and par[n].func is n):
            found.append("L%d %s is referenced, not called (an alias of it rebinds unseen)" % (n.lineno, n.id))
        elif isinstance(n, ast.Name) and n.id in DYN_ANY:
            found.append("L%d %s is referenced" % (n.lineno, n.id))
        # (c) a dunder name other than __name__ / __file__ / __doc__
        elif isinstance(n, ast.Name) and _dunder(n.id) and n.id not in DUNDER_NAMES_OK:
            found.append("L%d the dunder name %s is referenced" % (n.lineno, n.id))
        # (b) an attribute named like one of the seven (builtins.setattr, builtins.exec)
        elif isinstance(n, ast.Attribute) and n.attr in DYN_CALLED + DYN_ANY:
            found.append("L%d an attribute named %s is referenced" % (n.lineno, n.attr))
        # (c) any dunder attribute, loaded or stored (object.__setattr__, rj.__dict__, f.__code__, f.__globals__)
        elif isinstance(n, ast.Attribute) and _dunder(n.attr):
            found.append("L%d the dunder attribute .%s is referenced" % (n.lineno, n.attr))
        # (d) sys.modules
        elif isinstance(n, ast.Attribute) and n.attr == "modules" and isinstance(n.value, ast.Name) and n.value.id in sys_names:
            found.append("L%d %s.modules is referenced" % (n.lineno, n.value.id))
        # (e) the rejudge_grok alias used as a bare value (x = rj; f(rj); importlib.reload(rj))
        elif isinstance(n, ast.Name) and n.id in rj_names and isinstance(n.ctx, ast.Load) and not (isinstance(par.get(n), ast.Attribute) and par[n].value is n):
            found.append("L%d the alias %r is used as a value" % (n.lineno, n.id))
        # (a) a store / delete whose target chain passes through a call result or through rejudge_grok below the first attribute
        if isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, (ast.Store, ast.Del)) and not (
                isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in rj_names):      # rj.x = .. is the D-C line
            chain = []; x = n.value
            while True:
                chain.append(x)
                if isinstance(x, (ast.Attribute, ast.Subscript, ast.Starred)): x = x.value
                elif isinstance(x, ast.Call): x = x.func
                else: break
            if any(isinstance(c, ast.Call) for c in chain):
                found.append("L%d a store through a call result (%s)" % (n.lineno, ast.dump(n)[:60]))
            elif any(isinstance(c, ast.Name) and c.id in (rj_names | from_names) for c in chain):
                found.append("L%d a store through rejudge_grok (%s)" % (n.lineno, ast.dump(n)[:60]))
    # (d) importlib; `from sys import modules`; (e) a star import from rejudge_grok binds names unseen
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "importlib" for a in n.names):
            found.append("L%d importlib is imported" % n.lineno)
        elif isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "importlib":
            found.append("L%d importlib is imported" % n.lineno)
        elif isinstance(n, ast.ImportFrom) and n.module == "sys" and any(a.name in ("modules", "*") for a in n.names):
            found.append("L%d sys.modules is imported" % n.lineno)
        elif isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok" and any(a.name == "*" for a in n.names):
            found.append("L%d a star import from rejudge_grok" % n.lineno)
    # (e) any other binding of the alias or of a from-imported name: def / class / parameter / except-as / match capture / a second import
    bound = rj_names | from_names
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in bound:
            found.append("L%d %r is rebound by a def / class" % (n.lineno, n.name))
        elif isinstance(n, ast.arg) and n.arg in bound:
            found.append("L%d %r is rebound as a parameter" % (n.lineno, n.arg))
        elif isinstance(n, ast.ExceptHandler) and n.name in bound:
            found.append("L%d %r is rebound by except-as" % (n.lineno, n.name))
        elif isinstance(n, (getattr(ast, "MatchAs", ()), getattr(ast, "MatchStar", ()))) and getattr(n, "name", None) in bound:
            found.append("L%d %r is rebound by a match capture" % (n.lineno, n.name))
    targets = defaultdict(set)
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: targets[a.asname or a.name.split(".")[0]].add(a.name if a.asname else a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            for a in n.names: targets[a.asname or a.name].add("%s%s.%s" % ("." * n.level, n.module or "", a.name))
    for nm in sorted(bound):
        if len(targets.get(nm, ())) > 1:
            found.append("%r is imported as two different objects %s" % (nm, sorted(targets[nm])))
    return found


D1_MODULES = ("inspect", "gc", "pkgutil", "ctypes", "types", "runpy", "code", "codeop", "builtins")      # builtins: F5 (a3da968)
D1_ATTRS = ("f_globals", "f_locals", "f_builtins", "f_back", "currentframe", "_getframe", "resolve_name", "get_objects", "get_referrers",
            "get_referents", "FunctionType", "CodeType", "setitem", "delitem")
D1_BUILTIN_NAMES = ("compile",)
RJ_TARGET_NAMES = ("combine_orders", "parse_judge")


def module_tampering_d1(tree, alias, from_rj=()):
    """D1 (VFC-FIXES-2; review 9d3e261 u1-u7): the dynamic-rebinding routes D-C and D-C' do not see. -> list of findings (empty when clean).
    ast only, nothing executed; conservative (a finding may be harmless, a false FAIL). Stated limit: a route outside these lists."""
    rj_names = {k for k, v in alias.items() if v == "rejudge_grok"}
    from_names = set(from_rj) | {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok" for a in n.names}
    keys = rj_names | from_names | {"rejudge_grok"} | set(RJ_TARGET_NAMES)
    found = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] in D1_MODULES: found.append("L%d %s is imported (D1)" % (n.lineno, a.name))
        elif isinstance(n, ast.ImportFrom):
            if (n.module or "").split(".")[0] in D1_MODULES and not n.level:
                found.append("L%d %s is imported (D1)" % (n.lineno, n.module))
            for a in n.names:
                if a.name in D1_ATTRS: found.append("L%d %s is imported by name (D1)" % (n.lineno, a.name))
        elif isinstance(n, ast.Attribute) and n.attr in D1_ATTRS:
            found.append("L%d an attribute named %s is referenced (D1)" % (n.lineno, n.attr))
        elif isinstance(n, ast.Name) and n.id in D1_BUILTIN_NAMES:
            found.append("L%d the builtin %s is referenced (D1)" % (n.lineno, n.id))
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)) and n.attr in RJ_TARGET_NAMES and not (
                isinstance(n.value, ast.Name) and n.value.id in rj_names):          # rj.combine_orders = .. is the D-C line
            found.append("L%d an attribute named %s is stored on an object that is not the rejudge_grok alias (D1)" % (n.lineno, n.attr))
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)):
            k = n.slice.value if isinstance(n.slice, ast.Constant) else None
            if isinstance(k, str) and k in keys:
                found.append("L%d a store under the key %r (D1)" % (n.lineno, k))
    return found


def rj_self_bindings(tree):
    """D-C' (f): rejudge_grok.py itself carries AT MOST one def of combine_orders and of parse_judge and no other binding of either."""
    found = []
    for nm in ("combine_orders", "parse_judge"):
        defs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == nm]
        other = [n for n in ast.walk(tree) if (isinstance(n, ast.Name) and n.id == nm and isinstance(n.ctx, (ast.Store, ast.Del)))
                 or (isinstance(n, (ast.Import, ast.ImportFrom)) and any((a.asname or a.name) == nm for a in n.names))]
        if len(defs) > 1 or other:
            found.append("rejudge_grok binds %s %d times by def and %d times otherwise" % (nm, len(defs), len(other)))
    return found


PKG_ROOT = tuple(WRITER_DIR.split("/"))     # ("tools", "analysis"): a package-path import rooted here names a local module (D2)
BAD_PKG = "<bad-package-path>"               # marker: a package-path import rooted at `tools` that names no module under tools/analysis


def local_import_names(tree):
    """[(module name, line)] of every import in the module, at any depth: the top-level name; None for a relative import; for a package path
    rooted at `tools` (D2, 9d3e261) the module X under tools/analysis it names (`import tools.analysis.X`, `from tools.analysis import X`,
    `from tools.analysis.X import ..`), or BAD_PKG when it names none."""
    out = []
    def pkg(parts, line, names=()):
        if tuple(parts[:len(PKG_ROOT)]) == PKG_ROOT and len(parts) > len(PKG_ROOT):
            out.append((parts[len(PKG_ROOT)], line))
        elif tuple(parts) == PKG_ROOT and names:
            out.extend((x, line) for x in names)
        else:
            out.append((BAD_PKG, line))
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                parts = a.name.split(".")
                if parts[0] == PKG_ROOT[0]: pkg(parts, n.lineno)
                else: out.append((parts[0], n.lineno))
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                out.append((None, n.lineno)); continue
            parts = (n.module or "").split(".")
            if parts[0] == PKG_ROOT[0]: pkg(parts, n.lineno, [a.name for a in n.names if a.name != "*"] or [BAD_PKG])
            else: out.append((parts[0], n.lineno))
    return out


_INSTALLED = []


def installed_top_levels():
    """The top-level import names of the installed distributions (importlib.metadata; read once). The instrument's own use of importlib."""
    if not _INSTALLED:
        import importlib.metadata as md
        try: _INSTALLED.append(frozenset(md.packages_distributions()))
        except Exception: _INSTALLED.append(frozenset())
    return _INSTALLED[0]


def classify_import(repo, mod):
    """D2 (9d3e261), fail closed. -> ("local", relpath) | ("finding", why) | ("skip", why)."""
    relm = "%s/%s.py" % (WRITER_DIR, mod)
    rc, h = _git(repo, "log", "-1", "--format=%H", "--", relm)
    if rc == 0 and h.strip():
        return "local", relm
    d = os.path.join(repo, *WRITER_DIR.split("/"))
    if os.path.isfile(os.path.join(d, mod + ".py")) or os.path.isdir(os.path.join(d, mod)):
        return "finding", "%s is a local module on disk with no git history: it cannot be pinned (D2)" % (relm if os.path.isfile(os.path.join(d, mod + ".py"))
                                                                                                    else "%s/%s/" % (WRITER_DIR, mod))
    if mod in getattr(sys, "stdlib_module_names", ()):
        return "skip", "stdlib"
    if mod in installed_top_levels():
        return "skip", "installed distribution"
    return "finding", "the import %r is neither a local module with a history, nor stdlib, nor an installed distribution (D2)" % mod


def transitive_tampering(repo, tree, when, self_rel):
    """D-C' (f): every LOCAL module the writer imports (a module with a git history under WRITER_DIR), transitively, each at its last commit at or
    before `when` (the run-time pin of rejudge_grok), scanned by module_tampering + module_tampering_prime (+ rj_self_bindings for rejudge_grok).
    A local import that cannot be pinned, cannot be read or parsed, or a relative import, is a finding. -> (findings, scanned). Read-only git."""
    findings = []; scanned = []; seen = {self_rel}; queue = [tree]
    while queue:
        t = queue.pop(0)
        for mod, line in local_import_names(t):
            if mod is None:
                findings.append("L%d a relative import cannot be resolved" % line); continue
            if mod == BAD_PKG:
                findings.append("L%d a package-path import rooted at %r names no module under %s (D2)" % (line, PKG_ROOT[0], WRITER_DIR)); continue
            relm = "%s/%s.py" % (WRITER_DIR, mod)
            if relm in seen: continue
            seen.add(relm)
            kind, why = classify_import(repo, mod)     # D2 (9d3e261): fail closed; was `continue` on any import with no git history
            if kind == "finding":
                findings.append("L%d %s" % (line, why)); continue
            if kind == "skip": continue                # stdlib / an installed distribution: not scanned (stated limit)
            pc = _pin_commit(repo, relm, when) if when else None
            if not pc:
                findings.append("%s cannot be pinned at or before %s" % (relm, when)); continue
            rc2, src = _git(repo, "show", "%s:%s" % (pc[0], relm))
            try:
                mt = ast.parse(src) if rc2 == 0 else None
            except SyntaxError:
                mt = None
            if mt is None:
                findings.append("%s at %s cannot be read or parsed" % (relm, pc[0][:12])); continue
            malias = {a.asname or a.name: a.name for n in ast.walk(mt) if isinstance(n, ast.Import) for a in n.names}
            mfrom = {a.asname or a.name for n in ast.walk(mt) if isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok" for a in n.names
                     if a.name == "combine_orders"}
            f = module_tampering(mt, malias, mfrom) + module_tampering_prime(mt, malias, mfrom) + module_tampering_d1(mt, malias, mfrom) \
                + (rj_self_bindings(mt) if mod == "rejudge_grok" else [])
            scanned.append("%s.py@%s" % (mod, pc[0][:12]))
            findings += ["%s.py@%s %s" % (mod, pc[0][:12], x) for x in f]
            queue.append(mt)
    return findings, scanned


def from_pj(tree):
    """Names bound by `from rejudge_grok import parse_judge [as x]`."""
    return {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "rejudge_grok"
            for a in n.names if a.name == "parse_judge"}


def table_columns_from_source(tree, table):
    """The column names of `table` from a CREATE TABLE string constant in the writer's source (ast only), else None."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            m = re.search(r"CREATE TABLE (?:IF NOT EXISTS )?%s\s*\((.*)\)" % re.escape(table), n.value, re.S | re.I)
            if not m: continue
            body, depth, cur, parts = m.group(1), 0, "", []
            for ch in body:
                if ch == "(": depth += 1
                elif ch == ")": depth -= 1
                if ch == "," and depth == 0: parts.append(cur); cur = ""
                else: cur += ch
            parts.append(cur)
            cols = [x.split()[0] for x in (q.strip() for q in parts) if x and x.split()[0].upper() not in ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT")]
            return cols
    return None


def callsite_check(tree, calls, spec, alias, pj_names):
    """D2 (2c94cab), EXTENDED to order 1 by D-B (ae20138), ast only: for every combiner call and for EACH of its two arguments (the 2nd with the
    order-2 column, the 1st with the order-1 column): (i) the argument is a bare name stored at that column's index of every row tuple of the
    table's width built in the same function; (ii) that name's ONLY binding there is the first element of a tuple-unpack of a direct
    rejudge_grok.parse_judge call. -> (ok, lines). Stated limit (x2, ae20138): an order-2 name parsed from the ORDER-1 raw text passes both
    conditions; it shows in the data as a 100% flip rate on decisive rows."""
    lines = []; ok = True
    cols = table_columns_from_source(tree, spec["table"])
    if not cols or spec.get("v2") not in cols or spec.get("v1") not in cols:
        return False, ["cannot parse: no CREATE TABLE %s carrying %s and %s in the writer's source" % (spec["table"], spec.get("v1"), spec.get("v2"))]
    fns = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    rj_names = {k for k, v in alias.items() if v == "rejudge_grok"}
    def is_pj(call):
        return isinstance(call, ast.Call) and ((isinstance(call.func, ast.Attribute) and call.func.attr == "parse_judge" and isinstance(call.func.value, ast.Name)
                                                and call.func.value.id in rj_names) or (isinstance(call.func, ast.Name) and call.func.id in pj_names))
    for c, argi, col, ordn in [(c, argi, col, ordn) for c in calls for argi, col, ordn in ((1, spec["v2"], "order-2"), (0, spec["v1"], "order-1"))]:
        scope = min((f for f in fns if any(x is c for x in ast.walk(f))), key=lambda f: sum(1 for _ in ast.walk(f)), default=tree)
        where = "L%d" % c.lineno; nth = "2nd" if argi == 1 else "1st"; ic = cols.index(col)
        if len(c.args) < 2 or not isinstance(c.args[argi], ast.Name):
            ok = False; lines.append("%s (i) the %s argument is not a bare name: %s" % (where, nth, ast.dump(c.args[argi])[:70] if len(c.args) > argi else "(missing)")); continue
        name = c.args[argi].id
        rows_t = [t for t in ast.walk(scope) if isinstance(t, ast.Tuple) and len(t.elts) == len(cols)]
        if not rows_t:
            ok = False; lines.append("%s cannot parse: no row tuple of the table's %d columns in the calling function" % (where, len(cols))); continue
        stored = [t.elts[ic].id if isinstance(t.elts[ic], ast.Name) else ast.dump(t.elts[ic])[:40] for t in rows_t]
        if any(x != name for x in stored):
            ok = False; lines.append("%s (i) the %s column (%s, index %d) stores %s, not the name %r passed as the combiner's %s argument"
                                     % (where, ordn, col, ic, stored, name, nth)); continue
        binds = []
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)) and name in [a.arg for a in scope.args.args + scope.args.kwonlyargs]:
            binds.append("a parameter")
        for n in ast.walk(scope):
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
                for tg in tgts:
                    if isinstance(tg, ast.Name) and tg.id == name:
                        binds.append(("aug" if isinstance(n, ast.AugAssign) else "plain", n))
                    elif isinstance(tg, ast.Tuple):
                        for k, e in enumerate(tg.elts):
                            if isinstance(e, ast.Name) and e.id == name: binds.append(("tuple%d" % k, n))
            elif isinstance(n, (ast.For, ast.comprehension, ast.With, ast.NamedExpr)):
                if name in {x.id for x in ast.walk(n.target if hasattr(n, "target") else n) if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store)}:
                    binds.append(("loop/with/walrus", n))
        if len(binds) != 1 or binds[0] == "a parameter":
            ok = False; lines.append("%s (ii) %r (%s) has %d bindings in its function (exactly one, from parse_judge, is required)" % (where, name, ordn, len(binds))); continue
        kind, node = binds[0]
        if kind != "tuple0" or not is_pj(node.value):
            ok = False; lines.append("%s (ii) %r (%s) is not bound as the first element of a tuple-unpack of a direct rejudge_grok.parse_judge call (%s: %s)"
                                     % (where, name, ordn, kind, ast.dump(node.value)[:70])); continue
        lines.append("%s (i) %s column %s stores %r = the combiner's %s argument; (ii) %r bound directly from parse_judge at L%d"
                     % (where, ordn, col, name, nth, name, node.lineno))
    return ok, lines


# ─────────────────────────────────────────────────────────── read-only access ───────────────────────────────────────────────────────────

def ro_uri(path):
    return "file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/")


def open_ro(path):
    """The ONLY way this instrument (and position_index_all.py) opens a SQLite file."""
    uri = ro_uri(path)
    if not ("mode=ro" in uri and "immutable=1" in uri):          # explicit raises, never assert: they must survive python -O
        raise SystemExit("[RO] REFUSED: %s is not a read-only immutable URI" % uri)
    con = sqlite3.connect(uri, uri=True)
    con.execute("PRAGMA query_only=1")
    if int(con.execute("PRAGMA query_only").fetchone()[0]) != 1:
        con.close()
        raise SystemExit("[RO] REFUSED: PRAGMA query_only did not read back 1 on %s" % path)
    return con


def is_sqlite(path):
    try:
        with open(path, "rb") as f:
            return f.read(16) == SQLITE_MAGIC
    except OSError:
        return False


def stat_of(path):
    out = {}
    for suf in ("", "-wal", "-shm"):
        p = path + suf
        if os.path.exists(p):
            st = os.stat(p); out[suf or "db"] = (st.st_size, st.st_mtime_ns)
    return out


def sha256_16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:16]


def rel(p, root=None):
    try: return os.path.relpath(p, root or DATA_ROOT).replace("\\", "/")
    except ValueError: return str(p).replace("\\", "/")


def script_shas(path=None):
    """(sha256[:16] of the LF rendering, sha256[:16] of the bytes as checked out) — LF is the identity of record."""
    b = open(os.path.abspath(path or __file__), "rb").read()
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()[:16], hashlib.sha256(b).hexdigest()[:16]


def source_constant(script, name):
    """A module-level string constant read from a writer's SOURCE by ast (never imported)."""
    tree = ast.parse(open(os.path.join(HERE, script), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    raise SystemExit("[SOURCE] %s has no module-level string constant %s" % (script, name))


# ─────────────────────────────────────────────────────────── enumeration ───────────────────────────────────────────────────────────

def scan_sqlite_files(root):
    out = []
    er = os.path.join(root, "experiment_results")
    for dp, dns, fns in os.walk(er):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if os.path.isfile(p) and is_sqlite(p): out.append(p)
    for fn in sorted(os.listdir(root)):
        p = os.path.join(root, fn)
        if os.path.isfile(p) and is_sqlite(p): out.append(p)
    return out


def table_columns(con):
    tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    return {t: [(r[1], int(r[5] or 0)) for r in con.execute('PRAGMA table_info("%s")' % t.replace('"', '""'))] for t in tabs}


def read_schema(con):
    """-> {table: spec} for the dual-order candidate tables, from the schema only."""
    out = {}
    for t, cols in table_columns(con).items():
        names = [c for c, _ in cols]; low = {c.lower(): c for c in names}
        pk = [c for c, k in sorted(cols, key=lambda x: x[1]) if k]
        vpair = [c for c in names if VOTE_PAIR_RE.match(c)]
        rpair = [c for c in names if RAW_PAIR_RE.match(c)]
        okey = next((low[k] for k in ORDER_KEY_COLS if k in low), None)
        svote = next((low[k] for k in SINGLE_VOTE_COLS if k in low), None)
        sraw = next((low[k] for k in SINGLE_RAW_COLS if k in low), None)
        spec = None
        if len(vpair) >= 2 or len(rpair) >= 2:
            def pick(cands, rx, first):
                for c in cands:
                    m = rx.match(c)
                    if m and ((m.group(2).lower() in ORDER1_SUFFIX) == first): return c
                return None
            comb = next(((low[w], low.get(f)) for w, f in COMBINED_SPECS if w in low), (None, None))
            spec = dict(kind="WIDE", order_key="COLUMN-ORDINAL", v1=pick(vpair, VOTE_PAIR_RE, True), v2=pick(vpair, VOTE_PAIR_RE, False),
                        r1=pick(rpair, RAW_PAIR_RE, True), r2=pick(rpair, RAW_PAIR_RE, False), win=comb[0], flip=comb[1],
                        cond=okey, invalid=low.get("invalid"))
        elif okey and (svote or sraw):
            spec = dict(kind="LONG", order_key="ARM-VALUE", key=okey, vote=svote, raw=sraw,
                        finish=low.get("finish") or low.get("finish_reason"))
        if spec is None: continue
        spec.update(table=t, columns=names, pk=pk, match_key=next((low[k] for k in MATCH_KEY_COLS if k in low), None),
                    qid=next((low[k] for k in QID_COLS if k in low), None),
                    names=(low["model_a"], low["model_b"]) if "model_a" in low and "model_b" in low else None,
                    foreign=[low[c] for c in FOREIGN_COLS if c in low])
        out[t] = spec
    return out


def meta_rows(con):
    out = []
    for t in ("run_meta", "meta"):
        try: rows = con.execute('SELECT * FROM "%s"' % t).fetchall()
        except sqlite3.Error: continue
        out += [r for r in rows if len(r) >= 2]
    return out


def run_meta_pools(con):
    return ["%s=%s" % (r[0], r[1]) for r in meta_rows(con) if r[0] is not None and "pool" in str(r[0]).lower()]


def meta_value(con, key):
    for r in meta_rows(con):
        if r[0] == key: return r[1]
    return None


# ─────────────────────────────────────────────────────────── the frame test ───────────────────────────────────────────────────────────

def T(v):
    return {"Model A": "Model B", "Model B": "Model A"}.get(v, v)


def parse(raw):
    return rj.parse_judge(rr.strip_think(raw or ""))[0]


def combine_contestant(v1, v2):
    """combine_orders' twin under the CONTESTANT hypothesis: the stored order-2 vote is already transposed."""
    invalid = v1 == "INVALID" or v2 == "INVALID"
    flip = (not invalid) and v1 != v2
    return ("INVALID" if invalid else ("TIE" if flip else v1)), flip, invalid


def classify(n1_inf, n1_agree, n2_inf, n2_pos, n2_con):
    """Order 1 cannot DISCRIMINATE the frames but can REFUTE both: on order 1 both hypotheses predict stored == re-parse, so any
    order-1 contradiction is MIXED (READY review 14edeb4, B1). Order 2 discriminates."""
    if n1_agree != n1_inf:
        return "MIXED"
    pos_ok = n2_pos == n2_inf
    con_ok = n2_con == n2_inf
    if n2_inf == 0:
        return "AMBIGUOUS"
    if pos_ok and not con_ok: return "CERTIFIED-POSITIONAL"
    if con_ok and not pos_ok: return "CERTIFIED-CONTESTANT"
    if pos_ok and con_ok: return "AMBIGUOUS"
    return "MIXED"


def rowkey(spec, row):
    ks = spec.get("pk") or [c for c in (spec.get("match_key"), spec.get("key")) if c]
    return "|".join(str(row.get(k)) for k in ks) if ks else str(row.get("_rowid_"))


def fetch_rows(con, table):
    try:
        cur = con.execute('SELECT rowid AS _rowid_, * FROM "%s"' % table)
    except sqlite3.OperationalError:          # a WITHOUT ROWID table: its primary key is the row id
        cur = con.execute('SELECT * FROM "%s"' % table)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur]


def schedule_map(con, key, cols):
    """{key value: {col: value}} from a `schedule` table carrying `key` and every col, else None."""
    tc = table_columns(con)
    if "schedule" not in tc: return None
    have = {c for c, _ in tc["schedule"]}
    if key not in have or any(c not in have for c in cols): return None
    return {r[0]: dict(zip(cols, r[1:])) for r in con.execute('SELECT "%s", %s FROM schedule' % (key, ", ".join('"%s"' % c for c in cols)))}


_SHA_MEMO = {}


def sha256_full(path):
    """The full sha256 hex of a file's bytes, memoised on (absolute path, size, mtime_ns). Reads bytes only; opens no database."""
    st = os.stat(path); k = (os.path.abspath(path), st.st_size, st.st_mtime_ns)
    if k not in _SHA_MEMO:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
        _SHA_MEMO[k] = h.hexdigest()
    return _SHA_MEMO[k]


def name_profile_of(path, content_map=None):
    """VFC-NAME-PROFILE-BY-CONTENT (abf4db5 D1): -> (NAME_PROFILES key or None, how it was found). CONTENT first (the full sha256 of the file
    matched against the certified originals), then the file basename (the pre-existing key)."""
    cmap = NAME_PROFILE_CONTENT if content_map is None else content_map
    hit = cmap.get(sha256_full(path)) if cmap else None
    if hit is not None:
        return hit[0], "content sha256 %s = the certified original %s" % (sha256_full(path)[:16], hit[1])
    b = os.path.basename(path)
    if b in NAME_PROFILES:
        return b, "basename %s" % b
    return None, None


def name_resolver_long(con, path, content_map=None):
    key, _how = name_profile_of(path, content_map)
    prof = NAME_PROFILES.get(key) if key else None
    if prof is None: return None, None
    cols = [prof["second"]] + ([prof["first"][1]] if prof["first"][0] == "col" else [])
    sm = schedule_map(con, prof["key"], cols)
    if sm is None: return None, "profile %s: schedule table lacks %s" % (key, cols)
    const = source_constant(prof["first"][1], prof["first"][2]) if prof["first"][0] == "const" else None
    def resolve(row):
        s = sm.get(row.get(prof["key"]))
        if s is None: return None
        return (const if const is not None else s[prof["first"][1]]), s[prof["second"]]
    desc = "names: order-1 first = %s, second = schedule.%s (joined on %s)" % (
        ("%s.%s = %r" % (prof["first"][1], prof["first"][2], const)) if const is not None else "schedule." + prof["first"][1], prof["second"], prof["key"])
    return resolve, desc


def name_resolver_wide(con, spec):
    if spec.get("names"):
        a, b = spec["names"]
        return (lambda row: (row.get(a), row.get(b))), "names from the row's %s / %s" % (a, b)
    mk = spec.get("match_key")
    if mk:
        for key in (mk, "mid", "match_id"):
            sm = schedule_map(con, key, ["model_a", "model_b"])
            if sm is not None:
                def res(row, sm=sm, mk=mk):
                    s = sm.get(row.get(mk))
                    return (s["model_a"], s["model_b"]) if s else None
                return res, "names from schedule.model_a / model_b joined on %s" % key
    return None, None


def to_order1_frame(label, names):
    """A stored label -> a position label in ORDER-1's frame: position labels pass through; a contestant name maps to the position
    that contestant held in order 1 (names = (first-shown-in-order-1, other)); None if unresolvable."""
    if label in POS or label in ("TIE", "INVALID"): return label
    if label is None: return "INVALID"
    if names and label == names[0]: return "Model A"
    if names and label == names[1]: return "Model B"
    return None


def long_label(row, vote_col):
    """A LONG row's stored label; a row its writer flagged invalid=1 is INVALID whatever label it carries (arena13.py L119-L121,
    placebo_entry.py L126-L127 and ref_gated_rubric store an unparsed vote as "TIE" with invalid=1)."""
    if row.get("invalid") not in (None, 0, "0"): return "INVALID"
    return row.get(vote_col)


class Tally:
    def __init__(self):
        self.n_rows = 0; self.n1_inf = self.n1_agree = 0; self.n2_inf = self.n2_pos = self.n2_con = 0
        self.inv_on_decisive = self.decisive_on_nondecisive = self.unresolvable = 0
        self.unresolvable_inf = 0; self.unres_values = Counter()      # F1 (a3da968): E-COMB, on rows with both votes decisive; the labels seen
        self.bad1 = []; self.bad_pos = []; self.bad_con = []

    def order1(self, key, stored, parsed):
        if parsed in POS and stored != "INVALID":
            self.n1_inf += 1
            if stored == parsed: self.n1_agree += 1
            elif len(self.bad1) < 20: self.bad1.append(key)
        self._side(stored, parsed)

    def order2(self, key, stored, parsed):
        if parsed in POS and stored != "INVALID":
            self.n2_inf += 1
            if stored == parsed: self.n2_pos += 1
            elif len(self.bad_pos) < 20: self.bad_pos.append(key)
            if stored == T(parsed): self.n2_con += 1
            elif len(self.bad_con) < 20: self.bad_con.append(key)
        self._side(stored, parsed)

    def comb(self, key, hit_pos, hit_con):
        self.n2_inf += 1
        if hit_pos: self.n2_pos += 1
        elif len(self.bad_pos) < 20: self.bad_pos.append(key)
        if hit_con: self.n2_con += 1
        elif len(self.bad_con) < 20: self.bad_con.append(key)

    def _side(self, stored, parsed):
        if parsed in POS and stored == "INVALID": self.inv_on_decisive += 1
        if parsed not in POS and stored in POS: self.decisive_on_nondecisive += 1

    def klass(self):
        return classify(self.n1_inf, self.n1_agree, self.n2_inf, self.n2_pos, self.n2_con)

    def counts(self):
        return dict(rows=self.n_rows, order1_informative=self.n1_inf, order1_agree=self.n1_agree, order2_informative=self.n2_inf,
                    agree_positional=self.n2_pos, agree_contestant=self.n2_con, stored_invalid_on_decisive_parse=self.inv_on_decisive,
                    stored_decisive_on_nondecisive_parse=self.decisive_on_nondecisive, unresolvable_labels=self.unresolvable,
                    contradict_order1=self.bad1, contradict_positional=self.bad_pos, contradict_contestant=self.bad_con)


def comb_tally(rows, spec, v1f, v2f, resolve):
    """E-COMB over rows: v1f / v2f give the two per-order votes, resolve gives the row's names for a name-labelled winner."""
    t = Tally()
    for row in rows:
        t.n_rows += 1
        v1, v2 = v1f(row), v2f(row)
        w = row.get(spec["win"])
        wn = to_order1_frame(w, resolve(row) if resolve else None)
        if wn is None:          # R-2 "whatever the parse of the row" (F1, review a3da968): counted BEFORE the decisive-vote gate
            t.unresolvable += 1; t.unres_values[str(w)] += 1
            if v1 in POS and v2 in POS: t.unresolvable_inf += 1          # R-6's "n resolved of m informative" counts these only
            continue
        if v1 not in POS or v2 not in POS: continue
        if wn == "INVALID": continue
        wp, fp, _ = rj.combine_orders(v1, v2); wc, fc, _ = combine_contestant(v1, v2)
        fl = row.get(spec["flip"]) if spec.get("flip") else None
        hit_p = wn == wp and (fl is None or bool(int(fl)) == fp)
        hit_c = wn == wc and (fl is None or bool(int(fl)) == fc)
        t.comb(rowkey(spec, row), hit_p, hit_c)
    return t


def long_key_fn(spec):
    """The match key of a LONG table's row (the NOT-DUAL-ORDER rule and the index's pairing use the same one)."""
    cols = spec["columns"]; key = spec["key"]
    if spec.get("match_key"):
        mk = spec["match_key"]; return (lambda r: r.get(mk)), mk
    jc = ("snapshot_id", "eval_question_id", "model_a", "model_b")
    if all(c in cols for c in jc):
        jc = jc + tuple(c for c in ("judge_model", "recipe", "node_id") if c in cols)      # review 14edeb4 H2: never pair across judges
        return (lambda r: tuple(r.get(c) for c in jc)), "(%s)" % ", ".join(jc)
    pk = [c for c in spec.get("pk") or [] if c != key]
    if pk:
        return (lambda r: tuple(r.get(c) for c in pk)), "primary key without %s %s" % (key, pk)
    return (lambda r: r.get("_rowid_")), "rowid (no match key: every row is its own match)"


def order1_note(u, t):
    if t.n1_agree != t.n1_inf:
        u["notes"].append("ORDER-1 CONTRADICTION -> MIXED: order 1's stored vote differs from its own re-parse on %d of %d informative rows (both "
                          "hypotheses predict equality; first ids %s)" % (t.n1_inf - t.n1_agree, t.n1_inf, t.bad1))


def r6_downgrade(u, t, resolved_desc, tally):
    """R-2 / R-4 / R-5 / R-9 (VFC-RX-RULING): the unit is UNCERTIFIABLE (R6); the resolved-subset class and counts are printed beside,
    DESCRIPTIVE (they decide nothing). Called only when the resolved rows are not MIXED (R-3). F7 (a3da968): the resolved counts are printed per
    order, never summed across orders."""
    u["notes"].append("R6 stored labels unresolvable: %d unresolvable label(s) on the deciding tally (%s; labels %s); the resolved subset (%s) reads %s, "
                      "DESCRIPTIVE, decides nothing -> UNCERTIFIABLE (R6): UNCERTIFIABLE by instrument knowledge (a name-profile gap), not by frame"
                      % (t.unresolvable, tally, top_values(t), resolved_desc, u["klass"]))
    u.update(resolved_klass=u["klass"], klass="UNCERTIFIABLE", uncert_reason="R6", label_space="unresolved", unresolvable_values=top_values(t))


def top_values(t, k=5):
    """The (at most k) most frequent unresolvable stored labels with their counts: what (ii) must read when a class moves to R6."""
    return [[v, n] for v, n in t.unres_values.most_common(k)]


def certify_table(con, path, spec, comb_ctx=None):
    """-> unit dict: class, evidence, counts, and the frame fields the index needs."""
    rows = fetch_rows(con, spec["table"])
    u = dict(table=spec["table"], kind=spec["kind"], order_key=spec["order_key"], columns=spec["columns"], pk=spec["pk"],
             match_key=spec.get("match_key"), qid=spec.get("qid"), foreign=spec.get("foreign"), n_rows=len(rows), parser=PARSER_NAME,
             label_space="positions", names_desc=None, secondary=None, notes=[])
    if spec["kind"] == "WIDE":
        u.update(v1=spec["v1"], v2=spec["v2"], r1=spec["r1"], r2=spec["r2"], win=spec["win"], flip=spec["flip"], cond=spec["cond"])
        if spec["cond"]:
            u["cond_values"] = dict(Counter(str(r.get(spec["cond"])) for r in rows))
        resolve, ndesc = name_resolver_wide(con, spec)
        has_votes = bool(spec["v1"] and spec["v2"]); has_raw = bool(spec["r1"] and spec["r2"])
        full = lambda v: v not in (None, "")
        dual_rows = sum(1 for r in rows if (has_votes and full(r.get(spec["v1"])) and full(r.get(spec["v2"]))) or
                        (has_raw and full(r.get(spec["r1"])) and full(r.get(spec["r2"]))))
        u["dual_rows"] = dual_rows
        if dual_rows == 0:
            u.update(evidence="none", klass=NDO, counts=dict(rows=len(rows), dual_rows=0), positional_cols=[], contestant_cols=[])
            u["notes"].append("NOT-DUAL-ORDER: no row carries both orders (row-level rule, ruling (4))")
            return u
        tr = tc = None
        if has_votes and has_raw:
            tr = Tally()
            for row in rows:
                tr.n_rows += 1; k = rowkey(spec, row)
                tr.order1(k, row.get(spec["v1"]), parse(row.get(spec["r1"])))
                tr.order2(k, row.get(spec["v2"]), parse(row.get(spec["r2"])))
        if spec["win"] and (has_votes or has_raw):
            if has_votes:
                tc = comb_tally(rows, spec, lambda r: r.get(spec["v1"]), lambda r: r.get(spec["v2"]), resolve)
            else:
                tc = comb_tally(rows, spec, lambda r: parse(r.get(spec["r1"])), lambda r: parse(r.get(spec["r2"])), resolve)
            if ndesc and any(r.get(spec["win"]) not in POS + ("TIE", "INVALID", None) for r in rows):
                u["combined_label_space"] = ndesc
        if tr is not None:
            u.update(evidence="E-RAW", klass=tr.klass(), counts=tr.counts())
            order1_note(u, tr)
            if tc is not None:
                u["secondary"] = dict(evidence="E-COMB", klass=tc.klass(), counts=tc.counts())
                if tc.unresolvable:      # R-6 (VFC-RX-RULING): never CERTIFIED on a resolved subset; its resolved rows keep the power to downgrade
                    u["secondary"].update(klass="UNCERTIFIABLE", uncert_reason="R6", resolved_klass=tc.klass(), resolved=tc.n2_inf,
                                          informative=tc.n2_inf + tc.unresolvable_inf, unresolvable_values=top_values(tc))
                if u["klass"] in CERTIFIED and tc.klass() in CERTIFIED and tc.klass() != u["klass"]:
                    u["notes"].append("EVIDENCE CONFLICT: E-RAW %s, E-COMB %s%s -> MIXED" % (u["klass"], tc.klass(),
                                      " (on its resolved subset, %d of %d informative; R-6: the power to downgrade)" % (tc.n2_inf, tc.n2_inf + tc.unresolvable_inf)
                                      if tc.unresolvable else ""))
                    u["klass"] = "MIXED"
                elif tc.klass() == "MIXED":
                    u["notes"].append("WARNING: the stored combined column %s is MIXED against the stored votes (E-COMB); the per-order "
                                      "frame is decided by E-RAW" % spec["win"])
        elif tc is not None:
            u.update(evidence="E-COMB" if has_votes else "E-COMB(re-parsed raw)", klass=tc.klass(), counts=tc.counts())
            if not has_votes and u["klass"] == "CERTIFIED-CONTESTANT":      # B2 before R6 (R-3: a MIXED on the resolved rows is frame evidence)
                u["klass"] = "MIXED"
                u["notes"].append("RAW-ONLY: the combined column %s reproduces only the UNTRANSPOSED combine of votes re-parsed from raw text, "
                                  "which are positional by construction: combined column inconsistent with a positional recipe -> MIXED "
                                  "(review 14edeb4, B2)" % spec["win"])
            if tc.unresolvable and u["klass"] != "MIXED":         # R-2 / R-3: one or more unresolvable labels on the deciding (combined) tally
                r6_downgrade(u, tc, "order-2 informative %d, of which %d unresolvable labels sit on rows with both votes decisive"
                             % (tc.n2_inf, tc.unresolvable_inf), "combined column %s" % spec["win"])
                if has_votes and u["resolved_klass"] in CERTIFIED:      # F6 (a3da968): H3 run DESCRIPTIVELY; the class stays R6
                    cc = combiner_check(con, path, spec, rows, comb_ctx)
                    u["combiner_check_descriptive"] = cc
                    u["notes"].append("H3 on the R6 unit (DESCRIPTIVE, decides nothing; the class stays R6): combiner %s, call-site %s: %s"
                                      % ("PASS" if cc["ok"] else "FAIL", "PASS" if cc.get("callsite_ok") else ("FAIL" if cc["ok"] else "not reached"),
                                         "; ".join(cc["result"])[:300]))
            if has_votes and u["klass"] in CERTIFIED:          # H3 (0104e44): an E-COMB-only certificate needs a verified combiner
                cc = combiner_check(con, path, spec, rows, comb_ctx)
                u["combiner_check"] = cc
                if not cc["ok"]:
                    u["notes"].append("E-COMB, combiner not verified -> UNCERTIFIABLE (would have been %s): %s" % (u["klass"], "; ".join(cc["result"])))
                    u["klass"] = "UNCERTIFIABLE"; u["uncert_reason"] = "R2"
                    u["pin_timing"] = bool(cc.get("pin_timing"))
                elif not cc["callsite_ok"]:
                    u["notes"].append("E-COMB, call-site argument not verified -> UNCERTIFIABLE (would have been %s): %s" % (u["klass"], "; ".join(cc["callsite"])))
                    u["klass"] = "UNCERTIFIABLE"; u["uncert_reason"] = "R3"
            if not has_votes:
                u["votes_from_raw"] = True      # B2 (the RAW-ONLY CONTESTANT -> MIXED rule) is applied above, before R6
        else:
            u.update(evidence="none", klass="UNCERTIFIABLE", counts=dict(rows=len(rows)), uncert_reason="R1")
            u["notes"].append("no raw text of both orders and no combined column: nothing re-derivable" if has_votes else
                              "raw text of both orders but no stored vote and no combined column: nothing to certify")
        per_order = [c for c in (spec["v1"], spec["v2"]) if c] or [c for c in (spec["r1"], spec["r2"]) if c]
        if u["klass"] == "CERTIFIED-POSITIONAL":
            u["positional_cols"] = per_order
        else:
            u["positional_cols"] = per_order[:1] + ([c for c in (spec["r1"], spec["r2"]) if c] if spec["v1"] else [])
        u["contestant_cols"] = ([spec["v2"]] if u["klass"] == "CERTIFIED-CONTESTANT" and spec["v2"] else []) + \
                               (["%s (order-1 frame)" % spec["win"]] if spec["win"] and u["klass"] in CERTIFIED else [])
        return u
    # LONG
    u.update(key=spec["key"], vote=spec["vote"], raw=spec["raw"], finish=spec.get("finish"))
    vals = Counter(str(r.get(spec["key"])) for r in rows)
    u["arm_values"] = dict(vals)
    kf, kdesc = long_key_fn(spec)
    u["match_key_rule"] = kdesc
    per = defaultdict(set)
    for r in rows:
        a = str(r.get(spec["key"]))
        if a in ORDER_VOCAB: per[kf(r)].add(a)
    n_dual = sum(1 for v in per.values() if len(v) >= 2)
    u["dual_keys"] = n_dual
    if n_dual == 0:
        u.update(evidence="none", klass=NDO, counts=dict(rows=len(rows), dual_keys=0), pair=None, positional_cols=[], contestant_cols=[])
        u["notes"].append("NOT-DUAL-ORDER: no match key (%s) has rows under two or more order values; order-key values %s (row-level rule, ruling (4))"
                          % (kdesc, dict(vals)))
        return u
    pair = next((p for p in ORDER_PAIRS if any(p[0] in v and p[1] in v for v in per.values())), None)
    if pair is None:
        u.update(evidence="none", klass="UNCERTIFIABLE", counts=dict(rows=len(rows), dual_keys=n_dual), pair=None, uncert_reason="R5")
        u["notes"].append("rows reach two order values under no registered pair %s: nothing to certify" % [list(p) for p in ORDER_PAIRS])
        return u
    u["pair"] = list(pair); u["unpaired"] = {k: v for k, v in vals.items() if k not in pair}
    cnt = Counter((kf(r), str(r.get(spec["key"]))) for r in rows if str(r.get(spec["key"])) in pair)
    dups = sorted({k for (k, _), n in cnt.items() if n > 1}, key=str)
    single = sum(1 for v in per.values() if len(v & set(pair)) == 1)
    u["pairing"] = dict(keys=len(per), dual_keys=n_dual, duplicate_keys=len(dups), single_order_keys=single)
    if dups:
        u.update(evidence="none", klass="UNCERTIFIABLE", counts=dict(rows=len(rows), dual_keys=n_dual, duplicate_keys=len(dups)), uncert_reason="R4")
        u["notes"].append("DUPLICATE: %d match keys (%s) carry more than one row under one order value: the pairing is not unique -> REFUSED "
                          "(first %s)" % (len(dups), kdesc, [str(k) for k in dups[:10]]))
        return u
    if not spec["raw"] or not spec["vote"]:
        u.update(evidence="none", klass="UNCERTIFIABLE", counts=dict(rows=len(rows)), uncert_reason="R1")
        u["notes"].append("long frame without %s: nothing to re-parse and no combined column" % ("a raw column" if not spec["raw"] else "a vote column"))
        return u
    resolve, ndesc = name_resolver_long(con, path, (comb_ctx or {}).get("name_content"))
    u["name_profile"] = name_profile_of(path, (comb_ctx or {}).get("name_content"))[1]
    t = Tally()
    for row in rows:
        a = str(row.get(spec["key"]))
        if a not in pair: continue
        t.n_rows += 1
        names = resolve(row) if resolve else None
        stored = long_label(row, spec["vote"])
        x = to_order1_frame(stored, names)
        if x is None: t.unresolvable += 1; t.unres_values[str(stored)] += 1; continue
        if x in POS and stored not in POS: u["label_space"] = "names"
        p = parse(row.get(spec["raw"]))
        (t.order1 if a == pair[0] else t.order2)(rowkey(spec, row), x, p)
    u.update(evidence="E-RAW", klass=t.klass(), counts=t.counts(), names_desc=ndesc)
    order1_note(u, t)
    if t.unresolvable:
        u["notes"].append("%d stored labels are neither positions nor resolvable names%s" % (t.unresolvable, "" if ndesc else " (no name profile for this writer)"))
        if u["klass"] != "MIXED":       # R-2 / R-3 (VFC-RX-RULING): any unresolvable label on the pair's rows; MIXED on the resolved rows wins
            r6_downgrade(u, t, "order-1 informative %d, order-2 informative %d" % (t.n1_inf, t.n2_inf), "rows under the pair %s" % list(pair))
    u["positional_cols"] = ["%s (%s=%s)" % (spec["vote"], spec["key"], pair[0])] + (["%s (%s=%s)" % (spec["vote"], spec["key"], pair[1])] if u["klass"] == "CERTIFIED-POSITIONAL" else [])
    u["contestant_cols"] = ["%s (%s=%s)" % (spec["vote"], spec["key"], pair[1])] if u["klass"] == "CERTIFIED-CONTESTANT" else []
    return u


def cache_class(units):
    ks = [u["klass"] for u in units if u["klass"] != NDO]      # classed on its DUAL-ORDER tables (ruling (4)); single-order tables listed
    if not ks: return NDO
    cert = {k for k in ks if k in CERTIFIED}
    if "MIXED" in ks or len(cert) > 1: return "MIXED"
    if cert: return cert.pop()
    if "AMBIGUOUS" in ks: return "AMBIGUOUS"
    return "UNCERTIFIABLE"


# ─────────────────────────────────────────────────────── the index's reader (shared) ───────────────────────────────────────────────────────

def unit_votes(con, path, u, content_map=None):
    """Positional votes per match for a CERTIFIED unit, the certificate's transposition applied. REFUSES any other class.
    -> (list of dict(key, p1, p2, row), notes) where p1 / p2 are the POSITION named in order 1 / order 2 ("Model A" = first shown)."""
    if u["klass"] not in CERTIFIED:
        raise SystemExit("[FRAME] unit %s:%s is %s; only a CERTIFIED unit is read" % (rel(path), u["table"], u["klass"]))
    transpose2 = u["klass"] == "CERTIFIED-CONTESTANT"
    if u.get("votes_from_raw") and u["klass"] != "CERTIFIED-POSITIONAL":
        raise SystemExit("[FRAME] unit %s:%s: votes re-parsed from raw text are positional by construction and are never transposed; class %s "
                         "refused" % (rel(path), u["table"], u["klass"]))
    rows = fetch_rows(con, u["table"])
    out = []; notes = []
    if u["kind"] == "WIDE":
        for row in rows:
            if u.get("votes_from_raw"): v1, v2 = parse(row.get(u["r1"])), parse(row.get(u["r2"]))
            else: v1, v2 = row.get(u["v1"]), row.get(u["v2"])
            out.append(dict(key=rowkey(u, row), p1=v1, p2=T(v2) if transpose2 else v2, row=row))
        return out, notes
    resolve, _ = name_resolver_long(con, path, content_map)
    pair = u["pair"]
    mk, _ = long_key_fn(dict(columns=u["columns"], key=u["key"], match_key=u.get("match_key"), pk=u.get("pk")))
    by = defaultdict(dict); dup = set()
    for row in rows:
        a = str(row.get(u["key"]))
        if a not in pair: continue
        k = mk(row)
        if a in by[k]: dup.add(k)
        by[k][a] = row
    incomplete = 0
    for k, d in by.items():
        if k in dup: continue
        if pair[0] not in d or pair[1] not in d: incomplete += 1; continue
        xs = [to_order1_frame(long_label(d[a], u["vote"]), resolve(d[a]) if resolve else None) for a in pair]
        if None in xs:      # R-8 (VFC-RX-RULING): a CERTIFIED unit has 0 unresolvable labels on its paired rows; a None is drift. REFUSE.
            raise SystemExit("[FRAME] REFUSED (R-8): unit %s:%s is %s but the stored label of key %r (arm %s) is unresolvable at read time: drift "
                             "between the certificate and the reading (e.g. a name constant edited after the certificate); never dropped silently"
                             % (rel(path), u["table"], u["klass"], k, pair[xs.index(None)]))
        row = dict(d[pair[0]]); row.update({"_o2_" + c: v for c, v in d[pair[1]].items()})
        out.append(dict(key=k, p1=xs[0], p2=T(xs[1]) if transpose2 else xs[1], row=row))
    if dup: notes.append("%d match keys carry more than one row in an order and are excluded" % len(dup))
    if incomplete: notes.append("%d match keys lack one of the two orders and are excluded" % incomplete)
    return out, notes


# ─────────────────────────────────────────────────────────── the instrument ───────────────────────────────────────────────────────────

def enumerate_caches(root, say):
    files = scan_sqlite_files(root)
    stats0 = {p: stat_of(p) for p in files}
    listing = []
    for p in files:
        con = open_ro(p)
        try:
            sch = read_schema(con)
        except sqlite3.DatabaseError as e:
            say("  [SCHEMA] %s unreadable (%s): not enumerable" % (rel(p, root), e)); sch = {}
        finally:
            con.close()
        if sch: listing.append((p, sch))
    return files, stats0, listing


def print_enumeration(root, files, listing, say, shas):
    say("ENUMERATION: %d SQLite files scanned (experiment_results/** and the repository root); %d enumerated as dual-order candidates" % (len(files), len(listing)))
    for p, sch in listing:
        st = stat_of(p); wal = st.get("-wal", (0, 0))[0]
        say("  %-78s %12d bytes  sha256_16 %s  writer %s%s" % (rel(p, root), st["db"][0], shas[p], WRITER_OF.get(os.path.basename(p), "UNMAPPED"),
                                                              ("  WARNING: -wal %d bytes not read (immutable=1)" % wal) if wal else ""))
        for t, s in sch.items():
            if s["kind"] == "WIDE":
                say("      table %-20s WIDE (COLUMN-ORDINAL) votes %s/%s raw %s/%s combined %s/%s condition %s foreign %s"
                    % (t, s["v1"], s["v2"], s["r1"], s["r2"], s["win"], s["flip"], s["cond"], s["foreign"] or "-"))
            else:
                say("      table %-20s LONG (ARM-VALUE key %s) vote %s raw %s finish %s" % (t, s["key"], s["vote"], s["raw"], s["finish"]))


def dry_run(root=None):
    root = root or DATA_ROOT
    say = lambda s: print(s, flush=True)
    lf, crlf = script_shas()
    say("=== %s --dry-run (zero calls; writes nothing; certifies nothing) | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) ===" % (TEST, lf, crlf))
    files, stats0, listing = enumerate_caches(root, say)
    shas = {p: sha256_16(p) for p, _ in listing}
    print_enumeration(root, files, listing, say, shas)
    after = {p: stat_of(p) for p in files}
    moved = [rel(p, root) for p in files if after[p] != stats0[p]]
    say("NO-WRITE CHECK over %d scanned files: %s" % (len(files), "unchanged" if not moved else "CHANGED: %s" % moved))
    return 0 if not moved else 1


def require_steward(a):
    """--run refuses without the READY's independent listing (E1)."""
    if not a.steward_list:
        raise SystemExit("[E1] --run needs --steward-list: the READY's independent listing decides E1")


def score_criteria(n_enum, steward, enum_rel, units_ok, selftest_ok, moved):
    """-> ([(id, HELD|FAILED, line)] for E1-E4, the certificate verdict)."""
    out = []
    if steward is None:
        out.append(("E1", "FAILED", "E1 FAILED: no independent listing was supplied (the READY's data-steward list is required)"))
    else:
        only_me = sorted(set(enum_rel) - set(steward)); only_st = sorted(set(steward) - set(enum_rel))
        if not only_me and not only_st:
            out.append(("E1", "HELD", "E1 HELD: the enumeration (%d files) matches the independent listing file for file" % n_enum))
        else:
            out.append(("E1", "FAILED", "E1 FAILED: only in the enumeration %s; only in the independent listing %s" % (only_me, only_st)))
    out.append(("E2", "HELD", "E2 HELD: every enumerated cache carries exactly one of the SIX classes %s with its evidence counts" % (CLASSES,)) if units_ok else
               ("E2", "FAILED", "E2 FAILED: a cache has no class, two classes, a class outside the SIX, or a class without counts"))
    out.append(("E3", "HELD", "E3 HELD: the selftest returned every synthetic cache in its class (both branches executed)") if selftest_ok else
               ("E3", "FAILED", "E3 FAILED: the selftest misclassified a synthetic cache or did not complete"))
    out.append(("E4", "HELD", "E4 HELD: size and mtime of every enumerated file (and -wal / -shm) unchanged before / after") if not moved else
               ("E4", "FAILED", "E4 FAILED: changed files %s" % moved))
    verdict = "HELD" if all(r == "HELD" for _, r, _ in out) else "FAILED"
    return out, verdict


P5_NAMED = (("experiment_results/agent/bfcl_judged_pilot.db", True), ("experiment_results/x12_crossdomain/canary_baseline_pass1.db", False),
            ("experiment_results/x12_crossdomain/canary_baseline_pass2.db", False))


def require_reason_codes(caches):
    """R-7 (VFC-RX-RULING): every UNCERTIFIABLE unit (and every UNCERTIFIABLE secondary) carries a registered reason code, else the run REFUSES
    (an instrument defect). Returns None."""
    for c in caches:
        for u in c["units"]:
            for x, what in ((u, "unit"), (u.get("secondary") or {}, "secondary")):
                if x.get("klass") == "UNCERTIFIABLE" and x.get("uncert_reason") not in UNCERT_CODES:
                    raise SystemExit("[R-7] REFUSED: the UNCERTIFIABLE %s %s:%s carries no registered reason code (%r; registered %s): an instrument "
                                     "defect, never a default" % (what, c.get("path", "?"), u.get("table"), x.get("uncert_reason"), list(UNCERT_CODES)))


def uncert_breakdown(caches):
    """D7 (2c94cab): the UNCERTIFIABLE dual-order caches counted by the reason(s) their tables carry. -> (total, {code: n}, pin-timing n, lines)."""
    unc = [c for c in caches if c["klass"] == "UNCERTIFIABLE"]
    require_reason_codes(unc)       # R-7 (VFC-RX-RULING): no default reason; a missing code REFUSES
    cnt = Counter(); pin = 0
    for c in unc:
        codes = {u["uncert_reason"] for u in c["units"] if u["klass"] == "UNCERTIFIABLE"}
        for k in codes: cnt[k] += 1
        pin += any(u.get("pin_timing") for u in c["units"] if u["klass"] == "UNCERTIFIABLE")
    lines = ["P4 by reason (D7; a cache is counted under each reason its tables carry): " + "; ".join(
        "(%d) %s %d%s" % (i + 1, lab, cnt[k], (" [of which pin timing %d: UNCERTIFIABLE by pin timing, not by frame]" % pin) if k == "R2" else "")
        for i, (k, lab) in enumerate(UNCERT_REASONS))]
    if cnt["R6"]:       # R-5: an R6 unit is printed on its own line; the outcome states whether P4 is carried by R6
        lines.append("P4 reason (6) R6 %s: %d cache(s), UNCERTIFIABLE by instrument knowledge (a name-profile gap), not by frame (R-5); P4 IS carried "
                     "(in part or whole) by R6" % (UNCERT_REASONS[5][1], cnt["R6"]))
    carried = [lab for k, lab in UNCERT_REASONS if cnt[k]]
    lines.append("P4 is carried by: %s" % (carried or "no UNCERTIFIABLE cache"))
    return len(unc), dict(cnt), pin, lines


def score_predictions(classes, named):
    """classes: {rel path: cache class}; named: {rel path: (cache class, units)} for the P5 caches. -> [(id, HELD|FAILED, line)].
    P1-P4 are read over the DUAL-ORDER caches only (enumerated minus NOT-DUAL-ORDER; ruling (4), 04379d7); the raw enumeration count and the
    NOT-DUAL-ORDER count are printed beside. P5 is read on the REV arm (the fwd arm is AMBIGUOUS by construction)."""
    raw_n = len(classes); n_ndo = sum(1 for k in classes.values() if k == NDO)
    dual = {p: k for p, k in classes.items() if k != NDO}
    n = len(dual); c = Counter(dual.values())
    hf = lambda b: "HELD" if b else "FAILED"
    beside = " [over the dual-order caches: raw enumeration %d, NOT-DUAL-ORDER %d]" % (raw_n, n_ndo)
    out = [("P1", hf(25 <= n <= 60), "P1 %s: %d dual-order caches (registered band 25-60, point 40)%s" % (hf(25 <= n <= 60), n, beside))]
    share = c["CERTIFIED-POSITIONAL"] / n if n else 0.0
    out.append(("P2", hf(share >= 0.80), "P2 %s: %d of %d dual-order caches CERTIFIED-POSITIONAL = %.3f (registered >= 0.80)%s"
                % (hf(share >= 0.80), c["CERTIFIED-POSITIONAL"], n, share, beside)))
    out.append(("P3", hf(c["MIXED"] == 0), "P3 %s: %d MIXED of %d dual-order caches (registered 0)%s" % (hf(c["MIXED"] == 0), c["MIXED"], n, beside)))
    out.append(("P4", hf(c["UNCERTIFIABLE"] >= 1), "P4 %s: %d UNCERTIFIABLE among the %d dual-order caches (registered >= 1; a NOT-DUAL-ORDER cache "
                "never satisfies P4)%s" % (hf(c["UNCERTIFIABLE"] >= 1), c["UNCERTIFIABLE"], n, beside)))
    bad = []; fwd = None
    for path, want_long in P5_NAMED:
        if path not in named: bad.append("%s not enumerated" % path); continue
        k, units = named[path]
        if k != "CERTIFIED-POSITIONAL": bad.append("%s is %s" % (path, k)); continue
        if want_long:
            v = [u for u in units if u["table"] == "verdicts"]
            if not v or v[0]["kind"] != "LONG" or v[0].get("pair") != ["fwd", "rev"] or v[0]["klass"] != "CERTIFIED-POSITIONAL":
                bad.append("%s verdicts is not a LONG fwd/rev frame certified positional on the rev arm" % path)
            else:
                fwd = "fwd arm (beside, deciding nothing) agrees with its re-parse on %s of %s informative rows" % (
                    v[0]["counts"].get("order1_agree"), v[0]["counts"].get("order1_informative"))
    out.append(("P5", hf(not bad), "P5 %s: bfcl_judged_pilot.db LONG by arm, CERTIFIED-POSITIONAL on the REV arm, and both canary caches "
                "CERTIFIED-POSITIONAL%s [read on the rev arm: on the fwd arm the positional and contestant hypotheses coincide, so it is AMBIGUOUS "
                "by construction and does not decide the class (the registrar's recorded reading, 04379d7)]%s"
                % (hf(not bad), "" if not bad else ": " + "; ".join(bad), (" | " + fwd) if not bad and fwd else "")))
    return out


def run(steward_path, root=None, selftest_ok=None, out_txt=None, out_json=None, comb_ctx=None):
    root = root or DATA_ROOT
    out_txt = out_txt or os.path.join(root, "experiment_results", "vote_frame_cert.txt")
    out_json = out_json or os.path.join(root, "experiment_results", "vote_frame_cert.json")
    for p in (out_txt, out_json):
        if os.path.exists(p):
            raise SystemExit("[WRITE-ONCE] REFUSED: %s exists; the certificate of record is never rewritten" % rel(p, root))
    L = []
    def say(s):
        L.append(s); print(s, flush=True)
    lf, crlf = script_shas()
    say("=== %s (zero calls) | registration %s | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) ===" % (TEST, REGISTRATION, lf, crlf))
    say("parser of record for E-RAW: %s; combine rule for E-COMB: rejudge_grok.combine_orders and its untransposed twin" % PARSER_NAME)
    if selftest_ok is None:
        selftest_ok = selftest(quiet=True)
    say("selftest (E3), executed in-process before the census: %s" % ("PASS" if selftest_ok else "FAIL"))
    steward = None
    if steward_path:
        steward = [l.strip().replace("\\", "/") for l in open(steward_path, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    files, stats0, listing = enumerate_caches(root, say)
    shas = {p: sha256_16(p) for p, _ in listing}
    print_enumeration(root, files, listing, say, shas)
    say("")
    say("CERTIFICATE ROWS (a CENSUS: every row of every enumerated table):")
    caches = []; units_ok = True
    for p, sch in listing:
        con = open_ro(p)
        try:
            units = [certify_table(con, p, s, comb_ctx) for s in sch.values()]
            pools = run_meta_pools(con)
        finally:
            con.close()
        k = cache_class(units)
        if k not in CLASSES or not units or any(u["klass"] not in CLASSES or "counts" not in u for u in units): units_ok = False
        st = stat_of(p)
        single = [u["table"] for u in units if u["klass"] == NDO]
        caches.append(dict(path=rel(p, root), size=st["db"][0], mtime_ns=st["db"][1], sha256_16=shas[p], wal_bytes=st.get("-wal", (0, 0))[0],
                           writer=WRITER_OF.get(os.path.basename(p), "UNMAPPED"), pools=pools, klass=k, units=units, single_order_tables=single))
        say("  %s -> %s | pools %s%s" % (rel(p, root), k, pools or "(no run_meta pool)",
                                        (" | single-order tables LISTED (not classed on): %s" % single) if single and k != NDO else ""))
        for u in units:
            c = u["counts"]
            say("      %-20s %-5s %-21s %-22s rows %d | order-1 %s/%s | order-2 informative %s: positional %s, contestant %s | inv-on-decisive %s | "
                "decisive-on-nondecisive %s | unresolvable %s%s" % (u["table"], u["kind"], u["klass"], u["evidence"], c.get("rows", 0),
                c.get("order1_agree", "-"), c.get("order1_informative", "-"), c.get("order2_informative", "-"), c.get("agree_positional", "-"),
                c.get("agree_contestant", "-"), c.get("stored_invalid_on_decisive_parse", "-"), c.get("stored_decisive_on_nondecisive_parse", "-"),
                c.get("unresolvable_labels", "-"), (" | pair %s unpaired %s" % (u.get("pair"), u.get("unpaired"))) if u["kind"] == "LONG" else
                (" | condition %s %s" % (u.get("cond"), u.get("cond_values"))) if u.get("cond") else ""))
            say("        positional %s | contestant-labelled %s | order key %s%s%s" % (u.get("positional_cols"), u.get("contestant_cols"), u["order_key"],
                (" | " + u["names_desc"]) if u.get("names_desc") else "", (" | combined " + u["combined_label_space"]) if u.get("combined_label_space") else ""))
            if u.get("combiner_check"):
                cc = u["combiner_check"]
                say("        H3 CALL-SITE CHECK %s | %s" % ("PASS" if cc.get("callsite_ok") else ("FAIL" if cc["ok"] else "not reached"), cc.get("callsite")))
                say("        H3 COMBINER CHECK %s | writer %s | pinned blob %s | evidence %s | %s" % ("PASS" if cc["ok"] else "FAIL", cc["writer"],
                    cc["pin"], cc["evidence"], cc["result"]))
            if u.get("secondary"):
                sc = u["secondary"]["counts"]; sd = u["secondary"]
                if sd.get("uncert_reason") == "R6":      # R-6: never printed CERTIFIED; the resolved subset is descriptive, downgrade-only
                    say("        secondary %s: UNCERTIFIABLE (R6), secondary, %d resolved of %d informative (the resolved tally is DESCRIPTIVE: downgrade only, "
                        "never corroboration) (informative %d, positional %d, contestant %d, unresolvable %d, of which on rows with both votes decisive %d; "
                        "labels %s)" % (sd["evidence"], sd["resolved"], sd["informative"], sc["order2_informative"], sc["agree_positional"],
                        sc["agree_contestant"], sc["unresolvable_labels"], sd["informative"] - sd["resolved"], sd.get("unresolvable_values")))
                else:
                    say("        secondary %s: %s (informative %d, positional %d, contestant %d, unresolvable %d)" % (sd["evidence"],
                        sd["klass"], sc["order2_informative"], sc["agree_positional"], sc["agree_contestant"], sc["unresolvable_labels"]))
            if u["klass"] == "MIXED":
                say("        CONTRADICTING ROWS (first 20 each): order-1 %s | vs positional %s | vs contestant %s"
                    % (c.get("contradict_order1"), c.get("contradict_positional"), c.get("contradict_contestant")))
            for n in u.get("notes", []): say("        " + n)
    require_reason_codes(caches)      # R-7: before anything is written; over EVERY unit, whatever its cache's class
    after = {p: stat_of(p) for p in files}
    moved_enum = [rel(p, root) for p, _ in listing if after[p] != stats0[p]]
    moved_other = [rel(p, root) for p in files if after[p] != stats0[p] and rel(p, root) not in moved_enum]
    say("")
    say("NO-WRITE: %d enumerated files %s; %d other scanned files %s" % (len(listing), "unchanged" if not moved_enum else "CHANGED %s" % moved_enum,
        len(files) - len(listing), "unchanged" if not moved_other else "CHANGED %s" % moved_other))
    classes = {c["path"]: c["klass"] for c in caches}
    cc = Counter(classes.values())
    say("SUMMARY: %d caches enumerated (raw) | %s | dual-order caches %d (enumerated minus NOT-DUAL-ORDER %d)"
        % (len(caches), ", ".join("%s %d" % (k, cc[k]) for k in CLASSES), len(caches) - cc[NDO], cc[NDO]))
    crit, verdict = score_criteria(len(listing), steward, [c["path"] for c in caches], units_ok, selftest_ok, moved_enum)
    say("")
    for _, _, line in crit: say(line)
    say("CERTIFICATE: %s (HELD iff E1-E4 are all HELD)" % verdict)
    named = {c["path"]: (c["klass"], c["units"]) for c in caches}
    say("")
    for _, _, line in score_predictions(classes, named): say(line)
    for line in uncert_breakdown([c for c in caches if c["klass"] != NDO])[3]: say(line)
    doc = dict(test=TEST, registration=REGISTRATION, script_sha256_16_lf=lf, script_sha256_16_crlf=crlf, parser=PARSER_NAME,
               certificate=verdict, criteria={i: dict(result=r, line=l) for i, r, l in crit}, caches=caches,
               selftest="PASS" if selftest_ok else "FAIL", written=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(out_json, "x", encoding="utf-8") as f: json.dump(doc, f, indent=1, sort_keys=True, default=str)
    with open(out_txt, "x", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    print("[WRITTEN] %s and %s (write-once)" % (rel(out_txt, root), rel(out_json, root)), flush=True)
    return doc


# ─────────────────────────────────────────────────────────── selftest ───────────────────────────────────────────────────────────

def _raw(v):
    return '{"comparison": "x", "winner": "%s", "confidence": 0.8}' % v


def _mk(path, ddl, rows):
    con = sqlite3.connect(path)
    con.executescript(ddl)
    for t, rs in rows.items():
        for r in rs: con.execute("INSERT INTO %s VALUES (%s)" % (t, ",".join("?" * len(r))), r)
    con.commit(); con.close()


WIDE_DDL = ("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, qid INTEGER, vote1 TEXT, vote2_raw TEXT, "
            "winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT); CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT);")


def _positional_votes(n, seed):
    """Deterministic positional vote pairs covering agreements, both flip kinds, ties and an INVALID."""
    g = random.Random(seed); out = []
    for _ in range(n):
        out.append(g.choice([("Model A", "Model B"), ("Model B", "Model A"), ("Model A", "Model A"), ("Model B", "Model B"),
                             ("TIE", "Model A"), ("Model B", "TIE"), ("TIE", "TIE")]))
    out[0] = ("Model A", "Model A"); out[1] = ("Model A", "Model B"); out[2] = ("INVALID", "Model A")
    return out


def _wide_row(i, p1, p2_raw, s2, comb):
    w, f, inv = comb
    return (i, "ma", "mb", 100 + i // 2, p1, s2, w, int(f), int(inv), _raw(p1) if p1 != "INVALID" else "garbage", _raw(p2_raw))


def _wide_rows(votes, transpose_rows=None, all_transposed=False):
    """Positional truth votes -> stored rows. A transposed row stores T(p2) and its combined winner consistently with that storage."""
    rows = []
    for i, (p1, p2) in enumerate(votes):
        tr = all_transposed or (transpose_rows is not None and i in transpose_rows)
        s2 = T(p2) if tr else p2
        rows.append(_wide_row(i, p1, p2, s2, combine_contestant(p1, s2) if tr else rj.combine_orders(p1, s2)))
    return rows


RJ_BAD = '''
def combine_orders(vote1_raw, vote2_raw):
    invalid = vote1_raw == "INVALID" or vote2_raw == "INVALID"
    flip = (not invalid) and vote1_raw != vote2_raw
    return ("INVALID" if invalid else ("TIE" if flip else vote1_raw)), flip, invalid
'''
DDL_W = ("CREATE TABLE verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, "
         "invalid INTEGER, ts REAL, PRIMARY KEY (match_id, arm));")
def _writer(combine_expr, parse2="    v2, _ = rj.parse_judge(raw2)\n", stored2="v2", header="", pre=""):
    """A fixture writer: the clean D2 pattern unless a piece is replaced."""
    return ("import rejudge_grok as rj\nDDL = %r\n%s\ndef one(i, raw1, raw2):\n    v1, _ = rj.parse_judge(raw1)\n%s%s"
            "    gw, flip, invalid = %s\n    return (i, 'anchor', 'ma', 'mb', v1, %s, gw, int(flip), int(invalid), 0.0)\n"
            % (DDL_W, header, parse2, pre, combine_expr, stored2))
W_RJ = _writer("rj.combine_orders(v1, v2)")
W_LOCAL = ('''
T2 = None

def combine(a, b):
    tr = {"Model A": "Model B", "Model B": "Model A"}
    b2 = tr.get(b, b)
    bad = a == "INVALID" or b2 == "INVALID"
    fl = (not bad) and a != b2
    return ("INVALID" if bad else ("TIE" if fl else a)), fl, bad

def judge(v1, v2):
    return combine(v1, v2)
''')
W_LOCAL = _writer("combine(v1, v2)", header=W_LOCAL.replace("def judge(v1, v2):\n    return combine(v1, v2)\n", ""))
# D2 (2c94cab) call-site fixtures: the combiner verifies, the ARGUMENT does not
TRD_ = '{"Model A": "Model B", "Model B": "Model A"}'
W_CS_TRANSPOSE = _writer("rj.combine_orders(v1, v2c)", parse2="    v2c = %s.get(rj.parse_judge(raw2)[0], rj.parse_judge(raw2)[0])\n" % TRD_, stored2="v2c")
W_CS_OTHERNAME = _writer("rj.combine_orders(v1, v2)", pre="    v2s = v1\n", stored2="v2s")
W_CS_SUBSCRIPT = _writer("rj.combine_orders(v1, v2)", parse2="    v2 = rj.parse_judge(raw2)[0]\n")
W_CS_WRAP = _writer("rj.combine_orders(v1, str(v2))")
C_SRC = {   # the re-review's adversarial combiners (bc2ea7b, h3_adv.py), each the writer's local combiner
    "c3": "def combine(a, b):\n    b2 = %s.get(b, b)\n    b3 = 'Model A' if b2 == 'Model B' else ('Model B' if b2 == 'Model A' else b2)\n"
          "    bad = a == 'INVALID' or b3 == 'INVALID'\n    fl = (not bad) and a != b3\n    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n" % TRD_,
    "c4": "def combine(a, b):\n    b2 = %s.get(b, b)\n    bad = a == 'INVALID' or b == 'INVALID'\n    fl = (not bad) and a != b\n"
          "    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n" % TRD_,
    "c5": "def combine(a, b):\n    b2 = %s.get(b, b)\n    bad = a == 'INVALID' or b2 == 'INVALID'\n    fl = (not bad) and a == b2\n"
          "    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n" % TRD_,
    "c9": "def combine(a, b):\n    b2 = %s.get(b, b)\n    bad = a == 'INVALID' or b2 == 'INVALID'\n    fl = (not bad) and a != b2\n"
          "    return ('INVALID' if bad else ('TIE' if fl else b)), fl, bad\n" % TRD_,
    "c6": "SWAP = %s\n\ndef combine(a, b):\n    b2 = SWAP.get(b, b)\n    bad = a == 'INVALID' or b2 == 'INVALID'\n    fl = (not bad) and a != b2\n"
          "    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n" % TRD_,
}
W_C = {k: _writer("combine(v1, v2)", header="\n" + v) for k, v in C_SRC.items()}
W_LOCAL_IDENT = _writer("combine_orders(v1, v2)", header="\n" + REF_COMBINE_ORDERS.replace("(vote1_raw, vote2_raw):", "(x, y):\n    'a local copy'")
                        .replace("vote1_raw", "x").replace("vote2_raw", "y"))
W_LOCAL_BADCOPY = _writer("combine_orders(v1, v2)", header="\n" + RJ_BAD)
RJBAD_ROWS = True     # marker: the rjbad fixtures store the rows the bad pinned combine_orders produced
# D-C (776a2dd) writers: the combiner call is clean, the module is not
W_DC = {
    "dc_patch_combine": _writer("rj.combine_orders(v1, v2)", header="\ndef _nocombine(a, b):\n    return a, False, False\nrj.combine_orders = _nocombine\n"),
    "dc_patch_parse": _writer("rj.combine_orders(v1, v2)", header="\n_p = rj.parse_judge\nrj.parse_judge = lambda r: _p(r)\n"),
    "dc_rebind_alias": _writer("rj.combine_orders(v1, v2)", header="\nclass _R:\n    parse_judge = None\n    combine_orders = None\nrj = _R()\n"),
    "dc_setattr": _writer("rj.combine_orders(v1, v2)", header="\nsetattr(rj, 'combine_orders', None)\n"),
    "dc_exec": _writer("rj.combine_orders(v1, v2)", header="\nexec('x = 1')\n"),
    "dc_eval": _writer("rj.combine_orders(v1, v2)", header="\nY = eval('1')\n"),
    "dc_fromimport": ("from rejudge_grok import combine_orders\n" + _writer("combine_orders(v1, v2)", header="\ncombine_orders = None\n")),
}
# D-C' (VFC-DC-PRIME, ae88d3a) writers: the combiner call is clean, the module (or a local module it imports) is not; each fires ONE route,
# named by the substring its check requires. dcp_dep_clean imports a clean local module and must CERTIFY.
W_DCP_SPEC = {
    "dcp_ref_setattr": ("_sa = setattr\n", "setattr is referenced, not called"),
    "dcp_ref_globals": ("_g = globals\n", "globals is referenced"),
    "dcp_dunder_name": ("_b = __builtins__\n", "the dunder name __builtins__ is referenced"),
    "dcp_attr_named": ("import builtins\n_f = builtins.setattr\n", "an attribute named setattr is referenced"),
    "dcp_dunder_attr": ("_o = object.__setattr__\n", "the dunder attribute .__setattr__ is referenced"),
    "dcp_sys_modules": ("import sys\n_m = sys.modules\n", "sys.modules is referenced"),
    "dcp_alias_value": ("_r = rj\n", "the alias 'rj' is used as a value"),
    "dcp_store_call": ("_d = {}\n\ndef _g():\n    return _d\n_g()['k'] = 1\n", "a store through a call result"),
    "dcp_store_rj": ("rj.TABLE['k'] = 1\n", "a store through rejudge_grok"),
    "dcp_import_importlib": ("import importlib\n", "importlib is imported"),
    "dcp_from_sys_modules": ("from sys import modules as _m\n", "sys.modules is imported"),
    "dcp_star": ("from rejudge_grok import *\n", "a star import from rejudge_grok"),
    "dcp_def": ("def rj():\n    return None\n", "'rj' is rebound by a def / class"),
    "dcp_param": ("def _h(rj=None):\n    return 1\n", "'rj' is rebound as a parameter"),
    "dcp_except": ("try:\n    pass\nexcept Exception as rj:\n    pass\n", "'rj' is rebound by except-as"),
    "dcp_match": ("match 1:\n    case rj:\n        pass\n", "'rj' is rebound by a match capture"),
    "dcp_import_twice": ("from os import path as rj\n", "'rj' is imported as two different objects"),
    "dcp_dep_patch": ("import dcpmod_patch\n", "dcpmod_patch.py@"),
    "dcp_dep_vars": ("import dcpmod_vars\n", "vars is referenced"),
    "dcp_dep_deep": ("import dcpmod_mid\n", "dcpmod_patch.py@"),
    "dcp_dep_late": ("import dcpmod_late\n", "dcpmod_late.py cannot be pinned at or before"),
    "dcp_dep_relative": ("from . import dcpmod_clean\n", "a relative import cannot be resolved"),
    "dcp_dep_clean": ("import dcpmod_clean\n", None),
    # D1 (VFC-FIXES-2; review 9d3e261): the reviewer's vectors u1, u2, u3, u6, u7 (several routes each) ...
    "d1_u1_pkgutil": ("import pkgutil\n_m = pkgutil.resolve_name('rejudge_grok')\n_m.combine_orders = None\n", "pkgutil is imported (D1)"),
    "d1_u2_frame": ("import inspect\n_g = inspect.currentframe().f_globals\n_g['rj'] = None\n", "inspect is imported (D1)"),
    "d1_u3_gc": ("import gc\nfor _m in gc.get_objects():\n    if hasattr(_m, 'combine_orders'):\n        _m.combine_orders = None\n", "gc is imported (D1)"),
    "d1_u6_compile": ("import types\n_f = types.FunctionType(compile('import rejudge_grok as r\\nr.combine_orders = None', 'x', 'exec'), {})\n_f()\n",
                      "types is imported (D1)"),
    "d1_u7_setitem": ("import operator\nimport inspect\noperator.setitem(inspect.currentframe().f_globals, 'rj', None)\n",
                      "an attribute named setitem is referenced (D1)"),
    # ... and ONE route each, so that every D1 rule is necessary
    "d1_mod_only": ("import ctypes\n", "ctypes is imported (D1)"),
    "d1_from_mod": ("from inspect import signature\n", "inspect is imported (D1)"),
    "d1_from_attr": ("from operator import setitem\n", "setitem is imported by name (D1)"),
    "d1_attr_only": ("_x = None\n_y = _x.f_locals if _x else None\n", "an attribute named f_locals is referenced (D1)"),
    "d1_compile_only": ("_c = compile\n", "the builtin compile is referenced (D1)"),
    "d1_store_attr_only": ("class _K:\n    pass\n_k = _K()\n_k.combine_orders = None\n", "an attribute named combine_orders is stored on an object"),
    "d1_store_key_only": ("_d = {}\n_d['parse_judge'] = None\n", "a store under the key 'parse_judge' (D1)"),
    "d1_dep": ("import dcpmod_d1\n", "dcpmod_d1.py@"),
    "d1_re_compile_ok": ("import re\n_P = re.compile('x')\n", None),          # an ATTRIBUTE .compile is not the builtin: certifies
    # D2 (9d3e261): the transitive scan fails CLOSED (u4 untracked local module, u5 a package-path import) ...
    "d2_untracked": ("import dcpmod_untracked\n", "tools/analysis/dcpmod_untracked.py is a local module on disk with no git history"),
    "d2_untracked_pkg": ("import dcppkg_untracked\n", "tools/analysis/dcppkg_untracked/ is a local module on disk with no git history"),
    "d2_pkgpath_from": ("from tools.analysis import dcpmod_patch\n", "dcpmod_patch.py@"),
    "d2_pkgpath_import": ("import tools.analysis.dcpmod_patch\n", "dcpmod_patch.py@"),
    "d2_pkgpath_frommod": ("from tools.analysis.dcpmod_patch import _n\n", "dcpmod_patch.py@"),
    "d2_pkgpath_bad": ("from tools import analysis\n", "names no module under tools/analysis (D2)"),
    "d2_unknown": ("import zz_vfc_no_such_module_q7\n", "is neither a local module with a history, nor stdlib, nor an installed distribution (D2)"),
    "d2_stdlib_ok": ("import json\nimport os.path\n", None),
    # F4 / F5 (review a3da968): runpy / code / codeop each; the reviewer's two builtins vectors; a local module SHADOWING a stdlib name is scanned
    "d1_runpy": ("import runpy\n", "runpy is imported (D1)"),
    "d1_code": ("import code\n", "code is imported (D1)"),
    "d1_codeop": ("from codeop import compile_command\n", "codeop is imported (D1)"),
    "d1_getattr_builtins": ("import builtins\ngetattr(builtins, 'ex' + 'ec')('import rejudge_grok as r; r.combine_orders = None')\n", "builtins is imported (D1)"),
    "d1_from_builtins_exec": ("from builtins import exec as _e\n_e('x = 1')\n", "builtins is imported (D1)"),
    "d2_stdlib_shadow": ("import csv\n", "csv.py@"),
    # ... and D3: a committed local module that does not parse at the pin
    "d3_dep_syntax": ("import dcpmod_syntax\n", "dcpmod_syntax.py at"),
}
D2_INSTALLED_CANDIDATES = ("numpy", "pip", "setuptools", "scipy")     # the first installed one is the D2 "installed distribution" fixture
ECOMB_R6_FIXTURES = ("ecomb_r6", "ecomb_r6_mixed", "ecomb_r6_tie", "ecomb_r6_amb")                    # R-2 (c) / R-3: E-COMB primaries with unresolvable combined labels


def d2_installed_name():
    """The first of D2_INSTALLED_CANDIDATES that is an installed distribution's top-level name and not stdlib; None if none is (the selftest
    then FAILS its installed-distribution check rather than skip it)."""
    return next((m for m in D2_INSTALLED_CANDIDATES if m in installed_top_levels() and m not in getattr(sys, "stdlib_module_names", ())), None)
W_DCP = {k: _writer("rj.combine_orders(v1, v2)", header="\n" + h) for k, (h, _) in W_DCP_SPEC.items()}
DCP_MODS = {       # local modules of the temp repo, committed at A (dcpmod_late only at C)
    "dcpmod_patch.py": "import rejudge_grok as rj\n\ndef _n(a, b):\n    return a, False, False\nrj.combine_orders = _n\n",
    "dcpmod_vars.py": "import rejudge_grok as rj\n_v = vars\n",
    "dcpmod_mid.py": "import os\nimport dcpmod_patch\n",
    "dcpmod_clean.py": "import os\nX = 1\n",
    "dcpmod_d1.py": "import gc\nX = 1\n",                     # D1 route in a local dependency only
    "dcpmod_syntax.py": "def broken(:\n    pass\n",          # D3: does not parse at the pin
    "csv.py": "import rejudge_grok as rj\nrj.combine_orders = None\n",      # F4: a committed local module shadowing a stdlib name (scanned first)
}
DCP_UNTRACKED = {"dcpmod_untracked.py": "import rejudge_grok as rj\nrj.combine_orders = None\n",       # D2 u4: on disk, never committed
                 "dcppkg_untracked/__init__.py": "X = 1\n"}
RJ_SELF = REF_COMBINE_ORDERS + "\ncombine_orders = combine_orders\n"      # commit C: rejudge_grok rebinds its own combine_orders
W_O1_TRANSPOSE = _writer("rj.combine_orders(v1c, v2)", stored2="v2").replace("    v1, _ = rj.parse_judge(raw1)\n",
    "    v1c = %s.get(rj.parse_judge(raw1)[0], rj.parse_judge(raw1)[0])\n" % TRD_).replace("'ma', 'mb', v1, ", "'ma', 'mb', v1c, ")
W_O1_OTHERNAME = _writer("rj.combine_orders(v1, v2)", pre="    v1s = v2\n").replace("'ma', 'mb', v1, ", "'ma', 'mb', v1s, ")
W_O1_SUBSCRIPT = _writer("rj.combine_orders(v1, v2)").replace("    v1, _ = rj.parse_judge(raw1)\n", "    v1 = rj.parse_judge(raw1)[0]\n")
W_O1_NOCOL = _writer("rj.combine_orders(v1, v2)").replace("vote1 TEXT", "vote_one TEXT")     # the writer's DDL lacks the order-1 column
W_CS_PARAM = _writer("rj.combine_orders(v1, v2)").replace("def one(i, raw1, raw2):", "def one(i, raw1, raw2, v2=None):")
W_CS_REBIND = _writer("rj.combine_orders(v1, v2)", pre="    v2 = {'Model A': 'Model B'}.get(v2, v2)\n")
W_CS_NOROW = _writer("rj.combine_orders(v1, v2)").replace("    return (i, 'anchor',", "    return [i, 'anchor',").replace("int(invalid), 0.0)\n", "int(invalid), 0.0]\n")
W_CS_NODDL = _writer("rj.combine_orders(v1, v2)").replace("DDL = %r\n" % DDL_W, "")
W_CS_HELPER = _writer("rj.combine_orders(v1, v2)", parse2="    v2, _ = my_parse(raw2)\n",
                      header="\ndef my_parse(raw):\n    return rj.parse_judge(raw)\n")
W_CS_SECOND = _writer("rj.combine_orders(v1, v2)", parse2="    _, v2 = rj.parse_judge(raw2)\n")
W_CS_WHOLE = _writer("rj.combine_orders(v1, v2)", parse2="    v2 = rj.parse_judge(raw2)\n")
W_ZERO = ('''
def combine_votes(a, b):
    bad = a == "INVALID" or b == "INVALID"
    fl = (not bad) and a != b
    return ("INVALID" if bad else ("TIE" if fl else a)), fl, bad

def judge(v1, v2):
    return combine_votes(v1, v2)
''')
W_TWO = ('''
def combine_twice(a, b):
    b1 = {"Model A": "Model B", "Model B": "Model A"}.get(b, b)
    b2 = {"Model A": "Model B", "Model B": "Model A"}.get(b1, b1)
    bad = a == "INVALID" or b2 == "INVALID"
    fl = (not bad) and a != b2
    return ("INVALID" if bad else ("TIE" if fl else a)), fl, bad

def judge(v1, v2):
    return combine_twice(v1, v2)
''')
TRD = '{"Model A": "Model B", "Model B": "Model A"}'
# re-review (bc2ea7b) mutant fixtures: each writer below must FAIL the combiner check under EVERY reading of ruling H3 (b)
W_ORDER1 = ("def combine(a, b):\n    a2 = %s.get(a, a)\n    bad = a2 == 'INVALID' or b == 'INVALID'\n    fl = (not bad) and a2 != b\n"
            "    return ('INVALID' if bad else ('TIE' if fl else a2)), fl, bad\n\ndef judge(v1, v2):\n    return combine(v1, v2)\n" % TRD)
W_IDENT = ("def combine(a, b):\n    b2 = {'Model A': 'Model A', 'Model B': 'Model B'}.get(b, b)\n    bad = a == 'INVALID' or b2 == 'INVALID'\n"
           "    fl = (not bad) and a != b2\n    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n\ndef judge(v1, v2):\n    return combine(v1, v2)\n")
W_ONEPARAM = ("def combine_pair(pair):\n    a, b = pair\n    b2 = %s.get(b, b)\n    bad = a == 'INVALID' or b2 == 'INVALID'\n"
              "    fl = (not bad) and a != b2\n    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n\ndef judge(v1, v2):\n"
              "    return combine_pair((v1, v2))\n" % TRD)
W_TWOCALLS = ("import rejudge_grok as rj\n\ndef combine_votes(a, b):\n    bad = a == 'INVALID' or b == 'INVALID'\n    fl = (not bad) and a != b\n"
              "    return ('INVALID' if bad else ('TIE' if fl else a)), fl, bad\n\ndef judge(v1, v2):\n    x = rj.combine_orders(v1, v2)\n"
              "    return combine_votes(v1, v2)\n")
H3_T = {"A": "2026-01-01T12:00:00+00:00", "B": "2026-02-01T12:00:00+00:00", "C": "2026-04-01T12:00:00+00:00"}
H3_TS = {"after": 1772323200.0, "between": 1768478400.0, "before": 1748736000.0,     # 2026-03-01, 2026-01-15, 2025-06-01 (UTC)
         "late": 1777593600.0}                                                     # 2026-05-01: after commit C (D-C' (f) fixtures only)


def build_comb_repo(root):
    """A throw-away git repo under the temp dir: commit A (2026-01-01) carries a rejudge_grok.combine_orders with NO transposition and the
    writers; commit B (2026-02-01) replaces it by the real one. -> the H3 context for certify_table."""
    import subprocess
    repo = os.path.join(root, "repo"); d = os.path.join(repo, *WRITER_DIR.split("/")); os.makedirs(d)
    env = dict(os.environ)
    def g(*a, when=None):
        e = dict(env)
        if when: e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "-C", repo, "-c", "user.name=selftest", "-c", "user.email=selftest@invalid", "-c", "core.autocrlf=false"] + list(a),
                       check=True, capture_output=True, env=e)
    g("init", "-q")
    for name, src in (("rejudge_grok.py", RJ_BAD), ("w_rj.py", W_RJ), ("w_local.py", W_LOCAL), ("w_zero.py", W_ZERO), ("w_two.py", W_TWO),
                      ("w_order1.py", W_ORDER1), ("w_ident.py", W_IDENT), ("w_oneparam.py", W_ONEPARAM), ("w_twocalls.py", W_TWOCALLS),
                      ("w_cs_transpose.py", W_CS_TRANSPOSE), ("w_cs_othername.py", W_CS_OTHERNAME), ("w_cs_subscript.py", W_CS_SUBSCRIPT),
                      ("w_cs_wrap.py", W_CS_WRAP), ("w_cs_rebind.py", W_CS_REBIND), ("w_cs_norow.py", W_CS_NOROW), ("w_cs_noddl.py", W_CS_NODDL),
                      ("w_cs_helper.py", W_CS_HELPER), ("w_cs_second.py", W_CS_SECOND), ("w_cs_whole.py", W_CS_WHOLE),
                      ("w_c3.py", W_C["c3"]), ("w_c4.py", W_C["c4"]), ("w_c5.py", W_C["c5"]), ("w_c9.py", W_C["c9"]), ("w_c6.py", W_C["c6"]),
                      ("w_local_ident.py", W_LOCAL_IDENT), ("w_local_badcopy.py", W_LOCAL_BADCOPY), ("w_cs_param.py", W_CS_PARAM), ("w_o1_transpose.py", W_O1_TRANSPOSE),
                      ("w_o1_othername.py", W_O1_OTHERNAME), ("w_o1_subscript.py", W_O1_SUBSCRIPT), ("w_o1_nocol.py", W_O1_NOCOL)) + tuple(("w_%s.py" % k, v) for k, v in W_DC.items()) \
            + tuple(("w_%s.py" % k, v) for k, v in W_DCP.items()) + tuple(DCP_MODS.items()):
        with open(os.path.join(d, name), "w", newline="\n") as f: f.write(src)
    inst = d2_installed_name()
    if inst:          # D2: an installed distribution's top-level name is skipped (stated limit), not a finding
        with open(os.path.join(d, "w_d2_installed.py"), "w", newline="\n") as f: f.write(_writer("rj.combine_orders(v1, v2)", header="\nimport %s\n" % inst))
    g("add", "-A"); g("commit", "-q", "-m", "A", when=H3_T["A"])
    with open(os.path.join(d, "rejudge_grok.py"), "w", newline="\n") as f: f.write(REF_COMBINE_ORDERS)
    with open(os.path.join(d, "w_late.py"), "w", newline="\n") as f: f.write(W_RJ)      # a writer whose ONLY commit is B
    g("add", "-A"); g("commit", "-q", "-m", "B", when=H3_T["B"])
    with open(os.path.join(d, "rejudge_grok.py"), "w", newline="\n") as f: f.write(RJ_SELF)
    with open(os.path.join(d, "dcpmod_late.py"), "w", newline="\n") as f: f.write("X = 1\n")
    g("add", "-A"); g("commit", "-q", "-m", "C", when=H3_T["C"])
    for name, src in DCP_UNTRACKED.items():          # D2 (u4): on disk after the last commit, never added
        os.makedirs(os.path.dirname(os.path.join(d, name)), exist_ok=True)
        with open(os.path.join(d, name), "w", newline="\n") as f: f.write(src)
    w_rj_sha = hashlib.sha256(W_RJ.encode("utf-8")).hexdigest()[:16]
    writers = {"f8_comb_transposed.db": "w_rj.py", "h3_rj_after.db": "w_rj.py", "h3_rj_between.db": "w_rj.py", "h3_rj_before.db": "w_rj.py",
               "h3_local.db": "w_local.py", "h3_zero.db": "w_zero.py", "h3_two.db": "w_two.py", "h3_runmeta.db": "w_rj.py", "h3_runmeta_bad.db": "w_rj.py",
               "h3_order1.db": "w_order1.py", "h3_ident.db": "w_ident.py", "h3_oneparam.db": "w_oneparam.py", "h3_twocalls.db": "w_twocalls.py",
               "h3_straddle.db": "w_late.py", "h3_contestant_zero.db": "w_zero.py", "cs_transpose.db": "w_cs_transpose.py",
               "cs_othername.db": "w_cs_othername.py", "cs_subscript.db": "w_cs_subscript.py", "cs_wrap.db": "w_cs_wrap.py", "cs_rebind.db": "w_cs_rebind.py",
               "cs_norow.db": "w_cs_norow.py", "cs_noddl.db": "w_cs_noddl.py", "cs_helper.db": "w_cs_helper.py", "cs_second.db": "w_cs_second.py",
               "cs_whole.db": "w_cs_whole.py", "c3.db": "w_c3.py", "c4.db": "w_c4.py", "c5.db": "w_c5.py", "c9.db": "w_c9.py", "c6.db": "w_c6.py",
               "h3_local_ident.db": "w_local_ident.py", "h3_local_badcopy.db": "w_local_badcopy.py", "rjbad_direct.db": "w_rj.py",
               "rjbad_localcopy.db": "w_local_badcopy.py", "cs_param.db": "w_cs_param.py", "o1_transpose.db": "w_o1_transpose.py",
               "o1_othername.db": "w_o1_othername.py", "o1_subscript.db": "w_o1_subscript.py", "o1_nocol.db": "w_o1_nocol.py"}
    writers.update({"%s.db" % k: "w_%s.py" % k for k in W_DC})
    writers.update({"%s.db" % k: "w_%s.py" % k for k in W_DCP}); writers["dcp_rj_self.db"] = "w_rj.py"
    writers.update({"%s.db" % k: "w_rj.py" for k in ECOMB_R6_FIXTURES})     # R-2 (c): the clean writer; R6 decides before the combiner check
    if inst: writers["d2_installed.db"] = "w_d2_installed.py"
    writers["ecomb_r6_tampered.db"] = "w_dc_patch_combine.py"      # F6: R6 decides; H3 run descriptively FAILS
    return dict(repo=repo, writers=writers), w_rj_sha


def build_fixtures(root):
    """Synthetic caches with KNOWN frames under root; -> ({rel path: expected cache class}, truth votes)."""
    er = os.path.join(root, "experiment_results"); os.makedirs(os.path.join(er, "sub"), exist_ok=True)
    V = _positional_votes(60, 7)
    exp = {}
    # F1 wide positional (E-RAW), with a run_meta pool
    _mk(os.path.join(er, "f1_wide_positional.db"), WIDE_DDL + "INSERT INTO run_meta VALUES ('pool_id','p2dca21ab5f4ef3ae');", {"verdicts": _wide_rows(V)})
    exp["experiment_results/f1_wide_positional.db"] = "CERTIFIED-POSITIONAL"
    # F2 wide DELIBERATELY TRANSPOSED (contestant-labelled order-2 column, combined winner consistent with it): never certified positional
    _mk(os.path.join(er, "f2_wide_transposed.db"), WIDE_DDL, {"verdicts": _wide_rows(V, all_transposed=True)})
    exp["experiment_results/f2_wide_transposed.db"] = "CERTIFIED-CONTESTANT"
    # F2b ONE ROW transposed in an otherwise positional cache: REFUSED (MIXED, row listed)
    _mk(os.path.join(er, "f2b_one_row_sign_flip.db"), WIDE_DDL, {"verdicts": _wide_rows(V, transpose_rows={1})})
    exp["experiment_results/f2b_one_row_sign_flip.db"] = "MIXED"
    # F3 long by arm positional (bfcl-like), with a probe table and the unusable-finish rule on one row
    ddl3 = ("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, stratum TEXT, task_id TEXT, agent_a TEXT, agent_b TEXT, nj TEXT);"
            "CREATE TABLE verdicts (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, finish TEXT, PRIMARY KEY (mid, arm));"
            "CREATE TABLE probe (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, finish TEXT, PRIMARY KEY (mid, arm));")
    rows3 = {"schedule": [], "verdicts": [], "probe": []}
    for i, (p1, p2) in enumerate(V):
        rows3["schedule"].append((i, "headline", "t%d" % (i % 9), "a", "b", ""))
        rows3["verdicts"].append((i, "fwd", p1, 0.8, int(p1 == "INVALID"), _raw(p1) if p1 != "INVALID" else "x", "stop"))
        fin = "length" if i == 5 else "stop"
        rows3["verdicts"].append((i, "rev", "INVALID" if fin == "length" else p2, 0.8, 0, _raw(p2), fin))
        if i < 10:
            rows3["probe"].append((i, "fwd", p1, 0.8, 0, _raw(p1) if p1 != "INVALID" else "x", "stop"))
            rows3["probe"].append((i, "rev", p2, 0.8, 0, _raw(p2), "stop"))
    _mk(os.path.join(er, "sub", "f3_long_arm.db"), ddl3, rows3)
    exp["experiment_results/sub/f3_long_arm.db"] = "CERTIFIED-POSITIONAL"
    # F4 mixed: half the rows transposed
    _mk(os.path.join(er, "f4_mixed.db"), WIDE_DDL, {"verdicts": _wide_rows(V, transpose_rows=set(range(0, 60, 2)))})
    exp["experiment_results/f4_mixed.db"] = "MIXED"
    # F5 uncertifiable: two votes, no raw, no combined column (aggregate_ties replicate without its raw columns)
    _mk(os.path.join(er, "f5_uncertifiable.db"), "CREATE TABLE replicate (qid INTEGER, cond TEXT, vote1 TEXT, vote2 TEXT, PRIMARY KEY (qid, cond));",
        {"replicate": [(i, "c", p1, p2) for i, (p1, p2) in enumerate(V)]})
    exp["experiment_results/f5_uncertifiable.db"] = "UNCERTIFIABLE"
    # F6 degenerate: no order-2 row is decisive
    _mk(os.path.join(er, "f6_degenerate.db"), WIDE_DDL, {"verdicts": _wide_rows([(p1, "TIE") for p1, _ in V])})
    exp["experiment_results/f6_degenerate.db"] = "AMBIGUOUS"
    # F7 evidence conflict: votes positional by raw, combined winner written as if the votes were contestant-labelled
    _mk(os.path.join(er, "f7_conflict.db"), WIDE_DDL, {"verdicts": [_wide_row(i, p1, p2, p2, combine_contestant(p1, p2)) for i, (p1, p2) in enumerate(V)]})
    exp["experiment_results/f7_conflict.db"] = "MIXED"
    # F8 E-COMB only (rubric_ladder-like: no raw), transposed storage, arm as a condition
    ddl8 = ("CREATE TABLE verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, "
            "invalid INTEGER, ts REAL, PRIMARY KEY (match_id, arm));")
    _mk(os.path.join(er, "f8_comb_transposed.db"), ddl8, {"verdicts": [
        (i, "anchor", "ma", "mb", p1, T(p2)) + (lambda w, f, v: (w, int(f), int(v)))(*combine_contestant(p1, T(p2))) + (H3_TS["after"] + i,)
        for i, (p1, p2) in enumerate(V)]})
    # H3 fixtures: E-COMB-only POSITIONAL tables (stored votes, no raw) written by the temp repo's writers at a known time
    pos8 = lambda ts0: [(i, "anchor", "ma", "mb", p1, p2) + (lambda w, f, v: (w, int(f), int(v)))(*rj.combine_orders(p1, p2)) + (ts0 + i,)
                        for i, (p1, p2) in enumerate(V)]
    for name, ts0, want in (("h3_rj_after", "after", "CERTIFIED-POSITIONAL"), ("h3_local", "after", "UNCERTIFIABLE"),
                            ("h3_zero", "after", "UNCERTIFIABLE"), ("h3_two", "after", "UNCERTIFIABLE"),
                            ("h3_rj_between", "between", "UNCERTIFIABLE"), ("h3_rj_before", "before", "UNCERTIFIABLE"),
                            ("h3_nowriter", "after", "UNCERTIFIABLE"), ("c3", "after", "UNCERTIFIABLE"), ("c4", "after", "UNCERTIFIABLE"),
                            ("c5", "after", "UNCERTIFIABLE"), ("c9", "after", "UNCERTIFIABLE"), ("c6", "after", "UNCERTIFIABLE"),
                            ("h3_local_ident", "after", "CERTIFIED-POSITIONAL"), ("h3_local_badcopy", "between", "UNCERTIFIABLE"),
                            ("cs_param", "after", "UNCERTIFIABLE"), ("o1_othername", "after", "UNCERTIFIABLE"),
                            ("o1_subscript", "after", "UNCERTIFIABLE"), ("o1_nocol", "after", "UNCERTIFIABLE")) + tuple((k, "after", "UNCERTIFIABLE") for k in W_DC) \
            + tuple((k, "after", "UNCERTIFIABLE" if W_DCP_SPEC[k][1] else "CERTIFIED-POSITIONAL") for k in W_DCP) + (("dcp_rj_self", "late", "UNCERTIFIABLE"),):
        _mk(os.path.join(er, name + ".db"), ddl8, {"verdicts": pos8(H3_TS[ts0])})
        exp["experiment_results/%s.db" % name] = want
    ddl8m = ddl8 + "CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT);"
    _mk(os.path.join(er, "h3_runmeta.db"), ddl8m, {"verdicts": pos8(H3_TS["after"]),
                                                   "run_meta": [("script_sha256_16_lf", hashlib.sha256(W_RJ.encode("utf-8")).hexdigest()[:16])]})
    exp["experiment_results/h3_runmeta.db"] = "CERTIFIED-POSITIONAL"      # the writer pinned by its run_meta sha
    _mk(os.path.join(er, "h3_runmeta_bad.db"), ddl8m, {"verdicts": pos8(H3_TS["after"]), "run_meta": [("script_sha256_16_lf", "0123456789abcdef")]})
    exp["experiment_results/h3_runmeta_bad.db"] = "UNCERTIFIABLE"
    # D-A (776a2dd): rows AS the bad pinned rejudge_grok body wrote them (positional votes, UNtransposed combine): E-COMB would read CONTESTANT
    bad8 = [(i, "anchor", "ma", "mb", p1, p2) + (lambda w, f, v: (w, int(f), int(v)))(*combine_contestant(p1, p2)) + (H3_TS["between"] + i,)
            for i, (p1, p2) in enumerate(V)]
    for name in ("rjbad_direct", "rjbad_localcopy"):
        _mk(os.path.join(er, name + ".db"), ddl8, {"verdicts": bad8})
        exp["experiment_results/%s.db" % name] = "UNCERTIFIABLE"
    # D-B (ae20138), the re-review's x1: order 1 TRANSPOSED before storing and combining; rows as that writer stores them (T(p1) in vote1,
    # combine_orders(T(p1), p2)): the combined column is consistent, so E-COMB alone would certify it POSITIONAL
    x1 = [(i, "anchor", "ma", "mb", T(p1), p2) + (lambda w, f, v: (w, int(f), int(v)))(*rj.combine_orders(T(p1), p2)) + (H3_TS["after"] + i,)
          for i, (p1, p2) in enumerate(V)]
    _mk(os.path.join(er, "o1_transpose.db"), ddl8, {"verdicts": x1})
    exp["experiment_results/o1_transpose.db"] = "UNCERTIFIABLE"
    # re-review mutant fixtures (bc2ea7b): all must be UNCERTIFIABLE
    for name in ("h3_order1", "h3_ident", "h3_oneparam", "h3_twocalls"):
        _mk(os.path.join(er, name + ".db"), ddl8, {"verdicts": pos8(H3_TS["after"])})
        exp["experiment_results/%s.db" % name] = "UNCERTIFIABLE"
    # first write BETWEEN A and B, last write AFTER B, the writer's only commit is B: pinned at the FIRST write -> unpinnable
    straddle = pos8(H3_TS["between"]); straddle[-1] = straddle[-1][:-1] + (H3_TS["after"],)
    _mk(os.path.join(er, "h3_straddle.db"), ddl8, {"verdicts": straddle})
    exp["experiment_results/h3_straddle.db"] = "UNCERTIFIABLE"
    # an E-COMB CONTESTANT table whose writer's combiner fails: the check applies to CONTESTANT certificates too
    _mk(os.path.join(er, "h3_contestant_zero.db"), ddl8, {"verdicts": [
        (i, "anchor", "ma", "mb", p1, T(p2)) + (lambda w, f, v: (w, int(f), int(v)))(*combine_contestant(p1, T(p2))) + (H3_TS["after"] + i,)
        for i, (p1, p2) in enumerate(V)]})
    exp["experiment_results/h3_contestant_zero.db"] = "UNCERTIFIABLE"
    # D2 call-site fixtures: the combiner verifies, the argument does not -> UNCERTIFIABLE (R3)
    for name in ("cs_transpose", "cs_othername", "cs_subscript", "cs_wrap", "cs_rebind", "cs_norow", "cs_noddl", "cs_helper", "cs_second", "cs_whole"):
        _mk(os.path.join(er, name + ".db"), ddl8, {"verdicts": pos8(H3_TS["after"])})
        exp["experiment_results/%s.db" % name] = "UNCERTIFIABLE"
    exp["experiment_results/f8_comb_transposed.db"] = "CERTIFIED-CONTESTANT"
    # F9 name-labelled long frame, CONTESTANT-labelled (arena13 as written): ensemble = NEW first, reversed = opponent first; + unpaired selfref
    new = source_constant("arena13.py", "NEW")
    ddl9 = ("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, qid INTEGER, opponent TEXT, anchor TEXT, frontier INTEGER);"
            "CREATE TABLE verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm));")
    sched9 = [(i, 500 + i // 3, "opp%d" % (i % 4), "Law", int(i % 2 == 0)) for i in range(len(V))]
    rows9 = {"schedule": sched9, "verdicts": []}
    rows9b = {"schedule": sched9, "verdicts": []}
    for i, (p1, p2) in enumerate(V):
        opp = "opp%d" % (i % 4); r1 = _raw(p1) if p1 != "INVALID" else "x"
        m1 = {"Model A": new, "Model B": opp}; m2 = {"Model A": opp, "Model B": new}
        rows9["verdicts"] += [(i, "ensemble", m1.get(p1, "TIE"), int(p1 == "INVALID"), r1, 0.0), (i, "reversed", m2.get(p2, "TIE"), 0, _raw(p2), 0.0),
                              (i, "selfref", m1.get(p1, "TIE"), 0, r1, 0.0)]
        # F9b the SIGN BUG in name form: 'reversed' mapped through the ensemble map
        rows9b["verdicts"] += [(i, "ensemble", m1.get(p1, "TIE"), int(p1 == "INVALID"), r1, 0.0), (i, "reversed", m1.get(p2, "TIE"), 0, _raw(p2), 0.0)]
    for d, rows in (("x12", rows9), ("x12b", rows9b)):
        os.makedirs(os.path.join(er, d), exist_ok=True); _mk(os.path.join(er, d, "arena13.db"), ddl9, rows)
    exp["experiment_results/x12/arena13.db"] = "CERTIFIED-CONTESTANT"
    exp["experiment_results/x12b/arena13.db"] = "CERTIFIED-POSITIONAL"
    # A7 (reviewer) arena13-like names with the ARM LABELS SWAPPED: the true order 1 under 'reversed', the true order 2 under 'ensemble' -> MIXED
    rows9c = {"schedule": sched9, "verdicts": []}
    for i, (p1, p2) in enumerate(V):
        opp = "opp%d" % (i % 4); m1 = {"Model A": new, "Model B": opp}; m2 = {"Model A": opp, "Model B": new}
        rows9c["verdicts"] += [(i, "reversed", m1.get(p1, "TIE"), int(p1 == "INVALID"), _raw(p1) if p1 != "INVALID" else "x", 0.0),
                               (i, "ensemble", m2.get(p2, "TIE"), 0, _raw(p2), 0.0)]
    os.makedirs(os.path.join(er, "x12c"), exist_ok=True); _mk(os.path.join(er, "x12c", "arena13.db"), ddl9, rows9c)
    exp["experiment_results/x12c/arena13.db"] = "MIXED"
    # VFC-NAME-PROFILE-BY-CONTENT (abf4db5 D1 / D6): a BYTE-IDENTICAL copy of the CONTESTANT fixture under an unmapped basename, and another under
    # a basename that maps to a DIFFERENT profile (placebo.db, GEM first): both get the original's class by content. A name-labelled table under an
    # unmapped basename whose content matches no original: the RX branch (D6), executed.
    os.makedirs(os.path.join(er, "_backup"), exist_ok=True)
    shutil.copyfile(os.path.join(er, "x12", "arena13.db"), os.path.join(er, "_backup", "arena13_copy_2026-09-23.db"))
    shutil.copyfile(os.path.join(er, "x12", "arena13.db"), os.path.join(er, "_backup", "placebo.db"))
    exp["experiment_results/_backup/arena13_copy_2026-09-23.db"] = "CERTIFIED-CONTESTANT"
    exp["experiment_results/_backup/placebo.db"] = "CERTIFIED-CONTESTANT"
    rows9u = {"schedule": sched9, "verdicts": [r[:5] + (1.0,) for r in rows9["verdicts"] if r[1] != "selfref"]}
    os.makedirs(os.path.join(er, "x12u"), exist_ok=True); _mk(os.path.join(er, "x12u", "names_unmapped.db"), ddl9, rows9u)
    exp["experiment_results/x12u/names_unmapped.db"] = "UNCERTIFIABLE"
    # F10 arm-keyed single order (ref_gated_rubric-like): NOT DUAL-ORDER
    _mk(os.path.join(er, "f10_single_order.db"), "CREATE TABLE verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm));",
        {"verdicts": [(i, a, "Model A", 0, _raw("Model A"), 0.0) for i in range(5) for a in ("base", "card")]})
    exp["experiment_results/f10_single_order.db"] = NDO
    # F14 ROW-LEVEL: order values fwd AND rev both occur in the table, but no match has both -> NOT-DUAL-ORDER (not a value-level test)
    _mk(os.path.join(er, "f14_values_not_rows.db"), "CREATE TABLE verdicts (mid INTEGER, arm TEXT, vote TEXT, invalid INTEGER, raw TEXT, PRIMARY KEY (mid, arm));",
        {"verdicts": [(i, "fwd" if i % 2 else "rev", "Model A", 0, _raw("Model A")) for i in range(20)]})
    exp["experiment_results/f14_values_not_rows.db"] = NDO
    # F15 one dual-order table + one single-order table: classed on the dual-order table, the single-order one LISTED
    _mk(os.path.join(er, "f15_dual_plus_single.db"), WIDE_DDL + "CREATE TABLE side_arm (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, PRIMARY KEY (mid, arm));",
        {"verdicts": _wide_rows(V), "side_arm": [(i, "base", "Model A", 0, _raw("Model A")) for i in range(5)]})
    exp["experiment_results/f15_dual_plus_single.db"] = "CERTIFIED-POSITIONAL"
    # F16 a WIDE table in which no row carries both orders (every order-2 column empty): NOT-DUAL-ORDER
    _mk(os.path.join(er, "f16_wide_single.db"), WIDE_DDL, {"verdicts": [(i, "ma", "mb", i, p1, None, p1, 0, 0, _raw(p1), None) for i, (p1, _) in enumerate(V)]})
    exp["experiment_results/f16_wide_single.db"] = NDO
    # F17 ONE order-1 row mis-stored in an otherwise positional cache: both hypotheses refuted on that row -> MIXED (review 14edeb4, B1)
    rows17 = _wide_rows(V); r = list(rows17[1]); r[4] = "Model B"; rows17[1] = tuple(r)
    _mk(os.path.join(er, "f17_order1_drift.db"), WIDE_DDL, {"verdicts": rows17})
    exp["experiment_results/f17_order1_drift.db"] = "MIXED"
    # A1 (reviewer) the writer transposed ORDER 1 (vote1 = T(p1)), combined winner consistent with the stored votes -> MIXED
    _mk(os.path.join(er, "a1_order1_transposed.db"), WIDE_DDL, {"verdicts": [
        (i, "ma", "mb", 100 + i // 2, T(p1), p2) + (lambda w, f, v: (w, int(f), int(v)))(*rj.combine_orders(T(p1), p2)) +
        (_raw(p1) if p1 != "INVALID" else "garbage", _raw(p2)) for i, (p1, p2) in enumerate(V)]})     # raw1 = the TRUE order-1 text, vote1 = its transpose
    exp["experiment_results/a1_order1_transposed.db"] = "MIXED"
    # A4 (reviewer) raw-only WIDE, the writer's combiner did NOT transpose: never CONTESTANT, never transposed -> MIXED
    ddl_a4 = "CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, winner TEXT, flip INTEGER, raw1 TEXT, raw2 TEXT);"
    _mk(os.path.join(er, "a4_rawonly_untransposed.db"), ddl_a4, {"verdicts": [
        (i, i, "ma", "mb", combine_contestant(p1, p2)[0], int(combine_contestant(p1, p2)[1]), _raw(p1) if p1 != "INVALID" else "x", _raw(p2))
        for i, (p1, p2) in enumerate(V)]})
    exp["experiment_results/a4_rawonly_untransposed.db"] = "MIXED"
    ddl_long = ("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, stratum TEXT, task_id TEXT, nj TEXT);"
                "CREATE TABLE verdicts (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, finish TEXT, PRIMARY KEY (mid, arm));")
    sch_long = [(i, "headline", "t%d" % (i % 9), "") for i in range(len(V))]
    # A6c (reviewer) LONG fwd/rev LABELS SWAPPED, the fwd-labelled (true order-2) rows stored transposed -> MIXED via order 1
    _mk(os.path.join(er, "a6c_long_swapped.db"), ddl_long, {"schedule": sch_long, "verdicts": [
        x for i, (p1, p2) in enumerate(V) for x in ((i, "rev", p1, .8, 0, _raw(p1) if p1 != "INVALID" else "x", "stop"),
                                                    (i, "fwd", T(p2), .8, 0, _raw(p2), "stop"))]})
    exp["experiment_results/a6c_long_swapped.db"] = "MIXED"
    # F18 LONG fwd/rev stored CONTESTANT-labelled (rev = T(parse)): CERTIFIED-CONTESTANT; with the pair roles swapped it would be MIXED
    _mk(os.path.join(er, "f18_long_contestant.db"), ddl_long, {"schedule": sch_long, "verdicts": [
        x for i, (p1, p2) in enumerate(V) for x in ((i, "fwd", p1, .8, 0, _raw(p1) if p1 != "INVALID" else "x", "stop"),
                                                    (i, "rev", T(p2), .8, 0, _raw(p2), "stop"))]})
    exp["experiment_results/f18_long_contestant.db"] = "CERTIFIED-CONTESTANT"
    # F19 Kotlin judge_calls with TWO judges (review H2): 10 matches judged by both judges in both orders, 10 with grok order 1 + Mistral order 2
    ddl_k = ("CREATE TABLE judge_calls (id INTEGER PRIMARY KEY AUTOINCREMENT, snapshot_id TEXT, eval_question_id INTEGER, model_a TEXT, model_b TEXT, "
             "presentation_order INTEGER, judge_model TEXT, raw_content TEXT, parsed_winner TEXT, finish_reason TEXT);")
    rk = []
    for i, (p1, p2) in enumerate(V[:20]):
        r1_ = _raw(p1) if p1 != "INVALID" else "x"
        if i < 10:
            for j in ("grok", "mistral"):
                rk += [(None, "s", i, "ma", "mb", 1, j, r1_, p1, "stop"), (None, "s", i, "ma", "mb", 2, j, _raw(p2), p2, "stop")]
        else:
            rk += [(None, "s", i, "ma", "mb", 1, "grok", r1_, p1, "stop"), (None, "s", i, "ma", "mb", 2, "mistral", _raw(p2), p2, "stop")]
    _mk(os.path.join(er, "f19_kotlin_two_judges.db"), ddl_k, {"judge_calls": rk})
    exp["experiment_results/f19_kotlin_two_judges.db"] = "CERTIFIED-POSITIONAL"
    # F20 a LONG table with a DUPLICATE (two rows under one order value for one match key): the pairing is not unique -> REFUSED
    rows20 = [(None, "s", i, "ma", "mb", o, "grok", _raw("Model A"), "Model A", "stop") for i in range(5) for o in (1, 2)]
    rows20.append((None, "s", 0, "ma", "mb", 1, "grok", _raw("Model B"), "Model B", "stop"))
    _mk(os.path.join(er, "f20_duplicate.db"), ddl_k, {"judge_calls": rows20})
    exp["experiment_results/f20_duplicate.db"] = "UNCERTIFIABLE"
    rows20b = [(None, "s", i, "ma", "mb", o, "grok", _raw("Model A"), "Model A", "stop") for i in range(5) for o in (1, 2)]
    rows20b.append((None, "s", 3, "ma", "mb", 2, "grok", _raw("Model B"), "Model B", "stop"))
    _mk(os.path.join(er, "f20b_duplicate_order2.db"), ddl_k, {"judge_calls": rows20b})
    exp["experiment_results/f20b_duplicate_order2.db"] = "UNCERTIFIABLE"
    # F11 Kotlin judge_calls at the repository root (presentation_order 1/2, raw_content, parsed_winner), positional, no PK beyond id
    ddl11 = ("CREATE TABLE judge_calls (id INTEGER PRIMARY KEY AUTOINCREMENT, snapshot_id TEXT, eval_question_id INTEGER, model_a TEXT, model_b TEXT, "
             "presentation_order INTEGER, judge_model TEXT, raw_content TEXT, parsed_winner TEXT, finish_reason TEXT);"
             "CREATE TABLE match_history (id INTEGER PRIMARY KEY, winner TEXT);")
    rows11 = {"judge_calls": []}
    for i, (p1, p2) in enumerate(V):
        rows11["judge_calls"].append((None, "s", i, "ma", "mb", 1, "grok-4-1-fast-non-reasoning", _raw(p1) if p1 != "INVALID" else "x", p1, "stop"))
        rows11["judge_calls"].append((None, "s", i, "ma", "mb", 2, "grok-4-1-fast-non-reasoning", _raw(p2), p2, "stop"))
    _mk(os.path.join(root, "ratings_fixture.db"), ddl11, rows11)
    exp["ratings_fixture.db"] = "CERTIFIED-POSITIONAL"
    # F12 raw-only wide with a name-labelled combined winner joined through the schedule (leaf_powered-like), positional combination
    ddl12 = ("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, anchor TEXT, leaf TEXT, qid INTEGER, model_a TEXT, model_b TEXT);"
             "CREATE TABLE verdicts (mid INTEGER, arm TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (mid, arm));")
    rows12 = {"schedule": [(i, "Law", "l", i, "ma%d" % i, "mb%d" % i) for i in range(len(V))], "verdicts": []}
    for i, (p1, p2) in enumerate(V):
        w, f, inv = rj.combine_orders(p1, p2)
        rows12["verdicts"].append((i, "anchor", {"Model A": "ma%d" % i, "Model B": "mb%d" % i}.get(w, w), int(f), int(inv),
                                   _raw(p1) if p1 != "INVALID" else "x", _raw(p2), 0.0))
    _mk(os.path.join(er, "f12_rawonly.db"), ddl12, rows12)
    exp["experiment_results/f12_rawonly.db"] = "CERTIFIED-POSITIONAL"
    # ── VFC-RX-RULING (f1e9e68) fixtures (a)-(d), each decided on data; (e) and (f) are executed in selftest() ──
    dec = [i for i, (p1, p2) in enumerate(V) if p1 in POS and p2 in POS]          # rows with both votes decisive (informative candidates)
    # (a) LONG name-labelled (arena13-like, basename profile), SOME reversed labels unresolvable, the resolved rows consistent -> R6
    rows_a = [r[:5] + (0.0,) for r in rows9["verdicts"] if r[1] != "selfref"]
    unres_a = set(dec[3:6])
    rows_a = [r[:2] + ("stranger",) + r[3:] if r[1] == "reversed" and r[0] in unres_a else r for r in rows_a]
    os.makedirs(os.path.join(er, "rx_a"), exist_ok=True); _mk(os.path.join(er, "rx_a", "arena13.db"), ddl9, {"schedule": sched9, "verdicts": rows_a})
    exp["experiment_results/rx_a/arena13.db"] = "UNCERTIFIABLE"
    # (b) the same, with ONE resolved order-1 contradiction (an ensemble row stores the other contestant) -> MIXED, not R6
    i_b = dec[0]; m1b = {"Model A": new, "Model B": "opp%d" % (i_b % 4)}
    rows_b = [r[:2] + (m1b[T(V[i_b][0])],) + r[3:] if r[1] == "ensemble" and r[0] == i_b else r for r in rows_a]
    os.makedirs(os.path.join(er, "rx_b"), exist_ok=True); _mk(os.path.join(er, "rx_b", "arena13.db"), ddl9, {"schedule": sched9, "verdicts": rows_b})
    exp["experiment_results/rx_b/arena13.db"] = "MIXED"
    # (c) WIDE E-COMB primary (stored votes, no raw; the clean writer w_rj.py): ONE combined label unresolvable -> R6 (never reaches the combiner check)
    rows_c = pos8(H3_TS["after"]); i_c = dec[1]; rows_c[i_c] = rows_c[i_c][:6] + ("stranger",) + rows_c[i_c][7:]
    _mk(os.path.join(er, "ecomb_r6.db"), ddl8, {"verdicts": rows_c})
    exp["experiment_results/ecomb_r6.db"] = "UNCERTIFIABLE"
    # (c') E-COMB primary with an unresolvable label AND a resolved row contradicting both hypotheses -> MIXED (R-3)
    rows_cm = list(rows_c); i_cm = next(i for i in dec if i != i_c)
    rows_cm[i_cm] = rows_cm[i_cm][:6] + (T(V[i_cm][0]),) + rows_cm[i_cm][7:]        # the order-1 loser stored as the winner: neither combine gives it
    _mk(os.path.join(er, "ecomb_r6_mixed.db"), ddl8, {"verdicts": rows_cm})
    exp["experiment_results/ecomb_r6_mixed.db"] = "MIXED"
    # (c'') raw-only E-COMB (leaf_powered-like, names from the schedule), ONE combined label unresolvable -> R6
    rows_c2 = {"schedule": rows12["schedule"], "verdicts": list(rows12["verdicts"])}
    rows_c2["verdicts"][i_c] = rows_c2["verdicts"][i_c][:2] + ("stranger",) + rows_c2["verdicts"][i_c][3:]
    _mk(os.path.join(er, "rawonly_r6.db"), ddl12, rows_c2)
    exp["experiment_results/rawonly_r6.db"] = "UNCERTIFIABLE"
    # (c''') raw-only with an UNTRANSPOSING combiner (B2) AND one unresolvable combined label -> MIXED (B2 before R6)
    rows_c3 = [(i, i, "ma", "mb", combine_contestant(p1, p2)[0], int(combine_contestant(p1, p2)[1]), _raw(p1) if p1 != "INVALID" else "x", _raw(p2))
               for i, (p1, p2) in enumerate(V)]
    rows_c3[i_c] = rows_c3[i_c][:4] + ("stranger",) + rows_c3[i_c][5:]
    _mk(os.path.join(er, "rawonly_b2_r6.db"), ddl_a4, {"verdicts": rows_c3})
    exp["experiment_results/rawonly_b2_r6.db"] = "MIXED"
    # (d) WIDE with raw (E-RAW decides POSITIONAL) and a combined column written CONTESTANT-style with two unresolvable labels: the secondary's
    # resolved subset certifies the OTHER frame -> EVIDENCE CONFLICT -> MIXED (R-6: the power to downgrade survives)
    rows_d = [_wide_row(i, p1, p2, p2, combine_contestant(p1, p2)) for i, (p1, p2) in enumerate(V)]
    for i in dec[:2]: rows_d[i] = rows_d[i][:6] + ("stranger",) + rows_d[i][7:]
    _mk(os.path.join(er, "rx_d_conflict.db"), WIDE_DDL, {"verdicts": rows_d})
    exp["experiment_results/rx_d_conflict.db"] = "MIXED"
    # (d') the same frame, the combined column POSITIONAL, two labels unresolvable: the primary stays CERTIFIED-POSITIONAL (E-RAW decides), the
    # secondary is UNCERTIFIABLE (R6), secondary: never CERTIFIED, never counted in P4
    rows_d2 = _wide_rows(V)
    for i in dec[:2]: rows_d2[i] = rows_d2[i][:6] + ("stranger",) + rows_d2[i][7:]
    _mk(os.path.join(er, "rx_d_secondary.db"), WIDE_DDL, {"verdicts": rows_d2})
    exp["experiment_results/rx_d_secondary.db"] = "CERTIFIED-POSITIONAL"
    # -- review a3da968 F1 / F3 / F4 / F6 fixtures --
    ntie = [i for i, (p1, p2) in enumerate(V) if "TIE" in (p1, p2) and "INVALID" not in (p1, p2)]     # a vote is TIE: not both decisive
    # (a1) F3: EXACTLY ONE unresolvable label, on ORDER 1 (an ensemble row), the resolved rows consistent -> R6
    i_a1 = dec[2]
    rows_a1 = [r[:2] + ("stranger",) + r[3:] if r[1] == "ensemble" and r[0] == i_a1 else r
               for r in (r[:5] + (0.0,) for r in rows9["verdicts"] if r[1] != "selfref")]
    os.makedirs(os.path.join(er, "rx_a1"), exist_ok=True); _mk(os.path.join(er, "rx_a1", "arena13.db"), ddl9, {"schedule": sched9, "verdicts": rows_a1})
    exp["experiment_results/rx_a1/arena13.db"] = "UNCERTIFIABLE"
    # (c-tie) F1: E-COMB primary, ONE unresolvable combined label on a row whose vote is TIE -> R6 ("whatever the parse of the row")
    rows_ct = pos8(H3_TS["after"]); rows_ct[ntie[0]] = rows_ct[ntie[0]][:6] + ("stranger",) + rows_ct[ntie[0]][7:]
    _mk(os.path.join(er, "ecomb_r6_tie.db"), ddl8, {"verdicts": rows_ct})
    exp["experiment_results/ecomb_r6_tie.db"] = "UNCERTIFIABLE"
    # (c-amb) F4: E-COMB, every decisive row's combined label unresolvable: the resolved subset is AMBIGUOUS -> R6, not AMBIGUOUS
    rows_ca = [r[:6] + ("stranger",) + r[7:] if i in set(dec) else r for i, r in enumerate(pos8(H3_TS["after"]))]
    _mk(os.path.join(er, "ecomb_r6_amb.db"), ddl8, {"verdicts": rows_ca})
    exp["experiment_results/ecomb_r6_amb.db"] = "UNCERTIFIABLE"
    # (c-tampered) F6: an R6 E-COMB unit whose writer patches rejudge_grok: still R6; H3 runs descriptively and FAILS in the notes
    _mk(os.path.join(er, "ecomb_r6_tampered.db"), ddl8, {"verdicts": rows_c})
    exp["experiment_results/ecomb_r6_tampered.db"] = "UNCERTIFIABLE"
    # (d-tie) F1: a WIDE secondary whose ONLY unresolvable label sits on a TIE-vote row -> the secondary is UNCERTIFIABLE (R6), secondary
    rows_dt = _wide_rows(V); rows_dt[ntie[0]] = rows_dt[ntie[0]][:6] + ("stranger",) + rows_dt[ntie[0]][7:]
    _mk(os.path.join(er, "rx_d_tie.db"), WIDE_DDL, {"verdicts": rows_dt})
    exp["experiment_results/rx_d_tie.db"] = "CERTIFIED-POSITIONAL"
    # (d-warning) F4: an R6 secondary whose RESOLVED subset is MIXED keeps the WARNING (R-6 "If they are MIXED, the WARNING applies as now")
    rows_dw = _wide_rows(V)
    for i in dec[:2]: rows_dw[i] = rows_dw[i][:6] + ("stranger",) + rows_dw[i][7:]
    rows_dw[dec[4]] = rows_dw[dec[4]][:6] + (T(V[dec[4]][0]),) + rows_dw[dec[4]][7:]
    _mk(os.path.join(er, "rx_d_warning.db"), WIDE_DDL, {"verdicts": rows_dw})
    exp["experiment_results/rx_d_warning.db"] = "CERTIFIED-POSITIONAL"
    if d2_installed_name():
        _mk(os.path.join(er, "d2_installed.db"), ddl8, {"verdicts": pos8(H3_TS["after"])})
        exp["experiment_results/d2_installed.db"] = "CERTIFIED-POSITIONAL"
    # not enumerated: a non-dual SQLite file, a non-SQLite file with a .db name
    _mk(os.path.join(er, "not_dual.db"), "CREATE TABLE grades (qid INTEGER, model TEXT, grade REAL);", {"grades": [(1, "m", 0.5)]})
    with open(os.path.join(er, "not_sqlite.db"), "w") as f: f.write("plain text")
    return exp, V


@contextlib.contextmanager
def connect_trap(allowed_dir):
    """sqlite3.connect refuses any path outside allowed_dir for the duration (the selftests' no-DB-of-record guarantee)."""
    real = sqlite3.connect
    base = os.path.abspath(allowed_dir).replace("\\", "/").lower()
    def trap(db, *a, **k):
        s = str(db).replace("\\", "/").lower()
        if s != ":memory:" and base not in s:
            raise AssertionError("[SELFTEST] refused to open %s outside %s" % (db, allowed_dir))
        return real(db, *a, **k)
    sqlite3.connect = trap
    try: yield
    finally: sqlite3.connect = real


def selftest(quiet=False):
    """Every class (including a DELIBERATELY TRANSPOSED fixture that is never certified positional), every criterion and prediction branch,
    the write-once refusal, the reader's transposition and the read-only assertion, BY EXECUTION on synthetic caches under
    tempfile.mkdtemp(). No DB of record is opened: sqlite3.connect is trapped to refuse any path outside the temp dir."""
    tmp = tempfile.mkdtemp(prefix="vfc_selftest_")
    ok = True; lines = []
    def check(cond, what):
        nonlocal ok
        lines.append("  [%s] %s" % ("PASS" if cond else "FAIL", what)); ok = ok and bool(cond)
    try:
        with connect_trap(tmp):
            exp, V = build_fixtures(tmp)
            cctx, w_rj_sha = build_comb_repo(tmp)
            cctx["name_content"] = {sha256_full(os.path.join(tmp, "experiment_results", "x12", "arena13.db")): ("arena13.db", "experiment_results/x12/arena13.db")}
            files, stats0, listing = enumerate_caches(tmp, lambda s: None)
            enum = sorted(rel(p, tmp) for p, _ in listing)
            check(enum == sorted(exp), "enumeration = the %d dual-order fixtures (a non-dual SQLite file and a non-SQLite .db excluded by the rule)" % len(exp))
            got = {}
            for p, sch in listing:
                con = open_ro(p)
                try:
                    units = [certify_table(con, p, s, cctx) for s in sch.values()]
                    try:
                        con.execute("CREATE TABLE probe_write (a)"); wrote = True
                    except sqlite3.OperationalError:
                        wrote = False
                finally:
                    con.close()
                check(not wrote, "read-only: a write through open_ro(%s) is refused" % rel(p, tmp))
                got[rel(p, tmp)] = (cache_class(units), units)
            for path, want in sorted(exp.items()):
                k, units = got.get(path, ("(absent)", []))
                check(k == want, "%s -> %s (expected %s) [%s]" % (path, k, want, "; ".join("%s %s %s" % (u["table"], u["klass"], u["evidence"]) for u in units)))
            k2 = got["experiment_results/f2_wide_transposed.db"][0]
            check(k2 != "CERTIFIED-POSITIONAL", "THE DELIBERATELY TRANSPOSED FIXTURE IS REFUSED AS POSITIONAL (class %s): the sign flip is caught" % k2)
            u2b = got["experiment_results/f2b_one_row_sign_flip.db"][1][0]
            check(u2b["klass"] == "MIXED" and "1" in u2b["counts"]["contradict_positional"],
                  "ONE transposed row refuses the whole cache: MIXED, contradicting row id listed %s" % u2b["counts"]["contradict_positional"])
            u7 = got["experiment_results/f7_conflict.db"][1][0]
            check(any("EVIDENCE CONFLICT" in n for n in u7["notes"]), "E-RAW / E-COMB conflict refused: %s" % u7["notes"])
            u10 = got["experiment_results/f10_single_order.db"][1][0]
            check(u10["klass"] == NDO and any("NOT-DUAL-ORDER" in n for n in u10["notes"]),
                  "single-order arm-keyed table (arm values base/card) is the SIXTH class NOT-DUAL-ORDER, not UNCERTIFIABLE")
            u14 = got["experiment_results/f14_values_not_rows.db"][1][0]
            check(u14["klass"] == NDO and u14["arm_values"] == {"fwd": 10, "rev": 10} and u14["dual_keys"] == 0,
                  "ROW-LEVEL rule: both order values present in the table (%s) but no match has both -> NOT-DUAL-ORDER" % u14["arm_values"])
            k15, us15 = got["experiment_results/f15_dual_plus_single.db"]
            check(k15 == "CERTIFIED-POSITIONAL" and sorted((u["table"], u["klass"]) for u in us15) == [("side_arm", NDO), ("verdicts", "CERTIFIED-POSITIONAL")],
                  "a cache with a dual-order table is classed on it; its single-order table is NOT-DUAL-ORDER and listed")
            check(got["experiment_results/f16_wide_single.db"][1][0]["klass"] == NDO, "a WIDE table with no row carrying both orders is NOT-DUAL-ORDER")
            h3 = {k.split("/")[-1][:-3]: got[k][1][0] for k in got if k.split("/")[-1].startswith("h3_") or k.endswith("f8_comb_transposed.db")}
            ccs = {k: (u["klass"], (u.get("combiner_check") or {}).get("ok"), "; ".join((u.get("combiner_check") or {}).get("result", []))[:70]) for k, u in h3.items()}
            check(h3["h3_rj_after"]["klass"] == "CERTIFIED-POSITIONAL" and "AST-identical" in " ".join(h3["h3_rj_after"]["combiner_check"]["result"])
                  and "last commit" in " ".join(h3["h3_rj_after"]["combiner_check"]["evidence"]),
                  "H3 PASS: writer calls rejudge_grok.combine_orders, pinned by first write at commit A, rejudge_grok pinned at B: CERTIFIED (%s)" % ccs["h3_rj_after"][2])
            check(h3["f8_comb_transposed"]["klass"] == "CERTIFIED-CONTESTANT", "H3 PASS keeps an E-COMB CONTESTANT certificate when the combiner verifies")
            check(h3["h3_local"]["klass"] == "UNCERTIFIABLE" and "not AST-identical" in " ".join(h3["h3_local"]["combiner_check"]["result"]),
                  "D1 (94731da): a local combiner with one transposition that is NOT AST-identical now FAILS: %s" % ccs["h3_local"][2])
            for ck in ("c3", "c4", "c5", "c9", "c6"):
                uc = got["experiment_results/%s.db" % ck][1][0]
                check(uc["klass"] == "UNCERTIFIABLE" and uc.get("uncert_reason") == "R2" and "not AST-identical" in " ".join(uc["combiner_check"]["result"]),
                      "D1: the re-review's %s is UNCERTIFIABLE (R2, combiner not verified)%s: %s" % (ck.upper(), " [C6: a CONSERVATIVE false fail, stated limit (i)]"
                      if ck == "c6" else "", " ".join(uc["combiner_check"]["result"])[:120]))
            uli = got["experiment_results/h3_local_ident.db"][1][0]
            check(uli["klass"] == "CERTIFIED-POSITIONAL" and "AST-identical" in " ".join(uli["combiner_check"]["result"]),
                  "D1: a LOCAL copy AST-identical to the pinned combine_orders (renamed parameters, a docstring) is verified")
            ulb = got["experiment_results/h3_local_badcopy.db"][1][0]
            check(ulb["klass"] == "UNCERTIFIABLE" and ulb.get("uncert_reason") == "R2" and "is NOT AST-identical to the recipe's combine_orders (REF)"
                  in " ".join(ulb["combiner_check"]["result"]), "D-A: a local copy of a pinned body that is NOT the recipe's REF is UNCERTIFIABLE (R2); REF printed")
            check("IS AST-identical to the recipe's combine_orders (REF)" in " ".join(uli["combiner_check"]["result"]),
                  "D-A: the local-copy arm prints the pinned body's REF identity on a pass too")
            for rb in ("rjbad_direct", "rjbad_localcopy"):
                ur = got["experiment_results/%s.db" % rb][1][0]
                check(ur["klass"] == "UNCERTIFIABLE" and ur.get("uncert_reason") == "R2" and ur["counts"]["agree_contestant"] == ur["counts"]["order2_informative"] > 0,
                      "D-A: %s, rows as the bad pinned body wrote them (E-COMB reads CONTESTANT %d / %d): UNCERTIFIABLE (R2), NEVER a certificate"
                      % (rb, ur["counts"]["agree_contestant"], ur["counts"]["order2_informative"]))
            for k in W_DC:
                ud = got["experiment_results/%s.db" % k][1][0]
                check(ud["klass"] == "UNCERTIFIABLE" and ud.get("uncert_reason") == "R2" and "rebinds or patches rejudge_grok, or runs dynamic code (D-C, 776a2dd)" in " ".join(ud["combiner_check"]["result"]),
                      "D-C: %s -> UNCERTIFIABLE (R2): %s" % (k, " ".join(ud["combiner_check"]["result"])[:110]))
            for k, (_, want) in W_DCP_SPEC.items():
                ud = got["experiment_results/%s.db" % k][1][0]; cc = ud.get("combiner_check") or {}
                if want is None and k == "dcp_dep_clean":
                    ev = " ".join(cc.get("evidence", []))
                    check(ud["klass"] == "CERTIFIED-POSITIONAL" and "dcpmod_clean.py@" in ev and "rejudge_grok.py@" in ev,
                          "D-C' (f): a writer importing a CLEAN local module certifies; the scan ran on it: %s" % ev[ev.find("local imports"):][:150])
                elif want is None:
                    check(ud["klass"] == "CERTIFIED-POSITIONAL" and cc.get("ok") is True and cc.get("callsite_ok") is True,
                          "%s: a writer with no D1 / D2 route (%s) certifies (no false fail on the rule's boundary)" % (k, W_DCP_SPEC[k][0].strip().replace("\n", "; ")))
                else:
                    check(ud["klass"] == "UNCERTIFIABLE" and ud.get("uncert_reason") == "R2" and want in " ".join(cc.get("result", [])),
                          "D-C': %s -> UNCERTIFIABLE (R2) on %r: %s" % (k, want, " ".join(cc.get("result", []))[:120]))
            urs = got["experiment_results/dcp_rj_self.db"][1][0]; ccs_ = " ".join((urs.get("combiner_check") or {}).get("result", []))
            check(urs["klass"] == "UNCERTIFIABLE" and urs.get("uncert_reason") == "R2" and "rejudge_grok binds combine_orders 1 times by def and 1 times otherwise" in ccs_,
                  "D-C' (f): rejudge_grok.py at the pin rebinding its own combine_orders -> UNCERTIFIABLE (R2): %s" % ccs_[:120])
            rsb = lambda src: rj_self_bindings(ast.parse(src))
            check(rsb(REF_COMBINE_ORDERS) == [] and len(rsb(REF_COMBINE_ORDERS + REF_COMBINE_ORDERS)) == 1 and len(rsb("from x import parse_judge\n")) == 1,
                  "D-C' (f): rj_self_bindings: one def clean; two defs, or an import binding parse_judge, flagged")
            # VFC-NAME-PROFILE-BY-CONTENT: the copy gets its original's class by content; RX executed on an unmapped name-labelled table (D6)
            orig = [u for u in got["experiment_results/x12/arena13.db"][1] if u["table"] == "verdicts"][0]
            for cp in ("_backup/arena13_copy_2026-09-23.db", "_backup/placebo.db"):
                ucp = [u for u in got["experiment_results/" + cp][1] if u["table"] == "verdicts"][0]
                check(ucp["klass"] == "CERTIFIED-CONTESTANT" and ucp.get("uncert_reason") is None and ucp["counts"] == orig["counts"]
                      and ucp["label_space"] == "names" and str(ucp.get("name_profile")).startswith("content sha256"),
                      "NAME-PROFILE BY CONTENT: the byte-identical copy %s is CERTIFIED-CONTESTANT with the original's counts, profile by %s" % (cp, ucp.get("name_profile")))
            check(str(orig.get("name_profile")).startswith("content sha256") and
                  str([u for u in got["experiment_results/x12b/arena13.db"][1] if u["table"] == "verdicts"][0].get("name_profile")) == "basename arena13.db",
                  "NAME-PROFILE: the original found by content, a different content under a mapped basename found by basename (the pre-existing key)")
            uxu = got["experiment_results/x12u/names_unmapped.db"][1][0]
            check(uxu["klass"] == "UNCERTIFIABLE" and uxu.get("uncert_reason") == "R6" and uxu.get("name_profile") is None and uxu["counts"]["unresolvable_labels"] > 0
                  and uxu["label_space"] == "unresolved",
                  "D6 / R-1: a name-labelled table under an UNMAPPED basename with unmatched content is UNCERTIFIABLE (R6), label_space 'unresolved': %s"
                  % uxu["notes"][-1:])
            check(all(len(h) == 64 and v[0] in NAME_PROFILES for h, v in NAME_PROFILE_CONTENT.items()) and len(NAME_PROFILE_CONTENT) == 4,
                  "NAME_PROFILE_CONTENT: four full sha256 keys, each naming a NAME_PROFILES profile")
            qcp = os.path.join(tmp, "experiment_results", "_backup", "arena13_copy_2026-09-23.db"); ccp = open_ro(qcp)
            ucp = [u for u in got["experiment_results/_backup/arena13_copy_2026-09-23.db"][1] if u["table"] == "verdicts"][0]
            rcp = sorted((r["key"], r["p1"], r["p2"]) for r in unit_votes(ccp, qcp, ucp, cctx["name_content"])[0] if r["p1"] != "INVALID")
            rcp0 = None
            try: unit_votes(ccp, qcp, ucp)
            except SystemExit as e: rcp0 = str(e)
            ccp.close()
            check(rcp == sorted((i, p1, p2) for i, (p1, p2) in enumerate(V) if p1 != "INVALID") and rcp0 is not None and "[FRAME] REFUSED (R-8)" in rcp0,
                  "reader on the copy: with the content map it returns the true positional votes; without it (unmapped basename) the reader REFUSES "
                  "(R-8), never an empty or shrunk list: %s" % (rcp0 or "")[:110])
            uo1 = got["experiment_results/o1_transpose.db"][1][0]
            check(uo1["klass"] == "UNCERTIFIABLE" and uo1.get("uncert_reason") == "R3" and "(order-1) is not bound as the first element" in " ".join(uo1["combiner_check"]["callsite"])
                  and uo1["secondary"] is None and uo1["counts"]["agree_positional"] == uo1["counts"]["order2_informative"] > 0,
                  "D-B: the re-review's x1 (order 1 transposed; E-COMB alone reads POSITIONAL %d / %d) is UNCERTIFIABLE (R3) on the order-1 argument"
                  % (uo1["counts"]["agree_positional"], uo1["counts"]["order2_informative"]))
            csl1 = lambda k: " ".join(got["experiment_results/%s.db" % k][1][0]["combiner_check"]["callsite"])
            check("the order-1 column (vote1, index 4) stores ['v1s']" in csl1("o1_othername"), "D-B (i): an order-1 column storing another name than the 1st argument FAILS")
            check("'v1' (order-1) is not bound as the first element" in csl1("o1_subscript"), "D-B (ii): a SUBSCRIPTED order-1 parse FAILS")
            check("cannot parse: no CREATE TABLE verdicts carrying vote1 and vote2_raw" in csl1("o1_nocol"),
                  "D-B: a writer whose CREATE TABLE lacks the order-1 column FAILS (cannot parse)")
            check("order-1 column vote1 stores 'v1' = the combiner's 1st argument" in " ".join(h3["h3_rj_after"]["combiner_check"]["callsite"]),
                  "D-B PASS: the clean pattern verifies the order-1 argument too")
            upr = got["experiment_results/cs_param.db"][1][0]
            check(upr["klass"] == "UNCERTIFIABLE" and "2 bindings" in " ".join(upr["combiner_check"]["callsite"]),
                  "D2 (ii): a PARAMETER re-bound from parse_judge counts as a binding (2 bindings): FAILS")
            check(h3["h3_rj_before"].get("pin_timing") is True and not h3["h3_runmeta_bad"].get("pin_timing"),
                  "L2: pin timing set by the comparison (a first write before the writer's earliest commit), NOT by an unmatched run_meta sha")
            check(h3["h3_zero"]["klass"] == "UNCERTIFIABLE" and "0 transposition dicts" in " ".join(h3["h3_zero"]["combiner_check"]["result"])
                  and any("E-COMB, combiner not verified" in n for n in h3["h3_zero"]["notes"]),
                  "H3 FAIL: ZERO transpositions -> UNCERTIFIABLE ('E-COMB, combiner not verified')")
            check(h3["h3_two"]["klass"] == "UNCERTIFIABLE" and "2 transposition dicts" in " ".join(h3["h3_two"]["combiner_check"]["result"]), "H3 FAIL: TWO transpositions -> UNCERTIFIABLE")
            check(h3["h3_rj_between"]["klass"] == "UNCERTIFIABLE" and "is NOT AST-identical to the recipe's combine_orders (REF): not verified" in " ".join(h3["h3_rj_between"]["combiner_check"]["result"]),
                  "D-A: a DIRECT call whose pinned rejudge_grok body is not the recipe's REF is NOT verified: %s" % ccs["h3_rj_between"][2])
            check(h3["h3_rj_before"]["klass"] == "UNCERTIFIABLE" and "the writer's run-time blob cannot be pinned" in " ".join(h3["h3_rj_before"]["combiner_check"]["result"]),
                  "H3 FAIL: a first write before any commit of the writer: blob UNPINNABLE -> UNCERTIFIABLE")
            check(h3["h3_nowriter"]["klass"] == "UNCERTIFIABLE" and "no writer named" in " ".join(h3["h3_nowriter"]["combiner_check"]["result"]),
                  "H3 FAIL: an E-COMB cache with no named writer -> UNCERTIFIABLE")
            check(h3["h3_runmeta"]["klass"] == "CERTIFIED-POSITIONAL" and "run_meta script_sha256_16_lf = %s" % w_rj_sha in " ".join(h3["h3_runmeta"]["combiner_check"]["evidence"]),
                  "H3 PASS with the writer pinned by the cache's run_meta sha (%s), rejudge_grok at the first write" % w_rj_sha)
            check(h3["h3_runmeta_bad"]["klass"] == "UNCERTIFIABLE" and "NO commit" in " ".join(h3["h3_runmeta_bad"]["combiner_check"]["evidence"]),
                  "H3 FAIL: a run_meta sha that matches no commit of the writer -> UNPINNABLE -> UNCERTIFIABLE")
            rsn = lambda k: " ".join(h3[k]["combiner_check"]["result"])
            cs = {k: got["experiment_results/%s.db" % k][1][0] for k in ("cs_transpose", "cs_othername", "cs_subscript", "cs_wrap", "cs_rebind",
                                                                         "cs_norow", "cs_noddl", "cs_helper", "cs_second", "cs_whole")}
            csl = lambda k: " ".join(cs[k]["combiner_check"]["callsite"])
            check(all(u["klass"] == "UNCERTIFIABLE" and u.get("uncert_reason") == "R3" and u["combiner_check"]["ok"] for u in cs.values()),
                  "D2: ten call-site fixtures pass the COMBINER check and are UNCERTIFIABLE for the ARGUMENT (reason R3)")
            check("cannot parse: no row tuple" in csl("cs_norow"), "D2 (i): a row built as a LIST (no row tuple of the table's width) FAILS: cannot parse")
            check("cannot parse: no CREATE TABLE" in csl("cs_noddl"), "D2: a writer without the table's CREATE TABLE FAILS: cannot parse")
            check("not bound as the first element" in csl("cs_helper") and "my_parse" in csl("cs_helper"), "D2 (ii): a tuple-unpack from a NON-parse_judge helper FAILS")
            check("(tuple1:" in csl("cs_second"), "D2 (ii): binding the SECOND element (the confidence) of parse_judge's result FAILS")
            check("(plain:" in csl("cs_whole"), "D2 (ii): binding the WHOLE parse_judge result (no unpack) FAILS")
            check("(ii)" in csl("cs_transpose") and "not bound as the first element" in csl("cs_transpose"),
                  "D2 (ii): a call-site TRANSPOSITION (v2c = T(parse)) FAILS: %s" % csl("cs_transpose")[:110])
            check("(i) the order-2 column" in csl("cs_othername") and "stores ['v2s']" in csl("cs_othername"),
                  "D2 (i): a writer that STORES a different name than it passes FAILS: %s" % csl("cs_othername")[:110])
            check("(ii)" in csl("cs_subscript") and "tuple-unpack" in csl("cs_subscript"), "D2 (ii): a SUBSCRIPTED parse output FAILS")
            check("(i) the 2nd argument is not a bare name" in csl("cs_wrap"), "D2 (i): a WRAPPED argument (str(v2)) FAILS")
            check("2 bindings" in csl("cs_rebind"), "D2 (ii): a RE-ASSIGNMENT of the parsed name between parse and call FAILS")
            check(h3["h3_rj_after"]["combiner_check"]["callsite_ok"] and "bound directly from parse_judge" in " ".join(h3["h3_rj_after"]["combiner_check"]["callsite"]),
                  "D2 PASS: the clean pattern (v2, _ = rj.parse_judge(raw2); rj.combine_orders(v1, v2); v2 stored in vote2_raw)")
            check(h3["h3_order1"]["klass"] == "UNCERTIFIABLE" and "not AST-identical" in rsn("h3_order1"),
                  "re-review: a transposition on the ORDER-1 parameter FAILS (%s)" % rsn("h3_order1")[:90])
            check(h3["h3_ident"]["klass"] == "UNCERTIFIABLE" and "0 transposition dicts" in rsn("h3_ident"), "re-review: an IDENTITY dict is not a transposition: FAILS")
            check(h3["h3_oneparam"]["klass"] == "UNCERTIFIABLE" and "1 parameters" in rsn("h3_oneparam"), "re-review: a ONE-parameter combiner FAILS")
            check(h3["h3_twocalls"]["klass"] == "UNCERTIFIABLE" and "(a direct call)" in rsn("h3_twocalls") and "0 transposition dicts" in rsn("h3_twocalls"),
                  "re-review: one verified call beside one unverified combine call FAILS (ALL calls must verify)")
            check(h3["h3_straddle"]["klass"] == "UNCERTIFIABLE" and "the writer's run-time blob cannot be pinned" in rsn("h3_straddle")
                  and "min(verdicts.ts)" in " ".join(h3["h3_straddle"]["combiner_check"]["evidence"]),
                  "re-review: pinned at the FIRST write (a first write before the writer's only commit, a last write after it) -> unpinnable")
            check(h3["h3_contestant_zero"]["klass"] == "UNCERTIFIABLE" and any("would have been CERTIFIED-CONTESTANT" in n for n in h3["h3_contestant_zero"]["notes"]),
                  "re-review: an E-COMB CONTESTANT certificate is also subject to the combiner check")
            u20b = got["experiment_results/f20b_duplicate_order2.db"][1][0]
            check(u20b["klass"] == "UNCERTIFIABLE" and u20b["counts"]["duplicate_keys"] == 1, "re-review: a duplicate under ORDER 2 only is detected and refused")
            real_rj = next(n for n in ast.parse(open(os.path.join(HERE, "rejudge_grok.py"), encoding="utf-8").read()).body
                           if isinstance(n, ast.FunctionDef) and n.name == "combine_orders")
            nomsg = [l for l in lines if "AST-" + "equivalent" in l]
            check(not nomsg and "AST-" + "equivalent" not in json.dumps({k: v[1][0].get("combiner_check") for k, v in got.items()}, default=str),
                  "no combiner result anywhere reads AST-" + "equivalent (the arm is withdrawn; V-C2 holds by construction)")
            check(combiner_ok(real_rj) == (True, "AST-identical to rejudge_grok.combine_orders"),
                  "REF_COMBINE_ORDERS is AST-identical to the tree's rejudge_grok.combine_orders")
            u17 = got["experiment_results/f17_order1_drift.db"][1][0]
            check(u17["klass"] == "MIXED" and u17["counts"]["contradict_order1"] == ["1"] and any("ORDER-1 CONTRADICTION" in n for n in u17["notes"]),
                  "ONE order-1 row mis-stored refuses the table: MIXED, row id %s listed (B1)" % u17["counts"]["contradict_order1"])
            ua1 = got["experiment_results/a1_order1_transposed.db"][1][0]
            check(ua1["klass"] == "MIXED" and ua1["counts"]["order1_agree"] == 0,
                  "A1 writer transposed ORDER 1: MIXED (order 1 agrees on %d of %d)" % (ua1["counts"]["order1_agree"], ua1["counts"]["order1_informative"]))
            ua4 = got["experiment_results/a4_rawonly_untransposed.db"][1][0]
            check(ua4["klass"] == "MIXED" and any("RAW-ONLY" in n for n in ua4["notes"]), "A4 raw-only with an untransposing combiner: MIXED, never CONTESTANT (B2)")
            qa4 = os.path.join(tmp, "experiment_results", "a4_rawonly_untransposed.db"); ca4 = open_ro(qa4); ra4 = False
            try: unit_votes(ca4, qa4, dict(ua4, klass="CERTIFIED-CONTESTANT"))
            except SystemExit as e: ra4 = "never transposed" in str(e)
            finally: ca4.close()
            check(ra4, "B2, reader side: votes re-parsed from raw text are NEVER transposed, even for a unit a certificate JSON labels CONTESTANT")
            check(got["experiment_results/a6c_long_swapped.db"][0] == "MIXED" and got["experiment_results/x12c/arena13.db"][0] == "MIXED",
                  "A6c LONG fwd/rev labels swapped and A7 arena13 arm labels swapped: both MIXED (order 1 refutes)")
            u18 = got["experiment_results/f18_long_contestant.db"][1]
            v18 = [u for u in u18 if u["table"] == "verdicts"][0]
            q18 = os.path.join(tmp, "experiment_results", "f18_long_contestant.db"); c18 = open_ro(q18)
            r18 = sorted((r["key"], r["p1"], r["p2"]) for r in unit_votes(c18, q18, v18)[0] if r["p1"] != "INVALID"); c18.close()
            check(v18["klass"] == "CERTIFIED-CONTESTANT" and r18 == sorted((i, p1, p2) for i, (p1, p2) in enumerate(V) if p1 != "INVALID"),
                  "LONG fwd/rev stored contestant-labelled: CERTIFIED-CONTESTANT and the reader returns the true positional votes")
            u19 = got["experiment_results/f19_kotlin_two_judges.db"][1][0]
            q19 = os.path.join(tmp, "experiment_results", "f19_kotlin_two_judges.db"); c19 = open_ro(q19)
            r19, n19 = unit_votes(c19, q19, u19); c19.close()
            cross = [r for r in r19 if r["row"].get("judge_model") != r["row"].get("_o2_judge_model")]
            check("judge_model" in u19["match_key_rule"] and len(r19) == 20 and not cross and u19["pairing"]["duplicate_keys"] == 0
                  and u19["pairing"]["single_order_keys"] == 20,
                  "Kotlin two judges (H2): key %s; 20 same-judge pairs, 0 cross-judge pairs, 0 duplicates, 20 single-order keys (%s)"
                  % (u19["match_key_rule"], u19["pairing"]))
            u20 = got["experiment_results/f20_duplicate.db"][1][0]
            check(u20["klass"] == "UNCERTIFIABLE" and u20["counts"]["duplicate_keys"] == 1 and any("DUPLICATE" in n for n in u20["notes"]),
                  "a match key with two rows under one order value REFUSES the table (duplicate count 1 printed)")
            check(classify(0, 0, 4, 4, 4) == "AMBIGUOUS" and classify(2, 1, 4, 4, 0) == "MIXED" and classify(2, 2, 0, 0, 0) == "AMBIGUOUS"
                  and classify(2, 2, 4, 4, 0) == "CERTIFIED-POSITIONAL" and classify(2, 2, 4, 0, 4) == "CERTIFIED-CONTESTANT" and classify(2, 2, 4, 3, 1) == "MIXED",
                  "classify() contract on every state, including both hypotheses on 100% (AMBIGUOUS, never certified) and an order-1 contradiction (MIXED)")
            ub = uncert_breakdown([dict(klass=k, units=u) for k, u in got.values() if k != NDO])
            ubt = " ".join(ub[3])
            check(ub[1].get("R1", 0) >= 1 and ub[1].get("R2", 0) >= 1 and ub[1].get("R3", 0) >= 1 and ub[1].get("R4", 0) >= 1 and ub[2] >= 1
                  and "(3) E-COMB, call-site argument not verified 15" in ubt and ub[2] == 2 and "of which pin timing 2" in ubt and "P4 is carried by" in ubt,
                  "D7: P4 printed BY REASON on the fixture tree: %s" % ubt[:230])
            ub5 = uncert_breakdown([dict(klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", uncert_reason="R5")]),
                                    dict(klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", uncert_reason="R6")])])
            ub5t = " | ".join(ub5[3])
            check(ub5[1] == {"R5": 1, "R6": 1} and "(5) a pair outside the registered pairs 1" in ub5t
                  and "(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 1" in ub5t
                  and "P4 reason (6) R6" in ub5t and "not by frame (R-5)" in ub5t and "OUTSIDE" not in ub5t and "RX" not in ub5t,
                  "D7 / R-1 / R-5: reasons (5) and (6) print; R6 on its own line; the retired out-of-five line and 'RX' never print: %s" % ub5t[-260:])
            ub0 = uncert_breakdown([dict(klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", uncert_reason="R1")])])
            ub0t = " | ".join(ub0[3])
            check("(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 0" in ub0t and "P4 reason (6) R6" not in ub0t,
                  "R-1: P4 is printed under SIX reasons even at R6 = 0, and the R6 own line appears only when R6 > 0")
            # ── VFC-RX-RULING (f1e9e68) R-1..R-9, fixtures (a)-(f) ──
            check(UNCERT_REASONS[5] == ("R6", "stored labels unresolvable (a name-profile gap: instrument knowledge, not frame)") and len(UNCERT_REASONS) == 6
                  and UNCERT_CODES == ("R1", "R2", "R3", "R4", "R5", "R6") and not any("RX" in k or "outside the five" in lab or "OTHER" in lab for k, lab in UNCERT_REASONS),
                  "R-1: R6 is the SIXTH registered reason with the ruling's label; 'RX' and the out-of-five label are retired")
            ua = got["experiment_results/rx_a/arena13.db"][1][0]
            check(ua["klass"] == "UNCERTIFIABLE" and ua.get("uncert_reason") == "R6" and ua.get("resolved_klass") == "CERTIFIED-CONTESTANT"
                  and ua["counts"]["unresolvable_labels"] == 3 and ua["counts"]["order2_informative"] > 0 and ua["label_space"] == "unresolved"
                  and any(n.startswith("R6 stored labels unresolvable: 3 unresolvable") and "DESCRIPTIVE, decides nothing" in n for n in ua["notes"]),
                  "(a) R-2: LONG name-labelled, 3 of %d paired labels unresolvable, the resolved subset CERTIFIED-CONTESTANT on %d order-2 rows -> "
                  "UNCERTIFIABLE (R6), NOT certified on the subset; label_space 'unresolved' (R-9)" % (ua["counts"]["rows"], ua["counts"]["order2_informative"]))
            ub_ = got["experiment_results/rx_b/arena13.db"][1][0]
            check(ub_["klass"] == "MIXED" and ub_.get("uncert_reason") is None and ub_["counts"]["unresolvable_labels"] == 3
                  and ub_["counts"]["order1_agree"] == ub_["counts"]["order1_informative"] - 1 and any("ORDER-1 CONTRADICTION" in n for n in ub_["notes"]),
                  "(b) R-3: the same with ONE resolved order-1 contradiction -> MIXED (frame evidence), not R6; the 3 unresolvable labels do not cancel it")
            uc_ = got["experiment_results/ecomb_r6.db"][1][0]
            check(uc_["klass"] == "UNCERTIFIABLE" and uc_.get("uncert_reason") == "R6" and uc_["evidence"] == "E-COMB" and uc_["counts"]["unresolvable_labels"] == 1
                  and uc_.get("resolved_klass") == "CERTIFIED-POSITIONAL" and "combiner_check" not in uc_ and uc_["label_space"] == "unresolved",
                  "(c) R-2: a WIDE E-COMB primary with ONE unresolvable combined label -> UNCERTIFIABLE (R6) (resolved subset POSITIONAL, descriptive; "
                  "decided before the combiner check)")
            ucm = got["experiment_results/ecomb_r6_mixed.db"][1][0]
            check(ucm["klass"] == "MIXED" and ucm.get("uncert_reason") is None and ucm["counts"]["unresolvable_labels"] == 1,
                  "(c) R-3 on E-COMB: an unresolvable label beside a resolved row that contradicts both hypotheses -> MIXED, not R6")
            uc2 = got["experiment_results/rawonly_r6.db"][1][0]
            check(uc2["klass"] == "UNCERTIFIABLE" and uc2.get("uncert_reason") == "R6" and uc2["evidence"] == "E-COMB(re-parsed raw)" and uc2["counts"]["unresolvable_labels"] == 1,
                  "(c) R-2: a raw-only E-COMB table with ONE unresolvable combined name -> UNCERTIFIABLE (R6)")
            uc3 = got["experiment_results/rawonly_b2_r6.db"][1][0]
            check(uc3["klass"] == "MIXED" and uc3.get("uncert_reason") is None and any("RAW-ONLY" in n for n in uc3["notes"]),
                  "(c) R-3: a raw-only table whose resolved rows fail B2 (untransposed combine) is MIXED even with an unresolvable label")
            SD = lambda u: defaultdict(lambda: -1, u.get("secondary") or {})     # R2-L1 (f387d58): a missing key fails the check BY NAME, never a KeyError
            ud_ = got["experiment_results/rx_d_conflict.db"][1][0]; sdc = SD(ud_)
            check(ud_["klass"] == "MIXED" and ud_["evidence"] == "E-RAW" and sdc["klass"] == "UNCERTIFIABLE" and sdc["uncert_reason"] == "R6"
                  and sdc["resolved_klass"] == "CERTIFIED-CONTESTANT" and any("EVIDENCE CONFLICT" in n and "R-6: the power to downgrade" in n for n in ud_["notes"]),
                  "(d) R-6: a WIDE secondary whose RESOLVED subset certifies the OTHER frame still downgrades the unit to MIXED: %s"
                  % [n for n in ud_["notes"] if "CONFLICT" in n][:1])
            ud2 = got["experiment_results/rx_d_secondary.db"][1][0]; sd2 = SD(ud2)
            check(ud2["klass"] == "CERTIFIED-POSITIONAL" and sd2["klass"] == "UNCERTIFIABLE" and sd2["uncert_reason"] == "R6" and sd2["resolved"] == (sd2["counts"] if sd2["counts"] != -1 else {}).get("order2_informative")
                  and sd2["informative"] == sd2["resolved"] + 2 and not any("CONFLICT" in n or "WARNING" in n for n in ud2["notes"]),
                  "(d) R-6: a WIDE secondary with 2 unresolvable labels agreeing on its resolved subset: primary CERTIFIED-POSITIONAL by E-RAW, the secondary "
                  "UNCERTIFIABLE (R6), %d resolved of %d informative, never CERTIFIED" % (sd2["resolved"], sd2["informative"]))
            ua1 = got["experiment_results/rx_a1/arena13.db"][1][0]
            check(ua1["klass"] == "UNCERTIFIABLE" and ua1.get("uncert_reason") == "R6" and ua1["counts"]["unresolvable_labels"] == 1
                  and ua1.get("resolved_klass") == "CERTIFIED-CONTESTANT" and ua1.get("unresolvable_values") == [["stranger", 1]]
                  and any("order-1 informative %d, order-2 informative %d" % (ua1["counts"]["order1_informative"], ua1["counts"]["order2_informative"]) in n
                          for n in ua1["notes"]),
                  "(a1) F3: EXACTLY ONE unresolvable label, on ORDER 1, the resolved rows consistent -> UNCERTIFIABLE (R6); the resolved counts per order (F7)")
            uct = got["experiment_results/ecomb_r6_tie.db"][1][0]
            check(uct["klass"] == "UNCERTIFIABLE" and uct.get("uncert_reason") == "R6" and uct["counts"]["unresolvable_labels"] == 1
                  and uct.get("resolved_klass") == "CERTIFIED-POSITIONAL",
                  "(c-tie) F1: an E-COMB primary whose ONE unresolvable combined label sits on a TIE-vote row -> UNCERTIFIABLE (R6), unresolvable 1 "
                  "(counted before the decisive-vote gate)")
            uca = got["experiment_results/ecomb_r6_amb.db"][1][0]
            check(uca["klass"] == "UNCERTIFIABLE" and uca.get("uncert_reason") == "R6" and uca.get("resolved_klass") == "AMBIGUOUS"
                  and "combiner_check_descriptive" not in uca,
                  "(c-amb) F4: E-COMB with every decisive label unresolvable: the resolved subset is AMBIGUOUS -> R6, not AMBIGUOUS")
            ucx = got["experiment_results/ecomb_r6_tampered.db"][1][0]; ccx = ucx.get("combiner_check_descriptive") or {}
            ucd = uc_.get("combiner_check_descriptive") or {}
            check(ucx["klass"] == "UNCERTIFIABLE" and ucx.get("uncert_reason") == "R6" and ccx.get("ok") is False
                  and any(n.startswith("H3 on the R6 unit (DESCRIPTIVE") and "combiner FAIL" in n for n in ucx["notes"])
                  and ucd.get("ok") is True and ucd.get("callsite_ok") is True and "combiner_check" not in ucx,
                  "(c-tampered) F6: H3 runs DESCRIPTIVELY on an R6 E-COMB unit (a tampered writer prints FAIL, the clean one PASS); the class stays R6")
            udt = got["experiment_results/rx_d_tie.db"][1][0]; sdt = SD(udt)
            check(udt["klass"] == "CERTIFIED-POSITIONAL" and sdt["klass"] == "UNCERTIFIABLE" and sdt["uncert_reason"] == "R6"
                  and (sdt["counts"] if sdt["counts"] != -1 else {}).get("unresolvable_labels") == 1 and sdt["informative"] == sdt["resolved"] == (sdt["counts"] if sdt["counts"] != -1 else {}).get("order2_informative"),
                  "(d-tie) F1: a WIDE secondary whose only unresolvable label is on a TIE-vote row is UNCERTIFIABLE (R6), secondary, %d resolved of %d "
                  "informative (the TIE row is not informative)" % (sdt["resolved"], sdt["informative"]))
            udw = got["experiment_results/rx_d_warning.db"][1][0]
            check(udw["klass"] == "CERTIFIED-POSITIONAL" and SD(udw)["uncert_reason"] == "R6" and SD(udw)["resolved_klass"] == "MIXED"
                  and any(n.startswith("WARNING: the stored combined column") for n in udw["notes"]),
                  "(d-warning) F4 / R-6: an R6 secondary whose RESOLVED subset is MIXED keeps the WARNING")
            ub6 = uncert_breakdown([dict(klass="CERTIFIED-POSITIONAL", units=[ud2])])
            check(ub6[0] == 0 and not ub6[1], "R-6: the R6 secondary never enters uncert_breakdown or P4")
            # (e) R-7: an UNCERTIFIABLE unit with no code REFUSES (uncert_breakdown, require_reason_codes over every unit and secondary, and run())
            r7_exc = []
            def refuses(fn):        # F2 (a3da968): any other exception is a NAMED failure of the check, with its text, never a crash
                try: fn()
                except SystemExit as e: return "[R-7] REFUSED" in str(e)
                except Exception as e: r7_exc.append(repr(e)[:120]); return False
                return False
            xr7 = lambda: (" [NOT a [R-7] refusal: %s]" % r7_exc[-1]) if r7_exc else ""
            check(refuses(lambda: uncert_breakdown([dict(klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", table="t")])])),
                  "(e) R-7: uncert_breakdown REFUSES an UNCERTIFIABLE unit with no reason code (no default)" + xr7())
            check(refuses(lambda: uncert_breakdown([dict(klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", uncert_reason="RX", table="t")])])),
                  "(e) R-7: a code outside the six registered (the retired 'RX') REFUSES" + xr7())
            check(refuses(lambda: require_reason_codes([dict(path="p", klass="CERTIFIED-POSITIONAL", units=[dict(klass="CERTIFIED-POSITIONAL", table="a"),
                                                                                                            dict(klass="UNCERTIFIABLE", table="b")])])),
                  "(e) R-7: an UNCERTIFIABLE unit without a code inside a CERTIFIED cache REFUSES (every unit is checked, not only P4's caches)" + xr7())
            check(refuses(lambda: require_reason_codes([dict(path="p", klass="CERTIFIED-POSITIONAL", units=[dict(klass="CERTIFIED-POSITIONAL", table="a",
                                                                                                            secondary=dict(klass="UNCERTIFIABLE"))])])),
                  "(e) R-7: an UNCERTIFIABLE secondary without a code REFUSES" + xr7())
            check(require_reason_codes([dict(path="p", klass="UNCERTIFIABLE", units=[dict(klass="UNCERTIFIABLE", uncert_reason=k)]) for k in UNCERT_CODES]) is None,
                  "(e) R-7: every registered code R1-R6 is admitted")
            real_ct = globals()["certify_table"]; e_txt = os.path.join(tmp, "r7_refused.txt"); e_json = os.path.join(tmp, "r7_refused.json")
            def ct_nocode(*a, **k):
                u = real_ct(*a, **k); u.pop("uncert_reason", None); return u
            globals()["certify_table"] = ct_nocode
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    r7 = refuses(lambda: run(None, root=tmp, selftest_ok=True, out_txt=e_txt, out_json=e_json, comb_ctx=cctx))
            finally:
                globals()["certify_table"] = real_ct
            check(r7 and not os.path.exists(e_txt) and not os.path.exists(e_json),
                  "(e) R-7: run() on the fixture tree with the reason codes stripped REFUSES before anything is written" + xr7())
            def ct_nocode2(*a, **k):      # only the SECONDARY's code: its cache is CERTIFIED, so uncert_breakdown never sees it; run() must
                u = real_ct(*a, **k)
                if u.get("secondary"): u["secondary"].pop("uncert_reason", None)
                return u
            globals()["certify_table"] = ct_nocode2
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    r7b = refuses(lambda: run(None, root=tmp, selftest_ok=True, out_txt=e_txt, out_json=e_json, comb_ctx=cctx))
            finally:
                globals()["certify_table"] = real_ct
            check(r7b and not os.path.exists(e_txt) and not os.path.exists(e_json),
                  "(e) R-7: run() REFUSES an R6 secondary stripped of its code inside a CERTIFIED cache (the check covers every unit and secondary)" + xr7())
            # (f) R-8: unit_votes on a CERTIFIED unit whose name constant drifted after the certificate REFUSES, naming the unit and the first key
            q9f = os.path.join(tmp, "experiment_results", "x12", "arena13.db"); c9f = open_ro(q9f)
            v9f = [u for u in got["experiment_results/x12/arena13.db"][1] if u["table"] == "verdicts"][0]
            ok_f = len(unit_votes(c9f, q9f, v9f, cctx["name_content"])[0]) == len(V)
            real_sc = globals()["source_constant"]; msg_f = ""
            globals()["source_constant"] = lambda script, name: "PERTURBED-" + real_sc(script, name)
            try: unit_votes(c9f, q9f, v9f, cctx["name_content"])
            except SystemExit as e: msg_f = str(e)
            finally:
                globals()["source_constant"] = real_sc; c9f.close()
            check(ok_f and "[FRAME] REFUSED (R-8)" in msg_f and "experiment_results/x12/arena13.db:verdicts" in msg_f and "key 0" in msg_f,
                  "(f) R-8: the certified name-labelled unit reads %d matches; with arena13.NEW perturbed the reader REFUSES on the first key: %s"
                  % (len(V), msg_f[:120]))
            # D1 / D2 / D3 / D4 (review 9d3e261)
            inst = d2_installed_name()
            ui = got.get("experiment_results/d2_installed.db", (None, [{}]))[1][0]
            check(inst is not None and ui.get("klass") == "CERTIFIED-POSITIONAL",
                  "D2: an import of an installed distribution (%s) is skipped (stated limit), not a finding: the writer certifies" % inst)
            li = local_import_names(ast.parse("import tools.analysis.a\nfrom tools.analysis import b, c\nfrom tools.analysis.d import x\nimport tools\n"
                                              "from tools import analysis\nimport os.path\nfrom . import e\n"))
            check([m for m, _ in li] == ["a", "b", "c", "d", BAD_PKG, BAD_PKG, "os", None],
                  "D2: package paths rooted at tools resolve to the module under tools/analysis; other tools forms are BAD_PKG; relative is None")
            npc = hashlib.sha256(json.dumps(NAME_PROFILE_CONTENT, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            check(npc == NAME_PROFILE_CONTENT_SHA256, "D4: NAME_PROFILE_CONTENT is pinned by its canonical sha256 %s" % npc[:16])
            check(len(CLASSES) == 6 and CLASSES[-1] == NDO and cache_class([dict(klass=NDO)]) == NDO, "SIX classes; an all-single-order cache is NOT-DUAL-ORDER")
            f3 = {u["table"]: u for u in got["experiment_results/sub/f3_long_arm.db"][1]}
            check(set(f3) == {"verdicts", "probe"} and f3["verdicts"]["counts"]["stored_invalid_on_decisive_parse"] == 1,
                  "long bfcl-like frame: two tables certified separately; the unusable-finish row is counted, not a contradiction")
            v9 = [u for u in got["experiment_results/x12/arena13.db"][1] if u["table"] == "verdicts"][0]
            check(v9["pair"] == ["ensemble", "reversed"] and v9["unpaired"] == {"selfref": 60} and v9["label_space"] == "names",
                  "arena13-like: pair (ensemble, reversed), selfref unpaired and excluded, names resolved via %s" % v9["names_desc"])
            # the reader: the positional and the transposed fixture give the SAME positional votes; withholding the transposition changes them
            p1_, p2_ = os.path.join(tmp, "experiment_results", "f1_wide_positional.db"), os.path.join(tmp, "experiment_results", "f2_wide_transposed.db")
            con1, con2 = open_ro(p1_), open_ro(p2_)
            u1 = got["experiment_results/f1_wide_positional.db"][1][0]; u2 = got["experiment_results/f2_wide_transposed.db"][1][0]
            a = [(r["p1"], r["p2"]) for r in unit_votes(con1, p1_, u1)[0]]
            b = [(r["p1"], r["p2"]) for r in unit_votes(con2, p2_, u2)[0]]
            withheld = [(r["p1"], r["p2"]) for r in unit_votes(con2, p2_, dict(u2, klass="CERTIFIED-POSITIONAL"))[0]]
            check(a == b == V and withheld != a, "reader: positional and transposed caches both return the TRUE positional votes once the certificate's "
                  "transposition is applied; withheld, they do not")
            q9, q9b = os.path.join(tmp, "experiment_results", "x12", "arena13.db"), os.path.join(tmp, "experiment_results", "x12b", "arena13.db")
            c9, c9b = open_ro(q9), open_ro(q9b)
            v9b = [u for u in got["experiment_results/x12b/arena13.db"][1] if u["table"] == "verdicts"][0]
            truth = sorted((i, p1, p2) for i, (p1, p2) in enumerate(V) if p1 != "INVALID")
            r9 = sorted((r["key"], r["p1"], r["p2"]) for r in unit_votes(c9, q9, v9)[0] if r["p1"] != "INVALID")
            r9b = sorted((r["key"], r["p1"], r["p2"]) for r in unit_votes(c9b, q9b, v9b)[0] if r["p1"] != "INVALID")
            check(r9 == truth and r9b == truth, "reader on name-labelled frames: the contestant-labelled and the sign-bug frame both return the true positional votes")
            refused = False
            try: unit_votes(con1, p1_, dict(u1, klass="MIXED"))
            except SystemExit as e: refused = "[FRAME]" in str(e) and "only a CERTIFIED unit is read" in str(e)
            check(refused, "reader REFUSES a unit that is not CERTIFIED ([FRAME] message matched)")
            for c in (con1, con2, c9, c9b): c.close()
            # every criterion and prediction branch
            crit, v = score_criteria(3, ["a", "b", "c"], ["a", "b", "c"], True, True, [])
            check(v == "HELD" and [r for _, r, _ in crit] == ["HELD"] * 4, "E1-E4 HELD branch: " + " | ".join(l for _, _, l in crit))
            crit, v = score_criteria(3, ["a", "b"], ["a", "b", "c"], False, False, ["a"])
            check(v == "FAILED" and [r for _, r, _ in crit] == ["FAILED"] * 4, "E1-E4 FAILED branch: " + " | ".join(l for _, _, l in crit))
            check("SIX classes" in score_criteria(1, ["a"], ["a"], True, True, [])[0][1][2], "E2 HELD line names the SIX classes")
            crit, v = score_criteria(3, None, ["a"], True, True, [])
            check(crit[0][1] == "FAILED" and v == "FAILED", "E1 FAILED without an independent listing: " + crit[0][2])
            pos_units = lambda long: [dict(table="verdicts", kind="LONG" if long else "WIDE", pair=["fwd", "rev"], klass="CERTIFIED-POSITIONAL",
                                           counts=dict(order1_agree=5, order1_informative=5))]
            named_ok = {p: ("CERTIFIED-POSITIONAL", pos_units(lg)) for p, lg in P5_NAMED}
            cls_ok = {"c%d" % i: "CERTIFIED-POSITIONAL" for i in range(38)}; cls_ok.update({"u1": "UNCERTIFIABLE", "u2": "AMBIGUOUS"})
            cls_ok.update({"n%d" % i: NDO for i in range(30)})     # 30 NOT-DUAL-ORDER caches: outside every denominator
            P = score_predictions(cls_ok, named_ok)
            check([r for _, r, _ in P] == ["HELD"] * 5 and "raw enumeration 70, NOT-DUAL-ORDER 30" in P[0][2] and "38 of 40 dual-order" in P[1][2],
                  "P1-P5 HELD branch, P1-P4 over the 40 dual-order caches (70 raw, 30 NOT-DUAL-ORDER beside): " + " | ".join(l for _, _, l in P))
            P4n = score_predictions({"c1": "CERTIFIED-POSITIONAL", "n1": NDO, "n2": NDO}, named_ok)[3]
            check(P4n[1] == "FAILED", "P4: NOT-DUAL-ORDER caches never satisfy P4 (" + P4n[2] + ")")
            named_bad = dict(named_ok); named_bad[P5_NAMED[0][0]] = ("CERTIFIED-POSITIONAL", pos_units(False))
            P = score_predictions({"c1": "MIXED", "c2": "CERTIFIED-CONTESTANT"}, named_bad)
            check([r for _, r, _ in P] == ["FAILED"] * 5, "P1-P5 FAILED branch: " + " | ".join(l for _, _, l in P))
            # the full run on the fixture tree: outputs written once; a second run REFUSED
            steward = os.path.join(tmp, "steward.txt")
            with open(steward, "w") as f: f.write("# independent listing\n" + "\n".join(sorted(exp)) + "\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                doc = run(steward, root=tmp, selftest_ok=True, comb_ctx=cctx)
            check(doc["certificate"] == "HELD" and all(v["result"] == "HELD" for v in doc["criteria"].values()),
                  "full run on the fixture tree: certificate %s, %s" % (doc["certificate"], {k: v["result"] for k, v in doc["criteria"].items()}))
            txt = open(os.path.join(tmp, "experiment_results", "vote_frame_cert.txt"), encoding="utf-8").read()
            check(all(("%s HELD" % e) in txt for e in ("E1", "E2", "E3", "E4")) and "CERTIFICATE: HELD" in txt and all(("P%d " % i) in txt for i in range(1, 6)),
                  "the outcome text carries E1-E4, the certificate line and P1-P5")
            tl = txt.splitlines(); i_d2 = next((i for i, l in enumerate(tl) if l.startswith("  experiment_results/rx_d_secondary.db ->")), None)
            j_d2 = next((j for j in range(i_d2 + 1, len(tl)) if tl[j].startswith("  experiment_results/") or not tl[j].startswith("      ")), len(tl)) \
                if i_d2 is not None else 0          # the block of this cache only (the next cache's lines are not read)
            sec = [l for l in tl[i_d2:j_d2] if l.strip().startswith("secondary ")] if i_d2 is not None else []
            check(len(sec) == 1 and "secondary E-COMB: UNCERTIFIABLE (R6), secondary, %d resolved of %d informative" % (sd2["resolved"], sd2["informative"]) in sec[0]
                  and "CERTIFIED" not in sec[0] and "CERTIFIED-POSITIONAL" in tl[i_d2],
                  "(d) R-6 PRINTED: the R6 secondary line reads 'UNCERTIFIABLE (R6), secondary, n resolved of m informative' and never CERTIFIED: %s"
                  % (sec[0].strip()[:150] if sec else "(absent)"))
            check(all("OUTSIDE the five" not in l and "P4 by reason" not in l or "(6) stored labels unresolvable" in l for l in tl)
                  and any(l.startswith("P4 reason (6) R6") for l in tl) and not any("\"RX\"" in l or "(RX)" in l for l in tl),
                  "R-1 / R-5 PRINTED: the P4-by-reason line carries six reasons, R6 has its own line, the out-of-five line is gone")
            again = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): run(steward, root=tmp, selftest_ok=True, comb_ctx=cctx)
            except SystemExit as e:
                again = "WRITE-ONCE" in str(e)
            check(again, "a second --run is REFUSED (write-once outputs)")
            after = {p: stat_of(p) for p in files}
            check(all(after[p] == stats0[p] for p in files), "no fixture changed size or mtime across the census (the E4 mechanism)")
            dry = io.StringIO()
            with contextlib.redirect_stdout(dry): rc = dry_run(root=tmp)
            check(rc == 0 and "ENUMERATION:" in dry.getvalue() and "CERTIFICATE" not in dry.getvalue(), "--dry-run prints the enumeration, certifies nothing, rc 0")
            trapped = False
            try: sqlite3.connect(os.path.join(ROOT, "ratings.db"))
            except AssertionError: trapped = True
            check(trapped, "the connect trap refuses a path outside the temp dir (no DB of record can be opened by the selftest)")
            real_uri = globals()["ro_uri"]; refused_ro = False
            globals()["ro_uri"] = lambda path: "file:%s?mode=rw" % os.path.abspath(path).replace("\\", "/")
            try: open_ro(os.path.join(tmp, "experiment_results", "f1_wide_positional.db"))
            except SystemExit as e: refused_ro = "[RO] REFUSED" in str(e)
            finally: globals()["ro_uri"] = real_uri
            check(refused_ro, "open_ro REFUSES a URI without mode=ro&immutable=1 by an explicit raise (M1)")
            n_assert = {f: sum(isinstance(nd, ast.Assert) for nd in ast.walk(ast.parse(open(os.path.join(HERE, f), encoding="utf-8").read())))
                        for f in ("vote_frame_cert.py", "tie_mechanics.py", "position_index_all.py")}
            check(not any(n_assert.values()), "no `assert` statement in the three instruments (every guard survives python -O): %s" % n_assert)
            cli_refused = False
            try: require_steward(argparse.Namespace(steward_list=None))
            except SystemExit as e: cli_refused = "[E1]" in str(e)
            check(cli_refused and require_steward(argparse.Namespace(steward_list="x")) is None, "--run without --steward-list is REFUSED (E1); with one it proceeds")
    except (Exception, SystemExit) as e:      # a refusal inside the selftest is a FAIL line, not an abort
        import traceback
        lines.append("  [FAIL] exception: %r\n%s" % (e, traceback.format_exc())); ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not quiet or not ok:
        print("=== %s --selftest (synthetic caches under tempfile.mkdtemp(); no DB of record) ===" % TEST)
        print("\n".join(lines))
        print("SELFTEST %s: %d checks, %d failed" % ("PASS" if ok else "FAIL", len(lines), sum(1 for l in lines if "[FAIL]" in l)))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="VOTE-FRAME-CERT (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--steward-list", default=None, help="the data-steward's independent listing (required with --run)")
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.dry_run: sys.exit(dry_run())
    require_steward(a)
    doc = run(a.steward_list)
    sys.exit(0 if doc["certificate"] == "HELD" else 2)
