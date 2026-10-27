# POSTRUN — ESCALATION-RC: the readout of escalation_rc.py --run

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls, no JVM. Object: `experiment_results/archv2/escalation_rc/outcome.txt`
(127 lines, sha256 4dad8268248f63dbf5719e965ec53ea5d21c37d641642b6adb14749cdf00f6cf, mtime 18:26:38), written by blob a17f6821
(main, `git hash-object` = a17f6821; merge 9127cbde). Marker `escalation_rc.READ_STARTED` sha256 d7fb05a8… (18:26:10; text
carries the frozen policy sha 8d68018c…). Pre-data brackets 421f261f were committed at 18:25:17, before the marker. Console:
scratchpad `erc_run.log` (128 lines). READY: docs/reviews/READY_escalation_rc.md.

## Verdict: VALID. RC1 UNDETERMINED (a boundary case); F-RC NOT FIRED; P1 (e, D_E, Brier) and P2 HELD

Every deciding number reproduces to the printed digit from my own script: own correctness key from eval_view (`mode=ro&immutable=1`),
own geometry (the snapshot vmfMu read independently), K_0 centroids rebuilt as the normalised TRAIN means of the k_cells_s0 cells.
The run's two-stage interval also reproduces at the registered seed. The one qualifier that must travel with the words is
**(Q1)**: the lower end is −0.00004. The point is positive and the registered interval touches 0 by less than its own Monte Carlo
error, so the result is neither "escalation helps" nor "no effect".

## Per-claim table (my number against the outcome's)

| # | claim | outcome | mine (independent) | verdict | sev |
|---|---|---|---|---|---|
| N | Deciding set | 5,907 / 5,404; TRAIN 11,841; GATE 2,033 | 5,907 / 5,404 from eval_view `response` (mc6, roster 18, MATH-FIX overlay); every scored item has a bundle vector | CONFIRMED | — |
| I | IDENTITY (R12) | best 0.6049, AF-U 0.6201, K0 0.6271, G_AF +1.52pp [+0.14, +2.91] REPRODUCED; B3 equal; both views' sha256 BEFORE = AFTER | acc best 0.60488, AF 0.62011, K0 0.62705 | CONFIRMED | — |
| G | Geometry | (R4 printed in the run) | AF argmax = cell of record 5,745 / 5,745 non-IFEVAL scored items; K_0 re-filed differs 0 / 5,907 | CONFIRMED | — |
| e | Escalated share | AF-U e 0.22600 (1,335; margin only 1,071, OOS only 172, both 92); K_0 0.22973 (1,357) | 1,335 and 1,357 escalated, using the GATE thresholds I reproduced in the READY (AF 0.016134 / 0.540800; K_0 0.024357 / 0.538278) | CONFIRMED | — |
| RC1 | D_E, two-stage 95% | +0.00497, [−0.00004, +0.00997], SE_2stage 0.00255; percentile [−0.00089, +0.00901] → UNDETERMINED | point +0.00497; identity e(gap_esc − gap_all) = 0.226 × (0.00674 + 0.01524) = 0.00497. Two-stage at seed 42 (the module's run_boot, outputs to scratch): lo −0.000036, SE 0.00255, the same digits. Seeds 1-9: lo −0.000021 to −0.000254, every one < 0 | CONFIRMED → UNDETERMINED, by a hair at every seed tried (Q1) | — |
| F | F-RC | NOT FIRED (fires iff FAILED) | upper +0.00997 > 0 | CONFIRMED | — |
| K | D_E(K_0) (descriptive) | +0.00425 [−0.00070, +0.00920] | +0.00425; gap_esc −0.00368, gap_all −0.02218 | CONFIRMED | — |
| Δ | D_E(AF-U) − D_E(K_0) (descriptive) | +0.00072 [−0.00554, +0.00697] | +0.00072 (difference of my two points) | CONFIRMED | — |
| P | Predictions | P1 e 0.226 ∈ [0.15, 0.35] HELD; D_E +0.00497 ∈ [−0.003, +0.010] HELD; Brier 0.1550 (UNDETERMINED); P2 +0.00072 ∈ [−0.006, +0.006] HELD | 0.25² + 0.30² + 0.05² = 0.1550 | CONFIRMED | — |
| W | Written once; console = outcome | `OUTCOME written write-once` (mode "x") | all 127 outcome lines are in the console except the 2 heading lines, whose em-dash the console rendered as U+FFFD (an encoding artefact, the same text otherwise). The 1 console-only line is the write-once line. 0 REFUSED / Traceback. One marker. Outcome sha unchanged after my scratch replicates | CONFIRMED | — |

## Support re-measured (beside the deciding statistic)

SE_2stage 0.00255 against 0.00367 registered; i.i.d. SE 0.00224; DEFF 1.302 against 1.595 (the source was UNION-AF-ROUTE U1); n_eff 4,538;
MDE80 0.00715. The observed +0.00497 is below the MDE80, so RC1 was DESCRIPTIVE-ONLY at the observed effect as well as at the
prediction. My one-stage cluster bootstrap over EVAL components (policy fixed) gives SE 0.00223, so the cluster DEFF is about 0.99:
the inflation comes from the TRAIN policy refit, not from clustering of items. The planning discordance 0.05 overstated the per-item
variance (implied 0.0296). Across seeds 1-9 the DEFF ranges 1.29-1.46.

## Applied conditions (READY C-1..C-3, bracketed pre-data 421f261f)

- **D-1 / C-1: e and D_E without IFEVAL (descriptive; one-stage, not a criterion).** IFEVAL escalates 95 of its 162 items (58.6%;
  all by OOS, never by margin). Without IFEVAL (5,745 items): AF-U e 0.21584 (1,240), D_E **+0.00579**, one-stage cluster
  percentile [+0.00123, +0.01018]; K_0 e 0.22019, D_E +0.00499. IFEVAL's term in the decomposition D_E = (1/N) Σ (f_i − e)(gap_i)
  is −0.00080 on both arms. **The IFEVAL OOS leg PULLS D_E DOWN; it does not carry it.** The no-IFEVAL interval excludes 0 only
  in a one-stage, post-hoc form, which is not the registered statistic. It never upgrades RC1 (C-7: SUBSTITUTED if it were quoted
  as the result). Per-source terms for AF-U (descriptive): MMLU_PRO +0.00249, BBH +0.00131, MUSR +0.00115 (MUSR has 0 escalated
  items: its term is −e × a negative gap), MATH +0.00073, GPQA +0.00009.
- **D-2 / C-2 (K_0 is source-conditioned).** K_0 picks its candidate cells by the declared source, so the +0.00072 difference is
  between the anchor-free tree and source-conditioned k-means. It is descriptive, its interval covers 0, and it is never "the tree
  escalates as well as / better than k-means".
- **D-3 / the (g) identity.** The outcome's STRUCTURAL line prints "|D_E| <= e x |acc gap on the escalated items|". Its own
  numbers violate that line: 0.00497 > 0.226 × 0.00674 = 0.00152. Read it as the identity D_E = e (gap_esc − gap_all) =
  0.226 × (+0.00674 − (−0.01524)) = +0.00497 (bracketed 421f261f). Most of D_E comes from the random baseline's loss
  (e × 0.0152), not from a large gain on the escalated items.

## Further disclosures that bind the wording

- **Q2: against random escalation, not against no escalation.** AF-U: acc(rule) 0.62164 vs acc(cells) 0.62011, +0.15pp in absolute
  terms. K_0: 0.62621 vs 0.62705, **−0.08pp**. On both arms the best single is about as good as the cells on the escalated items
  (gap_esc +0.0067 / −0.0037). The rule avoids the cost of random escalation; it buys almost no accuracy. Never write "escalation
  raises routed accuracy" without this.
- **Q3: risk-coverage (descriptive, post-hoc).** On AF-U, ordering by fragility peaks at 0.63230 at coverage 0.55 (+1.2pp over the
  cells). Fragility is not the registered rule (R6). That peak was seen in the data, so it can be a hypothesis only.
- The thresholds are fixed from GATE, so their variability is outside the interval (R7).

## Registrar's wording (proposed)

"ESCALATION-RC, content-closed v2 union split, 0 calls: escalating the AF-U cell route to the best single model on low margin or
OOS (GATE p20 / TPR 0.95; e 0.226 of 5,907 EVAL items / 5,404 components) beats escalating the same share at random by D_E
**+0.50pp, two-stage 95% [−0.004pp, +1.00pp]: RC1 UNDETERMINED, a boundary case** (the lower end misses 0 by 0.00004, within
the bootstrap's seed variation; −0.00002 to −0.00025 over 10 seeds; percentile [−0.09pp, +0.90pp]; below the MDE80 0.72pp).
F-RC NOT FIRED. Against no escalation the rule changes accuracy by +0.15pp (AF-U) and −0.08pp (K_0): the rule avoids the cost of
random escalation and buys almost no accuracy. Without IFEVAL, whose one-cell OOS leg escalates 59% of its items, D_E is +0.58pp
(descriptive, one-stage; not the criterion). Source-conditioned k-means (K_0) gives +0.43pp; the difference +0.07pp [−0.55,
+0.70] is descriptive and not tree-specific. P1 and P2 HELD."
Not licensed: "escalation works" / "helps" / "a usable safety valve" (RC1 is not HELD); "no effect" or "escalation does not help"
(the interval is almost wholly positive); any HELD from the no-IFEVAL or one-stage intervals; "tree = k-means"; the fragility peak
as a finding.

## Defects

- **D-PR-1 (LOW)**: the STRUCTURAL line of the outcome is false as printed (bracketed pre-data; the outcome is write-once and
  stays as written). A later delta of the reader prints the identity instead.
- **D-PR-2 (LOW)**: the Support overstated the SE (0.00367 vs 0.00255) through the planning discordance, not through the DEFF.
  Future escalation registrations should derive the discordance as e(1 − e) P(gap ≠ 0).

## Commands

```
sha256sum experiment_results/archv2/escalation_rc/{outcome.txt,escalation_rc.READ_STARTED} ; stat -c '%y' <both> ; git log -1 --format=%cI 421f261f
PYTHONIOENCODING=utf-8 python - # set compare: outcome lines vs erc_run.log (2 U+FFFD heading lines, 1 console-only write-once line, 0 REFUSED)
python scratchpad/erc/recompute_post.py   # own key, own geometry, own K_0 centroids: counts, accs, D_E, identity, ex-IFEVAL, per-source, one-stage SE
SEEDS=42,1,...,9 python scratchpad/erc/seed_sens.py   # module run_boot at 10 seeds, outputs to scratch; seed 42 = outcome digits; outcome sha unchanged
```
