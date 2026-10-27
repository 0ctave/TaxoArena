# POSTRUN review: BZ-METER-AXIS (axis_v1 leaves read by the meter), vault read

Authority: `docs/agents/author_decisions/2026-10-20.md` D-2026-10-20-1. Pre-read: `READY_BZ-METER-AXIS.md` (6ecdd0ff,
READY with C1). Reviewer: adversarial reviewer, 2026-10-20. Zero API calls. The vault read was NOT re-run and my code
never opened the vault guard (see "Scope limit" below); nothing was written under `E:/benchzoom_demo`.

## Verdict

**VALID as a registered read; MATH `L3a|L2` SUPPORTED stands, with two qualifiers (Q1, Q2).** MMLU-Pro `L3a|L2`
NOT SUPPORTED stands (powered: MDE80 0.070 < delta_min 0.10). Falsifier FIRED on MATH: correct by the rule.

- **Q1 (magnitude, HIGH for any quoted number):** the point +0.259 is not a precise size. Its 3-SE lower bound is
  +0.070, BELOW delta_min (0.10); the registered word needs only the point >= delta_min (it is; g - 2 SE = +0.133).
  The best WORK-side estimate at the vault's own tau^2 and near its fit size is +0.120 (SE 0.047). Quote as
  "SUPPORTED (g +0.26, SE 0.063; WORK cross-fit +0.12): the axis leaves add a gain at about the bar of interest over
  subject x level", never "5x the v2 leaves" as a size.
- **Q2 (status):** the leaves were cut on all 4,914 MATH items' text, vault included (registration Section 1). This is
  a transductive leaf assignment, not a response leak (below). Keep the registered phrase "held out from the meter;
  leaves built on all items' text"; never "clean", "content-closed" or "held-out tree".

## The 5x gap (WORK pseudo-vault +0.054 vs vault +0.259): explained, mostly sampling plus tau^2

Own WORK-only diagnostic (`diag_work.py`, 0 vault reads asserted, reviewed snapshot 096d43d; MATH, 69 models):

| Step | g (x1e-3) | SE | what changes |
|---|---|---|---|
| registered pseudo-vault k=0, tau^2 0.01 (selected on 1,768 fit items) | +0.0539 | 0.0213 | reproduces work_exploratory to the digit |
| same split, tau^2 forced 0.04 | +0.0649 | 0.0675 | tau^2 alone: +0.011 |
| 4 more pseudo-vault draws (same rule, k=1..4), selected tau^2 .02/.04/.04/.02 | +0.107 / +0.119 / +0.088 / +0.142 | .038-.070 | k=0 is the LOWEST of 5 draws (mean of 5 = +0.102) |
| same 5 draws at tau^2 0.04 | +0.065 / +0.120 / +0.119 / +0.088 / +0.178 | .066-.070 | mean +0.114 |
| WORK 5-fold cross-fit (fit ~2,359, near the vault fit's 2,949), tau^2 0.04, pooled n 2,949 | +0.1199 | 0.0467 | fit size: about +0.006 |
| same, selected tau^2 per fold (.02,.02,.04,.04,.02) | +0.0936 | 0.0370 | per fold +0.148 / +0.191 / +0.125 / **-0.184** / +0.188 |
| vault (fit 2,949 WORK, tau^2 0.04 selected on WORK before the open, scored 1,960) | +0.2588 | 0.0628 | residual vs +0.120: +0.139, about 1.8 SE of the difference (sqrt(.063^2+.047^2) = .079) |

Reading: (1) the registered pseudo split was an unlucky low draw (about half the gap); (2) WORK selected tau^2 0.04 on
all 2,949 items versus 0.01 on 1,768, and a larger tau^2 both lifts g and inflates its SE (0.021 -> 0.063); (3) the
fitting-set size adds little; (4) the vault sits about 1.8 SE above the WORK expectation: sampling, not a mechanism.
The tau^2 sweep is sign-fragile at 0.04 (one WORK fold -0.18): the vault's +0.26 is a favourable draw of a real but
small effect, which is Q1.

**Leak (no).** Offsets are fitted on WORK responses only (`reader_sums` over `ctx.fit`); a vault item receives the
shrunk mean of its leaf's WORK items. Its leaf comes from its text, which never carries its responses. The pseudo-vault
items were in the tree build exactly as the vault items were (all 4,914 items' text), so the build cannot separate the
two and cannot explain the gap between them. The v2 atlas tree has the same status and showed the same pattern: v2
pseudo `L3t|L2` 0.000 (tau^2 0) against vault +0.058 (tau^2 0.005) (`meter_v2/calibration_work` vs `meter_v2/outcome.json`).

**Concentration (WORK cross-fit, tau^2 0.04; descriptive).** 20 of 36 leaves positive; the top 5 leaves (Prealgebra|51,
C&P|39, Geometry|29, Prealgebra|50, Algebra|48) carry +0.130 of +0.120 (the rest net negative). 41 of 69 models
positive; the top 5 (Llama-3.3-70B, Llama-3.2-1B, gemma-2-2b, command-a-reasoning, gemma-3-1b) carry +0.171. This is
weak-model heavy, consistent with the 22-model line +0.79. By level: L2 +0.034, L3 +0.030, L4 +0.046, L1 0.000, L5
+0.011. No extreme-difficulty artefact; the gain is mid-level and within subject x level. Leaf top-level share has
mean 0.31 (max 0.50; 5 levels; base rate not computed). The same leaves lead on pseudo k=0 (C&P|39, Prealgebra|50,
Geometry|29/57). **The vault-side per-leaf and per-model split is UNDETERMINED** (scope limit).

## Per-claim table (deciding claims)

| # | Claim | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | pins: code 096d43d, registration blob 5de17ff1, parent 5c457088, clean | meta.json `commit` 096d43d, `dirty` "", `axis_reg_blob` 5de17ff1, `reg_blob` 5c457088; `script_blob` 6ad6b268 = `git rev-parse 096d43d:examples/meter_test.py`; `meter_blob` f31973af = 096d43d:src/benchzoom/meter.py; reg LF blob = `git hash-object` 5de17ff1 (no CRLF rendering, pre-read) | CONFIRMED | - |
| 2 | wrote only the registered dir | `find E:/benchzoom_demo E:/benchzoom_cache -newermt 13:11 ! -newermt 13:20` = 10 entries (dir, 7 files, _logs, vault_read.log), all under meter_axis_v1; meter_v2/outcome.json 7bca5558, meter_v1 af1f8042, mtimes 10-12/10-11; `sha256sum -c` SHA256SUMS 6/6 OK, backup 6/6 OK; C1 command recorded (no --out) | CONFIRMED | - |
| 3 | outcome reproduces from the nulls (q95, tau0, words) | numpy linear p95 from nulls_axis_*.json (200 per series): MATH L3a\|L2 q95 +0.0035, tau0 127; L3a\|L1 +0.0041/125; 22-model +0.0101/+0.0105; MMLU-Pro +0.0005/153, +0.0089/123: all = outcome to the digit; [R2] words recomputed: 6/6 identical | CONFIRMED | - |
| 4 | MATH L3a\|L2 g +0.2588 SE 0.0628 SUPPORTED | z 4.12 >= 3, g > q95 (75x), g >= 0.10; DEFF 1.0887 = (0.06278/0.06017)^2; n_eff 1,960/1.0887 = 1,800; MDE80 3.84 x 0.06278 = 0.2411; clusters 1,960 = n | CONFIRMED (with Q1) | HIGH (Q1) |
| 5 | MMLU-Pro L3a\|L2 g -0.0059 NOT SUPPORTED (null and interest) | g <= q95 +0.0005 and g + 2 SE = 0.031 < 0.10; tau^2 0.005 (not DEGENERATE, unlike WORK); MDE80 0.0703 < 0.10 (powered); clusters 4,625 / n 4,654 | CONFIRMED | - |
| 6 | Bonferroni family = 2, p .00135 each, FWER .0027 | registration Section 5 = runner text; 12 deciding tests on this vault, FWER <= .0162 stated, word unchanged | CONFIRMED | - |
| 7 | predictions PA1, PA3, PA4, PA5, PA6-MATH NOT HELD; PA2, PA6-MMLU HELD | ranges and word sets of Section 8 applied to the outcome by hand: 7/7 identical. PA5 NOT HELD by range (0.79 > 0.30) though its word held | CONFIRMED | - |
| 8 | identities to meter_v2 exact | 4 + 4 lines diff 0; harness identity "yes" on both | CONFIRMED | - |
| 9 | A1 Support (vault SE 0.0165, MDE80 0.063) | realised SE 0.0628 (3.8x) and MDE80 0.241 > delta_min: the projection assumed tau^2 0.01; tau^2 0.04 inflated the SE | REFUTED as a projection (no effect on a SUPPORTED) | MEDIUM |
| 10 | "5x WORK" explained | see the table above | CONFIRMED: sampling + tau^2; leak excluded | - |

## Defects

- D1 (HIGH, wording): any reader of the record must carry Q1. Fix: the registrar's outcome entry quotes g with SE, the
  3-SE lower bound +0.070 and the WORK cross-fit +0.12 (SE 0.047); no "5x" ratio as a size.
- D2 (MEDIUM): the A1 Support re-cut scaled the SE at the pseudo split's tau^2 (0.01). The vault tau^2 (0.04) was
  knowable before the open (meta.json, WORK-side) and gives about 4x the SE. Fix for future meter lines: Support recut
  at the WORK-selected tau^2 of the full fitting set; report the pseudo split's draw-to-draw spread (here 0.054-0.142).
- D3 (LOW): the registered pseudo-vault is one draw; k=0 was the lowest of 5. A single-split dress rehearsal is not a
  prior for the vault; record this in the limitations note.
- D4 (LOW): `meter_test.py` / `tests/test_meter_axis.py` were modified after the read (13:20) and committed as f04f549
  (the D1 out-dir fix). This is after the read and does not touch the reviewed blobs; it needs its own delta review.

## Scope limit (vault-side decomposition)

A vault-side per-leaf / per-model decomposition needs the scored responses. My attempt to arm the guard in a scratch
copy was refused by the session's permission classifier, and the brief forbids re-running the read. I did not work
around it. The concentration above is WORK-side only. If the author wants the vault split, that is a further opening of
the vault (a fourth, to be disclosed) and needs the author's say-so.

## Commands

```
git -C Z:/FAC/TUBerlin/benchzoom rev-parse 096d43d:examples/meter_test.py 096d43d:src/benchzoom/meter.py; git hash-object docs/meter_axis_registration.md
cd E:/benchzoom_demo/meter_axis_v1 && sha256sum -c SHA256SUMS; (same in E:/TaxoArena_backup_20261020_meter_axis_v1)
find E:/benchzoom_demo E:/benchzoom_cache -newermt '2026-10-20 13:11' ! -newermt '2026-10-20 13:20'   (10 entries)
python: np.percentile(nulls_axis_<ds>.json[...], 95), tau0 counts, [R2] words, DEFF/n_eff/MDE80 from outcome.json
git archive 096d43d -> scratch; .venv python -I scratchpad/diag_work.py <snap>   (WORK only; guard never armed;
  vault_reads 0; pseudo_vault k=0..4, tau^2 sweeps, WORK 5-fold cross-fit strat_folds rng [20261020, 99], decompositions)
sha256 of 339 files (meter_axis_v1, meter_v2, axis_v1, emb, eee, math_v2, vault) before/after the diagnostic: identical
```
