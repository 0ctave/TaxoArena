# Cost bills for the open queue (cost-estimator, 2026-09-19 ~14:25)

Nothing run, built, registered or edited by the estimator; state read from the files named. Sources: docs/agents/CONTEXT.md; docs/agents/plans/2026-09-18_reframing_and_next.md §2/§4/§5; docs/plan_2026-09-15.md Amendments 4-6 (L167-231); docs/judge_v2_program.md K-SELECTION L8224-8391 + pre-build bracket L8761-8769, PLACEMENT-STEPS L8392-8550 + bracket L8752-8759, ARM-B-VINTAGE L8552-8733 + bracket L8737-8750, AGENT-CORPUS-ADMISSION L5855-7026, MODEL-VINTAGE-CANARY L6038-6084, canary pass 1 L3612-3629; docs/reviews/READY_arm_b_vintage.md; the REDRAW chain.log; grok-reasoning-v1.db (mode=ro).

State facts that moved the bills at pricing time (verified by command): (i) ARM-B mid-run, 91/200 rows at 14:23:46 (~0.75 rows/s at 8 workers) [finished 14:28, NO ALARM]. (ii) `tools/analysis/k_selection_readout.py` (readout of record per the pre-build bracket L8765) did not exist on disk or in history; k_selection.sh runs it "if it exists". (iii) `tools/analysis/model_vintage_canary.py` (registered --precheck) does not exist. (iv) placement_steps.py carried an uncommitted +57/-21 diff (the fix list in progress); no READY_placement_steps.md. (v) No post-run review file for STABLE-CELL-SET / UNION-PROFILE-HOME / AGREE-ORDER at pricing time [filed 83cb8e5]. (vi) experiment_results/agent is 373 MB untracked and not ignored (.gitignore L145 negation).

## Summary table

| # | task | kind | cce max / expected | wall-clock | agent-h | blocker | value (ceiling) |
|---|---|---|---|---|---|---|---|
| 1 | K-SELECTION chain | build-only, registered | 0 / 0 | ~1.7 h serial, no-readers window | 1.0-1.5 | readout script; window vs #8 reviews, ARM-B analyze, #2 dry-run | one qualifier: 3/4 -> rule property or corpus fragility; count moves <= 2 (P4) |
| 2 | PLACEMENT-STEPS | judged, registered, go given (Am. 6 item 5) | 800 / 800 | ~25-35 min run + 2 min analyze | 1.3-1.8 | ARM-B "NO ALARM" gate [met]; fix list + 2nd READY committed | sonnet 7 -> 4 excl / 5 incl at most (4-tier floor); gpt-4o-mini 3 -> 2 a coin flip |
| 3 | ARM-B-VINTAGE | solve-only, registered | 2,000 / 2,000 | done 14:28 | 0.5-0.7 | none | stamps v0; MDE ~5pp at n=200 |
| 4 | BFCL base judged pilot | judged, NEW (no own registration) | 3,250 / ~1,000-1,330 | probe 2 min; run 30-40 min | 2.0-2.8 | author: cap, agent list, .gitignore; registration; READY; go | one sentence on the "for Agents" bridge; no cell (57 tasks); A vs 0.75 at SE ~0.03 |
| 5 | Multi-SWE-bench_trajs admission | engineering/ingest, NEW | 0 / 0 | 4.73 GB download + ingest; overlaps builds | 3-8 | author question 6; disk + .gitignore | first candidate agent PROFILE cell (2-4 strata >= 120 EVAL) or description-only |
| 6 | CANARY pass 2 | judged, registered, no go needed | 600 / 600 | ~15 min run | 0.8-1.0 | date >= 2026-09-22; ARM-B NO ALARM [met] | first retest floor of the deployed judge; MDE ~2.7pp; prediction likely inside the 5.7% floor |
| 7 | MODEL-VINTAGE-CANARY pass 1 | engineering + author generation, registered | 0 judge cce; ~0.81M output tokens (author's currency) | author's harness; precheck minutes | 0.7-1.0 + generation ops | author question 5; precheck script missing | fifth stamp; MDE ~6pp agreement loss; 3pp drift invisible |
| 8 | Recording backlog (3 reviews + 4 outcomes + ledger) | registrar-only + review | 0 / 0 | readouts 2 min each (pool readers) | 1.0-1.5 | must run in a reader window before #1 | nothing publishes unreviewed |

Rule-7 serialisation of record (every pool_guard --dry-run / readout / recomputation is a reader; K-SELECTION builds and nulls may not overlap any of them): ARM-B finish + --analyze -> #8 reviews + #2 re-dry-run + 2nd READY (readers, ~1-1.5 h) -> #1 K-SELECTION window (~1.7 h, nothing else) -> #2 pilot + run (its assembler reads the eval caches: a reader for the whole run) -> #6 on 09-22. #5 overlaps anything (imports no pool_guard, opens no DB of record).

## Per-task bills

### 1. K-SELECTION chain (I2 + R1'/R2'/R3' + 3 nulls + readout)
1. Kind: build-only, zero calls; registered (8fde7fa), flag merged (967a936), chain committed (4cd39c6); nothing built.
2. API spend: 0; no go needed (Amendment 6).
3. Machine: 4 builds x 2-3 min (REDRAW af_s137 04:09->04:11, af_s2048 04:37->04:39) ~10 min; 3 site nulls x ~26 min ~78 min; per-arm readout ~1.5-2 min x 3 + I2 identity ~1 min; total ~1.6-1.8 h in ONE no-readers window. REDRAW's af_clean_s42 null was interrupted once by a reader and restarted (chain.log 03:32): the window must be clean.
4. Agent time: engine-coder writes k_selection_readout.py (12-25 min) -> reviewer READY 10-25 min (may overlap the builds; must precede the readout's --run) -> run-operator preflight + launch ~10 min, unattended ~1.7 h -> reviewer post-run 8-25 min -> registrar outcome + REDRAW C3 bracket + ledger 10-15 min. ~1.0-1.5 agent-h.
5. Dependencies: I2 needs experiment_results/anchorfree/redraw/af_clean_s42/seed_42 on disk (present, untracked); C0 must read HELD before any primed build (I2 first, ~3 min: early stop). Blocked by readers. Closed lines: ANCHOR-FREE-CERT levers (P4), FW L53. Hazards: snapshots.db untracked receives four snapshots; restore frozen_triples_*_MAIN.json after every build; .gitignore .db negation would track ratings_<arm>.db.
6. Value: one qualifier in §1.1(a): "k-selection-fragile at the bar" -> "resolved by a geometric hysteresis rule" (HELD) or "the fragility is the corpus's" (F1); P4 caps the certified-count movement at +-2. Either verdict informative.
7. Total: 0 cce; ~1.7 h wall-clock; ~1.2 agent-h. RUN once the readout exists and the reader window is clear.

### 2. PLACEMENT-STEPS
1. Kind: judged; registered (20cb7b6), authorised (Amendment 6 item 5, 800 calls); script NOT READY at pricing time.
2. API spend: 400 matches x 2 = 800 cce ceiling = expected (schedule hash 2f8cbeefca20ed6b; pilot 24 inside; P7 <= 2 unusable rows not re-posted; no solves). Under the rule; go quoted.
3. Machine: 800 calls at 8 workers ~25-35 min; --analyze ~2 min (B = 2,000 x 8 anchors). Re-dry-run and run are pool readers: not during #1.
4. Agent time: engine-coder four fixes + selftest + re-dry-run reproducing schedule hash and C0 = 0.910/0.505/0.225/0.510, 0.710/0.595/0.170/0.360 (~15-20 min); reviewer second READY 15-20 min -> docs/reviews/READY_placement_steps.md; run-operator pilot (12 matches ~2 min) + run + analyze ~40 min; reviewer post-run 15-25 min; registrar outcome + FW L15/L189/L211 brackets + ledger ~15 min. ~1.3-1.8 agent-h.
5. Dependencies: ref_remint_outcome.txt line 2 "ALARM STATE: NO ALARM" [met 14:28]; the committed READY. Hazards: own cache newcomer_placement_steps.db (untracked, .gitignore negation); cross-step reuse 21 of 300 allowed by the bracket.
6. Value: sonnet's band cannot fall below the 4-tier floor; max effect 7 -> 4 exclusive / 5 inclusive; gpt-4o-mini 3 -> 2 a coin flip (key gap 0.0199 vs SE 0.013). A share at n = 100 has SE ~0.05; haiku and Qwen1.5-110B steps decidable; the deepseek step (P3 0.60-0.75) can fail F1 by POWER at 100 matches rather than by judge error (the power column separates the two). Changes FW's placement cost to "400 + 100 per separable tier" for mid-board newcomers.
7. Total: 800 cce; ~45 min after the READY; ~1.5 agent-h. Dropping t7 saves 200 cce but removes the only positive control: not recommended.

### 3. ARM-B-VINTAGE
Done 14:28: 200/200 YIELD, A = 0.9450 [0.9042, 0.9690], C1/C3 HELD, NO ALARM, P6 FAILED by instrument (median 6 completion tokens, as the pre-run bracket anticipated). Remaining: reviewer post-run 8-25 min (incl. script_sha256_16 9292e670ddfcb329 vs the READY's 250b10776b5c97b9 + the SET_HASH line), registrar outcome + FW L37 bracket + ledger + commit of grok-reasoning_v0_stamp.json. The alarm branch (not taken) was priced at 2,000-3,800 cce re-mint + 1,888 calls non-inferiority.

### 4. BFCL base-stratum judged pilot
1. Kind: judged; NEW as a test; Amendment 6 explicitly does not authorise it.
2. API spend: probe 50 + 57 tasks x 28 pairs = 1,596 matches -> ceiling ~3,250 cce; expected after the checker-disagreement filter ~1,000-1,330 (~700-900 if empty-turn failures, 18% of episodes, are non-judgeable). Go NOT quoted: ask, with the cap and the agent list.
3. Machine: probe ~2 min; ~1,300 calls ~35-45 min; analyze minutes. Reads bfcl_result_2025-12-16.db only: overlaps #1.
4. Agent time: registrar 6-20 min; engine-coder trace-shaped assembler + CHECKER_OUTPUT reference + probe + guard + analyze ~45-60 min; reviewer READY 15-25 min; run-operator ~50 min; reviewer post-run 15-25 min; registrar 10-15 min. ~2.0-2.8 agent-h.
5. Dependencies: author's cap (chars/4 median 453 / p95 2,422 / max 7,199), agent list (grok-4-1-fast-reasoning-FC is a contestant of the grok judge), .gitignore call on 373 MB; probe before pilot; READY before pilot. Closed: no trajectory reference, no per-trajectory rank, no process rubric. Hazard D10: empty-turn rows must be classed before the count is fixed.
6. Value: one measured sentence for the "for Agents" bridge; no profile cell (57 tasks). A vs 0.75 decidable at > 5 SE; MATH rung (0.958) vs CACHED_SOLVE rung (0.865) at ~3 SE; rho over 8 agents coarse.
7. Total: ~1,000-1,330 cce expected (3,250 max); ~1 h; ~2.4 agent-h. NEEDS A GO. Cheapest variant: probe 50 + ~200 filtered matches (400 calls) on the 5 agents with terminated >= 0.98, grok-FC excluded: A vs 0.75 at SE ~0.04, ~450 cce.

### 5. Multi-SWE-bench_trajs admission pilot
1. Kind: engineering / ingest, zero calls; NEW (own registration needed: corpus, normaliser, D_c reading).
2. API spend: 0. Author question 6 is the go on time and disk.
3. Machine: 4.73 GB HF download; ingest ~2,092 instances x up to 27 (scaffold, model) configs ~56k episode rows, minutes once the normaliser exists. No pool reader: may overlap #1.
4. Agent time: registrar 6-20 min; engine-coder three trajectory formats + cap recovery + split by repo + strict D_c per (language, repo) + EVAL counts vs 120: 3-6 h; reviewer READY 15-25 + post-run 15-25 min; registrar 10-15 min. ~4-8 agent-h.
5. Dependencies: author question 6; .gitignore (another ~4.7 GB untracked); disk. Hazards: MagentLess has no cap concept (predicted FAIL for (c)); "agent" = (scaffold, model), 27 configurations; unequal rosters per instance.
6. Value: the only surveyed corpus that can carry an agent PROFILE cell (EVAL ~630 instances over 7 languages, 2-4 strata predicted >= 120). The judged pass afterwards: 3,060 cce per cell per epoch, crosses the 4,000-match rule at >= 3 cells.
7. Total: 0 cce; ~1 h machine; ~4-8 agent-h. NEEDS THE AUTHOR'S WORD. Cheapest variant: report.json files + MSWE-agent trajs only (exit status carrier) to answer the 120-instance support and (c) on one scaffold, ~1-2 h builder time.

### 6. CANARY-BASELINE pass 2
1. Kind: judged; registered (Block 2, hash 50af669ac6997f9f); no go needed; refused before 2026-09-22 (NOT_BEFORE_PASS2).
2. API spend: 300 x 2 = 600 cce. Under the rule.
3. Machine: ~15-20 min; --analyze seconds; pool reader at launch and through the assembler.
4. Agent time: run-operator ~30 min; reviewer code-only READY on the pass-2 preflight 10-15 min (the pass-1 review 1e3b1ea covers the script); reviewer post-run 8-15 min; registrar 10-15 min + Amendment 4 trigger (3) live. ~0.8-1.0 agent-h.
5. Dependencies: the date; ARM-B NO ALARM [met]; deployed judge unchanged (fingerprint asserted).
6. Value: first test-retest floor of the deployed judge and the live alarm trigger; MDE ~2.7pp; the prediction (4-6%) is inside DECOMP's 5.7% floor: likely one sentence.
7. Total: 600 cce; ~25 min; ~0.9 agent-h. RUN ON 2026-09-22, outside any construction window.

### 7. MODEL-VINTAGE-CANARY pass 1
1. Kind: engineering (precheck, zero cost) + the author's contestant generation; registered (L5985-6084); nothing generated.
2. API spend: 0 judge cce. Generation: 12 models x 279 + null 7 x 279 = 5,301 generations; ~0.81M output tokens (5 API models ~386k; 7 open checkpoints ~426k on hosted/rented GPU); input side ~8-13M tokens (outside estimate, not on record). Author question 5.
3. Machine: precheck seconds (opens mmlu_pro_dataset_cache_v2.db mode=ro: a pool reader); generation wall-clock is the author's harness, unmeasured here.
4. Agent time: engine-coder model_vintage_canary.py --precheck 12-25 min (~25 min with --ingest/--analyze); reviewer READY 10-25 min; run-operator 5 min; if generated: reviewer 15-25 + registrar 10-15 min. ~0.7-1.0 agent-h + generation ops.
5. Dependencies: harness P declared per generation; 7 checkpoints hosted; C1 >= 0.99 extractor reproduction on >= 10 of 12 models; C2 needs >= 5 of 7 checkpoints. Hazards: NON_TERMINATED > 5% per model refuses that model; new untracked cache.
6. Value: fifth stamp on every board row and the first contestant-drift reading; MDE ~6pp; the real risk is F_cache < 0.80 (harness mismatch, not drift).
7. Total: 0 cce here; ~0.9 agent-h + generation. DEFER TO THE AUTHOR; run the zero-cost precheck now. Cheapest informative variant: null on the 5 smallest open checkpoints + the 5 API models, skipping the two 70B nulls.

### 8. Recording backlog
Reviews of STABLE-CELL-SET / UNION-PROFILE-HOME / AGREE-ORDER [done 83cb8e5]; outcomes + brackets for the three + ARM-B; one ledger patch v115 -> v116 (grep the version first). ~1.0-1.5 agent-h; each recomputation is a pool reader: before #1. Hazards: union readouts on MAIN_union_routing*.csv only; AGREE-ORDER's P7 bracket on PROFILE-R-FILTERED by insertion; both conventions on every row; OPTIONS-key join.

## Queue totals
Judged / solve spend outstanding after ARM-B: #2 800 + #6 600 = 1,400 cce needing no further go; #4 ~1,000-1,330 expected (3,250 max) needs a go; #7 in the author's token currency. Lane-1 wall-clock today: ~1-1.5 h readers (#8, #2 READY) + ~1.7 h (#1) + ~45 min (#2) = ~3.5-4 h serial; #5 in parallel if the author says so; #6 on 09-22. Agent time: ~7-9 h for #1-#3, #6, #8; +2.4 h for #4; +4-8 h for #5; +0.9 h for #7's precheck.
