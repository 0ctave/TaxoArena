# Post-run review: ARCH-V2 G22 / G23 READY legs, record runs at 4381e4b (= ca84e44), outputs at 5abb79f

Adversarial reviewer, 2026-09-24. Zero judge calls. Read-only: every DB was opened `mode=ro&immutable=1`. Single process. No validity-v2 or `--dev` run.
Object: `experiment_results/archv2/g22_g23/` at 5abb79f (23 files). The `.log` files beside them are on disk and gitignored.
Registration: `docs/judge_v2_program.md` L15208-L15265 (d6129cf). Rulings: L15341-L15448 (83f431b, 4b25059, 97f3a1f, and the 5dfc825 record). READY: `docs/reviews/READY_archv2_EA.md` (ca84e44 section, conditions V1-V4 and F1-F2).

## VERDICT (per leg)

| leg | verdict | one-line reason |
|---|---|---|
| G23 (a) identity | **ACCEPT** | I re-ran it from a `git archive 4381e4b`: the tables come out 04754dbc… again and the body is byte-identical. My own code recomputes every integer. |
| G23 (b) certab | **ACCEPT** | Re-run is byte-identical. My own code gives grok A 653 / 2(1) / 1.24 and B 637 = 69.24%, 2(1), so B is ADMISSIBLE. P2 and P3 HELD. |
| G23 (c) conjuncts | **ACCEPT** (descriptive) | Re-run is byte-identical (drop 0). Not recomputed with independent code. |
| G23 (e) holm | **ACCEPT** | Re-run is byte-identical. My own McNemar and Holm give 809 / 736 / 671 and 19 lost edges, 0 of them wrong-direction. |
| G23 (f) mcstreams | **ACCEPT** (descriptive) | Re-run is byte-identical: 646 / 252 / 22 = 920. It uses the fast builder by design (5 streams). |
| G23 (d) residue, merged | **ACCEPT WITH** R1 | Precondition 1714 / 4(4) MET (my own code agrees). The per-edge "called" column is certificate A, not the certificate of record (R1). |
| G22 (b) nu | **ACCEPT WITH** N1, N2 | P2 FAILED on the 4 merged fits. The registered grok_calib arm (k ≤ 12) was not run in the record run (N1). |
| G22 (h) coverage | **ACCEPT WITH** C1 | My own code gives the same 2 / 14, every D_c to 4 decimals. P6 FAILED. The registered "A on the EVAL side" is not printed (C1). |
| G22 (f) overdispersion + P7 | **ACCEPT WITH** O1-O4 | Re-run is byte-identical. My own code gives the same χ², DEFF, residue and P7. P7 HELD only under the post-data scoring rule (O3). |
| G22 (a) v1 validity | **ACCEPT: the FAIL is genuine**, WITH V-a to V-c | The random (primary) mode misses 4 targets outside the ENTIRE simulated range (0 of 1,000 replicates reach them). Neither D9, the Bonferroni level, nor a wrong target explains it. The registered falsifier (a) FIRED. |

No leg is REJECTED. Nothing below moves a recorded number. The defects are wording, labelling and omissions.

## Proposed sentence of record

"ARCH-V2 G22 / G23 READY legs, record runs at 4381e4b, independently reproduced (post-run review 2026-09-24).
- G23: identity HELD (tables sha256 04754dbc…, byte-identical, re-run and recomputed). Certificate B is ADMISSIBLE on both draws (utility 69.2% / 69.3%, LOAO wrong(established) 1 ≤ A's 1). P1, P2 and P3 HELD (cross-draw Jaccard 0.941 / 0.938). Holm: 809 → 736 per anchor → 671 pooled; the 19 ordered edges that lose establishment are all right-direction. MC-UNRESOLVED 22 of 920.
- G22 v1 validity FAILED as registered: the fresh-judge (random) mode puts f_raw_wrong at median 222.5 (central 0.99643 interval [43.9, 468.7]) against 7, and f_loao_called at median 6 [0, 384.9] against 667, with no replicate of 1,000 reaching either target (u likewise). The falsifier (a) FIRED: the registered simulator decides nothing. Design readings can re-enter only through the POST-HOC-SPECIFIED one-shot v2 (ruling 1 (ii)).
- P1 FAILED; P2 FAILED (merged exponent 1.88-2.02, CIs [1.78, 2.16], against 1.06 [0.80, 1.30]; the grok arm was not run); P3-P5 NOT SCORED (gated); P6 FAILED (2 of 14 anchors at D_c ≥ 0.95).
- P7 HELD under the post-data ruling of 97f3a1f: Meta-Llama-3_1-70B-Instruct is the unique top among merged's 4 called wrong(established) edges; the roster clause is OK on all three boards. Under the pre-data reading 'unique top on every board' it is NOT HELD (x12 and grok are one-edge ties).
- Merged wrong(established) overdispersion: by model χ² 53.40 on 20 models, p ≤ 0.0005 (0 of 2,000 permutations; within-anchor null p 0.0001); by anchor χ² 22.34, p 0.0465 ± 0.005 (Monte Carlo); DEFF 1.780 (ICC 0.0050, Kish m 158.3)."

## Per-claim table

Scratch lives in the session scratchpad: `arch4381/` = `git archive 4381e4b tools experiment_configs src/main`, and `out/` holds the outputs. Env `TAXOARENA_DATA_ROOT=Z:\FAC\TUBerlin\THESIS\TaxoArena`.

| # | claim (operator) | result | command / script | mine vs claimed |
|---|---|---|---|---|
| 1 | Outputs ran on the pinned 4381e4b instrument | CONFIRMED | `grep blob: <out>` vs `git ls-tree -r 4381e4b -- tools/analysis/archv2_*` | 17 / 17 (G23 outputs) and 14 / 14 (G22 outputs) printed blobs are in the 4381e4b tree, 0 not in it. The pin-block digest is identical across all 6 G23 outputs and across all 4 G22 outputs. `git diff --name-only 4381e4b ca84e44 -- <archv2 files> \| wc -l` = 0. The 165ffb8 merge (11:29:17) postdates the last run (validity exit 11:27:56) |
| 2 | The pool line and pins match | CONFIRMED | `grep -m1 '^\[POOL\]'` on 10 outputs; `python tools/analysis/pool_guard.py --pool p2dca21ab5f4ef3ae` | All 10 outputs print `[POOL] p2dca21ab5f4ef3ae … PASSED`. My guard run: OK, ids 3,599 / judgeable 3,445 / sentinels 154. pool_guard.py blob 6521b51a is the same at 4381e4b, at HEAD and in the working tree |
| 3 | V3: the stream logs are intact | CONFIRMED | `sha256sum <out>.streams.tsv` vs the printed "log sha256"; `grep -c ''` vs "N named streams" | 10 / 10 MATCH, line counts equal. Validity: 45,014 = 3 × (1,000 + 14,000) + 14 (R = 1,000 per mode, completed) |
| 4 | V4: validity DB OPENS = 3, immutable | CONFIRMED | G22_validity.txt | 3 (snapshots, grok_calib, eval) |
| 5 | G23 identity PASS, 04754dbc, with witness | CONFIRMED (re-run + recomputed) | `archv2_g23_replay.py --leg identity` from arch4381 → `out/`; `sha256sum out/*.tsv`; body diff | Both tables are 04754dbc5d94…; the body diff (header lines excluded) is empty; witness {'edges_exact.boards': 4200, …}. Independent (review_stats.py): grok f 891: raw 733 / 7; LOAO 667 / 2(1) / 1.11, b0 -3.5451 b1 +3.3854; u 920: raw 740 / 8; LOAO 653 / 2(1) / 1.24; established 809 |
| 6 | certab: B ADMISSIBLE on both draws | CONFIRMED | re-run is body-identical; review_stats.py (own LOAO + own gate) on grok | Grok: A 653 / 2(1), 70.98%; B 637 / 2(1) = 69.24%. Kotlin (re-run only): A 661, B 636 / 918 = 69.28%, 1 ≤ 1 est |
| 7 | conjuncts drop 0 | CONFIRMED (re-run only) | body-identical | beta_len +0.3075 (SE 0.0428), 653 ordered, drop 0 |
| 8 | holm 809 / 736 / 671; 19 ordered-key edges lose establishment | CONFIRMED | review_stats.py: own exact McNemar (scipy binomtest) on each anchor's judged questions, own Holm, own LOAO A | 809 / 736 / 671; 19 lost, of which **0 are wrong-direction** (the output prints "key direction right" for all 19) |
| 9 | mcstreams 646 / 252 / 22 | CONFIRMED (re-run only) | body-identical | 646 + 252 + 22 = 920 |
| 10 | Precondition 1714 / 4(4) MET in both runs | CONFIRMED | review_stats.py: shipped pair cold (-3.2326 / +3.3133) + established-only decline on gap ≥ 0.02 | merged 2,538 → widener 1,783 → 1,714 called, 4 wrong. Residue edges: Law L3.1-70B vs Qwen72B / deepseek / gpt-4o-mini, Philosophy L3.1-70B vs gpt-4o-mini. x12 891 → 665 → 651, 1. grok 891 → 669 → 649, 1 |
| 11 | P7: identity HELD on merged; x12 / grok UNRESOLVED; roster OK | CONFIRMED (as ruled post-data) | review_stats.py incidence; eval DB `SELECT DISTINCT model_name` (47; 46 after the quarantine) | merged incidence {L3.1-70B: 4, gpt-4o-mini: 2, Qwen72B: 1, deepseek: 1} → unique top. x12 = grok = {L3.1-70B: 1, Qwen72B: 1}. Both are in the roster |
| 12 | merged overdispersion by model p 0.0005, by anchor 0.0465 | CONFIRMED, with MC precision added | review_stats.py (20,000 permutations, own RNG); review_within_anchor.py | χ² 53.40 / 20 models; 22.34 / 14 anchors (to the digit). p model < 5e-5 (0 / 20,000); the printed 0.0005 is the floor (1+0)/(1+2000). Within-anchor null p 0.0001. p anchor 0.0380 (SE 0.0014) vs recorded 0.0465 (SE ≈ 0.0047 at 2,000): consistent, and it sits close to 0.05 |
| 13 | grok / x12 overdispersion (not claimed; recomputed) | CONFIRMED | same | grok 20 / 809, χ² 15.87 / 11.99, p 0.0827 / 0.5021 (recorded 0.0775 / 0.5097), DEFF 0.945. x12 26 / 809, χ² 15.40 / 12.52, p 0.0920 / 0.4513 (recorded 0.0935 / 0.4673), DEFF 0.994. merged DEFF 1.780, n_eff 1241.9: to the digit |
| 14 | nu: P reading outside every CI | CONFIRMED on merged; the grok arm is ABSENT | G22_nu.txt; OLS on the printed medians (a sanity check) | Recorded exponents +1.879 / +1.992 / +1.876 / +2.019, CIs [1.780, 2.159]. My median-OLS gives 1.85 / 1.90 / 1.86 / 2.04. argv `--leg nu` (default board merged): no grok_calib run (N1) |
| 15 | Coverage 2 of 14 | CONFIRMED | review_coverage.py (own modal category, own D_c) | 14 D_c values equal to 4 decimals. PASS: other 0.9597 and psychology 0.9802. health 0.9496 and law 0.9443 sit just under the bar. Top tier gemini-3.1-pro_5-shots alone in all 14 (gap to the next 0.043-0.157 ≥ 0.017) |
| 16 | v1 validity FAIL (random misses f_raw_wrong, f_loao_called, u_raw_wrong, u_loao_called; fixed misses u_raw_wrong; retest passes) | CONFIRMED, GENUINE | G22_validity.txt quantile rows; json `modes_ok` {random False, fixed False, retest True}, `status` FAIL; partial replay (below) | See "v1 FAIL: genuine?" below |
| 17 | Denominators | CONFIRMED | review_stats.py; sqlite counts | grok 9,142 rows / 9,131 valid / 2,811 judged q; x12 9,142 valid; merged 21,536 valid (= the board of record x12 + x20, NOT the sparse x20 alone) / 2,811 judged q; Kotlin 9,123 rows / 9,106 valid / 2,801 q. Established on each anchor's JUDGED questions (809 / 809 / 2,210) |
| 18 | Read-only | CONFIRMED | `sha256sum -c` before / after my runs on grok_calib, x12all, x20, kotlin (4 / 4 OK); size, mtime and -wal of eval and snapshots unchanged (-wal 0 B) | no write |

### v1 FAIL: genuine?

- **Target is right.** The 12 count targets equal the grok record, recomputed by my own code (row 5). The 2 ddev targets are grok 4.47 and Kotlin 2.26, which is a mixed pair (LOW, V-c). Both are covered in every mode anyway, so neither moves the verdict.
- **Interval rule is right.** T = 14 gives 1 - 0.05/14 = 0.996429, quantiles 0.00179 / 0.99821 (code `bonferroni_level`, `covered`). This is the registered ruling (1).
- **D9 does not apply to the deciding misses.** `pct = P(v < t) + ½P(v = t)`; `'%.3f' % 0.0005 = '0.001'`, `'%.3f' % 0.9995 = '1.000'`:
  - f_raw_wrong pct 0.000 → 0 of 1,000 replicates ≤ 7.
  - u_raw_wrong 0.000 → 0 ≤ 8.
  - f_loao_called 1.000 → 0 > 667 (at most 1 equal).
  - u_loao_called 1.000 → 0 > 653.

  The targets lie outside the simulated range itself, so ANY order statistic, and even [min, max], fails.
- **Partial replay at the recorded streams.** `replay_validity_subset.py` rebuilds validity_leg's context from arch4381 and evaluates rep0000-rep0039 through `g22._validity_rep`, so these are the recorded replicates:
  - vm digest ea25e7fd…, the same as printed.
  - r_keep 0.77324, the same.
  - random rep0000 f_raw_wrong = 181 (the READY's R = 1 figure).
  - random, 40 reps: f_raw_wrong min 65 / median 224 / max 402; f_loao_called 0 / 16.5 / 292.
  - fixed, 40 reps: f_raw_wrong 8 / 12 / 17; u_raw_wrong 9 / 15 / 19.

  Consistent with the printed medians (222.5; 12; 15).
- **Mechanism.** The fresh-judge mode redraws v_m ~ N(0, 1.2528²) with no link to quality. Ruling 1 (ii) (83f431b) already records this: v_m vs keyacc Pearson 0.966 (DEV). Fresh judges then order about a third of the called edges the wrong way, the refitted widener widens, and LOAO calls about 6 edges. This is a genuine FAIL of the simulator AS REGISTERED. Its cause is the registered mode's specification, not an artefact.
- **The fixed-mode miss IS D9-territory.** u_raw_wrong target 8 against q_lo 8.78 and pct 0.001 means 1-2 replicates at or below 8. It decides nothing (primary = random). But the fixed mode sits HIGH on raw wrong for both f (pct 0.006) and u (pct 0.001): the fitted judge still produces about 1.7-1.9× the observed raw wrong calls. That is a direction, not a tail artefact, and it matters for v2's fixed/retest prints.

## Predictions P1-P7 (G22) and P1-P3 (G23), mapped to readings

| pred | registered | reading (file:line) | score |
|---|---|---|---|
| G22 P1 | (a) PASS (0.7) | G22_validity.txt "VALIDITY LEG: FAIL" | **FAILED** |
| G22 P2 | (b) exponent 1.06 [0.80, 1.30] | G22_nu.txt, 4 exponent lines: +1.879 [1.801, 1.953], +1.992 [1.893, 2.100], +1.876 [1.780, 1.978], +2.019 [1.889, 2.159] | **FAILED** (merged only; the grok arm is not of record, N1) |
| G22 P3 | (c) P(nominal ≥ 9) per design | not run (the validity gate refused; v2 pending) | NOT SCORED |
| G22 P4 | (d) 0.85 | not run | NOT SCORED |
| G22 P5 | (e) 0.03 | not run | NOT SCORED |
| G22 P6 | (h) 14 of 14 [12, 14] | G22_coverage.txt "anchors at or above the bar: 2 of 14" | **FAILED** |
| G22 P7 | (f) residue = Meta-Llama-3_1-70B-Instruct, inside the roster | G22_overdispersion.txt, P7 block | **HELD under the 97f3a1f post-data rule** (identity on merged, unique top 4 / 4). Roster clause OK on all 3 boards, so the falsifier did NOT fire. Pre-data reading (b) "unique top on every board": no. Reading (a): yes |
| G23 P1 | (a) HELD (0.9) | G23_identity.txt "IDENTITY LEG: PASS" | **HELD** |
| G23 P2 | B utility 0.70 [0.60, 0.85], LOAO wrong(est) ≤ A's | G23_certab.txt: 69.2% / 69.3%; 1 ≤ 1 on both draws | **HELD** |
| G23 P3 | cross-draw stability 0.90 [0.80, 0.97] | G23_certab.txt: A Jaccard 0.941, B 0.938 | **HELD**. The statistic is not defined in the registration. Jaccard is the stricter reading; share-of-common-edges agreement for A is ≈ 0.956 by arithmetic from 653 / 661 / J 0.941. Both are inside |
| G22 falsifier (a) | FAIL overturns the simulator | v1 FAIL | **FIRED**. The v2 amendment (83f431b ruling 1 (ii)) is post-hoc and one shot |
| G22 falsifiers (c), (e) | | not run | not reached |
| G23 falsifiers (a), (b) | | identity HELD; B not raising wrong(est), ≥ 60% | not fired |

## Builder check (exact where required)

- G22 (f) and P7 use the EXACT builder: "builder: EXACT … the edge objects of record" is printed for all 3 boards, and argv has `--builder exact`. F1 is satisfied.
- G23 identity, certab, holm and residue print "builder EXACT (build()'s loop, Random(42), rj.mm_fit)". The residue precondition line reads "REPRODUCED KTD-CHECK: called 1714 / 4(4) -> MET".
- The fast builder is used by the validity replicates (by design; the targets are the hard-coded exact integers, and the fast real board 740 / 8 is printed beside only), by nu (floor 0), by mcstreams (5 independent streams) and by the conjuncts' length/order boards. None of these is a place where the registration or a ruling demands the exact builder. Ruling 1 (iii)'s "builder of record" binds v2's H2 targets only.

## Defects

- **V-a (MEDIUM, disclosure):** the per-replicate statistics are not stored. The `.validity.json` holds only the fit, the targets and the fast-builder real board. The `.streams.tsv` holds only seeds. So the verdict cannot be recomputed from the record without a re-run. Here it is decided by pct 0.000 / 1.000, which needs no replicate values, but a tail verdict would not be auditable. The same holds at 17a93c7 for v2 (`grep write_once` shows only the token json), which is running now. Fix: write `<out>.reps.tsv` (mode, rep, 13 statistics). For the running v2, the post-run review must re-run any target whose pct is within 0.01 of an end, or the outcome must state it is unauditable at the tail.
- **V-b (LOW):** the json key `real` holds the FAST-builder re-draw (740 / 8, 666, 747 / 9), not the record's integers (733 / 7, 667, 740 / 8). Label it `real_fast_redraw`.
- **V-c (LOW):** the ddev targets mix boards (4.47 grok, 2.26 Kotlin) against a grok-fitted simulator. The verdict does not move; the outcome should say so.
- **N1 (MEDIUM):** the registration's (b) names "k ≤ 12 on grok_calib" beside merged. The record run is `--leg nu` with the default board (merged) only. The provisional grok exponents (1.65-2.33, rulings L15336) are DEV and not of record. Fix: run `--leg nu --board grok` as a record run, or record the omission. P2 is FAILED either way.
- **N2 (LOW):** nu's nominal uses the unshipped Mistral 920 pair (-3.0438 / +3.1980). Ruling B leaves "the key-blind frozen pair of the designs and stop legs" untouched, so this is allowed, but say so in the outcome.
- **C1 (LOW-MEDIUM):** the registered (h) lists three readings: D_c, the key-tier band, and "A on the EVAL side". The third is not implemented (`coverage_leg`, `key_tier_lines`; `grep` finds no A in G22_coverage.txt). D_c is read over ALL questions of each category, not the EVAL side (a disclosed builder limit, and the split is not drawn: C4 is open). Record it as NOT PRINTED.
- **O1 (LOW):** "by model p 0.0005" is the permutation floor at 2,000 permutations (0 exceedances). Write "p ≤ 0.0005 (0 / 2,000)".
- **O2 (LOW):** "by anchor p 0.0465" carries a Monte-Carlo SE of about 0.005; my 20,000-permutation value is 0.0380. Print the MC interval beside any p read against 0.05.
- **O3 (MEDIUM, wording):** P7's HELD rests on a scoring rule chosen after the DEV residue sets were seen (97f3a1f, declared). The sentence of record must carry "under the post-data ruling" and reading (b) = no.
- **O4 (LOW):**
  - grok's anchor-clustered ICC is negative (-0.0010), so DEFF 0.945 and n_eff 856.5 > N 809. Floor DEFF at 1 for any planning use.
  - The provisional "DEFF 1.897" (rulings L15336) is superseded by the exact-builder 1.780. Cite 1.780.
- **R1 (LOW):** in G23_residue_merged.txt the per-edge "Mistral-merged called yes/no" column is certificate A's LOAO refit (`g23.residue_leg` L387-L390). It is not the certificate of record that defines the residue: 3 of the 4 residue edges print "called no". Label the column. The summary "a second judge buys nothing on the residue" rests on 2 shared edges. It is DESCRIPTIVE and must not be generalised.

## What this review does not show

- A full independent re-run of v1 validity. Only rep0000-rep0039 of random and fixed were replayed. The FAIL is decided by the printed pct at the ends of the empirical range.
- The fixed-mode u_raw_wrong miss at other seeds (it is a D9 tail event; it decides nothing).
- conjuncts, mcstreams and the Kotlin certab draw recomputed with independent code. They were re-run through the instrument only (byte-identical).
- Any rate-leg reading (c), (d), (e), (g), or anything about v2, which is running now at 17a93c7 and was not touched.
- nu on grok_calib (not run of record).
- Coverage on an EVAL side: no split is drawn. D_c here is over all questions of each category.
- Any claim that the simulator is valid in any mode. retest passing reproduces verdicts it partly keeps. It is not a fresh-judge validation.
- Anything about content-closed splits: bareq512_s42 is id-disjoint only.
