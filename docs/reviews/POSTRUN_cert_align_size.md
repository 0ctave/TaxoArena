# POST-RUN review — CERT-ALIGN-SIZE

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Registration prog L24245-L24257 (feac5b3d) with the pre-data
brackets of 404d286d (C1-C3; post-run duties C4, C5). READY: `docs/reviews/READY_cert_align_size.md` (blob 820802de).
Run: from main, script `blob:80f7bb788f4feac0538eb1826e3febdfd79fa81d` (`sha256-lf16:a24389e66dc26913`; = `git hash-object` =
`HEAD:` blob; same blob as reviewed), rc 0.
Outcome of record: `E:/TaxoArena_backup_2026-10-04_cert_align_size/cert_align_size_outcome.txt`,
sha256 `86446d9e2ca2abc149035b467b531273ab85db5a3190bc75f87f3bfae1526b72` (`sha256sum -c SHA256SUMS.txt`: OK).

## Verdict

**VALID. CA1 = ALIGNED-BEYOND-SIZE (G +0.0633, p 0.0001; 52 certified / 216 uncertified sites, 16 of 20 strata, 4 dropped).
F-CA NOT FIRED. P1-P4 HELD.** Support line (f), applied as bracketed (C1): SCOREABLE, thin (MDE80 0.0471 vs 0.05).
Mandatory qualifier (C4): size is not matched inside the top quintile. The sign survives every size control I ran, but the
magnitude does not: 0.047 to 0.056 under finer size control, 0.032 (p 0.048) on q0-q3 alone.

## Per-claim table (deciding numbers recomputed independently)

My recompute uses my own child assignment (cosine to vmfMu from `np.frombuffer('>f4')`), my own NMI (contingency
table, arithmetic mean), my own G, permutation and OLS. It reads `snapshots.db`, `mmlu_pro_dataset_cache_v2.db`,
`embeddings_cache.db` (all `mode=ro&immutable=1`) and the 4 site-null CSVs. It imports nothing from the script.

| claim | outcome | mine | state |
|---|---|---|---|
| denominator | 268 / 52 cert / 216 uncert; 16 strata, 4 dropped, sum w 50 | same; 2,861 of 2,861 multi-holder vectors found | CONFIRMED |
| G (size-stratified, w = min) | +0.0633 | +0.06326 | CONFIRMED to the digit |
| permutation p | 0.0001 (10,000, seed 20261004) | 0.00005 (20,000, other RNG); null SD 0.0165 (outcome 0.0166); max null G 0.0600 < 0.0633 | CONFIRMED (p is at the floor in both) |
| raw gap; raw - G | +0.0827; +0.0194 | +0.08268; +0.01942 | CONFIRMED |
| mean Y cert / uncert | 0.2155 / 0.1328 | 0.2155 / 0.1328 | CONFIRMED |
| depth x tree gap | +0.0467 | +0.04666 | CONFIRMED |
| OLS cert (HC1) | +0.0470 (0.0158); log n +0.0384 (0.0136); depth +0.0046 (0.0086) | identical | CONFIRMED |
| CA1 / F-CA | ALIGNED-BEYOND-SIZE / NOT FIRED | G > 0 and p <= 0.05 | CONFIRMED |
| P1 G in [0, 0.12]; Brier | HELD; 0.2025 | 0.0633 in band; (0.55-1)^2 = 0.2025 | CONFIRMED |
| P2 raw-G in [0, 0.10] | HELD 0.0194 | 0.0194 | CONFIRMED |
| P3 20NG G in [0, 0.12] (seen, descriptive) | HELD 0.0736 (p 0.0516) | spot check: P9 loader 0.1215 / 0.0740 REPRODUCED (READY) | CONFIRMED (spot) |
| P4 o0 G in [-0.03, 0.07] (descriptive) | HELD 0.0316 (p 0.0349) | not recomputed (descriptive) | spot: in band as printed |
| T1b | G 0.4496, p 0.0529, 1 certified, 19 distinct permuted values | one site: no content | DESCRIPTIVE, uninformative |

## Write-once, console, hygiene

- Outcome and SHA256SUMS.txt written at 14:39:57 by `open(...,'x')`. The SHA256SUMS line matches the file.
- Console log `E:/TaxoArena_tmp/cas_run.log` is identical to the outcome except for its last line (the "wrote ..." line) and
  CRLF line ends: `head -n -1 | diff -q --strip-trailing-cr`. Count: 56 CR bytes in the log, 0 in the outcome (LF).
- Backup: the outcome is already in `E:/TaxoArena_backup_2026-10-04_cert_align_size/` with the script's SHA256SUMS.txt
  (left untouched). I added `cas_run_console.log` with `SHA256SUMS_console.txt`
  (522866ac33a9fd2cafd478095b01d68d57615b2369d8d33a1c14d8b75e224847). Nothing was committed.
- Size and mtime of the four input DBs are the same as my READY-time reading (before the run). All -wal files are 0 bytes.

## C1: Support line (f), as bracketed

SD of Y 0.0967. Registered estimator: SE_G with per-stratum SDs (a singleton class cell uses the stratum's pooled SD;
5 certified cells are singletons; the bracket leaves this convention open) = 0.0153, x sqrt(1.3) = 0.0174.
Permutation SD 0.0166 x 1.140 = **0.0189 (the larger; of record)**. MDE80 = 2.487 x 0.0189 = **0.0471 < 0.05**:
SCOREABLE, thin (margin 0.003). The single-SD reading (0.2050 x 0.0967 = 0.0198; MDE80 0.0493) gives the same line.
The script's printed SE 0.0170 / MDE 0.0424 is not of record (bracket). G / SE = 0.0633 / 0.0189 = 3.3.

## C4: size inside the top quintile (descriptive; my numbers)

q4 (n 701-8,132) holds 25 of 50 weight. Geometric-mean n: certified 2,163, uncertified 1,103 (1,700 for certified once the
roots are dropped). Among uncertified q4 sites, Y rises 0.039 per unit log n. Expected size bias from that slope:
0.039 x ln(2163/1103) = 0.026 on q4's gap.

| size control | G | p (10,000 within-stratum) |
|---|---|---|
| registered (tree x pooled quintile) | +0.0633 | 0.0001 |
| without the 4 depth-0 roots | +0.0633 | - |
| q4 split at its median n (1,294) | +0.0544 | 0.0006 |
| tree x pooled log-n deciles | +0.0563 | 0.0003 |
| OLS cert, adjusted for log n + depth + tree | +0.0470 (HC1 SE 0.0158) | - |
| q0-q3 only | +0.0319 | 0.0479 |
| q4 only | +0.0946 | - |

The sign agrees everywhere, so "matched size" holds IN SIGN. In MAGNITUDE, about 0.01 to 0.016 of the registered G is
residual size in q4. Half of the effect sits in the largest sites, which are the upper levels of the trees. Leave one tree
out: G 0.058 to 0.067. G per tree: 0.053 / 0.081 / 0.066 / 0.056, positive in 4 of 4. 4 of the 16 strata have a negative gap.

## C5: DEFF

Not measurable at 4 tree clusters. Indicative only: a CR1 SE for the OLS cert coefficient, clustered on 12 depth-1
subtrees (the roots counted as their own clusters), gives DEFF 1.09 (12 clusters, biased low). 1.3 stays a declared
assumption. n_eff = 268 / 1.3 = 206 (certified 40). The p stays below 0.05 until DEFF = (0.0633 / 1.645 / 0.0166)^2 = 5.4.
Nested sites share members, so the within-stratum permutation may be anti-conservative. That margin covers it.

## What it licenses (anchor-free re-draws of MMLU-Pro)

Licensed: on four label-free [LF] anchor-free re-draw trees of ONE corpus (MMLU-Pro TRAIN members, qwen3 R256, one
recipe), splits that pass their own site-null p95 (per site, uncorrected, 300 reps) agree more with the 14 declared
categories than uncertified splits in the same tree and size quintile. G +0.063 NMI, against a mean of 0.133 for
uncertified splits; size-adjusted +0.047 to +0.056. So the per-site certificate is not only a size statistic. On these
trees the geometric separation it tests goes together with declared-category structure. That is consistent with memo
change 10's "false-discovery guard" reading and does not narrow it (F-CA not fired).
NOT licensed: that certified splits are "correct" or category splits (mean NMI 0.2155 is low in absolute terms, and
uncertified splits carry 0.133); FDR-corrected certification (per-site flags only; KNOWLEDGE §1 wording for "certified");
other corpora, embedders or recipes (the 20NG arm is descriptive and seen, p 0.052; four draws of one corpus are not
independent replications); anchored trees ([AN] descriptive); a size-free effect of +0.063 (C4); anything about G12, the
judge or routing. Alignment with declared categories is not the only kind of real structure (registered).

## Registrar's wording (proposed)

"CERT-ALIGN-SIZE (2026-10-04, 0 calls) — VALID; CA1 ALIGNED-BEYOND-SIZE, F-CA not fired. On the four anchor-free MMLU-Pro
re-draw trees [LF] (268 sites, 52 certified at site-null p95, per site, uncorrected, 300 reps), certified splits align
with the declared categories better than uncertified splits in the same tree x size quintile: G +0.0633 NMI
(one-sided within-stratum permutation p 0.0001, 10,000 permutations). Support (f) per the C1 bracket: SE 0.0189, MDE80
0.0471, SCOREABLE, thin. QUALIFIER (C4): size is unmatched inside the top quintile (certified geometric-mean n 2,163 vs
1,103). The sign holds under every size control (log-n-adjusted OLS +0.047, SE 0.0158; deciles +0.056; q4 split +0.054),
the magnitude is about 0.01-0.016 smaller, and q0-q3 alone gives +0.032 (p 0.048). DEFF 1.3 stays an assumption
(unmeasurable at 4 trees; p < 0.05 holds to DEFF 5.4). P1-P4 HELD (Brier 0.2025). Licenses: the per-site certificate
carries declared-category alignment beyond site size ON THESE TREES; not correctness, not FDR certification, not other
corpora or embedders. Outcome E:/TaxoArena_backup_2026-10-04_cert_align_size/cert_align_size_outcome.txt sha256 86446d9e…;
POSTRUN docs/reviews/POSTRUN_cert_align_size.md."

## Defects

- None in the run. LOW (already bracketed): the script's printed Support clause uses the unstratified SE.
- LOW (for the registrar): the C1 per-stratum SE_G formula leaves singleton cells undefined. The permutation SD decides
  here as the larger, so the outcome is unaffected. Record the convention.

## Commands

```
git hash-object tools/analysis/cert_align_size.py ; git rev-parse HEAD:tools/analysis/cert_align_size.py      # 80f7bb78 both
cd E:/TaxoArena_backup_2026-10-04_cert_align_size && sha256sum -c SHA256SUMS.txt                            # OK
head -n -1 E:/TaxoArena_tmp/cas_run.log | diff -q --strip-trailing-cr - <outcome>                           # identical
tr -cd '\r' < <file> | wc -c                                                                                # 56 log / 0 outcome
python E:/TaxoArena_tmp/cas_review/post1.py   # independent per-site Y (268 sites) -> post_sites.json
python E:/TaxoArena_tmp/cas_review/post2.py   # G/raw/depth gap/perm p/OLS HC1+CR1/C1 SE/C4 table/LOTO
stat -c '%n %s %Y' snapshots.db mmlu_pro_dataset_cache_v2.db twenty_newsgroups_cache_v1.db embeddings_cache.db   # unchanged
```
