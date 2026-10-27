# READY_k46_deff: delta review of k46-deff e0669e57 (D1 of POSTRUN_rp21_v2, cb40d39e)

Reviewer: adversarial-reviewer, 2026-10-02. Zero calls. Delta review: `git diff cb40d39e..e0669e57` (2 files; base = the
reviewed blob 8c5ce9db, which is also main's blob at 18769e1f) plus regression. Nothing in main's checkout, no cache and no
backup was written (backup sha256 identical before and after; caches were COPIED to scratch and read there).

**Verdict: READY (for --analyze / analysis output only). MERGEABLE by path AFTER every posting from main's checkout has
completed (RP20 `--leg rp20` AND its ONE leg `--leg one`, C-K9).** Conditions: M-1, M-2 below.

Blob of review: `tools/analysis/k46_repost.py` blob:4159d62eb62c6705de0132da9f336d9df365dcc0, sha256-lf16:58f621dc4582616b
(LF of record); the k46-deff worktree is CRLF: sha256-crlf16:934c30c737e05956. Selftest blob:0da6e380e3025a48b50a66795ee0630a8a3641aa.

## Per-claim table (deciding claims only)

| # | claim | result | evidence / my number vs claimed | sev |
|---|---|---|---|---|
| 1 | posting paths unchanged; only analysis output changes | CONFIRMED | `git diff -U0` = 4 hunks (count): MUTANTS tuple L218 (+"deff_boot", read only by the selftest's mutant loop), `boot_mean` L1121 (+3 keys appended AFTER every RNG draw and every interval field), new `deff_analytic` L1187, `support_text` L1196. All of `boot_mean`/`deff_analytic`/`support_text` sit in the `statistics` section (L1097-L1226); posting is L798-L1096; `boot_mean` callers are all inside analyze_* / canary_floor (called only from analyze_pair L1542); ready_gate/order_gate/launch untouched | - |
| 2 | deciding bootstrap SE and intervals unchanged | CONFIRMED | RP21 v2 `--analyze-canary` run under BOTH blobs on copies of the backup caches: outcome files 34 vs 34 lines, `diff` = exactly 2 lines (the script sha16 header and the SUPPORT line). C1-v2 line identical: d_r 30/300 = 0.1000, 95% normal [0.0658, 0.1342], SE 0.0174, seeds 43-62 identical; C2-v2 / Delta / accounting (1,200 of 1,260) identical | - |
| 3 | RP21 v2 reproduces with DEFF 1.000, same verdict | CONFIRMED | new SUPPORT: "Kish mean cluster size 1.000, one per component \| DEFF 1.000 (ANALYTIC ...) \| n_eff 300.0 \| SE 0.0174 ... \| beside, NOT a measurement: ... 1.053"; `C1-v2: HELD` both blobs | - |
| 4 | the analytic DEFF is the right estimator | CONFIRMED | own script, RP20-like synthetic (1,258 matches in 360 components, Kish 4.191): analytic 1.7548 = my independent ratio-linearisation 1.7548; bootstrap ratio at B 20,000 1.7937 (MC + no g/(g-1)); linear SE 0.01621 vs bootstrap 0.01635; one-per-component -> 1.0 exactly | - |
| 5 | builder's selftest | CONFIRMED | 87 [OK], 0 [FAIL], rc 0 (python); rc 0 under python -O | - |
| 6 | builder's full mutant table | CONFIRMED | `--mutants`: KILLED 22 of 22 (the 21 of record + deff_boot, killed by G8b) | - |
| 7 | pins | CONFIRMED | `git rev-parse k46-deff:...` = 4159d62e; LF sha16 recomputed from the CRLF worktree file with CRLF->LF = 58f621dc4582616b, = the header the analyzer prints | - |

## Own mutants (deciding path = the DEFF printed beside the deciding SE)

- OM1 `var_iid_an` divided by n instead of n^2: KILLED (G8b, G8c). decisive.
- OM2 `deff_analytic` returns the Kish size: KILLED (G8d). decisive.
- OM3 clustered residual `s - pt` instead of `s - pt*c`: KILLED (G8c, G8d). decisive.

## Defects / conditions

- **M-1 (MEDIUM, merge order).** The gate (`parse_ready`) admits a `--go` only when the FIRST verdict line of
  READY_k46_repost.md names the running script's LF sha16. That line still names dd8152585fd7f0d7; the entry I inserted
  is not a verdict line. So after a merge, `--leg rp20` / `--leg one` posting (including a resume) with 58f621dc... is
  REFUSED (fail-closed, as wanted). Merge only after RP20 AND the ONE leg have finished posting, or the ONE leg needs a
  new gate line. --analyze is not gated (no ready_gate call on analyze paths), so the analysis may run with the new blob.
- **M-2 (LOW, wording).** MDE80 stays 2.80 x the bootstrap SE (0.0488 on RP21) rather than the analytic SE (0.0485,
  POSTRUN_rp21_v2 #10). Consistent with the deciding SE; the record should quote 0.0488 from the printed line, and
  POSTRUN W4's "DEFF 1.00 by construction" now matches the printout. No code change needed.
- **L-1 (LOW).** The analytic DEFF is the plug-in (large-B) form without g/(g-1); at RP20's 360 components the factor is
  1.0028 (descriptive only). Name it "plug-in" if quoted to 3 decimals.
- Cache rows posted by dd8152585fd7f0d7 carry that sha in `script_sha16_lf`; the analyzer prints its OWN sha in the header
  and does not compare (verified: RP21 rows dd81..., new blob analysed them rc 0). The postrun reviewer must name both shas.

## Gate entry

Inserted into docs/reviews/READY_k46_repost.md (insertion only, appended at the end; first verdict line and every line
above untouched): an --analyze-only entry for sha256-lf16 58f621dc4582616b. Checked after insertion:
`parse_ready(text, "dd8152585fd7f0d7")` -> reasons [] (RP20's running gate unchanged); `parse_ready(text,
"58f621dc4582616b")` -> refuses (no --go for the new blob); `transport_check.py --ready` (c) rc 0.

## Commands

```
git diff cb40d39e e0669e57 ; git diff -U0 cb40d39e e0669e57 -- tools/analysis/k46_repost.py | grep -c '^@@'   # 4
git rev-parse k46-deff:tools/analysis/k46_repost.py main:tools/analysis/k46_repost.py              # 4159d62e / 8c5ce9db
(worktree k46-deff) python tools/analysis/k46_repost.py --selftest ; python -O ... --selftest ; ... --mutants   # 87 OK; rc 0; 22/22
git archive cb40d39e|e0669e57 tools experiment_results/archv2/g17_canary docs/reviews/READY_k46_repost.md \
   docs/plan_2026-09-15.md src/main/kotlin/taxonomy/service | tar -x -C scratch/k46d/{base,new}
cp experiment_results/_backup/rp21_v2_20261001/*.db scratch/k46d/out_{base,new}/ ; sha256sum -c bk_before.txt   # OK, OK
TAXOARENA_DATA_ROOT=<main> python harness.py {base,new}   # K.real_cfg() with out_dir -> scratch copy; analyze_canary; rc 0, 0
diff out_base/g17_v2_canary_outcome.txt out_new/g17_v2_canary_outcome.txt        # 2 lines: sha header, SUPPORT
python deffchk.py   # analytic 1.7548 = own 1.7548; boot B20000 1.7937; one-per-comp 1.0
OM1-OM3: sed on a scratch copy, --selftest rc 1 each (G8b/G8c/G8d)
```
