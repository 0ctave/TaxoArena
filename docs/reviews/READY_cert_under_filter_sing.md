# READY review: CERT-UNDER-FILTER instrument, singular-information build (889091d)

Reviewer: adversarial-reviewer, 2026-09-23. Zero judge calls. No DB of record written; DB sha256 and mtimes identical before and after (below).
Object: branch `cert-under-filter` @ 889091d, `tools/analysis/cert_under_filter.py` (2,107 lines).
Against: registration 88a95d8 (programme L13229-L13360); rulings R1-R6 (8469780, L13576-L13642); the separation ruling (c669926, L13883-L13923); the singular-information ruling (0ce8460, L14034-L14069, read with `git show 0ce8460:docs/judge_v2_program.md`). No earlier READY exists for this instrument: `grep -l -i cert_under_filter docs/reviews/*` returns 3 files and none is a READY for it.
Scratch: session scratchpad `cuf_ready/` (tree exported with `git archive 889091d`; `selftest*.out`, `dry.out`, `dry_bypass.out`, `mutants.py/.out`, `mutants2.out`, `kink.py`).

## VERDICT: NOT-READY

One BLOCKER: the instrument refuses to open its own verdict cache, so `--dry-run` and `--run` can never get past `load_real`. It has been in the code since 4cd0bfa. It went unseen because no build ran `--dry-run`, and the selftest counts the refusal as a pass (D1). Before the next READY, the registrar must re-rule R3(iii) and rule on choices 1 and 4.

## Identity (pins with their kind)

| pin | kind | value | verified by | result |
|---|---|---|---|---|
| builder's | blob | 11c9435f20bce1db6332c2d2b62dc7c572b6ee29 | `git hash-object` + `git rev-parse 889091d:tools/analysis/cert_under_filter.py` | CONFIRMED |
| builder's | sha256-lf16 | d371597bae00eb18 | `sha256sum` of the working tree file and of `git show HEAD:<path>` | CONFIRMED (the worktree file is LF) |
| reviewer's | sha256-crlf16 | ffd48c9fa61282b8 | `git show HEAD:<path> \| sed 's/$/\r/' \| sha256sum`; the script prints the same value for a CRLF checkout | for reference only; the worktree is LF |
| build() source (R4(a)) | sha16 of LF source text | 128baa007a44a219 | printed and compared by the launch check (`dry_bypass.out`) | CONFIRMED |

## Rule-7 state

`Get-CimInstance Win32_Process` at 15:26 showed: an idle Gradle daemon (started 11:35), a Kotlin compile daemon (14:10), and 2 python processes from another agent's vote_frame mutation run in the session scratchpad. No construction, no site null, no Gradle worker running a build. The pool DB `-wal` files were 0 bytes or absent before any open.

## Per-claim table

| # | claim | status | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | selftest passes, 53/53 branches, under python and python -O | CONFIRMED | `python tools/analysis/cert_under_filter.py --selftest` in the exported tree, and again with `-O`; rc 0 both; 44 s each | 53 of 53, both runs; `sys.flags.optimize` 0 / 1 printed; `grep -c -E "^\s*assert\b"` = 0 | - |
| 2 | (a) flat +720 case: I = -0 exactly, UNIDENTIFIED via I <= 0 | CONFIRMED | selftest.out L270, L276 | b1* +720.5276, ddev 1.0602, I -0, h 0.0720528 (= 1e-4 x 720.5276), l -6.402525571, bound 2.275e-14 (mine 2.2746e-14); A(wrong) 0.3821-0.6341 and A(right) 0.3197-0.6400 overlap; P5 UNDETERMINED "1.06 descriptive" | - |
| 3 | (b) b1 +5.39 IDENTIFIED, I h^2 is 2.09e5 x the bound | CONFIRMED | selftest.out L272, L277; recomputed | I 0.169759, h 0.000538922, l -66.55563058; I h^2 4.9304e-08, bound 2.3645e-13, ratio 208,516 | - |
| 4 | (c) separation is named, and the singular check also fires | CONFIRMED | selftest.out L274, L278 | b1* +20.3771, I -0 -> "I <= 0", status "NO FIT (b1 unidentified: complete separation in A: max A(wrong) 0.5962 <= min A(right) 0.6047)" | - |
| 5 | (d) classifier boundary cases | CONFIRMED, not a tautology | `mutants2.py`: SING_FACTOR set to 0 / 15 / 17 WITH the bound-pin line neutralised | all three KILLED by the crafted cases alone: 8x and 16x must read ROUNDOFF, 17x must read not-singular, so the boundary is tested from both sides; the neutralised control (16) passes | - |
| 6 | mutant (i), singular branch dropped: killed | CONFIRMED | `mutants.py` B1 | KILLED ("CheckFailed: DISAGREE", favourable-fixture U check) | - |
| 7 | mutant (ii), SING_FACTOR 16 -> 0: killed | CONFIRMED; the kill is honest | B2 KILLED by the bound-equality pin first; with the pin removed it is KILLED by (d) (row 5) | the bound-equality line is a pin (it recomputes the constant from the ruling's literals), not a behavioural test; (d) is the behavioural kill and it is sufficient, as shown for 0, 15 and 17 | - |
| 8 | the execution witness (SING_EVALS > 0) in main_run is compared | PARTLY | L1536-L1537: `if not bool(SING_EVALS[0] > 0): raise SystemExit` | it is compared, but (1) it is only ever reached by a successful --run, which D1 makes impossible, so it has never executed, and (2) `> 0` would pass with 1 of the 43 expected fits; the selftest copy (L2072) is redundant: mutant R12 removes it and survives | LOW (D6) |
| 9 | criteria, bars, denominators unchanged since 0f44893 | CONFIRMED | `git diff 0f44893 889091d` touches 1 file (+351 / -49); a grep of the diff for PINS/PLAN/U_REF/thresholds/prediction bounds/`c1_verdict` returns 0 lines; the 49 deleted lines are the old descriptive curvature print, the old R-draw data check and the CONFLICT print | none changed | - |
| 10 | Support (registration (a)-(f)) arithmetic | CONFIRMED | my own python | SE 4.24 x sqrt(1.6) = 5.363 (5.37); MDE 15.02; pessimistic 7.344 / 20.56; break-even (16 / 11.872)^2 = 1.816; DEFF transport (2.2716 / 1.8592)^2 = 1.493 and (2.2716 / 1.7903)^2 = 1.610; dry-run cluster sizes 59/57/58/59/57/53/54/53/58/63/58/59/61/60: mean 57.79, Kish 57.92. Measured DEFF, n_eff and MDE are printed beside the deciding statistic (L882-L885) | - |
| 11 | dry-run is read-only by design | CONFIRMED for DB content | DB sha256 before and after identical (x12 eb0bec27..., eval 4f65414f..., snapshots 390c313e...); mtimes unchanged | see D7: pool_guard's mode=ro open left a 0-byte `-wal` and a `-shm` beside the eval DB; content is unchanged | LOW |
| 12 | the dry-run runs | REFUTED | `drive_dry.py dry` (the instrument's `main_dry` with DB paths pointed at the main checkout, since the worktree has no eval DB or snapshots.db) | `[HYGIENE] refused to open the stack cache file:Z:/.../stack_v2_promptv2_x12all.db?mode=ro&immutable=1`: the instrument refuses the verdict cache it must read | BLOCKER (D1) |

With a reviewer-side bypass of D1 (`cuf.ro` sent through the real connect, dry mode only, `dry_bypass.out`), G1-G3 reproduce the record: G2 6,066 / 9,142 (A) and 5,276 / 8,352 (B); G1 920 edges / 809 established / 26 wrong; G3 PASS on 20 x 2 draws; one arm build 13.5 s wall. The run then refuses again in `connection_log()`, because the stack cache appears in the log. That is D1 a second time. My next step, a blind real-data fit of all 43 arms to size the [C3-INNER] risk, also needed the bypass. The permission classifier denied it and I did not work around the denial. **The real-data inner-refusal risk (choice 1) is UNDETERMINED.**

## Reviewer mutants (selftest under python; KILLED iff rc != 0; `mutants.out`)

| mutant | result |
|---|---|
| R1 sign flip on I | KILLED |
| R2 h = 1e-4 x \|b1*\| (max(1,.) dropped) | **SURVIVED** (D3) |
| R3 / R3b classifier uses l or \|l\| instead of max(1,\|l\|) | KILLED / KILLED |
| R3c scale = l0 in observed_information | KILLED (by a [C3-INNER] refusal) |
| R4 singular check skipped when the fit is not separated | KILLED |
| R5 bootstrap run on an unidentified fit | KILLED |
| R6 inner-margin refusal disabled | **SURVIVED** (D4) |
| R7 `I < 0` instead of `I <= 0` | KILLED (case (a) is -0.0) |
| R8 no profile (b0 fixed at the optimiser's value) | KILLED (case (b) I 2.52 vs ~0.17) |
| R9 P5 scored on a NO FIT | KILLED (reads HELD) |
| R10 printed bound uses 8 instead of 16 | KILLED (pin) |
| R11 non-converged Brent accepted | **SURVIVED** (D4) |
| R12 selftest witness removed | SURVIVED (redundant check, D6) |
| R13 SINGULAR named over SEPARATION | KILLED |
| R14 INFO_STEP 1e-3 | KILLED (pin) |
| R15 inner error estimate forced to 0 | **SURVIVED** (D4) |

Flat-reads-IDENTIFIED probe (`kink.py`). I moved each of the 10 edges of the +720 fixture into the tau transition band at 5 offsets and refitted: 50 of 50 read SINGULAR, 0 read IDENTIFIED. The test is local by construction, so a runaway optimiser whose b1* sits where an edge crosses the band could still read IDENTIFIED. This was not observed; it is a limit of the ruling, not a builder defect.

## Defects

**D1. BLOCKER. The instrument refuses its own verdict cache.** `_logged_connect` (L231-L238) raises SystemExit on any path containing `stack_v2_promptv2_x12all.db`. `connection_log()` (L1489-L1491) refuses the same name. But `X12_CACHE` (L346) is that file. It is the cache the registration says the instrument "MAY READ, mode=ro&immutable=1" ("the cache systematic_budget.py reads"; systematic_budget L86-L87 sets `PROMPT = "v2"; ALL_X12 = True`, which resolves to `stack_v2_promptv2_x12all.db`). `load_real` (L500) therefore always refuses. Git history: `grep -c 'if STACK_CACHE_NAME in s'` = 0 at 4946646 and 1 at 4cd0bfa, 0f44893, cb20fc0, 3516626 and 889091d.
- Source: R3(iii) says, literally, "the stack cache (stack_v2_promptv2_x12all.db) is never opened". That contradicts the registration's permitted read; its intent was that the file is never opened by stack_judge / read-write.
- The selftest line "a stack-cache open is refused and absent from the log" passes because it proves the instrument cannot do its job. This is the vacuity class.
- Fix: a registrar re-ruling of R3(iii) ("never opened except once, by load_real, as `file:<path>?mode=ro&immutable=1`; any other open refuses"). The code then refuses only non-matching opens, and connection_log applies the same rule. The selftest executes `load_real` on a synthetic `stack_v2_promptv2_x12all.db` in the tempdir: the immutable URI must be admitted and a plain `sqlite3.connect(path)` must be refused.
- Condition for the next READY: an unbypassed `--dry-run` on the DBs of record, printing G1-G3 PASS and the connection log.

**D2. HIGH (needs a ruling). An unregistered refusal gate on a descriptive leg, [C3-INNER] / [C3-INFO].** A failed inner re-maximisation, a scan that never finds an interior optimum, an inner error above 12 eps max(1,|l|), or a non-finite I raises SystemExit inside `c3_fit`. That happens after C1 is computed, so the whole outcome is voided, including C1, the only barred endpoint.
- Exposure: 43 fits (U, F_A, F_B, 40 R draws) x 3 inner searches each.
- R2 (8469780) holds that which triggers and gates exist is registered, never inferred by a builder.
- R1(b) already registers what a fit that does not converge means: "if no ddev can be computed (the fit does not converge, or b1 is unidentified), P5 is UNDETERMINED". So the registered consequence is NO FIT / UNDETERMINED, not a refusal.
- Fix (recommended for the ruling): an inner failure makes that fit "NO FIT (b1 unidentified: inner re-maximisation not resolved: <reason>)". It is printed, P5 reads UNDETERMINED if it is F's fit, and C1 is unaffected. Otherwise the registrar registers [C3-INNER] as a gate knowing it can void C1.
- The real-data frequency is UNDETERMINED (see above). The selftest resolved 203 inner searches as "plateau" on the synthetic fixtures.

**D3. MEDIUM. The h = 1e-4 x max(1,|b1*|) floor is untested.** Mutant R2 survives. Every selftest fit has |b1*| >= 5.39 (a 720.5, b 5.39, c 20.4), so the h pin (L1799) cannot tell `max(1,|b1*|)` from `|b1*|`. On an R draw or F with |b1*| < 1 the mutant makes h smaller and pushes fits toward ROUNDOFF-singular.
- Fix: add a fit with |b1*| < 1 (for example the overlap generator with a slope near 0.5) and require h == 1e-4 exactly.

**D4. MEDIUM. The inner-search guard paths are not executed by the selftest.** Mutants R6 (margin refusal off), R11 (non-converged Brent accepted) and R15 (error estimate forced to 0) survive. None of these refusals is a registered branch id, so "53 of 53" does not cover them.
- Fix, if D2 keeps any of them: register branch ids and execute each on a crafted objective (a Brent result with success False; an objective whose g^2/(2c) exceeds 12 eps). If D2 maps them to NO FIT, execute that mapping instead.

**D5. MEDIUM (needs a ruling). INNER_MARGIN = 12 is the builder's constant, not the ruling's.** The ruling says "16 is that bound [4 eps |l|] times a 4x margin for the error of the inner re-maximisation": a multiplicative 4 x 4. It registers no check on the inner error; the margin absorbs it. The builder reads it additively (16 - 4 = 12 eps left for 4 x max inner error) and turns that reading into a refusal (D2). The reading is arithmetically defensible, but it is an unregistered constant. It is also decoupled: if the registrar changes 16, INNER_MARGIN does not follow.
- Fix: the registrar either admits it (with its decoupling) or rules that the inner error is printed and not gated, which follows D2's recommendation.

**D6. LOW. The execution witness is weak and has never executed.** `SING_EVALS > 0` (L1536) would pass with 1 of 43 fits, and main_run is never exercised (D1).
- Fix: require SING_EVALS == the number of `c3_fit` calls with a fit, counted independently. Print both.

**D7. LOW. Disclosure: WAL sidecars.** During my dry-run window a 0-byte `mmlu_pro_dataset_cache_v2.db-wal` (15:30:29) and a 32 KB `-shm` (15:30:36) appeared. Before, none existed (`ls` at 15:26). The DB is in WAL mode (header bytes 18-19 = 2, 2). The files are consistent with `pool_guard.open_ro` (mode=ro, not immutable). The instrument's own opens are immutable. Content is unchanged (sha256 identical). The empty `-wal` is admitted by R6. I left the files in place; SQLite removes them on the next read-write close. [RESOLVED 2026-09-23 by the registrar: POOL-GUARD-IMMUTABLE MERGED at d30c19e (pool_guard.py blob:6521b51ac0fce04063563f9e6dcf42554ad86591 / sha256-lf16:8ca50c0fba9b8ce3 / sha256-crlf16:5c528e083c4120d2); open_ro now opens mode=ro&immutable=1 and moves no -shm or -wal (reviews d72c790 claim 1d, cc0ccc9 R3); docs/judge_v2_program.md L14591-L14599.]

**D8. LOW. Note, not a defect of this build.** The anchor map comes from `bareq512_s42`, which CONTENT-DISJOINT-SPLIT-AUDIT (6f24e04; CONTEXT §3 bracket) now records as id-disjoint only. The registrar may want the outcome to carry that bracket.

## Builder choices 1-4

| choice | ruling | needs registrar? |
|---|---|---|
| 1. Inner b0 re-maximisation (Brent xtol 1e-12, plateau scan, g^2/(2c), [C3-INNER] refusals) | The numerics are reasonable: mutant R8 shows the profile matters (I 2.52 without it vs 0.17). The refusals are an unregistered gate on a descriptive leg that can void C1, and R1(b) already names the registered consequence of non-convergence (UNDETERMINED). Real-data risk UNDETERMINED (bypass denied). See D2 and D4. | **YES** |
| 2. "On every arm": all R draws fitted, descriptive | Within the registration. The separation ruling says "It applies on every arm (U, F, each R draw) and under each convention" (L13883 section), and the singular ruling (C) says "on every arm and under each convention". The singular test needs a fit, so fitting the R draws follows. Its cost is the 40-fold exposure to D2's refusals. | no (resolved by the D2 ruling) |
| 3. Both fire -> separation named | Consistent with "detected on the data before any fit". It does not change the outcome: both are NO FIT, P5 is UNDETERMINED either way, and the singular reading is printed beside the fit (info_line). Mutant R13 is killed. | no (record as a reading) |
| 4. INNER_MARGIN = 12 (16 - 4) | Not the ruling's arithmetic (4 x 4, multiplicative, no gate). It is a builder constant turned into a refusal. See D5. | **YES** |

## Conditions for the re-review

1. Registrar re-rules R3(iii) (D1); the code fix and its selftest land. An unbypassed `--dry-run` on the DBs of record reproduces G1 920/809/26, G2 6,066/9,142 and 5,276/8,352, G3 PASS, and prints the connection log with the one immutable open.
2. Registrar rules on choices 1 and 4 (D2, D5). The code implements the ruling, and each resulting branch (refusal or NO FIT mapping) is executed by the selftest (D4).
3. The selftest gains a |b1*| < 1 fit that kills mutant R2 (D3).
4. The witness counts fits exactly (D6).
5. A dry-run extension or a reviewer pass fits U, F_A, F_B and the 40 R draws blind (inner path and margin only) on real data, so the choice-1 risk is measured before --run.
