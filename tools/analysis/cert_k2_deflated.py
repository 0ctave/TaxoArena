"""cert_k2_deflated.py: CERT-K2-DEFLATED, the 96-site file (CERT-PC-K2-KNOWN's 33 KK sites, CERT-PC-K2's source split at full size
and its 30 subsamples, 20 random-relabelling negative controls, 10 elongation-cut controls (amended 26605924)), the dry-run, the launch command, the READOUT of the deflated-only
arm (SeparationNullBySizeTest `certK2Deflated - ...`, gradle task certK2Deflated) and the post-outcome replication. ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-04 (before any code or call) — CERT-K2-DEFLATED: under the existing DEFLATED site null (the declared groups'
between-centroid axis projected out of the centred rows; SNBST cpcDeflate), do two distinct declared MMLU-Pro categories merged into
one site certify at G12's depth-1 sizes, where the plain null gave NO-CONTROL (CERT-PC-K2-KNOWN), and how does the weak CERT-PC-K2
source split behave? (zero calls; site nulls, CPU)" (span L24123-L24141, commit fac3d50b); record docs/agents/results/CERT-K2-DEFLATED.json.
  SITES (i) CERT-PC-K2-KNOWN's site file (sha256 8e122edd...): STRONG chemistry + law, MID engineering + law, EDGE economics + physics,
  full size and 5 subsamples at n 486 and n 441 (33). (ii) CERT-PC-K2's source-family split inside math, physics, economics: full size
  (805 / 778 / 504) and its 5 subsamples at n 486 and n 441 (33). (iii) NEGATIVE CONTROL: 10 random size-matched 2-group relabellings
  of STRONG's n-486 subsample d1 and 10 of math's n-486 subsample d1 (seeds 1-10), each with its own deflated null (20).
  INSTRUMENT: cpcDeclaredSite's deflation (k - 1 = 1 dim), a FRESH seed base 20261004 per site name, plain null NOT re-drawn. Each
  site: k_defl = #{deflated replicates >= the declared statistic} of 300; DEFL-CERT iff k_defl <= 14.
  DF0 (gate, first): VALID-NULL iff <= 2 of the 20 negative-control sites DEFL-CERT; otherwise ANTI-CONSERVATIVE and DF1 / DF2 read
  NOT EVALUABLE.
  DF1 (DECIDING, n 486; STRONG and MID only): per pair DEFL-CERTIFIED-AT-SIZE iff >= 4 of 5 subsamples DEFL-CERT, DEFL-NOT iff <= 1,
  MIXED otherwise; DF1 = DEFL-SENSITIVE iff both pairs DEFL-CERTIFIED-AT-SIZE, DEFL-INSENSITIVE iff both DEFL-NOT, MIXED otherwise.
  FAILS (rule 8): DEFL-SENSITIVE is refuted by either pair at <= 1 of 5. DF1b (deciding): the same at n 441.
  DF2 (deciding): the source split at n 486, per anchor as above; LIBERAL iff >= 2 of 3 anchors DEFL-CERTIFIED-AT-SIZE; DISCRIMINATING
  iff 0 of 3; MIXED otherwise.
  P1 deflated p95 at STRONG's n-486 subsamples, median 0.105 [0.085, 0.118]. P2 DF1: DEFL-SENSITIVE 0.40, MIXED 0.30,
  DEFL-INSENSITIVE 0.30. P3 DF2: LIBERAL 0.25, MIXED 0.25, DISCRIMINATING 0.50. P4 DF0 VALID-NULL 0.95. Bands HELD iff in the closed
  interval; outcome probabilities by Brier.
  F-DF fires iff DF1 reads DEFL-INSENSITIVE. A deflated-null certification is ALWAYS written 'deflated-null certified' / DEFL-CERT,
  never 'certified' (the registrar's record L24118-L24121); the selftest scans every printed line for it.
  AMENDED PRE-DATA 26605924 (READY_cert_k2_deflated a45b4c10 B-1 option (b), the orchestrator's choice, flagged for the author at
  checkpoint H; C-1, C-2; registrar's record L24208-L24212; brackets L24127 / L24129 / L24132-L24134 / L24136-L24139 / L24141):
  (iv) ELONGATION-CUT CONTROL: for each deciding site (STRONG and MID, n 486, d1-d5) the same population cut at the median of its first
  principal axis (TRAIN rows of that site only; ties to the lower half), same deflated null, fresh seeds (control site names).
  C-1: a DEGENERATE site (reached < 20 of 300) is NOT EVALUABLE for every site class; the Q-K1 withholding rule applies to the counts.
  C-2: DF0 rests on the negative-control sites able to pass (declared >= 0); detects collapse, not calibration.
  DF1 (one exhaustive rule): per deciding pair DEFL-NOT iff <= 1 of 5, MIXED iff 2-3; at >= 4 of 5 SENSITIVE-PAIR iff (a) its control
  is NOT DEFL-CERTIFIED-AT-SIZE (<= 3 of 5) AND (b) mean over d1-d5 of (declared - control-cut statistic) > the sample SD (ddof 1) of
  the declared over d1-d5; otherwise ELONGATION-CONFOUNDED. DF1 = DEFL-SENSITIVE iff both SENSITIVE-PAIR; DEFL-INSENSITIVE iff both
  DEFL-NOT; ELONGATION-CONFOUNDED iff at least one ELONGATION-CONFOUNDED and neither DEFL-NOT; MIXED otherwise. DF1b (n 441, no
  control): its SENSITIVE word is WITHHELD ('DEFL-CERTIFIED, ELONGATION-UNCONTROLLED', descriptive); DEFL-INSENSITIVE stands.
  DF2 read as written, with the axis-cut caveat (licenses nothing about source-family structure). F-DF unchanged; the SUPPORTED
  sentence applies only to the amended DEFL-SENSITIVE. P2 re-stated: DEFL-SENSITIVE 0.15, ELONGATION-CONFOUNDED 0.25, MIXED 0.30,
  DEFL-INSENSITIVE 0.30 (the registered 0.40 printed beside, not scored). P5: the control DEFL-CERTIFIED-AT-SIZE, STRONG 0.70, MID 0.70.

INSTRUMENT (builder). A NEW Kotlin method certK2Deflated (additions only): dflEcError (amended: dflSiteError on the first 87 sites,
then the 10 EC sites: names, ids = their KK site's, labels pc_hi / pc_lo, pc_lo >= half, not the declared partition), dflSiteError
(the KK and K2 blocks through the reviewed kkpSiteError / pk2SiteError unchanged, plus the K2 block's order / anchor / subset and the
NC block), dflDeflatedSite (declared
statistic; cpcMoments -> cpcDeflate -> cpcSiteArm with tag SNDF and seed base dflSeedBase() = 20261004; no plain null, no C0).
cert_pc_k2_known.py blob 15717e13 is IMPORTED unchanged (and through it cert_pc_k2.py 38fb0dfc, cert_pc_size.py de39c648), never
copied: the KK and K2 sites are rebuilt by THEIR build_site_bytes and must equal their pinned site files byte for byte.
Labels: CERT-POSITIVE-CONTROL's label file of record (sha256 c0a20662...); snapshot 20261001_094311_Headless_Run_Auto_ge; config
experiment_configs/rp12_r2/B0/g12_site_null.sitenull (slice 512, sepBar 0.0145, dropTop 0, whiten false, 300 reps, 12 threads).

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction, another
site null or a pool reader; the pool check in the B0-2 form first; run from the data root's checkout, the rp12-r2-run worktree,
with a PATH CHECKOUT of the four files (READY_cert_k2_deflated C-3: a merge conflicts there, and `git diff 8419d4ce fac3d50b` over
every other input is empty): `git checkout <reviewed tip> -- build.gradle.kts src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt
src/test/kotlin/taxonomy/CertK2DeflatedArmTest.kt tools/analysis/cert_k2_deflated.py`, then `git hash-object` of the script = the
reviewed blob; TAXOARENA_DATA_ROOT unset; temp and scratch on E:/TaxoArena_tmp; nothing from the run is committed):
  python tools/analysis/cert_k2_deflated.py --selftest                 (never with python -O: refused)
  python tools/analysis/cert_k2_deflated.py --mutants
  TAXOARENA_DATA_ROOT=<main checkout> python tools/analysis/v2_union_pool.py --dry-run   (rc 0; pool file sha256-lf16 79d48f4b36434a55)
  python tools/analysis/cert_k2_deflated.py --dry-run [--data-root DIR] [--cpc-labels FILE]   the KK / K2 sites rebuilt = the two
        pinned site files; the Python declared statistic of every site (IDENTITY within 1e-9 of the arms'; the 63 KK / K2-subsample
        sites within the 6 printed digits of the two outcomes of record); the plain p95 of record beside (no deflated value is read);
        the 10 elongation cuts with their agreement with the declared partition; the DF1 (b) MARGIN per pair (DF-J); site file
        sha256 (= SITES_SHA256), heap, wall, COMMAND; writes nothing
  python tools/analysis/cert_k2_deflated.py --prepare [--cpc-labels FILE]   writes experiment_results/cert_k2_deflated/site_labels.tsv
        (mode x); refuses unless its sha256 is SITES_SHA256
  python tools/analysis/cert_k2_deflated.py --hashes before
  <the printed COMMAND: .\\gradlew.bat certK2Deflated ...>   then  .\\gradlew.bat --stop
  python tools/analysis/cert_k2_deflated.py --hashes after
  python tools/analysis/cert_k2_deflated.py --analyze [--cpc-labels FILE]   outcome (write-once, mode x):
        experiment_results/cert_k2_deflated/outcome.txt and df_sites.csv; runs the selftest first; refuses a REFUSED / partial arm, an
        arm other than SNDF in replicates.csv, a hash change, an IDENTITY failure, a site file that the labels do not rebuild byte for
        byte or whose KK / K2 rows are not the pinned site files of record, an instrument / seed base / snapshot other than the
        registered, a missing / extra / wrong-size site, a deflation of other than 1 dim, a recount (k, p50, p95, reached) that
        differs from the arm's, a KK / K2-subsample declared statistic that differs from its outcome of record; the elongation cuts are
        REBUILT from the cache (embeddings_cache.db of the data root, mode=ro) and must equal the site file's EC rows byte for byte.
  python tools/analysis/cert_k2_deflated.py --replication   ONLY AFTER the outcome exists (refused otherwise): the deflated columns
        already on disk (CERT-PC-K2 arm sites.csv defl_k_declared, seed base 88820260908) beside the fresh counts, descriptive;
        writes replication.txt (mode x).
Outputs are NEVER committed: pin them by sha256 and back them up to E:/TaxoArena_backup_<date>_cert_k2_deflated with SHA256SUMS.txt.

BUILDER'S READINGS (each flagged to the registrar; printed in the outcome header):
  DF-A seeds: cpcSeed(20261004, <site name>, rep) (the registration's "seed base 20261004, per site name"); tag SNDF. CERT-PC-K2's
       K2 subsample names are reused, so siteNull's base 88820260908 would REPRODUCE its on-disk deflated replicates: the fresh base
       is pinned in the arm (dflSeedBase), checked in status.txt (deflSeedBase=20261004) and by CertK2DeflatedArmTest.
  DF-B IDENTITY: the declared statistic only (0.107803, the instrument check of CERT-PC-SIZE / K2 / K2-KNOWN); its plain null is not
       re-drawn (the registration re-draws no plain null). The KK / K2-subsample declared statistics are checked against the two
       outcomes of record instead (63 sites, 6 printed digits).
  DF-C BLINDNESS: the deflated columns already on disk are never read before the outcome. The two outcome CSVs of record are read
       through read_record(), which keeps only site / declared / k_d / null_p95 (it refuses a requested column named defl*); CERT-PC-K2
       arm sites.csv and replicates.csv (they carry defl_k_declared / SND rows) are opened ONLY by --replication, which refuses unless
       outcome.txt exists. DISCLOSED (registration defect R-1, to the registrar): the registration says the certKnownPair arm "already
       computed a deflated null BESIDE the plain one"; it did not (certKnownPair runs cpcDeclaredSite with deflated = false and writes
       its defl_dims / defl_k_declared columns EMPTY: SNBST source, KK-4); only CERT-PC-K2's 30 subsamples (and CERT-PC-SIZE's
       sites, which are different sites) carry on-disk deflated counts. --replication prints this.
  DF-D NC relabelling: ids = the source site's ids sorted; the source labels in that order shuffled by random.Random(seed).shuffle,
       seed 1..10; rel_a = the positions that now carry the source's first label in sorted order (so the group sizes equal the
       source's), rel_b the rest. A relabelling equal to the source partition or its complement refuses (never at n 486 in practice).
  DF-E [superseded by C-1, amended 26605924] DEGENERATE (fewer than 20 of 300 deflated replicates reaching the gate) reads
       NOT EVALUABLE (DEGENERATE) at every site class. Counts follow Q-K1: a 4-of-5 word, the control word, DF0, DF1, DF1b and DF2 are
       printed when every value of the NOT EVALUABLE sites gives the same word, else NOT EVALUABLE. A DF0 that reads NOT EVALUABLE is
       not VALID-NULL, so DF1 / DF1b / DF2 read NOT EVALUABLE (builder's reading of 'otherwise ... NOT EVALUABLE').
  DF-F K2 full sites are named K2_<anchor>_n<N>_d0 (N = 504 / 805 / 778; CERT-PC-K2's populations, the stem-key twin dropped) and
       precede each anchor's 10 subsamples; the file order is IDENTITY, the 33 KK sites (CERT-PC-K2-KNOWN's order), economics / math /
       physics x (full, n486 d1..5, n441 d1..5), NC_STRONG_n486_s1..10, NC_math_n486_s1..10.
  DF-G DF1 / DF1b / DF2 when DF0 is ANTI-CONSERVATIVE read NOT EVALUABLE (registered); F-DF is then NOT FIRED (not evaluable), P2 / P3
       NOT SCORED; the pair / anchor words are still printed (descriptive).
  DF-H Observation for the registrar (not resolved in code): a random relabelling has declared statistic about 0 while a reached
       replicate scores > 0, so DF0 detects a COLLAPSED deflated null (most replicates unreached) more readily than a mildly
       anti-conservative one; the per-site reached counts are printed beside DF0. [C-2, amended: the outcome prints how many of the
       20 have declared < 0 and cannot pass; the dry-run of record: 11, so DF0 rests on 9.]
  DF-I the elongation cut (ec_cut): the site's unit rows (the routine's Embedding.projectTo(512)), centred; PC1 = the first right
       singular vector (numpy SVD, float64) with its largest-|loading| entry made positive; scores = centred rows . PC1; the lower
       median m = the score at 0-based rank (n - 1) // 2 when sorted by (score, id); pc_lo = score <= m (ties to the lower half), pc_hi
       the rest (243 / 243 at n 486). A cut equal to the declared partition or its complement refuses. Site names EC_<role>_n486_d<d>,
       after the NC block; seeds cpcSeed(20261004, EC name, rep). The scores are memoised per row matrix (a pure function; CPU only).
  DF-J DISCLOSED TO THE REGISTRAR (not resolved in code): the amended DF1 clause (b) uses declared statistics only, so it is FIXED BY
       THE BUILD before any null. Dry-run of record: STRONG mean margin 0.007269 > SD 0.002022 (exceeded); MID mean margin -0.000274
       < SD 0.002416 (NOT exceeded: the PC1 cut separates MID's population slightly better than the declared categories; the cut agrees
       with the declared partition on 482-484 of 486 items). So MID can only read DEFL-NOT, MIXED or ELONGATION-CONFOUNDED, and DF1
       CANNOT read DEFL-SENSITIVE; P2's DEFL-SENSITIVE 0.15 is decided before the run. The dry-run prints both margins.
  DF-K the margin uses the arm's declared statistics of the 5 KK and 5 EC sites (the same values the routine gives in Python).

DRY-RUN AT BUILD (2026-10-04, amended build, data root .claude/worktrees/rp12-r2-run, zero calls, no null, no deflated value read):
KK / K2 rows = the two site files of record byte for byte; declared check IDENTITY |diff| 3.3e-16, the 63 KK / K2-subsample sites max
|diff| 4.98e-07 (<= 5e-07: the records print 6 digits); EC cuts 243 / 243, declared STRONG 0.1126-0.1163 (agreement with the
declared partition 467 of 486), MID 0.1028-0.1095 (482-484 of 486); MARGINS STRONG exceeded, MID NOT exceeded (DF-J); site file 97
sites, 55,164 rows, sha256 00c00239... (= SITES_SHA256); the 20 NC declared statistics -0.001283 .. 0.000949 (DF-H); heap peak
0.45 GB (6g default); wall about 50 min at 12 threads. (The first build's 87-site pin 251b4f20 is superseded.)

SELFTEST (python tools/analysis/cert_k2_deflated.py --selftest): every registered branch through the real entry points (analyze(),
main(["--analyze"]), main(["--replication"]), build_site_bytes(), check_declared(), read_record()) on fixtures whose answer is known
by hand, asserting the printed VALUE; temp dirs only under E:/TaxoArena_tmp, removed after each case. MUTANTS: --mutants runs the
table MUTANTS below against --selftest (temporary copies under E:/TaxoArena_tmp, removed); the result table is in the commit message.
"""
import argparse
import contextlib
import csv
import hashlib
import io
import itertools
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

import numpy as np

HERE = os.environ.get("CKD_TOOLS_DIR") or os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro as RO  # noqa: E402

TAG = "[DFL]"
_IN_SELFTEST = False
PKK_BLOB = "15717e137066413866ea5cbd6edbe3b1a34ad885"
TMP_BASE = os.environ.get("CKD_TMP", "E:/TaxoArena_tmp")


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    got = RO.git_blob_lf(os.path.join(HERE, name + ".py"))
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


PKK = _import_pinned("cert_pc_k2_known", PKK_BLOB)
PK2, PCS, CPC, G = PKK.PK2, PKK.PCS, PKK.CPC, PKK.G

OUT_REL = "experiment_results/cert_k2_deflated"
CPC_LABELS_REL = PKK.CPC_LABELS_REL
LABELS_SHA = PKK.LABELS_SHA
SITES_NAME, ARM_NAME, OUTCOME_NAME, CSV_NAME, REPL_NAME = "site_labels.tsv", "arm", "outcome.txt", "df_sites.csv", "replication.txt"
SITE_HEADER = PCS.SITE_HEADER
SNAPSHOT, ROOT_ID, N_ROOT = PKK.SNAPSHOT, PKK.ROOT_ID, PKK.N_ROOT
TWINS = PKK.TWINS
ROLES, DECIDING_ROLES, ANCHORS = PKK.ROLES, ("STRONG", "MID"), PK2.ANCHORS
SIZES, DRAWS, NC_SEEDS = (486, 441), (1, 2, 3, 4, 5), tuple(range(1, 11))
NC_SOURCES = (("STRONG", "KK_STRONG_n486_d1"), ("math", "K2_math_n486_d1"))
NC_LABELS = ("rel_a", "rel_b")
EC_LABELS = ("pc_hi", "pc_lo")          # amended 26605924: the elongation-cut control
REPS, K_BAR, DF0_MAX, DEGENERATE_MIN = 300, 14, 2, 20
SEED_BASE = "20261004"
IDENTITY_DECLARED, IDENTITY_FULL, TOL = PKK.IDENTITY_DECLARED, PKK.IDENTITY_FULL, 1e-9
REC_TOL = 5.0e-7 + 1e-12          # a 6-printed-digit record vs the float64 statistic
INSTRUMENT = {"arm": "certK2Deflated", "reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false",
              "minClusterSize": "55", "deflSeedBase": SEED_BASE}
# the two site files and the two outcome CSVs of record (E:/TaxoArena_backup_2026-10-03_cert_pc_k2{,_known}/SHA256SUMS.txt)
KK_SITES_SHA = PKK.SITES_SHA256                 # 8e122edd...
K2_SITES_SHA = PK2.SITES_SHA256                 # efcc4e99...
KK_REC_REL, KK_REC_SHA = PKK.OUT_REL + "/kk_sites.csv", "691f83bc4cab19d2fe3ff67b13a9ef2a7ed129cf73d11d384028b7242fa1d96a"
K2_REC_REL, K2_REC_SHA = PK2.OUT_REL + "/pk2_sites.csv", "88926f502843dcead606ef20f3a5b5dca6cdc6c87117bab6dc5f7cd8866fc713"
# --replication only (after the outcome): the arms' sites.csv carrying the on-disk deflated columns
K2_ARM_REL, K2_ARM_SHA = PK2.OUT_REL + "/arm/sites.csv", "5948f820a7ec92ec4995a290904f408cb76c1cf82099384888f76ce30a101d05"
KK_ARM_REL, KK_ARM_SHA = PKK.OUT_REL + "/arm/sites.csv", "0737058e5ccc74069649ca2a8e9d2b173d5b96ace74a21362d8015d3f038db0d"
# the 97-site file (amended 26605924), pinned from the dry-run of 2026-10-04 (data root .claude/worktrees/rp12-r2-run; 97 sites,
# 55,164 rows); --prepare / --analyze refuse on a difference (supersedes the 87-site pin 251b4f20)
SITES_SHA256 = "00c002394ed99431b0189e5c00c6b7c265a53f6133f6d50197fa0ca8362c0110"
P1_BAND = (Fraction("0.085"), Fraction("0.118"))
P2_PROBS = {"DEFL-SENSITIVE": 0.15, "ELONGATION-CONFOUNDED": 0.25, "MIXED": 0.30, "DEFL-INSENSITIVE": 0.30}  # re-stated 26605924
P2_REGISTERED = {"DEFL-SENSITIVE": 0.40, "MIXED": 0.30, "DEFL-INSENSITIVE": 0.30}   # printed beside, not scored
P5_P = {"STRONG": 0.70, "MID": 0.70}                  # new 26605924: the control is DEFL-CERTIFIED-AT-SIZE
P3_PROBS = {"LIBERAL": 0.25, "MIXED": 0.25, "DISCRIMINATING": 0.50}
P4_P = 0.95
PK2_WALL_S = PKK.PK2_WALL_S     # CERT-PC-K2's arm: IDENTITY + 30 sites x (plain + deflated) + C0, 1,503 s at 12 threads
REG = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CERT-K2-DEFLATED: ..." L24123-L24141 '
       '(as registered, fac3d50b; amended pre-data 26605924 per READY_cert_k2_deflated B-1 option (b), C-1, C-2: brackets at '
       'L24127 / L24129 / L24132-L24134 / L24136-L24139 / L24141; registrar\'s record L24208-L24212)')

SENT_FDF_FIRED = ("F-DF: FIRED (DF1 DEFL-INSENSITIVE): even with the declared axis's elongation removed from the null, two distinct "
                  "merged categories are not deflated-null certified at G12's sizes; the covariance-inflation hypothesis "
                  "(POSTRUN_cert_pc_k2_known W-3) is REFUTED as the explanation of NO-CONTROL at these sizes.")
SENT_SUPPORTED = ("READING (DF1 DEFL-SENSITIVE: both deciding pairs beat their elongation-cut controls; DF0 VALID-NULL): the "
                  "covariance-inflation hypothesis is SUPPORTED for declared pairs: the PLAIN site null's demand at k = 2 includes the "
                  "site's own between-group elongation; declared two-category structure is deflated-null certified once that axis is "
                  "deflated, beyond what a cut of the same population at the median of its own first principal axis achieves; G12's 0 "
                  "of 60 is then read as 'not certified under the plain null of record', with a named mechanism that is a candidate for "
                  "data-driven splits too.")
SENT_CONFOUNDED = ("READING (DF1 ELONGATION-CONFOUNDED): not informative: the elongation-cut control is deflated-null certified too, or "
                   "the declared margin over the cut does not exceed the subsample SD; this supports neither the covariance-inflation "
                   "hypothesis nor two-category structure; nothing about G12's 0 of 60 is licensed beyond 'the deflated null does not "
                   "demand more than the cut axis's own spread'.")
SENT_LIBERAL = ("READ BESIDE DF2 LIBERAL: the deflated null also deflated-null certifies the source split at n 486; that split is an "
                "axis cut with no elongation control, so this describes the deflated null's behaviour on it and licenses nothing about "
                "source-family structure.")
DF2_CAVEAT = ("DF2 CAVEAT (amended 26605924): a source-split DEFL-CERT is also an axis cut with no elongation control: LIBERAL / "
              "DISCRIMINATING describe the deflated null's behaviour on that split only and license nothing about source-family "
              "structure.")
SENT_INSENSITIVE_WOULD = "WOULD (DF1 DEFL-INSENSITIVE): G12's 0 of 60 is not explained by covariance inflation of the plain null."
WOULD_NOT = ("WOULD NOT, either way: that G12's TOP splits would be deflated-null certified (not run here; for a data-driven split the "
             "deflation axis is chosen by the splitter's optimisation, a post-selection the declared case does not have); that G12's 0 "
             "of 60 is 'uninformative', 'insensitive' or 'too demanding' (CERT-PC-K2-KNOWN W-5 stands); any change to the certificate "
             "of record (the plain J site null); F-TAX N-1 and F2 stand.")
LIKE = ["LIKE WITH LIKE: | site | k | population | partition | null |",
        "  | KNOWN pairs (deciding) | 2 | two declared categories merged | declared | deflated |",
        "  | source split | 2 | one category | declared source family | deflated |",
        "  | negative control | 2 | as STRONG d1 / math d1 | random relabelling | deflated |",
        "  | elongation-cut control (amended) | 2 | as STRONG / MID n 486 d1-d5 | median cut of the site's PC1 | deflated |",
        "  | CERT-PC-K2-KNOWN / CERT-PC-K2 (reference) | 2 | as above | declared | plain |",
        "  | G12 TOP sites | 2-3 | routed anchor | data-driven | plain (NOT run here) |"]
DOES_NOT_SHOW = ("DOES NOT SHOW: a certificate of any tree site (a deflated-null certification is never the certificate); a mode test "
                 "(MIX-LRT-SITE closed); other members, draws, slices or k; whether anchors contain 2-way structure that the certificate passes.")
SUPPORT = ["SUPPORT (a) deciding units: 5 subsamples per pair at n 486 (STRONG, MID); 300 deflated replicates per site",
           "SUPPORT (b) DEFF 1.0 BY CONSTRUCTION (exceedance counts of independently seeded replicates; no item resampling; a tree-arm "
           "DEFF does not apply), as CERT-PC-K2-KNOWN C-4",
           "SUPPORT (c) n_eff 300 per site",
           "SUPPORT (d) SE at the bar sqrt(0.05 x 0.95 / 300) = %.4f" % math.sqrt(0.05 * 0.95 / 300),
           "SUPPORT (e) MDE80 = 2.8 x %.4f = %.4f per site" % (math.sqrt(0.05 * 0.95 / 300), 2.8 * math.sqrt(0.05 * 0.95 / 300)),
           "SUPPORT (f) VERDICT LINE: SCOREABLE as a classification; DESCRIPTIVE-ONLY at the level of a single site, SCOREABLE as the "
           "4-of-5 count",
           "SUPPORT (g) STRUCTURAL: reachable: removing one axis lowers the null's texture variance along the split",
           "SUPPORT (amended 26605924): the control margin uses the same 5 subsamples (no extra power claim); the per-site SE / MDE80 "
           "are unchanged",
           "SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered bootstrap are "
           "N/A to a null exceedance count"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------------------------------------ the site file
def kk_pairs():
    return {r: tuple(PKK.SELECTION[r].split(" + ")) for r in ROLES}


def relabel(lab, seed):
    """DF-D: {id: label} with 2 labels -> {id: rel_a / rel_b}, size-matched; refuses the source partition or its complement."""
    ids = sorted(lab)
    cats = sorted(set(lab.values()))
    if len(cats) != 2:
        refuse("relabelling source holds %d labels, not 2" % len(cats))
    seq = [lab[q] for q in ids]
    random.Random(seed).shuffle(seq)
    out = {q: (NC_LABELS[0] if seq[i] == cats[0] else NC_LABELS[1]) for i, q in enumerate(ids)}
    a = {q for q in ids if out[q] == NC_LABELS[0]}
    if a == {q for q in ids if lab[q] == cats[0]} or a == {q for q in ids if lab[q] == cats[1]}:
        refuse("relabelling seed %d reproduces the source partition" % seed)
    return out


def k2_full_sizes(pops):
    return {a: len(pops[a][PK2.FAM_ADD]) + len(pops[a][PK2.FAM_ORI]) for a in ANCHORS}


def kk_full_sizes(pops):
    return {r: len(pops[kk_pairs()[r][0]]) + len(pops[kk_pairs()[r][1]]) for r in ROLES}


def site_names(kk_sizes, k2_sizes):
    kk = PKK.site_names(kk_sizes)
    k2 = []
    for a in ANCHORS:
        k2.append("K2_%s_n%d_d0" % (a, k2_sizes[a]))
        k2.extend("K2_%s_n%d_d%d" % (a, n, d) for n in SIZES for d in DRAWS)
    nc = ["NC_%s_n486_s%d" % (t, s) for t, _src in NC_SOURCES for s in NC_SEEDS]
    ec = ["EC_%s_n486_d%d" % (r, d) for r in DECIDING_ROLES for d in DRAWS]
    return kk, k2, nc, ec


_EC_MEMO = {}


def ec_cut(ids, vec, decl):
    """Amended 26605924 (the elongation-cut control, DF-I): the site's unit rows (Embedding.projectTo(512), the routine's), centred;
    PC1 = the first right singular vector (numpy SVD, float64), its sign fixed so that its largest-|loading| entry is positive;
    scores = centred rows . PC1; the lower median m = the score at 0-based rank (n - 1) // 2 of the scores sorted by (score, id);
    pc_lo = score <= m (ties to the lower half), pc_hi the rest. Refuses a cut equal to the declared partition or its complement."""
    ids = sorted(ids)
    x = np.array([vec[q] for q in ids], dtype=np.float64)
    key = hashlib.sha256(x.tobytes()).hexdigest()           # a pure function of the rows: the scores are memoised (CPU only)
    if key not in _EC_MEMO:
        xc = x - x.mean(axis=0)
        v = np.linalg.svd(xc, full_matrices=False)[2][0]
        if v[int(np.argmax(np.abs(v)))] < 0:
            v = -v
        _EC_MEMO[key] = xc @ v
    sc = _EC_MEMO[key]
    order = sorted(range(len(ids)), key=lambda i: (sc[i], ids[i]))
    m = sc[order[(len(ids) - 1) // 2]]
    out = {q: (EC_LABELS[1] if sc[i] <= m else EC_LABELS[0]) for i, q in enumerate(ids)}
    lo = {q for q in ids if out[q] == EC_LABELS[1]}
    cats = sorted(set(decl[q] for q in ids))
    if any(lo == {q for q in ids if decl[q] == c} for c in cats):
        refuse("the elongation cut reproduces the declared partition (or its complement)")
    return out


def build_site_bytes(cat, src, vec_of):
    """-> dict(data, sites {name: sorted ids}, labels {name: {id: label}}, kk_bytes, k2_bytes, names (kk, k2, nc, ec), kk_pops,
    k2_pops). vec_of(ids) -> {id: unit row} serves the 10 elongation-cut controls (ec_cut).
    The KK rows come from cert_pc_k2_known.build_site_bytes and the K2 subsample rows from cert_pc_k2.build_site_bytes (imported)."""
    kb, ks, kl, kpops = PKK.build_site_bytes(cat, src, kk_pairs())
    qb, qs, ql, qpops = PK2.build_site_bytes(cat, src)
    sites, labels = {}, {}
    for s in ks:
        sites[s], labels[s] = ks[s], kl[s]
    for a in ANCHORS:
        full = sorted(qpops[a][PK2.FAM_ADD] + qpops[a][PK2.FAM_ORI])
        s = "K2_%s_n%d_d0" % (a, len(full))
        sites[s], labels[s] = full, {q: PK2.family(src[q]) for q in full}
        for n in SIZES:
            for d in DRAWS:
                s = "K2_%s_n%d_d%d" % (a, n, d)
                sites[s], labels[s] = qs[s], ql[s]
    for t, srcname in NC_SOURCES:
        for seed in NC_SEEDS:
            s = "NC_%s_n486_s%d" % (t, seed)
            labels[s] = relabel(labels[srcname], seed)
            sites[s] = sorted(labels[s])
    vec = vec_of(sorted({q for r in DECIDING_ROLES for d in DRAWS for q in sites["KK_%s_n486_d%d" % (r, d)]}))
    for r in DECIDING_ROLES:
        for d in DRAWS:
            srcname, s = "KK_%s_n486_d%d" % (r, d), "EC_%s_n486_d%d" % (r, d)
            labels[s] = ec_cut(sites[srcname], vec, labels[srcname])
            sites[s] = sorted(labels[s])
    names = site_names(kk_full_sizes(kpops), k2_full_sizes(qpops))
    if list(sites) != ["IDENTITY"] + names[0] + names[1] + names[2] + names[3]:
        refuse("internal: the site list is not IDENTITY + 33 KK + 33 K2 + 20 NC + 10 EC")
    rows = [SITE_HEADER]
    for s, ids in sites.items():
        rows.extend("%s\t%s\t%s" % (s, q, labels[s][q]) for q in ids)
    return dict(data=("\n".join(rows) + "\n").encode("utf-8"), sites=sites, labels=labels, kk_bytes=kb, k2_bytes=qb, names=names,
                kk_pops=kpops, k2_pops=qpops)


def group_sizes(lab):
    cats = sorted(set(lab.values()))
    return "/".join(str(sum(1 for v in lab.values() if v == c)) for c in cats)


def overlap_lines(B):
    s = B["sites"]
    L = []
    for t, srcname in NC_SOURCES:
        L.append("OVERLAP: NC_%s_n486_s1..10 hold exactly the ids of %s (the deciding / DF2 site), relabelled at random: the negative "
                 "control shares its population with that site by design" % (t, srcname))
    for a in ANCHORS:
        full = [x for x in s if x.startswith("K2_%s_" % a) and x.endswith("_d0")][0]
        L.append("OVERLAP: %s n %d; each n 486 subsample uses %.0f%% of it%s" % (
            full, len(s[full]), 100.0 * 486 / len(s[full]),
            " (DISCLOSED, CERT-PC-K2: its 5 subsamples overlap almost fully)" if 486 > 0.9 * len(s[full]) else ""))
    L.append("OVERLAP: EC_<role>_n486_d<d> hold exactly the ids of KK_<role>_n486_d<d> (the control is the same population, cut "
             "at the median of its PC1)")
    L.append("OVERLAP: the 5 draws of one pair / anchor and the two sizes are NOT independent replicates (CERT-PC-SIZE D-5)")
    return L


# ------------------------------------------------------------------------------------------------ records (blind, DF-C)
def read_record(path, sha, keep):
    """An outcome CSV of record -> {site: {col: value}} for the KEEP columns only (sha256 pinned). A defl* column is never kept."""
    bad = [k for k in keep if k.lower().startswith("defl")]
    if bad:
        refuse("read_record: %s requested; the deflated columns on disk are read only by --replication, after the outcome" % bad)
    if not os.path.isfile(path):
        refuse("the outcome CSV of record %s is not present" % path)
    b = open(path, "rb").read()
    if sha256_bytes(b) != sha:
        refuse("%s is sha256 %s, not the pinned %s" % (path, sha256_bytes(b), sha))
    out = {}
    for r in csv.DictReader(io.StringIO(b.decode("utf-8"))):
        out[r["site"]] = {k: r[k] for k in keep}
    return out


def read_records(data_root):
    kk = read_record(os.path.join(data_root, KK_REC_REL), KK_REC_SHA, ("site", "declared", "k_d", "null_p95"))
    k2 = read_record(os.path.join(data_root, K2_REC_REL), K2_REC_SHA, ("site", "declared", "k_d", "null_p95"))
    return kk, k2


def check_declared(stat_of, kk_rec, k2_rec, names, out=print):
    """IDENTITY within TOL of the arms' IDENTITY_FULL; each KK site and K2 subsample within REC_TOL of its outcome of record."""
    d0 = stat_of["IDENTITY"]
    if not abs(d0 - IDENTITY_FULL) <= TOL:
        refuse("IDENTITY: the statistic %.17g is not the instrument's %.17g within %.0e" % (d0, IDENTITY_FULL, TOL))
    worst, cnt = 0.0, 0
    for s in names[0] + [x for x in names[1] if not x.endswith("_d0")]:
        rec = (kk_rec if s.startswith("KK_") else k2_rec).get(s)
        if rec is None:
            refuse("the outcome of record holds no row for %s" % s)
        diff = abs(stat_of[s] - float(rec["declared"]))
        worst, cnt = max(worst, diff), cnt + 1
        if not diff <= REC_TOL:
            refuse("%s: declared %.9f differs from its outcome of record %s by %.2e > %.1e (not the site of record)"
                   % (s, stat_of[s], rec["declared"], diff, REC_TOL))
    out("%s DECLARED CHECK: IDENTITY %.17g (|diff| %.2e vs %.17g); %d KK / K2-subsample sites = their outcomes of record (max |diff| "
        "%.2e <= %.1e)" % (TAG, d0, abs(d0 - IDENTITY_FULL), IDENTITY_FULL, cnt, worst, REC_TOL))
    if cnt != 63:
        refuse("the declared check covered %d sites, not 63" % cnt)
    return cnt, worst


# ------------------------------------------------------------------------------------------------ dry-run / prepare / hashes
def assemble(data_root, cpc_labels):
    cfg, sid, root, cat14, _d, _s = PCS.assemble(data_root, cpc_labels)
    cat, src = PK2.read_labels(cpc_labels, LABELS_SHA)
    if cat != cat14:
        refuse("the label file read twice differs")
    tw = PKK.find_twins(cat, src, PKK.cache_texts(data_root, [q for q in cat if src[q]]))
    if tuple(tw) != TWINS:
        refuse("stem-key twins among the src-carrying ids %s, not the pinned %s" % (tw, list(TWINS)))
    vec = PKK.load_vectors(os.path.join(data_root, "embeddings_cache.db"), list(cat))
    B = build_site_bytes(cat, src, lambda ids: vec)
    check_sources(B, data_root)
    return cfg, sid, root, cat, src, B, vec


def check_sources(B, data_root):
    """The KK / K2 rows rebuilt by the imported builders equal the pinned site files of record (sha) and, when present on disk,
    the files themselves byte for byte."""
    for nm, b, pin, rel in (("KK", B["kk_bytes"], KK_SITES_SHA, PKK.OUT_REL), ("K2", B["k2_bytes"], K2_SITES_SHA, PK2.OUT_REL)):
        if sha256_bytes(b) != pin:
            refuse("the %s sites rebuilt from the labels are sha256 %s, not the site file of record %s" % (nm, sha256_bytes(b), pin))
        p = os.path.join(data_root, rel, SITES_NAME)
        if os.path.isfile(p) and open(p, "rb").read() != b:
            refuse("%s differs from the %s sites rebuilt from the labels" % (p, nm))


def command(cfg, heap):
    return ('.\\gradlew.bat certK2Deflated --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DsiteLabels=%s/%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], SNAPSHOT, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, SITES_NAME, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def pin_word(got, pin):
    return "= the pin" if got == pin else ("NOT the pin %s" % pin if pin is not None else "NO PIN YET")


def dry_run(data_root, cpc_labels, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no deflated value read, no verdict" % TAG)
    CPC.heavy_check()
    cfg, sid, root, cat, src, B, vec = assemble(data_root, cpc_labels)
    out("%s member B0/mmlu_pro_lb = snapshot %s; root %s '%s' n = %d (TRAIN); CPC labels sha256 %s (= the pin); twins %s (= the pin)"
        % (TAG, sid, root["id"], root.get("label"), len(cat), LABELS_SHA[:16], list(TWINS)))
    out("%s KK sites = CERT-PC-K2-KNOWN's site file of record (sha256 %s) and K2 subsamples = CERT-PC-K2's (sha256 %s), rebuilt by "
        "their imported builders: byte-identical" % (TAG, KK_SITES_SHA[:16], K2_SITES_SHA[:16]))
    stat_of = {s: float(PKK.site_stat(vec, lab)) for s, lab in B["labels"].items()}
    kk_rec, k2_rec = read_records(data_root)
    check_declared(stat_of, kk_rec, k2_rec, B["names"], out=out)
    out("%s SITES (declared statistic by the Python routine; plain null p95 / k_d of record beside, descriptive; no deflated value):"
        % TAG)
    for s in B["names"][0] + B["names"][1] + B["names"][2] + B["names"][3]:
        rec = (kk_rec if s.startswith("KK_") else k2_rec).get(s)
        out("%s   %-20s n %4d  groups %-9s  declared %.6f  %s%s" % (
            TAG, s, len(B["sites"][s]), group_sizes(B["labels"][s]), stat_of[s],
            "plain p95 %s k_d %s (of record)" % (rec["null_p95"], rec["k_d"]) if rec else "no plain value of record",
            "; %s" % ec_agreement(B, s) if s.startswith("EC_") else ""))
    for role in DECIDING_ROLES:                     # DF-J: the amended DF1's clause (b) needs no null: it is fixed by the build
        mok, m, sd = margin_ok([stat_of["KK_%s_n486_d%d" % (role, d)] for d in DRAWS], [stat_of["EC_%s_n486_d%d" % (role, d)] for d in DRAWS])
        out("%s MARGIN %s (amended DF1 (b), declared statistics only, determined before any null): mean(declared - cut) %.6f vs the "
            "sample SD of the declared %.6f -> %s%s" % (TAG, role, m, sd, "exceeded" if mok else "NOT exceeded",
                                                      "" if mok else ": this pair can only read DEFL-NOT, MIXED or ELONGATION-CONFOUNDED, "
                                                                     "so DF1 cannot read DEFL-SENSITIVE (DF-J; disclosed to the registrar)"))
    for ln in overlap_lines(B):
        out("%s %s" % (TAG, ln))
    sha = sha256_bytes(B["data"])
    out("%s site file %s/%s: %d sites, %d rows, sha256 %s (%s)" % (
        TAG, OUT_REL, SITES_NAME, len(B["sites"]), B["data"].count(b"\n") - 1, sha, pin_word(sha, SITES_SHA256)))
    nmax = max(len(v) for k, v in B["sites"].items() if k != "IDENTITY")
    need, live, heap = G.heap_estimate(nmax, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule, the largest null site n %d; IDENTITY draws no null): live %d, peak %.2f GB -> %s" % (
        TAG, nmax, live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap))
    cost = sum(len(v) ** 2 for k, v in B["sites"].items() if k != "IDENTITY")
    k2_cost = 2 * 30 * (466 ** 2)
    out("%s wall: about %.0f min at %d threads (CERT-PC-K2's arm took %d s for IDENTITY + 30 sites x (plain + deflated) + C0; this arm "
        "runs 96 sites x deflated only, sum n^2 %d vs about %d; the registration budgets about 1-2 h)" % (
            TAG, PK2_WALL_S / 60.0 * max(1.0, cost / float(k2_cost)), cfg["jvmThreads"], PK2_WALL_S, cost, k2_cost))
    if os.path.exists(os.path.join(ROOT, OUT_REL, ARM_NAME)):
        refuse("%s/%s exists: the arm writes it once" % (OUT_REL, ARM_NAME))
    pf = os.path.join(ROOT, "experiment_configs", "engine_pool_%s.json" % cfg["poolId"])
    pf_sha = sha256_bytes(open(pf, "rb").read().replace(b"\r\n", b"\n"))
    out("%s pool file sha256-lf %s (%s)" % (TAG, pf_sha[:16], "= the stamp's" if pf_sha == cfg["enginePoolSha256Lf"] else "MISMATCH"))
    if pf_sha != cfg["enginePoolSha256Lf"]:
        refuse("the engine pool file's LF sha256 is not the stamp's")
    same = CPC.same_checkout(data_root)
    out("%s LAUNCH FROM %s%s" % (TAG, os.path.abspath(data_root), "" if same else
        " (the data root is NOT this checkout: this dry-run is a preview; path-checkout the four files there (C-3) and run from there)"))
    out("%s COMMAND: %s" % (TAG, command(cfg, heap)))
    out("%s after the arm: .\\gradlew.bat --stop" % TAG)
    return dict(sites_sha=sha, heap=heap, sites=len(B["sites"]))


def prepare(data_root, cpc_labels):
    if not CPC.same_checkout(data_root):
        refuse("--prepare writes the site file into this checkout; the arm reads it from the data root's: run from %s" % data_root)
    CPC.heavy_check()
    B = assemble(data_root, cpc_labels)[5]
    if SITES_SHA256 is None or sha256_bytes(B["data"]) != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s" % (sha256_bytes(B["data"]), SITES_SHA256))
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, SITES_NAME), "xb") as f:
        f.write(B["data"])
    print("%s wrote %s/%s (sha256 %s)" % (TAG, OUT_REL, SITES_NAME, sha256_bytes(B["data"])))


def hashes(label, data_root):
    if not CPC.same_checkout(data_root):
        refuse("--hashes records the cache the arm reads: run it from the data root's checkout %s" % data_root)
    CPC.heavy_check()
    con = RO.open_ro(os.path.join(data_root, "embeddings_cache.db"))
    try:
        h = {t: v["table_sha"] + "/%d" % v["rows"] for t, v in RO.table_shas(con).items()}
    finally:
        con.close()
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "emb_hashes_%s.json" % label), "x", encoding="utf-8") as f:
        json.dump(h, f, sort_keys=True, indent=1)
    print("%s embeddings_cache.db per-table hashes (%s): %s" % (TAG, label, json.dumps({k: v[:16] for k, v in h.items()}, sort_keys=True)))


# ------------------------------------------------------------------------------------------------ the rules
AT, DNOT, MIX, NE = "DEFL-CERTIFIED-AT-SIZE", "DEFL-NOT", "MIXED", "NOT EVALUABLE"
NE_DEG = "NOT EVALUABLE (DEGENERATE)"


def site_word(k, reached):
    """C-1 (amended 26605924; CERT-PC-SIZE Q-2): a DEGENERATE deflated null (reached < 20 of 300) is NOT EVALUABLE, for every site
    class; otherwise DEFL-CERT iff k_defl <= 14 of 300 (the registered count rule)."""
    if reached < DEGENERATE_MIN:
        return NE_DEG
    return "DEFL-CERT" if bool(k <= K_BAR) else "not DEFL-CERT"


def _size_definite(c):
    if c >= 4:
        return AT
    if c <= 1:
        return DNOT
    return MIX


def size_possible(words):
    """The definite 4-of-5 words the 5 site words admit, each NOT EVALUABLE site counted either way (the Q-K1 withholding rule)."""
    c = sum(1 for w in words if w == "DEFL-CERT")
    e = sum(1 for w in words if w.startswith(NE))
    return {_size_definite(c + j) for j in range(e + 1)}


def one(ws):
    """Q-K1: the word when every admissible value gives the same word, else NOT EVALUABLE."""
    return next(iter(ws)) if len(ws) == 1 else NE


def size_word(words):
    return one(size_possible(words))


def df0_word(n_cert, n_ne=0):
    return one({("VALID-NULL" if bool(n_cert + j <= DF0_MAX) else "ANTI-CONSERVATIVE") for j in range(n_ne + 1)})


def margin_ok(decl, ctrl):
    """Amended DF1 (b): mean over d1-d5 of (declared - control-cut statistic) > the sample SD (ddof 1) of the declared statistic
    over d1-d5 (Q-KK2's SD). -> (bool, mean margin, SD)."""
    m = sum(a - b for a, b in zip(decl, ctrl)) / len(decl)
    sd = PKK.sd_sample(decl)
    return bool(m > sd), m, sd


def pair_possible(size_ws, ctrl_ws, mok):
    """Amended DF1, one deciding pair: DEFL-NOT (<= 1 of 5) / MIXED (2-3) as before; at >= 4 of 5 SENSITIVE-PAIR iff the control is
    not DEFL-CERTIFIED-AT-SIZE (<= 3 of 5) AND the margin is exceeded, else ELONGATION-CONFOUNDED. -> the admissible pair words."""
    out = set()
    for sw in size_ws:
        if sw != AT:
            out.add(sw)
            continue
        for cw in ctrl_ws:
            out.add("SENSITIVE-PAIR" if (cw != AT and mok) else "ELONGATION-CONFOUNDED")
    return out


def df1_definite(pws):
    if all(w == "SENSITIVE-PAIR" for w in pws):
        return "DEFL-SENSITIVE"
    if all(w == DNOT for w in pws):
        return "DEFL-INSENSITIVE"
    if any(w == "ELONGATION-CONFOUNDED" for w in pws) and not any(w == DNOT for w in pws):
        return "ELONGATION-CONFOUNDED"
    return MIX


def df1b_definite(sws):
    """DF1b (n 441, no control): the SENSITIVE word is WITHHELD (printed DEFL-CERTIFIED, ELONGATION-UNCONTROLLED); INSENSITIVE stands."""
    if all(w == AT for w in sws):
        return "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED"
    if all(w == DNOT for w in sws):
        return "DEFL-INSENSITIVE"
    return MIX


def df2_definite(aws):
    c = sum(1 for w in aws if w == AT)
    if c >= 2:
        return "LIBERAL"
    if c == 0:
        return "DISCRIMINATING"
    return MIX


def over(sets, fn):
    """A criterion over admissible word sets (Q-K1): its word when every combination agrees, else NOT EVALUABLE."""
    return one({fn(list(c)) for c in itertools.product(*[sorted(x) for x in sets])})


def ec_agreement(B, s):
    lab, srcl = B["labels"][s], B["labels"]["KK_" + s[3:]]
    first = sorted(set(srcl.values()))[0]
    a = sum(1 for q in lab if (lab[q] == EC_LABELS[1]) == (srcl[q] == first))
    return "cut vs declared agreement %d of %d (descriptive)" % (max(a, len(lab) - a), len(lab))


def in_closed(x, lo, hi):
    return bool(lo <= Fraction(repr(x)) <= hi)


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def brier(probs, outcome):
    return sum((p - (1.0 if v == outcome else 0.0)) ** 2 for v, p in probs.items())


_ALLOWED_CERT = ("defl-cert", "deflated-null certif", "not certified under the plain null of record", "certificate")


def wording_violations(lines):
    """Every 'certif' must be DEFL-CERT..., 'deflated-null certif...', 'certificate' or the registered plain-null phrase."""
    bad = []
    for ln in lines:
        low = ln.lower()
        for m in re.finditer(r"certif", low):
            i = m.start()
            ok = any(low.startswith(a, j) and j <= i < j + len(a) for a in _ALLOWED_CERT
                     for j in [low.rfind(a, 0, i + len(a))] if j >= 0)
            if not ok:
                bad.append(ln)
                break
    return bad


# ------------------------------------------------------------------------------------------------ the readout
def analyze(arm_dir, out_dir, sites_path, labels_path, kk_rec_path, k2_rec_path, vec_of, out=print):
    outcome_p, csv_p = os.path.join(out_dir, OUTCOME_NAME), os.path.join(out_dir, CSV_NAME)
    for p in (outcome_p, csv_p):
        if os.path.exists(p):
            refuse("%s exists: the outcome is write-once" % p)
    L = []

    def say(s):
        L.append(s)
        out(s)

    say("pool: none (no DB opened)")
    st_p = os.path.join(arm_dir, "status.txt")
    if not os.path.isfile(st_p):
        refuse("the arm wrote no status.txt (not run or killed): no readout")
    st_lines = open(st_p, encoding="utf-8").read().splitlines()
    if not st_lines or st_lines[0] != "COMPLETE":
        refuse("the arm's status is %r: no readout (a refused or partial arm)" % (st_lines[0] if st_lines else ""))
    st = dict(ln.split("=", 1) for ln in st_lines[1:] if "=" in ln)
    for k, v in INSTRUMENT.items():
        if st.get(k) != v:
            refuse("instrument: the arm ran %s=%r, the registered value is %r" % (k, st.get(k), v))
    if st.get("snapshot") != SNAPSHOT:
        refuse("the arm read snapshot %r, not %s" % (st.get("snapshot"), SNAPSHOT))
    cat, src = PK2.read_labels(labels_path, LABELS_SHA)
    B = build_site_bytes(cat, src, vec_of)
    if sha256_bytes(B["kk_bytes"]) != KK_SITES_SHA or sha256_bytes(B["k2_bytes"]) != K2_SITES_SHA:
        refuse("the KK / K2 sites rebuilt from the labels are not the site files of record (sha256 %s / %s)"
               % (KK_SITES_SHA[:16], K2_SITES_SHA[:16]))
    sbytes = open(sites_path, "rb").read()
    s_sha = sha256_bytes(sbytes)
    if st.get("sites_sha256") != s_sha:
        refuse("the arm read site file sha256 %s; %s is %s" % (st.get("sites_sha256"), sites_path, s_sha))
    if s_sha != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s" % (s_sha, SITES_SHA256))
    if B["data"] != sbytes:
        refuse("the site file is not the one the CPC labels (sha256 %s), TWINS, the registered NC seeds and the elongation cuts of the "
               "cached vectors rebuild" % LABELS_SHA[:16])
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    kk_rec = read_record(kk_rec_path, KK_REC_SHA, ("site", "declared", "k_d", "null_p95"))
    k2_rec = read_record(k2_rec_path, K2_REC_SHA, ("site", "declared", "k_d", "null_p95"))
    kkn, k2n, ncn, ecn = B["names"]
    names = kkn + k2n + ncn + ecn
    want = ["IDENTITY"] + names

    say("%s CERT-K2-DEFLATED outcome (tools/analysis/cert_k2_deflated.py blob %s; cert_pc_k2_known.py blob %s imported). Zero calls."
        % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), PKK_BLOB))
    say("registration: " + REG)
    say("arm: %s; snapshot %s; site file sha256 %s (= SITES_SHA256; rebuilt from the CPC labels sha256 %s: byte-identical; its KK rows "
        "= CERT-PC-K2-KNOWN's site file %s, its K2 subsample rows = CERT-PC-K2's %s); reps %s; sliceDim %s; sepBar %s; dropTop %s; "
        "whiten %s; minClusterSize %s; deflated seed base %s (fresh; never siteNull's 88820260908); threads %s; embeddings_cache.db "
        "per-table hashes before == after" % (
            st["arm"], st["snapshot"], s_sha, LABELS_SHA[:16], KK_SITES_SHA[:16], K2_SITES_SHA[:16], st["reps"], st["sliceDim"],
            st["sepBar"], st["dropTop"], st["whiten"], st["minClusterSize"], st["deflSeedBase"], st.get("threads")))
    say("builder's readings DF-A..DF-H (docstring); registration defect R-1 (certKnownPair drew no deflated null) disclosed; the plain "
        "values beside come from the two outcomes of record (kk_sites.csv sha256 %s, pk2_sites.csv sha256 %s; deflated columns not "
        "read)" % (KK_REC_SHA[:16], K2_REC_SHA[:16]))

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        rows = {r["site_id"]: r for r in csv.DictReader(f)}
    if list(rows) != want:
        refuse("sites.csv holds %s, not IDENTITY + the 96 sites in order" % list(rows)[:8])
    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["arm"] != "SNDF":
                refuse("replicates.csv holds arm %r (%s): the arm draws the deflated null SNDF only" % (r["arm"], r["site_id"]))
            reps.setdefault(r["site_id"], []).append((int(r["rep"]), float(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    if sorted(reps) != sorted(names):
        refuse("replicates.csv covers %d sites, not the 96 (missing %s)" % (len(reps), sorted(set(names) - set(reps))[:3]))
    R = {k: [x for _i, x in v] for k, v in reps.items()}

    ir = rows["IDENTITY"]
    d0 = float(ir["declared_stat"])
    say("IDENTITY: full-size root n %s, declared %.6f (registered %s); no null drawn (DF-B)" % (ir["n"], d0, IDENTITY_DECLARED))
    if not ("%.6f" % d0 == IDENTITY_DECLARED and int(ir["n"]) == N_ROOT and ir["defl_k_declared"] == ""):
        refuse("IDENTITY FAILED: declared %.6f n %s (want %s, %d, no null); no readout" % (d0, ir["n"], IDENTITY_DECLARED, N_ROOT))
    say("IDENTITY: REPRODUCED (precondition held)")
    for ln in SUPPORT:
        say(ln)
    for ln in LIKE:
        say(ln)
    for ln in overlap_lines(B):
        say(ln)

    res, out_rows = {}, []
    for s in names:
        r = rows[s]
        lab = B["labels"][s]
        n, gs = len(B["sites"][s]), group_sizes(lab)
        if int(r["n"]) != n or int(r["groups"]) != 2 or r["group_sizes"] != gs:
            refuse("sites.csv: %s n %s groups %s sizes %s (the site file holds n %d, 2 groups, %s)" % (s, r["n"], r["groups"],
                                                                                                    r["group_sizes"], n, gs))
        if r["defl_dims"] != "1":
            refuse("%s: the deflation removed %s dims, not the registered k - 1 = 1" % (s, r["defl_dims"]))
        if r["defl_seed_base"] != SEED_BASE or r["null_seed_id"] != s:
            refuse("%s: seeded by base %s / id %s, not %s / the site name" % (s, r["defl_seed_base"], r["null_seed_id"], SEED_BASE))
        d = float(r["declared_stat"])
        xs = R[s]
        srt = sorted(xs)
        k = CPC.kcount(xs, d)
        if k != int(r["defl_k_declared"]):
            refuse("%s: k_defl recount %d != the arm's %s" % (s, k, r["defl_k_declared"]))
        p50, p95 = CPC.pctl(srt, 0.50), CPC.pctl(srt, 0.95)
        if p50 != float(r["defl_p50"]) or p95 != float(r["defl_p95"]):
            refuse("%s: deflated p50 / p95 recount %r / %r != the arm's %s / %s" % (s, p50, p95, r["defl_p50"], r["defl_p95"]))
        reached = sum(1 for x in xs if x > 0.0)
        if reached != int(r["defl_reached"]):
            refuse("%s: reached recount %d != the arm's %s" % (s, reached, r["defl_reached"]))
        rec = (kk_rec if s.startswith("KK_") else k2_rec).get(s) if not s.startswith(("NC_", "EC_")) else None
        if rec is not None and not abs(d - float(rec["declared"])) <= REC_TOL:
            refuse("%s: the arm's declared %.9f differs from its outcome of record %s (not the site of record)" % (s, d, rec["declared"]))
        if rec is None and (s.startswith("KK_") or (s.startswith("K2_") and not s.endswith("_d0"))):
            refuse("the outcome of record holds no row for %s" % s)
        w = site_word(k, reached)
        res[s] = dict(d=d, k=k, p50=p50, p95=p95, reached=reached, word=w, n=n)
        say("  %-20s n %4d (%s): declared %.6f; deflated p50 %.6f / p95 %.6f / max %.6f; k_defl %3d of %d -> %s (reached %d); plain of "
            "record: %s%s" % (s, n, gs, d, p50, p95, srt[-1], k, REPS, w, reached,
                              "p95 %s, k_d %s" % (rec["null_p95"], rec["k_d"]) if rec else "none",
                              "; %s" % ec_agreement(B, s) if s.startswith("EC_") else ""))
        out_rows.append([s, s.split("_")[0], n, gs, "%.6f" % d, r["defl_dims"], k, "%.6f" % p50, "%.6f" % p95, reached, w,
                         rec["k_d"] if rec else "", rec["null_p95"] if rec else ""])
    say("DECLARED CHECK: the arm's declared statistic of the 33 KK sites and the 30 K2 subsamples equals its outcome of record "
        "(within %.1e)" % REC_TOL)

    def cnt(ws, w):
        return sum(1 for x in ws if x == w)

    def nev(ws):
        return sum(1 for x in ws if x.startswith(NE))

    # DF0 (gate, first)
    ncw = [res[s]["word"] for s in ncn]
    df0 = df0_word(cnt(ncw, "DEFL-CERT"), nev(ncw))
    per_src = ", ".join("%s %d of 10" % (t, cnt([res[s]["word"] for s in ncn if s.startswith("NC_%s_" % t)], "DEFL-CERT"))
                        for t, _x in NC_SOURCES)
    say("DF0 (gate): %d of 20 negative-control sites DEFL-CERT, %d NOT EVALUABLE (%s; reached min %d / max %d): %s (VALID-NULL iff <= %d)"
        % (cnt(ncw, "DEFL-CERT"), nev(ncw), per_src, min(res[s]["reached"] for s in ncn), max(res[s]["reached"] for s in ncn), df0,
           DF0_MAX))
    able = sum(1 for s in ncn if res[s]["d"] >= 0.0)
    say("DF0 DISCLOSURE (C-2): DF0 rests on the %d of 20 negative-control sites able to pass (declared >= 0); %d have declared < 0 and "
        "cannot DEFL-CERT (a non-splitting replicate scores 0.0 >= declared); DF0 detects collapse, not calibration; P4's Brier is not "
        "a calibration score of the deflated null" % (able, 20 - able))
    valid = bool(df0 == "VALID-NULL")

    def words_at(prefix, n):
        return [res["%s_n%d_d%d" % (prefix, n, dd)]["word"] for dd in DRAWS]

    size_ps = {n: {} for n in SIZES}
    for n in SIZES:
        for role in ROLES:
            ws = words_at("KK_%s" % role, n)
            size_ps[n][role] = size_possible(ws)
            say("PAIR %s (%s) n %d: %d of 5 DEFL-CERT, %d NOT EVALUABLE -> %s%s" % (
                role, PKK.SELECTION[role], n, cnt(ws, "DEFL-CERT"), nev(ws), one(size_ps[n][role]),
                "" if role in DECIDING_ROLES else " (descriptive)"))
    pair_w = {n: {r: one(size_ps[n][r]) for r in ROLES} for n in SIZES}
    anchor_ps = {n: {} for n in SIZES}
    for n in SIZES:
        for a in ANCHORS:
            ws = words_at("K2_%s" % a, n)
            anchor_ps[n][a] = size_possible(ws)
            say("ANCHOR %s n %d: %d of 5 DEFL-CERT, %d NOT EVALUABLE -> %s%s" % (
                a, n, cnt(ws, "DEFL-CERT"), nev(ws), one(anchor_ps[n][a]), "" if n == 486 else " (descriptive)"))
    anchor_w = {n: {a: one(anchor_ps[n][a]) for a in ANCHORS} for n in SIZES}
    ctrl_ps, pair_ps = {}, {}
    for role in DECIDING_ROLES:
        cws = words_at("EC_%s" % role, 486)
        ctrl_ps[role] = size_possible(cws)
        decl = [res["KK_%s_n486_d%d" % (role, dd)]["d"] for dd in DRAWS]
        ctrl = [res["EC_%s_n486_d%d" % (role, dd)]["d"] for dd in DRAWS]
        mok, m, sd = margin_ok(decl, ctrl)
        pair_ps[role] = pair_possible(size_ps[486][role], ctrl_ps[role], mok)
        say("CONTROL %s n 486 (elongation cut at the PC1 median): %d of 5 DEFL-CERT, %d NOT EVALUABLE -> %s; margin: mean(declared - "
            "cut) %.6f vs the sample SD of the declared %.6f -> %s" % (role, cnt(cws, "DEFL-CERT"), nev(cws), one(ctrl_ps[role]), m, sd,
                                                                     "exceeded" if mok else "NOT exceeded"))
        say("PAIR-WORD %s (amended DF1): %s" % (role, one(pair_ps[role])))
    df1 = {}
    raw1 = over([pair_ps[r] for r in DECIDING_ROLES], df1_definite)
    df1[486] = raw1 if valid else NE
    say("DF1 (n 486; STRONG, MID; amended 26605924): %s%s" % (df1[486], "" if valid else " (DF0 %s; the pair words would read %s)"
                                                                                       % (df0, raw1)))
    raw1b = over([size_ps[441][r] for r in DECIDING_ROLES], df1b_definite)
    df1[441] = raw1b if valid else NE
    say("DF1b (n 441; STRONG, MID; no elongation control at n 441): %s%s%s" % (
        df1[441], "" if valid else " (DF0 %s; the pair words would read %s)" % (df0, raw1b),
        " (the DEFL-SENSITIVE word is WITHHELD at n 441: descriptive)" if df1[441] == "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED" else ""))
    for n, nm in ((486, "DF1"), (441, "DF1b")):
        refuted = [r for r in DECIDING_ROLES if pair_w[n][r] == DNOT]
        say("%s FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: %s" % (
            nm, ("yes (%s)" % ", ".join(refuted)) if refuted else "no"))
    df2_raw = over([anchor_ps[486][a] for a in ANCHORS], df2_definite)
    df2 = df2_raw if valid else NE
    say("DF2 (n 486; economics, math, physics): %d of 3 anchors DEFL-CERTIFIED-AT-SIZE -> %s%s" % (
        sum(1 for a in ANCHORS if anchor_w[486][a] == AT), df2,
        "" if valid else " (DF0 %s; the anchor words would read %s)" % (df0, df2_raw)))
    say(DF2_CAVEAT)
    d1 = df1[486]
    fired = bool(d1 == "DEFL-INSENSITIVE")
    if fired:
        say(SENT_FDF_FIRED)
        say(SENT_INSENSITIVE_WOULD)
    else:
        say("F-DF: NOT FIRED (DF1 %s)." % d1)
        if d1 == "DEFL-SENSITIVE":
            say(SENT_SUPPORTED)
            if df2 == "LIBERAL":
                say(SENT_LIBERAL)
        elif d1 == "ELONGATION-CONFOUNDED":
            say(SENT_CONFOUNDED)
        else:
            say("READING: none (DF1 %s; no sentence)" % d1)
    say(WOULD_NOT)
    # predictions
    p1v = [res["KK_STRONG_n486_d%d" % dd]["p95"] for dd in DRAWS]
    p1 = median(p1v)
    say("P1 deflated p95 at STRONG's n-486 subsamples, median of %d = %.6f in [0.085, 0.118]: %s" % (
        len(p1v), p1, "HELD" if in_closed(p1, *P1_BAND) else "FAILED"))
    if d1 in P2_PROBS:
        say("P2 DF1 (re-stated pre-data 26605924: DEFL-SENSITIVE 0.15, ELONGATION-CONFOUNDED 0.25, MIXED 0.30, DEFL-INSENSITIVE 0.30): "
            "outcome %s, Brier (4-way sum) %.4f; the registered DEFL-SENSITIVE 0.40 / MIXED 0.30 / DEFL-INSENSITIVE 0.30 printed "
            "beside, not scored" % (d1, brier(P2_PROBS, d1)))
    else:
        say("P2 DF1: NOT SCORED (DF1 %s)" % d1)
    if df2 in P3_PROBS:
        say("P3 DF2 (LIBERAL 0.25, MIXED 0.25, DISCRIMINATING 0.50): outcome %s, Brier (3-way sum) %.4f" % (df2, brier(P3_PROBS, df2)))
    else:
        say("P3 DF2: NOT SCORED (DF2 %s)" % df2)
    e4 = valid
    say("P4 DF0 VALID-NULL (p 0.95): event %s, Brier %.4f" % ("yes" if e4 else "no", (P4_P - (1.0 if e4 else 0.0)) ** 2))
    for role in DECIDING_ROLES:
        cw = one(ctrl_ps[role])
        if cw == NE:
            say("P5 %s elongation-cut control DEFL-CERTIFIED-AT-SIZE (p %.2f): NOT SCORED (control NOT EVALUABLE)" % (role, P5_P[role]))
        else:
            e5 = bool(cw == AT)
            say("P5 %s elongation-cut control DEFL-CERTIFIED-AT-SIZE (p %.2f): event %s, Brier %.4f" % (
                role, P5_P[role], "yes" if e5 else "no", (P5_P[role] - (1.0 if e5 else 0.0)) ** 2))
    say("DESCRIPTIVE: EDGE (%s) n 486 %s, n 441 %s; full-size sites: %s" % (
        PKK.SELECTION["EDGE"], pair_w[486]["EDGE"], pair_w[441]["EDGE"],
        ", ".join("%s k_defl %d %s" % (s, res[s]["k"], res[s]["word"]) for s in names if s.endswith("_d0"))))
    say("DESCRIPTIVE: the on-disk deflated columns (CERT-PC-K2's 30 subsamples, old seed base) are read by --replication, after this "
        "outcome")
    say(DOES_NOT_SHOW)
    bad = wording_violations(L)
    if bad:
        refuse("internal: a deflated-null certification worded as 'certified': %r" % bad[0])

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "block", "n", "group_sizes", "declared", "defl_dims", "k_defl", "defl_p50", "defl_p95", "reached", "word",
                    "plain_k_d_record", "plain_p95_record"])
        w.writerows(out_rows)
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, csv_p))
    return dict(df0=df0, df1=df1, df2=df2, fired=fired, pair_w=pair_w, anchor_w=anchor_w, pair_ps=pair_ps, ctrl_ps=ctrl_ps, res=res,
                lines=L)


def replication(out_dir, k2_arm_path, kk_arm_path, out=print):
    """After the outcome only: CERT-PC-K2's on-disk deflated counts (seed base 88820260908) beside the fresh ones (descriptive)."""
    if not os.path.isfile(os.path.join(out_dir, OUTCOME_NAME)) or not os.path.isfile(os.path.join(out_dir, CSV_NAME)):
        refuse("--replication reads the on-disk deflated columns only AFTER the outcome (outcome.txt and df_sites.csv) exists")
    rp = os.path.join(out_dir, REPL_NAME)
    if os.path.exists(rp):
        refuse("%s exists: write-once" % rp)
    with open(os.path.join(out_dir, CSV_NAME), newline="", encoding="utf-8") as f:
        fresh = {r["site"]: r for r in csv.DictReader(f)}
    L = []

    def say(s):
        L.append(s)
        out(s)
    for p, pin in ((k2_arm_path, K2_ARM_SHA), (kk_arm_path, KK_ARM_SHA)):
        if sha256_bytes(open(p, "rb").read()) != pin:
            refuse("%s is not the pinned arm file %s" % (p, pin[:16]))
    with open(k2_arm_path, newline="", encoding="utf-8") as f:
        old = {r["site_id"]: r for r in csv.DictReader(f)}
    with open(kk_arm_path, newline="", encoding="utf-8") as f:
        kk_old = {r["site_id"]: r for r in csv.DictReader(f)}
    say("%s REPLICATION (descriptive; read after the outcome): CERT-PC-K2 arm sites.csv defl_k_declared (siteNull's seed base "
        "88820260908) beside this run's fresh k_defl (seed base %s)" % (TAG, SEED_BASE))
    kk_filled = [s for s, r in kk_old.items() if s != "IDENTITY" and (r["defl_dims"] or r["defl_k_declared"])]
    say("CERT-PC-K2-KNOWN arm: %d of %d KK sites carry a deflated value (%s)" % (
        len(kk_filled), len([s for s in kk_old if s != "IDENTITY"]),
        "certKnownPair drew no deflated null: registration defect R-1" if not kk_filled else "UNEXPECTED: see the rows"))
    agree, n = 0, 0
    for s in sorted(x for x in fresh if x.startswith("K2_") and not x.endswith("_d0")):
        if s not in old:
            refuse("CERT-PC-K2 arm sites.csv has no row for %s" % s)
        ko, kf = int(old[s]["defl_k_declared"]), int(fresh[s]["k_defl"])
        wo, wf = site_word(ko, REPS), fresh[s]["word"]          # the on-disk arm stored no reached count: the k rule only
        agree, n = agree + (1 if wo == wf else 0), n + 1
        say("  %-20s old k %3d -> %s; fresh k %3d -> %s" % (s, ko, wo, kf, wf))
    say("REPLICATION: the per-site word agrees on %d of %d K2 subsamples (two independently seeded deflated nulls)" % (agree, n))
    with open(rp, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    return agree, n


# ------------------------------------------------------------------------------------------------ selftest
def _labels_fixture():
    """6,993 ids: the 14 categories at CERT-PC-K2-KNOWN's registered counts; economics / math / physics split into CERT-PC-K2's
    registered families; the pinned twin (math, scibench) and 3 math + 1 computer science ids without src."""
    cat, src, i = {}, {}, 0

    def add(c, s, qid=None):
        nonlocal i
        q = qid or "q_%05d" % i
        i += 1
        cat[q], src[q] = c, s
    for c in sorted(PKK.REG_COUNTS):
        if c in PK2.REG_COUNTS:
            o, ad = PK2.REG_COUNTS[c]
            for j in range(o):
                add(c, "ori_mmlu-%s" % c)
            for j in range(ad):
                add(c, ("stemez-X", "theoremQA-Y", "scibench-z")[j % 3])
        else:
            for j in range(PKK.REG_COUNTS[c]):
                add(c, "ori_mmlu-x")
    add("math", "scibench-stat", TWINS[0])
    for c in ("math", "math", "math", "computer science"):
        add(c, "")
    return cat, src


def _write_labels(path, cat, src):
    data = (CPC.LABEL_HEADER + "\n" + "".join("%s\t%s\t%s\n" % (q, cat[q], src[q]) for q in sorted(cat))).encode("utf-8")
    open(path, "wb").write(data)
    return sha256_bytes(data)


_FX_CACHE = {}


def _fixture_raw(q):
    """A deterministic float32 600-vector per id (seeded by the id's sha256), as the cache would hold it."""
    return np.random.RandomState(int(hashlib.sha256(q.encode()).hexdigest()[:8], 16)).standard_normal(600).astype(np.float32)


_FX_VEC = {}


def _fixture_vec(ids):
    """{id: unit row} exactly as PKK.load_vectors returns it from a cache holding _fixture_raw (first 512 floats, L2-normalised)."""
    ids = sorted(ids)
    miss = [q for q in ids if q not in _FX_VEC]
    if miss:
        u = PKK.unit_rows(np.array([_fixture_raw(q) for q in miss], dtype=np.float32))
        _FX_VEC.update({q: u[i] for i, q in enumerate(miss)})
    return {q: _FX_VEC[q] for q in ids}


def _fixture_db(path, ids):
    """A cache fixture (queries / embeddings, big-endian float32, as cpcLoadSliceFloats reads it) holding _fixture_raw for ids."""
    import sqlite3
    import struct
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE queries (id TEXT, distilled_text TEXT)")
    con.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
    for q in ids:
        con.execute("INSERT INTO queries VALUES (?, ?)", (q, "t_" + q))
        con.execute("INSERT INTO embeddings VALUES (?, ?)", ("t_" + q, struct.pack(">600f", *[float(x) for x in _fixture_raw(q)])))
    con.commit()
    con.close()


def _fixture_build():
    if "B" not in _FX_CACHE:
        cat, src = _labels_fixture()
        _FX_CACHE["B"] = (cat, src, build_site_bytes(cat, src, _fixture_vec))
    return _FX_CACHE["B"]


def _rep(k, sc, reached=None, d=None):
    """300 replicates with exactly k >= d: SN = i x sc, d = (300 - k) x sc (the same float product), p50 = 149 sc, p95 = 284 sc.
    reached: all but the first (300 - reached) set to 0, d moved to 1.0 (or the given d) so k = 0 (a DEGENERATE site); d given
    without reached: that declared statistic (e.g. < 0: k = 300)."""
    xs = [i * sc for i in range(REPS)]
    dd = (REPS - k) * sc
    if reached is not None:
        xs = [0.0] * (REPS - reached) + [(j + 1) * sc for j in range(reached)]
        dd = 1.0
    return xs, (dd if d is None else d)


def _fx(tmp, spec=None, status="COMPLETE", hashes_equal=True, partial=None, site_sha_bad=False, arm_name="certK2Deflated",
        seed_base=SEED_BASE, snapshot=SNAPSHOT, ident_d=0.10780301, ident_n=6993, drop_site=None, n_lie=None, k_lie=None,
        p95_lie=None, reached_lie=None, gs_lie=None, dims=None, seed_lie=None, rec_lie=None, extra_arm=None, tamper=False,
        rec_drop=None, ident_null=False, tamper_ec=False):
    """spec[site] = dict(k=, sc=, reached=). Defaults: KK / K2 k 300 - 286 = ... (k 100, not DEFL-CERT), NC k 200; sc 0.0004 (deflated
    p95 0.1136). Writes arm/, out/ (site file, hashes), rec/ (the two outcome CSVs of record, pk2 with a POISON defl_k 777777)."""
    spec = spec or {}
    cat, src, B = _fixture_build()
    arm_d, outd, recd = os.path.join(tmp, "arm"), os.path.join(tmp, "out"), os.path.join(tmp, "rec")
    for d in (arm_d, outd, recd):
        os.makedirs(d)
    lp = os.path.join(tmp, "declared_labels.tsv")
    lsha = _write_labels(lp, cat, src)
    data = B["data"]
    if tamper:                          # one NC row relabelled: not the registered file
        i = data.index(b"\nNC_math_n486_s3\t")
        j = data.index(b"\n", i + 1)
        row = data[i + 1:j]
        flip = row[:-5] + (b"rel_b" if row.endswith(b"rel_a") else b"rel_a")
        data = data[:i + 1] + flip + data[j:]
    if tamper_ec:                       # one elongation-cut row flipped: not the cut the cached vectors give
        i = data.index(b"\nEC_MID_n486_d4\t")
        j = data.index(b"\n", i + 1)
        row = data[i + 1:j]
        flip = row[:-5] + (b"pc_hi" if row.endswith(b"pc_lo") else b"pc_lo")
        data = data[:i + 1] + flip + data[j:]
    sp = os.path.join(outd, SITES_NAME)
    open(sp, "wb").write(data)
    sha = sha256_bytes(data if not site_sha_bad else b"x")
    with open(os.path.join(arm_d, "status.txt"), "w") as f:
        f.write("%s\narm=%s\nsnapshot=%s\nsites_sha256=%s\nreps=300\nsliceDim=512\nsepBar=0.0145\ndropTop=0\nwhiten=false\n"
                "minClusterSize=55\ndeflSeedBase=%s\nthreads=12\n" % (status, arm_name, snapshot, sha, seed_base))
    kkn, k2n, ncn, ecn = B["names"]
    names = [s for s in kkn + k2n + ncn + ecn if s != drop_site]
    srows = ['IDENTITY,"IDENTITY",%d,14,x,%r,,%s,,,,,n00000001,300' % (ident_n, ident_d, "5" if ident_null else "")]
    rep_lines, kk_rec, k2_rec = [], [], []
    for s in names:
        sp_ = dict(k=200 if s.startswith(("NC_", "EC_")) else 100, sc=0.0004, reached=None, d=None)
        sp_.update(spec.get(s, {}))
        xs, d = _rep(sp_["k"], sp_["sc"], sp_["reached"], sp_["d"])
        srt = sorted(xs)
        k = CPC.kcount(xs, d) + (1 if k_lie == s else 0)
        p95 = CPC.pctl(srt, 0.95) + (1e-6 if p95_lie == s else 0.0)
        reached = sum(1 for x in xs if x > 0.0) + (1 if reached_lie == s else 0)
        gs = group_sizes(B["labels"][s]) if gs_lie != s else "1/485"
        n = len(B["sites"][s]) + (1 if n_lie == s else 0)
        srows.append('%s,"%s",%d,2,%s,%r,%s,%d,%r,%r,%d,%s,%s,300' % (
            s.split("_")[0], s, n, gs, d, "0" if dims == s else "1", k, CPC.pctl(srt, 0.50), p95, reached, SEED_BASE,
            "OTHER" if seed_lie == s else s))
        nrep = 150 if partial == s else REPS
        rep_lines += ['"%s",%s,%d,%r' % (s, "SNDF", i, x) for i, x in enumerate(xs[:nrep])]
        if extra_arm == s:
            rep_lines += ['"%s",SN,%d,%r' % (s, i, x) for i, x in enumerate(xs)]
        decl = "%.6f" % (d + (1e-5 if rec_lie == s else 0.0))
        if s.startswith("KK_") and s != rec_drop:
            kk_rec.append([s, s.split("_")[1], "x", n, gs, decl, 3, "4/301", "0.0", "0.0815", "0.1", "0.01", "true", 300, "x"])
        if s.startswith("K2_") and not s.endswith("_d0") and s != rec_drop:
            k2_rec.append([s, s.split("_")[1], n, gs, decl, 7, "8/301", "0.0911", "0.01", "true", 300, 777777, "x"])
    with open(os.path.join(arm_d, "sites.csv"), "w") as f:
        f.write("role,site_id,n,groups,group_sizes,declared_stat,defl_dims,defl_k_declared,defl_p50,defl_p95,defl_reached,"
                "defl_seed_base,null_seed_id,reps\n" + "\n".join(srows) + "\n")
    with open(os.path.join(arm_d, "replicates.csv"), "w") as f:
        f.write("site_id,arm,rep,stat\n" + "\n".join(rep_lines) + "\n")
    for x in ("before", "after"):
        json.dump({"embeddings": "aa/1", "queries": "bb/2" if (hashes_equal or x == "before") else "cc/2"},
                  open(os.path.join(outd, "emb_hashes_%s.json" % x), "w"))
    kp, qp = os.path.join(recd, "kk_sites.csv"), os.path.join(recd, "pk2_sites.csv")
    with open(kp, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "role", "pair", "n", "group_sizes", "declared", "k_d", "p_d", "null_min", "null_p95", "null_max", "c0_p95",
                    "c0_comparable", "reached", "status"])
        w.writerows(kk_rec)
    with open(qp, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "anchor", "n", "added_ori", "declared", "k_d", "p_d", "null_p95", "c0_p95", "c0_comparable", "reached",
                    "defl_k", "status"])
        w.writerows(k2_rec)
    pins = dict(LABELS_SHA=lsha, SITES_SHA256=sha256_bytes(data), KK_SITES_SHA=sha256_bytes(B["kk_bytes"]),
                K2_SITES_SHA=sha256_bytes(B["k2_bytes"]), KK_REC_SHA=sha256_bytes(open(kp, "rb").read()),
                K2_REC_SHA=sha256_bytes(open(qp, "rb").read()))
    return dict(arm=arm_d, out=outd, sites=sp, labels=lp, kk=kp, k2=qp, pins=pins, B=B)


@contextlib.contextmanager
def _pins(**kw):
    g = globals()
    saved = {k: g[k] for k in kw}
    g.update(kw)
    try:
        yield
    finally:
        g.update(saved)


def _ks(prefix, n, ks, sc=0.0004):
    return {"%s_n%d_d%d" % (prefix, n, i + 1): dict(k=k, sc=sc) for i, k in enumerate(ks)}


def _nc(src_tag, ks):
    return {"NC_%s_n486_s%d" % (src_tag, i + 1): dict(k=k) for i, k in enumerate(ks)}


def _merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    if not __debug__:
        refuse("python -O strips the selftest's asserts: run without -O")
    if not os.path.isdir(TMP_BASE):
        refuse("the temp base %s is absent (temp and scratch live on E:)" % TMP_BASE)
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="ckdst_", dir=TMP_BASE)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def sub(tmp, i):
        p = os.path.join(tmp, "s%d" % i)
        os.makedirs(p)
        return p

    def run(tmp, **kw):
        F = _fx(tmp, **kw)
        lines = []
        with _pins(**F["pins"]):
            r = analyze(F["arm"], F["out"], F["sites"], F["labels"], F["kk"], F["k2"], _fixture_vec, out=lines.append)
        return r, lines, F

    def refused(tmp, needle, pins_override=None, **kw):
        F = _fx(tmp, **kw)
        pins = dict(F["pins"])
        if pins_override:
            pins.update(pins_override)
        try:
            with _pins(**pins):
                analyze(F["arm"], F["out"], F["sites"], F["labels"], F["kk"], F["k2"], _fixture_vec, out=lambda s: None)
        except SystemExit as e:
            assert needle in str(e), (needle, str(e))
            assert not os.path.exists(os.path.join(F["out"], OUTCOME_NAME)), "a refusal wrote an outcome"
            return
        raise AssertionError("not refused: " + needle)

    def has(lines, s):
        assert s in lines, "missing line %r; got:\n%s" % (s, "\n".join(lines))

    def starts(lines, s):
        hit = [ln for ln in lines if ln.startswith(s)]
        assert hit, "no line starts with %r; got:\n%s" % (s, "\n".join(lines))
        return hit[0]

    SENS = _merge(_ks("KK_STRONG", 486, [0, 3, 14, 2, 1]), _ks("KK_MID", 486, [5, 6, 7, 8, 9]),
                  _ks("K2_economics", 486, [0, 0, 0, 0, 0]), _ks("K2_math", 486, [14, 13, 12, 11, 15]))
    P2L = ("P2 DF1 (re-stated pre-data 26605924: DEFL-SENSITIVE 0.15, ELONGATION-CONFOUNDED 0.25, MIXED 0.30, DEFL-INSENSITIVE 0.30): "
           "outcome %s, Brier (4-way sum) %s; the registered DEFL-SENSITIVE 0.40 / MIXED 0.30 / DEFL-INSENSITIVE 0.30 printed beside, "
           "not scored")
    DF1L = "DF1 (n 486; STRONG, MID; amended 26605924): "
    DF1bL = "DF1b (n 441; STRONG, MID; no elongation control at n 441): "

    def sensitive(tmp):
        # STRONG / MID n 486 all DEFL-CERT, controls 0 of 5 and margins exceeded -> DEFL-SENSITIVE; n 441 default -> DF1b
        # INSENSITIVE; economics 5, math 4, physics 0 -> LIBERAL
        r, L, F = run(sub(tmp, 1), spec=_merge(SENS, _nc("math", [14, 14, 300, 300, 300, 300, 300, 300, 300, 300])))
        has(L, "DF0 (gate): 2 of 20 negative-control sites DEFL-CERT, 0 NOT EVALUABLE (STRONG 0 of 10, math 2 of 10; reached min 299 / "
               "max 299): VALID-NULL (VALID-NULL iff <= 2)")
        has(L, "DF0 DISCLOSURE (C-2): DF0 rests on the 20 of 20 negative-control sites able to pass (declared >= 0); 0 have declared < 0 "
               "and cannot DEFL-CERT (a non-splitting replicate scores 0.0 >= declared); DF0 detects collapse, not calibration; P4's "
               "Brier is not a calibration score of the deflated null")
        has(L, "PAIR STRONG (chemistry + law) n 486: 5 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE")
        has(L, "PAIR MID (engineering + law) n 486: 5 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE")
        has(L, "PAIR EDGE (economics + physics) n 486: 0 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-NOT (descriptive)")
        has(L, "CONTROL STRONG n 486 (elongation cut at the PC1 median): 0 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-NOT; margin: "
               "mean(declared - cut) 0.078400 vs the sample SD of the declared 0.002280 -> exceeded")
        has(L, "PAIR-WORD STRONG (amended DF1): SENSITIVE-PAIR")
        has(L, "PAIR-WORD MID (amended DF1): SENSITIVE-PAIR")
        has(L, DF1L + "DEFL-SENSITIVE")
        has(L, "DF1 FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: no")
        has(L, DF1bL + "DEFL-INSENSITIVE")
        has(L, "DF1b FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: yes (STRONG, MID)")
        has(L, "ANCHOR math n 486: 4 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE")
        has(L, "DF2 (n 486; economics, math, physics): 2 of 3 anchors DEFL-CERTIFIED-AT-SIZE -> LIBERAL")
        has(L, DF2_CAVEAT)
        has(L, "F-DF: NOT FIRED (DF1 DEFL-SENSITIVE).")
        has(L, SENT_SUPPORTED)
        has(L, SENT_LIBERAL)
        has(L, WOULD_NOT)
        assert SENT_CONFOUNDED not in L
        has(L, "P1 deflated p95 at STRONG's n-486 subsamples, median of 5 = 0.113600 in [0.085, 0.118]: HELD")
        has(L, P2L % ("DEFL-SENSITIVE", "0.9650"))
        has(L, "P3 DF2 (LIBERAL 0.25, MIXED 0.25, DISCRIMINATING 0.50): outcome LIBERAL, Brier (3-way sum) 0.8750")
        has(L, "P4 DF0 VALID-NULL (p 0.95): event yes, Brier 0.0025")
        has(L, "P5 STRONG elongation-cut control DEFL-CERTIFIED-AT-SIZE (p 0.70): event no, Brier 0.4900")
        has(L, "P5 MID elongation-cut control DEFL-CERTIFIED-AT-SIZE (p 0.70): event no, Brier 0.4900")
        for ln in SUPPORT + LIKE + [DOES_NOT_SHOW, "IDENTITY: REPRODUCED (precondition held)"]:
            has(L, ln)
        ln = starts(L, "  KK_STRONG_n486_d3 ")
        assert "k_defl  14 of 300 -> DEFL-CERT (reached 299)" in ln and "plain of record: p95 0.0815, k_d 3" in ln, ln
        ln = starts(L, "  K2_math_n486_d5 ")
        assert "k_defl  15 of 300 -> not DEFL-CERT" in ln and "plain of record: p95 0.0911, k_d 7" in ln, ln
        ln = starts(L, "  K2_math_n805_d0 ")
        assert "plain of record: none" in ln, ln
        ln = starts(L, "  EC_MID_n486_d5 ")
        assert "(243/243)" in ln and "plain of record: none; cut vs declared agreement " in ln, ln
        assert r["df0"] == "VALID-NULL" and r["df1"] == {486: "DEFL-SENSITIVE", 441: "DEFL-INSENSITIVE"} and r["df2"] == "LIBERAL"
        assert r["fired"] is False
        assert not any("777777" in x for x in L), "a deflated column of record leaked into the outcome"
        assert wording_violations(L) == [], wording_violations(L)
        txt = open(os.path.join(F["out"], OUTCOME_NAME), encoding="utf-8").read()
        assert txt == "\n".join(r["lines"]) + "\n" and L[:-1] == r["lines"] and L[-1].startswith("%s wrote " % TAG)
        rows = list(csv.DictReader(open(os.path.join(F["out"], CSV_NAME), encoding="utf-8")))
        assert len(rows) == 96 and rows[0]["site"] == "KK_STRONG_n1254_d0" and rows[-1]["site"] == "EC_MID_n486_d5", rows[0]
        assert [x["word"] for x in rows if x["site"] == "NC_math_n486_s2"] == ["DEFL-CERT"]
        try:                                            # write-once: a second readout into the same dir refuses
            with _pins(**F["pins"]):
                analyze(F["arm"], F["out"], F["sites"], F["labels"], F["kk"], F["k2"], _fixture_vec, out=lambda s: None)
            raise AssertionError("a second analyze overwrote the outcome")
        except SystemExit as e:
            assert "exists: the outcome is write-once" in str(e)

    def confounded(tmp):
        ALL0 = _merge(_ks("KK_STRONG", 486, [0] * 5), _ks("KK_MID", 486, [0] * 5))
        # (a) STRONG's control 4 of 5 DEFL-CERT -> STRONG ELONGATION-CONFOUNDED; MID SENSITIVE -> DF1 ELONGATION-CONFOUNDED
        r, L, _F = run(sub(tmp, 1), spec=_merge(ALL0, _ks("EC_STRONG", 486, [0, 0, 0, 0, 15])))
        has(L, "PAIR-WORD STRONG (amended DF1): ELONGATION-CONFOUNDED")
        has(L, "PAIR-WORD MID (amended DF1): SENSITIVE-PAIR")
        has(L, DF1L + "ELONGATION-CONFOUNDED")
        has(L, "F-DF: NOT FIRED (DF1 ELONGATION-CONFOUNDED).")
        has(L, SENT_CONFOUNDED)
        assert SENT_SUPPORTED not in L and SENT_LIBERAL not in L and r["fired"] is False
        has(L, P2L % ("ELONGATION-CONFOUNDED", "0.7650"))
        has(L, "P5 STRONG elongation-cut control DEFL-CERTIFIED-AT-SIZE (p 0.70): event yes, Brier 0.0900")
        # (b) the control's boundary: 3 of 5 is NOT at size -> SENSITIVE
        r, L, _F = run(sub(tmp, 2), spec=_merge(ALL0, _ks("EC_STRONG", 486, [0, 0, 0, 15, 15])))
        has(L, "PAIR-WORD STRONG (amended DF1): SENSITIVE-PAIR")
        has(L, DF1L + "DEFL-SENSITIVE")
        # (c) margin not exceeded (control cut statistic above the declared): MID CONFOUNDED with its control not at size;
        # the last-read pair alone confounds
        r, L, _F = run(sub(tmp, 3), spec=_merge(ALL0, _ks("EC_MID", 486, [200] * 5, sc=0.002)))
        ln = starts(L, "CONTROL MID n 486 (elongation cut at the PC1 median): 0 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-NOT; margin: ")
        assert ln.endswith("-> NOT exceeded") and "mean(declared - cut) -0.080000" in ln, ln
        has(L, "PAIR-WORD MID (amended DF1): ELONGATION-CONFOUNDED")
        has(L, "PAIR-WORD STRONG (amended DF1): SENSITIVE-PAIR")              # each pair against its OWN control
        has(L, DF1L + "ELONGATION-CONFOUNDED")
        # (d) CONFOUNDED with the other pair DEFL-NOT -> MIXED (not ELONGATION-CONFOUNDED, not INSENSITIVE)
        r, L, _F = run(sub(tmp, 4), spec=_merge(_ks("KK_STRONG", 486, [0] * 5), _ks("EC_STRONG", 486, [0] * 5)))
        has(L, "PAIR-WORD STRONG (amended DF1): ELONGATION-CONFOUNDED")
        has(L, "PAIR-WORD MID (amended DF1): DEFL-NOT")
        has(L, DF1L + "MIXED")
        has(L, "READING: none (DF1 MIXED; no sentence)")
        # (e) a MIXED pair (2-3 of 5) is not confounded whatever its control
        r, L, _F = run(sub(tmp, 5), spec=_merge(_ks("KK_STRONG", 486, [0, 0, 0, 15, 15]), _ks("KK_MID", 486, [0] * 5),
                                                 _ks("EC_STRONG", 486, [0] * 5)))
        has(L, "PAIR-WORD STRONG (amended DF1): MIXED")
        has(L, DF1L + "MIXED")

    def insensitive(tmp):
        # STRONG 1 of 5 (boundary), MID 0 of 5 -> INSENSITIVE, F-DF fires; anchors 0 -> DISCRIMINATING
        r, L, _F = run(sub(tmp, 1), spec=_merge(_ks("KK_STRONG", 486, [15, 15, 14, 15, 15]), _ks("K2_physics", 486, [0, 0, 0, 15, 15])))
        has(L, "PAIR STRONG (chemistry + law) n 486: 1 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-NOT")
        has(L, DF1L + "DEFL-INSENSITIVE")
        has(L, "DF1 FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: yes (STRONG, MID)")
        has(L, "ANCHOR physics n 486: 3 of 5 DEFL-CERT, 0 NOT EVALUABLE -> MIXED")
        has(L, "DF2 (n 486; economics, math, physics): 0 of 3 anchors DEFL-CERTIFIED-AT-SIZE -> DISCRIMINATING")
        has(L, SENT_FDF_FIRED)
        has(L, SENT_INSENSITIVE_WOULD)
        assert SENT_SUPPORTED not in L and not any(x.startswith("F-DF: NOT FIRED") for x in L)
        has(L, P2L % ("DEFL-INSENSITIVE", "0.6650"))
        has(L, "P3 DF2 (LIBERAL 0.25, MIXED 0.25, DISCRIMINATING 0.50): outcome DISCRIMINATING, Brier (3-way sum) 0.3750")
        assert r["fired"] is True
        # MIXED: STRONG 4 of 5 (boundary), MID 2 of 5 -> MIXED, refuted no; one anchor -> DF2 MIXED
        r, L, _F = run(sub(tmp, 2), spec=_merge(_ks("KK_STRONG", 486, [14, 14, 14, 14, 15]), _ks("KK_MID", 486, [0, 0, 15, 15, 15]),
                                                 _ks("K2_economics", 486, [0, 0, 0, 0, 100])))
        has(L, "PAIR STRONG (chemistry + law) n 486: 4 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE")
        has(L, "PAIR MID (engineering + law) n 486: 2 of 5 DEFL-CERT, 0 NOT EVALUABLE -> MIXED")
        has(L, DF1L + "MIXED")
        has(L, "DF1 FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: no")
        has(L, "DF2 (n 486; economics, math, physics): 1 of 3 anchors DEFL-CERTIFIED-AT-SIZE -> MIXED")
        has(L, "F-DF: NOT FIRED (DF1 MIXED).")
        has(L, "READING: none (DF1 MIXED; no sentence)")
        has(L, P2L % ("MIXED", "0.6650"))
        has(L, "P3 DF2 (LIBERAL 0.25, MIXED 0.25, DISCRIMINATING 0.50): outcome MIXED, Brier (3-way sum) 0.8750")
        # MIXED with a refutation: STRONG 5 of 5, MID 1 of 5 (the second, last-read pair decides the refutation)
        r, L, _F = run(sub(tmp, 3), spec=_merge(_ks("KK_STRONG", 486, [0, 0, 0, 0, 0]), _ks("KK_MID", 486, [100, 100, 100, 100, 0])))
        has(L, DF1L + "MIXED")
        has(L, "DF1 FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: yes (MID)")
        # sensitive with DF2 DISCRIMINATING: no LIBERAL sentence
        r, L, _F = run(sub(tmp, 4), spec=_merge(_ks("KK_STRONG", 486, [0] * 5), _ks("KK_MID", 486, [0] * 5)))
        has(L, SENT_SUPPORTED)
        assert SENT_LIBERAL not in L
        # n 441 decides DF1b only and its SENSITIVE word is WITHHELD; EDGE never enters DF1
        r, L, _F = run(sub(tmp, 5), spec=_merge(_ks("KK_STRONG", 441, [0] * 5), _ks("KK_MID", 441, [0] * 5),
                                                 _ks("KK_EDGE", 486, [0] * 5)))
        has(L, DF1L + "DEFL-INSENSITIVE")
        has(L, DF1bL + "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED (the DEFL-SENSITIVE word is WITHHELD at n 441: descriptive)")
        assert not any(x.startswith(DF1bL + "DEFL-SENSITIVE") for x in L)
        has(L, "PAIR EDGE (economics + physics) n 486: 5 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE (descriptive)")
        # DF1b MIXED: one pair at size at n 441
        r, L, _F = run(sub(tmp, 7), spec=_ks("KK_MID", 441, [0] * 5))
        has(L, DF1bL + "MIXED")
        # DF2 reads n 486, not n 441
        r, L, _F = run(sub(tmp, 6), spec=_merge(_ks("K2_economics", 441, [0] * 5), _ks("K2_math", 441, [0] * 5)))
        has(L, "DF2 (n 486; economics, math, physics): 0 of 3 anchors DEFL-CERTIFIED-AT-SIZE -> DISCRIMINATING")
        has(L, "ANCHOR math n 441: 5 of 5 DEFL-CERT, 0 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE (descriptive)")

    def df0_gate(tmp):
        # 3 of 20 (all in the math block, the last sites read) -> ANTI-CONSERVATIVE: DF1 / DF1b / DF2 NOT EVALUABLE
        r, L, _F = run(sub(tmp, 1), spec=_merge(SENS, _nc("math", [300] * 7 + [0, 14, 2])))
        has(L, "DF0 (gate): 3 of 20 negative-control sites DEFL-CERT, 0 NOT EVALUABLE (STRONG 0 of 10, math 3 of 10; reached min 299 / "
               "max 299): ANTI-CONSERVATIVE (VALID-NULL iff <= 2)")
        has(L, DF1L + "NOT EVALUABLE (DF0 ANTI-CONSERVATIVE; the pair words would read DEFL-SENSITIVE)")
        has(L, DF1bL + "NOT EVALUABLE (DF0 ANTI-CONSERVATIVE; the pair words would read DEFL-INSENSITIVE)")
        has(L, "DF2 (n 486; economics, math, physics): 2 of 3 anchors DEFL-CERTIFIED-AT-SIZE -> NOT EVALUABLE (DF0 ANTI-CONSERVATIVE; "
               "the anchor words would read LIBERAL)")
        has(L, "F-DF: NOT FIRED (DF1 NOT EVALUABLE).")
        has(L, "READING: none (DF1 NOT EVALUABLE; no sentence)")
        has(L, "P2 DF1: NOT SCORED (DF1 NOT EVALUABLE)")
        has(L, "P3 DF2: NOT SCORED (DF2 NOT EVALUABLE)")
        has(L, "P4 DF0 VALID-NULL (p 0.95): event no, Brier 0.9025")
        assert SENT_SUPPORTED not in L and SENT_FDF_FIRED not in L and r["fired"] is False
        # ANTI-CONSERVATIVE with an INSENSITIVE pair pattern: F-DF must NOT fire
        r, L, _F = run(sub(tmp, 2), spec=_nc("STRONG", [0, 0, 0] + [300] * 7))
        has(L, DF1L + "NOT EVALUABLE (DF0 ANTI-CONSERVATIVE; the pair words would read DEFL-INSENSITIVE)")
        assert SENT_FDF_FIRED not in L and r["fired"] is False
        # the gate's boundary site: k 15 does not count, k 14 does
        r, L, _F = run(sub(tmp, 3), spec=_nc("STRONG", [15, 15, 15, 14] + [300] * 6))
        starts(L, "DF0 (gate): 1 of 20 negative-control sites DEFL-CERT, 0 NOT EVALUABLE (STRONG 1 of 10, math 0 of 10;")
        # C-2 disclosure: 11 negative-control sites with declared < 0 cannot pass (k 300 whatever the null)
        spec = {"NC_%s_n486_s%d" % (t, i): dict(k=200, d=-0.001) for t, i in [("STRONG", j) for j in range(1, 8)] +
                [("math", j) for j in (1, 2, 3, 9)]}
        r, L, _F = run(sub(tmp, 4), spec=spec)
        has(L, "DF0 DISCLOSURE (C-2): DF0 rests on the 9 of 20 negative-control sites able to pass (declared >= 0); 11 have declared < 0 "
               "and cannot DEFL-CERT (a non-splitting replicate scores 0.0 >= declared); DF0 detects collapse, not calibration; P4's "
               "Brier is not a calibration score of the deflated null")
        ln = starts(L, "  NC_math_n486_s9 ")
        assert "k_defl 300 of 300 -> not DEFL-CERT" in ln, ln
        # DF0 with a DEGENERATE NC site: 2 DEFL-CERT + 1 NOT EVALUABLE -> NOT EVALUABLE (Q-K1), DF1 NOT EVALUABLE
        r, L, _F = run(sub(tmp, 5), spec=_merge(SENS, _nc("math", [0, 0] + [300] * 8),
                                                 {"NC_STRONG_n486_s4": dict(k=0, reached=5, d=0.5)}))
        starts(L, "DF0 (gate): 2 of 20 negative-control sites DEFL-CERT, 1 NOT EVALUABLE (STRONG 0 of 10, math 2 of 10; reached min 5 / ")
        assert any(x.startswith("DF0 (gate): ") and x.endswith(": NOT EVALUABLE (VALID-NULL iff <= 2)") for x in L), L
        has(L, DF1L + "NOT EVALUABLE (DF0 NOT EVALUABLE; the pair words would read DEFL-SENSITIVE)")
        # 1 DEFL-CERT + 1 NOT EVALUABLE -> VALID-NULL either way
        r, L, _F = run(sub(tmp, 6), spec=_merge(SENS, _nc("math", [0] + [300] * 9), {"NC_STRONG_n486_s4": dict(k=0, reached=5, d=0.5)}))
        assert any(x.startswith("DF0 (gate): 1 of 20") and x.endswith(": VALID-NULL (VALID-NULL iff <= 2)") for x in L), L
        has(L, DF1L + "DEFL-SENSITIVE")

    def predictions(tmp):
        # P1 median of 5 STRONG n-486 p95 (284 sc): sc chosen so the median sits exactly at 0.085 (HELD, closed); min / max differ
        s0 = 0.085 / 284
        while 284 * s0 < 0.085:
            s0 = math.nextafter(s0, 1.0)
        while 284 * s0 > 0.085:
            s0 = math.nextafter(s0, 0.0)
        assert 284 * s0 == 0.085
        sc = [s0 * f if f != 1.0 else s0 for f in (0.5, 0.9, 1.0, 1.2, 1.5)]
        spec = {"KK_STRONG_n486_d%d" % (i + 1): dict(k=100, sc=s) for i, s in enumerate(sc)}
        r, L, _F = run(sub(tmp, 1), spec=_merge(spec, _ks("KK_MID", 486, [100] * 5, sc=0.0001)))
        ln = starts(L, "P1 deflated p95 at STRONG's n-486 subsamples, median of 5 = ")
        assert ln.endswith(": HELD"), ln
        assert "= 0.085000 in" in ln, ln
        sc2 = [0.1181 / 284 * f for f in (0.5, 0.9, 1.0, 1.01, 1.02)]
        spec2 = {"KK_STRONG_n486_d%d" % (i + 1): dict(k=100, sc=s) for i, s in enumerate(sc2)}
        r, L, _F = run(sub(tmp, 2), spec=spec2)
        ln = starts(L, "P1 deflated p95 at STRONG's n-486 subsamples, median of 5 = ")
        assert ln == "P1 deflated p95 at STRONG's n-486 subsamples, median of 5 = 0.118100 in [0.085, 0.118]: FAILED", ln
        assert median([1.0, 3.0, 2.0, 10.0, 0.0]) == 2.0 and median([1.0, 2.0, 3.0, 4.0]) == 2.5
        assert in_closed(0.118, *P1_BAND) and in_closed(0.085, *P1_BAND) and not in_closed(0.0849999, *P1_BAND)
        assert abs(brier(P2_PROBS, "DEFL-SENSITIVE") - 0.965) < 1e-12 and abs(brier(P3_PROBS, "DISCRIMINATING") - 0.375) < 1e-12
        assert abs(brier(P2_PROBS, "ELONGATION-CONFOUNDED") - 0.765) < 1e-12

    def degenerate(tmp):
        # C-1 (amended): a DEGENERATE site is NOT EVALUABLE; MID 1 DEFL-CERT + 1 NOT EVALUABLE -> {DEFL-NOT, MIXED} -> NOT EVALUABLE
        r, L, _F = run(sub(tmp, 1), spec={"KK_MID_n486_d2": dict(k=0, sc=0.0004, reached=19),
                                         "KK_MID_n486_d3": dict(k=0, sc=0.0004, reached=20)})
        ln = starts(L, "  KK_MID_n486_d2 ")
        assert "-> NOT EVALUABLE (DEGENERATE) (reached 19)" in ln, ln
        ln = starts(L, "  KK_MID_n486_d3 ")
        assert "-> DEFL-CERT (reached 20)" in ln, ln
        has(L, "PAIR MID (engineering + law) n 486: 1 of 5 DEFL-CERT, 1 NOT EVALUABLE -> NOT EVALUABLE")
        has(L, DF1L + "NOT EVALUABLE")
        has(L, "F-DF: NOT FIRED (DF1 NOT EVALUABLE).")
        has(L, "P2 DF1: NOT SCORED (DF1 NOT EVALUABLE)")
        # a NOT EVALUABLE site that cannot change the word: MID 4 DEFL-CERT + 1 DEGENERATE -> at size -> SENSITIVE
        r, L, _F = run(sub(tmp, 2), spec=_merge(_ks("KK_STRONG", 486, [0] * 5), _ks("KK_MID", 486, [0, 0, 0, 0, 0]),
                                                 {"KK_MID_n486_d2": dict(k=0, reached=19, d=0.12)}))
        has(L, "PAIR MID (engineering + law) n 486: 4 of 5 DEFL-CERT, 1 NOT EVALUABLE -> DEFL-CERTIFIED-AT-SIZE")
        has(L, DF1L + "DEFL-SENSITIVE")
        # a DEGENERATE control site that could change the control's word: 3 DEFL-CERT + 1 NOT EVALUABLE -> pair NOT EVALUABLE
        r, L, _F = run(sub(tmp, 3), spec=_merge(_ks("KK_STRONG", 486, [0] * 5), _ks("KK_MID", 486, [0] * 5),
                                                 _ks("EC_STRONG", 486, [0, 0, 0, 15, 15]),
                                                 {"EC_STRONG_n486_d4": dict(k=0, reached=10, d=0.04)}))
        starts(L, "CONTROL STRONG n 486 (elongation cut at the PC1 median): 3 of 5 DEFL-CERT, 1 NOT EVALUABLE -> NOT EVALUABLE; margin")
        has(L, "PAIR-WORD STRONG (amended DF1): NOT EVALUABLE")
        has(L, DF1L + "NOT EVALUABLE")
        has(L, "P5 STRONG elongation-cut control DEFL-CERTIFIED-AT-SIZE (p 0.70): NOT SCORED (control NOT EVALUABLE)")
        # ... unless the margin already fails: then CONFOUNDED either way
        r, L, _F = run(sub(tmp, 4), spec=_merge(_ks("KK_STRONG", 486, [0] * 5), _ks("KK_MID", 486, [0] * 5),
                                                 _ks("EC_STRONG", 486, [0, 0, 0, 15, 15], sc=0.002),
                                                 {"EC_STRONG_n486_d4": dict(k=0, reached=10, d=0.6)}))
        has(L, "PAIR-WORD STRONG (amended DF1): ELONGATION-CONFOUNDED")
        has(L, DF1L + "ELONGATION-CONFOUNDED")

    def refusals(tmp):
        i = [0]

        def t(needle, **kw):
            i[0] += 1
            refused(sub(tmp, i[0]), needle, **kw)
        t("the arm's status is 'REFUSED: x'", status="REFUSED: x")
        t("instrument: the arm ran arm='certKnownPair'", arm_name="certKnownPair")
        t("instrument: the arm ran deflSeedBase='88820260908'", seed_base="88820260908")
        t("the arm read snapshot 'other'", snapshot="other")
        t("the arm read site file sha256", site_sha_bad=True)
        t("is not SITES_SHA256", pins_override=dict(SITES_SHA256="0" * 64))
        t("the site file is not the one the CPC labels", tamper=True, pins_override=None)
        t("the site file is not the one the CPC labels", tamper_ec=True, pins_override=None)
        t("sites.csv holds", drop_site="EC_MID_n486_d5")
        t("seeded by base 20261004 / id OTHER", seed_lie="EC_STRONG_n486_d2")
        t("embeddings_cache.db changed during the arm", hashes_equal=False)
        t("sites.csv holds", drop_site="NC_math_n486_s10")
        t("not 0..299 in order (a partial file)", partial="K2_physics_n441_d5")
        t("replicates.csv holds arm 'SN'", extra_arm="KK_EDGE_n441_d5")
        t("IDENTITY FAILED", ident_d=0.1078039)
        t("IDENTITY FAILED", ident_n=6992)
        t("IDENTITY FAILED", ident_null=True)
        t("sites.csv: NC_STRONG_n486_s7 n 487", n_lie="NC_STRONG_n486_s7")
        t("sites.csv: K2_math_n805_d0 n 805 groups 2 sizes 1/485", gs_lie="K2_math_n805_d0")
        t("the deflation removed 0 dims", dims="KK_MID_n441_d2")
        t("seeded by base 20261004 / id OTHER", seed_lie="K2_economics_n486_d4")
        t("k_defl recount", k_lie="NC_math_n486_s10")
        t("deflated p50 / p95 recount", p95_lie="KK_EDGE_n441_d5")
        t("reached recount", reached_lie="K2_physics_n778_d0")
        t("differs from its outcome of record", rec_lie="KK_EDGE_n441_d5")
        t("differs from its outcome of record", rec_lie="K2_physics_n441_d5")
        t("the outcome of record holds no row for K2_physics_n441_d5", rec_drop="K2_physics_n441_d5")
        t("the outcome of record holds no row for KK_STRONG_n1254_d0", rec_drop="KK_STRONG_n1254_d0")
        t("is sha256", pins_override=dict(K2_REC_SHA="0" * 64))
        t("is sha256", pins_override=dict(KK_REC_SHA="0" * 64))
        t("are not the site files of record", pins_override=dict(KK_SITES_SHA="0" * 64))
        t("are not the site files of record", pins_override=dict(K2_SITES_SHA="0" * 64))
        t("is sha256", pins_override=dict(LABELS_SHA="0" * 64))
        F = _fx(sub(tmp, 98))                            # a deflated-null certification worded "certified" never reaches the file
        try:
            with _pins(DOES_NOT_SHOW="DOES NOT SHOW: whether the pair is certified", **F["pins"]):
                analyze(F["arm"], F["out"], F["sites"], F["labels"], F["kk"], F["k2"], _fixture_vec, out=lambda s: None)
            raise AssertionError("an outcome worded 'certified' was written")
        except SystemExit as e:
            assert "internal: a deflated-null certification worded as 'certified'" in str(e), e
            assert not os.path.exists(os.path.join(F["out"], OUTCOME_NAME))
        F = _fx(sub(tmp, 99))
        os.remove(os.path.join(F["out"], "emb_hashes_after.json"))
        try:
            with _pins(**F["pins"]):
                analyze(F["arm"], F["out"], F["sites"], F["labels"], F["kk"], F["k2"], _fixture_vec, out=lambda s: None)
            raise AssertionError("ran without the hashes")
        except SystemExit as e:
            assert "hashes before and after the arm are owed" in str(e), e

    def blind(tmp):
        try:
            read_record(os.path.join(tmp, "x.csv"), "0", ("site", "defl_k"))
            raise AssertionError("a defl column was read")
        except SystemExit as e:
            assert "the deflated columns on disk are read only by --replication" in str(e), e
        F = _fx(sub(tmp, 1))
        got = read_record(F["k2"], F["pins"]["K2_REC_SHA"], ("site", "declared", "k_d", "null_p95"))
        assert all(set(v) == {"site", "declared", "k_d", "null_p95"} for v in got.values()) and len(got) == 30
        assert not any("777777" in json.dumps(v) for v in got.values())
        # replication refuses before the outcome; after it, the agreement count is printed
        kd = os.path.join(tmp, "k2arm.csv")
        kkd = os.path.join(tmp, "kkarm.csv")
        try:
            replication(F["out"], kd, kkd, out=lambda s: None)
            raise AssertionError("replication ran before the outcome")
        except SystemExit as e:
            assert "only AFTER the outcome" in str(e), e
        r, L, F2 = run(sub(tmp, 2), spec=_ks("K2_math", 486, [0, 0, 300, 300, 300]))
        B = F2["B"]
        with open(kd, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["role", "site_id", "n", "groups", "group_sizes", "declared_stat", "k_declared", "defl_dims", "defl_k_declared",
                        "c0_p95", "c0_seed", "null_seed_id", "reps"])
            for s in B["names"][1]:
                if not s.endswith("_d0"):
                    w.writerow(["K2", s, 486, 2, "x", 0.1, 5, 1, 0 if s in ("K2_math_n486_d1", "K2_math_n486_d3") else 100, 0.1, 1, s, 300])
        with open(kkd, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["role", "site_id", "n", "groups", "group_sizes", "declared_stat", "k_declared", "defl_dims", "defl_k_declared",
                        "c0_p95", "c0_seed", "null_seed_id", "reps"])
            w.writerow(["IDENTITY", "IDENTITY", 6993, 14, "x", 0.1, 0, "", "", "", "", "n00000001", 300])
            for s in B["names"][0]:
                w.writerow(["KK", s, 486, 2, "x", 0.1, 5, "", "", 0.1, 1, s, 300])
        lines = []
        with _pins(K2_ARM_SHA=sha256_bytes(open(kd, "rb").read()), KK_ARM_SHA=sha256_bytes(open(kkd, "rb").read())):
            agree, n = replication(F2["out"], kd, kkd, out=lines.append)
        assert (agree, n) == (28, 30), (agree, n)
        has(lines, "REPLICATION: the per-site word agrees on 28 of 30 K2 subsamples (two independently seeded deflated nulls)")
        has(lines, "CERT-PC-K2-KNOWN arm: 0 of 33 KK sites carry a deflated value (certKnownPair drew no deflated null: registration "
                   "defect R-1)")
        assert os.path.isfile(os.path.join(F2["out"], REPL_NAME))
        try:
            with _pins(K2_ARM_SHA="0" * 64, KK_ARM_SHA=sha256_bytes(open(kkd, "rb").read())):
                os.remove(os.path.join(F2["out"], REPL_NAME))
                replication(F2["out"], kd, kkd, out=lambda s: None)
            raise AssertionError("replication read an unpinned arm file")
        except SystemExit as e:
            assert "is not the pinned arm file" in str(e), e
        half = sub(tmp, 3)                               # the outcome without its CSV: still refused (READY C-4 X6)
        shutil.copy(os.path.join(F2["out"], OUTCOME_NAME), os.path.join(half, OUTCOME_NAME))
        try:
            replication(half, kd, kkd, out=lambda s: None)
            raise AssertionError("replication ran without df_sites.csv")
        except SystemExit as e:
            assert "only AFTER the outcome" in str(e), e

    def site_file(tmp):
        cat, src, B = _fixture_build()
        kkn, k2n, ncn, ecn = B["names"]
        assert len(kkn) == 33 and len(k2n) == 33 and len(ncn) == 20 and len(ecn) == 10 and len(B["sites"]) == 97
        assert ecn == ["EC_%s_n486_d%d" % (r, d) for r in ("STRONG", "MID") for d in DRAWS] and list(B["sites"])[-10:] == ecn
        vec = _fixture_vec(sorted({q for e in ecn for q in B["sites"][e]}))
        for e in ecn:
            srcn = "KK_" + e[3:]
            lab = B["labels"][e]
            assert B["sites"][e] == B["sites"][srcn] and group_sizes(lab) == "243/243" and set(lab.values()) == set(EC_LABELS), e
            ids = B["sites"][e]
            x = np.array([vec[q] for q in ids])
            xc = x - x.mean(axis=0)
            v = np.linalg.svd(xc, full_matrices=False)[2][0]
            v = v if v[int(np.argmax(np.abs(v)))] > 0 else -v            # the orientation rule: largest |loading| positive
            scr = xc @ v
            lo = {q for q, z in zip(ids, scr) if lab[q] == "pc_lo"}
            hi_min = min(z for q, z in zip(ids, scr) if q not in lo)
            lo_max = max(z for q, z in zip(ids, scr) if q in lo)
            assert lo_max < hi_min, (e, lo_max, hi_min)                   # pc_lo = the LOWER half of the oriented PC1 scores
        # the cut follows PC1 (orientation-fixed), ties to the lower half, and refuses a cut equal to the declared partition
        toy = {"a%d" % k: np.array([float(k), 0.0, 0.0]) for k in range(6)}
        toy["a5"] = np.array([2.0, 0.0, 0.0])                      # scores 0,1,2,3,4,2: lower median 2 -> a0,a1,a2,a5 below
        cut = ec_cut(sorted(toy), toy, {q: ("x" if q in ("a0", "a3") else "y") for q in toy})
        assert sorted(q for q in cut if cut[q] == "pc_lo") == ["a0", "a1", "a2", "a5"], cut
        try:
            ec_cut(sorted(toy), toy, {q: ("x" if q in ("a0", "a1", "a2", "a5") else "y") for q in toy})
            raise AssertionError("a cut equal to the declared partition was accepted")
        except SystemExit as e2:
            assert "reproduces the declared partition" in str(e2), e2
        try:
            ec_cut(sorted(toy), toy, {q: ("x" if q in ("a3", "a4") else "y") for q in toy})
            raise AssertionError("a cut equal to the declared complement was accepted")
        except SystemExit as e2:
            assert "reproduces the declared partition" in str(e2), e2
        assert [s for s in k2n if s.endswith("_d0")] == ["K2_economics_n504_d0", "K2_math_n805_d0", "K2_physics_n778_d0"], k2n
        assert kkn[0] == "KK_STRONG_n1254_d0" and kkn[11] == "KK_MID_n1158_d0" and kkn[22] == "KK_EDGE_n1282_d0", kkn
        assert ncn[0] == "NC_STRONG_n486_s1" and ncn[10] == "NC_math_n486_s1"
        assert B["kk_bytes"] == PKK.build_site_bytes(cat, src, kk_pairs())[0] and B["k2_bytes"] == PK2.build_site_bytes(cat, src)[0]
        # the KK and K2 subsample rows of the combined file are exactly the imported builders' rows
        rows = B["data"].decode().split("\n")[1:-1]
        kk_rows = set(B["kk_bytes"].decode().split("\n")[1:-1])
        k2_rows = set(r for r in B["k2_bytes"].decode().split("\n")[1:-1] if not r.startswith("IDENTITY\t"))
        assert kk_rows <= set(rows) and k2_rows <= set(rows)
        full = B["labels"]["K2_math_n805_d0"]
        assert group_sizes(full) == "316/489" and set(full.values()) == {"added", "ori_mmlu"} and TWINS[0] not in full
        assert all(cat[q] == "math" for q in full) and all(set(B["sites"]["K2_math_n486_d%d" % d]) <= set(full) for d in DRAWS)
        for t, srcname in NC_SOURCES:
            srcl = B["labels"][srcname]
            for s in NC_SEEDS:
                nl = B["labels"]["NC_%s_n486_s%d" % (t, s)]
                assert sorted(nl) == sorted(srcl) and group_sizes(nl) == group_sizes(srcl), (t, s)
                first = sorted(set(srcl.values()))[0]
                agree = sum(1 for q in srcl if (srcl[q] == first) == (nl[q] == "rel_a"))
                assert 150 < agree < 336, (t, s, agree)        # random: about half agree, never the source partition
            assert len({json.dumps(B["labels"]["NC_%s_n486_s%d" % (t, s)], sort_keys=True) for s in NC_SEEDS}) == 10
        lab = {"a%d" % i: ("x" if i < 3 else "y") for i in range(8)}
        assert relabel(lab, 1) == relabel(lab, 1) and group_sizes(relabel(lab, 1)) == "3/5"
        try:
            relabel({"a": "x", "b": "y"}, 1)
            raise AssertionError("a 2-item relabelling equal to the source (or its complement) was accepted")
        except SystemExit as e:
            assert "reproduces the source partition" in str(e), e
        assert sha256_bytes(B["data"]) == SITE_FIXTURE_SHA, sha256_bytes(B["data"])
        # check_sources: rebuilt KK / K2 rows vs the pinned site files
        dr = os.path.join(tmp, "dr")
        for rel, b in ((PKK.OUT_REL, B["kk_bytes"]), (PK2.OUT_REL, B["k2_bytes"])):
            os.makedirs(os.path.join(dr, rel))
            open(os.path.join(dr, rel, SITES_NAME), "wb").write(b)
        with _pins(KK_SITES_SHA=sha256_bytes(B["kk_bytes"]), K2_SITES_SHA=sha256_bytes(B["k2_bytes"])):
            check_sources(B, dr)
            open(os.path.join(dr, PK2.OUT_REL, SITES_NAME), "wb").write(B["k2_bytes"] + b"x")
            try:
                check_sources(B, dr)
                raise AssertionError("a K2 site file differing from the rebuild was accepted")
            except SystemExit as e:
                assert "differs from the K2 sites rebuilt" in str(e), e
        try:
            check_sources(B, dr)
            raise AssertionError("an unpinned KK rebuild was accepted")
        except SystemExit as e:
            assert "the KK sites rebuilt from the labels are sha256" in str(e), e

    def declared(tmp):
        cat, src, B = _fixture_build()
        stat_of = {s: 0.05 for s in B["labels"]}
        stat_of["IDENTITY"] = IDENTITY_FULL
        kk_rec = {s: {"declared": "0.050000"} for s in B["names"][0]}
        k2_rec = {s: {"declared": "0.050000"} for s in B["names"][1] if not s.endswith("_d0")}
        lines = []
        cnt, worst = check_declared(stat_of, kk_rec, k2_rec, B["names"], out=lines.append)
        assert (cnt, worst) == (63, 0.0) and lines[0].startswith("%s DECLARED CHECK: IDENTITY" % TAG), lines
        for mod, needle in ((("IDENTITY", IDENTITY_FULL + 2e-9), "IDENTITY: the statistic"),
                            (("KK_EDGE_n441_d5", 0.0500006), "KK_EDGE_n441_d5: declared"),
                            (("K2_physics_n441_d5", 0.0499994), "K2_physics_n441_d5: declared")):
            so = dict(stat_of)
            so[mod[0]] = mod[1]
            try:
                check_declared(so, kk_rec, k2_rec, B["names"], out=lambda s: None)
                raise AssertionError("not refused: " + needle)
            except SystemExit as e:
                assert needle in str(e), e
        so = dict(stat_of)
        so["KK_EDGE_n441_d5"] = 0.0500004                        # within the 6-digit rounding
        check_declared(so, kk_rec, k2_rec, B["names"], out=lambda s: None)
        k2b = dict(k2_rec)
        del k2b["K2_math_n441_d5"]
        try:
            check_declared(stat_of, kk_rec, k2b, B["names"], out=lambda s: None)
            raise AssertionError("a missing record row was accepted")
        except SystemExit as e:
            assert "holds no row for K2_math_n441_d5" in str(e), e

    def helpers(tmp):
        assert site_word(14, 300) == "DEFL-CERT" and site_word(15, 300) == "not DEFL-CERT" and site_word(0, 20) == "DEFL-CERT"
        assert site_word(0, 19) == NE_DEG and site_word(300, 0) == NE_DEG
        C, X, E = "DEFL-CERT", "not DEFL-CERT", NE_DEG
        assert size_word([C] * 4 + [X]) == AT and size_word([C] + [X] * 4) == DNOT
        assert size_word([C] * 3 + [X] * 2) == MIX and size_word([C] * 2 + [X] * 3) == MIX
        assert size_word([C] * 4 + [E]) == AT and size_word([X] * 4 + [E]) == DNOT and size_word([C] * 3 + [E] + [X]) == NE
        assert size_word([C] + [E] + [X] * 3) == NE and size_word([C] * 2 + [E] + [X] * 2) == MIX and size_word([E] * 2 + [C] * 3) == NE
        assert size_possible([C] * 3 + [E] + [X]) == {MIX, AT}
        assert df0_word(2) == "VALID-NULL" and df0_word(3) == "ANTI-CONSERVATIVE" and df0_word(0) == "VALID-NULL"
        assert df0_word(2, 1) == NE and df0_word(1, 1) == "VALID-NULL" and df0_word(3, 2) == "ANTI-CONSERVATIVE"
        S, CF = "SENSITIVE-PAIR", "ELONGATION-CONFOUNDED"
        assert df1_definite([S, S]) == "DEFL-SENSITIVE" and df1_definite([DNOT, DNOT]) == "DEFL-INSENSITIVE"
        assert df1_definite([CF, S]) == CF and df1_definite([S, CF]) == CF and df1_definite([CF, CF]) == CF
        assert df1_definite([CF, MIX]) == CF and df1_definite([CF, DNOT]) == MIX and df1_definite([S, MIX]) == MIX
        assert df1_definite([S, DNOT]) == MIX and df1_definite([MIX, MIX]) == MIX and df1_definite([DNOT, MIX]) == MIX
        assert pair_possible({AT}, {DNOT}, True) == {S} and pair_possible({AT}, {MIX}, True) == {S}
        assert pair_possible({AT}, {AT}, True) == {CF} and pair_possible({AT}, {DNOT}, False) == {CF}
        assert pair_possible({AT}, {MIX, AT}, True) == {S, CF} and pair_possible({AT}, {MIX, AT}, False) == {CF}
        assert pair_possible({MIX}, {AT}, False) == {MIX} and pair_possible({DNOT, MIX}, {DNOT}, True) == {DNOT, MIX}
        assert over([{S}, {S, CF}], df1_definite) == NE and over([{S}, {S}], df1_definite) == "DEFL-SENSITIVE"
        assert over([{CF}, {S, CF}], df1_definite) == CF
        assert df1b_definite([AT, AT]) == "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED" and df1b_definite([DNOT, DNOT]) == "DEFL-INSENSITIVE"
        assert df1b_definite([AT, DNOT]) == MIX
        assert df2_definite([AT, AT, MIX]) == "LIBERAL" and df2_definite([MIX] * 3) == "DISCRIMINATING" and df2_definite([AT, MIX, DNOT]) == MIX
        ok, m, sd = margin_ok([0.1] * 5, [0.1] * 5)                 # margin 0 is not > SD 0
        assert (ok, m, sd) == (False, 0.0, 0.0), (ok, m, sd)
        ok, m, sd = margin_ok([0.10, 0.12, 0.14, 0.16, 0.18], [0.10] * 5)    # mean margin 0.04; sample SD 0.0316 (population 0.0283)
        assert ok and abs(m - 0.04) < 1e-12 and abs(sd - math.sqrt(0.001)) < 1e-12, (m, sd)
        ok, m, sd = margin_ok([0.10, 0.12, 0.14, 0.16, 0.18], [0.11] * 5)    # 0.03 is above the population SD, below the sample SD
        assert not ok and abs(m - 0.03) < 1e-12, (m, sd)
        ok, m, sd = margin_ok([0.10, 0.12, 0.14, 0.16, 0.18], [0.10, 0.10, 0.10, 0.10, 0.18])   # every draw enters the mean: 0.024
        assert not ok and abs(m - 0.024) < 1e-12, m
        assert wording_violations(["site X CERTIFIED", "DEFL-CERT ok", "deflated-null certified ok", "the certificate of record"]) == \
            ["site X CERTIFIED"]
        assert wording_violations(["not certified under the plain null of record"]) == []
        assert wording_violations(["it is certified (not plain)", "uncertified"]) == ["it is certified (not plain)", "uncertified"]
        for s in (SENT_FDF_FIRED, SENT_SUPPORTED, SENT_LIBERAL, SENT_INSENSITIVE_WOULD, WOULD_NOT, DOES_NOT_SHOW, SENT_CONFOUNDED,
                  DF2_CAVEAT):
            assert wording_violations([s]) == [], s
        cfg = dict(jvmThreads=12, nullReps=300, sliceDim=512, sepBar=0.0145, dropTop=0, whiten=False)
        c = command(cfg, 6)
        assert c.startswith(".\\gradlew.bat certK2Deflated ") and '"-DsepBar=0.0145"' in c and "-PnullReps=300" in c and \
            '"-DoutDir=%s/%s"' % (OUT_REL, ARM_NAME) in c and "siteNullHeap" not in c, c
        assert '"-DsiteNullHeap=9g"' in command(cfg, 9)

    def main_analyze(tmp):
        global OUT_REL
        F = _fx(sub(tmp, 1), spec=_merge(_ks("KK_STRONG", 486, [15, 15, 15, 15, 15])))
        os.replace(F["arm"], os.path.join(F["out"], ARM_NAME))
        dr = os.path.join(tmp, "dataroot")
        for rel, p in ((KK_REC_REL, F["kk"]), (K2_REC_REL, F["k2"])):
            os.makedirs(os.path.dirname(os.path.join(dr, rel)), exist_ok=True)
            shutil.copy(p, os.path.join(dr, rel))
        _fixture_db(os.path.join(dr, "embeddings_cache.db"), sorted({q for e in F["B"]["names"][3] for q in F["B"]["sites"][e]}))
        saved = OUT_REL, PKK._IN_SELFTEST
        OUT_REL, PKK._IN_SELFTEST = os.path.abspath(F["out"]), True        # PKK.load_vectors opens the fixture cache mode=ro
        try:
            with _pins(**F["pins"]):
                rc = main(["--analyze", "--cpc-labels", F["labels"], "--data-root", dr])
            assert rc == 0, rc
        finally:
            OUT_REL, PKK._IN_SELFTEST = saved
        txt = open(os.path.join(F["out"], OUTCOME_NAME), encoding="utf-8").read()
        assert "\nDF1 (n 486; STRONG, MID; amended 26605924): DEFL-INSENSITIVE\n" in txt and "\n" + SENT_FDF_FIRED + "\n" in txt, txt[-1500:]
        assert "\nDF0 (gate): 0 of 20 negative-control sites DEFL-CERT" in txt

    def main_red_gate(tmp):
        global _IN_SELFTEST, selftest
        saved = (_IN_SELFTEST, selftest)
        _IN_SELFTEST, selftest = False, (lambda: 1)
        try:
            main(["--analyze", "--cpc-labels", os.path.join(tmp, "none.tsv")])
            raise AssertionError("main --analyze ran on a red selftest")
        except SystemExit as e:
            assert "the selftest is red: no readout" in str(e), e
        finally:
            _IN_SELFTEST, selftest = saved

    for nm, fn in [("main --analyze (the run-of-record wiring)", main_analyze),
                   ("main --analyze refuses on a red selftest", main_red_gate),
                   ("DEFL-SENSITIVE + LIBERAL: every printed line, write-once, blind, wording", sensitive),
                   ("DEFL-INSENSITIVE / MIXED / refutation / n 441 / EDGE / DF2 at n 486", insensitive),
                   ("DF0 gate: 2 / 3 of 20, NOT EVALUABLE, F-DF not fired, k 14 / 15, C-2 disclosure, NC DEGENERATE", df0_gate),
                   ("P1 median closed band, Brier", predictions),
                   ("amended DF1: ELONGATION-CONFOUNDED by the control / the margin, control boundary 3 / 4 of 5", confounded),
                   ("DEGENERATE = NOT EVALUABLE (C-1) with the Q-K1 withholding rule, at sites and controls", degenerate),
                   ("refusals", refusals),
                   ("blindness: read_record, replication only after the outcome", blind),
                   ("site file: KK / K2 rows of record, full sites, NC relabelling", site_file),
                   ("declared check vs the outcomes of record", declared),
                   ("helpers, wording scan, command", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


SITE_FIXTURE_SHA = "33cd87fc9b2b4489d7ada63eab517b0f62a4583be7fbcf253651e7aae78865cd"

MUTANTS = [
    ('M0 control (no-op; must SURVIVE)', 'TAG = "[DFL]"', 'TAG = "[DFL]"'),
    ('M1 DEFL-CERT iff k < 14', '    return "DEFL-CERT" if bool(k <= K_BAR) else "not DEFL-CERT"', '    return "DEFL-CERT" if bool(k < K_BAR) else "not DEFL-CERT"'),
    ('M2 bar k <= 15', 'REPS, K_BAR, DF0_MAX, DEGENERATE_MIN = 300, 14, 2, 20', 'REPS, K_BAR, DF0_MAX, DEGENERATE_MIN = 300, 15, 2, 20'),
    ('M3 AT-SIZE needs 5 of 5', '    if c >= 4:\n        return AT', '    if c >= 5:\n        return AT'),
    ('M4 DEFL-NOT only at 0 of 5', '    if c <= 1:\n        return DNOT', '    if c <= 0:\n        return DNOT'),
    ('M5 size-word MIXED -> DEFL-NOT', '        return DNOT\n    return MIX\n\n\ndef size_possible', '        return DNOT\n    return DNOT\n\n\ndef size_possible'),
    ('M6 DF0 VALID-NULL iff < 2', '("VALID-NULL" if bool(n_cert + j <= DF0_MAX) else "ANTI-CONSERVATIVE")', '("VALID-NULL" if bool(n_cert + j < DF0_MAX) else "ANTI-CONSERVATIVE")'),
    ('M7 DF0 counts the STRONG source only (first block)', '    ncw = [res[s]["word"] for s in ncn]', '    ncw = [res[s]["word"] for s in ncn[:10]]'),
    ('M8 DF0 from the wrong population (the KK sites)', '    ncw = [res[s]["word"] for s in ncn]', '    ncw = [res[s]["word"] for s in kkn[:20]]'),
    ('M9 DF0 gate ignored', '    valid = bool(df0 == "VALID-NULL")', '    valid = True'),
    ('M10 DF1 SENSITIVE if any pair', '    if all(w == "SENSITIVE-PAIR" for w in pws):', '    if any(w == "SENSITIVE-PAIR" for w in pws):'),
    ('M11 DF1 INSENSITIVE if any pair', '    if all(w == DNOT for w in pws):\n        return "DEFL-INSENSITIVE"', '    if any(w == DNOT for w in pws):\n        return "DEFL-INSENSITIVE"'),
    ('M12 DF1 includes EDGE', 'ROLES, DECIDING_ROLES, ANCHORS = PKK.ROLES, ("STRONG", "MID"), PK2.ANCHORS', 'ROLES, DECIDING_ROLES, ANCHORS = PKK.ROLES, ("STRONG", "MID", "EDGE"), PK2.ANCHORS'),
    ('M13 DF1 over STRONG only (first pair)', '    raw1 = over([pair_ps[r] for r in DECIDING_ROLES], df1_definite)', '    raw1 = over([pair_ps[r] for r in DECIDING_ROLES[:1]], df1_definite)'),
    ('M14 F-DF / readings from DF1b (n 441)', '    d1 = df1[486]', '    d1 = df1[441]'),
    ('M15 DF1b read at n 486', '    raw1b = over([size_ps[441][r] for r in DECIDING_ROLES], df1b_definite)', '    raw1b = over([size_ps[486][r] for r in DECIDING_ROLES], df1b_definite)'),
    ('M16 DF2 LIBERAL at >= 1', '    if c >= 2:\n        return "LIBERAL"', '    if c >= 1:\n        return "LIBERAL"'),
    ('M17 DF2 DISCRIMINATING at <= 1', '    if c == 0:\n        return "DISCRIMINATING"', '    if c <= 1:\n        return "DISCRIMINATING"'),
    ('M18 DF2 read at n 441', '    df2_raw = over([anchor_ps[486][a] for a in ANCHORS], df2_definite)', '    df2_raw = over([anchor_ps[441][a] for a in ANCHORS], df2_definite)'),
    ('M19 DF2 over the first anchor only', '    df2_raw = over([anchor_ps[486][a] for a in ANCHORS], df2_definite)', '    df2_raw = over([anchor_ps[486][a] for a in ANCHORS[:1]] * 3, df2_definite)'),
    ('M20 F-DF fires on MIXED too', '    fired = bool(d1 == "DEFL-INSENSITIVE")', '    fired = bool(d1 in ("DEFL-INSENSITIVE", "MIXED"))'),
    ('M21 F-DF fires when NOT EVALUABLE (raw pair words)', '    fired = bool(d1 == "DEFL-INSENSITIVE")', '    fired = bool(raw1 == "DEFL-INSENSITIVE")'),
    ('M22 SUPPORTED sentence on any not-fired', '        if d1 == "DEFL-SENSITIVE":\n            say(SENT_SUPPORTED)', '        if d1 != "DEFL-INSENSITIVE":\n            say(SENT_SUPPORTED)'),
    ('M23 LIBERAL sentence whatever DF2', '            if df2 == "LIBERAL":\n                say(SENT_LIBERAL)', '            if True:\n                say(SENT_LIBERAL)'),
    ('M24 refutation on any pair not AT-SIZE', '        refuted = [r for r in DECIDING_ROLES if pair_w[n][r] == DNOT]', '        refuted = [r for r in DECIDING_ROLES if pair_w[n][r] != AT]'),
    ('M25 refutation line omitted', '        say("%s FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: %s" % (', '        (lambda *a: None)("%s FAILS (rule 8): DEFL-SENSITIVE refuted by a pair at <= 1 of 5: %s" % ('),
    ('M26 pair words from draw 1 only', '        return [res["%s_n%d_d%d" % (prefix, n, dd)]["word"] for dd in DRAWS]', '        return [res["%s_n%d_d%d" % (prefix, n, 1)]["word"] for dd in DRAWS]'),
    ('M27 P1 min (not median)', '    p1 = median(p1v)', '    p1 = min(p1v)'),
    ('M28 P1 max (not median)', '    p1 = median(p1v)', '    p1 = max(p1v)'),
    ('M29 P1 from MID', '    p1v = [res["KK_STRONG_n486_d%d" % dd]["p95"] for dd in DRAWS]', '    p1v = [res["KK_MID_n486_d%d" % dd]["p95"] for dd in DRAWS]'),
    ('M30 P1 from n 441', '    p1v = [res["KK_STRONG_n486_d%d" % dd]["p95"] for dd in DRAWS]', '    p1v = [res["KK_STRONG_n441_d%d" % dd]["p95"] for dd in DRAWS]'),
    ('M31 P1 band half-open', '    return bool(lo <= Fraction(repr(x)) <= hi)', '    return bool(lo < Fraction(repr(x)) <= hi)'),
    ('M32 P1 band upper 0.119', 'P1_BAND = (Fraction("0.085"), Fraction("0.118"))', 'P1_BAND = (Fraction("0.085"), Fraction("0.119"))'),
    ('M33 P1 from p50', '    p1v = [res["KK_STRONG_n486_d%d" % dd]["p95"] for dd in DRAWS]', '    p1v = [res["KK_STRONG_n486_d%d" % dd]["p50"] for dd in DRAWS]'),
    ('M34 P2 scored when NOT EVALUABLE', '    if d1 in P2_PROBS:', '    if True:'),
    ('M35 P3 scored when NOT EVALUABLE', '    if df2 in P3_PROBS:', '    if True:'),
    ('M36 P4 event inverted', '    e4 = valid', '    e4 = not valid'),
    ('M37 P2 scored on the registered (superseded) probabilities', '"outcome %s, Brier (4-way sum) %.4f; the registered DEFL-SENSITIVE 0.40 / MIXED 0.30 / DEFL-INSENSITIVE 0.30 printed "\n            "beside, not scored" % (d1, brier(P2_PROBS, d1))', '"outcome %s, Brier (4-way sum) %.4f; the registered DEFL-SENSITIVE 0.40 / MIXED 0.30 / DEFL-INSENSITIVE 0.30 printed "\n            "beside, not scored" % (d1, brier(P2_REGISTERED, d1))'),
    ('M38 k recount > (not >=)', '        k = CPC.kcount(xs, d)', '        k = sum(1 for x in xs if x > d)'),
    ('M39 p95 recount at 0.94', '        p50, p95 = CPC.pctl(srt, 0.50), CPC.pctl(srt, 0.95)', '        p50, p95 = CPC.pctl(srt, 0.50), CPC.pctl(srt, 0.94)'),
    ('M40 k recount check removed', '        if k != int(r["defl_k_declared"]):', '        if False:'),
    ('M41 reached recount check removed', '        if reached != int(r["defl_reached"]):', '        if False:'),
    ('M42 partial replicates accepted', '        if [i for i, _x in xs] != list(range(REPS)):', '        if False:'),
    ('M43 an arm other than SNDF accepted', '            if r["arm"] != "SNDF":', '            if False:'),
    ('M44 instrument check removed', '        if st.get(k) != v:\n            refuse("instrument', '        if False:\n            refuse("instrument'),
    ('M45 snapshot check removed', '    if st.get("snapshot") != SNAPSHOT:', '    if False:'),
    ('M46 site pin not checked', '    if s_sha != SITES_SHA256:', '    if False:'),
    ('M47 site rebuild not checked', '    if B["data"] != sbytes:', '    if False:'),
    ('M48 arm-read sha not checked', '    if st.get("sites_sha256") != s_sha:', '    if False:'),
    ('M49 hash check removed', '    if json.load(open(hb)) != json.load(open(ha)):', '    if False:'),
    ('M50 KK / K2 site files of record not checked', '    if sha256_bytes(B["kk_bytes"]) != KK_SITES_SHA or sha256_bytes(B["k2_bytes"]) != K2_SITES_SHA:', '    if False:'),
    ('M51 declared vs record not checked', '        if rec is not None and not abs(d - float(rec["declared"])) <= REC_TOL:', '        if False:'),
    ('M52 missing record row accepted', '        if rec is None and (s.startswith("KK_") or (s.startswith("K2_") and not s.endswith("_d0"))):', '        if False:'),
    ('M53 record tolerance x100', 'REC_TOL = 5.0e-7 + 1e-12', 'REC_TOL = 5.0e-5 + 1e-12'),
    ('M54 sites.csv list not checked', '    if list(rows) != want:', '    if False:'),
    ('M55 dims != 1 accepted', '        if r["defl_dims"] != "1":', '        if False:'),
    ('M56 seed base / id not checked', '        if r["defl_seed_base"] != SEED_BASE or r["null_seed_id"] != s:', '        if False:'),
    ('M57 group sizes not checked', ' or int(r["groups"]) != 2 or r["group_sizes"] != gs:', ' or int(r["groups"]) != 2:'),
    ('M58 IDENTITY gate removed', '    if not ("%.6f" % d0 == IDENTITY_DECLARED and int(ir["n"]) == N_ROOT and ir["defl_k_declared"] == ""):', '    if False:'),
    ('M59 IDENTITY may carry a null', ' and int(ir["n"]) == N_ROOT and ir["defl_k_declared"] == ""):', ' and int(ir["n"]) == N_ROOT):'),
    ('M60 write-once pre-check removed', '        if os.path.exists(p):\n            refuse("%s exists: the outcome is write-once" % p)', '        if False:\n            refuse("%s exists: the outcome is write-once" % p)'),
    ('M61 read_record keeps a defl column', '    if bad:\n        refuse("read_record:', '    if False:\n        refuse("read_record:'),
    ('M62 record sha not checked', '    if sha256_bytes(b) != sha:\n        refuse("%s is sha256 %s, not the pinned %s"', '    if False:\n        refuse("%s is sha256 %s, not the pinned %s"'),
    ('M63 replication before the outcome', '    if not os.path.isfile(os.path.join(out_dir, OUTCOME_NAME)) or not os.path.isfile(os.path.join(out_dir, CSV_NAME)):', '    if False:'),
    ('M64 replication arm pins not checked', '        if sha256_bytes(open(p, "rb").read()) != pin:', '        if False:'),
    ('M65 replication agreement always counted', '        agree, n = agree + (1 if wo == wf else 0), n + 1', '        agree, n = agree + 1, n + 1'),
    ('M66 relabel seed + 1', '    random.Random(seed).shuffle(seq)', '    random.Random(seed + 1).shuffle(seq)'),
    ('M67 relabel rel_a = the second label', '    out = {q: (NC_LABELS[0] if seq[i] == cats[0] else NC_LABELS[1]) for i, q in enumerate(ids)}', '    out = {q: (NC_LABELS[0] if seq[i] == cats[1] else NC_LABELS[1]) for i, q in enumerate(ids)}'),
    ('M68 relabel not shuffled', '    random.Random(seed).shuffle(seq)', '    pass'),
    ('M69 relabel source/complement check removed', '    if a == {q for q in ids if lab[q] == cats[0]} or a == {q for q in ids if lab[q] == cats[1]}:', '    if False:'),
    ('M70 NC math from d2', 'NC_SOURCES = (("STRONG", "KK_STRONG_n486_d1"), ("math", "K2_math_n486_d1"))', 'NC_SOURCES = (("STRONG", "KK_STRONG_n486_d1"), ("math", "K2_math_n486_d2"))'),
    ('M71 NC seeds 0..9', 'SIZES, DRAWS, NC_SEEDS = (486, 441), (1, 2, 3, 4, 5), tuple(range(1, 11))', 'SIZES, DRAWS, NC_SEEDS = (486, 441), (1, 2, 3, 4, 5), tuple(range(0, 10))'),
    ('M72 K2 full site = one family only', '        full = sorted(qpops[a][PK2.FAM_ADD] + qpops[a][PK2.FAM_ORI])', '        full = sorted(qpops[a][PK2.FAM_ORI])'),
    ('M73 check_sources: rebuilt vs pin removed', '        if sha256_bytes(b) != pin:\n            refuse("the %s sites rebuilt', '        if False:\n            refuse("the %s sites rebuilt'),
    ('M74 check_sources: on-disk file not compared', '        if os.path.isfile(p) and open(p, "rb").read() != b:', '        if False:'),
    ('M75 check_declared: IDENTITY not checked', '    if not abs(d0 - IDENTITY_FULL) <= TOL:', '    if False:'),
    ('M76 check_declared: K2 subsamples skipped', '    for s in names[0] + [x for x in names[1] if not x.endswith("_d0")]:', '    for s in names[0]:'),
    ('M77 check_declared: values not compared', '        if not diff <= REC_TOL:\n            refuse("%s: declared', '        if False:\n            refuse("%s: declared'),
    ('M78 wording scan disabled', '    bad = []\n    for ln in lines:', '    return []\n    for ln in lines:'),
    ('M79 wording scan not applied to the outcome', '    if bad:\n        refuse("internal: a deflated-null', '    if False:\n        refuse("internal: a deflated-null'),
    ('M80 DEGENERATE threshold 19', 'REPS, K_BAR, DF0_MAX, DEGENERATE_MIN = 300, 14, 2, 20', 'REPS, K_BAR, DF0_MAX, DEGENERATE_MIN = 300, 14, 2, 19'),
    ('M81 selftest gate in main removed', '    if not _IN_SELFTEST and selftest() != 0:', '    if False:'),
    ('M82 analyze reads the K2 record for KK sites', '        rec = (kk_rec if s.startswith("KK_") else k2_rec).get(s) if not s.startswith(("NC_", "EC_")) else None', '        rec = (k2_rec if s.startswith("KK_") else k2_rec).get(s) if not s.startswith(("NC_", "EC_")) else None'),
    ('M83 median of an even list wrong', '    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0', '    return s[n // 2]'),
    ('M84 Brier without the outcome term', '    return sum((p - (1.0 if v == outcome else 0.0)) ** 2 for v, p in probs.items())', '    return sum(p ** 2 for v, p in probs.items())'),
    ('M85 replication guard: outcome.txt only (READY C-4 X6)', '    if not os.path.isfile(os.path.join(out_dir, OUTCOME_NAME)) or not os.path.isfile(os.path.join(out_dir, CSV_NAME)):', '    if not os.path.isfile(os.path.join(out_dir, OUTCOME_NAME)):'),
    ('N1 amended DF1: the control is ignored', '            out.add("SENSITIVE-PAIR" if (cw != AT and mok) else "ELONGATION-CONFOUNDED")', '            out.add("SENSITIVE-PAIR" if (mok) else "ELONGATION-CONFOUNDED")'),
    ('N2 amended DF1: the margin is ignored', '            out.add("SENSITIVE-PAIR" if (cw != AT and mok) else "ELONGATION-CONFOUNDED")', '            out.add("SENSITIVE-PAIR" if (cw != AT) else "ELONGATION-CONFOUNDED")'),
    ('N3 amended DF1: a MIXED control counts as certifying (control <= 1 of 5 needed)', '            out.add("SENSITIVE-PAIR" if (cw != AT and mok) else "ELONGATION-CONFOUNDED")', '            out.add("SENSITIVE-PAIR" if (cw == DNOT and mok) else "ELONGATION-CONFOUNDED")'),
    ('N4 margin >= (not >)', '    return bool(m > sd), m, sd', '    return bool(m >= sd), m, sd'),
    ('N5 margin with the population SD', '    sd = PKK.sd_sample(decl)', '    sd = PKK.sd_pop(decl)'),
    ('N6 margin from draw 1 only', '    m = sum(a - b for a, b in zip(decl, ctrl)) / len(decl)', '    m = decl[0] - ctrl[0]'),
    ('N7 margin against the MID control for both pairs (wrong population)', '        ctrl = [res["EC_%s_n486_d%d" % (role, dd)]["d"] for dd in DRAWS]', '        ctrl = [res["EC_MID_n486_d%d" % dd]["d"] for dd in DRAWS]'),
    ("N8 control word from the pair's own sites", '        cws = words_at("EC_%s" % role, 486)', '        cws = words_at("KK_%s" % role, 486)'),
    ('N9 CONFOUNDED even beside a DEFL-NOT pair', '    if any(w == "ELONGATION-CONFOUNDED" for w in pws) and not any(w == DNOT for w in pws):', '    if any(w == "ELONGATION-CONFOUNDED" for w in pws):'),
    ('N10 CONFOUNDED only if both pairs', '    if any(w == "ELONGATION-CONFOUNDED" for w in pws) and not any(w == DNOT for w in pws):', '    if all(w == "ELONGATION-CONFOUNDED" for w in pws):'),
    ('N11 DF1b SENSITIVE not withheld', '        return "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED"', '        return "DEFL-SENSITIVE"'),
    ('N12 C-1 DEGENERATE ignored (warning only, as before)', '    if reached < DEGENERATE_MIN:\n        return NE_DEG', '    if False:\n        return NE_DEG'),
    ('N13 Q-K1 withholding ignored at the 4-of-5 count', '    e = sum(1 for w in words if w.startswith(NE))\n    return {_size_definite(c + j) for j in range(e + 1)}', '    e = 0\n    return {_size_definite(c + j) for j in range(e + 1)}'),
    ('N14 one(): the first admissible word, never NOT EVALUABLE', '    return next(iter(ws)) if len(ws) == 1 else NE', '    return sorted(ws)[0]'),
    ('N15 DF0 NOT EVALUABLE sites ignored', '    return one({("VALID-NULL" if bool(n_cert + j <= DF0_MAX) else "ANTI-CONSERVATIVE") for j in range(n_ne + 1)})', '    return one({("VALID-NULL" if bool(n_cert + j <= DF0_MAX) else "ANTI-CONSERVATIVE") for j in range(1)})'),
    ('N16 DF0 NOT EVALUABLE passes the gate', '    valid = bool(df0 == "VALID-NULL")', '    valid = bool(df0 != "ANTI-CONSERVATIVE")'),
    ('N17 DF1 over the first combination only (no withholding)', '    return one({fn(list(c)) for c in itertools.product(*[sorted(x) for x in sets])})', '    return one({fn([sorted(x)[0] for x in sets])})'),
    ('N18 ec_cut median rank n // 2', '    m = sc[order[(len(ids) - 1) // 2]]', '    m = sc[order[len(ids) // 2]]'),
    ('N19 ec_cut ties to the upper half', '    out = {q: (EC_LABELS[1] if sc[i] <= m else EC_LABELS[0]) for i, q in enumerate(ids)}', '    out = {q: (EC_LABELS[1] if sc[i] < m else EC_LABELS[0]) for i, q in enumerate(ids)}'),
    ('N20 ec_cut orientation rule removed', '        if v[int(np.argmax(np.abs(v)))] < 0:\n            v = -v', '        if False:\n            v = -v'),
    ('N21 ec_cut not centred', '        xc = x - x.mean(axis=0)\n        v = np.linalg.svd', '        xc = x\n        v = np.linalg.svd'),
    ('N22 ec_cut declared-partition refusal removed', '    if any(lo == {q for q in ids if decl[q] == c} for c in cats):', '    if False:'),
    ('N23 ec_cut second principal axis', '        v = np.linalg.svd(xc, full_matrices=False)[2][0]\n        if v[', '        v = np.linalg.svd(xc, full_matrices=False)[2][1]\n        if v['),
    ('N24 EC built from the next draw', '            srcname, s = "KK_%s_n486_d%d" % (r, d), "EC_%s_n486_d%d" % (r, d)', '            srcname, s = "KK_%s_n486_d%d" % (r, d % 5 + 1), "EC_%s_n486_d%d" % (r, d)'),
    ('N25 CONFOUNDED sentence not printed', '        elif d1 == "ELONGATION-CONFOUNDED":\n            say(SENT_CONFOUNDED)', '        elif False:\n            say(SENT_CONFOUNDED)'),
    ('N26 P5 event inverted', '            e5 = bool(cw == AT)', '            e5 = bool(cw != AT)'),
    ('N27 P5 scored when the control is NOT EVALUABLE', '        if cw == NE:\n            say("P5', '        if False:\n            say("P5'),
    ('N28 DF2 caveat omitted', '    say(DF2_CAVEAT)', '    pass'),
    ('N29 C-2 disclosure counts declared > 0.0 as able (all)', '    able = sum(1 for s in ncn if res[s]["d"] >= 0.0)', '    able = len(ncn)'),
    ('N30 margin SD halved', '    sd = PKK.sd_sample(decl)\n    return bool(m > sd), m, sd', '    sd = PKK.sd_sample(decl) * 0.5\n    return bool(m > sd), m, sd'),
]


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    t0 = src.index("\nMUTANTS = [\n")
    t1 = src.index("\n]\n", t0) + 3
    head, table, tail = src[:t0], src[t0:t1], src[t1:]        # never mutate the table's own text
    if not os.path.isdir(TMP_BASE):
        refuse("the temp base %s is absent" % TMP_BASE)
    rows = []
    env = dict(os.environ, CKD_TOOLS_DIR=HERE)
    for name, old, new in MUTANTS:
        if old in head:
            mut = head.replace(old, new, 1) + table + tail
        elif old in tail:
            mut = head + table + tail.replace(old, new, 1)
        else:
            rows.append((name, "NOT APPLIED (pattern absent)"))
            continue
        d = tempfile.mkdtemp(prefix="ckdmut_", dir=TMP_BASE)
        tmp = os.path.join(d, "cert_k2_deflated_mutant.py")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(mut)
            r = subprocess.run([sys.executable, tmp, "--selftest"], capture_output=True, text=True, timeout=1800, env=env)
            rows.append((name, "KILLED" if r.returncode != 0 else "SURVIVED"))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    for n, v in rows:
        print("  %-64s %s" % (n, v))
    k = sum(1 for n, v in rows if v == "KILLED" and not n.startswith("M0 "))
    ctrl = [v for n, v in rows if n.startswith("M0 ")] == ["SURVIVED"]
    print("%s mutants: %d of %d killed; control M0 %s" % (TAG, k, len(rows) - 1, "SURVIVED (harness valid)" if ctrl else "NOT SURVIVED (harness broken)"))
    return 0 if (k == len(rows) - 1 and ctrl) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--prepare", action="store_true")
    g.add_argument("--hashes", choices=("before", "after"))
    g.add_argument("--analyze", action="store_true")
    g.add_argument("--replication", action="store_true")
    ap.add_argument("--data-root", default=os.environ.get("TAXOARENA_DATA_ROOT", ROOT))
    ap.add_argument("--cpc-labels", default=None)
    a = ap.parse_args(argv)
    cpc_labels = a.cpc_labels or os.path.join(a.data_root, CPC_LABELS_REL)
    if a.selftest:
        return selftest()
    if a.mutants:
        return mutants()
    if a.dry_run:
        dry_run(a.data_root, cpc_labels)
        return 0
    if a.prepare:
        prepare(a.data_root, cpc_labels)
        return 0
    if a.hashes:
        hashes(a.hashes, a.data_root)
        return 0
    d = os.path.join(ROOT, OUT_REL)
    if a.replication:
        agree, n = replication(d, os.path.join(a.data_root, K2_ARM_REL), os.path.join(a.data_root, KK_ARM_REL))
        return 0
    if not _IN_SELFTEST and selftest() != 0:
        refuse("the selftest is red: no readout")
    emb = os.path.join(a.data_root, "embeddings_cache.db")
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(d, SITES_NAME), cpc_labels, os.path.join(a.data_root, KK_REC_REL),
            os.path.join(a.data_root, K2_REC_REL), lambda ids: PKK.load_vectors(emb, ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
