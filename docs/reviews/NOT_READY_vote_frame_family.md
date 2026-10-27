# READY review: VOTE-FRAME-CERT, TIE-MECHANICS, POSITION-INDEX-ALL (adversarial reviewer, 2026-09-23, zero calls)

Code reviewed: branch `vote-frame-instruments`, HEAD `d237e56` (parent `e4b5911`), worktree `.claude/worktrees/vote-frame-instruments`.
Record reviewed against: registrations TIE-MECHANICS L12911-L13030 (3c2fcab), VOTE-FRAME-CERT L13032-L13109 (8adae39), POSITION-INDEX-ALL
L13111-L13227 (b25bde0); the registrar's rulings L13691-L13746 (04379d7). Nothing was opened except synthetic fixtures under tempfile, the scratch
copies, and one JSON id file (`experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json`). No DB of record was opened. No `--dry-run`, no `--run`.
Every Python process ran under an audit hook that raises on any `.db` / sqlite open outside the temp and scratch dirs, with `PYTHONDONTWRITEBYTECODE=1`
(each run printed `[AUDIT] ... all under temp: True`). Scratch: `<session scratchpad>/vote_frame_review/` (guard.py, adv_frames.py, order1_endtoend.py,
kotlin_judges.py, c2paths.py, p2035.py, null_check.py, mutate_builder_guarded.py, mutate_review.py, *.out).

## VERDICTS

| instrument | verdict |
|---|---|
| VOTE-FRAME-CERT (`vote_frame_cert.py`) | **NOT READY** (two BLOCKERS, B1 and B2) |
| POSITION-INDEX-ALL (`position_index_all.py`) | **NOT READY** (it reads through vfc.unit_votes, so B1 and B2 apply to it as well; H1, H2) |
| TIE-MECHANICS (`tie_mechanics.py`) | **READY-WITH-CONDITIONS** (T-C1, T-C2) |

## Shas (re-derived)

The coordinator's "LF sha16" values are **sha256[:16] of the LF bytes** (the scripts' own `script_shas()` convention), NOT git blob ids. The working tree
has 0 CRLF lines in all three files (python byte count of b"\r\n" = 0), so the working tree IS the LF rendering. `git status --short | wc -l` = 0 in the worktree.

| file | sha256[:16] LF (= working tree) | sha256[:16] CRLF rendering | git blob, `git hash-object` (LF) |
|---|---|---|---|
| tools/analysis/vote_frame_cert.py | 3217ee2d78dd4421 (claimed 3217ee2d78dd4421: agrees) | 258d495b0cce9dbf | f2db3c832007d6b4768ddf9ca7f8fba9fc2975c5 |
| tools/analysis/tie_mechanics.py | b3df664f904849ab (claimed b3df664f904849ab: agrees) | 354848c6194b297b | abcfd28c863750d77be2a8b06d89e34799e8164c |
| tools/analysis/position_index_all.py | 5f6ac8e44049aa6c (claimed 5f6ac8e44049aa6c: agrees) | d274357f9bef9179 | a658e677af2c04af19dbea7b37830020b457c078 |

Commit hygiene: `git show --name-only --format= d237e56 | wc -l` = 3 and `... e4b5911 | wc -l` = 3; `git diff --name-only e4b5911~1 d237e56` lists exactly the three scripts.

## RULING ON THE ORDER-1 CHANGE (asked first)

**Ruling: an order-1 disagreement with the re-parse of its own raw text is an INTEGRITY failure AND frame evidence. It must refuse (MIXED, row ids listed). The
demotion to a WARNING is a BLOCKER (B1).**

Why. (i) The registration: "a stored vote equal to the re-parse on 100% of informative rows is POSITIONAL" and "MIXED (neither hypothesis on 100%)". On
order 1 BOTH hypotheses predict stored == re-parse; a mismatch refutes both, so it is "neither hypothesis", i.e. MIXED. (ii) The ruling of 04379d7 says the fwd
arm "is AMBIGUOUS by construction and does not decide the cache's class": it cannot DISCRIMINATE positional from contestant. It does not say a
contradiction on that arm is tolerated; nothing in it authorises certifying a table whose order-1 votes contradict their own raw text. (iii) It is not only
integrity: two frame errors surface ONLY on order 1 (an arm-label swap in a name-labelled frame; a writer that transposed order 1 instead of order 2). With
order 1 demoted, both are certified with a wrong s.

Fixture (reviewer's own, `order1_endtoend.py`): a WIDE cache whose writer transposed ORDER 1 (vote1 = T(p1), vote2 = p2; the combined winner consistent
with the stored votes), truth s = 30 / 40 = 0.750, full `vfc.run()` then `pia.plan/extract/family_stats`:

| code | cache class | certificate | enters index | index s |
|---|---|---|---|---|
| HEAD d237e56 | CERTIFIED-POSITIONAL (WARNING: order 1 disagrees on 100 of 100) | HELD | yes | **0.333** (FF 20, SS 40): FIRST-sided truth read SECOND-sided |
| e4b5911 | MIXED | HELD | no (excluded by class) | - |

**Yes: a table with order-1 mismatches is certified, the certificate reads HELD, and the index enters it with the wrong sign.** The builder's own fixture
F17 (`f17_order1_drift.db`) asserts exactly this behaviour as a PASS.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Shas 3217ee2d / b3df664f / 5f6ac8e4 | CONFIRMED as sha256[:16] of LF; they are NOT `git hash-object` | table above | agree to 16 hex; blob ids f2db3c83 / abcfd28c / a658e677 | LOW (naming) |
| 2 | selftests pass (64 / 26 / 33) | CONFIRMED, also under `python -O` | `python -O guard.py <t>.py --selftest` | 64/0, 26/0, 33/0 failed in both modes | - |
| 3 | guards are explicit raises, not assert | PARTLY | `grep -n '^\s*assert\b'` | 2 asserts: vote_frame_cert.py L168 (URI flags, tautological) and L171 (`PRAGMA query_only` read-back), both vanish under -O; open_ro is shared by all three instruments | MEDIUM |
| 4 | transposed fixture refused as positional | CONFIRMED | builder F2; reviewer A5b, A3 | F2 CERTIFIED-CONTESTANT; A5b (Kotlin order 2 stored transposed) CERTIFIED-CONTESTANT, s 0.750 | - |
| 5 | one transposed ORDER-2 row makes the table MIXED | CONFIRMED | builder F2b | MIXED, row 1 listed | - |
| 6 | one mis-stored ORDER-1 row makes the table MIXED | **REFUTED at HEAD** | adv_frames.py A2 | HEAD CERTIFIED-POSITIONAL, s 0.769 vs 0.750; e4b5911 MIXED | BLOCKER (B1) |
| 7 | index s = 0.750 from both frames with the certificate applied; 1 - s withheld | CONFIRMED for WIDE E-RAW and Kotlin and LONG | pia selftest; A0, A3, A3b, A5, A5b, A6, A6b | 0.750 each; withheld 0.250 | - |
| 8 | index never certifies a wrong sign on adversarial frames | **REFUTED** | adv_frames.py (HEAD) | A1 0.333, A2 0.769, A4 0.667, A6c 0.667, A7 0.667, all certified; A1 / A2 / A6c / A7 were MIXED at e4b5911, A4 was already wrong at e4b5911 | BLOCKER (B1, B2) |
| 9 | unit_votes refuses every uncertified class | CONFIRMED | adv_frames.py | MIXED, AMBIGUOUS, UNCERTIFIABLE, NOT-DUAL-ORDER, lower-case and empty class: all raise SystemExit | - |
| 10 | NOT-DUAL-ORDER is decided at ROW level | CONFIRMED | adv N1 (Kotlin, orders 1 and 2 present, no key has both), N2 (WIDE, no row with both), N3 (LONG, one dual key among singles) | N1 NDO, N2 NDO, N3 classed normally; at e4b5911 N1 and N2 were CERTIFIED-POSITIONAL (the ruling fixed a real defect) | - |
| 11 | E2 "one of SIX classes"; P1-P4 over dual-order only; P5 on the rev arm | CONFIRMED in code | score_criteria / score_predictions; mutants "P1-P4 over the raw enumeration", "cache classed on its single-order tables" KILLED | - | - |
| 12 | C2 PRIMARY never counts BFCL (ruling (3)) | **PARTLY** | c2paths.py | at 57/0: UNSUPPORTED, excluded (agrees). At 58/0: SUPPORTED (transported MDE 0.349). At 57 FF / 1 SS: measured DEFF 0.97, MDE 0.181, SUPPORTED, and C2 PRIMARY reads **HELD with BFCL as the second corpus**. The selftest itself asserts `support_of((BFCL, GROK), 200, 1.0) == SUPPORTED` | HIGH (H1) |
| 13 | the "UNDETERMINED if readings differ" trigger is gone | CONFIRMED | `grep -n -i differ position_index_all.py` | occurrences only in the superseded docstring bracket (L45), the ruling bracket (L51), a refusal message and C3; c2_verdict has no such branch; mutant "BFCL counted in PRIMARY C2" KILLED | - |
| 14 | p2035 check of record = compute_pool_id(judgeable(ids)) over 228 ids | CONFIRMED by execution; NOT executed by the selftest | p2035.py (reads the JSON id file only) | p2035adddedd1becb over 228 ids (4 keys x 57); selftest always passes pool_check=False, so this branch and its refusal are never executed there | MEDIUM (M2) |
| 15 | TIE exact null: E0 2.856, upper region n2 >= 7 at T = 59, no lower region | CONFIRMED | null_check.py (exact Fractions) | E0 2.85643, SD0 1.5276; P0(>=6) 0.05052, P0(>=7) 0.01462, P0(>=10) 0.00010; P0(n2 = 0) 0.0422 > 0.025, no lower region; first T with a lower region is 64 | - |
| 16 | one = 59 - 2 x two | CONFIRMED (identity) | counts(): T = sum(c1)+sum(c2) = n1 + 2 n2 with n1 = n_any - n2 | 39 = 59 - 20 at the predicted n2 = 10 | - |
| 17 | TIE ordered schema check refuses an order swap | CONFIRMED | selftest check + mutant "schema compared without ORDER" KILLED; mutant "pass 1 with provider columns accepted" KILLED | - | - |
| 18 | TIE Support arithmetic | CONFIRMED | python | SE 1.52 x sqrt(1.09) = 1.587; Poisson mean with P(X >= 7) = 0.80: 9.075, MDE 6.22, with DEFF 6.49; distance 10 - 2.856 = 7.14 > 6.49, margin 0.65 (registered "about 0.7") | - |
| 19 | PIA Support arithmetic | CONFIRMED | python | BFCL 57 / 3.60 = 15.83, SE 0.1257, MDE 0.3518; Mistral MDE 0.0439; grok 0.0602; canary 0.2923 | - |
| 20 | builder mutation 19 / 19 killed | CONFIRMED | mutate_builder_guarded.py on a COPY (root_head), selftests under the audit hook | 19 / 19; originals restored byte-identical: True | - |
| 21 | reviewer's sign-flip / vacuity mutants | PARTLY | mutate_review.py on the copy | 22 / 28 killed. SURVIVED: (a) fwd/rev roles swapped in ORDER_PAIRS (no LONG fwd/rev CONTESTANT fixture; with order 1 demoted the swap is invisible); (b) plan() admits MIXED caches (no MIXED cache in the PIA fixture tree); (c) the unit_votes refusal removed survives the PIA selftest; (d) p2035 re-derivation disabled; (e) TIE pool guard removed (both pool paths off in selftests); (f) the pos_ok-and-con_ok branch certified positional (equivalent mutant: unreachable when n2_inf > 0, dead code); (g) CLI steward-list check (CLI only) | MEDIUM (M3) |
| 22 | Kotlin judge_calls pairing | **DEFECT** | kotlin_judges.py | the match key (snapshot_id, eval_question_id, model_a, model_b) omits judge_model (FAMILY_MAP reads the Kotlin DBs through judge_col, so more than one judge is anticipated): matches judged by 2 judges in both orders -> 10 of 10 excluded as duplicates; matches with grok order 1 + Mistral order 2 -> 10 of 10 PAIRED ACROSS JUDGES and certified | HIGH (H2) |

## Defects

**B1 BLOCKER (vote_frame_cert.py, classify() / order1_warning(); d237e56).** Order 1 no longer decides; a mismatch is a WARNING. Five fixtures are certified with a
wrong s at HEAD and refused at e4b5911: A1 writer transposed order 1 (s 0.333), A2 one order-1 row mis-stored (0.769), A6c LONG fwd/rev labels swapped with the
fwd-labelled rows transposed (0.667), A7 arena13-like name frame with the arm labels swapped (0.667; 110 of 110 order-1 rows contradicted). End to end: certificate
HELD, index 0.333 against a truth of 0.750. FIX: classify must also require `n1_agree == n1_inf`; any order-1 contradiction gives MIXED with
`contradict_order1` listed (also when order 2 has no informative row); delete fixture F17's PASS expectation and make it expect MIXED; add A1, A6c and A7 as
fixtures. This is consistent with ruling (4)'s P5 reading: order 1 does not DISCRIMINATE; it can still REFUTE.

**B2 BLOCKER (vote_frame_cert.py unit_votes WIDE, `votes_from_raw`; present since e4b5911).** A raw-only WIDE table (raw1 / raw2 + combined winner, no stored
votes; the leaf_powered / j6 shape) is certified by E-COMB over the RE-PARSED raw. The parsed votes are positional by construction, so a CERTIFIED-CONTESTANT
result there means the writer's COMBINER did not transpose (a sign bug in the stored winner), not that any vote is contestant-labelled. unit_votes then
applies T() to the positional parse: fixture A4, s 0.667 against 0.750. FIX: when `votes_from_raw`, a CONTESTANT E-COMB result is classed MIXED ("combined column
inconsistent with a positional recipe"), never transposed; add A4 as a fixture.

**H1 HIGH (position_index_all.py support_of / c2_verdict).** Ruling (3) is categorical ("BFCL DOES NOT COUNT TOWARD C2's TWO-CORPORA REQUIREMENT"); the code
excludes BFCL only when its data are exactly s = 1 with n <= 57. At 58/0 or 57/1 BFCL is SUPPORTED and C2 PRIMARY reads HELD on BFCL + MMLU-Pro. FIX: exclude
(BFCL, *) from the PRIMARY support set unconditionally (the with-BFCL reading stays DESCRIPTIVE), or refuse C2 and route to the registrar when the BFCL family
differs from the ruling's premise (57 / 0); replace the selftest check `support_of((BFCL, GROK), 200, 1.0) == SUPPORTED` by one asserting that BFCL never enters the PRIMARY set.

**H2 HIGH (vote_frame_cert.py long_key_fn, Kotlin tuple).** judge_model (and recipe / node_id, per JudgeCallStore.kt L52-L53) are not in the match key: cross-judge
pairs are formed and certified; two-judge matches are dropped. FIX: add judge_model (and recipe, node_id where present) to the Kotlin key; print the duplicate and
cross-key counts as a COUNT beside each table and refuse a table whose duplicate count is > 0 after the fix.

**H3 HIGH (registration-level, for the registrar; E-COMB with STORED votes).** E-COMB cannot distinguish "order 2 stored contestant + correct combiner" from "order 2
stored positional + a combiner without transposition": both store (v1, v2, combine_contestant(v1, v2)). The same holds for the positional class against a
double-transposing combiner. An E-COMB certificate is therefore conditional on the writer's combiner being rejudge_grok.combine_orders. FIX: a ruling that
E-COMB certification requires the READY's per-cache source check of the combiner (WRITER_OF already names the writer), and the index prints E-COMB-only
caches as their own line in C5.

**M1 MEDIUM.** vote_frame_cert.py L168 and L171 use `assert` (URI flags and the query_only read-back) in open_ro, the opener of all three instruments; both vanish
under -O. FIX: explicit `raise SystemExit`.

**M2 MEDIUM (rule 11, branches by execution).** No selftest executes a pool check: TIE-MECHANICS and POSITION-INDEX-ALL always pass `pool_check=False`; the p2035
re-derivation and its refusal, and the TIE pass-1 sha256 refusal (`cache1_sha256=None` in the fixture), are never executed. FIX: run verify_pools with
pool_check=True on a fixture id file for both branches (admit / refuse), and the pass-1 sha branch on a fixture sha. The p2035 line is also PRESENCE-dependent: it runs
only when an entered cache's run_meta carries a pool key; refuse if the BFCL cache enters without p2035 in its run_meta.

**M3 MEDIUM (selftest vacuity).** Survivors of item 21: add a LONG fwd/rev CONTESTANT fixture, a MIXED cache (with a certified table) in the PIA fixture tree, and
an assertion that the PIA reader refuses a uncertified unit.

**L1 LOW.** The coordinator pins sha256[:16] of LF as "LF sha16" without naming the hash; record both (table above). L2 LOW: TIE schema_check compares the
`verdicts` table only (the registration's "the two schemas are identical"); run_meta is not compared. L3 LOW: TIE decides the region from the MC pmf, with the
closed form printed beside; at T = 59 the margin is wide (0.0146 against 0.025, MC SE about 0.0001).

## Conditions

VOTE-FRAME-CERT and POSITION-INDEX-ALL: fix B1, B2, H1, H2, M1, M2, M3; obtain the registrar's ruling on H3; re-run all three selftests (normal and -O) and both
mutation suites plus adv_frames.py (every A-fixture must be MIXED or read 0.750) and re-submit for READY with the new shas.

TIE-MECHANICS READY-WITH-CONDITIONS: T-C1 = M1 (it opens its caches through vfc.open_ro; its selftest re-run after that change with 26 / 26); T-C2 = M2
for its pass-1 sha refusal branch. Its own logic (frame gate, R1 counts, n2, null, region, schema order, predictions) is confirmed above and does not depend on
B1 / B2 / H1 / H2. Pin: tie_mechanics.py sha256[:16] LF b3df664f904849ab, git blob abcfd28c863750d7 (both change if T-C2 edits it).

## Commands (reproduce)

```
W=.claude/worktrees/vote-frame-instruments; S=<session scratchpad>/vote_frame_review
python -c "import sys;b=open(sys.argv[1],'rb').read();print(b.count(b'\r\n'))" $W/tools/analysis/<f>.py         # 0 for all three
sha256sum $W/tools/analysis/<f>.py | cut -c1-16 ; git -C $W hash-object tools/analysis/<f>.py
PYTHONDONTWRITEBYTECODE=1 python [-O] $S/guard.py <t>.py --selftest          (cwd $W/tools/analysis)
PYTHONDONTWRITEBYTECODE=1 python $S/guard.py $S/adv_frames.py                (VFR_WT=<copy of e4b5911 tree> for the comparison)
PYTHONDONTWRITEBYTECODE=1 python $S/guard.py $S/order1_endtoend.py
PYTHONDONTWRITEBYTECODE=1 python $S/guard.py $S/c2paths.py ; ... kotlin_judges.py ; ... p2035.py ; python $S/null_check.py
python $S/mutate_builder_guarded.py <copy>/tools/analysis ; python $S/mutate_review.py <copy>/tools/analysis
grep -n '^\s*assert\b' $W/tools/analysis/{vote_frame_cert,tie_mechanics,position_index_all}.py
```
