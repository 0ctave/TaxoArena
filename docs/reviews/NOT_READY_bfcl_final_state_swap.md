# NOT READY: BFCL-FINAL-STATE-SWAP (adversarial reviewer, 2026-09-23, zero calls)

This file deliberately does NOT carry the gate's file name (`READY_bfcl_final_state_swap.md`), so
`bfcl_final_state_swap.launch()` keeps refusing. **The instrument code has no blocker. The one blocker is in the
registration's Support section (D-S1).** It can be cleared at zero calls, and the script need not change.

## A. Object reviewed

- `tools/analysis/bfcl_final_state_swap.py` at branch `bfcl-separators` @ `5f459b2`:
  - LF sha256[:16] **`1c67847de8de2efe`** (`git show 5f459b2:<path> | sha256sum`).
  - Blob `bbf3cb1be4e83996778944edff3b18f9c0165dd1`.
  - The worktree file has 0 CRLF, so its CRLF rendering is identical to the LF rendering.
  - 1,658 lines.
- Parent pin: `5e9db53b894eeccb` (blob `b289bb72...`), identical on main and on the branch.
- Transitive modules and `TaxonomyArenaService.kt` are blob-identical on main HEAD and `5f459b2`.
- Record reviewed against:
  - Registration: L12315-L12598 (ca3a7cc), read in the main checkout with the D1/D2/D3 brackets.
  - Registrar defect rulings: L13362-L13443 (7da2ec5).
  - Closed-line ruling: `docs/agents/leads/2026-09-23_bfcl_final_state_swap_ruling.md` (1470fe8).
  - The parent's post-run review.

## B. Per-claim table

| # | claim | verdict | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | Four literal replacements, each count == 1, 4 in total, refusing otherwise | CONFIRMED BY EXECUTION: counts [1,1,1,1] in the template and in the filled prompt; the selftest refuses 0 and 2 matches | independent recompute `scratchpad/rv/prompts.py` (FROM/TO typed from L12338-L12346; parent constants read by `ast`, no DB) | [1,1,1,1] = [1,1,1,1] |
| 2 | The script's REPLACEMENTS literal equals the registration's FROM/TO | CONFIRMED (`ast.literal_eval` of the literal == the record's tuple) | prompts.py | True |
| 3 | Every changed character lies inside the four FROM spans | CONFIRMED: 12 difflib opcodes, all inside the spans; 16 characters removed, 12 inserted; the parent prompt with the replacements applied equals the new prompt; a stray edit is caught (mutant M5 KILLED) | prompts.py; mutate.py | - |
| 4 | "final answer" referents go from 4 to 0 | CONFIRMED: regex `final[ _-]*answers?` counts 4 in the old prompt and 0 in the new; **no occurrence of "answer" remains anywhere** in the new prompt | prompts.py | 4 -> 0 |
| 5 | System prompt goes from `058faa54f0697ad9` to `7cee3034d3d93296` | CONFIRMED independently: 2,683 chars to 2,679 chars | prompts.py | exact |
| 6 | RUBRIC_BFCL and SYSTEM_BFCL byte-identical to the parent's | CONFIRMED: the script uses the parent's own objects (`P.SYSTEM_BFCL`, `P.RUBRIC_BFCL`), each occurs once in the new prompt, and at run time they are asserted equal to the pilot run_meta's pinned values (`slots_ok`) | L506, L583 | - |
| 7 | Selftest opens no real DB, makes no network call, posts 0 calls | CONFIRMED BY EXECUTION under an audit hook (raises on sqlite connects outside `*_selftest_*` and on sockets) | `scratchpad/rv/audit_run.py` | 9 connects, all in `%TEMP%\bfcl_final_state_swap_selftest_*`; RC 0 |
| 8 | 50 of 50 declared branches executed | CONFIRMED; the declared set covers C1 (HELD, HELD_QUAL, FAILED, UND, 3 triggers, 3 pre-empts), R2 chip/nochip, UNDERPOWER yes/no/NA, C2-C5, HARM, falsifier x4, P1-P8 (P8 UND), P4(ii). The fence F3-F5, R1 (asserted x3), C2's note and the DECOMPOSITION are text-asserted | selftest output | 50 = 50 |
| 9 | Branch coverage has teeth | CONFIRMED BY MUTATION, 10 of 10 KILLED: interval scored before the triggers; UNUSABLE trigger off; P1 scored on the Delta form; falsifier evaluated under a trigger; stray template edit; R2 off; HARM off; qualified HELD off; go_gate removed; underpower off. The go_gate mutant was killed only because the scratch copy lacks the pool file (see D-S5) | `scratchpad/rv/mutate.py` | - |
| 10 | D2: triggers first; each trigger pre-empts an interval on either side; the falsifier is not evaluated | CONFIRMED BY EXECUTION: the selftest loops 3 triggers x 2 sides through `score_c1`, and the natural `overlap` scenario pre-empts a wholly-below interval. Mutants M1 and M4 are KILLED | L835-879 | - |
| 11 | D3: P1 is scored on T_swap only | CONFIRMED BY EXECUTION: edges 0.10 and 0.20 give HELD, 0.0999 and 0.2001 give FAILED; mutant M3 is KILLED | L1044 | - |
| 12 | Dry-run refuses unless 458 matches, 49 tasks and the pilot's 100/339/19 | CONFIRMED BY EXECUTION: `refusals()` on synthetic contexts, `split_check` stubbed, no DB | `scratchpad/rv/refusals_check.py` | registered -> `[]`; 99/340, 48 tasks and 457 each refused |
| 13 | Leakage: `assert_no_per_side_verdict` on 916 of 916 | CONFIRMED by construction trace (as in the FLIP READY, claim 11). The F2 gate requires 916 of 916 user turns equal to the parent's re-assembly, whose bytes the anchor ties to the 1,216 payloads the post-run review regex-audited (row 7f). The only prompt change is the four strings. The assertion's scope is the task statement only (D-S6) | - | - |
| 14 | Anchor recipe = the post-run review's | CONFIRMED: byte-for-byte the recipe of the review's `one.py` | L548-557 vs `scratchpad/one.py` | - |
| 15 | Go gate (`BFCL_SWAP_GO=11` plus a committed READY) guards every posting path, `--pilot` included | CONFIRMED: `P.post` has 1 call site (L1285), after `go_gate` (L1248); `rr.load_env` is called only there (L1261) | grep | - |
| 16 | DB guard: true connect captured before the parent wraps it; no chaining (D13); pilot cache opened `mode=ro&immutable=1` only; `stack_judge` unreachable | CONFIRMED BY EXECUTION (`scratchpad/rv/modcheck.py`) | - | - |
| 17 | Corpus opened read-only | PARTLY: the guard admits the corpus basename in any mode (`?mode=rwc` passed the guard). The code paths open it `mode=ro&immutable=1` | modcheck | D-S4 |
| 18 | Support: measured level- and delta-DEFF, n_eff and MDE beside every deciding statistic; "UNDERPOWERED FOR ITS OWN BAR" above 3.0 | CONFIRMED as code (`fmt_delta` for dT, dA, dW; `underpower_line`; mutant M10 KILLED) | L820-892 | - |
| 19 | Support section adequate for the bar (registration L12492-L12512) | **REFUTED IN SUBSTANCE**; the arithmetic reproduces (see D-S1) | power script (section C) | - |
| 20 | F1 regex (D4(d)) | CONFIRMED AS ADMISSIBLE: the count is of the artefact as the judge sees it | - | condition 3 |
| 21 | R2 chip on all three deltas (D4(c)) | CONFIRMED: conservative, the same reason applies to every paired delta against a cross-session cache | - | - |
| 22 | No DB of record written | CONFIRMED: 58/58 `*.db*` files identical in sha, mtime and size before and after | - | - |
| 23 | Numpy hygiene | CONFIRMED: 0 `is True` / `is False` | grep | 0 |

## C. D-S1, BLOCKER for READY (registration Support section; zero-call fix)

The registration states "MDE +-0.083 at 80% power", with SE(Delta) = sqrt(0.20 / 458 x 2.0) = 0.0296. That
reproduces, and so do 0.058, 0.0209 / 0.059 and 0.0443 / 0.124. The section then calls the design "ADEQUATE ... it can
distinguish 'the tie rate moved by about 8 points or more' from 'it did not move'".

**That MDE is measured against 0, but C1 decides against the bar -0.05.** HELD needs the interval's upper end below
-0.05, which means Delta-hat below -0.108. FAILED needs the lower end above -0.05, which means Delta-hat above +0.008.
Normal approximation at the registration's own planning values:

| true Delta | P(HELD) | P(FAILED) | P(UNDETERMINED) |
|---|---|---|---|
| -0.133 | 0.80 | 0.00 | 0.20 |
| -0.100 | 0.39 | 0.00 | 0.61 |
| **-0.0683 (P1's point)** | **0.09** | 0.005 | **0.905** |
| -0.05 | 0.025 | 0.025 | 0.95 |
| **0 (no effect)** | 0.00 | **0.39** | 0.61 |
| +0.03 | 0.00 | 0.77 | 0.23 |

- At d = 0.10 with DEFF 2.0: P1's point gives P(HELD) 0.14, and Delta = 0 gives P(FAILED) 0.67.
- At d = 0.30 with DEFF 3.0: P1's point gives 0.06, and Delta = 0 gives 0.20.
- **The 80%-power detectable effect against the bar is Delta <= -0.133 for HELD (T_swap <= 0.085, below P1's whole
  band and near the MMLU-Pro floor 0.074 that P1 says will not be reached) and Delta >= +0.033 for FAILED.**
- Under the registrar's own prediction, the run's most likely outcome is **UNDETERMINED (about 0.9)**.
- n is fixed at 458, the whole deciding set, so no budget can buy more support. The 916 calls buy, most likely, an
  UNDETERMINED plus a direction.
- Minor: the "unpaired MDE +-0.102" is a one-sample figure. A two-sample comparison is +-0.145. It is reference only.

This is the "MDE against the bar" item of the Support gate, and the section's adequacy sentence does not reproduce. The
closed-line ruling (§ "What this ruling does NOT show", item 3) explicitly left the statistics to this review.

**To clear, zero calls, no code change:**

1. The registrar inserts a dated bracket after the Support section that:
   - states the power against the bar (the table above, or its own recomputation);
   - states that P(UND) is about 0.9 at P1's point;
   - notes that n is fixed.
2. The author or experiment-manager records the decision to spend 916 calls on that basis.

Then a re-review of the record only can issue `READY_bfcl_final_state_swap.md` for the unchanged sha
`1c67847de8de2efe`, under conditions 1-5 below. Changing the bar or the statistic after this review is NOT offered as
a fix: that would be a re-registration.

## D. Conditions that will bind the READY once D-S1 is cleared

1. The dry-run, run from the checkout that will post, prints:
   - script LF `1c67847de8de2efe` and parent `5e9db53b894eeccb`;
   - `[F2 GATE] (a) 916 of 916` and anchor `951ec3a0a063b5a8 -> MATCH`;
   - (b) new sha16 `7cee3034d3d93296` beside `058faa54f0697ad9 -> MATCH`, the diff confined, and 'final answer' 4 -> 0;
   - (c) `[1, 1, 1, 1]`;
   - (d) schedule `bcf9d1654e68e4ca` True with SYSTEM_BFCL / RUBRIC_BFCL True;
   - 458 mids over 49 tasks, the pilot 100 / 339 / 19, and `REFUSALS: none`;
   - a last `[DBGUARD]` line that lists only the corpus and the pilot cache as `mode=ro&immutable=1` URIs.
2. `--override-guard` is not used.
3. F1: the dry-run's count of artefact sides naming a 'final answer' must be **0 of 916**. If it is > 0, the premise of
   the ruling (denotation failure) is not total, and the operator stops for the judge-design specialist before the
   pilot. The count of sides carrying a final state is quoted.
4. At `--analyze`, the post-run reviewer prints the usable-only paired Delta interval beside the literal one, and says
   whether C1's verdict differs. With up to 45 unusable calls below the 5% trigger, unusable-as-not-TIE can move Delta
   by up to -0.098, which is larger than the distance to the bar. D4(a) is confirmed as registered, and this is its
   companion.
5. The measured delta-DEFF and P(UND) are reported beside C1 in the outcome, whatever C1 reads.

## E. Other defects (not blocking)

- **D-S2 (MEDIUM):** `refusals()` is not executed by `--selftest`. This review executed it externally (claim 12).
- **D-S3 (MEDIUM):** the go gate checks that the READY exists, not what it says, and does not match the script sha.
  Condition 1 covers this. Fix: `gate_state()` requires the script's LF sha16 inside the READY file.
- **D-S4 (LOW):** the guard does not enforce read-only on the corpus basename.
- **D-S5 (LOW):** the selftest's `launch()` refusal test is live fire behind the gate. In the main checkout, a
  regressed gate would read the real corpus and the pilot cache, stopped only by the 13,990-call night stub. Fix: stub
  `P.post` and `load_context` inside the selftest.
- **D-S6 (LOW):** the leakage assertion's scope is the task statement plus the reference, not the traces. They are
  covered by construction and by the audit that the anchor ties to. Fix: a substring check over the whole user turn.
- **D-S7 (LOW):** posting errors are neither cached nor counted in the night ledger, and the append is not in a
  `finally`.
- **D-S8 (LOW, wording):** under a trigger, the HARM line prints "does not fire" rather than "not evaluated".
- **D-R (LOW, registrar):** hygiene (3)'s `pool_guard --pool p2035adddedd1becb` refuses, because the pool is not in the
  registry. Substitute: `compute_pool_id(judgeable(ids))` over the pool file gives p2035adddedd1becb (228 ids, no DB).

## F. Verdict

**NOT READY**, on D-S1 alone: the Support section's adequacy claim fails against the bar. The instrument code at
`1c67847de8de2efe` is otherwise fit for purpose. Not merged by this reviewer.
