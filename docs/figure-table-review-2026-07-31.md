# Figure and table review — 2026-07-31

Scope: every `\includegraphics`, tikzpicture, and tabular/longtable in
`report/02_Prematter`, `report/03_Content`, `report/04_Appendix`; every artifact
in `report/Figures/`; `FIGURE_PLAN.md`. Baseline: the settled 8-model, 8-domain
RESOLVED batch (snapshot `20260727_042523`); the pilot (Run A) and the 12-model
paired campaign are withdrawn. Cover-page layout tabulars and the two logos are
excluded as administrative.

Line numbers are as of this review and will drift; section labels are the
stable anchors.

---

## 1. Summary table

### Figures (placed)

| # | Figure | Where | Data vintage | Verdict |
|---|---|---|---|---|
| F-1 | `fig:pipeline` (TikZ) | 3_Method, before `sec:arch-frozen` | settled counts (8,673+3,445, 87 cells) | KEEP |
| F-2 | `fig:acceptance` (TikZ) | 3_Method | schematic, current gates (0.025, 2·SE) | KEEP |
| F-3 | `fig:scheduling` (TikZ) | 3_Method, `sec:meth-scheduling` | schematic, roster-neutral | KEEP (sweep surrounding prose: "at twelve models and eleven cells there are 726 slots" is stale) |
| F-4 | `fig:leaf-size-hist` (`leaf_size_hist.pdf`) | 5_Results, `sec:res-construction` | snapshot, regenerated 07-31 | KEEP |
| F-5 | `fig:rubric-specific` (`rubric_specific_not_decisive.pdf`) | 5_Results, `sec:res-rubric-null` | panel (a) current; **panel (b) is withdrawn Run A data** | **REGENERATE** panel (b) from settled batch, or cut to one panel |
| F-6 | `fig:frozen-tree` (`frozen_tree.pdf`) | App. G | snapshot, regenerated 07-31 | KEEP |
| F-7 | `fig:tree-full` (`tree_full.pdf`) | App. G | snapshot, regenerated 07-31 | KEEP |
| F-8 | `judge_example.tex` (generated exhibit, `\input`) | App. B `sec:judge-example` | snapshot + Kotlin sources, regenerated 07-31 | KEEP |

### Tables

| # | Table | Where | Verdict |
|---|---|---|---|
| T-1 | `tab:frozen-artifact` | 3_Method | KEEP |
| T-2 | `tab:meth-assumptions` | 3_Method | KEEP |
| T-3 | `tab:rq-map` | 4_Exp_Design | UPDATE (RQ1 names C3 as the rubric control; C3 ran only on the withdrawn pilot) |
| T-4 | `tab:info-separation` | 4_Exp_Design | KEEP |
| T-5 | `tab:model-roster-pilot` | 4_Exp_Design | MOVE to App. D (defect record, not a roster in use) |
| T-6 | `tab:arena-conditions` | 4_Exp_Design | UPDATE (C5 row still claims "the partition itself"; contradicted by its own chapter) |
| T-7 | `tab:run-record` | 5_Results `sec:res-runs` | KEEP |
| T-8 | `tab:settled-recovery` | 5_Results `sec:res-correctness` | KEEP |
| T-9 | `tab:tie-by-key` | 5_Results `sec:res-tie-signature` | KEEP (best figure candidate in the chapter) |
| T-10 | `tab:c5-decisiveness` | 5_Results `sec:res-c5` | KEEP |
| T-11 | `tab:requirements-evidence` | 5_Results `sec:res-construction` | UPDATE (one stale R2 row) |
| T-12 | `tab:j-floor` | 5_Results | KEEP |
| T-13 | `tab:anchor-cells` | 5_Results `sec:res-adapted-partition` | UPDATE ("run pool" column disagrees with `tab:run-record`) |
| T-14 | `tab:rubric-null` | 5_Results `sec:res-rubric-null` | KEEP |
| T-15 | `tab:granularity` | 5_Results `sec:res-granularity` | REWORK-CAPTION (no roster provenance stated) |
| T-16 | `tab:domain-screen` | 5_Results `sec:res-law` | KEEP |
| T-17 | `tab:res-summary` | 5_Results `sec:res-summary` | UPDATE (RQ2 cell is an erratum, not a verdict; RQ1 cell cites numbers absent from the chapter) |
| T-18 | `tab:hyperparams` | App. A | KEEP |
| T-19 | `tab:domain-registration` | App. A | UPDATE (Outcome column empty by design; fill from settled batch) |
| T-20 | `tab:arm-differences` | App. B | KEEP |
| T-21 | `tab:roster-r8` | App. D | KEEP |
| T-22 | `tab:model-roster` (12-model) | App. D | DELETE after Chapter-5 sweep (its own TODO says so) |
| T-23 | `tab:pipeline` | App. E | KEEP |
| T-24 | AI-use table (unlabelled) | 02_Prematter `i_AIUse.tex` | UPDATE (placeholder version cell; affidavit truth depends on it) |

### Unplaced PDFs in `report/Figures/`

| PDF | Built | Data | Verdict |
|---|---|---|---|
| `verdict_mechanism.pdf` | 07-30 | Run A pilot CSVs (withdrawn) | RETIRE |
| `rho_levels.pdf` | 07-30 | 12-model paired DBs + withdrawn 0.007 threshold | RETIRE |
| `screen_vs_arena.pdf` | 07-30 | 12-model paired DBs + 11-model screen | RETIRE |
| `domain_screen.pdf` | 07-30 | asserts the superseded 11-model screen | RETIRE |
| `routing_slopegraph.pdf` | 07-30 | synthetic Chapter-1 micro-example; the example is gone from the intro | RETIRE |
| `routing_provenance.pdf` | 07-31 | r8 (current) | HOLD — definition conflict with `sec:res-offsubject`, see §2 |
| `rubric_reach.pdf` | 07-31 | r8 (current) | PLACE in `sec:res-offsubject` (recommended), caption care on CIs |

---

## 2. Figure-by-figure findings

**F-1 `fig:pipeline` (TikZ, 3_Method).** Carries the two-lane
construction/arena separation and the split arithmetic; caption asserts "the
split is $70/30$ and closes exactly, $8{,}673 + 3{,}445 = 12{,}118$" — matches
the settled counts and `tab:frozen-artifact`. Encoding (two lanes, one
cross-link labelled "rubrics") is exactly the claim. KEEP.

**F-2 `fig:acceptance` (TikZ).** Schematic of the two split gates. Values
drawn (bar 0.025, `2 SE(ΔJ)`) match `tab:hyperparams`. KEEP.

**F-3 `fig:scheduling` (TikZ).** The seven-step loop; roster-neutral, still
accurate for the r8 runs (bootstrap floor, per-cell gate at 2.5σ). The figure
is fine; the paragraph introducing it computes the slot count "at twelve
models and eleven cells there are 726 distinct (cell, pair) slots" and the
bootstrap paragraph repeats "726 at twelve models and eleven cells" — stale
worked example; at the settled batch the natural example is 28 pairs × 52
cells. KEEP figure; fix prose in the parallel sweep.

**F-4 `fig:leaf-size-hist`.** Claim: leaf population distribution with the
birth floor and the one sub-floor leaf. Script reads `snapshots.db` snapshot
`20260727_042523...` read-only and asserts 154/87/median 88 before drawing;
regenerated 07-31. Caption states floor semantics honestly ("enforced at split
time … not an invariant of the final tree"). A histogram is the right encoding
for a distribution claim, and it does not restate any table. KEEP.

**F-5 `fig:rubric-specific` — the one broken placed figure.** Caption, last
sentence: "Panel~(b) is Run~A on the pilot roster." Section 5.1 declares Run A
"withdrawn in their entirety: their role was diagnostic, they produced no
reportable results". The chapter therefore withdraws Run A on page one and
presents a Run A panel as evidence in `sec:res-rubric-null` — 1,736
comparisons, 1,301 same-winner, 10 flips, all pilot verdicts, half of which
(per `sec:res-capture-gap`) measured "the presence of text, not model
quality". The panel's claim ("specificity is inert at the verdict") is *true*
on the settled batch, but its evidence is the withdrawn run.
`make_rubric_specific_not_decisive.py` still reads
`experiment_results/arena_math_frozen/seed_42/judging/*.csv` (the pilot path).
Fix: rebuild panel (b) from the r8 shared comparisons (same-winner /
one-or-both-abstain / flip over the paired triples; the settled equivalents
exist — e.g. 37 both-committed discordant, 11/26 split), or reduce the figure
to panel (a) and let `tab:c5-decisiveness` carry the verdict half. Panel (a)
(87 leaf vs 13 random CDFs, p = 1.21e-6) is current offline data and fine.
**REGENERATE.**

**F-6/F-7 `fig:frozen-tree`, `fig:tree-full` (App. G).** Both read the frozen
snapshot read-only, assert node/leaf/depth/mass and cross-check against each
run's recorded `MAIN_thesis_metrics.csv` before drawing; regenerated 07-31.
Captions state what is deliberately omitted. The icicle + labelled-tree pair
is the right split of "shape" vs "names". KEEP both.

**F-8 `judge_example.tex` (App. B).** Generated mechanically from the snapshot
and the Kotlin prompt sources "so they cannot drift from what the runs
actually sent" — the strongest provenance discipline in the document. KEEP.

**Unplaced but current: `rubric_reach.pdf`.** Built 07-31 from the snapshot,
embedding cache, eval cache and all eight r8 DBs; header claim: routed
held-out questions sit at cosine distance 0.511 from the rubric's induction
pool vs 0.353 construction-grade and 0.607 chance, and a 1-SD distance
increase moves the MAIN tie rate +1.02 pp against the GENERIC arm's +1.06 pp
(within-triple difference −0.04 pp). This is the quantitative version of
`sec:res-offsubject`'s "the judge does not care", and it covers the
*continuous* version of the claim the sign-test covers categorically.
Recommend PLACE in `sec:res-offsubject`. One caption obligation: it draws 95%
CIs from an OLS/bootstrap; `sec:exp-metrics` declares "No confidence interval
is reported anywhere" (in the BT context) — the caption must label the
intervals' source per the existing "binomial and labelled as such" carve-out,
or the metrics text needs one added sentence.

**Unplaced and trapped: `routing_provenance.pdf`.** Built 07-31 from r8, so it
is *current*, but its headline is "pooled on-subject routing rate 37.2% (609 /
1637)" under the leaf-dominant-construction-category convention, while
`sec:res-offsubject` reports "77.8% of the 1,637 judged questions carry the
MMLU-Pro category their cell was built from" under the anchor-level
convention (law 94.6% there vs 245/276 = 88.8% here). Both are defensible;
placing this figure without reconciling the two conventions manufactures an
apparent 77.8-vs-37.2 contradiction inside one chapter. HOLD until one
convention is chosen and named in both places; then it is a good candidate for
`sec:res-adapted-partition`.

**Withdrawn-data orphans** (`verdict_mechanism`, `rho_levels`,
`screen_vs_arena`, `domain_screen`, `routing_slopegraph`): see §6.

---

## 3. Table-by-table findings

**T-1 `tab:frozen-artifact`.** Snapshot id, config, seed, counts, J, and the
six governing parameters. Matches App. A and Chapter 5. Right size. KEEP.

**T-2 `tab:meth-assumptions`.** Assumption / failure / diagnostic. Honest last
row ("None applied; the Fisher standard errors … understate uncertainty").
Current — the diagnostics named point at settled-batch sections. KEEP.

**T-3 `tab:rq-map`.** RQ1's condition cell reads "C1 (main), with C3 as the
rubric control". Per `sec:exp-arena-conditions`, "C3 ran once, on the pilot" —
i.e. the named control ran only inside a withdrawn run; on the settled batch
the rubric control is C5/GENERIC. The metric cells are already
per-verdict-first (current). UPDATE the conditions column.

**T-4 `tab:info-separation`.** Access matrix; footnote b already carries the
settled verification ("zero of the 1,569 question texts the settled batch
judged appear in any leaf's induction pool"). KEEP.

**T-5 `tab:model-roster-pilot`.** Caption: "The pilot roster (Run~A), with
stored response format and ground-truth accuracy on the 241 judged Math
questions." The pilot is withdrawn entirely; what survives is the defect
record, and the one thing this table uniquely shows is the collinearity ("The
two format groups do not overlap in accuracy"), which `sec:res-capture-gap`
leans on. That is appendix material, not Experimental Design material: MOVE to
App. D beside the other historical roster. Note the surrounding section is the
stalest in the thesis — `sec:exp-rosters` opens "Three rosters appear in this
thesis" (pilot-8, 12-model, 11-model) and never mentions the settled r8 roster
at all; it also states "Every arena run sits on twelve models" and "The screen
was refitted at the twelve-model roster … the source of every screen $p$-value
quoted in this thesis (Table~\ref{tab:domain-screen})", both of which Chapter 5
(8-model refit, `sec:res-law`) now contradicts. The split subsection likewise
still says "the number of model pairs per leaf, $\binom{12}{2} = 66$ at the
twelve-model roster every paired run uses".

**T-6 `tab:arena-conditions`.** The C5 row still reads "No partition … with
Bradley--Terry fitted directly at the domain" and "What it controls: **the
partition itself**" — directly disowned by the paragraph beneath it ("Both
conditions therefore vary the judge prompt on a fixed partition") and by the
open `% TODO(author): rename C5. It is not a no-partition or no-taxonomy
baseline". This is the single most misleading table cell left in the document,
because it is the *summary* a skimming reader will take. UPDATE the row (and
either cut C3 or flag it pilot-only-and-withdrawn).

**T-7 `tab:run-record`.** Settled batch: 1,637 routed, 52 cells, 5,161
verdicts/arm; caption states the 3+1 short replays. Current, right size. KEEP.

**T-8 `tab:settled-recovery`.** 196/200, per-domain ρ, agreement 86.0% pooled;
caption states both-tie-convention identity and the conditional-on-commit
scope. Current. KEEP — and see V-1 in §5 for the figure that should sit beside
it, not replace it.

**T-9 `tab:tie-by-key`.** 13.0% vs 24.0%, ratios 1.3–2.5, all eight domains.
Current and honest. It is also the chapter's best case of a table forcing the
reader to do the figure's work (eight ratios read row by row); see V-2. KEEP.

**T-10 `tab:c5-decisiveness`.** Tie rate / conditional agreement / discordant
per domain, pooled 13.0/10.9, 86.0/87.2, 11/26. Current. The "discordant"
column's `0/0` and `1/2` cells are near-empty but the caption explains the
quantity; acceptable. KEEP.

**T-11 `tab:requirements-evidence`.** One row is stale: the second R2 row says
identification is reached "at 32.9 to 45 comparisons per cell, and the cost
varies across cells (Section~\ref{sec:res-cost})" — but `sec:res-cost` now
measures "all 52 cells, at between 7 and 10 comparisons per cell, median 7".
The 32.9–45 band is from the superseded era, and the row cites the very
section that contradicts it. Its caveat cell ("At 11 models there are 55 pairs
and the arithmetic was not redone") is likewise a leftover roster. UPDATE that
row; the other seven rows check out against their sections.

**T-12 `tab:j-floor`.** Five partitions, one J column, randomised rows with
percentile intervals labelled as such. Current offline analysis, exactly the
right size. KEEP.

**T-13 `tab:anchor-cells`.** The "run pool" column disagrees with
`tab:run-record`'s routed-question counts for five of the eight run domains:
engineering 202 vs 158, physics 237 vs 229, law 277 vs 276, cs 159 vs 158,
philosophy 130 vs 129 (math, history, psychology agree). The caption defines
the column as "the in-scope count that run recorded", and the table note
explains the harness-vs-run 3,445→2,884 disagreement — but nothing explains
run-pool-vs-routed, and at engineering the gap is 44 questions, far too large
to pass as rounding. Either the column is superseded counts (refresh from the
r8 DBs) or it is a third quantity (in-scope-but-unsampled included), in which
case the caption must say so and cross-reference `tab:run-record`. UPDATE.

**T-14 `tab:rubric-null`.** Four pre-registered discriminators, directions
stated. Current (re-derived 07-30 per the section's qualification list). KEEP.

**T-15 `tab:granularity`.** The analysis is ground-truth-only and offline, so
the run withdrawals do not void it — but the caption names no roster at all,
and the section's provenance sentences call the 8-model roster used "the
8-model pilot roster", a name that now denotes a withdrawn run. A reader
applying this review's own standard ("is the caption honest about which
roster?") cannot answer from the caption. REWORK-CAPTION: state GT-only, the
roster(s) (8-model pilot + 11-model band), and that the 88-leaf row is the
pre-correction snapshot control. Optionally add a settled-roster column for
coherence with the rest of the chapter; the finding (flatness) will not move.
The chapter's deliberate no-figure ruling here ("A box plot of four heavily
overlapping distributions makes a null look like a finding … The plotting
script written for it declines to draw") is correct — keep it.

**T-16 `tab:domain-screen`.** Refit at the settled roster, caption carries the
non-endorsement ("the selection was fixed under the earlier twelve-model fit
and carries no endorsement from this one") and the ρ=1.000 p-value caveat.
Current. KEEP. This table also *replaces* two orphaned figures (see §6).

**T-17 `tab:res-summary`.** Two defects. (1) The RQ2 cell is a visible erratum
posing as a verdict: "Every per-domain $\Delta\rho$ that stood here
(psychology $+0.0210$, …) came from the superseded twelve-model batch and was
measured against a decisive threshold since withdrawn. Report per-verdict
answer-key agreement instead." — that is an instruction to the author, printed
in the thesis's summary table, and it re-lists all the withdrawn numbers on
its way out. Rewrite as the settled verdict (identical rankings 7/8 domains;
decisiveness 13.0 vs 10.9; conditional agreement 86.0 vs 87.2; 11/26,
p=0.020). (2) The RQ1 cell asserts "agreement is highest with no reasoning
text, an inversion that strengthens to 97.0% against 83.2% at matched
capability (on 33 comparisons against 173)" — those numbers appear nowhere in
`sec:res-correctness`–`sec:res-tie-policy`, which the row points to; they are
the trace-confound analysis from the earlier runs. Source them from a settled
section or cut them from the row. UPDATE.

Also in the chapter head, the reading-conventions box quotes over-sampling
"43.2% to 67.9% … against the 16.7% a uniform scheduler would give at twelve
models" — twelve-model numbers described as "the completed paired runs";
stale under the withdrawal, needs restating from r8.

**T-18 `tab:hyperparams`.** Matches `tab:frozen-artifact`; the four
read-backwards warnings beneath it are current. KEEP.

**T-19 `tab:domain-registration`.** Outcome column empty, caption says why
("every outcome recorded before 2026-07-31 came from the superseded
twelve-model batch"), TODO instructs filling with per-verdict agreement. The
design is right; the fill is owed. UPDATE (fill, per its own TODO).

**T-20 `tab:arm-differences`.** Four-row bundle table plus the "Identical:"
footer row — this is the table `sec:res-c5` leans on for the bundle caveat,
and it is exactly right. KEEP.

**T-21 `tab:roster-r8`.** Read from the batch's own match histories; carries
the three honesty flags (5-shot, 21.4% bare, base model). KEEP.

**T-22 `tab:model-roster` (12-model).** Its own TODO: "once Chapter 5's Run A
and Run B material is restated from the settled batch, this section reduces to
a single sentence and Table~\ref{tab:model-roster} can go." Remaining
consumers are the stale spots flagged above (conventions box, res-summary RQ2
cell, `sec:exp-rosters`). DELETE once those are swept; until then it is the
provenance record for text that still exists, so deleting it first would
orphan citations.

**T-23 `tab:pipeline` (App. E).** Phase/class/output mapping; current
architecture (no cross-link phase). KEEP.

**T-24 AI-use table (`i_AIUse.tex`).** Version cell is the literal
"\textit{[versions used]}" and a "[further tool]" row is empty; the file's own
comment says "The affidavit's declaration is only true once this table is
complete." Not a results table, but it is the one table that can invalidate
the declaration. UPDATE before submission.

---

## 4. FIGURE_PLAN.md status

The plan is dated 2026-07-31 but was drafted mid-batch ("math, physics, law,
engineering complete; psychology running") and pre-withdrawal in places. Line
anchors it cites are dead throughout.

**Section 1 (current state): stale.** Lists `verdict_mechanism` as placed at
`5_Results.tex:304`; it has since been removed from the chapter (correctly —
it is Run A data). `frozen_tree` marked restored: confirmed.

**Section 2 (new figures F1–F6):**

- **F1 `validity_scatter` — alive, respecify.** Written for "102 of 105
  key-decidable model pairs recovered across four domains"; the settled figure
  is 196/200 across eight. Everything else in the spec (grey undecidable band,
  filled/hollow, label the misses) survives and is the right encoding. Build
  at 8 domains only, per the plan's own build-order rule.
- **F2 `rubric_vs_generic` — alive in spirit, numbers dead.** The 4-domain
  draft numbers (97 vs 51, pooled p = 0.0002, "drho = 0.0000 in every domain",
  slope values 79.3→82.7 …) are superseded: on the settled batch the
  discordant split is 11/26 (p = 0.020), conditional agreement 86.0 vs 87.2,
  rankings identical in 7/8 with one cs transposition, and the headline
  separation is *decisiveness* (13.0% vs 10.9% ties, 8/8 domains). The framing
  must soften from "the generic prompt beats the rubric" to "the rubric arm
  abstains more; conditional accuracy is about a point apart" — which is what
  `sec:res-c5` now says. The plan's "Caution — this result contradicts a
  section title" item is moot: that section title no longer exists.
- **F3 `cell_budget_and_uncertainty` — alive; adjust panel (b).** Panel (a)
  (comparisons/pair per cell vs the ~143 rule) matches the settled facts
  (1.6–5.0 achieved, identification at 7–10). Panel (b)'s bootstrap CIs
  collide with `sec:exp-metrics`'s blanket "No confidence interval is reported
  anywhere" — either amend that sentence (it was written against BT SEs) and
  label the intervals bootstrap-percentile in the caption, or re-encode
  without intervals. The protective purpose (foreclose the specialisation
  reanalysis) stands.
- **F4 `rank_recovery_grid` — unblocked.** The build gate ("needs all 8
  domains") is now satisfied. Still the right chapter-opening figure; note it
  partially overlaps `tab:settled-recovery`, so its caption should carry the
  per-model displacement reading that the table cannot.
- **F5 `design_schematic` — alive, unchanged, cheapest.** Chapter 4 still has
  no figure and its C5 row actively misleads (T-6). The plan's precondition —
  resolve the `% TODO(author): rename C5` first — is still open at
  `sec:exp-arena-conditions`.
- **F6 `judge_verdict_composition` — still optional**; its numbers need
  re-deriving from r8 (decidable share, tie 13.0%). Cut it if V-2 (below) is
  built, which carries the denominator story more directly.

**Section 4 (re-place the five orphans): mostly dead — this is what changed
today.**

- `frozen_tree` — done, correct.
- `routing_slopegraph` → "5.3.2 `sec:res-adapted-partition`" is a
  misattribution: the script's own header says it is "Figure 1.1 (routing
  micro-example slopegraph) … synthetic, declared-illustrative values from …
  Section 1.1.2 and Table 1.1". The rewritten introduction contains no
  micro-example, no Table 1.1, and no figure references at all. The plan
  probably meant `routing_provenance`. Either way: do not place.
- `domain_screen` → dead. The script asserts the registered **11-model** screen
  (economics p=0.003, health p=0.001, history p=0.003, law p=0.008 significant)
  which the settled 8-model refit contradicts outright (saturated; only law
  0.994/p=0.003 and chemistry 0.976/p<0.001 depart). Regenerating it at the
  settled roster would draw twelve bars at ρ=1.000 — `tab:domain-screen`
  carries that better than any figure.
- `screen_vs_arena` → dead twice over: reads the six `ratings_*_paired.db`
  (12-model, withdrawn) and plots against `THRESHOLD |Δρ| ≥ 0.007`, withdrawn.
- `rho_levels` → dead for the same two reasons (12-model DBs, `THRESHOLD =
  0.007` in the source). The plan's own caution ("Check `rho_levels` before
  restoring it") resolves as: drop, don't regenerate — its argument ("levels
  move more than contrasts") is now made in prose by `sec:res-tie-policy` with
  the seed replicate, on settled data.

**Section 5 (resulting inventory): obsolete** — it counts `verdict_mechanism`
plus four restored orphans in Results; the real number of placed Results
figures today is two, one of them needing regeneration.

---

## 5. The recommended visualisation set (ranked, essential first)

Ground rule kept from the plan: schematics are TikZ, data figures are
`make_*.py` + Agg + real data + assert-before-draw; nothing final built from
fewer than 8 domains. Chapters 2 and 6 stay figure-free — the plan's ruling
("add nothing merely to fill"; Discussion "argues from Chapter 5's figures")
is correct and is reaffirmed here.

**Essential (build these four):**

**V-1. `settled_validity_scatter` — the 196/200 monotonicity claim (= F1
respecified).**
Claim: the arena's BT ordering tracks the key wherever the key can see, and
all four misses sit where the key is nearly indifferent. Encoding: one point
per (domain, pair), n=224; x = |p_a−p_b|, y = θ_a−θ_b signed to agreement;
grey band = the 2·pooled-SE undecidability criterion of
`sec:res-correctness`; hollow = 24 undecidable pairs; label the 4 misses.
Why it beats `tab:settled-recovery`: the table proves the count; the scatter
proves the *shape* — monotone, misses at the smallest gaps, the decidability
boundary a property of the data rather than a caveat. Data:
`experiment_results/r8/<dom>/ratings_r8_<dom>.db:match_history` (MAIN) +
`mmlu_pro_dataset_cache_v2.db:eval_results`, joined by str(question_id),
8-roster-restricted; BT via the service's MM fitter. Difficulty: medium (join
traps: `ratings_r8_cs.db` name, capitalised categories in
`embeddings_cache.db` if touched).

**V-2. `tie_signature` — the 13.0%→24.0% abstention doubling.**
Claim: the judge's tie rate nearly doubles exactly where the key stops
discriminating, in all eight domains, in both arms from different bases.
Encoding: dumbbell per domain (decidable→undecidable tie rate), MAIN filled /
GENERIC hollow, pooled row emphasized; ratios as right-margin labels.
Why it beats the tables: this is the chapter's mechanism-signature claim and
it currently lives across *two* tables (`tab:tie-by-key` plus the tie columns
of `tab:c5-decisiveness`); "eight dumbbells all leaning the same way" is the
one-glance form of "the direction holds in all eight domains (ratios 1.3 to
2.5)". Data: same DBs as V-1, counts only, no BT fit. Difficulty: easy.

**V-3. `budget_vs_resolution` — identification is free, resolution is not
(= F3 respecified).**
Claim of `sec:res-cost`: all 52 cells connect at 7–10 comparisons (floor 7),
while resolution needs ~143 comparisons/pair and cells get 1.6–5.0.
Encoding: log-x strip, one dot per cell = achieved comparisons/pair, grouped
by domain, vertical rule at 143; small inset or rug at 7–10 for
identification. Why it beats prose: the two-orders-of-magnitude gap is the
whole point and is currently carried by two numbers in a paragraph; on a log
axis it is one visible gulf. Interval policy: draw no CIs, which sidesteps the
`sec:exp-metrics` no-CI rule entirely; if the caterpillar panel (F3b) is
wanted, the rule must first be amended. Data: `match_history` grouped by
`node_id`. Difficulty: easy.

**V-4. `design_schematic` — split, routing, and the shared triples (= F5,
TikZ, Chapter 4).**
Claim: C5 replays MAIN's exact (cell, pair, question) triples under MAIN's
cells — it varies the prompt bundle and nothing else. Chapter 4 has zero
figures and its own summary table currently asserts the opposite (T-6), so
this figure is also the repair for the most-misread design fact in the
thesis. Counts are settled (12,118 → 8,673/3,445 → 1,637 routed → 52 cells →
two arms reading one triple set). Precondition: resolve the C5 rename TODO so
the box is drawn with its final name. Difficulty: easy (TikZ, no data).

**Nice-to-have (in order):**

**V-5. `rank_recovery_grid` (= F4).** 8 models × 8 domains, signed rank
displacement, hatch undecidable cells. Now buildable. A mostly-white grid *is*
the "replications of one measurement" result of `sec:res-law`; place at
`sec:res-runs` as the orienting figure. Overlaps T-8 — justify via the
per-model displacement reading or skip.

**V-6. Repaired panel (b) for `fig:rubric-specific`.** Not new — this is the
F-5 regeneration from §2, listed here because it competes for the same effort
budget and ranks above V-5 if only one can be done: it fixes a placed figure
that currently rests on withdrawn data.

**V-7. `rubric_reach` placement.** Already built from r8; costs a float and a
caption. Covers the continuous dose-response side of `sec:res-offsubject`.

**V-8. `discordance_split` (= F2 reduced).** If `tab:c5-decisiveness` is felt
to under-sell RQ2: a single diverging bar of the 11/26 discordant split with
its binomial interval, plus the eight tie-rate slopes. Only worth building if
the RQ2 verdict in T-17 is rewritten to lean on it; otherwise the table
suffices at settled effect sizes.

Not recommended: any figure for `tab:granularity` (the chapter's own
declines-to-draw ruling is right); a Background/Chapter-2 diagram (nothing in
`sec:benchmarks`–`sec:synthesis` makes a claim a diagram would test); a
domain-screen figure (twelve identical bars).

---

## 6. Orphaned artifacts to clean up

PDFs with no `\includegraphics` consumer, with their scripts:

| Artifact | Script | Why dead | Action |
|---|---|---|---|
| `verdict_mechanism.pdf` | `make_verdict_mechanism.py` | Reads `experiment_results/arena_math_frozen/seed_42/judging/*.csv` — Run A, withdrawn; consumer removed from 5_Results today. Its panel-(b) numbers (863/868) survive as prose in `sec:res-capture-gap`, which is the right level of dignity for withdrawn data. | Retire both (git history preserves them). |
| `rho_levels.pdf` | `make_rho_levels.py` | 12-model `ratings_*_paired.db`; hard-codes `THRESHOLD = 0.007`, withdrawn. | Retire both. |
| `screen_vs_arena.pdf` | `make_screen_vs_arena.py` | 12-model paired DBs + asserts the 11-model screen p-values (law 0.008 etc.) superseded by the 8-model refit. | Retire both. |
| `domain_screen.pdf` | `make_domain_screen.py` | Asserts the registered 11-model screen; contradicts `tab:domain-screen` (settled refit: saturated). | Retire both; the table replaces it. |
| `routing_slopegraph.pdf` | `make_routing_slopegraph.py` | Synthetic Chapter-1 micro-example (its own header: "the ONLY figure in the thesis that is not real data"); the rewritten introduction has no micro-example and no Table 1.1. | Retire unless the motivating example returns to Chapter 1. |
| `routing_provenance.pdf` | `make_routing_provenance.py` | Current (r8, 07-31) but unplaced; 37.2% vs 77.8% on-subject definition conflict with `sec:res-offsubject` (see §2). | Hold; reconcile the convention, then place or retire. |
| `rubric_reach.pdf` | `make_rubric_reach.py` | Current (r8, 07-31), unplaced. | Place (V-7). |

Scripts with no PDF: `make_granularity_flat.py` — deliberately declines to
draw, and `sec:res-granularity` cites that refusal as part of the argument.
Keep the script; it is documentation.

Housekeeping adjacent to the figure pipeline: the withdrawn paired-run
databases (`ratings_math_paired.db` … `ratings_psychology_paired.db`) sit in
the repository root, while the removal note in `sec:res-c5`'s comment block
says "Their databases are under testing/ and are retained". Either move them
or fix the note — any retired script above that someone re-runs will still
find them at root and silently regenerate withdrawn-data PDFs.

Finally, `FIGURE_PLAN.md` itself should be rewritten or superseded by this
review: its current-state table, its orphan-restoration section, and four of
its six figure specs carry pre-withdrawal numbers, and it is the document a
future session will reach for first.
