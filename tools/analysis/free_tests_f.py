"""F-series free tests (docs/f_series_free_tests.md, criteria frozen before this ran).

  python tools/analysis/free_tests_f.py f1 f2 f3      # or any subset

F1 certified-vs-uncertified ladder split · F2 keyed profile vs MMLU-Pro categories ·
F3 judge confidence calibration. Zero judge calls.
"""
import os, sys, csv, json, math, random, sqlite3
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf

LADDER_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_ladder.db")
SITE_CSV = os.path.join(ROOT, "docs", "data", "site_null_frozen.csv")
STRATA = os.path.join(ROOT, "experiment_configs", "strata_profile_v1.json")
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
TOP4 = jf.TOP4
B = 2000


def key_correct():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    return {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}


def frozen_tree():
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []):
            parent[c] = n["id"]
    return nodes, parent


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, i) * 0.5 ** n for i in range(k + 1)))


def boot_ci(values_by_cluster, stat, seed=42):
    """cluster bootstrap over dict cluster -> list of items; stat(list_of_items) -> float"""
    keys = list(values_by_cluster)
    rng = random.Random(seed)
    out = []
    for _ in range(B):
        samp = [it for k in (keys[rng.randrange(len(keys))] for _ in keys) for it in values_by_cluster[k]]
        out.append(stat(samp))
    out.sort()
    return out[int(0.025 * B)], out[int(0.975 * B) - 1]


# ── F1 ─────────────────────────────────────────────────────────────────────────
def f1():
    print("\n== F1: leaf-over-anchor rubric gain, certified vs uncertified leaves ==")
    nodes, parent = frozen_tree()
    cert = {r["node_id"] for r in csv.DictReader(open(SITE_CSV, newline="", encoding="utf-8")) if r["cert_site_p95"] == "true"}
    sites = {n["id"] for n in nodes.values() if len(n.get("childIds", [])) >= 2 and n.get("dasguptaDeltaNorm", 0) > 0 and n["depth"] >= 1}

    def stratum(leaf):
        n = nodes[leaf]
        if n["depth"] <= 1:
            return "anchor-leaf"          # leaf rubric == anchor rubric: no contrast
        path = []
        cur = parent.get(leaf)
        while cur is not None and nodes[cur]["depth"] >= 1:
            path.append(cur)
            cur = parent.get(cur)
        imm = path[0] in cert
        strict = all(p in cert for p in path if p in sites)
        return "CERT-STRICT" if strict else ("CERT-IMMEDIATE" if imm else "UNCERTIFIED")

    x12 = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    leaf_v = {r[0]: (int(r[1]), r[2], r[3], r[4], "TIE" if r[6] else r[5]) for r in x12.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
    lad = sqlite3.connect("file:%s?mode=ro" % LADDER_DB, uri=True)
    anc_v = {r[0]: r[1] for r in lad.execute("SELECT match_id, winner FROM verdicts WHERE arm='anchor' AND invalid=0")}
    G = key_correct()
    rows = defaultdict(list)   # stratum -> list of (qid, leaf_ok, anchor_ok)
    for mid, aw in anc_v.items():
        rec = leaf_v.get(mid)
        if rec is None:
            continue
        qid, ma, mb, nid, lw = rec
        ca, cb = G.get((qid, ma)), G.get((qid, mb))
        if ca is None or cb is None or ca == cb:
            continue
        dw = ma if ca else mb
        rows[stratum(nid)].append((qid, lw == dw, aw == dw))
    res = {}
    for s in ("CERT-STRICT", "CERT-IMMEDIATE", "UNCERTIFIED", "anchor-leaf"):
        r = rows.get(s, [])
        if not r:
            print("  %-15s n=0" % s); continue
        l = sum(x[1] for x in r) / len(r); a = sum(x[2] for x in r) / len(r)
        b = sum(1 for x in r if x[1] and not x[2]); c = sum(1 for x in r if x[2] and not x[1])
        res[s] = r
        print("  %-15s n=%4d | leaf %.3f  anchor %.3f  gain %+.3f | discordant %d:%d  McNemar p=%.3f"
              % (s, len(r), l, a, l - a, b, c, mcnemar_p(b, c)))
    def gain(items): return sum(x[1] for x in items) / len(items) - sum(x[2] for x in items) / len(items)
    for s in ("CERT-STRICT", "CERT-IMMEDIATE"):
        if s not in res or "UNCERTIFIED" not in res:
            continue
        cs = {}
        for tag, items in ((s, res[s]), ("U", res["UNCERTIFIED"])):
            d = defaultdict(list)
            for it in items: d[(tag, it[0])].append((tag,) + it)
            cs.update(d)
        def diff(samp):
            a = [x[1:] for x in samp if x[0] == s]; u = [x[1:] for x in samp if x[0] == "U"]
            return (gain(a) if a else 0.0) - (gain(u) if u else 0.0)
        lo, hi = boot_ci(cs, diff)
        d0 = gain(res[s]) - gain(res["UNCERTIFIED"])
        cert_items = res[s]
        b = sum(1 for x in cert_items if x[1] and not x[2]); c = sum(1 for x in cert_items if x[2] and not x[1])
        p = mcnemar_p(b, c)
        verdict = "PASS" if (gain(cert_items) > 0 and p < 0.05 and lo > 0) else ("UNDERPOWERED" if (hi - lo) > 0.10 else "FAIL")
        print("  %s minus UNCERTIFIED gain: %+.3f, question-bootstrap 95%% [%+.3f, %+.3f] -> %s%s"
              % (s, d0, lo, hi, verdict, " (REGISTERED PRIMARY)" if s == "CERT-STRICT" else " (secondary)"))


# ── F2 ─────────────────────────────────────────────────────────────────────────
def f2():
    print("\n== F2: keyed capability profile — embedding cells vs MMLU-Pro categories (LOO Brier) ==")
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    nq = ev.execute("SELECT COUNT(DISTINCT question_id) FROM eval_results").fetchone()[0]
    # Meta-Llama-3-70B-Instruct is excluded by the campaign's standing rule (its ingested
    # rows carry 8.4% wrong question texts — the only such model; all others 0.1%).
    models = [m for m, n in ev.execute("SELECT model_name, COUNT(DISTINCT question_id) FROM eval_results GROUP BY model_name")
              if n >= 0.95 * nq and m != "Meta-Llama-3-70B-Instruct"]
    cat = {q: c.lower() for q, c in ev.execute("SELECT question_id, category FROM eval_results GROUP BY question_id")}
    # Train-side id mapping: NEVER by eval_results.question_text (per-row, polluted by one
    # model's file). Snapshot query -> HF text -> mmlu_pro row -> OPTIONS key -> eval id;
    # options are distinctive (5 duplicate option-sets in 11,995 rows).
    def okey(o):
        try:
            return json.dumps(json.loads(o)) if o and o.strip().startswith("[") else o
        except Exception:
            return o
    mm_by_text = defaultdict(list)
    for i, qtext, o in ev.execute("SELECT id, question, options FROM mmlu_pro"):
        mm_by_text[qtext].append(okey(o))
    opts2eval = defaultdict(set)
    for q, o in ev.execute("SELECT question_id, options_json FROM eval_results GROUP BY question_id"):
        opts2eval[okey(o)].add(q)
    G = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models:
            G[m][q] = int(c or 0)
    # partitions
    nodes, parent = frozen_tree()
    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"].lower()
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    id2text = {i: t for i, t in emb.execute("SELECT id, raw_text FROM queries")}
    leaf_of = {}
    multi = Counter(qi for n in nodes.values() if not n.get("childIds") for qi in n.get("queryIds", []))
    for n in nodes.values():
        if n.get("childIds"):
            continue
        for qi in n.get("queryIds", []):
            if multi[qi] > 1:
                continue                      # soft multi-membership on the train side: ambiguous, dropped
            keys = mm_by_text.get(id2text.get(qi), [])
            if len(keys) != 1:
                continue
            qs = opts2eval.get(keys[0], set())
            if len(qs) == 1:
                leaf_of[next(iter(qs))] = n["id"]
    n_train = len(leaf_of)
    best = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8")):
        q = int(r["question_id"]); w = float(r["weight"].replace(",", "."))
        if q not in best or w > best[q][0]:
            best[q] = (w, r["leaf_id"])
    for q, (_, leaf) in best.items():
        leaf_of.setdefault(q, leaf)
    strata = json.load(open(STRATA))["strata"]
    leaf2stratum = {l: s["id"] for s in strata for l in s["leafIds"]}
    # a question is usable if every retained model has a row for it (per-model coverage
    # is >= 95%; the intersection keeps the LOO paired over identical question sets)
    qs = sorted(q for q in leaf_of if q in cat and all(q in G[m] for m in models))
    parts = {
        "category": {q: cat[q] for q in qs},
        "anchor": {q: anchor_of(leaf_of[q]) for q in qs},
        "leaf": {q: leaf_of[q] for q in qs},
        "stratum": {q: leaf2stratum.get(leaf_of[q], "?") for q in qs},
    }
    disagree = [q for q in qs if parts["anchor"][q] != parts["category"][q]]
    print("  questions %d (train-side via text join %d, reserved %d) | models %d | anchor != category on %d (%.1f%%)"
          % (len(qs), n_train, len(qs) - n_train, len(models), len(disagree), 100 * len(disagree) / len(qs)))

    def loo_improvement(part, subset):
        """per-question Brier improvement (marginal LOO minus cell LOO), averaged over models."""
        idx = {q: i for i, q in enumerate(qs)}
        imp = np.zeros(len(subset))
        for m in models:
            y = np.array([G[m][q] for q in qs], dtype=float)
            N = len(y); S = y.sum()
            cells = defaultdict(list)
            for i, q in enumerate(qs): cells[part[q]].append(i)
            csum = {c: y[ix].sum() for c, ix in cells.items()}; cn = {c: len(ix) for c, ix in cells.items()}
            for j, q in enumerate(subset):
                i = idx[q]; c = part[q]
                marg = (S - y[i]) / (N - 1)
                cell = (csum[c] - y[i]) / (cn[c] - 1) if cn[c] > 1 else marg
                imp[j] += (marg - y[i]) ** 2 - (cell - y[i]) ** 2
        return imp / len(models)

    for label, subset in (("ALL questions", qs), ("DISAGREEMENT subset", disagree)):
        imps = {p: loo_improvement(parts[p], subset) for p in parts}
        print("  -- %s (n=%d): mean LOO Brier improvement over the marginal (x1000) --" % (label, len(subset)))
        for p in ("category", "anchor", "stratum", "leaf"):
            print("     %-9s %+7.2f" % (p, 1000 * imps[p].mean()))
        rng = random.Random(42)
        for p, tag in (("anchor", "REGISTERED PRIMARY"), ("stratum", "secondary"), ("leaf", "secondary")):
            d = imps[p] - imps["category"]
            bs = sorted(float(d[[rng.randrange(len(d)) for _ in range(len(d))]].mean()) for _ in range(B))
            lo, hi = bs[int(0.025 * B)], bs[int(0.975 * B) - 1]
            print("     %s - category: %+7.2f  95%% [%+.2f, %+.2f] -> %s (%s)"
                  % (p, 1000 * d.mean(), 1000 * lo, 1000 * hi, "WINS" if lo > 0 else ("LOSES" if hi < 0 else "TIE"), tag))


# ── F3 ─────────────────────────────────────────────────────────────────────────
def f3():
    print("\n== F3: judge confidence calibration (R2 live, key-decidable, decisive) ==")
    rows = []
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Rationale"].startswith("Reconstructed") or r["Winner"] == "TIE":
                continue
            ca, cb = r["CorrectA"] == "true", r["CorrectB"] == "true"
            if ca == cb:
                continue
            won_a = r["Winner"] == "Model A"
            rows.append((float(r["Confidence"]), int(won_a == ca)))
    conf = np.array([c for c, _ in rows]); ok = np.array([o for _, o in rows])
    print("  n=%d | accuracy %.3f | mean confidence %.3f" % (len(rows), ok.mean(), conf.mean()))
    bins = np.linspace(0.5, 1.0, 11)
    ece = 0.0
    print("  bin        n    conf   acc")
    for lo, hi in zip(bins[:-1], bins[1:]):
        sel = (conf >= lo) & (conf < hi + (1e-9 if hi == 1.0 else 0))
        if sel.sum() == 0: continue
        ece += sel.sum() / len(rows) * abs(conf[sel].mean() - ok[sel].mean())
        print("  [%.2f,%.2f) %5d  %.3f  %.3f" % (lo, hi, sel.sum(), conf[sel].mean(), ok[sel].mean()))
    pos, neg = conf[ok == 1], conf[ok == 0]
    def auc(p, n):
        allv = np.concatenate([p, n]); ranks = allv.argsort().argsort() + 1.0
        # tie-aware ranks
        order = np.argsort(allv); sv = allv[order]; r = np.empty(len(allv)); i = 0
        while i < len(sv):
            j = i
            while j + 1 < len(sv) and sv[j + 1] == sv[i]: j += 1
            r[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
        return (r[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
    a0 = auc(pos, neg)
    rng = np.random.default_rng(42)
    bs = sorted(auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(500))
    lo, hi = bs[12], bs[487]
    informative = lo > 0.5 and ece < 0.10
    print("  ECE %.3f | AUC %.3f [%.3f, %.3f] -> REGISTERED: confidence %s" % (ece, a0, lo, hi, "INFORMATIVE" if informative else "NOT informative"))
    # descriptive: confidence-weighted board
    r2 = jf.load_live(jf.R2)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, _ = jf.gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    confs = {}
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            confs[(int(r["QueryId"]), r["ModelA"], r["ModelB"])] = float(r["Confidence"])
    raw = jf.board_from(jf.current_votes(r2), models)
    wtd = jf.board_from(((r["a"], r["b"], (0.5 if r["w"] == "TIE" else (1.0 if r["w"] == r["a"] else 0.0)) * max(0.05, confs.get((r["q"], r["a"], r["b"]), 0.5)),
                          max(0.05, confs.get((r["q"], r["a"], r["b"]), 0.5))) for r in r2), models)
    for name, th in (("raw", raw), ("confidence-weighted", wtd)):
        o, pv, _ = jf.violations(th, gt_order)
        print("  board %-20s rho %.4f | top-4 %s (violations %d)" % (name, jf.rho(th, acc, models), " > ".join(o), pv))


if __name__ == "__main__":
    which = [a.lower() for a in sys.argv[1:]] or ["f1", "f2", "f3"]
    for w in which:
        {"f1": f1, "f2": f2, "f3": f3}[w]()
