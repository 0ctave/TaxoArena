# READY REVIEW emb-e0b3 (DELTA) 2026-09-29: 660a936 on aa9c2d7, tools/analysis/embedder_cross_flat.py

Adversarial reviewer; zero calls; no real-data run. Delta = `git diff aa9c2d7..660a936` (1 file, +62 / -14). Prior review
docs/reviews/READY_emb_conn_e0b2.md (38f0fd0) CONFIRMED everything the delta does not touch; not re-derived here.

## VERDICT

- 660a936: MERGEABLE (merge by path; `git merge-tree` main 920ed4f + 660a936 clean; main has not touched the file since aa9c2d7).
- E0b `--run` (cpu / embed): READY-WITH-CONDITIONS. PRE-RUN: R-1 (pins committed + the dry-run pin check on main + 660a936),
  R-2 (registrar brackets: D2 = C-E0B2-1, still absent; the support-tag bar = C-E0B3-1; which P1 label governs).
  C-E0B3-2 (MEDIUM, test gap) may follow the run: the code is right by reading and the line prints all three legs.

## PINS (reviewed blob)

| object | value |
|---|---|
| blob (LF, `git rev-parse 660a936:<f>` = `git hash-object` of the LF rendering) | 87811d3dd78b23d6e3b8b003c07db32b410d9790 |
| sha256 LF rendering | 181581e3f454367a2722ce29eb5a188cca317912807b1bbdc5a70595fe97f6be |
| sha256 CRLF rendering (= the emb-e0b3 worktree file) | 76c9a5311029462e32af411e7c31226e0bb3ce282e48d37de94c1a04c655cea3 |

## PER-CLAIM TABLE (deciding claims only)

| # | claim | finding | status | severity |
|---|---|---|---|---|
| 1 | C-E0B2-2 code: tag bar = max(registered MDE, measured spread_qwen3, realised MDE80), three legs printed | support_tag body and call site `support_tag(n, k, metric, c["spread"], 2.8 * se, ks[0])` read; se = (hi - lo) / 3.92 computed BEFORE the call (was after in aa9c2d7); the WORSE criterion (`fires`, `word`) is untouched by the delta | CONFIRMED | - |
| 2 | Is that bar the REGISTERED one? | NO. Registration Support (e) (prog L21724): "M1 0.0186, M2 1.00e-3 (bars max(MDE, spread_qwen3))"; (f) (L21725): "max(0.0186, spread)". The realised-MDE80 leg is the reviewer's own C-E0B2-2 recommendation, not a registered word. It is a NEW support rule: one-sided (can only demote SCOREABLE to DESCRIPTIVE-ONLY, never promote), so it cannot manufacture a scored outcome, but it can change P1's / P2's label. Also new vs (f): the MEASURED spread in place of the record's 0.0305 (C-E0B-2, never bracketed either). Programme on main: `C-E0B2` 0 hits, `C-E0B-2` 0, `realised MDE80` 0, `M1'` 0 | NEW RULE, registrar must bracket | HIGH (pre-run, C-E0B3-1) |
| 3 | E0-TAG kills OMX1 | The builder's OMX1 mutates the support_tag BODY; E0-TAG unit-tests the function with spread 0.03 > 0.0186, so it dies (39/39 KILLED, re-run). My OMX1 is the CALL SITE (as in 38f0fd0: the run path dropping the measured spread): `support_tag(n, k, metric, 0.0, 2.8 * se, ks[0])` -> SURVIVED on the full selftest. The E0-CPU stub's qwen3 V spread is still 0, so no stub has spread > max(MDE, MDE80); the "stub where qwen3's V spread exceeds the MDE" asked in C-E0B2-2 is not built | PARTLY | MEDIUM (C-E0B3-2) |
| 4 | C-E0B2-3: non-firing F1 prints "not shown; no support computed", never "the method's"; firing line unchanged | F1_NOT_SHOWN appended only on the `else` branch; E0-TAG asserts both; builder mutant "F1 non-firing unqualified" KILLED | CONFIRMED | - |
| 5 | Selftests / mutants | embedder_cross_flat --selftest 51 PASSED, --mutants 39/39 KILLED; embedder_arms --selftest 95 PASSED (unchanged file) | CONFIRMED | - |
| 6 | Hygiene | 1 path; 0 of application.yml / .env / .gitignore / experiment_results; insertion-only header block | CONFIRMED | - |
| 7 | Pin check of the E0b --dry-run on main + 660a936 | experiment_configs/embedder_cross_arm_pins.json on main 920ed4f: all four sha256 null, filled_by null. The registrar's fill is in the MAIN WORKING TREE, UNCOMMITTED, at review time; not read as of record. With null pins every read REFUSES (E0-REFUSE, killed mutant "pins checked late") | UNDETERMINED (step owed) | pre-run (R-1) |

## OWN MUTANTS (full selftest; control OMX0 KILLED)

- OMX0 control, spread over K seeds -> KILLED.
- OMX1 call site passes spread 0.0 -> SURVIVED. DECISIVE in kind (P1's tag); code correct by reading, legs printed.
- OMX4 call site passes MDE80 0.0 -> KILLED (E0-CPU).
- OMX5 call site MDE80 = 1.96 SE -> KILLED (E0-CPU).
- OMX6 tag compares the signed prior -> KILLED (E0-TAG).

## DEFECTS / CONDITIONS

- R-1 (pre-run): the registrar's pins commit lands on main; then, on main + 660a936, `--dry-run --part cpu` and `--dry-run --part
  embed` each pass the registrar_pin check for every arm the part reads (log line per arm, no REFUSED), sha256 equal to the
  provenance's sha256_after. This is the one remaining operational step.
- C-E0B3-1 (HIGH, pre-run; the registrar's, by insertion, before any outcome is read): bracket (i) D2 / M1' (C-E0B2-1, still 0 hits
  in the programme); (ii) the tag bar max(registered MDE, measured spread_qwen3, realised MDE80) as a POST-REGISTRATION tightening
  (reviewer-originated, one-sided), and that the REGISTERED label = max(registered MDE, spread_qwen3) is recoverable from the
  printed legs; (iii) which P1 / P2 label governs when (f) as registered (DESCRIPTIVE-ONLY on the record's 0.0305) and the
  re-derived tag disagree. Fix without a bracket: print both tags (registered two-leg and three-leg) on the (f) RE-DERIVED line.
- C-E0B3-2 (MEDIUM; may follow the run): an E0-CPU stub whose qwen3 V seeds spread above max(0.0186, MDE80) on M1', asserting the
  run-path tag's bar equals that spread, so the call-site OMX1 dies.
- CARRIED unchanged: C-CONN-1 / C-CONN-2 (LOW, embedder_arms.py; not in this delta); READY_emb_e0b NOTE on the two nomic_raw fits.

## COMMANDS (compact)

```
git diff --stat aa9c2d7 660a936 ; git diff --numstat ...                                     # 1 file, 62 / 14
git rev-parse 660a936:tools/analysis/embedder_cross_flat.py ; git show ...| sha256sum ; ...| sed 's/$/\r/' | sha256sum
git diff --name-only aa9c2d7 660a936 | grep -cE "application.yml|\.env|\.gitignore|experiment_results/"   # 0
git merge-tree --write-tree main 660a936 ; git diff --name-only aa9c2d7 main | grep -c embedder_cross_flat  # clean ; 0
sed -n 21714,21727p docs/judge_v2_program.md                                                 # (e) / (f) bars
for p in C-E0B2 "M1'" C-E0B-2 "realised MDE80"; do git show main:docs/judge_v2_program.md | grep -c "$p"; done   # 0 0 0 0
git show main:experiment_configs/embedder_cross_arm_pins.json                                 # 4 x null
export TAXOARENA_DATA_ROOT=<scratch>/nodata OLLAMA_HOST=http://127.0.0.1:9 OMP_NUM_THREADS=1
embedder_cross_flat.py --selftest (51 PASSED) --mutants (39/39) ; embedder_arms.py --selftest (95 PASSED)
python <scratch>/e0b3/own_mut4.py                                                             # OMX0,1,4,5,6
```
