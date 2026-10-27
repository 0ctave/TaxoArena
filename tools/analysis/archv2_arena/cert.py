"""The certificate layer.

FUNCTIONS OF RECORD (imported, never re-implemented for a reading of record): systematic_budget.craw / cbud / nll / fit
/ summarise / mcnemar_edge / established; calibration_status.status_word (FRAMEWORK L101). `sb` is passed in by the
caller (the CLIs import systematic_budget behind the stack_judge stub, see data.import_systematic_budget).

VECTORISED TWINS (the simulator's engine; hundreds of refits per design): craw_v, cbud_v, nll_v, fit_v, loao_v,
ddev_v. The selftest requires |nll_v - sb.nll| <= 1e-9 relative, fit_v within 1e-5 of sb.fit, and cbud_v == sb.cbud to
1e-12 on synthetic edges. The replay's identity and certificate legs use the functions of record (mode "exact").

NEW RULES (design proposals, arena section 2.4-2.5; NOT registered): the binned gate (certificate B), Holm on the key
partial order, the multi-stream c~ with its MC-UNRESOLVED class, unidentified() (zero events or range separation, the
first limb of the registrar's 2026-09-23 definition; the singular-information limb is NOT implemented here and is
printed as such).

[REGISTERED 2026-09-24 at d6129cf (ARCH-V2-G22 and ARCH-V2-G23, docs/judge_v2_program.md L15208-L15265), inserted by
the engine-coder; the text above is kept and read with this bracket: the bars are registered and printed as such, a
record run uses the registered masters (ARCHV2-G22-REC-1 / ARCHV2-G23-REC-1) and R = 1,000, other runs print DEV RUN.]
"""
import math

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import beta as beta_dist
from scipy.stats import chi2, norm, poisson
from scipy.stats import t as t_dist

THRESH = 0.975
FROZEN_GROK_UNFILTERED = (-3.3172, 3.3001)   # GROK-CALIB, 920 unfiltered pair (programme L3914ff; memo section 2(6))
FROZEN_MISTRAL_920 = (-3.0438, 3.1980)       # the 920 any-gap Mistral pair (systematic_budget docstring)
GATE_BINS = (0.5, 0.7, 0.85)                 # arena section 2.5 (B): <0.5, 0.5-0.7, 0.7-0.85, >=0.85
GATE_TARGET = 1.0 - THRESH                   # the certificate's own per-edge promise, 2.5%
CHI2_1_95 = 3.84


# ------------------------------------------------------------------------------------------------ edge arrays
class EdgeArrays:
    """Columns of an edge list (dicts with keys p, m, s, agree, right, anchor, gap, [est])."""

    def __init__(self, edges, anchors=None):
        self.edges = edges
        self.p = np.array([e["p"] for e in edges], dtype=float)
        self.m = np.array([e["m"] for e in edges], dtype=float)
        self.s = np.array([e["s"] for e in edges], dtype=float)
        self.agree = np.array([e["agree"] for e in edges], dtype=float)
        self.right = np.array([bool(e["right"]) for e in edges], dtype=bool)
        self.gap = np.array([e.get("gap", 1.0) for e in edges], dtype=float)
        self.est = np.array([bool(e.get("est", False)) for e in edges], dtype=bool)
        names = anchors if anchors is not None else sorted({e["anchor"] for e in edges})
        self.anchor_names = list(names)
        code = {a: k for k, a in enumerate(self.anchor_names)}
        self.anchor = np.array([code[e["anchor"]] for e in edges], dtype=int)

    def __len__(self):
        return len(self.edges)

    def subset(self, mask):
        return EdgeArrays([e for e, k in zip(self.edges, mask) if k], self.anchor_names)


def craw_v(p):
    return np.maximum(p, 1.0 - p)


def cbud_v(E, b0, b1):
    with np.errstate(over="ignore"):             # tau -> inf gives g = 0 (never called), as math would at its cap
        tau = np.exp(b0 + b1 * E.agree)
        g = norm.cdf(np.abs(E.m) / np.sqrt(E.s ** 2 + tau ** 2))
    return np.minimum(craw_v(E.p), g)


def nll_v(par, E):
    b0, b1 = par
    tau = np.exp(np.minimum(20.0, b0 + b1 * E.agree))
    z = np.abs(E.m) / np.sqrt(E.s ** 2 + tau ** 2)
    pw = np.minimum(np.maximum(norm.cdf(-z), 1e-12), 1 - 1e-12)
    return float(-(np.log(pw[~E.right]).sum() + np.log(1 - pw[E.right]).sum()))


def fit_v(E, x0=(-3.0, 3.0)):
    r = minimize(nll_v, np.array(x0, dtype=float), args=(E,), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1])


def summarise_v(E, b0, b1, thresh=THRESH):
    """(raw called, raw wrong, budget called, budget wrong, budget nominal) = systematic_budget.summarise."""
    rc = craw_v(E.p) >= thresh
    c = cbud_v(E, b0, b1)
    bc = c >= thresh
    return int(rc.sum()), int((rc & ~E.right).sum()), int(bc.sum()), int((bc & ~E.right).sum()), float((1 - c[bc]).sum())


def loao_v(E, x0=None, fit=None, thresh=THRESH):
    """Leave-one-anchor-out out-of-fold c~ (systematic_budget.main's (2) block: full fit first, each fold started there)."""
    fit = fit or fit_v
    b0, b1 = fit(E) if x0 is None else x0
    oof = np.zeros(len(E))
    params = {}
    for k in sorted(set(E.anchor.tolist())):
        tr = E.subset(E.anchor != k)
        f0, f1 = fit(tr, x0=(b0, b1))
        params[E.anchor_names[k]] = (f0, f1)
        te = E.anchor == k
        oof[te] = cbud_v(E.subset(te), f0, f1)
    called = oof >= thresh
    return dict(oof=oof, called=called, n_called=int(called.sum()), wrong=int((called & ~E.right).sum()),
                wrong_est=int((called & ~E.right & E.est).sum()), nominal=float((1 - oof[called]).sum()),
                b0=b0, b1=b1, fold_params=params)


def ddev_v(E_est, x0=(-3.0, 3.0), fit=None):
    """Established-label refit b1 and delta-deviance vs b1 = 0 (grok_calib.item26_criteria's recipe: b0 re-maximised
    by a bounded scalar search on (-12, 4))."""
    fit = fit or fit_v
    e0, e1 = fit(E_est, x0=x0)
    null = minimize_scalar(lambda x: nll_v((x, 0.0), E_est), bounds=(-12, 4), method="bounded")
    return e1, 2.0 * (null.fun - nll_v((e0, e1), E_est)), e0


def unidentified(E):
    """Zero wrong or zero right events, or range separation of A between them (registrar 2026-09-23, first limb)."""
    w = E.agree[~E.right]; r = E.agree[E.right]
    if w.size == 0:
        return "zero wrong events"
    if r.size == 0:
        return "zero right events"
    if w.max() <= r.min() or r.max() <= w.min():
        return "range separation of A"
    return None


# --------------------------------------------------------------------------------------------- intervals / tests
def cp_ub(w, n, conf=0.95):
    """One-sided Clopper-Pearson upper bound."""
    if n == 0:
        return 1.0
    if w >= n:
        return 1.0
    return float(beta_dist.ppf(conf, w + 1, n - w))


def poisson_ub(w, conf=0.95):
    return float(0.5 * chi2.ppf(conf, 2 * (w + 1)))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def holm(pvals, alpha=0.05):
    """Holm step-down: returns a list of booleans (rejected) aligned with pvals."""
    order = sorted(range(len(pvals)), key=lambda k: pvals[k])
    m = len(pvals)
    rej = [False] * m
    for rank, k in enumerate(order):
        if pvals[k] <= alpha / (m - rank):
            rej[k] = True
        else:
            break
    return rej


def poisson_tail(observed, nominal):
    return float(1 - poisson.cdf(observed - 1, nominal)) if observed > 0 else 1.0


# ---------------------------------------------------------------------------------------------- binned gate (B)
def gate_bin(agree, bins=GATE_BINS):
    return np.searchsorted(np.asarray(bins), agree, side="right")


def gate_fit(E, bins=GATE_BINS, target=GATE_TARGET, conf=0.95, thresh=THRESH):
    """Per A-bin among raw-called edges: n, wrong(established), one-sided CP UB; callable iff UB <= target."""
    rc = craw_v(E.p) >= thresh
    b = gate_bin(E.agree, bins)
    out = []
    for k in range(len(bins) + 1):
        sel = rc & (b == k)
        n = int(sel.sum()); w = int((sel & ~E.right & E.est).sum())
        ub = cp_ub(w, n, conf)
        out.append(dict(bin=k, n=n, wrong_est=w, wrong_all=int((sel & ~E.right).sum()), ub=ub, callable=ub <= target))
    return out


def gate_loao(E, bins=GATE_BINS, target=GATE_TARGET, conf=0.95, thresh=THRESH):
    rc = craw_v(E.p) >= thresh
    b = gate_bin(E.agree, bins)
    called = np.zeros(len(E), dtype=bool)
    ub_used = np.full(len(E), np.nan)
    for k in sorted(set(E.anchor.tolist())):
        tr = E.subset(E.anchor != k)
        table = gate_fit(tr, bins, target, conf, thresh)
        te = E.anchor == k
        ok = np.array([table[x]["callable"] for x in range(len(bins) + 1)])
        ubs = np.array([table[x]["ub"] for x in range(len(bins) + 1)])
        called[te] = rc[te] & ok[b[te]]
        ub_used[te] = ubs[b[te]]
    return dict(called=called, n_called=int(called.sum()), wrong=int((called & ~E.right).sum()),
                wrong_est=int((called & ~E.right & E.est).sum()),
                nominal_raw=float((1 - craw_v(E.p)[called]).sum()), nominal_ub=float(np.nansum(ub_used[called])))


# ------------------------------------------------------------------------------------------- multi-stream c~
def mc_classes(c_streams, thresh=THRESH, conf=0.95):
    """c_streams (S, E): c~ per bootstrap stream. Mean, Monte-Carlo interval (t_{S-1}); class CALLED (lo >= thresh),
    NOT CALLED (hi < thresh) or MC-UNRESOLVED (the interval contains thresh)."""
    c = np.asarray(c_streams, dtype=float)
    S = c.shape[0]
    if S < 2:
        raise SystemExit("[MC] at least 2 streams are needed for a Monte-Carlo interval (the rule asks for >= 5)")
    mean = c.mean(axis=0); sd = c.std(axis=0, ddof=1)
    half = t_dist.ppf(0.5 + conf / 2, S - 1) * sd / math.sqrt(S)
    lo, hi = mean - half, mean + half
    cls = np.where(lo >= thresh, "CALLED", np.where(hi < thresh, "NOT CALLED", "MC-UNRESOLVED"))
    return dict(mean=mean, sd=sd, lo=lo, hi=hi, cls=cls)


# ---------------------------------------------------------------------------------------------- key tiers
def key_tiers(acc, models, gap=0.017):
    """The record's adjacency rule (ktd_check.my_tiers): read down the key accuracy, a new tier where the drop to the
    next model is >= gap. Returns a list of tiers (lists of models)."""
    order = sorted(models, key=lambda m: (-acc[m], m))
    tiers = [[order[0]]]
    for prev, cur in zip(order, order[1:]):
        if acc[prev] - acc[cur] >= gap:
            tiers.append([cur])
        else:
            tiers[-1].append(cur)
    return tiers


def mcnemar_counts(Kcol_a, Kcol_b):
    """Exact two-sided McNemar from two aligned 0/1 arrays with -1 = missing (integer arithmetic, as
    systematic_budget.mcnemar_edge). Returns (p, b, c)."""
    ok = (Kcol_a >= 0) & (Kcol_b >= 0) & (Kcol_a != Kcol_b)
    b_ = int(((Kcol_a > Kcol_b) & ok).sum()); c_ = int(((Kcol_a < Kcol_b) & ok).sum())
    n = b_ + c_
    if n == 0:
        return 1.0, 0, 0
    k = min(b_, c_)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)), b_, c_


def kish_deff(cluster_sizes, icc):
    n = float(sum(cluster_sizes))
    mk = sum(x * x for x in cluster_sizes) / n if n else 0.0
    return 1.0 + (mk - 1.0) * icc, mk


def anova_icc(values_by_cluster):
    """One-way ANOVA ICC estimator for a (binary or continuous) indicator grouped by cluster."""
    groups = [np.asarray(v, dtype=float) for v in values_by_cluster if len(v) > 0]
    k = len(groups)
    n = sum(len(g) for g in groups)
    if k < 2 or n <= k:
        return float("nan")
    grand = np.concatenate(groups).mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    msb = ssb / (k - 1); msw = ssw / (n - k)
    n0 = (n - sum(len(g) ** 2 for g in groups) / n) / (k - 1)
    den = msb + (n0 - 1) * msw
    return float((msb - msw) / den) if den > 0 else float("nan")
