# Research checkpoint B (research-lead), 2026-10-01: the thesis story per SQ, lines to close, the 24-48 h queue, author decisions

Inputs:
- the caller's evidence list;
- docs/agents/results/{ARCH-V2-E-T-R2, MMLU-GOLD-GEOMETRY, INTENT-S0-SLOTSWAP-MECH, LCB-STAGE0-POWER-RESIM, E1-ROUTE}.json;
- prog "## ARCH-V2-E-T-R2 (2026-10-01, 0 calls) — PARTIAL" (L22511) and the ARCH-V2-E-T registration (L22028ff: G11-G14, FLAT, P3-P7);
- commits 9c9ee9e7 (G12) and 36f1310f (FLAT);
- framing SQ1-SQ5 (framing L35-L140);
- rev2 L392-L396 and L532-L534;
- checkpoint A (2026-10-01_checkpoint_A.md).

Zero calls. Nothing built, run or recorded by this checkpoint.

PROVISIONAL: G12 and FLAT are under post-run review in parallel. Every G12 or FLAT sentence below is the builder's reading, and none goes to the ledger before the review. If the review refutes either one, sections (a)-SQ3 and (b)3-4 are re-read.

## (a) The thesis story now (content-closed v2 split unless marked; split words per S3)

**SQ1 USE**
- CLAIMED. G14 HELD: G_tree +2.62pp [+1.43, +3.82] (two-stage; 5,907 items in 5,404 components; DEFF 1.392). The per-cell policy fitted on TRAIN, with cells read from the v2 tree, beats the best single model on content-closed union EVAL.
  - The declared-label policy gives C1 +2.67pp [+1.46, +3.89].
  - This is the content-closed sensitivity that replaces paeec's +2.92pp (id-disjoint only) as the headline. The words are "on the roster measured".
- AUDITED. Two-stage interval with measured DEFF. P5 (+2.5pp, HELD 0.85) is scored HELD.
- NEGATIVE / BOUNDED. Four limits:
  - M = -0.05pp [-0.69, +0.59] is DESCRIPTIVE-ONLY. Its words are "the tree's cells are not shown to cost or gain against declared labels", never parity.
  - The MMLU-Pro frontier roster gives zero (unchanged).
  - LCB is not evidence either way: G1 power is 0.22 at tau 0.20.
  - "Only where no model dominates" stays unlicensed.

**SQ2 TRUST**
- Unchanged today. No content-closed judged number exists under the v2 recipe.
- CLAIMED (id-disjoint only, or [P-FAM] with its bracket): the key's interaction R, and "fidelity tracks the reference's correctness".
- OPEN: the v2 recipe's no-reference branch (69.3% of K46's matches; RP20), the content-closed judged fidelity (RP19), and the v2 retest floor (RP21's canary leg).

**SQ3 TAXONOMY** (the day's main movement)
- CLAIMED. The content-closed tree is:
  - reproducible: G10 HELD after EMD, with per-node membership compared as sets;
  - order-stable: G15 HELD, max drift 0.0151pp;
  - a filer: G11 HELD, P_fl 0.8119 [0.8013, 0.8223] on 6,139 items in 5,628 components;
  - better as a flat leaf filer than by descent: D_fd +9.37pp [+8.28, +10.54]. This is the content-closed counterpart of MC-ROOT's +9.50pp (id-disjoint).
- CLAIMED, PROVISIONAL. FLAT C1 HELD: purity is +0.025 above a flat vMF mixture at matched k on the MMLU-Pro member.
  - P7 predicted -0.015 with C1 FAILED at 0.85. The prediction failed in the interesting direction, and it reverses af_clean_s42's -4.3pp (one tree, one draw, mechanism unidentified).
- AUDITED.
  - The R1 build FAILED G10 on intra-node list order. That failure is disclosed beside G10's HELD. G10 holds for set membership, which is weaker than R1's byte rule.
  - P_fl is a union mix: MMLU-Pro 0.745 (n 3,478) is below the 0.75 bar on its own; GPQA 0.673; MATH 0.621. BBH 0.973 and MUSR 1.000 carry the pooled bar.
- NEGATIVE.
  - G13 FAILED (genuine): D13 -0.0215 [-0.0301, -0.0125] against spread_KC 0.0112. The tree files worse than class-conditional k-means prototypes. Those prototypes use the declared labels; the tree does not.
  - G12 (provisional): N-1 FIRES. The hierarchical-BH set holds 0 of the 14 depth-1 sites (the caller counts 0 of 60 sites).
    - B-A2's soft wording is NOT available: MMLU-GOLD-GEOMETRY reads H 0.2912 against a p95 of 0.0264.
    - So the declared level IS geometric in qwen3 and the construction does not certify it.
  - FLAT C2 (F6) FAILED (provisional).
- F-TAX reading. The lever leg L-2 failed (G13). N-1 fires (G12). The record's sentence narrows to: "the tree buys reproducible TRAIN-only cells that file above descent and route without a shown cost, plus support and names; not a certificate, not filing beyond label-conditioned prototypes, not a routing gain over declared labels". The label-free case (RP13) is the one leg still able to move it toward "lever".

**SQ4 PRICE**
- Unchanged: "priced, and UNDETERMINED".
- RP21 is the only time instrument. Its v1 epoch-3 leg is date-gated (at least two weeks after 09-24, so not before 2026-10-08).

**SQ5 INVARIANCE**
- CLAIMED (RAW protocol, one draw).
  - Fine partitions depend on the embedder against gold labels, in both directions, on 3 intent corpora (S0 C1a) as well as MMLU-Pro.
  - A label-free cell is a surface-sensitive address: C4 FAILED and F4 fires (S 0.760).
  - The mechanism is both of SLOTSWAP's effects:
    - M1, origin margin: D_Q 0.469 [0.425, 0.512];
    - M2, swap share: D_T 0.141 [0.107, 0.175].
  - Label-free abstention detects curated OOS at AUROC 0.974 (C2). [CORRECTED 2026-10-02 by OOS-BASELINES (registrar; W-1 of docs/reviews/POSTRUN_oos_baselines.md, c5416c52): flat spherical k-means cells (K = 150) on qwen3-256 RAW vectors of CLINC150 (oos_plus), never the tree; equivalent within 0.010 AUROC to labelled centroid / class-Mahalanobis detectors, ahead of kNN k 10 and marginal Mahalanobis (k- and K-conditional, W-2); docs/judge_v2_program.md L23567-L23578 (section "## OOS-BASELINES (2026-10-02, 0 calls) — VALID ..."; _as_of the commit that writes it, parent c5416c52)] Margin ranks purity on 2 of 3 corpora (C3).
- DESCRIPTIVE. gemma beats qwen3 on gold geometry and on stability (S 0.826 vs 0.760, +0.066 [+0.052, +0.082]; one seed, RAW). MMLU-Pro's H is 0.29, between CLINC 0.14 and MASSIVE 0.40.
- NEGATIVE / INCONCLUSIVE.
  - No embedder parity is claimed (no TOST).
  - LCB adds no corpus evidence: power 0.22, and size 0.0075 at tau 0.

## (b) Open lines to close (registrar records each closure by insertion; S5 then binds)

1. **LCB judged line at this roster and design**: CLOSED. The STOP stands, and the power words become "inconclusive at power 0.22 [0.18, 0.27]; tau80 > 0.30". RP14 is closed. A new LCB test needs a new roster or a new corpus design.
2. **G10's canonical node order (ruling (B))**: not pursued. The claim of record is "deterministic up to intra-node order". Reopen only if a reader depends on list order.
3. **Certification as an SQ3 deliverable on MMLU-Pro** (after the G12 review confirms): close CERT-FAMILYWISE-REPS, RP24 (held-out certificate) and RP25 (power).
   - 2/70 (bareq512_s42), the empty s2048 set and 0 depth-1 sites on v2 now span three trees, so more reps cannot rescue a deliverable.
   - The dip half of L6 stays open (the statistic is different).
4. **Tree-as-lever filing (G13)**: closed as registered. No re-run at other k_c, slices or comparators (forking paths). Only stage 1's known-answer T-C1 may revisit tree vs k-means, and on other corpora.
5. **Absolute stability bars** (C4-style): retired. Every future stability criterion is relative, with a ceiling arm (checkpoint A (c)1).
6. **Embedder parity wording**: closed. SQ5 says "the fine partition belongs to the embedder". Any invariance claim needs a TOST registration.

Stays OPEN, each with a mechanism the record has not seen: RP13 (the label-free case), CARD-PROTOCOL (the RAW confound), FLAT-MIX-ANCHORED (RP05 arm (a): do the anchors explain the FLAT C1 reversal?), intent stage 1, and RP19-RP21.

## (c) Queue, next 24-48 h (re-ranked)

Constraints: rule 7; one heavy process; no paid run beside a construction; day cap 14,000 calls; each paid run needs registration -> RP32 preconditions (READY-TEMPLATE-TRANSPORT, STACK-JUDGE-RO-CACHE, both drafted) -> READY with a transport preflight.

| # | item | lane | cost | gate / why here |
|---|---|---|---|---|
| 1 | G12 and FLAT post-run reviews, then the RP12 outcome, ledger row, F3 | agent | 0 | everything in (a)-SQ3 waits on them |
| 2 | RP32 preconditions + CANARY-ANALYZE-FIX (engine-coder -> reviewer) | agent | 0 | gates every paid run |
| 3 | INTENT-S0-CARD-PROTOCOL (registration text below) | Ollama, heavy, ~1-2 h | 0 calls | decides whether gemma's edge is protocol; informs decision D3 |
| 4 | RP21 v2-canary leg (~1,224) | paid | < 4k, no go | v2 retest floor, needed before RP20's paired reading; its own posting day |
| 5 | E1 (RP09) after E1-ROUTE clears B-E1-1/2 | machine, construction | 0 | FLAT's embedder qualifier; F-E1 pre-registered |
| 6 | FLAT-MIX-ANCHORED (RP05 arm a), re-pointed to explain the FLAT C1 reversal | CPU reader | 0 | only after the FLAT review confirms C1 |
| 7 | RP20 V2-NONE-TEMPLATE (~3.5k matches) | paid | < 4k, no go | prices the false "carries a reference" sentence; feeds the reference policy (D2) |
| 8 | RP13 re-scoped (see D4): fresh anchor-free union build on draw 5a3e756 TRAIN, then the routing contrast | machine (~1.5-2.5 h) + CPU | 0 | the only leg that can move F-TAX; script absent, tree specialist drafts |
| 9 | Intent stage 1 registration (tree specialist; checkpoint A (c)1-6, plus T-C1 vs k-means as the known-answer counterpart of G13) | agent, then machine | 0 | the author's D5: after RP12's outcome |
| 10 | CAPABILITY-SURFACE-FILING (B0 now exists) | Ollama + CPU | 0 | discharges F4's "untested on capability text" |
| — | RP21 v1 epoch-3 leg (~624) | paid | — | not before 2026-10-08 |
| — | RP19 G21 (~5k matches, <= ~14k cce) | paid | > 4k | the author's GO; after RP20 and D2; its own posting day |

Concurrency: items 3, 5, 8 and 10 are serial on the machine lane. Paid items 4 and 7 run in no-construction windows on different posting days. Agent lanes run in parallel.

### Registration text (for the registrar): INTENT-S0-CARD-PROTOCOL (embedder-of-record evidence)

**Question.** Does gemma's fine-level edge over qwen3 (RAW: +0.033 and +0.056 NMI on 2 of 3 corpora; S +0.066) survive card-conformant prompts on both sides?

**Instrument.** S0's C1a fine NMI and SLOTSWAP's S, with the functions verbatim (S0 blob f662ceb1) and the corpora, split, K and seeds as S0.
- Card prompts, as published on each model card:
  - qwen3: its Instruct/Query form with an intent-retrieval task line;
  - gemma: the "task: clustering | query:" prefix;
  - nomic: the "clustering:" prefix.
- The texts are fixed before any embedding.

**Hygiene.**
- New per-(model, protocol) DBs. embeddings_cache.db and S0's pinned DBs are never written; they are re-hashed before and after.
- TRAIN-only fits. No pool of record is read.
- Ollama is one heavy process and never runs beside a construction.

**Criteria** (component-cluster bootstrap, B 2000).
- CP1: D = NMI(gemma, card) - NMI(qwen3, card) at fine K, per corpus. HELD iff on at least 2 of 3 corpora lower(95% CI) > 0 AND D > that corpus's k-means seed spread. FAILED iff on at least 2 of 3 corpora upper <= 0. UNDETERMINED otherwise.
- CP2: NMI(qwen3, card) - NMI(qwen3, RAW), with the same rule.
- CP3 (DESCRIPTIVE): S under card prompts for each embedder, ceiling-normalised.

**Predictions.**
- CP1: D +0.015 [-0.02, +0.045]; HELD p 0.40, FAILED p 0.15.
- CP2: +0.02 [0.00, +0.05]; HELD p 0.55.

**Falsifier.** CP1 FAILED overturns "gemma's fine edge belongs to the embedder" (the S0 C1a direction, and the descriptive gemma > qwen3 rows), which is then read as protocol.

**Support.**
- S0 measured SE 0.0014-0.0048 (MDE80 at most 0.013) and seed spreads 0.009-0.025 at fine K, so the effective bar is the spread.
- The RAW gaps (0.033, 0.056) exceed it: SCOREABLE on MASSIVE and Banking77.
- CLINC (gemma not better RAW) is DESCRIPTIVE.
- Structural leg: HELD and FAILED are both reachable at infinite budget.
- CP3: DESCRIPTIVE-ONLY.

**Cost.** 0 calls. Ollama re-embedding of ~57,350 texts x 3 (about S0's ~50 min each pass, unsourced). engine-coder ~2 h. One review.

## Plan of delegation (briefs; each "report in the KNOWLEDGE §0 format"; pins per KNOWLEDGE §1)

1. **adversarial-reviewer** (running): G12 and FLAT post-run.
   - Verified already: the R2 lane READY and merges (prog L22494, L22532).
   - Acceptance: CONFIRMED / REFUTED on N-1, C1 and C2.
   - Output: docs/reviews/POSTRUN_rp12_r2_g12flat.md.
2. **registrar**:
   - the RP12 outcome after (1);
   - closures (b)1-6 by insertion, (b)3 only if G12 is confirmed;
   - register CARD-PROTOCOL from the text above;
   - record the RP13 re-scope as a draft pending D4.
   - Acceptance: rule-9 re-grep and the closed-lines check.
3. **engine-coder** (worktree paid-pre, from main): RP32's two items and CANARY-ANALYZE-FIX, inert without a flag, then the reviewer. Then (worktree card-proto) CARD-PROTOCOL's script, with a --dry-run that prints the prompts, the DB paths and the hashes.
4. **judge-design-specialist**: drafts the RP20 and RP21-canary registrations. The v2 N1 template text and the canary draw are its own. Acceptance: Support with a measured DEFF source; a reachable criterion.
5. **tree-construction-specialist**: drafts the RP13 re-scope (anchor-free union build on 5a3e756 TRAIN under CK-CLOSE-v1; AF vs per-source k-means at matched counts; ARN-14 TOST) and stage 1. Acceptance: Support, plus the structural check.
6. **run-operator**: in queue order, dry-run -> pilot -> run, one construction or heavy process at a time.
7. **adversarial-reviewer** on every number, then the registrar, then the synthesis here.

## Synthesis (provisional on G12 and FLAT)

**The framework may now say:**
- On a content-closed split, a TRAIN-only tree is a reproducible (up to intra-node order) and order-stable filer.
- Its flat leaves beat its own descent by +9.4pp.
- Its cells route the union roster +2.6pp above the best single model, with no shown difference from declared labels.

**It refuses:**
- a certificate on MMLU-Pro (three trees now);
- filing beyond label-conditioned prototypes;
- a routing gain over declared labels;
- any v2 judged-fidelity claim;
- embedder invariance.

**It opens:**
- RP13, the label-free case;
- the anchors-and-purity mechanism (FLAT C1 reverses af_clean);
- CARD-PROTOCOL;
- stage 1's known-answer test of G13's failure.

**What this result does NOT show**
- That the tree is worse than k-means in general. G13's comparator uses declared labels; one tree, one draw, one embedder (qwen3 512-d slice).
- That the tree files MMLU-Pro above 0.75. The pooled 0.812 is carried by BBH and MUSR; MMLU-Pro alone is 0.745.
- Parity of tree cells with declared labels. M is DESCRIPTIVE-ONLY, with no TOST.
- Byte determinism. G10 holds for per-node membership as sets after EMD, and R1 failed on list order.
- That no site of the tree is real. N-1 concerns depth-1 sites in a hierarchical-BH set at 300 reps; the per-site p95 count is a different statement. G12 is provisional.
- That the declared MMLU-Pro level is non-geometric. H 0.29 says the opposite. The failure belongs to the certificate, not to the labels.
- That the v2 tree's purity edge generalises. FLAT C1 is one tree on one member, provisional, and its mechanism (anchors? federation?) is untested.
- That gemma is the better embedder. RAW protocol, one seed for S, descriptive; CARD-PROTOCOL is untested.
- That margin gating fixes surface sensitivity. Selective S 0.8375 is descriptive, not a criterion.
- Anything about LCB's interaction. Power 0.22 means absence of evidence.
- Any judged, SQ2 or SQ4 movement: zero calls today.

## (d) Decisions that are the author's (with recommendations)

- **D1, RP19 go (> 4k matches, <= ~14k cce).** Recommend GO, conditional: after RP20's outcome and D2, on its own posting day. It is SQ2's only content-closed v2 judged number.
- **D2, v2 reference policy and SQ2's instrument.** Recommend stating SQ2's content-closed claims under the v2 recipe with RP20's NONE template measured, and keeping STACK-v2 numbers as id-disjoint / [P-FAM] history.
- **D3, embedder of record (and the Gemma licence).** Recommend keeping qwen3 of record for the thesis: RP12 and all SQ1/SQ3 numbers are on it. gemma becomes a registered secondary arm. Revisit only if CARD-PROTOCOL CP1 HELD AND E1 does not fire F-E1.
- **D4, TRAIN-only rebuild-or-disclose (RP13's blocker).** Recommend: disclose for the existing objects, and approve RP13's re-scope to a fresh anchor-free build on draw 5a3e756 TRAIN. That is a new object under CK-CLOSE-v1, and no object of record is rebuilt.
- **D5, intent stage 1 go** (registered after RP12). Recommend GO once the RP12 outcome is recorded.
- **D6, thesis wording of SQ3** (report/ is the author's). Recommend the narrowed F-TAX sentence in (a)-SQ3, with G10's "up to intra-node order" and the R1 failure disclosed in one sentence.

Research-lead decisions, not the author's: the closures (b), the queue order, the CARD-PROTOCOL text, and the briefs.
