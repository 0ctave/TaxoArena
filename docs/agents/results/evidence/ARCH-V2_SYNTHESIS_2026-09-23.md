# Architecture v2: synthesis of the four stage proposals

research-lead, 2026-09-23. Zero calls. Nothing written to the record.

**Record read at HEAD 897a564:**
- CONTEXT.md.
- FRAMEWORK.md: the one-page summary, Budget, Limits, and Tests 1-26.
- Programme L15005-L15037: TRACE-TRUNCATION's budget, the CK-CLOSE-v1 adoption, and the registrar's rulings, including the temperature wording at L15037.
- multi_corpus_design.md, GEN-ARENA (L565-L605).
- The queue.json states.
- The thesis-title memory.

**Citation and number rules.** Proposals are cited as `tree §x`, `judge §x`, `arena §x` and `data §x`. Every figure comes from a proposal or the record. Arithmetic I did on them is marked **(arith.)**.

**State checks I ran, read-only:**
- The only copy of `kotlin_c0d3f708cbc3930e.db` in the repo is the original. `_backup/` has none, which agrees with data H1.
- 98 `*.db` files in the repo are untracked and not ignored. That count covers the whole repo, `_backup/` included; data §0 counts 83 of them under experiment_results, outside `_backup/`.
- Queue states:
  - CERT-DIRECTION-STREAM is READY and SPLIT-EXPOSURE-SENSITIVITY is built; neither has run.
  - CK-CLOSE-V1-IMPL, LOADER-OPTIONS-KEY, STACK-JUDGE-RO-CACHE, STATUS-WORD-UNIFY and UNION-AF-ROUTE are drafted.
  - TRACE-TRUNCATION and CANARY-EPOCH2-RUNG are registered.

---

## 1. The central question: what the big run is for

**All four proposals agree on one fact.** On every corpus v2 can ingest today, the key or checker ranks the models at zero calls, and it does so better than any judged board:
- ORACLE-BOARD gives rho 1.000 with 0 violations.
- The anchor profile's reliability R is 0.8665 from the key against 0.6728 from the judge.
- The judged-argmax router costs -4.7pp (GEN-ARENA; arena §0).

There is no unkeyed corpus in the record (arena D1). The agentic corpora are description-only: BFCL reads 0.740 A, below the 0.75 bar, and no Multi-SWE stratum reaches the 120-task floor (judge §1; FRAMEWORK Limits).

**The central question the v2 run must answer:**

> *Where the key can grade the judge, how often is an edge that the v2 certificate calls wrong, measured on the deployed v2 schedule with the byte-identical v2 recipe? Is that rate stable across independent draws, and does it reach a calibration status beyond UNDETERMINED?*

Every judged edge the framework could publish where no key exists would then rest on a **measured** error rate of the same instrument, not a transported one. Today it rests on nothing. FRAMEWORK Limits says the shipped judge "has no calibration board, so on day one no ORDERED-JUDGED edge exists". Calibration "is UNDETERMINED on every board in reach", and "no corpus in the programme supplies" the roughly 6,500 keyed edges needed.

### (A) Judge-audit study on keyed corpora

**Gain:**
- A measured wrong(established) rate, with its upper bound (UB), for the v2 recipe on the deployed, filtered schedule, under both conventions.
- A fresh-sample (R4) accuracy for the adopted recipe. This replaces 0.865, which is the maximum over about 15 arms on the reused R3 sample (judge §2.7).
- A certificate chosen by a registered replay and tested for cross-draw stability. This turns b1's re-draw fragility (Δdev 4.47 vs 2.26) into a criterion (arena §2.5).
- At union size, the programme's one chance to earn or refute the word "calibrated".

**Two sizes (arena §5):**
- **A-MMLU:** the filtered 20-model MMLU-Pro board, about 17,400 new matches and about 34,700 calls. It yields about 1,900 called edges at nominal 2.4-3.6, so it stays **UNDETERMINED by arithmetic**.
- **A-union:** the 18-model, 52-stratum board, 7,956 edges x 10 matches, about 79,600 matches and about 159,000 calls. This is **the only size at which nominal ≥ 9 is reachable**, with power 0.79 against a true 2x (arena §2.9).

**Risks:**
- The yield assumes x12's nominal per called edge transfers. That transfer is UNDETERMINED (arena, "does NOT show").
- b1 is not identified under the filter on current data (CERT C3).
- The union board collides with the reuse cap (R11).
- The filter is inert on MATH and IFEval.
- At A-MMLU size, the run may only confirm UNDETERMINED.

### (B) Unkeyed and open-ended corpora, agentic included

**Gain:** rankings where the arena is the only instrument. This is nearest to the title's "Dynamic Domains" and "Agents", but those words are motivation, not deliverable (thesis-title memory).

**Cost:**
- Everything in A comes first. The judge is certified only through a keyed calibration board of the byte-identical recipe (judge §2.7).
- On top of A:
  - acquiring a corpus the record does not have;
  - generating roster responses (unpriced in every proposal, and roster availability is unverified);
  - fresh references at about 5,300 cce per 1,000 matches (judge §5);
  - about 1,530 matches per source-level cell per epoch; 6 cells come to about 9,180 matches and need a go (arena §5).

**Risks:**
- Fidelity on unkeyed cells is **predicted, not measured**. The estimate Â = 0.93·r̂ + 0.34·(1−r̂) is a monitor that never gates (judge §2.7).
- Widener transfer is UNDETERMINED in every direction, so the best class available is BANDED-JUDGED (FRAMEWORK Limits).
- GEN-ARENA showed that judged verdicts do not supply an argmax.
- Agentic judging fails its bar at the point estimate and waits on TRACE-TRUNCATION.

### (C) No big judged run: the content-closed rebuild as the deliverable

**What it does:**
- Rebuilds every keyed claim on a CK-CLOSE-v1 split (data M0-M4; tree §2).
- Runs the structural questions the record never asked:
  - the tree against flat classifiers (tree V5);
  - the discovery arm UNION-AF-ROUTE (tree §2.6).
- Runs only the validation items that are under 4,000 matches.

**Gain:**
- Under rule 12, every keyed board, profile, tier and router claim may for the first time be called "held-out".
- A decisive answer to "is a taxonomy needed for filing?".

**Cost:** about 10-14 machine-hours and zero big calls (tree §5).

**Risk:** the judge chapter stays on one of two weak footings: a recipe whose rubric saw 14 norm-v1 twins, or a new recipe with no calibration board.

### Recommendation: A, built on C; B as a registered follow-on

1. **C is not optional under any option.** The author's priority and rule 12 require the content-closed rebuild before any new claim.
2. **A is the prerequisite for anything B could publish** (judge §2.7). Running B first would buy boards whose certificate has no measured basis.
3. **A is the only option whose deciding quantity is measured against truth.** It attacks the record's standing limit, "certification undetermined at the operating point", with a mechanism the record has not seen: a filtered, same-recipe calibration board large enough to reach nominal ≥ 9. Budget is no longer the constraint, and this is the one limit money can buy out.
4. **A has the smallest contamination surface.** With declared cells and a fixed, non-induced rubric, **no generation artefact touches an arena query at all**:
   - the tree is off the arena path (R5);
   - rubric induction is gone;
   - references are question-level artefacts minted at judgment time (rule 1).
5. **Every outcome is scorable.** Status beyond UNDETERMINED, UNDETERMINED with a measured UB, or an unstable certificate that forces the BANDED-JUDGED fallback: each is a finding.

**The size of A is not chosen here.** Gate G22 (the simulator) sets it before the go is asked. The default target is A-union, if G22 passes at a design that satisfies R11. Otherwise it is A-MMLU, whose honest product is the measured rate with its UB (arena §5).

---

## 2. One end-to-end architecture, with the conflicts reconciled

### Stage D: data (data §1-§4)

- **Corpus DB:** one sealed `corpus_v2.db` per corpus version, with four levels:
  - item (stem_key);
  - variant (a content key with the options sorted);
  - source_row (every upstream row, sentinels included, with the legacy ids kept as aliases);
  - label, plus label_conflict.
- **Responses** carry `seen_ck`.
- **Models:** a `model_registry`, with Llama quarantined.
- **Embeddings** are keyed by (model, dims, normaliser, sha(text)) and carry no category.
- **Verdict caches:** one append-only verdict DB per run, sealed at close.
- **Reads and provenance:** `ro.py` is the only connect point. Each run has a manifest; there is also a `data_manifest.json` and an `objects_of_record.json`.

### Stage S: the split (data §2; tree §2.1)

The split uses CK-CLOSE-v1 with all four conditions. It is computed once, at ingestion, over union-find components (stem, family, GPQA subset copies), and it is never recomputed.

The separation is physical:
- `gen_view.db` holds TRAIN and GATE, plus a salted EVAL hash set.
- `eval_view.db` and `emb_eval.db` hold the EVAL side.
- `open_generation` and `open_eval` each refuse by stage.

**R1. Tier a vs tier b.** tree §2.1 wants fresh tier-b pools and rejects keeping p2dca and paeec. data M2 wants tier a, seeded by p2dca (sentinels included) and paeec.
- **The conflict is only apparent.**
  - What tree rejected was the pinned lists with *routing-only* closure, which leaves the 37/70 and 471 twins inside.
  - Tier a closes globally at ingestion, so the twins leave the generation side.
  - Tier a also mints **new pool ids** (a hash of the component list), which meets tree's second reason: ending the p8a29 ambiguity.
- **Adopt tier a for the existing corpora, and tier b for any new corpus.**
- **One cost remains.** R4 (judge §2.7) must come from EVAL items with no verdict in any cache. The data-steward counts that supply. The x12/x20 complement alone is 3,445 − 2,811 = 634 questions **(arith.)**, which may not carry judge V6's roughly 1,000 matches without reuse.

**R2. Where the split is computed.** data computes it at ingestion; tree computes it in Kotlin `finishSplit` (CK-CLOSE-V1-IMPL (b)).
- **Ingestion is the source of truth.** Kotlin recomputes the split as an **assert** that must agree item for item (G2).
- The engine opens `gen_view` only.
- So (b) widens to three parts:
  - the Kotlin closure;
  - a gen_view adapter;
  - moving the `queries` / `reserved_pool_meta` writes into the build's own directory (data §3; tree F11).

**R3. LOADER-OPTIONS-KEY.** tree F16 says it lands before ingest. data §1 retires every text and options-key join.
- **Fold it into M1**, as the crossing that V1 verifies.
- Patch the retiring engine loader only if the legacy path must still serve bridge readouts.

**R4. One pointer file.** tree's `trees_of_record.json` and data's `objects_of_record.json` merge into a single `objects_of_record.json`. It carries tree §2.7's stamp fields plus build_manifest_sha and the gen_view sha.

### Stage T: the tree (tree §1-§2)

The tree is a filing instrument with a per-node certificate:
- **Build:** label-free, anchored, federated per corpus, grafted under a union root, routed flatLeaf.
- **Gate:** the z-gate at 2.0, with the isotropic bar as a prefilter only (0.0145 at 512).
- **Certificate:** the site null, published as a **view** and never used for admission.
- **Parameters:** the slice/bar pair per corpus, chosen by a D-sweep; mcs 55; testRatio 0.30.
- **Seeds:** seed 42 is the object of record, plus 3 variance seeds.
- **Provenance:** stamped **in the snapshot**.

**R5. Stratification.** tree §1 stratifies on declared cells, while arena and judge write "cell" without defining it.
- **The arena's cell is the declared anchor (source, domain) wherever the corpus declares one.**
- Under A, **the tree stratifies no board.** Its products are:
  - filing precision (V3);
  - the certificate (V4);
  - the tree-vs-flat null (V5);
  - the policy on declared vs filed cells (V6);
  - filing of metadata-free arrivals, under B only, published beside the ROUTING-ATTENUATION slope (0.795 at 19%).
- **The tree is therefore off the big run's critical path.**

### Stage J: the judge (judge §2)

- **Judge and reference:** grok-4-1-fast-non-reasoning, with one question-level reference and verify-first.
- **Rubric:** a **fixed, hand-written rubric per corpus type, with nothing induced**.
- **Order:** dual order, with a TIE on a flip.
- **Parameters:** temperature omitted and recorded as "omitted" (ruled at L15037); cap 8192.
- **Schedule:** the answer-disagreement filter at D_c ≥ 0.95; one judge per board.
- **Safety and provenance:** the full-payload leakage scan, full per-call provenance, and compressed bodies stored.

**R6. Vote vocabulary.** judge §2.3 uses {FIRST, SECOND, TIE, INVALID, NON_TERMINATED, CONTENT_FILTER}. data §3 uses {LEFT, RIGHT, TIE, INVALID} plus flags.
- **Resolution:** use judge's six-class enum inside data's verdict table.
- This way NON_TERMINATED and CONTENT_FILTER can never collapse into TIE.

**R7. Verdict identity: a defect in data §3 as written.** data §3 sets `verdict_id = sha256(payload_body)`, so the same body posted twice collides. That happens in three places:
- the canary's second pass;
- the second calibration draw that arena §2.5's stability criterion requires;
- a same-session control arm.

**Resolution:** key the verdict by (run_id, match_id, order, draw_index), and keep payload_sha256 as a column.

**R8. Schema of record.** judge §2.3 adopts the Kotlin `judge_calls` table; data §3 specifies one DB per run.
- **Resolution:** data's schema is the target, and Kotlin writes to it.
- arena §2.3's golden test guards the pair: the Kotlin board must equal `board_from` edge for edge.

**R9. Reference key.** judge §2.1 keys references by stem_key. data H4/M4 key them by the judged row's variant, because row content varies by model for 173-205 questions.
- **Resolution:** key by variant_id and cluster by component.
- judge failure 12's assert extends to the variant.

**R10. Rubric vs reuse.** arena §5 prices the MMLU-Pro board with the x12 pairs "reused from GROK-CALIB filtered at 0 calls". But judge §5 says GROK-CALIB is reusable **only** if the anchor rubric is kept, and that rubric was induced on corpora holding 14 twins.
- Under the author's priority the generic rubric wins.
- **Consequences:** GROK-CALIB is not reusable, the calibration board is wholly new, and the canary must be re-floored.
- **Disclosed cost** (STACK-NORUBRIC): A 0.850 vs 0.864 (−1.5pp, p 0.044); B 0.927 vs 0.929.

### Stage A: the arena (arena §2)

- **Schedule:** fixed before any verdict, from free data only. The unit is (cell, question), with a reuse cap r ≤ 4.
- **Filter:** the filter defines the edge estimand. A random AGREE audit runs at a registered π and is fitted separately.
- **Fit:** per-cell Bradley-Terry with a Jeffreys 0.5 prior and no pooling. The Python fit is the fit of record.
- **Intervals:** question-clustered bootstrap, with B ≥ 2,000 for any 0.975 tail. DEFF, n_eff and MDE are printed.
- **Calls near the threshold:** c~ is averaged over multiple bootstrap streams, with an MC-UNRESOLVED class.
- **Certificate:** the refitted widener or the binned gate, chosen by the replay, plus two ORDERED conjuncts (length-robust and per-order-robust).
- **Key order and frontier:** Holm on the key partial order; the frontier is BANDED by rule.

**R11. Reuse cap vs union board.**
- 6,482 questions over 52 strata is about 125 per stratum. 1,530 matches per stratum is then about 12 uses per question **(arith.)**.
- That is three times r ≤ 4, at a DEFF of about 2.0 (arena §2.1 table).
- G22 must show that identification and the wrong(established) count survive this reuse, or else cut the matches per pair.
- No proposal prices this.

**R12. Board size.** The proposals give three figures:
- judge §2.7: about 9,000 matches / 20,000 cce (the unfiltered GROK-CALIB shape);
- arena A-MMLU: about 34,700 calls;
- arena A-union: about 159,000 calls.

**G22 sets the size.**

**R13. Checker strata.** The filter is inert on MATH and IFEval (FRAMEWORK Limits).
- In the union board those strata run on a different schedule and are **fitted separately** (mixed-fit guard 12).
- The registration states whether they enter the union certificate.

### Stage P: boards

- **Keyed cells:** key-built board, Holm partial order, tiers at the 0.017 gap, anchor profiles, both conventions. 0 calls.
- **The audit board:** judge accuracy under A and B; wrong(established) with its UB by agreement bin; the status word from `status_word()` after STATUS-WORD-UNIFY.
- **Unkeyed cells (B only):** BANDED-JUDGED.
- **The router:** a key-based U_c on declared cells.

---

## 3. Build order and critical path

Work runs in four lanes (CONTEXT §7; queue.md):
- **LLM:** judged runs, which read the pool.
- **Machine:** constructions, site nulls and CPU windows.
- **CPU:** readouts.
- **Agent:** engineering in worktrees.

Rule 7 constrains how they overlap:
- The machine lane never overlaps any pool reader. That includes judged runs (L15005: "pool readers, rule 7 applies").
- One construction runs at a time.
- Agent work runs in parallel freely.

**P0. Data safety, now (§8).** Zero calls. Owners: data-steward and run-operator. Nothing starts before M0.

**P1. The two pinned long runs, already queued.** CERT-DIRECTION-STREAM (≥ 3.5 h) and SPLIT-EXPOSURE-SENSITIVITY (3.5 h) run back to back.
- They pin `pool_guard.py` and `stack_judge.py`.
- **Every v2 change to a pinned blob waits for them.** That includes CK-CLOSE-V1-IMPL (b) and STACK-JUDGE-RO-CACHE.

**P2. Engineering, in parallel worktrees.** Each item goes engine-coder → adversarial-reviewer READY → my merge after MERGEABLE → full suite → Block-2 dry-runs.
- **E-D, the data layer.**
  - Contents: M1-M3, `ro.py` plus the lint, the append-only verdict schema with R6 and R7, and the manifests.
  - Python only; it can run during P1.
- **E-J, the judge writer v2.**
  - Contents: the positional frame, the extended combiner, provenance, body storage, and the full-payload scan.
  - It can run during P1 where it touches no pinned blob.
- **E-A, the arena.**
  - Contents: the simulator, the v2 replay, Holm, STATUS-WORD-UNIFY, the binned gate, multi-stream c~, and the Kotlin golden parity test.
- **E-T, the tree.** It starts **after P1**.
  - Contents: the snapshot stamp, CK-CLOSE-V1-IMPL (b) widened per R2, and TrainOnlyGuard generalised to every generation artefact.
  - It needs a declared-change proof on a recorded build, with an execution witness (rule 11).

**P3. Zero-call gates.** G1-G9, G16, G22 and G23. These are CPU readouts on sealed copies, run outside construction windows.

**P4. Machine lane: the tree.**
- Contents: the D-sweeps, the builds of record, the site nulls, the V7 seeds, and UNION-AF-ROUTE if it is in scope.
- Cost: about 10-14 machine-hours, serial (tree §5).
- **It is off the critical path of A.** It competes only for rule-7 windows, so it runs as one block before the LLM lane opens.

**P5. Paid validation, each item under 4,000 matches.** Every item follows the same flow: registration, dry-run, READY, 12-match pilot, run, post-run review, outcome.
- The sequence: G17 canary re-floor, then G19 position floor, then recipe adoption on R3, then G21 R4 confirmation, then G24 pilots.
- G18 (TRACE-TRUNCATION, already registered) runs whenever it is scheduled. It gates only B's agentic cells.

**P6. The author's go, on G22's size, then the calibration board.**
- The schedule is fixed before the first verdict.
- Epochs serve only as guard checkpoints (truncation, errors). They are never looks at c~ (arena §2.1).

**The critical path for A:**

P0 → E-D (M1-M3 fix the pool ids) → E-J ∥ E-A → G1-G9, G16, G22, G23 → G17, G19 → adoption → G21 → G24 → go → board.

E-T, P4 and CK-CLOSE-V1-IMPL (b) sit on the router chapter's path and on B's path, **not** on A's.

---

## 4. Validation gates, merged and deduplicated

All gates cost zero calls unless a cost is shown. **No spend above the pilots until every gate on A's path passes.** The tree-only gates (G10-G15) block the router chapter, not the calibration board.

| # | gate (sources merged) | falsifier | cost |
|---|---|---|---|
| G1 | Ingestion bijection: mmlu_pro 12,000, union 21,606 and eval 560,379 rows each map 1:1; items 11,609 / 20,535; GPQA 546 (data V1) | a row unmapped or mapped twice; any count differs | 0 |
| G2 | Closure, computed in both languages: EVAL ∩ gen keys = 0 (sentinels included, global); families crossing sides = 0; cluster ids present; positive control: p2dca reproduces 37/70 (data V2 + tree V0) | any count > 0, or the two languages disagree on one item | 0 |
| G3 | Guard is not vacuous: the generalised guard reports 37/70, 26 and 28 on 212117, and 0 EVAL members on the v2 snapshots (data V3 + tree V1) | it reports 0 on 212117, or > 0 on v2 | 0 |
| G4 | Loader denial, both branches executed (data V4) | construct opens eval_view, or route is refused | 0 |
| G5 | Append-only store; the relaunch anti-join posts nothing when complete (data V5) | a mutation succeeds, or a cached row is re-posted | 0 |
| G6 | Body, frame and scan: the 1,974 R3 payloads are sha-equal to `payload_body` and to the Kotlin path; the frame selftest passes on six fixtures; E-RAW re-parses 100% of rows; the full-payload scan has 0 hits (judge V0 + data V6) | any mismatch or any hit | 0 |
| G7 | Legacy reproduction: import counts 9,142 / 12,394 / 9,142 / 9,123; the board of record re-fits to the digit; the replay identity leg gives 150/190 with 0 wrong and 1,713-1,720 per anchor, with an execution witness (data V7 + arena 2a) | any digit differs | 0 |
| G8 | No writes: the analysis suite on sealed files leaves sha and mtime unchanged; the test-isolation canary survives; per-table shas before and after each build (data V8-V9 + tree V8) | any change other than the build's own outputs | 0 |
| G9 | Manifest complete; the lint is clean; the Llama quarantine holds (data V10-V12) | a DB with no off-disk copy; a direct `connect`; a leaked quarantined row; a mismatch count other than 7,424 | 0 |
| G10 | Tree stamp and determinism: the snapshot stamp equals the TOML, the manifest and the pointer file; two rebuilds are byte-identical; the starved-pass accept count is printed (tree V1-V2) | any byte difference | 2 builds |
| G11 | Filing: flatLeaf source+domain precision, clustered; flatLeaf vs descent; the attenuation slope (tree V3) | < 75%, or flatLeaf not above descent | minutes |
| G12 | Certificate: a site null at 300 reps per corpus, after the D-sweep (tree V4) | MMLU-Pro certifies < 5 sites, or a root is uncertified; either fires the 256 / 0.025 arm | ~1.5-2 h + sweep | [CORRECTED 2026-09-27 by INCONSISTENCIES-PASS (RP01, A5): the falsifier cannot be scored as written: (i) "root uncertified" can never fire on an anchored tree (cert_resolution_sites.csv: bareq512_s42, frozen and o0_clean_s42 have 0 depth-0 sites; only the anchor-free af_clean_s42 has one); (ii) "< 5 sites" names no counting rule (bareq512_s42 reads 10/70 per-site p95, which would not fire, and 2/70 hierarchical BH, which would). Proposed re-statement (plan R-A, to be REGISTERED in F-TAX, not in force by this bracket): G12 fails iff the hierarchical-BH set at per-family q = 0.05 (300 reps) contains no depth-1 anchor split; per-site p95 counts printed beside, against Binomial(m, 0.05) (P(>= 5 of 70) = 0.272); corpora below the site-null floor read UNDETERMINED-by-support; a top family that cannot reach p <= 0.05/m at the rep count reads UNDETERMINED (at 300 reps the smallest p is 1/301 = 0.00332 against 0.05/14 = 0.00357, so only k = 0 rejects)]
| G13 | Is the tree needed: flatLeaf vs nearest centroid, kNN-15, and k-means at matched k (tree V5) | none: both outcomes are publishable, and a tie changes the text to "mixture-of-centroids classifier" | minutes |
| G14 | Policy consequence: the gain, and M (the accuracy change when the cell is read from the tree instead of the declared label), on the v2 split (tree V6) | the gain's CI covers 0 | minutes |
| G15 | Variance floor over 3 seeds; anchor-level drift ≤ 0.6pp (tree V7) | registered readout | ~3-4 h |
| G16 | Judge replays: the filter on `grok_calib.db`; STACK-NORUBRIC under both conventions; the monitor Â against realised accuracy (judge V1) | readouts that inform decision 3 | 0 |
| G22 | Simulator. Validity leg: reproduces 733/7 on 891 edges, the LOAO counts, and a Δdev range covering 2.26 and 4.47. Then: the identification rate at the planned size and at R11's reuse; whether any allocation rule inflates wrong(established) (arena §4.1) | the validity leg fails (the simulator then decides nothing), or identification < 0.8 (the size is wrong) | 0 |
| G23 | Replay: certificate A vs B (LOAO, utility, cross-draw stability); the two conjuncts; the two-judge residue check; Holm (arena §4.2 b-e) | wrong(established) rises, or utility falls below 60% of ALL edges | 0 |
| G17 | Canary re-floor under the v2 prompt, 300 x 2 x 2 (judge V2) | floor ≥ 0.138 | 1,224 calls |
| G18 | TRACE-TRUNCATION, as registered (judge V3) | its registered C1 / C2 | ≤ 2,184 calls |
| G19 | Position floor on content-identical pairs, 300 hard + 300 easy (judge V4) | SCOREABLE at ≥ 9pp, otherwise DESCRIPTIVE | ~1,200 calls |
| G20 | Pointwise vs pairwise on R4, optional (judge V5) | MDE ~4.6pp per decision; board rho is DESCRIPTIVE-ONLY | ~3,900 calls |
| G21 | R4 confirmation of the adopted recipe against the 0.849-0.852 band, both conventions (judge V6) | outside the band | ~2,000 calls |
| G24 | Pilots: 12 matches, then 600 keyed MMLU-Pro matches on the v2 production path; parity, realised π, DEFF (arena §4.3) | DEFF > 1.6, or parity broken | ~1,224 calls (arith.: 600 x 2 + 24) |

**Merged, not dropped:**
- tree V0 into G2;
- data V3 and tree V1 into G3;
- tree V8 and data V8-V9 into G8;
- arena 2a and data V7 into G7;
- judge V0 and data V6 into G6.

**Support.** G21 still needs its Support section before registration, and its R4 supply is the R1 caveat.

---

## 5. Total cost

### Calls

| line | calls | rule | source |
|---|---|---|---|
| Keyed boards, all corpora | 0 | none | arena §5 |
| Validation on A's path: G17 + G19 + G21 + G24 | ~5,648 **(arith.)** | each under the rule | judge §4, arena §4 |
| + G18, registered and authorised | ≤ 2,184 | under | L15005 |
| + G20, optional | ~3,900 | under | judge §4 |
| **All validation** | **~11,732 (arith.)** | each under | |
| Calibration board, A-MMLU | ~34,700 **plus** the x12 share, no longer reusable under R10 (≤ ~20,000 if run unfiltered, judge §2.7; the filtered share is unpriced) | **needs a go** (4.3x the rule) | arena §5 |
| Calibration board, A-union | ~159,000 | **needs a go** (20x the rule) | arena §5 |
| Second draw, for the stability criterion | up to 1x the board again (a full replicate is the ceiling; G22 sizes a subset) | **needs a go** | arena §2.5; ceiling (arith.) |
| B, if chosen later | the A board + ~9,180 matches per 6-cell epoch + fresh references (~5,300 cce per 1,000 matches) + response generation (unpriced) | **needs a go** | arena §5, judge §5 |

### Machine time

- **Tree lane:** about 10-14 h (tree §5).
- **The P1 long runs:** at least 7 h (queue).
- **Data migration M0-M4:** unpriced. The cost-estimator prices it before registration.
- **CPU gates:** minutes each.

### LLM wall time, extrapolated

The two registered throughputs are 2,184 calls in about 86 min and 1,200 in 30-40 min, which gives about 25-40 calls/min. At that rate **(arith.)**:
- A-MMLU takes about 14-23 h;
- A-union takes about 66-106 h.

Both figures are before any provider throttling.

### What needs the author's go

- each calibration board;
- the second draw;
- B's per-epoch cells.

Everything in P5 is under the rule, item by item. Plan Amendment 12's acceptance covers only CANARY-EPOCH2-RUNG and TRACE-TRUNCATION.

---

## 6. What the thesis can claim under A, and what it cannot

### Can claim, once the gate or outcome lands

- **Keyed products on a content-closed split.** Every keyed board, key partial order (Holm), tier map, anchor profile and router gain rests on a split that passes a CK-CLOSE-v1 content-key check. For the first time, rule 12 licenses the word "held-out".
- **Whether a taxonomy is needed for filing (G13), either way.** Also the filing precision and the per-node certificate of a label-free, anchored, federated tree.
- **The v2 recipe's own measurements:**
  - its fresh-sample key-decidable accuracy under both conventions (G21);
  - its test-retest floor under its own prompt (G17);
  - its position floor on content-identical pairs (G19);
  - a measured wrong(established) rate of the certificate on the deployed filtered schedule, with its UB by agreement bin and its cross-draw stability.
- **At A-union size, and only if G22 validates it:** the calibration status by the power rule, possibly beyond UNDETERMINED. This would be a first for the programme.
- **Clean by construction:** an arena whose queries no generation artefact has touched, shown by construction (R5, R10) rather than by audit.

### Cannot claim

- the frontier order;
- sub-anchor rows;
- any preference;
- a nominal confidence outside the fitted roster, judge or schedule (a union certificate does not transfer to the 20-model MMLU-Pro roster, to Mistral, or to unkeyed corpora);
- any ranking on an unkeyed cell;
- agents, beyond motivation;
- discovery, unless UNION-AF-ROUTE runs and beats k-means at matched k, against the record's prior;
- closure against paraphrases below norm-v1;
- that the rebuild validates the objects of record (those stay disclosed, under their own decision).

---

## 7. Author decisions, deduplicated, most consequential first

1. **What the big run is for: A, B or C** (arena D1).
   - *Default:* A built on C, with B as a follow-on registration.
   - Everything below depends on this.
2. **Calibration board size, and the go** (arena D2; judge 8).
   - The choice: A-MMLU (about 34,700 calls plus the x12 share) or A-union (about 159,000), plus the second-draw size.
   - *Default:* decide after G22. Choose A-union if G22 passes at a design that satisfies R11; otherwise A-MMLU.
   - This decides whether "calibrated" can ever be earned.
3. **Rubric** (judge 1; data D8).
   - *Default:* fixed generic text, nothing induced.
   - The alternatives:
     - keep the frozen anchor rubric and disclose its 14 twins (this keeps GROK-CALIB);
     - re-induce from gen_view (the expected gain is at most 1.5pp, so DESCRIPTIVE-ONLY).
   - This decides whether GROK-CALIB can be reused, whether the canary is re-floored, and whether the recipe carries any contamination.
4. **Split seeding** (data D1; tree D2).
   - *Default:* tier a, seeded by p2dca plus paeec, with global and family closure and new pool ids. The alternative is a fresh tier b.
   - This decides the reuse of references, verdicts and R3, whether the bridge to the old boards stays comparable, and the R4 supply.
5. **Stratify on declared cells** (tree D1).
   - *Default:* declared.
   - This takes the tree off the board path and removes the 19-25% attenuation.
6. **Rebuild or disclose the objects of record** (tree D7; arena D7; data D2).
   - This decision is already open, and SPLIT-EXPOSURE-SENSITIVITY informs it.
   - *Default under v2:* disclose. The old objects become historical, and no new claim depends on them.
7. **Agentic cells** (judge 6).
   - *Default:* checker-only / DESCRIPTIVE until TRACE-TRUNCATION reads.
8. **Filter as the default schedule, and π** (arena D3).
   - *Default:* yes, conditional on the filtered calibration board.
   - π is set in the registration; arena gives 0.10 as an example.
9. **Certificate adoption and the two ORDERED conjuncts** (arena D6, D4).
   - *Default:* the author approves the registered criterion and G23 picks the certificate.
   - Adopt both conjuncts.
10. **References after the rebuild** (judge 5).
    - *Default:* reuse v0 by variant as a legacy vintage, and mint v1 only for new EVAL items.
    - The alternative is a full re-mint at about 34k cce.
    - Vintages are never pooled.
11. **Format and ties** (judge 2, 3).
    - *Default:* pairwise dual order, TIE on a flip.
    - Fund G20 (pointwise vs pairwise) only if B is in scope.
12. **Tree recipe** (tree D3, D4, D6).
    - *Default:* a per-corpus D-sweep, K-selection hysteresis off, and no leaf names.
13. **Discovery arm UNION-AF-ROUTE in scope** (tree D5).
    - *Default:* yes. It costs 0 calls and about 1 h, and it is the only route to a claim beyond filing.
14. **Data details** (data D3-D7 and D9; judge 7).
    - MinHash census: report only.
    - Variant ordering: take it from the modal eval row, with responses carrying `seen_ck`.
    - Llama: quarantined and excluded from boards.
    - 20NG v2: cluster its duplicates, never drop them (CK-CLOSE condition 4).
    - Store full compressed bodies.
    - Move ag_news out.
    - **The off-disk backup target and the .gitignore / .gitattributes scope are author-owned files.**
15. **Rule 7 under sealed views.**
    - *Default:* no relaxation until G8 has held across several builds.
    - Any relaxation is the author's to grant.

The temperature wording (judge 4) is no longer open: it was ruled at programme L15037.

---

## 8. Data-safety actions to take now, whatever the option

These actions come from data §0 H1-H4 and M0, plus my two state checks. They belong to the data-steward and the run-operator, and all cost zero calls.

1. **M0: back up off the repo disk.**
   - Copy these to a disk other than the repo's:
     - the 17 gitignored DBs: the record's 11, grok-reasoning-cot, the three refqual_Kimi files, pointwise_grok and pointwise_grok_noref;
     - the 83 untracked, non-ignored DBs;
     - the 4 root caches.
   - `_backup/` does not count: it is inside the repo and untracked itself (H3).
   - Write data_manifest v0 with sha256-bytes and per-table shas.
2. **The Kotlin board.** CONTEXT L28 calls it "backed up", but I found no copy beyond the original in the repo.
   - Back it up first.
   - The registrar inserts an "unverified until M0" bracket.
3. **No `git clean` of any form** in the shared checkout until M0 is done and the author has scoped .gitignore (H2). The 83 untracked DBs include `grok_calib.db` and `checker_answers_v1.db`.
4. **The four WAL-bearing DBs:** 20NG (708,672 B), `ag_news_smoke_cache_v1.db`, and the two 09-08 embedding caches (about 4.6 MB each).
   - Back up each `-wal` together with its file.
   - Never read them with `immutable=1`, which hides the WAL tail.
   - The steward checkpoints them with a read-write open and close, under rule 7.
5. **`stack_judge.open_cache()` opens its cache read-write**, and its fix waits for the pinned long runs. Until then, back up `stack_v2_promptv2_x12all.db` and pin its per-table sha before and after any run that imports `stack_judge`.
6. **Before any construction**, including CK-CLOSE-V1-IMPL (b)'s proof build:
   - back up the embeddings and dataset DBs;
   - pin per-table shas in both views.
   - Builds rewrite `queries` and `reserved_pool_meta` (tree F11).
7. **Register `objects_of_record.json`.** Name 212117 as the tree of record and 043557 as its replica. This costs zero calls and ends the ambiguity before any v2 build writes a 208th snapshot.

---

## What this synthesis does NOT show

- **Nothing was measured.** Every figure is quoted from a proposal or the record, or is marked as arithmetic on them. The two state checks are file listings, not audits.
- **A-union's feasibility.** Its yield assumes that nominal per edge transfers, which is UNDETERMINED. Its reuse, about 12 per question on an average stratum, collides with r ≤ 4. G22 may cut it.
- **That the generic rubric is the right trade.** It costs a measured 1.5pp on A and forces a wholly new calibration board. The priority argument is the author's, not a measurement.
- **The R4 supply under tier a.** The 634 figure is only the x12/x20 complement.
- **A frontier order, and any transfer.** Nothing here makes the frontier orderable, and no v2 certificate transfers to another roster, judge or corpus.
- **Some costs.** Data-migration hours and LLM wall times are unpriced or extrapolated. B's response-generation cost appears in no proposal.
- **The R7 defect.** It is my reading of data §3's text, and the data-steward should confirm it before E-D is built.
- **That a v2 tree beats a flat classifier, or that declared-cell stratification changes any board.** Both are predictions.
