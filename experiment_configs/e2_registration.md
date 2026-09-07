# E2 registration — held-out routing fit: tree vs bridged vs placebo (frozen before the full run)

Harness: branch worktree-agent (commit 0cc7954), E2BridgeRunner + scripts/e2_bridge_analysis.py,
smoke-tested at n=200 (smoke numbers are disclosed as seen and adjudicate nothing).
Conditions on the frozen snapshot 20260727_042523: T = tree as-is; B = +8 bridges on the
E1 top pairs (donor = lowest ancestor of the primary not already a parent of the secondary);
P = +8 placebo edges (random depth-matched donors from other anchors, seed 999).
Metric: per-question ll(q) = logSumExp over reached leaves of [log path mass + vMF log
density] on the full reserved pool (3,599 questions).

PRIMARY (two-sided, frozen): D = (B−T) − (P−T) per question, full pool.
  "Bridges add predictive fit" iff mean D > 0 with the seeded 10,000-fold bootstrap 95% CI
  excluding 0 AND exact sign test p < 0.05. Any other pattern (CI straddling 0, or D < 0)
  is the TREE verdict for E2: structural bridges add nothing beyond edge-addition mechanics.
SECONDARIES (descriptive): affected-subset D; per-pair breakdown; placebo robustness with
  seeds 1000/1001/1002 (primary is seed 999); Top-1 agreement and NoMatch deltas.
DISCLOSURES: the placebo intentionally carries the descent-gate-loosening side effect —
  it is the control for edge mechanics, gate effects included. The smoke run (n=200) was
  seen before this freeze: (B−T) −0.019, (P−T) +0.014, D −0.033 (p=0.12); the full pool
  is 18x larger and the criteria above were fixed without further peeking.

## OUTCOME (2026-09-07, full pool, analysis run unchanged)

TREE VERDICT under the frozen criteria — decisively. Primary D = (B−T) − (P−T),
n = 3,599: mean −0.0141, 95% CI [−0.0244, −0.0037] (excludes 0, NEGATIVE side),
sign test p = 0.043 with the negative majority. The registered claim "bridges add
predictive fit" required D > 0; instead real bridges UNDERPERFORM placebo edges:
(P−T) = +0.019 [+0.012, +0.027] (edge mechanics help slightly), (B−T) = +0.005
[−0.003, +0.013] (real bridges capture less of even that mechanical benefit).
Bridging the genuinely-overlapping E1 pairs diverts beam mass in ways that reduce
held-out fit. Per-domain: the largest negative is Philosophy (−0.11), the bridged
leaf pulls mass from its own anchor; no domain shows the DAG-predicted gain.
Routing health identical across conditions (0 NoMatch; Top-1 agreement B 98.6%,
P 99.6%).

Reading: combined with E1 (overlap is real and pair-concentrated, p = 0.0005),
this is the SHARPENED TREE VERDICT the analysis agent gave 60% prior mass:
the overlap exists, soft routing already carries it, and structural edge-bridges
add nothing — measured this time by a DAG-sensitive criterion with a placebo
control, not by the partition objective. NOTE the scope limit: E2 tests
EDGE-bridges (second parent for an existing leaf). Shared-child EXTRACTION (E3)
is the one DAG variant still untested; per the registered sequence it only ran
if E2 favored bridges, so the program records it as the remaining open variant.
