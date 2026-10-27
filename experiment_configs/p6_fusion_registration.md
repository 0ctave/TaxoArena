# P6 registration record — twin fusion vs placebo fusion (criteria frozen in docs/v2_validation_plan.md, 2026-09-08)

Harness: E2FusionRunner (--e2-fusion-config) + scripts/e2_fusion_analysis.py, a clone of the
E2 bridge machinery. Conditions on the frozen snapshot 20260727_042523, full reserved pool
(3,599 questions), same ll metric (logSumExp over candidates of [log path mass + vMF log
density], residual mass scored at the gate-stopped node):

  T  = frozen tree as-is.
  F  = top-3 cross-anchor E1 twin pairs FUSED. Target = larger leaf, source = smaller:
       #1 Statistical Inference and Probability Theory (CS, n=121) <- Normal and Sampling
          Distribution Applications (Math, n=86)
       #2 Thermodynamic and Gas State Calculations (Chemistry, n=396) <- Thermodynamic and
          Heat Transfer Analysis (Engineering, n=344)
       #3 Quantum Photon Particle Duality Calculations (Physics, n=78) <- Quantum Particle
          Wavelength and Energy Transitions (Chemistry, n=62)
  Pf = 3 PLACEBO fusions, Random(999), matched member-wise on cross-anchor-ness and size
       (relative tolerance 0.25, widened x2 only when empty; E1 top-10 pair leaves excluded):
       #1 Contract Formation... (Law, 147) <- Elementary Algebraic... (Math, 75)   [tol 0.25]
       #2 Criminal Liability... (Law, 218) <- Comparative Functional... (Bio, 184) [tol 0.50]
       #3 Metabolic Biochemistry... (Health, 85) <- Psychotherapy Ethics... (Psych, 61) [tol 0.25]

FUSION MECHANISM (labeled choice): the QUERY-MOVE variant of TaxonomyMerger.fuseNodes —
source's queries/weights/residuals absorbed into the target (union, weights summed), vMF+NiW
blended n-weighted exactly as blendVmfAndNiw, source detached from its parents with NO parent
redirect (a fuseNodes redirect is ambiguous for cross-anchor pairs; the ll metric only cares
where mass can route), then root.updateAllShrinkages(). Snapshot loaded fresh per condition,
never saved back.

REGISTERED (two-sided, frozen in the plan before any run): D = (F-T) - (Pf-T) per question,
full pool primary; fusion helps iff mean D > 0 with the 10,000-fold seeded bootstrap 95% CI
excluding 0 AND exact sign test p < 0.05; otherwise the overlap program closes with soft
routing fully vindicated. Affected-subset secondary; per-pair breakdown descriptive.

DISCLOSURE: a 200-question smoke was seen before the full run (D +0.849 [+0.319, +1.450],
sign p 0.111 — same shape as the full result); the criteria were frozen in
docs/v2_validation_plan.md before the smoke.

## OUTCOME (2026-09-08, full pool n = 3,599)

NULL under the frozen criteria — the overlap program CLOSES, soft routing vindicated.
The conjunctive criterion fails on the sign test:

  D = (F-T) - (Pf-T): mean +0.1987, 95% CI [+0.0495, +0.3478] (excludes 0, positive)
  exact sign test: +1007 / -1085 / =1507, p = 0.0923  -> FAILS p < 0.05, and the
  nonzero MAJORITY is negative — the positive mean is carried by magnitude, not count.

Both fusion arms HURT held-out fit versus the tree:
  F  - T: mean -0.7284 [-0.8211, -0.6362], sign +409/-735, p = 3.9e-22
  Pf - T: mean -0.9271 [-1.0367, -0.8177], sign +473/-770, p = 3.3e-17
Real twin fusion is not better than placebo fusion where it matters — it merely destroys
slightly less likelihood on average. Affected subset (n=2,092): F-Pf mean +0.342
[+0.091, +0.602], sign p = 0.092 (same fail).

Per-pair (descriptive, subset = T admitted the pair's leaves): every real pair is NEGATIVE
on F-T — #1 Stats (n=81) -0.41; #2 Thermo (n=328) -6.85; #3 Quantum (n=63) -0.69. The
thermo fusion, the largest genuine twin, is the worst: collapsing two 300+-question leaves
into one vMF discards real distributional distinctness. Placebo fusions are more destructive
still (-7.2, -12.4, -3.9 on their subsets), which is what inflates the positive mean D.
Routing health: F introduces 128/3599 (3.6%) residual routings (leaf removal leaves beam
mass gate-stopped); Top-1 agreement with T: F 93.8%, Pf 94.6%.

Reading: with E1 (overlap real, pair-concentrated, p = 0.0005), E2 (bridges lose to placebo
edges), and now P6 (fusion loses to the tree and does not beat placebo fusion by the
registered test), every structural response to the measured overlap — edge, bridge, merge —
degrades held-out fit. The frozen tree's SOFT ROUTING already carries the overlap; the twin
leaves are redundant in identity but not in routing mass. Per the frozen plan, E3
(shared-child extraction) stays unrun and the overlap program is closed.
