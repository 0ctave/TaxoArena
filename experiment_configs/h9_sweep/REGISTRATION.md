# H9 extended sweep — registration (frozen before launch, 2026-09-07)

34 construction runs, all local, one knob (or only the seed) changed per run from
freeze_mcs55.toml with labeling/judging/final-metrics off. Analysis =
tools/analysis/h9_stability.py on every run vs the frozen artifact, and every
settings arm judged against the SEED VARIANCE FLOOR (now 20 seeds: the original
5 plus 16 here). Arm-1 claims (alpha/beta) were already adjudicated PASS on the
registered 5-run set (394786a); the 16 extra seeds are a disclosed extension that
tightens the floor estimate and re-checks alpha/beta descriptively at n=20.

Frozen expectations (descriptive; deviations reported as-is):
- bar 0.07 (within-domain-null territory): leaf count roughly halves, held-out
  Top-1 stays within the seed floor (the thesis "flat discriminative power" claim).
- bar 0.015 (below the isotropic-justified 0.025): leaf count rises; watch the
  cycle detector — this is the historical limit-cycle regime.
- mcs {30, 40, 75}: leaf count scales roughly like corpus/mcs (~110/95/65).
- routingBeamGamma {0.1, 0.3}, descentMargin {0.06, 0.18}, membershipFloor
  {0.15, 0.35}: never swept at the frozen operating point — purely descriptive;
  the interesting readout is whether Top-1 leaves the seed floor.
- acceptanceZ 0 (legacy lexicographic rule): quantifies what the z-gate buys;
  expect more accepted edits and a larger tree.

## OUTCOME (2026-09-07, all 34 runs + frozen baseline; analysis = h9_stability.py,
## archived at experiment_results/h9_sweep/stability_all.txt)

- SEEDS (n=20 incl. arm 1): Top-1 0.750-0.776 (spread 2.6pp — a hair above the
  arm-1 bar of 2.5pp, which was adjudicated PASS on its registered 5-run set and
  stands; the n=20 re-check is descriptive as registered). Leaves 72-92, anchor
  drift <= 0.59pp everywhere, mu-match 62-79/87. The arm-1 reading holds at 4x
  the sample: anchors and routing invariant, leaf identity is a sample draw.
- BAR: expectation WRONG in an informative direction. 0.045 and 0.07 do not
  "roughly halve" the leaf count — they COLLAPSE the tree to 16-20 leaves at
  depth 2 (near anchor level), confirming that almost all sub-domain splits sit
  below the within-domain null band. Top-1 drops only 2-4.6pp even so (0.728-
  0.739) — discriminative-power flatness holds under massive coarsening, though
  these values sit just below the seed floor, a deviation reported as-is.
  bar 0.015 (below the isotropic-justified bar): mild over-splitting (90-94
  leaves), elevated iterations (11-16), and ZERO cycle-detector fires — the
  create/destroy gate-consistency fix holds even in the historical limit-cycle
  regime.
- MCS {30,40,75}: leaves 151 / 112-119 / 58-60 — monotone as predicted, Top-1
  flat (0.746-0.779).
- BEAM {0.1,0.3} and DESCENT-MARGIN {0.06,0.18}: INERT — outputs bit-identical
  to each other (Top-1 equal to 16 digits, structures mu-match 87/87). Verified
  the overrides were parsed and applied; the gates simply do not bind in these
  ranges (Top-1 is provably beam-invariant: the argmax path survives any beam).
  This CLOSES construction-audit risk 7 (unswept routingBeamGamma): the knob is
  insensitive where it lives.
- MEMBERSHIP-FLOOR {0.15,0.35}: mild structural effect (91 / 84 leaves), Top-1
  in the seed band.
- Z=0 (legacy lexicographic rule): 90 leaves vs 87 — the z-gate trims ~3
  marginal leaves; Top-1 unchanged. The acceptance-rule choice is not
  load-bearing for evaluation.
- NOTE, disclosed: today's seed-42 rebuilds reproduce the frozen structure
  (mu-match 87/87, same mass 8,299) but Top-1 differs from the July frozen run
  by ~0.9pp (0.7666 vs 0.775) — same-config drift across code versions since
  c381211, within the seed band, and exactly what the planned byte-diff
  determinism CI (H9b) exists to catch. Run exports kept locally (~300MB, not
  committed); stability_all.txt is the committed record.
