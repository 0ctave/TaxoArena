REVIEW: POSTRUN
REGISTRATION: BZ-MMLUPRO-MOREMODELS
VERDICT: OUTCOME CONFIRMED

# Post-run review: BZ-MMLUPRO-MOREMODELS vault read (one read, 2026-10-22 15:18:44Z-18:08:45Z, EXIT 0)

RE-TEST, NOT fresh; 4th opening of the BZ-METER vault items (D-2026-10-21-3). Reviewer: adversarial reviewer, 2026-10-22,
TaxoArena `_as_of 7618b2a5` (programme blob:065e25c1 = HEAD = working tree); benchzoom 233b2f3 (porcelain 0 before and
after). Zero LLM calls; no second `vault` invocation. Recomputation = my own script E:/TaxoArena_tmp/postrun_more_vault/
recompute.py (sha256 9b9de454; log recompute.log f1ea1cef, EXIT 0, 4,523 s, 8 BLAS threads, nothing else running): it
loads through the pinned `load_more` (READY-1 gate, census and 320 part sha256 re-checked), keeps the matrix in memory,
rebuilds the main-context readers at the meta.json tau^2 with its OWN group-reader, log-loss and cluster-SE code, then
re-selects the group-reader tau^2 with the library's CV on the library's inner contexts and computes the L2 re-read
placebo. It reads the registered read's vault responses (verification, as directed); the only statistic it adds is the
placebo the brief asks for. Writes: none outside the scratch dir (`find E:/benchzoom_demo E:/benchzoom_cache -type f
-printf '%T@ %s %p'`, 5,266 files, before = after, `diff | wc -l` = 0; `sha256sum -c SHA256SUMS_vault` 7 OK after).

## Verdict

**OUTCOME CONFIRMED.** Every deciding and secondary number reproduces to the digit (max abs own - record 2.8e-16 over 12
subset x line cells); the words follow [R2]; V1-V5 MET. C-P1 is NOT SUPPORTED **by the interest clause only**: the gain is
detected (3.12 SE, above every null draw), so the word holds but the substance moved from the 23-model "no gain" to "a
small detected gain whose 2-SE upper end is below 0.10" (D1). The L2 re-read placebo is small on this read: +0.0049 SE
0.0171, C-P1 net +0.0481 SE 0.0194 (D2).

## Per-claim table

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | V1 code state | log CMD: head 233b2f37, src c9809e98, blob 306066ea (LF; CRLF rendering 53eda48a, READY-2); today `rev-parse HEAD HEAD:src/benchzoom`, `hash-object` give the same three, porcelain 0; benchzoom reflog: last HEAD move 2026-10-22 13:16:48 +0200, before the start (17:18:44 +0200) | MET | - |
| 2 | V2 tau^2 = [A1], reader for reader | vault log line, `[4557s]` stripped, is string-equal to work_run.log L3 (the [A1] full-WORK line; L18 is the dress rehearsal's pseudo-split line, not [A1]) and occurs once in the programme (`grep -o` count = 1); meta.json `tau2` == [A1] chain dict True (12 / 12), `tau2_axis` == {L3a .01, L3a1 .02} True; outcome.json the same; own CV re-selection (library `step`, library inner contexts, 5 backbones): L1 .04, L2 .04, L3t 0, L3a .01, L3a1 .02 = meta; main-context eta, library step vs own reader: max abs 1.8e-15 | MET | - |
| 3 | V3 record untouched | `git log 1aa43079..HEAD -- <programme, READY1, READY2>` counted by `wc -l` = 1 (7618b2a5, the READY-2 itself, 15:17:12Z, before the start); `git diff --quiet HEAD` on the three: clean; runner `section_text` sha = b99772da (True); meta.json section_sha256, runner_blob, pins = the runner's (True x3) | MET | - |
| 4 | V4 one run, inputs | vault_run.log: 1 CMD line, 1 EXIT line (35 lines, read whole); write-once refusals (`vault_refusals`, `more_core`) refuse a second read; mtimes meta.json 16:34Z = start + 4,557 s, outcome 18:08Z; outcome.txt = log L13-L33 (diff: one trailing blank line). Interpreter: the CMD echo is fixed text; the venv is implied (the system python has no benchzoom), not printed | MET (interpreter by inference) | LOW |
| 5 | V5 sums, backup, quotation | `sha256sum -c SHA256SUMS_vault` 7 / 7 OK, file sha256 cc2f5d48 = brief; vault_read/SHA256SUMS 5 / 5 OK; E:/TaxoArena_backup_2026-10-22_mmlupro_more_vault: 7 / 7 and 5 / 5 OK, `cmp` byte-equal 7 / 7; DEFF, n_eff, MDE80 beside C-P1: row 7; label on every quotation: this file | MET | - |
| 6 | C-P1 g +0.0530 SE 0.0170 | own +0.052972 / 0.016959, iid SE 0.008425, n 4,654, G 4,625, cells 1,489,280 (0 NaN), tau^2 .01; record +0.052972 / 0.016959 (abs diff 1.5e-16) | CONFIRMED (digit) | - |
| 7 | Support line: DEFF 4.052, n_eff 1149 / 4654, MDE80 0.0651 | DEFF = (0.016959 / 0.008425)^2 = 4.0517; n_eff = 4,654 / 4.0517 = 1,148.6; MDE80 = 3.84 x 0.016959 = 0.06512 < 0.10. This DEFF is the cross-model within-item one: twin clusters are 4,625, max size 2, Kish size sum(n^2)/sum(n) = 1.0125 (registration (a) printed the plain mean 1.006). Realised DEFF sits inside the [A1] WORK range 3.747-4.409; constant ICC forecast 2.82 understated it (rho 0.0057 at 23, 0.0096 at 320) | CONFIRMED | LOW (D3) |
| 8 | C-P1 word NOT SUPPORTED (by interest) | own [R2]: tau^2 .01 != 0; g 0.052972 > q95 0 (null branch silent); g + 2 SE = 0.086890 < 0.10, so (2) NOT SUPPORTED fires; see "Why" below | CONFIRMED | MEDIUM (D1) |
| 9 | C-P2 +0.2389 SE 0.0381 SUPPORTED (sec.) | own +0.238917 / 0.038052, DEFF 4.9346, z 6.28, g - 3 SE +0.1248, q95 0, tau^2 .02: SUPPORTED | CONFIRMED (digit) | - |
| 10 | C-P3 +0.0216 SE 0.0190 NOT SUPPORTED (sec.) | own +0.021580 / 0.018969, DEFF 2.9903, g + 2 SE 0.0595 < 0.10 (interest), z 1.14 | CONFIRMED (digit) | - |
| 11 | C-P4 +0.0495, C-P5 +0.0507 (no word) | own +0.049521 SE 0.016893 (315 models, cells 1,466,010) and +0.050732 SE 0.017166 (307, 1,428,778); z 2.93 and 2.96 (< 3); PP4 = C-P4 - C-P1 = -0.003451 | CONFIRMED (digit) | - |
| 12 | nulls q95 +0.0000, tau^2 = 0 in 184 / 144 | own `np.quantile(.95)` over nulls.json, 8 series x 200: all q95 0.000000. L3a-L2: 184 zero (one-to-one with the tau^2 = 0 draws), 16 negative, 0 positive (max 0; min -0.0183). L3a\|L1: 144 zero, 51 negative, 5 positive (all models max +0.0029; weak half 0 positive). Null = leaf permuted within category (registered); it preserves L1, not L2; it is NOT on the deciding path of this word (the interest clause decides; any higher q95 only adds the null branch) | CONFIRMED | - |
| 13 | harness PASSED | harness.json: 0 of 20 draws > +2 own SE (c = 2), mean -0.00097 < 0 (cannot exceed +2 SE), tau^2 0 in 18 / 20, the two others negative. Spot check from the file (the draws need the field readers on C; not re-fitted) | CONFIRMED (spot) | - |
| 14 | PP1 NOT HELD, PP2-PP4 HELD; falsifier not fired | PP1 0.052972 > 0.050 (word in set): NOT HELD, upward by 0.003; PP2 0.2389 in [.1,.5], SUPPORTED (sec.): HELD; PP3 0.0216 in [-.03,.08], word in set: HELD; PP4 -0.0035 in [-.02,.02]: HELD. FALSIFIER fires only on SUPPORTED: not fired; FAILS words (SUPPORTED, BELOW INTEREST, INCONCLUSIVE) not printed | CONFIRMED | - |
| 15 | L2 re-read placebo G(L2\|L2) (as POSTRUN_BZ-AXIS-CONFIRM-MMLU D1) | fine (L2) labels re-read on the fitted L2, tau^2 re-selected by the same CV: tau^2 .01, g +0.004913 SE 0.017059 (DEFF 6.79), i.e. 9% of C-P1. C-P1 net of it (per-item difference, clustered): +0.048059 SE 0.019449, z 2.47, net + 2 SE 0.0870 < 0.10 | COMPUTED | MEDIUM (D2) |

## Why C-P1 is NOT SUPPORTED although g - 3 SE = +0.0021 > 0

Registered rule (benchzoom docs/meter_registration.md Section 5, quoted by the section's criterion 1 as "the parent's [R2]
precedence, applied ONCE to the POINT with its SE ... no interval clause, rule 7"): "[R2] The words, in precedence order
(the first word that applies is the verdict): (1) DEGENERATE: tau^2 = 0 selected on WORK ...; (2) NOT SUPPORTED: g <= q95,
or g + 2 SE < delta_min; (3) SUPPORTED: g >= 3 SE AND g > q95 AND g >= delta_min; (4) BELOW INTEREST: g >= 3 SE AND g >
q95 AND g < delta_min ...; (5) INCONCLUSIVE: otherwise." The 3-SE clause appears only in (3) and (4); (2) precedes them.
Here g + 2 SE = 0.0530 + 0.0339 = 0.0869 < 0.10, so (2) fires on its interest branch. The conditions of (4) also hold
(0.0530 >= 3 SE 0.0509, > q95 0, < 0.10) and are never reached. At g = 0.0530 BELOW INTEREST is unreachable at ANY SE (it
needs SE >= (0.10 - g) / 2 = 0.0235 and SE <= g / 3 = 0.0177; feasible only for g >= 0.06); the only alternative word was
INCONCLUSIVE (SE >= 0.0235). 3-SE interval: [+0.0021, +0.1038] (it does not exclude 0.10; the rule excludes interest at 2
SE, one-sided p .023, not 3 SE). The 23-model read was NOT SUPPORTED "by null and interest" (g -0.0059 <= q95 +0.0005).

## 23-model -0.0059 SE 0.0183 vs 320-model +0.0530 SE 0.0170 (descriptive only)

Same items: yes (n_scored 4,654, clusters 4,625, dropped-ids sha256 4cd9a0a8, tree.csv 57050563, pickle e1d0b00a, 91
fine cells in both outcome.json files; 23-model file sha256 2b957d5d = runner REF23). Different denominators and fits:
cells 1,489,280 (320 x 4,654, 0 NaN) vs at most 107,042 (23 x 4,654); WORK-selected tau^2 L2 .04 vs .08, L3a .01 vs
.005; DEFF 4.052 vs 1.126; LOMO difficulties from 319 vs 22 other models. Difference +0.0589; a naive SE 0.0250 (z 2.36)
assumes independence, which fails: both share every item (the covariance needs a joint read = another opening) and no
test of it was registered. Within the 320, composition moves g: weak half +0.0216, so by the identity all = (weak +
strong) / 2 (full coverage: 1,489,280 = 2 x 744,640 cells) the strong half is +0.0844 (arithmetic from the record; the
script's by-product SE for it is not quoted). Roster size, roster composition and the roster-dependent tau^2 are
confounded: the difference may be quoted as "on the same items the 320-model fit's point is 0.059 above the 23-model
fit's", never as a roster(-size) effect.

## Defects

- **D1 (MEDIUM, wording vs substance):** "the NOT SUPPORTED holds" is literally right but the branch changed (null and
  interest at 23 models; interest only at 320) and the gain is detected at 3.12 SE, above all 200 null draws. The 3-SE
  edge is thin: C-P4 (z 2.93) and C-P5 (z 2.96) fall below it. Fix: every C-P1 quotation carries "NOT SUPPORTED by
  interest only (g + 2 SE = 0.087 < 0.10); g = 3.12 SE > null q95 0 (the [R2] (4) conditions hold; (2) precedes); 3-SE
  interval [+0.002, +0.104]"; no sentence "no gain" or "the null replicates" for this roster.
- **D2 (MEDIUM, interpretation):** the L2 re-read is +0.0049 SE 0.0171 here; quote "net of the L2 re-read +0.0481 SE
  0.0194" beside C-P1 (same rule as POSTRUN_BZ-AXIS-CONFIRM-MMLU D1). Net or not, the word is unchanged (net + 2 SE 0.087).
- **D3 (LOW, Support transport):** registration (c) carried n_eff 4,134 (23-model), realised 1,149 (3.6x smaller); the
  [A1] vault-SE forecast 0.0132-0.0144 understated the realised 0.0170 by 18-28%; the registered SE 0.0183 / MDE80 0.0703
  stayed conservative, and realised MDE80 0.0651 < 0.10 keeps SCOREABLE true after the run. Fix: record the realised
  values beside (b)-(e); relabel (a)'s 1.006 as the plain mean (Kish 1.0125).
- **D4 (LOW, V4):** the CMD echo prints "python", not the interpreter path. Fix (next runner/operator revision): echo
  `$(command -v ...)` or `sys.executable` into the log.
- READY-2 D1-D4 stand as written; D1 did not bite (V2 MET). Own mutants: none (numbers review of an unchanged blob; the
  independent recomputation replaces the scorer path; READY-2 X1-X3 cover the vault guards; suite not re-run, 107 passed
  at this blob in READY-2).

## Wording for the registrar (verbatim)

"BZ-MMLUPRO-MOREMODELS (2026-10-22, 0 LLM calls; RE-TEST, NOT fresh; 4th opening of the BZ-METER vault items; ONE vault
read, benchzoom 233b2f3, runner blob:306066ea, src tree c9809e98; POSTRUN docs/reviews/POSTRUN_BZ-MMLUPRO-MOREMODELS.md:
OUTCOME CONFIRMED). 320 new OLL v2 models x 4,654 kept vault items (4,625 twin clusters), x 1e-3 nats per cell. C-P1
G(L3a | L2) = +0.0530, item-clustered SE 0.0170, q95 +0.0000 (R 200), tau^2 0.01: NOT SUPPORTED by interest only (g + 2
SE = 0.087 < 0.10; g = 3.12 SE above a null whose 200 draws are all <= 0; 3-SE interval [+0.002, +0.104]). Support
realised: DEFF 4.052 (registered transport 1.1257), n_eff 1,149, MDE80 0.0651 vs delta_min 0.10. Net of the L2 re-read
(G(L2|L2) +0.0049 SE 0.0171): +0.0481 SE 0.0194. The NOT SUPPORTED holds; the falsifier did not fire. C-P2 G(L3a | L1)
+0.2389 SE 0.0381 SUPPORTED (secondary); C-P3 weak half +0.0216 SE 0.0190 NOT SUPPORTED (secondary); C-P4 without the 5
rostered reasoning models +0.0495 SE 0.0169 and C-P5 cap-3 +0.0507 SE 0.0172 (no word; both below 3 SE). Harness [R18]
PASSED. PP1 NOT HELD (g 0.0530 above [-0.02, 0.05]); PP2-PP4 HELD. Descriptive: the 23-model value on the same items
was -0.0059 SE 0.0183 (NOT SUPPORTED by null and interest); the difference is not a measured roster effect (shared items,
roster-dependent tau^2, no registered test)."

## Commands (read-only on every object of record)

```
cat -A E:/benchzoom_demo/mmlu_pro_more/vault_run.log          # whole, 35 lines; 1 CMD, 1 EXIT
cd E:/benchzoom_demo/mmlu_pro_more && sha256sum -c SHA256SUMS_vault | grep -c ': OK$'   # 7 (before and after); sha256 cc2f5d48
cd E:/TaxoArena_backup_2026-10-22_mmlupro_more_vault && sha256sum -c SHA256SUMS_vault (7 OK); vault_read: 5 OK; cmp x7 same
git -C benchzoom rev-parse HEAD HEAD:src/benchzoom; hash-object examples/mmlupro_more.py; status --porcelain | wc -l (0); reflog -5
git log --format='%h %cI' 1aa43079..HEAD -- docs/judge_v2_program.md docs/reviews/READY{1,2}_BZ-MMLUPRO-MOREMODELS.md | wc -l   # 1
sed -n 3p work_run.log vs grep 'WORK-side tau^2' vault_run.log (sed-stripped)       # STRING_EQUAL
python -I -c "<outcome.json crit arithmetic; nulls.json q95/pos/zero/neg per series; harness.json draws>"
.venv python -I -c "<section_text sha == SECTION_SHA; meta section_sha256/runner_blob/pins == runner>"   # True x4
OMP/OPENBLAS/MKL=8 benchzoom/.venv python -I E:/TaxoArena_tmp/postrun_more_vault/recompute.py > recompute.log   # rows 2, 6-12, 15
find E:/benchzoom_demo E:/benchzoom_cache -type f -printf '%T@ %s %p\n' | sort -k3   # before.txt = after.txt (5,266; diff 0)
```
