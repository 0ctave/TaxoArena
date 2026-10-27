# READY-WITH-CONDITIONS: BFCL-FINAL-STATE-SWAP instrument tools/analysis/bfcl_final_state_swap.py at LF sha16 48a9d23632c107e6 (branch bfcl-separators @ 26ffb1d)

**This version SUPERSEDES the version of this file committed at 09a786a**, which reviewed LF `198e037f10102e0e` @ e15d2a9.
- Readable with `git show 09a786a:docs/reviews/READY_bfcl_final_state_swap.md`.
- That version superseded `NOT_READY_bfcl_final_state_swap.md` (a45cdd8).
- **Every claim and every condition of 09a786a carries forward unchanged to this sha**, except where this file replaces
  one.
- This is a TARGETED re-review of the code diff e15d2a9..26ffb1d, +135/-15 in this file (`git diff --numstat`): the
  fixes for D-G1, D-G2, D-G3 and D-G5.
- Adversarial reviewer, 2026-09-23. Zero calls; no real DB opened; all 58 `*.db*` files have the same sha, mtime and
  size before and after.

## A. Object

- `git show 26ffb1d:tools/analysis/bfcl_final_state_swap.py | sha256sum` gives LF **`48a9d23632c107e6`**; blob
  `ee4fc59583061f276ee395529ab4d15a3a9d8c62`.
- The worktree file has 0 CR bytes, so its CRLF rendering is the same.
- Parent LF `5e9db53b894eeccb`, unchanged.

## B. Targeted per-claim table (scripts in the reviewer's `scratchpad/rv/`)

| # | claim | verdict | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | D-G1: the sha must be ON the verdict line | CONFIRMED | `named = bool(SCRIPT_SHA in first)` (L367) | - |
| 1a | The remaining `SCRIPT_SHA in text` (L358) cannot open the gate | CONFIRMED | it sits on the no-verdict-line return, which always refuses; case p REFUSED by execution | - |
| 2 | D-G1 by execution: the OLD sha `198e037f10102e0e` on the verdict line with the new sha elsewhere, or the new sha only on a 2nd verdict line | both **REFUSED** | `gate_attack.py`: real `gate_state` / `go_gate` against temp git repos | - |
| 3 | D-G2: a verdict only in a ```, ~~~, unclosed or 4-backtick fence | all **REFUSED** | - | - |
| 4 | No regression in the earlier attacks | CONFIRMED | all 21 cases behave as for FLIP, including D-G6 (a false refusal, fail-closed) | this file's verdict line 1 parses: reasons `[]` |
| 5 | **D-G5: C1_RESTATED is the registrar's text VERBATIM** | **CONFIRMED** against 9b046c4 | the only bold span of 9b046c4 section (C), extracted by regex, compared with the literal parsed from the script by `ast` | equal except that the record hard-wraps a line between "registered" and "prediction", where the code has a space; every character otherwise identical |
| 6 | **D-G5: the power numbers equal L13527-L13574** | CONFIRMED | my own normal recomputation, and the selftest's assertion at the printed digit | HELD Δ̂ < −0.1079; FAILED > +0.0079; P1 0.090 / 0.005 / 0.905; Δ = 0 FAILED 0.394; 80% at ≤ −0.1328 / ≥ +0.0328 |
| 7 | **The power is RECOMPUTED at the MEASURED SE**, not only printed at the planning 0.02955 | CONFIRMED BY EXECUTION on a synthetic cache (`usable_check.py`) | `power_lines` prints three lines: the record's table (a quoted constant), a line recomputed at the planning SE, and a line recomputed at `s["dT"]["sd"]` (the bootstrap SE of the paired Δ). A REALISED line gives P(HELD / FAILED / UND) at the observed Δ̂ and the measured SE | synthetic: measured SE 0.00725 moves the thresholds to −0.0642 / −0.0358 |
| 8 | D-G5: the usable-only Δ is printed WITH its interval | CONFIRMED BY EXECUTION | `bt_u`, L848, keeps only usable matches. Synthetic: 50 unusable non-tie matches, 23 ties converted: `dTu.n` = 408 = usable, Δ_u = −23/408 = −0.0564 against the literal −23/458 = −0.0502, and the printed interval is the `dTu` interval | exact |
| 9 | Selftest under the audit hook | CONFIRMED | - | **58/58** branches (+4 POWER, +3 USABLE); 21 sqlite opens, all in the temp dir; 0 outside; 0 socket/subprocess; RC 0 |
| 10 | Mutation | CONFIRMED | all previously killed mutants still die. New and KILLED: D-G1 reverted; fence stripping disabled; sha-on-line check removed; power at the measured SE removed; the realised P(UND) line removed; the power threshold made wrong (1.645); the usable-only DIFFERS branch never taken | - |
| 10a | Two mutants SURVIVE | the selftest does not cover them | N5: the usable-only interval computed over ALL matches (checked instead by row 8). N6: C1_RESTATED altered, because the selftest compares the constant with itself (checked instead by row 5). Both are pinned by this sha | D-G7 |

## C. Conditions

Conditions 1, 3 and 5 of 09a786a stand. Condition 1's expected script sha now reads **`48a9d23632c107e6`**.

- **Condition 2 is replaced:** the gate now requires this sha on the verdict line. The `[READY] ... OPEN` printout at
  `--pilot` must show the parsed verdict line naming `48a9d23632c107e6`.
- **Condition 4 is replaced:** the instrument now prints C1_RESTATED verbatim, the power table of record, the power
  recomputed at the planning and at the measured SE, the realised P(UNDETERMINED), and the usable-only Δ with its
  interval and a SAME / DIFFERS reading. The post-run reviewer recomputes these from the cache and checks them. The
  registrar quotes them beside C1.
- **New:** the "REALISED" probabilities treat the observed Δ̂ as the true Δ (observed power). They describe the design;
  they are not evidence about Δ. The outcome must not narrate them as such.

## D. Defects (none blocking)

- **D-G6 (LOW, fail-closed):** `^\s*` spans blank lines, so a verdict line preceded by a blank line is refused. Fix:
  `^[ \t]*`. The verdict must be the first line of a READY file, or follow a non-blank line.
- **D-G7 (LOW):** mutants N5 and N6 survive the selftest (row 10a). Both were verified by this review's execution.
  Suggested test: assert `C1_RESTATED == " ".join(<record text>.split())` using a hard-coded copy of the record text,
  and assert `dTu.n == usable` in the und_trigger scenario.
- D-G4 is carried forward.

## E. Verdict

**READY-WITH-CONDITIONS** for `tools/analysis/bfcl_final_state_swap.py` at LF sha16 `48a9d23632c107e6`. Not merged by
this reviewer.
