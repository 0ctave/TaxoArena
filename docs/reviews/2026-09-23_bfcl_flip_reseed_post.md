# Post-run numbers review: BFCL-FLIP-RESEED (run 6dca538)

Adversarial reviewer, 2026-09-23. Zero calls, read-only. Every DB was opened `mode=ro&immutable=1`. sha256 of the flip cache, the pilot cache and the corpus DB was taken before and after the review and is IDENTICAL (`0e18292c…`, `8c3c91fb…`, `c5eddd26…`). No `-wal` or `-journal` files exist in `experiment_results/agent/` (count 0).

Objects:
- Registration `docs/judge_v2_program.md` L12049-L12314 (ca3a7cc), plus the defect section L13362ff (7da2ec5, D1/D2).
- READY-WITH-CONDITIONS e3592dc.
- Script `tools/analysis/bfcl_flip_reseed.py` blob:898bafb5edf1cca45b8197c8a48c34a401f6b374 / sha256-lf16:d4e08a891a85b4cd, identical at 26ffb1d, merged at 70203ea. The working-tree CRLF rendering 430e14da1ecca2c2 is printed by the instrument.
- Outcome `experiment_results/agent/bfcl_flip_reseed_outcome.txt` blob:5bee2f278162654a1f5a30e1ce94a8a65de13988 / sha256-lf16:7bb4bd659ffb4084. The working tree is CRLF.
- Cache `experiment_results/agent/bfcl_flip_reseed.db` blob:2bd30896b0807122165fbf91400827d532e0b7a7 (sha256 0e18292c…, equal to the operator's scratch copy).

Reviewer scripts are outside the repo in the session scratchpad `flip_post/`:
- `recompute.py` is an independent reader that does not import the instrument.
- `leakscan.py` / `leakscan2.py` rebuild payloads with the instrument's own builder, as the brief asks. The scan logic is the reviewer's.

Rule 7: no construction or site null was running. The process list showed only an idle Gradle daemon (started 11:35, no worker children) and a peer's `split_exposure_sensitivity.py --dry-run`, which reads no BFCL object.

## MANDATORY POST-RUN CONDITION: full-payload leakage scan

RESULT: 0 / 200 cells carry a per-side verdict, a checker outcome or a checker-side reference result. All 200 cells were scanned in full: the system prompt plus the ENTIRE user turn (task text, reference block, both artefacts, template).

Method (`leakscan2.py`):
1. **Rebuild.** For each of the 100 mids and both arms, `F.assemble(row, arm, ctx)` was called after `F.load_context()`. The re-run byte gate reads anchor 951ec3a0a063b5a8 MATCH, 200/200 cells equal to the parent's re-assembly, system sha16 058faa54f0697ad9.
2. **Structure asserted per cell.** The user turn is EXACTLY `USER_TEMPLATE` with three slots (task+reference, first artefact, second artefact). The system prompt equals `F.system_prompt() == P.system_prompt()`. The task+reference slot has exactly 1 distinct rendering per task over the 35 tasks, so nothing per-side enters it.
3. **Per-side checker material searched in the full payload, for both sides of every cell:**
   - `episodes.checker_output`: the full string, plus every 60-char window (step 20) that is not explainable by either side's raw result entry or by the task/reference. All 200 sides carry a non-empty checker_output.
   - `episodes.error_type`.
   - The score file's `error_message` and `error_type`. There are 100 failing-episode score records among the 200 sides: one failing side per checker-disagreeing match, as expected.
   - Every score-file leaf of 40 chars or more (1,712 examined).
   - Every ground-truth-STATE leaf of 20 chars or more under `details.*.ground_truth` (248 examined). 90 of these are present in a payload, and every one is also present in one side's own raw result, i.e. an agent whose own final state equals the ground-truth state. That is legitimate artefact content, not checker leakage.
4. **Fixed tokens and words, located by region.**
   - Tokens: `all_pass`, `multi_turn:`, `[Outcome checker report]`, `error_type`, `error_message`, `instance_state_mismatch`, `execution_response_mismatch`, `ground truth instance`, `does not match the state`, `"valid"`, `'valid'`, `Model instance for`, `checker_output`, `possible_answer`, `checker`.
   - Words: PASS/PASSED/FAIL/FAILED, passed, failed, correct, incorrect, wrong, succeeded, winner.
   - Hits:
     - `checker`, `possible_answer` and `correct` occur once per cell (200) in the CONSTANT REF_BLOCK frame. It is hand-written, identical for every cell and states the reference's provenance.
     - `correct`, `winner` and `wrong` occur in the constant system prompt and template.
     - `failed` occurs 8 times inside artefacts, each present in that side's raw result: tool or environment output, not the checker.
     - `correct` 4 and `incorrect` 4 occur in the TASK text. These are the dataset's own user turns: "I've sent incorrect information to my advisor" (mids 700000072 and 700000358) and "certain everything's correct" (mids 700000076 and 700000130).
   - These 8 cells are the only flags left once the constant frame is excluded. All 8 are benign dataset text.

Limits of the scan (a "does not show"):
- It is a string scan against the known checker-side sources: DB checker_output, error_type and the score files. A paraphrased verdict cannot be found this way, but none can arise, because no slot has a checker-derived source (item 2).
- The payload scanned is the RE-ASSEMBLY. The cache stores no posted body, so "what was posted equals what was scanned" rests on the byte gate (A) and the pinned script and parent shas. That is the same basis as every BFCL cell.

The instrument's own `assert_no_per_side_verdict ... 200 of 200` is a PRESENCE count on 35 distinct task statements and inspects the task statement only. It is superseded by this scan and must not be cited for leakage.

## Per-claim table

| # | claim (as printed) | check | reviewer's number | verdict |
|---|---|---|---|---|
| 1 | The 100 = TIE under TIE-on-flip within the 458 deciding matches (headline stratum, nj/nj_a/nj_b clear) | `recompute.py`, pilot `schedule` + `verdicts` | 458 deciding over 49 tasks; 100 TIE; set sha16 9b414912be7e44a5 = run_meta `set_sha256_16`; pinned list == derived; flip cache mids == set, 200 rows | CONFIRMED |
| 2 | Pass-1 partition 57/0/24/14/3/2 | same | (A,A) 57, (A,TIE) 14, (TIE,A) 24, (TIE,TIE) 3, (B,TIE) 2, (B,B) 0 | CONFIRMED |
| 3 | Pass-2 partition | same | (A,A) 42, (A,TIE) 8, (A,B) 9, (B,A) 22, (TIE,A) 10, (B,B) 1, (TIE,TIE) 7, (TIE,B) 1 | CONFIRMED to the digit |
| 4 | R = 69/100 = 0.6900 | own `combine_orders` re-implementation | 69/100. By pass-1 class: (A,A) 40/57, (A,TIE) 9/14, (TIE,A) 16/24, (TIE,TIE) 3/3, (B,TIE) 1/2. Excluding the 3 double-TIEs: 66/97 = 0.680 | CONFIRMED |
| 5 | Clustered SE 0.0498, interval [0.5924, 0.7876], 35 clusters | own bootstrap, same algorithm at seed 137 | SE 0.0498, [0.5924, 0.7876], 35 clusters | CONFIRMED to 4 dp |
| 5b | (robustness) | numpy bootstrap, 20 seeds × 20,000 draws; analytic cluster-robust | SE 0.0502-0.0514 (median 0.0508); CR0 0.0503, CR1 0.0511. CR1 interval [0.5898, 0.7902], still wholly above 0.566 | C1 HELD is robust to the SE method |
| 6 | Percentile [0.5882, 0.7778]; Wilson [0.5937, 0.7722] | same | [0.5882, 0.7778]; [0.5937, 0.7722] | CONFIRMED |
| 7 | Usable-only line = literal (READY cond. 4) | external recomputation | usable 100/100 (0 INVALID, 0 pending), R_usable 69/100, identical interval | CONFIRMED; condition 4 MET |
| 8 | Measured DEFF 1.160, n_eff 86.2, MDE ±0.151 / ±0.139 | own | Seed 137 bootstrap: 1.160 / 86.2 / 0.151 / 0.139 exactly. Stable values: DEFF 1.20 (numpy median), 1.19 (CR0), 1.22 (CR1); n_eff 82-84; MDE ±0.152-0.155 / ±0.141-0.143 | CONFIRMED as printed; the printed 1.160 sits at the low end of bootstrap noise (LOW, D5) |
| 9 | C2(a) 32/57 = 0.5614 [0.3982, 0.7246], 25 clusters | own | 32/57, 25 tasks, SE 0.0833 (DEFF 1.61, n_eff 35) | CONFIRMED |
| 10 | C2(b) 40/57 = 0.7018 | own | 40/57 | CONFIRMED |
| 11 | C2(c) 133/167 = 0.7964; pilot 510/870 = 0.5862 | own | 133/167; 510/870 | CONFIRMED |
| 12 | C2(d) (TIE,TIE) → TIE 3; (B,TIE) → 1 COMMITTED, 1 TIE | own | same | CONFIRMED |
| 13 | C3 b 32, c 13, p 0.006609 | own exact McNemar | b 32, c 13, p 0.006609 | CONFIRMED |
| 14 | P3 25/31 = 0.8065 (convention A 25/100) | own, checker_winner from the pilot schedule | 25/31 | CONFIRMED |
| 15 | C4: 0 unusable of 200; finish stop 200; one fingerprint; max ctokens 435; 0 truncated | own | same | CONFIRMED |
| 16 | Night ledger 4,060 | sum of `night_calls_2026-09-23.json` | 9 rows, sum 4,060; FLIP rows 24 + 176 | CONFIRMED |
| 17 | Byte gate (A)-(E), P5 HELD | re-executed `F.byte_gate(ctx)` | ok True, anchor 951ec3a0a063b5a8, 200/200, 058faa54f0697ad9 | CONFIRMED, but see D3: (B) passes by construction |
| 18 | C1 HELD | interval wholly above 0.566, no trigger (usable 100 ≥ 90; gate 200/200) | same under every SE method tried | CONFIRMED |
| 19 | P1 FAILED; P2 FAILED; P6 FAILED; P3, P4, P5 HELD | as scored | same | CONFIRMED as scored; P1, P2 and P6 are band or anchor problems of the registration, not data problems (D1, D2) |
| 20 | DBGUARD: only the corpus and the pilot cache, both mode=ro&immutable=1 | executed `_guarded_connect` on 6 URIs | REFUSED: plain path, `?mode=ro`, `?mode=ro&immutable=1&mode=rw`, corpus `?mode=rwc`, an unlisted basename. ADMITTED: `?immutable=1&mode=ro`. Operator logs: every mode's last-but-one line lists only the corpus, the pilot cache and the own cache | CONFIRMED by execution; the printed line strips the query string, so it shows names, not modes (D6 LOW) |
| 21 | p2035 check of record = compute_pool_id over 228 ids | `pool_guard.compute_pool_id` on `reserved_pool_frozen_bfcl_p2035adddedd1becb.json` (4 keys × 57) | p2035adddedd1becb over 228; `grep -c p2035 experiment_configs/reserved_pools.json` = 0; pool_guard refuses (operator's `pool_guard_p2035.txt`) | CONFIRMED: it is the check of record per the corrected step (3) at L12107 (fdd6a99). POOL-REGISTRY-BFCL is still `state: drafted` in `docs/agents/queue.json` |
| 22 | READY condition 5 (FLIP waits for POSITION-INDEX-ALL) | git dates | f523981 at 18:20:56; cache `started 2026-09-23 19:14:27` | MET |

## Support (item 2): the DEFF behind P6

- **The pilot's 3.60 is a different statistic on a different cluster structure.** Recomputed from the pilot cache at seed 42, it is the DEFF of the fidelity statistic A (convention A, 0.7402), not of the tie indicator: DEFF(A) = 3.601. Its population is the 458 matches over 49 tasks, Kish mean cluster size 9.92.
- **The comparable quantity is lower.** The tie indicator on the same 458 has DEFF 2.71 (bootstrap, seed 42) or 2.81 (CR1). The implied ICC is 0.197.
- **The prediction had nothing to do with the formula.** The formula (bootstrap variance / binomial variance) is the same in the pilot and here, and the clustering unit (task) is right. What differs is the statistic (A vs tie) and the cluster size: selecting 100 of 458 cuts Kish from 9.92 to 4.24. At ICC 0.197 and Kish 4.24 the expected DEFF is 1 + 3.24 × 0.197 ≈ 1.64, not 3.8. Conditioning on pass-1 TIE plausibly lowers the ICC further. The measured value is 1.16-1.22.
- **P6's band [2.5, 6.0] was therefore mis-derived at registration.** Its reasoning ("ties cluster, so selecting on ties concentrates the set") ignored the shrinking cluster size. P6 FAILED is correctly scored, and the defect is the registration's.
- **Consequence for Support:** the planning DEFF 3.60 was CONSERVATIVE. The run has more power than planned (n_eff ≈ 83-86 vs 27.8; MDE ±0.15 vs ±0.265), and C1's verdict is not threatened.

## C1's reading, jointly with SWAP (18d8516) and POSITION-INDEX-ALL (f523981) (item 3)

**Stale wording.** The outcome's "separating them is BFCL-FINAL-STATE-SWAP's job" was the registration's wording, written before SWAP ran. SWAP has run: C1 FAILED, with the tie rate 0.2140 vs 0.2183, paired delta -0.0044 [-0.0387, +0.0300], wholly above -0.05. Template mis-fit at the four-string granularity is refuted. The outcome's sentence is stale and must not be carried into the record as a pending task.

What FLIP-RESEED + SWAP + POSITION-INDEX-ALL jointly license:
1. The BFCL order-flip TIE set is a stable per-match property of the deployed recipe under a byte-identical prompt. R = 0.69 [0.59, 0.79] is wholly above the 0.566 bar, and far above the noise anchor 0.2183.
2. Changing the four "final answer" strings to "final state" does not move the tie rate (SWAP). The template mis-fit hypothesis at that granularity is refuted.
3. The flips are positional in FORM, and that form reproduces at the match level on re-posting:
   - Among pass-2 both-decisive flips, the first-shown side is named in both orders 42 times and the second-shown side once (42 : 1, exact two-sided p 1.0e-11).
   - Of the 57 (A,A) matches, 32 are (A,A) again.
   - These are descriptive figures on a selected set, not a C2 bar.
   - POSITION-INDEX-ALL shows that a first/second IMBALANCE among both-decisive flips is general across supported families. It also shows that BFCL's degree of one-sidedness (1.000) is not reproduced by any family and that the direction differs by judge (grok first, Mistral second). Its C2 HELD rests on MATH at a margin of 0.024 on one cache.

What they do NOT license:
- That position preference CAUSES the ties rather than serving as the tie-breaker of a judge that cannot decide on hard matches. Corpus difficulty predicts a stable, positionally resolved flip set just as well. Position bias as the cause is consistent with the evidence but not established, and no registered test separates it from difficulty.
- Any fidelity number.
- That BFCL's 57/0 degree generalises.
- Any per-match claim off BFCL.

SWAP's 71/100 is not used here as R, is not compared with R and is not pooled.

## P1 / P2 (item 4): the bands or the data?

- **P1.** P1 [0.75, 0.95] (point 0.88) was set against the "stable anchor" 0.913 = 1 - CANARY-BASELINE pass 2's 0.087. That 0.087 is the MATCH-LEVEL disagreement rate over all 300 canary matches, most of which were decisive in both passes. It is NOT the canary's TIE-conditional reproduction rate, which is the quantity R measures.
- **The canary's own tie-conditional rates**, recomputed from `canary_baseline_pass{1,2}.db` (read-only): pass-1 TIE 75, TIE again 59, rate 59/75 = 0.787. For flip-origin ties: 55, flip again 35, rate 0.636.
- **Against the right anchor, BFCL's R is unremarkable.** R = 0.69 (flip-origin 66/97 = 0.680) sits between the canary's 0.636 and 0.787. The ties reproduce at the canary's own rate.
- **The bands, not the data, are the issue:**
  - P1's band sits above the correct stable anchor for flip-origin ties. P1 FAILED is correctly scored at the point. Its interval upper end 0.788 overlaps the band's lower edge, so the data do not exclude 0.75.
  - P2's band [0.60, 0.90] is 0.30 wide on n = 57. The registration's own Support statement puts the MDE at about ±0.35 (measured n_eff 35, SE 0.083). A point-in-band prediction narrower than the design's resolution is close to a coin flip. P2 FAILED at 0.561 while the interval [0.398, 0.725] covers most of the band.
- **C1 is robust to the anchor correction.** With a stable anchor of 0.636 or 0.787 the midpoint bar would be 0.427 or 0.503, and C1 HELD either way. The bar 0.566 stays the bar of record (never moved after the fact). This is recorded as a registration-anchor defect (D1) that changes no verdict.

## Checks that pass without checking (item 5)

- **Byte gate (B) "200 of 200".** `F.assemble` composes the same parent functions (`P.artefact_facts`, `rj.build_user_prompt`, the same system prompt) that `P.payloads` uses, so (B) compares the parent's code with itself and cannot fail except through a composition error. The tie to pass 1 is carried by (A) alone. (A) is a recomputation matched against a value that the pilot's post-run review itself computed by re-assembly, and the pilot stores no posted body. P5 HELD is true, but "byte-identical to what pass 1 posted" is established only through (A). The raw `result/` files (the artefacts) are not pinned in run_meta; they are covered transitively by (A). (D3, LOW)
- **`assert_no_per_side_verdict` "executed on 200 of 200".** It checks the task statement only (35 distinct statements, each checked 2-16 times: 1-8 matches per task x 2 arms). It is superseded by the full scan above. (D4, LOW; the condition is now MET)
- **The [DBGUARD] line.** It prints basenames with the query string stripped, so the line cannot show the mode. The ro&immutable guarantee is in `_guarded_connect`, verified here by execution. The whitelist is by BASENAME: a file named `bfcl_judged_pilot.db` in another directory would be admitted ro/immutable. Harmless here. (D6, LOW)

## Defects

| id | severity | defect | fix |
|---|---|---|---|
| D1 | MEDIUM | The registration's STABLE anchor 0.913 is the canary's match-level agreement, not its tie-conditional reproduction rate (59/75 = 0.787; flip-origin 35/55 = 0.636). P1's band and the bar's midpoint derivation inherit this. No verdict changes: C1 HELD at any of the three anchors | Registrar bracket at L12158-L12163 and in the outcome section: "the tie-conditional canary comparator is 0.787 (0.636 flip-origin); R = 0.69 sits between them; P1's band was anchored on the wrong quantity". Bar unchanged |
| D2 | MEDIUM | P6's band [2.5, 6.0] rests on the pilot's 3.60, which is the DEFF of A (not of ties) at Kish 9.92 (not 4.24). The expected DEFF from the pilot's own tie ICC is about 1.64. P2's 0.30-wide band sits below the registered MDE (about ±0.35) on n = 57 | Bracket P6 and P2 as registration defects; the scoring (FAILED) stands. Any future selected-subset Support section derives DEFF from the SAME statistic at the SUBSET's Kish size |
| D3 | LOW | Byte gate (B) passes by construction; pass-1 identity rests on (A) alone; the result/ files are not pinned | State this in the outcome section; pin the result-file sha256s in run_meta on future BFCL instruments |
| D4 | LOW | "assert_no_per_side_verdict executed on 200 of 200" is a presence count on the task statement only | Superseded by this review's scan (0/200); record the scan, not the assert, as the leakage evidence |
| D5 | LOW | The printed DEFF 1.160 is one bootstrap seed at the low end (stable 1.19-1.22) | Print the CR1 analytic DEFF beside the bootstrap DEFF in future readouts |
| D6 | LOW | The [DBGUARD] line omits the URI mode; the whitelist is by basename | Print the query string; match on the absolute path |
| D7 | MEDIUM (record) | The record's `launch_note` still says the coordinator "STOPPED IT BEFORE ANY CALL ... pending the author". The run posted 200 calls at 19:14-19:22, and neither 6dca538 nor the record names the launch decision (who, when, on what) | Registrar appends the launch decision to the record and the outcome section, citing the author's standing authorisation if that is its basis |
| D8 | LOW (wording) | The outcome's "separating them is BFCL-FINAL-STATE-SWAP's job" is stale (SWAP ran, C1 FAILED, 18d8516) | The outcome section quotes it as the registration's wording and states the joint reading below |

No BLOCKER, no HIGH. Every printed number reproduces.

## Verdict

- **C1 HELD: CONFIRMED.** R = 69/100 = 0.690, clustered interval [0.5924, 0.7876], wholly above 0.566, robust to the SE method (CR1 [0.590, 0.790]).
- **C2-C4 HELD** as printed.
- **Predictions:** P1 FAILED, P2 FAILED and P6 FAILED are correctly scored and are band defects of the registration (D1, D2). P3, P4 and P5 HELD.
- **Leakage:** 0 / 200 by full-payload scan; the post-run condition is MET.
- **Record:** NUMBERS OF RECORD STAND. D1, D2 and D7 go to the registrar as insertion-only brackets.

## Proposed sentence of record

"BFCL-FLIP-RESEED (200 calls, 0 errors, 0 unusable): the pilot's 100 order-flip ties, re-posted under a byte-identical prompt in a new session, tie again in 69 of 100 (task-clustered interval [0.592, 0.788], 35 tasks, measured DEFF 1.16-1.22, n_eff ~84), wholly above the 0.566 bar, so C1 HELD: the BFCL flip set is a stable per-match property, not boundary noise. The rate matches the MMLU-Pro canary's own tie-conditional retest rate (0.636 for flip-origin ties, 0.787 for all ties), not the 0.913 match-level floor the registration used as its stable anchor. P1, P2 and P6 FAILED on bands that the registration mis-derived. Among pass-2 both-decisive flips the first-shown side is named 42 : 1. With BFCL-FINAL-STATE-SWAP (template mis-fit at the four strings refuted) and POSITION-INDEX-ALL (a first/second imbalance general across families, BFCL's degree not), the flips are stable and positional in form. Whether position preference causes them or only breaks ties on matches the judge cannot decide (corpus difficulty) is not separated. [run 6dca538; review <this commit>; full-payload leakage scan 0/200; denominators: 100 matches over 35 tasks, selected from 458 deciding matches over 49 tasks, pool p2035adddedd1becb]"

## What this run does not show

- Why a flip happens. Position preference as a cause vs as the tie-breaker of an undecided judge (difficulty) is not separated by this or any registered test.
- A "different 100": no match decisive in pass 1 was re-posted. The noise-anchor inference assumes a session-stable marginal tie rate.
- R to better than about ±0.10, or any "flips reproduce at X%" with a tight interval.
- Any fidelity, rung, ladder, 0.75 bar, profile cell, agent ranking or "for Agents" bridge.
- That BFCL's 57/0 (or pass-2 42/1) degree of one-sidedness generalises. POSITION-INDEX-ALL says it does not.
- Any comparison with SWAP's re-tie count. That count was taken under a different prompt, and it is not R, not a control and not poolable.
- That the posted bodies equal the scanned re-assembly other than through byte gate (A) and the pinned shas. The cache stores no body.
- A calibration of the judge.
