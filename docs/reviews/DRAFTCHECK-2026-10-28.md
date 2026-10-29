# DRAFTCHECK 2026-10-28: BZ-AXIS-CONFIRM-FRESH draft amendment per D-2026-10-28-1 (TaxoArena a9138c19)

Reviewer: adversarial reviewer, 2026-10-28. Authority: D-2026-10-28-1 (d78972f2), with D-2026-10-27-4/-5. Zero LLM calls;
read-only on both repositories and on E: (fresh list, FRESH-SIZE outputs, pipeline roster CSVs); nothing run except git,
grep and short read-only scripts. Reviewed: `docs/judge_v2_program.md` section "## Registrar's record 2026-10-28
(insertion only; zero calls; nothing run) — BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-28-1: ..." L25760-L25776
(_as_of a9138c19), the queue items BZ-AXIS-CONFIRM-FRESH / FRESH-SIZE / FRESH-MATH-PIPELINE / BBH-WORK, and the records
FRESH-SIZE.json, FRESH-MATH-PIPELINE.json, BBH-WORK.json and INDEX.md at a9138c19. Sources: POSTRUN_FRESH-SIZE (613c1c03),
READY_fresh-math-pipeline (f00481d6), POSTRUN_PLANTED-POWER (8f0f5f1c), POSTRUN_DESIGN-SURFACE (5fb34baa), the earlier
draft sections L25692-L25758, DRAFTCHECK 2026-10-27 (c98534d2). No code is under review, so there are no mutants.

## Verdict

**SOUND WITH EDITS.** The commit is insertion-only and claims no registration. D-2026-10-28-1 is applied as the options
were worded: SE_cell is primary with the meter SE beside, the fresh set is every usable content-closed item (the 156 are
left to the author), the protocol is reasoning then the letter, serving and generation stay open, and BBH stays at 128.
Every number in the section traces to a reviewed source and reproduces to the printed digit: the 60 table values, the
list sha and count, the cost totals and the quotes. No n* is claimed, and the EXTRAPOLATION label is copied verbatim.
No BLOCKER and no HIGH. Two MEDIUM:
- D1: the 2026-10-27 DRAFTCHECK's F1-F7 were never recorded, and the new blocker list replaces the old one without them.
- D2: the cost premise of the author's option ("8-28% larger") is contradicted by the record's own power column. This
  has to be put to the author as a question, not left as a narrative relay.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Reviewer's result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; span L25760-L25776; parent f00481d6; programme blob LF | prog numstat 18 / 0. `git show a9138c19:prog \| wc -l` = 25,776, so the span ends at EOF and the heading sits at L25760. 0 CR bytes. Queue: 269 -> 271 items, 0 removed, 7 changed fields; all 7 are append-only (`startswith` 7/7; `depends_on` keeps the old list as a prefix). BBH-WORK.json changes only `last_update` and a trailing comma. Commit touches 6 files (`--name-only \| wc -l`) | CONFIRMED | - |
| 2 | D-2026-10-28-1 applied exactly (4 selections verbatim; meanings) | 5/5 quoted strings are exact substrings of the decisions file. (1) SE_cell primary, meter SE beside, every usable item, with the 156 PROVISIONAL and left to the author. (2) No generation; serving, roster and go stay OPEN (F). (3) Prompt asks for step-by-step reasoning, then `Answer: <letter>`. (4) BBH stays at 128, one bracket | CONFIRMED | - |
| 3 | A: P decides on the declared rule-B resampling SE_cell ([E1]), the SE the F family decides on; C-1 met; 3 SE_cell is a working bar (C-2 owed); multiplier 3.842; n* 4,346 dropped; 17,051 planning only | [E1] at L25715 reads "Declared for every F contrast and for P's printed sensitivity". C-1's words match. 3 + 0.8416 = 3.842. 17,051 and 4,346 are as printed in L25718. Choosing the resampling form rather than the clustered form follows C-7: the clustered form is "SUBSTITUTED" in every file. But see D2 (cost premise) and D3 (P's STRUCTURAL leg) | CONFIRMED | - |
| 4 | B: list v2 sha256 e39bb5f46949d5f6, 6,902 items, unique ids = 7,058 - 156; v1 f19569d9; SPEC 4023db05; twins 0 / 0 / max J 0.7989 | Own read of `E:/benchzoom_cache/fresh_math/fresh_items_v2.jsonl`: sha256 e39bb5f46949d5f6; 6,902 rows; 6,902 unique ids; 0 items with an empty option. v1 sha256 f19569d91d2fc795. SPEC.md sha256 4023db05e520edbe. Twin figures and the 97 / 4,914 are READY rows 4 and 6 (taken as given) | CONFIRMED | - |
| 5 | C: prompt b845360d45386fc3, regex 41ec6bba0ffd3298, cap 8,192, num_ctx cap + 4,096, extraction and invalid rules, blob 0966b648 LF | Pins = READY row 7 (given). `git cat-file -p 0966b648`: 0 CR. The rules match plan section 3 plus [BUILT] at ccedcd5 phrase for phrase: think removal, LAST matching line, case fold scoped to final/answer, category order, invalid share > 0.05 FLAGGED and kept, thinking `think: false` | CONFIRMED | - |
| 6 | D: C1-C9 as the READY states them; cost estimates | C1 (9 posts against a cap of 3), C2 (13,990 -> 14,010), C3, C4, C5 (R2 / R6 / R7 / R8), quote verbatim. From roster_20261028_131135 CSVs: local 18 rows, 120.0 / 192.3 / 2,938.9 h; llama3.2 1b + 3b excess 58.1 h (total 64.5). API 4 x 6,902 = 27,608; 27,608 / 12.76 / 60 = 36.1 h; twins Mistral 0.959, Kimi 0.99. The generation gate "C1-C5" is stricter than the READY's "C1-C4" (D5) | CONFIRMED (gate wording PARTLY) | LOW |
| 7 | E: the 15-cell table (central [band] / meter) at n 7,058, R 69 / 35 / 18, with distances; EXTRAPOLATION label | projection.csv (SHA256SUMS 5/5 OK): **60/60 values equal at 3 decimals**. Distances equal to the CSV's `distance` (0.10 / 0.17 / 0.25 / 0.25 / 0.062). Label present on 50/50 rows and copied verbatim. S-RES at R 69: P 0.2950, D_K 0.1392-0.1988, G(V0\|L2+N) 0.3250-0.3667 (`res_central`). Levers and CV equal POSTRUN rows 8, 9, 13. M-1, M-2, C-1 and Q1 quotes are verbatim (whitespace-normalised substring 5/5) | CONFIRMED | - |
| 8 | E planning reading: P DESCRIPTIVE-ONLY at every listed roster; the central comparisons | CSV `word`: P is "DISTANCE BELOW THE BAND" at R 69 / 35 / 18, and so is G(V0\|L2+N) at all three. At R 69 the central values of D_K, D_N and G(N\|L2+V0) are below their distances; at R 18 only G(N\|L2+V0) is (0.2114 < 0.25) | CONFIRMED | - |
| 9 | No n* claimed | None claimed. 17,051 and n_eq are labelled planning-only / never required. The citation "no n* (H1)" is wrong (D4) | CONFIRMED | LOW |
| 10 | Earlier answers intact (rule B decides; N_A = N'; continuous tau^2) | No earlier sentence changed (claim 1). A builds on "SE_cell UNDER RULE B"; G(3) carries "predictions under the cont tau^2 rule"; nothing in L25760-L25776 touches N_A. The "this section wins" clause differs from the earlier sections only on P's SE | CONFIRMED | - |
| 11 | G: still-blocking list complete ("replaces the list of the D-2026-10-27-5 record") | It carries a8004083 D1 and D3-D8, but none of DRAFTCHECK c98534d2's F1-F7: 0 references to c98534d2 / 31264855 in prog, queue and INDEX (`grep -c`, 0 / 0 / 0). 0 mentions of identity / select_cont / renderings in L25747-L25776 (D1). P's STRUCTURAL leg is not named (D3) | PARTLY | MEDIUM |
| 12 | Records: FRESH-SIZE / FRESH-MATH-PIPELINE created; INDEX 287; ledger unchanged v430 | INDEX "287 records". `test_ledger.html` last touched at 70c61579 and is not in the commit. FRESH-MATH-PIPELINE.json says "own mutants 4 of 8 survived on deciding paths", but 6 of 8 survived, 4 of them decisive (D6) | CONFIRMED | LOW |

## Defects (each with a fix; all insertion-only, at the registrar's next record)

- **D1 MEDIUM: DRAFTCHECK c98534d2 (2026-10-27, SOUND WITH EDITS, F1 MEDIUM, F2-F7 LOW) was never recorded.** G
  replaces the D-2026-10-27-5 blocker list and drops its open conditions. Fix: add a bracket that does the following.
  - F1: record it as RESOLVED by D-2026-10-28-1 (1) (n = every usable item) and G(1) (roster is the author's).
  - F2: carry it as code owed. The per-reader cont selection gets a selftest, mutants and a READY, and the READY proves
    "every tau^2 went through cont" by a COUNT per reader family.
  - F3: append TAU-CONT-ALL to `depends_on`, because note (a) uses POSTRUN_TAU-CONT-ALL C3 as the PF basis.
  - F4: declare the identity check either aliased or recomputed with a stated tolerance.
  - F5: fix the record ("except TAU-GRID's cont arm").
  - F6: pin the renderings at the full registration.
  - F7: record as moot, because P now decides on SE_cell and the meter z / p print beside it.
- **D2 MEDIUM: the cost premise of the author's choice is contradicted, and the hand-back does not ask about it.** The
  option was worded as "the detectable effect being about 8-28% larger than drafted". The arithmetic behind it is
  sqrt(1.9..2.7 x 4,300 / 7,060) = 1.08..1.28. The record's own numbers say otherwise:
  - FRESH-SIZE `power_central` at P's distance 0.10 (P's WORK point: PF5 +0.10, C1(V0) WORK +0.1093), on the clustered
    form, which is a lower bound for SE_cell: **0.120 / 0.047 / 0.018** at R 69 / 35 / 18. Under the meter SE the same
    column reads 0.606 / 0.184 / 0.057.
  - Under S-RES (P x1.4), at R 69: about 0.045 (reviewer's arithmetic, Phi(0.10 / (0.2950 / 3.8416) - 3)).
  - So P's MDE80 is 0.211-0.295 against the drafted 0.10, which is +111% to +195%. The rosters the record can name (18
    local, quantized and mostly sub-ceiling; 4 API) are at or below R 18, and neither is an EEE subset (M-2).
  - E relays only a same-n comparison (0.211 vs 0.117), and the 0.10 is not labelled as P's WORK point.
  - Fix: before any serving or generation go, put an explicit author question. Either keep SE_cell primary with P
    expected DESCRIPTIVE-ONLY (power <= 0.12 at R 69, at most 0.05 at R <= 35), or revisit P's SE or role. Bracket E so
    it names 0.10 as PF5's point.
- **D3 LOW: P's STRUCTURAL leg.** The 10-27 record dropped the 10-26 Q2 clause because "it holds only for a
  cell-clustered SE". P is now back on a cell SE, so the 2026-10-26 (g) fixed-cell floor applies to P again: P under
  SE_cell 0.183 > 0.10, unreachable at any n if V0''s leaf count does not grow. Fix: name it in G(3), together with the
  fact that n is capped at the pool (about 7,058), so P's word is DESCRIPTIVE-ONLY at the cap on these planning numbers.
- **D4 LOW: "no n* (H1)" misattributes.** H1 (POSTRUN_FRESH-RULES-SIM) only bars the W3/W4 n* and W2's CONSTANT words
  from the Support. Fix: cite FRESH-SIZE "No n* is licensed", DESIGN-SURFACE C4 and D-2026-10-28-1 (1) (n fixed).
- **D5 LOW: generation gate.** The record says "C1-C5 fixed and delta-reviewed before any AUTHORISED_GO entry". The
  READY's gate is "C1-C4 ...; C2 blocks only an Azure go". Fix: either mark C5 as the registrar's addition, or align with
  the READY (a local go needs C1, C3 and C4).
- **D6 LOW: attributions.**
  - "the existing data uses them" comes from the [BUILT] bracket ("the EEE runs used them"), not READY row 6.
  - The 247k / 127k figures are FRESH-SIZE summary.txt GRID rows: 247,030 / 127,044 answers at n 7,058, and 241,570 /
    124,236 on the 6,902 list. They are not "POSTRUN_FRESH-SIZE's options".
  - FRESH-MATH-PIPELINE.json should read "6 of 8 survived, 4 decisive (R2, R6, R7, R8)".
- **D7 LOW (Support input, spot check).** On the list of record, v2 has 6,902 items in 6,818 twin clusters, Kish 1.0275
  (n_eff 6,717), counted from the `cluster` field. The figures stated are the SPEC's 6,968 / 1.030 on 7,058. Fix: the
  Support states the value for the list that the READY pins.

## Commands (read-only; scratch = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/dc)

```
git diff --numstat f00481d6 a9138c19; git show a9138c19 --name-only --format= | wc -l          # 18/0 prog; 6 files
git show a9138c19:docs/judge_v2_program.md | wc -l; ... | tr -cd '\r' | wc -c                # 25776; 0
python qdiff.py <scratch>     # queue: 269->271, 0 gone, 7 fields append-only (startswith / list prefix)
python tab2.py <scratch>      # projection.csv vs the section's table: agree 15 rows x 4 = 60/60; res_central
(cd E:/benchzoom_demo/followups/fresh-size && sha256sum -c SHA256SUMS)                         # 5/5 OK
sha256sum E:/benchzoom_cache/fresh_math/fresh_items_v{1,2}.jsonl E:/benchzoom_demo/followups/fresh-math-prep/SPEC.md
python -I (v2: rows 6902, unique 6902, empty-option 0, clusters 6818, Kish 1.0275)
python -I (roster_20261028_131135/roster_local.csv: 18 rows, 120.0/192.3/2938.9 h; llama3.2 excess 58.1; roster_api.csv 4 x 6902)
python -I (projection.csv C1(V0) power_central: cell .120/.047/.018, meter .606/.184/.057 at R 69/35/18)
grep -c c98534d2 / 31264855 / FRESH-2026-10-27 docs/judge_v2_program.md docs/agents/queue.json docs/agents/results/INDEX.md   # 0 each
sed -n '25747,25776p' docs/judge_v2_program.md | grep -c -E 'identity|select_cont|renderings'                                 # 0
git -C Z:/FAC/TUBerlin/benchzoom cat-file -p {f564748d,18fdda24,0966b648} | tr -cd '\r' | wc -c                               # 0 each
git -C Z:/FAC/TUBerlin/benchzoom merge-base --is-ancestor {ccedcd5,4676efb} master                                            # 1, 1 (not merged)
python -I (quotes: 5 selections, M-1, READY "Each go ...", Q1, M-2, C-1, label: substring True, whitespace-normalised)
```
