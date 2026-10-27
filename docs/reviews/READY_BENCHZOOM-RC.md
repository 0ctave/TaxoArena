# READY review: benchzoom release candidate (HEAD bd09816), 2026-10-09

Reviewer: adversarial-reviewer. Zero LLM calls. benchzoom read-only. All runs ran in a scratch clone at
E:/TaxoArena_tmp/bz_review (venv, non-editable install from the clone). Programme spans are `_as_of 78f9bc2e`:
ADAPTIVE-PROFILE registration L25133-L25145; CERT-SPLIT-DIP registration L24958-L24972, outcome L25328-L25340.
Reviewed blobs (LF, `git rev-parse bd09816:<path>`): irt.py 5989d13a5d6d, profile.py a54856954207, gates.py c0ee87884644,
tree.py e2bf6bab9c80, atlas.py 44f8048e1a87, sources.py 2a3678c663e0, README.md eae3563c63e4, NOTICE.md e05239910004,
docs/defaults.md 019522bd15b6.
SCOPE NOTE: during this review a peer left 7 uncommitted changes in the benchzoom working tree (sources.py +108/-44,
README, tests, new `examples/mmlu_pro_open_llm_leaderboard.py`; `git status --short` gave 0 lines at start and 7 later).
They are NOT reviewed. A delta review is owed once they are committed.

## Verdict
**NOT READY as a release candidate.** The code core is CONFIRMED: the LOMO Rasch fit, EB shrinkage, the adaptive
read and the gates match the registration, and 108 tests, ruff and mypy pass. Two HIGH documentation defects
contradict the code or the record. Fix them, then M-1..M-5. No BLOCKER in the code.
CERT-SPLIT-DIP: the rule IS implemented (`gates.dip_p` / `DipGate`, line for line with the record's `cert_split_dip.py`
`skmeans2` / `dip_site` / `combine`). It is correctly off by default, but for the wrong stated reason (H-2).

## Per-claim table (deciding claims)
| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | LOMO: column m of b fitted without model m (prog L25133ff "b_i from the LOMO Rasch fit (prior N(0, 2^2))") | b col 3 vs independent L-BFGS MAP on Y[:, others]: max gap 8.3e-6; full fit vs reference 5.8e-6 (b), 2.2e-6 (theta); prior_sd_b 2.0 | CONFIRMED | - |
| 2 | theta_m with b fixed (LOMO column) | code fits theta on B[:, j] (irt.py L111); theta 3 = -2.107360 vs reference -2.107360 | CONFIRMED, but untested (mutant I3 survived) | MEDIUM (M-1) |
| 3 | EB prior N(0, tau_l^2) per depth, MoM floored at 0, one Newton step from the parent's linear predictor | profile.py L213-L239 implements it; MoM leaves out cells with h < h_min = 1 (registration: "all models and nodes") | PARTLY (disclosed in defaults.md; not in NOTICE's deviations) | LOW (L-2) |
| 4 | descend only if SE < 0.20 AND BH q 0.05 within the sibling family with a defined SE | profile.py L330-L338; mutants P4-P7 killed | CONFIRMED | - |
| 5 | one-member family: strict \|z\| > 1.96 | the code runs BH with m = 1, so it certifies at p <= 0.05, i.e. \|z\| >= 1.959964. The probe certifies z = 1.95997 and z = 1.96000, which the registered wording refuses | REFUTED at the boundary (zero measure) | LOW (L-1) |
| 6 | default certify = "registered" (D-2026-10-08-2, "Registered rule (Recommended)") | `AtlasConfig().certify == "registered"` (atlas.py L45; test L171). NOTICE.md says the default is "contrast" | code CONFIRMED / NOTICE REFUTED | HIGH (H-1) |
| 7 | start at the benchmark node | subject nodes are entered without a test (`enter_subjects`). The adapters set subject = task, so BBH's 27 subtasks become uncertified "benchmark" nodes | PARTLY | LOW (L-3) |
| 8 | spherical 2-means (k-means++, 10 restarts, <= 100 iterations, cosine) | identical to record `skmeans2`; d = 1 - cos is D^2/2, so the seeding is true k-means++. Mutant T1 (uniform seeding) survived | CONFIRMED / test gap | LOW (L-5) |
| 9 | SeparationGate p = (1 + #{J_null >= J}) / (1 + reps); early stop preserves the decision | limit = floor(0.05 * 301 - 1) = 14, so it passes iff exceed <= 14. Mutants G3, G4, G5, G7, G9 killed | CONFIRMED | - |
| 10 | DipGate = the CERT-SPLIT-DIP rule | the axis is chosen on A and B is tested; p = min(1, 2 x median). G1, G2, G8 killed. Departures: the halving RNG is the node stream, not sha256(name) + r; an extra n_B < 4 -> p = 1 guard; diptest is not pinned (record: 0.11.0, tabulated) | CONFIRMED (rule) | LOW (L-6) |
| 11 | README: DipGate "off by default until its registered calibration (CERT-SPLIT-DIP) has been read out"; defaults.md "has not been merged either" | read out VALID 2026-10-09 (POSTRUN 692d12ff): SD0 SIZE-OK 0/300, SD1 SENSITIVE 60/60 (qualifier S-1), F-SD not fired | REFUTED (stale) | HIGH (H-2) |
| 12 | README: "ADAPTIVE-PROFILE has not been run"; defaults "registered, not validated" | results/ADAPTIVE-PROFILE.json: blocked, NO OUTCOME ([AP-DENOM] refusal) | CONFIRMED | - |
| 13 | adapters: OLL metrics acc_norm BBH/GPQA/MuSR, acc MMLU-Pro, exact_match MATH-hard, IFEval mean of strict prompt- and instruction-level | match the leaderboard v2 definitions. The IFEval per-item analogue is disclosed (sources.py L50-L54) | CONFIRMED | - |
| 14 | lm-eval: "the task's primary metric (first of its metric_list)" | lm-eval has no primary-metric field. hellaswag / arc_* list acc before acc_norm in the harness's task YAMLs, and acc_norm is the conventional figure. Taken from the published YAMLs, NOT executed here (lm_eval not installed) | UNDETERMINED by command; wording overclaims | MEDIUM (M-2) |
| 15 | README gate calibration: SeparationGate certified "3 of 20" at axis ratio 10, "0 of 60" at ratios 1 and 3; defaults.md table 20 per class, dip delta 2 19/20 | at the suite's seeds (test_tree_gates `_rate`, s0 = 1, 2, 3, 4): sep 0/30, 0/30, **1/20**, d2 20/20, d6 20/20; dip 0/30, 0/30, 0/20, d2 **20/20**, d6 20/20. defaults.md "20 per class" contradicts README "60" (the suite runs 30 + 30) | REFUTED as stated (not reproducible; seeds not given) | MEDIUM (M-5) |
| 16 | defaults.md: planted fixture, registered 18/20 vs contrast 17/20 | 18 / 17 (spot check) | CONFIRMED | - |
| 17 | packaging: install from a clone, extras, licence files | non-editable `pip install ./clone[dev,plot,hf]` OK; wheel ships licenses/LICENSE + NOTICE.md; License-Expression MIT; extras st / plot / ollama / hf / dev present. NOTICE has no third-party-data section | PARTLY | MEDIUM (M-3) |
| 18 | tests run | 108 passed, 2 deselected (slow, network), 55.98 s; ruff "All checks passed"; mypy "no issues in 12 source files" | CONFIRMED | - |

## Own mutants (27; all applied by exact single-occurrence replacement; PYTHONPATH shadowing proved by the import path)
I1 LOMO column = full.b KILLED · I2 no b prior KILLED · **I3 theta fitted on full.b instead of the LOMO column SURVIVED (decisive for claim 2)** ·
I4 NaN mask dropped in the b gradient KILLED · I5 common-shift step removed SURVIVED (equivalent: a speed step; 125 s vs 54 s proves it ran) ·
P1 tau without the -mean(1/h) term KILLED · P2 unshrunk posterior mean KILLED · P3 offset not relative to the parent KILLED ·
P4 BH -> Bonferroni KILLED · P5 BH step-up -> min index KILLED · P6 s_max dropped KILLED · P7 descend everywhere KILLED ·
P8 predict at the leaf instead of the stop node KILLED · P9 BH `<=` -> `<` KILLED · P10 h_min ignored KILLED ·
P11 subjects not forced KILLED · G1 dip tested on half A KILLED · G2 median without x2 KILLED · G3 p = exceed / reps KILLED ·
G4 early stop off by one KILLED · G5 no renormalisation of the null KILLED · G6 SizeGate `>` KILLED · G7 tie `>` KILLED ·
G8 axis chosen on all rows KILLED · G9 J expectation n^2 KILLED · T1 uniform second seed SURVIVED (not decisive) ·
T2 tie to the latest cell SURVIVED (not decisive; the README and NOTICE claim "ties: the earliest").

## Defects and fixes
- **H-1 (HIGH)** NOTICE.md, first "Deviations" bullet: "the default certification statistic is sibling-centred
  (`certify="contrast"`); `certify="registered"` restores the registered wording". This is false since ca0f175, and the
  file ships in the wheel. FIX: replace it with "the default is the registered statistic z = d / SE(d);
  `certify="contrast"` (sibling-centred, tested against its own SE) is a library option".
- **H-2 (HIGH)** README "Defaults and their status" and defaults.md (header paragraph; `use_dip` row): the CERT-SPLIT-DIP
  readout is described as pending. FIX: keep `use_dip=False` and replace the text with "CERT-SPLIT-DIP VALID 2026-10-09:
  SENSITIVE (point classification at the declared DEFF 1.5; realised DEFF not estimable at delta 6; 20/20 in each of the
  3 categories; category-level DEFF 6.0 at delta 4, descriptive), SD0 SIZE-OK, F-SD not fired; 3 MMLU-Pro categories,
  qwen3 512, draw 5a3e756 TRAIN. It is NOT registered as a certificate of tree sites (no multiplicity control; prog
  L24958ff 'WHAT THIS RESULT WILL NOT SHOW'), so the gate stays off by default." Never quote SD1 bare (S-1).
- **M-1** I3 survives. FIX: a test where model j is extreme asserting `theta[j] == fit_theta(Y[:, j], lomo.b[:, j])` and
  `!= fit_theta(Y[:, j], lomo.b_full)` (beyond 1e-3).
- **M-2** The lm-eval default is called the "primary metric", but it is the first-listed one. FIX: reword it in
  README / docstring / MetricRecord.why. When `metric_list` has more than one entry, either require `metric=` or apply
  a documented override table (hellaswag, arc_*, piqa, openbookqa -> acc_norm) carrying its source.
- **M-3** No third-party-data notice. `Atlas.to_json` writes verbatim item text and options (export.py L78-L83), so an
  atlas built from GPQA would publish GPQA text against GPQA's no-plaintext request. FIX: add a NOTICE section
  "Imported benchmark data keeps its own licence and terms (gated OLL details, GPQA ...)" and a
  `to_json(include_text=False)` option, or a refusal or warning for gpqa tasks.
- **M-4** `predict_proba` is in-sample: offsets and theta are fitted on the same items they predict. The registered AP1
  fits on TRAIN and scores EVAL. FIX: one README sentence ("in-sample; not the registered held-out Brier") and,
  optionally, a `fit_rows=` holdout.
- **M-5** The README / defaults.md calibration counts cannot be reproduced (claim 15). FIX: commit the script with its
  seeds and print its counts, or quote the suite's own counts (sep ratio-10 1/20 at s0 = 3).
- **L-1** In a one-member family, certify iff |z| > 1.96 at q = 0.05 (special case), or state p <= 0.05 in defaults.md.
- **L-2** Add the h_min exclusion from tau's MoM to NOTICE's deviations list.
- **L-3** Document that subject = task makes the read start at the task level without a test.
- **L-4** `RaschFit.converged` is never read (`grep converged` returns irt.py only), so a non-converged fit would pass
  silently. FIX: warn or raise in `fit_rasch_lomo` (maxit 3 gives converged False with no message).
- **L-5** Add tests for the k-means++ second seed (T1) and the tie-to-earliest rule (T2).
- **L-6** Record the diptest version in the gate stats; consider `diptest==0.11.*` (the record's pin).

## Commands
```
git clone -q Z:/FAC/TUBerlin/benchzoom E:/TaxoArena_tmp/bz_review/clone; python -m venv venv; venv/Scripts/python -m pip install "./clone[dev,plot,hf]"
cd clone; ../venv/Scripts/python -m pytest -q -p no:cacheprovider   # 108 passed, 2 deselected in 55.98s
../venv/Scripts/python -m ruff check src tests; ../venv/Scripts/python -m mypy
E:/TaxoArena_tmp/bz_review/chk_irt.py     # L-BFGS MAP reference for fit_rasch / LOMO column / theta; single-child z probe
E:/TaxoArena_tmp/bz_review/chk_gates.py   # claim 15 counts at the suite's seeds (chk_gates.txt)
E:/TaxoArena_tmp/bz_review/chk_conv.py    # converged flag never consumed
E:/TaxoArena_tmp/bz_review/mut/run_mutants.py  # 27 mutants, results.txt (count 27 lines)
python -c "from tests.test_irt_profile import _planted_read_ok; ..."   # 18 / 17
git -C Z:/FAC/TUBerlin/benchzoom status --short | wc -l   # 0 at start, 7 later (peer edits, not reviewed)
grep -c converged src/benchzoom/*.py   # irt.py only
```
