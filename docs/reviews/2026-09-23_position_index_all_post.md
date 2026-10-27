# POSITION-INDEX-ALL: post-run numbers review (adversarial reviewer, 2026-09-23, zero calls, read-only)

Object: `experiment_results/position_index_all_outcome.txt` at b472d40 (blob:bb1578caf895568ec2484b41df77ce58ad171dbe;
sha256-lf 1c4370b23474cf3c... from `git show HEAD:<path> | sha256sum`; working-tree CRLF rendering sha256 5c7b12cb538a7917...).
Instrument `tools/analysis/position_index_all.py` blob:9c2ae4198971a0bd8984ed863f9fa20fd9aedf44 (sha256-lf16 8939144e5ce87636,
sha256-crlf16 6f6694eac5a176f8, both re-derived). Certificate `experiment_results/vote_frame_cert.json` blob:5ec19826a1b2bb33eccbe2810b389051906dd8c0,
status HELD, script_sha256_16_lf 72ceddfe919a982e; LF sha256_16 48e5f5a3d4dd02d0, working-tree (CRLF) sha256_16 c68a655ac64ae06d.
Registration: `docs/judge_v2_program.md` L13111-L13227 (b25bde0); rulings L13691-L13746, L14201-L14247, L14689-L14699.

Discipline: rule 7: no construction or site null running (two java.exe: the Gradle daemon started 11:35 and the Kotlin compile daemon;
no python process). Every DB opened `mode=ro&immutable=1`; -wal/-journal check: none beside any entered cache; `ratings_x12.db-wal`
0 bytes, `mmlu_pro_dataset_cache_v2.db-wal` 0 bytes. All 62 certified caches: size and mtime_ns equal to the certificate's (0 of 62 changed).
My own reader does NOT import the instrument or vote_frame_cert. Scratch (outside the repo):
`C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/pia_post/`
(`extract.py`, `stats.py`, `dups.py`, `c4.py`, `robust.py`, `copycheck.py`, outputs `*_out.txt`).

## 1. Recomputation: the family table (my reader; B 2000, numpy default_rng(42), cluster = (corpus, str(qid)), task_id on BFCL)

Rows entered: 118,833 in total, the same as the run's ENTERED 118,833. Per cache the counts are identical to every [COUNTS] line
(Kotlin board 9,123, kotlin_ae92 600, arena13 1,800, newcomer_placement 800, steps 400, placebo 599, BFCL 458 of 608).

| family | FF / SS / n (printed = mine) | clusters | Kish | s | SE_boot printed / mine / analytic cluster SE | interval, mine | DEFF printed / mine | MDE | n_eff (mine) | side |
|---|---|---|---|---|---|---|---|---|---|---|
| BFCL / grok-nr | 57 / 0 / 57 = | 25 = | 3.140 = | 1.000 = | 0 / 0 / 0 | [1.000, 1.000] | undef / undef | - (transported 0.352) | - | FIRST (descriptive) |
| IFEval / grok-nr | 259 / 18 / 277 = | 114 = | 3.484 = | 0.935 = | 0.0198 / 0.0194 / 0.0197 | [0.897, 0.973] | 1.78 / 1.72 | 0.112 / 0.110 | 161 | FIRST |
| MATH / grok-nr | 54 / 31 / 85 = | 71 = | 1.353 = | 0.635 = | 0.0568 / 0.0580 / 0.0585 | [0.522, 0.749] | 1.18 / 1.23 | 0.165 / 0.169 | 69 | FIRST |
| MMLU-Pro / Mistral | 790 / 4729 / 5519 = | 1522 = | 8.113 = | 0.143 = | 0.0083 / 0.0083 / 0.0082 | [0.127, 0.159] | 3.11 / 3.06 | 0.033 | 1801 | SECOND |
| MMLU-Pro / grok-nr | 2029 / 626 / 2655 = | 979 = | 5.447 = | 0.764 = | 0.0138 / 0.0141 / 0.0138 | [0.737, 0.792] | 2.81 / 2.92 | 0.046 | 908 | FIRST |
| MMLU-Pro / grok-r | 418 / 170 / 588 = | 324 = | 2.571 = | 0.711 = | 0.0246 / 0.0242 / 0.0245 | [0.663, 0.758] | 1.74 / 1.68 | 0.076 / 0.075 | 350 | FIRST |

FF, SS, n, clusters, Kish and s agree TO THE DIGIT for all six families, and every per-cache FF/SS line (58 lines) agrees exactly. The SE, DEFF
and interval ends differ only by bootstrap Monte Carlo error (at most 0.003 on an interval end; the analytic cluster SE lands between the two).
MDE arithmetic re-derived from the printed DEFF: 1.4 x sqrt(DEFF/n) gives 0.165 / 0.033 / 0.046 / 0.076 / 0.112, all as printed; BFCL
1.4 x sqrt(3.60/57) = 0.352 and the Kish bound 1.4 x sqrt(3.14/57) = 0.329, as printed.
A note on my own evidence: my first pass keyed clusters on the raw qid, and the three match_history-mapped caches (rejudge_grok, rubric_ladder,
rubric_swap) carry TEXT qids, so it split clusters (Mistral 1,941, grok-nr 1,141). The instrument's `str(q)` (L331) is the correct key and is
load-bearing. With it I get exactly 1,522 / 979.

## 2. Per-claim verdicts

| # | claim (as printed) | verdict | evidence (command) | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | C1 HELD: BFCL 458 / FF 57 / SS 0 | CONFIRMED | extract.py: schedule stratum='headline' and nj empty -> 458; fwd/rev `vote` | 458 / 57 / 0 vs 458 / 57 / 0; 25 task clusters | - |
| 2 | Family FF/SS/n/s (all six) | CONFIRMED | stats.py | table above, exact | - |
| 3 | Transposition of the 4 CERTIFIED-CONTESTANT caches (order-1 first = NEW / newcomer / GEM, order-2 first = opponent) | CONFIRMED | extract.py LONGC; per cache arena13 117/23, newcomer 29/16, steps 13/10, placebo 47/5 | exact | - |
| 4 | "a sign error in the transposition would flip a family's side" (the question asked) | REFUTED (it would not) | dups.py SIGN-SCENARIO: the 4 caches sit only in MMLU-Pro/grok-nr. Transposition withheld = order-2 label inverted: FF 4159 / SS 1402, s 0.748 [0.732, 0.764] FIRST; the 4 caches dropped: s 0.761 [0.733, 0.790] FIRST | side unchanged in every scenario | - |
| 5 | Family assignment per FAMILY_MAP | CONFIRMED | map read against run_meta/meta: Kotlin judge_calls judge_model = grok-4-1-fast-non-reasoning on 100% of rows (9,123x2, 600x2); newcomer(_steps) meta judge_model grok-nr; gen_arena `source` splits MATH 1,800 / IFEVAL 1,200 | 50 entered, 12 excluded, as printed | - |
| 6 | Same judgment entering a family twice | NONE FOUND | dups.py: 0 duplicate (raw1, raw2) groups in any family; 1 repeated raw1 in 62,154 Mistral rows; copycheck.py: vote agreement between re-judgings of the same match 0.69-0.87 (Kotlin board vs grok_calib 0.831 on 9,123; stack_v2 vs promptv2 0.806; rubric_ladder vs stack_v2 0.828), the test-retest level, never 1.000 | no copy | - |
| 7 | Reuse of the same question-pair across caches is clustered | CONFIRMED | robust.py REUSE: rows per (q, pair) mean 2.76 (max 36) on Mistral, 3.11 (max 17) on grok-nr; cluster bootstrap equals the analytic cluster SE; naive binomial SE on Mistral 0.0047 against 0.0083 clustered (DEFF 3.1, which the clustering absorbs) | - | - |
| 8 | Sided verdicts robust to how reuse is weighted | CONFIRMED | robust.py DEDUP. One flip per question: Mistral 0.191 [0.170, 0.211] S; grok-nr 0.745 [0.716, 0.773] F; grok-r 0.682 [0.631, 0.733] F; MATH 0.634 [0.522, 0.746] F; IFEval 0.930 [0.884, 0.975] F | no side changes; Mistral's point moves +0.05 with weighting | - |
| 9 | Side rule: interval = s +- 1.96 SE_boot, sided iff it excludes 0.5 | CONFIRMED | instrument L398-L434 read; my intervals from the same rule | as registered | - |
| 10 | Support: MDE <= 0.35, >= 2 corpora supported | CONFIRMED | 3 corpora supported (MMLU-Pro, MATH, IFEval); the largest MDE is 0.165 (MATH) | as printed | - |
| 11 | BFCL UNSUPPORTED (ruling (3)) | CONFIRMED as ruled; see D4 | DEFF 0/0; transported MDE 0.352 > 0.35 | - | LOW |
| 12 | C2 HELD (primary): every supported family sided | CONFIRMED as registered, FRAGILE | see D1: MATH lower end 0.524 (mine 0.522; 20 seeds 0.519-0.523; CP at n_eff [0.511, 0.748]) | margin 0.024 = 0.42 SE | MEDIUM |
| 13 | C2 permits Mistral SECOND with grok FIRST | CONFIRMED | registration L13154-L13156, verbatim: "HELD iff EVERY supported family is FIRST- or SECOND-SIDED; FAILED iff at least one supported family is UNRESOLVED. ... the direction is not required to be uniform (that is C3)." | - | - |
| 14 | C3: judges differ in direction | CONFIRMED | grok-nr FIRST on 3 corpora, grok-r FIRST, Mistral SECOND | - | LOW (D5) |
| 15 | C4 (a) AGREE-ORDER shares | CONFIRMED to 4 dp | c4.py against mmlu_pro_dataset_cache_v2.db eval_results.pred: AGREE 8922 .0184/.0474/.3484; DISAGREE 10442 .0071/.0538/.1228; UNDET 2172 .0115/.0405/.2063; ALL 21536 .0122/.0498/.2246 | exact | - |
| 16 | C4 (b) POSITION-DECOMP; (c) POSITION-FULL | CONFIRMED | c4.py arena13 by schedule.frontier: (b) n 600, 0.695 / 0.560, d -0.135, FF 81 SS 9, s 0.900; (c) n 1200, 0.910 / 0.899, d -0.011, FF 36 SS 14, s 0.720 | exact | LOW (D6) |
| 17 | C4: no sign change | CONFIRMED | - | - | - |
| 18 | P1 57/0 | CONFIRMED | = C1 | - | - |
| 19 | P2 Mistral SECOND, s in [0.10, 0.35] | CONFIRMED | 0.143 on the pooled family; on P2's own parenthesis (x12 + x20 only) FF 263 / SS 1073, s 0.197: in the band either way | - | - |
| 20 | P3 grok FIRST, s in [0.55, 0.80] | CONFIRMED | grok-nr 0.764; pooling grok-nr with grok-r would give 2447/3243 = 0.755, also in the band | - | - |
| 21 | P4 s 1.000 in [0.93, 1.00], point only | CONFIRMED, not independent of P1 | 57/57 | - | LOW (D7) |
| 22 | P5 C2 HELD, grok first, Mistral second | CONFIRMED | - | - | - |
| 23 | Falsifiers not fired | CONFIRMED | - | - | - |
| 24 | FLIP-RESEED "confirmatory rather than separating" is the registration's own statement | CONFIRMED (registration's words), reading OVERSTATED | see D2 | - | MEDIUM |
| 25 | Pins and hygiene | CONFIRMED | blobs re-derived (`git hash-object`); 62/62 caches unchanged since the certificate | - | LOW (D3) |

## 3. The FLIP-RESEED note, quoted
Registration, DEPENDENCIES (L13126-L13129), verbatim: "if one-sided composition proves GENERAL (C2 HELD), BFCL-FLIP-RESEED's C1 HELD would be
CONFIRMATORY rather than separating and the author may prefer not to buy its 200 calls; the launch decision is the author's and the
experiment-manager's; nothing in either registration's criteria changes." The outcome's L220 reproduces this; it is the registration's statement,
not the instrument's gloss. The same record also says, in BFCL-FLIP-RESEED's own dependency bracket (L12310-L12314): "NOTE ALSO WHAT THE INDEX CANNOT
DO, which is why this test is not withdrawn by the bracket: a marginal index over caches is a MARGINAL object, and this test is the only
registered instrument that asks whether the flip SET is stable AT THE MATCH LEVEL". The outcome quotes the first sentence and not the second.

## 4. Defects

- **D1 MEDIUM: C2 HELD rests on one family at the edge, and within it on one cache.** MATH/grok-nr's lower end is 0.524 (0.42 SE above 0.5).
  Leave-one-cache-out (robust.py LOCO): without gen_arena_grok.db (33 flips, s 0.758), stage3_math_grok_v2_capfree alone is 29 / 23, s 0.558
  [0.403, 0.713], UNRESOLVED, and C2 would be FAILED. The two caches use different prompts (GEN-ARENA vs prompt_v2 verify-first) and share
  only 112 of their questions. The verdict is as registered and is stable across bootstrap seeds (20 of 20 above 0.5). But the sentence of record must
  say that C2's HELD is decided by MATH at a margin of 0.024. Every other supported family clears 0.5 by at least 0.16 on the near end. Fix:
  add a sentence to the record (below); no re-run.
- **D2 MEDIUM: "one-sided flip composition is GENERAL" overstates what C2 measured.** C2 tests s != 0.5. BFCL's parent fact is 57 / 0
  (s = 1.000). BFCL's point is above the UPPER end of every supported family (IFEval 0.974, MMLU-Pro/grok-nr 0.792, grok-r 0.758, MATH 0.749);
  no supported family has SS = 0; and one judge is sided the OTHER way (Mistral 0.143). What generalises is a first/second IMBALANCE among
  both-decisive flips. The degree of BFCL's one-sidedness does not generalise, and neither does its direction, across judges. And the match-level question FLIP-RESEED
  asks is, by the record's own words, outside the index. Fix: the sentence of record uses "sided" and quotes both halves of §3.
- **D3 LOW: the certificate's pin is printed unlabelled.** `[CERT] ... sha256_16 c68a655ac64ae06d` is the working-tree CRLF rendering. The LF
  rendering is 48e5f5a3d4dd02d0 (`git show HEAD:experiment_results/vote_frame_cert.json | sha256sum`). Fix: the registrar's record names both,
  LF first.
- **D4 LOW: ruling (3)'s "under either available number BFCL fails" meets a third number that passes.** The Kish (rho = 1) bound DEFF 3.14,
  from BFCL's own clusters, gives MDE 0.329 <= 0.35. It is printed and "decides nothing". Verdict impact: none. C2 has three supported corpora
  without BFCL, and the with-BFCL reading is also HELD, although only on a degenerate [1.000, 1.000] interval, which is no evidence of support. Fix: none needed; note it
  if ruling (3) is ever cited as a precedent.
- **D5 LOW: C3 prints "the same side across its corpora" for judges with ONE corpus** (Mistral, grok-r). That consistency is vacuous. Only
  grok-nr has more than one corpus (three). Fix: in the record, say "one corpus only" for Mistral and grok-r.
- **D6 LOW: C4(c)'s sign test compares the recorded statistic with itself.** The registration asks for POSITION-FULL's "no direction" to be "re-read as
  s". s = 0.720 (36 / 14, n 50) is printed but not tested. The sign test runs on d = -0.011, which is the prior number recomputed on the same
  certified-positional frame, so it could not change. Its sign agrees with s > 0.5 (first-favoured), so nothing changes. Fix: record s = 0.720
  beside "no direction", with n = 50 flips and no interval.
- **D7 LOW: "P1-P5 HELD" is not five independent passes.** P4 (point in [0.93, 1.00]) is implied by C1 = P1 (57 / 0). P5 is implied by C2 together
  with the P2/P3 sides. Fix: record "P1-P5 HELD (P4 follows from P1; P5 from C2 and P2/P3)".
- **D8 LOW: C5 omits a family.** MMLU-Pro / DeepSeek-R1-0528 (rejudge_deepseek_r1_0528.db, 3 matches entered, 0 both-decisive flips) is
  entered (outcome L49) and absent from the FAMILY TABLE: `grep -c DeepSeek` on the outcome returns 1. Registration (g) says s is undefined where
  FF + SS = 0; the table should print it as such. Fix: the registrar lists it in the record as "entered, 0 flips, s undefined".

No BLOCKER, no HIGH. No number in the outcome is wrong.

## 5. Sentence of record (proposed)
"POSITION-INDEX-ALL (0 calls): C1 HELD (BFCL 57 / 0 on 458 deciding matches, certified frame); C2 HELD as registered: all five supported
families are SIDED (MMLU-Pro/grok-nr 0.764 [0.737, 0.791], grok-r 0.711 [0.663, 0.759], IFEval/grok-nr 0.935 [0.896, 0.974], MATH/grok-nr
0.635 [0.524, 0.747], MMLU-Pro/Mistral 0.143 [0.127, 0.159]), in OPPOSITE directions by judge (grok first, Mistral second). The HELD is decided by MATH at a
margin of 0.024 above 0.5, which rests on one of its two caches. BFCL's 1.000 lies above every supported family's upper end, so the imbalance generalises and
BFCL's degree of one-sidedness does not. The registration states that C2 HELD makes BFCL-FLIP-RESEED's C1 confirmatory rather than separating.
The record also states that the index is marginal and cannot answer FLIP-RESEED's match-level question. Numbers reproduced independently
to the digit (FF, SS, n, clusters, Kish, s); SE and DEFF within bootstrap error."

## 6. What this does not show
- Why any judge prefers a position, or why grok and Mistral are sided in opposite directions (judge and prompt are confounded: Mistral appears only on MMLU-Pro, under a different set of recipes).
- That BFCL's s = 1.000 is typical: it is not reproduced in any family.
- Anything at the match level: whether a flip SET reproduces on re-posting (FLIP-RESEED's question).
- Anything about the 12 excluded caches (rubric_contrast's Mistral rows, rubric_j6, bfcl_final_state_swap, leaf_powered, refgated, _backup copies).
- Any fidelity, board, tier or ranking number, and any recommendation to judge in one order (ORDER-1 / SELECTIVE-ORDER stay closed).
- That the pooled s is recipe-invariant. The per-cache s ranges from 0.000 to 0.217 (Mistral), 0.565 to 0.910 (grok-nr) and 0.571 to 0.847 (grok-r). The pooled s is a flip-weighted mean dominated by
  the R3 reuse sample (Kish 8.1 / 5.4), and one flip per question moves Mistral from 0.143 to 0.191.
- MATH sidedness independent of gen_arena_grok.db.

## 7. Verdict
Numbers: **CONFIRMED** (every deciding count to the digit; intervals within bootstrap error). C1, C2 (as registered), C3, C4, P1-P5: **CONFIRMED**.
The FLIP-RESEED line: **registration's own statement, CONFIRMED as quoted; reading OVERSTATED (D2)**. Defects: 0 BLOCKER, 0 HIGH, 2 MEDIUM
(D1, D2: wording of record, no re-run), 6 LOW (D3-D8). The outcome stands; the record needs the D1/D2 qualifiers.
