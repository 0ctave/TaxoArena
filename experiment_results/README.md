# experiment_results/

Outputs and readouts of TaxoArena runs.
The record of an output lives elsewhere: its ledger row in [docs/test_ledger.html](../docs/test_ledger.html), its JSON record in [docs/agents/results/](../docs/agents/results/INDEX.md) and its sections in [docs/judge_v2_program.md](../docs/judge_v2_program.md).
A record's `run.outcome_file` and `sources` fields name the files it wrote and read, so searching a directory's path in `docs/agents/results/` finds its record.
<!-- src: KNOWLEDGE.md section 4 (where things live); e.g. UNION-AF-ROUTE.json run.outcome_file, sources -->

## Kinds of directory

| kind | examples | how to read it |
|---|---|---|
| the r8 batch | `r8/` | history, never evidence; its README carries a HISTORY banner |
| outputs of tests in the record | `archv2/`, `anchorfree/`, `multicorpus/`, `cert_resolution/`, `flat_mix_mmlu/`, `promoted/` | the status of every number is its ledger row's last bracket |
| construction and calibration runs | `freeze_mcs55/`, `h9_seed*/`, `dimsweep*/`, `cal_iso/` | engine output and tree objects |
| run logs | `run_ops_2026-09-29/`, `threadcap/`, `trace_truncation/` | operational logs, not readouts |

<!-- src: prog L21449 _as_of 70c61579 (r8 history); row 2: each listed directory is named by the records in
docs/agents/results/*.json (grep its path); rows 3-4: the directories' names and contents (engine output, logs);
KNOWLEDGE.md section 1 (last bracket wins). A local scratch citation was dropped (REVIEW_REPO-TIDY E8). -->

Some directories need a word:

- `r8/`: the 8-domain, 8-model batch of 2026-07-31.
- `promoted/`: readouts of the tree of record bareq512_s42 (reserved leaf assignments and its 300-rep site null over 70 sites) and leaf assignments of a second tree on the same pool, abt2d512_s42. The snapshots themselves are not in the repository.
- `freeze_mcs55/`: the build of the frozen tree 20260727_042523, which is geometry only.
- `judge_solve/grok-reasoning.db` (not in the public copy): the cached reference solves of the STACK-v2 recipe (3,432), an instrument component, not a readout.
- `day_calls_<date>.json`: the judge calls posted on each day, one row per launch (test, launch, calls, time); the day's file is the count of record for its calls.

<!-- src: docs/RESULTS.md L3-L4 (r8: 8-domain, 8-model batch of 2026-07-31); prog L20856(a) _as_of 70c61579
(site_null_bareq512_s42.csv: 70 sites, 300 reps); ledger row PROMOTED (abt2d512_s42 on the pool of record p2dca);
prog L20823 _as_of 70c61579 (the bareq512_s42 build's evidence files are untracked); prog L20828 _as_of 70c61579
(freeze_mcs55/seed_42 is the frozen build, certified at iteration 10, tracked); KNOWLEDGE.md section 1 (frozen tree
geometry-only; STACK-v2 reference grok-reasoning.db, 3,432); docs/reviews/RULING_w0_p2dca_family.md L68 ("an
instrument component"); tools/analysis/accepted_tests_ledger.py L4-L8 (day_calls_<YYYY-MM-DD>.json, count of record
by posting date, one row per launch: test, launch, calls, ts) -->

## Rules for reading

- Judged readouts on pool p2dca21ab5f4ef3ae belong to the p2dca judged family: history, never evidence. Membership follows the run's split, not the directory or a printed pool id. Key-only readouts on that pool are not in the family; they carry "id-disjoint only". See [the ruling](../docs/reviews/RULING_w0_p2dca_family.md).
- Every readout carries its split word, copied from its record. Nothing is called clean, disjoint or held-out without a content-key check under CK-CLOSE.
- Open a tracked database read-only (`mode=ro`, and `immutable=1` for a database with a WAL). Never write to a database of record.
- New outputs are not committed. They are pinned by sha256 and backed up outside the repository. Tracked files stay at their paths because records and scripts read them by path.

<!-- src: prog L21474-L21480 _as_of 70c61579 (membership (a), "Membership follows the run's split", key-only not in
the family); CONTEXT.md section 4 rule 12 (split words); KNOWLEDGE.md section 2 "Never" list (DB of record: mode=ro,
immutable=1 for WAL DBs); KNOWLEDGE.md L193 ("Outputs are never committed: pin by sha256 and back up");
UNION-AF-ROUTE ledger bracket [CORRECTED 2026-10-03 ... THE AUTHOR's rule] -->
