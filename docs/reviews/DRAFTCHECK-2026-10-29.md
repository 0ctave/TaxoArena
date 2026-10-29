# DRAFTCHECK 2026-10-29: BZ-AXIS-CONFIRM-FRESH draft amendment per D-2026-10-29-1 and DRAFTCHECK-2026-10-28b (TaxoArena 79ce688a)

Reviewer: adversarial reviewer, 2026-10-29. Authority: D-2026-10-28-1, D-2026-10-28-2 (f81992b1), D-2026-10-29-1 (4ea20c63).
Zero LLM calls. Read-only on both repositories and on E: (FRESH-SIZE outputs); only git, grep and short read-only scripts ran.
No code is under review, so there are no mutants.

Reviewed: `docs/judge_v2_program.md` section "## Registrar's record 2026-10-29 (insertion only; zero calls; nothing run) —
BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-29-1 and DRAFTCHECK-2026-10-28b: ..." L25800-L25819 (_as_of 79ce688a); the
9 brackets on L25781-L25797; the queue items BZ-AXIS-CONFIRM-FRESH and FRESH-MATH-PIPELINE; FRESH-MATH-PIPELINE.json; INDEX.md.

Sources: author_decisions 2026-10-21 / -28 / -29; DRAFTCHECK-2026-10-28b (bbc495d4, "DC"); READY_fresh-math-pipeline delta
2026-10-29 (9944e168, "DELTA3"); POSTRUN_FRESH-SIZE (613c1c03); POSTRUN_FRESH-RULES-SIM; DRAFTCHECK a8004083;
E:/benchzoom_demo/followups/fresh-size (SHA256SUMS 5/5 OK); benchzoom 2a5bf9d, 12abc39, 033c79c.

## Verdict

**SOUND WITH EDITS.** No BLOCKER, no HIGH. One MEDIUM (H1), four LOW (H2-H5).

- **Insertion only, as claimed.** 6 changed lines, all insert-only; 9 brackets; 21 lines appended.
- **D-2026-10-29-1 (1)-(4) applied as worded.** One attribution is labelled wrongly (H3).
- **DC G1-G6 resolved.**
- **Every deciding number reproduces from its source:**
  - Holm m = 3 values;
  - the 3.2356 multiplier and the 0.969 rescaling;
  - 9/9 S-RES cells, 9/9 clustered centrals;
  - the descriptive P and G(V0) cells;
  - the floors under S-RES and under m = 3;
  - the pins.
- **Labels.** No n* is claimed. The EXTRAPOLATION label is verbatim. Earlier answers are intact.
- **H1 (MEDIUM).** The new power reading drops a qualifier the record requires: POSTRUN_FRESH-SIZE M-1's "central" qualifier, which binds "any copy".
  - The reading "D_N and G(N|L2+V0) powered at R 69 and 35" holds only under the central a = 0.5.
  - Under the measured trend, D_N at R 35 is not powered and G(N) straddles its distance.
  - The unqualified line reaches the author in Q2.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Reviewer's result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; span L25800-L25819; parent 9944e168 | **Programme:** numstat 27/6. difflib on the 6 changed lines (L25781, 25789, 25790, 25792, 25796, 25797): insert-only, 9 `[CORRECTED 2026-10-29` brackets (1/1/2/2/1/2). 25,793 of 25,799 positions identical; 21 lines appended (heading L25800, last L25819). 0 CR in all 4 blobs. `--is-ancestor 9944e168 79ce688a` rc 0. 4 files; test_ledger 0 (`grep -c`). **Queue:** 271 -> 271 items, order kept; every changed field is append-only except 2 `last_update`. **Results JSON:** state fields replaced (script.sha16/commit, review.file/commit/verdict, last_update), old values kept in brackets; the rest appended. **INDEX:** `results_index.render(load())` equals the committed file (287 records, 0 errs) | CONFIRMED | - |
| 2 | D-2026-10-29-1 applied exactly | **Quotes:** the 4 selections and "every model reasons in visible text as the prompt asks" are exact substrings of the decisions file. **(1)** m = 3 over D_K, D_N, G(N'\|L2+V0'); G(V0'\|L2+N') outside m; PF5 prints no HOLDS/FAILED. **(2)** think=false only to capability-reporting models. Refusals: DELTA3 row 12; also blob 911f616f L273 `API_THINKING_ONLY` and L313/L930 `REASONING_ONLY` (qwq, deepseek-r1, magistral) + gpt-oss. **(3)** Modelfile recorded; API not sent, called unobservable. **(4)** Clear forms are read, ambiguous stays MISSING; E1c left open as Q7. **But** "F-RESID descriptive" is filed as the author's (H3) | CONFIRMED (H3) | LOW |
| 3 | Holm m = 3: \|z\| 2.3940 / 2.2414 / 1.9600; MDE80 3.2356; x0.969 | Own NormalDist: 2.3940 / 2.2414 / 1.9600 (m = 4: 2.4977 / 2.3940 / 2.2414 / 1.9600); 2.3940 + 0.8416 = 3.2356 (exact 3.235601); 3.2356 / 3.3393 = 0.96895 | CONFIRMED | - |
| 4 | C: S-RES table at n 7,058; reading column; descriptive P and G(V0\|L2+N) | Read from projection.csv `res_central` / `mde_central` and summary.txt L125-L151. **S-RES cells:** D_K .1392-.1988 / .2077-.2967 / .3432-.4902; D_N .1146-.1400 / .1802-.2202 / .2751-.3363; G(N) .0953-.1165 / .1474-.1801 / .1903-.2326. 9/9 equal at 3 dp; centrals 9/9. **Descriptive:** P .295 / .4052 / .596; G(V0) .3250-.3667 / .4158-.4692 / .5906-.6663. **m = 3:** D_K band top R 69 0.1755 x 0.96895 = 0.17003, still above 0.17, so "no comparison changes" holds. Reading column 3/3 on the central projection. **But** the reading drops the "central" qualifier (H1) | numbers CONFIRMED; reading PARTLY | MEDIUM (H1) |
| 5 | D: floors on the clustered form; UNDETERMINED under the declared SE; D_K 0.188-0.268, m = 3 0.182-0.260; kNN floors | Multiplier 3.339 (P 3.842) = L25718 (g). Own: D_K 0.1876-0.2680, m = 3 0.1818-0.2597; D_N 0.1134-0.1386; G(N) 0.1224-0.1496. **But** the x0.9 end sits below the stated lower bound (H2) | CONFIRMED (H2) | LOW |
| 6 | E: provisional pins | rev-parse 2a5bf9d: script 911f616f850adfe9 (0 CR); go config aadd03e8 (0 CR; worktree `--no-filters` 770a7206, 4 CR); plan fb464a61 (worktree 6ee2b3f4, 464 CR). Go config = `note` + `"authorised_go": {}`. Regex 56cf4896222af049 and digest e1a81947f64583fe as DELTA3 row 2 (prior committed review, taken as given). Called PROVISIONAL, not of record | CONFIRMED | - |
| 7 | F: delta-3 numbers; merge state; gate | **Merge state:** 12abc39 = merge (parents 06c075f, 0be0164); master = 033c79c; `--is-ancestor 2a5bf9d master` rc 1; f2d87a1's parent is 033c79c. **Quotes:** the DELTA3 verdict and "Merge: MERGEABLE (fast-forward)" are exact. **Numbers:** rows 1, 3-6, 9, 11, 15 equal (0/0 chat/generate; 57/57, 43, 986/1/10; 177/177; 16/17; six races at 14,000; 51 recovered once; 157 + 8; 60 bodies; 14,116 / 28,232). **Gate:** E1 + E2 for any go, C-AZ for Azure = DELTA3's verdict | CONFIRMED | - |
| 8 | No n* | 2 mentions of n* in L25800-L25819, both negations | CONFIRMED | - |
| 9 | Extrapolation labelled | The label is a verbatim substring of summary.txt; 4 "registrar's arithmetic/comparison" labels. "No n* is licensed" in quote marks is not verbatim (H5a) | CONFIRMED (H5) | LOW |
| 10 | DC G1-G6 resolved | **G1:** C + L25789/L25797 (x0.9-1.1, D_N R 18 0.275-0.336). **G2:** D + L25790. **G3:** A + L25790. **G4:** B (the D-2026-10-21-1 quote is exact in 2026-10-21.md; L25695 quote exact). **G5:** H (3) + L25796. **G6a/d:** E + L25792. **G6b:** queue bracket present. **G6c:** INDEX `last_update` names v3 (the 157-character head, results_index L98-L99) | CONFIRMED | - |
| 11 | Earlier answers intact | Rule B, SE_cell primary, N_A = N', cont tau^2, the 156 kept, roster / serving / go open, ORDER, D-2026-10-20-4: all carried. 0 lines above L25799 altered beyond the 9 insertions. **But** L25716 / L25698 / L25701 have no forward bracket (H4) | CONFIRMED (H4) | LOW |
| 12 | Remaining author questions: Q2, Q6, Q7, call cap, llama3.2 1b/3b | Matches H (1) and DELTA3's list. Q6's six removals match the code (L273, L313, L930) | CONFIRMED | - |

## Defects (each with a fix; insertion only, at the registrar's next record, before the full registration)

- **H1 MEDIUM: the S-RES reading drops M-1's "central" qualifier.**
  - **Where:** C's "Reading" sentence, Q2, the L25797 bracket, the queue notes and the hand-back.
  - **What they say:** "D_N and G(N|L2+V0) are [powered] at R 69 and 35; at R 18 only G(N|L2+V0)".
  - **Why it needs the qualifier.** POSTRUN_FRESH-SIZE M-1 (MEDIUM): the central a = 0.5 is above every measured trend. Its fix binds "any copy" to read "under the central assumption a = 0.5, which no briefed cell's measured trend reaches".
  - **Own arithmetic (projection.csv; planning, not a verdict), measured trend (`mde_trend`) x S-RES:**

    | R | D_N (vs 0.25) | G(N) (vs 0.25) | D_K (vs 0.17) |
    |---|---|---|---|
    | 69 | .194-.237 | .163-.200 | .187-.268 |
    | 35 | **.272-.333** | **.218-.266** | .260-.372 |
    | 18 | .362-.443 | .196-.240 | .450-.643 |

    At the scenario band top x S-RES, R 35 is above the distance for both (D_N .307-.376, G(N) .259-.317). R 69 holds for D_N and G(N) in all three readings (band top x1.1: .237, .205).
  - **Why it matters:** the roster question Q2 is the one this feeds.
  - **Origin:** the wording is DC G1's fix text, the reviewer's own.
  - **Fix: bracket the Reading, Q2 and L25797 with:**
    - "central projection (a = 0.5; M-1)";
    - under the measured trend: D_N powered at R 69 only; G(N|L2+V0) at R 69 and 18, straddling at R 35;
    - at the band top: only R 69.
- **H2 LOW: the kNN factor's x0.9 end falls below the stated lower bound.**
  - C and D call the clustered form the LOWER bound of SE_cell, then apply x0.9. Examples: D_N R 69 .115 < clustered .127; D_N floor 0.113 < 0.126.
  - No comparison changes, because the x1.1 end decides every row.
  - Fix: mark the x0.9 end "below the stated lower bound (near-degenerate kNN readers); not credible as the deciding SE", or floor it at x1.0.
- **H3 LOW: a registrar entailment filed as the author's decision.**
  - The L25797 bracket says "Q1 answered by (1) (m = 3; G(V0'|L2+N'), F-RESID and PF5 descriptive)". The queue `author_decision` field says the same.
  - D-2026-10-29-1's "Meaning" names G(V0|L2+N) and PF5; it does not name F-RESID. F-RESID follows because it fires only on G(V0|L2+N)'s word.
  - Fix: label "F-RESID descriptive" as "the registrar's entailment of (1)".
- **H4 LOW: superseded earlier lines carry no forward bracket.**
  - A says it replaces "the 2026-10-26 [E3] count, L25716". L25716 still reads "Every planned F member stays in Holm's m = 4 ... still advances the step-down", with 0 brackets.
  - L25698 (Holm over 4) and L25701 (F-RESID "fires iff") also have 0 brackets.
  - A grep for "Holm's m" lands on L25716 first.
  - Fix: one dated bracket at the end of L25716, pointing to A of the 2026-10-29 record (optionally also L25698 and L25701).
- **H5 LOW: wording.**
  - (a) `FRESH-SIZE "No n* is licensed"` is in quote marks, but the source prints "NO n* IS LICENSED" (summary.txt L15). This was carried from the 2026-10-28 record.
  - (b) E names 4 models refused [G5]. The same code branch also refuses qwq and magistral (L313, L930; not exercised by the selftest), which C and Q6 count as removed. Add both to E.

## Questions that remain for the author (relayed; none new from this check)

- **Q2:** serving and roster. Read it with H1: only R 69 is robust for D_N and G(N|L2+V0), and D_K is not shown powered at any R. The nameable rosters (R <= 18) are not measured (M-2).
- **Q6:** confirm what thinking off removes: grok-4-1-fast-reasoning, Kimi-K2.6, gpt-oss, qwq, deepseek-r1 and magistral. That leaves 2 API deployments (14,116 calls at 7,058).
- **Q7 (E1c):** read an (I) answer statement followed by a sentence, or leave it MISSING.
- **Then:** the call cap, and whether to keep llama3.2 1b/3b.

## Commands (read-only; scratch = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/dc1029)

```
git show 79ce688a --numstat --format=; git show 79ce688a --name-only --format= | wc -l       # 13/13, 32/11, 1/1, 27/6; 4
git merge-base --is-ancestor 9944e168 79ce688a                                                 # rc 0
python -I ins.py      # CR 0/0; 25,793 identical; 6 lines insert-only (difflib); 9 brackets; heading L25800, last L25819
python -I jd.py       # results JSON state fields replaced, rest appended; queue 271->271, order kept, append-only + last_update
python -I -c "results_index.render(load()) == INDEX.md"                                       # True (287 records, 0 errs)
python -I num.py      # Holm m3 2.394/2.2414/1.96; 3.2356; x0.96895; res_central 9/9; band top m3 0.17003; floors
python -I quotes.py   # 26 quotes; "No n* is licensed" not verbatim (H5a); the rest exact
sha256sum -c E:/benchzoom_demo/followups/fresh-size/SHA256SUMS                               # 5/5 OK
python -I -c "projection.csv mde_trend, mde_band_hi x S-RES (D_K 1.4-2.0; D_N, G(N) 0.9-1.1)" # H1 table
sed -n '25698p;25701p;25716p' prog.md | grep -c 'CORRECTED'                                   # 0 (H4)
git -C Z:/FAC/TUBerlin/benchzoom log --format='%h %p' -1 12abc39; rev-parse --short master   # 06c075f 0be0164; 033c79c
git -C Z:/FAC/TUBerlin/benchzoom merge-base --is-ancestor 2a5bf9d master                     # rc 1
git -C Z:/FAC/TUBerlin/benchzoom rev-parse 2a5bf9d:<script|go config|plan>                    # 911f616f / aadd03e8 / fb464a61
git -C <worktree fresh-math-pipeline-3> hash-object --no-filters <go config|plan>            # 770a7206 / 6ee2b3f4 (CRLF)
git -C Z:/FAC/TUBerlin/benchzoom show 2a5bf9d:examples/fresh-math-pipeline.py | grep -n 'REASONING_ONLY\|API_THINKING_ONLY'   # L273, L313, L930
```
