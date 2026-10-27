# READY review — CERT-SPLIT-DIP (+ SI-NULL-TRIAD joint leg), build 397ebd77

Reviewer: adversarial-reviewer, 2026-10-08. Zero calls; no pool read (fixture DBs and the pinned planted / KK files on E: only).
Registrations: CERT-SPLIT-DIP prog L24958-L24972 (e83b59d5); SI-NULL-TRIAD L24335-L24347 + SI-C1 (L24955).
Reviewed blobs (LF, of record; the working tree carries 0 CR bytes, so CRLF rendering = none):
- tools/analysis/cert_split_dip.py `blob:1d46cd733e8728a35a30e5c88df5a564d1d5961a` / `sha256-lf16:be9591398f263faa`
- tools/analysis/si_null_triad.py `blob:7928e99b6de1b5c9b6a98b67788f3c5e20dd9893` / `sha256-lf16:b7d5bd88d6022602`
- imported unchanged: tools/analysis/cert_planted.py `blob:028f05a2cd6db90c5a1c76b36923647033127805`
Commit 397ebd77 touches 2 files (`git show 397ebd77 --name-only --format= | wc -l` = 2); parent e83b59d5 (ancestry checked); NOT yet in main (375cbcc9 touches none of the three files: count 0).

## Verdict

- **CERT-SPLIT-DIP: READY**, under conditions C1-C4. The dip rule, the site classes, every deciding denominator and word (SD0, SD1, SD2, F-SD) implement the registration. The dip leg does not depend on the proxy or on the identity word.
- **SI-NULL-TRIAD: NOT READY** (B1, HIGH, C-7 SUBSTITUTED). Under the kept reading SIN-2/SIN-4, arm S's null covariance and G_S's matrix are exactly the site's own projected covariance. That is the object the registered question excludes ("a site null whose covariance is not taken from the site"). The registrar must rule on this before any S / G_S word can be of record.
- The joint run may go ahead as built (one launch, no code change). Its SI-NULL-TRIAD outputs are NOT of record (C1).

## Per-claim table (deciding claims)

| # | claim | result | evidence (mine) | sev |
|---|---|---|---|---|
| 1 | The rule = registration (R 20; halving seed sha256(name) mod 2^32 + r; skmeans k 2, ++ init, 10 restarts, <= 100 it; u = c1 - c2 on A; dip of B; p = min(1, 2 median); <= 0.05) | CONFIRMED | read L240-L316. k-means++ on 1 - cos = ||x - y||^2 / 2 for unit rows, so the D^2 weighting is correct. Own mutants R6 (dip on A) and R8 (p := 1 - p) KILLED | - |
| 2 | Fresh plants: u = Random(20261008000 + 10d + j), halves = Random(20261108000 + 10d + j), plant_rows unchanged | CONFIRMED | U_SEED0 / H_SEED0 = 20261004 / 20261104 (cert_planted L150); offsets cancel. M38, M48 and own R1 (plant j ignored) KILLED | - |
| 3 | Denominators: SIZE 300, SD1 60, E 70 (50 + 20), POS 15, d0 15 at n 486 | CONFIRMED | `--selftest-io` site line: SIZE 300 / POWER 450 / E1 50 / E2 20 / POS 15 / REC 210 / RECX 60 / G12 60 / R256 classes 210 + 300 + 50 + 20 + 15. Tasks 5,195 = my hand count (1800 + 210 + 1200 + 300 + 200 + 50 + 80 + 20 + 60 + 15 + 840 + 240 + 180). Strict readout REFUSES other counts | - |
| 4 | SD0 / SD1 / SD2 / F-SD words and FAILS lines match L24966-L24969 | CONFIRMED | read csd_readout L704-L848. Each bar is one constant and matches the registration. The builder's mutants M05-M17 and M40 all KILLED by assertion | - |
| 5 | Dip leg is independent of SIN-3 | CONFIRMED | run_tasks / analyze: `need` = dip, plus S / G only if the identity word is PASS. selftest-io with identity FAIL (0 / 6600) wrote the dip readout and REFUSED the triad | - |
| 6 | Zero calls; TRAIN only; DB read-only | CONFIRMED | no HTTP / judge import. load_inputs refuses any site id outside IDENTITY (6,993 TRAIN root rows; KK file sha256 8e122edd). Vectors via RO.open_ro (immutable). D0 vs cache diff refused above 1e-6 | - |
| 7 | Pins: planted 14c626d5 / 2135279e, cpl_sites 359357a5, KK 8e122edd, G12 21f110af, diptest 0.11.0 | CONFIRMED | selftest-io lines 2-9 print OK for each. Pilot files: results.json 32fcf7cd8baa1367, VERIFIED_HEADLINE 98b32054b56bde7b = the registration | - |
| 8 | Selftest 34 / 34 | CONFIRMED | `--selftest` rc 0, "0 failed", 7 s | - |
| 9 | Mutants 50 / 50 killed | CONFIRMED, not vacuous | my sandboxed re-run (TMP / TEMP / TMPDIR on E:) classifies each kill: 50 / 50 are ASSERT-FAIL (>= 1 failed case), 0 are crashes | - |
| 10 | Support SD1: SE 0.0685, MDE80 0.192 at DEFF 1.5 (n_eff 40); SIZE SE 0.0126, MDE 0.035 | CONFIRMED; one digit off | my arithmetic: 0.19170 and 0.03523. At DEFF 2.0 the registration says MDE 0.217; I get 0.2214. The conclusion (DESCRIPTIVE-ONLY at DEFF 2) is unchanged. DEFF 1.5 is a declared pilot assumption with its source named | LOW |
| 11 | S is SigClust-soft, "covariance not taken from the site" (SI-NULL-TRIAD) | REFUTED in substance | on 4 planted sites (math d1 D0 / D6, economics n441 d2 D0, physics d3 D2), q = 64: lambda_min 0.00255-0.00269. sigma_b^2 estimate 0.00123 (3-anchor union); I also tried the site's own value and 2x the union. In every case tau = 0 and the null covariance changed by 0.00e+00 relative to the site's own. So S = a Gaussian moment-matched to the site in the projection, and G_S's matrix is the same object | HIGH (B1) |
| 12 | Runtime: dip about 5 min; joint run about 6-7 h single, about 1 h at --workers 8 | PLAUSIBLE (not re-timed) | numba njit is not parallel (no prange) and BLAS is set to 1 thread, so W workers use about W threads. 8 is under the 22-thread cap | - |

## Defects and conditions

- **B1 (HIGH, SI-NULL-TRIAD only, SUBSTITUTED).** The proxy-space reading (SIN-2 / SIN-4) makes the soft threshold inert: tau = 0 on 4 / 4 sites tested. S and G_S therefore test against the site's own projected covariance. TN1's THIRD-NULL-WORKS sentence would be false in substance. Only G_I uses a background covariance. The builder showed only that the alternative "simulate in 512, project on the held-fixed observed basis" is anti-conservative. The faithful SigClust reading was not built: simulate in 512 from the soft-thresholded 512-d eigenvalues (where tau > 0, since n 486 < 512 leaves zero eigenvalues), then run the WHOLE proxy, including its PCA, on each simulation. Fix: the registrar rules between (a) build that reading (an eigh / SVD per simulation; roughly +30 s per site) or (b) bracket S and G_S as site-covariance nulls and re-word TN1 / F-SN. A delta review follows either way.
- **C1 (condition for the joint launch).** SI_NULL_TRIAD_OUTCOME.txt and si_null_triad_sites.csv from this run are NOT of record until B1 is ruled. The operator moves them to `<out>/HELD_not_of_record/` before the E: backup, and the registrar records SI-NULL-TRIAD as NOT READY (B1). The alternative is a `--dip-only` switch: build_sites(triad=False) with no identity_fn, then a delta review. That run takes about 5 min instead of about 1 h.
- **C2 (MEDIUM, test gaps; the code is correct as read).** My own mutants that SURVIVED: R2 (E2 elongation removed; F-SD's elongation clause becomes vacuous), R3 (analyze treats the triad as complete without its S / G tasks), R4 (SIZE drawn at n 486 for both sizes), R5 (SD2 POS-FAIL bar <= 2), R7 (E1 matched to the EDGE population). Each was verified correct by reading build_sites L384-L431 and sd2_word L676. Fix: add selftest cases for these at the next delta. They do not block this launch, because the dry-run on the real pool prints the class counts and the run is deterministic.
- **C3 (LOW).** Seed overlap: E1 / E2 seeds 20261208-20261277 fall inside SIZE's 20261004-20261303 (SIZE idx 204-273). The draws reuse the same normal streams in different shapes. This is a registration-level artefact and mildly correlates F-SD with SD0. Disclose it in the post-run review.
- **C4 (LOW).** CSD-6's realised ICC clusters on the 30 subsamples only. Economics draws share 468-470 / 486 items (Support (a)), so the post-run review also prints the dependence at the category level.
- Rulings on the builder's readings: CSD-1..CSD-8 ACCEPTED. SIN-1 (one generator per anchor; anchor sizes 504 / 809 / 778) ACCEPTED. SIN-3 / SIN-8 ACCEPTED. SIN-2's 64-d at n < 500 (the registration says "128-d") is a deviation for the registrar together with B1. Note also that the 0.15 CP clause of SD0 / SA1 can never bind at n 300 (CP upper at 30 / 300 = 0.1397). It is registration-level, so nothing changes.

## Run command (operator; rule 7: no construction or site null in the window; main must contain 397ebd77 first)

```
git merge-base --is-ancestor 397ebd77 HEAD                     # else merge the branch first
python tools/analysis/v2_union_pool.py --dry-run                 # the operator's B0-2 check named by the tool (WAL/journal empty)
python tools/analysis/cert_split_dip.py --dry-run --pylib E:/TaxoArena_tmp/cert_split/pylib   # counts, set hash, identity word
powershell -File E:/TaxoArena_tmp/busy.ps1                       # must exit 1 (free) immediately before --run
python tools/analysis/cert_split_dip.py --run --workers 8 --pylib E:/TaxoArena_tmp/cert_split/pylib
python tools/analysis/cert_split_dip.py --analyze --pylib E:/TaxoArena_tmp/cert_split/pylib
# then C1 (quarantine SI_NULL_TRIAD_*), back up experiment_results/cert_split_dip to E:/TaxoArena_backup_2026-10-08_cert_split_dip + SHA256SUMS.txt
```

## Commands (all read-only; sandbox E:/TaxoArena_tmp/rv_csd)

```
git hash-object tools/analysis/{cert_split_dip,si_null_triad,cert_planted}.py     # 1d46cd73 / 7928e99b / 028f05a2
grep -c $'\r' tools/analysis/cert_split_dip.py tools/analysis/si_null_triad.py   # 0 / 0
python tools/analysis/cert_split_dip.py --selftest --pylib E:/TaxoArena_tmp/cert_split/pylib            # rc 0, 0 failed
python E:/TaxoArena_tmp/rv_csd/mut.py E:/TaxoArena_tmp/rv_csd/own.txt   # builder 50/50 ASSERT-FAIL; own R1 R6 R8 killed, R2 R3 R4 R5 R7 survived
python tools/analysis/cert_split_dip.py --selftest-io --g12-sites <main>/experiment_results/archv2/rp12_r2/g12/G12_sites.csv --pylib ...  # PASS; site line; tasks 5195
python - (SN.Site / site_eig / soft_threshold on 4 planted sites from E:/TaxoArena_backup_2026-10-05_cert_planted)       # tau 0, rel. change 0
python -c "SN.cp_upper(30,300); sqrt(.1875/40)*2.8; sqrt(.1875/30)*2.8; sqrt(.0475/300)*2.8"   # 0.1397 0.1917 0.2214 0.0352
sha256sum E:/TaxoArena_tmp/cert_split/{results.json,VERIFIED_HEADLINE.txt}                       # 32fcf7cd8baa1367 / 98b32054b56bde7b
```
