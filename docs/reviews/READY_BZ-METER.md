# Pre-data review: BZ-METER registration (benchzoom `docs/meter_registration.md`)

Reviewer: adversarial-reviewer, 2026-10-11. Zero LLM calls. No vault response read: every rerun below goes through
`common.work_mask`; the vault files and both v2 atlases have the same sha256 before and after (`sha256sum -c`: 4 OK).
Object: benchzoom `06f1307`, `docs/meter_registration.md`, LF blob `600933920ba821c72225c4c6e5b564981f1cfc7a`.
`git hash-object --no-filters` gives the same value, so the working tree has no CRLF rendering.
The commit touches 1 file (`git show 06f1307 --name-only --format=` gives 1 line). Authority: D-2026-10-11-9.

## Verdict: CHANGES (NOT READY to launch)

The Support numbers reproduce to the digit (I re-ran the chain on WORK and computed the SE myself), and so do the
vault pins and the near-duplicate drop. One deciding contrast is decided by its estimator, not by the data. The moment
tau^2 clips to 0 on MMLU-Pro, so `G(L3k | C)` is fixed in advance as "NOT SUPPORTED". When I fix tau^2 > 0, the same
WORK cross-fit gives a positive held-out gain at z 4.3-5.4. So P5's MMLU-Pro reading ("src absorbs the text
neighbourhood") is an artefact of the clip. Also, the verdict words can overlap. Apply E1-E3 as `[R<n>]` insertions,
re-cut P4/P5 and the Section 6 rows from a WORK re-run, then send the file to a delta review.

## Per-claim table (WORK side, x1e-3 nats per model x item cell; SE over items; vault SE = SE x sqrt(n_W/n_V))

| # | Claim (registration) | Claimed | Reviewer | Status | Sev |
|---|---|---|---|---|---|
| 1 | Slope L0 vs L0r: MATH69 / MMLU-Pro | +4.251 (.278) / +8.643 (.379) | +4.251 (.2780) / +8.643 (.3786) | CONFIRMED | - |
| 2 | L1 vs L0 | +0.973 (.077) / +1.826 (.162) | +0.973 (.0775) / +1.826 (.1624) | CONFIRMED | - |
| 3 | L2 vs L1 | +0.629 (.063) / +1.023 (.109) | +0.629 (.0629) / +1.023 (.1086) | CONFIRMED | - |
| 4 | Deciding L3k vs C, MATH69 / MATH22 | +0.203 (.018) / +0.617 (.057) | +0.203 (.0183) / +0.617 (.0571) | CONFIRMED | - |
| 5 | Vault SE factors, MDE80 = 3.84 x vault SE | x1.227 / x1.244; MATH L3k-C .022, MDE .09 | sqrt(2949/1960)=1.2266, sqrt(7197/4654)=1.2435; .0225 -> MDE .086; every row of the Section 6 table reproduces | CONFIRMED | - |
| 6 | DEFF 0.72-2.30, source = this WORK cache | yes | (clustered/cell-iid)^2 from the JSON: 0.72 (MATH22 L2a) to 2.30 (MMLU-Pro C-L2) | CONFIRMED | - |
| 7 | MMLU-Pro L3k vs C = 0 (tau = 0); P5 "src absorbs text" | 0.000, NOT SUPPORTED | with tau^2 fixed at .0025 / .005 / .01: **+0.030 (.0056) / +0.056 (.0111) / +0.092 (.0216)**; L3k0 vs L2 +0.033 / +0.062 / +0.103. Raw moment per fold -0.012..+0.009 (in-sample residuals of a parent that already fits the 91 src cells) | REFUTED (estimator artefact) | BLOCKER |
| 8 | L3t vs L2 = 0 on both (P4) | tau = 0 | with leaf tau^2 fixed at .005: MATH **+0.030 (.0095)**, MMLU-Pro -0.030 (.0127); raw moment negative in all 5 folds on both datasets | PARTLY: right on MMLU-Pro; on MATH the clip hides a z 3.2 gain that is below delta_min | HIGH |
| 9 | Near-dups of WORK at cos >= .98: MATH 5/1,965, MMLU-Pro 143/4,797; dropped-id sha 8b578b27 / 4cd9a0a8 | as stated | my own count from the embeddings: 9/5/1 and 210/143/95 at .95/.98/.995; same shas | CONFIRMED | - |
| 10 | Vault-only twins kept, MMLU-Pro 60 | 60 | 60 have a vault twin, but 2 of them also have a WORK twin and are dropped, so **58 are kept** | PARTLY | LOW |
| 11 | Vault file / id-list shas | 31c111e3 / 4bcd0baf; 5e66112a / 5c05640d | identical (recomputed from the sorted ids) | CONFIRMED | - |
| 12 | Frozen MATH 22-model list = WORK acc < .95; MMLU-Pro has no subset | 22; all 23 below | 22, same names as the JSON; MMLU-Pro max WORK acc .564 | CONFIRMED | - |
| 13 | Multiplicity (levels x 2 datasets) | not stated | 10 deciding tests (slope + L1, L2, L3t, L3k, on 2 datasets). One-sided 3 SE gives p = .00135 per test, Bonferroni FWER <= .0135 | OK in substance, UNSTATED | MEDIUM |
| 14 | Verdict words are exclusive | implied | SUPPORTED (g >= 3SE, g > q95) and NOT SUPPORTED (g + 2SE < .10) both hold when 3SE <= g < .10 - 2SE, possible whenever SE < .02 (e.g. row 7 at tau .0025, vault SE ~.007) | REFUTED | HIGH |
| 15 | Support row MMLU-Pro "L3t\|L1 = 0.000 (tau = 0)" | 0 on both | MMLU-Pro -0.000 with SE .011 (tau > 0, not degenerate) | PARTLY | LOW |

R1-R10 mapping. CONFIRMED: R2, R3 (one backbone, named), R4 (Support reproduces; n_eff not printed, E11), R6, R7
(wording; E10), R8 and R10 (out of scope by design), R9 (list frozen and printed). PARTLY: R1 (the matched control is
registered, but on MMLU-Pro it decides nothing while the clip holds; E1), R5 (renamed; 2PL/3PL are descriptive with no
trigger back to the author; E8).

## Defects and fixes (exact edits as `[R<n>]` insertions; the replaced wording goes to Section 12)

- **E1 BLOCKER (vacuity; C-7 risk).** Section 2, "one moment tau^2 per reader ... clipped at 0": the tau^2 is estimated
  from in-sample training residuals, which pushes it to 0 exactly where the parent is rich (row 7). Replace it with:
  "tau^2 per reader is chosen on WORK by inner 5-fold cross-fit from the grid {0, .0025, .005, .01, .02, .04}
  (S-TAU's rule), frozen in `meta.json` before the vault opens, and re-selected inside every null permutation by the
  same rule". S-TAU becomes the deciding estimator. The moment estimator stays as a descriptive line (S-MOM). Re-run
  the Support run with this rule and replace the Section 6 rows for L3t-L2, L3k-C and L3k0-L2 on both datasets.
  Re-cut P4 and P5 from those rows.
- **E2 HIGH (non-exclusive words).** Section 5, replace the three bullets with this list, in precedence order:
  "(1) DEGENERATE: tau^2 = 0 selected on WORK (not scored on the vault; never written NOT SUPPORTED);
  (2) NOT SUPPORTED: g <= q95, or g + 2SE < delta_min;
  (3) SUPPORTED: g >= 3SE AND g > q95 AND g >= delta_min;
  (4) BELOW INTEREST: g >= 3SE AND g > q95 AND g < delta_min (a detected gain smaller than the gain of interest;
  it does not extend depth);
  (5) INCONCLUSIVE: otherwise. The first word that applies is the verdict."
- **E3 HIGH (impossible falsifier).** Section 9: the falsifier "P5 MMLU-Pro SUPPORTED contradicts ..." cannot be
  reached at any budget while tau = 0. After E1 it becomes reachable. Replace "(tau = 0 on WORK: declared src absorbs
  the text neighbourhood)" with the re-cut WORK figure and its range. Delete the sentence "src absorbs text" unless
  the re-cut supports it.
- **E4 MEDIUM (depth rule).** Section 5, combined words: add "L3t and L3k are sibling readers at L3. Each has parents
  L2 and L1 only (L3k is read through C). A non-SUPPORTED L3t does not block L3k."
- **E5 MEDIUM (multiplicity).** Section 5: add "Family = the 10 deciding tests (slope; L1|L0, L2|L1, L3t|L2,
  L3k|C on each dataset). A one-sided 3 SE threshold gives FWER <= .0135 by Bonferroni. Every other line (MATH
  22-model, the 'over L1' lines, L2a, cumulative L2|L0, the S-lines) is SECONDARY: its word carries 'secondary' and it
  never sets the depth." In P6, mark the 22-model verdicts as secondary.
- **E6 MEDIUM (null count checks).** Section 4.1: the runner prints, per level, the count of the 200 permutations
  whose selected tau^2 = 0 and the q95, and refuses if fewer than 200 permutations were written. For L3k, state that
  the embedding rows are permuted within category over WORK and vault jointly, and that C is held fixed.
- **E7 MEDIUM (harness check).** Section 4.1: the check "|G| < 2 SE" fails when G = SE = 0. Replace it with
  "tau^2 = 0 selected, or |G| <= 2 SE".
- **E8 MEDIUM (R5 trigger).** Section 1: add "If S-2PL, or S-3PL on top of L0, beats L0 by >= 3 vault SE on either
  dataset, the backbone choice returns to the author (descriptive lines do not change the backbone by themselves)."
- **E9 MEDIUM (L2 wording).** Add a descriptive line `L2 | C1` (the finer label over the b+length fields on L1), so
  that the post does not read MATH `level` as information beyond difficulty. In Section 2, state that MMLU-Pro `src`
  carries provenance (stemez / theoremQA / scibench / ori_mmlu) as well as subject. The author already admitted it
  in D-2026-10-11-9; this is wording only.
- **E10 LOW.** Section 7.2 / Section 3: change "60 ... kept" to "58 kept (60 have a vault twin; 2 of them also have a
  WORK twin and are dropped)".
- **E11 LOW.** Section 6: add n_eff = n_scored / DEFF per row. Note that `support_meter.json`'s `vault_mde80_x1e3`
  is 2.8 SE, not the registered 3.84 SE; the registration's figure is the right one for its rule.
- **E12 LOW.** Section 6 descriptive note: MMLU-Pro L3t|L1 = -0.000 with SE .011 (not tau = 0).

No meter code exists yet, so no mutants were run (none apply). The meter code gets the code checks (golden inertness
test with the flag absent, an execution-graph update in the same commit, `meta.json` blob refusal) at its READY.

## Commands (read-only on data; outputs in my scratchpad)

```
git -C benchzoom ls-files -s docs/meter_registration.md; git hash-object --no-filters ...   # 60093392 both
git show 06f1307 --name-only --format=                                                      # 1 file
sha256sum vault/*.json math_v2/atlas.json mmlu_pro_v2/atlas.json > pre; ... ; sha256sum -c pre   # 4 OK after all runs
python: support_meter.json -> g, se, deff, se*sqrt(n_W/n_V), 3.84*vaultSE                    # rows 1-6
sm_rev.py = support_meter.py with a fixed-tau hook on the text field (fk, fk0) and _RAW export;
rev_run.py <ds> <tau|none>: own SE = sd(per-item model-mean diff, ddof 1)/sqrt(n)              # rows 1-4, 7
  python rev_run.py math none; mmlu_pro none / 0.0025 / 0.005 / 0.01 (5 parallel, OMP 4)
sm_rev_leaf.py: leaf group offset with tau^2 fixed at .005, raw moment printed                 # row 8
own twin check: normalised qwen3 vectors, max cos vault->WORK and vault->vault, sorted-id sha   # rows 9-10
vault json: sha256(sorted ids) == stored sha256                                               # row 11
JSON work_acc < .95 vs the names in registration Section 7.3                                  # row 12
```
