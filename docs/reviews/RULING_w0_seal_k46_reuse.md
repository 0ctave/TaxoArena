# RULING (2026-09-27, arena-specialist): the v2 EVAL seals and K46 store reuse for RP03 (legs U and M) and RP04

Wave W0 of the adopted framing "Cell-conditional evaluation" (plan 2026-09-27 rev 2, §B6 W0 "Rulings", §C1, §C2 R-B / R-C).

What I did: zero calls. I opened no DB; the four DB files named below were hashed as bytes only. I registered nothing and ran nothing. This is the arena half of the "seal ruling" that R-B's hygiene line waits for. The data-steward's half (the key join, the multi-response variant rule, coverage per item, the census) is separate and is still required.

## 0. Ruling

**R1. None of the three readouts breaks a seal, provided it reads exactly what §2 lists and meets the conditions in §3-§4.**
- Legs U and M read the key (`response.is_correct`) through `open_eval`. They join no verdict.
- RP04 re-reads a verdict × key join that was already unsealed, as registered, by K46's `--analyze` (0bfa148).
- Six seals exist on the v2 EVAL (§1). The only one any W0 readout touches in substance is the stage-1 key join, and only through K46's two anchors. That join is already open.

**R2. K46's store.**
- RP04 may read it: read-only, `mode=ro&immutable=1`, sha-verified before and after, never relaunched.
- RP03 must not read it. No verdict enters either leg.
- None of the three reads forfeits K46's reuse as stage-1 data. Reuse conditions (i)-(iv) of the judge-design ruling (prog L15960, part (3)) and (v) of amendment 0761cfa (prog L16943; outcome L19518) are all about recipe, artefact, anchors and roster identity. No read changes any of them.
- **K46's two anchors (health, math) are, however, KEY-SEEN, and have been since 0bfa148.** Reuse therefore stays conditional on the stage-1 registration carrying S1-S5 (§3). If it does not, K46 keeps only its DESCRIPTIVE-ONLY reading. This is the same form as ruling (3)'s "otherwise".

**R3. Read budget: each leg reads EVAL once** (B1-B4, §1 seal 6). Leg U's frozen TRAIN policy becomes the declared arm of every later EVAL read on pv2_1575de61bb20e977.

**R4. Every readout carries conditions W1-W12 (§4):** split words, [P-FAM] brackets, recipe label, key column, both conventions, clustering, rosters, outputs and operations.

## 1. The seals of record on the v2 EVAL, and whether each is touched

| # | seal | source | what it protects | U | M | RP04 | verdict |
|---|---|---|---|---|---|---|---|
| 1 | VIEW SEAL | `data_v2/views.py` L14-L21, L33-L34. `eval_view_REG.db` sha256-bytes e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369. `gen_view_REG.db` c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec. | EVAL is opened only by `open_eval(stage in judge/arena/route)`, TRAIN/GATE only by `open_generation(stage in construct/label/induce/policy_fit)`; nothing writes | gen `policy_fit` (TRAIN); eval `route` | eval `arena` | eval `arena` | intact if opened as in §2, with the sha pinned and printed before and after |
| 2 | RULE 1 / TRAIN-ONLY | CTX §4 rule 1; synthesis G4 | no EVAL-derived quantity enters construction, labelling, induction, rubric fit, selection or a policy fit | the policy is fitted on TRAIN and frozen before `eval_view` opens | fits no policy; the additive null is internal to the readout | fits nothing | intact under B3, B4 and W11 |
| 3 | STAGE-1 KEY JOIN | budget memo §5 (prog L15115): "KEY JOIN SEALED until the decision is recorded"; K46 HYGIENE (prog L15917) | the key-blind stop must be made without the verdict × key join (no optional stopping on wrong counts) | joins no verdict | joins no verdict | re-reads K46's join, unsealed as registered (see note (a)) | not broken; creates the KEY-SEEN condition (S1-S5) |
| 4 | K46 INSTRUMENT SEAL | 86e88d2 `archv2_pilot/analysis.py` L726-L739 (`unseal_key` refuses before C1) | C1 written key-blind | — | — | — | discharged at 0bfa148: outcome L70 "[C1 WRITTEN] ... before any key material is read", L77 "the key unsealed after C1 was written" |
| 5 | R4 SUPPLY | synthesis Stage S, R1: "R4 must come from EVAL items with no verdict in any cache" | fresh items for G21's confirmation | creates no verdict | creates no verdict | creates no verdict | intact; K46's 566 variants are already outside R4. Condition B4: R4 selection stays key-free |
| 6 | EVAL READ BUDGET | R-B "one declared read budget"; synthesis G14 | no adaptive re-reading of EVAL across policies | one read | one read | (store object; not a budget read) | intact under B1-B4 |

Note (a), what K46's unseal already covers. `unseal_key` read `response.is_correct` (corpus_version mmlu-pro-v2) for every (model, item) cell of the 37 roster models on the store's items. RP04 reads no key cell outside that set. The only key-derived field RP04 adds is `reference.correct` (vintage grok-reasoning-v0) on the ONE variants. That field is about the reference, joins no verdict of a fresh anchor, and falls under S1.

Note (b), the v2 verdict stores. The only verdict store of record that judges roster contestants on v2 EVAL is K46's. The JudgeBench DBs judge external pairs (gpt-4o-2024-05-13 responses). They enter no board, and they are EXCLUDED inputs for construction, labelling, induction, rubric fit, selection or a policy fit (prog L17362 and its D5 bracket). They are not stage-1 objects. RP03 and RP04 do not open them.

Note (c), the reads of record on the v2 EVAL key. Per the `eval_view` openers under `tools/analysis` (grep, §6), the only per-model correctness read of record is K46's `unseal_key`: 566 variants × 37 models, health and math.
- The stage-1 draw and the supply builder read counts only.
- The judge_v2 leak scans load answer strings as scan material and compute no correctness.
- No mc6 `is_correct` on the v2 EVAL has been read by any instrument of record.
- The data-steward confirms this in W0. An unrecorded read would be an incident, not an outcome.

### B1-B4: the read budget (seal 6)
- **B1. One read per leg.** Each leg reads EVAL once: ONE execution of a READY'd, pinned script, with a write-once outcome and refusal of partial runs.
  - A re-run, for example after a bug, needs a registration bracket before it happens, keeps the first read's outputs, and discloses them beside the second.
- **B2. Declare before reading.** Every "printed beside" quantity is declared in the registration before the read (R-B: G without the 422 residual items, leave-BBH-out, per-source G, the placebo). Nothing else is computed from these EVAL keys afterwards without a new registration that names the prior read as POST-HOC-SEEN.
- **B3. Leg U's frozen policy is the declared arm.** Leg U writes its TRAIN policy (the per-stratum argmax table, tie-break of record) write-once and prints its sha BEFORE `eval_view` opens.
  - That file, by sha, is the declared (D) arm of every later EVAL read on pv2_1575de61bb20e977: G14's M half (via RP12) and RP13's D arm. It is reused, never refitted.
  - A later policy's TRAIN-side knobs are fixed without reference to leg U's EVAL numbers, or they are declared POST-HOC-SEEN.
- **B4. No key-derived input to selection.** No per-model, per-category or per-item key quantity from legs U or M, or from RP04, is an input to any anchor, question, roster, schedule or R4/G21/G24 selection. Those selections stay key-free: registered streams, the free answer-disagreement filter, the K8 mask.

## 2. What each readout may read (anything not listed is refused)

| readout | file, opener, stage | rows | columns | never |
|---|---|---|---|---|
| U, fit | `gen_view_REG.db` (c2930c60...), `open_generation("policy_fit")` | TRAIN side only, corpus_version mc6-2026-09-11 named; GATE (2,033 items split-wide) and sentinel rows REFUSED and COUNTED | side/stratum (source, domain), component id; `response_lite` (model, item_id, is_correct, is_correct_mathfix); model_registry ACTIVE | GATE; any mmlu-pro-v2 response; any JudgeBench DB |
| U, score | `eval_view_REG.db` (e35b7518...), `open_eval("route")`, opened only after the B3 policy file exists | EVAL of pool pv2_1575de61bb20e977 (6,153 items / 5,642 components), corpus_version mc6-2026-09-11 named | side/stratum, component id; `response` (model, item_id, is_correct, is_correct_mathfix) | `output_zlib`, `reference`, `gt_raw` / `answer_text` / `pred` (not needed), mmlu-pro-v2 responses |
| M | `eval_view_REG.db`, `open_eval("arena")` | EVAL of pool pv2_41dbd3dbcd399df0 (3,492 items / 3,400 components), corpus_version mmlu-pro-v2 named | side `stratum_domain` (the declared category), component id; `response` (model, item_id, is_correct) for K12 and K37 (W10) | `output_zlib`, `reference`, re-scoring `pred` against `gt_raw`, mc6 responses, any tree or embedding |
| RP04 | K46 store `pilot_k46_verdicts_run2.db` (sha256-bytes 44724d25aa8653b49cef5ea85e99016f4e27f1c99819edc62073416eeec27793; journal 466c0f57...), `mode=ro&immutable=1`, after a no-sidecar check; plus `eval_view_REG.db` via `open_eval("arena")`, as K46's `--analyze` did (outcome.py L201) | the 2,664 scheduled matches on 566 variants (health 161, math 405) and nothing else | store: the schedule and the `match_status` view (match id, variant / response ids, model pair, order verdicts, combined verdict, reference class, response_model); view: `response.is_correct` of the judged responses of the 37 on those items; `reference.correct` for vintage grok-reasoning-v0 on the ONE variants | any `eval_view` row outside the 566; `judge_v2.loader` (stage `judge`: VIEWS-AUDIT-STAGE reserves it); payload rebuild; the retired store `pilot_k46_verdicts.db`; x12 / x20 / grok_calib / R3 / Kotlin caches |

RP04 identity gate. The run REFUSES as a failed precondition unless every value below matches, before any accuracy is computed (all from the outcome file and prog L19459-L19538):
- scheduled matches: 2,664;
- order verdicts: 5,328, with finish_reason stop on 5,328 and response_model grok-4-1-fast-non-reasoning on 5,328;
- usable matches: 2,661 (A 1,039 / B 1,022 / TIE 600);
- INVALID: 3, all reference NONE;
- reference class, scheduled: ONE 818 / NONE 1,846;
- ARENA12: 263 usable of 264 scheduled;
- variants: 566 (health 161 / math 405);
- store sha as above.

## 3. K46 store reuse

**RP04: admitted.** The store is its object. The conditions:
- the §2 row;
- the identity gate;
- the sha re-hashed after the read;
- no write and no relaunch (the merged writer refuses a relaunch in any case: prog L20031);
- the key of a match side is the `is_correct` of the response the judge was shown, joined by the scheduled response or variant, never a (model, item) lookup where the last row wins. A side whose cell has several responses is refused and counted. There were 1,443 such cells in the pool (outcome L16), and the K8 mask lost 0 cells on the board (outcome L17-L18), so the expected count is 0.

**RP03: not admitted.** Neither leg needs a verdict, and a verdict in either leg would be a mixed object.

**Stage-1 reuse: not forfeited, and KEY-SEEN.**

What is already open on health and math (outcome L77-L87):
- at k 37: 1,322 key-informed edges; pooled wrong(all labels) 97 and wrong(established) 27; LOAO-refit nominal 1.9478 with 796 edges called, wrong 3, wrong(established) 0;
- at k 12: 128 edges; wrong(all labels) 7, wrong(established) 0;
- the key-blind nominal of those anchors (C1: nu_2(37) 0.9874).

RP04 adds per-match accuracy by class on the same cells. It does not add the quantity that matters most to a status word; C3 already printed that quantity.

Conditions S1-S5. The stage-1 registration must carry all five, or K46's verdicts are DESCRIPTIVE-ONLY in stage 1:
- **S1. KEY-SEEN clause.** It names health and math as key-seen (C3 at 0bfa148, plus RP04 once it lands, with that outcome's commit). It also names the fresh anchors (chemistry, computer science, economics, other, philosophy) as key-sealed until the stop decision is recorded.
- **S2. A mechanical, key-blind stop.**
  - The following are fixed in the registration before any stage-1 call: margin, frozen pair, N, projection rule and the K46 inclusion rule.
  - The margin is chosen only from G22's operating characteristics at the real supply (G22-REAL-SUPPLY-RERUN, owed), together with the owed overdispersion sensitivity at DEFF 1.78 (prog L16009-L16041, (e) C3).
  - It is never chosen from C3, RP04 or leg M. A stop parameter that reads any key-informed K46 quantity makes the stage-1 READY fail.
- **S3. Two status words, side by side.** The status word is printed on the full stage-1 board and on the fresh anchors only.
  - A word that holds on the full board but not on the fresh anchors carries the words "carried by key-seen anchors (health, math)".
  - The fresh-only word is printed even when it reads UNDETERMINED.
  - Nothing is "calibrated".
- **S4. Key-dependent constants stay those of record.** These are:
  - the 0.017 tier gap;
  - the zero-gap drop;
  - `design.frontier_mask`;
  - established = exact two-sided McNemar p < 0.05 on the anchor's judged questions (`systematic_budget.mcnemar_edge`, integer arithmetic);
  - conventions A and B.
  No new key-dependent knob may enter after leg M's key tiers are seen.
- **S5. No outcome-based subsetting of K46.**
  - Reuse is decided by (i)-(v) as a recipe-identity rule: the whole store (default), or per match by reference class only if stage 1's recipe differs by class and its registration states that rule before posting.
  - K46 is never subset by a key-informed quantity: RP04's accuracies, C3's counts or leg M's tiers.
  - A subsetting rule applied to K46 applies identically to the fresh anchors.
  - Consequence named: if RP04 leads to a changed reference policy or to the NONE template for stage 1, (i) fails for the affected matches, and they fall to DESCRIPTIVE-ONLY. That falls out of the rule; nobody chooses it.

What the reuse is worth (arith., at k 37, the registered 7 anchors, N = 2):
- the full design is 7 × C(37,2) × 2 = 9,324 matches, 18,648 calls;
- K46 covers 2,664 matches (5,328 calls, 28.6%);
- the fresh remainder is 5 × 1,332 = 6,660 matches, 13,320 calls, plus a 24-call pilot. That is above the 4,000-match rule, so it needs the author's go.
- The memo's 600-match AGREE slice is not included.
- Fresh-anchor EVAL items: chemistry 346, computer science 128, economics 250, other 277, philosophy 148. At 1,332 matches per anchor, computer science needs about 10.4 matches per question if every item is used; K46's health figure was 8.30 (Kish). This is unpriced here: DEFF at that reuse is G24's question.

**Union-to-stage-1 overlap (C1 brief), by name.**
- Two models of leg U's 18 (router_clean_policy_outcome.txt L7) are in the stage-1 37:
  - `Llama-3.1-70B-Instruct`, which is `Meta-Llama-3_1-70B-Instruct` [A12], the residue model of record (prog L15119 bracket). The brief's "Meta-Llama-3_1-70B" is the base model, a different entry of the 37; the match is the Instruct.
  - `Mixtral-8x7B-Instruct-v0.1`, which is `Mixtral-8x7B-Instruct-v0.1`.
- These are name matches only, under different protocols (OLL-v2 log-likelihood argmax against TIGER generative CoT). Leg U reads their mc6 key on EVAL items that are also stage-1 items.
- This does not bear on seal 3 (no verdict is joined). It is a disclosure line in leg U's outcome.

## 4. Conditions every readout carries (W1-W12)

- **W1. Split words.**
  - v2 objects: "content-closed under CK-CLOSE-v2 (residual disclosed: 1,142 P pairs in the 15-19-token band covering 422 EVAL items, 1,096 of the pairs BBH; O 20)" (R4 review e2623b4; prog L16193-L16198).
  - Never write a bare "clean", "disjoint" or "held-out" (CTX rule 12). Leg U's fallback is worded "TRAIN cross-fit".
  - Comparators: p2dca / bareq512_s42 "id-disjoint only (bound 2.03pp)"; paeec "id-disjoint only (bound 1.32pp)".
  - Leg M prints how many of the 422 residual items lie in pv2_41dbd3dbcd399df0 (steward's count).
- **W2. Embedder words.**
  - Legs U and M "contain no embedder" (declared cells; no tree or embedding read). Never "embedder-invariant".
  - Comparators: +2.92 "reads cells predicted by the qwen3 union tree"; 0.8665 / 0.8118 "anchors filed by the qwen3 tree bareq512_s42 (24.7% misfiled), on the 2,811 judged questions" (ledger L239, L280).
- **W3. Leg U's word.** "A content-closed sensitivity and wording conversion, NOT a replication": the same item family and the same 18 models (twin removal already reads +3.28 [+2.12, +4.44], ledger L182).
- **W4. [P-FAM].**
  - RP03 prints no judged number. Any judged comparator it prints carries [P-FAM].
  - In RP04, every p2dca-family comparator carries "[P-FAM] (boundary ruling pending, plan §A4)". These are:
    - 0.852 (convention A, 4,507 matches) and 0.865 (a selection maximum);
    - ARENA12 0.848 / 0.916;
    - PAIR-NOREF 0.864 / 0.738 (+12.6pp, 144:25);
    - CONSENSUS-FIT 0.922 / 0.657 / 0.226;
    - DISAGREE +0.32/1k.
  - r8-family numbers (H3 +0.39/1k, the R2 LRT) are not printed.
  - Comparators are printed beside RP04's reading and never pooled with it (mixed-fit guard: different split, prompt and reference state).
- **W5. RP04's recipe label, verbatim.** "the recipe as posted by ARCH-V2-PILOT-K46: system turn d0c524bb... (= STACK-NORUBRIC's norubric system turn), GENERIC_RUBRIC 67f843eb..., E-J user turn, grok-4-1-fast-non-reasoning, dual order with TIE on flip; ONE = the cached grok-reasoning-v0 solve; NONE = no reference, while the system turn states that one exists (K5)".
  - F4's disclosure is printed verbatim.
  - Never "STACK-v2 fidelity". Never "the v2 recipe's fidelity" in general: which judged instrument SQ2 is stated under is the author's (B7 item 6).
- **W6. RP04's population.**
  - "2 of 14 anchors (health, math); 566 judged variants; k 37; N = 2; the filter on; the key-decidable subset; reference class fixed per item (174 ONE-only / 392 NONE-only stems, R-C, to be re-verified by the census)".
  - ONE − NONE is a between-item contrast: DESCRIPTIVE, a planning input only. It never confirms or withdraws PAIR-NOREF.
- **W7. Key column.**
  - RP04 and leg M: `response.is_correct` of mmlu-pro-v2, taken from the judged or scored response (§3). `pred` is never re-scored against `gt_raw`.
  - Leg U: `is_correct` with the MATH-FIX overlay (`is_correct_mathfix` where non-null), as ROUTER-CLEAN-POLICY does (router_clean_policy.py L42, L280-L290). The overlaid cells are counted per side.
- **W8. Conventions and denominators.**
  - RP04 reports conventions A and B.
  - Under A, the denominator keeps every key-decidable INVALID / NON_TERMINATED / CONTENT_FILTER match; the 3 INVALID are counted, never absent.
  - Key-decidable = exactly one side key-correct under W7.
  - Every rate carries its denominator.
  - Every edge count is written wrong(established): exact two-sided McNemar on the anchor's judged questions, with integer arithmetic.
- **W9. Clustering and support.**
  - RP04's C1 decides on the CK-CLOSE component-clustered bootstrap (B ≥ 2,000; condition 4: twins clustered, never dropped), with the stem-clustered bootstrap beside.
  - The measured DEFF, n_eff and MDE are printed beside C1. K46's DEFF of β̂ (1.0785) belongs to a different estimand and is never transported to RP04.
  - Leg U: clusters are components; DEFF is measured on the cache's own cluster sizes against the prior 1.71-1.79, which is an unsourced composition.
  - Leg M: the halving SD and the LOAO jackknife, as in ledger L239.
- **W10. Rosters.**
  - Leg U: the 18 of record, with Meta-Llama-3-70B-Instruct asserted absent.
  - Leg M:
    - K12 = rubric_p8.ARENA12.
    - K37 = the stage-1 roster (sha256-text 3a3204cc35cf600495506e6e1f545ab379707b26c16371df78ce654837846f91).
    - The ledger's K46 (46 models, p2dca) is a different roster, so the comparison is DESCRIPTIVE: roster, split, filing and question set all differ.
    - A 46-model v2 leg is admissible only as DESCRIPTIVE, and only if the steward shows that the 9 BANNED_MODELS carry an `is_correct` computed from a parsed prediction. Six of the nine are text-less (prog L16787 amendment).
- **W11. Outputs.**
  - Outputs are aggregates only: per stratum, category, model or class, and per-replicate records.
  - No per-item EVAL key rows are committed. A per-item intermediate stays in the session scratchpad. If one is committed for audit, it becomes an EXCLUDED input under the L17362 rule.
  - Outcome files are write-once and refuse partial runs. The first line is the pool id.
- **W12. Operations.**
  - Run in a W1 rule-7 window (the W1-W5 probe shows every pool DB FREE; at least 12 GB of RAM free).
  - Single-threaded (OMP / MKL / OPENBLAS = 1), one heavy process, no JVM, never beside a construction.
  - The sha of every opened file is printed before and after.
  - Stage labels are exactly as in §2. No `judge` stage, so VIEWS-AUDIT-STAGE is not a precondition. If a builder needs `judge_v2.loader`, VIEWS-AUDIT-STAGE merges first, or the mislabel is bracketed as INDUCE-RUBRIC-1's was.

## 5. Support facts the registrar can take (record-derived; the census still gates)

**Leg M.** Per-category EVAL items of pv2_41dbd3dbcd399df0, from `experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json` (counts_digest 08bc48d1...; a committed JSON, not a DB):
- biology 189, business 234, chemistry 346, computer science 128, economics 250, engineering 288, health 204, **history 108**, law 289, math 405, other 277, philosophy 148, physics 387, psychology 239; the sum is 3,492.
- Under the 120 floor (FW L271), history is EXCLUDED BY NAME. R is read on 13 categories, and the smallest scored category is computer science at 128.
- This is an item count, not a count of items that also have complete key coverage for the roster. The steward's coverage count per item can only lower it.

**RP04.** The ONE class rests on 174 stems, and fewer of them are key-decidable. Its deciding interval is therefore driven by at most 174 clusters.
- HELD (lower bound ≥ 0.80) is reachable only if the true ONE accuracy is at least about 0.83-0.87 (R-C's own figure, at its half-widths of about 0.03-0.07). That figure is re-derived once the census and the measured DEFF exist.
- The key-decidable n per class × anchor × v0-correct comes from the steward's census and is registered before the read.

**Leg U.** Support is owed to the steward's join census (items with complete mc6 coverage for the 18, sentinels not scored, the 422 residual items counted).

## 6. Commands (reproduce every state claimed here; zero calls, no DB opened)

```
cd /z/FAC/TUBerlin/THESIS/TaxoArena
sha256sum experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db \
  experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db.invocations.db \
  data_v2/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2/eval_view_REG.db \
  data_v2/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2/gen_view_REG.db
#  -> 44724d25...27793 / 466c0f57...0649a / e35b7518...e369 / c2930c60...c0ec (all equal to the record, 2026-09-27)
ls experiment_results/archv2/pilot_k46/ data_v2/REG_ARCHV2-SPLIT-2_*/ | grep -E -- "-wal|-journal|-shm"   # no output (rc 1)
git show 86e88d2:tools/analysis/archv2_pilot/analysis.py | sed -n '726,739p'                            # unseal_key
sed -n '70p;77,87p' experiment_results/archv2/pilot_k46/archv2_pilot_k46_outcome.txt                     # C1 written first; C3
grep -n "GENERATION_STAGES = \|EVAL_STAGES = " tools/analysis/data_v2/views.py                          # L33-L34
grep -rln "open_eval\|eval_view" tools/analysis --include=*.py                                           # the openers (note (c))
python -c "import json;print(json.load(open('experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json'))['counts'])"
sed -n '7p' experiment_results/multicorpus/router_clean_policy_outcome.txt                               # the 18
```

Programme pointers: L15115 (stop), L15917 (K46 hygiene), L15960 (reuse (3)), L16009-L16041 (G22 stop, DEFF 1.78 owed), L16193-L16198 (split, residual), L16787 ff. (the 37; reuse (v) at L16943), L17362 (EXCLUDED inputs), L19459-L19538 (K46 outcome), L20031 (relaunch refused).

## 7. What this ruling does NOT do or show
- It registers, runs and changes nothing. No number of record moves, and the K46 outcome is not revised.
- It does not rule the [P-FAM] family boundary. That belongs to the judge-design-specialist and the registrar; W4 only marks the comparators.
- It does not decide stage 1, the board size, the reference policy, recipe adoption, or which instrument SQ2 is stated under. All are the author's. S1-S5 are the conditions under which K46's reuse survives; they are not a stage-1 design.
- It does not make the K46 recipe "STACK-v2". It does not show that any fidelity figure transfers between recipes, rosters or judges.
- It does not supply the data-steward's half: the join, the multi-response variant rule, coverage, and the census of key-decidable matches.
- It does not show that no unrecorded read of the v2 EVAL key has happened. Note (c) is the record as grepped.
- It does not re-derive leg U's Support, and it does not price stage-1 DEFF at about 10 matches per question.
- It does not cover SuperGPQA (RP11). Its EVAL is a different object; its seal is R-H's (no aggregate JSON before registration). Nothing here transfers to it.
- It does not say "calibrated", order the frontier, or publish any nominal confidence.
