# READY re-review: POOL-GUARD-IMMUTABLE at d0946e3 (zero calls, read-only)

Adversarial reviewer, 2026-09-23. Branch `pool-guard-immutable`, commit **d0946e3** (parent abeacf1, reviewed NOT READY at d72c790). The .kt part is already on main (a441ae2), so this review covers `tools/analysis/pool_guard.py` only. `git diff abeacf1 d0946e3 --stat` shows one file (+215 / -71). The non-selftest hunks are the docstring bracket, `open_ro`'s docstring, the -wal refusal text and the new -journal block; nothing else outside `selftest()` changed. Main is at b9a945b, and `git diff --name-only 1fad897 HEAD -- tools/analysis/pool_guard.py | wc -l` = 0, so main has no overlap with the branch.

Scratch: session scratchpad `pool_guard_ready/`, containing `rr/` (the d0946e3 blob, split_side.py and configs), `wrap.py`, `stat.py`, `imp.py`, `mut_rr.py`, `hot/`, and the outputs `rro_*`, `rr_stat_*`, `rr_20ng.*` and `st_rr*.out`. Nothing under the repo was written except this file.

Rule 7: at 16:45 the only java processes were the idle Gradle daemon and the Kotlin compile daemon left by the d72c790 compile. No python process, construction or site null was running. snapshots_frozen.db was not opened.

## Identity (pins name their kind)

| file | pin at d0946e3 | verified by |
|---|---|---|
| tools/analysis/pool_guard.py | **blob:9ababad62965ae2acc97d46493853868e049eee8 / sha256-lf16:b890fc283b6e3634 / sha256-crlf16:d25833c3e751601d** | `git rev-parse d0946e3:<path>`; `git show d0946e3:<path>` holds 0 CR, so its sha256 is the LF rendering and the same stream with CRLF gives the CRLF rendering. All three equal the builder's pins. The scratch copy `git hash-object rr/tools/analysis/pool_guard.py` gives 9ababad6... |

Superseded: blob:c857fd2e1c20 / sha256-lf16:83de84ca92570068 / sha256-crlf16:30862860dfbab2c5 (main) and blob:e5f39612244d / sha256-lf16:a18babcbee474d99 (abeacf1, never merged).

## Verdict

**READY-WITH-CONDITIONS. MERGEABLE after C1.** C1 is a selftest addition only (two ACCEPT cases for rollback-mode DBs). The reviewer checks it mechanically: re-run `mut_rr.py` and require J8 and J14 KILLED. A full re-review is not needed. The shipped `open_ro` is correct by execution on every real DB and on every synthetic hazard I could construct. All five d72c790 conditions are met, except for this selftest gap, which is the same class as d72c790 D2.

## Per-claim table (builder's claims against the d72c790 conditions)

| # | claim | result | command | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | -journal refused after the unchanged -wal check, before any connect | CONFIRMED | code read (`open_ro`); `hot/` harness on the rr blob with a connect recorder | hot journal from a crashed writer (322064 B): REFUSED with the tag, **0 connects**. Live rollback writer (BEGIN + UPDATE, cache_size 5): REFUSED, 0 connects. Rollback DB with no journal after ROLLBACK: ACCEPTED, 1 connect, (20000, 0 negated) | - |
| 1b | selftest case 6: the immutable view bypassing the guard returns 2,658 uncommitted rows | CONFIRMED | `st_rr.out` L46 | 2658, as claimed | - |
| 1c | PERSIST refused (fail-closed false refusal) | CONFIRMED, a false refusal | `hot/`: PERSIST DB, clean commit and close | the -journal is 8720 B with its first 28 bytes zero (not hot); the new guard REFUSES with 0 connects, while plain `mode=ro` reads 2000 rows. TRUNCATE DB: 0 B -journal, ACCEPTED (2000 rows) | LOW (see D-R3) |
| 2 | case 3 (0 B -wal beside a 32 KB -shm accepted, -shm unchanged) and case 5 (crashed WAL writer, no -shm, refused; immutable 9 vs WAL-inclusive 59) | CONFIRMED | `python [-O] rr/.../pool_guard.py --selftest` | `st_rr.out` L17-L21, L32-L39: accepted beside 32768 B; refused with 0 connects; 9 vs 59, a 50-row tail | - |
| 2b | the d72c790 mutants killed | CONFIRMED | `mut_rr.py` (the d72c790 patterns, re-anchored on the new blob) | M1 to M11 all KILLED under python and -O (22/22). **M3, the d72c790 survivor, is now KILLED** (5 FAIL, at the case-3 accept) | - |
| 2c | my journal-branch mutants | 11 of 15 KILLED; **J8 and J14 SURVIVE** (J2 and J15 survive as equivalents) | `mut_rr.py`; J10 re-run as a clean patch (`if os.path.exists(wal) and os.path.exists(journal)`) | KILLED under both modes: J1 journal removed; J3 journal only when the header says WAL; J4 wrong directory; J5 suffix typo; J6 copy-paste -wal; J7 never refuse; J9 checked after connect; J10 only when a -wal exists; J11 assert (dies under -O); J12 untagged; J13 remedy text dropped. **SURVIVE 34/34 under both modes: J8 (refuse a 0 B -journal too) and J14 (refuse EVERY rollback-mode DB, header byte 18 == 1).** J2 (journal checked only when the header says rollback) and J15 (`path + "-journal"` without abspath) also survive; both are equivalent in practice (D-R2) | **MEDIUM** (J8, J14) |
| 3 | both refusals name the killed-JVM remedy | CONFIRMED | code; J13 KILLED; the 20NG refusal text | "back up the DB, then have the data-steward checkpoint it with a read-write open/close" (-wal) and "... roll the journal back ..." (-journal) | - |
| 4 | selftest 34/34 under both modes; accept cases record a FAIL rather than crash; gc before cleanup | CONFIRMED | `st_rr.out`, `st_rrO.out`, both rc 0 | 34/34 each. After 60 mutant runs (30 patterns x 2 modes), 0 `%TEMP%\pool_guard_selftest_*` directories were left (the glob before/after diff is empty; d72c790 D6 is closed) | - |
| 5 | pins | CONFIRMED | see Identity | exact | - |
| R1 | real-DB replay: p2dca, paeec, --diff-flag byte-identical to the old code | CONFIRMED | `wrap.py` new (rr1), then old (old2), then new (rr2), `TAXOARENA_DATA_ROOT=main` | p2dca: rc 0/0/0, sha256-16 of stdout f9769b8aec7b4bfd x3. paeec: 9a9489b635b723e6 x3. --diff-flag: 3eb648a7909e69a9 x3. All equal the d72c790 old-code outputs (`cmp`). One CONNECT per run, `?mode=ro&immutable=1` | - |
| R2 | 20NG refusal with the tag, 0 connects, no state change | CONFIRMED | `wrap.py rr --pool pf844849e133cda4e --db <20NG> --id-file <20ng json>` | rc 1, 0 B stdout, 0 CONNECT, `[POOL-GUARD] ...twenty_newsgroups_cache_v1.db-wal is non-empty (708672 bytes) ...` | - |
| R3 | sidecars and main-file identity before and after | CONFIRMED | `stat.py --sha` at start and end; `stat.py` after each pass | Main files (size / mtime_ns / sha256-16) are identical to the d72c790 baseline and unchanged throughout: mmlu_pro_dataset_cache_v2.db 974917632 / 1789828210106974800 / 4f65414f7625a1e7; multicorpus_cache_v1.db 1948323840 / 1789292669684275700 / ad66e30a0eb4abd6; twenty_newsgroups_cache_v1.db 75739136 / 1790098356251029800 / 012870e7dacf8b4a; bfcl 18767872 / c5eddd267623f0ff; multiswe 27705344 / 3ce5179c3f5085d2. After the NEW pass: 0 diffs, including -wal, -shm and -journal size, mtime and sha. After the OLD pass: only the -shm mtime moved on p2dca and paeec (bytes fd4c9fda9cd3f9ae unchanged), as at d72c790. No -journal exists anywhere (`find . -name '*-journal'`, excluding .claude, gives 0) | - |
| R4 | rollback-mode real DBs pass the new -journal check | CONFIRMED | `wrap.py rr --pool p2035adddedd1becb --db bfcl_result_2025-12-16.db --id-file ...`; the same for p79fb and multiswe | each reaches its connect (`?mode=ro&immutable=1`) and fails on `no such table: reserved_pool`, the same as the old code (d72c790 1b). State is identical before and after (`cmp` of stat). `--pool` alone gives the registry refusal with 0 connects | - |
| R5 | no DB opened at import | CONFIRMED | `imp.py rr` under `sys.addaudithook`, python and -O | 0 sqlite3.connect events and 0 non-.py opens in both runs | - |

## Defects

**D-R1 (MEDIUM): the selftest has no ACCEPT case for a rollback-mode DB, so J14 (refuse every rollback DB) and J8 (refuse a 0 B -journal) pass 34/34.** This is the vacuity class of guard that refuses everything and still passes its own test. Rollback-mode DBs are exactly the BFCL and MULTISWE DBs that POOL-REGISTRY-BFCL will register (R4 shows the shipped code accepts them). Every selftest rollback case (6, 7) is a refusal. **Fix (C1):** add case 8, a rollback-mode DB (journal_mode DELETE, header 1/1) with no -journal: ACCEPTED, exactly one connect, pool id verified. Add case 9, a journal_mode TRUNCATE DB after a clean commit (0 B -journal): ACCEPTED, and the -journal left at 0 B. Acceptance: J8 and J14 are KILLED under python and -O by `mut_rr.py` (patterns in the scratch file), with all other mutants still KILLED.

**D-R2 (LOW, no action): J2 and J15 are equivalent mutants.** J15's relative `path + "-journal"` resolves to the same file as the abspath form within one call. J2 differs from the shipped code only for a hot -journal beside a page 1 whose header says WAL. That can arise only from a crash inside a rollback-to-WAL mode switch; the shipped code is stricter than J2 there, which is the safe direction. The selftest cannot tell them apart and does not need to.

**D-R3 (LOW, record only): the PERSIST false refusal.** It is real (1c) and fail-closed. Exposure today is none:
- all 10 `journal_mode` settings in `src/main/kotlin` are `journal_mode=WAL` (`git grep -n -i journal_mode HEAD -- src/ tools/`);
- `tools/` sets none, so the Python writers use SQLite's default DELETE;
- there are 0 `-journal` files on disk.

PERSIST is a per-connection setting and is not stored in the file, so "no DB of record uses it" rests on that writer census, not on the file. **Record it** in the registrar's record as a known limitation of open_ro: "a PERSIST-mode DB is refused after a clean commit; convert or checkpoint before a guard read". No code change is needed. A header-byte-18 check could not distinguish PERSIST either; the journal-header-zero test (first 28 bytes zero means not hot) would, but it adds a parse whose failure mode is a false ACCEPT. Keeping the refusal is the right call.

**Residual carried from d72c790 D4 (documented in open_ro's docstring, CONFIRMED present):** the checks and the connect are not atomic; rule 7 excludes a writer that starts in between.

## Conditions for merge

- **C1.** D-R1 cases 8 and 9 land. The reviewer re-runs `mut_rr.py` and the selftest: 36+/36+ under both modes, J8 and J14 KILLED, M1 to M11 and J1 to J13 still KILLED. The new blob and its pin triple are re-stated in the merge message.
- **C2.** The merge is by path (`git checkout <branch-commit> -- tools/analysis/pool_guard.py`, then `git commit -- tools/analysis/pool_guard.py`). No -journal or non-empty -wal may exist beside p2dca or paeec at merge time; the stat at merge must show the 0 B -wal and 32 KB -shm state above.
- **C3.** TOPIC-PARTITION-20NG: not a merge condition, but a condition on its resume, carried from d72c790 D3.
  - (a) Back up `twenty_newsgroups_cache_v1.db` together with its -wal, then have the data-steward checkpoint it with a read-write open and close.
  - (b) `topic_partition.sh` `pool_export` (L533-L537) must map a `[POOL-GUARD] ... is non-empty` refusal to a failed precondition or UNDETERMINED, never to "C0 pool clause FAILED".
  - Until then, every 20NG guard read refuses; this is shown in R2.

## Pin impact (the registrar applies these at the merge, by insertion)

New pin of record for tools/analysis/pool_guard.py: the C1 blob, or blob:9ababad62965 / sha256-lf16:b890fc283b6e3634 / sha256-crlf16:d25833c3e751601d if C1 is waived.

| where | kind | action |
|---|---|---|
| docs/agents/results/TOPIC-PARTITION-20NG.json L19 (`sha16`: pool_guard.py 83de84ca92570068, blob c857fd2e1c20, "inert when absent") | sha256-lf16 + blob | Insert a bracket: true of the runs done (both `pool_guard_ng_af_*.out` came from c857fd2e); from merge <sha> the instrument is the new triple and refuses on a non-empty -wal or -journal. **New pin plus a re-review condition** (C3) for any T2 arm or re-verification |
| same file L197 (`instrument_shas_of_record`, full LF and CRLF sha256) | sha256-lf + sha256-crlf | same bracket, with the full LF and CRLF sha256 of the merged blob |
| docs/judge_v2_program.md L10865-L10866 (SCRIPT SHAS OF RECORD at 634e969) | sha256-lf, sha256-crlf, blob | bracket appended at the END of the programme: superseded at the merge; "byte-identical at both branch commits" stays true of 634e969 |
| docs/reviews/READY_topic_partition_20ng.md L15, L141, L173 | table LF / CRLF / blob; "UNCHANGED"; "inert and byte-identical" | historical, not edited; re-review condition C3 before any new pool_export |
| docs/agents/queue.json L843 (TOPIC-PARTITION-20NG notes) | sha256-lf16 | append the new pin |
| docs/agents/queue.json, POOL-GUARD-IMMUTABLE item | state | drafted -> READY-WITH-CONDITIONS (this review), then MERGED with the pin triple and the D-R3 limitation |
| docs/reviews/READY_model_vintage_stamp.md L46; docs/reviews/2026-09-22_model_vintage_stamp_post.md L25; docs/reviews/READY_cert_under_filter_sing.md D7 (L94); programme L14378-L14381 (D7) | behaviour: "pool_guard mode=ro without immutable moves the -shm" | RESOLVED at the merge (R3: the new blob moves nothing) |
| docs/agents/results/MODEL-VINTAGE-CANARY.json L34 | historical -shm mtime note | no action (true of c857fd2e) |
| docs/agents/CONTEXT.md L27 (verify with `pool_guard.py --pool <id>`) | behaviour | add: the verify command REFUSES on a non-empty `-wal` or `-journal` (and on a PERSIST-mode DB); a refusal is a failed precondition, never an outcome |
| tools/analysis/agent_admission_pilot.py L17/L408; bfcl_judged_pilot.py L224 | "opens no DB at import" | still true (R5); no action |

Absences proven by count:
- old-pin census: `git grep -c -I -E "c857fd2e|83de84ca" HEAD` gives 4 files, 8 lines (d72c790);
- -journal files on disk: `find . -path ./.claude -prune -o -name "*-journal" -print | wc -l` = 0;
- `journal_mode` in tools/: `git grep -l -i journal_mode HEAD -- tools/ | wc -l` = 0;
- connects before the 20NG refusal: `grep -c CONNECT rr_20ng.stderr` = 0;
- mutant temp dirs left: glob diff = [].

[CORRECTED 2026-09-23 by the reviewer, insertion only: the old-pin census above is the d72c790 figure. At b9a945b, `git grep -c -I -E "c857fd2e|83de84ca" HEAD` (excluding READY_pool_guard_immutable.md) gives **5 files / 14 lines**: the 8 listed above, plus docs/agents/results/POOL-GUARD-IMMUTABLE.json (4: L15, L60 and two more) and 2 more lines in docs/judge_v2_program.md (L14513, L14517). The 6 additional lines are the registrar's own record of this item. They quote the old triple as "before" and plan the brackets; they are not instrument pins and need no new-pin bracket, only the item's MERGED update.]
