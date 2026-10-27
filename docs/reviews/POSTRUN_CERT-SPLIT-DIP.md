# POST-RUN review: CERT-SPLIT-DIP (run 2026-10-09; zero calls)

Reviewer: adversarial-reviewer, 2026-10-09, HEAD c5e2161b. Registration prog L24958-L24972 (e83b59d5); READY
`docs/reviews/READY_cert_split_dip.md` (4bb0b263, C1-C4); failed-precondition review `POSTRUN_cert_split_dip.md`
(4111aecf); ruling D1 L25210. Read-only. Rule 7: busy.ps1 rc 1 before any read. No judge call. Nothing written
except this file and scratch under E:/TaxoArena_tmp/postrun_csd.

## Verdict

**VALID.** Words of record: **SD0 SIZE-OK; SD1 SENSITIVE (60 of 60); SD2 POS-OK; F-SD NOT FIRED; P1-P6 HELD.**
SI-NULL-TRIAD: REFUSED at its SIN-3 identity precondition (0.9707 against the bar 0.99). Its files are in
HELD_not_of_record/. They are not of record and are not an SI-NULL-TRIAD outcome; its registration and its B1 stand.
SD1 qualifier (S-1 below, the Support question the operator raised): SENSITIVE is a point classification under the
registered DEFF 1.5. The realised dependence cannot be estimated at delta 6. The word holds within each category
separately (20 of 20 in each, against a per-category bar of 15). The registrar prints it with that qualifier.

## Per-claim table (deciding claims)

| # | claim | status | my number vs claimed | sev |
|---|---|---|---|---|
| 1 | Data object: script blob 1d46cd73 (LF, `git hash-object`; working tree clean for the 3 scripts, count 0), sha256-lf16 be9591398f263faa; si_null_triad 7928e99b / b7d5bd88d6022602; cert_planted 028f05a2. These equal the cache meta | CONFIRMED | equal on all 3 | - |
| 2 | Data root D1: --run read `.claude/worktrees/rp12-r2-run` (run.log L44: 6993 IDENTITY rows, mode=ro&immutable=1; L45: D0 max diff 1.34e-08; L47: G12 blob 21f110af OK, snapshot 20261001_094311) | CONFIRMED for dry-run and run | analyze opens no DB. It reads the cache plus the pinned cpl_sites.csv from --planted-dir, so the root does not touch its numbers. The operator log abbreviates the run line ("--data-root ...") and does not record the analyze line (L-1) | LOW |
| 3 | Planted inputs: planted_sites.tsv 14c626d5, planted_vectors.f32be 2135279e | CONFIRMED | my sha256: 14c626d51fea40e9 / 2135279ee9ea5c9d | - |
| 4 | Completeness: 1,700 dip tasks of 5,195; missing 0; set hash ca25c934b9a6cee2 | CONFIRMED | 1,700 unique dip sites. The dip classes sum to 1,700 (SIZE 300, POWER 450, E1 50, E2 20, POS 15, REC 210, RECX 60, R256 210+300+50+20+15). The other 3,495 tasks are triad S/G, not needed after identity FAIL (READY row 5) | - |
| 5 | Per-site p = min(1, 2 x median of 20), cert iff <= 0.05 | CONFIRMED | recomputed on 1,700 sites: 0 cert flips. 72 sites differ in p by at most 8.7e-07 (the stored ps are rounded to 6 dp) | - |
| 6 | SD0: SIZE 0 of 300, CP upper 0.0122; delta 0 0 of 15 at n 486 (0 of 15 at n 441) -> SIZE-OK | CONFIRMED | 0/300, 1-0.025^(1/300) = 0.012221; 0/15, 0/15. Every SIZE p = 1.0 (min 1.0) | - |
| 7 | **SD1 (DECIDING): 60 of 60 (30/30 n 486, 30/30 n 441) -> SENSITIVE** | CONFIRMED, and INDEPENDENTLY REPRODUCED | cache 60/60. My own re-implementation (own fresh plants from the registered seeds, own spherical k-means++, the registered halving seed, the pinned diptest 0.11.0, D0 rows from the E: planted file, no import of the tool) gives 60/60. Max p 0.0 and cos>0.9 share 1.0 on every site | - |
| 8 | Boundary agreement of the independent build (the discriminating deltas) | CONFIRMED | site by site, own vs tool: D0 30/30 agree (0 cert); D4 60/60 agree (6 cert); D5 60/60 agree (54 cert); D6 60/60 agree | - |
| 9 | SD1 reading: plain site null of record at delta 6 is 0 of 15 at n 486 and 0 of 15 at n 441 | CONFIRMED | cpl_sites.csv (E:, pinned): delta 6, n 486 15 NOT CERTIFIED (reached 300); n 441 15 NOT CERTIFIED | - |
| 10 | SD2: STRONG 5, MID 5, EDGE 5 of 5 -> POS-OK | CONFIRMED | POS 15/15 by class column. The outcome line has a cosmetic defect: "certified of 5 {...}" (L-2) | LOW |
| 11 | F-SD: elongation controls 0 of 70 (E1 0/50, E2 0/20); INSENSITIVE clause not fired | CONFIRMED | 0/50, 0/20, every p = 1.0. My own spot null (10 moment-matched Gaussians of the n 486 economics subsamples, 6 elongated clouds at ratio 3 and 10) gives 0 of 16 | - |
| 12 | Predictions P1-P6 HELD; Brier P1 0.0025, P2 0.0168 | CONFIRMED | delta 3 0/60 in [0, 8]; delta 4 6/60 in [3, 25]; delta 8 60/60 in [57, 60]. delta* is 5 for every category: n 486 D5 9/10 each, D4 0/0/3. Median 5 lies in [4, 6]. Brier 0.05^2 = 0.0025; 0.1^2+0.08^2+0.02^2 = 0.0168 | - |
| 13 | Support line: "declared DEFF 1.5, n_eff 40, MDE80 0.192; realised ICC undefined" | CONFIRMED as printed; INCOMPLETE vs C4 | see S-1 | MEDIUM |
| 14 | C1: SI_NULL_TRIAD_* moved to HELD_not_of_record/ before the backup | CONFIRMED | the backup holds them under HELD_not_of_record/. SHA256SUMS.txt covers 9 files, `sha256sum -c` all OK, its own sha256 is 77d686689dcaa178. The backup outcome is identical to the working copy | - |
| 15 | Scorer line (D-2026-10-08-5) | NOT APPLICABLE | `grep -c 'eval_results\|is_correct' cert_split_dip.py` = 0. The script reads no MATH correctness (L25323) | - |
| 16 | Split / leakage: TRAIN only, labels define the merged-pair populations only | CONFIRMED (READY row 6, unchanged blob) | run.log L44: TRAIN root IDENTITY 6,993 rows | - |

## Support and dependence (S-1; C4; the operator's DEFF question settled)

- **Which DEFF applies.** The registered DEFF of record is 1.5 (Support (b), a declared pilot assumption). L25155,
  "the DESCRIPTIVE-ONLY verdict at DEFF 2 unchanged", repeats the registration's conditional in (f): at DEFF 2.0 the
  line would grade DESCRIPTIVE-ONLY, MDE80 0.2214 by READY row 10. It is not a ruling that 2.0 applies. The SUPPORT
  line correctly prints 1.5.
- **Realised, from the cache's own clusters.** At delta 6 all 60 sites certify, so ICC and DEFF are undefined: there
  is no variance, as the outcome says. Cluster sizes: subsample m = 2 (30 clusters), so DEFF is at most 2.0;
  category m = 20 (3 clusters).
  At the adjacent deltas, ICC(1) on cert:
  - delta 4: subsample -0.094 (DEFF 0.91); category 0.263 (DEFF 6.0, n_eff 10). All 6 certified sites are physics.
  - delta 5: subsample -0.094; category -0.053 (DEFF about 1). 18/18/18.
  - On -log10 median p: category ICC 0.325 at delta 4, -0.053 at delta 5.
- **Consequence.** If the delta 4 category DEFF of 6.0 held at delta 6, the SD1 MDE80 would be
  2.8 x sqrt(0.1875 x 6 / 60) = 0.383 > 0.25. The line would then grade DESCRIPTIVE-ONLY. The point outcome
  60/60 = 1.00 clears the bar 0.75 by 0.25, which is beyond the MDE up to DEFF 2.55.
  The word itself does not depend on the DEFF. The point decides (registration), and each category alone is 20/20
  against a pro-rata bar of 15/20. That is the robustness statement.
- **Fix (registrar).** Print SD1 as "SENSITIVE (point classification at the declared DEFF 1.5; realised DEFF not
  estimable at delta 6; 20/20 in each of the 3 categories; category-level DEFF 6.0 at delta 4, descriptive)".
  Make no interval or generalisation claim beyond these 3 categories and this member.

## Disclosures owed (C3, C4)

- **C3 (LOW, disclosed).** E1/E2 seeds 20261208-20261277 (`E_SEED + i`, `E_SEED + 50 + i`) lie inside SIZE's
  `SIZE_SEED0 + idx` = 20261004-20261303 (si_null_triad L98; idx 204-273). They are the same normal streams in
  different covariance shapes, so F-SD's elongation clause and SD0 are mildly correlated. The consequence is nil
  here: all 370 sites have p = 1.0, far from either bar.
- **C4 (MEDIUM, disclosed above).** Category-level dependence is printed in S-1. Economics subsamples share 468-470 of
  486 items (Support (a)).

## Defects

- **S-1 (MEDIUM).** The Support line omits the category-level dependence the READY C4 required. Fix: the registrar
  records the S-1 qualifier with the SD1 word. No re-run.
- **L-1 (LOW).** run_operator_20261009.log abbreviates the --run command ("--data-root ... --pylib ...") and has no
  analyze command line. D1 compliance of --run is proved by run.log L44/L47. Analyze is root-independent. Fix: log
  full argv in future runs.
- **L-2 (LOW, cosmetic).** The SD2 outcome line reads "certified of 5 {'STRONG': 5, ...}" with no leading count. The
  numbers are correct. The outcome file is write-once, so leave it and quote the per-pair counts.
- **L-3 (LOW, carried).** The READY C2 test gaps (R2-R5, R7 survived) remain for the next delta. They have no bearing
  on this outcome: the class counts were verified by count (row 4).
- **Note.** The dip's uniform calibration is very conservative on this object: every null and control site gives
  p = 1.0. This is covered by the registration's "exact size" non-claim. Do not read SIZE-OK as a calibrated size.

## Commands (compact; scratch E:/TaxoArena_tmp/postrun_csd)

```
powershell -File E:/TaxoArena_tmp/busy.ps1            # rc=1 (free) before any read
git hash-object tools/analysis/{cert_split_dip,si_null_triad,cert_planted}.py   # 1d46cd73 / 7928e99b / 028f05a2
sha256sum tools/analysis/cert_split_dip.py tools/analysis/si_null_triad.py      # be9591398f263faa / b7d5bd88d6022602
sha256sum experiment_results/cert_split_dip/{CERT_SPLIT_DIP_OUTCOME.txt,cache.jsonl}   # a40ada93aa252597 / dffe346efa657eb6
python E:/TaxoArena_tmp/postrun_csd/recount.py   # 1700 sites; p/cert from ps: 0 flips; SIZE 0/300; D0 0/15+0/15; D4 3+3; D5 27+27; D6 30+30; D8, D10 30+30
python - (cert_split_dip_sites.csv class column)  # POWER 240/450, E1 0/50, E2 0/20, POS 15/15, SIZE 0/300, REC 128/210, RECX 0/60, R256 per outcome
PYTHONPATH=E:/TaxoArena_tmp/cert_split/pylib python E:/TaxoArena_tmp/postrun_csd/own_dip.py   # independent rule + fresh plants: D0 0, D4 6, D5 54, D6 60; site-by-site agreement 210/210
PYTHONPATH=... python E:/TaxoArena_tmp/postrun_csd/own_null.py   # own 10 moment-matched + 6 elongated: 0 of 16
python E:/TaxoArena_tmp/postrun_csd/dep.py       # ICC(1): D4 sub -0.094 / cat 0.263 (DEFF 6.0); D5 sub -0.094 / cat -0.053; D6 undefined
python - (cpl_sites.csv, delta 6)                 # plain null: n486 15 NOT CERTIFIED, n441 15 NOT CERTIFIED
cd E:/TaxoArena_backup_20261009_cert_split_dip && sha256sum -c SHA256SUMS.txt   # 9/9 OK; SHA256SUMS 77d686689dcaa178
```
