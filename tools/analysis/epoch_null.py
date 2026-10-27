"""EPOCH-NULL (zero calls) - per-leaf Jaccard null between consecutive epochs, from re-celling the same eval
questions across the seed trees on disk. Registered by reference at commit eaf1dbf to docs/design/FRAMEWORK.md
(commit 8d77f7b), "Tests to register before shipping", item 15; scheduled in docs/plan_2026-09-15.md block 1.

  python tools/analysis/epoch_null.py

ITEM 15, quoted in full:
  "EPOCH-NULL. Per-leaf Jaccard null between consecutive epochs from re-celling the same eval questions across
   the seed trees on disk. Registered readout. 0 calls."

THE RECORD IT CITES (RESOLVE.md, accepted objection 5; RESOLVE_stress_operations.md RISK 2 guard (ii)):
  "Leaves are content-addressed and the epoch gate moves to the leaf layer. leaf_key = sha256(sorted content keys
   of its train-side members); the integer node id never leaves the process. The epoch gate measures per-leaf
   membership Jaccard against the previous epoch, calibrated against H9-1's 0.66-0.69 ARI as the null - gating on
   anchor stability measures the one layer that does not move and therefore has no power."
  H9-1 (ledger): seeds {137, 2048, 7, 31337} at the frozen config; "anchors and routing invariant, leaf identity
  is a sample draw"; the per-question ARI was registered there and NOT computed (h9_stability.py substituted
  mu-matching because the exports carry no per-question assignments). The 0.66 figure is P1's baseline
  (consensus_tree.py: mean pairwise ARI 0.663, range 0.585-0.704, over 20 seed builds, nearest-leaf-centroid
  assignment of TRAIN questions). So the number the gate is to be calibrated against was measured on train
  questions, pairwise, not per leaf, and not between consecutive epochs; this test computes the object the record
  actually names.

WHAT IS COMPUTED. A seed change with no data change is the null an epoch gate must tolerate: two trees built by
the same recipe on the same corpus differ only by the seed (and, in this campaign, by the 30% split the seed
draws). The same eval questions - the pool of record p2dca21ab5f4ef3ae, 3,445 judgeable questions - are
re-celled into every seed tree on disk, and per-leaf membership Jaccard between consecutive builds is read as
the null distribution. No verdict is registered; the readout is the distribution, the share of leaves that would
clear candidate bars under a pure seed change, and the chance floor a bar must also clear.

READINGS CHOSEN where the item is silent (fixed before the run, each stated in the output; where a choice exists
the one hardest on the programme's claim - that a per-leaf gate calibrated this way has power - is taken):
  R1 Seed trees on disk = two families, both reported. F = the frozen config (freeze_mcs55: slice 256, bar 0.025,
     mcs 55): the frozen artefact + H9-1's four seeds + the 16 H9-sweep seed arms = 21 builds; this is the family
     H9-1 and P1's 0.66 live in. P = the production config (bareq512: slice 512, bar 0.0145, label-free): the
     promoted bareq512_s42 and the D2 arms bareq512_s137 / _s2048 = 3 builds. "Consecutive epochs" = consecutive
     builds in chronological construction order (the snapshot timestamp); each consecutive pair is one epoch step
     with no data change. F gives 20 steps, P gives 2. All 210 F pairs are reported as a sensitivity line only.
  R2 Re-celling = nearest leaf centroid: max cosine of the question's first-sliceDim MRL slice of its stored
     4096-d embedding (embeddings_cache.db, joined by TEXT, the standing id-space rule) against each leaf's vmfMu,
     the campaign's disclosed approximation of routing (consensus_tree.py, dimsweep_report.py). It is validated
     here against the production router's own primary assignment (routeReserved, max-weight leaf) on the two
     trees that have one for this pool; the agreement rate is printed and is a data check, not a criterion.
  R3 Leaf correspondence. Leaf ids are per-process counters (the record's own objection), so leaves are matched
     by content. PRIMARY: for every leaf of epoch t with at least one eval member, J_best = the maximum Jaccard
     of its eval membership against any leaf of epoch t+1 - the number a gate asking "does my leaf still exist"
     would read, and the most favourable correspondence (an upper bound on any assignment's Jaccard). SECONDARY:
     the one-to-one maximum-Jaccard assignment (Hungarian on the Jaccard matrix), which forbids two old leaves
     claiming the same new one. Leaves with no eval member are counted and excluded (Jaccard undefined).
  R4 Chance floor = within-anchor permutation of epoch t+1's leaf labels over the eval questions
     (profile_tree_robust.shuffled_within_anchor, 200 reps per step): the J_best a leaf gets from random cells of
     the same sizes inside its anchor. A bar below the chance floor's 95th percentile is no gate at all.
  R5 Candidate bars 0.50 / 0.66 / 0.80: the share of leaves clearing each under the null is the share of cells
     an epoch gate would let POOL across versions when nothing but the seed changed; one minus it is the share
     it would re-open. Both readings are printed; the item registers neither as a criterion.
  R6 ARI between consecutive epochs on the eval questions (consensus_tree.ari) is printed beside the per-leaf
     numbers so the record's "0.66-0.69" can be placed; P1's train-question ARI is recomputed on family F's
     consecutive pairs from consensus_tree.train_questions() as the reproduction line.
  R7 Strict held-out subset: for each step, the pool-of-record questions that are on the reserved side of BOTH
     trees' own splits (snapshots.db reserved_queries). Every tree except the frozen artefact and the promoted
     tree activated its own split, so most of the pool sits on the train side of most seed trees; the strict
     subset is where re-celling touches nothing either tree was fitted on.
  R8 Wrong-direction counts. This test scores no judge direction (it re-cells questions; no verdict is read), so
     the McNemar-established rule (systematic_budget.mcnemar_edge / established on the anchor's judged questions)
     has no object here and no established count is reported. Key denominator: the 3,445 judgeable questions of
     the pool of record, all with an embedding on disk; per-leaf denominators are the re-celled eval membership
     sizes. Meta-Llama-3-70B-Instruct is not involved (no model enters this test).
  R9 Intervals: question bootstrap (200 reps, questions resampled with replacement, contingencies recomputed) on
     the pooled median J_best of each family; the per-step spread is printed as the between-epoch variation.
  Added 2026-09-16 after the first run (2026-09-15 21:51) and its adversarial check reproduced R1-R9 to the digit;
  R1-R9 and their numbers are unchanged, these are sensitivity lines the check showed the reading needs:
  R10 Determinism floor: same seed, same config, rebuilt a day apart (h9_seed137 vs dimsweep/d256_s137,
      h9_seed2048 vs dimsweep/d256_s2048). If membership is byte-identical (J_best = 1.000) the null above is a
      pure seed effect; if not, the null contains rebuild noise and the item's "seed trees" reading is too kind.
  R11 Leaf-size strata of J_best on the eval membership of the epoch-t leaf ([1,20), [20,40), [40,80), [80,+)):
      a single bar applied to every leaf reads differently on small and large leaves.
  R12 Instrument and the one real epoch on disk. (a) On the same tree, per-leaf J_best of the router's own
      membership (routeReserved primary) against the centroid re-cell membership: how much of a "change" the
      re-cell approximation manufactures by itself. (b) The one config change the programme actually shipped,
      freeze_mcs55 (slice 256, bar 0.025) -> promoted/bareq512_s42 (slice 512, bar 0.0145, label-free), read
      under the router on both sides and under the centroid on both sides; both trees hold the pool of record
      as their reserved side, so this is the strict held-out reading of a real epoch, placed against the
      seed-only null of R1-R5.
"""
import os, sys, csv, json, math, struct, sqlite3, random, time
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import linear_sum_assignment
import pool_guard
import rejudge_grok as rj
import consensus_tree as ct                # last_snapshot, ari, train_questions
import profile_tree_robust as ptr          # shuffled_within_anchor

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "epoch_null.txt")
SCRATCH = r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\block1"
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
POOL_CSV = os.path.join(ROOT, "reserved_leaf_assignments.csv")          # the pool of record's id list (pool_guard:16-17)
R = os.path.join(ROOT, "experiment_results")
NULL_REPS = 200
BOOT = 200
BARS = (0.50, 0.66, 0.80)
SEED = 42

FAMILY_F = ([("freeze_mcs55", "seed_42")] +
            [("h9_seed%d" % s, "seed_%d" % s) for s in (137, 2048, 7, 31337)] +
            [("h9_sweep/s%d" % s, "seed_%d" % s) for s in
             (3, 11, 99, 271, 500, 777, 1234, 4242, 9001, 12345, 54321, 65537, 111111, 314159, 999983, 424242)])
FAMILY_P = [("promoted/bareq512_s42", "seed_42"), ("dimsweep2/bareq512_s137", "seed_137"),
            ("dimsweep2/bareq512_s2048", "seed_2048")]
ROUTED = {"freeze_mcs55": POOL_CSV,
          "promoted/bareq512_s42": os.path.join(R, "promoted", "bareq512_s42_reserved_leaf_assignments.csv")}
# R10: same seed, same config (frozen recipe, slice 256), rebuilt 2026-09-08 in the D1 sweep
REPLICATES = [(("h9_seed137", "seed_137"), ("dimsweep/d256_s137", "seed_137")),
              (("h9_seed2048", "seed_2048"), ("dimsweep/d256_s2048", "seed_2048"))]
SIZE_BANDS = ((1, 20), (20, 40), (40, 80), (80, 10 ** 9))


# ----------------------------------------------------------------------------------------------- data objects
def pool_of_record():
    """(ids_by_domain, ids) of the pool of record, and its recomputed pool id."""
    by = defaultdict(set)
    with open(POOL_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by[row["category"]].add(int(row["question_id"]))
    ids = sorted(set().union(*by.values()))
    pid = pool_guard.compute_pool_id({d: sorted(v) for d, v in by.items()})
    return by, ids, pid


def eval_vectors(ids):
    """id -> 4096-d vector, by TEXT join eval_question_link -> embeddings.query."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    t = defaultdict(set)
    for q, tx in ev.execute("SELECT question_id, question_text FROM eval_question_link"):
        if q in ids:
            t[q].add(tx)
    multi = sum(1 for v in t.values() if len(v) > 1)
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    vec = {}
    need = {next(iter(v)): q for q, v in t.items() if len(v) == 1}
    for qtext, blob in emb.execute("SELECT query, vector FROM embeddings"):
        q = need.get(qtext)
        if q is None or not isinstance(blob, bytes) or len(blob) % 4:
            continue
        vec[q] = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)
    return vec, dict(with_text=len(t), multi_text=multi, with_vector=len(vec))


def snapshot_id(run_dir):
    import re
    txt = open(os.path.join(run_dir, "headless_run.log"), encoding="utf-8", errors="replace").read()
    return re.findall(r"Snapshot ID: (\S+)", txt)[-1]


def own_pool(snap_id):
    c = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    raw = c.execute("SELECT reserved_queries FROM snapshots WHERE id=?", (snap_id,)).fetchone()[0]
    d = json.loads(raw)
    judge = {k: sorted(q for q in v if q > 0) for k, v in d.items()}
    judge = {k: v for k, v in judge.items() if v}
    return set().union(*judge.values()), pool_guard.compute_pool_id(judge)


def load_tree(rel, seed_dir):
    run = os.path.join(R, rel, seed_dir)
    snap = ct.last_snapshot(run)
    nodes = {n["id"]: n for n in snap["nodes"]}
    kid2parent = {c: n["id"] for n in snap["nodes"] for c in n.get("childIds", [])}

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[kid2parent[n["id"]]]
        return n["label"]
    leaves = [n for n in snap["nodes"] if n["isLeaf"]]
    sid = snapshot_id(run)
    pool, pid = own_pool(sid)
    return dict(name=rel, snap=sid, leaf_ids=[n["id"] for n in leaves],
                mu=np.stack([np.array(n["vmfMu"], dtype=np.float64) for n in leaves]),
                dim=len(leaves[0]["vmfMu"]), anchor={n["id"]: anchor(n["id"]) for n in leaves},
                label={n["id"]: n["label"] for n in leaves}, own_pool=pool, own_pid=pid,
                iteration=snap["iteration"], nodes=len(snap["nodes"]))


def recell(tree, ids, vec):
    """nearest leaf centroid on the tree's own slice; returns np.array of leaf index per id."""
    d = tree["dim"]
    Q = np.stack([vec[q][:d] for q in ids])
    Q /= np.linalg.norm(Q, axis=1, keepdims=True)
    return np.argmax(Q @ tree["mu"].T, axis=1)


def routed_primary(path):
    """routeReserved's primary (max-weight) leaf per question. The CSV writes the weight with a decimal COMMA,
    which the csv module splits into two fields; the row is re-joined here rather than read through DictReader
    (rubric_512.primary_routing reads the truncated field and gets weight 0 on every row)."""
    best = {}
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f); next(rd)
        for row in rd:
            if len(row) == 7:
                q, leaf, w = int(row[0]), row[2], float(row[4] + "." + row[5])
            elif len(row) == 6:
                q, leaf, w = int(row[0]), row[2], float(row[4].replace(",", "."))
            else:
                continue
            if q not in best or w > best[q][0]:
                best[q] = (w, leaf)
    return {q: v[1] for q, v in best.items()}


# ----------------------------------------------------------------------------------------------- statistics
def jaccard_matrix(a, b, nA, nB):
    C = np.bincount(a * nB + b, minlength=nA * nB).reshape(nA, nB).astype(np.float64)
    sA = C.sum(1); sB = C.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        J = np.where(C > 0, C / (sA[:, None] + sB[None, :] - C), 0.0)
    return J, sA, sB


def step_stats(a, b, nA, nB):
    """per-leaf (of epoch t) J_best and one-to-one J for leaves with >= 1 eval member; ARI."""
    J, sA, sB = jaccard_matrix(a, b, nA, nB)
    live = sA > 0
    jbest = J.max(1)
    r, c = linear_sum_assignment(-J)
    jone = np.zeros(nA); jone[r] = J[r, c]
    ari = ct.ari({i: int(x) for i, x in enumerate(a)}, {i: int(x) for i, x in enumerate(b)})
    return jbest[live], jone[live], live, ari, J, sA, sB


def q(x, p):
    return float(np.percentile(x, p)) if len(x) else float("nan")


def dist_line(x):
    x = np.asarray(x)
    if len(x) == 0:
        return "n=0"
    return ("n=%d median %.3f mean %.3f p10 %.3f p25 %.3f p75 %.3f p90 %.3f | share>=%.2f %.3f >=%.2f %.3f >=%.2f %.3f"
            % (len(x), q(x, 50), float(x.mean()), q(x, 10), q(x, 25), q(x, 75), q(x, 90),
               BARS[0], float((x >= BARS[0]).mean()), BARS[1], float((x >= BARS[1]).mean()),
               BARS[2], float((x >= BARS[2]).mean())))


def chance_floor(a, b, treeB, ids, rng, reps):
    """R4: permute epoch t+1's leaf labels within each anchor; J_best per live leaf of epoch t, pooled over reps."""
    part = {i: int(x) for i, x in enumerate(b)}
    anc = {j: treeB["anchor"][treeB["leaf_ids"][j]] for j in range(len(treeB["leaf_ids"]))}
    nA = int(a.max()) + 1 if len(a) else 0
    out = []
    for _ in range(reps):
        sh = ptr.shuffled_within_anchor(part, lambda cell: anc[cell], rng)
        bb = np.array([sh[i] for i in range(len(b))])
        jb, _, _, _, _, _, _ = step_stats(a, bb, nA, len(treeB["leaf_ids"]))
        out.append(jb)
    return np.concatenate(out)


# ----------------------------------------------------------------------------------------------- main
def family_readout(L, tag, trees, ids, vec, rng, strict_all_pairs=False):
    n = len(ids)
    cells = [recell(t, ids, vec) for t in trees]
    idx = {qq: i for i, qq in enumerate(ids)}
    steps = list(zip(range(len(trees) - 1), range(1, len(trees))))
    L.append("")
    L.append("=== FAMILY %s: %d builds, %d consecutive epoch steps (chronological construction order) ===" % (tag, len(trees), len(steps)))
    for t in trees:
        L.append("  %-26s snap %s  it %2d nodes %3d leaves %2d slice %4d  own pool %s%s"
                 % (t["name"], t["snap"], t["iteration"], t["nodes"], len(t["leaf_ids"]), t["dim"], t["own_pid"],
                    "  (= pool of record)" if t["own_pid"] == pool_guard.FROZEN_POOL_ID else
                    "  (%d of the %d pool-of-record questions on its TRAIN side)" % (n - len(set(ids) & t["own_pool"]), n)))
    pooled_best, pooled_one, pooled_floor, pooled_strict = [], [], [], []
    per_step = []
    per_anchor = defaultdict(list)
    L.append("")
    L.append("  per step: leaves(t) live | J_best median [p10, p90] share>=.50/.66/.80 | one-to-one median | chance-floor median/95th | ARI(eval) | strict held-out: n_q, J_best median, n_live")
    for i, j in steps:
        A, B = trees[i], trees[j]
        a, b = cells[i], cells[j]
        jb, jo, live, ari, J, sA, sB = step_stats(a, b, len(A["leaf_ids"]), len(B["leaf_ids"]))
        fl = chance_floor(a, b, B, ids, rng, NULL_REPS)
        strict = sorted((set(ids) & A["own_pool"]) & B["own_pool"])
        if strict:
            si = np.array([idx[qq] for qq in strict])
            jbs, _, lives, _, _, _, _ = step_stats(a[si], b[si], len(A["leaf_ids"]), len(B["leaf_ids"]))
        else:
            jbs, lives = np.array([]), np.array([], dtype=bool)
        for k, lid in enumerate(A["leaf_ids"]):
            if live[k]:
                per_anchor[A["anchor"][lid]].append(J[k].max())
        pooled_best.append(jb); pooled_one.append(jo); pooled_floor.append(fl); pooled_strict.append(jbs)
        per_step.append(dict(a=A["name"], b=B["name"], live=int(live.sum()), med=q(jb, 50), ari=ari,
                             floor95=q(fl, 95), share66=float((jb >= 0.66).mean())))
        L.append("  %-22s -> %-22s %2d/%2d | %.3f [%.3f, %.3f] %.2f/%.2f/%.2f | %.3f | %.3f/%.3f | %.3f | %4d, %s, %d"
                 % (A["name"], B["name"], int(live.sum()), len(A["leaf_ids"]), q(jb, 50), q(jb, 10), q(jb, 90),
                    float((jb >= .5).mean()), float((jb >= .66).mean()), float((jb >= .8).mean()), q(jo, 50),
                    q(fl, 50), q(fl, 95), ari, len(strict), ("%.3f" % q(jbs, 50)) if len(jbs) else "-", int(lives.sum())))
    PB = np.concatenate(pooled_best); PO = np.concatenate(pooled_one); PF = np.concatenate(pooled_floor)
    PS = np.concatenate(pooled_strict) if any(len(x) for x in pooled_strict) else np.array([])
    L.append("")
    L.append("  POOLED over the %d steps (one entry per live leaf per step):" % len(steps))
    L.append("    J_best (primary, R3)      %s" % dist_line(PB))
    L.append("    one-to-one (secondary)    %s" % dist_line(PO))
    L.append("    chance floor (R4, within-anchor permutation, %d reps/step): median %.3f p95 %.3f p99 %.3f max %.3f"
             % (NULL_REPS, q(PF, 50), q(PF, 95), q(PF, 99), float(PF.max())))
    L.append("    strict held-out (R7)      %s" % dist_line(PS))
    aris = [s["ari"] for s in per_step]
    L.append("    ARI(eval) per step: mean %.3f min %.3f max %.3f   (record's calibration figure: 0.66-0.69; P1 train baseline 0.663 [0.585, 0.704])"
             % (float(np.mean(aris)), min(aris), max(aris)))
    meds = [s["med"] for s in per_step]
    L.append("    per-step median J_best: min %.3f max %.3f; per-step share>=0.66: min %.2f max %.2f"
             % (min(meds), max(meds), min(s["share66"] for s in per_step), max(s["share66"] for s in per_step)))
    # R9 question bootstrap on the pooled median J_best
    bs = []
    for _ in range(BOOT):
        pick = rng.choices(range(n), k=n)
        pick = np.array(pick)
        vals = []
        for i, j in steps:
            jb, _, _, _, _, _, _ = step_stats(cells[i][pick], cells[j][pick], len(trees[i]["leaf_ids"]), len(trees[j]["leaf_ids"]))
            vals.append(jb)
        bs.append(q(np.concatenate(vals), 50))
    L.append("    question bootstrap (R9, %d reps) on the pooled median J_best: [%.3f, %.3f]" % (BOOT, q(bs, 2.5), q(bs, 97.5)))
    # per anchor
    L.append("")
    L.append("  per anchor (anchor of the epoch-t leaf), pooled over steps: n leaves, median J_best, share>=0.66")
    for anc in sorted(per_anchor, key=lambda a: -len(per_anchor[a])):
        x = np.asarray(per_anchor[anc])
        L.append("    %-18s n=%4d median %.3f share>=0.66 %.2f" % (anc, len(x), q(x, 50), float((x >= .66).mean())))
    if strict_all_pairs and len(trees) > 3:
        allp = []
        for i in range(len(trees)):
            for j in range(i + 1, len(trees)):
                jb, _, _, _, _, _, _ = step_stats(cells[i], cells[j], len(trees[i]["leaf_ids"]), len(trees[j]["leaf_ids"]))
                allp.append(jb)
        AP = np.concatenate(allp)
        L.append("")
        L.append("  sensitivity: ALL %d pairs (not only consecutive): J_best %s" % (len(allp), dist_line(AP)))
    return dict(best=PB, one=PO, floor=PF, strict=PS, aris=aris, steps=per_step, cells=cells)


def main():
    t0 = time.time()
    os.makedirs(SCRATCH, exist_ok=True)
    active = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    rng = random.Random(SEED)
    L = ["EPOCH-NULL - per-leaf Jaccard null between consecutive epochs from re-celling the pool of record across the seed trees on disk",
         "registered by reference (eaf1dbf) to FRAMEWORK.md item 15 (8d77f7b); 0 calls; run %s" % time.strftime("%Y-%m-%d %H:%M"),
         "pool of record active: %s (pool_guard.assert_pool_of_record)" % active, ""]
    by, ids, pid = pool_of_record()
    vec, vinfo = eval_vectors(set(ids))
    ids = [qq for qq in ids if qq in vec]
    L.append("DATA CHECK: pool-of-record id list %s -> %d judgeable ids in %d domains, recomputed pool id %s (%s); "
             "eval texts found %d (multi-text ids %d); embeddings by text join %d; key denominator n = %d questions"
             % (os.path.relpath(POOL_CSV, ROOT), sum(len(v) for v in by.values()), len(by), pid,
                "MATCHES the pool of record" if pid == pool_guard.FROZEN_POOL_ID else "DOES NOT MATCH the pool of record",
                vinfo["with_text"], vinfo["multi_text"], vinfo["with_vector"], len(ids)))
    L.append("READINGS R1-R9 as in the docstring; wrong-direction counts: none exist in this test (R8).")

    F = [load_tree(*t) for t in FAMILY_F]
    P = [load_tree(*t) for t in FAMILY_P]
    F.sort(key=lambda t: t["snap"]); P.sort(key=lambda t: t["snap"])

    # R2 validation of the re-cell against the production router where a routeReserved file exists for this pool
    L.append("")
    L.append("=== R2 data check: nearest-centroid re-cell vs routeReserved primary assignment (same pool, same tree) ===")
    for t in F + P:
        if t["name"] in ROUTED:
            prim = routed_primary(ROUTED[t["name"]])
            cell = recell(t, ids, vec)
            lid = t["leaf_ids"]
            common = [k for k, qq in enumerate(ids) if qq in prim]
            agree = sum(1 for k in common if lid[cell[k]] == prim[ids[k]])
            same_anchor = sum(1 for k in common if prim[ids[k]] in t["anchor"] and t["anchor"][lid[cell[k]]] == t["anchor"][prim[ids[k]]])
            L.append("  %-24s routed %d of %d; leaf agreement %.3f (%d); anchor agreement %.3f" %
                     (t["name"], len(common), len(ids), agree / len(common), agree, same_anchor / len(common)))
    L.append("  (the approximation is disclosed throughout the campaign; this is the first time it is scored against the router on the pool of record)")

    resF = family_readout(L, "F (frozen config, H9-1's family)", F, ids, vec, rng, strict_all_pairs=True)
    resP = family_readout(L, "P (production config bareq512)", P, ids, vec, rng)

    # R6 reproduction: P1's train-question ARI (256 slice, consensus_tree metric). consensus_tree.train_questions()
    # takes EVERY text in embeddings_cache.db minus the pool; P1 ran it when the table held only MMLU-Pro (7,014
    # train texts). The table now also holds ~9,000 texts of the other corpora, which that helper would re-cell
    # into an MMLU-Pro tree; the reproduction is therefore restricted to MMLU-Pro texts (eval_question_link) with
    # an embedding, minus the pool of record - the closest set to P1's that the disk still identifies.
    L.append("")
    L.append("=== R6 reproduction line: TRAIN-question ARI (consensus_tree metric, 256 slice) on family F ===")
    tq_all = ct.train_questions()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    mm = {r[0] for r in ev.execute("SELECT DISTINCT question_text FROM eval_question_link")}
    ttexts = sorted(t for t in tq_all if t in mm); TQ = np.stack([tq_all[t] for t in ttexts])
    tcells = [np.argmax(TQ @ t["mu"][:, :256].T, axis=1) for t in F]
    taris = []
    for i in range(len(F) - 1):
        taris.append(ct.ari({k: int(x) for k, x in enumerate(tcells[i])}, {k: int(x) for k, x in enumerate(tcells[i + 1])}))
    L.append("  %d MMLU-Pro train texts (of %d texts consensus_tree.train_questions() now returns; P1 had 7,014); ARI per consecutive step: mean %.3f min %.3f max %.3f"
             % (len(ttexts), len(tq_all), float(np.mean(taris)), min(taris), max(taris)))
    # P1's own draw: 20 random pairs (random.Random(42).sample) over the 20 non-frozen builds in consensus_tree's order
    nonfro = [k for k, t in enumerate(F) if t["name"] != "freeze_mcs55"]
    prng = random.Random(42)
    pairs = [prng.sample(range(len(nonfro)), 2) for _ in range(20)]
    p1 = [ct.ari({k: int(x) for k, x in enumerate(tcells[nonfro[i]])}, {k: int(x) for k, x in enumerate(tcells[nonfro[j]])}) for i, j in pairs]
    L.append("  P1's 20 random pairs (seed 42, same build order) on this set: mean %.3f min %.3f max %.3f  (P1 report: 0.663 [0.585, 0.704])"
             % (float(np.mean(p1)), min(p1), max(p1)))
    tj = []
    for i in range(len(F) - 1):
        jb, _, _, _, _, _, _ = step_stats(tcells[i], tcells[i + 1], len(F[i]["leaf_ids"]), len(F[i + 1]["leaf_ids"]))
        tj.append(jb)
    L.append("  per-leaf J_best on TRAIN questions, pooled: %s" % dist_line(np.concatenate(tj)))

    # R10 determinism floor: same seed, same config, rebuilt a day apart
    L.append("")
    L.append("=== R10 determinism floor: same seed + same config rebuilt (is the null a pure seed effect?) ===")
    det = []
    for x, y in REPLICATES:
        A, B = load_tree(*x), load_tree(*y)
        a, b = recell(A, ids, vec), recell(B, ids, vec)
        jb, _, _, ari, _, _, _ = step_stats(a, b, len(A["leaf_ids"]), len(B["leaf_ids"]))
        det.append((jb, ari))
        L.append("  %-12s (snap %s, %d leaves, pool %s) vs %-20s (snap %s, %d leaves, pool %s): J_best median %.3f p10 %.3f share==1.0 %.3f ARI %.3f"
                 % (A["name"], A["snap"][:15], len(A["leaf_ids"]), A["own_pid"], B["name"], B["snap"][:15], len(B["leaf_ids"]), B["own_pid"],
                    q(jb, 50), q(jb, 10), float((jb == 1.0).mean()), ari))
    det_all = np.concatenate([d[0] for d in det])
    L.append("  pooled: %d leaves, share with J_best == 1.000: %.3f; min J_best %.3f" % (len(det_all), float((det_all == 1.0).mean()), float(det_all.min())))

    # R11 leaf-size strata (family F, eval membership size of the epoch-t leaf)
    L.append("")
    L.append("=== R11 leaf-size strata of the null (family F, size = eval members of the epoch-t leaf; P beside it) ===")
    def size_rows(trees, cells):
        rows = []
        for i in range(len(trees) - 1):
            jb, _, live, _, J, sA, _ = step_stats(cells[i], cells[i + 1], len(trees[i]["leaf_ids"]), len(trees[i + 1]["leaf_ids"]))
            for k in np.where(live)[0]:
                rows.append((int(sA[k]), float(J[k].max())))
        return np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
    sF, jF = size_rows(F, resF["cells"]); sP, jP = size_rows(P, resP["cells"])
    rk = lambda x: np.argsort(np.argsort(x))
    L.append("  rank correlation(size, J_best): F %.3f (n=%d), P %.3f (n=%d)"
             % (float(np.corrcoef(rk(sF), rk(jF))[0, 1]), len(sF), float(np.corrcoef(rk(sP), rk(jP))[0, 1]), len(sP)))
    for lo, hi in SIZE_BANDS:
        mF = (sF >= lo) & (sF < hi); mP = (sP >= lo) & (sP < hi)
        L.append("  size [%3d,%s): F n=%4d median J_best %s share>=0.50 %s >=0.66 %s | P n=%3d median %s share>=0.66 %s"
                 % (lo, ("%d" % hi) if hi < 10 ** 9 else "inf", int(mF.sum()),
                    ("%.3f" % q(jF[mF], 50)) if mF.any() else "-", ("%.2f" % float((jF[mF] >= .5).mean())) if mF.any() else "-",
                    ("%.2f" % float((jF[mF] >= .66).mean())) if mF.any() else "-", int(mP.sum()),
                    ("%.3f" % q(jP[mP], 50)) if mP.any() else "-", ("%.2f" % float((jP[mP] >= .66).mean())) if mP.any() else "-"))

    # R12 instrument sensitivity and the one real epoch on disk (frozen -> promoted), strict held-out on both sides
    L.append("")
    L.append("=== R12 instrument and the real epoch: freeze_mcs55 -> promoted/bareq512_s42 (both hold the pool of record as reserved) ===")
    Ft = next(t for t in F if t["name"] == "freeze_mcs55"); Pt = next(t for t in P if t["name"] == "promoted/bareq512_s42")
    rt = {}
    for t in (Ft, Pt):
        prim = routed_primary(ROUTED[t["name"]])
        pos = {lid: k for k, lid in enumerate(t["leaf_ids"])}
        rt[t["name"]] = np.array([pos[prim[qq]] for qq in ids])
        cc = recell(t, ids, vec)
        jb, _, _, ari, _, _, _ = step_stats(rt[t["name"]], cc, len(t["leaf_ids"]), len(t["leaf_ids"]))
        L.append("  (a) same tree %-24s router membership vs centroid re-cell membership: per-leaf J_best median %.3f p10 %.3f share>=0.80 %.3f ARI %.3f"
                 % (t["name"], q(jb, 50), q(jb, 10), float((jb >= .8).mean()), ari))
    cF, cP = recell(Ft, ids, vec), recell(Pt, ids, vec)
    real = {}
    for tag, a, b in (("ROUTER both sides", rt[Ft["name"]], rt[Pt["name"]]), ("CENTROID both sides", cF, cP)):
        jb, jo, _, ari, _, _, _ = step_stats(a, b, len(Ft["leaf_ids"]), len(Pt["leaf_ids"]))
        real[tag] = jb
        L.append("  (b) real epoch under %-20s J_best %s | one-to-one median %.3f | ARI(eval) %.3f"
                 % (tag + ":", dist_line(jb), q(jo, 50), ari))
    L.append("  placed against the seed-only null (R1-R5): F share>=0.50 %.3f / >=0.66 %.3f; real epoch (router) share>=0.50 %.3f / >=0.66 %.3f"
             % (float((resF["best"] >= .5).mean()), float((resF["best"] >= .66).mean()),
                float((real["ROUTER both sides"] >= .5).mean()), float((real["ROUTER both sides"] >= .66).mean())))

    # readout summary
    PB, PF, PS = resF["best"], resF["floor"], resF["strict"]
    L.append("")
    L.append("=== REGISTERED READOUT (item 15 registers no criterion; numbers, no PASS/FAIL) ===")
    L.append("  (1) NULL per-leaf Jaccard between consecutive epochs, family F, J_best: median %.3f [p10 %.3f, p90 %.3f]; one-to-one median %.3f; "
             "family P: median %.3f [p10 %.3f, p90 %.3f]"
             % (q(PB, 50), q(PB, 10), q(PB, 90), q(resF["one"], 50), q(resP["best"], 50), q(resP["best"], 10), q(resP["best"], 90)))
    L.append("  (2) SHARE of leaves an epoch gate would let pool under a pure seed change, family F, at bar 0.50 / 0.66 / 0.80: %.3f / %.3f / %.3f "
             "(re-opened: %.3f / %.3f / %.3f); family P: %.3f / %.3f / %.3f"
             % (float((PB >= .5).mean()), float((PB >= .66).mean()), float((PB >= .8).mean()),
                float((PB < .5).mean()), float((PB < .66).mean()), float((PB < .8).mean()),
                float((resP["best"] >= .5).mean()), float((resP["best"] >= .66).mean()), float((resP["best"] >= .8).mean())))
    L.append("  (3) CHANCE FLOOR (within-anchor permutation) J_best: family F median %.3f p95 %.3f; family P median %.3f p95 %.3f; "
             "share of null leaves above the floor's p95: F %.3f, P %.3f"
             % (q(PF, 50), q(PF, 95), q(resP["floor"], 50), q(resP["floor"], 95),
                float((PB > q(PF, 95)).mean()), float((resP["best"] > q(resP["floor"], 95)).mean())))
    L.append("  (4) ARI(eval) per consecutive step: F mean %.3f [%.3f, %.3f]; P mean %.3f [%.3f, %.3f]; TRAIN-question reproduction of P1: mean %.3f [%.3f, %.3f]"
             % (float(np.mean(resF["aris"])), min(resF["aris"]), max(resF["aris"]),
                float(np.mean(resP["aris"])), min(resP["aris"]), max(resP["aris"]), float(np.mean(taris)), min(taris), max(taris)))
    L.append("  (5) STRICT held-out subset (R7), family F: %s" % dist_line(PS))
    L.append("  (6) question-bootstrap interval on the pooled median J_best is printed in each family block (R9).")
    L.append("  (7) DETERMINISM floor (R10): same seed + config rebuilt, share of leaves at J_best == 1.000: %.3f of %d (the null is %s)"
             % (float((det_all == 1.0).mean()), len(det_all), "a pure seed effect" if (det_all == 1.0).all() else "NOT a pure seed effect"))
    L.append("  (8) LEAF-SIZE dependence (R11), family F: median J_best %s across size bands %s; rank corr(size, J_best) %.3f"
             % (" / ".join(("%.3f" % q(jF[(sF >= lo) & (sF < hi)], 50)) if ((sF >= lo) & (sF < hi)).any() else "-" for lo, hi in SIZE_BANDS),
                "[1,20) / [20,40) / [40,80) / [80,inf)", float(np.corrcoef(rk(sF), rk(jF))[0, 1])))
    L.append("  (9) REAL EPOCH (R12b, frozen -> promoted, router both sides, strict held-out): J_best median %.3f, share>=0.50 %.3f, >=0.66 %.3f, ARI %.3f; "
             "the re-cell instrument alone (R12a) moves per-leaf membership to J_best median %.3f / %.3f on the two trees"
             % (q(real["ROUTER both sides"], 50), float((real["ROUTER both sides"] >= .5).mean()), float((real["ROUTER both sides"] >= .66).mean()),
                ct.ari({i: int(x) for i, x in enumerate(rt[Ft["name"]])}, {i: int(x) for i, x in enumerate(rt[Pt["name"]])}),
                q(step_stats(rt[Ft["name"]], cF, len(Ft["leaf_ids"]), len(Ft["leaf_ids"]))[0], 50),
                q(step_stats(rt[Pt["name"]], cP, len(Pt["leaf_ids"]), len(Pt["leaf_ids"]))[0], 50)))
    L.append("")
    L.append("READING. The per-leaf Jaccard null is what the epoch gate of RESOLVE objection 5 / stress guard (ii) must tolerate when nothing but the")
    L.append("seed changes. A bar set inside this null re-opens the share of cells printed in (2) on every epoch with no data change; a bar set below")
    L.append("the chance floor's p95 in (3) passes leaves that share nothing beyond their anchor. Both are readouts; the item registers no verdict.")
    rr = real["ROUTER both sides"]
    below = q(rr, 50) < q(PB, 50) and float((rr >= .66).mean()) < float((PB >= .66).mean()) and float((rr >= .5).mean()) < float((PB >= .5).mean())
    L.append("The null is %s (7); it %s with leaf size (8); the one real epoch on disk (9) sits %s the seed-only null on median, share>=0.50 and"
             % ("a pure seed effect" if (det_all == 1.0).all() else "NOT a pure seed effect",
                "rises" if float(np.corrcoef(rk(sF), rk(jF))[0, 1]) > 0 else "does not rise",
                "BELOW" if below else "NOT below"))
    L.append("share>=0.66 (real p10-p90 [%.3f, %.3f] against null [%.3f, %.3f]); the two per-leaf distributions overlap, so a bar read leaf by leaf"
             % (q(rr, 10), q(rr, 90), q(PB, 10), q(PB, 90)))
    L.append("%s tell a seed change from that config change, and a bar that lets a seed change pool %.0f%% of leaves lets the config change pool %.0f%%; the record's"
             % ("cannot" if below else "may", 100 * float((PB >= .5).mean()), 100 * float((rr >= .5).mean())))
    L.append("'0.66-0.69' is an ARI over the whole partition and is not a per-leaf Jaccard bar (median per-leaf J_best under the seed null is %.2f F / %.2f P)."
             % (q(PB, 50), q(resP["best"], 50)))
    L.append("First run 2026-09-15 21:51 (R1-R9, independently reproduced); this run adds R10-R12 and changes no earlier number.")
    L.append("Wrong-direction counts: none (R8). Elapsed %.0f s." % (time.time() - t0))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
