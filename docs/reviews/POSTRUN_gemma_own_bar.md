# POSTRUN review: GEMMA-OWN-BAR (ops f375f2aa; run worktree gemma-own-bar-run at e18fe595)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. Registration L23915-L23927 (d50c47d4; R1 e1e6c81d), with the C3 brackets
of the registrar's record (7a1a8655). READY: docs/reviews/READY_gemma_own_bar.md. Data objects: R/experiment_results/gemma_own_bar
(cal/*, bar_g.json, g_af/seed_42), R/experiment_results/gemma_own_bar/ops_20261003/*.log, and for comparison S1's intent-s1-run
m_af and m_af_g headless logs. All were read read-only.

## VERDICT

**VALID.** **F-GO FIRES on its leaf clause** (L = 1 ≤ 10). **GO1 NOT READ**: there is no tree to score. It is neither EQUIVALENT
nor LOSS, and it is not a scored "degenerate tree". P1 MISSED (bar_g 0.043748, band [0.007, 0.020]). P2 MISSED (L 1, band [15, 90]).
P3 and the two Briers are not scoreable. The arithmetic and the TRAIN-only claim reproduce to the last printed digit. The build ran
with the pinned bar. The direction of the result is licensed: the rule's gemma bar is STRICTER than 0.025, not laxer. Its
interpretation is narrower than the coordinator's (W-1 to W-3).

## Per-claim table

| # | claim | result | my number vs claimed | sev |
|---|---|---|---|---|
| 1 | p95_null qwen3_256 = 0.038906, gemma768 = 0.068082 | CONFIRMED | recomputed from replicates.csv (300 + 300, rank 285): 0.03890563353258092 / 0.06808211692958388, bit-equal to status.txt and bar_g.json | - |
| 2 | bar_g = 0.043748 | CONFIRMED | 0.025 × 0.068082117 / 0.038905634 = 0.04374823820345296 (TOML 0.043748). Order-statistic 95% CI of each p95 gives a bar range [0.04325, 0.04401]. Replicate bootstrap (5,000 draws) gives [0.04346, 0.04392]. The bar is far from 0.025 and from P1's band at any of these | - |
| 3 | width-only 0.010885 (descriptive) | CONFIRMED | 0.025 × 0.0029964 / 0.0068819 = 0.010885. The D1 identity reproduces (0.0069, 0.0040; at 512 the bar is 0.01466 vs the record 0.0145) | - |
| 4 | TRAIN-only | CONFIRMED | both legs: n_train 9,826, train_text_set_sha256 6f7f9ace…, the same as the PREFLIGHT re-derivation from the pinned ingest DB; build table 6ce9bdf8 (= S1 manifest); 1,676 GATE rows not read. The fresh export holds 11,502 rows with EVAL 0. The emb working copies equal the pins 9e100e04 / b187b82f. The input sha256s in bar_g.json equal my sha256sum of the six cal files | - |
| 5 | bar fixed before the build; build used it | CONFIRMED | bar_g.json 76f2ed35… written 20:01:10, before the build W-probe at 20:03. diagnostics/config.toml = g_af.toml (blob 650b0439) after CR stripping (cmp equal), with `proposalSeparationBar = 0.043748`. Every root NO-SPLIT line prints bar=0.0437 (log) / 0.04375 (proposals.csv) | - |
| 6 | L = 1: root never split | CONFIRMED | proposals.csv: 15 rows, iterations 1-5, all `min_pair_sep_below_bar` at the root (n 9,826). Separations 0.02116 (emK 2), 0.02874 (emK 3 → routed k 2), 0.02203 (emK 4 → k 2) against bar 0.04375. The engine threw `[ANCHOR-FREE] … root as a single leaf … the vacuous outcome, not a negative result`, and there is no snapshot. The readout refused, and nothing was bypassed | - |
| 7 | not a setup fault | CONFIRMED | '[INTENT] fetched 11502 (9826 TRAIN + 1676 GATE, 0 EVAL)'; all 9,826 embeddings cached; the root's emK=2 separation 0.0212 is the SAME as S1 M-AF-g's root line (0.0212 at bar 0.0250), so the geometry is the same. RankingService SQLITE_CANTOPEN at boot (the ratings directory did not yet exist; runBenchmark false) does not touch construction: LOW, D-1. The pinned DBs re-hash unchanged. The gemma working copy changed (16617c14), which is expected for a working copy | LOW |

## Ruling on the falsifier (registrar's wording)

The registered clauses decide, not the engine's word. The engine's "vacuous, not negative" is a guard against treating a
one-leaf DAG as a partition. It governs whether a tree exists to SCORE. It does not govern a falsifier stated on the construction
outcome. L is observed (proposals.csv: the root was the only site and never split). So:

> "GEMMA-OWN-BAR VALID. G-AF built L = 1 (the root never split in 5 iterations; best root min-pair separation 0.02874 against the
> registered embedder-calibrated bar_g 0.043748 = 0.025 × 0.068082 / 0.038906). F-GO FIRES on its leaf clause (L ≤ 10). GO1 NOT
> READ: the engine refuses a single-leaf anchor-free DAG (no snapshot), so there is no partition to score. GO1 is neither EQUIVALENT
> nor LOSS, and the 'degenerate tree' mark (L < 10) has no score to attach to. P1 MISSED (0.0437 vs [0.007, 0.020]; the embedder-specific
> null p95 is HIGHER for gemma 768 than for qwen3 256, opposite to the width rule's direction). P2 MISSED (1 vs [15, 90]). P3 and the
> Briers not scoreable. Under the registered bar rule, M-AF-g's 4 leaves are NOT attributable to a qwen3-tuned bar that is too strict for gemma:
> the rule's gemma bar is stricter (0.0437 > 0.025). The F-GO sentence holds only in this form: 'the anchor-free recipe does not
> build a gemma 768 MASSIVE tree under this rule's embedder-calibrated bar'. Width-only bar 0.0109 descriptive and untested."

Not licensed: "the recipe does not transfer to gemma at any bar". A laxer bar (0.025) built 4 leaves, and 0.0109 was not run. Also not
licensed: "gemma is worse than qwen3 for intents" (D3 the author's; WILL NOT SHOW). Also not licensed: "a null result on GO1".

## The substantive reading: licensed with three qualifiers

Licensed, in direction: the registered rule makes gemma's bar 1.75× stricter than qwen3's. S1 Q-1's sentence "the AF recipe's bar
(0.025, calibrated at qwen3 256) does not transfer to gemma at 768" needs a bracket. The bar is embedder-dependent, but it does not
stall gemma by being too STRICT. Like for like at routed k = 2 (where the min-pair gate and the persisted k-way statistic are the
same number, TaxonomySplitter L455-L460), the root separations relative to each embedder's own null p95 are:
qwen3 M-AF root 0.039, which is 1.00 × p95 (4.0% of the qwen3 null replicates ≥ 0.039); gemma root best 0.02874, which is 0.42 × p95 and below
all 300 gemma null replicates (min 0.0654). So gemma's root separation is small relative to its own null. qwen3's is at its null's p95.

- **W-1 (the null does not certify either root).** qwen3's real root sits AT its null p95, not above it. Both bars sit below
  every null replicate of their embedder (0.025 < qwen3 min 0.0362; 0.0437 < gemma min 0.0654). The rule therefore transports
  "the same fraction of the moment-matched null" (0.643 × p95). It does not transport "a null-level control". This is the CERT-PC-K2 W-1 pattern
  (real structure below the site-null minimum). Write "relative to its own moment-matched root null", never "below noise" or "no
  structure".
- **W-2 (statistic and k).** The null records the persisted k-way statistic (sepKway), and the bar gates the min-pair statistic. The two are the
  same only at routed k = 2. The arm did not record the routed k per replicate. If gemma's null replicates route to k ≥ 3 at
  0.025 (S1's real gemma root did: k = 3, k-way 0.059, min-pair 0.0287), the gemma p95 is a k-way number above the gated
  statistic, and bar_g is inflated by an unknown factor. The direction (gemma's bar > 0.025) survives unless the inflation exceeds 1.75×.
  Even S1's real gemma k-way root separation (0.059) is 0.87 × its null p95, below the null minimum. Not ruled out; disclose.
- **W-3 (GOB-K1).** Both nulls ran at bar 0.025, which enters k-selection as marginalEps. A null at bar_g was not measured.

## Bearing on E1-SPLIT-DRAWS' N_e1sd1 (nomic, MMLU-Pro, qwen3 bar 0.025)

Not transferable, and the gemma result cuts against the bracket's word "the same bar-tuning mechanism" (L23915 cross-reference).
There, sites stalled at min-pair 0.0095-0.0215 against 0.025. Here the embedder-specific rule made the bar STRICTER for a
non-qwen3 embedder. So "the stall is caused by a qwen3-tuned bar that is too strict for the embedder" is unproven for gemma and
unmeasured for nomic: there is no nomic null, the corpus is different, and the slice is 256. Proposed bracket: "a bar-dependence of the AF recipe on nomic geometry; whether nomic's own
null would lower or raise the bar is unmeasured; GEMMA-OWN-BAR found the embedder-specific bar higher for gemma 768". POSTRUN
e1_split_draws N1's "coarse tree produced by the recipe's separation bar 0.025" stays true as stated, because it names no direction.

## Defects

- D-1 LOW: RankingService CANTOPEN at boot (ratings directory absent). FIX: the operator creates g_af/seed_42 before bootRun, or the launch plan says so.
- D-2 MEDIUM (instrument, forward): the null arm writes only sepKway. FIX for any re-use: write routed k, emK and the min-pair statistic per
  replicate (Rep already holds reason/emK/sepBinding), and calibrate on the gated statistic.
- D-3 LOW: the READY's D-1 (compute_go world assertion) is moot for this run (GO1 not read). It stays open for re-use.

## Commands

```
python: p95 by rank ceil(0.95n) on cal/null_*/replicates.csv and cal/iso/iso_replicates.csv; bar = 0.025*pg/pq; order-stat CI; bootstrap 5000
sha256sum cal/*/* ; sha256sum bar_g.json            # = bar_g.json input_sha256 ; 76f2ed35…
cmp <(tr -d '\r' < g_af/seed_42/diagnostics/config.toml) <(tr -d '\r' < experiment_configs/gemma_own_bar/g_af.toml)   # equal
cat g_af/seed_42/diagnostics/proposals.csv          # 15 root NO_PROPOSAL rows, iters 1-5, bar 0.04375
grep "Split 'INTENT'\|NO-SPLIT\] 'INTENT'" intent-s1-run/.../{m_af,m_af_g}/seed_42/headless_run.log   # qwen3 k=2 0.039; gemma 0.0212 / k=3 0.059
grep -n "ANCHOR-FREE\|CANTOPEN\|INTENT\] fetched" ops_20261003/build_g_af.log
python: fraction of the qwen3 null >= 0.039 (0.040); gemma null min 0.0654
```
