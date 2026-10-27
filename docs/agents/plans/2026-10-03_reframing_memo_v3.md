# Reframing memo v3 (checkpoint G, research-lead), 2026-10-03

Zero calls; nothing built, run, registered or committed. As of HEAD b97dea4b, ledger v370. Supersedes v2
(`2026-10-03_reframing_memo_v2.md`) and carries its brackets (v2 #8, #9). Numbers come from `docs/agents/results/<ID>.json`
(numbers_of_record / sentence_of_record). Every comparison carries its label status: **[LF]** label-free,
**[AN]** anchored (depth-2 = declared classes), **[DECL]** declared labels, **[LC]** label-conditioned (per-class
prototypes or source-conditioned). A cross-status comparison is marked **cross** and is never read as a method ranking.
The framing and `report/` are the author's; this is a proposal. GEMMA-OWN-BAR is built, not run: slot in section 2 SQ5.

## 1. Revised framing (the author's to adopt, amend or reject)

**Per-cell evaluation pays where the cells carry label information; the tree's own value is addressing, filing
discipline and a free abstention signal, not a better partition.** On the content-closed v2 union split, routing on
[DECL] cells beats the best single model by +2.67pp and on [AN] tree cells by +2.62pp (not shown different); an [LF]
anchor-free tree gives a thin +1.52pp and falls short of [DECL] by -1.15pp (cross, descriptive). [WEAKENED 2026-10-04 by the testing-logic review, claim 1 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): AF-U is federated per source, so it is [SC] (source-conditioned) by this memo's own legend, not [LF]; the sentence needs '[SC]' and stays open until ROUTE-SOURCE-NULL] On known-answer intent
corpora an [LF] tree partitions EQUIVALENT to [LF] k-means at matched k, holds addresses as well under slot swaps, and
abstains on out-of-scope queries within 0.010 AUROC of [LF] k-means (and 0.005 below it). The site-null certificate
clears declared 14-way structure at depth-1 sizes, but its sensitivity to 2-way structure inside an anchor is unknown:
the only k = 2 control was a failed positive control. [CORRECTED 2026-10-04 by CERT-PC-K2-KNOWN and CERT-K2-DEFLATED (registrar; POSTRUN 07721b48, 761e606c): k = 2 sensitivity is STILL UNDETERMINED; both instruments are now characterised: the PLAIN site null gave NO-CONTROL on merged two-category pairs (its null is large, p95 0.081-0.127), and the DEFLATED null certifies any cut along a high-variance axis (PC1 median-cut controls pass like the declared pairs: ELONGATION-CONFOUNDED) and no low-variance source split (axis variance, not discrimination); the deflated null is not a usable certificate for data-driven splits; the plain J site null stays the certificate of record. docs/judge_v2_program.md L24214-L24224 (section "## CERT-K2-DEFLATED (2026-10-04, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 761e606c)] Refitting [AN] leaf means on declared classes helps on MMLU-Pro
and hurts on CLINC. Online, cell ids stay stable only if means are frozen, and an online tree files a new member 3.9pp
below a batch rebuild. Judge trust remains the reference's trust (no new SQ2 evidence since v2).

## 2. SQ1-SQ5 (supported / negative / open; ID: number; scope)

**SQ1 USE.** *Supported:* V2-DECLARED-CELLS C1 +2.67pp [+1.46, +3.89] [DECL]; G14 +2.62pp [+1.43, +3.82] [AN];
UNION-AF-ROUTE U1 +1.52pp [+0.14, +2.91] [LF] [WEAKENED 2026-10-04 by the testing-logic review, claim 1 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): read [SC], not [LF]] (union EVAL 5,907 / 5,404, one draw, union roster).
*Negative / bounds:* U3b -1.15pp [-2.19, -0.12] ([LF] vs [DECL], cross, descriptive); U2 D_K -0.45pp [-1.31, +0.41]
([LF] vs [LF] k-means: not shown either way). ESCALATION-RC RC1 UNDETERMINED: escalating the [LF] AF-U route to the best
single model on low margin or OOS (e 0.226) beats random escalation of the same share by +0.50pp, 95% [-0.004, +1.00]pp
(boundary case); against no escalation +0.15pp; F-RC not fired. The K_0 arm (+0.43pp) is [LC], cross, descriptive. [WEAKENED 2026-10-04 by the testing-logic review, claim 1 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): AF-U and K_0 are both [SC]: like with like ([SC] both), not cross]
*Open:* any [LF] cell set routing as [DECL] does (no test drafted); per-corpus gains. Judged escalation stays CLOSED.

**SQ2 TRUST.** Unchanged from v2 (K46-KEY-READ 0.9249 / 506 right vs 0.2632 / 38 wrong; JUDGE-SOLVED-SPLIT JS1
UNDETERMINED, MDE80 0.090). *Open:* RP19 (go given; waits on D2).

**SQ3 TAXONOMY (partition, filing, certificate).**
*Supported:* INTENT-TRANSFER-S1 (MASSIVE 4,946 / CLINC 6,672 EVAL; qwen3 256 RAW; one draw; leaves 84 / 139):
T-C1 EQUIVALENT x2, [LF] tree vs [LF] k-means (MASSIVE +0.00037 [-0.00371, +0.00444], delta 0.01745; CLINC +0.00718
[+0.00440, +0.00997], delta 0.01246: inside delta and above 0); T-C7 EQUIVALENT (D7 -0.00892, delta 0.0355);
T-C8 flatLeaf over descent +0.0726 / +0.0769 (HELD x2); T-C2 hierarchy over average-link DP +0.063 (MASSIVE, interval
only). G11 D_fd +0.0937 [AN] (union). CERT-PC-SIZE PS1 / PS2 5 of 5 certified at n 486 / 441 (declared 14-way, MMLU-Pro
member root, k_d 0/300; not k- or population-matched; PS2 overlaps PS1). FITSET-FAITHFUL FF1 +0.0256 [+0.0193,
+0.0320] (6,139 union EVAL; [AN] refit using MORE TRAIN labels vs [AN] as built; MMLU-Pro carries 155 of 157 net items).
*Negative:* F-TAX N-1 (G12 0 of 60). G13 -0.0215 and INTENT T-C1b FAILED x2 (D13' -0.0356 / -0.0403) compare
[AN]/[LF] trees with [LC] per-class prototypes (cross): read "below one supervised centroid per class", [CORRECTED 2026-10-04 by INTENT-TRANSFER-S1 (registrar; docs/reviews/AUDIT_results_drafts_2026-10-04.md, 7fbc2692; POSTRUN_intent_s1 W-4, 24f0b00d): stated backwards: the label-free tree's coarse filing (0.872 / 0.941) lies BELOW the label-conditioned per-class prototypes (0.908 / 0.982) and AT OR ABOVE one supervised centroid per class (0.867 / 0.855); never 'the tree files below an unsupervised comparator'] not a method
loss. FITSET-INTENT F-FI fires: [AN] refit vs [AN] as built, MASSIVE +0.0049 [-0.0006, +0.0103], CLINC -0.0264
[-0.0333, -0.0192] (interval below 0; not REVERSED only because below the k-means seed spread 0.0529). CERT-PC-K2
PK1 / PK2 K2-NOT, 0 of 30 (declared 2-way source-family split inside math, physics, economics; statistic 0.014-0.019
below its null minimum 0.042-0.050): a FAILED POSITIVE CONTROL, neither showing nor refuting k = 2 sensitivity.
*Open:* the certificate's power for 2-way within-anchor structure (CERT-PC-K2-KNOWN); [CORRECTED 2026-10-04 by CERT-PC-K2-KNOWN and CERT-K2-DEFLATED (registrar; POSTRUN 07721b48, 761e606c): k = 2 sensitivity is STILL UNDETERMINED; both instruments are now characterised: the PLAIN site null gave NO-CONTROL on merged two-category pairs (its null is large, p95 0.081-0.127), and the DEFLATED null certifies any cut along a high-variance axis (PC1 median-cut controls pass like the declared pairs: ELONGATION-CONFOUNDED) and no low-variance source split (axis variance, not discrimination); the deflated null is not a usable certificate for data-driven splits; the plain J site null stays the certificate of record. docs/judge_v2_program.md L24214-L24224 (section "## CERT-K2-DEFLATED (2026-10-04, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 761e606c)] FF2 (rho +0.235 [-0.130, +0.544]).

**SQ3 abstention and online filing.** *Supported:* OOS-TREE-CELLS OT1 EQUIVALENT within 0.010, and below: [LF] C-AF
tree cells vs [LF] k-means at matched k, Delta_T -0.00516, 95% [-0.00754, -0.00278] (CLINC oos_plus 6,672 + 1,350,
qwen3 256, one draw). INTENT T-C9 margin abstention D9 +0.367 (not tree-specific: tree minus k-means +0.014).
ONLINE-REPLAY-LOMO P3: new-member OOS ranking AUROC median 0.905 on capability text (descriptive; a ranking, not a
catch rate). *Negative:* ONLINE-REPLAY-LOMO OL1 LOSS, D -0.0386 [-0.0512, -0.0260] [WEAKENED 2026-10-04 by the testing-logic review, claim 5 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): OL1 (-3.9pp) and OS1 (-3.3pp) are P_fl losses against batch-named declared classes: 'online filing trails a rebuild' is a label-agreement statement; its routing or decision consequence is unmeasured; never a routing cost] (online vs batch, same cells and
filing rule; 6,139 / 5,628, 6 replays; the online arm is transductive, which favours it); OL2 NOT-STABLE (means-only
churn BBH 0.0925, MMLU_PRO_LB 0.0304); F-OL fires. At the registered trigger (GATE TPR 0.95) the OOS flag caught 6.5%
of BBH, 9% of MATH, 28% of GPQA. Online tree minus k-means (+3.0pp) is descriptive and reverses under the unit start.
*Open:* a calibrated trigger; a certified online split (stage 2 unregistered); OOS on real traffic.

**SQ4 PRICE.** Unchanged: retest floor d_r 0.100 [0.0658, 0.1342] (G17-CANARY, DESCRIPTIVE-ONLY); pass 5 not before 10-08.

**SQ5 INVARIANCE.** *Supported:* GOLD-LEVEL-EMB QUANT INVARIANT. E1-SPLIT-DRAWS: the [LF] nomic tree files worse than
the [LF] qwen3 tree on all 3 content-closed MMLU-Pro re-draws (G -0.1723, -0.0494, -0.0794; every interval below 0).
*Negative:* SD1 NEITHER; F-SD fires on the spread clause (Gbar -0.1004 inside spread_N 0.1315, set by one 28-leaf nomic
build under the qwen3-tuned bar 0.025). E1 now reads "the sign held across 3 re-draws; the magnitude did not". GOLD
F-GL (prompt and embedder NOT-INVARIANT). *Pending slot:* **GEMMA-OWN-BAR** (GO1: [LF] gemma tree under its own bar vs
[LF] gemma k-means, MASSIVE): decides whether M-AF-g's 4 leaves (and, by the same mechanism, N_e1sd1's 28) are
bar-tuning or recipe. [CORRECTED 2026-10-03 by GEMMA-OWN-BAR (registrar; POSTRUN ea335789, VALID): slot filled: G-AF built L = 1 (root never split; best 0.02874 < bar_g 0.043748); F-GO FIRES on its leaf clause; GO1 NOT READ (no tree). Licensed direction: gemma's own bar is STRICTER than 0.025, so M-AF-g's stall is not a too-strict qwen3 bar (root separation 0.42x its null p95 vs qwen3's 1.00x); qualifiers W-1 (neither root clears its own null; never 'below noise'), W-2 (k-way null vs min-pair gate), W-3 (nulls at 0.025). N_e1sd1: a bar-dependence on nomic geometry, direction unmeasured. docs/judge_v2_program.md L24093-L24104 (section "## GEMMA-OWN-BAR (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 65e5c0d7)] *Open:* embedder ranking (D3, the author's); tree-level SQ5 beyond MMLU-Pro and MASSIVE.

## 3. Framework changes, re-ranked (value x evidence / cost)

1. **File by flat leaf, never by descent.** SUPPORTED on the [AN] union tree and [LF] intent trees (G11; T-C8 x2).
2. **Name the reference policy per claim; fidelity conditional on reference correctness.** SUPPORTED (unchanged).
3. **Ties and decisiveness as columns, conventions A and B.** SUPPORTED (unchanged).
4. **Route on declared cells where declarations exist; [LF] tree or k-means cells only where they do not.** SUPPORTED [WEAKENED 2026-10-04 by the testing-logic review, claim 2 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): no [LF] cell set was tested on the union; both arms used source declarations; the evidence for routing on genuinely label-free cells is zero]
   (U3b cross, descriptive; U2 and T-C1 make the [LF] tree interchangeable with [LF] k-means, within their deltas).
5. **Abstention as a filing-layer output, on flat AND [LF] tree cells** (CLINC, one draw; within 0.010 and 0.005 below
   k-means). Upgraded from v2 #8. Claim it for the filing layer, never as a tree advantage.
6. **Embedder, prompt and separation bar belong to a cell set's identity.** SUPPORTED; strengthened: the bar is
   embedder-specific (E1-SD N-1; GEMMA-OWN-BAR decides how much). [CORRECTED 2026-10-03 by GEMMA-OWN-BAR (registrar; POSTRUN ea335789): the rule's gemma 768 bar is 0.043748, 1.75x stricter than qwen3's 0.025, and the gemma tree did not split at it (L = 1); docs/judge_v2_program.md L24093-L24104 (section "## GEMMA-OWN-BAR (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 65e5c0d7)]
7. **Power check (Support + reachability) as a FRAMEWORK.md stage.** SUPPORTED (process).
8. **Online evolution (a design, not a result):** freeze leaf means (F-OL); file flat; buffer low-margin and OOS items
   instead of absorbing them (OL1's loss sits in members with in-union neighbours, which the trigger mostly missed);
   rebuild periodically, with the batch tree as reference (OL1 -3.9pp); calibrate the OOS threshold on GATE for a
   catch rate, not the TPR 0.95 point. No part of the policy has run as a whole; no online split is certified. [CORRECTED 2026-10-03 by ONLINE-STAGE2 (registrar; POSTRUN 6f064b3b, VALID): the design ran as a whole (frozen means, GATE-calibrated OOS buffer, buffer rebuild every 100): OS1 LOSS, online filing 3.3pp below a batch rebuild (D -0.0326, 95% [-0.0446, -0.0205]); OS2 UNDER-CATCH (median catch 0.55 vs target 0.80); F-OS FIRES: the design is not filing-neutral and PERIODIC BATCH REBUILD STAYS NECESSARY. MUSR was caught fully (1.00) and still lost 12.2pp, so the loss is not only a catch problem. Stable ids hold by construction (frozen means), not as a measured result; 3.9 -> 3.3pp is descriptive only and nothing is credited to freezing. docs/judge_v2_program.md L24076-L24085 (section "## ONLINE-STAGE2 (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 6f064b3b)]
9. **Route escalation on margin / OOS: safe to include, near-zero benefit.** "Safe" means only that F-RC did not fire
   (no loss against random escalation shown); +0.15pp against no escalation. Never "a usable safety valve".
10. **Certificate as a false-discovery guard:** sensitivity measured for declared 14-way structure at depth-1 sizes;
   **k = 2 sensitivity unknown** (CERT-PC-K2 failed control). [WEAKENED 2026-10-04 by the testing-logic review, claim 7 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): the three k = 2 controls all used declared labels as 'known structure'; their failures are as consistent with 'declared sub-structure is not geometric' as with low power; write k = 2 sensitivity as untestable with declared-label controls until a planted control (CERT-PLANTED) runs] [CORRECTED 2026-10-04 by CERT-PC-K2-KNOWN and CERT-K2-DEFLATED (registrar; POSTRUN 07721b48, 761e606c): k = 2 sensitivity is STILL UNDETERMINED; both instruments are now characterised: the PLAIN site null gave NO-CONTROL on merged two-category pairs (its null is large, p95 0.081-0.127), and the DEFLATED null certifies any cut along a high-variance axis (PC1 median-cut controls pass like the declared pairs: ELONGATION-CONFOUNDED) and no low-variance source split (axis variance, not discrimination); the deflated null is not a usable certificate for data-driven splits; the plain J site null stays the certificate of record. docs/judge_v2_program.md L24214-L24224 (section "## CERT-K2-DEFLATED (2026-10-04, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 761e606c)] Write a non-certified depth-1 split as "weaker than
   declared 14-way structure at that n", never "no structure".
11. **[AN] fit-set refit on declared classes (v2 #9 / #8'): NARROWED to MMLU-Pro.** [WEAKENED 2026-10-04 by the testing-logic review, claim 3 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): the metric (P_fl against declared classes) rewards label fitting by construction; FF1 is a property of P_fl, not evidence of better cells; only the CLINC loss is informative] Not shown on MASSIVE; hurts on
   CLINC. Uses more TRAIN labels; never label-free; never evidence for a construction (S1).

## 4. Revised wording drafts (THE AUTHOR'S DECISION)

**D2 (SQ2 instrument and v2 reference policy).** v2 text unchanged (no new SQ2 evidence): "SQ2's content-closed claims
are stated under the v2 recipe: judge grok-4-1-fast-non-reasoning, dual order, TIE on flip; reference the cached
grok-4-1-fast-reasoning solve where one exists (class ONE), none otherwise (class NONE), on pv2_41dbd3dbcd399df0. Every
fidelity figure by reference class, in conventions A and B, and, where a key exists, conditional on the reference's
correctness. Whether the judge's own solve status matters under a right reference is not determined at n 414. STACK-v2
numbers stay id-disjoint only or [P-FAM] history." It still gates RP19 (N1 on NONE, the research-lead's recommendation).

**D6 (SQ3 wording).** "On content-closed splits, TRAIN-only trees give reproducible, order-stable cell addresses.
- Filing by flat leaf beats descent: +9.4pp on the anchored union tree; +7.3 / +7.7pp on label-free intent trees.
- On MASSIVE and CLINC a label-free tree partitions equivalently to k-means at matched k, [WEAKENED 2026-10-04 by the testing-logic review, claim 6 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): true at the fine gold level and at leaf k only; nothing about the hierarchy (T-C2 is the only hierarchy readout: one corpus, interval only); add 'at the leaf level, against fine gold' (D6 is the author's)] holds addresses as well
  under slot swaps, and abstains on out-of-scope CLINC queries within 0.010 AUROC of k-means (0.005 below it). It does
  not reach one supervised centroid per class. [CORRECTED 2026-10-04 by INTENT-TRANSFER-S1 (registrar; docs/reviews/AUDIT_results_drafts_2026-10-04.md, 7fbc2692; POSTRUN_intent_s1 W-4, 24f0b00d): stated backwards: the label-free tree's coarse filing (0.872 / 0.941) lies BELOW the label-conditioned per-class prototypes (0.908 / 0.982) and AT OR ABOVE one supervised centroid per class (0.867 / 0.855); never 'the tree files below an unsupervised comparator']
- An anchored tree routes the union roster as declared labels do (+2.62 vs +2.67pp; the difference is not shown); [WEAKENED 2026-10-04 by the testing-logic review, claim 4 (registrar; docs/literature/2026-10-04_testing_logic_review.md (bd5ca001); no verdict changes; docs/judge_v2_program.md L24259-L24263 (registrar's record; _as_of the commit that writes it, parent bd5ca001)): near-tautological: depth-2 is the declared class; add 'by construction' or drop it from the evidence list (D6 is the author's)] a
  label-free tree routes thinly above the best single model (+1.52pp) and short of declared labels (-1.15pp).
- The certificate certifies none of the tree's 60 sites. It certifies declared 14-category structure at the root and
  at depth-1 sizes, so non-certification is not n alone; its sensitivity to two-way structure inside a category is
  not known.
- Re-estimating anchored leaf means on declared classes helps on MMLU-Pro and hurts on CLINC.
- Online, addresses stay stable only with frozen means, and online filing of a new source trails a rebuild by 3.9pp."
Forbidden, as in v2: "label-free" for anchored trees, "deterministic", "converged", "parity", "purer than flat
clustering", "the certificate is validated at depth 1". New: "the tree catches new domains", "escalation helps",
and "ids are immutable" without "with frozen means".

## 5. Draft leads awaiting the author

- **FITSET stage 1** (anchorFitSet flag + A-gt construction; replicates as split re-draws). Research-lead view:
  **decline for now.** FITSET-INTENT confines the stage-0 gain to MMLU-Pro and shows a loss on CLINC, so a build would
  test an MMLU-specific, label-using effect. Reopen only if the thesis needs an MMLU-Pro filing claim.
- **CERT-PC-K2-KNOWN** (draft, prog L23998): two distinct declared categories merged into one site, subsampled to
  n 486 / 441, as a k = 2 control of known strength. Zero calls, CPU about 1 h (unpriced). Research-lead view: **worth
  registering**; it is the only route from change 10's "unknown" to a measured sensitivity. Its Support must show the
  merged pair's full-n statistic clears its null by more than the subsampling SD, or it repeats CERT-PC-K2's failure.
- **ONLINE-REPLAY stage 2 with a calibrated threshold** (unregistered): frozen means; threshold set on GATE for a
  target catch rate; buffer, split proposal and a site null on the buffer (machine time, rule 7). Research-lead view:
  the threshold calibration (CPU, zero builds) can go first; the certified-split leg waits on CERT-PC-K2-KNOWN, because
  a buffer split is exactly the k = 2 case whose certificate sensitivity is unknown.

## What this memo does NOT show

- That any [LF] cell set routes as well as [DECL]; or that trees beat or lose to clustering. Every tree-vs-k-means
  result is one draw and one embedder, and EQUIVALENT means within a stated delta, never "equal" or "better".
- That T-C1b or G13 are method losses: their comparators are [LC] (cross).
- Abstention on real traffic, on capability text at a usable threshold, or on corpora other than CLINC.
- That escalation helps, or that it has no effect (RC1 UNDETERMINED; the interval is almost wholly positive).
- That the online design (change 8) works: frozen means plus buffering were never run as a policy; no split certified.
- The certificate's k = 2 power, or a certificate of any tree site.
- That fit-set refits help outside MMLU-Pro or on an [LF] tree, or that a construction would gain.
- An embedder ranking; anything about gemma before GEMMA-OWN-BAR; the nomic magnitude across draws.
- Anything new for SQ2 or SQ4.

## Decisions that are the author's

The section 1 framing; D2 (gates RP19); D6 and its new forbidden words; whether changes 1, 4, 5, 6, 8, 9, 10 and 11
enter FRAMEWORK.md as design of record; FITSET stage 1; the CERT-PC-K2-KNOWN go and any online stage 2; D3. The
research-lead's own calls: the section 3 ranking, the "safe" qualifier on change 9, and the section 5 views.

Record notes (nothing edited): `docs/literature/2026-10-03_tree_uses.md` section 0 P5 still says tree cells are pending,
and section 2 predicts zero churn and "ids are immutable"; OOS-TREE-CELLS and F-OL supersede both.
