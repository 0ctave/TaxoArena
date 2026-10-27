# READY review: GRANULARITY-SWEEP (branch granularity-sweep, tip d7ab9629)

Reviewer: adversarial-reviewer, 2026-10-06. Zero calls. Registration: docs/judge_v2_program.md "## Registered 2026-10-06 (before
any code or call) — GRANULARITY-SWEEP: ..." L24828-L24840 (_as_of 9bff7e39). Instrument reviewed: tools/analysis/granularity_sweep.py
**blob:1cf20fe88993bbcdfb780fd34a1b3de38dcf6cf8** (LF, of record; sha256-lf16:68e62892525683aa; CRLF rendering
sha256-crlf16:66012b9f5f98fb11; the worktree file holds no CR, so the two views agree).

## VERDICT: READY (no blocker)

Conditions (none blocks the run):
- C-1: --run is launched DETACHED (Start-Process) and polled (builder's estimate 1.5-3 h: B 2,000 replicates, each re-fitting the
  TRAIN 3PL and 59 arms' policies); busy.ps1 rc 1 before launch; nothing else reads the pool in the window (rule 7).
- C-2: the post-run review prints the realised DEFF, n_eff and MDE80 of D_lo and D_hi (the "support D_lo / D_hi" lines) against the
  registered 1.847 / 3,198 / 1.74pp (one contrast) / 1.99pp (both), and re-measures DEFF from the outcome's replicate SDs (D-5).
- C-3: the post-run reading carries the words of D-1, D-3 and D-4 below (registrar brackets before the run).

Readings stated by the builder, ruled here:
- GS-R1 (allocation): CONFIRMED. My own largest-remainder script gives 25/50/100/123/200/398 with the identical per-source cells
  (k 400: MMLU_PRO_LB 225, BBH 118, MATH 33, MUSR 10, GPQA 11 = cap; caps 1351/694/154/90/11 = floor(count/5)).
- GS-R2 (k-means = construction_arms.skm_best, n_init 5, intent_transfer_s0.skmeans): CONFIRMED as the literal registered text, with
  the words of D-1 (it is NOT K_s's own algorithm).
- GS-R5 (tree cut counts structural TRAIN items; overshoot allowed): CONFIRMED for a descriptive arm, with D-3's words.
- GS-R8 (seeds on a second stream default_rng(20261006), with replacement, the same draw for every k): CONFIRMED. The registration
  names default_rng(42) for the bootstrap; run_boot (pinned, unchanged) consumes that stream for the units, so a joint draw from the
  same stream would need an edit of a pinned import. The second stream is fixed pre-data and in the selftest (X49 killed). See D-2.
- GS-R10 (R2_int replicate intervals add a 3PL re-fit per replicate): CONFIRMED (descriptive; run_boot calls the hook once per two-
  stage replicate, in replicate order, v2_declared_cells L708-L714, so rec["r2"][b] aligns with SD[b]).
- GS-R3, R4, R6, R7, R9, R11-R13: CONFIRMED (read against L24832-L24834; mutants below).

## Per-claim table (deciding claims)

| # | claim | reviewer's result | verdict | sev |
|---|---|---|---|---|
| 1 | blob 1cf20fe8 LF; lf16 68e62892; crlf16 66012b9f | `git hash-object` 1cf20fe8…; python sha256 LF 68e62892525683aa / CRLF 66012b9f5f98fb11; `b'\r\n' in data` False | CONFIRMED | — |
| 2 | the six imports at the registered blobs | d5473976, 92a04543, bf3f17db, f0f56805, 1817ec8a, 5d08a5df in the worktree AND on main (`git rev-parse main:<path>`); `git diff --name-only 9bff7e39 main -- <7 paths> \| wc -l` = 0; the script refuses at import on any other blob (PINS) | CONFIRMED | — |
| 3 | the commit touches only the new script | `git show --name-only --format= d7ab9629 \| wc -l` = 1; `git diff --name-only 9bff7e39 d7ab9629 \| wc -l` = 1; worktree `status --porcelain \| wc -l` = 0 | CONFIRMED | — |
| 4 | --selftest 9/9 | my run: 9 / 9 passed (1 min 56 s; scratch on E:, entries before 145 = after 145) | CONFIRMED | — |
| 5 | mutants 52/52 killed, control survived | my re-run: "52 of 52 KILLED; control SURVIVED; survivors none; not applied / errors none" | CONFIRMED | — |
| 6 | real --dry-run clean | delta round: rc 0 (busy.ps1 rc 1 before and after; 59 lines); POOL line first; B0-2 rc 0; AF-U commit 1075b506, 123 leaves = profile; inputs manifest 53021e26 (18 + 11 EQUAL); policy 8d68018c; allocation 25/50/100/123/200/398 = GS-R1; TRAIN 12,351 / key-complete 11,841 = registration; gen_view sha before = after c2930c60; eval view NOT opened; output dir absent before and after | CONFIRMED | — |
| 7 | GS1 code = registration | gs1_verdict L614-L626: k* not in {50,100,200} → NOT-SHOWN (EDGE); else each of D_lo, D_hi needs point > 0 and lo > 0, else NOT-SHOWN with the failing D named; rule 8 REFUTED iff NOT-SHOWN; F-GS iff G_KW(25) − G_KW(100) > 0 and lo > 0 (L822-L831). k* = first strict max of mean_s G_KW on GATE over the grid only (123 never; L629-L635, L722-L724). lo = point − 1.96 SE_2stage (U.interval L359-L366, G14's form) | CONFIRMED | — |
| 8 | the deciding interval respects the design | D_lo, D_hi: per seed KW(k*,s) − KW(k_ref,s) (best single cancels, d_terms L713-L715), inside ONE two-stage replicate (TRAIN units re-drawn, every policy re-fitted; EVAL components within stratum), then the mean over the SAME five drawn seeds SD[b] (seed_stat L600-L611): item-paired, policy-refit-paired and seed-paired across k, as registered. Cells are fixed per seed (the seed term carries cell-fit variation). No triplets (STABILITY-VS-KMEANS B-1 n/a). k* on GATE with the full-TRAIN policy, never EVAL (no DRIFT-REPLAY self-calibration; X09, R2 killed). GS1 is KW vs KW: same construction at every k, no shape confound (CONSTRUCTION-ARMS lesson applies only to TC − KW, D-3) | CONFIRMED | — |
| 9 | no leakage | k-means fitted on the AF-U bundle's TRAIN rows only (prepare L512; R4 "fit on the bundle's EVAL rows" KILLED); Ward on TRAIN centroids; TC counts from the TRAIN side (X27 killed); TRAIN key, then GATE key (between-hook, gen view), then the marker and ONE EVAL read (read_views); [GSWEEP-K0] proves the slice/vectors/filing are K_s's before any key | CONFIRMED | — |
| 10 | Support (b)-(f) arithmetic | sources: ROUTE-SOURCE-NULL.json L79 (D_S SE 0.599pp, DEFF 1.847, n_eff 3,198, 5,907/5,404); UNION-AF-ROUTE.json L150 / POSTRUN_union_af_route L25 (spread_K 0.58pp, 0.00576). Mine: σ_seed 0.58/2.326 = 0.2494; √(2/5)·0.2494 = 0.1577; SE √(0.599² + 0.1577²) = 0.6194pp; n_eff 5907/1.847 = 3198.2; MDE80 2.8·0.6194 = 1.734, 3.21·0.6194 = 1.988pp (z for power √0.8: 1.2504); GATE SE 0.60·√(5907/1944) = 1.046pp; n* 1.311·7.84·0.30/0.01 = 308.35 → 309. All reproduce; the code's SUPPORT dict carries the same numbers. Verdict line DESCRIPTIVE-ONLY reproduces (0.4 < 1.99) | CONFIRMED (D-5) | LOW |
| 11 | identity before any new number | [GSWEEP-IDENTITY] and [GSWEEP-TC-IDENTITY] refuse (L961-L973) before analyze/gs_lines print anything; the GATE curve and k* are computed only in analyze (X31, X32 killed) | CONFIRMED | — |
| 12 | count checks, not presence checks | TRAIN per-source counts and caps = registered (refuse), GATE key-complete = 1,944 (refuse), DENOM 5,907/5,404, G3 = B + 2 fit checks, TC availability = (25, 50, 100, 123) (refuse), allocation nesting (refuse) | CONFIRMED | — |

## Mutants

Builder suite (`--mutants`, sandbox fixtures, scratch on E:): 52 of 52 KILLED, control X00 SURVIVED.

Reviewer's mutants (E:/TaxoArena_tmp/gsrev/rev_mut.py calls the module's own `_mutant_one`; sandbox only): 8 of 8 KILLED, control
SURVIVED.
- R1 deciding interval at z 1.645: KILLED. Decisive.
- R2 GATE curve read from seed 0's cells and policy for every seed: KILLED. Decisive (k*).
- R3 GS1 reads the upper bound instead of the lower: KILLED. Decisive.
- R4 k-means fitted on the bundle's EVAL rows (leakage): KILLED. Decisive.
- R5 KW never cut (every k = the top fit): KILLED. Decisive.
- R6 TC cut overshoots by one more expansion (`<=`): KILLED. Not decisive (TC descriptive).
- R7 F-GS against k_own (123) instead of k_mid (100): KILLED. Decisive (falsifier).
- R8 D point = mean of the two-stage replicates: KILLED. Decisive.

## Defects

- **D-1 LOW (GS-R2 words).** K_s (UNION-AF-ROUTE) was fitted by union_af_route.us_fit → g13_breakdown.ukm_fit →
  flat_mix_mmlu.spherical_kmeans (n_init 1, its own k-means++), while KW / KF use construction_arms.skm_best (intent_transfer_s0.skmeans,
  n_init 5), as the registration's literal words say. So KW(123) and KF are not K_s at those counts, and the "seen" G_K +1.97pp /
  R2_int K0 +0.0576 inform P1 / P4 only as a different fit. Fix: bracket "G_KW(123) is not G_K; no KW-vs-K_s difference is read".
- **D-2 LOW (GS-R8).** default_rng(20261006) is a pre-data constant not in the registration; resampling 5 seeds with replacement
  understates the seed variance by (n−1)/n = 0.8 (SE × 0.894 on the seed part). On the registered numbers the total SE moves from
  0.6194 to √(0.3588 + 0.8·0.0249) = 0.6154pp (−0.6%): immaterial. Fix: bracket the stream and the factor; no code change.
- **D-3 LOW (TC − KW; CONSTRUCTION-ARMS shape lesson).** TC is a multiway best-first cut whose realised count can exceed the
  allocation; KW is a binary Ward cut at exactly the allocation. TC − KW at 25/50/100 compares different shapes and possibly different
  counts (the realised counts are printed); filing also differs (TC flatLeaf with cross-source filings; KW mirrored by true source,
  UNION-AF-ROUTE D-4). At 123 the counts match. Fix: post-run words "shape- and count-confounded, filing-asymmetric; not a tree-vs-k-means
  quality comparison"; P6 scored as registered.
- **D-4 LOW (SCALE-AGREE D-1 analogue: not null-centred in k).** With no within-source structure, EVAL G(k) falls with k by
  estimation noise (argmax of noisier cell estimates), so D_hi > 0 is expected under the null and D_lo < 0 is expected under the null.
  GS1's joint clause is therefore conservative under the full null (the null fixture reads NOT-SHOWN), but a D_hi lower bound > 0 on its
  own must never be read as "400 cells are over-split by granularity". The registered ESTIMATION-NOISE DISCLOSURE covers it; the
  post-run review applies it to D_hi explicitly. No code change.
- **D-5 LOW (Support transport).** The transported SE 0.599pp is a 6-vs-123-cell contrast; D_hi involves 398-cell policies re-fitted per
  replicate, whose TRAIN-refit variance is likely larger, so the realised SE of D_hi may exceed 0.62pp. The verdict line cannot change
  (already DESCRIPTIVE-ONLY). Fix: C-2.
- Note (not a defect): the real cell build (k-means at 398, Ward, the TC cut on AF-U's trees) first executes inside --run (the dry-run
  fits nothing, by design: no key and no fit). A failure there is a refusal before the TRAIN key, never an outcome.

## Commands (all read-only; zero calls)

```
cd .claude/worktrees/granularity-sweep
git hash-object tools/analysis/granularity_sweep.py; python -c "<sha256 of LF / CRLF renderings; b'\r\n' in data>"
for f in union_route_common union_cells_io union_af_route v2_declared_cells resp_profile_info construction_arms; do git hash-object tools/analysis/$f.py; git rev-parse main:tools/analysis/$f.py; done
git show --name-only --format= d7ab9629 | wc -l; git diff --name-only 9bff7e39 d7ab9629 | wc -l; git status --porcelain | wc -l
python tools/analysis/scratch_dir.py --run -- python tools/analysis/granularity_sweep.py --selftest     # 9 / 9
python tools/analysis/scratch_dir.py --run -- python tools/analysis/granularity_sweep.py --mutants      # 52 / 52, X00 survived
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/gsrev/rev_mut.py                 # R1-R8 8 / 8, R00 survived
python -c "<largest-remainder allocation, caps floor(count/5)>"; python -c "<Support arithmetic (b)-(g), n*>"
grep -n "1.847\|0.599" docs/agents/results/ROUTE-SOURCE-NULL.json; grep -n "spread_K" docs/agents/results/UNION-AF-ROUTE.json
grep -n "def ukm_fit" -A3 tools/analysis/g13_breakdown.py; grep -n "def skm_best" -A10 tools/analysis/construction_arms.py   # D-1
bash E:/TaxoArena_tmp/gsrev/wait_dry.sh   # polls busy.ps1 to rc 1; ls outdir; --dry-run --data-root <main> > dry.log; ls outdir; busy.ps1
```

## Brackets owed (registrar)
1. INSTRUMENT: tools/analysis/granularity_sweep.py blob:1cf20fe8 (LF; crlf16 66012b9f) at branch granularity-sweep d7ab9629 is the
   instrument of L24828-L24840; READY at this review's commit; merge by path.
2. Readings GS-R1, GS-R2 (with D-1), GS-R5 (with D-3), GS-R8 (stream default_rng(20261006), with replacement; D-2), GS-R10 CONFIRMED.
3. D-1 words: KW / KF use skm_best (n_init 5), not K_s's spherical_kmeans (n_init 1); G_KW(123) is not G_K.
4. D-3 words for TC − KW and P6; D-4 words for D_hi (estimation noise, not over-splitting).
5. Post-run duties: C-1 detached launch; C-2 realised DEFF / n_eff / MDE80 of D_lo and D_hi against 1.847 / 3,198 / 1.74 / 1.99pp.

## Delta round 2026-10-06 (tip d7ab9629 unchanged; zero calls)

Delta = none: `git rev-parse HEAD` in the worktree = d7ab962912b1e3ec04acf85e9eac1d647d72c86d, `git status --porcelain | wc -l` = 0,
`git hash-object tools/analysis/granularity_sweep.py` = 1cf20fe8 (the reviewed blob); the six imports equal `main:<path>` at f25b53bc
(per-file `git hash-object` vs `git rev-parse main:`; all six equal). The only open item of the first round was claim 6.

- Claim 6 filled: real --dry-run rc 0 (row 6). The first attempt waited on busy.ps1 rc 0: the busy signal was a Gradle daemon
  (PID 83668, `GradleDaemon 8.10`, no child process, CPU delta 0.016 s over 5 s); it was not killed; the wait loop ran the dry-run at
  16:55 once busy.ps1 returned 1 (the daemon had exited on its own).
- Regression: --selftest re-run 9 / 9 (scratch entries 147 = 147). Mutants not re-run (blob unchanged since the builder's 52 / 52 and
  the reviewer's R1-R8 8 / 8 of the first round; rev_mut.log on E:).
- Support re-derived independently from the registration's (b)-(e): sigma_seed 0.2494, seed term 0.1577, SE 0.6194pp, n_eff 3,198.2,
  MDE80 1.734 / 1.988pp (z 1.96 + 1.2504 = 3.2104), GATE SE 1.046pp, n* 308.35 -> 309; DEFF 1.847 and SE 0.599pp found verbatim in
  docs/agents/results/ROUTE-SOURCE-NULL.json numbers_of_record (measured, two-stage). NON-VACUOUS; DESCRIPTIVE-ONLY reproduces.

VERDICT (delta): READY, no blocker. Conditions C-1..C-3 and brackets owed 1-5 above unchanged.
