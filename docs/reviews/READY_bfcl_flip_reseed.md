# READY-WITH-CONDITIONS: BFCL-FLIP-RESEED instrument tools/analysis/bfcl_flip_reseed.py at LF sha16 d4e08a891a85b4cd (branch bfcl-separators @ 26ffb1d)

**This version SUPERSEDES the version of this file committed at 29c1e8c**, which reviewed LF `af5bfca08ddccccb` @ e15d2a9.
- Readable with `git show 29c1e8c:docs/reviews/READY_bfcl_flip_reseed.md`.
- That version in turn superseded fdd6a99.
- **Every claim and every condition of 29c1e8c carries forward unchanged to this sha**, except where this file replaces
  one.
- This is a TARGETED re-review of the code diff e15d2a9..26ffb1d, +74/-15 in this file (`git diff --numstat`): the
  fixes for D-G1, D-G2, D-G3 and the usable-only interval.
- Adversarial reviewer, 2026-09-23. Zero calls; no real DB opened; all 58 `*.db*` files have the same sha, mtime and
  size before and after.

## A. Object

- `git show 26ffb1d:tools/analysis/bfcl_flip_reseed.py | sha256sum` gives LF **`d4e08a891a85b4cd`**; blob
  `898bafb5edf1cca45b8197c8a48c34a401f6b374`.
- The worktree file has 0 CR bytes, so its CRLF rendering is the same.
- Parent LF `5e9db53b894eeccb`, unchanged.
- The worktree is clean at 26ffb1d.

## B. Targeted per-claim table (scripts in the reviewer's `scratchpad/rv/`)

| # | claim | verdict | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | D-G1: the sha must be ON the verdict line | CONFIRMED | `named = bool(SCRIPT_SHA in first)` (L348) | - |
| 1a | The remaining `SCRIPT_SHA in text` (L339) cannot open the gate | CONFIRMED | it sits on the no-verdict-line return, which always carries a refusal reason; a no-verdict file naming the sha is REFUSED by execution (case p) | - |
| 2 | D-G1 by execution: the OLD sha on the verdict line and the new sha elsewhere | **REFUSED** | the real `gate_state` / `go_gate` against temp git repos (`gate_attack.py`), case d | - |
| 2a | The new sha only on a 2nd verdict line | **REFUSED** | case d2 | - |
| 3 | D-G2: a verdict only inside a ``` fence, a ~~~ fence, an unclosed fence, or a 4-backtick fence | all **REFUSED** | cases c4-c7 | - |
| 3a | A NOT READY line quoted inside a fence, beside a real READY | OPENS, correctly | case c9 | - |
| 4 | No regression in the earlier attacks | CONFIRMED: another sha, NOT READY, a later NOT READY line, quote block, table, indented block, another test, uncommitted, untracked: all REFUSED; the good file and a CRLF file OPEN | 21 cases for this test | as expected for 20 of 21 |
| 4a | The one unexpected result: a legitimate verdict line preceded by a blank line (e.g. just after a closed fence) | **REFUSED**, a false refusal, fail-closed | see D-G6 | this file's verdict is line 1 and parses: reasons `[]` |
| 5 | Selftest under the audit hook | CONFIRMED | - | **38/38** branches (+3 USABLE); 20 sqlite opens, all in the temp dir; 0 outside; 0 socket/subprocess; RC 0 |
| 6 | Mutation | CONFIRMED: every previously killed mutant still dies. New: D-G1 reverted, D-G2 fence stripping disabled, sha-on-line check removed: all KILLED | `mutate.py`, `mutate_fix.py` | - |
| 6a | Two mutants SURVIVE: N11 (usable-only R computed over ALL matches) and N12 (a label rename) | the selftest drives `usable_line` only on crafted numbers | checked instead by execution (row 7) | - |
| 7 | The usable-only R is printed WITH its interval | CONFIRMED BY EXECUTION on a synthetic set (`usable_check.py`): the printed interval is the R_u interval; its reading is compared with the literal one (SAME / DIFFERS / NA) | 85 usable of 100: `R_u.n` = 85, R_u = 0.6706 = 57/85, literal R = 0.57 | exact |
| 8 | D-G3: the posted-call counter is thread-safe | CONFIRMED by reading: `posted.append(1)` / `len(posted)`. `list.append` is atomic under the GIL. The G5 mutant (count removed) is still KILLED | - | - |

## C. Conditions

Conditions 1, 3, 4 and 5 of 29c1e8c stand. Condition 1's expected script sha now reads **`d4e08a891a85b4cd`**.

- **Condition 2 is replaced:** the gate itself now requires this sha on the verdict line. The `[READY] ... OPEN`
  printout at `--pilot` must show the parsed verdict line naming `d4e08a891a85b4cd`.
- **Condition 4 is replaced:** the instrument now prints the usable-only interval. The post-run reviewer checks it
  against an external recomputation instead of producing it.

## D. Defects (none blocking)

- **D-G6 (LOW, fail-closed):** `VERDICT_RE` opens with `^\s*`, and `\s` spans newlines. A verdict line preceded by a
  blank line (including a blanked fence) therefore parses with an empty "first line" and is REFUSED. This only ever
  refuses; it cannot open the gate. Fix: `^[ \t]*`. The practical rule until then: the verdict must be the first line
  of the READY file, or follow a non-blank line.
- **D-G7 (LOW):** selftest coverage gap. N11 and N12 survive; the correctness of the usable-only interval was
  established by this review's execution, not by the selftest.
- D-G4 (the live-fire `launch` test) is carried forward.

## E. Verdict

**READY-WITH-CONDITIONS** for `tools/analysis/bfcl_flip_reseed.py` at LF sha16 `d4e08a891a85b4cd`. Not merged by this
reviewer.
