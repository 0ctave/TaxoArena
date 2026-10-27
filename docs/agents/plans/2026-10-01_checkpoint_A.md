# Research checkpoint A (research-lead), 2026-10-01: what INTENT-TRANSFER-S0 means, RP12 pre-data notes, stage 1 priorities, new tests, the next 24 h

Inputs: experiment_results/intent_transfer/s0_outcome.txt (6d04e84; script blob f662ceb1); registration
prog L22092-L22134 _as_of 44ab46f; ARCH-V2-E-T registration prog "## Registered 2026-09-29 (before any code or
call) — ARCH-V2-E-T: ..." (G10-G15, FLAT, Support, P1-P7); framing SQ3/SQ5 (framing L83, L128); design
docs/agents/plans/2026-09-29_intent_transfer_design.md sections 3, 6, 9.
PROVISIONAL: the S0 post-run review runs in parallel. Every S0 number below is the builder's, copied from the
outcome file, and none goes to the ledger before the reviewer checks it. If the review refutes C2 or C4,
sections (a), (c) and (d) are re-read and B-A1 is not applied. Zero calls; nothing run or built by this
checkpoint.

## Readings beyond the verdict lines (the outcome's "beside" and descriptive rows)

- **C4's bar sat almost at the instrument's ceiling.**
  - k-means cells (K 60) score S 0.760 [0.746, 0.774].
  - Beside it, under the same swaps: a supervised TRAIN-centroid keeps its label 0.834 of the time, kNN-1 0.829,
    and two random same-intent utterances co-file 0.692.
  - The 0.80 bar was 3.4pp under what a gold-trained classifier reaches.
  - Ceiling-normalised, (S - 0.692) / (0.834 - 0.692) = 0.48. A slot swap moves a label-free address about half
    as far as replacing the utterance with another of the same intent.
  - P5 (0.90 [0.85, 0.95], p 0.85, Brier 0.72) is the run's worst prediction. Lesson: an absolute bar needs a
    ceiling arm at registration.
- **The CLINC coarse level is not convex.**
  - Coarse centroid accuracy is 0.86, against 0.98 for kNN-15 (qwen3).
  - The k-means seed spread at K 10 is 0.13, which is why C1b reads NEITHER on CLINC.
  - H is 0.14 (qwen3), against 0.27 (nomic) and 0.29 (gemma).
  - The 10 CLINC domains are unions of tight intent clusters, not regions of the space.
- **qwen3, the embedder of record, has the lowest gold-hierarchy geometry on both corpora.**
  - H on MASSIVE: 0.40 qwen3, 0.47 nomic, 0.88 gemma.
  - At fine level, gemma is BETTER on 2 of 3 corpora (+0.033 and +0.056 NMI). P2 failed in that direction on
    MASSIVE and Banking77.
  - RAW protocol only. qwen3 is instruction-aware, and no card prompts were used.
- **Short texts.** MASSIVE's shortest quintile (4 tokens or fewer) has centroid accuracy 0.72, against about 0.87
  for the others.
- **Near-copies.** EVAL items with a TRAIN neighbour at cos >= 0.98 were disclosed, not removed: 1,110 of 8,022
  (CLINC), 569 of 3,908 (Banking77), 274 of 4,946 (MASSIVE).

## (a) Meaning for SQ3 and SQ5

**SQ3 (TAXONOMY).** S0 builds no tree, so no SQ3 "already answered" row moves. Three readings change.

- **Filing.** Every filing rate of record now carries F4's qualifier, "surface-sensitive, untested on capability
  text". That covers flatLeaf 81.58% (id-disjoint only) and G11's P_fl when it lands. The qualifier binds
  supervised addresses too: the supervised centroid is only 0.834 stable.
- **Label-free cells.** Against a known answer they gain a self-diagnostic and scope detection:
  - C3: a TRAIN margin ranks cells by gold purity (rho 0.27-0.41, positive on 2 of 3).
  - C2: AUROC 0.974 on curated CLINC OOS, equal to the supervised centroid's 0.976.
  - Both are flat-cell results. Tree cells are stage 1's T-C6 and T-C7.
- **Hierarchy.** A declared coarse level can be weakly geometric (CLINC H 0.14). Two consequences follow:
  - A label-free coarse level cannot be expected to recover declared domains.
  - Descent through coarse centroids should lose to leaf filing exactly where coarse classes are non-convex.
    That is a mechanism for MC-ROOT's +9.5pp (flatLeaf over descent) which the record has not measured. T-C8 and
    MMLU-GOLD-GEOMETRY below test it.

**SQ5 (INVARIANCE).** "Fine structure depends on the embedder" now holds against gold on 3 of 3 intent corpora as
well as on MMLU-Pro (two kinds of corpus, one draw each, RAW protocol).

- "Coarse holds" is a non-fire, never parity (no TOST). On CLINC the coarse bar is a seed spread of 0.13, a
  resolution at which nothing could be shown.
- New is the direction. The second embedders are not uniformly worse:
  - nomic is worse everywhere;
  - gemma is better at fine on 2 of 3 corpora, and much better on MASSIVE's coarse level and gold geometry.
- SQ5's answer becomes "the fine partition belongs to the embedder", not "qwen3 is a safe default".
- Open: whether gemma's edge is a protocol artefact (qwen3 run RAW, without its instruction). INTENT-S0-CARD-PROTOCOL
  is drafted for that.
- Changing the embedder of record is the author's (KNOWLEDGE section 2). Nothing here proposes it.

## (b) RP12 readouts: pre-data changes only (no criterion, bar or prediction moves)

No RP12 readout is demoted. The checkpoint-A demotion trigger ("the construction does not recover gold coarse
structure against flat") is unreadable from S0, which has no build. The registrar inserts three pre-data brackets
into ARCH-V2-E-T, all before any RP12 EVAL readout:

- **B-A1 (G11 wording).** Every P_fl / D_fd sentence carries "surface-sensitive, untested on capability text"
  (INTENT-TRANSFER-S0 F4). The verdict logic is unchanged. Apply only if the review confirms C4.
- **B-A2 (G12 reading).** G12 is read beside MMLU-GOLD-GEOMETRY's H, which must be registered and run before G12
  is read. If N-1 fires while H <= its permutation p95, the text says "the declared depth-1 boundary is not shown
  to be geometric", not "the construction fails to certify". The N-1 verdict is unchanged.
- **B-A3 (G13 / FLAT prior note; nothing is revised).**
  - S0 measured k-means NMI seed spreads of 0.009-0.025 at fine K and 0.05-0.14 at coarse K. Both exceed P4's
    spread_KC prior of 0.004 [0.001, 0.012].
  - P4 is scored as registered.
  - The note records now that a G13 UNDETERMINED is the likelier reading. It means "neither a gain nor parity is
    shown" (Support (g)).

G10, G14, G15 and FLAT are untouched. No descriptive readout is added to RP12: margin and slot-swap on tree leaves
are stage 1's T-C7.

## (c) Stage 1 priorities (tree specialist drafts; registered after RP12, the author's D5)

1. **Relative criteria with a ceiling arm, everywhere.** T-C7 scores S_tree against S_kmeans at matched k, paired
   on the same variants, and prints the supervised 0.834 and the floor 0.692. No absolute 0.80 bar.
2. **Score T-C2 (hierarchy beyond the leaves) on MASSIVE.**
   - On CLINC it is reported against the gold-centroid ceiling (H 0.14) and is DESCRIPTIVE-ONLY, unless the
     registration shows the 0.02 gap is reachable inside the coarse seed spread.
   - CLINC still carries T-C1 (fine), T-C6 (OOS) and T-C8.
3. **A sharp T-C8 prediction:** D_fd(CLINC) > D_fd(MASSIVE). Mechanism: the coarse centroid-vs-kNN gap is 0.86 vs
   0.98 on CLINC and 0.87 vs 0.91 on MASSIVE.
4. **T-C3 adds a token-length covariate** (MASSIVE's shortest quintile is at 0.72).
5. **Hygiene (data-steward at READY).**
   - The split is closed under split_side.stem_key (CK-CLOSE-v1 binds new constructions).
   - The cos >= 0.98 near-copies are read with and without them, as a registered sensitivity line, not a removal.
6. **The embedder arm waits** for the E1 working-copy route and CARD-PROTOCOL. The primary stays qwen3.

## (d) New cheap tests

| id | claim the record has not tested | cost | Support | priority |
|---|---|---|---|---|
| INTENT-S0-SLOTSWAP-MECH | C4's instability is a cell-boundary effect (margin) and/or a surface-share effect (slot tokens dominate short texts) | 0 calls; CPU ~15 min on S0's pinned DBs; no Ollama | M1, M2 SCOREABLE; M3 DESCRIPTIVE-ONLY | 1 |
| MMLU-GOLD-GEOMETRY | MMLU-Pro's declared category level is geometric over its sources in qwen3 (like MASSIVE 0.40, unlike CLINC 0.14) | 0 calls; CPU minutes; TRAIN side only; rule-7 reader | SCOREABLE against a permutation null; the cross-corpus comparison is descriptive | 1 (before G12 is read) |
| INTENT-S0-CARD-PROTOCOL | gemma > qwen3 at fine survives card-conformant prompts | 0 calls; Ollama re-embed of 57,350 texts x 3 (one heavy process; time unpriced) | as S0 C1 (SE 0.0014-0.0048 measured) | 3, drafted only |
| CAPABILITY-SURFACE-FILING | a filed cell is a stable address under answer-preserving numeric swaps on MMLU-Pro EVAL text (discharges F4's "untested") | 0 judge calls; qwen3 embedding of a few thousand variants; needs RP12 B0 | to be computed at drafting | 2, drafted after B0 |

**Closed-lines check (CONTEXT section 5).** None of the four touches rubrics, references, the frontier, escalation
or the GMM LR. CARD-PROTOCOL attacks EMBED's named confound (RAW, no prefix), so it is not a closed-line re-run.

### Registration text 1 (for the registrar): INTENT-S0-SLOTSWAP-MECH

**Question.** On MASSIVE's 3,222 slot-swap variants (S0-C4):
- is a label-free cell flip predicted by the origin's distance to its cell boundary (M1)?
- is it predicted by the share of tokens swapped (M2)?
- does the embedder move S (M3, descriptive)?

**Instrument.** S0's C4 machinery verbatim (qwen3 256, K 60, seed 0, TRAIN-fit k-means).
- Origin margin = cos(nearest centroid) - cos(second-nearest), for the EVAL origin against the TRAIN-fit centroids.
- Swap share = swapped slot tokens / tokens.
- Seen before registration: S, the per-seed S, the "beside" lines and the slot-type counts in the outcome file.
  No per-variant flip has been read against margin or share.

**Hygiene.**
- Reads only S0's pinned DBs (ingest 487e0093, qwen3 9e100e04, nomic 4aafd6c7, gemma b187b82f), re-hashed before
  and after.
- No pool of record, no new embedding, TRAIN-only fits (fit_rows refuses otherwise).
- Precondition (data-steward): every variant is present in all three embedding DBs.

**Criteria.** Intervals: component (CK-CLOSE) cluster bootstrap, B 2000.
- M1: D_Q = flip rate (lowest origin-margin quintile) - flip rate (highest). HELD iff lower(95% CI) >= 0.10;
  FAILED iff upper < 0.10; else UNDETERMINED.
- M2: D_T = flip rate (top swap-share tercile) - flip rate (bottom). HELD iff lower > 0; FAILED iff upper <= 0;
  else UNDETERMINED.
- M3 (DESCRIPTIVE-ONLY): S_gemma - S_qwen3 and S_nomic - S_qwen3, paired, against the seed spread 0.0335.

**Printed, descriptive:**
- the M1 x M2 joint logistic;
- ceiling-normalised S per embedder;
- S at K 18 / 60 / 120;
- S over the top 80% of origin margins ("selective stability", the link to D4's +7.7pp);
- slot types with >= 80 variants.

**Predictions.**
- D_Q 0.30 [0.20, 0.40]; HELD p 0.80.
- D_T +0.12 [+0.04, +0.20]; HELD p 0.65.
- S_gemma - S_qwen3 +0.04 [0.00, +0.08].
- S_nomic - S_qwen3 -0.04 [-0.08, 0.00].

**Falsifiers.**
- F-SM1 fires iff M1 FAILED. It overturns the reading that margin-gated (selective) filing remedies F4 (design
  section 3(d); D4). F4's qualifier would then read "surface-dominated": addresses move across cell interiors.
- F-SM2 fires iff M2 FAILED. It overturns the slot-dominance explanation of D6's short-text deficit.

**Support.**
- Denominator: 3,222 variants in 3,207 components (measured); Kish DEFF 1.0093 (measured, S0); n_eff 3,192.
- M1: quintiles of ~640. SE = sqrt(0.24/640 + 0.09/640) x sqrt(1.0093) = 0.0228; MDE80 0.064. The prediction
  sits 0.20 from the bar, which exceeds the MDE: SCOREABLE.
- M2: terciles of ~1,070. SE = sqrt(2 x 0.21 / 1,070) = 0.0198; MDE80 0.055: SCOREABLE.
- M3: paired SE at a declared discordance of 0.25 is 0.0089. The effective bar is max(MDE 0.025, seed spread
  0.0335). The prediction sits 0.0065 from it, under the MDE: DESCRIPTIVE-ONLY.
- Structural leg: M1 and M2 are reachable at infinite budget. M3 can never pass a true gap inside the seed spread.

**Cost.** 0 calls, 0 cce. CPU ~15 min, single-threaded. engine-coder ~2 h plus one review.

### Registration text 2 (for the registrar): MMLU-GOLD-GEOMETRY

**Question.** Over MMLU-Pro's fine sources, does the declared 14-category level form geometric clusters in qwen3
(H above the permutation p95)? Where does it sit beside CLINC 0.143 and MASSIVE 0.404 (descriptive)?

**Instrument.**
- S0's D2 function verbatim: average-link on gold fine centroids, cut at K_c 14, scored against the gold coarse
  map with 1,000 random relabellings.
- Fine label = a (src, category) pair with >= 10 TRAIN items.
- qwen3 of record decides on S0's D2 slice; 512 is printed.

**Hygiene.**
- Reads only the TRAIN side of draw 5a3e756 (the MMLU_PRO_LB member, 6,994 items). It never reads EVAL or GATE,
  so RP12's single EVAL read is untouched.
- It reads embeddings_cache.db, so it is a rule-7 reader: never beside a construction or site null.
- No non-qwen3 embedder (rev2 section B8).

**Precondition (data-steward).** The src field is present for the member, and the fine-label census per category
is printed. If there are fewer than 2 fine labels per category on average, the test is declined.

**Criterion.** HELD iff H > random p95; FAILED iff H <= p95. An item-bootstrap CI (within fine labels, B 1000)
is printed.

**Prediction.** H 0.30 [0.12, 0.50]; HELD p 0.85.

**Falsifier.** A FAILED reading means the declared categories are not a geometric level in the embedder of record.
G12 is then read under B-A2, and D_fd > 0 is expected.

**Support.**
- Unit: the fine label. K_f is counted by the steward (expected ~60-80).
- H is a deterministic statistic against a permutation null: SCOREABLE; the structural leg is reachable.
- The cross-corpus contrast has different K and no interval: DESCRIPTIVE-ONLY.

**Cost.** 0 calls; CPU minutes.

## Plan of delegation (briefs; each "report in the KNOWLEDGE section 0 format")

1. **adversarial-reviewer** (running): S0 post-run review. Its verdicts gate B-A1 and every S0 number here.
2. **registrar** (after the review).
   - Task: S0 outcome, ledger row and results JSON. Then B-A1 (only if C4 is confirmed), B-A2 and B-A3 into
     ARCH-V2-E-T before any RP12 EVAL readout. Register INTENT-S0-SLOTSWAP-MECH and MMLU-GOLD-GEOMETRY from the
     texts above. Queue CARD-PROTOCOL and CAPABILITY-SURFACE-FILING as drafted.
   - Verified already: the S0 pins in the outcome file; RP12 is pre-data.
   - Acceptance: the rule-9 re-grep of every span written, plus the closed-lines check.
   - Output: programme and ledger, via ledger_patch.
3. **data-steward.**
   - Task: two preconditions, read-only, zero builds, outside any construction window: MMLU-GOLD-GEOMETRY's
     (src present; fine census on 5a3e756 TRAIN) and SLOTSWAP-MECH's (all 3,222 variants in the three S0 DBs).
   - Output: hand-back only.
4. **engine-coder** (worktree slotswap-geom, from main).
   - Task: two scripts, tools/analysis/intent_s0_slotswap_mech.py and tools/analysis/mmlu_gold_geometry.py, each
     importing S0's functions unchanged (blob f662ceb1); --dry-run first.
   - Acceptance: selftests and mutants; the dry-run prints the census, the pins and the Support.
   - Hands to the reviewer.
5. **adversarial-reviewer**: READY on both at zero calls, with an execution discriminator for the imported functions.
6. **run-operator**: MMLU-GOLD-GEOMETRY in a no-construction gap before G12 or G11 is read; SLOTSWAP-MECH in any CPU
   gap. Outcome files are write-once.
7. **adversarial-reviewer** checks the numbers; then **registrar** writes the outcomes.
8. **tree-construction-specialist** (checkpoint B): drafts stage 1 with priorities (c)1-6, and reads B0's structure
   against the CLINC non-convexity.

## (e) Re-ranked queue, next 24 h (zero judge calls throughout)

| # | machine lane (serial; rule 7) | agent lane (parallel) |
|---|---|---|
| 1 | RP12 B0, then the C-2 proof (unchanged; top) | S0 post-run review (running) |
| 2 | B0', o1, o2 (one pinned worktree, D-8) | registrar: S0 outcome + B-A1..B-A3 + 2 registrations; steward preconditions |
| 3 | gap: MMLU-GOLD-GEOMETRY (minutes; before any G12/G11 read) | engine-coder: the 2 scripts, then READY |
| 4 | G12 site null (its config review owed first) | checkpoint B (tree specialist; stage 1 draft) |
| 5 | RP12 readouts G10, G11, G13, G14, G15, FLAT | none |
| 6 | INTENT-S0-SLOTSWAP-MECH (CPU ~15 min) | RP12 post-run review, then the outcome |
| 7 | backfill: LCB-STAGE0-POWER-RESIM (READY); EVAL-METRIC-DETERMINISM and E1 once READY | checkpoint C (experiment-manager + research-lead) |
| 8 | INTENT-S0-CARD-PROTOCOL (Ollama; after RP12 frees the lane; once registered) | stage 1 registration; CAPABILITY-SURFACE-FILING draft on B0 |

Unchanged after RP12: RP09 E1, then RP13. The paid runs (RP21, RP20; RP19 needs the go) are priced at
checkpoint C.

## Synthesis of INTENT-TRANSFER-S0 (provisional until the post-run review)

**The framework may say:**
- On three intent corpora with a known answer (one draw, RAW protocol), the fine flat partition depends on the
  embedder against gold labels.
- A label-free no-match threshold detects curated CLINC out-of-scope queries at AUROC 0.974 [0.970, 0.978], as
  well as a supervised centroid does.
- A label-free TRAIN margin ranks flat cells by gold purity (rho 0.27-0.41; positive on 2 of 3).
- A label-free cell is a surface-sensitive address: S 0.760 under slot swaps, against 0.834 for a supervised
  centroid and 0.692 for a random same-intent utterance.

**It refuses:**
- embedder invariance or parity (no TOST);
- that qwen3 is the best, or a safe, embedder;
- any tree, construction, routing or capability claim;
- OOS detection on real traffic;
- that the 0.80 failure is specific to label-free cells.

**It opens:** SLOTSWAP-MECH, MMLU-GOLD-GEOMETRY, CARD-PROTOCOL, CAPABILITY-SURFACE-FILING.

**What this result does NOT show**
- Anything about the construction or a tree (no build; T-C1..T-C8 are stage 1's).
- That a tree leaf is more or less stable than a k-means cell (C4 measured k-means cells only).
- Surface sensitivity on capability text (F4's own words: "untested").
- That gemma beats qwen3 in general. The result is RAW protocol, one draw, fine level, and qwen3's instruction was
  not used.
- Coarse-level embedder parity. C1b's non-fire is never parity, and CLINC's coarse bar was a seed spread of 0.13.
- That the CLINC gold hierarchy is "wrong". H 0.14 says only that its coarse level is not geometric under these
  embedders.
- That margin-gated filing fixes surface sensitivity. D4's +7.7pp is accuracy at 80% coverage, not stability.
- Natural multi-intent text (D5 is synthetic concatenation).
- Robustness to near-copies (1,110 / 569 / 274 EVAL items kept with a TRAIN neighbour at cos >= 0.98).
- A second split draw, or k-means seeds beyond the 5 printed.

## Decisions that are the author's

- The thesis wording of F4's qualifier and of the known-answer study (D2; report/ is the author's).
- Any change of the embedder of record (gemma / nomic / mxbai). CARD-PROTOCOL informs this decision; it does not
  make it.
- D3 (BlendX) stays open.
- Stage 3 real traffic (D4: WildChat, local only) is not engaged until the review confirms C2.

Research-lead decisions, not the author's: B-A1..B-A3 as pre-data notes, the two registration texts, the stage 1
priorities and the queue order.
