# READY — A6 CANARY-ANALYZE-FIX + A9 `--level leaf` (code-only review, 2026-09-23 phase A)

Subject: commit `c3d931b`, merged at `fcd200e`. Reviewed by reading, `git`, `sha256` and grep only.
A construction chain was live: **no** `python tools/analysis/...` was executed (no `--analyze`, no `--selftest`,
no `--dry-run`). Every number below was recomputed by the reviewer's own script against the caches opened
`mode=ro` and against `experiment_results/promoted/bareq512_s42_reserved_leaf_assignments.csv`.

## Verdict per file

| file | verdict | LF sha256[:16] | CRLF sha256[:16] |
|---|---|---|---|
| `tools/analysis/canary_baseline.py` | **READY (conditional)** | `c73a96199d142e30` | `55329b2e4303f776` |
| `tools/analysis/canary_baseline_selftest.py` | **NOT READY (blocker)** | `03ed72e2599f14cd` | `cc14abbe3259c1a2` |
| `tools/analysis/profile_reliability_interaction.py` | **READY (conditional)** | `33cf5f9d72649257` | `56a61d83bea9dd08` |

The READY is **code-only** and is conditional on the phase-B commands below passing. Nothing here authorises a
judge call; both scripts post nothing.

## What was recomputed (reviewer's own script, read-only)

- Convention A from `canary_baseline_pass1.db` / `pass2.db`: contested **13/150 = 0.086667**, cross **13/150**,
  all **26/300**, pairs dropped **0**, bad rows (INVALID or `finish_reason=length`) **0 / 0** — identical to the
  hand-inserted line at `4178a7c`.
- Convention B bootstrap replicated (`random.Random(42)`, 2000 draws): contested SE 0.0247 DEFF 1.16, cross
  0.0230 / 1.00, all **0.0170 / 1.09** — identical to the committed outcome.
- MDE from the measured SE: **3.3pp** at n=300, **1.8pp** at n~1,000, alarm **0.138**, drift **+5.1pp**,
  n~1,000 threshold 0.115 — identical to the coder's claim and to the 4178a7c bracket.
- `ALARM_STATE_NOTE` and `CONV_A_NOTE`: byte-for-byte equal to the two lines of `4178a7c` (compared by
  `ast.literal_eval` of the source constants against `git show 4178a7c:<outcome>`); the state line is
  `ALARM STATE: NO ALARM` at column 0, the note on the next line indented so it cannot be mistaken for it.
- Rule (ii) as registered (programme L3631): `<= 0.114 -> NO ALARM`, above `-> UNDETERMINED`, ALARM never
  emitted, decided on the contested floor under **both** conventions — implemented as registered, fail-closed
  to UNDETERMINED if either convention is missing.
- A9 leaf support, recomputed from the promoted routing CSV joined to the x12 board
  (`stack_v2_promptv2_x12all.db`, 9,142 valid verdicts, 2,811 judged questions, 87 leaves):
  **exactly 1 leaf clears the 120 floor** (`n00000030`, 122 judged questions); 86 leaves are below it holding
  2,689 questions, largest below floor **91**; mean 32.3/leaf. `--level leaf` therefore **refuses**.

## Expected phase-B output

`python tools/analysis/profile_reliability_interaction.py --dry-run --level leaf` must print the 87-row support
table, `ADMISSIBLE LEAVES (>= 120 judged questions): 1` **first**, and exit non-zero with

```
[SUPPORT] UNDETERMINED-by-support: 1 cell(s) carry >= 120 judged questions, fewer than the 2 a (model x cell)
interaction needs; 86 cell(s) are below the floor (largest 91). Nothing is pooled, no R is read and no outcome
file is written.
```

That refusal **is** the honest answer to the leaf question, at zero cost. No `LEAF_OUT` is written.

`python tools/analysis/canary_baseline.py --analyze` (ONCE, after the fixture passes) must change **exactly two
lines** of `experiment_results/x12_crossdomain/canary_baseline_outcome.txt` under `git diff`: the header's own
`script sha256[:16]` and the final MDE line. Caveat: the working-tree file is currently LF, the script writes in
text mode, so on disk every line ending flips to CRLF; check with `git diff -- <path>` (autocrlf normalises) and
not with a byte compare.

## Phase B, in order

```
python tools/analysis/canary_baseline_selftest.py                                   # FAILS as committed - see blocker 1
python tools/analysis/profile_reliability_interaction.py --selftest
python tools/analysis/profile_reliability_interaction.py --selftest --level leaf
python tools/analysis/profile_reliability_interaction.py --dry-run --level leaf     # expected: the refusal above
python tools/analysis/canary_baseline.py --analyze                                  # ONCE, only after the fixture passes
git diff -- experiment_results/x12_crossdomain/canary_baseline_outcome.txt          # expected: 2 lines
```

## Defects, ranked

1. **BLOCKER (fixture)** `canary_baseline_selftest.py::check_conventions_differ` asserts an outcome the script
   cannot produce. The fixture plants 4 pass-1 INVALID rows and 4 pass-2 `finish_reason=length` rows, then
   expects `all       n=292 matches` and `pairs dropped by the script 8`. Convention B in `canary_baseline.py`
   drops only `invalid` rows (`not p1[k]["inv"] and not p2[k]["inv"]`), never non-terminated ones, so the run
   prints **n=296** and **dropped 4**. `find()` raises. Fix the fixture (296 / 4) and add an explicit assertion
   of the asymmetry; do **not** widen convention B, and do **not** relabel `(pass 1 INVALID %d, pass 2 INVALID %d)`
   — that text is part of the verbatim 4178a7c line.
2. **HIGH (record hazard, degraded paths)** the claim "a re-run of `--analyze` cannot wipe what 4178a7c inserted"
   holds only on the complete-cache happy path. Five early returns (`PROTOCOL GUARD`, guard-refused, `not p2`,
   `no paired valid matches`) still call `write()` on `OUT` in mode `"w"` and emit **no** `ALARM STATE` line, so
   they would overwrite the outcome of record and delete both verbatim brackets. Fix: in `write()`, refuse (or
   divert to `OUT_PARTIAL`) when `out_path == OUT` and `"ALARM STATE:"` is not in the text.
3. **MEDIUM (reading rule)** rule (ii) is registered on the floor **read at 3 dp by rule (i)**; the code compares
   the unrounded float (`c["floor"] <= 0.114`). Divergent only on (0.114, 0.1145], and in the conservative
   direction, but it reintroduces exactly the "the script's own comparison is not the reading of record" clause
   that rule (i) had to write for the band. Fix: compare `float("%.3f" % f)`.
4. **MEDIUM (claim)** the "consumer" of this line is not `placement_steps.py:142`: that function reads
   `experiment_results/judge_solve/ref_remint_outcome.txt` (`ARMB_OUT`), ARM-B-VINTAGE's outcome. The canary's
   `ALARM STATE` line has **no** programmatic consumer today; it is format-compatible with that pattern
   (column 0, exact equality against `ALARM STATE: NO ALARM`), which is what was verified.
5. **LOW** the on-disk line endings of the outcome flip LF -> CRLF on the first `--analyze`; two consecutive
   `--analyze` runs are byte-identical (so the fixture's idempotence check cannot see it). Either accept and
   diff through git, or write with `newline="\n"`.
6. **LOW** post-run review defect 5 (three epochs x 300 = 900, threshold 0.116, not "n~1,000") is not addressed;
   it was not claimed.
7. **LOW** `check_no_alarm`'s MDE tolerance `<= 0.06` sits exactly on the worst-case rounding bound
   (0.05 from `%.1f` + 0.0098 from the 4-dp SE); widen to 0.07.
8. **LOW (A9)** the refusal guards `< 2` admissible leaves, but 2 leaves x 12 models = 24 points per halving is
   below `MIN_POINTS = 50`, so a 2-leaf world would write `LEAF_OUT` full of `nan` verdict lines. Unreachable on
   the real data (1 admissible leaf). Suggest refusing when `len(adm) * min(len(models)) < MIN_POINTS`.
9. **LOW (A9)** `leaf_selftest`'s `assert r_int > r_flat + 0.3` is an empirical assertion on synthetic draws;
   deterministic under `RandomState(11)` / `Random(7)` but it is a phase-B failure surface.

## Confirmed as claimed

- Inertness of A9 when `--level` is absent: `git diff -w c3d931b^ c3d931b` removes exactly four lines —
  `r_of(..., min_points=50)` -> `MIN_POINTS` (= 50), `load_record(say)` -> `load_record(say, level="anchor")`,
  the returned dict gaining `undetermined`/`level`, and `selftest(); return`. No anchor print, no `PIN`, no
  `RECORDED_COUNTS`, no `OUT` touched; the leaf path writes only `LEAF_OUT`, write-once, checked twice.
- A9 support rule: inadmissible leaves are DROPPED (`admissible_leaves` returns two disjoint dicts, nothing
  merged into a parent, a sibling or a remainder), the admissible count is printed before any table or R, and a
  leg below `r_of`'s 50-point floor reads UNDETERMINED-by-support rather than a number.
- A6: `--pass` default (`NPASS = 1`), `protocol()`, the payload path, the prompt, the 5% guard arithmetic
  (`unparsed` refactored into `bad_row` with an identical predicate) and the ALARM line's own expression are
  unchanged; the diff touches the docstring, four constants, the conv-A block, the state line and the MDE line
  and nothing else.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G2eTaTRL4d3ohsmSQnuwsE
