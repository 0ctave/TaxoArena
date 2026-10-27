# READY review: G13-BREAKDOWN, branch g13-breakdown tip 4f1fd60f (cut from 0b4b11a6)

Reviewed blob: `tools/analysis/g13_breakdown.py` blob:3e284ac8c4ebeb9e3232e01cac82438b3a01c673 (LF; the worktree file is LF,
`git hash-object` = the tip blob; this repo has core.autocrlf=true, so a main checkout may render CRLF: the pin is the LF blob).
Registration of record: prog L22887-L23048 _as_of ffed1d52 ("## Registered 2026-10-02 (before any code or call) — G13-BREAKDOWN: ...").
Reviewer: adversarial-reviewer, 2026-10-02. Zero calls. No --run. Dry-run: structure-only, through a wrapper that replaced the
pool-guard call (D-1) with the B0-2 form; nothing else changed.

## Verdict

- **--run: NOT READY at 4f1fd60f.** D-1 (BLOCKER): the script's first step, `pool_guard.py --pool pv2_1575de61bb20e977`, returns
  rc 1 in main as well as in the worktree (the registry holds 0 pv2 pools), and the script refuses on rc != 0. A --run from main
  refuses at line one. The selftest stubs the guard to rc 0, so it never saw this.
- **READY WITH CONDITIONS C1-C6 once D-1 is fixed** and delta-checked (the diff, `--selftest`, `--mutants`, and a `--dry-run --lane r2`
  from main that prints the B0-2 lines). Everything else on the deciding paths reproduces or is implemented as registered.
- **MERGEABLE after the D-1 fix** (the merge itself is clean: 0b4b11a6..4f1fd60f adds 1 file; main's 4 later commits touch nothing
  under tools/ or rp12_r2, by `git diff --stat 4f1fd60f main -- experiment_results/archv2/rp12_r2 experiment_configs tools`).

## Per-claim table (deciding claims)

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | I1 reproduces G13: P_fl, P(KC_s) x5, D13 -0.0215 [-0.0301, -0.0125], U-global x5, NCC | CONFIRMED | dry-run I1 PASSED, all ten strings equal; P_fl 0.811859 recomputed from eval_fl and from the CSV (own script) | - |
| 2 | MC-EXCLUDE applied: 6,139 EVAL / 5,628 comp; TRAIN 12,334 | CONFIRMED | own: 6,139 / 5,628 / 12,334, EVAL∩TRAIN 0; per source 3478/3386, 1718/1408, 390/382, 229/129, 162/162, 162/161 = Support (a); excluded EVAL 14, GATE 5, TRAIN 15 | - |
| 3 | I2 P_descent 0.7182 on the bundle items | CONFIRMED | own 0.718195 | - |
| 4 | I3 >= 99.9% argmax-vmfMu = CSV leaf | CONFIRMED | own: 0 misses of 6,139 (script: 0) | - |
| 5 | I4/I5 133 leaves, 74/36/9/6/5/3 | CONFIRMED | own parse of the six LAST snapshot lines | - |
| 6 | A3 frontier and KC(d); KC(2) = NCC | CONFIRMED | own: F(2..7) = 52/84/109/130/132/133 nodes, 0 empty, sum k_c = same; k_c(2) = 1 for all 52 classes; the run asserts KC(2)_s = NCC item-wise | - |
| 7 | Criteria as registered incl. pre-data changes: C-a1/C-a4 interval below 0; C-b2/C-b1 interval AND spread (REVERSED = FAILED); C-M with the FAILED clause; UNRESOLVED printed UNDETERMINED | CONFIRMED (inspection L271-L295, L892-L962) | - | - |
| 8 | Support: SE / MDE80 as bracketed (0.00724/0.00466/0.00629/0.00199; 0.0203/0.0131/0.0176/0.0056), DEFF 1.214 measured in G13 | CONFIRMED | own sqrt(disc/n x 1.214) reproduces all eight to the digit; the script prints measured SE, DEFF, n_eff, MDE80 beside every deciding statistic (stat(), L257) | - |
| 9 | Every fit TRAIN-only | CONFIRMED | KC, KC(d), U-global, U-source, KC-relabel, source centroids, kNN read Xt/yt; A3 names from the TRAIN CSV leaves (tleaf); load_bundle runs check_sides (no EVAL/GATE in TRAIN); my mutant X3 (frontier named from EVAL) KILLED | - |
| 10 | (c) computed as registered; (d), (e) descriptive | CONFIRMED | (c) L742-L754; (d)/(e) feed render only, no verdict reads them | - |
| 11 | "pool_guard.py --pool pv2_1575... printed in the dry-run" (registered HYGIENE) | REFUTED | rc 1 from main (`not in the registry`); 0 occurrences of v2_union_pool / 79d48f4b in the script | BLOCKER (D-1) |
| 12 | selftest 10/10; mutants 38/38 KILLED, control survived | CONFIRMED | re-run at 4f1fd60f | - |
| 13 | Run must be from main (member logs untracked) | CONFIRMED | 8 headless_run.log in main, 0 in the worktree (ls); a worktree run prints ABSENT/INCOMPLETE for (d) only | - |
| 14 | Pinned readers | CONFIRMED | g13_comparator 61d83ec7, rp12_pairing 35214b3f, flat_mix_mmlu 555ae3ac = HEAD blobs in main and at the tip; rp12_lane ac25b152 unpinned (D-4) | LOW |

## Builder's open readings (rulings)

- R1 tree end-to-end = six member manifests + flatLeaf graft: ACCEPTED (prediction D only; descriptive; the flatLeaf filings
  scored here need the graft; members-only ratio printed beside). Seen loop sum check: first TOTAL TIME per member log
  15,313 + 2,263 + 1,716 + 3,268 + 88,226 + 1,731 ms = 112.5 s = the registered seen point; the parser handles "15 313 ms".
- R2 "D(>= 5) within 0.005 of D13" scored at d = 5, 6, 7: ACCEPTED, condition C5: it is ONE prediction; the outcome states HELD
  iff all three checks hold. Note D(7) != D13 by construction: one leaf (MMLU_PRO_LB:n00000162) is "other" in the leaves CSV
  (construction profile) but "physics" by TRAIN-routed majority (30 vs 27); the run prints this count (expected 1).
- R3 C-b1 measured support only: ACCEPTED (the registration fixes no SE for C-b1; Support (f) is seen point vs seen spread).
- rp12_pairing as an extra pinned import: ACCEPTED as an ADDITION (it is G13's own CSV/MC-EXCLUDE reader, pinned to the HEAD
  blob), not a substitution; the registrar records it (C6).

## Own mutants (in-memory edit of the tip blob, full --selftest; control 10/10)

| id | change | result | decisive |
|---|---|---|---|
| X1 | C-b2 spread clause reads spread_U (U-global) instead of spread_US | SURVIVED | yes (C-b2) |
| X2 | Delta = (fl-KC_0) - (tree(2) - KC_0) instead of - NCC | SURVIVED | yes (C-a4) |
| X3 | A3 frontier named from EVAL items/labels | KILLED (4/10) | yes (leakage) |
| X4 | G_own sign reversed | SURVIVED | yes (C-M) |
| X5 | D_U against U-global seed 1 | SURVIVED | yes (C-b1) |
| X6 | I1 does not compare lo/hi | SURVIVED | no (real dry-run matched lo/hi) |
| X7 | U-source primary filed within the true source | KILLED (crash; builder's M10 kills by value) | yes |

X1, X2, X4, X5 survive because fixture A is degenerate on them (KC_0 = NCC item-wise, G_own = 0, D_U insensitive to the U seed /
spread choice). The code is correct on all four by inspection (L710, L715, L739/L922, L770); see D-2 and C4.

## Defects

- **D-1 BLOCKER** pool guard unexecutable (as known since READY_rp12_et2 #8 / B0-2, prog L22165). Fix: replace `_pool_guard_proc`
  with the B0-2 form: run `tools/analysis/v2_union_pool.py --dry-run`, require rc 0 and both lines "... expected
  pv2_1575de61bb20e977" and "every check passed"; check `experiment_configs/engine_pool_pv2_1575de61bb20e977.json` sha256-lf
  79d48f4b36434a55 (measured now: 79d48f4b36434a55) and 0-byte -wal/-journal; keep the refusal and its selftest case. Registrar
  brackets the HYGIENE sentence onto the B0-2 form before the run (C6). Verified feasible: with exactly this substitute guard the
  dry-run passed I0-I5 and I1 in 16.5 s (output below).
- **D-2 MEDIUM** selftest blind to the deciding arithmetic of C-b2, C-a4, C-M, C-b1 (X1, X2, X4, X5). Fix (recommended, not
  gating): a fixture variant with NCC != KC_0 item-wise, G_own != 0 and U seeds that move D_U. Gating substitute: C4.
- **D-3 LOW** X6: the I1 refusal test does not exercise lo/hi. Fix: perturb hi in the I1 refusal case.
- **D-4 LOW** rp12_lane imported unpinned (guard only; can only weaken a refusal). Fix: add (rp12_lane.py, ac25b152...) to PINS.
- **D-5 LOW (registration gap)** A3 says the leaf-depth strata counts are "fixed in Support"; Support lists none. Fixed here,
  pre-run, from the committed CSV: depth 2 / 3 / 4 / 5 / >= 6 = 1,167 / 1,839 / 1,325 / 1,596 / 212 (6 = 159, 7 = 53).
- **D-6 LOW** A2 tree source (choice iii, the named class's source) vs A3 d = 1 (the corpus root's source) are two definitions;
  moot on these objects: 0 leaves are named with another source's class (own count).

## Conditions for the --run

- C1 D-1 fixed in the branch, delta-checked (diff + selftest + mutants + main dry-run printing the B0-2 lines), then merged.
- C2 Run from main (the 8 untracked logs); the outcome's (d) block must show 8 TOTAL TIME blocks and no "INCOMPLETE".
- C3 After the current Ollama pass ends; no construction or site null beside it (rule 7); the machine-state line printed shows no
  java and no active embedding; [THREADS] = 1.
- C4 Post-run reviewer recomputes from the printed means: D_Us = P_fl - P(US_0), D_U = P_fl - P(U_0), Delta = D13 - (P_tree(2) -
  P_NCC), G_own = P(KC_0) - P(KC-relabel_0), and checks C-b2's spread clause against spread_US (paired mean = difference of means).
- C5 The D(>= 5) prediction reported once (HELD iff d = 5, 6, 7 all within 0.005); D(7) - D13 read with the naming note (R2).
- C6 Registrar, pre-run: HYGIENE bracket (B0-2 form); DEV note for the rp12_pairing pin and D-5's counts; the operator pins the
  run's script blob as LF (with the CRLF rendering beside if main's file differs).

## Commands

```
git diff --stat 0b4b11a6..4f1fd60f                       # 1 file changed, 2051 insertions
git hash-object .claude/worktrees/g13-breakdown/tools/analysis/g13_breakdown.py   # 3e284ac8 (LF)
for f in g13_comparator rp12_pairing flat_mix_mmlu rp12_lane; do git hash-object tools/analysis/$f.py; done   # = tip/HEAD blobs
python tools/analysis/g13_breakdown.py --selftest        # (worktree) 10 / 10 passed
python tools/analysis/g13_breakdown.py --mutants         # 38 of 38 KILLED; control survived
python tools/analysis/pool_guard.py --pool pv2_1575de61bb20e977   # (main) rc 1: not in the registry  -> D-1
grep -c pv2_1575de61bb20e977 experiment_configs/reserved_pools.json      # 0 (main)
grep -c "v2_union_pool\|79d48f4b" tools/analysis/g13_breakdown.py        # 0 (tip)
python tools/analysis/v2_union_pool.py --dry-run         # (main) "... expected pv2_1575de61bb20e977"; "every check passed"
python scratchpad/g13r/wrap_dry.py --dry-run --lane r2   # tip module, guard -> v2_union_pool form only: I0-I5, I1 PASSED,
   # F(2..7) 52/84/109/130/132/133, I3 0 misses, MC 14/5/15, "NO new statistic", 16.5 s
python scratchpad/g13r/indep.py    # own: counts, P_fl 0.811859, P_descent 0.718195, I3 0, F(d), strata counts, SE/MDE80 arithmetic
python scratchpad/g13r/indep2.py   # leaf_major multiset = CSV leaf_dominant; 1 leaf named differently by TRAIN routing
python scratchpad/g13r/runmut.py X1..X7                  # own mutants (table above)
ls experiment_results/archv2/rp12_r2/B0/*/seed_42/headless_run.log | wc -l   # main 8; worktree 0
LC_ALL=C grep -a 'TOTAL TIME' .../B0/*/seed_42/headless_run.log              # first lines sum 112,517 ms
```
DB hygiene: no DB of record opened by the readout; the only recent *.db mtime in the repo root (intent_emb_gemma_card.db, 00:22) is
another lane's: no script this review ran opens it.

## Delta review 2026-10-02: tip 8f68476c (g13_breakdown.py blob:c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40, LF), against D-1, D-3, D-4

Scope: `git diff 4f1fd60f..8f68476c` (1 file, +129 / -15; `--name-only | wc -l` = 1), plus regression. Zero calls. RP20 files untouched.

**Verdict: MERGEABLE. --run READY under C2-C5** (C1 met by this delta; C6 met, registrar 16f01c43). Pin the run's blob as LF
c29fa1c3 (the worktree file hashes to the tip blob; a main checkout may render CRLF: name both if they differ).

| # | Claim | Result | Evidence | Sev |
|---|---|---|---|---|
| D-1 | pool_guard replaced by the B0-2 form: -wal/-journal of multicorpus_cache_v1.db and the SPLIT-2 corpus_v2_union_mc6.db absent or 0 bytes; engine pool file sha256-lf = 79d48f4b...; child `v2_union_pool.py --dry-run --pool <pool>` rc 0, first line "...recomputed...; expected <pool>", an "every check passed" line; main refuses on rc != 0 | CONFIRMED | diff (pool_check_v2); real dry-run from main (below): line 1 `POOL pv2_1575de61bb20e977 (B0-2 pool check rc 0): ... 5642 EVAL components ...; expected pv2_1575de61bb20e977 \| ... every check passed; nothing written ... \| engine pool file sha256-lf 79d48f4b36434a55 (pinned) \| multicorpus_cache_v1.db-wal 0 bytes; -journal absent; corpus_v2_union_mc6.db-wal absent; -journal absent`; own sha256 of the pool file 79d48f4b36434a55... | closed |
| D-1b | selftest exercises the REAL check with refusals | CONFIRMED | `guard` case runs pool_check_v2 (asserts `_POOL_GUARD[0] is pool_check_v2`) on v2_union_pool's own fixture DBs: accept (0-byte -wal passes), another pool (child S2, rc 1), pin mismatch, 5-byte -journal, 3-byte -wal, main() refusing with the check's line first. Selftest 11/11 | closed |
| D-3 | I1 refusal on hi | CONFIRMED | refusal case "I1 hi"; M39 (I1 ignores lo/hi) KILLED (= my prior X6) | closed |
| D-4 | rp12_lane pinned | CONFIRMED | PINS has ac25b152...; `git hash-object` main file = HEAD blob = ac25b152; dry-run line 2 prints it | closed |
| M | 43/43 mutants killed, control survived | CONFIRMED | re-run: "MUTANTS: 43 of 43 KILLED; control survived" (75 s) | - |
| R | real dry-run unchanged otherwise | CONFIRMED | I0, I1 (d13 -0.0215 [-0.0301, -0.0125], ncc 0.8065, p_fl 0.8119), I2 0.7182, I3 0 of 6139, I4 133 leaves, I5 6139/5628/12334; "NO new statistic"; 18.2 s, rc 0 | - |

Own mutants (in-memory copy, full --selftest):

| id | change | result | decisive |
|---|---|---|---|
| Y1 | first-line ("recomputed ...; expected <pool>") check removed | SURVIVED | no: a pool mismatch is refused by the child (S2, rc 1), covered by the guard case and M42 |
| Y2 | only -wal checked, -journal skipped | KILLED (guard 10/11) | yes |
| Y3 | guard_dbs loop over nothing | KILLED (guard 10/11) | yes |

Defects: **D-7 LOW** (Y1): the first-line assertion is untested on its own. Fix (optional, not gating): a guard case whose child
prints rc 0 with a different first line (stub the child). D-2 (MEDIUM) stands as recorded; C4 remains its gating substitute.

Merge: `git diff --stat 8f68476c main -- tools experiment_configs experiment_results/archv2/rp12_r2` = 1 file (g13_breakdown.py,
absent in main); 4f1fd60f is an ancestor of 8f68476c. Clean.

Hygiene: the dry-run was run from main with the tip blob written to tools/analysis/g13_breakdown.py (untracked; hash c29fa1c3) and
removed after (`ls` -> absent); the worktree cannot run it (DATA_ROOT is repo-relative; its DBs are in main). Before/after: the two
guard DBs' sizes and mtimes unchanged (mc 11:44:29, -wal 0 bytes 19:43:30; corpus SPLIT-2 20:22:44, read-only, no sidecar); no
outcome file written. RP20: no file of it opened or written by this review.

```
git diff 4f1fd60f..8f68476c ; git diff --name-only 4f1fd60f..8f68476c | wc -l          # 1
git hash-object .claude/worktrees/g13-breakdown/tools/analysis/g13_breakdown.py       # c29fa1c3 (LF)
git hash-object tools/analysis/rp12_lane.py ; git rev-parse HEAD:tools/analysis/rp12_lane.py   # ac25b152 both
sha256sum experiment_configs/engine_pool_pv2_1575de61bb20e977.json                    # 79d48f4b36434a55...
python tools/analysis/g13_breakdown.py --selftest        # (worktree) 11 / 11 passed
python tools/analysis/g13_breakdown.py --mutants         # (worktree) 43 of 43 KILLED; control survived
git show 8f68476c:tools/analysis/g13_breakdown.py > tools/analysis/g13_breakdown.py   # (main, temporary)
python tools/analysis/g13_breakdown.py --dry-run --lane r2 ; rm tools/analysis/g13_breakdown.py   # rc 0, POOL line above
python scratchpad/om.py                                  # Y1 SURVIVED, Y2 / Y3 KILLED
ls -l --time-style=+%T multicorpus_cache_v1.db* data_v2/REG_ARCHV2-SPLIT-2*/corpus_v2_union_mc6.db*   # before = after
```
