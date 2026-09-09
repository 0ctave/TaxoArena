"""F4-F7 (docs/f_series_free_tests.md, registered c06d154 before running). Zero judge calls.

  python tools/analysis/free_tests_f4_f7.py f4 f5 f6 f7
"""
import os, sys, csv, json, random, sqlite3, struct
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf
import consensus_tree as ct
from free_tests_f import frozen_tree, key_correct, mcnemar_p, boot_ci, SITE_CSV, EMB_DB, TOP4, B


def leaf_stratum_fn():
    nodes, parent = frozen_tree()
    cert = {r["node_id"] for r in csv.DictReader(open(SITE_CSV, newline="", encoding="utf-8")) if r["cert_site_p95"] == "true"}
    sites = {n["id"] for n in nodes.values() if len(n.get("childIds", [])) >= 2 and n.get("dasguptaDeltaNorm", 0) > 0 and n["depth"] >= 1}

    def stratum(leaf):
        n = nodes[leaf]
        if n["depth"] <= 1:
            return "anchor-leaf"
        path = []
        cur = parent.get(leaf)
        while cur is not None and nodes[cur]["depth"] >= 1:
            path.append(cur)
            cur = parent.get(cur)
        imm = path[0] in cert
        strict = all(p in cert for p in path if p in sites)
        return "CERT-STRICT" if strict else ("CERT-IMMEDIATE" if imm else "UNCERTIFIED")
    return stratum


def paired_gain_report(rows, label_a, label_b, primary_stratum="CERT-STRICT"):
    def gain(items):
        return sum(x[1] for x in items) / len(items) - sum(x[2] for x in items) / len(items)
    for s in ("CERT-STRICT", "CERT-IMMEDIATE", "UNCERTIFIED"):
        r = rows.get(s, [])
        if not r:
            print("  %-15s n=0" % s)
            continue
        b = sum(1 for x in r if x[1] and not x[2])
        c = sum(1 for x in r if x[2] and not x[1])
        print("  %-15s n=%4d | %s %.3f  %s %.3f  gain %+.3f | discordant %d:%d  McNemar p=%.3f"
              % (s, len(r), label_a, sum(x[1] for x in r) / len(r), label_b, sum(x[2] for x in r) / len(r),
                 gain(r), b, c, mcnemar_p(b, c)))
    for s in ("CERT-STRICT", "CERT-IMMEDIATE"):
        if s not in rows or "UNCERTIFIED" not in rows:
            continue
        cs = {}
        for tag, items in ((s, rows[s]), ("U", rows["UNCERTIFIED"])):
            d = defaultdict(list)
            for it in items:
                d[(tag, it[0])].append((tag,) + it)
            cs.update(d)

        def diff(samp):
            a = [x[1:] for x in samp if x[0] == s]
            u = [x[1:] for x in samp if x[0] == "U"]
            return (gain(a) if a else 0.0) - (gain(u) if u else 0.0)
        lo, hi = boot_ci(cs, diff)
        cert_items = rows[s]
        b = sum(1 for x in cert_items if x[1] and not x[2])
        c = sum(1 for x in cert_items if x[2] and not x[1])
        p = mcnemar_p(b, c)
        verdict = "PASS" if (gain(cert_items) > 0 and p < 0.05 and lo > 0) else ("UNDERPOWERED" if (hi - lo) > 0.10 else "FAIL")
        print("  %s minus UNCERTIFIED gain: %+.3f, question-bootstrap 95%% [%+.3f, %+.3f] -> %s%s"
              % (s, gain(cert_items) - gain(rows["UNCERTIFIED"]), lo, hi, verdict,
                 " (REGISTERED PRIMARY)" if s == primary_stratum else " (secondary)"))


# ── F4 ─────────────────────────────────────────────────────────────────────────
def f4():
    print("\n== F4: cell-over-SIBLING rubric gain, certified vs uncertified leaves (H7 swap_sibling arm) ==")
    stratum = leaf_stratum_fn()
    x12 = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    leaf_v = {r[0]: (int(r[1]), r[2], r[3], r[4], "TIE" if r[6] else r[5]) for r in x12.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
    sw = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_swap.db"), uri=True)
    sib = {r[0]: r[1] for r in sw.execute("SELECT match_id, winner FROM verdicts WHERE arm='swap_sibling' AND invalid=0")}
    G = key_correct()
    rows = defaultdict(list)
    for mid, sw_w in sib.items():
        rec = leaf_v.get(mid)
        if rec is None:
            continue
        qid, ma, mb, nid, cw = rec
        ca, cb = G.get((qid, ma)), G.get((qid, mb))
        if ca is None or cb is None or ca == cb:
            continue
        dw = ma if ca else mb
        rows[stratum(nid)].append((qid, cw == dw, sw_w == dw))
    paired_gain_report(rows, "cell", "sibling")


# ── shared keyed-question loader (F5/F6) ────────────────────────────────────────
def okey(o):
    try:
        return json.dumps(json.loads(o)) if o and o.strip().startswith("[") else o
    except Exception:
        return o


def keyed_questions():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    nq = ev.execute("SELECT COUNT(DISTINCT question_id) FROM eval_results").fetchone()[0]
    models = [m for m, n in ev.execute("SELECT model_name, COUNT(DISTINCT question_id) FROM eval_results GROUP BY model_name")
              if n >= 0.95 * nq and m != "Meta-Llama-3-70B-Instruct"]
    opts2mm = defaultdict(list)
    for i, qtext, o in ev.execute("SELECT id, question, options FROM mmlu_pro"):
        opts2mm[okey(o)].append(qtext)
    text = {}
    for q, o in ev.execute("SELECT question_id, options_json FROM eval_results GROUP BY question_id"):
        ts = opts2mm.get(okey(o), [])
        if len(ts) == 1:
            text[q] = ts[0]
    cat = {q: c.lower() for q, c in ev.execute("SELECT question_id, category FROM eval_results GROUP BY question_id")}
    G = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models and q in text:
            G[m][q] = int(c or 0)
    qs = sorted(q for q in text if q in cat and all(q in G[m] for m in models))
    return models, G, cat, {q: text[q] for q in qs}, qs


def loo_imp(part, qs, models, G):
    imp = np.zeros(len(qs))
    for m in models:
        y = np.array([G[m][q] for q in qs], dtype=float)
        N = len(y)
        S = y.sum()
        cells = defaultdict(list)
        for i, q in enumerate(qs):
            cells[part[q]].append(i)
        csum = {c: y[ix].sum() for c, ix in cells.items()}
        cn = {c: len(ix) for c, ix in cells.items()}
        for i, q in enumerate(qs):
            c = part[q]
            marg = (S - y[i]) / (N - 1)
            cell = (csum[c] - y[i]) / (cn[c] - 1) if cn[c] > 1 else marg
            imp[i] += (marg - y[i]) ** 2 - (cell - y[i]) ** 2
    return imp / len(models)


def boot_mean_ci(d, seed=42):
    rng = random.Random(seed)
    d = np.asarray(d)
    n = len(d)
    bs = sorted(float(d[[rng.randrange(n) for _ in range(n)]].mean()) for _ in range(B))
    return bs[int(0.025 * B)], bs[int(0.975 * B) - 1]


# ── F5 ─────────────────────────────────────────────────────────────────────────
def f5():
    print("\n== F5: leaf-over-category LOO improvement by leaf certification (frozen tree, F2 mapping) ==")
    models, G, cat, text, qs_all = keyed_questions()
    nodes, parent = frozen_tree()
    text2q = {t: q for q, t in text.items()}
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    id2text = {i: t for i, t in emb.execute("SELECT id, raw_text FROM queries")}
    multi = Counter(qi for n in nodes.values() if not n.get("childIds") for qi in n.get("queryIds", []))
    leaf_of = {}
    for n in nodes.values():
        if n.get("childIds"):
            continue
        for qi in n.get("queryIds", []):
            if multi[qi] > 1:
                continue
            q = text2q.get(id2text.get(qi))
            if q is not None:
                leaf_of[q] = n["id"]
    best = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8")):
        q = int(r["question_id"])
        w = float(r["weight"].replace(",", "."))
        if q not in best or w > best[q][0]:
            best[q] = (w, r["leaf_id"])
    for q, (_, leaf) in best.items():
        leaf_of.setdefault(q, leaf)
    qs = [q for q in qs_all if q in leaf_of]
    stratum = leaf_stratum_fn()
    d = loo_imp({q: leaf_of[q] for q in qs}, qs, models, G) - loo_imp({q: cat[q] for q in qs}, qs, models, G)
    groups = defaultdict(list)
    for i, q in enumerate(qs):
        groups[stratum(leaf_of[q])].append(d[i])
    res = {}
    for s in ("CERT-STRICT", "CERT-IMMEDIATE", "UNCERTIFIED", "anchor-leaf"):
        v = groups.get(s, [])
        if not v:
            print("  %-15s n=0" % s)
            continue
        lo, hi = boot_mean_ci(v)
        res[s] = (np.mean(v), lo, hi)
        print("  %-15s n=%5d | leaf - category improvement (x1000) %+6.2f  95%% [%+.2f, %+.2f]"
              % (s, len(v), 1000 * np.mean(v), 1000 * lo, 1000 * hi))
    u = res.get("UNCERTIFIED")
    print("  REGISTERED PRIMARY (positive within UNCERTIFIED leaves): %s" % ("PASS" if u and u[1] > 0 else "FAIL"))
    if "CERT-STRICT" in res and u:
        a = np.array(groups["CERT-STRICT"])
        b = np.array(groups["UNCERTIFIED"])
        rng = random.Random(7)
        bs = sorted(float(a[[rng.randrange(len(a)) for _ in range(len(a))]].mean()
                          - b[[rng.randrange(len(b)) for _ in range(len(b))]].mean()) for _ in range(B))
        print("  secondary CERT-STRICT minus UNCERTIFIED: %+.2f  95%% [%+.2f, %+.2f]"
              % (1000 * (a.mean() - b.mean()), 1000 * bs[int(0.025 * B)], 1000 * bs[int(0.975 * B) - 1]))


# ── F6 ─────────────────────────────────────────────────────────────────────────
TREES = [
    ("frozen", None, EMB_DB),
    ("d256_s137", "experiment_results/dimsweep/d256_s137/seed_137", EMB_DB),
    ("d512_s137", "experiment_results/dimsweep/d512_s137/seed_137", EMB_DB),
    ("d512_s2048", "experiment_results/dimsweep/d512_s2048/seed_2048", EMB_DB),
    ("abt2_s137", "experiment_results/dimsweep/abt2_s137/seed_137", EMB_DB),
    ("abt2_s2048", "experiment_results/dimsweep/abt2_s2048/seed_2048", EMB_DB),
    ("nomic", "experiment_results/h9_embed_nomic/seed_42", os.path.join(ROOT, "embeddings_cache_nomic-embed-text_latest.db")),
]
# D2 trees (registered clause (ii) of D2 uses the leaf-level loss vs frozen): `f6 d2` adds them.
TREES_D2 = [
    ("bareq512_s137", "experiment_results/dimsweep2/bareq512_s137/seed_137", EMB_DB),
    ("bareq512_s2048", "experiment_results/dimsweep2/bareq512_s2048/seed_2048", EMB_DB),
    ("abt2d512_s137", "experiment_results/dimsweep2/abt2d512_s137/seed_137", EMB_DB),
    ("abt2d512_s2048", "experiment_results/dimsweep2/abt2d512_s2048/seed_2048", EMB_DB),
    ("abt1_s137", "experiment_results/dimsweep2/abt1_s137/seed_137", EMB_DB),
    ("abt1_s2048", "experiment_results/dimsweep2/abt1_s2048/seed_2048", EMB_DB),
]
TREES_D3 = [
    ("bareq1024_s137", "experiment_results/dimsweep3/bareq1024_s137/seed_137", EMB_DB),
    ("bareq1024_s2048", "experiment_results/dimsweep3/bareq1024_s2048/seed_2048", EMB_DB),
    ("bareq512_s137", "experiment_results/dimsweep2/bareq512_s137/seed_137", EMB_DB),
    ("bareq512_s2048", "experiment_results/dimsweep2/bareq512_s2048/seed_2048", EMB_DB),
]
if "d2" in sys.argv:
    TREES = [TREES[0]] + TREES_D2
if "d3" in sys.argv:
    TREES = [TREES[0]] + TREES_D3


def tree_leaves(run_dir):
    if run_dir is None:
        nodes = rj.load_nodes()
        lst = list(nodes.values())
    else:
        lst = ct.last_snapshot(os.path.join(ROOT, run_dir))["nodes"]
        nodes = {n["id"]: n for n in lst}
    parent = {c: n["id"] for n in lst for c in n.get("childIds", [])}

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    return [(n["id"], np.array(n["vmfMu"], dtype=np.float64), anchor(n["id"])) for n in lst if not n.get("childIds")]


def embed_matrix(db, texts, dim):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    want = set(texts)
    vec = {}
    for t, blob in con.execute("SELECT query, vector FROM embeddings"):
        if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
            v = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)[:dim]
            n = np.linalg.norm(v)
            if n > 0:
                vec[t] = v / n
    return vec


def f6():
    print("\n== F6: key-only validation of construction variants (nearest-centroid cells, LOO Brier) ==")
    models, G, cat, text, qs_all = keyed_questions()
    per_q = {}
    for name, run_dir, db in TREES:
        if run_dir and not os.path.exists(os.path.join(ROOT, run_dir, "dag_snapshots.jsonl")):
            print("  %-11s (build not present, skipped)" % name)
            continue
        leaves = tree_leaves(run_dir)
        dim = len(leaves[0][1])
        vec = embed_matrix(db, list(text.values()), dim)
        qs = [q for q in qs_all if text[q] in vec]
        Q = np.stack([vec[text[q]] for q in qs])
        M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
        idx = np.argmax(Q @ M.T, axis=1)
        leaf_p = {q: leaves[i][0] for q, i in zip(qs, idx)}
        anc_p = {q: leaves[i][2].lower() for q, i in zip(qs, idx)}
        il = loo_imp(leaf_p, qs, models, G)
        ia = loo_imp(anc_p, qs, models, G)
        ic = loo_imp({q: cat[q] for q in qs}, qs, models, G)
        per_q[name] = dict(zip(qs, il))
        agree = sum(anc_p[q] == cat[q] for q in qs) / len(qs)
        print("  %-11s dim %3d leaves %3d | n=%d | LOO improvement x1000: leaf %+6.2f  anchor %+6.2f  (category %+6.2f) | anchor==category %.1f%%"
              % (name, dim, len(leaves), len(qs), 1000 * il.mean(), 1000 * ia.mean(), 1000 * ic.mean(), 100 * agree))
    fl = per_q["frozen"]
    print("  -- paired difference vs frozen (leaf level, x1000; REGISTERED: d512/abt2 >= -0.5 with CI upper > 0) --")
    for name, l in per_q.items():
        if name == "frozen":
            continue
        common = [q for q in l if q in fl]
        d = np.array([l[q] - fl[q] for q in common])
        lo, hi = boot_mean_ci(d)
        tag = ""
        if name.startswith(("d512", "abt2")):
            tag = "  -> %s" % ("PASS" if (d.mean() >= -0.0005 and hi > 0) else "FAIL")
        print("     %-11s %+6.2f  95%% [%+.2f, %+.2f]%s" % (name, 1000 * d.mean(), 1000 * lo, 1000 * hi, tag))


# ── F7 ─────────────────────────────────────────────────────────────────────────
def f7():
    print("\n== F7: within-top-4 length coefficient by verdict confidence (R2 live) ==")
    r2 = jf.load_live(jf.R2)
    confs = {}
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            confs[(int(r["QueryId"]), r["ModelA"], r["ModelB"])] = float(r["Confidence"])
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, L = jf.gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    top = [r for r in r2 if r["a"] in TOP4 and r["b"] in TOP4]
    bands = [("< 0.85", lambda c: c < 0.85), ("0.85-0.95", lambda c: 0.85 <= c < 0.95), (">= 0.95", lambda c: c >= 0.95)]
    est = {}
    for name, fn in bands:
        sub = [r for r in top if fn(confs.get((r["q"], r["a"], r["b"]), 0.5))]
        if len(sub) < 100:
            print("  band %-9s n=%d (too few)" % (name, len(sub)))
            continue
        theta, bl, se, n = jf.lc_bt(sub, L, TOP4)
        est[name] = (bl, se)
        ties = sum(r["w"] == "TIE" for r in sub) / len(sub)
        print("  band %-9s n=%5d (ties %.2f) | beta_len %+.3f/1k  95%% [%+.3f, %+.3f]"
              % (name, len(sub), ties, bl, bl - 1.96 * se, bl + 1.96 * se))
    if "< 0.85" in est and ">= 0.95" in est:
        (b1, s1), (b3, s3) = est["< 0.85"], est[">= 0.95"]
        sep = (b1 - 1.96 * s1) > (b3 + 1.96 * s3)
        print("  REGISTERED PRIMARY (beta(<0.85) > beta(>=0.95), non-overlapping CIs): %s" % ("PASS" if (b1 > b3 and sep) else "FAIL"))
    gated = [r for r in top if confs.get((r["q"], r["a"], r["b"]), 0.5) >= 0.95]
    th = jf.board_from(jf.current_votes(gated), TOP4)
    o, pv, _ = jf.violations(th, gt_order)
    print("  confidence-gated (>=0.95) top-4 board on %d matches: %s (violations %d; GT %s)"
          % (len(gated), " > ".join(o), pv, " > ".join(gt_order)))


if __name__ == "__main__":
    for w in [a.lower() for a in sys.argv[1:] if a.lower() in ("f4", "f5", "f6", "f7")] or ["f4", "f5", "f6", "f7"]:
        {"f4": f4, "f5": f5, "f6": f6, "f7": f7}[w]()
