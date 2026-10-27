# Data and measurement economics of a continual capability-profile framework (data-steward, read-only, 2026-09-17)

## Summary
1. ~588k scored rows over two corpora: MMLU-Pro eval_results 560,379 rows / 47 models / 12,118 qids (46 models / 12,032 qids after excluding Meta-Llama-3-70B-Instruct); multicorpus_cache_v1.db 388,908 rows / 18 models / 21,606 questions.
2. Judged verdicts of record: x12 9,142 (66 pairs, 2,811 q) + x20 12,394 (124 pairs, 2,646 q) + GROK-CALIB 9,142 + Kotlin board 9,123 + GEN-ARENA 3,000 + STAGE3-MATH-CAPFREE 2,996 + placement 1,600 + canary 300; 58 caches / 158,268 rows (JUDGE-FINISH-AUDIT).
3. Only 7 of 58 caches carry finish_reason (8.6% of rows); every board of record cannot tell NON_TERMINATED from wrong.
4. Keys/checkers exist for MMLU-Pro, BBH, GPQA, MuSR (log-likelihood, no traces), MATH (checker; 1,024-token cap hits 12-19% of eval rows), IFEval (constraint vector); a judge is needed nowhere for ranking on keyed cells.
5. Cost: 2 cce per match (dual order), 10 cce per reference solve, 0 per checker output; ~16.5 cce per unkeyed question first cycle (12 models).
6. Newcomer: 800 cce to BAND (3 tiers mid-board, 7 at the frontier: NEWCOMER-PLACEMENT-LIVE FAIL) plus ~3,100 cce for profile coverage; 400 matches is not a placement budget.
7. New judge: ~2,100 + ~20,000 cce and a human go (GROK-CALIB 18,284 calls); parameters do not transfer across roster/judge/corpus (BUDGET-TRANSFER, JUDGE-TRANSFER UNDETERMINED).
8. Support: SE 0.15 needs 63-136 distinct questions per cell under the declared fit (K-RECONCILE correction of H6b's 120-190); anchor-profile reliability 0.70 needs ~210 q/cell for the judge, 50 for the key; DEFF 2.0x median.
9. Noise floor 5.7% test-retest (DECOMP); JUDGE-WIRING -2.6pp on identical bytes is provider nondeterminism; canary floor unread until pass 2 >= 2026-09-22.
10. Id-space hazards: OPTIONS-key join only; 120 judged questions without an mmlu_pro row; 7 gt_answer mismatches; text-keyed ground_truth_category; x20 157 duplicate (ordered pair, qid) groups; reserved_test_queries.json overwritten per build.
11. p8a29/p2dca incident (71%) recurred in the multi-corpus line (~70%); fix = per-item hash split (GATE [300,400)), 3/3 rebuilds; the trees of record still FAIL the TRAIN-only invariant (2,437 / 37 / 427 EVAL texts).
12. Backups: no backup manifest; 9 caches the ledger calls "gitignored" are UNTRACKED-NOT-IGNORED (`!experiment_results/**/*.db`); truly ignored: kotlin board (82.5 MB), gen_arena_grok.db, multicorpus_cache_v1.db, refqual_*.
13. AGENTS: zero agent trajectories, zero tool logs, zero multi-step tasks (FRAMEWORK L269 "Nothing here judges agent traces"). Only trace-shaped evidence: MATH/IFEval single-turn generations.
14. Transferable finding: CHECKER OUTPUT (0.958 STAGE3-MATH-CAPFREE) > CACHED SOLVE (0.849-0.852) > SPECIFICATION (0.658 GEN-ARENA IFEval).
15. Ranked leads: L1 code-with-tests corpus (checker = test runner, 0 cce reference); L2 IFEval re-judge with checker OUTPUT (~2,400 cce); L3 agent-trajectory schema with final-state checker, pilot <= 4,000 matches; L4 GSM8K/MATH-500 keyed calibration cells; L5 WildChat/LMSYS: no key/checker, refused by the record's rule (routing structure only, 0 calls).

## Agent trajectory dataset requirements (to enter the pipeline as-is)
(a) stem + content_key for the per-item split (SplitSide norm-v1; family_id write-once for templated tasks); (b) a checker emitting a normalised OUTPUT per (task, agent) (pass/fail vector or final-state diff) so D_c >= 0.95, the disagreement filter is live, reference cost 0; (c) finish_reason and completion_tokens per step (rule 10; MATH lost 16.5% of pairs to an unrecorded cap); (d) tool log + final state as the judged artefact with a stated per-step cap (cap-hit is a class, not a verdict); (e) a designed (source, domain) stratum per task (routing value lives at the family layer: MC-E2E +3.38pp clean; leaf routing does not beat domains). Reserved-split rule: templated tasks share a family_id on one side; any artefact induced over EVAL trajectories is contamination.

## Versioning (what must be frozen)
Pool ids (p2dca 3,445; paeec 6,482) as id files; set hashes (canary 50af669ac6997f9f, JUDGE-WIRING ae92da306544f453, board c0d3f708cbc3930e); snapshot ids (frozen 20260727_042523; bareq512_s42 20260909_212117; union 20260911_144214); kit hash + payload sha per judge_calls row (Kotlin board only); script sha in meta; checker table sha; normaliser norm-v1. Per model version: deployment fingerprint, provider, response id, tokens, latency. Per judge version: fingerprint, prompt_hash, protocol_id, max_tokens, temperature literal, its own calibration board (b0, b1 re-draw fragile at ~26 events). Per reference vintage: model, prompt hash, protocol, minted_at, side_at_mint (the 3,432-solve cache has none: one vintage). Per tree: snapshot id, pool id, leaf_key = sha of TRAIN members, TRAIN-only audit count. Per pool: id file, corpus set, epoch.

## Per re-judge cycle (union, 18 models)
<= 900 references x 10 + 3,400-match edge pass x 2 + canary 1,200 + vintage probe 500 + 10% slack ~ 19,000 cce, 3,700 judged matches (under the 4,000-match cap). Board stability: 2,000 matches give rho >= 0.93 in 100% of draws; the top-4 violation count is 3.0 at every budget (budget buys nothing at the frontier). Answer-disagreement filter keeps 99.8% of decidable pairs, judges 16.9% of frontier matches; inert on open-ended generation.

## Steward hazards
No backup manifest; untracked-not-ignored caches (grok_calib, newcomer_placement, stack_norubric, ref_checklist, escalate_llama_law, canary_baseline_pass1, stage3_math_grok_v2_capfree, checker_answers_v1/v2, checklist_grok-reasoning) would be committed by `git add -A`; x20 and every rubric-line cache lack finish_reason; two 6,482-row pools coexist in multicorpus reserved_pool (paeec37aa28063c75 and pa95843d826d40ffd): pin by id.
