"""SPLIT-RATIO — reserved-pool ratio study readout (registered 2026-09-10 13:20, docs/judge_v2_program.md).

Structural half (per ratio 0.20 / 0.30 / 0.40; experiment_results/splitratio/r<RR>/seed_42, label-free
builds on their OWN seed-42 split; pool re-pinned by the chain): leaves, certified sites (site-null
harness, site_null_r<RR>.csv), held-out Top-1 with Wilson CI, keyed TRAIN questions per leaf, keyed
ARENA (reserved) questions per leaf and per anchor (nearest-centroid routing on the build's own tree).

Synthetic half (zero calls; LEAF-POWER's machinery): at each ratio, an arena at R2's verdict budget
(36,871 matches spread equally over the anchors) sampled uniformly over model pairs and over that
ratio's arena questions of the anchor, judged by the NOISY key (0.228 flip on decidable pairs, 80%
random winner on non-decidable); anchor-level BT fit; the QUERY-LEVEL cluster-bootstrap SE (resample
questions, refit; 100 resamples) of every model's strength — worst model per anchor — plus the analytic
floor sqrt(k/q), k = 3, from the design-effect study.
REGISTERED READOUT: the smallest ratio at which every anchor's worst-model SE at R2's budget is <= 0.15
while the build's certified-site count is within 2 of the 0.30 build's.

  python tools/analysis/splitratio_report.py [--ratios 20,30,40] [--boots 100] [--seeds 3]
"""
import os, sys, csv, math, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import free_tests_f4_f7 as ff
import profile_atlas as pa
import rubric_p8 as p8
import dimsweep_report as dr

SR = os.path.join(ROOT, "experiment_results", "splitratio")
R2_MATCHES = 36871
NOISE = 0.228


def pool_id_of(rr):
    log = os.path.join(SR, "r%02d" % rr, "seed_42", "headless_run.log")
    for line in open(log, encoding="utf-8", errors="replace"):
        if "Reserved pool " in line and "recorded" in line:
            return line.split("Reserved pool ")[1].strip("'\"").split("'")[0]
    raise SystemExit("no pool id in %s" % log)


def pool_ids(pid):
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db"), uri=True)
    return {q for (q,) in con.execute("SELECT question_id FROM reserved_pool WHERE pool_id = ?", (pid,))}


def route(rr, text, qs, vec_cache):
    leaves = ff.tree_leaves(os.path.join("experiment_results", "splitratio", "r%02d" % rr, "seed_42"))
    dim = len(leaves[0][1])
    if dim not in vec_cache:
        vec_cache[dim] = ff.embed_matrix(ff.EMB_DB, list(text.values()), dim)
    vec = vec_cache[dim]
    qq = [q for q in qs if text[q] in vec]
    Q = np.stack([vec[text[q]] for q in qq]); M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
    idx = np.argmax(Q @ M.T, axis=1)
    return {q: leaves[i][0] for q, i in zip(qq, idx)}, {q: leaves[i][2] for q, i in zip(qq, idx)}, len(leaves)


def site_cert(rr):
    p = os.path.join(SR, "site_null_r%02d.csv" % rr)
    if not os.path.exists(p):
        return None
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    return sum(1 for r in rows if r["cert_site_p95"] == "true"), len(rows)


def synth_anchor_se(arena_by_anchor, G, models, boots, seed):
    """Per anchor: worst-model query-level bootstrap SE of the BT strength at R2's per-anchor budget."""
    rng = random.Random(seed); out = {}
    budget = R2_MATCHES // len(arena_by_anchor)
    for anc in sorted(arena_by_anchor):
        aq = arena_by_anchor[anc]
        by_q = defaultdict(list)
        for _ in range(budget):
            a, b = rng.sample(models, 2); q = aq[rng.randrange(len(aq))]
            ca, cb = G[a][q], G[b][q]
            if ca == cb:
                wa = 0.5
                if rng.random() < 0.8:
                    wa = float(rng.random() < 0.5)
            else:
                wa = 1.0 if ca else 0.0
                if rng.random() < NOISE:
                    wa = 1.0 - wa
            key = (a, b) if a < b else (b, a); w = wa if key[0] == a else 1.0 - wa
            by_q[q].append((key, w))
        qlist = sorted(by_q)

        def fit_from(qsel):
            agg = defaultdict(lambda: [0.0, 0.0])
            for q in qsel:
                for key, w in by_q[q]:
                    agg[key][0] += w; agg[key][1] += 1
            th = pa.mm_fit({k: (v[0], v[1]) for k, v in agg.items()}, models)
            mean = sum(th.values()) / len(th)
            return {m: th[m] - mean for m in models}
        thetas = []
        for _ in range(boots):
            sel = [qlist[rng.randrange(len(qlist))] for _ in range(len(qlist))]
            thetas.append(fit_from(sel))
        se = {m: float(np.std([t[m] for t in thetas], ddof=1)) for m in models}
        worst = max(se, key=se.get)
        out[anc] = (se[worst], worst, len(aq))
    return out


def main(ratios, boots, seeds):
    models_all, G, cat, text, qs_all = ff.keyed_questions()
    models = [m for m in p8.ARENA12 if m in G]
    print("SPLIT-RATIO readout: %d keyed questions, %d arena models, R2 budget %d matches, %d bootstrap resamples, %d synthetic seeds"
          % (len(qs_all), len(models), R2_MATCHES, boots, seeds))
    vec_cache = {}; rows = {}
    print("\n%-5s %6s %10s %8s %18s %14s %14s %16s" % ("ratio", "leaves", "cert/sites", "top1", "wilson", "train/leaf med", "arena/leaf med", "arena/anchor min"))
    for rr in ratios:
        d = os.path.join(SR, "r%02d" % rr, "seed_42")
        if not os.path.exists(os.path.join(d, "dag_snapshots.jsonl")):
            print("r%d: build missing" % rr); continue
        pid = pool_id_of(rr); pool = pool_ids(pid)
        leaf, anc, n_leaves = route(rr, text, qs_all, vec_cache)
        train = [q for q in leaf if q not in pool]; arena = [q for q in leaf if q in pool]
        tpl = Counter(leaf[q] for q in train); apl = Counter(leaf[q] for q in arena); apa = defaultdict(list)
        for q in arena:
            apa[anc[q]].append(q)
        tvp = os.path.join(d, "validation", "MAIN_trickle_validation_results.csv")
        tv = dr.metric_csv(tvp) if os.path.exists(tvp) else {"Top1Accuracy": float("nan"), "Top1WilsonLow": float("nan"), "Top1WilsonHigh": float("nan")}
        sc = site_cert(rr)
        rows[rr] = dict(pool=pid, leaves=n_leaves, cert=sc, top1=tv["Top1Accuracy"], lo=tv["Top1WilsonLow"], hi=tv["Top1WilsonHigh"],
                        train_med=int(np.median(list(tpl.values()))), arena_med=int(np.median(list(apl.values()))) if apl else 0,
                        arena_anchor_min=min(len(v) for v in apa.values()) if apa else 0, apa=apa, n_train=len(train), n_arena=len(arena))
        r = rows[rr]
        print("%-5s %6d %10s %8.4f [%.4f,%.4f] %14d %14d %16d   pool %s (train %d, arena %d keyed)" % (
            "%.2f" % (rr / 100), n_leaves, ("%d/%d" % sc) if sc else "pending", r["top1"], r["lo"], r["hi"], r["train_med"], r["arena_med"], r["arena_anchor_min"], pid, r["n_train"], r["n_arena"]))
    print("\n== synthetic arena at R2's budget (NOISY judge), anchor-level profile: worst-model query-level SE per anchor ==")
    verdict = {}
    for rr in sorted(rows):
        apa = rows[rr]["apa"]; per_seed = []
        if not apa or min(len(v) for v in apa.values()) < 20:
            print("\nratio %.2f: synthetic arena skipped (fewer than 20 arena questions in some anchor — no arena is possible at this ratio)" % (rr / 100))
            verdict[rr] = (float("nan"), 0, max(1, len(apa))); continue
        for s in range(seeds):
            per_seed.append(synth_anchor_se(apa, G, models, boots, 5000 + s))
        print("\nratio %.2f (%d matches per anchor):" % (rr / 100, R2_MATCHES // len(apa)))
        worst_all = 0.0
        for a in sorted(apa):
            ses = [ps[a][0] for ps in per_seed]; m = float(np.mean(ses)); worst_all = max(worst_all, m)
            print("  %-18s arena q %4d | worst-model SE %.3f (seeds %s) | analytic floor sqrt(3/q) %.3f" % (
                a, len(apa[a]), m, "/".join("%.3f" % x for x in ses), math.sqrt(3.0 / len(apa[a]))))
        n_ok = sum(1 for a in apa if float(np.mean([ps[a][0] for ps in per_seed])) <= 0.15)
        verdict[rr] = (worst_all, n_ok, len(apa))
        print("  -> anchors with SE <= 0.15: %d/%d; worst anchor SE %.3f" % (n_ok, len(apa), worst_all))
    print("\n== REGISTERED READOUT ==")
    base = rows.get(30)
    base_cert = base["cert"][0] if base and base["cert"] else None
    ok = []
    for rr in sorted(rows):
        r = rows[rr]; w, n_ok, n_a = verdict[rr]
        se_ok = n_ok == n_a
        cert_ok = None if (r["cert"] is None or base_cert is None) else (r["cert"][0] >= base_cert - 2)
        print("  %.2f: all anchors SE <= 0.15: %s (%d/%d, worst %.3f) | certified within 2 of the 0.30 build: %s (%s vs %s)"
              % (rr / 100, "YES" if se_ok else "NO", n_ok, n_a, w, {None: "pending", True: "YES", False: "NO"}[cert_ok],
                 r["cert"][0] if r["cert"] else "?", base_cert if base_cert is not None else "?"))
        if se_ok and cert_ok:
            ok.append(rr)
    print("  smallest ratio meeting both: %s" % ("%.2f" % (ok[0] / 100) if ok else "none (or pending)"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratios", default="0,10,20,30,40"); ap.add_argument("--boots", type=int, default=100); ap.add_argument("--seeds", type=int, default=3)
    a = ap.parse_args()
    main([int(x) for x in a.ratios.split(",")], a.boots, a.seeds)
