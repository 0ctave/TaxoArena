## Three operational risks

---

### RISK 1 — The split is not a pure function. The MinHash cluster key is order-dependent and retroactive, and it will silently invalidate the held-out side a third time.

**Mechanism.** §3A defines `cluster key = min(content key in cluster)` and `side = uint64(cluster_key) mod 1000 < 300`. Cluster membership is a property of *what else is in the stream*, not of the item. Item A arrives alone at t₀ → cluster {A} → side = f(ck(A)). A near-duplicate B with a smaller content key arrives at t₉₀ → the cluster's min drops → **A's side flips retroactively**, after you have already bought its reference, graded it, and judged 40 matches on it. MinHash banding closes transitively, so clusters only ever merge and keys only ever decrease: the flip rate is not a startup transient, it runs forever. This is the same failure class the campaign has already diagnosed twice — `Z:\FAC\TUBerlin\THESIS\TaxoArena\docs\judge_v2_program.md` (POOL-ASSERTION PASS) classifies it as **class (b)**: "a side that mirrors whichever pool is active". The design removes `eval_results.is_reserved` and then reintroduces the same mutable carrier inside a function that *looks* pure. The design's own defence makes it worse, not better: §6.3's per-row `assert side(row.cluster_key) == EVAL` is FATAL, so the first legitimate merge halts live ingest — and the operational response to a fatal assert on a service that has to run for a year is to relax it, which is exactly audit finding **C-7 (criterion substitution after a failure)** replayed at the ops layer.

**Second, sharper bite: it annihilates the strata on template corpora.** Measured in `Z:\FAC\TUBerlin\THESIS\TaxoArena\multicorpus_cache_v1.db`: BBH is 5,761 questions in 24 template tasks (146–250 each), and under the *current* per-item split each task holds 44–75 reserved questions — which is the number §4(1) quotes. Band a template family into one MinHash cluster and the family gets **one** side draw: `web_of_lies` is 250-in-eval or 0-in-eval. BBH's eval side becomes 30% ± 9.4pp with all-or-nothing strata, and the 24 sub-task rows §4(1) promises to pool to source are 0 or 250, never 44–75. The near-dup fix and the support law are in direct conflict and the document does not notice.

**Guard.** Make the split a function of the item and only the item: `side = f(content_key)`, per item, no cluster key. Enforce family coherence by *deriving the family from metadata that already exists* (`corpus_questions.task`, `corpus_questions.upstream_id`, template id) — a declared, write-once, human-registerable grouping — and salt the side function with the family id where one is declared: `side = f(family_id ?: content_key)`. Families come from registration, like anchors, not from a clustering algorithm whose output depends on arrival order. Then run MinHash as a **detector, not an allocator**: a nightly job that reports cross-side near-duplicate pairs as a contamination metric (`|scored ∩ near-dup-of-train|`), with an alarm threshold, and never mutates a side. A split that a stream can change is not a split.

---

### RISK 2 — Node ids are a per-run counter, every persisted arena artifact is keyed on them, and the epoch gate measures the one layer that cannot move.

**Mechanism.** `Z:\FAC\TUBerlin\THESIS\TaxoArena\src\main\kotlin\taxonomy\model\GraphNode.kt:82`:

```kotlin
private val idCounter = java.util.concurrent.atomic.AtomicLong(0L)
fun nextNodeId(): String = "n" + "%08d".format(idCounter.incrementAndGet())
fun resetIdCounter() = idCounter.set(0L)
```

with the comment "Reset per pipeline run." Leaf identity is **allocation order**, not content. Now look at what is keyed on it: `node_pair_stats` and `node_bt_states` PRIMARY KEY `(snapshot_id, node_id, …)` in `ratings.db`; `match_history.node_id`; `Z:\FAC\TUBerlin\THESIS\TaxoArena\reserved_leaf_assignments.csv` (`leaf_id,n00000265`); and — the one that bites hardest — `Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_configs\strata_profile_v1.json`, which hard-codes `"leafIds": ["n00000040","n00000124",…]` against `"snapshotId": "20260727_042523_…"` and is the map the *stopping rule* reads. §3B's claim that "nothing that persists is ever keyed on a leaf id" is false of the shipped system in four places.

The design's guard cannot see the drift. §3B gates cross-version pooling on "per-anchor assignment agreement ≥ 95%". H9-1 measures anchor drift at **≤0.42pp** while leaves span 72–87 at **ARI 0.66–0.69** — i.e. ~a third of leaf memberships move between draws while the anchor check reads 99.6%. The gate passes every time, by construction, in exactly the cases it exists to catch. You have built a smoke detector in the one room that never burns.

**Cost blowup rides along.** `ActiveBtRacingScheduler.pairStatus` (`…\src\main\kotlin\taxonomy\arena\ActiveBtRacingScheduler.kt:293-303`):

```kotlin
val stratum = profile.stratumOf(a.leafId)
if (stratum != null && profile.converged(stratum)) return "RESOLVED"
…
return "UNRESOLVED"
```

A leaf id absent from the frozen stratum map returns `null`, never `RESOLVED`, and schedules until `PAIR_EXHAUSTED` — full budget, every pair. The first epoch that commits a split renames every leaf, misses the map wholesale, and the service spends its entire cycle on cells it has no reason to fund. And `BtStoppingPolicy`'s own comment records the sibling pathology already observed: *"The run stopped for want of schedulable work and recorded it as convergence."* EXHAUSTED and RESOLVED are not distinguished downstream.

**Guard.** Three parts, all cheap. (i) **Content-address the leaf**: `leaf_key = sha256(sorted cluster keys of its train-side members)`, or if membership churns, of its top-k nearest train items; the counter id becomes a per-process handle that never leaves the process. Every ledger row, stratum map and profile row keys on `leaf_key`. (ii) **Move the epoch gate to the layer that moves**: compute leaf-level membership ARI and per-leaf Jaccard against the previous epoch on the frozen probe, and pool across versions only where a leaf's own Jaccard clears a bar — H9-1's 0.66–0.69 ARI is the null you calibrate against, and it tells you the anchor check has no power. A cell whose leaf failed the bar opens a new epoch; the old estimate survives as a prior, as §3B intends, but now on evidence. (iii) Make `stratumOf` miss **fatal, not permissive**, and separate `EXHAUSTED` from `RESOLVED` all the way to the Atlas — an UNSUPPORTED cell that ran out of questions and one that ran out of budget carry different "price of the next level", and §5 sells that column.

---

### RISK 3 — The edge pass has no working admission control. Both gates are measured to fail, in opposite directions, and the cycle budget is an order of magnitude short.

Three independent legs, all measured, all in the repo.

**(a) The answer-disagreement filter is inert on generative corpora — silently.** `AnswerDisagreementFilter.verdict` returns `UNDETERMINED` when either `pred` is blank, and `keep()` keeps every UNDETERMINED. Counted directly in `multicorpus_cache_v1.db`:

| source | eval rows | blank `pred` |
|---|---|---|
| MMLU_PRO | 216,576 | 0 |
| BBH / GPQA / MuSR | 138,762 | 0 |
| **MATH** | **23,832** | **23,832** |
| **IFEVAL** | **9,738** | **9,738** |

`model_output` and `gt_answer` are fully populated on those rows; only the extracted answer is missing. So on MATH and IFEval the filter keeps **100%** of question-pairs, not 16.9%. The shipped code warns once (`[MATCH-FILTER] … is INERT on this corpus`, `MatchFilter.kt`, guarded by a run-global `inertWarned` flag) and then proceeds. A `log.warn` fired once is not a control on a service that runs for a year. And this is not a corner: **F1 — the experiment §8 calls "the experiment that decides whether RESOLVE has a product at all" — is MATH + IFEval.** It is specified to run in the one regime where the scheduler's cost model and one of `B_cell`'s three terms both quietly stop existing.

That second half is the worse half. §2.5 assembles `b_comp` from "the answer-agreement composition of the backing matches (flip 0.105 disagreeing vs 0.192 agreeing)". On a generative cell every pair is UNDETERMINED — there is no composition to read, and the design gives no rule for it. Meanwhile SELECTIVE-ORDER measured what unfiltered scheduling does on signal-free pairs: 10.4% key-decidable, a single order invents a winner 78% of the time and gives it to the longer answer 78% of those. So the certificate loses a systematic term precisely where the bias it prices is largest.

**(b) The close-grade gate has a measured floor of 36.1%, not the ~10% the cost model implies.** HYBRID, `docs\judge_v2_program.md`: *"the smallest budget available is already 36% because that many pairs carry exactly equal grades (a consequence of the 0/100 collapse)."* τ is not a dial below 36%. The design's "spent only on edges a certificate says are within reach" has no mechanism behind it at the volume it assumes.

**(c) The cycle budget is a maintenance budget sold as a build budget.** §7 funds 4,300 edge matches per cycle for 18 models × 52 strata = 7,956 pair-cells — **0.54 matches per pair-cell**, against `nMin`≈9 for the local binomial and against §2.1's own 120–190 distinct questions per cell. Scaling the deployed board (12 models, 14 anchors, 9,142 matches, ρ 0.972) by pair count (2.3×) and cell count (3.7×) puts one board-equivalent near 78,000 matches ≈ 18 cycles ≈ 500k cce. No cell in the published cycle ever accumulates toward ORDERED. The atlas is permanently BANDED/PREDICTIVE-ONLY *by budget*, independently of whether F3 finds k stable — which means §7's "price of the next level" column is unfunded before F3 ever runs.

**Guard.** (i) **Filter on the checker's output, not on `pred`.** The design already buys a verifier or a reasoning solve at ingest; make the ingest artifact carry a normalised extracted answer (MATH: the checker's parsed value; IFEval: the per-constraint pass vector, where "disagree" = different vectors). Backfill is ~33.6k extractions over cached `model_output`, near-zero marginal cost, and it restores the filter on exactly the corpora the design is expanding into. (ii) **Make inertness a budget class, not a log line.** The allocator refuses to open an edge pass on a cell whose filter determination rate is below a threshold unless an explicit `generativeEdgeBudget` is set, and the Atlas marks such cells' `b_comp` as *unmeasured* — which under §5 refusal 3 means PREDICTIVE-ONLY, not BANDED. (iii) **Cap the edge pass by cell, not globally**, and publish cold-start time: state up front how many cycles to first ORDERED cell, or drop ORDERED from the v1 product and ship the tier map as the whole deliverable.

---

## Runners-up (cheap to fix, expensive to discover later)

- **Reference vintage is a confound the allocator manufactures.** `experiment_results\judge_solve\grok-reasoning.db` is `answers(question_id PRIMARY KEY, answer, gt, correct, raw, tokens, latency, ts)` — no model id, no version, no prompt hash. §2.4 promotes "buy once, never again" to a permanent principle, so references minted in month 1 and month 12 come from different provider-side model generations. The judge *transcribes* the reference (+1.811 reference-following, accuracy 0.922/0.657/0.226 by reference correctness), and §7 targets new questions at *under-supported* cells — so reference vintage is correlated with cell support, biasing the exact cross-cell contrast the Atlas publishes. §4(3) already forbids pooling 0.864- and 0.738-quality verdicts on one board; vintage is the same argument. Guard: stamp `(reference_model, deployment_fingerprint, minted_at)` on every reference, carry it as a fit covariate, and re-mint a fixed 200-question vintage probe each cycle.
- **The canary cannot see what it is for.** 300 matches × 2 orders × 2 replicates gives MDE ~2.7pp, but its questions carry *fixed-vintage* references, so it measures judge drift and is blind to reference drift. Measured session drift is +0.8pp (RUBRIC-512-SS, "almost half of RUBRIC-512's +1.8") — same order as the effects being published, below the canary's floor. Guard: split the canary into a frozen-reference arm and a re-minted-reference arm.
- **There is no quarantine primitive.** `match_history` in `ratings.db` has no `batch_id`, no judge model, no prompt hash, no order column. §3C's stamps are a real improvement, but "recover from a bad batch" needs *refit-from-log-excluding-batch-X* as a tested, first-class operation, plus the provider's response id on every row. Note the precedent: **R2 lost per-order votes on 9,235 of 36,892 resumed rows** — the resume path, not the run path, is where state gets dropped.
- **A newcomer mid-stream is quoted honestly but scheduled invisibly.** §4(4) prices placement at ~400 matches; it does not say the 18th model turns 153 pair-cells into 171 across 52 cells and re-opens every cell's comparison graph. Guard: placement runs in its own budget line with its own stopping rule, and the Atlas shows a model as PROVISIONAL until its cells have their own certificates — never absorbed silently into an existing board.

---

**VERDICT: BUILD WITH CHANGES.** The evidence discipline is genuinely excellent and the refusals are the right product — but ship none of it until the split is per-item with registered families (not MinHash clusters), leaves are content-addressed with a leaf-level epoch gate, and the edge pass filters on checker output with a per-cell admission cap. Those three are prerequisites, not hardening: without them the first epoch boundary corrupts the ledger silently, and F1 runs in the one regime where the cost model and the certificate both quietly stop working.