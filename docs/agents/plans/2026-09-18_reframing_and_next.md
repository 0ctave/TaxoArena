# The reframing after the night batch, and what to continue (research-lead, 2026-09-18, ledger v114, HEAD 945076c)

Read-only synthesis over CONTEXT.md, the thirteen outcome sections of 2026-09-17/18 (PROG L5026-L5333, L5594-L5853,
L6388-L7026), the two review files (docs/reviews/2026-09-18_night_batch.md, 2026-09-18_profile_batch1.md), the plan of
2026-09-17 and the agent-corpus survey. Nothing was run, built, registered or edited except this file. Citation form:
[LEDGER id]; [PROG Lnnnn]; [FW Lnnn]; [REVIEW night/batch1]. Every number below is quoted from the line named beside it.

## 1. THE REFRAMING (the paper's spine)

### 1.1 What the framework is now shown to be, sentence by sentence

(a) The taxonomy. The embeddings-only tree exists on every draw with the same first axis (C1 5/5, C2 4/4, 12/12
categories) [PROG L6430-6431]. Its certified structure is a small discursive spine of 5 sites (root n00000001, n00000005,
n00000017, n00000016, n00000032; min record n 629) that reproduces in R1, R2 and R3, plus a per-draw fringe of 10-16 of
64-69 sites (SD ~2.6); the quantitative side has zero re-draw-stable certified sites [PROG L6424-6428, L6489]. On the
clean split anchors neither cost nor buy certification: anchored 11 of 60 against free 14 of 69, C6 FAILED, F4 FIRED,
"anchors cost certification" withdrawn as a headline [PROG L6437, L6458-6467]. The geometric certificate and the capability
content of a split select nearly independently: CAP-GATE Jaccard 0.29 at t = +1 [PROG L5040], CAP-PRUNE Jaccard 0.241
against a hypergeometric chance of 0.148, P(joint >= 7) 0.12 [PROG L6544-6545]; only 7 of the 20 pruned survivors carry a
held-out interval excluding 0 [PROG L6537-6540]. The quantitative depth-1 split is k-selection-fragile at the bar: R1
accepted k = 2 at min-pair 0.025148 against the bar 0.025 (1.006x) and is uncertified at 0.746 where the record, R2 and
R3 refuse k = 2 and certify k = 3 at 1.69-1.73x [PROG L6418-6423, L6478-6481]. [CORRECTED 2026-09-19 by K-SELECTION (outcome 4c25e56, review a949a35; programme section K-SELECTION, L9420): "k-selection-fragile at the bar" reads: k-selection at the bar, resolved at the depth-1 site by a geometric hysteresis rule (K-SELECTION) at the cost of a different tree below it (73 vs 82 leaves on the clean draw; purity -1.5 pp established; certified count +4/+3 on the in-sample draws); the primed trees are STRUCTURAL EVIDENCE ONLY and R1 af_clean_s42 remains the clean free tree of record.] Purity moves 2.3-3.4 pp on a sample
re-draw; the anchored-over-free purity gap is 4.3 pp clean [PROG L6486-6488]. The tree earns its place through routing on
the union (+3.38pp clean; leaves lose to designed strata, -0.011 +- 0.007) and nothing on MMLU-Pro [FW L179-180], with a [ID-ONLY 2026-09-23 (CLAIMS-SWEEP-BRACKETS, registrar): pool union paeec37aa28063c75; verified by id only, not by content; reviewed twins on this pool (reviews 1df2cf1, 8ebfa7a): 471 ids / 427 texts exact, 478 / 432 norm-v1 (GPQA 288, MMLU-Pro 185, MATH 3, BBH 2); see docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT) and L14455-L14487 (SPLIT-FOLLOWUPS).]
~20% proportional attenuation of every routed contrast at 19% misrouting [FW L183]. [RESTATED 2026-09-23 by the adversarial audit (insertion only; +3.38pp stands and is unchanged): the sentence above names ONE comparator. +3.38pp is the gain over the BEST SINGLE MODEL (MC-E2E criterion (1), clean pool paeec37aa28063c75: +4.37 / +2.43 / +3.34pp per seed, mean +3.38, 1,946 / 1,973 / 1,914 questions per see [ID-ONLY 2026-09-23 (CLAIMS-SWEEP-BRACKETS, registrar): pool union paeec37aa28063c75; verified by id only, not by content; reviewed twins on this pool (reviews 1df2cf1, 8ebfa7a): 471 ids / 427 texts exact, 478 / 432 norm-v1 (GPQA 288, MMLU-Pro 185, MATH 3, BBH 2); see docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT) and L14455-L14487 (SPLIT-FOLLOWUPS).]d). Against the corpus's own metadata -- the comparator a reviewer names first -- the tree COSTS: MC-E2E criterion (2) records a clean metadata cost of mean +0.71pp (per seed -0.46 / +1.22 / +1.36), so reading the declared (source, domain) label beats routing through the tree on 2 of the 3 seeds, and the row's own does_not_show carries "that inferring the cell costs the router essentially nothing (clean metadata cost mean +0.71pp)". Below the strata the tree also loses: MC-LEAF reads leaf 0.592 against domain 0.601, -0.9 +- 0.3pp (n = 6,479 reserved, 147 leaves; the row carries [FLAG 2026-09-15], its reserved side's contamination status never re-verified). And the magnitude is not seed-stable: MC-E2E criterion (3) FAILED, across-seed spread 1.56pp against a within-seed SE of 0.53pp. [CORRECTED 2026-09-23 by the registrar (MC-E2E criterion (3) figures; insertion only, zero calls): 'spread 1.56pp vs within-seed SE 0.53pp' are the FIRST, CONTAMINATED, pre-MATH-FIX readout's figures (experiment_results/multicorpus/router_e2e.txt, 'across-seed spread 0.0156 vs mean within-seed SE 0.0053', n = 6,481 per seed); the CLEAN MATH-FIX readout that +3.38pp comes from prints 'across-seed spread 0.0194 vs mean within-seed SE 0.0093' (experiment_results/multicorpus/router_e2e_mathfix_clean.txt, n = 1,946 / 1,973 / 1,914), i.e. 1.94pp vs 0.93pp. The verdict, (3) FAILED, stands under both. The contaminated pair entered this R2 bracket through the restatement pack R2 (9b41986).] THE CLAIM AT ITS REAL STRENGTH AND NO HIGHER: where no metadata exists the tree files an arrival into the designed (source, domain) address space at 81.3% Top-1 source+domain and 96.2% source (MC-E2E falsifier note; the union routing row reads 81.58% [80.62, 82.50] source+domain and 95.46% source, FRAMEWORK L53), and routing on that prediction beats the best single model by a mean +3.38pp (seed range +2.43 to +4.37, spread exceeding the within-seed SE) at a mean cost of +0.71pp against reading the label, the tree being worse than the label on 2 of 3 seeds; what the tree adds beyond the label is the split discipline and the per-cell support, not accuracy. Routing error is then an unmeasured proportional attenuation of every routed contrast, slope 0.795 (~0.80; ROUTING-ATTENUATION record) at 19% misrouting (ROUTING-ATTENUATION, criterion FAIL). FURTHER QUALIFIER, LOAD-BEARING: the 52 (source, domain) strata are GIVEN to the tree as registered anchors, not discovered by it -- experiment_configs/multicorpus/mc6_s42.toml L4-5 "Depth-1 anchors are the 52 (source, domain) keys: 24 BBH + 7 MATH + 3 MuSR + 1 IFEval + 3 GPQA + 14 MMLU-Pro", and in the DEPLOYED federated union experiment_configs/multicorpus/union_s42_flatleaf.toml L10-12 "depth-1 children = the per-corpus roots ..., depth-2 = their designed domain anchors" with per-corpus configs stating the same (bbh_s42.toml L4 "Depth-1 anchors = 24 BBH sub-tasks"). The 81.3% is therefore the Top-1 accuracy of a nearest-leaf-centroid classifier into a SUPPLIED 52-class address space whose classes were registered in advance, read off the leaf's ancestors; it is a filing rate, never a discovery rate, and the record's own rule says so ("Anchors are the reporting address space only and are born by registration, never by the loop", FRAMEWORK L53). Write "files into" or "reconstructs the assignment of queries to the designed strata", never "discovers the strata".] [CORRECTED 2026-09-23 by ROUTER-CLEAN-POLICY (2f53675; numbers review docs/reviews/2026-09-23_router_clean_policy_post.md, 21c4fda): on the split of record the deployed gain over the best single model is +2.92pp, two-stage [+1.81, +4.02] (replacing +3.38pp), and the metadata cost is M = +0.17pp [-0.61, +0.95] (replacing +0.71pp). The tree is NOT shown to cost against the label, and it is NOT shown to match it: the difference is indistinguishable from zero at this support (MDE ~ 1.1pp). "Worse than the label on 2 of 3 seeds" and the per-seed -0.46 / +1.22 / +1.36 are withdrawn as evidence (contaminated-fit split, 30% support per seed; 4,536-4,568 EVAL ids on the fitting side). "Not seed-stable" is replaced by: no seed statement is made on the pinned split; the policy-variance share is phi = 0.31 (R3 HELD). The rest of each sentence stands: the filing-not-discovery qualifier, the 81.3% / 96.2% routing rates and their A1 bound, and "what the tree adds beyond the label is the split discipline and the per-cell support, not accuracy". The leaf sentence (MC-LEAF -0.9 +- 0.3) keeps its flag; C3 re-reads it as -0.09pp [-1.09, +0.91], DESCRIPTIVE. NOTE: the coordinator's morning restatement (this bracket's R2 predecessor) carried the contaminated figures; they are replaced here by the clean policy's numbers.]

(b) The profile. It is real on the key: 127 of 280 (model, anchor) deviations key-certified (45.4%) [PROG L5774];
interaction-only (model- and anchor-demeaned) reliability 0.8665 [0.8000, 0.9330] on the 14 anchors against a 0.31
curvature floor [PROG L6867-6876], 0.8537 on the 52 union strata [PROG L5648]; 52/52 strata classed, class of record
27 PASS / 12 PASS-WITH-INTERVAL / 13 FAIL, order reading 39 / 8 / 5 [PROG L5620-5623]. It is not real on the judge: 22 of
280 judge-certified deviations, not key-corroborated (14/22 same-sign vs 55.7%, P 0.30), 3 of 22 wrong(established) and
those three are the frontier residue (top-cluster models above standing in Law, below in Math) [PROG L5795-5803,
L5828-5832]; judge reliability 0.6728 (x12) / 0.7183 (merged) is already interaction-only and the like-for-like gap to the
key is +0.19 [0.04, 0.35] on x12, +0.12 [0.03, 0.21] merged, 14/14 folds [PROG L6895-6903]; every difficulty-stratified
board is UNDETERMINED (42 of 42 anchor strata, nominal < 3) [PROG L5163-5164]. The difficulty axis inside a cell is the
reference's: 72-79% of the -15.5pp easy-to-hard accuracy drop is the reference-correct rate falling 98.4% -> 77.7%; the
judge's own residual within reference-correct is -4.5pp [-6.7, -2.5] [PROG L5133-5140].

(c) The judge. It is a reference transcriber. The reference ladder orders the instrument: CHECKER_OUTPUT 0.958 / 0.993 on
terminated MATH traces [PROG L3990] > CACHED_SOLVE 0.849-0.865 [LEDGER STACK-v2, GROK-CALIB] > NONE 0.738 [LEDGER
PAIR-NOREF] > SPECIFICATION 0.658 [LEDGER GEN-ARENA] [RESTATED 2026-09-23 by the adversarial audit (insertion only; every rung's number stands): this is a POSITIONING ACROSS CORPORA, ROSTERS AND POPULATIONS, not a ladder and never a paired test. BFCL-JUDGED-PILOT's does_not_show already states the rule this sentence broke -- "a paired comparison with any ladder rung: the rungs were measured on other corpora, so the ladder reading is a positioning across corpora and never a paired test; the rungs' own sampling error (PAIR-NOREF n = 826) is not carried". EXACTLY ONE RUNG-TO-RUNG STEP IS PAIRED WITHIN A CORPUS: CACHED_SOLVE 0.864 against NONE 0.738 on identical matches (PAIR-NOREF criterion (3): +12.6pp, 144:25, p = 1.6e-21, on R3's 944 key-decidable MMLU-Pro matches; decomposed 74% abstention / 26% discrimination, committed-only 0.929 vs 0.897; ties 0.070 -> 0.177). Each rung with its corpus, roster, reference form and population: CHECKER_OUTPUT 0.958 -- MATH, 8 models, checker (exact) output as reference, cheap judge, TERMINATED TRACES ONLY (16.5% of question-pairs excluded; the exclusion is selective on correctness, removed rows' key accuracy 0.034 vs 0.427), convention A ties wrong, n = 1,537 of 2,996 matches over 383 judged questions, union pool paeec37aa28063c75; 0.956 with INVALID wrong (n = 1,540), 0.993 convention B (n = 1,484). [STAGE3-MATH-CAPFREE] CACHED_SOLVE 0.852 -- MMLU-Pro, 12 models, one cached grok-4-1-fast-reasoning solve as a possibly-wrong reference, Mistral judge, x12 board of record, convention A, n = 4,507 key-decidable of 9,142 verdicts, pool p2dca21ab5f4ef3ae [ARENA-V2]; the shipped cheap judge on the same schedule 0.849, ties wrong, n = 4,499 [GROK-CALIB]; 0.865 is the R3 944-match arm-selection maximum and belongs beside the selection caveat of R1, not in a ladder. [STACK-v2] NONE 0.738 -- MMLU-Pro, 12 models, no reference block, deployed pairwise format, R3's 944 key-decidable matches, paired against the 0.864 arm on identical matches. [PAIR-NOREF] SPECIFICATION 0.658 -- IFEval, 8 models, the constraint LIST (the verifier's specification, not its output) as reference, cheap judge, n = 407 key-decidable of 1,200 matches, ties 0.256, flip 0.380, on a Python-recomputed seed-42 0.30 reserved side that is NOT the union pool (CERT-CORPUS overlap 55/162 IFEVAL). [GEN-ARENA] Beside these and not a rung: MATH unfiltered, checker as reference, 0.935 on 568 key-decidable of 1,800 matches, cap-hit rows included [GEN-ARENA]. So 0.958 vs 0.852 is a cross-corpus, cross-roster, cross-population contrast (different corpus, different 8- vs 12-model roster, different reference FORM, and a terminated-only population on one side); no paired test exists between them and the record registers none. The IFEval rung is additionally PERMANENT and not a design choice: the 2026-09-23 IFEVAL RULING (docs/agents/leads/2026-09-23_ifeval_ruling.md, af116f8) establishes that IFEval has no question-level checker output at all (its verifier emits a predicate ON a response), so the CHECKER_OUTPUT rung is unrealisable there and a per-response pass vector is an ORACLE-CLASS object that may never be quoted beside MATH's 0.958.]; agreeing with the reference is worth 2.7x being right (upper bound)
[LEDGER CONSENSUS-FIT]; the value of a reference is its answer, not its structure [PROG L4419]. REF-QUALITY-MONITOR is
the accounting identity A = ref x 0.93 + (1 - ref) x 0.34, residual -0.09: 14 reference readings, not 56; a vintage and
difficulty monitor, never a judge monitor [PROG L5726-5735]. The answer-disagreement filter removes a reproducible
non-key order (AGREE-only board R 0.648 vs 0.46-0.50 random, r -0.18 with the key profile) and halves nothing: filtered
R 0.5613 [0.3385, 0.7842] vs 0.7183, 58% of the drop support and 42% selection [PROG L6807-6815]. The widener's b1 is
identified at the registered bar only: pooled delta-deviance 6.51 >= 3.84 on 46 events that are 29 distinct edges (phi
0.735); under a correlation-preserving null the bar has size 0.14 and p ~ 0.07; power 0.62 single draw, <= ~0.8 pooled;
LOAO nominal 1.0-1.1 [PROG L6621-6647]. A perfect reference buys +16.4pp and still misses the frontier order [FW L13];
length is the best-measured bias (+0.39/1k chars) [LEDGER H3] but not the frontier pair's cause [LEDGER ARXIASK].

(d) The arena's economics. The newcomer bands are a bisection-steps shortfall over a structural floor: sonnet 7 = (i)
key-tie 1 + (ii) frontier 3 + (iii) separable 3, the separable tiers incumbents never judged against (5 iii-b, 1 iii-c,
0 iii-a); gpt-4o-mini 3 = 1 + 1 + 1 [PROG L6693-6700]. The (i) + (ii) = 4-tier residual fails criterion (22) at any
budget; the mid anchors at 0.505 / 0.510 would need 31,001 / 7,549 question-pairs to certify [PROG L6701-6703,
L6725-6726]. More matches at the same anchors buy nothing for sonnet (7 [7, 7] at every n, flat by design) and 3 tiers for
gpt-4o-mini (6 -> 3) [PROG L6705-6711]; PLACEMENT-CURVE as priced is declined [PROG L6724-6725]. The frontier stays
unorderable [FW L13, L252]; calibration at the operating point stays UNDETERMINED on every board [FW L253; PROG L6617].

(e) Agents. The admission rule works as a rule: parts (a) (b) (c) (e) VERIFIED by command, (d) FAILED for one undeclared
number, the per-episode artefact cap [PROG L6944-6960]. BFCL-Result multi_turn is admissible for checker-built rows only:
base 72/75 = 0.960 PASS-AT-POINT under the pre-fixed reading (55/300 empty-turn failures counted as decided; excluded,
0.81 and no stratum passes), the other three strata PREDICTIVE-ONLY [PROG L6961-6970]; every stratum has 57 EVAL tasks
(57 families) and is description-only; a judged pilot on base is a calibration / canary object, not a cell [PROG
L6989-6993]. Cap-hits are an agent property (Llama-3.3-70B carries 267 of 303), not a corpus property [PROG L6980-6981].

### 1.2 What the paper can now CLAIM, must RETRACT, should REFRAME

CLAIM (each with its row): a reproducible label-free tree with a 5-site certified spine and a per-draw fringe
[ANCHOR-FREE-REDRAW]; anchors as names, not certification [REDRAW C6/F4]; geometry and capability content as independent
selections [CAP-GATE-POSTHOC, CAP-PRUNE]; a key-built anchor profile that is a profile, 0.87 interaction-only against a
0.31 floor [PROFILE-RELIABILITY-INTERACTION]; 52 union strata classed on the key, 39 order-reliable
[PROFILE-INTERVAL-ALL-UNION]; the judge shortfall stated like-for-like, +0.12 to +0.19 [PROFILE-RELIABILITY-INTERACTION];
the reference ladder and the identity behind "reference quality" [REF-QUALITY-MONITOR, REF-CHECKLIST]; the placement
decomposition and its 4-tier floor [PLACEMENT-CEILING]; an agent admission rule verified on a real archive
[AGENT-CORPUS-ADMISSION]; b1 identified at the registered bar with its honest size printed [ITEM-26-POOLED].

RETRACT: the 16-vs-5 headline and "anchors cost certification" (the p8a29 split's) [PROG L4306 bracket, L6464-6465]; the
halved newcomer bill [FW L189 and L405 brackets]; "certified trunk" as written (root + both depth-1 + depth 2-5) [PROG
L4340 bracket]; "one bar step from not existing" -> "one bar step from a different accepted k" [PROG L4599 bracket]; any
"per-cell judge quality monitor" [PROG L5735]; any "certified above / below its own standing" on a judge-built cell [PROG
L5818-5819]; "the filter destroys the profile" (never written into the rule) [PROG L6805-6806].

REFRAME: the tree is not the ranking instrument; it is the instrument that measures how much of a fine-grained evaluation
is GEOMETRY (the certificate, independent of capability content: Jaccard 0.24-0.29 at chance), DIFFICULTY (anchor
difficulty is 9% of the K12 accuracy variance, 58% of the union table's; 72-79% of a within-cell contrast is the
reference's [PROG L6877, L5646, L5138]), REFERENCE (the identity A = 0.93 ref + 0.34 (1 - ref); 2.7:1) and CHOICE
(k-selection at the bar, 3/4; the fringe per draw; the filter's 42% selection term; the establishment rule's 1-3 events).
The ranking lives in the key where a key exists and in the reference where it does not; the tree's contribution is
routing on the union and the honest cell for the profile, and its certificate says where the geometry is stable.

## 2. WHAT TO CONTINUE, ranked (value per call, then what it changes in the paper)

Common hygiene: registration before code; caches mode=ro; pool id printed first; both conventions; wrong(established);
UNDETERMINED as an outcome; one construction at a time and nothing reads the pool meanwhile; closed lines [CTX §5] plus
ANCHOR-FREE-CERT's levers, MULTI-OWNERSHIP as a judging mechanism, dual-cell judging, and FW L53 (certification is never
an admission gate) untouched.

R1. A8 STABLE-CELL-SET on the 5-site spine. Zero calls, this week, unattended.
    Claim: the re-draw-stable certified sites, read on the CLEAN free tree R1 af_clean_s42 (the tree any registration must
    name for the TRAIN-ONLY guard [PROG L6474-6475]) as a 5-cell partition (n00000032; n00000017 minus n00000032; n00000016;
    n00000005 minus both; the quantitative remainder = complement of n00000005, NOT itself a stable certified site
    [PROG L6427]) carry a key-built profile on the pool of record. Instrument: anchor_free_readout.py view A on R1's
    matched sites (global-greedy Jaccard >= 0.5, the registered rule [PROG L6492]); per-cell held-out support; key
    interaction-only R with jackknife (profile_reliability.py --interaction-only); F6 key-only leaf information beside the
    14 categories' +10.79. Criteria: every cell >= 120 held-out q on p2dca; key interaction-only R >= 0.70; F6 >= +10.79.
    Predictions: 5 cells, all >= 120 q; interaction-only R 0.75-0.88 (5 columns, wide support); F6 +8 to +11, FAILS.
    Falsifier: any stable cell below 120 q or key R < 0.70 (then the spine is structural only, no profile home without
    labels). Cost 0 calls, 0 builds. Closed lines: no leaf row, no judge row on any free cell. Changes: one sentence,
    "an anchor-free profile home exists at 5 cells, with less information than the 14 names" (or not).

R2. K-SELECTION rule at the bar, as a registered construction change with REDRAW as its test. Zero calls, builds only.
    Claim: the quantitative depth-1 3/4 is the greedy first-k-that-passes rule's, not the corpus's [PROG L6421]. The rule
    must stay GEOMETRIC (FW L53 forbids reading the certificate at construction): either (i) max-margin, evaluate every k in
    2..K that clears the bar and take the k with the largest min-pair / bar ratio, or (ii) hysteresis, accept k only at
    min-pair >= 1.05 x bar (R1's 1.006x is refused, k = 3 at 0.056 / 0.025 = 2.2x accepted). Register ONE form (my call:
    hysteresis at 1.05, one knob, fail-closed TOML key, inert when absent; engine-coder in a worktree, reviewer MERGEABLE,
    full suite). Arms: R1', R2', R3' (the three sample draws) rebuilt under the rule, own site nulls at 300 reps, readout
    against REDRAW's arms. Predictions: R1' quantitative depth-1 certifies at k = 3 at 1.6-1.8x; discursive site and root
    unchanged (2.10-2.13, 1.12-1.14); stable set grows to 6 (adds n00000004); fringe count within +-2 of REDRAW's; purity
    within 1 pp. Falsifier: R1' still uncertified at the quantitative site, or the discursive site loses certification in
    any arm (then the fragility is the corpus's and the record's 3/4 stands as written). Cost: 3 builds + 3 nulls, ~2 h
    serial, nothing else reading the pool. Changes: "quantitative depth-1 3/4 (k-selection at the bar)" -> a stated rule
    and, if HELD, a certified trunk axis as a recipe property; the C3 chip on REDRAW takes a bracket.

R3. UNION-PROFILE-HOME readout (the 39 order-reliable strata vs the 14 anchors). Zero calls, this week.
    Claim: the union strata are the profile's home because they are the only cells with a routing consequence [FW L180].
    Instrument: on the 18-model union key (paeec37aa28063c75, MAIN_union_routing*.csv only): interaction-only R with a
    leave-one-stratum-out jackknife (the 0.8537 has no interval on record [REVIEW batch1 D1]); per source; the 14
    MMLU_PRO_LB strata beside K12 0.8665 with rosters and pools named and no level comparison; for each of the 39
    order-reliable strata, the key's undominated set and whether it differs from its source's. Predictions:
    interaction-only R [0.80, 0.90]; MMLU_PRO_LB 14 strata 0.80-0.90; >= 20 of 39 undominated sets differ from the
    source's (25 of 52 domains differ in best model [FW L180]). Falsifier: < 10 of 39 differ (the strata add nothing to the
    router beyond the source; the home stays 14 anchors + 6 sources). Cost 0. Changes: settles author question 6 with a
    number; the atlas's home and the router's index become one object.

R4. AGREE-ORDER: is the non-key order the filter removes the length preference? Zero calls, this week.
    Claim: the AGREE-only board's reproducible order (R 0.648, r -0.18 with the key [PROG L6809-6812]) is verbosity.
    Instrument: on the merged board's AGREE matches (same predicted letter, both present), H3's logistic of the verdict on
    length difference (beta_len per 1k chars); Spearman of the AGREE-only theta with mean output length per model; the
    AGREE-only split-half R on length-matched matches (|delta len| <= 300, H3b's cut). Secondary leg, registered expecting
    UNDETERMINED: on the 8 wrong-sign deviation cells [PROG L5795-5799], the longer-answer share of the certified model's
    in-anchor wins against the anchor's both-right length share (a 22-cell object; descriptive). Predictions: beta_len on
    AGREE-only >= +2.5/1k (the both-right +3.44/1k of TOPIC-DIFFICULTY [PROG L5145-5146]); Spearman(theta_AGREE, length)
    >= 0.6; length-matched AGREE-only R < 0.50. Falsifier: length-matched AGREE-only R >= 0.60 (the removed order is not
    length; an unexplained judge order is a finding). Cost 0. Closed lines: no length control enters the recipe (H7's
    "ignore length" clause stays closed); no frontier order is read. Changes: PROFILE-R-FILTERED's selection term gets a
    mechanism; links B1 verbosity to the filter and to the deviation residue in one paragraph.

R5. PLACEMENT-STEPS: the further-step design (new anchors, not more matches). Judged, 800 calls, needs a go by precedent.
    Claim: one further bisection step per (iii) tier removes exactly the separable tiers: sonnet 7 -> 4 (the structural
    floor), gpt-4o-mini 3 -> 2 (criterion (22) met). Instrument: for sonnet, 100 filtered dual-order matches against each
    of deepseek-chat-v2_5 (t5), claude-3-5-haiku (t6) and Qwen1.5-110B (t7) = 300 matches; for gpt-4o-mini, 100 against
    deepseek (key gap 0.0199 vs 0.017 [PROG L6726-6727]) = 100 matches; same recipe, cached reference, PRIMARY / A / B;
    match counts fixed before launch (guard 13); band re-read inclusive. Predictions: sonnet (iii) 3 -> 0, band 4 [4, 5];
    gpt-4o-mini band 2 or 3 (deepseek is inside the key's SE ~0.013: a coin flip, recorded as such). Falsifier: sonnet's
    band > 4 after the three steps (steps do not cure it; the band is judge error and NEWCOMER-PLACEMENT-LIVE's "not judge
    error" takes a bracket). Cost 400 matches = 800 calls, under the rule. Changes: FW L15 / L189 / L211 placement cost
    becomes "400 + 100 per separable tier" per newcomer (~1,400 cce for a frontier-adjacent one) and criterion (22) is
    stated as reachable for mid-board newcomers only.

R6. BFCL judged pilot on the base stratum, calibration / canary only. Judged; needs the cap, the agent list and a go.
    Claim: the cheap judge with a checker-output reference reaches the MATH rung on tool-call traces (0.958 [PROG L3990]).
    Instrument: item-19 probe (50 calls on the deployed judge, trace-shaped prompt) before any pilot; then base stratum,
    57 EVAL tasks x 28 pairs of the 8 ingested agents = 1,596 candidate matches, checker-disagreement filtered
    (both-pass / both-fail removed), dual order, cap declared by the author, the artefact = decoded call sequence + final
    state under the cap [PROG L6953-6955]; readouts: key-decidable accuracy under both conventions (bar 0.75), rho with the
    checker board, wrong(established), calibration by the power rule; the grok-4-1-fast-reasoning-FC contestant flagged
    for the self-preference hazard [PROG L7005-7006] and read separately. Predictions: A 0.90-0.96; rho >= 0.95; ties
    < 0.10; calibration UNDETERMINED. Falsifier: A < 0.75 (agent cells are checker-only; the "and agents" half reduces to
    checker-built rows). Cost: 50 + <= 3,200 calls (<= 1,600 matches), under the rule. Changes: the thesis's "for Agents"
    bridge gets one measured sentence with a real agent roster; no profile cell (57 tasks).

R7. Multi-SWE-bench_trajs admission pilot: the first corpus that could carry a profile cell. Zero LLM calls, network only. [CORRECTED 2026-09-22 by MULTI-SWE-ADMISSION (cheap variant; outcome in docs/judge_v2_program.md, review 5ba264c): OVERTURNED for the registered by-repo split. The admission pilot ran at zero calls: 51 (language, repo) strata, 16 EVAL-side, 390 EVAL instances, 0 strata >= 120, so this corpus carries NO profile cell and is DESCRIPTION-ONLY like BFCL; the five repos of >= 120 instances all hash TRAIN (P = 0.168), so the pin, not the corpus's size, decided it. R7's own falsifier fired and MopenHands / MagentLess were never downloaded. C2 HELD (recovery 1.0000; the MSWE-agent cap is 50 steps, recovered from the trajectories, so (c) is MET on that scaffold and "(c) FAILS on MagentLess" was never tested). The only unit that would clear 120 is a python LANGUAGE-level cell (234 EVAL over 7 repos), which is UNREGISTERED, would be checker-built-only (strict D_c 0.33 / 0.44) and repo-clustered (effective n ~85).]
    Claim: 2,092 instances (1,632 + 460 Python) with report.json FAIL_TO_PASS / PASS_TO_PASS, family = repository, stratum =
    language x repo, 3 scaffolds x 9 models on the same instances [lead 2026-09-18_agent_corpora.md §1.3] pass the rule
    set (a)-(e). Instrument: bfcl_ingest.py's pattern (new DB under experiment_results/agent/, no pool_guard import, no DB
    of record), split by family_id = repo under norm-v1, a normaliser for the three trajectory formats, cap recovery from
    the harness configs ((c) is "?" today), strict D_c per (language, repo) stratum, EVAL-side counts per stratum against
    the 120-q support floor. Predictions: (c) FAILS as-is on MagentLess (no cap concept) and PASSES on MSWE-agent /
    MopenHands; D_c >= 0.95 on every language; EVAL ~630 instances over 7 languages, 2-4 strata at or above 120; "agent" =
    (scaffold, model), 27 configurations, stated as such. Falsifier: no stratum reaches 120 EVAL instances (the corpus is
    description-only like BFCL and the profile-cell claim for agents waits on a bigger corpus). Cost: 4.7 GB download; a
    day of engine-coder time for the normaliser; 0 calls. Changes: the first agent PROFILE cell candidate; the judged pass
    on it is priced afterwards at the FW rate (1,530 matches per cell per epoch [FW L219]) and crosses the rule at >= 3
    cells (author's go).

R8. CANARY-BASELINE pass 2 (on/after 2026-09-22). Registered; 600 calls; no go needed [LEDGER CANARY-BASELINE].
    Prediction on record: floor 4-6% contested, lower cross-tier. Changes: the first "continual" sentence; RE-JUDGE-RULE's
    canary trigger becomes live (Amendment 4 [PROG L6641-6647]).

R9. ARM-B reference re-mint (200 frozen questions, ~2,000 cce). Needs a go (creates a second vintage). Criterion agreement
    >= 0.89, prediction 0.92-0.95, falsifier < 0.85 [plan 2026-09-17 C2]. Changes: stamps the legacy vintage; the only way
    REF-QUALITY-MONITOR's monitor can ever move [PROG L5731-5735]; the RE-JUDGE-RULE vintage trigger becomes testable.

R10. MODEL-VINTAGE-CANARY first pass. 0 judge calls; ~0.6M output tokens per roster pass + ~0.21M for the null on the 7
    fixed checkpoints [PROG L6066-6073]; registered, predictions P1-P4 recorded [PROG L6052-6056]. The author's cost and
    decision. Changes: the fifth stamp on every board row; guard 12 extended to contestant vintages.

R11. LEAF-INTERACTION (the unconverted leaf ratio 0.31). Zero calls, low priority. Claim: the leaf-level key 0.8135 and
    judge 0.2559 [PROG L6902] are difficulty-inclusive; the interaction-only leaf ratio stays < 0.5. Instrument: leaf- and
    model-demeaned split-half R on the 87 leaves, key and judge. Predictions: key 0.55-0.70, judge 0.15-0.30. Falsifier:
    judge >= 0.70 (recorded, but it reopens nothing: the sub-anchor line is closed for tree-robustness reasons
    [CTX §5]). Cost 0. Changes: converts one number; nothing else.

This week, zero-call and unattended: R1, R3, R4, R11 (analysis, W-windows only), R2 (builds, lane 1, serial), R7 (lane 5,
network). Need a go: R5 (800 calls; under the rule, asked by the precedent of the block go [plan 2026-09-17 L283-284]),
R6 (cap + agent list + go), R9 (second vintage). The author's alone: R10 (generation cost), and the decisions of §5.

## 3. WHAT TO STOP

- PLACEMENT-CURVE as priced (2 x 800 at the same anchors): cannot narrow sonnet, declined at zero calls [PROG L6724-6725].
- Re-drawing the anchor-free tree to move the certified count: the fringe is a per-draw object (10-16, SD ~2.6) and the
  levers are closed (no lever beats 16 under a common null) [PROG L6489, L4560]; EMBED-AF (B2) is parked unless the paper
  needs an embedder-invariance sentence; ARRIVAL-AF (B3) is parked behind R2 (a k-rule changes what "a certified Law site"
  means).
- A capability-gated construction arm: the rules select independently (0.241 at chance) and 7 of 20 replicate; a gated
  tree would be a different tree with no board; the line stays a PRUNE readout, never a gate [PROG L6552-6555; FW L53].
- REF-QUALITY-MONITOR as a Stage-9 judge signal and DIFFICULTY-PROXY-WIDENER (b2 not identified, power 0.145) [PROG
  L5707-5712, L5735].
- Certified deviations on judge-built cells: not key-corroborated, the frontier residue reappearing [PROG L5818-5832].
- Pooling a third draw of the same judge on the same bytes for item 26: phi 0.735 does not average out; "needs new
  questions, not re-draws" [PROG L6639-6640].
- The disagreement filter as a bill-halver, and difficulty-stratified judged boards (42/42 UNDETERMINED) [PROG L6800-6803,
  L5163-5164].
- MULTI-OWNERSHIP as a judging mechanism and the dual-cell arm (72% identical prompts) [PROG L5274-5283].
- BFCL miss_func / miss_param / long_context as judged cells (REFUSED; checker-built rows only) [PROG L6988-6989].
- TRACE-VERIFIER-ARMS (plan C5, ~9,900 cce): the ladder already orders CHECKER > CACHED_SOLVE > NONE across corpora
  [plan 2026-09-17 L236-238]; a same-corpus measurement changes one qualifier; not this cycle.
- IFEVAL-CHECKER-OUTPUT (plan C3, 2,400 calls, 162 questions): superseded by R6, which buys the same rung on an agentic
  artefact with a real roster at the same price band; the author may keep it as a second checker-shaped rung.
- Rubric lines, rubric-shaped references, the rubric-free continual recipe (a prompt-hash change is a new judge) [CTX §5;
  plan 2026-09-17 L214-216].

## 4. Two-week order (the night schedule's lanes: 1 compute unattended, 2 registrar, 3 builders in worktrees, 4 reviewer, 5 network / ingest)

Week 1 (2026-09-19 to 09-25)
- Day 1. Lane 2: registrar files R1 A8, R3 UNION-PROFILE-HOME, R4 AGREE-ORDER, R2 K-SELECTION (the construction change with
  its rebuild arms), R11 LEAF-INTERACTION, each at the END of the programme, closed-lines check on each; R5 PLACEMENT-STEPS
  and R6 BFCL-JUDGED-PILOT registered as text, not run (R6 blank where the cap and the agent list are the author's).
  Lane 3: engine-coder builds R1 / R3 / R4 / R11 scripts (--dry-run, selftest) and the R2 engine flag (inert when absent,
  fail-closed key, tests). Lane 4: reviewer READY on each at zero calls; MERGEABLE on the R2 branch.
- Day 2. Research-lead merges MERGEABLE branches; full suite in the main checkout; Block 2 dry-runs. Lane 1: run-operator
  runs R1, R3, R4, R11 --run serially in a no-construction window; reviewer recomputes; registrar outcomes.
- Day 3-4. Lane 1: R2's three rebuilds + nulls (~2 h, serial, nothing reads the pool); readout; reviewer; registrar
  outcome + REDRAW C3 bracket. Lane 5: R7 Multi-SWE download + ingest + admission pilot (network only), reviewer.
- Day 5. Ledger patch (one version), synthesis; science-writer drafts the §1 spine as thesis text from the rows.
- Day 6 (2026-09-22). Lane 1: R8 canary pass 2 (600 calls), --analyze, reviewer, registrar: the floor is recorded.
Week 2 (2026-09-26 to 10-02), after the author's answers to §5
- R5 PLACEMENT-STEPS: dry-run, 12-match pilot, run (800 calls), reviewer, registrar; FW L15 / L189 / L211 brackets.
- R6 BFCL: cap declared -> item-19 probe (50 calls) -> pilot (12 matches) -> run (<= 3,200 calls) -> reviewer -> registrar.
- R9 ARM-B (~2,000 cce) if the go is given; R10 if the author generates.
- Lane 2 in parallel: the R7 outcome, and the registration of the first Multi-SWE judged pass priced at the FW rate.
Total bill of the judged items: R8 600 + R5 800 + R6 3,250 = 4,650 calls on ~2,325 matches, plus R9 ~2,000 cce of
reasoning solves = ~6,650 cce. No single run crosses the 4,000-match rule; the sum is under the ~8k-call spirit of it;
the go is asked for the block by precedent, and separately for R9 (a second vintage) and R6 (the cap and the roster).

## 5. Decisions taken by precedent, and the questions only the author can answer

Decisions I took (reversible at registration): R1 named on the CLEAN tree R1 af_clean_s42 with the quantitative remainder
as a complement, not a site; R2 registered in the hysteresis form at 1.05 x bar, geometric only (the "take the certified
k" variant is refused by FW L53); R3 as a readout that settles the home question with a number rather than a choice; R4
with the deviation-residue leg registered expecting UNDETERMINED; R5 priced at 100 matches per separable tier; R6 sized
at the base stratum only, with the grok contestant read separately; C3 IFEval and C5 TRACE-VERIFIER dropped for this
cycle; B2 / B3 parked behind R2; the judged order R8 > R5 > R6 > R9; the go asked for the block.

Questions only the author can answer:
1. BFCL: the per-episode artefact cap in tokens (chars/4 median 453, p95 2,422, max 7,199 [PROG L7007]); the agent list
   (the 8 ingested; Llama-3.3-70B terminated 0.657; grok-4-1-fast-reasoning-FC as a contestant of the grok judge); the
   .gitignore call on experiment_results/agent (374 MB untracked, never git add -A) [PROG L7003-7007].
2. Does the anchor-free line continue past R1 / R2 (R7's tree, EMBED-AF, ARRIVAL-AF), or is the spine its last word?
3. Is the profile's home the union strata (R3 decides on a number) or the 14 anchors with the union as the routing
   appendix? The paper leads with one.
4. The judged block go (R5 + R6 + R9 = ~6,050 cce beyond the registered canary), or a subset.
5. MODEL-VINTAGE-CANARY pass 1: generate (~0.8M output tokens, the 7 open checkpoints hosted or rented) or defer.
6. Multi-SWE-bench_trajs: download and normalise now (R7, a day of builder time), or keep "agents" at BFCL description +
   one calibration sentence for this cycle.
7. The TRAIN-ONLY invariant of the trees of record (37 / 427 / 2,437 EVAL texts [FW L229]): acknowledge-and-disclose or
   rebuild; every routed-only row moves on rebuild.
8. Whether the thesis title's "for Agents" bridge is carried by R6's one sentence or stays motivation-not-deliverable.
