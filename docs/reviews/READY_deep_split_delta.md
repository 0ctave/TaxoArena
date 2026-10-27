# READY (delta) — DEEP-SPLIT-COMPARE: ANCHOR_TABLE item counts (I3 bracket) + the B0-2 pool check selftest

Reviewed: branch `deep-split`, tip dc7a7674 (parent a9fd8317), delta `git diff d517e21d..dc7a7674` (1 file,
`tools/analysis/deep_split_compare.py`, +106 / -18). Reviewed blob `blob:31af4ceaa35fadfaf0bd43acc2a237d85c8ca30e` (LF; the
worktree file has 0 CR bytes, so no CRLF rendering differs), sha256-lf16 4b1fbeb8f53874d4. Registration: prog L23125-L23314,
brackets L23129 / L23155 / L23170 / L23220 / L23242 / L23312, registrar's record L23424-L23429 (_as_of main 06268781).
Adversarial reviewer, 2026-10-02. Zero calls.

## Verdict

**READY (delta scope) for the real `--dry-run`; the dry-run was run once and PASSED (rc 0).** The ANCHOR_TABLE edit and the
B0-2 pool-check wiring are CONFIRMED.

**Condition C1 (BLOCKER for `--run`, not for the dry-run): no full first READY of the script is on record.**
`grep -il "deep.split|deep_split|DEEP-SPLIT" docs/reviews/* | wc -l` = 0 before this file. The queue item's blocker says
"delta READY owed ...; READY review", so both are owed. This delta review covers the I3 table and the pool path only. The
analysis paths (arms B/C/D, filing, naming, verdicts, F-RULE, consequences, Support printing, R3-R5) and the base mutants M01-M43
have no committed review. A full first READY of d517e21d+delta is required before any `--run`.
C2 (LOW, for the run-operator): run with `TAXOARENA_DATA_ROOT` = the main checkout. The worktree holds neither guard DB, and
`DATA_ROOT` falls back to the repo root (`tools/analysis/data_v2/common.py` L45). Without it, the child fails closed (rc != 0),
so nothing passes vacuously. The worktree also holds 0 of main's 8 B0 `headless_run.log` files (64 untracked files under
rp12_r2 in main), so a worktree `--run` prints "headless_run.log ABSENT" in the descriptive R5 timing lines. The g13 precedent
was to run from main or copy the logs.

## Per-claim table (deciding claims only)

| # | Claim | Result | My number vs claimed | Sev |
|---|---|---|---|---|
| 1 | 19 ANCHOR_TABLE F-tree values = the L23220 bracket (rows -> items) | CONFIRMED | parsed old (d517e21d) and new tables: exactly 19 anchors changed, the changed set = the bracket's 19, all 19 (old, new) pairs equal the bracket, 0 mismatches; only column F-tree moved (k_a, maxd, B-anc, class unchanged on all 52) | - |
| 2 | F-tree column sums to 12,334 | CONFIRMED | 12,951 -> 12,334; the differences sum to 617 = bracket; new assert `sum(v[2]) == 12334` in st_boundaries | - |
| 3 | Old table = the draft's section 4 (blob ec62ddef) | CONFIRMED (spot check by eye, all 52 rows) | matches draft L224-L245 | - |
| 4 | Table = the REAL objects (I3) | CONFIRMED | real dry-run line 14: "I3 PASSED: F-tree / B-anc / class counts = the table"; the refusal compares all 5 columns on all 52 anchors (`load_anchors`, L337-L350) | - |
| 5 | Arm C smallest planned cell 59.2 | CONFIRMED | min F/k_a over k_a > 1 = 59.2 (IFEVAL 296/5) | - |
| 6 | `_gb_hooks` passes this script's REG to `pool_check_v2` | CONFIRMED | `_gb_hooks` sets `GB._CFG[0] = cfg()`; in production `cfg() is REG` True; `_POOL_GUARD[0] is GB.pool_check_v2` True; REG's pool / pool_file / pin / guard_args / guard_dbs == GB.REG's (True); M45 and own X2 (GB._ROOT not handed) both KILLED by `pool` | - |
| 7 | `st_pool` child argv and refusal order | CONFIRMED | pass case asserts 1 child call, argv[1] ends `v2_union_pool.py`, argv[2:5] = `--dry-run --pool pv2_fixture`. Five refusals (-wal 7 B, pin, rc 1, first line, no "every check passed"). Each prints the POOL line first and nothing after it (`len(lines)==1`), writes no outcome, and the child is called 0 times on the -wal / pin failures and 1 time otherwise. That is the order -wal -> pin -> child in `pool_check_v2` L243-L264. `main` order: lane guard -> POOL line -> refuse on rc -> write-once -> objects -> I1-I4 | - |
| 8 | Faked child reads no pool / production DB | CONFIRMED | audit hook (`sys.addaudithook`) over `selftest(only={"pool"})`: 185 `open` events, 0 outside `%TEMP%` (non-code), 0 `subprocess.*`, 0 `sqlite3.*` events | - |
| 9 | M44-M48 kill | CONFIRMED | `--mutants` re-run: 48 of 48 KILLED, control M00 SURVIVED; M44 (boundaries+pool), M45, M46, M47, M48 (pool) each KILLED with "selftest failed". The harness refuses a target that does not occur exactly once (L1653) | - |
| 10 | Selftest | CONFIRMED | 10 / 10 passed (worktree, BLAS threads 1) | - |
| 11 | Real dry-run POOL line | CONFIRMED | line 1: `POOL pv2_1575de61bb20e977 (B0-2 pool check rc 0): [UNION-POOL] pool pv2_1575de61bb20e977 recomputed from the side export (5642 EVAL components with a member in mc6-2026-09-11); expected pv2_1575de61bb20e977 \| [UNION-POOL] DRY RUN: every check passed; nothing written (...) \| engine pool file sha256-lf 79d48f4b36434a55 (pinned) \| multicorpus_cache_v1.db-wal 0 bytes; multicorpus_cache_v1.db-journal absent; corpus_v2_union_mc6.db-wal absent; corpus_v2_union_mc6.db-journal absent`. Own sha256-lf of the pool file: 79d48f4b36434a55 | - |
| 12 | Dry-run denominators = Support (a) (L23245) | CONFIRMED | EVAL 6,139 / 5,628 components (reg 6,139 / 5,628); MMLU_PRO_LB 3,478 / 3,386 (reg same); TRAIN 12,334 (reg same); R3 k_a 1215/1002, 2066/1834, 2465/2421, 393/380 and depth 1215/1284/944/1916/387/393 = reg; 52 anchors, 133 leaves, k_a per source = reg; I1 SEEN p_fl 0.8119 / p_kc[0] 0.8334 = the controls of record; depth-2 d2 -0.0023 [-0.0108, +0.0064] = REG | - |
| 13 | Support SE / MDE arithmetic (check 8) | CONFIRMED | sqrt(p*DEFF/n): 0.00418 / 0.00467 / 0.00398 / 0.00601 / 0.00649; MDE80 0.0117 / 0.0131 / 0.0111 / 0.0168 / 0.0182; n_eff 4,578 / 5,057 / 3,325, all to the digit. DEFFs are TRANSPORTED (source named: G13-BREAKDOWN measured); the run must print the measured DEFF (registered) | - |
| 14 | No write by the dry-run | CONFIRMED | size+mtime of multicorpus_cache_v1.db (+ -wal 0 B, -shm), SPLIT-2 corpus_v2_union_mc6.db and the engine pool file: `diff` before/after empty; outcome file absent before and after; `git status --short \| wc -l` in the worktree = 0 | - |

Own mutants (≤3, delta):
- X1: compensated F-tree swap (math 741->740, physics 753->754). SURVIVED the selftest; not decisive, because the fixtures do not
  carry the real table and the real dry-run's I3 (claim 4) is the discriminator for the table values.
- X2: `_gb_hooks` does not hand `GB._ROOT`. KILLED (pool); decisive.
- X3: write-once check moved before the POOL line. KILLED (e2e_H); decisive for the refusal order.

## Defects

- D-1 (BLOCKER for `--run` only) = C1: there is no full READY of the analysis paths. Fix: a full first review of
  d517e21d..dc7a7674 (about 8 own mutants on the deciding paths) before any `--run`.
- D-2 (LOW) = C2: the run environment is not stated in the script's usage line. Fix: add
  `TAXOARENA_DATA_ROOT=<main checkout>` to the usage at L109, or run from main as G13 did.
- D-3 (LOW, observation): the lane guard (`guard_paths`) refuses before the POOL line. That is a refusal with no other output,
  so "pool printed FIRST" holds on every path past argument validation. No fix needed.
- D-4 (LOW): M44 is killed by a literal assert on the pin in st_boundaries, so it is tautological there. The `pool` kill (the
  "reg" pin case) is the substantive one. No fix needed.

## Process

Rule 7, before the dry-run (`Get-CimInstance Win32_Process` filtered to java|python|gradle|ollama): no java and no gradle were
running. Present were `ollama.exe serve` (idle daemon), `ollama app.exe`, and a peer `python oos_baselines.py --mutants`
(PID 51044; synthetic, not a construction or site null). The dry-run is a pool reader and ran alongside them. Nothing was
committed (this file is written on main, uncommitted, as briefed).

## Commands

```
git diff d517e21d..dc7a7674 ; git diff --name-only d517e21d..dc7a7674 | wc -l            # 1
git hash-object .claude/worktrees/deep-split/tools/analysis/deep_split_compare.py         # 31af4cea (LF); grep -c $'\r' -> 0
python <scratch>/table check: exec the _T block of d517e21d and of the worktree file; compare to the bracket   # 19/19, 12951->12334, 617
grep -il "deep.split\|deep_split\|DEEP-SPLIT" docs/reviews/* | wc -l                         # 0 (C1)
python tools/analysis/deep_split_compare.py --selftest      # (worktree) 10 / 10 passed
python tools/analysis/deep_split_compare.py --mutants       # (worktree) 48 of 48 KILLED; control survived
python <scratch>/dsc/own_mut.py                             # X0 control SURVIVED; X1 SURVIVED; X2, X3 KILLED
python <scratch>/dsc/audit_pool.py                          # st_pool: 185 opens, 0 outside %TEMP%, 0 subprocess/sqlite events
python -c "...M.REG vs GB.REG; M._POOL_GUARD[0] is GB.pool_check_v2; cfg() is REG"          # True / True / True
stat -c '%n %s %y' <5 inputs> > before.txt                  # then the same | diff - before.txt -> empty
TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' python tools/analysis/deep_split_compare.py --dry-run --lane r2   # (worktree) rc 0, 15 lines
git -C .claude/worktrees/deep-split status --short | wc -l  # 0
```
