# READY review: fresh-math-pipeline (benchzoom `fresh-math-pipeline` b86c014..ccedcd5; D-2026-10-28-1, prepare only)

Reviewer: adversarial-reviewer, 2026-10-28. Zero LLM calls by the reviewer (Ollama metadata endpoints only: one
`/api/version`, `/api/tags`, `/api/show` during the reviewer's dry run). Read-only on both repositories except this file.
Reviewed blobs (LF; index and working tree both `i/lf w/lf`, so no CRLF rendering differs): script
`blob:0966b648b1b000cc13b6bbd861b19d1de0948086`, mutants JSON `blob:e05798e2…`, test `blob:dc8cd498…`, plan
`blob:18fdda24…`. TaxoArena pins in the script match: `split_side.py` `blob:05224b5a…`, `accepted_tests_ledger.py`
`blob:b90e64dc…`.

## Verdict

- **Generation go: NOT READY.** C1-C4 below have to be fixed and delta-reviewed before any `AUTHORISED_GO` entry
  is added. C2 blocks only an Azure go.
- **Merge: MERGEABLE (fast-forward).** benchzoom master is still at b86c014, and `merge-tree` is clean against
  fresh-size, bbh, embed2-work, design-surface and fresh-rules. The code is inert because `AUTHORISED_GO` is empty,
  and no file under `src/` changed (4 files, all in examples/, tests/ and docs/), so the execution graph needs no update.
- **Support section:** N/A. This is engineering with no deciding statistic. The BZ-AXIS-CONFIRM-FRESH registration
  must carry its own Support section.

## Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | zero LLM calls | Ollama `server.log`, [GIN] lines dated 2026/10/28: 0 `/api/chat` or `/api/generate`; 54 show, 12 tags, 6 version, 3 ps, 3 HEAD; the 2 `/api/embed` at 00:29 come before the plan commit (12:28:55) and belong to another task. 0 AZURE_* env vars. 0 day-ledger files contain FRESH-MATH-GEN. The 1,661 scratch journals hold only `fake-*` and `stub/*` models. `fresh_math_raw/` absent. Ollama [GIN] count unchanged (3,356 → 3,356) across the reviewer's CLI refusals | CONFIRMED | - |
| 2 | frozen list v2: 6,902 items, sha256 e39bb5f4…, unique ids; 7,058 − 156 | 6,902; 6,902 unique; sha256 e39bb5f46949d5f6; items ⊂ SPEC candidates (7,058); 156 not in the list; 0 items fail the text / options / key / usability re-check against train.jsonl | CONFIRMED | - |
| 3 | each of the 156 has exactly one empty distractor, never the key | one empty option: 156 of 156; key empty: 0; non-distinct: 0 | CONFIRMED | - |
| 4 | twin re-check 0 exact / 0 near, max J 0.7989, max abs(J − SPEC) 0.0001 | reviewer's own code: 0 exact (stem_key), 0 at J ≥ 0.8, max J 0.7989, 204 at J ≥ 0.7, max abs(J − SPEC) 0.0001; used set 5,000 test + 4,914 EEE + 1,324 MATH-Hard | CONFIRMED | - |
| 5 | v1 gave rows 312/743 one id | v1 has 6,901 unique ids out of 6,902; the only difference from v2 is row 743 (00925 → 00959) | CONFIRMED | - |
| 6 | the test split has 97 empty-distractor items of 4,914 | 97 in MC-Evaluation `test.jsonl` (4,914) | CONFIRMED | - |
| 7 | prompt sha256 b845360d…, regex sha256 41ec6bba…, protocol reasoning then letter | b845360d45386fc3 and 41ec6bba0ffd3298 recomputed. The text asks for step-by-step reasoning, then `Answer: <letter>` on the last line, which matches D-2026-10-28-1 (3) | CONFIRMED | - |
| 8 | selftest 28/28; tests 15/15; mutants 67/67 | 28/28 standalone (sandbox); 15 passed; the builder's 67 re-run in a fresh camp: 67 killed, control passes, 0 survived | CONFIRMED | - |
| 9 | full suite 956 passed, 1 skipped | 956 passed, 1 skipped, 10 deselected, 0 failed (single process, PYTHONPATH=src, benchzoom venv, 873.6 s) | CONFIRMED | - |
| 10 | the dry run reaches the matrix and the loader | Reviewer's run: 48,314 stub attempts; closed forms EQUAL for 7 of 7 models; real-list stub matrix sha256 0054bf4f… is identical to the builder's; fixture 60 × 7 loads cell for cell. Beyond the claim, the REAL-list stub matrix (6,902 × 7) also loads cell for cell through `load_scores` / `Benchmark` / `backbone` (chance 0.25, 4 options) | CONFIRMED | - |
| 11 | refusals: no `--go`, D-2026-10-28-1, unknown id, real backend without authorisation | CLI, run by the reviewer: G2 for no go, for D-2026-10-28-1 (with and without `--cap`, and with `--cap 999999`), for an unknown id (not found) and for a malformed id; G1 for the stub. Sandbox (fake backends, no network): G3 at cap 501 > 500; G3 for a run cap above the authorisation; G4 at 13,995 + 10 = 14,005, with 0 posts | CONFIRMED | - |
| 12 | G3 "at most the decision's max_calls" | the cap is counted **per journal**: with max_calls 3 and three journal dirs, the same go posts **9** times (P2) | REFUTED | HIGH |
| 13 | G4 "ledger + planned ≤ 14,000; refused, not trimmed" | the check uses planned = pending items, but retries are counted calls the check does not bound: ledger 13,990 → **14,010** with one 429 per item and no `--limit` (P1); with `--limit 10` it stops at 14,000 (P1b) | REFUTED (Azure only) | HIGH |
| 14 | G8 pilot (default 12) | `PILOT_DEFAULT = 12` is never used and `--pilot` has no default. A **1-item** pilot passes G8 and unlocks the full run (P3) | PARTLY | MEDIUM |
| 15 | G8 overrides via the go entry | adding `pilot_overrides` to `AUTHORISED_GO` changes the script blob, so the resume is refused with `[G6] journal meta mismatch on ['script_blob']` (P5b). An override therefore forces a new journal, a new pilot and (with #12) a new cap | REFUTED as specified | MEDIUM |
| 16 | roster / cost tables (120 / 192 / 2,939 h; 27,608 calls, 2 days, 36 h; twins 0.959 / 0.990) | recomputed from the pinned SPEC CSVs and EEE parquet: max abs(Δ) 0.0 h on all 18 rows; totals 120.0 / 192.3 / 2,938.9; 27,608 / 2 / 36.1 h; 0.959 / 0.990. Every row carries its source columns, money is not priced, and it is labelled ESTIMATE | CONFIRMED | - |
| 17 | outputs outside git; credentials never printed | `git rev-parse` fails in E:/benchzoom_cache, E:/TaxoArena_tmp and E:/benchzoom_demo. The Azure preflight prints booleans only; errors print HTTP codes or type names; the selftest asserts the fake key is absent from the output | CONFIRMED | - |
| 18 | no fresh-item statistic, embedding or tree | the script calls no embed endpoint. The four prompt numbers (468.9 / 409 / 684.9 / 4,557) and the disclosed key balance (A 1,717 / B 1,736 / C 1,744 / D 1,705) are reproduced, and nothing else is printed about the fresh items. The stub matrices carry synthetic scores only | CONFIRMED (disclosure kept) | - |
| 19 | plan committed before any code; insertion only; backup | 92343cb touches 1 file (the plan); the [BUILT] section is 20 insertions and 0 deletions; backup SHA256SUMS 10 of 10 OK | CONFIRMED | - |

Own mutants (sandboxed copies, fake server; control passes):

| id | change | result | decisive |
|---|---|---|---|
| R1 | THINK_BLOCK `.*?` → `.*` (greedy) | SURVIVED | no (needs 2 think blocks) |
| R2 | answer-line prefix `[ \t>#*_-]*` → `[^\n]*?` | SURVIVED | yes (validity rule untested mid-line) |
| R3 | day cap ignores the planned calls | killed | yes |
| R4 | journal pin exempts `script_blob` | SURVIVED | no (other pins cover the protocol) |
| R5 | CTX guard at 4 chars per token | killed | yes |
| R6 | G7 containment without abspath (lexical) | SURVIVED | yes (the code is correct: `raw/../escape` is refused, P4) |
| R7 | full-run pilot guard on the first model only | SURVIVED | **yes** |
| R8 | THINK_BLOCK without `re.S` (multi-line blocks kept) | SURVIVED | **yes** (the code is correct on the multi-line case) |

## Defects and fixes

- **C1 HIGH (G3).** Make the go's `max_calls` bind per go, not per journal. Either bind each `AUTHORISED_GO` entry
  to one journal path, or sum the attempts of every journal under `RAW_ROOT` whose launches carry this go before
  each attempt. Add a selftest for a second journal under the same go.
- **C2 HIGH (G4, Azure only).** Bound retries by the checked plan. For azure, stop the loop when
  `launch_attempts == room`, or re-check `today + launch_attempts < 14,000` before every attempt. Add a selftest with
  repeated 429s.
- **C3 MEDIUM (G8).** Enforce a pilot-size floor: refuse a real full run when the journal's `pilot_n` is below 12
  (`PILOT_DEFAULT`), unless the go names another size.
- **C4 MEDIUM (G6 vs G8).** Move `AUTHORISED_GO` (overrides included) out of the script into a pinned JSON, or pin a
  protocol digest (prompt, regex, cap, sampling, scoring code) instead of the whole script blob. Document what a
  resume tolerates.
- **C5 MEDIUM (test gaps, decisive survivors R2 / R6 / R7 / R8).** Add these cases: a two-model pilot with the bad
  model second; `"<think>\n…Answer: A\n</think>\nAnswer: C"` → C; `"The final answer: C"` → MISSING (pins the
  strict prefix); `RAW_ROOT/../x` refused for a real backend.
- **C6 MEDIUM (author / registration).** Temperature 0 is the plan's choice, not the author's. None of the 69
  surveyed EEE runs used 0 (1.0: 21, 0.3: 19, 0.6: 14, 0.7: 3, 0.8: 1, unrecorded 11). Greedy decoding favours
  repetition loops in small models, and the runaway shares behind the 192 h estimate were measured at non-zero
  temperatures, so that estimate is probably optimistic for the llama3.2 rows. The setting must be decided before
  the go.
- **C7 LOW (extraction, behaves as pinned).** `Answer: A total of 12, so C` → WRONG A (the article is read as the
  letter). `Answer: A or C` → A. MISSING for: `The final answer is $\boxed{C}$` (the Llama-3 convention),
  `Answer: \(C\)`, `Answer: $\boxed{\text{C}}$`, `Answer: Option C`, `**Final Answer**\n\nC` and `1. Answer: C`. A
  stray `<think>` after the answer also gives MISSING. Every case is counted, flagged and caught by the pilot. Any
  widening is decided before the go, never after pilot outputs.
- **C8 LOW.** `--matrix` does not compare the journal's pinned regex / prompt / items digest with the current ones
  (the provenance shows both). Fix: refuse on a mismatch in `matrix_frame`.
- **C9 LOW.** An `Authorisation` built directly passes G1 (P6; in-process only). Descriptive figures: llama3.2 1b+3b
  account for 58.1 h of runaway excess (64.5 h in total), not "about 57"; the Kimi 40.5% sits at prog L2635/L3066, not
  L2633.

## Author decisions needed (before a go)

Serving (local or API); the 156 empty-distractor items (exclude or keep); thinking for qwen3 / qwen3.5; keeping
llama3.2 1b/3b; temperature (0, a survey-like setting, or the model default: C6). Each go needs a decision id and a
call cap, and that cap binds only after C1 is fixed.

## Commands (scripts in E:/TaxoArena_tmp/review_fmp/, read-only on the inputs)

```
grep -a "\[GIN\] 2026/10/28" .../Ollama/server.log | awk '{print $NF,$(NF-1)}' | sort | uniq -c   # #1
grep -l FRESH-MATH-GEN experiment_results/day_calls_*.json | wc -l                                 # 0
python -I verify_items.py      # #2-#6, #18 (sha, 6,902, 156, twins, J 0.7989, key balance)
python -I verify_roster.py     # #16, prompt stats, survey temperatures (second snippet)
python -I adv_regex.py         # C7 (36 adversarial strings through classify)
python -I guards_probe.py; python -I guards_probe2.py   # P1-P6, Q1-Q3 (fake backends, sandbox ledgers)
python dry_probe.py; python dry_real_load.py            # #10 (scratch E:/TaxoArena_tmp/review_fmp/dry)
python run_camp.py own_mutants.json mut_own; python run_camp.py <worktree>/examples/fresh-math-pipeline_mutants.json mut_builder
PYTHONPATH=src python -m pytest tests/test_fresh_math_pipeline.py -q -p no:cacheprovider   # 15 passed
PYTHONPATH=src python -m pytest -q -p no:cacheprovider     # 956 passed, 1 skipped, 10 deselected
git -C Z:/FAC/TUBerlin/benchzoom merge-tree --write-tree <b> fresh-math-pipeline; sha256sum -c SHA256SUMS
```

## Delta review 2026-10-28: fresh-math-pipeline-2 (benchzoom 06c075f..0be0164; D-2026-10-28-1 / -2; prepare only)

Reviewer: adversarial-reviewer. Zero LLM calls: Ollama `server.log` [GIN] 2026/10/28 holds 0 `/api/chat` and 0 `/api/generate`.
The reviewer's dry run added 18 show, 2 tags and 1 version. Every CLI refusal and the BZ_EXAMPLES probe added 0 (closed port 127.0.0.1:9).
0 AZURE_* variables were set. 0 day ledgers carry FRESH-MATH-GEN, and `fresh_math_raw/` is absent. The review is read-only on both
repositories except this section. Reviewed blobs (LF; `i/lf w/lf`, so no CRLF rendering differs):

- script `blob:90642e2fba6015c82b1e90f5e00eceed7f99c3c8`
- go config `blob:aadd03e8…`, which is `{}`, committed and clean
- mutants `blob:af5d8ea2…`
- test `blob:c1aef33d…`
- plan `blob:e662397d…`: the working tree reads `w/mixed`, but `git hash-object` equals the HEAD blob

The TaxoArena pins in the script still match: `split_side.py` `blob:05224b5a…` and `accepted_tests_ledger.py` `blob:b90e64dc…`.

### Verdict

- **Generation go: NOT READY.** C1 and C3-C8 are fixed. C2 holds for a single launch only.
  - Before any go: D3 and D4 must be fixed and delta-reviewed, with the decisive test gaps T1, T4 and T5 closed.
  - Before an Azure go, also D1 and D2.
  - A go still needs the author's decision id, serving, roster and cap.
- **Merge: MERGEABLE (fast-forward).** `merge-base --is-ancestor master fresh-math-pipeline-2` holds. The code is inert because the committed
  go config is empty. Five files changed and 0 of them are under `src/`, so the execution graph needs no update.
- **Extraction v2, the builder's question.** Rule: a later answer statement that names no letter makes the item MISSING (`Answer: C\nAnswer: 12`
  is MISSING). I CONFIRM it as a conservative rule, pinned before any output: the model's last statement names no option. D4 must be fixed first.
- **Support section: N/A** (engineering). The BZ-AXIS-CONFIRM-FRESH registration carries its own.

### Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | zero LLM calls | the above. The builder's 17:02 dry run: 18 show, 2 tags, 1 version, 0 chat/generate | CONFIRMED | - |
| 2 | list v3: sha256 169f99b7…, 7,058 = v2's 6,902 unchanged + the 156 | 169f99b714dc6ef5; 7,058 lines, 7,058 unique ids; the 6,902 v2 lines appear verbatim in v3. The 156 new items each have 1 empty option (142 `''`, 11 `' '`, 2 `'\n'`, 1 `'  '`); key empty 0; non-empty options distinct 156/156. v3 equals the SPEC `fresh_mc_candidate` rows (7,058, 0 left out) and fails 0 text/options/key re-checks against train.jsonl | CONFIRMED | - |
| 3 | twin re-check on 7,058: 0 exact, 0 near, max J 0.7989, max abs(J − SPEC) 0.0001 | own code: 0 exact (stem_key); 0 at J ≥ 0.8; max J 0.7989; 212 at J ≥ 0.7 (204 on v2); 0.0001 | CONFIRMED | - |
| 4 | pins: prompt b845360d, regex set 089ed314, protocol digest 06b03f0a, script blob 90642e2f | b845360d45386fc3, 089ed3143d30d24e, 06b03f0a46508a32 recomputed; `git hash-object` 90642e2f | CONFIRMED | - |
| 5 | selftest 44/44; targeted 28; full suite 971 passed, 1 skipped | 44/44 (sandbox, 8.7 s); 28 passed; full suite 971 passed, 1 skipped, 10 deselected, 0 failed (single process, PYTHONPATH=src, benchzoom venv, 879.1 s) | CONFIRMED | - |
| 6 | mutants 135/135 killed, control passes | re-run in a fresh camp (SCRATCH redirected, so the builder's `results.json` is not reused): 135 killed, control passes, 0 survived | CONFIRMED | - |
| 7 | dry run: 49,406 stub attempts, closed forms EQUAL for 7/7 | own run: 49,406 (= 7,058 × 7); 14/14 EQUAL lines (real + fixture). Matrix sha256 real 4f3752b1… and fixture fec0e444… are identical to the builder's. The real list loads cell for cell (7,058 × 7, 4 options, chance 0.25) | CONFIRMED | - |
| 8 | C1: the go cap binds over all journals | max_calls 3, three journals → 3 posts. `--cap 2` under max_calls 5, two journals → 2. Two concurrent journals (threads), max_calls 10 → 10 | CONFIRMED | - |
| 9 | C2: retries bounded by the plan; ledger re-read before every request | One launch: ledger 13,990 with pilot 12 → REFUSED [G4], 0 posts; `--limit 10` with a 429 on every item → 10 attempts, ledger 14,000. **Two overlapping Azure launches** (B starts while A posts; no instrumentation): actual day total **14,005** (ledger 13,985, 10 each), and **14,039** (ledger 13,850, 100 each). With a barrier after both start checks: 14,010 | PARTLY | **HIGH (D1, Azure)** |
| 10 | C2: recovery row for a crashed launch | Works for a crashed launch. The in-flight attempts of a LIVE overlapping launch are appended as `recovered`, then appended again by its `finally`: 24 posts are recorded as 29; 14 spurious calls in the 14,039 case | PARTLY | MEDIUM (D2) |
| 11 | C3: pilot floor | pilot 1 → REFUSED [G8] (0 posts, no journal). No pilot → refused. A go with pilot_min 20 and pilot 12 → refused. pilot_min 11 → refused at authorise. `--pilot` const 12. A journal with pilot_n 4 → refused (selftest) | CONFIRMED | - |
| 12 | C4: go config out of the script; a resume tolerates an override; protocol digest pinned | Override added plus script blob changed → the resume runs (60 rows; launch rows record both blobs; entry sha differs). MAX_ATTEMPTS changed → [G6] protocol_digest. An edit of `extract_answer` moves the digest 06b03f0a → 0ed31144 (REGEX_SHA unchanged). **BUT** `BZ_EXAMPLES` redirects GO_CONFIG to any committed JSON in any git repo. An unreviewed sandbox repo naming D-2026-10-28-1 (serving "Not yet") passes G2 and G3, and the run reaches G5 (stopped only by the closed port). Without it: REFUSED [G2] | PARTLY | MEDIUM (D3) |
| 13 | C5: R2 / R6 / R7 / R8 killed | the builder's adapted R1, R2, R6, R7 and R8 are killed in the reviewer's campaign (classify_table, g7_dotdot_escape_refused, pilot_guard_all_models) | CONFIRMED | - |
| 14 | C6: no temperature sent; recorded per model | Ollama body keys: model, messages, stream, keep_alive, think, options {seed, num_predict, num_ctx, num_thread}. Azure: model, max_tokens, messages. The dry run records gemma3:12b 0.1, gemma3:1b 1, llama3.2 "unset …" | CONFIRMED | - |
| 15 | C7: 96-case table; linear time | 88 cases + 8 finish-reason cases = 96. 48 own adversarial strings, none above 0.05 s (50,000-token and 5,000-newline inputs included). Defect D4 below | PARTLY | MEDIUM (D4) |
| 16 | C8: `--matrix` re-checks the pins (CLI) | `main(["--matrix", …])` on a journal with a tampered prompt, protocol, regex or items pin → [G6] and no parquet. Untampered → written. Another item list → [G6] | CONFIRMED | - |
| 17 | plan before code; insertion only; backup | a55f921 touches 1 file (the plan, 62+/0−); 0 deleted plan lines over 06c075f..0be0164; backup SHA256SUMS 9/9 OK | CONFIRMED | - |

Own mutants (sandboxed copies, run by `run_mutants` with SCRATCH redirected; control passes):

| id | change | result | decisive |
|---|---|---|---|
| N1 | `gl.reserve` against `auth.max_calls` instead of the launch `--cap` | SURVIVED | **yes** (the code binds `--cap`: probe C1' posts 2; no test covers it) |
| N2 | go ledger pin ignores a changed decision sha256 | SURVIVED | no (authorise refuses changed text first) |
| N3 | recovery after the launch-start day-cap check | SURVIVED | no (the per-request re-read reads the recovered row) |
| N4 | `OVERRIDDEN if overrides` (any model's override unlocks all) | SURVIVED | **yes** (the code is correct; no test covers it) |
| N5 | protocol digest without the function sources (`srcs = {}`) | SURVIVED | **yes** (with it, an edited `extract_answer` keeps the digest d41c2f4d: the resume and `--matrix` accept it) |

### Defects and fixes

- **D1 HIGH (G4, Azure go only).** The day cap is checked per launch. An overlapping launch's later attempts are in no ledger the other
  launch reads, so two Azure launches breach 14,000 (14,005 and 14,039 above).
  - Fix: inside `GoLedger.reserve`'s `BEGIN IMMEDIATE`, refuse when the posting-day total, plus (`day_attempts('azure', day)` − this test's
    ledger rows), plus 1, exceeds 14,000. The go ledger already holds every launch's attempts. Alternatively, hold an exclusive one-Azure-launch
    lock under RAW_ROOT.
  - Selftest: two overlapping launches at ledger 13,850.
- **D2 MEDIUM (Azure).** `recover_day_ledger` treats a live launch as crashed, so the TaxoArena day ledger of record over-counts.
  - Fix: write launch begin and end rows (with pid) to the go ledger, and recover only the attempts of launches that have no end row and whose
    pid is dead.
- **D3 MEDIUM (G2).** `EXAMPLES = BZ_EXAMPLES or HERE` also sets GO_CONFIG for `--run`, so the "reviewed commit" can be any repo's commit.
  - Fix: for `--run`, ignore BZ_EXAMPLES (GO_CONFIG = HERE / name). Require the go config's `git rev-parse --show-toplevel` to be ROOT. Honour
    BZ_EXAMPLES only under `--selftest` / `--mutants`.
- **D4 MEDIUM (extraction, fix BEFORE any output).** The closer run `(?>(?:[ \t]*CLOSE)*)` crosses whitespace and eats the OPENING delimiter of
  the next span (`$`, `$$`, `**`, `__`).
  - These are MISSING: `Answer: (C) $2$`, `Answer: (C) $\frac{1}{2}$`, `Answer: C) $2$`, `Answer: **C** $2$`, `Answer: C $2$`,
    `Answer: (C) **2**`. Yet `Answer: (C) 2` → C and `Answer: C. $2$` → C.
  - MATH-MC options are LaTeX, so restating the option is a realistic last line. MISSING scores 0, and 1 of 12 in the pilot refuses the model,
    which would force a change after outputs exist.
  - Fix: no whitespace inside the closer run for the symmetric delimiters, or close only what was opened. Add the six strings to
    EXTRACTION_CASES; the regex sha256 and the digest re-pin before any output.
- **T1 / T4 / T5 MEDIUM (test gaps; decisive survivors N1 / N4 / N5).** Add:
  - an Ollama launch with `--cap` below max_calls (posts == cap);
  - a two-model full run with an override for one model and the other failing (REFUSED on the other);
  - a protocol-function edit (an attribute swap of `extract_answer`) that must refuse [G6] both on resume and on `--matrix`.
- **D5 LOW.** Two first launches at once crash on `PRAGMA journal_mode=WAL` (`sqlite3.OperationalError: database is locked`; fail-closed,
  raw traceback). Fix: create the go ledger with a retry, or map the error to REFUSED.
- **D6 LOW (extraction policy, by the pinned rule; decide before the go, never after pilot outputs):**
  - `Answer: C, because x` → MISSING, but `Answer: **C**, because x` → C;
  - `Answer: C\xa0` (trailing NBSP) → MISSING;
  - `Answer: The correct option is C.` → MISSING;
  - `Answer:\n\n(C) 12` → MISSING;
  - `Answer: C\n\nThe answer is A positive number.` → MISSING (an "is"-form article read as a letter).
- **D7 LOW.** The protocol digest omits `matrix_frame`'s 0/1 map (CORRECT → 1, else 0) and the backends' response parsing (`generate`:
  content vs thinking, done_reason → finish). Fix: factor both into functions listed in `protocol_funcs`.
- **N2 / N3 LOW test gaps; carried:** C9 LOW (an `Authorisation` built in-process); the roster / cost tables at 7,058 not done.

### Author decisions needed (before a go; unchanged except the last two)

- serving, roster and cap;
- thinking for the thinking-capable models: the pipeline sends `think: false`, and gpt-oss `"low"`;
- the local "default temperature" is the Ollama Modelfile's (gemma3:12b 0.1, gemma3:1b 1, llama3.2 unset), recorded per model, not the
  model card's;
- the D6 policy cases.

### Commands (scripts in E:/TaxoArena_tmp/review_fmp2/, read-only on every input; sandboxes only)

```
LC_ALL=C grep -a "\[GIN\] 2026/10/28" $LOCALAPPDATA/Ollama/server.log | awk '{print $NF}' | sort | uniq -c   # 0 chat/generate
python -I verify_v3.py          # #2, #3 (sha, 7,058, 6,902 verbatim, the 156, SPEC rows, twins, J)
python probes.py                # #8-#12, #14, #16 (fake backends, sandbox ledgers/journals)
python probe_race.py; python probe_race2.py; python probe_race4.py   # D1/D2 (14,010 / 14,005 / 14,039)
BZ_EXAMPLES=<sandbox repo> OLLAMA_HOST=127.0.0.1:9 python fresh-math-pipeline.py --run --backend ollama --go D-2026-10-28-1 ...   # D3: reaches G5
python -I adv_regex2.py; python -I adv_dollar.py               # #15, D4, D6
python dry2.py                  # #7 (scratch E:/TaxoArena_tmp/review_fmp2/dry)
python run_camp2.py <worktree>/examples/fresh-math-pipeline_mutants.json mut_builder 2; python run_camp2.py own_mutants2.json mut_own 2
PYTHONPATH=src python -m pytest tests/test_fresh_math_pipeline.py -q -p no:cacheprovider   # 28 passed
PYTHONPATH=src python -m pytest -q -p no:cacheprovider                                    # 971 passed, 1 skipped, 10 deselected
git -C Z:/FAC/TUBerlin/benchzoom merge-base --is-ancestor master fresh-math-pipeline-2; sha256sum -c SHA256SUMS   # 9/9
```

## Delta review 2026-10-29: fresh-math-pipeline-3 (benchzoom 033c79c..2a5bf9d; D-2026-10-28-1 / -2, D-2026-10-29-1; prepare only)

Reviewer: adversarial-reviewer. Zero LLM calls (proof in #1). Read-only on both repositories except this section; every probe ran in
sandboxes under E:/TaxoArena_tmp/review_fmp3 against in-process fake servers (OLLAMA_HOST at the closed port 127.0.0.1:9, Azure variables
cleared). Reviewed blobs (LF of record, `git hash-object`): script `blob:911f616f850adfe9cf3508f13245ee63eb7c3407`, mutants `blob:d398e919…`,
test `blob:5c3374fa…` (both `i/lf w/lf`), plan `blob:fb464a61…` (working tree CRLF `blob:6ee2b3f4…`), go config `blob:aadd03e8…` = `{}`
(working tree CRLF `blob:770a7206…`; the script's pin is the LF blob, correct under core.autocrlf=true). TaxoArena pins in the script still
match (`split_side.py` 05224b5a…, `accepted_tests_ledger.py` b90e64dc…). The delta is 4 files (1,700+ / 344−), 0 under `src/`.

### Verdict

- **Generation go: NOT READY.** D1-D7, T1 / T4 / T5 and C9 are fixed and confirmed (table; D3 with a LOW residual, E3). Two new MEDIUM defects remain:
  - E1, extraction: clear answer forms are still MISSING. Extraction is pinned before any output, so E1 must be fixed now.
  - E2, D-2026-10-29-1 (2) "thinking off": the setting is enforced on the request only, and no check reads the outputs.
  E1 and E2 need a fix and a delta review. An Azure go also needs condition C-AZ.
  A go also needs the author's decision id, serving, roster and cap.
- **Merge: MERGEABLE (fast-forward).** `merge-base master fresh-math-pipeline-3` = 033c79c = master. The committed go config is `{}`, so
  `go_table_for_run` returns `{}` and the code is inert. 0 files under `src/` changed, so the execution graph needs no update.
- **Support section: N/A** (engineering). The Holm family (m = 3) binds the registration, not this pipeline.

### Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | zero LLM calls | Ollama `server.log` + `server-1..5.log`, [GIN] 2026/10/29: 0 `/api/chat`, 0 `/api/generate`. Before the review: 42 lines = 36 show, 4 tags, 2 version (the builder's dry run at 19:11 and roster at 19:12). The reviewer added 1 version + 4 show (Modelfile spot check) and the dry run's 18 show + 2 tags + 1 version; final count 68 (58 show, 6 tags, 4 version): every later probe, the selftests and the 195 mutant selftests added 0. `E:/benchzoom_cache/fresh_math_raw` is absent (no real journal or go ledger has ever been created). 0 TaxoArena day ledgers carry FRESH-MATH-GEN (5 files) | CONFIRMED | - |
| 2 | pins: prompt b845360d, regex set 56cf4896, digest e1a81947, go config aadd03e8, script 911f616f | recomputed by importing the blob: b845360d45386fc3, 56cf4896222af049, e1a81947f64583fe; `git hash-object` aadd03e8 / 911f616f; `AUTHORISED_GO` {} and `go_table_for_run` {} | CONFIRMED | - |
| 3 | selftest 57/57; targeted 43; full suite 986 passed, 1 skipped | 57/57 (sandbox, 12.5 s); 43 passed; 986 passed, 1 skipped, 10 deselected, 0 failed (single process, PYTHONPATH=src, benchzoom venv, 881.4 s) | CONFIRMED | - |
| 4 | mutants 177/177 killed, control passes | re-run in a fresh camp (SCRATCH redirected, so the builder's results.json is not reused; 1 worker, 52 min 58 s): 177 killed, control passes, 0 survived | CONFIRMED | - |
| 5 | D1: the day cap holds across launches and processes | 6 races of 2-3 PROCESSES, each with its own fake server, sharing one sandbox raw root and day ledger; the reviewer counted posts at the fake servers. Results: (a) ledger 13,985, pilot 12, 2 procs on a barrier → 7 + 8, day total **14,000**; (b) the same with 3 procs → 2 + 6 + 7 = **14,000**; (c) 13,850, 100 items, 2 procs staggered → 82 + 68 = **14,000**; (d) 13,850, 3 procs on a barrier, a 429 on each item's first request → 43 + 56 + 51 = **14,000** (retries counted); (e) 3 procs staggered → 63 + 52 + 35 = **14,000**; (f) 13,988, 3 procs staggered, with 429s → 12 posted, the other two REFUSED [G4] at start (13,990 + 12; 13,991 + 12). In 6/6 the day-ledger FRESH rows = go-ledger attempts = fake posts, with 0 recovered rows and 0 tracebacks. The prior review's 14,005 / 14,039 cases now end at 14,000 | CONFIRMED | - |
| 6 | D2: only a dead launch is recovered, once; a live one never | Launch A hard-killed (TerminateProcess on the reviewer's own child) after 51 reserved attempts. The next launch appends `recovered:L1` 51 once; rows 63 = go ledger 63. A third launch recovers nothing (75 = 75). A live launch (60, in flight) while another launch (12) begins and ends: 0 recovered rows, 72 = 72 = fake posts | CONFIRMED | (E4 LOW) |
| 7 | D3: the go config cannot be redirected | (a) `BZ_EXAMPLES` at a committed sandbox repo whose go config authorises D-2026-10-28-1 (reviewed script, CLI `--run`) → `REFUSED [G2] … 0 authorised decisions`. (b) Sandbox clone, go config edited to authorise D-2026-10-28-1: → [G2] modified. With `update-index --assume-unchanged` → [G2] blob 796fd741 ≠ pin. With assume-unchanged plus a clean filter injected through `GIT_CONFIG_COUNT/KEY/VALUE` → **G2 and G3 pass**, and the run stops at [G5] only because the port is closed | PARTLY | LOW (E3) |
| 8 | D4: a following `$…$` / `**…**` span is never consumed | the six D4 strings → C (6/6); also `(C) __2__`, `C __2__`, `$C$ $2$`, `(C) $$2$$`, `**(C)** $x^2$`, ideographic space and tab before `$2$` → C | CONFIRMED | - |
| 9 | D6 / D-2026-10-29-1 (4): clear forms → letter, ambiguous → MISSING; 157 cases + 8 | 157 + 8 = 165 counted. The four clear forms → C; `Answer: C\n\nThe answer is A positive number.` → MISSING (never A, never C). On 136 own strings: 0 WRONG letters where C was meant, but the clear forms in E1 → MISSING | PARTLY | MEDIUM (E1) |
| 10 | extraction linear; think removal linear (M04 case) | 15 own families timed at n and 4n, up to 2.6 M chars: max 0.46 s, 4n/n ratio ≤ 5.7 (the 5.7 is on a 1 ms timing); `<thi<think>x</think>nk>\nAnswer: C` → MISSING | CONFIRMED | - |
| 11 | D-2026-10-29-1 (3): no temperature sent; Modelfile recorded | 60 bodies captured at a fake: no `temperature` key at any depth. Ollama keys: model, messages, stream, keep_alive, think, options{seed, num_predict, num_ctx, num_thread}; Azure keys: model, max_tokens, messages. The journal records the Modelfile 0.7 (or the "unset" text), `parameters_sha256` and `ollama_version`. Real `/api/show` (Ollama 0.40.6): gemma3:12b 0.1, qwen3:8b 0.6, qwen3.5:2b 1, llama3.2:1b unset, as in the builder's table | CONFIRMED | - |
| 12 | D-2026-10-29-1 (2): think=false to thinking-capable models; unswitchable models refused [G5] | `think: false` only to the capability-reporting models, absent for the others and for Azure. gpt-oss / deepseek-r1 / grok-4-1-fast-reasoning / Kimi-K2.6 → [G5] (selftest; own Q09, Q10 killed). **But** outputs are never checked (E2), and the Azure check is a name denylist | PARTLY | MEDIUM (E2) |
| 13 | T1 / T4 / T5, C9, D5, D7 | the prior decisive survivors are now killed: N1 by go_cap_per_launch_cap, N4 by override_one_model_only, N5 by protocol_digest_covers_functions. C9: authorisation_sealed, plus a forged or altered Authorisation refused [G1]. D5: 6 own first opens of a fresh go ledger by 2-3 processes at once, 0 tracebacks (and the selftest's 32 threaded opens) | CONFIRMED | - |
| 14 | dry run on v3 | own run: 49,406 stub attempts; 14/14 EQUAL; matrix sha256 4f3752b1… (real) and fec0e444… (fixture), identical to the builder's and to v2's | CONFIRMED | - |
| 15 | roster at 7,058 (ESTIMATES) | from the builder's CSVs: 122.9 / 196.6 / 3,005.2 h over 18 models. API: 28,232 = 7,058 × 4, 3 days, 36.9 h (= 28,232 / 12.76 / 60); thinking-off subset 14,116, 2 days, 18.4 h. Spot check only (descriptive) | CONFIRMED | - |
| 16 | the builder's new finding: `accepted_tests_ledger.append` is not cross-process safe | read b90e64dc L130-L151: a read-modify-replace through a fixed `path + ".tmp"`. This test's own appends are serialised: FRESH rows = go ledger in 8/8 own multi-process runs (6 races, kill-and-recover, live launch). Another test's concurrent append can still be lost, which would make D1 under-count | CONFIRMED | MEDIUM (C-AZ) |
| 17 | plan before code; insertion only; backup | f2d87a1 touches 1 file (92+/0−); 0 deleted plan lines over 033c79c..2a5bf9d; 2a5bf9d touches 4 files, 0 under src/; backup SHA256SUMS 16/16 OK | CONFIRMED | - |

Own mutants (sandboxed copies of blob 911f616f via `run_mutants`, SCRATCH redirected, 1 worker; control passes):

| id | change | result | decisive |
|---|---|---|---|
| Q01 | `counted + 1 > DAY_CAP` → `counted > DAY_CAP` | killed (azure_day_cap_reread) | yes |
| Q02 | day count = other + go-ledger attempts (this test's day-ledger rows ignored) | killed (day_cap_counts_in_flight_and_rows) | yes |
| Q03 | the reserve counts only this launch's Azure attempts | killed (day_cap_concurrent_interleaved) | yes |
| Q04 | an uninspectable process counts dead | SURVIVED | no (code correct; same-user processes are inspectable; E4) |
| Q05 | the reused-pid creation-time check dropped | killed (pid_liveness) | yes |
| Q06 | the go config blob pin dropped | killed (go_config_not_redirectable) | yes |
| Q07 | the v2 closer run (symmetric closers across spaces) | killed (classify_table) | yes |
| Q08 | (I) under the (L) tail rule | killed (classify_table: `I think the answer is B, but let me check` → B) | yes |
| Q09 / Q10 / Q11 | no think=false / Azure preflight ignores thinking / temperature 0 sent | killed (ollama_pilot_values / thinking_off_refusals / ollama_pilot_values) | yes |
| Q12 | fallback to an earlier valid line | killed (classify_table) | yes |
| Q13 / Q14 | every unended launch dead / no day-ledger append at launch end | killed (recovery_dead_live_recorded / IndexError) | yes |
| N1 / N4 / N5 | the prior review's decisive survivors | killed (see #13) | yes |

### Defects and fixes

- **E1 MEDIUM (extraction v3; fix BEFORE any output).** Clear (L) forms are MISSING. MISSING scores 0, and 1 invalid answer in a 12-item pilot
  refuses the model, so these strings would force an extraction change after outputs exist.
  - A `.` inside a symmetric wrapper: `Answer: **C.**`, `**Answer: C.**`, `**Final Answer: C.**`, `**Answer: (C).**`, `Answer: $C.$`,
    `Answer: *C.*`, `__Answer: C.__`. By contrast `Answer: **C**.` → C.
  - A LaTeX space (or no space) after a wrapper or letter: `Answer: $\textbf{(C)}\ 12$`, `Answer: (C)~12`, `Answer: C~$12$`, `Answer: (C)\,12`,
    `Answer: (C)=12`. By contrast `Answer: $\textbf{(C) } 12$` and `Answer: (C) = 12` → C.
  - Fix:
    - in the eol and wrapped tails, accept `[.!]?` followed by symmetric closers;
    - read `\ `, `~`, `\,`, `\;` and `\quad` as spaces in the tail;
    - add these strings to EXTRACTION_CASES, then re-pin the regex sha256 and the protocol digest.
- **E1c LOW (policy for the author under D-2026-10-29-1 (4), to record before the go).** The (I) end-of-line rule makes these MISSING:
  - the unboxed Minerva sign-off `Final Answer: The final answer is C. I hope it is correct.` (also with `$C$`; the boxed form reads C);
  - `The answer is C because …`;
  - `the correct option is C, as shown.`
  Own Q08 shows that relaxing (I) to the (L) tail rule also reads `I think the answer is B, but let me check` and `If the answer is A, then …`.
  So the rule is a defensible conservative reading. A narrower option: accept `[.!]` + space + text after an (I) letter only when the
  statement opens the line.
- **E2 MEDIUM (D-2026-10-29-1 (2) checked on requests only).** Fake probe, 12-item pilots:
  - a thinking-capable model that ignores think=false: hidden `thinking` on 12/12 rows;
  - a model with a `<think>` block in its visible content: 12/12;
  - an Azure deployment returning `reasoning_content`, whose name the regex does not match: 12/12.
  All three pass G8 with 0 invalid (Azure pilot: 12 CORRECT), and the Ollama full run after the pilot is not refused. The journal still
  says "off: think=false sent".
  - Fix:
    - G8 refuses a model whose pilot rows carry non-empty `thinking` / `reasoning_content` or a removed `<think>` block, and prints the count;
    - the matrix provenance reports that count per model;
    - for Azure, an allowlist of deployments the record knows to be non-reasoning (grok-4-1-fast-non-reasoning, Mistral-Large-3) replaces
      the denylist regex.
- **C-AZ (condition for an Azure go; the builder's MEDIUM, confirmed).** No other writer of the TaxoArena day ledger may run during an Azure
  launch of this test. The alternative is a cross-test lock in `accepted_tests_ledger.append`, which is a TaxoArena change and the
  orchestrator's to schedule.
- **E3 LOW (D3 residual).** A clean filter injected through `GIT_CONFIG_*`, plus an assume-unchanged flag, lets an edited go config pass G2 / G3
  (#7 b). It needs deliberate tampering, and no go entry can arise by accident.
  - Fix: parse the go table from the pinned blob (`git cat-file blob <GO_CONFIG_BLOB>`), and run every git call with `GIT_*` removed from the
    environment.
- **E4 LOW (Q04).** `launch_alive`'s fail-safe branch (uninspectable counts alive) is untested. If it failed open, the label-only idempotence of
  `_append_launch` would skip the live launch's later attempts: the day ledger under-counts, though D1 stays bounded by the go ledger.
  - Fix: a selftest with `_proc_started` patched to "unknown". At launch end, append the go-ledger attempts minus those already recorded
    under `L<id>`.
- **LOW (process).** The builder's campaign runs 3 workers, and each worker's selftest spawns 2 children, so up to 9 Python processes run at
  once. The reviewer re-ran the campaign at 1 worker (3 processes at most).

### Author decisions needed (before a go)

- Serving, roster and cap. A go needs a decision id; it is above 8k calls for either API option.
- The consequence of thinking off for all: the API roster drops to 2 deployments, and gpt-oss, qwq, deepseek-r1 and magistral are out (the
  builder's question).
- E1c: whether an (I) statement followed by a sentence is read.

### Commands (scripts in E:/TaxoArena_tmp/review_fmp3/, read-only on every input; sandboxes only)

```
LC_ALL=C grep -a "\[GIN\] 2026/10/29" $LOCALAPPDATA/Ollama/server*.log | awk '{print $NF}' | sort | uniq -c   # 0 chat/generate
python -c "from load import load; m=load(); print(m.PROMPT_SHA, m.REGEX_SHA, m.protocol_digest(), m.go_table_for_run(m.GO_CONFIG))"   # #2
python race_parent.py races; python race_parent.py kill        # #5, #6 (2-3 child processes, own fake server each)
python d3_probe.py; python d3b.py                              # #7 (sandbox clone; OLLAMA_HOST=127.0.0.1:9)
python adv3.py; python adv3b.py; python adv3c.py; python adv3d.py   # #8-#10, E1 (136 strings, 15 timing families)
python settings_probe.py                                       # #11, #12, E2 (bodies, journal settings, thinking leak)
fresh-math-pipeline.py --selftest (TMP/TEMP/TMPDIR/BZ_SANDBOX=st); --dry-run --out dry       # #3, #14
python run_camp3.py own_mutants3.json mut_own 1; python run_camp3.py <worktree>/examples/fresh-math-pipeline_mutants.json mut_builder 1
PYTHONPATH=src python -m pytest tests/test_fresh_math_pipeline.py -q -p no:cacheprovider   # 43 passed
PYTHONPATH=src python -m pytest -q -p no:cacheprovider                                    # 986 passed, 1 skipped, 10 deselected
git -C Z:/FAC/TUBerlin/benchzoom merge-base master fresh-math-pipeline-3; sha256sum -c SHA256SUMS   # 033c79c; 16/16
```
