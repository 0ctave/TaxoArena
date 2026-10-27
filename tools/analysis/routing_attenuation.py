"""ROUTING-ATTENUATION (FRAMEWORK.md item 11, registered by reference at commit eaf1dbf; zero calls).

  python tools/analysis/routing_attenuation.py

The registered item, verbatim (docs/design/FRAMEWORK.md, "Tests to register before shipping", item 11):

    11. ROUTING-ATTENUATION. Synthetic misrouting at 0/10/20/30% on the key; attenuation of (model x anchor)
        contrasts. Criterion: attenuation at 19% <= the cell's clustered SE. Prediction: fails for the smallest
        anchors. 0 calls.

The record it cites (RESOLVE.md (2) and section 9; FRAMEWORK.md limits): union source+domain routing is 81.3%,
so ~19% of metadata-free arrivals are filed under the wrong (source, domain); MMLU-Pro alone routes 74-76%;
"no experiment in the campaign varied routing accuracy and measured the resulting attenuation of a capability
contrast" - the largest declared unknown, declared beside every routed-only row.

WHAT THIS SCRIPT DOES, at zero calls, on the key (per-question correctness of the 12 x12 models on the pool
of record p2dca21ab5f4ef3ae; Meta-Llama-3-70B-Instruct excluded, it is not in ARENA12):

  cells      (model, anchor); the anchor of record is the declared MMLU-Pro category (reserved_pool.domain).
  contrasts  C1 model-centred  = acc(m,a) - mean_a' acc(m,a')                 (the profile's "above its own average")
             C2 interaction    = acc(m,a) - acc(m,.) - acc(.,a) + acc(.,.)     (the literal (model x anchor) contrast)
  clustered SE  question-bootstrap SE of each contrast, resampling questions within anchor (cluster = question,
             all 12 models' outcomes move together), on the clean (declared) cells. The binomial SE of the cell
             accuracy is printed beside it.
  misrouting  each question is re-filed with probability p to another anchor, p in {0, .10, .19, .20, .30}:
             SYN-UNIFORM   destination uniform over the other 13 anchors          (the registered synthetic arm)
             SYN-TREE      destination drawn from the bareq512_s42 tree's empirical off-diagonal confusion row
             REALISED      the tree's actual routing of the pool (single realisation, native rate printed)
  attenuation per cell at rate p: bias = mean over draws of C_p - C_0 (the systematic part), and
             rms = sqrt(mean (C_p - C_0)^2) (the shift one realised routing produces). Plus the pooled
             shrinkage slope of C_p on C_0 across cells.
  criterion  per cell at p = 0.19: attenuation <= that cell's clustered SE.

READINGS TAKEN WHERE THE ITEM IS UNDER-SPECIFIED - each the one hardest on the programme's claims, and said so:
  (a) denominator: the EVAL-side keyed pool (3,445 questions) decides; it has the smaller SE. The x12 JUDGED
      denominator (2,811) is printed as the second class.
  (b) "attenuation": scored on both bias and rms; the verdict takes the worse.
  (c) contrast: scored on C1 and C2; the verdict takes the worse.
  (d) mechanism: the verdict takes the worse of the two synthetic arms; REALISED is reported as measured.
  (e) "fails for the smallest anchors": read as "the failing cells concentrate in the smallest anchors", scored
      by anchor rank of the failures and by Spearman(anchor size, failing cells).
  (f) "the cell's clustered SE": the question-bootstrap SE of the CONTRAST decides (it is the smaller); the
      Stage 5 row SE (question-bootstrap SE of the cell accuracy, ~binomial) is printed as a supplementary,
      softer reading, with the raw cell-accuracy shift scored against it as well.
Self-checks printed: a closed-form expectation of the SYN-UNIFORM mixture against the Monte Carlo bias, and a
second Monte Carlo seed for the failing-cell counts at 19%.
Pair directions (secondary): established key edges per anchor (exact McNemar p < 0.05 via
systematic_budget.mcnemar_edge over the anchor's JUDGED questions, the key denominator of record) under clean
cells, and at 19% misrouting the count that loses establishment or is established in the REVERSED direction
(each wrong-direction count carries its established count).
"""
import os, sys, math, sqlite3, time
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import spearmanr
import pool_guard
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "routing_attenuation.txt")
CACHE_DIR = os.environ.get("RA_CACHE", r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena"
                                       r"\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\block1")
POOL = pool_guard.FROZEN_POOL_ID
TREE = "bareq512_s42"
EXCLUDE = "Meta-Llama-3-70B-Instruct"
RATES = (0.0, 0.10, 0.19, 0.20, 0.30)
DRAWS = 200            # misrouting realisations per rate and mechanism
BOOT = 2000            # question-bootstrap draws for the clustered SE
MCN_DRAWS = 20         # misrouting realisations for the McNemar readout (exact test, Python loop)
SEED = 42


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ----------------------------------------------------------------------------------------------------- data
def load():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = dict(ev.execute("SELECT question_id, domain FROM reserved_pool WHERE pool_id = ?", (POOL,)))
    models = sorted(m for m in p8.ARENA12 if m != EXCLUDE)
    assert EXCLUDE not in models
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if q in pool and m in models:
            K[q][m] = int(c or 0)
    qs = sorted(pool)
    anchors = sorted(set(pool.values()))
    Y = np.full((len(qs), len(models)), np.nan)
    for i, q in enumerate(qs):
        for j, m in enumerate(models):
            if m in K[q]:
                Y[i, j] = K[q][m]
    declared = np.array([anchors.index(pool[q]) for q in qs])
    # the tree's actual routing of the same pool
    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    routed = np.array([anchors.index(anc(route[q])) for q in qs])
    # the x12 judged questions (STACK-v2 cache, ALL_X12), read-only
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    con = sqlite3.connect("file:%s?mode=ro" % sj.cache_path(), uri=True)
    judged = {q for q, inv in con.execute("SELECT qid, invalid FROM verdicts") if not inv}
    jmask = np.array([q in judged for q in qs])
    return qs, models, anchors, Y, declared, routed, jmask, K


# ------------------------------------------------------------------------------------------------ contrasts
def cell_acc(Y, lab, A):
    """(A x M) accuracy table from correctness Y (nan = missing) and integer anchor labels."""
    M = Y.shape[1]
    mask = ~np.isnan(Y); Y0 = np.where(mask, Y, 0.0)
    Z = np.zeros((len(lab), A)); Z[np.arange(len(lab)), lab] = 1.0
    num = Z.T @ Y0; den = Z.T @ mask
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def contrasts(acc):
    """C1 model-centred, C2 two-way interaction; unweighted means over the anchor x model table."""
    mm = np.nanmean(acc, axis=0, keepdims=True)   # per model, over anchors
    am = np.nanmean(acc, axis=1, keepdims=True)   # per anchor, over models
    gm = np.nanmean(acc)
    return acc - mm, acc - mm - am + gm


def boot_se(Y, lab, A, reps, rng):
    """Question bootstrap within anchor: SE of C1, C2 and of the cell accuracy itself (the Stage 5 row SE) per
    cell, on the given labelling. Cluster = question: all models' outcomes on a question move together."""
    idx_by = [np.where(lab == a)[0] for a in range(A)]
    c1s = []; c2s = []; accs = []
    for _ in range(reps):
        pick = np.concatenate([ix[rng.integers(0, len(ix), len(ix))] for ix in idx_by])
        acc = cell_acc(Y[pick], lab[pick], A)
        c1, c2 = contrasts(acc)
        c1s.append(c1); c2s.append(c2); accs.append(acc)
    return (np.nanstd(np.array(c1s), axis=0, ddof=1), np.nanstd(np.array(c2s), axis=0, ddof=1),
            np.nanstd(np.array(accs), axis=0, ddof=1))


def analytic_uniform(acc0, n, p, A):
    """Closed-form expectation of the cell accuracy table under SYN-UNIFORM misrouting at rate p (ratio of
    expected numerator to expected denominator; nan cells treated as absent): a cross-check on the Monte Carlo."""
    num = np.zeros_like(acc0); den = np.zeros(A)
    for a in range(A):
        keep = (1 - p) * n[a]
        foreign = p * sum(n[b] for b in range(A) if b != a) / (A - 1)
        num[a] = keep * np.nan_to_num(acc0[a]) + p * sum(n[b] * np.nan_to_num(acc0[b]) for b in range(A) if b != a) / (A - 1)
        den[a] = keep + foreign
    return num / den[:, None]


def misroute(lab, p, rng, A, conf_rows=None):
    """Re-file each question with probability p to another anchor: uniform over the other A-1, or from the
    empirical confusion row of its true anchor (conf_rows[a] = probabilities over destinations, self = 0)."""
    out = lab.copy()
    hit = np.where(rng.random(len(lab)) < p)[0]
    if conf_rows is None:
        shift = rng.integers(1, A, len(hit))          # 1..A-1
        out[hit] = (lab[hit] + shift) % A
    else:
        for i in hit:
            out[i] = rng.choice(A, p=conf_rows[lab[i]])
    return out


def confusion_rows(declared, routed, A):
    C = np.zeros((A, A))
    for d, r in zip(declared, routed):
        if d != r:
            C[d, r] += 1
    rows = []
    for a in range(A):
        s = C[a].sum()
        rows.append(C[a] / s if s > 0 else np.full(A, 1.0 / (A - 1)) * (np.arange(A) != a))
    return C, rows


def attenuation_table(Y, lab, A, c0, rates, draws, rng, conf_rows=None):
    """For each rate: per-cell bias and rms of C_p - C_0 (both contrasts), and the pooled shrinkage slope."""
    res = {}
    acc0 = cell_acc(Y, lab, A)
    for p in rates:
        d1 = []; d2 = []; d0 = []
        for _ in range(draws):
            lp = misroute(lab, p, rng, A, conf_rows) if p > 0 else lab
            accp = cell_acc(Y, lp, A)
            c1, c2 = contrasts(accp)
            d1.append(c1 - c0[0]); d2.append(c2 - c0[1]); d0.append(accp - acc0)
            if p == 0:
                break
        d1 = np.array(d1); d2 = np.array(d2); d0 = np.array(d0)
        slope = []
        for k, d in ((0, d1), (1, d2)):
            x = c0[k].ravel(); cp = (d + c0[k]).reshape(len(d), -1)
            ok = ~np.isnan(x)
            slope.append(float(np.mean([np.dot(cpi[ok], x[ok]) / np.dot(x[ok], x[ok]) for cpi in cp])))
        res[p] = dict(bias=(np.nanmean(d1, 0), np.nanmean(d2, 0)),
                      rms=(np.sqrt(np.nanmean(d1 ** 2, 0)), np.sqrt(np.nanmean(d2 ** 2, 0))),
                      acc_bias=np.nanmean(d0, 0), acc_rms=np.sqrt(np.nanmean(d0 ** 2, 0)),
                      slope=tuple(slope))
    return res


# ---------------------------------------------------------------------------------------- pair directions
def established_edges(K, models, anchors, qs, lab, jmask):
    """Per anchor: established key edges (McNemar p < 0.05 on the anchor's JUDGED questions under labelling lab).
    Returns {(anchor, a, b): sign} with sign = +1 if a beats b (b_ > c_), -1 otherwise."""
    anchor_qs = defaultdict(list)
    for i, q in enumerate(qs):
        if jmask[i]:
            anchor_qs[anchors[lab[i]]].append(q)
    out = {}
    for anc in anchors:
        if not anchor_qs.get(anc):
            continue
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                pv, b_, c_ = sb.mcnemar_edge(dict(anchor=anc, a=a, b=b), K, anchor_qs)
                if pv < 0.05:
                    out[(anc, a, b)] = 1 if b_ > c_ else -1
    return out, {a: len(v) for a, v in anchor_qs.items()}


# ----------------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    L = []
    active = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    os.makedirs(CACHE_DIR, exist_ok=True)
    qs, models, anchors, Y, declared, routed, jmask, K = load()
    A, M = len(anchors), len(models)
    rng = np.random.default_rng(SEED)
    n_anchor = np.bincount(declared, minlength=A)
    n_judged = np.bincount(declared[jmask], minlength=A)
    order_small = np.argsort(n_anchor)      # smallest first

    L.append("=== ROUTING-ATTENUATION (FRAMEWORK item 11): synthetic misrouting on the key, attenuation of (model x anchor) contrasts ===")
    L.append("  pool of record %s (active: %s) | %d questions | %d models (%s excluded; not in ARENA12) | %d anchors = declared MMLU-Pro categories"
             % (POOL, active, len(qs), M, EXCLUDE, A))
    L.append("  key: eval_results.is_correct; %d questions carry all %d models, %d carry fewer (nan-aware means)"
             % (int((~np.isnan(Y)).all(1).sum()), M, int((np.isnan(Y)).any(1).sum())))
    L.append("  denominators: EVAL-side keyed pool = %d questions (decides the verdict: smaller SE, the harder reading);"
             " x12 JUDGED = %d questions (second class, printed)" % (len(qs), int(jmask.sum())))
    L.append("  rates %s | %d misrouting draws per rate | clustered SE from %d within-anchor question-bootstrap draws | seed %d"
             % (", ".join("%.2f" % p for p in RATES), DRAWS, BOOT, SEED))
    L.append("  anchor sizes (declared, pool / judged): " + ", ".join("%s %d/%d" % (anchors[a], n_anchor[a], n_judged[a]) for a in order_small))

    # realised routing of the tree
    conf, conf_rows = confusion_rows(declared, routed, A)
    mis = int((declared != routed).sum())
    L.append("")
    L.append("=== (0) The tree's realised routing of this pool (%s, primary leaf -> anchor) ===" % TREE)
    L.append("  filed in the declared anchor %d of %d = %.1f%%; misfiled %.1f%% (the record's 'MMLU-Pro alone 74-76%%'; the union figure is 81.6%%, i.e. ~19%%)"
             % (len(qs) - mis, len(qs), 100.0 * (len(qs) - mis) / len(qs), 100.0 * mis / len(qs)))
    L.append("  NOTE: every x12 per-anchor board in the record was built on the ROUTED anchor (verdict.anchor == routed anchor on 9,142 of 9,142"
             " matches), so the anchor rows already carry this realised misfiling relative to the declared category.")
    L.append("  per anchor: misfiled OUT of it / foreign arrivals INTO it / net cell size under routing")
    for a in order_small:
        out_ = int(conf[a].sum()); in_ = int(conf[:, a].sum())
        top = sorted(((int(conf[a, b]), anchors[b]) for b in range(A) if conf[a, b] > 0), reverse=True)[:3]
        L.append("    %-17s n=%3d  out %3d (%4.1f%%)  in %3d  routed n=%3d  main destinations: %s"
                 % (anchors[a], n_anchor[a], out_, 100.0 * out_ / n_anchor[a], in_, int((routed == a).sum()),
                    ", ".join("%s %d" % (b, c) for c, b in top)))

    # ---- clean contrasts and clustered SE, both denominators
    results = {}
    for dname, dmask in (("EVAL", np.ones(len(qs), bool)), ("JUDGED", jmask)):
        Yd, ld, rd = Y[dmask], declared[dmask], routed[dmask]
        acc0 = cell_acc(Yd, ld, A); c0 = contrasts(acc0)
        cache = os.path.join(CACHE_DIR, "routing_attenuation_se_v2_%s_%d_%d.npz" % (dname, BOOT, SEED))
        if os.path.exists(cache):
            z = np.load(cache); se1, se2, se_acc = z["se1"], z["se2"], z["se_acc"]
        else:
            log("bootstrap SE on %s" % dname)
            se1, se2, se_acc = boot_se(Yd, ld, A, BOOT, np.random.default_rng(SEED + 1))
            np.savez(cache, se1=se1, se2=se2, se_acc=se_acc)
        cnt = (~np.isnan(Yd)).astype(float)
        Z = np.zeros((len(ld), A)); Z[np.arange(len(ld)), ld] = 1.0
        n_cell = Z.T @ cnt
        se_bin = np.sqrt(acc0 * (1 - acc0) / n_cell)
        log("attenuation tables on %s" % dname)
        uni = attenuation_table(Yd, ld, A, c0, RATES, DRAWS, np.random.default_rng(SEED + 2))
        tree = attenuation_table(Yd, ld, A, c0, RATES, DRAWS, np.random.default_rng(SEED + 3), conf_rows)
        cr1, cr2 = contrasts(cell_acc(Yd, rd, A))
        realised = (cr1 - c0[0], cr2 - c0[1])
        n_a_d = np.bincount(ld, minlength=A).astype(float)
        results[dname] = dict(acc0=acc0, c0=c0, se=(se1, se2), se_acc=se_acc, se_bin=se_bin, uni=uni, tree=tree, realised=realised,
                              n_cell=n_cell, n_a=n_a_d, rate=float((ld != rd).mean()))

    # ---- (1) contrasts and SE on the clean cells
    for dname in ("EVAL", "JUDGED"):
        R = results[dname]; se1, se2 = R["se"]; c1, c2 = R["c0"]
        L.append("")
        L.append("=== (1) Clean (declared) cells, %s denominator: contrast spread and clustered SE ===" % dname)
        L.append("  C1 model-centred: SD across cells %.4f, |C1| median %.4f max %.4f | clustered SE median %.4f (min %.4f, max %.4f)"
                 % (np.nanstd(c1), np.nanmedian(np.abs(c1)), np.nanmax(np.abs(c1)), np.nanmedian(se1), np.nanmin(se1), np.nanmax(se1)))
        L.append("  C2 interaction:   SD across cells %.4f, |C2| median %.4f max %.4f | clustered SE median %.4f (min %.4f, max %.4f)"
                 % (np.nanstd(c2), np.nanmedian(np.abs(c2)), np.nanmax(np.abs(c2)), np.nanmedian(se2), np.nanmin(se2), np.nanmax(se2)))
        L.append("  cell-accuracy SE (the Stage 5 row SE): question-bootstrap median %.4f, binomial median %.4f; ratio clustered-C1 / bootstrap-acc median %.3f"
                 " (the contrast SE is the smaller: the harder bar, and the one the verdict uses)"
                 % (np.nanmedian(R["se_acc"]), np.nanmedian(R["se_bin"]), np.nanmedian(se1 / R["se_acc"])))
        L.append("  cells with |C1| > 2 SE (a publishable 'above its own average' claim): %d of %d; |C2| > 2 SE: %d of %d"
                 % (int((np.abs(c1) > 2 * se1).sum()), A * M, int((np.abs(c2) > 2 * se2).sum()), A * M))
        L.append("  per-anchor clustered SE (C1 median over models): " + ", ".join(
            "%s %.3f" % (anchors[a], float(np.nanmedian(se1[a]))) for a in order_small))

    # ---- (2) attenuation by rate, pooled over cells
    for dname in ("EVAL", "JUDGED"):
        R = results[dname]; se1, se2 = R["se"]
        L.append("")
        L.append("=== (2) Attenuation by misrouting rate, %s denominator (pooled over the %d cells) ===" % (dname, A * M))
        L.append("  bias = mean over draws of C_p - C_0; rms = sqrt(mean (C_p - C_0)^2); slope = regression of C_p on C_0 through the origin")
        L.append("  mechanism   rate   C1: median|bias| max|bias| median rms  slope  cells |bias|<=SE  rms<=SE  | C2: median|bias| max|bias| median rms  slope  cells |bias|<=SE  rms<=SE")
        for mech in ("uni", "tree"):
            for p in RATES:
                r = R[mech][p]
                b1, b2 = r["bias"]; m1, m2 = r["rms"]
                L.append("  %-11s %.2f   %10.4f %9.4f %10.4f %6.3f  %6d/%d %6d/%d   | %10.4f %9.4f %10.4f %6.3f  %6d/%d %6d/%d"
                         % ("SYN-UNIFORM" if mech == "uni" else "SYN-TREE", p,
                            np.nanmedian(np.abs(b1)), np.nanmax(np.abs(b1)), np.nanmedian(m1), r["slope"][0],
                            int((np.abs(b1) <= se1).sum()), A * M, int((m1 <= se1).sum()), A * M,
                            np.nanmedian(np.abs(b2)), np.nanmax(np.abs(b2)), np.nanmedian(m2), r["slope"][1],
                            int((np.abs(b2) <= se2).sum()), A * M, int((m2 <= se2).sum()), A * M))
        d1, d2 = R["realised"]
        x1 = R["c0"][0].ravel(); x2 = R["c0"][1].ravel()
        s1 = float(np.dot((d1 + R["c0"][0]).ravel(), x1) / np.dot(x1, x1)); s2 = float(np.dot((d2 + R["c0"][1]).ravel(), x2) / np.dot(x2, x2))
        L.append("  %-11s %.3f  %10.4f %9.4f %10s %6.3f  %6d/%d %8s   | %10.4f %9.4f %10s %6.3f  %6d/%d %8s   (single realisation: shift, not bias)"
                 % ("REALISED", R["rate"], np.nanmedian(np.abs(d1)), np.nanmax(np.abs(d1)), "-", s1, int((np.abs(d1) <= se1).sum()), A * M, "-",
                    np.nanmedian(np.abs(d2)), np.nanmax(np.abs(d2)), "-", s2, int((np.abs(d2) <= se2).sum()), A * M, "-"))

    # ---- (3) the criterion at 19%, per anchor, every reading
    L.append("")
    L.append("=== (3) CRITERION: attenuation at 19%% <= the cell's clustered SE, per anchor (cells failing of %d per anchor) ===" % M)
    L.append("  columns: SYN-UNIFORM bias / rms, SYN-TREE bias / rms, each for C1 and C2; anchors smallest first")
    fails = {}
    for dname in ("EVAL", "JUDGED"):
        R = results[dname]; se1, se2 = R["se"]
        L.append("  -- %s denominator --" % dname)
        L.append("  %-17s   n   UNI-C1 bias rms   UNI-C2 bias rms   TREE-C1 bias rms   TREE-C2 bias rms   REALISED C1 C2   worst   UNI-C1 med|bias| / med SE" % "anchor")
        per_anchor = []
        for a in order_small:
            cells = []
            for mech in ("uni", "tree"):
                r = R[mech][0.19]
                for k, se in ((0, se1), (1, se2)):
                    cells.append(int((np.abs(r["bias"][k][a]) > se[a]).sum()))
                    cells.append(int((r["rms"][k][a] > se[a]).sum()))
            re1 = int((np.abs(R["realised"][0][a]) > se1[a]).sum()); re2 = int((np.abs(R["realised"][1][a]) > se2[a]).sum())
            worst = max(cells)
            per_anchor.append((anchors[a], int(n_anchor[a] if dname == "EVAL" else n_judged[a]), cells, re1, re2, worst))
            ub = R["uni"][0.19]["bias"][0][a]
            L.append("  %-17s %4d   %4d %4d          %4d %4d          %4d %4d           %4d %4d           %4d %4d    %4d   %.4f / %.4f = %.2f"
                     % (anchors[a], per_anchor[-1][1], cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], cells[6], cells[7], re1, re2, worst,
                        float(np.nanmedian(np.abs(ub))), float(np.nanmedian(se1[a])), float(np.nanmedian(np.abs(ub)) / np.nanmedian(se1[a]))))
        tot = [sum(pa[2][i] for pa in per_anchor) for i in range(8)]
        L.append("  %-17s %4s   %4d %4d          %4d %4d          %4d %4d           %4d %4d           %4d %4d    %4d"
                 % ("TOTAL failing", "", tot[0], tot[1], tot[2], tot[3], tot[4], tot[5], tot[6], tot[7],
                    sum(pa[3] for pa in per_anchor), sum(pa[4] for pa in per_anchor), sum(pa[5] for pa in per_anchor)))
        fails[dname] = per_anchor

    # ---- (4) verdicts
    L.append("")
    L.append("=== (4) VERDICTS ===")
    pa = fails["EVAL"]
    labels = ["UNI-C1 bias", "UNI-C1 rms", "UNI-C2 bias", "UNI-C2 rms", "TREE-C1 bias", "TREE-C1 rms", "TREE-C2 bias", "TREE-C2 rms"]
    tot = [sum(x[2][i] for x in pa) for i in range(8)]
    n_cells = A * M
    softest = min(tot); hardest = max(tot)
    L.append("  Criterion (attenuation at 19%% <= cell clustered SE), EVAL denominator, %d cells:" % n_cells)
    for lab_, t in zip(labels, tot):
        L.append("    %-13s failing cells %3d of %d (%.1f%%)" % (lab_, t, n_cells, 100.0 * t / n_cells))
    L.append("    registered reading (SYN-UNIFORM, bias): %d of %d cells fail -> %s"
             % (tot[0], n_cells, "PASS (every cell within its SE)" if tot[0] == 0 else "FAIL"))
    L.append("    hardest reading (worst of mechanism x contrast x bias/rms): %d of %d cells fail -> %s"
             % (hardest, n_cells, "PASS" if hardest == 0 else "FAIL"))
    L.append("    softest reading: %d of %d cells fail -> %s" % (softest, n_cells, "PASS" if softest == 0 else "FAIL"))
    L.append("    CRITERION VERDICT: %s (the item is per cell; a single failing cell fails it; scored on the hardest reading, as declared)"
             % ("PASS" if hardest == 0 else "FAIL"))
    jt = [sum(x[2][i] for x in fails["JUDGED"]) for i in range(8)]
    L.append("    JUDGED denominator, same readings: %s" % ", ".join("%s %d" % (l, t) for l, t in zip(labels, jt)))
    # supplementary readings of "the cell's clustered SE": the Stage 5 row SE (question-bootstrap SE of the cell
    # accuracy, ~binomial) instead of the contrast's SE; and the cell accuracy's own shift against it
    R = results["EVAL"]; sa = R["se_acc"]
    L.append("    supplementary, EVAL, SE = the cell-accuracy row SE (softer than the contrast SE): contrast bias > row SE: UNI-C1 %d, UNI-C2 %d, TREE-C1 %d, TREE-C2 %d;"
             " raw cell-accuracy bias > row SE: UNI %d, TREE %d; raw cell-accuracy rms > row SE: UNI %d, TREE %d (of %d)"
             % (int((np.abs(R["uni"][0.19]["bias"][0]) > sa).sum()), int((np.abs(R["uni"][0.19]["bias"][1]) > sa).sum()),
                int((np.abs(R["tree"][0.19]["bias"][0]) > sa).sum()), int((np.abs(R["tree"][0.19]["bias"][1]) > sa).sum()),
                int((np.abs(R["uni"][0.19]["acc_bias"]) > sa).sum()), int((np.abs(R["tree"][0.19]["acc_bias"]) > sa).sum()),
                int((R["uni"][0.19]["acc_rms"] > sa).sum()), int((R["tree"][0.19]["acc_rms"] > sa).sum()), n_cells))
    # analytic cross-check of the Monte Carlo (SYN-UNIFORM, closed-form mixture expectation)
    for p_ in (0.10, 0.19, 0.30):
        an = analytic_uniform(R["acc0"], R["n_a"], p_, A)
        a1, a2 = contrasts(an); b1, b2 = R["uni"][p_]["bias"]
        mc_se = R["uni"][p_]["rms"][0] / math.sqrt(DRAWS)
        L.append("    analytic cross-check SYN-UNIFORM %.2f: max|MC bias - closed form| C1 %.4f C2 %.4f (median MC SE of the bias %.4f);"
                 " failing cells by the closed form, C1 bias > SE: %d (MC %d)"
                 % (p_, float(np.nanmax(np.abs(b1 - (a1 - R["c0"][0])))), float(np.nanmax(np.abs(b2 - (a2 - R["c0"][1])))),
                    float(np.nanmedian(mc_se)), int((np.abs(a1 - R["c0"][0]) > R["se"][0]).sum()), int((np.abs(b1) > R["se"][0]).sum())))
    # second Monte Carlo seed at 19% (stability of the counts)
    rng2 = np.random.default_rng(SEED + 1000)
    u2 = attenuation_table(Y, declared, A, R["c0"], (0.19,), DRAWS, rng2)[0.19]
    t2 = attenuation_table(Y, declared, A, R["c0"], (0.19,), DRAWS, rng2, conf_rows)[0.19]
    se1, se2 = R["se"]
    c2nd = [int((np.abs(u2["bias"][0]) > se1).sum()), int((u2["rms"][0] > se1).sum()), int((np.abs(u2["bias"][1]) > se2).sum()), int((u2["rms"][1] > se2).sum()),
            int((np.abs(t2["bias"][0]) > se1).sum()), int((t2["rms"][0] > se1).sum()), int((np.abs(t2["bias"][1]) > se2).sum()), int((t2["rms"][1] > se2).sum())]
    L.append("    second MC seed (%d), EVAL, failing cells at 19%%: %s" % (SEED + 1000, ", ".join("%s %d" % (l, t) for l, t in zip(labels, c2nd))))
    # where the failures sit on the |C_0| / SE axis (the mechanism: bias ~ (1 - slope) x C_0)
    c1 = R["c0"][0]; b1 = R["uni"][0.19]["bias"][0]; ratio = np.abs(c1) / se1; failm = np.abs(b1) > se1
    L.append("    registered reading: |C1_0| / SE among failing cells min %.2f (median %.2f); among passing cells max %.2f -> a contrast of about %.1f SE or more"
             " is attenuated by more than one SE at 19%% uniform misrouting (bias/contrast slope %.3f)"
             % (float(np.nanmin(ratio[failm])) if failm.any() else float("nan"), float(np.nanmedian(ratio[failm])) if failm.any() else float("nan"),
                float(np.nanmax(ratio[~failm])), 1.0 / (1.0 - R["uni"][0.19]["slope"][0]), R["uni"][0.19]["slope"][0]))
    L.append("    failing cells, registered reading (anchor: models with |bias| / SE):")
    for a in order_small:
        fm = [(models[j], float(np.abs(b1[a, j]) / se1[a, j])) for j in range(M) if failm[a, j]]
        if fm:
            L.append("      %-17s %s" % (anchors[a], ", ".join("%s %.2f" % (m_, r_) for m_, r_ in fm)))
    # prediction: fails for the smallest anchors
    sizes = [x[1] for x in pa]; worst_per = [x[5] for x in pa]; reg = [x[2][0] for x in pa]
    rho_w, p_w = spearmanr(sizes, worst_per); rho_r, p_r = spearmanr(sizes, reg)
    three = [x[0] for x in pa[:3]]
    fail_small_w = sum(x[5] for x in pa[:3]); fail_rest_w = sum(x[5] for x in pa[3:])
    fail_small_r = sum(x[2][0] for x in pa[:3]); fail_rest_r = sum(x[2][0] for x in pa[3:])
    L.append("  Prediction 'fails for the smallest anchors' (three smallest: %s):" % ", ".join(three))
    L.append("    registered reading: failing cells in the three smallest anchors %d of %d (%d/%d elsewhere, %d anchors); Spearman(anchor size, fails) = %+.3f p = %.3f"
             % (fail_small_r, 3 * M, fail_rest_r, (A - 3) * M, A - 3, rho_r, p_r))
    L.append("    hardest reading:    failing cells in the three smallest anchors %d of %d (%d/%d elsewhere); Spearman(anchor size, worst fails) = %+.3f p = %.3f"
             % (fail_small_w, 3 * M, fail_rest_w, (A - 3) * M, rho_w, p_w))
    anchors_failing_w = [x[0] for x in pa if x[5] > 0]; anchors_failing_r = [x[0] for x in pa if x[2][0] > 0]
    L.append("    anchors with any failing cell - registered: %s | hardest: %s"
             % (", ".join(anchors_failing_r) or "none", ", ".join(anchors_failing_w) or "none"))
    share_small_r = fail_small_r / (3.0 * M); share_rest_r = fail_rest_r / float((A - 3) * M)
    share_small_w = fail_small_w / (3.0 * M); share_rest_w = fail_rest_w / float((A - 3) * M)
    if hardest == 0:
        pred = "NOT SUPPORTED (no cell fails on any reading)"
    elif share_small_r > share_rest_r and rho_r < 0:
        pred = "SUPPORTED on the registered reading (failures concentrate in the smallest anchors)"
    elif share_small_w > share_rest_w and rho_w < 0:
        pred = "SUPPORTED only on the hardest reading"
    else:
        pred = ("NOT SUPPORTED: failing-cell share in the three smallest anchors %.0f%% vs %.0f%% elsewhere (registered), %.0f%% vs %.0f%% (hardest); "
                "the size-fail correlation is positive - failures sit where the SE is smallest and the contrast largest, not where the anchor is small"
                % (100 * share_small_r, 100 * share_rest_r, 100 * share_small_w, 100 * share_rest_w))
    L.append("    PREDICTION: %s" % pred)
    L.append("    mechanism: the expected shift of a cell under SYN-UNIFORM is ~p x (mixture mean - acc(m,a)), i.e. proportional to the contrast itself"
             " (slope %.3f at 19%%), while the SE falls with sqrt(n); the small anchors take more foreign arrivals per own question but their SE absorbs it"
             % results["EVAL"]["uni"][0.19]["slope"][0])
    L.append("    Monte Carlo: bias estimated from %d draws; its MC standard error ~ rms/sqrt(%d) ~ %.4f, an order below the cell SE" % (DRAWS, DRAWS, float(np.nanmedian(results["EVAL"]["uni"][0.19]["rms"][0])) / math.sqrt(DRAWS)))
    L.append("  Realised routing (%s, %.1f%% misfiled, single realisation): cells shifted by more than their SE: C1 %d, C2 %d of %d (EVAL)"
             % (TREE, 100 * results["EVAL"]["rate"], sum(x[3] for x in pa), sum(x[4] for x in pa), n_cells))

    # ---- (5) what 19% misrouting does to the publishable contrasts
    L.append("")
    L.append("=== (5) Publishable contrasts (|C| > 2 SE on the clean cells) and their fate at 19% SYN-UNIFORM misrouting, EVAL denominator ===")
    R = results["EVAL"]
    for k, name in ((0, "C1 model-centred"), (1, "C2 interaction")):
        c = R["c0"][k]; se = R["se"][k]; b = R["uni"][0.19]["bias"][k]
        pub = np.abs(c) > 2 * se
        cp = c + b
        keep = pub & (np.abs(cp) > 2 * se) & (np.sign(cp) == np.sign(c))
        L.append("  %-18s publishable clean %3d of %d; still |C_19| > 2 SE with the same sign after the expected shift %3d; erased %3d; mean shrinkage of |C| among them %.1f%%"
                 % (name, int(pub.sum()), n_cells, int(keep.sum()), int((pub & ~keep).sum()),
                    100.0 * (1 - float(np.nanmean(np.abs(cp[pub]) / np.abs(c[pub])))) if pub.any() else float("nan")))

    # ---- (6) pair directions: established key edges per anchor under misrouting (McNemar on JUDGED questions)
    L.append("")
    L.append("=== (6) Pair directions: established key edges (exact McNemar p < 0.05, denominator = the anchor's JUDGED questions) ===")
    L.append("  key denominator: systematic_budget.mcnemar_edge over the anchor's x12 JUDGED questions under each labelling (declared, misrouted, realised);"
             " wrong-direction counts carry their established count as n(n_est)")
    log("McNemar on declared cells")
    est0, nq0 = established_edges(K, models, anchors, qs, declared, jmask)
    n_pairs = M * (M - 1) // 2
    L.append("  declared cells: established %d of %d per-anchor edges (%d anchors x %d pairs)" % (len(est0), A * n_pairs, A, n_pairs))
    rows = []
    rng_m = np.random.default_rng(SEED + 4)
    for name, labs in (("SYN-UNIFORM 19%", [misroute(declared, 0.19, rng_m, A) for _ in range(MCN_DRAWS)]),
                       ("SYN-TREE 19%", [misroute(declared, 0.19, rng_m, A, conf_rows) for _ in range(MCN_DRAWS)]),
                       ("REALISED %.1f%%" % (100 * results["EVAL"]["rate"]), [routed])):
        log("McNemar under %s (%d labellings)" % (name, len(labs)))
        agg = Counter(); per_anchor = defaultdict(Counter)
        for lab_ in labs:
            est, _ = established_edges(K, models, anchors, qs, lab_, jmask)
            for e, s in est0.items():
                if e in est:
                    if est[e] == s: agg["kept"] += 1; per_anchor[e[0]]["kept"] += 1
                    else: agg["reversed"] += 1; per_anchor[e[0]]["reversed"] += 1
                else:
                    agg["lost"] += 1; per_anchor[e[0]]["lost"] += 1
            agg["new"] += sum(1 for e in est if e not in est0)
            agg["total"] += len(est)
        n = len(labs)
        L.append("  %-16s per labelling (mean over %d): established %.1f | of the %d clean-established: kept %.1f (%.1f%%), lost %.1f, REVERSED = wrong-direction %.1f(%.1f) [n(n_established); established by construction] | newly established %.1f"
                 % (name, n, agg["total"] / n, len(est0), agg["kept"] / n, 100.0 * agg["kept"] / n / len(est0),
                    agg["lost"] / n, agg["reversed"] / n, agg["reversed"] / n, agg["new"] / n))
        worst = sorted(((per_anchor[a]["lost"] / n, a) for a in per_anchor), reverse=True)[:4]
        L.append("      most establishment lost: " + ", ".join("%s %.1f of %d" % (a, l, sum(1 for e in est0 if e[0] == a)) for l, a in worst))
        rev = [(a, per_anchor[a]["reversed"] / n) for a in per_anchor if per_anchor[a]["reversed"] > 0]
        if rev:
            L.append("      reversed (established wrong direction) by anchor: " + ", ".join("%s %.2f" % (a, r) for a, r in sorted(rev)))

    L.append("")
    L.append("  elapsed %.0f s; SE cache %s" % (time.time() - t0, CACHE_DIR))
    txt = "\n".join(L)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
