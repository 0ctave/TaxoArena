# Post-run numbers review: TOPIC-PARTITION-20NG-T1B-NULL addendum readout (READY condition C5)

Reviewer: adversarial-reviewer, 2026-09-23, zero calls, read-only. I recomputed every number below with my own script from the CSV and the jsonl. None was copied from the outcome file.
Scripts (session scratchpad): `t1b_post.py` covers k, Wilson, the A2 rows, the tree, the bands and the near-misses. `mc.py` covers the Monte-Carlo fragility of the p95. Both read `experiment_results/topic_partition/site_null_ng_af_bareq512_s42.csv` and `experiment_results/topic_partition/ng_af_bareq512_s42/seed_42/dag_snapshots.jsonl` read-only.
`snapshots.db` was NOT opened. It was not needed, because the depth-1 ids and the site count come from the jsonl.

## Objects pinned
| object | check | result |
|---|---|---|
| CSV | `sha256sum`; `git diff --quiet 8804930 -- <csv>` | sha256 9cc7375c06b016fc..., equal to 8804930. The backup copy in `_backup/t1b_null_2026-09-23/` has the same sha16. 97 rows, 97 distinct node_id, one snapshot 20260923_043423_Headless_Run_Auto_ge, reps {300} |
| addendum outcome | `git hash-object` vs `git rev-parse 9f9b9ac:<path>` | 782654cc0442... both; sha256 e2ff7e4e...; no working-tree diff |
| main outcome of record | sha256[:16]; `git hash-object` | 263ed95f9e9d1527 / 90632b36bed0, unchanged (matches what the addendum's guard printed) |
| jsonl | last line, iteration 15 | 197 nodes, 100 leaves, 97 sites (>= 2 children), one root n00000001; orphans CSV->site 0, site->CSV 0 |

## Per-claim table
| # | claim (outcome) | recomputed | verdict | command |
|---|---|---|---|---|
| 1 | k = 1 of 97 = 0.010, Wilson [0.002, 0.056] | cert_site_p95: false 96, true 1. Independent flag (observed >= p95) also gives 1. Share 0.010309, Wilson (z 1.959964) [0.001822, 0.056105], i.e. [0.002, 0.056] | CONFIRMED to the digit | t1b_post.py |
| 1a | (the one certified site) | n00000110: depth 4, n 271, observed 0.069971 vs p95 0.064652 (ratio 1.082) | detail | t1b_post.py |
| 2 | A2 root n00000001: n 11845, 0.048664 vs 0.056788, margin 0.857, False | identical; jsonl subtreeQueries 11845 | CONFIRMED | t1b_post.py |
| 2 | A2 depth-1 n00000004: n 5703, 0.036789 vs 0.046432, margin 0.792, False | identical; jsonl 5703 | CONFIRMED | t1b_post.py |
| 2 | A2 depth-1 n00000005: n 6254, 0.029781 vs 0.053796, margin 0.554, False | identical; jsonl 6254 | CONFIRMED | t1b_post.py |
| 2a | depth-1 ids taken from the tree, not from the script | jsonl: root childIds = [n00000004, n00000005]. The depth==1 nodes are exactly these two, each with parent n00000001 and 2 children | CONFIRMED | t1b_post.py |
| 3 | bands: n<200 0/22; 200-400 1/33; 400-800 0/19; >=800 0/23 | 0/22, 1/33, 0/19, 0/23 (sum 97). The cut rule is the one at topic_partition.py L863 (half-open, so n=800 falls in ">=800"). Exactly one site sits on a cut (n=800). It is uncertified, so no band's k depends on the boundary convention. Only its band n would change: 23 becomes 22 and 19 becomes 20 | CONFIRMED | t1b_post.py; `sed -n 855,870p tools/analysis/topic_partition.py` |
| 4 | A2 = PARTIAL; AF1 FIRED; AF2 NOT FIRED | Registration A2 (L11558): HELD iff the root AND at least one depth-1 site certify; PARTIAL if the arm is built (> 20 leaves) but either clause fails; UNDETERMINED iff A1 fails. Here A1 HELD and leaves are 100 > 20. The root is False and both depth-1 sites are False, so BOTH clauses fail and A2 = PARTIAL (A2 has no FAILED branch). Ruling (2) (L13486-L13489) says AF1 fires iff A2 = PARTIAL, so AF1 FIRED. AF2 fires iff A1 fails, so AF2 NOT FIRED | CONFIRMED | `git show 7da2ec5:docs/judge_v2_program.md \| sed -n 11542,11572p` (same line at HEAD); `sed -n 13440,13530p docs/judge_v2_program.md` |
| 5 | AP1 HELD at 134.5 min, no OOM | The .out has 2 segment headers. The last segment is L46-L201 (relaunch 11:35:16, -DsiteNullHeap=14g, -PnullReps=300). L199 reads "BUILD SUCCESSFUL in 2h 14m 29s" = 134.483 min, which rounds to 134.5. That is inside the registered 90-140 (point 108) and 5.5 min under the ceiling. OutOfMemory count in L46-L201: 0 (whole file: 0). [SITENULL-HEAP] 7.28 GB vs a 13.53 GB budget. [SEPBAR] at L76: 0.0145 / 512 / reps 300. The task's own summary line: "site-cert 1/97" | CONFIRMED | `sed -n 46,201p <out> \| grep -c -i OutOfMemory` |
| 5a | AP2 FAILED (registered 8-22%) | 0.0103 < 0.08 | CONFIRMED | arithmetic |
| 5b | AP3 FAILED | the root and both depth-1 sites are not certified | CONFIRMED | t1b_post.py |
| 5c | AP4 HELD (below 0.158) | 0.0103 < 0.158. T1's 0.158 is quoted from topic_partition_outcome.txt L14, which I verified is present. DESCRIPTIVE-ONLY: the Support MDE is 0.142 | CONFIRMED as recorded; no inferential weight | `sed -n 14p` |
| 5d | A4 print obeys ruling (4) | the A4 line never prints 16, 101, 85 or "16/101" as T1 figures | CONFIRMED | outcome text |
| 5e | A1 HELD; AP5 HELD | 97 rows, reps 300, one snapshot id, orphans 0/0. AP5 rests on the guard (2) PASS lines | CONFIRMED (A1 recomputed; AP5 read from the guard print) | t1b_post.py |

## Item 7: how fragile is k = 1 (a descriptive caveat, not a verdict)
- Sites by observed / site p95:
  - >= 0.95: 2 sites (n00000110 at 1.082, certified; n00000252 at 0.971).
  - >= 0.90: 4 sites.
  - >= 0.85: 12 sites.
  - >= 0.80: 13 sites.
- Monte-Carlo noise of a 300-rep p95, in a normal approximation: SE(p95) is about 0.122 x the null SD, with the null SD taken as (p95 - p50) / 1.645.
  - Expected k under a p95 redraw: 1.00.
  - The certified site sits +7.3 SE above its p95. The nearest miss (n00000252) sits -3.8 SE below. Every other site is below -9 SE.
  - Replicate noise alone therefore leaves k at 1. Even if every site within 10% of its p95 flipped, k would be 4. k cannot reach AP2's band (8/97).
- Context: at 86 of 97 sites, the observed separation is BELOW the null's own MEDIAN.
  - Only 11 sites have observed >= p50. The median observed/p50 ratio is 0.686.
  - The observed separation is >= the construction bar 0.0145 at 97/97 sites (min 0.016087), while the smallest null p50 is 0.033124.
  - So this is not a population of near-misses. This is a disclosure, not a registered statistic.
- NOT modelled, by the readout or here: variation from tree to tree (one seed, one split, no re-draw). The fragility that matters is the draw, not the 300 reps.

## Item 6: the AF1 sentence
Registered AF1 (L11562): "the per-corpus pair BUILDS BUT DOES NOT CERTIFY on this corpus, which would overturn the reading that the FRAMEWORK pair transfers whole and would narrow the transfer finding to the bar-0.025 / 256-dim recipe alone (C3 of TOPIC-PARTITION-20NG is untouched either way)".
Printed AF1: the same words with two changes. "would" is dropped, because the falsifier fired. "FRAMEWORK pair" becomes "FRAMEWORK 512 / 0.0145 pair", and the registration's own title names the pair as 512 / 0.0145. Verdict: CONFORMANT, with no added claim.
In this record, "does not certify" means exactly this: under A2's rule, T1b's root and BOTH depth-1 sites fail cert_site_p95 against their own 300-rep site null at bar 0.0145. Across all sites, 1 of 97 certifies (descriptive). The statement is about the CERTIFICATE on ONE built tree. It says nothing about whether construction works.

### Proposed sentence of record
"TOPIC-PARTITION-20NG-T1B-NULL (zero calls): on 20 Newsgroups, the T1b tree was built with the FRAMEWORK per-corpus pair (512 dims / bar 0.0145; seed 42, one split; 100 leaves, 97 sites). It BUILDS BUT DOES NOT CERTIFY against its own site null (300 reps). The root (observed 0.0487 vs p95 0.0568) and both depth-1 sites (0.0368 vs 0.0464; 0.0298 vs 0.0538) fail, so A2 = PARTIAL and AF1 FIRES. The reading that the 512 / 0.0145 pair transfers WHOLE to this corpus is overturned. On this corpus the recorded transfer (TOPIC-PARTITION-20NG C3, HELD) rests on the 256-dim / bar-0.025 arm T1 alone. Descriptively, 1 of 97 T1b sites certifies (0.010, Wilson [0.002, 0.056], nominal because the sites are nested); that count is not compared with T1's."

### What it does NOT show (must travel with the sentence)
1. It does not show that construction fails on 20 Newsgroups. T1 (256 / 0.025) on the same corpus and split built 110 leaves and certified its root and one depth-1 site. C3 HELD, and this addendum does not touch it.
2. It does not show that 512 / 0.0145 is worse than 256 / 0.025 on certified counts, or rank the two recipes in any way. The bars differ, the nulls differ, and p95 falls with n. Bracket (b)(5) bans the cross-bar certified-count comparison, and it is unpowered (MDE 0.142). Nobody may write "1 of 97 vs 16 of 101".
3. It does not show which knob is responsible. Dims and bar changed together, and no arm varies one of them alone.
4. It shows nothing about MMLU-Pro or any other corpus. ANCHOR-FREE-CERT arm 4 (the same pair, 10 of 87 on MMLU-Pro) is untouched. "Transfers whole" is overturned for 20NG only; it is not withdrawn where it was measured.
5. It does not show that the 256 / 0.025 recipe transfers in general. "Narrows to the 256 recipe alone" refers to the one arm that certified on this corpus, in one draw. It is not a new positive finding for that recipe.
6. It shows nothing about the partition (C1), the topic-informativeness of the certificate (C2; T1b's sites are never pooled, and the cert-vs-alignment line stays UNDETERMINED), or P12.
7. It does not show robustness to the draw: one corpus, one embedding model, one seed, one split, no re-draw. The Monte-Carlo noise of the 300-rep p95 does not threaten k = 1 (item 7), but the tree itself is a single draw.
8. It does not show that the bar 0.0145 is "wrong" in general. The addendum registers no reading of the observation that the bar sits below the null median (item 7).

## Defects
- D1 LOW: the outcome's A2 line says "at least one depth-1 site certified FAILED". In fact both depth-1 sites fail (0 of 2). The line is true, but a reader may take it as one of two. Fix: the registrar's bracket writes "root and both depth-1 sites not certified (0 of 2)".
- D2 LOW: AP1's 134.5 min is inside the band but 5.5 min from its ceiling and 26.5 min above the point (108). Wherever AP1 is restated, keep the measured value beside "HELD", as the outcome file does.
- D3 LOW (disclosure): the fragility disclosure should carry the numbers from item 7 (nearest miss 0.971; expected k 1.00 under a p95 redraw; 86/97 below the null median), so that "Monte-Carlo fragility disclosed" has content.
No BLOCKER, no HIGH, no MEDIUM.

## Verdict
C5 MET. The following reproduce independently to the printed digit: k, the Wilson interval, the three A2 rows, the depth-1 ids (taken from the jsonl) and the four bands. A2 = PARTIAL is the correct branch. Under ruling (2), AF1 FIRED and AF2 NOT FIRED are both correct. AP1 HELD at 134.5 min with 0 OOM in the last segment. AP2 and AP3 FAILED and AP4 and AP5 HELD, as recorded. The AF1 text matches its registration.
The sentence of record above is the ceiling. Wording over-reaches if it drops "against its own site null", "on this corpus" or "one draw", or if it puts T1b's count beside T1's.
