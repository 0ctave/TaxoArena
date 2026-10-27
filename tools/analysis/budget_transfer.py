"""BUDGET-TRANSFER — does the fitted widener survive a change of roster? (registered 2026-09-14, zero calls)

  python tools/analysis/budget_transfer.py

CORRECTED 2026-09-15 after the session review. Two defects in the first version:
  (1) It read stack_v2_promptv2_x20.db ALONE, which holds 12,394 verdicts on the 124 pairs involving a new
      model and ZERO on the 66 original pairs. The "20-model board" it fitted never compared the twelve
      originals directly, so SHARED / CROSS / INTERNAL did not mean fitted / half-fitted / unfitted. This
      version keeps the sparse-board run (labelled as such) AND adds the honest transfer design: fit on the x12
      verdicts, score ONLY the pairs whose verdicts are new, on the merged board of record.
  (2) It counted wrong-direction edges without the McNemar establishment filter the same session adopted.
      Every wrong count below carries its established count beside it, on the anchor's JUDGED questions.
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import norm
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "budget_transfer.txt")
X20 = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x20.db")
B = 300
THRESH = 0.975
GAP = 0.02
B0, B1 = -3.2326, 3.3133          # the shipped x12 parameters, applied COLD


def edges_from(rows, models, K, P, old, tag):
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))
    rng = random.Random(42)
    edges = []; anchor_qs = {}
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200:
            continue
        qs = sorted({q for _, _, q, _ in rs}); anchor_qs[anc] = qs
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
                if gap < GAP:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                na, nb = a not in old, b not in old
                prov = "INTERNAL" if (na and nb) else ("CROSS" if (na or nb) else "SHARED")
                edges.append(dict(anchor=anc, a=a, b=b, p=float((d > 0).mean()), m=float(d.mean()),
                                  s=float(d.std(ddof=1)), right=((float((d > 0).mean()) > 0.5) == (la[a] > la[b])),
                                  agree=agree, gap=gap, n=len(both), prov=prov, board=tag))
    return edges, anchor_qs


def load():
    con = sqlite3.connect("file:%s?mode=ro" % X20, uri=True)
    r20 = [r for r in con.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    r12 = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    models = sorted({r[0] for r in r20} | {r[1] for r in r20} | {r[0] for r in r12} | {r[1] for r in r12})
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in models:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    return r12, r20, models, K, P


def block(L, name, es, K, aq):
    if not es:
        L.append("  %-10s no edges" % name); return
    rc = [e for e in es if sb.craw(e) >= THRESH]
    bc = [e for e in es if sb.cbud(e, B0, B1) >= THRESH]
    rw = [e for e in rc if not e["right"]]; bw = [e for e in bc if not e["right"]]
    rwe = len(sb.established(rw, K, aq)); bwe = len(sb.established(bw, K, aq))
    nom = sum(1 - sb.cbud(e, B0, B1) for e in bc)
    est_c = [e for e in bc if sb.mcnemar_edge(e, K, aq)[0] < 0.05]
    nom_e = sum(1 - sb.cbud(e, B0, B1) for e in est_c)
    L.append("  %-10s %6d %8d %5d(%d) %9d %5d(%d) %8.2f %7s | established only: %d called, %d wrong, %.2f nom = %s"
             % (name, len(es), len(rc), len(rw), rwe, len(bc), len(bw), bwe, nom,
                ("%.1fx" % (len(bw) / nom)) if nom > 0 else "-",
                len(est_c), bwe, nom_e, ("%.1fx" % (bwe / nom_e)) if nom_e > 0 else "-"))


def main():
    L = []
    r12, r20, models, K, P = load()
    old = set(p8.ARENA12)
    new = [m for m in models if m not in old]
    L.append("=== BUDGET-TRANSFER (corrected 2026-09-15): does tau(A) = exp(%.4f + %.4f*A) survive a change of roster? ===" % (B0, B1))
    L.append("  x12 cache %d verdicts | x20 cache %d verdicts on %d pairs, of which %d involve two originals"
             % (len(r12), len(r20), len({tuple(sorted((r[0], r[1]))) for r in r20}),
                sum(1 for r in r20 if r[0] in old and r[1] in old)))
    L.append("  new models: %s" % ", ".join(sorted(new)))
    L.append("  wrong counts are shown as all(McNemar-established) on the anchor's judged questions.")

    # ---- A. the sparse board, kept for the record, labelled ----
    L.append("")
    L.append("=== A. THE SPARSE BOARD OF 2026-09-14 (x20 cache alone; the originals never compared directly) ===")
    L.append("  %-10s %6s %8s %8s %9s %8s %8s %7s" % ("prov", "edges", "rawcall", "wrong", "budcall", "wrong", "nominal", "ratio"))
    e_sp, aq_sp = edges_from(r20, models, K, P, old, "sparse")
    for nm in ("INTERNAL", "CROSS", "SHARED"):
        block(L, nm, [e for e in e_sp if e["prov"] == nm], K, aq_sp)
    block(L, "ALL", e_sp, K, aq_sp)
    L.append("  READ: on this board SHARED edges are inferred through the new models only; the strata do not mean")
    L.append("  fitted / half-fitted / unfitted. Shown so the retracted 6.9x and the retraction's 1.7x have a home.")

    # ---- B. the honest transfer: merged board, score only pairs with NEW verdicts ----
    L.append("")
    L.append("=== B. THE MERGED BOARD OF RECORD (x12 + x20 = %d verdicts), cold parameters, NEW-verdict pairs only ===" % (len(r12) + len(r20)))
    e_mg, aq_mg = edges_from(r12 + r20, models, K, P, old, "merged")
    L.append("  %-10s %6s %8s %8s %9s %8s %8s %7s" % ("prov", "edges", "rawcall", "wrong", "budcall", "wrong", "nominal", "ratio"))
    for nm in ("INTERNAL", "CROSS"):
        block(L, nm, [e for e in e_mg if e["prov"] == nm], K, aq_mg)
    block(L, "NEW (both)", [e for e in e_mg if e["prov"] != "SHARED"], K, aq_mg)
    block(L, "SHARED*", [e for e in e_mg if e["prov"] == "SHARED"], K, aq_mg)
    L.append("  SHARED* on the merged board IS the x12 fitting data plus indirect constraints - in-sample, sanity only.")
    novel = [e for e in e_mg if e["prov"] != "SHARED"]
    bc = [e for e in novel if sb.cbud(e, B0, B1) >= THRESH]
    bw = [e for e in bc if not e["right"]]; bwe = sb.established(bw, K, aq_mg)
    nom = sum(1 - sb.cbud(e, B0, B1) for e in bc)
    L.append("")
    L.append("  (1) PRIMARY on the %d NEW-verdict edges: called %d | wrong %d, established %d | nominal %.2f"
             % (len(novel), len(bc), len(bw), len(bwe), nom))
    if nom < 3.0:
        L.append("  -> UNDETERMINED: with a nominal of %.2f expected wrong calls, %d established against it cannot be" % (nom, len(bwe)))
        L.append("     told from calibrated. The registration pre-committed exactly this reading: transfer is")
        L.append("     UNTESTED, not demonstrated, and the parameter is published as roster-specific.")
    elif len(bwe) <= nom:
        L.append("  -> PASS on established labels: realised at or below nominal on pairs the budget never saw.")
    else:
        L.append("  -> FAIL on established labels: realised exceeds nominal; the parameter does not transfer.")
    frac = sum(1 for e in e_mg if sb.cbud(e, B0, B1) >= THRESH) / len(e_mg)
    L.append("  (2) UTILITY on the merged board: %.1f%% of edges still called (bar 60%%) -> %s" % (100 * frac, "PASS" if frac >= 0.60 else "FAIL"))
    f0, f1 = sb.fit(novel, x0=(B0, B1))
    fe = sb.established(novel, K, aq_mg)
    g0, g1 = sb.fit(fe, x0=(B0, B1)) if len(fe) > 100 else (float("nan"), float("nan"))
    L.append("  (3) b1 refit on NEW-verdict edges: all labels %+.4f | established labels %+.4f | x12 %+.4f, CI [1.72, 7.87]"
             % (f1, g1, B1))
    L.append("      a refit on a stratum with few wrong calls is weakly identified; report, do not adjudicate on it.")
    rc = [e for e in novel if sb.craw(e) >= THRESH]; rw = [e for e in rc if not e["right"]]
    L.append("  (4) raw certificate on NEW-verdict edges: %d called, %d wrong (%d established) = %.2f%% (%.2f%% established)"
             % (len(rc), len(rw), len(sb.established(rw, K, aq_mg)), 100.0 * len(rw) / max(1, len(rc)),
                100.0 * len(sb.established(rw, K, aq_mg)) / max(1, len(rc))))
    base_right = sum(1 for e in rc if e["right"])
    L.append("      budget: %d called, %d wrong (%d est), %d correct surrendered" % (len(bc), len(bw), len(bwe), base_right - sum(1 for e in bc if e["right"])))
    for t in (0.70, 0.80, 0.85):
        g = [e for e in rc if e["agree"] < t]; gw = [e for e in g if not e["right"]]
        L.append("      gate A < %.2f: %d called, %d wrong (%d est), %d correct surrendered"
                 % (t, len(g), len(gw), len(sb.established(gw, K, aq_mg)), base_right - sum(1 for e in g if e["right"])))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
