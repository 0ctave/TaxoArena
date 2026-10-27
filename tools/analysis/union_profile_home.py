"""UNION-PROFILE-HOME (registered 2026-09-19 before any code, commit 8b3f6e2, docs/judge_v2_program.md L7926-L8063; plan
2026-09-18 R3 and §5 question 3; review batch1 D1). ZERO calls. Key only. Pool paeec37aa28063c75.

  python tools/analysis/union_profile_home.py --selftest   # synthetic strata: one with the source's undominated set, one with a different one; the gate stop; no DB of record beyond the pool guard
  python tools/analysis/union_profile_home.py --dry-run    # pool id, the 52 / 39 / 14 stratum counts and supports, the frozen-file and routing-CSV checks; NO outcome number
  python tools/analysis/union_profile_home.py --run        # writes experiment_results/multicorpus/union_profile_home_outcome.txt (+ union_profile_home_strata.csv) ONCE

THE QUESTION (registration, condensed; the programme file wins over this copy). Are the 39 order-reliable union strata or
the 14 MMLU-Pro anchors the profile's home? The readout prints the numbers the choice needs: (1) an interaction-only
reliability WITH an interval on both objects; (2) the coverage of the union pool by the order-reliable strata; (3) per
order-reliable stratum, whether the key's undominated set differs from its source's (the router's object, FW L131 / L175);
(4) the roster caveat on every row.

DATA OBJECTS (as PROFILE-INTERVAL-ALL-UNION read them; nothing new): pool paeec37aa28063c75, 6,482 reserved questions in
52 (source, domain) strata from experiment_configs/reserved_pool_frozen_paeec.json; the routing CSV of record
MAIN_union_routing_queries.csv checked at the level it supports (52 keys, per-key counts, true_source; no id column);
eval_results on the 18-model union roster, MATH from eval_results_mathfix ONLY; Meta-Llama-3-70B-Instruct absent;
profile_interval_all_union_strata.csv (52 rows; cls_raw = order class): the 39 ORDER-RELIABLE strata = cls_raw == PASS; the
5 order-FAIL (BBH/causal_judgement, MUSR/murder_mysteries, MUSR/team_allocation, GPQA/Physics, GPQA/Chemistry) carry no
order claim and no undominated set ("no order"); the 8 order-PWI are printed beside, not counted.

INSTRUMENTS (imported, never re-implemented): profile_interval_union.load_strata / data_check / load_key / make_key_build /
halvings_fixed / support_table (the union test's loaders and its settings: 40 halvings Random(7), per-half floor min_cell
12); profile_reliability.reliability with demean_two_way (the --interaction-only path of record) and demean_by_model;
profile_reliability_interaction.r_of / jack / fit_additive_logit / key_table / variance_decomposition (the logit-additive
null of PROFILE-RELIABILITY-INTERACTION C2); systematic_budget.mcnemar_edge (exact two-sided McNemar, integer arithmetic).

READINGS CHOSEN WHERE THE REGISTRATION IS SILENT (each also printed in the outcome):
  * The gate (C1). The checker's 0.8537 (review batch1 D1, scratch s1b_union_null.py) was: the union test's halvings
    (Random(7), every stratum, sorted ids shuffled, mid = n // 2), per-half 18-model accuracy vectors, model-demeaned then
    stratum-demeaned, Pearson over the 936 points, Spearman-Brown of the mean r over 40 halvings. That is exactly
    profile_reliability.reliability(strata, qsel, build, models, Random(7), min_cell=12, demean=demean_two_way) on the
    frozen file's stratum order (demean_two_way's alternation converges after one model + one stratum pass on a balanced
    table). A mismatch to 4 dp stops the readout before any other number is printed.
  * Floors. reliability()'s 50-point floor is a 14 x 12 board floor: a 3-stratum source (54 points) loses every
    leave-one-stratum-out fold (36 points). As PROFILE-INTERVAL-ALL-UNION C3b did, the fixed-halving mirror
    (profile_interval_union.halvings_fixed, line-for-line reliability()) is read with the floor at 2 x 18 = 36 points;
    wherever the full object has >= 50 points the mirror is asserted equal to reliability() to 1e-12.
  * Jackknife: leave-one-stratum-out, RE-HALVED (fresh Random(7) on the remaining strata) primary, FIXED beside; z = 1.96;
    a jackknife over <= 3 strata is printed as a resolution statement. C2's class is read on the RE-HALVED lower bound;
    if the FIXED bound disagrees on the 0.70 boundary the class is UNDETERMINED (the ANCHOR-PROFILE-INTERVAL rule).
  * Null. a_m, d_s = the additive-logit MLE on the real 18 x 52 (successes, trials) table (fit_additive_logit); 20 tables,
    numpy RandomState(1..20), every reserved question of every stratum drawn Bernoulli(logistic(a_m - d_s)) for every
    model (the simulation loop is profile_reliability_interaction.null_tables', whose own halving reader carries the
    25-per-half floor; the tables are therefore drawn here with the same seeds and read through the union floor 12); each
    object (52 / 39 / 14 / per source) is re-halved on its own strata with Random(7) and read under both demeanings;
    median and range beside the real reading.
  * (3) Undominated set U = models with no ESTABLISHED ORDERED-KEY edge above them; an edge a > b is established iff exact
    two-sided McNemar p < 0.05 on the stratum's reserved questions AND b_ > c_. U_src by the same rule on the source's
    pooled reserved questions. "differs" = U_s != U_src as sets. argmax = the model with the highest reserved-side
    accuracy, ties broken by roster order (sorted names; the tie count is printed). D = the number of the 39 order-reliable
    strata with U_s != U_src.
  * P7's gate ("the argmax-differs count over the 52 reproduces 25 exactly"). FW L180's 25 was MC-ROUTER's count
    (multicorpus_router.py): argmax by TRAIN-side accuracy on its OWN per-(source, domain) 0.30 split (seed 42) over the
    21,606-question corpus, with the INGESTED MATH rows and ties to the first model in name order. The registered object
    here is the paeec RESERVED side with MATH-FIX. Both counts are printed: the registered one scores P7; MC-ROUTER's
    split rule is replayed beside (labelled) so the reviewer can see which object the 25 belongs to. C4 does not depend on
    P7 (the criteria text makes C1 the only stopping gate); if P7 fails the outcome says so and the registrar decides.
  * (4) Roster subsets: models sorted by their unweighted mean accuracy over the 52 strata; bottom-9 = the first 9,
    middle-9 = ranks 5-13, top-9 = the last 9 (the checker's abil[:9] / abil[4:13] / abil[9:]).
  * McNemar-established rule: wrong(established) applies to (3) only (no judge direction exists; both conventions n/a).
  * Write-once: --run refuses if the outcome file exists. Every DB mode=ro; the pool id is the FIRST printed line.
"""
import os, sys, csv, math, json, random, sqlite3, time, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import profile_reliability as pr
import profile_interval_union as piu
import profile_reliability_interaction as pri
import systematic_budget as sbg

POOL = pool_guard.UNION_POOL                       # paeec37aa28063c75
STRATA_CSV = os.path.join(ROOT, "experiment_results", "multicorpus", "profile_interval_all_union_strata.csv")
OUT_DIR = os.path.join(ROOT, "experiment_results", "multicorpus")
OUT_TXT = os.path.join(OUT_DIR, "union_profile_home_outcome.txt")
OUT_CSV = os.path.join(OUT_DIR, "union_profile_home_strata.csv")
MC_DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
GATE_R = 0.8537                                    # the checker's interaction-only R over the 52 strata (L5648)
RECORDED_MODEL_R52 = 0.9424                        # PROFILE-INTERVAL-ALL-UNION C2 (beside)
ORDER_FAIL = {"BBH/causal_judgement", "MUSR/murder_mysteries", "MUSR/team_allocation", "GPQA/Physics", "GPQA/Chemistry"}
EXPECTED_ORDER = {"PASS": 39, "PASS-WITH-INTERVAL": 8, "FAIL": 5}
FW_ARGMAX_DIFFERS = 25
N_MODELS = 18
BAR = 0.70
SEED = 7
REPS = pr.REPS
MIN_CELL = piu.MIN_CELL                            # 12
Z = 1.96
N_NULL = 20
ALPHA = 0.05
sb = pr.sb
mean_sd = piu.mean_sd
SOURCES = piu.SOURCES


# ----------------------------------------------------------------------------------------------- reliability with intervals
def r_mean(per_rep, dm, drop=None, min_points=None):
    return mean_sd([pri.r_of(P, dm, drop, min_points) for P in per_rep])


def leg(cells, qsel, build, models, tag, want_loo=True):
    """model-demeaned and interaction-only R on the same halvings; LOSO jackknife re-halved (primary) and fixed (beside)."""
    mp = 2 * len(models)
    per_rep = piu.halvings_fixed(cells, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
    present = [c for c in cells if any(p[0] == c for p in per_rep[0])]
    out = dict(tag=tag, cells=present, n_cells=len(present), mirror_checked=False)
    for name, dm in (("model", pr.demean_by_model), ("both", pr.demean_two_way)):
        r, sd, n = r_mean(per_rep, dm, None, mp)
        if len(present) * len(models) >= 50:
            r_ref, _, _ = pr.reliability(cells, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL, demean=dm)
            assert abs(r_ref - r) < 1e-12, "fixed-halving mirror differs from reliability(): %r vs %r" % (r_ref, r)
            out["mirror_checked"] = True
        R = sb(r)
        d = dict(r=r, sd=sd, n=n, R=R, halv_sd=(sb(r + sd) - R) if sd == sd else float("nan"))
        if want_loo and len(present) >= 2:
            loo_fx = [sb(r_mean(per_rep, dm, c, mp)[0]) for c in present]
            loo_re = []
            for c in present:
                sub = {k: v for k, v in cells.items() if k != c}
                pr_i = piu.halvings_fixed(sub, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
                loo_re.append(sb(r_mean(pr_i, dm, None, mp)[0]))
            se_fx, lo_fx, hi_fx = pri.jack(R, loo_fx); se_re, lo_re, hi_re = pri.jack(R, loo_re)
            d.update(lo_fx=lo_fx, hi_fx=hi_fx, lo_re=lo_re, hi_re=hi_re, loo_fx=dict(zip(present, loo_fx)), loo_re=dict(zip(present, loo_re)))
        else:
            d.update(lo_fx=float("nan"), hi_fx=float("nan"), lo_re=float("nan"), hi_re=float("nan"), loo_fx={}, loo_re={})
        out[name] = d
    return out


def cls_of(R, lo):
    if R != R: return "n/a"
    if R >= BAR and lo == lo and lo >= BAR: return "PASS"
    if R >= BAR: return "PASS-WITH-INTERVAL"
    return "FAIL"


def c2_class(e):
    a, b = cls_of(e["R"], e["lo_re"]), cls_of(e["R"], e["lo_fx"])
    return a if a == b else "UNDETERMINED (re-halved %s, fixed %s)" % (a, b)


# ----------------------------------------------------------------------------------------------- the null
def null_tables_union(strata, Kd, models, n_tables=N_NULL):
    """a_m, d_s fitted on the real table (pri.fit_additive_logit on pri.key_table); n_tables simulated key tables on the same
    questions (numpy RandomState(1..n), exactly null_tables' draw). Returns (list of {q: np.array}, fit info)."""
    k, n = pri.key_table(strata, Kd, models)
    a, d, iters, clipped = pri.fit_additive_logit(k, n)
    P = 1 / (1 + np.exp(-(a[:, None] - d[None, :])))
    tables = []
    for t in range(n_tables):
        rs = np.random.RandomState(t + 1)
        Ksim = {}
        for j, c in enumerate(strata):
            draws = rs.rand(len(strata[c]), len(models)) < P[:, j][None, :]
            for qi, q in enumerate(strata[c]):
                Ksim[q] = draws[qi].astype(float)
        tables.append(Ksim)
    vd = pri.variance_decomposition(k, n)
    return tables, dict(a=a, d=d, iters=iters, clipped=clipped, shares=vd["shares"])


def null_read(tables, cells, models):
    """read the instrument (re-halved on `cells`, Random(7), floor 12) under both demeanings on every simulated table."""
    mp = 2 * len(models)
    qsel = set(q for v in cells.values() for q in v)
    reads = []
    for Ksim in tables:
        build = piu.make_key_build(Ksim, models)
        per_rep = piu.halvings_fixed(cells, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
        reads.append((sb(r_mean(per_rep, pr.demean_by_model, None, mp)[0]), sb(r_mean(per_rep, pr.demean_two_way, None, mp)[0])))
    return dict(model=pri.summarise_null(reads, 0), both=pri.summarise_null(reads, 1))


# ----------------------------------------------------------------------------------------------- undominated sets
def undominated(models, Kd, qs, alpha=ALPHA):
    aq = {"cell": list(qs)}
    est = []; dominated = set()
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            p, b_, c_ = sbg.mcnemar_edge({"anchor": "cell", "a": a, "b": b}, Kd, aq)
            if p < alpha and b_ != c_:
                hi, lo = (a, b) if b_ > c_ else (b, a)
                est.append((hi, lo, p)); dominated.add(lo)
    return sorted(m for m in models if m not in dominated), len(est)


def argmax_acc(models, K, qs):
    M = np.stack([K[q] for q in qs]).mean(axis=0)
    best = float(M.max()); ties = [models[i] for i in range(len(models)) if M[i] == best]
    return ties[0], len(ties), M


# ----------------------------------------------------------------------------------------------- the analysis (data-agnostic; --run and --selftest share it)
def analyse(strata, K, models, order_cls, profile_cls, L, gate=GATE_R, n_null=N_NULL, mc_router=None, log=None):
    """strata: {key: [ids]} frozen order; K: {q: np.array(18)}; order_cls / profile_cls: {key: class} from the CSV of record.
    Returns (lines, csv rows, summary); raises SystemExit if the gate fails."""
    t0 = time.time(); say = L.append; log = log or (lambda s: None)
    build = piu.make_key_build(K, models)
    qsel = set(q for v in strata.values() for q in v)
    n_of = {k: len(v) for k, v in strata.items()}
    src_of = lambda k: k.split("/", 1)[0]
    Kd = {q: {m: int(K[q][i]) for i, m in enumerate(models)} for q in qsel}       # dict form for key_table / mcnemar_edge
    n_pool = sum(n_of.values())
    order_ok = [k for k in strata if order_cls[k] == "PASS"]
    order_pwi = [k for k in strata if order_cls[k] == "PASS-WITH-INTERVAL"]
    order_fail = [k for k in strata if order_cls[k] == "FAIL"]
    worse = lambda a, b: a if {"PASS": 0, "PASS-WITH-INTERVAL": 1, "FAIL": 2}[a] >= {"PASS": 0, "PASS-WITH-INTERVAL": 1, "FAIL": 2}[b] else b
    record_cls = {k: worse(profile_cls[k], order_cls[k]) for k in strata}
    mm14 = [k for k in strata if src_of(k) == "MMLU_PRO_LB"]
    summary = dict(n_pool=n_pool, n_order_ok=len(order_ok))

    # ---------- (1a) the gate ----------
    say("")
    say("=== (1) RELIABILITY WITH INTERVALS, interaction-only (model- AND stratum-demeaned half-vectors, Pearson across the %d models, Spearman-Brown, %d halvings Random(%d), per-half floor %d) ===" % (len(models), REPS, SEED, MIN_CELL))
    say("  leave-one-stratum-out jackknife RE-HALVED (primary) / FIXED (beside), z = %.2f; halving SD on the SB scale; model-demeaned R beside. A jackknife over <= 3 strata is a RESOLUTION statement." % Z)
    say("  reliability()'s 50-point floor (a 14 x 12 board floor) is read at 2 x %d = %d points through the fixed-halving mirror (PROFILE-INTERVAL-ALL-UNION C3b precedent); asserted equal to reliability() wherever >= 50 points." % (len(models), 2 * len(models)))
    r52, sd52, n52 = pr.reliability(strata, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL, demean=pr.demean_two_way)
    R52 = sb(r52)
    gate_ok = ("%.4f" % R52) == ("%.4f" % gate)
    say("  (1a) GATE C1: interaction-only R over the %d strata = %.4f (r %.4f, %d halvings) vs the checker's %.4f -> %s"
        % (len(strata), R52, r52, n52, gate, "REPRODUCES to 4 dp" if gate_ok else "MISMATCH: the readout STOPS here (nothing below is a number of record)"))
    summary.update(R52=R52, gate_ok=gate_ok)
    if not gate_ok:
        raise SystemExit("[GATE] 52-stratum interaction-only R %.4f != %.4f; readout stopped" % (R52, gate))
    legs = {}
    objects = [("52", "all %d strata" % len(strata), strata),
               ("39", "%d ORDER-RELIABLE strata (cls_raw PASS)" % len(order_ok), {k: strata[k] for k in order_ok}),
               ("14", "%d MMLU_PRO_LB strata (the 14 anchors as union strata, 18-model roster, pool %s)" % (len(mm14), POOL), {k: strata[k] for k in mm14})]
    for s in SOURCES:
        ks = [k for k in strata if src_of(k) == s]
        objects.append((s, "%s: %d strata over its own strata" % (s, len(ks)), {k: strata[k] for k in ks}))
    for okey, odesc, ocells in objects:
        if len(ocells) < 2:
            legs[okey] = None; continue
        legs[okey] = leg(ocells, set(q for v in ocells.values() for q in v), build, models, okey)
        log("(1) %s done %.0fs" % (okey, time.time() - t0))
    assert abs(legs["52"]["both"]["R"] - R52) < 1e-12
    say("  %-11s %-6s %6s %8s %8s %8s  %-19s %-19s  %s" % ("object", "demean", "strata", "r", "R(SB)", "halvSD", "jk RE-HALVED 95%", "jk FIXED 95%", "note"))
    for okey, odesc, ocells in objects:
        lg = legs[okey]
        if lg is None:
            say("  %-11s undefined by construction (%d stratum: demeaning leaves nothing to correlate)  [%s]" % (okey, len(ocells), odesc)); continue
        for name in ("model", "both"):
            e = lg[name]
            note = ""
            if okey == "52" and name == "model": note = "recorded 0.9424 [0.9264, 0.9585] (PROFILE-INTERVAL-ALL-UNION C2; fixed jk)"
            if okey == "52" and name == "both": note = "the checker's 0.8537 (no interval on record until now): C1 GATE"
            if okey == "39" and name == "both": note = "C2, P1: class %s" % c2_class(e)
            if okey == "14" and name == "both": note = "C3, P2: beside K12 0.8665 [0.8000, 0.9330] / K46 0.8118 [0.7254, 0.8983] on p2dca's 2,811 judged q; NO level comparison"
            if lg["n_cells"] <= 3: note += "  (jackknife over %d strata = resolution statement)" % lg["n_cells"]
            say("  %-11s %-6s %6d %8.4f %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]  %s"
                % (okey, name, lg["n_cells"], e["r"], e["R"], e["halv_sd"], e["lo_re"], e["hi_re"], e["lo_fx"], e["hi_fx"], note))
    say("  leave-one-stratum-out (interaction-only, re-halved), the 39: " + ", ".join("-%s %.4f" % (c.split("/", 1)[1][:22], v) for c, v in sorted(legs["39"]["both"]["loo_re"].items(), key=lambda kv: kv[1])[:6]) + " ... "
        + ", ".join("-%s %.4f" % (c.split("/", 1)[1][:22], v) for c, v in sorted(legs["39"]["both"]["loo_re"].items(), key=lambda kv: kv[1])[-3:]))
    # the null
    say("  logit-additive null (PROFILE-RELIABILITY-INTERACTION C2): a_m, d_s fitted on the real %d x %d table; %d tables; each object re-halved on its own strata; median [range]" % (len(models), len(strata), n_null))
    tables, fit = null_tables_union(strata, Kd, models, n_null)
    say("    additive-logit MLE: %d sweeps, %d logits clipped; a_m range [%.3f, %.3f]; variance shares of the accuracy table model / stratum / interaction %.2f / %.2f / %.2f"
        % (fit["iters"], fit["clipped"], fit["a"].min(), fit["a"].max(), *fit["shares"]))
    nulls = {}
    for okey, odesc, ocells in objects:
        if legs[okey] is None: continue
        nd = null_read(tables, ocells, models); nulls[okey] = nd
        say("    %-11s null model-only median %.4f [%.4f, %.4f] (real %.4f) | interaction-only median %.4f [%.4f, %.4f] (real %.4f; real - null %+.4f)"
            % (okey, nd["model"][0], nd["model"][1], nd["model"][2], legs[okey]["model"]["R"], nd["both"][0], nd["both"][1], nd["both"][2], legs[okey]["both"]["R"], legs[okey]["both"]["R"] - nd["both"][0]))
        log("null %s done %.0fs" % (okey, time.time() - t0))
    summary.update(legs=legs, nulls=nulls)

    # ---------- (4) roster subsets ----------
    say("")
    say("=== (4) ROSTER CAVEAT: the union roster is %d models (paeec); the MMLU-Pro anchor rows of record are K12 (ARENA12) and K46 on p2dca (2,811 judged q); no level comparison between (1c) and 0.8665 / 0.8118 ===" % len(models))
    gmean = {m: float(np.mean([np.stack([K[q] for q in strata[c]]).mean(axis=0)[i] for c in strata])) for i, m in enumerate(models)}
    abil = sorted(models, key=lambda m: gmean[m])
    subsets = [("all 18", models), ("middle 9", abil[4:13]), ("top 9", abil[9:]), ("bottom 9", abil[:9])]
    say("  roster subsets by unweighted mean accuracy over the %d strata (the checker's abil[:9] / abil[4:13] / abil[9:]); re-read for (1a) and (1b), both demeanings (point, no jackknife):" % len(strata))
    say("  %-10s %7s  %-8s %-8s  %-8s %-8s" % ("roster", "sprdSD", "52 model", "52 both", "39 model", "39 both"))
    rsub = {}
    for name, sub in subsets:
        mi = {m: i for i, m in enumerate(models)}
        def bS(cqs, sub=sub, mi=mi):
            M = np.stack([K[q] for q in cqs]).mean(axis=0)
            return {m: float(M[mi[m]]) for m in sub}
        vals = []
        for okey, ocells in (("52", strata), ("39", {k: strata[k] for k in order_ok})):
            qs_ = set(q for v in ocells.values() for q in v)
            for dm in (pr.demean_by_model, pr.demean_two_way):
                r_, _, _ = pr.reliability(ocells, qs_, bS, list(sub), random.Random(SEED), min_cell=MIN_CELL, demean=dm)
                vals.append(sb(r_))
        rsub[name] = vals
        say("  %-10s %7.3f  %8.4f %8.4f  %8.4f %8.4f" % (name, float(np.std([gmean[m] for m in sub])), *vals))
    summary["roster_subsets"] = rsub

    # ---------- (2) coverage ----------
    say("")
    say("=== (2) COVERAGE of the union pool (%d reserved questions) ===" % n_pool)
    n_ok = sum(n_of[k] for k in order_ok); n_rec = sum(n_of[k] for k in strata if record_cls[k] == "PASS"); n_nonfail = sum(n_of[k] for k in strata if order_cls[k] != "FAIL")
    say("  %d order-reliable strata (cls_raw PASS): %d / %d = %.4f" % (len(order_ok), n_ok, n_pool, n_ok / n_pool))
    say("  %d PASS-of-record strata (worse of profile and order): %d / %d = %.4f" % (sum(1 for k in strata if record_cls[k] == "PASS"), n_rec, n_pool, n_rec / n_pool))
    say("  %d non-FAIL strata (order reading): %d / %d = %.4f" % (sum(1 for k in strata if order_cls[k] != "FAIL"), n_nonfail, n_pool, n_nonfail / n_pool))
    cov_src = {}
    for s in SOURCES:
        ks = [k for k in strata if src_of(k) == s]; tot = sum(n_of[k] for k in ks)
        a = sum(n_of[k] for k in ks if order_cls[k] == "PASS"); b = sum(n_of[k] for k in ks if record_cls[k] == "PASS"); c = sum(n_of[k] for k in ks if order_cls[k] != "FAIL")
        cov_src[s] = (a / tot, b / tot, c / tot, tot)
        say("    %-12s %5d q: order-reliable %.3f (%d/%d strata) | PASS-of-record %.3f (%d) | non-FAIL %.3f (%d)"
            % (s, tot, a / tot, sum(1 for k in ks if order_cls[k] == "PASS"), len(ks), b / tot, sum(1 for k in ks if record_cls[k] == "PASS"), c / tot, sum(1 for k in ks if order_cls[k] != "FAIL")))
    summary.update(cov_ok=n_ok / n_pool, cov_rec=n_rec / n_pool, cov_nonfail=n_nonfail / n_pool, cov_src=cov_src)

    # ---------- (3) undominated sets ----------
    say("")
    say("=== (3) UNDOMINATED SETS per stratum: U_s = models with no ESTABLISHED ORDERED-KEY edge above them (exact two-sided McNemar p < %.2f on the stratum's reserved questions, systematic_budget.mcnemar_edge, integer arithmetic; the wrong(established) rule) ===" % ALPHA)
    say("  U_src by the same rule on the source's pooled reserved questions; 'differs' = U_s != U_src as sets; beside: argmax accuracy differs (ties to roster order) and |U_s| (the honesty of the row).")
    say("  the %d order-FAIL strata carry no order claim and no undominated set (printed 'no order'); the %d order-PWI are printed beside, not counted." % (len(order_fail), len(order_pwi)))
    U_src = {}; arg_src = {}
    for s in SOURCES:
        qs_ = [q for k in strata if src_of(k) == s for q in strata[k]]
        U_src[s], ne = undominated(models, Kd, qs_); arg_src[s] = argmax_acc(models, K, qs_)
        say("  source %-12s n=%5d  U_src = %s (|U| %d; established edges %d of %d)  argmax %s%s"
            % (s, len(qs_), U_src[s], len(U_src[s]), ne, len(models) * (len(models) - 1) // 2, arg_src[s][0], " (%d-way tie)" % arg_src[s][1] if arg_src[s][1] > 1 else ""))
    rows = []; D = 0; n_arg_diff52 = 0; sizes = []; n_arg_tie = 0
    say("  %-40s %5s %-6s %-19s %-19s %-7s %4s %-9s %-8s %s" % ("stratum", "n", "order", "profile", "record", "differs", "|U|", "argmax!=", "argmax", "U_s"))
    for k in strata:
        s = src_of(k); qs_ = strata[k]
        arg, nt, _ = argmax_acc(models, K, qs_); n_arg_tie += int(nt > 1)
        arg_diff = arg != arg_src[s][0]; n_arg_diff52 += int(arg_diff)
        if order_cls[k] == "FAIL":
            rows.append(dict(key=k, source=s, domain=k.split("/", 1)[1], n=n_of[k], cls_order=order_cls[k], cls_profile=profile_cls[k], cls_record=record_cls[k], counted=0,
                             U_s="no order", U_src="|".join(U_src[s]), size_U=float("nan"), n_established=float("nan"), differs="no order", argmax=arg, argmax_src=arg_src[s][0], argmax_differs=int(arg_diff),
                             loo52_both_rehalved=legs["52"]["both"]["loo_re"].get(k, float("nan")), loo52_both_fixed=legs["52"]["both"]["loo_fx"].get(k, float("nan")),
                             loo39_both_rehalved=float("nan"), loo39_both_fixed=float("nan")))
            say("  %-40s %5d %-6s %-19s %-19s %-7s %4s %-9s %-8s %s" % (k, n_of[k], "FAIL", profile_cls[k], record_cls[k], "-", "-", "yes" if arg_diff else "no", arg[:8], "no order"))
            continue
        U, ne = undominated(models, Kd, qs_)
        differs = (set(U) != set(U_src[s]))
        counted = order_cls[k] == "PASS"
        if counted: D += int(differs); sizes.append(len(U))
        rows.append(dict(key=k, source=s, domain=k.split("/", 1)[1], n=n_of[k], cls_order=order_cls[k], cls_profile=profile_cls[k], cls_record=record_cls[k], counted=int(counted),
                         U_s="|".join(U), U_src="|".join(U_src[s]), size_U=len(U), n_established=ne, differs=int(differs), argmax=arg, argmax_src=arg_src[s][0], argmax_differs=int(arg_diff),
                         loo52_both_rehalved=legs["52"]["both"]["loo_re"].get(k, float("nan")), loo52_both_fixed=legs["52"]["both"]["loo_fx"].get(k, float("nan")),
                         loo39_both_rehalved=legs["39"]["both"]["loo_re"].get(k, float("nan")), loo39_both_fixed=legs["39"]["both"]["loo_fx"].get(k, float("nan"))))
        say("  %-40s %5d %-6s %-19s %-19s %-7s %4d %-9s %-8s %s%s" % (k, n_of[k], "PASS" if counted else "PWI", profile_cls[k], record_cls[k], "YES" if differs else "no", len(U), "yes" if arg_diff else "no", arg[:8], U, "" if counted else "  [PWI: beside, not counted]"))
    med_size = float(np.median(sizes)) if sizes else float("nan")
    say("  D = %d of %d order-reliable strata whose undominated set differs from its source's; median |U_s| over the %d = %.1f; argmax differs from the source's in %d of %d strata (registered object: reserved side, MATH-FIX; %d argmax ties)"
        % (D, len(order_ok), len(order_ok), med_size, n_arg_diff52, len(strata), n_arg_tie))
    if mc_router is not None:
        say("  beside (labelled): MC-ROUTER's object replayed - argmax by TRAIN-side accuracy on its own per-(source, domain) 0.30 split (seed 42) over the %d-question corpus with the INGESTED MATH rows: %d of %d differ (FW L180 says 25)" % (mc_router["n"], mc_router["differs"], mc_router["strata"]))
    mm_rows = [r for r in rows if r["source"] == "MMLU_PRO_LB"]
    if mm_rows:
        say("  the 14 MMLU_PRO_LB strata against the MMLU_PRO_LB source (FW L179 predicts identical sets on p2dca's rosters; here the 18-model union key): %d of %d differ; argmax per stratum %s; source argmax %s"
            % (sum(1 for r in mm_rows if r["differs"] == 1), len(mm_rows), dict(Counter(r["argmax"] for r in mm_rows)), arg_src["MMLU_PRO_LB"][0]))
    say("  ROUTING-ATTENUATION (FW L183): these strata are DESIGNED (declared source x domain on the reserved side); the ~20% shrinkage applies to a routed deployment of the profile, not to these rows.")
    summary.update(D=D, med_size=med_size, n_arg_diff52=n_arg_diff52, rows=rows, U_src=U_src)

    # ---------- criteria ----------
    e39 = legs["39"]["both"]; e14 = legs["14"]["both"] if legs.get("14") else dict(R=float("nan"), lo_re=float("nan"), hi_re=float("nan"), lo_fx=float("nan"), hi_fx=float("nan"), halv_sd=float("nan"))
    say("")
    say("=== CRITERIA (in the registration's words) ===")
    say("  C1 'the 52-stratum interaction-only R reproduces 0.8537 to 4 dp (the gate)': %.4f -> HELD" % R52)
    c2c = c2_class(e39)
    say("  C2 'the 39-stratum interaction-only R with its jackknife interval is PUBLISHED': R = %.4f, re-halved jk [%.4f, %.4f], fixed jk [%.4f, %.4f], halving SD %.4f -> PUBLISHED; class %s (PASS if lower >= 0.70; PWI if point >= 0.70 and lower below; FAIL otherwise; re-halved primary)"
        % (e39["R"], e39["lo_re"], e39["hi_re"], e39["lo_fx"], e39["hi_fx"], e39["halv_sd"], c2c))
    say("  C3 'the 14 MMLU_PRO_LB strata's interaction-only R with interval PUBLISHED beside K12 / K46, rosters and pools named, no level claim': R = %.4f [%.4f, %.4f] re-halved, [%.4f, %.4f] fixed (18-model union roster, pool %s, 3,609 reserved q) beside K12 0.8665 [0.8000, 0.9330] and K46 0.8118 [0.7254, 0.8983] (p2dca, 2,811 judged q) -> PUBLISHED, no level claim"
        % (e14["R"], e14["lo_re"], e14["hi_re"], e14["lo_fx"], e14["hi_fx"], POOL))
    say("  C4 HOME COUNT: D = %d of %d" % (D, len(order_ok)))
    say("")
    say("=== VERDICT RULE (the plan's, 'the number decides') ===")
    if D >= 20:
        verdict = "D >= 20: the record may say 'the union strata are the profile's home: they carry an order-reliable key profile AND a routing consequence the sources do not'."
    elif D >= 10:
        verdict = "10 <= D < 20: the two objects are printed side by side and the author chooses (the paper leads with one, plan §5 q3)."
    else:
        verdict = "D < 10: the FALSIFIER F1 fires (below)."
    say("  D = %d of %d -> %s" % (D, len(order_ok), verdict))

    # ---------- predictions ----------
    say("")
    say("=== PREDICTIONS (the plan's R3 P1-P3 and the registrar's blind additions P4-P8, labelled; scored HELD / FAILED) ===")
    p1 = 0.80 <= e39["R"] <= 0.90; p2 = 0.80 <= e14["R"] <= 0.90; p3 = D >= 20
    say("  P1 (plan) 'interaction-only R over the 39 order-reliable strata in [0.80, 0.90]': %.4f -> %s" % (e39["R"], "HELD" if p1 else "FAILED"))
    say("  P2 (plan) 'the 14 MMLU_PRO_LB strata's interaction-only R in [0.80, 0.90]': %.4f -> %s" % (e14["R"], "HELD" if p2 else "FAILED"))
    say("  P3 (plan) 'D >= 20 of 39 undominated sets differ from the source's': %d -> %s" % (D, "HELD" if p3 else "FAILED"))
    e52 = legs["52"]["both"]; hw = (e52["hi_re"] - e52["lo_re"]) / 2; hwf = (e52["hi_fx"] - e52["lo_fx"]) / 2
    p4 = hw <= 0.06
    say("  P4 (registrar) 'the 52-stratum jackknife interval has half-width <= 0.06': re-halved %.4f (fixed %.4f) -> %s" % (hw, hwf, "HELD" if p4 else "FAILED"))
    p5 = summary["cov_ok"] >= 0.85
    say("  P5 (registrar) 'coverage of the 39 order-reliable strata >= 0.85 of %d': %.4f -> %s" % (n_pool, summary["cov_ok"], "HELD" if p5 else "FAILED"))
    bbh = legs.get("BBH"); p6 = bbh is not None and bbh["both"]["R"] < e39["R"]
    say("  P6 (registrar) 'BBH's 24-stratum interaction-only R < the 39-stratum reading': %s vs %.4f -> %s" % ("%.4f" % bbh["both"]["R"] if bbh else "undefined", e39["R"], "HELD" if p6 else "FAILED"))
    p7 = n_arg_diff52 == FW_ARGMAX_DIFFERS
    say("  P7 (registrar) 'the argmax-differs count over the 52 reproduces 25 exactly (the gate for (3))': %d on the registered object (reserved side, MATH-FIX) -> %s%s"
        % (n_arg_diff52, "HELD" if p7 else "FAILED", "" if p7 else "; FW L180's 25 is MC-ROUTER's train-side own-split ingested-MATH count (%s beside) - a different object, stated in inconsistency (b); (3) is delivered on the registered object and the registrar decides whether P7's 'gate' wording binds C4" % ("%d of %d" % (mc_router["differs"], mc_router["strata"]) if mc_router else "not replayed")))
    p8 = med_size >= 3
    say("  P8 (registrar) 'the median size of U_s over the 39 strata >= 3 models': %.1f -> %s" % (med_size, "HELD" if p8 else "FAILED"))
    say("")
    say("=== FALSIFIER (the plan's) ===")
    f1 = D < 10
    say("  F1 'D < 10 of 39': %s" % ("FIRES" if f1 else "silent"))
    if f1:
        say("  OVERTURNED: the plan's claim that the union strata are the profile's home because of their routing consequence; the strata add nothing to the ROUTER beyond the source")
        say("  (the source's undominated set is the stratum's in %d of %d); the home stays '14 anchors + 6 sources'; FW L180's '25 of 52 domains differ from their source's best' is bracketed as an argmax statement." % (len(order_ok) - D, len(order_ok)))
        say("  NOT overturned: the 52 strata's classes (PROFILE-INTERVAL-ALL-UNION stands), the routing gain +3.38pp (MC-E2E, a different instrument), the anchors' 0.8665.")
    say("  McNEMAR-ESTABLISHED RULE: wrong(established) applies to the undominated sets in (3) only; no judge direction exists here (both conventions n/a).")
    say("  runtime %.0fs, zero LLM calls" % (time.time() - t0))
    summary.update(c2c=c2c, p=(p1, p2, p3, p4, p5, p6, p7, p8), f1=f1, verdict=verdict)
    return L, rows, summary


# ----------------------------------------------------------------------------------------------- the CSV of record (classes)
def load_classes(path=STRATA_CSV):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    if len(rows) != piu.N_STRATA: raise SystemExit("[CLASSES] %s has %d rows, expected %d" % (path, len(rows), piu.N_STRATA))
    order = {r["key"]: r["cls_raw"] for r in rows}; prof = {r["key"]: r["cls"] for r in rows}
    cnt = Counter(order.values())
    if dict(cnt) != EXPECTED_ORDER: raise SystemExit("[CLASSES] order reading %s, expected %s" % (dict(cnt), EXPECTED_ORDER))
    if {k for k, v in order.items() if v == "FAIL"} != ORDER_FAIL: raise SystemExit("[CLASSES] the 5 order-FAIL strata differ from the record: %s" % sorted(k for k, v in order.items() if v == "FAIL"))
    return order, prof


def mc_router_replay(conn):
    """MC-ROUTER's argmax-differs count, its object: every corpus question with all 18 models (ingested rows, incl. MATH),
    per-(source, domain) split by random.Random(42) over sorted strata (ratio 0.30 to the reserved side), argmax by
    TRAIN-side accuracy, ties to the first model in name order (max() over ORDER BY model_name). Labelled beside; not the
    registered object."""
    Q = {q: (s, d) for q, s, d in conn.execute("SELECT question_id, source, domain FROM corpus_questions")}
    models = [m for (m,) in conn.execute("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")]
    G = defaultdict(dict)
    for q, m, c in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        G[q][m] = int(c)
    qs = sorted(q for q in Q if len(G[q]) == len(models))
    rng = random.Random(42); train = []
    by = defaultdict(list)
    for q in qs: by[Q[q]].append(q)
    for k, v in sorted(by.items()):
        v = v[:]; rng.shuffle(v); n = int(round(len(v) * 0.3)); train += v[n:]
    def best(qs_): return max(models, key=lambda m: sum(G[q][m] for q in qs_))
    s_best = {s: best([q for q in train if Q[q][0] == s]) for s in {Q[q][0] for q in train}}
    d_best = {k: best([q for q in train if Q[q] == k]) for k in by}
    return dict(n=len(qs), strata=len(by), differs=sum(1 for k in d_best if d_best[k] != s_best[k[0]]))


# ----------------------------------------------------------------------------------------------- modes
def header(mode):
    return ["reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL),
            "=== UNION-PROFILE-HOME: are the 39 order-reliable union strata or the 14 MMLU-Pro anchors the profile's home? (the numbers the choice needs) ===",
            "  registered 2026-09-19 (commit 8b3f6e2, docs/judge_v2_program.md L7926-L8063); zero calls; key only; every DB mode=ro; pool %s; %s" % (POOL, mode),
            "", "--- DATA CHECK (the object, before any stratum is read; profile_interval_union.data_check) ---"]


def dry_run():
    L = header("DRY RUN: counts, supports and checks only; no outcome number")
    strata = piu.load_strata()
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        ok, models = piu.data_check(conn, strata, L)
    finally:
        conn.close()
    ok &= piu.support_table(strata, L)
    order, prof = load_classes()
    src_of = lambda k: k.split("/", 1)[0]
    L.append("")
    L.append("  classes of record (%s): order reading %s; profile reading %s" % (os.path.basename(STRATA_CSV), dict(Counter(order.values())), dict(Counter(prof.values()))))
    ok39 = [k for k in strata if order[k] == "PASS"]
    L.append("  the 39 ORDER-RELIABLE strata: %d, %d reserved q of %d; per source %s" % (len(ok39), sum(len(strata[k]) for k in ok39), sum(len(v) for v in strata.values()),
             {s: "%d/%d" % (sum(1 for k in ok39 if src_of(k) == s), sum(1 for k in strata if src_of(k) == s)) for s in SOURCES}))
    L.append("  the 5 order-FAIL (no order, no undominated set): %s; the 8 order-PWI (beside, not counted): %s" % (sorted(k for k in strata if order[k] == "FAIL"), sorted(k for k in strata if order[k] == "PASS-WITH-INTERVAL")))
    L.append("  the 14 MMLU_PRO_LB strata: %d, %d reserved q" % (sum(1 for k in strata if src_of(k) == "MMLU_PRO_LB"), sum(len(strata[k]) for k in strata if src_of(k) == "MMLU_PRO_LB")))
    L.append("  roster (%d models): %s" % (len(models), ", ".join(models)))
    L.append("  gate on --run: the 52-stratum interaction-only R must reproduce %.4f to 4 dp (else the readout stops)" % GATE_R)
    L.append("  outputs on --run (written once): %s, %s" % (OUT_TXT, OUT_CSV))
    L.append("  existing outcome file: %s" % ("YES (--run will refuse)" if os.path.exists(OUT_TXT) else "no"))
    L.append("  DRY-RUN %s" % ("READY" if ok else "NOT READY: a data check failed"))
    print("\n".join(L))
    return 0 if ok else 1


def run():
    L = header("RUN")
    print("\n".join(L), flush=True)
    if os.path.exists(OUT_TXT):
        raise SystemExit("[ONCE] %s exists; the outcome is written once. Refusing." % OUT_TXT)
    strata = piu.load_strata()
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        ok, models = piu.data_check(conn, strata, L)
        ok &= piu.support_table(strata, L)
        if not ok:
            L.append("  DATA CHECK FAILED - stopping before any stratum is read; nothing written."); print("\n".join(L)); return 1
        K, models = piu.load_key(conn, strata, models)
        mc = mc_router_replay(conn)
    finally:
        conn.close()
    order, prof = load_classes()
    L.append("  roster (%d models): %s" % (len(models), ", ".join(models)))
    L.append("  KEY DENOMINATOR: each stratum's RESERVED questions of pool %s (n per row); key = is_correct (MATH: eval_results_mathfix only)." % POOL)
    L.append("  classes of record from %s: order %s, profile %s" % (os.path.basename(STRATA_CSV), dict(Counter(order.values())), dict(Counter(prof.values()))))
    body, rows, summary = analyse(strata, K, models, order, prof, [], mc_router=mc, log=lambda s: print(s, flush=True))
    L.extend(body)
    txt = "\n".join(L); print(txt)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_TXT, "w", encoding="utf-8", newline="\n") as f: f.write(txt + "\n")
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print("wrote %s and %s" % (OUT_TXT, OUT_CSV))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    """Synthetic 18-model key with planted structure: source A with 5 strata (3 order-PASS, one of them with the SAME undominated
    set as its source, two with a DIFFERENT one by a planted dominance; 1 order-PWI; 1 order-FAIL), sources B, C, D with 3 / 2 / 2
    strata. Checks: the gate stop on a wrong value, D counts the planted differences only, 'no order' rows carry no set, the
    interval brackets the point, the one-stratum source is undefined. Nothing of record is opened beyond the pool guard."""
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    print("=== UNION-PROFILE-HOME --selftest (synthetic) ===")
    rng = random.Random(11); rs = np.random.RandomState(11)
    models = ["m%02d" % i for i in range(N_MODELS)]
    ability = np.linspace(-1.5, 0.8, N_MODELS); ability[-1] = 3.0        # m17 clearly dominant: its set {m17} is the source's and every 'same' stratum's
    spec = [("A/same", 200, "same"), ("A/diff1", 250, "diff"), ("A/diff2", 250, "diff"), ("A/pwi", 120, "same"), ("A/fail", 80, "same"),
            ("B/b1", 150, "same"), ("B/b2", 150, "diff"), ("B/b3", 150, "same"), ("C/c1", 150, "same"), ("C/c2", 150, "same"), ("D/d1", 150, "same"), ("D/d2", 150, "same")]
    order = {"A/same": "PASS", "A/diff1": "PASS", "A/diff2": "PASS", "A/pwi": "PASS-WITH-INTERVAL", "A/fail": "FAIL", "B/b1": "PASS", "B/b2": "PASS", "B/b3": "PASS",
             "C/c1": "PASS", "C/c2": "PASS", "D/d1": "PASS", "D/d2": "PASS"}
    prof = {k: "PASS" for k in order}
    strata = {}; K = {}; qid = 1
    for key, n, kind in spec:
        dev = rs.normal(0, 0.4, N_MODELS); dev[-1] = 0.0
        for _ in range(n):
            diff = rs.normal(0, 1.0)
            p = 1 / (1 + np.exp(-(ability + dev - diff)))
            row = (rs.rand(N_MODELS) < p).astype(float)
            if kind == "diff":                              # planted dominance: m00 (the weakest) right on 99% of this stratum
                row[0] = float(rs.rand() < 0.995)
            K[qid] = row; strata.setdefault(key, []).append(qid); qid += 1
    saved = piu.SOURCES; piu.SOURCES = ("A", "B", "C", "D")
    global SOURCES, EXPECTED_ORDER
    SOURCES = ("A", "B", "C", "D")
    fails = []
    try:
        # the gate: a wrong value must stop the readout
        try:
            analyse(strata, K, models, order, prof, [], gate=0.1234, n_null=2); fails.append("gate did not stop on a wrong value")
        except SystemExit as e:
            print("  gate guard: %s" % e)
        # the gate at the true value: compute it first with the instrument of record
        qsel = set(q for v in strata.values() for q in v)
        r_, _, _ = pr.reliability(strata, qsel, piu.make_key_build(K, models), models, random.Random(SEED), min_cell=MIN_CELL, demean=pr.demean_two_way)
        L, rows, S = analyse(strata, K, models, order, prof, [], gate=float("%.4f" % sb(r_)), n_null=3, log=lambda s: print("  " + s, flush=True))
        print("\n".join(L))
    finally:
        piu.SOURCES = saved; SOURCES = saved
    byk = {r["key"]: r for r in rows}
    planted_diff = {"A/diff1", "A/diff2", "B/b2"}
    got_diff = {k for k, r in byk.items() if r["counted"] == 1 and r["differs"] == 1}
    if got_diff != planted_diff: fails.append("D should count exactly the planted dominances %s, got %s" % (sorted(planted_diff), sorted(got_diff)))
    if S["D"] != 3: fails.append("D should be 3, got %d" % S["D"])
    if byk["A/fail"]["U_s"] != "no order": fails.append("order-FAIL stratum should carry 'no order'")
    if byk["A/pwi"]["counted"] != 0: fails.append("order-PWI stratum must not be counted")
    for k in planted_diff:
        if byk[k]["U_s"] != "m00": fails.append("%s: planted dominance should give U_s = ['m00'], got %s" % (k, byk[k]["U_s"]))
    e39 = S["legs"]["39"]["both"]
    if not (e39["lo_re"] <= e39["R"] <= e39["hi_re"] and e39["lo_fx"] <= e39["R"] <= e39["hi_fx"]): fails.append("39-object interval does not bracket the point")
    if S["legs"]["A"] is None or S["legs"]["C"] is None: fails.append("multi-stratum sources should be defined")
    if S["verdict"].startswith("D < 10") is False: fails.append("verdict band should be D < 10 for D = 3")
    if not S["f1"]: fails.append("falsifier should fire at D = 3")
    # write-once
    scratch = os.path.join(os.environ.get("LOCALAPPDATA", ROOT), "Temp", "claude", "union_profile_home_selftest")
    os.makedirs(scratch, exist_ok=True); tmp = os.path.join(scratch, "outcome.txt"); open(tmp, "w").write("x\n")
    global OUT_TXT
    sv = OUT_TXT; OUT_TXT = tmp
    try:
        run(); fails.append("write-once did not refuse")
    except SystemExit:
        print("  write-once: refused an existing outcome file")
    finally:
        OUT_TXT = sv; os.remove(tmp)
    print("")
    if fails:
        print("SELFTEST FAILED:"); [print("  - " + f) for f in fails]; return 1
    print("SELFTEST OK: the gate stops on a wrong value and passes on the instrument's own value; D counts exactly the three planted dominances (one stratum keeps its")
    print("             source's set, two differ, one in B); 'no order' on the order-FAIL row; PWI not counted; intervals bracket the point; falsifier fires at D = 3; write-once refuses.")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="UNION-PROFILE-HOME (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true"); g.add_argument("--selftest", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest: return selftest()
    if a.dry_run: return dry_run()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
