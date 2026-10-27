"""si_null_triad.py: SI-NULL-TRIAD, the splitter PROXY, its identity precondition, arms S (SigClust-soft) and G (Gao-type
selective p, two covariance variants) and the READOUT (SA1, SA2, TN1, F-SN, P1-P4). ZERO calls. The per-site computation is
launched by tools/analysis/cert_split_dip.py in the same pool window (CERT-SPLIT-DIP's registration: "the same tool runs
SI-NULL-TRIAD's arms S and G in the same pool window on SI-NULL-TRIAD's grid under SI-NULL-TRIAD's registration"); this module is
the arms and the readout, cert_split_dip.py the site assembly, the cache and the launch.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-04 (before any code or call) — SI-NULL-TRIAD: does a site null whose covariance is not taken from the site
(SigClust-soft, Huang et al. 2015; a Gao-type selective p-value) certify CERT-PLANTED's planted 2-way structure without certifying
structureless clouds, beside the plain null of record? (zero calls; CPU; T-A of the hierarchy-evaluation pass)" (span
L24335-L24347), unchanged; state confirmed and condition SI-C1 in "## Registrar's record 2026-10-08 ... six zero-call tests
registered ..." (L24955). Record docs/agents/results/SI-NULL-TRIAD.json.
  Arms: P (plain site null of record; counts READ from CERT-PLANTED's cpl_sites.csv, sha256 359357a5...); S (SigClust-soft:
  sigma_b^2 from the whole corpus' centred TRAIN coordinates, soft-thresholded site eigenvalues, statistic = the proxy's 2-means
  cluster index at k = 2, 1,000 simulations); G (selective p by importance-sampling Monte Carlo, N = 2,000, the proxy as the
  clustering function; variants G_I (sigma_b^2 I) and G_S (S's thresholded matrix); k > 2: all sibling pairs, Holm). A site
  certifies under an arm iff its p <= 0.05. SA1 SIZE-OK iff the rejection rate over the 300 SIZE draws is <= 0.10 AND its 95%
  Clopper-Pearson upper bound <= 0.15. SA2 K2-SENSITIVE iff SIZE-OK AND delta 2 certifies >= 4 of 5 in >= 2 of 3 anchors at n 486.
  TN1 THIRD-NULL-WORKS iff S or G (either variant) is K2-SENSITIVE while P is not; NO-NULL-WORKS iff no SIZE-OK arm certifies
  >= 4 of 5 at delta 2 in >= 2 anchors; MIXED otherwise. F-SN fires iff TN1 NO-NULL-WORKS or every K2-SENSITIVE S / G arm fails SA1.
  P1 SA1 SIZE-OK S 0.80, G (sigma_b^2 I) 0.70, G (S matrix) 0.75; P2 K2-SENSITIVE S 0.70, G 0.75; P3 THIRD 0.20 / NO 0.10 /
  MIXED 0.70; P4 median delta* over sensitive arms 1 [0.5, 2].

BUILDER'S READINGS (each handed to the reviewer / registrar; none changes a criterion word, bar or denominator):
  SIN-1 SIZE generator: "50 draws from each anchor's own moment-matched generator at n 486 and n 441" = per anchor ONE generator,
        the record's withinNodeCloud form (mean + sum_c g_c c / sqrt(M) over the anchor's M centred TRAIN rows of the B0 member
        root, rows unit-renormalised), matched to ALL of the anchor's TRAIN items (IDENTITY rows of that category), drawn at n 486
        and n 441; draw index i = anchor (economics, math, physics) x size (486, 441) x g (0..49) in that order, seed
        numpy default_rng(20261004 + i) (the registered seed base). The literature file says "each site's own"; the
        registration's "each anchor's own" governs.
  SIN-2 PROXY = TaxonomySplitter.splitSingleNode's proposal ON ITS PCA PROJECTION, with forcedK = the site's k: rows =
        projectTo(512); PCA by the splitter's power iteration (java.util.Random init seeds of StatisticsUtils.pcaProject
        replicated; the JavaRandom replica is checked against Java's published Random(42) values) at the splitter's size rule
        (32 / 64 / 128 dims for n < 100 / < 500 / else: "the splitter's 128-d PCA projection" of the registration is that rule
        at n >= 500; at n 486 / 441 the splitter itself uses 64); pcaProject's row normalisation; vMF EM with the deterministic
        init under performVmfKMeans' forced-k loop (numba, Kotlin's loop order; a second numpy implementation agrees to 1e-13 in
        the selftest); hard assignment; the splitter's EM floor pre-check (a cluster below minClusterSize 55 -> no partition).
        NOT in the proxy: the routing of the children in the 512 slice, the coarsening loop and the min-pair acceptance gate
        (they act outside the projection the registration puts the proxy on; the acceptance gate is what arm P calibrates); the
        routed replica (routing + coarsening, split_replica) is computed beside in the identity check, DESCRIPTIVELY.
        "The PCA basis is held fixed" = the observed site's basis and centring; S's simulations and G's perturbations live in
        that projection (Zc = the site's centred projected coordinates, dimension q = 32 / 64 / 128). DISCLOSED CONSEQUENCE
        (selftest fixture 'isotropic 512'): the alternative reading (simulate in the 512 slice and project the simulations on the
        observed basis) is anti-conservative, because the observed basis is selected on the observed noise and not on the
        simulated (an isotropic cloud certified at p 0.005 under it, p 1.0 under this reading); this reading is conservative on
        near-isotropic clouds (sample eigenvalues re-inflated by the simulations' own sampling).
  SIN-3 Identity precondition: pooled item agreement over the 60 G12 sites (best one-to-one matching of the proxy's clusters
        to the persisted children; an item held by several children agrees if its cluster maps to any of them) >= 0.99; the
        per-site minimum and the routed replica's agreement are printed beside. FAIL -> the SI-NULL-TRIAD leg is REFUSED (no
        S / G site is computed; the registration says "else the run refuses" and "G is NOT EVALUABLE": both hold); CERT-SPLIT-
        DIP's dip arm does not use the proxy and runs.
  SIN-4 sigma_b = MAD(all entries of the corpus' centred 512 coordinates) / 0.6745 (SigClust's normal-consistent MAD; the
        registration's "MAD^2" read as the variance this gives; the background per coordinate is basis-free, so it applies to
        the orthonormal projection); corpus = the 6,993 TRAIN items of the B0 member root (IDENTITY of CERT-PC-K2-KNOWN's site
        file 8e122edd). S's null = N(0, diag(lambda~)) in the site's projected eigen-coordinates (the proxy is rotation-
        equivariant and the cluster index rotation-invariant), lambda = the eigenvalues of Zc's covariance (ddof 0),
        lambda~_j = max(lambda_j - tau, sigma_b^2) with tau >= 0 preserving the total power (Huang et al. 2015 soft
        thresholding; tau = +inf -> all sigma_b^2 when the projection's power is below q sigma_b^2). Disclosed: in the
        projection the kept eigenvalues usually exceed sigma_b^2, so tau is often 0 (printed per site). Cluster index =
        within / total sum of squares of Zc (observed) or of the simulated rows under the proxy's 2-way partition; p = (1 +
        #{CI_sim <= CI_obs}) / (1 + reached).
  SIN-5 G: X = Zc; X'(phi) = X + nu (phi - T) p^T / ||nu||^2 with T = ||Sigma^{-1/2} nu^T X||, p = Sigma^{1/2} (Sigma^{-1/2}
        nu^T X / T); phi ~ ||nu|| chi_q under H0; proposal N(T, ||nu||^2); p = sum_{phi >= T} w I / sum w I (I = the proxy at the
        site's k returns both tested clusters exactly). Sigma = sigma_b^2 I_q (G_I) or E diag(lambda~) E^T (G_S). k > 2:
        p_site = min(1, m x min_pair p) (Holm's first step = "Holm rejects any pair").
  SIN-6 NOT EVALUABLE sites (the proxy returns no partition on the observed rows; S: fewer than 67 of 1,000 simulations reach
        a partition, the record's 20-of-300 floor scaled; G: no weight on a reproduced selection) follow CPL-5: a word is printed
        iff it does not depend on how those sites would have read (Kleene three-valued logic over the arms), else NOT EVALUABLE.
  SIN-7 delta grid of the arms: CERT-PLANTED's record plants {0, 2, 4, 6, 8, 10, 12} plus 0.5 and 1 planted now with
        cert_planted.plant_rows at the record seeds (CPL-2 / CPL-3; condition SI-C1); delta* per anchor = smallest delta with
        >= 4 of 5 at n 486 (none -> '> 12'); an arm's delta* = the median over the 3 anchors (ranked, '> 12' above 12).
  SIN-8 F-SN's second clause is redundant under the record's definitions (a K2-SENSITIVE arm is SIZE-OK by definition, and
        whenever TN1 is not NO-NULL-WORKS some S / G arm is K2-SENSITIVE), so F-SN == (TN1 NO-NULL-WORKS); both clauses are
        evaluated and printed.

SELFTEST / MUTANTS: run through cert_split_dip.py (--selftest runs this module's selftest() first; --mutants mutates both files).
"""
import hashlib
import math
import os
import sys
from fractions import Fraction

import numpy as np

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
TAG = "[SNT]"

ALPHA = 0.05
S_SIMS, G_N = 1000, 2000
S_REACHED_MIN = 67                      # SIN-6: ceil(1000 x 20 / 300)
SA1_RATE, SA1_UPPER = Fraction(1, 10), Fraction(15, 100)
IDENTITY_MIN = Fraction(99, 100)
ANCHORS = ("economics", "math", "physics")
SIZES = (486, 441)
DECIDING_N = 486
DRAWS = (1, 2, 3, 4, 5)
SIZE_PER_CELL, SIZE_SEED0 = 50, 20261004
DELTAS_SN = ("0", "0.5", "1", "2", "4", "6", "8", "10", "12")
RECORD_DELTAS = ("0", "2", "4", "6", "8", "10", "12")
EXTRA_DELTAS = ("0.5", "1")
DELTA_SA2 = "2"
NONE_WORD_SN = "> 12"
ARMS = ("S", "G_I", "G_S")
ARM_LABEL = {"P": "P (plain site null of record)", "S": "S (SigClust-soft)", "G_I": "G (sigma_b^2 I)",
             "G_S": "G (S's thresholded matrix)"}
P1_P = {"S": 0.80, "G_I": 0.70, "G_S": 0.75}
P2_P = {"S": 0.70, "G_I": 0.75, "G_S": 0.75}
P3_P = {"THIRD-NULL-WORKS": 0.20, "NO-NULL-WORKS": 0.10, "MIXED": 0.70}
P4_BAND = (1.0, 0.5, 2.0)
MAD_NORMAL = 0.6744897501960817
REG = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — SI-NULL-TRIAD: ..." L24335-L24347, '
       'unchanged; condition SI-C1 and the joint run: "## Registrar\'s record 2026-10-08 ..." L24955')
CAVEAT_G = ("CAVEAT (registered): G's p is valid for the PROXY's selection event, not the engine's z-gate plus epoch schedule; real "
            "sites carry non-Gaussian texture, so S / G verdicts on G12's sites are DESCRIPTIVE ONLY, never a certificate.")
DOES_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW: a certificate of any real site (real-site verdicts descriptive); a mode test "
                 "(MIX-LRT-SITE closed); other members, draws or slices; validity of G for the engine's own selection.")


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ================================================================================================ the proxy (SIN-2)
MASK48 = (1 << 48) - 1


class JavaRandom:
    """java.util.Random (48-bit LCG): the seed scramble, next(bits) and nextDouble()."""

    def __init__(self, seed):
        self.s = (int(seed) ^ 0x5DEECE66D) & MASK48

    def next(self, bits):
        self.s = (self.s * 0x5DEECE66D + 0xB) & MASK48
        r = self.s >> (48 - bits)
        if r >= (1 << 31):
            r -= (1 << 32)
        return r

    def next_double(self):
        return ((self.next(26) << 27) + self.next(27)) * (2.0 ** -53)


def split_dim(n, width):
    """TaxonomySplitter: 32 / 64 / 128 for n < 100 / < 500 / else, capped at the row width."""
    return min(32 if n < 100 else (64 if n < 500 else 128), width)


def pca_basis(U, keep):
    """StatisticsUtils.pcaProject (dropTop 0, whiten false): centre, power iteration (30 steps, java.util.Random init seeded
    0x5EED + comp x 7919 + d x 104729 + n x 31, Gram-Schmidt against earlier components, in-place deflation). -> (mean, V (d, keep))."""
    U = np.asarray(U, dtype=np.float64)
    n, d = U.shape
    keep = min(keep, d)
    mean = U.mean(axis=0)
    R = U - mean
    comps = []
    for comp in range(keep):
        rng = JavaRandom(0x5EED + comp * 7919 + d * 104729 + n * 31)
        vec = np.array([rng.next_double() - 0.5 for _ in range(d)], dtype=np.float64)
        for _ in range(30):
            proj = R.T @ (R @ vec)
            if comps:
                C = np.stack(comps, axis=1)
                proj = proj - C @ (C.T @ proj)     # == the sequential Gram-Schmidt for orthonormal components
            nrm = math.sqrt(float(proj @ proj))
            vec = proj / nrm if nrm > 1e-10 else proj
        comps.append(vec)
        R -= np.outer(R @ vec, vec)
    return mean, np.stack(comps, axis=1)


def norm_rows(Z):
    """pcaProject's last step: each row L2-normalised when its norm > 1e-10 (works on (n, d) and (B, n, d))."""
    nr = np.sqrt((Z * Z).sum(axis=-1, keepdims=True))
    return np.where(nr > 1e-10, Z / np.where(nr > 1e-10, nr, 1.0), Z)


def log_gamma(x):
    """StatisticsUtils.logGamma (Lanczos)."""
    if x < 0.5:
        return math.log(math.pi / math.sin(math.pi * x)) - log_gamma(1.0 - x)
    coeff = (76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2,
             -0.5395239384953e-5)
    y = x
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in coeff:
        y += 1.0
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


def log_bessel_i(nu, kappa):
    """StatisticsUtils.logBesselI (Debye uniform asymptotic), vectorised over kappa."""
    kappa = np.asarray(kappa, dtype=np.float64)
    small = kappa <= 1e-4
    safe_nu = 1e-5 if nu <= 0.0 else nu
    kk = np.where(small, 1.0, kappa)
    z = kk / safe_nu
    t = np.sqrt(1.0 + z * z)
    eta = t + np.log(z / (1.0 + t))
    big = safe_nu * eta - 0.5 * math.log(2.0 * math.pi * safe_nu) - 0.25 * np.log(1.0 + z * z)
    lo = nu * np.log(np.where(small, kappa, 1.0) / 2.0) - log_gamma(nu + 1.0)
    return np.where(small, lo, big)


def log_vmf_norm(d, kappa):
    kappa = np.asarray(kappa, dtype=np.float64)
    nu = d / 2.0 - 1.0
    small = kappa <= 1e-4
    lo = log_gamma(d / 2.0) - (d / 2.0) * math.log(math.pi) - math.log(2.0)
    kk = np.where(small, 1.0, kappa)
    big = nu * np.log(kk) - (d / 2.0) * math.log(2.0 * math.pi) - log_bessel_i(nu, kk)
    return np.where(small, lo, big)


def bessel_ratio_ad(d, kappa):
    kappa = np.asarray(kappa, dtype=np.float64)
    pos = kappa > 0.0
    kk = np.where(pos, kappa, 1.0)
    nu = d / 2.0
    r = np.clip(np.exp(log_bessel_i(nu, kk) - log_bessel_i(nu - 1.0, kk)), 0.0, 1.0)
    return np.where(pos, r, 0.0)


def corrected_kappa(rbar, d, n):
    """StatisticsUtils.correctedKappa vectorised (rbar, n arrays of one shape)."""
    rbar = np.asarray(rbar, dtype=np.float64)
    n = np.asarray(n, dtype=np.float64)
    hi, lo = rbar >= 1.0, rbar <= 0.0
    r = np.clip(rbar, 1e-12, 1.0 - 1e-12)
    kappa = r * (d - r * r) / (1.0 - r * r)
    act = ~(hi | lo)
    for _ in range(5):
        if not act.any():
            break
        ad = bessel_ratio_ad(d, kappa)
        deriv = 1.0 - ad * ad - ((d - 1.0) / kappa) * ad
        act = act & ~(np.abs(deriv) < 1e-9)
        with np.errstate(divide="ignore", invalid="ignore"):
            nxt = kappa - (ad - r) / np.where(deriv == 0.0, 1.0, deriv)
        bad = ~np.isfinite(nxt) | (nxt <= 0.0)
        upd = act & ~bad
        conv = np.abs(nxt - kappa) < 1e-6 * kappa
        kappa = np.where(upd, np.clip(nxt, 1e-3, 1e6), kappa)
        act = upd & ~conv
    kml = np.clip(kappa, 1e-3, 1e4)
    shrink = (n - 1.0) / np.maximum(n + d - 2.0, 1.0)
    out = np.clip(kml * shrink, 1e-3, 1e4)
    return np.where(hi, 1e4, np.where(lo, 1e-3, out))


def vmf_em_batch(Z, k, min_frac):
    """StatisticsUtils.runVmfEm on each of B data sets at once. Z (B, n, d) unit rows. -> (R (B, n, k), ok (B,) bool):
    ok False = collapsed (a soft count below min_frac x n) or n < k."""
    B, n, d = Z.shape
    if n < k:
        return np.zeros((B, n, k)), np.zeros(B, dtype=bool)
    cen = Z.sum(axis=1)
    cn = np.sqrt((cen * cen).sum(axis=1, keepdims=True))
    mus = np.zeros((B, k, d))
    mus[:, 0] = np.where(cn > 0.0, cen / np.where(cn > 0.0, cn, 1.0), 0.0)
    ar = np.arange(B)
    for c in range(1, k):
        dots = np.einsum("bnd,bcd->bnc", Z, mus[:, :c])
        mind = (1.0 - np.clip(dots, -1.0, 1.0)).min(axis=2)
        mus[:, c] = Z[ar, np.argmax(mind, axis=1)]
    kappa = np.full((B, k), 10.0)
    lnorm = np.full((B, k), float(log_vmf_norm(d, 10.0)))
    pis = np.full((B, k), 1.0 / k)
    R = np.zeros((B, n, k))
    last = np.full(B, -sys.float_info.max)
    best = np.full(B, -sys.float_info.max)
    pat = np.zeros(B, dtype=int)
    ok = np.ones(B, dtype=bool)
    act = np.ones(B, dtype=bool)
    min_soft = min_frac * n
    for _it in range(150):
        idx = np.nonzero(act)[0]
        if idx.size == 0:
            break
        Zi = Z[idx]
        dots = np.matmul(Zi, np.transpose(mus[idx], (0, 2, 1)))
        logp = (np.log(np.maximum(pis[idx], 1e-10)) + lnorm[idx])[:, None, :] + kappa[idx][:, None, :] * dots
        mx = logp.max(axis=2, keepdims=True)
        ex = np.exp(logp - mx)
        se = ex.sum(axis=2, keepdims=True)
        Ri = ex / se
        L = (mx[:, :, 0] + np.log(se[:, :, 0])).sum(axis=1)
        R[idx] = Ri
        conv = np.abs(L - last[idx]) / n < 1e-5
        improved = L > best[idx] + 1e-6
        best[idx] = np.where(~conv & improved, L, best[idx])
        pat[idx] = np.where(conv, pat[idx], np.where(improved, 0, pat[idx] + 1))
        plateau = ~conv & (pat[idx] >= 10)
        go = ~conv & ~plateau
        act[idx[~go]] = False
        gi = idx[go]
        if gi.size == 0:
            continue
        last[gi] = L[go]
        Rg = Ri[go]
        sumr = Rg.sum(axis=1)
        nxt = np.matmul(np.transpose(Rg, (0, 2, 1)), Z[gi])
        coll = (sumr < min_soft).any(axis=1)
        ok[gi[coll]] = False
        act[gi[coll]] = False
        keep = ~coll
        gk = gi[keep]
        if gk.size == 0:
            continue
        sumr, nxt = sumr[keep], nxt[keep]
        pis[gk] = sumr / n
        nrm = np.sqrt((nxt * nxt).sum(axis=2))
        mus[gk] = np.where(nrm[:, :, None] > 0.0, nxt / np.where(nrm > 0.0, nrm, 1.0)[:, :, None], 0.0)
        rbar = nrm / np.maximum(sumr, 1e-9)
        nn = np.maximum(np.floor(sumr + 0.5), 2.0)
        kappa[gk] = corrected_kappa(rbar, d, nn)
        lnorm[gk] = log_vmf_norm(d, kappa[gk])
    return R, ok


# ------------------------------------------------------------------------------------------------ the same EM, scalar (numba)
# Kotlin's loop order replicated element by element (runVmfEm); used by the run. vmf_em_batch (numpy, above) is the independent
# second implementation the selftest compares it with.
_NB = {}


def _nb():
    if "em" in _NB:
        return _NB["em"]
    from numba import njit

    @njit(cache=False)
    def lgam(x):
        coeff = (76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2,
                 -0.5395239384953e-5)
        y = x
        tmp = x + 5.5
        tmp -= (x + 0.5) * math.log(tmp)
        ser = 1.000000000190015
        for c in coeff:
            y += 1.0
            ser += c / y
        return -tmp + math.log(2.5066282746310005 * ser / x)

    @njit(cache=False)
    def lbes(nu, kappa):
        if kappa <= 1e-4:
            return nu * math.log(kappa / 2.0) - lgam(nu + 1.0)
        snu = 1e-5 if nu <= 0.0 else nu
        z = kappa / snu
        t = math.sqrt(1.0 + z * z)
        eta = t + math.log(z / (1.0 + t))
        return snu * eta - 0.5 * math.log(2.0 * math.pi * snu) - 0.25 * math.log(1.0 + z * z)

    @njit(cache=False)
    def lnorm(d, kappa):
        nu = d / 2.0 - 1.0
        if kappa <= 1e-4:
            return lgam(d / 2.0) - (d / 2.0) * math.log(math.pi) - math.log(2.0)
        return nu * math.log(kappa) - (d / 2.0) * math.log(2.0 * math.pi) - lbes(nu, kappa)

    @njit(cache=False)
    def ad(d, kappa):
        if kappa <= 0.0:
            return 0.0
        nu = d / 2.0
        r = math.exp(lbes(nu, kappa) - lbes(nu - 1.0, kappa))
        return min(max(r, 0.0), 1.0)

    @njit(cache=False)
    def ckappa(rbar, d, n):
        if rbar >= 1.0:
            return 1e4
        if rbar <= 0.0:
            return 1e-3
        kappa = rbar * (d - rbar * rbar) / (1.0 - rbar * rbar)
        for _i in range(5):
            a = ad(d, kappa)
            der = 1.0 - a * a - ((d - 1.0) / kappa) * a
            if abs(der) < 1e-9:
                break
            nxt = kappa - (a - rbar) / der
            if not math.isfinite(nxt) or nxt <= 0.0:
                break
            conv = abs(nxt - kappa) < 1e-6 * kappa
            kappa = min(max(nxt, 1e-3), 1e6)
            if conv:
                break
        kml = min(max(kappa, 1e-3), 1e4)
        sh = (n - 1.0) / max(n + d - 2.0, 1.0)
        return min(max(kml * sh, 1e-3), 1e4)

    @njit(cache=False)
    def em(Z, k, min_frac, R):
        n, d = Z.shape
        if n < k:
            return False
        mus = np.zeros((k, d))
        cen = np.zeros(d)
        for i in range(n):
            for j in range(d):
                cen[j] += Z[i, j]
        cn = 0.0
        for j in range(d):
            cn += cen[j] * cen[j]
        cn = math.sqrt(cn)
        for j in range(d):
            mus[0, j] = cen[j] / cn if cn > 0.0 else 0.0
        for c in range(1, k):
            bs = -1.7976931348623157e308
            bi = 0
            for i in range(n):
                md = 1.7976931348623157e308
                for pv in range(c):
                    dot = 0.0
                    for j in range(d):
                        dot += mus[pv, j] * Z[i, j]
                    dist = 1.0 - min(max(dot, -1.0), 1.0)
                    if dist < md:
                        md = dist
                if md > bs:
                    bs = md
                    bi = i
            for j in range(d):
                mus[c, j] = Z[bi, j]
        kap = np.full(k, 10.0)
        lno = np.full(k, lnorm(d, 10.0))
        pis = np.full(k, 1.0 / k)
        last = -1.7976931348623157e308
        best = -1.7976931348623157e308
        pat = 0
        min_soft = min_frac * n
        logp = np.zeros(k)
        ex = np.zeros(k)
        for _it in range(150):
            tot = 0.0
            for i in range(n):
                for c in range(k):
                    dot = 0.0
                    for j in range(d):
                        dot += mus[c, j] * Z[i, j]
                    logp[c] = math.log(max(pis[c], 1e-10)) + lno[c] + kap[c] * dot
                mx = logp[0]
                for c in range(1, k):
                    if logp[c] > mx:
                        mx = logp[c]
                se = 0.0
                for c in range(k):
                    ex[c] = math.exp(logp[c] - mx)
                    se += ex[c]
                for c in range(k):
                    R[i, c] = ex[c] / se
                tot += mx + math.log(se)
            if abs(tot - last) / n < 1e-5:
                break
            if tot > best + 1e-6:
                best = tot
                pat = 0
            else:
                pat += 1
                if pat >= 10:
                    break
            last = tot
            sumr = np.zeros(k)
            nxt = np.zeros((k, d))
            for i in range(n):
                for c in range(k):
                    sumr[c] += R[i, c]
                    for j in range(d):
                        nxt[c, j] += R[i, c] * Z[i, j]
            for c in range(k):
                if sumr[c] < min_soft:
                    return False
            for c in range(k):
                pis[c] = sumr[c] / n
                nr = 0.0
                for j in range(d):
                    nr += nxt[c, j] * nxt[c, j]
                nr = math.sqrt(nr)
                for j in range(d):
                    mus[c, j] = nxt[c, j] / nr if nr > 0.0 else 0.0
                rb = nr / max(sumr[c], 1e-9)
                kap[c] = ckappa(rb, d, max(math.floor(sumr[c] + 0.5), 2.0))
                lno[c] = lnorm(d, kap[c])
        return True

    @njit(cache=False)
    def em_many(Zs, k, min_frac, Rs, oks):
        for b in range(Zs.shape[0]):
            oks[b] = em(Zs[b], k, min_frac, Rs[b])

    _NB["em"] = em_many
    return em_many


def vmf_em_many(Z, k, min_frac):
    """runVmfEm on each of B data sets (numba, Kotlin's loop order) -> (R (B, n, k), ok (B,))."""
    B, n, _d = Z.shape
    R = np.zeros((B, n, k))
    ok = np.zeros(B, dtype=np.bool_)
    _nb()(np.ascontiguousarray(Z, dtype=np.float64), k, float(min_frac), R, ok)
    return R, ok


EM_IMPL = {"fn": vmf_em_many}


def forced_k_labels(Z, k, mcs):
    """performVmfKMeans(maxK = k, minClusterFrac = mcs / n, marginalEps = -1e9) on each of B data sets -> list of label arrays
    (the winning k' <= k's hard assignment) or None (k = 2 collapsed or under minSize)."""
    B, n, _d = Z.shape
    frac = mcs / n
    min_size = max(int(n * frac), 1)
    amax = min(k, n // min_size)
    out = [None] * B
    if amax < 2:
        return out
    alive = np.ones(B, dtype=bool)
    for kk in range(2, amax + 1):
        idx = np.nonzero(alive)[0]
        if idx.size == 0:
            break
        R, ok = EM_IMPL["fn"](Z[idx], kk, frac)
        for j, b in enumerate(idx):
            if not ok[j]:
                alive[b] = False
                continue
            lab = np.argmax(R[j], axis=1)
            if np.bincount(lab, minlength=kk).min() < min_size:
                alive[b] = False
                continue
            out[b] = lab
    return out


class DenseRows:
    """Routing primitives over materialised unit rows U (n, D)."""

    def __init__(self, U):
        self.U = U
        self.n = U.shape[0]

    def csum(self, idx):
        return self.U[idx].sum(axis=0)

    def dots(self, M):
        return self.U @ M


def fit_mu(rows, idx):
    """fitVmfParams' mean: the normalised sum of the cluster's 512 rows, rounded to float32 (FloatArray)."""
    s = rows.csum(idx)
    nrm = math.sqrt(float(s @ s))
    if nrm == 0.0:
        mu = np.zeros_like(s)
        mu[0] = 1.0
        return mu
    return (s / nrm).astype(np.float32).astype(np.float64)


def route(rows, mus):
    S = rows.dots(np.stack(mus, axis=1))
    lab = np.argmax(S, axis=1)
    return [np.nonzero(lab == c)[0] for c in range(len(mus))]


def sep_from_stats(stats):
    """StatisticsUtils.chanceCorrectedSeparation over (n_c, sum_c) pairs (non-empty)."""
    st = [(nc, s) for nc, s in stats if nc > 0]
    if not st:
        return 0.0
    n = float(sum(nc for nc, _ in st))
    if n < 2.0:
        return 0.0
    tot = sum(s for _, s in st)
    ww = sum(nc * nc - float(s @ s) for nc, s in st)
    pf = sum(nc * (nc - 1.0) for nc, _ in st)
    wt = n * n - float(tot @ tot)
    exp_w = wt * pf / (n * (n - 1.0))
    if exp_w <= 1e-10:
        return 0.0
    return 1.0 - ww / exp_w


def split_replica(labels, rows, mcs, accept_eps):
    """The splitter after EM: floor pre-check, routing, the floor / weak-pair coarsening loop, the final floor. -> list of sorted
    index arrays (the routed children) or None."""
    k = int(labels.max()) + 1
    clusters = [np.nonzero(labels == c)[0] for c in range(k)]
    if any(len(c) < mcs for c in clusters):
        return None
    routed = route(rows, [fit_mu(rows, c) for c in clusters])
    while True:
        if any(len(c) < mcs for c in routed):
            if len(routed) <= 2:
                break
            surv = [c for c in routed if len(c) >= mcs]
            if len(surv) < 2:
                break
            routed = route(rows, [fit_mu(rows, c) for c in surv])
            continue
        stats = [(float(len(c)), rows.csum(c)) for c in routed]
        wi, wj, ws = -1, -1, sys.float_info.max
        for i in range(len(stats)):
            for j in range(i + 1, len(stats)):
                s = sep_from_stats([stats[i], stats[j]])
                if s < ws:
                    wi, wj, ws = i, j, s
        if wi >= 0 and ws < accept_eps and len(routed) > 2:
            merged = []
            for t in range(len(routed)):
                if t == wj:
                    continue
                merged.append(np.sort(np.concatenate([routed[wi], routed[wj]])) if t == wi else routed[t])
            routed = route(rows, [fit_mu(rows, c) for c in merged])
            continue
        break
    if any(len(c) < mcs for c in routed):
        return None
    return routed


def proxy_labels(Zc, k, mcs):
    """THE PROXY (SIN-2) on centred projected coordinates Zc (B, n, d): pcaProject's row normalisation, performVmfKMeans' forced
    k, hard assignment, the splitter's EM floor pre-check (a cluster below minClusterSize -> no partition). -> list of label
    arrays or None."""
    labs = forced_k_labels(norm_rows(Zc), k, mcs)
    out = []
    for lab in labs:
        if lab is None or np.bincount(lab).min() < mcs or len(np.bincount(lab)) < 2:
            out.append(None)
        else:
            out.append(lab)
    return out


def parts_of(lab):
    return None if lab is None else [np.nonzero(lab == c)[0] for c in range(int(lab.max()) + 1)]


class Site:
    """One site's fixed proxy state: unit rows X (n, 512); the held-fixed PCA basis (the observed site's); Zc = the centred
    projected coordinates (n, d) on which the proxy, S and G work; the observed partition at the site's k."""

    def __init__(self, X, mcs, accept_eps, k=2):
        self.X = np.asarray(X, dtype=np.float64)
        self.n, self.D = self.X.shape
        self.mcs, self.eps, self.k = mcs, accept_eps, k
        self.sd = split_dim(self.n, self.D)
        self.mean, self.V = pca_basis(self.X, self.sd)
        self.Zc = (self.X - self.mean) @ self.V
        self.lab = proxy_labels(self.Zc[None], k, mcs)[0]
        self.part = parts_of(self.lab)

    def routed_replica(self):
        """DESCRIPTIVE only: the full proposal path (routing in the 512 slice and the coarsening loop) after the proxy's EM."""
        if self.lab is None:
            return None
        return split_replica(self.lab, DenseRows(self.X), self.mcs, self.eps)


# ================================================================================================ identity precondition (SIN-3)
def agreement(part, children):
    """part: list of index arrays (proxy clusters); children: list of sets of item indices (persisted, may overlap). Best
    one-to-one matching of clusters to children maximising agreed items. -> agreed count."""
    import itertools
    if part is None:
        return 0
    m, c = len(part), len(children)
    gain = np.zeros((m, c), dtype=int)
    for i, cl in enumerate(part):
        for j, ch in enumerate(children):
            gain[i, j] = sum(1 for q in cl if int(q) in ch)
    best = 0
    if m <= c:
        for perm in itertools.permutations(range(c), m):
            best = max(best, sum(int(gain[i, perm[i]]) for i in range(m)))
    else:
        for perm in itertools.permutations(range(m), c):
            best = max(best, sum(int(gain[perm[j], j]) for j in range(c)))
    return best


def identity_check(sites, mcs, accept_eps, out=print):
    """sites: list of dict(node, X (n, 512) unit rows sorted by id, children [set of row indices]). -> (word, pooled, rows).
    The deciding agreement is the PROXY's (the function S and G use); the routed replica's is printed beside (descriptive)."""
    rows, agreed, agreed_r, total = [], 0, 0, 0
    for s in sites:
        k = len(s["children"])
        site = Site(s["X"], mcs, accept_eps, k)
        a = agreement(site.part, s["children"])
        ar = agreement(site.routed_replica(), s["children"])
        n = len(s["X"])
        agreed += a
        agreed_r += ar
        total += n
        rows.append((s["node"], n, k, 0 if site.part is None else len(site.part), a, a / n, ar))
    pooled = Fraction(agreed, total) if total else Fraction(0)
    word = "PASS" if total and pooled >= IDENTITY_MIN else "FAIL"
    mn = min((r[5] for r in rows), default=0.0)
    out("%s IDENTITY PRECONDITION (SIN-3): pooled item agreement %d / %d = %.4f over %d sites (bar >= 0.99); per-site minimum "
        "%.4f -> %s" % (TAG, agreed, total, float(pooled), len(rows), mn, word))
    out("%s   (descriptive) the routed replica (routing + coarsening after the proxy's EM): pooled %d / %d = %.4f" % (
        TAG, agreed_r, total, (agreed_r / total) if total else 0.0))
    for r in rows:
        out("%s   site %s n %d children %d proxy k %d agreed %d (%.4f); routed replica agreed %d" % (
            TAG, r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    return word, pooled, rows


# ================================================================================================ arm S (SIN-4)
def sigma_b2(corpus_rows):
    C = np.asarray(corpus_rows, dtype=np.float64)
    C = C - C.mean(axis=0)
    flat = C.ravel()
    mad = float(np.median(np.abs(flat - np.median(flat))))
    return (mad / MAD_NORMAL) ** 2


def soft_threshold(lam, s2):
    """lambda~_j = max(lambda_j - tau, s2), tau >= 0 with sum lambda~ = sum lambda (tau = inf -> all s2)."""
    lam = np.asarray(lam, dtype=np.float64)
    total = float(lam.sum())
    if total <= len(lam) * s2:
        return np.full_like(lam, s2), float("inf")

    def f(t):
        return float(np.maximum(lam - t, s2).sum()) - total
    if f(0.0) <= 0.0:
        return np.maximum(lam, s2), 0.0
    lo, hi = 0.0, float(lam.max())
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    t = 0.5 * (lo + hi)
    return np.maximum(lam - t, s2), t


def cluster_index(Y, part):
    """2-means cluster index: within-cluster SS / total SS of the rows Y under the partition."""
    Y = np.asarray(Y, dtype=np.float64)
    tot = float(((Y - Y.mean(axis=0)) ** 2).sum())
    if tot <= 0.0:
        return 1.0
    w = 0.0
    for c in part:
        Yc = Y[c]
        w += float(((Yc - Yc.mean(axis=0)) ** 2).sum())
    return w / tot


def site_eig(Zc):
    """Eigen-decomposition of the projected coordinates' covariance (ddof 0), descending."""
    C = Zc - Zc.mean(axis=0)
    lam, E = np.linalg.eigh(C.T @ C / Zc.shape[0])
    return np.maximum(lam[::-1], 0.0), E[:, ::-1]


def s_arm(site, s2, rng, sims=S_SIMS, batch=100):
    """SigClust-soft on the proxy's projection: null N(0, diag(lambda~)) in the site's projected eigen-coordinates (the proxy is
    rotation-equivariant and the cluster index rotation-invariant). -> dict(p, ci_obs, reached, tau, status)."""
    if site.part is None or len(site.part) != 2:
        return dict(p=None, status="NE:observed proxy returns no 2-way partition", reached=0)
    lam, _E = site_eig(site.Zc)
    lt, tau = soft_threshold(lam, s2)
    sd = np.sqrt(lt)
    ci_obs = cluster_index(site.Zc, site.part)
    cis = []
    done = 0
    while done < sims:
        b = min(batch, sims - done)
        Y = rng.standard_normal((b, site.n, site.sd)) * sd
        labs = proxy_labels(Y, 2, site.mcs)
        for j in range(b):
            if labs[j] is not None:
                cis.append(cluster_index(Y[j], parts_of(labs[j])))
        done += b
    reached = len(cis)
    if reached < S_REACHED_MIN:
        return dict(p=None, status="NE:%d of %d simulations reached a partition (< %d)" % (reached, sims, S_REACHED_MIN),
                    reached=reached, ci_obs=ci_obs, tau=tau)
    k_le = sum(1 for c in cis if c <= ci_obs)
    return dict(p=(1 + k_le) / (1 + reached), status="OK", reached=reached, ci_obs=ci_obs, tau=tau, k_le=k_le)


# ================================================================================================ arm G (SIN-5)
def log_chi(phi, q, s):
    """log density of s x chi_q at phi > 0."""
    x = phi / s
    return (q - 1.0) * np.log(x) - 0.5 * x * x - (q / 2.0 - 1.0) * math.log(2.0) - math.lgamma(q / 2.0) - math.log(s)


def g_pair(site, A, Bc, whiten, unwhiten, rng, N=G_N, batch=200):
    """Selective p for the pair (A, Bc) of the proxy's observed clusters on X = Zc. whiten(D) = Sigma^{-1/2} D; unwhiten(v) =
    Sigma^{1/2} v. phi ~ ||nu|| chi_q under H0 (q = the projection's dimension); proposal N(T, ||nu||^2)."""
    X = site.Zc
    nu = np.zeros(site.n)
    nu[A] = 1.0 / len(A)
    nu[Bc] = -1.0 / len(Bc)
    nn2 = 1.0 / len(A) + 1.0 / len(Bc)
    s = math.sqrt(nn2)
    Dw = whiten(nu @ X)
    T = math.sqrt(float(Dw @ Dw))
    if T <= 0.0:
        return dict(p=None, status="NE:zero mean difference", T=0.0)
    p = unwhiten(Dw / T)
    keyA, keyB = tuple(np.sort(A)), tuple(np.sort(Bc))
    phis = rng.normal(T, s, size=N)
    num_logw, den_logw = [], []
    for st in range(0, N, batch):
        ph = phis[st:st + batch]
        cs = (ph - T) / nn2
        Xb = X[None] + (cs[:, None] * nu[None, :])[:, :, None] * p[None, None, :]
        labs = proxy_labels(Xb, site.k, site.mcs)
        for j, phi in enumerate(ph):
            if phi <= 0.0 or labs[j] is None:
                continue
            keys = {tuple(c) for c in parts_of(labs[j])}
            if keyA not in keys or keyB not in keys:
                continue
            lw = float(log_chi(phi, site.sd, s)) - (-(phi - T) ** 2 / (2.0 * nn2) - math.log(s * math.sqrt(2.0 * math.pi)))
            den_logw.append(lw)
            if phi >= T:
                num_logw.append(lw)
    if not den_logw:
        return dict(p=None, status="NE:no proposal reproduced the selection", T=T)
    mx = max(den_logw)
    den = sum(math.exp(v - mx) for v in den_logw)
    num = sum(math.exp(v - mx) for v in num_logw)
    return dict(p=num / den, status="OK", T=T, kept=len(den_logw))


def g_arm(site, variant, s2, lt, E, rng, N=G_N):
    """variant 'G_I' (sigma_b^2 I) or 'G_S' (E diag(lt) E^T, S's thresholded matrix). k > 2: all pairs, p = min(1, m x min p)."""
    if site.part is None:
        return dict(p=None, status="NE:observed proxy returns no partition")
    if variant == "G_I":
        sb = math.sqrt(s2)
        whiten, unwhiten = (lambda v: v / sb), (lambda v: v * sb)
    else:
        isq, sq = 1.0 / np.sqrt(lt), np.sqrt(lt)
        whiten = lambda v: E @ ((E.T @ v) * isq)       # noqa: E731
        unwhiten = lambda v: E @ ((E.T @ v) * sq)      # noqa: E731
    pairs = [(i, j) for i in range(len(site.part)) for j in range(i + 1, len(site.part))]
    res = [g_pair(site, site.part[i], site.part[j], whiten, unwhiten, rng, N) for i, j in pairs]
    if any(r["p"] is None for r in res):
        bad = next(r for r in res if r["p"] is None)
        return dict(p=None, status=bad["status"], pairs=len(pairs))
    pmin = min(r["p"] for r in res)
    return dict(p=min(1.0, len(pairs) * pmin), status="OK", pairs=len(pairs), p_pairs=[r["p"] for r in res],
                T=[r["T"] for r in res])


def certified(p):
    """A site certifies under an arm iff its p <= 0.05."""
    return bool(p <= ALPHA)


def site_seed(tag, name):
    return int(hashlib.sha256(("%s|%s" % (tag, name)).encode("utf-8")).hexdigest(), 16) % (2 ** 32)


def run_site_arms(name, X, k, mcs, accept_eps, s2, arms, sims=S_SIMS, n_g=G_N):
    """The per-site computation of SI-NULL-TRIAD (S always at k = 2; G at the site's k) -> {arm: result dict}."""
    site = Site(X, mcs, accept_eps, k)
    site2 = site if k == 2 else Site(X, mcs, accept_eps, 2)
    lam, E = site_eig(site.Zc)
    lt, _tau = soft_threshold(lam, s2)
    out = {}
    for a in arms:
        if a == "S":
            out[a] = s_arm(site2, s2, np.random.default_rng(site_seed("S", name)), sims)
        else:
            out[a] = g_arm(site, a, s2, lt, E, np.random.default_rng(site_seed(a, name)), n_g)
        out[a]["cert"] = None if out[a].get("p") is None else certified(out[a]["p"])
        out[a]["k_proxy"] = None if site.part is None else len(site.part)
    return out


# ================================================================================================ the readout
def and3(*xs):
    if any(x is False for x in xs):
        return False
    if all(x is True for x in xs):
        return True
    return None


def or3(*xs):
    if any(x is True for x in xs):
        return True
    if all(x is False for x in xs):
        return False
    return None


def not3(x):
    return None if x is None else (not x)


def cp_upper(k, n, alpha=0.05):
    """Two-sided 95% Clopper-Pearson upper bound."""
    if n == 0:
        return 1.0
    if k >= n:
        return 1.0
    from scipy.stats import beta
    return float(beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))


def size_ok_of(k, n):
    return bool(Fraction(k, n) <= SA1_RATE and Fraction(cp_upper(k, n)).limit_denominator(10 ** 12) <= SA1_UPPER)


def sa1(certs):
    """certs: list of True / False / None over the SIZE draws -> (word True/False/None, k_lo, k_hi, n)."""
    n = len(certs)
    k_lo = sum(1 for c in certs if c is True)
    k_hi = sum(1 for c in certs if c is not False)
    a, b = size_ok_of(k_lo, n), size_ok_of(k_hi, n)
    return (a if a == b else None), k_lo, k_hi, n


def count_reach(by_anchor):
    """by_anchor: {anchor: [True/False/None x 5]} -> three-valued '>= 4 of 5 in >= 2 of the 3 anchors'."""
    lo = sum(1 for a in ANCHORS if sum(1 for c in by_anchor[a] if c is True) >= 4)
    hi = sum(1 for a in ANCHORS if sum(1 for c in by_anchor[a] if c is not False) >= 4)
    a, b = lo >= 2, hi >= 2
    return a if a == b else None


def delta_star(cert_by_delta, grid, none_word):
    """cert_by_delta: {delta: [bool...] of 5} -> smallest delta with >= 4 of 5 (None counted not certified) or none_word."""
    for dl in grid:
        if sum(1 for c in cert_by_delta.get(dl, []) if c is True) >= 4:
            return dl
    return none_word


def rank_of(dl, none_word, top):
    return top + 1.0 if dl == none_word else float(dl)


def median_ds(ds, none_word, top):
    xs = sorted(rank_of(d, none_word, top) for d in ds)
    if not xs:
        return None
    m = len(xs)
    return xs[m // 2] if m % 2 else 0.5 * (xs[m // 2 - 1] + xs[m // 2])


def fmt_word(x, yes, no):
    return "NOT EVALUABLE" if x is None else (yes if x else no)


def brier2(p, outcome):
    return (p - (1.0 if outcome else 0.0)) ** 2


def tn1_of(k2s, size_ok, reach, p_k2s):
    """k2s / size_ok / reach: {arm: three-valued} over S, G_I, G_S; p_k2s: P's three-valued K2-SENSITIVE.
    -> (TN1 word, third, nonull)."""
    third = and3(or3(*[k2s[a] for a in ARMS]), not3(p_k2s))
    any_ok_reach = or3(*[and3(size_ok[a], reach[a]) for a in ARMS], p_k2s)
    nonull = not3(any_ok_reach)
    if third is True:
        return "THIRD-NULL-WORKS", third, nonull
    if nonull is True:
        return "NO-NULL-WORKS", third, nonull
    if third is False and nonull is False:
        return "MIXED", third, nonull
    return "NOT EVALUABLE", third, nonull


def _c(res, s, arm):
    return res.get(s, {}).get(arm, {}).get("cert")


def readout(res, p_record, identity, out=print):
    """res: {site name: {arm: {"cert": True/False/None, "p": ...}}} over SIZE ('SIZE_<anchor>_n<n>_g<g>'), the power grid
    ('PL_<anchor>_n<n>_d<d>_D<delta>' record + extra) and the descriptive sites; p_record: {PL site: True/False/None} (P from
    CERT-PLANTED's cpl_sites.csv); identity: (word, pooled, rows). Prints every registered line; returns the verdict dict."""
    v = {}
    out("SI-NULL-TRIAD READOUT. %s" % REG)
    out("pool: TRAIN-only reader (embeddings_cache.db mode=ro&immutable=1 through cert_split_dip.py's assembly); no EVAL table "
        "opened")
    out("IDENTITY PRECONDITION (SIN-3): %s (pooled agreement %.4f, bar 0.99)" % (identity[0], float(identity[1])))
    if identity[0] != "PASS":
        out("SI-NULL-TRIAD: REFUSED (the proxy fails its identity check): S and G NOT EVALUABLE; SA1 / SA2 / TN1 / F-SN not "
            "scored; P1-P4 NOT SCORED")
        v["refused"] = True
        return v
    size_names = ["SIZE_%s_n%d_g%d" % (a, n, g) for a in ANCHORS for n in SIZES for g in range(SIZE_PER_CELL)]
    size_ok, reach, k2s = {}, {}, {}
    for arm in ARMS:
        certs = [_c(res, s, arm) for s in size_names]
        w, klo, khi, n = sa1(certs)
        size_ok[arm] = w
        rate = Fraction(klo, n)
        out("SA1 %s: %d of %d SIZE draws certified (rate %.4f; 95%% CP upper %.4f)%s -> %s" % (
            ARM_LABEL[arm], klo, n, float(rate), cp_upper(klo, n),
            "" if klo == khi else "; with the %d NOT EVALUABLE draws counted certified: %d" % (khi - klo, khi),
            fmt_word(w, "SIZE-OK", "NOT SIZE-OK")))
        by_anchor = {a: [_c(res, "PL_%s_n%d_d%d_D%s" % (a, DECIDING_N, d, DELTA_SA2), arm) for d in DRAWS] for a in ANCHORS}
        reach[arm] = count_reach(by_anchor)
        k2s[arm] = and3(size_ok[arm], reach[arm])
        out("SA2 %s: delta 2, n 486, certified of 5 per anchor %s; >= 4 of 5 in >= 2 of 3: %s -> %s" % (
            ARM_LABEL[arm], {a: sum(1 for c in by_anchor[a] if c is True) for a in ANCHORS},
            fmt_word(reach[arm], "yes", "no"), fmt_word(k2s[arm], "K2-SENSITIVE", "NOT K2-SENSITIVE")))
    p_by_anchor = {a: [p_record.get("PL_%s_n%d_d%d_D%s" % (a, DECIDING_N, d, DELTA_SA2)) for d in DRAWS] for a in ANCHORS}
    p_reach = count_reach(p_by_anchor)
    p_k2s = and3(None, p_reach)          # P's SIZE grid is not in CERT-PLANTED's record: unknown, decisive only if P reaches
    out("SA2 %s (READ from CERT-PLANTED): delta 2, n 486, certified of 5 per anchor %s; >= 4 of 5 in >= 2 of 3: %s -> %s "
        "(P's SA1 is not in the record; it decides nothing unless P reaches the count)" % (
            ARM_LABEL["P"], {a: sum(1 for c in p_by_anchor[a] if c is True) for a in ANCHORS}, fmt_word(p_reach, "yes", "no"),
            fmt_word(p_k2s, "K2-SENSITIVE", "NOT K2-SENSITIVE")))
    tn1, third, nonull = tn1_of(k2s, size_ok, reach, p_k2s)
    v.update(tn1=tn1, size_ok=size_ok, reach=reach, k2s=k2s, p_k2s=p_k2s)
    out("TN1 (DECIDING): %s" % tn1)
    if tn1 == "THIRD-NULL-WORKS":
        out("TN1 READING: a null whose covariance is not taken from the site (%s) certifies the planted 2-way structure at "
            "delta 2 without certifying the structureless SIZE draws, where the plain site null of record does not" %
            ", ".join(ARM_LABEL[a] for a in ARMS if k2s[a] is True))
    elif tn1 == "NO-NULL-WORKS":
        out("TN1 READING: no SIZE-OK arm certifies >= 4 of 5 at delta 2 in >= 2 anchors")
    elif tn1 == "MIXED":
        out("TN1 READING: MIXED (neither THIRD-NULL-WORKS nor NO-NULL-WORKS)")
    else:
        out("TN1 READING: NOT EVALUABLE (the word depends on NOT EVALUABLE sites; SIN-6)")
    refuted = or3(p_k2s, not3(or3(*[k2s[a] for a in ARMS])))
    out("FAILS (rule 8): THIRD-NULL-WORKS is refuted if P is K2-SENSITIVE or no S / G arm is: %s" %
        fmt_word(refuted, "REFUTED", "not refuted"))
    sens = [a for a in ARMS if k2s[a] is True]
    clause2_literal = (len(sens) > 0 and all(size_ok[a] is False for a in sens))
    fsn = (tn1 == "NO-NULL-WORKS") or clause2_literal
    v["fsn"] = fsn if tn1 != "NOT EVALUABLE" else None
    out("F-SN: %s (clause 1 TN1 NO-NULL-WORKS: %s; clause 2 every K2-SENSITIVE S / G arm fails SA1: %s, over %d K2-SENSITIVE "
        "arm(s); SIN-8: clause 2 is redundant under the record's definitions)" % (
            "NOT EVALUABLE" if v["fsn"] is None else ("FIRED: 'a background-covariance null resolves k = 2 sensitivity' is "
                                                       "false on the planted grid" if fsn else "NOT FIRED"),
            tn1 == "NO-NULL-WORKS", clause2_literal, len(sens)))
    # descriptive: delta* per arm
    grid = list(DELTAS_SN)
    out("DESCRIPTIVE: delta* per anchor at n 486 (smallest delta of %s with >= 4 of 5; SIN-7):" % "/".join(grid))
    dstar = {}
    for arm in ("P",) + ARMS:
        per = {}
        for a in ANCHORS:
            cb = {}
            for dl in grid:
                names = ["PL_%s_n%d_d%d_D%s" % (a, DECIDING_N, d, dl) for d in DRAWS]
                if arm == "P":
                    if dl in EXTRA_DELTAS:
                        continue
                    cb[dl] = [p_record.get(s) for s in names]
                else:
                    cb[dl] = [_c(res, s, arm) for s in names]
            per[a] = delta_star(cb, [g for g in grid if g in cb], NONE_WORD_SN)
        dstar[arm] = median_ds(list(per.values()), NONE_WORD_SN, 12.0)
        out("  %s: %s; median %s" % (ARM_LABEL[arm], per, "> 12" if dstar[arm] == 13.0 else dstar[arm]))
    # n 441 descriptive
    for arm in ARMS:
        c441 = {dl: sum(1 for a in ANCHORS for d in DRAWS if _c(res, "PL_%s_n441_d%d_D%s" % (a, d, dl), arm) is True)
                for dl in grid}
        out("DESCRIPTIVE n 441 %s certified of 15 per delta: %s" % (ARM_LABEL[arm], c441))
    # descriptive: the joint run's other sites (CERT-SPLIT-DIP's grid at R512) and G12's real sites (never a certificate)
    groups = [("CERT-SPLIT-DIP fresh plants delta %s (both sizes)" % dl,
               lambda s, dl=dl: s.startswith("CSD_") and s.endswith("_D%s" % dl)) for dl in ("0", "2", "3", "4", "5", "6", "8",
                                                                                         "10")]
    groups += [("CERT-SPLIT-DIP elongation controls E1 + E2", lambda s: s.startswith(("E1_", "E2_")) and "_256_" not in s),
               ("CERT-SPLIT-DIP merged pairs", lambda s: s.startswith("KK_")),
               ("G12's real sites (DESCRIPTIVE ONLY, never a certificate)", lambda s: s.startswith("G12_"))]
    for label, pred in groups:
        names = [s for s in res if pred(s)]
        if not names:
            continue
        out("DESCRIPTIVE %s: %s" % (label, "; ".join(
            "%s %d of %d (NOT EVALUABLE %d)" % (ARM_LABEL[arm], sum(1 for s in names if _c(res, s, arm) is True), len(names),
                                               sum(1 for s in names if _c(res, s, arm) is None)) for arm in ARMS)))
    # predictions
    out("PREDICTIONS (Brier; NOT SCORED where the word is NOT EVALUABLE):")
    for arm in ARMS:
        out("  P1 SA1 SIZE-OK %s p %.2f: %s" % (ARM_LABEL[arm], P1_P[arm], "NOT SCORED" if size_ok[arm] is None else
                                                "Brier %.4f" % brier2(P1_P[arm], size_ok[arm])))
    for arm in ARMS:
        out("  P2 SA2 K2-SENSITIVE %s p %.2f: %s" % (ARM_LABEL[arm], P2_P[arm], "NOT SCORED" if k2s[arm] is None else
                                                     "Brier %.4f" % brier2(P2_P[arm], k2s[arm])))
    if tn1 == "NOT EVALUABLE":
        out("  P3 TN1: NOT SCORED")
    else:
        b = sum((P3_P[w] - (1.0 if w == tn1 else 0.0)) ** 2 for w in P3_P)
        out("  P3 TN1 THIRD 0.20 / NO 0.10 / MIXED 0.70: outcome %s, Brier %.4f" % (tn1, b))
    if not sens:
        out("  P4 median delta* over sensitive arms 1 [0.5, 2]: NOT SCORED (no K2-SENSITIVE arm)")
    else:
        md = median_ds([("> 12" if dstar[a] == 13.0 else dstar[a]) for a in sens], NONE_WORD_SN, 12.0)
        held = bool(P4_BAND[1] <= md <= P4_BAND[2])
        out("  P4 median delta* over sensitive arms 1 [0.5, 2]: %s -> %s" % (md, "HELD" if held else "FAILED"))
    out(CAVEAT_G)
    out(DOES_NOT_SHOW)
    return v
