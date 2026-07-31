"""Hierarchical partial-pooling Bradley-Terry over a run's cells.

WHAT THIS IS FOR. The arena fits every cell independently, which is why small cells
are noisy, why separation blows up the per-cell Fisher information, and why the
aggregate standard error needed an arithmetic floor to stay sane. A hierarchical
model fixes all three at once by treating each cell's strength vector as drawn
around a shared vector:

    theta[cell, model] = mu[model] + tau * z[cell, model]

    mu   -- the strength every cell shares
    tau  -- how far cells depart from it
    z    -- standardised per-cell deviation

TAU IS THE POINT. The thesis's central empirical question is whether different
cells carry different true model rankings. Right now that is answered with
permutation nulls, a leaf-substructure test, and a domain screen whose correlation
with within-domain leaf agreement is +0.072. In this model it is a PARAMETER:

    tau -> 0   cells share one ranking; a per-cell profile carries nothing a single
               global ranking does not, and pooling is the correct estimator
    tau  > 0   cells genuinely diverge, and by how much is estimated directly

So this reports the quantity the apparatus was built to approximate, with an
interval, from one fit.

WHY IT IS OFFLINE AND IN PYTHON. It needs a sampler. The arena needs a point
estimate per round, fast, to schedule the next batch -- the penalised MM fit is
right for that job and stays. This runs afterwards on the verdicts already stored,
so it applies to runs that have ALREADY completed. No re-run is required to use it.

ESTIMATION. MAP by gradient ascent on the exact hierarchical log-posterior, plus a
parametric bootstrap for intervals. No autodiff dependency: the Bradley-Terry
gradient is analytic. This is deliberately not full HMC -- for the interval on tau,
which is what matters here, a bootstrap over resampled verdicts is adequate and has
no sampler-tuning failure modes to debug.

    python tools/analysis/hierarchical_bt.py <ratings.db> [--condition MAIN] [--boot 200]

Ties are half-weighted (each tie contributes half a win each way), matching the
"half" convention used throughout the thesis.
"""
import sqlite3, sys, math, random
from collections import defaultdict


def load(db, condition):
    """-> (models, cells, wins) where wins[(cell, i, j)] = weighted wins of i over j."""
    S = sqlite3.connect(db)
    rows = list(S.execute(
        "select node_id, winner, loser, is_tie from match_history "
        "where node_id is not null and condition = ?", (condition,)))
    if not rows:
        raise SystemExit(f"no verdicts for condition {condition} in {db}")
    models = sorted({r[1] for r in rows} | {r[2] for r in rows})
    cells = sorted({r[0] for r in rows})
    mi = {m: i for i, m in enumerate(models)}
    ci = {c: i for i, c in enumerate(cells)}
    wins = defaultdict(float)
    for node, w, l, tie in rows:
        c, a, b = ci[node], mi[w], mi[l]
        if tie:
            wins[(c, a, b)] += 0.5
            wins[(c, b, a)] += 0.5
        else:
            wins[(c, a, b)] += 1.0

    # Jeffreys smoothing, Beta(0.5, 0.5), applied only to pairs that HAVE data.
    #
    # Without it this model is unusable. A cell where one model wins every one of its
    # handful of comparisons is completely separated: the likelihood is maximised by
    # sending that cell's theta gap to infinity, there is no interior optimum, and the
    # hierarchy absorbs the divergence by inflating tau. Measured on the completed
    # computer-science run before this was added: tau = 3.49 with a bootstrap interval
    # of [0.002, 4.81], while the same fit's per-cell rankings agreed with the global
    # ranking at rho 0.83-0.96. Those two statements cannot both be true; the tau was an
    # artefact of separation, not a measurement of dispersion.
    #
    # Half a win each way keeps 0 < p < 1 strictly, so every cell has a finite optimum.
    # This is the same remedy BtMmFitter applies (DEFAULT_PRIOR_STRENGTH = 0.5) and for
    # the same reason. Restricting it to observed pairs matters: adding phantom wins to
    # unobserved pairs would silently connect a disconnected comparison graph and hide
    # exactly the coverage problem the mathematics re-run existed to expose.
    seen = {(c, a, b) for (c, a, b) in wins}
    for (c, a, b) in list(seen):
        if (c, b, a) in seen and a < b:
            wins[(c, a, b)] += 0.5
            wins[(c, b, a)] += 0.5
        elif (c, b, a) not in seen:
            wins[(c, a, b)] += 0.5
            wins[(c, b, a)] = wins.get((c, b, a), 0.0) + 0.5
    return models, cells, dict(wins)


def neg_log_post(mu, z, log_tau, wins, C, M, prior_mu=2.0):
    """Negative log posterior, and its gradients wrt mu, z, log_tau."""
    tau = math.exp(log_tau)
    theta = [[mu[m] + tau * z[c][m] for m in range(M)] for c in range(C)]
    nll = 0.0
    g_mu = [0.0] * M
    g_z = [[0.0] * M for _ in range(C)]
    g_tau = 0.0
    for (c, a, b), w in wins.items():
        if w == 0.0:
            continue
        d = theta[c][a] - theta[c][b]
        # w * log sigmoid(d)
        nll -= w * (-math.log1p(math.exp(-d)) if d > -30 else d)
        s = 1.0 / (1.0 + math.exp(d)) if d > -30 else 1.0    # 1 - sigmoid(d)
        g = w * s
        g_mu[a] += g; g_mu[b] -= g
        g_z[c][a] += g * tau; g_z[c][b] -= g * tau
        g_tau += g * (z[c][a] - z[c][b]) * tau
    # priors: z ~ N(0,1) (the non-centred hierarchy), mu ~ N(0, prior_mu^2),
    # log_tau ~ N(0,1) which is a weakly informative half-normal-ish prior on tau
    for c in range(C):
        for m in range(M):
            nll += 0.5 * z[c][m] ** 2
            g_z[c][m] -= z[c][m]
    for m in range(M):
        nll += 0.5 * (mu[m] / prior_mu) ** 2
        g_mu[m] -= mu[m] / prior_mu ** 2
    nll += 0.5 * log_tau ** 2
    g_tau -= log_tau
    return nll, g_mu, g_z, g_tau


def fit(wins, C, M, iters=4000, lr=0.05):
    mu = [0.0] * M
    z = [[0.0] * M for _ in range(C)]
    log_tau = math.log(0.3)
    m_mu = [0.0] * M; m_z = [[0.0] * M for _ in range(C)]; m_t = 0.0
    for it in range(iters):
        _, g_mu, g_z, g_tau = neg_log_post(mu, z, log_tau, wins, C, M)
        # gradient ASCENT on the log posterior == descent on nll; g_* are d(logpost)
        for m in range(M):
            m_mu[m] = 0.9 * m_mu[m] + 0.1 * g_mu[m]
            mu[m] += lr * m_mu[m]
        for c in range(C):
            for m in range(M):
                m_z[c][m] = 0.9 * m_z[c][m] + 0.1 * g_z[c][m]
                z[c][m] += lr * m_z[c][m]
        m_t = 0.9 * m_t + 0.1 * g_tau
        log_tau += lr * m_t
        log_tau = max(-8.0, min(2.0, log_tau))
        # sum-to-zero identification on mu
        avg = sum(mu) / M
        mu = [x - avg for x in mu]
    return mu, z, math.exp(log_tau)


def spearman(a, b):
    n = len(a)
    def rk(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n; i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]: j += 1
            for k in range(i, j + 1): r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b)
    ma, mb = sum(ra) / n, sum(rb) / n
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / den if den else float('nan')


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    db = sys.argv[1]
    cond = 'MAIN'
    boot = 200
    if '--condition' in sys.argv: cond = sys.argv[sys.argv.index('--condition') + 1]
    if '--boot' in sys.argv: boot = int(sys.argv[sys.argv.index('--boot') + 1])

    models, cells, wins = load(db, cond)
    M, C = len(models), len(cells)
    print(f"hierarchical Bradley-Terry -- {db}  condition={cond}")
    print(f"{M} models, {C} cells, {sum(wins.values()):.0f} weighted comparisons\n")

    mu, z, tau = fit(wins, C, M)
    print("GLOBAL STRENGTHS (mu, sum-to-zero)")
    for i in sorted(range(M), key=lambda i: -mu[i]):
        print(f"  {models[i]:<34} {mu[i]:+.4f}")

    print(f"\nTAU (cross-cell dispersion) = {tau:.4f}")

    # parametric bootstrap on tau: resample verdicts from the fitted probabilities
    rng = random.Random(42)
    taus = []
    keys = list(wins.keys())
    for _ in range(boot):
        w2 = {}
        for (c, a, b) in keys:
            n = wins[(c, a, b)] + wins.get((c, b, a), 0.0)
            if n <= 0: continue
            d = (mu[a] + tau * z[c][a]) - (mu[b] + tau * z[c][b])
            p = 1.0 / (1.0 + math.exp(-d))
            k = sum(1 for _ in range(int(round(n))) if rng.random() < p)
            w2[(c, a, b)] = float(k)
            w2[(c, b, a)] = float(int(round(n)) - k)
        _, _, t = fit(w2, C, M, iters=1200)
        taus.append(t)
    taus.sort()
    lo, hi = taus[int(0.025 * len(taus))], taus[int(0.975 * len(taus))]
    print(f"  parametric bootstrap 95% interval: [{lo:.4f}, {hi:.4f}]  ({boot} draws)")
    print()
    if hi < 0.05:
        print("  READING: tau is small with the interval excluding meaningful dispersion.")
        print("  Cells share one ranking. A per-cell profile carries little a single")
        print("  global ranking does not, and pooling is the correct estimator.")
    elif lo > 0.10:
        print("  READING: tau is clearly positive. Cells carry genuinely different")
        print("  rankings and a per-cell profile is not redundant.")
    else:
        print("  READING: tau is not resolved by this run. The interval spans both")
        print("  'cells agree' and 'cells differ'; do not claim either direction.")

    # how far pooling moves each cell's ranking away from its independent fit
    print("\nSHRINKAGE per cell -- Spearman(pooled cell ranking, global mu):")
    for c in range(C):
        th = [mu[m] + tau * z[c][m] for m in range(M)]
        print(f"  {cells[c]:<14} rho_vs_global = {spearman(th, mu):+.3f}")
    print("\n  Values near 1.000 mean the cell is pulled almost entirely onto the")
    print("  shared ranking, which is what small tau implies.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
