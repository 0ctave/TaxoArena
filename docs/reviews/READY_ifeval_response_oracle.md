# READY — IFEVAL-RESPONSE-ORACLE (`tools/analysis/ifeval_response_oracle.py`)

Adversarial reviewer, 2026-09-23, PHASE B head. **READY, with the five binding conditions in section 6.**
Zero calls were posted by this review. This review is the ruling's condition (d) and the FIRST EXECUTION of the
script: `--selftest`, `--dry-run`, `--compare-math`, `--pilot 12` (refused at the gate), `--run` (refused at the
gate) and `--analyze` (refused, no cache) were all run by the reviewer at zero calls.

## 1. Object under review, pinned

| item | value |
|---|---|
| script | `tools/analysis/ifeval_response_oracle.py`, 1,206 lines, 80,826 bytes on disk (CRLF checkout) |
| sha256[:16], LF-normalised (the sha `run_meta.script_sha256_16_lf` pins) | **ee7df0e64ab5caab** |
| sha256[:16], bytes on disk (CRLF; `run_meta.script_sha256_16`) | **ca9ee11bc9f13c50** |
| built at | 3c79ae4 (branch `ifeval-response-oracle`), merged to main at **1b62071** |
| registration | `docs/judge_v2_program.md` L11148-L11329, commit 4c8379c |
| ruling | `docs/agents/leads/2026-09-23_ifeval_ruling.md` §(6), af116f8 |
| population | 407 key-decidable IFEval matches, schedule hash **ba4a0ac8a2364a49** |
| control system string sha256[:16] | **ebaec3a0f4b81f33** |
| control `reference()` on the first match's target, sha256[:16] | **84fff82bc7154bba** |

Any change to the script before the first posted call re-pins both shas and requires a re-review; a change AFTER
the first posted call cannot be resumed into the same cache (`script_sha256_16_lf` is inside the compared
`run_meta`, so `pin_meta` REFUSES) and is a new session.

## 2. What was verified, by command

1. **`--selftest`**: 32 checks, all OK, exit 0, no database opened. Includes the negative transposition
   regression (a deliberately transposed order 2 is refused, hard `SystemExit`).
2. **`--dry-run`**: exit 0, **1,628 payloads assembled, 0 posted**, 0.66 s.
3. **Databases opened** (`sqlite3.connect` spy over the whole dry-run, import time included): exactly three, all
   `mode=ro` — `experiment_results/multicorpus/gen_arena_grok.db`, `multicorpus_cache_v1.db`,
   `experiment_results/multicorpus/checker_answers_v1.db`. **No MMLU-Pro pool, no board, no ratings, no snapshot,
   no embedding cache, none of the TOPIC-PARTITION-20NG chain's DBs.** `pool_guard` is not imported at all (it is
   named only in the docstring), which is stronger than the registration's "imported without opening one";
   `population_line()` is the first printed line and says so in terms.
4. **Nothing was written**: size+mtime of all three source DBs identical before and after every invocation
   (`gen_arena_grok.db` 12,390,400 / 1789296724 unchanged); `experiment_results/multicorpus/ifeval_response_oracle*`
   still does not exist after the dry-run, both gate refusals and `--analyze`.
5. **Population, recomputed independently** (reviewer's own SQL, not the script's): IFEval verdicts 1,200 over 162
   distinct questions; `invalid=0` 1,200; key-decidable (both contestants keyed, keys differ) **407** over **122**
   distinct questions, 55 distinct pairs. Fail-closed conditions recomputed over the whole population: 0 missing
   checker rows, 0 `instruction_ids` disagreements with `corpus_questions.target.instruction_id_list`, 0
   `len(vector) != n_constraints`, 0 rows where `all(strict_vector) != key` or `all_pass_strict != key`, 0 empty
   traces, **0 non-terminated contestants** (so the deciding subset = 407). `eval_results_mathfix` touches 0 IFEval
   rows, so the script's `key_correctness()` is literally GEN-ARENA's reading for this corpus.
6. **Control byte-identity by construction, not by copy** — four independent checks:
   - the strings are imported (`ga.SYSTEM_BY_SOURCE['IFEVAL']`, `ga.RUBRIC_BY_SOURCE['IFEVAL']`), never retyped;
   - the extracted `reference()` source is byte-identical to `generative_arena.py` L104-L116 (dedented);
   - the live nested function GEN-ARENA calls (its code object taken out of `ga.judge.__code__.co_consts` and
     bound to `ga.__dict__`) and the script's inspect-extracted, exec'd copy return **identical strings on all 541
     IFEval targets** — 0 mismatches; the function has no free variables, so the `exec` namespace `{"json": json}`
     is faithful;
   - a shadowed `generative_arena.py` was reworded five ways: the system-string first sentence, the L124-L125
     assembly line, the L112 `q = text + reference(source, target)` line and the `reference()` signature are each
     **REFUSED** (exit 3/4, no arm assembled). Two rewords are **NOT** refused — see defect D2.
7. **Treatment block against the ruling §(6)**: the header and the three example lines are asserted against the
   ruling FILE (not a constant), and the file is independent of the script, so the assertion is not circular.
   Rendered over the **whole** population (814 blocks, 224 distinct constraint lines), every line matches
   `^- <id> [(kwargs)] — PASS|FAIL$`: no aggregate, no "3 of 3", no `all_pass_strict`, no loose field, no verdict,
   no cross-response comparison, no STACK-v2 "may be wrong" wrapper. Blocks carry 1 / 2 / 3 constraints
   (408 / 336 / 70).
8. **Transposition**: `assert_transposition` runs on the POSTED bytes (`extract_blocks` re-reads the assembled
   user string) for **every** assembled treatment match in both `--dry-run` and `run()`, not a sample; it is a hard
   `SystemExit`; it also refuses when the two slots carry the same block while the vectors differ. Verified on all
   407 in the dry-run. The negative case is a real regression test in `--selftest`.
9. **Gates**: `go_gate()` is the first statement of `run()`, before `assert_registration_quotes`, before
   `configure_rr`, before `rr.load_env` and before `population()` opens anything. Confirmed by execution:
   `--pilot 12` and `--run` both exit 1 with `[READY] ... refused (0 calls, no database opened)` and no cache file
   is created. The gate requires the READY to be **tracked and clean in git**, not merely present.
10. **Payload**: `payload_body` equals `rr.payload_body` key for key; the source assertion on
    `rejudge_reasoning.py` holds; `model=grok-4-1-fast-non-reasoning`, `max_tokens=8192`, **no `temperature` key**
    (Amendment 1 D2). `rr` module defaults are `MAX_TOKENS 8192` / `TEMPERATURE None`, which is exactly what
    GEN-ARENA posted (it set only `JUDGE_MODEL`), and `call_judge` is `call_judge_full(...)[:4]`, same body.
    `prompt_v2.py` last changed 2026-09-09 (20c3f42), before GEN-ARENA's 2026-09-13 run, so the v2 template has not
    drifted under the control arm.
11. **Fingerprint / cache / accounting**: `check_fingerprint` is per call, fail-closed, with the single
    `azure:refusal` + `content_filter` exemption (rule 10; such a row is cached as unusable, never dropped from the
    guard denominator). The cache is a NEW file with `PRIMARY KEY (match_id, arm)`; the 25 table columns line up
    one-for-one with the 25-element row tuple (`finish1`/`finish2` at indices 15/16, which is what the progress
    counter reads). `pin_meta` refuses a relaunch differing on protocol, cap, temperature, arm text, schedule hash
    or script LF sha, printing both sides. Resumption skips cached `(match_id, arm)` rows; `posted_here =
    2 * len(done)` and `planned = 2 * len(jobs)` are the correct call arithmetic (pilot 48, run 1,580, total 1,628).
12. **MATH-comparison refusal is code**: `--compare-math` exits 1 with the refusal text; `scrub()` refuses any
    outcome text containing `0.958`, `0.993`, `STAGE3-MATH-CAPFREE`, `reference ladder`, `CHECKER_OUTPUT (MATH)`
    (verified in the selftest and by reading the `--analyze` write path: every outcome file — record, `_partial`,
    `_PILOT` — passes through `scrub` before it is written). `--analyze` cannot bypass it.
13. **DECLARED NOT SCORED**: the four items (GEN-ARENA criterion 2 rho, criterion 3 the BRIDGE, the exploratory
    router-cost readout, CONSENSUS-FIT's signed-contrast logistic) are printed with their reasons in `--analyze`
    and nothing in the script computes them; C4's recorded limit prints unconditionally. The outcome of record is
    WRITE-ONCE and a partial cache exits 2 into a banner-headed `_partial` / `_PILOT` file.

## 3. The support discrepancy, recomputed (this is the reading, not the protocol)

The registration's power paragraph (L11341-L11345) says "407 matches over **162** distinct reserved questions
(~2.5 decidable matches per question) ... n_eff = 204 (worst case 110)".

Reviewer's recomputation from the caches: the 407 key-decidable matches span **122** distinct questions,
**3.336** matches per question, Kish mean cluster size `sum(m_i^2)/n` = **4.376** (cluster sizes 1..8:
23/30/16/14/22/11/4/2). The 162 is GEN-ARENA's whole 1,200-match schedule. **The registration's 162 and ~2.5 are
WRONG for the judged population and must be bracketed by the registrar.**

But the registered `n_eff = 204` is `407 / DEFF` with QUERY-SUPPORT's median variance-ratio DEFF 2.0, and **does
not depend on the question count at all**; it is not invalidated by the 162→122 correction. Bracketing the honest
DEFF at the measured clustering:

- transporting QUERY-SUPPORT's own implied ICC (DEFF 2.0 at R2's mean reuse 12.8 → rho ≈ 0.085; worst 3.68 at
  reuse 38 → rho ≈ 0.072) to Kish 4.376 gives **DEFF ≈ 1.25-1.29, n_eff ≈ 315-325** — i.e. the registered 204 is
  CONSERVATIVE at this support, because 3.3 matches/question is far less clustered than R2's 12.8;
- the rho = 1 extreme gives DEFF = 4.376, **n_eff = 93**, against the registration's worst case 110; the MDEs there
  are 9.2 / 13.0 / 15.9pp at discordance 0.10 / 0.20 / 0.30.

**Reading of record:** the registered MDE line (6.2 / 8.8 / 10.7pp at DEFF 2.0; 8.5 / 12.0 / 14.7pp at DEFF 3.7)
and the 10pp scoreability floor STAND as registered. The floor is adequate only at low discordance and is already
declared optimistic at DEFF 3.7 by the registration itself; the measured clustering does not make it worse than
that, and under the record's own ICC makes it better. What must change is the two descriptive numbers (162, ~2.5),
not the power conclusion.

## 4. Defects

| # | severity | defect |
|---|---|---|
| D1 | **HIGH** | `--analyze`'s "SUPPORT AS MEASURED" sentence (script L~1015) prints, with the real numbers, "*At the record's median DEFF 2.0 that is n_eff = **204** rather than **204**, so the registered MDEs are the optimistic end*". `int(round(len(dec)/2.0))` = 204 is arithmetically identical to the registered 204 — the "correction" is vacuous — and the inference ("optimistic end") is unsupported and wrong in direction under the record's own ICC (section 3). The sentence lands in the OUTCOME OF RECORD. Fix: either the engine-coder replaces the clause BEFORE the first posted call (re-pin this READY) or condition C1 below applies. |
| D2 | MEDIUM | The control arm is proved against a reword of the system string's FIRST SENTENCE, the assembly line, the reference-append line and the `reference()` signature — but a reword of the **rubric string's tail** ("violates" → "breaks") and a reword of **`reference()`'s body text** ("must satisfy" → "should satisfy") are both silently ACCEPTED (reviewer's shadow-module test, exit 0, changed prompt sha). The strings are imported, so this can only happen by editing `generative_arena.py`, and nothing pins them against a GEN-ARENA-era value. Mitigated by condition C2 (the two shas are pinned in this READY and must be reprinted at launch). |
| D3 | MEDIUM | An errored job (`except Exception: err += 1; continue`) is **not cached**, so it never enters the truncation guard's denominator (`unusable_counts` reads cached rows only). A pilot with silent errors can pass the 5% guard on a shrunken denominator — the named vacuity class. Mitigated by condition C3. |
| D4 | MEDIUM | Night accounting: `night_spent()` reads `docs/agents/queue.json meta.tonight_budget.spent_calls`, which is 0 and which **no launch updates**; `experiment_results/night_calls_2026-09-23.json` (the ledger a registrar is said to be adopting) **does not exist** at review time. If it is adopted, the script should NOT be edited for it during a live cache (D6): the sanctioned bridge is `--night-spent N`, whose printed source line then reads "operator-supplied". Condition C4. |
| D5 | LOW | `queue.json meta.tonight_budget.planned_allocation` budgets **838** calls under the id **IFEVAL-CHECKER-OUTPUT** ("407 key-decidable matches x 2 orders + a 24-call pilot"), i.e. the single-arm design the ruling REFUSED. This instrument posts **1,628** under **IFEVAL-RESPONSE-ORACLE**. The 14,000 ceiling is not threatened (0 spent), but the manager/registrar must reconcile the id and the number before the run. |
| D6 | LOW | `script_sha256_16_lf` is inside the compared `run_meta`, so any code fix after the first posted call REFUSES resumption into the cache. Every fix (D1 included) must land before the pilot, or be made by insertion into the outcome text afterwards. |
| D7 | LOW | The four DECLARED NOT SCORED items and C4's recorded limit print only in `--analyze`, not in `--dry-run`, so the operator does not see them pre-run. P6 ("NON_TERMINATED <= 5%") is vacuous at 0 non-terminated (already declared in the build note). Convention-A flip/accuracy denominators include INVALID rows by design; convention B is printed beside them. |

None of D1-D7 is a BLOCKER: none of them can post a call, write a DB of record, or change the protocol.

## 5. PHASE B command sequence (the operator's, after this file is committed)

```
python tools/analysis/ifeval_response_oracle.py --selftest
python tools/analysis/ifeval_response_oracle.py --dry-run
set IFEVAL_ORACLE_GO=1628                      # PowerShell: $env:IFEVAL_ORACLE_GO = "1628"
python tools/analysis/ifeval_response_oracle.py --pilot 12 --workers 8
#   -> STOP and read the guard; do not continue unless it prints "done: ok 24, errors 0"
python tools/analysis/ifeval_response_oracle.py --run --workers 8 --night-spent <cumulative incl. the 48>
python tools/analysis/ifeval_response_oracle.py --analyze
```

`--pilot`/`--run` are the only invocations that post. Never `--compare-math`. The token is exported only for the
posting invocations.

## 6. Conditions (binding on the run and on the reading)

- **C1 (D1, on the reading).** The clause "*n_eff = 204 rather than 204, so the registered MDEs are the optimistic
  end*" in the outcome is **NOT of record**. The post-run reviewer strikes it and the registrar inserts instead:
  the judged population is 407 matches over **122** distinct questions at **3.34** matches/question (Kish 4.38),
  correcting the registration's "162 / ~2.5"; `n_eff = n / DEFF` does not depend on the question count, so the
  registered n_eff 204 (worst 110) and the MDE line stand, with the honest DEFF bracket 1.25-4.38 (n_eff 325-93)
  printed beside them. If the engine-coder instead fixes the sentence in code, it must be BEFORE the pilot and
  this READY must be re-pinned on the new LF sha.
- **C2 (D2).** The phase-B `--dry-run` must print `system ebaec3a0f4b81f33 | reference(sample question)
  84fff82bc7154bba` and the population line's schedule hash `ba4a0ac8a2364a49`. Any other value means
  `generative_arena.py` moved and the CONTROL arm is no longer the GEN-ARENA prompt: **stop, do not post**.
- **C3 (D3).** The pilot line must read `done: ok 24, errors 0`. Any non-zero `errors` voids the guard reading
  (errored rows are not in its denominator): report the pilot and stop.
- **C4 (D4).** The `--run` launch passes `--night-spent` with the true cumulative count (the pilot's 48 plus
  everything else posted tonight), because `queue.json meta.tonight_budget.spent_calls` is not updated by any
  launch. The printed `[NIGHT]` line is the record of the check; a launch that would cross 14,000 is refused, not
  trimmed.
- **C5 (D5).** Before `--run`, the manager or registrar reconciles `planned_allocation`: the item is
  IFEVAL-RESPONSE-ORACLE at 1,628 calls (ceiling 1,700), not IFEVAL-CHECKER-OUTPUT at 838.

## 7. Expected verbatim lines at phase B

```
[POPULATION] IFEVAL-RESPONSE-ORACLE | ... 1200 IFEval verdicts over 162 distinct questions -> 407 KEY-DECIDABLE
matches over 122 distinct questions (registered 407); deciding subset 407 after 0 NON_TERMINATED exclusion(s);
schedule hash ba4a0ac8a2364a49. NO MMLU-Pro pool is opened: p2dca21ab5f4ef3ae and paeec37aa28063c75 are untouched,
and gen_arena_grok.db is READ-ONLY (mode=ro) and is never written by this test.
[TRANSPOSITION] order1(A) == order2(B): True | order1(B) == order2(A): True | vectors differ between contestants: True
[TRANSPOSITION] PASS for the sample match and for ALL 407 assembled treatment matches (a failure is a hard refusal,
never a warning).
[DRY-RUN] 1628 payloads assembled, 0 posted.
[DRY-RUN] control arm: ... sha256[:16] system ebaec3a0f4b81f33 | reference(sample question) 84fff82bc7154bba
[NIGHT] cumulative 0 against the HARD CEILING of 14000 (plan Amendment 9); a judged launch of this test would add
up to 1628 calls (ceiling 1700) -> 1628 | source: docs/agents/queue.json meta.tonight_budget.spent_calls
```

Gate refusal, verbatim, with the token absent or this file uncommitted (verified by execution):

```
[READY] the 12-match interleaved pilot (48 calls) refused (0 calls, no database opened): IFEVAL_ORACLE_GO=None
(needs '1628') | docs\reviews\READY_ifeval_response_oracle.md MISSING. Nothing is posted, including the 48-call
pilot, until the reviewer's READY is COMMITTED and IFEVAL_ORACLE_GO=1628 is exported.
```

With this file committed and the token exported the same line reads `[READY] IFEVAL_ORACLE_GO='1628' (needs
'1628') | docs\reviews\READY_ifeval_response_oracle.md exists, committed <sha>`.

## 8. Verdict

**READY** at LF sha `ee7df0e64ab5caab` / CRLF `ca9ee11bc9f13c50`, under conditions C1-C5. The instrument posts
nothing without a committed READY and the token; it opens three databases, all read-only, and writes none of them;
the control arm is GEN-ARENA's own code and strings; the treatment block is the ruling's §(6) shape on all 814
rendered blocks; the transposition clause is asserted on the posted bytes of all 407 treatment matches and its
negative case is tested; the MATH comparison is refused in code. The only substantive finding is D1, which is a
sentence in the outcome, not the protocol.

---

## 9. RE-PIN 2026-09-23 (adversarial reviewer, by insertion; nothing above is rewritten)

D1-D4 were fixed by the engine-coder at 42678a2, merged to main at **10fc37e**, BEFORE the first posted call
(defect D6 respected). This READY is **RE-PINNED** on the new object. Sections 1-8 above stand as written and
record the review of the previous sha; this section records what changed and what I verified myself.

**ONE LINE FOR THE OPERATOR: READY. Launch the phase-B sequence in section 5 (conditions C3, C4, C5 still bind;
C1 and C2 are now satisfied IN CODE).**

### 9.1 New pins

| item | value |
|---|---|
| script sha256[:16], LF (`run_meta.script_sha256_16_lf`) | **b8ba94311d813ce7** (was ee7df0e64ab5caab) |
| script sha256[:16], CRLF bytes on disk | **6196a1b4e33e9e7a** (was ca9ee11bc9f13c50) |
| size | 91,258 bytes; 155 insertions / 35 deletions against 1b62071 |
| merged at | 10fc37e (engine-coder commit 42678a2) |
| control system sha / reference sha / schedule hash | **UNCHANGED**: ebaec3a0f4b81f33 / 84fff82bc7154bba / ba4a0ac8a2364a49 |

### 9.2 Re-verified by command (zero calls; all three source DBs byte-unchanged; no cache file created)

- `--selftest`: exit 0, **34/34 OK** (the 3 new D1 checks - measured Kish size present, the struck "optimistic"
  and "rather than" absent, "ARE UNCHANGED" present - plus the new control-system-sha-equals-the-pin check).
- `--dry-run`: exit 0, **1628 payloads assembled, 0 posted**, and line 2 reads verbatim
  `[PINS] control system ebaec3a0f4b81f33 | reference(first target) 84fff82bc7154bba | schedule ba4a0ac8a2364a49
  -> MATCH (pinned by docs/reviews/READY_ifeval_response_oracle.md, 2dea289, condition C2)`. `assert_pins()` is
  called in `dry_run()`, `run()` and `analyze()`; a mismatch is a hard `SystemExit`. **D2's fence is now in the
  code**; condition C2 is satisfied by the instrument and no longer depends on the operator reading a sha.
- **D1, recomputed independently, agrees to the digit.** My own arithmetic from the cluster-size histogram:
  n 407, 122 questions, 3.336/question, Kish `sum(n_i^2)/sum(n_i)` = **4.376**; transported ICC rho
  **0.072-0.085** -> DEFF **1.24-1.29** -> n_eff **327-316**; rho=1 -> DEFF **4.376**, n_eff **93**, MDEs
  **9.2 / 13.0 / 15.9pp**; 204 lies inside [93, 327] and below the plausible-end 316. Every figure the script
  prints matches. Nothing in the clause re-derives the registered power: `POWER_LINE` and `MDE_LINE` still print
  VERBATIM above it, are still asserted against the programme by `assert_registration_quotes()` (which the
  dry-run ran), and `REGISTERED_NEFF` is quoted as a constant, never recomputed. The struck clause and the
  "optimistic end" inference are gone. **Condition C1 is satisfied in code**; it survives only as the registrar's
  bracket on the registration's descriptive "162 / ~2.5" (section 3 text), which is not this script's to fix.
- **D3 verified by execution, not by reading.** `guard_report(con, ids, label, uncached_errors=6)` on a fixture of
  18 clean cached rows printed `24 row(s) on the deciding subset (cached 18 + 6 errored-and-not-cached, counted
  unusable) | 6 unusable (25.0%) ... ABOVE 5%`. The guard can now only be pessimistic. **Condition C3 STANDS
  unchanged** as the operator's stop rule (`done: ok 24, errors 0`): the guard now refuses on errors, but the
  reason a pilot errored still has to be read before 1,580 more calls are posted.
- **D4 verified.** `experiment_results/night_calls_2026-09-23.json` now exists containing `[]`; the dry-run night
  line reads `source: queue.json meta.tonight_budget.spent_calls = 0,
  experiment_results\night_calls_2026-09-23.json = 0 -> the larger is used`. Both sources named with their values,
  the larger taken, `--night-spent` still overriding and still quoting both. **Condition C4 is RESTATED, not
  withdrawn:** neither ledger is written by this script or by any launch, so the `--run` invocation must still
  pass `--night-spent` with the true cumulative count (the pilot's 48 plus anything else posted tonight). An
  empty ledger reads 0 exactly as a missing one does.

### 9.3 The unrequested change (`DATA_ROOT`), scrutinised

`DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)` is applied to the three read-only DBs, `OUTDIR` (cache
and all three outcome files) and the night ledger. **The record files stay on the CODE root**: `RULING` (L184),
`PROGRAMME` (L185), `QUEUE_JSON` (L186) and `READY` (L187) all use `ROOT`. Verified by command that the gate does
not follow the data root: with `TAXOARENA_DATA_ROOT` pointed at an empty directory, `--selftest` still prints
`docs\reviews\READY_ifeval_response_oracle.md exists, committed 2dea289` - the gate is not escapable through the
data root - while `--dry-run` refuses at `[HYGIENE] experiment_results\multicorpus\gen_arena_grok.db is missing;
nothing is opened and nothing is posted`. The byte-identity claim holds: `--dry-run` with the variable unset and
with it set explicitly to the code root produce identical output, and the population line carries no data-root
suffix and is the line quoted in section 7. A pointed data root would be self-announcing twice over: the
population line names it in full, and `assert_pins()` would refuse any other dataset on the schedule hash.
Accepted.

### 9.4 Standing defects after the fix

- **D5 (the queue budgets 838 under the refused IFEVAL-CHECKER-OUTPUT id) - agreed, registrar's field.** Condition
  C5 stands: reconcile before `--run`. It cannot breach the ceiling (0 spent, 1,628 against 14,000).
- **D6** - now historical: the fix landed before the first posted call, as required. From the first posted call
  the LF sha b8ba94311d813ce7 is frozen for this cache; any further edit is a new session.
- **D7 (the NOT-SCORED items and C4's recorded limit print only in `--analyze`) - agreed, LOW, do not re-pin for
  it.** They are printed before any of them could be quoted, which is what the rule asks.
- **New, LOW, process not code:** the scratchpad is not per-agent - the engine-coder's worktree dry-run overwrote
  this reviewer's saved dry-run capture at 05:20 (its population line carries `DATA ROOT Z:/FAC/... | the code
  root is ...\.claude\worktrees\ifeval-response-oracle`). No file of record was touched; the three source DBs and
  the absent cache were re-checked after every invocation. Agents sharing a checkout should assume they also
  share the scratchpad.

### 9.5 Verdict

**READY** at LF **b8ba94311d813ce7** / CRLF **6196a1b4e33e9e7a**, conditions C3, C4 and C5 binding; C1 and C2 are
satisfied in code and survive only as the registrar's bracket on the registration's "162 / ~2.5". Nothing was
posted by this re-review.
