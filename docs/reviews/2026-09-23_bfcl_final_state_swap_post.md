# POST-RUN REVIEW: BFCL-FINAL-STATE-SWAP (numbers re-derived from the caches; zero calls)

Adversarial reviewer, 2026-09-23. Subject: outcome `experiment_results/agent/bfcl_final_state_swap_outcome.txt`
(sha256 bfc2b9d56fa22173...), cache `experiment_results/agent/bfcl_final_state_swap.db` (sha256 87a058b35324e474...),
both committed at 316eef5. Instrument `tools/analysis/bfcl_final_state_swap.py`: git blob ee4fc59583061f276ee395529ab4d15a3a9d8c62
(same at 70203ea and in the working tree), sha256-lf16 48a9d23632c107e6, sha256-crlf16 (working tree) 9e911c509d5b322f.
READY-WITH-CONDITIONS 4cc024e; ruling 1470fe8; registration docs/judge_v2_program.md L12316-L12598; power 9b046c4; defects 7da2ec5.

## 0. Preconditions

| check | command | result |
|---|---|---|
| no -wal / -shm / -journal beside the three DBs | `ls experiment_results/agent \| grep -c -- "-wal\|-shm"` | 0 |
| nothing construction/null running | `Get-CimInstance Win32_Process` (java, python) | 2 JVMs (IDE, Kotlin compile daemon) and 5 python processes of another agent's mutation test in the session scratchpad (`cert_under_filter/mutants/M0x`); no construction, null or judged run |
| all DBs opened read-only | every script uses `file:...?mode=ro&immutable=1` | sha256 of pilot cache 8c3c91fb..., corpus c5eddd26..., SWAP cache 87a058b3... identical before and after this review |
| pilot cache byte-unchanged since its commit | `git hash-object experiment_results/agent/bfcl_judged_pilot.db` vs `git ls-files -s` | 9146ab74... = 9146ab74... |
| corpus DB not written by the run | `ls -la` | mtime Sep 18 03:04, before the run (14:31-14:41) |

Scripts (session scratchpad `swap_post/`, not in the repo): `nums.py` (own aggregation, bootstrap, McNemar, power),
`spread.py` (bootstrap SE over 40 seeds at B = 2000), `r1.py` (per-contestant, C2/C3 deltas, transition table),
`payload_scan.py` / `ctxchk.py` / `fa.py` (payload re-assembly, own leakage scan, template checks).
`nums.py` does NOT import the instrument: it reads `schedule` and `verdicts` from both caches and combines orders
itself (rev presents B first, so its vote is inverted; unequal -> TIE; TIE/TIE -> TIE).

## 1. Per-claim table

| # | claim | command | got | claimed | verdict |
|---|---|---|---|---|---|
| 1a | 458 deciding mids over 49 tasks, set sha256_16 a314ce23062663c8 | `nums.py`: pilot `schedule` rows, stratum='headline' and nj='' | 458 mids (461 headline, 3 nj=EMPTY), 49 tasks, sha a314ce23062663c8; SWAP cache holds exactly these 458 mids x {fwd, rev} = 916 rows | same | CONFIRMED |
| 1b | pilot on the 458: ties 100 / right 339 / wrong 19; T 0.2183, A 0.7402, W 0.0415 | `nums.py` | 100 / 339 / 19; 0.2183 / 0.7402 / 0.0415 | same | CONFIRMED |
| 2 | T_swap = 98/458 = 0.2140; 342 right + 18 wrong + 98 ties + 0 unusable | `nums.py` | 98 / 342 / 18 / 0; 0.2140 | same | CONFIRMED |
| 3a | paired delta = -0.0044 | `nums.py`, match by match | -2/458 = -0.0044 | -0.0044 | CONFIRMED |
| 3b | delta clustered SE 0.0175, interval [-0.0387, +0.0300] | `nums.py` (B = 20,000, own seed); `spread.py` (40 seeds x B = 2000) | SE 0.0177 (B=20k); 40 seeds at B=2000: mean 0.01779, sd 0.00026, range 0.01739-0.01840; CR1 analytic 0.0179; interval [-0.0390, +0.0303] (boot), [-0.0395, +0.0308] (analytic) | 0.01753, [-0.0387, +0.0300] | CONFIRMED within Monte-Carlo error (claimed SE 1.0 sd below the seed mean) |
| 3c | percentile [-0.0390, +0.0284] | `nums.py` | [-0.0383, +0.0301] at B = 20k | [-0.0390, +0.0284] | CONFIRMED (MC) |
| 3d | interval wholly above -0.05 -> C1 FAILED | `nums.py`, `spread.py` | every SE computed (max 0.01840; analytic 0.0179; t(48) half-width 0.0353 -> lower -0.0397) gives a lower end above -0.05; the SE needed to reach -0.05 is 0.0233 (delta-DEFF about 2.0), outside every draw | FAILED | CONFIRMED, robust to the bootstrap draw |
| 3e | measured delta-DEFF 1.151, n_eff 398, MDE +-0.049 | `nums.py` (SRS SE of the paired difference 0.0164) | DEFF 1.17 (B=20k), 1.12-1.26 across seeds; n_eff 392 (range 364-409); MDE80 at SE 0.01768 = 0.0495 | 1.151 / 398 / +-0.049 | CONFIRMED (MC) |
| 3f | level SE 0.0292, level-DEFF 2.328, n_eff 196.7 | `nums.py`, `spread.py` | SE 0.0299 (B=20k); 40 seeds mean 0.02989, sd 0.00046 (0.0287-0.0309); DEFF 2.44 (2.25-2.60); n_eff 187.5 | 0.0292 / 2.328 / 196.7 | CONFIRMED within MC (claimed 1.5 sd below seed mean); decides nothing |
| 4 | McNemar b 29, c 27, exact p 0.8939 | `nums.py` (scipy binomtest) | b 29, c 27, p 0.89385 | same | CONFIRMED |
| 5 | usable-only delta = literal delta | `select finish, provider, max_tokens, count(*), max(ctokens), sum(invalid) from verdicts group by 1,2,3` | stop x916, azure:grok-4-1-fast-non-reasoning x916, cap 8192, max ctokens 483, invalid 0; posting_order 24 + 892; 0 verdict rows without a posting row | 0 unusable | CONFIRMED |
| 6 | power at measured SE 0.01753: HELD needs < -0.0843, FAILED > -0.0157; P(FAILED) 0.740 at the observed delta | `nums.py` | -0.0844 / -0.0156 / 0.740 at SE 0.01753 (last-digit differences are SE rounding) | same | CONFIRMED; observed power, not evidence about delta |
| 7 | C2: A_swap 342/458 = 0.7467; dA +0.0066, SE 0.0159, [-0.0246, +0.0377], HELD | `r1.py` | 342; +3/458 = +0.0066; SE 0.0159 | same | CONFIRMED |
| 8 | C3: W_swap 18/458 = 0.0393; dW -0.0022, SE 0.0057, upper +0.0090, HELD | `r1.py` | 18; -1/458; SE 0.0058 | same | CONFIRMED |
| 9 | C4: first position 497/872 = 0.5700; flip table 50/5/16/21/1/3 + (TIE, Model B) 2 | `nums.py` | 497/872 = 0.5700; 50 / 5 / 16 / 21 / 1 / 3 / 2 | same | CONFIRMED (descriptive) |
| 10 | R1 per-contestant table | `r1.py` | all 7 rows reproduce (pass-share and pilot -> swap conv-A counts, e.g. DeepSeek 32/145, 109 -> 110; gemini 47/139, 97 -> 103) | same | CONFIRMED |
| 11 | night ledger 3,860 | `experiment_results/night_calls_2026-09-23.json` | 48+1580+100+24+1192+24+892 = 3860 over 7 rows | 3860 | CONFIRMED |
| 12 | leakage (BFCL-REF-ORACLE) | `payload_scan.py`: re-assembled all 916 posted (system + user) payloads; own patterns over the FULL text | cells with `\bPASS(ED)?\b` 0, `\bFAIL(ED/URE)?\b` 0, `all_pass` 0, `error_type` 0, `multi_turn:` 0, "Outcome checker report" 0, "passed" 0; either side's `checker_output` verbatim 0; any checker_output line >= 25 chars 0; either side's `error_type` value 0. "checker" occurs in 916 of 916, all from ONE identical sentence of the per-task reference block ("the task's checker is state-based, so a different sequence that reaches the same final state is as good"; `ctxchk.py`: 1 distinct context) | no per-side verdict | CONFIRMED (see D1 on what the instrument's own assert covers) |
| 13a | new system prompt sha16 7cee3034d3d93296; pilot's 058faa54f0697ad9 | `payload_scan.py`: parent `P.system_prompt()` with the four FROM/TO pairs copied from the REGISTRATION text, not the script's constants | pilot 058faa54f0697ad9; mine 7cee3034d3d93296 = the instrument's | same | CONFIRMED |
| 13b | four replacements present, each FROM exactly once; 'final answer' 0 | same | each FROM 1 in the pilot prompt and 0 in the new; each TO once; `final\s+answers?` 4 -> 0; length 2683 -> 2679 | same | CONFIRMED |
| 13c | user turns byte-identical to the pilot's | `payload_scan.py` | 916 of 916 equal to the parent's re-assembly; my own hash loop over all 608 rows' parent payloads = anchor 951ec3a0a063b5a8 (the pass-1 anchor of record) | 916/916, anchor MATCH | CONFIRMED; neither cache stores request bodies, so "on the stored payloads" is not possible: identity to pass 1 rests on re-assembly + the anchor (D2) |
| 13d | F1: 0 of 916 user turns name a 'final answer' | `fa.py` | 0 of 916 ('final state' 916 of 916, from the reference-block sentence) | 0 | CONFIRMED |
| 14 | R1: reference-wrong stratum empty by construction; contestant agreement beside accuracy | `grep -c "EMPTY BY CONSTRUCTION"` on the outcome | present (3x) with the 7-row table | present | CONFIRMED |
| 15 | C1 scored against the MEASURED SE | registration L12436-L12446 ("point +- 1.96 x the task-clustered bootstrap SE ... B = 2000, seed 42") and L12519-L12521 ("scores C1 against the MEASURED delta-DEFF, not against the planning 2.0") | the interval uses the bootstrap SE directly | same | CONFIRMED (no C-7 substitution) |

## 2. Rulings asked for

**FAILED at the measured SE is a legitimate reading.** The registration's deciding statistic is point +- 1.96 x the
task-clustered bootstrap SE (B = 2000, seed 42), and it states in terms that C1 is scored against the MEASURED
delta-DEFF. The planning forecast (UNDETERMINED about 90% of the time) was conditional on P1 (delta about -0.07); at
delta = 0 the planning table itself gave P(FAILED) 0.394, so FAILED was a registered, reachable outcome even at the
planning SE. The measured SE is lower because the discordance is lower than planned (56/458 = 0.122 against a planning
d = 0.20) and the delta-DEFF is 1.15, not 2.0. The verdict does not depend on the bootstrap draw (row 3d). What the
reading does NOT carry: the observed -0.0044 would have read UNDETERMINED at the planning SE 0.02955 (FAILED would
then need > +0.0079). That is not a defect; the registration chose the measured SE before the run.

**DBGUARD wording gap: MET IN SUBSTANCE; fix the condition's wording now and the print at the next sha.**
Condition 1 (09a786a, carried by 4cc024e) is a DRY-RUN condition. The dry-run's last line (`bfcl_final_state_swap_dryrun.log`
L971) is "4 call(s): bfcl_result_2025-12-16.db, bfcl_judged_pilot.db". The query-stripped print cannot show the mode,
but `_guarded_connect` (L195-L212) raises SystemExit for either basename unless `_ro_uri` finds a `file:` URI opened
with `uri=True` whose query parses to exactly `mode=['ro']` and `immutable=['1']`. The 4 printed calls could therefore
only have succeeded read-only; the pilot cache's git blob is unchanged (9146ab74...) and the corpus mtime predates the
run. The line is a presence print where the condition wanted a mode print; the enforcement makes the substance hold.
(i) WORDING, now, for future READY files: "a last [DBGUARD] line naming only the corpus and the pilot cache, each of
which `_guarded_connect` admits only as mode=ro&immutable=1 (refusal path proven by the selftest)". Do not ask for a
URI print that the code does not produce.
(ii) PRINT, next sha of any instrument on this guard: print the full URI, or a count line such as
`[DBGUARD] ro&immutable-enforced opens N of N (corpus k, pilot m); writable opens: cache only`. `dbguard_line()` also
de-duplicates on the stripped path, so a writable and a read-only open of the same file collapse into one entry. A
count check beats a presence print.
The instrument cannot change post-run (`--analyze` refuses another sha); no re-run is warranted.

## 3. Defects

- **D1 (MEDIUM, evidence wording):** the outcome says "assert_no_per_side_verdict executed on 916 of 916 re-assembled
  payloads". That function (`bfcl_judged_pilot.py` L720-L741) inspects the TASK STATEMENT (task text + reference block)
  only, not the artefacts or the whole user turn. True as worded, broader as read. This review's full-payload scan
  (row 12) finds 0/916, so the leakage conclusion holds on the evidence. Fix: the registrar's outcome section reads
  "task-statement guard 916/916; full-payload scan by the post-run reviewer 0/916 (this file, row 12)". Successor
  instruments scan the full user turn.
- **D2 (LOW, record):** neither cache stores the posted request bodies or their hashes. Every payload property (sha
  7cee..., byte-identity, leakage) is established by re-assembly through the parent module plus the pass-1 anchor
  951ec3a0a063b5a8. That stays sound only while the corpus DB, the raw result files and the parent module stay as they
  are. Fix for successors: store sha16(system) and sha16(user) per (mid, arm) row at post time.
- **D3 (LOW, cosmetic):** the R1 block is printed three times, including under the convention-B heading, where it still
  reads "judge conv-A". The R2 chip is appended to C3's delta line and verdict, where the bar is +0.05 and the chip's
  "[-0.05, 0]" refers to the tie delta. No number moves.
- **D4 (LOW, Monte-Carlo):** the level SE 0.0292 and level-DEFF 2.328 sit 1.5 sd below the 40-seed mean (0.0299 /
  2.44). They are within MC error and decide nothing. Quote the level-DEFF as "about 2.3-2.4 (MC)", not to three
  decimals.
- **D5 (MEDIUM, downstream: DEGRADED-CONTROL):** its ruling (DC13, section 5) required the joint reading table to be
  written BEFORE this outcome existed, or be marked DESCRIPTIVE-ONLY. It admitted a swap-template second arm ONLY if
  registered before this outcome. The outcome is now committed (316eef5), and
  `grep -c "DEGRADED-CONTROL" docs/judge_v2_program.md` = 0 (not registered; queue row 57 "deferred"). Therefore the
  DC13 joint table is DESCRIPTIVE-ONLY, and the template x difficulty 2x2 is no longer admissible under that ruling.
- No BLOCKER, no criterion substitution, no write to a DB of record, no denominator mismatch.

## 4. Proposed sentence of record

> BFCL-FINAL-STATE-SWAP (916 judge calls, 0 unusable; the 458 deciding matches of BFCL-JUDGED-PILOT over 49 tasks,
> both orders, user turns byte-identical to the pilot's): replacing "final answer" with "final state" in the four
> registered strings of the inherited verify-first block left the dual-order tie rate at 98/458 = 0.2140 against the
> pilot's 100/458 = 0.2183. The paired delta is -0.0044, with task-clustered interval [-0.0387, +0.0300] (bootstrap SE
> 0.0175, measured delta-DEFF 1.15, n_eff 398, MDE +-0.049). The interval lies wholly above the -0.05 bar, so C1 is
> FAILED: these four strings do not carry a share of the pilot's indecision of 5 points or more. The point is
> DESCRIPTIVE-ONLY (R2) and is not a move (McNemar b 29 / c 27, p 0.89). There is no harm: agreement delta +0.0066
> (lower end -0.0246) and wrong-committed delta -0.0022 (upper end +0.0090). Of the three hypotheses the pilot left
> open, template mis-fit at the granularity of these four strings is refuted. Position bias and corpus difficulty
> survive, and neither is established. The 0.2183 stands as an unexplained decisiveness collapse.

**Does not show:**
1. That the template is irrelevant to BFCL. Only these four strings (one referent, answer -> state) are cleared. The
   rest of the inherited furniture ("the question", "the response", "its reasoning") was deliberately left. Any
   further edit is governed by fence F3: a different F1-qualifying referent plus a pre-registered argument, and two
   readings close the line on this corpus.
2. That the four strings have NO effect. The interval admits a reduction of up to about 3.9 points (lower end
   -0.0387), up to roughly a sixth of the 21.8-point tie rate.
3. That the indecision is position bias, or that it is corpus difficulty. The test refutes one hypothesis and
   establishes neither of the others. The first-position rate 0.5700 (z 4.13) is descriptive, has no bar, and is not a
   replication of the pilot's 0.5862.
4. Any movement at all. Delta -0.0044, the first-position shift 0.586 -> 0.570, the (Model B, Model B) count 0 -> 5
   and the dA / dW points all sit inside the session floor (CANARY pass 2 0.087; DECOMP 5.7%). The two passes are
   different sessions 8.5 h apart, not interleaved. The discordance 56/458 = 0.122 sits at the upper edge of the
   CANARY retest interval [0.056, 0.122] and splits 29/27, which is what retest churn alone looks like.
5. Anything about the reference ceiling. The reference-wrong stratum is empty by construction (R1), and the
   CONSENSUS-FIT KEY/REF contrast is not estimable.
6. A rung, a ladder position, a 0.75-bar reading or a "for Agents" claim. A_swap is never on the ladder.
7. Anything about STACK-v2 or any other corpus (F5). No MMLU-Pro, MATH or IFEval number is touched.
8. That the design was underpowered. It was better powered than planned (delta-DEFF 1.15 against a planning 2.0).
   The REALISED P(FAILED) 0.740 is observed power at the point estimate, not evidence about delta.

## 5. What FLIP-RESEED and DEGRADED-CONTROL now bear on

- **BFCL-FLIP-RESEED** (registered, not run; 0 night-ledger rows) now carries the position-bias vs boundary-noise
  question alone.
  - HELD (the 100 flips reproduce) makes the 0.2183 a stable per-match property. That is consistent with position bias
    or with pair-bound difficulty, and does not separate them.
  - FAILED makes the flip set resampling noise at the tie boundary.
  - The swap cache implies that 71 of the pilot's 100 ties tied again under the swapped prompt (100 - b). By L12136
    the swap is NOT a control for FLIP-RESEED. The 71/100 was produced under a different prompt: it is never quoted as
    R, never used as a forecast against the 0.566 bar, and never pooled with pass 2.
- **BFCL-DEGRADED-CONTROL** (deferred, unregistered) is now the only instrument aimed at corpus difficulty, and it
  reaches only D-shape (DC1).
  - Per D5, its joint table is DESCRIPTIVE-ONLY and the swap-template arm is no longer admissible.
  - Its template stays the inherited one (DC7). This result neither changes that nor licenses changing it.
- Neither FLIP-RESEED nor DEGRADED-CONTROL, alone or together, separates position from difficulty cleanly (ruling
  section 5). Position needs a position-balanced arm that no current registration buys.

## 6. Verdict

- **Criteria:** C1 FAILED, CONFIRMED. C2 HELD, C3 HELD, C4 HELD and C5 HELD, all CONFIRMED.
- **Predictions:** P1, P2, P4 and P8 FAILED; P3, P4(ii), P5, P6 and P7 HELD. All CONFIRMED against the recomputed
  values.
- **Numbers:** every headline number reproduces exactly (counts) or within Monte-Carlo error (SEs, DEFFs).
- **Leakage and template:** leakage clean on the full payloads; template delta confirmed from the registration text.
- **DBGUARD:** MET IN SUBSTANCE, with the wording and print fixes in section 2.
- **Blockers:** none.
- **Fit for the registrar**, provided the outcome section applies D1 (quote the full-payload scan) and D4 (level-DEFF
  as MC-approximate), and D5 is carried into the DEGRADED-CONTROL registration.
