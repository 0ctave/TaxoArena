# POSTRUN review: FRESH-RULES-SIM (fresh-item rules A and B on a WORK pseudo-fresh split; EXPLORATORY, MATH WORK only)

Authority: D-2026-10-26-1 (a8990e4b, `docs/agents/author_decisions/2026-10-26.md`, incl. the main session's reading);
rule definitions: prog "## Registrar's record 2026-10-26 ... BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-26-1"
(L25708-L25724, _as_of 6f16a31c), paragraphs RULE B, RULE A, A-vs-B, SE_cell UNDER RULE B, POWER PLAN, FRESH-RULES-SIM.
Reviewer: adversarial reviewer, 2026-10-26. Zero LLM calls; my loads read no vault/reserved response (`guard.reads` 0).
Reviewed: benchzoom branch `fresh-rules` (local only; remote branches containing f3b16fb: 0), 8d8d824..f3b16fb, 2 files,
2,881 insertions, 0 files under `src/` (count: `git diff --name-only 8d8d824..f3b16fb | grep -c '^src/'` = 0). master
8d8d824 is an ancestor (fast-forward).
- Run blob (parts repro, split0-4, bootA, bootB, --analyze): `blob:659bb759e227c429ab7882c8f99fe21497a82b2e`
  (sha256-lf16:9b4b6aa5e928804e). Addendum blob (bootA2/bootB2, --analyze-boot2): `blob:7251775f` (lf16 a0cdbef228b9e78f).
  Tip blob `f525a403` (lf16 a9c746264f179e73): +12/-1 vs 7251775f (docstring paragraph + one header label, disclosed [P2]).
  Working tree 0 CR bytes: no CRLF rendering. Plan blob 2800aae `c4c24d5f` -> tip `269d51c8`: numstat 82/0 (insertion only).
- Every part JSON and all 36 build pickles carry `dirty ""`, blob 659bb759 (bootA2/bootB2: 7251775f), `vault_reads 0`;
  builds `model_responses_read False`. Outputs: summary.txt sha256 e99cf6a5..., SHA256SUMS 5f84e29c... (19/19 OK),
  summary_boot2.txt b86cfe68..., SHA256SUMS_boot2 (6/6 OK), splits.json d994dd06...; backup 236/236 OK, SHA256SUMS
  identical (`cmp`). Output dir unchanged by this review (SHA256SUMS sha256 before = after; 0 files newer than 21:30).

## Verdict

**OUTCOME CONFIRMED (exploratory): every printed number and word reproduces to the printed digit from my own code;
the rules match the registrar's definitions; no pseudo-fresh item reaches a rule-A object; the sanity checks ran; the
plan preceded every statistic. MERGEABLE (example + doc only). BUT the run does NOT license the FRESH power plan's n\*:
W3/W4 n\* and W2 "DEFF CONSTANT IN n" are REFUTED as planning inputs by the simulation's own n = 2,949 point (H1).
Two leakage mutants survive the selftest (H2). No BLOCKER for the exploratory merge.**

## Per-claim table (deciding claims; x 1e-3 nats per cell)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan before every statistic | Plan 2800aae 17:44:58; run code 449e95a 18:46:54; splits.json 18:47:05; 36 builds 18:50-19:11; first statistic (repro part) 19:17:34. [P1] 73401db 19:33:45, after bootA r00-r04 (19:29:57-19:33:08), before r05 (19:33:56); bootA2 r00 20:38:13 after 6e5ecc4 20:36:38. Scratch files before 17:44:58 (E:/TaxoArena_tmp/fresh_rules): synthetic probes, a text-side id/embedding check, the registrar's arithmetic; none reads a response statistic | CONFIRMED | - |
| 2 | Rules A/B = registrar's definitions; text + declared labels only | Code read against RULE B / RULE A: V0' = `map_config(0,"axis",3.0)` on old+fresh text, groups = subject; K' = flat-compare `kmeans_partition` (blob da00fcda = 516c6ba) at V0' per-anchor leaf counts, stream [20261025,1,rank,s]; N'/N512' = `meter.step("field_txt")`, pool = fresh training rows; A: own-cut routing, within-anchor nearest unit centroid, N_A pool = pseudo-old WORK rows with residuals under the pool-fitted parent. Rebuild of split0_A from text alone: paths and K_0..4 identical (187 s). Sim adaptations, declared: K_A at V0_A,s counts (stand-in for V0's 9/3/4/6/4/7/3); A transport at C = 36 | CONFIRMED | - |
| 3 | Pseudo-fresh never in rule-A cells / pool | Per split (5/5): \|A build ids ∩ F_s\| = 0; A ids = all 4,914 − F_s; K_A labels on build rows only; A fresh_ids = F_s; my own routing (library `axis_cut` per node) = pickled fresh leaf 885/885, K_A 885/885 x5 seeds; my harness with the pool built from scratch (WORK − F_0, 2,064) reproduces N_A per item (below). Split redrawn by my code = splits.json (5/5); clusters straddling fresh/old: 0. Text twins (cos >= 0.98) of fresh items among the 1,965 vault texts in A's build: 0/1/1/2/0 of 885 | CONFIRMED | - |
| 4 | Sanity S-B0/S-A0 ran | B0.pkl equal_v0 True, equal_km True; repro part vs FLAT-COMPARE math.npz per item: max\|diff\| 0.0 on all 11 arrays, clusters equal (my read); pinned V0 self-route 1.0000 | CONFIRMED | - |
| 5 | Per-item values (split 0, phi 1.00) | My harness (library readers wired by me; own pool kNN by full sort + own S-TAU loop): max\|mine − part\| 0.0 on V0A, KA0-4, V0B, KB0-4, NB, N512B, V0B\|L2+NB, NB\|L2+V0B; <= 9.0e-17 on NA, N512A, V0A\|L2+NA, NA\|L2+V0A; cell mismatches 0/12 | CONFIRMED | - |
| 6 | Table at 885 (A: −0.010/+0.012/+0.455/D_N −0.464; B: −0.016/+0.035/+0.050/−0.067) | Same to 4 decimals for all 8 contrasts x 2 rules (e.g. A D_N −0.4644 (0.1297), B D_K −0.0516 (0.0360)) | CONFIRMED | - |
| 7 | W1 "A AND B DISAGREE on N, N512" | D_AB(N) +0.4045 (0.1308), N512 +0.3832 (0.1245), 0/5 splits within 1 SE; V0 +0.0066 (0.0199) passes on the mean but only 2/5 splits within 1 SE; K −0.0233 (0.0285) 4/5. ARI 0.743 / 0.743 | CONFIRMED | L3 |
| 8 | W2 7/10 CONSTANT, D_K GROWS (1.53, 1.83), B D_N SHRINKS (0.65) | Arithmetic: same Q to 2 decimals. Substance: the sim's own n = 2,949 point (repro part = rule B with every WORK row fresh, same harness) gives DEFF P 3.26 (885: 1.60 B / 1.82 A), D_K 2.39 (1.78/1.56), D_N 1.48 (0.92/1.06), G(N\|L2+V0) 1.77 (1.01/1.04), G(V0\|L2+N) 2.23 (1.44/1.37): DEFF grows with n for every contrast beyond 885 | arithmetic CONFIRMED; as a planning input REFUTED | HIGH (H1) |
| 9 | W3/W4 SCOREABLE, n\* A 296/3,149/3,243/458, P 645/1,315; B 666/195/237/247, P 374/477; A floors 0.064/0.099/0.087/0.023/0.072 | Brute-force integer scan, own transport: every n\* and floor identical. Substance: transported SE at n = 2,949 (rule B, from 885) vs measured at 2,949 on the same harness: D_K 0.0321 vs 0.0553 (x1.72), D_N 0.0192 vs 0.0658 (x3.43), G(N\|L2+V0) 0.0215 vs 0.0611 (x2.85), G(V0\|L2+N) 0.0071 vs 0.0152 (x2.14), P meter 0.0093 vs 0.0316 (x3.41), P cell 0.0139 vs 0.0570 (x4.10). MDE80 understated by the same factor, n\* by about its square | arithmetic CONFIRMED; as planning n\* REFUTED | HIGH (H1) |
| 10 | Grouped f_boot2 ~1.0 kNN, ~2 P and D_K, 4-5 G(V0\|L2+N) | From the replicate files: A 2.11 / 1.02 / 0.94 / 3.78 / 1.82; B 1.95 / 1.13 / 0.99 / 4.83 / 1.87 (D_K, D_N, G(N), G(V0), P); planned ungrouped replicate means −2.21 (A) / −2.47 (B) for P vs points −0.027 / −0.009: [P1]'s leak is real | CONFIRMED ("4-5" is 3.8-4.8) | L1 |
| 11 | Leaf growth c 0.00744 vs 0.00733 | c 0.007439 (OLS 4.38 + 0.006423 x); with the 20 bootB builds as extra points 0.007449 | CONFIRMED | - |
| 12 | Selftest 9/9; mutants 87/87 + 11/11 + 14/14 | Selftest re-run (sandbox): 9/9 PASS, rc 0, tracked tree unchanged. Builder's mutants not re-run (table read). My 6 mutants: 4 killed, 2 leakage mutants SURVIVE (below) | PARTLY | HIGH (H2) |

Own mutants (copies under E:/TaxoArena_tmp/review_fresh-rules/mut/20261026T214637, TMP/TEMP/TMPDIR/BZ_SANDBOX redirected;
control passes): R1 W1 against the cell SE: killed (S7), not decisive on the data. R2 m = n/36: killed (S6). R4 DEFF
split mean = ratio of mean SEs: killed (S7). R5 W4 growth C = c·n: killed (S6). **R7 rule-A pool parent reads B0's
(fresh-text) leaves: SURVIVED. R8 rule-A tree built on old + fresh text: SURVIVED.** Both decisive for the leakage
property; the run of record is clean by the count checks of row 3, so they are guard defects, not outcome defects.

## What FRESH-RULES-SIM licenses for the FRESH power plan, and what it does not

Licenses (planning only):
1. Cell growth: V0' leaf count grows about in proportion to the items built on (c 0.007439 vs 36/4,914 = 0.007326,
   +1.5%; range 4,029-4,914 items, so 7,863 items is a 1.6x extrapolation). The "no growth" floor of Support (g) is not
   the expected case under B.
2. Constant-rho cell transport for the TREE contrasts (clustered form): rho at m 25-29 vs WORK at m 81.9: P 0.0255 (B)
   / 0.0293 (A) vs 0.0279; G(V0|L2+N) 0.0188 / 0.0130 vs 0.0152. For D_K the sim's rho is 1.2-1.9x WORK's (0.0332 /
   0.0199 vs 0.0171); for the kNN contrasts the sim's near-degenerate readers give rho ~0 vs WORK 0.0059 (D_N) / 0.0096.
3. Rule A's assignment is well defined for the real pinned V0 (own-cut self-route 1.0000 on 4,914 items).
4. Q3 sharpened: at 885, A-vs-B on N measures pool size (2,064 old rows vs ~708 fresh training rows); it does not
   transport to the planned n, where B's pool is about 0.8 n.
5. SE_cell by resampling needs inner folds grouped by content cluster ([P1]); rule-B rebuild wall-clock ~245 s per
   replicate build + ~52 s harness (6 workers).

Does not license:
1. Any n\* of W3/W4 (row 9). Re-derive with the registrar's WORK-anchored SE (n = 2,949) and the effect expected at
   the planned n; below 2,949 both the SE and the effect shrink, and neither transport models the effect.
2. "DEFF constant in n" (row 8): W2 compares 221 vs 885 only (DEFF SD over splits 0.1-0.6).
3. D_N's f from the sim (0.96-1.03). Measured instead from the repro part (= FLAT-COMPARE per item) at WORK scale:
   D_N V0-leaf f 1.215 (DEFF 1.48, rho 0.00589), replacing the 1.82 stand-in ("never measured" in the record). Under the
   registrar's own transport (SE_W 0.05419, distance 0.25): MDE80 at n 2,949 0.206 (cell growth) / 0.220 (fixed 36), floor 0.126 (< 0.25, so
   DRAFTCHECK E1's D_N floor 0.277 no longer arises), n\* 1,873-2,055 (c-growth / fixed 36). n\* below 2,949 has the
   caveat of item 1. Clustered form, not the declared resampling SE_cell (M1).
4. The draft's predicted points at fresh n: every partition gain under B is about 0 at 885 (C1(V0') −0.016, C1(K')
   +0.035, C1(N') +0.050) against +0.109 / +0.275 / +0.350 at 2,949.

## Defects and conditions

- **H1 (HIGH, record condition).** W3/W4 n\* and W2's CONSTANT words must not enter the FRESH Support. Fix: the
  registrar copies leaf growth (lic. 1), the rho comparison (lic. 2) and D_N's WORK f 1.215, and carries W2-W4 only with
  the words "transport SE understated x1.7-x4.1 at n 2,949 (POSTRUN_FRESH-RULES-SIM row 9)". A re-run is not needed: add
  the repro part as the n = 2,949 point of readout (ii) in any reuse.
- **H2 (HIGH, before any reuse of the rule-A code in the registration's READY).** No runtime refusal and no selftest
  check that rule A's build and pool exclude the fresh items (R7, R8 survive). Fix: in `build_record` (kind A) refuse
  unless set(build ids) ∩ set(fresh ids) = ∅; in `part_split`/`part_boot` refuse unless the pool-parent leaves come from
  the A record whose ids exclude F_s and pool rows ∩ scored rows = ∅; selftest S7 asserts both; re-run R7/R8 killed.
- **M1 (MEDIUM, SUBSTITUTED by plan, disclosed).** Transport (iii) and W3/W4 use the clustered f; the registrar's
  declared SE_cell under B is the partition-level resampling, measured at one split and one n only. At split 0 the
  resampling f is 1.4x (P), 1.4-2.0x (D_K), 0.9-1.1x (kNN), 3.9-4.4x (G(V0|L2+N)) the clustered f. Any copy is labelled
  "clustered form (SUBSTITUTED for the declared SE_cell)".
- **L1.** Hand-back "4-5" for G(V0|L2+N) f_boot2: A is 3.78. **L2.** "About 2.6 h of parts": part mtimes give about
  1.93 h (19:11-20:18 and 20:37-21:26); not of record. **L3.** W1's V0 leg passes on the mean with 2/5 splits within
  1 SE; agreement of near-zero gains is not agreement at the planned n. **L4.** Summary header mislabel (disclosed [P2]).
  **L5.** bootB2's kNN contrasts keep the residual twin effect (disclosed [P1]).

merge_ok: YES (benchzoom fresh-rules f3b16fb, fast-forward onto master 8d8d824; examples + docs only; outputs not
committed). The ledger, the programme and benchzoom master were not touched by this review.

## Commands (scripts and logs in E:/TaxoArena_tmp/review_fresh-rules; benchzoom venv, BLAS 1, <= 6 processes)

```
r1_stats.py   -> r1.log  own split redraw, leak sets, growth, own CR SEs / two-way / MC / DEFF / transport / brute-force n*,
                         n = 2,949 anchor from parts/repro.npz, f_boot from the replicate files
r2_route_harness.py -> r2.log  own routing (axis_cut per node) + own K_A, 5 splits; own harness split 0 phi 1.00 (4 workers),
                         pool from scratch; per-item max|diff| vs parts/split0.npz
r3_rebuild.py split0_A -> r3_split0_A.log  rebuild from text: paths and K_0..4 equal
r4_mutants.py -> r4_mutants.log  R0 control + R1 R2 R4 R5 R7 R8 (sandboxed copies)
r5_extra.py   -> r5.log  repro vs flat-compare math.npz per item; D_N transport with f 1.215; vault-text twins
PYTHONPATH="src;examples" python examples/fresh-rules.py --selftest      (sandboxed TMP) -> selftest.log 9/9 PASS
git log --format='%h %ad' --date=iso 8d8d824..f3b16fb; find E:/benchzoom_demo/followups/fresh-rules -printf '%T+ %p'
sha256sum -c SHA256SUMS (19) / SHA256SUMS_boot2 (6) / backup SHA256SUMS_backup (236)
```
