# POSTRUN review: G13-BREAKDOWN --run (lane r2), outcome commit 7f7b0fe3

Outcome of record: `experiment_results/archv2/rp12_r2/g13_breakdown_outcome.txt`, 148 lines, blob:3ca9629b89b6a4786a05f5df77f5bb8219380d7c
(= HEAD blob; LF, 0 CR, ends with a newline; sha256-lf16 9a9605c70cb6d384). Script of record `tools/analysis/g13_breakdown.py`
blob:c29fa1c3 (LF; the main working file hashes to the same blob, so no CRLF rendering differs). Registration prog L22887-L23048
_as_of ffed1d52; READY 7e6858eb + delta ac7bb984 (conditions C2-C5). Reviewer: adversarial-reviewer, 2026-10-02. Zero calls.
RP20: no file of it opened or written.

## Verdict

**VALID**, with wording conditions W1-W7. All five criterion lines reproduce item-for-item; C4 holds to the digit; the outcome
is complete and is the text the code writes (every line but the 12 wall-clock lines reproduces byte-identical). C-M's G_own
= 0 is a **real, structural zero, not a code degeneracy**: at seed 0 the relabel renames 0 of 133 KC prototypes, so KC-relabel_0
equals KC_0 item for item. The verdict UNDETERMINED is the correct output of the registered rule, but its printed Support
(SE 0, DEFF nan, MDE80 0) is degenerate and must not be quoted as precision (W4).

## Per-claim table (deciding claims)

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Outcome complete; = what the code writes | CONFIRMED | in-process re-run of main()'s --run path (no write): 148/148 lines; 136 identical; the 12 that differ are the wall-clock lines only (L72, L74-L81, L138-L140); every statistic, interval, verdict and prediction word identical. The file is written (mode `x`, utf-8) BEFORE `out(body)` (L1271-L1274), so the cp1252 crash came after a complete write | - |
| 2 | C-a1 HELD: D13_MMLU -0.0446 [-0.0566, -0.0321], n 3,478 / 3,386 comp | CONFIRMED | own -0.0446; own cluster bootstrap (other RNG, B 4,000) [-0.0575, -0.0317]; analytic cluster SE 0.00648, DEFF 1.074, n_eff 3,238, MDE80 0.0181 (printed 0.00639 / 1.046 / 3,325 / 0.0179); bar: 0.0446 > MDE80 | - |
| 3 | C-a4 HELD: Delta -0.0192 [-0.0292, -0.0089] | CONFIRMED | C4: D13 - (P_tree(2) - P_NCC) = -0.019221 = paired mean -0.019221; printed means -0.0215 - (0.8042 - 0.8065) = -0.0192; own interval [-0.0293, -0.0088]; SE 0.00522, DEFF 1.181 (printed 0.00514 / 1.147; registered SE 0.00466: measured SE 10% above plan, effect 1.3x MDE80) | - |
| 4 | C-b1 HELD: D_U +0.0738 [+0.0625, +0.0855], > spread_U 0.0414 | CONFIRMED | C4: 0.811859 - 0.738068 = +0.073791; spread_U 0.041375 (0.7573 - 0.7159); own [+0.0623, +0.0853], DEFF 1.370 | - |
| 5 | C-b2 HELD: D_Us +0.0656 [+0.0546, +0.0778], > spread_US 0.0233 | CONFIRMED | C4: 0.811859 - 0.746213 = +0.065646 (from the rounded printed means 0.8119 - 0.7462 = 0.0657: rounding only); spread clause reads spread_US 0.023294 (0.758755 - 0.735462), not spread_U (READY X1) | - |
| 6 | C-M UNDETERMINED: G_own +0.0000 [0, 0] | CONFIRMED (verdict); see W4 | own relabel from the run's prototypes: seed 0 renames 0 / 133 prototypes, 0 empty, 0 discordant EVAL items -> G_own identically 0; seeds 1, 3 also 0 renamed; seeds 2, 4 rename 1 prototype (BBH logical_deduction_five -> _seven; 32 vs 38 and 33 vs 38 of the TRAIN items nearest) and move 31 / 21 items, G_own -0.00049 / +0.00049. The code path executes and moves items when there is something to rename; on seed 0 there is nothing | MEDIUM (W4) |
| 7 | KC_0 filing reproduced independently | CONFIRMED | own argmax over the run's prototypes = script kc_ok[0] item-wise; P_fl 0.811859, P(KC_0) 0.833360 | - |
| 8 | C2 (8 TOTAL TIME blocks, no INCOMPLETE) | CONFIRMED | `grep -c "TOTAL TIME lines"` 8; `grep -c "INCOMPLETE\|ABSENT"` 0 | - |
| 9 | C3 machine state | PARTLY | printed: no java, BLAS 1,1, 31.4 GB free; ollama app/ollama admitted (whether an embedding was active is not shown). Timing is descriptive only: no verdict reads it | LOW |
| 10 | C5 D(>=5) as one prediction | CONFIRMED | -0.0005 / -0.0016 / -0.0007, all within 0.005; leaf-naming count printed 1 (as expected) | - |
| 11 | Timing: end-to-end / KC = 2,163x; timing predictions FAILED | CONFIRMED as printed; NOT STABLE to the digit | re-run: KC median 0.095 s -> 2,462x (members only 1,640x vs 1,441x). The ratio's denominator is a ~0.1 s fit; it moves ~14% between two runs on the same machine. KC 1-10 s, U-global 20-120 s and ratio 10-100x all FAILED by an order of magnitude in both runs | LOW (W6) |

C4 (READY): all four recomputed from the printed means and from the items; paired mean = difference of means in each case.
D-2 (fixtures degenerate on C-b2, C-a4, C-M, C-b1): on the real data C-b2, C-a4 and C-b1 are non-degenerate and reproduce;
C-M is degenerate on the real data too, for a structural reason (row 6), not because of the code.

## Defects

- **E-1 LOW (encoding incident).** `out(body)` prints Java's U+202F (narrow no-break space, 14 occurrences in the copied TOTAL
  TIME lines) to a cp1252 console and raises UnicodeEncodeError AFTER the write-once outcome is complete; the
  "wrote ... (write-once)" confirmation never printed, and attempt 2 refused correctly. No number is affected (row 1). Fix
  (forward only, not this blob): `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at entry, or the operator runbook
  sets PYTHONIOENCODING=utf-8 for every readout that copies JVM log text. **Record line: yes**, one sentence in the registrar's
  outcome record: "attempt 1 wrote the complete outcome (blob 3ca9629b) and then crashed printing to a cp1252 console; attempt 2
  refused write-once; POSTRUN_g13_breakdown re-ran the readout in-process: all non-timing lines identical."
- **E-2 MEDIUM (C-M Support vacuous after the fact).** The registered C-M Support (planning discordance 0.02, MDE80 0.0056)
  assumed the relabel moves items; observed discordance 0.0000 on seed 0. SE 0 / DEFF nan / MDE80 0 are printed as if
  measured. Fix: record C-M as "UNDETERMINED (degenerate: KC-relabel_0 = KC_0 item-wise; 0 of 133 prototypes renamed)"; no
  re-test of C-M in this form is informative at any n (the statistic is identically 0 on seed 0, |G_own| <= 0.0005 on 0-4).
- **E-3 LOW.** The ratio prediction compares a 12-thread JVM build (manifests) to a 1-thread Python fit of ~0.1 s; the
  printed ratio carries no run-to-run interval. Fix: quote it as an order of magnitude (W6).

## Wording conditions (VALID only with these)

- **W1** G13 FAILED stands: nothing here shows the tree is needed for filing (DOES-NOT-SHOW 1). No sentence of the form "the
  tree is competitive / matches KC".
- **W2** "Anchored tree (no LLM labelling; GT-seeded declared-class anchors)", never "label-free" (registrar Q1 bracket). C-b1 and
  C-b2 are wins over k-means that read TRAIN labels at naming only, while the tree also reads GT-seeded anchors (the outcome's
  LABEL LADDER). Do not write that the tree's data-driven split alone beats unsupervised clustering.
- **W3** C-a4 in the registered words: "the loss opens below the anchors" (Delta -0.0192 [-0.0292, -0.0089]), with "point seen
  before registration". D(2) -0.0023 [-0.0108, +0.0064] is UNDETERMINED: never "parity at the anchor level" (DOES-NOT-SHOW 2;
  no TOST). The same holds for MUSR (0 = 0 by ceiling, P 1.000 both) and every interval that contains 0.
- **W4** C-M: "UNDETERMINED; the mechanism test is degenerate: KC's own prototype classes already equal the TRAIN-majority
  classes on 133 of 133 prototypes at seed 0, so the relabel changes no filing (G_own = 0 exactly; |G_own| <= 0.0005 over
  seeds 0-4)". Do not quote [0, 0], SE 0 or MDE80 0 as precision; do not read it as "label ownership is ruled out by a test"
  nor as parity. Prediction G_own +0.012 FAILED.
- **W5** C-b1 carries "point seen before registration"; per-source lines other than MMLU are DESCRIPTIVE-ONLY (IFEval +0.0494
  [+0.0123, +0.0864] and BBH +0.0140 are not tree wins of record).
- **W6** Wall-clock: "about three orders of magnitude (2,163x in the run, 2,462x on a re-run) on this machine, 1-thread Python
  k-means against the 12-thread JVM build"; never a general cost ratio (DOES-NOT-SHOW 7); the timing predictions FAILED.
- **W7** The share 1.1742 (MMLU carries more than the whole net deficit) is descriptive; "MMLU-Pro carries the loss" is fine,
  "the tree loses only on MMLU-Pro" is not (other sources are descriptive and intervals contain 0).

## Commands

```
wc -l / git hash-object / git rev-parse HEAD:<outcome>         # 148; 3ca9629b both; 0 CR; U+202F x14 (python count)
git hash-object tools/analysis/g13_breakdown.py; git rev-parse HEAD:tools/analysis/g13_breakdown.py   # c29fa1c3 both
sed -n 1225,1276p tools/analysis/g13_breakdown.py              # open(outp, "x") + write precede out(body)
python scratchpad/pr/rerun.py   # imports the module, runs pool check + load_objects + identity_arms/check_i1 + compute +
                                # timing child + render, NO write; diff vs outcome: 12 lines differ, all wall-clock; 91 s
python scratchpad/pr/indep.py   # own KC filing, own cluster bootstrap + analytic cluster SE/DEFF for D13_MMLU, D13, Delta,
                                # D_U; C4 arithmetic; own relabel per seed (renamed prototypes, discordant items)
grep -c "TOTAL TIME lines" <outcome>  # 8 ;  grep -c "INCOMPLETE\|ABSENT" <outcome>  # 0
ls -l --time-style=+%T multicorpus_cache_v1.db*                # before = after (11:44:29; -wal 0 bytes 19:43:30)
tasklist java.exe                                               # none during the re-run
```
DB hygiene: the re-run opened the guard DBs read-only through the script's own loaders; sizes and mtimes unchanged; no outcome
or other file written outside the scratchpad.
