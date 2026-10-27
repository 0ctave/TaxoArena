# ROUND 2 (2026-09-25): delta READY of VFC-FIXES-2, part (i), build 930ccc7. Verdict: READY (part i)

Reviewer: adversarial-reviewer. Zero calls. No DB under experiment_results was opened; PILOT-K46 was writing at the time. Everything was executed on an LF `git archive` of 930ccc7, on temp fixtures, or on git objects. This section is inserted above round 1, which follows below it unchanged.

## R2.0 Verdict

**READY (part i)** for build 930ccc7. F1-F7 of round 1 are fixed and each is executed by the selftest.
- My 20 round-1 mutants and my 10 fresh ones (F1, F5, F6, F7) were run in one pass on my own LF archive: 28 killed by a named check, 1 killed by an exception (a LOW, R2-L1), 0 survived.
- Three conditions bind the next steps, not part (i):
  - **R2-M1**: fix the scorer hole BEFORE (ii) is scored.
  - The open deviation on '' is ACCEPTED under a routing rule (R2.5).
  - The (ii)/(iii) commands below are to be run exactly as written, after the pilot's outcome is written (F5 freeze).

## R2.1 Pins (hash kind named; the LF rendering is of record)

| file at 930ccc7 | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/vote_frame_cert.py | c99fb126ea813328e9909dc4ce1ed5123e1fece0 | 211112d41eed0b77 | ec3e9a34f042068f |
| tools/analysis/position_index_all.py (unchanged since 00775fc) | bcbaf609bf9ee959e45daef7fbd50810e164a696 | 9c78d485f37f442a | 50bb9285e9068f0b |
| tools/analysis/tie_mechanics.py (unchanged) | 7f88d2ac581679aea33a2a25dc088883785fca86 | d6a1a0409a0fc06e | 4a18124878801487 |

- Parent: `git rev-parse 930ccc7^` = 00775fc.
- Scope: `git diff --name-only 00775fc 930ccc7 | wc -l` = 1 (vote_frame_cert.py, +127/-24).
- VFC_PIN_LF: stays 72ceddfe919a982e.
- Harness (scratch, not committed): `vf2/rerun_vf3.py` sha256-lf16 721c16e43f0342f2, file LF (0 CR bytes). It must be re-pinned after the R2-M1 fix.
- Outputs of record at main 01a506e:

| output | blob | sha256-lf16 |
|---|---|---|
| vote_frame_cert.txt | 8db4403f | 5e3af71cfd97e759 |
| vote_frame_cert.json | 5ec19826 | 48e5f5a3d4dd02d0 |
| position_index_all_outcome.txt | bb1578ca | 1c4370b23474cf3c |
| x12_crossdomain/tie_mechanics_outcome.txt | a2df609d | 2b28ee178c466477 |

## R2.2 Per-claim table

| claim | verdict | command / evidence | got |
|---|---|---|---|
| selftests 472/0, 55/0 (1 INFO), 29/0, python and -O | CONFIRMED | `git -c core.autocrlf=false archive 930ccc7 ...` -> rv2/T3r (shas equal the LF pins); 6 runs, rv2/r2st_*.txt | 472/0 twice; 55/0 +1 INFO twice; 29/0 twice |
| F1: combined label resolved before the gate; total decides R-2 / R-6; unresolvable_inf feeds m; fixtures ecomb_r6_tie, rx_d_tie | CONFIRMED | diff L1148-L1157. My round-1 probe re-run on T3r (rv2/probe_r2.py): P1 (the defect) is now UNCERTIFIABLE R6, unres 1. P2-P5 are unchanged and correct | fresh mutants f1_resolve_after_gate, f1_inf_counts_all_rows, f1_trigger_on_inf_only and f1_m_uses_total: KILLED-BY-CHECK. f1_secondary_on_inf_only: KILLED-BY-EXCEPTION (R2-L1) |
| F2: refuses() fails by name on non-SystemExit | CONFIRMED | my r7_none_admitted and r7_breakdown_no_guard (round 1: killed by KeyError crash) | now KILLED-BY-CHECK: "[NOT a [R-7] refusal: KeyError('uncert_reason')]" |
| F3: rx_a1 | CONFIRMED | my r2_long_ge2 and r2_long_order2_only (round 1: SURVIVED) | KILLED-BY-CHECK on rx_a1 |
| F4: fixtures ecomb_r6_amb, rx_d_warning, d1_runpy / code / codeop, d2_stdlib_shadow | CONFIRMED | my r3_ecomb_amb_not_r6, r6_warning_lost, d1_drop_runpy_code, d2_stdlib_before_local (all SURVIVED in round 1) | all 4 KILLED-BY-CHECK |
| F5: builtins in D1_MODULES; my 2 vectors are fixtures | CONFIRMED | fresh f5_builtins_removed | KILLED-BY-CHECK (d1_from_builtins_exec) |
| F6: H3 descriptive on R6 E-COMB units | CONFIRMED | fresh f6_descriptive_decides (lets H3 set R2) and f6_not_run | both KILLED-BY-CHECK (c-tampered) |
| F7: per-order counts | CONFIRMED | fresh f7_summed_again | KILLED-BY-CHECK (a1) |
| builder's 44 mutants: 41 by check, 3 by designed refusals, 0 survived | CONFIRMED (read, not re-run) | vf2/mut3_out.txt shows 40 by check, 3 by exception (r1_label_rx, p_d5_reader_pinned, p_vfc_a_old_trigger: the designed SystemExit refusals accepted in round 1), 1 NOT-APPLIED (r9_no_label_space). vf2/adapted_out.txt: r9 adapted, KILLED-BY-CHECK | 40 + 1 adapted = 41 by check. Controls pass (472/0, 55/0) |
| my 20 rerun by the builder, "all killed by a named check; two strings adapted" | CONFIRMED, and meaning preserved | vf2/rmut3_out.txt (19 by check + 1 NOT-APPLIED, whose adapted run is in adapted_out.txt) and my own independent pass rv2/rmut2_out.txt | the adapted strings keep their meaning. r2_long_order2_only keeps `int(a != pair[0])` and leaves the new label tally in place. d1_drop_runpy_code removes runpy / code / codeop and keeps the new builtins. r9_no_label_space drops label_space and keeps unresolvable_values. In my pass all 20 are KILLED-BY-CHECK |
| harness refusals | CONFIRMED by execution | the hook's own source, extracted from rerun_vf3.py, executed against a FAKE repo in temp | REFUSED: open w; os.open O_WRONLY; os.remove; os.unlink; os.replace; os.rmdir; shutil.rmtree; a plain connect; mode=ro without immutable. ALLOWED: open r, os.open O_RDONLY, ro+immutable, a write in OUT. Not guarded: os.mkdir inside MAIN (harmless). C-ii-1 executed: a plain (CRLF) archive -> "[C-ii-1] REFUSED ... ec3e9a34 ... CR bytes 2766", and no OUT created |
| the scorer flags a class move | CONFIRMED, with ONE HOLE (R2-M1) | 9 synthetic variants of the builder's syn_A (itself 0 findings) scored by `rerun_vf3.py score-vfc` against the record text (rec_vfc.txt == `git show HEAD:experiment_results/vote_frame_cert.txt`, cmp identical) | FLAGGED (rc 3): the rubric_ladder class move (header and unit lines); P2 54 -> 53; a secondary m wrong; E2 line deleted; an inserted cache header; a "P4 reason (6) R6" line. **PASSED (rc 0): an 8-space-indented note line inserted under rubric_ladder** (e.g. a new "WARNING: ..." or "R6 ..." note). The scorer puts every inserted indented line, wherever it sits, into the "C3 block" |

## R2.3 Findings

- **R2-M1 (MEDIUM; condition on (ii), not on part (i)).** rerun_vf3.py score-vfc absorbs ANY inserted line that starts with 8 spaces into the C3 block, and checks that block only for "CERTIFIED-CONTESTANT / 387/387 / contestant 380". An inserted note anywhere is therefore not a finding. A new "WARNING: the stored combined column ... is MIXED" (R-6's retained power) would reach the record unflagged. So would a new "H3 on the R6 unit" note, although for that one the unit's class line also moves and is caught.
  - FIX: admit an inserted line into the C3 block only when its difflib opcode lies inside record L154-L157 (i1 in 153..157). Every other insertion is a finding.
  - Re-run my variant C, which must then give rc 3. Re-pin the harness sha.
- **R2-L1 (LOW).** Mutant f1_secondary_on_inf_only (R-6 keyed on unresolvable_inf only) makes the rx_d_tie secondary CERTIFIED. The (d-tie) check then indexes sdt["resolved"], and the selftest aborts at 435 of 472 with KeyError('resolved') and 0 named FAIL lines.
  - It is killed, but by an exception inside a check, and 37 checks never run.
  - FIX: use .get in the (d-tie) check (and the (d) / (d') checks), so that it fails by name. No re-review is needed for this alone; confirm by re-running that one mutant.
- **R2-L2 (LOW).** os.mkdir inside MAIN is not guarded by the hook. The instruments create no directories under MAIN, and C-ii-3 compares the four outputs of record. Documented only.

## R2.4 Deviations of round 2

- The (d-tie) informative count excludes the TIE row (m = resolved + the unresolvable labels on rows with both votes decisive). ACCEPT: that is R-6's "m informative". The total still decides R-6.
- `unresolvable_values` (the top-5 labels) is added to units and secondaries, and printed. ACCEPT: descriptive; (ii) needs it.
- The descriptive H3 runs only when resolved_klass is CERTIFIED (not AMBIGUOUS). ACCEPT: H3 has never been defined on an AMBIGUOUS unit (fixture ecomb_r6_amb asserts that it is absent).

## R2.5 The open deviation: should '' be unresolvable?

Ruling: **ACCEPT as the letter of the ruling, with a routing rule.**
- **The letter.** R-1's definition of an unresolvable label is "neither a position, nor TIE / INVALID / NULL, nor a contestant name the name profile can map". '' is none of these; NULL maps to INVALID, and '' is not NULL.
- **What changed.** '' was ALREADY unresolvable before round 2:
  - at 00775fc on every row with both votes decisive, and in LONG tables at every build (to_order1_frame('') is None);
  - probe P7 on T3r: '' on a decisive E-COMB row gives R6;
  - probe P6: '' on a TIE row gives R6.
  - Round 2 adds only the E-COMB rows whose votes are not both decisive, which is exactly what F1 requires.
- **Why not map '' to INVALID.** Mapping '' to INVALID would drop an informative row silently when its votes are decisive: abf4db5 D4 again. Mapping it only on non-decisive rows would be a new rule not in the ruling.
- **ROUTING RULE for (ii).** If the F1 readout shows any unit of record moving to R6, the readout must print its `unresolvable_values`. Then:
  - If the moved labels are ALL '', the move is a FINDING for the arena-specialist (the question is "is '' NULL?"), and (ii) is NOT scored until it is ruled. Neither the builder nor the run-operator may default it either way.
  - If any other label moves a unit, it is an ordinary R6 finding under R-5.

## R2.6 Commands and expected diffs for (ii) and (iii)

When: after the PILOT-K46 outcome is written (F5 freeze), and after the R2-M1 fix, with the harness re-pinned. Use Git Bash. Replace `<S>` with a scratch directory OUTSIDE the repository. `M=Z:/FAC/TUBerlin/THESIS/TaxoArena`.

```
# 0. the build and the records of reference (read-only git objects)
mkdir -p <S>/T && git -C $M -c core.autocrlf=false archive 930ccc7 tools/analysis src/main/kotlin experiment_configs | tar -x -C <S>/T
sha256sum <S>/T/tools/analysis/vote_frame_cert.py        # must print 211112d41eed0b77...
for f in vote_frame_cert.txt vote_frame_cert.json position_index_all_outcome.txt x12_crossdomain/tie_mechanics_outcome.txt; do
  git -C $M show HEAD:experiment_results/$f > <S>/rec_$(basename $f); done
# (ii) the certificate, restricted to the 62 recorded caches (it refuses on any cache that moved)
python <H>/rerun_vf3.py vfc --build <S>/T/tools/analysis --expect-lf 211112d41eed0b77 --repo $M --out <S>/ii
python <H>/rerun_vf3.py score-vfc --rec <S>/rec_vote_frame_cert.txt --new <S>/ii/vote_frame_cert.txt --rec-json <S>/rec_vote_frame_cert.json --new-json <S>/ii/vote_frame_cert.json
# (iii)
python <H>/rerun_vf3.py pia --build <S>/T/tools/analysis --expect-lf 211112d41eed0b77 --repo $M --out <S>/iii_pia
python <H>/rerun_vf3.py score-pia --rec <S>/rec_position_index_all_outcome.txt --new <S>/iii_pia/position_index_all_outcome.txt
python <H>/rerun_vf3.py tm --build <S>/T/tools/analysis --expect-lf 211112d41eed0b77 --repo $M --out <S>/iii_tm
python <H>/rerun_vf3.py score-tm --rec <S>/rec_tie_mechanics_outcome.txt --new <S>/iii_tm/tie_mechanics_outcome.txt
```

`<H>` is the directory of the RE-PINNED harness. Each leg must print:
- `[C-ii-3] ... unchanged`;
- vfc: `[PRE] 62 of 62` and `[POST] 62 of 62 caches unchanged`.

EXPECTED DIFFS, (ii), against the record text of c731836 (404 lines). ONLY these may differ:
- L1: the script sha, 211112d41eed0b77 / ec3e9a34f042068f.
- L4: "62 SQLite files scanned".
- L388: "0 other scanned files".
- L154-L157: the _backup copy is CERTIFIED-CONTESTANT, order-1 387/387, order-2 380 contestant, unresolvable 0 (C3).
- L345, L350: the H3 evidence gains the transitive-scan sentence.
- L389: classes 54 / 5 / 0 / 0 / 1 / 2.
- L400: "P4 HELD: 1 UNCERTIFIABLE among the 60".
- The six secondaries read "UNCERTIFIABLE (R6), secondary, n resolved of m informative":

  | line | cache | n resolved of m informative |
  |---|---|---|
  | L176 | causal_length/grok-reasoning | 111 of 1024 |
  | L180 | causal_length/mistral | 187 of 1048 |
  | L184 | causal_length/mistral_refgrok | 182 of 993 |
  | L188 | causal_length/mistral_refgrok_v2 | 140 of 972 |
  | L245 | x12_crossdomain/arxiask | 29 of 279 |
  | L275 | x12_crossdomain/oracle | 36 of 288 |

  - m is unchanged by F1, because unresolvable_inf counts the same rows as the old gated counter.
  - The TOTAL unresolvable printed in the same line MAY exceed 913 / 861 / 811 / 832 / 250 / 252 (F1). The readout states both totals, and the `labels` field.
- L402: six reasons, "(6) ... 0".
- L403: removed.
- L404: "P4 is carried by: ['E-COMB, combiner not verified']".

Anything else is a FINDING, never an expected diff. That includes:
- any class move, above all an E-COMB primary (rubric_ladder, rubric_swap, a raw-only E-COMB cache) moving to R6 under F1 (then R2.5 applies);
- any E1-E4 or P1-P5 line;
- a "P4 reason (6) R6" line;
- an inserted note (R2-M1).

EXPECTED DIFFS, (iii):
- position_index_all_outcome.txt: L2 ONLY (the index's own sha 8939144e5ce87636 / 6f6694eac5a176f8 -> 9c78d485f37f442a / 50bb9285e9068f0b). L3 (certificate writer 72ceddfe; entered 50, excluded 12) does not move. `[WITNESS]` shows 4 content resolutions.
- tie_mechanics_outcome.txt: 0 differing lines.
- A `[FRAME] REFUSED (R-8)` in either leg is a FINDING (drift), not an outcome.

## R2.7 Evidence (session scratchpad)

- rv2/T3r: the LF archive of 930ccc7.
- rv2/r2st_*.txt: the 6 selftest transcripts.
- rv2/probe_r2.py: probes P1-P7.
- rv2/rmut2.py and rmut2_out.txt: one pass, 3 workers, 30 mutants plus a control. Control PASS 472/0. 28 KILLED-BY-CHECK, 1 KILLED-BY-EXCEPTION (f1_secondary_on_inf_only), 0 survived.
- rv2/scor_*.txt: the 9 scorer variants.

## R2.8 What this round does not show

- It does not show (ii) or (iii).
- It does not show whether any unit of record moves under F1 or on '' labels.
- It does not show that no dynamic route beyond the 16 vectors now fixtured or probed exists. V-C5 stays in force.

---

# READY review: VFC-FIXES-2, part (i) (delta check (i) of VFC-RX-RULING section 5)

Reviewer: adversarial-reviewer, 2026-09-25. Zero calls. No real-data run: no DB under experiment_results was opened, and no `--run` or `--dry-run` was issued. Everything below was executed on an LF `git archive` of the build, on temp fixtures, or on git objects.

Governing record: VFC-RX-RULING, programme L17171-L17328 (f1e9e68, v259), R-1..R-9, conditions (1)-(5), delta checks (i)-(iii). VFC-FIXES-2 scope: D1-D5 of docs/reviews/READY_vote_frame_fixes.md (9d3e261).

## VERDICT: NOT READY (part i)

One HIGH defect: R-2 is not implemented as ruled on the E-COMB tally. The ruling says "whatever the parse of the row". The build counts an unresolvable combined label only when both per-order votes are decisive. I built a fixture that shows this: an E-COMB primary with one unresolvable combined label on a TIE-vote row is **CERTIFIED-POSITIONAL, with unresolvable_labels 0**.

Two MEDIUM test gaps:
- The R-7 fixture (e) kills its mutants by a KeyError crash, not by a named check.
- The LONG trigger's boundary is untested. Mutants survive for "one or more" rewritten as "> 1", and for "order-2 labels only".

The fixes are small (section 4). Part (i) needs a re-review of the delta only; my probes and mutants are in the scratchpad (section 6) and can be re-run as they are.

Everything else the builder claims reproduces:
- selftests 436/0, 55/0 (1 INFO) and 29/0 under python and -O;
- 38 of 38 mutants killed, with 2 passing controls;
- the static pre-check shows 0 findings;
- VFC_PIN_LF is 72ceddfe;
- the diff touches 2 files.

## 1. Pins (hash kind named; the LF rendering is of record)

| file at 00775fc | blob | sha256-lf16 | sha256-crlf16 | worktree file |
|---|---|---|---|---|
| tools/analysis/vote_frame_cert.py | 94ff6f714391caae668f5f73a767cf188c1d06ec | 8b1b0f4e7223987f | 9cbde52f26ddfc39 | LF (8b1b0f4e) |
| tools/analysis/position_index_all.py | bcbaf609bf9ee959e45daef7fbd50810e164a696 | 9c78d485f37f442a | 50bb9285e9068f0b | CRLF (50bb9285) |
| tools/analysis/tie_mechanics.py (unchanged) | 7f88d2ac581679aea33a2a25dc088883785fca86 | d6a1a0409a0fc06e | 4a18124878801487 | CRLF |

Commands: `git rev-parse 00775fc:<p>`, `git show 00775fc:<p> | sha256sum`, CRLF = the LF bytes with \n -> \r\n, hashed.

Other pins and state:
- Parent f1e9e68. `git merge-base --is-ancestor 5ff5e73 f1e9e68` = true, and f1e9e68 is an ancestor of main 31420e9.
- `git diff --name-only f1e9e68 HEAD -- <the three files> | wc -l` = 0: main has not moved these files since the parent.
- VFC_PIN_LF = "72ceddfe919a982e" at position_index_all.py L179 (grep).

## 2. Per-claim table

| # | claim | verdict | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | the diff touches only the two files | CONFIRMED | `git diff --name-only f1e9e68 00775fc \| wc -l` = 2; `... \| grep -c "judge_v2/\|data_v2/"` = 0; numstat vfc +434/-31, pia +57/-20 | 2 files; 0 under judge_v2/data_v2 | - |
| 2 | selftests vfc 436/0, pia 55/0 (1 INFO), tm 29/0, python and -O, on an LF archive | CONFIRMED | `git -c core.autocrlf=false archive 00775fc tools/analysis src/main/kotlin experiment_configs`; archive shas equal the LF pins; all 6 runs | 436/0, 436/0; 55/0 +1 INFO, 55/0 +1 INFO; 29/0, 29/0 | - |
| 2a | (side finding) "an LF git archive" | NOTE | this checkout has core.autocrlf=true. A plain `git archive` writes CRLF: vfc sha256 9cbde52f, not 8b1b0f4e. The builder's t_head/ is LF (verified 3 of 3 files) | - | LOW (C-ii-1) |
| 3 | 38 mutants all killed, 2 passing controls; run 1 vacuous and rebuilt | CONFIRMED, PARTLY in kind | read scratchpad vf2/mut_run2.txt (not re-run; one harness run was allowed and I spent it on my own mutants). Controls: rc 0, 436/0 and 55/0 in both modes. Run 1 had no SELFTEST line (crash kills, no control): vacuous, as disclosed | 38/38 KILLED. But the harness kill test (`"SELFTEST FAIL" in tail`) cannot tell a check from an exception, because selftest() turns every exception into "[FAIL] exception:" plus SELFTEST FAIL. 3 of 38 are exception kills: r1_label_rx (SystemExit [R-7]), p_d5_reader_pinned (SystemExit [CERT] REFUSED), p_vfc_a_old_trigger (SystemExit [FRAME] R-8). All 3 are DESIGNED refusals with registered messages, not crashes. I accept them as kills | LOW |
| 4 | static pre-check: rubric_ladder, rubric_swap give 0 findings | CONFIRMED | my own run on main's git objects (no DB): module_tampering + _prime + _d1 + transitive_tampering + classify_import at pins f03cb302 / 3ebf4f4a | 0 / 0 findings. Transitive scan: rejudge_grok@fb8fb5bd, rubric_value_contrast@70370357 (+ bias_audit@d76b1db5 for swap). Every import is stdlib or local-with-history, so NO import takes the environment-dependent "installed distribution" branch. rubric_value_contrast.py (whose unit is R2 by pin timing anyway): 0 findings too | - |
| 5 | VFC_PIN_LF unchanged at 72ceddfe | CONFIRMED | grep L179 | 72ceddfe919a982e | - |
| 6 | R-1 R6 is the sixth reason; RX retired; P4 under six reasons | CONFIRMED | code L296-L300; UNCERT_CODES; selftest checks; builder mutants r1_* killed | - | - |
| 7 | R-2 trigger: ONE OR MORE unresolvable labels on the deciding tally, WHATEVER THE PARSE | **PARTLY / REFUTED on E-COMB** | reviewer probe rv2/probe.py, P1: E-COMB primary (the clean writer w_rj.py, H3 "after"), ONE combined label "stranger" on a row whose order-1 vote is TIE | **CERTIFIED-POSITIONAL, unresolvable_labels 0** (ruled: UNCERTIFIABLE (R6)). Cause: comb_tally L1138 `if v1 not in POS or v2 not in POS: continue` runs BEFORE the resolution at L1140-L1141, so such a label is never counted. The same counter feeds the R-6 secondary. LONG is as ruled: probe P3 (an unresolvable label on a row whose raw parse is TIE) gives R6, and P2 (exactly one, on order 1) gives R6 | **HIGH** (F1) |
| 8 | R-3 MIXED before R6; R6 before CERTIFIED / AMBIGUOUS | CONFIRMED in code; PARTLY tested | fixtures (b), (c'), (c'''); my probe P5 (E-COMB with every decisive label unresolvable: resolved AMBIGUOUS gives R6, correct) | my mutant r3_long_amb_not_r6 KILLED-BY-CHECK; r3_b2_after_r6 KILLED-BY-CHECK; **r3_ecomb_amb_not_r6 SURVIVED** (no E-COMB fixture with a resolved AMBIGUOUS subset) | LOW (F4) |
| 9 | R-4 / R-5 R6 excluded by class, counted, own line | CONFIRMED | pia plan() L210 / L217 filters by CACHE and by UNIT class; pia selftest x12r check | - | - |
| 10 | R-6 the WIDE secondary is never CERTIFIED on a subset; downgrade power kept | CONFIRMED except the count (row 7) | fixtures (d), (d'); my probe P4 (the R6 secondary's resolved subset is MIXED, so the WARNING prints: correct) | my r6_secondary_klass_kept and r6_resolved_count KILLED-BY-CHECK; **r6_warning_lost SURVIVED** (no fixture for the ruled clause "If they are MIXED, the WARNING applies as now") | LOW (F4) |
| 11 | R-7 fail closed, no default | CONFIRMED in code; fixture kills by CRASH | my mutants r7_none_admitted (require_reason_codes admits None) and r7_breakdown_no_guard (the guard in uncert_breakdown removed) | both **KILLED-BY-EXCEPTION**: KeyError('uncert_reason'), at 402 of 436 checks, in both modes. `refuses()` catches only SystemExit, so the named (e) checks never fail. In production the unit still aborts, but by accident, not by the guard | MEDIUM (F2) |
| 12 | R-8 the reader refuses on a None | CONFIRMED | fixture (f), the copy check, pia x12r; my r8_order1_drop, r8_contestant_only and p_r8_via_index_order1_drop KILLED-BY-CHECK | - | - |
| 13 | R-9 label_space "unresolved" | CONFIRMED | r6_downgrade L1178; builder mutant r9 killed; my probes P2, P3, P5 print "unresolved" | - | - |
| 14 | D1 the five routes caught (u1-u7 as fixtures) | CONFIRMED for u1-u7; class still OPEN | my 14 new static vectors (rv2/d1_vectors.py and follow-up): 12 CAUGHT, **2 PASS**: `import builtins; getattr(builtins, 'ex'+'ec')('import rejudge_grok as r; r.combine_orders = None')` and `from builtins import exec as _e; _e(...)` | 2 new false certificates; **d1_drop_runpy_code SURVIVED** (runpy/code/codeop have no fixture) | MEDIUM (latent; V-C5 stays) (F5) |
| 15 | D2 the transitive scan fails closed | CONFIRMED | fixtures d2_*; my d2_isdir_off and d2_relative_skip KILLED-BY-CHECK | **d2_stdlib_before_local SURVIVED**: no fixture has a local module that SHADOWS a stdlib name. tools/analysis is first on sys.path, so tools/analysis/csv.py WOULD be the csv a writer imports. The build's order (history first) is right, but untested | LOW (F4) |
| 16 | D3 fixture, D4 digest pin, D5 INFO line | CONFIRMED | builder mutants d3_unparseable_passes, d4_wrong_content_sha and p_d5_reader_pinned killed; the D5 check executes load_cert with a foreign writer sha | - | - |
| 17 | prepared (ii)/(iii) harness refuses writes to MAIN and non-immutable opens | CONFIRMED by execution, with 2 holes | I executed the hook's own source (extracted from vf2/rerun_vf2.py) against a FAKE repo in temp | REFUSED: open w / a / r+, a plain sqlite3.connect, `mode=ro` without immutable. ALLOWED: open r, `mode=ro&immutable=1`. **ALLOWED (holes): os.open(O_WRONLY), os.remove.** None of the three instruments uses either outside its selftest temp dir (grep: the only os.remove is pia L1048/L1053, in the selftest on tmp) | LOW |
| 18 | expected diffs for (ii)/(iii) stated precisely enough to score | **NOT MET by the build** (the harness names only "L4 / L388"); STATED HERE, section 5 | cert_rec.txt = `git show HEAD:experiment_results/vote_frame_cert.txt` (404 lines); position_index_all_outcome.txt L2-L3; tie_mechanics_outcome.txt L14 | - | MEDIUM (C-ii-2) |

## 3. Deviations: rulings

- **Dev 1. The position_index_all selftest fixture changed; the index's own sha changes. ACCEPT (forced).** The old x12u fixture asserted the silently shrunk denominator that R-2 / R-8 abolish (26 read of 30). Under the ruling it could not pass. The twin fixture x12r carries the old subject (R6, excluded, reader refuses).
  Consequence for (iii), not stated by the builder: position_index_all_outcome.txt L2 prints the index's OWN LF / CRLF sha (8939144e5ce87636 / 6f6694eac5a176f8 at record). That line WILL differ (-> 9c78d485f37f442a / 50bb9285e9068f0b). The outcome does NOT print the imported vote_frame_cert sha at all: L3 prints the certificate JSON's writer sha 72ceddfe, which stays. So the ruling's "apart from their printed vote_frame_cert sha" reads, for the index: "apart from L2 (the index's own sha)".

- **Dev 2. E-COMB precedence: R6 is decided before the H3 combiner check. ACCEPT, with F6 (LOW).** The ruling is silent on it. On an E-COMB unit that carries an unresolvable label AND an unverified or tampered writer, this prints R6 ("instrument knowledge, not frame") and never runs H3. The R2 finding is hidden behind the benign reason. No unit of record is affected: E-COMB-only primaries carry 0 unresolvable, and see F1 on how that 0 was counted.
  F6: run combiner_check on R6 E-COMB units DESCRIPTIVELY and print its result in the unit notes. The class stays R6.

- **Dev 3. B2 before R6. ACCEPT.** B2 is a MIXED rule on resolved rows. R-3 puts MIXED first. The fixture is rawonly_b2_r6, and my mutant r3_b2_after_r6 is KILLED-BY-CHECK.

- **Dev 4. The R6 own line prints only when > 0. ACCEPT.**
  - The six-reason line always prints "(6) stored labels unresolvable ... n".
  - "P4 is carried by" lists R6 exactly when n > 0.
  - Together they state "whether P4 is carried by R6" (R-5) in both cases.
  - This is verified by the builder's ub0 check and its killed mutant r5_no_own_line.

- **Dev 5. D1 stays a denylist. ACCEPT AS A STATED LIMIT; D1 is PARTLY closed.**
  - u1-u7 are closed.
  - My 2 new vectors pass (row 14).
  - C1 of 9d3e261 (V-C5) stays in force.
  - F5: add "builtins" to D1_MODULES (it closes both of my vectors), OR name "the builtins module" in STATED LIMITS.

- **Dev 6. D2 is environment-dependent. ACCEPT, with a recorded condition.**
  - The record's writers never reach the installed-distribution branch (row 4), so the certificate's classes do not depend on the environment.
  - For any future writer, the H3 evidence should list the imports skipped as "installed distribution" (LOW).
  - The selftest's d2_installed fixture needs one of numpy / pip / setuptools / scipy installed. Otherwise the selftest FAILS by design, and that is stated.

- **Dev 7. The D4 pin is a dict digest. ACCEPT.**
  - The digest catches any value edit: builder mutant d4_wrong_content_sha is killed.
  - The values themselves were verified against the files by 9d3e261 claim 9 and the real-run witness.
  - A coordinated edit of both the dict and the digest is a deliberate change, and it needs a READY.

- **Dev 8 (inferred from the code; not in the brief). R-2 also applies to E-COMB(re-parsed raw) units. ACCEPT.** Such units are decided by the combined column. Fixtures rawonly_r6 and rawonly_b2_r6 cover them.

- **Dev 9 (inferred). R-7 is enforced in run() over EVERY unit and secondary, not only in uncert_breakdown. ACCEPT.** It is stricter than the ruling. Builder mutants e_no_run_check and e_no_secondary_check are killed.

- **Descriptive miscount (LOW, F7).** r6_downgrade on LONG prints "the resolved subset (%d informative)" with n1_inf + n2_inf. That sums the two orders' informative ROWS, so a match is counted up to twice. It decides nothing. Print the two counts separately.

The brief lists 9 deviations. It names 7 of them (Dev 1-7). Dev 8 and Dev 9 are my identification from the diff. If the builder's own 8 and 9 differ, they are UNDETERMINED here.

## 4. Defects and the fixes owed before READY (i)

- **F1 (HIGH): R-2 / R-6 "whatever the parse" on the combined column.**
  - The fix, in comb_tally: resolve `wn` and count `t.unresolvable` BEFORE the `v1/v2 in POS` gate. Keep a second count, the unresolvable labels on rows with both votes decisive, for R-6's "n resolved of m informative". Print the total beside it.
  - Fixtures:
    - (c-tie): E-COMB primary, one unresolvable combined label on a TIE-vote row, gives R6.
    - (d-tie): the same in a WIDE secondary, which prints UNCERTIFIABLE (R6), secondary.
  - Mutant: restore the gate; it must be killed by a named check.
  - Consequence to state in (ii): the six secondaries' unresolvable counts, and possibly the E-COMB-only primaries' (rubric_ladder, rubric_swap, rubric_contrast, and the raw-only E-COMB caches), can RISE under the corrected counter. The ruling's census ("E-COMB-only primaries: unresolvable 0") was read from the JSON written with the gated counter, so it does not show that the ungated count is 0. If any E-COMB primary of record reaches R6 under F1, a class moves, and the registrar must be told before (ii) is scored.

- **F2 (MEDIUM): R-7 fixture (e) discriminates by crash.** Make `refuses()` return False, with the exception text, on any non-SystemExit exception, so that my r7_none_admitted and r7_breakdown_no_guard die by a named check. Alternatively, have uncert_breakdown use `.get` after require_reason_codes, so that the guard alone refuses.

- **F3 (MEDIUM): LONG trigger boundary.** Add a LONG fixture with EXACTLY ONE unresolvable label, on ORDER 1 (the ensemble arm), with the resolved rows consistent; it gives R6. My probe P2 shows the build already does this. This kills r2_long_ge2 and r2_long_order2_only (both SURVIVED).

- **F4 (LOW): untested clauses.** Add fixtures for:
  - E-COMB with a resolved-AMBIGUOUS subset plus an unresolvable label, giving R6 (kills r3_ecomb_amb_not_r6);
  - an R6 secondary whose resolved subset is MIXED, giving the WARNING (kills r6_warning_lost);
  - `import runpy` / `import code` / `import codeop` (kills d1_drop_runpy_code);
  - a committed local module named like a stdlib module (e.g. tools/analysis/csv.py, a patcher), which must be SCANNED, not skipped (kills d2_stdlib_before_local).

- **F5 (MEDIUM, latent): D1.** Add "builtins" to D1_MODULES, or name it in STATED LIMITS. Add my two vectors as fixtures.

- **F6 (LOW): H3 on R6 E-COMB units.** Run combiner_check on R6 E-COMB units DESCRIPTIVELY (Dev 2).

- **F7 (LOW): the r6_downgrade count.** Fix the descriptive "informative" sum.

## 5. Conditions on (ii) and (iii) (after the pilot and INDUCE-RUBRIC-3 close)

- **C-ii-1.** Build <T> with `git -c core.autocrlf=false archive <build> tools/analysis src/main/kotlin experiment_configs`. Check that `sha256sum <T>/tools/analysis/vote_frame_cert.py` equals the LF pin of the build under review (8b1b0f4e7223987f at 00775fc; a NEW pin after F1-F3). The harness's [BUILD] line prints both shas, and it must read the LF pin.

- **C-ii-2. The expected diffs of (ii), scored line by line against `git show HEAD:experiment_results/vote_frame_cert.txt` (c731836, 404 lines).** ONLY these may differ:
  - (a) Harness lines:
    - L1, the script sha: 72ceddfe919a982e / 9d86e3fba063ef5d at record, to the build's LF / CRLF;
    - L4, "62 SQLite files scanned" (record 184; the restricted scan);
    - L388, "0 other scanned files" (record 122).
    - L3 ("selftest (E3) ... PASS") stays byte-identical, but it is ASSERTED by the harness (`selftest_ok=True`), not executed. E3 of the re-derivation rests on part (i)'s selftest of the SAME LF sha. The harness's audit hook would refuse the selftest's own fixture writes, so passing True is necessary; say so in the readout.
  - (b) The C3 disclosure of 9d3e261:
    - L154-L157: the copy -> CERTIFIED-CONTESTANT, order-1 387/387, order-2 380 contestant, unresolvable 0;
    - L345, L350: the H3 evidence lists gain the transitive-scan sentence;
    - L389: classes 54 / 5 / 0 / 0 / 1 / 2;
    - L400: "P4 HELD: 1 UNCERTIFIABLE among the 60".
  - (c) The ruling's own items:
    - The six secondary lines L176, L180, L184, L188, L245, L275 read "secondary E-COMB: UNCERTIFIABLE (R6), secondary, n resolved of m informative ...", with (n, unresolvable) = (111, 913), (187, 861), (182, 811), (140, 832), (29, 250), (36, 252) under the build as it stands; that is, m = 1024, 1048, 993, 972, 279, 288. **If F1 lands, these counts are re-derived by the corrected counter, and the readout prints both the old and the new counts.**
    - L402 prints six reasons, with "(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 0";
    - L403 is gone;
    - L404 reads "P4 is carried by: ['E-COMB, combiner not verified']";
    - no "P4 reason (6) R6" own line (R6 = 0).
  - Anything else that moves, above all any class, any E1-E4 line or any P1-P5 line, is a FINDING, never an expected diff.
  - JSON: new keys only: secondary.uncert_reason / resolved_klass / resolved / informative on the six; uncert_reason 'RX' removed from the copy; name_profile on 15 LONG units (per 9d3e261); the script shas.

- **C-iii.**
  - POSITION-INDEX-ALL: position_index_all_outcome.txt re-derives byte-identically EXCEPT L2 (the index's own sha, 8939144e5ce87636 / 6f6694eac5a176f8 -> the new LF / CRLF). L3 (cert writer 72ceddfe, "caches entered 50, excluded 12") must NOT move.
  - TIE-MECHANICS: tie_mechanics_outcome.txt re-derives with ZERO differing lines (its own sha d6a1a0409a0fc06e is unchanged; it prints no vote_frame_cert sha).
  - The R-8 refusal must not fire. A refusal is a FINDING (drift between the certificate of record and a name constant), not an outcome.
  - The harness's [WITNESS] line must show name_profile_of executed, with 4 content resolutions as in 9d3e261.

- **C-ii-3.** The audit hook does not see os.open or os.remove (row 17). Before and after each leg, compare the sha256 of experiment_results/vote_frame_cert.json, position_index_all_outcome.txt and tie_mechanics_outcome.txt (the vfc leg already checks the 62 caches).

## 6. Evidence (reviewer scratch, session scratchpad rv2/)

- `T/`: the LF archive of 00775fc.
- `st_*_{py,O}.txt`: the 6 selftest transcripts.
- `probe.py`: probes P1-P5. Output:
  - P1 CERTIFIED-POSITIONAL, unres 0 (DEFECT);
  - P2 R6, unres 1;
  - P3 R6, unres 1;
  - P4 WARNING printed, secondary R6;
  - P5 R6, resolved AMBIGUOUS.
- `rmut.py` / `rmut_out.txt`: 20 reviewer mutants plus a control, run once, 3 workers, python and -O.
  - Control: PASS 436/0.
  - KILLED-BY-CHECK 12: r2_ecomb_ge2, r3_long_amb_not_r6, r3_b2_after_r6, r6_secondary_klass_kept, r6_resolved_count, r8_order1_drop, r8_contestant_only, d1_drop_types, d1_store_any_name_exempt, d2_isdir_off, d2_relative_skip, p_r8_via_index_order1_drop.
  - KILLED-BY-EXCEPTION 2: r7_none_admitted, r7_breakdown_no_guard (KeyError).
  - SURVIVED 6: r2_long_ge2, r2_long_order2_only, r3_ecomb_amb_not_r6, r6_warning_lost, d1_drop_runpy_code, d2_stdlib_before_local.
- `d1_vectors.py`: 14 static vectors, 12 caught and 2 pass.
- The builder's harness and output: scratchpad vf2/mutate_vf2.py, mut_run1.txt (vacuous, disclosed) and mut_run2.txt (38/38; 3 kills by designed SystemExit refusals).

## 7. What this review does not show

- It does not show (ii) or (iii). No real-data run was made, and none was allowed tonight.
- It does not show whether any E-COMB primary of record carries an unresolvable combined label on a non-decisive row, which is what F1's re-derivation will count.
- It does not show that no dynamic route beyond my 14 vectors exists.
- It did not re-run the builder's 38 mutants; they were read from mut_run2.txt.
