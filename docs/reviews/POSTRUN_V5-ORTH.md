# POSTRUN review: V5-ORTH (label-orthogonal variant V5 as a tree and as k-means; EXPLORATORY, WORK only)

Authority: D-2026-10-23-1 (TaxoArena 17b9938b; the author's words "Go for 1 and 2", item 2). Reviewer: adversarial
reviewer, 2026-10-23. Zero LLM calls; vault / reserved reads 0 in my own loads; at most 8 worker processes of mine at a time (MMLU-Pro
8 + 1 idle parent; MMLU 7 + 1; mutants 3), BLAS 1 thread each.
Reviewed: benchzoom branch `v5-orth` (local only: 0 remote branches contain 0b96acc), 516c6ba..0b96acc, merge-base =
master 516c6ba. Builds at a6c3089 (runner LF blob `7c361a25`); the three parts and `--analyze` at 1c9d097 (runner LF blob
`594683d0`, `dirty` ""). Tip LF blobs: runner `8c46d776`, plan `f559c149` (pre-run plan 3781490: `5594e4e5`), test
`597ea9b6`. The working tree has 0 CR bytes in all 3 files and `git hash-object` equals the tip blob, so no CRLF rendering
differs. Outputs `E:/benchzoom_demo/followups/v5-orth`: summary.txt sha256 d17ba400…, SHA256SUMS 10/10 OK and
_work/SHA256SUMS 6/6 OK, checked before and after my runs.

## Verdict

**OUTCOME CONFIRMED (exploratory). The word stands: "centring helps" KILLED. MERGEABLE: 3 new files, src untouched,
plan insertion-only.**
- Every deciding number reproduces to the printed digit (table, rows 5-8). My own harness loop, built from
  `granularity_work` / `meter` primitives on partitions I computed myself, gives every per-item C1 array of V0, V5T,
  KM0-4 and V5K0-4 with max |diff| 0.0 on MMLU and MMLU-Pro. My own cluster-robust SE, MC term and rule code give the same
  four legs.
- The word is robust: the largest leg is z = +0.35. No SE convention brings any leg near 1 SE.
- Conditions on use, not on the merge: D1 and D2 (what the KILLED covers), D3 (power depends on the SE convention).

## Per-claim table (deciding claims)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 3781490 committed before any statistic on responses | Committer date = author date on all 7 commits; reflog shows 7 commits and no amend or reset. Plan 18:20:01, before the earliest V5 pickle (math_V5T, 18:21:52; the six end 18:21:52-18:34:58). Parts: math.npz 19:19:03 minus 402 s wall = 19:12:21, after the run commit 1c9d097 (19:12:08); launch_parts.sh is 19:12:17. Before 19:12:10, `find` over E:/benchzoom_demo and E:/TaxoArena_tmp/v5_orth for npz / summary / arms / part files gives 662 hits: 112 pytest, 550 selftest or mutant sandboxes, **0 other**. check*.log print only n / models / clusters / cell sizes. Plan diff 3781490..0b96acc: 0 deleted lines. Runner diff 1c9d097..0b96acc: +8 lines inside the module docstring, 0 deleted | CONFIRMED | - |
| 2 | Branch touches only its own files | `git diff --name-only master...v5-orth \| wc -l` = 3 (plan, runner, test), 2,288 insertions; 0 files under src; worktree `status --porcelain` 0 lines | CONFIRMED | - |
| 3 | Centring uses only labels and text, with the declared small-cell (EB shrinkage) rule | I re-implemented the rule from plan §2 alone, with inputs X512, anchor and fine label only. My X5 equals the builder's `centre()` output to max 5.6e-17 on all 3 datasets, and the builder's X5 sha256 equals the V5T pickle's `x_sha256` on all 3. My X5 gives bit-identical V5K0-4 partitions (MMLU, MMLU-Pro). Weights min / median / max: MATH 0.328 / 0.641 / 0.841 (smallest cell NT\|Level 1, n = 30, w 0.33); MMLU 0.634 / 0.951 / 0.998 (2 single-cell anchors unshifted, 343 rows bit-identical); MMLU-Pro 0.599 / 0.915 / 0.994 (smallest stemez-OrganicChemistry, n = 17, w 0.60). Between-cell share 0.0175 -> 0.0028, 0.0903 -> 0.0017, 0.0895 -> 0.0013. Builder's own mutants X63-X67 plus my R4, R6 and R8 are all killed by the selftest | CONFIRMED | - |
| 4 | V5 leaves cut across the fine labels; anchored | Own leaf walk: V5T depth-1 = V0's anchors; every leaf lies in one anchor; 88 / 81 leaves (V0 100 / 80). Own cAMI (sklearn exact EMI, LABEL-ALIGN's pooled form, WORK 8,428 / 7,197): MMLU V0 0.3963, V5T 0.0585, V5K (seed mean) 0.0849; MMLU-Pro 0.3207 / 0.0403 / 0.0567. All equal the builder's. MATH cAMI not recomputed (control) | PARTLY: alignment is cut by 0.28-0.37 but not removed. 3 of 6 V5 values are >= 0.05 (MATH values are the builder's; P1 and P2 FAILED) | MED (D1) |
| 5 | Reproduction: V0 / KM / N = FLAT-COMPARE (9/9), per-item 0.0 on 16 arrays; V0R = V0 | Direct npz-vs-npz: 16 common per-item arrays on each dataset, max \|diff\| 0.0, clusters equal. My V0R leaf partition = V0 (MMLU, MMLU-Pro). My V0 cAMI = LABEL-ALIGN 0.3963 / 0.3207 | CONFIRMED | - |
| 6 | C1 readouts (6 arms x 3 datasets) | My stat code on the per-item arrays gives every C1 and SE of the table in [P1] exactly, e.g. MMLU V5T +0.0350 (0.0147), V5K +0.0290 (0.0112); MMLU-Pro V5T -0.0028 (0.0120), V5K +0.0032 (0.0112); MATH V5T +0.1655 (0.0395) | CONFIRMED | - |
| 7 | The four deciding legs (D, paired SE) | MMLU tree -0.0086 (0.0176), km -0.0231 (0.0139 items, MC 0.0054 -> 0.0149). MMLU-Pro tree +0.0067 (0.0192), km +0.0010 (0.0127, MC 0.0041 -> 0.0134). From my own harness and stat code | CONFIRMED | - |
| 8 | Rule word "centring helps" KILLED (plan §8) | `orth_rule` matches §8 as written (strict D > SE; MMLU and MMLU-Pro only; NaN refuses). z -0.49 / -1.55 / +0.35 / +0.08: no leg helps. V0-leaf SEs: z -0.36 / -1.01 / +0.32 / +0.07, KILLED as well | CONFIRMED | - |
| 9 | Power at Delta* = 0.030: 0.76 (UNDERPOWERED) / 0.84 / 0.71 (UNDERPOWERED) / 0.89 | Phi(0.030/SE - 1) = 0.761 / 0.844 / 0.712 / 0.893; MDE80 = 1.8416 x SE = 0.0323 / 0.0275 / 0.0354 / 0.0246. One-sided 95% upper bounds: +0.0203 / +0.0015 / **+0.0383** / +0.0230. Under the V0-leaf SEs: power 0.609 / 0.625 / 0.670 / 0.869, MDE80 0.0433 / 0.0419 / 0.0384 / 0.0261 | CONFIRMED as printed; every leg powered: NO | MED (D3) |
| 10 | Support (plan §10): DEFF source, planning SE / MDE / power arithmetic | Planning rows re-derived: 1.8416 x 0.015 = 0.0276; Phi(1) = 0.841; SE 0.021 -> 0.666; 0.018 -> 0.748; 0.020 -> 0.691; break-even SE 0.030/1.8416 = 0.0163; MATH 0.036 / 0.050 / 0.029 -> 0.434 / 0.345 / 0.514; false-fire 1 - 0.841^4 = 0.500, 1 - 0.841^2 = 0.293. DEFF re-measured from the cache's own content clusters (8,375 / 7,085 clusters for 8,425 / 7,197 items): tree / km legs 1.011 / 1.004 (MMLU), 1.033 / 1.022 (MMLU-Pro); n_eff 8,335 / 8,393 / 6,970 / 7,044. V0-leaf DEFF 1.81 / 2.53 / 1.21 / 1.16 | CONFIRMED | - |
| 11 | Descriptive: N5 - N; MATH control; P1-P5 all FAILED | N5 - N: MATH -0.0548 (0.0187, z -2.93), MMLU -0.0389 (0.0128, z -3.04), MMLU-Pro -0.0015 (0.0259). MATH tree +0.0562 (0.0245, z 2.29; **z 1.75 under the V0-leaf SE 0.0321**), km -0.0185 (0.0234). P1-P5 FAILED as scored | CONFIRMED (MATH: see D2) | MED (D2) |
| 12 | Vault / reserved reads 0; no writes to data of record; zero LLM calls | My loads: guards [0] (MMLU-Pro), [0, 0] (MMLU); backbone fallbacks 0 / 0. 0 files under E:/benchzoom_cache, mmlu_confirm, flat-compare or label-align modified 18:00-20:30 (builder window). My runs: a listing of 1,482 files is identical before and after (diff 0 lines) | CONFIRMED | - |
| 13 | Selftest 12/12; mutants 70/70; suite 895 passed | My sandboxed selftest: 12 PASS / 0 FAIL by count. Branch tests: 3 passed, 1 deselected (slow). Own mutants: 6/8 killed, the 2 survivors are non-decisive (below). Full suite not re-run: the src diff is 0 files | CONFIRMED | LOW (D4) |
| 14 | Backup 46/46; outputs 10/10 | `sha256sum -c SHA256SUMS_backup`: 46 OK / 0 not OK (manifest sha256 9ec1368a…); outputs 10/10 | CONFIRMED | - |

## Defects (none blocks the word or the merge)

- **D1 MEDIUM: [P1] reading (1) over-reaches.** It says "The label alignment is therefore not what kept the MMLU /
  MMLU-Pro partition gains small". The V5 that was tested is label-REDUCED, not label-orthogonal: residual cAMI is
  0.04-0.085 and 3 of the 6 values are >= 0.05. Below the 1-SE bar the reading is backed only at the k-means legs' power.
  Fix: add a [P2] bracket (insertion only): "for this one-pass, EB-shrunk V5 (residual cAMI 0.04-0.085); established at
  the km legs (Delta* excluded at one-sided 95%: upper bounds +0.0015 / +0.0230); the tree legs are not detected".
- **D2 MEDIUM: the tree legs carry no build-variability term.** V0 and V5T are one greedy build each (MC 0.0000 on both
  tree legs), so every tree SE is conditional on two draws. The MATH control's +0.056 (z 2.29, or 1.75 under the V0-leaf
  SE; one of 6 partition legs; outside the rule) cannot be attributed to centring. Fix: state this in [P2]. If a tree leg
  is ever used, build >= 3 recipe seeds per arm and add their MC term. Never use the MATH tree gain to motivate a V5T
  arm on MATH.
- **D3 LOW: power depends on the SE convention.** "km legs powered" holds under the deciding content-cluster SE
  (DEFF about 1.00-1.03). Under the V0-leaf sensitivity SE (DEFF 1.81 / 2.53 on MMLU), both MMLU legs have power
  0.61 / 0.63. Only MMLU-Pro km stays powered (0.87). MMLU-Pro tree does not exclude Delta* under either SE (upper bound
  +0.0383). Fix: print the leaf-SE power and the one-sided bound beside each leg in [P2].
- **D4 LOW: the selftest does not pin the constants DELTA_STAR and Z80** (own mutants R2 and R3 survive). The printed
  MDE80 and power values are correct: I recomputed them with 0.030 and 0.8416212. Fix: assert both constants against
  plan §8 / §10 in S6.
- **D5 LOW (disclosed by the builder): commit 730f870's message names a docstring paragraph that landed in 0b96acc.**
  Cosmetic; no fix.

## What it licenses / does not

- **Licenses (exploratory, WORK-side, selection):** on these WORK items, centring the 512-d text rows within the declared
  fine cells (one pass, EB-shrunk) does not raise C1 by more than 1 paired SE, for the tree or for matched k-means, on
  MMLU or MMLU-Pro. Delta* = 0.030 is excluded at one-sided 95% on 3 of 4 legs. Centring the kNN reader's 4096-d rows
  lowers its C1 on MATH and MMLU (descriptive). The kNN field N stays the best reader on all three datasets.
- **Does not license:**
  - that label alignment in general does not limit partition gains (D1);
  - that a tree gain from centring is absent (tree legs UNDERPOWERED; D2);
  - the MATH tree gain as a finding (D2);
  - replacing V0, or adding or swapping a V5 arm, in BZ-AXIS-CONFIRM-FRESH. Its arms K / N are frozen at benchzoom 516c6ba
    (D-2026-10-23-1; draft f1060523), V0 stays the tree arm, and any V5 arm would need a new author decision and a
    registration;
  - any vault, reserved or registered number.

## Own mutants (sandbox copies under E:/TaxoArena_tmp/rev_v5orth/mut_20261023_202332; selftest as the killer)

| id | change | result | decisive |
|---|---|---|---|
| R0 | control | passes | - |
| R1 | word reads MMLU only (MMLU-Pro legs dropped) | killed (S6) | yes |
| R2 | DELTA_STAR 0.030 -> 0.020 | SURVIVED | no (power printout only; D4) |
| R3 | Z80 0.8416 -> 1.2816 | SURVIVED | no (MDE80 printout only; D4) |
| R4 | small-cell rule removed (weight from n~, uniform per anchor) | killed (C1) | yes |
| R5 | V5K streams unpaired from KM (s + 1) | killed (S2) | yes |
| R6 | MSB with C d degrees of freedom | killed (C1) | yes |
| R7 | leg helps at D > 0 (no SE bar) | killed (S6) | yes |
| R8 | half shift (w / 2) | killed (C1, C3, S2, S5, S6) | yes |

## Commands (scripts in the session scratchpad; all reads read-only; venv Z:/FAC/TUBerlin/benchzoom/.venv)

```
git -C benchzoom_wt_v5-orth log --format='%h ai=%ai ci=%ci' 516c6ba..0b96acc ; git reflog --date=iso v5-orth
git diff --name-only master...v5-orth | wc -l                      # 3
git diff 3781490 0b96acc -- docs/v5-orth.md | grep -c '^-[^-]'      # 0
git diff 1c9d097 0b96acc -- examples/v5-orth.py | grep '^@@'         # one hunk at L62, docstring
for f in ...; do tr -cd '\r' < $f | wc -c; git hash-object $f; git rev-parse 0b96acc:$f; done
python rev_v5.py mmlu_pro 8 out ; python rev_v5.py mmlu 7 out    # own centring, leaf walk, V5K, cAMI, harness, SEs
python rev_x5.py {math,mmlu,mmlu_pro}                              # X5 bits vs pickle, own stats on npz, leaf SE, bounds
python -c "npz(v5-orth) vs npz(flat-compare): 16 arrays, max|diff| 0.0"   # per dataset
find E:/benchzoom_demo E:/TaxoArena_tmp/v5_orth -newermt '18:00' ! -newermt '19:12:10' (npz|summary*|arms.csv|*part*)   # 662 = 112 pytest + 550 sandbox + 0 other
find data-of-record -printf '%p %s %T@' before/after my runs | diff | wc -l    # 0 (1,482 files)
sha256sum -c SHA256SUMS (10/10), _work/SHA256SUMS (6/6), SHA256SUMS_backup (46/46)
python examples/v5-orth.py --selftest (sandbox; 12 PASS / 0 FAIL); pytest tests/test_v5_orth.py (3 passed, 1 deselected)
python rev_mut.py 3                                                # R0-R8 above
```
