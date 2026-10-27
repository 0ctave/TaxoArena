# READY delta check (V-C4): VOTE-FRAME-CERT, POSITION-INDEX-ALL, TIE-MECHANICS at f6acf1b (adversarial reviewer, 2026-09-23, zero calls)

Code reviewed: branch `vote-frame-instruments`, HEAD `f6acf1b` (parent 5579eb7, whose files are on main at 8cd0f0e). Worktree clean
(`git status --short | wc -l` = 0). f6acf1b touches exactly vote_frame_cert.py and position_index_all.py (`git show --name-only`).
Record: the D-A bracket to 94731da, D-B RULED and D-C NOTED at ae20138 (programme L14214 bracket; section L14383ff), and x2 recorded as a STATED LIMIT.
Discipline as before: an LF export of f6acf1b (`git -c core.autocrlf=false archive`); every selftest, fixture and mutant run under the audit hook
(`guard.py`); the three rubric caches opened only through `vfc.open_ro` / a `mode=ro&immutable=1` URI (no `-wal` / `-shm` beside them: `ls rubric_*.db*`);
stat and sha256_16 unchanged after. No judge call, no `--dry-run`, no `--run`. Scratch: `<session scratchpad>/vote_frame_rr3/`.

## VERDICTS

| instrument | verdict |
|---|---|
| VOTE-FRAME-CERT (`vote_frame_cert.py`) | **READY-WITH-CONDITIONS** (V-C1, V-C2'', V-C5) |
| POSITION-INDEX-ALL (`position_index_all.py`) | **READY-WITH-CONDITIONS** (P-C2) |
| TIE-MECHANICS (`tie_mechanics.py`) | **READY** (byte-identical to its running pin) |

**V-C4: DISCHARGED for D-A and D-B; for D-C the listed vectors are closed but the class is not, and V-C5 replaces V-C4 for it.** V-C4's carry-over
test is met: h3_adv 0 of 9 false passes, rj_history 0 of 2 false certificates, callsite_adv 1 of 11 = x2 only, which ae20138 records as a stated
limit. I agree with the builder and the coordinator that x2 is a limit, not a trigger. On the record it is absent: the flip rate on both-decisive rows is
0.1372 (523 / 3812) in rubric_ladder, 0.1358 (544 / 4006) in rubric_swap and 0.1440 (1509 / 10478) in rubric_contrast, where x2 would read 1.000. My
own new vectors against D-C, however, find **10 false certificates of 15** (below). None of them is reachable on the record (a transitive scan of the
three writers and every local module they import finds none of them). COMB_WRITER is a closed list of three, so V-C5 makes any addition to it carry the
tamper reading.

## Pins this READY applies to (LF is the rendering of record; the working tree holds 0 CRLF bytes in all three)

| file | blob: (`git rev-parse f6acf1b:<path>` = `git hash-object`) | sha256-lf16: (of `git show f6acf1b:<path>`) |
|---|---|---|
| tools/analysis/vote_frame_cert.py | blob:8e1fbf6a7d557c2a82f5769ecea89c1d03f10705 | sha256-lf16:72ceddfe919a982e |
| tools/analysis/position_index_all.py | blob:31299cf31e134e05657798f528954f578975d286 | sha256-lf16:3bc1dae6fd4778db |
| tools/analysis/tie_mechanics.py | blob:7f88d2ac581679aea33a2a25dc088883785fca86 | sha256-lf16:d6a1a0409a0fc06e |

All agree to the digit with the coordinator's pins. `VFC_PIN_LF = "72ceddfe919a982e"` (position_index_all.py L156) equals vote_frame_cert.py's
sha256-lf16. **TIE-MECHANICS is byte-identical to its running pin:** `git diff --quiet 5579eb7 f6acf1b -- tools/analysis/tie_mechanics.py` succeeds; the
blob is 7f88d2ac at f6acf1b, at main 8cd0f0e, and in the main working tree (`git hash-object`), which is the blob the registrar records for the run
(programme, TIE-MECHANICS outcome section: "blob:7f88d2ac... / sha256-lf16:d6a1a0409a0fc06e").

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | pins | CONFIRMED | `git rev-parse`, `git show | sha256sum`, CRLF count | 6 / 6 | - |
| 2 | selftests 240 / 29 / 44 (+1 INFO), 0 failed, python and -O | CONFIRMED | `python [-O] guard.py <t>.py --selftest` | 240/0, 29/0, "44 checks, 0 failed; 1 INFO line(s), not checks" in both modes; audit 443 / 28 / 61 connects, all under temp. L1 fixed | - |
| 3 | mutate2 38/38 | CONFIRMED | re-run, own LF copy, baseline gated | 38/38 (1 NOT APPLIED, removed arm) | - |
| 4 | mutate3 15/15 | PARTLY | same | **13/13 applied, 2 NOT APPLIED** ("wrapped / non-name 2nd argument", "unparseable writer": the lines were rewritten by D-B) | LOW (L4) |
| 5 | mutate4 9/9 | PARTLY | same | **7/8 applied, 1 NOT APPLIED, 1 SURVIVED**: "a local def compared with REF, not with the pinned blob". This is an EQUIVALENT mutant under D-A: the pinned body must itself equal REF, so comparing the local def with REF or with the pinned body gives the same verdict | LOW (L4) |
| 6 | mutate5 11/11 | CONFIRMED | same | 11/11 | - |
| 7 | mutate_review 27/27; mutate_rr 7/7; mutate_rr2 11/11 (2 not applied) | CONFIRMED | same | 27/27 (1 NA); 7/7 (2 NA); 11/11 (2 NA: "pin-timing flag", "non-name 2nd argument", lines rewritten) | - |
| 8 | h3_adv 0 of 9 | CONFIRMED | h3_adv.py | 0 false passes; C6 a conservative false fail | - |
| 9 | rj_history 0 false certificates | CONFIRMED | rj_history.py | rjbad_direct and rjbad_localcopy UNCERTIFIABLE (R2): "the pinned rejudge_grok body is NOT AST-identical to the recipe's combine_orders (REF): not verified", printed on BOTH arms (D-A) | - |
| 10 | callsite_adv 1 of 11 = x2 | CONFIRMED | callsite_adv.py | x1 (order 1 transposed) now UNCERTIFIABLE R3 (D-B); x4 / x5 / x9 UNCERTIFIABLE R2 (D-C); x2 CERTIFIED (stated limit); x1b and x7 conservative false fails | - |
| 11 | real writers | CONFIRMED | h3_real.py, read-only | ladder: combiner "L307 ... AST-identical ... (a direct call)"; call site "'v2' bound directly from parse_judge at L306" and "'v1' ... at L305"; CERTIFIED-POSITIONAL 3812/0. swap: L187, v2 at L186, v1 at L185; CERTIFIED-POSITIONAL 4006/0. contrast: "the writer's earliest commit is 2026-09-06T15:07:16+02:00, after the first write: PIN TIMING", R2, pin_timing True (L2 fixed at L325 / L873). Caches unchanged | - |
| 12 | no registered criterion or denominator moved | CONFIRMED | `git diff -U0 5579eb7 f6acf1b -- tools/analysis/`: all 35 deleted lines read; added lines grepped for 0.80 / 25-60 / 0.35 / MDE / DEFF / score_ / P1-P5 / E1-E4 | 0 hits. The deletions are the D-A arms, the D2 single-argument call site, the old pin_timing line, VFC_PIN_LF (re-pinned), the selftest total line (L1), and the h3_rj_between / h3_local_badcopy CERTIFIED expectations (flipped to UNCERTIFIABLE, which restores 84ab7e3's expectation) | - |
| 13 | predecessor fixtures | CONFIRMED | adv_frames, kotlin_judges, c2paths | every A-fixture MIXED or 0.750; 0 cross-judge pairs; C2 PRIMARY UNDETERMINED | - |

## My new vectors against D-C and D-B (`tamper_adv.py`: each writer committed to a temp repo, rows as that writer would store them)

| writer | true frame | class | verdict |
|---|---|---|---|
| t0 clean | positional | CERTIFIED-POSITIONAL | correct |
| t1 `importlib.reload(rj)` | positional (reload re-runs the same source) | CERTIFIED-POSITIONAL | correct: inert |
| t2 `globals()['rj'] = _R()` (a bad combine_orders) | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t3 `vars(rj)['combine_orders'] = _nocombine` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t4 `__import__('rejudge_grok').combine_orders = _nocombine` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t5 `rj.__dict__['combine_orders'] = _nocombine` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t6 `sys.modules['rejudge_grok'].combine_orders = _nocombine` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t7 `rj.combine_orders.__code__ = _nocombine.__code__` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t8 `object.__setattr__(rj, 'combine_orders', _nocombine)` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t9 `_sa = setattr; _sa(rj, 'combine_orders', ...)` | positional | CERTIFIED-CONTESTANT | **FALSE** |
| t10 `vars(rj)['parse_judge'] = <transposing wrapper>` | both orders transposed | CERTIFIED-POSITIONAL | **FALSE** |
| t11 `rj.combine_orders(*(v2, v1))` (tuple swap inside the call) | positional, winner wrong | MIXED | correct (Starred argument; the data also refutes) |
| t12 `v1, v2 = v2, v1` before the call | orders swapped | UNCERTIFIABLE R3 | correct (two bindings) |
| t13 row stores `v2, v1` in the vote1 / vote2 slots | swapped in storage | MIXED | correct |
| t14 `import rj_patcher` (another module patches rejudge_grok at import) | positional | CERTIFIED-CONTESTANT | **FALSE** |

**10 of 15 false** (`tamper_adv.out`). module_tampering (L400-L415) implements the listed vectors exactly. Its own tests are strong: `mutate_rr3.py`,
12 of 12 of my mutants on the D-C, D-B, D-A and L2 code are killed (the tampering result ignored; each of its four branches removed; the order-1 leg
dropped; the order-1 column not required; direct call accepted whatever the pinned body; local copy of a non-REF body accepted; pin_timing never set or
always set; pinned body compared with itself). But an AST denylist cannot close Python's dynamic rebinding: subscript stores through `globals()` /
`vars()` / `__dict__` / `sys.modules`, a store whose target is rooted in a call (`__import__(...)`) or a chained attribute (`.__code__`), an aliased or
method-form setattr, and patches made by an imported module all pass.

**The record is clean of every one of them.** `writer_tamper_scan.py` reads, by git show and ast, the three writers at their pins AND, transitively,
every local module they import at its last commit at or before the cache's first write: rubric_ladder f03cb30 -> rejudge_grok fb8fb5b,
rubric_value_contrast 7037035; rubric_swap 3ebf4f4 -> bias_audit d76b1db -> rejudge_grok, rubric_value_contrast; rubric_value_contrast 7037035 ->
rejudge_grok. Result: 0 stores to the rj alias or its attributes, and 0 occurrences of globals() / vars( / __dict__ / __import__ / sys.modules /
__code__ / __setattr__ / setattr / delattr / exec( / eval( / importlib / reload( in any of them.

## Defects

**D-C' MEDIUM (latent; builder, within the spirit of ae20138's D-C).** module_tampering is a denylist, and 10 of 15 dynamic vectors pass it. The
record is unaffected, and COMB_WRITER is closed. FIX (conservative): fail R2 on
- any subscript store whose value is rooted in `globals()`, `vars(...)`, `sys.modules` or an `__dict__` attribute;
- any store whose target chain contains the rj alias, `__import__`, or a dunder attribute;
- any Name reference (not only a call) to `setattr`, `delattr`, `exec`, `eval`, `__import__`, `globals` or `vars`;
- any `object.__setattr__`;
- and scan the writer's local imports transitively at the same pin, as writer_tamper_scan.py does.

Or accept the residual and keep V-C5. Neither is required for the run of record.

**L4 LOW.** The builder's mutate3 "15/15" and mutate4 "9/9" do not reproduce at f6acf1b (13/13 with 2 not applied; 7/8 with 1 not applied and 1
equivalent survivor). The counts appear to be from before the D-A / D-B rewrite; nothing is weakened. FIX: re-run and retire the obsolete mutants.

**x2 (stated limit, ae20138).** Agreed. It is not a trigger; its data signature (a 1.000 flip rate) is absent on the record (0.136-0.144 above). An
optional, non-deciding print of the both-decisive flip rate per E-COMB table would make the limit visible in the certificate text; that is the
registrar's call.

## Conditions

**V-C1 (unchanged).** `--run` needs the data-steward's independent listing (E1).

**V-C2'' (replaces V-C2'; a COUNT check on the certificate text of the real run).**
- `grep -c "H3 COMBINER CHECK"` = 3: rubric_ladder.db PASS, pinned blob f03cb302dfb38f5d7cf396af3115736bc4f90b61, "L307 rejudge_grok.combine_orders:
  AST-identical to rejudge_grok.combine_orders (a direct call)"; rubric_swap.db PASS, 3ebf4f4a6e391de479f78ffcde1029530a72a571, "L187 ... (a direct
  call)"; rubric_contrast.db FAIL, "cannot be pinned", with the evidence "PIN TIMING".
- `grep -c "H3 CALL-SITE CHECK PASS"` = 2, and each of them carries both the order-2 line ("'v2' bound directly from parse_judge at L306" / "at L186")
  and the order-1 line ("'v1' ... at L305" / "at L185"). `grep -c "H3 CALL-SITE CHECK not reached"` = 1.
- `grep -c "is NOT AST-identical to the recipe"` = 0, `grep -c "AST-equivalent"` = 0, and `grep -c "rebinds or patches rejudge_grok"` = 0.
- The P4 reason line reads "(2) E-COMB, combiner not verified 1 [of which pin timing 1".
- Any other count voids this READY for VOTE-FRAME-CERT.

**V-C5 (replaces V-C4 for D-C).** COMB_WRITER stays the closed list of three. Any addition to it, or any reuse of the instrument on another E-COMB
cache, requires a READY that runs tamper_adv.py, callsite_adv.py, rj_history.py and writer_tamper_scan.py (the writer and its transitive local
imports at the pin) with 0 false certificates outside the ruled limits, unless D-C' is fixed first.

**P-C2 (unchanged).** The dry-run's first line is `[POOLS]`, naming p2035adddedd1becb verified over 228 ids and p2dca21ab5f4ef3ae through pool_guard;
it runs only after VOTE-FRAME-CERT is HELD and recorded. (P-C1 stays discharged: the index refuses any certificate whose script_sha256_16_lf is not
VFC_PIN_LF = 72ceddfe919a982e.)

## Commands (reproduce)

```
W=.claude/worktrees/vote-frame-instruments; R=<session scratchpad>/vote_frame_rr3
git -C $W -c core.autocrlf=false archive f6acf1b tools/analysis src/main/kotlin experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json | tar -x -C $R/tree
git -C $W rev-parse f6acf1b:tools/analysis/<f>.py ; git -C $W show f6acf1b:tools/analysis/<f>.py | sha256sum | cut -c1-16
git -C $W diff --quiet 5579eb7 f6acf1b -- tools/analysis/tie_mechanics.py && echo identical
(cd $R/tree/tools/analysis; PYTHONDONTWRITEBYTECODE=1 python [-O] $R/guard.py <t>.py --selftest)
python $R/mutate{2,3,4,5}.py <copy> $R/guard.py ; python $R/mutate_review_h.py <copy> ; python $R/mutate_rr{,2,3}.py <copy> $R/guard.py
python $R/guard.py $R/{h3_adv,callsite_adv,rj_history,tamper_adv}.py <copy> ; python $R/h3_real.py <copy> ; python $R/writer_tamper_scan.py
git -C $W diff -U0 5579eb7 f6acf1b -- tools/analysis/ | grep -E '^-' | grep -vc '^---'      # 35
```
