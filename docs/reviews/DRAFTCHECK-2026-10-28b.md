# DRAFTCHECK 2026-10-28b: BZ-AXIS-CONFIRM-FRESH draft amendment per D-2026-10-28-2 (TaxoArena 4cc73b0b)

Reviewer: adversarial reviewer, 2026-10-28. Authority: D-2026-10-28-1 and D-2026-10-28-2 (f81992b1). Zero LLM calls. Read-only on
both repositories and on E: (fresh lists, FRESH-SIZE outputs); nothing was run except git, grep and short read-only scripts.

Reviewed: `docs/judge_v2_program.md` section "## Registrar's record 2026-10-28 (insertion only; zero calls; nothing run) —
BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-28-2: ..." L25778-L25798 (_as_of 4cc73b0b), the 7 brackets on L25743-L25775, the
queue items BZ-AXIS-CONFIRM-FRESH and FRESH-MATH-PIPELINE, FRESH-MATH-PIPELINE.json and INDEX.md.

Sources:
- the draft sections L25692-L25776;
- DRAFTCHECK c98534d2, a8004083 and 6dc736e9;
- READY_fresh-math-pipeline delta (c5da09b8);
- POSTRUN_FRESH-SIZE (613c1c03) and POSTRUN_FRESH-RULES-SIM (8bebb4ee);
- benchzoom 0be0164 and 4676efb;
- E:/benchzoom_demo/followups/fresh-size (SHA256SUMS 5/5 OK).

No code is under review, so there are no mutants.

## Verdict

**SOUND WITH EDITS.** The amendment is insertion only and claims no registration.

- **D-2026-10-28-2 (1)-(4) is applied as worded.** D_K, D_N and G(N|L2+V0) decide on SE_cell. P prints its interval with no word and no
  bar. The fresh list is v3: 7,058 items, full sha256 reproduced. No temperature is sent, and each model's value is recorded. Roster,
  serving and the go stay open.
- **Every deciding number traces to its source and reproduces.** The table matches 36/36. The power, S-RES, floor, list and Kish figures
  all reproduce.
- **Labels.** No n* is claimed. The EXTRAPOLATION label is verbatim. Multiplicity is stated: one family, Holm at FWER 0.05 with m = 4,
  flagged as Q1.
- **Earlier checks resolved.** DRAFTCHECK-2026-10-28 D1-D7 and c98534d2 F1-F7 are recorded and resolved or carried.

There is no BLOCKER and no HIGH. Two MEDIUM:
- **G1:** a false absence claim about the record. Section C says no resampling factor for D_N or G(N|L2+V0) is in the record, but one is.
- **G2:** D writes the structural leg on the clustered lower bound and calls P's floor "under SE_cell". This conflicts with the open
  a8004083 D1, and under S-RES D_K's no-growth floor exceeds its distance.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Reviewer's result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only. Span L25778-L25798, parent c5da09b8. LF | **Programme:** numstat 28/6. difflib on the 6 changed lines: insert-only ops, 7 of 7 (7 brackets on 6 lines: L25743, L25764, L25766, L25773, L25774 and L25775 x2). 25,771 lines identical; 22 lines added after old L25776. 0 CR in all 4 committed blobs. `merge-base --is-ancestor c5da09b8 4cc73b0b` = 0. Commit = 4 files, ledger not among them. **Queue:** 271 -> 271 items, order kept; 12/12 changed fields are append-only (11 `startswith`, `depends_on` + TAU-CONT-ALL). **Results JSON:** replaces `script.sha16/commit`, `review.commit/verdict` and `last_update`. That is the record's practice for state fields (77 such removed lines in the last 30 results commits), and the old verdict stays in L25766 | CONFIRMED | - |
| 2 | D-2026-10-28-2 applied exactly | **Quotes:** the 4 selections and the re-ask sentence are exact substrings of the decisions file (5/5). **(1)** The three deciding contrasts are the decision's "k-means vs tree, kNN vs tree, kNN beyond the tree". P gets point, SE_cell, 95% interval and meter z/p beside, with NO word and NO bar. **(2)** Roster and serving stay open (J(1), Q2). **(3)** v3 sha256 169f99b714dc6ef548311e64528936901fec698181208c9800439ab0b36ddeab, full hex equal; 7,058 lines. **(4)** No backend sends a temperature; the C6 bracket quotes are equal to plan L245-L248 at 0be0164; `MAX_TOKENS 8192` and `NUM_CTX_EXTRA 4096` are in the script blob | CONFIRMED (G3, G6d) | - |
| 3 | Holm over m = 4 at FWER 0.05: \|z\| 2.498/2.394/2.241/1.960; MDE80 x3.339; Bonferroni sum lapses | Own: 2.4977/2.3940/2.2414/1.9600; 2.4977 + 0.8416 = 3.3393. A descriptive member counted in m is never less stringent for the 3 deciding contrasts than m = 3: thresholds are equal if it is rejected first and stricter otherwise. So "conservative" holds. The two-sided Holm F rule since 2026-10-23 is verbatim at L25698. [E3] m = 4 is at L25716 | CONFIRMED | - |
| 4 | C: planning table at n 7,058 (R 69/35/18), the reading column, D_K under S-RES, the DESCRIPTIVE P and G(V0) figures | projection.csv equals the table at 3 decimals: **36/36**. Reading column 9/9 (central vs distance; band top/bottom). D_K S-RES R 69: 0.1392-0.1988. P cell 0.2107/0.2894/0.4257. Power at 0.10: cell 0.1196/0.0472/0.0180, meter 0.6064/0.1844/0.0573. S-RES R 69 power Phi(0.10/(0.29504/3.8416) - 3) = 0.0448. G(V0): 0.0833/0.1066/0.1514, S-RES 0.3250-0.3667. D_N trend 0.21542 vs band top 0.21530. **But** "no resampling factor for D_N or G(N\|L2+V0) is in the record" is false (G1) | CONFIRMED / REFUTED (G1) | MEDIUM |
| 5 | D: floors D_K 0.134, D_N 0.126, G(N) 0.136, G(V0) 0.038, P 0.183; "every deciding word reachable at infinite budget"; P DESCRIPTIVE at the cap | The numbers equal L25718 (g) and L25732 (b). The conditioning conflicts with the open a8004083 D1 / row 7. Under S-RES, D_K's floor is 0.134 x 1.4-2.0 = 0.188-0.268 > 0.17 (G2) | numbers CONFIRMED; leg PARTLY | MEDIUM |
| 6 | E: v3 = v2's 6,902 verbatim + 156 with exactly one empty option (142/11/2/1); key empty 0; Kish for v3 = SPEC 6,968 / 1.030 | **Own read of v3:** 6,902/6,902 v2 lines are verbatim in v3. The 156 new items each have exactly 1 empty option (`''` 142, `' '` 11, `'\n'` 2, `'  '` 1); key empty 0; non-empty options distinct 156/156. **Cluster field:** v3 has 6,968 clusters, Kish 1.0298, n_eff 6,854, SE x1.0148; v2 has 6,818 / 1.0275 | CONFIRMED | - |
| 7 | F/G: pins and delta numbers; NOT READY gate; not merged | **Pins:** rev-parse at 0be0164: script 90642e2fba6015c8, go config aadd03e8, plan e662397d, 0 CR each. **Commits:** a55f921, 48fed00 and 0be0164 are on the branch; `--is-ancestor 0be0164 master` rc 1 (master 06c075f). **Quotes:** the c5da09b8 verdict, Merge, extraction-v2 and `i/lf w/lf` quotes are verbatim. **Delta numbers:** rows 1-7, 9, 10 and 14 match (44/44, 28, 971/1, 135/135, 49,406, 14/14, 14,005/14,039, 24 recorded as 29, gemma3:12b 0.1, gemma3:1b 1, llama3.2 unset). **Gate:** local D3, D4, T1/T4/T5; Azure also D1, D2. This equals the review's verdict | CONFIRMED (G6a) | - |
| 8 | No n* | 6 mentions of n* in L25778-L25798, all negations or attributions. "n is capped at the pool: 7,058" is a cap, not an n* | CONFIRMED | - |
| 9 | Extrapolation labelled | The label is a verbatim substring of L25773 / fresh-size.md. The S-RES and floor comparisons are labelled "registrar's comparison" or "on the draft's transport" | CONFIRMED | - |
| 10 | DRAFTCHECK-2026-10-28 D1-D7 resolved | **D1:** H(1) and J. **D2:** WHO DECIDED (re-asked) and the L25773 bracket. **D3:** D plus J(3). **D4:** L25775 bracket and J(3). **D5:** L25766 bracket and G's gate. **D6:** L25764, L25774 and the results bracket ("6 of 8 survived, 4 decisive"). **D7:** E (verified, row 6). D3's own wording carries the G2 defect | CONFIRMED (D3 PARTLY, G2) | - |
| 11 | c98534d2 F1-F7 recorded | **F1:** resolved, with n fixed by D-2026-10-28-1 (1) and -2 (3); FRESH-DESIGN-SURFACE is already in `depends_on`. **F2:** "the registrar's reading" plus code owed with a COUNT per reader family. **F3:** `depends_on` + TAU-CONT-ALL. **F4/F6:** owed; the F6 pins are equal to the review's. **F5:** the L25743 bracket. **F7:** moot | CONFIRMED | - |
| 12 | Earlier answers intact (rule B decides; N_A = N'; continuous tau^2; cell-aware primary) | **Rule B:** "DECIDING, under rule B" (A). **N_A = N':** untouched (only the bracket insertions change lines above); J(4) owes only the two assignment functions, consistent with 10-27 C (ii). **Continuous tau^2:** J(3), J(4). **Cell-aware primary:** B. **Gaps:** J drops two items of the 10-27 list (G5), and there is no D-2026-10-21-1 check (G4) | CONFIRMED (G4, G5) | LOW |
| 13 | 28178852 G3 met; ledger unchanged v430 | D-2026-10-28-2 occurrences, c5da09b8 -> 4cc73b0b: prog 0 -> 20, queue 0 -> 10, FRESH-MATH-PIPELINE.json 0 -> 7. `test_ledger.html` is not in the commit | CONFIRMED | - |

## Defects (each with a fix; all insertion-only, at the registrar's next record, before the full registration)

- **G1 MEDIUM: C claims an absence that the record refutes.** C says "no resampling factor for D_N or G(N|L2+V0) is in the record
  (OWED ...)". The record carries one in four places:
  - POSTRUN_FRESH-RULES-SIM M1, which C cites in the same sentence: "1.4x (P), 1.4-2.0x (D_K), 0.9-1.1x (kNN), 3.9-4.4x (G(V0|L2+N))".
  - FRESH-SIZE summary.txt L122 (S-RES): "D_N 0.9-1.1, G(N|L2+V0) 0.9-1.1".
  - fresh-size.md at 4676efb, L56 and L114-L115.
  - projection.csv `res_central`. D_N: [0.1146, 0.1400] / [0.1802, 0.2202] / [0.2751, 0.3363]. G(N|L2+V0): [0.0953, 0.1165] /
    [0.1474, 0.1801] / [0.1903, 0.2326], each at R 69 / 35 / 18.

  POSTRUN_FRESH-SIZE row 12 (and E of a9138c19) leave the kNN factor out, which is likely where the absence came from. Q2 relays the
  incomplete picture: it names D_K's factor and is silent on the kNN contrasts.

  Fix: bracket C and Q2 to say the following.
  - The record's kNN factor is x0.9-1.1. It comes from one split at n 885, from the simulation's near-degenerate kNN readers (rho ~0,
    POSTRUN_FRESH-RULES-SIM L58), so it is weak.
  - Under it, D_N and G(N|L2+V0) stay below their distances at R 69 and 35. At R 18, G(N|L2+V0) stays below (0.190-0.233), while D_N
    does not (0.275-0.336 > 0.25).
  - The factor under the declared scheme stays OWED.
- **G2 MEDIUM: D writes the structural leg on the lower bound and mislabels P's floor.**
  - **What D says.** "P under SE_cell 0.183 > 0.10, unreachable at any n without leaf growth". In B, SE_cell is the declared rule-B
    resampling SE.
  - **Why that conflicts with the record.**
    - The 0.183 floor exists only for a cell-clustered SE. Under the declared resampling SE the floor is UNDETERMINED (a8004083 row 7;
      D1 open, carried in J(3)).
    - The 10-27 record B (L25740) dropped exactly this clause on that ground.
  - **The second half has the same problem.** "Every deciding word is reachable at infinite budget on the draft's transport" holds only
    on the clustered form, which B itself calls the LOWER bound of the deciding SE. With S-RES applied, D_K's no-growth floor is
    0.188-0.268, above 0.17. The wording came from DRAFTCHECK-2026-10-28 D3, the reviewer's own.
  - **Fix: bracket D to say the following.**
    - The floors are on the clustered form, a lower bound.
    - Under the declared resampling SE_cell the floor is UNDETERMINED (a8004083 row 7).
    - With S-RES x1.4-2.0, D_K's no-growth floor exceeds 0.17.
    - The expected case under B is cell growth (c 0.007439, FRESH-RULES-SIM licence), and with growth there is no floor.
    - The registration shows D_K's structural leg under the declared SE, or conditions it on growth.
    - Rename P's floor "on the clustered form".
- **G3 LOW: PF5 still scores C1(V0').** D (L25790) carries "each PF's FAIL observable is its range and word", pointing at L25717. So PF5 (C1(V0'), range
  [0.00, +0.25]) still prints HOLDS / FAILED. D-2026-10-28-2 (1) says P "carries no pass/fail word". Fix: state the reading, either
  "PF5-PF7 are prediction scores, not P's word" or "PF5 is not scored", and add it to Q1.
- **G4 LOW: no D-2026-10-21-1 check.** L25778-L25798 has 0 occurrences of D-2026-10-21-1. The 10-23 record held that "C1(V0) the
  primary criterion; the flat contrasts ... never move the primary word". Fix: add one line. V0' (the full axis_v1 tree) remains the
  tree in every deciding contrast; C1(V0') stops deciding by the newer D-2026-10-28-2 (1); the zoom curve stays secondary. No conflict.
- **G5 LOW: J drops two items of the 10-27 list (5).** The missing items are "the cont rule in the Instrument" and "the falsifiers F-FLAT
  and F-RESID final". Both were already absent from a9138c19's G, and 6dc736e9 did not catch it. Counts: "Instrument" 0 and "cont rule"
  0 in L25760-L25798, against 2 and 6 in L25736-L25745. Fix: add both to J(3), with F-FLAT final and F-RESID descriptive per Q1.
- **G6 LOW: wording.**
  - (a) "go config ... blob:aadd03e8 = {}": the blob is a JSON object with a `note` and `"authorised_go": {}`. The shorthand comes from
    c5da09b8.
  - (b) The commit message and the queue note say "6 dated brackets", but I lists 7, on 6 lines.
  - (c) INDEX's FRESH-MATH-PIPELINE line still opens with the superseded v2 (6,902; e39bb5f4). The generator prints the sentence head,
    and the v3 update sits in a trailing bracket.
  - (d) For API models, "recorded per model" records "deployment default (not sent; not reported by the API)", which is no value. The
    default is unobservable. Disclose it as such, and fold it into Q3.

## Questions that remain for the author (relayed; the registrar's Q1-Q5 stand)

- **Q1** (registrar): are G(V0'|L2+N') and F-RESID descriptive, and does Holm run over m = 4 or m = 3? To add: is PF5 scored (G3)?
- **Q2** (registrar): serving and roster. Put it with the kNN factor (G1), not only D_K's.
- **Q3** (registrar): for local models, is the default the Modelfile's or the model card's? To add: for API models the default is not
  observable (G6d). Accept "not sent" as the record?
- **Q4** thinking. **Q5** the D6 extraction cases. Then the call cap, and whether to keep llama3.2 1b/3b.

## Commands (read-only; scratch = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad)

```
git show 4cc73b0b --numstat --format=; git show 4cc73b0b --name-only --format= | wc -l          # 13/12, 40/15, 1/1, 28/6; 4 files
python prefix.py; python -I nonprefix.py; python -I ctx.py   # 25,771 identical; 6 lines insert-only (difflib), 7 brackets; contexts
git show 4cc73b0b:<f> | tr -cd '\r' | wc -c                  # 0 for prog, queue, results JSON, INDEX
python qdiff2.py              # queue 271->271, order kept, 12/12 append; results JSON: 5 fields replaced, rest appended
python -I quotes.py; python -I q2.py   # selections 4/4 + re-ask exact; c5da09b8 quotes exact; SIZE C-2, M-1 exact
python -I tab3.py             # projection.csv vs C: 36/36; res_central D_K .1392-.1988, D_N/G(N) (G1); P power .1196/.0472/.0180
sha256sum E:/benchzoom_cache/fresh_math/fresh_items_v3.jsonl   # 169f99b714dc6ef5...0b36ddeab (full hex equal)
python -I kish3.py <v3>; python -I v3chk.py   # 7,058; 6,968 clusters, Kish 1.0298; 6,902 verbatim; 156: 142/11/2/1, key empty 0
grep -n 'S-RES' E:/benchzoom_demo/followups/fresh-size/summary.txt   # L122 "D_N 0.9-1.1, G(N|L2+V0) 0.9-1.1" (G1)
grep -n 'M1' docs/reviews/POSTRUN_FRESH-RULES-SIM.md                 # L89 "0.9-1.1x (kNN)" (G1)
sed -n '29,39p;40,52p' docs/reviews/DRAFTCHECK_BZ-AXIS-CONFIRM-FRESH-2026-10-26.md   # a8004083 row 7 / D1 (G2)
git -C Z:/FAC/TUBerlin/benchzoom rev-parse 0be0164:{examples/fresh-math-pipeline.py,examples/fresh-math-pipeline_go.json,docs/fresh-math-pipeline.md}
git -C Z:/FAC/TUBerlin/benchzoom merge-base --is-ancestor 0be0164 master   # rc 1 (master 06c075f)
for f in prog queue results: git show {c5da09b8,4cc73b0b}:$f | grep -o D-2026-10-28-2 | wc -l   # 0->20, 0->10, 0->7
sed -n '25778,25798p' docs/judge_v2_program.md | grep -o 'D-2026-10-2[01]-[0-9]'   # only D-2026-10-20-4 (G4)
python -I -c "NormalDist: Holm 2.4977/2.3940/2.2414/1.96; 3.3393; P S-RES power 0.0448; D_K floor x1.4/2.0 0.188/0.268"
```
