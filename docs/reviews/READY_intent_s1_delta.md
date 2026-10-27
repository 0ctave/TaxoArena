# Delta READY review: INTENT-TRANSFER-S1 readout fixes (branch intent-s1-fix, tip 3e9eedde, from main f6485dee). Zero calls.

Reviewer: adversarial-reviewer, 2026-10-02. Prior review: docs/reviews/READY_intent_s1.md (B-1, B-2, C-3, D-4..D-8). What
that review CONFIRMED on unchanged code is not re-derived here. Registrar ruling: a5c3e02a (prog L22693 bracket; record
L23794-L23799).
Scope: `git diff --name-only f6485dee 3e9eedde` = exactly 1 file (counted with `wc -l`):
tools/analysis/intent_transfer_s1.py. The exporter, configs and Kotlin are untouched.
Pin: `blob:4e9d9d05fbdf14d0a85966b4c897cfbfd779186d` (git hash-object = HEAD tree entry), `sha256-lf16:1ee80b09a00075da`.
The worktree rendering is byte-identical (CRLF = LF).
Machine: the 9 S1 builds are running. No snapshots.db / embeddings_cache.db read and no Gradle in this review; selftests and
mutants only.

## Verdict

**`--run` READY** (blob 4e9d9d05), under C-1..C-3. **I accept the builder's M-AF-only reading of the reproduction check**
(ruling below). The open items are a registrar bracket and LOW fixes; none is a blocker.

## Per-claim table

| # | Claim | Finding | Status | Sev |
|---|---|---|---|---|
| 1 | B-1: a NaN Mantel r gives NOT EVALUABLE, with the probe as a selftest | `mantel()` returns (r, nan) when r is not finite; `t_c4_verdict` returns NOT EVALUABLE when p is non-finite on either corpus. Selftest cases cover constant distance and constant counts on either corpus. My N2 (NaN checked on MASSIVE only) is KILLED | CONFIRMED | - |
| 2 | B-2 per a5c3e02a: floor at K = 60, ceiling = supervised TRAIN-centroid stability, 3-dp reproduction or refuse | floor = `cofile_floor(A, S0.skmeans(X[tr60], 60, 0), n)` through fit_idx (TRAIN only). This is the same construction as S0's c4() (`km_fit` = skmeans on S_idx TRAIN rows at the slice, seed 0; same SEED_COFILE pair draw). The ceiling expression is identical to S0's `cent`. The refusal compares `(round(c,3), round(f,3))` with (0.834, 0.692). The disclosed exception is printed in the T-C7 line | CONFIRMED | - |
| 3 | The check binds M-AF only; M-AF-s2 and M-AF-g print unchecked | Ruling below: ACCEPTED. But `desc_text` prints only D7 and the verdict for M-AF-s2 / M-AF-g, not their ceiling, floor or delta, and does not label them "unchecked" (D-2) | PARTLY | LOW |
| 4 | D-4: block parsing with refusal; port-parity needs every vector | `parse_diagnostics_full` + refusal when parsed blocks != `"\nTrue Domain:` markers. A garbled block makes the lazy match span two markers and the count check refuses (fail-closed). port_parity refuses unless every distinct query has a vector. My N3 (half coverage admitted) is KILLED | CONFIRMED | - |
| 5 | D-5: the 4 survivors die | My MY-3, MY-4, MY-5 and MY-8, re-run against the FULL selftest, are all KILLED; MY-1 (D-7) is KILLED too | CONFIRMED | - |
| 6 | selftest 151, mutants 72/72 | `--selftest` 151 checks OK; `--mutants` 72 of 72 KILLED, 0 SURVIVED (counted) | CONFIRMED | - |
| 7 | No new EVAL path before the GATE freeze | the only new fit is `tr60` = the arm's TRAIN through fit_idx; it runs inside t_c7, after the freeze, and reads no EVAL label for the fit | CONFIRMED | - |

## Ruling on the M-AF-only reproduction reading

The bracket says "the qwen3-256 AF arms must reproduce 0.834 / 0.692". Only M-AF and M-AF-s2 compute T-C7 at qwen3 256.
M-AF', M-o1 and M-o2 compute none, C-AF has no variants, and M-AF-g is gemma at 768. Both ends of delta depend only on the
TRAIN set, the slice and the embedder, never on the tree. S0's 0.834 / 0.692 were measured on the salt-1 TRAIN. M-AF-s2's
salt-2 TRAIN differs (1,413 items out, 1,435 in), so its ends are not expected to reproduce S0. A literal check would make
the run refuse on a descriptive arm by construction: an unreachable precondition, not a guard. **M-AF is the only arm on
which the identity is defined, so the M-AF-only reading is the correct one.** The registrar records this narrowing by
insertion (C-1). It moves no criterion: T-C7 is decided on M-AF only, and M-AF-s2's rows are registered descriptive.

## Conditions and defects

- **C-1 (registrar).** Bracket the narrowing above at L22693: "the qwen3-256 AF arms" = M-AF; M-AF-s2 and M-AF-g print
  their ends, unchecked, descriptive.
- **C-2 (operator, LOW).** The reproduction check first runs inside `--run`. `--dry-run` computes no k-means, so a
  mismatch can only show up late. A refusal there is a failed precondition (nothing is written, write-once intact), not
  an outcome. The rows S1 reads come from S0's float32 big-endian vectors through the same S0.unit and skmeans, so I
  expect exact reproduction. I did not compute it: the brief excluded non-selftest runs while the builds run.
- **D-1 (LOW, test gap).** My mutant N1 (reproduction tolerance 0.01 instead of 3 dp) SURVIVES. No case pins the 3-dp rule
  against a near miss. FIX: a fixture case with the installed values off by 0.002 must refuse.
- **D-2 (LOW, render).** In desc_text, print ceiling, floor and delta for M-AF-s2 / M-AF-g with "(B-2 reproduction not
  checked: salt-2 TRAIN / gemma 768)", as the docstring states.
- **D-3 (LOW, scoring).** P8 (`prob("P8", "T-C4 HELD", 0.65, V["T-C4"] == "HELD")`) scores a NOT EVALUABLE T-C4 as a miss.
  FIX: print P8 as NOT SCORED when T-C4 is NOT EVALUABLE (or the registrar adopts the miss convention by bracket).
- Carried from READY_intent_s1, unchanged: D-6 (the profiles filter is guarded by the >= 99.9% acceptance; now in the
  docstring) and D-8 (exporter cosmetics).

## Own mutants (delta; full selftest each)

MY-1 residual always on: KILLED · MY-3: KILLED · MY-4 floor seed 1: KILLED (the reproduction refusal) · MY-5: KILLED ·
MY-8: KILLED · N1 3-dp tolerance -> 0.01: SURVIVED (D-1, not decisive at S0's values) · N2 NaN p on MASSIVE only:
KILLED · N3 port parity at half coverage: KILLED.

## Commands

```
git diff --name-only f6485dee 3e9eedde | wc -l          # 1
git ls-tree intent-s1-fix tools/analysis/intent_transfer_s1.py ; git hash-object <worktree file> ; sha256sum (HEAD vs worktree)
git diff f3e46394 intent-s1-fix -- tools/analysis/intent_transfer_s1.py
python tools/analysis/intent_transfer_s1.py --selftest   # 151 OK      (worktree intent-s1-fix)
python tools/analysis/intent_transfer_s1.py --mutants    # 72 of 72 KILLED
python <scratchpad>/is1/mymut2.py                        # MY-1/3/4/5/8, N1-N3, full selftest per mutant
sed -n '22693p' docs/judge_v2_program.md                 # the B-2 bracket
```
