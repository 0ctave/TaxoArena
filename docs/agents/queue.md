# TaxoArena queue of record (human view of docs/agents/queue.json)

Owner: experiment-manager. Last update 2026-09-23T13:05+02:00 (HEAD 188cc85, ledger v133, MODE both (night of 2026-09-23, phased A/B/C under plan Amendment 9)). Rendered from queue.json; edit the JSON, not this table. [This render: the registrar, 2026-09-23, transcribing the experiment-manager's QUEUE_DELTA_2026-09-23; the header, the ranking list and the table '## The queue' are re-rendered from the JSON; every other section below is kept as written at e422daa (HEAD ebd462d) and is HISTORICAL for the night of 2026-09-23.]

Pricing: docs/agents/plans/2026-09-19_queue_bills.md (cost-estimator 2026-09-19 ~14:25) for the pre-existing items; the night slate re-priced by the cost-estimator on 2026-09-23 03:40-03:55 in one batched call (chain wall-clock, IFEVAL-CHECKER-OUTPUT, BFCL under the manager's cap/roster proposals, TRACE-TRUNCATION, the 27-row re-post, LEAF-INTERACTION, the canary --analyze fix, the INCONSISTENCIES pass); items priced by neither carry priced=false; the 2026-09-23 midday delta: cost-estimator 2026-09-23 ~11:55, batched, 21 items (transcribed by the registrar from the experiment-manager's QUEUE_DELTA_2026-09-23 at HEAD 0cca0d5)

Ranking:
- docs/agents/plans/2026-09-18_reframing_and_next.md (R1-R11, stop list, author questions 1-8)
- docs/plan_2026-09-15.md Amendment 6 (L190-231)
- docs/plan_2026-09-15.md Amendment 9 (L316-L363): tonight's ceiling of 14,000 grok calls
- docs/agents/plans/2026-09-17_continual_capability_profile_leads.md C3 (L174-L181) and C4 (L181-L185): the two judged leads revived tonight
- docs/plan_2026-09-15.md Amendment 11 (2026-09-23, the judged separator programme, BUDGET ONLY)

## Tonight's budget (plan Amendment 9)

Ceiling **14000 grok calls** for the night of 2026-09-23, pilots included; spent at this update: **0**.

| item | calls |
|---|---|
| BFCL-JUDGED-PILOT | 3,096 ceiling / 1,316 expected (probe 100 + pilot 24 inside) |
| IFEVAL-CHECKER-OUTPUT | 838 (the decidable-only variant: 407 key-decidable matches x 2 orders + a 24-call pilot); the 2,400-call full form is NOT scheduled because rho and the BRIDGE are vacuous under an oracle-shaped reference |
| POT-REPOST-27 | 27, conditional on the registrar resolving the authorisation contradiction in PHASE A |
| TRACE-TRUNCATION | 2,184, REGISTERED and BUILT tonight, RUN DEFERRED and NOT counted against tonight |
| **scheduled tonight, expected** | **2181** |
| if TRACE-TRUNCATION is added | 4365 |

Headroom: 11,819 of 14,000 left unspent under the scheduled plan; the binding constraint tonight is the chain's wall-clock and the single adversarial-reviewer, NOT the ceiling.

## State verified by command at this update

- 2026-09-23 03:35:28 powershell Get-CimInstance Win32_Process (python/java/bash/ollama): NO java, NO python, no chain process -> the chain was NOT running at 03:35; site_null_ng_af_s42.csv absent with ng_af_s42.sitenull.started present (an interrupted null: marker without CSV)
- 2026-09-23 03:55:11 the same command: java 7600 + 4292 (created 03:36:38) and 9716 (03:36:42, -DnullReps=300) -> the chain IS running; tail -4 experiment_results/topic_partition/chain.log -> '[03:36:38] ng_af_s42 SITENULL start snapshot 20260922_195728_Headless_Run_Auto_ge'; T1's build was skipped ('attempted earlier ... construction started; snapshot present; not retried') and the pool pf844849e133cda4e was verified earlier. PHASE A began 03:36:38.
- curl -s -m 8 http://localhost:11434/api/tags -> HTTP 200 with 'qwen3-embedding:latest' listed: the chain's one operator gate is MET
- git log --oneline -1 -> ebd462d (plan Amendment 9); git status --porcelain -- src/ tools/ docs/ -> empty
- grep -n 'ARENA-V3' docs/judge_v2_program.md -> registered L583, WITHDRAWN at L1944 by ARENA-V3-COMPILED; no section exists for TRACE-TRUNCATION or IFEVAL-CHECKER-OUTPUT (both unregistered)
- ls tools/analysis/ -> causal_length.py, generative_arena.py, stage3_math.py, pot_ref.py present; NO bfcl judged assembler exists (agent_admission_pilot.py is the zero-call admission script)
- sed -n '110,131p' tools/chains/topic_partition.sh -> busy_python counts ONLY python.exe whose command line matches 'tools/analysis'; wait_idle WAITS 60 s in a loop between steps: it does not refuse and does not corrupt
- grep -n -- '--pass' tools/analysis/canary_baseline.py -> choices=[1,2]: a canary pass 3 would need code and a registration

## Totals

- night slate: 7707 calls at ceiling, 4365 expected
- scheduled tonight: 2,181 expected (BFCL 1,316 + IFEVAL 838 + the re-post 27 if its authorisation resolves); TRACE-TRUNCATION's 2,184 is REGISTERED AND BUILT tonight but its RUN is DEFERRED to 2026-09-24 unless the author asks for the ceiling to be used
- machine window: 5.9 expected to CHAIN DONE (~09:30), p5 ~07:15, p95 9.7 (~13:15), measured from 03:36:38
- agent hours: ~15-19 across six roles for the whole night (registrar ~2.5, engine-coder A ~1.5, engine-coder B ~2.0, reviewer 1.6-2.2 strictly serial, judge-design 0.75, run-operator ~2.5, manager ~1)

## The queue

| # | id | state | kind | lane | posts LLM | reads pool | calls max / exp | cce max / exp | wall-clock | blocker | value rank |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GUARD-22-RENAME-PROOF | registered | engineering | machine | no | yes | 0 / 0 | 0 / 0 | ~20 min in one rule-7 no-readers window (two :siteNull legs at -PnullReps=24, ~7 min each, plus the switch an… | - | UNRANKED (the experiment-manager's) |
| 2 | BFCL-FLIP-RESEED | registered | judged | LLM | yes | yes | 200 / 200 | 200 / 200 | ~8 min (dry-run ~1, pilot ~1, run ~5, analyse ~1) | waits: BFCL-JUDGED-PILOT; AUTHOR/PRECEDENT: authorised to schedule (relayed by the orchestrator, 2026-09-23); not a budget-rule exception and no amendment written | UNRANKED (the experiment-manager's; the registrar does not rank) |
| 3 | BFCL-FINAL-STATE-SWAP | registered | judged | LLM | yes | yes | 916 / 916 | 916 / 916 | ~40 min (dry-run ~2, pilot ~2, run ~34, analyse ~2) | engine-coder script -> committed READY (the closed-line gate, Amendment 11 3(a), is DISCHARGED by the ruling at 1470fe8) | UNRANKED (the experiment-manager's; the registrar does not rank) |
| 4 | ARM-B-VINTAGE | done | solve | LLM | yes | yes | 2000 / 2000 | 2000 / 2000 | done 14:28 | - | R9 |
| 5 | STABLE-CELL-SET | done | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | done | - | R1 |
| 6 | UNION-PROFILE-HOME | done | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | done | - | R3 |
| 7 | AGREE-ORDER | done | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | done | - | R4 |
| 8 | ARMB-REVIEW | done | review | agent | no | yes | 0 / 0 | 0 / 0 | 8-25 min | waits: ARM-B-VINTAGE | R9 (recording) |
| 9 | REC-BACKLOG | done | registrar | agent | no | yes | 0 / 0 | 0 / 0 | readout re-runs 2 min each (pool readers) | waits: STABLE-CELL-SET, UNION-PROFILE-HOME, AGREE-ORDER, ARMB-REVIEW | gate |
| 10 | PS-FIXES | done | engineering | agent | no | yes | 0 / 0 | 0 / 0 | 15-20 min | waits: ARM-B-VINTAGE | R5 (prerequisite) |
| 11 | PS-READY2 | done | review | agent | no | yes | 0 / 0 | 0 / 0 | 15-20 min | waits: PS-FIXES | R5 (gate) |
| 12 | PLACEMENT-STEPS | done | judged | LLM | yes | yes | 800 / 800 | 800 / 800 | pilot ~2 min + run 25-35 min + analyze ~2 min | waits: ARM-B-VINTAGE, PS-FIXES, PS-READY2 | R5 |
| 13 | KSEL-READOUT | done | engineering | agent | no | yes | 0 / 0 | 0 / 0 | 12-25 min | - | R2 (prerequisite) |
| 14 | KSEL-READOUT-READY | done | review | agent | no | yes | 0 / 0 | 0 / 0 | 10-25 min | waits: KSEL-READOUT | R2 (gate) |
| 15 | K-SELECTION | done | build | machine | no | yes | 0 / 0 | 0 / 0 | ~1.6-1.8 h serial in ONE no-readers window (4 builds ~10 min + 3 nulls ~78 min + readouts ~7 min) | waits: KSEL-READOUT, KSEL-READOUT-READY, REC-BACKLOG, PS-READY2, ARMB-REVIEW | R2 |
| 16 | CANARY-READY2 | done | review | agent | no | yes | 0 / 0 | 0 / 0 | 10-15 min | - | R8 (gate) |
| 17 | CANARY-PASS2 | done | judged | LLM | yes | yes | 600 / 600 | 600 / 600 | ~15-20 min run + analyze seconds | waits: ARM-B-VINTAGE, CANARY-READY2 | R8 |
| 18 | BFCL-JUDGED-PILOT | done | judged | LLM | yes | no | 3096 / 1316 | 3096 / 1316 | probe ~4 min + pilot ~2 min + run ~48 min + analyze ~2 min = ~56 min | waits: BFCL-REG, BFCL-BUILD, BFCL-READY | R6 - ranked FIRST of the night's judged slate by value per call |
| 19 | MULTISWE-INGEST | done | engineering | agent | no | no | 0 / 0 | 0 / 0 | download + ingest ~1 h machine; no pool reader | waits: GITIGNORE-AGENT | R7 |
| 20 | MVC-PRECHECK | done | engineering | agent | no | yes | 0 / 0 | 0 / 0 | precheck seconds | - | R10 (prerequisite) |
| 21 | MODEL-VINTAGE-CANARY | done | engineering | agent | no | yes | 0 / 0 | 0 / 0 | the author's harness (unmeasured) | waits: MVC-PRECHECK | R10 |
| 22 | GITIGNORE-AGENT | blocked | registrar | agent | no | no | 0 / 0 | 0 / 0 | minutes | AUTHOR/PRECEDENT: question 1 (third clause): ignore experiment_results/agent/** (bfcl_raw + the result DB), or track the DB only, or trac… | gate |
| 23 | LEAF-INTERACTION | blocked | zero-call | CPU (PHASE C) | no | yes | 0 / 0 | 0 / 0 | engine-coder 12-25 min for a --level leaf path (profile_reliability.py --interaction-only already exists at L… | support: 87 leaves, mean 32.3, vs the 120-190 floor (the 9bd9850/0cca0d5 prompt rule) | R11 |
| 24 | TOPIC-PARTITION-20NG | done | build | machine | no | yes | 0 / 0 | 0 / 0 | RELAUNCHED 03:36:38 on 2026-09-23 after the author stopped it at 20:26 on 09-22. Remaining: T1 site null rest… | waits: TP20-BUILD, TP20-READY | machine lane, sole occupant. Ranked below the judged slate in paper value, but it IS the … |
| 25 | TP20-BUILD | done | engineering | agent | no | no | 0 / 0 | 0 / 0 | minutes; no build launched by the coder | waits: TOPIC-PARTITION-20NG | unranked (experiment-manager to rank; plan 2026-09-18 section 5 question 2 answered by th… |
| 26 | TP20-READY | done | review | agent | no | yes | 0 / 0 | 0 / 0 | minutes; a --dry-run is a pool reader (rule 7) | waits: TP20-BUILD | unranked (experiment-manager to rank; plan 2026-09-18 section 5 question 2 answered by th… |
| 27 | TP20-REVIEW | done | review | agent | no | yes | 0 / 0 | 0 / 0 | minutes; a pool reader, after the chain | waits: TOPIC-PARTITION-20NG | unranked (experiment-manager to rank; plan 2026-09-18 section 5 question 2 answered by th… |
| 28 | TP20-OUTCOME | done | registrar | agent | no | no | 0 / 0 | 0 / 0 | minutes | waits: TP20-REVIEW | unranked (experiment-manager to rank; plan 2026-09-18 section 5 question 2 answered by th… |
| 29 | IFEVAL-RULING | done | review | agent | no | no | 0 / 0 | 0 / 0 | 30-45 min | - | gate |
| 30 | IFEVAL-CHECKER-OUTPUT | done | judged | LLM | yes | yes | 838 / 838 | 838 / 838 | pilot ~2 min + run ~33 min + analyze ~2 min | waits: IFEVAL-RULING, TOPIC-PARTITION-20NG | third of the three judged items by value per call; scheduled SECOND because its reviewer … |
| 31 | TRACE-TRUNCATION | drafted | judged | LLM (deferred) | yes | yes | 2184 / 1100 | 2184 / 1100 | run ~86 min + analyze ~2 min (360 pairs x 3 arms x 2 orders, plus a 24-call pilot) | unauthorised, Amendment 11 3(c); re-price after TIE-MECHANICS | second of the three judged items by value per call |
| 32 | POT-AUTH-RESOLVE | done | registrar | agent | no | no | 0 / 0 | 0 / 0 | 15-20 min | - | gate |
| 33 | POT-REPOST-27 | closed-already-done | solve | LLM | yes | yes | 27 / 27 | 270 / 270 | ~16 min | waits: POT-AUTH-RESOLVE; AUTHOR/PRECEDENT: one line from the author: does the 2026-09-19 you-can-repost-them quoted in pot_ref.py cover this, or is the programme'… | hygiene; the cheapest item of the night |
| 34 | CANARY-ANALYZE-FIX | drafted | engineering | agent | no | yes | 0 / 0 | 0 / 0 | 20-30 min to write; its selftest is a tools/analysis invocation and is therefore PHASE B | - | gate for any future epoch |
| 35 | INCONSISTENCIES-PASS | drafted | registrar | agent | no | yes | 0 / 0 | 0 / 0 | text 45-60 min (PHASE A); scripted 45-60 min (PHASE C), folded into the ONE ledger patch of the night | - | record hygiene |
| 36 | BFCL-REG | done | registrar | agent | no | no | 0 / 0 | 0 / 0 | 20 min | - | gate |
| 37 | BFCL-BUILD | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | 45-60 min | waits: BFCL-REG | R6 (prerequisite) |
| 38 | BFCL-READY | drafted | review | agent | no | no | 0 / 0 | 0 / 0 | 20-25 min code-only in PHASE A, plus a 10 min dry-run confirmation at the head of PHASE B | waits: BFCL-BUILD | R6 (gate) |
| 39 | TP20-T1B-NULL | running | build | machine | no | no | 0 / 0 | 0 / 0 | the null 90-140 min (point 108) at -DsiteNullHeap=14g plus a bounded readout; ~1.8 h in ONE rule-7 no-readers… | waits: TOPIC-PARTITION-20NG | unranked (experiment-manager to rank) |
| 40 | TP20-C2-CONFORMANCE | registered | engineering | agent | no | no | 0 / 0 | 0 / 0 | minutes (selftest only; no build, no null, no readout run of record) | waits: TOPIC-PARTITION-20NG | unranked (experiment-manager to rank) |
| 41 | ROUTER-CLEAN-POLICY | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 15-30 m | no-readers block 1; the fix must ALSO cluster the bootstrap (multicorpus_router_e2e.py L116 resamples questions, not clusters, so the > 2 SE criterion runs on … | 1 |
| 42 | UNION-AF-ROUTE | drafted | build | machine | no | yes | 0 / 0 | 0 / 0 | 50-70 m | rule-7 window; author decision on TRAIN-ONLY rebuild-or-disclose | 2 |
| 43 | TIE-MECHANICS | drafted | zero-call | CPU | no | no | 0 / 0 | 0 / 0 | 2-5 m | none (runnable now); DESCRIPTIVE-ONLY: its reversal cell has no power | 3 |
| 44 | VOTE-FRAME-CERT | drafted | engineering | agent | no | yes | 0 / 0 | 0 / 0 | 10-20 m | block 1. PREMISE CORRECTED: positional-only storage is the CONVENTION, not canary's exception. rejudge_grok.py L200-206 computes the transposition and throws i… | 4a |
| 45 | POSITION-INDEX-ALL | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 15-30 m | VOTE-FRAME-CERT; stated dependency (not a gate) of BFCL-FLIP-RESEED | 4b |
| 46 | CERT-UNDER-FILTER | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 20-40 m | block 1; MUST be registered with a stated MDE against the filtered-schedule bias (A-REDEFINE-REFIT had no power against it, programme L3675) | 5 |
| 47 | REF-LADDER-RECOMPOSE | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 20-40 m | block 1; registration must say a recomposition of existing caches is NOT a new reference variant | 6 |
| 48 | DEFF-ATLAS | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 1.5-3 h | block 1; cache-fitness pass | 7 |
| 49 | BAND-INTERVAL | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 1-2.5 h | DEFF-ATLAS; do not start before the over-claim audit's findings are applied (it may retract the sentence the interval is built around) | 8 |
| 50 | CERT-ALIGN-SIZE | drafted | zero-call | CPU | no | no | 0 / 0 | 0 / 0 | 5-12 m | TP20-T1B-NULL; DESCRIPTIVE-ONLY on the 20NG arm | 9 |
| 51 | SUPPORT-FLOOR-CHECKER | drafted | zero-call | CPU | no | no | 0 / 0 | 0 / 0 | 20-40 m | author decision | 10 |
| 52 | JOIN-CARDINALITY-GUARD | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | 5 m + suite | suite after the null | 11 |
| 53 | MULTISWE-CORRECTIONS | drafted | zero-call | CPU | no | no | 0 / 0 | 0 / 0 | 10-20 m | GITIGNORE-AGENT (soft); the `_-` vs `__` join fix + the CAP_HIT re-read | 12 |
| 54 | SUPPORT-PLAN | drafted | zero-call | agent | no | no | 0 / 0 | 0 / 0 | 10-20 m | author: adopt as instrument | 13 |
| 55 | SEQ-LOOKS | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 2-5 m | block 1; DESCRIPTIVE-ONLY | 15 |
| 56 | SB-LENGTH | drafted | zero-call | CPU | no | yes | 0 / 0 | 0 / 0 | 1-3 m | block 1; DESCRIPTIVE-ONLY; must report against c = 2.52 and NEVER refit to the settled roster | 16 |
| 57 | BFCL-DEGRADED-CONTROL | deferred | judged | LLM | yes | no | 324 / 324 | 324 / 324 | 15-20 m | executor fetch (network + environment change) and an unrecorded harness code commit; DC3 may fail closed on code drift; re-evaluate after BFCL-FINAL-STATE-SWAP… | 17 |
| 58 | CANARY-EPOCH2-RUNG | drafted | judged | LLM | yes | yes | 1200 / 1200 | 1200 / 1200 | 30-40 m | the within-session rung is unregistered (the 600 epoch-2 calls are a standing obligation, item 21) | 18 |
| 59 | BFCL-LENGTH-POSITION | drafted | zero-call | CPU | no | no | 0 / 0 | 0 / 0 | 5-15 m | GITIGNORE-AGENT (hard) | 19 |
| 60 | EPOCH-GROWTH | drafted | build | machine | no | yes | 0 / 0 | 0 / 0 | 3-3.5 h | n = 3 tree-pairs is a band, not a test; the worst machine-hours-per-claim item | defer |
| 61 | FRAMEWORK-LIMITS-BRACKET | done | registrar | agent | no | no | 0 / 0 | 0 / 0 | minutes | DONE at 8b4075b (L263 / L411 bracketed) | 14 |
| 62 | BFCL-TRACE-TEMPLATE | declined | judged | none | no | no | 0 / 0 | 0 / 0 | none | inadmissible under the DANGLING-REFERENT fence F4 (1470fe8), and a duplicate of BFCL-FINAL-STATE-SWAP (Amendment 11 L405) | declined |
| 63 | KOTLIN-AUDIT-MERGE | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | not priced | JVM window: compile + 3 new tests + ConfigParsesTest + full suite + a byte-inertness replay on a recorded arm, then reviewer MERGEABLE | unranked (Kotlin audit, branch kotlin-stale-audit @ 1b6daf7) |
| 64 | REGENERATE-SPLIT-REFUSAL | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | not priced | needs registration: `regenerateSplit = true` on a snapshot-loading run silently overwrites the pool of record (the 2026-09-09 incident's shape); no committed c… | unranked (Kotlin audit, branch kotlin-stale-audit @ 1b6daf7) |
| 65 | EFFECTIVE-CONFIG-ARMS | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | not priced | needs registration: snapshots of record cannot say whether they were built anchor-free, order-shuffled or with a primed gate (applyEffectiveConfig writes back … | unranked (Kotlin audit, branch kotlin-stale-audit @ 1b6daf7) |
| 66 | STRICT-BOOLEAN-PARSE | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | not priced | 19 TOML booleans use String.toBoolean(), so `runPipeline = ture` builds nothing and exits 0; safe iff ConfigParsesTest stays green under toBooleanStrictOrNull | unranked (Kotlin audit, branch kotlin-stale-audit @ 1b6daf7) |
| 67 | STACK-JUDGE-RO-CACHE | drafted | engineering | agent | no | no | 0 / 0 | 0 / 0 | not priced | engine-coder change + reviewer READY; must not run while a reader of that cache is live | unranked (the experiment-manager's) |

States: drafted / registered / built / READY / running / paused / done / blocked / declined. Kinds: zero-call / build / judged / solve / engineering / registrar / review. Never delete an entry.

## Schedule of the night of 2026-09-23 (MODE both; nothing launched by the manager)

PHASE A runs from **03:36:38** (the verified chain relaunch) to **CHAIN DONE**, expected **~09:30**, p5 ~07:15, p95 ~13:15.
While it runs, **no `python tools/analysis/...` may execute** — that forbids every `--dry-run`, `--selftest`,
`ledger_patch.py` and `results_index.py`. Verified mechanics: `busy_python` (tools/chains/topic_partition.sh L118-121)
matches only command lines containing `tools/analysis`; `wait_idle` (L124-131) then **waits** 60 s at a time at the next
step boundary. A reader therefore **delays** the chain; it does not corrupt it. A reader alive during a **BUILD** step is
a rule-7 violation and is forbidden outright.

### PHASE A — agent lane only

| order | id | role | must NOT do |
|---|---|---|---|
| A1 | IFEVAL-RULING | judge-design-specialist | execute anything; it reads the record only. Do it FIRST: A4/A5/A12 all wait on it |
| A2 | BFCL-REG | registrar | write code; the registration commit must precede the first line of the assembler |
| A3 | BFCL-BUILD | engine-coder A (worktree) | run `--dry-run` or `--selftest` (both are PHASE B) |
| A4 | IFEVAL-CHECKER-OUTPUT registration | registrar | register before A1's ruling is written down |
| A5 | IFEval reference block + paired analyze | engine-coder A | run the assembler; touch gen_arena_grok.db for write |
| A6 | CANARY-ANALYZE-FIX | engine-coder B (worktree) | run `--analyze` on the epoch-1 outcome file — mode "w" would wipe the 4178a7c insertions |
| A7 | TRACE-TRUNCATION registration | registrar | schedule its run tonight (deferred by design) |
| A8 | causal_length.py retarget | engine-coder B | run it |
| A9 | LEAF-INTERACTION draft + `--level leaf` flag | registrar + engine-coder B | **register it** — that needs the author's word |
| A10 | INCONSISTENCIES-PASS, text half (items 2, 4, 5, 9) | registrar | touch `ledger_patch.py` or `results_index.py` |
| A11 | POT-AUTH-RESOLVE | registrar | post the 27 calls |
| A12 | code-only READYs: A6 → A9 → BFCL-READY → IFEval → TRACE-TRUNCATION | adversarial-reviewer | run a dry-run to "confirm" a READY; tonight the READY is code-only and the dry-run confirmation is the head of PHASE B |
| A13 | the PHASE-C ledger patch | registrar | **run** it; write it only |

The reviewer is the bottleneck: 75-100 min strictly serial, and it cannot start on a script before that script exists.
Take each READY the moment its script lands, never in a batch.

### PHASE B — LLM lane, strictly serial, after CHAIN DONE

| order | id | start condition | calls | cumulative / 14,000 | unblocks |
|---|---|---|---|---|---|
| B0 | dry-run + selftest confirmations | CHAIN DONE | 0 | 0 | every pilot below |
| B1 | BFCL-JUDGED-PILOT | B0 + committed READY | probe 100 → pilot 24 → run; 1,316 exp / 3,096 max | 1,316 | the "for Agents" sentence |
| B2 | IFEVAL-CHECKER-OUTPUT | B1 done | pilot 24 → run 814; 838 | 2,154 | the IFEval rung of the reference ladder |
| B3 | POT-REPOST-27 | B2 done **and** A11 resolved as authorised | 27 | 2,181 | the REF-FORM-BY-CELL yield line |
| B4 | TRACE-TRUNCATION | **not scheduled tonight** | (2,184) | (4,365) | deferred to 2026-09-24 |

### PHASE C

Post-run reviews (one per run), registrar outcomes, the LEAF-INTERACTION run if it was registered, the
INCONSISTENCIES scripted half, then **ONE** ledger patch v121 → v122 and `results_index.py --check`.

### Opportunistic overlap (the run-operator's call, not the manager's)

A judged run may start **inside a running SITE NULL step** if its expected duration fits the step's expected remainder
and the reviewer has certified by command that the script opens none of `twenty_newsgroups_cache_v1.db`,
`embeddings_cache.db`, `snapshots.db`, `mmlu_pro_dataset_cache_v2.db`. BFCL and IFEVAL-CHECKER-OUTPUT qualify;
POT-REPOST-27 does **not** (`pot_ref.py` L615 calls `pool_guard.assert_pool_of_record`). Never during a BUILD step.
Worst case is a bounded chain delay, never a corruption.

### Not scheduled, and why

- **ARENA-V3** — WITHDRAWN 2026-09-14 (programme L1944); no script and no cache were ever written; Amendment 9 (f)
  names it unauthorised; a pre-registered subset is refused by FRAMEWORK rule 14 ("never split to pass", L240).
- **Multi-corpus stage 3** — it is GEN-ARENA, and it already ran on 2026-09-13 (5,994 calls, REGISTERED FAIL).
- **Multi-SWE python language cell** — strict D_c 0.3283 / 0.4448 against the 0.95 enforcement bar; effective n ~85
  against the 120 floor; refused for judged rows by the record's own rule.
- **Canary pass 3** — `--pass` accepts only {1, 2}; it would need code and a registration for modest value.
- **MODEL-VINTAGE generation** — the author's cost and currency.


## Night 2026-09-25 (experiment-manager, MODE both, planning only)

| order | id | lane | cce | blocker |
|---|---|---|---|---|
| 1 | ARCH-V2-INDUCE-RUBRIC-3 | LLM | <=6 | builder -> READY |
| 2 | ARCH-V2-PILOT-K46 (k=37) | LLM | <=5,328 (cap 8,000) | INDUCE-3 re-pin + READY delta |
| a | G22-D-SIGNED-RULE | agent | 0 | none |
| a | VFC-RX-RULING, CANARY-ANALYZE-FIX, CANARY-SELFTEST-ASSERTS, CANARY-EPOCH2-LOW-ITEMS, TRACE-TRUNCATION-LOW-ITEMS | agent | 0 | none |
| a | ACCEPTED-LEDGER-LOCK | agent | 0 | registrar ledger quiet |
| a | BANNED-MODELS-REASON-CORRECTION | agent (worktree) | 0 | merge after pilot |
| a | JUDGEBENCH-CJB-SIDE (register + ingest) | agent | 0 tonight / ~1,300 next day | READY, next day cap |
| held | VIEWS-AUDIT-STAGE, EJ-RUBRIC-CORPUS-MATCH, SPLIT-DRAW-PROCESS-HYGIENE | - | 0 | move pilot/INDUCE-3 pins |
| held | G22-REAL-SUPPLY-RERUN | - | 0 | G22-D-SIGNED-RULE + new registration |
| no | GITIGNORE-AGENT, LEAF-INTERACTION | - | - | author / support |
