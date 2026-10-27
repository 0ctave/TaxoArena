# Next registrations (research-lead, 2026-10-01 for 2026-10-02): INTENT-TRANSFER-S1, RP13 UNION-AF-ROUTE re-scoped, CARD-PROTOCOL fixed, EMBED-QUANT (option), paid-run readiness RP21 -> RP20 -> RP19

This is a plan file, not a record file. Zero calls, design only. Nothing here is registered until the registrar commits it.
The dimension arm is a separate draft: EMBED-DIM-SLICE (`docs/agents/plans/2026-10-02_embed_dim_slice.md`, a5c88533), being registered and built.

Inputs:
- the author's decisions of 2026-10-01: prog L22567-L22571 (D1, D3, D4, D5; D2 and D6 open);
- the registrar's K1-K5 check of CARD-PROTOCOL: L22573-L22577;
- F-TAX: registration L21557-L21580, partial score L22555-L22565;
- ARCH-V2-E-T registration L22028ff (G13 and G14 rules, Support form);
- S0 registration L22092-L22134 and `s0_run.log`;
- results JSONs: INTENT-TRANSFER-S0, INTENT-S0-SLOTSWAP-MECH, MMLU-GOLD-GEOMETRY, F-TAX, K46-KEY-READ, CANARY-EPOCH2-RUNG;
- the queue items read on 2026-10-01;
- the design doc 2026-09-29_intent_transfer_design.md §3-§6;
- checkpoint A (c)1-6 and checkpoint B.

The coordinator relayed an author ruling on 2026-10-01: RP19 waits for BOTH RP20's outcome AND D2. The registrar should record it.

Facts verified for the briefs (commands named; agents do not re-verify):
- **S0 fine seed spreads**, from `s0_run.log` L32-L63:
  - qwen3: 0.02463 / 0.00942 / 0.01434 (MASSIVE / CLINC / Banking77);
  - gemma: 0.01757 / 0.00229 / 0.01400.
- **S0 bootstrap SE(D) at 256** (gemma − qwen3): 0.00289 / 0.00137 / 0.00247.
- **S0 EVAL denominators**:
  - MASSIVE 4,946 items in 4,923 components;
  - CLINC in-scope 6,672 in 6,672, plus 1,350 OOS;
  - Banking77 3,908 in 3,905.
  - Kish DEFF: 1.0093 / 1.0000 / 1.0015.
- **SLOTSWAP**:
  - 3,222 variants in 3,207 components;
  - S: qwen3 0.7598, gemma 0.8262; ceiling (supervised) 0.834; floor (random same-intent) 0.692;
  - by-margin quintile flip rates: 0.551 / 0.279 / 0.189 / 0.099 / 0.082;
  - seed spread of S: 0.0335.
- **G14 (RP12-R2)**:
  - G_tree +2.62pp [+1.43, +3.82], 5,907 items in 5,404 components, DEFF 1.392;
  - M = G_tree − G_declared: −0.05pp [−0.69, +0.59], which gives a paired SE of about 0.33pp.
- **G13 rule**: verbatim at prog L22034; spread_KC 0.0112; D13 −0.0215.
- **CANARY-ANALYZE-FIX**:
  - code merged on main: fcd200ea, fixes 5e9455b3 and d6c54231 (`git merge-base --is-ancestor`);
  - READY ad65d094 is conditional, and its selftest was NOT READY;
  - no delta READY on the fixed selftest and no phase-B run is recorded (grep of programme, results and reviews for d6c5423 / 5e9455b / ad65d09: 0 hits);
  - the queue still says "drafted", which is record drift.
- **canary_baseline.py**:
  - `--pass` accepts only 1-4 (L1808);
  - in its epoch-2 modes every `sqlite3.connect` is rewritten to ro/immutable, and `stack_judge.open_cache()` is never called (docstring L78-L83).
- **Not yet registered**: RP20 and RP21 have no queue item and no registration. READY-TEMPLATE-TRANSPORT and STACK-JUDGE-RO-CACHE are drafted and not built. E1-ROUTE is built 6b3f0b1 but NOT READY (B-E1-1, B-E1-2).
- **Local Ollama models** (`ollama show`): qwen3-embedding:latest is Q4_K_M (7.6B); embeddinggemma:latest is BF16. No non-Q4 qwen3 tag.
- **AF recipe of record**: af_clean_s42 is label-free, z 2.0, mcs 55, 256-d slice, bar 0.025 (its config.toml header).

## 1. INTENT-TRANSFER-S1 (the author's D5 "Go"): registration text (for the registrar)

**Heading.** `## Registered <date> (before any code or call) — INTENT-TRANSFER-S1: on MASSIVE en-US and CLINC150 (gold hierarchies known), do real TRAIN-only tree builds partition, file, nest and hold their addresses as well as flat k-means at matched k, relative to a supervised ceiling arm; does a label-free leaf margin buy stability by abstention; and does the tree file beyond label-conditioned prototypes (the known-answer counterpart of G13)? (zero calls; builds; plan Amendment 31 D5)`

**Question and kind.**
- Kind: build (machine lane), then CPU readouts. 0 LLM calls.
- It answers design §3(a)-(c) and (f) with real builds.
- Lessons carried in:
  - every criterion is relative: to matched-k k-means, and to a supervised ceiling arm (checkpoint A (c)1). There is no absolute bar such as C4's 0.80;
  - margin and abstention come from S0 C3 and SLOTSWAP M1;
  - the G13-style comparator is fixed now;
  - gemma is a registered secondary arm (the author's D3);
  - certification is NOT a deliverable: no site null is run (checkpoint B (b)3, closing).

**Prior results touched (none revised).**
- S0: C1a; C2 AUROC 0.974; C3 rho; C4 FAILED (S 0.760).
- SLOTSWAP M1 / M2.
- TOPIC-PARTITION-20NG: tree ties k-means, −0.0020 against spread 0.0074.
- FLAT-MIX-MMLU: af_clean_s42 is worse than V0.
- ARCH-V2-E-T-R2:
  - FLAT C1 HELD, thin (T level with spherical k-means K3);
  - G13 FAILED (−0.0215);
  - G11 D_fd +9.37pp.
- MC-ROOT (id-disjoint only).
- Closed lines: none.
  - No sub-anchor profile: the anchored arm discovers intents below scenario anchors, which is filing and partition against a known answer, never evidence for sub-anchor PROFILES.
  - No GMM LR.
  - No frontier.

**Hygiene.**
- Split: S0's CK-CLOSE-v1 hash sides (EVAL 0.30 / GATE 0.10 / TRAIN 0.60) on `intent_transfer_corpora_v1.db` (sha256 487e0093...).
  - Cross-label twins dropped (S0's 22).
  - Near-copies (cos >= 0.98) are disclosed, not removed. Every T readout is printed with and without them as a registered sensitivity line, never a removal.
  - The split word is the data-steward's.
- Build inputs: per-arm build DBs containing TRAIN and GATE rows ONLY, so EVAL is physically absent from the JVM.
- Embeddings: from S0's pinned embedding DBs, through the working-copy route: a per-run copy, sha checked before and after, `-Dtaxoarena.embeddingCacheFile` set to the copy, and its own `-Dranking.db.path`.
- `embeddings_cache.db` per-table hashes are unchanged across every build (the acceptance check).
- Fits:
  - k-means comparators, centroids and margins are fitted on TRAIN;
  - thresholds and the TOST delta are fixed on GATE before EVAL opens;
  - EVAL is read once.
- OOS never enters a build or a fit.
- Rule 7 W1-W5, a backup before each build, 12 threads, one construction at a time, no paid run concurrent.
- No corpus text in any committed file.

**Instrument.**
- Arms (qwen3 of record; recipes per arm, never ranked against each other):
  - MASSIVE AF-256: the af_clean_s42 recipe (label-free, z 2.0, mcs 55, 256-d, bar 0.025). This is arm **M-AF**. Also:
    - its replay **M-AF'** (determinism precondition);
    - two constructionOrderShuffleSeed arms, **M-o1** and **M-o2** (the T-C2 spread);
    - a split re-draw, salt 2, **M-AF-s2** (descriptive replicate).
  - MASSIVE anchored-512 (scenario anchors; bareq512 geometry, bar 0.0145): **M-AN**.
  - CLINC AF-256: **C-AF**.
  - CLINC anchored-512 (domain anchors): **C-AN**.
  - SECONDARY: MASSIVE AF on gemma at EMBED-DIM-SLICE's d_g*, RAW: **M-AF-g**. It runs only after E1-ROUTE is READY and merged (the non-qwen3 JVM route and vmfMu guard). If E1-ROUTE is not READY when the lane opens, the arm is OMITTED, and that is a stated precondition, not an outcome.
- Banking77 has no build: flat gold, no hierarchy, S0 covers it.
- Readout script: `tools/analysis/intent_transfer_s1.py`, TO BE BUILT. It imports S0's functions verbatim (k-means, NMI, component bootstrap B 2,000, margin, S).
- Engine: a generic intent DatasetType that fails closed with no Hugging Face fallback, plus the build-DB exporter, both TO BE BUILT.
- The outcome is write-once at `experiment_results/intent_transfer/s1_outcome.txt`.
- PRECONDITION P0: M-AF and M-AF' have identical per-node membership as sets (G10's rule as held after EMD; intra-node list order is excluded, per R1's recorded failure). A failure stops the lane.
- Ceiling arms, computed per corpus on the same EVAL:
  - supervised TRAIN-centroid filing and kNN-15 (fine and coarse);
  - the supervised partition's NMI;
  - S ceiling 0.834 and floor 0.692, recomputed per arm.

**Readouts and criteria** (95% component-bootstrap intervals unless named; comparators use k-means seeds 0-19, mean over seeds, because the seed term enters each TOST SE).

- **T-C1 (leaf partition, AF arms; TOST plus loss flag; the INTERVAL decides).** Per corpus, D1 = NMI_fine(tree leaves, flatLeaf) − mean_s NMI_fine(k-means at k = L).
  - delta_c = 0.25 x (NMI(supervised partition) − mean_s NMI(k-means at k = L)), measured on GATE and written before EVAL. This is a quarter of the ceiling gap: the criterion is relative to the ceiling arm.
  - EQUIVALENT iff the 90% CI of D1 lies inside ±delta_c.
  - LOSS (L1) iff D1 < −bar AND the 95% CI < 0, with bar = max(MDE80, spread_K), spread_K = max − min over seeds 0-4 (S0's rule).
  - GAIN symmetrically.
  - UNDETERMINED otherwise.
  - SE_total = sqrt(SE_boot^2 + var_seed(D1) / 20).
- **T-C1b (G13 analogue, AF arms; G13's rule verbatim at the COARSE level).**
  - D13' = coarse filing precision of the leaves (TRAIN-majority coarse label, flatLeaf) − P(KC_0).
  - KC_s: per gold coarse class, spherical k-means on that class's TRAIN members at k_c = max(1, number of leaves whose TRAIN majority is c), seeds 0..4.
  - HELD (lever) iff CI > 0 AND D13' > spread_KC; FAILED iff CI < 0 AND D13' < −spread_KC; UNDETERMINED otherwise.
  - Printed beside: nearest gold centroid; kNN-15 (the ceilings).
- **T-C2 (hierarchy beyond the leaves; M-AF only; POINT and INTERVAL).** D2 = DP(tree) − DP(average-link agglomerative on the same leaves), dendrogram purity against gold coarse.
  - HELD iff D2 > spread_o (max − min of D2 over M-AF, M-o1, M-o2) AND CI > 0. FAILED iff CI < 0. UNDETERMINED otherwise.
  - Floor: 200 random binary hierarchies over the same leaves.
  - CLINC: DESCRIPTIVE (coarse level not convex; H 0.14).
- **T-C7 (stable address, MASSIVE; TOST plus loss flag).** D7 = S(tree leaves) − mean_s S(k-means at k = L), paired on the 3,222 variants.
  - delta = 0.25 x (0.834 − 0.692) = 0.0355, a quarter of the ceiling-floor span, with both ends recomputed in-run per arm.
  - EQUIVALENT / LOSS / GAIN / UNDETERMINED as in T-C1; bar = max(MDE80, spread of S over seeds 0-4).
  - The ceiling-normalised R = (S − floor) / (ceiling − floor) is printed for both.
- **T-C9 (margin abstention on tree leaves; M-AF; the INTERVAL decides).** m(q) = cos(own leaf centroid) − cos(second-nearest leaf centroid) of the ORIGINAL item. This is label-free and computed from TRAIN centroids.
  - The abstention threshold is GATE's 20th percentile of m.
  - D9 = flip rate(abstained) − flip rate(kept).
  - HELD iff lower(D9) > 0; FAILED iff upper(D9) <= 0.
  - Printed beside: S(kept); and selective fine filing precision at 80% / 90% coverage on MASSIVE and CLINC (abstain = no-match).
  - D9(tree) − D9(k-means at k = L): DESCRIPTIVE.
- **T-C8 (filing rule, AF arms).** D_fd = fine filing precision flatLeaf − descent, paired.
  - HELD iff lower(D_fd) > 0 on both corpora; FAILED iff upper <= 0 on either.
  - **T-C8b**: D_fd(CLINC) − D_fd(MASSIVE). HELD iff its CI (independent bootstraps) > 0.
  - Mechanism: coarse centroid-vs-kNN gap 0.12 (CLINC) vs 0.04 (MASSIVE).
- **T-C4 (overlap tracking).** Mantel r between gold intent confusion (S0 D3) and LCA distance of the intents' modal leaves, against 10,000 intent-label permutations.
  - HELD iff p < 0.05 on both corpora; FAILED iff p >= 0.05 on both.
  - Tree vs agglomerative: DESCRIPTIVE.
- **DESCRIPTIVE ONLY:**
  - T-C3 granularity: own-leaf rate against log TRAIN size per intent, with a token-length covariate. The slope sign is scored only at the point: predicted positive.
  - T-C6 OOS AUROC of leaf centroids against k-means at k = L, beside supervised 0.9764.
  - The anchored arms' T-C1 and T-C8.
  - M-AF-s2's replicate rows.
  - Every gemma-arm row (M-AF-g: T-C1, T-C7, T-C9), beside qwen3, never contrasted as a criterion.

**Support.**
- (a) Deciding denominators:
  - MASSIVE EVAL 4,946 items in 4,923 components; CLINC in-scope EVAL 6,672 in 6,672 (OOS 1,350 for T-C6 only);
  - T-C7 and T-C9: 3,222 variants in 3,207 components;
  - T-C4: intents (60 / 150), with pairs 1,770 / 11,175;
  - T-C2: M-AF's leaves.
  - The dry-run reconciles counts; a difference above 5% is re-stated by bracket before any read.
- (b) DEFF and source: Kish 1.0093 / 1.0000, and 1.0093 for the variants, all measured in S0 on the same components.
- (c) n_eff: 4,900 / 6,672; 3,192.
- (d) SE, arithmetic:
  - **T-C1:**
    - SE_boot is transported from S0's paired-NMI bootstrap: 0.00289 / 0.00137;
    - seed term: sd = spread / 2.33 (the range of 5 normal draws), giving 0.0106 / 0.00404, then / sqrt(20) = 0.00236 / 0.00090;
    - SE_total = sqrt(0.00289^2 + 0.00236^2) = 0.00373 (MASSIVE) and sqrt(0.00137^2 + 0.00090^2) = 0.00164 (CLINC).
    - The tree's own build variance is NOT in this SE; on MASSIVE the four arms print it.
  - **T-C1b:** sqrt((d − D^2) / n_eff) with planning discordance d of 0.08 / 0.06 and D = −0.02. This gives 0.00403 / 0.00299.
  - **T-C2:** 0.005 (design planning value).
  - **T-C7:** sqrt(0.20 / 3,192) = 0.0079, plus a seed term of 0.0335 / 2.33 / sqrt(20) = 0.0032, giving SE_total 0.0085.
  - **T-C9:** sqrt(0.16 x 0.84 / 2,578 + 0.55 x 0.45 / 644) x sqrt(1.0093) = 0.0210. The flip rates are SLOTSWAP's top-four and bottom quintiles.
  - **T-C8:** sqrt((0.12 − 0.0025) / n_eff) = 0.0049 / 0.0042. T-C8b: 0.0065.
  - **T-C4:** Mantel SE of about 1 / sqrt(K) = 0.13 / 0.08 (planning; the permutation null decides).
- (e) MDE80 = 2.8 x SE:
  - T-C1 0.0104 / 0.0046. The TOST half-width is 1.645 x SE_total = 0.0061 / 0.0027. Planning delta_c is 0.025 / 0.015 (assuming ceiling gaps of 0.10 / 0.06); the GATE measurement decides.
  - T-C1b 0.0113 / 0.0084 (spread_KC planning 0.0112, G13's).
  - T-C2 0.014 (spread_o planning <= 0.005; G15's order drift was 0.0151pp).
  - T-C7 0.024; TOST half-width 0.0140; delta 0.0355; LOSS bar 0.0335.
  - T-C9 0.059. T-C8 0.0137 / 0.0118; T-C8b 0.018.
  - T-C4 r 0.36 / 0.23.
- (f) VERDICT LINES at the predictions:
  - **T-C1:** EQUIVALENT is SCOREABLE (predicted −0.005, inside delta − half = 0.019 / 0.012). LOSS is DESCRIPTIVE-ONLY at the prediction (−0.005 is inside −bar).
  - **T-C1b:**
    - FAILED clause on CLINC: THIN SCOREABLE (0.0088 beyond −spread_KC > 0.0084).
    - On MASSIVE: DESCRIPTIVE-ONLY (0.0088 < 0.0113).
  - **T-C2:** SCOREABLE (+0.020 > MDE 0.014; the spread clause is structural, (g)).
  - **T-C7:** EQUIVALENT is SCOREABLE (−0.010 inside 0.0355 − 0.0140 = 0.0215). LOSS is DESCRIPTIVE-ONLY.
  - **T-C9:** SCOREABLE (+0.30 against 0.059).
  - **T-C8:** SCOREABLE (+0.03 > 0.0137; +0.08 > 0.0118). T-C8b SCOREABLE (+0.05 > 0.018).
  - **T-C4:** SCOREABLE on CLINC; THIN on MASSIVE (r 0.35 against 0.36). HELD needs both, so T-C4 is THIN.
  - The DESCRIPTIVE rows are the deliverable only as context.
- (g) STRUCTURAL LEG:
  - A TOST is reachable iff the true absolute D < delta − 1.645 SE_total (0.019 / 0.012 / 0.0215 at planning values).
  - The LOSS, T-C1b and T-C2 spread clauses are reachable only where the true difference exceeds the seed or order spread, which does not shrink with n. Inside it they read UNDETERMINED at any budget (stated now).
  - T-C8, T-C9 and T-C4 are reachable.

**Predictions (80% intervals; priors named).**
- P0 precondition holds: 0.90 (G10 as sets; THREAD-CAP C1).
- P1 leaves: M-AF 25-50; C-AF 60-110 (design; size-dependent bar); M-AN 50-90; C-AN 100-160.
- P2 T-C1 D1: −0.005 [−0.025, +0.015] on both corpora. EQUIVALENT on both 0.45; LOSS on either 0.15. Priors: 20NG tie (−0.0020); FLAT K3 tie; af_clean_s42's loss.
- P3 T-C1b D13': −0.02 [−0.04, 0.00]. FAILED on at least one corpus 0.45; HELD on either 0.05 (G13 −0.0215).
- P4 T-C2 D2: +0.02 [−0.02, +0.05]. HELD 0.40; DP above the random p95 0.95.
- P5 T-C7 D7: −0.010 [−0.040, +0.020]. EQUIVALENT 0.50; LOSS 0.10 (SLOTSWAP; matched k removes the granularity effect).
- P6 T-C9 D9: +0.30 [+0.20, +0.40]. HELD 0.95 (SLOTSWAP M1, D_Q 0.469 on k-means cells).
- P7 T-C8: MASSIVE +0.03 [+0.01, +0.06]; CLINC +0.08 [+0.04, +0.12]. HELD 0.80; T-C8b HELD 0.65 (checkpoint A (c)3).
- P8 T-C4 r: MASSIVE 0.35, CLINC 0.30. HELD 0.65.
- P9 T-C3 slope sign positive: 0.80.

**Falsifiers** (none revises a recorded number).
- **F-S1a:** T-C1 LOSS on both corpora. FLAT-MIX-MMLU's partition clause then extends from MMLU-Pro to known-answer intent corpora, for the AF recipe at qwen3 256.
- **F-S1b:** T-C1b FAILED on both corpora. G13's failure ("the tree files below label-conditioned prototypes") then becomes a property seen on known answers, not one tree.
- **F-S1c:** T-C9 FAILED. The margin mechanism (SLOTSWAP M1) does not carry to tree leaves, and "abstain on low margin" is not a remedy route for the tree.
- **F-S1d:** T-C8 FAILED on either corpus. "flatLeaf over descent" (G11 D_fd; MC-ROOT) does not hold against gold.
- **F-S1e:** P0 fails. Construction determinism (G10 as sets) does not transfer to intent builds, and the lane stops.
- **Positive branch, registered now:** T-C1 EQUIVALENT on both corpora AND T-C7 EQUIVALENT. The record may then write its first parity sentence for tree against flat clustering: "on two known-answer intent corpora, the AF tree's leaves partition and hold addresses as well as flat k-means at matched k, within a quarter of the ceiling gap (qwen3 256, one draw, RAW)".

**Cost.**
- 0 calls.
- Machine: an estimate, unsourced; the cost-estimator re-prices. 8 qwen3 builds plus 1 gemma build, on about 10-14k short TRAIN+GATE texts, at 12 threads and 0.5-1 h each, about 5-9 machine-h in total. This is scaled from RP12-R2's 4-6 h for 4 builds plus a 300-rep null. There is no site null. CPU readouts about 1-2 h single-threaded (20-seed k-means at k = L).
- Agent time: engine-coder about 10-16 h (intent DatasetType, build-DB exporter, readout); tree-construction specialist (TOMLs); reviewer READY and post-run; registrar.
- Dependencies:
  - E1-ROUTE READY (B-E1-1, B-E1-2 cleared). Every arm reads S0's DBs through the working-copy route, not only the gemma arm.
  - EMBED-DIM-SLICE's d_g* for M-AF-g.
  - Lane order: AFTER RP13's single build.

## 2. RP13 UNION-AF-ROUTE, re-scoped (the author's D4): registration text (for the registrar)

**Heading.** `## Registered <date> (before any code or call) — UNION-AF-ROUTE: on the content-closed v2 union split (draw 5a3e756), do the cells of a FRESH anchor-free, federated, TRAIN-only tree route the union roster above the best single model, above per-source k-means at matched counts (F-TAX L-1), and equivalently to declared labels within 1pp? (zero calls; one build; the author's D4)`

**Question and kind.**
- Kind: build (one construction), then CPU readouts. 0 LLM calls.
- This is the only label-free routing test. It discharges F-TAX L-1, the last open leg.
- A new object under CK-CLOSE-v1. No object of record is rebuilt (D4: disclose).
- It publishes aggregate G only, with no per-leaf model rows (rev2 L680).

**Prior results touched (none revised).**
- G14 (RP12-R2): G_tree +2.62pp [+1.43, +3.82]; M −0.05pp [−0.69, +0.59].
- V2-DECLARED-CELLS C1: +2.67pp [+1.46, +3.89].
- ROUTER-CLEAN-POLICY C3: leaf − domain −0.09pp (id-disjoint only).
- MC-LEAF: leaves lose to domains as a router (id-disjoint only).
- FLAT C1: T level with spherical k-means K3.
- F-TAX: N-1 FIRES; L-2 not fired; L-1 pending.
- Closed lines: none (no judge, rubric, sub-anchor row or frontier). MC-LEAF is not re-run: the comparator here is k-means, not domains.

**Hygiene.**
- Split: draw 5a3e756 (content-closed under CK-CLOSE-v2, residual disclosed). Union pool pv2_1575de61bb20e977: EVAL 6,153 items in 5,642 components.
- Verify with `pool_guard.py --pool pv2_1575de61bb20e977`.
- The construction reads TRAIN only (the TRAIN-ONLY guard). Label-free: no labelling, no induction, no leaf names.
- Rule 7 W1-W5; a backup before the build; 12 threads.
- Per-table hashes of `embeddings_cache.db` checked before and after (the build rewrites its tables: memory note).
- The declared-label comparator is leg U's frozen TRAIN policy file, its sha printed before EVAL opens (R3 of the framing record). No key output feeds any selection.

**Instrument.**
- Build AF-U:
  - RP12-R2's B0 member TOMLs (`experiment_configs/rp12_r2/B0/`, federated per source under a union root, routed flatLeaf), with anchors OFF (`anchorFree = true`);
  - the anchor-free recipe of record (af_clean_s42: z 2.0, mcs 55, 256-d slice, bar 0.025);
  - seed 42, run from one detached worktree pinned at one commit (D-8).
  - The 512 / 0.0145 anchored recipe is not used, and the recipes are never ranked against each other.
- Cells: AF-U leaves, flatLeaf-filed. A per-cell policy is fitted on TRAIN keyed accuracy by G14's reader, with its machinery and backoff rule unchanged. The two-stage bootstrap uses B 2,000 over CK-CLOSE components.
- Comparator K_s (fixed now):
  - within each source, spherical k-means (k-means++, n_init 1, max_iter 300) on that source's TRAIN items in the same 256-d slice;
  - k = AF-U's leaf count in that source;
  - an EVAL item is filed by its source to the nearest centroid;
  - seeds s = 0..4; G_K = mean over s; spread_K = max − min over s of G_K,s.
- Declared arm: G14's declared-cell policy refit in the same run. IDENTITY PRECONDITION: it reproduces +2.67pp [+1.46, +3.89] to the printed digits, else refuse.
- Readers TO BE BUILT: the AF-cell arm and the K comparator in the v2 RP03/G14 reader, inert when absent. The outcome is write-once at `experiment_results/archv2/union_af_route/outcome.txt`.

**Readouts and criteria** (two-stage 95% intervals, G14's machinery).
- **U1 (the INTERVAL decides).** G_AF = acc(per-cell policy on AF-U cells) − acc(best single model) on union EVAL. HELD iff lower > 0; FAILED iff upper <= 0; UNDETERMINED otherwise.
- **U2 (= F-TAX L-1, verbatim).** D_K = G_AF − G_K, paired.
  - L-1 FIRES iff the 95% interval lies wholly above 0 AND D_K > spread_K.
  - Reported beside: the reverse (interval below 0 AND D_K < −spread_K).
  - Otherwise "not fired: neither a gain nor parity is shown by U2".
- **U3 (TOSTs, delta = 1.0pp, Holm over the two; registered before code as F-TAX requires for any parity word).**
  - U3a: D_K (AF against per-source k-means).
  - U3b: M_AF = G_AF − G_declared.
  - EQUIVALENT iff the Holm-adjusted two-sided interval (95% for the first, 90% for the second) lies inside ±1.0pp.
  - delta = 1.0pp is about 0.37 of the declared-cell gain of 2.67pp. It is the research-lead's choice, open to the author before registration.
- **DESCRIPTIVE:**
  - per-source leaf counts;
  - P_fl and D_fd of AF-U against (source, domain) labels;
  - G_K per seed;
  - beside them: the anchored B0 G_tree +2.62pp (of record, not recomputed).

**Support.**
- (a) Deciding denominator: G14's 5,907 items in 5,404 components (after the Llama and variant rules; multi-class items kept; ruling (b)).
- (b) DEFF 1.392: measured by G14 on the same design (two-stage).
- (c) n_eff = 5,907 / 1.392 = 4,244.
- (d) SE:
  - U1: SE 0.61pp, from G14's interval width (3.82 − 1.43) / 3.92.
  - U2 and U3: the paired SE between two cell policies on the same EVAL, transported from G14's M interval: (0.59 + 0.69) / 3.92 = 0.33pp. spread_K has no source; planning 0.5pp [0.2, 1.0], measured in-run.
- (e) MDE80:
  - U1 1.71pp;
  - U2 0.91pp; its bar is max(MDE80, spread_K), planning 0.91pp;
  - U3: the Holm intervals have half-widths 1.96 x 0.33 = 0.65pp and 1.645 x 0.33 = 0.54pp. Equivalence is reachable iff the true absolute D < 0.35pp (first) or < 0.46pp (second).
- (f) VERDICT LINES:
  - U1 SCOREABLE (+2.4 against 1.71).
  - **U2 is DESCRIPTIVE-ONLY at its prediction** (+0.1 against a bar of 0.91). A FIRE is observable at n only if the true D_K >= about 1.8pp (bar + MDE).
  - U3a SCOREABLE (predicted absolute D_K 0.1 < 0.35).
  - U3b THIN (predicted absolute M_AF 0.2 < 0.35, by 0.15pp).
  - CONDITION FOR THE REGISTRAR (pre-data, F-TAX by insertion). F-TAX Support (f) says a leg whose test registers DESCRIPTIVE-ONLY "cannot fire". This registration proposes the reading "a fire OBSERVED under a DESCRIPTIVE-ONLY-at-prediction line counts as a fire; a non-fire reads 'not fired, by support'". The support limit binds non-fires, not fires. Without that bracket, U2 cannot move F-TAX in either direction.
- (g) STRUCTURAL LEG:
  - U1 is reachable.
  - U2's spread clause is reachable only if the true D_K exceeds spread_K, which does not shrink with n.
  - U3 is reachable iff the true absolute D is below the half-width margins stated in (e).

**Predictions.**
- U1: G_AF +2.4pp [+1.2, +3.6]; HELD 0.85 (G14; V2-DECLARED-CELLS).
- U2: D_K +0.1pp [−0.8, +1.0]; spread_K 0.5pp [0.2, 1.0]; L-1 fires 0.10. F-TAX's P2 of 0.15 is scored as registered there.
- U3a EQUIVALENT 0.45; U3b EQUIVALENT 0.40, with M_AF −0.2pp [−1.0, +0.6] (ROUTER-CLEAN-POLICY; G14 M).
- Leaves: AF-U 70-110 in total (af_clean_s42 had 82 on MMLU-Pro alone; federated sources add leaves).

**Falsifier.**
- F-U1 fires iff U1 FAILED. The union router gain on declared cells (+2.67pp) and on anchored tree cells (+2.62pp) then does not transfer to label-free cells.
- If L-1 fires, that is F-TAX's F1 (lever), and F-TAX's reading table then reads "a lever AND N-1: recorded joined, no sentence".

**F-TAX consequence (read through F-TAX's table only).**
- L-1 not fired: "a filing device only" (N-1 fired). The synthesis must add "(lever leg not fired, by support)" whenever U2 reads inside its bar.
- U3b EQUIVALENT adds the licensed parity clause "label-free cells route equivalently to declared labels within 1pp (content-closed union, this roster)".

**Cost.**
- 0 calls.
- Machine: one federated build, about 1.5-2.5 h at 12 threads (rev2 L525; the cost-estimator re-prices). No site null.
- CPU: readouts in minutes.
- Agent time: tree-construction specialist (TOMLs); engine-coder (the AF-cell arm and the K comparator in the G14 reader, about 3-4 h); reviewer READY and post-run; registrar.
- Lane: machine, serial with the CARD-PROTOCOL Ollama pass (one heavy process at a time; the experiment-manager orders the two), BEFORE stage 1's builds.

## 3. INTENT-S0-CARD-PROTOCOL, fixed for K1-K5 (prompt arm only; the dimension arm is EMBED-DIM-SLICE): registration text (for the registrar)

How each check is answered:
- **K1:** Support (a)-(g) is complete below.
- **K2:** CP1 is a total classification, the same as DS1. Its per-corpus lines are stated at the prediction: MASSIVE is DESCRIPTIVE-ONLY, CLINC and Banking77 are SCOREABLE.
- **K3:** the bar is the IN-RUN seed spread. S0's values are quoted per corpus as planning values only.
- **K4:** CP2 has its own pooled rule, Support and falsifier.
- **K5:** the prompt strings and DB paths are written in, and the timings are sourced or marked unsourced.

**Heading.** `## Registered <date> (before any code or call) — INTENT-S0-CARD-PROTOCOL: at each embedder's EMBED-DIM-SLICE-selected slice, does gemma's fine-level edge over qwen3 survive card-conformant prompts on both sides (CP1), and do card prompts raise qwen3's fine NMI over RAW (CP2)? (zero calls; Ollama re-embedding; no build)`

**Prior results touched (none revised).**
- S0 C1a: the gemma rows.
- SLOTSWAP M3.
- EMBEDDER-CROSS-FLAT: card-conformant is a registered secondary there.
- EMBED-DIM-SLICE: d_q* and d_g*, read from its selection file, sha printed.
- Closed lines: none.

**Hygiene.**
- S0's corpora, split, K_f, seeds 0-4 and functions are used verbatim (blob:f662ceb1).
- New DBs at the repo root (root `*.db` is gitignored):
  - `intent_emb_qwen3_card.db`
  - `intent_emb_gemma_card.db`
  - `intent_emb_nomic_card.db` (descriptive arm)
- Written through `embedder_arms.py`'s paced writer; meta `protocol CARD` plus the prompt's sha256.
- `embeddings_cache.db` and S0's three pinned DBs are never written. Their sha256 are checked before and after every pass, as are the per-table hashes of the shared caches.
- TRAIN-only fits; no pool of record.
- Ollama is one heavy process and never runs beside a construction.
- A zero-call TRANSPORT PREFLIGHT inside the dry-run embeds 20 texts per embedder and checks route parity (S0's bars: qwen3 0.9980, gemma 0.9999).

**Prompt strings (exact bytes, UTF-8; prepended to EVERY text of every side: TRAIN, GATE, EVAL, variants, OOS).**
- They are committed before any embedding in `experiment_configs/card_protocol_prompts.json`, whose sha256 the READY pins.
- qwen3 (the Qwen3-Embedding card's query form, `Instruct: {task}\nQuery:{query}`):
  - `"Instruct: Given a user utterance to a virtual assistant, identify the user's intent\nQuery:"` + text;
  - `\n` is one LF byte, and there is no space after `Query:`;
  - one task line for all three corpora, not tuned per corpus.
- gemma (the EmbeddingGemma card's clustering prompt): `"task: clustering | query: "` + text.
- nomic (the nomic-embed-text v1.5 card's clustering prefix; DESCRIPTIVE arm CP4): `"clustering: "` + text.
- The READY re-checks each string against the model card as published. A mismatch is a precondition failure, never a silent edit.

**Readouts and criteria** (BASIC component-bootstrap CI, B 2,000, partitions fixed; S0's C1 rule).
- **CP1 (deciding; POINT and INTERVAL, one conjunctive clause each way).** Per corpus:
  - D_card = mean_s NMI_EVAL(gemma, CARD, d_g*) − mean_s NMI_EVAL(qwen3, CARD, d_q*), at K_f.
  - BETTER iff D_card > bar AND CI > 0; WORSE symmetrically; NEITHER otherwise.
  - bar = max(MDE80, max(spread_qwen3,CARD, spread_gemma,CARD)), both spreads IN-RUN (max − min over seeds 0-4 of that arm's EVAL NMI).
  - VERDICT: REOPEN-CANDIDATE iff gemma is BETTER on >= 2 of 3; KEEP iff on <= 1; KEEP-STRONG iff gemma is WORSE on >= 2 of 3. The classification is total.
- **CP2 (deciding; pooled).**
  - D̄ = (1/3) Σ_c [mean_s NMI_EVAL(qwen3, CARD, d_q*) − mean_s NMI_EVAL(qwen3, RAW, d_q*)].
  - bar_pool = max(MDE80(D̄), the mean over corpora of max(spread_qwen3,CARD, spread_qwen3,RAW)), in-run.
  - HELD (card raises qwen3) iff D̄ > bar_pool AND lower(CI) > 0.
  - HURTS iff D̄ < −bar_pool AND upper(CI) < 0.
  - NOT SHOWN otherwise.
  - The CI is from a joint bootstrap over the three corpora, resampled independently per corpus.
- **CP3 (DESCRIPTIVE):** S under CARD for qwen3 and gemma at d* (MASSIVE, K 60, seeds 0-4), ceiling-normalised with the supervised-centroid S and the random co-filing floor recomputed per arm.
- **CP4 (DESCRIPTIVE):** the nomic CARD rows; gemma CARD − gemma RAW.

**Support.**
- (a) Deciding denominators, per corpus (S0 census):
  - MASSIVE 4,946 EVAL items in 4,923 components;
  - CLINC in-scope 6,672 in 6,672;
  - Banking77 3,908 in 3,905.
  - Kish: 1.0093 / 1.0000 / 1.0015.
  - CP3: 3,222 variants in 3,207 components.
- (b) DEFF and source: the Kish values above, measured in S0 on the same components (`s0_run.log` L23-L26). CP3: 1.0093 (SLOTSWAP).
- (c) n_eff: 4,900 / 6,672 / 3,902; CP3 3,192.
- (d) SE, arithmetic:
  - CP1 per corpus: S0's measured paired bootstrap SE(D) (gemma − qwen3, fine, 256) of 0.00289 / 0.00137 / 0.00247, transported (same items and pairing; only the protocol and slice differ) and re-measured in-run.
  - CP2: SE(D̄) = sqrt(0.00289^2 + 0.00137^2 + 0.00247^2) / 3 = sqrt(1.633e-5) / 3 = 0.00135. This is conservative: a within-qwen3 protocol pair is at least as correlated as a cross-embedder pair.
- (e) MDE80 = 2.8 x SE:
  - CP1 0.0081 / 0.0038 / 0.0069;
  - CP2 0.0038.
  - Planning bars (S0 at 256, max of the two arms' spreads, quoted per corpus): **0.0246 / 0.0094 / 0.0143**.
  - CP2 planning bar_pool: (0.02463 + 0.00942 + 0.01434) / 3 = **0.0161**.
  - The bars of record are the in-run values (K3).
- (f) VERDICT LINES at the predictions:
  - CP1 Banking77 SCOREABLE (+0.035 is 0.021 beyond 0.0143, more than its MDE of 0.0069).
  - CP1 CLINC SCOREABLE (−0.025 is 0.0156 beyond −0.0094, more than its MDE of 0.0038).
  - CP1 MASSIVE DESCRIPTIVE-ONLY (+0.010 lies inside 0.0246).
  - So CP1's classification is SCOREABLE, and KEEP reads "not shown", never "explained by protocol".
  - CP2 THIN SCOREABLE (+0.020 is 0.0039 beyond 0.0161, against its MDE of 0.0038).
  - CP3 and CP4 DESCRIPTIVE-ONLY.
- (g) STRUCTURAL LEG:
  - CP1 and CP2 are reachable at infinite budget only where the true difference exceeds the in-run seed spread, which does not shrink with n. Inside it, a corpus reads NEITHER and CP2 reads NOT SHOWN at any budget (stated now).
  - HELD, HURTS, KEEP and REOPEN are all reachable.

**Predictions (80% intervals; priors named).**
- CP1 D_card: MASSIVE +0.010 [−0.010, +0.030]; CLINC −0.025 [−0.040, −0.010]; Banking77 +0.035 [+0.015, +0.055].
  - Prior: EMBED-DIM-SLICE's P3 plus a qwen3 instruct gain of about +0.015 (the model card's instruction claim) against a gemma prefix gain of about +0.003.
  - Verdict: KEEP 0.75 (KEEP-STRONG 0.10), REOPEN-CANDIDATE 0.25.
- CP2 D̄: +0.020 [0.000, +0.040]. HELD 0.45, HURTS 0.05.
- CP3: under CARD, gemma S − qwen3 S = +0.04 [+0.01, +0.07].
- The predictions are conditional on EMBED-DIM-SLICE's d*. If its outcome moves P3 by more than 0.01 on any corpus, the registrar brackets the shifted CP1 points pre-data (the criterion is unchanged).

**Falsifiers.**
- **F-CP1:** fires iff CP1 reads REOPEN-CANDIDATE. It overturns the reading that protocol explains S0's gemma edge. Together with EMBED-DIM-SLICE REOPEN-CANDIDATE, it satisfies the first of D3's revisit conditions (CP1 HELD-in-the-gemma-direction); E1 remains.
- **F-CP2:** fires iff CP2 is NOT SHOWN or HURTS.
  - It withdraws "qwen3 is instruction-aware and was run RAW" as a candidate MECHANISM for S0's qwen3 rows. The sentence stays as a disclosure only.
  - HURTS additionally says the RAW protocol of record is the better one for qwen3 on intent clustering.

**Reading against D3 (the author's).**
- KEEP on both EMBED-DIM-SLICE and CP1: D3 stands, and neither the slice nor the protocol is shown to hide a gemma advantage.
- REOPEN-CANDIDATE on both: the evidence for the author's revisit is complete except E1 and quantisation (EMBED-QUANT, an option).
- Mixed: relayed as mixed; no wording is chosen here.

**Cost.**
- 0 calls.
- Ollama, one heavy process, serial; all timings unsourced:
  - gemma and nomic about 20-25 min each (from S0's DB file mtimes 05:55 -> 06:16 -> 06:39, assuming back-to-back passes);
  - qwen3 has no clean timing (S0 embedded it across several --go sessions after the TIME_WAIT incident). Planning 60-120 min RAW, and up to 2-3x that with the instruct prefix (the prefix is about 20 tokens on utterances of about 8).
  - The dry-run's 500-text timed probe prices each pass. Total about 2-5 h.
- CPU readouts about 1 h.
- Agent time: engine-coder about 2 h (the card writer on `embedder_arms.py`; the readout imports S0 and EMBED-DIM-SLICE functions); reviewer READY and post-run; registrar.
- Order: after EMBED-DIM-SLICE's outcome (it needs d*).

## 4. EMBED-QUANT (OPTION for the author; not to be registered without the author's go on the download)

**Recommendation.** Register and run it ONLY IF EMBED-DIM-SLICE or CP1 reads REOPEN-CANDIDATE. Otherwise, disclose "qwen3 Q4_K_M, gemma BF16; quantisation not tested" and stop.
- Reason: under KEEP, a quantisation effect could only make qwen3 better (Q4 loses information), which would strengthen KEEP. Under REOPEN, quantisation is the last named confound.

**Heading (draft).** `## Registered <date> (before any code or call) — EMBED-QUANT: is qwen3-embedding's Q4_K_M quantisation a confound of the intent-corpus embedder contrasts, i.e. is fine NMI at d_q* equivalent between Q4_K_M and a higher-precision tag (Q8_0) within the k-means seed spread? (zero calls; one Ollama re-embedding; no build)`

**Instrument.**
- Pull `qwen3-embedding:8b-q8_0` (about 8 GB; the tag's availability is checked at pull time; F16 at about 15 GB is the alternative, the author's choice).
- Re-embed S0's 57,350 texts RAW into `intent_emb_qwen3_q8.db` (root; `embedder_arms.py` writer; transport preflight; S0's pins re-checked).
- Readouts at d_q* (EMBED-DIM-SLICE), S0's functions, seeds 0-19 (the seed term enters the TOST).
- Printed: median and min cos(Q8, Q4) per text after slicing.

**Criterion EQ1 (TOST; the INTERVAL decides).** Per corpus:
- D_q = mean_s NMI_EVAL(Q8) − mean_s NMI_EVAL(Q4).
- delta_c = the corpus's in-run qwen3 seed spread at d_q* (planning 0.0246 / 0.0094 / 0.0143). That is: equivalence within what every embedder contrast in this family can resolve.
- EQUIVALENT iff the 90% CI lies inside ±delta_c, with SE_total = sqrt(SE_boot^2 + var_seed / 20).
- VERDICT:
  - NOT-A-CONFOUND iff EQUIVALENT on >= 2 of 3;
  - CONFOUND-CANDIDATE iff the absolute D_q exceeds delta_c with the 95% CI excluding 0 on >= 2 of 3 (direction printed);
  - UNDETERMINED otherwise.

**Support.**
- (a) As CP1: 4,946 / 4,923; 6,672 / 6,672; 3,908 / 3,905.
- (b) Kish as S0.
- (c) n_eff 4,900 / 6,672 / 3,902.
- (d) SE_boot: transported, conservatively, from S0 (0.00289 / 0.00137 / 0.00247). Seed term: spread / 2.33 / sqrt(20) = 0.00236 / 0.00090 / 0.00138. SE_total = 0.00373 / 0.00164 / 0.00283.
- (e) 90% half-widths: 0.0061 / 0.0027 / 0.0047.
- (f) SCOREABLE at the prediction (absolute D_q of about 0.003, inside delta − half = 0.018 / 0.0067 / 0.0096).
- (g) Equivalence is reachable iff the true absolute D_q < delta − half.

**Predictions.**
- NOT-A-CONFOUND 0.70 (prior: Q4_K_M usually costs little on embedding benchmarks; unverified here).
- Absolute D_q 0.003 [0.000, 0.010].
- Median cos(Q8, Q4) >= 0.98: 0.85.

**Falsifier.** CONFOUND-CANDIDATE overturns the use of the Q4 tag as "qwen3" in every intent-corpus embedder contrast (S0 C1a, SLOTSWAP M3, EMBED-DIM-SLICE, CP1). Those rows then carry "Q4_K_M; the higher-precision model differs".

**Cost.**
- 0 calls.
- Download about 8 GB (or 15 GB) — the author's call on disk and network.
- Ollama: one qwen3 pass, unsourced; planning 60-150 min (a Q8 model is slower than Q4).
- CPU about 1 h.
- Agent time: engine-coder about 1-2 h (a model-tag flag on the writer and a --quant arm on EMBED-DIM-SLICE's script); reviewer; registrar.

## 5. Paid-run readiness: RP21 (about 1.8k matches) -> RP20 (about 3.5k) -> RP19 (above 4k; after RP20 AND D2)

The common gates for every paid run (rule 2, rule 5, KNOWLEDGE §2):
- a registration with Support;
- the RP32 preconditions;
- a READY carrying a zero-call TRANSPORT PREFLIGHT inside the dry-run, before any journal or ledger row;
- dry-run -> pilot 12 (the truncation guard refuses above 5% unparsed) -> run -> --analyze (refuses partial caches);
- the day cap of 14,000 calls per posting day;
- no construction concurrent. Paid days fall in machine-lane gaps, which conflicts with RP13 and S1 builds, so the experiment-manager places them.

| gate | what it is | state at 47c72bb5 | owner | blocks |
|---|---|---|---|---|
| RP32a READY-TEMPLATE-TRANSPORT | the READY template gains checks (a)/(b)/(c): a transport preflight in the dry-run, load_env on the dry-run path, refusal when the count is 0 | drafted, NOT built; the reviewer must show it refuses on the K46 incident state (64ff708) | engine-coder -> reviewer | RP21, RP20, RP19 |
| RP32b STACK-JUDGE-RO-CACHE | 7 analysis originals open caches read-write | drafted, NOT built | engine-coder -> reviewer (a READY per blob) | RP20 and RP19 if their instruments import `stack_judge` or any of the 7. RP21's canary path does NOT call `open_cache` (canary_baseline.py L78-L83 guard); the reviewer confirms the guard covers the new pass modes |
| CANARY-ANALYZE-FIX | `--analyze` prints the ALARM STATE line, the convention-A floor and the measured-SE MDE, so a re-run cannot wipe the 4178a7c insertions | code MERGED (fcd200ea, fixes 5e9455b3 and d6c54231); READY ad65d094 conditional with the selftest blocker; NO delta READY on the fix and NO phase-B selftest recorded; queue says "drafted" (drift) | reviewer: delta READY plus the phase-B selftest on a SCRATCH copy, never `--analyze` on the epoch-1 outcome file; registrar corrects the queue | RP21 (both legs) |
| RP21 registration | G17: the v2 canary (1,224 matches) plus the v1 epoch 3 (about 624) | NOT registered; no queue item; the v2 canary not drawn | judge-design-specialist drafts (draw rule, legs, Support with CANARY-EPOCH2-RUNG's measured DEFF 1.169 and n_eff 256.6 per 300) -> registrar | RP21 |
| RP21 v2 instrument | the v2 recipe (the K46 store's recipe) posting a canary | NOT built: canary_baseline.py is the STACK-v2 v1 instrument | engine-coder (worktree) -> reviewer | RP21 v2 leg |
| RP21 v1 epoch-3 code | canary_baseline.py `--pass` accepts 1-4 only (L1808); epoch 3 needs new pass ids and their pins and pre-flights | NOT built | engine-coder -> reviewer delta READY | RP21 v1 leg |
| 2026-10-08 date gate | the v1 epoch-3 leg must be at least 2 weeks after 09-24 (#99) | binding | run-operator | RP21 v1 leg only |
| RP20 registration | V2-NONE-TEMPLATE plus REF-PAIRED-V2 on the K46 store; prices the false "carries a reference" sentence (69.3% of K46's matches) | NOT registered; depends on RP04 (K46-KEY-READ, done: ONE A 0.8787, DEFF 2.727) | judge-design-specialist (the N1 NONE template text, its Support from K46-KEY-READ's measured DEFF) -> registrar | RP20 |
| RP20 instrument | posting the NONE template | NOT built | engine-coder -> reviewer | RP20 |
| RP20 optional ONE leg | +about 2,400 matches, about 5,920 in total | needs THE AUTHOR'S GO (above 4,000) | author | RP20 optional leg only |
| RP19 | G21 re-scoped; go GIVEN ("Go, after RP20") | waits on RP20's outcome AND D2 (the author's ruling relayed 2026-10-01; the registrar records it); not registered; at most about 14k cce | — | — |

**Shortest path to READY.** Agent lanes run in parallel today; nothing posts before its READY.

1. **Today, zero calls, in parallel:**
   - (a) engine-coder builds RP32a, and RP32b for the scripts RP20 will import, in worktree `paid-pre`;
   - (b) reviewer writes the CANARY-ANALYZE-FIX delta READY and runs the phase-B selftest on a scratch copy;
   - (c) judge-design-specialist drafts the RP21 and RP20 registrations, and the registrar commits them.
2. engine-coder builds RP21's v2 canary instrument and the epoch-3 pass code, then RP20's NONE-template instrument, each with a transport preflight inside `--dry-run`.
3. reviewer writes READY on each instrument, under the new template.
4. **RP21 v2 leg:** run-operator, on its own posting day (dry-run -> pilot 12 -> run). Earliest: the day after step 3. Under 4,000 matches, so no author go is needed.
5. **RP20:** its own posting day, after RP21's v2 floor exists (checkpoint B: needed before RP20's paired reading). Under 4,000 without the ONE leg.
6. **RP21 v1 epoch-3 leg:** any posting day on or after 2026-10-08.
7. **RP19:** registered after RP20's outcome; posts only after D2 as well; its own posting day; the author's go is already quoted (Amendment 31).

Critical path to the first paid call: steps 1(a), 1(c) -> 2 -> 3. This is about 1-2 agent-days, gated by the two instruments, not by any author decision.

## 6. Plan of delegation (briefs; each "report in the KNOWLEDGE §0 format"; pins per KNOWLEDGE §1; the verified facts at the top of this file are not re-verified)

1. **registrar.**
   - Register §2 (RP13) and §3 (CARD-PROTOCOL) verbatim.
   - Register §1 (S1) once the tree specialist's TOML review (brief 3) confirms the arm list.
   - Insert the F-TAX pre-data bracket proposed in §2 (f).
   - Record the author's "RP19 waits for RP20 AND D2".
   - Correct the CANARY-ANALYZE-FIX queue state (merged fcd200ea / 5e9455b3 / d6c54231; delta READY owed).
   - Queue EMBED-QUANT as an OPTION (author_decision: download).
   - Acceptance: the rule-9 re-grep; the closed-lines check; K1-K5 answered (§3 header).
2. **engine-coder** (worktree `paid-pre`, from main). RP32a (READY-TEMPLATE-TRANSPORT), then RP32b for the scripts RP20 will import. Both inert when absent, with execution discriminators. Acceptance: RP32a refuses on the K46 state 64ff708 by execution. Hand to the reviewer.
3. **tree-construction-specialist.**
   - The RP13 AF-U TOMLs (B0 members with `anchorFree = true` and the af_clean_s42 parameters).
   - The S1 arm TOMLs (M-AF / M-AF' / M-o1 / M-o2 / M-AF-s2 / M-AN / C-AF / C-AN; M-AF-g after E1-ROUTE).
   - Confirm the P1 leaf predictions, or flag any change before registration.
   - Output under `experiment_configs/union_af_route/` and `experiment_configs/intent_s1/`.
4. **engine-coder** (worktree `union-af-route`). The AF-cell arm and the per-source K comparator in the G14 reader, inert when absent. Its dry-run prints the pool guard, the denominators (5,907 / 5,404), the declared identity +2.67pp, and the frozen-policy sha before EVAL. Then the reviewer.
5. **engine-coder** (worktree `card-proto`). The card writer and the readout, with a dry-run that prints the three prompt strings with their sha256, the DB paths, the S0 pins, the transport preflight and the 500-text timing. It waits for EMBED-DIM-SLICE's selection file to run, not to be built.
6. **engine-coder** (worktree `intent-s1`, after E1-ROUTE's B-E1-1/2 fixes). The intent DatasetType (fail-closed), the TRAIN+GATE build-DB exporter, and `intent_transfer_s1.py`.
7. **judge-design-specialist.**
   - Draft the RP21 registration (the v2 canary draw rule; leg composition; Support with DEFF 1.169 from CANARY-EPOCH2-RUNG).
   - Draft the RP20 registration (the N1 NONE template text; Support from K46-KEY-READ's DEFF 2.727).
   - A reachable criterion each.
   - Output: plan-file texts for the registrar.
8. **adversarial-reviewer.**
   - The CANARY-ANALYZE-FIX delta READY plus the phase-B selftest on a scratch copy.
   - Then READY on each built script (RP32a/b, the RP13 reader, card-proto, intent-s1, the RP21/RP20 instruments).
   - Post-run on every number.
9. **run-operator.** In the experiment-manager's lane order: one heavy process at a time; rule 7 for the RP13 build and the S1 builds; paid legs on their own posting days.
10. **registrar** (after each outcome), then the **research-lead** writes the synthesis here.

## 7. Synthesis frames (fixed before data; filled after each outcome)

**INTENT-TRANSFER-S1.**
- Lets the framework say:
  - whether tree leaves are a partition and an address equivalent to flat k-means on known answers (first parity line);
  - whether flatLeaf beats descent against gold;
  - whether a label-free margin buys stability by abstention on tree leaves.
- Refuses: certification (not measured); routing (no models).
- Opens: stage 1b (union absorption) and stage 2 (soft routing on the capability side).
- **Does NOT show:**
  - anything about capability text or MMLU-Pro;
  - routing value;
  - certified sites;
  - sub-anchor profiles (the anchored arm discovers intents, never profiles);
  - embedder invariance (gemma rows are descriptive);
  - a tree draw effect beyond MASSIVE's arms;
  - that EQUIVALENT means "better" (or that a non-EQUIVALENT means worse);
  - anything about the anchored recipe against the AF recipe (never ranked).

**RP13 UNION-AF-ROUTE.**
- Lets the framework say: whether label-free cells route above the best single model, and (U3b) equivalently to declared labels within 1pp.
- F-TAX gets its last leg.
- Refuses: "the taxonomy is a lever" unless L-1 fires; any per-leaf model row.
- Opens: a reference point against key-projected space (RP41); the soft-routing stage 2.
- **Does NOT show:**
  - that the tree beats clustering in general (one draw, one recipe, one roster, qwen3 256);
  - a gain over declared labels;
  - parity outside ±1pp, or parity at all if U3 is not EQUIVALENT;
  - anything for MMLU-Pro alone (the union mix carries the gain, BBH-heavy per RP03);
  - any certificate;
  - that a non-fire of L-1 is evidence of no lever (U2 is DESCRIPTIVE-ONLY at its prediction).

**CARD-PROTOCOL.**
- Lets the framework say: whether the gemma edge is protocol, and whether RAW under-served qwen3.
- Refuses: an embedder switch (D3 is the author's).
- **Does NOT show:**
  - quantisation effects;
  - capability text;
  - parity (no TOST);
  - that MASSIVE's NEITHER is explanation.

**EMBED-QUANT (if run).**
- **Does NOT show:**
  - F16 behaviour, if Q8 is pulled;
  - anything about gemma's quantisation;
  - capability text.

**Paid lane.**
- RP21 gives the v2 retest floor and the v1 time point.
- RP20 prices the NONE template.
- Neither gives SQ2's content-closed fidelity; that is RP19, after D2.

## 8. Decisions that are the author's

- **D2:** the v2 reference policy and SQ2's instrument. Open; RP19 waits on it as well as on RP20.
- **D6:** the SQ3 thesis wording. Open; F-TAX's sentence is read after RP13.
- **EMBED-QUANT:** download about 8 GB (Q8_0) or 15 GB (F16). Recommended only if a REOPEN-CANDIDATE appears.
- **RP20's optional ONE leg:** above 4,000 matches.
- **D3:** after EMBED-DIM-SLICE, CARD-PROTOCOL and E1. The Gemma licence and mxbai stay undecided (D3 note).
- **RP13 U3's delta of 1.0pp:** the research-lead's choice. The author may change it BEFORE registration, because it fixes the thesis's parity words.

Research-lead decisions, not the author's:
- the arm lists;
- the ceiling-relative deltas;
- dropping the S1 site null;
- the F-TAX bracket proposal;
- the lane order, which goes to the experiment-manager.

## 9. What can start building today (zero calls)

- **Already running:** EMBED-DIM-SLICE (CPU).
- **Engineering, in parallel worktrees:**
  - RP32a and RP32b (`paid-pre`);
  - the RP13 reader arm plus the K comparator (`union-af-route`);
  - the card-proto writer and readout (`card-proto`);
  - E1-ROUTE's B-E1-1/2 fixes (which unblock S1);
  - the S1 DatasetType and exporter.
- **Reviews and registrations:**
  - the CANARY-ANALYZE-FIX delta READY;
  - the judge-design-specialist's RP21 and RP20 drafts;
  - the registrar commits RP13 and CARD-PROTOCOL.
- **Machine lane, once READY, serial:**
  - EMBED-DIM-SLICE -> CARD-PROTOCOL Ollama pass and RP13 build (either order; one heavy process) -> S1 builds.
  - Paid legs go in the gaps: RP21 v2, then RP20, then RP21 v1 on or after 10-08, then RP19 after RP20 and D2.
