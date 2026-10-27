"""KTD-CHECK — independent recompute of KEY-TIE-DECLINE (registered by reference 2026-09-15, zero calls).

  python tools/analysis/ktd_check.py            # fresh rebuild (seed 42 everywhere, as the record) + comparison
  python tools/analysis/ktd_check.py --sens     # additionally: the same objects at a SECOND bootstrap seed (43)

REGISTERED ITEM (docs/design/FRAMEWORK.md, commit 8d77f7b, "## Tests to register before shipping", item 1), quoted:
  "1. KTD-CHECK. Independent recompute of KEY-TIE-DECLINE from its registration. Criterion: pooled widener +
   decline at 0.975 reproduces 150 called / 0 wrong; per anchor 1,714 / 4(4). Prediction: reproduces, with the
   residue anchors read as Law x3 + Philosophy x1 (bracket inserted into the programme). 0 calls."

THE REGISTRATION IT RECOMPUTES (docs/judge_v2_program.md, "### B. KEY-TIE-DECLINE"): "Decline any separation
whose pair's key direction is not established (exact McNemar p >= 0.05 on the cell's judged questions), on top
of the raw certificate and on top of the budget. Measure on x12 (891 edges) and on the merged 20-model board."

WHAT "INDEPENDENT" MEANS HERE (the reading hardest on the programme's claims):
  * NOTHING is read from key_tie_decline.py's code path. The verdict caches are read by this script's own SQL,
    the key by its own SQL, the routing by rubric_512 (the only routing there is), and the per-anchor and pooled
    bootstraps are re-run by this script's own loop with the SAME seed and draw order the record states
    (Random(42); per anchor B = 300 in sorted-anchor order with a >= 200-verdict floor; pooled B = 400 over the
    sorted judged questions). The Bradley-Terry engine is the shared judge_free_tests.board_from -> rejudge_grok.mm_fit;
    it is the programme's one fitting engine and is not re-derived here (stated as the one shared component).
  * Every statistic is re-implemented: the raw certificate, the widener (Phi via math.erfc, not scipy.norm), the
    exact two-sided McNemar (exact rationals via fractions.Fraction, cross-checked against scipy.stats.binomtest),
    key accuracy, the 0.017 reading-down tiering, the decline rule, the within/across strata, the residue list,
    and the undominated set. Each is then compared against the committed helpers (systematic_budget.craw/cbud/
    mcnemar_edge/established, budget_transfer.B0/B1, x20_replications.key_tiers) on the same inputs.
  * The fresh edge tables are compared FIELD BY FIELD against key_tie_decline's cached tables under scratchpad/
    bigpic/ (ktd_x12_edges.pkl, ktd_merged_edges.pkl), which are the tables FRAMEWORK's numbers were read from.
  * The x20_merged.txt board-of-record counts (within 6/7 separated, 3(1) wrong | across 176/183, 5(4)) are
    reproduced BEFORE any stratum is read, as the standing rule requires.
  * The key denominator is named at every count: x12 per-anchor = the anchor's JUDGED questions (qids with a
    valid STACK-v2 x12 verdict routed to that anchor under bareq512_s42); merged per-anchor = the same on the
    merged (x12 + x20) verdict set; pooled = all judged questions of the merged board. Every wrong count is
    printed as all(McNemar-established) on that denominator.
  * --sens: the criterion is an EXACT count at one bootstrap seed. A second seed says whether "150 / 0" and
    "1,714 / 4(4)" are properties of the board or of the draw. Reported as a caveat, not a criterion.
  * Meta-Llama-3-70B-Instruct is asserted absent from every roster. No network, no LLM calls.
"""
import os, sys, math, random, pickle, sqlite3, time
from fractions import Fraction
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import binomtest
import pool_guard
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import systematic_budget as sb
import budget_transfer as bt
import x20_replications as xr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "ktd_check.txt")
SCRATCH = os.path.join(r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad")
CACHE = os.path.join(SCRATCH, "block1")
BIGPIC = os.path.join(SCRATCH, "bigpic")
X20_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x20.db")
TREE = "bareq512_s42"
B_ANCHOR = 300          # systematic_budget.B / budget_transfer.B
B_POOLED = 400          # x20_replications.B (TIER-HONEST)
FLOOR = 200             # per-anchor verdict floor
GAP = 0.02              # key-gap filter on per-anchor edges
KEY_GAP = 0.017         # tiering gap (x20_merged)
CONF_X20 = 0.95         # x20_merged's separation confidence
ALPHA = 0.05
THRESHOLDS = (0.90, 0.95, 0.975, 0.99, 0.995)
B0, B1 = -3.2326, 3.3133            # the shipped widener, typed from the record; asserted == budget_transfer.B0/B1
EXCLUDE = "Meta-Llama-3-70B-Instruct"
SENS_SEED = 43
POOL_OF_RECORD = "p2dca21ab5f4ef3ae"


def log(msg):
    print("[ktd-check %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        log("cache hit %s" % name)
        return pickle.load(open(p, "rb"))
    log("building %s" % name)
    t0 = time.time()
    v = fn()
    pickle.dump(v, open(p, "wb"))
    log("built %s in %.0fs" % (name, time.time() - t0))
    return v


# ----------------------------------------------------------------------------------------------------------
# independent statistics
# ----------------------------------------------------------------------------------------------------------
def phi(z):
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def my_craw(e):
    return e["p"] if e["p"] >= 0.5 else 1.0 - e["p"]


def my_cbud(e, b0=B0, b1=B1):
    tau = math.exp(b0 + b1 * e["agree"])
    return min(my_craw(e), phi(abs(e["m"]) / math.sqrt(e["s"] * e["s"] + tau * tau)))


def my_mcnemar_p(b_, c_):
    """Exact two-sided McNemar = two-sided exact binomial at 0.5 on the discordant counts, in exact rationals."""
    n = b_ + c_
    if n == 0:
        return 1.0
    k = min(b_, c_)
    tail = Fraction(sum(math.comb(n, i) for i in range(k + 1)), 2 ** n)
    return float(min(Fraction(1), 2 * tail))


def discordant(K, a, b, qs):
    b_ = c_ = 0
    for q in qs:
        r = K.get(q)
        if not r:
            continue
        ka = r.get(a); kb = r.get(b)
        if ka is None or kb is None or ka == kb:
            continue
        if ka > kb:
            b_ += 1
        else:
            c_ += 1
    return b_, c_


def my_tiers(acc, models, gap=KEY_GAP):
    """Reading down the key accuracy; a new tier starts where the drop to the next model is >= gap."""
    order = sorted(models, key=lambda m: (-acc[m], m))
    tiers = [[order[0]]]
    for prev, cur in zip(order, order[1:]):
        if acc[prev] - acc[cur] >= gap:
            tiers.append([cur])
        else:
            tiers[-1].append(cur)
    return tiers


# ----------------------------------------------------------------------------------------------------------
# data: own SQL
# ----------------------------------------------------------------------------------------------------------
def read_verdicts(path):
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    rows = [(a, b, q, w) for a, b, q, w, inv in
            con.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not inv]
    con.close()
    return rows


def read_key(models):
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = {}; P = {}
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in models:
            K.setdefault(q, {})[m] = int(c or 0)
            P.setdefault(q, {})[m] = (pr or "").strip().upper()[:1]
    n_pool = ev.execute("SELECT COUNT(*) FROM reserved_pool WHERE pool_id = ?", (POOL_OF_RECORD,)).fetchone()[0]
    ev.close()
    return K, P, n_pool


def votes(rows):
    return [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rows]


def route_rows(rows):
    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for r in rows:
        if r[2] in route:
            by[anchor_of(route[r[2]])].append(r)
    return by


def pair_stats(models, draws, qs, K, P):
    la = {}
    for m in models:
        v = [K[q][m] for q in qs if q in K and m in K[q]]
        if v:
            la[m] = sum(v) / len(v)
    out = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            if a not in la or b not in la:
                continue
            d = np.array([dr[a] - dr[b] for dr in draws])
            p = float((d > 0).mean())
            both = [q for q in qs if q in P and P[q].get(a) and P[q].get(b)]
            agree = (sum(1 for q in both if P[q][a] == P[q][b]) / len(both)) if both else 0.0
            out.append(dict(a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)), agree=agree, n=len(both),
                            gap=abs(la[a] - la[b]), right=((p > 0.5) == (la[a] > la[b])), la=(la[a], la[b])))
    return out, la


def anchor_edges(by, models, K, P, seed, B=B_ANCHOR, keep_zero_gap=False):
    """Own bootstrap loop, same seed and draw order as systematic_budget.build / budget_transfer.edges_from."""
    rng = random.Random(seed)
    edges = []; anchor_qs = {}
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < FLOOR:
            continue
        qs = sorted({r[2] for r in rs}); anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            draws.append(jf.board_from(votes([r for q in pick for r in byq[q]]), models))
        es, _ = pair_stats(models, draws, qs, K, P)
        for e in es:
            if e["n"] == 0:
                continue
            if e["gap"] == 0 or (not keep_zero_gap and e["gap"] < GAP):
                continue
            e["anchor"] = anc
            edges.append(e)
        log("  anchor %-22s %5d verdicts %4d questions -> %d edges" % (anc, len(rs), len(qs), sum(1 for e in edges if e["anchor"] == anc)))
    return edges, anchor_qs


def pooled_edges(rows, models, K, P, seed, B=B_POOLED):
    rng = random.Random(seed)
    qs = sorted({r[2] for r in rows})
    byq = defaultdict(list)
    for r in rows:
        byq[r[2]].append(r)
    draws = []
    for i in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        draws.append(jf.board_from(votes([r for q in pick for r in byq[q]]), models))
        if i % 100 == 99:
            log("  pooled draw %d/%d" % (i + 1, B))
    es, acc = pair_stats(models, draws, qs, K, P)
    for e in es:
        e["anchor"] = "POOLED"
    return es, qs, acc


# ----------------------------------------------------------------------------------------------------------
# the rule
# ----------------------------------------------------------------------------------------------------------
def attach_mcnemar(edges, K, aq):
    for e in edges:
        b_, c_ = discordant(K, e["a"], e["b"], aq[e["anchor"]])
        e["mc_b"], e["mc_c"] = b_, c_
        e["mc_p"] = my_mcnemar_p(b_, c_)
        e["est"] = e["mc_p"] < ALPHA


def table(L, edges, title, tier_of=None):
    L.append("")
    L.append("=== %s ===" % title)
    n_est = sum(1 for e in edges if e["est"])
    nw = sum(1 for e in edges if not e["right"]); nwe = sum(1 for e in edges if not e["right"] and e["est"])
    L.append("  edges %d | key direction established (McNemar p < %.2f) %d | unestablished %d | wrong-direction %d(%d)"
             % (len(edges), ALPHA, n_est, len(edges) - n_est, nw, nwe))
    L.append("  %-8s %6s %7s %7s %10s %14s %8s %14s" % ("base", "thr", "called", "surr", "right surr", "wrong->removed", "residue", "residue wrong"))
    out = {}
    for base, cf in (("raw", my_craw), ("widener", my_cbud)):
        for t in THRESHOLDS:
            called = [e for e in edges if cf(e) >= t]
            surr = [e for e in called if not e["est"]]
            res = [e for e in called if e["est"]]
            cw = [e for e in called if not e["right"]]
            rw = [e for e in res if not e["right"]]
            st = dict(called=len(called), surr=len(surr), right_surr=sum(1 for e in surr if e["right"]),
                      wrong=len(cw), wrong_est=sum(1 for e in cw if e["est"]), removed=len(cw) - len(rw),
                      residue=len(res), res_wrong=len(rw), res_wrong_est=sum(1 for e in rw if e["est"]), res_edges=res)
            if tier_of is not None:
                ac = [e for e in called if tier_of[e["a"]] != tier_of[e["b"]]]
                wi = [e for e in called if tier_of[e["a"]] == tier_of[e["b"]]]
                st.update(ac_called=len(ac), ac_surr=sum(1 for e in ac if not e["est"]),
                          ac_wrong=sum(1 for e in ac if not e["right"]), ac_wrong_est=sum(1 for e in ac if not e["right"] and e["est"]),
                          ac_res_wrong=sum(1 for e in ac if not e["right"] and e["est"]),
                          wi_called=len(wi), wi_surr=sum(1 for e in wi if not e["est"]),
                          wi_wrong=sum(1 for e in wi if not e["right"]), wi_wrong_est=sum(1 for e in wi if not e["right"] and e["est"]),
                          wi_res_wrong=sum(1 for e in wi if not e["right"] and e["est"]))
            out[(base, t)] = st
            L.append("  %-8s %6.3f %7d %7d %10d %8d(%d)->%d %8d %10d(%d)"
                     % (base, t, st["called"], st["surr"], st["right_surr"], st["wrong"], st["wrong_est"], st["removed"],
                        st["residue"], st["res_wrong"], st["res_wrong_est"]))
    if tier_of is not None:
        L.append("  by KEY TIER (reading-down at %.3f over the judged questions):" % KEY_GAP)
        L.append("  %-8s %6s | %-44s | %-40s" % ("base", "thr", "ACROSS: called, surr (%), wrong(est) -> residue wrong",
                                                 "WITHIN: called, surr, wrong(est) -> residue wrong"))
        for base in ("raw", "widener"):
            for t in THRESHOLDS:
                st = out[(base, t)]
                fr = (100.0 * st["ac_surr"] / st["ac_called"]) if st["ac_called"] else float("nan")
                L.append("  %-8s %6.3f | %5d, %4d (%5.1f%%), %2d(%d) -> %2d | %4d, %3d, %2d(%d) -> %2d"
                         % (base, t, st["ac_called"], st["ac_surr"], fr, st["ac_wrong"], st["ac_wrong_est"], st["ac_res_wrong"],
                            st["wi_called"], st["wi_surr"], st["wi_wrong"], st["wi_wrong_est"], st["wi_res_wrong"]))
    return out


def list_edges(L, edges, label):
    if not edges:
        L.append("  %s: none" % label); return
    L.append("  %s (%d):" % (label, len(edges)))
    for e in sorted(edges, key=lambda e: (e["mc_p"], e["anchor"])):
        L.append("    %-12s %-28s vs %-28s raw=%.4f wid=%.4f key %.3f/%.3f A=%.3f McNemar %d:%d p=%.4f %s"
                 % (e["anchor"][:12], e["a"][:28], e["b"][:28], my_craw(e), my_cbud(e), e["la"][0], e["la"][1], e["agree"],
                    e["mc_b"], e["mc_c"], e["mc_p"], "ESTABLISHED" if e["est"] else "declined"))


def undominated(res_edges, models):
    """Models no other model is certified above, from the ORDERED (called-and-kept) edges."""
    above = defaultdict(set)
    for e in res_edges:
        win, lose = (e["a"], e["b"]) if e["p"] > 0.5 else (e["b"], e["a"])
        above[lose].add(win)
    return [m for m in models if not above[m]]


def compare_tables(L, fresh, cached_edges, keyf, label):
    """Field-by-field comparison of two edge tables keyed by (anchor, a, b)."""
    cidx = {keyf(e): e for e in cached_edges}
    fidx = {keyf(e): e for e in fresh}
    only_f = set(fidx) - set(cidx); only_c = set(cidx) - set(fidx)
    worst = {}; nflip = 0
    for k in set(fidx) & set(cidx):
        f, c = fidx[k], cidx[k]
        for fld in ("p", "m", "s", "agree", "gap"):
            worst[fld] = max(worst.get(fld, 0.0), abs(f[fld] - c[fld]))
        if f["right"] != c["right"] or f["n"] != c["n"]:
            nflip += 1
    L.append("  %s: fresh %d edges vs cached %d | only-fresh %d | only-cached %d | right/n mismatches %d | max |diff| p %.2e m %.2e s %.2e agree %.2e gap %.2e"
             % (label, len(fresh), len(cached_edges), len(only_f), len(only_c), nflip,
                worst.get("p", 0), worst.get("m", 0), worst.get("s", 0), worst.get("agree", 0), worst.get("gap", 0)))
    ok = not only_f and not only_c and nflip == 0 and all(v == 0.0 for v in worst.values())
    L.append("    -> %s" % ("IDENTICAL (every field bit-equal on every edge)" if ok else
                            ("EQUAL within 1e-9" if not only_f and not only_c and nflip == 0 and all(v < 1e-9 for v in worst.values())
                             else "MISMATCH")))
    return ok


def helper_checks(L, edges, K, aq):
    """The committed helpers on the same inputs, compared to this script's re-implementations."""
    d_raw = max(abs(my_craw(e) - sb.craw(e)) for e in edges)
    d_bud = max(abs(my_cbud(e) - sb.cbud(e, bt.B0, bt.B1)) for e in edges)
    nmis = 0; d_p = 0.0; d_sci = 0.0
    for e in edges:
        p_, b_, c_ = sb.mcnemar_edge(e, K, aq)
        if (b_, c_) != (e["mc_b"], e["mc_c"]):
            nmis += 1
        d_p = max(d_p, abs(p_ - e["mc_p"]))
        n = e["mc_b"] + e["mc_c"]
        if n:
            d_sci = max(d_sci, abs(binomtest(min(e["mc_b"], e["mc_c"]), n, 0.5).pvalue - e["mc_p"]))
    n_est_helper = len(sb.established(edges, K, aq)); n_est_mine = sum(1 for e in edges if e["est"])
    L.append("  helpers on the same edges: |craw - sb.craw| max %.1e | |cbud - sb.cbud(B0,B1)| max %.1e | McNemar (b,c) mismatches %d |"
             " |p - sb.mcnemar_edge| max %.1e | |p - scipy.binomtest| max %.1e | established: mine %d, sb.established %d"
             % (d_raw, d_bud, nmis, d_p, d_sci, n_est_mine, n_est_helper))
    return d_raw < 1e-12 and d_bud < 1e-9 and nmis == 0 and d_p < 1e-12 and n_est_helper == n_est_mine


# ----------------------------------------------------------------------------------------------------------
def build_x12():
    models = sorted(p8.ARENA12)
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = read_verdicts(sj.cache_path())
    K, P, n_pool = read_key(set(models))
    by = route_rows(rows)
    edges, aq = anchor_edges(by, models, K, P, seed=42, keep_zero_gap=True)
    return dict(models=models, rows_n=len(rows), K=K, P=P, edges=edges, aq=aq, n_pool=n_pool,
                cache=sj.cache_path())


def build_merged(seed):
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    r12 = read_verdicts(sj.cache_path()); r20 = read_verdicts(X20_DB)
    rows = r12 + r20
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    K, P, _ = read_key(set(models))
    by = route_rows(rows)
    edges, aq = anchor_edges(by, models, K, P, seed=seed)
    pooled, qs_judged, acc = pooled_edges(rows, models, K, P, seed=seed)
    return dict(models=models, n12=len(r12), n20=len(r20), K=K, P=P, edges=edges, aq=aq, pooled=pooled,
                qs_judged=qs_judged, acc=acc, n_orig_pairs_in_x20=sum(1 for r in r20 if r[0] in set(p8.ARENA12) and r[1] in set(p8.ARENA12)))


def main(sens):
    L = []
    L.append("=== KTD-CHECK: independent recompute of KEY-TIE-DECLINE (item 1, FRAMEWORK.md @ 8d77f7b; registered by reference 2026-09-15) ===")
    L.append("  criterion: pooled widener + decline at 0.975 reproduces 150 called / 0 wrong; per anchor 1,714 / 4(4).")
    L.append("  prediction: reproduces, with the residue anchors read as Law x3 + Philosophy x1.")
    L.append("  pool of record %s active (pool_guard.assert_pool_of_record) | widener tau(A) = exp(%.4f + %.4f*A) | %s excluded"
             % (POOL_OF_RECORD, B0, B1, EXCLUDE))
    assert (B0, B1) == (bt.B0, bt.B1), "shipped widener parameters differ from budget_transfer"
    L.append("  independence: own SQL on both verdict caches and the key; own bootstrap loop (seed 42, same draw order); own")
    L.append("  craw / widener (erfc) / exact McNemar (Fraction) / tiering / decline / strata; shared component = board_from -> mm_fit.")

    # ---------------- x12 ----------------
    x = cached("ktdc_x12_s42.pkl", build_x12)
    assert EXCLUDE not in x["models"]
    e12 = [e for e in x["edges"] if e["gap"] >= GAP]
    attach_mcnemar(x["edges"], x["K"], x["aq"])
    L.append("")
    L.append("--- DATA CHECK x12: cache %s | %d valid verdicts | %d models | anchors at the %d-verdict floor: %d | judged questions per anchor %d..%d (%d total) | edges any gap %d, gap >= %.2f: %d"
             % (os.path.basename(x["cache"]), x["rows_n"], len(x["models"]), FLOOR, len(x["aq"]),
                min(len(v) for v in x["aq"].values()), max(len(v) for v in x["aq"].values()), sum(len(v) for v in x["aq"].values()),
                len(x["edges"]), GAP, len(e12)))
    L.append("  key denominator: the anchor's JUDGED questions (qids with a valid verdict routed to the anchor under %s)." % TREE)
    c12 = pickle.load(open(os.path.join(BIGPIC, "ktd_x12_edges.pkl"), "rb"))
    ok_x12 = compare_tables(L, e12, [e for e in c12[3] if e["gap"] >= GAP], lambda e: (e["anchor"], e["a"], e["b"]), "x12 891-edge table vs key_tie_decline cache")
    ok_h12 = helper_checks(L, e12, x["K"], x["aq"])
    st12 = table(L, e12, "x12: %d per-anchor edges (gap >= %.2f), decline on both bases" % (len(e12), GAP))
    list_edges(L, [e for e in e12 if my_cbud(e) >= 0.975 and not e["right"]], "  x12 wrong calls, widener 0.975")
    list_edges(L, [e for e in e12 if my_craw(e) >= 0.975 and not e["right"]], "  x12 wrong calls, raw 0.975")

    # ---------------- merged ----------------
    mg = cached("ktdc_merged_s42.pkl", lambda: build_merged(42))
    assert EXCLUDE not in mg["models"]
    models = mg["models"]
    attach_mcnemar(mg["edges"], mg["K"], mg["aq"])
    aq_pool = {"POOLED": mg["qs_judged"]}
    attach_mcnemar(mg["pooled"], mg["K"], aq_pool)
    tiers = my_tiers(mg["acc"], models)
    tier_of = {m: i for i, t in enumerate(tiers) for m in t}
    kt_helper = xr.key_tiers(mg["acc"], models, gap=xr.KEY_GAP)
    L.append("")
    L.append("--- DATA CHECK merged board: x12 %d + x20 %d = %d verdicts | x20 verdicts on original pairs: %d (must be 0) | %d models | %d judged questions | per-anchor edges (gap >= %.2f) %d on %d anchors | pooled pairs %d"
             % (mg["n12"], mg["n20"], mg["n12"] + mg["n20"], mg["n_orig_pairs_in_x20"], len(models), len(mg["qs_judged"]), GAP, len(mg["edges"]), len(mg["aq"]), len(mg["pooled"])))
    L.append("  key tiers (own reading-down at %.3f over the %d judged questions): %d | x20_replications.key_tiers: %d, %s"
             % (KEY_GAP, len(mg["qs_judged"]), len(tiers), len(kt_helper), "same partition" if [set(t) for t in tiers] == [set(t) for t in kt_helper] else "DIFFERENT"))
    for i, t in enumerate(tiers):
        L.append("    tier %2d: %s" % (i, ", ".join("%s (%.4f)" % (m[:26], mg["acc"][m]) for m in t)))
    cm = pickle.load(open(os.path.join(BIGPIC, "ktd_merged_edges.pkl"), "rb"))
    ok_mg = compare_tables(L, mg["edges"], cm[2], lambda e: (e["anchor"], e["a"], e["b"]), "merged per-anchor table vs key_tie_decline cache")
    ok_pl = compare_tables(L, mg["pooled"], cm[5], lambda e: ("POOLED", e["a"], e["b"]), "merged pooled table vs key_tie_decline cache")
    acc_diff = max(abs(mg["acc"][m] - cm[6][m]) for m in models)
    L.append("  key accuracy over judged questions vs cache: max |diff| %.1e | judged-question sets %s" % (acc_diff, "equal" if mg["qs_judged"] == cm[4] else "DIFFERENT"))
    ok_hmg = helper_checks(L, mg["edges"], mg["K"], mg["aq"])
    ok_hpl = helper_checks(L, mg["pooled"], mg["K"], aq_pool)

    # board-of-record reproduction before any stratum
    sep = [e for e in mg["pooled"] if my_craw(e) >= CONF_X20]
    wi = [e for e in sep if tier_of[e["a"]] == tier_of[e["b"]]]; ac = [e for e in sep if tier_of[e["a"]] != tier_of[e["b"]]]
    n_wi = sum(1 for e in mg["pooled"] if tier_of[e["a"]] == tier_of[e["b"]]); n_ac = len(mg["pooled"]) - n_wi
    rep = (len(wi), n_wi, sum(1 for e in wi if not e["right"]), sum(1 for e in wi if not e["right"] and e["est"]),
           len(ac), n_ac, sum(1 for e in ac if not e["right"]), sum(1 for e in ac if not e["right"] and e["est"]))
    ok_rep = rep == (6, 7, 3, 1, 176, 183, 5, 4)
    L.append("  board of record at CONF %.2f: within %d/%d separated, wrong %d(%d) | across %d/%d, wrong %d(%d) -> x20_merged.txt (6/7, 3(1) | 176/183, 5(4)): %s"
             % ((CONF_X20,) + rep + ("REPRODUCED" if ok_rep else "MISMATCH",)))

    L.append("")
    L.append("  key denominator (pooled): all %d judged questions of the merged board, one pseudo-anchor." % len(mg["qs_judged"]))
    stP = table(L, mg["pooled"], "MERGED board, POOLED (%d pairs; TIER-HONEST object, %d draws)" % (len(mg["pooled"]), B_POOLED), tier_of)
    list_edges(L, [e for e in mg["pooled"] if my_craw(e) >= CONF_X20 and tier_of[e["a"]] == tier_of[e["b"]]], "  pooled within-tier separations at 0.95")
    list_edges(L, [e for e in mg["pooled"] if my_craw(e) >= CONF_X20 and not e["right"]], "  pooled WRONG separations at 0.95 (raw)")
    list_edges(L, [e for e in mg["pooled"] if my_cbud(e) >= 0.975 and not e["est"]], "  pooled widener 0.975: calls the decline surrenders")
    L.append("")
    L.append("  key denominator (per-anchor): the anchor's JUDGED questions on the merged verdict set (%d..%d per anchor)."
             % (min(len(v) for v in mg["aq"].values()), max(len(v) for v in mg["aq"].values())))
    stA = table(L, mg["edges"], "MERGED board, PER-ANCHOR (%d edges, gap >= %.2f, %d draws per anchor)" % (len(mg["edges"]), GAP, B_ANCHOR), tier_of)
    resA = [e for e in stA[("widener", 0.975)]["res_edges"] if not e["right"]]
    list_edges(L, resA, "  per-anchor widener + decline 0.975: the RESIDUE wrong calls")
    list_edges(L, [e for e in mg["edges"] if my_cbud(e) >= 0.975 and not e["right"] and not e["est"]], "  per-anchor widener 0.975: wrong calls the decline removes")

    # undominated set on the pooled composed rule at 0.975
    resP = stP[("widener", 0.975)]["res_edges"]
    und = undominated(resP, models)
    inv = [e for e in resP if tier_of[e["a"]] != tier_of[e["b"]] and not e["right"]]
    L.append("")
    L.append("  pooled widener + decline at 0.975 -> ORDERED %d of %d | undominated set (%d): %s | cross-tier key inversions among ORDERED: %d"
             % (len(resP), len(mg["pooled"]), len(und), ", ".join(sorted(und)), len(inv)))
    L.append("  (FRAMEWORK L11 states six: iask_pro, gemini-3.1-pro, claude-3-5-sonnet, arx_3, gpt-4o, arx_0314 -> %s)"
             % ("same set" if set(und) == {"iask_pro", "gemini-3.1-pro_5-shots", "claude-3-5-sonnet-20241022", "arx_3", "gpt-4o-2024-08-06", "arx_0314"} else "DIFFERENT"))

    # ---------------- criteria ----------------
    sP = stP[("widener", 0.975)]; sA = stA[("widener", 0.975)]; s12 = st12[("widener", 0.975)]
    anchors_res = sorted(e["anchor"] for e in resA)
    by_anchor = defaultdict(int)
    for e in resA:
        by_anchor[e["anchor"]] += 1
    models_res = sorted({m for e in resA for m in (e["a"], e["b"])})
    arena_winner = sorted({(e["a"] if e["p"] > 0.5 else e["b"]) for e in resA})
    key_winner = sorted({(e["a"] if e["la"][0] > e["la"][1] else e["b"]) for e in resA})
    # "called" under the composed rule = calls that SURVIVE the decline = the table's residue column
    c1a = sP["residue"] == 150 and sP["res_wrong"] == 0
    c1b = sA["residue"] == 1714 and sA["res_wrong"] == 4 and sA["res_wrong_est"] == 4
    pred = by_anchor.get("Law", 0) == 3 and by_anchor.get("Philosophy", 0) == 1 and len(resA) == 4
    L.append("")
    L.append("=== REGISTERED CRITERION AND PREDICTION ===")
    L.append("  (1a) pooled widener + decline at 0.975: called %d of %d, wrong %d(%d) [registered 150 / 0]  -> %s"
             % (sP["residue"], len(mg["pooled"]), sP["res_wrong"], sP["res_wrong_est"], "PASS" if c1a else "FAIL"))
    L.append("       (widener alone %d called, %d(%d) wrong; the decline surrenders %d, %d of them correct)"
             % (sP["called"], sP["wrong"], sP["wrong_est"], sP["surr"], sP["right_surr"]))
    L.append("  (1b) per-anchor widener + decline at 0.975: called %d of %d, wrong %d(%d) [registered 1,714 / 4(4)]  -> %s"
             % (sA["residue"], len(mg["edges"]), sA["res_wrong"], sA["res_wrong_est"], "PASS" if c1b else "FAIL"))
    L.append("       (widener alone %d called, %d(%d) wrong; the decline surrenders %d, %d of them correct; wrong rate on the residue %.2f%%)"
             % (sA["called"], sA["wrong"], sA["wrong_est"], sA["surr"], sA["right_surr"], 100.0 * sA["res_wrong"] / max(1, sA["residue"])))
    L.append("  PREDICTION residue anchors Law x3 + Philosophy x1: observed %s -> %s; models in the residue: %s"
             % (", ".join("%s x%d" % (k, v) for k, v in sorted(by_anchor.items())) or "none", "MET" if pred else "NOT MET", ", ".join(models_res)))
    L.append("  DIRECTION of the residue (a reading the record leaves loose): key winner in every residue edge = %s; arena winner = %s."
             % (", ".join(key_winner), ", ".join(arena_winner)))
    L.append("    i.e. the key says Meta-Llama-3.1-70B beats Qwen1.5-72B, deepseek-v2.5 and gpt-4o-mini in Law and gpt-4o-mini in Philosophy, and")
    L.append("    the arena rates it BELOW them: the judge UNDER-rates Llama-3.1-70B in those cells (equivalently over-rates the opponents).")
    L.append("    FRAMEWORK L97's 'the same model over-rated against cheaper-tier opponents' has the direction backwards; deepseek-v2.5 (tier 4)")
    L.append("    is also a higher key tier than Llama-3.1-70B (tier 5), so 'cheaper-tier' holds only for Qwen1.5-72B. Model-anchored: yes.")
    L.append("  record check: the programme's KEY-TIE-DECLINE entry carries the [CORRECTED 2026-09-15 ...] bracket with the same four edges (read by hand from docs/judge_v2_program.md).")
    L.append("  x12 widener + decline at 0.975 (KEY-TIE-DECLINE criterion (2)): called %d, wrong %d(%d) [record 651 / 1(1)] -> %s"
             % (s12["residue"], s12["res_wrong"], s12["res_wrong_est"], "reproduced" if (s12["residue"], s12["res_wrong"], s12["res_wrong_est"]) == (651, 1, 1) else "MISMATCH"))
    L.append("  x12 raw + decline at 0.975: called %d, wrong %d(%d) [record 712 / 4(4)] -> %s"
             % (st12[("raw", 0.975)]["residue"], st12[("raw", 0.975)]["res_wrong"], st12[("raw", 0.975)]["res_wrong_est"],
                "reproduced" if (st12[("raw", 0.975)]["residue"], st12[("raw", 0.975)]["res_wrong"]) == (712, 4) else "MISMATCH"))
    costs = dict(pooled_raw_095=100.0 * stP[("raw", 0.95)]["ac_surr"] / stP[("raw", 0.95)]["ac_called"],
                 pooled_wid_0975=100.0 * stP[("widener", 0.975)]["ac_surr"] / stP[("widener", 0.975)]["ac_called"],
                 anchor_raw_0975=100.0 * stA[("raw", 0.975)]["ac_surr"] / stA[("raw", 0.975)]["ac_called"],
                 anchor_wid_0975=100.0 * stA[("widener", 0.975)]["ac_surr"] / stA[("widener", 0.975)]["ac_called"])
    L.append("  cost of the rule in across-tier calls [record 0.6%% pooled, 3.4-5.6%% per anchor]: pooled raw 0.95 %.1f%%, pooled widener 0.975 %.1f%%, per-anchor raw 0.975 %.1f%%, per-anchor widener 0.975 %.1f%% -> falsifier (> 25%%) %s"
             % (costs["pooled_raw_095"], costs["pooled_wid_0975"], costs["anchor_raw_0975"], costs["anchor_wid_0975"],
                "does not fire" if max(costs.values()) <= 25 else "FIRES"))
    L.append("  data-object agreement: x12 table %s | merged per-anchor table %s | pooled table %s | helpers agree x12 %s, merged %s, pooled %s | board-of-record counts %s"
             % tuple("OK" if v else "MISMATCH" for v in (ok_x12, ok_mg, ok_pl, ok_h12, ok_hmg, ok_hpl, ok_rep)))

    # ---------------- sensitivity to the bootstrap seed ----------------
    L.append("")
    L.append("=== SENSITIVITY (caveat, not a criterion): the same objects at bootstrap seed %d ===" % SENS_SEED)
    if sens:
        ms = cached("ktdc_merged_s%d.pkl" % SENS_SEED, lambda: build_merged(SENS_SEED))
        attach_mcnemar(ms["edges"], ms["K"], ms["aq"]); attach_mcnemar(ms["pooled"], ms["K"], {"POOLED": ms["qs_judged"]})
        L.append("  the key, tiers and McNemar labels are seed-free; only p, m, s of each edge move with the draw.")
        stP2 = table(L, ms["pooled"], "POOLED at seed %d" % SENS_SEED, tier_of)
        stA2 = table(L, ms["edges"], "PER-ANCHOR at seed %d" % SENS_SEED, tier_of)
        resA2 = [e for e in stA2[("widener", 0.975)]["res_edges"] if not e["right"]]
        list_edges(L, resA2, "  per-anchor widener + decline 0.975 residue at seed %d" % SENS_SEED)
        k42 = {(e["anchor"], e["a"], e["b"]) for e in resA}; k43 = {(e["anchor"], e["a"], e["b"]) for e in resA2}
        und2 = undominated(stP2[("widener", 0.975)]["res_edges"], models)
        L.append("  seed %d vs 42 (composed rule at 0.975, calls surviving the decline): pooled %d vs %d called, wrong %d vs %d | per-anchor %d vs %d called, wrong %d(%d) vs %d(%d) | residue edges shared %d, only-42 %d, only-%d %d | undominated set %s"
                 % (SENS_SEED, stP2[("widener", 0.975)]["residue"], sP["residue"], stP2[("widener", 0.975)]["res_wrong"], sP["res_wrong"],
                    stA2[("widener", 0.975)]["residue"], sA["residue"], stA2[("widener", 0.975)]["res_wrong"], stA2[("widener", 0.975)]["res_wrong_est"],
                    sA["res_wrong"], sA["res_wrong_est"], len(k42 & k43), len(k42 - k43), SENS_SEED, len(k43 - k42),
                    "same" if set(und2) == set(und) else "DIFFERENT: " + ", ".join(sorted(und2))))
    else:
        L.append("  not run (pass --sens).")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main("--sens" in sys.argv)
