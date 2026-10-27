# READY_G-PEAKS-REGISTRATION: pre-data review of benchzoom `docs/peaks_registration.md`

Reviewed: benchzoom master `73f41a8`, `docs/peaks_registration.md` LF blob `efaa37b9d9ced5d5fdb6fdc999469bc8d843fe0a`
(`git rev-parse 73f41a8:docs/peaks_registration.md`; the working tree hashes the same with core.autocrlf=true, so
there is no CRLF variant to pin). Authority D-2026-10-11-3/-5/-6. Zero LLM calls. No score, response or profile column
was read. The text-only diagnostics below read item text/options, embeddings and atlas `items`/`tree` only. That
is a further look at text, and the run's disclosure (§0) must list it (edit E9).

## Verdict: CHANGES (NOT READY): 1 BLOCKER, 3 HIGH

The registered clump null (§4.4) is degenerate on these data. Its clump sizes come from the cos >= 0.90 components,
and those are tiny: the largest is 7 (MMLU-Pro) or 3 (MATH), and 99% of items are singletons. So the null is the
Gaussian null under another name. Its d1 match check fails for **28 of 30 eligible leaves** (MMLU-Pro 0/19, MATH
2/11) at every registered w. By §4.4 those leaves are EXCLUDED, which leaves the held-out test with no leaves and
N1-C pooled over about zero draws. A null whose clump size AND spread are both fitted matches 29/30 leaves. The
registration becomes READY once edits E1-E8 are inserted, which is a pre-launch change (`[R1]`...; §13 keeps the old
wording) and therefore a new blob. A delta review of that diff is needed, not a full re-review.

## Per-claim table (deciding claims)

| # | claim | my number | status | sev |
|---|---|---|---|---|
| 1 | Library LF blobs at 9a08f54 (8 modules) | all 8 equal at 9a08f54 = HEAD = working tree; `git diff --name-only 9a08f54 HEAD` = 4 files, 0 under src/ | CONFIRMED | - |
| 2 | 6 data-object sha256 (2 atlas, 2 npz, 2 parquet) | all 6 equal to the digit | CONFIRMED | - |
| 3 | Eligible leaves: MATH 11 / 4,626; MMLU-Pro 19 / 10,568 | 11 / 4,626 of 4,914 (13 leaves: 11 Sep, 2 Size); 19 / 10,568 of 11,994 (30 leaves: 20 Sep incl. 1 with n<150, 8 Size, 2 refused_by NaN) | CONFIRMED | - |
| 4 | Models 69 / 23 (QwQ excluded); N4 pairs 9 / 3 | parquet: 73-4 = 69; 30-6 = 24, minus QwQ = 23; round(0.25*69/2) = 9, round(0.25*23/2) = 3 | CONFIRMED | - |
| 5 | §4.4 C-null "preserves near-duplicates and templates" and is matchable (±15% on d1, d10) | cos>=0.90 components: MMLU-Pro max 7, 870/11,836 rows in a component of size > 1; MATH max 3, 146/4,914. Null/real d1 ratio at the registered w grid: MMLU-Pro 1.16-2.10 (leaf 34: 4.2-27), MATH 1.12-1.39. Matched: **2/30** (MATH leaves 12 and 16). w changes nothing because the clumps are singletons | REFUTED: the null is degenerate and the exclusion rule takes nearly every leaf | **BLOCKER** |
| 6 | A fitted Neyman-Scott clump null is feasible | size in {2,3,5,10,15} x the registered w grid, fitted to d1 and d10: **29/30** within ±15%. The fail is MMLU-Pro leaf 34 (n=265, 126 exact-duplicate pairs, d1 ratio 3.27) | CONFIRMED as a fix (one draw per cell, seed 99, descriptive) | - |
| 7 | §7.5 verdict rule has 5 reachable words | Rule 1 (support floor: "< 2 leaves pocketed in >= 3/5 folds") fires before rule 2 when there are zero pockets. **NO POCKETS is unreachable**, and P1 would be scored against the wrong word | REFUTED | HIGH |
| 8 | N1-C is certified after the §4.6 exclusions | Exclusion (>= 5/20) and certification use the same 20 draws. If a leaf's true rate is r, the expected observed rate among kept leaves is 0.092 / 0.124 / 0.145 at r = 0.10 / 0.15 / 0.20, and P(kept) is 0.96 / 0.83 / 0.63. The bar partly certifies its own exclusion, and with every leaf excluded N1 is pooled over 0 draws (no rule given) | PARTLY vacuous | HIGH |
| 9 | Templates are kept out of the held-out side (§7.1 groups, cos >= 0.95) | The clump null and §9 use cos >= 0.90. Pairs at 0.90-0.95 (MMLU-Pro 870-535 = 335 rows in a size>1 component at 0.90 but not at 0.95) can straddle folds, so a near-twin's model-specific outcome is carried by the k-NN weight. That is a template false gain that the random-pocket null does not reproduce. At 0.90 the largest component is 7, so grouping at 0.90 is feasible | PARTLY | HIGH |
| 10 | §12.1 support: SE 0.0007, MDE about 0.002 nats, about tau 0.2 | The arithmetic reproduces: SE = 0.1*sqrt(2/46,000) = 0.000659, MDE = 2.8 SE = 0.00185; gain(0.3) = 0.00531, gain(0.2) = 0.00156; the undiluted tau at the MDE is 0.211. But (a) DEFF 2 and SD 0.1 have **no source**. (b) Delta averages over ALL pairs in pocketed leaves, so the gain is diluted by the pocket share: tau at the MDE is 0.48 / 0.37 / 0.32 at share 0.1 / 0.2 / 0.3. (c) The support floor of 2,000 PAIRS gives SE 0.0032 and MDE 0.0089, 4.8 x the stated MDE | PARTLY | MEDIUM |
| 11 | §7.4 random-pocket q95 is a binding second condition | Random same-size subsets give k-NN weights of about the base rate, so their increments mostly shrink or gate to 0, and q95 sits near 0 when the gate stays closed in >= 95% of draws. What it does control is the gain from undoing leaf-level shrinkage, which is real because the children tile the leaf. It does NOT test whether the gain is specific to density: any compact text region could give it | PARTLY (needs a count check) | MEDIUM |
| 12 | Leakage (text/Y split, LOMO b, fold discovery) | crossfit masks every held-out answer (crossfit.py L158, L198); held-out b comes from the other models only (L171); discovery is on training text; the §10 flip selftest is well posed. The N4 mirrored pairs keep b free of the plant | CONFIRMED | - |
| 13 | Thresholds fixed (2 SE, q95, N1 0.10/0.15, N3 0.05/0.15, N2/N4 0.80, stability 63/90 + 4/10 per cell, bulk 50%) | Wilson: N1 passes at <= 22/220 (upper 0.147) and <= 38/380 (0.134); N3 at <= 3/64 (0.129). N2/N4 have point bars only: 26/32 has Wilson lower 0.647, 88/110 has 0.716 | CONFIRMED fixed; N4 bar soft | LOW |
| 14 | Multiplicity | One registered test per dataset, two datasets with separate words: acceptable. Per-leaf existence has no per-leaf error rate: at an N1 rate of 0.10, about 1.9 of 19 MMLU-Pro leaves are expected to be falsely pocketed, against P2's ">= 3 leaves" | PARTLY | MEDIUM |

## Defects and exact edits (insert as [R1]-[R9]; keep the replaced text in §13)

- **E1 (BLOCKER, 4.4)**: replace the clump-size rule. The new rule: "Each null is a Neyman-Scott process with
  clumps of size s and spread w, where (s, w) in {2,3,5,10,15} x {0.01,0.02,0.05,0.1,0.2,0.3,0.5} minimises
  |log d1 ratio| + |log d10 ratio| over 3 pilot draws (seed stream 20261017). The leaf's template families
  (cos >= 0.90 components of size > 1, including exact duplicates, which share one embedding row) are planted
  in addition, each as its own clump at spread w_t = the median within-component squared distance / trace(Sigma).
  s never exceeds 15 (< mcs = 25), so a background clump cannot be a pocket by itself." Keep the ±15% match check and
  the per-leaf exclusion. Add a count rule: **if more than 1/3 of a dataset's eligible leaves are "clump null
  unmatched", the dataset is NOT INTERPRETABLE (calibration)**. Print s, w, both ratios and the number of planted
  template clumps per leaf.
- **E2 (HIGH, 7.5)**: reorder to 1 = N1/N3 fail -> NOT INTERPRETABLE (calibration); 2 = no leaf pocketed in any fold ->
  NO POCKETS; 3 = support floor fails -> NOT INTERPRETABLE (support); then PREDICT / HURT / NO GAIN. The two
  NOT INTERPRETABLE words carry their reason in brackets. The selftest asserts each of the 6 branches on a fixture.
  N3/N4 sims apply rules 2, 3 and the Delta conditions only (rule 1 is circular there).
- **E3 (HIGH, 4.6/6)**: certification must not reuse the draws that selected the leaves. Add "N1 (all three families)
  is computed on 20 FRESH draws per non-excluded leaf (stream `[20261018, ds, leaf, family, draw]`). The selection
  draws are printed beside it." Apply the per-leaf >= 5/20 exclusion to G and E as well as C, so that one leaf firing
  20/20 cannot be diluted in the pool. With 0 certification draws, N1 = FAIL.
- **E4 (HIGH, 7.1)**: set the deciding `groups` to cos >= 0.90 components ∪ doc_hash, the same threshold as §4.4 and
  §9. Print the 0.95-grouped and the ungrouped reads beside it, non-deciding.
- **E5 (MEDIUM, 12.1)**: add the DEFF source ("assumed; TaxoArena query-support median 2.0, memory
  query-support-design-effect"), or derive the SD and DEFF from the stage-2 N3 sims, which are pocket-free and allowed
  to read Y, and pin them before stage 3. State the denominator: Delta averages over all pairs in pocketed leaves, and
  the MDE in tau is about 0.37 at a pocket share of 0.2. Raise the support floor to "realised MDE <= 0.005 nats", or to
  ">= 10,000 pairs on items with max_{c≠other} w >= 0.5". Print the realised DEFF (from the cluster sizes of the
  groups), n_eff, SE and MDE beside Delta.
- **E6 (MEDIUM, 7.4)**: print the share of the 200 random draws whose pocket gate opened, per fold. If that share is
  below 5%, label q95 "non-binding" in the tables. Add a **random-ball null**, printed and non-deciding: same sizes,
  members = the nearest training items (PCA-30) of a random training centre, disjoint, 200 draws, q95_ball. A
  POCKETS PREDICT with Delta <= q95_ball is reported as "POCKETS PREDICT (not density-specific)", and the blog line
  must carry that qualifier.
- **E7 (MEDIUM, 9/12.2)**: per dataset, print "expected falsely pocketed leaves = N1-C rate x leaves tested" beside
  the pocketed-leaf count. P2 is scored HELD only if the count exceeds that expectation by 2 or more.
- **E8 (LOW)**: (a) an N4 lower bar of Wilson lower >= 0.65, or 64 sims; (b) state the embedding join: key =
  sha256(name\0format_item(text, options)), with options decoded from JSON for MMLU-Pro and question-only for MATH
  (as in the demos); atlas ids are "h:" + sha256(parquet id)[:16]; MATH has no `src`/`doc_hash`, so the stage-1
  projection is per dataset; (c) print the reference-pocket counts at ms 30, mcs x2 and raw-4096, descriptive. These
  are the settings review C9 showed kill peaks, and they are outside the grid; (d) the "flip another fold" non-vacuity
  fixture must have an open pocket gate; (e) a parity selftest: the d^(k) of hard-labelled training children equals
  `fit_offsets(centre_models=True, gate_alpha=0.05)` on a tree augmented with those children, separate tau included.
- **E9 (LOW, §0)**: disclose this review's text-only diagnostics: cos >= 0.90/0.95 component sizes, and per-leaf
  d1/d10 ratios. No pocket was computed and no score was read.

Mutants: none. No code exists. The §10 mutant table must add "E2 order reverted" and "fresh N1 draws replaced by the
selection draws".

## Commands
```
cd Z:/FAC/TUBerlin/benchzoom
git rev-parse 73f41a8:docs/peaks_registration.md; git hash-object docs/peaks_registration.md      # efaa37b9 both
for f in crossfit profile irt tree atlas gates embed data; do git rev-parse 9a08f54:src/benchzoom/$f.py; git hash-object src/benchzoom/$f.py; done
git diff --name-only 9a08f54 HEAD | wc -l    # 4, none under src/ (count, not a truncated view)
sha256sum E:/benchzoom_demo/{math,mmlu_pro}_v4/atlas.json E:/benchzoom_cache/emb/*qwen3*.npz E:/benchzoom_cache/{eee/math_mc,hf/mmlu_pro}_scores.parquet
python: pd.read_csv(tree.csv, usecols=[node,parent,n,kind,n_children,leaf,gate_refused_by]); leaves n_children==0; Sep & n>=150
python: pyarrow read_schema (names only) for the model counts
python: cos>=thr components over all unit rows (scipy connected_components), thr 0.90 / 0.95
E:/TaxoArena_tmp/peaks_prereg_review/cnull.py  <ds> <emb>   # registered C-null: per-leaf clump sizes, d1/d10 ratios at w grid
E:/TaxoArena_tmp/peaks_prereg_review/cnull2.py <ds> <emb>   # fitted (size, w) Neyman-Scott: 29/30 matched
python: Wilson bars; selection bias E[rate|kept] (binomial, 20 draws, keep <= 4); §12.1 gain/SE/MDE and tau at MDE by share
```
The atlas was read by a top-level raw_decode that keeps only `items` and `tree`. No other key was inspected or printed.
