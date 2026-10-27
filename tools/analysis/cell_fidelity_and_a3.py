"""#2 cell-size vs judge fidelity, #3 aggregation-level fidelity (A3 curve).

Both are regroupings of verdicts already on disk. No new judge calls.
"""
import sqlite3, json, math
from collections import defaultdict

R = sqlite3.connect('ratings.db')
D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')
SNAP = '20260727_042523_Headless_Run_Auto_ge'

# ---------- tree ----------
g = json.loads(R and D and sqlite3.connect('snapshots.db').execute(
    "select graph from snapshots where id=?", (SNAP,)).fetchone()[0])
NODES = {n['id']: n for n in g['nodes']}
def ancestors(nid):
    out, cur = [], nid
    while cur:
        out.append(cur)
        p = NODES[cur].get('parentIds') or []
        cur = p[0] if p else None
    return out  # leaf -> root

# ---------- ground truth ----------
# is_correct per (question_id, model)
correct = {}
for qid, m, ic in D.execute(
        "select question_id, model_name, is_correct from eval_results"):
    correct[(str(qid), m)] = ic

# ---------- verdicts ----------
def load(cond):
    rows = []
    for nid, qid, w, l, tie, ma, mb in R.execute(
            "select node_id, eval_question_id, winner, loser, is_tie, model_a, model_b "
            "from match_history where snapshot_id=? and condition=? and node_id is not null",
            (SNAP + '_' + cond, cond)):
        rows.append((nid, str(qid), w, l, tie, ma, mb))
    return rows

# ---------- Bradley-Terry (MM) ----------
def bt(pairs, models):
    """pairs: list of (winner, loser, weight). Returns dict model->score."""
    W = defaultdict(float); N = defaultdict(float)
    for w, l, wt in pairs:
        W[w] += wt; N[(w, l)] += wt; N[(l, w)] += wt
    ms = sorted(models)
    if not any(W[m] for m in ms):
        return None
    p = {m: 1.0 for m in ms}
    for _ in range(500):
        new = {}
        for m in ms:
            denom = 0.0
            for o in ms:
                if o == m: continue
                nij = N[(m, o)]
                if nij: denom += nij / (p[m] + p[o])
            new[m] = W[m] / denom if denom > 0 else p[m]
        gm = sum(new.values()) / len(new)
        if gm <= 0: return None
        new = {m: v / gm for m, v in new.items()}
        if max(abs(new[m] - p[m]) for m in ms) < 1e-10:
            p = new; break
        p = new
    return p

def spearman(a, b):
    """a,b: dicts model->value. Returns rho over shared keys."""
    ks = sorted(set(a) & set(b))
    n = len(ks)
    if n < 3: return None
    def rank(d):
        vs = sorted(ks, key=lambda k: d[k])
        r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]: j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1): r[vs[k]] = avg
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    num = sum((ra[k] - ma) * (rb[k] - mb) for k in ks)
    da = math.sqrt(sum((ra[k] - ma) ** 2 for k in ks))
    db = math.sqrt(sum((rb[k] - mb) ** 2 for k in ks))
    return num / (da * db) if da and db else None

def gt_acc(qids, models):
    """GT accuracy per model over a question set."""
    out = {}
    for m in models:
        hits = [correct[(q, m)] for q in qids if (q, m) in correct]
        if hits: out[m] = sum(hits) / len(hits)
    return out

def analyse(rows, label):
    models = sorted({r[5] for r in rows} | {r[6] for r in rows})
    print(f"\n{'='*78}\n{label}   ({len(rows)} verdicts, {len(models)} models)\n{'='*78}")

    # ---------- #2 per-cell ----------
    cells = defaultdict(list)
    for r in rows: cells[r[0]].append(r)

    print(f"\n#2  PER-CELL FIDELITY vs SIZE")
    print(f"{'cell':<11}{'nQ':>5}{'cmp':>6}{'GT-agree':>11}{'SE':>7}{'tie%':>7}"
          f"{'rho':>8}{'rho_bl':>8}{'nbl':>6}{'r=n/(n+7.66)':>14}")
    per_cell = []
    for nid in sorted(cells, key=lambda k: -len({r[1] for r in cells[k]})):
        cr = cells[nid]
        qids = sorted({r[1] for r in cr})
        n = len(qids)
        # GT-agreement on discriminable pairs
        disc = agree = ties = 0
        blind_pairs = []
        all_pairs = []
        for _, q, w, l, tie, ma, mb in cr:
            cw = correct.get((q, w)); cl = correct.get((q, l))
            if tie: ties += 1
            if cw is None or cl is None: continue
            if not tie and cw != cl:
                disc += 1; agree += (cw == 1)
            if cw == cl:  # correctness-blind: key gives no signal
                if tie:
                    blind_pairs.append((w, l, 0.5)); blind_pairs.append((l, w, 0.5))
                else:
                    blind_pairs.append((w, l, 1.0))
            if tie:
                all_pairs.append((w, l, 0.5)); all_pairs.append((l, w, 0.5))
            else:
                all_pairs.append((w, l, 1.0))
        ga = agree / disc if disc else float('nan')
        se = math.sqrt(ga * (1 - ga) / disc) if disc else float('nan')
        gt = gt_acc(qids, models)
        s_all = bt(all_pairs, models); s_bl = bt(blind_pairs, models)
        rho = spearman(s_all, gt) if s_all else None
        rho_bl = spearman(s_bl, gt) if s_bl else None
        nbl = len([p for p in blind_pairs if p[2] == 1.0]) + len(blind_pairs) // 2 * 0
        rel = n / (n + 7.66)
        per_cell.append((nid, n, ga, rho, rho_bl, rel, disc))
        f = lambda v: f"{v:>8.3f}" if v is not None and v == v else f"{'--':>8}"
        print(f"{nid:<11}{n:>5}{len(cr):>6}{ga*100:>10.1f}%{se*100:>6.1f}%"
              f"{ties/len(cr)*100:>6.1f}%{f(rho)}{f(rho_bl)}{nbl:>6}{rel:>14.3f}")

    # correlation of fidelity with size
    print(f"\n  Regression of fidelity on cell size (n = held-out questions):")
    for name, idx in (('GT-agreement', 2), ('rho', 3), ('rho_blind', 4)):
        pts = [(c[1], c[idx]) for c in per_cell if c[idx] is not None and c[idx] == c[idx]]
        if len(pts) < 3: continue
        a = {f'c{i}': p[0] for i, p in enumerate(pts)}
        b = {f'c{i}': p[1] for i, p in enumerate(pts)}
        rs = spearman(a, b)
        print(f"    {name:<14} vs n:  rho = {rs:+.3f}   (k={len(pts)} cells)")
    # does the reliability curve predict it?
    pts = [(c[5], c[3]) for c in per_cell if c[3] is not None]
    if len(pts) >= 3:
        a = {f'c{i}': p[0] for i, p in enumerate(pts)}
        b = {f'c{i}': p[1] for i, p in enumerate(pts)}
        print(f"    rho vs r=n/(n+7.66): rho = {spearman(a,b):+.3f}")
    return rows, models, per_cell

def a3_curve(rows, models, label):
    """#3: re-aggregate at leaf cut / depth-2 cut / Math-as-one-cell."""
    print(f"\n#3  AGGREGATION-LEVEL FIDELITY (A3 curve) -- {label}")
    leaves = sorted({r[0] for r in rows})
    depths = {l: NODES[l]['depth'] for l in leaves}
    print(f"    leaf depths present: {sorted(set(depths.values()))}")

    def cut_at(target_depth):
        m = {}
        for l in leaves:
            anc = ancestors(l)  # leaf -> root
            pick = None
            for a in anc:
                if NODES[a]['depth'] == target_depth: pick = a; break
            m[l] = pick or anc[-1]
        return m

    cuts = [('leaf cut', {l: l for l in leaves})]
    for d in (3, 2):
        c = cut_at(d)
        if len(set(c.values())) != len(set(cuts[-1][1].values())):
            cuts.append((f'depth-{d} cut', c))
    cuts.append(('Math as one cell', {l: 'ALL' for l in leaves}))

    print(f"\n    {'cut':<20}{'groups':>8}{'mean rho':>11}{'median':>9}"
          f"{'mean nQ':>10}{'weighted rho':>14}")
    out = []
    for name, mapping in cuts:
        groups = defaultdict(list)
        for r in rows: groups[mapping[r[0]]].append(r)
        rhos, ns = [], []
        for gid, gr in groups.items():
            qids = sorted({r[1] for r in gr})
            pairs = []
            for _, q, w, l, tie, ma, mb in gr:
                if tie: pairs += [(w, l, .5), (l, w, .5)]
                else: pairs.append((w, l, 1.))
            s = bt(pairs, models)
            gt = gt_acc(qids, models)
            rr = spearman(s, gt) if s else None
            if rr is not None: rhos.append(rr); ns.append(len(qids))
        if not rhos: continue
        mean = sum(rhos) / len(rhos)
        med = sorted(rhos)[len(rhos) // 2]
        wmean = sum(r * n for r, n in zip(rhos, ns)) / sum(ns)
        print(f"    {name:<20}{len(rhos):>8}{mean:>11.3f}{med:>9.3f}"
              f"{sum(ns)/len(ns):>10.1f}{wmean:>14.3f}")
        out.append((name, len(rhos), mean, med, wmean))
    return out

for cond in ('MAIN', 'GENERIC_JUDGE'):
    rows, models, per_cell = analyse(load(cond), cond)
    a3_curve(rows, models, cond)
