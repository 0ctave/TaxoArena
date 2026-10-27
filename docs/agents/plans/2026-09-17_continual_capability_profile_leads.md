# Continual capability profile: the honest object and the leads (research-lead synthesis, 2026-09-17)

Read-only synthesis pass over five lens reports (scratchpad/leads/: arena_profile.md, judge_continual.md, cells.md,
data_economics.md, refuter.md), CONTEXT.md, ledger v112 (HEAD 4f7ab20), the programme (5,333 lines) and FRAMEWORK.md.
Zero calls, zero builds, no edits under docs/ or experiment_results/ except this file. Numbers were spot-checked against
the ledger row or programme line named beside them; where a lens and the record disagree it is said so.
Citation form: [LEDGER id]; [PROG Lnnnn]; [FW Lnnn]; [lens file §].

State on disk at writing (verified by command; cells.md §0 confirmed): ANCHOR-FREE-REDRAW registered [PROG L4627] and
half-run: R1 af_clean_s42 built (leaves 82, train 8,230 / test 3,770, pool p2dca21ab5f4ef3ae, CERTIFIED true), its site
null started 20:14:16 and produced nothing (sitenull_af_clean_s42.out 0 bytes, no CSV); R1c, R2, R3, R4 not started;
only the Gradle daemon (PID 40328) alive. Canary pass 2 refused before 2026-09-22 [LEDGER CANARY-BASELINE].

## 1. The honest object

What the framework can promise today, in the author's four words, with the refuter's minimal object as the floor and
the arena lens's atlas as the ceiling. Floor [refuter.md §2]: for a corpus with a key or a checker, a (model x anchor)
verification-fidelity table over the corpus's own pinned categories with question-bootstrap intervals, a certified
partial order per anchor at 0.975 labelled "calibration UNDETERMINED", and a band (above / below / unseparated) per
model, for the roster and the one frozen judge it was fitted on, the frontier as one unordered band, nothing below the
anchor, no preference or agent-process claim, no drift statement until the canary's second pass. Ceiling
[arena_profile.md §1.6]: the same, published as an atlas: per model, a key-built row per keyed anchor (R 0.9135 at
~201 q/cell [LEDGER PROFILE-RELIABILITY]), a judge-built theta/SD_cell row per unkeyed anchor with the anchor's own
class (merged board: PASS Physics 0.9148, Math 0.8833; PASS-WITH-INTERVAL Law, Psychology, Business, Chemistry,
Philosophy, Other, History 0.71-0.79; FAIL Engineering, Biology, CS, Economics, Health, published PREDICTIVE-ONLY
[LEDGER PROFILE-INTERVAL-ALL C2]), wrong(established) beside every ORDERED count (per-anchor 1,714 / 4(4) at the
record's seed, 4-5 over 11 seeds; pooled 150 / 0(0) [LEDGER KTD-CHECK]), the tier map [9, 9, 2] and the undominated set
of six [FW L119, L131], and, once Lead A1 lands, the list of anchors on which the model's deviation from its own global
standing is certified. The four words, each with the wording the record supports:
- "capability" -> verification fidelity. Every number is agreement with a key, a checker or a possibly wrong reference
  [CTX §1]; on unkeyed cells the judge transcribes the reference (REF +2.177 vs KEY +0.788, 2.7:1 upper bound
  [LEDGER CONSENSUS-FIT]) and 72-79% of a cell's difficulty contrast is the reference's [LEDGER TOPIC-DIFFICULTY].
  The row an unkeyed cell can carry is "agreement with reference vintage v at fidelity f, class BANDED-JUDGED".
- "profile" -> an anchor-level atlas with certified deviations. Sub-anchor rows are closed twice (PROFILE-TREE-ROBUST,
  KEY-SUBANCHOR-SCALE; no cell size reopens them [CTX §5]); the judge-built board-level R is 0.7183 [0.6076, 0.8291]
  and rests on Physics and Math [LEDGER ANCHOR-PROFILE-INTERVAL; FW L117]; on MMLU-Pro the atlas routes nothing (gemini
  best in 14/14 [LEDGER ROUTER-REGRET-MMLU]). The deviation term delta_ac has never been published with its own
  certificate; that is the one statement that would make the atlas a profile rather than a re-indexed global score.
- "continually" -> repeatable, not yet monitored. Measured: the frozen recipe, provenance on every row since
  2026-09-16, the 5.7% test-retest floor on contested prompts [LEDGER DECOMP], the re-draw fragility of b1 (4.47 vs 2.26
  against 3.84 on ~26 events [PROG L4259-4267]). Waiting: the canary floor (pass 2 on/after 2026-09-22), the reference
  vintage (3,432 solves, one vintage, no stamps; arm B never run [FW L37]), model drift (no test at all).
- "agents" -> zero rows. No trajectory, tool log or process checker exists in the record (refuter's grep 0/0/0;
  FW L269). The only transferable law is the reference ladder: CHECKER_OUTPUT 0.958 / 0.993 on terminated MATH traces
  [PROG L3996-3997] > CACHED_SOLVE 0.849-0.865 [LEDGER STACK-v2, GROK-CALIB] > NONE 0.738 [LEDGER PAIR-NOREF] >
  SPECIFICATION 0.658 with 25.6% ties [LEDGER GEN-ARENA] (different corpora; the ordering, not the gaps, is the law).

One record correction to file (registrar, by insertion, no calls): FRAMEWORK L160 and L258 still read "per-anchor
certifiability is unmeasured"; PROFILE-INTERVAL-ALL C2 delivered it on MMLU-Pro. What remains unmeasured is the
reliability of the 52 union strata [FW L258; multi_corpus_design.md L251]. The refuter's floor inherited the stale line.

## 2. The leads, deduplicated and ranked by value per call

Common hygiene on every lead: registration before code; caches mode=ro; denominators named; both conventions;
wrong(established); predictions scored HELD / FAILED; UNDETERMINED is an outcome; nothing concurrent with a construction;
no analysis reads the pool while a build or site null runs (rule 7). Closed lines no lead may touch [CTX §5]: rubric
text at any granularity, rubric-shaped references, ensembles / gating / confidence / two references, sub-anchor
profiles, the frontier order, escalation, temperature, single or selective order, construction levers for
certification (ANCHOR-FREE-CERT), dual-cell judging (BOUNDARY-DISAGREEMENT), the Kimi reference line.

### Tier A: zero calls, zero builds (ranked)

A1. PROFILE-DEVIATION-CERT [arena L1]. Claim: the (model, anchor) deviation term delta_ac carries certifiable content
    beyond the global theta. Instrument: merged-board draw matrix (x20_merged.py, B >= 2,000 question-clustered);
    |delta_ac| / SD >= the scale-consistent per-anchor critical value from MAXT-MULTIPLICITY (raw-z or widened-q, never
    the hybrid); key comparator on the 46-model key by McNemar against the pool mean; variance share of delta vs theta;
    wrong(established) where a judge-certified deviation has the opposite key sign. If it holds the profile may say
    "m is certified above/below its own standing in anchor c", the first sentence that is a profile. Prediction: key
    < 30% of cells certified, judge < 15%, concentrated in Physics/Math/Law; wrong-key-sign 0-2. Falsifier: judge-
    certified deviations with the wrong key sign > 5% of those certified. Cost 0 calls, ~1 CPU-hour. Hazards: prior
    shrinkage 1.23-1.82x per anchor [LEDGER K-RECONCILE (3)]; routing attenuation ~20% [LEDGER ROUTING-ATTENUATION];
    FAIL anchors stay PREDICTIVE-ONLY whatever the deviation test says. Owner: arena-specialist designs, engine-coder
    builds, reviewer recomputes.
A2. PROFILE-INTERVAL-ALL-UNION [refuter §3.1; cells §5 "belongs to the arena specialist"]. Claim: the 52 (source,
    domain) union strata, the only cells with a routing consequence (+3.38pp clean [LEDGER MC-E2E]), carry a key-built [ID-ONLY 2026-09-23 (CLAIMS-SWEEP-BRACKETS, registrar): pool union paeec37aa28063c75; verified by id only, not by content; reviewed twins on this pool (reviews 1df2cf1, 8ebfa7a): 471 ids / 427 texts exact, 478 / 432 norm-v1 (GPQA 288, MMLU-Pro 185, MATH 3, BBH 2); see docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT) and L14455-L14487 (SPLIT-FOLLOWUPS).]
    profile row. Instrument: profile_reliability.py's split-half estimator with jackknife interval and halving SD on
    the union key rows (multicorpus_cache_v1.db, 18 models, pool paeec37aa28063c75 pinned by id), per stratum and
    board-level. Lets the profile grow from 14 cells to up to 66, each with a class. Prediction: MMLU-Pro-source strata
    PASS, MATH/GPQA/MuSR/IFEval strata mostly FAIL by support (1,324 / 1,192 / 756 / 541 q). Falsifier: none needed; the
    test only adds or marks rows. Cost 0. Hazards: the 18-model roster is not the 46 (reliability is roster-dependent);
    text-keyed ground_truth_category is shared across corpora (use MAIN_union_routing*.csv, never the generic centroid
    CSV); two 6,482-row pools coexist, pin by id [data_economics.md steward hazards].
A3. ITEM-26-POOLED + RE-JUDGE-RULE (one registration; merges arena L3 B1-POOLED-DRAWS, judge Lead 1, refuter §3.3).
    Claim: pooling the established labels of the two draws of the same judge on the same bytes (GROK-CALIB Python,
    Kotlin c0d3f708cbc3930e; 9,123 shared matches, ~52 events) identifies b1. Instrument: systematic_budget's
    established-label refit with a draw indicator as a scale term, bootstrap clustered by question, delta-deviance vs
    b1 = 0 at 3.84, both single-draw values printed beside, and a power statement (P(true b1 = +2.7 clears 3.84) at 26
    and 52 events). Lets the profile say whether ORDERED-JUDGED exists for the shipped judge on evidence rather than on
    a draw. Prediction: pooled delta-deviance 3.5-5.5, identified; LOAO wrong 2-4 (1-2 established), nominal ~2.2,
    status UNDETERMINED. Falsifier: pooled delta-deviance < 2.5 (every grok cell is BANDED-JUDGED). In the same commit,
    a plan amendment stating the re-judge triggers the record supports: judge fingerprint change; reference vintage
    change on a question; canary alarm. Not a trigger: tree re-celling (verdicts depend on the tree only through the
    anchor rubric, +0.2pp discrimination [LEDGER STACK-NORUBRIC]) PROVIDED the anchor-rubric bytes are held fixed (a
    regenerated rubric is a prompt-hash change, guard 11); not a trigger: provider re-draw (whole-board agreement inside
    1.9pp [PROG L4246-4248]). Every re-judge read on identical matches, both conventions, question-clustered CI. Cost 0.
A4. REF-QUALITY-MONITOR [judge Lead 2], with DIFFICULTY-PROXY-WIDENER [arena L9] folded in as a secondary readout.
    Claim: per-cell reference-correct rate on keyed audit mass is the continual per-cell quality signal. Instrument:
    on x12, GROK-CALIB, Kotlin and x20, per (anchor, cache) reference-correct rate vs accuracy A and B; then the
    key-free plurality proxy (Spearman 0.785 with difficulty [LEDGER TOPIC-DIFFICULTY]) as a LOAO widener covariate
    beside A, wrong(established) at matched utility, with an identification profile. Criteria: Spearman(ref-correct,
    A) across 14 x 4 >= 0.8; proxy leg registered expecting UNDETERMINED (26-40 events; b1 alone is re-draw fragile).
    Falsifier: Spearman < 0.5. Cost 0. Hazards: the proxy is consensus-shaped (DECOMP's leakage object); it monitors,
    it never gates (gating closed). Not a new signal of reference accuracy at inference (withdrawn in SYSTEMATIC-BUDGET (a)).
A5. PER-ANCHOR BAND ATLAS [arena L2]. Not a test; the deliverable artefact. Per (model, anchor): band, anchor class
    from PROFILE-INTERVAL-ALL C2, key-built row beside, wrong(established), denominators, the 11-seed residue band (the
    Law arx_0314 vs claude-3-5-sonnet edge sits 2.7e-5 under the cutoff [LEDGER KTD-CHECK]), the two newcomers'
    PROVISIONAL rows single-source only. Mistral board and the Kotlin grok board as two atlases, never merged (guard
    on mixed fits). Cost 0. Owner: arena-specialist, then science-writer.
A6. PLACEMENT-CEILING [arena L5]. Claim: the newcomer band (7 and 3 key tiers at 400 matches [LEDGER
    NEWCOMER-PLACEMENT-LIVE]) is a key-tie band, not a budget band. Instrument: newcomer_placement.db single source;
    band width decomposed into positions inside a key-tie cluster (0.017 gap), inside the frontier band, and positions
    the arena could have separated at nominal power; subsample 100/200/300 of the bought 400 for the resolution curve.
    Decides whether C6 is worth its calls. Prediction: sonnet's width entirely frontier + key-tie; gpt-4o-mini's 3
    tiers = the 0.631/0.629/0.628 cluster plus one each side; budget narrows at most 1 tier. Cost 0.
A7. CAP-PRUNE [cells L4]. Claim: a capability rule that survives as a held-out-replicating PRUNE keeps only the trunk.
    Instrument: cap_gate_posthoc.py's per-site LOMO gains; keep a site iff gain > its own within-site null p95 on the
    train side AND > 0 on the tree's held-out side minus p2dca (2,193 q); the script must write the null and held-out
    columns CAP-GATE left in scratch [PROG L5117]. Falsifier: survivors <= 4 closes the capability-gated construction
    line at zero builds. Prediction: 4-6 survivors, Jaccard with the certified 16 ~0.25. Cost 0. Never a gate [FW L53].
A8. STABLE-CELL-SET readout [cells L2] (after B1). Object: record sites reproducing at Jaccard >= 0.5 in R1, R2, R3,
    read as a partition against the 14 anchors, view A, the 2-cell trunk and the 81 leaves with anchor_free_readout.py.
    Criteria: every stable cell >= 120 held-out q on the pool of record; key R >= 0.70; F6 >= the 14 categories' +10.79.
    Prediction: 5-8 cells, key R 0.85-0.92, F6 +8 to +11, i.e. the third criterion FAILS and the stable set's only claim
    is "available without labels". Cost 0 after B1. R2/R3 contribute identity only (~70% in-sample on the pool).
A9. MODEL-VINTAGE-CANARY definition [judge Lead 3]. A registered definition, not yet a measurement: model drift =
    answer-content drift on the 279 canary questions; per-model agreement with the cached vintage; alarm below the
    REF-SC null (0.94 - 3 SE); a model below the alarm is a new vintage, never pooled. The null must first be read on a
    fixed checkpoint (two generations); contestant temperature recorded (the TEMP-0 analogue). Judge cost 0; contestant
    generation cost is the author's (no arena calls).
A10. AGENT-CORPUS-ADMISSION rule set [judge Lead 7; data_economics.md agent requirements]. A registered rule set, §3
    below. Cost 0. Prediction: the first agent corpus fails on termination the way MATH did (12-19% cap-hit rows) and its
    judged cells are PREDICTIVE-ONLY on day one.
A11. PROFILE-R-FILTERED [arena L4]. Claim: the anchor profile's reliability survives the answer-disagreement filter that
    halves the newcomer bill (FRAMEWORK L405 names it untested). Instrument: PROFILE-INTERVAL-ALL's estimator on the
    merged board restricted to disagreeing matches, q_distinct printed per anchor. Hazards: the filtered theta scale
    is 13% wider; compare R only [LEDGER PLACEBO-ENTRY]. Cost 0. Ranked here because its value is a bill, not a claim.
A12. FOREIGN-GATE re-specification [cells L7]. Fix the two under-specifications (reference = host anchor name; purity =
    own train-side purity - 2 SD) and re-score FOREIGN-GATE-D4 on the D4 artefacts. The only novelty instrument the
    design has. Cost 0. Lowest in this tier because no arrival exists to gate until B3.

### Tier B: builds only (0 calls; one construction at a time; nothing reads the pool meanwhile)

B1. Finish ANCHOR-FREE-REDRAW [cells L1; refuter honourable mention]. Registered [PROG L4627-4782]. Restart R1's null
    from snapshot 20260917_201353_Headless_Run_Auto_ge, then R1c, R2, R3, R4 serially (4 builds x 2-4 min + 5 nulls
    x ~30 min, ~3 h). All five run regardless; an arm whose null does not reach 300 reps is UNDETERMINED. Decides
    which anchor-free claims are recipe properties (prediction: trunk axis and depth-1 certification) and which are
    seed-42 properties (root certification, fringe count); C5 predicts a re-draw-stable set of 5-8 sites, all n >= 560.
    Prerequisite of A8, B2, B3. Owner: run-operator; reviewer recomputes counts from the CSVs; registrar scores C1-C6.
    [OUTCOME 2026-09-18 by ANCHOR-FREE-REDRAW (programme §ANCHOR-FREE-REDRAW; ledger v114): C1 5/5, C2 4/4, C3 depth-1 FAILED (3/4: the quantitative site on the clean split accepted k=2 at the bar and is uncertified), C3 root HELD 4/4 (the prediction "root is a seed-42 property" FAILED: margin 1.12-1.14 on every draw), C4 FAILED (R3 15.2%), C5 HELD (7 / 8 / 8 / 16), C6 FAILED 14 vs 11 and F4 FIRED: "anchors cost certification" (§1 of the cells lead) is withdrawn as a headline. Re-draw-stable certified set = 5 sites, root + the discursive spine (n00000001, n00000005, n00000017, n00000016, n00000032), min n 629, the quantitative side 0. A8 STABLE-CELL-SET may now be registered on that set; whether the anchor-free line continues is the author's question (§5).]
B2. EMBED-AF [cells L5] (1 build + 1 null, ~35 min; nomic cache on disk). Claim: the free trunk's axis is corpus-level,
    not embedder-level. Own site null on nomic's geometry (the bar is per geometry, D1-D3). Prediction: root k = 2 on
    the same axis; certified count differs by > 5; Philosophy forms its own region. Register UNDETERMINED for "does not
    build". Only if REDRAW's C2 holds.
B3. ARRIVAL-AF [cells L3] (2 builds + 2 nulls, ~1.5 h). Claim: a newcomer question mass forms a persistent cell when
    the root can split, and incumbents persist. Arms: R1 with Law withheld from TRAIN (may need an excludeFromTrain
    key: engine-coder, fail-closed, inert when absent) vs R1. ARRIVES iff a certified >= 60%-Law site exists and >= 50%
    of held-out Law routes to it; PERSISTS iff >= 80% of the control's certified sites reproduce at Jaccard >= 0.5.
    Prediction: Law forms the region, certification a coin flip at 0.97x p95; incumbents persist on the quantitative
    side. The only clean-hygiene test of "new mass becomes a cell without an anchor" in reach.
Not now: FED-AF-UNION [cells L6] (predicted to change nothing the router consumes); EPOCH re-growth with new questions
(no new questions exist; [cells L8]).

### Tier C: judged (calls; the 4,000-match rule is per run, ~8k calls)

C1. CANARY-BASELINE pass 2 [all five lenses]. 600 calls, registered, on/after 2026-09-22; no go needed. The first
    "continual" sentence: the deployed judge's retest floor (prediction 4-6% contested, lower cross-tier). MDE ~2.7pp
    at n = 300 [FW L141]; a 2pp drift is invisible in one epoch.
C2. ARM-B-VINTAGE [judge Lead 4; refuter §3.2]. 200 frozen pool questions re-solved by grok-4-1-fast-reasoning under
    the JSON answer-only protocol, ~2,000 cce (reasoning solves, not arena matches; under the rule, but it creates a
    second reference vintage, so the author's go is asked anyway). Criterion: agreement >= 0.89 (REF-SC null 0.94);
    < 0.89 -> re-mint the discriminating subset before any further judged spend; vintages never pooled. Prediction
    0.92-0.95; falsifier < 0.85. Stamps the legacy vintage for the first time. The reference is the larger half of the
    instrument (2.7:1), so this is the drift that matters.
C3. IFEVAL-CHECKER-OUTPUT [arena L7; data_economics L2]. 1,200 GEN-ARENA IFEval matches re-judged with the checker's
    per-constraint pass VECTOR (checker_answers_v2 backfill) as the reference block instead of the constraint list;
    paired same-match contrast. 2,400 calls, under the rule. Lets the profile say whether a constraint-shaped,
    agent-adjacent cell can carry a judge-built row at the 0.75 bar under both conventions. Prediction: A rises from
    0.658 to 0.80-0.88, ties fall below 0.15. Falsifier: A < 0.75 (agent cells are checker-only; the "and agents" half
    reduces to checker-built rows). Hazards: 162 eval questions, bottom of the support rule; the prompt must present
    what each answer PASSED, never a checklist of criteria (REF-CHECKLIST closed).
C4. TRACE-TRUNCATION [judge Lead 5]. causal_length.py's three arms on ~360 cap-free MATH pairs with the checker
    output as reference: ~2,160 calls, under the rule. Decides whether a judge holding an exact outcome reference is
    an outcome judge or still a reasoning-content judge. Prediction: truncation drop < 0.10 (original ~0.95, truncate
    >= 0.85), pad null. Falsifier: truncate < 0.70, i.e. no trajectory pair with equal outcomes is judgeable without a
    length control. H7's "ignore length" clause stays closed.
C5. TRACE-VERIFIER-ARMS [judge Lead 6]. The framework's unmeasured >= +5pp verifier gain on trace-shaped tasks
    [FW L269]: NONE and CACHED_SOLVE arms on a 1,500-match stratified subset of STAGE3-MATH-CAPFREE plus a 53-match
    byte-identical control = 3,053 matches, ~6,100 calls plus ~383 reasoning solves (~3,800 cce). Under the per-run
    rule at this size; the full-arm version (5,992 matches) needs the author's go. Prediction: NONE 0.80-0.86,
    CACHED_SOLVE 0.90-0.94, CHECKER 0.958; gain HELD at +10 to +15pp. Falsifier: CHECKER - NONE < +3pp. The CHECKER
    arm is ORACLE-shaped on MATH (the target is the key); the gain is an upper bound on what a deployed checker buys.
C6. PLACEMENT-CURVE [arena L8], conditional on A6 showing budget can narrow the band. 2 newcomers x 800 matches x 2
    orders = 3,200 calls, both stages' match counts fixed before launch (guard 13). Falsifier: the band does not narrow
    at 1,200 matches (placement is key-tie-bound; 800 cce is the whole placement budget forever).
C7. Code-with-tests corpus admission, then its edge pass [data_economics L1]. Reference cost 0 (the test runner is the
    checker). Bill at the FRAMEWORK rate: 1,530 matches per cell per epoch [FW L219], so any corpus with >= 3 judged
    cells crosses the 4,000-match rule and needs the author's go; the board itself is checker-built at 0 calls, judge
    calls buy calibration and a canary only. Not priceable until the author names the corpus (§5).

### Disagreements between the lenses and my call

- Cells lens ("leaves are dead as profile rows; the anchors are the ceiling; finish REDRAW first") vs arena lens
  ("PROFILE-DEVIATION-CERT first"). No conflict on the object: A1 is at the anchor. On order: A1 first, because it
  changes what the profile SAYS today; B1 is three hours of machine time that runs in a window nobody reads the pool,
  and its outcome changes only the anchor-free line, which is not arena-bound [CTX §3].
- Judge lens ("re-celling is not a re-judge trigger") vs cells lens ("re-growth re-cells; the sub-anchor residual is
  zero"). Both hold: verdicts are cell-independent, fits are not, and the row is the anchor. My call is the judge
  lens's rule with one clause added: only while the anchor-rubric bytes are held fixed (guard 11).
- Arena lens (IFEval checker-output first toward agents) vs judge lens (TRACE-TRUNCATION is "the one number") vs data
  lens (a code-with-tests corpus first). Order: C3, then C4, then C5, then C7; C3 and C4 use data on disk and each is
  under the rule; C7 waits on A10 and the author's corpus.
- Refuter (per-anchor certifiability unmeasured) vs ledger (PROFILE-INTERVAL-ALL C2 delivered). The ledger wins; the
  FRAMEWORK lines get a bracket.
- Judge lens Lead 8 (rubric-free continual recipe as a plan amendment) is declined for now: dropping the rubric changes
  the prompt hash, which makes the recipe a new judge for the certificate (~2,100 + ~20,000 cce [FW L193]); the
  numbers it would cite (STACK-NORUBRIC +1.5pp decisiveness, +0.2pp discrimination) are already on record.

## 3. The agent question

Schema an agent-trajectory corpus must carry to enter the pipeline as-is [data_economics.md agent requirements;
judge_continual.md Lead 7]:
(a) stem + content_key for the per-item split (SplitSide norm-v1); family_id write-once for templated tasks so a
    family sits on one side; a pool id exported as a file; the TRAIN-ONLY tree state asserted per row.
(b) an OUTCOME CHECKER table emitting a normalised output per (task, agent): pass/fail vector or final-state diff;
    checker table sha; D_c (decidable share) >= 0.95 per cell or the cell is PREDICTIVE-ONLY; a consistent termination
    proxy versioned like checker_answers_v2 (the MATH lesson: D_c 0.9840 vs 0.6701 under two readings of one table).
(c) finish_reason and completion_tokens per step and per episode (rule 10); a cap-hit episode is NON_TERMINATED, a
    class, never a verdict, never a tie; the admitted-population denominator printed on every row.
(d) the tool log + final state as the judged artefact with a stated per-step and per-episode cap; per agent: deployment
    fingerprint, provider, response id, tokens, latency.
(e) a designed (source, domain) stratum per task, because routing value lives at the family layer (+3.38pp clean
    [LEDGER MC-E2E]; leaves lose to domains as a router [LEDGER MC-LEAF]).
Any artefact induced over EVAL trajectories is contamination (the p8a29/p2dca incident recurred at ~70% in the
multi-corpus line; the per-item hash split is the fix).

Reference ladder, as measured: CHECKER_OUTPUT (0.958 / 0.993, terminated MATH traces, 16.5% of pairs excluded by the
cap [PROG L3996-4014]) > CACHED_SOLVE (0.849-0.865 on MMLU-Pro, 2.7:1 reference-following) > NONE (0.738, ties 0.177)
> SPECIFICATION (0.658, ties 0.256, flips 0.38 on IFEval). Rule that transfers unchanged [FW L37]: give the judge the
checker's OUTPUT, never its specification; a specification-shaped reference is not a rung, it is refused. A reasoning
model's own trajectory is CACHED_SOLVE, admissible only after C5 sizes it and after a REF-QUAL pass under one recorded
protocol with a trajectory leakage audit that does not yet exist (the n-gram audit has no trajectory analogue).

What "agent capability" would be measured AS: per task family (anchor) with an outcome checker, the agent's checker-
built accuracy row with a question-bootstrap interval on terminated episodes, at 0 judge calls; the judge's verification
fidelity on the same cells as a calibration board and a canary (expected UNDETERMINED, as STAGE3-MATH-CAPFREE was); a
band per agent; the undominated set per family. No per-trajectory rank, no "better process" claim (a preference claim,
refused by rule), no row below the family. Where no checker exists, reference_state is NONE and there is no fidelity
object; the framework refuses the number. An agent whose episodes often hit the cap gets a profile of its short episodes.

Admission rule before any spend (A10, registered as text): (a)-(e) above verified by command; a per-model max_tokens
probe on the trace-shaped prompt (item 19, 50 calls per judge) before any pilot, because two trajectories plus a
reference must fit under the 8192 cap; the judge-vendor affinity check if any agent shares the judge's vendor
[FW L260]; a first pilot at <= 4,000 matches; C3 and C4 read before the first agent edge pass, because their falsifiers
(a pass vector does not lift IFEval; truncation still moves the verdict under an exact reference) each make the judged
half of an agent row unreachable with the deployed recipe.

## 4. Proposed order

Two weeks at zero calls (the one exception is C1, already registered):
Week 1
- Day 1 morning: registrar files A1, A2, A3 (with the re-judge amendment), A4, A6 as one registration batch, each its
  own section at the END of the programme, plus the FRAMEWORK L160/L258 bracket; closed-lines check on each.
- Day 1 afternoon/evening: run-operator relaunches the REDRAW chain (B1) from R1's snapshot, then R1c, R2, R3, R4
  serially; nothing reads the pool for ~3 h; back up experiment_results/anchorfree first.
- Day 2-3: engine-coder (worktree) builds profile_deviation_cert.py, item26_pooled.py, profile_interval_union.py, each
  with --dry-run and a self-test; reviewer READY at zero calls; run-operator runs them; reviewer recomputes every number;
  registrar writes outcomes and ledger rows. Merges are mine after MERGEABLE, then the full suite, then the Block 2
  dry-runs.
- Day 3-4: reviewer recomputes REDRAW's certified counts from the CSVs; registrar scores C1-C6; I write the REDRAW
  synthesis (continue or stop the anchor-free line: author's question, §5).
- Day 4-5: A5 band atlas (arena-specialist, then science-writer); A6 PLACEMENT-CEILING; A4 REF-QUALITY-MONITOR.
- Day 6 (2026-09-22): run-operator runs canary pass 2 (C1, 600 calls); reviewer; registrar; the floor is recorded.
Week 2
- A8 STABLE-CELL-SET (if REDRAW's C5 held), A7 CAP-PRUNE, A11 PROFILE-R-FILTERED, A12 FOREIGN-GATE re-spec.
- B2 EMBED-AF (only if C2 held) and B3 ARRIVAL-AF, one at a time, each in its own no-pool-readers window.
- A9 MODEL-VINTAGE-CANARY definition and A10 AGENT-CORPUS-ADMISSION as registrar text from my briefs.
- Registrations for C2, C3, C4 written (not run) so the judged block can start the day the author says go.

Judged spend after the author's go (in order; each with dry-run, 12-match pilot under the truncation guard, run,
analysis, reviewer, registrar): C3 IFEVAL-CHECKER-OUTPUT 2,400 calls; C2 ARM-B-VINTAGE ~2,000 cce; C4 TRACE-TRUNCATION
~2,160 calls; C5 TRACE-VERIFIER-ARMS ~6,100 calls + ~3,800 cce of solves; C6 PLACEMENT-CURVE 3,200 calls only if A6
says budget can narrow. Total bill: 600 (C1, registered) + 2,400 + 2,000 + 2,160 + 9,900 + 3,200 = ~20,300 cce, of
which ~14,500 are judge calls on ~7,200 arena matches summed over five runs (600 + 2,400 + 2,160 + 6,100 + 3,200). No single run at these sizes crosses the
4,000-match rule; the sum does cross the ~8k-call spirit of it, so the go is asked for the block, not per run. C7 is
unpriced until the corpus is named and crosses the rule at >= 3 cells.

## 5. Decisions that were the author's, and the questions only the author can answer

Decisions I took (by precedent, reversible at registration):
- A1 ranked above B1; both zero-call, A1 changes the published object, B1 changes a structural line.
- Arena L3, judge Lead 1 and refuter §3.3 merged into one registration (A3), with the re-judge rule as a plan
  amendment in the same commit and the anchor-rubric-bytes clause added.
- Arena L9 folded into A4 as a secondary readout registered expecting UNDETERMINED.
- The rubric-free recipe (judge Lead 8) declined: a prompt-hash change is a new judge for the certificate.
- FED-AF-UNION and epoch re-growth not scheduled.
- C5 sized at 1,500 matches per arm (under the rule); the full-arm version left to the author.
- C6 made conditional on A6.
- The judged order C3 > C2 > C4 > C5 > C6; C7 last and unpriced.
- The wording of §1 (verification fidelity; anchor-level atlas with certified deviations; repeatable not monitored;
  zero agent rows with the reference ladder as the only law).

Questions only the author can answer:
1. Which corpora. Is there an agent corpus with an outcome checker the author wants ingested (code-with-tests: which
   benchmark, which harness, which test runner), or does "agents" stay motivation-not-deliverable for this cycle?
   Without a named corpus C7 cannot be priced and A10 is the whole agent deliverable.
2. Which budget. A go for the judged block (~14,500 judge calls / ~7,200 matches over five runs; ~20,300 cce with solves),
   or a subset; and separately whether the full-arm C5 (5,992 matches) is wanted.
3. Whether the anchor-free line continues after REDRAW: if C2/C3/C5 hold, B2 and B3 are the next builds (~2 h); if
   F1 or F2 fires, the line is one-draw structural evidence and B2/B3 are dropped; either way the free tree is never
   arena-bound without a new registration.
4. The TRAIN-ONLY invariant of the trees of record (2,437 / 37 / 427 EVAL texts among members [FW L229]): acknowledge-
   and-disclose or rebuild. Every routed-only profile row moves on rebuild; the atlas (A5) prints whichever is chosen.
5. MULTI-OWNERSHIP as an attribution choice (a question contributing to two anchors' rows): open per BOUNDARY-
   DISAGREEMENT; it changes the denominator of every row it touches; needs the author's yes before registration.
6. Whether the 52 union strata are the profile's home for the paper (the only cells with a routing consequence) or
   MMLU-Pro's 14 anchors stay the object of record with the union as the routing appendix; A2 answers what the strata
   can carry, not which the paper leads with.
7. Whether the thesis title's "for Agents" bridge stands with zero agent rows after this cycle, or whether C3/C4's
   outcomes are the sentence that replaces it.
