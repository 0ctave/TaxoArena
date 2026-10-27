# Framing of record for the TaxoArena thesis (research lead, 2026-09-26)

**Name:** Cell-conditional evaluation. When does filing questions into cells change the model an evaluator should use, or the comparison it may trust? And what does a taxonomy add to that?

This framing is led by framing B. It keeps A's licence-table discipline and title bridge, and it adopts C's ARCH-V2 constraint. The skeptic's ranking (B ≳ A > C) stands, and all of the skeptic's HIGH defects are fixed below.

I checked these pointers myself in this pass:
- CTX §1–§5, FW L251–L271 and L352–L384.
- `clean_subset_reanalysis.txt` L33–L35.
- prog L15080–L15084, L17015–L17022, L21205–L21230.
- Synthesis L94–L105 and L310–L320.
- Ledger L73, L79, L84–L86, L94, L149, L177, L182, L200, L217, L231, L235, L244, L283.
- The queue states.
- `h9_embed_nomic.toml`.
- The title at `b_Meta.tex` L32.

I made zero calls and wrote nothing to the repo.

## Central question
For a fixed roster, a corpus split content-closed under CK-CLOSE, and a fixed verification instrument (an answer key, an executed checker, or the frozen STACK-v2 judge with its cached reference): when does evaluating per cell change which model an evaluator should use, or which pairwise comparison it may trust, compared with one pooled leaderboard? What does that cost, and which answers survive a second embedder, a second tree draw and a second corpus? Cells are declared labels for the arena, and are read by a TRAIN-only embedding taxonomy where labels are missing.

## Scope rules that bind every sub-question
- **S1. Arena cells are declared.** This is ARCH-V2 decision 5, which is a default (prog L15082 (4)). The tree is off the arena path (synthesis L100, R5). The tree is audited in four ways: filing (G11/G13), M (G14), partition (FLAT) and certificate (G12). Changing this is the author's call. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B1): the pointer is synthesis decision 5, recorded in item (4) at prog L15080 ("cells DECLARED (decision 5)"); L15082 is item (5), the ARCH-V2 queue entry]
- **S2. Verification fidelity only** (CTX §1; FW L253). The record holds no unkeyed corpus (ARCH-V2_SYNTHESIS L31). A judged cell therefore means keyed fidelity plus a transport assumption, and transport is UNDETERMINED (JUDGE-TRANSFER, ledger L289). This fixes C's SQ4, which had no data object. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B2): "ARCH-V2_SYNTHESIS L31" is L32 (L31 is blank). "transport is UNDETERMINED (JUDGE-TRANSFER, ledger L289)" is replaced by: transport to an unkeyed corpus is UNTESTED, "the widener's parameters do not transfer across corpora (untested)" (FW L191 step (5)); ledger L289 (JUDGE-TRANSFER) is the widener across judge FAMILIES, a different question (plan A3 item 11)]
- **S3. Every object carries its split word** (CTX §4 rule 12):
  - Content-closed: af_clean_s42 (R256), and the v2 split 5a3e756 (pv2_41dbd3dbcd399df0, pv2_1575de61bb20e977; prog L16193–L16198).
  - Id-disjoint only: p2dca / bareq512_s42 (bound 2.03pp) and paeec (the union tree holds 432 of 6,482 EVAL texts; bound 1.32pp). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B3): add to the id-disjoint-only list: the anchor-free re-draws af_s137 (pd610c9a), af_s2048 (p19d9f47) and af_s42_o1 (p8a29), until the data-steward's closure check (ledger row ANCHOR-FREE-REDRAW; plan S3)]
- **S4. Recipes are never joined.**
  - R256 and R512 counts are never set against each other (prog L21006). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B4): scope: L21006 bans setting CERT-RESOLUTION's certified-site counts across R256 and R512; the registered within-embedder dimension ladder D1-D3 (ledger rows D1-D3) keeps its own words; S4 is not read wider (plan S4)]
  - T1 and T1b are stated separately, each against its own null. "1 of 97 vs 16 of 101" is never written (ledger L177).
- **S5. Closed lines stay closed** (CTX §5). The LCB STOP is quoted only with its synthetic-power qualifier until LCB-STAGE0-POWER-RESIM lands.

## The sub-questions

### SQ1 (USE): does a per-cell policy fitted on TRAIN beat the best single model on content-closed EVAL, and on which (roster, corpus) pairs?

**Already answered, id-disjoint only:**
- **Six-corpus union (paeec):** G = +2.92pp [+1.81, +4.02] on 6,482 EVAL questions, with 18 models and 52 declared strata. True labels give +3.09pp.
  - BBH carries +1.96pp of the +2.92pp.
  - The MMLU-Pro source alone gives +0.86 [−0.54, +2.26].
  - The placebo is centred at −0.52. It certifies the fit-and-score code, not routing.
  - Pointers: ledger L182; prog L14145–L14184.
- **MMLU-Pro with a frontier roster:** +0.000 ± 0.007 by anchor and −0.002 by leaf. gemini is TRAIN-best in 14 of 14 anchors (ledger L303).
- **Judged verdicts cannot pick the argmax:** routing on them costs −4.7pp pooled. This is EXPLORATORY and on a re-derived side (GEN-ARENA, ledger L318).
- **Licensed words:** "on the two rosters measured". The word "only" is not licensed.

**Still open:**
- A content-closed replication. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B5): not a "replication": a content-closed SENSITIVITY and wording conversion (same item family, same 18 models; twin removal already reads +3.28 [+2.12, +4.44], ledger row ROUTER-CLEAN-POLICY; plan A3 item 14)]
- The BBH share. 1,096 of the 1,142 residual near-duplicate pairs on v2 are BBH (prog L16193–L16198).
- How the gain depends on the roster beyond these two points.

**What closes it:** V2-DECLARED-CELLS, which is G14's declared-label half (REG-1 below; zero calls). A roster dose-response comes later and is DESCRIPTIVE; there the curve itself is the deliverable. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B5): REG-1 is a content-closed sensitivity and wording conversion, not a replication (plan A3 item 14)]

### SQ2 (TRUST): at which grain are per-cell comparisons reliable on the key and on the judge, and what sets the judge's fidelity in a cell?

**Already answered:**
- **Key, interaction-only split-half R.** Each is paired with its own null:
  - K12: 0.8665 [0.8000, 0.9330] against a null of 0.3142.
  - K46: 0.8118 [0.7254, 0.8983] against a null of 0.2343.
  - Both are on 14 anchors routed by bareq512_s42, on p2dca (id-disjoint only; bound 2.03pp; ledger L239).
  - The 52 declared union strata read 0.8537 (paeec; FW L260 bracket). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B18): add "id-disjoint only; declared strata, no embedder" to 0.8537]
- **Judge.** The anchor-profile R is 0.7183 [0.6076, 0.8291], published as PASS-WITH-INTERVAL forever. Under the filter it reads 0.5613 [0.3385, 0.7842] (FW L260). The key beats the judge by +0.194 [0.037, 0.351] on x12 and +0.121 [0.030, 0.211] merged (ledger L239).
- **Grain.** Reporting is terminal at the anchor (FW L259; CTX §5).
- **Fidelity depends on the reference:**
  - A paired +12.6pp from the reference: 0.864 vs 0.738 on the same 944 matches, 144:25 (PAIR-NOREF, ledger L217).
  - The defensible board-scale figure is 0.852 (convention A, 4,507 matches). 0.865 is a selection maximum (FW L263).
  - The checker's 0.958 is on MATH, a different corpus.
  - CONSENSUS-FIT: accuracy is 0.922 when the reference backs the key-correct answer, 0.657 when it backs neither, and 0.226 when it backs the wrong one (ledger L208).
  - The judge model was compared for one cross-family pair only, on 7 scored anchors, under this recipe (prog L7508).
- **Misfiling.** MMLU-Pro's realised misfiling rate is 24.7%. The attenuation slope lies between 0.80 and 0.68, and 0 established edges reversed (ledger L280).

**Not SQ2 evidence:** the OPTION-A LRT (38.8 against a null p95 of 21.0). It is computed on the R2 atlas over 3 groups (math / law+psych / other) with the old judge (`clean_subset_reanalysis.txt` L33–L35). It belongs to the r8 family.

**Still open:**
- Any judged profile under the v2 recipe. 69.3% of K46's matches carried no reference, a branch never measured (prog L19524–L19532).
- The declared-cell key interaction on the v2 roster.
- A third judge family.

**What closes it:**
- REG-1's secondary readout (zero calls).
- G21 (~2,000 calls) and G24 (~1,224 calls). Each is under 4,000 matches and needs its own registration.

### SQ3 (TAXONOMY): what does a TRAIN-only tree add beyond declared labels (filing, M, partition, certificate, label-free cells)?

**Already answered:**
- **Filing:** flatLeaf 81.58% [80.62, 82.50] against 72.08% by descent. This is a filing rate, not discovery (ledger L201). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B18): add "id-disjoint only; descent compares the tree with itself"]
- **M:** +0.17 [−0.61, +0.95] at an MDE of ~1.1pp. The licensed words are "neither a cost nor parity is shown" (ledger L182).
- **Leaves:** MC-LEAF reads −0.9 ± 0.3pp; it is i.i.d. and its flag is still open (ledger L321). C3 (leaf vs domain) reads −0.09, descriptive only.
- **Partition:** FLAT-MIX-MMLU gives a purity difference of −4.3pp [−5.6, −2.9] and F6 −1.5e−3. That is one tree, one comparator and one corpus, and the mechanism is not identified (prog L21205–L21230).
- **20NG:** the tree ties k-means (NMI −0.0020 against a seed spread of 0.0074; ledger L226).
- **Certificate:**
  - 2 of 70 sites on bareq512_s42 at per-family FDR 0.05; BY rejects nothing; 53 sites are untested (prog L20957–L21027).
  - The J site null discriminates, whereas the Gaussian-mixture LR certifies 282 of 282 sites (ledger L159, carrying the W1 qualifier).
  - The tree of record is not a fixed point (prog L21029–L21058).
- **R256 results, stated separately:** 5 re-draw-stable sites, per-site (ledger L244). 5 label-free cells carry 54% of the names' key information (ledger L235).

**Still open:**
- G11–G14 on a content-closed tree. ARCH-V2-E-T is drafted; its lane is ~10–14 machine-hours, serial.
- FLAT-MIX-ANCHORED (drafted).
- UNION-AF-ROUTE (drafted). It is the only test of the label-free case, the one case where the tree is needed to choose a model.
- The dip half of L6, with a texture-preserving null (unregistered).
- CERT-FAMILYWISE-REPS (needs the author's window).

**Falsifier F-TAX, to be committed now.** The expected sentence is: "the taxonomy buys filing, a certificate, support and names, not partition quality or a routing gain". [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B6): the expected sentence is replaced by: "the taxonomy buys filing, a certificate, support and names; on MMLU-Pro its cells are a worse partition than a flat mixture at the same granularity (af_clean_s42, one draw; the anchored control ties, reported only; mechanism not identified); no routing gain is shown" (prog L21218, L21220-L21227: the generalisation is not licensed; L21142-L21143; ledger row ROUTER-CLEAN-POLICY)]
- It moves toward "an evaluation lever" if either:
  - UNION-AF-ROUTE's label-free policy beats the declared-label policy by more than its MDE, or
  - G13 puts flatLeaf above nearest-centroid and k-means filing beyond its interval.
- It narrows to "a filing device only" if G12 fails on the content-closed tree: MMLU-Pro certifies fewer than 5 sites, or the root is uncertified (synthesis G12 row). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B7): G12's leg is ill-defined as written ("root uncertified" can never fire on an anchored tree; "< 5 sites" names no counting rule); use the re-statement of the ARCH-V2_SYNTHESIS G12-row bracket (A5): G12 fails iff the hierarchical-BH set at per-family q = 0.05 (300 reps) contains no depth-1 anchor split; per-site p95 counts printed beside against Binomial(m, 0.05); below the site-null floor UNDETERMINED-by-support; a top family that cannot reach p <= 0.05/m at the rep count reads UNDETERMINED]

### SQ4 (PRICE AND ERROR RATE, the "dynamic" axis): what does judged trust cost as rosters grow, newcomers arrive and corpora are added, and at what realised error rate?

**Already answered:**
- **Roster growth:** K46 gives β̂ 1.8014, widened [1.2821, 2.3207]: "P EXCLUDED", not "M EXCLUDED". This is planning scale on 2 anchors, and the 14-anchor nominal is not reachable by that design (prog L19459–L19538).
- **Calibration:** UNDETERMINED, and permanent on current data (FW L255). GROK-CALIB's b1 is not identified at a correlation-honest 0.05 (ledger L264). Transfer is UNDETERMINED (ledger L289).
- **Newcomers:** "400 + 100 per separable tier" HELD for two newcomers, mid-board only (ledger L231). 400 matches alone is not a placement budget (FW L380). [P-FAM (c) 2026-09-27, applied by the registrar (RP01 B18) (docs/reviews/RULING_w0_p2dca_family.md, 5effe96): "400 + 100 per separable tier" is a p2dca-family quantity — planning only]
- **Corpora:** federated construction certifies 13 sites against 5 (ledger L200).
- **Domain arrival:** an arriving domain is absorbed, not born (ledger L94).
- **Drift:** under the v1 recipe, epoch 2 reads NO ALARM (0.070 against 0.138; prog L15882). EPOCH-NULL has no criterion (ledger L283).

**Still open:**
- The board size. It is the author's decision, and G22 is blocked; its simulator is not centred on the record (prog L15636). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B8): ARCH-V2-G22 stays RUNNING (prog L16041). Validity v2 passed at the boundary with the simulator not centred on the record (D2 HIGH, L15636); the designs and stop are recorded with conditions (L16009-L16041, record runs a5b68e6); the real-supply re-run is owed (queue item G22-REAL-SUPPLY-RERUN) and no stage-1 reading may be cited until it runs; the board size is the author's (ruling 3)]
- A calibration board above 4,000 matches, which needs the author's go.
- G17 (1,224 calls).
- Drift under the v2 prompt.

**What closes it:** without the go, the answer is "priced, and UNDETERMINED". This is not "a computable budget question".

### SQ5 (INVARIANCE, the author's embedder and dataset question): which answers to SQ1–SQ3 belong to the method rather than to qwen3, seed 42 and MMLU-Pro?

**Already answered:**
- **Seed floor:** Top-1 spans 0.750–0.776 and leaf counts 72–92 over 20 seeds (ledger L73). Leaf identity ARI is 0.585–0.704 (FW L57).
- **Dimension:** D1–D3 (ledger L84–L86). The bar is set by iso-equalization: 0.0145 = 0.025 × 0.0040/0.0069.
- **Embedder:** EMBED is EXPLORATORY and DESCRIPTIVE (ledger L79), and it is confounded. nomic reused qwen3's 256-d bar of 0.025 on raw text with no prefix (`h9_embed_nomic.toml` L1–L10, L54–L57). gemma was parked after a runner fault.
- **Corpus:** 20NG (partition only); LCB STOP at synthetic power (prog L19732–L19800); the union (SQ1).

**Still open:**
- Every licence under a second embedder.
- FLAT under a second tree draw.
- A non-dominated keyed corpus outside the six Open LLM Leaderboard v2 tasks.

**What closes it:** REG-2 (EMBEDDER-CROSS-FLAT), LCB-STAGE0-POWER-RESIM, and DATASET-SURVEY.

## How the framing honours the title
The registered title is "Query-Adaptive Multidimensional Ranking for Agents in Dynamic Domains" (`b_Meta.tex` L32; immutable).
- **Query-Adaptive = SQ1 plus the filing half of SQ3.** Each query is ranked in the cell it is filed into, and SQ1 says when that changes the decision.
- **Multidimensional Ranking = SQ2.** Per-cell key profiles with intervals, and judged undominated sets (U_c) rather than an argmax.
- **Dynamic Domains = SQ4, carried as scope.** It covers roster growth priced by K46, newcomer placement, federated corpus arrival, absorption (D4) and drift at the canary. It is not a drift result.
- **for Agents = motivation only.** No agent corpus reaches the 120-task floor (FW L271), and nothing judged an agent trace. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B9): no REGISTERED agent stratum reaches 120 (the unregistered Multi-SWE python language cell has 234 EVAL instances, n_eff ~85; FW L271). BFCL traces WERE judged once (BFCL-JUDGED-PILOT, ledger row of that id; 1,316 calls) and the falsifier fired at the point, so "for Agents" is motivation for a measured reason]

The thesis builds and audits the measurement that query-adaptive ranking for agents would depend on. It claims no router or agent deliverable.

## How r8 is disclosed (one paragraph, no number carried forward)
Proposed text:

> "A first iteration (the r8 batch and the judged runs of its era: x8, x12 v1, the R2 atlas) was judged on pool p2dca21ab5f4ef3ae while the frozen tree withheld p8a29d8f3ff75aa55. 2,425 of 3,445 judged questions (71%) lay on the tree's train side and inside rubric induction (INCIDENT, ledger L148). Its split was id-only, and its judge and rubric recipe has since been replaced. On re-score its rubric-value claims were withdrawn (AUDIT/OPTION-A, ledger L149). No result of that iteration is used in this thesis." [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B10): "2,425 of 3,445 judged questions (71%) lay on the tree's train side and inside rubric induction" is: of the pool's 3,445 JUDGEABLE questions, 2,437 (70.7% by content; 2,425 = 70.4% by id) lay on the frozen tree's train side and inside its CELL-rubric induction (incident doc L10-L13)]

**The boundary of the r8 family:** it includes the R2-based interaction LRT. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B11): the r8 boundary covers the R2 LRT; H3 +0.39/1k (bias_audit.py reads ratings_x12.db and the R2 ratings_x12p.db); L1 0.766->0.259; the J-floor table; the frozen tree as evidence. H9-EXT and D1-D3 are carved out as geometry only (plan A4)]

**Not r8:** the post-incident STACK-v2 boards on p2dca routed by bareq512_s42 (bound 2.03pp) and the paeec union. They are quoted at board scale with their id-disjoint-only brackets. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B11): SUPERSEDED by the [P-FAM] ruling (docs/reviews/RULING_w0_p2dca_family.md, 5effe96), adopted boundary plan A4: every judged number on the p2dca / x12-schedule judged sample, post-incident STACK-v2 boards included, is p2dca judged family — HISTORY, NOT EVIDENCE; the paeec union key readouts are not in the family and keep "id-disjoint only"]

The "contaminated position fits" in the author's premise needs a record pointer from the science-writer before it enters the paragraph. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B10): "contaminated position fits" means: 22 per-leaf fits, and the stopping decisions that consumed them, were contaminated by the since-removed correction; all 8 pooled per-domain leaderboards reproduce (experiment_results/r8/refit_delta_report.md L7-L14, L22-L43, L47)]

## Thesis claim, if the sub-questions land as the record points
Clauses marked † depend on an open test; the falsifier is named inside the clause.

On the rosters and corpora measured, conditioning evaluation on cells of the question space changes which comparison an evaluator may trust far more often than which model it should use. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B12): delete "far more often": a comparison nobody registered (plan B8 words)]
- Model × cell interaction is real and reliable on the key at anchor and declared-stratum granularity: R 0.81–0.87 against logit-additive nulls of 0.23–0.31, and 0.85 on the union strata. The anchor is the terminal reporting grain.
- Conditioning changes the model to use only on a roster without a dominant model: +2.92pp [+1.81, +4.02] on an 18-model union, two thirds of it BBH, against 0.000 on MMLU-Pro with a frontier roster. † A content-closed replication is pending, and the clause is withdrawn if REG-1's interval covers 0. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B12/B5): "only on a roster without a dominant model" is: on one of the two rosters measured, and not on MMLU-Pro, where one model is best in 14 of 14 anchors; the two points also differ in scoring protocol (multi_corpus_design.md L236-L243); this framing's own L45 and L188 say "only" is not licensed. "A content-closed replication" is a content-closed sensitivity (B5)]
- The gain comes from the declared cells. The taxonomy contributes four things:
  - filing of unlabelled arrivals (81.6% against 72.1% by descent);
  - a size-matched certificate that attaches an error rate to few splits (2 of 70 at per-family FDR 0.05 on the R512 tree of record) and discriminates where a Gaussian-mixture LR certifies everything; [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B18): add "(hierarchical BH over nested sites, 300 reps, bareq512_s42, R512; id-disjoint only)" and, for the GMM contrast, "on these embeddings, at p = 10; zero judge calls, geometry of construction members only" (prog L21395)]
  - support per cell;
  - names.
- The taxonomy does not contribute partition quality: one anchor-free tree is a worse partition than a flat mixture on MMLU-Pro. † REG-2 and FLAT-MIX-ANCHORED test its generality. At the measured MDE it also shows no routing gain: M is +0.17pp, neither a cost nor parity. † F-TAX. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B6): replaced by: "the taxonomy buys filing, a certificate, support and names; on MMLU-Pro its cells are a worse partition than a flat mixture at the same granularity (af_clean_s42, one draw; the anchored control ties, reported only; mechanism not identified); no routing gain is shown"]
- Where only a judge verifies, fidelity is set by the reference: a paired +12.6pp, and 0.852 at board scale. [P-FAM 2026-09-27, applied by the registrar (RP01 B18) (docs/reviews/RULING_w0_p2dca_family.md, 5effe96): +12.6pp and 0.852 are p2dca judged family — history, not evidence; this clause cannot stand as a claim and is † OPEN until RP04 (level by reference class), RP20's ONE leg (paired contrast) and RP19 (G21) report (ruling section 4)]
- In judged cells the instrument publishes undominated sets, declines the frontier, and leaves certificate calibration UNDETERMINED.
- The cost of judged trust grows super-linearly with the roster: exponent 1.80 [1.28, 2.32], P excluded, planning scale. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B18): add "2 anchors, k 12->37, planning scale on the GROK-CALIB pair [P-FAM (c)]; 'P EXCLUDED', NOT 'M EXCLUDED'" (prog L19459, L19526-L19530)]
- The licences that survive a second embedder, tree draw and corpus are the method's. The rest are published as properties of one draw. † REG-2.

Unlike A's "the table stands either way", this claim can be wrong: REG-1, F-TAX and REG-2 each name the outcome that rewrites a clause. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B5): REG-1 is a sensitivity, not a replication]

## What this framing does NOT show
- It runs nothing and moves no recorded number. Every † clause is a prediction.
- Nothing in it replicates on a content-closed split except FLAT, the certificate on R256 objects, and K46.
- It does not show that any embedder other than qwen3, or any tree draw other than seed 42, reproduces any licence.
- It does not show that the tree adds routing value, or that label-free cells pay (UNION-AF-ROUTE is unrun).
- It says nothing about human preference, the frontier order, "calibrated", sub-anchor rows, agents, or drift under v2.
- "Only where no model dominates" is not licensed; the licensed words are "on two rosters".
- The dominance screen is a necessary condition for G > 0 by construction, not an independent predictor.

## How the skeptic's defects are resolved
| Skeptic row | Resolution |
|---|---|
| 1 | The R2 LRT moves to the r8 disclosure. The registrar inserts a bracket on ledger L149 naming its object. |
| 2, 3 | Handled by S4. |
| 4 | KEY-INTERACTION-V2 is dropped. It becomes a secondary readout of REG-1 on declared cells, with a TRAIN cross-fit fallback. |
| 5, 7, 8, 9 | REG-2 is rebuilt around them. |
| 10–18 | The licensed words are used in the SQs above. ARENA-13 is dropped. |
| 19, 20 | Handled by S1 and S2. |

On row 7, the skeptic's "derive the bar from each embedder's own isotropic null" needs a correction. The isotropic null depends only on dimension, so at 256-d the record's rule reproduces 0.025. The confound left over is embedder anisotropy, so REG-2 prints it per arm.

## Delegation plan and draft registrations

The registrar commits these texts before any code.

### REG-1: V2-DECLARED-CELLS (G14's declared half)
- **Instrument:** the ROUTER-CLEAN-POLICY fit plus its two-stage bootstrap, unchanged, on pv2_1575de61bb20e977 with declared (source, domain) strata. Key only; no tree.
  - Secondary readout: interaction-only R using PROFILE-RELIABILITY-INTERACTION's estimator.
  - Tertiary readout: the share of strata whose TRAIN argmax differs from the global one, against a logit-additive null fitted on TRAIN. This is a readout only.
- **Hygiene:** fit on TRAIN only. The EVAL key is read once, through eval_view, only after a ruling by the data-steward and arena-specialist.
  - Fallback: a component-level 2-fold cross-fit inside TRAIN, worded "TRAIN cross-fit" and never "held-out".
- **Criteria:**
  - C1: the CI of G excludes 0.
  - C2: the lower bound of R is above the null's p95.
  - Printed beside them: G without the 422 residual EVAL items, and G leaving BBH out.
- **Predictions:**
  - G in [+1.5, +4.0]pp.
  - BBH carries at least 50% of G.
  - The leave-BBH-out interval covers 0. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B13): the prediction is: leave-BBH-out in [0, +2.5]pp; it may or may not cover 0; DESCRIPTIVE-ONLY. The only analogue is a point derived from the DESCRIPTIVE per-source table (router_clean_policy_outcome.txt L125-L132): +1.305pp on 4,754 items; no interval exists in the record]
  - R in [0.78, 0.90].
- **Falsifier:** C1 fails. The USE clause is then withdrawn as a content-closed claim, and +2.92 stays an id-only historical result.
- **Support:**
  - Denominator: 6,153 EVAL items in 5,642 components (prog L16193–L16198), joined to the 18-model key. Coverage is UNDETERMINED until the steward checks the join.
  - Clusters are components. The DEFF prior is 1.31–1.37, n_eff ~4,700–4,900 and MDE 1.6pp (ledger L182); DEFF is re-measured. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B14): that n_eff is paeec's (6,482/1.37-1.31 = 4,731-4,948; on 6,153 items the same DEFF gives 4,491-4,697), and the paeec DEFF omits v2's component clustering: the EVAL-side component Kish is 1.304 = 8,021/6,153 (BBH 1.733, MuSR 2.476; manifest REG_ARCHV2-SPLIT-2 outputs[2].checks.v2.kish_eval_items, recomputed by the registrar); re-derive per plan R-B and re-measure on the split before registration; draft 1's "1.89" appears nowhere (kish_key 1.9047, kish_component 2.1727)]
  - Status: SCOREABLE for G ≥ ~1.6pp. A smaller true G reads UNDETERMINED. The leave-BBH-out figure is DESCRIPTIVE-ONLY.
  - Structural check: the criterion is reachable at infinite budget if and only if true G ≠ 0.
- **Cost:** 0 calls, minutes of CPU. It is a pool reader, so it needs a rule-7 window.

### REG-2: EMBEDDER-CROSS-FLAT (staged)
- **E0, zero builds:** the FLAT instrument on a second qwen3 anchor-free tree (candidate af_s42_o1, ledger L244), only if the steward shows its held-out set is content-closed against its TRAIN. Its split may be p8a29, not p2dca. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B15): STRUCK, no valid object: af_s42_o1 IS on p8a29 (its config.toml L5-L6: "Same p8a29 split ... 70.4% in-sample") and is membership-identical to af/seed_42 (ledger row ANCHOR-FREE-REDRAW R4), so it is neither a second draw nor held out from FLAT's 3,445]
- **E1, construction:** label-free anchor-free builds on af_clean_s42's TRAIN side (8,125 fit texts, steward 9073a8a).
  - Arms: a qwen3 draw control (a new seed, required if E0 has no object), nomic-embed-text, mxbai-embed-large and embeddinggemma. The TOML is identical except the model (and the control's seed). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B16): (a) a new-seed qwen3 control on af_clean_s42's pinned split is a byte replay (prog L4676-L4680); (b) "the TOML is identical except the model" cannot be done: the model is the JVM property -Dtaxoadapt.llm.embedding-model (h9_embed_nomic.toml L3-L6) and an unknown TOML key is fatal (HeadlessBenchmarkRunner.kt L2261). Use plan R-D / R-G]
  - Raw text with no prefix, matching the record.
  - A 256-d slice only where the model card documents Matryoshka truncation; the specialist verifies this, and the h9 config's assertion is not a source. Otherwise native dimension, flagged as dimension-confounded.
  - Bar by the iso rule (0.025 at 256-d), with an anisotropy readout per arm.
  - Each arm is scored by the unchanged FLAT instrument at k = its own leaf count, V seeds 0–4. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B16): (c) the unchanged FLAT instrument cannot score another tree: flat_mix_mmlu.py (blob c5cc7934) hard-codes POOL_ID (L89), K (L92), FIT_N (L94), T_SNAPSHOT (L99), T_RUN (L100), T_LEAVES (L102), READOUT_TXT (L107), PIN_TABLES (L116) and ALLOWED_DB_BASENAMES (L128), and reads the qwen3 embeddings_cache.db; parameterise after MIX-FLAT-SELFTEST-GAPS with a delta READY (plan R-D / R-G)]
- **Criteria:** FLAT's C1/C2/L1, verbatim, per arm. How each arm reads:

  | qwen3 draw control L1 | Embedder arms where L1 fires | Reading |
  |---|---|---|
  | Fires | 2 or 3 of 3 | The loss replicates, one draw each |
  | Fires | 0 or 1 of 3 | FLAT narrows to "under qwen3" (non-replication) |
  | Does not fire | any | FLAT narrows to "one draw"; the embedder contrast is UNDETERMINED |

- **Predictions:**
  - The control fires.
  - At least 2 of 3 embedder arms fire, with purity differences in [−6, −2]pp.
  - The root axis is quantitative/discursive in all arms (descriptive).
- **Falsifier:** the control fires and at most 1 of 3 embedder arms fires.
- **Support:**
  - Denominator: 3,445 held-out questions (FLAT qualifier (a)); clusters are questions.
  - Purity MDE 2.1pp; F6 MDE 1.00e−3. L1 is bound by each arm's own measured spread_V.
  - Structural check: a loss smaller than max(MDE, spread_V) cannot be reached at any budget, so UNDETERMINED is registered per arm.
  - Status: SCOREABLE per arm. The cross-arm difference is DESCRIPTIVE-ONLY (one draw per arm against the ARI seed floor) and is not scored.
- **E2, optional, in the author's window:** a 300-rep site null per arm, descriptive.
- **Cost:** 0 calls. The cost-estimator prices the machine time; for reference, one 97-site null took 134.5 min (ledger L177) and one 1024-d build took 594 s (ledger L86).
  - Embeddings: 3,520 missing for gemma and all of them for mxbai. These are the skeptic's counts, to be re-verified by key.

### Waves (the first five are zero-call)
- **W0, data-steward:**
  - Back up and checkpoint the nomic and gemma caches (their -wal files are non-empty), and pin per-table hashes of embeddings_cache.db.
  - Rule on the v2 key join and eval_view, with the arena-specialist.
  - Rule on af_s42_o1's closure.
  - Count v2 EVAL per stratum, including the 422 residual items.
  - Check gemma coverage by key.
  - Run DATASET-SURVEY, a table only. The admission legs are the LCB legs (prog L19745), 120 EVAL items per stratum (FW L271), CK-CLOSE-closable, and no dominant model. The leads are unverified: more models on the six Open LLM Leaderboard v2 tasks, HELM per-instance outputs, and LCB beyond 26 models.
- **W1, registrar:** commit F-TAX, REG-1, FLAT-MIX-ANCHORED (Support uses C2 SE 0.357e−3), LCB-STAGE0-POWER-RESIM, REG-2 E0 and REG-2 E1. Insert the L149 bracket.
- **W2, engine-coder and tree-construction-specialist:** build each script with `--dry-run`. The specialist writes the E1 TOMLs (one knob per arm) and verifies Matryoshka support.
- **W3, adversarial-reviewer:** READY at zero calls.
- **W4, run-operator:**
  - Pool readers (REG-1, FLAT-MIX-ANCHORED, E0), run serially.
  - Then POWER-RESIM (CPU, not a pool reader).
  - Then the E1 builds, one construction at a time, after the author orders them against ARCH-V2-E-T.
- **W5:** reviewer on the numbers, registrar for outcomes, research lead for the synthesis, science-writer for prose.
- **W6, paid, each under 4,000 matches with its own registration:** G17 (1,224 calls), G21 (~2,000), G24 (~1,224). The calibration board goes only on the author's go.

Zero-call waves may start under the standing authorisation (memory `autonomous-scheduling-authorised.md`). Adopting this framing does not fall under it; that is the author's call.

## Decisions that are the author's
1. Adopting this framing and the central question, and any rewrite of report/ (RQs, abstract, REPORT-FIXED-POINT-SCOPE, REPORT-BACKGROUND-ACCEPTANCE-TEXT).
2. Rebuild-or-disclose. DISCLOSE is only the v2 default (prog L15082 bracket). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, B17): prog L15080, the QUALIFIED bracket inside item (4)]
3. Whether the r8 paragraph appears in the thesis, and where.
4. The order of the machine lane (ARCH-V2-E-T against REG-2 E1), which embedders to run, fixing the gemma runner, and embedding mxbai from scratch.
5. Whether an external corpus enters scope (ingest, CK-CLOSE, roster responses).
6. The board size, and any calibration board above 4,000 matches.
7. The CERT-FAMILYWISE-REPS window (11.7 h and a 14 g heap, against the half-machine cap).
8. Whether to override ARCH-V2 decision 5 (declared cells).
9. The word to register LEAF-INTERACTION.
10. config/application.yml, .env and .gitignore.

## Files
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/CONTEXT.md
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/design/FRAMEWORK.md
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/judge_v2_program.md
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/test_ledger.html
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/queue.json
- Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/results/evidence/ARCH-V2_SYNTHESIS_2026-09-23.md
- Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/clean_subset_reanalysis.txt
- Z:/FAC/TUBerlin/THESIS/TaxoArena/tools/analysis/clean_subset_reanalysis.py
- Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_configs/h9_embed_nomic.toml
- Z:/FAC/TUBerlin/THESIS/TaxoArena/report/01_Document_administration/b_Meta.tex

<!-- Committed verbatim by the registrar on 2026-09-27 (Wave-0 record; the author's adoption, plan Amendment 25; programme section "Author's decision 2026-09-27 (recorded by the registrar;  ..."). Source: the orchestrator's scratchpad framing_of_record.md (CRLF; sha256 of the CRLF source bytes a34c1b2cbc45dafe); this copy is its LF rendering (verbatim body blob:575940a4 / sha256-lf16:1dfea466cdb448d9, i.e. the file before this comment line and before the brackets). The line-end brackets [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, ...)] and [P-FAM ...] are the registrar's insertions; nothing is rewritten. Line numbers of the source are preserved: this comment is appended at the END. -->
