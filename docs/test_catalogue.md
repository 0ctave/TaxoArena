# TaxoArena test catalogue [as of 2026-10-07; counts not maintained]

A plain-language guide to every experiment on record: what each test does, why it was run, and what it tells us. One entry per record in `docs/agents/results/<ID>.json`; the text is copied from the `plain_description` field of that record (written 2026-10-07). This catalogue is descriptive only: it changes no outcome, verdict, chip or sentence of record. The binding record of each test stays the programme (`docs/judge_v2_program.md`), the ledger (`docs/test_ledger.html`) and the record JSON; where this summary and the record differ, the record wins.

Tests are grouped by sub-question (SQ1 USE, SQ2 TRUST, SQ3 TAXONOMY, SQ4 PRICE, SQ5 INVARIANCE in the framing of record) plus two support groups (data hygiene, engineering), then by state, finished tests first. Results marked as "history, not evidence" belong to the older judged question family (p2dca) that the author ruled out as evidence for the thesis.

254 tests in total.

## Contents

| Group | Tests | By state |
|---|---|---|
| [SQ1 Use](#sq1-use) | 30 | done 28, UNDETERMINED 2 |
| [SQ2 Trust](#sq2-trust) | 105 | done 97, UNDETERMINED 5, paused 1, READY 1, withdrawn 1 |
| [SQ3 Taxonomy](#sq3-taxonomy) | 47 | done 43, UNDETERMINED 2, run-unreviewed 1, registered 1 |
| [SQ4 Price](#sq4-price) | 19 | done 18, blocked 1 |
| [SQ5 Invariance](#sq5-invariance) | 18 | done 14, UNDETERMINED 1, registered 2, withdrawn 1 |
| [Data hygiene](#data-hygiene) | 15 | done 14, built 1 |
| [Engineering/infrastructure](#engineeringinfrastructure) | 20 | done 17, blocked 1, built 1, withdrawn 1 |

## SQ1 Use

30 tests: does cell-conditional evaluation change a decision (routing, model choice, profiles)?

### State: done (28)

#### CELL-FLIPS — on the union routing data, cells where a TRAIN-chosen challenger beats the TRAIN-chosen best single model on ...

- **What it tests:** On the multi-benchmark union data, with training and evaluation sides split so no question text is shared, it picks the best overall model and a per-cell challenger on the training side. It then checks on the evaluation side, cell by cell, whether the challenger really beats the overall best beyond noise. The tree is built separately inside each source benchmark, so it uses the source label (source-conditioned) and is not fully label-free. No judge calls; answer keys only.
- **Why:** Tests the core premise of cell-conditional evaluation: do some cells of the tree have a different best model than the global leaderboard says?
- **What it tells us:** If no cell flips, reporting per cell adds nothing over one leaderboard. If cells flip, it does add something. Result: flips exist. 7 of 101 tested cells show a real winner change (4.6% of items), mostly reasoning-puzzle (BBH) task cells won by one model. This is the same reordering the declared task labels already show. It does not show that the tree finds order changes the labels miss (3 such flips are descriptive only), nor that BBH as a whole has a different winner. One data draw only.

#### DESIGN-PROBES — six probes opened by relaxing three design constraints: drop the anchors, rank per TIER with cost as a router ...

- **What it tests:** Six quick probes on cached data. Two compare routing that goes straight to the nearest leaf with routing that descends through the category layer. One measures per-cell accuracy of the reference answers. Three try grouping models into tiers and routing to the cheapest model in a tier. No calls.
- **Why:** It tests whether three design choices earn their place: the category layer, choosing a reference model, and ranking models strictly.
- **What it tells us:** Each probe tells the design what to keep or drop. Result: descriptive only. Straight-to-leaf routing is slightly better (0.764 vs 0.753, and 81.6 vs 72.1 on the six-corpus union), so the category layer helps reporting, not routing. Picking a reference per cell gains nothing, but reference accuracy varies (0.73 to 0.95), so it must be tracked. Tier-then-cheapest on the union nearly matches the best per cell with 83% of the parameters. Tiers are not recovered exactly. Bootstrap tiers can be confidently wrong where the judge is biased. Two of the six probes were added after the registration. The reference-per-cell, tier-recovery and bootstrap-tier legs were later ruled 'history, not evidence'. The routing and tier-router legs were not.

#### DRIFT-REPLAY — synthetic source-mix shifts replayed from the content-closed v2 union EVAL; OOS-rate and cell-occupancy ...

- **What it tests:** Simulates shifts in the mix of question sources on held-out data. It compares two drift alarms tuned to the same false-alarm rate: a chi-square test on how questions fill the tree's cells, and the existing out-of-scope flag rate. It also compares the anchor-free tree's cells with k-means cells of the same number (no judge calls).
- **Why:** It tests whether the cells are useful for monitoring, by detecting when incoming traffic changes, and whether a tree does this better than plain clustering.
- **What it tells us:** If watching cell occupancy beats the out-of-scope rate, cells add a practical monitoring use; a tree beating k-means would favour the tree. Result: on synthetic shifts of moderate size, the cell-occupancy alarm detects more often than the out-of-scope rate (61% vs 21%). This comes from small sources whose share is multiplied, not from pure cells, and the out-of-scope rate is blind by construction to some directions. The tree's cells do no better than k-means (no equivalence claimed). Small shifts were not detected. The shifts are synthetic, not real traffic.

#### ESCALATION-CURVE — full accuracy-coverage curve as the lowest-margin / OOS items escalate to the best single model (combined ...

- **What it tests:** Draws the full accuracy curve for routing the least certain questions to the best single model instead of the per-cell choice, at every coverage level. It compares this with sending a random set of questions of the same size. Uses about 5,900 evaluation questions. No judge calls.
- **Why:** Checks whether the routing's uncertainty signal is a useful safety valve: does escalating uncertain items first beat escalating at random?
- **What it tells us:** A positive area means the uncertainty ordering helps. A negative area would remove it as a safety valve. Result: averaged over the coverage levels tested, escalating uncertain items first beats escalating at random by about +0.66 accuracy points, which is small. It is not a gain at every level: at high coverage the interval at each level includes zero. A plain k-means partition does the same (+0.60), so this is not a property of the tree. There is no usable operating point: the chosen coverage's gain includes zero, and escalating at very low coverage lowers accuracy.

#### ESCALATION-RC — does escalating low-margin, OOS or fragile queries from the AF-U cell policy to the best single model beat ...

- **What it tests:** On the multi-corpus routing data, sends low-confidence or out-of-scope questions to the best single model instead of the per-cell routed model. The tree is built separately within each source benchmark, so it is source-conditioned, not fully label-free. It compares this with escalating the same share of questions at random, with a k-means version beside it. No judge calls.
- **Why:** It checks whether route confidence (margin, out-of-scope detection) is a usable safety valve for the routing product.
- **What it tells us:** If confidence-based escalation beats random escalation, the router knows when it is unsure. If it loses, the confidence signal is misleading. Result: done, undetermined. It beats random escalation by +0.50pp, but the interval just touches zero (a boundary case, below the detectable effect size). Compared with no escalation it adds almost nothing (+0.15pp). It avoids the cost of random escalation but buys almost no accuracy. The failure condition did not fire.

#### GPQA-HEADROOM — does a harder corpus restore the discriminative power MMLU-Pro has lost? (zero calls)

- **What it tests:** Using 18 models' existing results, the test compared a harder benchmark (GPQA) with MMLU-Pro. It counted how often the top 4 models all get a question right, and how often two models disagree on a question.
- **Why:** Ranking the strongest models needs questions they do not all solve, and MMLU-Pro may be nearly used up for that purpose.
- **What it tells us:** If GPQA still separates the strong models, it is the place for work on the top of the leaderboard. Result: done, with no judging involved. On GPQA the top 4 all succeed on only 7% of questions, against 37% on MMLU-Pro, and models disagree more often (36% against 20%). So GPQA has not saturated and is the natural place for that work. This is a saturation readout only, not a judged result.

#### KEY-INFO-V2 — LOO Brier key information of AF-U cells over the marginal, summed over 18 models, vs K_0 (KI1) and vs 200 ...

- **What it tests:** No calls. On the combined dataset (about 5,900 held-out questions, 18 models), the test measured how much knowing a question's tree cell improves prediction of which models answer correctly. It compared this with k-means cells and with 200 random cell sets of the same size within each source.
- **Why:** It asks whether cells carry real information about model strengths beyond simply knowing which benchmark a question came from.
- **What it tells us:** Beating the random cells means the cells are meaningful. Beating k-means would favour the tree as an index. Result: done. The tree's cells carry clearly more information than random cells within the same source. But k-means did somewhat better than the tree as built, and about half of that gap comes from 191 questions the tree files under another source. All of this uses source labels ('source-conditioned'). It is predictive information, not a measured routing gain.

#### LCB-STAGE0-INTERACTION — on LiveCodeBench v6 (1,055 problems), a model x region interaction in pass/fail beyond difficulty, difficulty ...

- **What it tests:** On LiveCodeBench (coding problems, 26 models), a label-free tree is built on problem texts. The test asks whether some models do unusually well or badly in particular tree regions, beyond overall problem difficulty and input format. It is a pre-check before paying for a specialised-judge experiment.
- **Why:** Per-cell evaluation and specialised judges only pay off if models really have region-specific strengths on this corpus.
- **What it tells us:** Result (no new calls): STOP. No model-by-region effect was found on the training side. A later power check corrected the original claim: at the actual design the test could only reliably detect effects larger than about 0.30 logit SD, so it is uninformative about smaller ones. This is bounded, never 'no interaction'. The judged stage is not run on LiveCodeBench. This covers this corpus, roster and tree recipe only.

#### LCB-STAGE0-POWER-RESIM — G1's power at the MEASURED LCB stage-0 design (plug-in null on the real TRAIN data, iid interaction on the ...

- **What it tests:** Simulation (no calls) on the real LiveCodeBench stage-0 design: if model rankings truly differed between regions by a given amount, how often would the test have detected it?
- **Why:** An earlier test found no region-dependent ranking and stopped; this checks whether that test was strong enough for its 'no effect' to mean anything.
- **What it tells us:** High power would make the earlier null informative; low power makes it uninformative. Result: done; power was only 22% at 0.20 and 66% at 0.30 logit SD, so the earlier null says nothing about effects up to at least 0.30; the stop decision stands but 'no interaction' must never be written.

#### MC-E2E — MC-E2E (+ MC-SEEDS): does the multi-corpus router survive when the cell must be INFERRED rather than given? ...

- **What it tests:** Runs the multi-corpus router end to end. The question's cell is predicted by the tree instead of given, then the policy picks a model. It is compared with the best single model over three random seeds. No calls.
- **Why:** It checks whether the routing gain survives when the cell must be inferred in practice.
- **What it tells us:** A gain above noise at every seed would make routing usable. Result: the router beats the best single model in all three seeds (about +3.4 points as first read). But the gain varies between seeds more than the noise level, so its size is not seed-stable. Corrections: the analysis drew its own split, so about 70% of the questions it scored had been training data for the taxonomy. A later clean re-read on the split of record gives +2.9 points [+1.8, +4.0], and the cost of inferring the cell is neither shown nor ruled out. The routing tree also had about 6.7% of the routed questions visible during construction. An early figure (+4.1) was superseded. The pool is checked by question id only, not by content.

#### MC-LEAF — multi-corpus stage 2b: does the grown taxonomy route better than the designed source/domain strata? (zero ...

- **What it tests:** On a six-dataset combined pool, sends each held-out question to its nearest tree leaf and answers it with the model that did best on that leaf's training questions. Accuracy is compared with routing by the designed dataset/domain groups.
- **Why:** It asks whether the discovered fine-grained taxonomy routes questions to models better than the obvious human-designed categories.
- **What it tells us:** It shows whether fine leaves add routing value or spread the data too thin. Result: done. As first read, the grown tree lost to the designed domains (59.2% vs 60.1%, -0.9 points), as predicted, which suggested that model strengths sit at family or domain level and that leaves dilute support. A later clean re-read on the split of record gives -0.09 points with an interval from -1.1 to +0.9, descriptive only, so the loss is not reproduced as a decided result. An open flag remains: the held-out side may overlap with training content and has not been re-verified (pool checked by id only).

#### MC-ROOT — multi-corpus stage 1c: can a different UNION ROOT rule recover the routing the six-way descent loses? (zero ...

- **What it tests:** In the merged six-benchmark tree, it compares three rules for routing a new question to a leaf: step-by-step descent from the root, picking the nearest leaf directly ('flat leaf'), or picking the benchmark first. Measured on 6,482 held-out questions.
- **Why:** Descent through the merged root was losing routing accuracy, and the fix needed to be located.
- **What it tells us:** It shows which routing rule to use for multi-benchmark runs and where the accuracy loss sits. Result: done, descriptive. Nearest-leaf routing reached 81.6% correct vs 72.1% for descent (+9.5 points, highly significant). Benchmark-first changed almost nothing, so the loss is in the root directions. Nearest-leaf became the recommended default. Later disclosure: about 6.7% of the routed test questions had been visible to the tree's construction, so these numbers carry a contamination caveat (bounded, not re-estimated).

#### MC-ROUTER — multi-corpus stage 2: is there anything to route on a union of task families? (key-only, zero calls)

- **What it tests:** On a union of six benchmarks (21,606 questions, 18 open models), it picks the best model per benchmark or per subject on the training side, and compares accuracy on the held-out side with the best single model and with a perfect per-question oracle. Answer keys only.
- **Why:** Asks whether a multi-benchmark mix has anything to gain from routing, after MMLU-Pro alone showed none.
- **What it tells us:** A real gain justifies the routing line of the thesis. Result: yes, there is something to route. Routing by benchmark or by subject gains about 4 to 5 points over the best single model (0.553), and this is beyond noise. A MATH answer-formatting artefact inflated this, and after the fix the gain is about +2.7 points. The perfect oracle (0.907) is a ceiling, not a reachable target. On MMLU-Pro alone the gain is zero.

#### MULTI-SWE-ADMISSION — MULTI-SWE-ADMISSION (cheap variant): does Multi-SWE-bench_trajs carry at least one (language x repo) stratum ...

- **What it tests:** Checks whether the Multi-SWE-bench agent trajectories contain any language-and-repository group with at least 120 evaluation tasks under the split rules, and whether the agent's step cap can be recovered. Data download only, no LLM calls.
- **Why:** It decides whether this agent corpus can support a per-cell agent profile or only a description.
- **What it tells us:** A group of 120 or more would allow an agent profile cell. Result: done. No group reaches 120 on the evaluation side (all large repos fell on the training side), so agents stay description-only on this corpus under this split. The step cap was fully recovered: 50 steps. There are no agent capability numbers and no cross-scaffold comparison.

#### ONLINE-REPLAY-LOMO — ONLINE-REPLAY-LOMO (stage 1, no build): replaying a left-out union member into the other five AF-U trees ...

- **What it tests:** Leaves one corpus out and feeds it into the trees of the other five corpora one question at a time (filing, out-of-scope buffering, refitting the cell means). It compares this with a batch rebuild, and checks how many existing cell addresses move. No judge calls.
- **Why:** It asks whether the tree can absorb a new domain online without moving existing addresses, and how close it gets to a full rebuild.
- **What it tells us:** Small loss and stable addresses would support online updating in deployment. Result: done. Online replay files 3.9pp worse than a batch rebuild (interval -5.1 to -2.6pp; one draw). Refitting the means moved 9.25% of existing addresses when BBH was added (3% for MMLU-Pro), so addresses stay stable only if the means are frozen. The claim that 'ids are immutable' online narrows accordingly. The tree vs k-means comparison is descriptive only.

#### ONLINE-STAGE2 — frozen leaf means, an OOS-only buffer with a GATE-calibrated threshold (target catch rate 0.80, nested ...

- **What it tests:** Simulates a new corpus arriving one question at a time. The tree files each question online (fixed leaf centres, a buffer for odd questions, periodic small rebuilds), and the result is compared with a full rebuild on the same six held-out corpora. No calls.
- **Why:** It tests whether the tree can grow online without losing filing accuracy compared with rebuilding.
- **What it tells us:** Matching a rebuild would back the 'evolving tree' design. A loss would mean rebuilding is needed. Result: online filing is 3.3 points worse than a rebuild, so the warning test fired. The online design is not filing-neutral, and the claim narrows to 'stable ids at a filing cost; rebuild periodically'. The buffer also catches too few new questions (55%). One draw only.

#### OOS-BASELINES — is S0's label-free no-match score (CLINC150 AUROC 0.974, qwen3 256) equivalent within 0.010 AUROC to standard ...

- **What it tests:** On a standard intent dataset (CLINC150) with the same embeddings, compares the label-free 'no matching cell' score from flat k-means cells with standard out-of-scope detectors. Two of these use class labels (nearest class centre, class Mahalanobis) and two do not (nearest-neighbour distance, one global ellipsoid). No judge calls.
- **Why:** It checks whether the earlier 0.974 detection score is special to the cell approach or just reflects the embedding, by comparing with standard baselines.
- **What it tells us:** If simple detectors match it, the score belongs to the embedding; if the cells match labelled detectors without labels, that is a real advantage. Result: the k-means cells beat the two label-free baselines and are within 0.01 of the two labelled detectors, without using labels. The lead depends on the settings (nearest-neighbour with k=1 does slightly better). These are flat k-means cells, not the tree, on one dataset and one embedder.

#### PROFILE-DEVIATION-CERT — does the (model, anchor) deviation term carry certifiable content beyond the global theta? (zero judge calls ...

- **What it tests:** For each model and subject anchor, it tests whether the model's subject-specific deviation from its overall strength can be certified, using either the key or the judge. No judge calls.
- **Why:** Per-cell profiles are only informative if "model X is certainly better or worse than usual here" can be stated. This checks whether such statements are supported.
- **What it tells us:** If the judge's certified deviations agree with the key, profiles add real per-cell content. Result: the judge certified 22 of 280 cells, but 3 of these (13.6%) have the wrong sign against an established key. That triggers the registered rule (a count rule, not a significance claim). The certified set is not confirmed by the key. No 'above or below its own standing' claim is published for any judge-built cell, and profiles stay a re-indexed global score. Older judged question family, later ruled 'history, not evidence'.

#### PROFILE-INTERVAL-ALL-UNION — do the 52 (source, domain) union strata carry a key-built profile row with a class? (zero calls; plan A2)

- **What it tests:** Using answer keys only (no judge), for each of 52 (benchmark, domain) groups in the 6-benchmark union with 18 models, checks by split-half whether the model ranking inside the group is reproducible, and gives each group a pass/fail class.
- **Why:** Per-cell profiles are only useful if the per-cell ranking is stable; before this, union groups had no reliability measurement at all.
- **What it tells us:** It shows which groups can carry a per-cell profile and which cannot. Result: done; all 52 classed (on the strictest reading 27 pass, 12 pass with interval, 13 fail); overall reliability high (0.85 for group-specific differences). Two GPQA groups pass without any real within-group order. Key-based only, no judge; caveat: the union tree used leaks some evaluation questions into training (disclosed later).

#### PROFILE-RELIABILITY-INTERACTION — what is the MMLU-Pro profile reliability once anchor difficulty is removed, i.e. the model- AND ...

- **What it tests:** On 14 MMLU-Pro anchors, it measured how reproducible each model's per-cell profile is across random halves of the questions. Overall model skill and cell difficulty were both removed first. The bar was 0.70. No calls were made.
- **Why:** It tests whether a 'profile' is real per-cell information, or just the global score re-sorted by how hard each cell is.
- **What it tells us:** High reliability would mean profiles carry real per-cell strengths. Near-baseline reliability would mean they are just a global score. Result: done. The answer-key profile reliability is 0.87 [0.80, 0.93], so it passes. The judge-built profile is lower, at 0.67. The judge-built figures come from the older judged question family, later ruled 'history, not evidence'. A later disclosure noted that this tree had some evaluation questions leaking into its build; no number was changed.

#### PROFILE-RELIABILITY-X20 — does a bigger roster rescue the anchor capability profile? (zero calls; the identical instrument at the ...

- **What it tests:** No calls. A split-half reliability check on the 20-model board: each cell's questions were split in two at random, per-model strength profiles were computed on each half, and the two were correlated (40 repeats), at subject and leaf level.
- **Why:** It asks whether per-subject capability profiles are stable enough (bar 0.70) to publish, after the 12-model board just missed the bar (0.67).
- **What it tells us:** Passing allows per-subject claims on a board of this size. Failing would close that deliverable. Result: done, corrected. On the merged board subject-level reliability is 0.72, which clears the bar, but only narrowly (95% range 0.61 to 0.83). It must be published with that range. An earlier 'fail' reading on a sparser board was withdrawn. Note: older question pool, ruled 'history, not evidence'.

#### ROUTER-CLEAN-POLICY — does the deployed union router still beat the best single model when every policy is fitted on the TRAIN side ...

- **What it tests:** It re-measured the gain from choosing the best model per cell (cell = benchmark x domain, predicted by the tree), compared with always using the single best model. Policies were fitted only on training questions and scored on all 6,482 held-out questions, with an interval that includes policy-fitting noise.
- **Why:** The earlier gain (+3.38 points) had been fitted partly on held-out questions, so it needed a clean re-read.
- **What it tells us:** A clean positive gain supports per-cell routing as useful. No gain would withdraw the claim. Result: done. Per-cell choice beats the single best model by +2.9 points (95% interval +1.8 to +4.0), replacing the old figure. The cells are supplied (declared), not discovered, so this is not evidence that the taxonomy was discovered. About two thirds of the gain comes from BBH, and MMLU-Pro alone shows no clear gain. Reading the cell from the tree instead of the true label changes accuracy by an amount not distinguishable from zero (a cost below about 1 point is neither shown nor excluded).

#### ROUTER-REGRET-MMLU — is there anything to route on MMLU-Pro at all? (zero calls; key as oracle on the pool of record)

- **What it tests:** Using the key on MMLU-Pro, it picks the best model per tree leaf and per subject on the training side, and compares held-out accuracy with the best single model and a perfect oracle, on 12- and 46-model rosters. No calls.
- **Why:** Asks whether a single benchmark has any routing signal at all.
- **What it tells us:** A gain would justify routing within MMLU-Pro. Result: nothing to route. The same model (gemini) is best in all 14 subjects, and the routing gain is zero. Model-by-topic effects exist but never change the winner. This motivated the multi-benchmark line. The train/test split was checked by question id only, not by content.

#### ROUTING-ATTENUATION — FRAMEWORK item 11: does misrouting at the 19% union rate attenuate per-cell contrasts by more than the cell's ...

- **What it tests:** Simulating sending questions to the wrong cell (10, 19 and 30% error, plus the tree's real 24.7% mismatch with declared subjects). It measures how much this weakens per-cell model differences, across 168 subject-by-model cells.
- **Why:** Per-cell routing is only useful if realistic misrouting does not wash out the differences it is meant to reveal.
- **What it tells us:** Result (no new calls): the criterion fails. At 19% misrouting, 42 of 168 cell differences shift by more than their standard error. The effect is a uniform shrinkage (about 20% at 19%). It hurts most where differences are large, not in the small subjects, which pass only because their uncertainty is larger. No established model ordering was reversed under any misrouting level.

#### TREE-BACKOFF — does empirical-Bayes back-off of AF-U leaf accuracies toward their ancestors (tau on GATE) route the union ...

- **What it tests:** No calls. On the content-closed combined dataset, the test compared routing by each leaf's own model accuracies with routing that blends small leaves' estimates toward their parent nodes (empirical-Bayes 'back-off'). A k-means hierarchy was run alongside.
- **Why:** It asks whether the tree's hierarchy itself (not just its leaves) improves the decision of which model to send a question to.
- **What it tells us:** A gain supports the claim that the hierarchy is useful. A loss would withdraw 'the hierarchy helps routing'. Result: done, marginal gain of +0.9 points (range +0.03 to +1.76). The gain depends on the chosen blending strength (one item decided it; at the next setting the range touches zero). It comes from MMLU-Pro, not BBH, and uses source labels. It does not show the tree's hierarchy beats k-means'.

#### UNION-AF-ROUTE — UNION-AF-ROUTE (RP13, re-scoped per the author's D4): a FRESH anchor-free federated TRAIN-only tree on draw ...

- **What it tests:** Builds a fresh federated tree without the declared category labels, but separately within each source benchmark (so it is source-conditioned, not fully label-free). It uses only training questions on the clean multi-corpus split. It tests whether routing each cell to its best model beats the best single model, beats per-source k-means at matched cell counts, and matches routing by declared labels within 1pp. No judge calls.
- **Why:** It checks whether the routing gain survives when the cells are discovered rather than declared, and whether the tree beats plain clustering.
- **What it tells us:** Shows whether label-free discovered cells are useful for routing and whether the tree structure adds anything over k-means. Result: done. Beats the best single model by +1.52pp (thin, interval +0.14 to +2.91). It falls 1.15pp short of declared labels, so it is not equivalent to them. Against per-source k-means the difference (-0.45pp) is within noise, so the tree is not shown to be better than clustering. One draw, one roster.

#### UNION-PROFILE-HOME — are the 39 order-reliable union strata or the 14 MMLU-Pro anchors the profile's home? (the numbers the ...

- **What it tests:** On the six-corpus union pool (6,482 questions, 18 models), it measures how reliably each designed stratum orders models. For each reliable stratum it then checks whether the set of best models differs from its source corpus's set. No calls.
- **Why:** It decides whether the per-cell model profile lives best on the 39 union strata or on the 14 MMLU-Pro categories.
- **What it tells us:** It answers which object the profile should be built on. Result: the 39 strata are reliable (0.865), while the 14 MMLU-Pro categories are less so (0.68). The best set differs from the source's in 36 of 39 strata, but in 28 of these the set is only larger, a power effect. A real routing consequence shows in only 8 strata. Which object the paper leads with stays the author's choice. Answer keys only. Caveat disclosed later: the union tree used leaks some evaluation questions into training.

#### V2-DECLARED-CELLS — leg U, the declared-cell gain G on the content-closed v2 union EVAL (a sensitivity, NOT a replication); leg ...

- **What it tests:** On the clean version 2 split, with no tree and no embedder, picks the best model per human-declared cell (dataset × domain) from training data. It checks whether this beats the single best model on held-out data, and whether model skill profiles vary reliably across the 13 MMLU-Pro categories.
- **Why:** It checks the basic "per-cell evaluation is useful" claim on clean data, using only the declared categories.
- **What it tells us:** It shows whether cell-level model choice pays off at all, before any discovered tree enters. Result: done and valid. The per-cell policy beats the best single model by +2.7 points, and the skill profiles are more reliable than chance. It is a sensitivity check, not a replication. Most of the gain comes from one dataset (BBH): leaving BBH out, or looking at MMLU-Pro alone, the gain is not separated from zero, so it is descriptive. No claim is made per dataset.

### State: UNDETERMINED (2)

#### KNN-ROUTE — cell-free kNN routing (k = 50 deciding; own-source [SC]) vs AF-U on the union routing data; unrestricted kNN ...

- **What it tests:** Compares routing each question by its 50 nearest neighbours (within its own source corpus) with routing by the discovered cells of the label-free union tree, on about 5,900 evaluation questions. No calls.
- **Why:** It asks whether cells add anything for routing over raw neighbourhoods.
- **What it tells us:** If neighbours did as well, cells would only matter for reporting. If cells did better, they would earn their routing role. Result: undetermined. The gap is +0.12 points with an interval of -1.2 to +1.4, so cells are neither shown to add nor shown unneeded. The result is source-conditioned (it uses the source corpus). The unrestricted neighbour comparison is descriptive only.

#### ROUTE-SOURCE-NULL — AF-U's routing gain against a 6-cell source policy (D_S) and 200 random within-source cell sets at AF-U's ...

- **What it tests:** On the combined clean pool, compares the routing gain of the anchor-free tree's cells with two baselines. One simply routes by dataset (6 cells). The other uses 200 random cell sets of the same sizes drawn inside each dataset.
- **Why:** It asks how much of the tree's +1.5-point routing gain comes from just knowing which dataset a question came from.
- **What it tells us:** It separates gain from real structure from gain that only reflects the dataset label. Result: UNDETERMINED. The tree's cells beat dataset-only routing by +0.5 points, but the interval includes zero, so "better than dataset routing" is not shown at this sample size. The gain is above what random cells of the same size give, so the dataset alone does not explain it either. The cells are source-conditioned (they use the dataset label), so this is not a label-free gain.

## SQ2 Trust

105 tests: can the LLM judge and its certificates be trusted, and where do they fail?

### State: done (97)

#### A-REDEFINE-REFIT — FRAMEWORK item 2: refit the widener with the answer-agreement predictor A redefined on the eval side; does ...

- **What it tests:** Re-fits the small model that predicts when the judge goes wrong. The predictor "do the two answers agree?" is now computed from the models' extracted answers on the evaluation questions instead of from the judged questions. Uses the 12-model MMLU-Pro board, with no new judge calls.
- **Why:** Checks whether how the agreement predictor was defined could have biased the judge-error model, and whether its main slope is actually supported by the cases where the right answer is firmly known.
- **What it tells us:** If nothing moves, the earlier fit holds. If the numbers shift, the predictor was biased by which questions got judged. Result: passed as a consistency check only. On this evenly spread schedule the two definitions are almost identical (correlation 0.997), so the test had no power against the bias it was meant to catch, and that bias remains untested. The slope passed its registered rule but is only borderline once questions are resampled in groups by subject. It also showed that an earlier claim that MMLU-Pro is 100% decidable by the answer key was false (0.68 to 0.98 per subject). It was later ruled history rather than evidence, because it ran on the older question pool.

#### ABSTAIN — the judge scores 0.15 when misled; can the reference's own confidence flag those cases and turn them into ...

- **What it tests:** On 242 questions where models disagree, the judge was allowed to abstain (score as a coin flip) whenever the reference answer's own confidence fell below a threshold. Several thresholds were compared with always answering.
- **Why:** The judge goes badly wrong when the reference answer misleads it. The test asks whether the reference's own confidence can flag those cases in advance.
- **What it tells us:** A win would give a cheap safety valve for the judge. A loss would close another confidence-based fix. Result: negative (no new calls). Confidence does carry signal: the reference is right 48% of the time below 90 and 90% at 100. But every abstention threshold scores lower than always answering, because abstaining throws away more wins than losses. This is the third confidence-based fix to fail. It is on the older judged data, which the author has since ruled history rather than evidence.

#### AGGREGATE — is the dual-order TIE rule protective or lossy, and can an order-symmetric tie-break recover the frontier ...

- **What it tests:** The judge sees each pair of answers twice, once in each order. When the two readings disagree it records a tie. This test took the 49 ties in two earlier runs and tried two ways to break them fairly: ask the judge twice more and take the majority, or have it grade each answer separately.
- **Why:** It checks whether those ties hide real information the judge throws away, and whether resolving them would let the judge recover the true order of the strongest models.
- **What it tells us:** If the ties can be settled correctly, the judge becomes more accurate for only a few extra calls. If the strongest-model order still does not come out right, judge noise is not the only obstacle. Result: done. Asking twice more settles most ties correctly and raises overall accuracy by about 8 points for about 16% more calls. It does not recover the order of the strongest models: ordering two models 1.7 points apart is beyond this judge on this corpus. Later ruled history rather than evidence, because it ran on the older question pool.

#### ANCHOR-PROFILE-INTERVAL — is the 0.7183 pass a pass? (zero calls)

- **What it tests:** Measures how reliable the per-subject model profiles are (how well two random halves of the judged questions agree), and puts a confidence interval around it by leaving out one subject (one of 14 anchor domains) at a time. Done on the 12-model board and the merged 20-model board, using already-stored verdicts (no new judge calls).
- **Why:** The merged board's reliability of 0.7183 just cleared the 0.70 bar, and the question was whether that is a real pass or a lucky point estimate.
- **What it tells us:** If the lower end of the interval clears 0.70, per-subject claims can be published as reliable; if not, they need the interval printed next to them. Result: not a clear pass. The interval is about 0.61 to 0.83, so its lower end is below 0.70 on every reading. Per-subject claims may be published only with the interval. The gain from merging boards is not distinguishable from zero. Ruled later as history rather than evidence, because it was judged on the older question pool.

#### ARCH-V2-G23 — the zero-call replay (identity; certificate A vs B; conjuncts; two-judge residue; Holm; multi-stream c~)

- **What it tests:** A replay of recorded judge data through the new version-2 code (no new calls). It checks that the code reproduces the old tables of pairwise model wins byte for byte. It also checks whether a new certificate rule (B) for declaring one model better than another is acceptable in place of the old rule (A).
- **Why:** Before trusting the new pipeline, it must reproduce the old results, and the new certificate must not certify more wrong orderings.
- **What it tells us:** Exact reproduction plus an acceptable rule B would let version 2 replace version 1 safely. Result: reproduction held exactly. Rule B was acceptable on both data draws (it keeps about 69% of comparisons, with no more wrong 'established' orderings than A). The ranking was stable across draws. A companion simulator meant to predict error rates failed its own validity check and decides nothing. The certificate reading rests on older judged data and is now treated as an imported quantity, not fresh evidence.

#### ARCH-V2-INDUCE-RUBRIC-2 — re-induce ONE MCQ rubric artefact from the same 40 TRAIN inputs of record with a corrected induction prompt ...

- **What it tests:** An LLM wrote a grading guide (a rubric) for multiple-choice questions from the same 40 training examples, using a corrected prompt and an automatic screen for unwanted wording. The aim was a rubric for the new judge design.
- **Why:** The judge needs a rubric that does not bias its verdicts, and the first attempt had been rejected.
- **What it tells us:** A fit rubric could go into the new judge. An unfit one shows that the induction step or the screen is still flawed. Result: done. The rubric passed every automatic check on the first try, but a reviewer judged it unfit: it defines correctness as matching a reference answer that is itself wrong on 133 of 1,027 items, and it rewards visible reasoning. It was not adopted, and this registration will not be re-tried. The author then registered a separate new induction with a revised prompt. It makes no claim about rubric value or accuracy, and it shows that the automatic screen is weak evidence of fitness.

#### ARENA-13 — add grok-4-1-fast-reasoning as a 13th contestant without circularity, and measure self-preference on purpose ...

- **What it tests:** Adds a 13th model (grok-4-1-fast-reasoning) to the judged arena. About 1,800 new matches are judged against a reference answer built from other strong models, and 598 frontier matches are re-judged with grok's own answer as the reference. 2,394 judge calls.
- **Why:** Tests whether an arena can take a new model without upsetting the existing order, and whether a judge favours its own model family.
- **What it tells us:** A stable order would show that boards can grow step by step. A gap between the two references would point to self-preference. Result: the 12 existing models kept their order (rank agreement 0.970). Accuracy was 0.837, just below the 0.85 bar. The newcomer came first, but later checks found the ordering unresolved at this budget, not wrong. The apparent self-preference (+7.9 points) was later explained as the reference agreeing with that model, not as true self-preference. This test belongs to the older question pool, so it now counts as history, not evidence.

#### ARENA-V2 — STACK-v2 on the arena's own matches: the board the paper publishes from the deployed judge (9,144 matches ...

- **What it tests:** Re-judges all 9,144 arena matches (12 models, 87 cells) with the improved production judge recipe (Mistral judge, reasoning reference, both answer orders, anchor rubric). It compares the resulting leaderboard and accuracy with the first-version judge.
- **Why:** The paper publishes its leaderboard from this judge, so it must agree with answer-key accuracy at least as well as the old judge did.
- **What it tells us:** If the leaderboard tracks key accuracy closely and the judge is right more often, the published board can be trusted. If not, the board is built on a weak judge. Result: done, about 18k calls. Rank agreement with key accuracy is 0.972 (old judge 0.951). On questions with a decidable key, accuracy is 0.852 (old 0.757), and model-by-domain differences are significant. The top-4 order count is fragile: whether it has 'at most 1 violation' depends on how the board is fitted, roughly a coin flip. The robust claim is that the new judge beats the old one. The order of the frontier models is not settled. Older judged question family, later ruled 'history, not evidence'.

#### ARENA-V2-X20 — how does the deployed judge behave when the board grows from 12 to 20 models, with two new frontier entrants ...

- **What it tests:** Adds eight models to the 12-model arena, so 20 in total, about 12,400 new matches judged by Mistral-Large, and checks the merged board against the answer key on five criteria.
- **Why:** It tests whether the deployed judge stays trustworthy as the board grows, including two new models that land in the top group.
- **What it tells us:** Passing would mean the board can grow without breaking. Failing on the top group would mean the judge cannot order the strongest models. Result: passed 4 of 5. Correlation with the key is 0.963, the original 12 keep their order, and new pairs are judged correctly 88% of the time. It failed on the top-6 order (4 inversions where at most 3 were allowed). Later ruled 'history, not evidence' because it ran on the earlier, contaminated question pool.

#### ARM-B-VINTAGE — the ARM-B reference re-mint — does a second vintage of the cached grok-4-1-fast-reasoning reference, minted ...

- **What it tests:** The judge is given a cached 'reference answer' written by grok-4-1-fast-reasoning. This test re-generated that reference on 200 canary questions with exactly the original protocol and measured how often the new copy agrees with the old one.
- **Why:** The reference is reused for weeks. If the same model under the same prompt now answers differently, the old cached references could silently drift out of date.
- **What it tells us:** High agreement means the cached reference can be treated as stable over time. Agreement below the 0.89 alarm bar would trigger a re-mint and doubt about reuse. Result: done. The two copies agreed on 189 of 200 questions (94.5%, 95% interval 90.4% to 96.9%), so no alarm. Both copies were right about equally often (84.5% vs 85.0%). This is agreement, not accuracy, from one re-mint, so it gives no drift rate. Older question family, later ruled 'history, not evidence'.

#### ARXIASK — given ONLY the questions that discriminate the inverted frontier pair, can either format recover the true ...

- **What it tests:** Uses only the 302 questions where two top models (arx and iask) differ by the answer key, so that every match has a known winner. Both are judged in pairwise and pointwise format, plus a version matched for answer length (1,196 calls).
- **Why:** Asks why the judged arena puts these two frontier models in the wrong order: is it answer length or something else?
- **What it tells us:** Shows whether a judge can recover the true order when given only the questions that matter, and what blocks it. Result: neither format recovered the true order. Length was not the cause. The cause was that the reference answer shown to the judge is much worse on these questions (0.73 correct, against 0.86 overall), and the judge follows it. A judge that relies on a reference cannot order two models better than the reference is accurate on the questions where they differ. This was measured on an older judged set that is now classed as history, not evidence.

#### BFCL-FINAL-STATE-SWAP — does the INHERITED verify-first block's 'final answer' furniture explain the BFCL pilot's indecision? One ...

- **What it tests:** Re-judges the same 458 disputed agent-task comparisons from the BFCL judged pilot, in both answer orders, with one change: four phrases in the judge prompt say 'final state' instead of 'final answer'. Main measure: how often the judge's verdict flips into a tie when the order is swapped.
- **Why:** In the pilot the judge was undecided about 22% of the time; this checks whether a prompt written for question answering (talking about a 'final answer') was a poor fit for agent tasks and caused that indecision.
- **What it tells us:** A drop of 5 points or more would blame the prompt wording; no drop rules that wording out. Result: done; tie rate 21.4% vs 21.8% (change -0.4 points, interval about -3.9 to +3.0), so these four strings do not explain 5 points or more of the indecision (descriptive point only; a small effect is not excluded). Position bias and task difficulty remain open, neither established.

#### BFCL-FLIP-RESEED — do the BFCL pilot's 100 ORDER-FLIP TIES reproduce when the SAME 100 matches are posted a second time, or are ...

- **What it tests:** The test re-sent the same 100 matches from a function-calling benchmark (BFCL), in both orders and with an identical prompt. In the pilot, these were the matches where the judge's verdict flipped with answer order. It counted how many flipped again.
- **Why:** It separates two explanations: are these flips a stable property of certain matches, or random noise at the edge of a decision?
- **What it tells us:** If they flip again often, the flips are systematic, and position bias or task difficulty should be handled. If they rarely flip again, they are just noise. Result: done. 69 of 100 tied again, clearly above the noise level, so the flips are a stable property of each match. When both orders gave a decision, the judge picked the answer shown first 42 to 1. The test cannot tell whether position preference causes the flips or only breaks ties on matches the judge cannot decide.

#### BFCL-JUDGED-PILOT — on the BFCL base stratum, where does the deployed judge's agreement with the corpus's own CHECKER_OUTPUT sit ...

- **What it tests:** The first judged run on an agent benchmark (BFCL function-calling, 57 tasks). It measures how often the deployed LLM judge agrees with the benchmark's own automatic checker, with the task's correct call sequence given as a reference.
- **Why:** It tests whether the judge can be trusted outside MMLU-Pro-style questions, on agent traces, against a 0.75 agreement bar.
- **What it tells us:** Agreement well above or below 0.75 would say whether the judge transfers to agent tasks. Result: done. When ties count, agreement is 0.74 [0.66, 0.82], and the run cannot say whether that is above or below 0.75. On the verdicts where the judge commits, agreement is 0.95, its best in the record. The weak spot is many order-flip ties, with a clear preference for the first-shown answer; the cause is not separated. Self-preference is not shown. Pilot only, with no profile cell.

#### BOARD-W — confidence-weighted vs gated vs ungated top-4 board (zero calls)

- **What it tests:** It re-read the 599 top-model matches of the STACK-v2 judge run, with no new calls. Three versions of the top-4 leaderboard were built: unweighted, weighted by the judge's confidence, and keeping only verdicts with confidence of 0.95 or more.
- **Why:** It checks whether trusting only confident judge verdicts gives a leaderboard closer to the true answer-key order.
- **What it tells us:** If weighting or gating fixed the order, confidence would be a useful filter. If not, it adds nothing. Result: done, descriptive. All three boards give the same order with 1 violation of the answer-key order. Squaring the confidence weight gave the key order, but that was exploratory only. Note: this belongs to the older p2dca data family, which is now classed as history, not evidence.

#### BOUNDARY-DISAGREEMENT — is judge disagreement concentrated at the tree's cell boundaries? (zero judge calls; the MULTI-OWNERSHIP ...

- **What it tests:** No judge calls. On about 21,500 existing judged matches, the test compared questions that sit near a cell boundary (low routing margin) with questions deep inside a cell. It looked for more ties, more verdicts that flip when the answer order is swapped, and less stable model rankings.
- **Why:** It checks the idea behind 'multi-ownership' (judging boundary questions in two cells): that the judge struggles most at cell boundaries.
- **What it tells us:** An excess of disagreement at boundaries would justify a paid dual-cell judging run. No excess would close that idea for free. Result: done. On the merged board there was no clear excess of ties or flips, so no dual-cell run was launched and the idea closes as a judging mechanism. Qualifier: on one of the two schedules (x12) flips were somewhat higher at boundaries, so the mechanism is 'not shown', not shown to be absent. Note: this record belongs to the older question pool, which the author ruled 'history, not evidence'.

#### BUDGET-LOMO — was leave-one-ANCHOR-out the wrong fold structure? (zero calls; BUDGET-TRANSFER's first reading suggested the ...

- **What it tests:** Re-tests the calibration of the error-budget widener for the ranking certificate. Each fold leaves out every comparison involving one model (12 folds). This is set beside leaving out one subject area or one model pair, all on the same 891 comparison edges. No judge calls.
- **Why:** An earlier reading suggested that leaving out one subject area might hide errors that run along models, which would make the adopted 2.4x calibration figure too optimistic.
- **What it tells us:** If leaving out a model gave much worse calibration, the adopted figure would be wrong. Result: done (corrected rerun). All three fold types agree: 2.3x to 2.5x overall, 1.7x on statistically established edges. So the adopted 2.4x stands, and the predicted 4-8x failed. The falsifier did not fire. One earlier explanation (about parameter instability) was withdrawn. It was judged on the arena pool later ruled 'history, not evidence'.

#### CANARY-BASELINE — the test-retest floor of the deployed judge (grok-4-1-fast-non-reasoning, STACK-v2) on the frozen 300-match ...

- **What it tests:** Judges a frozen set of 300 matches twice, one week apart, with the deployed judge (grok-4-1-fast, production recipe). It measures how often the verdict changes between the two passes.
- **Why:** Before the judge can be watched for drift, we need its own baseline noise level, so that later changes have something to be compared against.
- **What it tells us:** A low and stable retest rate gives an alarm threshold for later checks. A high rate would mean the judge is too noisy to monitor. Result: done. 26 of 300 verdicts changed (8.7%, interval 5.6-12.2%), the same rate on contested and cross-tier matches. No alarm. Every change happened at the edge of a 'tie' verdict: no clear win flipped to a loss. This is a noise floor, not a drift test. Older p2dca question family, later ruled 'history, not evidence'.

#### CANARY-EPOCH2-RUNG — epoch-2 alarm and the within-session rung on the frozen 300-match canary (1,200 calls)

- **What it tests:** Re-judges a frozen set of 300 matches about two days later and again in the same session (1,200 calls). It counts how often the judge's verdict changes.
- **Why:** It checks whether the judge drifts over time beyond its normal retest noise, which would undermine every comparison made with it.
- **What it tells us:** A disagreement rate above 0.138 would raise the drift alarm and flag later judged numbers for re-reading. Result: no alarm. Verdicts changed on 7% of matches after about two days and on 9.3% within the same session, with no time trend. At this resolution the canary measures retest noise and finds no drift. Drift smaller than about 4.5 points cannot be ruled out. The frozen match set comes from the older question pool, which was later ruled history rather than evidence.

#### CERT-ALIGN-SIZE — on the four anchor-free MMLU-Pro re-draw trees, are site-certified splits better aligned with the declared ...

- **What it tests:** On four MMLU-Pro trees built without any category labels, compares splits that passed the statistical 'site certificate' with uncertified splits of similar size, on how well each matches MMLU-Pro's declared subject categories.
- **Why:** Checks that the certificate is not just rewarding big splits, i.e. that it carries real information about meaningful structure.
- **What it tells us:** If certified splits align better at equal size, the certificate means more than 'large'; if not, it is mostly a size filter. Result: done; certified splits align better (+0.063 on a 0-1 agreement scale, permutation p 0.0001), holding under every size control though about 0.01-0.016 smaller, and size is not fully matched in the largest group. Valid on these trees only; it does not show splits are 'correct', nor other corpora or embedders.

#### CERT-DIRECTION-STREAM — integrated over the arm direction stream, how often does CERT-UNDER-FILTER's C1 hold, and what is its ...

- **What it tests:** Re-runs an earlier certificate check (CERT-UNDER-FILTER) over 200 random draws instead of the one registered draw. It counts how often the result still holds and builds an interval that includes this extra randomness. No new calls.
- **Why:** It asks whether an earlier trust result depended on one lucky random draw.
- **What it tells us:** A high hold rate would mean the earlier result is robust. A low one would mean it depends on the draw. Result: descriptive only. The result holds in 49 of 200 draws (about 25%), and the wider interval includes zero. So it held at the registered draw but is marginal across draws, and even that band depends on the bootstrap seed. The earlier verdict cannot and does not change. A later ruling classes the underlying judged data as history.

#### CERT-K2-DEFLATED — CERT-PC-K2-KNOWN's merged pairs and CERT-PC-K2's source split re-run under the existing DEFLATED site null ...

- **What it tests:** Earlier two-way split tests were re-run against a stricter 'deflated' random baseline for the structure certificate. A negative control cut the data along its longest axis. No calls were made.
- **Why:** It checks whether the certificate can tell real two-category structure apart from data that is merely stretched in one direction.
- **What it tells us:** If the deflated baseline certified real splits but not the axis-cut controls, it would be a usable certificate for data-driven splits. Result: done, valid. The deflated baseline certified the real splits and the meaningless axis cuts alike (5 of 5 each). Its verdicts follow high-variance directions whether or not discrete structure is there. So it does not discriminate, and it is not a usable certificate for this purpose. The hypothesis it was meant to test was neither refuted nor supported.

#### CERT-PC-K2-KNOWN — a known-strength k = 2 certificate positive control at G12's depth-1 sizes: two distinct declared categories ...

- **What it tests:** A positive control for the split certificate. It merges two distinct declared MMLU-Pro subjects into one cell, at strong, medium and borderline pairings. Then it asks whether the certificate detects the known two-way split at realistic sizes (about 450-490 questions). No calls.
- **Why:** An earlier test saw 0 of 60 two-way splits certified. That could mean no real structure, or a certificate too weak to see two-way structure. A known-strength control would tell these apart.
- **What it tells us:** If known two-way splits certify, the certificate can see that kind of structure. If they fail at full size, the certificate has a sensitivity limit. Result: done, a non-outcome. No chosen pair qualified as a valid control. Only chemistry+law certified, and only by a margin smaller than its own subsampling noise. So the certificate's sensitivity to two-way splits stays undetermined. This does not show the certificate is too strict or insensitive.

#### CERT-PLANTED — power curve of the plain J site null for a planted 2-way shift (random direction, random half-split, delta x ...

- **What it tests:** Plants an artificial two-way split of known strength inside real math, physics and economics question samples (about 486 questions each). It then checks whether the certification test for branch points detects that split. No judge calls.
- **Why:** An earlier build certified 0 of 60 first-level branch points. This test asks whether that zero says anything about the data, or whether the test simply cannot see such structure at these sizes.
- **What it tells us:** If the planted splits are detected, a zero means there is no real structure. If they are missed, the zero is uninformative. Result: done. At the chosen strength the planted split was certified in only 1, 0 and 1 of 5 cases. Because the null distribution is fitted to the site's own (planted) rows, the test is insensitive at these sizes, so the earlier 0 of 60 is uninformative under that null. This is not a general 'the certificate cannot detect structure' finding: the chosen strength is the point where signal and null cross.

#### CERT-POSITIVE-CONTROL — does the site-null certificate that gave G12 0 of 60 certify the declared 14-category level of R2's MMLU-Pro ...

- **What it tests:** Applies the split certificate (which compares a split with random splits) to structure known to exist: the 14 official MMLU-Pro categories over about 7,000 questions. No calls.
- **Why:** An earlier test (G12) certified 0 of 60 tree splits, so this checks whether the certificate can certify anything at all, or whether it is simply blind.
- **What it tells us:** If the known categories failed too, G12's zero would be a sensitivity limit. If they pass, the certificate works at least at this scale. Result: the certificate clearly certifies the declared categories (statistic 0.108 against a random-split maximum of 0.042). That overturns the 'blind certificate' reading at whole-corpus scale. A later test (CERT-PC-SIZE) extended this to the smaller sizes of real tree splits. The test does not 'validate' the certificate in general.

#### CERT-RESOLUTION — per-site Clopper-Pearson on the null exceedance, flat BH and prefix-closed hierarchical BH over the recorded ...

- **What it tests:** Applies standard multiple-testing corrections to the existing per-split chance tests, which use 300 random repeats, on four trees. The corrections are false-discovery-rate control over all splits and a nested version that only tests a split if its parent passed. The question is which splits remain certified at a stated error rate.
- **Why:** It decides which tree splits the thesis and the talk may honestly call certified, rather than just "passed their own test".
- **What it tells us:** It turns a loose per-split pass/fail into a claim with a known error rate. Result: done, and the review found it valid. On the tree of record, 2 of 70 splits are certified (the splits at Chemistry and at Engineering) under the nested correction, at a per-family 5% false-discovery rate. The flat correction certifies none. The certificate does not cover the tree as a whole. 53 splits were never tested because their parent did not pass, so they are "untested", not "unreal". Only 300 repeats were used.

#### CERT-UNDER-FILTER — does the answer-disagreement filter bias the separation certificate's edges AGAINST the key, beyond what its ...

- **What it tests:** The deployed filter drops matches where both answers agree, which keeps about two thirds of the 9,142 verdicts. On the 12-model board, it compares how many certified 'A beats B' edges point against the answer key under that filter with random subsets of the same size.
- **Why:** Before making the filtered schedule the default, the separation certificate must not get biased toward wrong orderings just because of which matches the filter keeps.
- **What it tells us:** Fewer wrong edges than in random subsets means the filter is safe on direction. More wrong edges would forbid making it the default. Result: done. Under the filter, 17 certified edges pointed against the key, against an average of 24.15 for random subsets of the same size. The interval was just below zero, so the check held, but only marginally. It became uncertain under many alternative random streams: it held on only about a quarter to a third of 200 direction streams. One subject, psychology, carries much of the effect. The other counting convention was undetermined. This settles direction only, and the default switch stays the author's decision. This belongs to the older question pool, which is now ruled history, not evidence.

#### CONSENSUS-FIT — how much of a model's standing in a reference-based arena is being RIGHT, and how much is AGREEING WITH THE ...

- **What it tests:** Statistical model fitted on existing judged matches (no new calls): how much does the judge's verdict depend on a model being actually correct versus agreeing with the reference answer the judge is shown?
- **Why:** If an LLM judge mostly rewards agreement with its reference, an arena measures conformity, not correctness.
- **What it tells us:** A large agreement effect would show the arena rewards matching the reference. Result: done; agreeing with the reference weighs about 2.7 times as much as being right, but this is an upper bound (part of it appears even when no reference is shown). At the model level nothing can be separated (correctness and agreement are almost the same), so an earlier 'consensus' explanation of one model's lead was withdrawn. Note: this test is on the older p2dca question family, later ruled 'history, not evidence'.

#### DECOMP — is the ARENA-13 +7.9pp self-preference, or just a reference that happens to agree with one contestant? (zero ...

- **What it tests:** Splits the 598 paired frontier matches from ARENA-13 by which answer each reference supports. It then separates the +7.9-point gap into a part caused by the reference agreeing with a contestant and a remaining part. No judge calls.
- **Why:** Tests whether ARENA-13's apparent judge self-preference is real or just the reference siding with one contestant.
- **What it tells us:** A large remaining part would mean genuine self-preference. A remaining part near zero would mean the reference's agreement leaks into the verdict. Result: the claim was amended. Reference agreement explains all of the gap, and no self-preference is left. As a by-product, on 299 matches with byte-identical prompts the judge still disagreed with itself 5.7% of the time. That is the judge's repeat-noise floor. This test belongs to the older question pool, so it now counts as history, not evidence.

#### ENSEMBLE-REF — can a stronger reference be built from the eval set's own strongest models? (free check, zero calls)

- **What it tests:** The answers of the 6 strongest models in the set were combined by majority vote to build a reference answer for the judge. The result was compared with the single reasoning-model reference, overall and on hard questions. No calls were made.
- **Why:** It asks whether a better reference for the judge can be built from the models being evaluated.
- **What it tells us:** A higher accuracy would give a cheap, stronger reference. The same accuracy would mean a better reference must come from outside the set. Result: done. It is not stronger: 0.875 overall and 0.772 on hard questions, the same ceiling as the single reference. The hard questions are hard for every model in the set. Older p2dca data family: history, not evidence.

#### ESCALATE-LLAMA-LAW — FRAMEWORK item 24: does escalating to the reasoning judge buy back the model-anchored residue on ...

- **What it tests:** Re-judges every Law and Philosophy match of Llama-3.1-70B, plus a matched control model (Qwen1.5-72B), with a stronger reasoning judge. It then compares the verdicts with the cheap judge on the same matches (666 calls).
- **Why:** A few remaining wrong-direction verdicts were tied to Llama-3.1-70B in those cells. The test asks whether escalating to a stronger judge just there fixes them.
- **What it tells us:** A gain on the treated model and none on the control would justify a targeted escalation rule. Result: done, failed as predicted. The stronger judge mostly removes ties. It does not make committed verdicts more accurate (gain +0.000 on the treated model), and its gain is larger on the control. The escalation rule is not adopted, and these cells stay 'unseparated, not certified'. The comparison was against a proxy of the shipped judge, and the script was edited during the run window. Older judged question family, later ruled 'history, not evidence'.

#### FLIP-PROV — where do STACK-v2's flips come from? (B2; zero calls)

- **What it tests:** Using about 2,000 verdicts from the assembled judge, the test asked when the verdict changes if the two answers swap position. It compared pairs where the answer key decides the winner with pairs where it does not, and checked which of the two order-wise votes was right.
- **Why:** It decides whether order flips need an extra fix or are already handled by recording a tie.
- **What it tells us:** If flips sat on clear-cut pairs, the judge would need repair. If they sit on near-ties where neither vote is reliable, recording a tie is the right response. Result: done. Flips are 22% on undecidable pairs and 5% on decidable ones, mostly where the two answers are close. On flipped decidable pairs, each order is right about half the time, a coin toss. The flip guard was relaxed. It did not separate position bias from noise, which a later test did. Later ruled history rather than evidence, because it ran on the older question pool.

#### FORMAT — style perturbation (CALM-style; ~1.2k Mistral calls; conditional on prevalence >= 150)

- **What it tests:** It used 383 answer pairs where exactly one answer had markdown formatting. The formatting was stripped and the Mistral judge's verdicts were compared before and after (about 1,200 calls).
- **Why:** It checks whether the judge rewards formatting style rather than correctness.
- **What it tells us:** A change of more than 3 points would reveal a format bias. No change would rule it out for this judge. Result: done. No format bias: 0.786 vs 0.791 (p = 0.79) and 0 flips toward the plain answer. This was shown for Mistral only. Older p2dca data family: history, not evidence.

#### FORMAT-REF — is GRADING less reference-dominated than COMPARING, and is the 2.7:1 a property of the format, the judge ...

- **What it tests:** No calls. A regression was refitted on existing verdict caches for the same matches: pairwise and pointwise (single-answer grading) formats, two judge families (grok, Mistral), and a version with no reference answer in the prompt as a control.
- **Why:** It asks why the judge follows the reference answer more than actual correctness: is it the format, the judge model, or the recipe?
- **What it tells us:** It separates 'the judge copies the reference' from 'the judge reasons for itself', and shows whether the result depends on the judge model. Result: done, descriptive. The control failed, so the earlier 2.7:1 'reference beats correctness' ratio is an upper bound. In the grading format, showing a reference made the judge lean on it more and on its own assessment less. A follow-up found this displacement does not happen in the pairwise format. grok and Mistral behaved almost identically, so it is the recipe, not the model. Note: older question pool, ruled 'history, not evidence'.

#### FRONTIER — is the top-cluster inversion caused by dilution, by judge capability, or by the reserved split taking the ...

- **What it tests:** Looks at the top-4 models, whose arena order is inverted against the answer key. It checks whether the questions that separate them exist, what happens on matches the key can decide, and how the judge behaves when the key calls a tie. No judge calls.
- **Why:** Finds out whether the top-cluster inversion comes from too little data, a weak judge, or the judging format itself.
- **What it tells us:** Each possible cause points to a different fix: more data, a better judge, or a different format. Result: the dataset is cleared, since all pairs are separable, for example 301 questions separate arx and iask. The likely mechanism is that on pairs the key calls a tie, the pairwise judge invents a winner 52% of the time and favours the longer answer. The capability question stays underpowered (about 44 matches per pair). This test belongs to the older question pool, so it now counts as history, not evidence.

#### FRONTIER-FIT — FRAMEWORK item 5: can a widener fitted on the frontier edges alone reach a readable calibration status, and ...

- **What it tests:** Tries to fit the 'widener' (a correction that inflates uncertainty so that separations between models are not over-called) using only the 75 per-cell comparisons among the top (frontier) models. It also checks whether the rule that keeps the frontier 'banded' (left unordered) holds. No judge calls.
- **Why:** It checks whether the calibration of the separation certificate can be verified in the frontier region, where the judge is weakest.
- **What it tells us:** A readable calibration status would tell us whether frontier separations can be trusted. Result: done. The criterion fails by simple arithmetic: 75 comparisons are too few to ever reach a readable status, so the status is undetermined. 'Banded by rule' is confirmed on the pooled board (0 of 6 frontier pairs ordered), but on the per-cell edges it is only a manual override. A correction fitted away from the frontier detectably under-covers frontier errors. Older p2dca question family, later ruled 'history, not evidence'.

#### GEN-ARENA — does the deployed judge reproduce the router's decisions WITHOUT an answer key, on the union's generative ...

- **What it tests:** A judged arena of 3,000 matches (5,994 calls) on MATH and IFEval with 8 models. The judge is shown the checker's material as its reference: the correct answer for MATH, the list of constraints for IFEval. Judged results are compared with the answer key.
- **Why:** Asks whether a judge can stand in for the answer key, both in ranking models and in picking the winner a router would choose.
- **What it tells us:** If the judge matches the key, judged arenas could replace keys where none exist. Result: registered FAIL. The judge ranks the field well on MATH (rank correlation 0.92) but poorly on IFEval (0.72, many ties), and it picks the wrong top model on both, because the top two are nearly tied. Judged verdicts can stand in for a key for a ranking, not for choosing the single best model, which is what routing needs. Later note: 367 of the MATH matches involve answers cut off by the 1,024-token limit.

#### GROK-CALIB — FRAMEWORK item 26, the x12 schedule re-judged by the SHIPPED judge under the recipe, so the shipped judge ...

- **What it tests:** Paid run (18,284 calls). The 9,142-match schedule was re-judged with the judge actually shipped (grok-4-1-fast) under the final recipe, both answer orders. Its verdicts were compared match by match with the earlier Mistral verdicts.
- **Why:** The shipped judge needs its own calibration evidence, not one borrowed from a different judge, before its confident 'A beats B' edges can be published.
- **What it tells us:** If its error pattern can be estimated, ordered edges can be published for this judge. If not, it stays in a fallback mode. Result: done. The prediction held and the error pattern closely matched Mistral's. Calibration remains undetermined at the operating point. Later corrections: a second run of the same judge did not reproduce the estimate. Pooling both runs passes the registered bar, but not a stricter check that accounts for repeated questions (p about 0.07). Note: older question pool, ruled 'history, not evidence'.

#### IFEVAL-RESPONSE-ORACLE — with an executed per-response constraint-checker vector attached to each trace, does the IFEval judge's ...

- **What it tests:** On instruction-following questions (IFEval), judges the same 407 matches twice: once normally, and once with the automatic constraint checker's pass/fail result for each response attached. It then compares tie rate, order flips and accuracy. Uses 1,628 judge calls.
- **Why:** The judge did poorly on IFEval (many ties and flips). This tests whether it could not check the constraints or simply would not commit to a verdict.
- **What it tells us:** If ties vanish once checking is done for the judge, the problem is verification; if ties persist, the judge is unwilling to decide. Result: ties fell from 26% to 1%, flips from 24% to 1%, and accuracy rose from 0.65 to 0.99. So the judge failed to count constraints, not to commit. Important limit: the attached result decides the answer outright. This is an upper bound, not a usable recipe, and it is from one judge, one session and one corpus.

#### ITEM-26-POOLED — ITEM-26-POOLED + RE-JUDGE-RULE: does pooling the established labels of the two draws of the same judge on ...

- **What it tests:** Pools two repeated runs of the same judge (grok) on identical inputs to test whether a calibration parameter of the judge's error model can be estimated reliably. The pooled data holds 46 cases where the board ordered a model pair in the wrong direction, which are only 29 distinct pairs. It also sets rules for when a re-judge is needed. No calls.
- **Why:** One run met the bar and the other did not; pooling asks whether the judge's error calibration is actually identified, which underpins trusting ordered per-cell judged rankings.
- **What it tells us:** Identification would support ordered judged rankings for this judge; failure would downgrade them. Result: done. It passes the registered bar, but the two runs share most of the same errors (the 46 wrong orderings are only 29 distinct model pairs). Once that overlap is accounted for, it is not significant at the usual 5% level (p about 0.07). No cell is downgraded. Older p2dca question family, later ruled 'history, not evidence'.

#### J1-R — the reasoning judge WITH the reasoning reference: the ceiling of verify-then-judge at reference accuracy 0.86 ...

- **What it tests:** A reasoning judge (grok) re-judged about 2,000 matches with a reasoning model's reference answer, which is right 86% of the time. The comparison was the same judge without a reference.
- **Why:** It sets the ceiling for the 'check against a reference, then judge' design, so the cheaper production judge can be measured against it.
- **What it tells us:** It shows how much a reference adds and how close the cheap judge gets to the best design. Result: done. The reference raises accuracy on decidable pairs from 0.846 to 0.879, and from 0.65 to 0.75 on the strongest models. The cheap judge (0.865) sits about 1.4 points below this ceiling, recovering about 95% of it at a fraction of the cost. Later ruled history rather than evidence, because it ran on the older question pool.

#### J2-D — two references on the disagree stratum (~1.4k Mistral calls)

- **What it tests:** On matches where the models disagree, it gives the judge two reference answers instead of the single strongest one (about 1,400 calls).
- **Why:** It tests whether adding a second reference improves judge accuracy.
- **What it tells us:** A gain would argue for multi-reference judging. Result: null, with a negative direction. Two references scored 0.748 against 0.774 with the best single reference (not significant). The second reference dilutes a good one and helps only when the second model was right. One strongest reference only, and this line is closed. A later ruling classes this run's judged data as history, not evidence.

#### J6 — are the rubrics just not good enough? Frontier-written and contrastive (wrong-answers-in-view) anchor rubrics ...

- **What it tests:** Mistral-induced rubrics were compared with rubrics written by a frontier model and with 'contrastive' rubrics built with wrong answers in view. The Mistral judge used each one, over about 6,000 jobs.
- **Why:** It tests whether better-written grading rubrics make the judge more accurate.
- **What it tells us:** A gain would make rubric authorship worth investing in. No gain would close that line. Result: done. No gain. Contrastive rubrics were slightly worse (-1.8 points, p = 0.043), and frontier-written ones were not significantly different. Rubric text is not the lever. The run had no pool check at run time; one was added afterwards. Later ruled history rather than evidence, because it ran on the older question pool.

#### JUDGE-2x2 — is the judge limited by its own ability to solve the question, or only by the reference? (zero calls; the ...

- **What it tests:** No calls. Judge accuracy on discriminating questions was split four ways: whether the judge model could solve the question itself, crossed with whether the reference answer was right. Done for the pairwise and grading formats.
- **Why:** It asks whether a cheap judge must be smart enough to solve the question, or only needs a correct reference.
- **What it tells us:** If judge ability mattered at a fixed reference, cheap judges would be risky. If only the reference matters, a cheap judge plus a good reference is enough. Result: done, descriptive. With the reference held fixed, judge ability made no difference (for example 0.78 vs 0.80 accuracy when the reference is right). A wrong reference drives accuracy down sharply. This supports the cheap-judge design. Note: older question pool, ruled 'history, not evidence'.

#### JUDGE-BY-CELL — is there any cell in which one cheap judge beats another by more than the test-retest floor, stably across ...

- **What it tests:** On 9,123 matches judged by two cheap judge models (Mistral-Large-3 and two runs of grok), it checks, per MMLU-Pro subject area, whether one judge beats the other by more than the judge's own retest noise (5.7 points). It also checks whether picking the best judge per cell beats using one judge everywhere. No calls.
- **Why:** Earlier work found that the recipe, not the judge model, carries the gain. This test checks whether that still holds cell by cell, or whether judges should be routed by query type.
- **What it tells us:** A stable per-cell winner would reopen judge choice as a property of the cell. Result: done. On the 7 subject areas with enough questions to score, no judge wins beyond the noise bar (largest gap anywhere 3.2 points, not significant). The other 7 areas are undetermined because they have too few questions. Choosing a judge per cell loses 0.1-0.2 points against the single best judge. Judge routing by cell is closed for this pair of judges and this recipe, on the scored areas. Later ruled history rather than evidence, because it ran on the older question pool.

#### JUDGE-SOLVED-SPLIT — on K46-KEY-READ's key-decidable ONE matches, does key accuracy depend on whether the judge model solved the ...

- **What it tests:** On 414 matches where the answer key decides the winner and the judge's reference answer is right, it compares the judge's accuracy on questions the judge model can solve itself with its accuracy on those it cannot. No judge calls.
- **Why:** It checks whether a cheap judge is enough once it gets a correct reference, or whether the judge's own competence still matters.
- **What it tells us:** A clear gap would mean judge competence matters even with a right reference. No gap at adequate power would support cheap judges. Result: done, undetermined. The difference is +2.0pp with an interval from -4.7 to +8.0pp. This is not shown either way at this sample size and must never be read as 'judge ability makes no difference'. Descriptive only.

#### JUDGE-TRANSFER — does the widener transfer across JUDGE families? (zero calls)

- **What it tests:** Takes the uncertainty-widening parameters fitted on one judge (Mistral) and applies them unchanged to verdicts from a different judge family (grok). It also refits them on grok, using stored verdicts only.
- **Why:** It tests whether the confidence calibration is specific to one judge or carries over when the judge is swapped.
- **What it tells us:** Transfer would mean calibration need not be redone per judge; failure would mean it must be. Result: inconclusive. The grok refit falls inside the Mistral interval, but the estimate is weakly pinned down. The error rate at the operating point could not be measured (0 errors among 354 calls), although a large failure was ruled out. Nothing supports 'Mistral-specific', and transfer at the operating point is not established. It was later superseded by grok's own calibration, and ruled history rather than evidence (older question pool).

#### JUDGE-WIRING-BOARD — JUDGE-WIRING's consequence discharged: the x12 MAIN schedule re-judged through the Kotlin production path on ...

- **What it tests:** The full 12-model match schedule (9,123 matches with a reference, 18,246 calls) was re-judged through the actual production Kotlin code path with the shipped judge, and compared with the earlier Python-judged results.
- **Why:** An earlier smaller check had failed to match the two paths, so the production pipeline had no board of record of its own.
- **What it tells us:** Agreement shows the shipped code behaves like the research code, so production rankings can be trusted. Divergence would mean a wiring problem. Result: done, descriptive. On the large set the two paths agree within the judge's own noise (+0.4 / +0.2 points), so the earlier failure was a small-sample effect, and this run is now the production board of record. A side finding: one statistical parameter of the confidence formula was identified on one draw of the same judge on the same data but not on another, so it is fragile on a single draw. Pooling both draws reaches the registered bar but not a stricter honest test (p about 0.07). Later ruled history rather than evidence, because it ran on the older question pool.

#### K46-KEY-READ — key-decidable accuracy of the recipe as ARCH-V2-PILOT-K46 posted it, by reference class ONE / NONE, on the ...

- **What it tests:** It re-read the verdicts of the 37-model pilot on clean, content-disjoint data. It counted how often the judge picked the answer-key-correct side, with and without a reference answer. The bar was 0.80 with a reference. No calls were made.
- **Why:** It checks whether the judge recipe actually used in the new pilot is accurate enough to plan on.
- **What it tells us:** Below 0.80 would withdraw the older accuracy figure used for pricing future boards. Above it keeps that figure. Result: done. 0.879 [0.833, 0.924] with a reference (bar held) and 0.751 without. This depends on the reference being right, which it was 93% of the time. When the reference is wrong, accuracy falls to 0.26, on only 38 matches. The result covers health and math only.

#### KEY-NOISE-CEILING — how much of the arena's remaining error is the key's own noise? (zero calls)

- **What it tests:** Splits the judged questions into two random halves 40 times per subject area. This measures how often the answer key agrees with itself on which model is better, and compares the arena judge's agreement with the key against that ceiling. No calls.
- **Why:** Asks how much of the arena's remaining error is noise in the answer key rather than judge mistakes, and whether judge improvement on MMLU-Pro is exhausted.
- **What it tells us:** Arena close to the ceiling would mean little measurable judge headroom is left. Result: done. The criterion passes on its wording (arena 0.55 points below the ceiling on established edges), but the 'judge line is closed' conclusion does not follow. On those edges the ceiling is near 100% by construction and cannot see the remaining pure judge errors. On all edges, key noise explains 27-54% of the arena's 1.08% error. Arena-pool data, later ruled history, not evidence.

#### KTD-CHECK — FRAMEWORK item 1: the independent check KEY-TIE-DECLINE never had; do the record's integers reproduce and ...

- **What it tests:** An independent recomputation of an earlier result. That result combined a confidence-widening rule with a 'decline to call' rule for deciding which model is better, both overall and per subject. The check also reruns it with 11 random seeds (no judge calls).
- **Why:** The earlier result had never been independently checked, and the framework quoted its error counts.
- **What it tells us:** Matching numbers confirm the record; differences would correct it. Result: it reproduces. Overall, 150 of 190 pairs are called with 0 wrong. Per subject, 1,714 of 2,538 are called with 4 to 5 wrong (about 0.25%) depending on the seed, so the residue sits on a knife edge. The check also corrected the direction of the residual error in the framework: the judge under-rates the Llama-3.1-70B model. Ruled history rather than evidence (older question pool).

#### L1-V2 — truncation under the reference AND the v2 mechanics (~2k Mistral calls)

- **What it tests:** Re-judges a set of matches where one answer was artificially cut short, padded, or left as is. This time the judge prompt says to check the final answer first and never let a wrong final answer win (about 2,000 calls).
- **Why:** Earlier tests showed that judges reward longer, more elaborate answers. This test checks whether a prompt change can reduce that.
- **What it tells us:** It tells whether judge bias toward elaboration can be fixed by changing the instructions. Result: done; the main test passed. The judge picked the correct answer in the cut-short case 43% of the time instead of 35% (+8.3 points, p=0.0002). This is the first causal evidence that a prompt change reduces the bias. Normal accuracy dipped slightly, which is not significant. The automatic adoption threshold was not reached, so adoption is the author's call. This belongs to the older question pool, which is now ruled history, not evidence.

#### LEAF-POWERED — does a leaf-level rubric beat the anchor-level one? (the cancelled LEAF-SS, run properly, on the four anchors ...

- **What it tests:** About 2,150 verdicts on four subject areas, comparing the judge using a grading guide written for each fine-grained leaf of the tree with the judge using a guide written for the broad subject.
- **Why:** It tests whether making the judge's instructions more specific to each cell improves its accuracy.
- **What it tells us:** A gain would support cell-specific judging. No gain would close that line. Result: done. No gain: 0.934 with the broad guide against 0.931 with the leaf guide. The two guides give the same verdict on 93% of matches and change right-or-wrong on only 2% of the decidable ones, so a leaf guide can move accuracy by at most about 2 points. Earlier larger per-subject 'gains' were noise. This was single-order judging on filtered matches, and it compares leaf against subject guides only. Later ruled history rather than evidence, because it ran on the older question pool.

#### LOW-AGREEMENT — what predicts the errors the fitted budget is blind to? (zero calls)

- **What it tests:** It looked at the judge's remaining errors that the fitted uncertainty budget misses. Several signals available without the answer key were tested as predictors, including trace-length difference and confidence. No calls were made.
- **Why:** It looks for a second warning signal for when the arena's call is wrong.
- **What it tells us:** A working predictor would let the uncertainty margin flag more errors. Result: done, descriptive, after a correction. The registered predictor failed. A reported one turned out to be the outcome in disguise. The premise was also wrong: the errors were not low-agreement ones. No second warning channel is supported; there were only six events. Older p2dca data family: history, not evidence.

#### MAXT-MULTIPLICITY — FRAMEWORK item 6: the max-t simultaneous critical value per cell, and how many ORDERED edges survive a ...

- **What it tests:** Computes a stricter threshold that controls errors across all model pairs at once, from existing resamples on four boards. It then counts how many model orderings survive it. No judge calls.
- **Why:** Checks whether the published tier maps of models still hold when many pairwise comparisons are corrected for together.
- **What it tells us:** A big loss of orderings would weaken the leaderboard tiers. Little loss would confirm them. Result: delivered as a readout. The predicted 15-25% drop only appears under a mixed reading that compares quantities on different scales. Under consistent readings the drop is at most 14%, and the main tier map does not change. Which statistic the framework rule should use is still open. This test belongs to the older question pool, so it now counts as history, not evidence.

#### OOS-TREE-CELLS — do INTENT-S1's anchor-free tree cells (C-AF) detect CLINC oos_plus OOS as well as flat k-means at matched k ...

- **What it tests:** On the CLINC intent dataset, uses the anchor-free tree's cells (139 leaves, built without labels) to flag out-of-scope queries. It compares this with flat k-means using the same number of clusters.
- **Why:** It asks whether the tree can support abstention (saying "this question is outside what we cover") as well as flat clusters can.
- **What it tells us:** If equivalent, the tree can be used for both routing and abstention. Result: done. The two are equivalent within the ±0.01 margin. Tree cells are very slightly worse (about 0.005 lower detection score, a difference that is statistically real but tiny). One dataset, one embedder, one draw.

#### ORACLE — what survives a PERFECT reference? Give the judge the answer key and see whether the frontier resolves (596 ...

- **What it tests:** On 302 hard questions where two frontier models differ, the judge was given the true answer key as its reference instead of a grok-written reference, with everything else unchanged (596 calls).
- **Why:** It measures how much judge error comes from imperfect references versus the judge itself, and whether a perfect reference resolves the frontier ordering.
- **What it tells us:** A big gain that recovers the right order would say references are the bottleneck. A residual error would point at the judge's own behaviour. Result: done. A perfect reference raised accuracy from 61.2% to 77.7% but still did not recover the correct order of the two models. Most remaining errors were ties, and committed errors mostly favoured the longer answer. The judge's own error was the larger part, so 'the reference is the binding constraint' is too strong. Later ruled history, not evidence, for the current thesis (old data family).

#### ORACLE-BOARD — what is the ceiling of ANY reference on the x12 schedule? (zero calls; the answer key used as the verdict)

- **What it tests:** Re-scores the recorded 12-model arena schedule with the answer key as the verdict: the correct model wins, and undecidable pairs are ties. It then compares this with the real judge boards. No calls.
- **Why:** Sets the best result any judge or reference could reach on this schedule, so judge results have a fair yardstick.
- **What it tells us:** Tells how much of the gap to the truth the deployed judge closes. Result: the ceiling is a perfect order (rank correlation 1.0, top 4 exactly right). The deployed judge recipe closes about 43% of the remaining gap in rank correlation and half the top-4 disorder. This is a bound, not a reachable target, and it comes from an older judged set now classed as history.

#### PAIR-NOREF — does FORMAT-REF's displacement finding hold in the PAIRWISE format the arena actually deploys? (1,882 calls)

- **What it tests:** Re-judges 944 head-to-head matches in both orders with the reference answer removed from the judge prompt, everything else identical, and compares with the version that has the reference.
- **Why:** An earlier finding was that a reference makes the judge stop thinking for itself when grading single answers; this checks it in the head-to-head format the arena actually uses.
- **What it tells us:** It shows whether that 'displacement' carries over to comparisons and how much the reference is worth. Result: done; displacement does NOT replicate in head-to-head format (the reference outweighs rather than replaces the judge's own reasoning); the reference adds +12.6 points of accuracy, but about 74% of that comes from the judge declaring fewer ties. On the older p2dca question family, later ruled 'history, not evidence'.

#### PLACEBO-ENTRY — does the ARENA-13 protocol inflate whoever enters through it, and is the +0.045 residue real at all? (arm A ...

- **What it tests:** Asks whether the protocol for adding a new model to the arena inflates the newcomer's score, and whether a small +0.045 advantage seen earlier is real. One arm uses existing data, the other 1,192 judge calls.
- **Why:** It checks that the leaderboard is fair to models that join later.
- **What it tells us:** Inflation would mean the entry protocol biases rankings. Result: not confirmed, but the test was under-powered, so this is absence of evidence. The +0.045 gap's interval includes zero, so there is no residue to explain. It led to a rule: any rank-based pass/fail needs a resolution check first. A later ruling classes this run's judged data as history.

#### POINTWISE — the thesis's founding bet, tested directly for the first time: is a judge more reliable comparing two answers ...

- **What it tests:** Compares two ways of using an LLM judge on the same answers: grading each answer alone on 0-100, versus comparing two answers head to head. One arm uses a reference answer and one does not (about 7,400 graded answers).
- **Why:** It tests the thesis's founding bet, that judges are more reliable comparing than grading. The test was set up so the thesis could lose.
- **What it tells us:** Pointwise winning would undercut the pairwise design. Result: done, split verdict. Comparing is better for deciding a single match (0.864 vs 0.808, significant). Grading gives a slightly better overall leaderboard (rank correlation 0.993 vs 0.979). Both effects replicate without a reference. The leaderboard advantage did not replicate on small per-area samples. Working rule: grade where answers are checkable, compare where they are not. Later ruled history rather than evidence, because it ran on the older question pool.

#### POINTWISE-REPL — does the pointwise board advantage replicate at anchor scale? (zero calls)

- **What it tests:** Compares grading each answer alone with comparing two answers side by side, separately within each of 13 subject areas. Each format is scored against that area's own answer key. No judge calls.
- **Why:** Checks whether grading's overall edge over side-by-side comparison holds inside individual subjects.
- **What it tells us:** Shows whether one judging format is best everywhere or depends on the type of question. Result: the edge does not replicate per subject. Grading wins 4 areas, comparison 8, with 1 tie. Grading wins where answers are checkable (math, sciences, engineering), and comparison wins in discursive fields (law, history, philosophy). Small per-area samples are noisy. This test belongs to the older question pool, so it now counts as history, not evidence.

#### POOLED-RESTATE — FRAMEWORK item 4 (review verify item 7): restate the pooled gate-vs-widener comparison on the board of ...

- **What it tests:** Re-scores, on the merged 20-model board, two rules for deciding which model pairs the board may call as ordered: a fitted uncertainty widener and an agreement gate. It compares wrong calls at a matched number of withheld pairs. No calls.
- **Why:** An earlier claim that the gate always beats the widener had to be rechecked on the board of record.
- **What it tells us:** It decides which safety rule to ship for declaring 'A beats B'. Result: the widener (with declines) wins. It makes 0 wrong calls against 2 to 3 for the gate at matched withholding, in 20 of 20 settings. This rests on only five wrong events and is not a significance result. The 'gate dominates' claim was dropped. Later ruled 'history, not evidence'.

#### POSITION-DECOMP — how much of the ARENA-13 over-ranking is the slot the model sat in? (596 calls)

- **What it tests:** Re-judges 600 frontier matches with the two answers in swapped order. It uses repeats of identical prompts to separate how much verdict flipping is due to answer position and how much is plain judge noise. Uses 596 judge calls.
- **Why:** A new model seemed over-ranked in an earlier arena, and the question was whether presentation order (position bias) caused it.
- **What it tells us:** Position bias above noise would mean arenas must judge both orders. Result: about half the 12% flip rate is position (about 7 points) and half is noise (about 6 points). The newcomer wins 70% when shown first vs 56% when shown second. Its lead shrinks a lot but it still ranks first. Practical rule: new arena extensions must judge both orders. Ruled history rather than evidence (older question pool).

#### POSITION-FULL — balance the remaining 1,200 cross-tier matches: does the newcomer fall to 2nd once ALL of arm A is dual ...

- **What it tests:** Re-judges the remaining 1,200 matches between models of different strength with the answers shown in the opposite order, so all matches are judged in both orders (1,196 calls). It checks whether the newcomer model's ranking holds and how much answer order sways the judge.
- **Why:** It asks whether the judge's preference for the answer shown first is distorting rankings, and where that bias shows up.
- **What it tells us:** It shows where order bias matters and whether a single order is safe. Result: done. Flips between orders are rare in matches between models of clearly different strength. They sit at the level of judge noise, compared with 18% among top models. Order carried about 85% of the newcomer's lead, but it still ranks first. The gap is not distinguishable from zero. A later correction: the bias tracks matches that lack decisive evidence, not "frontier versus not", so there is no cheap subset that can safely be judged in one order only. This belongs to the older question pool.

#### POSITION-INDEX-ALL — across every CERTIFIED dual-order cache, among order-flips whose two votes are both decisive, what share name ...

- **What it tests:** Each match is judged in both orders. Across all certified caches, it looks at cases where the verdict flipped with order, and measures what share favoured whichever answer was shown first, per benchmark and judge.
- **Why:** A tool-use benchmark (BFCL) showed flips going entirely one way. The question was whether that kind of position bias is general.
- **What it tells us:** If one-sided flips are general, dual-order judging is needed everywhere and the BFCL pattern is not special. Result: done. All five supported families showed one-sided flips, but in opposite directions by judge: grok favours the first answer, Mistral the second. The general conclusion rests on MATH, only slightly above even, from one of its two caches. BFCL's total one-sidedness is not typical. It says nothing about why judges prefer a position or about individual matches. The MMLU-Pro caches come from the older question pool, later ruled history rather than evidence; the BFCL part is not affected.

#### PROFILE-INTERVAL-ALL — FRAMEWORK item 9: the reliability crossing published as a range and a per-anchor certifiability list with ...

- **What it tests:** Putting uncertainty intervals on every reliability number of the per-subject model profiles. It reports how many questions per subject are needed for a reliable profile, and which of 14 MMLU-Pro subjects reach the reliability bar.
- **Why:** Per-subject profiles are only trustworthy if their reliability is shown with intervals, not as point values.
- **What it tells us:** Result (no new calls): delivered. Physics and Math pass. Seven subjects pass only within their intervals. Engineering, Biology, Computer science, Economics and Health fail. The failing set is not simply the smallest subjects. At about 120-130 questions per subject, a per-subject deviation row cannot be certified. Later disclosure: the tree used for routing had about 6.7% of the routed questions visible during construction. It is on older judged data now ruled history.

#### PROFILE-RELIABILITY — is the ANCHOR-level capability profile reliable, and at what cell size does reliability arrive? (zero calls)

- **What it tests:** Measures how reproducible a model's capability profile across cells is (split-half reliability) at leaf level and at anchor/domain level, and how many questions per cell reliability needs. No calls.
- **Why:** It decides whether per-cell capability claims from the judge can be published as measured quantities.
- **What it tells us:** Reliability of at least 0.70 would allow per-cell claims. Result: done. The anchor profile misses the bar (0.67 vs 0.70; leaves 0.26), so per-anchor judge profiles may not be published as measurements. About 210 questions per cell are needed, and anchors average 201. The answer-key profile is far more reliable. A later ruling classes the judge parts as history; the answer-key parts are not affected.

#### PROMPT-AUDIT — is the eval set's own ranking, the ground truth everything validates against, confounded by prompt ...

- **What it tests:** Measures how much the prompt setup changes a model's score on the evaluation set. The same model answers the same 3,430 questions under two prompts. It also catalogues which prompt setups the leaderboard entries declare. No judge calls.
- **Why:** The eval set's ranking is the ground truth everything is validated against, so it must not be an artefact of prompt choices.
- **What it tells us:** A large prompt effect would make close frontier gaps unreliable. A small one would make them safe. Result: the ground truth is not materially affected by the prompt. The effect is about 1 point (-0.010 ± 0.004), not the 4.6 points an earlier faulty probe claimed. All frontier gaps are safe, with arx vs iask marginal. Whether gemini's 5-shot setup inflates its score cannot be tested here.

#### RECIPE-GROK — does the STACK-v2 recipe carry over to a second judge family, or was the gain Mistral-specific? (3,956 calls)

- **What it tests:** Runs the production judge recipe (same reference answers, mechanics and rubric) with a different judge model family, grok, on 1,980 matches. It compares the result with grok's old-recipe verdicts and with the Mistral judge. About 4k calls.
- **Why:** It asks whether the judge's accuracy gain comes from the recipe or from the particular judge model (Mistral).
- **What it tells us:** If grok gains as much, the recipe carries the gain and cheaper or other judges can be swapped in. Result: done, passed. Accuracy is 0.864 with the recipe against 0.744 without it, and 0.722 against 0.568 on the top cluster. This is nearly identical to Mistral (0.865 / 0.699) and gives the same leaderboard. A later cell-level check found per-subject gaps of at most 3.2 points, each with an interval that includes zero. Under this recipe the judge model accounts for only about 3% of committed verdicts. Older judged question family, later ruled 'history, not evidence'.

#### REF-CHECKLIST — a per-question verification checklist (facts and steps a correct answer must contain, no answer) as a ...

- **What it tests:** Compares three judge setups on 826 matches with a known key: (a) a reference answer, (b) a checklist of facts and steps a correct answer needs, without the answer, and (c) both. Uses about 5,700 calls.
- **Why:** Reference answers help the judge but leak the answer. This tests whether a checklist gives the same help with less leakage, or rescues cases where the reference is wrong.
- **What it tells us:** A useful checklist would offer a safer reference format; a useless one shows that the value is in the answer itself. Result: failed. The checklist adds about +1.6 points (not significant) against +11 for the answer, and it does not rescue cases where the reference is wrong. The value of a reference is its correct answer, and its leakage is the price of that value. Ruled history rather than evidence (older question pool).

#### REF-CONF — can a reference that reports its own confidence let the judge discount weak hints? (B7 mitigation; ~2.8k ...

- **What it tests:** A strong model re-solves about 2,800 questions and reports its confidence. The judge then sees this reference answer with or without the confidence, over about 2,000 matches (about 7,900 judge calls).
- **Why:** Judges tend to follow a wrong reference answer. The test asks whether telling the judge the reference was unsure helps it ignore weak hints.
- **What it tells us:** It shows whether confidence signals can protect the judge from bad references. Result: done. The confidence itself was informative (AUC 0.80), but showing it to the judge changed nothing. The judge follows a wrong reference about 2 times in 3 either way. This line of fixes is closed; only a more accurate reference helps. This belongs to the older question pool, which is now ruled history, not evidence.

#### REF-FORM-BY-CELL — on the quantitative anchors, does a reference of a stronger FORM (a program-of-thought solve, executed ...

- **What it tests:** On 597 quantitative questions (math, physics, chemistry, engineering), the reference model wrote a Python program that was executed in a sandbox, and its answer was compared with the usual cached reasoning reference.
- **Why:** It tests whether a stronger kind of reference (computed, not reasoned) would help the judge in quantitative cells.
- **What it tells us:** More correct answers would justify a per-cell reference form and a judged follow-up. No gain closes the idea. Result: done; the judged stage was never run. The program-based reference was right on exactly as many questions as the usual one (464 of 482). The two agreed 98% of the time and often repeated the same mistakes, so the remaining errors are modelling errors, not arithmetic slips. The idea is closed for this corpus. Older question family, later ruled 'history, not evidence'.

#### REF-GATED-RUBRIC — is rubric value CONDITIONAL on the reference being right? (the specific-judges line, redirected; 3,594 calls)

- **What it tests:** A 2x2 judged run (3,594 calls). It compares matches where the reference answer is wrong with matches where it is right, each judged with and without a cell-specific rubric card.
- **Why:** Tests whether a rubric only helps when the judge's reference is correct, which decides whether a cell-specific judge needs a cell-specific rubric or a cell-specific reference.
- **What it tells us:** Tells where to invest to make judges better per cell. Result: the registered interaction test FAILED (not confirmed), largely because of how the samples were drawn. Taken separately, the rubric does exactly nothing when the reference is wrong, and gives a small gain (+1.3pp) when it is right. Direction: a rubric cannot replace a good reference, it can only sharpen one that works. Older judged set, now classed as history.

#### REF-QUAL-KIMI — qualify Kimi-K2.6 as a candidate REFERENCE before buying a full re-judge (569 calls; first attempt VOID)

- **What it tests:** Has Kimi-K2.6 solve 569 questions to see whether it would be a better reference answer source for the judge than the current one.
- **Why:** A better reference should make judge verdicts more accurate; this was a cheap qualifying test before paying for a full re-judge.
- **What it tells us:** A pass would justify a re-judge with Kimi as reference. Result: done. It failed the gate (70.5% vs 72.5% on discriminating questions) and was not promoted. But the comparison was not like-for-like (different prompt and token budget, a design error), so a rule was added that candidates must be solved the same way as the incumbent. A later like-for-like test also found Kimi unusable as reference. Later ruled history rather than evidence, because it ran on the older question pool.

#### REF-QUAL-KIMI-JSON — the matched-protocol re-solve: is a better reference buyable, and is Kimi it? (569 reasoning calls under the ...

- **What it tests:** The test re-solved 569 questions with the Kimi model under exactly the same answer protocol as the current reference model. It checked whether Kimi would be a better reference for the judge, applying gates on accuracy, bias toward one contestant, and failure to finish answers.
- **Why:** A more accurate reference answer is the biggest lever on judge accuracy, so a better reference was worth looking for.
- **What it tells us:** Passing would mean promoting Kimi as the reference. Failing shows which obstacles block a better reference. Result: done. Not promoted: two gates failed. First, Kimi is more accurate (about +4 points), but 6.8% of its answers hit the length limit, above the 5% allowed. Second, it failed the bias gate: it agrees more with the strongest contestant, which follows from being more accurate. The Kimi line is closed. A future bias check should take correctness into account. Later ruled history rather than evidence, because it ran on the older question pool.

#### REF-QUALITY-MONITOR — is per-cell reference-correct rate the continual per-cell quality signal? with DIFFICULTY-PROXY-WIDENER as ...

- **What it tests:** Tests whether the rate at which the reference answer is correct in each cell can serve as an ongoing per-cell judge-quality signal. A secondary check covers a difficulty-proxy widener. No calls.
- **Why:** It asks whether there is a cheap per-cell monitor of judge quality.
- **What it tells us:** A strong link would license a per-cell quality monitor. Result: the correlation held on paper (+0.84), but it is just an identity: the judge agrees when the reference is right. So it monitors difficulty and the reference, not the judge, and it needs the answer key. The secondary check is undetermined. No per-cell judge monitor is licensed. A later ruling classes this run's judged data as history.

#### REF-SC — can self-consistency of the reference model raise the reference ceiling on the hard questions? (free check on ...

- **What it tests:** Two existing independent solves by the reference model were compared, to see whether a majority over more samples could raise its accuracy on hard questions. No calls were made.
- **Why:** It decides whether a paid third sample is worth buying to strengthen the judge's reference.
- **What it tells us:** Large disagreement would mean voting could help. High agreement would mean it cannot. Result: done. The two solves agree 94% of the time, so a majority of 3 would gain about nothing. Only a different family of solver could raise the ceiling. The paid test was not run. Older p2dca data family: history, not evidence.

#### RK-1 — does a per-leaf verification kit (knowledge card + failure catalogue + 2 worked neighbours, induced on ...

- **What it tests:** Gives the LLM judge a per-cell verification kit: a knowledge card, a list of common failures and two worked neighbour examples. It compares judge accuracy with and without the kit on 944 key-decidable matches. About 8,000 judge calls.
- **Why:** Tests whether cell-specific background material makes the judge more accurate than the existing best recipe.
- **What it tells us:** A gain would show that the taxonomy can improve the judge itself. No gain would close this route. Result: failed. The gain was +0.7 points (p = 0.39), with a +4.1-point hint in the top cluster that is not significant. There was no difference between quantitative and discursive questions. A later review put the honest estimate near +1.3 points because of control noise. The run had no question-pool check at the time. Later ruled history rather than evidence, because it ran on the older question pool.

#### RK-1b — does a DATA-ONLY leaf card (answer form, distractor spacing, numeric error signature, <= 6 conceptual ...

- **What it tests:** Adds a 'data card' for each leaf, built only from data (answer format, distractor spacing, numeric error patterns, common misconceptions), to the judge prompt. It is compared with the plain production judge on 1,980 matches. About 8k calls.
- **Why:** It checks whether cell-specific context built from the tree makes the judge more accurate at no extra induction cost.
- **What it tells us:** A gain would show the tree's cells can improve judging itself. Result: done, passed as registered: +1.7 points on decidable matches (0.875 vs 0.858), larger on quantitative cells. Later restated: most of the gain comes from the judge abstaining (saying 'tie') less often, not from better discrimination. After correcting for the twelve rubric tests it is not significant (adjusted p 0.35), and the honest estimate is about +1.3 points. A tie-break method replaces it. Older p2dca question family, later ruled 'history, not evidence'.

#### RK-1b-GROK — does the data-only leaf card's gain transfer to a second judge family (as the recipe did)? (7,912 calls)

- **What it tests:** Gives the grok judge a short data-only description card of the question's leaf, or no card, on the same 1,980 matches (7,912 calls). It measures accuracy against the answer key.
- **Why:** It checks whether a gain first seen with Mistral carries over to a second judge family.
- **What it tells us:** Transfer would mean leaf context helps judges in general. Result: the main test failed by its own rule (+1.3 points, p = 0.073). The direction and size match the Mistral result. A later re-analysis found the gain mostly comes from the judge abstaining less, not from judging better, and it does not survive multiple-testing correction. Later ruled 'history, not evidence'.

#### RK-1c — RK-1b plus two worked neighbours whose solutions are the reasoning model's key-verified solves of TRAIN-side ...

- **What it tests:** Adds two worked example solutions from similar training-side questions to the judge's prompt, on top of the cell card, and compares accuracy on 944 matches with a known key. About 8,000 calls.
- **Why:** It tests whether showing the judge solved neighbouring problems improves its verdicts beyond the cell card.
- **What it tells us:** A gain would support adding worked examples; no gain closes that line. Result: failed. Accuracy went from 0.859 to 0.868 (+0.8 points, not significant). Once the judge has a reference for the question itself, worked solutions to other questions add nothing, and this line of judge-prompt additions was closed. Ruled history rather than evidence (older question pool).

#### RUBRIC-512-R — cell rubric value for the REASONING judge (~8k calls; both arms fresh in one session)

- **What it tests:** Judges about 1,980 matches twice with the reasoning version of grok: once with a rubric written for each cell of the tree and once with the generic rubric, then compares accuracy on questions with a known answer.
- **Why:** Checks whether cell-specific rubrics help a stronger reasoning judge, after they gave little to a weaker judge.
- **What it tells us:** A gain would justify per-cell rubrics; none closes that line. Result: done; exactly zero gain (84.2% vs 84.2%). Together with other tests, cell rubrics are worth 0 to +1 point on keyed questions; the rubric line was closed. On the older p2dca question family, later ruled 'history, not evidence'.

#### RUBRIC-HIDDEN — did the rubric tests hide a real per-leaf effect, through the pairs they discarded or through pooling? (zero ...

- **What it tests:** Using no new calls, the test re-read earlier rubric experiments. It checked whether a rubric makes the judge abstain on the undecidable pairs those tests had discarded. It also checked whether pooling across subjects hid real effects in individual subjects.
- **Why:** Earlier tests found little value in rubrics, and the question was whether that verdict was an artefact of how they were analysed.
- **What it tells us:** It tells whether the negative rubric result can be trusted or needs a cleaner test. Result: done. The first explanation was refuted: with or without the rubric, the judge still invents a winner on about 60% of undecidable pairs and still prefers longer answers. The second stayed open: each subject had too few pairs to test effects of the size observed, so per-subject effects could not be tested one by one. This led to LEAF-POWERED, which settled it. Later ruled history rather than evidence, because it ran on the older question pool.

#### STACK — the assembled judge v2, end-to-end (~4k Mistral calls)

- **What it tests:** The full new judge was run end to end on about 2,000 matches. It combines a production template, a reasoning model's reference answer, a subject-level rubric, judging in both orders, and confidence scores. Six pass/fail checks were set in advance.
- **Why:** It tests whether the assembled cheap judge is good enough to be adopted as the production judge.
- **What it tells us:** Passing would let the design be adopted. Any failed check marks a remaining weakness. Result: done. 5 of 6 checks pass: accuracy 0.843, a large gain over the old judge (+7 points), and fewer ties, flips and length bias. The ranking check failed: two order errors among the top 4 models, against 1 allowed. The design was still registered as the next version (STACK-v2). Later ruled history rather than evidence, because it ran on the older question pool.

#### STACK-NORUBRIC — FRAMEWORK item 20: the recipe WITHOUT the anchor rubric; what does a cell with no induced rubric lose? (2,100 ...

- **What it tests:** Runs the judge recipe without the cell's LLM-written rubric (2,100 calls) and compares it with the recipe that has the rubric.
- **Why:** It measures what a cell loses when it has no induced rubric, which tells whether rubrics are worth their cost.
- **What it tells us:** A big loss would make rubrics essential. A small loss would allow rubric-free deployment. Result: as predicted, not worse. The rubric adds about 1.5 points of decisiveness (fewer ties, p = 0.044) and no real accuracy in telling models apart (+0.2, within noise). A later ruling classes this run's judged data as history, not evidence.

#### STACK-v2 — the assembled judge with the v2 verify-first mechanics (~4k Mistral calls; registered 2026-09-10 02:15)

- **What it tests:** The assembled Mistral judge was run with a 'verify first' system prompt on 1,980 matches (about 4,000 calls). It was scored on six registered checks against the answer key.
- **Why:** It tests whether this judge configuration is good enough to become the production judge.
- **What it tells us:** Passing would make it the recipe for later judged tests. Result: done, registered primary check passed. Accuracy is 0.865, the best Mistral configuration. The top-4 order has 1 violation. It beats the earlier judges (+1.6 and +9.3 points). The order-flip rate, 13.9%, misses its guard by 1.1 points and is disclosed. It does not settle the order at the very top. Older p2dca data family: history, not evidence.

#### STAGE3-MATH-CAPFREE — FRAMEWORK item 23 re-registered on the population the framework's own rules admit: the cheap judge with a ...

- **What it tests:** Measures the cheap judge's accuracy against the key on MATH, 8 models (5,992 calls). The judge gets an exact checker reference answer. Responses cut off by the 1,024-token generation cap are excluded (83.5% of question pairs kept).
- **Why:** The unfiltered MATH cell failed the accuracy bar because truncated answers polluted it. The test asks whether the judge is reliable on the population the framework's rules admit.
- **What it tells us:** Passing shows the cheap judge is accurate when it has an exact reference. Result: done, passed (0.958 accuracy, bar 0.75). Comparing this with MMLU-Pro's 0.85 is only a positioning, not a measurement: corpus, models and reference type differ, and the excluded rows were mostly wrong answers. It says nothing about the truncated responses or about calibration.

#### SYSTEMATIC-BUDGET — fit the continuous widener SYSTEMATIC-SIGNAL licensed; does a fitted systematic budget calibrate the ...

- **What it tests:** Fits four candidate forms of an extra uncertainty margin ('systematic budget') for the board's 'A beats B' certificate, using 891 model pairs with 44 known-wrong directions. Each form is checked by leaving one category out at a time. No calls.
- **Why:** The raw certificate was overconfident, so the test asks whether a fitted margin can make it honest.
- **What it tells us:** Adopting a calibrated margin would make 'A beats B' calls trustworthy. Result: a two-parameter margin was adopted. It cuts the overconfidence from 9.7x to 2.4x, a level no longer detectable (3 events), but it is not shown to be calibrated. As predicted, it withdraws a disputed top-pair call. Transfer to other boards or judges is undetermined. Later ruled 'history, not evidence'.

#### SYSTEMATIC-SIGNAL — can a free signal predict where the bootstrap is confidently wrong? (the fix for TIER-HONEST's flaw; zero ...

- **What it tests:** On 891 subject-by-model-pair comparisons, checks whether signals available without extra calls predict where the arena is confidently wrong about which model is better. The signals are how often the two models give the same answer, and how accurate the reference is.
- **Why:** Confidence intervals were sometimes confidently wrong. This looks for a cheap warning signal to widen uncertainty where errors are likely.
- **What it tells us:** A predictive signal would let the system flag risky comparisons; none would leave those errors hidden. Result: confirmed as stated, but corrected. High answer agreement between the two models predicts wrong calls. Reference accuracy also predicts them, but it needs the answer key, so only answer agreement can be used in practice. As a hard cut-off the signal is poor, so it is used as a continuous widening instead. Ruled history rather than evidence (older question pool).

#### TEMP-0 — is the 5.7% test-retest floor a property of LLM judging, or a sampling default nobody set? (598 calls)

- **What it tests:** Re-judges 299 identical matches twice at temperature 0, meaning no sampling randomness (598 calls). It then checks whether the judge's 5.7% disagreement with itself goes away.
- **Why:** No judge call had ever set a temperature, so the judge's self-disagreement might have been a setting nobody chose, not a property of LLM judging.
- **What it tells us:** If disagreement vanished, earlier noisy results would need re-reading and a cheap fix would exist. Result: done. Disagreement stayed about the same (5.0% vs 5.7%). Temperature changes the wording of the judge's reply, not its decision. So the roughly 5% noise floor is real, and nothing measured earlier is invalidated. Differences under about 3 points cannot be read reliably. This belongs to the older question pool.

#### TIE-MECHANICS — is the canary's 'every retest disagreement sits at the tie boundary, and no decisive match reverses' a ...

- **What it tests:** In a repeated judge run (300 matches, each judged in both answer orders, run twice), it counts how often both order votes of a match changed together. It compares this with what independent random vote changes would predict. No calls.
- **Why:** Checks whether "retest changes only happen at ties" is just arithmetic from independent per-call noise, which would justify computing match-level noise floors from a single per-call rate.
- **What it tells us:** If independence held, noise floors could be derived cheaply. Result: it failed. Both votes changed together 10 times against about 3 expected, so changes cluster within matches. No match-level noise floor may be derived from one pooled per-call rate. It cannot tell real within-match dependence apart from some matches simply being shakier. No recorded number moves. Older judged question family, later ruled 'history, not evidence'.

#### TIER-HONEST-X20 — does the finding the entire budget line rests on (within-tier separations disproportionately wrong ...

- **What it tests:** Re-testing, on a 20-model board with three times as many model pairs, an earlier finding about the judge's errors. The finding was that orderings between near-tied models are disproportionately wrong, while orderings across clear tiers are error-free.
- **Why:** The budget line rested on that finding, so it needed replication.
- **What it tells us:** Result (no new calls, corrected): only partly replicated. Overconfidence on near-tied pairs and one specific inversion (arx vs iask) replicate. 'Near-tied orderings are disproportionately wrong' does not (1 of 6 vs 4 of 176 once a stricter test is applied). 'Across-tier is error-free' holds on the original roster but fails on added models. The earlier dramatic headline is superseded. It is on older judged data now ruled history.

#### TOPIC-DIFFICULTY — does a difficulty axis inside a cell change the judge and the model order? (zero judge calls)

- **What it tests:** Re-reads about 21,500 existing verdicts (no new calls), splitting each cell's questions into easy, middle and hard thirds, and compares judge accuracy, ties, length preference and model order between easy and hard.
- **Why:** Tests whether a single per-cell ranking is misleading because the judge behaves differently on hard questions within the same cell.
- **What it tells us:** A difference would require difficulty-split rankings. Result: done; judge accuracy drops 15.5 points on hard questions, but 72-79% of that is because the reference answer is more often wrong there, not a new judge effect; no reliable length or model-order difference; every difficulty-split ranking is undetermined. On the older p2dca question family, later ruled 'history, not evidence'.

#### TRACE-TRUNCATION — is a judge holding an exact outcome reference an outcome judge, or still a reasoning-content judge? (ceiling ...

- **What it tests:** The judge was given the exact correct final answer as a reference. The correct answer's reasoning was then cut down to its final line. The test checked whether verdicts change, using 360 MATH pairs and about 2,200 calls, with a control that pads the text back with spaces.
- **Why:** It asks whether a judge with an exact reference just checks the outcome or still reacts to the reasoning text.
- **What it tells us:** No drop would make it an outcome judge. A drop would mean the reasoning still matters. Result: done. Accuracy fell from 0.983 to 0.914, mostly into ties rather than wrong verdicts. Whether this crosses the 0.10 bar is undetermined. The 0.70 floor held. Padding hurt even more, so the effect reads as sensitivity to edits, not to content. It is not shown to be an outcome judge.

#### UNFILTERED-ADOPT — FRAMEWORK item 3: adopt the unfiltered 920-edge widener fit in place of the 891 filtered one? (zero calls)

- **What it tests:** Refits the confidence formula for ranking calls on all 920 model pairs instead of the 891 filtered pairs. It then checks whether quality, utility and error rate hold. No judge calls.
- **Why:** Using all pairs avoids a hidden selection, making the method's reported population honest.
- **What it tells us:** Shows whether dropping the filter costs anything. Result: 3 of 4 criteria met, with the same error counts and about 70% utility. The fourth check was not met because the main script does not yet print that row, so adoption is not confirmed. The change makes the reported population honest but brings no accuracy gain (18 correct calls given up, 0 wrong ones removed). This belongs to the older question pool, which is now ruled history, not evidence.

#### V2-NONE-TEMPLATE — V2-NONE-TEMPLATE (RP20) with its ONE leg REF-PAIRED-V2: the price of the v2 system turn's false 'carries a ...

- **What it tests:** Two parts. (1) On 1,846 matches judged without a reference, the judge prompt wrongly said 'the question carries a reference solution'. Those matches were re-judged with a corrected sentence. (2) On 818 matches, the judge was run with vs without the cached reference. Paid run: 10,656 calls, done on the author's go.
- **Why:** It checks whether a false prompt sentence corrupted past verdicts, and how much the cached reference is worth under the current recipe on clean data.
- **What it tells us:** Equivalence means past no-reference verdicts can be reused with a disclosure. A large reference effect quantifies how much the judge leans on it. Result: done. The false sentence made no meaningful difference: accuracy stayed within plus or minus 4 points (+1.4, and the 95% interval includes 0), only ties shifted, and past verdicts are reusable with disclosure. Removing the reference cost about 16 points of accuracy (95% interval -21 to -11), mostly decisions turning into ties. That effect bundles the reference with the prompt sentence.

### State: UNDETERMINED (5)

#### AGREE-ORDER — is the reproducible order carried by the same-answer (AGREE) matches the filter removes a LENGTH order, a ...

- **What it tests:** Takes the 8,922 judged matches where both models gave the same final answer, which the filter normally throws away. It asks whether the stable model order these matches still produce comes from answer length, from which side is shown first, or from the models themselves. No new judge calls.
- **Why:** It checks whether the judge's order on 'same-answer' matches is a real ability signal or a length bias that the filter quietly removes.
- **What it tells us:** If length explained it, the filter would be removing a bias. If it did not, the filter would be throwing away real signal. Result: undetermined. Within these matches the judge clearly prefers longer answers. But once the matches are length-matched, too few questions remain to tell 'length' apart from 'too little data'. The order these matches give is basically the usual leaderboard order. A later ruling classes this run's judged data as history, not evidence.

#### BUDGET-TRANSFER — does the fitted widener survive a change of ROSTER? (zero calls; the x12 parameters applied COLD to the ...

- **What it tests:** Takes the formula that decides when a pairwise ranking call is confident enough, fitted on the 12-model board, and applies it unchanged to new pairs on the 20-model board. It counts how often the confident calls point the wrong way. No judge calls.
- **Why:** Checks whether the confidence formula still works when the set of models changes, or only fits the roster it was trained on.
- **What it tells us:** Error rates at or below the promised level would mean the formula transfers. Higher rates would mean it must be refitted for each roster. Result: undetermined, as the registration expected. There were only 2 confirmed wrong calls against about 1.6 expected, which is too few to decide. The formula still made 70% of the possible calls. Two earlier, opposite readings were withdrawn. The formula is published as fitted to one roster, with transfer untested. Later ruled history rather than evidence, because it ran on the older question pool.

#### CERT-CORPUS — FRAMEWORK item 8: the calibration status and the widener's sign and utility on the checker cells (MATH ...

- **What it tests:** Using cached verdicts from a generative arena (MATH and instruction-following, 3,000 verdicts, 8 models), the test asked two things. Is the judge-based certificate's confidence calibrated? Does a correction that widens its uncertainty point the right way and stay useful?
- **Why:** The certificate attached to each cell is only trustworthy if its confidence statements can be checked against answer keys.
- **What it tells us:** A calibrated result would let the certificate be read at face value on these tasks. An undetermined one means there is not enough checkable data. Result: UNDETERMINED everywhere: the data falls about 50x short of what a readable calibration status needs. The correction points the expected way wherever instruction-following is included, but only borderline. On the stricter labels it is not identified. Its usefulness is 85% on MATH and only 33% on instruction-following, below the 60% bar.

#### KEY-TIE-DECLINE — a product rule wherever a key exists: decline any separation whose pair's key direction is not established ...

- **What it tests:** Tests a product rule: decline to declare one model better than another in a cell when the answer key itself does not clearly separate them. It is applied on three leaderboard views, and the test counts how many calls are lost and how many wrong separations are removed. No judge calls.
- **Why:** It asks whether a simple key-based rule removes the remaining wrong 'model A beats model B' claims without giving up too many correct ones.
- **What it tells us:** Low cost with most errors removed would make it worth shipping. Losing more than 25% of calls would make it too blunt. Result: undetermined on the registered criterion, because the target count referred to a board that no longer exists. On the existing board the rule is cheap and works. Combined with the widener it leaves 0 wrong separations on the pooled board while still calling about 150 of 190 pairs. The per-cell residue is 4 to 5 errors in 1,714 calls depending on the random seed, all involving one model (Llama-3.1-70B). The failure condition did not fire. Older judged question family, later ruled 'history, not evidence'.

#### REF-QUAL-GATE3-COND — FRAMEWORK item 12: does the correctness-conditional form of REF-QUAL gate (3) decouple 'agrees because right' ...

- **What it tests:** When a judge model agrees more with a better reference answer, the gain was split into two parts: agreeing because both are right, and agreeing because both are wrong in the same way. Only the both-wrong part was compared with the spread across models.
- **Why:** It asks whether conditioning on correctness can separate 'agrees because right' from 'agrees because the models make correlated errors'.
- **What it tells us:** Result (no new calls): undetermined. Every interval contains zero, and the verdict depends on the reading. The conditional version is as tied to reference accuracy as the plain one. On the both-wrong questions, the models mostly converge on the same wrong option. The plan to use this conditional gate should not proceed. It is on older judged data now ruled history.

### State: paused (1)

#### G17-CANARY — G17-CANARY (RP21): the v2 recipe's within-session and epoch retest floor on a frozen 300-match v2 canary ...

- **What it tests:** Re-posts the exact same 300 judge requests of the new (v2) judge recipe and counts how often the combined verdict changes. A second leg will re-run the older v1 canary set about two weeks later to check for drift. About 1,800 calls are planned in total: 1,200 for the v2 leg (done) and 600 for the v1 leg (pending, not before 2026-10-08).
- **Why:** It sets the judge's own noise floor, so that later changes in verdicts can be told apart from random judge wobble or drift over time.
- **What it tells us:** A low, stable retest rate means verdict changes above it are real; a high one means the judge is noisy. Result so far (paused): the v2 leg is done, and verdicts change on 10% of re-posted matches (about 7% to 13%). This is descriptive only and is a noise floor, not accuracy. The v1 epoch-3 leg and the drift-over-time comparison are still pending.

### State: READY (1)

#### JUDGEBENCH-REASONING-SIDE — on JudgeBench's GPT-4o split (350 correctness-grounded pairs, NO reference), does a reasoning judge ...

- **What it tests:** On JudgeBench's external set of 350 answer pairs (one correct, one wrong by an objective check), with no reference shown, it compares a reasoning version of the grok judge with the standard version, using identical prompts. Per-category differences are descriptive only.
- **Why:** An outside-validity check: does the in-house finding that a reasoning judge is more accurate (+10pp on MMLU-Pro) carry over to an independent benchmark?
- **What it tells us:** A gain would support using a reasoning judge beyond our own data. No gain would refute that carry-over. Result: not run yet. The test is registered and READY, waiting for a launch day; nothing is recorded. Even when run, it says nothing about the deployed recipe, which does use a reference.

### State: withdrawn (1)

#### ARENA-V3 — the adopted judge (STACK-v2 + the data-only leaf card) on all 9,144 arena matches (registered 2026-09-11 at ...

- **What it tests:** Planned to re-judge all 9,144 arena matches with the adopted judge recipe plus a short data-only description card of each question's cell, about 18,300 judge calls, and compare it to the previous arena.
- **Why:** It would have tested whether the cell-description card improves the judge at full arena scale.
- **What it tells us:** A gain would have supported putting cell descriptions into the judge's prompt; no gain would have shown they are not worth it. Result: withdrawn and never run, so there are no numbers. The card's earlier gain was a single positive among twelve tests and did not replicate with a second judge. A cheaper fix (breaking ties with repeated judgments) did the same job better, and the run was 4.5 times over the approval threshold.

## SQ3 Taxonomy

47 tests: is the discovered tree real, stable and better than simpler partitions?

### State: done (43)

#### ANCHOR-FREE — the tree grown from the embeddings alone, no category anchors (one construction, zero LLM calls)

- **What it tests:** One tree was grown from the question embeddings alone, without giving it the dataset's category labels as its first layer. It was compared with the same code run with those labels as anchors. No LLM calls were made.
- **Why:** It tests whether the tree's structure comes from the data or is borrowed from the human category labels it is normally seeded with.
- **What it tells us:** If the label-free tree recovered the categories and still certified structure, the labels would be doing less work than assumed. Result: done. All three registered criteria passed: purity within 10 points, certified structure, and key information close to the anchored tree's. The labels make cells about 4 to 6 points purer by category (6.4 here, 4.3 on the clean split). The anchors still earn named reporting cells and a little extra key information, so the anchored tree stays the tree of record. The label-free tree has a certified trunk, but a later re-draw cut it to the root plus a 'discursive' branch, about 5 sites. An earlier, stronger reading, that the labels actually cost certifiable structure, was withdrawn.

#### ANCHOR-FREE-CERT — how many split sites of the embeddings-only tree can be certified at the registered site null, and at what ...

- **What it tests:** Exploratory sweep with no judge calls. The tree is built from embeddings alone, with no declared subject labels. The test counted how many of its split points pass the statistical significance check (the 'certificate'). It then tried six construction changes one at a time (wider embeddings, pruning, removing top principal components, a different split bar, and combinations).
- **Why:** It asks whether the tree's structure is real and certifiable, or whether only a small part of it passes the significance check.
- **What it tells us:** If some change raised the certified count fairly, it would give a better recipe for building trees. If not, the record count is the honest ceiling. Result: done, exploratory. No change beat the record's 16 of 69 certified splits under a common null. Gains only appeared when a change also weakened the null. A later re-draw corrected the reading: the certified 'fringe' changes from draw to draw (10 to 16 sites), and only 5 core splits are certified on every draw. Nothing was promoted.

#### ANCHOR-FREE-FULL — the embeddings-only tree on the FULL corpus (STRUCTURAL EVIDENCE ONLY; never arena-bound)

- **What it tests:** Grows the embeddings-only tree (no declared subject labels) on almost all 12,000 MMLU-Pro questions instead of only the training share, and compares it with the train-only tree of record. No judge calls.
- **Why:** Asks whether the tree's shape depends on how much data it is grown from: more leaves, a different first split, more certified splits?
- **What it tells us:** If more data gave a higher share of certified splits, data size would be a way to get a more trustworthy tree. If it only adds leaves, data is not the bottleneck. Result: done, structural evidence only. With the full corpus the tree has 36% more leaves and the same first split. More splits certify (18 vs 16), but a smaller share of them (19% vs 23%). On this corpus, data adds leaves but does not raise the certified share. This tree has seen the arena questions, so it may never be judged, used to write rubrics or published as a leaderboard.

#### ANCHOR-FREE-MCS — minimum cell size on the anchor-free tree (EXPLORATORY, zero judge calls)

- **What it tests:** Rebuilds the tree learned without topic labels (the anchor-free tree) with smaller minimum cell sizes (40 and 30 questions instead of 55). It then compares the number of leaves, label purity, how many splits pass the certificate, and how many held-out questions each leaf gets. No judge calls.
- **Why:** Checks whether the anchor-free tree could split further, and what finer cells would cost.
- **What it tells us:** If smaller cells keep quality and still have enough questions, finer cells could be used. If they leave too few questions per cell, the registered size of 55 stays. Result: exploratory only, so it settles nothing. Smaller cells give more leaves (81, then 108, then 143) and slightly higher purity. They lower the share of certified splits and leave very few questions per cell (median 20 at size 30, as few as 6), far below the roughly 120-190 needed. Size 55 stays.

#### ANCHOR-FREE-Z — the acceptance gate on the anchor-free tree (EXPLORATORY sweep, zero judge calls)

- **What it tests:** Rebuilds the tree discovered without declared categories, with the bar a split must clear to be accepted lowered from 2.0 to 1.5 and to 1.0. It reports leaves, the biggest leaf, purity and how many splits pass the significance certificate. No judge calls.
- **Why:** One big leaf (549 engineering/chemistry/physics questions) refused every split, and the question was whether a looser bar finds real structure or just makes more leaves.
- **What it tells us:** If new splits pass the certificate, the bar was too strict. If they don't, the bar is fine and the extra leaves are noise. Result: exploratory only. A bar of 1.5 splits the big leaf and adds 6 leaves, one certified split (three of the four new splits look like noise) and +0.8 points of purity. A bar of 1.0 adds nothing more. The original tree (bar 2.0) stays the tree of record.

#### ARCH-V2-E-T-R2 — a full re-run of the RP12 tree lane (B0, B0', o1, o2 from one new pinned commit after EVAL-METRIC-DETERMINISM ...

- **What it tests:** A full rebuild of the version-2 query tree on the clean data split (no duplicate questions shared between building and testing), after a fix to how its quality metrics are computed. It checks that the tree rebuilds identically, how well it files new questions into the right class, whether a k-means clustering that is allowed to read the class labels does better, and whether any top-level split is statistically certified.
- **Why:** The previous build failed the 'rebuilds identically' check. The thesis needs a reproducible tree before any claim about it can stand, plus an honest comparison against simpler clustering.
- **What it tells us:** A tree that rebuilds identically and files well would support using it as the evaluation's address book. Losing to label-reading k-means, or having no certified splits, would mean its structure mostly comes from the declared labels it is anchored on. Result: done. The tree rebuilt byte-identically on the 7 pairs checked (never a general 'deterministic' claim). It filed 81.2% of new questions correctly, about 9.4 points better than step-by-step descent through the tree. This is a mixed-corpus figure: 74.5% on MMLU-Pro alone. Label-reading k-means filed about 2 points better. No top-level split was certified. Its leaves were somewhat purer than a flat mixture-model control (one build, one draw, thin margin), with no gain on key information. Note: the tree is anchored on declared labels, so 'label-free' only means no LLM labelling.

#### CAP-GATE-POSTHOC — would a CAPABILITY split gate accept the sites the geometric gate certifies? (zero judge calls, zero ...

- **What it tests:** On an existing tree (69 split points, 16 of which are statistically certified on geometry), checks whether a 'capability' rule would accept the same splits. That rule keeps a split only if the child cells really show different model-performance profiles. No new judge calls and no new tree builds.
- **Why:** Statistical separation in embedding space does not automatically mean the cells differ in what models can do. This tests whether the certificate has capability meaning.
- **What it tells us:** If the two rules picked the same splits, geometry would be a stand-in for capability; if they picked different ones, the two notions come apart. Result (exploratory): mostly different sets. At the main threshold the capability rule accepts 24 splits, 9 of them certified; overlap is low (about 0.29). The certified splits clear the capability rule only when each is compared with its own random baseline. On held-out data the top-level splits replicate, but the two strongest deep splits flip sign. Reading: geometric certification is enough for capability content only above the split's own baseline, and it is never necessary.

#### CAP-PRUNE — does a capability rule that survives as a held-out-replicating PRUNE keep only the trunk? (zero judge calls ...

- **What it tests:** Using the anchor-free tree (69 splits), this test asks which splits carry a gain in predicting which models answer correctly. A split is kept only if its gain beats its own chance level on training data and is still positive on held-out data.
- **Why:** It asks whether model capability, not just text similarity, could be used to prune the tree, or whether only the top few splits matter.
- **What it tells us:** If only the trunk survived, the idea of building the tree around capability could be dropped. If more survive, the idea stays alive as a pruning step. Result: done. 20 of 69 splits survived, more than the 4 to 6 predicted, so the capability idea stays open, but only as a pruning step, never as a gate. Only 7 splits have a held-out gain clearly above zero. The splits kept this way overlap only weakly with the geometric certificate: the two select splits nearly independently of each other. Nothing was rebuilt or judged.

#### CELL-DIFFICULTY — out-of-sample difficulty variance explained by AF-U cells vs random within-source cells plus composition ...

- **What it tests:** On the clean version-2 evaluation set (5,907 questions x 18 models), it measures how much of the variation in question difficulty is explained by the anchor-free tree's cells, compared with random cells of the same size drawn within each source benchmark. A secondary check looked at 7 cells where model rankings flip.
- **Why:** If cells are only topics, they might not matter for evaluation. If they also group questions by difficulty, that helps explain why per-cell rankings differ.
- **What it tells us:** A clear excess over random cells shows the cells capture real difficulty structure. No excess would mean cells are difficulty-neutral labels. Result: done, valid. The cells are difficulty strata: they explain 23% of difficulty variation against at most about 8% for random cells. Per-source k-means cells do at least as well (24%, descriptive), so this does not show the tree beats k-means. The 7-flip-cell check is only a consistency check, not evidence of more than one ability dimension.

#### CERT-PC-K2 — does the site-null certificate certify a declared 2-way source-family partition inside math, physics and ...

- **What it tests:** No calls. A positive control for the significance check: inside math, physics and economics, the questions were split two ways by known source (original MMLU questions vs added sources), resized to the earlier test's sizes, and run through the same certificate 30 times.
- **Why:** An earlier test certified 0 of 60 splits. This one asks whether that is because the check is too weak to detect a simple two-way split inside one subject.
- **What it tells us:** If the known split were certified, the check would be shown sensitive enough and the earlier 0 of 60 would reflect weak structure. If not, the check might simply be blind at this size. Result: done. The known split was certified on none of the 30 runs; its separation was below every random baseline. This is read as a failed positive control: it cannot tell 'the check is not sensitive enough' apart from 'source families are only weakly separated'. The earlier conclusions are unchanged.

#### CERT-PC-SIZE — does the site-null certificate still certify the declared 14-category partition at G12's depth-1 site sizes ...

- **What it tests:** Takes the 14 declared MMLU-Pro subject categories and shrinks them to the small sample sizes of the tree's first-level splits (486, 441 and 264 questions). It then checks whether the split certificate, which compares against random reshuffles, still certifies them. No judge calls.
- **Why:** An earlier test certified 0 of 60 first-level tree splits. This test checks whether that happened only because the samples were too small for the certificate.
- **What it tells us:** If the known-real categories fail at these sizes, the earlier zero means nothing. If they pass, the tree's splits really are weaker. Result: the declared categories were certified in 5 of 5 subsamples at every size. So the certificate is not limited by sample size here, and the tree's own first-level splits are less separated than the declared categories. Caveat: this compares 14 groups against 2-way splits, on different populations.

#### CERT-REDRAW-R512 — CERT-REDRAW-R512 (+ CERT-HIER-FWER): the re-draw qualifier of the two certified exhibits (Chemistry ...

- **What it tests:** Checks whether the two certified splits of the main tree (Chemistry and Engineering) stay certified when the tree is rebuilt on two other random train/test draws. Also checks a stricter top-down multiple-testing rule. No judge calls.
- **Why:** A certificate that disappears when the data are redrawn would be fragile. This measures how stable the tree's two showcase splits are.
- **What it tells us:** Surviving both redraws would make the splits robust; surviving one would make them draw-dependent. Result (descriptive, and the analysts had already seen the data): each split is certified on the main tree and on 1 of the 2 redraws. On the other redraw nothing is certified. Under the stricter rule, Chemistry passes on two of the three trees, and Engineering cannot pass at all with 300 repetitions. The redraws are only id-disjoint, not content-disjoint.

#### CONSTRUCTION-ARMS — once the greedy top-down shape and the leaf count are held fixed, does the split rule matter? Python ...

- **What it tests:** The test kept the top-down tree shape and the number of leaves fixed and swapped the splitting rule: a k-means stand-in for the engine, bisecting k-means, Gaussian mixtures, Ward clustering, and HDBSCAN (description only). It ran on three corpora with 5 seeds. It measured how well held-out items are filed into leaves.
- **Why:** It asks whether the tree's quality comes from the particular splitting rule or from the overall top-down design.
- **What it tells us:** If one rule clearly won, the engine should switch to it. If none wins, the choice of rule is not the main lever. Result: done, descriptive only. No rule clearly beats the k-means stand-in, though this is not proof that they are equal. Ward comes closest on two corpora, but that lead is fragile. The Gaussian-mixture rule loses on one corpus because it hits its cap on splits per node. The stand-in is not the engine itself, and the test reached less power than planned.

#### COVERAGE-AUDIT — per union member, the share of its EVAL items filed into cells dominated by other members (X_m) under AF-U ...

- **What it tests:** No calls. For each benchmark in the combined dataset, the test measured the share of its held-out questions that land in a cell dominated by a different benchmark. It compared the tree built without topic labels but separately within each source benchmark (source-conditioned, not label-free) with per-source k-means clustering.
- **Why:** It asks whether the tree mixes benchmarks more than plain k-means does, which would make it a worse index for checking coverage.
- **What it tells us:** If the tree mixed more, it would be the worse tool for coverage audits. Equivalence means neither is worse on this measure. Result: done. The two are equivalent within a 2-point margin (about 3% of items land in a foreign-dominated cell under both). This is equivalence within a margin, not 'no difference'. It is not a claim that foreign filing is an error, and it does not compare how well the two separate benchmarks.

#### DEEP-SPLIT-COMPARE — holding B0's anchors and depth-2 frontier fixed (B0 of lane r2), does a different label-free split rule below ...

- **What it tests:** Keeps the tree's declared top two levels fixed and replaces the splitting rule below them with alternatives: plain spherical k-means, a PCA plus Gaussian mixture, and k-means that knows the class labels. It compares how well each one files held-out questions. No judge calls.
- **Why:** An earlier test found the tree lost to label-aware k-means below depth 2. This one asks whether the cause is the splitting rule or the label information.
- **What it tells us:** If a label-free rule closes the gap, the engine's splitting rule should change. If only label-aware k-means does, the gap comes from labels and changing the engine is not worth it. Result: done. Plain k-means files worse than the tree's own rule (by a thin margin, one construction). Label-aware k-means files better than plain k-means. No label-free rule recovers half the gap, so the splitting rule is not the cause. A descriptive check places the edge in which items enter the depth-2 fit, not in labels below depth 2.

#### F-TAX — which outcomes move the taxonomy clause of the framing of record (expected sentence / 'an evaluation lever' / ...

- **What it tests:** A pre-registered rule, with no new calls, that combines three other tests to decide which sentence the thesis may write about the taxonomy. The candidates were: the expected sentence, 'an evaluation lever', or 'a filing device only'.
- **Why:** It fixes in advance how the thesis's main claim about the tree's value must change given the results, so the wording cannot be chosen after seeing the data.
- **What it tells us:** A routing or filing advantage over k-means would let the thesis call the tree an evaluation lever; losing the top-level certificate would narrow it to a filing device. Result: 'a filing device only'. The presented tree has no certified top-level split, so its certificate clause is withdrawn. Neither lever condition fired. Filing lost to k-means built within each class. Routing was not distinguishable from per-source k-means (difference within noise). The record explicitly avoids saying 'no lever'.

#### FITSET-FAITHFUL — FITSET-FAITHFUL (stage 0 only): with A's (B0 of lane r2) leaves and topology fixed, does re-estimating leaf ...

- **What it tests:** The leaves and shape of one existing anchored tree are kept fixed, but each leaf's centre is recomputed using only training questions of the leaf's declared class. It then checks whether this 'class-pure' version files held-out questions better than the tree as built.
- **Why:** It tests whether the purity of the questions used to fit each leaf is the lever behind k-means' filing advantage over the tree.
- **What it tells us:** A gain says purer fit sets improve filing. No gain would say the k-means advantage comes from something else. Result: done. The class-pure refit filed held-out questions 2.6 points better (95% interval +1.9 to +3.2), above the noise bar. It uses more training labels than the original tree, almost all of the gain is on MMLU-Pro, and it says nothing about anchor-free or label-free trees. Whether the gain tracks impurity is undetermined.

#### FITSET-INTENT — does the class-pure leaf-mean refit improve fine filing on INTENT-S1's anchored trees (M-AN, C-AN), beyond ...

- **What it tests:** Takes trees on intent-classification datasets with known answers (MASSIVE and CLINC) whose top levels follow the declared classes. It re-estimates each leaf's centre using only training items of the matching declared class, keeps the tree shape fixed, and measures fine-level filing accuracy. No calls.
- **Why:** An earlier refit (FITSET-FAITHFUL) improved filing on MMLU-Pro. This checks whether that gain carries beyond MMLU-Pro.
- **What it tells us:** A gain here would make the refit a general improvement. No gain limits it to MMLU-Pro. Result: not shown. The refit is flat within noise on MASSIVE and makes filing worse on CLINC. The earlier gain keeps the limit "mostly MMLU-Pro". This applies to label-anchored trees only, one draw, and the refit itself uses training labels, so it is not label-free.

#### FLAT-GENERALITY — does the FLAT-MIX-MMLU loss appear in the three anchor-free re-draws (af_s137, af_s2048, af_s42_o1), and does ...

- **What it tests:** An earlier test found the tree's leaves less pure than a flat clustering with the same number of groups on one MMLU-Pro draw. This test repeats the comparison on three other label-free tree re-draws. It also checks whether the label-anchored tree loses to a flat clustering, either with the same number of groups (84) or one that is also guided by the labels.
- **Why:** It asks whether 'the tree partitions worse than flat clustering' is a one-off or a general property of the construction.
- **What it tells us:** Result (no new calls, no new builds): the purity loss reappears on 2 of 3 re-draws (one only narrowly) but not the third. The second measure, key information, loses on none. The anchored tree does not lose to either flat comparison, but that is descriptive only and is not a tie. The re-draws are separated by question id only, and one is not independent of the original draw.

#### FLAT-MIX-MMLU — is af_clean_s42 (82 leaves, content-closed) a better partition of MMLU-Pro than a flat vMF mixture / ...

- **What it tests:** Compares the label-free tree af_clean_s42 (82 leaves) on MMLU-Pro against flat clusterings with the same number of groups (a von Mises-Fisher mixture and spherical k-means, 5 seeds), on held-out purity, how much the groups predict model correctness, reliability and held-out likelihood.
- **Why:** Asks whether building a hierarchy gives a better partition of questions than simply clustering flat into the same number of groups.
- **What it tells us:** If the tree wins, the hierarchical construction adds value as a partition; if it loses, the tree's benefit must come from elsewhere. Result: done; the tree is a WORSE partition than the flat mixture (purity -4.3 points, also less predictive), beyond the seed spread. One tree, one corpus; the cause is not identified, and it says nothing about routing or about which is the better taxonomy.

#### G13-BREAKDOWN — per-corpus and per-depth decomposition of R2's G13 (D13 -0.0215), unsupervised k-means comparators at matched ...

- **What it tests:** Breaks down an earlier result where the union tree filed questions less accurately than k-means given the class labels. It splits the result by source corpus and tree depth, and adds plain unsupervised k-means with the same number of clusters. No calls.
- **Why:** It locates where the tree loses and checks whether it beats clustering that uses no labels.
- **What it tells us:** It shows whether the loss is local (one corpus, one depth) and whether the tree adds value over unsupervised clustering. Result: the loss sits mainly in MMLU-Pro (-4.5 points) and opens below the category layer. The tree beats unsupervised k-means by about 7 points, but that lead comes from the tree's declared category anchors (label information), not from discovered structure. The earlier failure stands, and this is not a label-free win.

#### GAP-FIX — does a within-parent Lloyd refinement of af_clean_s42's leaves (T 5) close its purity gap to flat vMF V0 ...

- **What it tests:** The anchor-free tree groups questions into category-pure cells less well than a flat mixture model. This test tries a cheap fix: re-assign each question to the nearest cell within its parent branch (a few k-means-style passes). It then measures how much of the purity gap remains, on about 3,400 held-out questions.
- **Why:** It asks whether the tree's weaker partition can be repaired cheaply, or whether it is built into the tree approach.
- **What it tells us:** If the gap closed, the tree would be as good a partition as the flat model. If it did not, the cost of using a tree is real. Result: done and valid, with a partial outcome. The gap is NOT closed: it shrinks but stays below zero. Whether what remains is large cannot be read: its size sits only 0.0009 under the bar for calling it large, too close to call, so this point is descriptive only. Most of the improvement comes from just recomputing the cell centres. The refinement passes themselves are not shown to help. Results on the other re-draws are descriptive (on one of them the original gap's interval contains zero).

#### GMM-FIXEDK — CONSTRUCTION-ARMS extended with bisecting diagonal GMM and bisecting full-covariance GMM (PCA-32, reg_covar ...

- **What it tests:** Comparing split rules for building the tree, always splitting each node in two. Gaussian-mixture splits (diagonal or full covariance) are compared with a spherical k-means split that mimics the engine. Done on MASSIVE, CLINC and MMLU-Pro with the same number of leaves and 5 seeds.
- **Why:** It asks whether a more flexible split rule would give better partitions than what the engine uses.
- **What it tells us:** A clear win would make a mixture-based split a candidate for a new, separately approved test (never a direct engine change). Result (no new calls): no mixture rule clearly beat the k-means stand-in. The full-covariance rule led on CLINC but fell just short of the seed-to-seed spread. On MASSIVE the bar was out of reach. Its leads are descriptive only, and 'no win' is not proof of a tie.

#### GRANULARITY-GT — best-cut AMI of the [LF] intent trees (M-AF, C-AF) vs an average-link hierarchy at the coarse gold level ...

- **What it tests:** On two intent datasets with gold labels (MASSIVE and CLINC), it compares the label-free discovered tree with an average-link clustering hierarchy at the coarse gold level. It also compares the tree's purity with 200 random trees of the same shape. No calls.
- **Why:** It tests whether the discovered tree reflects real structure ('right at some granularity') rather than arbitrary splits.
- **What it tells us:** Beating random trees shows real structure. Beating a standard hierarchy would show it is better than an off-the-shelf method. Result: valid. The tree beats random trees of the same shape on both corpora. Against average-link the result is mixed: it wins on MASSIVE, but only against a badly chained comparator, and does not win on CLINC. This shows no routing value and no MMLU-Pro result.

#### GRANULARITY-SWEEP — does the union routing gain of per-source k-means cells merged by Ward (about 25/50/100/200/400 cells) peak ...

- **What it tests:** Questions were grouped into k-means cells at about 25, 50, 100, 200 and 400 cells. The routing gain at each size was measured on held-out data. No calls were made.
- **Why:** It asks whether there is a best number of cells for model profiles, and whether finer cells route better than coarse ones.
- **What it tells us:** A clear peak at a middle size would identify the right granularity. Coarse cells winning would mean fine cells add nothing. Result: done, descriptive only. A best middle granularity is not shown. 100 cells beat 25 by +0.69 points, but the interval crosses 0. 100 cells beat 400 by +1.55 points (interval above zero), but this is not read as over-splitting: with 400 cells each cell's estimate rests on fewer questions and is noisier. The choice of 100 as best was itself noisy. Coarse cells did not win. The result is source-conditioned.

#### HIER-F — HIER-F (pre-data addendum to GRANULARITY-GT): hierarchical F over every node of the [LF] intent trees vs ...

- **What it tests:** Scores the label-free intent trees on two intent datasets (MASSIVE, CLINC) against their gold class hierarchy, giving credit at every node, not just leaves. It compares them with average-link clustering and with 200 random trees of the same shape. No judge calls.
- **Why:** It asks whether the tree captures the true hierarchy above its leaves, which is the point of building a tree rather than flat clusters.
- **What it tells us:** Beating random same-shape trees would show the tree carries hierarchy beyond its leaves. Result: done. The tree scores far above average-link on both corpora (0.75 and 0.85 against 0.27 and 0.34), but average-link degenerated into one huge leaf, so this means 'better than a broken baseline', not 'better than a competent hierarchy'. The comparison with random trees could not be evaluated as designed (impossible on CLINC). On MASSIVE alone it is above random, as a per-corpus descriptive reading only.

#### INTENT-TRANSFER-S1 — INTENT-TRANSFER-S1 (the author's D5): real TRAIN-only tree builds on MASSIVE and CLINC150 against matched-k ...

- **What it tests:** Real tree builds on two intent datasets with known label hierarchies (MASSIVE and CLINC150). The trees are compared with flat k-means at the same number of groups and with a supervised upper bound. Checks cover partition quality, hierarchy, address stability, filing new items, and abstaining on borderline items.
- **Why:** On data where the true answer is known, it tests whether the label-free tree recovers real structure as well as standard clustering does.
- **What it tells us:** Result (builds, no judge calls): the label-free tree partitions as well as k-means (judged equivalent on both datasets). It keeps its cell addresses as well as k-means when slot words in a query are swapped (for example a different city name). It files new items better by nearest leaf than by walking down the tree. Its hierarchy beats a simple average-link grouping of the same leaves (interval only). It fails against label-conditioned per-class prototypes, which is a registered failure. This is one draw and one embedder, and 'equivalent' does not mean 'better'.

#### K-SELECTION — is the quantitative depth-1 site's 3-of-4 certification the greedy first-k-that-passes rule's or the ...

- **What it tests:** Asks whether a first-level split of the MMLU-Pro tree certifying 3 out of 4 times comes from the greedy 'take the first number of children that passes' rule or from the data. It rebuilds three trees with a rule that requires a 5% margin above the bar, plus 300-repetition null tests. No calls.
- **Why:** It checks whether a taxonomy result is an artefact of a construction rule rather than a property of the corpus.
- **What it tells us:** If the margin rule makes the split certify every time, the old 3/4 was a rule artefact. Result: done. With the 1.05 margin rule the site certifies on all three draws, but the rule is not local: it changes the tree below the site. This was tested for one corpus, one bar and one margin value only. Nothing was promoted, and there was no judging.

#### KEY-SUBANCHOR-SCALE — is sub-anchor structure dead for taxonomy reasons or data reasons? (zero calls, KEY only)

- **What it tests:** Compares two trees of different granularity on about 11,200 answer-key questions. On questions whose cell changes most between the trees, it asks whether model strengths below the topic level agree across trees. It also checks how this changes with cell size. No judge calls.
- **Why:** Asks whether structure below the topic level failed because the taxonomy is not real or only because cells had too few questions.
- **What it tells us:** Agreement that grows with more data would reopen the sub-topic line as a data problem. Null or negative agreement would close it as a taxonomy problem. Result: the registered statistic was positive, but a checker showed this came from nested cells, which agree by construction. On questions whose cell really changes, agreement is null or negative. The prediction is not shown to fail, but the sub-topic line stays closed for taxonomy reasons on this evidence. The measure must be redone before the line is reopened.

#### MC-BUILD — multi-corpus stage 1: the first six-corpus build (one construction loop over the union, 52 source/domain ...

- **What it tests:** The first single construction loop over all six corpora together (21,606 questions, 18 models, 52 declared anchors). It counts leaves, filing accuracy and certified branch points per source against the single-corpus builds. No judge calls; descriptive.
- **Why:** It checks whether one tree can be built over a multi-corpus union without losing quality.
- **What it tells us:** If certification holds up, one union loop is enough. If it collapses, the construction must change. Result: done. 147 leaves, filing accuracy 0.785. Only 5 of 94 branch points certified, against 8-11 on MMLU-Pro alone: one loop spreads the budget too thin per anchor. This led to the federated design (one tree per corpus, joined under a common root).

#### MC-FED — multi-corpus stage 1b: federated construction (per-corpus trees, each with its own loop, split and site null ...

- **What it tests:** Builds a separate tree for each of six benchmarks, each with its own certification, then grafts them under one root. The result is compared with a single tree built on all six at once: how many splits are certified, and how well held-out questions are routed to the right cell (no judge calls).
- **Why:** It tests whether building per corpus and then merging gives a better multi-benchmark taxonomy than one joint build.
- **What it tells us:** More certified splits and good routing would favour the federated design. Result: per-corpus building recovers certification (13 certified splits vs 5 for the joint build). The grafted tree routes 72% of questions to the right cell. The loss comes from the top-level choice of which benchmark subtree to enter: assigning each question straight to the nearest cell scores 82%. No rule for the top level is shown.

#### MIX-LRT-SITE — full-covariance 1-vs-2 Gaussian likelihood ratio in site-local PCA-10 against the SAME site null ...

- **What it tests:** A statistical test of whether each tree split is 'one blob vs two groups' (a Gaussian mixture likelihood ratio in the split's top 10 principal directions), applied to every split of four trees. The aim was to separate a known contamination split from two Philosophy splits.
- **Why:** The current split certificate is geometric. The test asks whether a mixture test could show that certified splits correspond to real separate modes.
- **What it tells us:** Result (no new calls): negative. The mixture test certifies every split on all four trees, including the Philosophy ones, so it cannot discriminate. The certificate stays geometric, with no support for modes from this test. That does not show the splits lack modes, and the alternative dip test is unexplored. The existing certificate remains the one of record.

#### MMLU-GOLD-GEOMETRY — is MMLU-Pro's declared 14-category level geometric over its 91 (src, category) fine labels in qwen3 (H vs ...

- **What it tests:** Groups the 91 fine MMLU-Pro source-subject labels by their average qwen3 embeddings and checks whether the grouping recovers the 14 official categories better than random relabellings.
- **Why:** Tests whether MMLU-Pro's declared categories actually show up as structure in embedding space, which matters for judging trees against those categories.
- **What it tells us:** Strong recovery means the categories are geometric; weak recovery means comparing trees against them is limited. Result: done; recovered above chance but only partially (agreement 0.29, against 0.03 for the 95th percentile of random relabellings; 1 would be perfect). Training data and qwen3 only; the comparison with CLINC and MASSIVE is descriptive.

#### N4-RECONCILED — does the multi-corpus union really cost MMLU-Pro its certified structure? (zero calls; the two existing ...

- **What it tests:** It paired two existing analyses anchor by anchor. One built the tree on MMLU-Pro alone, the other on several benchmarks pooled together. It counted how many of the 14 MMLU-Pro topics certify in each. No calls were made.
- **Why:** It tests a standing claim that pooling benchmarks roughly halves MMLU-Pro's certified structure.
- **What it tells us:** If true, multi-benchmark trees would lose structure. If false, the cost lies elsewhere. Result: done. The 'halved' claim is withdrawn: 3 vs 5 of 14, p = 0.625. What pooling costs is questions, not separation. MMLU-Pro math questions get absorbed into the MATH benchmark's cells. This supports building each benchmark separately and then combining them.

#### RECORD-RECIPE-EDGE-AUDIT — the tree of record bareq512_s42 (snapshot 20260909_212117) is NOT a certified fixed point (CERTIFIED false at ...

- **What it tests:** Audits the 10 certified splits of the main tree (bareq512). It checks whether any was created late, after the build had gone quiet, and whether any barely clears the minimum separation bar. No calls.
- **Why:** The main tree turned out not to be a true fixed point, so its certified splits might come from late, unstable edits.
- **What it tells us:** If certified splits were late or borderline, the certified structure would be fragile. Result: none of the 10 were born late, and all sit 2.4 to 6.2 times above the bar. The certified structure is not a product of late edits. The tree is still not a certified fixed point, and the cluster-count side is undetermined.

#### RESP-PROFILE-INFO — out-of-sample R^2 of 3PL residuals explained by AF-U cells vs 200 random within-source cell sets (RP1) and ...

- **What it tests:** Removes question difficulty and general model ability with an item-response model, on 5,907 evaluation items x 18 models from a content-closed multi-source pool. It then measures how well the discovered cells explain which model does better. This is compared with random cells of the same sizes inside each source, and with per-source k-means clusters of matched count. No calls.
- **Why:** Asks whether the discovered cells carry real which-model-wins information beyond the dataset source, and whether they beat a simple clustering baseline.
- **What it tells us:** Beating random cells means cells carry signal beyond source. Beating k-means would favour the discovered tree. Result: done. The cells beat random cells of the same size inside each source (explained share 0.053 vs 0.038 at the 97.5th percentile). But per-source k-means is slightly better than the tree as built, and that holds descriptively on own-source items too. This is not a routing gain and is tied to these 18 models.

#### SITE-SUPPORT — transfer support (TBE) of certified vs uncertified sites across the four AF MMLU-Pro re-draw trees on their ...

- **What it tests:** Across four anchor-free MMLU-Pro trees from different re-draws, it measures how often each branch point's cluster reappears in the other trees. It compares certified with uncertified branch points of the same depth and size, and also with random subsets. No judge calls.
- **Why:** If the certificate means something, certified branch points should be more stable across re-draws than uncertified ones.
- **What it tells us:** Higher recurrence for certified sites would link the certificate to stability. Result: done, not shown, and the failure condition fired: certified branch points do not recur more than uncertified ones. Nearly all sites (263 of 264) recur more than random subsets, but that null is only a floor and shows just that the trees are related. Stability is not correctness either way.

#### SPLIT-RATIO-SEEDS — does the certification plateau below 0.20 replicate across seeds? (builds + site nulls, zero calls)

- **What it tests:** Rebuilds label-free trees with 10% and 20% of the data held out, with extra random seeds. It counts how many tree splits pass the certification test against a null, compared with the usual 30% held-out split. No calls.
- **Why:** Checks whether an earlier finding (certified structure stops growing once enough data is on the training side) is robust to the seed.
- **What it tells us:** Decides whether the 30% held-out split should change. Result: the plateau replicates. About 13 to 14 certified splits at 10% and 20%, against about 10 at 30%, while the number of leaves keeps growing. The 30% split stays.

#### STABILITY-VS-KMEANS — triplet disagreement between the four AF MMLU-Pro re-draw trees vs matched-data, matched-leaf-count ...

- **What it tests:** How consistently four label-free MMLU-Pro tree re-draws group the same question triples. They are compared with hierarchical k-means baselines that use the same data, the same leaf count and the same shape (bisecting k-means, and flat k-means followed by merging), with 5 seeds.
- **Why:** It checks whether the trees' stability is a special property of the tree, or just what any comparable clustering would give.
- **What it tells us:** Result (no new calls): the trees are as stable as bisecting k-means, not more. Their apparent edge comes from leaving about 12% of triples unresolved. They are more stable than merge-based hierarchies, but bisecting k-means matches them, so this is not a tree property. The registered falsifier fired, and an earlier larger stability gap is no longer read as a tree property.

#### STABLE-CELL-SET — the 5-site re-draw-stable certified set as a partition on the clean free tree R1 af_clean_s42 — does it carry ...

- **What it tests:** Takes the 5 cells of the label-free clean tree that stay stable across re-draws, uses them as a 5-group partition of 3,445 questions, and checks with answer keys whether they support a reliable model profile, compared with the 14 named MMLU-Pro categories.
- **Why:** Asks whether a label-free tree yields a usable home for per-cell model profiles.
- **What it tells us:** It shows whether label-free cells can replace named categories for profiling. Result: done; yes in a weak sense only: reliability 0.93, but a random 5-way grouping of the named categories reaches 0.91, the result leans on one uncertified catch-all cell, and the cells carry about half the information of the 14 names.

#### TOPIC-PARTITION-20NG — on a corpus with ground-truth topic labels the construction has never seen (20 Newsgroups, 20 labels under 7 ...

- **What it tests:** The tree-building recipe was run on 20 Newsgroups, a text corpus with 20 known topic labels the method never saw. The test checked whether the recipe builds and certifies a tree, whether it splits the space better than k-means, Ward or HDBSCAN with the same number of parts, and whether its certified splits line up with the true topics.
- **Why:** It tests on ground truth whether the discovered tree reflects real structure and is better than plain clustering.
- **What it tells us:** Beating k-means would show the tree finds better structure. Certified splits lining up with the topics would support trusting the certificate. Result: done. The recipe builds and certifies on this corpus. It splits the space no better than k-means with the same number of parts. Certified splits are somewhat more topic-aligned (p about 0.05), but this rests on few effective sites and does not survive a control for cluster size. One embedder, one seed, one split.

#### TOPIC-PARTITION-20NG-T1B-NULL — does the per-corpus pair (512 / 0.0145) CERTIFY on 20 Newsgroups? The one hole TOPIC-PARTITION-20NG left - ...

- **What it tests:** Completes a missing certification on 20 Newsgroups for a tree built with the 512-dimension, 0.0145-bar settings (100 leaves). It runs the null test that had earlier crashed with an out-of-memory error. No judge calls.
- **Why:** It tests whether these construction settings carry over unchanged to a new corpus.
- **What it tells us:** Certification would show the settings transfer whole. Result: done. The tree builds but does not certify: the root and both first-level splits fail their null. Only 1 of 97 sites certifies, which is descriptive. On this corpus the earlier transfer result rests on the 256-dimension, 0.025-bar tree alone. The two recipes cannot be ranked against each other.

#### TREE-LIKE — Gromov delta / ultrametricity / cophenetic z-scores against the moment-matched Gaussian null on intent ...

- **What it tests:** Measures whether intent-dataset embeddings (CLINC, MASSIVE; qwen3 embedder) are geometrically tree-like (Gromov delta and related measures). This is compared with a Gaussian null of matched mean and covariance, after a planted-hierarchy positive control. No calls.
- **Why:** Asks whether the embedding space has hierarchy beyond its covariance, or whether any tree built on it is imposed by the algorithm.
- **What it tells us:** Not tree-like would mean the hierarchy is an artefact. Tree-like would support, but not prove, hierarchy. Result: done, mixed. CLINC reads tree-like in 5 of 5 subsamples, MASSIVE in 0 of 5. But a flat cluster mixture also reads tree-like under this test, so neither reading is evidence of hierarchy, and it is not 'CLINC hierarchical, MASSIVE flat'. The falsifier did not fire. The MMLU-Pro arm was not run.

### State: UNDETERMINED (2)

#### FOREIGN-GATE-D4 — FRAMEWORK item 14: does the FOREIGN gate (a leaf's arrival purity against its own train-side purity) trip on ...

- **What it tests:** Checks whether a proposed 'foreign arrival' alarm, which compares a leaf's purity on new data with its training purity, fires on Law questions absorbed into another region and not on genuine Philosophy regions. It uses existing artefacts and no calls.
- **Why:** It tests whether the tree can detect when new kinds of queries arrive in a cell, as the framework design requires.
- **What it tells us:** Firing on Law but not Philosophy would show the alarm works. Result: undetermined, because the alarm's written definition is ambiguous in two places that flip the outcome. Under one reasonable reading (the reference is the anchor name, with the leaf's own training purity minus 2 SD), the Law regions do trip. The design must fix both definitions before the item can be scored.

#### NEARDUP-AUDIT — CK-CLOSE-v1 stem_key twins between p2dca EVAL and bareq512_s42's TRAIN members as positives: leaf blocking + ...

- **What it tests:** No calls. Using 70 known near-duplicate pairs between held-out and training questions, the test compared two ways to find them: searching only within the same tree leaf, and a plain similarity threshold over all questions. k-means was measured alongside.
- **Why:** It asks whether the tree can safely serve as a shortcut for finding near-duplicate questions, i.e. for contamination checks.
- **What it tells us:** If searching within leaves missed more than 10% of duplicates, the advice would be to use plain similarity search. Result: undetermined. Searching within leaves missed 5 of 70 (7%), but the uncertainty range reaches about 13% and the estimate sits close to the 10% bar. So the tree is not shown to be a safe index. Paraphrases and decontamination verdicts are not covered.

### State: run-unreviewed (1)

#### ARCH-V2-E-T — ARCH-V2-E-T (RP12): the content-closed v2 tree lane: G10 determinism, G11 filing, G12 certificate (= F-TAX ...

- **What it tests:** A planned battery of checks on the rebuilt version 2 tree, which is built on a cleaner data split with no repeated question text. The tree is rebuilt several times to see whether it comes out the same, whether it files new questions correctly, whether it beats class-aware k-means and a flat mixture, whether its cells change the model-choice policy, and whether it has a statistically certified top-level split.
- **Why:** The thesis needs a tree that is reproducible and better than simpler groupings before any per-cell claim can rest on it.
- **What it tells us:** If the tree passes, it becomes a stable, defensible base for the later per-cell tests. If it fails, the thesis has to work with a simpler partition. Result: run, but the post-run review has not happened yet. The first gate, byte-for-byte reproducibility, FAILED as registered, so the lane stopped. The tree structure itself reproduces exactly. The failure came from the order of queries inside a node (a multi-threaded step) and from order-sensitive metrics. None of the other checks (filing, k-means comparison, flat mixture, policy, certificate, order stability) was read. A follow-up run is planned.

### State: registered (1)

#### SI-NULL-TRIAD — plain vs SigClust-soft vs Gao-type selective null on CERT-PLANTED's planted grid (size and power); real sites ...

- **What it tests:** Plans to compare three ways of building the 'no structure' baseline for split certificates: the plain one and two stricter statistical variants. Each is tested on artificial data with planted 2-way structure and on structureless data. No judge calls.
- **Why:** Looks for a certificate baseline that detects real 2-way splits without certifying random clouds.
- **What it tells us:** Would show whether any baseline can certify the tree's binary splits fairly, or whether none can. Result: registered but not run yet.

## SQ4 Price

19 tests: what does a reliable board or placement cost, and what can be saved?

### State: done (18)

#### ARCH-V2-PILOT-K46 — the key-blind nominal per anchor at k = 46 (46-model roster, 2 anchors of the split of record, N = 2 ...

- **What it tests:** A paid pilot judged 37 models on 2 topic anchors (health and math), using about 5,300 judge calls. It measured how the number of comparisons needed grows when the roster goes from 12 to 37 models. The test was registered for 46 models and later cut to 37.
- **Why:** It gives the planning number for how much a large leaderboard would cost under the new design.
- **What it tells us:** A low growth exponent would mean big boards are cheap to plan. A high one would mean they are expensive. Result: done. The exponent is about 1.8, with an interval of 1.28 to 2.32. This rules out the optimistic planning reading (exponent about 1.06) but not a reading near 2. It is a planning-scale reading only, from 2 anchors (math alone does not rule out the optimistic reading). It does not choose a board size; that is the author's decision.

#### ARENA-V3-COMPILED — the paper's board, rebuilt from the interventions that survived rather than from the RK-1b card (1,250 calls ...

- **What it tests:** Three versions of the model leaderboard, all built with the same judge. A is the published board. B adds a filter that skips matches where both models gave the same answer, at no new cost. C adds an extra re-judging step to break B's ties. The test compares ranking quality, judge accuracy and the number of judge calls.
- **Why:** It asks whether the paper's leaderboard can be rebuilt more cheaply and more accurately from the changes that held up in earlier tests.
- **What it tells us:** It shows whether cheaper judging costs ranking quality, and whether tie-breaking actually helps the judge. Result: done. The filter cut judge calls from about 18,300 to about 10,550 with no loss in ranking quality. The honest claim is "no cost, about half the bill", not "a better board", because the confidence intervals overlap. The tie-break missed its target: +2.2 points of accuracy against a +3-point bar. It makes the judge commit to more matches, but the extra decisions are less accurate than its average. This belongs to the older question pool, which is now ruled history, not evidence.

#### CELL-STRATA-EVAL — leave-one-model-out accuracy estimation from n sampled EVAL items: AF-U-cell strata vs random, source and K_0 ...

- **What it tests:** Estimating each model's accuracy from only 100 sampled questions. Sampling is spread evenly across the tree's cells, then compared with plain random sampling, sampling by benchmark source, and sampling by per-source k-means groups. Done on 5,907 held-out questions with 18 models, each model left out in turn.
- **Why:** If the tree's cells capture what makes questions differ, sampling by cell should give accurate scores from fewer questions, which would make evaluation cheaper.
- **What it tells us:** A clear win over source sampling would support 'the tree cuts evaluation cost'. Result (no new calls): sampling by tree cell beats plain random sampling (about 5% lower error). It is not better than per-source k-means groups, and it cannot be told apart from sampling by source (undetermined, below what the test could detect), for the tree as built. So no 'the tree makes evaluation cheaper' claim is made.

#### COST-AXES-INGEST — FRAMEWORK item 16: token counts per (model, cell) and the tier-then-cheapest router's accuracy and cost ...

- **What it tests:** Token counts were estimated per model and per cell with tokenizer proxies. A router that picks the cheapest model within 0.5 points of the best model in each cell was then scored out of sample. It needed to reach 85% or less of the best model's token cost. No LLM calls were made.
- **Why:** It tests whether per-cell routing can save money as well as keep accuracy.
- **What it tells us:** Passing would show a real cost saving from routing. Failing would mean the savings exist only on a rough parameter-count proxy. Result: done, FAIL, and robust to the choice of tokenizer. Accuracy was kept (+0.54 points, interval covering 0). Cost was 98.8% of the best model's, a saving of only about 1%, because the top tier often has only one model. The re-read on all 52 cells is undetermined. Latency was not computed.

#### FILTER-BOARD — does the answer-disagreement filter preserve board quality, or does dropping 36% of matches cost something? ...

- **What it tests:** Takes about 2,000 matches that were judged twice, removes those where both models gave the same answer, and rebuilds the leaderboards with and without the filter. No new judge calls.
- **Why:** It checks whether skipping same-answer matches, which saves about a third of the judging, harms the leaderboard.
- **What it tells us:** It shows whether a cheap filter is safe to ship. Result: done. The filter kept 64% of matches, including every match whose answer key could decide the winner. Ranking agreement held or slightly rose (0.979 to 0.986), and violations stayed at 1. So it is safe for leaderboards. A later test found that it does lower the reliability of the per-model skill profile (0.72 to 0.56). This belongs to the older question pool, which is now ruled history, not evidence.

#### HYBRID — grade to rank, compare only where grades are close: does routing between the two formats beat either? (zero ...

- **What it tests:** Using cached verdicts from both judging formats on the same 1,971 matches, it uses the grade-only verdict when two answers' grades are far apart and the head-to-head comparison when they are close. It sweeps the threshold. No calls.
- **Why:** It tests whether mixing the two formats gives better accuracy at lower cost than either one.
- **What it tells us:** Success would give a cheaper, more accurate judging recipe. Result: failed on two of three requirements. Accuracy peaks at 0.883, above both formats. But no setting fixes the order of the top models, because close-grade pairs are exactly the top pairs, and the mix is never cheaper. Advice: rank with grades only, and use the mix only for individual verdicts. Later ruled 'history, not evidence'.

#### JUDGE-SWAP — standing DECISION (2026-09-11): which model is the cheap judge? (free paired check, zero calls)

- **What it tests:** Compares Mistral-Large and grok-4-1-fast as judges on the same 944 answer-key-decidable pairs, with the same recipe, using cached verdicts. No calls.
- **Why:** It decides whether a judge about ten times cheaper can replace the expensive one for all future re-judging.
- **What it tells us:** Equal accuracy justifies the swap. A gap would mean paying for quality. Result: accuracy is a wash (0.865 vs 0.864) and the board is the same, so grok became the standard re-judge model. Caveat: grok later also entered as a contestant, and judge-to-same-family bias is untested. Later ruled 'history, not evidence'.

#### K-RECONCILE — FRAMEWORK item 10: reconcile the per-cell k of 4.84 (STRESS) with 2.06 (RESOLVE-CALIB) and declare the ...

- **What it tests:** Two earlier analyses gave different values (4.84 and 2.06) for a factor that sets how many questions each cell needs. Using no new calls, the test reran both on the same data to find where the gap comes from.
- **Why:** The budget of questions per cell depends on this factor, so the framework needs one declared value and an explanation.
- **What it tells us:** It tells the framework which number to use for budgeting and what that number depends on. Result: done. The prediction that the gap came from correlation between models was refuted. Both numbers are the same quantity under two fitting methods, and almost the whole gap comes from a statistical smoothing setting in one fit. The declared value is about 2.05, valid only under that setting, which must be stated wherever the value is used. Later ruled history rather than evidence, because it ran on the older question pool.

#### MATCH-FILTER — ship the answer-disagreement rule as a scheduler OPTION that degrades cleanly where no extractable answer ...

- **What it tests:** Engineering, no calls. Added a scheduler option that only sends a question to the judge when the two models gave different final answers. It needs no answer key, is off by default, and falls back cleanly when answers cannot be extracted. Checked with tests and a bit-identical replay with the option off.
- **Why:** It turns the SCHEDULING finding into a usable feature that cuts judge spend on matches that carry no signal.
- **What it tells us:** It shows the cheaper scheduling can ship without changing past results. Result: done, shipped. 307 tests pass, the replay with the filter off is identical, and it reproduces the 16.9% figure from SCHEDULING. Later caveat: the filter lowers the reliability of the per-subject capability profile (0.72 to 0.56), so it does not suit that use.

#### NEWCOMER-PLACEMENT-LIVE — FRAMEWORK item 22: two real newcomers absent from x12 (claude-3-5-sonnet-20241022, frontier-adjacent ...

- **What it tests:** Places two new models (claude-3-5-sonnet, gpt-4o-mini) live into the existing 19-model leaderboard. Each is compared against 4 incumbents chosen by bisection, with 100 questions each: 400 matches per newcomer, 1,600 calls.
- **Why:** Tests whether a new model can be ranked cheaply, within 2 adjacent tiers, without re-running the whole arena.
- **What it tells us:** A tight interval would make 400 matches a valid, cheap placement budget. Result: done, failed by the registered falsifier. Both placements point the right way and contain the true tier, but the intervals are too wide (7 and 3 tiers). A later re-analysis split the width into two parts. Part comes from frontier models the record refuses to order, a floor that no budget can remove for a frontier newcomer. Part comes from incumbents the newcomer was never judged against, which more bisection steps would remove. So 400 matches is not a placement budget. This belongs to the older question pool, which is now ruled history, not evidence.

#### ORDER-1 — is single-order judging a free cost halving? (from ARENA-V2's cache; zero calls)

- **What it tests:** Using about 9,100 stored verdicts, keeping only one of the two answer orderings the judge sees (A then B, or B then A) instead of both, and comparing accuracy, ranking agreement and leaderboard.
- **Why:** Judging each pair in only one order would halve cost, if it were free.
- **What it tells us:** Result (no new calls): it fails. Single order looks more accurate only because the dual-order judge abstains on ties. The leaderboard changes depending on which order is kept, so both orders stay. A scheduling confound (the stronger model is usually shown second) means this is not a measure of position bias. It is on older judged data now ruled history.

#### PLACEMENT-CEILING — is the newcomer band at 400 matches a key-tie band or a budget band? (zero calls; plan A6; decides whether C6 ...

- **What it tests:** Two newcomer models were placed on the leaderboard with 400 matches each and landed in wide bands (7 and 3 tiers). The test decomposed each band into tiers the answer key itself cannot separate and tiers that were simply never tested. No calls were made.
- **Why:** It decides whether a costlier placement run (3,200 calls) would narrow the bands.
- **What it tells us:** If the band came from too few matches, the paid run would be worth it. If it came from ties or untested steps, it would not. Result: done. For Claude-3.5-Sonnet, 3 tiers were never matched against; that is a shortfall of placement steps, not of match count. The other 4 tiers are a structural floor at any budget. The paid run as priced was declined, and a step-based placement design was proposed instead. Later ruled history rather than evidence, because it ran on the older question pool.

#### PLACEMENT-STEPS — does one further bisection step per separable tier remove exactly the separable tiers from the two recorded ...

- **What it tests:** Paid run. Four steps of 100 filtered matches each (both answer orders) placed two newcomer models (sonnet, gpt-4o-mini) against chosen existing models, with one known-easy comparison as a positive control.
- **Why:** It asks how much it costs to place a new model on the leaderboard, and whether extra targeted matches narrow its uncertain band down to the unavoidable minimum.
- **What it tells us:** It gives a price for adding a model (matches per newcomer) and shows where narrowing stops. Result: done. Both criteria held: each extra step separated the targeted tier, and the positive control worked. Cost is about 400 + 100 matches per separable tier. The remaining band is a structural floor set by the rules, not by measurement. Only two newcomers were tested, so this is priced, not replicated. Note: older question pool, ruled 'history, not evidence'.

#### PROFILE-R-FILTERED — does the anchor profile's reliability survive the answer-disagreement filter that halves the newcomer bill? ...

- **What it tests:** On about 21,500 existing verdicts, the test kept only matches where the two models gave different final answers. This filter roughly halves the judging bill for a new model. It then measured how reproducible the per-subject model order stays, by comparing two random halves of the data.
- **Why:** It checks whether the cheaper evaluation still gives a reliable per-subject profile of the models.
- **What it tells us:** If reliability held, new models could be profiled at about half the cost. If it dropped, the saving costs precision. Result: done. Reliability fell from 0.72 to 0.56, below the 0.60 bar, so the prediction failed. About 58% of the drop is just from having fewer matches. The rest is because the dropped same-answer matches carry an order of their own. The filtered profile actually tracks the answer key better. This does not show that the filter 'destroys' the profile. Older judged question family, later ruled 'history, not evidence'.

#### SCHED — does Varco Arena's single-elimination tournament beat this framework's cell-stratified BT racing scheduler at ...

- **What it tests:** A simulated arena with 12 models was run at the real campaign's match budget, with a simulated noisy judge. It compared a single-elimination tournament with this framework's adaptive, cell-stratified match scheduler. No calls were made.
- **Why:** It checks whether the framework's scheduler spends a fixed budget better than a simpler published tournament design.
- **What it tells us:** If the tournament won, the scheduler would be unnecessary. Result: done, on simulation only. The tournament does not win. The overall ranking is about equal at realistic noise and favours the framework at high noise. The framework makes 4 to 13 times fewer top-4 order errors and is slightly better per cell. The round-robin per-cell comparison was not comparable. It uses an older-family schedule, so it counts for planning only.

#### SCHEDULING — is the frontier unresolvable because the scheduler picks the wrong matches? (zero calls)

- **What it tests:** No calls. For the six pairs among the top 4 models on about 3,400 questions, the test compared how often the answer key can settle a match when the two models' own final answers differ versus when they agree.
- **Why:** It asks whether the frontier models cannot be told apart because the scheduler wastes matches on questions with no signal.
- **What it tells us:** If informative matches sit almost only where answers differ, judging only those cuts cost with no loss. Result: done, descriptive. Answers differ on 16.9% of question pairs. Filtering on that keeps 99.8% of all decidable pairs while judging only 16.9% of matches, with no answer key needed. This works for multiple-choice and checkable tasks, not open-ended generation.

#### SELECTIVE-ORDER — can the second order be skipped where the candidates' own answers already agree? (zero calls)

- **What it tests:** Replays three judging policies on 9,142 cached matches that store both presentation orders: always judge in both orders, always one order, or both orders only when the two models' answers differ. No calls.
- **Why:** Judging each pair in both orders doubles the cost. The test asks whether the second order can be skipped when the answers already agree.
- **What it tells us:** Same quality at fewer calls would be a cheap saving. Result: done, registered failure. The selective policy costs 58% more than single order and gives the same weaker leaderboard (0.958 vs 0.972). Orders disagree more often on agreeing answers (19% vs 11%). There, a single order invents a winner and usually favours the longer answer. There is no cheap subset to skip. Arena-pool data, later ruled history, not evidence.

#### SPLIT-RATIO — reserved-pool ratio study: how much of the query set can the arena take without losing construction ...

- **What it tests:** Trees were built while reserving different shares of the questions (0.1% to 40%) for the arena. It checks how many leaves and certified splits survive, and whether simulated per-anchor rankings stay precise enough.
- **Why:** It looks for how much data can go to evaluation without weakening tree construction, a cost trade-off.
- **What it tells us:** It tells which split ratio balances evaluation precision and tree quality. Result: done (zero calls). The prediction that 30% is the sweet spot was not supported; the readout pointed to 20% (an extended run said 10%). 30% stays the deployed, defensible middle. Leaves grow with training size, but certified splits plateau, limited by the minimum cluster size, not data volume. Leaf-level rankings are not supported at any ratio.

### State: blocked (1)

#### ARCH-V2-G22 — the arena simulator (validity; nu(k, N); P(nominal >= 9) per design; b1 identification; the key-blind stop ...

- **What it tests:** Builds a simulator of the arena and checks it against the board that was actually recorded. The aim was then to use it to choose a board size (number of matches and calls) likely to certify at least 9 model orderings, with a safe stopping rule that does not look at the answer key.
- **Why:** Before paying for a large new judged board, the thesis needs evidence about how big it must be. Only a validated simulator can supply that.
- **What it tells us:** A valid simulator would size the next arena cheaply and justify a stopping rule. A failed one means no design can be sized this way. Result: the simulator as registered FAILED its validity check, so it decides nothing. Its error counts were far from the recorded ones, and cost grows much faster with the number of models than the planning memo assumed (exponent about 1.9 to 2.0 instead of 1.06). A separate certificate check passed. A second simulator, specified after the data were seen and run once, passed at the very edge of its rule. It is not centred on the record (it over-predicts wrong orderings), so its design readings are only an ordering of designs. No board size follows. These are planning quantities from the older question family. The item is now blocked: a re-run on real data is owed, and dropping it is proposed but waits for the author's decision.

## SQ5 Invariance

18 tests: do the results survive changes of embedder, split, seed or corpus?

### State: done (14)

#### ANCHOR-FREE-REDRAW — does the anchor-free tree's certified trunk survive a re-draw of the sample, the split and the construction ...

- **What it tests:** Rebuilds the tree discovered from embeddings alone, with no declared categories, five times: on a clean question split, with a new random sample (two draws), and with a different construction order. A tree built with declared categories on the clean split serves as a control. For each build it checks which branch points are statistically certified. No judge calls.
- **Why:** All earlier anchor-free claims came from a single draw (seed 42, on a contaminated split). This test checks whether the 'certified trunk', and the claim that anchors cost certification, belong to the method or to that one seed.
- **What it tells us:** If the trunk comes back on every draw, the tree's top structure is a property of the method. If it does not, it was luck of the sample. Result: done. The tree exists on all 5 draws and has the same first split. The root and the 'discursive' first-level branch are certified on every draw. The 'quantitative' branch is certified on 3 of 4 draws. Only about 7-8 of the 16 original certified branch points come back on a new sample. On the clean split the anchored control certifies 11 of 60 against 14 of 69, so the earlier claim that 'anchors cost certification' was withdrawn as a headline. This is structural evidence only.

#### E1-SPLIT-DRAWS — is E1's nomic-vs-qwen3 anchor-free tree-filing loss consistently negative and beyond the between-split spread ...

- **What it tests:** Rebuilds the label-free tree on MMLU-Pro with two embedders (nomic and qwen3) on three fresh random train/evaluation splits that share no question text (6 builds, no calls). It compares how well each tree files questions into the right place.
- **Why:** An earlier test (E1) found the nomic embedder files worse. This checks whether that loss is real or just luck of one split.
- **What it tells us:** A consistent loss larger than the split-to-split spread would make the embedder effect robust. Otherwise it stays specific to one split. Result: neither. Nomic filed worse on all 3 splits (the sign held), but the average loss is not larger than the spread between splits. That spread was inflated by one unusually coarse nomic build. The falsifier fired on the size of the effect, not its direction. E1 now reads "at this split only; not stable across 3 re-draws". One corpus and one recipe only.

#### EMBED-DIM-SLICE — is S0's fine-level 'gemma beats qwen3' (C1a; SLOTSWAP M3) an artefact of the 256-d slice? qwen3 at ...

- **What it tests:** An earlier result found that the gemma embedder beats the qwen3 embedder at fine levels, but both were cut to 256 dimensions, which keeps only 6% of qwen3's size and 33% of gemma's. This test compares each embedder at several sizes on three intent datasets with known labels, choosing the size on one data part and reading the result once on another.
- **Why:** It checks whether the 'gemma is better' finding is just an artefact of the size cut.
- **What it tells us:** If the edge vanished, the earlier finding would be an artefact. Result (no new calls): at each embedder's best size, gemma's edge survives on 2 of 3 datasets (MASSIVE and Banking77) and is a tie on CLINC. The size cut explains part of the edge, not all of it. Prompts were not controlled. A later check found that quantisation does not explain the edge (tested up to Q8 only). This makes 'gemma is better' a candidate for reopening, not a change of the embedder of record. Intent datasets only; nothing about MMLU-Pro.

#### EMBED-QUANT — is qwen3-embedding's Q4_K_M quantisation a confound of the intent-corpus embedder contrasts (EQ1 TOST of fine ...

- **What it tests:** Clusters three intent datasets (MASSIVE, Banking77, CLINC) with k-means using the qwen3 embedding model at two compression levels (4-bit Q4_K_M vs 8-bit Q8_0) and checks whether cluster quality is the same within the normal seed-to-seed noise.
- **Why:** The thesis uses a compressed embedder; if compression changed the clusters, embedder comparisons could be an artefact of compression.
- **What it tells us:** Equivalence clears compression as a confound; a difference would require re-running with higher precision. Result: done; equivalent within seed noise on MASSIVE and Banking77 (CLINC equivalent but descriptive only), so not a confound between these two levels. Precision above 8-bit is untested, and it does not explain why another embedder (gemma) scored higher.

#### EMBEDDER-CROSS-FLAT — EMBEDDER-CROSS-FLAT (REG-2 revised; E0 STRUCK): flat partitions in other embedding spaces with no builds (E0b ...

- **What it tests:** The test built simple flat clusterings in two other embedding models (nomic, gemma) and with a keyword baseline, then compared them with the qwen3 embedder on MMLU-Pro. It measured how pure the clusters are and how much information they carry about the answer key, at 14 and at 82 clusters. The planned full tree build in another embedder was not run.
- **Why:** It checks whether the partition results belong to the method or depend on one particular embedding model.
- **What it tells us:** Similar results across embedders would point to a property of the method. Large gaps would mean the results depend on the embedder. Result: done for the flat part only, descriptive. At 14 clusters, the other embedders are not shown to be worse than qwen3. At 82 clusters, nomic is worse. The keyword baseline is far worse. One corpus and one draw per embedder, with no claim of equivalence. The tree build in another embedder was not run.

#### GEMMA-OWN-BAR — with a gemma-768 separation bar from the record's bar rule on TRAIN-only nulls, does a gemma anchor-free ...

- **What it tests:** An earlier anchor-free tree built with the gemma embedder on MASSIVE intents had only 4 leaves. This test rebuilt it with a separation threshold recalibrated for gemma's own embedding space, rather than the threshold tuned for the default qwen3 embedder.
- **Why:** It asks whether the tiny gemma tree came from an unfair threshold tuned for another embedder, or from the recipe itself.
- **What it tells us:** Many leaves would blame the threshold. A tiny tree again would point at the recipe for this embedder. Result: done, valid. The gemma-calibrated threshold came out stricter, not looser (0.044 vs 0.025), and the tree never split (1 leaf), so the comparison with gemma k-means could not be scored. Conclusion, in this form only: the anchor-free recipe does not build a gemma MASSIVE tree under this threshold rule. It does not show the recipe fails at every threshold, nor 'no structure'.

#### GOLD-LEVEL-EMB — is the gold COARSE-level k-means readout invariant within 0.025 NMI across slice, quantisation, prompt and ...

- **What it tests:** Runs k-means at the coarse, human-labelled level of MASSIVE and CLINC and checks whether agreement with those coarse labels stays within 0.025 across vector length, compression, prompt wording and embedder choice (9 settings).
- **Why:** The literature says clustering survives such changes; the thesis wanted to know if that holds at the coarse level while only the fine level depends on the embedder.
- **What it tells us:** Invariance would let the thesis say the coarse level is robust; non-invariance limits the claim. Result: done; compression is invariant, vector length undetermined, but prompt wording and embedder choice DO change the coarse readout (no consistent direction), so the robustness claim must name those two factors. k-means only; nothing about trees or MMLU-Pro.

#### H9-REM-FLAG — Block 3 prerequisite: the construction-order shuffle debug flag (constructionOrderShuffleSeed), then the ...

- **What it tests:** Adds a debug setting that shuffles the order in which the tree builder considers splits and merges. It rebuilds the topic-labelled tree under 3 shuffled orders plus an unshuffled control. No judge calls.
- **Why:** An audit flagged that the greedy builder may depend on processing order. This test measures how much.
- **What it tells us:** If order effects are as large as drawing a new data sample, the tree is fragile. If much smaller, the risk is bounded. Result: order dependence exists but is close to inert. Top-1 accuracy moves by only 0.25 points, against 2.6 points across data re-draws, and 85-86 of 86 leaves are recovered. Shown on the labelled tree only.

#### INTENT-S0-CARD-PROTOCOL — INTENT-S0-CARD-PROTOCOL (prompt arm only; K1-K5 fixed): at each embedder's EMBED-DIM-SLICE-selected slice ...

- **What it tests:** On three user-intent datasets (MASSIVE, CLINC, Banking77), re-embeds the questions with each embedder's recommended task prompt. It then compares how well k-means clusters match the fine intent labels for gemma against qwen3, and qwen3 with prompts against qwen3 without.
- **Why:** It asks whether the embedder choice, and the way inputs are prompted, changes the taxonomy the method discovers.
- **What it tells us:** It shows whether gemma's earlier edge is real or due to unfair prompting, and whether prompts help qwen3. Result: done and valid. With proper prompts, gemma does worse than qwen3 on MASSIVE and CLINC and better on Banking77, so the evidence on which embedder is better is mixed. The embedder of record is unchanged (the author's decision). Prompts did not raise qwen3's clustering quality when pooled across corpora (not shown). The effect varies by corpus and is descriptive; it does not show that prompts hurt.

#### INTENT-S0-SLOTSWAP-MECH — what carries S0-C4's slot-swap instability: origin margin (M1), swap share (M2), embedder (M3, descriptive) ...

- **What it tests:** On 3,222 MASSIVE intent queries whose slot words were swapped (e.g. a different city name), it asks what predicts a query jumping to a different k-means cell. Candidates are how close the original sat to a cell boundary and how much of the text was swapped, with a descriptive look at the embedder.
- **Why:** An earlier test found cells unstable under slot swaps. This test tries to explain why, and whether flagging near-boundary queries could help.
- **What it tells us:** If boundary closeness predicts flips, low-confidence queries could be flagged. If swap size predicts flips, the instability is driven by surface wording. Result: done. Both predict flips. Near-boundary queries flipped 55% of the time vs 8% for the safest fifth, and larger swaps flipped more even at fixed boundary distance. These are associations, not causes (swap share is mixed up with text length). Not shown: that boundary-gating fixes the problem. The embedder look is descriptive only, one seed, not a ranking.

#### INTENT-TRANSFER-S0 — known-answer stage 0 on MASSIVE en-US, CLINC150 (+OOS) and Banking77: embedder dependence against gold ...

- **What it tests:** On three intent datasets with known answers (MASSIVE, CLINC150 with out-of-scope queries, Banking77), split so no text is shared, it checks four things with k-means and no tree build: whether results depend on the embedder; whether "no match" flags out-of-scope queries; whether a label-free cell margin predicts how pure a cell is; and whether a cell stays the same when slot words in the query are swapped.
- **Why:** Checks against true labels whether the behaviours seen on MMLU-Pro (coarse level stable, fine level embedder-dependent) generalise, and whether label-free cells are trustworthy addresses.
- **What it tells us:** Confirms or narrows earlier MMLU-Pro claims. Result: fine structure depends on the embedder on all 3 datasets (nomic worse each time), while coarse differences stay within noise. "No match" detects CLINC's out-of-scope queries very well (AUROC 0.974, as good as a supervised method). The margin ranks cell purity on 2 of 3 datasets. But cells are not stable when slot words are swapped, so every filing rate of record now carries the note "surface-sensitive, untested on capability text". Short intent utterances only, one split.

#### PROFILE-TREE-ROBUST — does the sub-anchor capability profile survive a change of TREE? (H10's question, zero calls)

- **What it tests:** Takes the same 12-model verdicts and re-assigns them to cells under two different trees (87 leaves vs 47 leaves) built with different embedding settings. It then checks whether per-leaf model strengths agree between the trees beyond chance. No calls.
- **Why:** Asks whether the fine-grained, below-subject capability profile is real structure or an artefact of one particular tree.
- **What it tells us:** High agreement beyond chance would support reporting below the subject level. Result: done, corrected. The first 'structure is real' headline was withdrawn: the agreement came from subject-level structure the trees share. Where the trees actually re-cell questions, agreement is zero or negative. So no reproducible below-subject structure was shown. Later disclosure: the tree saw about 2% of evaluation questions during construction. Older judged question family, later ruled 'history, not evidence'.

#### SCALE-AGREE — label-free agreement between embedders across k (kNN overlap, k-means AMI, CKA), normalised by the qwen3 ...

- **What it tests:** Without labels, compares how two embedding models (qwen3 vs gemma) group the same texts, at increasing numbers of k-means clusters, on MASSIVE and CLINC. Scores are scaled against a near-copy of qwen3. No calls.
- **Why:** It asks whether different embedders agree at coarse levels but disagree at fine ones, which bears on whether the tree depends on the embedder.
- **What it tells us:** A clear trend would show where the embedders diverge. Result: the prediction failed. Agreement rises slightly with more clusters, but the method produces the same trend under a null, so it gives no label-free support either way. That is not a refutation. It does not say which embedder is better.

#### SUPERGPQA-STAGE0b — SUPERGPQA-STAGE0 with the 1,251 MMLU-Pro-colliding items (4.7156%) excluded and no A4 bar; POST-COUNT ...

- **What it tests:** On SuperGPQA, after removing the 1,251 questions that duplicate MMLU-Pro, it fits a per-discipline 'pick the best model' policy on training questions and tests it on held-out ones against the best single model. It also checks whether model strengths vary by discipline more than chance. No judge calls.
- **Why:** It asks whether the per-cell routing gain and the 'models differ by discipline' finding carry over to a new corpus.
- **What it tells us:** If both hold, the cell-conditional claims transfer beyond MMLU-Pro and the union. Result: done. The policy beats the best single model (DeepSeek-R1) by +0.65pp, but the lower bound is only +0.04pp and one interval form contains zero, so it is descriptive only. The discipline-interaction reliability is 0.64, clearly above the null of 0.10. This holds only for SuperGPQA minus the duplicates, never for SuperGPQA as a whole.

### State: UNDETERMINED (1)

#### EPOCH-NULL — FRAMEWORK item 15: the per-leaf null between consecutive seed builds (what a re-opening gate would see under ...

- **What it tests:** No calls. Using 21 trees built with different random seeds (plus 3 trees of the newer recipe), the test measured how much each leaf changes between consecutive rebuilds when only the seed and the data split change. It also measured a pure-chance floor.
- **Why:** It sets a baseline for how much a leaf 'moves' by chance alone, so a later rule for re-opening a cell after a rebuild is not triggered by noise.
- **What it tells us:** It shows what a re-opening threshold would flag under pure noise. Result: undetermined by design (a readout with no pass/fail criterion). Leaves overlap with their successor at a median of 0.57 to 0.67. A 0.66 per-leaf bar would re-open about half or more of the leaves from a seed change alone. The '0.66-0.69' figure quoted earlier holds for whole-tree agreement, not per leaf. The effect of a real growth step (adding data) was not measured.

### State: registered (2)

#### SLOTSWAP-DECISION — when a slot swap moves a MASSIVE item to another k-means cell, does the routed model stay the same more often ...

- **What it tests:** Planned check on the MASSIVE intent dataset: when swapping a slot word in a request moves it to another k-means cell, does the routed model stay the same more often than chance? No judge calls for the readout.
- **Why:** It tests whether routing decisions are robust even when cell membership is sensitive to surface wording.
- **What it tells us:** Held would mean addresses move but decisions stay. Failed would mean routing decisions are surface-sensitive too. Result: not run yet. It is registered but cannot run until a table of which models answer each MASSIVE item correctly exists. That needs a paid data step that has not been registered.

#### SUPERGPQA-STAGE0 — key only on declared disciplines (13 / 72 / 285), CK-CLOSE-v1 split at 0.30 EVAL per field: per-discipline ...

- **What it tests:** Planned to repeat the routing and profile checks on a second benchmark, SuperGPQA, using its declared disciplines and a content-closed train/eval split. It would ask whether a per-discipline best-model choice beats the best single model, and whether model profiles per discipline are reliable. No judge calls.
- **Why:** Tests whether the MMLU-Pro findings carry over to a different corpus.
- **What it tells us:** Would show whether the per-cell gains and reliable profiles generalise beyond one benchmark. Result: not run as registered. An admission check failed because 4.7% of items collide with MMLU-Pro, above the 2% limit. A version that excludes these items (STAGE0b) replaced it before any answer key was read.

### State: withdrawn (1)

#### E1-REPLICATES — is E1's nomic-vs-qwen3 anchor-free tree-filing gap (-0.0456) larger than the construction-seed spread at 4 ...

- **What it tests:** Planned to rebuild the anchor-free tree 4 times for each of two embedders to see whether the filing gap between nomic and qwen3 (-0.046) is bigger than the variation between build runs.
- **Why:** It asks whether the earlier filing loss belongs to the embedder or is just build-to-build noise.
- **What it tells us:** It would have separated a real embedder effect from build randomness. Result: WITHDRAWN before any data was collected. With a fixed data split, the build is effectively deterministic, so the test would only have measured a spread already known to be close to zero.

## Data hygiene

15 tests: are splits, pools, keys and caches clean enough to support the claims?

### State: done (14)

#### AGENT-CORPUS-ADMISSION — which agent corpus may enter the pipeline, under what rule set, and does the BFCL-Result 2025-12-16 ...

- **What it tests:** Writes a five-point rule set that an agent benchmark (tool-using AI agents) must pass before it may be judged, and applies it without any judge calls to one archive: 8 agents x 800 multi-turn tasks from the BFCL function-calling leaderboard (Dec 2025), using a 300-episode sample.
- **Why:** Extending the thesis from question answering to agents needs a gate so that unusable or badly specified agent data does not enter the evaluation pipeline.
- **What it tells us:** A pass would let agent data enter the pipeline; a failure names exactly what is missing. Result: done; NOT admitted as-is. Four of five rules were verified, but the per-episode size cap for what the judge would read was never declared (the author's decision), and all four task groups are description-only for now (the 'base' group passed only at its point estimate); nothing was ranked or judged.

#### BANNED-MODELS-REASON-CORRECTION — a dated [CORRECTED] comment inserted beside the false exclusion reason of the 6 text-less ...

- **What it tests:** A code-comment correction. Six models are excluded from the evaluation data, and the stated reason ('no answer text in the archive') was false. A dated comment was added saying the text exists under other field names that the loader never reads. The exclusion itself was left unchanged.
- **Why:** A false reason in the record could mislead readers or later analyses about why these models are missing.
- **What it tells us:** It keeps the record honest without changing any data or result. Result: done and merged. The six models stay excluded and the reasons are byte-unchanged. It does not show that those archives hold usable text beyond the first record checked. The wording in the thesis report is left to the author.

#### CHECKER-ANSWER-INGEST — FRAMEWORK item 7: ingest the checker's answers on the generative corpora; is MATH decidable (D_c >= 0.95) and ...

- **What it tests:** Loads the automatic answer checker's outputs for the MATH and IFEval benchmarks into a database. It then measures how often the key can decide a pair of models on MATH (18 models), and how many pairs would still have to go to the judge.
- **Why:** Before spending on judged MATH matches, it checks whether MATH is actually decidable by its answer key, as had been assumed.
- **What it tells us:** If MATH is decidable, the judge is barely needed there. If not, judged results on MATH need care. Result: FAIL. Under the reading of record only about 83% of MATH pairs are key-decidable, and about 80% would still go to the judge. The reason is a 1,024-token output limit in the test harness: many answers were cut off, and with that applied consistently decidability drops to 0.67. This was carried into later MATH work before any judged spend.

#### CLAIMS-SWEEP — every 'clean split' / 'clean reserved side' claim in the record, classified id-only or content-closed

- **What it tests:** A sweep of every statement in the project record that calls a data split or reserved question set 'clean'. Each is classified by whether it was only checked by question id or also by question text.
- **Why:** Pools were found to be separated by id but not always by content (duplicate question texts can sit on both sides), so 'clean' claims may be overstated.
- **What it tells us:** It shows which claims need a correction bracket and whether contamination reached any scoring. Result: done (no new calls). 80 unbracketed id-only 'clean' claims were found across 575 rows. A small number of near-twin questions sat in the tree's labelling and rubric material. The link problem never reached a scorer, and the remaining corrections are queued as a mechanical follow-up. It does not adjudicate all 80 rows (18 were sampled) and does not cover near-duplicates.

#### CONTENT-DISJOINT-SPLIT-AUDIT — are the pools of record content-disjoint, not only id-disjoint? (zero calls; DESCRIPTIVE audit)

- **What it tests:** An audit of whether the training and evaluation pools share questions with the same text, not only different IDs. It covers the union pool, the MMLU-Pro pool of record, 20 Newsgroups, BFCL and Multi-SWE. No calls.
- **Why:** If evaluation questions have text twins on the training side, tree-building and rubric writing may have seen them, which would weaken evaluation claims.
- **What it tells us:** Zero twins would make the splits clean. Twins would need to be disclosed, or the data rebuilt. Result: done (descriptive). The pools are ID-disjoint but not content-disjoint. 471 union evaluation IDs have an exact-text training twin, mostly GPQA and MMLU-Pro. On the MMLU-Pro pool of record, 37 exact (70 normalised) have one, and 31 judged questions are full copies. 20 Newsgroups, BFCL and Multi-SWE have no cross-side twins. The effect on any readout is not measured.

#### LINK-COPY-AUDIT — did any judged readout use the LINKED mmlu_pro row instead of the JUDGED eval row?

- **What it tests:** Audits whether any judged readout accidentally used the linked MMLU-Pro dataset row instead of the evaluation row that was actually judged. It also traces text twins into tree labelling and rubric-writing inputs. No calls.
- **Why:** A mismatch between the judged question and the scored row would corrupt accuracy and agreement numbers.
- **What it tells us:** No hazard means scorers are safe. A hazard would require re-scoring. Result: done. The link hazard never reached a scorer (scorers read the judged row, which agrees on all 3,445). But the tree of record was LLM-labelled and rubric-induced, and 28 judged questions had a near-twin in a leaf's rubric-writing corpus. Scorers were spot-checked, not exhaustively.

#### MATH-FIX — is the MATH corpus's near-zero accuracy a capability result or an answer-extraction artefact, and what does ...

- **What it tests:** Re-scores MATH answers with a more tolerant answer extractor. It accepts the last boxed answer, 'final answer is' or the last number, with numeric tolerance, and it only ever raises scores. Then it re-runs the routing evaluation on the corrected data. No calls.
- **Why:** Six models scored near 0 on MATH. That looked like an answer-extraction artefact rather than real inability, and it could inflate the measured routing gain.
- **What it tells us:** If zeros jump, the old numbers were artefacts and the routing gain must be re-estimated. Result: done, artefact confirmed. 21.7% of cells were corrected, and several models went from about 0 to 0.40-0.60. Routing per cell still helps in every seed, but less: +2.7 points on average instead of +5.0. A later re-read on the tree's own held-out pool gave about +3.4. That figure was itself replaced by a clean re-measurement of about +2.9, with policies fitted on training questions only. Pool separation was checked by question id only, not by content.

#### MODEL-VINTAGE-CANARY — when may a row still be called by a contestant's name? a DEFINITION of contestant drift and a null-first ...

- **What it tests:** The test defines how to detect that a contestant model has changed since its cached answers were recorded, using 279 canary questions. Its first step checked whether one answer-extraction rule reproduces the cached answers for 12 models. It then tagged each model with the evaluation harness it came from.
- **Why:** A leaderboard row may only carry a model's name if its answers still reflect that model and not artefacts of how they were extracted.
- **What it tells us:** It shows whether the cached answers can be trusted as a baseline for spotting model drift. Result: the preliminary steps are done. With one extractor, only 5 of 12 models reproduce. With each model's own harness rule, all 12 do, so the cached answers are harness artefacts and are now tagged by harness. The actual drift check needs new model generations and has not been run, so no model drift has been measured.

#### POOL-GUARD-IMMUTABLE — pool_guard.open_ro opens with mode=ro&immutable=1 after a -wal emptiness check, so a guard read leaves no ...

- **What it tests:** An engineering change: the tool that checks the reserved question pool now opens the database read-only, in 'immutable' mode, after first checking that no pending write log exists. It is verified on every pool of record. No judge calls.
- **Why:** Reading the database used to create side files next to databases of record, which risks silently altering or misreading the frozen pool that keeps arena questions out of construction.
- **What it tells us:** Confirms that the guard reads frozen pools without touching them and fails loudly rather than reading torn data. Result: done and merged. Output is byte-identical to the old guard on every pool of record and no side file is created. Known limits: it refuses some database modes, and it offers no protection against a concurrent writer (only a process rule does).

#### REGEN — can grok-4-1-fast-reasoning enter the arena fairly, given its answer-only traces were a third the ...

- **What it tests:** 3,445 model calls, no judging. Answers from grok-4-1-fast-reasoning were regenerated with the same step-by-step prompt the other contestants used. An admission rule was fixed beforehand: typical answer length within the contestants' range, and answer extraction above 98%.
- **Why:** Its original answers were a third as long as the others', so judging it as-is would be unfair (judges favour length).
- **What it tells us:** It decides whether the model can enter the arena on equal terms, and how much the prompt format alone changes accuracy. Result: done, admitted. Median length was 886 characters (contestants 503 to 1,474) and extraction 99.6%. Accuracy was 0.849, second on the pool. The prompt effect is about -1 point, far smaller than an earlier, retracted 4.6-point claim.

#### SPLIT-EXPOSURE-SENSITIVITY — how much does the recorded content leak move the recorded readouts it touches, measured against ...

- **What it tests:** For 13 recorded results that used questions whose near-duplicate copies leaked into the construction side, removes the exposed questions and re-scores each result. Each shift is compared with removing the same number of random questions from the same subjects (no judge calls).
- **Why:** Questions were split by id rather than by content, so some copies leaked. This measures whether the leak moved the results, to inform the author's rebuild-or-disclose decision (it decides nothing itself).
- **What it tells us:** Shifts no larger than random removals would mean the leak did not change results. Larger shifts would point to contamination. Result: on 12 of 13 results the shift is within random variation. One certificate-filter readout moved unusually: around the 99th percentile at the registered random stream, but only about the 90th when averaged over several streams. One flag in 13 is what chance gives about half the time. No recorded verdict changes, and this does not prove that no leak mechanism exists. It re-scores results on the older question pool, which is now ruled history, not evidence.

#### SPLIT-FUNCTION-IMPL — SPLIT-FUNCTION-IMPL (+ TRAIN-ONLY-TREE): FRAMEWORK item 18: the construction / arena split as a FUNCTION of ...

- **What it tests:** An engineering change. Whether a question is used for building the tree or for the arena is now computed from the question's own content, with a check on every row in both Kotlin and Python. Benchmark runs refuse trees not built on training-only data, and old toggle flags are retired.
- **Why:** Earlier incidents showed arena questions leaking into tree building. This makes the split a fixed function that can be checked, not a setting someone can change.
- **What it tells us:** It guarantees that the build and test sets stay separate for new work. Result: done. The invariants were verified and the pinned pools reproduce exactly. A later correction: the trees built earlier do NOT meet the training-only rule (some held-out texts were inside them). The worst-case effect on routing figures is at most about 1.3 points (combined pool) and 2 points (MMLU-Pro). Whether to rebuild or disclose is still the author's decision.

#### UNION-TREE-LABELLING-CHECK — did the union tree 20260911_144214 run labelling or rubric induction?

- **What it tests:** Audit of whether the multi-benchmark union tree, and the main tree, ran LLM labelling or rubric generation on text that included copies of judged questions. Zero calls.
- **Why:** If judged questions or their near-duplicates entered labelling or rubric prompts, rubric-based results could be contaminated.
- **What it tells us:** No labelling means the union tree is clean on that route; labelling with leaked copies means the affected results need disclosure. Result: the union tree and its six grafts ran no labelling or rubric generation. The main tree did: 28 judged questions had near-duplicate copies (with keys) in its rubric material, so that route applies to the rubric family of results. A separate text-matching hazard never reached any scorer.

#### VOTE-FRAME-CERT — for every dual-order cache in the record, which stored vote column is POSITIONAL, which (if any) is ...

- **What it tests:** An engineering audit of every stored dual-order judging cache, row by row. It certifies whether each vote column records the screen position (left/right) or the named model, so that no statistic mixes the two.
- **Why:** Position-bias and order analyses are wrong if they mix position-labelled and model-labelled votes.
- **What it tells us:** Result (no new calls): the certificate holds and was independently reproduced to the digit. No cache mixes frames. One cache could not be certified because of commit timing. One backup copy was misclassified because of its filename, an instrument artefact. It certifies frames only, not any bias number, and 11 caches are not backed up.

### State: built (1)

#### DATASET-SURVEY — the admission table for a keyed second corpus (>= 20 complete models; >= 120 EVAL per scored stratum ...

- **What it tests:** Builds an admission table of candidate datasets for a second corpus with an answer key. Each candidate is checked on sourced conditions: at least 20 complete models, enough evaluation questions per cell, a closable content-overlap check, a key, a stated licence and the needed protocol columns.
- **Why:** The thesis needs a second keyed corpus to show results are not specific to MMLU-Pro. This survey decides which candidate (SuperGPQA first) may enter.
- **What it tells us:** It would say which datasets are admissible and why the others fail. If SuperGPQA failed any condition, the second-corpus claim would become a stated limit. Result: built, not yet run as a result. Only the SuperGPQA row is filled, and it is provisionally admitted. The final analysis is deferred until the 14 other rows are complete. No result of record yet.

## Engineering/infrastructure

20 tests: tooling, guards and determinism checks the experiments depend on.

### State: done (17)

#### ARCH-V2-INDUCE-RUBRIC-1 — one MCQ rubric artefact induced from gen_view TRAIN of the split of record (recipe component)

- **What it tests:** One automated run that asks an LLM to write a grading rubric for multiple-choice questions, from 40 training questions of MMLU-Pro, to be plugged into the new (v2) judging recipe.
- **Why:** The v2 judging pipeline needs a rubric component before its pilot can run; this test produces and checks that component.
- **What it tells us:** It tells whether the rubric-writing step works mechanically, not whether rubrics help. Result: done; the artefact was produced on the first try and passed its formal checks, but a review found it grades the answer format (a bare letter), not the answer itself, so it was NOT ADOPTED and a second induction was ordered. It makes no claim about rubric value or accuracy.

#### ARCH-V2-INDUCE-RUBRIC-3 — a THIRD induction of ONE MCQ rubric artefact for E-J's $rubric slot (ARCH-V2-PILOT-K46 and stage 1), the same ...

- **What it tests:** A third attempt to have an LLM write one grading rubric for multiple-choice questions. It used the same 40 training questions, a revised prompt and a fresh screening check, and then ran a fitness checklist on the result.
- **Why:** The new judge recipe has a rubric slot, and the earlier rubric attempts were judged unfit for use.
- **What it tells us:** A fit rubric would fill the slot. An unfit one sends the slot to a pre-chosen generic rubric. Result: done. A valid rubric was produced on the second try, but both blind reviews found it unfit: its last line asks for verdict wording the parser rejects, and one review also saw too many ties. It was not adopted, and the generic rubric was used instead. This is a recipe component and makes no claim about rubric value or accuracy.

#### ARCH-V2-STAGE1-ANCHOR-DRAW-2 — ARCH-V2: the stage-1 anchor RE-DRAW on the ARCH-V2-SPLIT-DRAW-2 supply (7 of the 14 MMLU-Pro anchors ...

- **What it tests:** A one-time random draw with no model calls. Using a pre-registered seed, it picked which 7 of the 14 MMLU-Pro subject areas form stage 1 of the new (v2) architecture, stratified by size. It was redone on the new data split.
- **Why:** It fixes the stage-1 subjects in advance and at random, so that later results cannot come from choosing subjects after seeing the data.
- **What it tells us:** It produces a fixed, auditable list of subjects. A mismatch with the reviewer's independent prediction would have voided the draw. Result: done. The subjects are chemistry, computer science, economics, health, math, other and philosophy. They match the reviewer's prediction. This draw replaces the first draw for future use. It says nothing about stage-1 results.

#### ARCHV2-SELFTEST-CLOCK-FIX — tools/analysis/archv2_pilot/selftest.py injects the fixture clock (clock=lambda: TODAY at L886) so that all ...

- **What it tests:** Changes the self-test of the version-2 architecture pilot tool so it uses a fixed test date instead of the real calendar date. Then checks that all 282 checks pass on any day. No calls.
- **Why:** Some self-test checks depended on today's date, so the suite could fail or skip checks on the wrong day. Other work needed date-independent tests.
- **What it tells us:** Passing means the self-test is reproducible whatever the date. Result: done and merged. 282 checks pass, 0 fail, on any date. One limit stays open: the self-test cannot yet catch a future slip back to the real clock. A follow-up trap test was drafted for that.

#### E1-ROUTE — the JVM working-copy route for EMBEDDER-CROSS-FLAT E1 (RP09): per run, a pin-checked throwaway copy of the ...

- **What it tests:** An engineering check. The tree-building program (a JVM) must read embedding files only through a throwaway working copy that is hash-checked before and after each run. Pinned and source embedding files must never be opened directly.
- **Why:** The embedder-comparison experiment needs proof that building a tree cannot silently modify the frozen embedding files that other results rely on.
- **What it tells us:** Success means the embedder-comparison builds can be trusted not to corrupt pinned data. A failure would block those builds. Result: done. The route held: no protected file changed in the trial run or in any of the embedder-comparison builds. Engineering only, no science claim.

#### EVAL-METRIC-DETERMINISM — compute TotalDasguptaCost, TripletAccuracy, DendrogramPurity and the spherical silhouette in a canonical ...

- **What it tests:** Makes four tree-quality metrics process questions in a fixed order. It then checks whether three repeat builds of a small AG_NEWS tree give byte-identical quality files and leave every other output unchanged.
- **Why:** Tree-quality numbers drifted slightly between identical builds, which made small comparisons between configurations unreliable.
- **What it tells us:** If the files match, the drift came from processing order and is now fixed. If they don't, there is another cause. Result: 0 of 6 comparisons differ and 0 of 24 other outputs moved, so the files are byte-identical over 3 repeat builds. This is not a claim of full determinism. Numbers from before the fix cannot be compared digit for digit with numbers after it.

#### FRAMEWORK — a framework to judge and rank every model on every question, designed from the record as it stands at v100 ...

- **What it tests:** A design document (docs/design/FRAMEWORK.md), written by a multi-agent workflow from the results ledger. It is a framework for judging and ranking every model on every question. Every rule is traced to a recorded result and its current status. No calls.
- **Why:** Before spending on more judged runs, the project needed one consistent design that uses no withdrawn result and states its limits.
- **What it tells us:** It gives the rules to follow, the open limits, and the tests to register first: 19 zero-call and 5 judged. Result: done. Three record errors were found and fixed at synthesis, and some framework lines were later corrected. It is a design, not evidence. Its references to arena-pool judged numbers are design provenance only. It refuses a frontier order, sub-cell rows and the word 'calibrated'.

#### GUARD-22-RENAME-PROOF — does the per-arm local rename in SeparationNullBySizeTest leave the site-null output BYTE-IDENTICAL? ...

- **What it tests:** Checks that renaming local variables in two copy-pasted blocks of a split-significance test does not change its output. The site-null CSV is produced before and after the rename and compared byte by byte (no judge calls).
- **Why:** The two blocks were identical, so an edit could land in the wrong one and still compile. The rename removes that hazard, but only if it is truly inert.
- **What it tells us:** Identical outputs, plus proof that the renamed code actually ran, show the rename is safe. Any byte difference would mean the two arms were not independent. Result: done, passed. The CSVs are byte-identical, and compiled classes show the new code ran. This covers the 'site-null' arm only and fixes one instance of the hazard, not the whole class.

#### JUDGE-FINISH-AUDIT — FRAMEWORK item 19 / process rule 10: which caches of record can tell NON_TERMINATED from wrong, and does the ...

- **What it tests:** Checks 58 stored judge-verdict caches (about 158,000 rows) for whether they record why a judge answer ended: finished normally, cut off by the length limit, or blocked by a content filter. It also fixes the shared judge-call code to keep provider IDs and store refusals. No judge calls.
- **Why:** A cut-off judge answer can look like a wrong verdict. The thesis needs to know whether its stored results can tell the two apart.
- **What it tells us:** This shows which results can be checked for truncation, and it prevents silent data loss in future runs. Result: only 7 of 58 caches record the finish reason. All main boards are among the 51 that cannot tell a cut-off from a wrong answer, apart from crude proxies. Future calls now record provider IDs and store refusals as unusable rows. The per-model length probe was not run.

#### JUDGE-WIRING — FRAMEWORK item 25: does the Kotlin production path, posting the STACK-v2 recipe to grok, reproduce the Python ...

- **What it tests:** Re-judges 600 matches through the production Kotlin arena, now wired to the newer judge and prompt recipe. It compares the verdicts with the Python research scripts on identical inputs (1,200 calls).
- **Why:** Every judged result since the new judge recipe came from Python scripts, so the production path had to be shown to give the same verdicts.
- **What it tells us:** A pass would allow mixing results from both paths. A fail means only a whole-board re-judge can be trusted. Result: done; FAIL as registered under one of the two tie-counting rules (-2.6 points, outside the 1.9-point bar). Under the other rule it was within the bar. Both paths sent identical bytes, so the gap is the provider's own randomness plus how ties are counted. A later whole-board re-judge found the two paths act as the same instrument within the judge's known noise floor.

#### JV2-PARALLEL-POSTING — a bounded worker pool for the judge_v2 posting path (two-phase transport, journal v2, live rate control) ...

- **What it tests:** An engineering change: a bounded worker pool with live rate control that lets the version-2 judge send several calls at once. It was checked against all safety guarantees (journal, no double counting, ceilings, preflight) and checked to give byte-identical behaviour when run with one worker.
- **Why:** Judging is slow when calls go one at a time. Speed must not cost any guarantee about the recorded verdicts.
- **What it tells us:** Result: done and merged (no live calls). With one worker it is byte-identical to the old path, and no deliberately injected bug went undetected. At the default rate limit the speed-up is at most about 1.17x. It does not show that concurrency leaves live judge verdicts unchanged, or that more workers are safe on a given day. The first live parallel run must declare its settings in advance.

#### JV2-RATE-PROBE — at how many concurrent in-flight calls N in {1, 2, 4, 8, 12} does the grok-4-1-fast-non-reasoning deployment ...

- **What it tests:** Sends up to 398 synthetic judge requests to the grok-4-1-fast-non-reasoning deployment at 1, 2, 4, 8 and 12 parallel calls, measuring throughput, rate-limit errors and latency.
- **Why:** Decides whether it is worth building a parallel caller to make judged runs faster; it says nothing about judge quality.
- **What it tells us:** A large speed-up would support parallel posting. None would keep runs sequential. Result: done. On one night, 12 parallel calls ran about 10x faster than 1, with zero rate-limit errors. The registered falsifier fired: the good conditions of an earlier night had returned. The decision to build the parallel caller had already been taken by the author regardless of this result, so the probe measures the limit rather than deciding the build. 12 is a lower bound, measured on one night only and on the non-reasoning model only. It licenses no daytime run, where limits were much worse earlier.

#### LCB-D9-BYTE-INERTNESS — is the LCB Kotlin of 4497373 (four src/main blobs) BYTE-INERT on the AG_NEWS smoke construction, leg A ...

- **What it tests:** An engineering check. It asks whether merging four code files that add LiveCodeBench support changes any output byte of a small AG_NEWS tree build, by comparing the build before and after the change.
- **Why:** New code must not silently change existing trees before it is merged.
- **What it tells us:** Identical outputs would clear the merge. Differences would block it, unless they come from run-to-run randomness. Result: done. The check failed as registered: 2 of 21 files differed, in three quality metrics. A repeat of the old code alone showed the same differences, so the cause is non-determinism in those metrics, not the change. The 19 other identical files are descriptive only, the merge was not done, and the question moved to a follow-up test.

#### LCB-D9B-BYTE-INERTNESS — is the LCB Kotlin of 6b9fc7c BYTE-INERT on the AG_NEWS smoke construction on every output field not declared ...

- **What it tests:** Runs the small AG_NEWS smoke construction before and after a code change to four Kotlin files that added LiveCodeBench support. It compares every output byte against a run-twice control on the old code. No calls.
- **Why:** A merge gate: the new code must not silently change existing construction outputs.
- **What it tells us:** Any unexpected difference would block the merge. Result: passed. The outputs are byte-identical on every compared field, except three evaluation metrics already known to vary from run to run, which were not tested. This is based on one before/after pair and one determinism pair only.

#### NOISRESERVED-TEST-ALLOWLIST — a line-level allowlist in NoIsReservedInSourceTest for the 7 recorded data_v2 hits (the red on main since ...

- **What it tests:** Fixes a source-code guard test that had been failing on main. The test now allows exactly 7 known, recorded lines, while any new matching line still fails. Mutation tests confirm it behaves this way.
- **Why:** A guard test that is always red hides new problems. This makes it green again without weakening it.
- **What it tells us:** A green, strict test restores protection against code that mishandles reserved (held-out) data. Result: done and merged, and the known failure on main is cleared. Caveats: some swap cases may not be caught, and a plain Gradle run can skip the test after tool changes, so a clean rebuild is required.

#### PERF-8-MEMO — cross-iteration proposal memo (perf review 2026-09-09 item #8): implemented behind a fail-closed TOML flag ...

- **What it tests:** The test added an optional cache of split proposals to the tree-building engine, off by default, then rebuilt the tree with it off and on. It checked that the tree comes out identical and measured the time saved.
- **Why:** A performance review estimated the cache could save about 37% of one build phase.
- **What it tells us:** It shows whether this speed-up is real and safe. Result: done. Safe, since the tree is byte-identical, but useless: 0 cache hits, because the graph changes every iteration, and the build is 49 seconds slower (55% overhead). The cache stays off and the item is closed as negative.

#### VFC-FIXES-2 — vote_frame_cert.py D1-D5 of review 9d3e261 plus R-1..R-9 of VFC-RX-RULING (and D5 in position_index_all.py) ...

- **What it tests:** Fixes and re-reviews the vote-certification script (and one helper), with self-tests and deliberately broken copies (mutants) to show each fix is exercised. It then re-derives the existing certificate and two dependent results to check that only the expected differences appear. No calls.
- **Why:** Several results reuse this instrument. It had to be correct before reuse.
- **What it tells us:** Clean passes license reuse. Any unexpected difference would be a finding. Result: done. The fixes were merged after all mutants were killed. The re-derivation checks passed with only the expected differences, so reuse by three dependent tests is licensed. The certificate was not re-issued.

### State: blocked (1)

#### THREAD-CAP — -XX:ActiveProcessorCount=N forwarded to the siteNull and bootRun forked JVMs (fail-closed -PjvmThreads) ...

- **What it tests:** An engineering check. It caps every tree-building JVM and embedding run at 12 processor threads (half the machine), and checks that capped runs give byte-identical significance-test results and identical trees whether run with 12 or 8 threads.
- **Why:** The author wants half the machine kept free, and the cap must not change any result.
- **What it tells us:** Passing shows results do not depend on the thread count, so the cap is safe to adopt. Result: blocked, not finished. The JVM legs passed: identical null-test output, trees deterministic, and the same at 12 and 8 threads (small AG_NEWS build only). The embedding-server (Ollama) leg was not run, and the standing adoption of the cap waits for the author.

### State: built (1)

#### EMBEDDER-PLUMBING — fail-closed -DembeddingCacheFile forwarded to the site null, a canonical-name cache guard, the vmfMu cosine ...

- **What it tests:** Engineering work to safely switch embedding models in the pipeline: explicit cache-file flags that fail closed, a check that the cache matches the model name, and a cosine-similarity guard (at least 0.99) before any other embedder is used. The default model's path must stay byte-for-byte unchanged.
- **Why:** It is needed before any test can compare embedders (invariance) without silently reading the wrong embeddings.
- **What it tells us:** Working guards make later cross-embedder results trustworthy. Missing guards could mix up embeddings. Result: built, not finished as a test. Code is merged, one guard check passed (minimum cosine 0.9996), and the embedding caches for the other models were written. This says nothing yet about any embedder result.

### State: withdrawn (1)

#### STAGE3-MATH — Block 2 (f), FRAMEWORK item 23: the judged Stage 3 spend on the MATH cell, HELD before any call (zero calls) ...

- **What it tests:** A planned paid judging run (up to 3,000 matches) on the MATH cell. It was stopped by its launch gate before any call: many MATH answers had been cut off by a 1,024-token generation limit, and the rules forbid judging cut-off answers.
- **Why:** It guards against a judged result driven by truncated answers rather than model ability.
- **What it tells us:** It shows the gate works and decides which population may be judged. Result: withdrawn (held, zero calls). It was re-registered on the questions where both answers finished (STAGE3-MATH-CAPFREE), which passed. The original population stays unjudged.
