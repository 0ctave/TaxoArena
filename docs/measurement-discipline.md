# Measurement discipline: four rules, each from a failure

Every rule below was learned by getting it wrong in this project, and in each
case the error survived review and was caught only by a downstream run or by an
external reader. They are listed with their instances because the instance is
what makes the rule credible.

The first three generalise past this project.

---

## 0. A test that cannot fail is not a test

**Ask before running any check: what result would falsify this?** If the answer
is "none available", the instrument is wrong and a clean result carries no
information.

This is the parent of rules 1 and 5, and of the 0-firings problem in rule 3.
Three instances in this project, each of which produced a confident null that
was structurally guaranteed:

* **The id-space audit.** Classifying every id column by set membership against
  every known id space returned **~100% for every column against every space** —
  because these are dense small-integer ranges over one corpus. The spaces
  coincide as SETS while disagreeing about which row each value points to. The
  audit had no failure mode. Only resolving a sample and comparing the retrieved
  CONTENT can distinguish them, which is how `7687` was found to resolve to two
  different questions.
* **"0 of 36 rescues."** The join was on `iter`, which the splitter hardcoded to
  `-1` for NO_PROPOSAL rows, so the numerator could not be non-zero. The
  measurement was acted on; a run refuted it.
* **The k-way gate at 0 firings.** Its statistic sat entirely on the passing
  side, which reads as "miscalibrated" — but min-pair fired first and censored
  everything it would have caught. Its evaluations were a filtered sample, so
  "never fired" could not distinguish redundant from mis-set.

The practical consequences are concrete and cheap: report a join's overlap and
its mixed-group count (rule 1); compare a gate's evaluation count against the
gate upstream (rule 3); audit ids by content resolution, never by membership
(rule 5).

**And a design corollary.** Where the schema has a choice of key, prefer one
that cannot collide by construction. `queries.id` is a content hash
(`q_dc3beb8ef429b9c1`); every integer id in this project shares a range with two
others. A key that cannot be confused needs no audit.

---

## 1. Report a join's overlap before reporting its result

A zero-overlap join produces a clean-looking null indistinguishable from a real
one. `0 of 36 rescues` and `no sibling pairs` both looked like findings.

**Instances (5).** The worst: a short-circuit was implemented on measured
evidence of "0 of 36 rescues", where the join was on `iter` and the splitter
wrote `iter = -1` for every NO_PROPOSAL row. Those rows sat in a bucket that
could not contain an ACCEPTED row, so the numerator was structurally impossible.
The change shipped, and a run refuted it (74 leaves against 84, J -0.011). The
corrected join gave 3 rescues in 404 — a 1% rate on an event that seeds a whole
subtree, which is exactly when a short-circuit is a bad trade.

Separately, a discriminative analysis joined taxonomy `queryId` (content hashes,
`q_dc3beb...`) to `eval_results.question_id` (integers). Overlap: **0 of 8299**.
It returned "no sibling pairs", which reads as a structural result.

**Rule.** Before reporting any null result from a join, report the overlap and
the mixed-group count. Here that count was **0 of 613 before a fix and 97 of 613
after** — visible without any domain knowledge.

---

## 2. Report a median with its IQR, and claim only what the spread supports

**Instances (3).** All the same shape: a number in the middle looked like a
result, the spread said otherwise.

* *Recoverable-normalised specificity.* Median 0.96 was reported as "rubrics
  recover essentially all of what is recoverable". IQR **[0.59, 1.25]**, 10-90
  **[0.23, 1.90]**, 43% above 1.0, max 2.76. The median was coincidental, and
  the ratio was not even commensurable — rubric vocabulary overlaps the cell's
  *hapax* terms, which the denominator excludes by construction. Retired.
* *CV under the z-gate.* CV rose 14.3% -> 15.7% and was reported as a
  degradation. The effect is an additive ~4.4-leaf offset
  (corr(reduction, seed deviation) = +0.006); SD is unchanged (variance ratio
  1.05 against F(4,4) crit 6.39) and CV rises mechanically from the mean shift.
  Correct statement: **no detectable dispersion change in either direction**.
* *Disattenuated correlation.* Rises 0.942 -> 1.015 -> 1.039 across granularity
  and clips past 1.0. Reading it as primary gives the opposite conclusion from
  the data, because disattenuation divides by sqrt(r_A r_B) and inflates
  whatever the observed value is. Pre-registering *observed as primary* is the
  only reason the conclusion was readable.

**Rule.** A median is not a result. Report the IQR beside it, and if the claim
would change at the quartiles, the claim is not supported.

---

## 3. A threshold derived for one quantity at one stage does not transfer

**Instances (3).**

* `separationEpsilon = 0.01` against observed separations of 0.028-0.087 — never
  binding because the threshold was calibrated on a different statistic.
  0 firings, but the fix was recalibration (0.025), not deletion.
* `proposalSeparationBar` served as both `marginalEps` ("how much must cluster
  k+1 ADD?" — a DIFFERENCE of separations) and the min-pair bar ("is every pair
  distinct?" — a LEVEL). One constant, two quantities.
* `tau = 1e-6` serves both a per-edit acceptance neutrality band (natural scale
  ~1e-4, the SE(dJ) median) and a per-iteration whole-corpus fixed-point
  tolerance. The certificate failed on a 2e-6 oscillation because a
  per-iteration tolerance was borrowed from a per-edit band.

**Rule.** A threshold is derived against a specific quantity at a specific
pipeline stage. Reusing it for a different quantity or a different stage is
silently wrong and surfaces only when something downstream fails.

**Diagnostic table for a gate with 0 firings** — the three cases look identical
in a counter and need different responses:

| evaluations | firings | statistic | diagnosis | fix |
|---|---|---|---|---|
| 0 | 0 | - | unreachable | delete |
| many | 0 | straddles the threshold | redundant, a stricter gate fires first | delete |
| many | 0 | entirely on one side | miscalibrated | recalibrate |

Distinguishing rows 2 and 3 requires the **evaluation count of the gate
upstream**: if gate B sees fewer evaluations than gate A, then A is filtering
B's input and B's observed distribution is censored. Without that, a redundant
gate is misdiagnosed as miscalibrated. (The k-way gate would have failed its own
test this way.)

---

## 4. Cross-node comparison in a mixture model needs shared concentration

Domain-specific, but the most consequential single defect found here.

In hierarchical vMF models, any comparison ACROSS nodes must use a shared
concentration. Per-child normalisers bias assignment toward the concentrated
sibling: `logNormalizer` decreases with kappa while `kappa*cos` increases, so
boundary queries go to the tighter cluster for reasons of concentration
bookkeeping rather than direction. At d = 256 the bias is tens of nats.

**Two sites, search closed.** First in the trickler's sibling competition (fixed
earlier; it had killed four ground-truth domains). Then, still live, in
`TaxonomySplitter.routeToVmfs` — the routing-sustainability check, which was
therefore validating candidates against a router the tree does not use.
Correcting it (`c381211`) moved rejections 750 -> 42 and leaves 84 -> 152.

**Rule.** When a fix is applied to one scoring site, grep for the pattern
everywhere it could appear. The second instance survived for months because the
first was considered closed.

---

## 6. A warning that fires on benign conditions is worse than no warning

It trains the reader to discount it, and then the one time it matters the
reader discounts that too. Same family as rule 0: a check that ALWAYS fires
carries as little information as one that CANNOT fire.

**Instance.** The run manifest had a single `dirty` boolean meaning "tracked
source differs from HEAD". It fired identically for a splitter edited mid-run
and for a `.tex` file edited in another session. The frozen artifact
`20260727_042523` read `dirty: true` from 14 `report/*.tex` files and one test
file, with **no production source dirty at all** — technically correct,
practically useless. Earlier in the same project a genuine mid-run source
modification was discounted because the flag looked like it always said that.

**Fix.** Split by what the condition actually implies:

| field | scope | severity | meaning |
|---|---|---|---|
| `dirty_src` | `src/main` | **warn** | blocks a freeze; the run is not reproducible |
| `dirty_other` | tests, report, docs | info | noise; the artifact is unaffected |

**And state the benign case positively.** The info branch says
*"src/main is clean, so this run IS reproducible from the repository"* rather
than staying silent. Silence is an absence the reader has to interpret; a
positive assertion is something they can rely on. This is the same reasoning
that turned the `excludeFromAnchoring` parse check from "notice the missing
warning" into a startup failure.

---

## Appendix: the reliability constant

`r = n/(n+c)` is Spearman-Brown rearranged, so `c = (1-r1)/r1` and
`r1 = 1/(1+c)` is the reliability of a **single query** for ranking 8 models.

Refit on the three measured split-half values: **c = 7.602, r1 = 0.1163**.

| n (held-out/cell) | measured r | predicted | diff |
|---:|---:|---:|---:|
| 40.8 | 0.842 | 0.843 | +0.0009 |
| 51.2 | 0.872 | 0.871 | -0.0013 |
| 90.2 | 0.922 | 0.922 | +0.0003 |
| 38.0 | 0.833 | 0.833 | +0.0003 (**out-of-sample**: 87-leaf tree, postdates the fit) |

Max deviation 0.0013 across all four.

**Two caveats that must travel with it.**

1. The bootstrap CI on `c` ([7.52, 7.66], 20k resamples of 3 points) measures how
   tightly three points pin a one-parameter curve — NOT sampling uncertainty in
   the underlying split-half estimates, which it does not propagate. Quote
   `r1 ~ 0.116`; do not quote the interval as a confidence interval.
2. It was fitted on **ground-truth** rankings, noise-free per question. Judge
   noise adds on top, so arena reliability at n queries will be BELOW this
   curve. It is a ceiling, not a prediction — the same status as the
   discriminative-power result.

---

## 5. A value you must parse out of another value is not a key

If you `substringBefore` it, split it, or read it from a prefix, it should be
its own column.

**Instances (3), all found in one afternoon.**

* `question_id` names **three different id spaces** — `mmlu_pro.id`,
  `eval_results.question_id`, `eval_question_link.question_id`. Joining
  taxonomy queryIds to `eval_results.question_id` gave **overlap 0 of 8299** and
  returned a clean-looking null.
* `match_history.query` carries the eval id as a `7687::` **text prefix**.
  Resolving that prefix against `mmlu_pro.id` returns a **different question
  that parses fine** — no error, well-formed output, wrong answer.
* `condition` is a **suffix on `snapshot_id`** (`..._MAIN`, `..._GENERIC_JUDGE`),
  recovered by chained `substringBefore` calls. It breaks the first time a
  condition or snapshot name contains an underscore.

**The shared tell:** each looked like a working key until something changed
underneath it, and none of them fails loudly.

### Set membership CANNOT audit these — content resolution can

Measured across every id column in the project:

| column | matches (set membership) |
|---|---|
| eval_results.question_id | mmlu_pro.id 100%, link.question_id 100% |
| mmlu_pro.id | link.question_id 100%, eval_results.question_id 96% |
| reserved_pool.question_id | queries.query_id 100%, mmlu_pro.id 100% |
| match_history '::' prefix | queries.query_id 100%, mmlu_pro.id 100% |

Everything matches everything. These are dense small-integer ranges over one
corpus, so the spaces coincide as SETS while disagreeing about which row each
value points to — which is precisely how `7687` resolved to two different
questions.

**Rule.** Never audit an id column by membership. Resolve a sample in each
candidate space and compare the retrieved CONTENT. And prefer a key that cannot
collide: `queries.id` is a content hash (`q_dc3beb8ef429b9c1`) and is
unambiguous by construction, where every integer id in this project is not.

### Migration note

Replace the parse chains, do not supplement them. If both paths survive, the
next reader cannot tell which is authoritative and the old one silently wins
wherever it is still called. Migrate historical rows forward rather than
supporting two schemas — pre-`c381211` verdict sets are not citable anyway.
