# POSTRUN review: BZ-METER v2 (meter_v2, [R18]), 2026-10-12

Reviewer: adversarial-reviewer. Authority: author_decisions/2026-10-12.md D-2026-10-12-1. Reviewed objects: benchzoom
9a42c49 (HEAD; the brief's "master e1fb080" is two commits behind, and 0 commits / 0 diff lines follow 9a42c49);
outputs `E:/benchzoom_demo/meter_v2`; operator logs `E:/TaxoArena_backup_20261012_bz_meter_v2/operator_logs/`. Prior:
READY_BZ-METER-R18.md (82371943, READY; code unchanged since, so no code re-review), POSTRUN_BZ-METER-v1.md. Zero LLM calls.

## Verdict: VALID; has results. State READ: all three harness/calibration gates passed, every level word exists.

The registration [R18] was committed before every v2 output. The vault was opened once, in one `--vault` process.
I recomputed every deciding number from the vault matrices with my own log-loss, cluster-SE, DEFF, q95 and word code,
using the library chain only to produce the predictions. All of them agree to the printed digit. All 20 harness draws
per dataset match to 6 dp, and so do 10 slope-null replicates (diffs below 2e-14). Every word, the depth, the slope
word and the 10 P-lines follow mechanically from the registered rules. Four findings are wording or provenance
items (MEDIUM/LOW). None of them changes a verdict.

## Per-claim table (deciding claims; mine = own script, cmd A)

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | [R18] precedes outputs | CONFIRMED | 9a42c49 05:51:27; first v2 output calibration_synthetic/null/meta.json 06:06:25; vault meta.json 07:16:14. All 4 metas (null, planted, work, vault): commit 9a42c49, dirty "", reg_blob 5c457088 = REG_BLOB = `git rev-parse 9a42c49:docs/meter_registration.md` = `hash-object` = `hash-object --no-filters` (LF; no CRLF rendering differs). Runner de240f4a, meter.py f31973af: same three-way match | - |
| 2 | Exactly one v2 vault read | CONFIRMED | vault.log: 1 launch line (`grep -c 'registration meter_registration'` = 1), 2 `vault opened (reads=1)` (one per dataset), 0 `reused`/`resume` lines. So harness, nulls and real labels all ran in that one process. Order in code (L536-610) and mtimes: harness 07:19 < nulls 07:27/07:41 < slope nulls 08:28/08:40 < outcome 08:50 | - |
| 3 | v1 untouched; vault sums | CONFIRMED | meter_v1/outcome.json af1f8042 (pinned); `v1_record_ok()` True; vault 31c111e3/4bcd0baf; 17 sha lines (vault, meter_v1, meter_v2 json) identical before and after my run (cmd C) | - |
| 4 | Gates before --vault | CONFIRMED | `calibration_meta_ok` (True, []); gate.txt PASSED; the 3 calibration outcomes are state READ with rule "[R18] one-sided, K draws"; fixture == SYNTH_FIXTURES for null and planted | - |
| 5 | MATH harness PASSED | CONFIRMED to digit | G-bar -0.000484 SE 0.001530 (mean part: -0.0005 > +0.0031? no); 0 of 20 draws > +2 own SE (c = 2); tau2 = 0 in 9; draw 0 -0.016671 / 0.007491. All 20 draws match the stored (tau2, G, SE) | - |
| 6 | MMLU-Pro harness PASSED | CONFIRMED to digit | G-bar -0.005651 SE 0.001963; 0 of 20 exceed; tau2 = 0 in 16; largest draw +0.002295 SE 0.006859 | - |
| 7 | Slope MATH | CONFIRMED | g +4.933846 SE 0.340620 z 14.5; DEFF 1.3285 n_eff 1475.3 (n 1960, 1960 singleton clusters, 135,240 cells); MDE80 1.308; null q95 +0.546960 (200/200 finite, mean +0.405, max +0.668) | - |
| 8 | Slope MMLU-Pro | CONFIRMED | g +8.927162 SE 0.476970 z 18.7; DEFF 1.2147 n_eff 3831.4 (n 4654, 4625 clusters, 107,042 cells); MDE80 1.832; null q95 +0.234005 (max +0.404) | - |
| 9 | SLOPE FIX HELD (both); 22-model HELD (sec.) | CONFIRMED | both g >= 3 SE, >= 0.10, > q95; 22-model g +12.241878 SE 0.811772 > q95 +1.936797 | - |
| 10 | MATH L1\|L0, L2\|L1, L3k\|C SUPPORTED | CONFIRMED | +1.129271 (0.121685, q95 .004721, DEFF .957, n_eff 2049, z 9.28); +0.452311 (0.067668, .005111, .885, 2215, z 6.68); +0.394054 (0.084096, .002873, 1.000, 1960, z 4.69) | - |
| 11 | MATH L3t\|L2 NOT SUPPORTED | CONFIRMED | +0.057702 SE 0.011098; g + 2 SE = 0.0799 < 0.10, so rule (2) applies (before BELOW INTEREST, [R2]). z 5.20, g > null max .0123: see F1 | - |
| 12 | MMLU-Pro L1\|L0, L2\|L1 SUPPORTED | CONFIRMED | +2.219849 (0.210000, q95 0, DEFF 1.220, n_eff 3816, z 10.6); +1.264789 (0.203104, .004510, 1.290, 3607, z 6.23) | - |
| 13 | MMLU-Pro L3t\|L2 DEGENERATE | CONFIRMED | WORK tau2 fk/L3t = 0 selected (chain tau2 identical to outcome's); g = SE = 0 | - |
| 14 | MMLU-Pro L3k\|C INCONCLUSIVE | CONFIRMED | +0.042113 SE 0.049534 (z 0.85; DEFF 1.125, n_eff 4136, MDE80 0.190 > delta_min): no rule (2)/(3) applies. See F3 | - |
| 15 | Depth MATH L3 (L3k), MMLU-Pro L2 | CONFIRMED | [R4] from rows 10-14 | - |
| 16 | 10 P-lines: 9 HELD, P4 MATH NOT HELD; falsifiers not fired | CONFIRMED | P4 MATH word right, g 0.058 > hi 0.056. P2/P3/P5 falsifiers need NOT SUPPORTED / SUPPORTED words that did not occur. Backbone trigger: S2PL-L0 and S3PL_L0-L0 are below 3 SE on both datasets | - |
| 17 | Label-null q95 | CONFIRMED (q95), spot (draws) | all q95 recomputed from the 200 stored values (numpy linear) to 6 dp; per-permutation re-derivation is a spot check of 14 permutations; 13 of them hit tau2 = 0 (vacuous). The one non-vacuous case, MMLU L3k r0 (+0.00433317, tau .005), matches. Every non-degenerate real g is above the null MAXIMUM, so the null's precision cannot move a word | - |
| 18 | meter_v2 SHA256SUMS OK; backup 44 files | CONFIRMED | `sha256sum -c` 11/11 OK; backup 44 lines, 0 non-OK; `diff -rq` 0 lines | - |

Secondary words, recomputed and all matching outcome.txt: MATH L3t|L1 NOT SUPPORTED, L3k|L1 / L2a|L1 / L2|L0 SUPPORTED;
22-model all 8 SUPPORTED (incl. L3t|L2 +0.175917 SE 0.034252); MMLU-Pro L3t|L1 NOT SUPPORTED, L3k|L1, L2|L0 SUPPORTED.

## Plain-language summary (vault of record; x 1e-3 nats per model x item cell)

**MATH (69 models, 1,960 vault items).**
- *Difficulty slope:* letting each model's accuracy fall off with difficulty at its own rate predicts held-out
  answers better (+4.93). That is about 9x what a no-slope model produces by chance (q95 +0.55). It is a measurement
  fix only. v_j is not a model's "sensitivity to difficulty" ([R17]/[R18] wording binds).
- *L1 subject:* real and clear (+1.13).
- *L2 subject x level:* adds more (+0.45). `level` is the benchmark's own difficulty annotation.
- *L3t tree leaves:* a tiny gain is detected (+0.058, about 5 SE), but it is smaller than the registered gain of
  interest (0.10), which it rules out. Word: NOT SUPPORTED. This means "too small to matter", not "zero".
- *L3k text neighbourhoods over the difficulty/length control:* real (+0.39). The finest level these data can see
  is L3 (text neighbourhoods).

**MMLU-Pro (23 models, 4,654 vault items).**
- *Slope:* held-out fix (+8.93, null q95 +0.23). Same wording limits as MATH.
- *L1 category* (+2.22) and *L2 category x source* (+1.26): both real. L2 is the value of the source-and-subject
  annotation ([R9]), never "finer subject" alone.
- *L3t leaves:* not measurable. The WORK data chose no leaf effect (DEGENERATE).
- *L3k text over control:* undecided (+0.04 ± 0.05). The test could not detect the gain of interest at this support
  (MDE80 0.19). The finest level is L2.

## Defects

- **F1 MEDIUM (post wording; binds the registrar's outcome and any article).** MATH L3t|L2 is NOT SUPPORTED by
  rule (2) (g + 2 SE < delta_min), yet the gain is detected (z 5.20, above all 200 null values). The 22-model
  secondary line is SUPPORTED (+0.176). Fix: write "a detectable gain below the gain of interest (0.058 ± 0.011;
  excludes 0.10)". Never write "leaves add nothing". The 22-model SUPPORTED stays secondary and does not set depth ([R5]).
- **F2 LOW.** P6 (22-model, secondary, [R16] ranges) is not in the runner's `PREDICTIONS`, so the operator record does
  not score it. Scored by me: all 5 g are in range (slope 12.24 in 8.9-13.5; L1 3.34; L2 1.39; L3k|C 1.23; L3t|L2
  0.176 in -0.05-0.18). Words: 4 held; L3t|L2 SUPPORTED (secondary) against predicted INCONCLUSIVE, so NOT HELD
  (secondary). Fix: the registrar records P6 with this miss (insertion), and a future runner scores P6.
- **F3 LOW (wording).** MMLU-Pro L3k|C INCONCLUSIVE was underpowered by registration (MDE80 0.190 > 0.10; [R16] P5
  predicted it). Fix: the post says "undecided at this support", never "no text signal on MMLU-Pro".
- **F4 LOW (provenance).** `calibration_work/SHA256SUMS` lists 4 of its 12 files: on resume, reused files are not
  re-listed. The 5 reused files' sha256 (harness bdbf2bee, meta 0440f58d, nulls 64aeda08/8cc3bda7, slope a9f82f53)
  equal the shas in cal_work2.log, which I checked (cmd B). The vault directory is unaffected (no resume there).
  Fix: on resume, append the reused files' lines, or write SHA256SUMS over the whole directory at the end.
- **Process deviation (operator):** the killed first `--calibrate work` stopped on a time limit, not a crash. The
  resume was the reviewed meta-match path. It touched only the WORK pseudo-vault (a dress rehearsal), not the vault.
  Accepted.
- **Reviewer disclosure.** Cmd A opened the vault matrices in memory, once per dataset, in a scratch process. It wrote
  nothing outside the scratchpad and recomputed only registered statistics that were already published in
  outcome.json. Vault, meter_v1 and meter_v2 hashes were unchanged (cmd C). benchzoom porcelain stayed at 0.

## Author decisions: none new. The [R17]/[R18] slope wording and F1/F3 bind the post.

## Commands (benchzoom, read-only; scripts in the session scratchpad)
```
git log -3 --format='%h %ci %s'; git rev-parse 9a42c49:<f>; git hash-object <f>; git hash-object --no-filters <f>   (reg, runner, meter.py)
ls -la --time-style=full-iso meter_v2 meter_v2/*/ ; grep -c 'registration meter_registration' vault.log (1); grep -c 'reused\|resume' vault.log (0)
A: recompute_v2.py 5 -> load_dataset (pins), guard.open once/ds, M.chain(cv); own ll (clip 1e-6), item means, CR1 cluster SE,
   cell-iid SE, DEFF, n_eff; q95 = np.percentile(stored nulls, 95); own level/slope words; 20 harness draws via M._restep +
   own G-bar/SE/rule; slope-null r 0-4 own Y* + M.backbone; label-null spot (L3k r0,r1; L1 r0; L3t r0)  (MATH 185 s, MMLU 103 s)
B: sha256sum -c meter_v2/SHA256SUMS (11 OK); calibration_* SHA256SUMS (0 non-OK); sha256 of 5 reused calibration_work files
   vs cal_work2.log; backup sha256sum -c (0 non-OK, 44 lines); diff -rq meter_v2 backup/meter_v2 | wc -l (0)
C: sha256sum vault/*.json meter_v1/* meter_v2/*.json before/after A | diff (identical, 17 lines); git status --porcelain | wc -l (0)
python: T.calibration_meta_ok(out) (True, []); T.v1_record_ok() True; meta fixture == SYNTH_FIXTURES (True, True)
```
