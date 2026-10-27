# POST-RUN review: GRANULARITY-GT + HIER-F (one readout, zero calls)

Reviewer: adversarial-reviewer, 2026-10-04, at main a29895dd. Registrations and brackets: prog L24317-L24328 and L24430-L24441
(brackets L24321-L24325, L24433-L24438 as of a29895dd). Run log `E:/TaxoArena_tmp/ggt_run.log`; outcome
`E:/TaxoArena_backup_2026-10-04_granularity_gt/granularity_gt_outcome.txt` sha256 f338a3e6065433ee... (= its SHA256SUMS; equal to
the log body bar the em-dash encoding). Backup of record: `E:/TaxoArena_backup_2026-10-04_ggt` (outcome, sums, run log, the
reviewer's scripts and log; SHA256SUMS.txt verified by `sha256sum -c`). Nothing under experiment_results committed.

## VERDICT

| reading | as printed | review word |
|---|---|---|
| GR1 | MIXED (MASSIVE TREE-BETTER, CLINC NEITHER) | **VALID**, with disclosure C-1 (the MASSIVE comparator is a chained average-link) |
| GR2 | HELD | **VALID** |
| HF1 | TREE-BETTER on both | **VALID** as registered (like-with-like confirmed), with disclosure C-1; the size is the comparator's degeneracy, not a definition mismatch |
| HF2 | MIXED; FAILS "HELD REFUTED"; P2 Brier 0.5625 | **REFUTED as worded -> HF2 NOT EVALUATED**: CLINC NOT EVALUATED (criterion unreachable at any number of draws, D-1); MASSIVE ABOVE-RANDOM stands as a per-corpus word; the FAILS line and HF P2 are NOT SCORED |

Concurrency (RESP-PROFILE-INFO and three routing readouts in the window): **no effect on validity**. All are zero-call CPU
readers of other objects; no construction ran; the run's own before/after pins (ingest 487e0093..., emb 9e100e04...) are PIN OK,
the reviewer's re-run printed sha256+mtime of the ingest, embedding and snapshots DBs unchanged, and every deciding point
reproduces to the digit on a separate execution (deterministic readers; concurrency can change wall time only).

## Per-claim table (deciding claims; reviewer's number vs the outcome)

| # | claim | outcome | reviewer | verdict | sev |
|---|---|---|---|---|---|
| 1 | Pinned blob = main | blob:bcb4240d (LF) | `git rev-parse HEAD:` = `git hash-object` = bcb4240d; `git log e2c082ef..HEAD -- <path>` 0 commits; e2c082ef ancestor of HEAD. Main's working tree is CRLF (1867 CR bytes): the printed "working-tree bytes sha256 e54ade54..." is sha256-crlf16:e54ade5498dbf140; LF rendering sha256-lf16:3a9a38fc29c8012b (= READY) | CONFIRMED | LOW (D-4) |
| 2 | MASSIVE best-cut AMI coarse tree / avg | 0.65875 / 0.31837 | 0.65875 / 0.31837 (sklearn AMI; avg-link re-fit by scipy fcluster maxclust, ARI 1.0 to the script's leaves) | CONFIRMED | - |
| 3 | MASSIVE spread_B (R-2) | 0.03154; seeds .65637 .64775 .65080 .67587 .67928 | 0.03154; same five to 5 d.p. | CONFIRMED | - |
| 4 | MASSIVE D1 and interval (R-2) | +0.34038 [+0.32256, +0.34974], SE 0.00689 | +0.34038 [+0.32323, +0.34953], SE 0.00692 (own component bootstrap, B 1000, seed 4242) | CONFIRMED (gap <= 0.0007) | - |
| 5 | CLINC D1, spread_B, interval (R-2) | -0.02317, 0.03535, [-0.03051, -0.01740] | -0.02317, 0.03535, [-0.03002, -0.01792]; NEITHER because abs(D1) < spread_B | CONFIRMED | - |
| 6 | GR2 DP and p97.5 | M 0.67043 vs 0.30353; C 0.47730 vs 0.19703 | own DP code, same stream: identical; other stream (seed 77, 400): p97.5 0.29925 / 0.19717, 0 >= tree | CONFIRMED | - |
| 7 | HF fine tree / avg / D (R-2) | M .74780 / .26611 / +.48169; C .84700 / .33767 / +.50933 | identical (own loop implementation over every node) | CONFIRMED | - |
| 8 | HF1 spread_B and interval (R-2) | M .02675 [.46587,.49370]; C .01343 [.49610,.51694] | M .02675 [.46580,.49299]; C .01343 [.49647,.51750] (B 2000, seed 4343) | CONFIRMED | - |
| 9 | HF1 like-with-like | - | same TRAIN, same L, same HF code path for both arms, filing argmax-cos for both; node counts 160 vs 167 (M), 269 vs 277 (C). Average-link leaves: largest holds 8,455 of 9,870 TRAIN (85.7%), 21 singletons (M); 3,207 of 13,487 (23.8%), 32 singletons (C); tree's largest leaf 336 / 226 | CONFIRMED like-with-like; comparator degenerate (C-1) | MEDIUM |
| 10 | HF2 CLINC NOT ABOVE-RANDOM | HF 0.84700, p97.5 0.84757, median 0.84700, 200/200 >= | 0 of 150 fine classes have an internal best node; HF(tree) = the leaves+root floor 0.8469997 exactly; every permutation keeps the leaves' item sets, so HF(random) >= floor = HF(tree) for every draw: ABOVE-RANDOM is impossible, not underpowered. Draws are NOT inert (182/200 equal, 18 above; own 1000 draws: 938 equal, 1000 >=) | REFUTED as a test outcome -> NOT EVALUATED | BLOCKER on the word |
| 11 | HF2 MASSIVE ABOVE-RANDOM | 0.74780 vs p97.5 0.69713, 0/200 | 9 of 60 fine classes internal-best; floor 0.68717 = min of 1000 own draws; p97.5 0.69713 (same stream), 0.69910 (own); 0 >= | CONFIRMED (live test) | - |
| 12 | 44 duplicate MASSIVE TRAIN rows (D2 "negligible") | disclosed | 9,870 rows / 9,826 unique texts (CLINC 13,487 / 13,487). Average-link re-fit on unique texts: D1 +0.35155 (+0.0112), HF D +0.50398 (+0.0223); every word unchanged | PARTLY: words robust; "negligible" overstated (shift 1.6 SE of D1) | LOW (D-3) |
| 13 | Support re-measured | Kish M 1.0093 / C 1.0000, n_eff 4900 / 6672 | same; realised SE(D1) M 0.0069 (registered planning 0.0050), MDE80 0.019 vs D1 0.340; C SE 0.0033, MDE 0.009 vs abs(D1) 0.023; HF SE .0071/.0054 | CONFIRMED; planning SE under by 1.4x on MASSIVE, immaterial | LOW |

## Defects and fixes

- **D-1 (BLOCKER on the HF2 word)**: under the registered matched-shape permutation a leaf keeps its item set, so HF2 can
  only move through classes whose best node is internal (the pre-data D4 bracket said so). On CLINC that count is 0 of 150:
  HF(tree) equals the leaves+root floor and is <= every random draw by construction. The CLINC cell is NOT EVALUATED, HF2
  overall NOT EVALUATED (a both-corpora rule with one cell); the printed "FAILS: HF2 HELD is REFUTED" and "HF P2 event FALSE,
  Brier 0.5625" are NOT SCORED. MASSIVE ABOVE-RANDOM is carried as a per-corpus word (9 of 60 internal-best classes; tree
  0.74780 > p97.5 0.69713). Fix: registrar bracket on the HIER-F outcome; any future HF null must preserve what it conditions on
  (e.g. permute items or leaf contents, or score only internal-best classes), registered before data.
- **D-2 (MEDIUM, disclosure C-1)**: average-link (cosine) chains on MASSIVE (one leaf = 85.7% of TRAIN; AMI ~0 for k <= 12)
  and partly on CLINC (fine h 0.576). GR1 MASSIVE TREE-BETTER and HF1 TREE-BETTER on both are true of the registered
  comparator but say "better than a chained average-link", not "better than a competent hierarchy". Against the bisecting
  arm (descriptive): MASSIVE coarse best-cut tree 0.659 inside the seed range 0.648-0.679, HF 0.748 inside 0.724-0.751; CLINC
  HF 0.847 above all five seeds (max 0.822). Fix: the outcome text carries this sentence beside GR1 and HF1; no word changes.
- **D-3 (LOW)**: the D2 bracket's "effect negligible" is wrong in size (D1 +0.011, HF D +0.022 on deduplicated TRAIN), right in
  consequence (no word moves; both shifts favour the tree). Fix: bracket the D2 line with the shifts.
- **D-4 (LOW)**: the outcome's "working-tree bytes sha256 e54ade54..." is the CRLF rendering of main's checkout; name it
  sha256-crlf16:e54ade5498dbf140 beside sha256-lf16:3a9a38fc29c8012b; the blob of record bcb4240d is unchanged.
- **D-5 (LOW)**: the D4 bracket asked for the internal-best class count to be printed (descriptive); the outcome has 0 lines
  matching "internal" (`grep -c -i internal` on the whole outcome = 0). Supplied here: MASSIVE 9 / 60, CLINC 0 / 150.

No new mutants: post-run numbers review on the blob READY'd at bcb4240d (unchanged on main); the decisive discriminator for
D-1 is executed (floor == HF(tree) on CLINC, floor < HF(tree) on MASSIVE).

## Registrar duties

1. HIER-F outcome: HF2 NOT EVALUATED (CLINC NOT EVALUATED, D-1; MASSIVE ABOVE-RANDOM per corpus); FAILS line and HF P2 NOT
   SCORED; HF1 TREE-BETTER both, VALID, with C-1; HF P1 FAILED both, Briers 0.36 / 0.36 stand; HF P3 NOT EVALUATED.
2. GRANULARITY-GT outcome: GR1 MIXED VALID (C-1 on MASSIVE); GR2 HELD VALID, P2 Brier 0.0625; P1 MASSIVE FAILED, CLINC HELD;
   'GR1 NEITHER 0.6' NOT SCORED (GG-1); P3 Brier 0.0100 (descriptive).
3. Brackets: D2 shift (D-3); D4 counts (D-5); script hash kinds (D-4); realised Support (row 13); concurrency ruling (above);
   backup `E:/TaxoArena_backup_2026-10-04_ggt` (SHA256SUMS.txt).

## Commands

```
git rev-parse HEAD:tools/analysis/granularity_gt.py; git hash-object tools/analysis/granularity_gt.py   # both bcb4240d
git log --oneline e2c082ef..HEAD -- tools/analysis/granularity_gt.py | wc -l                           # 0
tr -cd '\r' < tools/analysis/granularity_gt.py | wc -c                                                 # 1867 (CRLF checkout)
git show bcb4240d | sha256sum                                                                          # 3a9a38fc... (LF)
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/ggt_review/rev.py   # rows 2-5, 7-13; DB sha+mtime unchanged: True
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/ggt_review/dp.py    # row 6
grep -c -i internal E:/TaxoArena_backup_2026-10-04_granularity_gt/granularity_gt_outcome.txt           # 0 (D-5)
(cd E:/TaxoArena_backup_2026-10-04_ggt && sha256sum -c SHA256SUMS.txt)                                 # 5 OK
```
rev.py: imports the pinned loader and TRAIN fits (granularity_gt.load_all / train_phase) only; AMI = sklearn; average-link
re-derived by scipy fcluster(maxclust); HF, the component bootstrap, the leaves+root floor and the permutation nulls are the
reviewer's own code (copies in the backup, `review/`).
