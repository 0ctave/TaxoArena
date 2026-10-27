"""KEY-SUBANCHOR-SCALE (zero calls) - is sub-anchor structure dead for taxonomy reasons or data reasons?
(registered 2026-09-15 at commit 60cb7f3, docs/judge_v2_program.md section D, before any run)

  python tools/analysis/key_subanchor_scale.py

REGISTRATION, quoted:
  "PROFILE-TREE-ROBUST (corrected) found the key-derived sub-anchor profile is not tree-robust on the 2,811
  reserved questions (most-changed third: -0.071). The corrected extrapolation says 900-1,500 questions per leaf
  would be needed. The snapshots carry train-side membership (node.queryIds), so the key-only test can run on
  the full keyed set (~10,900 questions: train side + reserved) for both trees, at their native sizes (~125 and
  ~230 questions per leaf), with the within-anchor null and (model, anchor) demeaning; and at subsampled sizes
  below that to draw the trend. Contamination note: this uses the TRAIN side by design - the question is
  whether the KEY's own profile is tree-stable on the questions the trees were fitted to separate, which is the
  most favourable case for sub-anchor structure. If it fails there it fails everywhere.
  CRITERIA: (1) PRIMARY: (model, anchor)-demeaned cross-tree r on the most-changed third of questions, at the
  full size, against its within-anchor null 95th pct. (2) The trend of that r with cell size. (3) Whether the
  extrapolated 900-1,500 requirement is on the trend line.
  PREDICTION: still negative or null on the most-changed third at full size, for both trees - sub-anchor
  structure is not tree-stable even on the training questions, which closes it for TAXONOMY reasons. FALSIFIER:
  a positive, null-clearing r on the most-changed third at full size reopens sub-anchor as a data question."

IMPLEMENTATION NOTES (constraints from the registration and the launch note, not design freedom):
  trees bareq512_s42 and abt2d512_s42. Full keyed set per tree = reserved routing (rubric_512.primary_routing)
  UNION train-side leaf membership from the snapshot nodes' queryIds. Key-only profiles: per-cell accuracy per
  model over the 12 ARENA12 models, cells with >= 25 questions. (model, anchor) demeaning and the within-anchor
  null (200 reps) are the corrected PROFILE-TREE-ROBUST helpers, imported, not rewritten. Strata = terciles of
  the Jaccard overlap of the question's cell company between trees. Sizes: full, 50%, 25%.
  Primary = most-changed tercile at full size vs its within-anchor null 95th pct.

READINGS CHOSEN where the registration is silent (fixed before the run; each is stated in the output):
  R1 queryIds. Verified on both snapshots: only LEAF nodes carry queryIds (every internal node's list is
     empty), so "the deepest node whose queryIds contain it" is the leaf. Some questions sit in more than one
     leaf with queryWeights summing to 1; the primary leaf is the max-weight one (the same rule
     primary_routing applies to the reserved side; no exact weight ties exist).
  R2 id mapping. queryIds are 'q_' + sha256(rawText)[:16], not question ids. embeddings_cache.queries maps the
     hash to raw_text; the raw_text is joined to eval_question_link.question_text (whitespace-normalised). The
     queries.query_id column is NOT used (it disagrees with the text join on 1,717 of 8,278 ids; the standing
     rule is join by text only). A hash whose text belongs to more than one eval question id is resolved only
     if, after removing reserved candidates, exactly one candidate remains or all remaining candidates carry an
     identical 12-model key vector (then the choice cannot change any number); otherwise the hash is DROPPED.
  R3 anchor of a question = tree A's anchor of its cell (as PROFILE-TREE-ROBUST (1c)); agreement with tree B's
     anchor is reported. eval_results.category is not used for anything (6,624 question ids carry more than one
     category value in that table); the mmlu_pro category by text is used for the data-check line only.
  R4 null. The primary null is PIPELINE-FAITHFUL: each of the 200 within-anchor shuffles (both trees) rebuilds
     the profiles, recomputes the Jaccard company overlap and its terciles, and reads r on ITS OWN most-changed
     third - the null preserves exactly what the observed statistic conditions on. A fixed-strata null (observed
     tercile membership held, cells shuffled) is reported as a sensitivity line, not as the primary.
  R5 subsampling for the trend: a uniform random subsample of the common question set at the fraction, the whole
     pipeline rerun on it (the 25-question floor included), 5 independent draws per fraction, 40 null reps per
     draw (200 per fraction); observed r reported as the mean over draws with its range. A fixed-cell variant
     (the full-size profiled cells kept, each thinned to the fraction) is reported as a secondary trend.
  R6 criterion (3) reading: "on the trend line" = a least-squares line of r(most-changed third) on log2(cell
     size) over the measured sizes, extrapolated to 900 and 1,500 questions per leaf, reaches the programme's
     publishability bar for a profile (0.70, PROFILE-RELIABILITY) with a positive slope; a Spearman-Brown growth
     curve anchored at the full-size point is reported alongside. If r is negative or inside its null at every
     size the trend carries no reliability to grow and the requirement is not on it.
  R7 wrong-direction counts. This test produces none (it is a correlation of key-only profiles, no judge
     direction is scored), so the McNemar-established rule has no object here; the key denominator of every
     profile cell is the cell's questions keyed for ALL 12 ARENA12 models. Meta-Llama-3-70B-Instruct is not in
     ARENA12 and appears nowhere.
"""
import os, sys, re, json, math, random, sqlite3, time
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import profile_tree_robust as ptr      # shuffled_within_anchor, demean_by_model_anchor, pearson
import profile_reliability as prel     # sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "key_subanchor_scale.txt")
SCRATCH = r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\bigpic"
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
TREE_A = "bareq512_s42"; TREE_B = "abt2d512_s42"
MIN_CELL = 25
NULL_REPS = 200
FRACS = [1.0, 0.5, 0.25]
DRAWS = {1.0: 1, 0.5: 5, 0.25: 5}
BAR = 0.70            # PROFILE-RELIABILITY's registered publishability bar, used for the (3) reading only
REQ = (900, 1500)     # the extrapolated requirement the registration names

norm = lambda s: re.sub(r"\s+", " ", s).strip()


# ----------------------------------------------------------------------------------------------- data objects
def train_membership(tree):
    """hash -> primary leaf id (max queryWeight; tie -> deeper, then id). Also the propagation check."""
    nodes = r512.load_graph(r512.snapshot_id(tree))
    internal_with_ids = sum(1 for n in nodes.values() if n.get("childIds") and n.get("queryIds"))
    leaves = [n for n in nodes.values() if not n.get("childIds")]
    cand = defaultdict(list); entries = 0; ties = 0
    for n in leaves:
        for h in n["queryIds"]:
            entries += 1
            cand[h].append((float(n["queryWeights"][h]), n["depth"], n["id"]))
    prim = {}
    for h, v in cand.items():
        v.sort()
        if len(v) > 1 and abs(v[-1][0] - v[-2][0]) < 1e-9:
            ties += 1
        prim[h] = v[-1][2]
    wsum = Counter(round(sum(x[0] for x in v), 3) for v in cand.values())
    info = dict(nodes=len(nodes), leaves=len(leaves), entries=entries, distinct=len(cand),
                multi=sum(1 for v in cand.values() if len(v) > 1), ties=ties,
                internal_with_ids=internal_with_ids, weight_sums=dict(wsum.most_common(3)))
    return nodes, prim, info


def hash_to_qid(hashes, reserved, K12):
    """R2: text join, ambiguity rule. Returns (map hash->qid, stats)."""
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    raw = {i: t for i, t in emb.execute("SELECT id, raw_text FROM queries")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    t2q = defaultdict(set)
    for q, t in ev.execute("SELECT question_id, question_text FROM eval_question_link"):
        t2q[norm(t)].add(q)
    st = Counter(); out = {}
    for h in hashes:
        t = raw.get(h)
        if t is None:
            st["hash not in embeddings cache"] += 1; continue
        s = t2q.get(norm(t))
        if not s:
            st["no eval question with this text"] += 1; continue
        if len(s) == 1:
            out[h] = next(iter(s)); st["unique text"] += 1; continue
        c = [q for q in s if q not in reserved]
        if len(c) == 1:
            out[h] = c[0]; st["ambiguous, one non-reserved candidate"] += 1; continue
        keys = {json.dumps(K12.get(q), sort_keys=True) for q in c}
        if len(c) > 1 and len(keys) == 1 and None not in [K12.get(q) for q in c]:
            out[h] = min(c); st["ambiguous, identical key vectors (choice cannot matter)"] += 1; continue
        st["ambiguous, DROPPED"] += 1
    if len(set(out.values())) != len(out):
        # two hashes resolving to the same qid would double-count a question; keep the first, count it
        seen = set(); dup = 0
        for h in list(out):
            if out[h] in seen: del out[h]; dup += 1
            else: seen.add(out[h])
        st["hash collision on one qid, DROPPED"] = dup
    return out, st


def key_profile(part, qs, K, models):
    bycell = defaultdict(list)
    for q in qs:
        c = part.get(q)
        if c is not None:
            bycell[c].append(q)
    out = {}
    for c, cqs in bycell.items():
        if len(cqs) < MIN_CELL:
            continue
        out[c] = {m: sum(K[q][m] for q in cqs) / len(cqs) for m in models}
    return out, {c: len(v) for c, v in bycell.items()}


def paired(pa, pb, partA, partB, qs, models):
    out = []
    for q in qs:
        ca, cb = partA.get(q), partB.get(q)
        if ca not in pa or cb not in pb:
            continue
        for m in models:
            out.append((q, m, pa[ca][m], pb[cb][m]))
    return out


def jaccard(partA, partB, qs):
    """Company overlap per question: |cellA(q) & cellB(q)| / |cellA(q) | cellB(q)| over qs."""
    na = Counter(partA[q] for q in qs); nb = Counter(partB[q] for q in qs)
    nab = Counter((partA[q], partB[q]) for q in qs)
    return {q: nab[(partA[q], partB[q])] / (na[partA[q]] + nb[partB[q]] - nab[(partA[q], partB[q])]) for q in qs}


def r_ma(P, anc_of_q):
    if len(P) < 100:
        return float("nan")
    D = ptr.demean_by_model_anchor(P, anc_of_q)
    return ptr.pearson([p[2] for p in D], [p[3] for p in D])


def run_once(partA, partB, qs, K, models, anc_of_q, strata_fixed=None):
    """One full pass: profiles, pairs, terciles, r on each stratum. Returns a dict."""
    pa, sizesA = key_profile(partA, qs, K, models); pb, sizesB = key_profile(partB, qs, K, models)
    P = paired(pa, pb, partA, partB, qs, models)
    jac = jaccard(partA, partB, qs)
    prof = sorted({p[0] for p in P}, key=lambda q: (jac[q], q))
    n = len(prof); t = n // 3
    strata = {"low": set(prof[:t]), "mid": set(prof[t:2 * t]), "high": set(prof[2 * t:])}
    res = {"n_pairs": len(P), "n_prof": n,
           "cellsA": len(pa), "cellsB": len(pb),
           "qpcA": (sum(sizesA[c] for c in pa) / len(pa)) if pa else float("nan"),
           "qpcB": (sum(sizesB[c] for c in pb) / len(pb)) if pb else float("nan"),
           "r_all": r_ma(P, anc_of_q)}
    for k, ss in strata.items():
        sub = [p for p in P if p[0] in ss]
        res["r_" + k] = r_ma(sub, anc_of_q); res["n_" + k] = len(ss)
        res["jac_" + k] = (sum(jac[q] for q in ss) / len(ss)) if ss else float("nan")
    if strata_fixed is not None:
        for k, ss in strata_fixed.items():
            sub = [p for p in P if p[0] in ss]
            res["rfix_" + k] = r_ma(sub, anc_of_q)
    res["strata"] = {k: sorted(v) for k, v in strata.items()}
    return res


def null_dist(partA, partB, qs, K, models, anc_of_q, ancA, ancB, strata_fixed, reps, rng, tag, L=None):
    rows = []
    t0 = time.time()
    for i in range(reps):
        ra = ptr.shuffled_within_anchor(partA, ancA, rng); rb = ptr.shuffled_within_anchor(partB, ancB, rng)
        res = run_once(ra, rb, qs, K, models, anc_of_q, strata_fixed)
        rows.append({k: v for k, v in res.items() if k != "strata"})
        if (i + 1) % 50 == 0:
            print("  [%s] null rep %d/%d  %.0fs" % (tag, i + 1, reps, time.time() - t0), flush=True)
    return rows


def q95(xs):
    xs = sorted(x for x in xs if x == x)
    return (xs[len(xs) // 2], xs[int(0.95 * len(xs))], len(xs)) if xs else (float("nan"), float("nan"), 0)


def fit_loglin(points):
    """least squares r = a + b*log2(n) over (n, r) points."""
    xs = [math.log2(n) for n, _ in points]; ys = [r for _, r in points]
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else float("nan")
    a = my - b * mx
    return a, b


def sb_curve(r0, n0, n):
    """Spearman-Brown growth of a reliability r0 measured at n0 to length n."""
    k = n / n0
    return k * r0 / (1 + (k - 1) * r0)


# ------------------------------------------------------------------------------------------------------- main
def main():
    os.makedirs(SCRATCH, exist_ok=True)
    L = []
    models = sorted(p8.ARENA12)
    assert "Meta-Llama-3-70B-Instruct" not in models

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0)
    K12 = {q: d for q, d in K.items() if len(d) == 12}
    reserved = set(pool_guard.eval_ids(pool_guard.MMLU_PRO_POOL))
    mp_cat = {norm(q): c.lower() for q, c in ev.execute("SELECT question, category FROM mmlu_pro")}
    qtext = {q: norm(t) for q, t in ev.execute("SELECT question_id, question_text FROM eval_question_link")}

    L.append("=== KEY-SUBANCHOR-SCALE: is sub-anchor structure dead for taxonomy reasons or data reasons? ===")
    L.append("  key-only test; models %d (ARENA12); reserved pool of record %s (%d questions in the id file)"
             % (len(models), pool_guard.FROZEN_POOL_ID, len(reserved)))
    L.append("  questions keyed for all 12 models: %d" % len(K12))
    L.append("")
    L.append("=== DATA CHECK (before any stratum is read): recovering the full keyed set per tree ===")

    trees = {}
    for tree in (TREE_A, TREE_B):
        nodes, prim, info = train_membership(tree)
        anc = r512.anchor_fn(nodes)
        hmap, st = hash_to_qid(sorted(prim), reserved, K12)
        train = {hmap[h]: prim[h] for h in hmap}
        route = r512.primary_routing(tree)
        overlap = set(train) & set(route)
        assert not overlap, "train side and reserved routing overlap on %d questions" % len(overlap)
        assert not (set(train) & reserved), "train side contains reserved questions"
        full = dict(train); full.update(route)
        full_keyed = {q: c for q, c in full.items() if q in K12}
        cat_ok = sum(1 for q, c in train.items() if mp_cat.get(qtext.get(q)) == anc(c).lower())
        L.append("  %s: snapshot %s | %d nodes, %d leaves" % (tree, r512.snapshot_id(tree), info["nodes"], info["leaves"]))
        L.append("    queryIds propagation: internal nodes carrying queryIds = %d (all ids sit on leaves; the leaf IS the deepest node)"
                 % info["internal_with_ids"])
        L.append("    leaf entries %d | distinct hashes %d | in >1 leaf %d (weights per hash sum to %s; exact ties %d) -> primary = max weight"
                 % (info["entries"], info["distinct"], info["multi"], info["weight_sums"], info["ties"]))
        L.append("    hash -> question id by text join: " + "; ".join("%s %d" % (k, v) for k, v in sorted(st.items())))
        L.append("    train side recovered %d questions (%d keyed for all 12) | train-side category == leaf anchor (mmlu_pro category by text): %d of %d"
                 % (len(train), sum(1 for q in train if q in K12), cat_ok, len(train)))
        L.append("    reserved routing %d questions (%d keyed) | train & reserved = %d (must be 0) | train & routing = %d (must be 0)"
                 % (len(route), sum(1 for q in route if q in K12), len(set(train) & reserved), len(overlap)))
        L.append("    FULL KEYED SET: %d questions | %d leaves used | mean %.1f q/leaf"
                 % (len(full_keyed), len(set(full_keyed.values())), len(full_keyed) / max(1, len(set(full_keyed.values())))))
        trees[tree] = dict(nodes=nodes, anc=anc, train=train, route=route, full=full_keyed, info=info, st=st)
        json.dump({str(q): c for q, c in full_keyed.items()}, open(os.path.join(SCRATCH, "keyed_partition_%s.json" % tree), "w"))

    A, Bt = trees[TREE_A], trees[TREE_B]
    partA0, partB0 = A["full"], Bt["full"]
    qs = sorted(set(partA0) & set(partB0))
    partA = {q: partA0[q] for q in qs}; partB = {q: partB0[q] for q in qs}
    ancA, ancB = A["anc"], Bt["anc"]
    anc_of_q = lambda q: ancA(partA[q])
    same_anc = sum(1 for q in qs if ancA(partA[q]) == ancB(partB[q]))
    n_train_common = sum(1 for q in qs if q in A["train"]); n_res_common = sum(1 for q in qs if q in A["route"])
    L.append("  OVERLAP between trees: %d questions in both full keyed sets (%d train-side, %d reserved) | only in %s: %d | only in %s: %d"
             % (len(qs), n_train_common, n_res_common, TREE_A, len(set(partA0) - set(partB0)), TREE_B, len(set(partB0) - set(partA0))))
    L.append("  anchor agreement between trees on the common set: %d of %d (%.4f); demeaning uses %s's anchor (R3)"
             % (same_anc, len(qs), same_anc / len(qs), TREE_A))
    ca = Counter(partA.values()); cb = Counter(partB.values())
    L.append("  native cell sizes on the common set: %s %d leaves, mean %.1f q/leaf, %d leaves >= %d | %s %d leaves, mean %.1f, %d >= %d"
             % (TREE_A, len(ca), len(qs) / len(ca), sum(1 for v in ca.values() if v >= MIN_CELL), MIN_CELL,
                TREE_B, len(cb), len(qs) / len(cb), sum(1 for v in cb.values() if v >= MIN_CELL), MIN_CELL))
    L.append("  (registration expected ~10,900 questions and ~125 / ~230 q/leaf)")

    # ---------------------------------------------------------------- full size: observed + null
    rng = random.Random(42)
    obs = run_once(partA, partB, qs, K, models, anc_of_q)
    strata_fixed = {k: set(v) for k, v in obs["strata"].items()}
    L.append("")
    L.append("=== FULL SIZE: observed (model, anchor)-demeaned cross-tree r of the KEY profile, by Jaccard tercile ===")
    L.append("  profiled cells: %s %d (mean %.1f q) | %s %d (mean %.1f q) | pairs %d over %d questions"
             % (TREE_A, obs["cellsA"], obs["qpcA"], TREE_B, obs["cellsB"], obs["qpcB"], obs["n_pairs"], obs["n_prof"]))
    print("full-size observed:", {k: v for k, v in obs.items() if k != "strata"}, flush=True)
    t0 = time.time()
    nulls_full = null_dist(partA, partB, qs, K, models, anc_of_q, ancA, ancB, strata_fixed, NULL_REPS, rng, "full")
    print("  full-size null done in %.0fs" % (time.time() - t0), flush=True)
    L.append("  %-36s %6s %8s %9s | %-32s | %-32s" % ("stratum", "n_q", "overlap", "observed", "pipeline-faithful null (R4): med / 95th", "fixed-strata null: med / 95th"))
    for k, lab in (("low", "most changed third (lowest overlap)"), ("mid", "middle third"), ("high", "least changed third (highest overlap)")):
        m1, p1, n1 = q95([r["r_" + k] for r in nulls_full]); m2, p2, n2 = q95([r["rfix_" + k] for r in nulls_full])
        L.append("  %-36s %6d %8.3f %+9.4f | %+8.4f / %+8.4f (%d reps)          | %+8.4f / %+8.4f (%d reps)"
                 % (lab, obs["n_" + k], obs["jac_" + k], obs["r_" + k], m1, p1, n1, m2, p2, n2))
    m1, p1, n1 = q95([r["r_all"] for r in nulls_full])
    L.append("  %-36s %6d %8s %+9.4f | %+8.4f / %+8.4f (%d reps)" % ("all profiled questions", obs["n_prof"], "-", obs["r_all"], m1, p1, n1))
    L.append("  the null's OWN most-changed third has mean company overlap %.3f (observed %.3f): the within-anchor shuffle keeps the"
             % (sum(r["jac_low"] for r in nulls_full) / len(nulls_full), obs["jac_low"]))
    L.append("  shared-question share of the two cells' accuracies at the same level, so a null-clearing r is not shared data.")
    L.append("  (PROFILE-TREE-ROBUST (6) on the 2,811 reserved questions alone read the same statistic at -0.0711 on the most-changed third)")

    # sensitivity: anchor from tree B
    anc_of_qB = lambda q: ancB(partB[q])
    obsB = run_once(partA, partB, qs, K, models, anc_of_qB)
    L.append("  sensitivity, demeaning by %s's anchor instead: most-changed third r = %+.4f | all %+.4f" % (TREE_B, obsB["r_low"], obsB["r_all"]))

    # bridge: the same pipeline on the two halves of the full set (decomposition, not a criterion)
    L.append("")
    L.append("  BRIDGE (decomposition, not a criterion): the same pipeline on the reserved keyed questions alone and on the train side alone,")
    L.append("  each with its own %d-rep pipeline-faithful null. The reserved-only line is the PROFILE-TREE-ROBUST (6) instrument on the" % NULL_REPS)
    L.append("  keyed reserved set (%d questions there vs 2,811 with verdicts). Its terciles are its own, so it is not the full-size low third." % n_res_common)
    bridge = {}
    for lab, sel in (("reserved only", [q for q in qs if q in A["route"]]), ("train side only", [q for q in qs if q in A["train"]])):
        pA = {q: partA[q] for q in sel}; pB = {q: partB[q] for q in sel}
        aq = lambda q, pA=pA: ancA(pA[q])
        o = run_once(pA, pB, sel, K, models, aq)
        nl = null_dist(pA, pB, sel, K, models, aq, ancA, ancB, None, NULL_REPS, random.Random(77 + len(sel)), lab)
        m1, p1, n1 = q95([r["r_low"] for r in nl])
        bridge[lab] = dict(n=len(sel), cellsA=o["cellsA"], qpcA=o["qpcA"], cellsB=o["cellsB"], qpcB=o["qpcB"], r_low=o["r_low"], jac_low=o["jac_low"],
                           null_med=m1, null95=p1, r_all=o["r_all"], r_mid=o["r_mid"], r_high=o["r_high"])
        L.append("  %-16s n=%5d | cells %d (%.0f q) / %d (%.0f q) | most-changed third r %+.4f (overlap %.3f) vs null med %+.4f / 95th %+.4f | mid %+.4f high %+.4f all %+.4f"
                 % (lab, len(sel), o["cellsA"], o["qpcA"], o["cellsB"], o["qpcB"], o["r_low"], o["jac_low"], m1, p1, o["r_mid"], o["r_high"], o["r_all"]))

    # ---------------------------------------------------------------- (1) primary verdict
    med_low, n95_low, nn = q95([r["r_low"] for r in nulls_full])
    med_fix, n95_fix, _ = q95([r["rfix_low"] for r in nulls_full])
    r_low = obs["r_low"]
    clears = r_low > n95_low and r_low > 0
    clears_fix = r_low > n95_fix and r_low > 0
    L.append("")
    L.append("=== (1) PRIMARY: most-changed third at full size vs its within-anchor null 95th pct ===")
    L.append("  observed r = %+.4f | pipeline-faithful null median %+.4f, 95th pct %+.4f (%d reps) | fixed-strata null 95th %+.4f"
             % (r_low, med_low, n95_low, nn, n95_fix))
    L.append("  positive AND clears the null 95th (pipeline-faithful null, the primary): %s | on the fixed-strata null: %s"
             % ("YES" if clears else "NO", "YES" if clears_fix else "NO"))
    if clears:
        L.append("  -> FALSIFIER FIRES: a positive, null-clearing r on the most-changed third at full size REOPENS sub-anchor as a DATA question.")
        L.append("     The registered prediction (still negative or null) FAILED.")
    else:
        L.append("  -> AS PREDICTED: %s on the most-changed third at full size. Sub-anchor structure is not tree-stable even on the"
                 % ("negative" if r_low < 0 else "inside its null"))
        L.append("     training questions the trees were fitted to separate; the registration closes it for TAXONOMY reasons.")
    if clears != clears_fix:
        L.append("  NOTE: the two nulls disagree; the primary is the pipeline-faithful one (R4, fixed before the run).")

    # ---------------------------------------------------------------- (2) trend with cell size
    L.append("")
    L.append("=== (2) TREND of the most-changed-third r with cell size ===")
    L.append("  R5: uniform subsample of the common set at each fraction, whole pipeline rerun (25-question floor included),")
    L.append("  %d draws per fraction, %d null reps per draw (pooled). Observed = mean over draws [min, max]." % (DRAWS[0.5], NULL_REPS // DRAWS[0.5]))
    L.append("  %-6s %7s %8s %8s %8s %8s | %-24s | %-24s | %-16s" % ("frac", "n_q", "cellsA", "q/cellA", "cellsB", "q/cellB", "r low: mean [min,max]", "null low: med / 95th", "r all (mean)"))
    trend = {}   # frac -> dict
    for frac in FRACS:
        rows_obs = []; rows_null = []
        for d in range(DRAWS[frac]):
            if frac == 1.0:
                sub = qs; o = obs; nl = nulls_full
            else:
                rs = random.Random(1000 + int(frac * 100) * 10 + d)
                sub = sorted(q for q in qs if rs.random() < frac)
                pA = {q: partA[q] for q in sub}; pB = {q: partB[q] for q in sub}
                aq = lambda q, pA=pA: ancA(pA[q])
                o = run_once(pA, pB, sub, K, models, aq)
                nl = null_dist(pA, pB, sub, K, models, aq, ancA, ancB, None, NULL_REPS // DRAWS[frac],
                               random.Random(2000 + int(frac * 100) * 10 + d), "frac %.2f draw %d" % (frac, d))
            rows_obs.append({k: v for k, v in o.items() if k != "strata"}); rows_null.extend(nl)
        mean = lambda k: sum(r[k] for r in rows_obs) / len(rows_obs)
        lo = min(r["r_low"] for r in rows_obs); hi = max(r["r_low"] for r in rows_obs)
        m1, p1, n1 = q95([r["r_low"] for r in rows_null])
        trend[frac] = dict(n_q=mean("n_prof"), cellsA=mean("cellsA"), qpcA=mean("qpcA"), cellsB=mean("cellsB"), qpcB=mean("qpcB"),
                           r_low=mean("r_low"), r_low_min=lo, r_low_max=hi, null_med=m1, null95=p1, null_n=n1,
                           r_all=mean("r_all"), r_mid=mean("r_mid"), r_high=mean("r_high"), obs=rows_obs)
        t = trend[frac]
        L.append("  %-6.2f %7.0f %8.1f %8.1f %8.1f %8.1f | %+7.4f [%+.4f,%+.4f] | %+8.4f / %+8.4f (%d) | %+8.4f"
                 % (frac, t["n_q"], t["cellsA"], t["qpcA"], t["cellsB"], t["qpcB"], t["r_low"], lo, hi, m1, p1, n1, t["r_all"]))
    L.append("  middle / least-changed thirds (mean over draws): " + " | ".join(
        "frac %.2f: mid %+.4f high %+.4f" % (f, trend[f]["r_mid"], trend[f]["r_high"]) for f in FRACS))

    # secondary trend: fixed cells thinned (cells held at the full-size profiled set)
    L.append("")
    L.append("  SECONDARY TREND (R5): the full-size profiled cells held fixed, each cell thinned to the fraction (no floor reapplied),")
    L.append("  observed most-changed-third r on the FULL-SIZE tercile membership, %d draws; no null (reported for the trend shape only)." % DRAWS[0.5])
    profA = {c for c in Counter(partA.values()) if Counter(partA.values())[c] >= MIN_CELL}
    profB = {c for c in Counter(partB.values()) if Counter(partB.values())[c] >= MIN_CELL}
    fixed_rows = {}
    for frac in (0.5, 0.25):
        vals = []
        for d in range(DRAWS[frac]):
            rs = random.Random(3000 + int(frac * 100) * 10 + d)
            sub = sorted(q for q in qs if rs.random() < frac)
            pA = {q: partA[q] for q in sub}; pB = {q: partB[q] for q in sub}
            # profiles on the thinned cells, restricted to the full-size profiled cells, floor removed
            bycA = defaultdict(list); bycB = defaultdict(list)
            for q in sub: bycA[pA[q]].append(q); bycB[pB[q]].append(q)
            pa = {c: {m: sum(K[q][m] for q in v) / len(v) for m in models} for c, v in bycA.items() if c in profA and len(v) >= 2}
            pb = {c: {m: sum(K[q][m] for q in v) / len(v) for m in models} for c, v in bycB.items() if c in profB and len(v) >= 2}
            P = paired(pa, pb, pA, pB, sub, models)
            ss = strata_fixed["low"]
            vals.append((r_ma([p for p in P if p[0] in ss], lambda q, pA=pA: ancA(pA[q])),
                         sum(len(v) for c, v in bycA.items() if c in pa) / max(1, len(pa)),
                         sum(len(v) for c, v in bycB.items() if c in pb) / max(1, len(pb))))
        fixed_rows[frac] = (sum(v[0] for v in vals) / len(vals), min(v[0] for v in vals), max(v[0] for v in vals),
                            sum(v[1] for v in vals) / len(vals), sum(v[2] for v in vals) / len(vals))
        L.append("  frac %.2f: q/cellA %.1f q/cellB %.1f | r low = %+.4f [%+.4f, %+.4f]" % (frac, fixed_rows[frac][3], fixed_rows[frac][4], fixed_rows[frac][0], fixed_rows[frac][1], fixed_rows[frac][2]))
    L.append("  frac 1.00: q/cellA %.1f q/cellB %.1f | r low = %+.4f" % (obs["qpcA"], obs["qpcB"], r_low))

    # trend reading
    pts = [((trend[f]["qpcA"] + trend[f]["qpcB"]) / 2, trend[f]["r_low"]) for f in FRACS]
    a, b = fit_loglin(pts)
    inside = [f for f in FRACS if not (trend[f]["r_low"] > trend[f]["null95"] and trend[f]["r_low"] > 0)]
    L.append("")
    L.append("  TREND READ: r(most-changed third) at cell sizes %s (mean of the two trees' q/cell) = %s"
             % (", ".join("%.0f" % n for n, _ in pts), ", ".join("%+.4f" % r for _, r in pts)))
    L.append("  least-squares on log2(cell size): slope %+.4f per doubling, intercept %+.4f" % (b, a))
    L.append("  sizes at which r is positive AND clears its null 95th: %s | inside the null or negative: %s"
             % ([f for f in FRACS if f not in inside] or "none", inside or "none"))
    spread = max(r for _, r in pts) - min(r for _, r in pts)
    null_spread = max(trend[f]["null95"] - trend[f]["null_med"] for f in FRACS)
    L.append("  the whole movement of r across a 4x range of cell size is %.4f; the null's own median-to-95th spread is up to %.4f"
             % (spread, null_spread))

    # ---------------------------------------------------------------- (3) is 900-1,500 on the trend line?
    L.append("")
    L.append("=== (3) Is the extrapolated 900-1,500 questions-per-leaf requirement on the trend line? (reading R6) ===")
    n_full = pts[-1][0] if FRACS[0] == 1.0 else None
    n_full = (trend[1.0]["qpcA"] + trend[1.0]["qpcB"]) / 2
    for n in REQ:
        lin = a + b * math.log2(n)
        sbv = sb_curve(r_low, n_full, n) if r_low > 0 else float("nan")
        L.append("  at %4d q/leaf: log-linear extrapolation r = %+.4f | Spearman-Brown growth from the full-size point (%.0f q, r %+.4f) = %s"
                 % (n, lin, n_full, r_low, ("%+.4f" % sbv) if sbv == sbv else "undefined (r <= 0 at full size: there is no reliability to grow)"))
    on_line = (b > 0) and (a + b * math.log2(REQ[1]) >= BAR)
    L.append("  bar for 'on the trend line': positive slope AND extrapolated r >= %.2f somewhere in 900-1,500 -> %s" % (BAR, "YES" if on_line else "NO"))
    if b > 0:
        need = 2 ** ((BAR - a) / b)
        L.append("  the log-linear line reaches %.2f at about %s questions per leaf (%.0fx the 1,500 upper end of the requirement)"
                 % (BAR, ("%.0f" % need) if need < 1e9 else ">1e9", need / REQ[1]))
    else:
        L.append("  the slope is not positive: no cell size on the fitted line reaches %.2f" % BAR)
    if r_low <= 0 or r_low <= n95_low:
        L.append("  READ: with r at full size %s, the requirement is NOT on the trend line. More questions per leaf grow a reliability;"
                 % ("negative" if r_low <= 0 else "inside its null"))
        L.append("  there is none here to grow: the key's sub-anchor profile does not agree with itself across trees at any measured size,")
        L.append("  and the 900-1,500 figure (PROFILE-TREE-ROBUST (7)) was a JUDGE split-half extrapolation within one tree, which says")
        L.append("  nothing about cross-tree stability. The extrapolation is therefore inapplicable, not merely unmet.")
    else:
        L.append("  READ: r is positive and null-clearing at full size; the log-linear line %s the %.2f bar inside 900-1,500."
                 % ("reaches" if on_line else "does NOT reach", BAR))

    # ---------------------------------------------------------------- verdict block
    L.append("")
    L.append("=== VERDICTS (registered criteria) ===")
    L.append("  (1) PRIMARY  most-changed third, full size: r %+.4f vs null 95th %+.4f -> %s"
             % (r_low, n95_low, "FALSIFIER FIRES (positive, null-clearing): sub-anchor reopens as a data question"
                if clears else "AS PREDICTED (negative or null): closed for taxonomy reasons"))
    L.append("  (2) TREND    r low at frac 0.25 / 0.50 / 1.00 = %+.4f / %+.4f / %+.4f (null 95th %+.4f / %+.4f / %+.4f); slope %+.4f per doubling"
             % (trend[0.25]["r_low"], trend[0.5]["r_low"], trend[1.0]["r_low"], trend[0.25]["null95"], trend[0.5]["null95"], trend[1.0]["null95"], b))
    L.append("  (3) 900-1,500 on the trend line: %s" % ("YES" if on_line else "NO"))
    L.append("  McNemar rule (R7): this test scores no judge direction, so it carries no wrong-direction count; key denominator per cell =")
    L.append("  the cell's questions keyed for all 12 ARENA12 models (%d in the common set)." % len(qs))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
    cache = dict(obs={k: v for k, v in obs.items() if k != "strata"}, strata=obs["strata"], nulls_full=nulls_full,
                 trend={str(f): {k: v for k, v in t.items()} for f, t in trend.items()}, fixed_rows={str(f): v for f, v in fixed_rows.items()},
                 fit=dict(a=a, b=b, points=pts), common_qs=len(qs), bridge=bridge)
    json.dump(cache, open(os.path.join(SCRATCH, "key_subanchor_scale_cache.json"), "w"))


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
