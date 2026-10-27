# Post-run review: ARCH-V2-G22 designs (D4, D1-stage1, D1-full; legs (c), (d), (g)) and the stop leg (e). Record runs a5b68e6

Adversarial reviewer, 2026-09-24. Zero calls, read-only, single process. Scratch scripts: `scratchpad/g22rc.py` (designs) and `scratchpad/g22stop.py` (stop), session scratchpad, plus inline checks quoted below.

## VERDICT: RECORDABLE WITH CONDITIONS (C1-C6 below)

Every printed number reproduces to the digit from the stored per-replicate records, and so does every Wilson interval.

Chips:
- **NUMBERS CONFIRMED.** 3 x 1,000 design records and 1,000 stop records. The manifest shas match. 40,563 + 19,002 stream seeds re-derived with 0 mismatches. instrument_lf16 876d01413318bd7b re-derived at 8f2cf69, 53eccb6 and a5b68e6.
- **(c):** D4 BELOW. D1-stage1 and D1-full MEETS, optimistic by construction. These are admissible only as the ORDER and the schedule quantities.
- **(d):** BELOW on all 3 designs. The statistic is SIGN-BLIND (D1, HIGH).
- **(e):** MEETS at every margin. It is exercised at stage 1 only at margins 0 and 1 (D2), in a world without overdispersion (D3).
- **Predictions:**
  - P3: D4 HELD; D1-stage1 FAILED; D1-full FAILED; D0 and D2 NOT SCORED.
  - P4: D1-full HELD ON ITS INTERVAL ONLY; D1-stage1 and D4 FAILED.
  - P5: HELD.
- **Falsifiers:** (c) and (e) NOT FIRED.
- **Item 2:** NOTHING VOIDED. The ruling post-dates both launches. The real-supply, registered-anchor re-run is OWED, and it needs a new registered re-binding.

### SENTENCE OF RECORD

"ARCH-V2-G22 designs and stop record runs (a5b68e6; lf16 876d01413318bd7b; master ARCHV2-G22-REC-1, R 1,000; DEV proportional supply) reproduce to the digit from their stored replicates. On the DEV supply, P(LOAO nominal >= 9) is 0.000 [0.000, 0.004] for D4, 1.000 [0.996, 1.000] for D1-stage1 and 1.000 [0.996, 1.000] for D1-full; frozen 0.000 / 0.974 / 1.000; deflated x1.18 0.000 / 0.996 / 1.000. Under ruling 2 these are admissible only as the order D4 < D1-stage1 < D1-full and as the schedule quantities (3,990 / 14,490 / 28,980 matches). The (d) identification rates 0.182 / 0.518 / 0.654 are BELOW 0.80 but are sign-blind: the simulator does not reproduce the sign of the widener slope (validity-v2 random mode: established b1 median -0.023, 506 of 1,000 <= 0, against the record's +2.6386). The key-blind stop calls a calibrated judge MISCALIBRATED in 0.020-0.024 of re-draws at every margin, but its stage-1 branch fires in only 1 and 0 of 1,000 at margins 2 and 3, and its calibrated labels carry no overdispersion. P3 FAILED for D1-stage1 and D1-full, held for D4; P5 held; no falsifier fired. The real-supply, registered-anchor re-run is owed."

## Per-claim table

| # | claim (operator / output) | status | command | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | D4 P(nom_loao >= 9) = 0 / 1000, Wilson [0.000, 0.004], BELOW | CONFIRMED | g22rc.py over `G22_designs.txt.designs.D4.records.jsonl` | 0/1000 [0.000, 0.004]; median 2.15 [1.68, 2.69]; frozen 0/1000, median 1.71 [1.41, 2.03]; decl 0/1000 | = |
| 2 | D4 deflated x1.06 / x1.18: 0 / 1000 | CONFIRMED | same | 0 / 0 | = |
| 3 | D1-stage1 P = 1.000 MEETS (LOAO); frozen 0.974; deflated x1.18 0.996 | CONFIRMED | same, D1-stage1 records | LOAO 1000/1000 [0.996, 1.000]; frozen 974/1000 [0.962, 0.982]; decl 999 [0.994, 1.000]; x1.06 1000; x1.18 996 [0.990, 0.998] | = |
| 4 | D1-full P = 1.000 MEETS | CONFIRMED | same, D1-full records | LOAO / frozen / decl 1000 [0.996, 1.000]; medians 26.40 / 19.92 / 24.17; x1.06 and x1.18 1000 | = |
| 5 | (d) D1-stage1 0.518 BELOW; D1-full 0.654 BELOW; D4 0.182 | CONFIRMED (numbers); SUBSTANCE: see D1 | same | 518 [0.487, 0.549]; 654 [0.624, 0.683]; 182 [0.159, 0.207]; Holm 317 / 490 / 104 | = / D1 HIGH |
| 6 | (g) DEFF 1.152 (D1-stage1), 1.156 (D1-full), 1.066 (D4), a lower bound | CONFIRMED | per-edge `deff` lists: exactly 20 replicates carry them, with 144,100 / 288,133 / 26,469 edges | 1.152 IQR 1.025-1.313; 1.156 IQR 1.029-1.317; 1.066 IQR 0.968-1.178 | = |
| 7 | Both counts per design (all-label / established) | CONFIRMED | medians of `w_loao` and `w_loao_est` | D4 3 / 0; D1-stage1 15 / 2; D1-full 30 / 4. Status words recomputed with calibration_status's rule: all-label 175 and 138 MISCALIBRATED, established 0 and 0 | = |
| 8 | Stop P(MISCALIBRATED given calibrated) 0.020-0.024 at every margin, MEETS | CONFIRMED (numbers); PARTLY in substance (D2, D3) | g22stop.py over `G22_stop.txt.stop.records.jsonl` | m0 20/1000 [0.013, 0.031]; m1 21 [0.014, 0.032]; m2 24 [0.016, 0.035]; m3 24 [0.016, 0.035]; key-world MISCALIBRATED 124 / 153 / 154 / 154 | = / MEDIUM |
| 9 | Frozen-to-LOAO ratio 1.325 | CONFIRMED | same (`map`) | median 1.3249 [1.194, 1.479]; LS slope 0.260; per-replicate corr(frozen, LOAO) **0.130**. Independently, the D1-full design records (different streams) give median 1.3249 | = |
| 10 | Schedule: matches 3,990 / 14,490 / 28,980; reuse 2.06 / 7.47 / 7.36; exhausted 0 | CONFIRMED | min = max of `matches` in every design; C(20,2)x3x7 = 3,990, C(46,2)x2x7 = 14,490, x14 = 28,980 | identical; reuse = matches / questions_used | = |
| 11 | Token file sha 14cfff2f..., chain file sha ff70668c... (launch record) | CONFIRMED | `sha256sum` on the working tree and on `git show HEAD:<path>`; `git hash-object` | 14cfff2fb55c...e57ca (blob c4870ebb); ff70668ced25...33c1 (blob 6743d02f); LF = working tree = HEAD | = |
| 12 | instrument_lf16 876d01413318bd7b | CONFIRMED | sha256 over name+NUL+LF bytes of the 11 INSTRUMENT_FILES (g22.py L616) from `git show <rev>:` | 876d01413318bd7b at 8f2cf69, 53eccb6, a5b68e6 and the working tree | = |
| 13 | Streams sha 2dc6e2df... / 701e26e9... | CONFIRMED | `sha256sum *.streams.tsv`; every seed = sha256("ARCHV2-G22-REC-1\|name")[:8] BE | 40,563 / 19,002 rows, 0 mismatches | = |
| 14 | "HEAD at launch: 53eccb6" (launch record) | REFUTED | `git reflog --date=iso`; output "started" lines; proclist UTC stamps | designs launched 15:29:45, HEAD ed9c384 (15:29:07); stop launched 16:12:07, HEAD 5e406fc (15:35:05); 53eccb6 = 16:51:51, during the stop run (stop .txt mtime 16:57:31) | LOW (D4) |
| 15 | No writes to DBs of record | CONFIRMED | `stat` | mmlu_pro_dataset_cache_v2.db 974,917,632 B, mtime 2026-09-19 16:30:10 (= printed); x12all / x20 unchanged; -wal 0 B | = |
| 16 | Rule-7 window | CONFIRMED | `grep -c -i "python\|java\|gradle"` on both proclists: 0 and 0; FreePhysicalMemory 33,999,740 KB | 0 foreign readers; 34.0 GB free | = |
| 17 | 13 files committed at a5b68e6 | CONFIRMED | `git show --name-only --format= a5b68e6` (13 lines, whole list read) | .log files absent (gitignored, as stated) | = |

## Question 2: the ruling-2 print requirements

| requirement (L15667-L15686; chain record L15830) | designs | stop | ruling |
|---|---|---|---|
| (i) admissibility sentence | printed | printed | MET. The sentence's "the real split is not drawn" was FALSE at launch: b51eb71 at 15:20:00, R4 met at ed9c384 at 15:29:07. Bracket it (D5) |
| (ii) MEETS labelled "optimistic by construction" | on every MEETS line | n/a | MET |
| (iii) bias line | once per design | once | MET |
| (iii) deflated x1.06 / x1.18 from the stored replicates, with Wilson | nom_loao, from the .jsonl (re-computed here) | n/a (no P(nom >= 9) reading) | MET; the stop is N/A, stated |
| (iii) (g) DEFF labelled a lower bound | yes | n/a | MET |
| (iii) both counts | per design, plus status words under each | ALL-LABEL ONLY | designs MET. Stop NOT MET, covered by the builder limit of record (L15208ff: "the stop leg (e) uses the all-label count"). An established count is undefined on synthetic calibrated labels. The outcome must say "not met, limit of record", not stay silent |
| (iii) PASS chip | "PASS AT THE BOUNDARY (D9 realised on H2 u_raw_wrong)" | same | MET as coded; STALE. The replay outcome (L15816ff) appended "; Monte-Carlo-fragile on one row, by one replicate". The outcome prints the full chip (D5) |
| (iii) token_digest in full | yes | yes | MET |
| L15830: token-file sha256 and chain-file sha256 printed by "any designs or stop outcome" | not printed by the instrument | not printed | **RULING: ACCEPTED AS MET BY THE LAUNCH RECORD, with a condition.** L15830 binds the OUTCOME, not the instrument. Changing the 11 hashed files to print them would need a new re-binding. The operator's launch record is committed in the same commit as the outputs (a5b68e6), and both values reproduce (row 11). CONDITION C5: the registrar's outcome prints both file shas, citing the launch record and this review. The instrument's own chain check is content-based: token_digest, old_lf16 and new_lf16 == live are all checked (g22.py L680-L700), and the log's L22 "[G22] the token of record admitted through the rebind chain" is the execution witness. But replay_output_sha and registrar_commit are checked for FORMAT ONLY (L701-L704) (D6) |

## Question 3: admissibility and the item-2 ruling

- **Schedule quantities: ADMISSIBLE.**
  - Matches and calls are exact arithmetic, C(k,2) x N x S, constant across all 1,000 replicates, and independent of the simulator and the supply.
  - Reuse per question IS supply-dependent. The DEV supply has 4,002 MMLU-Pro EVAL questions; the split of record pv2_6f78aece2bf9a612 has 3,749 items (L15855). So the real reuse is higher (D1-full about 7.8 vs 7.36).
  - "Exhausted pairs 0" is structurally zero at this supply and shows nothing.
- **ORDER: ADMISSIBLE.** D4 < D1-stage1 < D1-full holds on all three nominals, with disjoint central 95% ranges.
  - D1-full / D1-stage1 = 2.05 (LOAO medians 26.40 / 12.89) is essentially the doubling of the strata, so it is close to tautological.
  - D4 vs D1 compares a different roster AND a different 7-anchor set: D4 has {biology, business, health, history, law, other, physics}, D1-stage1 has {chemistry, computer science, economics, engineering, philosophy, physics, psychology}. Re-drawn here with design.choose_strata from the logged seeds.
- **Absolute MEETS: "optimistic by construction", NOT admissible for the board size (ruling 3).** Two further facts:
  - The frozen reading, which does no refit, also MEETS: 0.974 and 1.000.
  - The simulator's frozen medians land on the memo's X column for all three designs: 1.71 vs 1.8; 9.80 vs 9.5; 19.92 vs 19.1 (`MEMO_NOMINAL_PMX`, design.py L39). This agrees with ruling 3's M / X planning basis, and adds no independent evidence for it.
- **Item-2 ruling (L15985-L15994): NOTHING IS VOIDED.**
  - The ruling (53eccb6, 16:51:51) post-dates both launches: designs at 15:29:45, finished 16:11:27; stop at 16:12:07.
  - The registered draw ARCHV2-STAGE1-ANCHORS-1 has NOT been run. The record says "no draw has been run with it" (L15989), and no commit runs it (`git log --all --oneline | grep -i stage1`: only 53eccb6 and a5b68e6).
  - Compliance was therefore impossible. The ruling's words "the re-run D1-stage1 design" name the real-supply re-run of ruling 2 (v).
  - Consequence: the stage-1 sets used are OWN-STREAM DEV SETS and must not be cited as stage-1 readings. They also differ from each other: the stop has {biology, business, chemistry, computer science, economics, engineering, math}; D1-stage1 has {chemistry, computer science, economics, engineering, philosophy, physics, psychology}; 4 of 7 are shared.
  - The re-run is OWED and needs all of the following:
    - (a) the registered draw run and recorded;
    - (b) an input by which the instrument reads that set. The CLI has none (archv2_g22_sim.py L198-L227): the stop draws `stop/stage1-strata` and D1-stage1 draws `designs/D1-stage1/part0/strata`. This is a change to the 11 hashed files, so it needs a NEW registered re-binding (L15830 effect clause) and a delta READY;
    - (c) a per-anchor `--supply-json` built from the split of record (the flag exists, L213; the operator states that no tool produces its content).

## Question 4: predictions and falsifier

| prediction (L15208ff) | observed (primary nom_loao) | score |
|---|---|---|
| P3 D4 0.00 [0.00, 0.02] | 0.000 [0.000, 0.004] | HELD |
| P3 D1-stage1 0.30 [0.05, 0.60] | 1.000 [0.996, 1.000]; frozen 0.974; x1.18 0.996 | FAILED. This holds under every reading, so the failure survives the bias. Mechanism: the memo's P column (exponent 1.06), against the measured exponent 1.6-2.3 (P2 FAILED) |
| P3 D1-full 0.75 [0.30, 0.95] | 1.000 [0.996, 1.000] (every reading) | FAILED (same mechanism) |
| P3 D0 / D2 | not run (ruling 2 (iv)) | NOT SCORED (outside the validity domain) |
| P4 (d) 0.85 [0.60, 0.97] | D1-full 0.654 [0.624, 0.683]; D1-stage1 0.518; D4 0.182 | D1-full HELD ON ITS INTERVAL ONLY: the point misses by 0.196 against an MDE of 0.042, and the prediction implied MEETS where BELOW was observed. D1-stage1 FAILED. D4 FAILED. All sign-blind (D1) |
| P5 (e) 0.03 [0.01, 0.08] | 0.020 / 0.021 / 0.024 / 0.024 | HELD |
| Falsifier (c): D1-full BELOW | MEETS | NOT FIRED (under the post-hoc v2 simulator only; ruling 3: the registered simulator decides nothing) |
| Falsifier (e): EXCEEDS | MEETS at every margin | NOT FIRED (D2 and D3 limit what this shows) |

Support, re-derived after the run. DEFF is 1 by design across replicates (independent streams; source: the simulator). n_eff = 1,000.
- (c) D1-full: P 1.000; the Wilson lower bound 0.996 is 0.196 above the bar.
- (d) D1-full: SE sqrt(0.654 x 0.346 / 1000) = 0.0150; MDE 0.042; gap to the bar 0.146.
- (e) margin 3: SE sqrt(0.024 x 0.976 / 1000) = 0.0048; MDE 0.0136; gap 0.026.

All are SCOREABLE at this R, as the registration stated. The registration's arithmetic reproduces: 0.0126 / 0.0354 at 0.8, and 0.0054 / 0.0151 at 0.03. The Monte-Carlo SE is not the binding uncertainty. The binding one is the structural leg (g): the simulator is not centred, and it extrapolates from k = 12 to k = 46.

## Question 5: the stop leg's count and the bias line

- **Count.** The ALL-LABEL count: `status_word(L["nominal"], L["wrong"])` (g22.py `_stop_rep`), as disclosed.
- **Bias line, interpreted.**
  - The calibrated world's labels are drawn from the FROZEN pair's Bernoulli(Phi(-|m| / sqrt(s^2 + tau^2))) (`_calibrated`). The simulated judge's over-calling of wrong verdicts therefore does NOT enter the calibrated labels at all.
  - The simulator enters only through the edge geometry (m, s, A), which sets the size of the called set and the nominal (about 9.7 at stage 1 and 19.9 at full).
  - At those sizes, a one-sided Poisson test at 0.05 has an exact size of at most 0.038 (lambda 9.67, k 16), 0.031 (lambda 10.17, k 17) and 0.050 (lambda 19.88, k 28) (scipy, computed here).
  - The observed 0.020-0.024 therefore sits BELOW the test's own ceiling. The leg measures only whether the LOAO refit inflates the test's size, and it does not.
  - "NOT DETERMINED" is correct for the simulator's bias. It omits one channel whose direction IS known: the calibrated labels are independent across edges, while the record's wrong events are overdispersed. Leg (f) on the merged board gives by-model chi2 53.40 on 20 models, p <= 0.0005, and DEFF 1.780 (L15597ff).
  - Overdispersion at a fixed mean fattens the upper tail, so it pushes the false-alarm rate UP. The 0.020-0.024 is a reading under no overdispersion (D3).
- **Key world, deciding nothing.** The simulated judge is called MISCALIBRATED in 124-154 of 1,000 replicates on the all-label count. The design leg's established count gives 0 of 1,000 for D1-stage1 and D1-full, against 175 and 138 all-label. This is a descriptive input to author decision 8: under this simulator, the choice of count alone flips about 14% of status words.

## Question 6 / defects list

- **D1 (HIGH): leg (d) is sign-blind, and the simulator does not reproduce the widener's slope sign.**
  - `identified` is `ddev >= 3.84` against b1 = 0, two-sided (g22.py L896, L914; cert.ddev_v). The established-label refit b1 is computed and discarded (`_, dd, _ = cert.ddev_v(...)`), so the design records cannot show its sign.
  - Proxies that the records can show:
    - The stored `b1` (the all-label pooled fit, `L["b1"]`) is <= 0 in 306 / 587 / 644 of 1,000 replicates (D4 / D1-stage1 / D1-full).
    - Among the replicates counted as identified, it is <= 0 in 93 / 182, 429 / 518 and 552 / 654. Identified AND b1 > 0: 89 / 89 / 102 of 1,000.
    - In the validity-v2 random mode, the mode these designs use: the stored `b1_est` has median -0.023 and 506 / 1,000 are <= 0, against the record's +2.6386 (G22_validity_v2.txt L36). Among its 233 identified replicates, 100 have b1_est <= 0.
  - Validity never targeted b1's value or sign; its ddev targets are sign-blind. The v2 review (L131) already called the ddev coverage "near-vacuous".
  - Consequences:
    - (d) BELOW and P4's interval-HELD say nothing about identifying the record's positive slope on a real k = 46 board.
    - The LOAO-nominal PRIMARY is refit on a simulated world whose slope is about 0. (c) is carried by the frozen reading, which also MEETS.
  - FIX (C1): record (d) as "sign-blind; SUBSTANTIVELY UNDETERMINED". Before the real-supply re-run:
    - store b1e per replicate;
    - register a signed identification rule (b1e > 0 and ddev >= 3.84);
    - add the widener slope to any future validity target set.
- **D2 (MEDIUM): the stop's MEETS mostly certifies the full-board read, not the stop.**
  - Stage-1 reads by margin: 960 / 210 / 1 / 0 of 1,000.
  - Conditional on the stage-1 branch:
    - margin 0: 19 / 960 = 0.020 [0.013, 0.031];
    - margin 1: 6 / 210 = 0.029 [0.013, 0.061], which CONTAINS 0.05, so that branch is UNRESOLVED;
    - margins 2 and 3: unexercised.
  - The "no status" branch was never exercised (projected minimum 16.53 against 4.5).
  - The printed "no status 0" hides 45 stage-1 reads at margin 0 (and 1 at margin 1) whose word is UNDETERMINED (LOAO nominal < 9 on the calibrated labels). They are counted as non-alarms.
  - FIX (C2): the outcome prints the per-branch conditional rates and the UNDETERMINED count, and states that only margins 0-1 exercise the stop.
- **D3 (MEDIUM): the stop's calibrated world has no overdispersion** (Question 5). FIX (C3): before the stop is adopted, a registered sensitivity with a model-level random effect at the measured DEFF 1.78. The outcome brackets the bias line: "direction NOT DETERMINED for the simulator's bias; UPWARD for the omitted overdispersion".
- **D4 (LOW): "HEAD at launch: 53eccb6" is false.** The heads were ed9c384 and 5e406fc (row 14). No numeric effect: the lf16 is identical. FIX (C4): the registrar's bracket.
- **D5 (LOW): two stale strings in the output.** "The real split is not drawn" (false at launch), and the PASS chip lacks the replay's fragility suffix. FIX (C5, with the file shas): print both corrections beside the outcome.
- **D6 (LOW): the chain gate checks replay_output_sha and registrar_commit by format only.** FIX at the next re-binding: compare them to pinned constants, or pin the chain file's sha256.
- **D7 (LOW): the supply manifest is read through a branch ref.** The ref is `worktree-agent-a11f8bf63949fabe0`, now 2c184be8, and not a commit sha. DEV is +6.7% against the split of record (4,002 vs 3,749). FIX: print the resolved commit.
- **D8 (MEDIUM): the owed re-run is not runnable as built** (Question 3, item 2). FIX (C6): register the stage-1 draw run, the stage-1-set input and a per-anchor supply builder, then a new re-binding and a delta READY, before the real-supply D1 and stop re-runs.

Refuted suspicions:
- "The stop and D1-full replicates are the same boards": 0 of 1,000 rows are equal. The shared ratio median of 1.3249 is a coincidence of a dense distribution.
- "The DB of record was touched": no (row 15).
- "Foreign readers during the run": 0 (row 16).

## Does not show

- Any reading at the EVAL supply of record, or at the registered stage-1 anchors.
- That a real k = 46 board would identify b1 (D1), or that its LOAO nominal behaves like the simulated one (the per-replicate corr of frozen with LOAO is 0.13, so the 1.325 is a ratio, not a map).
- The stop's false-alarm rate under overdispersed wrong events (D3), or at margins 2-3 on the stage-1 branch (D2).
- Anything about D0 or D2 (not run).
- Any board size: ruling 3 holds, and the author decides.
- Validity outside grok_calib's 12-model, 14-anchor board.
