# READY delta 1: LCB-D9B-BYTE-INERTNESS (2026-09-25, zero calls; follows READY_lcb_d9b.md at d984724)

## VERDICT: READY. B1 is closed by R5. D3 and D2 are fixed. The step list of record is S0'-S12 of READY_lcb_d9b.md, with the S0' pins replaced by the table below.

Scope: the diffs of d9b_aux.py and d9b_compare.py against their `*_r4` copies (the files pinned at d984724), the tests, and my mutants. Nothing else moved:
- d9b_prep.py is still 8cc3eb84...;
- every d9\ pin is unchanged: d9_legrun.cmd e986bb84 (CRLF bytes), d9_leg_check_v2.py b2d1ae8d, probe_lcb.toml 617bd50b, pins.py 8dd4dfd9, w1.ps1 0f68ce4b;
- d9b_compare_r4.py, d9b_aux_r4.py, run_tests_r4.py and run_tests_r4.out are byte-identical to the d984724 pins (c1e0dc17, 28200e47, 25384450, crlf 43872960 / lf a4215dfe).

## Per-claim table

| # | claim | status | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | d9b_compare.py changes only by D3 (docstring, load_readout, one call site) | CONFIRMED | `diff d9b_compare_r4.py d9b_compare.py` | 3 hunks: docstring L49-L50; `load_readout` (catches OSError / ValueError and checks the shape, both as Refuse, so exit 2); the call site L385. No drop list, mapping or P6 line changed | - |
| 2 | d9b_aux.py changes only by R5 | CONFIRMED | `diff d9b_aux_r4.py d9b_aux.py` | docstring; `norm_path`; `parse_sums`; v10's hash test is now `sums.get("classlists/leg<L>_<id>.txt") == own sha256 and not in conflict`, with an ABSENT / WRONG / LISTED TWICE state printed per list; classlists and v11 untouched | - |
| 3 | norm_path cannot make two lists collide | CONFIRMED | python over `X.LEGS x (X.IDS + ("all",))`, lower-cased | 15 keys, 15 distinct (lega_ vs lega2_; the four ids differ after lower-casing) | - |
| 4 | a list hashed under another path cannot pass | CONFIRMED | norm_path on 9 renderings (my script); T17i; mutant M13 | `./a2/classlists/legA_all.txt` -> `a2/classlists/lega_all.txt`; `evidence_A2/...` stays prefixed; another stage prefix (`C:\T\run2\...`) is not stripped; `classlists/../classlists/...` is not collapsed, so it reads ABSENT (fail-closed); only the stage's own prefix, `*` and `./` are stripped | - |
| 5 | B1 case now NOT MET | CONFIRMED | T17e and T17j (a copy of my `rev_d9b\harness\v10st`) | 11 ABSENT, V10 NOT MET, rc 1 | - |
| 6 | run_tests.py: 132 of 132 | CONFIRMED | isolated copy `$SPR\rev_d9b\harness2\` (the 4 .py files; copies of the evidence, pool copies, misses, A' pseudoroot, probe TOML and v10st fixture) | "132 of 132 cases as expected; 0 mismatches"; the case-id list equals the builder's run_tests.out | - |
| 7 | my surviving mutants and new ones | 6 of 7 killed | `$SPR\rev_d9b\harness2\mut3.py` | M1 (+RoutingECE) killed by T19a / T19b; M6 (+mass) by T19a / T19c; M9 (set compare) by T19h; M11 (R5 reverted to presence) by T17e / g / h; M13 (norm_path reduces to basename) by T17i; M14 (D3 reverted) by T18 (crash). **M12 (conflict check removed) SURVIVES 132/132** | LOW (E1) |
| 8 | builder's mutation evidence | CONFIRMED (read) | `$SPR\d9b_mutants.out` (file bytes da32f935..., LF 6eb455e1...) | 12/12 killed; its M11 / M12 equal my M11 / M14 | - |
| 9 | no write to evidence or main | CONFIRMED | sha256 of the 139 evidence files vs `rev_d9b\evidence_before.sha`: identical; main AG DB 7cf2082f / -wal 7eea2abd | unchanged | - |

## Defects

- **E1 (LOW, test gap; not blocking).** The conflict branch of R5 (`key not in conflict`) is untested in the order where it matters.
  - T17h lists the wrong sha256 LAST. Last-wins then already yields WRONG sha256, so removing the conflict check (M12) still passes 132/132.
  - The code itself is correct: a path listed twice with different sha256 reads LISTED TWICE, so NOT MET, in either order.
  - Fix, optional: T17h' with the wrong sha256 FIRST and the right one last.
- **E2 (LOW, operational).** T17j reads `$SPR\rev_d9b\harness\v10st`, the reviewer's fixture. If that directory is removed, T17j FAILS (fail-closed, not silent). Keep it until the outcome is recorded, or copy the fixture into d9b\.

## Final pins of record (kinds per CONTEXT rule 8; the gate checks sha256 of the file bytes with Get-FileHash)

| file | sha256 of file bytes | rendering | blob |
|---|---|---|---|
| d9b\d9b_compare.py | 55b961cac716568800f724eea17e3fa41b0ce9110f8f1b8ab53d6378254009c9 | LF (sha256-lf) | blob:209eb2e6 |
| d9b\d9b_aux.py | ca9becec509a36e2e9cefba783bc74c5e815e5a598489293e05a60919224ba2f | LF (sha256-lf) | blob:5f255f66 |
| d9b\d9b_prep.py | 8cc3eb84e92aa00a4b4bbd9cff88a27baa62cf9027c092ce2c1769c73cb7fab7 | LF | blob:d0b75bb2 |
| d9b\run_tests.py | 409c118fbb2bbb5f... | LF | blob:23c20cae |
| d9b\run_tests.out | sha256-crlf16:d71080b3d59db1f8 (file bytes, 386 CR); sha256-lf16:7782ddb7a54f6fc2 (of record) | CRLF on disk | blob:3c671ae5 (LF) |
| d9\d9_legrun.cmd | e986bb848ebf3b986c535c48bd1abb1034d8f6f2fad83a9f4e2f421af478ca60 | CRLF on disk (sha256-lf 884f6cc4...) | blob:8a67bcbf (LF) |
| d9\d9_leg_check_v2.py | b2d1ae8df0d1bd354e87e0d3bf9a32c3744cf2e73a49259d6b0eb97f6e037bfd | LF | blob:e5f2ff7a |
| d9\probe_lcb.toml | 617bd50b30aa4fdbfd00077393b5363517c13f88bc1e3858c1421417d08b297b | LF | blob:e78bbaaa |
| d9\pins.py / d9\w1.ps1 (operator tools) | 8dd4dfd9... / 0f68ce4b... | LF | - |
| $SPR\d9bm_run.py (builder's mutation runner, evidence only) | 522f180019cb6f81... | LF | blob:82e53c45 |

Command: `sha256sum < f; tr -d '\r' < f | sha256sum; tr -d '\r' < f | git hash-object --stdin`. All values equal the builder's relayed pins.

## Final step list (of record)

S0'-S12 exactly as written in READY_lcb_d9b.md, section "## Exact step list" (d984724). The only change is S0': Get-FileHash must match the table above (d9b_compare 55b961ca..., d9b_aux ca9becec...). In brief:
1. S0' pins and hygiene (no java / python: WAIT; at least 12 GB RAM; L6 pins in both views; W1).
2. S1 worktrees d9b-legA (a62c7e0), d9b-legB (6b9fc7c), d9b-legA2 (a62c7e0).
3. S2 `d9b_prep.py`, ending [V2] PASS.
4. S3' leg A: legrun, then checker, then `classlists A`.
5. S4' leg B: the same, with `classlists B`.
6. S4b leg A2 as "A" into `$ST\a2`: legrun, then checker (root d9b-legA2), then `classlists A2`.
7. S5' C1' into `$ST`, and S5b' C2 into `$ST\aa2`, with the SAME leg-A root literal. Both run before any probe.
8. S5c `--verdict` (0 / 3 / 6 / 2).
9. S6' V11, then probe B.
10. S7' probe A (MANDATORY).
11. S8 UTF-8 append to `$ST\d9_disc.txt`.
12. S9 `gradlew --stop`.
13. S10 evidence, then SHA256SUMS: Git bash `cd $ST && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS` (accepted by R5: T17b / T17c).
14. S10b `d9b_aux.py v10 $ST` MET, BEFORE removal.
15. S11 remove the worktrees.
16. S12 V9 (the -shm mtimes are expected to move).

DISCHARGED needs S5c exit 0 AND V1-V11 met. The verdict script does not check V1-V11.

## Reviewer's evidence (scratchpad, not committed)

- `$SPR\rev_d9b\harness2\mine.out`: 132/132.
- `$SPR\rev_d9b\harness2\mut3.py`: 7 mutants.
- `$SPR\rev_d9b\evidence_before.sha`: evidence unchanged.
