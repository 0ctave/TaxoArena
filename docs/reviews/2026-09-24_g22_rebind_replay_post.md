# Post-run review: G22-REBIND-1 replay of validity-v2 (475da53)

Adversarial reviewer, 2026-09-24. Zero judge calls. Read-only, single process. Every figure below is recomputed from the committed files. The recorded output is experiment_results/archv2/g22_g23/G22_validity_v2.txt (e644a25) and its token; the replay is experiment_results/archv2/g22_g23/rebind/ (475da53). Script output: session scratchpad rev_ea/replay_post.txt.

## VERDICT

**REPLAY PASS CONFIRMED.** The re-binding may be recorded (ruling 1 (iii) of 56751fa) with this chain:
- old_lf16 **f37145df9516b7ec**
- new_lf16 **876d01413318bd7b**
- token_digest **3069666d0f5e553ad61bd9cb8f178e2771d6fd683f63f01b8b35435cf56cdfc0**
- replay_output_sha **3a410b9627c275fc81137fd24cdab91c11e17d3db82a499d20a4d8611e1b0822** (sha256 of the committed LF output)

**DEVIATION (the four extra files): RULED HARMLESS.** They are byte-identical to 74fc4f7, to main HEAD and to main's working tree. They are unchanged since the record run's commit 165ffb8. None is among the 11 hashed files. The two failed attempts printed no figure.

**D9 SETTLED ON THE STORED RECORDS.**
- Of the 24 deciding targets (random mode 12, H2 12), **23 sit clear of their Bonferroni tail**.
- **H2 u_raw_wrong** (target 3) is the single Monte-Carlo-undetermined row. 5 of 1,000 replicates are ≤ 3 (2 below, 3 at). The tail is 0.0050, Clopper-Pearson [0.0016, 0.0116], and it CONTAINS the per-side bar 0.05 / 24 = 0.00208.
- Coverage needs at least 4 replicates ≤ 3; the run had 5, a margin of ONE replicate.
- Estimated from the 1,000 runs, a fresh master would clear this row with probability about 0.74; with the true tail at the bar, about 0.16.
- The v2 PASS is **"PASS AT THE BOUNDARY, Monte-Carlo-fragile on one row"**, and the record should say so.

## Per-claim table

| # | claim | result | command / evidence | mine vs claimed |
|---|---|---|---|---|
| 1 | RP1: instrument_lf16 876d01413318bd7b | CONFIRMED | Console L1 "RP1 instrument_lf16 (extracted tree) = 876d01413318bd7b". The output's identity lines show g22.py blob:c21e0a33 / lf16 3d178b1bc6d7207d, archv2_g22_sim.py blob:72b01978 / fee6e27a207fbbea and selftest_g22_rebind.py blob:69d1e569. The run tree `scratchpad/rebind_run/tools/analysis` holds 206 files: 206 of 206 equal to `git ls-tree 74fc4f7 tools/analysis` after LF normalisation, 0 differ, no extra file (pycache excluded) | = |
| 2 | (a) the block is BYTE-IDENTICAL: 13,433 bytes, lf16 06039d95eff7b781 | CONFIRMED | My own extraction, independent of g22's (start marker to the first stop prefix). Recorded: lines 28-134, 107 lines, 13,433 bytes, lf16 06039d95eff7b781. Replay: lines 28-134 identical line for line; its L135 is one EMPTY line (the `say("")` before the REPLAY lines), which the registered extraction strips (`rstrip`). Same bytes, same lf16 | = (the one trailing blank line is the only difference, and the registered rule strips it) |
| 3 | (a) the board line is EQUAL | CONFIRMED | 1 line in each: "board grok: 9131 valid verdicts, 9131 routed, anchors 14, models 12; … snapshot 20260909_212117_Headless_Run_Auto_ge…" | = |
| 4 | (b) streams 58,039 / 0791961e… EQUAL | CONFIRMED, stronger than printed | Beyond the printed lines, the FULL streams .tsv files are byte-identical: sha256 0791961ee6b76940… for both, 58,039 rows | = |
| 5 | (c) vm digest e9d78b8e… EQUAL | CONFIRMED | The token of record's vm_digest e9d78b8ea98638c6… equals my own sha256(json(verdict_model, sort_keys)) over the token's params, and equals the replay's printed digest. The token's token_digest recomputes (3069666d…); T 14, T2 12, coverage 0.996429, level2 0.995833 | = |
| 6 | Witness: 0 → 4,000 records; 48 lines recomputed, 0 missing | CONFIRMED independently | I recomputed all 48 quantile rows (random, fixed, retest × 12; H2 × 12) with `numpy.quantile` (default linear, i.e. type 7 inclusive) at the token's levels, formatted as the instrument prints. They are compared against the RECORDED file (not the replay): **48 / 48 byte-identical**. The 3 delta-deviance rows recompute and MATCH too. Manifest: 4 files × 1,000 records, sha256s as listed | = |
| 7 | ONE_SHOT and token untouched; no chain file written | CONFIRMED | ONE_SHOT.json mtime 11:31:42.475 (the record launch). `git diff --quiet HEAD` on the recorded output and its token: unchanged. `experiment_configs/` has 0 rebind files | = |
| 8 | RP2: replay_output_sha = sha256 of the committed LF output | CONFIRMED | `git show 475da53:…/G22_validity_v2_REPLAY.txt \| sha256sum` = 3a410b9627c275fc81137fd24cdab91c11e17d3db82a499d20a4d8611e1b0822 = the working file's sha; 0 CR bytes in the file (LF) | = |
| 9 | The four extra files are byte-identical to main | CONFIRMED | For TaxonomyArenaService.kt, reserved_pools.json, reserved_pool_frozen_p2dca.json and reserved_pool_frozen_paeec.json, the run-tree copy equals 74fc4f7, main HEAD and main's working tree, both raw and LF-normalised (lf16 7a67c263…, a244db4e…, da113869…, 57e81105…). `git diff --stat 165ffb8 HEAD` over the four paths is EMPTY | = |

### Ruling on the deviation (the extra files and two failed attempts)

The record run of e644a25 ran from main at 165ffb8, whose tree held these four files at the same bytes (item 9). So the replay's inputs equal the record run's inputs.
- `rejudge_grok` reads TaxonomyArenaService.kt at import, for prompt constants the simulator does not use.
- `pool_guard` reads the three pool files to verify p2dca21ab5f4ef3ae. That is a check, not an input to any computation, and it printed PASSED.

The proof conditions (a), (b) and (c) are unaffected, and so are the 11 hashed files. The two failed attempts (scratchpad incident1/) died at import or at the pool guard. Their consoles have 19 and 25 lines, with **0** figure lines (VERDICT MODEL, table rows, PART A, [RECORDS]), so nothing was computed or seen. The rule-7 proclist records one admitted `-O` selftest process and a PID killed with the author's approval. **No effect on the proof.** The record should keep the incident consoles and name the four files in the chain entry as "run-tree support files, byte-identical to main (not hashed)".

## D9 on the stored per-replicate records (closes aec0a55's replay-denied gap)

Rule: a target is covered iff it lies within the type-7 quantiles at q = (1 − level) / 2 and 1 − q. Part A: level 0.99643, q 0.00179, h = 999·q = 1.784. H2: level 0.99583, q 0.00208, h = 2.081. The empirical one-sided tail is min(#≤t, #≥t) / 1,000 with a Clopper-Pearson 95% interval, read against the per-side bar α / (2T).

**H2 u_raw_wrong (target 3; the recorded q_lo 3.00):**
- lowest order statistics: 1, 2, **3, 3, 3**, 4, …
- #<3: 2; #≤3: 5; #≥3: 998
- tail 5 / 1,000 = 0.0050, CP [0.0016, 0.0116] ∋ 0.00208 → **MC-UNDETERMINED**
- q_lo = s(3) + 0.081·(s(4) − s(3)) = 3 + 0.081·0 = 3.00, so the target is covered AT THE EDGE
- with one replicate fewer at ≤ 3 (1, 2, 3, 4, …), q_lo = 3.081 and the target is NOT covered (part B and v2 FAIL)
- P(at least 4 of 1,000 at ≤ 3): 0.736 at p = 0.005 (the point estimate); 0.157 at p = 0.00208 (the bar); 0.079 at the CP lower end

**Every other deciding target is clear** (its CP interval lies wholly above the bar). The nearest:

| row | target | tail | CP 95% |
|---|---|---|---|
| H2 f_raw_wrong | 3 | #≤3 = 20 / 1,000 (0.0200) | [0.0123, 0.0307] |
| H2 f_loao_called | 500 | #≥500 = 22 (0.0220) | [0.0138, 0.0331] |
| H2 u_loao_called | 490 | #≥490 = 20 (0.0200) | [0.0123, 0.0307] |
| random u_raw_wrong | 8 | #≤8 = 29 (0.0290) | [0.0195, 0.0414] |
| random u_raw_called | 740 | #≤740 = 42 (0.0420) | [0.0304, 0.0564] |

The H2 zero-count targets (f_loao_wrong, u_loao_wrong, *_est) are covered by the mass at 0: 66 / 76 / 716 / 762 replicates at 0.

The fixed and retest modes decide nothing. For the record, fixed-mode f_raw_called (733 < min 737), u_raw_called (740 < 746.78) and u_raw_wrong (8; #≤8 = 1) lie outside their intervals.

**Reading for the record.** v2's PASS stands as registered: the rule is the rule, and the recorded interval covers. Its Monte-Carlo fragility is now MEASURED rather than asserted. One of 24 rows is undetermined at R = 1,000, and it passes by one replicate. The chip "PASS AT THE BOUNDARY (D9 realised on H2 u_raw_wrong)" is exact. Ruling 2's admissibility wording ("passed at the boundary … NOT CENTRED") applies unchanged to every downstream reading.

## Defects

- **P1 (LOW):** the replay's streams file `rebind/G22_validity_v2_REPLAY.txt.streams.tsv` is untracked (`git status`: `??`), while the recorded run's is tracked. It is byte-identical to the tracked one (sha 0791961e…). Commit it, or state in the record that it is identical.
- **P2 (LOW, wording):** "BYTE-IDENTICAL" for (a) holds under the registered extraction, which strips one trailing blank line in the replay. Say so in the chain entry.

## What this does not show

- Anything beyond validity-v2's determinism and the re-binding. Designs and stop are still unrun and carry ruling 2's labels.
- The PASS probability under another master: the ~0.74 figure is a plug-in estimate from one run's tail, not a registered quantity.
- The v1 validity outcome, which is recorded separately.
