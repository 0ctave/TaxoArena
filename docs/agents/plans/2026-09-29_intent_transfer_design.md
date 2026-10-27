# INTENT-TRANSFER: a known-answer foundation study for the construction (design; not registered)

Written 2026-09-29 by the research lead at HEAD 32c4c72 (ledger v314). Zero judge calls, nothing run. This is a plan
file, not a record file. The registration draft in section 7 goes to the registrar, who commits it once the author has
decided D1 (section 10). It does not bind anyone until then. Web facts (licences, sizes, prior work) come from one
research agent's check of primary sources on 2026-09-29. Where it marked something UNVERIFIED, this file says so too.

## 0. The author's request, and how it is read

The author, 2026-09-29, verbatim as relayed: "Maybe this could be run first to tests the relevence of this part, having
a really coherent ground for the rest of the framework is really precious. It might allow to see the limits, the
improvements, the overlap of domains and soft routing or cross routing relevence and maybe mroe, research that".
Plan Amendment 28 places "INTENT-TRANSFER stage 0 BEFORE RP12 in the machine lane" (prog L22019-L22026, the
orchestrator's reading).

The reading here: every construction readout of record is scored against declared categories (MMLU-Pro's 14, the
union's 52 strata), against a flat mixture (FLAT) or against its own site null (certificate). None of these is a known
answer at two levels. 20NG (TOPIC-PARTITION-20NG) came closest, with 20 labels under 7 groups. It was scored at the leaf
level only (C1 tie with k-means), plus one fragile certificate-alignment reading. Intent corpora have a designed
two-level hierarchy, short and templated texts, an out-of-scope class and slot annotations. This lets the record
adjudicate things it could not before:
- which embedder is right, not merely different (EMBEDDER-CROSS-FLAT could only say "worse on MMLU purity");
- whether no-match detects out-of-scope;
- whether a cell is a stable address for a query;
- whether a label-free statistic tells meaningful cells from arbitrary ones;
- whether the tree's hierarchy adds anything beyond its leaves.

**The honest limit, stated first.** A gold coarse level (MASSIVE's 18 scenarios, CLINC's 10 domains) is one designer's
taxonomy. Several of its classes are functional grab-bags, not topics: MASSIVE "general", "qa" and "play" (play_music
sits beside music_query); CLINC "utility", "meta" and "small_talk". So failing to recover the coarse level is NOT, on
its face, a defect of a construction. Stage 0 therefore measures how GEOMETRIC each gold level is (D2) before any tree
is scored against it. Stage 1 scores trees relative to flat baselines at matched k and relative to that ceiling, never
on absolute recovery alone. The fine level (intent) is the strong known answer.

## 1. What the record already says, and what this study builds on (read from results JSONs, 2026-09-29)

| result | what it says | what INTENT-TRANSFER adds |
|---|---|---|
| TOPIC-PARTITION-20NG (C1 FAILED, F1 fired) | the tree ties k-means at the same k on NMI(20): -0.0020 vs a spread of 0.0074; the certificate is topic-informative only at the registered instrument (11 effective site-pairs; a size control takes p to 0.13) | a two-level known answer; the hierarchy scored beyond the leaves (T-C2); certificate alignment re-read with the size control registered up front (T-C5) |
| TOPIC-PARTITION-20NG-T1B-NULL | 512 / 0.0145 builds but does not certify on 20NG | stage 1 arms keep the recipe per arm (AF 256 / 0.025; anchored 512 / 0.0145) and never rank the two recipes (ban (b)(5)) |
| FLAT-MIX-MMLU, FLAT-GENERALITY (RP05) | af_clean_s42 is worse than a flat vMF mixture at k 82; the loss appears in 2 of 3 re-draws on M1 only; af_s137 clears its bar by 0.0026 (thin); the anchored control O is not fired | a partition test on corpora whose fine labels are the answer (T-C1), with the anchored arm scored as well |
| CERT-REDRAW-R512 (RP06) | the certified set depends on the draw (s2048 empty) | any certificate claim on an intent tree carries one re-draw (salt 2) from the start (T-C5) |
| EMBEDDER-CROSS-FLAT E0b | at k 14 nomic and gemma are not shown worse on M2; at k 82 nomic is WORSE; every cross-arm contrast is DESCRIPTIVE-ONLY, and "gemma better" is forbidden | the same coarse-vs-fine pattern against GOLD labels, where "better" becomes a registered symmetric readout (S0-C1) |
| V2-DECLARED-CELLS (RP03) | the declared-cell gain +2.67pp is carried by BBH (0.728); leave-BBH-out contains 0 | nothing directly: intent corpora have no models. The study separates FILING quality (measurable here) from ROUTING GAIN (not measurable here) |
| MC-FED / MC-ROOT / MC-LEAF / ROUTER-CLEAN-POLICY | federation recovers certification (13 vs 5); flatLeaf files 81.6% vs 72.1% by descent (id-disjoint only); leaves lose to domains as a router; M +0.17pp [-0.61, +0.95] | flatLeaf vs descent against gold (T-C8); a union of intent corpora with KNOWN cross-corpus overlap (CLINC banking / credit_cards vs Banking77) for the absorption mechanism (stage 1b) |
| ROUTING-ATTENUATION | misrouting shrinks contrasts proportionally (slope 0.795 at 19%) | a posterior over cells and selective filing as the mechanism the record has not tried (S0-D4, stage 2) |
| Huot, Kaisers & Lapata, arXiv 2607.09197 (resolves; "When is Routing Meaningful? Diversity and Robustness in Language Model Societies") | routing is meaningful only if actors differ (Hierarchic Social Entropy, HSE, computed from per-actor correctness vectors) and the router is ROBUST (surface variants go to the same actor); kNN routers gain accuracy but lose robustness. HSE is NOT label-free | the robustness half transfers to cells with a known answer: slot-swap stability (S0-C4). The diversity half (HSE) is read on the union roster at zero calls (stage 2, descriptive). The label-free predictor is this study's own (S0-C3) |

## 2. Corpora (primary-source check 2026-09-29; the steward's census at READY supersedes every count)

| corpus | licence | size | hierarchy | role | hazards |
|---|---|---|---|---|---|
| MASSIVE en-US (`AmazonScience/massive`) | CC-BY-4.0 | 16,521 (11,514 / 2,033 / 2,974) | 18 scenarios / 60 intents; slot annotations (`annot_utt`) | primary; two levels; slot-swap robustness | localised from SLURP, whose text is the Liu et al. 2019 (HWU64) data |
| CLINC150 (`clinc/clinc_oos`, "plus") | CC-BY-3.0 | 22,500 in-scope (150 x 150) + OOS 250 / 100 / 1,000 (the OOS counts are the research agent's arithmetic from the card totals, UNVERIFIED as a card statement) | 10 domains / 150 intents + `oos` | primary; two levels; out-of-scope | documented ID/OOS mislabels (Podolskiy et al. 2021) |
| Banking77 (`PolyAI/banking77`) | CC-BY-4.0 | 13,083 (10,003 / 3,080) | flat, 77 intents in one domain | fine-granularity stress, no coarse level | label errors documented (Insights 2022; found, not read) |
| HWU64 (`xliuhw/NLU-Evaluation-Data`) | CC BY 4.0 | 25,716 | 64 intents; "21 domains" (secondary sources only) | NOT an independent replicate: same source as SLURP and MASSIVE. Used only for the steward's cross-corpus twin count | large exact / near-exact overlap with MASSIVE-en expected (rate UNVERIFIED) |
| BlendX (`HYU-NLP/BlendX`) | GPL-2.0 (repo) | BlendCLINC150 54,896 / 2,889 / 2,977 over 147 intents; about 50% two-intent | multi-intent gold | cross routing with natural multi-intent text (stage 1+ only) | built with ChatGPT; utterances duplicated by the authors' own statement; source overlap with CLINC150 / Banking77, which is a twin hazard across corpora |
| WildChat-1M / 4.8M (`allenai/WildChat-*`) | ODC-BY (changed from ImpACT, retroactive); not gated (the Full, toxic-included set is gated) | about 838k rows (1M) | none | stage 3 descriptive occupancy only | personal data: hashed IPs, `redacted` flag; PII removal not verified |
| LMSYS-Chat-1M | custom agreement, gated; no redistribution; no re-identification; deletion on request | 1M | none | NOT recommended | an English subset could never be published |

Prior work used as prediction anchors (verified by the research agent):
- k-means on Instructor embeddings: CLINC NMI 91.5, Banking NMI 81.7 (Viswanathan et al. 2023, arXiv 2307.00524).
- k-means on averaged GloVe: CLINC NMI 70.89 / ARI 26.86 (DeepAligned, arXiv 2012.08987).
- CLINC OOS AUROC 97.1-98.4 for fine-tuned detectors (Podolskiy et al. 2021, arXiv 2101.03778). No verified label-free off-the-shelf number exists (UNVERIFIED).
- Dendrogram purity (Heller & Ghahramani 2005) needs only flat gold classes.
- No cited level-wise gold-hierarchy measure was confirmed. The level readouts below are therefore defined here and registered as ours.

## 3. The questions: measure, baseline, falsifier, support, meaning

Notation:
- EVAL / GATE / TRAIN are the hash sides of section 5.
- K_c and K_f are the gold coarse and fine counts: MASSIVE 18 / 60; CLINC 10 / 150; Banking77 has only K_f = 77.
- "spread" is the max-min over k-means seeds 0-4.
- "bar" is max(MDE80, spread).
- n planning values are pre-census estimates: MASSIVE EVAL about 4,890; CLINC in-scope EVAL about 6,750 plus OOS about 1,350; Banking77 EVAL about 3,925. DEFF 1.05 is declared (exact-duplicate components only) and is measured at the run.

### (a) Does the construction recover a gold hierarchy, level by level, against flat k-means at the same k?

Stage 0 cannot answer this (there is no build). It supplies the ceilings and the baselines (S0-D1, S0-D2). Stage 1
answers it with three readouts.

**T-C1: leaf partition.**
- Measure: NMI(fine) of EVAL items filed flatLeaf into the tree's L leaves.
- Baseline: spherical k-means at k = L on the same TRAIN rows, seeds 0-4.
- HELD iff the difference exceeds the spread AND the component-bootstrap CI excludes 0.
- L1 fires if the difference is below -bar with the CI below 0.
- Falsifier: an L1 fire on both hierarchical corpora extends FLAT-MIX-MMLU's partition clause from MMLU-Pro to a known answer.
- Support: n about 4,890 / 6,750; planning NMI SE 0.004; spread 0.010 (20NG 0.0074, rounded up); bar 0.0112.
- SCOREABLE only if the true difference exceeds the spread (the structural leg: the spread does not shrink with n).
- Prior: tie (20NG), so predicted FAILED with L1 not fired.

**T-C2: the hierarchy beyond the leaves (a mechanism the record has not measured).**
- Measure: dendrogram purity against the gold COARSE labels.
- The tree's own hierarchy is compared with two others over the SAME leaves:
  - (i) average-link agglomerative clustering on the leaf centroids;
  - (ii) 200 random binary hierarchies (the floor).
- This isolates what the construction's top-down cuts add over a post-hoc hierarchy on its own leaves. FLAT tests the partition only.
- HELD iff DP(tree) - DP(agglomerative) exceeds the tree's draw spread (from the two order-shuffle arms) with the CI above 0.
- Falsifier: DP(tree) inside the random-hierarchy p95 means the tree's upper structure carries no gold-coarse information on that corpus.
- Support: SCOREABLE if the predicted gap is at least 0.02 (planning SE 0.005, MDE80 0.014).
- Predicted: tree about equal to agglomerative (UNDETERMINED); both far above random.
- Anchor-free arms only: in the anchored arm the coarse level is supplied, so DP(coarse) there is trivial.

**T-C8: filing rule against gold.**
- Measure: flatLeaf vs descent fine-label filing precision, paired. This is MC-ROOT's contrast with a known answer and a content-closed split.
- Support: discordance about 0.12, difference about +0.05; SE about 0.005; SCOREABLE.

For SQ3: this is the first known-answer reading of the partition, hierarchy and filing clauses. It is what F-TAX's
sentence "not partition quality" and the filing clause could be checked against outside MMLU-Pro.

### (b) Where does it fail: granularity, short texts, embedder?

**Embedder: S0-C1 (stage 0, deciding).**
- Measure: k-means NMI against gold at K_c and at K_f under qwen3, nomic and gemma (RAW, slice 256 renormalised, E0b-conformant; slice 512 printed).
- Question: does "coarse holds, fine is embedder-dependent" (E0b) reappear when the answer is known, and is qwen3 the RIGHT embedder or only the incumbent?
- Support: SCOREABLE at the fine level (predicted -0.02 to -0.03 against bar 0.0112).

**Granularity.**
- Stage 0: NMI against K at 0.5x, 1x and 2x the gold count (descriptive curve).
- Stage 1, T-C3: per-intent own-leaf rate against TRAIN size.
- The mechanism to test is the size-dependent separation bar ("p95 falls with n"): small nodes cannot pass, so fine intents with about 90 TRAIN members (CLINC) should merge.
- Prediction: CLINC AF leaves 60-110, well below 150.
- DESCRIPTIVE (about 45 EVAL items per CLINC intent); the registered slope sign is the only scored element.

**Short texts.**
- EVAL filing accuracy by token-length quintile (S0-D6).
- DESCRIPTIVE: length is confounded with intent and corpus. The cross-corpus comparison with 20NG is never scored.

For SQ5: a corpus-and-embedder axis with a known answer. The E0b pattern is either confirmed as a method property or
narrowed to MMLU-Pro.

### (c) Domain overlap: confusable scenarios and intents, and whether the tree tracks it

**Stage 0 (S0-D3, descriptive).**
- The gold overlap map: the fine-label confusion matrix of TRAIN-centroid filing, aggregated to coarse pairs.
- The within-coarse share of the confusion mass. Predicted: majority within scenario for MASSIVE (set / query / remove share their noun); a cross-scenario block for play vs music, and for alarm vs calendar vs reminder.
- The top-20 confusable pairs.

**Stage 1, T-C4.**
- Measure: Mantel correlation between gold pairwise confusion and tree distance (LCA depth between the intents' modal leaves).
- Null: an intent-label permutation test. SCOREABLE against that null.
- The tree vs agglomerative-hierarchy contrast is DESCRIPTIVE.

**Stage 1b (union of intent corpora).**
- The known cross-corpus overlap: CLINC "banking" / "credit_cards" against Banking77.
- Absorption rate in a joint loop against the federated construction: the N4 / MC-FED mechanism with a known answer.
- DESCRIPTIVE unless the steward's counts support it.

For the framework: whether "overlap of domains" is something the tree SHOWS (by structure) or only something it
SUFFERS (as misfiling).

### (d) Soft routing (a posterior over cells) and cross routing (a query in two cells)

**Soft routing: S0-D4 (stage 0, descriptive).**
- Posterior: vMF responsibilities over k-means cells, with the concentration fitted on GATE by NLL.
- The cell -> fine-label policy (TRAIN majority, the structural analogue of the per-cell model policy) is compared hard vs soft, where soft = argmax_y of sum_c P(c|q) P(y|c).
- Also read: Brier score; and the coverage-precision curve of SELECTIVE filing by posterior margin (abstain to a global default).

Why descriptive:
- soft vs hard on a proper score is near-guaranteed by construction (hard is the kappa -> infinity limit of the fitted family);
- on argmax accuracy the predicted gain (+0.2 to +0.5pp) is inside the MDE (about 0.8pp).
- The deliverable is WHERE the posterior mass sits (the confusable pairs of (c)) and what selective filing buys at 80% / 90% coverage.
- A test that would spend effort to land inside its own MDE is declined as a deciding criterion (the BFCL-JUDGED-PILOT lesson).

**Cross routing: S0-D5 (stage 0, descriptive).**
- Synthetic two-intent queries: 1,000 EVAL-EVAL pairs from different coarse labels joined with " and " (registered seed; never TRAIN).
- Read: top-2 cell recall of both gold intents; AUROC of posterior entropy for single vs pair.
- Synthetic concatenation is not natural multi-intent text, which is why this is descriptive.
- BlendX gives natural text but is GPL-2.0 and ChatGPT-built (author decision D3).

**Stage 2 (capability side, after RP12).**
- Posterior-weighted per-cell policy against hard filing on the v2 union tree, on G14's machinery.
- Predicted |soft - hard| of about 0.2pp against an M-scale MDE of about 1.1pp, so DESCRIPTIVE-ONLY; it is registered only as a curve.
- Cross routing on the capability side needs a notion of a two-cell question that the union's declared cells do not supply, so it is not proposed.

Relation to the record: the r8-era polyhierarchy (DAG bridging) negative is history, not evidence, and not a closed
line. A query-level posterior is a different mechanism (membership per query, not multi-parent nodes).

For the framework: whether a posterior and selective filing answer ROUTING-ATTENUATION's proportional shrinkage. On
intent corpora this is measurable against truth; on capability it is only descriptive.

### (e) No-match as out-of-scope detection

**S0-C2 (stage 0, deciding), CLINC150.**
- Score: max cosine to label-free k-means centroids (K = 150, in-scope TRAIN only); the threshold is set at 95% in-scope TPR on GATE.
- Read: AUROC and FPR95 for in-scope EVAL vs OOS. All OOS rows go to EVAL (never fitted); any OOS row whose stem_key collides with an in-scope row is dropped.
- Printed beside: supervised TRAIN-centroid max-cos; K in {50, 100, 300}.
- Support: n_OOS about 1,350, n_in about 6,750, AUROC about 0.9; Hanley-McNeil SE 0.0059 x sqrt(1.05) = 0.006; MDE80 0.017; the bar 0.85 is 0.03-0.05 from the prediction, so SCOREABLE.
- Stage 1: the tree's leaf centroids against k-means at k = L, paired. DESCRIPTIVE (predicted tie).

For the framework: a calibrated no-match threshold is the instrument stage 3 would need to say how much real traffic
falls outside the capability cells. If S0-C2 FAILS, stage 3 has no instrument and is declined.

### (f) Further high-value readouts

**S0-C3: a label-free predictor of meaningful cells (deciding).**
- For each flat k-means cell at K_f (qwen3 256, seed 0), the separation margin m_c is the mean over its TRAIN members of cos(own centroid) - cos(second-nearest centroid). It is label-free and TRAIN-only.
- Target: the cell's gold purity on EVAL.
- Read: Spearman rho across cells, with a cell-level bootstrap. Cells with fewer than 10 EVAL items are excluded (count printed).
- The structural limit: the number of cells, not items, bounds support:
  - SE_z = 1/sqrt(K-3) is 0.132 / 0.083 / 0.117 for MASSIVE / CLINC / Banking77;
  - the rho-MDE80 is 0.35 / 0.23 / 0.31;
  - the prediction is 0.45-0.50, so SCOREABLE, thin on MASSIVE.

Meaning: label-free cells (UNION-AF-ROUTE, the R256 free cells) would carry a self-diagnostic. If it FAILS, the
framework says label-free cells give no internal sign of their own validity, which strengthens S1 (declared cells).
Stage 1 T-C5 then asks the same of the site-null certificate (size-stratified, one re-draw).

**S0-C4: a cell is a stable address, the Huot robustness half (deciding).**
- For MASSIVE EVAL items with at least one slot, one variant each: slot values swapped for another value of the SAME slot type seen within the SAME intent on TRAIN (registered seed; derived texts are EVAL-side; stem_key collisions with TRAIN are dropped and counted).
- Measure: S = P(cell(variant) = cell(original)) under k-means at K_f.
- Printed beside:
  - supervised-centroid label stability;
  - kNN-1 label stability (Huot's reported collapse is for kNN routers);
  - paraphrase co-filing of random same-intent pairs.
- Support: n about 3,400; SE 0.0053; MDE80 0.015; bar 0.80 against a predicted 0.90, so SCOREABLE.
- Falsifier: an upper CI below 0.80 means filing is surface-sensitive on the easiest known answer. That would bear directly on the 81.6% filing clause's meaning.

**Stage 2: HSE on the union roster (zero calls, key vectors; descriptive).**
- Read the roster's diversity in the paper's own units, and per-cell HSE against the per-cell policy gain over the 52 declared strata.
- DESCRIPTIVE: 52 cells, with BBH carrying 0.728 of G. This is positioning against arXiv 2607.09197, not a claim.

**Stage 3: real-traffic occupancy (WildChat-1M, author decision D4; descriptive only).**
- Read: the share of English first-turn prompts filed into v2 union cells vs no-match at S0-C2's threshold.
- The descriptive reading is itself the deliverable (the author asked for it), so DESCRIPTIVE-ONLY is accepted here.

## 4. Closed lines to avoid (CONTEXT section 5; KNOWLEDGE section 3)

- No rubric, reference, judge, escalation, order or temperature variant: the study has no judge.
- No sub-anchor capability profile. The anchored stage-1 arm discovers intents BELOW declared scenario anchors. That is filing / partition against a known answer, and it must never be written as evidence that sub-anchor PROFILES are meaningful (PROFILE-TREE-ROBUST, KEY-SUBANCHOR-SCALE stay closed).
- The frontier order is not touched.
- No GMM LR / BIC mode test on any intent site (MIX-LRT-SITE, closed negative). The dip half stays open but is not part of this design.
- Not a closed line, but a result not to re-run: MC-LEAF (leaves vs domains as a router). Stage 2 does not re-run it.
- Never `seeds = [...]`; never the frozen 07-27 tree as a comparator (rev2 section B8); P-FAM is not a reason to reopen anything.
- Never write "clean", "disjoint" or "held-out" for these splits before the steward's CK-CLOSE check (S3).

## 5. Hygiene

- **Split.** CK-CLOSE-v1 by construction: side = `split_side.side_of_hash(side_hash(stem_key(text)))` (EVAL 0.30 / GATE 0.10 / TRAIN 0.60).
  - Exact norm-v1 duplicates share a side.
  - A component whose texts carry two gold labels is dropped from every readout (count printed).
  - Near-copies below norm-v1 are COUNTED: cos >= 0.98 at qwen3 512 between EVAL and TRAIN, as FLAT-MIX-MMLU did. They are disclosed, not removed. Templated utterances make them frequent, and every contrast is paired on the same split, so the bias is shared.
  - Per-label side counts are printed. Labels with fewer than 10 EVAL or 20 TRAIN items are listed.
  - The split word is the steward's to grant.
- **What reads what.**
  - Centroids, k-means, TF-IDF and slot values are fitted on TRAIN; vMF concentrations and thresholds on GATE.
  - EVAL is read once, by the readouts.
  - OOS never enters a fit.
  - Stage 1 build DBs contain TRAIN and GATE rows ONLY, so EVAL is physically absent from the JVM's inputs.
- **Own files, never the record's.**
  - One ingest DB `intent_transfer_corpora_v1.db` and one embedding DB per embedder, `intent_emb_<model>.db`, both at the repo root. Root `*.db` is ignored (.gitignore L58). `experiment_results/**/*.db` is RE-INCLUDED (L145), so no DB goes under experiment_results.
  - Raw downloads stay in the Hugging Face cache outside the repo (`data/.../*.jsonl` is NOT ignored). `.gitignore` is author-owned and is not edited.
  - Nothing reads or writes `embeddings_cache.db`, `mmlu_pro_dataset_cache_v2.db`, a ratings DB of record or a pool of record. `queries.ground_truth_category` is never written.
- **Working copies.**
  - Writers close and checkpoint (no -wal). The registrar pins sha256 for each DB. Readers open `mode=ro&immutable=1` and re-check the sha before and after.
  - Stage 1: the JVM never opens a pinned file. A pre-step copies it to a per-run working file after checking its sha (the C-ET2-1 route, which RP09 E1 also needs), `-Dtaxoarena.embeddingCacheFile` names the working copy, and the pinned file is re-checked after the run.
  - `-Dranking.db.path` is an own file (the 20NG precedent).
  - Acceptance: per-table hashes of `embeddings_cache.db` unchanged across every build (the memory note "construction writes cache DBs").
- **Rule 7 and machine.** Stage 0 has no construction and reads no pool of record. Its Ollama embedding runs are still "one heavy process", so they never overlap a construction or site null. CPU readouts run single-threaded (BLAS 1) and are paused during constructions. Stage 1 builds follow rule 7 W1-W5, a backup, the [THREAD-CAP] line and one construction at a time.
- **Ollama transport.**
  - Reuse `tools/analysis/embedder_arms.py`'s writer: its batching survived the 2026-09-29 TIME_WAIT socket incident (incident_w2).
  - A zero-call TRANSPORT PREFLIGHT inside the dry-run embeds 20 texts per embedder and checks route parity.
  - The pilot is a timed 500-text probe per embedder, which also prices the run.
- **Licences.** Attribution strings for CC-BY corpora are printed in every outcome file. No corpus text is committed anywhere, including examples in reviews; ids and hashes only.

## 6. Stages, order and cost

| stage | content | machine | agent-hours (estimate) | depends on |
|---|---|---|---|---|
| 0 | ingest MASSIVE-en, CLINC150-plus, Banking77 (and the HWU64 twin count); embed about 58k short texts (+3.4k slot variants, +1k synthetic pairs) under qwen3 / nomic / gemma; the CPU readouts S0-C1..C4 and S0-D1..D7 | Ollama: nomic and gemma about 15 min each (E0b ran 11.7k MMLU-Pro texts in about 3 min per arm on 2026-09-29; intent texts are shorter); qwen3 UNSOURCED, planning 30-90 min, priced by the pilot's timed probe. CPU about 2-3 h single-threaded. No build, no site null | about 12-18 (steward 2-3, engine-coder 4-6, reviewer 2x2, registrar 1-2, operator 1-2) | the author's D1 (corpora in scope) |
| 1 | builds: MASSIVE AF-256 and anchored-512 (scenario anchors); CLINC AF-256 and anchored-512 (domain anchors); a MASSIVE AF re-draw (split salt 2); two order-shuffle arms on MASSIVE AF (T-C2's spread); site nulls at 300 reps on the AF arms; readouts T-C1..T-C8 | about 6-10 machine-h at 12 threads, an ESTIMATE: builds on 10-14k short texts plus about 1-2 h per 300-rep null, scaled from THREAD-CAP B1's 562 s / 24 reps / 87 sites. The cost-estimator re-prices | about 10-16 (a generic intent DatasetType that fails closed with no HF fallback, unlike fetchTwentyNewsgroups; the working-copy route; the readout) | THREAD-CAP B2/B3 proved; the working-copy route READY; stage 0 VALID (its ceilings set stage 1's predictions) |
| 1b | union of the three intent corpora, federated vs joint (the absorption mechanism) | about 2-3 machine-h | about 4 | stage 1 |
| 2 | soft / selective routing and HSE on the capability side (v2 union tree) | CPU minutes | about 4-6 | RP12 B0 VALID |
| 3 | WildChat-1M occupancy (descriptive) | Ollama for about 50k prompts; CPU | about 6 | D4; S0-C2 HELD; RP12 |

Order in the machine lane (lane order is the author's, rev2 section B7 item 2):
- Amendment 28 already places stage 0 BEFORE RP12. Stage 0 needs no JVM, so THREAD-CAP B2/B3 does not gate it. Its embedding runs only need a window with no construction.
- Recommended order: stage 0 -> RP12 -> stage 1 -> RP09 E1 (which shares the working-copy route) -> RP13.
- Stage 1 goes AFTER RP12 because both need capped constructions and RP12 is the tree the thesis presents. Stage 1 also needs stage 0's ceilings to state its predictions.
- If the author wants stage 1 ahead of RP12, that is decision D5.

Judge calls: 0 in every stage. The 4k-match rule and the day cap are not engaged.

Stage-1 readout index (registered separately after the S0 synthesis):

| id | readout | status |
|---|---|---|
| T-C1 | leaf partition | SCOREABLE |
| T-C2 | hierarchy beyond the leaves, by dendrogram purity | SCOREABLE if the gap is at least 0.02 |
| T-C3 | granularity: own-leaf rate against TRAIN size | slope sign scored; the rest DESCRIPTIVE |
| T-C4 | overlap tracking (Mantel) | SCOREABLE against the null; the tree vs agglomerative contrast DESCRIPTIVE |
| T-C5 | certified sites against gold boundaries | size-stratified, one re-draw; DESCRIPTIVE unless at least about 40 sites per arm |
| T-C6 | leaf-centroid no-match AUROC against k-means at k = L | DESCRIPTIVE, predicted tie |
| T-C7 | S0-C3's margin and S0-C4's slot-swap stability on tree leaves | SCOREABLE as in S0 |
| T-C8 | flatLeaf vs descent against gold | SCOREABLE |

## 7. Registration draft: INTENT-TRANSFER-S0 (for the registrar; not committed as a registration until D1)

**Heading.** `## Registered <date> (before any code or call) — INTENT-TRANSFER-S0: on three intent corpora with a known answer (MASSIVE en-US 18/60, CLINC150 10/150 + OOS, Banking77 77), split content-closed by CK-CLOSE-v1 hash sides, does the embedder dependence seen on MMLU-Pro (coarse holds, fine depends) reappear against GOLD labels, does label-free no-match detect out-of-scope, does a label-free cell margin predict gold cell purity, and is a flat cell a stable address under slot swaps? (zero calls; no build; plan Amendment 28 stage 0)`

**Question and kind.** Kind: readout (0 LLM calls, no construction). A known-answer foundation for SQ3 (filing, label-free
cells) and SQ5 (embedder and corpus). It supplies stage 1's ceilings. It scores no tree.

**Prior results touched (none revised).**
- EMBEDDER-CROSS-FLAT E0b: S0-C1's prior (k 14 not shown worse; k 82 nomic WORSE).
- TOPIC-PARTITION-20NG: the NMI spread prior 0.0074.
- FLAT-MIX-MMLU: the near-copy count method.
- ROUTER-CLEAN-POLICY / MC-ROOT: filing, context only.
- arXiv 2607.09197: S0-C4's contrast.
- Closed lines: none touched (section 4).

**Hygiene.** As in section 5, verbatim. The preconditions (each a failed precondition, never an outcome):
- the steward's census within 5% of the planning counts, or re-stated by bracket before any read;
- 0 EVAL rows in any fit (a TRAIN-ONLY assertion per fit);
- 0 OOS rows in any fit;
- DB sha pins re-checked before and after;
- no -wal on any read;
- `embeddings_cache.db` per-table hashes unchanged;
- the transport preflight passes;
- no other heavy process during embedding.

**Instrument.**
- Embedders: `qwen3-embedding:latest`, `nomic-embed-text:latest` and `embeddinggemma:latest`, RAW (PRIMARY protocol of record). Slice 256 then renormalise (E0b-conformant); slice 512 printed. mxbai is excluded (not decided).
- TF-IDF -> SVD-256 floor: printed.
- Spherical k-means: k-means++, n_init 1, max_iter 300, seeds 0-4, fit on TRAIN, EVAL filed to the nearest centroid.
- NMI: arithmetic normalisation; ARI printed.
- Intervals: 95% percentile, CK-CLOSE-component bootstrap, B 2,000, partitions fixed, unless named.
- Scripts TO BE BUILT: `tools/ingest/intent_ingest.py` (`--dry-run / --selftest / --fetch / --manifest`) and `tools/analysis/intent_transfer_s0.py` (`--selftest / --dry-run / --run`; write-once outcome `experiment_results/intent_transfer/s0_outcome.txt`; CSVs beside).

**Criteria (each states whether the point or the interval decides).**

S0-C1, embedder against gold. D(e, g) = mean over seeds of NMI_e,g - NMI_qwen3,g, for e in {nomic, gemma}, g in {coarse, fine}.
- WORSE(e, g) iff D < -max(MDE80, spread) (point) AND the paired CI lies below 0 (interval).
- BETTER(e, g) symmetrically. Allowed here because the answer is known.
- C1a (fine dependence) HELD iff at least 1 of the 2 families is WORSE at the fine level on at least 2 of 3 corpora; FAILED otherwise.
- C1b (coarse) NOT FIRED iff 0 of 2 are WORSE at the coarse level on both MASSIVE and CLINC; FIRES otherwise.
- A non-fire is never parity.

S0-C2, OOS (CLINC150):
- A = AUROC of max-cos to label-free k-means (K 150) centroids, in-scope EVAL vs OOS.
- HELD iff lower(A) >= 0.85; FAILED iff upper(A) < 0.85; UNDETERMINED otherwise.
- FPR95 printed.

S0-C3, label-free cell quality:
- rho = Spearman(m_c, EVAL gold purity_c) over cells at K_f (qwen3 256, seed 0; seeds 1-4 printed), with a cell-level bootstrap.
- HELD iff lower(rho) > 0 on at least 2 of 3 corpora; FAILED iff upper(rho) <= 0 on at least 2 of 3; UNDETERMINED otherwise.

S0-C4, slot-swap stability (MASSIVE):
- S = P(same k-means cell at K_f 60 | original, variant).
- HELD iff lower(S) >= 0.80; FAILED iff upper(S) < 0.80; UNDETERMINED otherwise.
- Printed beside: supervised-centroid label stability, kNN-1 label stability and random same-intent co-filing.

Descriptive (never scored, each printed with n):
- D1: ceilings. Supervised TRAIN-centroid and kNN-15 accuracy per level and embedder; k-means NMI / ARI at 0.5x, 1x and 2x the gold K.
- D2: gold geometricity H. ARI of average-link clustering on the gold fine TRAIN centroids, cut at K_c, against the gold map, with a size-matched random-partition p95.
- D3: the overlap map and within-coarse confusion share.
- D4: soft / hard / selective filing (the vMF concentration on GATE).
- D5: synthetic two-intent pairs (1,000, registered seed).
- D6: length quintiles.
- D7: the HWU64 <-> MASSIVE-en twin count (steward).

**Support.**

(a) Deciding denominators (planning, reconciled at the census):

| readout | denominator |
|---|---|
| C1 | EVAL: MASSIVE about 4,890, CLINC in-scope about 6,750, Banking77 about 3,925 |
| C2 | 6,750 in-scope + about 1,350 OOS |
| C3 | cells K_f = 60 / 150 / 77 |
| C4 | about 3,400 MASSIVE EVAL items with a slot |

Clusters: exact-duplicate CK-CLOSE components.

(b) DEFF and its source: 1.05, DECLARED (a Kish bound from exact-duplicate components). Measured and printed at the run. C3's unit is the cell (DEFF not applicable).

(c) n_eff: about 4,657 / 6,429 / 3,738 (C1); C2 n_OOS,eff about 1,286; C4 about 3,238.

(d) SE:

| readout | SE | source |
|---|---|---|
| C1 paired NMI difference | 0.004 | declared pilot; bootstrap measured at the run |
| C2 | 0.006 | Hanley-McNeil at A 0.90, n1 1,350, n2 6,750, times sqrt(1.05) |
| C3 | SE_z 0.132 / 0.083 / 0.117 | 1/sqrt(K-3) |
| C4 | 0.0053 | sqrt(0.09/3,238) |

(e) MDE80 = 2.8 x SE:

| readout | MDE80 | bar |
|---|---|---|
| C1 | 0.0112 | max(0.0112, spread); planning spread 0.010, transported from 20NG, measured at the run |
| C2 | 0.017 | — |
| C3 | rho 0.35 / 0.23 / 0.31 | — |
| C4 | 0.015 | — |

(f) Verdict lines:
- C1a SCOREABLE: the predicted fine D of -0.02 to -0.03 exceeds the 0.0112 bar.
- C1b is a non-fire readout: it can only be "not fired", never parity.
- C2 SCOREABLE: 0.88 vs 0.85 is 0.03 > 0.017.
- C3 SCOREABLE on CLINC and Banking77, and thin on MASSIVE (0.45 vs 0.35).
- C4 SCOREABLE: 0.10 > 0.015.

(g) Structural leg (can the criterion be reached at infinite budget?):
- C1: only where the true |D| exceeds the k-means seed spread, which does not shrink with n. Inside it, C1a reads FAILED at any budget. Stated now.
- C2 and C4: yes.
- C3: bounded by the number of cells, not items. At K = 60, a true rho below about 0.35 is unreachable at any item count.

**Predictions** (80% intervals; each scored).

P1, levels (qwen3 256, seed mean):

| corpus | coarse | fine |
|---|---|---|
| MASSIVE | NMI 0.68 [0.58, 0.78] at K 18 | 0.78 [0.72, 0.84] at K 60 |
| CLINC | 0.50 [0.38, 0.62] at K 10 | 0.90 [0.86, 0.93] at K 150 (Instructor 0.915) |
| Banking77 | — | 0.80 [0.74, 0.85] at K 77 (Instructor 0.817) |

P2, C1:
- fine nomic D: MASSIVE -0.025 [-0.05, 0.00]; CLINC -0.020 [-0.04, 0.00]; Banking77 -0.030 [-0.06, -0.005].
- fine gemma D: -0.010 [-0.035, +0.015] on each corpus.
- C1a HELD 0.55; C1b NOT FIRED 0.65; qwen3 BETTER than both at the fine level on at least 2 of 3 corpora: 0.40.

P3, C2: A = 0.88 [0.80, 0.94]; FPR95 0.45 [0.30, 0.65]; HELD 0.65. The supervised-centroid A is printed, predicted 0.91.

P4, C3: rho = 0.45 [0.20, 0.65] (MASSIVE), 0.50 [0.35, 0.62] (CLINC), 0.45 [0.25, 0.62] (Banking77); HELD 0.75.

P5, C4: S = 0.90 [0.85, 0.95]; HELD 0.85. kNN-1 label stability is below the supervised-centroid stability: 0.60.

P6, descriptive, scored as HELD / FAILED at the point:
- D2 H(MASSIVE) = 0.45 [0.25, 0.65] and H(CLINC) = 0.55 [0.30, 0.75], both above their random p95.
- D3: the within-scenario share of MASSIVE confusion mass is at least 0.55.
- D4: selective filing at 80% coverage raises fine precision by at least 5pp on MASSIVE.

**Falsifiers.**
- F1: C1a FAILED. E0b's "the fine structure is embedder-dependent" (k 82, nomic WORSE) is not reproduced against a known answer on 2 of 3 corpora. That clause narrows to MMLU-Pro and one draw.
- F1': C1b FIRES. The coarse "not shown worse" of E0b does not generalise.
- F2: C2 FAILED. Label-free no-match is not an out-of-scope detector on the canonical known-answer corpus. Stage 3 is declined, and the framework may not describe no-match as scope detection.
- F3: C3 FAILED. A label-free margin carries no sign of a flat cell's meaning. Label-free cells get no self-diagnostic, and S1 (declared cells) is strengthened.
- F4: C4 FAILED. Flat cells are not stable addresses under slot swaps on the easiest known answer. Every filing rate of record (81.6%) must carry "surface-sensitive, untested on capability text".

**Cost and consequence.**
- Calls: 0; cce: 0.
- Machine: Ollama embedding of about 62k texts x 3 embedders, serial, one heavy process. nomic and gemma about 15 min each (sourced by analogy to E0b's 2026-09-29 runs); qwen3 UNSOURCED, priced by the pilot's timed 500-text probe. CPU about 2-3 h single-threaded.
- Agents: about 12-18 h.
- Order: census -> scripts -> READY -> transport preflight -> pilot (500 texts per embedder, timed; CPU readouts on the pilot's rows as a smoke run, discarded) -> full embedding -> --run -> post-run review -> outcome.
- Consequence: stage 1's predictions and criteria take their ceilings (D1, D2) and bars from this outcome. F2 and F4 have framework consequences stated above.

**Does NOT show (written before the run).**
- Anything about the tree or the construction: no build. Stage 1 is where the construction is scored.
- Capability, judges, boards, routing GAIN or any policy: no models on these corpora.
- That a gold coarse level is the right taxonomy: a low H is a property of the designer's hierarchy as much as of the geometry.
- Transfer from short, templated, English utterances to benchmark questions (long, varied). No sentence about MMLU-Pro cells follows from these numbers.
- Parity of embedders anywhere (no TOST).
- Anything from a second split draw: the hash split is one draw.
- Natural multi-intent behaviour: D5 is synthetic concatenation.
- The OOS number on "real" out-of-scope traffic: CLINC OOS is one curated, hard-OOS set with documented mislabels.
- The card-conformant (prefixed) protocol of any embedder: RAW only; qwen3 without an instruction.

## 8. Plan of delegation (briefs; each report in the KNOWLEDGE section 0 format)

1. **cost-estimator** (before registration). "INTENT-TRANSFER-S0, design section 7 of docs/agents/plans/2026-09-29_intent_transfer_design.md. Price stage 0 and stage 1: Ollama time per embedder for about 62k short texts (use E0b's 2026-09-29 run logs in experiment_results/embedder_cross_runlog), CPU h, agent h, and rule-7 windows. Verified already: 0 calls; no pool of record read; embedder DBs of record untouched. Output: your price block in the hand-back only."
2. **registrar.** "Register INTENT-TRANSFER-S0 from section 7 of the design file, after the author's D1 is quoted. Heading as drafted. Closed-lines check (section 4). Create docs/agents/results/INTENT-TRANSFER-S0.json and the queue item; state registered. Nothing else changes. Ledger: add a plan chip only."
3. **data-steward** (census, before code). "INTENT-TRANSFER-S0 census. Fetch to the HF cache (outside the repo) MASSIVE en-US, clinc_oos plus and banking77; HWU64 for the twin count only. Report: raw rows, norm-v1 components, cross-label components, side counts (split_side hash), per-label minima, EVAL<->TRAIN near-copies at cos >= 0.98 (after the embedding; owed later), the HWU64 <-> MASSIVE-en exact and norm-v1 twin counts, and OOS <-> in-scope collisions. Acceptance: counts within 5% of the design's planning values, or a bracket. Output: docs/reviews/STEWARD_intent_transfer_census.md."
4. **engine-coder** (worktree `.claude/worktrees/intent-s0`, branch intent-s0; Python only). "Build tools/ingest/intent_ingest.py and tools/analysis/intent_transfer_s0.py per the registration. Reuse split_side (stem_key, side_hash, side_of_hash) and embedder_arms.write_vectors (the TIME_WAIT-safe batching). Own DBs at the repo root, never embeddings_cache.db. The --dry-run includes the transport preflight (20 texts per embedder, route parity) and prints every denominator. --selftest covers: TRAIN-only fits (a planted EVAL row refuses), OOS never fitted, slot swap within the same slot type and intent, write-once outcome. Hand to the adversarial-reviewer."
5. **adversarial-reviewer** (zero calls). "READY review of intent-s0 at <sha>: recompute the side counts, the Hanley-McNeil SE and one NMI bootstrap on the selftest fixture; mutants for EVAL-in-fit, OOS-in-fit, cross-label components kept, a slot swap crossing intents, and a WAL read. Output docs/reviews/READY_intent_s0.md, MERGEABLE / READY verdicts."
6. **research lead**: merge by path after MERGEABLE, full suite, then the Block 2 dry-runs as the regression check.
7. **run-operator.** "INTENT-TRANSFER-S0 run from main at <merge sha>: ingest --fetch -> registrar pins -> transport preflight -> pilot (500 texts per embedder, timed; smoke readout discarded) -> full embedding (one heavy process; no construction running) -> --run. Refuse on any precondition in section 5. Output: experiment_results/intent_transfer/s0_outcome.txt (write-once) and CSVs."
8. **adversarial-reviewer** (post-run). "Recompute every deciding number (C1-C4) and the census reconciliation; check the does-NOT-show list; output docs/reviews/POSTRUN_intent_s0.md."
9. **registrar**: the outcome section, ledger row, results JSON, INDEX and queue; the stage-1 registration only after the synthesis.
10. **tree-construction-specialist** (stage 1 design, after the S0 outcome): the arm recipes, the mcs-floor prediction for CLINC, the split-salt re-draw and the order-shuffle arms; the generic intent DatasetType spec (fail closed, no HF fallback).
11. **Not called:** judge-design-specialist (no judge) and arena-specialist (until stage 2).

## 9. Synthesis (to be written after the outcome; the frame is fixed now)

| outcome | what the framework may say | what it refuses | what it opens |
|---|---|---|---|
| C1a HELD, C1b not fired | "coarse flat structure holds and fine structure depends on the embedder, against gold labels on intent corpora and against categories on MMLU-Pro" (two kinds of corpus, one draw each) | "invariant"; any tree-level embedder claim | stage 1 under a second embedder (the E1 route) |
| C1a FAILED | E0b's k 82 clause stays MMLU-Pro-bound | a general fine-scale embedder dependence | which property of MMLU-Pro (long, varied, multi-topic items) drives it |
| C2 HELD | "a label-free no-match threshold detects curated out-of-scope queries at AUROC X" | anything about real traffic before stage 3 | stage 3 |
| C3 HELD | "a label-free margin ranks flat cells by gold purity (rho X, cells n)" | the same for tree cells or certificates (stage 1 T-C5) | a self-diagnostic column for label-free cells in RP13 |
| C4 HELD | "a flat cell is a stable address under slot swaps (S X)" | robustness on capability text; any kNN-router claim | the same readout on tree leaves (stage 1) |

**What this result does NOT show** (to be completed at the synthesis; the section 7 list plus whatever the post-run
review adds): the construction; capability; routing gain; transfer to benchmark questions; embedder parity; a second
draw; natural multi-intent text.

## 10. Decisions that are the author's

- **D1 (needed before registration): external corpora in scope** (rev2 section B7). MASSIVE en-US (CC-BY-4.0), CLINC150 (CC-BY-3.0), Banking77 (CC-BY-4.0) as known-answer, non-capability corpora, with attribution; HWU64 (CC BY 4.0) for the twin count only.
- **D2:** the thesis wording for a known-answer construction study (framing S-rules; `report/` is the author's).
- **D3:** BlendX (GPL-2.0, ChatGPT-built) for natural multi-intent text in stage 1+, or synthetic concatenation only.
- **D4:** stage 3 real traffic. WildChat-1M (ODC-BY; personal-data handling: local only, no text committed, no per-conversation output) is recommended. LMSYS-Chat-1M (gated agreement, no redistribution) is NOT recommended.
- **D5:** machine-lane position of stage 1 relative to RP12 (recommended: after RP12).
- mxbai stays excluded (undecided). Gemma is used as in E0b under Amendment 26 (b).
