# TaxoArena research plan, 2026-09-27 (revision 2, after the adversarial review)

Research lead, programme of record. This pass made zero calls. It registered nothing, built nothing and wrote nothing to the repo.

**What it rests on:**
- CONTEXT.md, re-read in full this pass.
- FRAMEWORK "Tests to register" and "Limits" (FW L251-L384), plus FW L186-L195 (online operation), re-read this pass.
- The adversarial review of draft 1. Its 27-row per-claim table is cited below as "rev row n". Its verdict was NOT READY. This revision applies H1-H5, M1-M13 and L1-L17.
- My own re-reads this pass:
  - prog L15076-L15084, L16009, L16041, L19459, L19486, L19524-L19532, L21216-L21228;
  - ledger L73, L226, L289;
  - queue items INCONSISTENCIES-PASS, UNION-AF-ROUTE, ARCH-V2-G22, G22-REAL-SUPPLY-RERUN, JUDGEBENCH-CJB-SIDE, EVAL-METRIC-DETERMINISM, MIX-FLAT-SELFTEST-GAPS and FLAT-MIX-ANCHORED;
  - commits eef090a, a249f77 and a34642c;
  - the local Ollama manifests (`Z:\Ollama\Models\manifests`).
- Queue: 169 items. HEAD 9e216ba (the MIX-LRT-SITE outcome). There is no `day_calls_2026-09-27.json` (rev row 1).
- Other numbers come from the verified assessments behind the brief and carry their pointer. Estimates are marked "unsourced".

**Abbreviations:**
- prog = `docs/judge_v2_program.md`
- ledger = `docs/test_ledger.html`
- FW = `docs/design/FRAMEWORK.md`
- CTX = `docs/agents/CONTEXT.md`
- q = queue
- syn = `docs/agents/results/evidence/ARCH-V2_SYNTHESIS_2026-09-23.md`
- brief v2 = scratchpad `tree_argument_brief_v2.md`
- RPnn = this plan's items. The IDs are stable handles; the rank order is in §B1.
- **[P-FAM]** = "post-incident recipe on the p2dca / x12-schedule judged sample". That sample is r8-era, id-disjoint only, drawn on the frozen tree's cells, and its anchor rubrics were induced while 71% of the pool sat on that tree's train side. The mark means the boundary ruling is pending (§A4). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C2): misleading: the 14 STACK-v2 anchor rubrics were induced from TRAIN-side texts assigned to the frozen tree's leaf centroids, withholding p2dca by exact text (0 exact / 14 norm-v1 twins; prog L80 bracket, review 8ebfa7a); what unites the family is the r8-era sample drawn on the frozen tree's cells, routing in-sample for about 71% (incident doc), and id-disjoint-only splits; the defining words are now the judge-design-specialist's ruling (docs/reviews/RULING_w0_p2dca_family.md, 5effe96), with the registrar's WHY-clause bracket]

---

## 0. One screen

**The question:** when does filing questions into cells change which model an evaluator should use, or which comparison it may trust? What does a TRAIN-only taxonomy add to that, and which answers survive a second embedder, a second tree draw and a second corpus?

**The eight directions, in rank order:**
1. Correct the record, including one ruling for the whole p2dca judged family (RP01).
2. The first content-closed fidelity number under the v2 recipe (RP04).
3. The content-closed wording conversion of USE, plus an MMLU-Pro key R that uses no embedder (RP03, two legs). This is a sensitivity, not a replication.
4. FLAT generality with no builds (RP05).
5. The certificate under re-draw (RP06).
6. Thread cap, embedder plumbing and the nomic arm: the author's embedder question (RP07-RP09).
7. The dataset survey, then SuperGPQA: the author's dataset question (RP10-RP11).
8. The content-closed tree lane and the label-free routing test (RP12-RP13).

**What the author decides first:**
- Adopt the framing, with the corrections in §A3 and the widened boundary in §A4.
- The machine-lane order and the JVM thread-cap amendment.
- Which embedders run, and under which protocol.
- Whether external corpora enter scope (SuperGPQA first).
- The v2 reference policy (mint slice or the NONE template), and RP19's cost (≤ ~14k cce).

**Bill (unsourced except where pointed):**
- **Core:** 0 judge calls. About 23-34 machine-hours at 12 threads, most of it the E-T lane. About 15-20 agent-days.
- **Strengthening:** about 10.4k judge calls (+2.4k optional) across four separate tests, each under 4,000 matches. About 8.8-19.1 priced CPU/machine-hours. About 10-14 agent-days.
- **Paid extension:** RP34 JudgeBench, 1,400 calls (READY, gated).

---

# PART A — THE QUESTION

## A1. Framing of record (adopted from framing B)

**Name:** Cell-conditional evaluation.

**Central question.** Revised per M10: the instrument slot is now open.
> "For a fixed roster, a corpus split content-closed under CK-CLOSE, and a fixed verification instrument named per claim (an answer key, an executed checker, or one frozen judge recipe with its reference policy stated): when does evaluating per cell change which model an evaluator should use, or which pairwise comparison it may trust, compared with one pooled leaderboard? What does that cost, and which answers survive a second embedder, a second tree draw and a second corpus? Cells are declared labels for the arena, and are read by a TRAIN-only embedding taxonomy where labels are missing."

**Why the slot stays open.** Every content-closed judged datum in the record is under the v2 recipe (the K46 store), and 69.3% of its matches carry no reference (prog L19506). Which judged recipe SQ2 is stated under is the author's decision (§B7 item 6).

**Closest prior work (M9).** Huot, Kaisers and Lapata, "When is Routing Meaningful?", arXiv 2607.09197, 10 Jul 2026 (https://arxiv.org/abs/2607.09197; verified to exist, rev row 19).
- It asks SQ1's question almost verbatim.
- Its findings are not summarised here. The science-writer and I read it before A1's wording is frozen.
- Candidate differences, each to be checked against the paper and not asserted until then:
  - content-closed splits;
  - a TRAIN-only, certificate-carrying source of cells;
  - judge fidelity where no key exists.
- It is cited in A7 and RP16, not only under a dropped item.

**Scope rules S1-S5:**
- **S1. Arena cells are declared.** This is synthesis decision 5, recorded in item (4) at prog L15080 ("cells DECLARED (decision 5)"). It is a default that stands until the author says otherwise. The tree is off the arena path (syn L100). The tree is audited as filing (G11/G13), M (G14), partition (FLAT) and certificate (G12).
- **S2. Verification fidelity only** (CTX §1; FW L253). There is no unkeyed corpus in the record (syn L32). Transport to an unkeyed corpus is untested. For a new corpus, "the widener's parameters do not transfer across corpora (untested)" (FW L191, step (5)).
- **S3. Every object carries its split word** (CTX §4 rule 12).
  - Content-closed: af_clean_s42 (R256), and the v2 split 5a3e756: pv2_41dbd3dbcd399df0 (3,492 EVAL) and pv2_1575de61bb20e977 (6,153 EVAL) (prog L16193-L16198).
  - Id-disjoint only: p2dca / bareq512_s42 (bound 2.03pp); paeec (bound 1.32pp); the anchor-free re-draws af_s137, af_s2048 and af_s42_o1, until the steward's check (R-D).
- **S4. Recipes are never joined.** R256 and R512 counts are never set against each other (prog L21006). T1 and T1b are stated separately (ledger L177). L21006 scopes the ban to CERT-RESOLUTION's counts. A registered within-embedder dimension ladder (D1-D3, ledger L86) has its own words, so S4 must not be read wider.
- **S5. Closed lines stay closed** (CTX §5). The LCB STOP is quoted with its synthetic-power qualifier until POWER-RESIM lands.

## A2. Sub-questions: answered, open, closers

### SQ1 (USE)
*Does a per-cell policy fitted on TRAIN beat the best single model on content-closed EVAL, and on which (roster, corpus) pairs?*

**Answered, id-disjoint only:**
- **Six-corpus union (paeec):** G = +2.92pp [+1.81, +4.02] on 6,482 EVAL questions, 18 models and 52 strata (ledger L182; prog L14145-L14184). This reads the cell PREDICTED by the qwen3 union tree.
  - The declared-cell comparator uses TRUE labels: +3.09 [+1.98, +4.19].
  - With twins removed: +3.28 [+2.12, +4.44] (ledger L182).
  - BBH carries +1.96pp. The MMLU-Pro source alone reads +0.86 [−0.54, +2.26]. The placebo is centred at −0.52.
  - Leave-BBH-out reads +1.305, carried by MMLU-Pro (+0.65) and MuSR (+0.63); IFEval contributes +0.21 (router_clean_policy_outcome.txt L125-L132; rev row 21).
- **MMLU-Pro with a frontier roster (ROUTER-REGRET-MMLU):** +0.000 ± 0.007 by anchor and −0.002 by leaf. gemini is best in 14/14 anchors (ledger L303; the ± is at FW L131).
  - It is read per leaf and anchor of bareq512_s42 on p2dca (prog L595). So it is id-disjoint only, and its cells are filed by a qwen3 tree.
- **Judged argmax:** −4.7pp pooled (GEN-ARENA, ledger L318). EXPLORATORY, on a re-derived side, not the router's split (overlap 114/394 MATH, 55/162 IFEval).
- **Licensed words:** "on the two rosters measured", never "only".

**Open:**
- The content-closed wording.
- The BBH share. 1,096 of the 1,142 residual pairs are BBH.
- How the gain depends on the roster.
- The protocol confound. The union's MMLU-Pro, BBH, GPQA and MuSR rows are log-likelihood argmax; TIGER K12/K46 are generative CoT (multi_corpus_design.md L236-L243). The two SQ1 points therefore differ in protocol as well as roster.

**Closers:**
- RP03 leg U. It re-splits the same ~20.5k-item family with the same 18 models, so it is a content-closed sensitivity and wording conversion, not a replication (M4).
- Strengtheners: RP16 (roster dose curve), RP18 (HELM frontier multi-source), RP17 (BFCL key roster), RP11 (SuperGPQA stage 0).

### SQ2 (TRUST)
*At which grain are per-cell comparisons reliable on the key and on the judge, and what sets the judge's fidelity in a cell?*

**Answered:**
- **Key, interaction-only R, each against its own null** (ledger L239):
  - K12: 0.8665 [0.8000, 0.9330] against 0.3142.
  - K46: 0.8118 [0.7254, 0.8983] against 0.2343.
  - Both are on p2dca routed by bareq512_s42: id-disjoint only. The anchors are filed by a qwen3 tree (24.7% misfiled, ledger L280), so these numbers are not embedder-free.
  - The 52 declared union strata read 0.8537 (FW L260). Those strata are declared, so this number uses no embedder; it is id-disjoint only (paeec).
- **Judge [P-FAM]:**
  - Anchor-profile R: 0.7183 [0.6076, 0.8291], published as PASS-WITH-INTERVAL forever.
  - Filtered: 0.5613 [0.3385, 0.7842] (FW L260).
  - The key beats the judge by +0.194 [0.037, 0.351] on x12 and +0.121 [0.030, 0.211] merged (ledger L239).
- **Fidelity and the reference [P-FAM throughout]:**
  - PAIR-NOREF: paired +12.6pp, 0.864 against 0.738, 144:25 (ledger L217).
  - 0.852 is the board-scale figure (convention A, 4,507 key-decidable matches; FW L79, repeated at L263). 0.865 is a selection maximum (FW L263).
  - CONSENSUS-FIT (x12 MAIN arm): 0.922 / 0.657 / 0.226 (ledger L208).
  - Judge family:
    - one cross-family pair on 7 scored anchors (prog L7508);
    - JUDGE-SWAP 0.865 vs 0.864 on 944 R3 pairs (ledger L300);
    - JUDGE-BY-CELL M 0.8523 vs 0.8483 on 4,495 key-decidable matches (ledger L237), read per bareq512_s42 anchor.
- **Misfiling:** 24.7% realised, with 0 established edges reversed (ledger L280).

**Not SQ2 evidence:** the OPTION-A LRT, 38.8 against 21.0 (`clean_subset_reanalysis.txt` L33-L35). It is r8 family.

**Open:**
- Any judged number under the v2 recipe. K46 has no key-based quality readout (prog L19528), and 69.3% of its matches carry no reference (prog L19506).
- **The NONE branch's false sentence.** Every one of K46's 5,328 bodies carries one system turn (sha d0c524bb, 2,085 chars) that states "The question carries a reference solution". This includes the 3,692 NONE bodies (K5, prog L17664; confirmed on the store, rev row 5).
- An MMLU-Pro key R that is content-closed and uses no embedder.
- A third judge family. Local candidates exist (RP55).

**Closers:**
- RP04: the K46 key read at zero calls. The key is already unsealed at model-edge level (outcome L77; prog L16856), so this needs a reuse ruling, not an unseal.
- RP03 leg M (the embedder-free, content-closed key R, H2) and leg U's secondary R.
- Paid: RP19 (G21 re-scoped), RP20 (the NONE template), RP21 (G17).

### SQ3 (TAXONOMY)
*What does a TRAIN-only tree add beyond declared labels (filing, M, partition, certificate, label-free cells)?*

**Answered:**
- **Filing:** flatLeaf 81.58% [80.62, 82.50] against 72.08% by descent, 819:203 (ledger L201). Id-disjoint only, and descent compares the tree with itself.
- **M:** +0.17 [−0.61, +0.95] at an MDE of ~1.1pp; "neither a cost nor parity is shown" (ledger L182). MC-LEAF reads −0.9 ± 0.3pp, i.i.d., flag open (ledger L321).
- **Partition:**
  - FLAT: purity −4.3pp [−5.6, −2.9] and F6 −1.534e−3, on one tree (af_clean_s42), one comparator and one corpus.
  - The mechanism is NOT IDENTIFIED (prog L21121-L21274).
  - The anchored control O ties V0 (0.770 vs 0.770). It is reported only and POST-HOC-SEEN (prog L21142-L21143).
  - The licensed sentence, verbatim (prog L21218): "on MMLU-Pro the hierarchy buys the certificate, the support per cell, the names and the routing discipline; its cells are a worse partition than a flat mixture at the same granularity".
  - NOT licensed: "that trees, or this construction, are worse partitions in general" (prog L21220-L21227; brief v2 L264-L271).
  - 20NG: the tree ties k-means (ledger L226).
- **Certificate:**
  - 2 of 70 at per-family FDR 0.05 on bareq512_s42 R512. BY rejects nothing. 53 sites are untested (prog L20957-L21027).
  - The J null discriminates where the GMM LR certifies 282/282 (ledger L159, with the W1 qualifier).
  - Not a fixed point (CTX §3).
  - R256, stated separately: 5 re-draw-stable sites (ledger L244), and 5 label-free cells carry 54% of the names' key information (ledger L235).
- **Withdrawn:** "anchors cost certification". REDRAW F4 fired: 14/69 against 11/60 on the clean split (ledger L244, L256).

**Open:**
- G11-G14 on a content-closed tree (ARCH-V2-E-T, q drafted).
- UNION-AF-ROUTE, the only label-free test (q drafted, script absent).
- FLAT under a second draw, embedder or corpus.
- The dip half of L6.
- **J's size and power against planted truth.** prog L21397's "nothing here" is scoped to MIX-LRT-SITE. The only read of certified sites against truth is TOPIC-PARTITION-20NG Q2, "identify topics at its certified sites" (ledger L226). No test plants truth and reads J's size and power (RP25).

**Closers:** RP05, RP06, RP09, RP12, RP13. Strengtheners: RP24-RP27, RP29, RP30.

### SQ4 (PRICE and the "dynamic" axis)
*What does judged trust cost as rosters grow, newcomers arrive and corpora are added, and at what realised error rate?*

**Answered:**
- **K46:** β̂ 1.8014 [1.2821, 2.3207]. The record's words are "P EXCLUDED", NOT "M EXCLUDED" (prog L19459).
  - 2 anchors (health, math); k 12 → 37.
  - Planning scale only: "every nu and beta is on the frozen GROK-CALIB pair transported from 12 models" (prog L19526-L19530). The scale is therefore [P-FAM].
  - Measured DEFF of β̂: 1.0785 (prog L19486).
- **Calibration:** UNDETERMINED on every board in reach (FW L255). GROK-CALIB's b1 is not identified at 0.05 (ledger L264) [P-FAM].
- **Newcomers:** "400 + 100 per separable tier", which holds mid-board only (ledger L231; FW L189 bracket, L380) [P-FAM: two newcomers on the x12 board].
- **Federated construction:** 13 against 5 (ledger L200). An arriving domain is ABSORBED (ledger L94).
- **Drift:** epoch 2 NO ALARM, 0.070 against 0.138 (prog L15882) [v1 recipe, p2dca canary: P-FAM]. Pass 2 and pass 3 were about 50 h apart (prog L15891), not a week.

**Open:**
- The board size (author's decision).
- G22 stays RUNNING by the record's own words. Its designs and stop are recorded (prog L16009-L16041); the real-supply re-run is owed (q G22-REAL-SUPPLY-RERUN), and no stage-1 reading may be cited until it runs.
- Calibration above 4k matches (needs a go).
- G17.
- Drift under v2. The v2 loader is EVAL-only (loader.py L11), so the frozen p2dca canary cannot be re-floored whole.

**Closers:** "priced, and UNDETERMINED" stands without spend. Strengtheners: RP21, RP23. Extension: RP40.

### SQ5 (INVARIANCE)
*Which answers to SQ1-SQ3 belong to the method rather than to qwen3, seed 42 and MMLU-Pro?*

**Answered:**
- **Seed floor:** Top-1 0.750-0.776, leaves 72-92 (ledger L73), leaf ARI 0.585-0.704 (FW L57).
  - This is split-draw variance, because construction is seed-inert on a pinned split (TaxonomySplitter L527; TaxonomyMerger L447; runner L525-L528; code read, not executed).
  - Geometry-only carve-out (§A4): the frozen recipe, label-free, with no judged number.
- **Dimension:** D1-D3 (ledger L84-L86), under the same geometry-only carve-out.
- **Embedder:** EMBED is EXPLORATORY and confounded (ledger L79):
  - bar reused from qwen3;
  - no prefix, although the nomic card requires one;
  - no layer_norm before the slice, although the card prescribes it (the engine has 0 layer_norm hits);
  - anchored; p8a29; pre-P7-FIX.
- **Corpus:** 20NG (partition only); LCB STOP at synthetic power (prog L19732-L19800); the union.

**Open:** every licence under a second embedder; FLAT under a second draw; a keyed corpus outside the six OLL-v2 tasks.

**Fact to write now (H2).** Only readouts on declared cells contain no embedder:
- true-label G (+3.09);
- the 52 declared union strata (R 0.8537);
- both legs of RP03.

Every MMLU-Pro readout of record read through bareq512_s42 reads anchors filed by a qwen3 tree (24.7% misfiled, ledger L280), so it can move with the embedder. These are key R 0.8665 / 0.8118, judge R 0.7183, ROUTER-REGRET-MMLU and JUDGE-BY-CELL. +2.92 can move too, because it reads cells predicted by the qwen3 union tree. Under S1 the arena uses declared cells. The embedder question therefore bears on:
- the taxonomy's licences;
- the label-free test;
- every tree-filed readout of record.

It does not bear on declared-cell readouts.

**Closers:** RP05 (draw), RP09 (embedder), RP10-RP11 (corpus). Strengtheners: RP14, RP15a/b, RP26, RP27, RP53.

## A3. Corrections to the framing of record and to this plan's first draft

The registrar inserts each of these as a bracket.

1. **r8 counts.** 2,425/3,445 is 70.4%; the incident doc's 2,437 is 70.7% (incident doc L9-L12). Ledger L148 pairs 2,425 with "71%". 3,445 is the pool's JUDGEABLE count, not r8's judged set.
2. **"Contaminated position fits"** means 22 per-leaf fits. All 8 pooled r8 leaderboards reproduce (experiment_results/r8/refit_delta_report.md).
3. **Pointers.**
   - Arena cells declared = synthesis decision 5, recorded in item (4) at prog L15080. L15082 is item (5), the ARCH-V2 queue entry.
   - The syn text is at L32.
   - Draft 1's "0.852 is at FW L79, not L263" is withdrawn: both lines carry it (rev row 20).
4. **"Nothing judged an agent trace" is false.** BFCL-JUDGED-PILOT, 1,316 calls, ledger L224:
   - C1 FAILED at the point (A 0.7402 = 339/458) and was UNDETERMINED by interval [0.6640, 0.8164];
   - B 0.9469; ties 0.2183.
   - FW L271 predates the pilot, and FRAMEWORK never names it (grep: 0).
   - The outcome file's mechanism sentence (outcome L39) was STRUCK by the post-run review (prog L11866-L11878). Only "decisiveness collapsed, not fidelity" is licensed. [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C3): not record text; the licensed words are "a DECISIVENESS result, not a FIDELITY result" (prog L11876)]
5. **"158 model directories" is 109.** Sources: `docs/agents/leads/2026-09-18_agent_corpora.md` L15/L63/L123; prog L5905. Checked with the GitHub git-trees API, untruncated, at pin 6830ed13 and at HEAD cadd76a8 (rev row 9).
6. **REG-2's E0 has no valid object.** af_s42_o1 is on split p8a29, not p2dca (config.toml L5-L6), and is membership-identical to af/seed_42 (ledger L244 R4). A "qwen3 new-seed control" on af_clean_s42's pinned split would be a byte replay (prog L4675-L4680).
7. **REG-2's "FLAT unchanged except the model" is impossible as written.** flat_mix_mmlu.py hard-codes the pool, FIT_N, K, T_RUN, T_LEAVES, READOUT_TXT and the qwen3 DB (L89-L128, L592-L596). The embedder is a JVM `-D` property, not a TOML key.
8. **F-TAX leg 3 (G12) is ill-defined.** Anchored trees have 0 depth-0 sites (cert_resolution_sites.csv), so "root uncertified" can never fire. "Certifies < 5 sites" names no counting rule: 10/70 per-site against 2/70 per-family FDR. Re-stated in §C2 R-A.
9. **REG-1's Support.**
   - Draft 1's "manifest kish bound 1.89" is REFUTED (rev row 3b). No 1.89 appears in REG_ARCHV2-SPLIT-2's checks.
   - Recomputed from `v2.kish_eval_items`: the EVAL-side component Kish is **1.304** (BBH 1.73, MuSR 2.48); the whole-split key Kish is 1.905.
   - Support is re-derived in R-B.
   - Its "leave-BBH-out covers 0" prediction contradicts the paeec analogue +1.305, which is carried by MMLU-Pro and MuSR (router_clean_policy_outcome.txt L125-L132). [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C4): "contradicts" is "is in tension with" (the analogue is a DESCRIPTIVE point with no interval; see the framing copy's L220 bracket, B13)]
10. **"Anchors cost certification"** (my brief) is withdrawn (§A2 SQ3).
11. **S2's transport pointer.** Ledger L289 is JUDGE-TRANSFER, i.e. the widener across judge families. Transport to unkeyed corpora is FW L191 step (5) (rev row 22).
12. **G22.**
    - prog L15636 is stale. The designs and stop are at L16009-L16041, plus q G22-REAL-SUPPLY-RERUN.
    - The record says "ARCH-V2-G22 stays RUNNING" (L16041). My draft-1 brief asking the registrar to call "running" stale is withdrawn.
13. **"Nothing scores J against truth"** (prog L21397) is scoped to MIX-LRT-SITE. See SQ3 Open.
14. **REG-1 is a sensitivity, not a replication.** It uses the same item family and roster, and twin removal already reads +3.28 [+2.12, +4.44] (ledger L182).
15. **Embedder invariance.**
    - Draft 1's "SQ2 readouts contain no embedder" is false for the MMLU-Pro readouts (rev row 25).
    - Its "+2.92 can move only within M's interval" is also wrong. That interval is the sampling uncertainty of the qwen3 tree's M and does not bound another embedder. Worse filing moves G toward the pooled-best value.

## A4. How r8 and the p2dca judged family are disclosed

**Proposed r8 paragraph.** One paragraph; no r8 number is carried forward as evidence.
> "A first iteration (the r8 batch and the judged runs of its era: x8, x12 v1, the R2 atlas) was judged on pool p2dca21ab5f4ef3ae while the frozen tree withheld p8a29d8f3ff75aa55. Of that pool's 3,445 judgeable questions, 2,437 (70.7%) lay on the frozen tree's train side, and its anchor rubrics were induced over them. Its split was id-only; its judge and rubric recipe have since been replaced; on re-score its rubric-value claims were withdrawn, and its 22 per-leaf position fits were contaminated by a since-removed correction, while its eight pooled leaderboards reproduce. No result of that iteration is used in this thesis." [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C1): "its anchor rubrics" is "its CELL rubrics": the incident doc says cell-rubric induction (L13, L27); the ladder's anchor and stratum rubrics withheld p2dca]

Sources: incident report L9-L12, with 2,437 chosen; ledger L148 records 2,425 (70.4%) and rounds it to 71%; AUDIT/OPTION-A at ledger L149.

**The r8 boundary includes** (none quoted):
- the R2 LRT;
- H3's +0.39/1k (bias_audit.py reads the x12 v1 DB and R2);
- L1 0.766 → 0.259 (R2);
- the J-floor table (5_Results.tex L700-L725);
- the frozen tree as evidence.

Geometry-only carve-out, stated once: H9-EXT (ledger L73) and D1-D3 (ledger L84-L86) use the frozen recipe for label-free geometry, carry no judged number, and are quoted as geometry only.

**The p2dca judged family needs ONE ruling, not three (H3).** The incident doc (L9-L12) says every judged run "and all re-judge harnesses" used p2dca. Every judged number from those samples carries [P-FAM] until judge-design-specialist and the registrar rule, and then the author words it:
- ARENA-V2 x12 0.852 (FW L79, L263); R3 sample 0.865 (FW L263); PAIR-NOREF +12.6pp (ledger L217);
- judge profile R 0.7183 and filtered 0.5613 (FW L260); key-beats-judge +0.194 / +0.121 (ledger L239);
- CONSENSUS-FIT, x12 MAIN arm (ledger L208); JUDGE-SWAP (ledger L300); JUDGE-BY-CELL (ledger L237); JUDGE-TRANSFER (ledger L289);
- GROK-CALIB b1 (ledger L264), and through it the scale of K46's ν and β (prog L19526-L19530);
- PLACEMENT-STEPS "400 + 100 per separable tier" and NEWCOMER-PLACEMENT-LIVE (ledger L231; FW L189);
- the v1 canary epochs (prog L15882-L15891).

Planned items that depend on this ruling: RP22 (x12 caches), RP48 (v1 board), RP23 (re-price on the GROK-CALIB-scaled ν), RP40.

**My recommendation:** one family bracket, "post-incident recipe on an r8-era, id-disjoint-only question sample drawn on the frozen tree's cells, whose anchor rubrics were induced while 71% of the pool sat on that tree's train side". [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, C2): same defect as L27; SUPERSEDED by the ruling (docs/reviews/RULING_w0_p2dca_family.md, 5effe96), which also DECLINES the carve-out below as an evidence rule and keeps the robustness order only as a ranking of planning priors]
- Within the family, paired contrasts that keep sample and rubric fixed on both arms are the most robust: PAIR-NOREF, JUDGE-SWAP, and JUDGE-BY-CELL's paired M.
- Levels are the least robust: 0.852, 0.865, 0.7183, b1.
- RP04, RP19 and RP21 supply content-closed replacements.

## A5. Title fit

"Query-Adaptive Multidimensional Ranking for Agents in Dynamic Domains" (b_Meta.tex L32; immutable).

- **Query-Adaptive = SQ1 plus SQ3's filing.**
- **Multidimensional Ranking = SQ2:** per-cell key profiles with intervals, and undominated sets U_c.
  - On MMLU-Pro the cells of record are qwen3-filed; RP03 leg M gives the declared-cell form.
  - U_c has never been scored against the key; RP22 would do that.
- **Dynamic Domains = SQ4, carried as scope:** K46's roster exponent, placement, federated arrival, D4 absorption, and the canary, which is the only time instrument. An arriving domain is absorbed, not born. Anchor birth is manual by design rule (FW L191, L266).
- **for Agents = motivation, for a measured reason.**
  - The BFCL pilot's falsifier fired at the point (ledger L224).
  - No registered agent stratum reaches 120 EVAL items. The unregistered python language cell has 234 items, n_eff ~85 (FW L271; ledger L227, L238).
  - The only zero-call routes to a key-level agent sentence are RP17 and RP35. The author decides whether they are worded into the bridge.
- **The bridge sentence stands:** the thesis builds and audits the measurement that query-adaptive ranking for agents would depend on; it claims no router or agent deliverable.

## A6. Thesis claim if the sub-questions land (a † marks an open test, named)

On the rosters and corpora measured:

- **Interaction is real on the key at anchor and declared-stratum grain.**
  - MMLU-Pro: R 0.81-0.87 against nulls of 0.23-0.31. Id-disjoint only; anchors filed by the qwen3 tree.
  - The 52 declared union strata: 0.85. Id-disjoint only.
  - † RP03 leg M gives the content-closed MMLU-Pro reading, with no embedder.
- **Conditioning changed the model to use on one of the two rosters measured.**
  - There is a gain on the 18-model union: +3.09 on declared cells and +2.92 tree-filed, carried mostly by BBH.
  - There is none on MMLU-Pro, where one model is best in all 14 anchors.
  - The two points also differ in scoring protocol.
  - † RP03 leg U converts the union reading's wording to content-closed (a sensitivity).
  - † RP16 adds roster points.
- **The gain lives in the declared cells.** The taxonomy contributes:
  - filing: 81.6% against 72.1% by descent, id-disjoint only († RP12's G13 against flat prototypes);
  - a certificate: 2/70 at per-family FDR on R512, which discriminates where the GMM LR does not († RP06 re-draw qualifier; † RP25 size and power);
  - support;
  - names.
- **Partition, in the licensed words (prog L21218):** "on MMLU-Pro the hierarchy buys the certificate, the support per cell, the names and the routing discipline; its cells are a worse partition than a flat mixture at the same granularity".
  - This is one anchor-free tree, one draw and one corpus. The anchored control ties and is reported only. The mechanism is not identified.
  - † RP05 draws; † RP09 embedder; † RP11 corpus.
  - No routing gain is shown († RP13 label-free).
- **Where only a judge verifies, fidelity tracks the reference:** paired +12.6pp, and 0.852 at board scale [P-FAM]. † RP04 and RP19 give the content-closed v2 reading.
- **The judged cost of a roster step, on a planning scale:** β̂ 1.80 [1.28, 2.32].
  - 2 anchors, k 12 → 37, on the GROK-CALIB scale [P-FAM].
  - "P EXCLUDED", not "M EXCLUDED".
  - Calibration stays UNDETERMINED.

## A7. The skeptic's strongest objection, and the answer

**Objection.** "Your only positive evaluation result is choosing a model per benchmark source. It needs no taxonomy: the declared labels give +3.09 and your tree gives +2.92. It sits on an id-only split, and the case that would make the tree necessary, label-free cells, has never run. Your judge fidelity numbers come from a question sample drawn on the r8 tree's cells, with rubrics induced over it. A recent paper already asks when routing is meaningful. So what does the taxonomy contribute to evaluation, and what here is content-closed?"

**Answer.** The framing concedes the substance and makes the concession falsifiable.

- F-TAX commits the expected sentence: "filing, a certificate, support and names; on MMLU-Pro its cells are a worse partition than a flat mixture at the same granularity (one draw); no routing gain is shown".
- Four tests can overturn it:
  - RP03 makes the USE wording content-closed or withdraws it. Leg M makes the key R embedder-free.
  - RP13 is the label-free test. Its deciding contrast is AF against per-source k-means at matched counts, so a win belongs to the tree, not to any clustering.
  - RP12/G13 tests filing against class-conditional flat prototypes.
  - RP06 and RP24 test the certificate under re-draw and out of sample.
- On the judge, the content-closed objects are the K46 store and G21. RP04 gives the first number at zero calls. Until then every judged figure carries [P-FAM].
- **Against arXiv 2607.09197:** the thesis states only what it adds that the paper, once read, does not already claim.
- The thesis is defended as an audited instrument that says where it refuses, not as a router.

---

# PART B — DIRECTIONS

## B1. The directions that matter most (rank order)

1. **RP01 Record corrections, plus the single p2dca-family ruling (zero cost, now).** The framing currently carries:
   - a false agent sentence;
   - a count paired with the wrong percentage;
   - an ill-defined falsifier (G12);
   - an impossible REG-2 control;
   - wrong pointers;
   - a boundary applied to three numbers instead of the family.
   RP01 folds into INCONSISTENCIES-PASS (q drafted).
2. **RP04 K46-KEY-READ (0 calls, minutes).** The first key-based fidelity number of the v2 recipe on content-closed data, split by reference class ONE / NONE. It decides whether G21, the NONE template and any board are worth their calls before a paid call is spent.
3. **RP03 V2-DECLARED-CELLS, two legs (0 calls, minutes).**
   - Leg U: the USE wording on content-closed union EVAL. A sensitivity, not a replication.
   - Leg M (new, H2): K12/K46 interaction-only R on the 14 declared categories of pv2_41dbd3dbcd399df0 EVAL. This is the only zero-call reading that is content-closed and uses no embedder for SQ2's key clause.
   - Ranked below RP04 because leg U mostly re-words a result already robust to twin removal.
4. **RP05 FLAT-GENERALITY (0 builds, ~1 CPU-h).** Three existing anchor-free re-draws, plus the anchored control against a label-anchored flat arm V_A. Arm (a) is q FLAT-MIX-ANCHORED; MIX-FLAT-SELFTEST-GAPS runs first.
5. **RP06 CERT-REDRAW-R512 + hierarchical FWER (0 calls, minutes).** It qualifies the only two splits the thesis calls certified. Agents have already partly seen the result (§C2 R-E).
6. **RP07-RP09 thread cap → embedder plumbing → nomic arm.** This is the author's embedder question in the only form that decides a thesis clause.
   - Today no construction fits the half-machine cap.
   - Any non-qwen3 tree would be scored silently on qwen3 vectors: all 8,299 nomic snapshot ids resolve in the qwen3 cache (rev row 16b).
   - After both fixes, one build of about 1.5-2 min decides FLAT's embedder qualifier.
7. **RP10-RP11 DATASET-SURVEY → SuperGPQA.** This is the author's dataset question. SuperGPQA is the only external keyed in-genre corpus with a declared 3-level hierarchy (13/72/285), a complete 49-model zero-shot roster and an ODC-BY licence. Stage 0 needs no build and reads the key only.
8. **RP12-RP13 ARCH-V2-E-T lane + UNION-AF-ROUTE.** The content-closed tree the thesis will present, with its four audits, and the only label-free routing test.
   - These carry most of the machine hours and wait for the author's lane order.
   - RP13 also waits for the author's TRAIN-ONLY rebuild-or-disclose decision (q UNION-AF-ROUTE blocker).

## B2. By sub-question

| SQ | Core closers | Strengtheners | Still open after all run |
|---|---|---|---|
| SQ1 | RP03 leg U (sensitivity) | RP16 roster curve; RP18 HELM frontier; RP17 BFCL; RP11 stage 0; RP13 (label-free half) | "only where no model dominates" (never licensed by descriptive curves); the protocol confound unless PROTOCOL-CONFOUND-5 (folded into RP16) runs |
| SQ2 | RP04; RP03 leg M (key R, content-closed, embedder-free); leg U secondary R | RP19 G21; RP20 NONE template; RP21 G17; RP22 U_c LOAO (after the P-FAM ruling) | third judge family (RP55; local candidates); unkeyed transport (S2; FW L191(5)); calibration |
| SQ3 | RP05, RP06, RP12, RP13 | RP24 held-out certificate; RP25 power; RP29 depth; RP30 dip; RP26/27 certificate under embedders; RP53 embedder × filing | hierarchy quality (RP38, extension); T-4 mechanism (RP37) |
| SQ4 | none required ("priced, and UNDETERMINED") | RP21 (time axis); RP23 G22 validity, re-price and G22-REAL-SUPPLY-RERUN | board status word (RP40, author's go); drift under v2 beyond one pass |
| SQ5 | RP05 (draw), RP09 (embedder), RP10-RP11 (corpus) | RP14 LCB power; RP15a/RP15b E0b space-level; RP26/27; RP28 BigCodeBench | breadth across embedder families (RP36); corpus × embedder interaction (RP69) |

## B3. EMBEDDING MODELS

**What the question can and cannot change (H2).**
- **Readouts that use no embedder:** true-label G (+3.09); the 52 declared union strata (R 0.8537); both legs of RP03.
- **Readouts that move with the embedder** (all of them read qwen3-filed cells):
  - +2.92;
  - the MMLU-Pro key R (0.8665 / 0.8118);
  - judge R 0.7183;
  - ROUTER-REGRET-MMLU;
  - JUDGE-BY-CELL;
  - filing, M, the partition (FLAT), the certificate and the label-free test.
- M's interval [−0.61, +0.95] (ledger L182) is the qwen3 tree's sampling uncertainty and does not bound another embedder. A worse filing pulls G toward the pooled-best value. RP53 (folded into RP12's G13) measures this on the union.

**Candidates.** Local facts come from GGUF metadata and Ollama manifests (rev row 18). External facts are cited by URL.

| model | local | dims / ctx | MRL | card protocol | licence | cache coverage (MMLU-Pro) |
|---|---|---|---|---|---|---|
| qwen3-embedding:latest (record) | yes, 7.6B Q4_K_M | 4096 / 40,960 | 32-4096 | instruction +1-5% (not used by the record) | Apache-2.0 ([card](https://huggingface.co/Qwen/Qwen3-Embedding-8B)) | full |
| nomic-embed-text:latest = v1.5 | yes, F16 137M | 768 / 2,048 in Ollama (8,192 on the card) | 768→64, **layer_norm before truncation** | **must** use "clustering: " | Apache-2.0 ([card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)) | 11,769 with the WAL applied (all texts); 11,722 immutable |
| embeddinggemma | yes, BF16 300M | 768 / 2,048 | 768→512/256/128 | "task: clustering \| query: " | Gemma terms ([card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card)) | 8,249; **3,520 missing**; [CORRECTED 2026-09-29 by the data-steward: gemma's missing count under the registered read set (fit 8,125 ∪ held-out 3,445 ∪ keyed; 11,687 texts) is 3,504 (sha256 d47ccf3aa80fbdf6…); the 3,520 was the whole-corpus count (11,769 − 8,249); the 16 difference are un-root-placed TRAIN texts outside E0b's read set (sha256 5c04eadc9114818…); the DB row set is unchanged by the checkpoint (8,249).] queries table 0 rows |
| mxbai-embed-large | yes, F16 334M | 1024 / **512** | yes | none outside retrieval | Apache-2.0 ([card](https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1)) | none |
| snowflake-arctic-embed2, bge-m3 | absent | 1024 | to 256 / none | — | Apache / MIT | none |
| KaLM-12B, nemotron-8b | absent | 3840 / 4096 | yes / no | — | community / non-commercial | none. Dropped: no local runtime (no torch / sentence-transformers). RAM is not the blocker: ≈16 GB (8B) and ≈24 GB (12B) at F16 both fit the ~30 GB cap (unsourced arithmetic, 2 bytes/param). nemotron is also non-commercial. |

**Hazards, located and unfixed** (EMB-01, D02, verifiers; rev row 17):
- The site null hard-codes `embeddings_cache.db` (SeparationNullBySizeTest.kt L604, L818, L1076, L1168, L1221, L1380, L1670).
- The FLAT readers whitelist only that DB.
- The dimension check is vacuous: 4096 and 768 both exceed 256.
- The siteNull Gradle task forwards 7 properties only (build.gradle.kts L184-L223).
- EmbeddingCache.kt L41 routes every `qwen3-embedding*` tag to the DB of record.
- The WAL tails are non-empty: 4,647,392 / 4,643,272 B.
- The nomic manifest lacks `embedding_model`.
- A working guard exists: cos(mean of the site vectors, the snapshot's vmfMu) ≥ 0.99. It reads 1.0000 / 0.9997 / 0.9984 with the right embedder and 0.009 / −0.025 / 0.058 with the wrong one.

**Confounds to register per arm:**
- prefix policy;
- nomic's layer_norm;
- context truncation (mxbai 512; 35 of 11,769 stems exceed 2,000 chars);
- quantisation (only qwen3 is quantised);
- tag drift (pin the digest).
- **Bar:** the iso rule gives 0.025 at 256-d for every arm (ledger L86). An anisotropy-equalised bar would be a new convention, and a second scored bar per arm would be a forking path. Print the centred-cosine anisotropy and do not score it (EMB-03 ruling).
- **Scratch geometry, not of record:** nomic's higher mean cosine is mostly a global offset. Centred PR and top-PC are near-equal, so "concentrated clouds explain 75 vs 87 leaves" is weakly supported.

**Cheapest decisive tests:**
- **Screen with no builds, split in two (M11):**
  - **RP15a (W1 CPU window):** qwen3-256 raw, nomic-256 raw (after the steward's WAL checkpoint) and the TF-IDF→SVD-256 floor.
    - Flat vMF and k-means partitions at k = 14 and 82, on af_clean_s42's 8,125 fit texts.
    - Scored by purity (3,445 held-out) and F6 (10,925 keyed).
    - Cross-space mutual kNN@10 and CKA among these three.
  - **RP15b (W2 machine lane, after RP07 and RP08):**
    - the gemma runner fault fixed, then gemma's 3,520 missing texts; [CORRECTED 2026-09-29 by the data-steward: 3,504 under the registered read set, not 3,520; see the bracket in the embeddinggemma row of the embedder table.]
    - mxbai embedded from scratch;
    - nomic-card and gemma-card re-embeds;
    - the 500-text qwen3 re-embed reproducibility floor.
    These are Ollama embedding runs, so each is one heavy process.
  - Together they decide whether any embedder effect is a space effect before any tree exists.
- **Clause-deciding (one build): RP09 = REG-2 E1-minimal.**
  - A label-free anchor-free nomic build on af_clean_s42's content-closed TRAIN.
  - Timing: anchor-free re-draw builds read 93-106 s total at 24 threads (72-84 s first phase; rev row 27). At 12 threads, roughly double (unsourced).
  - Scored by FLAT against its own V at its own k, and by flatLeaf filing on the same 3,445 held-out questions.
  - The qwen3 draw floor is RP05's three re-draws; no new seed is drawn.
- **Then, conditional:**
  - RP26: nomic certificate on the existing anchored tree. The prediction is re-derived, since nomic's Chemistry dDN is 0.0476, 6th of 14.
  - RP27: trunk certificate per arm, matched by the depth-1 split.
  - RP36: gemma and mxbai, only if RP09 splits.

**Declined:**
- EMB-08: its criterion is unreachable, and filing is folded into RP09.
- EMB-16: needs a local runtime the machine lacks. Replace it with a limits sentence naming the Q4, uninstructed, 256/512-sliced configuration. Never write "the embedder of record was MMTEB #1".
- EMB-14: future-work.
- EMB-13: future-work; it needs the canonical-name cache guard first.
- EMB-17: power binds, not the embedder.

## B4. DATASETS

**Inventory of record** (DS-0 Part A, condensed; each with its split word):

| corpus | status | split word | pointer |
|---|---|---|---|
| MMLU-Pro (12,032) | the SQ2 corpus; nothing to route with a frontier roster | p2dca id-only; v2 pv2_41dbd content-closed | ledger L303, L239 |
| OLL-v2 six-task union (21,606 × 18) | SQ1's only positive; MATH artefact 21.7% | paeec id-only; v2 pv2_1575 content-closed | ledger L182, L202 |
| LCB v6 (1,055 × 26) | STOP at synthetic power | CK-CLOSE-v2 | prog L19732-L19800 |
| 20NG (16,921 docs, no keys) | tree ties k-means | pf844849 (norm-v1) | ledger L226 |
| BFCL multi_turn (8 of 109) | description-only; judged pilot FAILED/UNDETERMINED | family-closed | ledger L224, L238 |
| Multi-SWE (2,132 × 82) | 0/51 strata ≥ 120 EVAL | by-repo, id-keyed | ledger L227 |

**Admission legs** (DS-0 with fixes):
- ≥ 20 complete models;
- ≥ 120 EVAL items per scored stratum (FW L271);
- closable under CK-CLOSE-v1, with a stem_key collision check against every text store;
- a key from an answer key or an executed checker;
- a stated licence;
- SCORING-PROTOCOL, METRIC-GRANULARITY and CoT-extraction columns.

Dominance is a reported column, never an admission leg. Admitting on it would select on SQ1's dependent variable.

| candidate | verified facts | feasibility | cheapest decisive test |
|---|---|---|---|
| **SuperGPQA** (RP11): [dataset](https://huggingface.co/datasets/m-a-p/SuperGPQA), [records](https://huggingface.co/datasets/m-a-p/SuperGPQA-Records) | 26,529 q; 13/72/285; 49 zero-shot models × 26,529 (4.32 GB); 26 five-shot base models; 64 BoN files; ODC-BY; R1 0.6182, top 3 within 1.6pp (rev row 19) | DatasetType is a closed enum (TaxonomyConfig.kt L578-L587): append + fetcher + inertness proof; separate cache; register BEFORE anyone opens the whole-corpus aggregate JSON | Stage 0, key only: G and interaction R on 10 of 13 disciplines ≥ 120 EVAL; MDE80 ~1.4-1.7pp (unsourced derivation) |
| HELM Capabilities v1.15.0 (RP18) | 68 models × 5 scenarios; MMLU-Pro 1,000 (TIGER ids), GPQA 446, IFEval 541; public bucket; data licence unstated (verifier DS-3; URL not verified in this pass, DS-3's source to be quoted) | ~0.3 GB selective fetch; IFEval key fractional (binarise at 1.0); CoT extraction audit owed | Source-grain G on ~586 EVAL items; MDE80 3.6-7.2pp, so UNDETERMINED is likely |
| RouterEval / OLL-v2 roster (RP16): [repo](https://github.com/MilkThink-Lab/RouterEval) | MIT, ungated; MATH responses present (MATH-FIX possible); ~20.5 MB per model for six tasks; up to ~3,285 models before family dedupe | pickles: restricted Unpickler only | REG-1 identity at N = 18, then a descriptive curve |
| BFCL-Result full (RP17): [repo](https://github.com/HuanzhiMao/BFCL-Result) | 109 models; v4 22 categories, 5,106 entries; 5.12 GB; Apache-2.0 | cross-category family closure (memory × 3 backends; web_search × 2); only 3 categories ≥ 120 EVAL | Pooled G, SCOREABLE at ≥ ~4pp; xLAM-2-70b tops all 4 multi_turn categories among 8 (dominance likely) |
| BigCodeBench-perf (RP28): [dataset](https://huggingface.co/datasets/bigcode/bigcodebench-perf) | 1,140 tasks; 153 complete / 126 instruct models; pass/fail matrix; **no licence tag** (rev row 19) | primary-domain rule for multi-label tasks; 97.7 TRAIN per domain is below the 130 floor, so coarsen | G1 on TRAIN; pooled G MDE ~6-7pp (DESCRIPTIVE) |
| EmbedLLM (112), RouterBench (RP46) | Apache / MIT repos (URLs not verified in this pass) | pre-empted by Huot et al. 2026 ([arXiv 2607.09197](https://arxiv.org/abs/2607.09197)), now also cited in A1, A7 and RP16 | positioning only |
| MMLU / HELM MMLU (drop) | 6,810 of 12,032 MMLU-Pro items come from MMLU | not independent | — |
| LiveBench (RP66) | model_judgment: 494 distinct questions, 3 categories | admission unreachable at any budget | — |
| Agent corpora | SWE-bench Multilingual: 46 EVAL issues under by-repo hash; HAL: no licence, 113 GB; OSWorld: 500 GB; TB2/τ2: retest data | support-bound | BFCL key roster (RP17) is the only scoreable one |
| LCB (RP14) | the power of record is synthetic | CPU only | POWER-RESIM |

## B5. Full table (stable IDs; rank order in §B1)

Value is central / sub / presentation, on a 0-5 scale. "cap" = fits the half-machine cap. "after RP07" means only once the thread cap is proved.

| # | item (source ids) | area | tier | value | calls | compute | cap | availability | closed line | depends on | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RP01 | RECORD-CORRECTIONS (AG-14; #6 slice; §A3 items 1-15; leads 158→109; FW L271; the p2dca-family ruling request); folds into INCONSISTENCIES-PASS | record | core | 2/3/1 | 0 | agent-h | yes | now | none | registrar; judge-design ruling | Removes false or mismatched sentences before any prose or registration |
| RP02 | W0 STEWARD PASS (EMB-01e; D05 step 0; K46 census; WAL checkpoints incl. 20NG/ag_news; union join/variant counts; pv2_41dbd per-category EVAL and K12/K46 key coverage) | data | core | 1/3/0 | 0 | minutes | yes | now | none | — | Every reader below refuses on a -wal tail or an unruled split |
| RP03 | V2-DECLARED-CELLS: leg U (ARN-13; #53; framing REG-1) + leg M (H2: K12/K46 R on 14 declared MMLU-Pro categories) | SQ1/SQ2 | core | 4/4/2 | 0 | minutes; 1 rule-7 slot | yes | v2 reader to build | none | RP02; seal ruling; C0 gate | Content-closed wording of USE (a sensitivity) and the only content-closed, embedder-free key R |
| RP04 | K46-KEY-READ (ARN-01; #83; ARN-02 folded; CONSENSUS-FIT stratum) | SQ2 | core | 3/5/1 | 0 | minutes; 1 slot | yes | store sha-pinned | none | RP02 census; arena reuse ruling | First content-closed fidelity number of the v2 recipe |
| RP05 | FLAT-GENERALITY (D03/#18 + V_A; D05 re-draws incl. af_s42_o1; size-floor V); arm (a) = q FLAT-MIX-ANCHORED | SQ3/SQ5 | core | 3/4/4 | 0 | ~1 CPU-h | yes (BLAS 1) | trees exist; FLAT to parameterise | none | MIX-FLAT-SELFTEST-GAPS before re-parameterising; RP02 closure check; RP08(c) | The "one tree" qualifier; REG-2's draw floor with no builds |
| RP06 | CERT-REDRAW-R512 + CERT-HIER-FWER (#41+#25; D15; D11) | SQ3/SQ5 | core (descriptive, post-hoc-seen) | 2/4/5 | 0 | minutes; not a pool reader | yes | nulls exist | none | CERT-RES-SELFTEST-GAPS; tree-spec READY | Re-draw qualifier on the two named certified splits |
| RP07 | THREAD-CAP (D01) | enabler | core | 1/2/1 | 0 | 0.5-1 machine-h proofs | yes | not queued | none | RP31 same-N control, or an exception | No build or null fits the cap today |
| RP08 | EMBEDDER-PLUMBING (EMB-01 a-c; D02; vmfMu guard; -D forwarding) | SQ5 enabler | core (while REG-2 stands) | 2/4/1 | 0 | ~15 min legs | after RP07 | defects located | none | RP02, RP07; GMM-RESIDUE-CLEANUP order | Stops silent qwen3 scoring of other embedders |
| RP09 | REG-2 E1-MINIMAL: nomic arm N (+ card arm) + filing (EMB-06; D08 E1a; EMB-04 printout) | SQ5/SQ3 | core | 3/4/4 | 0 | 1-2 builds (93-106 s each at 24 threads, ~2× at 12, unsourced) + FLAT ~10 min | after RP07 | nomic cached (WAL) | none | RP05, RP08, protocol decision | Decides FLAT's embedder qualifier: the author's question |
| RP10 | DATASET-SURVEY (DS-0 + fixes) | SQ5 | core (enabling) | 3/4/3 | 0 | minutes | yes | now | none | RP02 | Scopes "different dataset", or states a sourced limit |
| RP11 | SUPERGPQA (DS-4; + two-roster; + BoN floor) | SQ1/3/5 | core | 4/4/4 | 0 | stage 0 ~1-2 h; stage 1 1 build + FLAT | stage 1 after RP07 | ODC-BY; public | none (field grain descriptive) | RP10; author scope; DatasetType append | Second in-genre keyed corpus with a declared hierarchy |
| RP12 | ARCH-V2-E-T LANE (D19; #49; G13 = D16; FLAT + certificate on v2; RP53 folded) | SQ3 | core | 4/5/5 | 0 | ~20-28 machine-h at 12 threads (unsourced; re-price) | after RP07 | drafted, unpriced | none | RP07; CK-CLOSE (b); E-T engineering; G12/G15 fixes | The content-closed tree the thesis presents |
| RP13 | UNION-AF-ROUTE (D18; #51; ARN-14 TOST) | SQ1/SQ3 | core | 4/5/5 | 0 | 50-70 min full machine (~1.5-2.5 h at 12 threads) | after RP07 | drafted, script absent | none | the author's TRAIN-ONLY rebuild-or-disclose decision (q blocker); RP03 (D arm); RP12 v2 ingest; per-source K | The only label-free test; F-TAX's lever leg |
| RP14 | LCB-STAGE0-POWER-RESIM (DS-12; #31) | SQ5 | strengthening | 2/3/1 | 0 | 3.3-4.4 CPU-h, 1 core | yes | drafted; harness at tag only | qualifies, never reopens | worktree from tag | Licenses or removes the STOP's power words |
| RP15a | E0b-CPU (EMB-10/11/03; qwen3 raw, nomic raw, TF-IDF floor; kNN/CKA) | SQ5 | strengthening | 2/3/2 | 0 | CPU minutes | yes | nomic cached (WAL) | adjacent (no R at ≤ 14 cells) | RP02 checkpoint; RP08(c) | Is the embedder effect a space effect? No builds |
| RP15b | E0b-EMBED (gemma completion + card; mxbai; nomic card; EMBED-REPRO 500-text floor) | SQ5 | strengthening | 1/3/2 | 0 | Ollama embedding, tens of GPU-min (unsourced) | after RP07/RP08 | gemma −3,520; [CORRECTED 2026-09-29 by the data-steward: 3,504 under the registered read set, not 3,520; see the bracket in the embeddinggemma row of the embedder table.] mxbai none; gemma runner fault | adjacent | RP07, RP08; gemma runner fix | Completes the screen for the other spaces |
| RP16 | ROSTER-DOSE (ARN-15; DS-1; #11; DS-16; PROTOCOL-CONFOUND-5) | SQ1 | strengthening (descriptive curve) | 3/3/1 | 0 | 1-3 CPU-h; ~20 MB/model | yes | RouterEval MIT | none | RP03 first; safe unpickling; positioning against arXiv 2607.09197 | Turns two roster points into a curve on the same items |
| RP17 | BFCL-KEY-ROSTER (DS-7) | SQ1/SQ5/agents | strengthening | 3/4/1 | 0 | 5.12 GB; minutes | yes | Apache-2.0, 109 models | none | GITIGNORE-AGENT, or a DB outside that dir | The only zero-call key-level sentence under "for Agents" |
| RP18 | HELM-CAPABILITIES source-grain G (DS-3) | SQ1 | strengthening | 3/3/1 | 0 | ~0.3 GB; minutes | yes | public; licence unstated | none | RP10; extraction audit | The only multi-source frontier-roster reading |
| RP19 | G21 RE-SCOPED (ARN-08 G21; #70) | SQ2 | strengthening (core if a v2 judged number is quoted) | 3/4/1 | ≤ ~4,050 + ≤ 1,000 reasoning solves (≤ ~14k cce): **the author's cost decision** | light | yes | not registered | adjacent | RP04; adoption (G19 or the K46 fixed recipe); template decision; preflight | Content-closed judged fidelity under v2 |
| RP20 | V2-NONE-TEMPLATE + REF-PAIRED-V2 (#33; ARN-03) | SQ2 | strengthening | 2/3/0 | ~3,520 (+ ~2,400 ONE leg, optional) | light | yes | K46 store | adjacent (single reference open) | RP04; judge-design N1 text | Prices the false "carries a reference" sentence on 69.3% of K46 matches |
| RP21 | G17 v2 CANARY + v1 EPOCH 3 (ARN-06; #61; #99) | SQ4/SQ2 | strengthening | 1/3/0 | 1,224 + ~624 | light | yes | v2 canary to draw | none | CANARY-ANALYZE-FIX; #99 ≥ 2 weeks after 09-24 | The only time instrument; the v2 floor for paired contrasts |
| RP22 | JUDGED-U-SET LOAO (ARN-12) | SQ2/SQ1 | strengthening | 2/3/2 | 0 | ~1 h | yes | x12 caches [P-FAM] | none | the P-FAM ruling; widener-only LOAO; size-matched null | First key validity reading of the judged-cell product |
| RP23 | G22 VALIDITY + REPRICE-K37 (ARN-09) + G22-REAL-SUPPLY-RERUN | SQ4 | strengthening | 2/3/0 | 0 | CPU windows | yes | drafted | none | re-binding; centring readout; the P-FAM ruling (ν scale) | Input to the author's board decision |
| RP24 | CERT-HELDOUT (#27) | SQ3 | strengthening | 2/3/4 | 0 | ~1 d engineering + 1-2 h JVM | after RP07 | new | none | RP07; pipeline-mirroring null | Answers "the certificate certifies its own fit" |
| RP25 | SITE-NULL-POWER-PLANT (D13; #28a) | SQ3 | strengthening | 2/3/4 | 0 | ~1 d engineering + 0.5-6 h JVM | after RP07 | new | none | RP07; J leaf-size check; CERT-ALIGN-SIZE | J's size and power against planted truth |
| RP26 | NOMIC-CERT-EXISTING (EMB-05) | SQ5 | strengthening | 2/4/4 | 0 | ~1 h at 12 threads | after RP07/08 | tree exists | none | prediction registered post-hoc-seen | Strongest R256 region under a second embedder |
| RP27 | CERT-EMBEDDER (D09) | SQ5 | strengthening | 2/4/4 | 0 | ~1 h per arm | after RP09 | blocked | none | depth-1 match rule | The trunk certificate under a second embedder |
| RP28 | BIGCODEBENCH declared domains (DS-11) | SQ1/SQ5 | strengthening | 2/2/1 | 0 | minutes | yes | no licence tag | none | RP10; licence; primary-domain rule | Code with declared cells, complementing LCB |
| RP29 | FLAT-DEPTH-HYBRID (D04) | SQ3 | strengthening | 1/3/3 | 0 | 15-30 CPU-min | yes | inputs exist | none | RP05; DAG membership rule | Locates FLAT's loss in depth; gates RP39 |
| RP30 | DIP-SPLIT (D12; #30b) | SQ3 | strengthening if the power gate passes | 1/2/3 | 0 | minutes | yes | L6 half open | adjacent (LR half closed) | diptest decision; TRAIN-dip bound | Closes or bounds the open dip half |
| RP31 | EVAL-METRIC-DETERMINISM (D22) | enabler | strengthening | 1/1/2 | 0 | 8-11 CPU-min | exception or after RP07 | q state "registered"; build eef090a exists, unreviewed | none | READY with P6 at capped threads | Registered debt; G10 precondition |
| RP32 | PAID-LANE PRECONDITIONS (READY-TEMPLATE-TRANSPORT; STACK-JUDGE-RO-CACHE) | enabler | strengthening | 1/2/0 | 0 | minutes | yes | drafted | none | engine-coder | Before RP19-RP21 |
| RP33 | AGENT-CK-CLOSE (AG-11) | agents | strengthening (gate) | 1/2/0 | 0 | minutes + text download | yes | Multi-SWE key is id-keyed | none | — | Split word for any agent number |
| RP34 | JUDGEBENCH-REASONING-SIDE (ARN-05; #16) | SQ2 | extension (run as registered; paid lane W3) | 1/2/0 | 1,400 (cap 1,540); 350 matches | light | yes | READY a249f77 (delta-2 of 85a2d9f); merged e0735e3 | adjacent | the OPEN `--workers` decision; the a34642c C2 operator check (prints 0, exits 0) on the launch day; a day with no other judged row | Authorised external validity only |
| RP35 | MSWE-LANG-CELLS (+ FACTORIAL) (AG-01/02; DS-8) | agents | extension (register only if TRAIN-priced R is SCOREABLE) | 2/2/1 | 0 | minutes | yes | DB in record | none | pricing; python scaffold aliasing; issue halves | Agent key sentence from data in the record |
| RP36 | EMBEDDER-CROSS-FULL (EMB-07; D08 E1b) | SQ5 | extension (only if RP09 splits) | 2/3/3 | 0 | 4-6 machine-h | after RP08(d) | gemma −3,520, [CORRECTED 2026-09-29 by the data-steward: 3,504 under the registered read set, not 3,520; see the bracket in the embeddinggemma row of the embedder table.] mxbai none | none | pre-embedder cos ≥ 0.9999 | Adjudicates a split RP09 reading |
| RP37 | MATCHED-K J (ARN-20; #52; #4) | SQ3 | extension | 1/3/4 | 0 | minutes + J port | yes | no Python J | none | hierarchical + size-floor comparators | Mechanism probe on the construction's own objective |
| RP38 | HIERARCHY-VS-FLAT-AGGLO (D17) | SQ3 | extension | 1/2/3 | 0 | 10-20 CPU-min | yes | 20NG tree | none | 20NG WAL; same-leaves control; citation fix | The only test of hierarchy, not partition |
| RP39 | ROOT-WIDTH-ARM (D07) | SQ3 | extension | 1/3/3 | 0 | ~1-1.5 h | after RP07 | new code | none | RP29, RP05; after E-T merge | Labels against the width of the first cut |
| RP40 | STAGE-1 CALIBRATION BOARD (ARN-10; #72) | SQ4 | extension | 3/4/1 | 14.5k-19.9k stage 1; ~37.3k full | light | yes | author go | adjacent | RP23; reference policy; P-FAM ruling | The only route to a calibration status word |
| RP41 | KEY-PROJECTED SPACE (EMB-18) | SQ3 | extension | 2/3/3 | 0 | minutes | yes | — | adjacent (k ≤ 14) | union variant beside RP13 | Reference point for label-free cells |
| RP42 | CAPABILITY-INSTRUCTED qwen3 (EMB-12) | SQ3/SQ5 | extension | 2/3/3 | 0 | tens of GPU-min per arm | yes | canonical-name guard first | none | RP08(a) | Space as a design lever (flat, so not a tree win) |
| RP43 | HELM-TRACE-TRANSPORT (DS-13) | SQ2 | extension | 2/3/0 | ≤ 3k + solves | light | yes | after RP18 | adjacent | self-preference stratum (grok on the roster) | Monitor transport to GPQA |
| RP44 | AGENT-TREE-PARTITION (AG-04) | SQ3/agents | extension | 2/2/3 | 0 | 1 build | after RP07 | download | none | after core lane | Agent-task tree figure (F6 computable) |
| RP45 | TP20×EMBEDDER (EMB-15) | SQ5 | extension | 2/2/2 | 0 | 1.5-2 h per arm | after RP07 | — | none | truncation census | Partition clause on a second corpus × embedder |
| RP46 | EXTERNAL-ROUTER-MATRICES (DS-6) | SQ1 | extension | 2/3/0 | 0 | minutes | yes | EmbedLLM Apache | none | winner's-curse note | Related-work positioning (the arXiv 2607.09197 positioning now lives in A1/A7/RP16) |
| RP47 | DEFF per consumer (ARN-19; #56) | enabler | extension | 1/2/0 | 0 | 1.5-3 h | yes | drafted | none | publish ICC and m̄, not DEFF | Support priors; would not have saved BFCL |
| RP48 | JUDGE-CELL-FIDELITY (a) (#38) | SQ2 | extension | 2/2/1 | 0 | minutes | yes | x12 [P-FAM] | none | the P-FAM ruling; mode=ro reader | Attenuation against noise on the v1 board |
| RP49 | FLAT-MIX-RECORD512 (D06) | SQ3 | extension | 1/2/2 | 0 | 15-25 CPU-min | yes | — | none | only if RP05's O loses on M2 | Insurance for bareq512_s42 |
| RP50 | CERT-SEQ-REPS (D10; #48) | SQ3 | extension | 1/2/2 | 0 | 1.5-12 h | after RP07 | proposal | none | RP06 D11 first; B_max 9,999 | Holm words for ≤ 3 splits |
| RP51 | SPLIT-PREDICTION-STRENGTH (D14) | SQ3 | extension | 0/2/2 | 0 | minutes | yes | — | none | n00000004 readout only | Construction footnote |
| RP52 | FLAT-FED-PERCORPUS | SQ3/SQ5 | extension | 1/2/2 | 0 | minutes | yes | id-only trees | none | closure per corpus | Second-corpus FLAT (id-only) |
| RP53 | EMBEDDER × FILING union (EMB-09 arm a) | SQ3/SQ5 | extension (fold into RP12 G13 on v2) | 2/3/2 | 0 | embed ~10k texts | yes | — | none | RP12 | Measures how far a second embedder moves the one union number that reads a tree (+2.92) |
| RP54 | G24 (ARN-08 part; #101) | SQ4 | future | 1/2/0 | ~1,224 | light | yes | no Kotlin v2 path (prog L15172) | none | Kotlin v2 build | Plumbing for an unauthorised board |
| RP55 | CROSS-FAMILY-V2 / third family (ARN-11) | SQ2 | future | 1/2/0 | ~1,660 per judge | light (Azure) or one heavy local process | yes | Azure deployment unknown; locally installed: gpt-oss:latest, qwen3.6:27b, gemma4:31b-it-q4_K_M (Ollama manifests) | adjacent | adopted recipe; family-affinity check against the roster; local throughput unpriced | v1 parity already on record [P-FAM] |
| RP56 | LENGTH-CAUSAL-V2 (ARN-21) | SQ2 | future | 1/2/0 | ~2,184-4,320 | light | yes | — | none in CTX §5 (H3's length sentence is r8-family, not a closed line) | RP20 | Replaces an r8-family sentence only |
| RP57 | REASONING-DEPLOYMENT mint (ARN-04) | SQ2 | future | 1/2/0 | ≤ ~35k cce | light | yes | quota unobserved | adjacent | author go | The premise is not yet shown |
| RP58 | NEW-REF-FAMILY-QUAL (#98) | SQ2 | future | 1/2/0 | ~600 per candidate | light | yes | no candidate | adjacent | gate-(3) replacement | Gate coupled to accuracy |
| RP59 | D4-ROOT (D21; #57) | SQ4 | future | 1/2/3 | 0 | 2-4 h + engine | after RP07 | designed | none | contradicts FW L191; author scope | Birth mechanism, off the arena path |
| RP60 | LCB-A8 + code embedder (D23; #58; EMB-17) | SQ5 | future | 1/2/2 | 0 | ~1-2 h | after RP07 | — | adjacent | RP14 hypothetical-composition leg | Power binds, not recipe |
| RP61 | QWEN3 SIZE/PRECISION LADDER (EMB-13; family-dose) | SQ5 | future | 1/1/1 | 0 | GPU; ~26 GB downloads | yes | not pulled | none | RP08(a) | Within the seed floor (unsourced) |
| RP62 | DIM-LADDER-2 (EMB-14) | SQ5 | future | 1/1/1 | 0 | 8-12 h | after RP07 | — | none | RP08 | Low SQ relevance |
| RP63 | SWEV-DECLARED-CELLS (AG-03) | agents | future | 2/2/0 | 0 | minutes | yes | licence none | none | licence ruling | Nested frontier already published |
| RP64 | agent replay / retest / union (AG-06/07/08/09) | agents | future | 1/1-2/0 | 0 | — | varies | licences, ingests | none | — | Support- or licence-bound |
| RP65 | BFCL-DEGRADED-CONTROL (AG-13) | agents | future | 1/1/0 | 324 | light | yes | deferred | adjacent | DC3 zero-cost check | Changes no sentence |
| RP66 | LIVEBENCH-TEMPORAL (DS-10) | SQ4 | future | 1/2/0 | 0 | — | yes | 494 questions | none | — | Admission unreachable |
| RP67 | AGENT-TRACE-JUDGED-PILOT (DS-14) | agents | future | 1/1/0 | ≤ 3,000 | — | yes | — | adjacent | — | DESCRIPTIVE-ONLY in advance |
| RP68 | UNKEYED-CELL (DS-15) | SQ2 | future | 1/1/0 | 0-2,000 | — | yes | — | adjacent | author scope | Outside S2 |
| RP69 | CORPUS × EMBEDDER 2×2 | SQ5 | future | 2/3/2 | 0 | 4 constructions | after RP07 | — | none | RP09, RP11 | Separates the method from the interaction |
| RP70 | DROP: EMB-08, EMB-16, EMB-09 cross arms, DS-5, DS-9, D20 KSEL, ARN-07 (fold + plan amendment), ARN-16 (**REJECT**: GPQA/MuSR have no generative text; 0 of 21,456 / 13,608 outputs), ARN-17, AG-05, AG-10, AG-12, AG-15, AG-16 | — | drop | — | — | — | — | — | — | — | Unreachable, dominated, confounded, or no sentence moves |

## B6. Tiers and dependencies (waves)

- **W0: now, zero calls, no machine,** under the standing authorisation for cheap zero-call work.
  - RP01, RP02, RP10.
  - Registrations: F-TAX (revised), RP03 (two legs), RP04, RP05, RP06, REG-2 (revised), plus engineering entries for RP07 and RP08.
  - Rulings:
    - arena-specialist: the seal, and K46 reuse for RP03's two legs and RP04;
    - judge-design with the registrar: the single p2dca-family ruling.
  - Engine-coder worktrees:
    - MIX-FLAT-SELFTEST-GAPS first, then the FLAT parameterisation;
    - RP07; RP08;
    - the v2 RP03 reader (legs U and M);
    - the cert_resolution tree spec plus mutants;
    - POWER-RESIM from the tag.
  - (RP34 is no longer in W0. It posts calls and moved to W3.)
- **W1: pool-reader windows.** Serial, never beside a construction, and before any build that rewrites `embeddings_cache.db.queries` (flat_mix_mmlu pins it; otherwise budget a re-pin).
  - Order: RP03 → RP04 → RP05 → RP15a → RP22 (after the P-FAM ruling).
  - CPU lane (not pool readers; paused during constructions): RP14, RP06, RP23, RP16.
- **W2: machine lane.** Only after RP07 is proved and RP08 is merged.
  - Order: RP09 (< 1 h) → RP15b (Ollama embedding, one heavy process) → RP11 stage 0 (Ollama embedding) → optional RP26/RP27 → E-T engineering merge with CK-CLOSE (b) → RP12 → RP13 (after the author's TRAIN-ONLY decision) → RP11 stage 1.
  - The author may reorder RP12 against RP09/RP11.
- **W3: paid LLM lane.** Each test is under 4,000 matches, with one judged test per day.
  - RP32 first.
  - RP34, after the `--workers` decision and the a34642c C2 check on the day.
  - RP21, after the v2 canary is drawn.
  - RP20.
  - RP19, after adoption, the reference decision and the author's cost decision.
- **W4:** reviewer on the numbers, registrar outcomes, research-lead synthesis, science-writer.

**Hard edges:**
- RP05 → RP09 (draw floor).
- MIX-FLAT-SELFTEST-GAPS → RP05.
- RP03 → RP13 (D arm) and → RP16.
- RP04 → RP19, RP20, RP40.
- P-FAM ruling → RP22, RP23, RP40, RP48.
- RP07 → every construction, null and RP15b.
- RP08 → RP09, RP15a (FLAT reader), RP15b, RP26, RP27.
- The author's TRAIN-ONLY decision → RP13.
- RP12's G12 and G15 fixes → before any E-T gate registration.
- RP29 → RP39.
- RP06 (D11) → RP50.

## B7. Author decisions that gate directions

1. **Adopt the framing** with the §A3 corrections and the §A4 widened boundary. Rewriting report/ (RQs, abstract) is the author's alone.
2. **Machine-lane order** (RP09, RP11 stage 1, RP12, RP13, RP36, RP59) and the **JVM thread-cap amendment**: its value and form, and a 24-thread exception for RP31's legs if wanted.
3. **Embedders and protocol:**
   - which arms;
   - raw against card-conformant (my default: nomic raw as primary for continuity, card-conformant as a registered secondary run regardless);
   - fixing the gemma runner;
   - embedding mxbai from scratch;
   - accepting the Gemma licence.
4. **External corpora in scope** (SuperGPQA, BFCL archive, HELM, BigCodeBench, RouterEval/OLL), their licences (bigcodebench-perf untagged; HELM terms unstated; SWE-bench experiments none) and disk.
5. **v2 reference policy:**
   - a mint slice against the NONE template (#33);
   - whether stage 1 carries references;
   - ~35k cce for a full mint;
   - reuse of K46's NONE verdicts.
6. **Which judged instrument SQ2's content-closed claims are stated under** (the central question leaves the slot open): the STACK-v2 v1 prompt or the v2 recipe. Also the words of the single p2dca-family bracket (§A4).
7. **Rebuild-or-disclose.** Which tree the thesis presents: bareq512_s42 disclosed, or the v2 tree. This also gates RP13 (q UNION-AF-ROUTE blocker).
8. **The r8 paragraph:** whether, where, and whether it carries an r8-specific number (census (a)).
9. **Board size, the calibration board go (> 4k), D4 against D1,** and k = 37 against 46 (INGEST-TRACE-KEYS-REPAIR). At k = 46, stage 1 projects nominal ~9.5 against ~6.4 at k = 37.
10. **v1 or v2 as the standing canary alarm.**
11. **"for Agents" wording** of a key-level result (RP17/RP35), and GITIGNORE-AGENT (.gitignore).
12. **The diptest dependency** (GPLv2+) or an in-house dip.
13. **Windows** for CERT-FAMILYWISE-REPS / RP50 / KSEL.
14. **Loop-born anchors** (RP59) against the design rule at FW L191.
15. **Judges:** JudgeBench `--workers`; a Mistral arm; a local third-judge family (gpt-oss, qwen3.6:27b and gemma4 are installed) against an Azure deployment; procuring a new reference candidate.
16. **SUPPORT-PLAN / SUPPORT-FLOOR-CHECKER** adoption.
17. **The word for LEAF-INTERACTION.**
18. **A G19 plan amendment.** G19 is on ARCH-V2's critical path (prog L15082, item (5)), and its design is inverted: on identical payloads a non-TIE is retest noise.
19. **Any override of declared cells** (synthesis decision 5, recorded in item (4) at prog L15080). The default stays.
20. **config/application.yml, .env, .gitignore,** and environment changes (≈26 GB of Ollama pulls, torch) if future items revive.
21. **RP19's cost:** ≤ ~4,050 calls + ≤ 1,000 reasoning solves, ≈ ≤ 14k cce. This follows the JudgeBench precedent, where the posting "AWAITS THE AUTHOR'S SIZE CONFIRMATION … (cce about 5x the earlier estimate)" (q JUDGEBENCH-CJB-SIDE; plan Amendment 24).

## B8. What not to do, and why

**r8 re-reads.** Portfolio #3, #5, #9, #10, #12, #13, #17, #19, #20, #21, #24, #26, #29, #34, #35, #37, #39, #47, #65, #67, #75; #7 beyond census (a); #14 except its code read.
- Do not quote H3 +0.39/1k, the R2 LRT 38.8, L1 0.766→0.259 or the J-floor table.
- Do not use the frozen 07-27 tree as an evidential comparator. Use the geometry-only carve-out, or re-anchor to h9_order o0, o0_clean_s42 or bareq512.
- Do not quote any [P-FAM] number without its bracket.

**Closed lines** (CTX §5):
- rubric text; reference ensembles, gating, confidence, two-reference variants;
- sub-anchor profiles;
- the frontier order;
- escalation;
- single or selective order; temperature 0;
- the LCB judged stage;
- the GMM LR half of L6.

Directions that brush them:
- RP15a/b must not read R at ≤ 14 cells as a partition discriminator.
- RP41 stays at k ≤ 14.
- AG-05 would be a sub-declared-cell profile.
- RP13 publishes aggregate G only, with no per-leaf model rows.

(No "length clause" appears in CTX §5. RP56 is marked accordingly.)

**Structurally unreachable or DESCRIPTIVE-ONLY paid tests:**
- ARN-16: no generations exist.
- G24's 1.9pp bar at 600 matches: it fails under true parity with probability 0.115, and ~0.285 at 276 key-decidable matches.
- G21's 0.849-0.852 band: at the band centre the point lands outside the band 89.4% of the time.
- LEAF-INTERACTION (support floor).
- DS-14, AG-16, DS-9, LiveBench.

**Hazards:**
- no non-qwen3 site null, FLAT read or RP15b embedding before RP08;
- no build before RP07 under the cap, and no construction without a backup first;
- no `new seed` control on a pinned split;
- no E0 on af_s42_o1 against FLAT's held-out set;
- no `qwen3-embedding:*` variant tag through EmbeddingCache before the canonical-name guard;
- no `pickle.load` of RouterEval;
- no reading of the SuperGPQA aggregate JSON before registration;
- no importing `stack_judge.open_cache`;
- no construction beside a pool reader;
- no git write to src/ inside a rule-7 window;
- no re-parameterised flat_mix_mmlu.py before MIX-FLAT-SELFTEST-GAPS.

**Words:**
- never "158 models";
- never "only" for the rosters;
- never "far more often" (an unregistered comparison);
- never "embedder-invariant" for any tree-filed readout, and for declared-cell readouts only as "contains no embedder". Elsewhere, without a registered TOST margin: "not shown worse beyond max(MDE, spread)";
- never "trees, or this construction, are worse partitions in general";
- never "replication" for RP03 leg U;
- never R256 against R512 counts, or "1 of 97 vs 16 of 101";
- never "fixed point" for bareq512_s42;
- never "clean" or "held-out" for id-only splits;
- never "calibrated";
- never "anchors cost certification";
- never "the embedder of record was MMTEB #1" (the record ran Q4, uninstructed, sliced);
- never cite BFCL's struck mechanism sentence;
- never withdraw or confirm PAIR-NOREF on K46's ONE−NONE contrast.

## B9. Rough bill

All figures are unsourced estimates unless a pointer is given.

| block | judge calls | machine / CPU | agent time |
|---|---|---|---|
| Core (RP01-RP13) | 0 | Machine lane ~23-34 h at 12 threads (RP12 20-28 h, scaled from syn's 10-14 h and to be re-priced without the vacuous G15 seeds; RP13 1.5-2.5 h; RP11 ~1-2 h; RP09 < 1 h; RP07 0.5-1 h). Pool readers ~2-3 CPU-h. | ~15-20 agent-days (E-T engineering, CK-CLOSE (b) and the SuperGPQA ingest dominate) |
| Strengthening (RP14-RP33) | ≈ 10.4k: RP19 ≤ ~4,050 + ≤ 1,000 reasoning solves = ≤ ~5,050 (≤ ~14k cce, the author's decision); RP20 ~3,520; RP21 1,224 + ~624. Total 10,418; +2,400 optional (RP20's ONE leg). | Priced components sum to ≈ 8.8-19.1 h: RP14 3.3-4.4 CPU-h (q), RP16 1-3, RP22 ~1, RP24-RP27 ~3-10, RP29 0.25-0.5, RP31 ~0.2. Unpriced: RP15b's embedding and RP23's windows. (Draft 1's "12-26 h" was not the sum; its four named components sum to 7.5-17.6 h.) | ~10-14 agent-days |
| Extension, if chosen | RP34 1,400 (q; READY a249f77; paid lane W3); RP40 14.5k-19.9k stage 1 (**needs the go**) | RP36 4-6 h | — |

**Posting:**
- No test exceeds 4,000 matches: RP19 ≈ 2,000; RP20 ≈ 1,760; RP21 ≈ 612 + 312; RP34 350.
- The day cap is 14,000 calls. With one judged test per day, the strengthening block needs ≥ 4 posting days, and ≥ 5 with RP34.
- **Throughput:** K46 posted serially at 12.76 calls/min (rev row 6).
  - 10,418 calls ≈ 13.6 h; 12,818 with the optional leg ≈ 16.7 h.
  - The probe measured ~210/min once, at night (prog L20478 ff).

**Lanes:**
- Agent lane: parallel worktrees; I merge serially.
- LLM lane: runs concurrently with the CPU lane. A local-judge arm (RP55) would instead be a machine-lane heavy process.
- CPU lane: single-threaded, OMP/OPENBLAS/MKL = 1; pauses during constructions.
- Pool-reader windows: exclusive against constructions (W1-W5 probe, ≥ 12 GB free).
- Machine lane: exclusive, one construction at a time; back up first; JVM ActiveProcessorCount = 12; Ollama num_thread ≤ 12.
- At 12 threads the site-null heap roughly halves and wall time roughly doubles. Formula at build.gradle.kts L190-L196: ~1.7 GB for a 256-d anchor-free null; ~5.7 GB for a 512-d union root null.

---

# PART C — DELEGATION AND REGISTRATION TEXTS

## C1. Delegation plan (each agent's brief)

- **data-steward (W0):**
  - Back up, then checkpoint, the nomic, gemma, 20NG and ag_news -wal tails. Pin per-table hashes of every cache DB in both views.
  - Count the K46 key-decidable matches by class × anchor × v0-correct.
  - Print pv2_41dbd3dbcd399df0 EVAL counts per declared MMLU-Pro category, with the minimum, and K12/K46 key coverage per item (RP03 leg M).
  - Rule on the v2 union variant rule (20,535 items from 21,606 rows; 31 conflicts; 21,606 → 21,384 unexplained).
  - Run the steward-9073a8a-form closure check on the re-draw splits pd610c9a, p19d9f47 and p8a29 (held-out 3,448 / 3,446 / 3,437): stem_key overlap, exact-text overlap, and fit set = post-closure train side. Also run the CK-CLOSE-v1 four conditions.
  - Confirm that o0_clean_s42 is on the p2dca reservedPoolFile split.
  - Verify nomic coverage by key of af_clean_s42's 8,125 + 3,445.
  - Produce the DATASET-SURVEY table with the new columns.
  - Produce the SuperGPQA and BFCL counts. Read nothing from the SuperGPQA aggregate JSON.
- **registrar:**
  - Brackets for §A3 items 1-15, folded into INCONSISTENCIES-PASS where they overlap (FW L271; ledger L148; leads L63; F-TAX; REG-2).
  - The single [P-FAM] family bracket, once ruled.
  - Commit R-A..R-H below, before any code.
  - Correct EVAL-METRIC-DETERMINISM's queue note: the state is "registered", and build eef090a exists unreviewed. Leave ARCH-V2-G22 at RUNNING (prog L16041).
  - Add a queue item for the thread cap.
- **arena-specialist:**
  - Rule that RP03's two EVAL reads and RP04's per-question read do not forfeit stage-1 reuse.
  - Name Mixtral-8x7B-Instruct-v0.1, and Llama-3.1-70B ≡ Meta-Llama-3_1-70B, in the union-to-stage-1 overlap.
  - Re-derive the Support for RP03 and RP04.
  - Re-price stage 1 at k = 37.
- **judge-design-specialist:**
  - The single p2dca-family boundary ruling (§A4 list).
  - N1 text for GENERIC_SYSTEM.
  - The adoption path for G21: G19 or the K46 fixed recipe.
  - The G19 plan-amendment proposal.
  - Whether a local third family (gpt-oss / qwen3.6 / gemma4) is admissible under the recipe.
- **tree-construction-specialist:**
  - V_A definition: per-anchor leaves [11,9,5,6,5,6,3,8,5,6,7,5,5,3], one anchor per text, held-out routed by O's own filing.
  - The DAG-overlap membership rule.
  - RP09 launch lines: pinned `-Dtaxoadapt.llm.embedding-model`, with the digest recorded.
  - G12/G15 re-statement for E-T.
  - The SuperGPQA TOML.
- **engine-coder** (worktrees; inert when the flag is absent; execution discriminators):
  - MIX-FLAT-SELFTEST-GAPS first.
  - RP07.
  - RP08:
    - a fail-closed `-DembeddingCacheFile` forwarded through Gradle;
    - the vmfMu guard;
    - refusal when `embedding_model` is absent;
    - FLAT parameters, with the identity check M1 0.727 [0.712, 0.741] / M2 +12.785;
    - the canonical-name guard.
  - The v2 RP03 reader: leg U with the C0 gate (0.5912 / 0.6220 on paeec), and leg M with the ledger L239 R and null re-pointed to declared categories.
  - The K46 reader through the 86e88d2 unseal path.
  - The cert_resolution tree spec, plus the mutants crB, crK, crL and raG.
  - POWER-RESIM from tag `lcb-stage0-outcome-of-record`.
  - The SuperGPQA DatasetType append and fetcher.
- **adversarial-reviewer:** READY at zero calls on every builder change; recompute every number; a delta READY for each re-parameterised blob.
- **run-operator:**
  - W1 windows, serially.
  - RP07 proof legs.
  - W2 builds and embeddings, one at a time. Before any construction, back up output dirs and the cache DBs, because a build rewrites `embeddings_cache.db` queries and `reserved_pool_meta`, and pin per-table hashes (CTX §4 rule 7; memory note construction-writes-cache-dbs, background).
  - W3 pilots of 12 with a transport preflight inside the dry-run.
- **cost-estimator:**
  - re-price RP12 without the G15 seeds;
  - price RP35's R from TRAIN marginals;
  - price RP19 at δ = 3pp and 5pp;
  - price RP15b's embedding;
  - price a local-judge arm's throughput (RP55).
- **science-writer:** the r8 paragraph and the agent bridge paragraph, from bracketed rows only. Read arXiv 2607.09197 with me before A1's wording is frozen.

## C2. Registration drafts (for the registrar; I commit none of these)

**R-A. F-TAX (revised).**

Expected sentence: "the taxonomy buys filing, a certificate, support and names; on MMLU-Pro its cells are a worse partition than a flat mixture at the same granularity (af_clean_s42, one draw; the anchored control ties, reported only; mechanism not identified); no routing gain is shown."

The partition clause is the licensed sentence of prog L21218, attached to its object. It widens only through the registered reading tables of RP05, RP09 and RP11. It is never generalised to "trees" or "this construction".

- **Moves toward "an evaluation lever" if either holds:**
  - (1) UNION-AF-ROUTE: the two-stage interval of G_AF − G_K,per-source excludes 0 in AF's favour, beyond spread_K. The comparator is k-means within source at AF's per-source leaf counts, with the seed policy registered.
  - (2) G13 on the v2 tree: flatLeaf filing precision exceeds class-conditional k-means at matched per-class prototypes. The paired interval must exclude 0 AND the difference must exceed the comparator's seed spread.
- **Narrows to "a filing device only" if G12 fails on the v2 MMLU-Pro tree.** G12 fails when the hierarchical-BH set at per-family q = 0.05 (300 reps) contains no depth-1 anchor split.
  - Per-site p95 counts are printed beside it, against their binomial null: P(≥ 5 of 70 | 5%) ≈ 0.27.
  - Corpora below the site-null floor read UNDETERMINED-by-support.
  - A top family that cannot reach p ≤ 0.05/m at the rep count reads UNDETERMINED until reps are raised by registration.
- **"Parity"** is written only through a TOST with δ and interval form registered before code. Otherwise: "neither a cost nor parity is shown".

**R-B. V2-DECLARED-CELLS (formerly REG-1; two legs; one rule-7 slot; one declared read budget).**

- **Instrument:**
  - Leg U: ROUTER-CLEAN-POLICY's fit and two-stage bootstrap (B 2,000), through a new v2 reader. C0: reproduce 0.5912 / 0.6220 on paeec through the new path. Clusters = CK-CLOSE components. The label-permutation placebo is carried over.
  - Leg M: the ledger L239 interaction-only R and its logit-additive null, re-pointed to the 14 declared MMLU-Pro categories, for K12 and K46 separately.
- **Hygiene:**
  - Leg U fits on TRAIN 12,358 only; GATE 2,033 is unused. EVAL has 6,153 items in 5,642 components, read once via eval_view after the seal ruling.
  - Leg M reads the key on pv2_41dbd3dbcd399df0 EVAL (3,492 items) only. It uses no tree and reads no embedding.
  - Both legs: assert 0 Meta-Llama-3-70B rows; apply the steward's multi-response variant rule; the budget covers G14's declared half now and M later.
- **Criteria (disjoint):**
  - C1 (U): the CI of G against 0, read HELD / FAILED / UNDETERMINED.
  - C2 (U): the interaction-only R lower bound against the logit-additive null p95.
  - C3 (M): per roster, the R lower bound against its null p95.
- **Printed beside:** G without the 422 residual items; leave-BBH-out; per-source G.
- **Predictions (priors, unsourced):**
  - G in [+1.5, +4.0]pp, centred on the TRUE analogue +3.09. The lower part of this interval lies below the MDE (Support), so it falls in the UNDETERMINED zone.
  - BBH ≥ 50% of G.
  - Leave-BBH-out in [0, +2.5]pp (paeec analogue +1.305, carried by MMLU-Pro and MuSR); it may or may not cover 0.
  - R(U) in [0.78, 0.90].
  - R(M): K12 in [0.80, 0.93], K46 in [0.74, 0.90]. The centres sit at or above the routed id-only values (0.8665 / 0.8118), because misfiling attenuates interaction.
- **Falsifiers:**
  - C1 not HELD → the USE clause is withdrawn as a content-closed claim; +2.92 / +3.09 stay id-only history.
  - C3 FAILED for a roster → the key-R clause stays id-disjoint-only, tree-filed history for that roster.
- **Framing:** a content-closed sensitivity and wording conversion, NOT a replication (same item family, same 18 models; twin removal already +3.28 [+2.12, +4.44], ledger L182).
- **Support:**
  - Leg U:
    - DEFF ≈ 1.71-1.79. This is the conservative product of paeec's 1.31-1.37 (ledger L182) and the EVAL-side component Kish 1.304 (REG_ARCHV2-SPLIT-2 manifest `v2.kish_eval_items`, the reviewer's recompute). The product is an unsourced composition, re-measured on the split before registration.
    - n_eff 3,445-3,603.
    - MDE80 ≈ 1.85pp (paeec SE transported).
    - SCOREABLE for G ≥ ~1.9pp. Leave-BBH-out DESCRIPTIVE-ONLY.
    - Reachable at infinite budget iff G ≠ 0.
  - Leg M:
    - 3,492 / 14 ≈ 249 EVAL items per category on average (arithmetic). The steward prints the minimum; a category below 120 is excluded by name, and R is read on the rest.
    - DEFF from that split's component Kish, measured.
    - SCOREABLE iff every scored category is ≥ 120.
    - Reachable iff the true interaction is non-zero.
- **Cost:** 0 calls; minutes; one rule-7 slot.

**R-C. K46-KEY-READ.**

- **Object:** `pilot_k46_verdicts_run2.db` (sha256 44724d25…), mode=ro&immutable=1.
  - 2,661 usable matches: ONE 818, NONE 1,843.
  - 566 stems: 174 ONE-only, 392 NONE-only.
  - health and math; k = 37; EVAL of pv2_41dbd3dbcd399df0.
  - Joined by variant_id / item_id through the 86e88d2 path. Needs VIEWS-AUDIT-STAGE merged, or a bracket.
- **Readouts:**
  - C1: key-decidable accuracy per class under conventions A and B, with a stem-clustered bootstrap (B 2,000) and the component-clustered one beside.
  - ONE split by v0 key-correct.
  - The difficulty-balance table.
  - The ARENA12 sub-board (264), DESCRIPTIVE, against 0.848 / 0.916 [P-FAM comparators].
  - β_len DESCRIPTIVE; the DISAGREE comparator +0.32/1k only (H3 is r8).
- **Criteria:**
  - C1 for ONE: HELD if the lower bound ≥ 0.80; FAILED if the upper bound < 0.80; else UNDETERMINED.
  - C2 = ONE − NONE: DESCRIPTIVE, between items, planning input only.
- **Predictions (key-informed quantities only; priors):** ONE(A) 0.82-0.90; NONE(A) 0.70-0.80; gap +8 to +15pp (scored descriptively); A below B by roughly the tie share.
- **Falsifier (H4).** C1 FAILED for ONE. This withdraws the planning use of the p2dca-family referenced fidelity (0.852 at board scale) as a figure for the v2 recipe, and RP19 / RP20 / any v2 board are re-priced before any paid call.
  - C2 withdraws nothing. Reference class is fixed per item, so ONE − NONE cannot confirm or withdraw PAIR-NOREF's paired +12.6pp.
- **Support:**
  - Key-decidable n comes from the steward's census, registered before the read.
  - Kish m̄ 5.79 / 5.84.
  - DEFF planning range 1.08-3.6, bracketed by the record's measured values: K46's DEFF of β̂ 1.0785 (prog L19486; a different estimand) and BFCL-JUDGED-PILOT 3.60 (ledger L224). Measured on the store before the read.
  - C1 half-width ~0.03-0.07 across that range (unsourced; n from the census). HELD is reachable only if true ONE ≥ ~0.83-0.87.
  - C2 MDE ~7-12pp: DESCRIPTIVE-ONLY below.
  - The causal reading is unreachable on this store at any budget.

**R-D. FLAT-GENERALITY.**

- **Instrument:** flat_mix_mmlu.py, parameterised (tree, fit set, held-out pool, embedding DB, K, DIM) after MIX-FLAT-SELFTEST-GAPS. The identity check must reproduce first.
- **Arms:**
  - (a) = q FLAT-MIX-ANCHORED: O = o0_clean_s42 against V at k = 84 (seeds 0-4) and V_A. **POST-HOC-SEEN:** O vs V0 at 0.770 / 0.770 and +13.949 / +14.318. M2 decides; M1 is label-advantaged.
  - (b) Re-draws af_s137 (79 leaves), af_s2048 (81) and af_s42_o1 (81, p8a29, order knob disclosed), each on its own held-out set, with V at its own k.
  - (c) A size-floor V (minimum component 55) beside T, DESCRIPTIVE.
- **Criteria:** FLAT C1/C2/L1 verbatim per arm; one deciding loss rule (L1). The seed-wise all-5-CIs rule is a registered secondary.
- **Predictions (unsourced):** L1 fires on M1 in ≥ 2 of 3 re-draws; O ties V_A on M2; V_A ≥ V0.
- **Falsifiers:**
  - 0 of 3 re-draws fire → FLAT narrows to "one draw".
  - V_A beats O on M2 beyond spread → the loss belongs to the construction even when anchored.
- **Reading:** "the loss appears in k of 3 qwen3 re-draws", with k printed.
- **Support:**
  - Per draw: C1 SE ≈ 0.0067, MDE ≈ 0.019, bound by that draw's spread_V (0.0305 on the record).
  - C2 SE 0.357e-3, MDE 1.00e-3 (forward rule, prog L21179).
  - Cross-draw readings DESCRIPTIVE.
  - A loss below max(MDE, spread_V) is unreachable at any budget, so UNDETERMINED is registered.
- **Words:** the re-draws are "id-disjoint only" until the steward's 9073a8a-form check passes on each. Their build logs show the same engine closure as af_clean_s42's 171 moves (164 / 195 / 182), so they are presumed neither weaker nor stronger.

**R-E. CERT-REDRAW-R512 + CERT-HIER-FWER (DESCRIPTIVE; POST-HOC-SEEN).**

- **Inputs:** dimsweep2 s137 (67 sites) and s2048 (71), 300 reps; promoted s42.
- **Instrument:** cert_resolution.py with a new tree spec (new blob; READY; mutants first).
- **Disclosed as already seen by agents** (rev row 14):
  - Engineering passes its own p95 on s137 and s2048 (0.0744 vs 0.0635; 0.0727 vs 0.0629).
  - Chemistry passes on s137 (k = 0) and not on s2048 (0.0444 vs 0.0471, q 0.26), where the split at the anchor is 2-way against 3-way.
  - Law and Business pass per-site on all three draws; History on s42 only.
- **Readouts:**
  - The hierarchical-BH set per re-draw (anchors matched by label; fringe sites by Jaccard ≥ 0.5).
  - D11's weighted top-down FWER, with its weights and denominator fixed before leaf counts are read: "FWER 0.05 against the Gaussian site null, arbitrary dependence across sites".
- **Consequence for the thesis:** the certified exhibits carry a re-draw qualifier.
- **Support:** per-site MC SE 0.0126, MDE80 0.035. A rank-1 top-family rejection needs k = 0 at 300 reps. DESCRIPTIVE-ONLY, because the outcome is largely seen.
- **Words:** R512 only. The re-draws are on their own pre-closure splits (id-disjoint only) and are pre-P7-FIX, like s42.

**R-F. THREAD-CAP (engineering amendment).**

- **Change:** forward `-XX:ActiveProcessorCount=N` to the siteNull and bootRun forked JVMs (build.gradle.kts L184-L222, L259-L295). Print the effective availableProcessors and the heap estimate on every run. The JAVA_TOOL_OPTIONS route also needs `--no-daemon`.
- **Proof:**
  - (b) siteNull at `-PnullReps=24` on af_bareq512_s42 with N = 12 must be byte-identical to the recorded CSV (sha256 aec4b517…a665), with witness `live=12`. First show that the src/main commits since 1e0afab are inert on this path.
  - (a) AG_NEWS build at N = 12 against RP31's same-N replicates. Back up before it runs. Exclude MAIN_taxonomy_quality.csv until RP31 merges.
- **Falsifier:** any byte difference. Capped builds are then a new code path, and every comparison with a pre-cap tree needs a declared-drop comparison.

**R-G. REG-2 revised (EMBEDDER-CROSS-FLAT).**

- **E0 is struck.**
- **E0b** = RP15a (CPU) + RP15b (machine lane).
  - V/K at k = 14 and 82, seeds 0-4, on the 8,125 fit texts, in these spaces:
    - RP15a: qwen3-256 raw; nomic-256 raw; the TF-IDF→SVD-256 floor.
    - RP15b: nomic-256 card (the "clustering: " prefix, layer_norm, then slice and renormalise); gemma-256 raw and card; mxbai-256 raw (truncation count printed); the 500-text qwen3 re-embed floor.
  - Scored by purity (3,445) and F6 (10,925; 71% on the TRAIN side).
  - Geometry printed: centred cosine, PR, mutual kNN@10, CKA.
  - Criterion per arm: FLAT's L1 form against qwen3's spread. The positive side is worded "not shown worse" unless a TOST δ (2.1pp purity; 1.0e-3 F6) is registered.
  - Falsifier: ≥ 2 of 3 families worse beyond spread on F6 at k = 14. It is read after RP15b; RP15a alone reads the nomic family only.
- **E1-minimal (= RP09):**
  - Arm N-raw (primary) and N-card (secondary, via a verified pre-embedder writing a new per-model file).
  - Both built on af_clean_s42.toml, with the embedder set by a pinned `-D` launch line.
  - Witnesses: the opened per-model cache, the vector length, and the vmfMu guard.
  - Readouts: FLAT C1/C2/L1 at its own k; flatLeaf filing on the 3,445 against af_clean_s42 (paired McNemar); root axis, leaf count and ARI printed.
- **Reading table** (k = the number of qwen3 re-draws in which L1 fires, from R-D; printed, never rounded to "three"):

  | k | N-raw | reading |
  |---|---|---|
  | ≥ 2 | fires | "the loss appears in k of 3 qwen3 re-draws and in the one nomic draw, on one corpus" |
  | ≥ 2 | does not fire | "in k of 3 qwen3 re-draws, not in the one nomic draw"; embedder contrast DESCRIPTIVE |
  | ≤ 1 | any | "in k of 3 re-draws"; embedder contrast UNDETERMINED |

- **E2** = RP27 (depth-1 match rule). **E3** = RP36, conditional.
- **Support** as in R-D per arm; the cross-arm contrast is DESCRIPTIVE-ONLY.

**R-H. SUPERGPQA Stage 0.**

- **Sources:** https://huggingface.co/datasets/m-a-p/SuperGPQA and https://huggingface.co/datasets/m-a-p/SuperGPQA-Records.
- **Committed before any agent opens the aggregate results JSON.**
- **Admission legs:**
  - 49 zero-shot models complete (asserted count);
  - key audit: re-extraction agreement ≥ 0.95 per model on a stratified sample, with miss rates printed;
  - a CK-CLOSE-v1 split at 0.30 per field, with stem_key family closure;
  - a zero-collision preflight against every text store, MMLU-Pro included.
  - Any failure → STOP, and the refusal is the outcome.
- **Readouts:**
  - G on the 10 discipline strata with ≥ 120 EVAL items;
  - interaction-only R against the logit-additive null;
  - field grain DESCRIPTIVE (19 of 72 ≥ 120);
  - the two-roster contrast (49 zero-shot against 26 base) DESCRIPTIVE;
  - the BoN resample floor DESCRIPTIVE;
  - a family-collapsed sensitivity.
- **Predictions:** no dominance is assumed (the top three are within 1.6pp); UNDETERMINED is registered as live.
- **Support:** n_EVAL ≈ 7,959 before closure; DEFF 1.0-1.4 (LCB 1.011; union 1.31-1.37; the v2 union's EVAL component Kish 1.304), re-measured; MDE80 ≈ 1.4-1.7pp.
- **Stage 1** (after RP07 and the author's lane decision) is a separate registration:
  - one label-free build in its own cache and worktree, backed up first;
  - FLAT C1/C2/L1;
  - the TOPIC-PARTITION C2 analogue against the declared hierarchy;
  - LCB G1 at matched df (ported from the tag);
  - filing against the declared fields.

---

# PART D — SYNTHESIS (planning; no outcome has landed)

## D1. What the plan lets the framework say, refuse, and open

**What it lets the framework say** (conditional on outcomes):
- The judged half gets its first content-closed number under the v2 recipe, split by reference class (RP04). A FAILED ONE class removes the p2dca-family fidelity figures from v2 planning.
- The USE wording becomes content-closed or is withdrawn (RP03 leg U, a sensitivity).
- The key-R clause gains a reading on MMLU-Pro that is content-closed and uses no embedder (RP03 leg M).
- The partition limitation is stated as "k of 3 draws" (RP05), and, with RP09, with or without an embedder qualifier.
- The certified exhibits carry an honest re-draw qualifier (RP06).
- A second in-genre keyed corpus either replicates the licences or yields a sourced limit (RP10-RP11).
- The content-closed tree carries filing, certificate and M, and the label-free case is finally tested (RP12-RP13).
- One family bracket replaces three ad-hoc ones for every p2dca-sample judged number (RP01 + ruling).

**What it keeps refusing:**
- the frontier order;
- "calibrated" (without RP40 and the go);
- sub-anchor rows;
- preference;
- "only where no model dominates";
- "worse partitions in general";
- embedder invariance for any tree-filed readout;
- any agent deliverable;
- equivalence words without a registered TOST;
- any number of the r8 family;
- any [P-FAM] number without its bracket.

**What it opens next:**
- the corpus × embedder factorial (RP69);
- a third judge family (local candidates now exist);
- the calibration board;
- the dip half of L6, if its power gate passes;
- hierarchy quality (RP38);
- the positioning against arXiv 2607.09197.

## D2. What this plan does NOT show

- **No outcome.** Nothing ran and no recorded number moved. Every prediction is a prior; every estimate without a pointer is unsourced.
- **Nothing becomes content-closed by being planned.** p2dca, paeec, bareq512_s42 and the three anchor-free re-draws stay id-disjoint only.
- **RP03 leg U is not a replication.** It re-splits the same item family with the same roster. A HELD C1 converts wording; it adds no independent evidence of USE on a new population.
- **Post-hoc contamination.** RP06's and RP26's outcomes are partly seen by agents, so their readings are DESCRIPTIVE and cannot be scored as predictions. O vs V0 in RP05 has been seen too.
- **The K46 store answers nothing causal** about the reference, because reference class is fixed per item. RP04 can neither withdraw nor confirm PAIR-NOREF.
- **Embedder scope.** Only declared-cell readouts contain no embedder: true-label G, the 52 union strata and RP03's legs. Every tree-filed number (+2.92, MMLU-Pro key R, judge R, JUDGE-BY-CELL, ROUTER-REGRET-MMLU) can move with the embedder, and no planned core test re-reads them under a second embedder except RP53 (folded into RP12). The embedder results speak for one corpus and one draw per arm, at 256-d, under stated protocol confounds.
- **The p2dca-family ruling changes no number.** It brackets words. It does not make any x12 / R3 / GROK-CALIB figure content-closed.
- **SuperGPQA scope.** It tests transport of licences to one more corpus, not to agents, judges or unkeyed data.
- **Plumbing.** The thread cap and the plumbing are preconditions. Their inertness proofs are not findings.
- **The bill** is dominated by the E-T lane. Its price is the synthesis's own unsourced 10-14 h, scaled, and it includes items still to be re-priced.
- **"Dynamic Domains"** stays scope. Only the canary measures time, and one more pass is not a drift result.
- **The prior-work positioning** is not done. The paper has been verified to exist, but it has not been read for this plan.
- **Queue items** are placed by state and blocker; their prices are the queue's own, marked provisional where so marked.

## D3. Decisions that were the author's

All 21 items in §B7. The first five gate the core:
1. Adopt the framing, with the §A3 corrections and the §A4 widened boundary.
2. Machine-lane order and the thread-cap amendment.
3. Embedder arms and protocol.
4. External corpus scope and licences.
5. The v2 reference policy, together with item 21 (RP19's ≤ ~14k cce).

In every branch these stay the author's: rebuild-or-disclose (which also gates RP13), the r8 paragraph, the judged instrument SQ2 is stated under, the board size, and any go above 4,000 matches.

## Files

- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/CONTEXT.md`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/design/FRAMEWORK.md`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/judge_v2_program.md`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/test_ledger.html`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/queue.json`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/leads/2026-09-18_agent_corpora.md`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/agents/results/evidence/ARCH-V2_SYNTHESIS_2026-09-23.md`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/data_v2/manifests/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2.json`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/multicorpus/router_clean_policy_outcome.txt`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/cert_resolution/cert_resolution_sites.csv`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/dimsweep2/site_null_bareq512_s137.csv`, `site_null_bareq512_s2048.csv`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/tools/analysis/flat_mix_mmlu.py`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/tools/analysis/router_clean_policy.py`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/EmbeddingCache.kt`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/build.gradle.kts`
- `Z:/FAC/TUBerlin/THESIS/TaxoArena/report/01_Document_administration/b_Meta.tex`
- `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/tree_argument_brief_v2.md`

I did not write this to `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/research_plan.md`. My operating instructions forbid writing report or plan .md files and require returning the text instead, so the calling script should save this text to that path.

---

## Changelog (draft 1 → revision 2)

**HIGH findings**
- **H1:** A6 no longer says "only". It reads "one of the two rosters measured … none on MMLU-Pro, where one model is best in all 14 anchors".
- **H2:** Invariance is limited to true-label G, the 52 declared union strata and RP03 (SQ5, B3, D2). MMLU-Pro key R, judge R, ROUTER-REGRET-MMLU and JUDGE-BY-CELL are marked as filed by the qwen3 tree. The M-interval claim is removed. RP03 gains leg M (content-closed, embedder-free K12/K46 R on the declared categories of pv2_41dbd).
- **H3:** One [P-FAM] family ruling, listing every number (§A4). RP22, RP23, RP40 and RP48 depend on it. β's scale is bracketed with prog L19526-L19530.
- **H4:** RP04's falsifier is now "C1 FAILED for ONE withdraws the p2dca-family figures from v2 planning". C2 is planning-only and withdraws nothing.
- **H5:** F-TAX and A6 use the licensed prog L21218 sentence with its object (af_clean_s42, one draw), plus "anchored control ties, reported only; mechanism not identified". "In general" is added to B8's banned words.

**MEDIUM findings**
- **M1:** "far more often" is removed.
- **M2:** β now carries "2 anchors, k 12→37, planning scale, P EXCLUDED, NOT M EXCLUDED" (prog L19459).
- **M3:** 1.89 is refuted. RP03 leg U Support is now DEFF 1.71-1.79, n_eff 3,445-3,603, MDE80 ≈ 1.85pp, SCOREABLE ≥ ~1.9pp; the prediction's low end is flagged as falling below the MDE.
- **M4:** RP03 leg U is called a sensitivity with +3.28 cited; it is re-ranked below RP04 (value 4/4/2).
- **M5:** The bill is ≈ 10.4k (+2.4k optional). The time estimate is re-derived (13.6 h / 16.7 h). RP19's ≤ ~14k cce is a new author decision (B7 item 21), with the JudgeBench precedent quoted from the queue.
- **M6:** RP34 moved from W0 to W3, gated on `--workers` and the a34642c C2 check. Its READY is a249f77, merged e0735e3.
- **M7:** FLAT-MIX-ANCHORED is named as RP05 arm (a). MIX-FLAT-SELFTEST-GAPS is a hard edge. RP01 folds into INCONSISTENCIES-PASS. G22-REAL-SUPPLY-RERUN is added to RP23. RP13 depends on the author's TRAIN-ONLY decision.
- **M8:** URLs are added for SuperGPQA (both datasets), BFCL-Result, RouterEval, bigcodebench-perf and arXiv. HELM, EmbedLLM and RouterBench are marked "URL not verified in this pass".
- **M9:** arXiv 2607.09197 is positioned in A1, A7, RP16 and D1/D2.
- **M10:** The central question's instrument slot is now open.
- **M11:** RP15 is split into RP15a (W1 CPU) and RP15b (W2, after RP07/RP08).
- **M12:** Split words are added to key R, 0.8537, filing and ROUTER-REGRET-MMLU (prog L595).
- **M13:** S2 now cites FW L191 step (5).

**LOW findings**
- **L1:** The FW L263 "correction" is withdrawn.
- **L2:** "Synthesis decision 5, recorded in item (4) at prog L15080" is used in S1 and B7 items 18-19.
- **L3:** The A4 paragraph uses 2,437 and names L148's 2,425.
- **L4:** The carriers are MMLU-Pro +0.65 and MuSR +0.63 (IFEval +0.21).
- **L5:** The leads-doc path is named.
- **L6:** The G22 pointer is now L16009-L16041.
- **L7:** "Nothing scores J against truth" is re-scoped; TOPIC-PARTITION-20NG Q2 is cited (ledger L226).
- **L8:** The R-G table prints k.
- **L9:** The steward runs the 9073a8a-form check on the re-draws; they are presumed neither weaker nor stronger.
- **L10:** KaLM/nemotron: the blocker is the runtime, not RAM.
- **L11:** Local third-judge candidates are verified in the Ollama manifests and added to RP55 and B7 item 15.
- **L12:** Strengthening compute is now ≈ 8.8-19.1 h, shown as a sum.
- **L13:** "Back up before any construction" is added to the run-operator, R-F and R-H.
- **L14:** "No registered agent stratum", with the python cell at 234 / n_eff ~85.
- **L15:** RP04's DEFF is 1.08-3.6, citing prog L19486 and ledger L224; the half-width is re-scaled.
- **L16:** The geometry-only carve-out is applied to H9-EXT and D1-D3.
- **L17:** RP56's "length clause closed" is removed (not in CTX §5).
- **Rev row 27:** build time is 93-106 s total.

**Beyond the review, found while re-reading**
- My draft-1 brief asking the registrar to call ARCH-V2-G22's "running" stale is withdrawn: the record says "stays RUNNING" (prog L16041).
- FW L189 is added as the PLACEMENT-STEPS pointer.
- The v1 canary epochs are marked [P-FAM].

<!-- Committed verbatim by the registrar on 2026-09-27 (Wave-0 record; the author's adoption, plan Amendment 25; programme section "Author's decision 2026-09-27 (recorded by the registrar;  ..."). Source: the orchestrator's scratchpad research_plan_final.md (CRLF; sha256 of the CRLF source bytes 326ca5497d11a0bd); this copy is its LF rendering (verbatim body blob:408a822e / sha256-lf16:6ab7eaec5ea3b2f5, i.e. the file before this comment line and before the brackets). The line-end brackets [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, ...)] and [P-FAM ...] are the registrar's insertions; nothing is rewritten. Line numbers of the source are preserved: this comment is appended at the END. -->
