# Review: CONTENT-DISJOINT-SPLIT-AUDIT readout (data steward), 2026-09-23

Reviewer: adversarial-reviewer. Zero judge calls, read-only. I did not import the steward's `core.py`. Every number below comes from my own scripts in
`scratchpad/content_split_review/`: `ro2.py`, `keys2.py`, `a_paeec.py`, `b_mmlu.py`, `b2_pairs.py`, `c_link2.py`, `c_evalside.py`, `d_closure.py`, `d2_closure.py`, `d3_paeec.py`, `d4.py`, `d5.py`, `e_1020.py`, `f_20ng.py`, `g_agent.py`, `h_members.py` and `h2.py`.
The repo modules imported are the function of record `tools/analysis/split_side.py` (stem_key and side_hash only; I also wrote my own normaliser, and it agrees with `split_side.norm` on 21,606 / 21,606 union texts), `pool_guard.compute_pool_id` / `judgeable`, and, for the 20NG rebuild only, `tools/ingest/twenty_newsgroups_ingest`.

Discipline:
- Every DB was opened `mode=ro&immutable=1` after a size check on its `-wal`. The WALs of multicorpus_cache_v1.db and snapshots.db are 0 B. mmlu_pro_dataset_cache_v2.db, bfcl_result and multiswe_result have no WAL.
- twenty_newsgroups_cache_v1.db was not opened. Its WAL is 708,672 B, dated 09-23 04:30. Its size and mtime were unchanged before and after the rebuild.
- snapshots_frozen.db was never opened.
- DB sizes and mtimes were identical at the start and the end of the review.
- Rule 7: the only JVMs running were an idle Gradle daemon (PID 49416, started 11:35) and a Kotlin compile daemon. There was no test worker, no construction, no site null and no tools/analysis python.

## Per-claim table

| # | claim (steward) | mine | verdict | command |
|---|---|---|---|---|
| 1 | paeec RES<->GEN exact 471 ids / 427 keys; norm-v1 478 / 432; stem+optset 358 / 322; GEN with a RES twin 538 / 543 / 416; norm-v1 by source GPQA 288, MMLU-Pro 185, MATH 3, BBH 2; within-RES dups 213 / 215 / 147 | 471/427, 478/432, 358/322; 538/543/416; GPQA 288, MMLU_PRO 185, MATH 3, BBH 2; 213/215/147 | CONFIRMED to the digit; matches 21c4fda D2 (L48: 471 / 478 / 427 / 543) | `a_paeec.py` |
| 2 | p2dca RES with a GEN twin: exact 37 / norm-v1 70 / optset 33; every GEN partner is an unlinked sentinel; equals A1's member counts for bareq512_s42 | 37 / 70 / 33; partners 42 / 75 / 33, all sentinels (linked 0). Members of 20260910_043557 are EXACTLY the 8,278 distinct GEN texts (sha256[:16] ids), so 37 / 70 EVAL texts among members is an identity, confirmed on the tree itself. Other pools: p8a29 44/86/41, pd610 35/70/35, p19d9 51/81/29, p7f7ce 0/1/1, all equal to the steward's (norm-v1 partners in p8a29 and p19d9 include 1 and 2 linked rows) | CONFIRMED as keyed. The option-set figure is keyed on the WRONG OBJECT: see D1 (64, not 33, on the question actually judged) | `b_mmlu.py`, `h_members.py`, `c_evalside.py` |
| 3 | closure moves 171 GEN rows -> test 3,770 / train 8,230 = af_clean_s42 | 171 / 3,770 / 8,230 (gate 843, train-excl-gate 7,387); the engine log line "[SPLIT-SIDE] 8230 train (843 gate) / 3770 test" occurs 12 times, and `experiment_results/anchorfree/redraw/af_clean_s42.build.out` carries "[SPLIT-CLOSURE] 171" | CONFIRMED | `d_closure.py`, grep of the build logs |
| 3b | "+92" (SPLIT-FUNCTION-IMPL: p2dca 3,537 with closure, gate 860, train 7,603) | NOT REPRODUCED under any of the 20 readings (4 readings x 5 MMLU-Pro pools). The nearest is 3,552 / 859 / 7,589 (+107). See "Resolution of +92" | UNRESOLVED; no reading of today's data yields it | `d_closure.py`, `d2_closure.py`, `d4.py`, `d5.py` |
| 4 | 1,020 CLEAN include 12 exact / 23 norm-v1 twins on the frozen tree's GEN side | 1,020 + 2,425 = 3,445 reproduced (p2dca judgeable intersected with the p8a29 list). Twins 12 / 23, partners all sentinels. The frozen tree's members (8,299) are exactly the distinct texts of the universe minus the p8a29 list; p2dca judgeable ids with the exact text among members = 2,437 = 2,425 + 12 (norm-v1 2,448 = 2,425 + 23). This reconciles the incident's own 2,437 with its 1,020 / 2,425 | CONFIRMED; on the judged eval row, optset 22 and full ordered duplicates 11 | `e_1020.py`, `h2.py` |
| 5 | GPQA: 382 pairs, same option set and answer, 367 shuffled; an ordered key misses 367 / 382 | 382 pairs: 367 shuffled + 15 same order, all with the same option set and the same answer text | CONFIRMED. The same holds on MMLU-Pro alone: all 33 optset twins on p2dca are shuffled (ordered key: 0) | `a_paeec.py`, `b2_pairs.py` |
| 6 | paeec MMLU-Pro: 68 true duplicates (agreement 0.999), 127 stem-only variants | 68 same-optset pairs, cell agreement 0.9992, identical 0.985; 127 stem-only pairs, agreement 0.7533, identical 0.134; random RES-GEN null 0.5342 (18 models, Meta-Llama-3-70B-Instruct absent, 0 rows in this DB) | CONFIRMED. Note that the stem-only variants carry an intermediate agreement: they are NOT independent questions | `a_paeec.py` |
| 7 | 20NG, BFCL, Multi-SWE: 0 cross-side twins | 20NG 0 / 0 (exact / norm-v1) on 16,921 rebuilt rows (cache sha and rows sha equal the manifest; the pool file hashes to pf844849e133cda4e). BFCL 0 on stem, norm, content_key, dialogue_key and family; 0 of 200 index families split. Multi-SWE 0, but content_key = stem_key(instance_id) on 2,132 / 2,132 | PARTLY: the counts are right; the 20NG zero holds by construction and the Multi-SWE zero is vacuous (D4, D5) | `f_20ng.py`, `g_agent.py` |
| 8 | 54 of 3,445 p2dca ids link to an mmlu_pro row whose option set or answer differs; 17 with a different answer text | 54 with the gpt-4o-2024-08-06 eval row as reference; answer text differs on **19** (17 where the option set also differs, plus 2 where the option set is equal but the key letter differs). With the modal eval row over 46 models (Meta-Llama-3-70B-Instruct excluded): 63 / 27. On 51 of the 54, the eval row's ORDERED options match an UNLINKED mmlu_pro row exactly | PARTLY (17 is the answer-and-option-set-both-differ cell, not all answer differences; the reference row is unnamed) | `c_link2.py` |
| 9 | GPQA Kish 1.380 on paeec; BFCL family Kish 4.00 | GPQA sum(n^2)/n = 1.3799 (358 ids / 295 clusters). BFCL family 4.000 (228 / 57). Not stated by the steward: BFCL stem-key clusters give 3.377 (81 clusters) and Multi-SWE repo families give **37.76** (390 ids / 16 repos) | CONFIRMED. The label is wrong: this is DEFF at rho = 1, an upper bound, not a DEFF (D7) | `a_paeec.py`, `g_agent.py` |
| 10 | claims table: records whose "clean split" rests on an id-only check | The steward's table is not in the scratch directory; I spot-checked 5 rows myself (below) | UNDETERMINED for the steward's table; my spot-checks below | grep / build logs |

### Claim 10 spot-checks (5 rows)

1. **CONTEXT.md L30, "promoted bareq512_s42 (87 leaves, clean split)".** Snapshot 20260910_043557 was built 09-10 04:36 (experiment_results/hygiene/build.out), from the reserved FILE, before 13f2142 (09-16). The SPLIT-CLOSURE and SPLIT-SIDE lines occur 0 times in build.out and headless_run.log (`grep -c`). **ID-ONLY.** 37 / 70 EVAL texts are among its members (h_members.py).
2. **FRAMEWORK L180, "+3.38pp ... on the clean reserved side"** (union tree 20260911_144214, paeec). **ID-ONLY**: 471 / 478 EVAL ids have a TRAIN twin. The 2026-09-23 bracket replaces the number (+2.92pp) and carries the A1 bound, but the words "clean reserved side" stand unbracketed.
3. **Programme L6401 / ANCHOR-FREE-REDRAW R1 af_clean_s42, "the first anchor-free tree on the clean split".** Its build.out carries "[SPLIT-CLOSURE] 171 train item" and snapshot 20260917_201353. It is **CONTENT-CLOSED under stem_key**, so "clean" is earned at norm-v1. Near-duplicates below norm-v1 were not measured.
4. **Incident doc L28 / L73, "the 1,020 CLEAN questions".** **ID-ONLY**: 12 exact / 23 norm-v1 of the 1,020 are frozen-tree members (h2.py). The rubric-induction route also applies to these 12, because induction withheld by id (incident L7-L8).
5. **SPLIT-FUNCTION-IMPL C1 "|eval_closure ∩ train| = 0".** This is TRUE BY DEFINITION on the function: closure is applied before the check. It says nothing about the trees of record, as the A1 bracket already records.

## Resolution of +92

**No reading of the data produces 3,537 / 860 / 7,603.** What I ran (all at universe 12,000 = mmlu_pro LEFT JOIN eval_question_link, sentinel = -1,000,000 - rowid, exactly as `MMLUDatasetFetcher.loadFromDb` L493-L556):

| reading | eval | gate | train |
|---|---|---|---|
| R1: engine `finishSplit` (L863-L901): pinned = all 3,599 listed ids incl. 154 sentinels; key = stem_key of every test item | 3,770 (+171) | 843 | 7,387 |
| R2: pinned = 3,445 judgeable, keys of judgeable only | 3,552 (+107) | 859 | 7,589 |
| R3: pinned 3,445, keys of all 3,599 | 3,770 | 843 | 7,387 |
| R4 / R5: exact-text closure, pinned 3,599 / 3,445 | 3,699 / 3,507 | 850 / 866 | 7,451 / 7,627 |
| historical rowid fallback (the pre-07-26 id bug), pinned 3,445 or 3,599 | 3,741 | 842 | 7,417 |
| universe = eval_results (12,032), pinned 3,445 | 3,552 | 861 | 7,619 |
| R1 / R2 / exact readings on p8a29, pd610, p19d9, p7f7ce | none is 3,537 / 860 / 7,603 | | |

- Controls: R1 reproduces EVERY engine log triple on today's DB, for p8a29 (182; 3,781 / 832, h9_order logs of 09-16 08:28, the morning of the record), pd610 (164; 3,763 / 821), p19d9 (195; 3,794 / 829) and p7f7ce (12 / 1,206 / 10,782 = "11988 train (1206 gate) / 12 test"). So the DB's link table has not moved since 09-16, and a "past DB state" does not explain the gap.
- The record's paeec triple, 7,025 / 1,487 / 13,094, reproduces EXACTLY (d3_paeec.py) under R2, which equals R1 there because paeec has no sentinels.
- Under the SAME method, p2dca gives 3,552 / 859 / 7,589. The recorded p2dca triple is 15 items off it, and the 107 closure rows split into gate 12 / train 95, so the 11-gate / 81-train split that 3,537 / 860 / 7,603 requires matches no class of twin (GEN / RSENT x exact / norm-only).
- "3,537" appears first in c0f5ff7 (programme text) with no script (`git log -S'3,537'`: c0f5ff7, fd21fec, 611d540, all record-only commits).
- **Reading:** a transcription or an unsaved computation. Not recoverable; nothing in the data supports it.
- **Fix:** bracket the SPLIT-FUNCTION-IMPL p2dca line UNREPRODUCED and cite both reproducible readings: engine 3,770 / 843 / 7,387 (+171 over the 3,599 listed) and the paeec method 3,552 / 859 / 7,589 (+107 over the 3,445 judgeable). Say that the record's "eval 3,445 by id" is judgeable-only while the engine pins 3,599.

## Defects (ranked)

**D1 (HIGH): the MMLU-Pro-alone option-set and ordered counts are keyed on the linked mmlu_pro row, not the eval row that was judged.**
- Keyed on the judged eval row (gpt-4o reference row), p2dca RES with a GEN twin is norm-v1 70 (unchanged, since stems agree on 3,445 / 3,445), optset **64** (steward 33) and ordered-full-duplicate **31** (steward 0). On the 1,020 CLEAN: optset 22 / ordered 11 (steward's key: 11 / 0).
- So 31 p2dca questions were judged on an exact copy (stem + options in order) that sat in construction.
- Cause: the link picked the other copy (claim 8: on 51 of 54 mismatched links, the eval row's ordered options match an unlinked row).
- "Option-set 33" and "ordered 0" understate the true-duplicate count by about 2x.
- Fix: compute every options-bearing key on BOTH renderings (linked row and eval row) and report the union. Name the eval reference row.

**D2 (MEDIUM): +92 unresolved; the record's p2dca closure triple is unreproducible.** See above. Fix: the bracket as stated.

**D3 (MEDIUM): claim 8's reference object and answer count.**
- The eval row varies across models: 173 qids have more than one normalised option list with Meta-Llama-3-70B-Instruct excluded, and 7,485 with it included (7,510 Meta-Llama rows in this DB).
- The count is 54 / 19 against gpt-4o's row and 63 / 27 against the modal row. "17 with a different answer text" is one cell; the answer text differs on 19.
- Fix: name the reference row; report 54 / 19 (gpt-4o) and 63 / 27 (modal); state the 51 wrong-copy links.

**D4 (MEDIUM): the Multi-SWE "0 cross-side twins" is vacuous.**
- `tasks.content_key == stem_key(instance_id)` on 2,132 / 2,132 (meta: "ck-v1 (stem_key over the instance id; options-free)"), so content twins cannot exist by construction.
- The real guarantee is family closure: 0 of 51 repos span sides.
- Unreported support: 390 RES instances in 16 repos, family sum(n^2)/n = 37.76, so n_eff at rho = 1 is about 10.
- Fix: restate as "repo-family closure 0 / 51; no content key exists for Multi-SWE (the key is over the id)". Print the family Kish beside every Multi-SWE statistic.

**D5 (LOW): the 20NG zero holds by construction and rests on an untracked file.**
- Ingest rule (3) (`apply_rules` L118-L121) drops ALL copies of every norm-v1 duplicate group, so exact and norm-v1 twins are 0 on the whole universe and not only across sides.
- `experiment_configs/reserved_pool_frozen_pf844849e133cda4e_20ng.json` is untracked (`git status`: `??`).
- The rebuilt rows match the manifest sha; the WAL tail was not read, so what it holds is unverified.
- Fix: say "0 by ingest rule (3)"; commit the id file or name it as uncommitted. Near-duplicates (quoted replies) are unexamined.

**D6 (MEDIUM): CK-CLOSE-v1's key set is unspecified with respect to sentinels.**
- The engine closes on the stems of ALL test items (3,599). The paeec method (judgeable only) would leave **96** GEN rows (77 linked + 19 sentinels) that share a stem ONLY with a routing-only sentinel test item.
- Those rows would then contaminate every held-out ROUTING metric (Top-1 is computed over sentinels).
- Fix: the rule must say "keys of every held-out item, sentinels included".

**D7 (LOW): "Kish" is DEFF at rho = 1.** sum(n^2)/n is the upper bound of DEFF when the within-cluster correlation is 1. Report the range [1, 1.380] and n_eff [259, 358] (GPQA), and measure rho on correctness before calling it a DEFF.

**D8 (LOW): the three inline pieces were not saved** (the Multi-SWE check, the 3,537 reconciliation, the 1,020 reproduction). I redid all three (g_agent.py, d_closure.py through d5.py, e_1020.py plus h2.py). Fix: save scripts for every number the registrar records.

Not defects (checked):
- Meta-Llama-3-70B-Instruct is absent from multicorpus eval_results (0 rows) and excluded in mp_audit / linkcheck.
- No mmlu_pro<->eval crossing by id without an options check: the link is the fetcher's own, and D1 / claim 8 measure where it is wrong.
- Sentinels are excluded from both counts and reported separately (RSENT). That neither inflates nor hides the RES<->GEN counts; I reproduce them.

## CK-CLOSE-v1: is it sound?

Sound as a GENERATION-SIDE rule if it states four things:
1. **The key set is every held-out item including sentinels** (D6).
2. **Closure is global across corpora and pools of one build.** 3 MATH RES ids have MMLU-Pro GEN twins on paeec.
3. **Where a family exists, the family is closed too** (BFCL index family, Multi-SWE repo). stem_key over an id is not a content key (D4).
4. **Within-RES twin groups are clustered, not dropped**, with cluster-robust SEs by stem cluster (GPQA upper-bound DEFF 1.38; within-RES dups 215 ids on paeec).

Stem-only keying is conservative: it also moves the 127 stem-only MMLU-Pro variants, which are correlated with their twins (agreement 0.753 vs 0.534 null). It is immune to the link hazard, because stems agree on 3,445 / 3,445. It does NOT catch near-duplicates below norm-v1 (MinHash is out of scope and should be named).

**Routes left open in the trees of RECORD, which the rule cannot fix.**
- (a) **Construction members.** Frozen 20260727_042523: 2,437 / 2,448 p2dca texts, of which 12 / 23 are in the 1,020 CLEAN. bareq512_s42: 37 / 70. Union 20260911_144214: 427 distinct / 471 ids exact.
- (b) **Rubric induction on the frozen tree.** It withheld by ID (incident L7-L8), so the 12 exact twins of CLEAN questions were inside the induction corpora. The Option-A CLEAN re-analysis is therefore not fully clean (12 / 1,020 = 1.2%).
- (c) **The policy fit of ROUTER-CLEAN-POLICY / MC-E2E** on the union train side (21c4fda D2).
- (d) **Full-copy judging.** 31 p2dca questions were judged on an exact copy that was a construction member of bareq512_s42's generation side (D1).

bareq512_s42 is label-free (hygiene/bareq512_s42_labelfree), so route (b) does not apply to it. [REGISTRAR NOTE 2026-09-23, by insertion (the reviewer's text is not edited): CORRECTED 2026-09-23 by the SPLIT-FOLLOWUPS review (8ebfa7a): FALSE for the tree of record. 20260909_212117 was built with labelling and induction ON (143 LLM-written labels - not 158: the other 15 are the root and the 14 ground-truth anchors - and 87 induced leaf judgePrompt / judgeRubric). Induction withheld the active pool by EXACT linked text after an 80% hash hold-in, so 29 of the 37 exact twins were withheld; 28 OF THE 33 NORM-V1-ONLY TWINS WERE IN THE INDUCTION CORPORA OF 16 LEAVES, with the key mark and CoT; 28 IS EXACT, NOT AN UPPER BOUND (the corpus model reproduces all 17 [JUDGE-LEAK] log lines). Labelling applies NO reserved filter: 26 twin texts (12 exact, 14 norm-v1-only) were in the leaf labelling prompts of 16 leaves (the sampling is deterministic and was reproduced); internal-node samples are seeded and unreproduced, and all 70 are eligible there. ROUTE (b) APPLIES to RUBRIC-512 (cell arm), RUBRIC-512-SS, RUBRIC-512-R, LEAF-POWERED and rubric_text_stats; the RK-1 kit material is built from 212117 leaf members and its exposure is unmeasured. See docs/judge_v2_program.md L14455-L14487 (SPLIT-FOLLOWUPS).] I did not verify whether the union tree ran labelling or induction.

Closing only the generation side leaves no route in a NEW build at norm-v1, provided D6 is honoured. The trees of record need a rebuild or disclosure at the A1 bound.

## Proposed sentence of record

"CONTENT-DISJOINT-SPLIT-AUDIT (2026-09-23, zero calls; data steward, independently recomputed): the pools of record are id-disjoint but not content-disjoint.
- On the union pool paeec37aa28063c75, 471 EVAL ids (427 distinct texts) have an exact-text TRAIN twin and 478 have one under norm-v1: GPQA 288 (382 pairs, all with the same options and answer, 367 with the options shuffled), MMLU-Pro 185 (68 true duplicates at 0.999 correctness agreement, 127 stem-only variants at 0.753), MATH 3, BBH 2.
- On the MMLU-Pro pool of record p2dca21ab5f4ef3ae, 37 exact / 70 norm-v1 judgeable ids have a TRAIN twin, every one an unlinked sentinel row. Keyed on the question actually judged, 64 share the option set and 31 are full ordered duplicates.
- Of the incident's 1,020 CLEAN questions, 12 exact / 23 norm-v1 were frozen-tree members.
- 20NG (by its ingest's dedup rule), BFCL and Multi-SWE (repo-family closure; no content key) have no cross-side twins.
- The engine's stem-key closure (since 13f2142) moves 171 rows on p2dca (3,770 / 8,230, the af_clean_s42 split); the SPLIT-FUNCTION-IMPL figure 3,537 is not reproduced by any reading of the data."

## Does not show

- the effect of the twins on any routed or judged readout (only the A1 worst-case bound exists);
- near-duplicates below norm-v1 (paraphrase, punctuation beyond NFKC / whitespace / ASCII case, 20NG quoted replies);
- the content of the 20NG WAL tail (708,672 B, 09-23 04:30);
- where 3,537 / 860 / 7,603 came from;
- whether the union tree 20260911_144214 ran labelling or rubric induction over twin-bearing members;
- a DEFF: the Kish figures are rho = 1 bounds, not measured correlations;
- the steward's claims table (not saved); only my five spot-checks.

## Verdict

- Claims 1, 3, 4, 5, 6 and 9: CONFIRMED to the digit.
- Claim 2: CONFIRMED as keyed, understated on the judged object (D1).
- Claims 7 and 8: PARTLY.
- Claim 3b (+92): UNRESOLVED; the record's number is unreproducible.
- Claim 10: UNDETERMINED (table not saved); spot-checks as above.

**RECORDABLE WITH CONDITIONS:** D1, D2, D3, D4 and D6 enter the record's text (the sentence above carries D1, D2 and D4). CK-CLOSE-v1 is sound only with D6's key-set clause and the family clause.
