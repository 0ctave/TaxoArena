# POST-RUN review: ONLINE-REPLAY-LOMO stage 1 (--run, main, blob fb3a9563)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. The run was made from main after merge 59f2234c and the brackets b19a6f92
(committed 18:56:23; outcome written 18:58:31). `git hash-object tools/analysis/online_replay_lomo.py` on main =
**fb3a956369ad2e921b61202d4d9ff460c53eab03** (LF), which is the delta READY's blob. The working tree is CRLF (sha256-crlf16:d51138c3, printed
by the outcome). Outputs: `experiment_results/online_replay_lomo/outcome.txt` (84 lines, sha256 63ae0f8f…0e08) and
`online_replay_items.csv` (73,669 lines = header + 2 x (6,139 + 30,695), sha256 4766bb09…9345); both untracked
(`git ls-files` = 0). Console: scratchpad orl_run.log (85 lines).

## Verdict: VALID

All deciding numbers reproduce to the printed digit, from my own replay re-implemented on the raw inputs and separately from the
items CSV. The outcome was written once. **OL1 DIFFERENT (LOSS); OL2 NOT-STABLE; F-OL FIRES; P1 HELD; P2 FAILED; P3 HELD
(descriptive).** Two wording points bind the coordinator's summary: W-2 (the OOS AUROC is a ranking, not a catch rate) and W-4
(the tree's smaller loss than k-means flips under the unit-start rule).

**Java at run time.** Three java.exe were alive: the Gradle daemon, the Kotlin compile daemon, and the JUnit test worker of
`.claude/worktrees/gemma-own-bar` (`-Djunit.platform...gemma-own-bar\build\test-results\test`). That is a test suite, not a
construction or site null (no `-DoutDir` / `nullReps`). Rule 7 is not breached.

## Per-claim table

| claim (outcome) | mine | status |
|---|---|---|
| identities 0.7346 / 0.7265 / 0.7368 / 0.7289; I3 6,139/6,139; K_0 labels 12,334/12,334 | My own cells from snapshots, af_cells and the leaves CSV, plus us_fit: symmetric batch 0.7265 (tree) / 0.7289 (K_0) | CONFIRMED |
| OL1 D -0.0386 (online 0.6879 - batch 0.7265); SE 0.00644; 90% [-0.0492, -0.0280]; 95% [-0.0512, -0.0260]; DIFFERENT (LOSS) | Own replay (thresholds, stream, true-mean start, renaming, buffer ukm, filing): **D -0.0386**. CSV: -0.0386. My bootstrap (own RNG, B 4,000): SE 0.00648, 95% [-0.0513, -0.0259], DEFF 1.263. \|D\| > 0.020 and the 95% interval lies below 0 | CONFIRMED (SE gap 4e-5, from the stream) |
| per-replay D_m tree +0.0178 / -0.1391 / -0.1000 / 0.0000 / +0.0123 / -0.1420 (MMLU_PRO_LB, BBH, MATH, MUSR, IFEVAL, GPQA) | identical to 4 dp; thresholds, buffer counts and k identical (tau to 5 dp) | CONFIRMED |
| OL2 means-only churn 0.0304 / 0.0925 / 0.0082 / 0.0000 / 0.0079 / 0.0161; uppers 0.0373 / 0.1015 / …; NOT-STABLE (-MMLU_PRO_LB, -BBH) | own replay: identical churns; CSV percentile uppers 0.0372 / 0.1019 / 0.0105 / 0 / 0.0102 / 0.0194 | CONFIRMED |
| F-OL FIRES (mean refit, -BBH 0.0925) | follows from OL2. **Robust to the readings:** -BBH stays > 0.020 under unit start (0.0767) and under all-cells churn (0.0945); -MMLU_PRO_LB stays > 0.020 under unit start (0.0229) | CONFIRMED |
| P1 -0.0386 in [-0.080, 0] HELD (Brier 0.4850); P2 FAILED (-MMLU_PRO_LB, -BBH, -GPQA outside [0, 0.015]; Brier 0.6400) | same | CONFIRMED |
| P3 AUROC median 0.9049 HELD (descriptive) | own rank AUROC per replay: 0.9537 / 0.8296 / 0.8234 / 0.9959 / 0.9519 / 0.8578; median 0.9049 | CONFIRMED |
| k-means arm D -0.0687 [-0.0822, -0.0553]; churn -MMLU_PRO_LB 0.0331, -BBH 0.0758 | own replay -0.0687; same churns; AUROC median 0.8996 | CONFIRMED (descriptive) |
| tree-minus-k-means +0.0301 [+0.0151, +0.0449] | from my two D vectors: +0.0301 | CONFIRMED (descriptive) |
| written once; console = outcome | Both files have mtime 18:58:31 (mode "x" in code). One `===` block. All 84 outcome lines appear in the console in the same order (em dash normalised); the 1 console-only line is `WROTE (write-once) … sha256 63ae0f8f… / 4766bb09…`. No Traceback or REFUSED | CONFIRMED |
| D-5 transductive disclosure | printed in the outcome (DISCLOSURE (D-5)), and carried into the wording below | CONFIRMED |

**Support, re-measured.** OL1 DEFF 1.245 (mine 1.263) vs 1.223 transported. n_eff 4,931. SE 0.00644 vs 0.00547 registered
(discordance 0.206 vs 0.15 planned). MDE80 0.0180. TOST reach 0.0040, DIFFERENT reach 0.0254. The observed |D| 0.0386 clears
the DIFFERENT reach. No wrong-direction counts apply (declared-class keyed; no judge verdict).

## Wording the registrar must use

- **W-1 (OL1).** "Online replay files a left-out union member **3.9pp worse than a batch rebuild** with the same cells and filing
  rule: OL1 DIFFERENT (LOSS), D -0.0386, 95% [-0.0512, -0.0260] (6,139 items / 5,628 components, 6 replays, one draw)." The loss
  is concentrated: BBH -13.9pp, GPQA -14.2pp, MATH -10.0pp. MMLU_PRO_LB is **+1.8pp**; MUSR 0 (99.9% buffered); IFEVAL +1.2pp
  (n.s.). The pooled D is item-weighted (MMLU_PRO_LB 3,478 and BBH 1,718 of 6,139). Mirrored comparator beside: -0.0468.
- **W-2 (P3; the "positive part" needs this qualifier).** Write "new-domain OOS **ranking** AUROC median 0.905 (0.82-1.00 over
  six members; capability text, first time; descriptive)". Never write "OOS detection catches new domains". At the registered
  GATE operating point (TPR 0.95) the OOS trigger flagged **6.5% of BBH's streamed items, 9.0% of MATH's, 28% of GPQA's, 41% of
  MMLU_PRO_LB's, 69% of IFEVAL's and 99.7% of MUSR's**. The two lowest AUROCs (MATH 0.82, BBH 0.83) are the members with
  in-union neighbours. Their items were mostly absorbed into existing cells, which produced BBH's churn and loss.
- **W-3 (OL2 / F-OL).** "OL2 NOT-STABLE: the online mean refit moved 9.25% of in-member addresses when BBH was replayed and 3.04%
  for MMLU_PRO_LB (four replays <= 1.6%); F-OL FIRES: ids stay stable only with frozen means; the note's 'ids are immutable'
  online claim narrows to mean-freezing." This holds under the unit-start and all-cells readings too (both > 0.020 for BBH).
- **W-4 (tree vs k-means; DESCRIPTIVE).** "The k-means arm lost 6.9pp (D -0.0687); tree minus k-means +3.0pp [+1.5, +4.5]."
  It must carry: WILL-NOT-SHOW excludes tree-over-k-means superiority. Each arm is measured against its own batch (0.7265 vs
  0.7289). **Under the unit-start rule (descriptive) the order reverses (tree -0.0437, k-means -0.0393).** Never write "the tree
  absorbs new domains better than k-means".
- **W-5 (D-5, transductive).** "The online arm streamed the held-out member's EVAL and clustered it in the buffer (registered),
  so the 3.9pp loss is against a rebuild that never saw those EVAL items, and the comparison favours the online arm."
  Residual of "never touched": 15 TRAIN / 14 EVAL MATH and MMLU_PRO_LB text-shared items stayed in the MMLU_PRO_LB tree's fit.
- Scope: six sources, one draw, stage 1 only. Nothing is certified. No real traffic or drift.

## Conditions / defects

- **K-1 (before the registrar records):** back up both outputs to `E:/TaxoArena_backup_2026-10-03_online_replay_lomo` with
  SHA256SUMS.txt (none existed at review time: `ls -d /e/TaxoArena_backup_2026-10-03*` shows no online_replay entry). Never commit
  them.
- L-1 / L-2 of the delta READY remain LOW. L-1 is now moot: I recomputed the OL1 word from `online_ok - batch_ok` (LOSS). L-2: the
  "unit-start" line (first build's rule) uses n = TRAIN count; it is descriptive and affects only W-4's qualifier.

## Commands

```
git hash-object tools/analysis/online_replay_lomo.py   # fb3a9563 (main); git log -1 --format=%cI b19a6f92 -> 18:56:23
sha256sum experiment_results/online_replay_lomo/*; wc -l; ls -l --time-style=full-iso (both 18:58:31)
python (console vs outcome): 84/84 outcome lines in log, same order; 1 log-only WROTE line
python $TEMP/orl/post_csv.py      # CSV: D -0.0386 SE .00648 [-.0513,-.0259]; km -0.0687; per-replay D_m and churns
python $TEMP/orl/post_replay.py   # own replay from raw inputs: tau, buffers, D_m, churns, AUROCs all equal; pooled D -0.0386 / -0.0687
Get-CimInstance Win32_Process java.exe: Gradle daemon, Kotlin daemon, gemma-own-bar JUnit worker (no construction)
```
