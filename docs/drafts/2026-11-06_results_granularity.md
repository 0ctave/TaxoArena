# Granularity and hierarchy: the audit, not the builder (draft results section)

<!-- DRAFT for D-2026-11-06-1 item (2) (docs/agents/author_decisions/2026-11-06.md): "a draft results section on
tests 1-3 and flat vs tree, quoted from the record, zero model calls, nothing in report/ touched".
Written 2026-11-06 by the science writer; records read at HEAD b57abcb4 (the session's git snapshot); ledger v430.
Every figure is copied, never re-derived, from a results record (docs/agents/results/<ID>.json), its POSTRUN review
(docs/reviews/POSTRUN_<ID>.md) or a programme span (docs/judge_v2_program.md, "prog"); the registered background rows
also cite docs/test_ledger.html (the last bracket wins). The number-to-source list is at the end, then the list of
sentences left out because no record carries them.
Conventions: "held-out" in a source record is written "out-of-fold" here wherever the split is not content-closed
(CONTEXT rule 12); it stays "held-out" only for TREE-CUT-GRANULARITY, whose splits are content-closed under CK-CLOSE-v1.
Units: the meter's G and C1 are in 10^-3 nats per cell; SKILL-BACKOFF's D is in 10^-3 nats of log-loss per (item, model)
cell; routing differences are in percentage points (pp). No em-dashes; one sentence per line, as README.md. -->
<!-- REVISED 2026-11-06 for lead #2 WRITEUP-AUDIT-NOT-BUILDER: D-2026-11-06-3 item (1) ("Write-up angle (#2)"; meaning as
worded: "revise the new draft: the contribution is the audit, not the tree builder; no computing"), angle of
docs/agents/plans/2026-11-06_leads.md section "### 2. WRITEUP-AUDIT-NOT-BUILDER (rank 2)" (b42d58ef). Records re-read at
the session's git snapshot b42c3300; ledger v430. Changes: the title; a two-sentence lead; section 1 (the author's
TaxoAdapt question, verbatim); section 8 rewritten (the granularity answer, the audit and the builder, two companion
sentences, the TaxoAdapt answer); section 9 (bullets added and one replaced); both lists at the end extended. Sections 2 to
7 are unchanged: no number moved, no qualifier dropped. The words of the framing (SQ3) are not restated. -->

This section reports exploratory WORK-row tests of granularity and hierarchy, and the registered rows behind them.
Section 8 draws one reading from them: the contribution is the audit, and the hierarchy builder it audits is replaceable.
<!-- src: D-2026-11-06-3 item (1); leads file section 2 (the angle); the reading is stated once, in section 8, with its
qualifiers -->

## Status of this evidence

Every result in sections 4 to 7 is exploratory.
Each test committed its plan before its first statistic, was reviewed adversarially and was recorded by the registrar, but none was registered and none has a ledger row.
They read only WORK rows: the WORK side of the BZ-METER split for MATH (2,949 items x 69 models), MMLU-Pro (7,197 x 23) and MMLU (8,425 x 79), and the WORK side of BBH's own sealed split (3,457 items x a seeded 128 of 342 models).
No test read a reserved response: the meter's reserved side stays closed (D-2026-10-20-4: no further opening of it), and BBH's RESERVED responses were read 0 times.
The partitions were built on the text of all items, the reserved items' text included, exactly as the tree's own construction read it.
The record calls the meter's reserved side not content-closed, so nothing in sections 4 to 7 is called held-out.
Every test made zero model calls.
The fresh-data test that would confirm or overturn the flat-vs-tree reading, BZ-AXIS-CONFIRM-FRESH, was drafted and never registered; the author paused it on 2026-11-01 and kept its preparation.
The registered tests in section 2 are background; each carries its own split word, corpus and roster.
<!-- src: FLAT-COMPARE.json, NEST-METER.json, BBH-HIER.json, SKILL-BACKOFF.json: registration.commit "none (exploratory, not
registered)", plan commits before any statistic, review files, "ledger": null, run.calls 0, run.pool (WORK rows; RESERVED /
vault responses read 0; partitions read all items' TEXT); BBH-WORK.json run.pool (seeded 128 of 342; text of all 5,761
items read); POSTRUN_FLAT-COMPARE row 11 ("vault items' text included, exactly as V0's own construction did");
BZ-METER-AXIS.json run.pool ("BZ-METER reserved 40% vault ... not content-closed"); prog L25712 (D-2026-10-20-4 "no
further opening of the BZ-METER reserved side"); prog L25870 (BZ-AXIS-CONFIRM-FRESH PAUSED per D-2026-11-01-1; still
drafted, NOT registered; nothing lost) -->

## 1. The question

On 2026-11-02 the author asked whether the tree still has a reason to exist for granularity even if flat clustering beats it.
The main session answered from the record and noted that the tree and a nested k-means hierarchy had never been compared on the meter.
It proposed three zero-call WORK-row tests: (1) the tree cut against nested and flat k-means at matched cell counts, at every level; (2) per-cell skill estimates with and without back-off; (3) recovery of BBH's known hierarchy (family, subtask, 3/5/7 variant).
The author replied with a second question, verbatim: "Would also this logic have sense in a more general clusterring method, like show in the TaxoAdapt paper on the scientific litterature ?"
The main session answered it in chat; section 8 answers it from the record.
The author started tests 1 and 3 that day (D-2026-11-02-1) and test 2 on 2026-11-03 (D-2026-11-03-1).
<!-- src: docs/agents/author_decisions/2026-11-02.md (D-2026-11-02-1 Context, Author's words verbatim, Read as: "The
TaxoAdapt question is answered in chat (no action)"); prog L25866 (the same words, verbatim); prog L25875
(D-2026-11-03-1, "Yes, run it (Recommended)", test 2 of D-2026-11-02-1) -->

## 2. What the record held before the tests (rows in the ledger)

The first item reads the axis_v1 leaves, the recipe of V0 in sections 4 to 7.
The other trees in this section are different objects: anchor-free MMLU-Pro re-draws and the federated union tree AF-U, all on qwen3.
<!-- src: prog L25702 (V0 = the pinned axis_v1 seed-0 MATH pickle); POSTRUN_FLAT-COMPARE row 3 (MATH G(V0|L2) 0.12405 SE
0.03497 reproduces the record); ledger TREE-CUT-GRANULARITY, NESTING, STABILITY-VS-KMEANS (anchor-free MMLU-Pro re-draw
trees, qwen3), TREE-BACKOFF, HIER-FAIR-BACKOFF, UNION-AF-ROUTE (AF-U, federated per source) -->

- `BZ-METER-AXIS` and `BZ-GRANULARITY-WORK`: finer cells carry signal on MATH, not on MMLU-Pro.
  On the meter's reserved 40% (its third opening; not content-closed), the MATH axis leaves add a gain over subject x level that reads SUPPORTED, qualified: g +0.2588, SE 0.0628, with a 3-SE lower bound of +0.070, below delta_min 0.10 (1,960 scored items x 69 models; leaves built on all items' text).
  The word is read on the meter SE, as registered; a projection with transported SE factors, not a measurement, puts its z at 2.42-3.78 under a cell-aware SE, so it is not settled on which side of 3 SE it falls, and the word stands.
  <!-- src: prog L25486 bracket [PROJECTION 2026-11-07 by the registrar (D-2026-11-06-3 (2))] ("a PROJECTION, NOT A
  MEASUREMENT"; 2.99 / 2.50 / 2.42 and 3.78-3.03; "The word SUPPORTED, its chip and the sentence of record stand");
  added by the main session after the bracket landed (79ef14a7) -->
  On MMLU-Pro the same read is NOT SUPPORTED (powered): g -0.0059, SE 0.0183, MDE80 0.0703 (4,654 items x 23 models).
  On WORK the MATH leaves add +0.124 (SE 0.035) over subject x level, peak at depth 4 (+0.15, SE 0.036), and keep +0.109 (SE 0.032) after difficulty and length controls (exploratory).
  <!-- src: ledger BZ-METER-AXIS (chips "MATH SUPPORTED, QUALIFIED (Q1, Q2)", "MMLU-Pro NOT SUPPORTED (powered)"; observed
  cell); BZ-METER-AXIS.json sentence_of_record; ledger BZ-GRANULARITY-WORK (chip "EXPLORATORY (WORK only)"; observed
  cell); BZ-GRANULARITY-WORK.json A1-A3 -->
- `NESTING`: only a hierarchy nests.
  Flat spherical k-means fitted separately at a coarse and at a fine cell count do not nest: NON-NESTED in 6 of 6 tree-depth cells, V90 0.3807-0.6592 over 30 seed values against a bar of 0.10 (fit sets of three MMLU-Pro re-draws, TRAIN only).
  The record calls this a property, not a value; the tree and bisecting k-means nest by construction.
  <!-- src: ledger NESTING (chip "VALID (POST-RUN 37672103): NV NON-NESTED 6/6; F-NV NOT FIRED"; OUTCOME bracket "A property,
  not a value"; identity check); NESTING.json -->
- `TREE-CUT-GRANULARITY`: as partitions, the anchor-free tree's cuts are worse than flat k-means of the same size.
  On three MMLU-Pro re-draw trees, content-closed under CK-CLOSE-v1, the tree cut at each depth is a worse held-out partition than flat spherical k-means with the same cell count: depth-averaged purity differences -0.0298 [-0.0383, -0.0209], -0.0263 [-0.0343, -0.0189] and -0.0315 [-0.0397, -0.0229] (held-out 3,598 / 3,522 / 3,500 items; purity scored by the labels).
  The same record does not show that k-means is a better taxonomy, because flat k-means does not nest.
  <!-- src: ledger TREE-CUT-GRANULARITY (chips "VALID (POST-RUN 37672103): TC CUT-WORSE 3/3", "W-4 ... ONE RECIPE, MMLU-PRO,
  QWEN3"; OUTCOME bracket); TREE-CUT-GRANULARITY.json sentence_of_record, does_not_show -->
- `STABILITY-VS-KMEANS`: bisecting k-means is as stable as the trees.
  On the 2,772 common items of four anchor-free MMLU-Pro re-draws, the trees are as stable as bisecting spherical k-means at matched data, leaf count and shape, not more (ST1 NEITHER; F-ST FIRED).
  Their edge on triplets resolved in both hierarchies holds only where the trees resolve: they leave about 12% of triplets unresolved, against 0.1% for k-means.
  Three of the four re-draw splits are id-disjoint only.
  <!-- src: ledger STABILITY-VS-KMEANS (chips; OUTCOME bracket "about 12% unresolved vs 0.1%"); STABILITY-VS-KMEANS.json
  does_not_show "content-closed re-draws (three id-only)"; docs/agents/KNOWLEDGE.md section 1 (pd610c9a, p19d9f47, p8a29
  id-disjoint only) -->
- `TREE-BACKOFF` and `HIER-FAIR-BACKOFF`: a k-means hierarchy routes at least as well as the tree's.
  On the content-closed v2 union split, back-off of AF-U's leaf accuracies toward their ancestors routed EVAL +0.90pp better than AF-U's flat leaves, marginally: two-stage 95% [+0.03, +1.76]pp, the percentile interval reaches 0, and tau 100 beat tau 200 by one GATE item (5,907 items / 5,404 components; 18 models; key-scored accuracy, so no judge tie convention applies; every arm source-conditioned [SC]).
  Under TRAIN cross-validation, back-off over a shape-matched spherical k-means hierarchy then routed 0.53pp better than back-off over AF-U (95% [-0.944, -0.106]pp; 11,841 items / 10,781 components).
  That sign word is DESCRIPTIVE-ONLY by Support (0.53pp below the measured MDE80 of 0.61pp), parity is refuted, and the TRAIN leg re-reads the pilot's items, so it is not an independent replication.
  On EVAL, tree minus k-means back-off reads +0.29pp [-0.42, +0.99], NEITHER (descriptive).
  The record withdrew "the tree's hierarchy routes better".
  <!-- src: ledger TREE-BACKOFF (chips "VALID (POST-RUN 9be0e7c3): BO1 HIERARCHY-HELPS (marginal) [SC]", "W-1..W-4 ...";
  OUTCOME bracket incl. "W-4: all arms [SC], key-scored"; scope cell "18 models"); ledger HIER-FAIR-BACKOFF (chips "VALID
  (POST-RUN 37672103): PARITY REFUTED (SCOREABLE); HB2 NEITHER", "HB1 KMEANS-BETTER, DESCRIPTIVE-ONLY BY SUPPORT (W-1:
  0.53pp < MDE80 0.61pp); F-HB FIRES: 'THE TREE'S HIERARCHY ROUTES BETTER' WITHDRAWN; TRAIN-CV, NOT AN INDEPENDENT
  REPLICATION; EVAL NEITHER"; OUTCOME bracket) -->
- `UNION-AF-ROUTE`: on the union, the anchor-free tree is not shown better than per-source k-means.
  Against per-source k-means at matched cell counts its routing difference is -0.45pp [-1.31, +0.41], so the tree is not shown better (5,907 items / 5,404 components).
  On filing, falsifier F-AK fires: the tree is not better than unsupervised per-source k-means at matched k beyond its seed spread, under the mirrored filing fixed before the data; under the registered rule it would miss by 0.0002.
  Against declared labels the tree's cells fall short by -1.15pp [-2.19, -0.12], a measured shortfall (descriptive), never parity.
  The cells are source-conditioned [SC], not label-free; one draw, one roster.
  <!-- src: README.md L145-L151 (quoted); ledger UNION-AF-ROUTE (chips "VALID (POST-RUN 589c04ae): U1 HELD (THIN); F-AK
  FIRES (MIRRORED FILING)", "U3b SHORTFALL -1.15pp VS DECLARED, NEVER PARITY; ... F-AK MISSES BY 0.0002 UNDER THE
  REGISTERED RULE (Q1)"; CORRECTED 2026-10-04 bracket [SC]) -->

## 3. Objects, the meter and the word rules

V0 is the axis tree that the meter tests read: the full axis_v1-recipe tree, with no depth chosen on responses, read on the 512-d prefix of the qwen3 text embedding.
Its depth-1 nodes are the declared categories, called the anchors: 7 on MATH, 14 on MMLU-Pro, 17 on MMLU and 24 on BBH, where V0 is anchored on the subtasks.
Its leaf counts are 36 on MATH, 80 on MMLU-Pro, 100 on MMLU and 40 on BBH.
K (called KF in test 1) is flat spherical k-means inside each anchor, at V0's leaf count in that anchor, on the same 512-d vectors, with 5 partition seeds.
BKM-A is bisecting k-means inside each anchor, so its cells nest across levels; BKM is bisecting k-means that ignores the anchors.
RND is random cells with the tree's per-anchor sizes.
N is the meter's text-kNN field reader: the shrunk pooled residual of the 40 nearest training rows of the same category, read on the 4,096-d vectors; it is a soft reader, not a partition.
<!-- src: prog L25695 (V0 = the full axis_v1-recipe tree, no depth chosen on responses); prog L25696 (K: within each anchor,
V0's depth-1 node; spherical k-means on the 512-d MRL prefix renormalised at k_a = V0's leaf count; seeds 0..4; N: K = 40
nearest TRAINING rows of the same category, cosine on the 4096-d unit rows); prog L25697 ("N reads 4096-d vectors, V0 and K
the 512-d prefix"); NEST-METER.json numbers_of_record "levels" (A = 7 / 14 / 17 / 24; L = 36 / 80 / 100 / 40); BBH-HIER.json
("the subtask-anchored V0"; fits "V0 40 ... leaves"); POSTRUN_NEST-METER row 3 (BKM-A nested inside anchors, BKM crosses
anchors, KF not nested); EMBED2-WORK.json D2 ("the soft text field") -->

The meter scores a reader X by G(X | parent), the predictive information X adds over a parent on responses of the test fold, cross-fitted on WORK with 5 content-grouped folds x 5 seeds.
The criterion of this section is C1(X) = G(X | L2 + difficulty + length): the gain beyond the declared finer label (L2; on MATH, subject x level), per-model difficulty deciles and length deciles.
Two standard errors appear.
The meter SE is clustered by content cluster; it is practically item-iid and ignores the dependence that shared estimated cell offsets induce among items of one cell.
Clustering by V0 leaf (SE_leaf) inflated FLAT-COMPARE's SEs by x1.3-1.8.
On planted MATH data the meter SE understated the replicate spread by x1.38-1.65 at C1 0.10 (9 degeneracy-free pairs; a one-fold-seed meter).
Two tau rules appear: f2, the meter's factor-2 grid, and cont, every tau^2 chosen continuously on its own criterion.
<!-- src: BZ-METER-AXIS.json question ("held-out predictive information over subject x declared finer label (L2)"; the
record's "held-out" written "out-of-fold" here); BZ-GRANULARITY-WORK.json sentence_of_record (5 content-grouped folds x 5
seeds); prog L25698 (C1(arm) = G(arm | L2 + diff + len), L2 = subject x level, per-model difficulty deciles then length
deciles); POSTRUN_FLAT-COMPARE D2 (content-cluster SE practically item-iid; leaf clustering x1.3-1.8); prog L25754 and
L25756 note (b) (PLANTED-POWER: x1.38-1.65 at C1 0.10, 9 degeneracy-free pairs, one-fold-seed meter); TAU-CONT-ALL.json
title and bracket ("S-TAU's factor-2 grid"; "every tau^2 chosen continuously on its own S-TAU criterion") -->

## 4. Flat vs tree at the leaves (FLAT-COMPARE and the records after it)

Table 1. C1 by arm on WORK rows (10^-3 nats per cell; SE in brackets where the record prints it).

| corpus (items x models) | V0 | K | RND | N |
|---|---|---|---|---|
| MATH (2,949 x 69) | +0.1093 (0.0316) | +0.2745 (0.0462) | -0.0053 | +0.3499 (0.0596) |
| MMLU (8,425 x 79) | +0.0435 | +0.0521 | -0.0004 | +0.1064 |
| MMLU-Pro (7,197 x 23) | -0.0095 | +0.0022 | -0.0056 | +0.0689 |
| BBH (3,457 x 128) | +0.0845 (0.0722) | +0.0719 (0.0621) | +0.0118 (0.0385) | +2.4758 (0.3901) |

<!-- src: POSTRUN_FLAT-COMPARE row 4 (MATH, MMLU, MMLU-Pro points); prog L25700 (MATH SEs: PF5 C1(V0) +0.1093 (0.0316),
PF6 C1(K) +0.2745 (0.0462), PF7 C1(N) +0.3499 (0.0596)); BBH-WORK.json numbers_of_record "C1 of the arms" (POSTRUN_BBH-WORK
row 8) -->

Table 2. The flat-vs-tree contrasts (content-cluster SE in brackets).

| contrast | MATH | MMLU | MMLU-Pro | BBH |
|---|---|---|---|---|
| V0 - K | -0.1652 (0.0358), z -4.61 | -0.0085 (0.0147), z -0.58 | a tie (0.8 SE) | +0.0126 (0.0528) |
| N - V0 | +0.2406, z 4.44 | +0.0629, z 2.97 | +0.0784, z 2.40 | not printed |
| V0 - RND | +0.1146 (0.0316), 3.63 SE | +0.0439 (0.0180), 2.44 SE | -0.0039 (0.0197) | +0.0727 (0.0775) |
| V0 - RND under SE_leaf | 2.02 SE | 1.51 SE | - | - |
| V0 - K under SE_leaf | z -3.41 (f2), -2.98 (cont) | - | - | - |

<!-- src: POSTRUN_FLAT-COMPARE rows 5, 7, 14 and D2; FLAT-COMPARE.json numbers_of_record (K1, L3k - V0, V0 vs random) and
the 2026-10-28 bracket (TAU-CONT-ALL C1: z -3.41 f2 / -2.98 cont under V0-leaf clustering); BBH-WORK.json K1 and "V0 vs
random" -->

On MATH and MMLU, flat within-anchor k-means at V0's resolution, on the same 512-d vectors, predicts at least as well as the tree after the controls, and better on MATH.
The wording of record is: k-means reaches V0 on MMLU (-0.0085, SE 0.0147) and beats it on MATH (-0.165, 4.6 SE); the text-kNN field beats V0 on all three.
The MATH margin depends on the SE convention: under V0-leaf clustering it reads z -3.41 under f2 and z -2.98 under cont, against -4.612 and -4.067 under the content-cluster SE.
It also depends on the embedder: rebuilt on embeddinggemma, the k-means lead on MATH shrinks to -0.0363 (SE 0.0279), z -1.30, so the record prints ORDERING NOT INVARIANT (moves: MATH V0 - K).
Under the continuous tau rule the signs and the arms' C1 rank order on MATH and MMLU stand: ORDERING STANDS (content-cluster SE; under V0-leaf SE the MATH V0 - K status flips, marginal; signs and C1 rank order unchanged under both).
On MMLU-Pro, V0's own C1 is -0.0095, and no reading goes beyond descriptive.
On BBH, V0's C1 is NOT SHOWN AT 3 SE (+0.0845, SE 0.0722, z 1.17; realised MDE80 0.2775), and k-means reaches it.
The selection favours V0: TREE-VARIANTS retained V0 on these same WORK items.
<!-- src: POSTRUN_FLAT-COMPARE "What the result licenses" (first bullet) and D1; FLAT-COMPARE.json sentence_of_record ("WORK
favours V0 (TREE-VARIANTS selection)") and 2026-10-28 bracket; EMBED2-WORK.json R2 and sentence_of_record; TAU-CONT-ALL.json
sentence_of_record (ORDERING STANDS, quoted per its C1 bracket); POSTRUN_FLAT-COMPARE "Does not license" ("Any MMLU-Pro reading
beyond descriptive (V0's own C1 there is -0.0095)"); BBH-WORK.json R1, K1 -->

Against size-matched random cells, the leaves carry text structure on MATH at 3.63 SE, and at 2.02 SE under leaf clustering.
On MMLU the same word (2.44 SE) is quoted only with its sensitivity: under leaf clustering it falls to 1.51 SE, which would read NOT DISTINGUISHABLE.
On MMLU-Pro the comparison is NOT DISTINGUISHABLE (UNDERPOWERED), and on BBH NOT DISTINGUISHABLE FROM SIZE ALONE (UNDERPOWERED; MDE80 0.2204 above C1(V0)).
<!-- src: FLAT-COMPARE.json "V0 vs random" and the D2 bracket; review.verdict ("MMLU-Pro NOT DISTINGUISHABLE (UNDERPOWERED)");
BBH-WORK.json "V0 vs random" -->

The text-kNN field carries V0's information on MATH: V0's residual beyond the field is +0.0067, with a 95% upper bound of +0.027.
On MMLU, V0 keeps a residual of +0.0165 (1.56 SE) beyond the field.
The field reads 4,096-d vectors and V0 the 512-d prefix, so the field's lead is not attributed to method rather than to dimension.
On embeddinggemma the field's lead over the tree holds on MATH; on MMLU it is not established.
On BBH the field's gain beyond the tree, +2.3142 (SE 0.3885), is quoted only as: K2 KILLED on BBH (content-cluster SE, the plan's; arm A is 1.74 SE clustered by subtask and 1.87 by V0 leaf; geometric_shapes, disambiguation_qa and boolean_expressions carry 83% of N's gain; on the other 21 subtasks G(N|L2+V0) +0.29 (0.32)).
FLAT-COMPARE did not test k-means at its own best k.
<!-- src: POSTRUN_FLAT-COMPARE "What the result licenses" (bullets 2, 3) and "Does not license" (4096-d vs 512-d; k-means at
its own best k); FLAT-COMPARE.json "K2 MATH" (arm B +0.0067 (0.0102; 95% upper +0.027)); EMBED2-WORK.json bracket D2 ("the
soft text field beats the tree" is embedder-robust on MATH; on MMLU under gemma the lead is not established); BBH-WORK.json
K2 (C1 HIGH bracket wording) -->

## 5. Matched granularity at every level (NEST-METER, test 1)

Test 1 compared the tree cut, nested bisecting k-means inside the anchors (BKM-A) and flat k-means inside the anchors (KF), each at the tree's own per-anchor cell count at every level.
The levels were MATH 7 / 14 / 25 / 36 cells, MMLU-Pro 14 / 28 / 51 / 80, MMLU 17 / 33 / 58 / 100 and BBH 24 / 40 (A / B / C / L, A being the anchors).
On WORK rows every arm has exactly its level's cell count in every seed; BKM-A nests across levels inside the anchors, and KF does not nest on MATH, MMLU-Pro and MMLU (on BBH's two levels it nests trivially).
Words are printed at 3 SE_leaf under the cont rule; at the anchors the arms are identical by construction.
<!-- src: NEST-METER.json question, numbers_of_record "levels", "words"; POSTRUN_NEST-METER rows 2, 3 -->

Table 3. Contrasts at matched granularity (10^-3 nats per cell; D (SE_leaf), z where the record prints it).

| corpus | level (cells) | D_nest = BKM-A - TREE | D_flat = KF - TREE | D_cost = KF - BKM-A | word (all three) |
|---|---|---|---|---|---|
| MATH | B (14) | +0.0047 (0.0107), z 0.44 | +0.0016 (0.0099), z 0.16 | -0.0031 (0.0030), z -1.02 | NEITHER |
| MATH | C (25) | +0.0531 (0.0332), z 1.60 | +0.1037 (0.0426), z 2.43 | +0.0506 (0.0292), z 1.74 | NEITHER |
| MATH | L (36) | +0.0813 (0.0409), z 1.98 | +0.1540 (0.0518), z 2.98 | +0.0728 (0.0374), z 1.94 | NEITHER |
| MMLU-Pro | B (28) | +0.0022 (0.0019) | +0.0012 (0.0018) | -0.0010 (0.0007) | NEITHER |
| MMLU-Pro | C (51) | +0.0194 (0.0135) | +0.0114 (0.0110) | -0.0080 (0.0141) | NEITHER (UNDERPOWERED) |
| MMLU-Pro | L (80) | +0.0238 (0.0166) | +0.0082 (0.0128) | -0.0157 (0.0192) | NEITHER (UNDERPOWERED) |
| BBH | L (40) | -0.0058 (0.0602) | -0.0037 (0.0642) | +0.0021 (0.0362) | NEITHER (UNDERPOWERED) |
| MMLU | B (33) | +0.0033 (0.0054) | +0.0019 (0.0056) | -0.0015 (0.0022) | NEITHER |
| MMLU | C (58) | -0.0138 (0.0179) | -0.0237 (0.0190) | -0.0099 (0.0144) | NEITHER (UNDERPOWERED) |
| MMLU | L (100) | +0.0055 (0.0126) | +0.0057 (0.0132) | +0.0002 (0.0145) | NEITHER (UNDERPOWERED) |

<!-- src: NEST-METER.json numbers_of_record (MATH, MMLU-Pro, BBH, MMLU rows; "words": 15 of 30 UNDERPOWERED in MMLU-Pro C, L;
BBH L; MMLU C, L); POSTRUN_NEST-METER rows 5, 6 -->

No contrast among the tree cut, nested bisecting k-means and flat k-means separates at 3 SE_leaf at any level, on any of the four corpora.
In the reviewer's words: a nested k-means hierarchy is not detectably worse than the tree at any level, and the price of nesting relative to flat k-means is not detected.
The nulls are bounded by power: MDE80 is 0.012-0.199 on MATH, 0.003-0.074 on MMLU-Pro, 0.008-0.073 on MMLU and 0.139-0.247 on BBH, and the D_cost MDE80s are lower bounds.
Fifteen of the 30 contrasts below the anchors are flagged UNDERPOWERED.
The largest, MATH L D_flat, reads NEITHER at z 2.98 (reproduced): it reproduces TAU-CONT-ALL and is not new evidence.
Under the meter SE, MATH C D_flat (z 3.07), L D_nest (z 3.18) and L D_flat (z 4.07) would read BETTER, and under f2 MATH L D_flat reads z 3.41; these are printed beside and never decide.
<!-- src: POSTRUN_NEST-METER "What the result licenses"; NEST-METER.json "support" (MDE80 ranges; D_cost MDE80s lower bounds,
Q5), "largest z" (Q3), "beside, never the word" (Q4 values) -->

Two reviewer qualifiers of MEDIUM severity travel with this result.
Q1: the predictions scored on point estimates rest on noise-level margins, so the share of flat k-means' MATH lead that survives nesting is 0.53 with an SE of about 0.19, even holding D_flat fixed, and D_flat itself is z 2.98.
Q2: one reviewer mutant (the SE grouping in part_stats switched to content clusters) survives the selftest and would flip three MATH words to BETTER; the run itself is unaffected, and a selftest fix is owed without a rerun.
The prediction that the anchors help nested k-means on MATH at the leaves failed by point estimate, at noise level: C1(BKM-A) +0.1974 against C1(BKM) +0.2340 (D -0.0366, SE 0.0642, z -0.57).
<!-- src: NEST-METER.json brackets (Q1, Q2 MEDIUM), sentence_of_record; predictions P5 (FAILED); POSTRUN_NEST-METER Q1, Q2 and
own-mutant N2 -->

## 6. A known hierarchy: BBH (BBH-HIER, test 3)

Test 3 asked whether any hierarchy recovers BBH's known structure (20 families, 24 subtasks, and the 3/5/7 variant inside the two merged families) from item text alone.
It read the 3,457 WORK items' text on the qwen3 512-d prefix and no response.
The hierarchies were the anchor-free axis tree AF, bisecting k-means BKM, bisecting inside the families BKMA, average-link KAL and Ward KWD on 96 k-means centroids, and the record trees V0 (anchored on the 24 subtasks) and V0m (anchored on the 20 families, the two variant families merged); flat k-means stood beside.
<!-- src: BBH-HIER.json title, question, run.pool; numbers_of_record "fits (WORK rows)"; POSTRUN_BBH-HIER Q6 ("V0 / V0m / BKMA
have it by construction"); BBH-WORK.json predictions PB1, PB8 ("2 merged anchors"; "the merged anchors' WORK items") -->

Table 4. Best-cut AMI against the gold levels (seed means; bootstrap SD in brackets; 3,457 items, 2,662 content clusters, n_eff 783).

| hierarchy (leaves) | G1: 20 families | G2: 24 subtasks |
|---|---|---|
| AF, anchor-free axis tree (22) | 0.9305 (0.0049) | 0.8855 (0.0089) |
| BKM, bisecting k-means (96) | 0.9605 (0.0020) | 0.9147 (0.0064) |
| KAL, average-link on 96 centroids (96) | 1.0000 (0.0000) | 0.9517 (0.0045) |
| KWD, Ward on 96 centroids (96) | 0.9837 (0.0008) | 0.9363 (0.0046) |
| BKMA, bisecting inside the families (82) | by construction | 0.9517 (0.0045) |
| V0m, record tree (41) | by construction | 0.9517 (0.0045) |
| V0, record tree (40) | by construction | by construction |
| FLAT, best single k-means fit, not nested | 0.9736 (0.0008) | 0.9265 (0.0041) |
| variant-blind ceiling AMI(G1, G2) | - | 0.9517 |

<!-- src: BBH-HIER.json numbers_of_record "best-cut AMI G1 / G2", "fits (WORK rows)"; POSTRUN_BBH-HIER rows 2, 4 -->

Every anchor-free hierarchy tried (AF, BKM, KAL, KWD) recovers the 20 families at some cut, with AMI 0.93-1.00; V0, V0m and BKMA have the family level by construction.
At the node level (DP and HF), every hierarchy not anchored at a level sits above the p97.5 of 200 matched-shape random trees, at G1 and at G2.
The subtask level is reached by variant-blind partitions (V0m, BKMA and KAL exactly at the 0.9517 ceiling), so it is never read as recovering the subtasks.
No node of any hierarchy other than the subtask-anchored V0 is a variant: HF against the variant is 0.500 in both merged families, the family node alone.
The record's word is ANY HIERARCHY SEPARATES 3/5/7 IN BOTH MERGED FAMILIES: NO.
BKMA reads IN ONE (tracking_shuffled_objects 0.5031 at depth 6, 26 cells; logical_deduction at most 0.4936, 27-28 cells; bar 0.50), quoted only with Q1 (MEDIUM): both families' depth-6 cuts are pure in the variant (homogeneity 1.000); the family difference is the cell count (26 vs 27-28), not separation.
The text orders the merged families family, then scenario, then variant: the gold's order (variant, then scenario) is not recovered as a level, and the variant appears only as a refinement beneath the scenario (BKMA G3 0.988).
<!-- src: BBH-HIER.json numbers_of_record "level words", "node level", "3/5/7", sentence_of_record and brackets (Q1, Q5, Q6);
POSTRUN_BBH-HIER "What the result licenses" (family -> scenario -> variant; BKMA G3 0.988), row 7 -->

Among the anchor-free hierarchies at their best cut, KAL ranks above KWD, KWD above BKM and BKM above AF, also at matched k 20.
The contrasts at G1 are BKM - AF +0.0300 (SE 0.0050), BKM - KWD -0.0231 (0.0049) and KWD - KAL -0.0163 (0.0026), with a realised MDE80 of 0.007-0.014.
Flat k-means' best single fit among 95 k beats BKM's best nested cut (G1 +0.0130, SE 0.0049; G2 +0.0118, SE 0.0051), quoted only that way (Q2, MEDIUM): the best k beats the median of its neighbouring k by 0.02-0.06 per seed, more than the difference itself.
At matched k, BKM is at or above flat k-means (k 20: 0.953 vs 0.936 on G1; k 24: 0.946 vs 0.942), so "flat beats nested" is not shown.
Eleven of 14 predictions held.
The result is about text, not models: BBH-WORK's meter is the response-side evidence, and V0 and V0m carry their fit on all 5,761 texts.
The plan's pre-plan scenario counts read RESERVED items' text (no response); no new fit or statistic touched a RESERVED row.
<!-- src: POSTRUN_BBH-HIER "What the result licenses" (KAL > KWD > BKM > AF, also at matched k 20), row 10 (realised MDE80
0.0070-0.0142), row 11 (matched k values), Q2, Q4; BBH-HIER.json "contrasts", "predictions" (11 of 14), brackets (Q2;
Q3-Q6, T-1), does_not_show -->

## 7. Fine cells: per-cell skill with and without back-off (SKILL-BACKOFF, test 2)

Test 2 asked whether a model's skill can be read at fine granularity, and which hierarchy makes per-cell estimates best.
It estimated per-model rates in every cell at V0's leaf granularity (test 1's level L, matched cell counts) and scored them by out-of-fold log-loss on WORK rows, with FLAT-COMPARE's folds (5 folds x 5 seeds, content-grouped, label-stratified).
The arms were the per-model label rates (LABELS), the raw leaf rates (TREE-RAW), back-off along V0's levels (TREE-BO) and along nested bisecting k-means (BKMA-BO), and shrinkage of flat KF cells (KF-BO) and of random cells (RND-BO).
One common tau per arm and task was chosen on inner folds of the training rows only.
Words are printed at 3 SE_word, the larger of the content-cluster and V0-leaf SEs; the label SE is printed beside and never decides.
<!-- src: SKILL-BACKOFF.json question, title; prog L25876 (WHAT RAN: folds, tau on inner folds, arms, words); prog L25880 Q3
("one-level shrinkage (KF-BO) with four-level shrinkage at one tau (TREE-BO)") -->

Table 5. Words of record (10^-3 nats of log-loss per (item, model) cell, first-named arm minus second, positive = first arm better; z in brackets).

| contrast | MATH | MMLU-Pro | BBH | MMLU |
|---|---|---|---|---|
| Z_bo = TREE-BO - TREE-RAW | +10.28 (6.42) BETTER | +1.17 (2.47) NEITHER | +2.57 (3.8) BETTER | +2.55 (6.2) BETTER |
| Z_hier = BKMA-BO - TREE-BO | +0.26 (1.4) NEITHER | +0.83 (1.5) NEITHER | +0.17 (0.9) NEITHER | +0.70 (0.6) NEITHER |
| MDE80 of Z_hier | 0.75 | 2.13 | 0.78 | 4.54 |
| Z_nest = KF-BO - BKMA-BO | +0.67 (2.1) NEITHER | +0.48 (0.6) NEITHER | -0.08 (-0.8) NEITHER | +2.93 (2.7) NEITHER |
| V_raw = TREE-RAW - LABELS | -10.03 (-5.8) WORSE | +9.50 (2.2) NEITHER | -2.01 (-1.8) NEITHER | +12.60 (3.84) BETTER; label SE NEITHER |
| V_tree = TREE-BO - LABELS | +0.25 (1.2) NEITHER | +10.67 (2.7) NEITHER | +0.55 (1.0) NEITHER | +15.14 (4.76) BETTER |
| V_bkma = BKMA-BO - LABELS | +0.51 (1.7) NEITHER | +11.50 (2.8) NEITHER | +0.73 (1.3) NEITHER | +15.84 (4.9) BETTER |
| V_kf = KF-BO - LABELS | +1.18 (3.4) BETTER, thin | +11.97 (3.2) BETTER, thin | +0.65 (1.2) NEITHER | +18.78 (5.4) BETTER |
| V_rnd = RND-BO - LABELS | -0.02 (-2.0) NEITHER | -0.02 (-2.4) NEITHER | -0.04 (-1.1) NEITHER | -0.02 (-1.4) NEITHER |
| B_lab = LABELS-b - LABELS | +47.3 (10.2) BETTER | +193.7 (25.5) BETTER | +109.3 (9.7) BETTER | +207.3 (35.2) BETTER |

<!-- src: SKILL-BACKOFF.json numbers_of_record (units; Z_hier; Z_bo; Z_nest; V_raw; V_tree; V_bkma; V_kf; V_rnd; B_lab); prog
L25878 (OUTCOME words, primary) -->

Shrinking per-model leaf rates toward the label predicts the test fold better than the raw leaf rates on MATH, BBH and MMLU; on MMLU-Pro the gain reads z 2.47, NEITHER.
The back-off gain is shrinkage toward the label, not the hierarchy (Q2, MEDIUM): label-only shrinkage of the tree's leaves gains at least as much as full back-off on MATH (+10.69 vs +10.28), MMLU-Pro (+1.73 vs +1.17) and BBH (equal).
On MMLU it gains less (+1.97 vs +2.55), where the tree's internal levels read +0.57 (SE_word 0.30), descriptive.
On MATH and MMLU-Pro the internal levels, shrunk at one common tau, cost by point and descriptively: TREE-BO minus label-only shrinkage reads -0.41 (SE_word 0.15) and -0.57 (0.30), and the same for BKMA reads -0.49 (0.20) and -0.59 (0.27).
Which hierarchy the estimates back off along, V0 or nested bisecting k-means, is not detected under one common tau (Z_hier NEITHER on all four), and neither is flat KF against nested BKMA (Z_nest NEITHER).
<!-- src: SKILL-BACKOFF.json sentence_of_record, brackets (Q1-Q3 MEDIUM and the registrar's note on Q2: "'label-only shrinkage
is at least Z_bo' holds on MATH (+10.69 vs +10.28), MMLU-Pro (+1.73 vs +1.17) and BBH (equal), not on MMLU (+1.97 vs +2.55;
internal levels +0.57, SE_word 0.30, descriptive"); prog L25880 (Q2 figures); POSTRUN_SKILL-BACKOFF "What the run licenses"
-->

The raw leaf rate is not a usable skill estimate on its own on MATH only (Q1, MEDIUM): there it is worse than the label rate (-10.03, z -5.8).
On MMLU it is better than the label rate (+12.60, z 3.84; the label SE beside reads NEITHER), and on MMLU-Pro and BBH it is NEITHER.
After back-off, the per-cell estimates of V0, BKMA and KF all beat the label rates on MMLU; V0's do so on no other corpus.
The flat KF cells read BETTER than the labels on MATH and MMLU-Pro, but thinly (Q3, MEDIUM): with the SE clustered by KF cell, z is 3.11 and 3.03, the label SE reads NEITHER on both, and the comparison sets one-level shrinkage against V0's four-level shrinkage at one tau, so it is not a cells comparison.
Random cells of V0's sizes carry nothing (V_rnd NEITHER on all four).
The backbone dwarfs every cell effect: adding the meter's backbone as an offset to the label rates gains +47 to +207, z 9.7 or more.
By point, back-off gains more in small leaves (fewer than 64 items) than in large ones (112 items or more) on all four corpora, descriptively; BBH's large-leaf bin is zero by construction, and the pattern holds on 3 of 3 without it.
On MMLU-Pro the realised leaf design effect for an arm against LABELS was 9.2-13.6, larger than planned; the words use the realised SEs.
Eight of 10 predictions held; the prediction that V0's per-cell estimates beat the labels on MATH failed (+0.25, SE_word 0.21, NEITHER).
The per-cell estimates enter only as predictors scored in aggregate: no per-cell board, interval or profile is published, and the closed line PROFILE-TREE-ROBUST / KEY-SUBANCHOR-SCALE is not reopened.
<!-- src: SKILL-BACKOFF.json brackets (Q1, Q3), numbers_of_record (V_tree, V_bkma, V_kf, V_rnd, B_lab, "Z_bo by size", "support"),
predictions P1 (FAILED), P7 (Q6), "8 of 10 held" (prog L25879), closed_line; prog L25880 (Q1, Q3, Q6 wording); prog L25881
(LICENSED / NOT LICENSED); prog L25876 (secondary (-b) = the meter's backbone as offset) -->

## 8. The reading: the audit is the contribution, the builder is replaceable

This section states the reading once, at the level the records license.
It adds no new measurement: every figure is copied from sections 2 to 7 or from the records it cites.
<!-- src: leads file section 2 ("state SQ3's answer once"; "Changes: no claim moves"; "Every qualifier travels") -->

### 8.1 The granularity question

The question was whether the tree keeps a reason to exist for granularity even if flat clustering beats it.
On these WORK rows (exploratory; qwen3; one roster per corpus; not confirmed on fresh items), the record detects no granularity advantage of the tree over a nested k-means hierarchy.
That is a null bounded by power, not a showing that the two are equal.
<!-- src: docs/agents/author_decisions/2026-11-02.md (the question); NEST-METER.json sentence_of_record ("a nested k-means
hierarchy is not detectably worse than the tree at any level") and does_not_show ("'equal', 'equivalent' or 'nesting is
free'"); SKILL-BACKOFF.json sentence_of_record (Z_hier NEITHER) and does_not_show ("'equal' hierarchies"); the clauses
below, each with its record -->

Granularity itself carries signal on MATH (SUPPORTED, qualified, on the reserved read), but not on MMLU-Pro (NOT SUPPORTED, powered).
Independently fitted flat k-means does not nest (NON-NESTED in 6 of 6 cells), and bisecting k-means nests by construction; the record calls nesting a property, not a value.
On MMLU-Pro re-draws, the anchor-free trees are as stable as bisecting k-means, not more.
At the tree's own cell counts, a nested k-means hierarchy is not detectably worse than the tree at any level of MATH, MMLU-Pro, MMLU or BBH, with MDE80 up to 0.199, 0.074, 0.073 and 0.247 and 15 of 30 contrasts underpowered.
How much of flat k-means' MATH lead survives nesting is not pinned down: the share is 0.53 with an SE of about 0.19, even holding D_flat fixed, and D_flat itself is z 2.98 (Q1, MEDIUM).
On BBH text, every anchor-free hierarchy tried recovers the family level, and the anchor-free axis tree has the lowest best-cut AMI among them (0.9305 on the 20 families; bisecting k-means is +0.0300 above it, SE 0.0050).
No hierarchy except the subtask-anchored V0 has a node that is a variant.
Which hierarchy per-cell estimates back off along is not detected under one common tau (Z_hier NEITHER on all four corpora; MDE80 0.75 / 2.13 / 0.78 / 4.54), and the back-off gain is shrinkage toward the label, not the hierarchy (Q2, MEDIUM).
<!-- src: ledger BZ-METER-AXIS chips; ledger NESTING chip and OUTCOME bracket ("A property, not a value"); ledger
STABILITY-VS-KMEANS (ST1 NEITHER; F-ST FIRED; "as stable ..., not more"); POSTRUN_NEST-METER "What the result licenses";
NEST-METER.json "support", "words", bracket Q1; BBH-HIER.json "best-cut AMI G1 / G2", "contrasts" (prog L25868: "D1 BKM -
AF G1 +0.0300 (0.0050) BKM HIGHER"), "3/5/7"; POSTRUN_BBH-HIER "What the result licenses" (KAL > KWD > BKM > AF);
SKILL-BACKOFF.json numbers_of_record Z_hier, bracket Q2 -->

### 8.2 The audit, not the builder

Read together, these records place the contribution in the audit rather than in the tree builder.
The audit has four parts.
- The meter asks whether a hierarchy's cells add predictive information on responses beyond the declared labels, after difficulty and length controls (C1, section 3).
- Nesting and back-off ask whether the cells nest across levels, and whether per-cell estimates gain by backing off along them (NESTING, NEST-METER, SKILL-BACKOFF).
- The certificate tests the split sites of a tree against their site nulls, the J site null at 300 reps.
- The split words: every object carries the word its content check licenses, and a side that is not content-closed is never called held-out.
<!-- src: leads file section 2 (the four parts as named there: "meter gain beyond declared labels, nesting and back-off,
the certificate, the split words"; the reading is the leads file's, adopted by D-2026-11-06-3 item (1)); prog L25698 (C1);
NESTING.json, NEST-METER.json, SKILL-BACKOFF.json questions; ledger CERT-RESOLUTION question cell ("At the recorded
300-rep site nulls, which splits of the tree of record ..."); ledger MIX-LRT-SITE chip "J SITE NULL REMAINS THE
CERTIFICATE"; docs/agents/KNOWLEDGE.md section 1 (split words; CONTEXT rule 12); prog L21448 S3 via README.md L100-L106 -->

The certificate's numbers belong to a different object from V0: the engine's tree of record bareq512_s42 (MMLU-Pro, R512, id-disjoint only).
On it, only Chemistry n00000006 and Engineering n00000015 may be called "certified at per-family FDR q = 0.05 (hierarchical BH over nested sites, 300 reps, bareq512_s42, R512)".
The other 8 of its 10 site-certified splits pass "their own site-null p95 (per-site, uncorrected)" only.
BY rejects nothing, and 53 of the 70 sites were never tested because their ancestors were not rejected (untested, not unreal).
What is certified is the split at the site, not the anchor category.
The tree is not a certified fixed point: its certificate reads CERTIFIED false at iteration 18, a GED-quiescence stop.
The Gaussian-mixture likelihood-ratio / BIC test certified every site it was run on, so it cannot discriminate; that line is closed negative, which is not evidence that the certified splits lack modes.
The dip half stays open; a dip test on the real sites (CERT-DIP-SITES) was chosen to start on 2026-11-06 and has no result in the records read.
<!-- src: KNOWLEDGE.md section 1 (Trees: the required wording; bareq512_s42 87 leaves, R512, id-disjoint only); ledger
CERT-RESOLUTION chips "C1 HELD: R512 HIERARCHICAL BH = 2 (CHEMISTRY, ENGINEERING; k = 0; NOT MC-MARGINAL)" and "PER-FAMILY
FDR ONLY: BY 0 ON EVERY TREE; 53/70 UNTESTED, NOT UNREAL; 300 REPS; OTHER 8 R512 SITES E3 WORDS ONLY"; CERT-RESOLUTION.json
sentence_of_record as quoted at README.md L193-L203 ("what is certified is the split at the site, not the anchor
category"); ledger RECORD-RECIPE-EDGE-AUDIT chip "RECORDED: bareq512_s42 CERTIFIED FALSE AT ITERATION 18 (GED-QUIESCENCE
STOP); NOT A FIXED POINT"; ledger MIX-LRT-SITE chips "C1 FAILED [FAILED-ALL-CERTIFY]: THE LR CERTIFIES 66/66, 69/69, 60/60,
87/87 ...; L6 LR/BIC HALF CLOSED NEGATIVE" and W1 ("NO MODAL SUPPORT; NOT EVIDENCE OF NO MODES"); the per-tree counts are
left in the ledger row and never set beside R256 counts (S4); README.md L256 (CONTEXT section 5 wording) and KNOWLEDGE.md
section 3 (dip half OPEN); D-2026-11-06-3 item (1) (#7 CERT-DIP-SITES starts) -->

The builder is replaceable in a precise sense: the audit takes a hierarchy as its input, and sections 4 to 7 ran it with k-means hierarchies in the tree's place.
On WORK rows, no advantage of the axis tree over nested k-means is detected, by the meter (NEST-METER), by back-off (SKILL-BACKOFF) or on BBH text (BBH-HIER).
None of the registered rows of section 2 shows one either, each on its own object and split: the anchor-free trees' cuts are worse partitions than flat k-means of the same size (CUT-WORSE 3 of 3), the anchor-free trees are as stable as bisecting k-means and not more, the record withdrew "the tree's hierarchy routes better", and on the union the anchor-free tree is not shown better than per-source k-means [SC].
"Replaceable" does not mean that the builder never matters: each comparison above is a bounded null or a descriptive reading, on four corpora, one embedder and one roster per corpus.
Nor does it replace V0 (end of this section).
<!-- src: arms of NEST-METER.json, SKILL-BACKOFF.json and BBH-HIER.json (question; numbers_of_record "fits (WORK rows)");
POSTRUN_NEST-METER row 3; ledger TREE-CUT-GRANULARITY chip "VALID (POST-RUN 37672103): TC CUT-WORSE 3/3"; ledger
STABILITY-VS-KMEANS (ST1 NEITHER; F-ST FIRED); ledger HIER-FAIR-BACKOFF chip "F-HB FIRES: 'THE TREE'S HIERARCHY ROUTES
BETTER' WITHDRAWN"; ledger UNION-AF-ROUTE chips and CORRECTED 2026-10-04 bracket [SC]; does_not_show of NEST-METER,
SKILL-BACKOFF, BBH-HIER ("any other embedder or corpus"; "anything that replaces V0") -->

### 8.3 Two companion sentences

The first turns SKILL-BACKOFF's licensed reading into advice: shrink per-cell estimates toward the declared label.
On WORK rows, shrinking per-model leaf rates toward the label predicts out-of-fold responses better than the raw leaf rates on MATH, BBH and MMLU; on MMLU-Pro it reads NEITHER (z 2.47).
The gain comes through the label, not the hierarchy (Q2, MEDIUM): label-only shrinkage gains at least as much as full back-off on MATH, MMLU-Pro and BBH, though not on MMLU.
Shrinking does not make the cells beat the labels everywhere: after back-off, V0's per-cell estimates beat the label rates on MMLU only.
Before back-off, the raw leaf rate is worse than the label rate on MATH, better on MMLU (the label SE beside reads NEITHER), and NEITHER on MMLU-Pro and BBH (Q1, MEDIUM).
The shrunk flat KF cells' BETTER against the labels on MATH and MMLU-Pro is thin and not a cells comparison (Q3, MEDIUM).
The estimates were scored in aggregate; no per-cell board, interval or profile follows from them.
<!-- src: prog L25881 (LICENSED: "shrinking per-model leaf rates toward the label predicts held-out WORK responses better
than the raw leaf rates (Z_bo BETTER; MMLU-Pro z 2.47 NEITHER)"; the record's "held-out" written "out-of-fold"); leads
file section 2 ("shrink per-cell estimates toward the declared label" = "SKILL-BACKOFF's licensed reading");
SKILL-BACKOFF.json brackets Q1-Q3 and the registrar's note on Q2; numbers_of_record V_tree, V_kf; closed_line; section 7 of
this draft for every figure -->

The second is a hypothesis, not a finding: granularity pays where the declared fine label is not the skill axis.
The pattern behind it: within the anchors, the axis leaves are nearly orthogonal to the MATH level (cAMI 0.0287, SE 0.0043) and partly rebuild the MMLU subject (0.3963, SE 0.0051) and the MMLU-Pro src (0.3207, SE 0.0048).
Beside that, on the meter's reserved read, the leaves' gain beyond the declared fine label reads SUPPORTED, qualified, on MATH and NOT SUPPORTED (powered) on MMLU-Pro (section 2).
LABEL-ALIGN reads item labels only (WORK 2,949 / 8,428 / 7,197 items for MATH / MMLU / MMLU-Pro) and adjudicates nothing.
It does not show that label re-discovery causes the smaller MMLU and MMLU-Pro gain, and the corpus is confounded with the kind of label: MATH's fine label is a difficulty tag.
No record read tests the hypothesis.
<!-- src: LABEL-ALIGN.json numbers_of_record "WORK cAMI", run.pool ("item labels only (WORK 2,949 / 8,428 / 7,197); no
response file opened"), sentence_of_record ("[EXPLORATORY, labels only, adjudicates nothing; POSTRUN 533002c3; dataset
confounded with label kind]"), does_not_show ("that label re-discovery CAUSES the smaller MMLU/MMLU-Pro gain"; "a
like-for-like dataset contrast (MATH's fine label is a difficulty tag)"); ledger BZ-METER-AXIS chips; leads file section 2
("at hypothesis level only"; "LABEL-ALIGN does not show causation"); the words "the skill axis" are the leads file's,
not a record's -->

### 8.4 The TaxoAdapt question

The author's second question was whether this logic makes sense for a more general clustering method, like the one in the TaxoAdapt paper on the scientific literature.
The audit's readouts take the hierarchy as an input and do not depend on how it was built, and the record has run most of them on several builders.
In sections 4 to 7 the builders are the axis tree (V0 anchored, AF anchor-free), bisecting spherical k-means with and without the anchors (BKM-A and BKMA; BKM), flat within-anchor k-means (K, KF), and average-link and Ward agglomeration on k-means centroids (KAL, KWD; BBH text only).
The registered rows of section 2 add flat spherical k-means (NESTING, TREE-CUT-GRANULARITY), bisecting spherical k-means (STABILITY-VS-KMEANS), a shape-matched spherical k-means hierarchy (HIER-FAIR-BACKOFF) and per-source k-means (UNION-AF-ROUTE).
Of the audit's four parts, the certificate is the one that the records read apply only to the engine's trees.
An LLM-built taxonomy was not tested.
The rule that no LLM enters the method binds benchzoom's structure, splits and labels (D-2026-10-12-2); whether an LLM-built taxonomy may enter as a comparator arm is left to the author.
No scientific-literature corpus has been audited, and the records state that the TaxoAdapt generalisation is untested.
Growing a taxonomy as new material arrives is outside the engine's design of record: anchor birth is manual, and FOREIGN prevents mislabelling and cannot create a cell.
The two leads proposed for these questions, CORPUS-ARRIVAL and SUPERGPQA-HIER, did not start (D-2026-11-06-3).
<!-- src: docs/agents/author_decisions/2026-11-02.md (the question, verbatim in section 1); leads file section 2 ("the
logic is hierarchy-agnostic and has already been run on several builders (axis tree, bisecting k-means with and without
anchors, flat k-means, agglomerative)": the leads file's reading, the builders checked against the records below); prog
L25695-L25697 (V0, K); NEST-METER.json question (TREE, BKM-A, BKM, KF); POSTRUN_NEST-METER row 3; BBH-HIER.json
numbers_of_record "fits (WORK rows)" (AF, BKM, BKMA, KAL, KWD on 96 k-means centroids, V0, V0m); ledger NESTING,
TREE-CUT-GRANULARITY, STABILITY-VS-KMEANS, HIER-FAIR-BACKOFF, UNION-AF-ROUTE (section 2 comments); certificate: ledger
CERT-RESOLUTION (bareq512_s42, the frozen tree, af_clean_s42, o0_clean_s42) and MIX-LRT-SITE (four trees), no record read
applies it to a k-means hierarchy; docs/agents/author_decisions/2026-10-12.md D-2026-10-12-2 ("benchzoom's structure,
splits and labels must not depend on LLM generation"); leads file "Decisions that are the author's" item 6 ("any LLM-built
comparator"); BBH-HIER.json does_not_show ("the TaxoAdapt generalisation is untested"); NEST-METER.json does_not_show ("a
TaxoAdapt-style generalisation"); docs/design/FRAMEWORK.md L266 (section "Limits, stated plainly"); D-2026-11-06-3 item (4)
("#5 ..., #8, #9 and #10 do not start"; #8 = CORPUS-ARRIVAL, #9 = SUPERGPQA-HIER, leads file summary table) -->

### 8.5 What the reading does not say

The record does not say that the tree is worse than nested k-means on the meter or in back-off, that the two are equal or equivalent, or anything about fresh items.
Nor does it say that flat partitions beat nested ones at matched granularity: on BBH, nested bisecting k-means is at or above flat k-means at matched k.
Outside this question the tree keeps the place the record gives it: V0 remains the pre-specified primary object of the paused fresh test, and no result here licenses replacing it.
<!-- src: NEST-METER.json does_not_show; BBH-HIER.json does_not_show and Q2 bracket; prog L25695 (V0 "stays the primary object",
D-2026-10-21-1); NEST-METER.json, BBH-HIER.json, SKILL-BACKOFF.json, FLAT-COMPARE.json does_not_show (nothing replaces V0
for BZ-AXIS-CONFIRM-FRESH) -->

## 9. What is not shown

- Nothing here is confirmed on fresh items.
  BZ-AXIS-CONFIRM-FRESH is drafted, never registered, and paused by the author (D-2026-11-01-1); its preparation stays on benchzoom master.
  A review of its proposed text found that, at the 18-25 models nameable today, no deciding contrast is SCOREABLE at m = 3, so that test could only falsify.
  <!-- src: prog L25870; docs/agents/author_decisions/2026-11-01.md; docs/reviews/DRAFTCHECK-2026-10-29b.md L83 (Q2 read with M1) -->
- Nothing here reads the meter's reserved side, a vault or a registered criterion; every result is a WORK-row readout on one split.
  <!-- src: run.pool of FLAT-COMPARE.json, NEST-METER.json, BBH-HIER.json, SKILL-BACKOFF.json; prog L25712 (D-2026-10-20-4) -->
- No equality, equivalence or "nesting is free": the NEITHER words of tests 1 and 2 are bounded by their MDE80s.
  <!-- src: NEST-METER.json does_not_show; SKILL-BACKOFF.json does_not_show ("'equal' hierarchies ... MDE80 up to 4.54") -->
- No ordering of nested k-means, the tree and flat k-means at any level.
  <!-- src: NEST-METER.json does_not_show -->
- No "k-means cells beat the tree's cells", no "the tree's internal levels help", and no general "raw leaf rates are unusable".
  <!-- src: SKILL-BACKOFF.json does_not_show (Q1, Q2, Q3) -->
- No "flat beats nested", and no "recovers the subtasks" on BBH.
  <!-- src: BBH-HIER.json does_not_show (Q2, Q6) -->
- No per-cell board, interval or profile; the closed sub-anchor line stays closed.
  <!-- src: SKILL-BACKOFF.json closed_line, does_not_show; docs/agents/KNOWLEDGE.md section 3 (sub-anchor profiles closed) -->
- One embedder for tests 1 to 3 (qwen3); on the one second embedder tried, the MATH k-means lead over the tree shrank to z -1.30.
  <!-- src: NEST-METER.json, BBH-HIER.json and SKILL-BACKOFF.json does_not_show ("any other embedder"); BBH-HIER.json run.pool
  (qwen3 512-d prefix); EMBED2-WORK.json R2 -->
- One roster per corpus (69, 23, 79 and a seeded 128 of 342 models), and one tree build per corpus.
  <!-- src: run.pool of NEST-METER.json and SKILL-BACKOFF.json; BBH-WORK.json does_not_show ("any statement about the full
  342-model roster"); EMBED2-WORK.json D4 ("V0 and V0g are one seed-0 build each") -->
- Flat k-means at its own best k on the meter, and the attribution of the kNN field's lead to method rather than to 4,096-d vectors.
  <!-- src: POSTRUN_FLAT-COMPARE "Does not license" -->
- Any generalisation to other corpora or to TaxoAdapt-style scientific-literature taxonomies; no LLM-built taxonomy and no scientific-literature corpus was audited, and in the records read the certificate has been applied to the engine's trees only.
  <!-- src: NEST-METER.json does_not_show ("a TaxoAdapt-style generalisation"); BBH-HIER.json does_not_show ("the TaxoAdapt
  generalisation is untested"); ledger CERT-RESOLUTION, MIX-LRT-SITE (trees only); D-2026-11-06-3 item (4) (#8, #9 do not
  start) -->
- No "the builder does not matter": "replaceable" means that the audit ran with other builders in the tree's place, and every builder comparison here is a bounded null or a descriptive reading.
  <!-- src: NEST-METER.json, SKILL-BACKOFF.json does_not_show (no equality; MDE80s); ledger HIER-FAIR-BACKOFF (DESCRIPTIVE-ONLY
  BY SUPPORT), STABILITY-VS-KMEANS (NEITHER), UNION-AF-ROUTE (not shown better) -->
- No test of the label-alignment hypothesis of section 8.3, and no causal reading of LABEL-ALIGN.
  <!-- src: LABEL-ALIGN.json does_not_show; leads file section 2 ("at hypothesis level only") -->

In the records read, benchzoom brackets and selftest fixes are owed for all three tests (NEST-METER [P2] and the N2 fix; BBH-HIER [P3] and T-1; SKILL-BACKOFF [P3] and Q5).
Until they land, the records and the POSTRUNs carry the qualifiers quoted above.
<!-- src: prog L25869 (NEST-METER, BBH-HIER: brackets and fixes owed); prog L25882 (SKILL-BACKOFF: [P3] and the Q5 selftest
commit owed); docs/agents/author_decisions/2026-11-06.md D-2026-11-06-1 (3) (the small review fixes go ahead) -->

---

## Number-to-source list

Every figure in the text, in order of appearance, with the record it is copied from.
"JSON" is docs/agents/results/<ID>.json; "POSTRUN" is docs/reviews/POSTRUN_<ID>.md; "ledger" is docs/test_ledger.html (last bracket); "prog" is docs/judge_v2_program.md.

| section | figure(s) | source |
|---|---|---|
| Status | 2,949 x 69; 7,197 x 23; 8,425 x 79; 3,457 x 128 of 342 | NEST-METER JSON run.pool; BBH-WORK JSON run.pool |
| Status | reserved 40%, not content-closed | BZ-METER-AXIS JSON run.pool |
| 2 | g +0.2588, SE 0.0628, LB +0.070, delta_min 0.10, 1,960 x 69 | ledger BZ-METER-AXIS observed cell; BZ-METER-AXIS JSON criteria |
| 2 | g -0.0059, SE 0.0183, MDE80 0.0703, 4,654 x 23 | ledger BZ-METER-AXIS; BZ-METER-AXIS JSON |
| 2 | +0.124 (0.035), +0.15 (0.036), +0.109 (0.032) | ledger BZ-GRANULARITY-WORK observed cell; JSON A1-A3 |
| 2 | 6 of 6, V90 0.3807-0.6592, 30 seed values, bar 0.10 | ledger NESTING OUTCOME bracket; NESTING JSON |
| 2 | D_cut -0.0298 [-0.0383, -0.0209], -0.0263 [-0.0343, -0.0189], -0.0315 [-0.0397, -0.0229]; 3,598 / 3,522 / 3,500 | ledger TREE-CUT-GRANULARITY OUTCOME bracket; JSON sentence_of_record |
| 2 | 2,772 items; about 12% vs 0.1% unresolved | ledger STABILITY-VS-KMEANS OUTCOME bracket |
| 2 | +0.90pp [+0.03, +1.76]; tau 100 vs 200 by one GATE item; 5,907 / 5,404; 18 models | ledger TREE-BACKOFF chips, OUTCOME bracket, scope cell |
| 2 | 0.53pp [-0.944, -0.106]; MDE80 0.61pp; 11,841 / 10,781; EVAL +0.29pp [-0.42, +0.99] | ledger HIER-FAIR-BACKOFF chips, OUTCOME bracket |
| 2 | -0.45pp [-1.31, +0.41]; 0.0002; -1.15pp [-2.19, -0.12]; 5,907 / 5,404 | README.md L145-L151; ledger UNION-AF-ROUTE chips, OUTCOME bracket |
| 3 | 512-d; 4,096-d; 40 nearest rows; 5 seeds | prog L25696, L25697 |
| 3 | anchors 7 / 14 / 17 / 24; leaves 36 / 80 / 100 / 40 | NEST-METER JSON "levels" |
| 3 | 5 folds x 5 seeds | BZ-GRANULARITY-WORK JSON sentence_of_record; prog L25876 |
| 3 | x1.3-1.8 | POSTRUN_FLAT-COMPARE D2 |
| 3 | x1.38-1.65 at C1 0.10, 9 pairs | prog L25754, L25756 (b) |
| 4, Table 1 | MATH / MMLU / MMLU-Pro C1 points | POSTRUN_FLAT-COMPARE row 4 |
| 4, Table 1 | MATH SEs 0.0316 / 0.0462 / 0.0596 | prog L25700 (PF5-PF7) |
| 4, Table 1 | BBH C1 and SEs | BBH-WORK JSON "C1 of the arms" |
| 4, Table 2 | V0 - K -0.1652 (0.0358) z -4.61; -0.0085 (0.0147) z -0.58; MMLU-Pro "a tie (0.8 SE)" | POSTRUN_FLAT-COMPARE rows 5, 14 |
| 4, Table 2 | N - V0 +0.2406 / +0.0629 / +0.0784, z 4.44 / 2.97 / 2.40 | FLAT-COMPARE JSON "L3k - V0" |
| 4, Table 2 | V0 - RND +0.1146 (0.0316) 3.63; +0.0439 (0.0180) 2.44; -0.0039 (0.0197); leaf 2.02 / 1.51 | FLAT-COMPARE JSON "V0 vs random"; POSTRUN row 7, D2 |
| 4, Table 2 | V0 - K leaf z -3.41 (f2), -2.98 (cont); content -4.612 / -4.067 | FLAT-COMPARE JSON bracket 2026-10-28 (TAU-CONT-ALL C1) |
| 4, Table 2 | BBH V0 - K +0.0126 (0.0528); V0 - RND +0.0727 (0.0775) | BBH-WORK JSON K1, "V0 vs random" |
| 4 | -0.165, 4.6 SE | FLAT-COMPARE JSON sentence_of_record (D1 wording) |
| 4 | gemma -0.0363 (0.0279), z -1.30 | EMBED2-WORK JSON R2 |
| 4 | MMLU-Pro C1(V0) -0.0095 | POSTRUN_FLAT-COMPARE "Does not license" |
| 4 | BBH +0.0845 (0.0722), z 1.17, MDE80 0.2775; MDE80 0.2204 | BBH-WORK JSON R1, "V0 vs random" |
| 4 | +0.0067, upper +0.027; +0.0165 (1.56 SE) | FLAT-COMPARE JSON "K2 MATH"; POSTRUN_FLAT-COMPARE licenses |
| 4 | BBH +2.3142 (0.3885); 1.74 / 1.87 SE; 83%; 21 subtasks +0.29 (0.32) | BBH-WORK JSON K2 and C1 bracket |
| 5 | levels 7/14/25/36, 14/28/51/80, 17/33/58/100, 24/40 | NEST-METER JSON "levels"; POSTRUN row 2 |
| 5, Table 3 | every D, SE_leaf, z; UNDERPOWERED cells | NEST-METER JSON MATH / MMLU-Pro / BBH / MMLU rows and "words" |
| 5 | MDE80 0.012-0.199, 0.003-0.074, 0.008-0.073, 0.139-0.247 | NEST-METER JSON "support" |
| 5 | 15 of 30 | NEST-METER JSON "words" |
| 5 | z 2.98; meter z 3.07 / 3.18 / 4.07; f2 z 3.41 | NEST-METER JSON "largest z", "beside, never the word" |
| 5 | share 0.53, SE about 0.19 | NEST-METER JSON bracket Q1 |
| 5 | +0.1974 vs +0.2340; D -0.0366 (0.0642), z -0.57 | NEST-METER JSON prediction P5 |
| 6 | 3,457; 2,662 clusters; n_eff 783 | BBH-HIER JSON "best-cut AMI"; POSTRUN_BBH-HIER row 2 |
| 6, Table 4 | every AMI and SD; leaf counts; ceiling 0.9517 | BBH-HIER JSON "best-cut AMI G1 / G2", "fits (WORK rows)" |
| 6 | AMI 0.93-1.00; p97.5 of 200 | BBH-HIER JSON sentence_of_record, "node level" |
| 6 | 0.500 | BBH-HIER JSON "3/5/7" |
| 6 | 0.5031, 26 cells; 0.4936, 27-28 cells; bar 0.50; homogeneity 1.000 | BBH-HIER JSON prediction PH7, bracket Q1; prog L25868 |
| 6 | G3 0.988 | BBH-HIER JSON "3/5/7" |
| 6 | +0.0300 (0.0050), -0.0231 (0.0049), -0.0163 (0.0026); MDE80 0.007-0.014 | BBH-HIER JSON "contrasts" |
| 6 | +0.0130 (0.0049), +0.0118 (0.0051); 95 k; 0.02-0.06 | BBH-HIER JSON "contrasts", bracket Q2 |
| 6 | k 20: 0.953 vs 0.936; k 24: 0.946 vs 0.942 | POSTRUN_BBH-HIER row 11 |
| 6 | 11 of 14; 5,761 texts | BBH-HIER JSON "predictions", sentence_of_record |
| 7 | 5 folds x 5 seeds | prog L25876 |
| 7, Table 5 | every D, z, word; MDE80 of Z_hier; B_lab | SKILL-BACKOFF JSON numbers_of_record; prog L25878 |
| 7 | +10.69 vs +10.28; +1.73 vs +1.17; BBH equal; +1.97 vs +2.55; +0.57 (0.30) | SKILL-BACKOFF JSON bracket (registrar's note on Q2); prog L25880 |
| 7 | -0.41 (0.15), -0.57 (0.30); -0.49 (0.20), -0.59 (0.27) | SKILL-BACKOFF JSON "internal levels"; prog L25880 |
| 7 | -10.03, z -5.8; +12.60, z 3.84 | SKILL-BACKOFF JSON V_raw, bracket Q1 |
| 7 | z 3.11 / 3.03 | SKILL-BACKOFF JSON V_kf, bracket Q3 |
| 7 | +47 to +207, z 9.7 or more | SKILL-BACKOFF JSON sentence_of_record |
| 7 | 64 / 112 items; 3 of 3 without BBH | SKILL-BACKOFF JSON prediction P7 |
| 7 | leaf DEFF 9.2-13.6 | SKILL-BACKOFF JSON "support" |
| 7 | 8 of 10; +0.25, SE_word 0.21 | prog L25879; SKILL-BACKOFF JSON prediction P1 |
| 8.1 | 6 of 6 | ledger NESTING chip, OUTCOME bracket |
| 8.1 | MDE80 0.199 / 0.074 / 0.073 / 0.247; 15 of 30 | NEST-METER JSON sentence_of_record, "words" |
| 8.1 | share 0.53, SE about 0.19; z 2.98 | NEST-METER JSON bracket Q1 |
| 8.1 | AMI 0.9305 (G1); BKM - AF +0.0300 (0.0050) | BBH-HIER JSON "best-cut AMI G1 / G2", "contrasts"; prog L25868 |
| 8.1 | Z_hier MDE80 0.75 / 2.13 / 0.78 / 4.54 | SKILL-BACKOFF JSON numbers_of_record Z_hier |
| 8.2 | J site null, 300 reps; q = 0.05; Chemistry n00000006, Engineering n00000015; 8 of 10; 53 of 70 | ledger CERT-RESOLUTION chips; KNOWLEDGE.md section 1 (wording); README.md L193-L203 |
| 8.2 | CERTIFIED false at iteration 18 | ledger RECORD-RECIPE-EDGE-AUDIT chip |
| 8.2 | the LR certifies every site | ledger MIX-LRT-SITE chip C1 (66/66, 69/69, 60/60, 87/87; not printed in the text) |
| 8.2 | CUT-WORSE 3 of 3 | ledger TREE-CUT-GRANULARITY chip |
| 8.3 | z 2.47 | SKILL-BACKOFF JSON Z_bo; prog L25881 |
| 8.3 | cAMI 0.0287 (0.0043), 0.3963 (0.0051), 0.3207 (0.0048); 2,949 / 8,428 / 7,197 items | LABEL-ALIGN JSON numbers_of_record "WORK cAMI", run.pool |
| 9 | 18-25 models; m = 3 | docs/reviews/DRAFTCHECK-2026-10-29b.md L83 |
| 9 | z -1.30 | EMBED2-WORK JSON R2 |
| 9 | 69, 23, 79, 128 of 342 | NEST-METER JSON run.pool; BBH-WORK JSON run.pool |

## Sentences left out (no record carries them)

1. A plain-language definition of the meter's "backbone" used by B_lab: the records say only "the meter's backbone as offset" (prog L25876), so the text keeps those words.
2. The SEs of C1 for the MMLU and MMLU-Pro arms and for MATH RND: not printed in the records read (POSTRUN_FLAT-COMPARE row 4 says only "SEs equal to 4 dp"), so Table 1 leaves them out.
3. The MMLU-Pro V0 - K point and SE: the review prints only "a tie (0.8 SE)" (row 14), so Table 2 quotes that.
4. BBH's N - V0 contrast: not recorded (BBH-WORK records G(N|L2+V0) instead), so Table 2 prints "not printed".
5. Whether the meter's responses are key-scored correctness: not stated in the records read, so no accuracy word is attached to the meter.
6. The roster size of HIER-FAIR-BACKOFF: its ledger row does not print it, so only TREE-BACKOFF's 18 models are given.
7. Why the meter's MATH leaf gain (C1(V0) +0.1093) and SKILL-BACKOFF's V_tree NEITHER on MATH read differently: no record explains it, so no reason is offered.
8. Any build-cost or runtime comparison between the tree and k-means as a reason to prefer either: not in the record.
9. A description of TaxoAdapt's method: the leads file calls it background, not record, so section 8.4 does not characterise the paper.
10. The content of the main session's chat answer to the TaxoAdapt question of 2026-11-02: the decision file says only "answered in chat (no action)", so section 8.4 is written from the records alone.
11. Whether the J site null applies unchanged to a k-means split: no record read applies the certificate to a k-means hierarchy, so section 8.4 says only that it has been applied to the engine's trees.
12. Lead 1's projection of the MATH SUPPORTED word under the cell-aware SE: the z values in the leads file are the lead's arithmetic, not the record, and the projection note of D-2026-11-06-3 item (2) is absent from the records read; sections 2, 8.1 and 8.3 keep the recorded word "SUPPORTED, qualified" and must carry the note once it lands. [RESOLVED 2026-11-07 by the main session: the bracket landed at prog L25486 (79ef14a7) and section 2 now carries it; sections 8.1 and 8.3 do not quote the MATH word.]
13. A definition of "the skill axis": no record defines it; section 8.3 keeps the leads file's words as the wording of a hypothesis.
14. CONSTRUCTION-ARMS (registered; Ward, bisecting and per-node GMM-BIC split rules against an engine-like k-means stand-in on two intent corpora; NO-ARM-WINS, DESCRIPTIVE-ONLY) as one more builder in section 8.4: left out because its record prints no split word for those corpora beyond "EVAL by CK-CLOSE components", which S3 would need.
