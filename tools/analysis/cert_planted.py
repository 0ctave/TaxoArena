"""cert_planted.py: CERT-PLANTED, the planted site and vector files (TRAIN only), the dry-run, the launch command and the READOUT of
the planted two-way shift arm (SeparationNullBySizeTest `certPlanted - ...`, gradle task certPlanted). ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-04 (before any code or call) — CERT-PLANTED: is the plain J site null sensitive to a PLANTED 2-way shift of
known size (random direction, random half-split, delta x SD) at G12's depth-1 sizes, with delta = 0 as the size check? (zero calls;
site nulls, machine time under rule 7; T4)" (span L24304-L24315, commit b66b075d), AMENDED PRE-DATA in 2fc67857 (grid, CP1 /
F-CP at delta 8, P2-P4 restated, readings CPL-1..7 of record); record docs/agents/results/CERT-PLANTED.json.
  DATA. The TRAIN items of math, physics, economics on R2's B0 MMLU_PRO_LB member (draw 5a3e756 TRAIN; qwen3 512 slice; sepBar
  0.0145; mcs 55), subsampled to n 486 and n 441 (5 subsamples per cell, draw seeds 1-5, as CERT-PC-K2). PLANT: per subsample a
  random unit direction u in the 512-d slice (seed 20261004 + subsample index) and a random half-split (seed 20261104 + index);
  each half shifted by +/- delta x s x u, s = the subsample cloud's SD along u; rows renormalised to unit length. delta in
  {0, 2, 4, 6, 8, 10, 12} (amended; was {0, 0.5, 1, 2}). Labels are never used (beyond choosing the category). 3 x 2 x 7 x 5 =
  210 sites, 300 reps each.
  INSTRUMENT. The certPcK2 arm's declared-site path with the planted halves as the declared 2-way groups (the new INPUT MODE:
  the planted vectors), the plain site null of record; DEGENERATE (reached < 20 of 300) is NOT EVALUABLE.
  CERTIFIED iff k_d <= 14 of 300 (p_d = (k_d + 1) / 301 <= 0.05). CP0 (gate, n 486): SIZE-OK iff delta 0 certifies <= 1 of 15,
  else ANTI-CONSERVATIVE (CP1 then NOT EVALUABLE). CP1 (DECIDING, n 486, re-anchored at delta 8): SENSITIVE iff delta 8 certifies >= 4 of 5
  in >= 2 of the 3 categories; INSENSITIVE iff delta 8 certifies <= 1 of 5 in >= 2 of the 3; MIXED otherwise. F-CP fires iff CP1
  INSENSITIVE (at delta 8).
  DESCRIPTIVE: the power curve (certified per delta, of 15 per size), delta* per category (smallest delta with >= 4 of 5), n 441,
  the planted statistic per delta, delta* on the separation-statistic scale beside G12's 14 TOP splits (0.037-0.040).
  P1 CP0 SIZE-OK 0.85 (delta 0: 0 [0, 1] of 15). P2 (restated) certified of 15 at n 486: delta 0 0 [0, 1]; 2 0 [0, 2]; 4 1 [0, 5];
  6 7 [3, 12]; 8 14 [10, 15]; 10 15 [13, 15]; 12 15 [14, 15]. P3 (restated) CP1 SENSITIVE 0.75 / MIXED 0.15 / INSENSITIVE 0.10.
  P4 (restated) median delta* 6 [4, 8]. The pre-amendment P2 / P3 / P4 are printed beside, not scored.

INSTRUMENT AND IMPORTS. cert_pc_k2_known.py blob 981097af is IMPORTED (load_vectors, declared_stat = the routine's Python port,
TOL), and through it cert_pc_k2.py blob 38fb0dfc (assemble, build_site_bytes, read_labels, site_names, SITES_SHA256, the CPC / G /
PCS modules it pins); never copied. The Kotlin arm (additions only) reads the planted files, checks them (cplSiteError,
cplPlantCheck) and reuses cpcDeclaredSite unchanged.

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction, another
site null or a pool reader; back up the cache DBs first; run from the rp12-r2-run worktree, the data root, TAXOARENA_DATA_ROOT
unset; bring this branch's files there by PATH CHECKOUT, never a merge of the detached HEAD:
  git -C .claude/worktrees/rp12-r2-run checkout cert-planted -- tools/analysis/cert_planted.py tools/analysis/cert_pc_k2_known.py
      tools/analysis/scratch_dir.py src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt src/test/kotlin/taxonomy/CertPlantedArmTest.kt
      build.gradle.kts
  (cert_pc_k2_known.py and scratch_dir.py at main's blobs; the other imported scripts are unchanged since 8419d4ce). PRECONDITION:
  rp12-r2-run carries an UNTRACKED src/test/kotlin/taxonomy/CertK2DeflatedArmTest.kt (CERT-K2-DEFLATED, unmerged 1d282351) that
  calls dfl* members absent from SeparationNullBySizeTest.kt, so the test source set does not compile there; the operator moves it
  aside (or brings a combined SeparationNullBySizeTest.kt once both branches merge) before the arm; then there:
  python tools/analysis/cert_planted.py --selftest                     (never with python -O: refused)
  python tools/analysis/cert_planted.py --mutants
  TAXOARENA_DATA_ROOT=<main checkout> python tools/analysis/v2_union_pool.py --dry-run   (the B0-2 pool form; rc 0)
  python tools/analysis/cert_planted.py --dry-run   populations (= CERT-PC-K2's 30 subsamples, SITES_SHA256), per subsample u / half
                                       seeds, s, half sizes; the planted statistic per site (Python routine); file shas vs the pins;
                                       heap, wall, COMMAND; writes nothing
  python tools/analysis/cert_planted.py --prepare   writes experiment_results/cert_planted/planted_sites.tsv and
                                       planted_vectors.f32be (mode x), refuses unless both sha256 equal the pins
  python tools/analysis/cert_planted.py --hashes before
  <the printed COMMAND: .\\gradlew.bat certPlanted ...>   then  .\\gradlew.bat --stop
  python tools/analysis/cert_planted.py --hashes after
  python tools/analysis/cert_planted.py --analyze   outcome (write-once, mode x): experiment_results/cert_planted/outcome.txt and
        cpl_sites.csv; runs the selftest first; refuses a REFUSED / partial arm, a hash change, an IDENTITY failure, a PLANT CHECK
        other than OK, a site or vector file other than the pinned (the site file rebuilt from the CPC labels; every planted row
        rebuilt from the file's delta-0 rows and the pinned seeds), a declared statistic other than the planted rows' (Python
        routine, |diff| <= 1e-9), an instrument or snapshot other than the registered, a missing / extra / wrong-size site.
Outputs are NEVER committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_cert_planted with SHA256SUMS.txt (the two
planted files and emb_hashes_before/after.json included). Temp files only under E:/TaxoArena_tmp (scratch_dir, imported).

DRY-RUN FINDING (2026-10-04, data root rp12-r2-run; handed to the registrar, who amended the grid in 2fc67857): s along a random axis is about 0.03-0.04,
so the planted statistic (the between share, about delta^2 s^2 / total scatter) is 0.0058-0.0113 at delta 2 (median about 0.0077),
below the sepBar 0.0145, below G12's TOP splits 0.037-0.040, and far below the plain null p95 on these same populations (CERT-PC-K2's
arm: median null p95 0.067-0.070 at n 486 / 441). At the registered grid no site can plausibly certify, so CP1 would read INSENSITIVE
and F-CP fire by the grid's scale, not by the instrument; reaching the null p95 needs delta of about 6. Support (f) / (g) and P2 / P4
assumed otherwise. Built now to the amended grid; pins re-taken from a new dry-run.

BUILDER'S READINGS (of record since the amendment 2fc67857; printed in the outcome header):
  CPL-1 populations: "as CERT-PC-K2" read as CERT-PC-K2's 30 subsamples THEMSELVES (its registered draw, SITES_SHA256 efcc4e99...,
        rebuilt from the CPC labels and refused on a difference): the same ids per (category, n, draw); the family labels are
        dropped. Economics at n 486 uses 486 of its 504 items (the 5 subsamples overlap almost fully; disclosed).
  CPL-2 "subsample index" = the draw seed d (1..5) of the subsample, so u_d and the half-split seed are shared by the six cells of
        one draw (different populations, so the half-splits differ); the four deltas of one subsample share u, s and the halves
        (one power curve per subsample).
  CPL-3 u = the normalised vector of 512 draws random.Random(20261004 + d).gauss(0, 1); halves: random.Random(20261104 + d).shuffle
        of the subsample's ids sorted, the first floor(n / 2) are 'hi' (+delta), the rest 'lo' (-delta); s = the population SD
        (ddof 0) of x . u over the subsample's unit slice rows x (the cache's first 512 floats, L2-normalised: the arm's rows).
  CPL-4 site order: categories economics, math, physics; n 486 then 441; draws 1..5; deltas 0, 2, 4, 6, 8, 10, 12; names
        PL_<category>_n<n>_d<draw>_D<delta>; each site's rows sorted by id; IDENTITY first (CERT-PC-SIZE's rows) as the instrument
        precondition, its null seeded by the root id; each PL null seeded by the site name (siteNull's formula, base 20260908).
  CPL-5 NOT EVALUABLE counts (DEGENERATE, or n < 110): CP0 and CP1 print the registered word when it does not depend on how the
        NOT EVALUABLE sites would have read (the word with them counted as not certified equals the word with them counted as
        certified); otherwise NOT EVALUABLE. CP0 NOT EVALUABLE makes CP1 NOT EVALUABLE like ANTI-CONSERVATIVE.
  CPL-6 delta* = the smallest delta of {0, 2, 4, 6, 8, 10, 12} with >= 4 of 5 certified; none -> '> 12' (ranked above 12 for the
        median of P4); P4 scored at n 486; the scale conversion = the median declared statistic of that category's delta* sites at n 486.
  CPL-7 P1 binary Brier on CP0 SIZE-OK (NOT SCORED when CP0 is NOT EVALUABLE) and the delta-0 count against [0, 1]; P2 the
        counts against the restated intervals; P3 three-way Brier sum (NOT SCORED when CP1 is NOT EVALUABLE).

SELFTEST (python tools/analysis/cert_planted.py --selftest): every registered branch through the real entry points (analyze(),
main(["--analyze"]), build(), plant_rows(), direction(), halves(), vectors_from_db()) on fixtures whose answer is known by hand,
asserting the printed VALUE; the case list is in selftest(). MUTANTS: --mutants runs the table MUTANTS below against --selftest
(copies under the scratch dir on E:, removed by scratch_dir at exit); the result table is in the commit message.
"""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import random
import sqlite3
import subprocess
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from fractions import Fraction

import numpy as np

HERE = os.environ.get("CPL_SRC_DIR") or os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro as RO  # noqa: E402

TAG = "[CPL]"
_IN_SELFTEST = False
PKK_BLOB = "981097afa244f7eeb8cc794396060e9ec437d605"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    got = RO.git_blob_lf(os.path.join(HERE, name + ".py"))
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


PKK = _import_pinned("cert_pc_k2_known", PKK_BLOB)
PK2 = PKK.PK2
PCS, CPC, G = PK2.PCS, PK2.CPC, PK2.G

OUT_REL = "experiment_results/cert_planted"
CPC_LABELS_REL = PK2.CPC_LABELS_REL
SITES_NAME, VEC_NAME, ARM_NAME, OUTCOME_NAME, CSV_NAME = ("planted_sites.tsv", "planted_vectors.f32be", "arm", "outcome.txt",
                                                          "cpl_sites.csv")
SITE_HEADER = PCS.SITE_HEADER
SNAPSHOT, ROOT_ID, N_ROOT = PK2.SNAPSHOT, PK2.ROOT_ID, PK2.N_ROOT
ANCHORS = ("economics", "math", "physics")
SIZES = (486, 441)
DECIDING_N = 486
DRAWS = (1, 2, 3, 4, 5)
DELTAS = ("0", "2", "4", "6", "8", "10", "12")
DELTA_DEC = "8"                 # CP1 / F-CP (amended 2fc67857; was delta 2)
NONE_WORD = "> 12"              # delta* when no delta of the grid certifies >= 4 of 5 (CPL-6)
U_SEED0, H_SEED0 = 20261004, 20261104
SLICE = 512
REPS, MCS, DEGENERATE_MIN = 300, 55, 20
BAR = Fraction(1, 20)
TOL = PKK.TOL                   # Python vs Kotlin statistic (float64, different summation order)
PLANT_TOL = 1e-6                # a planted row rebuilt from the delta-0 rows vs the file's (float32 rendering)
IDENTITY_DECLARED, IDENTITY_K = PK2.IDENTITY_DECLARED, PK2.IDENTITY_K
PC1_P95, PC1_MAX = PK2.PC1_P95, PK2.PC1_MAX
INSTRUMENT = {"arm": "certPlanted", "reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false",
              "minClusterSize": "55", "plant_check": "OK"}
G12_TOP = ("0.037", "0.040")    # the registration: G12's 14 TOP splits on math / physics / economics (CERT-PC-K2 W-4)
P1_P = 0.85
P1_BAND = (0, 1)
P2_REG = {"0": (0, 0, 1), "2": (0, 0, 2), "4": (1, 0, 5), "6": (7, 3, 12), "8": (14, 10, 15), "10": (15, 13, 15),
          "12": (15, 14, 15)}      # restated (2fc67857): (point, lo, hi)
P3_PROBS = {"SENSITIVE": 0.75, "MIXED": 0.15, "INSENSITIVE": 0.10}
P4_REG = (6.0, 4.0, 8.0)
PRE_AMENDMENT = ("PRE-AMENDMENT PREDICTIONS (printed beside, NOT scored; 2fc67857): P2 delta 0.5 1 [0, 4], delta 1 6 [2, 12], delta 2 "
                 "15 [12, 15]; P3 SENSITIVE 0.70 / MIXED 0.15 / INSENSITIVE 0.15; P4 median delta* 1 [0.5, 2]")
PK2_WALL_S = 1503               # CERT-PC-K2's arm: IDENTITY + 30 sites x (plain + deflated + C0), 12 threads
# The planted files of record (amended grid, 2fc67857), pinned from the dry-run of 2026-10-04 (data root
# .claude/worktrees/rp12-r2-run, read-only; 211 sites / 104,328 rows; 97,335 rows x 512 float32 = 199,342,080 bytes); the pre-amendment
# pins 93f64aa5... / 435701b2... are superseded. None = NOT PINNED (--prepare / --analyze refuse).
SITES_SHA256 = "14c626d51fea40e9ec6392be2e01d4dc45d445d5c659264e2e41716b0be3aa4f"
VECTORS_SHA256 = "2135279ee9ea5c9d45e54a555fd63f574507a15a1f162e323470de03c3e447df"
REG = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CERT-PLANTED: ..." L24304-L24315 '
       '(as registered, b66b075d; amended pre-data 2fc67857)')

SENT_FCP_FIRED = ("F-CP: FIRED (CP1 INSENSITIVE): the plain site null is insensitive to strong 2-way structure at depth-1 sizes, so "
                  "G12's 0 of 60 is uninformative about 2-way structure.")
LIKE = ["LIKE WITH LIKE: | control | k | partition | known strength |",
        "  | CERT-PLANTED (this) | 2 | random half-split on a random axis | planted delta |",
        "  | CERT-PC-K2 | 2 | declared source family | unknown (failed) |",
        "  | CERT-PC-K2-KNOWN | 2 | declared merged categories | gate failed |",
        "  | CERT-K2-DEFLATED | 2 | declared, deflated null | elongation-confounded |",
        "  | G12 TOP | 2-3 | data-driven | unknown |"]
DOES_NOT_SHOW = ("DOES NOT SHOW: that declared sub-structure is or is not geometric; a certificate of any tree site; other members, "
                 "draws, slices or k; a mode test (MIX-LRT-SITE closed)")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def pop_name(a, n, d):
    return "PL_%s_n%d_d%d" % (a, n, d)


def site_name(a, n, d, dl):
    return "%s_D%s" % (pop_name(a, n, d), dl)


def site_names():
    return [site_name(a, n, d, dl) for a in ANCHORS for n in SIZES for d in DRAWS for dl in DELTAS]


def parse_name(s):
    _pl, a, n, d, dl = s.split("_")
    return a, int(n[1:]), int(d[1:]), dl[1:]


# ------------------------------------------------------------------------------------------------ the plant (CPL-2, CPL-3)
def direction(d, dim=SLICE):
    """u_d: the normalised vector of dim draws random.Random(U_SEED0 + d).gauss(0, 1)."""
    rng = random.Random(U_SEED0 + d)
    g = np.array([rng.gauss(0.0, 1.0) for _ in range(dim)], dtype=np.float64)
    return g / math.sqrt(float(g @ g))


def halves(ids, d):
    """{id: 'hi' | 'lo'}: random.Random(H_SEED0 + d).shuffle of the ids sorted; the first floor(n / 2) are 'hi'."""
    perm = sorted(ids)
    random.Random(H_SEED0 + d).shuffle(perm)
    hi = set(perm[:len(perm) // 2])
    return {q: ("hi" if q in hi else "lo") for q in sorted(ids)}


def unit(x):
    x = np.asarray(x, dtype=np.float64)
    nrm = np.sqrt((x * x).sum(axis=1))
    if bool((nrm <= 0.0).any()):
        refuse("a planted row has zero norm")
    return x / nrm[:, None]


def plant_rows(X, hi_mask, u, delta):
    """X (n, dim) unit rows; hi_mask (n,) bool; -> (unit(X + sign x delta x s x u), s), s = SD (ddof 0) of X . u."""
    X = np.asarray(X, dtype=np.float64)
    p = X @ u
    s = float(np.sqrt(((p - p.mean()) ** 2).mean()))
    sign = np.where(np.asarray(hi_mask, dtype=bool), 1.0, -1.0)
    return unit(X + (sign * float(delta) * s)[:, None] * u[None, :]), s


def build(cat, k2_sites, vec):
    """cat: {id: category} over the root (IDENTITY); k2_sites: {K2 site name: sorted ids} (CERT-PC-K2's 30); vec: {id: unit row}.
    -> (site bytes, vector bytes, meta {population: dict(d, s, n_hi, n_lo)}, planted {site: (ids, labels, rows float32)})."""
    rows = [SITE_HEADER] + ["IDENTITY\t%s\t%s" % (q, cat[q]) for q in sorted(cat)]
    chunks, meta, planted = [], {}, {}
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                k2 = "K2_%s_n%d_d%d" % (a, n, d)
                if k2 not in k2_sites:
                    refuse("CERT-PC-K2's site %s is missing" % k2)
                ids = sorted(k2_sites[k2])
                if len(ids) != n:
                    refuse("%s holds %d ids, not %d" % (k2, len(ids), n))
                lab = halves(ids, d)
                hi_mask = [lab[q] == "hi" for q in ids]
                X = np.array([vec[q] for q in ids], dtype=np.float64)
                u = direction(d)
                pn = pop_name(a, n, d)
                for dl in DELTAS:
                    Y, s = plant_rows(X, hi_mask, u, dl)
                    sn = site_name(a, n, d, dl)
                    rows.extend("%s\t%s\t%s" % (sn, q, lab[q]) for q in ids)
                    y32 = Y.astype(np.float32)
                    chunks.append(y32.astype(">f4").tobytes())
                    planted[sn] = (ids, lab, y32)
                meta[pn] = dict(d=d, s=s, n_hi=sum(hi_mask), n_lo=n - sum(hi_mask))
    return ("\n".join(rows) + "\n").encode("utf-8"), b"".join(chunks), meta, planted


def stat_of(ids, lab, y32):
    """The declared statistic of a planted site as the arm computes it: projectTo(512) of the float rows, groups hi then lo."""
    U = PKK.unit_rows(y32)
    return PKK.declared_stat([U[[i for i, q in enumerate(ids) if lab[q] == c]] for c in ("hi", "lo")])


# ------------------------------------------------------------------------------------------------ data root: assemble / dry-run
def vectors_from_db(db_path, ids):
    """{id: unit 512 row} (PKK.load_vectors: the cache's first 512 big-endian floats, L2-normalised)."""
    return PKK.load_vectors(db_path, ids)


def assemble(data_root, cpc_labels):
    cfg, sid, root, cat, src, data, sites, labels, pops = PK2.assemble(data_root, cpc_labels)
    if sha256_bytes(data) != PK2.SITES_SHA256:
        refuse("CERT-PC-K2's site file rebuilds to sha256 %s, not its registered draw %s" % (sha256_bytes(data), PK2.SITES_SHA256))
    k2 = {s: sites[s] for s in PK2.site_names()}
    ids = sorted(set().union(*[set(v) for v in k2.values()]))
    vec = vectors_from_db(os.path.join(data_root, "embeddings_cache.db"), ids)
    sdata, vdata, meta, planted = build(cat, k2, vec)
    return cfg, sid, root, cat, k2, sdata, vdata, meta, planted


def command(cfg, heap):
    return ('.\\gradlew.bat certPlanted --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DsiteLabels=%s/%s" '
            '"-DplantedVectors=%s/%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], SNAPSHOT, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, SITES_NAME, OUT_REL, VEC_NAME, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def pin_word(got, pin):
    return "NOT PINNED (pin it from this dry-run)" if pin is None else ("= the pin" if got == pin else "NOT the pin %s" % pin)


def dry_run(data_root, cpc_labels, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table (TRAIN only)")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no verdict" % TAG)
    CPC.heavy_check()
    cfg, sid, root, cat, k2, sdata, vdata, meta, planted = assemble(data_root, cpc_labels)
    out("%s member B0/mmlu_pro_lb = snapshot %s; root %s '%s' n = %d (TRAIN); CERT-PC-K2's 30 subsamples rebuilt (sha256 %s = its "
        "SITES_SHA256; CPL-1)" % (TAG, sid, root["id"], root.get("label"), len(cat), PK2.SITES_SHA256[:16]))
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                m = meta[pop_name(a, n, d)]
                st = ["D%s %.6f" % (dl, stat_of(*planted[site_name(a, n, d, dl)])) for dl in DELTAS]
                out("%s %-18s u seed %d, half seed %d: hi %d / lo %d; s = %.6f; planted statistic %s" % (
                    TAG, pop_name(a, n, d), U_SEED0 + d, H_SEED0 + d, m["n_hi"], m["n_lo"], m["s"], ", ".join(st)))
    for ln in PK2.overlap_lines(k2, PK2.populations(*PK2.read_labels(cpc_labels))):
        out("%s %s (CERT-PC-K2's subsamples = these populations; CPL-1)" % (TAG, ln))
    ss, vs = sha256_bytes(sdata), sha256_bytes(vdata)
    out("%s site file %s/%s: %d sites, %d rows, sha256 %s (%s)" % (TAG, OUT_REL, SITES_NAME, 1 + len(site_names()),
                                                                  sdata.count(b"\n") - 1, ss, pin_word(ss, SITES_SHA256)))
    out("%s vector file %s/%s: %d bytes (%d rows x %d float32 big-endian), sha256 %s (%s)" % (
        TAG, OUT_REL, VEC_NAME, len(vdata), len(vdata) // (4 * SLICE), SLICE, vs, pin_word(vs, VECTORS_SHA256)))
    need, live, heap = G.heap_estimate(N_ROOT, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule, the IDENTITY site n %d): live %d, peak %.2f GB -> %s; plus the vector file %.0f MB twice" % (
        TAG, N_ROOT, live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap, len(vdata) / 1e6))
    out("%s wall: about %.0f min at %d threads (bound: CERT-PC-K2's arm took %d s for IDENTITY + 30 sites x 2 null arms; this arm runs "
        "IDENTITY + 210 plain null arms at n 441-486; budget the window at about 100-120 min)"
        % (TAG, 3.5 * PK2_WALL_S / 60.0, cfg["jvmThreads"], PK2_WALL_S))
    if os.path.exists(os.path.join(ROOT, OUT_REL, ARM_NAME)):
        refuse("%s/%s exists: the arm writes it once" % (OUT_REL, ARM_NAME))
    same = CPC.same_checkout(data_root)
    out("%s LAUNCH FROM %s%s" % (TAG, os.path.abspath(data_root), "" if same else
        " (the data root is NOT this checkout: this dry-run is a preview; path-checkout the branch's files there and run from there)"))
    out("%s COMMAND: %s" % (TAG, command(cfg, heap)))
    out("%s after the arm: .\\gradlew.bat --stop" % TAG)
    return dict(sites_sha=ss, vec_sha=vs, heap=heap)


def prepare(data_root, cpc_labels):
    if not CPC.same_checkout(data_root):
        refuse("--prepare writes the planted files into this checkout; the arm reads them from the data root's: run from %s" % data_root)
    if SITES_SHA256 is None or VECTORS_SHA256 is None:
        refuse("the planted files are NOT PINNED (SITES_SHA256 / VECTORS_SHA256): pin them from a dry-run first")
    CPC.heavy_check()
    _c, _s, _r, _cat, _k2, sdata, vdata, _m, _p = assemble(data_root, cpc_labels)
    if sha256_bytes(sdata) != SITES_SHA256 or sha256_bytes(vdata) != VECTORS_SHA256:
        refuse("the planted files' sha256 %s / %s are not the pins %s / %s" % (sha256_bytes(sdata), sha256_bytes(vdata), SITES_SHA256,
                                                                             VECTORS_SHA256))
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    for name, b in ((SITES_NAME, sdata), (VEC_NAME, vdata)):
        with open(os.path.join(d, name), "xb") as f:
            f.write(b)
        print("%s wrote %s/%s (%d bytes, sha256 %s)" % (TAG, OUT_REL, name, len(b), sha256_bytes(b)))


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


# ------------------------------------------------------------------------------------------------ the readout
def subsample_status(n, k, reached):
    if n < 2 * MCS:
        return "NOT EVALUABLE (NULL-INFEASIBLE)"
    if reached < DEGENERATE_MIN:
        return "NOT EVALUABLE (DEGENERATE)"
    return "CERTIFIED" if bool(CPC.p_of(k) <= BAR) else "NOT CERTIFIED"


def cp0_word(c):
    return "SIZE-OK" if c <= 1 else "ANTI-CONSERVATIVE"


def cp0_verdict(c, e):
    """CP0 from the delta-0 certified count c and NOT EVALUABLE count e (CPL-5)."""
    lo, hi = cp0_word(c), cp0_word(c + e)
    return lo if lo == hi else "NOT EVALUABLE"


def cp1_word(counts):
    if sum(1 for c in counts if c >= 4) >= 2:
        return "SENSITIVE"
    if sum(1 for c in counts if c <= 1) >= 2:
        return "INSENSITIVE"
    return "MIXED"


def cp1_verdict(cp0, ce):
    """CP1 from CP0 and [(certified, NOT EVALUABLE)] per category at DELTA_DEC (8), n 486 (CPL-5)."""
    if cp0 != "SIZE-OK":
        return "NOT EVALUABLE"
    lo, hi = cp1_word([c for c, _e in ce]), cp1_word([c + e for c, e in ce])
    return lo if lo == hi else "NOT EVALUABLE"


def delta_star(cert_by_delta):
    """{delta: certified of 5} -> the smallest delta with >= 4 (CPL-6), or None."""
    for dl in DELTAS:
        if cert_by_delta[dl] >= 4:
            return dl
    return None


def median_rank(xs):
    """Median of 3 delta* values (None ranked above 12) -> the middle value (None = '> 12')."""
    key = sorted(xs, key=lambda v: float("inf") if v is None else float(v))
    return key[len(key) // 2]


def median(xs):
    s = sorted(xs)
    return s[len(s) // 2]


def read_planted(sites_path, vec_path):
    """The planted files as any reader takes them (this readout; SI-NULL-TRIAD's POWER grid reuses them byte for byte):
    -> (sfile {site: {id: label}} in file order, {PL site: (sorted ids, (n, 512) float32 rows)}, site bytes, vector bytes).
    Refuses a site list other than IDENTITY + the 210 PL sites in order, a site whose rows are not sorted by id, or a vector file
    whose size is not rows x 512 x 4. Pins are the CALLER's (SITES_SHA256 / VECTORS_SHA256)."""
    sbytes = open(sites_path, "rb").read()
    sfile = PCS.parse_site_file(sites_path)
    if list(sfile) != ["IDENTITY"] + site_names():
        refuse("the site file lists %s, not IDENTITY + the 210 registered PL sites in order" % list(sfile)[:6])
    n_rows = sum(len(sfile[s]) for s in site_names())
    vbytes = open(vec_path, "rb").read()
    if len(vbytes) != n_rows * SLICE * 4:
        refuse("the vector file holds %d bytes, not %d rows x %d x 4" % (len(vbytes), n_rows, SLICE))
    V = np.frombuffer(vbytes, dtype=">f4").reshape(n_rows, SLICE).astype(np.float32)
    rows_by_site, off = {}, 0
    for s in site_names():
        ids = sorted(sfile[s])
        if list(sfile[s]) != ids:
            refuse("site %s's rows are not sorted by id" % s)
        rows_by_site[s] = (ids, V[off:off + len(ids)])
        off += len(ids)
    return sfile, rows_by_site, sbytes, vbytes


def analyze(arm_dir, out_dir, sites_path, vec_path, labels_path, out=print):
    outcome_p, csv_p = os.path.join(out_dir, OUTCOME_NAME), os.path.join(out_dir, CSV_NAME)
    for p in (outcome_p, csv_p):
        if os.path.exists(p):
            refuse("%s exists: the outcome is write-once" % p)
    L = []

    def say(s):
        L.append(s)
        out(s)

    say("pool: none (no DB opened; TRAIN-only planted files)")
    if SITES_SHA256 is None or VECTORS_SHA256 is None:
        refuse("the planted files are NOT PINNED (SITES_SHA256 / VECTORS_SHA256): no readout")
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
    sfile, rows_by_site, sbytes, vbytes = read_planted(sites_path, vec_path)
    want = ["IDENTITY"] + site_names()
    s_sha = sha256_bytes(sbytes)
    if st.get("sites_sha256") != s_sha:
        refuse("the arm read site file sha256 %s; %s is %s" % (st.get("sites_sha256"), sites_path, s_sha))
    if s_sha != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s (the registered plant)" % (s_sha, SITES_SHA256))
    v_sha = sha256_bytes(vbytes)
    if st.get("vectors_sha256") != v_sha:
        refuse("the arm read vector file sha256 %s; %s is %s" % (st.get("vectors_sha256"), vec_path, v_sha))
    if v_sha != VECTORS_SHA256:
        refuse("the vector file's sha256 %s is not VECTORS_SHA256 %s (the registered plant)" % (v_sha, VECTORS_SHA256))
    cat, src = PK2.read_labels(labels_path)
    k2data, k2sites, _kl, _kp = PK2.build_site_bytes(cat, src)
    if sha256_bytes(k2data) != PK2.SITES_SHA256:
        refuse("CERT-PC-K2's draw rebuilt from the CPC labels is sha256 %s, not its SITES_SHA256" % sha256_bytes(k2data))
    # the site file rebuilt from the labels (ids, halves, order); vectors are checked below from the file's own delta-0 rows
    rebuilt_rows = [SITE_HEADER] + ["IDENTITY\t%s\t%s" % (q, cat[q]) for q in sorted(cat)]
    for s in site_names():
        a, n, d, dl = parse_name(s)
        ids = sorted(k2sites["K2_%s_n%d_d%d" % (a, n, d)])
        lab = halves(ids, d)
        rebuilt_rows.extend("%s\t%s\t%s" % (s, q, lab[q]) for q in ids)
    if ("\n".join(rebuilt_rows) + "\n").encode("utf-8") != sbytes:
        refuse("the site file is not the registered plant rebuilt from the CPC labels (CERT-PC-K2's draw, the half seeds)")
    worst, s_of = 0.0, {}
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                ids, X0 = rows_by_site[site_name(a, n, d, "0")]
                lab = sfile[site_name(a, n, d, "0")]
                hi_mask = [lab[q] == "hi" for q in ids]
                X = unit(X0)
                for dl in DELTAS:
                    Y, s = plant_rows(X, hi_mask, direction(d), dl)
                    diff = float(np.abs(Y.astype(np.float32) - rows_by_site[site_name(a, n, d, dl)][1]).max())
                    worst = max(worst, diff)
                    if not diff <= PLANT_TOL:
                        refuse("%s: the planted rows are not the delta-0 rows planted with u seed %d / s %.6f / delta %s (max |diff| %.3e)"
                               % (site_name(a, n, d, dl), U_SEED0 + d, s, dl, diff))
                s_of[pop_name(a, n, d)] = s
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    say("%s CERT-PLANTED outcome (tools/analysis/cert_planted.py blob %s; cert_pc_k2_known.py blob %s and cert_pc_k2.py blob %s "
        "imported). Zero calls." % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), PKK_BLOB, PKK.PK2_BLOB))
    say("registration: " + REG)
    say("arm: %s; snapshot %s; site file sha256 %s (= SITES_SHA256; rebuilt from the CPC labels: byte-identical); vector file sha256 "
        "%s (= VECTORS_SHA256; every planted row rebuilt from the file's delta-0 rows and the pinned seeds, max |diff| %.3e <= %.0e); "
        "PLANT CHECK %s (delta-0 rows vs the cache: %s sites, max |diff| %s); reps %s; sliceDim %s; sepBar %s; dropTop %s; whiten %s; "
        "minClusterSize %s; threads %s; embeddings_cache.db per-table hashes before == after" % (
            st["arm"], st["snapshot"], s_sha, v_sha, worst, PLANT_TOL, st["plant_check"], st.get("d0_sites"), st.get("d0_max_abs_diff"),
            st["reps"], st["sliceDim"], st["sepBar"], st["dropTop"], st["whiten"], st["minClusterSize"], st.get("threads")))
    say("builder's readings CPL-1..CPL-7 (docstring) to the registrar")

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        rows = {r["site_id"]: r for r in csv.DictReader(f)}
    if list(rows) != want:
        refuse("sites.csv holds %s, not IDENTITY + the 210 registered PL sites in order" % list(rows)[:6])
    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reps.setdefault((r["site_id"], r["arm"]), []).append((int(r["rep"]), float(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    R = {k: [x for _i, x in v] for k, v in reps.items()}
    for s in want:
        if (s, "SN") not in R:
            refuse("replicates: %s's SN arm is missing" % s)

    ir = rows["IDENTITY"]
    d0 = float(ir["declared_stat"])
    k0 = CPC.kcount(R[("IDENTITY", "SN")], d0)
    sn0 = sorted(R[("IDENTITY", "SN")])
    p95_0, max_0 = "%.6f" % CPC.pctl(sn0, 0.95), "%.6f" % sn0[-1]
    say("IDENTITY: full-size root n %s, declared %.6f (registered %s), k_d %d of %d (registered %d); null seeded by %s; null p95 "
        "%s / max %s (PC1 of record %s / %s)" % (ir["n"], d0, IDENTITY_DECLARED, k0, REPS, IDENTITY_K, ir["null_seed_id"],
                                                  p95_0, max_0, PC1_P95, PC1_MAX))
    if not ("%.6f" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K and int(ir["n"]) == N_ROOT and ir["null_seed_id"] == ROOT_ID
            and p95_0 == PC1_P95 and max_0 == PC1_MAX):
        refuse("IDENTITY FAILED: declared %.6f k_d %d n %s seed %s p95 %s max %s (want %s, %d, %d, %s, %s, %s); no readout"
               % (d0, k0, ir["n"], ir["null_seed_id"], p95_0, max_0, IDENTITY_DECLARED, IDENTITY_K, N_ROOT, ROOT_ID, PC1_P95, PC1_MAX))
    say("IDENTITY: REPRODUCED (precondition held; null p95 / max equal PC1's)")

    se = math.sqrt(0.05 * 0.95 / REPS)
    say("SUPPORT (a) %d null replicates per site; deciding units: 5 subsamples per category at delta 8, n 486 (15 sites), the CP0 gate "
        "15 sites at delta 0, n 486; (b) DEFF 1.0 BY CONSTRUCTION (exceedance counts of independently seeded replicates; a tree-arm "
        "DEFF does not apply); (c) n_eff %d per site; (d) SE at the bar sqrt(0.05 x 0.95 / %d) = %.4f; (e) MDE80 = 2.8 x SE = %.4f "
        "per site; (f) floor 1/301 = %.4f; NULL-INFEASIBLE below n %d, DEGENERATE below %d reached replicates" % (
            REPS, REPS, REPS, se, 2.8 * se, 1 / 301.0, 2 * MCS, DEGENERATE_MIN))
    say("SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered bootstrap "
        "are N/A to a null exceedance count; the 5 draws of a category and the 4 deltas of a subsample are NOT independent "
        "(shared ids; shared u, s and halves)")
    for ln in LIKE:
        say(ln)

    res, out_rows = {}, []
    for s in site_names():
        a, n_reg, d, dl = parse_name(s)
        r = rows[s]
        n = int(r["n"])
        ids, Y = rows_by_site[s]
        lab = sfile[s]
        gs = "%d/%d" % (sum(1 for v in lab.values() if v == "hi"), sum(1 for v in lab.values() if v == "lo"))
        if n != len(ids) or n != n_reg or int(r["groups"]) != 2 or r["group_sizes"] != gs:
            refuse("sites.csv: %s n %s groups %s sizes %s (the site file holds %d, halves hi/lo %s; want n %d, 2 groups)"
                   % (s, r["n"], r["groups"], r["group_sizes"], len(ids), gs, n_reg))
        dk = float(r["declared_stat"])
        dp = stat_of(ids, lab, Y)
        if not abs(dp - dk) <= TOL:
            refuse("%s: the arm's declared statistic %.17g is not the planted rows' %.17g (|diff| %.2e > %.0e)" % (s, dk, dp, abs(dp - dk), TOL))
        sn = sorted(R[(s, "SN")])
        k = CPC.kcount(R[(s, "SN")], dk)
        if k != int(r["k_declared"]):
            refuse("%s: k_d recount %d != the arm's %s" % (s, k, r["k_declared"]))
        reached = sum(1 for x in R[(s, "SN")] if x > 0.0)
        if reached != int(r["reached"]):
            refuse("%s: reached recount %d != the arm's %s" % (s, reached, r["reached"]))
        np95 = CPC.pctl(sn, 0.95)
        status = subsample_status(n, k, reached)
        res[s] = dict(a=a, n=n, d=d, dl=dl, stat=dk, k=k, np95=np95, reached=reached, status=status)
        say("  %-24s n %3d (hi/lo %s): planted statistic %.6f; null p50 %.6f / p95 %.6f / max %.6f; k_d %3d of %d, p_d %d/301 = "
            "%.6f; reached %d -> %s" % (s, n, gs, dk, CPC.pctl(sn, 0.50), np95, sn[-1], k, REPS, k + 1, float(CPC.p_of(k)), reached,
                                        status))
        out_rows.append([s, a, n, d, dl, gs, "%.6f" % s_of[pop_name(a, n, d)], "%.6f" % dk, k, "%d/301" % (k + 1), "%.6f" % np95,
                         reached, status])

    def counts(a, n, dl):
        sts = [res[site_name(a, n, dd, dl)]["status"] for dd in DRAWS]
        return sum(1 for x in sts if x == "CERTIFIED"), sum(1 for x in sts if x.startswith("NOT EVALUABLE"))

    cnt = {(a, n, dl): counts(a, n, dl) for a in ANCHORS for n in SIZES for dl in DELTAS}
    for n in SIZES:
        for a in ANCHORS:
            say("CELL %s n %d: certified of 5 by delta %s; NOT EVALUABLE %s; median planted statistic %s; median null p95 %s" % (
                a, n, ", ".join("%s: %d" % (dl, cnt[(a, n, dl)][0]) for dl in DELTAS),
                ", ".join("%s: %d" % (dl, cnt[(a, n, dl)][1]) for dl in DELTAS),
                ", ".join("%s: %.6f" % (dl, median([res[site_name(a, n, dd, dl)]["stat"] for dd in DRAWS])) for dl in DELTAS),
                ", ".join("%s: %.6f" % (dl, median([res[site_name(a, n, dd, dl)]["np95"] for dd in DRAWS])) for dl in DELTAS)))
    for n in SIZES:
        say("POWER CURVE n %d (certified of 15 per delta; NOT EVALUABLE beside): %s" % (n, "; ".join(
            "delta %s: %d of 15 (%.2f), NE %d" % (dl, sum(cnt[(a, n, dl)][0] for a in ANCHORS),
                                                  sum(cnt[(a, n, dl)][0] for a in ANCHORS) / 15.0,
                                                  sum(cnt[(a, n, dl)][1] for a in ANCHORS)) for dl in DELTAS)))

    c0 = sum(cnt[(a, DECIDING_N, "0")][0] for a in ANCHORS)
    e0 = sum(cnt[(a, DECIDING_N, "0")][1] for a in ANCHORS)
    cp0 = cp0_verdict(c0, e0)
    say("CP0 (gate, n 486, delta 0): %s; certified %d of 15, NOT EVALUABLE %d (SIZE-OK iff <= 1 of 15; CPL-5)" % (cp0, c0, e0))
    ce = [cnt[(a, DECIDING_N, DELTA_DEC)] for a in ANCHORS]
    cp1 = cp1_verdict(cp0, ce)
    say("CP1 (DECIDING, n 486, delta 8): %s; certified of 5 per category %s; NOT EVALUABLE %s%s" % (
        cp1, ", ".join("%s %d" % (a, c) for a, (c, _e) in zip(ANCHORS, ce)), ", ".join("%s %d" % (a, e) for a, (_c, e) in zip(ANCHORS, ce)),
        " (CP0 %s: CP1 NOT EVALUABLE)" % cp0 if cp0 != "SIZE-OK" else ""))

    dstar = {}
    for n in SIZES:
        for a in ANCHORS:
            dstar[(a, n)] = delta_star({dl: cnt[(a, n, dl)][0] for dl in DELTAS})
        say("DELTA* n %d (smallest delta with >= 4 of 5 certified; CPL-6): %s" % (
            n, ", ".join("%s %s" % (a, NONE_WORD if dstar[(a, n)] is None else dstar[(a, n)]) for a in ANCHORS)))
    scale = {}
    for a in ANCHORS:
        ds = dstar[(a, DECIDING_N)]
        if ds is not None:
            scale[a] = median([res[site_name(a, DECIDING_N, dd, ds)]["stat"] for dd in DRAWS])
    say("SCALE (n 486): delta* on the separation-statistic scale (median planted statistic of the delta* sites): %s; G12's 14 TOP "
        "splits %s-%s (registered)" % (", ".join("%s %s" % (a, ("%.6f" % scale[a]) if a in scale else "n/a (delta* > 12)") for a in ANCHORS),
                                        G12_TOP[0], G12_TOP[1]))

    if cp1 == "INSENSITIVE":
        say(SENT_FCP_FIRED)
    else:
        say("F-CP: NOT FIRED (CP1 %s)." % cp1)
        if cp1 == "SENSITIVE":
            say("READING (CP1 SENSITIVE): G12's 0 of 60 reads 'the tree's depth-1 splits are weaker than a planted shift of delta* at "
                "these sizes' (delta* at n 486: %s; on the statistic scale %s; G12 TOP %s-%s)." % (
                    ", ".join("%s %s" % (a, NONE_WORD if dstar[(a, DECIDING_N)] is None else dstar[(a, DECIDING_N)]) for a in ANCHORS),
                    ", ".join("%s %s" % (a, ("%.6f" % scale[a]) if a in scale else "n/a") for a in ANCHORS), G12_TOP[0], G12_TOP[1]))
        else:
            say("READING: none (CP1 %s: %s; no sentence)" % (cp1, "a registered MIXED" if cp1 == "MIXED" else
                                                            "not evaluable (CP0 %s; CPL-5)" % cp0))

    if cp0 != "NOT EVALUABLE":
        e1 = bool(cp0 == "SIZE-OK")
        say("P1 CP0 SIZE-OK (p %.2f): event %s (%s), Brier %.4f; delta-0 count %d of 15 against [%d, %d]: %s" % (
            P1_P, "yes" if e1 else "no", cp0, (P1_P - (1.0 if e1 else 0.0)) ** 2, c0, P1_BAND[0], P1_BAND[1],
            "inside" if P1_BAND[0] <= c0 <= P1_BAND[1] else "OUTSIDE"))
    else:
        say("P1 CP0 SIZE-OK (p %.2f): NOT SCORED (CP0 NOT EVALUABLE; CPL-7); delta-0 count %d of 15 against [%d, %d]: %s" % (
            P1_P, c0, P1_BAND[0], P1_BAND[1], "inside" if P1_BAND[0] <= c0 <= P1_BAND[1] else "OUTSIDE"))
    for dl in DELTAS:
        c = sum(cnt[(a, DECIDING_N, dl)][0] for a in ANCHORS)
        pt, lo, hi = P2_REG[dl]
        say("P2 delta %s at n 486: certified %d of 15 (predicted %d [%d, %d]): %s, |count - point| %d" % (
            dl, c, pt, lo, hi, "inside" if lo <= c <= hi else "OUTSIDE", abs(c - pt)))
    if cp1 in P3_PROBS:
        b3 = sum((p - (1.0 if v == cp1 else 0.0)) ** 2 for v, p in P3_PROBS.items())
        say("P3 CP1 readings (SENSITIVE 0.75, MIXED 0.15, INSENSITIVE 0.10): outcome %s, Brier (3-way sum) %.4f" % (cp1, b3))
    else:
        say("P3 CP1 readings: NOT SCORED (CP1 NOT EVALUABLE; CPL-7)")
    mds = median_rank([dstar[(a, DECIDING_N)] for a in ANCHORS])
    in4 = mds is not None and P4_REG[1] <= float(mds) <= P4_REG[2]
    say("P4 median delta* at n 486 (predicted %g [%g, %g]): %s: %s" % (P4_REG[0], P4_REG[1], P4_REG[2], NONE_WORD if mds is None else mds,
                                                                   "inside" if in4 else "OUTSIDE"))
    say(PRE_AMENDMENT)
    say(DOES_NOT_SHOW)

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "category", "n", "draw", "delta", "hi_lo", "s", "planted_stat", "k_d", "p_d", "null_p95", "reached", "status"])
        w.writerows(out_rows)
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, csv_p))
    return dict(cp0=cp0, cp1=cp1, fired=bool(cp1 == "INSENSITIVE"), dstar=dstar, res=res, cnt=cnt, lines=L)


# ------------------------------------------------------------------------------------------------ selftest
_FX_CACHE = {}


def _fx_build():
    """The labels fixture of CERT-PC-K2 (6,993 ids), random 512-d vectors for the anchor ids (seed 7), built by build()."""
    if "b" not in _FX_CACHE:
        cat, src = PK2._labels_fixture()
        data, sites, _l, _p = PK2.build_site_bytes(cat, src)
        k2 = {s: sites[s] for s in PK2.site_names()}
        ids = sorted(set().union(*[set(v) for v in k2.values()]))
        rng = np.random.default_rng(7)
        raw = rng.standard_normal((len(ids), SLICE)).astype(np.float32) + np.float32(0.3)
        U = PKK.unit_rows(raw)
        vec = {q: U[i] for i, q in enumerate(ids)}
        _FX_CACHE["b"] = (cat, src, data, k2, vec, build(cat, k2, vec))
    return _FX_CACHE["b"]


def _sn_default(d, k, sc=1e-4):
    """300 replicates with exactly k >= d (the first of them == d: a tie); below d: inside (0, d) when d > 0 (all reached),
    else d - j x sc (none reached: a d <= 0 site that certifies is DEGENERATE by construction)."""
    nb = 300 - k
    below = [d * (j + 1) / (nb + 1) for j in range(nb)] if d > 0 else [d - (nb - j) * sc for j in range(nb)]
    return below + [d + j * sc for j in range(k)]


def _fx(tmp, spec=None, status="COMPLETE", hashes_equal=True, partial=False, site_sha_bad=False, vec_sha_bad=False, sepbar="0.0145",
        arm="certPlanted", snapshot=SNAPSHOT, plant_check="OK", ident_d=0.10780301, ident_k=0, ident_seed="n00000001", ident_n=6993,
        ident_p95=0.041626, ident_max=0.042414, drop_site=None, n_bad=None, k_lie=None, reach_lie=None, gs_lie=None, stat_lie=None,
        drop_reps=None, tamper_vec=None, tamper_label=None):
    """spec[site] = dict(k=, reached=None|int): SN built around the site's TRUE planted statistic d (the Python routine on the file's
    rows) so that exactly k replicates are >= d (the k-th equals d: a tie); reached = the number of replicates > 0 (when given, the
    other replicates are 0.0 and d > 0 is required). Default k: 150 at delta 0, 0 elsewhere. Returns (arm, out, sites, vec, labels,
    pins)."""
    spec = spec or {}
    arm_d, outd = os.path.join(tmp, "arm"), os.path.join(tmp, "out")
    os.makedirs(arm_d)
    os.makedirs(outd)
    cat, src, _data, _k2, _vec, (sdata, vdata, _meta, planted) = _fx_build()
    lp = os.path.join(tmp, "declared_labels.tsv")
    lsha = PK2._write_labels(lp, cat, src)
    if "pins" not in _FX_CACHE:
        _FX_CACHE["pins"] = (sha256_bytes(sdata), sha256_bytes(vdata))
    pins = (lsha,) + _FX_CACHE["pins"]
    if tamper_vec:                 # one float of one row of one site nudged by 1e-3
        names = site_names()
        off = sum(len(planted[s][0]) for s in names[:names.index(tamper_vec)])
        arr = bytearray(vdata)
        f = np.frombuffer(bytes(arr[off * SLICE * 4: off * SLICE * 4 + 4]), dtype=">f4")[0]
        arr[off * SLICE * 4: off * SLICE * 4 + 4] = np.array([f + np.float32(1e-3)], dtype=">f4").tobytes()
        vdata = bytes(arr)
    if tamper_label:               # swap one hi and one lo id in all four deltas of a population (still a half-split)
        a, n, d, _dl = parse_name(tamper_label)
        ids, lab, _y = planted[site_name(a, n, d, "0")]
        qh = next(q for q in ids if lab[q] == "hi")
        ql = next(q for q in ids if lab[q] == "lo")
        for dl in DELTAS:
            sn = site_name(a, n, d, dl)
            sdata = sdata.replace(("%s\t%s\thi\n" % (sn, qh)).encode(), ("%s\t%s\tlo\n" % (sn, qh)).encode())
            sdata = sdata.replace(("%s\t%s\tlo\n" % (sn, ql)).encode(), ("%s\t%s\thi\n" % (sn, ql)).encode())
    sp, vp = os.path.join(outd, SITES_NAME), os.path.join(outd, VEC_NAME)
    open(sp, "wb").write(sdata)
    if tamper_vec:
        open(vp, "wb").write(vdata)
    else:                          # the untampered 114 MB file is written once per process and hard-linked (read-only use)
        if "vp" not in _FX_CACHE:
            shared = os.path.join(tempfile.mkdtemp(prefix="cplvec_"), VEC_NAME)
            open(shared, "wb").write(vdata)
            _FX_CACHE["vp"] = shared
        os.link(_FX_CACHE["vp"], vp)
    ssha = (sha256_bytes(sdata) if tamper_label else pins[1]) if not site_sha_bad else sha256_bytes(b"x")
    vsha = (sha256_bytes(vdata) if tamper_vec else pins[2]) if not vec_sha_bad else sha256_bytes(b"x")
    with open(os.path.join(arm_d, "status.txt"), "w") as f:
        f.write("%s\narm=%s\nsnapshot=%s\nsites_sha256=%s\nvectors_sha256=%s\nreps=300\nsliceDim=512\nsepBar=%s\ndropTop=0\n"
                "whiten=false\nminClusterSize=55\nplant_check=%s\nd0_sites=30\nd0_max_abs_diff=5.9e-08\nnorm_max_dev=1.1e-07\n"
                "threads=12\n" % (status, arm, snapshot, ssha, vsha, sepbar, plant_check))
    names = ["IDENTITY"] + site_names()
    if drop_site:
        names.remove(drop_site)
    srows, rep_lines = [], []
    for s in names:
        if s == "IDENTITY":
            sn = [i / 100000.0 for i in range(284)] + [ident_p95] * 15 + [ident_max]
            if ident_k:
                sn[-1] = ident_d + 1e-9
            srows.append('IDENTITY,"IDENTITY",%d,14,,%r,%d,300,%r,%s,300' % (ident_n, ident_d, ident_k, ident_p95, ident_seed))
            rep_lines += ['"IDENTITY",SN,%d,%r' % (i, x) for i, x in enumerate(sn[:150] if partial else sn)]
            continue
        ids, lab, y = planted[s]
        d = _FX_CACHE.setdefault("stat", {}).get(s)
        if d is None:
            d = _FX_CACHE["stat"][s] = stat_of(ids, lab, y)
        sp_ = dict(k=150 if s.endswith("_D0") else 0, reached=None)
        sp_.update(spec.get(s, {}))
        k = sp_["k"]
        if sp_["reached"] is None:
            sn = _sn_default(d, k)
        else:
            assert d > 0 and k == 0, (s, d, k)
            sn = [0.0] * (300 - sp_["reached"]) + [d * (j + 1) / (sp_["reached"] + 1) for j in range(sp_["reached"])]
        n = len(ids) + (1 if n_bad == s else 0)
        gs = "%d/%d" % (sum(1 for v in lab.values() if v == "hi"), sum(1 for v in lab.values() if v == "lo"))
        if gs_lie == s:
            gs = "1/%d" % (n - 1)
        k_arm = sum(1 for x in sn if x >= d) + (1 if k_lie == s else 0)
        reach_arm = sum(1 for x in sn if x > 0.0) + (1 if reach_lie == s else 0)
        d_arm = d + (1e-8 if stat_lie == s else 0.0)
        srows.append('PL,"%s",%d,2,%s,%r,%d,%d,%r,%s,300' % (s, n, gs, d_arm, k_arm, reach_arm, CPC.pctl(sorted(sn), 0.95), s))
        if drop_reps == s:
            continue
        rep_lines += ['"%s",SN,%d,%r' % (s, i, x) for i, x in enumerate(sn)]
    with open(os.path.join(arm_d, "sites.csv"), "w") as f:
        f.write("role,site_id,n,groups,group_sizes,declared_stat,k_declared,reached,null_p95,null_seed_id,reps\n")
        f.write("\n".join(srows) + "\n")
    with open(os.path.join(arm_d, "replicates.csv"), "w") as f:
        f.write("site_id,arm,rep,stat\n" + "\n".join(rep_lines) + "\n")
    for x in ("before", "after"):
        json.dump({"embeddings": "aa/1", "queries": "bb/2" if (hashes_equal or x == "before") else "cc/2"},
                  open(os.path.join(outd, "emb_hashes_%s.json" % x), "w"))
    return arm_d, outd, sp, vp, lp, pins


@contextlib.contextmanager
def _pins(lsha, ssha, vsha):
    global SITES_SHA256, VECTORS_SHA256
    saved = (PK2.LABELS_SHA, PK2.SITES_SHA256, SITES_SHA256, VECTORS_SHA256)
    k2pin = sha256_bytes(_fx_build()[2])
    PK2.LABELS_SHA, PK2.SITES_SHA256, SITES_SHA256, VECTORS_SHA256 = lsha, k2pin, ssha, vsha
    try:
        yield
    finally:
        PK2.LABELS_SHA, PK2.SITES_SHA256, SITES_SHA256, VECTORS_SHA256 = saved


def _ks(anchor, size, delta, ks, **kw):
    return {site_name(anchor, size, i + 1, delta): dict(k=k, **kw) for i, k in enumerate(ks)}


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
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="cplst_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(tmp, **kw):
        arm, outd, sp, vp, lp, pins = _fx(tmp, **kw)
        lines = []
        with _pins(*pins):
            r = analyze(arm, outd, sp, vp, lp, out=lines.append)
        return r, lines, outd

    def refused(tmp, needle, pins_override=None, k2pin=None, **kw):
        arm, outd, sp, vp, lp, pins = _fx(tmp, **kw)
        try:
            with _pins(*(pins_override(pins) if pins_override else pins)):
                if k2pin is not None:
                    PK2.SITES_SHA256 = k2pin          # restored by _pins on exit
                analyze(arm, outd, sp, vp, lp, out=lambda s: None)
        except SystemExit as e:
            assert needle in str(e), (needle, str(e))
            assert not os.path.exists(os.path.join(outd, OUTCOME_NAME)), "a refusal wrote an outcome"
            return
        raise AssertionError("not refused: " + needle)

    def has(lines, s):
        assert s in lines, "missing line %r; got:\n%s" % (s, "\n".join(lines))

    def starts(lines, s):
        assert any(l.startswith(s) for l in lines), "no line starting %r; got:\n%s" % (s, "\n".join(lines))

    def sub(tmp, i):
        p = os.path.join(tmp, "s%d" % i)
        os.makedirs(p)
        return p

    def plant_hand(tmp):
        # 4 unit rows in 3-d, u = e1: x . u = [1, 0, 1, 0], mean 0.5, s (ddof 0) = 0.5; delta 1 -> shift +/- 0.5 e1
        X = np.array([[1.0, 0, 0], [0, 1.0, 0], [1.0, 0, 0], [0, 1.0, 0]])
        u = np.array([1.0, 0, 0])
        Y, s = plant_rows(X, [True, False, False, True], u, "1")
        assert s == 0.5, s
        r5 = 1 / math.sqrt(1.25)
        want = np.array([[1, 0, 0], [-0.5 * r5, r5, 0], [1, 0, 0], [0.5 * r5, r5, 0]])
        assert np.abs(Y - want).max() < 1e-15, Y
        Y0, s0 = plant_rows(X, [True, False, False, True], u, "0")
        assert np.abs(Y0 - X).max() == 0.0 and s0 == 0.5
        # delta 2 on a 2-d toy without a zero row: x = (cos t, sin t) for t in 0, 90, 180-ish; check the halves' mean projections
        X2 = unit(np.array([[3.0, 1.0], [1.0, 3.0], [2.0, 2.0], [1.0, 1.5]]))
        u2 = np.array([1.0, 0.0])
        p = X2 @ u2
        s2_want = float(np.sqrt(((p - p.mean()) ** 2).mean()))
        Y2, s2 = plant_rows(X2, [True, True, False, False], u2, "2")
        assert abs(s2 - s2_want) < 1e-15 and s2 != float(np.std(p, ddof=1))
        raw = X2 + np.outer([2 * s2, 2 * s2, -2 * s2, -2 * s2], u2)
        assert np.abs(Y2 - raw / np.linalg.norm(raw, axis=1)[:, None]).max() < 1e-15
        assert abs(float(np.linalg.norm(Y2, axis=1).max()) - 1.0) < 1e-15

    def seeds(tmp):
        u1, u1b, u2 = direction(1), direction(1), direction(2)
        assert u1.shape == (SLICE,) and abs(float(u1 @ u1) - 1.0) < 1e-12 and np.array_equal(u1, u1b) and not np.allclose(u1, u2)
        rng = random.Random(20261005)
        g = [rng.gauss(0.0, 1.0) for _ in range(SLICE)]
        nrm = math.sqrt(sum(x * x for x in g))
        assert np.abs(u1 - np.array(g) / nrm).max() < 1e-15, "u_1 is not Random(20261004 + 1)"
        ids = ["q%03d" % i for i in range(11)]
        h = halves(list(reversed(ids)), 3)
        perm = list(ids)
        random.Random(20261107).shuffle(perm)
        assert sorted(q for q in ids if h[q] == "hi") == sorted(perm[:5]) and sum(1 for v in h.values() if v == "lo") == 6, h
        assert list(h) == ids
        assert halves(ids, 3) == h and halves(ids, 4) != h

    def built(tmp):
        cat, src, data, k2, vec, (sdata, vdata, meta, planted) = _fx_build()
        lines = sdata.decode().split("\n")
        assert lines[0] == SITE_HEADER and lines[-1] == ""
        names = []
        for ln in lines[1:-1]:
            s = ln.split("\t")[0]
            if not names or names[-1] != s:
                names.append(s)
        assert names == ["IDENTITY"] + site_names(), names[:5]
        assert len(site_names()) == 210 and site_names()[:8] == ["PL_economics_n486_d1_D0", "PL_economics_n486_d1_D2",
                                                                "PL_economics_n486_d1_D4", "PL_economics_n486_d1_D6",
                                                                "PL_economics_n486_d1_D8", "PL_economics_n486_d1_D10",
                                                                "PL_economics_n486_d1_D12", "PL_economics_n486_d2_D0"]
        assert site_names()[-1] == "PL_physics_n441_d5_D12"
        n_rows = sum(len(planted[s][0]) for s in site_names())
        assert n_rows == 105 * 486 + 105 * 441 and len(vdata) == n_rows * SLICE * 4
        for s in ("PL_math_n486_d3_D0", "PL_physics_n441_d5_D2"):
            a, n, d, dl = parse_name(s)
            ids, lab, y = planted[s]
            assert ids == sorted(k2["K2_%s_n%d_d%d" % (a, n, d)]) and lab == halves(ids, d)
        # delta 0 rows = the cache rows (float32); every row unit; D2 rows shifted along u_d by +/- 2 s
        ids, lab, y0 = planted["PL_math_n486_d3_D0"]
        assert np.abs(y0 - np.array([vec[q] for q in ids], dtype=np.float32)).max() <= 6e-8
        _i, _l, y2 = planted["PL_math_n486_d3_D2"]
        X = np.array([vec[q] for q in ids])
        u = direction(3)
        p = X @ u
        s = float(np.sqrt(((p - p.mean()) ** 2).mean()))
        assert abs(meta["PL_math_n486_d3"]["s"] - s) < 1e-15 and meta["PL_math_n486_d3"]["n_hi"] == 243
        hi = np.array([lab[q] == "hi" for q in ids])
        raw = X + np.where(hi, 2 * s, -2 * s)[:, None] * u
        assert np.abs(y2 - (raw / np.linalg.norm(raw, axis=1)[:, None]).astype(np.float32)).max() == 0.0
        # the planted statistic rises with delta (between share ~ delta^2 s^2 / total)
        st = [stat_of(*planted["PL_math_n486_d3_D%s" % dl]) for dl in DELTAS]
        assert st[0] < st[1] < st[2] < st[3] and st[3] > 0, st
        # the file's vector bytes are the planted rows in site order, big-endian
        first = np.frombuffer(vdata[:SLICE * 4], dtype=">f4")
        assert np.array_equal(first, planted["PL_economics_n486_d1_D0"][2][0])
        # deterministic: build again -> identical bytes
        again = build(cat, k2, vec)
        assert again[0] == sdata and again[1] == vdata
        # a missing / wrong-size CERT-PC-K2 site refuses
        for bad, needle in (({k: v for k, v in k2.items() if k != "K2_math_n441_d2"}, "CERT-PC-K2's site K2_math_n441_d2 is missing"),
                            (dict(k2, K2_math_n441_d2=k2["K2_math_n441_d2"][:-1]), "K2_math_n441_d2 holds 440 ids, not 441")):
            try:
                build(cat, bad, vec)
                raise AssertionError("not refused: " + needle)
            except SystemExit as e:
                assert needle in str(e), e

    def db_path(tmp):
        # vectors_from_db: the cache's first 512 big-endian floats, L2-normalised, joined on distilled_text
        import struct
        p = os.path.join(tmp, "emb.db")
        con = sqlite3.connect(p)
        con.execute("CREATE TABLE queries (id TEXT, distilled_text TEXT)")
        con.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
        for i in range(3):
            v = [float(i + 1)] + [0.0] * 599
            v[1] = 1.0
            con.execute("INSERT INTO queries VALUES (?, ?)", ("q%d" % i, "t%d" % i))
            con.execute("INSERT INTO embeddings VALUES (?, ?)", ("t%d" % i, struct.pack(">600f", *v)))
        con.commit()
        con.close()
        got = vectors_from_db(p, ["q2", "q0"])
        assert sorted(got) == ["q0", "q2"] and abs(got["q2"][0] - 3 / math.sqrt(10)) < 1e-12 and abs(got["q0"][1] - 1 / math.sqrt(2)) < 1e-12
        assert got["q2"].shape == (SLICE,)

    def readout_sensitive(tmp):
        r, L, outd = run(tmp)
        assert r["cp0"] == "SIZE-OK" and r["cp1"] == "SENSITIVE" and r["fired"] is False, (r["cp0"], r["cp1"])
        has(L, "CP0 (gate, n 486, delta 0): SIZE-OK; certified 0 of 15, NOT EVALUABLE 0 (SIZE-OK iff <= 1 of 15; CPL-5)")
        has(L, "CP1 (DECIDING, n 486, delta 8): SENSITIVE; certified of 5 per category economics 5, math 5, physics 5; NOT EVALUABLE "
               "economics 0, math 0, physics 0")
        has(L, "F-CP: NOT FIRED (CP1 SENSITIVE).")
        starts(L, "READING (CP1 SENSITIVE): G12's 0 of 60 reads 'the tree's depth-1 splits are weaker than a planted shift of delta* at "
                  "these sizes' (delta* at n 486: economics 2, math 2, physics 2; on the statistic scale economics 0.")
        has(L, "DELTA* n 486 (smallest delta with >= 4 of 5 certified; CPL-6): economics 2, math 2, physics 2")
        has(L, "POWER CURVE n 486 (certified of 15 per delta; NOT EVALUABLE beside): delta 0: 0 of 15 (0.00), NE 0; delta 2: 15 of 15 "
               "(1.00), NE 0; delta 4: 15 of 15 (1.00), NE 0; delta 6: 15 of 15 (1.00), NE 0; delta 8: 15 of 15 (1.00), NE 0; "
               "delta 10: 15 of 15 (1.00), NE 0; delta 12: 15 of 15 (1.00), NE 0")
        has(L, "P1 CP0 SIZE-OK (p 0.85): event yes (SIZE-OK), Brier 0.0225; delta-0 count 0 of 15 against [0, 1]: inside")
        has(L, "P2 delta 0 at n 486: certified 0 of 15 (predicted 0 [0, 1]): inside, |count - point| 0")
        has(L, "P2 delta 2 at n 486: certified 15 of 15 (predicted 0 [0, 2]): OUTSIDE, |count - point| 15")
        has(L, "P2 delta 4 at n 486: certified 15 of 15 (predicted 1 [0, 5]): OUTSIDE, |count - point| 14")
        has(L, "P2 delta 6 at n 486: certified 15 of 15 (predicted 7 [3, 12]): OUTSIDE, |count - point| 8")
        has(L, "P2 delta 8 at n 486: certified 15 of 15 (predicted 14 [10, 15]): inside, |count - point| 1")
        has(L, "P2 delta 10 at n 486: certified 15 of 15 (predicted 15 [13, 15]): inside, |count - point| 0")
        has(L, "P2 delta 12 at n 486: certified 15 of 15 (predicted 15 [14, 15]): inside, |count - point| 0")
        has(L, "P3 CP1 readings (SENSITIVE 0.75, MIXED 0.15, INSENSITIVE 0.10): outcome SENSITIVE, Brier (3-way sum) 0.0950")
        has(L, "P4 median delta* at n 486 (predicted 6 [4, 8]): 2: OUTSIDE")
        has(L, PRE_AMENDMENT)
        assert L.index(PRE_AMENDMENT) == L.index(DOES_NOT_SHOW) - 1
        has(L, "IDENTITY: REPRODUCED (precondition held; null p95 / max equal PC1's)")
        has(L, DOES_NOT_SHOW)
        for ln in LIKE:
            has(L, ln)
        assert any(l.startswith("SUPPORT (a) 300 null replicates per site;") and "0.0126" in l and "0.0352" in l for l in L), L
        cat, src, data, k2, vec, (sdata, vdata, meta, planted) = _fx_build()
        d = stat_of(*planted["PL_math_n486_d2_D2"])
        assert d > 0
        has(L, "  PL_math_n486_d2_D2       n 486 (hi/lo 243/243): planted statistic %.6f; null p50 %.6f / p95 %.6f / max %.6f; k_d   0 "
               "of 300, p_d 1/301 = 0.003322; reached 300 -> CERTIFIED" % (d, d * 150 / 301.0, d * 285 / 301.0, d * 300 / 301.0))
        starts(L, "  PL_physics_n441_d5_D0    n 441 (hi/lo 220/221): planted statistic ")
        assert any(l.startswith("  PL_physics_n441_d5_D0") and l.endswith("k_d 150 of 300, p_d 151/301 = 0.501661; reached %d -> NOT CERTIFIED"
                                                                           % r["res"]["PL_physics_n441_d5_D0"]["reached"]) for l in L)
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert txt.startswith("pool: none (no DB opened; TRAIN-only planted files)\n") and "\nCP1 (DECIDING, n 486, delta 8): SENSITIVE;" in txt
        rows = list(csv.DictReader(open(os.path.join(outd, CSV_NAME), encoding="utf-8")))
        assert len(rows) == 210 and rows[0]["site"] == "PL_economics_n486_d1_D0" and rows[0]["status"] == "NOT CERTIFIED" and \
            rows[3]["status"] == "CERTIFIED" and rows[3]["p_d"] == "1/301" and rows[0]["hi_lo"] == "243/243", rows[0]
        try:
            with _pins(*_fx(sub(tmp, 9))[5]):
                analyze(os.path.join(tmp, "arm"), outd, os.path.join(outd, SITES_NAME), os.path.join(outd, VEC_NAME),
                        os.path.join(tmp, "declared_labels.tsv"), out=lambda s: None)
            raise AssertionError("second analyze not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e

    def cp_levels(tmp):
        no = [100] * 5
        # INSENSITIVE: delta 8 certifies <= 1 of 5 in 2 of 3 (math 1, physics 0), economics 5 -> F-CP fires with its sentence
        sp_ = _merge(_ks("math", 486, "8", [0, 100, 100, 100, 100]), _ks("physics", 486, "8", no))
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["cp1"] == "INSENSITIVE" and r["fired"] is True, r["cp1"]
        has(L, "CP1 (DECIDING, n 486, delta 8): INSENSITIVE; certified of 5 per category economics 5, math 1, physics 0; NOT EVALUABLE "
               "economics 0, math 0, physics 0")
        has(L, SENT_FCP_FIRED)
        assert not any(l.startswith("READING") or l.startswith("F-CP: NOT FIRED") for l in L), L
        has(L, "P3 CP1 readings (SENSITIVE 0.75, MIXED 0.15, INSENSITIVE 0.10): outcome INSENSITIVE, Brier (3-way sum) 1.3950")
        # MIXED: one category >= 4, one <= 1, one at 2-3
        sp2 = _merge(_ks("math", 486, "8", [0, 0, 100, 100, 100]), _ks("physics", 486, "8", no))
        r, L, _o = run(sub(tmp, 1), spec=sp2)
        assert r["cp1"] == "MIXED" and r["fired"] is False, r["cp1"]
        has(L, "F-CP: NOT FIRED (CP1 MIXED).")
        has(L, "READING: none (CP1 MIXED: a registered MIXED; no sentence)")
        has(L, "P3 CP1 readings (SENSITIVE 0.75, MIXED 0.15, INSENSITIVE 0.10): outcome MIXED, Brier (3-way sum) 1.2950")
        # boundaries: 4 of 5 counts as SENSITIVE (two categories at 4), 3 of 5 does not; k 14 certifies, k 15 does not
        sp3 = _merge(_ks("math", 486, "8", [14, 14, 14, 14, 15]), _ks("physics", 486, "8", [0, 0, 0, 0, 100]),
                     _ks("economics", 486, "8", no))
        r, L, _o = run(sub(tmp, 2), spec=sp3)
        assert r["cp1"] == "SENSITIVE", r["cp1"]
        assert r["res"]["PL_math_n486_d1_D8"]["status"] == "CERTIFIED" and r["res"]["PL_math_n486_d5_D8"]["status"] == "NOT CERTIFIED"
        starts(L, "  PL_math_n486_d1_D8       n 486 (hi/lo 243/243): planted statistic ")
        assert any(l.startswith("  PL_math_n486_d5_D8") and "k_d  15 of 300, p_d 16/301 = 0.053156;" in l and l.endswith("NOT CERTIFIED")
                   for l in L)
        sp4 = _merge(_ks("math", 486, "8", [14, 14, 14, 15, 15]), _ks("physics", 486, "8", [0, 0, 0, 0, 100]),
                     _ks("economics", 486, "8", no))
        r, L, _o = run(sub(tmp, 3), spec=sp4)
        assert r["cp1"] == "MIXED", r["cp1"]       # math 3, physics 4, economics 0: one >= 4, one <= 1
        # 2 of 5 is not INSENSITIVE: math 2, physics 2, economics 5 -> MIXED
        sp5 = _merge(_ks("math", 486, "8", [0, 0, 100, 100, 100]), _ks("physics", 486, "8", [0, 0, 100, 100, 100]))
        r, L, _o = run(sub(tmp, 4), spec=sp5)
        assert r["cp1"] == "MIXED", r["cp1"]
        # CP1 reads n 486 only: n 441 delta 8 all failing leaves CP1 SENSITIVE; and n 486 failing with n 441 passing -> INSENSITIVE
        sp6 = _merge(*[_ks(a, 441, "8", no) for a in ANCHORS])
        r, L, _o = run(sub(tmp, 5), spec=sp6)
        assert r["cp1"] == "SENSITIVE" and r["dstar"][("math", 441)] == "2", (r["cp1"], r["dstar"])
        sp7 = _merge(*[_ks(a, 486, "8", no) for a in ANCHORS])
        r, L, _o = run(sub(tmp, 6), spec=sp7)
        assert r["cp1"] == "INSENSITIVE" and r["fired"] is True, r["cp1"]
        # CP1 reads delta 8 only: delta 6 all failing leaves SENSITIVE
        sp8 = _merge(*[_ks(a, 486, "6", no) for a in ANCHORS])
        r, L, _o = run(sub(tmp, 7), spec=sp8)
        assert r["cp1"] == "SENSITIVE", r["cp1"]
        has(L, "P2 delta 6 at n 486: certified 0 of 15 (predicted 7 [3, 12]): OUTSIDE, |count - point| 7")

    def cp0_gate(tmp):
        # a delta-0 site can certify only if its planted statistic is > 0 (else every exceeding replicate is <= 0: DEGENERATE);
        # the fixture's positive delta-0 sites at n 486:
        planted = _fx_build()[5][3]
        pos = [(a, dd) for a in ANCHORS for dd in DRAWS if stat_of(*planted[site_name(a, 486, dd, "0")]) > 0]
        assert len(pos) >= 2, pos
        (a1, d1), (a2, d2) = pos[0], pos[1]
        # delta 0 certifies 1 of 15 -> SIZE-OK; 2 of 15 -> ANTI-CONSERVATIVE and CP1 NOT EVALUABLE (no F-CP, no reading)
        r, L, _o = run(sub(tmp, 0), spec={site_name(a1, 486, d1, "0"): dict(k=0)})
        assert r["cp0"] == "SIZE-OK" and r["cp1"] == "SENSITIVE", (r["cp0"], r["cp1"])
        has(L, "CP0 (gate, n 486, delta 0): SIZE-OK; certified 1 of 15, NOT EVALUABLE 0 (SIZE-OK iff <= 1 of 15; CPL-5)")
        has(L, "P1 CP0 SIZE-OK (p 0.85): event yes (SIZE-OK), Brier 0.0225; delta-0 count 1 of 15 against [0, 1]: inside")
        sp_ = _merge({site_name(a1, 486, d1, "0"): dict(k=0), site_name(a2, 486, d2, "0"): dict(k=14)},
                     _merge(*[_ks(a, 486, "8", [100] * 5) for a in ANCHORS]))
        r, L, _o = run(sub(tmp, 1), spec=sp_)
        assert r["cp0"] == "ANTI-CONSERVATIVE" and r["cp1"] == "NOT EVALUABLE" and r["fired"] is False, (r["cp0"], r["cp1"])
        has(L, "CP0 (gate, n 486, delta 0): ANTI-CONSERVATIVE; certified 2 of 15, NOT EVALUABLE 0 (SIZE-OK iff <= 1 of 15; CPL-5)")
        has(L, "CP1 (DECIDING, n 486, delta 8): NOT EVALUABLE; certified of 5 per category economics 0, math 0, physics 0; NOT "
               "EVALUABLE economics 0, math 0, physics 0 (CP0 ANTI-CONSERVATIVE: CP1 NOT EVALUABLE)")
        has(L, "F-CP: NOT FIRED (CP1 NOT EVALUABLE).")
        has(L, "READING: none (CP1 NOT EVALUABLE: not evaluable (CP0 ANTI-CONSERVATIVE; CPL-5); no sentence)")
        has(L, "P1 CP0 SIZE-OK (p 0.85): event no (ANTI-CONSERVATIVE), Brier 0.7225; delta-0 count 2 of 15 against [0, 1]: OUTSIDE")
        has(L, "P3 CP1 readings: NOT SCORED (CP1 NOT EVALUABLE; CPL-7)")
        # CP0 with one certified and one NOT EVALUABLE (a delta-0 site with statistic <= 0 at k 0 is DEGENERATE) -> NOT EVALUABLE
        neg = next((a, dd) for a in ANCHORS for dd in DRAWS if stat_of(*planted[site_name(a, 486, dd, "0")]) <= 0)
        r, L, _o = run(sub(tmp, 2), spec={site_name(a1, 486, d1, "0"): dict(k=0), site_name(neg[0], 486, neg[1], "0"): dict(k=0)})
        assert r["cp0"] == "NOT EVALUABLE" and r["cp1"] == "NOT EVALUABLE", (r["cp0"], r["cp1"])
        assert r["res"][site_name(neg[0], 486, neg[1], "0")]["status"] == "NOT EVALUABLE (DEGENERATE)"
        has(L, "CP0 (gate, n 486, delta 0): NOT EVALUABLE; certified 1 of 15, NOT EVALUABLE 1 (SIZE-OK iff <= 1 of 15; CPL-5)")
        has(L, "P1 CP0 SIZE-OK (p 0.85): NOT SCORED (CP0 NOT EVALUABLE; CPL-7); delta-0 count 1 of 15 against [0, 1]: inside")
        has(L, "READING: none (CP1 NOT EVALUABLE: not evaluable (CP0 NOT EVALUABLE; CPL-5); no sentence)")
        # CP0 reads n 486 only: every n 441 delta-0 site at k 0 (certified or DEGENERATE) leaves SIZE-OK
        r, L, _o = run(sub(tmp, 3), spec=_merge(*[_ks(a, 441, "0", [0] * 5) for a in ANCHORS]))
        assert r["cp0"] == "SIZE-OK" and r["cp1"] == "SENSITIVE", (r["cp0"], r["cp1"])
        # CP0 reads delta 0 only: delta 2 certifying everywhere (the default) leaves SIZE-OK (readout_sensitive)

    def not_evaluable(tmp):
        # DEGENERATE 19 / 20 at a delta-2 site; reached 19 -> NOT EVALUABLE (DEGENERATE)
        r, L, _o = run(sub(tmp, 0), spec={"PL_math_n486_d1_D8": dict(k=0, reached=19)})
        assert r["res"]["PL_math_n486_d1_D8"]["status"] == "NOT EVALUABLE (DEGENERATE)" and r["cp1"] == "SENSITIVE", r["cp1"]
        r, L, _o = run(sub(tmp, 1), spec={"PL_math_n486_d1_D8": dict(k=0, reached=20)})
        assert r["res"]["PL_math_n486_d1_D8"]["status"] == "CERTIFIED"
        # CPL-5 on CP1: math 3 certified + 2 NE, physics 3 + 2 NE, economics 0 -> lo MIXED (3, 3, 0), hi SENSITIVE (5, 5, 0)
        sp_ = _merge(_ks("math", 486, "8", [0, 0, 0, 0, 0]), _ks("physics", 486, "8", [0, 0, 0, 0, 0]), _ks("economics", 486, "8", [100] * 5))
        for a in ("math", "physics"):
            for dd in (4, 5):
                sp_[site_name(a, 486, dd, "8")] = dict(k=0, reached=5)
        r, L, _o = run(sub(tmp, 2), spec=sp_)
        assert r["cp1"] == "NOT EVALUABLE" and r["fired"] is False, r["cp1"]
        has(L, "CP1 (DECIDING, n 486, delta 8): NOT EVALUABLE; certified of 5 per category economics 0, math 3, physics 3; NOT "
               "EVALUABLE economics 0, math 2, physics 2")
        has(L, "READING: none (CP1 NOT EVALUABLE: not evaluable (CP0 SIZE-OK; CPL-5); no sentence)")
        # ... and when the NE sites cannot change the word: math 4 + 1 NE, physics 4 + 1 NE -> SENSITIVE either way
        sp2 = _merge(_ks("economics", 486, "8", [100] * 5))
        sp2["PL_math_n486_d5_D8"] = dict(k=0, reached=5)
        sp2["PL_physics_n486_d5_D8"] = dict(k=0, reached=5)
        r, L, _o = run(sub(tmp, 3), spec=sp2)
        assert r["cp1"] == "SENSITIVE", r["cp1"]
        # helpers: every CPL-5 completion pattern agrees with the brute force over the NE sites
        import itertools
        for c, e in itertools.product(range(16), range(16)):
            if c + e > 15:
                continue
            words = {cp0_word(c + j) for j in range(e + 1)}
            assert cp0_verdict(c, e) == (words.pop() if len(words) == 1 else "NOT EVALUABLE"), (c, e)
        for ce in itertools.product([(c, e) for c in range(6) for e in range(6) if c + e <= 5], repeat=3):
            words = {cp1_word([c + j for (c, _e), j in zip(ce, js)]) for js in itertools.product(*[range(e + 1) for _c, e in ce])}
            assert cp1_verdict("SIZE-OK", list(ce)) == (words.pop() if len(words) == 1 else "NOT EVALUABLE"), ce
        assert cp1_verdict("NOT EVALUABLE", [(5, 0)] * 3) == "NOT EVALUABLE" and cp1_verdict("ANTI-CONSERVATIVE", [(5, 0)] * 3) == "NOT EVALUABLE"
        assert subsample_status(109, 0, 300) == "NOT EVALUABLE (NULL-INFEASIBLE)" and subsample_status(110, 0, 300) == "CERTIFIED"
        assert subsample_status(486, 14, 20) == "CERTIFIED" and subsample_status(486, 15, 300) == "NOT CERTIFIED"

    def dstar_scale(tmp):
        # delta* = the SMALLEST delta with >= 4 of 5: math fails at 2 -> 4; physics fails at 2, 4, 6 -> 8; economics fails at every
        # delta but 8, where it certifies 3 of 5 -> '> 12'; median of (4, 8, > 12) = 8
        no = [100] * 5
        sp_ = _merge(_ks("math", 486, "2", no), _ks("physics", 486, "2", no), _ks("physics", 486, "4", no), _ks("physics", 486, "6", no),
                     *[_ks("economics", 486, dl, no) for dl in ("2", "4", "6", "10", "12")], _ks("economics", 486, "8", [0, 0, 0, 100, 100]))
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["dstar"][("math", 486)] == "4" and r["dstar"][("physics", 486)] == "8" and r["dstar"][("economics", 486)] is None
        has(L, "DELTA* n 486 (smallest delta with >= 4 of 5 certified; CPL-6): economics > 12, math 4, physics 8")
        has(L, "P4 median delta* at n 486 (predicted 6 [4, 8]): 8: inside")
        cat, src, data, k2, vec, (sdata, vdata, meta, planted) = _fx_build()
        sm = median([stat_of(*planted[site_name("math", 486, dd, "4")]) for dd in DRAWS])
        sp = median([stat_of(*planted[site_name("physics", 486, dd, "8")]) for dd in DRAWS])
        has(L, "SCALE (n 486): delta* on the separation-statistic scale (median planted statistic of the delta* sites): economics n/a "
               "(delta* > 12), math %.6f, physics %.6f; G12's 14 TOP splits 0.037-0.040 (registered)" % (sm, sp))
        assert sm != median([stat_of(*planted[site_name("math", 486, dd, "8")]) for dd in DRAWS])
        has(L, "CP1 (DECIDING, n 486, delta 8): SENSITIVE; certified of 5 per category economics 3, math 5, physics 5; NOT EVALUABLE "
               "economics 0, math 0, physics 0")
        has(L, "DELTA* n 441 (smallest delta with >= 4 of 5 certified; CPL-6): economics 2, math 2, physics 2")
        # two categories never -> median '> 12', P4 OUTSIDE
        sp2 = _merge(sp_, *[_ks("math", 486, dl, no) for dl in ("4", "6", "8", "10", "12")])
        r, L, _o = run(sub(tmp, 1), spec=sp2)
        has(L, "P4 median delta* at n 486 (predicted 6 [4, 8]): > 12: OUTSIDE")
        # P4 boundaries: median 4 and 8 inside, 2 and 10 outside
        for i, (dm, want) in enumerate((("4", "inside"), ("10", "OUTSIDE"))):
            fail = [dl for dl in DELTAS[1:] if int(dl) < int(dm)]
            sp3 = _merge(*[_ks(a_, 486, dl, no) for a_ in ANCHORS for dl in fail])
            r, L, _o = run(sub(tmp, 2 + i), spec=sp3)
            has(L, "P4 median delta* at n 486 (predicted 6 [4, 8]): %s: %s" % (dm, want))
        assert median_rank([None, "0", "2"]) == "2" and median_rank(["4", "0", "12"]) == "4" and median_rank([None, None, "0"]) is None
        assert median_rank(["10", "2", "8"]) == "8", "median ranks numerically, not as strings"

        def cbd(**kw):
            d = {dl: 0 for dl in DELTAS}
            d.update({k[1:]: v for k, v in kw.items()})
            return d
        assert delta_star(cbd(d0=3, d2=4, d4=5)) == "2" and delta_star(cbd(d0=5)) == "0" and delta_star(cbd(d12=4)) == "12"
        assert delta_star(cbd(d2=3, d4=3, d6=3, d8=3, d10=3, d12=3)) is None
        assert median([0.3, 0.1, 0.2]) == 0.2

    def identity(tmp):
        refused(sub(tmp, 0), "IDENTITY FAILED: declared 0.107804 k_d 0", ident_d=0.1078041)
        refused(sub(tmp, 1), "IDENTITY FAILED: declared 0.107803 k_d 1", ident_k=1)
        refused(sub(tmp, 2), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed PL_x", ident_seed="PL_x")
        refused(sub(tmp, 3), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6992 seed n00000001", ident_n=6992)
        refused(sub(tmp, 4), "p95 0.041627 max 0.042414", ident_p95=0.041627)
        refused(sub(tmp, 5), "p95 0.041626 max 0.042415", ident_max=0.042415)

    def refusals(tmp):
        for i, (needle, kw) in enumerate([
                ("the arm's status is 'REFUSED: x'", dict(status="REFUSED: x")),
                ("a partial file", dict(partial=True)),
                ("embeddings_cache.db changed during the arm", dict(hashes_equal=False)),
                ("the arm read site file sha256", dict(site_sha_bad=True)),
                ("the arm read vector file sha256", dict(vec_sha_bad=True)),
                ("instrument: the arm ran sepBar='0.025'", dict(sepbar="0.025")),
                ("instrument: the arm ran arm='certPcK2'", dict(arm="certPcK2")),
                ("instrument: the arm ran plant_check='FAILED'", dict(plant_check="FAILED")),
                ("the arm read snapshot 'OTHER'", dict(snapshot="OTHER")),
                ("sites.csv holds", dict(drop_site="PL_math_n441_d3_D4")),
                ("sites.csv: PL_physics_n441_d2_D2 n 442", dict(n_bad="PL_physics_n441_d2_D2")),
                ("sites.csv: PL_math_n486_d4_D2 n 486 groups 2 sizes 1/485", dict(gs_lie="PL_math_n486_d4_D2")),
                ("PL_math_n486_d3_D2: k_d recount 0 != the arm's 1", dict(k_lie="PL_math_n486_d3_D2")),
                ("PL_economics_n441_d5_D4: reached recount", dict(reach_lie="PL_economics_n441_d5_D4")),
                ("PL_physics_n486_d2_D10: the arm's declared statistic", dict(stat_lie="PL_physics_n486_d2_D10")),
                ("replicates: PL_physics_n486_d2_D0's SN arm is missing", dict(drop_reps="PL_physics_n486_d2_D0"))]):
            refused(sub(tmp, i), needle, **kw)
        # the planted files other than the pinned refuse, by the pin and (each alone) by the rebuild
        refused(sub(tmp, 20), "is not VECTORS_SHA256", tamper_vec="PL_math_n441_d2_D6")
        refused(sub(tmp, 21), "PL_math_n441_d2_D6: the planted rows are not the delta-0 rows planted", tamper_vec="PL_math_n441_d2_D6",
                pins_override=lambda p: (p[0], p[1], sha256_bytes(open(os.path.join(tmp, "s21", "out", VEC_NAME), "rb").read())))
        refused(sub(tmp, 22), "is not SITES_SHA256", tamper_label="PL_physics_n486_d3_D0")
        refused(sub(tmp, 23), "the site file is not the registered plant rebuilt from the CPC labels", tamper_label="PL_physics_n486_d3_D0",
                pins_override=lambda p: (p[0], sha256_bytes(open(os.path.join(tmp, "s23", "out", SITES_NAME), "rb").read()), p[2]))
        refused(sub(tmp, 24), "not CERT-POSITIVE-CONTROL's label file of record", pins_override=lambda p: ("0" * 64, p[1], p[2]))
        refused(sub(tmp, 28), "CERT-PC-K2's draw rebuilt from the CPC labels is sha256", k2pin="0" * 64)
        refused(sub(tmp, 25), "the planted files are NOT PINNED", pins_override=lambda p: (p[0], None, p[2]))
        refused(sub(tmp, 26), "the planted files are NOT PINNED", pins_override=lambda p: (p[0], p[1], None))
        # a delta-0 tamper breaks that row's unit norm -> its own rebuild (renormalised) refuses first
        refused(sub(tmp, 27), "PL_math_n441_d2_D0: the planted rows are not the delta-0 rows planted", tamper_vec="PL_math_n441_d2_D0",
                pins_override=lambda p: (p[0], p[1], sha256_bytes(open(os.path.join(tmp, "s27", "out", VEC_NAME), "rb").read())))

    def helpers(tmp):
        cfg = G.load_config(os.path.join(ROOT, PCS.CONFIG_REL))
        assert command(cfg, 6) == (
            '.\\gradlew.bat certPlanted --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 '
            '"-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" '
            '"-DsiteLabels=experiment_results/cert_planted/planted_sites.tsv" '
            '"-DplantedVectors=experiment_results/cert_planted/planted_vectors.f32be" "-DoutDir=experiment_results/cert_planted/arm"'), command(cfg, 6)
        assert command(cfg, 8).endswith(' "-DsiteNullHeap=8g"')
        assert parse_name("PL_economics_n441_d3_D10") == ("economics", 441, 3, "10")
        for fn_, arg in ((prepare, (tmp, "x")), (hashes, ("before", tmp))):
            try:
                fn_(*arg)
                raise AssertionError("%s from another data root not refused" % fn_.__name__)
            except SystemExit as e:
                assert tmp in str(e), e
        assert pin_word("a", None).startswith("NOT PINNED") and pin_word("a", "a") == "= the pin" and pin_word("a", "b") == "NOT the pin b"

    def main_analyze(tmp):
        global OUT_REL
        arm, outd, sp, vp, lp, pins = _fx(tmp, spec=_merge(_ks("math", 486, "8", [100] * 5), _ks("physics", 486, "8", [0, 100, 100, 100, 100])))
        os.replace(arm, os.path.join(outd, ARM_NAME))
        saved = OUT_REL
        OUT_REL = os.path.abspath(outd)
        try:
            with _pins(*pins):
                rc = main(["--analyze", "--cpc-labels", lp])
            if rc != 0:
                raise AssertionError("main --analyze returned %r" % rc)
        finally:
            OUT_REL = saved
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert "\nCP1 (DECIDING, n 486, delta 8): INSENSITIVE;" in txt and "\n" + SENT_FCP_FIRED + "\n" in txt, txt[-900:]

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
                   ("plant_rows on hand-computed rows (s ddof 0, sign, renormalisation)", plant_hand),
                   ("direction / halves seeds (CPL-2, CPL-3)", seeds),
                   ("build(): order, sizes, delta-0 rows, D2 geometry, statistic rises, determinism, refusals", built),
                   ("vectors_from_db on a fixture cache", db_path),
                   ("SENSITIVE: every printed line, write-once", readout_sensitive),
                   ("CP1 levels, boundaries 4 / 3 / 2 / 1 of 5, tie at k 14, n 486 only, delta 8 only, F-CP", cp_levels),
                   ("CP0 gate 1 / 2 of 15, n 486 only; ANTI-CONSERVATIVE -> CP1 NOT EVALUABLE", cp0_gate),
                   ("NOT EVALUABLE: DEGENERATE 19 / 20, CPL-5 completions (brute force)", not_evaluable),
                   ("delta* smallest, '> 12', median, P4 bounds, scale conversion", dstar_scale),
                   ("IDENTITY refusals (incl. PC1 p95 / max)", identity), ("refusals (incl. both pins and both rebuilds)", refusals),
                   ("helpers", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


MUTANTS = [
    ("M0 control (no-op; must SURVIVE)", "TAG = \"[CPL]\"", "TAG = \"[CPL]\""),
    ("M1 k_d counts > (not >=)", "        k = CPC.kcount(R[(s, \"SN\")], dk)", "        k = sum(1 for x in R[(s, \"SN\")] if x > dk)"),
    ("M2 p = k/300", "    return \"CERTIFIED\" if bool(CPC.p_of(k) <= BAR) else \"NOT CERTIFIED\"",
     "    return \"CERTIFIED\" if bool(Fraction(k, 300) <= BAR) else \"NOT CERTIFIED\""),
    ("M3 CP0 <= 1 -> <= 2", "    return \"SIZE-OK\" if c <= 1 else \"ANTI-CONSERVATIVE\"", "    return \"SIZE-OK\" if c <= 2 else \"ANTI-CONSERVATIVE\""),
    ("M4 CP0 <= 1 -> == 0", "    return \"SIZE-OK\" if c <= 1 else \"ANTI-CONSERVATIVE\"", "    return \"SIZE-OK\" if c == 0 else \"ANTI-CONSERVATIVE\""),
    ("M5 CP0 from n 441", "    c0 = sum(cnt[(a, DECIDING_N, \"0\")][0] for a in ANCHORS)", "    c0 = sum(cnt[(a, 441, \"0\")][0] for a in ANCHORS)"),
    ("M6 CP0 from delta 2", "    c0 = sum(cnt[(a, DECIDING_N, \"0\")][0] for a in ANCHORS)", "    c0 = sum(cnt[(a, DECIDING_N, \"2\")][0] for a in ANCHORS)"),
    ("M7 ANTI-CONSERVATIVE does not gate CP1", "    if cp0 != \"SIZE-OK\":\n        return \"NOT EVALUABLE\"", "    if False:\n        return \"NOT EVALUABLE\""),
    ("M8 CP1 c >= 4 -> >= 3", "    if sum(1 for c in counts if c >= 4) >= 2:", "    if sum(1 for c in counts if c >= 3) >= 2:"),
    ("M9 CP1 SENSITIVE in >= 1 category", "    if sum(1 for c in counts if c >= 4) >= 2:", "    if sum(1 for c in counts if c >= 4) >= 1:"),
    ("M10 CP1 INSENSITIVE c <= 1 -> <= 2", "    if sum(1 for c in counts if c <= 1) >= 2:", "    if sum(1 for c in counts if c <= 2) >= 2:"),
    ("M11 CP1 INSENSITIVE in >= 3 categories", "    if sum(1 for c in counts if c <= 1) >= 2:", "    if sum(1 for c in counts if c <= 1) >= 3:"),
    ("M12 CP1 INSENSITIVE checked first", "    if sum(1 for c in counts if c >= 4) >= 2:\n        return \"SENSITIVE\"\n    if sum(1 for c in counts if c <= 1) >= 2:\n        return \"INSENSITIVE\"",
     "    if sum(1 for c in counts if c <= 0) >= 2:\n        return \"INSENSITIVE\"\n    if sum(1 for c in counts if c >= 4) >= 2:\n        return \"SENSITIVE\""),
    ("M13 CP1 from n 441", "    ce = [cnt[(a, DECIDING_N, DELTA_DEC)] for a in ANCHORS]", "    ce = [cnt[(a, 441, DELTA_DEC)] for a in ANCHORS]"),
    ("M14 CP1 from delta 6", "    ce = [cnt[(a, DECIDING_N, DELTA_DEC)] for a in ANCHORS]", "    ce = [cnt[(a, DECIDING_N, \"6\")] for a in ANCHORS]"),
    ("M14b CP1 from delta 2 (the pre-amendment anchor)", "DELTA_DEC = \"8\"", "DELTA_DEC = \"2\""),
    ("M14c CP1 from delta 10", "DELTA_DEC = \"8\"", "DELTA_DEC = \"10\""),
    ("M15 CP1 from the first category only", "    ce = [cnt[(a, DECIDING_N, DELTA_DEC)] for a in ANCHORS]", "    ce = [cnt[(ANCHORS[0], DECIDING_N, DELTA_DEC)] for a in ANCHORS]"),
    ("M16 cell counts from the first draw only", "        sts = [res[site_name(a, n, dd, dl)][\"status\"] for dd in DRAWS]",
     "        sts = [res[site_name(a, n, 1, dl)][\"status\"] for dd in DRAWS]"),
    ("M17 CPL-5 ignores NE on CP1", "    lo, hi = cp1_word([c for c, _e in ce]), cp1_word([c + e for c, e in ce])\n    return lo if lo == hi else \"NOT EVALUABLE\"",
     "    lo, hi = cp1_word([c for c, _e in ce]), cp1_word([c + e for c, e in ce])\n    return lo"),
    ("M18 CPL-5 NE counted certified on CP1", "    lo, hi = cp1_word([c for c, _e in ce]), cp1_word([c + e for c, e in ce])\n    return lo if lo == hi else \"NOT EVALUABLE\"",
     "    lo, hi = cp1_word([c for c, _e in ce]), cp1_word([c + e for c, e in ce])\n    return hi"),
    ("M19 CPL-5 ignores NE on CP0", "    lo, hi = cp0_word(c), cp0_word(c + e)\n    return lo if lo == hi else \"NOT EVALUABLE\"",
     "    lo, hi = cp0_word(c), cp0_word(c + e)\n    return lo"),
    ("M20 F-CP on MIXED too", "    if cp1 == \"INSENSITIVE\":\n        say(SENT_FCP_FIRED)", "    if cp1 in (\"INSENSITIVE\", \"MIXED\"):\n        say(SENT_FCP_FIRED)"),
    ("M21 SENSITIVE reading on MIXED", "        if cp1 == \"SENSITIVE\":\n            say(\"READING (CP1 SENSITIVE)", "        if cp1 != \"NOT EVALUABLE\":\n            say(\"READING (CP1 SENSITIVE)"),
    ("M22 fired flag on SENSITIVE", "fired=bool(cp1 == \"INSENSITIVE\")", "fired=bool(cp1 != \"MIXED\")"),
    ("M23 P1 scored when NOT EVALUABLE", "    if cp0 != \"NOT EVALUABLE\":\n        e1 = bool(cp0 == \"SIZE-OK\")", "    if True:\n        e1 = bool(cp0 == \"SIZE-OK\")"),
    ("M24 P3 scored when NOT EVALUABLE", "    if cp1 in P3_PROBS:", "    if True:"),
    ("M25 P2 counts n 441", "        c = sum(cnt[(a, DECIDING_N, dl)][0] for a in ANCHORS)\n        pt, lo, hi = P2_REG[dl]",
     "        c = sum(cnt[(a, 441, dl)][0] for a in ANCHORS)\n        pt, lo, hi = P2_REG[dl]"),
    ("M26 delta* = the LARGEST delta", "    for dl in DELTAS:\n        if cert_by_delta[dl] >= 4:", "    for dl in reversed(DELTAS):\n        if cert_by_delta[dl] >= 4:"),
    ("M27 delta* >= 3 of 5", "        if cert_by_delta[dl] >= 4:", "        if cert_by_delta[dl] >= 3:"),
    ("M28 delta* skips delta 0", "    for dl in DELTAS:\n        if cert_by_delta[dl] >= 4:", "    for dl in DELTAS[1:]:\n        if cert_by_delta[dl] >= 4:"),
    ("M29 median_rank -> min", "    return key[len(key) // 2]", "    return key[0]"),
    ("M30 P4 from n 441", "    mds = median_rank([dstar[(a, DECIDING_N)] for a in ANCHORS])", "    mds = median_rank([dstar[(a, 441)] for a in ANCHORS])"),
    ("M31 scale from delta 8 always", "            scale[a] = median([res[site_name(a, DECIDING_N, dd, ds)][\"stat\"] for dd in DRAWS])",
     "            scale[a] = median([res[site_name(a, DECIDING_N, dd, \"8\")][\"stat\"] for dd in DRAWS])"),
    ("M32 degenerate check removed", "    if reached < DEGENERATE_MIN:", "    if False:"),
    ("M33 degenerate floor 20 -> 19", "REPS, MCS, DEGENERATE_MIN = 300, 55, 20", "REPS, MCS, DEGENERATE_MIN = 300, 55, 19"),
    ("M34 infeasible floor removed", "    if n < 2 * MCS:", "    if False:"),
    ("M35 s with ddof 1", "    s = float(np.sqrt(((p - p.mean()) ** 2).mean()))", "    s = float(np.std(p, ddof=1))"),
    ("M36 s = total SD (all dims)", "    s = float(np.sqrt(((p - p.mean()) ** 2).mean()))", "    s = float(np.sqrt(((X - X.mean(axis=0)) ** 2).sum(axis=1).mean()))"),
    ("M37 both halves shifted +", "    sign = np.where(np.asarray(hi_mask, dtype=bool), 1.0, -1.0)", "    sign = np.where(np.asarray(hi_mask, dtype=bool), 1.0, 1.0)"),
    ("M38 no renormalisation", "    return unit(X + (sign * float(delta) * s)[:, None] * u[None, :]), s", "    return X + (sign * float(delta) * s)[:, None] * u[None, :], s"),
    ("M39 shift by delta x u (no s)", "    return unit(X + (sign * float(delta) * s)[:, None] * u[None, :]), s", "    return unit(X + (sign * float(delta))[:, None] * u[None, :]), s"),
    ("M40 u seed off by one (index d + 1)", "    rng = random.Random(U_SEED0 + d)", "    rng = random.Random(U_SEED0 + d + 1)"),
    ("M41 half seed = the u seed", "    random.Random(H_SEED0 + d).shuffle(perm)", "    random.Random(U_SEED0 + d).shuffle(perm)"),
    ("M42 halves not shuffled (first half by id)", "    random.Random(H_SEED0 + d).shuffle(perm)", "    pass"),
    ("M43 hi = ceil(n / 2)", "    hi = set(perm[:len(perm) // 2])", "    hi = set(perm[:(len(perm) + 1) // 2])"),
    ("M44 u not normalised", "    return g / math.sqrt(float(g @ g))", "    return g"),
    ("M45 build: u by category index", "                u = direction(d)", "                u = direction(d + ANCHORS.index(a))"),
    ("M46 build: populations from draw d + 1", "                k2 = \"K2_%s_n%d_d%d\" % (a, n, d)\n                if k2 not in k2_sites:",
     "                k2 = \"K2_%s_n%d_d%d\" % (a, n, d % 5 + 1)\n                if k2 not in k2_sites:"),
    ("M47 build: little-endian vector file", "                    chunks.append(y32.astype(\">f4\").tobytes())", "                    chunks.append(y32.astype(\"<f4\").tobytes())"),
    ("M48 site order: deltas outer", "    return [site_name(a, n, d, dl) for a in ANCHORS for n in SIZES for d in DRAWS for dl in DELTAS]",
     "    return [site_name(a, n, d, dl) for dl in DELTAS for a in ANCHORS for n in SIZES for d in DRAWS]"),
    ("M49 delta grid 12 -> 14", "DELTAS = (\"0\", \"2\", \"4\", \"6\", \"8\", \"10\", \"12\")", "DELTAS = (\"0\", \"2\", \"4\", \"6\", \"8\", \"10\", \"14\")"),
    ("M49b grid without delta 4", "DELTAS = (\"0\", \"2\", \"4\", \"6\", \"8\", \"10\", \"12\")", "DELTAS = (\"0\", \"2\", \"6\", \"8\", \"10\", \"12\")"),
    ("M75 P2 restated delta 8 lo 10 -> 9", "\"8\": (14, 10, 15)", "\"8\": (14, 9, 15)"),
    ("M76 P2 skips delta 0", "    for dl in DELTAS:\n        c = sum(cnt[(a, DECIDING_N, dl)][0] for a in ANCHORS)", "    for dl in DELTAS[1:]:\n        c = sum(cnt[(a, DECIDING_N, dl)][0] for a in ANCHORS)"),
    ("M77 P3 pre-amendment probabilities", "P3_PROBS = {\"SENSITIVE\": 0.75", "P3_PROBS = {\"SENSITIVE\": 0.70"),
    ("M78 P4 pre-amendment interval", "P4_REG = (6.0, 4.0, 8.0)", "P4_REG = (1.0, 0.5, 2.0)"),
    ("M79 pre-amendment line not printed", "    say(PRE_AMENDMENT)\n", ""),
    ("M80 NONE_WORD > 2", "NONE_WORD = \"> 12\"", "NONE_WORD = \"> 2\""),
    ("M50 IDENTITY gate removed", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K", "    if False and not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K"),
    ("M51 IDENTITY p95 / max not checked", "\n            and p95_0 == PC1_P95 and max_0 == PC1_MAX):", "):"),
    ("M52 IDENTITY seed not checked", " and ir[\"null_seed_id\"] == ROOT_ID\n", "\n"),
    ("M53 site pin not checked", "    if s_sha != SITES_SHA256:", "    if False:"),
    ("M54 vector pin not checked", "    if v_sha != VECTORS_SHA256:", "    if False:"),
    ("M55 site rebuild not checked", "    if (\"\\n\".join(rebuilt_rows) + \"\\n\").encode(\"utf-8\") != sbytes:", "    if False:"),
    ("M56 vector rebuild not checked", "                    if not diff <= PLANT_TOL:", "                    if False:"),
    ("M57 arm-read site sha not checked", "    if st.get(\"sites_sha256\") != s_sha:", "    if False:"),
    ("M58 arm-read vector sha not checked", "    if st.get(\"vectors_sha256\") != v_sha:", "    if False:"),
    ("M59 hash check removed", "    if json.load(open(hb)) != json.load(open(ha)):", "    if False:"),
    ("M60 write-once pre-check removed", "        if os.path.exists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)"),
    ("M61 partial replicates accepted", "        if [i for i, _x in xs] != list(range(REPS)):", "        if False:"),
    ("M62 instrument check removed", "        if st.get(k) != v:\n            refuse(\"instrument", "        if False:\n            refuse(\"instrument"),
    ("M63 snapshot check removed", "    if st.get(\"snapshot\") != SNAPSHOT:", "    if False:"),
    ("M64 sites.csv set check removed", "    if list(rows) != want:", "    if False:"),
    ("M65 k recount check removed", "        if k != int(r[\"k_declared\"]):", "        if False:"),
    ("M66 reached recount check removed", "        if reached != int(r[\"reached\"]):", "        if False:"),
    ("M67 declared statistic check removed", "        if not abs(dp - dk) <= TOL:", "        if False:"),
    ("M68 group sizes not checked", " or int(r[\"groups\"]) != 2 or r[\"group_sizes\"] != gs:", " or int(r[\"groups\"]) != 2:"),
    ("M69 missing arm not checked", "        if (s, \"SN\") not in R:", "        if False:"),
    ("M70 pins-None refusal removed (analyze)", "    if SITES_SHA256 is None or VECTORS_SHA256 is None:\n        refuse(\"the planted files are NOT PINNED (SITES_SHA256 / VECTORS_SHA256): no readout\")",
     "    if False:\n        refuse(\"the planted files are NOT PINNED (SITES_SHA256 / VECTORS_SHA256): no readout\")"),
    ("M71 CERT-PC-K2 pin not checked (analyze)", "    if sha256_bytes(k2data) != PK2.SITES_SHA256:", "    if False:"),
    ("M72 selftest gate in main removed", "    if not _IN_SELFTEST and selftest() != 0:", "    if False:"),
    ("M73 k_d against the Python statistic + 1e-6", "        k = CPC.kcount(R[(s, \"SN\")], dk)", "        k = CPC.kcount(R[(s, \"SN\")], dk + 1e-6)"),
    ("M74 stat_of groups lo then hi swapped to one group", "    return PKK.declared_stat([U[[i for i, q in enumerate(ids) if lab[q] == c]] for c in (\"hi\", \"lo\")])",
     "    return PKK.declared_stat([U])"),
]


MUTANT_WORKERS = 8         # parallel selftest children (single-threaded BLAS each)


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    t0 = src.index("\nMUTANTS = [\n")
    t1 = src.index("\n]\n", t0) + 3
    head, table, tail = src[:t0], src[t0:t1], src[t1:]        # never mutate the table's own text
    from concurrent.futures import ThreadPoolExecutor
    sandbox = scratch_dir.mkdtemp(prefix="cpl_mut_")         # on E:, removed by scratch_dir at exit (no deletion code here)
    env = dict(os.environ, CPL_SRC_DIR=HERE, PYTHONPATH=HERE, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    jobs = []
    for i, (name, old, new) in enumerate(MUTANTS):
        if old in head:
            mut = head.replace(old, new, 1) + table + tail
        elif old in tail:
            mut = head + table + tail.replace(old, new, 1)
        else:
            jobs.append((name, None))
            continue
        p = os.path.join(sandbox, "cert_planted_m%02d.py" % i)
        with open(p, "x", encoding="utf-8") as f:
            f.write(mut)
        jobs.append((name, p))

    def one(job):
        name, p = job
        if p is None:
            return name, "NOT APPLIED (pattern absent)"
        r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True, timeout=1800, env=env)
        return name, "KILLED" if r.returncode != 0 else "SURVIVED"
    with ThreadPoolExecutor(max_workers=MUTANT_WORKERS) as ex:
        rows = list(ex.map(one, jobs))
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
    if not _IN_SELFTEST and selftest() != 0:
        refuse("the selftest is red: no readout")
    d = os.path.join(ROOT, OUT_REL)
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(d, SITES_NAME), os.path.join(d, VEC_NAME), cpc_labels)
    return 0


if __name__ == "__main__":
    sys.exit(main())
