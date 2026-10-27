# READY re-review: VOTE-FRAME-CERT, TIE-MECHANICS, POSITION-INDEX-ALL (adversarial reviewer, 2026-09-23, zero calls)

Code reviewed: branch `vote-frame-instruments`, HEAD `84ab7e3` (parent `d237e56`), worktree `.claude/worktrees/vote-frame-instruments`, clean
(`git status --short | wc -l` = 0). The commit touches exactly the three scripts (`git show --name-only --format= 84ab7e3 | wc -l` = 3).
Reviewed against: the prior review `docs/reviews/NOT_READY_vote_frame_family.md` (14edeb4; B1, B2, H1-H3, M1-M3, T-C1, T-C2), the H3 ruling
(0104e44, programme section "Registrar's ruling 2026-09-23 ... review finding H3"), the registrations VOTE-FRAME-CERT L13032-L13109,
POSITION-INDEX-ALL L13111-L13227, TIE-MECHANICS L12911-L13030 and the rulings L13691-L13746 of `docs/judge_v2_program.md`.
Every selftest and fixture ran on an LF export of 84ab7e3 (`git -c core.autocrlf=false archive`) under the predecessor's audit hook
(`guard.py`: raises on any `.db` open or `sqlite3.connect` outside temp/scratch). DBs of record were opened ONLY through `vfc.open_ro`
(`mode=ro&immutable=1`, `PRAGMA query_only` read back) or an equivalent `mode=ro&immutable=1` URI, after checking that no non-empty `-wal`
sits beside them; size, mtime_ns and sha256_16 were taken before and after (all unchanged). No judge call, no `--dry-run`, no `--run`.
Scratch: `<session scratchpad>/vote_frame_rr/` (tree*, guard.py, h3_real.py, h3_adv.py, mutate_rr.py, schema_scan.py, long_dups.py,
kdups.py, indep_comb.py, rawonly_real.py, *.out).

## VERDICTS

| instrument | verdict |
|---|---|
| VOTE-FRAME-CERT (`vote_frame_cert.py`) | **READY-WITH-CONDITIONS** (V-C1..V-C3) |
| POSITION-INDEX-ALL (`position_index_all.py`) | **READY-WITH-CONDITIONS** (P-C1, P-C2) |
| TIE-MECHANICS (`tie_mechanics.py`) | **READY** (T-C1 and T-C2 of 14edeb4 discharged) |

## Pins this READY applies to (LF rendering is the rendering of record; working tree has 0 CRLF bytes in all three)

| file | blob: (`git hash-object`, = `git rev-parse 84ab7e3:<path>`) | sha256-lf16: | sha256-crlf16: (beside, not of record) |
|---|---|---|---|
| tools/analysis/vote_frame_cert.py | blob:384f26b75bfbf162f0d3efc0d0ecd381f66a344f | sha256-lf16:a426fddc03ce7601 | sha256-crlf16:3576b9d9ee003da5 |
| tools/analysis/tie_mechanics.py | blob:7f88d2ac581679aea33a2a25dc088883785fca86 | sha256-lf16:d6a1a0409a0fc06e | sha256-crlf16:4a18124878801487 |
| tools/analysis/position_index_all.py | blob:1e4fec8a35e230f93a365c5cbd256359b59dd4d7 | sha256-lf16:3efb4097d4c09d3d | sha256-crlf16:386580e5f6c50b41 |

Builder's pins (blob 384f26b75bfbf162 / 7f88d2ac581679ae / 1e4fec8a35e230f9; sha256-lf16 a426fddc03ce7601 / d6a1a0409a0fc06e / 3efb4097d4c09d3d):
all six agree to the digit. The gate a run-operator checks is **sha256-lf16** (the scripts print it as "script sha256[:16] of the LF bytes").

## Per-claim table

| # | builder's claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | pins | CONFIRMED | `git hash-object`, `sha256sum`, CRLF count = 0 | all six agree | - |
| 2 | selftests 118 / 29 / 42, 0 failed, normal and -O | CONFIRMED | `python [-O] guard.py <t>.py --selftest` on the LF export | 118/0, 29/0, 42/0 in both modes; audit: 215 / 28 / 57 connects, all under temp | - |
| 3 | B1: an order-1 contradiction is MIXED | CONFIRMED | classify() L488-L500 (`n1_agree != n1_inf -> MIXED`, before any order-2 branch); adv_frames.py A1 / A2 / A6c / A7 | A1 MIXED (0/100 order-1 agree), A2 MIXED (row 3 listed), A6c MIXED (110/110 contradicted), A7 MIXED; order1_endtoend.py: bad_order1.db MIXED, not entered (the script's KeyError is the fixture's absence from the index, i.e. the fix) | - |
| 4 | B2: raw-only tables never CONTESTANT, never transposed | CONFIRMED | certify_table L710-L716, unit_votes L806-L808; A4 | A4 MIXED with the RAW-ONLY note; reader refuses a raw-only unit labelled CONTESTANT | - |
| 5 | H1: BFCL never counts toward C2, two layers | CONFIRMED | support_of L330-L336, c2_verdict L404; c2paths.py | BFCL s=1 at n 57 / 58 / 60: UNSUPPORTED ("ruling (3)"), the data reading printed beside; BFCL 57 FF / 1 SS: measured DEFF 0.97, MDE 0.181, UNSUPPORTED; C2 PRIMARY UNDETERMINED (MMLU-Pro alone). Mutants "support override removed" and "c2_verdict lets BFCL in" KILLED | - |
| 6 | H2: judge in the Kotlin key; duplicates UNCERTIFIABLE | CONFIRMED | long_key_fn L642-L645; L752-L760; kotlin_judges.py; F19 / F20 | two-judge fixture: 20 same-judge pairs, 0 cross-judge; F20 UNCERTIFIABLE, duplicate count 1 printed | - |
| 7 | H3: E-COMB-only certificate needs its combiner verified by AST at the writer's and rejudge_grok's run-time pins | CONFIRMED on the record; PARTLY in general | h3_real.py on the three real caches (below); h3_adv.py; mutate_rr.py | real caches: result exactly as the ruling specifies (table below). Generic matcher: 4 of 9 adversarial combiners FALSE-PASS, a call-site double transposition certifies the wrong frame, 7 of 8 new H3/H2 mutants SURVIVE the selftest (mutate_rr.py) | HIGH (D1, D2; not reachable on the record, V-C2) |
| 8 | M1: no asserts, checked by ast | CONFIRMED | `ast.walk` count of `ast.Assert` | 0 / 0 / 0 in the three files; 0 `__debug__` refs; open_ro L342-L348 explicit raises; selftest checks it | - |
| 9 | M2: pool branches executed through an injectable guard | CONFIRMED | PIA verify_pools L192-L213, selftest L802-L827; TIE gates L185-L203, selftest L603-L620; mutants | admit and refuse branches executed; p2035 recomputed over the copied id file and refused one id short; BFCL-without-p2035 refuses. Real BFCL cache run_meta carries `pool_id = p2035adddedd1becb` (read-only query), so the new refusal does not fire on the record. The REAL pool_guard.assert_pool_of_record is executed only at run time (the selftest injects a stub) | LOW (D6) |
| 10 | M3: survivors covered | CONFIRMED | mutate_review.py, hardened (kill only on a SELFTEST FAIL line) | 27 / 27 applied killed; 1 NOT APPLIED ("(pool_check path) pool guard removed": the line is now `(guard or pool_guard.assert_pool_of_record)(...)`; the builder's mutant "T-C2: TIE pool guard removed" covers it, KILLED) | - |
| 11 | builder mutation 39 / 39, hardened harness | CONFIRMED | re-ran mutate2.py on a separate LF copy | BASELINE printed and gated (`sys.exit` if any baseline rc != 0; baseline 118/29/42 PASS); a kill counts only if `"SELFTEST FAIL"` is in the last stdout line; 39 / 39 killed; originals restored byte-identical | - |
| 12 | predecessor's mutate_review 27 / 27, 1 NOT APPLIED | CONFIRMED | same, on its own LF copy | 27 / 27, 1 NOT APPLIED; with the kill rule hardened from `rc != 0` to "SELFTEST FAIL line" the count is unchanged (every kill line reads SELFTEST FAIL) | - |
| 13 | adv_frames: every A-fixture MIXED or 0.750 | CONFIRMED | adv_frames.py (VFR_WT = the LF export) | A0 0.750; A1 / A2 / A4 / A6c / A7 MIXED; A3 / A3b / A5 / A5b / A5c / A6 / A6b 0.750; N1 / N2 NOT-DUAL-ORDER; unit_votes refuses all six non-certified class strings | - |
| 14 | no registered criterion or denominator changed | CONFIRMED | `git diff -U0 d237e56 84ab7e3 -- tools/analysis/` deleted lines listed in full (45 lines, `grep -E "^-" | grep -vc "^---"`) | no bar, band, prediction value, falsifier, E1-E4 / P1-P5 / C1-C5 threshold, SUPPORT_MDE, DEFF or MDE formula deleted or changed; the semantic changes are B1 (restores the registered sentence), B2, H1 and H3 (rulings), H2 (key), and the duplicate refusal (a class extension NOT yet ruled: D4) | MEDIUM (D4) |
| 15 | TIE T-C1 / T-C2 | CONFIRMED | tie_mechanics L130 opens through vfc.open_ro; mutants "T-C2 pool guard removed" / "pass-1 sha refusal removed" KILLED; CFG_OF_RECORD cache1_sha256 = sha256 of the real canary_baseline_pass1.db | `sha256sum` 5142795bdc8c5a8e... = the pinned value (no -wal beside) | - |

## H3 on the real caches (read-only; `h3_real.py`, repo = main checkout)

No `-wal`/`-shm` beside any of the three (`ls rubric_*.db*`); stat and sha256_16 unchanged after the run.

| cache (sha256_16) | writer | first write (min verdicts.ts, UTC) | writer pin | rejudge_grok pin | combiner call | H3 result | class |
|---|---|---|---|---|---|---|---|
| rubric_ladder.db (4412f92306bed20b) | rubric_ladder.py | 1788820241 = 2026-09-07T22:30:40 | f03cb302dfb3 (2026-09-07T21:53:04Z), blob:d94831fc534e | fb8fb5bd2f1a, blob:939de7c7e31a | L307 rj.combine_orders, AST-identical | PASS | CERTIFIED-POSITIONAL (E-COMB 3812 / 3812 positional, 0 contestant) |
| rubric_swap.db (2173b4dfa52345bb) | rubric_swap.py | 1788780512 = 2026-09-07T11:28:31 | 3ebf4f4a6e39 (11:28:01Z), blob:82e2065f2f77 | fb8fb5bd2f1a | L187 rj.combine_orders, AST-identical | PASS | CERTIFIED-POSITIONAL (4006 / 4006, 0) |
| rubric_contrast.db (d929b53056000d27) | rubric_value_contrast.py | 1788699989 = 2026-09-06T13:06:29 | NONE: the script's only commit 7037035 is 13:07:16Z, 47 s AFTER the first row | - | - | FAIL "the writer's run-time blob cannot be pinned" | UNCERTIFIABLE (would have been CERTIFIED-POSITIONAL: 10478 / 10478, 0) |

Independent recomputation (`indep_comb.py`, own combine, own name mapping): 3812/0, 4006/0, 10478/0 informative positional/contestant: agree to the digit.
rubric_contrast: 16 of 11,124 rows precede commit 7037035 (`ts < 2026-09-06T13:07:16Z`); last row 15:50:33Z; the script has exactly one
commit ever and its HEAD blob is that commit's (blob:9e1541a7bdf1). All four scripts have one or two commits in all history (`git log --follow`),
so no blob changed between first and last write of any cache.

Data flow, read by the reviewer at the pinned blobs (the part the ruling's AST check does not see, D2): rubric_ladder.py f03cb30 L306-L309
`v2, _ = rj.parse_judge(raw2)` -> `rj.combine_orders(v1, v2)` -> row stores `v2` in vote2_raw; rubric_swap.py 3ebf4f4 L186-L189 identical;
rubric_value_contrast.py 7037035 L163-L168 `v2_raw, c2 = rj.parse_judge(raw2)` -> `rj.combine_orders(v1, v2_raw)` -> row stores `v2_raw`.
The stored order-2 vote is the positional parse and is exactly the value passed to combine_orders: POSITIONAL is the true frame of all three.
Other scripts referencing the three caches open them `mode=ro` (clean_subset_reanalysis, judge_solve_map, j6_rubrics, stack_judge,
free_tests_f*), so the WRITER attribution holds.

Population of the H3 path on the record (`schema_scan.py`, schema only, 184 SQLite files, 6 skipped for a non-empty -wal, all embedding /
text caches): E-COMB-only WIDE tables = **3**, exactly COMB_WRITER's three. Raw-only WIDE tables (the B2 path) = **1**, leaf_powered.db, which
is NOT-DUAL-ORDER (raw2 = '' on 2156 / 2156 rows: leaf_powered.py L105-L107 SINGLE branch). LONG dual-order tables: 16 (`long_dups.py`),
duplicate (key, order) groups = **0** on all 16, including kotlin_c0d3f708cbc3930e.db (18,246 rows, 9,123 dual keys = the Kotlin board of record).

## Rulings asked for

**(a) Duplicate-key table UNCERTIFIABLE (P4) rather than MIXED (P3): the builder's choice is the right one of the two, but it is an
unruled class extension (D4).** MIXED asserts row-level frame evidence ("neither hypothesis on 100%, the contradicting row ids listed")
and its registered consequence flags every consumer readout for re-read; a duplicate is a pairing defect, not a frame contradiction, and the
per-row E-RAW test does not even need the pairing. UNCERTIFIABLE ("cannot certify") is the honest class. But the registered UNCERTIFIABLE is
"neither raw text nor a combined column", and P4 ("at least 1 UNCERTIFIABLE") would count a pairing refusal. On the record the question is
moot: 0 duplicate groups on all 16 LONG dual-order tables. Registrar: record the extension by insertion (as for H3), and have P4 printed with its
UNCERTIFIABLE count broken down by reason (registered definition / H3 combiner not verified / duplicate key / pair outside the registered pairs).

**(b) leaf_powered-type raw-only tables fall under B2, not H3: CONFIRMED.** H3's ambiguity exists because the frame of STORED votes is
unknown, so the combined column cannot separate "contestant + correct combiner" from "positional + untransposing combiner". In a raw-only table
the combiner's inputs are re-parsed from raw text and are positional by construction; the 100% reproduction of combine_orders on those inputs
tests the combiner on known-frame data, and the index reads the re-parse, never the stored winner. A CONTESTANT result there can only mean a
combiner sign bug and is MIXED (B2). No source check is needed. On the record the path is empty (leaf_powered is NOT-DUAL-ORDER).

## Checks that can pass without checking (item 5)

- **Printed-not-compared (D3, PIA):** load_cert L162-L169 refuses a certificate that is not VOTE-FRAME-CERT HELD, but the certificate's
  `script_sha256_16_lf` is only PRINTED (L580, L607); a certificate written by any other vote_frame_cert build (e.g. the d237e56 build that
  certified order-1 transposition) would be read.
- **H3 "AST-equivalent" branch (D1):** passes a combiner on "one transposition dict whose .get is applied once to the second parameter"
  without checking that the transposed value is what is compared or returned (C4: computed and unused; C3: undone by an if-expression; C5:
  flip inverted; C9: winner = the raw order-2 vote): 4 FALSE-PASS of 9 (`h3_adv.out`). Unreachable on the record (all three real writers
  PASS by the AST-identical branch).
- **H3 sees the combiner, not the call (D2):** a writer that stores `v2c = T(parse2)` and calls `rj.combine_orders(v1, v2c)` is CERTIFIED-
  POSITIONAL with H3 PASS while its order-2 column is contestant-labelled (`h3_adv.out`, E2E callsite.db). This is the ruling's own
  "positional against a double-transposing combiner" case with the extra transposition moved to the call site; the ruling's (b) does not close
  it. Closed for the record by the source reading above.
- **Untested reject branches (mutate_rr.py, baseline-gated, kill only on SELFTEST FAIL): 1 of 8 applied vfc mutants killed.** SURVIVED:
  transposition accepted on ANY parameter; any two-key dict counted as a transposition; `any(oks)` instead of `all(oks)`; pin at the LAST write
  instead of the first; a CONTESTANT E-COMB certificate skipping the check; duplicates detected on order 1 only; a one-parameter combiner
  admitted. KILLED: a run_meta sha matching any commit. The "pin at the last write" survivor is OUTCOME-DETERMINING on the record: under it,
  rubric_contrast would pin 7037035 and PASS. The code implements the ruling (first write; L270-L271, and the real evidence line reads
  "first write min(verdicts.ts)"), but no selftest locks that choice.
- Weak selftest refusal checks (D5, LOW): vfc L1477 and L1530, PIA L759 and L818 accept ANY SystemExit (no message match); PIA L818 would also
  pass if the p2035 re-derivation raised instead of the stub guard. TIE's pass-1 sha gate is presence-dependent (`if cfg.get("cache1_sha256")
  and ...`, L202): the config of record carries it, so it runs.
- Not found: an `assert` under -O (0 in all three); a sha matched anywhere instead of on its line (the H3 selftest matches the run_meta sha on
  the evidence entry; the TIE sha refusal matches its own message); a byte-identity claim without an execution witness (none is made).

## Defects

**D1 HIGH (vote_frame_cert.py combiner_ok L225-L243; latent).** The AST-equivalence branch certifies combiners that do not apply the transposition
before comparing (4 of 9 false passes). FIX: delete the branch and accept only rejudge_grok.combine_orders imported by name and AST-identical at the
run-time pin (the record needs nothing else: all three E-COMB writers take that branch), or require that the transposed name is the one compared
in `flip` and that the returned winner is the order-1 parameter; add a fixture per surviving mutant (wrong parameter, identity dict, a second
unverified combine call, one-parameter combiner, CONTESTANT with a failing combiner, duplicate under order 2 only, a first-write vs last-write pin
that straddles a commit).

**D2 HIGH (the H3 ruling, for the registrar; latent).** The source check verifies the combiner FUNCTION, not the ARGUMENT: a call-site transposition
before a correct combiner is certified with the wrong frame. FIX (ruling-level): the check also asserts, by ast at the pinned blob, that the second
argument of the combiner call is the name stored in the order-2 column and that it is bound directly from rejudge_grok.parse_judge; until then every
E-COMB certificate carries a reviewer's data-flow reading at the pinned blob (done here for the three caches).

**D3 MEDIUM (position_index_all.py load_cert L162-L169).** The certificate's script sha is printed, not compared. FIX: refuse unless
`cert["script_sha256_16_lf"]` equals the READY's sha256-lf16 of vote_frame_cert.py (a426fddc03ce7601) or at least `vfc.script_shas()[0]` of the
imported module. Until fixed: condition P-C1.

**D4 MEDIUM (registration-level).** Duplicate keys -> UNCERTIFIABLE is a class extension not in the registration or any ruling (ruling (a) above);
moot on the record (0 duplicate groups).

**D5 LOW.** Selftest refusal checks that accept any SystemExit (listed above). FIX: match the message.

**D6 LOW.** The real pool_guard.assert_pool_of_record is not executed by any selftest (injected stub); its execution is the dry-run's `[POOLS]` /
`[POOL]` line. FIX: none needed if the dry-run output is read (P-C2).

**D7 MEDIUM (for the registrar; not a code defect).** rubric_contrast.db is classed UNCERTIFIABLE by the ruling's pin rule because its first 16 of
11,124 rows precede the writer's only commit by up to 47 s; its frame is POSITIONAL by source reading and by 10,478 / 10,478 E-COMB rows. The
instrument applies the ruling as written and must not be changed by the run-operator. Consequences the registrar should record before the run:
(i) P4 ("at least 1 UNCERTIFIABLE") may be carried by this pin-timing reason (hence the reason breakdown in ruling (a)); (ii) the Mistral
rubric_contrast rows are excluded from POSITION-INDEX-ALL. Keeping or amending the pin rule is the registrar's decision; this review makes no
recommendation to relax it.

## Conditions

**V-C1 (VOTE-FRAME-CERT, registration flow).** `--run` needs the data-steward's INDEPENDENT listing (E1; the registration's WHO line); it is not
part of this review. The run refuses without it (require_steward, mutant KILLED).

**V-C2 (VOTE-FRAME-CERT, count check on the run output).** The certificate text must carry EXACTLY three `H3 COMBINER CHECK` lines
(`grep -c "H3 COMBINER CHECK"` = 3): rubric_ladder.db PASS, pinned blob f03cb302dfb38f5d7cf396af3115736bc4f90b61, "L307 rejudge_grok.combine_orders:
AST-identical"; rubric_swap.db PASS, 3ebf4f4a6e391de479f78ffcde1029530a72a571, "L187 ... AST-identical"; rubric_contrast.db FAIL, "first write
min(verdicts.ts) = 1788699989", "cannot be pinned", class UNCERTIFIABLE; and `grep -c "AST-equivalent"` = 0. Any other count or result voids this
READY for VOTE-FRAME-CERT (D1 / D2 would then be reachable).

**V-C3 (registrar, before the run is scored).** Rule D4 (duplicate class) and D7 (rubric_contrast), and fix how P4 is read (by reason).

**P-C1 (POSITION-INDEX-ALL).** Until D3 is fixed, the run-operator verifies before `--dry-run`:
`python -c "import json;print(json.load(open('experiment_results/vote_frame_cert.json'))['script_sha256_16_lf'])"` prints `a426fddc03ce7601`;
any other value refuses.

**P-C2 (POSITION-INDEX-ALL).** The dry-run's first line is `[POOLS]` and names p2035adddedd1becb verified over 228 ids and p2dca21ab5f4ef3ae through
pool_guard (the real guard's execution, D6); it runs only after VOTE-FRAME-CERT is HELD and recorded (unchanged registration gate).

TIE-MECHANICS: READY at the pins above; its logic was confirmed at d237e56 (14edeb4 items 15-18) and the 84ab7e3 diff to it touches only the
injectable guard, the [SCHEMA] message and the selftest (`git diff d237e56 84ab7e3 -- tools/analysis/tie_mechanics.py`).

## Commands (reproduce)

```
W=.claude/worktrees/vote-frame-instruments; R=<session scratchpad>/vote_frame_rr
git -C $W -c core.autocrlf=false archive 84ab7e3 tools/analysis src/main/kotlin experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json | tar -x -C $R/tree
git -C $W hash-object tools/analysis/<f>.py ; sha256sum $R/tree/tools/analysis/<f>.py | cut -c1-16
(cd $R/tree/tools/analysis; PYTHONDONTWRITEBYTECODE=1 python [-O] $R/guard.py <t>.py --selftest)
VFR_WT=$R/tree/tools/analysis python $R/guard.py $R/{adv_frames,order1_endtoend,kotlin_judges}.py ; (cwd tree/tools/analysis) python $R/guard.py $R/c2paths.py
python $R/mutate2.py $R/tree_m2/tools/analysis $R/guard.py ; python $R/mutate_review_h.py $R/tree_mr/tools/analysis ; python $R/mutate_rr.py $R/tree_mine/tools/analysis $R/guard.py
python $R/h3_real.py $R/tree_mine/tools/analysis ; python $R/indep_comb.py ; python $R/h3_adv.py $R/tree_mine/tools/analysis
python $R/schema_scan.py $R/tree_mine/tools/analysis ; python $R/long_dups.py $R/tree_mine/tools/analysis ; python $R/kdups.py
git log --follow --format='%h %cI' -- tools/analysis/{rubric_ladder,rubric_swap,rubric_value_contrast,rejudge_grok}.py
```
