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
