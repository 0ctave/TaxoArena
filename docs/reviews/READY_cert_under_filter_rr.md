# READY re-review: CERT-UNDER-FILTER instrument @ 073f0cc

Reviewer: adversarial-reviewer, 2026-09-23. Zero judge calls. `--run` was NOT executed. No DB of record was written: sha256 and mtime of every input DB are identical before and after (below).
Object: branch `cert-under-filter` @ 073f0cc (parents 02fa49c, 889091d), `tools/analysis/cert_under_filter.py`.
Against: the registrar's rulings on review acd054a (8bbe6ce, programme L14342-L14381) plus everything the previous review (acd054a) read.
Scratch: session scratchpad `cuf_rr/` (tree exported with `git archive 073f0cc`; `selftest.out`, `selftest_O.out`, `dry.out`, `blind.out`, `drive.py`, `mutants.py/.out`, `db_before.txt`, `db_after.txt`).

## VERDICT: READY-WITH-CONDITIONS

All five re-review conditions of 8bbe6ce are MET by execution, with no bypass. The conditions below are for the launch and the record. None requires a code change.

## Identity (pins with their kind)

| pin | kind | value | verified by | result |
|---|---|---|---|---|
| builder's | blob | f7d59019c3d65128687df46aebdcb798b43c3062 | `git rev-parse 073f0cc:<path>`, `git hash-object` (worktree and export) | CONFIRMED |
| builder's | sha256-lf16 | 0db2026f17b559a1 | `git show 073f0cc:<path> \| sha256sum`; `sha256sum` of the worktree file | CONFIRMED (worktree is LF, clean: `git status --short \| wc -l` = 0) |
| reviewer's | sha256-crlf16 | b144a7d4377acfd3 | CRLF rendering of the blob; the script prints the same for a CRLF export | reference only |
| build() source | sha16 of LF source | 128baa007a44a219 | launch check, printed in `dry.out` | CONFIRMED |

## Rule 7

`Get-CimInstance Win32_Process`, checked twice: an idle Gradle daemon, a Kotlin compile daemon, and other agents' mutation runs (`mutate*.py`) in the session scratchpad. No construction, no site null, no Gradle build worker.

## The five conditions of 8bbe6ce

| # | condition | status | evidence and numbers |
|---|---|---|---|
| 1 | Unbypassed `--dry-run`: G1 920/809/26, G2 6,066/9,142 and 5,276/8,352, G3 PASS, with the ONE immutable open in the log | **MET** | See the dry-run section below |
| 2 | D2 NO FIT branches executed and given ids | **MET** | See the D2 branch list below |
| 3 | A fit with \|b1*\| < 1 | **MET** | Case (e): b1* -0.5117, h 0.0001 exactly, I 0.9497, IDENTIFIED. My earlier survivor R2 (h without max(1,.)) is now KILLED by it ("h 5.117e-05 ... = 1e-4 exactly") |
| 4 | The exact witness | **MET** | See the witness section below |
| 5 | Blind real-data pass over all 43 arms | **MET** | See the blind-pass section below |

### Condition 1: the dry-run

Driver `drive.py dry` runs the `__main__` launch sequence unchanged: `check_build_pin`, `check_scipy_brent`, `main_dry(1)`. No guard, hook or function is replaced. Only the four data-path constants are pointed at the main checkout, because the worktree holds no eval DB or snapshots.db: `X12_CACHE`, `rj.EVAL_DB`, `r512.SNAP_DB`, `r512.PROMOTED`.

Before the run the stack cache had no `-wal` and no `-shm` (`db_before.txt`).

`dry.out` shows:
- G2: AGREE 3,076 | DISAGREE 5,276 | missing 790; A keeps 6,066 of 9,142, B keeps 5,276 of 8,352: PASS.
- G1: 920 edges, 809 established, 26 against the key: PASS.
- G3: PASS on 20 draws x 2 conventions.
- One arm build: 14.4 s. Kish mean cluster size 57.92.
- Routed set equals the pool (3,445).
- Connection log: 4 opens, 0 at import. The stack cache appears EXACTLY ONCE, as `file:Z:/.../stack_v2_promptv2_x12all.db?mode=ro&immutable=1`, with 0 refused attempts. The other three opens are pool_guard's eval DB (`mode=ro`) and the eval DB and snapshots.db (both immutable).
- "DRY-RUN COMPLETE: nothing written."

### Condition 2: the D2 branch ids

Selftest hit counts: INNER.BRENT_NOT_CONVERGED 2, INNER.NO_INTERIOR 43, INNER.NONFINITE_SCAN 2, SING.NONFINITE_I 2, C3.NO_FIT_INNER 44, C3.NO_FIT_NONFINITE_I 1, C3.NO_FIT_SINGULAR 133, HYGIENE.STACK_ADMITTED 1, HYGIENE.STACK_REFUSED 10.

The selftest totals are 62/62 branches, under python and python -O (`sys.flags.optimize` 0 / 1).

Case (f) runs all four mappings, each giving NO FIT with P5 UNDETERMINED.

Case (g): all 41 fits of a full readout fail their inner search, the readout still completes, and C1 is unchanged: FAILED, Delta_W +4.35 [+0.95, +7.75], equal to the unfailed readout.

The `[C3-INNER]` and `[C3-INFO]` refusals are gone: `grep -n 'SystemExit("\[C3-' | wc -l` = 0, and the only remaining mentions are the docstring brackets at L180 and L192.

### Condition 4: the witness

`check_witness` requires assessments == fits. The two are counted in different functions (`observed_information` and `c3_fit`), and both are printed. `main_run` requires exactly 3 + 2 x 20 = 43 `c3_fit` calls.

The selftest pins calls 268, fits 215, assessments 215, plateaus 203, and executes three cases: it refuses assessments != fits, refuses 42 of 43 calls, and admits 43 of 43.

My mutant W1 (the equality check disabled) is KILLED.

### Condition 5: the blind pass

Harness `drive.py blind 12`. It calls the instrument's own `load_real` (the one immutable open), `prepare`, `run_arms` and `c3_fit` on the C3 edge sets of each arm: U, F_A, F_B and R_A_01..20, R_B_01..20.

It reads only `inner_how` and the descriptive error estimate through a pass-through wrapper on `observed_information`. The lines are printed without arm names, sorted, and no I, b1, Delta-deviance, event count, branch or status is printed.

`blind.out`:
- **43 of 43 fits, every one `brent/brent/brent`.**
- **0 unresolved, 0 scan paths, 0 plateaus.**
- **Maximum error estimate x4: 2.15e-14.** The minimum is 2.8e-17.
- c3_fit calls 43, fits 43, assessments 43.

This equals the witness `main_run` requires. On the real data the D2 NO FIT path is never taken, so C3 is not degraded by inner failures. The ratio to 16 eps max(1,|l|) is not printed, because printing it would reveal |l|. Under D5 no check applies to it anyway.

## DB state (`db_before.txt` vs `db_after.txt`)

The sha256 values are identical: x12 eb0bec27..., eval 4f65414f..., snapshots 390c313e.... The size and mtime of all three `.db` files are identical, and the stack cache still has no `-wal` and no `-shm`.

The one difference is the mtime of `mmlu_pro_dataset_cache_v2.db-shm` (1790173856 before, 1790174178 after). That is pool_guard's plain `mode=ro` open, the D7 root already queued as POOL-GUARD-IMMUTABLE. The `-wal` is unchanged at 0 bytes.

## The builder's claims

| claim | status | my evidence |
|---|---|---|
| D1: opened once by load_real, immutable, after a -wal check; every other open refused with a named reason; connection_log requires exactly one | CONFIRMED | dry-run log (above). `_load_real_selftest` executes: plain and immutable opens outside load_real, a plain path and a `mode=ro` URI while authorised, a non-empty -wal, and a second load_real. My mutants H1 (URI check off) and H2 (second-open check off) are KILLED |
| D2: InnerUnresolved becomes NO FIT, refusals removed; fixture (g) leaves C1 identical | CONFIRMED | `selftest.out` (g); code diff |
| D5: INNER_MARGIN removed, error descriptive | CONFIRMED | `grep -n INNER_MARGIN \| wc -l` = 1, the docstring bracket at L194 only; the estimate is printed as "(DESCRIPTIVE, no check)" |
| D3: the b1* = -0.5117 fit requires h == 1e-4 | CONFIRMED | (e); R2 killed |
| D6: exact witness 268/215/215/203; --run requires 43 | CONFIRMED | above; the blind pass independently gives 43 calls |
| 62/62 under python and -O | CONFIRMED | `selftest.out`, `selftest_O.out`, rc 0 both, 47-49 s |
| R11 and R15 killed, R2 killed, R6 moot | CONFIRMED | `mutants.out`: R11 "Brent maxiter 2 was resolved ... expected unresolved"; R15 "estimate 0.0, expected (x-3)^2"; R6 has no target left (INNER_MARGIN deleted) |

## The kills by crash (N4, N9, N11): could a real regression of that kind pass silently?

I re-ran each and wrote non-crashing variants of the same class (`mutants.out`).

- **N4 (log rule off).** It dies with `IndexError` on the empty-log case: `st[0]` of an empty list. A real regression of the same kind would NOT always crash. With two opens, or one non-immutable open, the rule-off code returns silently.
  - The selftest still catches both, through its own named checks placed after the crash point. S4a (length-only rule) is KILLED "log with a non-immutable open did not refuse". S4b (presence-only rule) is KILLED "log with two opens did not refuse".
  - So the class is covered by named checks; the crash only reaches them first. HONEST.
- **N9 (InnerUnresolved not caught).** It dies with an uncaught `InnerUnresolved`. In production a regression of this kind would also crash, before the write, so nothing is written. That is loud, not silent.
  - The silent versions of the class are all KILLED by named checks in (f): S9a (swallowed into a non-finite I with `unresolved=None`), S9b (swallowed as I = 1, identified) and S9c (the mapping skipped) all fail "(f) Brent not converged: branch IDENTIFIED status REJECTED".
  - A flat or unresolved fit cannot silently read IDENTIFIED. HONEST.
- **N11 (scan start reverted to plateau).** In my run it is killed by a NAMED check: "(f) Brent not converged: branch IDENTIFIED status REJECTED". It is not a crash.
- **H1 (hook URI check off).** Killed by a crash: `ValueError`, `s.index("?")` on a plain path inside the hook. In production a `mode=ro` URI (which contains "?") would be admitted silently. The named selftest case "authorised, mode=ro URI" stands behind the crash and would refuse it. HONEST, but LOW: the crash hides the named check.

## The builder's own choices

1. **scipy Brent floor as a launch `[PIN]` refusal: admitted as a launch integrity pin; the registrar should record it.** It fires before any data is read or computed, so it can never void a computed C1. It is the same class as R4(a)'s build() pin. It is still a refusal the registration does not name, and D5 said "no registered check beyond the tight convergence already documented".
   - It also reads a private attribute (`scipy.optimize._optimize.Brent._mintol`). A scipy release that renames it would raise `ImportError` or `AttributeError` at launch rather than the named `[PIN]`. That still fails closed.
   - LOW; condition L1 below.
2. **Scan "plateau" now bracketed and solved by Brent: fine.** It changes numerics only on the scan path, which the real data never reaches (0 of 129 inner searches). The selftest still executes the plateau case (203 plateaus).
3. **`_INNER_IMPL` selftest override: acceptable.**
   - `None` at module load; set only inside selftest `try/finally`.
   - `main_run` never sets it. The blind pass ran with it `None` and took the real path (`brent` everywhere).
   - Optional hardening: have `main_run` refuse if `_INNER_IMPL[0] is not None` (LOW).
4. **Cross-drive relpath fix (`_rel`): cosmetic and correct.** It prints the absolute path when relpath fails; the dry-run printed absolute paths.

## Defects (all LOW; none blocks)

- **L1.** Choice 1: the registrar records the scipy launch pin (or strikes it). A fix would catch `ImportError`/`AttributeError` inside `check_scipy_brent` and re-raise the named `[PIN]`.
- **L2.** `main_run` does not assert `_INNER_IMPL[0] is None` (choice 3). It is inert in practice.
- **L3.** The dry-run's wall-time line prints "about 10 min at 1 worker, 10 min at 1 worker(s)", a redundant phrase.
- **L4.** D7 carries over: pool_guard's `mode=ro` open touches the eval DB's `-shm` mtime (queued POOL-GUARD-IMMUTABLE).
- **L5.** D8 carries over: the anchor map comes from bareq512_s42, id-disjoint only; the outcome's record carries the chip, as ruled.

## Conditions (launch and record, no code change required)

1. The registrar records or strikes the scipy Brent launch pin (L1) before `--run`.
2. Run-operator: inside a rule-7 window (no construction or site null), confirm all three `-wal` files are absent or 0 bytes. Run `--run --workers N` from a checkout whose ROOT holds the three DBs of record. The worktree lacks the eval DB and snapshots.db: `--run` from the worktree would fail at the pool guard, which reads through `TAXOARENA_DATA_ROOT`, or at `load_real`.
3. The outcome must print the same witness as the blind pass: 43 c3_fit calls, and fits == assessments. It must also print the connection log with the one immutable open.
4. The post-run review re-measures DEFF from the cluster sizes (planned 1.6, break-even 1.82) and prints n_eff and the MDE beside C1's interval.
