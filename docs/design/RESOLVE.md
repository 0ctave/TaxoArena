# RESOLVE
### A standing capability service that publishes its own resolution

*Design document, v1. Every number below is from the campaign; where I computed something new from the repo I say so and give the query's result.*

---

## 1. The one-paragraph answer

RESOLVE is a streaming evaluation service whose deliverable is a **coverage-and-resolution matrix over (model × anchor), not a leaderboard**: each cell carries a Bradley–Terry strength, a question-clustered interval widened by a *measured* systematic-error budget, and a publication class that says what that cell can support — an order, a band, a router weight, or nothing. Queries arrive continuously and are routed by a federated per-source tree whose **leaf centroids learn online, whose splits commit only at epoch boundaries, and whose anchors change only by registration**, because leaf identity is a sample draw and the loop has never once birthed an anchor. Judging is split by *product* rather than by topic: a cheap pointwise **grade pass** feeds the ranking and supplies two free contestedness signals, and a pairwise **edge pass** with dual order and the replicate tie-break is spent only on edges that a certificate says are within reach. The reference is bought once per question at ingest and never again, which turns the campaign's strongest lever into amortised capital and makes per-cell reference accuracy a free diagnostic rather than a bandit's arm. The system's headline output is a **tier map with a resolution of roughly 0.5 logits**, which is what the measured per-cell standard errors (0.14–0.29, median 0.20 on the deployed board) actually buy, and its second output is the explicit list of comparisons it declines to make.

---

## 2. What the evidence forces

### 2.1 The reporting cell is the anchor, and its resolution is a tier, not a rank

M1 settles the granularity: anchor +0.0062 [+0.0041,+0.0084] over global on next-verdict log-loss, leaf −0.0251, hierarchical κ=30 −0.0078 (κ=200 a post-hoc tie). LEAF-POWER never crosses below V=400 under either judge; LEAF-SHRINK puts λ=0 best in 5/5.

What has not been written down is *how thin the anchor cell already is*. I recomputed it on the deployed board (`experiment_results/x12_crossdomain/ratings_x12.db`, 9,144 matches, all 9,144 mapped to a domain through `eval_question_link → mmlu_pro.category`):

| | distinct questions |
|---|---|
| per anchor | 105 (CS) … 326 (Math), median 185 |
| per **(anchor, model)** cell, 168 cells | **min 25, median 74, max 194** |
| cells reaching 120 / 133 | **24 / 168 · 20 / 168** |

Under `SE ≈ sqrt(k/q)` with k=3 that is a cell SE of 0.142 at Math, 0.201 at the median, 0.289 at Computer science — which reproduces R2's honest query-level band of 0.141–0.245 almost exactly, so the law is validated on the campaign's own scheduler rather than assumed. **The anchor cell is already at the edge of estimability; there is no room below it and only Math has room inside it.** A per-anchor *ranking* needs edges of ~0.5 logits before two cells separate. A per-anchor *tier map* is what 0.20 buys.

This also kills the argument about the constant in `q ≥ k/S²`. Two documents in the repo disagree (blog/03 and the H6b row put the design effect *inside* k at 120–190; P5 and the validation plan multiply it again to 240–380), and a design that picks a point in that 5× span is choosing its own answer. **RESOLVE never uses a q-threshold as an admission gate.** `q ≥ k/S²` is the *planning* heuristic the allocator uses to forecast; admission is decided by the measured question-clustered SE, with k estimated per cell and published. The constant stops being a matter of opinion the moment you measure it per cell.

### 2.2 The roster divides the question supply — the support law, derived

None of the proposals noticed that q is not a property of the corpus. Each match yields two model-question observations, so for M models in a cell holding Q distinct questions and V matches, the achievable per-model support is

```
q ≈ 1.4 · V / M          (bounded above by Q),      reuse r = V / Q
⇒  q ≈ 1.4 · r · Q / M
```

The 1.4 is the measured allocation efficiency of the deployed scheduler, and it is tight: Math, V=1,279, M=12 predicts q=149 against an observed cell median of **149**; Physics predicts 131 against 128; Chemistry 89 against 100. At M=12 and a reuse of 3 (above which the design effect starts eating the gain it bought), **q ≈ 0.35·Q**. To reach q=133 in a cell you need ~380 reserved questions in it. In the pool of record exactly one anchor has that (Math, 393). On the six-corpus union, 15 of 52 strata clear 133 *reserved questions at all*, 8 clear 240 — and that is before the roster of 18 divides them. The atlas is therefore tier-resolution by arithmetic, not by timidity, and any design that publishes a per-cell order is publishing noise.

### 2.3 Format follows the product, not the topic

POINTWISE and HYBRID between them dispose of the per-anchor format table that four of the five proposals shipped. Pairwise wins the *pair* (0.864 vs 0.808, and the hybrid at τ=30 reaches 0.883). Pointwise wins the *board* (ρ 0.9930 vs 0.9790, 0 top-4 violations vs 1) at 1.86 calls/match against 2.00, and HYBRID's conclusion is unambiguous: pure pairwise is dominated on all three axes. POINTWISE-REPL's topic axis does not replicate at n=64–274, and RUBRIC-HIDDEN prices resolving 1pp per anchor at ~3,900 matches, so a per-cell format table cannot be bought at 52 cells or even at 14.

So: **grades rank, comparisons decide.** The ranking layer is pointwise (no order, no tie-break — those are pairwise constructs and the incoherence in four proposals came from pretending otherwise). The edge layer, which publishes a claim about two named models, is pairwise, dual order, replicate tie-break. This also gives the grade pass a second job for free: the grade gap is a key-free contestedness meter (36.1% of pairs carry exactly equal grades, and those *are* the frontier pairs).

### 2.4 The reference is capital, not a decision

3,432 of 3,445 pool questions already carry a cached reasoning solve, so runs on the pool of record pay zero reference calls. That is the correct shape: **buy the reference once, at ingest, for every question that lands eval-side**, and never make a reference decision at schedule time again. It follows that:

- The reference broker/bandit is dead. REF-BY-CELL is decisive — per-cell reference *selection* gains +0.0000 (grok-reasoning wins all 13 anchors) — and ENSEMBLE-REF showed the ceiling does not move with more voters. But the same probe hands you the thing that matters: grok's own accuracy spans **0.727 (History) to 0.952 (Math)**, and since the judge transcribes the reference, that spread is the dominant term in per-cell judge quality. Track it; never select on it.
- Where a checker exists, pass its **output**, never its specification (0.935 with 5.5% ties vs 0.658 with 25.6%). Checker coverage is the only lever in the programme that raises the ceiling rather than moving along it.
- The displacement asymmetry is respected by construction: the format that displaces (pointwise ΔKEY −0.560) is used only for the aggregate, where errors are unbiased across models and average out; the format that merely outweighs (pairwise ΔKEY −0.022) is used for every individual claim.

### 2.5 A bootstrap CI is a licence to be confidently wrong

TIER-HONEST is the most consequential unexploited result in the ledger. The arena separates 62 of 64 across-tier pairs with **0 wrong directions** — and separates **2 of 2 within-tier pairs at 95% confidence**, including arx/iask, where it is certain and the key says the opposite; its own self-tiering carries 2 cross-tier key inversions. The diagnosis in the row is exactly right: *resampling sees sampling noise, never a bias present in every sample.*

So every published edge is gated by a **separation certificate**: the question-clustered gap CI widened by a systematic budget assembled from the three terms the campaign has already measured — the intrinsic test–retest floor (0.057, and TEMP-0 proved it is not a sampling default), the cell's reference accuracy (0.727–0.952), and the answer-agreement composition of the backing matches (flip 0.105 disagreeing vs 0.192 agreeing; the flip rate *is* an absence-of-decisive-evidence meter). The inflation is calibrated, at zero calls, on the existing 9,144-match board against one target: **zero confident wrong separations and zero inversions inside the system's own tiers.** That is a weaker demand than reproducing the key's partition — which TIER-RECOVERY showed is unreachable at 0% of draws at every budget and coarseness — and it is exactly the demand a cost-aware router places.

### 2.6 Structure arrives by registration; leaves route, anchors report

H9-1: anchors and routing invariant across seeds (Top-1 spread 1.6pp, anchor drift ≤0.42pp) while leaves span 72–87 at ARI 0.66–0.69, and P1 falsified consensus as a fix. D4: a withheld domain is routed correctly and absorbed — twelve Law-dominated regions, eleven at 90–100% purity, carrying 89% of held-out Law, *no* certified site, *no* anchor born, the loop never splits the root; D4-ROOT is designed and unrun. ADAPT: in-loop gating at p95 loses q=0.000 structure (35 leaves/0.742 against the promoted 84–88) — certify by pruning, not gating. ANCHOR-VALUE and MC-ROOT: flat nearest-leaf routing beats anchor descent (0.764 vs 0.753 on the corpus whose own categories *are* the anchors; 81.58% vs 72.08% on the union), so the anchor layer is a reporting convenience, not a routing mechanism.

Therefore: leaves are the **routing address space** and may churn freely; anchors are the **reporting address space** and nothing that persists is ever keyed on a leaf id. And an arriving domain must never inherit a host anchor's name — that produces a silently *mislabelled* profile, which is worse than a coarse one.

### 2.7 Budget never fixes the top; only the ceiling does

M2's `top4viol_md` column: median 3.0 at *every* budget from 250 to 36,871 matches across 24 consecutive Mistral rows, ρ flat at 0.951 from 500. ORACLE: a perfect reference plus order balancing plus tie resolution takes 0.612 → 0.857 and the order still does not come out (p=0.41), with judge-irreducible error 0.223 *larger* than reference-induced 0.165. The allocator is therefore forbidden from spending marginal budget on frontier matches, and spends it instead on checker/reference coverage and on new distinct questions.

### 2.8 The split must be a pure function with no mutable flag anywhere

The POOL-ASSERTION audit named the mechanism precisely: class (a), addressed by explicit pool id, *cannot* drift because the id is the content hash of the set; class (b), `eval_results.is_reserved`, is the drift vector because it mirrors whichever pool is active; class (c), scripts re-deriving their own split, was the second incident. Both incidents happened with a written rule in force. RESOLVE has no class (b) and structurally cannot have class (c) — §6.

**Ruled out by the above, and not re-litigated anywhere in this document:** leaf-level profiles; any partial pooling toward a parent; per-anchor format tables; reference brokers, ensembles, and any per-query reference decision; per-query judge adaptivity as a class; confidence gating and abstention thresholds; rubric text as a lever; single-order economies; online anchor birth; in-loop certification gating; publishing an order at the frontier at any budget.

---

## 3. The architecture

```
                         ARRIVALS  (one query stream, all sources)
                                   │
                    ┌──────────────▼──────────────────────────────────┐
                    │ A. INGEST & PIN                                 │
                    │  content key = sha256(norm stem ‖ sorted norm   │
                    │                option set ‖ contract id)        │
                    │  near-dup: MinHash band → cluster key = min(ck) │
                    │  side = uint64(cluster key) mod 1000 < 300      │
                    │      → EVAL, else TRAIN.  Pure function.        │
                    │  EVAL ⇒ buy reference ONCE (checker output if   │
                    │         a verifier exists, else 1 reasoning     │
                    │         solve); cache keyed by content key      │
                    └────────┬──────────────────────┬─────────────────┘
                      TRAIN  │                      │ EVAL
             ┌───────────────▼──────────┐    ┌──────▼─────────────────────────┐
             │ B. ROUTER                │    │ C. CELL LEDGER (verdict-level) │
             │  federated per-source    │    │  every row stamps:             │
             │  trees; flatLeaf over    │───▶│  epoch · router_ver · recipe   │
             │  the union's leaves      │    │  hash · cell · content key ·   │
             │  centroids  : online     │    │  pair · ORDER · outcome ·      │
             │  splits     : epoch only │    │  grade · filter flag           │
             │  anchors    : registered │    │  (pair counts are a VIEW)      │
             │  FOREIGN gate on purity  │    └──────┬─────────────────────────┘
             └──────────────────────────┘           │
        ┌─────────────────────────────────────┬─────┴───────────────────────┐
        │ D. JUDGE ASSEMBLY                   │ E. BOARD                    │
        │  GRADE PASS  pointwise, 1 call per  │  streaming BT: global θ +   │
        │    (question, model), no order,     │  UNPOOLED anchor δ          │
        │    reference/checker in prompt      │  question-clustered boot →  │
        │  EDGE PASS   pairwise, dual order,  │  statistical CI             │
        │    replicate tie-break on ties,     │  + systematic budget B_cell │
        │    scheduled only on answer-        │  ⇒ SEPARATION CERTIFICATE   │
        │    disagreeing, close-grade pairs   │                             │
        └─────────────────────────────────────┴─────┬───────────────────────┘
                                                    │
                  ┌─────────────────────────────────▼──────────────────────┐
                  │ F. ATLAS   (model × anchor) tier map + coverage matrix │
                  │   class ∈ ORDERED / BANDED / PREDICTIVE-ONLY /         │
                  │           UNSUPPORTED / FOREIGN                        │
                  └────────────────────────────────────────────────────────┘
   G. ALLOCATOR  one currency (cheap-call equivalents), spend order fixed by §7
   H. AUDIT      300-match canary · key-decidable slice · certificate calibration
```

### A. Ingest & Pin

The content key is the **options key**, never the raw text: `question_text` is polluted on 8.4% of one model's rows and text joins map roughly half of train questions wrongly (HARNESS 5), which is why the standing repo rule is to cross id spaces by the options key. For generative items with no option set the key is `norm(stem) ‖ verifier id`.

Near-duplicates are the hole every proposal left open, and BBH is the proof: 24 template sub-tasks, 100% within-corpus Top-1, "trivially routable". A MinHash band over the same normalised token stream assigns each item a **cluster key = the minimum content key in its cluster**, and the side function is applied to the *cluster* key. A paraphrase, a re-template, and a cross-corpus reappearance therefore land on the same side by construction, and a template family cannot straddle the split.

Eval-side admission buys the reference immediately: checker output where a verifier exists, one reasoning solve otherwise. This is the only reasoning spend in the system and it is paid once per question forever.

### B. Router

Federated per-source trees (MC-FED: 13 certified sites against 5 for one loop), union routing by flatLeaf (+9.50pp, McNemar p=1.8e-82) with the per-source costs reported beside the headline, not buried — GPQA 88.0→77.7, MATH 65.6→60.8. 512-dim slice because that is the promoted recipe; certification is *reported*, never gating (ADAPT), so the D3 1024-vs-512 argument is moot — RESOLVE does not use certification as an admission criterion anywhere, and says so.

Three timescales:
- **Centroids** update continuously (Welford on the unit sphere) from **train-side arrivals only**.
- **Splits** are proposed continuously and committed only at an epoch boundary, on the production z-gate at ≥2× minClusterSize support, then pruned against each node's own anisotropy-preserving null (band 0.026–0.063; median q 0.965 in the reach ≥90% subset) with the result *published as a certificate*, not enforced as a gate.
- **Anchors** change only when a human registers a source or domain. An anchor proposal is emitted with D4's warning attached — ~1,300 questions or it certifies nothing at minClusterSize 55 — and nothing else.

**The FOREIGN gate**, which is the fix for D4 and is testable at zero calls on the D4 artifacts: for each leaf, compute the share of its recent arrivals whose declared (source, domain) matches the leaf's modal train-side (source, domain). Below 0.60, the leaf's arrivals are routed to `FOREIGN/<leaf-content-hash>`, profiled in their own cell, and **never attributed to the host anchor**. D4's Law hosts — 90–100% Law under a Philosophy anchor — trip this on the first window.

**Router versioning of the ledger.** Every verdict stamps `router_ver`. At an epoch boundary the frozen 3,445-question probe is re-routed under old and new; per-anchor assignment agreement ≥95% (H9-1's ≤0.42pp anchor drift is what a stable rebuild looks like) permits pooling across versions. Below it, the cell opens a new epoch and the old estimate survives only as a prior. This closes the drift channel that no pool-id check can see.

### C. Cell Ledger

Verdict-level rows are the state; pair counts are a derived view. This is not negotiable: a question-clustered bootstrap cannot be computed from pair aggregates, and match-level SEs understate by 2.0× median, 3.7× worst. Per-**order** win counts are mandatory on every path including resume (R2 lost them on 9,235 rows), and no post-hoc position adjustment ever touches the fit. Canary verdicts (§H) live in a separate store and are structurally excluded from the ledger.

### D. Judge Assembly

Recipe frozen: cheap judge (grok-4-1-fast-non-reasoning — judge identity is a wash at p=1.0 for a tenth the price), reasoning reference or checker output, v2 verify-first mechanics, dual order on the edge pass. The anchor rubric is retained only as a zero-marginal-cost carry-over and labelled +1.5pp n.s.; it is inside the ±3pp floor and nothing downstream depends on it.

**Grade pass:** one pointwise call per (question, model), amortised over every future comparison that touches that question. Unit of spend is a *cell entry*, not a pair — which is why the allocator can target under-supported cells precisely.

**Edge pass:** scheduled only where (i) the two models' own extracted answers differ — free, key-free, judge-free, keeps 99.8–100% of decidable pairs at 16.9% of frontier question-pairs — and (ii) the grade gap is below τ. Dual order always; SELECTIVE-ORDER closed that question and the corrected statement is in the ledger. Ties get the replicate tie-break, priced honestly as **+2.2pp decisive-and-correct at board scale against a registered +3pp bar (FAIL) with correct-given-committed falling 0.918→0.903** — it buys decisiveness, so it is fired only where tie mass is what blocks a certificate.

### E. Board

Streaming BT with Jeffreys phantom ties added only to pairs carrying at least one real comparison. Two levels, **unpooled**: global θ plus anchor deviation δ. No shrinkage — M1 falsified it at κ=30 and κ=200 is a tie, so pooling buys nothing and costs a parameter nobody can estimate. A cell whose comparison graph is disconnected is refused, not imputed.

Intervals: 2,000-resample question-clustered bootstrap for the statistical part; systematic budget `B_cell = sqrt(b_retest² + b_ref² + b_comp²)` added in quadrature, with the three terms calibrated as in §2.5. Filtered and unfiltered edges carry a per-edge flag and are never mixed in one fit without an explicit scale term — PLACEBO-ENTRY measured filtering widening the θ scale by 13%.

### F. Atlas

The published object. Per (model, anchor): θ, statistical SE, systematic budget, q, V, reuse r, measured k, routing precision for the cell, reference accuracy for the cell, and a **publication class**:

| class | condition | what may be said |
|---|---|---|
| ORDERED | certificate separates this model from its neighbour | "A above B in this cell" |
| BANDED | certificate does not separate, cell otherwise supported | "A and B are not distinguished here" |
| PREDICTIVE-ONLY | q below the planning floor but the cell improves next-verdict log-loss over global | usable as a router weight; **not quotable as a claim** |
| UNSUPPORTED | neither | printed with the price of the next level |
| FOREIGN | purity gate tripped | profiled separately, never attributed |

PREDICTIVE-ONLY is the class the five proposals were missing, and it is what makes the atlas non-empty. M1 shows the anchor profile earns its keep *at the observed support* — the support rule governs whether you may publish a cell's number, not whether the cell helps a router. Two questions, two answers, printed separately.

---

## 4. The four requested outputs

### (1) Granular capability profile

**Granularity: the anchor** — 14 on MMLU-Pro, 52 designed strata on the six-corpus union. **Resolution: a tier, ~0.5 logits.** Per-cell θ standard errors on the deployed board are 0.142 (Math), 0.201 (median), 0.289 (Computer science), which reproduces R2's honest query-level 0.141–0.245; a two-cell comparison therefore needs roughly 0.5–0.6 logits before the certificate fires, which is about 8–10 points of key accuracy — one tier step.

Coverage, published first and not buried: on MMLU-Pro, 24 of 168 (anchor × model) cells hold ≥120 distinct questions, 20 hold ≥133. On the union, 15 of 52 strata hold ≥133 *reserved questions* before the roster of 18 divides them; BBH's 24 sub-task strata hold 44–75 each and are pooled to source on arrival. So the honest MMLU-Pro atlas is roughly **5–7 ORDERED-capable anchors, the rest BANDED or PREDICTIVE-ONLY**, and the honest union atlas is **the 14 MMLU-Pro anchors plus 6 source-level rows**, with GPQA/MATH/MuSR/IFEval carried as single uncertified anchors.

Sub-anchor rows are refused, and there is a precondition before that is ever revisited: `leaf_profile_evidence.py` calls `ff.keyed_questions()` with no reserved-side filter, so LEAF-PROFILE arm A — the one result that says per-leaf capability is real — is evaluated on questions that largely built the leaves. **Re-run it restricted to the tree's own reserved pool (zero calls) before any sub-anchor row is admissible.** If it does not replicate, the anchor is the hard ceiling permanently.

### (2) Online domain tree

**Learns:** leaf centroids, continuously, from train-side arrivals. **Commits:** splits, at epoch boundaries, on the production z-gate with pruning-based certification reported. **Does not learn:** anchors. Routing accuracy, published per family rather than as a mixture: union Top-1 **81.58%**, source **95.46%**, source+domain **81.12%**; MMLU-Pro alone **74.1%** (the only non-trivial family — BBH's 100% is 24 templates and should never be averaged in). That means roughly **19% of metadata-free arrivals are filed under the wrong (source, domain)**, and the resulting attenuation of cell contrasts is an *unmeasured* bias term, declared as such beside every routed-only cell. Where corpus metadata exists the profile keys on the designed anchor and routing is used only for arrivals without it — the +0.71pp clean metadata cost is sign-unstable across seeds (−0.46/+1.22/+1.36) and MC-E2E's stability criterion failed, so nothing in the design leans on inferred cells being free.

### (3) Judge selection

Selection is over **two products and three reference states**, and nothing else — no per-query adaptivity, no bandit, no per-cell format table.

| | ranking product | edge product |
|---|---|---|
| format | pointwise grade, 1 call per (q, model) | pairwise, dual order |
| aggregation | BT over grade-derived pair outcomes | majority of two, replicate tie-break on ties |
| cost | 1.86 calls/match at r=2.68 | 2.00 + ~0.32 calls/match |
| accuracy | board ρ 0.9930, 0 top-4 violations | 0.864 per pair; 0.883 in the hybrid regime |

Reference state per question, decided at ingest, never at schedule time: **checker output** (0.935, ties 5.5%) > **cached reasoning solve** (0.864) > **none** (0.738, ties 0.177). Cells whose questions are predominantly reference-free are fitted as a separate component and are never placed on the same board — pooling 0.864-quality and 0.738-quality verdicts with a 2.5× tie-rate difference biases exactly the cross-cell contrast the atlas exists to publish, and a flag in a column does not remove a bias from a fit.

### (4) Online ranking

Streaming BT, global + unpooled anchor deviation, updated per verdict, refit for intervals every 500. **Published resolution:** an edge is ORDERED only if its gap survives the separation certificate. The calibration target is TIER-HONEST's: zero confident wrong separations, zero key inversions inside the system's own tiers — measured on the key-decidable slice, and the inflation constant is republished with every calibration.

**Newcomer placement** is quoted from M3's NOISY row, which is the deployed condition, not the oracle row four proposals quoted: at 400 matches per newcomer, "within ±1 rank" is 78% / 78% / 48% / **36%** at rosters 16/24/32/46, median rank error 2.0 (p75 3.0) at 46. So a newcomer costs ~400 dual-order filtered matches (~930 calls) and is reported as **a tier assignment with a ±3-rank interval at large roster**, never as a rank. Placement into the top tier is refused outright.

---

## 5. What it refuses to do

This is the product, not the disclaimer.

1. **It will not order the frontier.** ORACLE gave the judge the answer key: 0.612 → 0.777 (+16.4pp, p=5.4e-11) and arx/iask still does not come out (p=0.41); with order balancing and tie resolution stacked, 0.857 and still p=0.29. M2's median top-4 violation count is 3.0 at every budget from 250 to 36,871 across 24 configurations. The system prints `NOT RESOLVED` with the gap, the certificate's two components, and the statement that no budget in the measured range changes it.

2. **It will not publish a leaf-level number.** Not as a profile row, not as a shrunk row, not as a router cell that gets quoted. Leaf ids address scheduling strata and rubric context and nothing that persists.

3. **It will not report a cell whose interval it cannot honestly widen.** A cell with no key-decidable audit mass has no measurable `b_ref` and is published as PREDICTIVE-ONLY regardless of how many verdicts it has.

4. **It will not claim the answer-disagreement filter saves money in a refilling scheduler.** The 58% figure (18,284 → 10,552 calls) is a retrospective replay from a finished cache; the shipped Kotlin scheduler measures run-wide matches falling **42,300 → 38,910**, because most pairs across 12 models already disagree and unresolved pairs spend their budget either way. The filter's product is better matches, and a ~8% run-wide reduction. The 16.9% holds on the frontier sub-schedule where it was measured.

5. **It will not quote the tie-break as an accuracy gain.** +2.2pp decisive-and-correct at board scale, registered FAIL against its own +3pp bar, correct-given-committed falling 0.918 → 0.903. Every accuracy number in the system carries both conventions, and the tie convention is registered together with any bar.

6. **It will not attribute an unregistered domain to a host anchor.** FOREIGN cells are unnamed, profiled separately, and blocked from the atlas until a human registers them.

7. **It will not treat verification fidelity as preference fidelity.** Every number is agreement with a key or a checker. There is no human annotation anywhere in the evidence base and the atlas header says so.

`NOT RESOLVED` is a first-class row: it carries the gap, the statistical half-width, the systematic budget, the binding term (support / reference / judge-irreducible), and the price of the next level — the questions *and* the verdicts short, since both bind.

---

## 6. The contamination discipline

The rule failed twice — 71% of judged questions on the tree's train side in the main line, ~70% overlap at chance in the multi-corpus line six weeks later, with a written rule in force both times. The audit's class analysis says why: **(a)** addressing by explicit pool id cannot drift because the id is a content hash; **(b)** `eval_results.is_reserved` mirrors whichever pool is active and is the drift vector; **(c)** two scripts re-derived their own split with `random.Random(seed)`.

RESOLVE removes class (b) and makes class (c) inert:

1. **No mutable side flag exists.** There is no `is_reserved` column, no active-pool pointer, no split file. `side(item) = uint64(cluster_key) mod 1000 < 300`, a pure function of content. A script that re-derives the split gets the identical answer, which is the point: the failure mode in class (c) was *disagreement*, and a pure function cannot disagree with itself.

2. **The split's identity is the FUNCTION, not the SET.** This is where every proposal that hashed the eval set broke in a stream: a growing set's hash changes on every arrival, so either every artifact goes stale or you introduce an epoch pointer, which is the mutable process-global object that caused the first incident. Artifacts stamp `(normaliser version, key-derivation rule, side modulus, epoch cutoff timestamp)`. That tuple is write-once and content-addressed. Membership is asserted **per row** at write time — `assert side(row.cluster_key) == EVAL` — not as set equality at run start.

3. **Assertion is a save-time invariant in both languages**, on every writer, with mismatch FATAL, and pinned by a test on the source text of the predicate, in the style of the shipped `MatchFilterInputsTest`. The scheduler and judge processes additionally read a projection with `gt_answer`/`is_correct` physically absent — structural absence beats a reviewed invariant, though it is a second line and not the first: incident 2 was a *scoring* error on train-side items, which no key barrier would have caught. The per-row side assertion would have.

4. **The near-duplicate cluster key** (§3A) closes the paraphrase and template channels that a plain text or options hash leaves open, and it is the only defence against BBH's template families straddling the split.

5. **Two audits, both cheap.** (i) `|scored \ eval| == 0` on every scored run — the invariant, not a chance-overlap window that passes silently at 85% contamination. (ii) A quarterly re-derivation of every artifact's side from its stamped function tuple, which detects a normaliser change as a version mismatch rather than as silently re-split data.

6. **Reference and card provenance is stamped with the side the item held when the artifact was minted.** A cached reference solve is model-generated content about a held-out question; if any future consumer reads the cache for anything other than judging, the stamp is what makes that auditable.

7. **Nothing selects on the eval side.** Tree commits are gated on a third GATE partition carved from the train side, never on held-out routing accuracy — an epoch-boundary regression gate that reads the eval side is repeated model selection on held-out data forever, and no pool-id check can see it.

---

## 7. Cost model

One currency: **cheap-call equivalents (cce)**. A reasoning reference solve is priced at 10 cce (JUDGE-SWAP's order-of-magnitude, applied honestly rather than counting "calls"). A cycle is an increment; the atlas is cumulative.

**Standing cycle, six-corpus union, 18 models:**

| line | volume | cce | notes |
|---|---|---|---|
| Ingest references | 900 new eval-side questions × 1 reasoning solve | 9,000 | capital; never repaid. Checker output where a verifier exists costs ~0 |
| Grade pass | 6,000 pointwise grades | 6,000 | targeted at under-supported (cell, model) entries |
| Edge pass | 4,300 matches × 2.00 | 8,600 | answer-disagreement + close-grade filtered |
| Tie-breaks | ~690 ties × 2 | 1,380 | only on edges within reach of a certificate |
| Canary | 300 frozen matches × 2 orders × 2 replicates | 1,200 | separate store; MDE ~2.7pp at n=300, ~1.5pp pooled over 3 cycles |
| Slack / retries | — | 1,800 | |
| **Total** | | **~28,000 cce** | ≈ 20,000 cheap calls + 900 reasoning |

The ingest line is a third of the cycle and it is the line that must not be cut: it is the only spend that raises the ceiling rather than moving along it.

**Marginal value of the next call, in one currency:**

1. **A checker on a question that has none.** 0.658 → 0.935 in the cleanest comparison available, at ~0 marginal cost per question thereafter. Nothing else in the programme is close.
2. **A reasoning reference on an uncovered eval-side question.** +12.6pp pairwise — of which 74% is abstaining less, so priced as +3.2pp of discrimination — for 10 cce paid once and amortised over unbounded future reuse. At r=3 that is ~3.3 cce/match on first use and falls toward zero.
3. **A new distinct question in an UNSUPPORTED cell.** Moves SE as `sqrt(k/q)`: at the median cell (q=74, SE 0.201), ten questions buy 0.201 → 0.188. Cost 10 cce (reference) + M grades.
4. **A tie-break on a tie that is blocking a certificate.** 2 cce for +2.2pp decisive-and-correct and −1.5pp committed — worth buying only when tie mass, not gap size, is what holds the edge below threshold.
5. **Another match on an already-supported pair at the frontier.** Measured at zero at every budget from 250 to 36,871. The allocator is hard-coded to refuse it.

The ordering is the design. Four of the five proposals inverted (2) and (4) by counting "calls" instead of price; the inversion reverses once reasoning solves are priced at 10× — and then flips back the moment you notice the reference is paid once per question rather than per match, which is the actual deployed accounting (3,432 of 3,445 cached, zero reference calls on the pool of record).

---

## 8. What would falsify it

**F1 — The certificate does not transfer.** The systematic-error budget is calibrated on MMLU-Pro's 66 pairs at zero calls, then frozen and applied out-of-sample to a corpus with a checker. Run GEN-ARENA's exact shape — MATH (1,800) + IFEval (1,200), 8 models, dual order, verifier reference — and read: confident wrong separations, and confident separations of pairs the checker ties. **Criterion: both zero.** Cost ~6,000 cce. If the inflation calibrated on one corpus does not deliver zero confident-wrong separations on another, the certificate is decoration and the tier map inherits TIER-HONEST's failure — the arx/iask pattern (certain, and backwards) reappearing under a new name. This is the experiment that decides whether RESOLVE has a product at all.

**F2 — Pointwise is not the ranking instrument.** The board advantage rests on one run at n=1,971 with Δρ CI [−0.028, +0.035] — a coin flip, and POINTWISE-REPL does not replicate at anchor scale. Judge 6,000 union matches in **both** formats (pairwise dual order 12,000 calls + ~11,000 grade calls ≈ 23,000 cce), registered readout: board ρ with CIs, top-4 violations, cost per match. **Criterion: pointwise's ρ ≥ pairwise's with violations no worse, at lower cost.** If pairwise wins, the grade pass loses its primary job, the close-grade contestedness signal has to be bought some other way, and the cycle cost rises by roughly a third.

**F3 — The design effect is endogenous and no cell is ever fundable.** The support law `q ≈ 1.4·r·Q/M` says the only way to raise q is to raise reuse, and reuse is what drives the design effect that sets k. Take Math (Q=393 reserved, the one cell with room), spend to q=250 for 6 models — V ≈ 1,070 matches ≈ 2,500 cce — and estimate k per cell from the clustered bootstrap at each of q ∈ {75, 150, 250}. **Criterion: k stable within ±25% as r rises from 3 to 6.** If k rises with reuse, then SE is bounded below by the schedule rather than by the corpus, no cell can ever be bought up to ORDERED, and the atlas is permanently tier-only — which is a finding, but it turns the allocator's entire "price of the next level" column into a lie and that column has to be deleted.

A fourth, free: re-run LEAF-PROFILE arm A restricted to the reserved side. Zero calls. If the pooled p=0.005 does not survive, the ANCHOR becomes the ceiling by measurement rather than by budget, and §5's refusal (2) hardens from "not purchasable" to "not there".

---

## 9. The honest gap

**No preference fidelity, anywhere.** Every number the system produces is agreement with an answer key or a checker. There is no human annotation, no inter-annotator agreement, no preference data in the entire evidence base, and nothing here speaks to open-ended generation. A capability profile for writing, reasoning style, or helpfulness is not a budget problem for this design — it is out of its measurement class entirely. What would change it: an annotation programme with its own reliability study, which is a different project with a different cost structure, not a parameter.

**The frontier stays unordered and always will under this instrument.** The judge's own irreducible error (0.223) is larger than the reference-induced half (0.165), so reference quality — the lever the whole programme sharpened — cannot close it. Judge identity is a wash (0.865 vs 0.864, p=1.0), the recipe is within 1.4pp of its own ceiling (STACK-v2 0.865 against J1-R 0.879), rubric text is null or negative in five tests, and the test–retest floor is intrinsic at temperature 0. What would change it: an exact verifier on the task, which is a property of the *task*, not of the budget — which is why the ingest line is the one the allocator protects. On free-form MATH a verifier reference reached 0.935 with 5.5% ties. On IFEval, where the "reference" lists constraints instead of checking them, 0.658. The distinction between a checker and a specification is the whole difference between a resolvable frontier and an unresolvable one.

**Sub-anchor structure is real in the key and unpurchasable in the arena.** LEAF-PROFILE (pooled p=0.005, 10/14 anchors) against LEAF-POWER (never below V=400 in 5/5 seeds) is not a contradiction — it is the support law. To buy a leaf-level cell at M=12 and reuse 3 you need ~380 distinct reserved questions *in that leaf*; the train-half median is 58. What would change it: more distinct questions per cell, which is corpus growth, not arena spend — and the growth law works against you, because a splitting tree holds per-node support near `minClusterSize` forever (leaves grow linearly with the train set, ~85 train questions per leaf throughout). **You cannot split and accumulate at the same time.** RESOLVE resolves this by freezing the reporting layer and letting only the routing layer split; the cost is that the atlas's granularity is terminal at the anchor, not provisional.

**Anchor birth does not work and the fix is unrun.** D4 is a registered FAIL with the mechanism fully diagnosed: routing recovers an unseeded domain, certification and anchor birth do not, because the loop never splits the root. D4-ROOT is designed and was never run. Until it is, RESOLVE's FOREIGN gate prevents the *mislabelling* — which is the serious failure — but cannot create the cell. New domains onboard by human registration, and calling that "online" would be dishonest.

**Routing error is an unmeasured bias in every metadata-free cell.** Source+domain routing is 81.3%, so ~19% of arrivals are filed wrong, and **no experiment in the campaign varied routing accuracy and measured the resulting attenuation of a capability contrast.** MC-E2E's +0.71pp metadata cost is a router-utility number, not a profile-accuracy number, and it is sign-unstable across seeds besides. This is the largest declared unknown in the design and it is declared rather than modelled, because modelling it without measuring it would be exactly the move this campaign has spent a year refusing.

**And the routing payoff itself is key-derived.** MC-ROUTER, MC-E2E and ROUTER-REGRET-MMLU are all zero-call, key-side analyses; the one attempt to derive a per-cell argmax from the judge instead of the key — GEN-ARENA — failed its bridge criterion on both corpora, with the judged top-two gap at 0.032/0.040 logits and a pooled −4.7pp cost of judging instead of keys. So the atlas's router utility is *demonstrated* only where keys exist, and on a key-free corpus it is a claim about the profile, not about the router. The tier map is the hedge: TIER-ROUTER-U reaches 0.6143 against per-cell best 0.6169 at 83% of the parameters and beats best-single 0.5543 by 6.0pp, which is a real product built entirely out of distinctions the judge can actually make — and on MMLU-Pro alone, where gemini wins all 14 anchors, the same machinery correctly returns nothing, and the system says so.
---

## AMENDMENTS FROM MEASUREMENT AND FROM THE OPERATIONS STRESS PASS (2026-09-14)

Three statistical objections were measured (RESOLVE-CALIB, `experiment_results/x12_crossdomain/resolve_calibration.txt`):

1. **§2.1's k=3 stands, and is conservative.** Measured k median 2.06 over 168 cells (p10 1.33, p90 3.02), not
   the 4.8 the stress pass estimated. SE=0.20 needs 51 distinct questions per cell, not 75. The resolution
   claim does not need re-deriving downward.
2. **§F's certificate moves from 0.95 to 0.975.** On all 891 (anchor, model-pair) edges rather than 66 global
   pairs: wrong-direction 1.68% at 0.95 (95% UB 2.59%) against 0.82% at 0.975 (UB 1.47%), costing 40 declined
   edges of 891. The target is restated as *wrong-direction rate with a 95% upper bound*, never a zero count.
3. **§4(1)'s tier map must standardise.** Per-anchor theta SD runs 0.937 to 1.630, a 1.7x spread, so raw theta
   is not comparable across anchors. The atlas publishes theta/SD_cell with SD_cell beside it; any statement
   that cannot be made that way is made within an anchor only.

Three operational objections are accepted without measurement, because the mechanism is clear and the campaign
has already paid for the lesson three times:

4. **The split is per ITEM, never per cluster.** `side = f(family_id ?: content_key)`, where `family_id` is a
   declared, write-once grouping taken from corpus metadata (task, upstream id, template id) and registered
   like an anchor. A MinHash cluster minimum is a property of what else has arrived, so a later near-duplicate
   retroactively flips an earlier item's side - the mutable-carrier failure the POOL-ASSERTION pass classifies
   as class (b), reintroduced inside a function that looks pure. MinHash runs as a nightly DETECTOR that
   reports cross-side near-duplicate mass as a contamination metric and never mutates a side.
5. **Leaves are content-addressed and the epoch gate moves to the leaf layer.** `leaf_key = sha256(sorted
   content keys of its train-side members)`; the integer node id never leaves the process. The epoch gate
   measures per-leaf membership Jaccard against the previous epoch, calibrated against H9-1's 0.66-0.69 ARI as
   the null - gating on anchor stability measures the one layer that does not move and therefore has no power.
6. **`stratumOf` misses are FATAL, and EXHAUSTED is separated from RESOLVED** all the way to the atlas: a cell
   that ran out of questions and one that ran out of budget carry different prices for the next level, and §5
   sells that column.
