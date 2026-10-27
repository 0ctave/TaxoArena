"""cert_split_dip.py: CERT-SPLIT-DIP (the split-dip certificate; deciding) and the joint run of SI-NULL-TRIAD's arms S and G
(module si_null_triad.py) in ONE pool window: site assembly, the per-site cache, the launch and both READOUTS. ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-08 (before any code or call) — CERT-SPLIT-DIP: does a sample-splitting dip certificate (spherical k-means
k = 2 on a random half A, Hartigan's dip test of half B projected on A's centroid difference, 2 x median p over R = 20 halvings)
certify FRESHLY planted 2-way shifts at G12's depth-1 sizes where the plain site null of record does not, without certifying
moment-matched or elongated unimodal clouds? (zero calls; CPU; run with SI-NULL-TRIAD in one pool window)" (span L24958-L24972,
commit e83b59d5); registrar's record L24950-L24956; record docs/agents/results/CERT-SPLIT-DIP.json. SI-NULL-TRIAD: L24335-L24347
(si_null_triad.py's docstring).
  THE RULE per site: R = 20 halvings A / B (halving seed = int(sha256(site name)) mod 2^32 + r); on A spherical k-means k = 2
  (k-means++ init, 10 restarts, cosine, <= 100 iterations); u = c1 - c2; B's unit rows projected on u; Hartigan's dip test
  (diptest 0.11.0, tabulated p); p_site = min(1, 2 x median of the 20 p); CERTIFIED iff p_site <= 0.05.
  SD0 (gate): SIZE-OK iff the 300 SIZE draws certify at a rate <= 0.10 with 95% CP upper <= 0.15 AND delta 0 certifies <= 1 of 15
  at n 486; else ANTI-CONSERVATIVE and SD1 NOT EVALUABLE. SD1 (DECIDING; delta 6; fresh plants; n 486 and n 441 pooled, 60 sites):
  SENSITIVE iff >= 45 of 60; INSENSITIVE iff <= 15 of 60; MIXED otherwise. SD2: POS-OK iff >= 4 of 5 in >= 2 of the 3 merged
  pairs; POS-FAIL iff <= 1 of 5 in >= 2 of 3; MIXED otherwise. F-SD fires iff >= 8 of the 70 elongation controls certify OR SD1
  reads INSENSITIVE. P1 SD0 SIZE-OK 0.95, SIZE rate 0.00 [0.00, 0.02]; P2 SD1 SENSITIVE 0.90 / MIXED 0.08 / INSENSITIVE 0.02,
  delta 6 58 [50, 60] of 60; P3 delta 3 2 [0, 8], delta 4 12 [3, 25], delta 8 60 [57, 60]; P4 SD2 POS-OK 0.95; P5 elongation
  0 [0, 3] of 70; P6 median delta* 5 [4, 6].
  PILOT DISCLOSURE (registered): the 2026-10-07 exploratory numbers were SEEN, pilot role only, never evidence:
  E:/TaxoArena_tmp/cert_split (results.json sha256 32fcf7cd8baa1367..., VERIFIED_HEADLINE.txt 98b32054b56bde7b..., analyze.log,
  cert_split.py, verify/: dip 30/30 at delta 6 / 8 vs the site null 0/15, 2/15; 0/150 matched Gaussians; the PC1 median-cut
  control population 10/10), E:/TaxoArena_tmp/hier_tests (granularity_free, nesting, test3_fair_backoff + review dirs),
  E:/TaxoArena_tmp/scpb/review_v3_synthesis.md. Every deciding plant here is FRESH (seed bases 20261008000 / 20261108000 /
  20261208, used by neither the record, the pilot nor its verifier). The pilot script is NOT the instrument (nothing copied; the
  rule is re-implemented here and the record's cert_planted.direction / halves / plant_rows / read_planted are imported).

BUILDER'S READINGS (each handed to the reviewer / registrar; none changes a criterion word, bar or denominator):
  CSD-1 Halving RNG: numpy default_rng(int(sha256(name).hexdigest(), 16) mod 2^32 + r); the permutation is drawn first, A = the
        first floor(n / 2), B the rest; the same generator then seeds the k-means++ draws. A halving whose 10 restarts all
        degenerate (one cluster) contributes p = 1.
  CSD-2 Fresh plants: u_dj = cert_planted.direction(20261008000 + 10 d + j - 20261004) (= random.Random(20261008000 + 10 d + j),
        512 gauss draws, normalised; the record function with its seed offset); halves = cert_planted.halves(ids, 20261108000 +
        10 d + j - 20261104); rows = cert_planted.plant_rows(D0 rows, hi, u, delta), rendered float32 then projectTo(512) as
        CERT-PLANTED's planted file is. D0 rows = CERT-PLANTED's planted file (pinned 14c626d5 / 2135279e), checked equal to the
        cache's rows within 1e-6.
  CSD-3 SIZE draws = SI-NULL-TRIAD's (SIN-1). E1 = per STRONG / MID n-486 merged-pair subsample, 5 draws of the record
        generator form (mean + sum_c g_c c / sqrt(M), unit-renormalised) with that subsample's mean and covariance, seed
        default_rng(20261208 + i), i = role (STRONG, MID) x draw (1..5) x g (0..4) in that order. E2 = 20 clouds N(0,
        diag(r^2, 1, ..., 1)) in the slice, unit-renormalised, r = 3 (g 0..9) then 10 (g 0..9), seed default_rng(20261208 + 50 +
        i) (the pilot's form; the record names no other synthetic form for "axis ratio").
  CSD-4 Second slice R256 (descriptive): the same ids' first 256 cache floats renormalised (= the 512 rows truncated and
        renormalised), plants with cert_planted.direction(..., dim=256) (the first 256 draws of the same stream) and the same
        halves; SIZE / E1 / E2 / merged pairs at 256 with the same seeds.
  CSD-5 delta* per category = smallest nonzero delta of {2, 3, 4, 5, 6, 8, 10} with >= 8 of 10 (5 draws x 2 plants) certified at
        n 486 (delta 0 has 5 sites and cannot reach 8); none -> '> 10' (ranked 11 for P6's median).
  CSD-6 Realised dependence (printed beside the declared DEFF 1.5, never deciding): one-way ANOVA ICC of the 60 delta-6
        outcomes over the 30 subsamples (2 plants each), DEFF = 1 + ICC, n_eff, MDE80 = 2.8 sqrt(0.75 x 0.25 / n_eff).
  CSD-7 The dip arm is never NOT EVALUABLE (a degenerate halving contributes p = 1). The (vi) PC1 median-cut population = the
        STRONG / MID merged pairs: its line READS (iv)'s 10 sites, it is not recomputed.
  CSD-8 SI-NULL-TRIAD "on this grid descriptively" = S, G_I, G_S on (i)-(iv) at R512; G12's 60 real sites at their own k.

LAUNCH SEQUENCE (run-operator; a POOL READER under rule 7: never beside a construction or site null; E:/TaxoArena_tmp/busy.ps1
exit 1 immediately before --run; single-threaded BLAS per process):
  python tools/analysis/cert_split_dip.py --selftest           both tests' selftests (fixtures; every registered print branch)
  python tools/analysis/cert_split_dip.py --mutants            the mutant table below against --selftest (copies on E:)
  python tools/analysis/cert_split_dip.py --selftest-io --g12-sites <main>/experiment_results/archv2/rp12_r2/g12/G12_sites.csv
                                                               the DB half of --dry-run / --run --pilot 1 / --analyze --pilot 1
                                                               end to end on a FIXTURE data root (fixture embeddings_cache.db
                                                               and snapshots.db on E:; no pool read)
  python tools/analysis/cert_split_dip.py --smoke              NO DB: two record plants through the dip rule and one S / G site
                                                               at reduced sims; timings (record plants: seen in the pilot)
  python tools/analysis/cert_split_dip.py --dry-run            READS the pool (embeddings_cache.db, snapshots.db, mode=ro&
                                                               immutable=1): pins, every site class and count, the identity
                                                               precondition, the set hash, the runtime estimate; writes nothing
  python tools/analysis/cert_split_dip.py --run [--workers W] [--pilot N]
                                                               selftest gate; meta pinned in <out>/cache.jsonl at first launch
                                                               (refused on mismatch); resumable; identity precondition first
  python tools/analysis/cert_split_dip.py --analyze            from a COMPLETE cache, write-once (mode x): <out>/
                                                               CERT_SPLIT_DIP_OUTCOME.txt, cert_split_dip_sites.csv,
                                                               SI_NULL_TRIAD_OUTCOME.txt, si_null_triad_sites.csv; a partial
                                                               cache writes *_partial.txt only; a pilot cache *_PILOT.txt
  Defaults: --data-root $TAXOARENA_DATA_ROOT or the repo root; --planted-dir E:/TaxoArena_backup_2026-10-05_cert_planted;
  --kk-labels E:/TaxoArena_backup_2026-10-03_cert_pc_k2_known/site_labels.tsv; --out <repo>/experiment_results/cert_split_dip.
  diptest 0.11.0 must import (else --pylib DIR, e.g. E:/TaxoArena_tmp/cert_split/pylib; the version and the sha256 of its two
  files are pinned in the cache meta). Outputs are NEVER committed: E:/TaxoArena_backup_<date>_cert_split_dip with SHA256SUMS.txt.
  --pilot N: no judge, so the registered 5%-unparsed truncation guard has nothing to parse; a pilot runs the first N sites of
  each class into <out>/pilot_cache.jsonl and --analyze --pilot writes *_PILOT.txt.

RUNTIME (measured 2026-10-08 on the planted files, one process, single-threaded BLAS): dip about 0.1-0.2 s per site (about
1,700 sites: about 5 min); S about 4-5 s and G about 5 s per variant per n-486 site (1,105 sites: about 4.5 h); G12's 60 sites
(n up to about 800, q 128, k up to 4: up to about 1 min per G variant): about 1.5-2 h; in all about 6-7 h single-process,
about 1 h at --workers 8 (results are identical for any worker count: seeds follow the site name).

SELFTEST (--selftest, about 10 s; each case runs a real entry point on a fixture with a hand-known answer and asserts the printed
VALUE): the rule (bimodal / unimodal / degenerate, 2 x median, the halving seed, alpha inclusive); SD0 (30 / 31 of 300, 1 / 2 of
15, n 441 never gates, the CP upper as its own bar, the NOT EVALUABLE path); SD1 (45 / 44 / 16 / 15, pooled sizes, the FAILS line,
the three readings, the record's delta-6 counts per size); SD2 (seven count patterns); F-SD (7 / 8 of 70 over E1 + E2, the
INSENSITIVE clause); P1-P6 (bands and Brier values); delta*; the realised ICC / DEFF; the denominators (300 / 70 or REFUSED); the
proxy (java.util.Random, numba EM == numpy EM, correctedKappa, the identity precondition at 1.0 / 0.9917 / 0.9854 / 0.75); the arms
(planted / isotropic / elongated fixtures, S's (1 + k) / (1 + B) form, Holm at k = 3, the S floor, the soft threshold); TN1 (THIRD /
NO / MIXED / NOT EVALUABLE incl. SIN-6 and P reaching the count), F-SN, P1-P4, the descriptive lines; the engine (run, resume
without recomputation, meta refusal, the identity gate, analyze write-once, partial and pilot files); main(['--run']).
MUTANTS (--mutants; 50 / 50 killed on 2026-10-08; table in the commit message).
"""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402
from fractions import Fraction  # noqa: E402

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
HERE = os.environ.get("CSD_SRC_DIR") or SELF_DIR          # the record modules (cert_planted & co.) live here
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, SELF_DIR)
import tempfile; import scratch_dir  # noqa: E401,E402  TEMP-SPRAWL: temp on E:, removed at exit
from data_v2 import ro as RO  # noqa: E402
import si_null_triad as SN  # noqa: E402

TAG = "[CSD]"
_IN_SELFTEST = False
CP_BLOB = "028f05a2cd6db90c5a1c76b36923647033127805"      # cert_planted.py at e83b59d5


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_cp():
    got = RO.git_blob_lf(os.path.join(HERE, "cert_planted.py"))
    if got != CP_BLOB:
        refuse("cert_planted.py is blob %s, not the pinned %s (imported unchanged, never copied)" % (got, CP_BLOB))
    import cert_planted
    return cert_planted


CP = _import_cp()
PKK, PCS = CP.PKK, CP.PCS
CPC, G = CP.CPC, CP.G

# ------------------------------------------------------------------------------------------------ registered constants
R_HALV, KM_RESTARTS, KM_ITERS, ALPHA = 20, 10, 100, 0.05
DIPTEST_VERSION = "0.11.0"
ANCHORS, SIZES, DRAWS, DECIDING_N = CP.ANCHORS, CP.SIZES, CP.DRAWS, CP.DECIDING_N
DELTAS_CSD = ("0", "2", "3", "4", "5", "6", "8", "10")
DELTA_DEC = "6"
R256_DELTAS = ("0", "4", "6", "8")
PLANTS = (1, 2)
U_SEED_F, H_SEED_F, E_SEED = 20261008000, 20261108000, 20261208
ROLES, E1_ROLES, E1_PER, E2_RATIOS, E2_PER = ("STRONG", "MID", "EDGE"), ("STRONG", "MID"), 5, (3, 10), 10
N_SIZE, N_ELONG, N_SD1 = 300, 70, 60
SD1_SENS, SD1_INS = 45, 15
FSD_ELONG = 8
P1_P, P1_BAND = 0.95, (0.00, 0.00, 0.02)
P2_P = {"SENSITIVE": 0.90, "MIXED": 0.08, "INSENSITIVE": 0.02}
P2_BAND = (58, 50, 60)
P3_BANDS = {"3": (2, 0, 8), "4": (12, 3, 25), "8": (60, 57, 60)}
P4_P = 0.95
P5_BAND = (0, 0, 3)
P6_BAND = (5.0, 4.0, 6.0)
NONE_WORD = "> 10"
DEFF_DECL, NEFF_DECL, MDE_DECL = 1.5, 40.0, 0.192
CPL_CSV_SHA256 = "359357a56de26f2a574094ef6a67b672ba9f09ba52acd40e10c7fdbcbd6d4e6c"
PLANTED_DIR_DEFAULT = "E:/TaxoArena_backup_2026-10-05_cert_planted"
KK_LABELS_DEFAULT = "E:/TaxoArena_backup_2026-10-03_cert_pc_k2_known/site_labels.tsv"
G12_SITES_REL = CPC.G12_SITES_REL
CONFIG_REL = CPC.CONFIG_REL
MCS = 55
OUT_REL = "experiment_results/cert_split_dip"
CSD_OUT, CSD_CSV = "CERT_SPLIT_DIP_OUTCOME.txt", "cert_split_dip_sites.csv"
SN_OUT, SN_CSV = "SI_NULL_TRIAD_OUTCOME.txt", "si_null_triad_sites.csv"
REG = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — CERT-SPLIT-DIP: ..." L24958-L24972 '
       '(e83b59d5); registrar\'s record L24950-L24956')
PILOT_LINE = ("PILOT DISCLOSURE (registered; SEEN, pilot role only, never evidence): E:/TaxoArena_tmp/cert_split (results.json "
              "32fcf7cd8baa1367..., VERIFIED_HEADLINE.txt 98b32054b56bde7b...), E:/TaxoArena_tmp/hier_tests, "
              "E:/TaxoArena_tmp/scpb/review_v3_synthesis.md; delta_dec and the bars were sized on the pilot; every deciding "
              "plant is fresh")
LIKE = ["LIKE WITH LIKE: | arm | calibration | axis chosen on | statistic | label status |",
        "  | split-dip (this) | dip's uniform tables, 2 x median over halvings | half A, disjoint from the tested half | dip of "
        "half B | [LF] |",
        "  | plain J site null (CERT-PLANTED, record) | Gaussian moment-matched to the site's own rows | the declared partition "
        "| J | declared |",
        "  | deflated (CERT-K2-DEFLATED, record) | site rows with the declared axis projected out | the declared partition | J "
        "| declared |",
        "  | S, G (SI-NULL-TRIAD) | background covariance / selective | the site | 2-means CI / selective mean difference | "
        "[LF] |"]
NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW: a certificate of any tree site (G12's sites are not run by the dip arm; a later "
            "registration with multiplicity control); exact size (the dip's uniform calibration is conservative; SIZE-OK bounds "
            "the rate only); k > 2; other members, draws or embedders (R256 descriptive); that the plain site null of record is "
            "wrong (a different calibration, not a correction); anything from the pilot's LRT arms; a GMM LR / BIC mode test "
            "(closed).")
SENT_SENS = ("SD1 READING (SENSITIVE): the split-dip rule certifies a planted 2-way shift of a size the plain site null of "
             "record did not certify")
SENT_FSD_E = ("F-SD (elongation clause) FIRED: the split-dip rule is an elongation detector like the deflated null "
              "(CERT-K2-DEFLATED W-2); no SD1 or SD2 certification can be read as evidence of 2-way structure")
SENT_FSD_I = ("F-SD (INSENSITIVE clause) FIRED: the pilot's 30/30 at delta 6 is overturned as a property of the rule rather "
              "than of the plants it used")


# ================================================================================================ the rule
_DIP = {}


def load_diptest(pylib=None):
    if "m" in _DIP:
        return _DIP["m"]
    try:
        import diptest
    except ImportError:
        if pylib and os.path.isdir(pylib):
            sys.path.insert(0, pylib)
            import diptest
        else:
            refuse("diptest is not importable; pass --pylib DIR (e.g. E:/TaxoArena_tmp/cert_split/pylib)")
    if getattr(diptest, "__version__", None) != DIPTEST_VERSION:
        refuse("diptest %s is not the pinned %s" % (getattr(diptest, "__version__", None), DIPTEST_VERSION))
    _DIP["m"] = diptest
    return diptest


def diptest_pins():
    m = load_diptest()
    d = os.path.dirname(m.__file__)
    files = sorted(os.path.join(dp, f) for dp, _dn, fs in os.walk(d) for f in fs
                   if f.endswith((".py", ".pyd", ".so")) and "__pycache__" not in dp)
    h = hashlib.sha256()
    for f in files:
        h.update(os.path.relpath(f, d).replace("\\", "/").encode())
        h.update(open(f, "rb").read())
    return dict(version=m.__version__, files=len(files), sha256=h.hexdigest())


def unit(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.sqrt((X * X).sum(axis=1))
    n[n == 0] = 1.0
    return X / n[:, None]


def skmeans2(X, rng, n_init=KM_RESTARTS, iters=KM_ITERS):
    """Spherical k-means k = 2: k-means++ init on cosine distance, n_init restarts, <= iters Lloyd steps; best by sum of
    max cosine. -> (2, d) unit centroids or None (every restart degenerate)."""
    n = len(X)
    best, best_obj = None, -np.inf
    for _ in range(n_init):
        i0 = int(rng.integers(n))
        d = np.clip(1.0 - X @ X[i0], 0.0, None)
        if d.sum() <= 0:
            continue
        i1 = int(rng.choice(n, p=d / d.sum()))
        C = np.stack([X[i0], X[i1]])
        lab = None
        for _it in range(iters):
            new = (X @ C.T).argmax(axis=1)
            if lab is not None and np.array_equal(new, lab):
                break
            lab = new
            if lab.min() == lab.max():
                break
            C = unit(np.stack([X[lab == 0].sum(axis=0), X[lab == 1].sum(axis=0)]))
        if lab is None or lab.min() == lab.max():
            continue
        obj = float((X @ C.T).max(axis=1).sum())
        if obj > best_obj:
            best_obj, best = obj, C.copy()
    return best


def certified(p):
    """CERTIFIED iff p_site <= 0.05."""
    return bool(p <= ALPHA)


def halving_seed(name, r):
    return int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16) % (2 ** 32) + r


def combine(ps):
    """p_site = min(1, 2 x median of the halvings' p)."""
    return float(min(1.0, 2.0 * float(np.median(np.asarray(ps, dtype=np.float64)))))


def dip_site(name, X, u_plant=None, R=R_HALV):
    diptest = load_diptest()
    X = unit(X)
    n = len(X)
    ps, coss = [], []
    for r in range(R):
        rng = np.random.default_rng(halving_seed(name, r))
        perm = rng.permutation(n)
        A, B = perm[: n // 2], perm[n // 2:]
        C = skmeans2(X[A], rng)
        if C is None:
            ps.append(1.0)
            continue
        u = C[0] - C[1]
        nu = float(np.linalg.norm(u))
        if nu == 0.0:
            ps.append(1.0)
            continue
        y = X[B] @ (u / nu)
        _d, p = diptest.diptest(np.asarray(y, dtype=np.float64))
        ps.append(float(p))
        if u_plant is not None:
            coss.append(abs(float(u @ u_plant)) / nu)
    p_site = combine(ps)
    return dict(p=p_site, cert=certified(p_site), ps=ps,
                cos09=(None if not coss else sum(1 for c in coss if c > 0.9) / len(coss)))


# ================================================================================================ site assembly
def gen_matched(P, n, rng):
    """The record's moment-matched generator (withinNodeCloud): mean + sum_c g_c c / sqrt(M), rows unit-renormalised."""
    P = np.asarray(P, dtype=np.float64)
    mu = P.mean(axis=0)
    C = P - mu
    Z = rng.standard_normal((n, len(P)))
    return unit(mu + (Z @ C) / math.sqrt(len(P)))


def trunc(U, dim):
    return unit(np.asarray(U, dtype=np.float64)[:, :dim])


def rows512(y32):
    return PKK.unit_rows(np.asarray(y32, dtype=np.float32))


def fresh_plant(ids, U0, d, j, delta, dim=512):
    u = CP.direction(U_SEED_F + 10 * d + j - CP.U_SEED0, dim=dim)
    hl = CP.halves(ids, H_SEED_F + 10 * d + j - CP.H_SEED0)
    hi = np.array([hl[q] == "hi" for q in ids])
    Y, _s = CP.plant_rows(U0, hi, u, delta)
    Y32 = Y.astype(np.float32).astype(np.float64)
    return unit(Y32), u


def record_extra_plant(ids, U0, d, delta):
    """SI-C1: delta 0.5 / 1 planted with the RECORD seeds (CPL-2 / CPL-3)."""
    u = CP.direction(d)
    hl = CP.halves(ids, d)
    hi = np.array([hl[q] == "hi" for q in ids])
    Y, _s = CP.plant_rows(U0, hi, u, delta)
    return rows512(Y.astype(np.float32))


def add(sites, name, cls, X, arms, **meta):
    if name in sites:
        refuse("duplicate site name %s" % name)
    sites[name] = dict(name=name, cls=cls, X=np.ascontiguousarray(X, dtype=np.float64), arms=tuple(arms), k=meta.pop("k", 2),
                       u=meta.pop("u", None), meta=meta)


TRIAD = ("S", "G_I", "G_S")


def build_sites(planted, kk, vec, g12=None, triad=True):
    """planted: {PL site: (ids, (n, 512) float32)}; kk: the KK site file {site: {id: category}} incl. IDENTITY; vec: {id: unit 512
    row}; g12: list of dict(node, ids, children [list of id sets]) or None. -> ordered {name: site}."""
    S = {}
    tri = TRIAD if triad else ()
    pops = {}
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                ids, y32 = planted[CP.site_name(a, n, d, "0")]
                pops[(a, n, d)] = (list(ids), rows512(y32))
    # (i) POWER, fresh plants, R512 and R256 (CSD-2, CSD-4)
    for dim, pre, grid in ((512, "CSD", DELTAS_CSD), (256, "CSD256", R256_DELTAS)):
        for a in ANCHORS:
            for n in SIZES:
                for d in DRAWS:
                    ids, U0 = pops[(a, n, d)]
                    U0d = U0 if dim == 512 else trunc(U0, dim)
                    add(S, "%s_%s_n%d_d%d_D0" % (pre, a, n, d), "POWER" if dim == 512 else "POWER256", U0d,
                        ("dip",) + (tri if dim == 512 else ()), cat=a, n=n, draw=d, plant=0, delta="0", dim=dim)
                    for j in PLANTS:
                        for dl in grid[1:]:
                            Y, u = fresh_plant(ids, U0d, d, j, dl, dim)
                            add(S, "%s_%s_n%d_d%d_j%d_D%s" % (pre, a, n, d, j, dl), "POWER" if dim == 512 else "POWER256", Y,
                                ("dip",) + (tri if dim == 512 else ()), u=u, cat=a, n=n, draw=d, plant=j, delta=dl, dim=dim)
    # (ii) SIZE (SIN-1 / CSD-3)
    ident = kk["IDENTITY"]
    idx = 0
    for a in ANCHORS:
        pid = sorted(q for q, c in ident.items() if c == a)
        if not pid:
            refuse("IDENTITY holds no %s item" % a)
        P = np.array([vec[q] for q in pid])
        for n in SIZES:
            for g in range(SN.SIZE_PER_CELL):
                seed = SN.SIZE_SEED0 + idx
                add(S, "SIZE_%s_n%d_g%d" % (a, n, g), "SIZE", gen_matched(P, n, np.random.default_rng(seed)), ("dip",) + tri,
                    cat=a, n=n, g=g, seed=seed, dim=512)
                add(S, "SIZE256_%s_n%d_g%d" % (a, n, g), "SIZE256", gen_matched(trunc(P, 256), n, np.random.default_rng(seed)),
                    ("dip",), cat=a, n=n, g=g, seed=seed, dim=256)
                idx += 1
    # (iii) ELONGATION CONTROLS E1, E2 (CSD-3)
    i = 0
    for role in E1_ROLES:
        for d in DRAWS:
            pid = sorted(kk["KK_%s_n486_d%d" % (role, d)])
            P = np.array([vec[q] for q in pid])
            for g in range(E1_PER):
                seed = E_SEED + i
                add(S, "E1_%s_n486_d%d_g%d" % (role, d, g), "E1", gen_matched(P, 486, np.random.default_rng(seed)),
                    ("dip",) + tri, role=role, n=486, draw=d, g=g, seed=seed, dim=512)
                add(S, "E1_256_%s_n486_d%d_g%d" % (role, d, g), "E1_256", gen_matched(trunc(P, 256), 486,
                                                                                      np.random.default_rng(seed)),
                    ("dip",), role=role, n=486, draw=d, g=g, seed=seed, dim=256)
                i += 1
    i = 0
    for r in E2_RATIOS:
        for g in range(E2_PER):
            seed = E_SEED + 50 + i
            for dim, pre, cls, arms in ((512, "E2", "E2", ("dip",) + tri), (256, "E2_256", "E2_256", ("dip",))):
                Z = np.random.default_rng(seed).standard_normal((486, dim))
                Z[:, 0] *= r
                add(S, "%s_r%d_g%d" % (pre, r, g), cls, unit(Z), arms, ratio=r, g=g, seed=seed, n=486, dim=dim)
            i += 1
    # (iv) POSITIVE CONTROLS (merged pairs) R512 and R256
    for role in ROLES:
        for d in DRAWS:
            nm = "KK_%s_n486_d%d" % (role, d)
            pid = sorted(kk[nm])
            P = np.array([vec[q] for q in pid])
            add(S, nm, "POS", P, ("dip",) + tri, role=role, n=486, draw=d, dim=512)
            add(S, "KK256_%s_n486_d%d" % (role, d), "POS256", trunc(P, 256), ("dip",), role=role, n=486, draw=d, dim=256)
    # record plants (descriptive for the dip; SI-NULL-TRIAD's POWER grid) and SI-C1's 0.5 / 1
    for s in CP.site_names():
        a, n, d, dl = CP.parse_name(s)
        ids, y32 = planted[s]
        add(S, s, "REC", rows512(y32), ("dip",) + tri, cat=a, n=n, draw=d, delta=dl, dim=512)
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                ids, U0 = pops[(a, n, d)]
                for dl in SN.EXTRA_DELTAS:
                    add(S, CP.site_name(a, n, d, dl), "RECX", record_extra_plant(ids, U0, d, dl), ("dip",) + tri,
                        cat=a, n=n, draw=d, delta=dl, dim=512)
    # G12's real sites (SI-NULL-TRIAD descriptive)
    for s in (g12 or []):
        if triad:
            add(S, "G12_%s" % s["node"], "G12", np.array([vec[q] for q in s["ids"]]), tri, k=len(s["children"]),
                node=s["node"], n=len(s["ids"]), dim=512)
    return S


def expected_tasks(sites):
    return sorted((name, arm) for name, s in sites.items() for arm in s["arms"])


def set_hash(sites):
    h = hashlib.sha256()
    for name in sorted(sites):
        s = sites[name]
        h.update(("%s|%s|%d|" % (name, ",".join(s["arms"]), s["k"])).encode())
        h.update(np.ascontiguousarray(s["X"], dtype=np.float64).tobytes())
    return h.hexdigest()


def sha256_file(p):
    return RO.file_sha256(p)


def read_record_p(path):
    """CERT-PLANTED's cpl_sites.csv -> {PL site: True / False / None}."""
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            st = r["status"]
            out[r["site"]] = True if st == "CERTIFIED" else (False if st == "NOT CERTIFIED" else None)
    return out


def load_inputs(a, out=print, with_db=True):
    """The pinned files and (with_db) the pool rows. -> dict(planted, kk, vec, rec_p, g12, s2, cfg, pins)."""
    pins = {}
    sp, vp = os.path.join(a.planted_dir, "planted_sites.tsv"), os.path.join(a.planted_dir, "planted_vectors.f32be")
    cp_csv = os.path.join(a.planted_dir, "cpl_sites.csv")
    for p, pin, what in ((sp, CP.SITES_SHA256, "planted_sites.tsv"), (vp, CP.VECTORS_SHA256, "planted_vectors.f32be"),
                         (cp_csv, CPL_CSV_SHA256, "cpl_sites.csv"), (a.kk_labels, PKK.SITES_SHA256, "KK site_labels.tsv")):
        if not os.path.isfile(p):
            refuse("%s not found at %s" % (what, p))
        got = sha256_file(p)
        out("%s pin %s sha256 %s... %s" % (TAG, what, got[:16], "OK" if got == pin else "MISMATCH (pinned %s...)" % pin[:16]))
        if got != pin:
            refuse("%s sha256 %s is not the pinned %s" % (what, got, pin))
        pins[what] = got
    _sf, rows_by_site, _sb, _vb = CP.read_planted(sp, vp)
    kk = PCS.parse_site_file(a.kk_labels)
    rec_p = read_record_p(cp_csv)
    res = dict(planted=rows_by_site, kk=kk, rec_p=rec_p, pins=pins, vec=None, g12=None, s2=None)
    if not with_db:
        return res
    db = os.path.join(a.data_root, "embeddings_cache.db")
    ident = sorted(kk["IDENTITY"])
    out("%s reading %d IDENTITY (TRAIN root) rows from %s (mode=ro&immutable=1; first 512 floats)" % (TAG, len(ident), db))
    vec = PKK.load_vectors(db, ident)
    need = set()
    for s, m in kk.items():
        need |= set(m)
    for s in CP.site_names():
        need |= set(rows_by_site[s][0])
    extra = sorted(need - set(ident))
    if extra:
        refuse("%d site ids are outside the IDENTITY TRAIN root (e.g. %s)" % (len(extra), extra[:3]))
    worst = 0.0
    for an in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                ids, y32 = rows_by_site[CP.site_name(an, n, d, "0")]
                diff = float(np.max(np.abs(np.array([vec[q] for q in ids]) - rows512(y32))))
                worst = max(worst, diff)
    out("%s D0 rows of the planted file vs the cache's rows (30 populations): max |diff| %.2e (tolerance 1e-6)" % (TAG, worst))
    if worst > 1e-6:
        refuse("the planted D0 rows differ from the cache's rows by %.2e" % worst)
    s2 = SN.sigma_b2(np.array([vec[q] for q in ident]))
    out("%s sigma_b^2 (SIN-4, whole-corpus MAD over %d x 512 centred coordinates) = %.6g" % (TAG, len(ident), s2))
    cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
    sid, graph, byid, root = CPC.member(cfg, a.data_root)
    g12_path = a.g12_sites or os.path.join(a.data_root, G12_SITES_REL)
    gb = RO.git_blob_lf(g12_path)
    out("%s G12 sites %s blob %s %s; snapshot %s; sepBar %s; dropTop %s; whiten %s" % (
        TAG, g12_path, gb[:8], "OK" if gb == CPC.G12_SITES_BLOB else "MISMATCH", sid, cfg["sepBar"], cfg["dropTop"],
        cfg["whiten"]))
    if gb != CPC.G12_SITES_BLOB:
        refuse("G12_sites.csv blob %s is not the pinned %s" % (gb, CPC.G12_SITES_BLOB))
    if cfg["dropTop"] != 0 or cfg["whiten"] or cfg["sliceDim"] != 512:
        refuse("the member's splitter is not dropTop 0 / whiten false / slice 512: the proxy does not replicate it")
    nodes = [r["node_id"] for r in csv.DictReader(open(g12_path, newline="", encoding="utf-8"))]
    g12 = []
    for nid in nodes:
        if nid not in byid:
            refuse("G12 site %s is not in snapshot %s" % (nid, sid))
        ids = sorted(CPC.region_ids(byid, nid))
        kids = [sorted(CPC.region_ids(byid, c)) for c in (byid[nid].get("childIds") or []) if c in byid]
        if len(kids) < 2 or len(ids) < 2 * MCS:
            refuse("G12 site %s has %d children and %d items: not a splitter site" % (nid, len(kids), len(ids)))
        miss = [q for q in ids if q not in vec]
        if miss:
            refuse("G12 site %s: %d members are outside the IDENTITY rows" % (nid, len(miss)))
        g12.append(dict(node=nid, ids=ids, children=[set(k) for k in kids]))
    res.update(vec=vec, g12=g12, s2=s2, cfg=cfg, snapshot=sid)
    return res


def identity_sites(g12, vec):
    out = []
    for s in g12:
        pos = {q: i for i, q in enumerate(s["ids"])}
        out.append(dict(node=s["node"], X=np.array([vec[q] for q in s["ids"]]),
                        children=[{pos[q] for q in ch if q in pos} for ch in s["children"]]))
    return out


# ================================================================================================ the cache and the run
def script_pins():
    return {"cert_split_dip.py": RO.sha256_lf16(os.path.join(SELF_DIR, "cert_split_dip.py")),
            "si_null_triad.py": RO.sha256_lf16(os.path.join(SELF_DIR, "si_null_triad.py")),
            "cert_planted.py(blob)": CP_BLOB}


def make_meta(sites, s2, eps, extra=None):
    m = dict(test="CERT-SPLIT-DIP + SI-NULL-TRIAD", scripts=script_pins(), diptest=diptest_pins(), R=R_HALV, alpha=ALPHA,
             s_sims=SN.S_SIMS, g_n=SN.G_N, mcs=MCS, sep_bar=eps, sigma_b2=s2, set_hash=set_hash(sites),
             tasks=["%s|%s" % t for t in expected_tasks(sites)], numpy=np.__version__)
    m.update(extra or {})
    return m


def read_cache(path):
    meta, ident, done = None, None, {}
    if not os.path.isfile(path):
        return meta, ident, done
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue                     # a torn last line (killed mid-write) is ignored and recomputed
            if "meta" in r:
                meta = r["meta"]
            elif "identity" in r:
                ident = r["identity"]
            else:
                done[(r["site"], r["arm"])] = r["res"]
    return meta, ident, done


def append(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def compute_task(task):
    name, arm, X, k, u, mcs, eps, s2, sims, n_g = task
    if arm == "dip":
        r = dip_site(name, X, u)
        return name, arm, dict(p=r["p"], cert=r["cert"], cos09=r["cos09"], ps=[round(x, 6) for x in r["ps"]])
    out = SN.run_site_arms(name, X, k, mcs, eps, s2, (arm,), sims=sims, n_g=n_g)[arm]
    keep = {kk: out[kk] for kk in ("p", "cert", "status", "reached", "tau", "kept", "pairs", "k_proxy") if kk in out}
    return name, arm, keep


def run_tasks(sites, cache, meta, s2, eps, workers=1, identity_fn=None, sims=SN.S_SIMS, n_g=SN.G_N, out=print):
    """Pin / check the meta, run the identity precondition (once), then every missing (site, arm). -> (done, identity)."""
    old, ident, done = read_cache(cache)
    if old is None:
        os.makedirs(os.path.dirname(os.path.abspath(cache)), exist_ok=True)
        append(cache, {"meta": meta})
        out("%s cache %s: meta pinned at first launch (set hash %s...)" % (TAG, cache, meta["set_hash"][:16]))
    elif old != meta:
        bad = sorted(k for k in set(old) | set(meta) if old.get(k) != meta.get(k))
        refuse("the cache %s was pinned with a different meta (%s): refusing to mix runs" % (cache, ", ".join(bad)))
    else:
        out("%s cache %s: resuming, %d of %d tasks done" % (TAG, cache, len(done), len(meta["tasks"])))
    if ident is None and identity_fn is not None:
        ident = identity_fn()
        append(cache, {"identity": ident})
    triad_ok = ident is not None and ident.get("word") == "PASS"
    todo = [(n, a) for n, a in expected_tasks(sites) if (n, a) not in done and (a == "dip" or triad_ok)]
    if not triad_ok:
        out("%s SI-NULL-TRIAD leg REFUSED (identity precondition %s): S / G tasks not computed (SIN-3)" % (
            TAG, None if ident is None else ident.get("word")))
    order = {"SIZE": 0, "POWER": 1, "E1": 2, "E2": 3, "POS": 4}
    todo.sort(key=lambda t: (order.get(sites[t[0]]["cls"], 9), t))
    out("%s %d tasks to compute (%d workers)" % (TAG, len(todo), workers))
    tasks = [(n, a, sites[n]["X"], sites[n]["k"], sites[n]["u"], MCS, eps, s2, sims, n_g) for n, a in todo]
    t0 = time.time()
    it = map(compute_task, tasks) if workers <= 1 else None
    pool = None
    if it is None:
        from multiprocessing import Pool
        pool = Pool(workers)
        it = pool.imap_unordered(compute_task, tasks, chunksize=1)
    try:
        for i, (n, a, r) in enumerate(it):
            append(cache, {"site": n, "arm": a, "res": r})
            done[(n, a)] = r
            if (i + 1) % 50 == 0:
                out("%s   %d / %d  %.0f s" % (TAG, i + 1, len(tasks), time.time() - t0))
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    return done, ident


# ================================================================================================ the CERT-SPLIT-DIP readout
def _cert(done, name, arm="dip"):
    r = done.get((name, arm))
    return None if r is None else r.get("cert")


def sd0_word(k_size, k_d0):
    return bool(SN.size_ok_of(k_size, N_SIZE) and k_d0 <= 1)


def sd1_word(c):
    return "SENSITIVE" if c >= SD1_SENS else ("INSENSITIVE" if c <= SD1_INS else "MIXED")


def sd2_word(counts):
    hi = sum(1 for r in ROLES if counts[r] >= 4)
    lo = sum(1 for r in ROLES if counts[r] <= 1)
    return "POS-OK" if hi >= 2 else ("POS-FAIL" if lo >= 2 else "MIXED")


def icc_deff(groups):
    """groups: list of lists of 0/1 (equal size m). -> (icc or None, deff or None)."""
    k = len(groups)
    m = len(groups[0]) if groups else 0
    if k < 2 or m < 2:
        return None, None
    ys = np.array(groups, dtype=float)
    gm = ys.mean(axis=1)
    om = ys.mean()
    msb = m * float(((gm - om) ** 2).sum()) / (k - 1)
    msw = float(((ys - gm[:, None]) ** 2).sum()) / (k * (m - 1))
    den = msb + (m - 1) * msw
    if den <= 0.0:
        return None, None
    icc = (msb - msw) / den
    return icc, 1.0 + (m - 1) * icc


def band(x, b):
    return "HELD" if b[1] <= x <= b[2] else "FAILED"


def csd_readout(done, sites, rec_p, out=print, strict=True):
    """Every registered CERT-SPLIT-DIP line from the cache (strict: the registered denominators or REFUSED; a pilot / partial
    readout prints the same lines over what it has, under its NOT-of-record header). -> verdict dict."""
    v = {}
    out("CERT-SPLIT-DIP READOUT. %s" % REG)
    out(PILOT_LINE)
    for ln in LIKE:
        out(ln)
    size = [n for n, s in sites.items() if s["cls"] == "SIZE"]
    if strict and len(size) != N_SIZE:
        refuse("%d SIZE draws, not %d" % (len(size), N_SIZE))
    k_size = sum(1 for n in size if _cert(done, n) is True)
    d0_486 = ["CSD_%s_n486_d%d_D0" % (a, d) for a in ANCHORS for d in DRAWS]
    d0_441 = ["CSD_%s_n441_d%d_D0" % (a, d) for a in ANCHORS for d in DRAWS]
    k_d0 = sum(1 for n in d0_486 if _cert(done, n) is True)
    k_d0b = sum(1 for n in d0_441 if _cert(done, n) is True)
    up = SN.cp_upper(k_size, N_SIZE)
    sd0 = sd0_word(k_size, k_d0)
    v["sd0"] = "SIZE-OK" if sd0 else "ANTI-CONSERVATIVE"
    out("SD0 (gate): SIZE draws certified %d of %d (rate %.4f; 95%% CP upper %.4f; bars rate <= 0.10, upper <= 0.15); delta 0 "
        "certified %d of 15 at n 486 (bar <= 1; n 441 descriptive: %d of 15) -> %s" % (
            k_size, N_SIZE, k_size / N_SIZE, up, k_d0, k_d0b, v["sd0"]))
    out("SD0 FAILS (rule 8): SIZE-OK is refuted by >= 31 of 300 or >= 2 of 15: %s" % (
        "REFUTED" if (k_size >= 31 or k_d0 >= 2) else "not refuted"))
    dec = ["CSD_%s_n%d_d%d_j%d_D%s" % (a, n, d, j, DELTA_DEC) for a in ANCHORS for n in SIZES for d in DRAWS for j in PLANTS]
    if strict and len(dec) != N_SD1:
        refuse("SD1 holds %d sites, not %d" % (len(dec), N_SD1))
    c_dec = sum(1 for n in dec if _cert(done, n) is True)
    c486 = sum(1 for n in dec if "_n486_" in n and _cert(done, n) is True)
    rec6 = {n: sum(1 for a in ANCHORS for d in DRAWS if rec_p.get(CP.site_name(a, n, d, DELTA_DEC)) is True) for n in SIZES}
    if not sd0:
        v["sd1"] = "NOT EVALUABLE"
        out("SD1 (DECIDING, delta 6, fresh plants, n 486 + n 441 pooled): NOT EVALUABLE (SD0 ANTI-CONSERVATIVE); certified %d "
            "of %d printed, not scored" % (c_dec, N_SD1))
    else:
        v["sd1"] = sd1_word(c_dec)
        out("SD1 (DECIDING, delta 6, fresh plants, n 486 + n 441 pooled): certified %d of %d (n 486 %d of 30, n 441 %d of 30; "
            "bars SENSITIVE >= 45, INSENSITIVE <= 15) -> %s" % (c_dec, N_SD1, c486, c_dec - c486, v["sd1"]))
        out("SD1 FAILS (rule 8): SENSITIVE is refuted by <= 44 of 60: %s" % ("REFUTED" if c_dec <= 44 else "not refuted"))
        if v["sd1"] == "SENSITIVE":
            out(SENT_SENS + " (the plain site null of record at delta 6, record plants, READ from cpl_sites.csv: %d of 15 at "
                "n 486, %d of 15 at n 441)" % (rec6[486], rec6[441]))
        elif v["sd1"] == "INSENSITIVE":
            out("SD1 READING (INSENSITIVE): the rule does not certify fresh planted 2-way shifts at delta 6")
        else:
            out("SD1 READING (MIXED): neither SENSITIVE nor INSENSITIVE at delta 6")
    # support beside the deciding statistic
    groups = [[1 if _cert(done, "CSD_%s_n%d_d%d_j%d_D%s" % (a, n, d, j, DELTA_DEC)) is True else 0 for j in PLANTS]
              for a in ANCHORS for n in SIZES for d in DRAWS]
    icc, deff = icc_deff(groups)
    if deff is None:
        out("SUPPORT (SD1): declared DEFF %.1f (pilot assumption), n_eff %.0f, MDE80 %.3f; REALISED dependence: ICC undefined "
            "(no within- or between-subsample variation), DEFF not estimable" % (DEFF_DECL, NEFF_DECL, MDE_DECL))
    else:
        d_eff = max(1.0, deff)
        neff = N_SD1 / d_eff
        out("SUPPORT (SD1): declared DEFF %.1f (pilot assumption), n_eff %.0f, MDE80 %.3f; REALISED (CSD-6): ICC %.3f over 30 "
            "subsamples x 2 plants, DEFF %.3f, n_eff %.1f, MDE80 %.3f (printed beside; the verdict line is the registration's)" % (
                DEFF_DECL, NEFF_DECL, MDE_DECL, icc, d_eff, neff, 2.8 * math.sqrt(0.75 * 0.25 / neff)))
    # SD2
    pos = {r: sum(1 for d in DRAWS if _cert(done, "KK_%s_n486_d%d" % (r, d)) is True) for r in ROLES}
    v["sd2"] = sd2_word(pos)
    out("SD2 (positive control, merged pairs n 486): certified of 5 %s -> %s" % (pos, v["sd2"]))
    # elongation and F-SD
    el = [n for n, s in sites.items() if s["cls"] in ("E1", "E2")]
    if strict and len(el) != N_ELONG:
        refuse("%d elongation controls, not %d" % (len(el), N_ELONG))
    k_el = sum(1 for n in el if _cert(done, n) is True)
    k_e1 = sum(1 for n in el if sites[n]["cls"] == "E1" and _cert(done, n) is True)
    fire_e = k_el >= FSD_ELONG
    fire_i = v["sd1"] == "INSENSITIVE"
    v["fsd"] = bool(fire_e or fire_i)
    out("ELONGATION CONTROLS: certified %d of %d (E1 %d of 50, E2 %d of 20)" % (k_el, N_ELONG, k_e1, k_el - k_e1))
    out("F-SD: %s (elongation clause %d of 70 vs >= 8: %s; INSENSITIVE clause: %s)" % (
        "FIRED" if v["fsd"] else "NOT FIRED", k_el, "fires" if fire_e else "does not fire",
        "fires" if fire_i else "does not fire"))
    if fire_e:
        out(SENT_FSD_E)
    if fire_i:
        out(SENT_FSD_I)
    # descriptive: power curve, delta*, axis share
    out("DESCRIPTIVE power curve (fresh plants, certified of 30 per delta and size):")
    curve = {}
    for n in SIZES:
        row = {}
        for dl in DELTAS_CSD:
            names = (["CSD_%s_n%d_d%d_D0" % (a, n, d) for a in ANCHORS for d in DRAWS] if dl == "0" else
                     ["CSD_%s_n%d_d%d_j%d_D%s" % (a, n, d, j, dl) for a in ANCHORS for d in DRAWS for j in PLANTS])
            row[dl] = (sum(1 for x in names if _cert(done, x) is True), len(names))
        curve[n] = row
        out("  n %d: %s" % (n, "  ".join("D%s %d/%d" % (dl, c, t) for dl, (c, t) in row.items())))
    pooled = {dl: sum(1 for a in ANCHORS for n in SIZES for d in DRAWS for j in PLANTS
                      if _cert(done, "CSD_%s_n%d_d%d_j%d_D%s" % (a, n, d, j, dl)) is True) for dl in DELTAS_CSD[1:]}
    ds = {}
    for a in ANCHORS:
        ds[a] = NONE_WORD
        for dl in DELTAS_CSD[1:]:
            c = sum(1 for d in DRAWS for j in PLANTS if _cert(done, "CSD_%s_n486_d%d_j%d_D%s" % (a, d, j, dl)) is True)
            if c >= 8:
                ds[a] = dl
                break
    med = SN.median_ds(list(ds.values()), NONE_WORD, 10.0)
    out("DESCRIPTIVE delta* per category (n 486, >= 8 of 10; CSD-5): %s; median %s" % (ds, "> 10" if med == 11.0 else med))
    shares = {}
    for dl in DELTAS_CSD[1:]:
        xs = [done[(nm, "dip")]["cos09"] for nm in sites if sites[nm]["cls"] == "POWER" and sites[nm]["meta"].get("delta") == dl
              and (nm, "dip") in done and done[(nm, "dip")].get("cos09") is not None]
        shares[dl] = None if not xs else float(np.median(xs))
    out("DESCRIPTIVE share of halvings with |cos(A-axis, u)| > 0.9 (median over fresh-plant sites per delta): %s" % (
        {k: (None if x is None else round(x, 3)) for k, x in shares.items()}))
    for cls, label in (("POWER256", "(v) R256 power"), ("SIZE256", "(v) R256 SIZE"), ("E1_256", "(v) R256 E1"),
                       ("E2_256", "(v) R256 E2"), ("POS256", "(v) R256 merged pairs"), ("REC", "dip on CERT-PLANTED's record "
                                                                                         "plants (seen in the pilot)"),
                       ("RECX", "dip on SI-C1's delta 0.5 / 1 plants")):
        names = [n for n, s in sites.items() if s["cls"] == cls]
        if cls in ("POWER256", "REC", "RECX"):
            by = {}
            for n in names:
                key = "n%d D%s" % (sites[n]["meta"]["n"], sites[n]["meta"]["delta"])
                by.setdefault(key, [0, 0])
                by[key][0] += _cert(done, n) is True
                by[key][1] += 1
            out("DESCRIPTIVE %s: %s" % (label, "  ".join("%s %d/%d" % (k, c, t) for k, (c, t) in sorted(by.items()))))
        else:
            out("DESCRIPTIVE %s: certified %d of %d" % (label, sum(1 for n in names if _cert(done, n) is True), len(names)))
    out("DESCRIPTIVE (vi) the registered PC1 median-cut population = the STRONG / MID merged pairs (CSD-7; read from (iv), "
        "never scored): certified %d of 10" % (pos["STRONG"] + pos["MID"]))
    # predictions
    out("PREDICTIONS (words by Brier, counts by closed bands; HELD iff the point lies in the band):")
    out("  P1 SD0 SIZE-OK 0.95: Brier %.4f; SIZE rate %.4f vs [0.00, 0.02]: %s" % (
        (P1_P - (1.0 if sd0 else 0.0)) ** 2, k_size / N_SIZE, band(k_size / N_SIZE, P1_BAND)))
    if v["sd1"] == "NOT EVALUABLE":
        out("  P2 SD1 word: NOT SCORED (SD1 NOT EVALUABLE); certified at delta 6 %d vs [50, 60]: %s" % (c_dec, band(c_dec, P2_BAND)))
    else:
        b = sum((P2_P[w] - (1.0 if w == v["sd1"] else 0.0)) ** 2 for w in P2_P)
        out("  P2 SD1 SENSITIVE 0.90 / MIXED 0.08 / INSENSITIVE 0.02: outcome %s, Brier %.4f; certified at delta 6 %d vs "
            "[50, 60]: %s" % (v["sd1"], b, c_dec, band(c_dec, P2_BAND)))
    for dl, bd in P3_BANDS.items():
        out("  P3 certified of 60 at delta %s: %d vs [%d, %d]: %s" % (dl, pooled[dl], bd[1], bd[2], band(pooled[dl], bd)))
    out("  P4 SD2 POS-OK 0.95: outcome %s, Brier %.4f" % (v["sd2"], (P4_P - (1.0 if v["sd2"] == "POS-OK" else 0.0)) ** 2))
    out("  P5 elongation controls certified %d of 70 vs [0, 3]: %s" % (k_el, band(k_el, P5_BAND)))
    out("  P6 median delta* %s vs [4, 6]: %s" % ("> 10" if med == 11.0 else med, band(med, P6_BAND)))
    out(NOT_SHOW)
    v.update(k_size=k_size, k_d0=k_d0, c_dec=c_dec, pos=pos, k_el=k_el, med=med, pooled=pooled, curve=curve)
    return v


def sn_results(done, sites):
    """{site: {arm: {"cert": ..}}} for the triad readout (missing -> cert None)."""
    res = {}
    for n, s in sites.items():
        res[n] = {a: (done.get((n, a)) or {"cert": None}) for a in TRIAD}
    return res


# ================================================================================================ analyze (write-once)
def sites_from_meta(meta):
    """The task list pinned in the meta -> {name: {cls, arms, meta}} (classes and fields recovered from the names)."""
    sites = {}
    for t in meta["tasks"]:
        name, arm = t.split("|")
        s = sites.setdefault(name, dict(name=name, arms=[], cls=cls_of(name), meta=meta_of(name)))
        s["arms"].append(arm)
    return sites


def cls_of(name):
    for pre, cls in (("CSD256_", "POWER256"), ("CSD_", "POWER"), ("SIZE256_", "SIZE256"), ("SIZE_", "SIZE"),
                     ("E1_256_", "E1_256"), ("E1_", "E1"), ("E2_256_", "E2_256"), ("E2_", "E2"), ("KK256_", "POS256"),
                     ("KK_", "POS"), ("G12_", "G12")):
        if name.startswith(pre):
            return cls
    if name.startswith("PL_"):
        return "RECX" if name.split("_D")[-1] in SN.EXTRA_DELTAS else "REC"
    refuse("unknown site class of %s" % name)


def meta_of(name):
    m = {}
    for part in name.split("_"):
        if part.startswith("n") and part[1:].isdigit():
            m["n"] = int(part[1:])
        elif part.startswith("D") and part != "D":
            m["delta"] = part[1:]
    return m


def write_text(path, text, once=True):
    if once:
        try:
            with open(path, "x", encoding="utf-8", newline="\n") as f:
                f.write(text)
        except FileExistsError:
            refuse("%s exists: outcome files of record are write-once" % path)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def analyze(out_dir, rec_p, pilot=False, current_meta=None, out=print):
    cache = os.path.join(out_dir, "pilot_cache.jsonl" if pilot else "cache.jsonl")
    meta, ident, done = read_cache(cache)
    if meta is None:
        refuse("no cache at %s" % cache)
    if current_meta is not None and any(meta.get(k) != current_meta.get(k) for k in ("scripts", "diptest")):
        refuse("the cache was produced by other scripts / diptest than these (%s vs %s)" % (meta.get("scripts"),
                                                                                           current_meta.get("scripts")))
    sites = sites_from_meta(meta)
    want = [tuple(t.split("|")) for t in meta["tasks"]]
    triad_ok = ident is not None and ident.get("word") == "PASS"
    need = [t for t in want if t[1] == "dip" or triad_ok]
    missing = [t for t in need if t not in done]
    complete = not missing and not pilot
    suffix = "" if complete else ("_PILOT" if pilot else "_partial")
    buf = io.StringIO()

    def say(s):
        out(s)
        buf.write(s + "\n")
    say("pool: none (no DB opened; the cache %s)" % cache)
    say("%s cache meta: scripts %s; diptest %s; set hash %s...; tasks %d; done %d; missing %d%s" % (
        TAG, meta["scripts"], meta["diptest"], meta["set_hash"][:16], len(want), len(done), len(missing),
        "" if complete else " -> %s (NOT the outcome of record)" % suffix))
    v = csd_readout(done, sites, rec_p, out=say, strict=not pilot)
    rows = ["site,class,arm,p,cert,cos09"]
    for (n, a), r in sorted(done.items()):
        if a == "dip":
            rows.append("%s,%s,dip,%s,%s,%s" % (n, sites[n]["cls"] if n in sites else "", r.get("p"), r.get("cert"),
                                                r.get("cos09")))
    os.makedirs(out_dir, exist_ok=True)
    write_text(os.path.join(out_dir, CSD_OUT.replace(".txt", suffix + ".txt")), buf.getvalue(), once=complete)
    write_text(os.path.join(out_dir, CSD_CSV.replace(".csv", suffix + ".csv")), "\n".join(rows) + "\n", once=complete)
    buf2 = io.StringIO()

    def say2(s):
        out(s)
        buf2.write(s + "\n")
    say2("pool: none (no DB opened; the cache %s)" % cache)
    if ident is None:
        identity = ("NOT RUN", 0.0, [])
    else:
        identity = (ident["word"], ident["pooled"], ident.get("rows", []))
    v2 = SN.readout(sn_results(done, sites), rec_p, identity, out=say2)
    rows2 = ["site,arm,p,cert,status"]
    for (n, a), r in sorted(done.items()):
        if a != "dip":
            rows2.append("%s,%s,%s,%s,%s" % (n, a, r.get("p"), r.get("cert"), str(r.get("status", "")).replace(",", ";")))
    write_text(os.path.join(out_dir, SN_OUT.replace(".txt", suffix + ".txt")), buf2.getvalue(), once=complete)
    write_text(os.path.join(out_dir, SN_CSV.replace(".csv", suffix + ".csv")), "\n".join(rows2) + "\n", once=complete)
    return v, v2, complete


# ================================================================================================ modes
def heavy_check():
    CPC.heavy_check()


def parse_args(argv):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("--selftest", "--selftest-io", "--mutants", "--smoke", "--dry-run", "--run", "--analyze"):
        g.add_argument(m, action="store_true")
    ap.add_argument("--data-root", default=os.environ.get("TAXOARENA_DATA_ROOT", ROOT))
    ap.add_argument("--planted-dir", default=PLANTED_DIR_DEFAULT)
    ap.add_argument("--kk-labels", default=KK_LABELS_DEFAULT)
    ap.add_argument("--g12-sites", default=None)
    ap.add_argument("--out", default=os.path.join(ROOT, OUT_REL))
    ap.add_argument("--pylib", default=None)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--pilot", type=int, default=0)
    return ap.parse_args(argv)


ASSEMBLE = {}


def assemble(a, out=print):
    if "fn" in ASSEMBLE:
        return ASSEMBLE["fn"](a, out)
    inp = load_inputs(a, out=out)
    sites = build_sites(inp["planted"], inp["kk"], inp["vec"], inp["g12"])
    eps = float(inp["cfg"]["sepBar"])

    def identity_fn():
        word, pooled, rows = SN.identity_check(identity_sites(inp["g12"], inp["vec"]), MCS, eps, out=out)
        return dict(word=word, pooled=float(pooled), rows=[list(r) for r in rows])
    return dict(sites=sites, s2=inp["s2"], eps=eps, rec_p=inp["rec_p"], identity_fn=identity_fn, pins=inp["pins"])


def pilot_subset(sites, n):
    keep, seen = {}, {}
    for name, s in sites.items():
        c = seen.get(s["cls"], 0)
        if c < n:
            keep[name] = s
            seen[s["cls"]] = c + 1
    return keep


def counts_line(sites):
    by = {}
    for s in sites.values():
        by.setdefault(s["cls"], [0, 0])
        by[s["cls"]][0] += 1
        by[s["cls"]][1] += len(s["arms"])
    return "  ".join("%s %d sites / %d tasks" % (c, a, b) for c, (a, b) in sorted(by.items()))


def estimate(sites, s2, eps, out=print):
    """Time one dip site, one S site and one G site at reduced counts; extrapolate per class."""
    some = next(s for s in sites.values() if s["cls"] == "POWER" and s["meta"].get("delta") == DELTA_DEC)
    t0 = time.time()
    dip_site(some["name"], some["X"], some["u"])
    t_dip = time.time() - t0
    t0 = time.time()
    SN.run_site_arms(some["name"], some["X"], 2, MCS, eps, s2, ("S",), sims=100)
    t_s = (time.time() - t0) * SN.S_SIMS / 100.0
    t0 = time.time()
    SN.run_site_arms(some["name"], some["X"], 2, MCS, eps, s2, ("G_I",), n_g=200)
    t_g = (time.time() - t0) * SN.G_N / 200.0
    n_dip = sum(1 for s in sites.values() if "dip" in s["arms"])
    n_s = sum(1 for s in sites.values() if "S" in s["arms"])
    n_g = sum(1 for s in sites.values() for a in s["arms"] if a.startswith("G_"))
    tot = n_dip * t_dip + n_s * t_s + n_g * t_g
    out("%s RUNTIME ESTIMATE (one n-%d site timed): dip %.1f s x %d, S %.1f s x %d, G %.1f s x %d -> %.1f h single-process "
        "(G12's larger sites cost more)" % (TAG, len(some["X"]), t_dip, n_dip, t_s, n_s, t_g, n_g, tot / 3600.0))
    return tot


def main(argv=None):
    a = parse_args(argv)
    load_diptest(a.pylib)
    if a.selftest:
        return selftest()
    if a.selftest_io:
        return selftest_io(a.g12_sites or os.path.join(a.data_root, G12_SITES_REL), a.planted_dir, a.kk_labels)
    if a.mutants:
        return mutants()
    if a.smoke:
        return smoke(a)
    if a.dry_run:
        print("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode READS embeddings_cache.db (TRAIN "
              "ids only) and snapshots.db, mode=ro&immutable=1; no EVAL table; writes nothing")
        if not _IN_SELFTEST:
            heavy_check()
        A = assemble(a)
        print("%s diptest %s; scripts %s" % (TAG, diptest_pins(), script_pins()))
        print("%s sites: %s" % (TAG, counts_line(A["sites"])))
        print("%s set hash %s; tasks %d" % (TAG, set_hash(A["sites"]), len(expected_tasks(A["sites"]))))
        A["identity_fn"]()
        estimate(A["sites"], A["s2"], A["eps"])
        print("%s DRY RUN: nothing written; no verdict" % TAG)
        return 0
    if a.run:
        print("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); a POOL READER (rule 7): busy.ps1 exit 1 "
              "immediately before this launch")
        if not _IN_SELFTEST:
            heavy_check()
            if selftest() != 0:
                refuse("the selftest is red: no run")
        A = assemble(a)
        sites = pilot_subset(A["sites"], a.pilot) if a.pilot else A["sites"]
        meta = make_meta(sites, A["s2"], A["eps"], {"pilot": a.pilot})
        cache = os.path.join(a.out, "pilot_cache.jsonl" if a.pilot else "cache.jsonl")
        run_tasks(sites, cache, meta, A["s2"], A["eps"], a.workers, A["identity_fn"])
        print("%s run finished; next: --analyze%s" % (TAG, " --pilot %d" % a.pilot if a.pilot else ""))
        return 0
    if a.analyze:
        if not _IN_SELFTEST and selftest() != 0:
            refuse("the selftest is red: no readout")
        cp_csv = os.path.join(a.planted_dir, "cpl_sites.csv")
        got = sha256_file(cp_csv)
        if got != CPL_CSV_SHA256:
            refuse("cpl_sites.csv sha256 %s is not the pinned %s" % (got, CPL_CSV_SHA256))
        analyze(a.out, read_record_p(cp_csv), pilot=bool(a.pilot),
                current_meta=dict(scripts=script_pins(), diptest=diptest_pins()))
        return 0
    return 2


def smoke(a):
    """NO DB: two record plants (seen in the pilot) through the dip rule; one S / G site at reduced counts; timings."""
    print("pool: none (no DB opened; CERT-PLANTED's planted files on E: only). SMOKE: not evidence; record plants were seen in "
          "the pilot")
    inp = load_inputs(a, with_db=False)
    for s in ("PL_math_n486_d1_D0", "PL_math_n486_d1_D6"):
        ids, y32 = inp["planted"][s]
        t0 = time.time()
        r = dip_site(s, rows512(y32))
        print("%s SMOKE dip %s: p_site %.4g cert %s (%.1f s)" % (TAG, s, r["p"], r["cert"], time.time() - t0))
    ids, y32 = inp["planted"]["PL_math_n486_d1_D6"]
    X = rows512(y32)
    s2 = SN.sigma_b2(X)
    t0 = time.time()
    r = SN.run_site_arms("smoke", X, 2, MCS, 0.0145, s2, TRIAD, sims=100, n_g=200)
    print("%s SMOKE S (100 sims) / G (200) on PL_math_n486_d1_D6 with sigma_b^2 from the site itself (smoke only): %s (%.1f s)" % (
        TAG, {k: (round(x["p"], 4) if x["p"] is not None else None, x["status"]) for k, x in r.items()}, time.time() - t0))
    return 0


# ================================================================================================ selftest
def _cls_sites():
    """A synthetic site table with the registered names and classes (no rows)."""
    S = {}

    def put(name, cls, **m):
        S[name] = dict(name=name, cls=cls, arms=("dip",) + TRIAD, meta=m, k=2, u=None, X=None)
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                put("CSD_%s_n%d_d%d_D0" % (a, n, d), "POWER", n=n, delta="0")
                for j in PLANTS:
                    for dl in DELTAS_CSD[1:]:
                        put("CSD_%s_n%d_d%d_j%d_D%s" % (a, n, d, j, dl), "POWER", n=n, delta=dl)
                for dl in CP.DELTAS + SN.EXTRA_DELTAS:
                    put(CP.site_name(a, n, d, dl), "RECX" if dl in SN.EXTRA_DELTAS else "REC", n=n, delta=dl)
        for n in SIZES:
            for g in range(SN.SIZE_PER_CELL):
                put("SIZE_%s_n%d_g%d" % (a, n, g), "SIZE", n=n)
    for role in E1_ROLES:
        for d in DRAWS:
            for g in range(E1_PER):
                put("E1_%s_n486_d%d_g%d" % (role, d, g), "E1", n=486)
    for r in E2_RATIOS:
        for g in range(E2_PER):
            put("E2_r%d_g%d" % (r, g), "E2", n=486)
    for role in ROLES:
        for d in DRAWS:
            put("KK_%s_n486_d%d" % (role, d), "POS", n=486)
    return S


def _done(S, cert_fn, triad_fn=None):
    done = {}
    for n, s in S.items():
        done[(n, "dip")] = dict(p=0.01 if cert_fn(n, s) else 0.5, cert=bool(cert_fn(n, s)), cos09=1.0)
        if triad_fn:
            for arm in TRIAD:
                c = triad_fn(n, s, arm)
                done[(n, arm)] = dict(p=None if c is None else (0.01 if c else 0.5), cert=c, status="OK")
    return done


def _power_cert(n_cert_by_delta):
    """cert_fn certifying, per delta, the first k fresh-plant sites in name order (both sizes)."""
    order = {}

    def fn(name, s):
        if s["cls"] != "POWER" or name.endswith("_D0"):
            return False
        dl = s["meta"]["delta"]
        k = n_cert_by_delta.get(dl, 0)
        lst = order.setdefault(dl, sorted(x for x, t in _ALL.items() if t["cls"] == "POWER" and t["meta"]["delta"] == dl
                                          and not x.endswith("_D0")))
        return lst.index(name) < k
    return fn


_ALL = _cls_sites()


def _readout(S, done, rec_p=None):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        v = csd_readout(done, S, rec_p or {}, out=print)
    return v, buf.getvalue()


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    SN_CASES = []
    fails = []

    def case(name, fn):
        try:
            fn()
            print("  PASS %s" % name)
        except BaseException as e:   # noqa: BLE001  (SystemExit from refuse included)
            fails.append(name)
            print("  FAIL %s: %r" % (name, e))
    print("%s SELFTEST (fixtures; zero calls; no DB)" % TAG)
    S = _ALL

    # ---- the rule
    def rule_bimodal():
        rng = np.random.default_rng(5)
        m = rng.normal(size=64)
        m /= np.linalg.norm(m)
        u = rng.normal(size=64)
        u -= (u @ m) * m
        u /= np.linalg.norm(u)
        X = m + rng.normal(size=(300, 64)) * 0.02
        X[:150] += 0.15 * u
        X[150:] -= 0.15 * u
        r = dip_site("bi", X, u)
        assert r["cert"] is True and r["p"] <= 0.05 and r["cos09"] == 1.0, r
        Y = m + rng.normal(size=(300, 64)) * 0.02
        r2 = dip_site("uni", Y)
        assert r2["cert"] is False and r2["p"] > 0.05, r2
        assert dip_site("uni", Y)["p"] == r2["p"]                       # deterministic in the name
        assert dip_site("uni2", Y)["ps"] != r2["ps"]                    # the name seeds the halvings
    case("rule: bimodal certifies, unimodal does not, seeds follow the name", rule_bimodal)

    def rule_combine():
        assert abs(combine([0.01] * 10 + [0.9] * 10) - 0.91) < 1e-12
        assert combine([0.02] * 11 + [0.9] * 9) == 0.04
        assert combine([0.03] * 11 + [0.9] * 9) == 0.06
        assert combine([0.9] * 20) == 1.0
        assert certified(0.05) is True and certified(0.05 + 1e-12) is False
        assert SN.certified(0.05) is True and SN.certified(0.05 + 1e-12) is False
        assert halving_seed("abc", 3) == int(hashlib.sha256(b"abc").hexdigest(), 16) % 2 ** 32 + 3
    case("rule: 2 x median (not min, not mean), cap 1, halving seed formula", rule_combine)

    def rule_degenerate():
        X = np.tile(np.eye(8)[0], (40, 1))
        r = dip_site("deg", X)
        assert r["p"] == 1.0 and r["cert"] is False and all(p == 1.0 for p in r["ps"])
    case("rule: all restarts degenerate -> p 1 per halving (CSD-1)", rule_degenerate)

    # ---- the CERT-SPLIT-DIP readout on synthetic caches
    def base(n_cert=None, size_k=0, d0=0, pos=(5, 5, 5), el=(0, 0), d0b=0):
        n_cert = n_cert or {}
        size_names = sorted(x for x, t in S.items() if t["cls"] == "SIZE")
        el1 = sorted(x for x, t in S.items() if t["cls"] == "E1")
        el2 = sorted(x for x, t in S.items() if t["cls"] == "E2")
        d0n = ["CSD_%s_n486_d%d_D0" % (a, d) for a in ANCHORS for d in DRAWS]
        d0nb = ["CSD_%s_n441_d%d_D0" % (a, d) for a in ANCHORS for d in DRAWS]
        pf = _power_cert(n_cert)

        def fn(name, s):
            if s["cls"] == "SIZE":
                return size_names.index(name) < size_k
            if s["cls"] == "E1":
                return el1.index(name) < el[0]
            if s["cls"] == "E2":
                return el2.index(name) < el[1]
            if s["cls"] == "POS":
                role = name.split("_")[1]
                return int(name[-1]) <= pos[ROLES.index(role)]
            if name in d0n:
                return d0n.index(name) < d0
            if name in d0nb:
                return d0nb.index(name) < d0b
            return pf(name, s)
        return _done(S, fn)

    def sd1_bounds():
        for k, word in ((45, "SENSITIVE"), (44, "MIXED"), (16, "MIXED"), (15, "INSENSITIVE"), (60, "SENSITIVE"), (0, "INSENSITIVE")):
            v, txt = _readout(S, base({"6": k}))
            assert v["sd1"] == word, (k, v["sd1"])
            assert "certified %d of 60" % k in txt and "-> %s" % word in txt, txt
        v, txt = _readout(S, base({"6": 45}))
        assert "n 486 20 of 30, n 441 25 of 30" in txt, txt               # pooled over BOTH sizes
        assert "SD1 FAILS (rule 8): SENSITIVE is refuted by <= 44 of 60: not refuted" in txt
        assert SENT_SENS in txt
        v, txt = _readout(S, base({"6": 44}))
        assert "SD1 FAILS (rule 8): SENSITIVE is refuted by <= 44 of 60: REFUTED" in txt
        assert "SD1 READING (MIXED)" in txt
        v, txt = _readout(S, base({"6": 15}))
        assert "SD1 READING (INSENSITIVE)" in txt and SENT_FSD_I in txt and v["fsd"] is True
    case("SD1: 45 / 44 / 16 / 15 boundaries, pooled sizes, FAILS line, readings", sd1_bounds)

    def sd1_rec_sentence():
        rec = {CP.site_name(a, n, d, "6"): (n == 486 and a == "math" and d == 1) for a in ANCHORS for n in SIZES for d in DRAWS}
        v, txt = _readout(S, base({"6": 50}), rec)
        assert "READ from cpl_sites.csv: 1 of 15 at n 486, 0 of 15 at n 441" in txt, txt
    case("SD1: the record's delta-6 counts are READ per size", sd1_rec_sentence)

    def sd0_bounds():
        v, txt = _readout(S, base({"6": 60}, size_k=30))
        assert v["sd0"] == "SIZE-OK" and "SIZE draws certified 30 of 300" in txt and v["sd1"] == "SENSITIVE"
        assert "SD0 FAILS (rule 8): SIZE-OK is refuted by >= 31 of 300 or >= 2 of 15: not refuted" in txt
        v, txt = _readout(S, base({"6": 60}, size_k=31))
        assert v["sd0"] == "ANTI-CONSERVATIVE" and v["sd1"] == "NOT EVALUABLE" and "SD1 (DECIDING" in txt
        assert "NOT EVALUABLE (SD0 ANTI-CONSERVATIVE); certified 60 of 60 printed, not scored" in txt
        assert "P2 SD1 word: NOT SCORED" in txt and "REFUTED" in txt
        v, txt = _readout(S, base({"6": 60}, d0=1))
        assert v["sd0"] == "SIZE-OK" and "delta 0 certified 1 of 15 at n 486" in txt
        v, txt = _readout(S, base({"6": 60}, d0=2))
        assert v["sd0"] == "ANTI-CONSERVATIVE"
        v, txt = _readout(S, base({"6": 60}, d0b=15))
        assert v["sd0"] == "SIZE-OK" and "n 441 descriptive: 15 of 15" in txt   # n 441 never gates
        v, txt = _readout(S, base({"6": 60}, size_k=300))
        assert "SIZE draws certified 300 of 300 (rate 1.0000" in txt          # every draw counted
        v, txt = _readout(S, base({"6": 10}, size_k=31))
        assert v["fsd"] is False                                            # INSENSITIVE clause needs an evaluable SD1
    case("SD0: 30 / 31 of 300, 1 / 2 of 15 at n 486 only; NOT EVALUABLE path", sd0_bounds)

    def sd0_upper_bound():
        # rate <= 0.10 alone is not enough: the CP upper bound must also be <= 0.15 (both at 300 draws)
        assert SN.size_ok_of(30, 300) is True and SN.size_ok_of(31, 300) is False
        assert SN.cp_upper(30, 300) <= 0.15 and SN.cp_upper(31, 300) > SN.cp_upper(30, 300)
        assert SN.size_ok_of(1, 10) is False                                 # rate 0.10 but upper 0.445
    case("SD0 / SA1: the CP upper bound is a separate bar", sd0_upper_bound)

    def sd2_words():
        for pos, w in (((4, 4, 0), "POS-OK"), ((5, 3, 4), "POS-OK"), ((1, 1, 5), "POS-FAIL"), ((4, 3, 1), "MIXED"),
                       ((3, 3, 3), "MIXED"), ((0, 5, 1), "POS-FAIL"), ((4, 1, 0), "POS-FAIL")):
            v, txt = _readout(S, base({"6": 60}, pos=pos))
            assert v["sd2"] == w, (pos, v["sd2"])
            assert "-> %s" % w in txt
    case("SD2: POS-OK / POS-FAIL / MIXED over the 3 pairs", sd2_words)

    def fsd():
        v, txt = _readout(S, base({"6": 60}, el=(7, 0)))
        assert v["fsd"] is False and "certified 7 of 70" in txt and "F-SD: NOT FIRED" in txt
        v, txt = _readout(S, base({"6": 60}, el=(0, 8)))
        assert v["fsd"] is True and SENT_FSD_E in txt and "(E1 0 of 50, E2 8 of 20)" in txt
        v, txt = _readout(S, base({"6": 60}, el=(4, 4)))
        assert v["fsd"] is True and "certified 8 of 70" in txt                # E1 and E2 pooled
        v, txt = _readout(S, base({"6": 60}, el=(8, 0)))
        assert v["fsd"] is True and "(E1 8 of 50, E2 0 of 20)" in txt
    case("F-SD: 7 / 8 of 70 over E1 + E2; INSENSITIVE clause (above)", fsd)

    def preds():
        v, txt = _readout(S, base({"3": 9, "4": 25, "6": 58, "8": 56}, size_k=6))
        assert "SIZE rate 0.0200 vs [0.00, 0.02]: HELD" in txt
        assert "Brier %.4f" % ((0.95 - 1.0) ** 2) in txt
        b = (0.90 - 1) ** 2 + 0.08 ** 2 + 0.02 ** 2
        assert "outcome SENSITIVE, Brier %.4f; certified at delta 6 58 vs [50, 60]: HELD" % b in txt
        assert "delta 3: 9 vs [0, 8]: FAILED" in txt and "delta 4: 25 vs [3, 25]: HELD" in txt
        assert "delta 8: 56 vs [57, 60]: FAILED" in txt
        v, txt = _readout(S, base({"6": 49}))
        assert "certified at delta 6 49 vs [50, 60]: FAILED" in txt
        v, txt = _readout(S, base({"6": 50}))
        assert "certified at delta 6 50 vs [50, 60]: HELD" in txt
        v, txt = _readout(S, base({"6": 60}, size_k=7))
        assert "SIZE rate 0.0233 vs [0.00, 0.02]: FAILED" in txt
        v, txt = _readout(S, base({"6": 60}, pos=(1, 1, 1), el=(3, 0)))
        assert "P4 SD2 POS-OK 0.95: outcome POS-FAIL, Brier %.4f" % (0.95 ** 2) in txt
        assert "P5 elongation controls certified 3 of 70 vs [0, 3]: HELD" in txt
    case("predictions P1-P5: bands and Brier values", preds)

    def dstar():
        # economics reaches 8 of 10 (n 486) at delta 4, math at 6, physics never -> median 6; n 441 sites ignored
        fn_cert = {}
        for a, dl in (("economics", "4"), ("math", "6")):
            for d in DRAWS:
                for j in PLANTS:
                    for dd in DELTAS_CSD[DELTAS_CSD.index(dl):]:
                        fn_cert["CSD_%s_n486_d%d_j%d_D%s" % (a, d, j, dd)] = (d <= 4)
        for d in DRAWS:
            for j in PLANTS:
                fn_cert["CSD_physics_n441_d%d_j%d_D2" % (d, j)] = True
        done = _done(S, lambda n, s: fn_cert.get(n, False))
        v, txt = _readout(S, done)
        assert "{'economics': '4', 'math': '6', 'physics': '> 10'}; median 6.0" in txt, txt
        assert "P6 median delta* 6.0 vs [4, 6]: HELD" in txt
        for a in ANCHORS:
            for d in DRAWS:
                for j in PLANTS:
                    fn_cert["CSD_%s_n486_d%d_j%d_D10" % (a, d, j)] = False
        fn_cert.update({k: False for k in fn_cert if "economics" in k or "math" in k})
        v, txt = _readout(S, _done(S, lambda n, s: fn_cert.get(n, False)))
        assert "median > 10" in txt and "P6 median delta* > 10 vs [4, 6]: FAILED" in txt
        # 7 of 10 is not enough
        fc = {"CSD_economics_n486_d%d_j%d_D2" % (d, j): (d <= 3 or (d == 4 and j == 1)) for d in DRAWS for j in PLANTS}
        v, txt = _readout(S, _done(S, lambda n, s: fc.get(n, False)))
        assert "'economics': '> 10'" in txt
    case("delta* per category (>= 8 of 10, n 486) and P6", dstar)

    def support():
        groups = [[1, 1]] * 15 + [[0, 0]] * 15
        icc, deff = icc_deff(groups)
        assert abs(icc - 1.0) < 1e-12 and abs(deff - 2.0) < 1e-12
        icc, deff = icc_deff([[1, 0]] * 30)
        assert icc < 0 and deff < 1.0
        v, txt = _readout(S, base({"6": 30}))
        assert "REALISED (CSD-6)" in txt and "declared DEFF 1.5" in txt
        assert icc_deff([[1, 1]] * 30) == (None, None)
        v, txt = _readout(S, base({"6": 60}))
        assert "ICC undefined" in txt
    case("support: realised ICC / DEFF beside the declared 1.5", support)

    def classes_counts():
        bad = dict(S)
        bad.pop(sorted(x for x, t in S.items() if t["cls"] == "E2")[0])
        try:
            _readout(bad, base({"6": 60}))
            raise AssertionError("69 elongation controls accepted")
        except SystemExit:
            pass
        bad = dict(S)
        bad.pop(sorted(x for x, t in S.items() if t["cls"] == "SIZE")[0])
        try:
            _readout(bad, base({"6": 60}))
            raise AssertionError("299 SIZE draws accepted")
        except SystemExit:
            pass
    case("denominators: 300 SIZE and 70 elongation sites or REFUSED", classes_counts)

    # ---- SI-NULL-TRIAD: the proxy, arms and readout
    def java_random():
        r = SN.JavaRandom(42)
        assert r.next_double() == 0.7275636800328681 and r.next_double() == 0.6832234717598454
        assert SN.JavaRandom(42).next(32) == -1170105035                    # new Random(42).nextInt()
    case("proxy: java.util.Random replica (Random(42) published nextDouble x 2 and nextInt)", java_random)

    def em_two_impls():
        rng = np.random.default_rng(3)
        Z = SN.norm_rows(rng.standard_normal((6, 200, 16)) * np.linspace(3, 1, 16))
        for k in (2, 3):
            R1, ok1 = SN.vmf_em_many(Z, k, 20 / 200)
            R2, ok2 = SN.vmf_em_batch(Z, k, 20 / 200)
            assert (ok1 == ok2).all() and np.abs(R1 - R2).max() < 1e-10, np.abs(R1 - R2).max()
        R, ok = SN.vmf_em_many(Z[:1], 2, 0.6)
        assert not ok[0]                                                     # collapse (soft count < 0.6 n)
    case("proxy: numba EM == numpy EM (k 2 / 3), collapse", em_two_impls)

    def kappa_fns():
        assert SN.corrected_kappa(np.array([1.0]), 64, np.array([10.0]))[0] == 1e4
        assert SN.corrected_kappa(np.array([0.0]), 64, np.array([10.0]))[0] == 1e-3
        k = SN.corrected_kappa(np.array([0.5]), 64, np.array([100.0]))[0]
        assert 10 < k < 100
        assert abs(SN.log_gamma(5.0) - math.log(24.0)) < 1e-9
    case("proxy: correctedKappa caps / shrinkage, logGamma", kappa_fns)

    def identity_fx():
        rng = np.random.default_rng(11)
        m = rng.normal(size=64)
        m /= np.linalg.norm(m)
        u = rng.normal(size=64)
        u -= (u @ m) * m
        u /= np.linalg.norm(u)
        X = m + rng.normal(size=(240, 64)) * 0.02
        X[:120] += 0.2 * u
        X[120:] -= 0.2 * u
        X = unit(X)
        good = dict(node="a", X=X, children=[set(range(120)), set(range(120, 240))])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            w, pooled, rows = SN.identity_check([good, good], 20, 0.0145, out=print)
        assert w == "PASS" and pooled == 1 and "pooled item agreement 480 / 480 = 1.0000" in buf.getvalue()
        bad = dict(node="b", X=X, children=[set(range(0, 240, 2)), set(range(1, 240, 2))])
        with contextlib.redirect_stdout(io.StringIO()):
            w, pooled, rows = SN.identity_check([good, bad], 20, 0.0145, out=print)
        assert w == "FAIL" and abs(float(pooled) - (240 + 120) / 480) < 1e-12, pooled
        for moved, word in ((7, "FAIL"), (4, "PASS")):                    # 473 / 480 = 0.9854; 476 / 480 = 0.9917
            near = dict(node="c", X=X, children=[set(range(120 - moved)), set(range(120 - moved, 240))])
            with contextlib.redirect_stdout(io.StringIO()):
                w, pooled, rows = SN.identity_check([good, near], 20, 0.0145, out=print)
            assert w == word and pooled == Fraction(480 - moved, 480), (moved, w, pooled)
        assert SN.agreement([np.arange(10), np.arange(10, 20)], [set(range(10, 20)), set(range(10))]) == 20
        assert SN.agreement([np.arange(5), np.arange(5, 10), np.arange(10, 12)], [set(range(12))]) == 5
    case("identity precondition: PASS at 1.0, FAIL at 0.75, permutation matching", identity_fx)

    def arms_fx():
        rng = np.random.default_rng(21)
        m = rng.normal(size=128)
        m /= np.linalg.norm(m)
        iso = unit(m + rng.normal(size=(300, 128)) * 0.03)
        s2 = SN.sigma_b2(unit(m + rng.normal(size=(2000, 128)) * 0.03))
        u = rng.normal(size=128)
        u -= (u @ m) * m
        u /= np.linalg.norm(u)
        pl = m + rng.normal(size=(300, 128)) * 0.03
        pl[:150] += 0.12 * u
        pl[150:] -= 0.12 * u
        pl = unit(pl)
        r_iso = SN.run_site_arms("iso", iso, 2, 30, 0.0145, s2, TRIAD, sims=80, n_g=120)
        r_pl = SN.run_site_arms("pl", pl, 2, 30, 0.0145, s2, TRIAD, sims=80, n_g=120)
        for arm in TRIAD:
            assert r_pl[arm]["cert"] is True, (arm, r_pl[arm])
        assert r_iso["S"]["cert"] is False and r_iso["G_S"]["cert"] is False, r_iso
        assert r_pl["S"]["p"] == 1.0 / 81.0, r_pl["S"]                      # (1 + 0) / (1 + 80): the registered form
        SN_CASES.append((r_iso, r_pl))
        # an elongated unimodal cloud: G with sigma_b^2 I certifies the elongation, G with S's matrix and S do not; the S value
        # is a golden pin of the registered form on this seeded fixture (cluster index on the un-normalised simulated rows)
        rng = np.random.default_rng(21)
        m = rng.normal(size=128)
        m /= np.linalg.norm(m)
        rng.normal(size=(2300, 128))
        e = rng.normal(size=128)
        e -= (e @ m) * m
        e /= np.linalg.norm(e)
        Z = rng.normal(size=(300, 128)) * 0.03
        Z += np.outer(Z @ e, e) * 5.0
        r_el = SN.run_site_arms("el", unit(m + Z), 2, 30, 0.0145, s2, TRIAD, sims=80, n_g=120)
        assert r_el["G_I"]["cert"] is True and r_el["G_S"]["cert"] is False and r_el["S"]["cert"] is False, r_el
        assert r_el["S"]["reached"] == 80 and r_el["S"]["k_le"] == 48 and r_el["S"]["p"] == 49.0 / 81.0, r_el["S"]
    case("arms: S / G_I / G_S certify a planted 2-way cloud; S and G_S do not certify an isotropic cloud", arms_fx)

    def g_holm():
        rng = np.random.default_rng(31)
        m = rng.normal(size=64)
        m /= np.linalg.norm(m)
        Q = np.linalg.qr(rng.normal(size=(64, 3)))[0]
        X = m + rng.normal(size=(360, 64)) * 0.02
        X[:120] += 0.15 * Q[:, 0]
        X[120:240] += 0.15 * Q[:, 1]
        X[240:] += 0.15 * Q[:, 2]
        X = unit(X)
        r = SN.run_site_arms("k3", X, 3, 30, 0.0145, 4e-4, ("G_I",), n_g=60)["G_I"]
        assert r["pairs"] == 3 and r["k_proxy"] == 3, r
        assert r["p"] == min(1.0, 3 * min(r["p_pairs"])) and r["p"] != min(r["p_pairs"]), r
    case("G at k = 3: all 3 sibling pairs, Holm's first step (3 x min p)", g_holm)

    def s_reached_floor():
        site = SN.Site(unit(np.random.default_rng(2).normal(size=(120, 16))), 55, 0.0145, 2)
        r = SN.s_arm(site, 1e-3, np.random.default_rng(0), sims=20)
        assert r["p"] is None and r["status"].startswith("NE:"), r
    case("S: NOT EVALUABLE when the proxy has no partition / too few simulations reach one", s_reached_floor)

    def soft_thr():
        lt, tau = SN.soft_threshold(np.array([5.0, 1.0, 0.0, 0.0]), 1.0)
        assert abs(lt.sum() - 6.0) < 1e-9 and abs(tau - 2.0) < 1e-6 and list(np.round(lt, 6)) == [3.0, 1.0, 1.0, 1.0]
        lt, tau = SN.soft_threshold(np.array([1.0, 1.0]), 2.0)
        assert tau == float("inf") and list(lt) == [2.0, 2.0]
        lt, tau = SN.soft_threshold(np.array([3.0, 2.0]), 1.0)
        assert tau == 0.0 and list(lt) == [3.0, 2.0]
    case("S: soft threshold preserves total power (tau 2), inf and 0 cases", soft_thr)

    # SI readout fixtures
    def sn_fixture(size_k=None, d2=None, p_d2=0, ne=None):
        """size_k: {arm: certified of 300}; d2: {arm: per-anchor count at delta 2 n 486}; p_d2: P's per-anchor count."""
        size_k = size_k or {}
        d2 = d2 or {}
        res = {}
        for n, s in S.items():
            res[n] = {}
            for arm in TRIAD:
                c = False
                if s["cls"] == "SIZE":
                    idx = sorted(x for x, t in S.items() if t["cls"] == "SIZE").index(n)
                    c = idx < size_k.get(arm, 0)
                elif n.startswith("PL_") and n.endswith("_D2") and "_n486_" in n:
                    a = n.split("_")[1]
                    d = int(n.split("_")[3][1:])
                    c = d <= d2.get(arm, {}).get(a, 0)
                if ne and (n, arm) in ne:
                    c = None
                res[n][arm] = {"cert": c}
        rec = {CP.site_name(a, nn, d, dl): (dl == "2" and nn == 486 and d <= p_d2) for a in ANCHORS for nn in SIZES
               for d in DRAWS for dl in CP.DELTAS}
        return res, rec

    def sn_read(res, rec, ident=("PASS", 1.0, [])):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            v = SN.readout(res, rec, ident, out=print)
        return v, buf.getvalue()
    full = {"economics": 5, "math": 4, "physics": 0}

    def tn1_third():
        res, rec = sn_fixture(size_k={"S": 30}, d2={"S": full})
        res["G12_n00000006"] = {"S": {"cert": True}, "G_I": {"cert": None}, "G_S": {"cert": False}}
        v, txt = sn_read(res, rec)
        assert v["tn1"] == "THIRD-NULL-WORKS" and "TN1 (DECIDING): THIRD-NULL-WORKS" in txt, txt
        assert ("G12's real sites (DESCRIPTIVE ONLY, never a certificate): S (SigClust-soft) 1 of 1 (NOT EVALUABLE 0); "
                "G (sigma_b^2 I) 0 of 1 (NOT EVALUABLE 1)") in txt
        assert "CERT-SPLIT-DIP elongation controls E1 + E2: S (SigClust-soft) 0 of 70" in txt
        assert "SA1 S (SigClust-soft): 30 of 300 SIZE draws certified" in txt and "-> SIZE-OK" in txt
        assert "certified of 5 per anchor {'economics': 5, 'math': 4, 'physics': 0}" in txt
        assert "F-SN: NOT FIRED" in txt and "refuted if P is K2-SENSITIVE or no S / G arm is: not refuted" in txt
        assert "P3 TN1 THIRD 0.20 / NO 0.10 / MIXED 0.70: outcome THIRD-NULL-WORKS, Brier %.4f" % (
            (0.2 - 1) ** 2 + 0.1 ** 2 + 0.7 ** 2) in txt
        assert "P1 SA1 SIZE-OK S (SigClust-soft) p 0.80: Brier %.4f" % (0.2 ** 2) in txt
    case("TN1 THIRD-NULL-WORKS (S at 30 / 300 and 5 / 4 / 0)", tn1_third)

    def tn1_no():
        res, rec = sn_fixture(size_k={"S": 31, "G_I": 0, "G_S": 0}, d2={"S": full, "G_I": {"economics": 3, "math": 4,
                                                                                         "physics": 3}})
        v, txt = sn_read(res, rec)
        assert v["tn1"] == "NO-NULL-WORKS" and v["fsn"] is True, v
        assert "F-SN: FIRED" in txt and "THIRD-NULL-WORKS is refuted if P is K2-SENSITIVE or no S / G arm is: REFUTED" in txt
        assert "P4 median delta* over sensitive arms 1 [0.5, 2]: NOT SCORED (no K2-SENSITIVE arm)" in txt
    case("TN1 NO-NULL-WORKS (S counts but fails SA1 at 31; G under the count); F-SN fires", tn1_no)

    def tn1_mixed():
        # P reaches the count at delta 2 -> P's K2-SENSITIVE is undetermined (no SIZE grid) -> THIRD cannot be asserted
        res, rec = sn_fixture(size_k={"S": 0}, d2={"S": full}, p_d2=4)
        v, txt = sn_read(res, rec)
        assert v["tn1"] == "NOT EVALUABLE", v["tn1"]
        res, rec = sn_fixture(size_k={"G_I": 0}, d2={"G_I": {"economics": 4, "math": 3, "physics": 4}})
        v, txt = sn_read(res, rec)
        assert v["tn1"] == "THIRD-NULL-WORKS" and "G (sigma_b^2 I)" in txt
    case("TN1 with P reaching the count -> NOT EVALUABLE; G_I alone -> THIRD", tn1_mixed)

    def tn1_ne():
        size_names = sorted(x for x, t in S.items() if t["cls"] == "SIZE")
        ne = {(n, "S") for n in size_names[:2]}
        res, rec = sn_fixture(size_k={"S": 31}, d2={"S": full}, ne=ne)
        v, txt = sn_read(res, rec)
        assert v["size_ok"]["S"] is None and v["tn1"] == "NOT EVALUABLE", v
        assert "29 of 300 SIZE draws certified" in txt and "with the 2 NOT EVALUABLE draws counted certified: 31" in txt
        res, rec = sn_fixture(size_k={"S": 20}, d2={"S": full}, ne={(size_names[-1], "S")})
        v, txt = sn_read(res, rec)
        assert v["size_ok"]["S"] is True and v["tn1"] == "THIRD-NULL-WORKS"
    case("SIN-6: NOT EVALUABLE draws decide only when they could flip the word", tn1_ne)

    def sn_refused():
        res, rec = sn_fixture()
        v, txt = sn_read(res, rec, ident=("FAIL", 0.5, []))
        assert v.get("refused") is True and "SI-NULL-TRIAD: REFUSED (the proxy fails its identity check)" in txt
        assert "TN1 (DECIDING)" not in txt
    case("SI-NULL-TRIAD refused on an identity FAIL", sn_refused)

    def sn_mixed_word():
        # an S arm SIZE-OK and reaching, but P also reaches with a known... P never has a SIZE word: MIXED arises when no arm is
        # K2-SENSITIVE yet some SIZE-OK arm... impossible by definition; MIXED needs THIRD False and NO False:
        res, rec = sn_fixture(size_k={"S": 0, "G_I": 0, "G_S": 0}, d2={}, p_d2=0)
        v, txt = sn_read(res, rec)
        assert v["tn1"] == "NO-NULL-WORKS"
        assert SN.tn1_of({"S": False, "G_I": False, "G_S": False}, {"S": True, "G_I": True, "G_S": True},
                         {"S": False, "G_I": False, "G_S": False}, False)[0] == "NO-NULL-WORKS"
        assert SN.tn1_of({"S": True, "G_I": False, "G_S": False}, {"S": True, "G_I": True, "G_S": True},
                         {"S": True, "G_I": False, "G_S": False}, True)[0] == "MIXED"
    case("TN1 MIXED (an S / G arm sensitive while P is too) and the NO path", sn_mixed_word)

    def sn_dstar():
        res, rec = sn_fixture(size_k={"S": 0}, d2={"S": full})
        for a in ANCHORS:
            for d in DRAWS:
                res[CP.site_name(a, 486, d, "1")]["S"]["cert"] = (a != "physics")
                for dl in ("2", "4", "6", "8", "10", "12"):
                    res[CP.site_name(a, 486, d, dl)]["S"]["cert"] = (a != "physics") or dl == "2"
        v, txt = sn_read(res, rec)
        assert "S (SigClust-soft): {'economics': '1', 'math': '1', 'physics': '2'}; median 1.0" in txt, txt
        assert "P4 median delta* over sensitive arms 1 [0.5, 2]: 1.0 -> HELD" in txt
    case("SI delta* per anchor (incl. SI-C1's 0.5 / 1) and P4", sn_dstar)

    # ---- the engine: run_tasks, resume, meta pin, analyze write-once
    def engine():
        tmp = tempfile.mkdtemp(prefix="csd_selftest_")
        try:
            rng = np.random.default_rng(9)
            m = unit(rng.normal(size=(1, 32)))[0]
            mini = {}
            for i in range(2):
                add(mini, "MINI_%d" % i, "POWER", unit(m + rng.normal(size=(150, 32)) * 0.05), ("dip", "S"))
            meta = make_meta(mini, 1e-3, 0.0145)
            cache = os.path.join(tmp, "cache.jsonl")
            calls = []

            def ident():
                calls.append(1)
                return dict(word="PASS", pooled=1.0, rows=[])
            with contextlib.redirect_stdout(io.StringIO()):
                done, idn = run_tasks(mini, cache, meta, 1e-3, 0.0145, 1, ident, sims=70, n_g=50)
            assert len(done) == 4 and calls == [1]
            n_lines = len(open(cache, encoding="utf-8").read().splitlines())
            with contextlib.redirect_stdout(io.StringIO()):
                done2, _ = run_tasks(mini, cache, meta, 1e-3, 0.0145, 1, ident, sims=70, n_g=50)
            assert calls == [1] and done2 == done                               # resumed: nothing recomputed
            assert len(open(cache, encoding="utf-8").read().splitlines()) == n_lines == 1 + 1 + 4
            bad = dict(meta)
            bad["sigma_b2"] = 2e-3
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    run_tasks(mini, cache, bad, 2e-3, 0.0145, 1, ident)
                raise AssertionError("meta mismatch accepted")
            except SystemExit:
                pass
            # identity FAIL: S tasks are not computed
            c2 = os.path.join(tmp, "c2.jsonl")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                d3, _ = run_tasks(mini, c2, meta, 1e-3, 0.0145, 1, lambda: dict(word="FAIL", pooled=0.5, rows=[]), sims=70)
            assert sorted(a for _n, a in d3) == ["dip", "dip"] and "SI-NULL-TRIAD leg REFUSED" in buf.getvalue()
            # analyze: a complete synthetic cache writes the outcome once; a second call refuses; partial -> _partial
            full_meta = dict(meta)
            full_meta["tasks"] = ["%s|%s" % (n, a) for n in sorted(S) for a in ("dip",) + TRIAD]
            d = os.path.join(tmp, "out")
            os.makedirs(d)
            done_full = base({"6": 50})
            for (n, a), r in list(done_full.items()):
                pass
            for n in S:
                for a in TRIAD:
                    done_full[(n, a)] = {"cert": False, "p": 0.5, "status": "OK"}
            with open(os.path.join(d, "cache.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"meta": full_meta}) + "\n")
                f.write(json.dumps({"identity": {"word": "PASS", "pooled": 1.0, "rows": []}}) + "\n")
                for (n, a), r in done_full.items():
                    f.write(json.dumps({"site": n, "arm": a, "res": r}) + "\n")
            rec = {CP.site_name(a, nn, dd, dl): False for a in ANCHORS for nn in SIZES for dd in DRAWS for dl in CP.DELTAS}
            with contextlib.redirect_stdout(io.StringIO()):
                v, v2, complete = analyze(d, rec)
            assert complete and v["sd1"] == "SENSITIVE" and v2["tn1"] == "NO-NULL-WORKS"
            txt = open(os.path.join(d, CSD_OUT), encoding="utf-8").read()
            assert txt.startswith("pool: none") and "-> SENSITIVE" in txt and PILOT_LINE in txt
            assert "TN1 (DECIDING): NO-NULL-WORKS" in open(os.path.join(d, SN_OUT), encoding="utf-8").read()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    analyze(d, rec)
                raise AssertionError("second analyze overwrote the outcome")
            except SystemExit:
                pass
            # partial: drop one dip row -> _partial files, no outcome of record
            d2 = os.path.join(tmp, "out2")
            os.makedirs(d2)
            with open(os.path.join(d2, "cache.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"meta": full_meta}) + "\n")
                f.write(json.dumps({"identity": {"word": "PASS", "pooled": 1.0, "rows": []}}) + "\n")
                for i, ((n, a), r) in enumerate(done_full.items()):
                    if i:
                        f.write(json.dumps({"site": n, "arm": a, "res": r}) + "\n")
            with contextlib.redirect_stdout(io.StringIO()):
                v, v2, complete = analyze(d2, rec)
            assert not complete and os.path.isfile(os.path.join(d2, "CERT_SPLIT_DIP_OUTCOME_partial.txt"))
            assert not os.path.isfile(os.path.join(d2, CSD_OUT))
            # identity FAIL in the cache: S / G rows not needed for completeness; SI outcome says REFUSED
            d3d = os.path.join(tmp, "out3")
            os.makedirs(d3d)
            with open(os.path.join(d3d, "cache.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"meta": full_meta}) + "\n")
                f.write(json.dumps({"identity": {"word": "FAIL", "pooled": 0.5, "rows": []}}) + "\n")
                for (n, a), r in done_full.items():
                    if a == "dip":
                        f.write(json.dumps({"site": n, "arm": a, "res": r}) + "\n")
            with contextlib.redirect_stdout(io.StringIO()):
                v, v2, complete = analyze(d3d, rec)
            assert complete and v2.get("refused") is True
            assert "REFUSED (the proxy fails its identity check)" in open(os.path.join(d3d, SN_OUT), encoding="utf-8").read()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    case("engine: run / resume / meta refusal / identity gate / analyze write-once / partial", engine)

    def main_run_path():
        tmp = tempfile.mkdtemp(prefix="csd_main_")
        try:
            rng = np.random.default_rng(4)
            m = unit(rng.normal(size=(1, 32)))[0]
            mini = {}
            add(mini, "MINI_0", "POWER", unit(m + rng.normal(size=(120, 32)) * 0.05), ("dip",))
            ASSEMBLE["fn"] = lambda a, out: dict(sites=mini, s2=1e-3, eps=0.0145, rec_p={}, pins={},
                                                 identity_fn=lambda: dict(word="PASS", pooled=1.0, rows=[]))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(["--run", "--out", tmp])
            assert rc == 0 and os.path.isfile(os.path.join(tmp, "cache.jsonl")), buf.getvalue()
            assert buf.getvalue().startswith("pool: ")
            meta, ident, done = read_cache(os.path.join(tmp, "cache.jsonl"))
            assert ("MINI_0", "dip") in done and ident["word"] == "PASS"
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main(["--run", "--out", tmp, "--pilot", "1"])
            assert os.path.isfile(os.path.join(tmp, "pilot_cache.jsonl"))
        finally:
            ASSEMBLE.pop("fn", None)
            shutil.rmtree(tmp, ignore_errors=True)
    case("main(['--run']): selftest-gated path, cache written, pilot cache separate", main_run_path)

    def write_once_fn():
        tmp = tempfile.mkdtemp(prefix="csd_wo_")
        try:
            p = os.path.join(tmp, "o.txt")
            write_text(p, "a")
            try:
                write_text(p, "b")
                raise AssertionError("overwrote")
            except SystemExit:
                pass
            assert open(p).read() == "a"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    case("write-once: mode x refuses an existing outcome", write_once_fn)

    def names_and_classes():
        assert cls_of("CSD_math_n486_d1_j2_D6") == "POWER" and cls_of("CSD256_math_n486_d1_D0") == "POWER256"
        assert cls_of("PL_math_n486_d1_D0.5") == "RECX" and cls_of("PL_math_n486_d1_D6") == "REC"
        assert cls_of("E1_256_STRONG_n486_d1_g0") == "E1_256" and cls_of("E1_STRONG_n486_d1_g0") == "E1"
        assert cls_of("KK256_MID_n486_d2") == "POS256" and cls_of("KK_MID_n486_d2") == "POS"
        assert sum(1 for s in S.values() if s["cls"] in ("E1", "E2")) == 70
        assert sum(1 for s in S.values() if s["cls"] == "SIZE") == 300
        assert sum(1 for n in S if n.startswith("CSD_") and n.endswith("_D6")) == 60
        assert sum(1 for s in S.values() if s["cls"] == "POWER") == 30 + 420
    case("site names, classes and the registered denominators (450 / 300 / 70 / 15)", names_and_classes)

    def fresh_seeds():
        ids = ["q_%03d" % i for i in range(40)]
        U0 = unit(np.random.default_rng(1).normal(size=(40, 512)))
        Y, u = fresh_plant(ids, U0, 3, 2, "6")
        u_ref = CP.direction(20261008000 + 32 - 20261004)
        import random
        rr = random.Random(20261008032)
        g = np.array([rr.gauss(0.0, 1.0) for _ in range(512)])
        assert np.allclose(u, g / np.linalg.norm(g)) and np.allclose(u, u_ref)
        hl = CP.halves(ids, 20261108032 - 20261104)
        perm = sorted(ids)
        random.Random(20261108032).shuffle(perm)
        assert {q for q, v in hl.items() if v == "hi"} == set(perm[:20])
        hi = np.array([hl[q] == "hi" for q in ids])
        Yref = unit(CP.plant_rows(U0, hi, u_ref, "6")[0].astype(np.float32).astype(np.float64))
        assert np.array_equal(Y, Yref)                                       # the fresh halves, float32 rendering
        Y2, u2 = fresh_plant(ids, U0, 3, 1, "6")
        assert not np.allclose(u, u2)
        u256 = fresh_plant(ids, trunc(U0, 256), 3, 2, "6", dim=256)[1]
        assert np.allclose(u256 * np.linalg.norm(g[:256]), g[:256])
    case("fresh plants: seeds 20261008000 + 10 d + j / 20261108000 + 10 d + j (CSD-2), R256 = the stream's first 256", fresh_seeds)

    def generator():
        P = unit(np.random.default_rng(0).normal(size=(50, 8)) + 3)
        G1 = gen_matched(P, 30, np.random.default_rng(7))
        G2 = gen_matched(P, 30, np.random.default_rng(7))
        assert np.array_equal(G1, G2) and G1.shape == (30, 8) and np.allclose((G1 * G1).sum(1), 1.0)
        big = gen_matched(P, 20000, np.random.default_rng(1))
        Pm = P.mean(0)
        assert np.abs(big.mean(0) - Pm).max() < 0.02
    case("generator: the record's moment-matched form, seeded, unit rows", generator)

    _IN_SELFTEST = False
    n = 0
    print("%s SELFTEST: %d failed%s" % (TAG, len(fails), (": " + ", ".join(fails)) if fails else ""))
    return 1 if fails else n


def selftest_io(g12_sites, planted_dir=PLANTED_DIR_DEFAULT, kk_labels=KK_LABELS_DEFAULT):
    """--selftest-io: the DB half of --dry-run / --run / --analyze end to end on a FIXTURE data root (no pool read): a fixture
    embeddings_cache.db (the planted D0 rows for the planted ids, random unit rows for the other IDENTITY ids), a fixture
    snapshots.db holding G12's 60 node ids (random children), the real pinned planted / KK / G12 files. Asserts the printed
    VALUES (site counts per class, the D0 identity, the identity precondition's word), then a --run --pilot 1 and an --analyze
    --pilot 1 that write *_PILOT files only."""
    global _IN_SELFTEST
    import sqlite3
    import struct
    tmp = tempfile.mkdtemp(prefix="csd_io_")
    _IN_SELFTEST = True
    try:
        _sf, rows_by_site, _sb, _vb = CP.read_planted(os.path.join(planted_dir, "planted_sites.tsv"),
                                                      os.path.join(planted_dir, "planted_vectors.f32be"))
        kk = PCS.parse_site_file(kk_labels)
        ident = sorted(kk["IDENTITY"])
        known = {}
        for s in CP.site_names():
            if s.endswith("_D0"):
                ids, y32 = rows_by_site[s]
                for q, r in zip(ids, y32):
                    known[q] = np.asarray(r, dtype=np.float32)
        rng = np.random.default_rng(0)
        con = sqlite3.connect(os.path.join(tmp, "embeddings_cache.db"))
        con.execute("CREATE TABLE queries (id TEXT, distilled_text TEXT)")
        con.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
        for q in ident:
            v = known.get(q)
            if v is None:
                v = unit(rng.normal(size=(1, 512)) + 3.0)[0].astype(np.float32)
            con.execute("INSERT INTO queries VALUES (?, ?)", (q, "t_" + q))
            con.execute("INSERT INTO embeddings VALUES (?, ?)", ("t_" + q, struct.pack(">512f", *[float(x) for x in v])))
        con.commit()
        con.close()
        cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
        entry = G.pointer_entry(cfg, ROOT)
        nodes_g12 = [r["node_id"] for r in csv.DictReader(open(g12_sites, newline="", encoding="utf-8"))]
        pool = list(ident)
        rng.shuffle(pool)
        nodes = [dict(id="n00000001", depth=0, childIds=list(nodes_g12), queryIds=[])]
        off = 0
        for nid in nodes_g12:
            a, b = "%s_a" % nid, "%s_b" % nid
            nodes.append(dict(id=nid, depth=1, childIds=[a, b], queryIds=[]))
            nodes.append(dict(id=a, depth=2, childIds=[], queryIds=pool[off:off + 55]))
            nodes.append(dict(id=b, depth=2, childIds=[], queryIds=pool[off + 55:off + 110]))
            off += 110
        con = sqlite3.connect(os.path.join(tmp, "snapshots.db"))
        con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, settings TEXT)")
        con.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (entry["snapshot_id"], json.dumps(dict(rootId="n00000001",
                                                                                                    nodes=nodes)),
                                                               json.dumps(dict(buildStamp=entry["stamp"]))))
        con.commit()
        con.close()
        common = ["--data-root", tmp, "--g12-sites", g12_sites, "--planted-dir", planted_dir, "--kk-labels", kk_labels,
                  "--out", os.path.join(tmp, "out")]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--dry-run"] + common)
        txt = buf.getvalue()
        sys.stdout.write(txt)
        for want in ("E1 50 sites / 200 tasks", "E2 20 sites / 80 tasks", "G12 60 sites / 180 tasks", "POS 15 sites / 60 tasks",
                     "POWER 450 sites / 1800 tasks", "REC 210 sites / 840 tasks", "RECX 60 sites / 240 tasks",
                     "SIZE 300 sites / 1200 tasks", "POWER256 210 sites / 210 tasks", "SIZE256 300 sites / 300 tasks",
                     "E1_256 50 sites / 50 tasks", "E2_256 20 sites / 20 tasks", "POS256 15 sites / 15 tasks",
                     "max |diff| 0.00e+00", "-> FAIL", "RUNTIME ESTIMATE", "DRY RUN: nothing written"):
            assert want in txt, want
        assert txt.startswith("pool: ") and not os.path.exists(os.path.join(tmp, "out"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--run", "--pilot", "1"] + common)
            main(["--analyze", "--pilot", "1"] + common)
        txt = buf.getvalue()
        sys.stdout.write(txt[-3000:])
        od = os.path.join(tmp, "out")
        assert os.path.isfile(os.path.join(od, "pilot_cache.jsonl"))
        assert os.path.isfile(os.path.join(od, "CERT_SPLIT_DIP_OUTCOME_PILOT.txt"))
        assert not os.path.isfile(os.path.join(od, CSD_OUT)) and not os.path.isfile(os.path.join(od, SN_OUT))
        assert "SI-NULL-TRIAD leg REFUSED" in txt
        print("%s SELFTEST-IO: PASS" % TAG)
        return 0
    finally:
        _IN_SELFTEST = False
        shutil.rmtree(tmp, ignore_errors=True)


# ================================================================================================ mutants
MUTANTS = [
    # (id, file, old, new)
    ("M01 combine min-p", "cert_split_dip.py", "2.0 * float(np.median(np.asarray(ps, dtype=np.float64)))",
     "2.0 * float(np.min(np.asarray(ps, dtype=np.float64)))"),
    ("M02 combine mean", "cert_split_dip.py", "2.0 * float(np.median(np.asarray(ps, dtype=np.float64)))",
     "2.0 * float(np.mean(np.asarray(ps, dtype=np.float64)))"),
    ("M03 alpha strict", "cert_split_dip.py", "    return bool(p <= ALPHA)", "    return bool(p < ALPHA)"),
    ("M43 SN alpha strict", "si_null_triad.py", "    return bool(p <= ALPHA)", "    return bool(p < ALPHA)"),
    ("M44 P read at n 441", "si_null_triad.py",
     'p_by_anchor = {a: [p_record.get("PL_%s_n%d_d%d_D%s" % (a, DECIDING_N, d, DELTA_SA2))',
     'p_by_anchor = {a: [p_record.get("PL_%s_n%d_d%d_D%s" % (a, 441, d, DELTA_SA2))'),
    ("M45 SA2 at delta 4", "si_null_triad.py", 'DELTA_SA2 = "2"', 'DELTA_SA2 = "4"'),
    ("M46 SIZE gate over 299", "cert_split_dip.py", "    up = SN.cp_upper(k_size, N_SIZE)",
     "    up = SN.cp_upper(k_size, N_SIZE)\n    k_size = sum(1 for n in size[1:] if _cert(done, n) is True)"),
    ("M04 axis on B (in-sample)", "cert_split_dip.py", "C = skmeans2(X[A], rng)", "C = skmeans2(X[B], rng)"),
    ("M05 SD1 bar 44", "cert_split_dip.py", "SD1_SENS, SD1_INS = 45, 15", "SD1_SENS, SD1_INS = 44, 15"),
    ("M06 SD1 ins bar 16", "cert_split_dip.py", "SD1_SENS, SD1_INS = 45, 15", "SD1_SENS, SD1_INS = 45, 16"),
    ("M07 SD1 n486 only", "cert_split_dip.py", "c_dec = sum(1 for n in dec if _cert(done, n) is True)",
     "c_dec = sum(1 for n in dec if '_n486_' in n and _cert(done, n) is True) * 2"),
    ("M08 SD0 d0 bar 2", "cert_split_dip.py", "return bool(SN.size_ok_of(k_size, N_SIZE) and k_d0 <= 1)",
     "return bool(SN.size_ok_of(k_size, N_SIZE) and k_d0 <= 2)"),
    ("M09 SD0 d0 from n 441", "cert_split_dip.py", "k_d0 = sum(1 for n in d0_486 if _cert(done, n) is True)",
     "k_d0 = sum(1 for n in d0_441 if _cert(done, n) is True)"),
    ("M10 SA1 rate only", "si_null_triad.py",
     "return bool(Fraction(k, n) <= SA1_RATE and Fraction(cp_upper(k, n)).limit_denominator(10 ** 12) <= SA1_UPPER)",
     "return bool(Fraction(k, n) <= SA1_RATE)"),
    ("M11 SA1 rate 0.11", "si_null_triad.py", "SA1_RATE, SA1_UPPER = Fraction(1, 10), Fraction(15, 100)",
     "SA1_RATE, SA1_UPPER = Fraction(11, 100), Fraction(15, 100)"),
    ("M12 SD2 >=2 -> >=1", "cert_split_dip.py", 'return "POS-OK" if hi >= 2 else', 'return "POS-OK" if hi >= 1 else'),
    ("M13 SD2 fail first", "cert_split_dip.py",
     'return "POS-OK" if hi >= 2 else ("POS-FAIL" if lo >= 2 else "MIXED")',
     'return "POS-FAIL" if lo >= 1 else ("POS-OK" if hi >= 2 else "MIXED")'),
    ("M14 F-SD elong 9", "cert_split_dip.py", "FSD_ELONG = 8", "FSD_ELONG = 9"),
    ("M15 F-SD E2 only", "cert_split_dip.py", "    k_el = sum(1 for n in el if _cert(done, n) is True)",
     '    k_el = sum(1 for n in el if sites[n]["cls"] == "E2" and _cert(done, n) is True)'),
    ("M16 F-SD no INSENSITIVE clause", "cert_split_dip.py", 'fire_i = v["sd1"] == "INSENSITIVE"', "fire_i = False"),
    ("M17 SD1 words swapped", "cert_split_dip.py",
     'return "SENSITIVE" if c >= SD1_SENS else ("INSENSITIVE" if c <= SD1_INS else "MIXED")',
     'return "INSENSITIVE" if c <= SD1_INS else ("SENSITIVE" if c > SD1_SENS else "MIXED")'),
    ("M18 delta* 7 of 10", "cert_split_dip.py", "            if c >= 8:\n", "            if c >= 7:\n"),
    ("M19 delta* min over cats", "cert_split_dip.py", "med = SN.median_ds(list(ds.values()), NONE_WORD, 10.0)",
     "med = min(SN.rank_of(x, NONE_WORD, 10.0) for x in ds.values())"),
    ("M20 P1 band 0.03", "cert_split_dip.py", "P1_P, P1_BAND = 0.95, (0.00, 0.00, 0.02)", "P1_P, P1_BAND = 0.95, (0.00, 0.00, 0.03)"),
    ("M21 P3 delta 8 band", "cert_split_dip.py", '"8": (60, 57, 60)', '"8": (60, 56, 60)'),
    ("M22 TN1 ignore P", "si_null_triad.py", "third = and3(or3(*[k2s[a] for a in ARMS]), not3(p_k2s))",
     "third = or3(*[k2s[a] for a in ARMS])"),
    ("M23 SA2 3 of 5", "si_null_triad.py",
     "    lo = sum(1 for a in ANCHORS if sum(1 for c in by_anchor[a] if c is True) >= 4)",
     "    lo = sum(1 for a in ANCHORS if sum(1 for c in by_anchor[a] if c is True) >= 3)"),
    ("M24 SA2 one anchor", "si_null_triad.py", "    a, b = lo >= 2, hi >= 2", "    a, b = lo >= 1, hi >= 1"),
    ("M25 SIN-6 NE as not-cert", "si_null_triad.py", "    return (a if a == b else None), k_lo, k_hi, n",
     "    return a, k_lo, k_hi, n"),
    ("M26 S p = k/B", "si_null_triad.py", "p=(1 + k_le) / (1 + reached)", "p=max(k_le, 1e-9) / reached"),
    ("M27 S >= instead of <=", "si_null_triad.py", "k_le = sum(1 for c in cis if c <= ci_obs)",
     "k_le = sum(1 for c in cis if c >= ci_obs)"),
    ("M28 G numerator all", "si_null_triad.py", "            if phi >= T:\n                num_logw.append(lw)",
     "            num_logw.append(lw)"),
    ("M29 Holm min p", "si_null_triad.py", "p=min(1.0, len(pairs) * pmin)", "p=min(1.0, pmin)"),
    ("M30 identity bar 0.98", "si_null_triad.py", "IDENTITY_MIN = Fraction(99, 100)", "IDENTITY_MIN = Fraction(98, 100)"),
    ("M31 identity gate off", "cert_split_dip.py",
     'triad_ok = ident is not None and ident.get("word") == "PASS"\n    todo',
     'triad_ok = True\n    todo'),
    ("M32 write-once off", "cert_split_dip.py", 'with open(path, "x", encoding="utf-8", newline="\\n") as f:',
     'with open(path, "w", encoding="utf-8", newline="\\n") as f:'),
    ("M33 partial as complete", "cert_split_dip.py", "complete = not missing and not pilot", "complete = not pilot"),
    ("M34 resume recomputes", "cert_split_dip.py",
     "if (n, a) not in done and (a == \"dip\" or triad_ok)]", "if (a == \"dip\" or triad_ok)]"),
    ("M35 meta check off", "cert_split_dip.py", "    elif old != meta:", "    elif False:"),
    ("M36 java random scramble", "si_null_triad.py", "self.s = (int(seed) ^ 0x5DEECE66D) & MASK48",
     "self.s = int(seed) & MASK48"),
    ("M37 soft threshold no tau", "si_null_triad.py", "    return np.maximum(lam - t, s2), t", "    return np.maximum(lam, s2), t"),
    ("M38 fresh plant record seed", "cert_split_dip.py",
     "    u = CP.direction(U_SEED_F + 10 * d + j - CP.U_SEED0, dim=dim)", "    u = CP.direction(d, dim=dim)"),
    ("M39 EM collapse ignored", "si_null_triad.py", "                if sumr[c] < min_soft:\n                    return False",
     "                if sumr[c] < -1.0:\n                    return False"),
    ("M40 SD0 NOT EVALUABLE path off", "cert_split_dip.py", "    if not sd0:\n        v[\"sd1\"] = \"NOT EVALUABLE\"",
     "    if False:\n        v[\"sd1\"] = \"NOT EVALUABLE\""),
    ("M41 P2 band lo 49", "cert_split_dip.py", "P2_BAND = (58, 50, 60)", "P2_BAND = (58, 49, 60)"),
    ("M47 G_S as G_I", "si_null_triad.py", '    if variant == "G_I":\n        sb = math.sqrt(s2)',
     '    if True:\n        sb = math.sqrt(s2)'),
    ("M48 fresh halves record seed", "cert_split_dip.py",
     "    hl = CP.halves(ids, H_SEED_F + 10 * d + j - CP.H_SEED0)", "    hl = CP.halves(ids, d)"),
    ("M49 fresh rows not float32", "cert_split_dip.py", "    Y32 = Y.astype(np.float32).astype(np.float64)", "    Y32 = Y"),
    ("M50 S CI on normalised rows", "si_null_triad.py", "                cis.append(cluster_index(Y[j], parts_of(labs[j])))",
     "                cis.append(cluster_index(norm_rows(Y[j]), parts_of(labs[j])))"),
    ("M42 TN1 NO ignores SIZE-OK", "si_null_triad.py",
     "any_ok_reach = or3(*[and3(size_ok[a], reach[a]) for a in ARMS], p_k2s)",
     "any_ok_reach = or3(*[reach[a] for a in ARMS], p_k2s)"),
]
MUTANT_WORKERS = 8


def _run_mutant(args):
    mid, fname, old, new, src_dir, work = args
    d = os.path.join(work, "m_%s" % mid.split()[0])
    os.makedirs(d, exist_ok=True)
    for f in ("cert_split_dip.py", "si_null_triad.py"):
        shutil.copy(os.path.join(SELF_DIR, f), os.path.join(d, f))
    p = os.path.join(d, fname)
    txt = open(p, encoding="utf-8").read()
    cut = txt.find("\nMUTANTS = [")                  # the table itself is never mutated
    head, tail = (txt, "") if cut < 0 else (txt[:cut], txt[cut:])
    if head.count(old) != 1:
        return mid, "BAD PATTERN (%d matches)" % head.count(old)
    open(p, "w", encoding="utf-8", newline="\n").write(head.replace(old, new) + tail)
    env = dict(os.environ, CSD_SRC_DIR=src_dir, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMBA_NUM_THREADS="1")
    pyl = [x for x in sys.path if os.path.isdir(os.path.join(x, "diptest"))]
    if pyl:
        env["PYTHONPATH"] = os.pathsep.join(pyl + [env.get("PYTHONPATH", "")])
    r = subprocess.run([sys.executable, os.path.join(d, "cert_split_dip.py"), "--selftest"], env=env, capture_output=True,
                       text=True, timeout=3600)
    return mid, ("KILLED" if r.returncode != 0 else "SURVIVED")


def mutants():
    from multiprocessing import Pool
    work = tempfile.mkdtemp(prefix="csd_mutants_")
    try:
        jobs = [(m[0], m[1], m[2], m[3], HERE, work) for m in MUTANTS]
        with Pool(MUTANT_WORKERS) as pool:
            res = pool.map(_run_mutant, jobs, chunksize=1)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    killed = sum(1 for _m, r in res if r == "KILLED")
    for m, r in res:
        print("  %-36s %s" % (m, r))
    print("%s MUTANTS: %d / %d killed" % (TAG, killed, len(res)))
    return 0 if killed == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
