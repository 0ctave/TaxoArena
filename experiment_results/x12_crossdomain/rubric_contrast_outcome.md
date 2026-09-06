# Rubric-value contrast — OUTCOME (2026-09-06)

Registration: `tools/analysis/rubric_value_contrast.py` header, committed 7037035
before any generic-arm verdict existed. Analysis = `--analyze` run UNCHANGED on the
completed caches. Cell-rubric arms are pre-existing caches (Mistral = the x12 run's
match_history; grok = the R3 re-judge cache); generic arms were collected for this
contrast through the byte-identical prompt template with only the system prompt and
rubric line swapped for the fixed generic text.

## Data

| arm | judge | rubric | matches | invalid |
|---|---|---|---|---|
| x12 | Mistral-Large-3 | cell | 9,144 | 0 |
| new | Mistral-Large-3 | generic | 9,144 / 9,144 | 0 |
| R3 | grok-4-1-fast-non-reasoning | cell | 1,980 | 0 |
| new | grok-4-1-fast-non-reasoning | generic | 1,980 / 1,980 | 1 |

The single grok generic INVALID (both presentation orders unparseable) is excluded
by the registered `invalid=0` filter, leaving 1,979 grok pairs. One Mistral generic
match (6528) failed with an HTTP 400 during the main collection sweep; the identical
request succeeded on retry the next day (transient), completing the arm at 9,144.

## REGISTERED PRIMARY — CONFIRMED

Mistral pair, key-decidable matches (n = 4,509; verdict correct iff it names the
GT-correct model, TIE/INVALID count wrong):

- correct-verdict rate: **cell 0.757 vs generic 0.741** (+1.5 pp)
- discordant pairs: 196 cell-only-correct vs 127 generic-only-correct
- exact two-sided McNemar **p = 0.0001**

## Robustness (grok, pre-registered secondary) — same direction

- cell 0.743 vs generic 0.719 (+2.4 pp), discordant 57 vs 34, McNemar p = 0.0206.
- The cell-rubric advantage therefore replicates in a judge family that did NOT
  write the rubrics. Directionally the foreign judge gains MORE from the rubrics
  (+2.4 vs +1.5 pp); no test of that difference was registered and none is claimed.

## Other secondaries

- Tie rates: Mistral cell 0.194 vs generic 0.185; grok 0.236 vs 0.235. The cell
  advantage is NOT explained by committing more often — the cell rubric ties
  slightly MORE yet is more accurate where the key decides.
- 12-model board (Mistral, full 9,144 per arm): Spearman rho = 1.000, order
  IDENTICAL under both rubrics. Rubric value is a per-verdict accuracy effect;
  the aggregate ranking is robust to rubric choice (consistent with the x12/GT
  rho 0.951 being reachable even under a generic judge).

## Disclosures

1. Two ~8-match mechanics pilots (one per judge) ran before the registration
   freeze to validate parsing/caching; their verdicts were deleted and re-collected
   and adjudicated nothing.
2. A mid-collection progress peek at ~17% of the Mistral arm showed the OPPOSITE
   direction (generic ahead by ~1.1 pp). No analysis choice remained free at that
   point (test, sample, and filters were frozen at 7037035), so it adjudicates
   nothing, but it is disclosed — and is a caution against interim readings of
   paired contrasts.
3. The grok pair reuses the R3 sample (1,980 stratified matches, 600 oversampled
   from the top cluster); it is a robustness check, not an independent draw.

## EXPLORATORY (post-hoc, adjudicates nothing): where the rubric helps

Per-anchor breakdown of the Mistral pair (grouping formed AFTER seeing this table):
the advantage concentrates in qualitative domains — Philosophy +5.7 pp (13:4,
p=0.049), Biology +5.1 (18:4, p=0.004), History +3.4, Health +2.9, Economics +2.6 —
and vanishes in formal ones (Math +1.3, Physics +0.6, Engineering 0.0, Chemistry
-0.7, CS -0.9). Pooled qualitative-vs-quantitative: QUAL +2.7 pp (131:67,
p<0.0001) vs QUANT +0.2 pp (65:60, p=0.72). Plausible mechanism: in formal domains
correctness is self-evident from the trace, so the generic instruction is already
near-optimal; cell rubrics add discriminating criteria where grading is judgmental.

Headroom check (is the split just ceiling effects / judge skill?): the Mistral judge
is WORSE at qualitative domains under the generic rubric (0.719 vs 0.766), so the
gain does not track judge strength — it tracks judge weakness, with more headroom
where grading is judgmental. Baseline anti-correlates with gain across anchors
(r = -0.56), so headroom explains part of the gradient, but not all of it: on
relative error reduction (which normalizes headroom away) QUAL fixes 9.6% of
remaining errors vs 1.0% in QUANT, Computer science has ample headroom (0.714
baseline) yet a NEGATIVE gain, and Math has the least headroom (0.813) yet the
best QUANT reduction (7.1%). Judge domain skill itself cancels in the pairing
(both arms share the judge); only ceiling proximity does not, and it is handled
by the relative metric.

Cross-family check does NOT confirm the concentration: grok gains roughly uniformly
(QUAL +2.5, p=0.10; QUANT +2.3, p=0.13) — though its sample is 1/5 the size and
domain-non-representative (R3 top-cluster oversampling). Status: hypothesis only;
a confirmation would need a registered qual-minus-quant difference test on new data.

## Interpretation

The thesis RQ2 claim — that induced cell-specific judge rubrics measurably beat a
generic judge — is supported on the registered confound-free design: same matches,
same questions, same response traces, same template, judge family crossed. The
effect is small per verdict (+1.5–2.4 pp) but systematic (p = 0.0001), and it does
not move the aggregate board, which localizes the rubric's value to exactly where
the thesis claimed it: individual verdict quality.
