# Checkpoint D (research-lead), 2026-10-03: tonight's results against the reframing memo

Zero calls. Nothing built, run, registered or committed. Read: KNOWLEDGE.md, `2026-10-02_reframing_memo.md`, and
`docs/agents/results/{DEEP-SPLIT-COMPARE,JUDGE-SOLVED-SPLIT,OOS-BASELINES,E1-ROUTE}.json` (ledger v349, HEAD 81f44d26).
GOLD-LEVEL-EMB is still running; I did not read its files.

## 1. What each result changes (memo section; framework-change number)

- **DEEP-SPLIT-COMPARE (VALID bcd4a88f; W1, W2).** The vMF rule beats flat k-means at matched cells (C-AB HELD,
  D_AB +0.0134 [+0.0069, +0.0203]). This is knife-edge: 0.0008 over B's spread, and A is one construction. F-RULE FIRES:
  no label-free split rule recovers half the G13 gap. C-DB HELD, D_DB +0.0349 [+0.0254, +0.0444], MMLU-Pro +0.0497. The
  bridge B-gt puts that edge in **depth-2 fit-set membership** (P(B-gt) - P(D) +0.0028 [-0.0015, +0.0069]), not in
  label ownership below depth 2. The tree's routed fit sets are class-pure for 0.8125 of TRAIN items (POSTRUN W2).
  *Memo:* the SQ3 row and D6 say "below its anchors it files worse than class-conditioned k-means". Keep the
  sentence, but read "below the anchors" as the location, not the cause. Add: "the gap is not the split rule
  (F-RULE fired). Descriptively, it is which TRAIN items each anchor's cells are fit on." *Changes:* withdraw **#8**
  ("replace deep splits by the winner"): there is no winner, and SPLIT-VMF and HYB-LC as drafted are not indicated. Add
  **#8' "keep depth-2 fit sets faithful to declared classes"** as SPECULATIVE, for three reasons. (a) The basis is one
  descriptive bridge on k-means arms, not the vMF construction. (b) It uses more TRAIN labels, so it is an
  anchored-tree change only and moves the tree further from "label-free" (C4). (c) Fit-set size is confounded with
  purity. It earns design status only through section 2.
- **OOS-BASELINES (VALID c5416c52).** The memo's open question was whether 0.974 belongs to the cells or to the
  geometry. On flat cells, the cells beat both registered label-free peers: kNN k=10 by -0.0129 and a single
  ellipsoid by -0.0472 (CELLS-ADD). They match the labelled detectors within 0.010 (COMPETITIVE; centroid +0.0016
  excludes 0). The lead depends on k and K: kNN k=1 0.97707, S0 at K50 0.94509. *Change #6 (abstention output):*
  PENDING becomes "supported on flat k-means cells, CLINC oos_plus, qwen3-256 RAW". Tree cells are still
  INTENT-TRANSFER-S1 T-C6/T-C7, so C2 stands (never the tree).
- **JUDGE-SOLVED-SPLIT (VALID b60dd49d).** JS1 UNDETERMINED: Delta_S +0.0196 [-0.0472, +0.0802] on 414 matches
  (measured MDE80 0.090, DESCRIPTIVE-ONLY). Convention B reverses the sign (-0.0251, through ties). JS2 does not show
  the Krumdick pattern, but only on 9 variants. *Memo:* SQ2 and change #2 are unchanged, and nothing licenses "judge
  competence does / does not matter with a right reference". Section 5 should read "Lee-vs-Krumdick not reconciled
  at this n", not "exactly JSS". J-COMPLETE (29 paid solve calls) cannot shrink an MDE of 0.09, so I do not
  recommend it.
- **E1-ROUTE (L1 VALID c2468c2a; builds VALID ba32fbc6).** This is engineering only. The JVM working-copy route holds
  (C1-C5, F1 not fired). E1's FLAT/FILING criteria stay unscored until the readout runs, and the readout waits on the
  WAL checkpoint. No framing change. It enables SQ5's first cross-embedder tree-level reading.
- **GOLD-LEVEL-EMB: [slot reserved; still running].** Until it reads, C3 stands: no coarse-invariance sentence.

## 2. Follow-up DSC indicates (draft lead, NOT registered): FITSET-FAITHFUL

Claim: with the vMF construction rule held fixed, fitting each anchor's sub-cells on the TRAIN items of its declared
class files EVAL better than fitting them on the tree's routed fit set. The bridge saw this on k-means arms only.
- **S0 (zero builds, CPU; a pool reader).** (i) Dose-response over the 32 split anchors: per-anchor
  P(B-gt) - P(B) against F-tree impurity, with fit-set size as a covariate (separates purity from size).
  (ii) **A-refit**: keep A's leaves and topology, re-estimate each leaf's vMF mean from the TRAIN items of the
  anchor's class only (nearest A-leaf within the anchor), and file EVAL. Deciding: D = P(A-refit) - P(A), interval
  above 0 AND D above spread_B (A's own spread is unmeasured). Support transported from C-DB: 6,139 / 5,628, DEFF
  about 1.22, MDE80 about 0.014. SCOREABLE if the effect is at least half the bridge (about 0.019). Falsifier: D's
  interval at or below 0 means purity is not the lever for the vMF rule, and the bridge is a k-means artefact. #8'
  is then withdrawn.
- **S1 (only if S0 HELD; constructions, one at a time).** An engine flag `anchorFitSet=declared`, inert when absent.
  Build A-gt plus A at 2 more construction seeds; the replicates also settle W1. The cost-estimator prices it. It
  runs after RP13 and CERT-POSITIVE-CONTROL. Hygiene: TRAIN labels only. EVAL is never seen. Claims are refused
  below the declared level (closed sub-anchor lines).
- Delegation, if the author says register: tree-construction-specialist drafts S0, then registrar (with Support),
  engine-coder (dry-run), adversarial-reviewer, run-operator.
- Side note for CERT-POSITIVE-CONTROL: PC3's "TOP-site populations" are the tree's routed sets, about 19% impure.
  PC3 is DESCRIPTIVE-ONLY, so this is a wording caveat, not a blocker.

## 3. Queue for the next 24 h (zero calls)

| # | item | lane | gate |
|---|---|---|---|
| 1 | GOLD-LEVEL-EMB finish, then post-run review, then registrar | machine (running) / agents | none |
| 2 | CERT-POSITIVE-CONTROL Kotlin declared-site arm, then READY | agents | none (launch waits on WAL) |
| 3 | INTENT-TRANSFER-S1 build, then READY (tree-cell abstention, T-C6/T-C7) | agents | none (construction waits on rule 7) |
| 4 | FITSET-FAITHFUL S0 draft, then registration | agents | author's word to register |
| 5 | **after WAL:** E1 readout (minutes, a reader), then UNION-AF-ROUTE build (the only like-for-like label-free SQ1/SQ3 test), then CERT-POSITIVE-CONTROL site null | machine, strictly serial (rule 7) | **author's WAL checkpoint** |
| 6 | FITSET-FAITHFUL S0 run | machine (a reader; never beside a construction) | registration + READY; C-PB-1 scope (Q2) |
| 7 | registrar housekeeping: E1-ROUTE record state, memo brackets (section 5 JSS line, C4) | agents | none |

Not in the window: RP19 (D2), G17 pass 5 (not before 10-08), the SLOTSWAP-DECISION paid leg, JUDGEBENCH-CJB-SIDE
(8,470 cce, its own go), J-COMPLETE (declined: no power), SPLIT-VMF and HYB-LC as drafted (not indicated).

## What these results do NOT show

- A seed-free C-AB (A unreplicated), or that the vMF rule beats k-means in general.
- That declared-faithful fit sets would help the vMF construction. The bridge is descriptive and uses k-means arms.
- Anything about anchor-free trees (RP13), or parity of any two arms (no TOST).
- That tree cells abstain, or OOS on traffic or another corpus. OOS-BASELINES covers flat cells, CLINC, qwen3-256 only.
- That judge ability makes no difference, or that it does (JS1 UNDETERMINED). The Krumdick reconciliation is not shown.
- Any E1 science: its FLAT/FILING criteria are unscored. GOLD's result is not read.

## 4. Questions for the author

1. When can you checkpoint `mmlu_pro_dataset_cache_v2.db-wal`? It unblocks the E1 readout, the RP13 build and
   CERT-POSITIVE-CONTROL.
2. Does C-PB-1 (the WAL checkpoint before any pool reader) also bind union-pool readers such as FITSET-FAITHFUL S0?
   DSC ran tonight under the B0-2 check. The data-steward should rule; the timing of item 6 depends on it.
3. Do you adopt the D6 re-wording (location, not cause) and the withdrawal of change #8?
4. Should FITSET-FAITHFUL S0 be registered? It is a zero-build test, but it deliberately adds TRAIN-label use to an
   anchored tree. Is that inside the thesis's scope?
5. Change #6 (abstention output): enter it into FRAMEWORK.md now as "flat cells only", or wait for INTENT-TRANSFER-S1?
6. D2 is still open and gates RP19.
