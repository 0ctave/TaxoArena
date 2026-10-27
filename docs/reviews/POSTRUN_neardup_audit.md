# POST-RUN review: NEARDUP-AUDIT (adversarial reviewer, 2026-10-04; zero calls)

Run: `python tools/analysis/neardup_audit.py --run` from main, blob:4122ba72 (LF; `git show 122d6fc5:tools/analysis/neardup_audit.py
| git hash-object --stdin` = 4122ba72...; the console PIN line prints the same, crlf16 4ba2a8971f5f764d). Outcome
`E:/TaxoArena_backup_2026-10-04_neardup_audit/neardup_audit_outcome.txt` sha256 0e47b6ed988b9983d9d0291b672d7c37eb6680184d28ea06cd50071047f2ae88
(= SHA256SUMS.txt, `sha256sum -c` OK; = the console's "wrote" line). Reviews: READY_neardup_audit.md, READY_neardup_audit_delta.md.

## VERDICT: VALID. ND1 UNDETERMINED (R1-DEPENDENT: primary-leaf-only reads LOSES); F-ND NOT FIRED. P1 HELD, P2 FAILED,
## P3 HELD, P4 HELD. SCOREABLE as registered (C-6 met). Conditions W-1..W-4 go into the record verbatim.

## Per-claim table (recomputed by my own script from the DBs, `mode=ro&immutable=1`, `split_side.stem_key` directly)

| claim | run | reviewer | status |
|---|---|---|---|
| positives / PLAIN-flagged at 0.95 | 70 / 70 over 70 ids | 70 / 70 (min cos 0.9802) | CONFIRMED |
| ND1 BLOCK-LOSS (R1) | 0.071, 5 of 70 | 5/70 = 0.0714 | CONFIRMED |
| ND1 bootstrap 95% (B 2,000, seed 20261004) | [0.014, 0.129] | [0.0143, 0.1289]; seeds 1, 2: [0.0143, 0.1429] (verdict seed-stable) | CONFIRMED |
| CP upper (decides only on a zero-width bootstrap; not here) | 0.159; bootstrap decides; agree | Beta(0.975; 6, 65) = 0.1589; both UNDETERMINED | CONFIRMED |
| ND1 verdict / F-ND | UNDETERMINED / NOT FIRED | 0.071 <= 0.10 and 0.129 > 0.10 -> UNDETERMINED | CONFIRMED |
| R1 sensitivity (primary-leaf-only) | 0.114 [0.043, 0.200] LOSES, R1-DEPENDENT | 8/70 = 0.1143, [0.0429, 0.2000]; CP 0.2128 | CONFIRMED |
| PLAIN recall / precision(LB) at 0.95 | 1.000 / 0.407 (172 pairs flagged) | 70/70; 70/172 = 0.4070 | CONFIRMED |
| P3 registered (unweighted) / R4 reading | 0.0122 / 0.0146 | 0.0122 / 0.0146 | CONFIRMED |
| members filing into a leaf that lists them | 0.8938 | 0.8938 | CONFIRMED |
| KMEANS-BLOCK BLOCK-LOSS (descriptive) | 0.009 (1/1/1/0/0 of 70) | spot check seeds 0 and 3: 1/70 and 0/70, iters 29 and 35 (as printed) | CONFIRMED (spot) |
| C-5 R512 slice | PIN "full dim 4096, sliced 512" | own read: all vectors 4096-d, sliced [:512] and re-normed; numbers above reproduce on that slice | CONFIRMED |
| C-6 support | deciding 70 pairs, Kish m 1.000 (clusters 1:70), n_eff 70, realised SE 0.0308, MDE80 0.086 | n_dec 70 >= 47, so SCOREABLE as registered (SE 0.0204 / MDE80 0.057 at the planning 0.03). At the realised point 0.071 the SE is sqrt(0.0714 x 0.9286 / 70) = 0.0308, MDE80 0.086: the point is 0.029 below the bar, inside one MDE, so UNDETERMINED is the expected word at this n, not a support failure | CONFIRMED |
| write-once, console | mode x; rc 0 | the directory holds exactly 2 files (outcome + sums); the console body after the header equals the outcome file byte for byte (`cmp`); scratch removed: True, no `neardup_` dirs left in E:/TaxoArena_tmp (count 0); no java running at review (count 0) | CONFIRMED |

The missed twins (deciding set; my script): R1 misses 5 = 3 EXACT (cos 1.0000; identical vectors) + 2 SAME-OPTIONS
(cos 0.9961, 0.9914), all single-leaf members. Primary-only adds 3 EXACT twins whose members are listed in 2 leaves and
file into the non-primary one. The mechanism the falsifier names (membership vs filing disagreement for near-identical
vectors) is present: 10.6% of all members (1 - 0.8938) file into a leaf that does not list them.

## Conditions / disclosures (verbatim for the record)
- W-1 R1-DEPENDENT: ND1 of record is UNDETERMINED under R1 (fixed pre-data, B-3 at L24174). Under the primary-leaf-only
  block, 8/70 = 0.114 > 0.10 reads LOSES and F-ND would fire. The registration's literal "the TRAIN member's construction
  leaf" is singular, so the record must not report the tree as a safe blocking index: "UNDETERMINED (R1); LOSES under
  primary-leaf-only membership".
- W-2 P2 FAILED for the reason B-2 foresaw: no stem-only tier exists, every twin has cos >= 0.980, so PLAIN recall is 1.000
  at every tau up to 0.98 (0.929 at 0.99). The registered band is scored as written.
- W-3 KMEANS-BLOCK (descriptive, [AN]): k-means at k = 87 loses 0.009 (seed mean; 0.6 of 70 twins) against the tree's
  0.071; tree minus k-means +0.063. Descriptive only: no interval, five seeds, and the tree is anchored (label
  information). It may be quoted as "k-means blocking lost fewer twins on this object, descriptively"; it is not a
  tested ordering.
- W-4 PROCESS (LOW): the "merge" 122d6fc5 is a single-parent commit (`git rev-parse 122d6fc5^@` = 4120f15a only;
  `merge-base --is-ancestor f7502b80 122d6fc5` rc 1). It touches 2 paths (the script and the delta review;
  `--name-only | wc -l` = 2), and the blob is identical to the reviewed 4122ba72, so the run is of the reviewed code.
  The record should say "squash-applied", not "merged".

## Registrar wording (proposed)
NEARDUP-AUDIT (2026-10-04, 0 calls) — VALID; ND1 UNDETERMINED (R1-DEPENDENT). BLOCK-LOSS 0.071 (5 of 70 PLAIN-flagged
stem_key twins), 95% cluster bootstrap [0.014, 0.129] (Clopper-Pearson upper 0.159, which agrees); primary-leaf-only
membership 0.114 [0.043, 0.200] reads LOSES. F-ND NOT FIRED (under R1). n 70 pairs / 70 EVAL ids, DEFF 1.000 measured,
SE 0.0308, MDE80 0.086: SCOREABLE; the point sits within one MDE of the 0.10 bar. P1 HELD (0.071), P2 FAILED (PLAIN recall
1.000; no stem-only tier, B-2), P3 HELD (0.0122 unweighted; EVAL-weighted 0.0146 beside), P4 HELD (k-means 0.009,
descriptive [AN]). Membership-vs-filing disagreement: 10.6% of TRAIN members file outside their listed leaves; 3 of the
5 misses are exact twins sharing a vector. Not shown: tree vs k-means or ANN as an index; paraphrases; the v2 split; any
decontamination verdict. W-1..W-4. Outcome on E: (sha256 0e47b6ed...), never committed.

## Commands (compact)
```
git show 122d6fc5:tools/analysis/neardup_audit.py | git hash-object --stdin; git rev-parse 122d6fc5^@; git show 122d6fc5 --name-only --format= | wc -l
cd E:/TaxoArena_backup_2026-10-04_neardup_audit && sha256sum -c SHA256SUMS.txt; ls -la (2 files)
cmp <(log minus header/scratch/wrote lines) neardup_audit_outcome.txt           # equal
post.py (scratchpad): own load of the 3 DBs (ro, immutable), R512 slice + unit norm, member-mean flatLeaf, stem_key positives;
  R1 / primary misses, CP via scipy beta, bootstrap seeds 20261004/1/2, PLAIN flagged pairs, fractions, self-filing,
  per-miss tier/leaf count/cos; k-means seeds 0 and 3 through nd.spherical_kmeans
ls E:/TaxoArena_tmp | grep -c neardup_ (0); tasklist | grep -ci java (0)
```
