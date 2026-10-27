# What the record supports as a CAPABILITY PROFILE at the arena/board level — and what it refuses

Research pass, read-only, 2026-09-17. Zero calls, zero builds, zero edits to docs/ or experiment_results/.
Read: docs/agents/CONTEXT.md; docs/test_ledger_distilled.html (v110 cut, 194 rows); docs/test_ledger.html v112
(rows named below); docs/judge_v2_program.md (NEWCOMER-PLACEMENT-LIVE L3852-3882, GROK-CALIB L3911-3944,
STAGE3-MATH-CAPFREE L3990-4018, JUDGE-WIRING-BOARD L4235-4271, CAP-GATE-POSTHOC L5026+, TOPIC-DIFFICULTY L5122+,
BOUNDARY-DISAGREEMENT L5227+); docs/design/FRAMEWORK.md (one-page L5-15, Stages 5-8 L81-135, Per-question L147-156,
Per-cell L158-171, Online operation L187-195, Budget L199-223, Guards L225-247, Limits L249-269, tests 1-26 L350-382).
Citation form: [LEDGER id] for a ledger row (last bracket wins), [FW Lnnn] for FRAMEWORK.md, [PROG Lnnn] for the
programme, [CTX] for CONTEXT.md.

Lens: the author wants a framework that judges models AND agents continually and returns a CAPABILITY PROFILE per
model/agent. This report asks what object the record can publish under that name today, at the board level, and where
the name is a claim the data cannot carry.

---

## 0. Data objects and denominators (named once, used throughout)

- Pool of record p2dca21ab5f4ef3ae: 3,445 judgeable questions [CTX §3]. Judged denominators: 2,811 (x12), 2,646
  (x20-judged); the merged board = x12 9,142 Mistral verdicts + x20 12,394 = 21,536 [CTX §3]. The x20 cache ALONE has
  zero verdicts on the 66 original pairs [CTX §4 rule 4; LEDGER TIER-HONEST-X20 bracket].
- Grok calibration board: 9,142 grok verdicts, Python draw (GROK-CALIB); Kotlin draw of the same judge on the same
  bytes: 9,123 matches, 9,106 valid verdicts, 2,801 judged questions [PROG L4236-4243].
- Edge populations: 891 key-gap-filtered x12 edges (809 established) vs 920 unfiltered (adopted denominator; 4 key-tied
  edges dropped inside build()) [LEDGER UNFILTERED-ADOPT]; merged per-anchor 2,538 edges; pooled 190 pairs (183
  established) [LEDGER KTD-CHECK, POOLED-RESTATE].
- Established = exact two-sided McNemar p < 0.05 on the anchor's JUDGED questions, integer arithmetic
  (systematic_budget.mcnemar_edge) [CTX §3]. Every wrong count below is wrong(established).
- Tiers: key tiers at the 0.017 gap; arena self-tiers by the adjacency reading-down rule [FW L119]. Conventions A
  (ties/INVALID/non-terminated wrong) and B (committed only) always both [CTX §3].

---

## 1. The profile object the record can publish TODAY

### 1.1 The row: (model x anchor), two provenances, never mixed

**Key-built row (keyed cells).** Accuracy with a question-bootstrap SE; pair directions by exact McNemar over the cell's
EVAL-side keyed questions; the key's tiers by the 0.017 adjacency rule; 0 judge calls [FW L115]. Reliability: split-half
Spearman-Brown, model-demeaned, 40 halvings: key anchor R 0.9135 at ~201 q/cell, 0.7143 at 50 q/cell
[LEDGER PROFILE-RELIABILITY]; on the merged 20-model board key 0.9045 at anchor [LEDGER PROFILE-RELIABILITY-X20].
On MMLU-Pro this is the profile; the judge is a diagnostic only [FW L9, L388].

**Judge-built row (unkeyed cells).** theta/SD_cell with its clustered SE and a Stage 6 class [FW L115]. Reliability of
the judge-built anchor profile:
- x12 (12 models, 9,142 verdicts): R 0.6728, LOAO jackknife [0.4932, 0.8524] — FAIL at the registered 0.70 bar as a
  point rule [LEDGER PROFILE-RELIABILITY, ANCHOR-PROFILE-INTERVAL].
- merged 20-model board (21,536 verdicts): R 0.7183 [0.6076, 0.8291] — PASS-WITH-INTERVAL; the margin over the bar is
  about one halving-SD (0.030) [LEDGER ANCHOR-PROFILE-INTERVAL; FW L117, L160]. It rests on Physics and Math: dropping
  either takes it below 0.70 [FW L117].
- The gain x12 -> merged decomposes into +0.093 [+0.020, +0.165] from new-pair verdicts through the joint fit and
  -0.047 [-0.084, -0.011] from adding eight profile rows [LEDGER ANCHOR-PROFILE-INTERVAL]. More models make the
  profile WORSE per row; more verdicts on the same questions make it better.

**Per-anchor certifiability (the profile as 14 rows, merged board, PROFILE-INTERVAL-ALL C2):** PASS Physics 0.9148,
Math 0.8833; PASS-WITH-INTERVAL Law 0.7923, Psychology 0.7882, Business 0.7701, Chemistry 0.7604, Philosophy 0.7334,
Other 0.7090, History 0.7063; FAIL Engineering 0.6866, Biology 0.3987, Computer science 0.3054, Economics 0.1431,
Health -0.0710 (2 / 7 / 5). On x12: 2 / 4 / 8. Key-20 rows on the smallest anchors (119-132 q) are 0.668 / 0.648 /
0.674 — "at 119-132 questions a per-anchor deviation row is not certifiable by the key either"
[LEDGER PROFILE-INTERVAL-ALL]. A judge-built FAIL anchor demotes its rows to PREDICTIVE-ONLY [FW L117].

So the honest judge-built profile on the board of record is: 2 anchors certifiable, 7 certifiable with an interval that
contains FAIL, 5 not certifiable. That is the object, per model, today.

### 1.2 The edge: classes, not ranks

Per (a, b, cell): c_raw from the question-clustered bootstrap; tau(A) = exp(b0 + b1 A) with A = the pair's answer
agreement; c~ = min(c_raw, Phi(|m| / sqrt(s^2 + tau^2))); call iff c~ >= 0.975 [FW L95; LEDGER SYSTEMATIC-BUDGET].
Composed with the key-tie decline where a key exists [FW L97]. Classes: ORDERED-KEY, ORDERED-JUDGED, KEY-CONTRADICTED,
BANDED, BANDED-JUDGED, DECLINED-KEY-TIE, NOT RESOLVED, PREDICTIVE-ONLY, EXHAUSTED, FOREIGN, PROVISIONAL, UNCHECKED
[FW L121].

wrong(established) on every board in reach, at 0.975:
- x12 Mistral, 891 edges: raw 739 / 8(4); widener 665 / 2(1); widener + decline 651 / 1(1) (Law, Llama-3.1-70B vs
  Qwen1.5-72B, 59:29 p = 0.0018) [LEDGER KEY-TIE-DECLINE, KTD-CHECK]. LOAO widener 663 / 3(2) / nominal 1.27
  [LEDGER BUDGET-LOMO].
- merged per-anchor, 2,538 edges: widener + decline 1,714 / 4(4) = 0.23% at the record's seed; 4-5 wrong over 11 seeds
  (0.23-0.29%), 1,713-1,720 called; the Law arx_0314 vs claude-3-5-sonnet edge sits 2.7e-5 under the cutoff
  [LEDGER KTD-CHECK]. All four residue edges: KEY winner Llama-3.1-70B, UNDER-rated by the judge (3 Law, 1 Philosophy)
  [LEDGER KTD-CHECK (2)].
- merged pooled, 190 pairs: 150 / 0(0) at every threshold 0.90-0.995; 150-151 over 11 seeds; rule-of-three UB 2.0%;
  nominal 0.148, EXTRAPOLATED (fit population s 0.20-0.30, pooled s median 0.071) [LEDGER KTD-CHECK; FW L101, L169].
- grok (Python draw), 891 edges: LOAO 667 / 2(1) / nominal 1.11, utility 74.9%; unfiltered 920: 653 / 2(1) / 1.24
  [LEDGER GROK-CALIB].
- grok (Kotlin draw), 890 edges: LOAO 669 / 2(1) / nominal 1.00, utility 75.2%; unfiltered 918: 661 / 1(1) / 1.10
  [PROG L4254-4258].
- MATH with a checker reference (STAGE3-MATH-CAPFREE): 24 of 28 pairs established, 0 of 24 wrong at every threshold,
  exact one-sided UB 0.117; calibration UNDETERMINED by design [PROG L4009-4011].

Calibration status word on every one of these boards: UNDETERMINED (nominal < 3) [FW L101; LEDGER SYSTEMATIC-BUDGET,
GROK-CALIB, CERT-CORPUS]. "Calibrated" is never emitted [FW L101, guard 6 L232].

### 1.3 Tiers and bands

Pooled 20-model board of record, widener + decline at 0.975: 3 tiers [9, 9, 2], 0 cross-tier key inversions, 35 of
150 ORDERED edges inside a tier; raw self-tiering 11 tiers / 7 inversions (4 established); raw + decline 8 / 3(3)
[FW L119]. Per-model band (certified above, certified below, unseparated): gemini-3.1-pro (0, 14, 5), arx_0314
(0, 12, 7), gpt-4o-mini (3, 10, 6), Llama-3.1-70B (7, 9, 3), Llama-2-7b (18, 0, 1) [FW L119]. The undominated set
(router's object) is six models: iask_pro, gemini-3.1-pro, claude-3-5-sonnet, arx_3, gpt-4o, arx_0314 [FW L11, L131].
Under the scale-consistent max-t readings the board keeps [9, 9, 2] with all 150 ORDERED; ORDERED falls at most
14.1% per anchor, 0.0% pooled [LEDGER MAXT-MULTIPLICITY].

Across-tier is NOT error-free: on the merged board 176/183 across-tier separations, 5 wrong, 4 established, all on
NOVEL pairs (2.9% raw rate); within-tier 6/7, 3 wrong, 1 established (arx/iask) [LEDGER TIER-HONEST-X20 bracket].

### 1.4 Conventions A/B on the boards of record

Kotlin board: key-decidable accuracy A 0.852 (n = 4,495), B 0.917 (n = 4,177); decidable tie rate 0.069; ties 0.221;
flips 0.159 [PROG L4246-4248]. Grok Python draw: A 0.849 (n = 4,499) vs Mistral 0.852 on the same schedule
[LEDGER GROK-CALIB]. STAGE3-MATH-CAPFREE: A 0.958 (n = 1,537), B 0.993 (n = 1,484) [PROG L3998-4000]. GEN-ARENA IFEval
(constraint-list reference): 0.658, ties 25.6%, flips 38% [LEDGER GEN-ARENA].

### 1.5 Support rule and design effect

- k = q x SE^2 declared under the Jeffreys 0.5 prior of rj.mm_fit / BtMmFitter: 2.04 [p10 1.42, p90 3.06] on
  ratings_x12.db, 2.06 [1.33, 3.02] on STACK-v2; the 4.84 is the same quantity under the unpenalised fit — the whole
  gap is the prior (clustering DEFF median 1.12 explains 13%) [LEDGER K-RECONCILE]. Allocator: SE 0.20 needs 36-77
  distinct questions per cell; SE 0.15 needs 63-136 [FW L85 bracket, L207 bracket]. The earlier 92-215 (and the
  "~120-190 q/cell" quoted in H6b / LEAF-PROFILE) mixed two theta scales [FW L207 bracket; LEDGER H-6, LEAF-PROFILE].
- Prior magnitude is not small: 66 pseudo-matches per anchor = 5.2% (Math) to 23.0% (Philosophy) of real matches;
  per-anchor theta SD shrunk 1.23-1.82x; SD_cell 0.937-1.630 is prior-dependent [LEDGER K-RECONCILE checker (3)].
- Match-level SEs understate by DEFF 2.0x median, 3.7x worst (question reuse) [LEDGER H-6 (H6b)].
- Profile-reliability crossing (a different quantity from SE): six largest anchors 178-320 q/cell, interval union
  [82, 418]; first measured seed-mean >= 0.70 at S = 210 (0.7071; 3 of 10 seeds below); all-14 x12 349-732
  [135, 9405], merged 226-325 [141, 495], none measured >= 0.70 within the 115-q ceiling; key 19-58 / 34-49
  [LEDGER PROFILE-INTERVAL-ALL C1]. "210" is not quoted [FW L117].
- Routing attenuation: realised bareq512_s42 routing misfiles 24.7% of the pool; the attenuation is a proportional
  ~20% shrinkage of every (model x anchor) contrast at 19% (30-35% in the smallest anchors); publishable contrasts
  99 -> 84 (C1), 91 -> 65 (C2); established key edges 97.6% kept, 0 reversed [LEDGER ROUTING-ATTENUATION].

### 1.6 The honest name for the object

What the record publishes per model is: (i) a key-built (model x anchor) accuracy row with SE and McNemar directions on
keyed cells, at 0 judge calls; (ii) on unkeyed cells a theta/SD_cell row whose board-level reliability is 0.72 with an
interval that contains FAIL, and whose per-anchor certifiability is 2 PASS / 7 PASS-WITH-INTERVAL / 5 FAIL; (iii) a
certified partial order (ORDERED edges) with wrong(established) beside it and the status word UNDETERMINED; (iv) a tier
map and a band (above, below, unseparated) per model; (v) the undominated set per cell.

This is a **verification-fidelity atlas with intervals and classes**, not a capability profile in the sense of a
per-skill vector. Two facts make the difference load-bearing:
- On MMLU-Pro the profile's routing content is zero: gemini-3.1-pro is best in all 14 anchors on both rosters, routing
  gain 0.000 (anchor) / -0.002 (leaf) against an oracle ceiling 0.967 / 0.982 [LEDGER ROUTER-REGRET-MMLU]. The
  model x anchor interaction is real (ARENA-V2 anchor LRT p = 0.001; anchor profile beats global on next-verdict
  log-loss +0.0062 [+0.0041, +0.0084], M1) [LEDGER X12/ARENA-V2, M1/M2] but never flips the argmax. A "profile" whose
  14 rows are monotone in one global score carries little that the global score does not.
- The profile's deviation content (delta_ac) is what a capability profile would mean, and the record has never
  published the deviation term with its own certificate; it publishes theta/SD_cell per cell. Lead L1 below.

---

## 2. What it refuses, and why

| Refused | Why (record) |
|---|---|
| Frontier order (arx_0314, iask_pro, gemini, gpt-4o; six undominated on the merged board) | 24 consecutive Mistral rows, median top-4 violations 3.0 at every budget 250-36,871 [LEDGER M1/M2]; perfect reference 0.612 -> 0.777 and arx vs iask still 0.528, p = 0.41 [LEDGER ORACLE, distilled]; frontier fit in sample 0 called / nominal 0.000, raw 31 / 5(2) / 0.187 (26.8x); b1 profile contains 0 [LEDGER FRONTIER-FIT]; the composed KEYED rule still orders 4 frontier-internal per-anchor edges (all right-direction), so BANDED there holds by fiat override [LEDGER FRONTIER-FIT checker (1)]. Guard 8 [FW L234]. |
| Per-question ranks | 5.7% test-retest floor on byte-identical prompts, 0.050 at T = 0, CI [-0.030, +0.017] [LEDGER DECOMP, TEMP-0]; 41% of x12 wrong-direction labels key-indeterminate (18 of 44) [LEDGER SYSTEMATIC-BUDGET (c)]; a verdict is largely a transcription of the reference [FW L153]. |
| Sub-anchor rows (leaf, twig, shrunk) | Judge leaf R 0.086-0.36; key sub-anchor profile not tree-robust on re-celled questions: most-changed third key -0.071, judge -0.084 [LEDGER PROFILE-TREE-ROBUST]; KEY-SUBANCHOR-SCALE: containment < 0.25 (n = 1,239) r = -0.0665 below all 200 null reps; no cell size brings it to 0.70; the Jaccard tercile instrument is invalid (37% nested pairs) [LEDGER KEY-SUBANCHOR-SCALE]. Reliability 0.80 at leaf needs ~1,127-1,514 q per leaf [LEDGER PROFILE-TREE-ROBUST (7)]. Guard 16 [FW L242]. |
| The word "calibrated" | Operating point 3 wrong vs 1.27 nominal, Poisson P(>= 3) = 0.135 [LEDGER SYSTEMATIC-BUDGET]; aggregate pass carried by 228 uncalled edges and a doubled widener passes it too [LEDGER SYSTEMATIC-BUDGET; FW guard 6]. NOT DETECTABLY MISCALIBRATED needs nominal >= 9, ~7.3x the x12 support (~100 anchors, ~6,500 keyed edges); no corpus in the programme supplies that [FW L171, L253]. |
| Nominal confidence off the fitting roster or judge | BUDGET-TRANSFER 1,104 called / 10(2) wrong / nominal 1.59, UNDETERMINED as pre-registered [LEDGER BUDGET-TRANSFER]; JUDGE-TRANSFER 354 / 0 / 0.93 established, utility 57.0%, established-label MLE tau -> 0 [LEDGER JUDGE-TRANSFER]; parameters stored per (board id, judge_model) and refused elsewhere [FW L95, guard 7]. |
| ORDERED-JUDGED for the shipped judge as a settled fact | b1 identification is re-draw-fragile: Δdev 4.47 (Python draw) vs 2.26 (Kotlin draw of the identical judge on identical bytes) against 3.84, ~26 established events [PROG L4259-4267; LEDGER GROK-CALIB bracket]. "Available for grok" rests on one draw until item 26 is amended. |
| Difficulty-stratified boards | every merged stratum board UNDETERMINED (nominal < 3 in 42 of 42 anchor strata; 5,233 called, 181 raw wrong, 11 established); 72-79% of the accuracy drop is the reference's [LEDGER TOPIC-DIFFICULTY]. |
| Boundary / dual-cell rows | MULTI-OWNERSHIP closed as a judging mechanism: tie Q1-Q5 -0.2pp [-2.4, +2.1], flip +0.4pp [-1.3, +2.1], leaf-FE -0.024 [-0.074, +0.025] on the merged board; wrong(established) Q1-Q5 A +1.2pp [-2.3, +4.6], B +0.0 [-2.5, +2.6] [LEDGER BOUNDARY-DISAGREEMENT]. |
| Any preference claim; any agent-trace row | no human preference data anywhere [CTX §1]; "Nothing here judges agent traces; the registered >= +5pp verifier gain on trace-shaped tasks was never measured" [FW L269]. |
| Rubric text, checklists, ensembles, gating, escalation, temperature, single/selective order | closed lines [CTX §5]; REF-CHECKLIST: checklist 0.749 vs no reference 0.734 vs answer 0.845 (n = 826) [distilled]; ESCALATE-LLAMA-LAW FAIL, gain is tie removal larger on the control [LEDGER ESCALATE-LLAMA-LAW]. |

---

## 3. Newcomer placement and its cost per model

**Measured (NEWCOMER-PLACEMENT-LIVE, 1,600 calls):** four-anchor sequential bisection of the 19-incumbent board,
100 pool questions per anchor = 400 filtered dual-order matches per newcomer, grok + STACK-v2, single-source primary
readout with B = 2,000 question-clustered bootstrap [PROG L3852-3866].
- claude-3-5-sonnet (frontier-adjacent): certified above Qwen1.5-72B and below gemini (0 opposite draws each);
  UNSEPARATED from gpt-4o (0.505 [0.414, 0.591]) and arx_3 (0.510 [0.420, 0.590]); key-tier interval 1..7 (7 tiers),
  own tier 3 contained [PROG L3867-3870].
- gpt-4o-mini (mid-board): above Qwen1.5-72B and claude-3-5-haiku (36 opposite draws of 2,000), below arx_0314 and
  gpt-4o (2 opposite draws); interval 4..6 (3 tiers), own tier 6 contained [PROG L3870-3872].
- Criterion (<= 2 adjacent tiers) FAIL for both; class BANDED, PROVISIONAL; "400 matches is not a placement budget"
  [PROG L3872-3873; FW L15 bracket, L211 bracket, L267 bracket, L378 bracket].
- The width is where the bisection lands, not judge error: key-decidable accuracy 0.765 / 0.817; sonnet sits in the
  band the record refuses to order; gpt-4o-mini's 3 tiers are the tier-6 cluster (0.631 / 0.629 / 0.628) plus one tier
  each side [PROG L3874-3879]. Read adversarially: more matches will not narrow a band whose width is the key's own
  0.003 cluster plus a frontier the record declines. The ceiling on placement precision is a key-tie ceiling, and it
  is per-position, not per-budget.
- SECONDARY (mixed fit, never the verdict): theta +1.421 [+1.249, +1.611] band [3, 6]; +0.706 [+0.526, +0.891]
  band [7, 9] [PROG L3879-3881].

**Cost per model, cheap-call equivalents [FW L209-213, L189]:** keyed cells 0; placement 800 cce measured to buy a
3-tier band mid-board / whole-frontier band near the top; profile coverage at the x20 density ~1,550 unfiltered matches
= ~3,100 cce per model (100 per new pair, 12,394 / 8 models) — and the filtered equivalent is UNTESTED for profile
reliability [FW L405]. So the honest per-newcomer bill for a judge-built profile row on 14 anchors is ~3,900 cce, and
what it buys is a row on a board whose reliability is 0.72 with an interval that contains FAIL.

**Synthetic economics (M3, key as oracle, 46 models):** placement ~400 matches flat in roster size (median rank error
0/0/1/1 at 16/24/32/46) but "within +-1" falls 98 -> 88 -> 72 -> 61%; a judge 4x noisier than the key needs > 4x the
matches (prediction "~2x" wrong); NOISY rho 0.947 -> 0.975 as the roster grows [LEDGER M3]. The +-3-rank interval is
M3's synthetic p75 and is not quoted as a measurement [FW L121]. The real newcomer before this one (ARENA-13,
grok-reasoning, 2,394 calls) ended UNRESOLVED with theta CI [-0.068, +0.186] [LEDGER ARENA-13, PLACEBO-ENTRY]; the
methodological rule from PLACEBO-ENTRY (every rank-based pass/fail needs a resolution check) is why NEWCOMER's FAIL is
read as band width and not mis-ranking [LEDGER PLACEBO-ENTRY].

**Board growth is safe for the incumbents:** the 12 keep their order at tau 0.970 with 8 added models [LEDGER
ARENA-V2-X20]; ARENA-13 tau 0.970 at 1,800 calls [LEDGER ARENA-13]; one-by-one insertion ~ joint fit (M3). What is
not safe is the frontier read: top-6 iask > gemini > sonnet > arx_0314 > arx_3 > gpt-4o vs key gemini > arx_0314 >
iask > arx_3 > sonnet > gpt-4o = 4 violations [LEDGER ARENA-V2-X20].

---

## 4. The reliability constant, seed fragility, halving bands

- **The pre-campaign constant is dead.** The thesis-era r = n/(n + 7.66) was 3.04x too large (Spearman-Brown applied
  after the fit, x0.50; roster dependence, x0.66; corrected c = 2.52 at the 11-model band, never refit to the settled
  roster) [docs/IMPLEMENTATION.md L103; memory reliability-constant-wrong]. The record now carries no constant: per-cell
  reliability is the split-half instrument with a jackknife interval and the halving SD (guard 15 [FW L241]), and
  support is k = q x SE^2 under the declared prior [LEDGER K-RECONCILE]. Any profile row that quotes a closed-form
  reliability is quoting a superseded number.
- **Halving bands.** The "+-0.012 over 40 halvings" on x12's 0.6728 is re-halving spread, not sampling uncertainty; the
  sampling interval is [0.49, 0.85] and contains FAIL, PASS and "worse at 20 models" [LEDGER PROFILE-RELIABILITY
  bracket; FW guard 15]. Per anchor, History [0.681, 0.731], Other [0.678, 0.738], Engineering [0.652, 0.720] have 0.70
  inside their 40-halving bands: seed-dependent classes [LEDGER PROFILE-INTERVAL-ALL checker (1)]. The three estimators
  on the same board give 0.6728 [0.5108, 0.8348] fixed / [0.4932, 0.8524] re-halved / [0.4097, 0.8054] cell-boot
  [LEDGER PROFILE-INTERVAL-ALL (1)].
- **Seed fragility elsewhere in the profile chain.** b1 identification flips across draws (4.47 vs 2.26)
  [PROG L4259]; b1 swings 2.61x across LOMO folds (+2.05 to +5.37) with b0 co-varying at -0.99, so the b1 column says
  nothing about scale on its own [LEDGER BUDGET-LOMO]; JUDGE-TRANSFER's anchor-clustered bootstrap on b1 is
  seed-dependent ([-0.78, +19.15] / [+0.28, +28.20]) [LEDGER JUDGE-TRANSFER]; the per-anchor residue is 4 wrong in 9 of
  11 seeds and 5 in 2 [LEDGER KTD-CHECK]; the union router's across-seed spread 1.56pp exceeds its within-seed SE 0.53
  [LEDGER MC-E2E]; [CORRECTED 2026-09-23 by the registrar (MC-E2E criterion (3) figures; insertion only, zero calls): 'spread 1.56pp vs within-seed SE 0.53pp' are the FIRST, CONTAMINATED, pre-MATH-FIX readout's figures (experiment_results/multicorpus/router_e2e.txt, 'across-seed spread 0.0156 vs mean within-seed SE 0.0053', n = 6,481 per seed); the CLEAN MATH-FIX readout that +3.38pp comes from prints 'across-seed spread 0.0194 vs mean within-seed SE 0.0093' (experiment_results/multicorpus/router_e2e_mathfix_clean.txt, n = 1,946 / 1,973 / 1,914), i.e. 1.94pp vs 0.93pp. The verdict, (3) FAILED, stands under both.] leaf identity is a sample draw (ARI 0.585-0.704) while anchors drift <= 0.59pp [FW L57].
- **Consequence for a profile row:** the row's class (PASS / PASS-WITH-INTERVAL / FAIL) is a seed-dependent label on
  3 of 14 anchors, and the certificate's ORDERED/BANDED label on the shipped judge is a draw-dependent label. A
  continual system that re-reads these each epoch will flip classes on noise unless it publishes the halving SD and the
  draw beside the class. The framework's guard 15 demands it; no epoch-to-epoch stability of a class has been measured
  (EPOCH-NULL is a leaf-level readout with no criterion [LEDGER EPOCH-NULL]).

---

## 5. Which of today's findings change what a profile row can say

- **CAP-GATE-POSTHOC (exploratory, zero calls).** A capability split gate accepts a DIFFERENT SET of sites from the
  geometric certificate (af: 24 of 69 at t = +1, 9 of 16 certified, Jaccard 0.29); the certified-vs-uncertified LOMO
  contrast +1.20 is mostly site size (matched on log n +0.31); the strongest "different" sites are small, deep and do
  not replicate on the tree's own held-out side (joint 6/16, contrast +0.34) [LEDGER CAP-GATE-POSTHOC]. For a profile
  row: geometric certification of a cell is NOT a certificate that the cell's children differ in capability, and never
  necessary. A row's cell address stays a reporting address; "certified split" must not be read into the row as
  "capability-distinct cell". Adjudicates nothing about any board.
- **TOPIC-DIFFICULTY (zero calls).** Inside a cell, key-decidable accuracy falls 0.938 -> 0.783 (-15.5pp
  [-18.5, -12.4]) and ties rise +6.6pp [+5.0, +8.3] easy -> hard; 72-79% of the drop is the reference's (reference-
  correct rate 98.4 -> 93.7 -> 77.7%); judge's own residual within reference-correct -4.5pp [-6.7, -2.5]; rho(easy,
  hard) below the null in 5 of 14 anchors; every stratum board UNDETERMINED [LEDGER TOPIC-DIFFICULTY]. For a profile row:
  the row's verification fidelity is not difficulty-invariant, and the non-invariance is the reference's; a row on an
  unkeyed cell inherits the cell's reference-correct rate as an unprinted covariate. The only deployable by-product: the
  key-free plurality-agreement proxy (Spearman 0.785 with difficulty; recovers 44% of the contrast) — a new registration
  if used as a widener covariate [LEDGER TOPIC-DIFFICULTY consequence].
- **BOUNDARY-DISAGREEMENT (zero calls).** No boundary excess on the merged board; C3 HELD (wrong(established) does not
  differ by margin); the x12 66-pair schedule reads a flip gradient (+2.9pp [+0.4, +5.4]) the 124-novel-pair schedule
  does not (-1.2 [-3.6, +1.1]), paired +4.15pp [+1.04, +7.50]; the depth-1 margin reads positive (tie +2.5 [+0.2, +4.5],
  flip +2.5 [+0.7, +4.3]) but anchor-confounded [LEDGER BOUNDARY-DISAGREEMENT checker]. For a profile row: a question's
  cell margin does not change its verdict reliability, so dual-cell judging buys nothing; multi-ownership as an
  ATTRIBUTION choice (a question contributing to two cells' rows) is unmeasured and open — and it would change the
  denominator of every row it touches.
- **ANCHOR-FREE / ANCHOR-FREE-CERT (zero calls).** The embeddings-only tree keeps the key-visible capability
  information (13.2 vs 14.0 per 1000), loses 6.4 points of purity, certifies 16 of 69 vs 5 of 65; no lever beats 16
  under a common null; the record's tree is one bar step from not existing (d512 arm stops at 4 leaves; bar 0.030 at
  2 leaves) [LEDGER ANCHOR-FREE, ANCHOR-FREE-CERT]. For a profile row: the row's cell can be an anchor-free node (no
  category name) without losing capability information — but that tree is a structural artefact, "not arena-bound for
  boards" [CTX §3], and nothing changes for the published rows until an anchor-free tree is arena-bound by registration.
- **STAGE3-MATH-CAPFREE / CHECKER-ANSWER-INGEST.** With an exact checker reference on terminated traces the cheap
  judge reaches A 0.958 / B 0.993 and 0 of 24 established pairs wrong; but 16.5% of question-pairs are excluded by the
  1,024-token cap and per-model checker accuracy is up to +0.10 higher on admitted rows [PROG L4012-4016]. For a
  profile row on a generative cell: the row's denominator is the ADMITTED population, and any agent-like trace that
  does not terminate is NON_TERMINATED, never a verdict, never a tie [FW L73]. A capability profile of an agent whose
  traces frequently hit a cap is a profile of its short traces.
- **GEN-ARENA (IFEval).** Constraint-list reference: 0.658, rho 0.719, ties 25.6%, flips 38%; judged argmax != key
  argmax on both generative corpora; routing on judged verdicts costs -4.7pp pooled [LEDGER GEN-ARENA]. The only
  constraint-shaped (agent-adjacent) cell in the record does not clear the profile bar as judged.

---

## 6. Adversarial reading: where "capability profile" is a claim the data cannot carry

1. **"Capability."** Every number is verification fidelity against a key, checker or a possibly-wrong reference
   [CTX §1]. On unkeyed cells the row measures agreement with a cached reference whose own accuracy spans 0.727-0.952
   across cells (REF-BY-CELL) and 98.4 -> 77.7% across difficulty terciles [LEDGER TOPIC-DIFFICULTY]; the judge
   transcribes it (match-level REF +2.177 vs KEY +0.788 [FW L153]). A row on an unkeyed cell is a reference-fidelity
   row. Weaker object it can carry: "agreement with reference R_v (vintage v) at fidelity f, class BANDED-JUDGED".
2. **"Profile."** The judge-built anchor vector has board-level R 0.72 [0.61, 0.83] and 5 of 14 anchors FAIL; 3 more
   are seed-dependent [LEDGER PROFILE-INTERVAL-ALL]. Weaker object: a global theta with a band, plus a list of anchors
   on which the model's deviation is certified (Lead L1), with the rest PREDICTIVE-ONLY.
3. **"Per model."** Rows exist only for models with traces on the EVAL side of a corpus with a pinned pool; a newcomer
   costs ~3,900 cce for a judge-built profile whose reliability at the filtered density is untested [FW L405]; its
   placement is a 3-7-tier band [PROG L3872]. Weaker object: PROVISIONAL band + key-built rows, with judge-built rows
   only after coverage.
4. **"Continually."** The record has one epoch. Canary pass 2 (the only drift instrument) is refused before
   2026-09-22 [LEDGER CANARY-BASELINE]; the reference cache carries no vintage stamps (3,432 legacy solves) [FW L37];
   the sequential-look rule (L_max = 2 at 0.9875) is DESIGN, uncalibrated [FW L103, L266]; no test calibrates the
   certificate under adaptive allocation [FW guard 13]. Weaker object: a single-epoch atlas with a registered canary,
   and NO drift statement until pass 2 lands.
5. **"And agents."** Zero rows. No agent trace has been judged; the verifier gain on trace-shaped tasks was never
   measured [FW L269]; the nearest cells (MATH with a checker; IFEval with a constraint list) show that the reference
   FORM decides everything (0.958 vs 0.658) and that non-terminated traces are excluded by rule. Weaker object: for an
   agent, a checker-output-referenced row on terminated episodes only, with the admitted-population denominator
   printed; nothing else exists to publish.
6. **"Frontier."** The models a user most wants profiled are exactly the ones the record refuses to order at any
   budget [LEDGER M1/M2, FRONTIER-FIT]. The profile of a frontier model is a band of six with a per-anchor NOT RESOLVED
   row per pair [FW L121].

---

## 7. LEADS — registrable next tests, ranked by value per call

Each: instrument; what it would let the profile say; cost; hazards; closed lines it must not reopen. Ranked by value
per call; zero-call leads first because their value is not divided by zero but their risk is confined to the record.

### L1 (0 calls, highest value/call) — PROFILE-DEVIATION-CERT: publish the deviation term with its own certificate
- Instrument: from the merged board's draw matrix (x20_merged.py, B >= 2,000 question-clustered) compute per
  (model, anchor) delta_ac = (theta_a + delta_ac) - theta_a with its bootstrap SD; call a deviation CERTIFIED iff
  |delta_ac| / SD >= q_cell from MAXT-MULTIPLICITY's scale-consistent per-cell critical value (3.43-3.80 merged per
  anchor); key comparator: the same on the 46-model key (accuracy deviation from the model's pool mean, McNemar-
  established against the pool). Report the variance share of delta vs theta on key and judge, the certified-deviation
  list per model, and the wrong(established) count where a judge-certified deviation has the opposite sign on the key.
- What the profile could say: "model m is certified above/below its own global standing in anchor c" — the first
  statement that is a capability PROFILE and not a re-indexed global score; and, adversarially, how many of the 280
  merged cells carry any certified deviation at all (the record's suspicion: few, and mostly the same anchors that
  PASS reliability).
- Cost: 0 calls; ~1 CPU-hour (bootstraps cached).
- Hazards: the hybrid max-t artefact (use raw-z or widened-q, never the hybrid) [LEDGER MAXT-MULTIPLICITY checker (1)];
  the Jeffreys prior shrinks per-anchor theta SD 1.23-1.82x, so a deviation on a small anchor is prior-shrunk — print the
  prior [LEDGER K-RECONCILE (3)]; routing attenuation ~20% on every contrast [LEDGER ROUTING-ATTENUATION]; FAIL anchors
  (Health, Economics, CS, Biology, Engineering) must publish PREDICTIVE-ONLY regardless of the deviation test.
- Must not reopen: sub-anchor rows (the cell is the anchor, full stop); no leaf deviation.
- Prediction to register: on the key, certified deviations exist for < 30% of (model, anchor) cells; on the judge,
  < 15%, concentrated in Physics/Math/Law; judge-certified deviations with the wrong key sign: 0-2 (established).

### L2 (0 calls) — PER-ANCHOR BAND ATLAS: the profile object as an artefact, with classes
- Instrument: ktd_check.py's per-anchor edge table (2,538 edges, composed rule at 0.975) -> per (model, anchor) the band
  (certified above, certified below, unseparated), the anchor's reliability class from PROFILE-INTERVAL-ALL C2, the
  key-built row beside it, wrong(established) per anchor, denominators (2,811 / 2,646 / per-anchor 119-304), and the
  PROVISIONAL rows for the two newcomers from newcomer_placement_outcome.txt (single-source only).
- What the profile could say: exactly what the record supports, in one table per model, with the five FAIL anchors
  visibly PREDICTIVE-ONLY. This is the deliverable the author's goal names, at the granularity the record allows.
- Cost: 0 calls.
- Hazards: the knife-edge Law edge (c = 0.974973) flips the residue between 4 and 5 across seeds — publish the 11-seed
  band, not one seed [LEDGER KTD-CHECK]; the merged board is Mistral; the shipped judge's board (Kotlin) needs its own
  atlas and must never be merged into this one (mixed-fit guard [FW L238]); key-tie decline exists only where a key
  exists, so the atlas has a keyed-cell shape that unkeyed cells will not have.
- Must not reopen: nothing; this is a readout.

### L3 (0 calls) — B1-POOLED-DRAWS: amend item 26 so ORDERED-JUDGED for grok does not rest on a draw
- Instrument: pool the established labels of GROK-CALIB (Python) and JUDGE-WIRING-BOARD (Kotlin) on their 9,123
  shared matches (~52 established wrong-direction events), fit tau(A) with a draw indicator as a scale term (same
  judge, same bytes — allowed under the mixed-fit guard only WITH the term), cluster the bootstrap by question (the two
  draws share questions, they are not independent), and publish the Δdev at b1 = 0 with a power statement: the
  probability that a true b1 = +2.7 clears 3.84 at 26 vs 52 events.
- What the profile could say: whether any ORDERED-JUDGED row exists for the shipped judge, with a power number instead
  of a coin-flip between 4.47 and 2.26.
- Cost: 0 calls.
- Hazards: pooling two draws double-counts questions unless clustered; the widened tau must be stored per (board,
  judge, draw-set); if the pooled Δdev also straddles 3.84 the outcome is UNDETERMINED and grok's cells stay
  BANDED-JUDGED — a registered outcome, not a failure.
- Must not reopen: JUDGE-TRANSFER's cold read; no borrowing of Mistral parameters.

### L4 (0 calls) — PROFILE-R-FILTERED: reliability of the anchor profile under the filtered schedule
- Instrument: PROFILE-INTERVAL-ALL's estimator on the merged board restricted to answer-disagreeing matches
  (PLACEBO-ENTRY arm A's refit population; x12 34.3% same-letter, x20 48.2% [LEDGER TOPIC-DIFFICULTY bracket]), 40
  halvings, LOAO jackknife, per-anchor C2 classes.
- What the profile could say: whether the ~3,100 cce per-newcomer coverage figure survives the filter that halves the
  bill (ARENA-V3-COMPILED: 10,552 vs 18,284 calls at rho 0.986 vs 0.972). FRAMEWORK L405 names this as untested.
- Cost: 0 calls.
- Hazards: filtering widens the theta scale 13% (SD 1.785 vs 1.574) — compare R only, never thetas across the two fits
  [LEDGER PLACEBO-ENTRY; FW guard 12]; the filtered board has fewer distinct questions per cell, so R will fall by
  support alone — report q_distinct per anchor beside R.
- Must not reopen: the tie-break line (AGGREGATE / ARENA-V3-COMPILED arm C) — NO-TIES default stays.

### L5 (0 calls) — PLACEMENT-CEILING: is the newcomer band a key-tie band?
- Instrument: from newcomer_placement.db (single source), for each unseparated anchor pair compute the key gap and the
  McNemar establishment on the newcomer's 100 pool questions per anchor; the band's width decomposed into
  (positions inside a key-tie cluster at the 0.017 gap) + (positions inside the frontier band) + (positions the arena
  could have separated at nominal power). Plus a zero-call resolution curve: subsample the existing 400 matches at
  100/200/300 to read how the band width moves with budget on the data already bought.
- What the profile could say: whether a placement budget above 400 matches CAN narrow the band, or whether the width
  is the key's own (0.631 / 0.629 / 0.628) and no budget changes it. This decides whether Lead L8 is worth its calls.
- Cost: 0 calls.
- Hazards: single-source readout only (the mixed-fit secondary is never the verdict) [PROG L3879]; the 100-question
  anchors are below the SE 0.15 support (63-136 distinct questions) on the smaller anchors.
- Must not reopen: the frontier order.

### L6 (600 calls, already registered) — CANARY-BASELINE pass 2 on/after 2026-09-22
- Instrument: canary_baseline.py pass 2 on the frozen 300-match set (hash 50af669ac6997f9f); the floor is pass 1 vs
  pass 2 [LEDGER CANARY-BASELINE].
- What the profile could say: the first and only "continual" sentence — that the deployed judge's retest floor on this
  set is X% (predicted 4-6% contested, lower cross-tier) and that the epoch's boards are read against it.
- Cost: 600 calls. Hazard: MDE ~2.7pp at n = 300; a single epoch cannot see a 2pp drift [FW L141].
- Must not reopen: temperature (omitted, D2).

### L7 (~2,400 calls) — IFEVAL-CHECKER-OUTPUT: the agent-adjacent cell with an answer-shaped reference
- Instrument: GEN-ARENA's 1,200 IFEval matches re-judged with the CHECKER OUTPUT (per-constraint pass vector, backfilled
  by CHECKER-ANSWER-INGEST; IFEval D_c 0.99-1.00) as the reference block, instead of the constraint LIST (0.658, ties
  25.6%); paired same-match contrast, both conventions, wrong(established) on the 28 pairs, calibration status by the
  power rule (expected UNDETERMINED).
- What the profile could say: whether a constraint-shaped, trace-like cell can carry a judge-built row at the accuracy
  bar (>= 0.75 both conventions), i.e. whether an AGENT profile row is even reachable with the deployed recipe when the
  verifier's output (not its specification) is the reference. This is the single cheapest step toward the "and agents"
  half of the author's goal, and its FAIL branch is informative: if a pass vector does not lift IFEval, agent cells are
  key/checker-only.
- Cost: 1,200 matches x 2 orders = 2,400 calls (under the 4,000-match rule); 0 reasoning solves.
- Hazards: IFEval eval side is 162 questions, at the bottom of the support rule; ties may stay high (25.6%) since the
  judge must still verify per constraint; a pass VECTOR is answer-shaped, but the prompt must not present it as a
  checklist of criteria (REF-CHECKLIST closed: a checklist without the answer is worth +1.6pp n.s.) — it presents which
  constraints each answer PASSED, which is the checker's output [FW L37: CHECKER_OUTPUT > CACHED_SOLVE > NONE].
- Must not reopen: rubric-shaped references; ensembles; escalation.

### L8 (~3,200 calls, conditional on L5) — PLACEMENT-CURVE at 800 and 1,200 matches per newcomer
- Instrument: newcomer_placement.py extended: the two same newcomers, anchors chosen by the tier map (the two tier-
  boundary models each side of the 400-match band) rather than a fresh bisection, +400 matches per stage, single-source
  primary readout B = 2,000, band width in key tiers at 400 / 800 / 1,200.
- What the profile could say: the cost per model of a <= 2-tier band, or (the falsifier) that the band does not narrow
  and placement is key-tie-bound — in which case the profile publishes bands and the 800-cce line is the whole
  placement budget forever.
- Cost: 2 newcomers x 800 matches x 2 orders = 3,200 calls (one plan, under the cap).
- Hazards: sonnet's band is frontier-bound by rule and cannot narrow below the six undominated (do not spend on it if L5
  shows the width is entirely frontier + key-tie); optional-stopping if the second stage is triggered by the first
  stage's certificate (guard 13) — fix both stages' match counts before launch.
- Must not reopen: the frontier order; ARENA-13's ensemble reference.

### L9 (0 calls, low power, lowest rank) — DIFFICULTY-PROXY-WIDENER
- Instrument: the key-free plurality-agreement proxy (Spearman 0.785 with key difficulty) as a second covariate in
  tau(A, P) on the 891/920 x12 edges, LOAO, established labels, with the identification profile.
- What the profile could say: a narrower tau on hard cells without a key. Ranked last: SYSTEMATIC-SIGNAL's two-
  predictor fit was only 26-40 events deep, b1 alone is re-draw-fragile, and a second parameter at this support will not
  be identified — the registered outcome is almost certainly UNDETERMINED [LEDGER TOPIC-DIFFICULTY consequence; FW
  L193's "~900 edges / ~40 wrong labels" support rule]. Register only with a power statement.
- Must not reopen: reference-accuracy as a signal (key-derived; withdrawn in SYSTEMATIC-BUDGET (a)).

### Not a lead (named so it is not re-proposed)
- More matches at the frontier (M2: violations flat 250-36,871); a better cheap judge (JUDGE-2x2, JUDGE-SWAP: identity
  irrelevant given the reference); escalation on the residue (ESCALATE-LLAMA-LAW FAIL); sub-anchor rows at any cell
  size (KEY-SUBANCHOR-SCALE); dual-cell judging (BOUNDARY-DISAGREEMENT); construction levers for certification
  (ANCHOR-FREE-CERT, no lever beats 16 of 69); a checklist reference (REF-CHECKLIST); a temperature (TEMP-0).

---

## 8. Commands that reproduce the numbers quoted (read-only)

- Ledger rows as text: python strip.py docs/test_ledger.html <out> (scratchpad/leads/strip.py), then grep -F "<ID> |".
- Composed rule and residue: python tools/analysis/ktd_check.py (outputs experiment_results/x12_crossdomain/ktd_check.txt).
- Profile reliability and per-anchor classes: python tools/analysis/profile_interval_all.py
  (experiment_results/x12_crossdomain/profile_interval_all.txt); anchor_profile_interval.py.
- Grok calibration board: experiment_results/x12_crossdomain/grok_calib_outcome.txt, grok_calib_systematic_budget.txt;
  Kotlin draw: experiment_results/judge_wiring/board_outcome.txt, board_systematic_budget.txt.
- Newcomer bands: experiment_results/x12_crossdomain/newcomer_placement_outcome.txt (single-source primary section).
- k and the prior: python tools/analysis/k_reconcile.py (experiment_results/x12_crossdomain/k_reconcile.txt).
- Max-t: experiment_results/x12_crossdomain/maxt_multiplicity.txt.
- Difficulty / boundary: experiment_results/topic_difficulty/topic_difficulty_outcome.txt;
  experiment_results/x12_crossdomain/boundary_disagreement_outcome.txt.
- MATH checker cell: experiment_results/multicorpus/stage3_math_outcome.txt.

Nothing in this pass posted a call, built a tree, or wrote under docs/ or experiment_results/.
