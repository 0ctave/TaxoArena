# Stale-results audit — every per-domain arena number in `report/` and `docs/`

**Written 2026-07-31, reframed later the same day. Analysis only. Nothing in `report/`
was edited.**

> **Read this first.** When this file was written, the M = 12 batch was the results and
> the re-runs were architecture tests. That is inverted. The M = 12 batch is not a
> baseline — every run in it had one complete cell and the rest starved, and three had
> arm imbalance down to 0.833. The five revised-scheduler runs are the results; they
> live in `docs/newlogic-rerun-record.md`. The M = 12 batch is kept as the record of
> what the defects cost.
>
> The inventory below is still the map: it says where every number sits and which run
> produced it. What changed is the instruction. **Wherever a row says a value is
> "correct for the batch" and should stay, read it as: correct for a superseded batch,
> and to be replaced by the revised-scheduler value where one exists.** Where no
> revised-scheduler run exists — law, physics, computer science — the M = 12 value is
> all there is, and the text has to say which batch it came from.

Same roster, same snapshot (`20260727_042523_Headless_Run_Auto_ge`), same seed 42, same
paired design across both batches; the sampler and the question count changed.

Read alongside `docs/batch-M12-complete-record.md` (superseded) and
`docs/newlogic-rerun-record.md` (the results). Neither is duplicated here.

---

## 0. Three staleness axes, not one

The thesis is behind in three separate ways, and they need different repairs.

**Axis A — the thesis is behind even its own superseded batch.** `tab:c5-all-domains`
still prints the *original* mathematics run (−0.0640 / −0.0070, i.e. −18.22 / −2.00
steps) and marks both computer science and the mathematics re-run `PENDING`. That batch
has since closed: computer science returned +2.00 / +8.00 (a registered null failed,
positive) and the registered mathematics re-run returned −23.04 / −29.05 (a registered
null failed, negative). Both are registered outcomes on complete domain-level graphs.
They are the only two rows the thesis is *obliged* to add, because the registrations
were written first — and both must be reported even though the batch they belong to is
superseded, precisely because they are registered failures.

**Axis B — the results are the revised-scheduler batch and the thesis has none of it.**
Five domains: philosophy +14.00 / +14.00, history +4.00 / +4.00, psychology +2.00 /
+2.00, mathematics −2.00 / 0.00, engineering +3.01 / +3.01. MAIN beats C5 in four of
five. Nothing in `report/` prints any of these. No registration covers any of them
either, and the text has to say so.

**Axis C — per-cell coverage was broken batch-wide and nobody registered against it.**
Addendum 4 registered the *domain-level* confound (math at 20/66) and the registered
re-run fixed it. What Addendum 4 never saw is that the old bootstrap counted its floor
domain-wide and put every bootstrap match on the largest leaf, so exactly one cell per
domain reached 66/66 and the rest sat at 4 to 33. Δρ is fitted on pooled domain verdicts
and survives; every *per-cell* quantity does not. This is the defect that makes the
M = 12 batch a record rather than a baseline.

Verified directly on all five re-run domains (`*_newlogic_secured/ratings.db.final` and
`math_btrank_secured/` against the M = 12 databases): per-cell pairs go
philosophy `[16, 20, 66]` → `[66, 66, 66]`, history `[12, 12, 28, 66]` → all 66,
psychology `[23×5, 26, 26, 66]` → all 66, mathematics `[18, 19×9, 66]` → all 66,
engineering `[4, 11, 33, 66]` → all 66. Arms: philosophy 1319/1188 → 966/966,
engineering 792/660 → 649/649.

---

## 1. `report/` — every site

Δρ in grid steps throughout (one step = 0.0034965 at M = 12; two steps = 0.0069930 is
the pre-registered decisive threshold). Positive favours the per-leaf arm.

### 1.1 `report/03_Content/6_Results.tex`

| line | as written | run it came from | re-run effect | claimable / not |
|---|---|---|---|---|
| 126 | "Comparison counts run from 660 to 3,300 per arm" | old-logic batch (engineering 660, psychology 3300) | Revised batch runs 649 to 2,405 per arm. Cost fell 12–42% per domain: psychology 3300 → 2405, history 1448 → 839, philosophy 1319 → 966, engineering 792 → 649, mathematics 2640 → 2328. | Replace with the revised range. The old sentence stays true of the superseded batch and should not be quoted as a cost figure for the architecture. |
| 141–155 | pairing overlap ">99% on mathematics, law, history and psychology", "89.9% on philosophy", "83.3% on engineering"; counts "1,319 against 1,188, and 792 against 660" | old-logic batch | Change 3 (C5 stops at MAIN's count) makes arm balance 1.000 by construction. Philosophy verified: 1319/1188 → 966/966, balance 0.901 → 1.000. Tuple-overlap under the new logic was not recomputed. | Still correct about the batch. Cannot claim the residual is fixed — arm *balance* is fixed, tuple *overlap* was not measured. Do not assert 100% overlap. |
| 500–506 | "meets the decisive threshold in five, returns a clean null in engineering, and returns a verdict for the partition-free arm in mathematics" | old-logic batch, seven domains | Under the re-runs psychology drops to +2.00 steps, which is 0.006993 — exactly the seam (§4). Mathematics drops to −2.00 / 0.00. | The count "five" is fragile in both directions and depends on the seam ruling. Do not restate as a count without saying which batch and which ruling. |
| 541–542 | mathematics key agreement 94.2% / 94.7% | mathematics **original** | Registered re-run 93.1% / 94.3%. Revised-scheduler run, computed 2026-07-31: **81.8% / 86.0%**, gap −4.2 against combined SE 1.77. | Correct for the original run, labelled as such. Provenance is currently unlabelled at this line. The revised run is the only key-agreement gap in either batch that clears its own noise, and it favours C5 — which is the one thing that makes the mathematics negative more than a coin flip. |
| 547–561 (`tab:c5-rho`) | MAIN 0.887 / C5 0.951 / Δ −0.064; MAIN 0.916 / C5 0.923 / Δ −0.007 | mathematics **original** | Registered re-run: −23.04 / −29.05 steps. Newlogic: −2.00 / 0.00. | The Δ column is defensible for the original run. The **absolute** ρ values (0.887, 0.951, 0.916, 0.923) are not stable to three decimals across analysis conventions and the thesis's own scope condition three says so. This table violates it. |
| 563–566 | "nine times the decisive threshold"; "collapses to exactly the threshold" | mathematics original | Both phrasings die under either re-run. | Keep only with the run named in the same sentence. |
| 570 | Jeffreys-prior export 0.874 / 0.965 | mathematics original | unaffected as an illustration of convention sensitivity | Fine — it is quoted to make the instability point, not as a result. |
| 577–582 | "the registered rule returned a verdict for the partition-free arm" (−0.064 / −0.007) | mathematics original | The registered re-run confirms the direction, harder (−23 / −29). The revised-scheduler run softens it to −2.00 / 0.00. | The verdict stands. The **magnitude** does not survive. See §3. |
| 624–631 | law: 2,499 / 2,479 comparisons, ties 19.8 / 17.8, key agreement 88.0 / 86.2, ρ 0.9510/0.9510 and 0.9650/0.9441, Δ +0.0210 | old-logic batch | **Law has no re-run.** Two attempts were discarded — `ratings_law_slowrun_discarded.db` ran at 30 verdicts/min against 90–100 elsewhere, unexplained. | Unchanged. The four absolute ρ values quoted here have the same three-decimal problem as `tab:c5-rho`. |
| 695 | psychology **+0.0210 / +0.0210**, 85.2% / 84.3% | old-logic batch (+6.00 / +6.00) | **+2.00 / +2.00** — shrinks by four steps and lands on the seam | This is the single most consequential moved number in the thesis. See §3. |
| 696 | physics **+0.0140 / +0.0140**, 83.8% / 79.8% | old-logic batch (+4.01 / +4.01) | **No physics re-run.** | Unchanged, but it now sits in a table where its neighbours moved. |
| 697 | history **+0.0105 / +0.0105**, 83.3% / 79.4% | old-logic batch (+3.01 / +3.01) | **+4.00 / +4.00** — grows one step; converged 4/4 (first ever in the project) | Direction and decisiveness hold under both. |
| 698 | law **+0.0000 / +0.0210**, 88.0% / 86.2% | old-logic batch (0.00 / +6.00) | no re-run | Unchanged. |
| 700 | philosophy **+0.0490 / +0.0420**, 92.9% / 94.2% | old-logic batch (+14.00 / +12.00) | **+14.00 / +14.00** — half held exactly, dropped rose two steps to match; the two conventions converged; arm balance 0.901 → 1.000 | The strongest row in the table under both batches. See §3. |
| 701 | mathematics **−0.0640 / −0.0070**, 94.2% / 94.7%, dagger footnote | mathematics **original**, the confounded run | Registered re-run −23.04 / −29.05, key agreement 93.1 / 94.3, 66/66 domain pairs. Newlogic run −2.00 / 0.00. | **The thesis is printing the run its own registration says must be superseded.** Addendum 4 fixed in advance that both runs appear together and the re-run is preferred on 66/66 against 20/66. Neither is in the table. |
| 702 | computer science `PENDING` | — | Old-logic batch closed at **+2.00 / +8.00** — a registered null failed in the *positive* direction. No re-run. | Must be filled from the registered batch. This row is the one that protects the thesis against a fishing charge (§3). |
| 703 | engineering **+0.0035 / −0.0035**, 89.0% / 88.5% | old-logic batch (+1.00 / −1.00, registered null MET) | Re-run landed 2026-07-31 00:26: **+3.01 / +3.01**, arms 649/649, all four cells at 66/66, key agreement 92.0 / 91.4. | **The batch's one clean registered null moves.** Either the revised logic favours the per-leaf arm or the old run (arms 0.833, one cell at 4 of 66) was too broken to detect an effect. Report both values and say that nothing distinguishes the two readings. Do not present engineering as a clean positive. |
| 705 | "mathematics, re-run" `PENDING` | — | The registered re-run has landed: −23.04 / −29.05. | Must be filled. Addendum 4's reading rule then applies — outcome 1, "the finding strengthens". |
| 709–713 | dagger footnote, "20 of the 66 model pairs, against 66 of 66 in every other row" | correct for the batch at *domain* level | Correct as written and now *incomplete*: at *cell* level every other row was also starved (median ~19/66). | The domain-level sentence is true. The implied contrast ("every other row is complete") is true only at the domain level, and the footnote does not say which level it means. |
| 716–720 | "Three of the four clear the decisive threshold under both conventions" | old-logic batch | Psychology's re-run at +2.00 steps sits on the seam, so the count depends on the ruling. | See §4. |
| 722–738 | engineering: one grid step, sign flips, key agreement 89.0% (SE 2.0%) / 88.5% (SE 2.2%), registered prediction met | old-logic batch | Re-run: +3.01 steps under both conventions, key agreement 92.0 / 91.4 (gap +0.6, combined SE 2.32). | The registered prediction was met **in the batch it was registered against**, and that has to be said in the same sentence. The revised run's key-agreement gap is null; its Δρ is not. |
| 740–742 | engineering tie rates 31.4% / 23.5% on 792 and 660 | old-logic batch | Re-run tie rates 27.9% MAIN / 25.4% C5 on 649 and 649. | The old sentence's point was the C5 tie excess on unequal arms. Under matched arms the excess reverses and shrinks. Rewrite or drop. |
| 744–759 | physics +0.0140, four grid steps; key agreement 83.8 / 79.8, 4.0 points, ~2.3 combined SE | old-logic batch | no re-run | Unchanged. |
| 761–773 | philosophy: "largest measured (+0.0490 and +0.0420)"; key agreement 92.9 / 94.2, gap 1.3 points against combined SE 1.8; "the screen's false negative at p = 0.053" | old-logic batch | Δρ holds at +14.00 / +14.00. Key agreement under the revised run, computed 2026-07-31: **83.5 / 83.8**, gap −0.3 against combined SE 2.83. | Δρ replicates. The **dissociation replicates in sign only** — the key-agreement gap falls from 1.3 points (0.7 SE, already weak) to 0.3 points (0.1 SE). State it as a direction, not as an effect. Note also that key agreement is computed on each run's own question set (99 questions against 126), so the levels are not comparable. |
| 790–804 | near-clone Prediction 2: law 11/24 tied per arm; psychology 18 direct comparisons per arm; history 13/35 and 4/35; "philosophy and engineering each gave the pair 2 direct comparisons per arm, the bootstrap minimum, which is too thin to read" | old-logic batch, **per-pair supports** | Recomputed 2026-07-31 on `claude-3.5-sonnet` vs `claude-3-5-sonnet-20241022`, direct comparisons per arm, M = 12 → revised: philosophy 2 → 27, engineering 2 → 16, mathematics 2 → 63, psychology 18 → 79, history 35 → 22. Identical in both arms throughout. | **This is a per-cell quantity and it moved by an order of magnitude.** Philosophy and engineering are no longer too thin to read. The tie rates would be recomputed on entirely different supports. Withdrawn in `docs/void-results.md` §2. Nothing here is safe to restate as a property of the pair. |
| 806–822 | near-clone Prediction 3: "met in seven of the ten arms", failures on law MAIN (2.4 SE), psychology MAIN (2.8 SE), philosophy C5 (2.2 SE); footnote says computed "from the per-leaf leaderboards as the mean of leaf-level θ with a pooled standard error" | old-logic batch | Computed on per-leaf fits over graphs at 12–26 pairs of 66. Three of the five domains involved now have complete per-cell coverage. | **The most exposed per-cell claim in the thesis.** Its footnote already concedes "a domain-level refit could move them either way". The re-runs give the material for a per-leaf refit on complete graphs. Nothing may be claimed about over-resolution from the old numbers beyond what the footnote already concedes. |
| 833–854 | the screen record: four flagged all positive, philosophy the largest at p = 0.053, engineering clean null, mathematics a verdict for C5; screen-p vs between-leaf agreement +0.072 | old-logic batch | Every element survives the re-runs in direction. Philosophy holding exactly at +14 steps makes the false-negative point harder. | Strengthens. See §3. |
| 856–891 | mathematics paragraph: "−0.064 half-weighted and −0.007 dropped"; "20 of 66"; "no property of mathematics as a domain may be inferred"; re-run "outstanding when this chapter was fixed"; `PLACEHOLDER(author)` at 888–891 | mathematics original | The registered re-run has landed. The placeholder is now actionable. | Fill **Addendum 4's obligation** from the registered re-run — the addendum specifies "identical configuration to Runs C–J", so the revised-scheduler run does not discharge it. Then report the revised run separately as the current result, and say the two magnitudes disagree by 21 to 29 steps. |
| 893–911 | "Every positive number in `tab:c5-all-domains` should be read as a precision gain on a shared ranking"; law leaf-vs-domain 0.895–0.993 against 0.873–0.970 | law run + offline analyses | Unaffected. The bound is computed on ground-truth accuracy, never on verdicts. | Unaffected, and it is the bound that the re-runs make *more* necessary, since the magnitudes it bounds turn out to be sampler-sensitive. |
| 912–920 | "seven sit between three and six grid steps"; "Only philosophy, at twelve and fourteen steps, is large" | old-logic batch | Under the re-runs the flagged spread becomes psychology 2, physics 4 (unchanged), history 4, law 0/6 — so "three to six" becomes "zero to six". Philosophy goes to fourteen/fourteen. | The *shape* of the claim (small margins, one large outlier) survives. The exact range does not. |
| 921–928 | coverage bound: six of fourteen domains untested, business 0.052, health 0.070 | screen, not arena | Unaffected. | Unaffected. |
| 1600 | "forces every positive Δρ in `tab:c5-all-domains` to be read as a precision gain" | offline nulls | Unaffected. | Unaffected. |
| 1772–1787 (`tab:res-summary`) | RQ2 row: "seven complete"; psychology +0.0210, physics +0.0140, history +0.0105, law +0.000/+0.021; philosophy +0.049/+0.042; engineering one step; mathematics −0.064/−0.007 with "a registered re-run outstanding"; "Computer science… still running" | mathematics **original**, rest old-logic batch | Same as the table rows above. | Every correction to `tab:c5-all-domains` has to be mirrored here. |

### 1.2 `report/02_Prematter/e_Abstract.tex`

| line | as written | run | re-run effect | claimable / not |
|---|---|---|---|---|
| 69 | mathematics key agreement "94.2% against 94.7%" | mathematics **original** | registered re-run 93.1 / 94.3 | Provenance unlabelled. Both runs give the same reading (the two arms match to within about a point), so the sentence survives either way. |
| 69–71 | "across the seven completed domains that difference runs from −1.3 to +4.0 points and favours the per-leaf arm in five of them" | old-logic batch, seven domains | Computer science (87.1 / 87.6) makes it eight domains and does not change the range. | The range is stale only in the domain count. |
| 76 | "Eight domains were then run under a paired protocol, seven of them complete." | pre-CS | Computer science is complete. | Now wrong. Eight of eight. |
| 77–81 | four flagged never reverse sign; engineering returns the registered null; philosophy the largest advantage at p = 0.053 | old-logic batch | Signs hold. **Engineering's clause does not** — its revised run is +3.01 under both conventions. | Rewrite the engineering clause. The registered null was met in the batch it was registered against, and the control moved when the scheduler was fixed. Both facts, same sentence. |
| 90–96 | "One registered prediction failed" (mathematics); "covers 20 of the 66 model pairs"; "a re-run is registered and outstanding" | mathematics original | The re-run has landed, and it failed the null harder. Also: **two** registered predictions failed, not one — computer science failed positive at +2.00 / +8.00. | "One registered prediction failed" is now false. This is the single largest factual error the batch closure creates in the abstract. |
| 108–109 | "eight domains of fourteen, at one seed" | — | unaffected | Fine. |
| 29–37 | the German-abstract TODO already says the English text moves when CS and the math re-run land | — | Both have landed. | The TODO is correct and now due. |

### 1.3 `report/03_Content/1_Introduction.tex`

| line | as written | run | re-run effect | claimable / not |
|---|---|---|---|---|
| 615–617 | "Seven of the eight have results. Computer science… was still running when this text was fixed." | pre-CS | CS is complete, and it failed its registered null positive. | Stale. |
| 628–633 | four flagged, all positive, no sign reversal; engineering returns the registered null | old-logic batch | holds in direction | Holds. |
| 634–641 | philosophy the largest at p = 0.053; mathematics "returned a verdict for the partition-free arm… re-run… outstanding" | mathematics original | re-run landed, direction confirmed | The philosophy sentence strengthens. The mathematics sentence needs the re-run added. |
| 665–671 | scope condition four: mathematics "covers 20 of 66 model pairs where every other paired run covers all 66"; re-run "registered and outstanding" | correct at domain level | The re-run resolved it. At *cell* level the contrast does not hold — every domain was starved. | Rewrite the "outstanding" clause. Say which level the 66/66 refers to. |
| 74–89 | `%` comment block tracking CS and the math re-run as blockers | — | both landed | The comment is a live checklist and is now due. |

### 1.4 `report/03_Content/5_Experimental_Design.tex`

| line | as written | run | re-run effect | claimable / not |
|---|---|---|---|---|
| 47–54 | eight domains, registration status per domain, "computer science was still running when this chapter was fixed" | pre-CS | stale | Stale. |
| 66, 451 | decisive threshold `|Δρ| ≥ 0.007`, two steps of the 0.0035 grid | — | unaffected | Unaffected, and load-bearing for §4. |
| 515 | grid at M = 8 / 11 / 12 | — | unaffected | Note: `docs/evidence-audit-2026-07-30.md:480` flags a Ch.5-vs-Ch.6 mismatch on the middle value. Unrelated to the re-runs. |
| 525, 542 | the 0.0069930-vs-0.007 seam, stated explicitly | — | The re-runs put **psychology** on that seam too (§4). | The thesis already documents the seam. It now catches a third result. |
| 461–476 | "The mathematics coverage confound, and the re-run registered against it"; 20/66 against 66/66; "reporting only the re-run is excluded under every outcome" | correct | The registered re-run landed and is preferred on coverage. | Update from "registered" to "registered and landed", and report both per Addendum 4. |

### 1.5 `report/03_Content/7_Discussion.tex`

| line | as written | run | re-run effect | claimable / not |
|---|---|---|---|---|
| 37–44 | "The mathematics run covers 20 of 66 model pairs and predates two scheduler fixes, so law carries more of the inference than mathematics does" | mathematics original | The registered re-run removes the coverage excuse and keeps the negative. Mathematics now carries more weight than this sentence gives it. | Weakens as written — the hedge is now unnecessary for the registered re-run and should be re-pointed at the original. |
| 56–60 | "Of 293 within-domain leaf pairs, three survive Bonferroni, all three in mathematics… The one domain where cells demonstrably differ is the one where the paired arm failed." | offline, ground-truth accuracy only, **no judge calls** | The offline half is unaffected by per-cell arena coverage. The arena half moves: −23.04 / −29.05 registered, −2.00 / 0.00 in the reported run. | The sentence survives as a **direction** — mathematics is negative in all four of its runs, and the reported run's key agreement backs it at 2.4 SE. It does not survive as a demonstration of size. Rewrite so it does not depend on the magnitude. |
| 85–86 | "the eight paired runs… do separate in five domains" | old-logic batch, seven results | Same count problem as `6_Results.tex:500`. | Count depends on batch and on the seam ruling. |

### 1.6 `report/03_Content/8_Conclusion.tex`

| line | as written | run | re-run effect | claimable / not |
|---|---|---|---|---|
| 24–27 | "from 94.2% against 94.7% on mathematics to a largest gap of 4.0 points on physics" | mathematics original + physics | registered math re-run 93.1 / 94.3; CS adds 87.1 / 87.6 | Range holds; the mathematics endpoint's provenance is unlabelled. |
| 57–58 | "Eight domains were then run under the paired protocol, seven of them complete." | pre-CS | stale | Stale. |
| 58–66 | "psychology and law by six grid steps, physics by four, history by three… philosophy… twelve to fourteen steps… engineering… one grid step" | old-logic batch | psychology 6 → **2**; history 3 → **4**; philosophy 12–14 → **14–14**; physics and law unchanged; engineering unfinished | **This is the most step-explicit sentence in the thesis and three of its five numbers move.** It cannot be restated as run-independent. |
| 81–90 | mathematics registered failure; "20 of 66 model pairs… on a run predating two scheduler repairs"; "a re-run is registered and outstanding" | mathematics original | re-run landed | Stale on "outstanding". |
| 153–161 | future work: "The mathematics re-run… is the one measurement that would let the thesis say anything about mathematics as a domain" | — | It has been made. | Item is complete; demote or rewrite. |
| 163–175 | pairing: ">99% on mathematics, law, history and psychology… 89.9% on philosophy and 83.3% on engineering"; "the mathematics run reaches 20 of the 66 model pairs" | old-logic batch | Arm balance is fixed by construction under the new logic (philosophy verified 0.901 → 1.000). Tuple overlap not recomputed. | Same caution as `6_Results.tex:141–155`. |

### 1.7 `report/Figures/make_screen_vs_arena.py` (untracked; **not referenced from any `.tex`**)

Lines 77–88 hardcode six Δρ pairs and six screen p-values as values the script "MUST
reproduce". Two problems independent of the re-runs: the mathematics entry is the
original run (−0.0637 / −0.0070), and the screen p-values are the **superseded 11-model
band** (law 0.008, philosophy 0.046, history 0.003, math 1.000, engineering 0.706)
against the 12-model values the thesis quotes (0.011, 0.053, 0.009, 0.289, 0.817).
`6_Results.tex:1690–1692` says the 8- and 11-model generations "are superseded… and are
not cited for any value". The figure cites them. It is not in the document, so nothing
is broken yet, but it must not be pulled in as is.

---

## 2. `docs/` — every site

| file:line | as written | run | re-run effect |
|---|---|---|---|
| `docs/README.md:26–32` | eight-row Δρ table | old-logic batch, **mathematics original** (−0.064 / −0.007), CS `RUNNING`, math re-run `PENDING` | Replaced 2026-07-31 with the five-row revised-scheduler table plus the superseded batch below it. |
| `docs/README.md:38–40` | key agreement, seven domains | old-logic batch | Replaced with the revised-scheduler values. |
| `docs/README.md:42–49` | the coverage confound, "a re-run is registered and pending" | — | Replaced: the domain-level confound resolved, and the batch-wide per-cell defect recorded in its place. |
| `docs/prereg_generic_judge_baseline.md:593–599` | the outcome table | old-logic batch, mathematics original, CS `RUNNING`, re-run `PENDING` | **Do not edit the registered predictions.** Addendum 6, appended 2026-07-31, closes CS and the math re-run against their registrations and records that the revised-scheduler batch is unregistered. |
| `…:446` | philosophy "the largest per-leaf advantage of all six completed domains (+0.049 / +0.042)" | old-logic batch | Holds; the re-run puts it at +14 / +14. |
| `…:483–546` | Addendum 4: what is being re-run, "identical configuration to Runs C–J"; the original returned −0.064 / −0.007 | — | **Load-bearing.** The registered re-run is `math_rerun_secured` (old logic, 66/66 domain pairs), and it satisfies outcome 1: "the failed null is a real property of mathematics and not a scheduler artifact… the finding strengthens." The newlogic math run is a *third* run under a *different* configuration and is not covered by this addendum. |
| `…:647` | "math moved −0.064" | mathematics original | Provenance is explicit here; fine. |
| `docs/evidence-audit-2026-07-30.md:88–95` | A1.1–A1.8, per-domain Δρ with DB provenance | old-logic batch, A1.6 = mathematics original with DB named | Provenance is stated per row, which is why this file ages well. Banner added 2026-07-31 marking its arena numbers superseded; the replacement rows, with databases and hashes, are in `docs/newlogic-rerun-record.md`. |
| `…:7` | physics +0.0140 / +0.0140 | old-logic batch | unchanged |
| `…:309` | philosophy +0.0490/+0.0420, history +0.0105/+0.0105 | old-logic batch | philosophy holds; history → +4.00 steps |
| `…:480–481` | Ch.5-vs-Ch.6 grid-step mismatch at M = 10 vs M = 11 | — | Unrelated to the re-runs; still open. |
| `…:532` | "engineering's Δρ *is* one grid step" | old-logic batch | Engineering re-run unfinished. |
| `docs/gap-analysis-final.md:51, 84, 86` | philosophy +0.049/+0.042; "Every printed number in this table is **correct**"; "Add a physics row… and a computer-science row marked pending" | old-logic batch | Line 84's "correct" is a statement about the old batch and should carry a date. The CS instruction is now executable with real numbers. |
| `docs/figures-plan-v2.md:271–272` | six Δρ pairs, math −0.0637/−0.0070 | old-logic batch + math original | Superseded on mathematics; no physics, no CS. |
| `docs/figures-plan-v3.md:8, 389–391` | "all twelve Δρ reproduce the registered table exactly", six pairs listed, math −0.0637/−0.0070 | old-logic batch + math original | Same. The word "exactly" is a reproduction check against the old batch, not a claim of stability. |
| `docs/figures-plan.md:220` | "0.887/0.951 (+0.064)" | mathematics original | Superseded; sign convention also reads backwards here. |
| `docs/peer-review-2026-07-28.md:12–13, 110, 358` | the sign-convention error, "+0.064 / +0.007" corrected to "−0.064 / −0.007" | mathematics original | Historical record of a fixed defect. Leave alone. |
| `docs/math-run-original-record.md:38–39` | −0.063703 (−18.219 steps) / −0.006993 (−2.000 steps) | mathematics original | Correct, frozen, provenance explicit. This is the model the other files should follow. |
| `docs/batch-M12-complete-record.md` (whole) | the nine-row batch | old-logic batch | Reframed 2026-07-31: banner marks it superseded, run geometry gains a per-cell coverage column, caveat 7 records the coverage defect, and "Choosing a headline later" is replaced by "What was chosen, and what it costs". Its numbers are unchanged. |
| `docs/newlogic-rerun-record.md` (whole) | five runs | revised scheduler | Rewritten 2026-07-31 as the results record. Adds philosophy and engineering, corrects the false "Every domain moved" headline, adds key agreement, and records the mathematics adjacency split. |

---

## 3. What strengthens, what weakens, what is untouched

### Strengthens

**The main claim now rests on runs that are not broken.** On matched comparison budgets
and complete per-cell coverage, the per-leaf arm recovers the ground-truth ranking more
closely than the generic judge in four of five domains, and both arms land close to the
true MMLU-Pro ordering (mean ρ 0.9224 against 0.9077). The M = 12 batch could not support
that sentence — its arms differed by up to 17% and its cells were empty. This one can, so
long as it carries §4.

**The screen-is-not-a-predictor argument.** Philosophy (screen p = 0.053, not flagged)
holds the largest effect in the project and held it *exactly* — +14.00 half under both
samplers, with the dropped convention rising to meet it, on a run whose arm balance went
from 0.901 to 1.000 and whose per-cell coverage went from `[16, 20, 66]` to complete. The
one result the screen missed is the one result that did not move.

**"Direction replicates, magnitude does not."** The thesis's own scope condition three
(`1_Introduction.tex:660–664`) already refuses absolute ρ to three decimals. The two
batches extend that refusal to per-domain magnitudes, and the extension is empirical
rather than argued: five domains, five different amounts of movement, one sampler change.
Mathematics makes it twice over — two revised-scheduler runs of the same domain, differing
only in how leaves are ranked for adjacency, land 14 grid steps apart (−16.00 Copeland,
−2.00 BT).

**The case for a larger roster.** Batch caveat 1 says the 0.0069930-vs-0.007 seam is the
strongest argument for M = 17. Psychology (+2.00) and mathematics (−2.00) both land on it
in the revised batch, joining computer science (+2.00) and the original mathematics run
(−2.00) in the old one. Four results on one seam, two of them in the batch being
reported. One ruling has to cover all four.

**The registered mathematics re-run.** It failed its null in the same direction as the
original, harder, on complete domain-level coverage. Under Addendum 4's outcome 1 the
finding strengthens. It is registered evidence, it belongs to the superseded batch, and
it must still be reported — a registered failure does not stop counting because a later
batch is cleaner.

### Weakens

**Every per-domain magnitude.** `tab:c5-all-domains`, `tab:res-summary`, and
`8_Conclusion.tex:58–66` all quote magnitudes to a precision the sampler does not
support. The conclusion's step-count sentence is the worst case: three of its five
numbers move.

**"Mathematics shows the partition costs something."** Four mathematics runs now exist:
original −18.22 / −2.00, registered re-run −23.04 / −29.05, revised-scheduler with
Copeland adjacency −16.00 / −22.00, revised-scheduler with BT adjacency −2.00 / 0.00. The
sign is negative in all four, so the *direction* is the stable part. The magnitude spans
29 grid steps, and 14 of that spread is between two runs of the *same* configuration
differing only in how leaves are ranked for adjacency. Any sentence that quotes a size
for the cost is unsupported. `7_Discussion.tex:56–60` ("the one domain where cells
demonstrably differ is the one where the paired arm failed") is the sharpest version of
this claim and the reported run puts it at two grid steps. What does hold up is key
agreement: C5 beats MAIN on the answer key in mathematics under both batches, and in the
revised run it is the only key-agreement gap anywhere that clears its own noise (−4.2
points, 2.4 combined SE).

**Everything computed per cell.** The near-clone check is the exposed case.
Prediction 2's tie rates (`6_Results.tex:790–804`) rest on per-pair supports that the
new logic changes by an order of magnitude — the clone pair's direct comparisons per arm
go 2 → 27 on philosophy, 18 → 79 on psychology, 35 → 22 on history. Prediction 3
(`806–822`) is fitted on per-leaf leaderboards over graphs at 12–26 pairs of 66, and its
own footnote already concedes that a refit "could move them either way". The
over-resolution claim is the one that rested hardest on sparse per-cell graphs and it is
the one with the least support.

**"One registered prediction failed"** (abstract, line 90). Two did.

**The domain-level 66/66 contrast in the mathematics footnote.** True at the domain
level, and it reads as though every other run was complete. At cell level none of them
was.

### Unaffected

- The offline analyses. The granularity null (`sec:res-granularity`), the leaf-substructure
  permutation null (`sec:res-leaf-null`), the rubric-specificity null, the domain screen,
  and the fixed-point certificate are computed on ground-truth accuracy or on the tree,
  never on judge verdicts. Per-cell arena coverage cannot touch them. This includes the
  three-of-293 Bonferroni survivors and the +0.072 screen-vs-leaf-agreement correlation.
- The precision-gain bound (`6_Results.tex:893–911`, law leaf-vs-domain 0.895–0.993
  against 0.873–0.970). Computed from ground truth. The re-runs make it more necessary,
  since the magnitudes it bounds turn out to be sampler-sensitive.
- Everything in `sec:res-judge` — key agreement 88.8%, the tie-rate tripling, the
  97.0%-vs-83.2% trace inversion, the 10-of-1,736 rubric-swap contrast. Run A, different
  roster, not touched.
- Law, physics and computer science. None has a revised-scheduler result. Law's two
  attempts were discarded for an unexplained 3× throughput collapse; physics was running
  when this was written; computer science was never attempted. For these three the
  M = 12 values are all there is, and the text must say which batch they came from.

---

## 4. What the new batch must carry, stated once

Seven qualifications. None is optional, and each has to appear near the number it
qualifies rather than once in a limitations list.

1. **Nothing in it is registered.** Every registration in
   `docs/prereg_generic_judge_baseline.md` was written against the M = 12 configuration.
   Addendum 4 registers a mathematics re-run at "identical configuration to Runs C–J" —
   old logic with the domain-wide bootstrap floor — and that run is `math_rerun_secured`,
   landed at −23.04 / −29.05. The revised-scheduler mathematics run is a different
   configuration and does **not** satisfy Addendum 4. Say so where mathematics is
   reported.

2. **Promoting a batch after two registered nulls failed invites a fishing charge.** The
   answer is not that the new numbers are better; it is that the old scheduler was
   broken in two named, structural ways. Give both, and give the fact that blunts the
   charge: the two failures went in **opposite** directions — computer science positive
   (+2.00 / +8.00), mathematics negative (−23.04 / −29.05). Fishing does not produce
   failures that cancel.

3. **Five of eight, not eight of eight.** Physics was running when this was written;
   computer science was never attempted under the revised scheduler; law failed twice at
   3× slower than comparable domains for reasons never established. "Four of five" is a
   count over the runs that finished, and the three that did not are not a random sample
   of anything.

4. **Engineering is unresolved.** It was the batch's one clean registered NULL (+1.00 /
   −1.00, sign flipping, MET) and it is now +3.01 under both conventions. Either the
   revised logic favours the per-leaf arm, or the old run was too broken to detect a real
   effect — arm balance 0.833, one cell at 4 of 66 pairs. Nothing available distinguishes
   the two. Engineering may not be presented as a clean positive.

5. **The seam catches two of the five.** +2.00 grid steps is 2 × 0.0034965 = 0.0069930,
   seven millionths below the pre-registration's literal 0.007. Psychology (+2.00) and
   mathematics (−2.00) both land there, joining computer science and the original
   mathematics run. One ruling must cover all four, and it has to be stated before the
   results are read, not after.

6. **Absolute ρ still may not be quoted to three decimals**, and **no Bradley–Terry
   interval exists or may be added.** `tab:c5-rho` and the law paragraph quote absolutes
   anyway; the new batch does not license that. The variance computation was wrong before
   a dated fix and intervals were never recomputed. The revised scheduler's
   inverse-variance combination of per-leaf Fisher SEs is a scheduler input, not a
   reportable interval.

7. **The code is uncommitted.** `git status` on 2026-07-31 shows 567 inserted and 190
   deleted lines across `ArcTaxonomyLLMClient.kt`, `ActiveBtRacingScheduler.kt`,
   `BtMatchScheduler.kt`, `BtStoppingPolicy.kt`, `TaxonomyBenchmarkService.kt` and
   `TaxonomyRankingService.kt`, all unstaged. There is no commit hash to cite, so no
   future pre-registration can name this configuration until there is one.

An eighth, weaker than the rest but real: the batch is not code-identical across its five
domains. BT-score adjacency landed between the history run and the mathematics BT run, so
history ran under Copeland ordering and the other four did not. Inferred from file
timestamps; nothing in the artefacts records it.

---

## 5. The two record files — done

Both corrections identified here were applied on 2026-07-31.

**`docs/newlogic-rerun-record.md`** was rewritten as the results record. It now covers
five domains rather than three, drops the false headline "Every domain moved" (philosophy
held at +14.00 exactly), adds key agreement under the revised logic, records that two
mathematics runs exist 14 grid steps apart, and marks history's claimed 4/4 convergence
as provenance unclear — its log has rotated out.

**`docs/batch-M12-complete-record.md`** was reframed as superseded. Its run-geometry
table gained a per-cell coverage column, caveat 7 records the coverage defect, the
mathematics "8 of 11 cells" line is withdrawn as a per-cell claim on 18–19-pair cells,
and "Choosing a headline later" is replaced by what was chosen and what it costs. No
number in it changed.

---

## 6. What I could not verify

- **History's 4/4 convergence.** Carried from the 2026-07-30 record. History finished at
  19:44; the surviving logs start at 21:21. Not re-checkable. **Provenance unclear.**
- **Which code state each revised run used.** Timestamps put history before the
  BT-adjacency change and the other four after, but nothing in the databases, exports or
  logs records the code state. `benchmark_metadata` is empty in every ranking database in
  the project, old batch included, so run parameters are recoverable only from the TOML
  files.
- **Law under the revised scheduler.** Two attempts discarded, cause unexplained.
- **Physics under the revised scheduler.** Running when this was written.
- **Computer science under the revised scheduler.** Never attempted.
- **The provenance of `6_Results.tex:541–542` and `8_Conclusion.tex:24–27`** is inferred
  from the value matching the original mathematics run (94.2 / 94.7). Neither line names
  its run.
- **The screen p-values in `report/Figures/make_screen_vs_arena.py:86–88`.** They match
  the superseded 11-model band rather than the 12-model band the thesis quotes. I did not
  re-run `domain_reorder_screen.py` to confirm which generation produced them.

### Verified since this file was first written

Δρ, absolute ρ, arm counts, per-cell pair coverage, question counts, tie rates,
`(question, model pair)` overlap and answer-key agreement were recomputed from the
ranking databases for all five revised runs and for every M = 12 run, with one estimator
and one script. The values in `docs/newlogic-rerun-record.md` and
`docs/batch-M12-complete-record.md` reproduce. Hard-error and connection-reset counts
were checked in the surviving logs: zero hard errors, two transient resets during
psychology, both retried.
- **The screen p-values in `report/Figures/make_screen_vs_arena.py:86–88`.** They match
  the superseded 11-model band rather than the 12-model band the thesis quotes. I did not
  re-run `domain_reorder_screen.py` to confirm which generation produced them.
