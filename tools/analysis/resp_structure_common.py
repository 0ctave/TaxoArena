"""resp_structure_common.py: the shared, read-only machinery of three zero-call CPU readouts on the union model x item matrix,
registered 2026-10-04 (docs/judge_v2_program.md, commit 633255f2):
  RESP-PROFILE-INFO  tools/analysis/resp_profile_info.py   (L24388-L24400)
  CELL-DIFFICULTY    tools/analysis/cell_difficulty.py     (L24402-L24414)
  CELL-STRATA-EVAL   tools/analysis/cell_strata_eval.py    (L24416-L24428)
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. Readers only; nothing here writes except the B1
marker and the write-once outcome the three scripts name. Temp files: scratch_dir (E:/TaxoArena_tmp), imported first.

REUSED UNCHANGED (blob-pinned below; each pins its own dependencies):
  union_cells_io.py (blob:92a04543)  the objects of record (pool pv2_1575de61bb20e977, G14's EVAL set 5,907 / 5,404, the frozen
                                     TRAIN policy of UNION-AF-ROUTE sha256 8d68018c..., the inputs manifest 53021e26...), the B0-2
                                     pool line (first line of every mode), the AF-U and K_0 cells through union_af_route.load_inputs,
                                     eval_set (the EVAL key read: B1 marker, UNUSABLE_CELL, MATH-FIX overlay), pct, kish.
  cell_flips.py     (blob:998d39a7)  bh (BH step-up), the CELL-FLIPS cells and its outcome format (CELL-DIFFICULTY CD2).
  v2_declared_cells.py (through U.V) open_tw / pool_row / registry / side_items / cell_counts / structurally_complete / read_key
                                     (the TRAIN key of the gen view, table response_lite, MATH-FIX overlay), build_ud, fit (G14's
                                     reader; its G3 assert keeps every policy fit on TRAIN), train_full, run_boot.

THE IRT MODEL (registered, "fixed now"; one implementation for the three scripts):
  3PL  P_im = c_i + (1 - c_i) sigmoid(a_i (theta_m - b_i)), a_i = exp(alpha_i); guessing floor c_i FIXED at 1/options for the MC
       sources (GPQA 1/4, MMLU_PRO 1/10; the view's stratum_source naming) and 0 elsewhere (BBH, IFEVAL, MATH, MUSR).
  IRT-R1 TRAIN fit (theta of record): joint ML over the TRAIN key matrix, alternating (i) three Newton steps (observed information
       where positive definite, Fisher scoring otherwise) of every TRAIN item's (alpha_i, b_i) given theta with the ridge penalty (lambda / 2)(alpha_i^2 + b_i^2), lambda = 1.0, and (ii) one
       Fisher-scoring step of every theta_m given the items (TRAIN item weights w: the bootstrap's multiplicities, 1 at the
       point), theta re-standardised to mean 0, SD 1 (ddof 0) over the roster after each step; step halving on the (penalised)
       log-likelihood; stop when max |delta theta| < 1e-7 (3,000 iterations cap; the run refuses if not converged); the TRAIN
       items are then refitted given the final theta. Start: theta = standardised logit of TRAIN accuracy, alpha 0, b = -logit of
       the item's mean (clipped 0.02 / 0.98). Every position passed to fit_train is asserted TRAIN (SystemExit, python -O safe).
  IRT-R2 EVAL items: theta FIXED (TRAIN's), each item's (alpha_i, b_i) by the same Newton / Fisher steps with the same ridge, item
       by item (vectorised; items are independent given theta), until max |step| < 1e-8 (200 cap; the run refuses above 1e-6).
       Checked against scipy (Nelder-Mead on the penalised likelihood, item by item) in every script's irt selftest case.
  CAVEAT (stated for the READY): the registered ridge pulls extreme difficulties toward 0 (theta is standardised), so for items
       that (nearly) every model answers right or wrong the fitted P of weak (strong) models is too low (high); CELL-DIFFICULTY
       prints a calibration control for it (CD-R7).
  Residual e_im = (y_im - P_im) / sqrt(P_im (1 - P_im)); P clipped to [1e-10, 1 - 1e-10].

RWS (as ROUTE-SOURCE-NULL, L24265-L24276: "within each source a random partition of the TRAIN items at AF-U's per-source leaf
count AND size profile; EVAL items filed by source, then to a random cell drawn with the TRAIN size weights"; draw r = 1..200 on
default_rng(20261004 + r)): RWS-R1 the profile of source s = the TRAIN sizes of the AF-U cells met among the scored TRAIN items
whose stratum source is s, in AF cell-index order; one stream per draw: per source (sorted) a uniform permutation of its TRAIN
positions (position order) cut into blocks of the profile sizes, then every EVAL item of the source filed to a cell of its source
drawn with the TRAIN size weights. (The same algorithm, written independently, as the ROUTE-SOURCE-NULL build in progress.)

IDENTITY PRECONDITION (all three registrations): the declared arm reproduces C1 +2.67pp and AF-U reproduces G_AF +1.52pp, else
the run refuses. ID-R1 checked at the POINT (the registered digits are points) on the policy G14's reader re-fits on the full
TRAIN beside EVAL, which must equal the frozen file on best single, the AF-U and K0 picks and the declared picks (B3), with the
arm accuracies of the UNION-AF-ROUTE outcome (sha256 e50a8e0f...) beside: best single 0.6049, declared 0.6316, AF-U 0.6201.
RESP-PROFILE-INFO additionally reproduces the two-stage C1 interval [+1.46pp, +3.89pp] from the same run_boot that carries its
RP2 replicates.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import io            # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import hashlib       # noqa: E402
import contextlib    # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import scratch_dir   # noqa: E402,F401  (tempfile -> E:/TaxoArena_tmp/py_<pid>_..., removed at exit)


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


PINS = (("union_cells_io.py", "92a04543b9c75eae5f37a76ae86eb189a190a9bd"),
        ("cell_flips.py", "998d39a7b718faa6647c4d5795dcf03044544955"),
        ("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"))
for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        raise SystemExit("[RESP-STRUCTURE] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import union_cells_io as U      # noqa: E402  (pins union_af_route -> v2_declared_cells ...)
import cell_flips as CF         # noqa: E402  (bh; the CELL-FLIPS outcome format)
V, G, UA = U.V, U.G, U.UA

FLOOR = {"GPQA": 0.25, "MMLU_PRO": 0.10}
LAMBDA = 1.0
KSEEDS = (0, 1, 2, 3, 4)
KNAMES = tuple("K%d" % s for s in KSEEDS)

# identity and CELL-FLIPS constants (the selftests swap this dict; nothing else writes _K)
KCONST = dict(c1="+2.67pp", gaf="+1.52pp", best="0.6049", tdom="0.6316", af="0.6201",
              c1_int=("+1.46pp", "+3.89pp"),
              uar_outcome_sha="e50a8e0fa267db967981fb03320902c238fff505f00b1088d49c3c3a6596cd08",
              flips_rel="experiment_results/archv2/cell_flips/cell_flips_outcome.txt",
              flips_sha="0338331407639ecf1431bdf9415722f0b27d0d0bef703b87122ec63490b14c06",
              flips=(("BBH:n00000066", "internlm2_5-20b-chat", 39, "+0.2051"),
                     ("BBH:n00000067", "internlm2_5-20b-chat", 36, "+0.2222"),
                     ("BBH:n00000105", "internlm2_5-20b-chat", 36, "+0.2222"),
                     ("BBH:n00000124", "internlm2_5-20b-chat", 41, "+0.1463"),
                     ("BBH:n00000159", "internlm2_5-20b-chat", 41, "+0.1463"),
                     ("MMLU_PRO_LB:n00000175", "Llama-3.3-70B-Instruct", 53, "+0.1321"),
                     ("MMLU_PRO_LB:n00000223", "Qwen2.5-32B-Instruct", 27, "+0.2963")))
_K = [KCONST]


def K():
    return _K[0]


def pp(x):
    return "%+.2fpp" % (100.0 * x)


def in_band(x, band):
    return bool(band[0] <= x <= band[1])


def hw(x, band):
    return "HELD" if in_band(x, band) else "FAILED"


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ── IRT (IRT-R1, IRT-R2) ────────────────────────────────────────────────────────────────────────────────────────────────
EPS = 1e-10


def floors_of(srcs):
    return np.array([FLOOR.get(s, 0.0) for s in srcs], dtype=np.float64)


def _sig(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def prob(theta, alpha, b, c):
    a = np.exp(alpha)[:, None]
    z = a * (np.asarray(theta)[None, :] - b[:, None])
    return np.clip(c[:, None] + (1.0 - c[:, None]) * _sig(z), EPS, 1.0 - EPS)


def resid(Y, P):
    return (Y - P) / np.sqrt(P * (1.0 - P))


def _ll(Y, P):
    return Y * np.log(P) + (1.0 - Y) * np.log(1.0 - P)


def item_obj(Y, theta, alpha, b, c, lam):
    return _ll(Y, prob(theta, alpha, b, c)).sum(axis=1) - 0.5 * lam * (alpha ** 2 + b ** 2)


def _item_init(Y):
    p = np.clip(Y.mean(axis=1), 0.02, 0.98)
    return np.zeros(Y.shape[0]), -np.log(p / (1.0 - p))


def fit_items(Y, c, theta, lam=LAMBDA, alpha=None, b=None, tol=1e-8, maxit=200):
    """IRT-R2: every item's (alpha, b) given theta, Newton (observed information where positive definite, else Fisher scoring)
    with step halving -> (alpha, b, iterations, max last step)."""
    Y = np.asarray(Y, dtype=np.float64)
    if alpha is None or b is None:
        alpha, b = _item_init(Y)
    alpha, b = alpha.astype(np.float64).copy(), b.astype(np.float64).copy()
    theta = np.asarray(theta, dtype=np.float64)
    f = item_obj(Y, theta, alpha, b, c, lam)
    mx = float("inf")
    it = 0
    for it in range(1, maxit + 1):
        a = np.exp(alpha)[:, None]
        z = a * (theta[None, :] - b[:, None])
        s = _sig(z)
        P = np.clip(c[:, None] + (1.0 - c[:, None]) * s, EPS, 1.0 - EPS)
        dPdz = (1.0 - c[:, None]) * s * (1.0 - s)
        u = (Y - P) / (P * (1.0 - P))
        r = u * dPdz
        W = dPdz ** 2 / (P * (1.0 - P))
        ga = (r * z).sum(axis=1) - lam * alpha
        gb = -(r * a).sum(axis=1) - lam * b
        Iaa = (W * z * z).sum(axis=1) + lam
        Ibb = (W * a * a).sum(axis=1) + lam
        Iab = -(W * z * a).sum(axis=1)
        # Newton (observed information) where it is positive definite, Fisher scoring elsewhere
        v = -Y / P ** 2 - (1.0 - Y) / (1.0 - P) ** 2
        h2 = v * dPdz ** 2 + u * dPdz * (1.0 - 2.0 * s)
        Oaa = -(h2 * z * z + r * z).sum(axis=1) + lam
        Obb = -(h2 * a * a).sum(axis=1) + lam
        Oab = -(-h2 * z * a - r * a).sum(axis=1)
        newton = (Oaa > 0) & (Oaa * Obb - Oab ** 2 > 1e-12)
        Iaa, Ibb, Iab = np.where(newton, Oaa, Iaa), np.where(newton, Obb, Ibb), np.where(newton, Oab, Iab)
        det = Iaa * Ibb - Iab ** 2
        da = (Ibb * ga - Iab * gb) / det
        db = (Iaa * gb - Iab * ga) / det
        na, nb, nf = alpha.copy(), b.copy(), f.copy()
        step = np.ones(len(alpha))
        pend = np.ones(len(alpha), dtype=bool)
        for _h in range(40):
            idx = np.flatnonzero(pend)
            if not len(idx):
                break
            ta = alpha[idx] + step[idx] * da[idx]
            tb = b[idx] + step[idx] * db[idx]
            tf = item_obj(Y[idx], theta, ta, tb, c[idx], lam)
            ok = tf >= f[idx] - 1e-12
            acc = idx[ok]
            na[acc], nb[acc], nf[acc] = ta[ok], tb[ok], tf[ok]
            pend[acc] = False
            step[idx[~ok]] *= 0.5
        mx = float(max(np.abs(na - alpha).max(initial=0.0), np.abs(nb - b).max(initial=0.0)))
        alpha, b, f = na, nb, nf
        if mx < tol:
            break
    return alpha, b, it, mx


def _theta_obj(Y, theta, alpha, b, c, w):
    return (w[:, None] * _ll(Y, prob(theta, alpha, b, c))).sum(axis=0)


def theta_step(Y, theta, alpha, b, c, w):
    a = np.exp(alpha)[:, None]
    z = a * (theta[None, :] - b[:, None])
    s = _sig(z)
    P = np.clip(c[:, None] + (1.0 - c[:, None]) * s, EPS, 1.0 - EPS)
    dPdz = (1.0 - c[:, None]) * s * (1.0 - s)
    r = (Y - P) / (P * (1.0 - P)) * dPdz
    W = dPdz ** 2 / (P * (1.0 - P))
    g = (w[:, None] * r * a).sum(axis=0)
    I = (w[:, None] * W * a * a).sum(axis=0)
    d = np.clip(g / np.where(I > 0, I, 1.0), -1.0, 1.0)
    f0 = _theta_obj(Y, theta, alpha, b, c, w)
    out = theta.copy()
    step = np.ones(len(theta))
    pend = np.ones(len(theta), dtype=bool)
    for _h in range(40):
        if not pend.any():
            break
        t = np.where(pend, theta + step * d, out)
        f1 = _theta_obj(Y, t, alpha, b, c, w)
        ok = pend & (f1 >= f0 - 1e-12)
        out[ok] = t[ok]
        pend &= ~ok
        step[pend] *= 0.5
    return out


def _std(t):
    return (t - t.mean()) / t.std()


def fit_train(Y, c, w=None, lam=LAMBDA, theta=None, alpha=None, b=None, tol=1e-7, maxit=3000):
    """IRT-R1 -> dict(theta, alpha, b, iters, converged). Y: TRAIN rows only (the caller asserts the positions)."""
    Y = np.asarray(Y, dtype=np.float64)
    w = np.ones(Y.shape[0]) if w is None else np.asarray(w, dtype=np.float64)
    if theta is None:
        p = np.clip((w[:, None] * Y).sum(axis=0) / w.sum(), 0.02, 0.98)
        theta = _std(np.log(p / (1.0 - p)))
    if alpha is None or b is None:
        alpha, b = _item_init(Y)
    theta = np.asarray(theta, dtype=np.float64).copy()
    conv, it = False, 0
    for it in range(1, maxit + 1):
        alpha, b, _i, _m = fit_items(Y, c, theta, lam, alpha, b, tol=0.0, maxit=3)
        nt = _std(theta_step(Y, theta, alpha, b, c, w))
        dth = float(np.abs(nt - theta).max())
        theta = nt
        if dth < tol:
            conv = True
            break
    alpha, b, _i, _m = fit_items(Y, c, theta, lam, alpha, b, tol=1e-10, maxit=500)
    return dict(theta=theta, alpha=alpha, b=b, iters=it, converged=conv)


def assert_train(D, pos):
    """The TRAIN-only guard of every IRT fit and every cell mean: positions must be TRAIN (SystemExit, python -O safe)."""
    bad = set(int(k) for k in np.asarray(pos).tolist()) - D.train_set
    if bad:
        raise SystemExit("[TRAIN-ONLY] a TRAIN-side fit received %d EVAL position(s)" % len(bad))


def irt_point(D, say=None, tag="", lam=LAMBDA):
    """theta and TRAIN items from TRAIN (IRT-R1); EVAL items with theta fixed (IRT-R2). -> dict with P / e on both sides."""
    assert_train(D, D.T)
    cT = floors_of([D.src[k] for k in D.T])
    cE = floors_of([D.src[k] for k in D.E])
    YT = D.A[D.T].astype(np.float64)
    YE = D.A[D.E].astype(np.float64)
    ft = fit_train(YT, cT, lam=lam)
    if not ft["converged"]:
        raise SystemExit("%s REFUSED: the TRAIN 3PL fit did not converge in %d iterations" % (tag, ft["iters"]))
    aE, bE, itE, mxE = fit_items(YE, cE, ft["theta"], lam)
    if mxE >= 1e-6:
        raise SystemExit("%s REFUSED: the EVAL item fit did not converge (last step %.2e)" % (tag, mxE))
    PT = prob(ft["theta"], ft["alpha"], ft["b"], cT)
    PE = prob(ft["theta"], aE, bE, cE)
    out = dict(theta=ft["theta"], aT=ft["alpha"], bT=ft["b"], aE=aE, bE=bE, cT=cT, cE=cE, YT=YT, YE=YE, PT=PT, PE=PE,
               eT=resid(YT, PT), eE=resid(YE, PE), iters=ft["iters"], itE=itE)
    if say:
        say("%s IRT (3PL, floors GPQA 1/4, MMLU_PRO 1/10, else 0; ridge lambda %.1f): TRAIN fit on %d TRAIN items x %d models"
            " converged in %d iterations; EVAL items (%d) fitted with theta fixed in %d Fisher steps" % (
                tag, lam, len(D.T), len(D.models), ft["iters"], len(D.E), itE))
        say("%s theta (TRAIN, standardised): %s" % (tag, ", ".join("%s %+.3f" % (m, t) for m, t in zip(D.models, ft["theta"]))))
    return out


# ── data (TRAIN key of the gen view; the EVAL key through union_cells_io) ──────────────────────────────────────────────
def refuse(tag, msg):
    raise SystemExit("%s REFUSED: %s" % (tag, msg))


def prelude(root, say, tag, test_id, reg_txt, scripts, outs, dry):
    """POOL line first; write-once paths; pins; frozen policy; AF-U, K0..K4 cells (manifest-pinned)."""
    U.pool_line(say, tag)
    if not dry:
        U.write_once_check(outs, tag)
    say("%s %s (zero calls; %s) | registration %s" % (tag, test_id, "DRY-RUN" if dry else "RUN", reg_txt))
    U.script_pins(say, tag, scripts + [os.path.join(HERE, "resp_structure_common.py"), os.path.join(HERE, "union_cells_io.py"),
                                       os.path.join(HERE, "cell_flips.py"), os.path.join(HERE, "union_af_route.py"),
                                       os.path.join(HERE, "v2_declared_cells.py")])
    say("%s data root %s; outputs %s (write-once; never committed: sha256 + E:)" % (tag, root, ", ".join(outs)))
    pol = U.load_policy(root, say, tag)
    man, af, k0 = U.load_cells(root, say, tag)
    kx = {"K0": k0}
    for s in KSEEDS[1:]:
        rel = UA.RES + "/inputs/k_cells_s%d.tsv" % s
        if rel not in man["inputs"]:
            refuse(tag, "the inputs manifest carries no %s" % rel)
        kx["K%d" % s], d = V.load_tree_cells(U.P(root, rel), man["inputs"][rel])
        say("%s K_%d cells: %s" % (tag, s, d))
    return pol, af, kx


def read_train(root, say, tag, roster, key):
    """The gen view (TRAIN side; open_generation('policy_fit')): structure, and with key=True the ONE TRAIN key read
    (response_lite, UNUSABLE_CELL, MATH-FIX overlay). -> (models, train_meta, comp_strata, K_tr | None, n complete)."""
    c = U.C()
    path = U.P(root, c["gen_rel"])
    tw, gsha = V.open_tw("gen", "policy_fit", path, c["gen_sha"], "gen_view", say)
    K = None
    try:
        nc, ni, _s = V.pool_row(tw, c["pool"], c["cv"])
        if (nc, ni) != (c["pool_comp"], c["pool_items"]):
            refuse(tag, "the gen view's pool row is %d components / %d items, not %d / %d" % (nc, ni, c["pool_comp"], c["pool_items"]))
        models = sorted(m for m, s in V.registry(tw, c["cv"]).items() if s == "ACTIVE")
        if len(models) != c["roster"] or c["excluded"] in models or list(roster) != models:
            refuse(tag, "the gen view's ACTIVE roster (%d) is not the frozen policy's %d-model roster without %s" % (
                len(models), c["roster"], c["excluded"]))
        meta = V.side_items(tw, c["cv"], "TRAIN")
        comp_strata = V.component_strata(tw)
        cc = V.cell_counts(tw, "response_lite", c["cv"], models, meta)
        pre = V.structurally_complete(cc, models, c["rule"])
        if key:
            tw.unseal("%s: the one TRAIN key read (the TRAIN-only 3PL fit, TRAIN cell means, G14's B3 / identity re-fit)" % tag)
            K, kst = V.read_key(tw, "response_lite", c["cv"], models, meta, True, c["rule"])
            items = V.complete_items(K, models)
            if set(items) != pre:
                refuse(tag, "the key-complete TRAIN set (%d) differs from the structurally complete one (%d)" % (len(items), len(pre)))
            say("%s TRAIN key: cells single %d, multi %d; MATH-FIX overlay rows %d (changed %d)" % (
                tag, kst["single"], kst["multi"], kst["overlay_rows"], kst["overlay_changed"]))
    finally:
        tw.close()
    if not V.after_sha(path, gsha, "gen_view", say):
        refuse(tag, "the gen view's sha256 changed during the read")
    say("%s TRAIN SET (gen view TRAIN items of %s, every one of the %d models with exactly one response, %s): %d of %d TRAIN items"
        " (%d components)" % (tag, c["cv"], len(models), c["rule"], len(pre), len(meta), len(set(meta[i][0] for i in pre))))
    return models, meta, comp_strata, K, len(pre)


def build(models, train_meta, E, K_tr, comp_strata, af, kx, pol, tag):
    D = V.build_ud(models, train_meta, E["meta"], K_tr, E["K"], comp_strata, V.PRECONDITIONS["train_unit"], None,
                   V.REG["placebo_seed"], tree=af, xtrees=kx)
    if D.n_eval != U.C()["n_eval"] or D.eval_units["n_units"] != U.C()["comp_eval"]:
        refuse(tag, "the scored EVAL set is %d items / %d components, not %d / %d" % (
            D.n_eval, D.eval_units["n_units"], U.C()["n_eval"], U.C()["comp_eval"]))
    if "train_items_scored" in pol and int(pol["train_items_scored"]) != D.n_train:
        refuse(tag, "the scored TRAIN set is %d items, not the frozen policy's %d" % (D.n_train, pol["train_items_scored"]))
    bad = [D.items[k] for k in D.E if D.tree_keys[D.g_tree[k]] in (V.NO_ROUTING_ROW, UA.NO_ROW, UA.UNROUTED)]
    if bad:
        refuse(tag, "[G14-NOROW] %d EVAL item(s) of the scored set carry no AF-U cell (first %s)" % (len(bad), bad[:3]))
    return D


def b3_identity(D, pol, say, tag):
    """B3 (the point policy re-fitted on the full TRAIN equals the frozen file) and ID-R1 (C1 and G_AF points)."""
    P0 = V.fit(D, V.train_full(D))
    nn = lambda d: {k: v for k, v in d.items() if v is not None}       # noqa: E731
    tree = {D.tree_keys[i]: D.models[q] for i, q in enumerate(P0.pol["tree"]) if q >= 0}
    k0 = {D.xkeys["K0"][i]: D.models[q] for i, q in enumerate(P0.pol["x:K0"]) if q >= 0}
    tdom = {"%s/%s" % D.dom_keys[i]: D.models[q] for i, q in enumerate(P0.pol["tdom"]) if q >= 0}
    if D.models[P0.gb] != pol["best_single"] or tree != nn(pol["tree_cell"]) or k0 != nn(pol["xtree_cell"]["K0"]) or \
            tdom != nn(pol["true_source_domain"]):
        refuse(tag, "[B3] the point policy re-fitted on TRAIN beside EVAL differs from the frozen TRAIN policy")
    say("%s B3: the policy re-fitted on the full TRAIN equals the frozen file (best single %s; AF-U, K0 and declared picks)" % (
        tag, pol["best_single"]))
    AE = D.A[D.E]
    r = np.arange(len(D.E))
    gb = P0.gb

    def routed(key, g):
        p_ = P0.pol[key][g[D.E]]
        return AE[r, np.where(p_ < 0, gb, p_)].astype(np.float64)
    best = float(AE[:, gb].mean())
    acc_d = float(routed("tdom", D.g_tdom).mean())
    acc_t = float(routed("tree", D.g_tree).mean())
    got = dict(c1=pp(acc_d - best), gaf=pp(acc_t - best), best="%.4f" % best, tdom="%.4f" % acc_d, af="%.4f" % acc_t)
    k = K()
    if any(got[x] != k[x] for x in ("c1", "gaf", "best", "tdom", "af")):
        refuse(tag, "[IDENTITY] C1 %s, G_AF %s (best %s, declared %s, AF-U %s) are not the registered C1 %s, G_AF %s (best %s,"
               " declared %s, AF-U %s)" % (got["c1"], got["gaf"], got["best"], got["tdom"], got["af"], k["c1"], k["gaf"], k["best"],
                                          k["tdom"], k["af"]))
    say("%s IDENTITY (point; registered C1 %s, G_AF %s): declared C1 %s, AF-U G_AF %s (best single %s, declared %s, AF-U %s;"
        " UNION-AF-ROUTE outcome sha256 %s...) -> REPRODUCED" % (tag, k["c1"], k["gaf"], got["c1"], got["gaf"], got["best"],
                                                                got["tdom"], got["af"], k["uar_outcome_sha"][:16]))
    return P0, got


def arms_of(D):
    """Every partition arm over ALL scored positions: name -> (grouping, number of cells, cell names)."""
    out = {"AF-U": (D.g_tree, len(D.tree_keys), list(D.tree_keys))}
    for nm in KNAMES:
        g, ng = D.groupings["x:" + nm]
        out[nm] = (g, ng, list(D.xkeys[nm]))
    out["SRC"] = (D.g_tsrc, len(D.src_keys), list(D.src_keys))
    out["declared"] = (D.g_tdom, len(D.dom_keys), ["%s/%s" % k for k in D.dom_keys])
    return out


def load_all(root, say, tag, pol, af, kx, marker, marker_text, between=None):
    """TRAIN key, then (between: the pre-EVAL hook, e.g. the TRAIN-half pre-pass) the EVAL key (B1 marker); D built."""
    models, tmeta, cstr, K_tr, _n = read_train(root, say, tag, pol["roster"], True)
    if between is not None:
        between(models, tmeta, K_tr)
    E = U.eval_set(root, say, tag, roster=pol["roster"], key=True, marker=marker)
    D = build(models, tmeta, E, K_tr, cstr, af, kx, pol, tag)
    return D


def dry_structure(root, say, tag, pol, af, kx):
    """--dry-run: the TRAIN and EVAL structure (no key column selected); the denominators."""
    models, tmeta, _c, _K, ntr = read_train(root, say, tag, pol["roster"], False)
    E = U.eval_set(root, say, tag, roster=pol["roster"], key=False)
    for nm, cells in (("AF-U", af),) + tuple(sorted(kx.items())):
        ne = len(set(cells.get(i) for i in E["items"]))
        miss = sum(1 for i in E["items"] if cells.get(i) in (None, V.NO_ROUTING_ROW, UA.NO_ROW, UA.UNROUTED))
        say("%s DENOMINATOR %-5s %d distinct cells on the %d-item EVAL set; EVAL items without a cell %d (must be 0)" % (
            tag, nm, ne, len(E["items"]), miss))
        if miss:
            refuse(tag, "[G14-NOROW] %s: %d EVAL item(s) carry no cell" % (nm, miss))
    return models, ntr, E


# ── RWS (RWS-R1; as ROUTE-SOURCE-NULL) ─────────────────────────────────────────────────────────────────────────────────
def rws_profile(D, g_af):
    prof = {}
    for s in sorted(set(D.src)):
        cnt = {}
        for k in D.T:
            if D.src[k] == s:
                cnt[int(g_af[k])] = cnt.get(int(g_af[k]), 0) + 1
        prof[s] = [cnt[j] for j in sorted(cnt)]
    return prof


def rws_cells(D, prof, seed):
    rng = np.random.default_rng(seed)
    g = np.full(D.n, -1, dtype=np.int64)
    base = 0
    starts = {}
    srcs = sorted(prof)
    for s in srcs:
        pos = np.array([k for k in D.T if D.src[k] == s], dtype=np.int64)
        sizes = prof[s]
        if sum(sizes) != len(pos):
            raise SystemExit("[RWS] source %s: profile sizes sum %d != %d TRAIN items" % (s, sum(sizes), len(pos)))
        perm = rng.permutation(len(pos))
        off = 0
        for j, sz in enumerate(sizes):
            g[pos[perm[off:off + sz]]] = base + j
            off += sz
        starts[s] = base
        base += len(sizes)
    for s in srcs:
        epos = np.array([k for k in D.E if D.src[k] == s], dtype=np.int64)
        if not len(epos):
            continue
        w = np.asarray(prof[s], dtype=np.float64)
        g[epos] = starts[s] + rng.choice(len(w), size=len(epos), p=w / w.sum())
    if (g < 0).any():
        raise SystemExit("[RWS] %d scored item(s) of a source without TRAIN items" % int((g < 0).sum()))
    return g, base


def mc_se_pct(xs, q, B=2000, seed=20261004):
    """Monte Carlo SE of the U.pct percentile of xs: SD of the percentile over B resamples of xs."""
    xs = np.asarray(xs, dtype=np.float64)
    rng = np.random.default_rng(seed)
    v = [U.pct(sorted(xs[rng.integers(0, len(xs), len(xs))].tolist()), q) for _b in range(B)]
    return float(np.std(v, ddof=1))


def brier(p, outcome_true):
    return (p - (1.0 if outcome_true else 0.0)) ** 2


def support_deff(D):
    """Kish mean EVAL component size (the DEFF analogue the cache's own cluster sizes give)."""
    return U.kish(Counter(D.comp[k] for k in D.E).values())


# ── selftest machinery (fixtures under scratch_dir's per-process dir on E:) ────────────────────────────────────────────
FX_MODELS = ["m0", "m1", "m2", "m3", "m4", "m5"]
FX_THETA = {"m0": -1.3, "m1": -0.7, "m2": -0.1, "m3": 0.4, "m4": 0.9, "m5": 1.5}
# (cell member prefix, view source, number of AF cells, difficulty centres)
FX_SOURCES = (("BBH", "BBH", 4, (-1.4, -0.4, 0.5, 1.4)), ("GPQA", "GPQA", 2, (0.3, 1.2)),
              ("MMLU_PRO_LB", "MMLU_PRO", 4, (-1.0, -0.2, 0.6, 1.3)), ("MATH", "MATH", 2, (-0.6, 0.9)))
FX_PLANT = ("BBH:n00000004", "MMLU_PRO_LB:n00000010")       # m2 gets +4.0 logits there ("planted")
FX_PLANT_MODEL = "m2"


def fx_generate(variant="planted", seed=7, n_tr=(34, 46), n_ev=(16, 24), scale=1.0):
    """The fixture's items and responses (the value of record per (item, model)); planted interaction / difficulty strata.
    variant: planted (difficulty strata + the m2 interaction in FX_PLANT), null (one difficulty centre, no interaction),
    strata (difficulty strata, no interaction)."""
    rs = np.random.RandomState(seed)
    rows = []
    nid = [0]
    ci = 0
    for pref, src, ncell, centres in FX_SOURCES:
        for j in range(ncell):
            ci += 1
            cell = "%s:n%08d" % (pref, ci)
            dom = "d%d" % (j // 2)
            centre = 0.2 if variant == "null" else scale * centres[j]
            for side, (lo, hi) in (("TRAIN", n_tr), ("EVAL", n_ev)):
                n = rs.randint(lo, hi + 1)
                k = 0
                while k < n:
                    twins = 2 if (side == "EVAL" and k % 6 == 2 and k + 1 < n) else 1
                    nid[0] += 1
                    comp = "c:%s:%05d" % (side[0], nid[0])
                    for _t in range(twins):
                        iid = "i:%05d" % (nid[0] * 3 + _t)
                        a = rs.uniform(0.7, 1.8)
                        b = rs.normal(centre, 0.5)
                        cfl = FLOOR.get(src, 0.0)
                        y = {}
                        for m in FX_MODELS:
                            z = a * (FX_THETA[m] - b)
                            if variant == "planted" and cell in FX_PLANT and m == FX_PLANT_MODEL:
                                z += 4.0
                            p = cfl + (1 - cfl) / (1 + math.exp(-z))
                            y[m] = int(rs.uniform() < p)
                        rows.append(dict(id=iid, comp=comp, side=side, src=src, dom=dom, af=cell, y=y))
                        k += 1
    return rows


def fx_kcells(rows, s):
    """K_s cells: within each source, a seeded random partition of the items at the AF-U per-source cell count."""
    out = {}
    rs = np.random.RandomState(100 + s)
    nper = {src: n for _p, src, n, _c in FX_SOURCES}
    pref = {src: p for p, src, _n, _c in FX_SOURCES}
    for r in rows:
        out[r["id"]] = "K%d:%s:%03d" % (s, pref[r["src"]], rs.randint(0, nper[r["src"]]))
    return out


def fx_policy(rows, kcells):
    """The frozen TRAIN policy by an independent loop (argmax of TRAIN correct counts over the sorted roster; first on ties)."""
    tr = [r for r in rows if r["side"] == "TRAIN" and r.get("scored", True)]

    def best(rs_):
        tot = [sum(r["y"][m] for r in rs_) for m in FX_MODELS]
        return FX_MODELS[int(np.argmax(tot))]

    def per(keyf):
        by = defaultdict(list)
        for r in tr:
            by[keyf(r)].append(r)
        return {k: best(v) for k, v in sorted(by.items())}
    return dict(best_single=best(tr), roster=FX_MODELS, tree_cell=per(lambda r: r["af"]),
                xtree_cell={"K0": per(lambda r: kcells[0][r["id"]])},
                true_source_domain=per(lambda r: "%s/%s" % (r["src"], r["dom"])), train_items_scored=len(tr), test="SELFTEST")


def fx_identity(rows, pol):
    ev = [r for r in rows if r["side"] == "EVAL" and r.get("scored", True)]
    g = pol["best_single"]
    best = sum(r["y"][g] for r in ev) / len(ev)
    d = sum(r["y"][pol["true_source_domain"].get("%s/%s" % (r["src"], r["dom"])) or g] for r in ev) / len(ev)
    t = sum(r["y"][pol["tree_cell"].get(r["af"]) or g] for r in ev) / len(ev)
    return dict(c1=pp(d - best), gaf=pp(t - best), best="%.4f" % best, tdom="%.4f" % d, af="%.4f" % t)


def build_fixture(tmp, variant="planted", seed=7, flips=None, **gen):
    """A complete layout under tmp/root: sealed gen (TRAIN) and eval (EVAL) views, the frozen policy, the inputs manifest with
    the AF-U and K0..K4 cells, a CELL-FLIPS outcome stub. -> (root, X) with X = dict(const, kconst, rows, kcells, pol)."""
    rows = fx_generate(variant, seed, **gen)
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    items, responses = [], []
    for r in rows:
        items.append(dict(id=r["id"], comp=r["comp"], side=r["side"], src=r["src"], dom=r["dom"], cvs=["fx"]))
        for m in FX_MODELS:
            ov = r["src"] == "MATH" and m == "m1"          # the MATH-FIX overlay carries the value of record
            responses.append(dict(cv="fx", model=m, item=r["id"], side=r["side"], src=r["src"], c=(1 - r["y"][m]) if ov else r["y"][m],
                                  mf=r["y"][m] if ov else None))
    extra = []
    for side in ("TRAIN", "EVAL"):                         # out of the scored sets: a missing response and a multi-response cell
        for j, kind in enumerate(("missing", "multi")):
            iid = "x:%s:%d" % (side, j)
            comp = "c:x:%s:%d" % (side, j)
            items.append(dict(id=iid, comp=comp, side=side, src="BBH", dom="d0", cvs=["fx"]))
            for m in FX_MODELS:
                if kind == "missing" and m == "m5":
                    continue
                responses.append(dict(cv="fx", model=m, item=iid, side=side, src="BBH", c=1, mf=None))
            if kind == "multi":
                responses.append(dict(cv="fx", model="m0", item=iid, side=side, src="BBH", c=0, mf=None))
            extra.append(dict(id=iid, comp=comp, side=side, src="BBH", dom="d0", af="BBH:n00000001", y=None, scored=False))
    ev_all = [it for it in items if it["side"] == "EVAL"]
    n_comp_all = len(set(i["comp"] for i in ev_all))
    pools = [("pv_fx", "fx", n_comp_all, json.dumps({"fx": len(ev_all)}))]
    registry = [("fx", m, "ACTIVE") for m in FX_MODELS] + [("fx", V.EXCLUDED, "QUARANTINED")]
    spec = dict(items=items, responses=responses, registry=registry, pools=pools)
    vdir = os.path.join(root, "data_v2")
    os.makedirs(vdir)
    gsha = V._mk_view(os.path.join(vdir, "gen_view_fx.db"), "gen", ("TRAIN",), spec)
    esha = V._mk_view(os.path.join(vdir, "eval_view_fx.db"), "eval", ("EVAL",), spec)
    kcells = {s: fx_kcells(rows + extra, s) for s in KSEEDS}
    pol = fx_policy(rows, kcells)
    pp_ = U.P(root, U.CONST["policy_rel"])
    os.makedirs(os.path.dirname(pp_))
    with open(pp_, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
    inp = U.P(root, UA.RES + "/inputs")
    os.makedirs(inp)
    shas = {}
    af = {r["id"]: r["af"] for r in rows + extra}
    files = [(U.CONST["af_rel"], af, "fixture af")] + [(UA.RES + "/inputs/k_cells_s%d.tsv" % s, kcells[s], "fixture k%d" % s) for s in KSEEDS]
    for rel, cells, hdr in files:
        with open(U.P(root, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(UA.cells_text(cells, hdr))
        shas[rel] = UA.sha256_lf(U.P(root, rel))
    mp = U.P(root, UA.RES + "/inputs/inputs_manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(dict(afu_files={}, inputs=shas), indent=1, sort_keys=True) + "\n")
    ev = [r for r in rows if r["side"] == "EVAL"]
    const = dict(U.CONST, pool="pv_fx", cv="fx", n_eval=len(ev), comp_eval=len(set(r["comp"] for r in ev)), pool_items=len(ev_all),
                 pool_comp=n_comp_all, roster=len(FX_MODELS), eval_rel="data_v2/eval_view_fx.db", eval_sha=esha,
                 gen_rel="data_v2/gen_view_fx.db", gen_sha=gsha, policy_sha=sha256_bytes(pp_), manifest_sha=UA.sha256_lf(mp))
    idn = fx_identity(rows, pol)
    # the CELL-FLIPS stub: the planted cells and one more cell whose frozen pick is not the best single (the registered format)
    g = pol["best_single"]
    if flips is None:
        flips = [c for c in FX_PLANT if pol["tree_cell"].get(c) not in (None, g)]
        for c in sorted(set(r["af"] for r in rows)):
            if c not in FX_PLANT and pol["tree_cell"].get(c) not in (None, g):
                flips.append(c)
                break
    fl = []
    for c in flips:
        ch = pol["tree_cell"][c]
        rs_ = [r for r in ev if r["af"] == c]
        D = sum(r["y"][ch] - r["y"][g] for r in rs_) / len(rs_)
        fl.append((c, ch, len(rs_), "%+.4f" % D))
    fp = U.P(root, "experiment_results/archv2/cell_flips/cell_flips_outcome.txt")
    os.makedirs(os.path.dirname(fp))
    with open(fp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("[CELL-FLIPS] fixture stub\n")
        for c, ch, n, D in fl:
            fh.write("  FLIP %-8s %-30s n %4d  challenger %-30s D_c %s  p %.5f\n" % ("AF-U", c, n, ch, D, 0.0001))
        fh.write("  FLIP %-8s %-30s n %4d  challenger %-30s D_c %s  p %.5f\n" % ("K_0", "K0:BBH:000", 30, "m2", "+0.1000", 0.0001))
    kconst = dict(KCONST, flips=tuple(fl), flips_sha=sha256_bytes(fp), **idn)
    return root, dict(const=const, kconst=kconst, rows=rows, kcells=kcells, pol=pol, flips=fl)


@contextlib.contextmanager
def patched(X, pool=(0, "SELFTEST stub: pool check not run")):
    old_c, old_p, old_r, old_k = U._C[0], U._POOL[0], UA._ROOT[0], _K[0]
    U._C[0] = X["const"]
    U._POOL[0] = lambda _pool: pool
    _K[0] = X["kconst"]
    try:
        yield
    finally:
        U._C[0], U._POOL[0], UA._ROOT[0], _K[0] = old_c, old_p, old_r, old_k


def capture(fn, *a, **k):
    buf = []
    res = fn(*a, out=buf.append, **k)
    return res, "\n".join(buf)


def need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def line_with(text, prefix):
    for ln in text.split("\n"):
        if ln.startswith(prefix):
            return ln
    raise AssertionError("no line starting %r" % prefix)


def fx_matrices(rows):
    """An independent view of a fixture: TRAIN / EVAL item lists (sorted by id, as build_ud orders positions)."""
    sc = sorted((r for r in rows if r.get("scored", True)), key=lambda r: r["id"])
    tr = [r for r in sc if r["side"] == "TRAIN"]
    ev = [r for r in sc if r["side"] == "EVAL"]
    Y = lambda rs: np.array([[r["y"][m] for m in FX_MODELS] for r in rs], dtype=np.float64)   # noqa: E731
    return tr, ev, Y(tr), Y(ev)


def fx_irt(rows):
    """The oracle's IRT: the same estimator (fit_train / fit_items, checked against scipy in each selftest's irt case) on the
    fixture's own TRAIN / EVAL rows (no loader, no D)."""
    tr, ev, YT, YE = fx_matrices(rows)
    cT, cE = floors_of([r["src"] for r in tr]), floors_of([r["src"] for r in ev])
    ft = fit_train(YT, cT)
    aE, bE, _i, _m = fit_items(YE, cE, ft["theta"])
    PT, PE = prob(ft["theta"], ft["alpha"], ft["b"], cT), prob(ft["theta"], aE, bE, cE)
    return dict(tr=tr, ev=ev, YT=YT, YE=YE, theta=ft["theta"], aT=ft["alpha"], bT=ft["b"], aE=aE, bE=bE, cT=cT, cE=cE, PT=PT, PE=PE,
                eT=resid(YT, PT), eE=resid(YE, PE))


def irt_selfcheck():
    """IRT-R1 / IRT-R2 against scipy on a small synthetic matrix: the EVAL item fit equals scipy's minimiser of the penalised
    negative log-likelihood item by item; the TRAIN fit is a fixed point of (items | theta) then (theta step, standardise);
    the floors and the residual formula by hand."""
    from scipy.optimize import minimize
    rs = np.random.RandomState(3)
    th = np.array([-1.0, -0.3, 0.2, 0.8, 1.4])
    n = 40
    a0, b0 = rs.uniform(0.6, 1.6, n), rs.normal(0, 1, n)
    c = np.array([0.25 if i % 3 == 0 else 0.0 for i in range(n)])
    Y = (rs.uniform(size=(n, 5)) < c[:, None] + (1 - c[:, None]) / (1 + np.exp(-a0[:, None] * (th[None, :] - b0[:, None])))).astype(float)
    al, bb, _it, mx = fit_items(Y, c, th)
    assert mx < 1e-8
    for i in range(n):
        def nll(x, i=i):
            P = np.clip(c[i] + (1 - c[i]) / (1 + np.exp(-math.exp(x[0]) * (th - x[1]))), EPS, 1 - EPS)
            return -(Y[i] * np.log(P) + (1 - Y[i]) * np.log(1 - P)).sum() + 0.5 * (x[0] ** 2 + x[1] ** 2)
        res = minimize(nll, np.array([0.0, 0.0]), method="Nelder-Mead", options=dict(xatol=1e-10, fatol=1e-12, maxiter=20000))
        assert abs(res.x[0] - al[i]) < 1e-4 and abs(res.x[1] - bb[i]) < 1e-4, (i, res.x, al[i], bb[i])
    ft = fit_train(Y, c)
    assert ft["converged"] and abs(ft["theta"].mean()) < 1e-12 and abs(ft["theta"].std() - 1) < 1e-12
    a2, b2, _i, _m = fit_items(Y, c, ft["theta"], alpha=ft["alpha"], b=ft["b"], tol=0.0, maxit=3)
    t2 = _std(theta_step(Y, ft["theta"], a2, b2, c, np.ones(n)))
    assert np.abs(t2 - ft["theta"]).max() < 1e-6, "TRAIN fit is a fixed point"
    assert np.allclose(floors_of(["GPQA", "MMLU_PRO", "BBH", "MATH", "MUSR", "IFEVAL"]), [0.25, 0.1, 0, 0, 0, 0])
    P = prob(th, np.zeros(1), np.zeros(1), np.array([0.25]))
    assert abs(P[0, 2] - (0.25 + 0.75 / (1 + math.exp(-0.2)))) < 1e-12
    e = resid(np.array([[1.0]]), np.array([[0.8]]))
    assert abs(e[0, 0] - 0.2 / math.sqrt(0.16)) < 1e-12
    # weights: a zero-weight item does not move theta
    w = np.ones(n)
    w[0] = 0
    f1 = fit_train(Y, c, w=w)
    Y2 = Y.copy()
    Y2[0] = 1 - Y2[0]
    f2 = fit_train(Y2, c, w=w)
    assert np.abs(f1["theta"] - f2["theta"]).max() < 1e-6, "a zero-weight TRAIN item leaves theta unchanged"


def run_cases(tag, cases, hitc, branches, only=None, quiet=False):
    """Run the selftest cases (tmp cases get a fresh dir under scratch_dir's process dir on E:); then the branch registry."""
    import tempfile
    hitc.clear()
    fails, ran = [], 0
    for name, fn, kind in cases:
        if only is not None and name not in only:
            continue
        ran += 1
        d = None
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                if kind == "tmp":
                    d = tempfile.mkdtemp(prefix="rsc_")
                    fn(d)
                else:
                    fn()
            if not quiet:
                print("  ok   %s" % name, flush=True)
        except BaseException as e:          # noqa: B902
            fails.append(name)
            if not quiet:
                print("  FAIL %s: %s: %s" % (name, type(e).__name__, str(e)[:500]), flush=True)
        finally:
            if d is not None:
                scratch_dir.rmtree_robust(d)
    if only is None:
        ran += 1
        miss = [b for b in branches if hitc[b] == 0]
        if miss:
            fails.append("branch_cover")
            if not quiet:
                print("  FAIL branch_cover: print branches never executed: %s" % miss, flush=True)
        elif not quiet:
            print("  ok   branch_cover", flush=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (tag, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(script_path, modname, mutants, tag, only=None):
    """Each mutant edits the script's source above its MUTANTS table (or this module, target "common") in memory, then runs the
    named selftest cases in a fresh namespace; KILLED iff the selftest fails. C00 is the no-op control."""
    src = open(script_path, encoding="utf-8").read()
    csrc = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("\nMUTANTS = (")
    head, tail = src[:cut], src[cut:]
    me = sys.modules[__name__]
    killed, surv, n_real, control = 0, [], 0, None
    for name, old, new, tests, target in mutants:
        if only and not any(name.startswith(o) for o in only):
            continue
        base = head if target == "self" else csrc
        if base.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times: %r" % (tag, name, base.count(old), old[:80]))
        mut = base.replace(old, new)
        ns = {"__name__": modname + "_mutant", "__file__": script_path}
        res = True
        try:
            if target == "common":
                exec(compile(mut, me.__file__, "exec"), me.__dict__)
            exec(compile((mut + tail) if target == "self" else src, "<mutant>", "exec"), ns)
            ns["selftest"](only=set(tests), quiet=True)
        except BaseException as e:      # noqa: B902
            res = "%s: %s" % (type(e).__name__, str(e)[:160])
        finally:
            if target == "common":
                exec(compile(csrc, me.__file__, "exec"), me.__dict__)
        if name.startswith("C00"):
            control = res is True
            print("  %-70s control %s" % (name, "SURVIVED (as it must)" if control else "KILLED (harness broken): %s" % res), flush=True)
            continue
        n_real += 1
        k = res is not True
        killed += int(k)
        if not k:
            surv.append(name)
        print("  %-70s %-8s %s" % (name, "KILLED" if k else "SURVIVED", "" if res is True else res[:110]), flush=True)
    print("%s MUTANTS: %d of %d KILLED; control %s; survivors %s" % (tag, killed, n_real, "survived" if control else "KILLED/not run",
                                                                     surv or "none"))
    return 0 if killed == n_real and control else 1


def pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None
