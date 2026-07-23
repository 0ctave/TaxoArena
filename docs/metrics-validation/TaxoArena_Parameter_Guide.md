# TaxoArena — Parameter Guide for Calibration

Every tunable parameter: what it controls, how changing it moves the DAG structure
and the results, its interactions, and calibration guidance. Verified against HEAD
(TaxonomyConfig.kt). Values are code defaults; your canonical build overrides several.

Legend: ↑ = increasing the parameter. "structure" = DAG shape; "results" = routing/
arena metrics. [SWEPT] = currently in the L9 sweep. [NEW] = added in the rework.

═══════════════════════════════════════════════════════════════════════════════
## GROUP A — GRANULARITY & DEPTH (how many leaves, how deep)
═══════════════════════════════════════════════════════════════════════════════

### minClusterSize (default 25; canonical 50)
- Controls: minimum queries a node needs to split further.
- ↑ → FEWER, LARGER leaves (coarser taxonomy). ↓ → more, smaller leaves (finer).
- Structure: strongest single lever on leaf count (empirically r ≈ -0.95 with leaf
  count). Directly sets granularity.
- Results: ↑ raises per-leaf sample size → better judge induction, but coarser
  domains (less specific judges). ↓ risks tiny low-support leaves (SmallLeafFraction ↑),
  noisier judges, starved leaves.
- Calibration: the granularity dial. Set by target leaf count / min viable judge
  corpus. 50 keeps SmallLeafFraction ≈ 0. Sweep if leaf count is off-target.

### maxDepth (default 12; canonical 8)
- Controls: hard cap on taxonomy depth.
- ↑ → allows deeper hierarchies; ↓ → flatter.
- Structure: rarely binding — observed avg leaf depth ~3.2, so 8 is ample. Acts as a
  runaway-recursion guard, not a shaping parameter.
- Calibration: leave at 8 unless you observe leaves hitting the cap (they don't).

═══════════════════════════════════════════════════════════════════════════════
## GROUP B — SOFT ASSIGNMENT / ROUTING (where queries go, multi-membership)
═══════════════════════════════════════════════════════════════════════════════

### constructionMargin [NEW] (default 0.20)  ← replaces deltaAssign for construction
- Controls: the unified membership margin during DAG-building trickle (post-rework).
- ↑ → BROADER soft descent: queries assigned to more branches/leaves → smeared,
  less crisp structure, more bridges/overlap. ↓ → tighter, crisper clusters.
- Structure: governs how much multi-membership shapes the DAG. Too high smears
  cluster identity; too low makes it a near-tree.
- Results: ↑ raises AvgMatchCount, BorderlineRate; interacts with calibration.
- Calibration: the primary structural-breadth dial post-rework. Keep TIGHT (favor
  crisp structure). Center around the value reproducing ~current 29% multi-leaf rate.

### arenaMargin [NEW] (default 0.40)  ← arena-time membership breadth
- Controls: membership margin at ARENA/eval time (looser than construction by design).
- ↑ → more soft members per leaf at eval → richer judge-induction corpora, more
  cross-domain queries participate, more generalization. ↓ → stricter eval membership.
- Structure: NONE — does not change the persisted DAG, only eval-time membership.
- Results: ↑ enriches per-leaf samples (better judges) but risks immigrant queries
  diluting a leaf's identity. Directly controls the "close embeddings → close judging"
  breadth.
- Calibration: tune SEPARATELY from construction (does not affect DAG). Explore
  looser values; monitor native-vs-immigrant judge coherence as the guardrail.

### deltaAssign [SWEPT] (legacy; being replaced by constructionMargin)
- Controls (legacy): log-softmax descent margin. Dominant lever on BorderlineRate/ECE
  (|r| ~0.85-0.97 observed).
- ↑ → broader routing → BorderlineRate ↑, ECE ↓ (better calibration but more
  ambiguity), MaxAssignmentCapRate ↑. Inverse-correlated with ECE at r ≈ -0.97.
- Calibration note: post-rework this folds into constructionMargin. Until then it is
  the ECE/borderline dial — but recall BorderlineRate is now a DIAGNOSTIC, not a gate.

### assignmentCosineGap [SWEPT] (default 0.03; canonical 0.15)
- Controls: leaf-qualification margin, SCALED by sibling κ (marginNats = gap × κ).
- ↑ → more leaves qualify per query (broader final assignment). ↓ → stricter.
- Structure: none directly; affects final leaf membership set.
- Results: weak on ECE/borderline; stronger on Top-1 accuracy (r ≈ 0.54) and
  cross-anchor migration (r ≈ -0.54).
- Calibration: secondary lever; tune for Top-1 / migration once margin is set. Post-
  rework this also folds into the single margin rule.

### maxLeafAssignments (default 5)
- Controls: hard cap on leaves per query.
- ↑ → allows broader multi-membership; ↓ → forces sparser assignment.
- Results: caps AvgMatchCount tail. ~3.3% of queries hit the cap of 5 (mild binding).
- Calibration: 5 is reasonable. Lower only if you want to force sparser membership.

### routingSoftmaxTau (default 1.0; canonical 1.50)
- Controls: base temperature of the routing softmax.
- ↑ → softer routing (flatter distribution, more ties → more multi-assignment). ↓ →
  sharper (more confident single-leaf).
- Results: ↑ raises BorderlineRate/AvgMatchCount, similar direction to margin but
  weaker. Interacts multiplicatively with κ via tauKappaScalingFactor.
- Calibration: secondary temperature dial. Held fixed at 1.5 last gen. Sweep if the
  margin alone can't hit the target multi-leaf rate.

### tauKappaScalingFactor (γ) (default 0.0)
- Controls: couples routing temperature to cluster concentration: τ_eff = τ·κ^γ.
- ↑ (toward 1.0) → tighter clusters route MORE sharply (temperature drops where κ is
  high). 0.0 = unscaled (κ-independent temperature).
- Structure/results: this IS the geometry-adaptation mechanism for routing. γ>0 makes
  routing confidence adapt to local concentration.
- Calibration: ABLATION variable for the geometry-adaptation study ({0.0, 0.5, 1.0}).
  Keep 0.0 as canonical; report γ>0 as an ablation.

═══════════════════════════════════════════════════════════════════════════════
## GROUP C — SPLITTING (when a node divides)
═══════════════════════════════════════════════════════════════════════════════

### separationEpsilon (default 0.04; canonical 0.01)
- Controls: Dasgupta-delta floor to ACCEPT a split (and JS floor for passthrough
  collapse). A split is accepted when its improvement δ exceeds this.
- ↑ → FEWER splits accepted (only strongly-separated ones) → coarser, shallower DAG.
  ↓ → more splits accepted → finer, deeper DAG, but risks over-splitting on weak
  separations.
- Structure: gates the entire split cascade. Lower = more aggressive subdivision.
- Results: interacts with minClusterSize (both control granularity from different
  angles: minClusterSize by count, separationEpsilon by separation quality).
- Calibration: 0.01 is permissive (accepts fine separations at d=256). Raise if you
  see over-fragmentation / low-purity micro-leaves.

### enableResidualSplitGate / enableResidualRouting (default true)
- Controls: whether low-confidence queries are pooled as "residual" rather than
  force-assigned, and whether residual routing feeds split decisions.
- Off → every query force-routed (higher coverage, noisier leaves). On → ambiguous
  queries pooled (cleaner leaves, higher NoMatchRate).
- Results: On raises NoMatchRate (~12% observed) but keeps leaves clean.
- Calibration: keep ON (clean leaves matter for judge quality); the NoMatch is honest.

═══════════════════════════════════════════════════════════════════════════════
## GROUP D — BRIDGING / MERGING (polyhierarchy, cross-links)
═══════════════════════════════════════════════════════════════════════════════

### fusionSimilarityThreshold (default 0.92; canonical 0.90)
- Controls: cosine threshold to fuse two nodes into a multi-parent bridge.
- ↑ → FEWER bridges (only near-identical nodes fuse) → more tree-like. ↓ → MORE
  bridges (looser fusion) → more polyhierarchy, but risk over-merging.
- Structure: THE bridge-formation dial. Validated: 0.90 preserves coherence (WLP even
  ↑) while forming SourceA (same-anchor) refinement bridges. Cross-anchor bridges are
  geometry-limited (SourceB=0) at any threshold that preserves coherence.
- Results: ↑ BridgeRatio, more cross-domain structure — but below ~0.85 same-anchor
  over-merging degrades purity.
- Calibration: 0.90 validated. Do NOT go below ~0.88 without checking purity/silhouette
  hold. Consider sweeping {0.88, 0.90, 0.92}.

### secondaryMassFloor [SWEPT] (default 5.0; canonical 2.0)
- Controls: minimum secondary probability mass for a secondary/bridge-candidate
  assignment to count.
- ↑ → stricter (fewer secondary/bridge assignments). ↓ → more permissive.
- Structure: gates secondary structure formation. 2.0 (canonical) is permissive.
- Calibration: SWEPT factor; tune for bridge count / secondary richness.

### bridgeSupportRelFraction [SWEPT] (default 0.10)
- Controls: relative support a bridge must carry vs its parent to be admitted.
- ↑ → only well-supported bridges admitted (fewer, stronger). ↓ → more, weaker bridges.
- Structure: bridge admission strength gate.
- Calibration: SWEPT factor. Balance bridge count against bridge quality (avoid
  Coverage=0 degenerate bridges).

### effectiveSupportFloor (default 2.0)
- Controls: minimum effective (soft) support for a node to be retained.
- ↑ → prunes more low-support nodes (cleaner, fewer nodes). ↓ → keeps marginal nodes.
- Calibration: 2.0 guards against near-empty nodes. Rarely needs tuning.

### enableBridging (default true; DAG_MAX sets it)
- Controls: master switch for polyhierarchy. Off → strict tree.
- Calibration: ON for the thesis (the polyhierarchy IS the contribution). dagMode
  DAG_MAX enforces it.

═══════════════════════════════════════════════════════════════════════════════
## GROUP E — vMF FITTING / STABILIZATION (cluster parameter estimation)
═══════════════════════════════════════════════════════════════════════════════

### emaAlpha (default 0.7)
- Controls: EMA smoothing of κ across iterations.
- ↑ → more weight on new estimate (faster adaptation, less stable). ↓ → smoother,
  slower-moving κ.
- Results: affects convergence stability. 0.7 balances adaptation vs stability.
- Calibration: rarely tuned; 0.7 is a safe default. Lower if κ oscillates across iters.

### defaultKappaPrior (default 10.0)
- Controls: NiW prior concentration when a node has too few points for stable MLE.
- ↑ → stronger prior pull toward a default concentration in the tiny-N regime. ↓ →
  weaker prior (more data-driven even at small N).
- Calibration: only matters for small leaves; 10.0 is a weak, safe prior.

### refitMuPerIteration (default true)
- Controls: whether cluster means are refit each iteration.
- On → means track the evolving membership (more accurate, more compute). Off → frozen
  after initial fit.
- Calibration: ON for accuracy; it is part of why convergence works. Leave on.

═══════════════════════════════════════════════════════════════════════════════
## GROUP F — DEFENSIBILITY / ABLATION FLAGS
═══════════════════════════════════════════════════════════════════════════════

### enableGtWarmStart [NEW, now TOML-parseable] (default true)
- Controls: the depth-1 ground-truth (editorial-label) warm-start bias in iter≤1
  (the +ln(1/0.7) toward the editorial-anchor child).
- On → construction warm-started toward MMLU-Pro labels in iteration 1. Off → PURELY
  geometry-driven from the start.
- **This is the key defensibility ablation.** Off strengthens the RQ2 "geometry not
  labels" claim IF quality holds. Now that it is a TOML flag, run the ablation:
  build with true vs false, same seed, compare NMI/DendrogramPurity/WLP/Top-1.
  - Quality holds → set FALSE, report as strengthening RQ2.
  - Quality drops → keep TRUE, disclose as iter-1 initialization.
- Calibration: settle this BEFORE the sweep (it changes the pipeline). Highest
  defensibility value of any single flag.

═══════════════════════════════════════════════════════════════════════════════
## GROUP G — JUDGE / ARENA SCOPE (evaluation, not construction)
═══════════════════════════════════════════════════════════════════════════════

### maxJudgeGenerality (default 1)
- Controls: which nodes get judges: 0 = leaves only, 1 = leaves + parents, etc.
- ↑ → judges induced at higher levels too (broader domain judges, more judge-gen
  cost). ↓ → only leaf judges.
- Calibration: 1 gives leaf + parent judges. Higher = more coverage, more induction
  cost. Tune vs judge-generation budget.

### llmParallelism (default 8)
- Controls: concurrent LLM calls. Pure throughput/rate-limit knob. No structure/result
  effect. Set to your provider's rate limit.

═══════════════════════════════════════════════════════════════════════════════
## CALIBRATION STRATEGY (how to use this guide)
═══════════════════════════════════════════════════════════════════════════════

**Tier 1 — settle BEFORE any sweep (change the pipeline):**
- enableGtWarmStart (ablation — decide on/off from data)
- fusionSimilarityThreshold (0.90 validated)
- The construction/arena margin split (constructionMargin tight, arenaMargin loose)
These change DAG output; lock them before tuning.

**Tier 2 — the L9 sweep factors (the real calibration):**
- constructionMargin (structural breadth — dominant post-rework)
- minClusterSize (granularity)
- secondaryMassFloor + bridgeSupportRelFraction (bridge controls)
These are the 4 to sweep. They span the independent axes: breadth, granularity,
bridging-mass, bridging-support.

**Tier 3 — hold fixed unless a target is missed:**
- maxDepth (8), maxLeafAssignments (5), emaAlpha (0.7), defaultKappaPrior (10),
  effectiveSupportFloor (2.0), separationEpsilon (0.01), routingSoftmaxTau (1.5).
Only sweep one of these if the Tier-2 sweep can't hit a target metric.

**Tier 4 — arena-only, tune AFTER the canonical DAG is locked (no structure effect):**
- arenaMargin (membership breadth for judge enrichment)
- maxJudgeGenerality (judge coverage)
- tauKappaScalingFactor (γ ablation for geometry-adaptation study)

**The independent axes to keep distinct when sweeping** (avoid confounding):
- GRANULARITY: minClusterSize, separationEpsilon
- BREADTH/SOFTNESS: constructionMargin, routingSoftmaxTau, assignmentCosineGap
- BRIDGING: fusionSimilarityThreshold, secondaryMassFloor, bridgeSupportRelFraction
- EVAL: arenaMargin, maxJudgeGenerality
Sweep at most one or two axes at a time; a factor from each axis in one L9 keeps them
separable (which the current 4-factor design roughly does).

**Metric → knob quick map (which parameter to move to fix a metric):**
- Leaf count wrong → minClusterSize
- BorderlineRate/ECE off → constructionMargin (or routingSoftmaxTau)
- Top-1 low → assignmentCosineGap, minClusterSize
- Too few / too many bridges → fusionSimilarityThreshold, bridgeSupportRelFraction
- SmallLeafFraction high → minClusterSize ↑, effectiveSupportFloor ↑
- Judges weak (sparse corpus) → arenaMargin ↑ (enrich), minClusterSize ↑
- Cross-domain migration → assignmentCosineGap
