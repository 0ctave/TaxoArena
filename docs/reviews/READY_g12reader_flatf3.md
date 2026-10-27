# READY_g12reader_flatf3: g12-reader c9907919 and flat-f3-fix 4e5a41b9 (both based on f4136a78)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls. No `--run` executed. Nothing written to any DB or output of record.
Reviewed at main 1c5316d8 (the delta since f4136a78 touches neither tools/analysis/flat_v2.py nor g12_reader.py:
`git rev-parse HEAD:tools/analysis/flat_v2.py` = 13fc9de7 = the base; `git ls-tree HEAD tools/analysis/g12_reader.py | wc -l` = 0).

## VERDICT

| branch | merge | run |
|---|---|---|
| g12-reader c9907919 (tools/analysis/g12_reader.py, new) | **MERGEABLE** (by path, 1 file) | **G12 READY to read in lane r2** under GC-1..GC-3 |
| flat-f3-fix 4e5a41b9 (tools/analysis/flat_v2.py) | **MERGEABLE** (by path, 1 file) | **FLAT R2 READY**: `--dry-run --lane r2` then `--run --lane r2`, under FC-1..FC-3 |

No BLOCKER, no HIGH. One MEDIUM for the registrar (D-RV-1, the disclosure wording); LOW defects below.

## Pins (LF of record; CRLF beside)

- g12_reader.py `blob:1c8bf8bccc922449422f5957af99f63c228026aa` / sha256-lf16:15c7ed5d4600f8d9 / sha256-crlf16:bcab0a62bb7b1776
  (`git rev-parse c9907919:tools/analysis/g12_reader.py`; self-identity line of the reviewer's dry-run).
- flat_v2.py `blob:ef7bca333504c9097015d498e24a2af858d409ba` / sha256-lf16:2741fa7dcd859582 / sha256-crlf16:4c00c4aceeed1b4e
  (`git rev-parse 4e5a41b9:tools/analysis/flat_v2.py`; `[SCRIPT]` line of the reviewer's dry-run).
- Reader imports cert_resolution.py blob:dbe9425d (= `main:` and `c9907919:`; LF sha asserted on import).
- Lane r2 inputs, `git hash-object` on main's working tree = `main:` blob = reader pin, for all five: CSV ec8619f8,
  jsonl 11dc92d8, pointer ec718d47, g10_r2.txt fd6fe0ae, gold outcome ec65dd67 (all tracked). Frozen reproduction inputs
  site_null_frozen.csv 1577e9e4, freeze_mcs55 jsonl 1c020ca5, cert_resolution_sites.csv 6d83df50 (all tracked, LF shas = pins).

## Per-claim table (deciding claims)

| # | claim | result | reviewer's evidence | sev |
|---|---|---|---|---|
| 1 | g12 selftest 15/15, mutants 25/25 killed | CONFIRMED | re-run on a `git archive c9907919` copy: 15 checks 0 failed; 25 run 25 killed | - |
| 2 | reproduces cert_resolution 66/66 on the frozen tree | CONFIRMED | st12 PASS (row-by-row p_site, family_key, reached, hier_bh, cert); independent read of the CSV of record: frozen 66 rows, hier_bh {n00000006, n00000005} | - |
| 3 | real dry-run lane r2 passes, computes nothing | CONFIRMED | rc 0; 5 pins match; "G10: HELD"; gold H 0.2912 > p95 0.0264; snapshot 20261001_094311 = pointer = G-1; identity PASS, multi-parent 0; 60 sites (d1 14, d2 22, d3 21, d4 2, d5 1), 33 families, TOP m 14, depths [1] = g12_dryrun.txt (bf32edf8) L4; "0 statistics evaluated"; `--lane r1` REFUSED rc 2 | - |
| 4 | deciding statistic = the registered one (hierarchical BH, per-family q 0.05, 300 reps, CERT-RESOLUTION's instrument; N-1 FIRES iff no depth-1 site in the set) | CONFIRMED | imported, not copied; `n1_verdict` is the registered clause; on R2 all 14 depth-1 sites ARE the TOP family, so N-1 = "no TOP rejection" | - |
| 5 | Support: SE sqrt(.05 x .95 / 300) = 0.01258, MDE80 0.0352 per site, DEFF 1 (source: ARCH-V2-E-T Support (a)-(g), "deterministic set readout"; R2 L22427 carries G12 0.0352) | CONFIRMED | 0.0475/300 = 1.5833e-4, sqrt = 0.012583, x 2.80 = 0.035232; bar m = 14 <= 15: 1/301 = 0.003322 <= 0.05/14 = 0.003571 (reachable; a TOP rejection needs one k = 0 site). SCOREABLE | - |
| 6 | R-a: Binomial(m, 0.05) with m = all sites | CONFIRMED (reading) | matches F-TAX N-1's own example "P(>= 5 of 70 \| 5%) = 0.272" (70 = bareq512_s42's site count in cert_resolution_sites.csv); orchestrator-confirmed 7f83622d; descriptive only, never deciding | - |
| 7 | R-c: "site-null floor" undefined -> NOT EVALUATED | CONFIRMED | `grep -c "site-null floor"` prog = 5, none numeric; rev2 L825, framing L108, synthesis L316: no number; orchestrator ruling recorded 7f83622d (never defined after data). Only feasibility OK + reps 300 checked (CR refuses otherwise) | - |
| 8 | D-G12-1: bar and an N-1 clause both apply at m > 15; unreachable on R2 | CONFIRMED | m = 16, two k = 0 TOP sites: 1/301 = 0.00332 <= 2/16 x 0.05 = 0.00625, so BH rejects while the bar reads UNDETERMINED (st07 asserts it); R2 m = 14 pinned by G-3 | LOW |
| 9 | the "site-cert 1/60" sight does not compromise the reader | PARTLY (not compromised; the record understates what was seen) | see D-RV-1 | MEDIUM |
| 10 | flat selftest 13/13; DF1 killed | CONFIRMED | re-run in a detached worktree at 4e5a41b9: 13/13; FM1 (= DF1) killed 12/13 | - |
| 11 | the CLI dry-run now prints [F-3] | CONFIRMED (real data) | reviewer's real `--dry-run --lane r2` (DATA_ROOT rp12-r2-run, java 0): rc 0, `[F-3] T2 census equals the pin: snapshot 20261001_094311_Headless_Run_Auto_ge, leaves 74, root fit ids 6993` right after the census line; diff vs the operator's flat_dryrun2.txt = the [SCRIPT] line + that one inserted line only; DATA_ROOT `*.db*` size+mtime listing identical before/after | - |
| 12 | `over` semantics unchanged elsewhere | CONFIRMED | `t2_spec` applies only non-None values (empty dict == all-None dict); `header(over)` ignores it; `run`/`analyze` take no override | - |

## D-RV-1 (claim 9): what "site-cert 1/60" carries

cert_site_p95 (observed > the site's null p95) needs k <= 14; any BH rejection needs (k+1)/301 <= q r/m_f <= 0.05, i.e. k <= 14.
On the record, hier_bh is a subset of cert_site_p95 on all 265 sites of 4 trees (cert_resolution_sites.csv: 0 hier-not-cert).
So the count 1/60 bounds the hierarchical-BH set at <= 1 site: P3's set-size leg ("1 [0, 3]") is foreknown HELD, and N-1
hinges on whether that one site is a depth-1 site at k = 0. It is therefore more than "a count beside G12".
Not compromising: the reader has no data-dependent lever on the deciding path. N-1 and the bar are a transcription of the
registration (mutants bar_ge, fires_first, set_nonempty, wrong_depth, q_010, flat_not_hier, GM4 killed); R-a moves only a
descriptive tail; R-c is NOT EVALUATED (the one lever that could have produced UNDETERMINED was not pulled, and is now the
orchestrator's ruling); D-G12-1 is unreachable at m = 14; P3 was registered pre-data and is scored as registered. The
sentence is in the untracked site_null.log (`git show 6a6d2715 --name-only` = 1 file, the CSV).
**Fix (registrar, insertion only):** bracket the 7f83622d DISCLOSURE: "the per-site count bounds the hierarchical-BH set at
<= 1 site (hier subset of cert on 265/265 sites of record), so P3's set-size leg was foreknown; no reader parameter depends on it."

## Conditions

- **GC-1** Run from main after the by-path merge: `python tools/analysis/g12_reader.py --run --lane r2`, with the reader at
  blob:1c8bf8bc and cert_resolution at dbe9425d; it refuses unless the 5 inputs match their pins (verified now).
- **GC-2** `experiment_results/archv2/rp12_r2/g12/` holds no G12_OUTCOME.txt / G12_sites.csv before the run (`ls` now: 2
  entries, site_null.log and the CSV); the run's in-process selftest + 25 mutants must be green (it refuses otherwise).
- **GC-3** D-RV-1 bracket by the registrar before the outcome section is written (it does not block the run).
- **FC-1** OC-1 stands: `TAXOARENA_DATA_ROOT` = `.claude/worktrees/rp12-r2-run` (absolute). OC-2 discharged (53a46849; no
  embeddings_cache.db-wal now; snapshots.db-wal 0 bytes).
- **FC-2** The operator's own `--dry-run --lane r2` after the merge must print `[SCRIPT] ... blob:ef7bca33` and the [F-3] line
  above (OC-3); then `--run --lane r2`.
- **FC-3** Rule 7 / one heavy process: FLAT --run is a pool reader; not beside a construction or site null (java 0 at review).

## Defects

- **D-RV-1 MEDIUM** (registrar wording) above.
- **D-RV-2 LOW (flat)** FM3 survived: `(a.run or a.analyze or a.identity_check) and over` -> `and False` passes 13/13; the
  refusal of census overrides beside --run/--analyze/--identity-check is untested (run() ignores overrides, so not decisive).
  Fix: a main() case `--run --leaves 74` asserting the refusal text.
- **D-RV-3 LOW (g12)** GM1 survived: B-A2's alternative wording on a NOT verdict when H <= p95 is untested (unreachable on
  record: H 0.2912 > p95 pinned). Fix: in st05, a NOT fixture with H 0.0100 asserting "N-1 did not fire, no wording changes".
- **D-RV-4 LOW (g12)** GM2 survived: the families-count leg of the G-1 equality is untested (G-3 itself needs sites and TOP
  m). Fix: a fixture with expect families off by one.
- **D-RV-5 LOW (g12)** GM3 survived: gold gate's p95 comparison untested; redundant with the outcome.txt sha pin. Fix: a
  fixture line "H 0.2912 > p95 0.0300".

## Mutants (reviewer's own; one temporary edit each, reverted; sha re-checked after)

| id | change | result | decisive |
|---|---|---|---|
| GM1 | `if w == "FIRES" and alt` -> `if alt` | survived | no (unreachable on record) |
| GM2 | G-1 equality drops families | survived | no |
| GM3 | gold gate compares H only | survived | no (sha pin) |
| GM4 | NOT returned before the m > 15 bar | killed (st03, st07, st13) | yes |
| GM5 | per-site count = len(BH set) | killed (st07, st12) | yes |
| GM0 | comment control | survived (control) | - |
| FM1 | always-truthy `over` (= DF1) | killed (12/13) | yes |
| FM2 | check_census never refuses | killed (12/13) | yes |
| FM3 | override refusal off | survived | no |
| FM0 | comment control | survived (control) | - |

## Commands

```
git rev-parse g12-reader flat-f3-fix c9907919:tools/analysis/g12_reader.py 4e5a41b9:tools/analysis/flat_v2.py main:tools/analysis/cert_resolution.py
git diff --stat f4136a78 g12-reader ; git diff --stat f4136a78 flat-f3-fix          # 1 file each
for f in <5 lane inputs + 3 frozen inputs>; do git hash-object $f; tr -d '\r' <$f | sha256sum; git rev-parse main:$f; done
git archive c9907919 tools/analysis <inputs> | tar -x -C scratch/g12
python tools/analysis/g12_reader.py --selftest | --mutants | --dry-run --lane r2 | --dry-run --lane r1
python: cert_resolution_sites.csv per tree: |hier_bh|, |cert|, hier-not-cert (0 on 66/70/69/60)
git -c core.longpaths=true worktree add --detach scratch/wtf 4e5a41b9 ; python tools/analysis/flat_v2.py --selftest
TAXOARENA_DATA_ROOT=.../rp12-r2-run python tools/analysis/flat_v2.py --dry-run --lane r2 ; diff vs flat_dryrun2.txt
ls -la --time-style=full-iso rp12-r2-run/*.db* before/after (identical) ; tasklist java (0)
scratch/mut_g12.py, scratch/mut_flat.py (mutant harnesses; originals restored; worktree removed, `git worktree list | grep -c scratchpad` = 0)
grep -c "site-null floor" docs/judge_v2_program.md (5) ; git show 6a6d2715 --name-only --format= | wc -l (1)
```
