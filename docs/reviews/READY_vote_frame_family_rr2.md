# READY delta re-review: VOTE-FRAME-CERT, POSITION-INDEX-ALL, TIE-MECHANICS at 5579eb7 (adversarial reviewer, 2026-09-23, zero calls)

Code reviewed: branch `vote-frame-instruments`, HEAD `5579eb7` (parents efbf376, 84ab7e3; the READY bc2ea7b covered 84ab7e3). Worktree clean
(`git status --short | wc -l` = 0). efbf376 and 5579eb7 each touch exactly vote_frame_cert.py and position_index_all.py (`git show --name-only`).
Record reviewed against: the rulings 2c94cab (programme L14201-L14246: D2 call site, D4 duplicate key R4, D7 P4 by reason) and the amendment
94731da (L14248-L14278, bracket at L13994: the AST-equivalent arm withdrawn). Same discipline as bc2ea7b: an LF export of 5579eb7
(`git -c core.autocrlf=false archive`); every selftest, fixture and mutant under the audit hook (`guard.py`); DBs of record opened only through
`vfc.open_ro` after checking that no `-wal` sits beside them (none beside the three rubric caches); stat and sha256_16 unchanged after.
No judge call, no `--dry-run`, no `--run`. Scratch: `<session scratchpad>/vote_frame_rr2/`.

## VERDICTS

| instrument | verdict |
|---|---|
| VOTE-FRAME-CERT (`vote_frame_cert.py`) | **READY-WITH-CONDITIONS** (V-C1, V-C2', V-C4) |
| POSITION-INDEX-ALL (`position_index_all.py`) | **READY-WITH-CONDITIONS** (P-C2) |
| TIE-MECHANICS (`tie_mechanics.py`) | **READY** (unchanged since bc2ea7b) |

## Pins this READY applies to (LF is the rendering of record; the working tree holds 0 CRLF bytes in all three)

| file | blob: (`git rev-parse 5579eb7:<path>` = `git hash-object`) | sha256-lf16: (of `git show 5579eb7:<path>`) |
|---|---|---|
| tools/analysis/vote_frame_cert.py | blob:57dca54498e5b574073cc2c4ddc4d2b2d3933dd8 | sha256-lf16:fb114fecd879a6ca |
| tools/analysis/position_index_all.py | blob:6c3726c6a03d9f498ac324e72ea9b98a5fcd74aa | sha256-lf16:7be589fc83a0110e |
| tools/analysis/tie_mechanics.py | blob:7f88d2ac581679aea33a2a25dc088883785fca86 | sha256-lf16:d6a1a0409a0fc06e |

All three agree to the digit with the coordinator's pins. The gate a run-operator checks is sha256-lf16. position_index_all.py's
`VFC_PIN_LF = "fb114fecd879a6ca"` equals vote_frame_cert.py's sha256-lf16 (the selftest's INFO line prints "equal").

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | pins | CONFIRMED | `git rev-parse`, `git show | sha256sum`, CRLF count | 6 / 6 agree | - |
| 2 | selftests 195 / 29 / 45, 0 failed, python and -O | CONFIRMED, with a caveat | `python [-O] guard.py <t>.py --selftest` | 195/0, 29/0, "45 checks, 0 failed" in both modes; audit 359 / 28 / 61 connects, all under temp. The PIA "45" counts one `[INFO]` line (VFC_PIN_LF equality), so it is 44 checks + 1 INFO | LOW (L1) |
| 3 | mutate2 38/38, 1 not applied | CONFIRMED | re-run on its own LF copy; baseline gated | 38/38; NOT APPLIED "H3: zero transpositions accepted" (the arm is gone) | - |
| 4 | mutate3 15/15, mutate4 9/9 | CONFIRMED | same | 15/15; 9/9. Both gate on the baseline and kill only on a "SELFTEST FAIL" line | - |
| 5 | mutate_review 27/27, 1 not applied | CONFIRMED | hardened copy (kill only on SELFTEST FAIL) | 27/27; NOT APPLIED the old TIE pool-guard string (covered by mutate2's T-C2 mutant, KILLED) | - |
| 6 | my mutate_rr 7/7, 2 not applied | CONFIRMED | same | 7/7; NOT APPLIED the two mutants of the removed equivalence code | - |
| 7 | h3_adv FALSE-PASS 0 of 9 | CONFIRMED | h3_adv.py | 0 false passes; C6 (correct, differently written) a stated conservative false fail; C8 (renamed real body) PASS | - |
| 8 | real writers: ladder PASS+PASS, swap PASS+PASS, contrast FAIL on the pin | CONFIRMED | h3_real.py, read-only, repo = main checkout | rubric_ladder f03cb302 combiner "AST-identical ... (a direct call)", call site "L307 ... 'v2' bound directly from parse_judge at L306", CERTIFIED-POSITIONAL 3812/0; rubric_swap 3ebf4f4a, L187 / L186, CERTIFIED-POSITIONAL 4006/0; rubric_contrast "cannot be pinned", UNCERTIFIABLE, uncert_reason R2, pin_timing True (10478/0 underneath). Caches unchanged (size, mtime_ns, sha256_16) | - |
| 9 | D1 per the amendment | CONFIRMED as written; the amendment's text leaves a hole | combiner_ok L257-L265 (identity only); combiner_check L346-L367 | the equivalence arm is removed; see the ruling below and D-A | HIGH (D-A) |
| 10 | D2(a) call-site check | CONFIRMED for the second argument; PARTLY overall | callsite_check L398-L446; my 11 adversarial writers (callsite_adv.py) + 13 new mutants (mutate_rr2.py) | 5 false certificates of 11 (below); 12 of 13 mutants killed | HIGH (D-B, D-C) |
| 11 | D3 index refuses unless VFC_PIN_LF matches | CONFIRMED | load_cert L168-L180 (compare at L176); mutant "certificate pin not compared" KILLED | refuses on a mismatched pin; reads the matching one | - |
| 12 | D5 refusal tags | CONFIRMED | `grep -n "except SystemExit:"` | 0 bare catches in the three files | - |
| 13 | D7 P4 by reason, D4 duplicate key R4 | CONFIRMED | uncert_breakdown L1037-L1053; mutants "pin-timing flag never set" and "every reason counted as R2" KILLED | P4 still scored on the total UNCERTIFIABLE count (registered); reasons R1-R5 + RX printed | - |
| 14 | no registered criterion or denominator moved | CONFIRMED | `git diff -U0 84ab7e3 5579eb7 -- tools/analysis/`, all 61 deleted lines read (`grep -E "^-" | grep -vc "^---"`); grep of the added lines for 0.80 / 25-60 / 0.35 / MDE / DEFF / P1-P5 | score_criteria and score_predictions untouched; P1-P5 bands, E1-E4, SUPPORT_MDE, DEFF, MDE unchanged; the only criterion-adjacent additions are the P4 reason lines (printed, not scored). One EXPECTATION moved: the selftest check "h3_rj_between -> UNCERTIFIABLE" was deleted and replaced by "-> CERTIFIED-POSITIONAL" (D-A) | - |
| 15 | no assert | CONFIRMED | `ast.walk` count | 0 / 0 / 0 | - |

## The coordinator's question: does H3 trust rejudge_grok's history? YES. I agree with the fix.

**It produces a false certificate end to end, not just a green fixture** (`rj_history.py`): a writer run while rejudge_grok.combine_orders
lacked the transposition (the builder's RJ_BAD at commit A, first write "between" A and B) stores positional votes and an untransposed combined
winner. At 5579eb7: `rjbad_direct.db` (direct `rj.combine_orders` call) -> **CERTIFIED-CONTESTANT**, H3 PASS, call site PASS; `rjbad_localcopy.db`
(a local copy of that body) -> **CERTIFIED-CONTESTANT**, H3 PASS ("AST-identical to rejudge_grok.combine_orders"). The true frame is POSITIONAL;
unit_votes then transposes order 2 and the index reads FF / SS **19 / 21 against a truth of 33 / 27**. That is exactly the sign failure H3 exists
to stop. The builder's own fixture h3_rj_between reads CERTIFIED-POSITIONAL only because its rows were written with the CORRECT combine; the
selftest does not build the case the history defect produces. For the local copy the defect is also SILENT: only the direct-call arm prints
"NOT the recipe's REF_COMBINE_ORDERS"; the local-copy arm prints "AST-identical" with no comparison to the recipe.

**The fix, as the coordinator states it, is right:** a combiner is verified only if the pinned rejudge_grok.combine_orders body is AST-identical
to REF_COMBINE_ORDERS AND (the call is a direct call OR the local def is AST-identical to that body), else R2. Equivalently: compare everything
with REF, and additionally require the pinned rejudge_grok body to be REF when the call is direct. REF_COMBINE_ORDERS is itself pinned by the
selftest check "REF_COMBINE_ORDERS is AST-identical to the tree's rejudge_grok.combine_orders".

**It is within the amendment's text; the builder can do it; the registrar should add a one-line clarifying bracket when recording, not a new
ruling.** Reasons: (1) the amendment is headed "H3(b) of 0104e44 NARROWED" and says it WITHDRAWS the AST-equivalent arm and that conditions (a),
(c) and D2 "stand unchanged". It gives no licence to WIDEN anything, and a narrowing cannot move a case from UNCERTIFIABLE to CERTIFIED. (2) Under
0104e44(b) as implemented at 84ab7e3 (READY bc2ea7b), the direct call was checked "in rejudge_grok.py at ITS last commit at or before the same pin
time" against REF, and h3_rj_between was UNCERTIFIABLE. The 5579eb7 selftest deleted that expectation (`git diff -U0 84ab7e3 5579eb7`: the removed
check "H3 FAIL: rejudge_grok pinned at the SAME run-time (commit A, no transposition) -> UNCERTIFIABLE"). So the builder's literal reading WIDENED
the certified set, against the amendment's stated scope. (3) The amendment's stated rationale is "A wrong combiner can no longer certify a wrong
frame", and the literal reading contradicts it. (4) The words "AT THE PINNED rejudge_grok BLOB" are only meaningful if that blob's body is
checked. The builder was right to stop and report rather than choose. The registrar's bracket should say that "AST-identical to
rejudge_grok.combine_orders at the pinned blob" means "and that pinned body is AST-identical to the recipe's REF_COMBINE_ORDERS", so the reading
is fixed on the record. **On the record it changes nothing:** rejudge_grok.py has exactly one commit ever (fb8fb5b, `git log --follow`), its body
is REF (both real direct calls print "AST-identical ... (a direct call)"), and no writer of record uses a local copy.

## D2(a) call site: my adversarial writers (`callsite_adv.py`, each committed to a temp repo, rows as that writer would store them)

| writer | true frame | class at 5579eb7 | reason / H3 / call site | verdict |
|---|---|---|---|---|
| x0 clean | positional | CERTIFIED-POSITIONAL | PASS / PASS | correct |
| x1 `v1 = T(rj.parse_judge(raw1)[0])` stored and combined | **order 1 transposed** | **CERTIFIED-POSITIONAL** | PASS / PASS | **FALSE CERTIFICATE** (the check covers only the 2nd argument; E-COMB has no raw text to refute order 1: A1's class in an E-COMB-only cache) |
| x1b `v1 = rj.parse_judge(raw1)[0]` | positional | CERTIFIED-POSITIONAL | PASS / PASS | correct |
| x2 `v2, _ = rj.parse_judge(raw1)` (order-1 text parsed as order 2) | order-2 column holds order 1 | CERTIFIED-POSITIONAL | PASS / PASS | FALSE CERTIFICATE (an argument-source bug; every decisive row is then a flip, so it is visible in the data) |
| x3 `rj.combine_orders(v2, v1)` | positional | MIXED | - | correct (data refutes) |
| x4 module-level `rj.combine_orders = _nocombine` | positional | **CERTIFIED-CONTESTANT** | PASS / PASS | **FALSE CERTIFICATE** (a monkeypatched combiner counts as a "direct call") |
| x5 module-level `rj.parse_judge = <transposing wrapper>` | **both orders transposed** | **CERTIFIED-POSITIONAL** | PASS / PASS | **FALSE CERTIFICATE** |
| x6 row rebuilt after the tuple with T(order 2) | contestant | CERTIFIED-CONTESTANT | PASS / PASS | correct (data tells the truth once the combiner input is positional) |
| x7 the parse inside a `with` block | positional | UNCERTIFIABLE R3 | "2 bindings" | conservative false fail (`With` has no `.target`, so the whole block is walked) |
| x8 `from rejudge_grok import parse_judge as pj` | positional | CERTIFIED-POSITIONAL | PASS / PASS | correct |
| x9 `rj = _R()` (module name rebound to an object with a bad combine_orders) | positional | **CERTIFIED-CONTESTANT** | PASS / PASS | **FALSE CERTIFICATE** |

5 false certificates of 11 (`callsite_adv.out`). None is reachable on the record. writer_flow.py read by ast at the three pinned blobs
(f03cb30, 3ebf4f4, 7037035): **0** assignments to `rj.<attr>`, **0** rebindings of `rj`, **0** setattr / exec / eval; `v1, _ = rj.parse_judge(raw1)`
and `v2, _ = rj.parse_judge(raw2)` (contrast: `v1, c1` / `v2_raw, c2`) with raw1 built from `(ta, tb)` and raw2 from `(tb, ta)` (ladder L303-L306,
swap L183-L186, contrast L161-L164).

My mutants on the new code (`mutate_rr2.py`, baseline gated, a kill only on a SELFTEST FAIL line): **12 of 13 killed**. That includes the stored-name
check removed, more than one binding admitted, a binding not from parse_judge, a non-first tuple element, the call-site verdict ignored,
callsite_check's result discarded, no row tuple treated as a vacuous pass, no CREATE TABLE treated as a pass, a non-name argument, the pin-timing
flag, the reason counts, and the D3 pin. SURVIVED: "a parameter counted as no binding". It is near-equivalent, because a parameter never
re-bound from parse_judge still has 0 bindings and fails. LOW.

## Checks that pass without checking (item 4)

- The **rejudge_grok history trust** (D-A): "verified" without checking the body that ran.
- The **call site trusts the names `rj` and `rejudge_grok.parse_judge`** (D-C): a rebound or monkeypatched module passes both checks.
- **pin_timing** is set by the substring "cannot be pinned" (L826). It is also set by a run_meta sha that matches no commit ("the writer's run-time
  blob cannot be pinned"), which is not a timing case (L2, LOW).
- **VFC_PIN_LF equality with the imported vote_frame_cert** is an `[INFO]` line, not a check. This is harmless: any mismatch fails closed at load_cert
  on a real run. It is counted in the PIA "45 checks" (L1).
- Not found: an assert under -O; a bare `except SystemExit`; a sha matched off its line; a byte-identity claim without an execution witness.

## Defects

**D-A HIGH (latent; H3 trusts rejudge_grok's history).** Shown above. FIX (builder, within the amendment as argued): require the pinned
rejudge_grok.combine_orders body to be AST-identical to REF_COMBINE_ORDERS for a direct call, and compare a local def with REF (both, not
either); otherwise R2. Print the pinned body's REF identity on BOTH arms. Flip h3_rj_between and h3_local_badcopy to UNCERTIFIABLE (R2); add
rjbad_direct / rjbad_localcopy (rows written with the bad combine) as fixtures expecting UNCERTIFIABLE. mutate4's two last mutants, which are this
fix, then become the new baseline. The registrar adds a clarifying bracket at recording.

**D-B HIGH (latent; for the registrar: D2 covers only the order-2 argument).** An E-COMB-only cache whose writer transposed ORDER 1 before
storing and combining is CERTIFIED-POSITIONAL (x1). This is the bc2ea7b A1 blocker reappearing on the E-COMB path, where no raw text exists to
refute order 1. FIX: extend D2's (i) and (ii) to the first argument and the order-1 column (a one-line insertion that extends R3). x2 (order-2
name parsed from the order-1 raw) is a stated limit: record it as such. It is visible as a 100% flip rate.

**D-C HIGH (latent; for the registrar or builder).** The direct-call and parse_judge recognitions trust the module name: x4 (`rj.combine_orders =`),
x5 (`rj.parse_judge =`) and x9 (`rj = ...`) certify a wrong frame. FIX: a writer with any Store to the rejudge_grok alias, any assignment to an
attribute of it, or any setattr / exec / eval FAILS R2 (conservative). This is within the spirit of the amendment ("a direct call to
rejudge_grok.combine_orders"). A monkeypatched attribute is not that function, so the builder can implement it; the registrar notes it.

**L1 LOW.** The PIA selftest counts an `[INFO]` line as a check (45 = 44 + 1). **L2 LOW.** pin_timing also covers the unmatched-run_meta-sha case.
**L3 LOW.** `with`-block binding is a conservative false fail (x7).

## Conditions

**V-C1 (unchanged).** `--run` needs the data-steward's independent listing (E1).

**V-C2' (replaces V-C2; a COUNT check on the certificate text of the real run).**
- `grep -c "H3 COMBINER CHECK"` = 3: rubric_ladder.db PASS, pinned blob f03cb302dfb38f5d7cf396af3115736bc4f90b61, "L307 rejudge_grok.combine_orders:
  AST-identical to rejudge_grok.combine_orders (a direct call)"; rubric_swap.db PASS, 3ebf4f4a6e391de479f78ffcde1029530a72a571, "L187 ... (a direct
  call)"; rubric_contrast.db FAIL, "cannot be pinned".
- `grep -c "H3 CALL-SITE CHECK PASS"` = 2 (ladder "'v2' bound directly from parse_judge at L306"; swap "at L186") and `grep -c "H3 CALL-SITE CHECK
  not reached"` = 1.
- `grep -c "NOT the recipe's REF_COMBINE_ORDERS"` = 0 and `grep -c "AST-equivalent"` = 0.
- The P4 reason line shows "(2) E-COMB, combiner not verified 1 [of which pin timing 1 ...]".
- Any other count voids this READY for VOTE-FRAME-CERT. Under these counts none of D-A, D-B, D-C is reached: the only E-COMB-only tables on the record
  are these three (bc2ea7b schema scan: 3 of 184 files; read_schema is unchanged since).

**V-C4 (before any E-COMB cache other than these three is certified, or the instrument is reused).** D-A, D-B and D-C are fixed and re-reviewed. If
the builder fixes D-A (and D-C) now, the pins change and a delta check of those hunks is needed; the verdicts above then carry over if
h3_adv, callsite_adv and rj_history show 0 false certificates.

**P-C2 (unchanged).** The dry-run's first line is `[POOLS]`, naming p2035adddedd1becb verified over 228 ids and p2dca21ab5f4ef3ae through pool_guard;
it runs only after VOTE-FRAME-CERT is HELD and recorded. **P-C1 is DISCHARGED** by D3: load_cert refuses any certificate whose
script_sha256_16_lf is not VFC_PIN_LF = fb114fecd879a6ca (mutant KILLED).

TIE-MECHANICS: READY at blob:7f88d2ac581679aea33a2a25dc088883785fca86 / sha256-lf16:d6a1a0409a0fc06e. The file is unchanged since 84ab7e3; 29/29 normal
and -O; its mutants all killed in mutate2 / mutate_review.

## Commands (reproduce)

```
W=.claude/worktrees/vote-frame-instruments; R=<session scratchpad>/vote_frame_rr2
git -C $W -c core.autocrlf=false archive 5579eb7 tools/analysis src/main/kotlin experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json | tar -x -C $R/tree
git -C $W rev-parse 5579eb7:tools/analysis/<f>.py ; git -C $W show 5579eb7:tools/analysis/<f>.py | sha256sum | cut -c1-16
(cd $R/tree/tools/analysis; PYTHONDONTWRITEBYTECODE=1 python [-O] $R/guard.py <t>.py --selftest)
python $R/mutate{2,3,4}.py <copy>/tools/analysis $R/guard.py ; python $R/mutate_review_h.py <copy> ; python $R/mutate_rr{,2}.py <copy> $R/guard.py
python $R/guard.py $R/{adv_frames,kotlin_judges,c2paths}.py ; python $R/guard.py $R/h3_adv.py <copy> ; python $R/guard.py $R/callsite_adv.py <copy>
python $R/guard.py $R/rj_history.py <copy> ; python $R/h3_real.py <copy> ; python $R/writer_flow.py f03cb30:tools/analysis/rubric_ladder.py 3ebf4f4:... 7037035:...
git -C $W diff -U0 84ab7e3 5579eb7 -- tools/analysis/ | grep -E '^-' | grep -v '^---'
```
