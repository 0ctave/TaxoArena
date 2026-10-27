"""TaxoArena bias-audit panel (hardening roadmap H1-H6 + verbosity mechanism).

One rerunnable tool consolidating the 2026-09-07 free battery. Every check reads
committed campaign artifacts; nothing here spends judge calls. Run all panels:

    python tools/analysis/bias_audit.py            # all panels, default DBs
    python tools/analysis/bias_audit.py h3 h6      # selected panels

Panels:
  h1  rubric-induced per-model theta shift, bootstrap CIs (cell vs generic arm)
  h2  rubric content scan: answer-leakage patterns over all 87 cell rubrics
  h3  length bias: logistic verdict ~ lengthDiff + gtDiff per judge arm, plus the
      length-matched top-cluster refit (the verbosity-mechanism check)
  h4  order-bias sweep over node_pair_stats + a matched order-symmetric null
  h5  routing anchor purity vs MMLU-Pro categories (primary assignment)
  h6  board invariance to cell weighting (raw / per-leaf / pool / per-anchor)

Findings this panel produced (2026-09-07, x12 + R2 + rubric-contrast data):
  h1 no model's shift excludes 0 (max +0.14) · h2 zero leakage hits ·
  h3 beta_len=+0.39/1k chars z=14.6 all arms; length-matched refit flips the top
     cluster to near-GT order in x12 AND R2 · h4 5.0% flagged vs 3.0% chance ·
  h5 73.6% purity, flows on ambiguous boundaries · h6 ordering identical, rho=1.
"""
import sys, os, csv, math, re, json, sqlite3, random, statistics
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc

X12_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "ratings_x12.db")
R2_DB = os.path.join(ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
ASSIGN = os.path.join(ROOT, "reserved_leaf_assignments.csv")
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]


def _fit(rows, models):
    agg = defaultdict(lambda: [0.0, 0.0])
    for w, ma, mb in rows:
        a, b = min(ma, mb), max(ma, mb)
        rec = agg[(a, b)]
        rec[1] += 1
        if w == "TIE":
            rec[0] += 0.5
        elif w == a:
            rec[0] += 1.0
    return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models)


def _x12_rows():
    con = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    rows = con.execute(
        "SELECT id, eval_question_id, model_a, model_b, winner, is_tie FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,)).fetchall()
    con.close()
    return rows


def _anchor_fn():
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []):
            parent[c] = n["id"]

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    return nodes, anchor


# ── H1 ─────────────────────────────────────────────────────────────────────────
def h1(B=300, seed=42):
    print("\n== H1: rubric-induced per-model shift (theta_cell - theta_generic) ==")
    cell = [("TIE" if t else w, ma, mb) for _, _, ma, mb, w, t in _x12_rows()]
    cache = sqlite3.connect("file:%s?mode=ro" % rc.CACHE_DB, uri=True)
    gen = [(w, ma, mb) for ma, mb, w in cache.execute(
        "SELECT model_a, model_b, winner FROM verdicts "
        "WHERE judge='mistral' AND rubric='generic' AND invalid=0")]
    models = sorted({m for _, a, b in cell for m in (a, b)})
    th_c, th_g = _fit(cell, models), _fit(gen, models)
    rng = random.Random(seed)
    boots = defaultdict(list)
    for _ in range(B):
        bc = _fit([cell[rng.randrange(len(cell))] for _ in range(len(cell))], models)
        bg = _fit([gen[rng.randrange(len(gen))] for _ in range(len(gen))], models)
        for m in models:
            boots[m].append(bc[m] - bg[m])
    flagged = 0
    for m in sorted(models, key=lambda m: -(th_c[m] - th_g[m])):
        bs = sorted(boots[m])
        lo, hi = bs[int(0.025 * B)], bs[int(0.975 * B)]
        sig = lo > 0 or hi < 0
        flagged += sig
        print("  %-30s %+7.3f [%+.3f, %+.3f]%s"
              % (m, th_c[m] - th_g[m], lo, hi, "  <-- EXCLUDES 0" if sig else ""))
    print("  models whose CI excludes 0: %d of %d" % (flagged, len(models)))


# ── H2 ─────────────────────────────────────────────────────────────────────────
def h2():
    print("\n== H2: rubric content scan (answer leakage) ==")
    nodes, _ = _anchor_fn()
    leaves = [n for n in nodes.values() if not n.get("childIds")]
    pats = {
        "option letter answer": re.compile(
            r"answer\s+is\s+\(?[A-J]\)?|correct\s+(option|answer)\s*(is|:)\s*\(?[A-J]\)?", re.I),
        "explicit option ref": re.compile(r"\boption\s+\(?[A-J]\)\b"),
        "numeric = answer": re.compile(r"correct\s+(value|result|answer)\s*(is|=)\s*[-+]?\d"),
        "TODO/FIXME": re.compile(r"TODO|FIXME|XXX"),
    }
    total_hits = 0
    for k, p in pats.items():
        hits = [(l["id"], f) for l in leaves for f in ("judgeRubric", "judgePrompt")
                if p.search(l.get(f) or "")]
        total_hits += len(hits)
        print("  %-24s %d hit(s) %s" % (k, len(hits), hits[:3] if hits else ""))
    print("  rubrics scanned: %d | total hits: %d" % (len(leaves), total_hits))


# ── H3 ─────────────────────────────────────────────────────────────────────────
def _lengths_gt():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L, G = {}, {}
    for q, m, out, ok in ev.execute(
            "SELECT question_id, model_name, model_output, is_correct FROM eval_results"):
        L[(q, m)] = len(out or "")
        G[(q, m)] = ok or 0
    return L, G


def _logit3(X, Y):
    b = [0.0, 0.0, 0.0]
    H = None
    for _ in range(50):
        g = [0.0] * 3
        H = [[1e-9] * 3 for _ in range(3)]
        for (x1, x2), y in zip(X, Y):
            z = max(-30, min(30, b[0] + b[1] * x1 + b[2] * x2))
            p = 1 / (1 + math.exp(-z))
            xs = (1.0, x1, x2)
            for i in range(3):
                g[i] += (y - p) * xs[i]
                for j in range(3):
                    H[i][j] += p * (1 - p) * xs[i] * xs[j]

        def solve(mat, rhs):
            A = [mat[i][:] + [rhs[i]] for i in range(3)]
            for i in range(3):
                piv = A[i][i]
                for j in range(i + 1, 3):
                    f = A[j][i] / piv
                    for k in range(4):
                        A[j][k] -= f * A[i][k]
            d = [0.0] * 3
            for i in (2, 1, 0):
                d[i] = (A[i][3] - sum(A[i][k] * d[k] for k in range(i + 1, 3))) / A[i][i]
            return d
        d = solve(H, g)
        b = [b[i] + d[i] for i in range(3)]
        if max(abs(x) for x in d) < 1e-9:
            break
    ses = []
    for i in range(3):
        e = [1.0 if j == i else 0.0 for j in range(3)]
        A = [H[r][:] + [e[r]] for r in range(3)]
        for r in range(3):
            piv = A[r][r]
            for j in range(r + 1, 3):
                f = A[j][r] / piv
                for k in range(4):
                    A[j][k] -= f * A[r][k]
        d = [0.0] * 3
        for r in (2, 1, 0):
            d[r] = (A[r][3] - sum(A[r][k] * d[k] for k in range(r + 1, 3))) / A[r][r]
        ses.append(math.sqrt(max(0.0, d[i])))
    return b, ses


def h3(match_len_threshold=300):
    print("\n== H3: length bias (verdict ~ lengthDiff/1k + gtDiff, decisive only) ==")
    L, G = _lengths_gt()
    x12 = _x12_rows()
    arms = {"mistral/cell": [(int(q), ma, mb, "TIE" if t else w) for _, q, ma, mb, w, t in x12]}
    qid_of = {mid: int(q) for mid, q, *_ in x12}
    cache = sqlite3.connect("file:%s?mode=ro" % rc.CACHE_DB, uri=True)
    arms["mistral/generic"] = [(qid_of[mid], a, b, w) for mid, a, b, w in cache.execute(
        "SELECT match_id, model_a, model_b, winner FROM verdicts "
        "WHERE judge='mistral' AND rubric='generic' AND invalid=0") if mid in qid_of]
    r3 = sqlite3.connect("file:%s?mode=ro" % rc.R3_DB, uri=True)
    mm = {mid: (ma, mb) for mid, _, ma, mb, *_ in x12}
    arms["grok/cell"] = [(qid_of[mid], mm[mid][0], mm[mid][1], w) for mid, w in r3.execute(
        "SELECT match_id, grok_winner FROM verdicts WHERE grok_invalid=0") if mid in qid_of]
    for name, rows in arms.items():
        X, Y = [], []
        for qid, ma, mb, w in rows:
            la, lb = L.get((qid, ma)), L.get((qid, mb))
            if la is None or lb is None or w not in (ma, mb):
                continue
            X.append(((la - lb) / 1000.0, (G.get((qid, ma), 0)) - (G.get((qid, mb), 0))))
            Y.append(1.0 if w == ma else 0.0)
        b, s = _logit3(X, Y)
        print("  %-16s n=%5d | beta_len %+0.4f (z=%+.1f) | beta_gt %+0.3f (z=%+.1f)"
              % (name, len(Y), b[1], b[1] / s[1], b[2], b[2] / s[2]))

    print("  -- length-matched top-cluster refit (|dlen| <= %d chars) --" % match_len_threshold)
    for name, db in (("x12", X12_DB), ("R2 ", R2_DB)):
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        allr, matched = [], []
        for ma, mb, w, t, q in con.execute(
                "SELECT model_a, model_b, winner, is_tie, eval_question_id "
                "FROM match_history WHERE condition='MAIN'"):
            if ma not in TOP4 or mb not in TOP4:
                continue
            w = "TIE" if t else w
            allr.append((w, ma, mb))
            la, lb = L.get((int(q), ma)), L.get((int(q), mb))
            if la is not None and lb is not None and abs(la - lb) <= match_len_threshold:
                matched.append((w, ma, mb))
        ba, bm = _fit(allr, TOP4), _fit(matched, TOP4)
        print("  %s all(n=%d):     %s" % (name, len(allr),
              " > ".join(sorted(TOP4, key=lambda m: -ba[m]))))
        print("  %s matched(n=%d): %s" % (name, len(matched),
              " > ".join(sorted(TOP4, key=lambda m: -bm[m]))))


# ── H4 ─────────────────────────────────────────────────────────────────────────
def h4(sims=400, seed=7):
    print("\n== H4: order-bias sweep (|winAFirst-winASecond|/n > 0.3, n >= 6) ==")
    for name, db in (("x12", X12_DB), ("R2 ", R2_DB)):
        c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        rows = c.execute(
            "SELECT wins_a, wins_b, ties, win_a_first, win_a_second, total_comparisons "
            "FROM node_pair_stats WHERE total_comparisons >= 6").fetchall()
        rng = random.Random(seed)
        obs = exp = 0.0
        for wa, wb, t, w1, w2, n in rows:
            n = int(n)
            if abs((w1 or 0) - (w2 or 0)) / n > 0.3:
                obs += 1
            p = [wa / n, t / n, wb / n]
            hits = 0
            for _ in range(sims):
                d = sum(rng.choices([1.0, 0.5, 0.0], weights=p)[0]
                        - rng.choices([1.0, 0.5, 0.0], weights=p)[0] for _ in range(n))
                if abs(d) / n > 0.3:
                    hits += 1
            exp += hits / sims
        k = max(1, len(rows))
        print("  %s eligible %4d | flagged %.1f%% | chance-expected %.1f%%"
              % (name, len(rows), 100 * obs / k, 100 * exp / k))


# ── H5 ─────────────────────────────────────────────────────────────────────────
def h5():
    print("\n== H5: routing anchor purity vs MMLU-Pro category (primary assignment) ==")
    _, anchor = _anchor_fn()
    best = {}
    with open(ASSIGN, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            q = int(row['question_id'])
            w = float(row['weight'].replace(',', '.'))
            if q not in best or w > best[q][0]:
                best[q] = (w, row['leaf_id'], row['category'])
    agree = Counter()
    total = Counter()
    confus = Counter()
    for q, (w, leaf, cat) in best.items():
        a = anchor(leaf)
        total[cat] += 1
        if a == cat:
            agree[cat] += 1
        else:
            confus[(cat, a)] += 1
    n = sum(total.values())
    print("  overall purity %.1f%% (%d/%d)" % (100 * sum(agree.values()) / n, sum(agree.values()), n))
    for (c, a), k in confus.most_common(5):
        print("  flow %-16s -> %-16s %d" % (c, a, k))


# ── H6 ─────────────────────────────────────────────────────────────────────────
def h6():
    print("\n== H6: board invariance to cell weighting (x12) ==")
    _, anchor = _anchor_fn()
    by_leaf = defaultdict(list)
    con = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    for nid, ma, mb, w, t in con.execute(
            "SELECT node_id, model_a, model_b, winner, is_tie FROM match_history "
            "WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,)):
        by_leaf[nid].append(("TIE" if t else w, ma, mb))
    models = sorted({m for ms in by_leaf.values() for _, a, b in ms for m in (a, b)})
    pool = defaultdict(set)
    with open(ASSIGN, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            pool[r['leaf_id']].add(int(r['question_id']))
    n_anchor = defaultdict(int)
    for leaf, ms in by_leaf.items():
        n_anchor[anchor(leaf)] += len(ms)

    def wboard(leaf_w):
        agg = defaultdict(lambda: [0.0, 0.0])
        for leaf, ms in by_leaf.items():
            wgt = leaf_w(leaf, len(ms))
            for w, ma, mb in ms:
                a, b = min(ma, mb), max(ma, mb)
                rec = agg[(a, b)]
                rec[1] += wgt
                if w == "TIE":
                    rec[0] += 0.5 * wgt
                elif w == a:
                    rec[0] += wgt
        return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models)

    base = wboard(lambda l, n: 1.0)
    order0 = sorted(models, key=lambda m: -base[m])
    for name, fn in (("uniform per leaf", lambda l, n: 1.0 / n),
                     ("pool-proportional", lambda l, n: len(pool.get(l, [1])) / n),
                     ("uniform per anchor", lambda l, n: 1.0 / n_anchor[anchor(l)])):
        b = wboard(fn)
        order = sorted(models, key=lambda m: -b[m])
        print("  %-20s rho %.4f | order %s"
              % (name, rj.spearman([base[m] for m in models], [b[m] for m in models]),
                 "IDENTICAL" if order == order0 else " > ".join(order)))


PANELS = {"h1": h1, "h2": h2, "h3": h3, "h4": h4, "h5": h5, "h6": h6}

if __name__ == "__main__":
    which = [a.lower() for a in sys.argv[1:]] or list(PANELS)
    for name in which:
        PANELS[name]()
