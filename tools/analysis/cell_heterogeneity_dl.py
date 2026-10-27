"""Between-cell heterogeneity in model strength: DerSimonian-Laird random effects.

THE QUESTION. Do a domain's cells rank models differently from one another by more
than sampling noise? That is the premise the whole partition claim rests on: if every
cell carries the same ranking, a per-cell profile tells a router nothing a single
global ranking does not.

WHY THIS ESTIMATOR. The obvious approach -- a hierarchical model
theta[cell,model] = mu[model] + tau*z[cell,model] fitted by MAP -- DOES NOT WORK, and
an earlier version of this analysis failed exactly that way. In the non-centred
parameterisation the posterior is always improved by growing tau and shrinking z with
tau*z held fixed: shrinking C*M standardised deviations saves far more prior penalty
than the log-tau prior costs. MAP estimation of a hierarchical variance is degenerate
there, which is why such models are fitted with MCMC and not with an optimiser.
Measured on the computer-science run: tau = 3.49, then 3.72 after adding Jeffreys
smoothing, with a bootstrap interval of [0.01, 4.35] -- while the same fit's per-cell
rankings agreed with the global ranking at rho 0.80-0.93. Contradictory, and the
smoothing changing nothing is what ruled out separation as the cause.

DerSimonian-Laird sidesteps the degeneracy instead of fighting it. Each cell is fitted
INDEPENDENTLY (which the arena already does), giving an estimate and a within-cell
variance. The observed spread across cells is then split into the part sampling noise
explains and the part it does not:

    Q     = sum_c w_c (y_c - ybar)^2         w_c = 1/v_c        (weighted spread)
    tau^2 = max(0, (Q - df) / C_dl)          df = #cells - 1    (true heterogeneity)
    I^2   = max(0, (Q - df) / Q)                                (share of variance
                                                                 that is real)

Closed form, no optimiser, no ridge, and Q has a chi-square(df) reference distribution
under the null of no heterogeneity. It consumes exactly the per-cell fits and standard
errors the arena already produces.

APPLIED PER MODEL. A Bradley-Terry fit is identified only up to an additive constant
per cell, so each cell's strength vector is centred to sum zero before cells are
compared -- otherwise arbitrary per-cell offsets would masquerade as heterogeneity.
Then one DL analysis is run per model: tau^2 for model m answers "does this model's
standing move across cells by more than its standard errors allow?".

    python tools/analysis/cell_heterogeneity_dl.py <ratings.db> [--condition MAIN]

CAVEAT kept in view: centring induces correlation between models within a cell, so the
per-model analyses are marginal rather than jointly independent. That inflates nothing
in tau^2 itself but means the per-model p-values should not be combined naively.
"""
import sqlite3, sys, math
from collections import defaultdict

PRIOR = 0.5   # Jeffreys Beta(0.5,0.5), matching BtMmFitter.DEFAULT_PRIOR_STRENGTH


# ── chi-square upper tail, via the regularised incomplete gamma ────────────────
def _gammainc_upper(a, x):
    if x <= 0: return 1.0
    if x < a + 1.0:                       # series for the lower tail, then complement
        term = 1.0 / a; s = term; n = 0
        while n < 1000:
            n += 1; term *= x / (a + n); s += term
            if abs(term) < abs(s) * 1e-14: break
        return 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for the upper tail (Lentz)
    tiny = 1e-300
    b = x + 1.0 - a; c = 1.0 / tiny; d = 1.0 / b; h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny: d = tiny
        c = b + an / c
        if abs(c) < tiny: c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14: break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(q, df):
    if df <= 0: return 1.0
    return max(0.0, min(1.0, _gammainc_upper(df / 2.0, q / 2.0)))


# ── penalised Bradley-Terry fit + Fisher SEs, mirroring BtMmFitter ────────────
def invert(A):
    n = len(A)
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-13: return None
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        M[col] = [v / p for v in M[col]]
        for r in range(n):
            if r == col: continue
            f = M[r][col]
            if f: M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


def fit_cell(pairs, models):
    """pairs[(i,j)] = (wins_i, wins_j, n). Returns (theta centred, se) or None."""
    K = len(models)
    W = [0.0] * K; N = defaultdict(float)
    any_data = False
    for (i, j), (wi, wj, n) in pairs.items():
        if n <= 0: continue
        any_data = True
        W[i] += wi + PRIOR; W[j] += wj + PRIOR
        N[(i, j)] += n + 2 * PRIOR; N[(j, i)] += n + 2 * PRIOR
    if not any_data: return None
    p = [1.0] * K
    for _ in range(2000):
        new = []
        for m in range(K):
            den = sum(N[(m, o)] / (p[m] + p[o]) for o in range(K) if o != m and N[(m, o)])
            new.append(W[m] / den if den > 0 else p[m])
        g = sum(new) / K
        if g <= 0: return None
        new = [v / g for v in new]
        if max(abs(a - b) for a, b in zip(new, p)) < 1e-12:
            p = new; break
        p = new
    theta = [math.log(max(v, 1e-300)) for v in p]
    mean = sum(theta) / K
    theta = [t - mean for t in theta]          # sum-to-zero: required to compare cells
    # Fisher information under the penalised likelihood
    F = [[0.0] * K for _ in range(K)]
    for (i, j), (wi, wj, n) in pairs.items():
        if n <= 0: continue
        d = math.exp(theta[i]) + math.exp(theta[j])
        pij = math.exp(theta[i]) / d if d > 0 else 0.5
        nij = n + 2 * PRIOR
        info = nij * pij * (1 - pij)
        F[i][i] += info; F[j][j] += info; F[i][j] -= info; F[j][i] -= info
    Fc = [[F[i][j] + 1.0 for j in range(K)] for i in range(K)]   # + J
    inv = invert(Fc)
    if inv is None: return None
    se = []
    for i in range(K):
        v = inv[i][i] - 1.0 / (K * K)        # constrained covariance
        se.append(math.sqrt(max(v, 1e-9)))
    return theta, se


def load(db, condition):
    S = sqlite3.connect(db)
    rows = list(S.execute("select node_id,winner,loser,is_tie from match_history "
                          "where node_id is not null and condition=?", (condition,)))
    if not rows: raise SystemExit(f"no verdicts for {condition} in {db}")
    models = sorted({r[1] for r in rows} | {r[2] for r in rows})
    mi = {m: i for i, m in enumerate(models)}
    cells = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))
    for node, w, l, tie in rows:
        a, b = mi[w], mi[l]
        i, j = (a, b) if a < b else (b, a)
        e = cells[node][(i, j)]
        e[2] += 1
        if tie: e[0] += 0.5; e[1] += 0.5
        elif a == i: e[0] += 1
        else: e[1] += 1
    return models, {c: {k: tuple(v) for k, v in d.items()} for c, d in cells.items()}


def dl(ys, vs):
    """DerSimonian-Laird. -> (tau2, Q, df, I2, p)"""
    k = len(ys)
    if k < 2: return 0.0, 0.0, 0, 0.0, 1.0
    w = [1.0 / v for v in vs]
    sw = sum(w)
    ybar = sum(wi * y for wi, y in zip(w, ys)) / sw
    Q = sum(wi * (y - ybar) ** 2 for wi, y in zip(w, ys))
    df = k - 1
    C = sw - sum(wi * wi for wi in w) / sw
    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    return tau2, Q, df, I2, chi2_sf(Q, df)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    db = sys.argv[1]
    cond = sys.argv[sys.argv.index('--condition') + 1] if '--condition' in sys.argv else 'MAIN'
    models, cells = load(db, cond)
    fits = {}
    for c, pairs in cells.items():
        f = fit_cell(pairs, models)
        if f: fits[c] = f
    if len(fits) < 2:
        print(f"only {len(fits)} usable cell(s); heterogeneity is undefined"); return 1
    names = sorted(fits)
    print(f"DerSimonian-Laird between-cell heterogeneity -- {db}  condition={cond}")
    print(f"{len(models)} models, {len(names)} cells\n")
    print(f"{'model':<34}{'tau^2':>9}{'tau':>8}{'I^2':>8}{'Q':>10}{'p(Q)':>9}  {'median SE':>9}")
    print('-' * 88)
    rows = []
    for m in range(len(models)):
        ys = [fits[c][0][m] for c in names]
        vs = [fits[c][1][m] ** 2 for c in names]
        tau2, Q, df, I2, p = dl(ys, vs)
        med = sorted(math.sqrt(v) for v in vs)[len(vs) // 2]
        rows.append((models[m], tau2, I2, Q, p, med))
    for name, tau2, I2, Q, p, med in sorted(rows, key=lambda r: -r[1]):
        flag = '  <-- heterogeneous' if p < 0.05 else ''
        print(f"{name:<34}{tau2:>9.4f}{math.sqrt(tau2):>8.4f}{I2*100:>7.1f}%{Q:>10.2f}{p:>9.4f}  {med:>9.4f}{flag}")
    sig = sum(1 for r in rows if r[4] < 0.05)
    med_tau2 = sorted(r[1] for r in rows)[len(rows) // 2]
    med_I2 = sorted(r[2] for r in rows)[len(rows) // 2]
    print('-' * 88)
    print(f"median tau^2 = {med_tau2:.4f}   median I^2 = {med_I2*100:.1f}%   "
          f"models with p(Q) < 0.05: {sig}/{len(rows)}")
    print()
    if med_I2 < 0.25 and sig <= max(1, len(rows) // 10):
        print("READING: between-cell variation is mostly sampling noise. Cells do not")
        print("carry materially different rankings, so a per-cell profile adds little")
        print("to a single global ranking on this domain.")
    elif med_I2 > 0.50:
        print("READING: a majority of the between-cell variance is real heterogeneity.")
        print("Cells differ by more than their standard errors allow.")
    else:
        print("READING: mixed. Some models move across cells by more than noise and")
        print("others do not; do not summarise this domain with a single verdict.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
