# READY review: E1-SPLIT-DRAWS build (branch e1-split-draws, tip 6ff23dc9)

Reviewer: adversarial reviewer, 2026-10-03. Zero calls. Registration L23831-L23859 (a1c65848; section "## Registered 2026-10-03
(before any code or call) — E1-SPLIT-DRAWS: ..."). Builder declarations L1-L3 (commit 6ff23dc9 message): their brackets were not
yet in the programme when this was written (`git diff HEAD -- docs/` empty on main at 8e474b4b); my positions are under DEFECTS.

## VERDICT

**READY** to merge and launch, with conditions C1 (operational, binds the run-operator; no code change) and C2 (LOW, follow-up).
The splits are content-closed and new; the six TOMLs are af_clean_s42 with exactly three keys changed; the launcher's order and
refusals hold on real data; the readout's deciding path (per-split paired Wald, spread, SD1 / F-SD, identity, guards,
write-once) reproduces and kills 6 of my 9 mutants. The 3 that survive expose selftest gaps; the shipped code is correct on each.

## Pins reviewed (LF git blobs = `git hash-object` = `git ls-tree 6ff23dc9`; the working tree is CRLF, autocrlf)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/e1sd_split_draw.py | 0c12e9b8 | 29e725ae6198f890 | bd599d6f0ee7b533 |
| tools/analysis/e1sd_launch.py | bdbb3fc6 | 14228847d2040359 | 3ee345d1e035e637 |
| tools/analysis/e1_split_draws.py | 3318a16a | 1004a8e1750f5810 | 02668b7d81080bf1 |
| reserved_pool_e1sd1/2/3.json | 33ad1c55 / 55231da0 / 5ad9c86e | (sha256-lf cf4a7f30 / 3a7cf453 / 0b2233ac) | |
| N_e1sd1..3.toml | 4fac964f / 4ba063c1 / 00d2543e | | |
| Q_e1sd1..3.toml | a910b359 / f51ee5a6 / e5ffd8b9 | | |

`git cat-file blob 0c12e9b8 | grep -c $'\r'` = 0, so the blobs are LF. (`git show <c>:<path>` applies the autocrlf rendering and
shows CR: an artefact of the command, not of the blob.) Commit = 12 files, 12 new, 0 under src/, 0 application.yml/.env/.gitignore
(counted with `git diff --name-only a1c65848 6ff23dc9 | grep -c`).

## Per-claim table (deciding claims)

| # | claim | mine vs claimed | state | sev |
|---|---|---|---|---|
| 1 | Splits re-derive: side = side_of_hash(sha256(salt U+001F stem_key)) < 300 | my own hashlib recompute == each file's id set (3 of 3); 3,671 / 3,590 / 3,573 held-out rows of 12,000 (0.3059 / 0.2992 / 0.2978) | CONFIRMED | - |
| 2 | Content-closed (CK-CLOSE-v1) | stem_key overlap 0/0/0, exact text 0/0/0, engine finishSplit moves 0/0/0, id overlap 0/0/0; an extra NFKC+casefold+whitespace key (mine) 0/0/0 | CONFIRMED | - |
| 3 | Never an arena pool / not p2dca / not in the registry / distinct | pools p5fb86f1075d76e34, p6d15d913354f256d, p69d2762ac6223d93; `grep -c` in reserved_pools.json = 0; 'p2dca' in the split files = 0; all FRESH in the corpus DB | CONFIRMED | - |
| 4 | NON-VACUITY: each split has a different held-out | pairwise held-out id overlap 1,097 / 1,057 / 1,054 (about 0.30 of 3,600, as for independent salts); none identical; overlap with p2dca's held-out texts 1,027 / 1,061 / 1,014 (about 0.30 x 3,445). Mutant RV5 (every split scored on split 1) KILLED | CONFIRMED | - |
| 5 | TOMLs = af_clean_s42 (blob 7d63d0f9) except outputDir, reservedPoolFile, pool | `diff` of each body against the base: exactly lines 44, 47, 48; seed 42 x1, `seeds` 0, in all 6; N and Q of a split differ only in outputDir. The brief's "only pool and outputDir" omits reservedPoolFile, which has to change with the split | CONFIRMED | - |
| 6 | Launcher order N1, N2, N3, then Q1, Q2, Q3, with refusals | check_order read; L04/L05 KILLED; real-data pre-launch steps (2) DECLARED x6, (5) COVERAGE nomic_raw DIR 11,769/11,769 and qwen3 11,769/11,769, (6) POOL FRESH x3 executed from my script; P sidecars today: only main/embeddings_cache.db (-wal 0 B, -shm 32 KB), so CP-0 is needed | CONFIRMED | - |
| 7 | Checkpoint points use tools/ops/wal_checkpoint.py | NO: CP-0 / CP-1 say "a clean read-write open/close"; the tool is not named (the branch base a1c65848 predates its merge 8e474b4b). All three CP-1 DBs and the CP-0 DB are on its allow-list. It refuses while any java.exe runs, and an idle Gradle daemon (PID 31012) runs now | REFUTED (wording) -> C1 | MEDIUM |
| 8 | Readout: per-split paired Wald decides | e1_readout.mcnemar: (b-c)/n -/+ 1.96 sqrt(b+c-(b-c)^2/n)/n; exact McNemar and bootstrap beside, never deciding | CONFIRMED | - |
| 9 | SD1 / F-SD logic | WORSE iff all hi < 0 and Gbar < -max(spread_N, spread_Q); BETTER symmetric; F-SD iff any G_k >= 0 or abs(Gbar) <= max spread. Spreads are on top-1 per embedder (RV4 KILLED); G sign is N - Q (RV3 KILLED); Gbar excludes E1 (R13) | CONFIRMED | - |
| 10 | Identity precondition | real dry-run: af 0.7269, N-raw 0.6813, b 327, c 484, n 3,445 -> HELD; G_E1 -0.0456 [-0.0617, -0.0294]. My arithmetic: -157/3,445 = -0.04557; SE sqrt(811 - 157^2/3,445)/3,445 = 0.008230; +/- 0.01613 | CONFIRMED (to the digit) | - |
| 11 | Embedder guards | af ADMIT 69 sites min 0.9990, discriminators REFUSE (other arm -0.0663, permuted 0.6573); N-raw ADMIT 64 sites min 0.9997, REFUSE (-0.0645, 0.8570) | CONFIRMED | - |
| 12 | Write-once outcome; dry-run refuses while builds are ABSENT | real dry-run rc 2 "builds ABSENT (6 of 6)"; R15/R16 KILLED | CONFIRMED | - |
| 13 | Support: SE 0.0083, MDE80 0.023, DEFF 1.0 (source: E1 measured) | measured Kish m-bar 1.0295 / 1.0250 / 1.0331 (rho = 1 upper bound; 3,546 / 3,479 / 3,442 groups); at disc 0.235: SE sqrt(0.235/3,598 x 1.0295) = 0.00820, sqrt(0.235/3,522 x 1.0250) = 0.00827, sqrt(0.235/3,500 x 1.0331) = 0.00833; MDE80 0.0230 / 0.0232 / 0.0233; n_eff 3,495 / 3,436 / 3,388. Power at G = -0.040: z = 0.040/0.0083 - 1.96 = 2.86, 0.998 per split, 0.994 for all three (the registration says 0.99 / 0.97: conservative). Range E = 1.693 x 0.010 = 0.017 | CONFIRMED, NON-VACUOUS (interval clause SCOREABLE; spread clause DESCRIPTIVE-ONLY as registered) | - |
| 14 | Zero writes to DBs of record during my checks | sizes and mtimes of the corpus DB, embeddings_cache.db, snapshots.db and their sidecars identical before and after (`ls --full-time` diff) | CONFIRMED | - |

## Tests and mutants (re-run by me, worktree, TAXOARENA_DATA_ROOT = main)

Selftests: split tool 58 OK; launcher 39 PASSED; readout 129 PASSED. Builder mutants: 19/19, 20/20, 31/31 KILLED. `--check` rc 0
(the numbers above). Real readout `--dry-run` rc 2 at ABSENT, after the identity check HELD. A real launcher `--dry-run` cannot
run before the merge: C-E1-3 requires data root = JVM cwd = the main checkout, so I ran steps (2), (5) and (6) directly
(rows 6 and 14). gradle test not re-run: no src/ change (0 files).

Own mutants (deciding paths):
- RV1 SD1 spread sign `gbar < -ms` -> `gbar < ms`: KILLED (decisive).
- RV2 Q tree read in the nomic space: KILLED (decisive).
- RV3 paired(hq, hn) (sign of G flipped): KILLED (decisive).
- RV4 spread over G instead of per-embedder top-1: KILLED (decisive).
- RV5 every split scored on split 1's held-out (non-vacuity): KILLED (decisive).
- RV6 BETTER without its spread conjunct (`elif all_above:`): SURVIVED. Not decisive: the code is correct; selftest gap (C2).
- RV7 check_order: Q admitted after N_e1sd1 only: SURVIVED. Not decisive: an N after a Q stays REFUSED (fail-closed; it costs one
  extra author checkpoint); selftest gap (C2).
- RV8 identity compares af only: SURVIVED. Not decisive: the code compares the full dict (af, nraw, b, c, n; the real dry-run
  prints all five); selftest gap (C2).

## DEFECTS / CONDITIONS

- **C1 (MEDIUM, operational; binds the run-operator; no blob change)**: the checkpoints run through `tools/ops/wal_checkpoint.py`
  (on main since 8e474b4b), each one preceded by `gradlew --stop` (the tool refuses on any java.exe; Gradle daemons outlive the
  builds). After CP-0, `ls embeddings_cache.db-wal embeddings_cache.db-shm` must find 0 files, or the N dry-run's B-E1-1 refuses.
  This review's launch sequence is the binding text. The launcher docstring wording stays as it is: editing it would move blob
  bdbb3fc6 and the readout's IMPORT_PINS.
- **C2 (LOW, follow-up; not a launch gate)**: add selftest cases that kill RV6 (all lo > 0 and Gbar <= max spread -> NEITHER),
  RV7 (Q after only N_e1sd1 -> REFUSED) and RV8 (identity off in nraw / b / c only -> REFUSED). If done before the run, re-pin
  the readout and launcher blobs.
- D3 (LOW): every build overwrites the untracked `reserved_test_queries.json` in the main checkout (MMLUDatasetFetcher L814), and
  four chain scripts read it. Fix: record its sha256 before N_e1sd1 and restore it after Q_e1sd3.
- D4 (LOW, wording, registrar): "held-out never enters the JVM" (HYGIENE). The engine loads the full corpus and keeps the held-out
  side as its test split. What the guard enforces is "never enters construction" (the [TRAIN-ONLY] line, checked by
  check_run_dir and hygiene()).
- D5 (LOW, Support wording): the measured DEFF upper bound is 1.03, not 1.0 (twin groups inside held-out). SE and MDE80 move in
  the 4th decimal (row 13). The Wald decides without DEFF, as registered. The readout prints m-bar and the bootstrap beside.
- L1 (builder): agreed. FRESH-or-RECORDED + [POOL-PIN] before N_k, assert_pool_of_record(db, id_file) before Q_k and after every
  build, is the satisfiable form of "pool_guard.py --pool <id> before each build".
- L2 (builder): agreed. 2 checkpoints (CP-0, CP-1) within the registered "up to 3"; between builds, views read checkpointed
  scratch copies.
- L3 (builder): agreed, a registrar wording point. F-SD also fires under SD1 BETTER, and its sentence then sits beside a reversed
  loss. Suggested bracket: under BETTER, print F-SD as "fired (reversed sign)".

## LAUNCH SEQUENCE (from the main checkout after the merge; one build per rule-7 window; 12 threads; backup first)

0. Merge e1-split-draws (6ff23dc9) to main. Gradle daemon down: `.\gradlew.bat --stop`.
1. CP-0 (author): `python tools/ops/wal_checkpoint.py --db embeddings_cache.db`; then 0 sidecars beside it. Record the sha256 of
   reserved_test_queries.json (D3).
2. For B in N_e1sd1, N_e1sd2, N_e1sd3, Q_e1sd1, Q_e1sd2, Q_e1sd3: take a fresh backup of both caches (plus any non-empty -wal) to
   E:/TaxoArena_backup_<date>_e1sd/<B>/; run `python tools/analysis/e1sd_launch.py --build B --backup-dir <that dir> --dry-run`,
   then the same without --dry-run; back up the run dir (N: also the working copy) with SHA256SUMS.txt; never commit outputs.
3. CP-1 (author): `.\gradlew.bat --stop`; then `python tools/ops/wal_checkpoint.py --db mmlu_pro_dataset_cache_v2.db`, the same
   with `--db embeddings_cache.db`, the same with `--db snapshots.db`.
4. `python tools/analysis/e1sd_launch.py --verify --backup-dir <the backup taken before N_e1sd1>`; restore
   reserved_test_queries.json.
5. `python tools/analysis/e1_split_draws.py --dry-run` (needs all 6 PRESENT, identity HELD, guards), then `--run` (write-once).

## Commands

```
git cat-file blob 0c12e9b8 | grep -c $'\r'                       # 0 (LF blob)
git diff --name-only a1c65848 6ff23dc9 | wc -l / grep -c '^src/'  # 12 / 0
python tools/analysis/e1sd_split_draw.py --selftest --quiet | --mutants | --check   # 58 OK; 19/19; rc 0
python tools/analysis/e1sd_launch.py --selftest --quiet | --mutants                 # 39; 20/20
python tools/analysis/e1_split_draws.py --selftest --quiet | --mutants | --dry-run  # 129; 31/31; rc 2 at ABSENT, identity HELD
scratchpad/indep_split.py   # own hashlib side + overlaps (stem_key, text, NFKC-casefold) on mmlu_pro (mode=ro&immutable=1)
scratchpad/launch_parts.py  # LA.check_declared x6, LA.coverage x2, LA.pool_check x3, RL.protected_set sidecars
scratchpad/rv.py            # RV1-RV8 on temp copies (selftest exit code)
grep -cE 'p5fb86f1075d76e34|p6d15d913354f256d|p69d2762ac6223d93' experiment_configs/reserved_pools.json   # 0
ls --full-time {mmlu_pro_dataset_cache_v2,embeddings_cache,snapshots}.db*  # before == after
```
