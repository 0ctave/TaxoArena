# DRAFTCHECK 2026-10-29b: BZ-AXIS-CONFIRM-FRESH registrar record and PROPOSED registration text (TaxoArena 91a3213e)

Reviewer: adversarial reviewer, 2026-10-30. Authority: D-2026-10-28-1/-2 (2026-10-28.md), D-2026-10-29-1/-2/-3 (2026-10-29.md).
Zero LLM calls. Only git, grep and short read-only scripts ran (projection.csv / summary_boot2.txt / the pinned V0 pickle opened `rb`).
No code is under review, so there are no mutants. The pins were recomputed from the benchzoom objects.

Reviewed: `docs/judge_v2_program.md` sections "## Registrar's record 2026-10-30 (insertion only; zero calls; nothing run) —
BZ-AXIS-CONFIRM-FRESH (still drafted, NOT registered): ..." L25821-L25831 and "## Registrar's record 2026-10-30 (insertion only;
zero calls; nothing run) — BZ-AXIS-CONFIRM-FRESH: PROPOSED REGISTRATION TEXT ..." L25833-L25862 (_as_of 91a3213e); the 9 brackets;
the queue items; the FRESH-MATH-PIPELINE, BZ-GUARDS-FRESH-TAU, FRESH-CONT-SELECT and FRESH-RULE-A records; INDEX.md.

## Verdict

**SOUND WITH EDITS. No BLOCKER and no HIGH; three MEDIUM (M1-M3) and four LOW (L1-L4).**

- **Record.**
  - Insertion only: 9 lines each end with one bracket; 43 lines appended.
  - D-2026-10-28-1/-2 and D-2026-10-29-1/-3 are applied as worded. DRAFTCHECK-2026-10-29 (DC29) H1-H5 are resolved.
  - Every copied number traces to its source, and every pin reproduces except L2. No n* is claimed.
- **R9 Support.** Its deciding cells reproduce from projection.csv to ±0.001 in MDE80. DEFF and n_eff are within 1% (L3).
- **Proposed text: three coherence defects.**
  - **M1:** the R10 rule plus its nearest-R clause gives a verdict that is not monotone in R. G(N|L2+V0) is SCOREABLE at R 18 and DESCRIPTIVE-ONLY at R 35.
  - **M2:** Q10 omits the two consequences that decide it.
  - **M3:** R1 calls itself "as run in bootB2", but it departs from bootB2 twice without saying so.
- **The relayed clipped-cut difference is resolved:** both counts hold (row 9).

## Per-claim table (deciding claims)

| # | Claim (registrar) | Reviewer's result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; spans L25821-L25831, L25833-L25862; parent fc4632f7 | **Programme:** difflib fc4632f7→91a3213e. 25,811 lines identical. 9 lines (25698, 25701, 25716, 25797, 25805, 25811-25813, 25818) are prefix-preserving with exactly 1 `[CORRECTED 2026-10-30` each. 43 lines appended, with headings at L25821 and L25833. CR 0 in all 7 blobs. `--is-ancestor fc4632f7 91a3213e` rc 0. 7 files changed (`--name-only \| wc -l`); test_ledger is not among them. **Queue:** 271→273 items, order kept, the 2 new at the end; every changed field is APPEND except 3 `last_update` / `head_at_update`. **Pipeline JSON:** 5 state fields are replaced, but the old ids are still referenced (911f616f ×2, 9944e168 ×7, 2a5bf9d ×5). The 2 new records did not exist before. **INDEX:** `render(load())` equals the committed file (289 records, 0 errs) | CONFIRMED | - |
| 2 | D-2026-10-29-3 recorded as worded | All 3 selections and the sign-off are exact substrings of 2026-10-29.md, and all 49 quoted strings trace (quotes.py: 44 literal, 5 across markdown / line wraps or proposed wording). The 6 models, on/switchable/none 6/5/15, think=true ×3, false ×5, absent ×13 and "API 4 eligible" all equal DELTA4 row 10. The sign-off is read as 8 variants → C, and 3 forms → MISSING (DELTA4 row 6). The `on` class follows the named list (row 10 note); relayed below | CONFIRMED | - |
| 3 | DC29 H1-H5 applied | **H1:** brackets L25797, L25811 and L25818, and the queue notes ("central" ×1). The B readings equal DC29's H1 table. **H2:** floored at x1.0 in R9(b). The L25812 numbers are 0.126-0.139 / 0.136-0.150; own x1.0/x1.1: 0.1260/0.1386, 0.1360/0.1496. **H3:** L25797 bracket, plus the queue `author_decision` ("entailment" ×2). **H4:** L25698, L25701 and L25716 bracketed. **H5a:** "No n* is licensed" occurs on L25763, L25775, L25794 and L25805 (`grep -c` 5 incl. the new B), with one bracket. **H5b:** L25813 | CONFIRMED | - |
| 4 | C/D/E copied from DELTA4/FCS/FRA | **Quotes.** The 3 verdict quotes are exact, allowing for markdown bold and line wraps (L372; FCS L20; FRA L11). **DELTA4 rows** 1-4, 6, 7, 15 and 16 are equal (65/65, 62, 1005; 250/250; 49,406, 14/14, 9a7d379b; 1 letter flip/300k; 164.8 h, 28,232). **FCS rows** 1-6 are equal (2,350 ×3; 1,150 = 75+50+875+150; 1,200 f2; 0 at 0.32). **FRA rows** 5-9 are equal. **Merge state:** b546270 = merge (033c79c, 2a5bf9d); 15ac7a2, a71c79d and 3bfc34f are not ancestors of master (rc 1 ×3) | CONFIRMED | - |
| 5 | Pins (C, R12) | Recomputed with `rev-parse` and `git show \| sha256sum`; all are LF with 0 CR. 3b892895 / 194292ce / 29efd471. b6d74a6c / 25f3893e. aadd03e8. Plan 07e8da7c. 38d1cb6e / 3176d188 (a71c79d). 3939032f / a7a367fd (7bbc08d). d3e72dd4 / efbd2141 (3bfc34f). 731818dc (f40e3ac). tau-grid plan 13a26e8a / 88161a2b. **But** R12's "master blob:4ef4f65c" is fdeee7f's, not master's (L2) | CONFIRMED (L2) | LOW |
| 6 | R9 table (x1e-3; m = 3) | tab.py from projection.csv: cell `mde_central` × factor (D_K 1.4-2.0; kNN 1.0-1.1) / 3.3393. 27 of 27 SE_cell / MDE80 cells agree to ±0.0001 / ±0.001, and the trend and band columns agree to ±0.001. DEFF and n_eff come from meter MDEs rounded to 3 dp: D_K R69 2.79-5.69 vs 2.81-5.74, n_eff 1,240-2,532 vs 1,230-2,509 (L3). The worked D_N R69 example: 0.0381 (claimed 0.0380), DEFF 1.26-1.53, n_eff 4,613-5,582, MDE80 0.123-0.136 | CONFIRMED (L3) | LOW |
| 7 | R10 verdicts by the stated rule | The rule reproduces all 9 rows. **But** G(N\|L2+V0)'s measured-trend MDE is not monotone in R (projection `mde_trend` .2181 / .2418 / .1815 at R 18 / 35 / 69). The rule therefore marks R 18 SCOREABLE and R 35 DESCRIPTIVE-ONLY. The nearest-R clause then flips the mark between rosters of 26 and 27 (M1) | PARTLY | MEDIUM |
| 8 | R8 PFs under cont | **Identities:** PF1 = .1161 − .2701 = −.1540 and PF2 = −.2431, as at L25756. **Distance from the points:** the largest distance from the 2026-10-26 points (L25717) is 0.0161 < 0.017. **PF8:** −0.0574 is the sign flip of L25751's N − N512 cont +0.0574 (0.0297). **PF9:** .35 − .06 − .27 = +.02. Every range is unchanged | CONFIRMED | - |
| 9 | Relayed: a8004083 D3 "5 of the gated cuts are clipped" vs FRA "0 clipped" | **Own read of the pinned pickle** (sha c2003c598a2553df): 36 gated nodes. **The 29 split nodes** (7 subject + 22 split, all binary) have cut_clipped False and cut_fallback False. **The 7 refused gated nodes are leaves:** 5 clipped, 2 not. Both statements hold. Routing never reads a clipped cut, so D3's concern does not bite | RESOLVED | - |
| 10 | R1 SE_cell "as run in FRESH-RULES-SIM bootB2" | **Matches bootB2 on:** stratified cluster resampling, distinct-item builds and grouped inner folds (fresh-rules.md §3, [P1]). **Wall-clock and bias** reproduce from summary_boot2.txt: B build median 245 s, harness 52 s. \|rep mean − point\| / SE_boot2 is 0.56 / 0.68 / **1.38** / 0.83 / 0.74. **But** (a) bootB2's SE = SD only (fresh-rules.py L1547: `np.std(v, ddof=1)`), and R1 adds the K seed MC term in quadrature. (b) "differ ... in fold grouping and copy exclusion only" omits the build-size difference (M3) | PARTLY | MEDIUM |
| 11 | R7 departure (a DESCRIPTIVE-ONLY TREE-AHEAD rejection fires F-FLAT) | **Coherent:** a Holm rejection keeps the FWER at any power. The sentence it departs from (L25699) is registrar draft text, not an author decision. **But** the label and its interaction with Q10 are not stated (L1, M2) | CONFIRMED (L1) | LOW |
| 12 | R6 FLAGGED rule = the pipeline's definition | The pipeline defines invalid = FILTERED + TRUNCATED + EMPTY + MISSING over all items, flagged when `share > FLAG_MAX` = 0.05 (15ac7a2 docs L94-L95, script L334 and L1026). The rule reads that share only | CONFIRMED | - |
| 13 | Labels, no n*, open items | n* appears only in negations (2). The table carries the EXTRAPOLATION label and 6 "registrar's arithmetic" labels. The remaining open items are serving, roster, cap and go | CONFIRMED | - |

## Defects (fix at the registrar's next record, by insertion, before the full registration)

- **M1 MEDIUM: R10's reading is not monotone in R, and the nearest-R clause turns that into a roster flip.**
  - **Arithmetic.** The upper-end MDE80 of G(N|L2+V0) under the trend is 0.232 at R 18, 0.258 at R 35 and 0.193 at R 69. So R 18 is SCOREABLE and R 35 is not.
  - **How it flips.** For a non-EEE roster, R10 takes the row of the nearest R. That makes G(N|L2+V0) SCOREABLE for 19-26 models and DESCRIPTIVE-ONLY for 27-52. Every roster that can be named today is non-EEE and has at most 25 models (21 local, 4 API).
  - **Fix:**
    - Read the trend on a monotone envelope: MDE_env(R) = max over measured R' >= R of MDE(R').
    - For an unmeasured R, take the next measured R below it.
  - **Result under that fix (m = 3).** G(N|L2+V0) at R 18 becomes 0.258, DESCRIPTIVE-ONLY. D_N and G(N|L2+V0) are then SCOREABLE at R 69 only, and **no deciding contrast is SCOREABLE at any roster nameable today.**
- **M2 MEDIUM: Q10 (and R11's AUTHOR mark) leaves out the two consequences that decide it.**
  - **(a) m = 2 changes the marks.**
    - The multiplier becomes 3.0830, which is x0.9528 of 3.2356.
    - G(N|L2+V0) becomes SCOREABLE at R 35 (trend .246 against 0.25, a 0.004 margin) and at R 18, including under M1's envelope (.246).
    - D_N is unchanged (R 35 trend .307).
  - **(b) R7 couples D_K's falsifier leg to its Holm membership.** At m = 3, a TREE-AHEAD rejection of D_K fires F-FLAT even though D_K is DESCRIPTIVE-ONLY. At m = 2, F-FLAT keeps only its D_N leg, and K1 KILLED is no longer testable by this test.
  - **Fix.** State (a) and (b) in Q10 and R11. Write R2's "3.2356" as "the Holm MDE80 multiplier of the registered m".
- **M3 MEDIUM: R1 departs from bootB2 twice without saying so.**
  - **(a) The MC term.** bootB2's SE_boot2 is the replicate SD alone. K'*_q is rebuilt in every replicate, so the replicate SD already contains the seed term. Adding SD_seed/sqrt 5 in quadrature double-counts it, unless fixed seeds make the seed effects correlated across replicates.
  - **(b) The build size.** A replicate builds on about 4,914 + 0.632 x 7,058 ≈ 9,376 items, which is 78% of the point build's 11,972. On c that is about 70 leaves against 89. In bootB2 at 885 items the ratio was 93% (4,588 / 4,914). So bootB2's bias evidence (replicate means within 1 SE_boot2, except G(N|L2+V0) at 1.38) was gathered at a much smaller gap and does not carry over.
  - **Fix.**
    - Drop the term, or keep it and state the correlated-seed reason. Let the runner's selftest pin which one.
    - Strike "only" and state the build-size gap.
    - Have stage 1 also print the distribution of replicate leaf counts and, per contrast, (replicate mean − point) / SE_cell. Stage 1 prints no point, so this belongs in the committed stage-1 file, read at stage 2.
- **L1 LOW: under R7, "DESCRIPTIVE-ONLY" no longer means "decides nothing".**
  - Print "(DESCRIPTIVE-ONLY by support; a TREE AHEAD rejection still fires F-FLAT)".
  - At registration, bracket L25699's "decides nothing".
- **L2 LOW: R12's tau-grid master pin is stale.**
  - Master b546270 has blob:a6b2de48 = sha256-lf16:95e1a96448407aaf, and the working tree is sha256-crlf16:2983bc27db30a3d4 with 204 CR.
  - The pinned 4ef4f65c / 5adbe370 / a3f3e68e (196 CR) belong to fdeee7f, superseded by 61b149c's insertion-only [P2].
  - The cont bullet is unchanged, and the plan of record 13a26e8a reproduces.
  - Fix: replace the pin, or keep the plan of record and the library pin only.
- **L3 LOW: R9's DEFF and n_eff come from rounded meter MDEs (up to 1% off).** Fix: compute them unrounded, or print 2 significant figures. No mark moves.
- **L4 LOW: R2's stage order is procedural.**
  - Fix: stage 2 refuses unless stage 1's sha256 appears in `git show HEAD:docs/judge_v2_program.md`.
  - State that the blind is procedural: the replicate part files hold the values. The demotion itself is mechanical.

## Questions that remain for the author (relayed; Q2/Q8-Q11 as the registrar lists them, sharpened)

- **Q2 (serving and roster), read with M1.** Under the envelope, at the 18-25 models that can be named today, no deciding contrast is SCOREABLE at m = 3. The test could then only falsify: F-FLAT via R7, with the PFs scored on range only. Only R 69 (not nameable) scores D_N and G(N|L2+V0).
- **Q10, read with M2.** m = 2 makes G(N|L2+V0) SCOREABLE at R 18-35, by a narrow margin at R 35. In exchange, F-FLAT loses its D_K leg.
- **Q8:** the token cap for the six thinking-on models. 8,192 includes the hidden trace, so R6 may exclude them.
- **Q9:** does an empty think block count as thinking (F5)?
- **Q11:** R_B = 200, or 100.
- **Then:** the call cap, the go, and whether to keep or drop llama3.2 1b/3b.
- **Information for Q9, no new question.**
  - The `on` class for qwq, deepseek-r1 and magistral comes from the decision's named list. /api/show reports them as it reports the switchable qwen3 (DELTA4 row 10).
  - So "cannot turn off" has not been observed for these three. Showing it would take a generation.

## Commands (read-only; scratch = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/dc1029b)

```
git show 91a3213e --numstat --format=; git show 91a3213e --name-only --format= | wc -l     # 7 files; no test_ledger
git merge-base --is-ancestor fc4632f7 91a3213e                                             # rc 0
python -I ins.py     # CR 0 x7; 25,811 identical; 9 lines prefix-preserving, 1 bracket each; 43 appended (L25821..L25862)
python -I jd.py      # queue 271->273, order kept, APPEND-only + last_update; pipeline JSON 5 state fields replaced
python -I -c "results_index.render(load()[0]) == INDEX.md"                                 # True, 289 records, 0 errs
python -I quotes.py  # 49 quotes (4 inter-quote fragments dropped); 44 literal; 5 = markdown/wrap (3 verdicts, D3) or proposed wording (list closure)
sha256sum -c E:/benchzoom_demo/followups/fresh-size/SHA256SUMS                            # 5/5 OK
python -I tab.py     # R9: 27/27 SE & MDE80 cells; DEFF/n_eff within 1% (rounded meter MDE)
python -I m2.py      # R10 under m=3/m=2, with and without the monotone envelope (M1, M2)
grep -n 'se_boot=' examples/fresh-rules.py@b546270                                        # L1547 np.std(v, ddof=1): no MC term (M3a)
sed -n '5,16p' E:/benchzoom_demo/followups/fresh-rules/summary_boot2.txt                  # 245 s / 52 s; rep-mean bias 1.38 SE for B G(N)
PYTHONPATH=src .venv/Scripts/python.exe clip3.py   # pinned V0: 29 split nodes clip 0 / fb 0; 7 refused leaves: 5 clipped
git -C benchzoom rev-parse b546270:docs/tau-grid.md fdeee7f:docs/tau-grid.md 13a26e8a    # a6b2de48 / 4ef4f65c / plan (L2)
git -C benchzoom merge-base --is-ancestor {15ac7a2,a71c79d,3bfc34f} master                 # rc 1 x3; 2a5bf9d rc 0
```
