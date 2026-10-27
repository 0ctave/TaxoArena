"""A-REDEFINE-REFIT — the widener's A over the cell's EVAL-side questions instead of its JUDGED questions.

  python tools/analysis/a_redefine_refit.py

REGISTERED BY REFERENCE (docs/plan_2026-09-15.md -> docs/design/FRAMEWORK.md "Tests to register before shipping",
commit 8d77f7b, item 2), quoted verbatim:

  "2. A-REDEFINE-REFIT. Refit b0, b1 with A over the cell's eval-side questions with extracted answers instead
  of judged questions, on the 891 and 920 edge sets. Criterion: LOAO wrong count and utility within one event
  / 5pp of the judged-question fit; b1 = 0 rejected on established labels. Prediction: parameters move by less
  than their CI width. 0 calls."

WHY (FRAMEWORK.md Stage 6): "A_ab(c) is redefined here over eval-side questions rather than judged questions:
systematic_budget.py:68-97 computes it over the anchor's judged questions, which under x12's uniform schedule were
a near-random 82% of the pool but under the filtered schedule of Stage 3 would be enriched for disagreement and
bias A downward on exactly the high-agreement pairs the widener budgets."

IMPLEMENTATION, fixed before the run:
  * Edge table: systematic_budget.build() (B = 300, Random(42), floor 200 matches per anchor), read from
    key_tie_decline's cache scratchpad/bigpic/ktd_x12_edges.pkl when present, else rebuilt; the committed
    counts (920/60 any gap, 891/44 at gap >= 0.02, raw 739/8 filtered, fit -3.2326/+3.3133) are asserted
    before anything is read. Meta-Llama-3-70B-Instruct is asserted absent.
  * ONLY A is redefined. p, m, s, right and gap stay exactly as build() made them (gap and the key direction
    are over the anchor's judged questions, as in the shipped fit), so "the 891 and 920 edge sets" are the
    same edges under both definitions.
  * A_judged = build()'s value: agreement over the anchor's judged questions where both models have a non-blank
    extracted answer (eval_results.pred). A_eval = the same statistic over the anchor's EVAL-side questions:
    the pool of record p2dca21ab5f4ef3ae (3,445 questions, reserved_pool table, read by explicit id) routed to
    the anchor by rubric_512.primary_routing("bareq512_s42"), restricted to questions where both models have a
    non-blank extracted answer. The judged set is asserted to be a subset of the eval-side set per anchor.
  * Fits, LOAO and utility exactly as systematic_budget.py / budget_lomo.py: sb.fit (Nelder-Mead on sb.nll),
    14 leave-one-anchor-out folds, x0 = the set's in-sample fit, call iff cbud >= 0.975, utility = called /
    edges. The judged-question baselines are recomputed HERE on the same code path (the 920-set LOAO figure
    646/3/1.28, 70.2% exists only in the review's scratch), and checked against the committed 891 figures.
  * Every wrong count prints as all(McNemar-established). KEY DENOMINATOR: systematic_budget.mcnemar_edge over
    anchor_qs[anchor] = the anchor's JUDGED questions (119-304 per anchor), the framework's ORDERED-rule
    denominator; the EVAL-side denominator (124-384 routed pool questions per anchor) is printed as a
    sensitivity, never as the primary.
  * Criterion 1, hardest reading: on EACH of the 891 and 920 sets, |LOAO wrong(all) - baseline| <= 1 AND
    |LOAO wrong(established) - baseline| <= 1 AND |utility - baseline| <= 5pp. Any one outside -> FAIL.
  * Criterion 2, "b1 = 0 rejected on established labels": established = sb.established(edges) (judged
    denominator), A = A_eval; primary test = profile likelihood ratio, dev(b1 = 0, b0 free) - dev(MLE) against
    chi-square(1) at 5% (this is the framework's own identification rule, Stage 6: "rejects b1 = 0 at
    delta-deviance 3.84"); secondary = 14-anchor cluster bootstrap P(b1 <= 0) < 0.025 (the derivation's own
    interval procedure), confirmed at 2,000 reps on a second seed. The item names no test, so the HARDEST
    reading is taken: PASS needs both; one rejecting and one not -> UNDETERMINED, and the verdict under the
    framework's registered rule alone is printed beside it. Read on both sets; the hardest reading requires both
    sets. The judged-A established refit (+2.1430 on 891) is printed beside it.
  * Prediction, "parameters move by less than their CI width": CI = the derivation's 14-anchor cluster bootstrap
    (600 reps, numpy default_rng(11), Nelder-Mead from (-3, 3)) on the judged-A fit of each set; it must
    reproduce b1 [1.72, 7.87] on 891 before it is used. Literal reading: |b_eval - b_judged| < (upper - lower)
    for BOTH b0 and b1. Stricter reading also printed: b_eval inside the judged-A CI. Because b0 and b1 co-vary
    at -0.99, tau at A = 0.30 / 0.60 / 0.88 is compared against its own bootstrap interval as well.
  * Bootstraps use a vectorised copy of sb.nll asserted equal to sb.nll at the MLE to 1e-6; results cached under
    scratchpad/block1/. No network, no LLM calls, no DB written, no other script modified.
"""
import os, sys, math, pickle, time, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm, chi2
import pool_guard
import rejudge_grok as rj
import rubric_512 as r512
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "a_redefine_refit.txt")
SCRATCH = os.path.join(r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad")
BLOCK1 = os.path.join(SCRATCH, "block1")
KTD_CACHE = os.path.join(SCRATCH, "bigpic", "ktd_x12_edges.pkl")
TREE = "bareq512_s42"
POOL = pool_guard.FROZEN_POOL_ID
EXCLUDE = "Meta-Llama-3-70B-Instruct"
THRESH = sb.THRESH
GAP = sb.GAP
ALPHA = 0.05
SHIPPED_891 = (-3.2326, 3.3133)
SHIPPED_920 = (-3.0438, 3.1980)
BOOT_REPS = 600
BOOT_SEED = 11
CI_891_B1 = (1.72, 7.87)
T0 = time.time()


def log(msg):
    print("[arr %5.0fs] %s" % (time.time() - T0, msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(BLOCK1, exist_ok=True)
    p = os.path.join(BLOCK1, name)
    if os.path.exists(p):
        log("cache hit %s" % name)
        return pickle.load(open(p, "rb"))
    log("building %s" % name)
    v = fn()
    pickle.dump(v, open(p, "wb"))
    return v


# ---------------------------------------------------------------- data
def load_edges():
    if os.path.exists(KTD_CACHE):
        log("reading key_tie_decline's cache %s" % KTD_CACHE)
        models, K, P, edges, aq = pickle.load(open(KTD_CACHE, "rb"))
        return models, dict(K), dict(P), edges, aq
    def build():
        models, K, P, by, edges, aq = sb.build()
        return models, dict(K), dict(P), edges, aq
    return cached("arr_x12_edges.pkl", build)


def eval_side_questions():
    """anchor -> sorted eval-side question ids: the pool of record routed by the promoted tree's primary assignment."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {r[0] for r in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id = ?", (POOL,))}
    ev.close()
    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anchor_of = r512.anchor_fn(nodes)
    assert set(route) == pool, "routing CSV (%d) is not the pool of record (%d)" % (len(route), len(pool))
    out = defaultdict(list)
    for q in sorted(route):
        out[anchor_of(route[q])].append(q)
    return dict(out), len(pool)


def agreement(P, qs, a, b):
    both = [q for q in qs if P.get(q, {}).get(a) and P.get(q, {}).get(b)]
    if not both:
        return None, 0
    return sum(1 for q in both if P[q][a] == P[q][b]) / len(both), len(both)


def with_A(es, key):
    return [dict(e, agree=e[key]) for e in es]


# ---------------------------------------------------------------- fitting helpers
def vec(es):
    return (np.array([e["agree"] for e in es], float), np.abs(np.array([e["m"] for e in es], float)),
            np.array([e["s"] for e in es], float), np.array([bool(e["right"]) for e in es]))


def vnll(par, A, M, S, R):
    tau = np.exp(np.minimum(20.0, par[0] + par[1] * A))
    pw = np.clip(norm.cdf(-M / np.sqrt(S ** 2 + tau ** 2)), 1e-12, 1 - 1e-12)
    return -float(np.sum(np.where(R, np.log(1 - pw), np.log(pw))))


def vfit(A, M, S, R, x0=(-3.0, 3.0)):
    r = minimize(vnll, np.array(x0, float), args=(A, M, S, R), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1])


def cluster_boot(es, reps=BOOT_REPS, seed=BOOT_SEED):
    """The derivation's interval: resample the 14 anchors with replacement, refit; returns arrays (b0, b1)."""
    ancs = sorted({e["anchor"] for e in es})
    bya = {a: [e for e in es if e["anchor"] == a] for a in ancs}
    rng = np.random.default_rng(seed)
    b0s = []; b1s = []; skipped = 0
    for _ in range(reps):
        pick = rng.choice(len(ancs), len(ancs), replace=True)
        sub = [e for i in pick for e in bya[ancs[i]]]
        A, M, S, R = vec(sub)
        if R.all():
            skipped += 1
            continue
        f0, f1 = vfit(A, M, S, R)
        b0s.append(f0); b1s.append(f1)
    return np.array(b0s), np.array(b1s), skipped


def pct(x, q):
    return float(np.percentile(x, q))


def loao(es, x0):
    """Leave-one-anchor-out out-of-fold budget confidence per edge, exactly as systematic_budget.py section (2)."""
    ancs = sorted({e["anchor"] for e in es})
    oof = {}; fits = {}
    for A_ in ancs:
        tr = [e for e in es if e["anchor"] != A_]
        te = [e for e in es if e["anchor"] == A_]
        f0, f1 = sb.fit(tr, x0=x0)
        fits[A_] = (f0, f1)
        for e in te:
            oof[id(e)] = sb.cbud(e, f0, f1)
    return oof, fits


def row(es, conf, K, aq, aq_eval):
    called = [e for e in es if conf[id(e)] >= THRESH]
    wrong = [e for e in called if not e["right"]]
    est = sb.established(wrong, K, aq)
    est_ev = sb.established(wrong, K, aq_eval)
    nom = sum(1 - conf[id(e)] for e in called)
    return dict(called=len(called), wrong=len(wrong), est=len(est), est_eval=len(est_ev), nom=nom,
                util=100.0 * len(called) / len(es), wrong_edges=wrong,
                called_keys={ekey(e) for e in called}, wrong_keys={ekey(e) for e in wrong})


def ekey(e):
    """Edge identity across the per-definition copies with_A() makes: (anchor, a, b)."""
    return (e["anchor"], e["a"], e["b"])


def fmt_row(label, r):
    return "  %-40s %7d %8d(%d)[%d] %9.2f %8s %8.1f%%" % (
        label, r["called"], r["wrong"], r["est"], r["est_eval"], r["nom"],
        ("%.1fx" % (r["wrong"] / r["nom"])) if r["nom"] > 0 else "-", r["util"])


def profile_lr(es):
    """Deviance at the MLE vs at b1 = 0 with b0 free; p from chi-square(1)."""
    A, M, S, R = vec(es)
    best = None
    for x0 in ((-3.0, 3.0), (-2.0, 0.0), (-4.0, 6.0), (-1.0, 1.0)):
        f0, f1 = vfit(A, M, S, R, x0)
        v = vnll((f0, f1), A, M, S, R)
        if best is None or v < best[0]:
            best = (v, f0, f1)
    v, f0, f1 = best
    r0 = minimize_scalar(lambda x: vnll((x, 0.0), A, M, S, R), bounds=(-30.0, 5.0), method="bounded")
    dd = 2.0 * (float(r0.fun) - v)
    return dict(b0=f0, b1=f1, dev=2 * v, dev0=2 * float(r0.fun), b0_at0=float(r0.x), ddev=dd,
                p=float(chi2.sf(max(dd, 0.0), 1)))


# ---------------------------------------------------------------- main
def main():
    L = []
    say = L.append
    say("=== A-REDEFINE-REFIT: A over the cell's EVAL-side questions with extracted answers, not its judged questions ===")
    say("  registered by reference: FRAMEWORK.md item 2 (commit 8d77f7b); 0 calls; pool of record %s" % POOL)
    say("  form unchanged: tau(A) = exp(b0 + b1*A); c~ = min(c_raw, Phi(|m|/sqrt(s^2+tau^2))); call iff c~ >= %.3f" % THRESH)

    # ---- edges and the committed checks
    models, K, P, edges_all, aq = load_edges()
    assert EXCLUDE not in models, "%s must be excluded" % EXCLUDE
    assert len(models) == 12
    filt = [e for e in edges_all if e["gap"] >= GAP]
    rc = [e for e in filt if sb.craw(e) >= THRESH]
    chk = (len(edges_all), sum(1 for e in edges_all if not e["right"]), len(filt),
           sum(1 for e in filt if not e["right"]), len(rc), sum(1 for e in rc if not e["right"]))
    say("")
    say("  DATA CHECK x12 edge table (systematic_budget.build via key_tie_decline's cache): %d edges any gap / %d wrong |"
        " %d at gap >= %.2f / %d wrong | raw 0.975 on filtered %d called / %d wrong" % (chk[:3] + (GAP,) + chk[3:]))
    assert chk == (920, 60, 891, 44, 739, 8), chk
    j0, j1 = sb.fit(filt)
    assert abs(j0 - SHIPPED_891[0]) < 2e-3 and abs(j1 - SHIPPED_891[1]) < 2e-3, (j0, j1)
    u0, u1 = sb.fit(edges_all)
    assert abs(u0 - SHIPPED_920[0]) < 2e-3 and abs(u1 - SHIPPED_920[1]) < 2e-3, (u0, u1)
    say("  judged-A fits reproduce: 891 b0 %+.4f b1 %+.4f (shipped %+.4f/%+.4f) | 920 b0 %+.4f b1 %+.4f (printed %+.4f/%+.4f)"
        % (j0, j1, SHIPPED_891[0], SHIPPED_891[1], u0, u1, SHIPPED_920[0], SHIPPED_920[1]))
    log("edge table checked; judged fits reproduced")

    # ---- eval-side questions
    aq_eval, npool = eval_side_questions()
    for anc in aq:
        assert set(aq[anc]) <= set(aq_eval[anc]), "judged questions of %s are not inside its eval-side set" % anc
    njudged = len({q for v in aq.values() for q in v})
    say("")
    say("  EVAL-SIDE CELLS: pool of record %s = %d questions, routed by %s primary assignment to 14 anchors;"
        % (POOL, npool, TREE))
    say("  judged questions %d = %.1f%% of the pool (the record's '82%%'); judged subset of eval-side asserted per anchor."
        % (njudged, 100.0 * njudged / npool))
    say("  %-18s %8s %8s %10s   %s" % ("anchor", "judged", "eval", "determ.", "determination = share of (q, model) with a non-blank extracted answer"))
    for anc in sorted(aq):
        qs = aq_eval[anc]
        det = sum(1 for q in qs for m in models if P.get(q, {}).get(m)) / (len(qs) * len(models))
        say("  %-18s %8d %8d %9.1f%%" % (anc, len(aq[anc]), len(qs), 100 * det))

    # ---- redefine A
    for e in edges_all:
        e["agree_judged"] = e["agree"]; e["n_judged"] = e["n"]
        a_ev, n_ev = agreement(P, aq_eval[e["anchor"]], e["a"], e["b"])
        assert a_ev is not None
        e["agree_eval"] = a_ev; e["n_eval"] = n_ev
    dA = np.array([e["agree_eval"] - e["agree_judged"] for e in edges_all])
    Aj = np.array([e["agree_judged"] for e in edges_all]); Ae = np.array([e["agree_eval"] for e in edges_all])
    say("")
    say("  A_eval vs A_judged over the %d edges: corr %.4f | mean diff %+.4f | median |diff| %.4f | p90 |diff| %.4f | max |diff| %.4f"
        % (len(edges_all), float(np.corrcoef(Aj, Ae)[0, 1]), float(dA.mean()), float(np.median(np.abs(dA))),
           pct(np.abs(dA), 90), float(np.abs(dA).max())))
    hi = [i for i, e in enumerate(edges_all) if e["agree_judged"] >= 0.80]
    say("  on the %d edges with A_judged >= 0.80 (the pairs the widener budgets hardest): mean diff %+.4f, range [%+.4f, %+.4f]"
        % (len(hi), float(dA[hi].mean()), float(dA[hi].min()), float(dA[hi].max())))
    say("  per-edge question support: judged median %d (min %d) -> eval-side median %d (min %d)"
        % (int(np.median([e["n_judged"] for e in edges_all])), min(e["n_judged"] for e in edges_all),
           int(np.median([e["n_eval"] for e in edges_all])), min(e["n_eval"] for e in edges_all)))
    say("  under x12's uniform schedule the judged questions are a near-random subset, so A should move little; the")
    say("  redefinition matters for the FILTERED schedule of Stage 3, which this test cannot see. The test is whether")
    say("  the parameters and the operating point are indifferent to the definition on the data that exist.")

    # ---- fits under both definitions on both sets
    sets = {"891 (gap >= 0.02)": filt, "920 (any gap)": edges_all}
    fits = {}
    say("")
    say("=== (1) THE REFIT, both definitions, both edge sets ===")
    say("  %-20s %-9s %10s %10s %9s | tau at A = 0.30 / 0.60 / 0.88" % ("set", "A over", "b0", "b1", "deviance"))
    for sname, es in sets.items():
        for key, lab in (("agree_judged", "judged"), ("agree_eval", "eval")):
            ez = with_A(es, key)
            b0, b1 = sb.fit(ez, x0=(-3.0, 3.0))
            fits[(sname, lab)] = (b0, b1)
            say("  %-20s %-9s %+10.4f %+10.4f %9.2f | %.3f / %.3f / %.3f"
                % (sname, lab, b0, b1, 2 * sb.nll((b0, b1), ez),
                   math.exp(b0 + 0.30 * b1), math.exp(b0 + 0.60 * b1), math.exp(b0 + 0.88 * b1)))
    log("point fits done")

    # ---- LOAO under both definitions on both sets
    say("")
    say("=== (2) LEAVE-ONE-ANCHOR-OUT (14 folds) at %.3f: the criterion's two numbers ===" % THRESH)
    say("  wrong = all(McNemar-established on the anchor's JUDGED questions)[established on the anchor's EVAL-side questions]")
    say("  KEY DENOMINATOR for the bracketed count: sb.mcnemar_edge over anchor_qs[anchor] = judged questions (%d-%d per anchor);"
        % (min(len(v) for v in aq.values()), max(len(v) for v in aq.values())))
    say("  the square-bracketed eval-side count (%d-%d routed pool questions per anchor) is a sensitivity only."
        % (min(len(v) for v in aq_eval.values()), max(len(v) for v in aq_eval.values())))
    say("  %-40s %7s %14s %9s %8s %9s" % ("set / A over / fold", "called", "wrong", "nominal", "ratio", "utility"))
    rows = {}
    for sname, es in sets.items():
        for key, lab in (("agree_judged", "judged"), ("agree_eval", "eval")):
            ez = with_A(es, key)
            b0, b1 = fits[(sname, lab)]
            ins = {id(e): sb.cbud(e, b0, b1) for e in ez}
            rows[(sname, lab, "in")] = row(ez, ins, K, aq, aq_eval)
            say(fmt_row("%s / %s / in sample" % (sname[:3], lab), rows[(sname, lab, "in")]))
            oof, ffits = loao(ez, (b0, b1))
            rows[(sname, lab, "loao")] = row(ez, oof, K, aq, aq_eval)
            rows[(sname, lab, "loao")]["fold_fits"] = ffits
            rows[(sname, lab, "loao")]["oof"] = oof
            rows[(sname, lab, "loao")]["edges"] = ez
            say(fmt_row("%s / %s / LOAO" % (sname[:3], lab), rows[(sname, lab, "loao")]))
            log("LOAO %s %s done" % (sname, lab))
        rr = [e for e in es if sb.craw(e) >= THRESH]; rw = [e for e in rr if not e["right"]]
        say("  %-40s %7d %8d(%d)[%d] %9s %8s %8.1f%%   (empirical called set; no nominal)"
            % ("%s / raw certificate" % sname[:3], len(rr), len(rw), len(sb.established(rw, K, aq)),
               len(sb.established(rw, K, aq_eval)), "-", "-", 100.0 * len(rr) / len(es)))
    b891 = rows[("891 (gap >= 0.02)", "judged", "loao")]
    say("  committed baseline check (systematic_budget.txt / budget_lomo.txt): 891 judged LOAO 663 / 3(2) / 1.27, 74.4%% -> here %d / %d(%d) / %.2f, %.1f%% %s"
        % (b891["called"], b891["wrong"], b891["est"], b891["nom"], b891["util"],
           "OK" if (b891["called"], b891["wrong"], b891["est"]) == (663, 3, 2) and abs(b891["nom"] - 1.27) < 0.01 else "MISMATCH"))
    b920 = rows[("920 (any gap)", "judged", "loao")]
    say("  review-scratch baseline (adv_budget.out, uncommitted): 920 judged LOAO 646 / 3 / 1.28, 70.2%% -> here %d / %d(%d) / %.2f, %.1f%% %s"
        % (b920["called"], b920["wrong"], b920["est"], b920["nom"], b920["util"],
           "OK" if (b920["called"], b920["wrong"]) == (646, 3) and abs(b920["nom"] - 1.28) < 0.01 else "MISMATCH"))

    # wrong calls and flips
    say("")
    say("  wrong calls out of fold, eval-side A (each with McNemar b:c and p on the judged denominator):")
    for sname in sets:
        r = rows[(sname, "eval", "loao")]
        if not r["wrong_edges"]:
            say("    %s: none" % sname)
        for e in sorted(r["wrong_edges"], key=lambda e: sb.mcnemar_edge(e, K, aq)[0]):
            p_, b_, c_ = sb.mcnemar_edge(e, K, aq); pe, be, ce = sb.mcnemar_edge(e, K, aq_eval)
            say("    %-18s %-16s %-26s vs %-26s c~=%.4f A_j=%.3f A_e=%.3f gap=%.4f | judged %d:%d p=%.4f %s | eval %d:%d p=%.4f"
                % (sname[:18], e["anchor"][:16], e["a"][:26], e["b"][:26], r["oof"][id(e)], e["agree_judged"], e["agree_eval"],
                   e["gap"], b_, c_, p_, "ESTABLISHED" if p_ < ALPHA else "unestablished", be, ce, pe))
    say("  call-set differences between the two definitions (LOAO), edges keyed by (anchor, a, b):")
    for sname in sets:
        rj_, re_ = rows[(sname, "judged", "loao")], rows[(sname, "eval", "loao")]
        only_j = rj_["called_keys"] - re_["called_keys"]; only_e = re_["called_keys"] - rj_["called_keys"]
        common = rj_["called_keys"] & re_["called_keys"]
        wj = len(only_j & rj_["wrong_keys"]); we = len(only_e & re_["wrong_keys"])
        say("    %-20s common %d | judged-only %d (%d wrong) | eval-only %d (%d wrong) | same wrong set: %s"
            % (sname, len(common), len(only_j), wj, len(only_e), we,
               "yes" if rj_["wrong_keys"] == re_["wrong_keys"] else "NO"))
        for k in sorted(only_j | only_e):
            e = next(x for x in rj_["edges"] if ekey(x) == k)
            say("      %-9s %-16s %-26s vs %-26s A_j=%.3f A_e=%.3f c~ judged %.4f / eval %.4f key %s"
                % ("judged" if k in only_j else "eval", k[0][:16], k[1][:26], k[2][:26], e["agree_judged"], e["agree_eval"],
                   rj_["oof"][id(e)], re_["oof"][id(next(x for x in re_["edges"] if ekey(x) == k))],
                   "right" if e["right"] else "WRONG"))

    # ---- criterion 1
    say("")
    say("=== CRITERION 1: LOAO wrong count within ONE EVENT and utility within 5pp of the judged-question fit ===")
    c1 = {}
    for sname in sets:
        rj_, re_ = rows[(sname, "judged", "loao")], rows[(sname, "eval", "loao")]
        d_all = re_["wrong"] - rj_["wrong"]; d_est = re_["est"] - rj_["est"]; d_u = re_["util"] - rj_["util"]
        ok = abs(d_all) <= 1 and abs(d_est) <= 1 and abs(d_u) <= 5.0
        c1[sname] = ok
        say("  %-20s wrong all %d -> %d (delta %+d) | established %d -> %d (delta %+d) | utility %.1f%% -> %.1f%% (delta %+.1fpp) | nominal %.2f -> %.2f -> %s"
            % (sname, rj_["wrong"], re_["wrong"], d_all, rj_["est"], re_["est"], d_est, rj_["util"], re_["util"], d_u,
               rj_["nom"], re_["nom"], "PASS" if ok else "FAIL"))
    say("  hardest reading (both sets, all-label AND established counts, both within one event; utility within 5pp): %s"
        % ("PASS" if all(c1.values()) else "FAIL"))

    # ---- criterion 2: b1 = 0 rejected on established labels
    say("")
    say("=== CRITERION 2: b1 = 0 rejected on ESTABLISHED labels, A over eval-side questions ===")
    say("  established = sb.established(edges, K, anchor_qs): exact McNemar p < %.2f on the anchor's judged questions." % ALPHA)
    say("  primary: profile likelihood ratio, dev(b1 = 0, b0 free) - dev(MLE) ~ chi2(1); secondary: 14-anchor cluster")
    say("  bootstrap P(b1 <= 0) (%d reps, seed %d). PASS needs both at 5%% / 2.5%%." % (BOOT_REPS, BOOT_SEED))
    c2 = {}; c2_lr = {}; c2_bt = {}
    est_sets = {sname: sb.established(es, K, aq) for sname, es in sets.items()}
    k891 = {ekey(e) for e in est_sets["891 (gap >= 0.02)"]}; k920 = {ekey(e) for e in est_sets["920 (any gap)"]}
    say("  established edges: 891-set %d, 920-set %d, identical sets: %s (every McNemar-established edge has key gap >= %.2f,"
        % (len(k891), len(k920), "yes" if k891 == k920 else "NO", GAP))
    say("  so the criterion is one test read twice; the two rows below are the same edges).")
    say("  %-20s %-7s %6s %6s %10s %10s %8s %8s %9s | %s" % ("set", "A over", "edges", "wrong", "b0", "b1", "ddev", "p(LR)", "P(b1<=0)", "b1 95% cluster CI"))
    for sname, es in sets.items():
        est = est_sets[sname]
        for key, lab in (("agree_judged", "judged"), ("agree_eval", "eval")):
            ez = with_A(est, key)
            pr = profile_lr(ez)
            A, M, S, R = vec(ez)
            assert abs(vnll((pr["b0"], pr["b1"]), A, M, S, R) - sb.nll((pr["b0"], pr["b1"]), ez)) < 1e-6
            b0s, b1s, sk = cached("arr_boot_est_%s_%s.pkl" % (sname[:3], lab), lambda: cluster_boot(ez))
            p_le0 = float((b1s <= 0).mean())
            b0c, b1c, skc = cached("arr_boot_est_%s_%s_r2000_s2026.pkl" % (sname[:3], lab),
                                   lambda: cluster_boot(ez, reps=2000, seed=2026))
            p_le0c = float((b1c <= 0).mean())
            lr_ok = pr["p"] < ALPHA; bt_ok = p_le0 < 0.025
            verdict = "PASS" if (lr_ok and bt_ok) else ("FAIL" if (not lr_ok and not bt_ok) else "UNDETERMINED (tests disagree)")
            if lab == "eval":
                c2[sname] = verdict; c2_lr[sname] = lr_ok; c2_bt[sname] = bt_ok
            say("  %-20s %-7s %6d %6d %+10.4f %+10.4f %8.2f %8.4f %9.4f | [%+.2f, %+.2f] (%d reps%s) -> %s"
                % (sname, lab, len(ez), sum(1 for e in ez if not e["right"]), pr["b0"], pr["b1"], pr["ddev"], pr["p"], p_le0,
                   pct(b1s, 2.5), pct(b1s, 97.5), len(b1s), (", %d all-right draws skipped" % sk) if sk else "",
                   verdict if lab == "eval" else "(reference)"))
            say("  %-20s %-7s confirmation bootstrap 2000 reps seed 2026: P(b1 <= 0) %.4f | b1 95%% CI [%+.2f, %+.2f]%s"
                % ("", "", p_le0c, pct(b1c, 2.5), pct(b1c, 97.5), (" | %d all-right draws skipped" % skc) if skc else ""))
            log("criterion 2 %s %s done" % (sname, lab))
    say("  committed reference: 891 established refit with judged A gave b1 = +2.1430 (systematic_budget.txt section 4).")
    say("  READINGS. (a) The framework's own identification rule (Stage 6: 'rejects b1 = 0 at delta-deviance 3.84', the")
    say("      Mistral board's 5.22 established): profile delta-deviance on eval-side A -> %s."
        % ("PASS (both sets)" if all(c2_lr.values()) else "FAIL"))
    say("      (b) Hardest reading, the derivation's own interval procedure (14-anchor cluster bootstrap, two-sided 5%):")
    say("      P(b1 <= 0) must be < 0.025 -> %s. The judged-A reference rows carry the SAME disagreement, so this is a"
        % ("PASS" if all(c2_bt.values()) else "NOT REJECTED"))
    say("      property of the established-label fit (26 wrong events, 14 clusters), not of the redefinition.")
    say("  hardest reading (both tests reject on both sets): %s"
        % ("PASS" if all(v == "PASS" for v in c2.values()) else
           ("FAIL" if any(v == "FAIL" for v in c2.values()) else "UNDETERMINED")))

    # ---- prediction: parameters move by less than their CI width
    say("")
    say("=== PREDICTION: parameters move by less than their CI width ===")
    say("  CI = the derivation's interval procedure (14-anchor cluster bootstrap, %d reps, numpy default_rng(%d), Nelder-Mead" % (BOOT_REPS, BOOT_SEED))
    say("  from (-3, 3)) on the JUDGED-A fit of each set; the 891 interval must reproduce b1 [%.2f, %.2f] first." % CI_891_B1)
    pred = {}
    for sname, es in sets.items():
        ez = with_A(es, "agree_judged")
        A, M, S, R = vec(ez)
        bj0, bj1 = fits[(sname, "judged")]
        assert abs(vnll((bj0, bj1), A, M, S, R) - sb.nll((bj0, bj1), ez)) < 1e-6
        b0s, b1s, sk = cached("arr_boot_all_%s_judged.pkl" % sname[:3], lambda: cluster_boot(ez))
        lo0, hi0 = pct(b0s, 2.5), pct(b0s, 97.5); lo1, hi1 = pct(b1s, 2.5), pct(b1s, 97.5)
        be0, be1 = fits[(sname, "eval")]
        d0, d1 = be0 - bj0, be1 - bj1
        lit = abs(d0) < (hi0 - lo0) and abs(d1) < (hi1 - lo1)
        strict = (lo0 <= be0 <= hi0) and (lo1 <= be1 <= hi1)
        pred[sname] = (lit, strict)
        say("  %-20s judged-A b0 %+.4f CI [%+.3f, %+.3f] width %.3f | b1 %+.4f CI [%+.3f, %+.3f] width %.3f | P(b1<=0) %.4f%s"
            % (sname, bj0, lo0, hi0, hi0 - lo0, bj1, lo1, hi1, hi1 - lo1, float((b1s <= 0).mean()),
               (" | %d all-right draws skipped" % sk) if sk else ""))
        if sname.startswith("891"):
            rep = abs(lo1 - CI_891_B1[0]) < 0.02 and abs(hi1 - CI_891_B1[1]) < 0.02
            say("  %-20s reproduction of the recorded b1 CI [%.2f, %.2f]: %s" % ("", CI_891_B1[0], CI_891_B1[1], "OK" if rep else "MISMATCH [%.2f, %.2f]" % (lo1, hi1)))
        say("  %-20s eval-A   b0 %+.4f (delta %+.4f = %.0f%% of width) | b1 %+.4f (delta %+.4f = %.0f%% of width) -> literal %s; inside the judged CI %s"
            % ("", be0, d0, 100 * abs(d0) / (hi0 - lo0), be1, d1, 100 * abs(d1) / (hi1 - lo1),
               "HELD" if lit else "FAILED", "yes" if strict else "no"))
        for a_ in (0.30, 0.60, 0.88):
            t = np.exp(b0s + b1s * a_)
            tj = math.exp(bj0 + bj1 * a_); te = math.exp(be0 + be1 * a_)
            say("  %-20s tau(A=%.2f): judged %.3f CI [%.3f, %.3f] | eval %.3f -> %s"
                % ("", a_, tj, pct(t, 2.5), pct(t, 97.5), te, "inside" if pct(t, 2.5) <= te <= pct(t, 97.5) else "OUTSIDE"))
        log("prediction %s done" % sname)
    say("  literal reading (|delta| < CI width, both parameters, both sets): %s" % ("HELD" if all(v[0] for v in pred.values()) else "FAILED"))
    say("  strict reading (eval-A point inside the judged-A CI, both parameters, both sets): %s" % ("HELD" if all(v[1] for v in pred.values()) else "FAILED"))

    # ---- verdict
    say("")
    say("=== VERDICT ===")
    say("  criterion 1 (LOAO wrong within one event, utility within 5pp; both sets): %s" % ("PASS" if all(c1.values()) else "FAIL"))
    say("  criterion 2 (b1 = 0 rejected on established labels, eval-side A; both sets): %s"
        % ("PASS" if all(v == "PASS" for v in c2.values()) else ("FAIL" if any(v == "FAIL" for v in c2.values()) else "UNDETERMINED")))
    say("      under the framework's registered identification rule (profile delta-deviance > 3.84): %s;"
        % ("PASS" if all(c2_lr.values()) else "FAIL"))
    say("      under the anchor-clustered bootstrap (hardest reading): %s"
        % ("rejected" if all(c2_bt.values()) else "not rejected at two-sided 5%; identical on the judged-A reference"))
    say("  prediction (parameters move by less than their CI width): %s (literal) / %s (strict)"
        % ("HELD" if all(v[0] for v in pred.values()) else "FAILED", "HELD" if all(v[1] for v in pred.values()) else "FAILED"))
    say("  what this test cannot say: whether A_eval differs from A_judged under a FILTERED schedule - x12's schedule is")
    say("  uniform, so the two definitions are near-identical here by construction; the refit is a consistency check on")
    say("  the parameters, not evidence about Stage 3. Calibration at the operating point stays UNDETERMINED (nominal < 3).")
    say("  runtime %.0f s; no LLM calls; no DB written; caches under %s" % (time.time() - T0, BLOCK1))

    txt = "\n".join(L)
    print(txt)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
