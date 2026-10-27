# Post-run numbers review: CERT-DIRECTION-STREAM (adversarial reviewer, zero calls, read-only, single process)

Date 2026-09-24. Object: the outcome at e5dbb0f, `experiment_results/x12_crossdomain/cert_direction_stream_outcome.txt`.
- Registration: `docs/judge_v2_program.md` L14758-L14792. Rulings: L14843-L14865 (60ddf85). READY: a21256d (`docs/reviews/READY_cert_direction_stream_rr.md`). Crash disclosure: L15149-L15157.
- CPU rule in force (the SPLIT-EXPOSURE-SENSITIVITY window). No stream was rebuilt and nothing was multiprocessed. Every number below was recomputed from the outcome's 200 PER STREAM lines (13 exact d_a each) and from the logs.
- Scratch: `scratchpad/cds_post/recompute.py` -> `recompute.out`, and `mcse.py` -> `mcse.out`. Both import nothing from `tools/analysis`.

## Identity of the object

| object | command | got | claimed |
|---|---|---|---|
| outcome @e5dbb0f | `git ls-tree e5dbb0f <path>`; `git show e5dbb0f:<path> \| sha256sum`; `sha256sum <path>` | blob:1563f1d1ece71daed048d3dcdfd311a8983c5f74; sha256 LF bccac1060dc03fda... (the working tree is LF, so the two are identical) | blob:1563f1d1ece71dae..., LF bccac1060dc03fda... |
| e5dbb0f scope | `git show --name-only --format= e5dbb0f \| wc -l` | 1 file (the outcome) | - |
| instrument at HEAD | `git rev-parse HEAD:tools/analysis/cert_direction_stream.py`; `git show HEAD:<p> \| sha256sum`; `sha256sum <p>` | blob:a4be06c34aa7df18b7e50db754309f9911d007e0 / sha256-lf16:b9164a0457affbd1 / sha256-crlf16:62f34cd56026ec0e (working tree) | header: same three |
| CERT instrument | same commands | blob:f7d59019c3d65128687df46aebdcb798b43c3062 / sha256-lf16:0db2026f17b559a1 / sha256-crlf16:b144a7d4377acfd3 | header: same three, MATCH |
| outcome vs operator run.log | `diff` of run.log minus progress lines against the outcome minus per-stream lines | the only difference is the "outcome written once" line | - |
| outcome written after the launch | `git log -- <outcome>` | first and only commit e5dbb0f at 05:04:38. The run started 01:37:35 and finished 05:03:22 | READY C4 |

## Per-claim table

| # | claim (as printed) | result | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | 200 per-stream lines, s = 1..200, 42 inside and counted once | CONFIRMED | recompute.py (regex parse) | 200 lines, keys == 1..200; `grep -cE '^ +[0-9]+: '` = 200 | - |
| 2 | d_a printed exactly | CONFIRMED | recompute.py (Fractions) | all 2,600 d_a are multiples of 1/20; sum d_a == Delta_W and W_F - mean W_R == Delta_W on 200 of 200 (exact rationals) | - |
| 3 | per-stream SE, lo, hi, verdict | CONFIRMED | own cluster bootstrap (B 2,000, default_rng(42), 13 anchors); hi = Delta + 1.96 SE | 0 digit mismatches out of 200 on SE (3 dp), lo and hi (2 dp) and verdict | - |
| 4 | C1 h = 49/200 = 0.2450 | CONFIRMED | recompute.py | k = 49; the HELD list is identical to the printed one (49 seeds) | - |
| 5 | Wilson 95% [0.1906, 0.3090]; MC SE 0.0304 | CONFIRMED (arithmetic); PARTLY (meaning, see D1) | own Wilson | [0.1906, 0.3090], 0.0304; Clopper-Pearson beside [0.1871, 0.3106] | MEDIUM (D1) |
| 6 | band "HELD at the registered stream, MARGINAL over the direction stream" | CONFIRMED as registered | integer band edges | 100*49 >= 20*200 and < 80*200: MARGINAL. The wording equals L14768 character for character | - (see D1) |
| 7 | C2 Delta_W mean -6.474, sd 0.943 (ddof 0 0.941); 2.5/50/97.5 = -8.15/-6.40/-4.65; range [-8.45, -3.65] | CONFIRMED | recompute.py | identical to the digit | - |
| 8 | C2 upper end mean +0.888, sd 1.249, median +0.79, 2.5/97.5 = -1.32/+3.32, range [-1.77, +4.50] | CONFIRMED | recompute.py (unrounded hi) | identical; exact median +0.7914 | - |
| 9 | C2 W_F / mean W_R / W_U distributions | CONFIRMED | recompute.py | W_F 17.650/0.906; W_R 24.124/0.226; W_U 25.640/0.930, with percentiles and ranges identical | - |
| 10 | C3 point -6.474; within 14.152, between 0.889 (ddof 0 0.885); mixture SE 3.878; +-1.96 [-14.08, +1.13] | CONFIRMED | recompute.py | 14.152 / 0.889 / 0.885 / 3.8783 / [-14.08, +1.13] | - |
| 11 | C3 two-stage percentile [-14.35, +0.75]; replicate sd 3.832 | CONFIRMED at the registered RNG | own loop, d5 draw order, default_rng(42) | [-14.3500, +0.7500], sd 3.8317. Seeds 1, 2, 3, 7 and 99 give an upper end of +0.700; 10^6 replicates give [-14.350, +0.700] and P(rep >= 0) = 0.039 | LOW (D3) |
| 12 | C4: 282 streams at h 0.245; 320 at 0.30; 381 at 0.50 | CONFIRMED | own Wilson half-width search | 282 / 320 / 381 | - |
| 13 | C0 leg 1: stream 42 = record in every field | CONFIRMED | line s=42 vs CERT's record (RECORD_42; the record's -7.15 +- 1.96 x 3.606 = [-14.218, -0.082]) | 26 17 24.15 -7.15 3.606 -14.22 -0.08 HELD, 752 / 13 | - |
| 14 | C0 leg 2: the review's 20 streams digit for digit, 20 of 20 | CONFIRMED independently | `sha256sum scratchpad/cert_post/armseed.out` = 8210a64e465c3097... (the embedded pin); compared the review's own armseed.out lines to the outcome's s = 1..20 | 20 of 20 match in W_F, W_R, Delta, SE, lo, hi and verdict; 15 of 20 upper ends >= 0; review range [-1.29, 2.76] | - |
| 15 | the first 54 streams equal the aborted run, elapsed stripped | CONFIRMED on 5 fields | own regex over the COMMITTED evidence log (blob:6038e168...; working tree sha256 99b6f63a..., byte-identical to scratch `cds_run_aborted_crash_stream54/run.log`) vs `cds_run/run.log` | 54 of 54 identical; the evidence log holds exactly 54 stream lines (`grep -c`). `cmp old54.txt new54.txt`: identical (sha256 d927e73c... both) | LOW (D5) |
| 16 | P1 HELD (36 <= k < 90) | CONFIRMED | integer | k = 49 | - |
| 17 | P2 HELD (mean in [-7.0, -6.1]; sd in [0.8, 1.4]; median hi in [-0.1, +0.9]) | CONFIRMED | recompute.py | -6.474 / 0.943 / +0.791: all three legs in | - |
| 18 | P3 HELD (mix SE in [3.65, 3.90]; percentile hi in [+0.2, +1.5]) | CONFIRMED as registered | recompute.py | 3.878 / +0.75: in. The margin on the SE leg is 0.022 (D2) | LOW (D2) |
| 19 | P4 HELD | CONFIRMED | = C0 | - | LOW (D7) |
| 20 | P5 NOT SCORED | CONFIRMED per ruling (2) | - | 320 at h = 0.30 (the prediction said "about 320"); 282 at the measured h | - |
| 21 | falsifier not fired; no insertion owed; C1 does not move | CONFIRMED | L14788-L14789 | h is not >= 0.45 and not < 0.18; band MARGINAL, so neither insertion branch applies | - |
| 22 | pins in the header | CONFIRMED | row "identity" above; build pin 128baa007a44a219 as READY C1 | all READY C1 pins printed and matching | - |
| 23 | DB identity before = after | CONFIRMED (x12 fully); PARTLY (the two large DBs) | `sha256sum stack_v2_promptv2_x12all.db` = eb0bec2795f3e5a0 now; os.stat size/mtime_ns of mmlu (974917632 / 1789828210106974800) and snapshots (1065541632 / 1790130866590831700) = printed; -wal 0 B; no -journal | the full sha256 of the two 1 GB DBs was NOT recomputed (CPU window) | - |
| 24 | connections all immutable, stack cache opened once, workers 0 | CONFIRMED as self-reported | outcome CONNECTION LOG: 4 connects, all `?mode=ro&immutable=1`, 0 at import; worker witness 4400 jobs / 8 processes / 0 opens | consistent with the code the READY verified by mutants. I did not re-execute it | - |
| 25 | Support (a)-(g) | PARTLY | own arithmetic | 2.889 x sqrt(1.636) = 3.6952 (printed 3.696, registered 3.695); MDE 10.35 OK; ratio DEFF 3.606^2/2.889^2 = 1.5580 OK. However "752 / 1.636 = 459.5" gives 459.66, and 1 + 56.99 x 0.0112 = 1.6383, not 1.636 (both come from an unrounded ICC) | LOW (D4) |

## Defects

**D1 (MEDIUM): h and its Wilson interval are conditional on ONE shared cluster-bootstrap index matrix, and the interval understates the Monte-Carlo error of h.**
- The per-stream SE comes from CERT's c1_stats: `default_rng(42)`, B 2,000, re-seeded at every call. All 200 streams therefore use the SAME 2,000 x 13 index matrix.
- On these data, that matrix inflates SE by a median of 1.3% over the exact B -> infinity value, which is sqrt(sum (d_a - mean)^2) (range 0.9989-1.0221 of exact). It does so on every stream at once. Stream 42: 3.606 vs exact 3.559.
- At the exact SE, k = 59/200 = 0.295, not 49.
- Over cluster-bootstrap seeds 1..100 (d_a fixed), k ranges from 33 to 83 (median 56). The band falls to "HELD AT ONE STREAM ONLY" at 3 of 100 seeds, and P1 is FAILED at 2 of 100.
- The registration pinned "the cluster bootstrap B 2,000, numpy seed 42", so 49/200 is the correct as-registered readout, and nothing is re-scored.
- But "Wilson 95% interval [0.1906, 0.3090] (Monte-Carlo only)" reads as the whole Monte-Carlo error of h. It is the direction-stream component only. It also excludes neither 0.20 (P(Bin(200, 0.20) >= 49) = 0.069) nor, across bootstrap seeds, a k well outside it.
- Script: `mcse.py` -> `mcse.out`.
- FIX: a registrar's bracket beside the outcome: "h at the registered cluster-bootstrap seed 42; exact-SE k = 59/200 = 0.295; over bootstrap seeds 1-100, k in [33, 83]; the Wilson interval is the stream component only." For C4's proposed D-1 standard: a registration that integrates over the direction stream must also integrate over, or remove, the cluster-bootstrap seed. The exact variance sum (d - mean)^2 is available whenever the statistic is a sum over clusters.

**D2 (LOW): P3's mixture-SE leg holds by 0.022 inside the seed noise.**
- 3.878 against a bracket top of 3.90.
- The within term inherits the D1 inflation. With the exact within variance (13.837), the mixture SE is 3.8375.
- Over bootstrap seeds 1..100 it ranges 3.727-3.944, and exceeds 3.90 at 9 of 100.
- P3 is HELD as registered. FIX: print the exact-within mixture SE beside it.

**D3 (LOW): the two-stage percentile upper end +0.75 is a lattice value at the registered RNG.**
- Replicates live on a 0.05 grid. At 10^6 replicates, and at 5 other seeds, the upper end is +0.70.
- Both values sit inside P3's [+0.2, +1.5] and both contain 0, so nothing changes. FIX: quote "+0.75 (registered RNG; +0.70 at 10^6 replicates)".
- Related: stream 168 prints "+0.00 UNDETERMINED". Its unrounded upper end is +0.0032, so the verdict is correct. Six streams sit within 0.02 of the bar (168, 129, 91, 105, 110, 50).

**D4 (LOW): Support arithmetic does not reproduce at the printed precision.**
- "n_eff = 752 / 1.636 = 459.5" gives 459.66. "ICC 0.0112 -> DEFF 1.636" gives 1.638 from the printed Kish size.
- Both come from unrounded inputs (DEFF about 1.6366), and the registration's (c) carries the same line.
- FIX: print DEFF and ICC to 4 significant places.
- Also, the Support section reprints stream 42's values, which were derived from the same stream in 605675c. It is not a re-measurement across the 200 streams; see D8.

**D5 (LOW): the 54-line determinism proof covers the 5 fields the aborted log printed.**
- Those fields are W_F, mean W_R, Delta_W, hi and verdict. W_U, SE, lo and the 13 d_a were never printed by the aborted run.
- The disclosure's "any difference voids the run" was therefore checked on 5 of 9 fields plus d_a. The rest is carried by C0 (s = 42 and the 20 review streams, all fields).
- No action needed. The record should say "on the five printed fields".

**D6 (LOW, procedural): the rule-7 witness for the relaunch is a 0-byte `cds_run/proclist_before_run.txt`.**
- Neither run.log nor dryrun.log prints free RAM or admitted PIDs. A 0-byte file cannot tell "no foreign process" from "capture failed".
- The numbers are unaffected: the run is deterministic and C0 HELD, so a breach could change wall time only.
- FIX: the operator records the W1-W5 lines, or the registrar notes the witness as absent.

**D7 (LOW): P4 is C0 restated.** "P1-P4 HELD" counts a validity gate as a prediction; three predictions are substantive. FIX: the sentence of record says "P1-P3 HELD; P4 (= C0) HELD".

**D8 (LOW): no across-stream DEFF.**
- The registration's rule-8 re-measurement is stream 42 only.
- The ratio DEFF per stream needs SE_iid per stream (sum of d_e^2), which is not printed. It needs a rebuild and is listed below.

Checks that pass without checking: D5 (5-field identity); D6 (empty witness file); SEED-PATH (2) "distinct fingerprint", a presence check that proves the knob moved but not that it moved correctly (correctness is carried by C0 leg 2); P4 = C0 (D7); the Support section re-prints the registered stream-42 values (D8); the "Monte-Carlo only" Wilson interval (D1). No check was found that could not fail. The READY's mutants covered the code paths (24 of 24 killed).

## Band wording

The printed band equals the registered string at L14768 exactly. It is licensed on the point h, by integer edges (ruling d6).

It does NOT license:
- reading h as a probability that C1 is true;
- reading "MARGINAL" as Monte-Carlo determinate. The Wilson lower end 0.1906 is below the 0.20 edge, and across cluster-bootstrap seeds the band flips at 3 of 100 (D1).

The commit subject's "band MARGINAL" is an abbreviation, not a change.

## Proposed sentence of record

"CERT-DIRECTION-STREAM (zero calls; outcome e5dbb0f, blob:1563f1d1ece71dae / sha256-lf16:bccac1060dc03fda): over the 200 registered arm-bootstrap streams (s = 1..200, 42 inside), CERT-UNDER-FILTER's C1 upper end lies below 0 on 49 (h = 0.2450, Wilson [0.1906, 0.3090], the direction-stream component only, at the registered cluster-bootstrap seed 42), band "HELD at the registered stream, MARGINAL over the direction stream"; Delta_W mean -6.474 (sd 0.943), upper-end median +0.79; the two-stage percentile interval [-14.35, +0.75] (mixture SE 3.878) contains 0; C0 HELD (s = 42 and the review's 20 streams to the digit), P1-P3 HELD, P4 (= C0) HELD, P5 not scored; C1's recorded verdict does not move. [Reviewer, 2026-09-24, recomputed from the per-stream d_a: at the exact (B -> infinity) cluster-bootstrap SE k = 59/200 = 0.295, and over cluster-bootstrap seeds 1-100 k spans 33-83, so the band is MARGINAL at the registered seed and at the exact SE but not Monte-Carlo determinate at the 0.20 edge.]"

## Does not show

- Anything about the population: 13 anchor clusters, DESCRIPTIVE-ONLY at any stream count (registration (g)). h is a share of seeds on the SAME data, not a probability of the effect.
- That C1 would hold, or fail, on new data, boards or anchors.
- The band's robustness to the cluster-bootstrap seed (D1).
- Convention B (not built, as ruled).
- The design effect across streams (D8).
- A content-closed split: the routing is bareq512_s42, id-disjoint only.
- Rule-7 compliance of the relaunch window (D6).
- The full sha256 of mmlu_pro_dataset_cache_v2.db and snapshots.db after the run, re-derived by me. Size and mtime only; the x12 cache was re-hashed.

## Stream spot-checks by rebuild, for after the window (single stream each, main checkout, read-only)

1. s = 42: reference; all fields and the 13 d_a.
2. s = 168: closest to the bar, +0.0032, UNDETERMINED.
3. s = 129 and s = 91: HELD by -0.0096 and -0.0138.
4. s = 54 and s = 55: the crash boundary; 55 is the first stream not covered by the aborted log.
5. s = 49: minimum Delta_W, -8.45.
6. s = 36: maximum W_F, 20 (with 117).
7. s = 55 also carries the minimum mean W_R, 23.40.
8. s = 200: the last stream.
9. For D8: at s = 42 and two others (for example 1 and 168), print SE_iid (sqrt of sum d_e^2), the ratio DEFF and the ANOVA ICC.

Also after the window: the full sha256_16 of the two 1 GB DBs against 4f65414f7625a1e7 and 390c313e5a40e0a7.

## Verdict

NUMBERS CONFIRMED. Every printed headline figure reproduces to the digit from the per-stream d_a with independent code. Every registered score (P1-P4 HELD, P5 not scored, band MARGINAL, falsifier not fired, C1 unmoved) is correct as registered.

RECORDABLE with the D1 bracket, which is MEDIUM: it qualifies the meaning of h's interval and does not change a score. D2-D8 are LOW.
