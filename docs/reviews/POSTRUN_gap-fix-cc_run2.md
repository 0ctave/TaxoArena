# POST-RUN review GAP-FIX-CC (run of 2026-10-09; outcome of record candidate)

Object: `experiment_results/gap_fix_cc/gap_fix_cc_outcome.txt` (sha256 dadf3065…284abe05) and `gap_fix_cc_arms.csv`
(sha256 c42c3a91…3d3e427d), written by `tools/analysis/gap_fix_cc.py` blob:41aa53aa (merged to main by path in c5e2161b, which
touches 1 file). Registration prog L25029-L25041 with its brackets (P-1 L25212-L25219; F-GFC ruling 1 L25147-L25157). READY
58580670 (delta) / 3968447d. The earlier refusal review is `POSTRUN_gap-fix-cc.md` (443cf9ff). This file is written beside it
and does not overwrite it: on this case-insensitive filesystem, `POSTRUN_GAP-FIX-CC.md` would be the same file. Zero calls.
Read-only. `busy.ps1` returned 1 before my pool read.

## Verdict

**VALID.** Words of record:
- **GF1-CC (DECIDING, qwen3): PARTIAL.** CLOSED is REFUTED, which is scoreable: Q_e1sd1 and Q_e1sd3 each fail CLOSED on two
  counts, so the refutation does not rest on Q_e1sd2 alone. OPEN vs PARTIAL is DESCRIPTIVE-ONLY on all three trees under (f).
  The 3 trees are GAP-SHOWN out of 3.
- **F-GFC: NOT FIRED.** Under the ruled reading, m of c = 0 of 0. No qwen3 tree reads CLOSED.
- **GF1-N (SCORED SECONDARY, nomic; never joined): OPEN.** The tree words are OPEN, CLOSED, OPEN. GF1-N CLOSED is REFUTED. On
  both OPEN trees, OPEN vs PARTIAL is DESCRIPTIVE-ONLY under (f) (N-raw is 0.0059 from its bar, N_e1sd3 0.0090), so the word
  must be printed with that qualifier.
- **Predictions:** P1 occurred (Brier 0.2025); P2 HELD on 3 of 3; P3 HELD on 3 of 3; P4 PARTIAL (Brier 0.3850); P5 occurred,
  2 of 3 (Brier 0.0625); P6 OPEN (Brier 0.9850).

Conditions for the registrar (C-1, C-2, C-3) are listed under Defects.

## Per-claim table (deciding)

All my numbers come from my own Lloyd-WP, my own M1 (leaf-majority label, ties counted), my own stem_key-group bootstrap
(B 1,000 at seed 20260926, plus an independent B 4,000 at seed 7) and a cluster-robust normal SE. The V fits use the
registered fitter `FM.vmf_em` (unchanged) under the P-1 rule. MAP assignment is my own.

| # | claim (outcome) | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | hits for every arm the words read (T, WP_0, WP_5, V0-V4) on 7 trees | CONFIRMED | 56/56 hit counts equal to the CSV, e.g. Q_e1sd2 T 2590, WP_5 2628, V0 (seed 5) 2688 | - |
| 2 | Q_e1sd1: D_T -0.0253 [-0.0405,-0.0105]; D_R -0.0206 [-0.0339,-0.0059]; I_R +0.0047 [-0.0047,+0.0145]; bar 0.0361 (spread_V); PARTIAL | CONFIRMED | identical to the digit. B4000/s7: D_R UB -0.0075, I_R LB -0.0050; normal: PARTIAL | - |
| 3 | Q_e1sd2: D_T -0.0278; D_R -0.0170 [-0.0312,-0.0020]; I_R +0.0108 [+0.0031,+0.0184]; bar 0.0216; PARTIAL | CONFIRMED | identical. B4000/s7 UB(D_R) -0.0026; normal PARTIAL. This is the closest UB to 0, and the only tree whose not-CLOSED rests on UB(D_R) alone | - |
| 4 | Q_e1sd3: D_T -0.0234; D_R -0.0186 [-0.0320,-0.0043]; I_R +0.0049 [-0.0026,+0.0117]; bar 0.0191 (MDE80); PARTIAL | CONFIRMED | identical. Note: \|D_R\| sits 0.0005 under the bar, so its PARTIAL rests on the measured-discordance MDE80 0.0191, which is the registered rule. The registered 0.0176 would give bar 0.0183 and OPEN. GF1-CC is PARTIAL either way (2 of 3) | LOW |
| 5 | GF1-CC PARTIAL; CLOSED REFUTED (3 not CLOSED); F-GFC NOT FIRED | CONFIRMED | rule applied to my words: PARTIAL x3. The CLOSED refutation survives Q_e1sd2 flipping. Ruled F-GFC: c = 0, so NOT FIRED. The tool's parenthetical "(B-3: F-GFC needs all of them)" is the all-c reading that is not of record, and it gives the same result | LOW |
| 6 | nomic: N-raw OPEN (D_R -0.0244, bar 0.0185), N_e1sd2 CLOSED (D_R +0.0048 [-0.0077,+0.0173], LB(I_R) +0.0119), N_e1sd3 OPEN (-0.0286, bar 0.0196); GF1-N OPEN | CONFIRMED | identical. All three intervals agree under B4000/s7 and under the normal SE | - |
| 7 | N_e1sd1 descriptive only, never counted | CONFIRMED | OPEN (D_R -0.0500); excluded from GF1-N by `leg N1` | - |
| 8 | GAP-SHOWN 3/3 qwen3 and 3/3 nomic | CONFIRMED | UB(D_T) < 0 on all 6 (largest -0.0011, on N_e1sd2) | - |
| 9 | P-1 applied: only Q_e1sd2 V0 is replaced (seed 0 -> 5); 35 VFIT lines | CONFIRMED | my fitter loop chose seed 5 independently. The VFIT lines are byte-identical between the dry-run and the outcome (`diff`) | - |
| 10 | denominators 3,598 / 3,522 / 3,500 (nomic 3,445 / 3,522 / 3,500); groups 3546 / 3479 / 3442 | CONFIRMED | my stem_key groups match. Kish m-bar 1.0295 / 1.0250 / 1.0331 (N-raw 1.0000) | - |
| 11 | Support re-measured (rule 8) | PARTLY | DEFF 1.0 was transported; the measured upper bound is 1.03. SE(D_R) is 0.00680 / 0.00728 / 0.00689 against the registered 0.00630. MDE80 is 0.0190 / 0.0203 / 0.0191 against 0.0176. Discordance is 0.166-0.185 against 0.1388, so the SE was understated by 8-16% through discordance, not through DEFF. n_eff is 3495 / 3436 / 3388. No word changes. The (f) "within 0.0176" test gives the same classification at the measured MDE | LOW |
| 12 | hygiene: fit inside TRAIN, held-out in fit 0, shared stem_key 0 (D-3 N-raw 0) | CONFIRMED (printed lines) | all 7 HYGIENE lines read 0. N-raw's D-3 count of 0 equals the recount in 443cf9ff. The pins are unchanged | - |
| 13 | scorer line (D-2026-10-08-5) | N/A, CONFIRMED | `grep -ci 'is_correct\|mathfix\|eval_results'` returns 0 in gap_fix_cc.py and gap_fix.py. flat_mix_mmlu.py has 2 hits, both in its DB-hash table only. M1 reads categories, never correctness (prog L25323) | - |
| 14 | READY conditions: merge by path, `--run --nomic-leg e1-guard`, busy rc 1 before the dry-run and the run, write-once, backup | CONFIRMED | c5e2161b touches 1 file, blob 41aa53aa. Stdout shows `[MODE] --run (nomic leg: e1-guard)`. run.log shows busy rc 1, dry rc 0, busy pre-run rc 1, run rc 0. Backup `sha256sum -c` gives 5/5 OK | - |
| 15 | wrong(established) / McNemar | N/A | no judge verdict enters, as the outcome states | - |
| 16 | no DB write by my readout | CONFIRMED | size+mtime of 421 *.db/-wal/-journal (maxdepth 4) identical before and after (`diff` empty) | - |

Descriptive spot checks: the M1 tie cells number 0-2 per arm (first-encountered majority, the same in tool and mine), which is
immaterial to every word. On predictions, the P2/P3 band membership and the P1/P4/P5/P6 Brier values were recomputed by hand
and agree.

## Defects / conditions

- **C-1 (registrar; MEDIUM; wording):** record GF1-N as "OPEN (OPEN vs PARTIAL DESCRIPTIVE-ONLY on both OPEN trees, (f))".
  Record GF1-CC as "PARTIAL (CLOSED REFUTED, scoreable; OPEN vs PARTIAL DESCRIPTIVE-ONLY on 3/3)". Neither word may be quoted
  bare. GF1-N is never joined with GF1-CC (S4).
- **C-2 (registrar; LOW):** F-GFC is scored from the ruled m-of-c line (0 of 0). Record that the tool's "(B-3: … all of
  them)" text is the non-record reading. A one-word fix in a future delta (`gap_fix_cc.py` L695) would print "FIRES iff m >= 2".
- **C-3 (registrar; LOW; Support):** record the measured Support beside the registered one (row 11). The registered SE used
  GAP-FIX's discordance 0.1388, and the e1sd trees discord at 0.166-0.185. Disclose that Q_e1sd3's PARTIAL is 0.0005 under the
  bar (row 4).
- **D-1 (this review; LOW):** the review file name differs from the brief's `POSTRUN_GAP-FIX-CC.md`. That name maps
  case-insensitively onto the existing refusal review 443cf9ff, which would have been overwritten. The fix is this `_run2` file.
- The READY 58580670 items D-1..D-3 (B-7/B-8 record, ive-underflow wording, shared-pool wording) are still owed to the record.
  None of them is reached by this run: there is 1 replacement and VOID-TREE is 0.

## Commands

```
cd Z:/FAC/TUBerlin/THESIS/TaxoArena
git show c5e2161b --name-only --format= | wc -l ; git hash-object tools/analysis/gap_fix_cc.py      # 1 ; 41aa53aa
sha256sum experiment_results/gap_fix_cc/* ; (cd E:/TaxoArena_backup_20261009_gap_fix_cc && sha256sum -c SHA256SUMS.txt)  # dadf3065/c42c3a91 ; 5 OK
cat E:/TaxoArena_tmp/gfc_run/run.log ; grep -n '\[MODE\]' E:/TaxoArena_tmp/gfc_run/run_stdout.log   # busy 1/dry 0/busy 1/run 0 ; e1-guard
diff <(grep '^VFIT ' E:/TaxoArena_tmp/gfc_run/dryrun.log) <(grep '^VFIT ' experiment_results/gap_fix_cc/gap_fix_cc_outcome.txt)  # identical, 35
grep -ci 'is_correct\|mathfix\|eval_results' tools/analysis/{gap_fix_cc,gap_fix,flat_mix_mmlu}.py   # 0 / 0 / 2 (hash table)
powershell -File E:/TaxoArena_tmp/busy.ps1 ; echo $?                                                 # 1
find . -maxdepth 4 (*.db|*-wal|*-journal) -printf '%p %s %T@' | sort > before/after ; diff           # 421, identical
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/postrun_gfc/recompute.py      # rc 0; log E:/TaxoArena_tmp/postrun_gfc/recompute.log
#   recompute.py: loader of record (gap_fix_cc.load_real + admit e1-guard, read-only); OWN within-parent Lloyd (renormalised member
#   means, empty keeps previous, argmax within the current leaf's parent subtree, T=5), OWN M1 (leaf-majority over the label set),
#   OWN stem_key-group bootstrap (B1000 s20260926; B4000 s7) + cluster SE; V via FM.vmf_em under P-1; OWN MAP (log pi + log C_d + kappa mu.x)
```
