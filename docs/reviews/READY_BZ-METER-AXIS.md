# READY review: BZ-METER-AXIS (axis_v1 leaves read by the meter), pre-read

Authority: `docs/agents/author_decisions/2026-10-20.md` D-2026-10-20-1. Reviewer: adversarial reviewer, 2026-10-20.
Zero API calls; no vault read run. benchzoom (local) at 096d43d; registration LF blob 5de17ff1 (no CRLF rendering:
`git hash-object --no-filters` = filtered = 5de17ff1; runner `examples/meter_axis.py` LF blob dbbc103f = HEAD).

## Verdict

**READY, one condition (C1).** C1 (MEDIUM): the vault read must be launched as exactly
`python examples/meter_test.py --axis vault` with NO `--out` (or land the one-line fix of D1 first, then delta review
of that line only). The operator's hand-back records the exact command line. Nothing else blocks.

## A1 in plain words

[A1] (096d43d, 12:52:30) was inserted AFTER the synthetic gate (outputs 12:46:31-12:46:45) and the WORK dry run
(12:46:50-12:51:10) were seen, and before any vault read (`meter_axis_v1/outcome.json` absent). It is insertion-only
(0 deleted lines; 5 hunks, all in the header, Section 0, Section 1, Section 6, Section 12). It adds the disclosure, the
MMLU-Pro node-count correction (152 -> 147 nodes / 80 leaves; descriptive, and true: own count below) and the
exploratory WORK Support table. No criterion, word, range, null, multiplicity or prediction changed; the WORK run
showed PA3, PA4, PA5 and PA6-MATH would NOT hold and they were left as committed. It does not matter for the read.

## Per-claim table (deciding claims)

| # | Claim | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Registration committed before code | 0297313 (12:18:35) adds only the registration; first commit touching `meter_axis.py`/`test_meter_axis.py` is 567841c (12:46:18) (`git log --all -- <paths>` = 2 commits); `src/` untouched 0297313..096d43d (0 commits) | CONFIRMED | - |
| 2 | Predictions fixed before WORK numbers | Section 8 present at 0297313; WORK/synthetic outputs all mtime >= 12:46:31 (after 567841c); A1 adds no line in Section 8 | CONFIRMED | - |
| 3 | [A1] insertion-only, before any vault read, criteria unchanged | see above; runner diff 567841c..096d43d = the `AXIS_REG_BLOB` line only (6aacc8dd -> 5de17ff1) | CONFIRMED | - |
| 4 | item->leaf map reproduces axis_v1 | own script from the pinned pickles: MATH 66 nodes / 36 leaves, sizes 83..224, sum 4,914 = n_items, 4,914 unique rows; MMLU-Pro 147 / 80, sizes 84..329, sum 11,994 = n_items; leaf {id: n} dict equal to tree.csv leaves on both; 0 leaves span >1 subject; pins (2 csv, 2 pkl) match `axis_v1/SHA256SUMS.txt` to the digit | CONFIRMED | - |
| 5 | Map covers every meter row, aligned by id | WORK outcome: 2,949/2,949 and 7,197/7,197 rows mapped; subject != declared category for 0 rows (an alignment witness); WORK+vault item counts 2,949+1,965 = 4,914, 7,197+4,797 = 11,994 (every vault item is in the tree) | CONFIRMED | - |
| 6 | Tree text-only, built on all items incl. reserved, disclosed | manifests `model_responses_read: false`, `parquet_columns_read: [id, text, options, subject]`; pickle `items` columns = id, text, question, subject, options; Section 1 "Status of the tree" and Section 7 disclose it ("never clean or content-closed") | CONFIRMED | - |
| 7 | No vault row / record touched by dry run or map | WORK meta: code 567841c clean, guard reads 0 (asserted in code); `meter_v2/outcome.json` 7bca5558, `meter_v1/outcome.json` af1f8042 = pins; sha256 of all 65 files under meter_v2 + meter_axis_v1 identical before/after my refusal script | CONFIRMED | - |
| 8 | Null permutes within category, own stream, not vacuous | code: `permute_within(leaf, cat, fit|score, default_rng([20261012, 8, r]))`, = v2's L3t null except code 8; leaves nested in category (claim 4), so sizes per category preserved; own recompute from `nulls_axis_*.json`: 200/200 written per series; tau2=0 in 153 (MATH) / 151 (MMLU-Pro) for L3a|L2; q95 +0.0011 / +0.0000 (numpy linear) = outcome to the digit. Mutant O4 (permute within leaf = identity) killed | CONFIRMED (see D3) | LOW |
| 9 | Refusal guards fire | sandbox/monkeypatched, no real output: wrong csv pin, wrong pkl pin, tree.csv n+1 (re-pinned copy), tree.csv node dropped, wrong registration blob, v2 record sha mismatch, no gate in out, gate but no work_exploratory, out under meter_v2: 9/9 REFUSED, all before `load_dataset` | CONFIRMED | - |
| 10 | L3a path = L3t path except the label | L3t: `STEPS ("L3t","group","leaf","L2")` -> `step(kind, lab.leaf, [c.eta["L2"] for c in ctxs], ctxs, cat, rule)`; L3a: `_restep(ch,"group",leaf,"L2",cat)` -> the same `step` on the same `ch.ctxs`/parents/rule; L3a1 likewise on L1. WORK identity: v2 tau2, all 20 harness draws, G(L1|L0), G(L2|L1), G(L3t|L2), G(L3t|L1) diff 0 | CONFIRMED | - |
| 11 | WORK Support re-cut arithmetic (A1 table) | MATH L3a|L2 vault SE 0.0213 x sqrt(1181/1960)=0.776 -> 0.0165, MDE80 3.84 x 0.0165 = 0.063 < delta_min 0.10; MMLU-Pro L3a|L1 0.0777 x 0.787 = 0.0611 (table 0.0612, unrounded SE), MDE80 0.235; DEFF 1.0748 from the run's own item clusters (1,181 clusters / 1,181 items in the pseudo-vault; vault uses twin components); n_eff 1181/1.0748 = 1,099 | CONFIRMED | - |
| 12 | Synthetic gate PASSED | gate.txt sha 6130637b; planted SUPPORTED g +13.5763 SE 1.7413 (z 7.80); null DEGENERATE | CONFIRMED (see D4) | LOW |
| 13 | Suite 635/0 | `pytest -q`: 640 passed, 4 deselected, 0 failed (597 s) | PARTLY (count differs, no failure) | LOW |
| 14 | Mutants 18/18 | builder's runner is not in the repo, not re-run; own 7 below: 5 killed, 2 survived (non-decisive) | UNDETERMINED (builder's) | LOW |

## Own mutants (sandbox copy of examples/ + src/benchzoom/meter.py, git-initialised; CONTROL 18/18 pass)

- O1 tree.csv parent not compared (load_axis_map): SURVIVED; non-decisive (claim 4 checks parents' effect: leaf dict, partition, node set).
- O2 axis tau2 change-on-vault-open assertion removed (axis_core): SURVIVED; non-decisive (inertness assertion).
- O3 deciding L3a|L2 word reads the L3a|L1 null q95 (axis_words): killed (gate_golden); decisive.
- O4 null permuted within leaf (identity null) (axis_nulls): killed (null_permutes_within_category, gate_golden); decisive.
- O5 vault proceeds when work_exploratory is missing (axis_main): killed (vault_refusals_before_any_data); decisive.
- O6 tree.csv leaf flag not compared (load_axis_map): killed (load_axis_map_refusals).
- O7 label category taken from the axis-build subject (axis_labels): killed (axis_labels_coverage).

## Defects

- D1 (MEDIUM; C1): "read ONCE into the NEW directory meter_axis_v1" (Section 7) is enforced only by write-once of
  `<out>/outcome.json`; `meter_test.py --axis vault --out <dir>` is accepted for any dir not under meter_v1/v2, and the
  gate/work refusals read `<out>/calibration_synthetic` and `<out>/work_exploratory` (my case f: a copied gate passes,
  refusal only at work_exploratory). A copied WORK dir would allow a second vault read elsewhere. Fix: in `axis_main`,
  `if mode == "vault" and out.resolve() != OUT_AXIS.resolve(): raise SystemExit("REFUSED: ...")`, plus a test.
- D2 (LOW): O1/O2 survive; add a parent-mismatch case to `test_load_axis_map_refusals` (the assertion of O2 is
  untestable without a data change; acceptable).
- D3 (LOW, descriptive): the within-category null rarely binds (q95 +0.0011 MATH, +0.0000 MMLU-Pro; 153/151 of 200 at
  tau2 = 0); the effective bar for SUPPORTED is 3 SE and delta_min. It is the parent's registered null, not a defect of
  this line; the read should say the null did not decide.
- D4 (LOW): the gate's planted effect (z 7.8, g 136 x delta_min) tests direction, not sensitivity near the bar; the null
  fixture passes as DEGENERATE. Registered design; no change.
- D5 (LOW): `T.code_state()["dirty"]` (recorded in WORK meta) does not cover `examples/meter_axis.py`; the vault-mode
  dirty refusal does. Record only.
- D6 (LOW): builder's suite count 635 vs 640 passed here; correct the count in the hand-back.

## Commands

```
git -C benchzoom log --format='%h %ad %s' --date=iso -12; git show --name-only 0297313 096d43d 567841c
git diff 0297313 096d43d -- docs/meter_axis_registration.md | grep '^-' (0 removed lines); git diff -U0 ... | grep '^@@'
git diff 567841c 096d43d -- examples/meter_axis.py (1 line); git hash-object [--no-filters] <reg> <runner>
ls -la --time-style=full-iso E:/benchzoom_demo/meter_axis_v1/*; sha256sum -c work_exploratory/SHA256SUMS (6/6 OK)
scratchpad/leafcheck.py (pickle leaves vs tree.csv, subject nesting, manifest inputs)
scratchpad/refuse.py (9 refusals; before/after sha256 of 65 files under meter_v2 + meter_axis_v1: identical)
numpy percentile/tau0 recompute from nulls_axis_{math,mmlu_pro}_pseudo.json
scratchpad/mut.py (BENCHZOOM_METER_AXIS sandbox; pytest tests/test_meter_axis.py per mutant)
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider  -> 640 passed, 4 deselected
```
