# TaxoArena — agent knowledge base (read this FIRST, every time)

The stable facts agents keep re-deriving, each with a pointer. It is a digest, not a record: when a fact
decides your task, open the pointer (grep the id, read the span). CONTEXT.md §4 stays the binding text of
the standing rules; §2 below is its digest. Written 2026-09-27 at HEAD 3fdc5d2, ledger v309; "prog" =
`docs/judge_v2_program.md`, "plan" = `docs/plan_2026-09-15.md`, "rev2" =
`docs/agents/plans/2026-09-27_research_plan_rev2.md`. If a pointer here disagrees with the record, the record
wins: say so in your hand-back so the registrar can bracket this file.

## 0. How to work cheaply (binds every agent)

**Reading.**
- Read this file first. Do NOT read `docs/agents/CONTEXT.md` whole; grep its § you need (§3 objects, §4
  rules, §5 closed lines). Never read the programme (~22k lines), the ledger (HTML) or `queue.json`
  (~6k lines) whole.
- Programme: `grep -n '^## ' docs/judge_v2_program.md | tail -40` for the latest sections; `grep -n '<ID>'`
  then `sed -n 'A,Bp'` on the span. Headings are fixed: `## Registered <date> (before any code or call) — <ID>:`,
  `## <ID> (<date>, <calls>) — <verdict>`, `## Registrar's record <date> ...`, `## Author's decision <date> ...`.
  Newest LAST; the last bracket wins.
- One experiment's state: `docs/agents/results/<ID>.json` (then `INDEX.md` for the one-line list). Read the
  JSON before the programme.
- One queue item: `python -c "import json;q=json.load(open('docs/agents/queue.json',encoding='utf-8'));print(json.dumps([i for i in q['items'] if i['id']=='<ID>'],indent=1))"`.
- Plan amendments: `grep -n '^## Amendment' docs/plan_2026-09-15.md`, then the span.
- Reuse committed scripts (`tools/analysis/*.py`: `pool_guard.py`, `ledger_patch.py`, `results_index.py`,
  `split_side.py`, `accepted_tests_ledger.py`, `systematic_budget.mcnemar_edge`, `support_readout` in
  `ifeval_response_oracle.py` L511-L533) before writing a new one.

**Verification.** Facts the brief states as already verified (pins, pool ids, blobs, prior verdicts, line spans)
are taken as given, UNLESS the fact is your own acceptance check (a reviewer's deciding numbers and the
reviewed blob's pins; an operator's pool guard and dry-run lines; a registrar's re-grep of the span it writes,
rule 9). Never re-derive pins/pool ids/split words that are listed in §1 below. A state claim you make still
needs the command that shows it (CONTEXT §6), but name the command, do not paste its output.

**REPORT FORMAT (the hand-back; about 150-250 words, never more than ~300).**
```
VERDICT/STATE: <one line: READY / NOT READY / VALID / HELD / done / blocked ...>
COMMITS: <sha(s)>; ledger <vNNN or unchanged>
NUMBERS OF RECORD: <only the deciding ones, with denominator/interval>
BLOCKERS / CONDITIONS: <ids, one line each, severity>
AUTHOR DECISIONS NEEDED: <none | one line each>
FILES: <absolute or repo paths of the committed file(s)>
```
All detail (commands, tables, pins, blobs, mutant lists, prior-commit chains, line numbers) goes into the
COMMITTED file only; the hand-back points to it and never repeats it. No restated brief, no history.

**Briefs (for the orchestrator/research-lead writing them).** Give: task id, worktree/branch, the facts
already verified (so they are not re-verified), the acceptance check, the output file path. Reference §1/§2
here instead of restating pins or rules.

## 1. Pins of record (HEAD-independent)

**Framing of record** (adopted by the author 2026-09-27; prog L21435-L21457; plan Amendment 25; texts
`docs/agents/plans/2026-09-26_framing_of_record.md`, rev2): "Cell-conditional evaluation", SQ1 USE, SQ2 TRUST,
SQ3 TAXONOMY, SQ4 PRICE, SQ5 INVARIANCE; scope S1-S5 (framing §"Scope rules"): S1 arena cells are DECLARED;
S2 verification fidelity only; S3 every object carries its split word; S4 recipes never joined (R256 vs R512
counts, T1 vs T1b); S5 closed lines stay closed.
**History, never evidence:** r8 and the whole p2dca judged family [P-FAM] (`docs/reviews/RULING_w0_p2dca_family.md`;
prog L21459-L21504). Quote any [P-FAM] number only with its bracket; the words of the family bracket and of the
r8 paragraph are the author's. Do not use the frozen 07-27 tree as an evidential comparator (rev2 §B8).

**Split words (S3; CONTEXT rule 12).** Never write "clean", "disjoint" or "held-out" without a CK-CLOSE check.
- Content-closed: the v2 split, draw 5a3e756 (ARCH-V2-SPLIT-DRAW-2, prog L16193ff; EVAL 0.30 / GATE 0.10 /
  TRAIN 0.60, plan Amendment 15; content-closed under CK-CLOSE-v2 with the residual disclosed): pools
  `pv2_41dbd3dbcd399df0` (mmlu-pro-v2, 3,492 EVAL items / 3,400 components; the K46 store's split) and
  `pv2_1575de61bb20e977` (all corpora + mc6, 6,153 / 5,642). `pv2_6f78aece2bf9a612` (split b51eb71) is
  SUPERSEDED for forward use (plan Amendment 19). Also content-closed: `af_clean_s42` (R256).
- Id-disjoint only: `p2dca21ab5f4ef3ae` (3,445 judgeable of 3,599 ids; bareq512_s42's split; bound 2.03pp),
  `paeec37aa28063c75` (union, 6,482; bound 1.32pp), the re-draw splits af_s137 (pd610c9a), af_s2048
  (p19d9f47), af_s42_o1 (p8a29) until the data-steward's closure check (framing S3 + its B3 bracket).
- 20NG smoke pool: `pf844849e133cda4e` (`experiment_configs/reserved_pool_frozen_pf844849e133cda4e_20ng.json`).
- CK-CLOSE-v1 key = `split_side.stem_key` (CONTEXT rule 12; plan Amendment 13); it binds every NEW pool,
  construction and policy fit; objects of record are not rebuilt (rebuild-or-disclose is the author's). [CORRECTED 2026-10-01 by the registrar: SETTLED by the author's D4 "Disclose + fresh build for RP13": disclose for the existing objects; RP13 re-scoped onto a fresh anchor-free build on draw 5a3e756 TRAIN; D3 "Keep qwen3, gemma secondary"; plan Amendment 31; prog section "## Author's decision 2026-10-01 (insertion only; zero calls; nothing run) — checkpoint B's D1 ...".]
- Verify a pool with `python tools/analysis/pool_guard.py --pool <id>` (refuses on a non-empty -wal/-journal:
  a failed precondition, never an outcome; nothing is "activated"; CONTEXT §3).

**Trees.**
- `bareq512_s42` = snapshot 20260909_212117 (87 leaves, R512, id-disjoint only; config
  `experiment_configs/promoted/bareq512_s42.toml`). NOT a certified fixed point (CERTIFIED false at iteration
  18). Only Chemistry n00000006 and Engineering n00000015 may be called "certified at per-family FDR q = 0.05
  (hierarchical BH over nested sites, 300 reps, bareq512_s42, R512)"; the other 8 of 10 pass "their own
  site-null p95 (per-site, uncorrected)" only (CONTEXT §3 brackets; prog L20957-L21058). Engineering is
  R2-unreachable on s42: print "UNREACHABLE at 300 reps" (prog L21831ff R1).
- `af_clean_s42` = snapshot 20260917_201353_Headless_Run_Auto_ge (82 leaves, anchor-free, content-closed,
  `experiment_results/anchorfree/redraw/af_clean_s42/seed_42`); FLAT-MIX-MMLU: a measurably WORSE partition
  than a flat vMF mixture at k = 82 (prog L21121).
- Frozen `20260727_042523` (154 nodes / 87 leaves, `snapshots_frozen.db`, never modified): geometry-only.
- Anchor-free `af/seed_42` (81 leaves): structural artefact, not arena-bound.

**Embedders.** qwen3-embedding is of record: `embeddings_cache.db` (all 4096-d, 39,631 rows; READY review
bb30526). Second embedders (Amendment 26 (b)): nomic-embed-text v1.5 and embeddinggemma, per-model DBs
`embeddings_cache_nomic-embed-text_latest.db`, `embeddings_cache_embeddinggemma_latest.db`; PRIMARY protocol
RAW, card-conformant a registered secondary; mxbai not decided. With no flag readers read qwen3; any other
embedder needs the explicit flag plus the vmfMu guard (R2, prog L21831ff). No non-qwen3 site null / FLAT
read before EMBEDDER-PLUMBING (RP08) merges (rev2 §B8). `queries.ground_truth_category` is text-keyed and
shared across corpora (last writer wins).

**Judge recipes (never joined).**
- STACK-v2 (v1 prompt): judge grok-4-1-fast-non-reasoning; reference = cached grok-4-1-fast-reasoning solve
  (`experiment_results/judge_solve/grok-reasoning.db`, 3,432); cap 8192; temperature OMITTED (plan Amendment 1
  D2); dual order, TIE on flip; every call via `rejudge_reasoning.call_judge_full`; body via `rr.payload_body`
  (CONTEXT rules 5, 9, 10).
- v2 recipe: the K46 store `experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db` (sha256 44724d25…,
  open `mode=ro&immutable=1`); split pv2_41dbd3dbcd399df0; 69.3% of its matches carry no reference (rev2 L68).
- Which instrument SQ2's content-closed claims are stated under is OPEN, the author's (rev2 §B7 item 6).

**Ledger and record conventions.**
- `docs/test_ledger.html` (v309 at 3fdc5d2): patched ONLY through `tools/analysis/ledger_patch.py`
  (`insert_outcome / add_row_before / replace_chip / stamp / audit / write`); §7 newest-first; chip classes
  ok / run / plan / warn / null; chip text carries the qualifier; entities, `&mdash;`; `audit()` before `stamp`.
- Wrong counts are wrong(established) (exact McNemar, `systematic_budget.mcnemar_edge`); both tie conventions
  A and B; question-clustered intervals (CONTEXT §3).
- Pins name their hash kind: `blob:<hex>` / `sha256-lf16:<hex16>` / `sha256-crlf16:<hex16>`; LF is of record
  (CONTEXT rule 8 bracket).
- Line spans carry `_as_of <sha>` and a verbatim heading (registrar rule 9).
- Corrections by insertion only: `[CORRECTED YYYY-MM-DD by <TEST>: ...]`; last bracket wins.
- Outcome files are write-once (mode `x`); pilots write `*_PILOT.txt`.

## 2. Standing rules (digest of CONTEXT §4; all still bind in full)

- **Standard flow** (CONTEXT §7 last line): (experiment-manager / cost-estimator) → research-lead → registrar
  (registration, with Support, BEFORE code) → engine-coder or specialist (script, `--dry-run`) →
  adversarial-reviewer (committed READY; mandatory before any pilot) → run-operator (dry-run → pilot 12 read by
  the truncation guard, refuse >5% unparsed → run → `--analyze` refusing partial caches) → adversarial-reviewer
  (numbers) → registrar (outcome, ledger, results JSON, INDEX, queue) → research-lead (synthesis).
- **Split** (rule 1): construction, labelling and rubric induction never see EVAL; TRAIN-ONLY guard.
- **Commit by path** (rule 8): `git add <new paths>` then `git commit -F <msg> -- <paths>`; never `git add -A`,
  `git add .` or a bare commit (the index and branch tip are shared). After any rebuild/amend of your own
  commit, check `git merge-base --is-ancestor <peer-sha> HEAD` (memory: concurrent-agent staging, 9bd9850 was
  orphaned once). Attribution lines at the end of every message. `git ls-files --error-unmatch` before
  moving/deleting in main.
- **Rule 7 (one construction, no readers):** one construction or site null at a time, never while anything
  reads the pool (every `--dry-run` via pool_guard is a reader); operational form W1-W5 (exclusive-open probe
  FREE, admitted PIDs printed, ≥ 12 GB free RAM, no git write under src/ in the window); a breach is a failed
  precondition (CONTEXT rule 7; prog L13849-L13881). Back up before any construction.
- **The author's half-machine cap** (plan Amendment 26 (c); prog L21838; rev2 L737-L743): 12 threads is the
  standing default for constructions and site nulls (JVM ActiveProcessorCount = 12; Ollama num_thread ≤ 12);
  it binds once THREAD-CAP is proved, and until then NO JVM construction or site null runs (READY 7676eab NOT
  READY). [CORRECTED 2026-09-30 by the registrar: the orchestrator ruled that THREAD-CAP B1-B3 HELD suffice for the cap to bind on JVM constructions and site nulls; B4 (Ollama) gates only RP53; prog section "## Registrar's record 2026-09-30 (insertion only; zero calls; nothing run; pre-data) — READY_rp12_et 03760e2 and merge 225e4fd; ...".] CPU lane single-threaded (OMP/OPENBLAS/MKL = 1), paused during constructions; ONE heavy process at a
  time (an Ollama embedding run is one). [CORRECTED 2026-09-29 by the registrar: the author raised the machine cap to about 22 of 24 threads (about 2 left for Windows); 12 is no longer the ceiling; rule 7 and one heavy process at a time unchanged; plan Amendment 27; prog section "## Registrar's record 2026-09-29 (insertion only; zero calls; nothing run; pre-data) — the data-steward's preconditions 8c2b846, ...".] Kill by PID only, never by image name (`taskkill /IM python.exe`
  once killed every python: CERT-RESOLUTION.json `process_incident`); a foreign java/python makes the next
  step WAIT, it is not killed.
- **4k-match rule** (rule 5): any judged run above 4,000 arena matches (~8k calls) needs the author's go,
  quoted in the plan. **Day cap:** 14,000 calls per posting day (rev2 L732), on the posting-day ledger; per-test
  CEILINGS in `accepted_tests_ledger.py`; a zero-call TRANSPORT PREFLIGHT inside the dry-run precedes any
  journal/ledger row (memory note dry-run-skips-transport, PILOT-K46 pilot-12; prog L20238). Autonomous scheduling of cheap tests is authorised (memory note autonomous-scheduling, renewed
  2026-09-25); the flow is not waived.
- **Never:** modify `snapshots_frozen.db`; commit/edit `config/application.yml`, `.env`, `.gitignore`; touch
  `report/`; use `seeds = [...]`; join mmlu_pro↔eval by text (OPTIONS key); include
  `Meta-Llama-3-70B-Instruct`; write to a DB of record (open `mode=ro`, `immutable=1` for WAL DBs); import
  `stack_judge.open_cache` (it opens read-write; rev2 L699, CONTEXT §2 bracket); post a judge call outside a registered test.
- **Guards** (rule 11): read inputs from the configured object, print estimate and budget every run, both
  branches verified by execution; an inertness proof needs an execution discriminator (changed code ran).
- **Author-owned** (framing "Decisions that are the author's"; rev2 §B7 items 1-21; memory
  autonomous-scheduling): the framing and any `report/` text; rebuild-or-disclose; the r8 paragraph and the
  P-FAM bracket words; machine-lane order and thread-cap exceptions; embedders (mxbai, Gemma licence);
  external corpora in scope; the v2 reference policy; SQ2's instrument; board size and anything > 4k matches;
  declared-cell overrides; the LEAF-INTERACTION word; `config/application.yml`, `.env`, `.gitignore`. Ask; do
  not infer consent. Relay the open item in "AUTHOR DECISIONS NEEDED".

## 3. Closed lines (CONTEXT §5; do not reopen without a new registration and a mechanism the record has not seen)

- Rubric text at every granularity (RUBRIC, LADDER, RUBRIC-512-R, J6, RK-1, LEAF-POWERED, STACK-NORUBRIC).
- Rubric-shaped references (REF-CHECKLIST).
- Reference ensembles, gating, confidence, two-reference variants (ENSEMBLE-REF, J2-D, REF-CONF, ABSTAIN).
- Sub-anchor profiles (PROFILE-TREE-ROBUST, KEY-SUBANCHOR-SCALE).
- The frontier order (FRONTIER, AGGREGATE, ORACLE).
- Escalation to a reasoning judge on the residue (ESCALATE-LLAMA-LAW).
- The proposal memo (PERF-8); single and selective order (ORDER-1, SELECTIVE-ORDER); temperature 0 (TEMP-0).
- LCB judged stage at that roster/recipe (LCB-STAGE0-INTERACTION F1 STOP; prog L19732-L19800).
- GMM LR / BIC half of L6 (MIX-LRT-SITE, CLOSED NEGATIVE, prog L21326-L21433; quote only with its qualifier);
  the dip half stays OPEN.
- P-FAM is not a reopening reason (RULING_w0_p2dca_family.md §3.2).

## 4. Where things live

| what | where |
|---|---|
| registrations, outcomes, rulings | `docs/judge_v2_program.md` (grep, never read whole) |
| per-experiment state (machine-readable) | `docs/agents/results/<ID>.json`; `INDEX.md` via `results_index.py` |
| queue of record | `docs/agents/queue.json` (items: id, state, go, ready_file, author_decision, cost, lane, notes); `queue.md` view |
| ledger | `docs/test_ledger.html` (+ `_distilled.html`), via `ledger_patch.py` |
| plan amendments, author's gos | `docs/plan_2026-09-15.md` `## Amendment NN` |
| current plan, B7 author list, B8 don'ts | `docs/agents/plans/2026-09-27_research_plan_rev2.md` |
| framing | `docs/agents/plans/2026-09-26_framing_of_record.md` |
| reviews / READY / rulings | `docs/reviews/READY_*.md`, `POSTRUN_*.md`, `RULING_*.md` |
| design of record | `docs/design/FRAMEWORK.md` (check the brackets) |
| engineering worktrees | `.claude/worktrees/<name>` (do not touch another agent's) |
| backups | `E:\TaxoArena_backup_2026-09-2x` (same physical disk: guards deletion only) |

## Temp files and destructive code (2026-10-04)
- All temp/scratch goes under E:/TaxoArena_tmp via `tools/analysis/scratch_dir.py` (merged f460d72c). Scripts not switched (pinned ones) run as `python tools/analysis/scratch_dir.py --run -- python tools/analysis/<script>.py --selftest`.
- Code that deletes, moves or overwrites files is selftested and mutated ONLY inside a sandbox, with TMP, TEMP and TMPDIR all redirected there; real paths are dry-run only. (Incident 2026-10-04: mutants of a purge guard run on real paths wiped about 7,100 entries from the system Temp.)
- Outputs are never committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_<tag> with SHA256SUMS.
