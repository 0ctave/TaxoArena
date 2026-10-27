"""Bradley-Terry fits for the simulator and the replay's diagnostic fits.

THE FIT OF RECORD is rejudge_grok.mm_fit (via judge_free_tests.board_from; synthesis Stage A: "The Python fit is the fit
of record"); the replay's identity leg uses it unchanged. The batched numpy MM below is the SIMULATOR's engine: the same
MM iteration (Jeffreys prior 0.5 pseudo-match per observed pair, Gauss-Jacobi update, mean-1 normalisation, stop at
max |delta p| < tol), vectorised over bootstrap boards; the selftest requires agreement with rj.mm_fit to 1e-8 in
theta. bt_offset_batch is a Newton fit of the same likelihood with a per-match offset (the length-adjusted fit of the
G23 length conjunct); with zero offsets it maximises the same penalised likelihood as MM (selftest: agreement 1e-7).
"""
import numpy as np

PRIOR = 0.5


def mm_fit_batch(W, N, prior=PRIOR, tol=1e-12, maxit=2000):
    """W[b,i,j] = (fractional) wins of i over j, N[b,i,j] = matches between i and j (symmetric). Returns theta (b, M),
    each row demeaned. A 2-D input returns a 1-D theta."""
    W = np.asarray(W, dtype=float)
    N = np.asarray(N, dtype=float)
    squeeze = W.ndim == 2
    if squeeze:
        W, N = W[None], N[None]
    present = (N > 0).astype(float)
    Wtot = (W + prior * present).sum(axis=2)
    Np = N + 2.0 * prior * present
    nb, M, _ = W.shape
    p = np.ones((nb, M))
    active = np.arange(nb)
    for _ in range(maxit):
        pa = p[active]
        with np.errstate(divide="ignore", invalid="ignore"):
            den = (Np[active] / (pa[:, :, None] + pa[:, None, :])).sum(axis=2)
        new = np.where(den > 0, Wtot[active] / np.where(den > 0, den, 1.0), pa)
        new = new / new.mean(axis=1, keepdims=True)
        delta = np.abs(new - pa).max(axis=1)
        p[active] = new
        active = active[delta >= tol]
        if active.size == 0:
            break
    th = np.log(np.maximum(p, 1e-300))
    th = th - th.mean(axis=1, keepdims=True)
    return th[0] if squeeze else th


def question_tensors(rows, midx, qidx):
    """rows: iterable of (a, b, q, wa) with wa in [0, 1] the share of the match won by a. Returns (Wq, Nq) of shape
    (Q, M, M): per question the wins matrix and the match-count matrix."""
    Q, M = len(qidx), len(midx)
    Wq = np.zeros((Q, M, M))
    Nq = np.zeros((Q, M, M))
    for a, b, q, wa in rows:
        i, j, k = midx[a], midx[b], qidx[q]
        Wq[k, i, j] += wa
        Wq[k, j, i] += 1.0 - wa
        Nq[k, i, j] += 1.0
        Nq[k, j, i] += 1.0
    return Wq, Nq


def boot_counts(rng, Q, B):
    """B question-bootstrap draws as a (B, Q) count matrix (resampling the Q questions with replacement)."""
    idx = rng.integers(0, Q, size=(B, Q))
    counts = np.zeros((B, Q))
    np.add.at(counts, (np.repeat(np.arange(B), Q), idx.ravel()), 1.0)
    return counts


def boot_boards(Wq, Nq, counts, **kw):
    W = np.tensordot(counts, Wq, axes=(1, 0))
    N = np.tensordot(counts, Nq, axes=(1, 0))
    return mm_fit_batch(W, N, **kw)


def pair_moments(theta, pairs):
    """theta (B, M); pairs list of (i, j). Returns p = share of boards with theta_i > theta_j, m = mean difference,
    s = sd (ddof 1): systematic_budget.build()'s three moments."""
    ii = np.array([i for i, _ in pairs], dtype=int)
    jj = np.array([j for _, j in pairs], dtype=int)
    d = theta[:, ii] - theta[:, jj]
    return (d > 0).mean(axis=0), d.mean(axis=0), d.std(axis=0, ddof=1)


def bt_offset_batch(i, j, y, off, wts, M, prior=PRIOR, iters=60, tol=1e-10):
    """Newton fit of P(i beats j) = sigma(theta_i - theta_j + off) on weighted rows, one board per row of `wts`
    (shape (nb, R)); the prior is PRIOR pseudo-win each way per pair with positive weight in the board (rj.mm_fit's).
    Returns theta (nb, M), demeaned."""
    i = np.asarray(i, dtype=int); j = np.asarray(j, dtype=int)
    y = np.asarray(y, dtype=float); off = np.asarray(off, dtype=float)
    wts = np.atleast_2d(np.asarray(wts, dtype=float))
    nb, R = wts.shape
    lo, hi = np.minimum(i, j), np.maximum(i, j)
    keys = lo * M + hi
    uk, inv = np.unique(keys, return_inverse=True)
    pw = np.zeros((nb, uk.size))
    np.add.at(pw, (slice(None), inv), wts)
    pi_, pj_ = uk // M, uk % M
    I = np.concatenate([i, pi_]); J = np.concatenate([j, pj_])
    Y = np.concatenate([y, np.full(uk.size, 0.5)])
    O = np.concatenate([off, np.zeros(uk.size)])
    Wt = np.concatenate([wts, 2.0 * prior * (pw > 0)], axis=1)
    A = np.zeros((I.size, M))
    A[np.arange(I.size), I] += 1.0
    A[np.arange(I.size), J] -= 1.0
    th = np.zeros((nb, M))
    ones = np.ones((M, M)) / M
    for _ in range(iters):
        z = th @ A.T + O[None, :]
        p = 1.0 / (1.0 + np.exp(-z))
        g = (Wt * (Y[None, :] - p)) @ A
        h = Wt * p * (1.0 - p)
        H = -np.einsum("rm,br,rn->bmn", A, h, A) - ones[None] - 1e-12 * np.eye(M)[None]
        step = np.linalg.solve(H, -g[:, :, None])[:, :, 0]
        th = th + step
        th = th - th.mean(axis=1, keepdims=True)
        if np.abs(step).max() < tol:
            break
    return th
