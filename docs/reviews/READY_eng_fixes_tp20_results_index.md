# READY review: TP20-GUARD-REFUSAL-PRECONDITION + RESULTS-INDEX-SELFTEST-ASSERTS (abd4a38)

Reviewer: adversarial-reviewer, 2026-09-23. Zero calls. No chain, no build, no site null, no --dry-run, no DB of record opened.
Every guard invocation ran on SYNTHETIC DBs in temp dirs. Scratch: session scratchpad `eng_fixes_a_ready/` (not in the repo).
Object: branch `worktree-agent-a3fcd9f99667d0692`, commit abd4a38 (parent eba09f3). `git show abd4a38 --name-only --format= | wc -l` = 2
(tools/analysis/results_index.py, tools/chains/topic_partition.sh); numstat +12/-5 and +51/-10. Neither file changed on main
since eba09f3 (`git log eba09f3..main -- <both>` empty; main HEAD still holds blob:ba0cca2c / blob:022bfe71), so a pathspec merge is clean.
pool_guard.py read and executed at blob:6521b51ac0fce04063563f9e6dcf42554ad86591 (= d30c19e = worktree = main HEAD).

## Pins (kinds named; the LF rendering is the pin, CRLF beside it because the worktree copies are CRLF)

| file | before | after (READY object) |
|---|---|---|
| tools/chains/topic_partition.sh | blob:ba0cca2c983c524b7aaab24213c054f6f9b720c3 / sha256-lf16:6455d849898fefb5 / sha256-crlf16:ab204c1452ca9fa3 | blob:3b6f329f03da2da96c05f75db38f24f94f3aa27f / sha256-lf16:3ac4a3a5c691635c / sha256-crlf16:f2730d41c9c96409 |
| tools/analysis/results_index.py | blob:022bfe71fee5a89802a02477f95700b33b621d05 / sha256-lf16:add48f95463fd29d / sha256-crlf16:6e57b72e8b8802e8 | blob:661a0eb62ef581013b2f85d446cd672a74247e26 / sha256-lf16:db252cbbaf118b72 / sha256-crlf16:9d810ec0d21ad976 |

Commands: `git rev-parse abd4a38:<path>`; `git show abd4a38:<path> | sha256sum` (LF); `... | sed 's/$/\r/' | sha256sum` (CRLF).
Python byte count on the worktree files: topic_partition.sh 742 CRLF, sha256 of the bytes f2730d41c9c96409 (= the crlf pin), of CRLF->LF
3ac4a3a5c691635c (= the lf pin); results_index.py 177 CRLF, 9d810ec0d21ad976 / db252cbbaf118b72. The builder's pins in the commit message
agree to the digit.

## 1. TP20-GUARD-REFUSAL-PRECONDITION (tools/chains/topic_partition.sh)

| # | claim | result | evidence (command) | got vs claimed |
|---|---|---|---|---|
| 1a | harness 74/74 | CONFIRMED | `bash tp_harness.sh <wt> old_topic_partition.sh` from my scratch; the old copy is `git show eba09f3:...` (hash-object ba0cca2c) | 74 PASS / 0 FAIL (`grep -c '^  PASS'` = 74, `'^  FAIL'` = 0) |
| 1b | the old script logs "C0 pool clause FAILED" in all 5 refusal cases | CONFIRMED | `grep -c "OLD script logs 'C0 pool clause FAILED'" harness_out.txt` | 5 vs 5 |
| 1c | OK / mismatch cases byte-identical old vs new | CONFIRMED | 4 same_case blocks: "chain.log identical old vs new" x4, every .out cmp-identical | 4/4 |
| 1d | 5/5 builder mutants killed | CONFIRMED | `python tp_mutants.py <wt>` (my scratch) | 5 KILLED, 0 SURVIVED |
| 1e | every [POOL-GUARD] message classified correctly | PARTLY | AST census + my probe gen_msgs.py (below) | 21 AGREE / 2 DISAGREE; both disagreements are unreachable from the chain |
| 1f | --dry-run transcript identical before/after (86 lines) | PARTLY | builder's `cmp_dry.py dry_before.txt dry_after.txt` | 86 vs 86 lines but they DIFFER on line 3 ("now: 2" vs "now: 0", a live python count, so environmental). Also VACUOUS as an inertness proof: every new branch is gated on DRY != 1, so a dry-run cannot execute the change. The harness is the proof, not the dry-run |
| 1g | withholding the readout cannot lose a valid T1 outcome | CONFIRMED | `ls experiment_results/topic_partition`: topic_partition_outcome.txt 32,751 B 04:42:40 exists; both pool_guard_*.out contain " OK:" (short-circuit before any guard call); readout() has no write path when withheld | see 1g below |
| 1h | T2's t2() never calls pool_export | CONFIRMED (pre-existing, not introduced) | `sed -n '/^t2() /,/^}/p'`: build + sitenull only; the same in ba0cca2c | see D3 |

### 1e. Census of pool_guard.py messages (blob:6521b51a)

`ast.walk` over the file finds 19 `raise SystemExit(...)`: 18 tagged `[POOL-GUARD]` + 1 `[SCORED-EVAL]` (not on the CLI path). Each was
TRIGGERED where reachable (in-process on synthetic DBs, or by the real CLI via subprocess, exact bytes) and format-rendered where it was not.
The probe adds 2 untagged tracebacks and 1 OK. Each output was fed to the chain's own `guard_refusal_tag` (extracted from blob 3b6f329f).
"Mine" is my classification by the ruling (L14522: a refusal is raised before any comparison; a mismatch has compared).

| pool_guard line | message | how | mine | chain | |
|---|---|---|---|---|---|
| 111 | pool X is not in the registry R (known: ...) | triggered | REFUSAL | registry refusal | agree |
| 145 | malformed pool id | triggered (in_pool_sql only; not on the CLI) | REFUSAL (arg) | not-refusal | DISAGREE, unreachable |
| 165 | database not found | CLI | REFUSAL | database not found | agree |
| 170 | <db>-wal is non-empty (N bytes) | CLI | REFUSAL | non-empty -wal | agree |
| 178 | <db>-journal is non-empty (N bytes) | CLI | REFUSAL | non-empty -journal | agree |
| 201 | pool X has no reserved_pool rows in this DB | triggered (assert_frozen_pool; not on the CLI) | MISMATCH | not-refusal | agree |
| 204 | reserved_pool rows for X hash to Y | triggered (not on the CLI) | MISMATCH | not-refusal | agree |
| 220 | pool X is not in the registry R: an unregistered pool needs BOTH | CLI | REFUSAL | registry refusal | agree |
| 240 | <idfile> hashes to Y, not X | CLI | MISMATCH | not-refusal | agree |
| 243 | lists N judgeable ids, registry says M | format | MISMATCH | not-refusal | agree |
| 250 | pool X is not recorded in <db> | CLI | MISMATCH | not-refusal | agree |
| 252 | rows for X in <db> do not hash to it | CLI + format | MISMATCH | not-refusal | agree (x2) |
| 256 | id file and reserved_pool rows differ by N | format | MISMATCH | not-refusal | agree |
| 298 | snapshot S not found or carries no reserved pool | CLI | NOT a pre-comparison refusal (a read result) | not-refusal | agree |
| 324 | member pool ... registry says | format | MISMATCH | not-refusal | agree |
| 362 | --db needs a value / --id-file needs a value | CLI | REFUSAL | argument refusal | agree (x2) |
| 683 | --activate is gone | CLI | REFUSAL (arg) | not-refusal | DISAGREE, unreachable (the chain never passes --activate) |
| 696 | --db / --id-file apply to --pool <id> only | CLI | REFUSAL | argument refusal | agree |
| - | FileNotFoundError traceback (id file missing) | CLI | untagged, pre-comparison | not-refusal | agrees with the ruling's letter; see D2 |
| - | sqlite3.OperationalError: no such table: reserved_pool | CLI | untagged, pre-comparison | not-refusal | agrees with the ruling's letter; see D2 |
| - | OK | CLI rc=0 | OK | (not consulted: rc = 0) | agree |

No compared mismatch is classed as a refusal, and no reachable refusal is classed as a mismatch. The chain passes two argvs: verify
`--pool <non-empty> --db $ING --id-file <path>` and export `--export-snapshot snapshots.db <snap> --out <idf>`. Under them the reachable
refusals are 165, 170 and 178. 362 is reachable only if $idf began with "--", which cannot happen by construction, and 111/220/696 cannot be
reached with both overrides given. CRLF: the patterns are anchored at the line start and not at the line end, so they match the Windows "\r\n"
stderr (the CLI cases above are real Windows bytes).

### Reviewer mutants (my_mutants.py; harness = builder's tp_harness.sh, probe = my classification of the 23 messages)

| mutant | harness | probe |
|---|---|---|
| N1 registry pattern broken | survived (74/0) | KILLED (L111, L220 -> not-refusal) |
| N2 "needs a value" dropped | survived (74/0) | KILLED (L362 x2) |
| N3 "--db / --id-file" dropped | survived (74/0) | KILLED (L696) |
| N4 final `exit 3` removed | KILLED (64/10) | survived (expected: not a classification change) |
| N5 verify refusal checked only on rc = 0 | KILLED (42/32) | survived (expected) |
| N6 pool_then_null ignores the stop | KILLED (64/10) | survived (expected) |
| N7 WITHHELD logged but the readout falls through | KILLED (69/5) | survived (expected) |
| N8 PRECOND_FAILED never set | KILLED (54/20) | survived (expected) |
| N9 db-not-found pattern dropped | KILLED (66/8) | KILLED |
| N10 -journal tagged as -wal | KILLED (73/1) | KILLED |

10/10 are killed by the harness and the probe together; 3 survive the builder's harness alone (D4).

### 1g. Can withholding the readout lose a valid T1 outcome?

No.
- (i) The run of record: topic_partition_outcome.txt exists (04:42:40, write-once), and both pool_guard_*.out carry " OK:", so pool_export
  returns before any guard call. A refusal is reachable only if a .out is deleted. Then readout() logs WITHHELD instead of "outcome present"
  and touches no file: the withheld branch has no write path, and N7 shows the harness catches a fall-through.
- (ii) A fresh run where T1 is OK and T1b is refused: T1's .out, site-null CSV and build log persist and are skipped on re-run (sitenull returns
  on an existing CSV; pool_export short-circuits on " OK:"). The outcome is DEFERRED to the remedied re-run, not lost.
- Running the readout instead would have written T1b's certification as "site null ABSENT ... UNDETERMINED (C0's null clause FAILED ...)"
  (topic_partition.py L1249-L1254) into the write-once file. That would record a precondition failure as an outcome, so withholding is the
  conservative reading of the ruling.
- Residual only: if the refusal can never be remedied, no readout is ever written, and the registrar would need a ruling. That is the ruling's
  intent.

## 2. RESULTS-INDEX-SELFTEST-ASSERTS (tools/analysis/results_index.py)

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 2a | SELFTEST PASS under python and -O | CONFIRMED | `python ...results_index.py --selftest`; `python -O ... --selftest` (worktree) | PASS rc 0 / PASS rc 0 |
| 2b | --check OK | CONFIRMED | `python tools/analysis/results_index.py --check` (worktree) | "OK 160 records" vs 160. The new file's `load()` on the main checkout's docs/agents/results: 162 records, 0 defects. `git status --short docs/agents/results \| wc -l` = 0 before and after |
| 2c | the diff touches only selftest() | CONFIRMED | `git diff eba09f3 abd4a38 -- results_index.py`: hunks at new L119-L140 and L147-L154; `def selftest` is L108, the next `def main` L156 | 2 hunks, both inside selftest() |
| 2d | K1-K5 fail under -O | CONFIRMED | `python ri_mutants.py <wt>` (my scratch) | NEW: 5/5 KILLED, each naming its check, under python AND -O. HEAD under -O: K2-K5 SURVIVE (the defect fixed); K1 is killed by a later explicit check |
| 2e | no other load-bearing assert | CONFIRMED | `grep -cE '^\s*assert\b' tools/analysis/results_index.py` over the WHOLE file | 0 (the two remaining "assert" hits are comments, L122/L138) |

## Defects

- D1 MEDIUM (TP20): the classifier depends on pool_guard's WORDING, and nothing pins that wording.
  - The chain's preflight checks only that pool_guard.py EXISTS (the L242 list). Nothing pins blob:6521b51a or the five format strings.
  - If pool_guard ever rewords a refusal (e.g. the -wal message), that refusal silently goes back to "C0 pool clause FAILED", the exact defect
    this item fixes.
  - Fix: add a preflight COUNT check that each of the five refusal patterns matches its format string in tools/analysis/pool_guard.py, with a
    mutant. Alternatively, refuse unless `git hash-object tools/analysis/pool_guard.py` = 6521b51a....
- D2 MEDIUM: the classifier lists refusals and treats everything else as a mismatch, so an unknown error gets recorded as an outcome instead of
  stopping the arm (it fails open). This conforms to the ruling's letter (L14522 names -wal, -journal and registry).
  - Any untagged failure that happens before a comparison takes the "C0 pool clause FAILED" path, although the guard compared nothing:
    - id file missing: FileNotFoundError;
    - ingest DB without reserved_pool: OperationalError;
    - a corrupt DB;
    - python not found: rc 127.
  - The fail-closed form lists the other side instead: the compared mismatches (L240/243/250/252/256) take the registered path, and everything
    else is PRECONDITION FAILED.
  - Whether to extend the ruling is the registrar's call. Not a condition of this READY.
- D3 MEDIUM (pre-existing since ba0cca2c, not introduced by this commit): t2() never calls pool_export.
  - Consequence: a T2 arm's pool is never verified, and the refusal fix does not cover T2.
  - It does not affect anything recorded: T2 was not run (chain.log L108 "T2 not run: T1 built with leaves=110"), and the outcome is written.
  - It does falsify the premise of the registrar's hazard (4)(b) (programme L14521): "only a NEW arm (T2) or a deleted .out reaches it". T2
    cannot reach pool_export; only a deleted .out can.
  - Fix: a registrar bracket at (4)(b). If T2 is ever to run, add `pool_then_null` for it (a registered change).
- D4 LOW: the builder's harness has no positive case for the "registry refusal" and "argument refusal" tags. Mutants N1-N3 survive it and are
  killed only by my probe. These tags cannot be reached from the chain's argv today. Fix: add my gen_msgs.py cases to the harness.
- D5 LOW: two refusals are classed as not-refusal, L683 "--activate is gone" and L145 "malformed pool id". Neither can be reached from the chain.
- D6 LOW: after a T1 refusal, the chain goes on to build T1b.
  - That build writes the ingest DB (twenty_newsgroups_cache_v1.db) whose sidecar caused the refusal. It does so before the remedy's first step,
    "back up the DB with its sidecars".
  - This conforms to the ruling ("the arm stops") and to "T1b runs regardless".
  - If the refusal names the ingest DB, stopping the chain before any further build would keep the evidence state. Registrar's call.
- D7 LOW: the commit message says the "--dry-run transcript [is] identical before/after". It is not exactly identical (line 3 differs, for an
  environmental reason). A dry-run also cannot prove that branches gated on DRY != 1 are inert (1f).

## Verdicts

- tools/chains/topic_partition.sh blob:3b6f329f03da2da96c05f75db38f24f94f3aa27f (sha256-lf16:3ac4a3a5c691635c; sha256-crlf16:f2730d41c9c96409):
  READY WITH CONDITIONS. The gate checks the LF rendering (git blob / sha256-lf16).
  - C1 (from D1): the refusal classification is certified ONLY for pool_guard.py blob:6521b51ac0fce04063563f9e6dcf42554ad86591. Before any chain
    step that can reach pool_export under a different pool_guard blob, re-run the census probe (gen_msgs.py plus the classify loop), or land the
    D1 preflight check.
  - C2 (from D3): the registrar inserts a bracket at programme L14521 (hazard (4)(b)) recording that T2 does not reach pool_export.
- tools/analysis/results_index.py blob:661a0eb62ef581013b2f85d446cd672a74247e26 (sha256-lf16:db252cbbaf118b72; sha256-crlf16:9d810ec0d21ad976):
  READY, no conditions. The gate checks the LF rendering.
- MERGEABLE by pathspec (`git checkout abd4a38 -- tools/chains/topic_partition.sh tools/analysis/results_index.py`); neither path has moved on main.

State after the review: `git status --short` in the worktree shows no tracked change. No DB of record was opened; the guard ran only on
synthetic DBs in temp dirs.
