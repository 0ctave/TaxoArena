# Reframing memo v2 (checkpoint F, research-lead), 2026-10-03

Zero calls. Nothing built, run, registered or committed. As of HEAD 541fde40, ledger v357. This memo supersedes
`2026-10-02_reframing_memo.md` (v1) and carries its brackets. Every number comes from `docs/agents/results/<ID>.json`
(numbers_of_record / sentence_of_record). CERT-PC-SIZE comes from `docs/reviews/POSTRUN_cert_pc_size.md` (541fde40, VALID),
because its JSON is still "built". The framing and `report/` belong to the author; this is a proposal.

## 1. Revised framing (one paragraph; the author's to adopt, amend or reject)

**Per-cell evaluation pays where the cells carry label information.** On the content-closed v2 union split
(5,907 items / 5,404 components), a TRAIN-fitted policy on declared cells beats the best single model by +2.67pp
(V2-DECLARED-CELLS). On the anchored tree's cells it gives +2.62pp, a difference not shown in either direction
(ARCH-V2-E-T-R2 G14). On a fresh anchor-free tree, the policy still beats the best single model, thinly: +1.52pp
[+0.14, +2.91] (UNION-AF-ROUTE U1). It falls short of declared labels by -1.15pp [-2.19, -0.12] (U3b NOT EQUIVALENT,
descriptive). It is not shown to differ from per-source k-means (D_K -0.45pp [-1.31, +0.41]).

**Judge trust is the reference's trust** (unchanged from v1). JUDGE-SOLVED-SPLIT does not settle whether the judge's
own competence adds anything.

**The tree is an audited filing and addressing layer, not a better partition.** F-TAX reads "a filing device only
(N-1 fired) (lever leg not fired, by support)". The certificate certifies declared-strength structure at the root and
at depth-1 site sizes (CERT-POSITIVE-CONTROL; CERT-PC-SIZE). So the tree's 0 of 60 is not a matter of sample size
alone: its data-driven splits are weaker than the declared level at the same n. Below the anchors, the gap to
class-conditioned k-means is not the split rule (F-RULE fired). Descriptively, it lies in depth-2 fit-set membership.

**Invariance (SQ5):** the partition, and the tree's filing, belong to embedder x prompt (x corpus). Only quantisation
leaves the coarse level invariant.

## 2. SQ1-SQ5 (supports, negatives, open)

| SQ | supports (ID: number) | negatives / bounds | still open |
|---|---|---|---|
| SQ1 USE | V2-DECLARED-CELLS C1 +2.67pp [+1.46, +3.89]; G14 G_tree +2.62pp [+1.43, +3.82] (**anchored**: depth-2 = 52 declared classes); UNION-AF-ROUTE U1 G_AF +1.52pp [+0.14, +2.91] (**anchor-free**; thin; percentile [-0.03, +2.73]); per-source k-means G_K +1.97pp | U3b M_AF -1.15pp [-2.19, -0.12] (anchor-free vs declared: a shortfall); U2 D_K -0.45pp [-1.31, +0.41], spread_K 0.58pp (label-free vs label-free: not shown either way; no TOST); BBH carries 0.728 of G; MMLU-Pro +0.18 [-1.18, +1.54]; frontier roster zero | whether any label-free cell set routes as declared labels do (needs a new test; none drafted); per-corpus gains |
| SQ2 TRUST | K46-KEY-READ: reference right 0.9249 / 506, wrong 0.2632 / 38; V2-NONE-TEMPLATE EQUIVALENT (Delta_A +0.0143); C_ONE -0.1599, 82 of 97 lost matches to TIE | JUDGE-SOLVED-SPLIT JS1 UNDETERMINED: Delta_S +0.0196 [-0.0472, +0.0802], 414 matches, MDE80 0.090 (DESCRIPTIVE-ONLY); conv B reverses the sign (-0.0251); JS2 has 9 variants. The Krumdick reconciliation is not shown | RP19 G21-RESCOPED (go given; waits on D2); J-COMPLETE declined (no power) |
| SQ3 TAXONOMY | G11 P_fl 0.8119; D_fd +0.0937 [+0.0828, +0.1054]; G10 7/7 byte-identical (as sets); DSC C-AB D_AB +0.0134 [+0.0069, +0.0203] (vMF over flat k-means at matched cells; margin 0.0008 over spread, one A construction); CERT-POSITIVE-CONTROL PC1 0.1078 vs null max 0.0424 (root, n 6,993); CERT-PC-SIZE PS1 (n 486) and PS2 (n 441) CERTIFIED-AT-SIZE 5/5, k_d 0/300 on all 15 subsamples | F-TAX N-1 (G12 0 of 60; 0 of 14 depth-1); G13 D13 -0.0215 [-0.0301, -0.0125]; DSC F-RULE fires, C-DB D_DB +0.0349 [+0.0254, +0.0444], bridge P(B-gt)-P(D) +0.0028 [-0.0015, +0.0069] (descriptive: fit-set membership, not label ownership); UNION-AF-ROUTE F-AK fires (anchor-free not better than unsupervised k-means on filing: D_AUs -0.0021 [-0.0115, +0.0077] vs spread 0.0165); G12 13 of 14 TOP splits below their own null median (descriptive) | certifiable 2-way structure inside an anchor and the certificate's power for it (CERT-PC-SIZE is not k- or population-matched; PS2 shares 47-59% of items with PS1); FITSET-FAITHFUL S0 |
| SQ3 abstention | OOS-BASELINES: flat k-means no-match mean A 0.97479; beats kNN k=10 by 0.0129 and the ellipsoid by 0.0472; EQUIVALENT within 0.010 to labelled centroid (0.97640) and Mahalanobis | flat cells only; CLINC oos_plus; qwen3-256 RAW; k=1 kNN 0.97707; S0 at K50 0.94509 | tree cells: INTENT-TRANSFER-S1 T-C6/T-C7 |
| SQ4 PRICE | v2 retest floor d_r 0.100 [0.0658, 0.1342] (G17-CANARY, DESCRIPTIVE-ONLY) | no second pass | G17 pass 5, not before 2026-10-08 |
| SQ5 INVARIANCE | GOLD-LEVEL-EMB QUANT INVARIANT (MASSIVE D -0.0054, CLINC -0.0058, margin 0.025); E0b k14 flat M2 not shown worse (nomic +0.350e-3, gemma +2.173e-3; DESCRIPTIVE) | GOLD-LEVEL-EMB F-GL FIRED: PROMPT and EMBEDDER NOT-INVARIANT, DIM UNDETERMINED (seen-carried); E1 FILING HELD-WORSE -0.0456 [-0.0617, -0.0294] (nomic anchor-free tree vs af_clean_s42, 3,445 p2dca held-out under stem_key, MMLU-Pro; **at this split**: construction variation ~0, split draw untested); E0b k82 nomic WORSE | E1-SPLIT-DRAWS (author's go); tree-level SQ5 beyond MMLU-Pro |

## 3. Framework changes, re-ranked (value x evidence / cost)

| # | change | evidence state | basis (what moved since v1) |
|---|---|---|---|
| 1 | File by flat leaf, not descent | SUPPORTED (anchored tree) | D_fd +0.0937; AF-U's D_fd NOT COMPUTED (D-3), so this is not shown for anchor-free trees |
| 2 | Name the reference policy per claim; state fidelity conditional on reference correctness; invest in reference correctness, not gating | SUPPORTED | unchanged; JSS adds nothing either way |
| 3 | Ties and decisiveness as first-class columns (conv A and B) | SUPPORTED, strengthened | JSS: conv B reverses JS1's sign through ties |
| 4 | **Route on declared cells where declarations exist; tree / k-means cells only where they do not.** Claims stay at the declared or coarse level | SUPPORTED (new half: descriptive) | U3b shortfall -1.15pp; G14 not shown different; AK / U2 not shown different from k-means. Never "the tree beats clustering" |
| 5 | **Certificate as a false-discovery guard with measured sensitivity at root and depth-1 sizes**: a non-certified depth-1 split is weaker than the declared level at that n, not merely underpowered | SUPPORTED at the declared-14-way strength; untested for 2-way within-anchor structure | PC1; CERT-PC-SIZE W-2 with its three mandatory caveats; supersedes v1 change 7's bracket for the size question only |
| 6 | Embedder and prompt are part of a cell set's identity (declared with every partition, filing and route) | SUPPORTED (new) | GOLD F-GL; E1 at this split; CARD-PROTOCOL sign reversals |
| 7 | Power check (Support + reachability) as a FRAMEWORK.md stage | SUPPORTED (process) | E1-REPLICATES was withdrawn at READY, pre-data, because it would have measured a known zero spread (061a2418) |
| 8 | Abstention as a filing-layer output | SUPPORTED on flat cells only; tree PENDING [CORRECTED 2026-10-03 by OOS-TREE-CELLS (registrar; POSTRUN b9b67b11 W-1): SUPPORTED on flat AND anchor-free tree cells, within 0.010 and below k-means (Delta_T -0.00516, 95% [-0.00754, -0.00278]; CLINC oos_plus, qwen3 256, one draw); docs/judge_v2_program.md L23975-L23987 (section "## OOS-TREE-CELLS (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 964511fd)] | OOS-BASELINES; INTENT-TRANSFER-S1 decides tree cells; escalation to a reasoning judge stays CLOSED |
| 9 | #8' keep depth-2 fit sets faithful to declared classes (anchored trees only) | SPECULATIVE [CORRECTED 2026-10-03 by FITSET-FAITHFUL (registrar; POSTRUN 158d81cb): SUPPORTED (stage 0: re-estimated means on fixed topology, mostly MMLU-Pro; FF1 HELD +0.0256 [+0.0193, +0.0320], 155 of 157 net items MMLU-Pro); not evidence that a construction (S1) would gain; S1 and the A replicates stay unauthorised; docs/judge_v2_program.md L23819-L23829 (section "## FITSET-FAITHFUL stage 0 (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent 158d81cb)] [CORRECTED 2026-10-03 by FITSET-INTENT (registrar; POSTRUN 06f03005): #8' NARROWED to "MMLU-Pro-specific; not shown on intent corpora, and it hurts on CLINC" (FI1 MASSIVE +0.0049 UNDETERMINED; CLINC -0.0264, interval below 0); docs/judge_v2_program.md L24001-L24009 (section "## FITSET-INTENT (2026-10-03, 0 calls) — VALID ..."; _as_of the commit that writes it, parent b8f7cbee)] | DSC bridge (k-means arms, descriptive); FITSET-FAITHFUL S0. v1 #8 "replace deep splits" WITHDRAWN (F-RULE) |

## 4. Proposed wording (THE AUTHOR'S DECISION; drafts only)

**D2 (SQ2 instrument and v2 reference policy)**, v1 text kept, one sentence added: "SQ2's content-closed claims are
stated under the v2 recipe: judge grok-4-1-fast-non-reasoning, dual order, TIE on flip. The reference is the cached
grok-4-1-fast-reasoning solve where one exists (class ONE) and none otherwise (class NONE), on pv2_41dbd3dbcd399df0.
Every fidelity figure is reported by reference class, in conventions A and B, and, where a key exists, conditional on
the reference's correctness. The false 'carries a reference' sentence on NONE matches leaves key accuracy equivalent
within +-4pp (RP20). Whether the judge's own solve status changes fidelity under a right reference is not determined
at n 414 (JUDGE-SOLVED-SPLIT). STACK-v2 numbers stay id-disjoint only or [P-FAM] history." Consequence: RP19 runs under
this policy (N1 on NONE, the research-lead's recommendation).

**D6 (SQ3 wording)**: "On a content-closed split, a TRAIN-only tree anchored on declared classes gives cells that are
reproducible (byte-identical on the declared set, as sets, for 7 build pairs) and order-stable.
- They file union EVAL at 0.812 from flat leaves (+9.4pp over descent; MMLU-Pro alone 0.745).
- They route the union roster as declared labels do (+2.62 vs +2.67pp; the difference is not shown).
- The tree certifies none of its 60 sites at per-family q 0.05. On the same member, the certificate does certify the
  declared 14-category partition at the root and when subsampled to the depth-1 site sizes, so the tree's
  non-certification is not explained by n alone. That comparison is not k- or population-matched.
- Below its anchors the tree files 2.15pp worse than class-conditioned k-means. The gap is not the split rule;
  descriptively, it lies in which TRAIN items each anchor's cells are fit on. Its lead over unsupervised k-means
  belongs to the anchors.
- An anchor-free tree built on the same split routes above the best single model (+1.52pp, thin), short of declared
  labels (-1.15pp). It files no better than unsupervised k-means."

Forbidden words, as in v1: "label-free" (for the anchored tree), "deterministic", "converged", "purer than flat
clustering", "parity", "the certificate is validated at depth 1".

## 5. Draft leads awaiting the author

- **FITSET-FAITHFUL.** Stage 0 is registered (prog L23580; zero calls, no build, CPU); `--run` waits on your scope
  word (checkpoint D Q4) and the C-PB-1 ruling. Research-lead view: S0 is in scope as an anchored-tree diagnostic of
  change 9. It adds TRAIN-label use only, so it is not evidence about label-free trees. S1 (the anchorFitSet flag, the
  A-gt construction and A replicates) stays unregistered, and the order-shuffle finding behind the E1-REPLICATES
  withdrawal means "A replicates" must be re-specified as split re-draws.
- **E1-SPLIT-DRAWS.** Draft only (prog L23779). It separates embedder from split draw for SQ5's tree-filing clause,
  and costs up to K author-run WAL checkpoints plus 2K builds (unpriced). Without it, the sentence stays "at this
  split". Research-lead view: worth K = 2 only if the thesis states SQ5 at tree level beyond one split; otherwise
  disclose.
- **INTENT-TRANSFER-S1 builds.** The go was given (D5, Amendment 31). The definitions are bracketed (L23752ff). The
  readout script and its READY are still owed. The builds take 5-9 machine-h (unsourced) at 12 threads under rule 7.
  The machine-lane slot is yours. It is the only test of tree-cell abstention (change 8) and the next SQ3 item of
  value.

## What this memo does NOT show

- That any label-free cell set routes as well as declared labels. U3b shows the opposite for one anchor-free tree,
  descriptively. No TOST shows parity anywhere.
- That trees beat or lose to clustering in general. AK and U2 are one draw, one recipe, one roster, qwen3-256, and
  "not shown" is not parity.
- Anything for MMLU-Pro routing alone, or a ranking of anchor-free against anchored recipes.
- That the certificate certifies tree sites, or has power for 2-way structure inside an anchor. CERT-PC-SIZE is
  14-way, all categories, one member, one draw, and PS2 is not an independent replicate.
- That declared-faithful fit sets would help the vMF construction (the bridge is descriptive, on k-means arms), or a
  seed-free C-AB.
- That judge competence matters or does not (JS1 UNDETERMINED).
- That tree cells abstain, or OOS behaviour on traffic or a corpus other than CLINC.
- That the nomic filing loss holds across split draws, or that any embedder is better. D3 stands.
- Coarse-level invariance beyond quantisation.
- Anything about SQ4 beyond one retest floor.

## Decisions that are the author's

The section 1 framing; D2 (it gates RP19); D6 and the withdrawal of v1 #8; whether changes 1, 4, 5, 6 and 8 enter
FRAMEWORK.md as design of record; the FITSET-FAITHFUL scope; the E1-SPLIT-DRAWS go and K; the INTENT-S1 machine slot;
D3 stays open. The research-lead's own calls are the ranking in section 3, the new change 4 (declared-first routing)
and change 6, and the views in section 5.

Record notes for the registrar (nothing edited): F-TAX.json `does_not_show` still says "L-1 open" and "UNION-AF-ROUTE
not run"; both are stale since 589c04ae. CERT-PC-SIZE.json is still in state "built".
