# Queue re-rank, 2026-10-04 (experiment-manager; MODE status + plan, local-only; zero calls)

Inputs: KNOWLEDGE.md; queue.json (215 items: 131 done, 84 not done/declined); checkpoint H digest; memo v3 §2-§5.
Nothing launched, queue.json NOT edited (brief: "edit nothing else"); the registrar should copy the states below.

## STATE (verified)
- `tasklist | grep -ciE "java|python"` = 0 and `Get-CimInstance Win32_Process` (java|python) = empty: NO run is alive.
- So the queue's `running` entries are STALE: ARCH-V2-G22 (last 2026-09-27), THREAD-CAP (09-29), G17-CANARY (10-02; pass 5 not before 10-08). Registrar to restate them (paused/done) from their logs.
- Last recorded: COVERAGE-AUDIT VALID (216abff1). No pool reader alive: a rule-7 machine slot is open now.

## (a) Zero-call, no author gate (ranked: thesis value per cost; cost is the queue's, "~" = mine, unpriced)
| # | id | SQ / value | cost | pool reader | needs first |
|---|---|---|---|---|---|
| 1 | FLAT-MIX-ANCHORED | SQ3 (memo change 1/4): anchors vs construction as the source of partition quality; directly answers the anchored-tree correction | minutes CPU | yes (machine slot) | registration (registrar) + READY |
| 2 | CERT-ALIGN-SIZE | SQ3 certificate (change 10) by size; DESCRIPTIVE-ONLY on 20NG | 5-12 m | no | registration |
| 3 | DEFF-ATLAS | SQ2/SQ4: measured DEFF per cache, the support floor every interval in the drafts leans on | 1.5-3 h | yes | registration; cache-fitness pass |
| 4 | INCONSISTENCIES-PASS | submission hygiene: record self-consistency before the drafts are lifted | 45-60 m + 45-60 m | yes (ledger patch) | none |
| 5 | REF-LADDER-RECOMPOSE | SQ2: reference ladder from existing caches (wording: not a new reference variant) | 20-40 m | yes | registration |
| 6 | BAND-INTERVAL | SQ2/SQ4 intervals | 1-2.5 h | yes | registration |
| 7 | SB-LENGTH / SEQ-LOOKS | SQ2 length bias / sequential-look correction (small) | 1-5 m each | yes | registration |
| 8 | MULTISWE-CORRECTIONS / SUPPORT-PLAN | SQ1 agentic external validity / framework #7 | 10-20 m each | no | registration |
| 9 | CDS-SPOTCHECK | SQ3 certificate stream D5/D6/D8 closure | ~10 x 60 s rebuilds + 2 sha passes | CONSTRUCTION (exclusive) | none |
| 10 | DATASET-SURVEY (built) | SQ1 second keyed corpus admission table | minutes | no | review only |
| 11 | CANARY-ANALYZE-FIX (READY) | SQ4 gate for any future epoch | 20-30 m | selftest = phase B | none |
| 12 | ONLINE threshold calibration (unregistered, memo §5) | SQ3 online: catch-rate trigger | ~1 h CPU | yes | registration |

Hygiene (engineering, zero-call): WORTH DOING BEFORE SUBMISSION (they protect numbers in the text):
JOIN-CARDINALITY-GUARD, RUBRIC512-ROUTING-DECIMAL-COMMA, STRICT-BOOLEAN-PARSE, PARETO-NOISE-FLOOR,
GMM-RESIDUE-CLEANUP, TRACE-TRUNCATION-LOW-ITEMS, CERT-RES-SELFTEST-GAPS, MIX-FLAT-SELFTEST-GAPS,
SES-INSTRUMENT-EXCEEDANCE-BASERATE, EMBEDDER-PLUMBING (built; SQ5 embedder identity), GRADLE-TEST-INPUTS.
DECLINE (forward-only, process, or on the stopped ARCH-V2 lane; no thesis number depends on them):
ARCH-V2, ARCH-V2-E-D/E-J/E-A/E-T, ARCH-V2-G22, ARCH-V2-INDUCE-SELECT-1, G22-D-SIGNED-RULE, G22-REAL-SUPPLY-RERUN,
EJ-RUBRIC-CORPUS-MATCH, INDUCE-RUBRIC-1-L1/L4/L5, RR-PROVENANCE-FIELDS, ARCHV2-SELFTEST-CLOCK-TRAP (lane stopped at
G10 FAILED, 2026-10-01); EPOCH-GROWTH (defer); CANARY-D10-RUNG-ABANDONED, ACCEPTED-LEDGER-LOCK, CANARY-SELFTEST-ASSERTS,
CANARY-EPOCH2-LOW-ITEMS, KOTLIN-AUDIT-MERGE, REGENERATE-SPLIT-REFUSAL, EFFECTIVE-CONFIG-ARMS, STACK-JUDGE-RO-CACHE,
TP20-CHAIN-FAIL-CLOSED, PIN-KIND-AUDIT, POOL-GUARD-IDFILE-ENTRY, SB-SIDEFILES-REGEN, STATUS-WORD-UNIFY,
SES-ROUTE-HOOK-FS-EVENTS, RULE7-PROCLIST-RECORD, SPLIT-DRAW-PROCESS-HYGIENE, VIEWS-AUDIT-STAGE, VFC-HARNESS-V5-HARDENING,
CK-CLOSE-V1-IMPL (only if no new data is built before submission). Close as done: NEARDUP-AUDIT (UNDETERMINED recorded),
POT-REPOST-27 (closed-already-done), E1-REPLICATES (withdrawn).

## (b) Waiting on an author decision
- GITIGNORE-AGENT: ignore experiment_results/agent/* (unblocks BFCL-BUILD, BFCL-READY, BFCL-LENGTH-POSITION, BFCL-GUARD-FULL-PAYLOAD; R6/R7).
- REPORT-BACKGROUND-ACCEPTANCE-TEXT, REPORT-FIXED-POINT-SCOPE: thesis wording.
- SUPPORT-FLOOR-CHECKER: adopt as a FRAMEWORK stage (memo change 7).
- LEAF-INTERACTION: the word to register; also blocked: support (87 leaves vs 120-190-question floor).
- THREAD-CAP: standing adoption and form of the cap. LOADER-OPTIONS-KEY: loader review. READY-TEMPLATE-TRANSPORT: standing rule.
- SUPERGPQA-STAGE0: disk (~4.3 GB) and DATASET-SURVEY admits. FITSET stage 1: decline (research-lead's view).
- D2 (gates RP19, G21-RESCOPED), D6 (SQ3 wording), memo v3 adoption, git-history rewrite of 66fedf63 before any push.
- INGEST-TRACE-KEYS-REPAIR: decided; waits on the CJB pilot.

## (c) Paid (not schedulable local-only)
| id | calls | 4k-match rule |
|---|---|---|
| JUDGEBENCH-CJB-SIDE (READY) | <= 8,470 cce, 350 items dual order (~700 judge calls + ingest) | under; go given 2026-09-25 |
| G21-RESCOPED | <= ~4,050 matches + <= 1,000 reasoning solves (<= ~14k cce) | AT/OVER the line: go D1 given, waits D2 |
| G17-CANARY pass 5 | ~1.8k matches | under; not before 2026-10-08 |
| BFCL-DEGRADED-CONTROL (deferred) | 324 cce | under |
| SLOTSWAP-DECISION data leg | 7,200-21,600 solves, unregistered, unpriced | over at its upper end; needs its own go |

## Proposed windows (group (a) only; rule 7: one construction at a time, no pool reader inside a machine slot)
W1 (5 h). Agent lane h0-h2: registrar registers FLAT-MIX-ANCHORED, CERT-ALIGN-SIZE, REF-LADDER-RECOMPOSE, SB-LENGTH,
SEQ-LOOKS; reviewer READYs; review DATASET-SURVEY; engine-coder JOIN-CARDINALITY-GUARD + RUBRIC512 decimal comma.
CPU (non-pool) h0-h1: CERT-ALIGN-SIZE, MULTISWE-CORRECTIONS. Machine slot h2-h4 (pool readers serialised, nothing else
on the pool): FLAT-MIX-ANCHORED -> REF-LADDER-RECOMPOSE -> SB-LENGTH -> SEQ-LOOKS. h4-h5: INCONSISTENCIES-PASS text (A).
W2 (5 h). h0-h0.5 CONSTRUCTION slot, exclusive (backup DBs first; no reader alive): CDS-SPOTCHECK. Then pool-reader slot
h0.5-h3.5: DEFF-ATLAS, then BAND-INTERVAL. Agent lane throughout: CANARY-ANALYZE-FIX, hygiene keep-list items, the
online threshold registration. h3.5-h5: INCONSISTENCIES-PASS scripted, the ONE ledger patch, no reader concurrent.
Leave one core free; no stray JVM at the end (check: tasklist | grep -iE "java|python").
