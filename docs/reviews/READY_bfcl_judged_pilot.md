# READY — BFCL-JUDGED-PILOT (`tools/analysis/bfcl_judged_pilot.py`)

Adversarial-reviewer READY of record, 2026-09-23, zero calls. Registration `docs/judge_v2_program.md`
L10965-L11237, commit 22c5d5f, AMENDED BY INSERTION at 6ccf2f7 (the ruling BFCL-REF-ORACLE at L11001 and the
five-item bracket at L11190). Instrument built at 1c43c20, amended at 66aaaf7, merged to main at a753c2f.

**VERDICT: READY**, under the conditions in section 8. Every number below was recomputed by the reviewer from
the corpus DB (`mode=ro&immutable=1`) and from the raw files, and `--selftest` and `--dry-run` were EXECUTED.
No posting mode was run past its gate; `BFCL_GO` was never exported; no cache exists; the corpus DB md5 is
unchanged (`5aff2f2fb3d972df9bcce1f94de6bcfc` before and after every command in this review); the night ledger
still reads `[]`.

## 1. The two shas pinned

| pin | value |
|---|---|
| script sha256[:16], LF-normalised (= the git blob, = `run_meta.script_sha256_16_lf`) | `fa38c1dbe2776314` |
| script sha256[:16], working-tree raw bytes (CRLF checkout) | `3546292c480123af` |
| `possible_answer/BFCL_v4_multi_turn_base.json` sha256[:16] (the REFERENCE OF RECORD) | `1fee67823b317571` |
| `dataset/BFCL_v4_multi_turn_base.json` sha256[:16] (the task statements) | `1a21a995d06fd6f2` |
| schedule hash (seed 42, 608 matches) | `bcf9d1654e68e4ca` |
| corpus archive_sha (first 12) | `6830ed13035c` |

`git diff --quiet HEAD -- tools/analysis/bfcl_judged_pilot.py` is clean; `git cat-file -p HEAD:... | sha256sum`
= `fa38c1dbe27763140e86...`, i.e. the LF pin is the committed blob.

## 2. The reference of record IS the per-task expected outcome, and cannot leak

- `read_ground_truth()` opens ONLY `experiment_results/agent/bfcl_raw/2025-12-16/dataset/possible_answer/
  BFCL_v4_multi_turn_base.json`, read-only, and keeps only `e["ground_truth"]`. `render_reference()` renders
  `Turn k: call ; call` lines into `REF_BLOCK`. Nothing else enters the block.
- `checker_text()` is GONE: `grep -n "checker_text"` returns only the CHECKER_TEXT_CUT class name (L73, L279,
  L1187, L1564). `grep -n "checker_details"` returns only the docstring (L68-L69): the column is never read.
- `grep -n "checker_output"` returns L512/L514 (the `Corpus` SELECT), L726-L728 (the NEGATIVE check inside
  `assert_no_per_side_verdict`), and two selftest fixtures. It reaches no prompt. `episodes.passed` and
  `episodes.error_type` are used only by the checker-disagreement FILTER and by `checker_winner`.
- The prompt is `q = tasktext[t] + refs[t][0]` plus the two capped traces. REVIEWER'S OWN SCAN over ALL 608
  assembled matches (both orders, 1,216 payloads): 0 occurrences of any side's `checker_output`, any side's
  `error_type`, `all_pass`, or `[Outcome checker report]` anywhere in the full user prompt. The only hit for the
  string `checker` is the block header's own sentence ("the task's checker is state-based"), 608/608, by design.
- ORDER-INVARIANCE, asserted on ALL 608 matches, not the first: `u1.count(ref) == u2.count(ref) == 1`,
  `u1.count(q) == u2.count(q) == 1`, and `u1 == build_user_prompt(q, tA, tB)`, `u2 == build_user_prompt(q, tB, tA)`.
  **0 identity failures.** The block is byte-identical in the two posted orders; the orders differ only by the
  trace swap. No transposition hazard.
- `grep -n "ORACLE_HAZARD"`: one definition (L300), one use (L741, inside the `SystemExit` of
  `assert_no_per_side_verdict`), plus docstring/selftest mentions. It fires on NO live path: the per-side form is
  not constructible by any flag — there is no flag, no config key and no branch that reads `checker_output` or
  `checker_details` into a prompt. CONFIRMED.

## 3. `assert_no_per_side_verdict` — what it actually catches (read this, not the docstring)

The reviewer tried to defeat it with 17 constructed leaks. It **refused**: the exact `checker_output` of either
side (len > 3, substring), either side's `error_type`, the tokens `multi_turn:`, `all_pass`,
`[Outcome checker report]`, and `\bPASS\b` / `\bFAIL\b`.

It **MISSED**: lower-case `pass`/`fail`, `passed`/`failed`, the checker's error text with the `multi_turn:` prefix
stripped, `allPass`, `all pass` (spaced), a `checker_details` JSON fragment, and `Model A: Pass` (mixed case).

Ruling: **not a blocker, and not a live hazard** — the guard is defence in depth over a task statement built only
from `possible_answer` and the dataset user turns, and section 2's scan proves no verdict material reaches any of
the 1,216 payloads. But the docstring's "checks every assembled task statement for it" claims more than the
predicate does. The READY records the predicate as it is; DO NOT cite the guard as the guarantee — the
construction is the guarantee.

FALSE-POSITIVE RISK (the coder's "0 false positives on 608 statements"): CONFIRMED on this corpus — all 608
statements assembled with no refusal. But the mechanism is not as safe as claimed: a passing episode's
`checker_output` is the literal string `PASS` (2,950 episodes), so the substring rule refuses on ANY task
statement containing `PASS` as a substring — the reviewer showed that a ground truth `set_mode(mode='PASS')` AND a
ground truth `login(PASSWORD='x')` are both refused. The direction is fail-closed (a refusal, never a leak), and
it is deterministic and already exercised: the dry-run assembled all 608 without one. No action.

## 4. The counts, re-derived by the reviewer's own SQL (not by the script)

Own script over `file:...bfcl_result_2025-12-16.db?mode=ro&immutable=1`, 21 headline pairs x 57 EVAL base tasks:

| denominator | registered | script's dry-run | reviewer's own recomputation |
|---|---|---|---|
| headline matches (both TERMINATED) | 1,113 | 1,113 | **1,113** |
| headline after the filter | 461 | 461 | **461** |
| grok-FC stratum matches | 385 | 385 | **385** |
| grok-FC after the filter | 147 | 147 | **147** |
| both-present before the termination rule | — | 1,197 / 399 | **1,197 / 399** |
| pass-differs WITHOUT the both-decided clause | — | 461 / 147 | **461 / 147** |
| deciding subset (461 minus 3 non-judgeable) | 458 | 458 | **458** |
| tasks spanned by the deciding subset | (reg. says 57) | 49 | **49** |

Termination (`bfcl_term_v1`), reviewer's own count: every agent 57/57 TERMINATED except
`meta-llama_Llama-3.3-70B-Instruct-FC` 43 TERMINATED / **14 CAP_HIT** / 0 ERROR. CONFIRMED: only that one agent
has CAP_HITs, 14 of 57.

C2, recomputed by the reviewer from the raw result files (not via the script): **EMPTY 1 + DEGENERATE 0 = 1 of
385** terminated 7-agent base EVAL episodes; the single empty trace is `multi_turn_base_179` x
`gemini-2.5-flash-FC`; it removes **3 of 461** matches, giving the deciding subset 458. The error-type object
beside it: `multi_turn:empty_turn_model_response` on **56 of 385** (0.1455). All CONFIRMED to the digit.

NOTE (LOW): the both-decided clause of the filter is INERT on this corpus — kept equals pass-differs in both
strata (461 and 147). The script prints both readings, so nothing is hidden.

NOTE (MEDIUM, disclosure): the cluster unit for C1 is **49 tasks, not the registered 57** (8 of the 57 EVAL tasks
carry no checker-disagreeing match). The code prints the true count, so the outcome will read "cluster unit = the
49 TASKS"; the registration's "SE ~0.024 at 461 matches on 57 tasks" was an expectation over 57 clusters and the
realised SE will be slightly larger. Read the printed SE, never 0.024.

## 5. The two prompt strings — APPROVED (amendment item (2) makes this the reviewer's call)

Both are quoted here verbatim as printed in full by `--dry-run`; a relaunch differing on either is REFUSED by
`pin_meta` (`run_meta.system_bfcl` / `run_meta.rubric_bfcl`).

> **SYSTEM_BFCL:** You are judging two attempts by tool-using agents at the same multi-turn function-calling task. Each attempt is shown as its decoded tool-call sequence followed by the final environment state. The task statement carries the corpus's own ground-truth call sequence for the task: one sequence that solves it, not necessarily the only one.

> **RUBRIC_BFCL:** Rank by: (1) whether the attempt reaches the outcome the task asks for, read against the ground-truth sequence and against your own reading of the task; (2) whether the calls are valid and in an order that could produce that outcome; (3) whether the final environment state is the state the task asks for. A different sequence that reaches the same final state is as good; an attempt that does not reach the outcome cannot win on style, on length or on the number of calls.

Ruled against the amendment's three prohibitions:

- **names the checker's verdict?** NO. Neither string contains `verdict`, `error_type`, `all_pass`,
  "the checker says", or `pass`/`passed`/`fail`/`failed` as words (the selftest asserts each of these and it was
  EXECUTED and passed). Neither mentions a checker at all.
- **promises the reference is correct?** It says the ground-truth sequence is "one sequence that solves it, not
  necessarily the only one". That IS an assertion that the sequence solves the task — but it is the exact sentence
  the ruling MANDATES (L11020-L11023: "says it is ONE correct solution and not necessarily the only one"), and it
  is strictly weaker than STAGE3-MATH's block header at the 0.958 rung, which reads `[Verified reference answer]`.
  APPROVED.
- **tells the judge to defer?** NO, the opposite: "read against the ground-truth sequence AND against your own
  reading of the task", and "A different sequence that reaches the same final state is as good."

`system_prompt()` is byte-for-byte the STAGE3-MATH construction (`prompt_v2.v2_system_template()` with the two
slots plus `rj.SCHEMA_INSTRUCTION`), and `payloads()` mirrors `stage3_math.payloads()`
(`q = text + REF_BLOCK % target`).

**V2_INHERITED_NOTE — ruled: KEEPING IT IS RIGHT.** The template's inherited sentence "The question carries a
reference solution (marked as produced independently; it may be wrong)" does misdescribe this object: the
per-task expected outcome is the corpus's ground truth, not an independently produced solve, and it is not
plausibly wrong. But (a) the misdescription runs in the SAFE direction — it can only reduce deference to the
reference, which is the hazard the ruling removed, never increase it; (b) STAGE3-MATH's 0.958 rung carried the
identical sentence over a `[Verified reference answer]` block, so removing it here would make this test's recipe
differ from the rung it positions itself against, which is the one comparison the registration buys; (c) it is
disclosed verbatim in `V2_INHERITED_NOTE`, printed by `--dry-run` and quoted in the outcome. Keep it, disclose it,
and do not read the two sentences' tension as a defect of the instrument.

## 6. Gates, hygiene and accounting — proved by command

- **READY + BFCL_GO, both legs.** `python tools/analysis/bfcl_judged_pilot.py --pilot 12` with no token gives
  `[READY] --pilot 12 refused (0 calls, nothing opened): BFCL_GO=None (needs '9') | docs\reviews\READY_bfcl_judged_pilot.md MISSING.`,
  exit 1. The reviewer also drove `launch("probe"/"pilot"/"run")` in-process with `rr.call_judge_full` replaced by
  a raiser: all three refused at `go_gate`, the FIRST statement of `launch()`. **No cache file was created**
  (`experiment_results/agent/bfcl_judged_pilot.db` does not exist). The second leg (token present, READY absent)
  is asserted by `--selftest` step 12, which was EXECUTED and passed.
- **DBGUARD.** `--dry-run` last line, verbatim:
  `[DBGUARD] sqlite3.connect: 1 call(s) in this process: experiment_results\agent\bfcl_result_2025-12-16.db | whitelist [':memory:', 'bfcl_judged_pilot.db', 'bfcl_result_2025-12-16.db'] | never opened: twenty_newsgroups_cache_v1.db, embeddings_cache.db, snapshots.db, snapshots_frozen.db, mmlu_pro_dataset_cache_v2.db, multicorpus_cache_v1.db, ratings.db, ratings_x12.db`
  Exactly one DB opened, read-only and immutable. `--selftest`'s last line shows `:memory:` only. `pool_guard` is
  not imported. The selftest exercises the refusal on all 8 forbidden names plus a foreign verdict cache.
- **Night ledger.** `experiment_results/night_calls_2026-09-23.json` exists and contains `[]`; `night_line()` read
  it at the dry-run (`0 launch rows`) and printed `cumulative grok calls tonight 0 of 14000`. It REFUSES, does not
  trim, at the ceiling (selftest step 12 drives `night_line(14001)` to `[NIGHT] REFUSED`). A malformed ledger is a
  SystemExit (fail-closed). `night_ledger_append` is append-only via tmp + `os.replace`.
- **Fail-closed fingerprint.** `check_fingerprint` accepts only `azure:grok-4-1-fast-non-reasoning`, plus
  `azure:refusal` with `finish_reason content_filter` (rule 10). Four negative cases asserted in the selftest.
  A mismatch halts the run and caches nothing for that call.
- **Body / temperature.** Body keys `('model','max_tokens','messages')`; `assert_body_copy` checks the SOURCE of
  `rr.payload_body` and `rr.call_judge_full`; `rr.payload_body("s","u") == post_body("s","u")` is asserted.
  Temperature is never sent (Amendment 1 D2).
- **run_meta pinning.** Cap, protocol, rosters, reference form, schedule hash, both prompt strings and both raw
  shas are pinned; any differing relaunch key REFUSES. Schedule drift REFUSES.

## 7. What P4 and P5 will read, and why — stated NOW so no one can read it as a surprise

Both are determined at ZERO CALLS by the dry-run and are a property of the bands, not of the corpus:

- **P4 will read 0.0000, FAILED.** Measured per-side estimated tokens on the 1,216 base-stratum sides:
  median 428, p95 699, **max 1,169** against the 2,500-token cap. **Truncated sides 0 of 1,216; truncated matches
  0 of 608; state-over-cap sides 0.** The cap is INERT on this stratum, so the whole truncation machinery
  (`ARTEFACT_OVER_CAP`, the ~180-character marker, `STATE_OVER_CAP`) is unexercised on this run — it is exercised
  only by the selftest. P4's band [0.04, 0.12] was calibrated on the admission pilot's distribution (median 453,
  p95 2,422, max 7,199), which is POOLED OVER ALL FOUR STRATA including `long_context` (admission line (d), 300
  drawn episodes; the one artefact-less episode is a `long_context` one). The base stratum alone is an order of
  magnitude shorter. **A FAILED P4 is a MIS-CALIBRATED BAND, exactly as amendment item (3) ruled for P5, not a
  surprise and not a finding about the corpus.** The outcome must say so in those words.
- **P5 will read 1/385 = 0.0026, FAILED.** C2 is a TRACE-SHAPE class; the band [0.10, 0.25] was calibrated on the
  18.3% `empty_turn_model_response` ERROR-TYPE share, again pooled over all four strata. The on-corpus error-type
  share is printed beside it (56 of 385 = 0.1455, i.e. the admission's object roughly reproduces on the base
  stratum). Item (3) already rules this a mis-calibrated band. No definition may be changed after the count.

Neither failure touches C1, C2's HELD condition, C3 or the ladder.

## 8. CONDITIONS — binding on phase B

1. **`--override-guard` is FORBIDDEN in this test.** Two places in the script claim it "is recorded in run_meta"
   (L1334, L1824); it is NOT — `OVERRIDE_GUARD` is never persisted anywhere. If the 5% guard fires, STOP and
   report; do not post past it.
2. **The pilot line must read 12 of 12.** `post()` has the sibling instrument's hole:
   `except Exception: err += 1; continue` leaves NO cached row, and `guard_numbers` counts only matches with BOTH
   orders cached, so errored jobs shrink the guard denominator instead of failing it. (`rr.call_judge_full`
   retries 6x on 408/429/5xx and caches a content-filter 400 as an unusable row, so this bites only on a hard
   error.) After `--pilot 12` the operator must read the printed
   `[GUARD] ... matches with both orders N of 12` and the `done: ok N, errors N` line, and proceed to `--run` ONLY
   if both orders are present on all 12 non-non-judgeable pilot matches AND `errors 0`. Any `errors > 0`: stop,
   report the count, reconcile the night ledger from the cache before any further launch.
3. **Night-ledger reconciliation.** `night_ledger_append(ok, ...)` records CACHED ROWS, not HTTP attempts: retries
   and errored attempts are uncounted, and the append is SKIPPED entirely if `post()` raises the `[FINGERPRINT]`
   SystemExit. After any halted or errored launch the operator reconciles the actual count from the cache into
   `experiment_results/night_calls_2026-09-23.json` BEFORE the next launch (registration item (4)).
4. **Quote the printed cluster count, not 57.** C1's interval of record is the point plus/minus 1.96 x the
   clustered SE over the **49** tasks the deciding subset spans; the percentile interval is printed beside it, and
   C1 is UNDETERMINED if the two disagree about 0.75 (amendment (5)(d), implemented and verified by reading
   `analyze()`).
5. **P4 and P5 are reported with section 7's sentence** ("a mis-calibrated band, not a surprise"), and the cap's
   inertness (0 of 1,216 sides truncated, max 1,169 of 2,500 estimated tokens) is stated in the outcome so the
   manager's reversible choice (i) is read against a measured cost of zero.
6. **Do not cite `assert_no_per_side_verdict` as the leakage guarantee** (section 3). Cite the construction: the
   task statement is the dataset user turns plus the `possible_answer` render, and 0 of 1,216 assembled payloads
   carry any verdict material.
7. Nothing in the outcome, ledger, thesis or blog may quote the REJECTED per-side form, and A is never placed
   beside 0.958 except under the CROSS-CORPORA CAVEAT the script prints verbatim.
8. `experiment_results/night_calls_2026-09-23.json` is currently UNTRACKED by git. Commit it (path only) once the
   night's launches are recorded, so the count of record survives.

## 9. The phase-B command sequence

```
# 0. re-verify at zero calls (must reproduce section 10 exactly)
python tools/analysis/bfcl_judged_pilot.py --selftest
python tools/analysis/bfcl_judged_pilot.py --dry-run

# 1. commit this READY (path only), then the run-operator exports the token
$env:BFCL_GO = "9"              # PowerShell;  export BFCL_GO=9  in bash

# 2. the item-19 preflight: 100 calls into the `probe` table, never an arm
python tools/analysis/bfcl_judged_pilot.py --probe
#    STOP unless the probe prints: item-19 criterion (no cell above 5% length): MET

# 3. the 12-match pilot: 24 calls, inside the 922
python tools/analysis/bfcl_judged_pilot.py --pilot 12
#    STOP unless the guard line reads both orders 12 of 12, unusable <= 5%, and "errors 0" (condition 8.2)

# 4. the run: the remaining matches of both strata (resume = relaunch)
python tools/analysis/bfcl_judged_pilot.py --run

# 5. the readout (refuses a partial cache; writes the write-once outcome)
python tools/analysis/bfcl_judged_pilot.py --analyze
```

Expected bill: probe 100 + headline 922 + self-preference 294 = **1,316** calls, ceiling 3,096 (structurally
unreachable: the schedule is 608 fixed matches and no cached row is re-posted, so the maximum postable is
100 + 1,216 = 1,316). Night ceiling 14,000, currently 0 posted.

## 10. The expected verbatim lines (a launch that does not reproduce these is a DIFFERENT instrument)

```
[POOL] BFCL pool of record p2035adddedd1becb: 57 EVAL base tasks, id read from the FILE NAME of experiment_configs\reserved_pool_frozen_bfcl_p2035adddedd1becb.json (no hashing, pool_guard NOT imported: this test has no MMLU-Pro pool of record and touches no p2dca21ab5f4ef3ae / paeec37aa28063c75 row)
corpus bfcl_result_2025-12-16 snapshot 2025-12-16 archive_sha 6830ed13035c | agents 8 | base-stratum EVAL tasks 57 | episodes 6400 (mode=ro&immutable=1)
  headline_matches   registered  1113 | recomputed  1113
  headline_filtered  registered   461 | recomputed   461
  grok_matches       registered   385 | recomputed   385
  grok_filtered      registered   147 | recomputed   147
  both-present pairs before the termination rule: headline 1197, self-preference 399 | pass-differs WITHOUT the both-decided clause: headline 461, self-preference 147 (the filter of record adds that clause)
  meta-llama_Llama-3.3-70B-Instruct-FC     TERMINATED  43 | CAP_HIT  14 | ERROR   0  (of 57)
C2 NON-JUDGEABLE CLASS (declared in the header before any count): EMPTY 1 + DEGENERATE 0 = 1 of 385 base-stratum EVAL TERMINATED episodes of the 7-agent roster (0.003); matches removed from the deciding subset 3 of 461 (0.007). BESIDE IT (a different object, the admission's 18.3%): episodes whose error_type is multi_turn:empty_turn_model_response: 56 of 385 (0.145)
  rendered block length over the 57 tasks: min 339, median 609, p95 943, max 1118 characters (= 279 estimated tokens at the max) | CHECKER_TEXT_CUT at 1200 characters: 0 of 57 TASKS (denominator TASKS, not sides)
ARTEFACT CAP 2500 estimated tokens (chars/4; the manager's reversible choice (i)): per-side estimated tokens median 428 p95 699 max 1169 | truncated sides 0 of 1216 (0.000) | truncated matches 0 of 608 | state-over-cap sides 0
SCHEDULE fixed at this dry-run (seed 42; hash bcf9d1654e68e4ca): headline 461 matches + self-preference 147 = 608; probe 50 matches (preflight, never an arm) + pilot 12 matches inside the headline count
BILL: 1216 payloads assembled, 0 posted | --probe 100 calls, --pilot 24 calls (inside the 922), --run 1216 calls remaining at most | registration: probe 100 + headline 922 + self-preference 294 = 1,316 expected, ceiling 3,096
script sha256[:16] LF fa38c1dbe2776314 | raw-bytes 3546292c480123af
[NIGHT] cumulative grok calls tonight 0 of 14000 (Amendment 9 hard ceiling; ...) | this launch (--dry-run (0 calls)) would post at most 0 -> 0 | source: experiment_results\night_calls_2026-09-23.json (0 launch rows); this test's own cache holds 0 posted rows
[DBGUARD] sqlite3.connect: 1 call(s) in this process: experiment_results\agent\bfcl_result_2025-12-16.db | whitelist [':memory:', 'bfcl_judged_pilot.db', 'bfcl_result_2025-12-16.db'] | never opened: twenty_newsgroups_cache_v1.db, embeddings_cache.db, snapshots.db, snapshots_frozen.db, mmlu_pro_dataset_cache_v2.db, multicorpus_cache_v1.db, ratings.db, ratings_x12.db
```

The first payload of the headline deck is `multi_turn_base_147`, `DeepSeek-V3.2-Exp-FC` (Model A) vs
`claude-sonnet-4-5-20250929-FC` (Model B), checker winner `claude-sonnet-4-5-20250929-FC`.

## 11. Defects, ranked (none is a blocker)

| # | severity | defect | disposition |
|---|---|---|---|
| 1 | MEDIUM | pilot-guard denominator shrinkable by errored jobs (no cached row) | condition 8.2 (operator reads "both orders N of 12" and "errors 0") |
| 2 | MEDIUM | `--override-guard` claims to be recorded in run_meta; it is not | condition 8.1 (flag forbidden) |
| 3 | MEDIUM | cluster unit is 49 tasks, not the registered 57; SE 0.024 was an expectation | condition 8.4 (quote the printed SE and q) |
| 4 | MEDIUM | P4 (and P5) fail deterministically at zero calls on bands calibrated over all four strata | condition 8.5 / section 7 |
| 5 | LOW-MED | night ledger counts cached rows, not HTTP attempts; append skipped on a `[FINGERPRINT]` halt | condition 8.3 |
| 6 | LOW-MED | `assert_no_per_side_verdict` catches far less than the docstring claims (12 of 17 constructed leaks pass) | condition 8.6; not reachable, see section 2 |
| 7 | LOW | the substring rule on `checker_output == "PASS"` would refuse a statement containing `PASSWORD`; 0 occurrences here | none (fail-closed, verified absent on all 608) |
| 8 | LOW | the filter's both-decided clause is inert (kept equals pass-differs in both strata) | none (both readings printed) |
| 9 | LOW | the 3,096 test ceiling is not enforced in code, only the 14,000 night ceiling | none (structurally unreachable, section 9) |
| 10 | LOW | `experiment_results/night_calls_2026-09-23.json` untracked | condition 8.8 |

Reviewed by the adversarial-reviewer, 2026-09-23. `--selftest` and `--dry-run` EXECUTED; `--probe`, `--pilot` and
`--run` were driven only far enough to prove the gate refuses; `BFCL_GO` was never exported; zero calls posted.

---

## 12. [RE-PIN 2026-09-23 by the adversarial-reviewer, after the step-(7) halt — insertion only; §§1-11 stand as written except where this section names them]

**ONE-LINE VERDICT: READY — resume at `--run`.** Zero calls posted in this re-pin; `BFCL_GO` never exported.

### 12.1 What halted, and the new shas

`--run` crashed with `TypeError: %d format: a real number is required, not NoneType` at L1306, the first statement
of `launch()`, ONE LINE BEFORE `go_gate`: the label dict was eager, so `"--pilot %d" % n` was evaluated on the
`--run` branch, where the CLI passes `n=None`. Zero calls posted, no cache row, no ledger row.

Fixed at d1ead84, merged to main at **95c6d92**. **The shas of §1 are SUPERSEDED for the script** (the four data
shas, the schedule hash and the archive_sha are unchanged):

| pin | was (§1) | **now** |
|---|---|---|
| script sha256[:16] LF (= the git blob, = `run_meta.script_sha256_16_lf_relaunch`) | `fa38c1dbe2776314` | **`5e9db53b894eeccb`** |
| script sha256[:16] raw bytes (CRLF working tree) | `3546292c480123af` | **`72ecb9777f927eb1`** |

Recomputed by the reviewer with `hashlib` over the working-tree bytes: CRLF `72ecb9777f927eb1`, LF
`5e9db53b894eeccb`. AGREE to the digit with the coder's pins.

### 12.2 The diff is what it is said to be

`git diff a753c2f 95c6d92 -- tools/analysis/bfcl_judged_pilot.py` → **49 insertions, 1 deletion**, three hunks and
nothing else:

- the one behavioural line, `what = {"probe": ..., "pilot": "--pilot %d" % n, "run": "--run"}[mode]` →
  `what = {"probe": ..., "run": "--run"}.get(mode) or ("--pilot %d" % n)`;
- `cli_launch_shapes()` (additive), which `ast`-parses THIS FILE'S OWN `__main__` block and evaluates each
  `launch(...)` argument against an argparse Namespace;
- selftest case 14 (additive) plus its printed line.

CONFIRMED: no other line of the instrument moved. `pin_meta` is **byte-untouched** (the diff mentions neither
`pin_meta` nor `script_sha256_16_lf`: `grep -c` → 0) and still exempts `script_sha256_16_lf` from its refusal set
(`bad = [... if k != "script_sha256_16_lf" ...]`), recording the new sha as `script_sha256_16_lf_relaunch` with a
printed NOTE. **The resumption of the 124 posted rows is therefore safe**, and the operator will see a NOTE, never
a `[META] REFUSED`.

### 12.3 Executed

`--selftest` → `selftest OK: 14 cases | case 14, the CLI's own argument shapes read from this file's __main__
dispatch and each driven into launch(): launch('probe', 50, 8), launch('pilot', 12, 8), **launch('run', None, 8)**
-> all three reached go_gate and were REFUSED there with the right label`. The real `n=None` shape is now driven.

`--dry-run --no-payload` diffed line by line against §10's capture: **exactly the five named lines moved, and no
other** — the sha line, `cache ... (EXISTS)`, the READY gate now `exists, committed 5d1dde1`, `[NIGHT] 1752 of
14000 ... (4 launch rows); this test's own cache holds 124 posted rows`, and `[DBGUARD] 2 call(s)` (the second
being this test's own cache opened `mode=ro` by `own_posted_calls()`, which only happens once the cache exists).
Every denominator, the termination table, C2, the reference lengths, the cap line, the schedule hash
`bcf9d1654e68e4ca` and the bill are byte-identical to §10. Corpus DB md5 `5aff2f2fb3d972df9bcce1f94de6bcfc` and
cache md5 `acbf2a7b359c344252482245e328f6d3` unchanged by every command in this re-pin.

### 12.4 The relaunch arithmetic — CONFIRMED from the cache

`verdicts` holds **24 rows on 12 mids** (both orders on all 12; `finish` all `stop`; one fingerprint
`azure:grok-4-1-fast-non-reasoning`; 0 unusable), `probe` holds **100 rows on 50 mids**, total 124 = the
`[NIGHT]` line's own-rows count. `launch()` builds `have` from `table`, which is `verdicts` for every non-probe
mode, so the probe's 100 rows are in a different table and are irrelevant to the skip. **1,216 − 24 = 1,192 calls
remaining**, taking the night from **1,752 → 2,944 of 14,000**. The ledger's 4 rows (IFEVAL 48 + 1,580, BFCL probe
100 + pilot 24 = 1,752) are committed at ca2e346, which **discharges condition 8.8**.

### 12.5 The review-method finding (mine, and it belongs here)

§6 of this READY says `launch("probe"/"pilot"/"run")` were driven in-process and "all three refused at `go_gate`,
the FIRST statement of `launch()`". **That statement was false for the run branch.** I drove all three modes as
`launch(mode, 12, 1)` — a non-None `n` — because that was the convenient shape, not the shape the dispatch passes.
The CLI calls `launch("run", None, a.workers)`. With `n=12` the eager label formats fine and the call reaches the
gate; with `n=None` it raises one line earlier. I verified a shape the program never uses, and reported the
conclusion as if I had verified the program.

**The general lesson, for every reviewer of every instrument in this programme: an in-process drive of an entry
point must use the argument shape the dispatch actually passes, READ FROM THE DISPATCH, not the shape the reviewer
finds convenient.** If the reviewer must hard-code a shape, the shape is a claim and must be recomputed from the
dispatch like any other number. This defect was invisible to `--selftest`, `--dry-run`, `--probe` and `--pilot`
for exactly the same reason it was invisible to me: every one of them exercises a branch where `n` is not None.
`cli_launch_shapes()` is the right fix precisely because it *reads* the shapes instead of *asserting* them — the
same "count checks beat presence checks" rule this programme already applies to data.

### 12.6 Conditions

Conditions **8.1–8.7 carry over unchanged**. **8.8 is DISCHARGED** (the ledger is committed at ca2e346; keep
appending and keep committing it). Three additions:

9. **At the first `--run` relaunch, read two lines before letting it proceed:** the `NOTE: cache first produced by
   script LF sha fa38c1dbe2776314; this script is 5e9db53b894eeccb (resume recorded)` (expected, benign — §12.2),
   and `to post 1192 calls` with `[NIGHT] ... 1752 ... would post at most 1192 -> 2944`. Any `[META] REFUSED`, any
   `[SCHEDULE] REFUSED`, or a to-post count other than 1,192 is a STOP.
10. **The instrument's sha of record for everything posted from here is `5e9db53b894eeccb` (LF) /
    `72ecb9777f927eb1` (CRLF).** The outcome must state that the cache was opened under `fa38c1dbe2776314` (probe
    + pilot, 124 rows) and completed under `5e9db53b894eeccb`, and that the difference is the one-line label fix,
    which touches no prompt, no denominator, no schedule and no statistic.
11. LOW, noted not blocking: the fix's `.get(mode) or (...)` makes an *unknown* mode fall through to the pilot
    label instead of raising `KeyError`. Case 14 asserts the dispatch drives exactly `probe` / `pilot` / `run`, so
    the fall-through is unreachable; if a fourth mode is ever added, case 14 fails first, which is the right order.

### 12.7 Operational hazard, for the record

The engine-coder ran its dry-run by copying the script into the main checkout and then deleting it, not realising
the path was already TRACKED there. That left a working-tree deletion of a tracked file and blocked the merge
until it was restored. Nothing was lost. The rule this implies, alongside CONTEXT rule 8's shared index: **a
worktree agent that needs to execute in the main checkout must not create-then-delete a path there — check
`git ls-files --error-unmatch <path>` first, and never `rm` a path git tracks to clean up after itself.**

Re-pinned by the adversarial-reviewer, 2026-09-23, after the step-(7) halt. `--selftest` and `--dry-run` EXECUTED
on 95c6d92; `--run` NOT run; `BFCL_GO` never exported; zero calls posted; both DBs byte-identical before and after.
