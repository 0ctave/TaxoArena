# Checkpoint C: reframing memo for the author (research-lead), 2026-10-02

Zero calls. Nothing built, run, registered or recorded. As of HEAD d635fec5, ledger v343. Post-incident evidence
only (memory: thesis-evidence-base-post-incident). [P-FAM] numbers appear only with their bracket. Every number
carries its record ID, from `docs/agents/results/<ID>.json` `numbers_of_record` / `sentence_of_record`. The registered
title ("Query-Adaptive Multidimensional Ranking for Agents in Dynamic Domains") and `report/` are untouched; what
follows is a proposal, and the framing is the author's (KNOWLEDGE §2).

## 1. Revised framing (one paragraph; the author's to adopt, amend or reject)

Per-cell evaluation pays where the cells are **declared**: on the content-closed v2 union split a TRAIN-fitted
per-cell policy beats the best single model by +2.67pp on declared cells. The same policy on the anchored tree's
cells gives +2.62pp, and the difference is not shown in either direction. Because the tree's depth-2 frontier *is*
the 52 declared classes, this is the expected result, not parity of discovered structure. **Judge trust is the
reference's trust.** Under the v2 recipe the judge picks the key-correct side 0.92 of the time when the reference is
right and 0.26 when it is wrong. A false "carries a reference" sentence costs nothing measurable (RP20 EQUIVALENT
within +-4pp). Removing a mostly-correct reference loses about 16pp, mostly by turning decisions into ties rather
than into wrong winners. **The tree is an audited filing and addressing layer, not a better partition.** It is
reproducible and order-stable, and files 9.4pp better from its flat leaves than by descent. It certifies none of its
60 sites. Below its anchors it files worse than class-conditioned k-means. Label-free *flat* cells abstain on curated
out-of-scope queries at AUROC 0.974, and their TRAIN margin tracks purity; whether either carries over to tree cells
is untested. **Invariance (SQ5):** the fine partition belongs to embedder x prompt x corpus. A coarse-level
invariance sentence is NOT yet available (§2 SQ5; conflict C3).

## 2. SQ1-SQ5 restated

| SQ | restated claim | supports (ID: number) | negative / bounding | pending tests that could move it |
|---|---|---|---|---|
| SQ1 USE | On the roster measured, per-cell routing on declared (or declared-anchored) cells beats the best single model on content-closed union EVAL; the gain is concentrated, and the frontier roster gives zero. | V2-DECLARED-CELLS C1 +2.67pp [+1.46, +3.89] (5,907 items / 5,404 components); ARCH-V2-E-T-R2 G14 G_tree +2.62pp [+1.43, +3.82], DEFF 1.392 | M -0.05pp [-0.69, +0.59] DESCRIPTIVE-ONLY (never parity); BBH carries 0.728 of G, leave-BBH-out +1.03 [-0.27, +2.32], MMLU-Pro +0.18 [-1.18, +1.54] (V2-DECLARED-CELLS); LCB power 0.22 (LCB-STAGE0-POWER-RESIM) | **UNION-AF-ROUTE (RP13)**: U1 (do anchor-free cells beat best single?), U3b TOST +-1pp vs declared, AK1/AK2 vs unsupervised k-means; the only like-for-like label-free test |
| SQ2 TRUST | Fidelity is conditional on the reference's correctness; without a reference the judge mostly declines (TIE) rather than errs. | K46-KEY-READ C1 0.8787 [0.8332, 0.9241] on 544 ONE matches (160 components); reference right 0.9249 / 506, wrong 0.2632 / 38; NONE 0.7512 / 1,258 conv A vs 0.9292 / 1,017 conv B; V2-NONE-TEMPLATE C1 Delta_A +0.0143, 90% [+0.0006, +0.0280], EQUIVALENT; C_ONE Delta1_A -0.1599 [-0.2095, -0.1103], 82 of 97 lost matches to TIE, conv B -2.9pp on 411 | the wrong-reference cell is 38 matches in 2 of 14 anchors (descriptive); C_ONE is a bundle (block + sentence); confidence gating CLOSED (REF-CONF, ABSTAIN); v2 retest floor d_r 0.100 [0.0658, 0.1342] (G17-CANARY C1-v2, DESCRIPTIVE-ONLY) | **JUDGE-SOLVED-SPLIT** (JS1 DESCRIPTIVE-ONLY at prediction; JS2 5 vs 27 matches); **RP19 G21-RESCOPED** (the author's go, waits on D2): the only content-closed v2 judged-fidelity number at scale |
| SQ3 TAXONOMY | A TRAIN-only anchored tree buys reproducible, order-stable cells that file well from flat leaves; it does not certify, and below the anchors it does not beat label-conditioned prototypes. | ARCH-V2-E-T-R2: G11 P_fl 0.8119 [0.8013, 0.8223] (6,139 / 5,628); D_fd +0.0937 [+0.0828, +0.1054]; G10 7 of 7 pairs byte-identical on the declared set (as sets); G15 max drift 0.0151pp; FLAT D1 +0.0246 [+0.0125, +0.0369] (thin, M1 only, one member); MMLU-GOLD-GEOMETRY H 0.2912 vs p95 0.0264 | G13 D13 -0.0215 [-0.0301, -0.0125]; G13-BREAKDOWN C-a4 below anchors -0.0192 [-0.0292, -0.0089] (point seen pre-registration), MMLU-Pro D13 -0.0446; G12 0 of 60 hierarchical-BH (0 of 14 depth-1); CERT-RESOLUTION 2 of 70 (R512, bareq512_s42, another tree); FLAT C2 FAILED; P_fl MMLU-Pro alone 0.745; the +0.0738 lead over unsupervised k-means is the anchors' (G13-BREAKDOWN bracket) | **DEEP-SPLIT-COMPARE** (split rule vs label information below depth 2; C-DB SCOREABLE thin, C-AB/C-AC DESCRIPTIVE-ONLY at prediction); **CERT-POSITIVE-CONTROL** (can the certificate certify the geometric declared level? P1 NOT CERTIFIED 0.85); UNION-AF-ROUTE AK1/AK2 |
| SQ3 (abstention leg) | Label-free cells carry a scope signal and a self-diagnostic, shown on flat cells of intent corpora. | INTENT-TRANSFER-S0 C2 AUROC 0.97437 [0.97043, 0.97813] (CLINC, k-means cells; supervised centroid 0.97640); C3 rho 0.27 / 0.41 / 0.39 (MASSIVE interval crosses 0); INTENT-S0-SLOTSWAP-MECH M1 D_Q 0.4689 [0.4253, 0.5123] | all flat k-means, not tree cells; curated OOS, not traffic; S 0.760 under slot swaps | **OOS-BASELINES** (OB-d decides cells vs embedder geometry; F-OB); stage 1 T-C6/T-C7 (INTENT-TRANSFER-S1) for tree cells |
| SQ4 PRICE | Priced, and UNDETERMINED. | v2 retest floor 0.100 (G17-CANARY) | no time instrument has a second pass on v2 | RP21 / G17-CANARY pass 5, not before 2026-10-08 |
| SQ5 INVARIANCE | The fine partition belongs to embedder x prompt x corpus; label-free addresses are surface-sensitive, with a margin mechanism. | S0 C1a gemma +0.0334 / -0.0069 / +0.0563 (MASSIVE / CLINC / Banking77), nomic worse on all three; EMBED-DIM-SLICE edge survives the slice (REOPEN-CANDIDATE); CARD-PROTOCOL CP1 under card prompts -0.0324 MASSIVE, -0.0339 CLINC, +0.1183 Banking77 (sign reverses on two); SLOTSWAP M1, M2 D_T 0.1411 [0.1067, 0.1752] | no TOST anywhere; C1b NOT FIRED is never parity; a coarse gemma lead is seen (S0 +0.135 MASSIVE at 256) | **GOLD-LEVEL-EMB** (coarse TOST, 4 families; its own predictions are NOT-INVARIANT on PROMPT and EMBEDDER, INVARIANT on QUANT); SLOTSWAP-DECISION (decisions vs addresses; data leg paid, unpriced) |

## 3. Framework changes, ranked (value x evidence / cost)

| # | change | value | cost | evidence state | record basis / caveat |
|---|---|---|---|---|---|
| 1 | **File by flat leaf, not descent** (descent stays a diagnostic) | high: +9.4pp filing for free | low: flatLeaf routing exists; FRAMEWORK text + default | SUPPORTED | ARCH-V2-E-T-R2 D_fd; MC-ROOT +9.50pp (id-disjoint only); union mix, MMLU-Pro 0.745; "surface-sensitive, untested on capability text" |
| 2 | **Name the reference policy per claim; state fidelity conditional on reference correctness; invest in reference correctness (key / checker / better solve), not in gating** (replaces "gate the judge on reference quality"; conflict C1) | high: this is the SQ2 sentence | zero (wording, readout columns) | SUPPORTED | K46-KEY-READ; V2-NONE-TEMPLATE; REF-CONF "only a more accurate reference helps"; REF-QUALITY-MONITOR licenses no per-cell judge monitor |
| 3 | **Report ties and decisiveness as first-class columns** (conv A and B, TIE share, right/wrong reversals) | high: every recent judge effect is TIE vs decisive | zero (the conventions exist) | SUPPORTED | RP20 zero right/wrong reversals; C_ONE 82 of 97 to TIE, conv B -2.9pp vs conv A -16.0pp |
| 4 | **Claims at declared / coarse level only**; sub-anchor rows refused | high (keeps claims inside support) | zero (codifies scope S1 + closed lines) | SUPPORTED | PROFILE-TREE-ROBUST, KEY-SUBANCHOR-SCALE (closed); G12 0 of 60; G13 |
| 5 | **A power check in every registration** (Support section + structural reachability), written into FRAMEWORK.md as a stage | medium-high (stops DESCRIPTIVE-ONLY spend) | zero | SUPPORTED (process) | standing practice since BFCL-JUDGED-PILOT (1,316 calls inside its own worst-case support) and LEAF-INTERACTION; FRAMEWORK.md does not yet carry it as a stage |
| 6 | **Abstention as a first-class output** of the filing layer (no-match, low-margin flag), beside the judge's TIE and the key-tie decline | medium | low (readout); stage 1 for tree cells | PENDING | S0 C2/C3 and SLOTSWAP M1 on flat cells; OOS-BASELINES and T-C6/T-C7 decide. **Escalation to a reasoning judge is CLOSED** (ESCALATE-LLAMA-LAW); confidence-gated judge abstention is CLOSED (ABSTAIN); escalation to a key / checker is untested (speculative) |
| 7 | **Certificate as a false-discovery guard**: "no discovered-structure claim without it", never evidence of absence  [CORRECTED 2026-10-03 by CERT-POSITIVE-CONTROL (registrar; W-2 of POSTRUN_cert_positive_control): PC1 CERTIFIED the declared 14-category partition at the member root (k_d 0 of 300): the certificate is shown CAPABLE of certifying at one root-size site (n about 7,000); its sensitivity at depth-1 sizes is untested; the "conservative with unmeasured power" branch does not apply at root scale; F-TAX N-1 and F2 stand; docs/judge_v2_program.md L23638-L23649 (section "## CERT-POSITIVE-CONTROL (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 218f9b7f)] | medium | zero (wording) once CERT-POSITIVE-CONTROL reads | PENDING | G12, CERT-RESOLUTION. If PC1 is NOT CERTIFIED on the H 0.29 structure, the guard is conservative with unmeasured power; its false-certification rate is not measured (speculative) |
| 8 | **Replace deep splits by the deep-split winner** | uncertain | an engine change (SPLIT-VMF) only if a rule wins | SPECULATIVE until DEEP-SPLIT-COMPARE | if F-RULE fires with C-DB HELD, the gap is label information and no engine change follows; the "winner" may need fine labels, which a TRAIN-only label-free tree does not have |

## 4. Proposed wording (THE AUTHOR'S DECISION; drafts only)

**D2 (SQ2 instrument and v2 reference policy).** "SQ2's content-closed claims are stated under the v2 recipe:
judge grok-4-1-fast-non-reasoning, dual order, TIE on flip; reference = the cached grok-4-1-fast-reasoning solve
where one exists (class ONE), none otherwise (class NONE). The content-closed v2 split is pv2_41dbd3dbcd399df0.
Every fidelity figure is reported by reference class, in conventions A and B, and, where a key exists, conditional
on the reference's correctness. The K46 store was posted with a false 'carries a reference' sentence on NONE
matches; that sentence leaves key accuracy equivalent within +-4pp (RP20). STACK-v2 numbers stay id-disjoint only
or [P-FAM] history." Consequence: RP19 runs under this policy (with N1 on NONE, the research-lead's recommendation).

**D6 (SQ3 wording).** "On a content-closed split, a TRAIN-only tree anchored on declared classes gives cells that are
reproducible (byte-identical on the declared set, as sets, for 7 build pairs) and order-stable. They file union EVAL
at 0.812 from flat leaves (+9.4pp over descent; MMLU-Pro alone 0.745). They route the union roster as declared
labels do (+2.62 vs +2.67pp; the difference is not shown). The tree certifies none of its 60 sites at per-family
q 0.05. Below its anchors it files 2.15pp worse than class-conditioned k-means, and its lead over unsupervised
k-means belongs to the anchors." Forbidden words: "label-free" (for this tree), "deterministic", "converged",
"purer than flat clustering", "parity". G10's R1 list-order failure is disclosed in one sentence. Revisit after
UNION-AF-ROUTE, DEEP-SPLIT-COMPARE and CERT-POSITIVE-CONTROL.

## 5. Literature positioning (docs/literature/2026-10-02_related_work_pass2.md §4)

- **Declared-label baseline as the stricter comparator (SQ1).** Published discovered-task routers report gains
  against the best single model. We add a TRAIN-fitted declared-label policy on content-closed EVAL, and against it
  the anchored tree adds nothing shown. The sentence must say "anchored", not "label-free" (conflict C4).
- **Krumdick et al. 2025 (SQ2).** A deliberately wrong reference gives kappa 0.21, below no reference (0.46). This is
  the external twin of K46's 0.2632 (38 matches), and it agrees in direction with C_ONE's reference-wrong stratum
  (+0.0789 when the reference is removed, descriptive). The Lee-vs-Krumdick reconciliation ("does the judge solve it
  itself?") is exactly JUDGE-SOLVED-SPLIT. Its wrong-reference leg (JS2) is 5 vs 27 matches, so it can only be
  descriptive.
- **Avengers (Zhang et al. 2025) (SQ1/SQ3).** k-means routing is insensitive to algorithm, K and embedder. This is
  consistent with +2.62 vs +2.67, but our tree is anchored, so the like-for-like test is UNION-AF-ROUTE U3b/AK1. An
  Avengers-style K-sweep k-means routing baseline (pass 2 §5 item 8) is a zero-call addition.
- **Kostiuk & Enevoldsen 2026 (SQ5).** Prompt choice can reorder embedder leaderboards. This is the frame for
  CARD-PROTOCOL's sign reversal on MASSIVE and CLINC. SQ5's claim becomes a distribution over prompts, not a ranking.
- Pass 2 itself flags that its HTML-derived numbers (Krumdick, Avengers) need checking against the papers' tables
  before quoting.

## Record conflicts found (for the orchestrator / registrar; nothing edited)

- **C1 (closed line).** "Gate the judge on reference quality", as worded, is a variant of the CLOSED reference-gating
  / confidence line (REF-CONF, ABSTAIN, J2-D; CONTEXT §5). REF-QUALITY-MONITOR licenses no per-cell judge-quality
  monitor. Re-worded as change 2.
- **C2 (object).** OOS AUROC 0.974 and "margin predicts purity" are INTENT-TRANSFER-S0 results on flat label-free
  k-means cells (CLINC; 2 of 3 corpora). They are not tree results, and the brief's framing attributed them to the
  tree. Tree cells are stage 1's T-C6/T-C7.
- **C3 (SQ5).** "Coarse structure robust" is not in the record. S0 C1b is a non-fire, never parity. A coarse gemma
  lead is seen (S0 +0.135 MASSIVE). GOLD-LEVEL-EMB's own registered predictions expect NOT-INVARIANT on the prompt and
  embedder families. At most "coarse robust to slice and quantisation" is pending. [CORRECTED 2026-10-03 by GOLD-LEVEL-EMB (registrar; POSTRUN dad630f2): resolved: coarse QUANT INVARIANT (within 0.025 NMI), DIM UNDETERMINED (seen-carried, never "slice-invariant"), PROMPT and EMBEDDER NOT-INVARIANT; F-GL FIRED; "coarse structure robust" stays unavailable; docs/judge_v2_program.md L23622-L23636 (section "## GOLD-LEVEL-EMB (2026-10-02, 0 calls) — VALID ..."; _as_of the commit that writes it, parent aac3f7fc)]
- **C4 (anchoring).** Literature pass 2 §4 SQ1 calls the v2 tree's cells "label-free" ("+2.62 vs +2.67pp"). They are
  anchored (G13-BREAKDOWN bracket; memory anchored-tree-comparisons). Needs a bracket before any prose reuses it.
- **C5 (abstention).** "Escalation" as a framework output collides with ESCALATE-LLAMA-LAW (closed) if it means a
  reasoning judge on the residue.

## What this memo does NOT show

- That tree cells equal declared cells: M is DESCRIPTIVE-ONLY with no TOST, and the tree is anchored.
- Any per-corpus routing gain: BBH carries 0.728 of G, and MMLU-Pro's interval contains 0.
- That the judge is accurate in general: 0.9249 / 0.2632 are on the key-decidable ONE subset in 2 of 14 anchors, and
  the wrong cell has n 38.
- That removing the reference costs 16pp of *wrong* verdicts: most of the loss is ties (conv B -2.9pp).
- That a tree, rather than flat cells, abstains well, or that 0.974 belongs to the cells rather than to the embedder
  (OOS-BASELINES OB-d).
- That the certificate is powerless: CERT-POSITIVE-CONTROL has not run.
- That any label-free split rule would close G13's gap: DEEP-SPLIT-COMPARE has not run.
- Coarse-level invariance, or that gemma is the better embedder: the evidence is mixed (EMBED-DIM-SLICE vs
  CARD-PROTOCOL), and D3 stands.
- Anything about SQ4 beyond one retest floor.

## Decisions that are the author's

- Adopting, amending or rejecting the §1 framing (framing of record, Amendment 25).
- D2 (the §4 wording; SQ2's instrument; the v2 reference policy), which gates RP19.
- D6 (the SQ3 thesis wording; `report/` is the author's).
- Whether change 1 (flat-leaf filing as the default) and change 6 (abstention output) enter FRAMEWORK.md as design
  of record.
- D3 (embedder of record) stays open; nothing here proposes a change.

Research-lead calls, not the author's: the ranking in §3, the conflict list, and the re-wording of change 2.
