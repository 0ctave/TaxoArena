# Night schedule 2026-09-18 (research-lead; written 02:40, machine time verified by `date` = Fri Sep 18 02:34:57 2026)

Read-only planning pass: nothing was run, built, registered or edited except this file. Every state claim below
carries the command that showed it. Sources: docs/agents/CONTEXT.md; plans 2026-09-17_continual_capability_profile_leads.md
(§2 tiers A/B/C, §4 order) and 2026-09-17_anchor_free_redraw.md; leads 2026-09-17_judge_loop2.md (A9/A10 drafts) and
2026-09-18_agent_corpora.md (BFCL); docs/judge_v2_program.md L5334-5853 (registrations after L5334 and the batch-1
outcomes); ledger v113 stamp; FRAMEWORK.md "Tests to register before shipping" (L350-382) and "Limits" (L249-269).

## 0. State at 02:35, by command

| fact | command | result |
|---|---|---|
| item26 running, single-threaded | `powershell -NoProfile -Command "Get-Process -Id 20408 \| Select-Object Id,CPU,StartTime"` | PID 20408, CPU 5575 s over 93 min wall (one core), started 01:03:45 |
| its command line and how the exit line is written | `powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"ProcessId=20408\" \| Select-Object CommandLine"`, and the same for its parent 44396 | `python tools/analysis/item26_pooled.py --run`; the launcher appends `exit $?` to `experiment_results/x12_crossdomain/item26_pooled_run.log` when the process ends |
| item26 stage | `tail -n 5 experiment_results/x12_crossdomain/item26_pooled_run.log`; `ls -la --time-style=full-iso` on it | at stage (4): "first replicate 30.8 s -> ~154 min for B=300"; log mtime 01:05:17 -> bootstrap started ~01:04:46 -> stage 4 ends ~03:39; stages (5) power (3 x 1,000 sims) and (6) LOAO follow (minutes); the outcome file is written at the end (`ls experiment_results/x12_crossdomain/item26_pooled_outcome.txt` -> absent now) |
| no JVM at all (no daemon either) | `tasklist //FI "IMAGENAME eq java.exe"` | none |
| only one python process | `tasklist //FI "IMAGENAME eq python.exe"` | PID 20408 only |
| REDRAW chain state | `cat experiment_results/anchorfree/redraw/chain.log`; `ls -la experiment_results/anchorfree/redraw/` | R1 af_clean_s42 BUILD exit 0 at 20:14:16 (snapshot 20260917_201353_Headless_Run_Auto_ge, [SPLIT-CLOSURE] 171, leaves=82, slice 256 / dropTop 0 / whiten false); R1 SITENULL started 20:14:16, `af_clean_s42.sitenull.started` present, no `site_null_af_clean_s42.csv`, `sitenull_af_clean_s42.out` 0 bytes; R1c / R2 / R3 / R4 not started |
| chain resumes the null by itself | `sed -n '/^sitenull()/,/^}/p' tools/chains/anchor_free_redraw.sh` | marker without CSV -> "interrupted; restarting", output appended; a build whose `.build.out` exists is never retried |
| chain preflight refuses on a non-daemon java.exe; it does NOT check python | `sed -n '/^preflight()/,/^}/p' tools/chains/anchor_free_redraw.sh` | the wait on item26 must live in the night script |
| the five configs and the readout exist | `ls experiment_configs/anchorfree/redraw/ tools/analysis/anchor_free_redraw.py` | af_clean_s42, o0_clean_s42, af_s137, af_s2048, af_s42_o1; script present (commit 190cb48, reviewer READY / MERGEABLE) |
| redraw readout refuses on a missing null unless told | `sed -n 56,75p tools/analysis/anchor_free_redraw.py` | `--run` refuses on a missing manifest / CSV / readout; `--failed <arm>` and `--undetermined <arm>` are operator declarations (a morning decision if the chain's own `--run` is refused) |
| site-null durations on this machine | `grep -E "SITENULL\|BUILD" experiment_results/anchorfree/cert_chain.log experiment_results/anchorfree/cert_arm4.log` | builds 1.5-4 min; nulls at 256 d with 34-36 sites 20-24 min; at 512 d with 87 sites 68 min -> R1 (82 leaves, ~70 sites, 256 d) ~40-50 min; each of R1c / R2 / R3 / R4 ~40-50 min |
| every pinned script opens the pool DB | `grep -c assert_pool_of_record tools/analysis/{newcomer_placement,cap_gate_posthoc,profile_interval_all,profile_reliability,anchor_free_redraw,anchor_free_readout,foreign_gate_d4,x20_merged,canary_baseline}.py`; `sed -n 153,175p tools/analysis/pool_guard.py` | all >= 1; `assert_pool_of_record` opens mmlu_pro_dataset_cache_v2.db mode=ro -> every `--dry-run` of a pinned script is a pool reader under rule 7 |
| registrations pending | `grep -c <id> docs/judge_v2_program.md docs/test_ledger.html` for MODEL-VINTAGE-CANARY, AGENT-CORPUS-ADMISSION, PLACEMENT-CEILING, CAP-PRUNE, PROFILE-R-FILTERED, STABLE-CELL-SET, EMBED-AF, ARRIVAL-AF | 0 / 0 each: none registered, none in the ledger |
| registered, not recorded | `grep -n "ANCHOR-FREE-REDRAW\|ITEM-26-POOLED" docs/judge_v2_program.md`; `grep -o "<b>v113</b>[^<]*" docs/test_ledger.html` | REDRAW registered L4627 (no outcome, no ledger row); ITEM-26-POOLED registered L5458 ("not yet recorded" in the v113 note) |
| the interaction-only bracket | `grep -o "[^.]*interaction-only[^.]*\." docs/test_ledger.html` | "The MMLU-Pro interaction-only number was not computed and is left for the author"; PROFILE-RELIABILITY 0.9135 bracketed as model-demeaned, includes anchor difficulty |
| canary pass 2 | ledger CANARY-BASELINE row; FRAMEWORK L377 | refuses before 2026-09-22; 600 calls; registered, no go needed; NOT tonight |
| repo | `git rev-parse --short HEAD`; `git status --short \| grep -v '^??'` | 46f44e8; only the two standing local edits (.gitignore, config/application.yml) |
| Amendment 4 (re-judge rule) on disk | `grep -n "Amendment 4" docs/plan_2026-09-15.md` | L167 present (item26's RE-JUDGE-RULE half reads "on disk: yes") |

## 1. Inventory

Kinds: compute (machine, unattended) / registrar (text before code) / builder (script, dry-run only tonight) / reviewer (zero calls) / record (outcome, ledger, brackets).
"Reads the pool?" = opens mmlu_pro_dataset_cache_v2.db, snapshots.db or embeddings_cache.db (rule 7: none of it while a construction or a site null runs).

| id | state | kind | cost | reads the pool? | needs a go? | blocked by | who | when |
|---|---|---|---|---|---|---|---|---|
| ITEM-26-POOLED + RE-JUDGE-RULE | RUNNING (PID 20408) | compute | 0 calls; ~2.7 h on one core; ends ~03:50 +-15 min | yes (verdict caches + mmlu_pro cache, mode=ro, opened at start) | no | nothing | run-operator launched it; the night script waits on it | in flight |
| ITEM-26-POOLED post-run review | not started | reviewer | 0 | yes (recompute) | no | the `exit` line + the outcome file | adversarial-reviewer | morning (or after the chain ends; NEVER during it) |
| ITEM-26-POOLED outcome + ledger row + FRAMEWORK item 26 bracket | not started | record | 0 | no | no | review CONFIRMED | registrar | morning (ledger v114) |
| ANCHOR-FREE-REDRAW chain: R1 null restart, R1c, R2, R3, R4 | STOPPED, RESUMABLE (R1 built) | compute (4 constructions + 5 site nulls) | 0 calls; ~3.5-4 h; one JVM at a time | IS the exclusive owner of the pool while it runs | no | item26 exit AND zero non-daemon java.exe | run-operator via the night script | ~03:50 -> ~07:55 |
| REDRAW readout `anchor_free_redraw.py --run` | the chain's last step | compute | minutes | yes | no | all five arms complete; refuses on a missing null (then `--undetermined` / `--failed` is a morning decision) | the chain; else run-operator in the morning | end of the chain |
| REDRAW post-run review (counts from CSVs, Jaccard from snapshots.db, C1-C6, geometry = [SLICE], snapshots_frozen.db sha) | not started | reviewer | 0 | yes | no | SWEEP DONE | adversarial-reviewer | morning |
| REDRAW outcome, ledger row, brackets on ANCHOR-FREE / ANCHOR-FREE-CERT if F1 / F2 / F4 fire | not started | record | 0 | no | no | review | registrar | morning (v114) |
| CANARY-BASELINE pass 2 (C1) | registered; judged | compute (calls) | 600 calls | no | no (registered), but the script refuses before 2026-09-22 | the date | run-operator | 2026-09-22 or later |
| A9 MODEL-VINTAGE-CANARY (a definition) | drafted, not registered (judge_loop2.md §1) | registrar | 0 judge calls; contestant generation is the author's | no | the generation is the author's; the definition needs no go | closed-lines check | registrar | tonight (lane 2) |
| A10 AGENT-CORPUS-ADMISSION (a rule set) | drafted, not registered (judge_loop2.md §2) | registrar | 0 | no | no | closed-lines check | registrar | tonight (lane 2, first) |
| A10 pilot: BFCL-Result multi_turn download + checker-output ingest (800 entries x N agents) | not started; needs a new ingest script | builder + compute | 0 LLM calls; network; score files tens of MB, result files ~200 MB for 8 models | NO (a new DB under experiment_results/agent/; no pool_guard import) | no | the A10 registration commit (register before code) | engine-coder (script, worktree) -> run-operator (download + ingest + pilot readout) -> reviewer | tonight (lane 5) |
| A5 PER-ANCHOR BAND ATLAS (artefact) | plan-listed; an artefact, not a test | builder (arena-specialist) | 0 | yes (merged board caches via pool_guard) | no | the reviewer on its numbers | arena-specialist | morning / W2 |
| A6 PLACEMENT-CEILING | plan-listed, not registered | registrar -> builder -> reviewer | 0 | yes (newcomer_placement.db + pool_guard) | no | registration commit; dry-run in W1 or W2 only | registrar tonight; engine-coder tonight (worktree); reviewer pre-run on the code tonight, recompute in W2 | lanes 2 / 3 / 4 |
| A7 CAP-PRUNE | plan-listed, not registered | registrar -> builder -> reviewer | 0 | yes, and it reads snapshots.db, which the chain's builds WRITE | no | registration; dry-run strictly outside the chain | as A6 | lanes 2 / 3 / 4; dry-run in W1 only if it finishes before 03:45, else W2 |
| A8 STABLE-CELL-SET | plan-listed | registrar -> builder | 0 after B1 | yes | no | REDRAW's outcome (C5) | registrar | morning, after the REDRAW outcome (decision 4, §6) |
| A11 PROFILE-R-FILTERED | plan-listed, not registered | registrar -> builder -> reviewer | 0 | yes (x12 / x20 caches + pool_guard) | no | registration | as A6 | lanes 2 / 3 / 4 |
| A12 FOREIGN-GATE re-specification | plan-listed; design only | design text (no registration tonight) | 0 | no (text) | no | nothing | tree-construction-specialist | tonight if idle; else week 2 |
| PROFILE-RELIABILITY-INTERACTION (the MMLU-Pro interaction-only R named by the v113 bracket) | named by the bracket, not registered | registrar -> builder (small) -> reviewer | 0; minutes | yes (key rows + pool_guard) | no | registration | registrar tonight; engine-coder tonight; run in W2 | lanes 2 / 3 |
| B2 EMBED-AF, B3 ARRIVAL-AF | not registered | compute (builds) | 0 calls; ~35 min / ~1.5 h | constructions | the author's question 3 (09-17 plan §5) | REDRAW's outcome | - | not tonight |
| C2-C7 judged block | not registered | compute (calls) | 2,000-6,100 calls each | - | YES (author's go, not given) | the go | - | not tonight |
| Merges of lane-3 branches into main + full suite + Block 2 dry-runs | - | research-lead | a gradle-test JVM + pool readers | yes | no | MERGEABLE verdicts; SWEEP DONE (the test JVM is a non-daemon java.exe; the Block 2 dry-runs read the pool) | research-lead | morning, after SWEEP DONE |

Nothing tonight posts a judge call. Nothing tonight needs the author's go. The author's decisions that gate the next steps are in §6.

## 2. Dependency graph and lanes

```
item26 (running) --exit line--> [zero non-daemon java.exe] --> REDRAW chain: R1 null -> R1 readout -> R1c build/null/readout
      |                                                          -> R2 -> R3 -> R4 -> anchor_free_redraw.py --run -> SWEEP DONE
      |                                                                                                    |
      +-> morning: reviewer(item26) -> registrar outcome                          morning: reviewer(REDRAW) -> registrar outcome
                                                                                                    +-> A8 registration (needs C5)
lane 2 (registrar, text only, no pool): A10, A9, A6, A7, A11, PROFILE-RELIABILITY-INTERACTION
      |     each: closed-lines check -> append at the END -> git commit -- docs/judge_v2_program.md
      |                    |
      |                    +-> lane 5: bfcl_ingest.py (worktree) -> download + ingest (network, no LLM, no pool) -> pilot readout -> reviewer
      +-> lane 3: engine-coder worktrees for A6, A7, A11, INTERACTION; --dry-run / cache-reading --selftest ONLY in W1 or W2
                    +-> lane 4: adversarial-reviewer pre-run at zero calls (code reading + synthetic selftests any time; cache recomputation only in W1 / W2)
```

Windows for pool readers (every `--dry-run` of a pinned script is one, through `pool_guard.assert_pool_of_record`):
- W1 = now until the night log prints `CHAIN LAUNCH` (~03:50). Python readers beside item26 are allowed: rule 7 forbids readers during a CONSTRUCTION, not beside another reader.
- CLOSED = from `CHAIN LAUNCH` to `NIGHT DONE` (~03:50 -> ~07:55). No python that imports pool_guard, no gradle task, no sqlite shell on mmlu_pro_dataset_cache_v2.db / snapshots.db / embeddings_cache.db. Coding in worktrees, reading files, committing docs and scripts are fine.
- W2 = after `NIGHT DONE` (tail the night log). Everything queued in lanes 3 / 4 that opens a cache runs then, serially.
Always safe: lane 5 (a new DB under experiment_results/agent/, network only; the ingest script must not import pool_guard or open any DB of record).

### Lane 1: compute, unattended (the night script, §4)
1. Wait for `^exit` in `experiment_results/x12_crossdomain/item26_pooled_run.log` (poll 60 s) and for PID 20408 to be gone.
2. Wait for zero non-daemon java.exe (the Gradle daemon excluded; none exists now).
3. `bash tools/chains/anchor_free_redraw.sh` (resumable: R1's build is skipped, R1's null restarts, then R1c, R2, R3, R4, then the redraw readout).
4. Log `NIGHT DONE` with the per-arm null presence, the tracked-change list, the snapshots_frozen.db sha, and whether `anchor_free_redraw_outcome.txt` exists (absent = the chain's `--run` was refused; the morning declares `--failed` / `--undetermined`).
Nothing else touches a JVM or the pool between steps 3 and 4.

### Lane 2: registrar, tonight (text before code; one commit per registration; `git commit -- <paths>` because the index is shared)
Order: A10, A9 (registrar-ready text in leads/2026-09-17_judge_loop2.md §2 and §1: copied as the registration body under the standard header "Registered 2026-09-18 (before any code or call) - <ID>: <question> (zero calls; plan A9 / A10; lead judge_loop2.md §n)", with the closed-lines line and the falsifier as drafted), then A6, A7, A11, PROFILE-RELIABILITY-INTERACTION from the briefs in §3. Each: the closed-lines grep (ledger and programme for the id and its subject; CONTEXT §5), criteria in scorable terms, predictions as numbers, a falsifier naming what it overturns, cost 0 stated, the hygiene line (caches mode=ro; pool named by id; both conventions where a board is read; wrong(established)). The A10 registration names the pilot's corpus and file of record (§3). Each commit lands BEFORE the matching engine-coder brief is launched. A8 is not registered tonight (decision 4). No ledger patch tonight: rows follow outcomes; v114 is one morning commit.

### Lane 3: script builds, dry-run only (engine-coder, one worktree per script; branches stay unmerged tonight)
- `tools/analysis/placement_ceiling.py` (A6): reads `experiment_results/x12_crossdomain/newcomer_placement.db` only (assert the cache basename); the band decomposition and the 100 / 200 / 300 / 400 resolution curve; `--dry-run` prints the pool id, the row counts and the two newcomers' match counts, no number; `--selftest` on synthetic boards; `--run` write-once to `experiment_results/x12_crossdomain/placement_ceiling_outcome.txt`.
- `tools/analysis/cap_prune.py` (A7): cap_gate_posthoc's per-site LOMO gains on af/seed_42 plus the two columns CAP-GATE left in scratch (within-site null p95 on the train side; the tree's held-out side minus p2dca, 2,193 q); the keep rule; Jaccard with the certified 16; `--dry-run`, `--selftest`, `--run` write-once to `experiment_results/anchorfree/cap_prune_outcome.txt`. It reads snapshots.db: dry-run in W1 only if before 03:45, else W2.
- `tools/analysis/profile_r_filtered.py` (A11): PROFILE-INTERVAL-ALL's estimator on the merged board restricted to disagreeing matches; q_distinct per anchor; R only; `--dry-run`; `--run` write-once to `experiment_results/x12_crossdomain/profile_r_filtered_outcome.txt`.
- `profile_reliability.py --interaction-only` (PROFILE-RELIABILITY-INTERACTION): one flag, inert when absent (the default path byte-identical; a test that pins the default output on a synthetic table); model- and anchor-demeaned split-half R with the jackknife interval on the 46-model key over the 14 anchors of p2dca21ab5f4ef3ae; write-once to `experiment_results/x12_crossdomain/profile_reliability_interaction_outcome.txt`.
Each builder hands to the reviewer. Merges are mine in the morning after MERGEABLE, then `.\gradlew.bat test --offline` in the main checkout (a JVM: W2 only), then the Block 2 dry-runs (pool readers: W2 only).

### Lane 4: pre-run reviews (adversarial-reviewer, zero calls)
Per lane-3 branch: the flag is inert when absent; no DB of record is opened for writing; `--dry-run` prints the pool id first and no outcome number; the selftest plants and recovers; denominators named; the write-once guard. Code reading and synthetic selftests at any time; any recomputation that opens a cache waits for W1 (before 03:45) or W2. Verdicts READY (script) / MERGEABLE (branch) go into the review file under docs/reviews/ (the reviewer writes; nothing of record is edited).

### Lane 5: BFCL download + ingest (network, no LLM, no pool); blocked only by the A10 commit
1. registrar commits A10 (lane 2, first).
2. engine-coder (worktree): `tools/ingest/bfcl_ingest.py`. Inputs: BFCL-Result `2025-12-16/result/<model>/multi_turn/BFCL_v4_multi_turn_{base,miss_func,miss_param,long_context}_result.json` and `2025-12-16/score/<model>/multi_turn/*_score.json` for 8 models (candidates from the survey: claude-sonnet-4-5-20250929-FC, gpt-5.2-2025-12-11, gemini-2.5-flash, DeepSeek-V3.2-Exp-FC, Qwen_Qwen3-32B-FC, grok-4-1-fast-reasoning-FC, Llama-3.3-70B-Instruct-FC, xLAM-2-70b; the list is the author's to confirm, decision 5), plus the gorilla dataset `BFCL_v4_multi_turn_*.json` and `possible_answer/` for the stems. Output: a NEW `experiment_results/agent/bfcl_result_2025-12-16.db` (verify first with `git check-ignore -v experiment_results/agent/bfcl_result_2025-12-16.db` that an existing cache pattern ignores it; .gitignore is never committed) with tasks(id, family_id = base index, category, stem_sha, split_side under SplitSide norm-v1 with the family wholly on one side), episodes(task_id, agent, steps, cap_hit = force-terminated at the 20-step cap, decoded call sequence, final-state text), checker(task_id, agent, valid, error_text = the normalised OUTPUT, checker_sha) and provenance(archive commit sha, download time, file shas). The pass/fail vector = all ids minus the score file's failures, asserted against the score file's line-1 `total_count` / `correct_count`. `--dry-run` lists files and counts, writes nothing; `--run` downloads to `experiment_results/agent/raw/bfcl_result_2025-12-16/` then ingests. No pool_guard import; no DB of record opened.
3. run-operator: `--dry-run`, `--run`, then the A10 pilot readout as registered: 300 episodes question-stratified over the 4 categories x >= 3 agents, strict D_c with Wilson intervals per stratum and pooled, cap-hit share per agent, the 50-row extractor reproduction >= 0.98; write-once to `experiment_results/agent/bfcl_admission_pilot.txt`.
4. adversarial-reviewer recomputes D_c per stratum from the raw score files independently; registrar records the pilot outcome in the morning (v114).
Prediction of record (A10 as drafted): strict D_c < 0.95 in at least half the strata (long_context first); judged cells PREDICTIVE-ONLY on day one; key-built rows publishable on terminated episodes.

## 3. Registration briefs for lane 2 (the registrar writes each as its own section at the END of docs/judge_v2_program.md)

A6 PLACEMENT-CEILING (plan A6; lens arena_profile.md L5). Question: is the newcomer band (7 and 3 key tiers at 400 matches, NEWCOMER-PLACEMENT-LIVE) a key-tie band or a budget band? Instrument: newcomer_placement.db as the single source (assert the basename); per newcomer the band width decomposed into (i) positions inside a key-tie cluster (0.017 gap), (ii) positions inside the frontier band, (iii) positions the arena could have separated at nominal power; subsamples of 100 / 200 / 300 of the bought 400 (question-stratified, B >= 300) for the resolution curve. Criteria: (C1) the decomposition sums to the band width per newcomer under both conventions; (C2) the resolution curve at 100 / 200 / 300 / 400 with intervals. Predictions: sonnet's width entirely (i) + (ii); gpt-4o-mini's 3 tiers = the 0.631 / 0.629 / 0.628 cluster plus one each side; budget narrows at most 1 tier from 100 to 400. Falsifier: (iii) >= 2 tiers for either newcomer (then budget is the band and C6 PLACEMENT-CURVE is worth its 3,200 calls). Cost 0. Closed lines: the frontier stays one band (no order); no sub-anchor row.

A7 CAP-PRUNE (plan A7; lens cells.md L4). Question: does a capability rule that survives as a held-out-replicating PRUNE keep only the trunk? Instrument: cap_gate_posthoc's per-site LOMO gains on af/seed_42; keep a site iff its gain > its own within-site null p95 on the train side AND > 0 on the tree's held-out side minus p2dca (2,193 q, count printed); the script writes the null and held-out columns CAP-GATE left in scratch (programme L5117). Criteria: (C1) the survivor count with both columns per site; (C2) Jaccard with the certified 16. Predictions: 4-6 survivors; Jaccard ~0.25. Falsifier: survivors <= 4 closes the capability-gated construction line at zero builds. Never a gate (FRAMEWORK L53). Cost 0. Closed lines: ANCHOR-FREE-CERT closed construction levers for certification; this is a post-hoc prune readout, no build.

A11 PROFILE-R-FILTERED (plan A11; lens arena_profile.md L4). Question: does the anchor profile's reliability survive the answer-disagreement filter that halves the newcomer bill (FRAMEWORK L405 names it untested)? Instrument: PROFILE-INTERVAL-ALL's split-half estimator with the jackknife interval on the merged board (x12 + x20 = 21,536 verdicts; pool p2dca21ab5f4ef3ae) restricted to matches whose extracted answers disagree; q_distinct per anchor; R only (the filtered theta scale is 13% wider, PLACEBO-ENTRY). Criteria: (C1) board R filtered vs unfiltered with intervals; (C2) the per-anchor class under the filter beside PROFILE-INTERVAL-ALL C2. Predictions: board R within 0.05 of the unfiltered 0.7183; no anchor moves more than one class step; >= 3 anchors fall under the support rule (q_distinct < 120) and read UNDETERMINED. Falsifier: board R < 0.60 (the filter destroys the profile; the newcomer bill cannot be halved). Cost 0.

PROFILE-RELIABILITY-INTERACTION (the v113 bracket; 09-17 plan §1 correction). Question: what is the MMLU-Pro key-built profile reliability once anchor difficulty is removed, i.e. the interaction-only (model- and anchor-demeaned) split-half R on the 46-model key over the 14 anchors? Instrument: profile_reliability.py's estimator under a `--interaction-only` flag (inert when absent), the jackknife interval, ~201 q/cell; a no-interaction null (Bernoulli(logistic(a_m - d_c)) fitted from the real table) printed beside, as PROFILE-INTERVAL-ALL-UNION did. Criteria: (C1) the number with its interval; (C2) the null. Predictions: interaction-only R 0.78-0.88 (the union fell 0.9424 -> 0.8537); above the 0.70 bar; the no-interaction null <= 0.90. Falsifier: interaction-only R < 0.70 (the MMLU-Pro profile is a re-indexed global score; PROFILE-RELIABILITY's row takes the bracket and the atlas's key-built rows carry "offset, not order"). Cost 0, minutes.

A9 and A10: the text in leads/2026-09-17_judge_loop2.md §1 and §2 is registration-ready; the registrar adds the header, the closed-lines line (none reopened: no rubric, no specification reference, no gating, no trajectory reference, no judge temperature), and for A10 the pilot's file of record `experiment_results/agent/bfcl_admission_pilot.txt` and the corpus: BFCL-Result 2025-12-16 multi_turn (800 entries, 4 categories, family_id = base index, 20-step cap; survey 2026-09-18_agent_corpora.md §1.5).

## 4. Compute lane: exact commands and the night script

Manual equivalents (the run-operator may run these by hand; the script below sequences them):
```
# 1. wait for item26 (poll every 60 s; the launcher appends "exit <rc>" to the log when the process ends)
until grep -q '^exit' experiment_results/x12_crossdomain/item26_pooled_run.log; do sleep 60; done
tail -n 3 experiment_results/x12_crossdomain/item26_pooled_run.log        # expect "[ITEM-26-POOLED] written to ..." then "exit 0"
ls -la experiment_results/x12_crossdomain/item26_pooled_outcome.txt
tasklist //FI "PID eq 20408"                                               # expect no python.exe
# 2. zero non-daemon java.exe
powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count"   # expect 0
# 3. the registered chain (resumable: R1 build skipped, R1 null restarted, then R1c, R2, R3, R4, then anchor_free_redraw.py --run)
bash tools/chains/anchor_free_redraw.sh
# 4. after SWEEP DONE
tail -n 12 experiment_results/anchorfree/redraw/chain.log
ls experiment_results/anchorfree/redraw/anchor_free_redraw_outcome.txt     # absent => the chain's --run was refused; see anchor_free_redraw.log; the morning declares --failed / --undetermined
git status --short | grep -v '^??'                                          # only .gitignore and config/application.yml
```

`tools/chains/night_2026-09-18.sh` (the run-operator creates it with this content and launches it; resumable: a re-run after a kill takes the same path and the chain skips what exists):
```bash
#!/usr/bin/env bash
# Night 2026-09-18: item26 (running) -> ANCHOR-FREE-REDRAW chain (resumable) -> readout. Zero judge calls.
# Plan: docs/agents/plans/2026-09-18_night_schedule.md §4. Rule 7: the chain starts only when nothing reads the pool
# (item26 has exited) and no non-daemon java.exe is alive. Resumable: re-run after a kill; every step is skip-if-done.
# Launch (Git Bash, repo root):  (bash tools/chains/night_2026-09-18.sh > experiment_results/anchorfree/redraw/night_2026-09-18.out 2>&1 &)
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8
R=experiment_results/anchorfree/redraw
I26=experiment_results/x12_crossdomain/item26_pooled_run.log
I26OUT=experiment_results/x12_crossdomain/item26_pooled_outcome.txt
LOG=$R/night_2026-09-18.log
PIDF=$R/night_2026-09-18.pid
mkdir -p "$R"
log() { local m="[$(date +%H:%M:%S)] $*"; echo "$m"; echo "$m" >> "$LOG"; }
busy_jvm() {
  powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count" 2>/dev/null | tr -d '[:space:]'
}
# single instance
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then log "another night script is alive (pid $(cat "$PIDF")); refusing"; exit 1; fi
echo $$ > "$PIDF"
log "NIGHT start HEAD $(git rev-parse --short HEAD) | item26 log $I26 | chain tools/chains/anchor_free_redraw.sh"

# ---- 1. wait for item26 (its launcher appends 'exit <rc>' to the log when the process ends) --------------------
if [ -f "$I26" ] && grep -q '^exit' "$I26"; then
  log "item26 already ended: $(grep '^exit' "$I26" | tail -1)"
else
  log "waiting for item26: poll '^exit' in $I26 every 60 s (stage 4 ETA ~03:40, then power + LOAO)"
  while ! grep -q '^exit' "$I26" 2>/dev/null; do sleep 60; done
  log "item26 ended: $(grep '^exit' "$I26" | tail -1) | $(grep -c . "$I26") log lines"
fi
# belt and braces: the python process itself must be gone (it held the caches open)
while tasklist //FI "PID eq 20408" //NH 2>/dev/null | grep -qi python.exe; do log "PID 20408 still alive after the exit line; waiting 30 s"; sleep 30; done
if [ -f "$I26OUT" ]; then log "item26 outcome present: $I26OUT ($(wc -l < "$I26OUT") lines); NOT read here; morning: reviewer, then registrar"
else log "item26 outcome ABSENT ($(grep '^exit' "$I26" | tail -1)); morning: read the log; do NOT re-run blindly (write-once)"; fi

# ---- 2. no non-daemon JVM ----------------------------------------------------------------------------------------
n=$(busy_jvm); while [ -n "$n" ] && [ "$n" != "0" ]; do log "$n non-daemon java.exe alive; waiting 60 s"; sleep 60; n=$(busy_jvm); done
log "no non-daemon JVM; no python of record; CHAIN LAUNCH (pool readers are CLOSED from here to NIGHT DONE)"

# ---- 3. the registered chain (resumable; strictly serial; all five arms regardless) -----------------------------
bash tools/chains/anchor_free_redraw.sh >> "$R/chain_stdout.log" 2>&1
rc=$?
log "chain exit $rc"

# ---- 4. summary for the morning (no number of record is read here) ---------------------------------------------
if grep -q 'SWEEP DONE' "$R/chain.log"; then log "SWEEP DONE seen in $R/chain.log"; else log "SWEEP DONE NOT seen: chain interrupted; re-run this script (resumable)"; fi
for a in af_clean_s42 o0_clean_s42 af_s137 af_s2048 af_s42_o1; do
  if [ -f "$R/site_null_$a.csv" ]; then
    ro=ABSENT; [ -f "$R/anchor_free_${a}_readout.txt" ] && ro=present
    log "$a: site null present ($(grep -c . "$R/site_null_$a.csv") lines); readout $ro"
  else log "$a: site null ABSENT (UNDETERMINED unless the morning decides otherwise)"; fi
done
if [ -f "$R/anchor_free_redraw_outcome.txt" ]; then log "REDRAW outcome written: $R/anchor_free_redraw_outcome.txt"
else log "REDRAW outcome ABSENT: the chain's --run was refused or not reached; see $R/anchor_free_redraw.log; the morning declares --failed / --undetermined per arm"; fi
log "tracked changes: $(git status --short | grep -v '^??' | tr '\n' ' ')"
log "snapshots_frozen.db sha256: $(sha256sum snapshots_frozen.db 2>/dev/null | cut -c1-16)"
log "non-daemon JVMs now: $(busy_jvm) | python.exe: $(tasklist //FI 'IMAGENAME eq python.exe' //NH 2>/dev/null | grep -ci python.exe)"
log "NIGHT DONE; pool readers OPEN (W2)"
rm -f "$PIDF"
exit 0
```
Launch, from the repo root in Git Bash (the same detach pattern that kept item26 alive after its launcher returned):
`(bash tools/chains/night_2026-09-18.sh > experiment_results/anchorfree/redraw/night_2026-09-18.out 2>&1 &) ; sleep 5; tail -n 3 experiment_results/anchorfree/redraw/night_2026-09-18.log`
Progress: `tail -f experiment_results/anchorfree/redraw/night_2026-09-18.log` and `tail -n 5 experiment_results/anchorfree/redraw/chain.log`.
Kill (only if the author asks): kill the bash pid in `night_2026-09-18.pid`, then the running java.exe. A site null killed mid-way leaves its marker and restarts on resume; a build killed mid-way leaves `.build.out` and is recorded as the arm's result, never retried, so do not kill inside a "BUILD start" window (the 2-4 min after that line in chain.log).

## 5. Timetable 02:45 - 09:00 (machine clock; +-15 min on item26, +-30 min on the chain)

| time | lane 1 compute | lane 2 registrar | lane 3 builders (worktrees) | lane 4 reviewer | lane 5 BFCL |
|---|---|---|---|---|---|
| 02:45 | run-operator creates and launches the night script; it waits on item26 (stage 4 bootstrap, ETA 03:40) | A10: closed-lines check, registration text, commit | - | - | - |
| 03:00 | item26 bootstrapping (one core) | A9 -> commit; A6 -> commit | engine-coder: A6 placement_ceiling.py (worktree); its dry-run is allowed now (W1) | reads A6 code as it lands | after the A10 commit: engine-coder bfcl_ingest.py (worktree); `--dry-run` (lists files; nothing written) |
| 03:30 | item26 stage 4 ends ~03:39; stages 5-6 (minutes) | A7 -> commit; A11 -> commit | A7 cap_prune.py; its dry-run ONLY if it can finish before 03:45, else W2 | A6 pre-run review (code + synthetic selftest) | run-operator: bfcl_ingest `--run` (download raw, ingest into the new DB) |
| 03:50 | item26 `exit`; outcome file written; the night script sees zero JVMs -> CHAIN LAUNCH; R1's site null restarts (~45 min) | PROFILE-RELIABILITY-INTERACTION -> commit | POOL CLOSED: coding only; `--selftest` on synthetic data only | code reading only | ingest running (no pool); the pilot readout once the DB is complete |
| 04:35 | R1 readout; R1c build (3 min), then its null (~40 min) | done: six registrations committed; no ledger patch | A11 profile_r_filtered.py; the interaction flag on profile_reliability.py | A7 / A11 code reviews | reviewer recomputes D_c from the raw score files (no pool) |
| 05:20 | R2 build + null (~50 min) | - | branches complete in their worktrees; MERGEABLE requested | interaction-flag review (default path byte-identical: diff of the default output on a synthetic table) | pilot text written (write-once) |
| 06:10 | R3 build + null | - | idle | idle | idle |
| 07:00 | R4 build + null | - | - | - | - |
| 07:50 | `anchor_free_redraw.py --run` (minutes); SWEEP DONE ~07:55; NIGHT DONE; W2 opens | - | - | - | - |
| 08:00 | machine otherwise idle (W2): the queued dry-runs and cache selftests of A6 / A7 / A11 / INTERACTION, then their `--run` (minutes each), serially, by the run-operator | - | - | recomputation against the caches | - |
| 09:00 | the author returns: nothing running (`tasklist` shows no python.exe and no java.exe beyond the daemon); morning checklist §7 | | | | |

If item26 overruns by an hour the chain ends ~09:00; nothing else changes, because every W2 step waits for `NIGHT DONE`. If the author returns while the chain runs: do not open a cache, do not run gradle, do not kill inside a "BUILD start" window; the chain is resumable.

## 6. Decisions that were the author's (taken by precedent tonight; reversible before the morning's commits)

1. The chain restarts R1's site null unattended (its own "interrupted; restarting" branch) instead of waiting for an operator decision; the interrupted attempt is logged and appended, nothing overwritten.
2. If an arm's null does not complete, the chain's `--run` is refused and the `--undetermined` / `--failed` declarations are made in the morning by the run-operator with the reviewer watching, never by the night script.
3. Lane 2 registers six tests tonight from existing drafts and briefs (A10, A9, A6, A7, A11, PROFILE-RELIABILITY-INTERACTION); each is a zero-call test or a rule; no ledger patch until outcomes exist (one v114 patch in the morning).
4. A8 STABLE-CELL-SET is NOT registered tonight: its object (the re-draw-stable set) is defined by REDRAW's C5 and the morning's outcome may make it void. Registering it before seeing the CSVs would be the blinder choice; if the author prefers that, the registrar files it in the morning BEFORE the reviewer opens the REDRAW CSVs, with a "void if C5 FAILED" clause.
5. The BFCL pilot uses 8 agents (the survey's (f) threshold) rather than A10's minimum of 3, on the 2025-12-16 archive; the exact model list is the author's to confirm before any judged spend; nothing judged is scheduled on it.
6. A5 (band atlas) and A12 (FOREIGN-GATE re-spec) are not scheduled tonight: A5 needs the pool (W2) and the reviewer; A12 is design text with nothing to gate until B3.
7. No merge into main tonight: merges need the reviewer's MERGEABLE, the full suite (a JVM) and the Block 2 dry-runs (pool readers); all three are W2 or morning.
8. B2 / B3 and every judged test stay unscheduled (the author's questions 2 and 3 in the 09-17 plan §5; canary pass 2 refuses before 2026-09-22).

## 7. Morning checklist (the author and the record agents, in order)

1. State: `tail -n 15 experiment_results/anchorfree/redraw/night_2026-09-18.log` (expect NIGHT DONE); `tasklist //FI "IMAGENAME eq java.exe"` (daemon only, or none); `tasklist //FI "IMAGENAME eq python.exe"` (none); `git status --short | grep -v '^??'` (the two standing edits only); `sha256sum snapshots_frozen.db` equal to the chain log's line.
2. item26: `tail -n 40 experiment_results/x12_crossdomain/item26_pooled_outcome.txt` (C1-C4, predictions, falsifier, RE-JUDGE-RULE "on disk: yes"). Note already visible in the run log at stage (3): pooled delta-deviance 6.51 (b1 +2.44, b2 -0.09, 46 events on 1,620 pooled established edges) - C1 HELD if it stands, but the registered prediction band was 3.5-5.5, so the prediction is scored FAILED in the interesting direction (stronger identification than predicted), and b2 is inside the registrar's [-1, +1]. The adversarial-reviewer recomputes from the two caches independently: the pooled delta-deviance, the bootstrap interval and the share >= 3.84, power at ~26 / ~52 events, LOAO per draw and pooled, utility. Then the registrar writes the outcome at the END of the programme, brackets FRAMEWORK item 26 (L382) and the Limits L253-254 if C1 HELD (b1 identified on pooled established labels for the shipped judge; calibration status still by the power rule), and the ledger row.
3. REDRAW: if `anchor_free_redraw_outcome.txt` is absent, run-operator reads chain.log and anchor_free_redraw.log, declares `--failed` / `--undetermined` per arm as the logs dictate, and runs `python tools/analysis/anchor_free_redraw.py --run [--failed ARM] [--undetermined ARM]`. adversarial-reviewer: certified counts from the five CSVs, the Jaccard table from snapshots.db, the category sides, C1-C6 and every prediction's HELD / FAILED, each null's geometry = the build's [SLICE] line, no tracked DB changed. registrar: outcome, ledger row, brackets on ANCHOR-FREE / ANCHOR-FREE-CERT if F1 / F2 / F4 fire. research-lead: synthesis; the author's question 3 (continue the anchor-free line with B2 / B3, or stop).
4. A10 pilot: `cat experiment_results/agent/bfcl_admission_pilot.txt`; the reviewer's independent D_c; registrar outcome.
5. Lane 3 branches: reviewer verdicts in docs/reviews/; research-lead merges the MERGEABLE ones, then `.\gradlew.bat test --offline` in the main checkout (the two known environmental failures are worktree-only), then the Block 2 dry-runs; then run-operator runs A6 / A7 / A11 / INTERACTION `--run` serially; reviewer on the numbers; registrar outcomes.
6. Ledger v114 in ONE patch: ITEM-26-POOLED, ANCHOR-FREE-REDRAW, the A10 pilot, and whichever of A6 / A7 / A11 / INTERACTION completed with a review; bracket the v113 note's "ITEM-26-POOLED not yet recorded" by insertion.
7. Register A8 if the author wants it (decision 4); write the registrations for C2, C3, C4 (not run) so the judged block can start the day the go is given; canary pass 2 on or after 2026-09-22.
8. Update the memory resume note (in-flight-2026-09-10.md) to the new state: NOTHING RUNNING, ledger v114, HEAD <sha>.

## Morning additions (03:20, orchestrator)
- CAP-PRUNE before --run (W2): registrar brackets (a) the site-id transcription errors in CAP-GATE's outcome / review (n00000163 -> n00000164 as the replicating depth-5 site; n00000124 / n00000126 -> n00000125 / n00000127 as the sign-flipping depth-4 sites; reviewer to confirm from scratchpad/review_capgate/report3_af.out), (b) R1's literal id so the trunk criterion is scored on the intended site, (c) the builder's disclosure (it saw the checker's scratch per-site columns; the instrument and the e803cf4 predictions are unchanged; the record must carry that P1 is scored with this knowledge state known). Then `python tools/analysis/cap_prune.py --run`, reviewer, registrar.
- BFCL pilot: independent labeller (adversarial-reviewer) fills experiment_results/agent/bfcl_admission_pilot_labels.csv from the raw files BEFORE --run; then `python tools/analysis/agent_admission_pilot.py --run`; registrar bracket for the proxy-vs-marker disagreement (6 of 6,400) and the last-turn cap (13 episodes).
