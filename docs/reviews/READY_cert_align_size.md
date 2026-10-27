# READY review — CERT-ALIGN-SIZE (tools/analysis/cert_align_size.py)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Registration: prog L24245-L24257 (feac5b3d), `_as_of` b66b075d.
Reviewed: branch `cert-align-size`, tip 3f2dccb3; script `blob:80f7bb788f4feac0538eb1826e3febdfd79fa81d`,
`sha256-lf16:a24389e66dc26913` (LF, of record; working tree is LF, 0 CR lines by `grep -c $'\r'`; CRLF rendering
`sha256-crlf16:dd451ec699cdbdda`). `git hash-object` (working tree) = `git rev-parse HEAD:<path>` = the blob printed by the script.

## Verdict

**READY WITH CONDITIONS.** CA1's decide path, the data object, the denominators and the P9 loader gate all hold under my
own commands. C1 (HIGH) and C2 (MEDIUM) are pre-data registrar brackets to land BEFORE `--run`; they need no code change.
C3-C5 are LOW/MEDIUM brackets or post-run duties. No blocker.

## Per-claim table (deciding claims)

| # | claim | mine vs claimed | state | sev |
|---|---|---|---|---|
| 1 | deciding denominator 268 sites / 52 certified (plan ~280 / ~60) | 268 / 52 (af_clean_s42 14/69, af_s137 12/64, af_s2048 10/66, af_s42_o1 16/69); every graph split site has a null row (0 missing in all four) | CONFIRMED (12 short of 280, 8 short of 60) | - |
| 2 | P9 loader reproduction 0.12146 / 0.07402 | own arithmetic on `load_arm` Y: raw 0.12146, depth-stratified 0.07402 (16 cert / 85 uncert, w 11, 1,401 multi-holder slots) = record 0.1215 / 0.0740 | CONFIRMED to the digit | - |
| 3 | P9 gate is a real discriminator | geometric NMI -> 0.14145 / 0.08552; little-endian vectors -> 0.12162 / 0.07253; both NOT REPRODUCED, run refuses; unsliced vector -> exception | CONFIRMED | - |
| 4 | inputs pinned | 4 deciding CSV blobs = `17a44347:<path>`; o0 = 17a44347; 20NG = HEAD blobs (last touched 0b99e9aa / 88049302); reps 300 and snapshot ids enforced | CONFIRMED | - |
| 5 | read-only, no writes | size + mtime of snapshots.db / mmlu_pro_dataset_cache_v2.db / twenty_newsgroups_cache_v1.db / embeddings_cache.db identical before and after selftest, dry-run, mutants and my scripts; all -wal 0 bytes; worktree `status --short` 0 lines | CONFIRMED | - |
| 6 | registered Support (d)-(f): SE 0.0166, MDE80 0.041, SCOREABLE thin | arithmetic reproduces (0.10 x 0.1458 x 1.140 = 0.0166) but for an UNSTRATIFIED two-sample gap, not the registered estimator G. SE of G (w = min over the 16 contributing strata; 57 sites in 4 dropped strata) = 0.1798 x SD, x sqrt(1.3) = 0.2050 x SD. At planning SD 0.10: SE 0.0205, MDE80 0.0510 > 0.05 = prediction-to-bar distance. Script's printed clause uses sqrt(1/nc+1/nu) (0.1761 x SD), i.e. reads "beyond the MDE" for any SD < 0.114 where the estimator's SE says "beyond" only for SD < 0.098 | PARTLY (C1) | HIGH |
| 7 | "at matched size" | q4 (n 701-8,132) carries 25 of 50 stratum weight; certified geo-mean n 2,163 vs uncertified 1,103; all four roots (n ~8,130) certified and in q4; q0-q3 balanced (169/145, 220/218, 305/322, 534/506) | PARTLY (C4) | MEDIUM |
| 8 | DEFF 1.3, source | DECLARED PILOT ASSUMPTION, no measurement; sites nested in parent-child chains (member slots 177,145 over ~8,130 members per tree) | stated, unmeasured (C5) | LOW |
| 9 | CA1 decide path | `ca1_decide`: G > 0 AND p <= 0.05; boundary mutants M7 / M8 killed; numpy scalars handled | CONFIRMED | - |

## The builder's readings (which need registrar brackets)

| reading | finding | bracket? |
|---|---|---|
| (1) multi-holder members assigned by cosine to child vmfMu via `embeddings_cache.db` | 953 / 913 / 946 / 919 of 45,968 / 42,866 / 44,619 / 43,692 deciding member slots (2.1%). P9's `assign_child` rule verbatim in form; `len(vmfMu)` = `sliceDim` on every node of all 7 snapshots (256; T1b 512), so `[:d]` is the node's slice. Big-endian decode = `anchor_free_readout`. The read is NOT in DATA OBJECTS (which names the snapshots for child assignment) | YES (C2) |
| (2) size quintiles pooled over the four trees | as registered. Convention "stratum = cutpoints strictly below log n": 2 deciding sites sit exactly on a cutpoint (n 374.0 is one) and go DOWN; mutant R1 (<=) moves fixture G 0.875 -> 0.791. Descriptive arms use their own pools (registration silent) | YES, LOW (C3) |
| (3) depth x tree for the beside depth-gap | P9's form had one tree; crossing with tree is the like-for-like reading; descriptive only | YES, LOW (C3) |
| (4) ties counted against, p = (1+ge)/(1+N) | P9's conservative form; standard | no |
| (5) SIZE-ONLY when G cannot be formed | literal "SIZE-ONLY otherwise"; unreachable on the data (16 of 20 strata hold both classes, dry-run counts). Note: P9 bracketed the same case UNDETERMINED (topic_partition bracket (e)); the registrar may record the divergence | no (note) |
| (6) root of o0_clean_s42 has no null row | the root's 14 children are the 14 declared categories (anchor split, not a construction split); o0 arm = 60 sites; descriptive (P4) only | YES, LOW (C3) |

**Like with like on labels: CONFIRMED.** Deciding trees [LF], 14 MMLU-Pro categories (lower-cased), 11,769 distinct texts;
4 texts carry two categories, touching 4 deciding members (1/2/0/1), resolved by the first-row rule: negligible. o0 [AN]
is anchored on the same 14 categories (alignment partly by construction; descriptive). 20NG uses 20 labels: its NMI level
is not on the MMLU scale; P3 is a band on its own scale, never a cross-corpus contrast. The contrast is within tree x
size stratum, so the 14-vs-20 difference never enters CA1.

## Mutants (selftest 48/48 OK, re-run; sandboxed copies under E:/TaxoArena_tmp/cas_review/mut, TMP/TEMP/TMPDIR redirected)

Builder's decisive mutants re-run: M1 killed (G 0.7000), M2 killed (0.6667), M4 killed (T1b p 0.9040), M5 killed (p 0.0000),
M6 killed (SIZE-ONLY p 1.0), M7 killed, M8 killed, M9 (Y=None variant) killed by exception, M10 killed (G -0.875),
M11 killed (0.8462), M18 killed. Mine:
- R1 cutpoint `<` -> `<=`: killed (G 0.7906). Decisive (convention; C3).
- R2 NMI arithmetic -> geometric: SURVIVED the selftest; caught at run time by the P9 gate (20NG 0.14145 / 0.08552). Decisive, covered.
- R3 vectors `>f` -> `<f`: SURVIVED the selftest; caught at run time by the P9 gate (0.12162 / 0.07253). Decisive, covered.
- R4 permutation seed + 1: SURVIVED. Not decisive (p reproducibility only; the seed is printed).
- R5 ties counted for (`g > g_obs + eps`): killed (T1b p 0.0005).
- R6 o0_clean_s42 added to DECIDING: killed (100 sites).
- R7 vector not sliced: SURVIVED the selftest (fixture D = slice = 4); real data raises ValueError. Not silent.

## Defects and conditions (fix each)

- **C1 HIGH (pre-data bracket, before --run).** Support line (f) is applied with the SE of the REGISTERED estimator:
  SE_G = sqrt(sum_h w_h^2 (s_c,h^2/n_c,h + s_u,h^2/n_u,h)) / sum_h w_h x sqrt(1.3), or the printed permutation SD of G
  x sqrt(1.3), the larger. The script's "beyond / NOT beyond the MDE" clause (support_lines, sqrt(1/nc+1/nu)) is NOT of
  record. At planning SD 0.10 the realised design gives MDE80 0.051 > 0.05: the test is at the SCOREABLE/DESCRIPTIVE-ONLY
  edge, not "SCOREABLE, thin". CA1 itself is unaffected. Optional code fix: compute SE_G in `support_lines` (delta review, <= 3 mutants).
- **C2 MEDIUM (pre-data bracket).** DATA OBJECTS gains `embeddings_cache.db` (qwen3, read-only, immutable after -wal check;
  vectors of multi-holder TRAIN members only, 2.1% of slots), child = higher cosine to the child's vmfMu in its sliceDim (P9's rule).
- **C3 LOW (pre-data bracket).** Record readings (2) cutpoint convention and own-pool quintiles for descriptive arms,
  (3) depth x tree for the beside gap, (6) o0 arm = 60 sites, the declared-category root split has no null row.
- **C4 MEDIUM (post-run duty).** Size is not matched inside q4 (2,163 vs 1,103, 25 of 50 weight). The post-run prints G
  beside the OLS cert coefficient (log n adjusted, already printed) and recomputes G without the four depth-0 roots,
  DESCRIPTIVE; if G and the adjusted coefficient disagree in sign, the post-run says "matched size" holds only for q0-q3.
- **C5 LOW (post-run duty).** Nested sites share members; within-stratum permutation treats them as exchangeable (p may be
  anti-conservative). DEFF is not measurable at 4 tree clusters; the post-run states 1.3 stays an assumption, prints n_eff
  = 268 / 1.3 = 206 (certified 40) and the C1 SE/MDE beside G.
- LOW: the script does not refuse a DECIDING arm with graph sites lacking a null row (it prints the count; 0 on the data).
  LOW: R4 shows the seed is not asserted by the selftest.

## Launch (from the worktree; the worktree holds no snapshots.db, so --data-root is required there)

`python tools/analysis/cert_align_size.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`
(default out `E:/TaxoArena_backup_<date>_cert_align_size/cert_align_size_outcome.txt` + SHA256SUMS.txt, write-once;
from main after a merge, `--data-root` may be omitted.)

## Commands

```
git -C .claude/worktrees/cert-align-size rev-parse HEAD:tools/analysis/cert_align_size.py ; git hash-object <same>   # 80f7bb78
git rev-parse 17a44347:experiment_results/anchorfree/redraw/site_null_<arm>.csv                                      # 4 deciding + o0 pins
python tools/analysis/cert_align_size.py --selftest                                                                  # 48/48 OK (worktree)
python tools/analysis/cert_align_size.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena                      # 268 / 52; counts per tree x quintile
E:/TaxoArena_tmp/cas_review/chk1.py   # vmfMu length = sliceDim on all nodes; o0 root children = 14 declared categories
E:/TaxoArena_tmp/cas_review/chk2.py   # 20NG raw 0.12146 / depth 0.07402; label conflicts 4; cutpoint ties 2; SE_G/SD 0.1798 (x1.140 = 0.2050); MDE80(SD .10) 0.0510
E:/TaxoArena_tmp/cas_review/chk3.py   # within-quintile geo-mean n by class; four roots certified in q4
E:/TaxoArena_tmp/cas_review/mut/harness.py ; real20ng.py R2|R3|R7                                                    # mutant table above
stat -c '%n %s %Y' snapshots.db mmlu_pro_dataset_cache_v2.db twenty_newsgroups_cache_v1.db embeddings_cache.db       # before = after
```
No Y was computed on the deciding arms (chk2/chk3 use `with_y=False` there); only the SEEN 20NG arm's Y was read.
