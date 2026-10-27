"""JUDGE-TRANSFER — does the widener transfer across JUDGE families? (registered 2026-09-15 at 60cb7f3, zero calls)

  python tools/analysis/judge_transfer.py

REGISTERED TEXT (docs/judge_v2_program.md, "### C. JUDGE-TRANSFER"), quoted:
  "Roster transfer is undetermined. Judge transfer has not been asked and is cheaper to power: the grok judge
   cache stack_v2_kit2_grok.db carries 3,948 verdicts on 1,371 x12 questions across all 66 pairs, in two arms
   (the arm without the leaf card is used, so the recipe matches the x12 Mistral cache). Fit tau on Mistral x12
   (the shipped b0, b1), apply COLD to per-anchor edges built from grok verdicts; also refit on grok.
   DATA CHECK FIRST: with ~100 questions per anchor the per-anchor floor of 200 matches will not be met
   everywhere; report which anchors qualify at a 100-match floor and run only those, said plainly.
   CRITERIA: (1) realised wrong-direction rate (all / established) against nominal on the grok edges with the
   Mistral parameters; (2) b1 refit on grok inside the Mistral anchor-clustered CI [1.72, 7.87]; (3) utility.
   PREDICTION: b1 refit on grok lands inside the CI (widening with agreement is a judge-family property) and the
   cold ratio is 1.5-3x on established labels - the same band as in-roster. FALSIFIER: b1 refit outside the CI
   or a cold ratio above 5x on established labels means the parameter is Mistral-specific and must be published
   so. Expected to be UNDERPOWERED at the operating point; the b1 criterion is the one with power."

IMPLEMENTATION, held to the registration:
  * Edges are built EXACTLY as systematic_budget.build(): per anchor, 300 question-resampled boards with
    random.Random(42) in sorted-anchor order, judge_free_tests.board_from, key gap > 0 stored and the fit /
    scoring population filtered at key gap >= 0.02 (GAP), agreement from eval_results.pred as build() does.
    The ONLY change is the match floor: 100 instead of 200 (registered), and the verdict source.
  * Verdict source: the grok arm WITHOUT the leaf card. In rubric_kit2.judge() the card is appended only for
    arm in ("datacard", "reasoned"); the base arm "stackv2_<variant>" is plain STACK-v2. The two arm labels and
    their counts are printed from the DB before anything is read into edges.
  * Every wrong count carries its McNemar-established count via systematic_budget.mcnemar_edge /
    established() on anchor_qs = the anchor's GROK-JUDGED questions (the key denominator). A secondary line
    uses the Mistral x12 judged questions as denominator, labelled, because it is the larger set and a reader
    will ask.
  * Mistral parameters: systematic_budget.fit on the 891 filtered x12 edges (cached build; the shipped values
    are -3.2326 / +3.3133 and the script asserts the refit reproduces them to 1e-3).
  * Underpowered readings follow budget_transfer's pre-committed rule: a nominal below 3.0 expected wrong calls
    cannot be told from calibrated -> UNDETERMINED, unless an exact Poisson tail P(X >= observed | nominal)
    is below 0.05, in which case the excess is real at that support and the falsifier fires.
"""
import os, sys, math, random, sqlite3, pickle, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import norm, poisson
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import judge_free_tests as jf
import pool_guard
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "judge_transfer.txt")
GROK = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_kit2_grok.db")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Temp", "claude",
                       "Z--FAC-TUBerlin-THESIS-TaxoArena", "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "bigpic")
B = sb.B                 # 300
THRESH = sb.THRESH       # 0.975
GAP = sb.GAP             # 0.02
FLOOR = 100              # registered: the 200 floor is not met everywhere on ~100 questions per anchor
CI = (1.72, 7.87)        # the Mistral anchor-clustered CI on b1, registered
SHIPPED = (-3.2326, 3.3133)
EXCLUDE = {"Meta-Llama-3-70B-Instruct"}


def load_keys(models):
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in models:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    return K, P


def inspect_arms(L):
    con = sqlite3.connect("file:%s?mode=ro" % GROK, uri=True)
    arms = con.execute("SELECT arm, COUNT(*), COUNT(DISTINCT qid), COUNT(DISTINCT match_id), SUM(invalid) "
                       "FROM verdicts GROUP BY arm ORDER BY arm").fetchall()
    npair = con.execute("SELECT COUNT(*) FROM (SELECT DISTINCT model_a, model_b FROM verdicts)").fetchone()[0]
    nq = con.execute("SELECT COUNT(DISTINCT qid) FROM verdicts").fetchone()[0]
    L.append("=== DATA CHECK: the grok cache %s ===" % os.path.basename(GROK))
    L.append("  %d verdicts total on %d distinct questions, %d (model_a, model_b) orderings"
             % (sum(a[1] for a in arms), nq, npair))
    for arm, n, q, m, inv in arms:
        L.append("  arm %-18s %5d verdicts | %4d questions | %4d matches | invalid %d" % (arm, n, q, m, inv or 0))
    L.append("  rubric_kit2.judge(): the leaf data card is appended only when arm in ('datacard', 'reasoned');")
    L.append("  'stackv2_datacard' is the base STACK-v2 prompt with NO card -> that arm is used here.")
    arm = "stackv2_datacard"
    assert arm in {a[0] for a in arms}, "expected arm %s not found" % arm
    rows = [r for r in con.execute("SELECT model_a, model_b, qid, winner, invalid, anchor FROM verdicts WHERE arm=?", (arm,))
            if not r[4]]
    con.close()
    return arm, rows


def build_edges(rows, models, K, P, floor, L, db_anchor):
    """Copy of systematic_budget.build()'s edge loop with the match floor as a parameter. Nothing else differs."""
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list); mism = 0; unrouted = 0
    for a, b, q, w, _, anc_db in rows:
        if q in route:
            anc = anchor_of(route[q])
            if anc != anc_db: mism += 1
            by[anc].append((a, b, q, w))
        else:
            unrouted += 1
    L.append("  routed by rubric_512.primary_routing('bareq512_s42') like build(): %d rows routed, %d unrouted, "
             "%d disagree with the DB's anchor column" % (sum(len(v) for v in by.values()), unrouted, mism))
    L.append("")
    L.append("  per-anchor matches in the card-free arm, against the 200 floor build() uses and the registered 100 floor:")
    L.append("  %-18s %8s %10s %8s %8s" % ("anchor", "matches", "questions", ">=200", ">=100"))
    qual = []
    for anc in sorted(by):
        rs = by[anc]; nq = len({q for _, _, q, _ in rs})
        L.append("  %-18s %8d %10d %8s %8s" % (anc, len(rs), nq, "yes" if len(rs) >= 200 else "no",
                                                "yes" if len(rs) >= floor else "NO"))
        if len(rs) >= floor: qual.append(anc)
    L.append("  qualify at the %d floor: %d of %d anchors -> %s" % (floor, len(qual), len(by), ", ".join(qual)))
    L.append("  excluded: %s" % ", ".join(a for a in sorted(by) if a not in qual))
    L.append("  qualify at the 200 floor build() uses: %s" % ", ".join(a for a in sorted(by) if len(by[a]) >= 200))

    rng = random.Random(42)                      # same seed and draw order as systematic_budget.build()
    anchor_qs = {}; edges = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < floor:
            continue
        qs = sorted({q for _, _, q, _ in rs})
        anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                        for a, b, _, w in sub], models))
        la = {}
        for m in models:
            v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la:
                    continue
                gap = abs(la[a] - la[b])
                if gap == 0:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=len(both)))
    return edges, anchor_qs, by


def mistral_build():
    """systematic_budget.build(), cached under the scratchpad so a checker can reuse it (~10 min uncached)."""
    os.makedirs(SCRATCH, exist_ok=True)
    pk = os.path.join(SCRATCH, "mistral_build.pkl")
    if os.path.exists(pk):
        d = pickle.load(open(pk, "rb"))
        return d["models"], d["K"], d["P"], d["edges"], d["anchor_qs"], "cached %s" % pk
    t = time.time()
    models, K, P, by, edges, anchor_qs = sb.build()
    pickle.dump(dict(models=models, K=dict(K), P=dict(P), edges=edges, anchor_qs=anchor_qs), open(pk, "wb"))
    return models, K, P, edges, anchor_qs, "built in %.0fs and cached to %s" % (time.time() - t, pk)


def block(L, name, es, K, aq, b0, b1):
    """Same layout as budget_transfer.block: wrong counts as all(established), nominal, ratio; then established-only."""
    if not es:
        L.append("  %-14s no edges" % name); return None
    rc = [e for e in es if sb.craw(e) >= THRESH]
    bc = [e for e in es if sb.cbud(e, b0, b1) >= THRESH]
    rw = [e for e in rc if not e["right"]]; bw = [e for e in bc if not e["right"]]
    rwe = len(sb.established(rw, K, aq)); bwe = len(sb.established(bw, K, aq))
    nom = sum(1 - sb.cbud(e, b0, b1) for e in bc)
    est_c = sb.established(bc, K, aq)
    nom_e = sum(1 - sb.cbud(e, b0, b1) for e in est_c)
    L.append("  %-14s %6d %8d %6d(%d) %9d %6d(%d) %8.2f %7s | established only: %d called, %d wrong, %.2f nom = %s"
             % (name, len(es), len(rc), len(rw), rwe, len(bc), len(bw), bwe, nom,
                ("%.1fx" % (len(bw) / nom)) if nom > 0 else "-",
                len(est_c), bwe, nom_e, ("%.1fx" % (bwe / nom_e)) if nom_e > 0 else "-"))
    return dict(edges=len(es), rc=len(rc), rw=len(rw), rwe=rwe, bc=len(bc), bw=len(bw), bwe=bwe, nom=nom,
                est_c=len(est_c), nom_e=nom_e)


def fit_best(es, starts):
    """systematic_budget.fit from several starts; keep the lowest deviance (Nelder-Mead is local)."""
    best = None
    for x0 in starts:
        print("  [fit] %d edges from %s" % (len(es), x0), file=sys.stderr, flush=True)
        b0, b1 = sb.fit(es, x0=x0)
        v = sb.nll((b0, b1), es)
        if best is None or v < best[2]:
            best = (b0, b1, v)
    return best


def fast_fit(es, x0):
    """Vectorised twin of systematic_budget.nll/fit (same clamp, clipping, optimiser and tolerances), used ONLY
    for the informational bootstrap; the registered point refits go through sb.fit itself."""
    from scipy.optimize import minimize
    A = np.array([e["agree"] for e in es]); M = np.abs([e["m"] for e in es]); S = np.array([e["s"] for e in es])
    R = np.array([bool(e["right"]) for e in es])
    def nll(par):
        tau = np.exp(np.minimum(20.0, par[0] + par[1] * A))
        pw = np.clip(norm.cdf(-M / np.sqrt(S ** 2 + tau ** 2)), 1e-12, 1 - 1e-12)
        return -float(np.sum(np.where(R, np.log(1 - pw), np.log(pw))))
    r = minimize(nll, np.array(x0), method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1]), float(r.fun)


def fast_nll(es):
    A = np.array([e["agree"] for e in es]); M = np.abs([e["m"] for e in es]); S = np.array([e["s"] for e in es])
    R = np.array([bool(e["right"]) for e in es])
    def nll(b0, b1):
        tau = np.exp(np.minimum(20.0, b0 + b1 * A))
        pw = np.clip(norm.cdf(-M / np.sqrt(S ** 2 + tau ** 2)), 1e-12, 1 - 1e-12)
        return -float(np.sum(np.where(R, np.log(1 - pw), np.log(pw))))
    return nll


def profile(es, grid):
    """Profile deviance 2*min_b0 nll(b0, b1) on a b1 grid (b0 bounded at -30, where tau is already ~0)."""
    from scipy.optimize import minimize_scalar
    f = fast_nll(es)
    return {b1: 2 * minimize_scalar(lambda b0: f(b0, b1), bounds=(-30.0, 5.0), method="bounded").fun for b1 in grid}


def degenerate(b0, b1):
    """The MLE ran to tau -> 0 everywhere (no widener): b1 is then not an estimate of anything."""
    return math.exp(b0 + b1 * 1.0) < 1e-3 and math.exp(b0) < 1e-3


def anchor_cluster_ci(es, starts, reps=200, seed=7):
    """Anchor-clustered bootstrap of the b1 refit (resample anchors with replacement). Informational only:
    the registered criterion is the point refit against the Mistral CI."""
    rng = random.Random(seed)
    ancs = sorted({e["anchor"] for e in es}); byA = {a: [e for e in es if e["anchor"] == a] for a in ancs}
    out = []
    for i in range(reps):
        pick = [ancs[rng.randrange(len(ancs))] for _ in ancs]
        sub = [e for a in pick for e in byA[a]]
        if not any(not e["right"] for e in sub):
            continue                       # no wrong edge at all: b1 is unidentified in that replicate
        best = min((fast_fit(sub, x0) for x0 in starts), key=lambda t: t[2])
        out.append(best[1])
        if (i + 1) % 50 == 0: print("  [ci] %d/%d" % (i + 1, reps), file=sys.stderr, flush=True)
    out.sort()
    return out


def main():
    L = []
    L.append("=== JUDGE-TRANSFER: does tau(A) = exp(b0 + b1*A), fitted on Mistral x12, transfer to a grok judge? ===")
    L.append("  registered 2026-09-15 at 60cb7f3; zero calls; verdicts read from the existing grok cache only.")
    L.append("")
    models = sorted(m for m in p8.ARENA12 if m not in EXCLUDE)
    assert not (set(p8.ARENA12) & EXCLUDE), "excluded model present in ARENA12"
    K, P = load_keys(set(models))

    # ---- data check first, as registered ----
    arm, rows = inspect_arms(L)
    bad = [r for r in rows if r[0] not in models or r[1] not in models]
    assert not bad, "verdict rows on models outside the 12-model roster: %d" % len(bad)
    L.append("  using arm %s: %d valid verdicts on %d questions, %d unordered pairs"
             % (arm, len(rows), len({r[2] for r in rows}), len({tuple(sorted(r[:2])) for r in rows})))
    L.append("  Meta-Llama-3-70B-Instruct: excluded everywhere (not in the roster; asserted).")
    L.append("")
    print("  [stage] building grok edges", file=sys.stderr, flush=True)
    edges_g, aq_g, by_g = build_edges(rows, models, K, P, FLOOR, L, True)
    print("  [stage] grok edges built: %d" % len(edges_g), file=sys.stderr, flush=True)
    filt_g = [e for e in edges_g if e["gap"] >= GAP]
    L.append("")
    L.append("  grok edges (key gap > 0): %d, of which %d wrong-direction | key gap >= %.2f: %d, %d wrong"
             % (len(edges_g), sum(1 for e in edges_g if not e["right"]), GAP, len(filt_g),
                sum(1 for e in filt_g if not e["right"])))
    L.append("  bootstrap: %d question-resampled boards per anchor, Random(42) in sorted-anchor order, board_from, as build()." % B)
    L.append("  KEY DENOMINATOR for every McNemar below: the anchor's GROK-JUDGED questions (anchor_qs from this arm),")
    L.append("  %d questions over the %d qualifying anchors; agreement from eval_results.pred over those same questions."
             % (sum(len(v) for v in aq_g.values()), len(aq_g)))
    pickle.dump(dict(edges=edges_g, anchor_qs=aq_g), open(os.path.join(SCRATCH, "grok_edges_floor%d.pkl" % FLOOR), "wb"))

    # ---- the Mistral parameters ----
    models_m, K_m, P_m, edges_m, aq_m, how = mistral_build()
    assert models_m == models
    filt_m = [e for e in edges_m if e["gap"] >= GAP]
    b0, b1 = sb.fit(filt_m)
    L.append("")
    L.append("=== THE MISTRAL PARAMETERS (systematic_budget.build + fit on the %d filtered x12 edges; %s) ===" % (len(filt_m), how))
    L.append("  b0 = %+.4f | b1 = %+.4f | shipped %+.4f / %+.4f -> %s"
             % (b0, b1, SHIPPED[0], SHIPPED[1], "reproduced" if abs(b0 - SHIPPED[0]) < 1e-3 and abs(b1 - SHIPPED[1]) < 1e-3 else "DIFFERS"))
    assert abs(b0 - SHIPPED[0]) < 1e-3 and abs(b1 - SHIPPED[1]) < 1e-3, "shipped parameters not reproduced"
    L.append("  in-roster reference (x12, Mistral, in sample), same columns as below:")
    L.append("  %-14s %6s %8s %9s %9s %9s %8s %7s" % ("set", "edges", "rawcall", "wrong", "budcall", "wrong", "nominal", "ratio"))
    ref = block(L, "x12 Mistral", filt_m, K_m, aq_m, b0, b1)

    # ---- (1) cold application on grok ----
    L.append("")
    L.append("=== (1) COLD: the Mistral parameters applied unchanged to the grok edges, called iff c_bud >= %.3f ===" % THRESH)
    L.append("  wrong counts are all(McNemar-established) on the anchor's grok-judged questions.")
    L.append("  %-14s %6s %8s %9s %9s %9s %8s %7s" % ("set", "edges", "rawcall", "wrong", "budcall", "wrong", "nominal", "ratio"))
    cold = block(L, "grok, all", filt_g, K, aq_g, b0, b1)
    for anc in sorted(aq_g):
        block(L, anc[:14], [e for e in filt_g if e["anchor"] == anc], K, aq_g, b0, b1)
    sub200 = [e for e in filt_g if len(by_g[e["anchor"]]) >= 200]
    L.append("  subset of the above on the anchors that would also clear the 200 floor (not a rerun; same per-anchor draws):")
    block(L, ">=200 anchors", sub200, K, aq_g, b0, b1)
    L.append("  sensitivity, SECONDARY denominator = the Mistral x12 judged questions of the anchor (larger set, more power to establish):")
    aq_alt = {a: aq_m[a] for a in aq_g if a in aq_m}
    alt = block(L, "grok, x12-den", [e for e in filt_g if e["anchor"] in aq_alt], K, aq_alt, b0, b1)

    ratio_all = cold["bw"] / cold["nom"] if cold["nom"] > 0 else float("nan")
    ratio_est = cold["bwe"] / cold["nom_e"] if cold["nom_e"] > 0 else float("nan")
    p_tail_est = float(poisson.sf(cold["bwe"] - 1, cold["nom_e"])) if cold["nom_e"] > 0 else float("nan")
    p_tail_all = float(poisson.sf(cold["bw"] - 1, cold["nom"])) if cold["nom"] > 0 else float("nan")
    L.append("")
    L.append("  (1) realised against nominal, cold:")
    L.append("      ALL labels:         %d wrong of %d called vs nominal %.2f -> ratio %.2fx | Poisson P(X >= %d | %.2f) = %.3f"
             % (cold["bw"], cold["bc"], cold["nom"], ratio_all, cold["bw"], cold["nom"], p_tail_all))
    L.append("      ESTABLISHED labels: %d wrong of %d called vs nominal %.2f -> ratio %.2fx | Poisson P(X >= %d | %.2f) = %.3f"
             % (cold["bwe"], cold["est_c"], cold["nom_e"], ratio_est, cold["bwe"], cold["nom_e"], p_tail_est))
    L.append("      registered band 1.5-3x on established labels; falsifier > 5x on established labels.")
    if cold["nom_e"] >= 3.0:
        v1 = "FAIL (falsifier: > 5x on established labels)" if ratio_est > 5.0 else "PASS (at or below 5x; %s the 1.5-3x band)" % ("inside" if 1.5 <= ratio_est <= 3.0 else "outside")
    elif p_tail_est < 0.05:
        v1 = "FAIL (nominal %.2f < 3 but the observed excess is significant, Poisson p = %.3f)" % (cold["nom_e"], p_tail_est)
    else:
        v1 = "UNDETERMINED (nominal %.2f < 3 expected wrong calls on established labels: %d observed cannot be told from calibrated; Poisson p = %.3f)" % (cold["nom_e"], cold["bwe"], p_tail_est)
    L.append("      -> criterion (1): %s" % v1)
    L.append("      rule: budget_transfer's pre-committed reading (nominal < 3 -> UNDETERMINED) with the one addition that a")
    L.append("      significant Poisson excess at low nominal fires the falsifier rather than hiding behind the power caveat.")

    # ---- (2) refit on grok ----
    L.append("")
    L.append("=== (2) REFIT ON GROK: b1 against the Mistral anchor-clustered CI [%.2f, %.2f] ===" % CI)
    starts = [(b0, b1), (-3.0, 3.0), (-2.0, 0.0), (-4.0, 6.0)]
    g0, g1, gv = fit_best(filt_g, starts)
    est_g = sb.established(filt_g, K, aq_g)
    n_wrong_est = sum(1 for e in est_g if not e["right"])
    e0, e1, ev_ = fit_best(est_g, starts) if len(est_g) > 100 else (float("nan"), float("nan"), float("nan"))
    L.append("  same construction as the shipped fit (all labels, key gap >= %.2f, %d edges, %d wrong):" % (GAP, len(filt_g), sum(1 for e in filt_g if not e["right"])))
    L.append("    b0 = %+.4f | b1 = %+.4f | deviance %.2f (best of %d starts) | tau at A = 0.30/0.60/0.90: %s"
             % (g0, g1, 2 * gv, len(starts), " / ".join("%.3f" % math.exp(g0 + g1 * a) for a in (0.30, 0.60, 0.90))))
    L.append("    cold Mistral parameters on the same edges: deviance %.2f" % (2 * sb.nll((b0, b1), filt_g)))
    f_all = fast_nll(filt_g); assert abs(f_all(b0, b1) - sb.nll((b0, b1), filt_g)) < 1e-6, "vectorised nll differs from sb.nll"
    deg_e = (not math.isnan(e1)) and degenerate(e0, e1)
    L.append("  established labels only (%d edges, %d wrong): b0 = %+.4f | b1 = %+.4f%s"
             % (len(est_g), n_wrong_est, e0, e1, "  <- DEGENERATE: MLE at tau -> 0 for every A (no widener); not an estimate of b1" if deg_e else ""))
    inside_all = CI[0] <= g1 <= CI[1]; inside_est = (CI[0] <= e1 <= CI[1]) if (not math.isnan(e1) and not deg_e) else None
    # identifiability: profile deviance over b1 with b0 profiled out
    grid = [-2.0, 0.0, 1.0, CI[0], 2.0, 3.0, 5.0, CI[1], 10.0, 15.0, 20.0, 30.0]
    L.append("")
    L.append("  IDENTIFIABILITY (profile deviance, b0 profiled out; 3.84 = one-parameter 95% cut):")
    L.append("  %-28s %s" % ("b1", " ".join("%7.2f" % b for b in grid)))
    prof = {}
    for name, es, base in (("all labels", filt_g, 2 * gv), ("established labels", est_g, 2 * ev_ if not math.isnan(ev_) else None)):
        pr = profile(es, grid); prof[name] = pr
        mn = min(pr.values()) if base is None else min(base, min(pr.values()))
        L.append("  %-28s %s" % (name + " delta-dev", " ".join("%7.2f" % (pr[b] - mn) for b in grid)))
    for name, es in (("all labels", filt_g), ("established labels", est_g)):
        L.append("  %-28s deviance at Mistral params %.2f | at tau = 0 (raw) %.2f | at the grok MLE %.2f"
                 % (name, 2 * sb.nll((b0, b1), es), 2 * sb.nll((-50.0, 0.0), es), min(prof[name].values())))
    pa = prof["all labels"]; mn_a = min(2 * gv, min(pa.values()))
    lr0 = pa[0.0] - mn_a
    flat_ci = max(pa[CI[0]], pa[CI[1]]) - mn_a < 3.84
    flat_far = pa[15.0] - mn_a < 3.84 or pa[0.0] - mn_a < 3.84
    L.append("  all labels: LR test of b1 = 0 -> delta-dev %.2f (%s); delta-dev at the CI ends %.2f / %.2f; at b1 = 15: %.2f"
             % (lr0, "b1 = 0 rejected at 5%" if lr0 >= 3.84 else "b1 = 0 NOT rejected", pa[CI[0]] - mn_a, pa[CI[1]] - mn_a, pa[15.0] - mn_a))
    ci_g = anchor_cluster_ci(filt_g, starts[:2], reps=200)
    if ci_g:
        lo, hi = ci_g[int(0.025 * len(ci_g))], ci_g[min(len(ci_g) - 1, int(0.975 * len(ci_g)))]
        L.append("  anchor-clustered bootstrap of the grok refit (200 reps over %d anchors, %d identified): b1 95%% [%+.2f, %+.2f], median %+.2f"
                 % (len(aq_g), len(ci_g), lo, hi, ci_g[len(ci_g) // 2]))
    L.append("")
    L.append("  -> b1 refit, all labels (the shipped construction): %+.4f is %s [%.2f, %.2f]" % (g1, "INSIDE" if inside_all else "OUTSIDE", *CI))
    if inside_est is not None:
        L.append("  -> b1 refit, established labels: %+.4f is %s [%.2f, %.2f]" % (e1, "INSIDE" if inside_est else "OUTSIDE", *CI))
    elif deg_e:
        L.append("  -> b1 refit, established labels: UNIDENTIFIED - the profile deviance is flat in b1 and the MLE is 'no widener';")
        L.append("     the Mistral parameters fit these edges WORSE than tau = 0 by %.2f deviance (2 parameters)."
                 % (2 * sb.nll((b0, b1), est_g) - min(prof["established labels"].values())))
    if not inside_all:
        v2 = "FAIL (falsifier: refit outside the CI on the shipped construction)"
    elif inside_est is False:
        v2 = "FAIL on the hardest reading (inside on all labels, OUTSIDE on established labels)"
    elif flat_ci and flat_far:
        v2 = ("UNDETERMINED (point %+.2f is inside, so the registered falsifier does not fire, but the grok data do not locate b1: "
              "profile delta-dev < 3.84 across the whole CI and out to b1 = 15%s; on established labels b1 is unidentified)"
              % (g1, "" if lr0 >= 3.84 else " and b1 = 0 is not rejected"))
    else:
        v2 = "PASS (inside on the shipped construction%s)" % ("" if inside_est is None else " and on established labels")
    L.append("  -> criterion (2): %s" % v2)
    L.append("     reading chosen: the registered refit is on the population the shipped b1 was fitted on (all labels, gap >= 0.02);")
    L.append("     the literal point-in-interval check is reported first; the verdict is the hardest reading the registration")
    L.append("     supports - a refit whose own profile cannot tell the CI's ends from b1 = 15 has not been located inside it.")

    # ---- (3) utility ----
    L.append("")
    L.append("=== (3) UTILITY: fraction of grok edges the cold budget still calls (bar 60%, as SYSTEMATIC-BUDGET (2) and BUDGET-TRANSFER (2)) ===")
    frac = cold["bc"] / len(filt_g)
    frac_raw = cold["rc"] / len(filt_g)
    L.append("  raw certificate calls %d of %d (%.1f%%); cold budget calls %d of %d (%.1f%%); correct calls surrendered %d"
             % (cold["rc"], len(filt_g), 100 * frac_raw, cold["bc"], len(filt_g), 100 * frac,
                (cold["rc"] - cold["rw"]) - (cold["bc"] - cold["bw"])))
    rc = [e for e in filt_g if sb.craw(e) >= THRESH]; base_right = sum(1 for e in rc if e["right"])
    for t in (0.70, 0.80, 0.85):
        g = [e for e in rc if e["agree"] < t]; gw = [e for e in g if not e["right"]]
        L.append("  gate A < %.2f: %d called, %d wrong (%d est), %d correct surrendered"
                 % (t, len(g), len(gw), len(sb.established(gw, K, aq_g)), base_right - sum(1 for e in g if e["right"])))
    v3 = "PASS" if frac >= 0.60 else "FAIL"
    L.append("  in-roster x12 for comparison: raw %d of %d (%.1f%%), budget %d of %d (%.1f%%)"
             % (ref["rc"], ref["edges"], 100.0 * ref["rc"] / ref["edges"], ref["bc"], ref["edges"], 100.0 * ref["bc"] / ref["edges"]))
    L.append("  retained relative to the raw certificate: %.1f%% of raw calls (%d of %d)" % (100.0 * cold["bc"] / cold["rc"], cold["bc"], cold["rc"]))
    L.append("  -> criterion (3): %.1f%% of edges called against the 60%% bar the two previous budget tests registered -> %s" % (100 * frac, v3))
    L.append("     reading chosen: 'utility' is not given a bar in this registration; the 60% bar of SYSTEMATIC-BUDGET (2) and")
    L.append("     BUDGET-TRANSFER (2) is the only one on record and is the harder reading (the raw certificate itself calls %.1f%% here)." % (100 * frac_raw))

    # ---- summary ----
    L.append("")
    L.append("=== SUMMARY ===")
    L.append("  data: arm %s, %d verdicts, %d anchors at the 100 floor (%s excluded), %d edges at gap >= 0.02"
             % (arm, len(rows), len(aq_g), ", ".join(a for a in sorted(by_g) if a not in aq_g), len(filt_g)))
    L.append("  (1) cold ratio all %.2fx (%d/%.2f) | established %s (%d/%.2f) -> %s"
             % (ratio_all, cold["bw"], cold["nom"], ("%.2fx" % ratio_est) if cold["nom_e"] > 0 else "-", cold["bwe"], cold["nom_e"], v1))
    L.append("  (2) b1 refit on grok %+.4f (all) / %s (established) vs [%.2f, %.2f] -> %s"
             % (g1, "UNIDENTIFIED (tau -> 0)" if deg_e else "%+.4f" % e1, *CI, v2))
    L.append("  (3) utility %.1f%% -> %s" % (100 * frac, v3))
    pred_b1 = inside_all
    pred_ratio = (1.5 <= ratio_est <= 3.0) if cold["nom_e"] > 0 else False
    L.append("  PREDICTION (b1 inside CI AND cold established ratio 1.5-3x): b1 %s; ratio %s%s"
             % ("inside" if pred_b1 else "outside", "in band" if pred_ratio else "not in band",
                "" if cold["nom_e"] >= 3.0 else " (underpowered, nominal %.2f)" % cold["nom_e"]))
    L.append("  FALSIFIER (b1 point refit outside CI OR established ratio > 5x): %s"
             % ("FIRES" if (not inside_all or (cold["nom_e"] > 0 and ratio_est > 5.0 and (cold["nom_e"] >= 3.0 or p_tail_est < 0.05)))
                else ("does not fire on the b1 criterion; the ratio criterion is underpowered" if cold["nom_e"] < 3.0 else "does not fire")))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
