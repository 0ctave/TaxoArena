# POST-RUN review: FLAT-MIX-MMLU (run from main 346ea3b, flat_mix_mmlu.py blob:c5cc7934 / sha256-lf16:70666bb7c751fd54; adversarial reviewer, 2026-09-26; zero calls, read-only)

## VERDICT: VALID

The outcome of record reproduces to every printed digit from the 13 state files and the pinned inputs. I recomputed it with my own code; the only imports were `pool_guard` (id file, `open_ro`) and `split_side.stem_key`.

- **What the outcome says:**
  - C1 FAILED, C2 FAILED, L1 FIRES (on M1 AND on M2), reading **T-4**, F1 FIRES.
  - P1b, P2b, P4, P5, P6, P8 HELD.
  - P1a, P2a, P3, P7 FAILED.
- **The loss is robust across the V seeds.** T is below EVERY V seed and EVERY K seed on purity. On key information it is below every V seed.
  - Against the worst V seed on purity, the difference is still negative with a CI below zero.
  - The large spread_V comes from local optima of the partition, NOT from the non-converged EM. Continuing each seed's EM to convergence moves M1 by at most 0.0020.
- **Two things must be carried with it:**
  - The registered T-4 sentence names a mechanism ("the size floor and the greedy cuts") that this test does not identify. The reported-only anchored control O ties V0 (section 4).
  - The C2 SE was transported, and it is 19% optimistic (R7).

Outputs of record: untracked, LF, 0 CR, write-once.

| file | sha256 | blob (LF) |
|---|---|---|
| experiment_results/flat_mix_mmlu/flat_mix_mmlu_outcome.txt | 8a85ffb27511de8f... | 9841da6c |
| flat_mix_mmlu_arms.csv | 9f1baca45ba8ea5e... | 6def22c5 |

State: 13 files. Every part carries script blob c5cc7934. The per-file sha256-16 values are listed in the scratchpad `rev_mix\post_flat.log`.

**Order deviation.** FLAT ran before MIX, against R6 of READY dde660e, by the orchestrator's ruling. This is ACCEPTED as immaterial:
- the two instruments share no state;
- both are read-only on the same pinned tables, and the pins are equal before and after (below);
- R4 `--identity-check` printed REPRODUCED before `--run` (gmm_run\flat_identity.log).

## 1. Per-claim table

My script is `scratchpad\rev_mix\post_flat.py` and its log is `post_flat.log`. It ran single-threaded, as the only python process: I waited for the builder's MIX jobs to exit. CPU 79 s.

| # | claim (outcome) | result | mine | sev |
|---|---|---|---|---|
| 1 | fit set 8,125 distinct texts; 0 overlap with the 3,445 held-out | CONFIRMED | 8,125 ids = 8,125 distinct texts; exact overlap 0; stem_key overlap 0; fit set is a subset of train (8,125 of 8,324); 3,445 singleton stem_key groups, so the "twin-group" bootstrap is an iid question bootstrap and DEFF = 1 is measured | - |
| 2 | per-table pins unchanged | CONFIRMED | my pins taken before and after my recompute are equal to each other and to the run log's before/after on all 6 tables. Snapshot graph 30f5274d7e203237; both jsonl 1b9bd34d / c73b1cc2 | - |
| 3 | M1 per arm (hits / 3,445, Wilson) | CONFIRMED, all 12 to the hit | T 2504, O 2653, V0 2652, V1 2647, V2 2559, V3 2664, V4 2610, K0 2655, K1 2571, K2 2588, K3 2629, K4 2639. Majority-label ties: 2 cells in V2 and 1 in K4. My first-seen tie-break reproduces the counts | - |
| 4 | M2 per arm (x1000) | CONFIRMED to 3 decimals | +12.785 / +13.949 / +14.318 / +13.725 / +14.429 / +13.607 / +13.730 / +13.723 / +12.523 / +13.361 / +13.156 / +14.105 on 10,925 keyed questions, 46 models (keyed set and LOO re-implemented) | - |
| 5 | M3 per arm | CONFIRMED to 3 decimals | 0.786 / 0.847 / 0.845 / 0.808 / 0.870 / 0.846 / 0.889 / 0.842 / 0.791 / 0.850 / 0.859 / 0.845 (22 / 14 / 24 / 30 / 28 / 22 / 22 / 23 / 26 / 23 / 22 / 25 cells of >= 50). O rests on 14 cells | - |
| 6 | M4 per arm; T/K/O refit | CONFIRMED | 415.6267 ... 416.3118 to 4 decimals. My Banerjee refit of T, O and K0-K4 on the fit set equals the stored parameters (max abs dev: mu 1e-16, kappa 1e-15 relative, pi 0). No M4 VOID | - |
| 7 | spreads | CONFIRMED | spread_V: M1 0.0305, M2 0.822e-3, M4 0.8441. spread_K: M1 0.0244, M2 1.582e-3 | - |
| 8 | C1: T - V0 = -0.0430 [-0.0557, -0.0293] -> FAILED | CONFIRMED | same bootstrap (default_rng(20260926), 1000 resamples, [25] / [974]) gives -0.0430 [-0.0557, -0.0293] | - |
| 9 | C2: -1.534 [-2.230, -0.826] e-3 -> FAILED | CONFIRMED | F6's `boot_mean_ci` re-implemented (Random(42), 2000 resamples) gives -1.534 [-2.230, -0.826] | - |
| 10 | L1 FIRES (M1 yes, M2 yes) | CONFIRMED | M1: -0.0430 < -0.0305, CI hi -0.0293 < 0. M2: -1.534 < -0.822, CI hi -0.826 < 0. Margins beyond the spread: 0.0125 and 0.71e-3 | - |
| 11 | reading T-4; F1 FIRES (a LOSS) | CONFIRMED | L1 fired with C1 and C2 FAILED is T-4 by the registered table (L20705). B5 is not engaged | - |
| 12 | P1a-P8 | CONFIRMED (all 10 lines) | P1a -0.0430 outside [-0.025, +0.015]: FAILED. P1b HELD. P2a -1.534 outside [-1.0, +1.5]: FAILED. P2b HELD. P3 0.0305 outside [0.003, 0.020]: FAILED. P4 V0 416.98 > T 415.63: HELD. P5 \|0.7707 - 0.7698\| = 0.0009: HELD. P6 HELD. P7 T-4: FAILED. P8 T M1 0.727 [0.712, 0.741], M2 +12.785: HELD | - |
| 13 | K0 beside | CONFIRMED | M1 -0.0438 [-0.0569, -0.0287]; M2 -0.938 [-1.576, -0.288] e-3; M4 -0.8054 | - |
| 14 | M4 T - V0 = -1.3530 [-1.7164, -0.9475] (descriptive) | CONFIRMED | same | - |

Minor issue (LOW): `analyze()` computes the before-pins but prints only the after-pins (flat_analyze.log L17-L26). The equality was enforced by `check_pins_after` and holds by my independent pins. Printing both is the house rule; fix it in a later build.

## 2. R7: realised SE against the registered Support

| | registered | realised (T - V0) | consequence |
|---|---|---|---|
| C1 discordance | 0.20 (declared) | **0.1533** | - |
| C1 SE | 0.00762 | analytic sd/sqrt(n) **0.00663**; bootstrap CI/3.92 0.00674 | the registration was conservative by 13%; realised MDE 2.80 x 0.00663 = 0.0186 |
| C2 SE | 0.300e-3 (transported from a tree-vs-tree pair) | analytic **0.357e-3**; F6 CI/3.92 0.358e-3 | **optimistic by 19%**. The transport assumption failed as the registration warned (L20710): a tree-vs-flat pair disagrees more. Realised MDE 2.80 x 0.357 = 1.00e-3 against the registered 0.84e-3. The C2 loss (-1.534) still clears it |
| effective thresholds | max(MDE, spread_V) | C1: 0.0305 (bound by the seed spread, not the MDE); C2: 0.840 registered (0.822 spread) / 1.00 realised | the M1 loss clears the spread by 0.0125 = 1.9 realised SE; the M2 loss clears the realised MDE by 0.53e-3 |

## 3. The large spread_V (0.0305, about 4x the predicted 0.008)

**It is not EM non-convergence.**
- All five V seeds stopped at max_iter 200 unconverged (`converged` False; the tol 1e-6 on a mean log-likelihood near 420 is a 2e-9 relative tolerance). That is the registered stopping rule.
- DESCRIPTIVE: I continued each seed's EM from its saved state. All five then converged within 33-94 more iterations.
- The changes were small: M1 moved by at most 0.0020 (V2 0.7428 -> 0.7448), M2 by at most 0.16e-3, and the training log-likelihood by at most 0.037 nats.

**It is local optima of the partition at k = 82.**
- Pairwise ARI between V seeds on the fit set is 0.55-0.56; between K seeds 0.50; V0 vs K0 0.63.
- V2 is a distinctly lower-purity optimum (0.7428; the other four lie in 0.758-0.773).
- K shows the same behaviour (spread 0.0244, K1 0.7463).
- The registered comparator V0 has the LOWEST training likelihood of the five seeds (420.61) but the second-highest purity, so likelihood does not select purity here.
- Every V seed has one small MAP component: 3-13 fit texts, the smallest at pi 0.00037. This does not drive M1.

**Does V0's win survive another seed? YES (DESCRIPTIVE).**

| comparator | M1 T - V | 95% CI | M2 T - V (e-3) | 95% CI |
|---|---|---|---|---|
| V0 (of record) | -0.0430 | [-0.0557, -0.0293] | -1.534 | [-2.230, -0.826] |
| median seed by M1: V1 | -0.0415 | [-0.0546, -0.0279] | -0.941 | [-1.644, -0.246] |
| worst seed by M1: V2 | **-0.0160** | **[-0.0293, -0.0023]** | -1.644 | [-2.340, -0.888] |
| worst seed by M2: V3 | -0.0464 | [-0.0589, -0.0319] | **-0.822** | **[-1.452, -0.142]** |
| V4 | -0.0308 | [-0.0447, -0.0160] | -0.945 | [-1.609, -0.218] |

- T's M1 0.727 is below all 5 V seeds (min 0.743) and all 5 K seeds (min 0.746).
- T's M2 +12.785 is below all 5 V seeds (min +13.607) and 4 of 5 K seeds (K1 +12.523 is lower).
- Every paired CI in the table excludes 0 on the negative side.
- The spread leg is what made C1's L1 margin (0.0125) the binding question. Against the single worst seed the M1 loss shrinks to 1.6 pp, below the registered MDE of 2.1 pp. That is DESCRIPTIVE and does not change the scored L1, which is defined against V0 with the spread.

## 4. What the result licenses, and what it does not

**Licensed (the words of record, with their qualifiers):**
- "On MMLU-Pro, the content-closed anchor-free tree af_clean_s42 (82 leaves) is a WORSE partition of the held-out questions than a flat vMF mixture at the same k = 82: held-out purity -4.3 pp [-5.6, -2.9] and key-only F6 information -1.5 x1e-3 [-2.2, -0.8], each beyond the flat mixture's seed spread (L1 on both measures; reading T-4, a LIMITATION for the construction chapter's record)."
- Qualifiers carried every time:
  - (a) "held-out" = the 3,445 judgeable questions of p2dca21ab5f4ef3ae, **content-closed under stem_key at norm-v1**. Near-copies below norm-v1 exist: 37 of 3,445 (1.1%) have a fit text at cos >= 0.98 (steward 9073a8a).
  - (b) ONE tree (one build, seed 42), ONE flat comparator of record (V0), ONE corpus.
  - (c) F6 uses the 10,925 keyed questions of both sides (the F2-CLEAN caveat, for every arm alike).
  - (d) spread_V was 4x the prediction (P3 FAILED), so the purity threshold was bound by the seed spread.
- The TOPIC-PARTITION-20NG sentence ("its value ... is ... not the partition") transfers IN THE STRONGER FORM on this corpus: "not a better partition, and measurably a worse one". The talk may say: "on MMLU-Pro the hierarchy buys the certificate, the support per cell, the names and the routing discipline; its cells are a worse partition than a flat mixture at the same granularity".

**NOT licensed:**
1. **The T-4 mechanism clause** ("the size floor and the greedy cuts cost ..."). The test compares partitions and identifies no cause.
   - The reported-only anchored control O (o0_clean_s42, 84 leaves) ties V0 on purity (0.770 vs 0.770) and nearly on F6 (+13.949 vs +14.318).
   - O is the same-code control: its config.toml differs from T's only by the absence of `anchorFree = true` (plus headers and outputDir, by `diff`). So it has the same size floor (mcs 55) and the same greedy splitter.
   - So the data are at least as consistent with "the anchor-free construction costs partition quality" as with the registered mechanism.
   - O is REPORTED ONLY (L20690). That is a disclosure, not a sentence of record.
   - **Fix:** the registrar brackets the T-4 sentence, "mechanism not identified by this test; O (reported only) ties V0", and nothing in the talk states the mechanism.
2. That trees, or this construction, are worse partitions in general: no second tree seed, no second content-closed anchor-free tree, no second corpus.
3. Anything about routing, boards, judges, profiles or the frontier. The multi-corpus router result is not re-tested.
4. That V is a better TAXONOMY. It carries no certificate, names or support floor, and its M4 advantage (+1.35 nats) is by construction (M4 is descriptive).
5. Any comparison to K beyond "reported". Any statement about O versus T as a scored contrast.
6. A size for the loss sharper than the CIs above. Against the worst V seed the purity loss is 1.6 pp.

## 5. Conditions for the registrar

- **C-a:** record the outcome in the printed words, with the qualifiers (a)-(d) of section 4, the R7 realised-SE table, and the order deviation (ruled by the orchestrator; immaterial).
- **C-b:** bracket T-4's mechanism clause as not identified, with O disclosed beside it.
- **C-c:** record that the V EM stopped at max_iter on every seed. The descriptive continuation shows the result is insensitive to this: M1 changes by at most 0.0020, M2 by at most 0.16e-3.
- **C-d:** future C2 registrations use the realised tree-vs-flat SE 0.357e-3 (MDE 1.00e-3), not the transported 0.300e-3.
