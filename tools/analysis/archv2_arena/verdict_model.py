"""The per-order verdict model (arena section 4.1: "a verdict model fitted on grok_calib.db (flip, tie, and P(correct)
by agree/disagree, length difference and order)").

One vote per presentation order; the model sees the FIRST-shown and the SECOND-shown response:

    eta = kappa * (k_first - k_second) * [DEC] + u[g, first] - u[g, second] + lam * dlen_1k + pi
    P(first) = sigma(eta - c_t),  P(second) = sigma(-eta - c_t),  P(tie) = 1 - both,  c_t = exp(gamma_t)

  t (match type, from the KEY and the extracted answers): DEC = the key decides (k_a != k_b); AGREE = same key and the
    same non-blank extracted answer; NONDEC = everything else (both wrong with different answers, a blank answer...).
  u[g, m] = the judge's systematic, non-key preference for model m in anchor g (ridge 1/(2 sigma0^2) u^2); after the
    fit it is decomposed u = v_m (model-level, shared across anchors) + w_gm (the residue is "model-anchored, not
    anchor-anchored": ESCALATE-LLAMA-LAW), whose SDs drive the RANDOM mode.
  pi = position bias toward the first-shown response; lam = length preference per 1,000 characters.

The match verdict is the dual-order rule of record (rejudge_grok.combine_orders): A iff both orders pick A, B iff both
pick B, TIE otherwise (a flip or any tie).

Simulation modes
  fixed   u at its fitted values: a parametric bootstrap of the fitted judge on the same schedule;
  random  u drawn afresh per replicate from N(0, sigma_v^2) + N(0, sigma_w^2): a NEW judge instance of the same kind
          (the mode every design leg uses: a new roster and a new prompt have no fitted u);
  retest  each observed per-order vote is KEPT with probability r_keep, else redrawn from the fixed model; r_keep is
          solved (bisection on the exact expected agreement) so the re-draw's 3-way agreement with the observed draw
          equals a measured test-retest agreement (default 0.896, JUDGE-WIRING-BOARD raw 3-way agreement GROK-CALIB vs
          the Kotlin draw of the same judge, programme L4252).
"""
import hashlib
import json
import math

import numpy as np
from scipy.optimize import minimize

TYPES = ("DEC", "AGREE", "NONDEC")
VOTE_Y = {"Model A": 0, "Model B": 1, "TIE": 2}   # positional: "Model A" = the first-shown response
Y_VOTE = {0: "Model A", 1: "Model B", 2: "TIE"}
RETEST_AGREEMENT_OF_RECORD = 0.896


def match_type(ka, kb, pa, pb):
    if ka is not None and kb is not None and ka >= 0 and kb >= 0 and ka != kb:
        return 0
    if pa and pb and pa == pb:
        return 1
    return 2


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


class Obs:
    """Per-order observations: g, f, s (model idx), t (type), kd (k_f - k_s), dl (len_f - len_s)/1000, y."""

    def __init__(self, g, f, s, t, kd, dl, y):
        self.g = np.asarray(g, int); self.f = np.asarray(f, int); self.s = np.asarray(s, int)
        self.t = np.asarray(t, int); self.kd = np.asarray(kd, float); self.dl = np.asarray(dl, float)
        self.y = np.asarray(y, int)


def obs_from_matches(ms):
    """ms: list of dicts with g, a, b (indices), t, kd_ab, dl_ab, v1, v2 (raw positional votes). INVALID skipped."""
    G, F, S, T, KD, DL, Y = [], [], [], [], [], [], []
    for r in ms:
        for order in (1, 2):
            v = r["v1"] if order == 1 else r["v2"]
            if v not in VOTE_Y:
                continue
            if order == 1:
                f, s, kd, dl = r["a"], r["b"], r["kd_ab"], r["dl_ab"]
            else:
                f, s, kd, dl = r["b"], r["a"], -r["kd_ab"], -r["dl_ab"]
            G.append(r["g"]); F.append(f); S.append(s); T.append(r["t"]); KD.append(kd); DL.append(dl); Y.append(VOTE_Y[v])
    return Obs(G, F, S, T, KD, DL, Y)


class VerdictModel:
    def __init__(self, n_anchor, n_model, sigma0=1.0):
        self.G, self.M, self.sigma0 = n_anchor, n_model, sigma0
        self.kappa = 1.0; self.pi = 0.0; self.lam = 0.0
        self.gamma = np.zeros(3)
        self.u = np.zeros((n_anchor, n_model))
        self.sigma_v = 0.0; self.sigma_w = 0.0
        self.fit_info = {}

    # ------------------------------------------------------------------ likelihood
    def _unpack(self, x):
        return x[0], x[1], x[2], x[3:6], x[6:].reshape(self.G, self.M)

    def _nll(self, x, O):
        kappa, pi, lam, gam, u = self._unpack(x)
        dec = (O.t == 0).astype(float)
        eta = kappa * O.kd * dec + u[O.g, O.f] - u[O.g, O.s] + lam * O.dl + pi
        c = np.exp(gam[O.t])
        P1 = _sig(eta - c); P2 = _sig(-eta - c)
        P0 = np.maximum(1.0 - P1 - P2, 1e-12)
        P1c = np.maximum(P1, 1e-300); P2c = np.maximum(P2, 1e-300)
        y = O.y
        ll = np.where(y == 0, np.log(P1c), np.where(y == 1, np.log(P2c), np.log(P0)))
        dl_deta = np.where(y == 0, 1 - P1, np.where(y == 1, -(1 - P2), (-P1 * (1 - P1) + P2 * (1 - P2)) / P0))
        dl_dc = np.where(y == 0, -(1 - P1), np.where(y == 1, -(1 - P2), (P1 * (1 - P1) + P2 * (1 - P2)) / P0))
        g = np.zeros_like(x)
        g[0] = -(dl_deta * O.kd * dec).sum()
        g[1] = -dl_deta.sum()
        g[2] = -(dl_deta * O.dl).sum()
        gg = np.zeros(3)
        np.add.at(gg, O.t, dl_dc * c)
        g[3:6] = -gg
        gu = np.zeros((self.G, self.M))
        np.add.at(gu, (O.g, O.f), dl_deta)
        np.add.at(gu, (O.g, O.s), -dl_deta)
        g[6:] = -gu.ravel() + u.ravel() / self.sigma0 ** 2
        return float(-ll.sum() + 0.5 * (u ** 2).sum() / self.sigma0 ** 2), g

    def fit(self, O, use_length=True):
        x0 = np.zeros(6 + self.G * self.M)
        x0[0] = 1.0
        bounds = [(None, None)] * x0.size
        if not use_length:
            bounds[2] = (0.0, 0.0)
        bounds[3:6] = [(-8.0, 4.0)] * 3
        r = minimize(self._nll, x0, args=(O,), jac=True, method="L-BFGS-B", bounds=bounds,
                     options=dict(maxiter=5000, ftol=1e-12, gtol=1e-7))
        if not r.success:
            raise SystemExit("[VERDICT-MODEL] the fit did not converge: %s" % r.message)
        self.kappa, self.pi, self.lam, self.gamma, u = self._unpack(r.x)
        self.gamma = np.array(self.gamma)
        present = np.zeros((self.G, self.M), bool)
        present[O.g, O.f] = True; present[O.g, O.s] = True
        u = np.where(present, u, 0.0)
        for g in range(self.G):
            if present[g].any():
                u[g, present[g]] -= u[g, present[g]].mean()
        self.u = u
        vm = np.array([u[present[:, m], m].mean() if present[:, m].any() else 0.0 for m in range(self.M)])
        w = (u - vm[None, :])[present]
        have = present.any(axis=0)
        self.sigma_v = float(vm[have].std(ddof=1)) if have.sum() > 1 else 0.0
        self.sigma_w = float(w.std(ddof=1)) if w.size > 1 else 0.0
        self.fit_info = dict(nll=float(r.fun), n_obs=int(O.y.size), iters=int(r.nit), present=int(present.sum()))
        return self

    # ------------------------------------------------------------------ identity
    def params(self):
        return dict(kappa=self.kappa, pi=self.pi, lam=self.lam, gamma=[float(x) for x in self.gamma],
                    sigma_v=self.sigma_v, sigma_w=self.sigma_w, sigma0=self.sigma0,
                    u=[[float(x) for x in row] for row in self.u], G=self.G, M=self.M)

    def digest(self):
        return hashlib.sha256(json.dumps(self.params(), sort_keys=True).encode("utf-8")).hexdigest()

    @classmethod
    def from_params(cls, d):
        if d.get("mode") == "fresh-judge-v2" and cls is VerdictModel:      # dispatch to the v2 subclass (83f431b)
            return VerdictModelV2.from_params(d)
        vm = cls(d["G"], d["M"], d["sigma0"])
        vm.kappa, vm.pi, vm.lam = d["kappa"], d["pi"], d["lam"]
        vm.gamma = np.array(d["gamma"], float); vm.u = np.array(d["u"], float)
        vm.sigma_v, vm.sigma_w = d["sigma_v"], d["sigma_w"]
        return vm

    def lines(self, models=None, anchors=None):
        out = ["  VERDICT MODEL: kappa %+.4f | pi (first-position) %+.4f | lam (per 1k chars) %+.4f | tie cutpoints c ="
               " %s (DEC / AGREE / NONDEC) | sigma_v (model) %.4f | sigma_w (anchor x model) %.4f | ridge sigma0 %.2f"
               % (self.kappa, self.pi, self.lam, " / ".join("%.3f" % math.exp(x) for x in self.gamma),
                  self.sigma_v, self.sigma_w, self.sigma0),
               "    fit: %s | digest %s" % (self.fit_info, self.digest()[:16])]
        if models is not None:
            vm = self.u.mean(axis=0)
            order = np.argsort(vm)
            out.append("    model-level u (mean over anchors), lowest three: %s"
                       % ", ".join("%s %+.3f" % (models[k], vm[k]) for k in order[:3]))
        return out

    # ------------------------------------------------------------------ probabilities / simulation
    def _probs(self, g, f, s, t, kd, dl, u):
        dec = (t == 0).astype(float)
        eta = self.kappa * kd * dec + u[g, f] - u[g, s] + self.lam * dl + self.pi
        c = np.exp(self.gamma[t])
        P1 = _sig(eta - c); P2 = _sig(-eta - c)
        return np.stack([P1, P2, np.maximum(1 - P1 - P2, 0.0)], axis=1)

    def draw_u(self, rng, G=None, M=None):
        G = self.G if G is None else G; M = self.M if M is None else M
        return rng.normal(0.0, self.sigma_v, size=M)[None, :] + rng.normal(0.0, self.sigma_w, size=(G, M))

    def order_probs(self, S, u):
        """S: schedule dict of arrays g, a, b, t, kd (k_a - k_b), dl ((len_a - len_b)/1000). Returns (P_order1, P_order2)
        over (first, second, tie)."""
        P1 = self._probs(S["g"], S["a"], S["b"], S["t"], S["kd"], S["dl"], u)
        P2 = self._probs(S["g"], S["b"], S["a"], S["t"], -S["kd"], -S["dl"], u)
        return P1, P2

    @staticmethod
    def _draw(P, rng):
        U = rng.random(P.shape[0])
        return np.where(U < P[:, 0], 0, np.where(U < P[:, 0] + P[:, 1], 1, 2))

    def simulate(self, S, rng, mode="random", u=None, observed=None, r_keep=None):
        """Returns dict(y1, y2 (positional votes per order), wa (share won by a: 1 / 0 / 0.5), u)."""
        if mode == "random":
            u = self.draw_u(rng) if u is None else u
        elif mode in ("fixed", "retest"):
            u = self.u
        else:
            raise SystemExit("[VERDICT-MODEL] unknown mode %r" % mode)
        P1, P2 = self.order_probs(S, u)
        y1 = self._draw(P1, rng); y2 = self._draw(P2, rng)
        if mode == "retest":
            if observed is None or r_keep is None:
                raise SystemExit("[VERDICT-MODEL] retest mode needs the observed votes and r_keep")
            k1 = rng.random(y1.size) < r_keep; k2 = rng.random(y2.size) < r_keep
            y1 = np.where(k1 & (observed[0] >= 0), observed[0], y1)
            y2 = np.where(k2 & (observed[1] >= 0), observed[1], y2)
        return dict(y1=y1, y2=y2, wa=winner_share(y1, y2), u=u)


def winner_share(y1, y2):
    """Order 1 shows a first, order 2 shows b first. a wins iff order 1 says first (0) and order 2 says second (1)."""
    a_wins = (y1 == 0) & (y2 == 1)
    b_wins = (y1 == 1) & (y2 == 0)
    return np.where(a_wins, 1.0, np.where(b_wins, 0.0, 0.5))


def expected_retest_agreement(vm, S, observed, r):
    """Exact expected 3-way agreement of a retest winner with the observed winner, at keep probability r."""
    P1, P2 = vm.order_probs(S, vm.u)
    o1, o2 = observed
    Q1 = (1 - r) * P1; Q2 = (1 - r) * P2
    Q1[np.arange(o1.size), np.maximum(o1, 0)] += np.where(o1 >= 0, r, 0.0)
    Q2[np.arange(o2.size), np.maximum(o2, 0)] += np.where(o2 >= 0, r, 0.0)
    pa = Q1[:, 0] * Q2[:, 1]; pb = Q1[:, 1] * Q2[:, 0]; pt = 1 - pa - pb
    w_obs = winner_share(o1, o2)
    agree = np.where(w_obs == 1.0, pa, np.where(w_obs == 0.0, pb, pt))
    return float(agree.mean())


def solve_r_keep(vm, S, observed, target=RETEST_AGREEMENT_OF_RECORD):
    lo, hi = 0.0, 1.0
    a_lo = expected_retest_agreement(vm, S, observed, lo)
    a_hi = expected_retest_agreement(vm, S, observed, hi)
    if not (a_lo <= target <= a_hi):
        return None, a_lo, a_hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if expected_retest_agreement(vm, S, observed, mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), a_lo, a_hi


# =====================================================================================================================
# FRESH-JUDGE v2 (POST-HOC-SPECIFIED; ruling 1 of 83f431b, docs/judge_v2_program.md L15341-L15365). Appended by the
# engine-coder; the v1 class above is unchanged except for the dispatch line in from_params, so the registered v1 modes
# stay byte-identical (the selftest pins the v1 readout's sha256 computed at 4c2d2b5).
#   eta_v2 = eta_v1 + beta * (keyacc_f - keyacc_s), beta fitted JOINTLY in the likelihood; keyacc = convention-A key
#   accuracy of the model in the anchor over the board's judged questions (a design leg: over the design's EVAL supply).
#   u = epsilon_m + w_gm keeps the ridge sigma0 = 1.0. Fresh draws: epsilon_m ~ N(0, sigma_eps_LOMO^2), where
#   sigma_eps_LOMO is the LEAVE-ONE-MODEL-OUT prediction SD of the model's total effect (beta * keyacc + u, both centred
#   per anchor) from a fit that never saw the model; w_gm ~ N(0, sigma_w^2) as in v1.
# [CORRECTED 2026-09-24 by RULING A (4b25059, docs/judge_v2_program.md L15377-L15389), inserted by the engine-coder:
# beta is UNPENALISED and u carries the ridge (sigma0 = 1.0), so at the MAP beta is the least-squares PROJECTION of the
# anchor-centred total effect (beta x keyacc + u) on keyacc; its estimand is the in-sample slope of the judge's total
# model preference on key accuracy. The selftest reading "beta and u are collinear; identified only through the ridge"
# (a944d22) is WITHDRAWN: it compared beta-hat with the generator's beta in a world whose u correlates with keyacc, where
# the ORACLE projection is what beta-hat recovers. keyacc is MODEL-LEVEL (pooled over anchors, centred per anchor).
# A two-stage estimator (u after beta) is REJECTED by the same ruling.]
# MUTANT "lomo_leak" (READY 5dfc825 D1) keeps model m's observations in its own LOMO refit.
# MUTANT is a SELFTEST-ONLY switch (None in every real run; the selftest sets it and restores it): "beta_zero" drops the
# beta term from the simulation, "beta_unfit" pins beta at 0 in the fit, "lomo_zero" sets sigma_eps_LOMO = 0.
# =====================================================================================================================
V2_MODE = "fresh-judge-v2"
POST_HOC = "POST-HOC-SPECIFIED (fresh-judge v2, ruling 1 of 83f431b; specified after the R = 1 dry run)"
MUTANT = None


def diagnostics_line(vm):
    """RULING A (v): the four diagnostics printed beside the verdict, deciding nothing."""
    c = getattr(vm, "corr_u_keyacc", float("nan"))
    return ("    DIAGNOSTICS (ruling A (v), 4b25059; deciding nothing): beta-hat %+.4f | sigma_eps_LOMO %.4f | the %d LOMO errors"
            " [%s] | corr(u-hat, keyacc) %+.2e = an OPTIMISER CHECK only (zero by construction at the MAP, D5 ruling;"
            " expected |.| < 1e-3): %s" % (vm.beta, vm.sigma_eps_lomo, len(vm.lomo_errors),
                                          ", ".join("%+.4f" % x for x in vm.lomo_errors), c,
                                          "OK" if abs(c) < 1e-3 else ("n/a" if c != c else "EXCEEDS 1e-3: the fit is not at the MAP")))


class ObsV2(Obs):
    def __init__(self, g, f, s, t, kd, dl, y, ka):
        Obs.__init__(self, g, f, s, t, kd, dl, y)
        self.ka = np.asarray(ka, float)

    def subset(self, mask):
        return ObsV2(self.g[mask], self.f[mask], self.s[mask], self.t[mask], self.kd[mask], self.dl[mask], self.y[mask],
                     self.ka[mask])


def obs_v2_from(O, KA):
    """Attach keyacc differences (first-shown minus second-shown) to v1 observations."""
    return ObsV2(O.g, O.f, O.s, O.t, O.kd, O.dl, O.y, KA[O.g, O.f] - KA[O.g, O.s])


class VerdictModelV2(VerdictModel):
    def __init__(self, n_anchor, n_model, sigma0=1.0):
        VerdictModel.__init__(self, n_anchor, n_model, sigma0)
        self.lomo_models = []
        self.lomo_leak_obs = 0
        self.beta = 0.0
        self.sigma_eps_lomo = 0.0
        self.lomo_errors = []
        self.present = np.zeros((n_anchor, n_model), bool)

    def _unpack2(self, x):
        return x[:6 + self.G * self.M], x[6 + self.G * self.M]

    def _nll(self, x, O):
        x1, beta = self._unpack2(x)
        kappa, pi, lam, gam, u = self._unpack(x1)
        dec = (O.t == 0).astype(float)
        eta = kappa * O.kd * dec + u[O.g, O.f] - u[O.g, O.s] + lam * O.dl + pi + beta * O.ka
        c = np.exp(gam[O.t])
        P1 = _sig(eta - c); P2 = _sig(-eta - c)
        P0 = np.maximum(1.0 - P1 - P2, 1e-12)
        P1c = np.maximum(P1, 1e-300); P2c = np.maximum(P2, 1e-300)
        y = O.y
        ll = np.where(y == 0, np.log(P1c), np.where(y == 1, np.log(P2c), np.log(P0)))
        dl_deta = np.where(y == 0, 1 - P1, np.where(y == 1, -(1 - P2), (-P1 * (1 - P1) + P2 * (1 - P2)) / P0))
        dl_dc = np.where(y == 0, -(1 - P1), np.where(y == 1, -(1 - P2), (P1 * (1 - P1) + P2 * (1 - P2)) / P0))
        g = np.zeros_like(x)
        g[0] = -(dl_deta * O.kd * dec).sum()
        g[1] = -dl_deta.sum()
        g[2] = -(dl_deta * O.dl).sum()
        gg = np.zeros(3)
        np.add.at(gg, O.t, dl_dc * c)
        g[3:6] = -gg
        gu = np.zeros((self.G, self.M))
        np.add.at(gu, (O.g, O.f), dl_deta)
        np.add.at(gu, (O.g, O.s), -dl_deta)
        g[6:6 + self.G * self.M] = -gu.ravel() + u.ravel() / self.sigma0 ** 2
        g[6 + self.G * self.M] = -(dl_deta * O.ka).sum()
        return float(-ll.sum() + 0.5 * (u ** 2).sum() / self.sigma0 ** 2), g

    def fit(self, O, use_length=True):
        n = 6 + self.G * self.M
        x0 = np.zeros(n + 1)
        x0[0] = 1.0
        bounds = [(None, None)] * x0.size
        if not use_length:
            bounds[2] = (0.0, 0.0)
        bounds[3:6] = [(-8.0, 4.0)] * 3
        if MUTANT == "beta_unfit":
            bounds[n] = (0.0, 0.0)
        r = minimize(self._nll, x0, args=(O,), jac=True, method="L-BFGS-B", bounds=bounds,
                     options=dict(maxiter=5000, ftol=1e-12, gtol=1e-7))
        if not r.success:
            raise SystemExit("[VERDICT-MODEL v2] the fit did not converge: %s" % r.message)
        x1, beta = self._unpack2(r.x)
        self.beta = float(beta)
        self.kappa, self.pi, self.lam, self.gamma, u = self._unpack(x1)
        self.gamma = np.array(self.gamma)
        present = np.zeros((self.G, self.M), bool)
        present[O.g, O.f] = True; present[O.g, O.s] = True
        u = np.where(present, u, 0.0)
        for gi in range(self.G):
            if present[gi].any():
                u[gi, present[gi]] -= u[gi, present[gi]].mean()
        self.u = u
        self.present = present
        vm = np.array([u[present[:, m], m].mean() if present[:, m].any() else 0.0 for m in range(self.M)])
        w = (u - vm[None, :])[present]
        have = present.any(axis=0)
        self.sigma_v = float(vm[have].std(ddof=1)) if have.sum() > 1 else 0.0
        self.sigma_w = float(w.std(ddof=1)) if w.size > 1 else 0.0
        self.fit_info = dict(nll=float(r.fun), n_obs=int(O.y.size), iters=int(r.nit), present=int(present.sum()))
        return self

    def fit_lomo(self, O, KA, use_length=True):
        """The full fit, then sigma_eps_LOMO: for each model m, refit WITHOUT any observation involving m and predict m's
        total effect (beta * keyacc + u, both centred per anchor over the models present) by beta_(-m) * keyacc alone;
        sigma_eps_LOMO = sqrt(mean over models of the anchor-averaged prediction error squared)."""
        self.fit(O, use_length)
        pres = self.present
        kac = np.where(pres, KA, 0.0)
        for gi in range(self.G):
            if pres[gi].any():
                kac[gi, pres[gi]] = KA[gi, pres[gi]] - KA[gi, pres[gi]].mean()
        total = self.beta * kac + self.u
        errs = []
        models_done = []
        self.lomo_leak_obs = 0
        for m in range(self.M):
            if not pres[:, m].any():
                continue
            keep = (O.f != m) & (O.s != m)
            if MUTANT == "lomo_leak":
                keep = np.ones_like(keep)
            sub_obs = O.subset(keep)
            sub = VerdictModelV2(self.G, self.M, self.sigma0).fit(sub_obs, use_length)
            pred = sub.beta * kac[:, m]
            errs.append(float((total[pres[:, m], m] - pred[pres[:, m]]).mean()))
            models_done.append(m)
            # READY 5dfc825 D1: the refit must NOT see model m (its observations are excluded); counted, checked by the selftest
            self.lomo_leak_obs += int(((sub_obs.f == m) | (sub_obs.s == m)).sum())
        self.lomo_errors = errs
        self.lomo_models = models_done
        self.sigma_eps_lomo = 0.0 if MUTANT == "lomo_zero" else (float(np.sqrt(np.mean(np.square(errs)))) if errs else 0.0)
        uu, kk = self.u[pres], kac[pres]
        self.corr_u_keyacc = float(np.corrcoef(uu, kk)[0, 1]) if uu.size > 2 and uu.std() > 0 and kk.std() > 0 else float("nan")
        return self

    def params(self):
        d = VerdictModel.params(self)
        d.update(mode=V2_MODE, beta=self.beta, sigma_eps_lomo=self.sigma_eps_lomo,
                 lomo_errors=[float(x) for x in self.lomo_errors], corr_u_keyacc=getattr(self, "corr_u_keyacc", float("nan")),
                 lomo_models=[int(x) for x in getattr(self, "lomo_models", [])])
        return d

    @classmethod
    def from_params(cls, d):
        vm = cls(d["G"], d["M"], d["sigma0"])
        vm.kappa, vm.pi, vm.lam = d["kappa"], d["pi"], d["lam"]
        vm.gamma = np.array(d["gamma"], float); vm.u = np.array(d["u"], float)
        vm.sigma_v, vm.sigma_w = d["sigma_v"], d["sigma_w"]
        vm.beta, vm.sigma_eps_lomo = d["beta"], d["sigma_eps_lomo"]
        vm.lomo_errors = list(d.get("lomo_errors", []))
        vm.corr_u_keyacc = d.get("corr_u_keyacc", float("nan"))
        vm.lomo_models = list(d.get("lomo_models", []))
        return vm

    def lines(self, models=None, anchors=None):
        out = VerdictModel.lines(self, models, anchors)
        out.insert(0, "  " + POST_HOC)
        out.append("    v2: beta (per unit keyacc difference, fitted jointly) %+.4f | sigma_eps_LOMO %.4f over %d held-out models"
                   " (in-sample sigma_v %.4f) | fresh draws: epsilon ~ N(0, sigma_eps_LOMO^2), w ~ N(0, sigma_w^2)"
                   % (self.beta, self.sigma_eps_lomo, len(self.lomo_errors), self.sigma_v))
        out.append(diagnostics_line(self))
        return out

    def _probs2(self, g, f, s, t, kd, dl, ka, u):
        beta = 0.0 if MUTANT == "beta_zero" else self.beta
        dec = (t == 0).astype(float)
        eta = self.kappa * kd * dec + u[g, f] - u[g, s] + self.lam * dl + self.pi + beta * ka
        c = np.exp(self.gamma[t])
        P1 = _sig(eta - c); P2 = _sig(-eta - c)
        return np.stack([P1, P2, np.maximum(1 - P1 - P2, 0.0)], axis=1)

    def order_probs(self, S, u):
        if "ka" not in S:
            raise SystemExit("[VERDICT-MODEL v2] the schedule carries no keyacc difference 'ka'")
        P1 = self._probs2(S["g"], S["a"], S["b"], S["t"], S["kd"], S["dl"], S["ka"], u)
        P2 = self._probs2(S["g"], S["b"], S["a"], S["t"], -S["kd"], -S["dl"], -S["ka"], u)
        return P1, P2

    def draw_u(self, rng, G=None, M=None):
        G = self.G if G is None else G; M = self.M if M is None else M
        return rng.normal(0.0, self.sigma_eps_lomo, size=M)[None, :] + rng.normal(0.0, self.sigma_w, size=(G, M))
