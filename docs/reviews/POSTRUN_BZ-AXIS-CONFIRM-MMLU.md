REVIEW: POSTRUN
REGISTRATION: BZ-AXIS-CONFIRM-MMLU
VERDICT: OUTCOME CONFIRMED

# Post-run review: BZ-AXIS-CONFIRM-MMLU vault read (one read, 2026-10-22 10:45-11:09)

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena `_as_of 1d23bf32`; benchzoom dfeb0aa (porcelain 0 before and after).
Zero LLM calls; no second `vault` invocation. Recomputation = my own scripts in E:/TaxoArena_tmp/postrun_mmlu_vault
(`recompute.py`, `probe2.py`): they import the pinned loaders (`load_real`, every pin asserted), refit the chain in memory
and compute g / SE / DEFF / words with their own log-loss and cluster-SE code. Nothing written under E:/benchzoom_demo,
E:/benchzoom_cache or the benchzoom checkout: a `find -printf '%T@ %s %p'` snapshot of both trees, 338 files, is identical
before and after (`diff | wc -l` = 0); `sha256sum -c SHA256SUMS_vault` 7 / 7 OK after.

## Verdict

**OUTCOME CONFIRMED.** Every deciding and secondary number reproduces to the printed digit. The words follow [R2]. V1-V4
of READY-2 held; V4's wording is owed by the registrar (D2). No artefact found inflates the gains beyond the
known L2 re-read (D1), which accounts for about a quarter of C-M1 and has to be quoted beside it.

## Per-claim table

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | V1 code state | log L1: dfeb0aa, src c9809e98, runner aec30584, porcelain 0; `git rev-parse HEAD HEAD:src/benchzoom HEAD:examples/axis_confirm_mmlu.py` today gives the same three | CONFIRMED | - |
| 2 | V3 inputs | log L2: `fetch3 86 OK 0 FAILED 10:45:20`, before the read; `load_real` re-asserted every PIN in my runs (no refusal) | CONFIRMED | - |
| 3 | V2 tau^2 = [A1] exactly | log L4 readers and meta.json `rosters.helm.tau2.readers` = {L3a .02, L3a1 .08, diff .16, len .005, L3ac .01, grp .04, L1g .08}; my refit on the full matrix gives the same dict (`== A1: True`); the chain dict also matches meta | CONFIRMED | - |
| 4 | V4 section untouched until done | `git log f6402011..HEAD -- docs/judge_v2_program.md` = 0 commits, the working tree equals HEAD; the run's own section-sha refusal passed | CONFIRMED | - |
| 5 | C-M1 g +0.1171 SE 0.0346 | own: g +0.117081, SE 0.034569, iid SE 0.024859, DEFF 1.9338, n 5,530, G 5,504, 436,870 cells; outcome.json +0.117081 / 0.034569 / 1.9338 | CONFIRMED (digit) | - |
| 6 | C-M1 Support: DEFF 1.934, n_eff 2860, MDE80 0.1327 | SE = sqrt(1.9338) x 0.024859 = 1.3906 x 0.024859 = 0.03457; n_eff = 5,530 / 1.9338 = 2,859.7; MDE80 = 3.84 x 0.034569 = 0.1327 (> 0.10); 3 SE = 0.1037 so g / SE = 3.39. Realised DEFF 1.934 sits inside the [A1] WORK range 1.881-2.044. The registered transport (DEFF 1.1257, SE 0.0167) understated SE 2.07x, as [A1] disclosed | CONFIRMED | LOW (D4) |
| 7 | C-M1 word SUPPORTED, DESCRIPTIVE-ONLY | my [R2]: tau^2 0.02 != 0; g > q95 0; g + 2 SE >= 0.10; g >= 3 SE (0.1171 >= 0.1037), g >= 0.10, so SUPPORTED. meta/outcome `descriptive_only` True; outcome.txt prints "its word SUPPORTED is printed and decides nothing" and no FAILS line | CONFIRMED | - |
| 8 | C-M2 +1.1688 SE 0.1228 SUPPORTED (secondary) | own +1.168761 / 0.122786, DEFF 2.2281, q95 +0.002013, tau^2 0.08: SUPPORTED | CONFIRMED (digit) | - |
| 9 | C-M3 +0.0792 SE 0.0187 BELOW INTEREST (secondary) | own +0.079245 / 0.018749, q95 +0.001779, tau^2 0.01; 0.0792 >= 3 SE 0.0562, > q95, < 0.10, and g + 2 SE = 0.1167 >= 0.10, so BELOW INTEREST (not NOT SUPPORTED). Hence "beyond difficulty AND length" is NOT licensed (E3) | CONFIRMED (digit) | - |
| 10 | n = 5,530 scored / 5,504 clusters = census | vault 5,614 - 83 near-dup drops - 1 not-one-correct (international_law/51) = 5,530 (READY-2 row 9); meta near_dup n_kept 5,531, clusters 5,505 before that 1 removal; cluster sizes: max 2, Kish 1.0094; n_rows 13,955 = 14,042 - 83 - 4; n_work 8,425 = 8,428 - 3 | CONFIRMED | - |
| 11 | nulls R = 200 | nulls_helm.json 200 x 3; C-M1 164 at tau^2 = 0 (each gives a gain of exactly 0), 4 > 0, 32 < 0, max +0.0068, q95 0.000000; C-M2 139 / q95 +0.002013; C-M3 146 / q95 +0.001779 (all = log). The observed C-M1 is 17x the null max | CONFIRMED | - |
| 12 | harness PASSED | harness_helm.json: [R18] K 20, n_exceed 0 (fails at > 2), mean -0.00146 SE 0.00074 (fails at > +2 SE), tau^2 0 in 10 of 20 | CONFIRMED | - |
| 13 | predictions | PM1 0.1171 outside [-.02,.06], wrong word: FAILED; PM2 1.1688 outside [.05,.50] (word in set): FAILED; PM3 0.0792 outside [-.03,.05], BELOW INTEREST not in set: FAILED; PM4 NOT SCORED (NOT ALIGNED, Spearman +0.2219, refused unless equal to [A1] within 1e-12); PM5 Zmax d3 0.1467 outside: FAILED; PM6 0.1138 - 0.1171 = -0.0033 inside [-.02,.02]: HELD | CONFIRMED | - |
| 14 | no vault leakage into WORK fits | `confirm_core` writes meta.json (10:53) with the WORK tau^2 BEFORE `guard.arm()`; harness 11:04 and outcome 11:09 come later; `read_roster` asserts the chain and reader tau^2 unchanged after opening (passed: "WORK side identical"); group-reader sums run over `ctx.fit` rows only (meter.reader_sums); tree manifest `model_responses_read: false` | CONFIRMED | - |
| 15 | backup | E:/TaxoArena_backup_2026-10-22_mmlu_vault: `sha256sum -c SHA256SUMS_vault` 7 OK, 0 not OK | CONFIRMED | LOW (D3) |

## Artefact probes: can anything inflate the gains? (descriptive, no word)

| probe | result | inflates? |
|---|---|---|
| damped Newton (irt.fit_theta_slope) | an undamped replica fails on exactly 7 columns (olmo-7b, claude-3.5-sonnet x2, claude-3-opus, deepseek-v3, gemini-1.5-pro-002, gpt-4o-0806), i.e. the C2 disclosure. All 79 columns end at max abs gradient 6.3e-13, so the damped points are maximisers. Those 7 contribute +0.0004 of 0.1171; the 72 others alone give +0.1280 per cell | no |
| DEFF | it enters the SE only, never g; the realised SE is larger than the registered one, which is conservative | no |
| near-duplicate clustering | twins are rare (Kish 1.0094). Also dropping the scored items with max cos to WORK >= 0.95 (23 more): g +0.1126 SE 0.0346; >= 0.90 (139): +0.1043 SE 0.0349 | no |
| answer-letter leakage via text leaves | I(answer; leaf given subject) = 0.0289 nats vs a within-subject leaf-permutation null q95 0.0293 (max 0.0306, 200 draws): no letter structure | no |
| L2 re-read (POSTRUN_BZ-TREE-VARIANTS-WORK D4) | G(L2 given L2) = +0.0307 SE 0.0132 (tau^2 0.01; reproduced). C-M1 net of it = +0.0864 SE 0.0326, which is < 0.10 and < 3 SE | YES, about 26% of C-M1 (D1) |
| concentration | by subject: miscellaneous 24%, moral_scenarios 15%, human_sexuality 13%; 32 of 79 models contribute < 0. Without moral_scenarios g is +0.1060 SE 0.0334; without moral_scenarios and miscellaneous it is +0.0808 SE 0.0348 | the gain is real but uneven |

The predictions failed upward. On the evidence above, the gains are not a fitting artefact: the nulls, the harness, the
out-of-sample cell sums and the letter check all hold. The honest prior (MMLU-Pro roughly 0) did not transfer.

## Defects

- **D1 (MEDIUM, interpretation):** about 0.031 of C-M1's 0.117 is the meter's L2 re-read artefact. The registered
  statistic is plain G (E2), so this is not a criterion substitution and the word stands. Fix: the record quotes "net of
  the L2 re-read +0.0864 SE 0.0326" beside every C-M1 quotation. Any future MMLU/axis registration should register the net
  form or a re-read-corrected bar.
- **D2 (LOW, READY-2 D4 / V4):** outcome.txt has no FALSIFIER line, and the C-M1 word has no "(DESCRIPTIVE-ONLY by support)"
  suffix. Fix: the registrar writes both, in the wording below.
- **D3 (LOW):** the registered GUARD names the backup E:/TaxoArena_backup_<date>_axis_confirm_mmlu; the actual path is
  `..._mmlu_vault` (content verified 7 / 7). Fix: record the actual path.
- **D4 (LOW, carried from [A1]):** Support (b)-(d) transported DEFF 1.1257 / SE 0.0167; the realised values are 1.934 / 0.0346.
  Fix: record the realised values beside the registered ones. Lesson: DEFF grows with the roster beyond the constant-ICC
  forecast (1.45).
- Own mutants: none. This is a numbers review of an unchanged blob; READY-2 M1-M4 cover the vault-mode guards, and the
  independent recomputation replaces the scorer path.

## Wording for the registrar (verbatim)

"BZ-AXIS-CONFIRM-MMLU (2026-10-22, 0 LLM calls; ONE vault read, benchzoom dfeb0aa, runner blob:aec30584, src tree c9809e98;
POSTRUN docs/reviews/POSTRUN_BZ-AXIS-CONFIRM-MMLU.md: OUTCOME CONFIRMED). HELM, 79 models x 5,530 kept vault items (5,504
twin clusters), x 1e-3 nats per cell. C-M1 G(L3a | L2) = +0.1171, item-clustered SE 0.0346, q95 +0.0000 (R 200), tau^2
0.02: SUPPORTED (DESCRIPTIVE-ONLY by support; Support condition (f) fired before the vault opened; the word decides
nothing). Support realised: DEFF 1.934 (registered transport 1.1257), n_eff 2,860, MDE80 0.1327 vs delta_min 0.10. Net of
the L2 re-read (G(L2|L2) +0.0307 SE 0.0132): +0.0864 SE 0.0326. FALSIFIER: the C-M1 word is SUPPORTED (DESCRIPTIVE-ONLY by
support): printed, overturns nothing. C-M3 G(L3a | L2 + diff + len) = +0.0792 SE 0.0187: BELOW INTEREST (secondary), so
'beyond difficulty and length' is not licensed. C-M2 G(L3a | L1) = +1.1688 SE 0.1228: SUPPORTED (secondary). Harness [R18]
PASSED. tinyBenchmarks NOT ALIGNED (Spearman +0.2219): C-M4 NOT SCORED. Predictions: PM1, PM2, PM3, PM5 FAILED (the
observed gains lie above the predicted ranges), PM4 NOT SCORED, PM6 HELD. Descriptive: S1 +0.1138 SE 0.0350 (148 Redux-
flagged items removed); S2 +0.1753 SE 0.0441 (2,608 MMLU-Pro overlap items removed); Z max-T over depths given L2 +3.826 at
d2. No claim 'the axis leaves add a gain of interest over the 57 subjects' is licensed (C-M1 is descriptive-only); C-M3 is
quoted beside C-M1 in every quotation."

## Commands (read-only on every object of record)

```
sed -n 1,12p E:/benchzoom_demo/mmlu_confirm/vault_run.log; diff <(sed -n '9,$p' vault_run.log) vault_read/outcome.txt   # by eye
cd E:/benchzoom_demo/mmlu_confirm && sha256sum -c SHA256SUMS_vault          # 7 OK (before and after); backup dir: 7 OK, 0 not OK
git -C benchzoom rev-parse HEAD HEAD:src/benchzoom HEAD:examples/axis_confirm_mmlu.py; git status --porcelain | wc -l   # 0
git log --oneline f6402011..HEAD -- docs/judge_v2_program.md | wc -l        # 0
find E:/benchzoom_demo/mmlu_confirm E:/benchzoom_cache/mmlu_confirm -type f -printf '%T@ %s %p\n' | sort   # before = after (338)
python -c "<meta.json tau2 / near_dup / load; outcome.json lines; nulls_helm.json pos/zero/neg, q95; harness_helm.json>"
OMP/OPENBLAS/MKL=1 benchzoom/.venv python E:/TaxoArena_tmp/postrun_mmlu_vault/recompute.py   # rows 3, 5-9, 10, probes (528 s)
OMP/OPENBLAS/MKL=1 benchzoom/.venv python E:/TaxoArena_tmp/postrun_mmlu_vault/probe2.py      # per-subject, letter leakage
```
Logs: E:/TaxoArena_tmp/postrun_mmlu_vault/recompute.log, probe2.log (scratch, not committed).
