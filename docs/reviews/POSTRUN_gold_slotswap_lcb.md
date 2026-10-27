# POSTRUN review: MMLU-GOLD-GEOMETRY, INTENT-S0-SLOTSWAP-MECH, LCB-STAGE0-POWER-RESIM

Adversarial reviewer, 2026-10-01, zero calls, read-only (every DB opened `mode=ro&immutable=1` or through the reviewed
read-only openers; intent_emb_* size/mtime unchanged before/after; `git status --porcelain` on the three result dirs and
on tools/analysis: 0 lines before and after). Reviewed at HEAD 174b4abf. Registrations: prog "## Registered 2026-10-01 ...
MMLU-GOLD-GEOMETRY" (L22332-L22357), "## Registered 2026-10-01 ... INTENT-S0-SLOTSWAP-MECH" (L22301-L22330),
"## Registered 2026-09-30 ... LCB-STAGE0-POWER-RESIM" (L22208-L22228), with their brackets through L22404.

## Verdicts

| run | commit | verdict |
|---|---|---|
| MMLU-GOLD-GEOMETRY | 40d841d7 | **VALID**: G-1 HELD; F-G1 NOT FIRED; under wording conditions W-G1, W-G2 |
| INTENT-S0-SLOTSWAP-MECH | 174b4abf | **VALID**: M1 HELD, M2 HELD; F-SM1, F-SM2 NOT FIRED; M3 descriptive; under W-S1..W-S3 |
| LCB-STAGE0-POWER-RESIM | b880c44 | **VALID**: C0 PASS; C1 FAILED; F1 FIRES; under W-L1, W-L2 |

No BLOCKER and no HIGH finding. Every deciding number was reproduced to the printed digit by an independent script.

## Pins (LF of record; 0 CR in every outcome, so working tree = LF; `git hash-object` = `git rev-parse <commit>:<path>`)

- gold outcome blob:ec65dd67010bc84985e12aecfb931083a5201382; script blob:5ab1c87846e56cdd29da72f557e97ccb00645260 (= READY 97d5f45 pin)
- slotswap outcome blob:dd165e77d37a8ef04d79d5156b210a2826b49ad4; script blob:7821815544e47679f611204d9bbd02a039bd46d4 (= READY pin)
- LCB outcome blob:fdb1637624439bea7a4a03c01b3b2533bbf1953e; script blob:8622ff95661f35214791752b9469088aca090432 (= READY_backfill pin)
- S0 machinery intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271 (unchanged)
- Commit hygiene: 40d841d7 2 files, 174b4abf 3, b880c44 5; files outside experiment_results/: 0 in each (counted with `--name-only | wc -l` / `grep -vc`).

## Per-claim table (deciding claims)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| G1 | member: TRAIN 6,992 items, 2 ambiguous rows, kept 6,988; 91 fine in 14 | 6,992 / 2 / 6,988; 91 / 14 (own join: side TSV + options key on 1 raw file, own item grouping) | CONFIRMED | - |
| G2 | H (qwen3 slice 256) = 0.2912, 14 clusters | 0.2912, 14 (own centroids, own ARI; scipy average-link cosine) | CONFIRMED | - |
| G3 | null p95 0.0264, mean -0.0005, SD 0.0155 (1,000 perms, seed 2105) | 0.0264 / -0.0005 / 0.0155; = READY's POST-RUN check value | CONFIRMED | - |
| G4 | G-1 HELD (H > p95; the point decides) | 0.2912 > 0.0264; margin 0.265 = 6.9 x MDE80 0.0384 | CONFIRMED | - |
| G5 | slice 512 H 0.3130 (descriptive) | 0.3130 | CONFIRMED (spot) | - |
| S1 | S0-C4 reproduced S 0.75978, n 3,222, 3,207 components | S 0.75978; nomic 0.69305; gemma 0.82619 | CONFIRMED | - |
| S2 | per-variant margin, variant-side share, flips (CSV) | own assignment, own top-2 margin (max abs diff 5.0e-7), own share by token arithmetic, not the SB3 replica (max 4.7e-7); flips 0 mismatches x 3 embedders | CONFIRMED | - |
| S3 | quintiles [644,645,644,645,644], terciles [1027,1027,1168] | identical (own tie-block grouping) | CONFIRMED | - |
| S4 | M1 D_Q 0.4689 [0.4253, 0.5123] HELD (lower >= 0.10) | 0.4689 [0.4253, 0.5123] at seed 20261003; own stream seed 7 [0.4249, 0.5154] | CONFIRMED | - |
| S5 | M2 D_T 0.1411 [0.1067, 0.1752] HELD (lower > 0) | 0.1411 [0.1067, 0.1752]; seed 7 [0.1062, 0.1785] | CONFIRMED | - |
| S6 | M3 gemma +0.0664 [+0.0515, +0.0820], nomic -0.0667 [-0.0843, -0.0497] (descriptive) | identical | CONFIRMED | - |
| S7 | Support: DEFF 1.0093, n_eff 3,192; SE M1 0.0227 / M2 0.0197; MDE80 0.0637 / 0.0551 | Kish sum m^2/n = 1.00931 from the CSV's components; SE arithmetic reproduces; bootstrap SE 0.0221 / 0.0176 | CONFIRMED (label defect SS-P1) | LOW |
| L1 | rejections 3 / 24 / 89 / 152 / 264 of 400 at tau 0 / .15 / .20 / .25 / .30; 0 refusals | identical from worlds.jsonl; w = 0..399 complete per tau; reject flag = (p_T <= 0.01) on all 2,000 | CONFIRMED | - |
| L2 | C1 power(0.20) 0.2225, Wilson [0.1845, 0.2658] -> FAILED (upper < 0.80) | own Wilson: [0.1845, 0.2658]; FAIL observable needs <= 304, observed 89 | CONFIRMED | - |
| L3 | C0: identity T 96.689 / p_T 0.0300; size 3 of 400 <= 12 | identity re-run REPRODUCED; design_sha 4891b89c... equal; 58 worlds re-run (40 at tau 0.20, 10 at 0.30, 8 at 0) give identical p_T and reversals | CONFIRMED | - |
| L4 | tau80 > 0.30 (descriptive) | no grid tau has Wilson lower >= 0.80 (max 0.6123 at 0.30) | CONFIRMED | - |

Robustness of the deciding calls (mine; none moves a verdict):
- LCB: 58 tau-0.20 worlds have p_T in (0.005, 0.02]. If every one rejected, 147 of 400 < 304: the FAIL is not
  Monte-Carlo noise. G is drawn `rng.normal(0, tau)` (SD = tau, as registered "N(0, tau) ... logit SD").
- Slotswap M2 versus margin (null preserving the conditioning): with share permuted WITHIN margin quintiles (2,000
  draws), D_T has mean 0.0244 and p97.5 0.0583; observed 0.1411. corr(margin, share) = -0.098. M2 is not carried by margin.
- Slotswap tie rule (SB1): ordinal ranks instead give terciles [1074]x3 and D_T 0.1443, D_Q unchanged: not decisive.

## Own mutants (deciding paths; recomputation level)

- OM-1 slotswap groups average -> ordinal ranks: D_T 0.1411 -> 0.1443, M2 still HELD: SURVIVED, not decisive (SB1 not load-bearing).
- OM-2 LCB Wilson denominator -> non-refused worlds: identical (0 refusals): SURVIVED, not decisive (= READY C-LR-3, test gap stands).
- OM-3 LCB rejection `<=` -> `<` 0.01: p_T is on the grid k/2001, no world at exactly 0.01: SURVIVED, not decisive.
- Builder suites re-run on main: gold --selftest 54 ok, --mutants 37 of 37 KILLED; slotswap --selftest 84 ok, --mutants
  40 of 40 KILLED; lcb --selftest 9 / 9.

## Wording conditions (bind the registrar's outcome sections and any thesis sentence)

- **W-G1.** "The 14 declared MMLU-Pro categories are recovered above chance by average-link on qwen3 fine-source TRAIN
  centroids: ARI H 0.291 (p95 of 1,000 size-matched relabellings 0.026; slice 256; 6,988 TRAIN items, 91 sources)." Never
  "the categories are geometric clusters" without the number: ARI 0.29 is partial recovery, far from 1.
- **W-G2.** The CLINC 0.143 / MASSIVE 0.404 comparison stays DESCRIPTIVE-ONLY (different K, no interval). F-G1 NOT FIRED
  feeds B-A2's reading of G12 in ARCH-V2-E-T-R2 only; G10 FAILED does not touch this result (no RP12 tree read).
- **W-S1.** M1 is an association: variants of low-margin origins flip more (0.551 vs 0.082, lowest vs highest quintile).
  It does not show that slot swaps are a small perturbation, nor that margin gating remedies F4: "selective stability"
  0.8375 over the top 80% is descriptive, carries no interval and is not a registered criterion. F-SM1 NOT FIRED keeps the
  margin-gating reading open; it does not license "remedies".
- **W-S2.** M2: a larger inserted-token share predicts flips, also with margin held fixed (within-quintile null above;
  joint logistic b_share 0.34). Share is confounded with item length; no causal word (registered DOES NOT SHOW).
- **W-S3.** M3 is never written as an embedder ranking or parity: gemma +0.066 and nomic -0.067 against qwen3 are
  outside the seed spread 0.0335 on one k-means seed per embedder (seed 0), RAW protocol; the embedder of record is the author's.
- **W-L1.** The STOP sentence's power clause reads, at the measured design, "power 0.22 [0.18, 0.27] at 0.20 logit SD and
  0.66 [0.61, 0.70] at 0.30; tau80 > 0.30 (measured design, plug-in null, iid interactions on the fixed real regions)".
  G1's FAIL is uninformative about interactions up to at least 0.30 logit SD; "no interaction" is never written.
- **W-L2.** The "fewer than about 2-7 model pairs with a true 10pp reversal" translation is void at the measured design:
  the mean true 10pp-reversal count is 0.00 at tau <= 0.25 and 0.01 at 0.30 (max 1 pair in any world). It must not be
  kept as a separate clause; the closed LCB line stays closed (CONTEXT §5).

## Defects (none changes a verdict)

- **SS-P1 (LOW).** The slotswap outcome prints "Kish mean cluster size 1.0093"; registration Support (a) names the
  mean cluster size 1.0047 (3,222 / 3,207) and the DEFF 1.0093. 1.0093 is S0's `kish()` (sum m^2 / sum m = DEFF at
  ICC 1). Fix: the registrar quotes "DEFF (Kish, ICC 1) 1.0093; mean cluster size 1.0047".
- **SS-P2 (LOW, the registrar's quintile-label defect: CONFIRMED, dry-run only).** `dry_run` passes
  `q_sizes=[len(variants)//5]*5` into `support_lines`, which labels them "realised quintile sizes" ([644]x5, sum 3,220).
  The --run prints the realised [644, 645, 644, 645, 644] (sum 3,222, reproduced above), which is of record; the outcome
  file is unaffected. Fix (next edit of the script): label the dry-run line "nominal (n // 5; margins not computed)".
- **SS-P3 (LOW).** The slotswap run transcript was committed under experiment_results/archv2/rp12/readouts/
  (slotswap_run_run.txt), not beside its outcome. Fix: cite it by that path; do not move it (write-once record).
- **GG-D2 (LOW, still owed from 97d5f45).** The gold outcome prints "EVAL items without src: 0 of 3492" beside the
  census's 13 (another denominator: the 12,000-row mmlu_pro table route). Never quote it as "0 EVAL items without src"
  without the member's denominator. No EVAL vector or label is read; not deciding.
- **LR-P1 (LOW).** Every world runs G1's permutations on the same `C.PERM_SEED` stream, so the Monte-Carlo p-value
  noise is correlated across worlds. The registered "registered stream" requires it; the 58-borderline bound above shows
  it cannot move C1. Disclose only.

## Commands (all read-only; scripts in the session scratchpad, not committed)

```
gold_ind.py   own: side TSV parse, split_side.stem_key, options key on 1 raw sample file, item grouping, centroids,
              own ARI, scipy average-link cosine, null rng default_rng(2105) x 1000
  -> train items 6992 / ambiguous rows 2 / kept 6988; fine 91 coarse 14; slice 256 H 0.2912 (14 clusters);
     slice 512 H 0.3130; null p95 0.0264 mean -0.0005 sd 0.0155
ss_ind.py     S0's load_corpora / c4_variants / km_fit (registered instrument, seed 0); own vector load (immutable),
              own assignment, margin, share, tie-block quantile groups, component bootstrap; within-margin-quintile null
  -> S 0.75978 / 0.69305 / 0.82619; margin, share, 3 flip columns = CSV; q [644,645,644,645,644] t [1027,1027,1168];
     DQ 0.4689 [0.4253, 0.5123]; DT 0.1411 [0.1067, 0.1752]; M3 [0.0515, 0.0820] / [-0.0843, -0.0497];
     M2 null mean 0.0244 p97.5 0.0583; DB size/mtime unchanged
lcb_ind.py    own Wilson + counts from worlds.jsonl; lcb_power_resim.prepare at tag-root lcb-build-2 (3bcc9ab, porcelain 0)
              + 58 worlds re-run through world()
  -> k 3/24/89/152/264; Wilson(89,400) [0.1845, 0.2658]; identity REPRODUCED; design_sha 4891b89c...; 0 of 58 differ;
     EVAL sealed sha 74ea30e5... unchanged
python -c (CSV components) -> 3222 in 3207, Kish 1.00931, mean 1.00468
python tools/analysis/{mmlu_gold_geometry,intent_s0_slotswap_mech,lcb_power_resim}.py --selftest ; --mutants (gold, slotswap)
git show <c> --name-only --format= | wc -l ; | grep -vc '^experiment_results/'   (2/0, 3/0, 5/0)
git hash-object <outcome> = git rev-parse <c>:<outcome> ; tr -cd '\r' | wc -c = 0 for all three outcomes
```
