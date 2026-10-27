"""G22, the arena simulator: the legs (a)-(h). The CLI is tools/analysis/archv2_g22_sim.py; the docstring there is the
launch sequence. Everything here takes loaded objects, so the selftest runs every leg on synthetic worlds.

THE VALIDITY LEG DECIDES WHETHER THE SIMULATOR DECIDES ANYTHING. It writes a token (JSON) with its status and the fitted
verdict model; legs (c), (d), (e) and the simulated part of (g) REFUSE unless handed a PASS token whose verdict-model
digest re-computes. Legs (b), (f) and (h) are measurements on existing boards and the key, not simulations: they run
without the token and print its absence.
"""
import hashlib
import json
import math
import os
import random
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import cert, data, design, report
from .report import hit, need, quantiles
from .streams import Streams
from .verdict_model import (POST_HOC, RETEST_AGREEMENT_OF_RECORD, V2_MODE, VOTE_Y, VerdictModel, VerdictModelV2,
                            match_type, obs_from_matches, obs_v2_from, solve_r_keep)

GAP = 0.02
REGISTERED = "registered bar, ARCH-V2-G22 at d6129cf (programme L15208-L15265)"
REG_RULE = ("REGISTERED 2026-09-24 at d6129cf (ARCH-V2-G22, programme L15208-L15265)")
FALLBACK_D = "the binned gate or the raw certificate (named in advance by the arena proposal section 2.5)"
# The record's targets for the validity leg (GROK-CALIB, programme L3914ff; grok_calib_outcome.txt; JUDGE-WIRING-BOARD
# L4258 for the Kotlin draw's delta-deviance).
TARGETS = dict(
    f_raw_called=733, f_raw_wrong=7, f_loao_called=667, f_loao_wrong=2, f_loao_wrong_est=1, f_loao_nominal=1.11,
    u_raw_called=740, u_raw_wrong=8, u_loao_called=653, u_loao_wrong=2, u_loao_wrong_est=1, u_loao_nominal=1.24,
)
TARGET_EDGES = dict(f=891, u=920, est=809)
DDEV_TARGETS = (4.47, 2.26)
_CTX = {}
MUTANT = None          # SELFTEST-ONLY switch (None in every real run): chain_missing_ok, chain_digest_unchecked,
#                        chain_oldlf16_unchecked, chain_successor_unchecked, store_draws_random, replay_touches_one_shot,
#                        replay_mints_token, bias_line_missing, half_seed, half_drop, h2_fast, t2_offbyone, u_zero,
#                        gate_presence_only, one_shot_off, p7_tie_held, p7_x12_scored, p7_roster_merged_only,
#                        half_same, residue_all_wrong,
                       # ties_broken, holm_off


def _init_worker(ctx):
    global _CTX
    from . import ro
    ro.install_global_guard()          # a worker opens no DB; the guard makes that a refusal, not a hope
    _CTX = ctx


def run_reps(fn, ctx, tasks, workers, parent_streams):
    """Sequential when workers <= 1 (the only mode the selftest executes); otherwise a process pool. Each task
    returns (record, streams_log, witness_delta); logs merge into the parent's, witness deltas add up."""
    global _CTX
    out = []
    if workers <= 1:
        _CTX = ctx
        results = map(fn, tasks)
    else:
        ex = ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(ctx,))
        results = ex.map(fn, tasks, chunksize=1)
    for rec, log, wit in results:
        parent_streams.merge(log)
        if workers > 1:
            for k, v in wit.items():
                data.WITNESS[k] += v
        out.append(rec)
    if workers > 1:
        ex.shutdown()
    return out


def _witness_snapshot():
    return dict(data.WITNESS)


def _witness_delta(before):
    return {k: v - before.get(k, 0) for k, v in data.WITNESS.items() if v - before.get(k, 0)}


def decide_rate(k, n, bar, good="high"):
    """A rate against its REGISTERED bar (d6129cf), read by its Wilson 95% interval; the interval decides. good="high": MEETS iff lo >= bar, BELOW iff
    hi < bar; good="low": MEETS iff hi <= bar, EXCEEDS iff lo > bar; otherwise UNRESOLVED AT THIS R."""
    lo, hi = cert.wilson(k, n)
    if good == "high":
        word = "MEETS" if lo >= bar else ("BELOW" if hi < bar else "UNRESOLVED AT THIS R")
    else:
        word = "MEETS" if hi <= bar else ("EXCEEDS" if lo > bar else "UNRESOLVED AT THIS R")
    hit("RATE.%s.%s" % (good, word.split()[0]))
    return word, lo, hi


# ----------------------------------------------------------------------------------------------- board -> model
def board_matrix(board, floor=200):
    """Match-level arrays of the anchors that pass the floor: the schedule S (g, a, b, t, kd, dl), the observed per-order
    votes, and the per-match metadata to rebuild a board from simulated verdicts."""
    models = board.models
    midx = {m: k for k, m in enumerate(models)}
    anchors = [a for a in sorted(board.by) if len(board.by[a]) >= floor]
    g, A, Bm, T, KD, DL, Y1, Y2, meta = [], [], [], [], [], [], [], [], []
    for gi, anc in enumerate(anchors):
        for (a, b, q, w), (v1, v2) in zip(board.by[anc], board.votes[anc]):
            ka, kb = board.K.get(q, {}).get(a), board.K.get(q, {}).get(b)
            pa, pb = board.P.get(q, {}).get(a, ""), board.P.get(q, {}).get(b, "")
            la, lb = board.L.get(q, {}).get(a), board.L.get(q, {}).get(b)
            g.append(gi); A.append(midx[a]); Bm.append(midx[b])
            T.append(match_type(-1 if ka is None else ka, -1 if kb is None else kb, pa, pb))
            KD.append(float(ka - kb) if ka is not None and kb is not None else 0.0)
            DL.append((la - lb) / 1000.0 if la is not None and lb is not None else 0.0)
            Y1.append(VOTE_Y.get(v1, -1)); Y2.append(VOTE_Y.get(v2, -1))
            meta.append((anc, a, b, q))
    S = dict(g=np.array(g), a=np.array(A), b=np.array(Bm), t=np.array(T), kd=np.array(KD), dl=np.array(DL))
    return anchors, S, (np.array(Y1), np.array(Y2)), meta


def fit_verdict_model(board, anchors, S, observed, use_length=True, sigma0=1.0):
    ms = [dict(g=int(S["g"][k]), a=int(S["a"][k]), b=int(S["b"][k]), t=int(S["t"][k]), kd_ab=float(S["kd"][k]),
               dl_ab=float(S["dl"][k]),
               v1={0: "Model A", 1: "Model B", 2: "TIE"}.get(int(observed[0][k]), "INVALID"),
               v2={0: "Model A", 1: "Model B", 2: "TIE"}.get(int(observed[1][k]), "INVALID"))
          for k in range(S["g"].size)]
    return VerdictModel(len(anchors), len(board.models), sigma0).fit(obs_from_matches(ms), use_length=use_length)


def with_verdicts(board, meta, sim):
    nb = data.Board.__new__(data.Board)
    nb.label = board.label + "+sim"; nb.models = board.models
    nb.K, nb.P, nb.L = board.K, board.P, board.L
    nb.by = defaultdict(list); nb.votes = defaultdict(list); nb.n_valid = len(meta)
    v = {0: "Model A", 1: "Model B", 2: "TIE"}
    for k, (anc, a, b, q) in enumerate(meta):
        wa = sim["wa"][k]
        nb.by[anc].append((a, b, q, a if wa == 1.0 else (b if wa == 0.0 else "TIE")))
        nb.votes[anc].append((v[int(sim["y1"][k])], v[int(sim["y2"][k])]))
    return nb


# ------------------------------------------------------------------------------------------------ metrics
def cert_metrics(edges, est_keys, gap=GAP, min_est=50):
    for e in edges:
        e["est"] = (e["anchor"], e["a"], e["b"]) in est_keys
    out = {}
    fpar = None
    for tag, sel in (("f", [e for e in edges if e["gap"] >= gap]), ("u", edges)):
        E = cert.EdgeArrays(sel)
        rc = cert.craw_v(E.p) >= cert.THRESH
        L = cert.loao_v(E)
        if tag == "f":
            fpar = (L["b0"], L["b1"])
        out.update({"%s_n" % tag: len(E), "%s_raw_called" % tag: int(rc.sum()), "%s_raw_wrong" % tag: int((rc & ~E.right).sum()),
                    "%s_loao_called" % tag: L["n_called"], "%s_loao_wrong" % tag: L["wrong"],
                    "%s_loao_wrong_est" % tag: L["wrong_est"], "%s_loao_nominal" % tag: L["nominal"],
                    "%s_util" % tag: L["n_called"] / max(1, len(E)), "%s_b1" % tag: L["b1"]})
    est = cert.EdgeArrays([e for e in edges if e["gap"] >= gap and e["est"]])
    out["est_n"] = len(est)
    out["unident"] = cert.unidentified(est) if len(est) else "no edges"
    if len(est) >= min_est and out["unident"] is None:
        b1e, dd, _ = cert.ddev_v(est, x0=fpar)
    else:
        b1e, dd = float("nan"), float("nan")
    out["b1_est"], out["ddev"] = b1e, dd
    we = [e for e in edges if e["est"] and not e["right"]]
    inc = Counter()
    for e in we:
        inc[e["a"]] += 1; inc[e["b"]] += 1
    out["wrong_est_all"] = len(we)
    top = inc.most_common(1)
    out["top_model"], out["top_share"] = (top[0][0], top[0][1] / len(we)) if we else ("-", 0.0)
    out["top_set"] = "{%s}" % ", ".join(top_set(inc)[1]) if we else "-"      # ruling 5: ties as a SET (v2 prints it)
    return out


def top_set(inc):
    """(max incidence, the SORTED SET of models at it): ruling 5 of 83f431b, ties are never broken by name."""
    if not inc:
        return 0, []
    mx = max(inc.values())
    s = sorted(m for m, v in inc.items() if v == mx)
    if MUTANT == "ties_broken":
        s = s[-1:]
    return mx, s


# ============================================================================================ (a) VALIDITY
def _validity_rep(task):
    mode, r = task
    C = _CTX
    before = _witness_snapshot()
    st = Streams(C["master"])
    vm = VerdictModel.from_params(C["vm"])
    tag = C.get("tag", "validity")
    sim = vm.simulate(C["S"], st.np("%s/%s/rep%04d/verdicts" % (tag, mode, r)), mode=mode,
                      observed=C["obs"], r_keep=C["r_keep"])
    b2 = with_verdicts(C["board"], C["meta"], sim)
    edges, _ = data.edges_fast(b2, C["B"], st, "%s/%s/rep%04d" % (tag, mode, r), floor=C["floor"])
    return cert_metrics(edges, C["est_keys"], min_est=C["min_est"]), st.log, _witness_delta(before)


def bonferroni_level(T, family_alpha=0.05):
    """The registered validity interval (d6129cf, ruling (1)): each target inside its central (1 - alpha / T)
    interval, so the family-wise false-FAIL rate under a correct simulator is <= alpha."""
    need(T >= 1, "validity needs at least one target")
    return 1.0 - family_alpha / T


def covered(values, target, level):
    """(covered, q_lo, median, q_hi) of target against the central `level` interval of values."""
    ql, qm, qh = quantiles(values, ((1 - level) / 2, 0.5, (1 + level) / 2))
    return bool(ql <= target <= qh), ql, qm, qh


def validity_leg(say, board, sb, streams, R=1000, B=300, family_alpha=0.05, modes=("random", "fixed", "retest"),
                 primary="random", floor=200, targets=None, ddev_targets=DDEV_TARGETS, edge_targets=None,
                 retest_target=RETEST_AGREEMENT_OF_RECORD, workers=1, use_length=True, min_est=50, v2=False,
                 tag="validity", store=None):
    import time as _t
    t_leg0 = _t.time()
    t_reps = 0.0; rep_units = 0
    targets = dict(TARGETS if targets is None else targets)
    edge_targets = dict(TARGET_EDGES if edge_targets is None else edge_targets)
    T = len(targets) + len(ddev_targets)
    level = bonferroni_level(T, family_alpha)
    say("", "=== (a) VALIDITY LEG: the simulator fitted on %s must reproduce the record ===" % board.label,
        "  targets: edges %s | %s | delta-deviance range must cover %s"
        % (edge_targets, ", ".join("%s %s" % (k, v) for k, v in targets.items()),
           " and ".join("%.2f" % x for x in ddev_targets) or "(none given)"),
        "  rule (%s, ruling (1), Bonferroni): EVERY target inside its simulated central (1 - %.2f / T) interval of"
        " the PRIMARY (fresh-judge) mode %s; T = %d targets (%d counts + %d delta-deviance values) -> central %.5f"
        " interval; R %d replicates per mode, B %d" % (REG_RULE, family_alpha, primary, T, len(targets),
                                                      len(ddev_targets), level, R, B))
    lab = (" [%s]" % POST_HOC) if v2 else ""
    if v2:
        say("  MODE: %s; keyacc under convention A over the board's judged questions; the verdict model below is the v2"
            " model (beta fitted jointly, sigma_eps_LOMO for the fresh draws)" % POST_HOC)
    anchors, S, obs, meta = board_matrix(board, floor)
    need(len(anchors) > 0, "no anchor passes the %d-row floor" % floor)
    if v2:
        KA = keyacc_matrix(board, anchors)
        S = with_ka(S, KA)
    real_edges, aq = data.edges_fast(board, B, streams, "%s/real" % tag, floor=floor)
    data.mark_established(real_edges, board.K, aq, sb)
    est_keys = {(e["anchor"], e["a"], e["b"]) for e in real_edges if e["est"]}
    real = cert_metrics(real_edges, est_keys, min_est=min_est)
    data.WITNESS["validity.%s_path" % ("v2" if v2 else "v1")] += 1       # execution witness: which path ran
    say("  the real board through the NEW fast builder (numpy boards, stream %s/real; the record's own stream is"
        " build()'s random.Random(42) through rj.mm_fit, so these are a re-draw of the bootstrap, printed beside):" % tag,
        "    edges f %d / u %d / established %d (record %d / %d / %d: %s) | f raw %d / %d | f LOAO %d / %d (%d) %.2f |"
        " u raw %d / %d | u LOAO %d / %d (%d) %.2f | est b1 %+.4f ddev %.2f"
        % (real["f_n"], real["u_n"], real["est_n"], edge_targets["f"], edge_targets["u"], edge_targets["est"],
           "EDGE SETS MATCH" if (real["f_n"], real["u_n"], real["est_n"]) == (edge_targets["f"], edge_targets["u"], edge_targets["est"]) else "EDGE SETS DIFFER",
           real["f_raw_called"], real["f_raw_wrong"], real["f_loao_called"], real["f_loao_wrong"], real["f_loao_wrong_est"],
           real["f_loao_nominal"], real["u_raw_called"], real["u_raw_wrong"], real["u_loao_called"], real["u_loao_wrong"],
           real["u_loao_wrong_est"], real["u_loao_nominal"], real["b1_est"], real["ddev"]))
    edge_sets_match = (real["f_n"], real["u_n"], real["est_n"]) == (edge_targets["f"], edge_targets["u"], edge_targets["est"])
    vm = (fit_verdict_model_v2(board, anchors, S, obs, KA, use_length=use_length) if v2
          else fit_verdict_model(board, anchors, S, obs, use_length=use_length))
    say(*vm.lines(board.models))
    r_keep, a_lo, a_hi = solve_r_keep(vm, S, obs, retest_target)
    if r_keep is None:
        hit("VALIDITY.RETEST_UNSOLVABLE")
        say("  retest mode: the target agreement %.3f is outside the reachable range [%.3f, %.3f]; retest mode SKIPPED"
            % (retest_target, a_lo, a_hi))
        modes = tuple(m for m in modes if m != "retest")
    else:
        say("  retest mode: r_keep %.4f reproduces the measured re-draw agreement %.3f (reachable [%.3f, %.3f])"
            % (r_keep, retest_target, a_lo, a_hi))
    ctx = dict(master=streams.master, vm=vm.params(), S=S, obs=obs, r_keep=r_keep, board=board, meta=meta, B=B,
               floor=floor, est_keys=est_keys, min_est=min_est, tag=tag)
    results = {}
    verdict_ok = {}
    for mode in modes:
        t_r0 = _t.time()
        recs = run_reps(_validity_rep, ctx, [(mode, r) for r in range(R)], workers, streams)
        t_reps += _t.time() - t_r0; rep_units += len(recs)
        store_put(store, "%s.%s" % (tag, mode), recs)          # G22-REBIND-1: additive, write-once, no random number
        results[mode] = recs
        say("", "  mode %-7s (%d replicates)%s%s" % (mode, len(recs), "   <- PRIMARY (the downstream legs' mode)" if mode == primary
                                                  else ("   (printed, deciding nothing)" if v2 else ""), lab),
            "    %-20s %9s %9s %9s %9s %10s  %s" % ("statistic", "target", "q_lo", "median", "q_hi", "pct(target)", "covered"))
        ok = True
        for key, tv in targets.items():
            v = np.array([r[key] for r in recs], dtype=float)
            cov, ql, qm, qh = covered(v, tv, level)
            pct = float((v < tv).mean() + 0.5 * (v == tv).mean())
            ok &= bool(cov)
            say("    %-20s %9.2f %9.2f %9.2f %9.2f %10.3f  %s" % (key, tv, ql, qm, qh, pct, "yes" if cov else "NO"))
        dd = np.array([r["ddev"] for r in recs], dtype=float)
        fin = dd[np.isfinite(dd)]
        ql, qm, qh = quantiles(fin, ((1 - level) / 2, 0.5, (1 + level) / 2))
        dcov = all(covered(fin, x, level)[0] for x in ddev_targets) if fin.size else False
        ok &= bool(dcov)
        say("    %-20s %9s %9.2f %9.2f %9.2f %10s  %s   (finite in %d of %d; not identified by the 3.84 bar in %d)"
            % ("delta-deviance", "/".join("%.2f" % x for x in ddev_targets), ql, qm, qh, "-", "yes" if dcov else "NO",
               fin.size, dd.size, int((fin < cert.CHI2_1_95).sum()) + int((~np.isfinite(dd)).sum())))
        tops = Counter(r["top_model"] for r in recs)
        shares = [r["top_share"] for r in recs]
        say("    descriptive: wrong(established) over all edges median %.0f; the most-incident model's share median %.2f"
            " (real board: %s at %.2f); modal top model %s"
            % (float(np.median([r["wrong_est_all"] for r in recs])), float(np.median(shares)), real["top_model"],
               real["top_share"], tops.most_common(1)[0][0] if tops else "-"))
        if v2:
            tops = Counter()
            for x in recs:
                tops[x.get("top_set", "-")] += 1
            say("    ALL-WRONG population (printed under its own name; ties as a SET): the real board's most-incident set %s;"
                " modal simulated set %s" % (real.get("top_set", "-"), tops.most_common(1)[0][0] if tops else "-"))
        verdict_ok[mode] = ok
    status = "PASS" if verdict_ok.get(primary, False) and edge_sets_match else "FAIL"
    say("")
    if v2:
        # READY 5dfc825 D10: inside v2 the inner line reports PART A only; the leg's verdict follows part B
        hit("VALIDITY.%s" % status)
        say("  v2 PART A (the 14 full-board targets) [%s]: %s%s" % (POST_HOC, status, "" if status == "PASS" else " (%s)" % (
            "the edge sets differ from the record's" if not edge_sets_match else "a target lies outside the primary mode's interval")))
    elif status == "PASS":
        hit("VALIDITY.PASS")
        say("  VALIDITY LEG: PASS (%s): every one of the T = %d targets lies inside its central %.5f interval in mode"
            " %s; the downstream legs may run.%s" % (REG_RULE, T, level, primary, lab))
    else:
        hit("VALIDITY.FAIL")
        say("  VALIDITY LEG: FAIL (%s): %s. THE SIMULATOR DECIDES NOTHING; legs (c), (d), (e) and the simulated (g)"
            " REFUSE.%s" % (REG_RULE, "the edge sets differ from the record's" if not edge_sets_match
                            else "a target lies outside the primary mode's interval", lab))
    return dict(status=status, primary=primary, real=real, verdict_model=vm.params(), vm_digest=vm.digest(), coverage=level, T=T, family_alpha=family_alpha,
                R=R, B=B, targets=targets, ddev_targets=list(ddev_targets), modes_ok=verdict_ok,
                edge_sets_match=edge_sets_match, master=streams.master, r_keep=r_keep,
                timing=dict(fixed_s=_t.time() - t_leg0 - t_reps, reps_s=t_reps, rep_units=rep_units)), results



# ============================================================================== FRESH-JUDGE v2 (ruling 1, 83f431b)
HALF_MASTER = "ARCHV2-G22-V2-HALF-1"             # the held-out half seed, registered at 83f431b before any split
H2_TARGET_KEYS = ("f_raw_called", "f_raw_wrong", "f_loao_called", "f_loao_wrong", "f_loao_wrong_est", "f_loao_nominal",
                  "u_raw_called", "u_raw_wrong", "u_loao_called", "u_loao_wrong", "u_loao_wrong_est", "u_loao_nominal")


def keyacc_matrix(board, anchors, models=None):
    """RULING A (4b25059): MODEL-LEVEL keyacc. Convention-A correct counts per (anchor, model) over the anchor's JUDGED
    questions (a missing key row counts wrong), pooled over ALL anchors per model, broadcast to every anchor and centred
    per anchor over the models present (design.model_level_keyacc, shared with the design legs)."""
    models = board.models if models is None else models
    correct = np.zeros((len(anchors), len(models)))
    n = np.zeros(len(anchors))
    present = np.zeros((len(anchors), len(models)), bool)
    for gi, anc in enumerate(anchors):
        qs = sorted({r[2] for r in board.by[anc]})
        n[gi] = len(qs)
        in_anchor = {r[0] for r in board.by[anc]} | {r[1] for r in board.by[anc]}
        for mi, m in enumerate(models):
            correct[gi, mi] = sum(1 for q in qs if board.K.get(q, {}).get(m) == 1)
            present[gi, mi] = m in in_anchor
    return design.model_level_keyacc(correct, n, present)


def with_ka(S, KA):
    S2 = dict(S)
    S2["ka"] = KA[S["g"], S["a"]] - KA[S["g"], S["b"]]
    return S2


def fit_verdict_model_v2(board, anchors, S, observed, KA, use_length=True, sigma0=1.0):
    ms = [dict(g=int(S["g"][k]), a=int(S["a"][k]), b=int(S["b"][k]), t=int(S["t"][k]), kd_ab=float(S["kd"][k]),
               dl_ab=float(S["dl"][k]),
               v1={0: "Model A", 1: "Model B", 2: "TIE"}.get(int(observed[0][k]), "INVALID"),
               v2={0: "Model A", 1: "Model B", 2: "TIE"}.get(int(observed[1][k]), "INVALID"))
          for k in range(S["g"].size)]
    O2 = obs_v2_from(obs_from_matches(ms), KA)
    return VerdictModelV2(len(anchors), len(board.models), sigma0).fit_lomo(O2, KA, use_length=use_length)


def half_split(board, master=HALF_MASTER, floor=0):
    """Per anchor, the JUDGED questions (sorted) permuted by the named stream 'half/<anchor>' of Streams(master); H1 is
    the first floor(n / 2), H2 the rest. Returns (H1, H2, the stream log). The selftest pins the split on its fixture by a
    golden sha256 (READY 5dfc825 D1)."""
    st = Streams(master + ("#MUTANT" if MUTANT == "half_seed" else ""))
    H1, H2 = set(), set()
    for anc in sorted(board.by):
        qs = sorted({r[2] for r in board.by[anc]})
        perm = st.np("half/%s" % anc).permutation(len(qs))
        h = len(qs) // 2
        H1 |= {qs[k] for k in perm[:h]}
        H2 |= {qs[k] for k in perm[h + (1 if MUTANT == "half_drop" else 0):]}
    if MUTANT == "half_same":
        H2 = set(H1)
    return H1, H2, st.log


def half_split_check(board, H1, H2):
    """(disjoint, complete, n_judged): the halves must be disjoint AND cover every judged question of every anchor."""
    judged = {r[2] for anc in board.by for r in board.by[anc]}
    return (not (H1 & H2)), (H1 | H2) == judged, len(judged)


def board_by_questions(board, qset, label):
    nb = data.Board.__new__(data.Board)
    nb.label = label; nb.models = list(board.models)
    nb.K, nb.P, nb.L = board.K, board.P, board.L
    nb.by = defaultdict(list); nb.votes = defaultdict(list); nb.n_valid = 0
    for anc in sorted(board.by):
        for r, v in zip(board.by[anc], board.votes[anc]):
            if r[2] in qset:
                nb.by[anc].append(r); nb.votes[anc].append(v); nb.n_valid += 1
    return nb


def edge_key_sets(edges, gap=GAP):
    return dict(f=sorted((e["anchor"], e["a"], e["b"]) for e in edges if e["gap"] >= gap),
                u=sorted((e["anchor"], e["a"], e["b"]) for e in edges),
                est=sorted((e["anchor"], e["a"], e["b"]) for e in edges if e["gap"] >= gap and e.get("est")))


def record_count_targets(board, sb, B=None, floor=200):
    """The 12 count targets of a board computed with the BUILDER OF RECORD: build()'s loop (data.edges_exact, rj.mm_fit,
    Random(42)) and the record's fit through the LOAO driver (g23.v1_readout). The builder is WITNESSED (the exact
    builder's board counter must move; a fast builder is REFUSED, READY 5dfc825 D1). Returns (targets, edge key sets)."""
    from . import g23
    before = data.WITNESS.get("edges_exact.boards", 0)
    if MUTANT == "h2_fast":
        edges, aq = data.edges_fast(board, sb.B if B is None else B, Streams("MUTANT-h2_fast"), "h2fast", floor=floor)
    else:
        edges, aq = data.edges_exact(board, B=sb.B if B is None else B, floor=floor)
    if data.WITNESS.get("edges_exact.boards", 0) - before <= 0:
        hit("VALIDITY_V2.H2_BUILDER_REFUSED")
        raise SystemExit("[G22 v2] the H2 targets must come from the builder of record (edges_exact: Random(42), rj.mm_fit);"
                         " no exact board was witnessed: refused")
    data.mark_established(edges, board.K, aq, sb)
    keys = edge_key_sets(edges)
    rd = g23.v1_readout(sb, edges, board.K, aq)
    out = {}
    for tag in ("f", "u"):
        for k in ("raw_called", "raw_wrong", "loao_called", "loao_wrong", "loao_wrong_est"):
            out["%s_%s" % (tag, k)] = int(rd[tag][k])
        out["%s_loao_nominal" % tag] = float(rd[tag]["loao_nominal"])
    return out, keys


def _heldout_rep(task):
    r = task
    C = _CTX
    before = _witness_snapshot()
    st = Streams(C["master"])
    vm = VerdictModel.from_params(C["vm"])
    u = vm.draw_u(st.np("validity-v2/heldout/rep%04d/u" % r), G=C["G"], M=C["M"])
    if MUTANT == "u_zero":
        u = np.zeros_like(u)
    sim = vm.simulate(C["S"], st.np("validity-v2/heldout/rep%04d/verdicts" % r), mode="random", u=u)
    b2 = with_verdicts(C["board"], C["meta"], sim)
    edges, _ = data.edges_fast(b2, C["B"], st, "validity-v2/heldout/rep%04d" % r, floor=C["floor"])
    m = cert_metrics(edges, C["est_keys"], min_est=C["min_est"])
    m["u_sd"] = float(np.std(u))
    return m, st.log, _witness_delta(before)


# ------------------------------------------------------------------ D5 (ruling on the degenerate corr): the diagnostics
V1_DEV_R2 = 0.933              # the v1 DEV reference R^2 of v_m on keyacc_m (arena rulings, DEV, NOT OF RECORD)


def model_keyacc_vector(KA, present=None):
    """The model-level centred keyacc_m from the (G, M) matrix (identical across anchors where every model is present)."""
    present = np.ones_like(KA, dtype=bool) if present is None else present
    return np.array([KA[present[:, m], m].mean() if present[:, m].any() else 0.0 for m in range(KA.shape[1])])


def fresh_draw_share(beta, k, sigma_eps):
    """beta^2 var(k) / (beta^2 var(k) + sigma_eps^2), var with ddof 0 (the D5 ruling)."""
    vk = float(np.var(np.asarray(k, dtype=float)))
    den = beta * beta * vk + sigma_eps * sigma_eps
    return float(beta * beta * vk / den) if den > 0 else float("nan")


def in_sample_share(beta, k, T):
    vt = float(np.var(np.asarray(T, dtype=float)))
    return float(np.var(beta * np.asarray(k, dtype=float)) / vt) if vt > 0 else float("nan")


def d5_lines(vm, KA, models, label, vm_h1=None):
    """The D5 diagnostics beside the v2 verdict, deciding nothing."""
    pres = vm.present if getattr(vm, "present", None) is not None and vm.present.any() else np.ones_like(KA, bool)
    k = model_keyacc_vector(KA, pres)
    ubar = np.array([vm.u[pres[:, m], m].mean() if pres[:, m].any() else 0.0 for m in range(vm.M)])
    T = vm.beta * k + ubar
    out = ["  D5 DIAGNOSTICS for %s (the D5 ruling; printed beside the verdict; NONE enters PASS / FAIL):" % label,
           "    quality-alignment shares over the %d models (model-level centred keyacc_m; T_m = beta-hat keyacc_m + mean_g"
           " u-hat_gm): IN-SAMPLE var(beta-hat keyacc) / var(T) = %.4f | FRESH-DRAW beta^2 var(k) / (beta^2 var(k) +"
           " sigma_eps_LOMO^2) = %.4f | beside: the v1 DEV reference R^2 %.3f (DEV, NOT OF RECORD) and the v1 random mode's"
           " share ~0 (v redrawn with no link to quality)"
           % (len(k), in_sample_share(vm.beta, k, T), fresh_draw_share(vm.beta, k, vm.sigma_eps_lomo), V1_DEV_R2)]
    lm = list(getattr(vm, "lomo_models", []))
    if lm and len(lm) == len(vm.lomo_errors):
        kk = k[lm]; ee = np.array(vm.lomo_errors)
        r = float(np.corrcoef(ee, kk)[0, 1]) if len(ee) > 2 and ee.std() > 0 and kk.std() > 0 else float("nan")
        order = np.argsort(kk)
        pick = list(order[:2]) + list(order[-2:])
        out.append("    LOMO prediction errors vs keyacc_m (DESCRIPTIVE, n = %d): Pearson %+.4f | two lowest-keyacc: %s | two"
                   " highest-keyacc: %s" % (len(ee), r,
                                            ", ".join("%s %+.4f" % (models[lm[i]], ee[i]) for i in pick[:2]),
                                            ", ".join("%s %+.4f" % (models[lm[i]], ee[i]) for i in pick[2:])))
    if vm_h1 is not None:
        out.append("    beta-hat on H1 %+.4f beside beta-hat on the full board %+.4f: stability across question halves, NOT"
                   " independent (H1 is a subset)" % (vm_h1.beta, vm.beta))
    return out


def validity_v2_leg(say, board, sb, streams, R=1000, B=300, family_alpha=0.05, floor=200, targets=None,
                    ddev_targets=DDEV_TARGETS, edge_targets=None, retest_target=RETEST_AGREEMENT_OF_RECORD, workers=1,
                    use_length=True, min_est=50, half_master=HALF_MASTER, h2_targets=None, h2_edge_targets=None,
                    record_B=None, store=None):
    """Ruling 1 (ii)-(v) of 83f431b, rulings A / B of 4b25059, the P7 record 97f3a1f: part A = the 14 full-board targets
    in the v2 fresh-judge mode (fixed and retest v2 printed, deciding nothing); part B = the held-out conjunct (fit on H1,
    simulate H2 with a FRESH judge, H2's 12 count targets from the WITNESSED builder of record). v2 PASSES iff BOTH parts
    pass. ONE SHOT: a FAIL is final. Returns (token, H2 records); the token carries T, level, T2, level2 and the timing."""
    import time as _t
    t_start = _t.time()
    say("", "=== (a') VALIDITY, FRESH-JUDGE v2: %s; rulings 83f431b (ruling 1), 4b25059 (rulings A, B), 97f3a1f (P7) ==="
        % POST_HOC,
        "  ONE SHOT (ruling 1 (v)): a v2 FAIL is FINAL for the simulator as a board-size instrument; a PASS re-admits the"
        " design readings ONLY as readings of a post-hoc-specified simulator.")
    tokA, _ = validity_leg(say, board, sb, streams, R=R, B=B, family_alpha=family_alpha, primary="random", floor=floor,
                           targets=targets, ddev_targets=ddev_targets, edge_targets=edge_targets,
                           retest_target=retest_target, workers=workers, use_length=use_length, min_est=min_est,
                           v2=True, tag="validity-v2", store=store)
    t_b0 = _t.time()
    H1, H2, hlog = half_split(board, half_master)
    streams.merge(hlog)
    b1 = board_by_questions(board, H1, board.label + "[H1]")
    b2 = board_by_questions(board, H2, board.label + "[H2]")
    disjoint, complete, n_judged = half_split_check(board, H1, H2)
    say("", "  (a'-B) HELD-OUT CONJUNCT [%s]: judged questions split in halves per anchor by the registered seed %r"
        " (stream 'half/<anchor>'): H1 %d, H2 %d of %d judged questions | disjoint %s | complete (H1 u H2 = judged) %s;"
        " fit on H1, simulate H2" % (POST_HOC, half_master, len(H1), len(H2), n_judged, "YES" if disjoint else "NO",
                                     "YES" if complete else "NO"))
    if not disjoint:
        hit("VALIDITY_V2.HALVES_OVERLAP")
        say("  the halves OVERLAP: the held-out conjunct is VOID -> part B FAILS")
    if not complete:
        hit("VALIDITY_V2.HALVES_INCOMPLETE")
        say("  the halves do NOT cover the judged set (a question dropped): the held-out conjunct is VOID -> part B FAILS")
    exact_before = data.WITNESS.get("edges_exact.boards", 0)
    computed = h2_targets is None
    if computed:
        h2_targets, h2_edge_targets = record_count_targets(b2, sb, B=record_B, floor=floor)
    exact_delta = data.WITNESS.get("edges_exact.boards", 0) - exact_before
    T2 = len(h2_targets)
    level2 = bonferroni_level(T2 + (1 if MUTANT == "t2_offbyone" else 0), family_alpha)
    say("  H2 targets (builder of record: build()'s loop + the record's fit through the LOAO driver; exact-builder witness"
        " %s): %s" % (("+%d boards" % exact_delta) if computed else "not computed here (targets given)",
                      ", ".join("%s %s" % (k, v) for k, v in h2_targets.items())),
        "  rule: every H2 target inside its central (1 - %.2f / T2) interval, T2 = %d -> %.5f, of the v2 fresh-judge mode"
        " fitted on H1" % (family_alpha, T2, level2))
    a1, S1, obs1, meta1 = board_matrix(b1, floor)
    KA1 = keyacc_matrix(b1, a1)
    vm1 = fit_verdict_model_v2(b1, a1, with_ka(S1, KA1), obs1, KA1, use_length)
    say(*vm1.lines(b1.models))
    a2, S2, obs2, meta2 = board_matrix(b2, floor)
    KA2 = keyacc_matrix(b2, a2)
    S2 = with_ka(S2, KA2)
    real2, aq2 = data.edges_fast(b2, B, streams, "validity-v2/heldout/real", floor=floor)
    data.mark_established(real2, b2.K, aq2, sb)
    est2 = {(e["anchor"], e["a"], e["b"]) for e in real2 if e["est"]}
    fast_keys = edge_key_sets(real2)
    # D12: the H2 edge IDENTITIES (not counts) of the fast builder against the builder of record
    edges_ok = h2_edge_targets is None or all(sorted(map(tuple, h2_edge_targets[k])) == fast_keys[k] for k in ("f", "u", "est"))
    ctx = dict(master=streams.master, vm=vm1.params(), S=S2, board=b2, meta=meta2, B=B, floor=floor, est_keys=est2,
               min_est=min_est, G=len(a2), M=len(b2.models))
    t_fixed_b = _t.time() - t_b0
    t_r0 = _t.time()
    recs = run_reps(_heldout_rep, ctx, list(range(R)), workers, streams)
    t_reps_b = _t.time() - t_r0
    store_put(store, "validity-v2.heldout", recs)            # G22-REBIND-1: additive, write-once, no random number
    u_sd = float(np.median([x["u_sd"] for x in recs])) if recs else 0.0
    fresh = u_sd > 0 or (vm1.sigma_eps_lomo == 0 and vm1.sigma_w == 0)
    say("    part B draws a FRESH judge per replicate: median SD of the drawn u %.4f (%s)"
        % (u_sd, "fresh" if fresh else "NOT FRESH: u = 0; part B is VOID"))
    if not fresh:
        hit("VALIDITY_V2.NOT_FRESH")
    okB = bool(disjoint and complete and edges_ok and fresh)
    say("    %-20s %9s %9s %9s %9s %10s  %s" % ("H2 statistic", "target", "q_lo", "median", "q_hi", "pct(target)", "covered"))
    for key, tv in h2_targets.items():
        v = np.array([x[key] for x in recs], dtype=float)
        cov, ql, qm, qh = covered(v, tv, level2)
        pct = float((v < tv).mean() + 0.5 * (v == tv).mean())
        okB &= bool(cov)
        say("    %-20s %9.2f %9.2f %9.2f %9.2f %10.3f  %s" % (key, tv, ql, qm, qh, pct, "yes" if cov else "NO"))
    say("    H2 edge IDENTITIES (fast builder vs builder of record; f / u / est key sets): %s"
        % ("MATCH" if edges_ok else "DIFFER" if h2_edge_targets is not None else "not compared (no record key sets)"))
    statusB = "PASS" if okB else "FAIL"
    status = "PASS" if (tokA["status"] == "PASS" and okB) else "FAIL"
    hit("VALIDITY_V2.%s" % status)
    say("", "  VALIDITY v2 [%s]: part A (14 full-board targets) %s; part B (held-out H2, %d targets) %s -> %s%s"
        % (POST_HOC, tokA["status"], T2, statusB, status,
           "" if status == "PASS" else ". ONE SHOT: THIS FAIL IS FINAL; THE SIMULATOR DECIDES NOTHING; the board size reverts"
           " to the memo's arithmetic plus a registered pilot"))
    from .verdict_model import diagnostics_line
    vmA = VerdictModel.from_params(tokA["verdict_model"])
    anchorsA = [a for a in sorted(board.by) if len(board.by[a]) >= floor]
    KAA = keyacc_matrix(board, anchorsA)
    vmA.present = np.array([[any(m in (r[0], r[1]) for r in board.by[a]) for m in board.models] for a in anchorsA])
    say("  beside the verdict, the full-board v2 model:", diagnostics_line(vmA),
        "  beside the verdict, the H1 v2 model:", diagnostics_line(vm1))
    say(*d5_lines(vmA, KAA, board.models, "the full-board v2 model", vm_h1=vm1))
    tok = dict(tokA)
    tA = tokA.get("timing", {})
    tok.update(status=status, mode=V2_MODE, label=POST_HOC, partA=tokA["status"], partB=statusB, h2_targets=h2_targets,
               half_master=half_master, h1=len(H1), h2=len(H2), T2=T2, level2=level2, h2_complete=complete,
               h2_exact_witness=exact_delta, h2_fresh_u_sd=u_sd,
               timing=dict(fixed_s=tA.get("fixed_s", 0.0) + t_fixed_b,
                           per_rep_s=(tA.get("reps_s", 0.0) / max(1, tA.get("rep_units", 1)) * 3 + t_reps_b / max(1, R)),
                           reps_units_A=tA.get("rep_units", 0), R=R, total_s=_t.time() - t_start))
    return tok, recs


# ------------------------------------------------------------------ the record token (READY 5dfc825 D2) and ONE SHOT (D3)
REC_MASTER_G22 = "ARCHV2-G22-REC-1"
INSTRUMENT_FILES = ("archv2_g22_sim.py", "archv2_arena/g22.py", "archv2_arena/verdict_model.py", "archv2_arena/data.py",
                    "archv2_arena/design.py", "archv2_arena/cert.py", "archv2_arena/bt.py", "archv2_arena/g23.py",
                    "archv2_arena/streams.py", "archv2_arena/ro.py", "archv2_arena/report.py")
ONE_SHOT_PATH = os.path.join(data.DATA_ROOT, "experiment_results", "archv2", "G22_validity_v2.ONE_SHOT.json")


def instrument_lf16():
    """sha256 (first 16 hex) over the LF renderings of the instrument's files, in a fixed order: the token is bound to
    the instrument that produced it."""
    import hashlib
    h = hashlib.sha256()
    for f in INSTRUMENT_FILES:
        h.update(f.encode("utf-8") + b"\0")
        h.update(open(os.path.join(data.HERE, f), "rb").read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def _token_digest(tok):
    import hashlib
    body = {k: v for k, v in tok.items() if k != "token_digest"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def seal_token(tok):
    """Bind the WHOLE token (status included) to its digest and to the instrument's lf16. Round-trip through JSON first
    so the digest is computed on exactly what load_token will read."""
    t = json.loads(json.dumps(tok, default=str))
    t["instrument_lf16"] = instrument_lf16()
    t["token_digest"] = _token_digest(t)
    return t


def one_shot_claim(out, master, path=None):
    """ONE SHOT, enforced (D3): a record v2 run first claims the fixed record path; if a claim (a launched record v2 run)
    already exists there, the run is REFUSED whatever --out says. The claim is written ONCE (mode 'x')."""
    path = path or ONE_SHOT_PATH
    if os.path.exists(path) and MUTANT != "one_shot_off":
        hit("ONE_SHOT.REFUSED")
        raise SystemExit("[G22 v2] ONE SHOT: a record fresh-judge v2 run has already been launched (%s); a second one is"
                         " refused whatever --out says (ruling 1 (v), 83f431b)" % path)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        report.write_once(path, json.dumps(dict(launched=__import__("time").strftime("%Y-%m-%d %H:%M:%S"), out=out,
                                                master=master, instrument_lf16=instrument_lf16()), indent=1))
    hit("ONE_SHOT.CLAIMED")
    return path


# ------------------------------------------------------------------ RB1 (delta READY d8a71ce): ruling 1 (iii) of 56751fa
# The token of record was minted by the frozen build (instrument_lf16 f37145df9516b7ec). The rebuilt instrument accepts
# THAT token, and only that token, iff (1) its token_digest is the registrar-pinned one, (2) its own instrument_lf16 is the
# frozen build's, and (3) the LIVE instrument_lf16 is named as its successor in a CHAIN FILE the registrar writes only
# AFTER the replay PASSES. The chain file lives OUTSIDE the 11 hashed files (a file cannot name its own hash); missing or
# malformed, the old token is REFUSED (fail-closed).
REBIND_PINNED_DIGEST = "3069666d0f5e553ad61bd9cb8f178e2771d6fd683f63f01b8b35435cf56cdfc0"
REBIND_OLD_LF16 = "f37145df9516b7ec"
CHAIN_PATH = os.path.join(data.DATA_ROOT, "experiment_configs", "g22_rebind_chain.json")
CHAIN_FIELDS = ("old_lf16", "new_lf16", "token_digest", "replay_output_sha", "registrar_commit")


def rebind_accepts(tok, live_lf16, chain_path=None):
    """(ok, reason). The fail-closed rebind rule of ruling 1 (iii)."""
    import re
    chain_path = chain_path or CHAIN_PATH
    if MUTANT != "chain_digest_unchecked" and tok.get("token_digest") != REBIND_PINNED_DIGEST:
        return False, "the token's token_digest %s is not the pinned %s" % (tok.get("token_digest"), REBIND_PINNED_DIGEST)
    if MUTANT != "chain_oldlf16_unchecked" and tok.get("instrument_lf16") != REBIND_OLD_LF16:
        return False, "the token's instrument_lf16 %s is not the frozen build's %s" % (tok.get("instrument_lf16"), REBIND_OLD_LF16)
    if not os.path.exists(chain_path):
        if MUTANT == "chain_missing_ok":
            return True, "chain missing (MUTANT)"
        return False, "no chain file at %s (the registrar writes it only after the replay PASSES)" % chain_path
    try:
        ch = json.load(open(chain_path, encoding="utf-8"))
    except Exception as ex:                                         # a malformed chain refuses
        return False, "the chain file is not valid JSON (%s)" % ex
    missing = [f for f in CHAIN_FIELDS if f not in ch]
    if missing:
        return False, "the chain file lacks %s" % ", ".join(missing)
    if ch["old_lf16"] != REBIND_OLD_LF16:
        return False, "the chain's old_lf16 %s is not %s" % (ch["old_lf16"], REBIND_OLD_LF16)
    if ch["token_digest"] != REBIND_PINNED_DIGEST:
        return False, "the chain's token_digest %s is not the pinned one" % ch["token_digest"]
    if MUTANT != "chain_successor_unchecked" and ch["new_lf16"] != live_lf16:
        return False, "the chain names the successor %s, not this instrument %s" % (ch["new_lf16"], live_lf16)
    if not re.fullmatch(r"[0-9a-f]{16}|[0-9a-f]{64}", str(ch["replay_output_sha"])):
        return False, "the chain's replay_output_sha is not a sha256 (16 or 64 hex)"
    if not re.fullmatch(r"[0-9a-f]{7,40}", str(ch["registrar_commit"])):
        return False, "the chain's registrar_commit is not a commit hash"
    return True, "chain %s: %s -> %s, replay %s, registrar %s" % (chain_path, ch["old_lf16"], ch["new_lf16"],
                                                                  ch["replay_output_sha"], ch["registrar_commit"])


def load_token(path, need_pass=True, need_v2=False, dev=False):
    if path is None or not os.path.exists(path):
        hit("TOKEN.REFUSED_MISSING")
        raise SystemExit("[G22] no validity token at %r: run the validity leg first; without a PASS the simulator"
                         " decides nothing" % path)
    tok = json.load(open(path, encoding="utf-8"))
    vm = VerdictModel.from_params(tok["verdict_model"])
    if vm.digest() != tok["vm_digest"]:
        hit("TOKEN.REFUSED_DIGEST")
        raise SystemExit("[G22] the token's verdict-model digest does not re-compute; refused")
    if need_pass and tok["status"] != "PASS":
        hit("TOKEN.REFUSED_FAIL")
        raise SystemExit("[G22] the validity leg FAILED (token %s): THE SIMULATOR DECIDES NOTHING; this leg refuses"
                         % path)
    if need_v2 and tok.get("mode") != V2_MODE:
        hit("TOKEN.REFUSED_NOT_V2")
        raise SystemExit("[G22] this leg runs ONLY IF the fresh-judge v2 validity PASSES (ruling 1, 83f431b; run order (3));"
                         " token %s is mode %r" % (path, tok.get("mode", "v1 (registered)")))
    if need_v2 and MUTANT != "gate_presence_only":
        # READY 5dfc825 D2: the WHOLE token is sealed and bound to this instrument
        if tok.get("token_digest") != _token_digest(tok):
            hit("TOKEN.REFUSED_SEAL")
            raise SystemExit("[G22] the token's whole-token digest does not re-compute (status or any field altered); refused")
        live = instrument_lf16()
        if tok.get("instrument_lf16") != live:
            ok_rb, why = rebind_accepts(tok, live)
            if not ok_rb:
                hit("TOKEN.REFUSED_INSTRUMENT")
                raise SystemExit("[G22] the token was produced by another instrument (lf16 %s, this one %s) and the rebind"
                                 " chain does not admit it (%s); refused" % (tok.get("instrument_lf16"), live, why))
            hit("TOKEN.REBIND_ADMITTED")
            print("[G22] the token of record admitted through the rebind chain (ruling 1 (iii), 56751fa): %s" % why)
        if not dev:
            probs = []
            if tok.get("record") is not True:
                probs.append("not a record token (a --dev run never produces one)")
            if tok.get("master") != REC_MASTER_G22:
                probs.append("master %r is not %s" % (tok.get("master"), REC_MASTER_G22))
            if tok.get("R") != 1000 and not tok.get("r_registration"):
                probs.append("R %r is not the registered 1,000 (and no registered smaller R is named)" % tok.get("R"))
            if tok.get("label") != POST_HOC:
                probs.append("label is not the POST-HOC-SPECIFIED label")
            if tok.get("partA") != "PASS" or tok.get("partB") != "PASS":
                probs.append("part A %r / part B %r (both must PASS)" % (tok.get("partA"), tok.get("partB")))
            if tok.get("T") != 14 or tok.get("T2") != 12:
                probs.append("T %r / T2 %r (registered 14 / 12)" % (tok.get("T"), tok.get("T2")))
            if probs:
                hit("TOKEN.REFUSED_NOT_RECORD")
                raise SystemExit("[G22] token %s is not a record fresh-judge v2 PASS: %s; refused" % (path, "; ".join(probs)))
            hit("TOKEN.RECORD_ADMITTED")
        else:
            hit("TOKEN.DEV_ADMITTED")
    return tok, vm


# ============================================================================================ (b) nu(k, N)
def _nominal_frozen(edges, pair):
    fr = design.frontier_mask(edges)
    E = cert.EdgeArrays([e for e, f in zip(edges, fr) if not f])
    if len(E) == 0:
        return 0.0, 0, 0
    c = cert.cbud_v(E, *pair)
    called = c >= cert.THRESH
    return float((1 - c[called]).sum()), int(called.sum()), len(E)


def nu_leg(say, board, streams, pair, ks, Ns, reps=20, B=300, floor=0, boot=2000, pair_label=""):
    say("", "=== (b) NOMINAL-VS-ROSTER SCALING nu(k, N) by SUBSAMPLING %s (%d models) ===" % (board.label, len(board.models)),
        "  nominal = sum(1 - c~) over called non-frontier edges under the FROZEN pair %s (b0 %+.4f, b1 %+.4f): key-blind,"
        " no refit, no decline; nu = nominal per anchor with edges; per-anchor floor %d rows (the record's build() uses"
        " 200; thinned boards fall below it); %d subsamples per (k, N); B %d" % (pair_label, pair[0], pair[1], floor, reps, B))
    table = {}
    for N in Ns:
        for k in ks:
            if k > len(board.models):
                continue
            vals = []
            for r in range(reps):
                rng = streams.py("nu/N%s/k%02d/rep%03d/roster" % (N, k, r))
                models = sorted(rng.sample(board.models, k))
                sub = board.restrict(models, None if N == "full" else int(N), rng, label="%s k%d N%s" % (board.label, k, N))
                edges, aq = data.edges_fast(sub, B, streams, "nu/N%s/k%02d/rep%03d" % (N, k, r), floor=floor)
                nom, called, n_e = _nominal_frozen(edges, pair)
                n_anc = len({e["anchor"] for e in edges})
                vals.append((nom / n_anc if n_anc else float("nan"), nom, called, n_e, n_anc))
            table[(N, k)] = vals
            v = np.array([x[0] for x in vals])
            ql, qm, qh = quantiles(v)
            say("  N %-4s k %2d: nu median %.4f [%.4f, %.4f] | nominal median %.3f | called median %.0f of %.0f edges | anchors %.0f | zero-nominal draws %d"
                % (N, k, qm, ql, qh, float(np.median([x[1] for x in vals])), float(np.median([x[2] for x in vals])),
                   float(np.median([x[3] for x in vals])), float(np.median([x[4] for x in vals])), int((v == 0).sum())))
    fits = {}
    for N in Ns:
        kk = [k for k in ks if (N, k) in table]
        if len(kk) < 2:
            continue
        rng = streams.np("nu/N%s/beta-boot" % N)

        def beta_of(sample):
            x, y = [], []
            for k, vals in sample.items():
                for v in vals:
                    if v > 0 and np.isfinite(v):
                        x.append(math.log(k)); y.append(math.log(v))
            if len(set(x)) < 2:
                return float("nan")
            return float(np.polyfit(x, y, 1)[0])

        base = {k: [x[0] for x in table[(N, k)]] for k in kk}
        b_hat = beta_of(base)
        bs = []
        for _ in range(boot):
            bs.append(beta_of({k: list(rng.choice(base[k], size=len(base[k]), replace=True)) for k in kk}))
        bs = np.array([b for b in bs if np.isfinite(b)])
        lo, hi = (float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))) if bs.size else (float("nan"),) * 2
        fits[N] = (b_hat, lo, hi)
        say("  N %-4s: exponent beta (log nu = a + beta log k, zero-nominal draws excluded) %+.3f, bootstrap 95%% CI"
            " [%+.3f, %+.3f] over %d resamples of the subsamples within each k" % (N, b_hat, lo, hi, bs.size))
        say("          readings (memo section 1): P beta ~ 1.06 %s | M / X (nominal per edge constant) beta ~ 2 %s"
            % ("INSIDE the CI" if lo <= 1.06 <= hi else "outside the CI", "INSIDE the CI" if lo <= 2.0 <= hi else "outside the CI"))
        say("          CI resamples: 2,000 (correction 3, 83f431b: the registered 'B 300' is the per-subsample edge"
            " bootstrap)",
            "          the memo's '>= 0.9' reading, AS WRITTEN (VACUOUS per correction 3): CI lower end %.3f %s 0.9"
            % (lo, ">=" if lo >= 0.9 else "<"),
            "          the reach-to-P reading, POST-DATA (declared after the data, correction 3): the CI %s reading P's"
            " 1.06 (lower end %.3f, upper end %.3f)" % ("REACHES DOWN TO" if lo <= 1.06 else "does NOT reach down to", lo, hi))
        hit("NU.READINGS")
    hit("NU.DONE")
    return table, fits


# ============================================================================== (c) (d) (g) designs
def resolve_designs(names, rosters, supply, strata_pool, streams, spec=None):
    spec = spec or design.MEMO_DESIGNS
    out = {}
    for name in names:
        if name not in spec:
            raise SystemExit("[G22] unknown design %r (known: %s)" % (name, ", ".join(sorted(spec))))
        parts = []
        for pi, p in enumerate(spec[name]):
            corpus = p["corpus"]
            if p["roster"] not in rosters:
                raise SystemExit("[G22] design %s needs roster %r, not loaded" % (name, p["roster"]))
            sup = supply[corpus]
            if isinstance(p["strata"], str):
                pref = tuple(p["strata"].split("|"))
                strata = sorted(s for s in sup if s.split("/")[0].upper() in pref)
            else:
                strata = design.choose_strata(sup, p["strata"], streams.np("designs/%s/part%d/strata" % (name, pi)))
            parts.append(dict(p, models=rosters[p["roster"]], strata=strata,
                              supply={s: sup[s] for s in strata}, pool={s: strata_pool[corpus][s] for s in strata}))
        out[name] = parts
    return out


def holm_flags(edges, alpha=0.05):
    """Holm-established per anchor on the edges' exact McNemar p (mark_established sets mc_p)."""
    by = defaultdict(list)
    for k, e in enumerate(edges):
        by[e["anchor"]].append(k)
    out = [False] * len(edges)
    for anc, ks in by.items():
        rej = cert.holm([edges[k]["mc_p"] for k in ks], alpha)
        for k, r in zip(ks, rej):
            out[k] = bool(r)
    if MUTANT == "holm_off":
        out = [bool(e.get("est")) for e in edges]
    return out


def _design_part_metrics(edges, board, aq, sb, pair, deff, min_est=50):
    data.mark_established(edges, board.K, aq, sb)
    fr = design.frontier_mask(edges) if edges else np.zeros(0, bool)
    kept = [e for e, f in zip(edges, fr) if not f]
    E = cert.EdgeArrays(kept) if kept else None
    res = dict(edges=len(edges), frontier=int(fr.sum()), kept=len(kept))
    if E is None or len(E) < 3:
        res.update(nom_frozen=0.0, nom_loao=0.0, nom_decl=0.0, w_frozen=0, w_loao=0, w_loao_est=0, w_decl=0,
                   called_frozen=0, called_loao=0, identified=False, ddev=float("nan"), unident="no edges", deff=[],
                   est=0, est_holm=0, identified_holm=False, ddev_holm=float("nan"))
        return res
    c = cert.cbud_v(E, *pair); cf = c >= cert.THRESH
    L = cert.loao_v(E)
    decl = L["called"] & E.est
    est = E.subset(E.est)
    reason = cert.unidentified(est) if len(est) else "no established edges"
    if reason is None and len(est) >= min_est:
        _, dd, _ = cert.ddev_v(est, x0=(L["b0"], L["b1"]))
    else:
        dd = float("nan")
    # (d) under HOLM-established labels beside the unadjusted ones (83f431b notes; the UNADJUSTED decides)
    est_h = holm_flags(kept)
    Eh = cert.EdgeArrays([dict(e, est=h) for e, h in zip(kept, est_h)])
    esth = Eh.subset(Eh.est)
    reason_h = cert.unidentified(esth) if len(esth) else "no established edges"
    if reason_h is None and len(esth) >= min_est:
        _, dd_h, _ = cert.ddev_v(esth, x0=(L["b0"], L["b1"]))
    else:
        dd_h = float("nan")
    res.update(est_holm=int(sum(est_h)), identified_holm=bool(reason_h is None and np.isfinite(dd_h) and dd_h >= cert.CHI2_1_95),
               ddev_holm=dd_h)
    res.update(nom_frozen=float((1 - c[cf]).sum()), called_frozen=int(cf.sum()), w_frozen=int((cf & ~E.right).sum()),
               w_frozen_est=int((cf & ~E.right & E.est).sum()),
               nom_loao=L["nominal"], called_loao=L["n_called"], w_loao=L["wrong"], w_loao_est=L["wrong_est"],
               nom_decl=float((1 - L["oof"][decl]).sum()), called_decl=int(decl.sum()), w_decl=int((decl & ~E.right).sum()),
               est=int(E.est.sum()), identified=bool(reason is None and np.isfinite(dd) and dd >= cert.CHI2_1_95),
               ddev=dd, unident=reason, b1=L["b1"],
               deff=[(e["s"] / e["s_iid"]) ** 2 for e in kept if deff and e.get("s_iid", 0) > 0])
    return res


def _design_rep(task):
    name, r = task
    C = _CTX
    before = _witness_snapshot()
    st = Streams(C["master"])
    vm = VerdictModel.from_params(C["vm"])
    sb = data.import_sb()
    parts = C["designs"][name]
    recs = []
    for pi, p in enumerate(parts):
        tag = "designs/%s/rep%04d/part%d" % (name, r, pi)
        rq = st.np(tag + "/evalq")
        strata_qs = {}
        for s in p["strata"]:
            pool = p["pool"][s]
            n = min(p["supply"][s], len(pool))
            strata_qs[s] = sorted(int(x) for x in rq.choice(pool, size=n, replace=False))
        u = vm.draw_u(st.np(tag + "/u"), G=len(p["strata"]), M=len(p["models"]))
        board, stats = design.simulate_part(p, C["keytabs"][p["corpus"]], strata_qs, vm, st.np(tag + "/schedule"),
                                            st.np(tag + "/verdicts"), u, "%s rep %d part %d" % (name, r, pi))
        edges, aq = data.edges_fast(board, C["B"], st, tag, floor=C["floor"], deff=(r < C["deff_reps"]))
        m = _design_part_metrics(edges, board, aq, sb, C["pair"], r < C["deff_reps"], C["min_est"])
        m.update(stats)
        recs.append(m)
    return recs, st.log, _witness_delta(before)


def designs_leg(say, token, vm, designs, keytabs, streams, R=200, B=300, floor=200, deff_reps=20, workers=1,
                pair=cert.FROZEN_GROK_UNFILTERED, primary="nom_loao", bar=9.0, ident_bar=0.8, p_bar=0.8, min_est=50,
                store=None):
    say("", "=== (c) P(nominal >= %g), (d) b1 identification under the filter, (g) DEFF: simulated designs ===" % bar,
        "  verdict model: the validity token's (status %s, digest %s), RANDOM mode (a new judge instance per replicate);"
        " R %d replicates per design; B %d; floor %d; frozen key-blind pair (%+.4f, %+.4f); primary nominal %s"
        % (token["status"], token["vm_digest"][:16], R, B, floor, pair[0], pair[1], primary))
    if isinstance(vm, VerdictModelV2):
        say("  %s: every design reading below is a reading of a POST-HOC-SPECIFIED simulator (ruling 1 (v), 83f431b);"
            " keyacc under convention A over each design's EVAL supply" % POST_HOC)
    say("  the validity token of record: %s | token_digest (in full) %s" % (PASS_CHIP, token.get("token_digest", "(none)")),
        ADMISSIBLE_AS)
    ctx = dict(master=streams.master, vm=vm.params(), designs=designs, keytabs=keytabs, B=B, floor=floor,
               deff_reps=deff_reps, pair=pair, min_est=min_est)
    summary = {}
    for name, parts in designs.items():
        for pi, p in enumerate(parts):
            say("  %s part %d: %s roster %d models (%s), %d strata, N %d; supply %d EVAL questions (%s)"
                % (name, pi, p["corpus"], len(p["models"]), p["roster"], len(p["strata"]), p["N"],
                   sum(p["supply"].values()), ", ".join("%s %d" % (s, p["supply"][s]) for s in p["strata"][:8])
                   + (" ..." if len(p["strata"]) > 8 else "")))
            if p["corpus"] == "union":
                hit("DESIGNS.HYPOTHETICAL")
                say("    %s part %d is TRACE-LESS / HYPOTHETICAL (ruling 2, 83f431b): the union rows carry no generated text"
                    " (log-likelihood tasks); read as 'if traces were generated'; it CANNOT BE CHOSEN without a new"
                    " registration that prices generation; BBH and MuSR extracted answers are MISSING" % (name, pi))
        recs = run_reps(_design_rep, ctx, [(name, r) for r in range(R)], workers, streams)
        sp = store_put(store, "designs.%s" % name, recs)       # G22-REBIND-1: additive, write-once, no random number
        tot = lambda key: np.array([sum(pp.get(key, 0) for pp in rr) for rr in recs], dtype=float)
        noms = {k: tot(k) for k in ("nom_frozen", "nom_loao", "nom_decl")}
        matches = tot("matches")
        say("  %s: matches per replicate median %.0f (%.0f calls, dual order) | reuse per question median %s | exhausted pairs median %.0f"
            % (name, float(np.median(matches)), 2 * float(np.median(matches)),
               " / ".join("%.2f" % float(np.median([rr[pi]["reuse"] for rr in recs])) for pi in range(len(parts))),
               float(np.median(tot("exhausted_pairs")))))
        if name == "D0":
            say("    D0 matches median %.0f BESIDE the memo's 79,600 and the cap 79,560 (52 strata x 153 pairs x N 10)"
                % float(np.median(matches)))
        for k, v in noms.items():
            n9 = int((v >= bar).sum())
            word, lo, hi = decide_rate(n9, len(v), p_bar, "high")
            ql, qm, qh = quantiles(v)
            say("    %-10s nominal median %.2f [%.2f, %.2f] | P(nominal >= %g) = %d / %d = %.3f, Wilson [%.3f, %.3f];"
                " vs %.2f (%s): %s%s%s"
                % (k, qm, ql, qh, bar, n9, len(v), n9 / len(v), lo, hi, p_bar, REGISTERED, word,
                   " (optimistic by construction, ruling 2 (ii))" if word == "MEETS" else "",
                   "   <- PRIMARY" if k == primary else ""))
        if MUTANT != "bias_line_missing":
            say(BIAS_LINE)
        if sp is not None:
            srecs = read_records(sp)
            snoms = {k: [sum(pp.get(k, 0) for pp in rr) for rr in srecs] for k in noms}
            say(*deflated_lines(snoms, primary, bar, "computed from the stored replicates %s" % os.path.basename(sp)))
        else:
            say(*deflated_lines(noms, primary, bar, "computed from the in-memory replicates: no store in this run"))
        say("    BOTH COUNTS (LOAO-called, per replicate median): all-label wrong %.1f | wrong(established) %.1f"
            % (float(np.median(tot("w_loao"))), float(np.median(tot("w_loao_est")))))
        pmx = design.MEMO_NOMINAL_PMX.get(name)
        if pmx:
            say("    memo (arith.) nominal under P / M / X: %.1f / %.1f / %.1f" % pmx)
        # status words under the primary nominal with both counts
        from calibration_status import status_word
        wl = tot("w_loao"); wle = tot("w_loao_est")
        words = Counter(status_word(n, int(w)).split(" (")[0] for n, w in zip(noms["nom_loao"], wl))
        words_e = Counter(status_word(n, int(w)).split(" (")[0] for n, w in zip(noms["nom_loao"], wle))
        say("    status word (LOAO nominal) with the ALL-label count: %s | with wrong(established): %s"
            % (dict(words), dict(words_e)),
            "    BOTH COUNTS PRINTED; NEITHER DECIDES the status word (d6129cf ruling (3): author decision 8, which count"
            " feeds status_word, is open)")
        for pi in range(len(parts)):
            idf = [rr[pi]["identified"] for rr in recs]
            k_id = int(sum(idf))
            word, lo, hi = decide_rate(k_id, len(idf), ident_bar, "high")
            reasons = Counter(rr[pi]["unident"] for rr in recs if rr[pi]["unident"])
            dd = [rr[pi]["ddev"] for rr in recs]
            ql, qm, qh = quantiles(dd)
            hit("IDENT.%s" % word.split()[0])
            say("    (d) part %d: b1 identified (established labels, delta-deviance >= 3.84, not separated) in %d / %d ="
                " %.3f, Wilson [%.3f, %.3f] against the %.2f bar (%s): %s | ddev median %.2f [%.2f, %.2f] | unidentified"
                " reasons %s" % (pi, k_id, len(idf), k_id / len(idf), lo, hi, ident_bar, REGISTERED, word, qm, ql, qh,
                                 dict(reasons) if reasons else "none"))
            if word == "BELOW":
                say("    (d) part %d is BELOW the bar: the fallback, named in advance, is %s" % (pi, FALLBACK_D))
            idh = [rr[pi].get("identified_holm", False) for rr in recs]
            wh, loh, hih = decide_rate(int(sum(idh)), len(idh), ident_bar, "high")
            say("    (d) part %d under HOLM-established labels (beside; the UNADJUSTED labels above DECIDE): identified in"
                " %d / %d = %.3f, Wilson [%.3f, %.3f]: %s | established per replicate median: unadjusted %.0f, Holm %.0f"
                % (pi, int(sum(idh)), len(idh), sum(idh) / len(idh), loh, hih, wh,
                   float(np.median([rr[pi].get("est", 0) for rr in recs])),
                   float(np.median([rr[pi].get("est_holm", 0) for rr in recs]))))
            hit("DESIGNS.HOLM_PRINTED")
            dfs = [x for rr in recs for x in rr[pi]["deff"]]
            if dfs:
                ql, qm, qh = quantiles(dfs, (0.25, 0.5, 0.75))
                say("    (g) part %d: DEFF = (clustered s / match-level s)^2 over %d edges of %d replicates: median %.3f"
                    " (IQR %.3f-%.3f) at reuse median %.2f; memo arith. at reuse 8.4: 1.63; G24's bar 1.6 was set for r <= 4;"
                    " this DEFF is %s" % (pi, len(dfs), min(deff_reps, R), qm, ql, qh,
                                          float(np.median([rr[pi]["reuse"] for rr in recs])), DEFF_LOWER_BOUND))
        summary[name] = dict(noms={k: v.tolist() for k, v in noms.items()}, matches=matches.tolist(), recs=recs)
    hit("DESIGNS.DONE")
    return summary


# ============================================================================================ (e) the stop
def _calibrated(E, pair, rng):
    tau = np.exp(pair[0] + pair[1] * E.agree)
    pw = cert.norm.cdf(-np.abs(E.m) / np.sqrt(E.s ** 2 + tau ** 2))
    wrong = rng.random(len(E)) < pw
    edges = [dict(e, right=not w) for e, w in zip(E.edges, wrong)]
    return cert.EdgeArrays(edges, E.anchor_names)


def _stop_rep(task):
    name, r = task
    C = _CTX
    before = _witness_snapshot()
    st = Streams(C["master"])
    vm = VerdictModel.from_params(C["vm"])
    sb = data.import_sb()
    p = C["part"]
    tag = "stop/rep%04d" % r
    rq = st.np(tag + "/evalq")
    strata_qs = {s: sorted(int(x) for x in rq.choice(p["pool"][s], size=min(p["supply"][s], len(p["pool"][s])), replace=False))
                 for s in p["strata"]}
    u = vm.draw_u(st.np(tag + "/u"), G=len(p["strata"]), M=len(p["models"]))
    board, stats = design.simulate_part(p, C["keytab"], strata_qs, vm, st.np(tag + "/schedule"), st.np(tag + "/verdicts"),
                                        u, "stop rep %d" % r)
    edges, aq = data.edges_fast(board, C["B"], st, tag, floor=C["floor"])
    data.mark_established(edges, board.K, aq, sb)
    fr = design.frontier_mask(edges)
    kept = [e for e, f in zip(edges, fr) if not f]
    E = cert.EdgeArrays(kept)
    s1 = np.array([e["anchor"] in C["stage1"] for e in kept])
    E1 = E.subset(s1)
    pair = C["pair"]
    c1 = cert.cbud_v(E1, *pair)
    frozen1 = float((1 - c1[c1 >= cert.THRESH]).sum())
    projected = frozen1 * len(p["strata"]) / max(1, len(C["stage1"]))
    Ecal = _calibrated(E, pair, st.np(tag + "/calibrated-labels"))
    from calibration_status import status_word
    out = dict(frozen1=frozen1, projected=projected, reads={})
    for margin in C["margins"]:
        if frozen1 >= C["bar"] + margin:
            read = "stage1"; sel = s1
        elif projected >= C["stage2_bar"]:
            read = "full"; sel = np.ones(len(E), bool)
        else:
            out["reads"][margin] = ("none", None, None, None, None)
            continue
        res = {}
        for world, EE in (("calibrated", Ecal), ("key", E)):
            sub = EE.subset(sel)
            L = cert.loao_v(sub)
            res[world] = (L["nominal"], L["wrong"], status_word(L["nominal"], L["wrong"]))
        out["reads"][margin] = (read, res["calibrated"][0], res["calibrated"][2], res["key"][0], res["key"][2])
    Lk = cert.loao_v(E)
    cf = cert.cbud_v(E, *pair)
    out["map"] = (float((1 - cf[cf >= cert.THRESH]).sum()), Lk["nominal"])
    return out, st.log, _witness_delta(before)


def stop_leg(say, token, vm, part, keytab, streams, R=200, B=300, floor=200, margins=(0.0, 1.0, 2.0, 3.0), bar=9.0,
             stage2_bar=4.5, stage1_n=7, workers=1, pair=cert.FROZEN_GROK_UNFILTERED, alpha_bar=0.05, store=None):
    stage1 = design.choose_strata(part["supply"], stage1_n, streams.np("stop/stage1-strata"))
    say("", "=== (e) THE KEY-BLIND STOP: P(MISCALIBRATED | calibrated simulated judge) ===",
        "  design: %d models x %d strata x N %d; stage 1 = %d strata drawn stratified by size (%s); key-blind statistic ="
        " frozen-pair nominal (%+.4f, %+.4f) on stage 1; rule (memo section 4): frozen >= %.0f + margin -> stop and read on"
        " stage 1; else projected (x %d/%d) >= %.1f -> stage 2 and read on all; else no status (rate UB only)"
        % (len(part["models"]), len(part["strata"]), part["N"], len(stage1), ", ".join(stage1), pair[0], pair[1], bar,
           len(part["strata"]), len(stage1), stage2_bar),
        "  COUNT: the ALL-LABEL count (a builder limit of record, d6129cf); it reads under ruling (3)'s caveat.",
        "  CALIBRATED WORLD: every edge's wrong label ~ Bernoulli(Phi(-|m| / sqrt(s^2 + tau(A)^2))) under the frozen pair"
        " (the widener is TRUE); the read refits the widener LOAO on those labels and applies"
        " calibration_status.status_word(LOAO nominal, all-label wrong among called). The KEY WORLD (the simulated"
        " judge's own labels) is printed beside, deciding nothing.",
        "  the validity token of record: %s | token_digest (in full) %s" % (PASS_CHIP, token.get("token_digest", "(none)")),
        ADMISSIBLE_AS)
    if MUTANT != "bias_line_missing":
        say(BIAS_LINE)
    ctx = dict(master=streams.master, vm=vm.params(), part=part, keytab=keytab, B=B, floor=floor, stage1=set(stage1),
               margins=list(margins), bar=bar, stage2_bar=stage2_bar, pair=pair)
    recs = run_reps(_stop_rep, ctx, [("stop", r) for r in range(R)], workers, streams)
    store_put(store, "stop", recs)                            # G22-REBIND-1: additive, write-once, no random number
    res = {}
    for margin in margins:
        reads = [rr["reads"][margin] for rr in recs]
        n_read = sum(1 for x in reads if x[0] != "none")
        mis = sum(1 for x in reads if x[0] != "none" and x[2].startswith("MISCALIBRATED"))
        word, lo, hi = decide_rate(mis, R, alpha_bar, "low")
        hit("STOP.%s" % word.split()[0])
        kw = Counter(x[4].split(" (")[0] for x in reads if x[0] != "none")
        say("  margin %.1f: read at stage 1 %d, at full %d, no status %d | P(MISCALIBRATED | calibrated) = %d / %d = %.3f,"
            " Wilson [%.3f, %.3f] vs %.2f (%s): %s | key world words %s"
            % (margin, sum(1 for x in reads if x[0] == "stage1"), sum(1 for x in reads if x[0] == "full"), R - n_read,
               mis, R, mis / R, lo, hi, alpha_bar, REGISTERED, word, dict(kw)))
        res[margin] = (mis, R, lo, hi, word)
    mp = np.array([rr["map"] for rr in recs])
    ok = mp[:, 0] > 0
    ratio = mp[ok, 1] / mp[ok, 0]
    ql, qm, qh = quantiles(ratio)
    slope = float(np.polyfit(mp[:, 0], mp[:, 1], 1)[0]) if len(set(mp[:, 0].tolist())) > 1 else float("nan")
    say("  map frozen-pair nominal -> LOAO-refit nominal (key world, all %d strata): ratio median %.3f [%.3f, %.3f];"
        " least-squares slope %.3f" % (len(part["strata"]), qm, ql, qh, slope))
    hit("STOP.DONE")
    return res, recs

# =====================================================================================================================
# G22-REBIND-1 (56751fa, docs/judge_v2_program.md L15667-L15686): ADDITIVE per-replicate storage, the REPLAY mode of
# validity-v2, and the print lines of ruling 2. ADDITIVE ONLY: the storage consumes NO random number, changes no
# computation, stream name or seed, and adds NOTHING to the output text (its sha256 lines go to the console and to the
# write-once manifest beside the output). With store=None every leg is exactly the frozen build's (lf16 f37145df9516b7ec).
# =====================================================================================================================
BIAS_LINE = ("  BIAS (ruling 2 (iii), 56751fa): the simulator over-calls wrong: raw-wrong medians 13 / 18 vs 7 / 8 (full board),"
             " 11 / 13 vs 3 / 3 (H2); LOAO called 7-15% low; LOAO nominal 6-18% high; the PRIMARY here is the LOAO nominal,"
             " so P(nominal >= 9) and the (d) identification rate (more wrong events) are OPTIMISTIC; the direction for the"
             " stop leg is NOT DETERMINED")
PASS_CHIP = "PASS AT THE BOUNDARY (D9 realised on H2 u_raw_wrong)"
ADMISSIBLE_AS = ("  READINGS ADMISSIBLE ONLY AS (ruling 2 (i)): readings of a post-hoc-specified simulator that passed at the"
                 " boundary and is NOT CENTRED on the record, validated on grok_calib's 12-model, 14-anchor board only,"
                 " EXTRAPOLATED to the 46-model roster and to a proportionally ALLOCATED EVAL supply (the DEV manifest; the"
                 " real split is not drawn); a MEETS read on P(nominal >= 9) is 'optimistic by construction'")
DEFF_LOWER_BOUND = ("a LOWER BOUND: the simulated judge has no question-level effect beyond the key, the answers and the"
                    " length (ruling 2 (iii))")
DEFLATE_FACTORS = (1.06, 1.18)
DECLARED_DEVIATION = ("NOT RUN (declared deviation, ruling 2 (iv)): trace-less and hypothetical, outside the simulator's"
                      " validity domain; P3's prediction recorded NOT SCORED; run only on the author's request")
REPLAY_BLOCK_START = "=== (a') VALIDITY, FRESH-JUDGE v2"
REPLAY_BLOCK_STOPS = ("  token sealed:", "  EXECUTION WITNESS", "  REPLAY ", "  DB OPENS", "  RANDOM STREAMS")
STREAMS_OF_RECORD_PREFIX = "0791961e"            # the recorded v2 run's streams-log sha (ruling 1 (ii)(b), 56751fa)


class RecordStore:
    """Write-once per-replicate record files beside the output (never a DB): '<prefix>.<name>.records.jsonl', one JSON
    object per replicate (sort_keys), sha256 printed on the console and listed in '<prefix>.records.manifest.txt'."""

    def __init__(self, prefix):
        self.prefix = prefix
        self.files = []

    def put(self, name, recs):
        if MUTANT == "store_draws_random":
            np.random.random(); random.random()
        path = "%s.%s.records.jsonl" % (self.prefix, name.replace("/", "_"))
        txt = "".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in recs)
        report.write_once(path, txt)
        sha = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        self.files.append((name, path, len(recs), sha))
        data.WITNESS["records.stored"] += len(recs)
        print("[RECORDS] %s: %d records -> %s | sha256 %s" % (name, len(recs), path, sha), flush=True)
        return path

    def path_of(self, name):
        for n, p, k, s in self.files:
            if n == name:
                return p
        return None

    def write_manifest(self):
        if not self.files:
            return None
        txt = "".join("%s\t%s\t%d\t%s\n" % (n, os.path.basename(p), k, s) for n, p, k, s in self.files)
        path = self.prefix + ".records.manifest.txt"
        report.write_once(path, txt)
        print("[RECORDS] manifest %s | sha256 %s" % (path, hashlib.sha256(txt.encode("utf-8")).hexdigest()), flush=True)
        return path


def store_put(store, name, recs):
    return store.put(name, recs) if store is not None else None


def read_records(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def declared_deviation(names, author_flag, say):
    """Ruling 2 (iv): D0 and D2 print NOT RUN and are refused unless the author's flag is given."""
    kept = []
    for n in names:
        if n in ("D0", "D2") and not author_flag:
            hit("DESIGNS.DECLARED_DEVIATION")
            say("  %s: %s" % (n, DECLARED_DEVIATION))
        else:
            kept.append(n)
    if not kept:
        raise SystemExit("[G22] only D0 / D2 were asked: %s; refused (--author-d0d2 runs them on the author's request)"
                         % DECLARED_DEVIATION)
    return kept


def deflated_lines(noms, primary, bar, store_note):
    out = []
    v = np.asarray(noms[primary], dtype=float)
    for f in DEFLATE_FACTORS:
        k = int((v >= bar * f).sum())
        lo, hi = cert.wilson(k, len(v))
        out.append("    DEFLATED SENSITIVITY (ruling 2 (iii); deciding nothing; NOT a correction): P(%s >= %g x %.2f = %.2f) ="
                   " %d / %d = %.3f, Wilson [%.3f, %.3f] (%s)" % (primary, bar, f, bar * f, k, len(v), k / max(1, len(v)),
                                                                  lo, hi, store_note))
    return out


def extract_replay_block(text):
    lines = text.replace("\r\n", "\n").split("\n")
    try:
        i = next(k for k, s in enumerate(lines) if s.startswith(REPLAY_BLOCK_START))
    except StopIteration:
        return ""
    j = next((k for k in range(i, len(lines)) if lines[k].startswith(REPLAY_BLOCK_STOPS)), len(lines))
    return "\n".join(lines[i:j]).rstrip("\n") + "\n"


def parse_streams_line(text):
    import re
    m = re.search(r"RANDOM STREAMS \(master '([^']*)'\): (\d+) named streams, log sha256 ([0-9a-f]{64})", text)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (None, None, None)


def _table_line(key, v, tv, level):
    cov, ql, qm, qh = covered(v, tv, level)
    pct = float((v < tv).mean() + 0.5 * (v == tv).mean())
    return "    %-20s %9.2f %9.2f %9.2f %9.2f %10.3f  %s" % (key, tv, ql, qm, qh, pct, "yes" if cov else "NO")


def replay_recompute(store, tok, text):
    """The execution witness: the printed quantile lines RE-COMPUTED FROM THE STORED RECORDS must appear in the output
    byte for byte. Returns (records read, lines checked, lines missing)."""
    lines = set(text.replace("\r\n", "\n").split("\n"))
    n_rec = n_chk = 0; missing = []
    for mode in ("random", "fixed", "retest"):
        p = store.path_of("validity-v2.%s" % mode)
        if p is None:
            continue
        recs = read_records(p); n_rec += len(recs)
        for key, tv in tok["targets"].items():
            ln = _table_line(key, np.array([r[key] for r in recs], dtype=float), tv, tok["coverage"])
            n_chk += 1
            if ln not in lines:
                missing.append(ln)
    p = store.path_of("validity-v2.heldout")
    if p is not None:
        recs = read_records(p); n_rec += len(recs)
        for key, tv in tok["h2_targets"].items():
            ln = _table_line(key, np.array([r[key] for r in recs], dtype=float), tv, tok["level2"])
            n_chk += 1
            if ln not in lines:
                missing.append(ln)
    return n_rec, n_chk, missing


def replay_v2(say, board, sb, streams, recorded_path, store, token_path=None, expect_master=None,
              expect_streams_prefix=STREAMS_OF_RECORD_PREFIX, **leg_kw):
    """REPLAY MODE (ruling 1 (ii), 56751fa): re-run validity-v2 at the recorded master, R and half seed; it NEITHER
    touches ONE_SHOT_PATH NOR mints a token. PASS iff (a) the recorded table / verdict block is byte-identical (LF),
    (b) the streams-log sha and count equal the recorded ones, (c) the verdict-model digest equals the token of record's,
    and the WITNESS holds (stored records 0 -> > 0; the quantiles re-computed from them match the printed lines)."""
    expect_master = REC_MASTER_G22 if expect_master is None else expect_master
    need(streams.master == expect_master, "the replay runs at the recorded master %s, not %s" % (expect_master, streams.master))
    need(store is not None, "the replay stores the per-replicate records (the witness)")
    token_path = token_path or (recorded_path + ".validity_v2.json")
    stored_before = data.WITNESS.get("records.stored", 0)
    if MUTANT == "replay_touches_one_shot":
        one_shot_claim(recorded_path, streams.master)
    tok, recs = validity_v2_leg(say, board, sb, streams, store=store, **leg_kw)
    if MUTANT == "replay_mints_token":
        report.write_once(store.prefix + ".validity_v2.json", json.dumps(seal_token(tok), default=str))
    rec_txt = open(recorded_path, encoding="utf-8").read().replace("\r\n", "\n")
    new_txt = say.text()
    ba, bb = extract_replay_block(rec_txt), extract_replay_block(new_txt)
    # RB3 (delta READY d8a71ce): the header's board line (the data object) is compared too
    board_rec = [l for l in rec_txt.split("\n") if l.startswith("  board ")]
    board_new = [l for l in new_txt.replace("\r\n", "\n").split("\n") if l.startswith("  board ")]
    ok_board = board_rec == board_new
    ok_a = bool(ba) and ba == bb and ok_board
    lf16 = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]
    rm, rn, rh = parse_streams_line(rec_txt)
    ok_b = (rn == len(streams.log) and rh == streams.digest()
            and (expect_streams_prefix is None or (rh or "").startswith(expect_streams_prefix)))
    tr = json.load(open(token_path, encoding="utf-8"))
    ok_c = tr.get("vm_digest") == tok["vm_digest"]
    n_rec, n_chk, missing = replay_recompute(store, tok, new_txt)
    stored_after = data.WITNESS.get("records.stored", 0)
    ok_w = stored_after - stored_before > 0 and n_rec > 0 and n_chk > 0 and not missing
    ok = ok_a and ok_b and ok_c and ok_w
    hit("REPLAY.%s" % ("PASS" if ok else "FAIL"))
    diff = []
    if not ok_a:
        import difflib
        diff = list(difflib.unified_diff(ba.split("\n"), bb.split("\n"), lineterm="", n=0))[:12]
    say("",
        "  REPLAY (G22-REBIND-1 ruling 1 (ii), 56751fa): master %s | no ONE_SHOT touched | no token minted" % streams.master,
        "  REPLAY (a) the recorded table / verdict block (%d bytes, sha256-lf16 %s) vs the replay's (sha256-lf16 %s): %s"
        % (len(ba), lf16(ba), lf16(bb), "BYTE-IDENTICAL" if ba == bb and bool(ba) else "DIFFER"),
        "  REPLAY (a) the header's board line: recorded %r | replay %r: %s"
        % (board_rec[0] if board_rec else None, board_new[0] if board_new else None, "EQUAL" if ok_board else "DIFFER"),
        *["      " + d for d in diff])
    say("  REPLAY (b) streams: recorded %s streams, sha256 %s | replay %d streams, sha256 %s: %s"
        % (rn, rh, len(streams.log), streams.digest(), "EQUAL" if ok_b else "DIFFER"),
        "  REPLAY (c) verdict-model digest: token of record %s (token_digest %s) | replay %s: %s"
        % (tr.get("vm_digest"), tr.get("token_digest"), tok["vm_digest"], "EQUAL" if ok_c else "DIFFER"),
        "  REPLAY WITNESS: stored records %d -> %d (+%d); %d records re-read; %d quantile lines re-computed from them, %d"
        " missing from the output: %s" % (stored_before, stored_after, stored_after - stored_before, n_rec, n_chk,
                                          len(missing), "MATCH" if not missing else "MISMATCH"),
        "  REPLAY VERDICT: %s" % ("PASS: the re-binding may be recorded (ruling 1 (iii))" if ok
                                  else "FAIL: the re-binding is REFUSED (ruling 1 (iv)); the non-reproduction is a finding"))
    return dict(ok=ok, a=ok_a, b=ok_b, c=ok_c, witness=ok_w, n_rec=n_rec, n_chk=n_chk, missing=missing,
                block_lf16=lf16(bb), token=tok)



# ============================================================================================ (f) overdispersion
# ============================================================== RULING B (4b25059): the certificate of record
# The SHIPPED widener pair applied COLD per (board, judge_model), never refitted on the board being read, plus the
# key-tie decline at 0.975, per anchor, on the key-gap >= 0.02 edges, as KTD-CHECK recomputed it (ktd_check.py L70 /
# L401; budget_transfer.py L32; key_tie_decline.py L20): a call is c~ >= 0.975 under the cold pair AND an established key
# direction (exact McNemar, p < 0.05). Pairs are stored per (board, judge_model) and REFUSED elsewhere (FRAMEWORK L95).
SHIPPED_PAIRS = {
    "x12": ((-3.2326, 3.3133), "Mistral: the SHIPPED pair, the fit on the 891 filtered x12 edges (FRAMEWORK L95, L165, L319)"),
    "merged": ((-3.2326, 3.3133), "Mistral: the SHIPPED pair, the fit on the 891 filtered x12 edges (FRAMEWORK L95, L165, L319)"),
    "grok": ((-3.5451, 3.3854), "grok: the GROK-CALIB stored pair on the same 891 denominator (programme L3928)"),
}
KTD_MERGED = (1714, 4, 4)          # KTD-CHECK C1b: per-anchor widener + decline at 0.975 on merged, called / wrong(est)
RECORD_GAP = 0.02


def record_pair(board_key):
    if board_key not in SHIPPED_PAIRS:
        hit("RECORD_CERT.REFUSED_BOARD")
        raise SystemExit("[RULING B] no stored widener pair for board %r: pairs are stored per (board, judge_model) and"
                         " refused elsewhere (FRAMEWORK L95)" % (board_key,))
    pair, src = SHIPPED_PAIRS[board_key]
    if MUTANT == "wrong_pair":
        pair = SHIPPED_PAIRS["x12" if board_key == "grok" else "grok"][0]
    return pair, src


def record_certificate(edges, board_key, fit=None, thresh=cert.THRESH, gap=RECORD_GAP):
    """Ruling B: the shipped pair COLD + the key-tie decline at 0.975 on the key-gap >= 0.02 edges. `fit` (optional) only
    produces the IN-SAMPLE widener printed beside, deciding nothing (under the mutant widener_refit it replaces the cold
    pair, which the selftest must catch)."""
    pair, src = record_pair(board_key)
    sel = [e for e in edges if e["gap"] >= gap]
    E = cert.EdgeArrays(sel)
    insample = None
    if fit is not None and len(E) >= 3:
        insample = fit(E)
        if MUTANT == "widener_refit":
            pair = insample
    c = cert.cbud_v(E, *pair)
    wid = c >= thresh
    called = wid & E.est
    cw = [e for e, k in zip(sel, called & ~E.right) if k]
    res = dict(pair=tuple(pair), source=src, n=len(sel), widener_called=int(wid.sum()), called=int(called.sum()),
               wrong=int((called & ~E.right).sum()), wrong_est=int((called & ~E.right & E.est).sum()),
               wrong_edges=cw, insample=insample)
    if insample is not None:
        ci = cert.cbud_v(E, *insample)
        k = (ci >= thresh) & E.est
        res["insample_counts"] = (int(k.sum()), int((k & ~E.right).sum()))
    return res


def residue_precondition(board_key, builder, rc, expect=KTD_MERGED):
    """Ruling B PRECONDITION: on merged, the EXACT builder must reproduce KTD-CHECK's 1,714 called / 4(4) before any
    residue model is read; a mismatch STOPS the residue readout (a failed precondition, not an outcome)."""
    if board_key != "merged":
        return True, "N/A (no precondition is registered for board %s; merged only)" % board_key
    if MUTANT == "precondition_skipped":
        return True, "precondition skipped"
    if builder != "exact":
        hit("RECORD_CERT.PRECONDITION_FAILED")
        return False, "the %s builder was used; ruling B requires the EXACT builder (Random(42), rj.mm_fit) on merged" % builder
    got = (rc["called"], rc["wrong"], rc["wrong_est"])
    if got != tuple(expect):
        hit("RECORD_CERT.PRECONDITION_FAILED")
        return False, "called %d / %d(%d) against KTD-CHECK's %d / %d(%d)" % (got + tuple(expect))
    hit("RECORD_CERT.PRECONDITION_MET")
    return True, "REPRODUCED KTD-CHECK: called %d / %d(%d)" % got


def called_residue(edges, board_key, builder="exact", fit=None, expect=KTD_MERGED):
    """Ruling 4 (83f431b) as corrected by ruling B (4b25059): the CALLED wrong(established) population under the certificate
    of record. Returns a dict (the certificate's counts, the precondition, the incidence of the residue)."""
    rc = record_certificate(edges, board_key, fit)
    ok, msg = residue_precondition(board_key, builder, rc, expect)
    wrong = rc["wrong_edges"]
    if MUTANT == "residue_all_wrong":
        wrong = [e for e in edges if e.get("est") and not e["right"]]
    inc = Counter()
    for e in wrong:
        inc[e["a"]] += 1; inc[e["b"]] += 1
    rc.update(precondition_ok=ok, precondition=msg, wrong_edges=wrong, inc=inc)
    return rc


def record_certificate_lines(rc, board_key):
    out = ["  THE CERTIFICATE OF RECORD (ruling B, 4b25059): the SHIPPED pair COLD for %s: b0 %+.4f b1 %+.4f (%s) + the key-tie"
           " decline at 0.975, per anchor, on the %d key-gap >= 0.02 edges: widener alone %d called; after the decline %d"
           " called, wrong %d(%d)" % (board_key, rc["pair"][0], rc["pair"][1], rc["source"], rc["n"], rc["widener_called"],
                                      rc["called"], rc["wrong"], rc["wrong_est"]),
           "    precondition (merged only; exact builder, KTD-CHECK 1,714 / 4(4)): %s -> %s"
           % (rc["precondition"], "N/A" if board_key != "merged" else
              ("MET" if rc["precondition_ok"] else "FAILED PRECONDITION: THE RESIDUE READOUT IS STOPPED"))]
    if rc.get("insample") is not None:
        out.append("    in-sample widener (a DIFFERENT OBJECT, printed beside, deciding nothing): b0 %+.4f b1 %+.4f; + decline"
                   " at 0.975: %d called, wrong(established) %d" % (rc["insample"][0], rc["insample"][1],
                                                                      rc["insample_counts"][0], rc["insample_counts"][1]))
    return out




def set_line(name, mx, s, roster_models):
    return ("%s: {%s} at %d each%s" % (name, ", ".join(s), mx,
            "" if roster_models is None else " | roster membership: " + ", ".join(
                "%s %s" % (m, "IN" if m in roster_models else "NOT IN") for m in s)))


def overdispersion_leg(say, board, edges, streams, perms=2000, quarantined=data.QUARANTINED, roster_models=None,
                       all_models=None, fit=None, board_key=None, builder="exact"):
    say("", "=== (f) OVERDISPERSION of wrong(established) on %s ===" % board.label)
    est = [e for e in edges if e.get("est")]
    wrong = np.array([not e["right"] for e in est])
    W, N = int(wrong.sum()), len(est)
    say("  denominator: %d established edges (exact McNemar on each anchor's judged questions); wrong(established) %d"
        % (N, W))
    if N == 0 or W == 0:
        hit("OVERDISP.NO_EVENTS")
        say("  no wrong(established) events: dispersion not computable")
        return None
    models = sorted({e["a"] for e in est} | {e["b"] for e in est})
    anchors = sorted({e["anchor"] for e in est})

    def stats(wr):
        rate = wr.mean()
        inc = defaultdict(float); n_m = defaultdict(float)
        for e, w in zip(est, wr):
            for m in (e["a"], e["b"]):
                inc[m] += w; n_m[m] += 1
        chi_m = sum((inc[m] - rate * n_m[m]) ** 2 / (rate * n_m[m]) for m in models if rate * n_m[m] > 0)
        inc_a = defaultdict(float); n_a = defaultdict(float)
        for e, w in zip(est, wr):
            inc_a[e["anchor"]] += w; n_a[e["anchor"]] += 1
        chi_a = sum((inc_a[a] - rate * n_a[a]) ** 2 / (rate * n_a[a]) for a in anchors if rate * n_a[a] > 0)
        top = max(models, key=lambda m: (inc[m], m))
        return chi_m, chi_a, top, inc[top] / max(1, wr.sum()), inc
    chi_m, chi_a, top, share, inc = stats(wrong)
    rng = streams.np("overdispersion/%s/permutations" % board.label)
    ge_m = ge_a = ge_s = 0
    for _ in range(perms):
        pm, pa, _, ps, _ = stats(rng.permutation(wrong))
        ge_m += pm >= chi_m; ge_a += pa >= chi_a; ge_s += ps >= share
    say("  by MODEL (each edge counts for both endpoints): chi-square vs a homogeneous rate %.2f over %d models,"
        " permutation p %.4f (%d permutations of the wrong labels among the established edges)" % (chi_m, len(models), (1 + ge_m) / (1 + perms), perms),
        "  by ANCHOR: chi-square %.2f over %d anchors, permutation p %.4f" % (chi_a, len(anchors), (1 + ge_a) / (1 + perms)),
        "  ALL-WRONG population (printed under its own name; NOT the deciding residue definition): %s (share %.2f;"
        " permutation p for the top share %.4f)" % (set_line("most-incident SET", int(inc[top]), top_set(inc)[1], roster_models),
                                                   share, (1 + ge_s) / (1 + perms)),
        "  incidence by model: %s" % ", ".join("%s %d" % (m, int(inc[m])) for m in sorted(models, key=lambda m: -inc[m]) if inc[m] > 0))
    by_anchor = defaultdict(list)
    for e, w in zip(est, wrong):
        by_anchor[e["anchor"]].append(float(w))
    icc = cert.anova_icc(list(by_anchor.values()))
    deff, mk = cert.kish_deff([len(v) for v in by_anchor.values()], icc if icc == icc else 0.0)
    neff = N / deff if deff > 0 else float("nan")
    say("  DEFF of the wrong indicator, anchor-clustered: ANOVA ICC %.4f, Kish m %.2f, DEFF %.3f, n_eff %.1f; rate %d / %d ="
        " %.4f, one-sided 95%% CP UB at n %d: %.4f, at n_eff (w scaled) %.4f"
        % (icc, mk, deff, neff, W, N, W / N, N, cert.cp_ub(W, N), cert.cp_ub(int(round(W / deff)), int(round(neff)))))
    residue = None
    n_cw = 0
    if board_key is not None:
        rc = called_residue(edges, board_key, builder, fit)
        say(*record_certificate_lines(rc, board_key))
        hit("OVERDISP.CALLED_RESIDUE")
        if not rc["precondition_ok"]:
            residue = "STOPPED"
            say("  RESIDUE MODEL: NOT READ (failed precondition, ruling B); not an outcome")
        else:
            mx, s = top_set(rc["inc"])
            residue = s
            cw = rc["wrong_edges"]
            n_cw = len(cw)
            say("  RESIDUE MODEL, THE DECIDING DEFINITION (ruling 4 as corrected by ruling B): CALLED wrong(established)"
                " under the certificate of record: %d edges" % len(cw),
                "    " + (set_line("the residue model SET", mx, s, roster_models) if s else "no called wrong(established) edge: no residue model"),
                "    the called wrong(established) edges: " + ("; ".join("%s %s vs %s" % (e["anchor"], e["a"], e["b"]) for e in cw) or "none"))
    if all_models is not None:
        llama70 = [m for m in all_models if "llama" in m.lower() and "70b" in m.lower()]
        say("  RESIDUE MODEL, RESOLVED FROM THE DATA: the 70B Llama models in the eval DB roster: %s"
            % (", ".join(llama70) or "none"),
            "    quarantined (CONTEXT.md section 4 rule 6): %s -> %s" % (quarantined, "in the DB, EXCLUDED from the roster" if quarantined in all_models else "not in the DB"),
            "    the residue model on this board (CALLED definition, ruling 4): %s | roster: %d models"
            % ("{%s}" % ", ".join(residue) if isinstance(residue, list) and residue else
               ("NOT READ (failed precondition)" if residue == "STOPPED" else "(not computed)"), len(roster_models or [])))
        for m in llama70:
            say("    %s: in the roster %s; quarantined %s" % (m, "YES" if roster_models and m in roster_models else "NO",
                                                          "YES" if m == quarantined else "no"))
    hit("OVERDISP.DONE")
    return dict(chi_m=chi_m, chi_a=chi_a, top=top, top_set=top_set(inc)[1], share=share, deff=deff, neff=neff,
                residue=residue, n_called_wrong=n_cw)


# ====================================================================================== P7 SCORING (the P7 ruling)
P7_NAMED = "Meta-Llama-3_1-70B-Instruct"


def p7_score(results, roster, named=P7_NAMED):
    """results: {board: dict(residue=<sorted list> | "STOPPED" | None, n_called_wrong=int)}.
    IDENTITY: scored on MERGED ONLY: HELD iff `named` is the UNIQUE most-incident model among merged's called
    wrong(established) edges under the certificate of record; a tie is NOT HELD; merged not read -> UNDETERMINED.
    x12 and grok: DESCRIPTIVE; a residue set formed by ONE called edge prints UNRESOLVED (one-edge tie), never scored.
    ROSTER: checked on ALL boards read: every member of every residue set inside the roster, else the falsifier fires.
    Beside, POST-DATA, deciding nothing: reading (a) the named model in the top set on every board read; reading (b) the
    unique top on every board read. Returns (lines, verdict dict)."""
    scored = ["merged"] + (["x12"] if MUTANT == "p7_x12_scored" else [])
    lines = ["", "=== P7 (the P7 scoring ruling): the residue model and its roster membership ==="]
    ident = None
    for bk in scored:
        r = results.get(bk)
        if r is None or not isinstance(r.get("residue"), list):
            ident = "UNDETERMINED (%s not read%s)" % (bk, " : failed precondition" if r and r.get("residue") == "STOPPED" else "")
            break
        s = r["residue"]
        ok = (named in s) if MUTANT == "p7_tie_held" else (s == [named])
        if not ok:
            ident = "NOT HELD (%s: the most-incident set is {%s}%s)" % (bk, ", ".join(s),
                                                                        ", a TIE" if len(s) > 1 else "")
            break
    if ident is None:
        ident = "HELD (%s is the UNIQUE most-incident model on merged)" % named
    hit("P7.IDENTITY_%s" % ident.split()[0])
    lines.append("  IDENTITY CLAUSE (scored on MERGED ONLY): %s" % ident)
    for bk in ("x12", "grok"):
        r = results.get(bk)
        if r is None:
            continue
        s = r.get("residue")
        if not isinstance(s, list):
            lines.append("  %s (DESCRIPTIVE, never scored): residue not read (%s)" % (bk, s))
        elif r.get("n_called_wrong", 0) == 1 and len(s) == 2:
            hit("P7.ONE_EDGE_TIE")
            lines.append("  %s (DESCRIPTIVE, never scored): {%s}: UNRESOLVED (one-edge tie)" % (bk, ", ".join(s)))
        else:
            lines.append("  %s (DESCRIPTIVE, never scored): {%s} over %d called wrong(established) edges"
                         % (bk, ", ".join(s), r.get("n_called_wrong", 0)))
    checked = ["merged"] if MUTANT == "p7_roster_merged_only" else sorted(results)
    outside = [(bk, m) for bk in checked for m in (results[bk].get("residue") if isinstance(results.get(bk, {}).get("residue"), list) else [])
               if m not in roster]
    roster_ok = not outside
    hit("P7.ROSTER_%s" % ("OK" if roster_ok else "FALSIFIER"))
    lines.append("  ROSTER CLAUSE (checked on ALL boards read: %s): %s"
                 % (", ".join(checked), "every residue-set member is inside the %d-model roster" % len(roster) if roster_ok
                    else "FALSIFIER FIRES: outside the roster: " + "; ".join("%s on %s" % (m, bk) for bk, m in outside)))
    read = {bk: r["residue"] for bk, r in results.items() if isinstance(r.get("residue"), list)}
    ra = bool(read) and all(named in s for s in read.values())
    rb = bool(read) and all(s == [named] for s in read.values())
    lines.append("  POST-DATA readings, deciding nothing: (a) '%s in the top set on every board read' %s; (b) 'the unique top"
                 " on every board read' %s (boards read: %s)" % (named, "yes" if ra else "no", "yes" if rb else "no",
                                                               ", ".join(sorted(read)) or "none"))
    return lines, dict(identity=ident, roster_ok=roster_ok, outside=outside, reading_a=ra, reading_b=rb)


# ============================================================================================ (h) coverage
def coverage_leg(say, keytab, roster, strata_of, eval_ids=None, bar=0.95, letters="ABCDEFGHIJ"):
    say("", "=== (h) EXTRACTION COVERAGE D_c per anchor for the %d-model roster ===" % len(roster),
        "  D_c = share of (question, pair) with two non-blank extracted answers (FRAMEWORK L39); a missing row counts"
        " blank; the valid-letter variant (%s) beside; questions: %s" % (letters, "the EVAL id file given" if eval_ids
                                                                        else "ALL questions of the category (the DEV split's EVAL ids are not read here)"))
    M = len(roster); pairs = M * (M - 1) / 2
    by = defaultdict(list)
    for q, s in strata_of.items():
        if eval_ids is None or q in eval_ids:
            by[s].append(q)
    res = {}
    for s in sorted(by):
        qs = by[s]
        nb = np.array([sum(1 for m in roster if keytab.P.get(q, {}).get(m, "")) for q in qs])
        nv = np.array([sum(1 for m in roster if keytab.P.get(q, {}).get(m, "") in letters and keytab.P.get(q, {}).get(m, "")) for q in qs])
        dc = float((nb * (nb - 1) / 2).sum() / (len(qs) * pairs))
        dv = float((nv * (nv - 1) / 2).sum() / (len(qs) * pairs))
        word = "PASS" if dc >= bar else "BELOW"
        hit("COVERAGE.%s" % word)
        res[s] = (dc, dv, len(qs), word)
        say("  %-28s q %5d | D_c %.4f | valid-letter %.4f | %s the %.2f bar" % (s, len(qs), dc, dv, word, bar))
    blank = {m: sum(1 for s in by for q in by[s] if not keytab.P.get(q, {}).get(m, "")) / max(1, sum(len(v) for v in by.values()))
             for m in roster}
    worst = sorted(blank, key=lambda m: -blank[m])[:8]
    say("  per-model blank rate, worst eight: %s" % ", ".join("%s %.3f" % (m, blank[m]) for m in worst),
        "  anchors at or above the bar: %d of %d" % (sum(1 for v in res.values() if v[3] == "PASS"), len(res)))
    return res


def key_tier_lines(say, keytab, roster, strata_of, gap=0.017):
    say("  frontier band from KEY TIERS (0.017 adjacency rule) per anchor, %d-model roster:" % len(roster))
    by = defaultdict(list)
    for q, s in strata_of.items():
        by[s].append(q)
    for s in sorted(by):
        acc = {}
        for m in roster:
            v = [keytab.K[q][m] for q in by[s] if m in keytab.K.get(q, {})]
            if v:
                acc[m] = sum(v) / len(v)
        if acc:
            t = cert.key_tiers(acc, sorted(acc), gap)
            say("    %-28s top tier (%d): %s" % (s, len(t[0]), ", ".join(t[0])))
