"""Synthetic worlds for the selftests (no DB of record is ever opened by a selftest).

make_world() builds a small keyed corpus (models with skills, questions in anchors, extracted answers with blanks,
response lengths) and a judged board whose per-order votes come from a KNOWN VerdictModel, so every leg can run end to
end in seconds. write_dbs() materialises the world as the four on-disk objects systematic_budget.build() reads (an eval
DB, a verdict cache, snapshots.db with a graph, the promoted routing CSV and run log) in a temp dir, with ro.REAL_CONNECT.
"""
import csv
import json
import os

import numpy as np

from . import ro
from .data import Board
from .verdict_model import VerdictModel, VerdictModelV2, match_type

LETTERS = "ABCDEFGHIJ"


class KeyView:
    def __init__(self, K, P, L, cat):
        self.K, self.P, self.L, self.cat = K, P, L, cat
        self.strata = cat
        self.all_models = sorted({m for q in K for m in K[q]})
        self.models = self.all_models

    def arrays(self, models, qids):
        mi = {m: k for k, m in enumerate(models)}
        K = -np.ones((len(qids), len(models)), dtype=np.int8)
        P = np.zeros((len(qids), len(models)), dtype="<U1")
        L = np.full((len(qids), len(models)), np.nan)
        for r, q in enumerate(qids):
            for m, v in self.K.get(q, {}).items():
                if m in mi:
                    K[r, mi[m]] = v
            for m, v in self.P.get(q, {}).items():
                if m in mi:
                    P[r, mi[m]] = v
            for m, v in self.L.get(q, {}).items():
                if m in mi:
                    L[r, mi[m]] = v
        return K, P, L


def make_world(seed=7, n_models=5, anchors=("AncA", "AncB", "AncC"), q_per_anchor=40, per_pair=20,
               bad_model=None, blank_rate=0.05, kappa=2.0, pi=0.4, lam=0.3, u_sd=0.35, model_names=None, beta=None):
    rng = np.random.default_rng(seed)
    models = sorted(model_names or ["m%d" % k for k in range(n_models)])
    skill = dict(zip(models, np.linspace(0.85, 0.35, len(models))))
    K, P, L, cat = {}, {}, {}, {}
    qid = 1000
    anchor_qs = {}
    for anc in anchors:
        qs = []
        for _ in range(q_per_anchor):
            qid += 1; qs.append(qid); cat[qid] = anc
            gt = LETTERS[rng.integers(0, 4)]
            K[qid] = {}; P[qid] = {}; L[qid] = {}
            for m in models:
                ok = rng.random() < skill[m]
                K[qid][m] = int(ok)
                ans = gt if ok else LETTERS[(LETTERS.index(gt) + 1 + rng.integers(0, 3)) % 4]
                P[qid][m] = "" if rng.random() < blank_rate else ans
                L[qid][m] = int(rng.integers(300, 3000))
        anchor_qs[anc] = qs
    vm = VerdictModel(len(anchors), len(models)) if beta is None else VerdictModelV2(len(anchors), len(models))
    vm.kappa, vm.pi, vm.lam = kappa, pi, lam
    vm.gamma = np.log(np.array([0.6, 1.2, 0.8]))
    vm.u = rng.normal(0, u_sd, size=(len(anchors), len(models)))
    if bad_model is not None:
        vm.u[:, models.index(bad_model)] -= 1.5
    vm.sigma_v, vm.sigma_w = 0.2, 0.2
    if beta is not None:
        vm.beta = beta
        vm.sigma_eps_lomo = 0.2
    rows = []
    midx = {m: k for k, m in enumerate(models)}
    for g, anc in enumerate(anchors):
        qs = anchor_qs[anc]
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                for _ in range(per_pair):
                    q = int(qs[rng.integers(0, len(qs))])
                    x, y = (a, b) if rng.random() < 0.5 else (b, a)
                    rows.append((g, x, y, q))
    S = dict(g=np.array([r[0] for r in rows]), a=np.array([midx[r[1]] for r in rows]),
             b=np.array([midx[r[2]] for r in rows]),
             t=np.array([match_type(K[r[3]][r[1]], K[r[3]][r[2]], P[r[3]][r[1]], P[r[3]][r[2]]) for r in rows]),
             kd=np.array([K[r[3]][r[1]] - K[r[3]][r[2]] for r in rows], dtype=float),
             dl=np.array([(L[r[3]][r[1]] - L[r[3]][r[2]]) / 1000.0 for r in rows]))
    KA = None
    if beta is not None:
        # a quality-aligned judge (the v2 world): keyacc under convention A over each anchor's questions
        KA = np.array([[sum(K[q][m] for q in anchor_qs[a]) / len(anchor_qs[a]) for m in models] for a in anchors])
        S["ka"] = KA[S["g"], S["a"]] - KA[S["g"], S["b"]]
    sim = vm.simulate(S, rng, mode="fixed")
    vote = {0: "Model A", 1: "Model B", 2: "TIE"}
    cache_rows = []
    for k, (g, a, b, q) in enumerate(rows):
        v1, v2 = vote[int(sim["y1"][k])], vote[int(sim["y2"][k])]
        w = a if sim["wa"][k] == 1.0 else (b if sim["wa"][k] == 0.0 else "TIE")
        cache_rows.append((a, b, q, w, 0, v1, v2))
    route = {q: "leaf_" + cat[q] for q in cat}
    anchor_of = lambda leaf: leaf[5:]
    kv = KeyView(K, P, L, cat)
    board = Board(cache_rows, route, anchor_of, models, kv, "synthetic")
    return dict(models=models, anchors=list(anchors), K=K, P=P, L=L, cat=cat, vm=vm, rows=cache_rows, KA=KA, S=S,
                board=board, keyview=kv, route=route, anchor_of=anchor_of)


def write_dbs(world, tmp, tree="synth_tree", snap_id="SNAP_SYNTH"):
    """The on-disk objects systematic_budget.build() reads, in tmp. Returns the paths."""
    ev = os.path.join(tmp, "eval.db")
    con = ro.REAL_CONNECT(ev)
    con.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, pred TEXT, is_correct INTEGER, "
                "model_output TEXT, category TEXT)")
    for q in sorted(world["K"]):
        for m in world["models"]:
            con.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?)",
                        (q, m, world["P"][q][m], world["K"][q][m], "x" * world["L"][q][m], world["cat"][q]))
    con.commit(); con.close()
    cache = os.path.join(tmp, "verdicts.db")
    con = ro.REAL_CONNECT(cache)
    con.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, qid INTEGER, "
                "winner TEXT, invalid INTEGER, vote1 TEXT, vote2_raw TEXT)")
    for k, (a, b, q, w, inv, v1, v2) in enumerate(world["rows"]):
        con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?,?)", (k + 1, a, b, q, w, inv, v1, v2))
    con.commit(); con.close()
    snaps = os.path.join(tmp, "snapshots.db")
    nodes = [dict(id="root", depth=0, label="root", childIds=["n_" + a for a in world["anchors"]])]
    for a in world["anchors"]:
        nodes.append(dict(id="n_" + a, depth=1, label=a, childIds=["leaf_" + a]))
        nodes.append(dict(id="leaf_" + a, depth=2, label=a + "-leaf", childIds=[]))
    con = ro.REAL_CONNECT(snaps)
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT)")
    con.execute("INSERT INTO snapshots VALUES (?,?)", (snap_id, json.dumps(dict(nodes=nodes))))
    con.commit(); con.close()
    promoted = os.path.join(tmp, "experiment_results", "promoted")
    os.makedirs(os.path.join(promoted, tree, "seed_42"))
    with open(os.path.join(promoted, tree, "seed_42", "headless_run.log"), "w", encoding="utf-8") as f:
        f.write("Snapshot ID: %s\n" % snap_id)
    with open(os.path.join(promoted, "%s_reserved_leaf_assignments.csv" % tree), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "leaf_id", "category", "weight"])
        for q in sorted(world["cat"]):
            w.writerow([q, "leaf_" + world["cat"][q], world["cat"][q], "1,000000"])
    return dict(eval=ev, cache=cache, snapshots=snaps, promoted=promoted, tree=tree)
