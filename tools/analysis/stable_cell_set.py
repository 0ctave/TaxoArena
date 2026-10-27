"""STABLE-CELL-SET (registered 2026-09-19 before any code, commit 7bd1355, docs/judge_v2_program.md L7765-L7924; plan
2026-09-18 R1 = cells lead L2 A8). ZERO judge calls, ZERO builds. Key only. Pool p2dca21ab5f4ef3ae.

  python tools/analysis/stable_cell_set.py --selftest   # synthetic: plants a floor cell, a broken nesting, a perturbed Jaccard table; opens nothing of record
  python tools/analysis/stable_cell_set.py --dry-run    # pool id, the five Jaccard assertions, the R1 nesting assertion, the five cell supports on the three denominators; NO outcome number
  python tools/analysis/stable_cell_set.py --run        # writes experiment_results/anchorfree/redraw/stable_cell_set_outcome.txt (+ stable_cell_set_cells.csv) ONCE

THE QUESTION (registration, condensed; the programme file wins over this copy). Read as a 5-cell PARTITION of the pool of
record, do the 5 re-draw-stable certified sites of ANCHOR-FREE-REDRAW (record ids n00000001 / n00000005 / n00000017 /
n00000016 / n00000032 on af/seed_42), mapped to the CLEAN tree R1 af_clean_s42 by the Jaccard table of
anchor_free_redraw_outcome.txt (R1 block (d)), carry (i) support, (ii) a key-built profile with intervals, (iii) key-only
information, (iv) an interaction-only reliability, against the 14 named anchors (bareq512_s42), with the quantitative
remainder as a COMPLEMENT cell (not a certified site)?

THE OBJECT. Five disjoint cells by set difference along the spine root -> n00000005 -> {n00000017, n00000018} -> n00000042:
  S1 = R1 n00000042 [record n00000032]                                   (d3)
  S2 = R1 n00000017 minus n00000042 [n00000017 minus n00000032]          (d2 remainder)
  S3 = R1 n00000018 [n00000016]                                          (d2)
  S4 = R1 n00000005 minus (n00000017 union n00000018)                    (d1 remainder)
  S5 = R1 n00000001 minus n00000005 = the COMPLEMENT (= n00000004 under R1's root k = 2; UNCERTIFIED at 0.746; printed
       with that label on every row)
The five Jaccard values (1.000 / 0.979 / 0.953 / 0.937 / 0.856) are asserted from the outcome file's table BEFORE anything
else is read; the nesting is asserted from R1's dag_snapshots.jsonl; if it does not hold the partition is UNDETERMINED and
the script prints R1's ancestry and stops. Cell membership of a held-out question = anchor_free_readout's flatLeaf routing
(nearest R1 leaf centroid on the 256-dim MRL slice, then the leaf's ancestors). No cell carries a name: the majority-train
category and its share are a description only.

INSTRUMENTS (imported, never re-implemented): anchor_free_readout.corpus / full_vectors / sliced / load_tree / route /
f6_block; free_tests_f4_f7.keyed_questions / tree_leaves / embed_matrix / loo_imp / boot_mean_ci; profile_reliability.
reliability with demean_by_model and demean_two_way (the --interaction-only path of record, 2ccd646); profile_interval_union.
halvings_fixed / per_cell_r / stratum_jackknife / stratum_bootstrap (the PROFILE-INTERVAL-ALL / -UNION per-cell class
instrument: class on the LOWER of a recentred question bootstrap B = 125 x 16 halvings and a delete-one-question jackknife on
10 fixed halvings; both the profile reading and the order reading; class of record = the worse, the union's D2 rule);
profile_reliability_interaction.fit_additive_logit / key_table / halvings_fixed / mean_r / jack / variance_decomposition
(the logit-additive null of PROFILE-RELIABILITY-INTERACTION C2, 20 tables); systematic_budget.mcnemar_edge (exact two-sided
McNemar, integer arithmetic) for the ORDERED-KEY edges of (5).

READINGS CHOSEN WHERE THE REGISTRATION IS SILENT (each also printed in the outcome):
  * Denominators. (1) SUPPORT over the 3,445 judgeable pool questions (C1's denominator), the 2,811 judged questions (the
    x12 cache of record, mode=ro, never the x20 alone) and the 10,925 keyed questions (F6's denominator; the share that is
    on R1's TRAIN side is printed, not assumed).
  * Rosters. K12 = sorted(rubric_p8.ARENA12), the leg of record of PROFILE-RELIABILITY-INTERACTION; K46 = every eval_results
    model minus Meta-Llama-3-70B-Instruct (count pinned 46), beside.
  * Missing key rows. 37 of the 3,445 pool questions lack at least one ARENA12 row (176 for K46). The per-model accuracy and
    the reliability leg (4) use every available row per model (profile_reliability's key_build, the instrument of record:
    a model's half-accuracy is the mean over the half's questions that carry its row). The per-cell CLASS instrument (2)
    (profile_interval_union.stratum_jackknife) needs complete rows and is read on the cell's questions with a complete
    roster row; the count used is printed per row.
  * Cell order for the halvings: S1..S5 (the registration's order); the 14 anchors in order of first appearance over the
    sorted pool ids (the record's convention); no reproduction of a recorded value is expected on this question set.
  * (4) uses profile_reliability.reliability's default per-half floor (min_cell 25 = the 50-question cell floor of the
    recorded MMLU-Pro runs); every cell here is far above it. Jackknife = leave-one-cell-out, RE-HALVED (fresh Random(7)
    on the remaining cells) primary, FIXED halvings beside; z = 1.96; 5 (or 4) folds = a RESOLUTION statement.
  * The 14-anchor comparator is recomputed on the SAME 3,445 questions (bareq512_s42 primary routing -> depth-1 anchor)
    and the same roster; the recorded 0.8665 [0.8000, 0.9330] on the 2,811 judged questions is quoted beside, never
    compared by level.
  * (3) F6: anchor_free_readout.f6_block reproduces the record's (b) +10.791 / (c) +12.785 / (d) +3.604 to 3 dp as a
    gate; (a) = loo_imp on the same qs with the 5-cell partition (leaf -> cell by R1 ancestry). The clean-subset variant:
    loo_imp(part, qs_pool, models, G) with qs_pool = the keyed questions that are pool ids (fit = None: the cell
    statistic is built from the scored subset itself, the same design as the 10,925 row) - admitted without
    re-implementation, printed as unregistered / descriptive.
  * (5) Undominated set U = models with no ORDERED-KEY edge above them; an edge a > b is ESTABLISHED iff exact two-sided
    McNemar p < 0.05 on the cell's held-out pool questions AND b_ > c_ (a right, b wrong more often). The anchors' sets are
    computed on the anchors' held-out POOL questions (like for like with the cell) and, beside, on the anchors' JUDGED
    questions (the record's denominator for wrong(established)). "Differs from the 14 anchors' undominated sets that the
    cell overlaps" is scored under two readings (ANY overlapping anchor's set differs / ALL overlapping anchors' sets
    differ); an anchor overlaps a cell if >= 1 pool question of the cell routes to it (the overlap count is printed).
  * McNemar-established rule: wrong(established) applies to (5) only (no judge direction exists; both conventions n/a).
  * Write-once: --run refuses if the outcome file exists. Every DB mode=ro. --selftest opens nothing of record.
"""
import os, sys, csv, math, json, random, sqlite3, time, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import profile_reliability as pr
import profile_interval_union as piu
import profile_reliability_interaction as pri
import systematic_budget as sbg

POOL = pool_guard.MMLU_PRO_POOL                      # p2dca21ab5f4ef3ae
R1_DIR = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw", "af_clean_s42", "seed_42")
R1_SNAPSHOT = "20260917_201353"
REDRAW_OUT = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw", "anchor_free_redraw_outcome.txt")
OUT_DIR = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw")
OUT_TXT = os.path.join(OUT_DIR, "stable_cell_set_outcome.txt")
OUT_CSV = os.path.join(OUT_DIR, "stable_cell_set_cells.csv")
TREE14 = "bareq512_s42"
EXCLUDE = "Meta-Llama-3-70B-Instruct"

# the mapping of record (registration L7775-L7778; asserted from the outcome file's R1 (d) table before anything is read)
JACCARD = {"n00000001": ("n00000001", 1.000), "n00000005": ("n00000005", 0.979), "n00000017": ("n00000017", 0.953),
           "n00000016": ("n00000018", 0.937), "n00000032": ("n00000042", 0.856)}
R1_ROOT, R1_DISC, R1_D2A, R1_D2B, R1_D3 = "n00000001", "n00000005", "n00000017", "n00000018", "n00000042"
CELLS = ["S1", "S2", "S3", "S4", "S5"]
CELL_DESC = {"S1": "R1 n00000042 [record n00000032] (d3)",
             "S2": "R1 n00000017 minus n00000042 [n00000017 minus n00000032] (d2 remainder)",
             "S3": "R1 n00000018 [record n00000016] (d2)",
             "S4": "R1 n00000005 minus (n00000017 union n00000018) (d1 remainder)",
             "S5": "R1 n00000001 minus n00000005 = COMPLEMENT (= n00000004, UNCERTIFIED quantitative site, margin 0.746; not a certified site)"}
PIN = dict(pool=3445, judged=2811, keyed=10925, k12=12, k46=46, r1_leaves=82, r1_nodes=151, r1_iter=14, anchors=14)
F6_RECORD = dict(category=10.791, leaf=12.785, depth1=3.604)   # anchor_free_af_clean_s42_readout.txt (3a), x1000
FLOOR = 120                 # C1: held-out questions per cell on the pool of record
BAR = 0.70
SEED = 7
REPS = pr.REPS              # 40
Z = 1.96
N_NULL = 20
BOOT_B, BOOT_H, JACK_H = 125, 16, 10
ACC_B = 2000                # question bootstrap of the per-(cell, model) accuracy (a 0.975 tail is published)
sb = pr.sb


# ----------------------------------------------------------------------------------------------- the two gates
def parse_jaccard_table(path=REDRAW_OUT):
    """The R1 block's '(d) certified-site identity vs the record' table: {record id: (arm id, jaccard, verdict)}."""
    rows = {}; inside = False; in_d = False
    for line in open(path, encoding="utf-8"):
        if line.startswith("--- R1 af_clean_s42"): inside = True; continue
        if inside and line.startswith("--- "): break
        if inside and line.strip().startswith("(d) certified-site identity"): in_d = True; continue
        if inside and in_d:
            s = line.strip()
            if s.startswith("(e)") or not s: break
            p = s.split()
            if len(p) >= 6 and p[0].startswith("n0") and p[4].startswith("n0"):
                rows[p[0]] = (p[4], float(p[5]), " ".join(p[6:]))
    return rows


def assert_jaccard(table):
    """The five values of record, asserted before anything else is read. Returns the lines printed."""
    L = []
    for rec, (arm, jac) in JACCARD.items():
        if rec not in table:
            raise SystemExit("[JACCARD] record site %s absent from the R1 (d) table of %s" % (rec, REDRAW_OUT))
        got_arm, got_j, verdict = table[rec]
        ok = (got_arm == arm) and (abs(got_j - jac) < 5e-4) and verdict.startswith("reproduces")
        L.append("  [%s] record %s -> R1 %s Jaccard %.3f (registered %s / %.3f; verdict '%s')" % ("ok" if ok else "FAIL", rec, got_arm, got_j, arm, jac, verdict))
        if not ok:
            raise SystemExit("[JACCARD] mapping of record differs for %s: %s" % (rec, table[rec]))
    return L


def ancestry(byid, kid2parent, nid):
    out = [nid]
    while nid in kid2parent:
        nid = kid2parent[nid]; out.append(nid)
    return out


def assert_nesting(tree):
    """n00000042 under n00000017; n00000017 and n00000018 under n00000005; n00000005 under the root n00000001 (depth 0)."""
    byid = tree["byid"]
    kid2parent = {c: n["id"] for n in byid.values() for c in n.get("childIds", [])}
    want = [(R1_D3, R1_D2A), (R1_D2A, R1_DISC), (R1_D2B, R1_DISC), (R1_DISC, R1_ROOT)]
    bad = [(c, kid2parent.get(c), p) for c, p in want if kid2parent.get(c) != p]
    L = []
    if bad or byid.get(R1_ROOT, {}).get("depth") != 0 or R1_ROOT in kid2parent:
        L.append("  NESTING DOES NOT HOLD on R1: " + "; ".join("%s parent is %s, expected %s" % b for b in bad))
        for nid in (R1_ROOT, R1_DISC, R1_D2A, R1_D2B, R1_D3):
            L.append("    ancestry of %s: %s" % (nid, " <- ".join(ancestry(byid, kid2parent, nid)) if nid in byid else "ABSENT"))
        return False, L, kid2parent
    for c, p in want:
        L.append("  [ok] %s (d%d, %s) is a child of %s (d%d)" % (c, byid[c]["depth"], byid[c]["label"][:24], p, byid[p]["depth"]))
    root_kids = byid[R1_ROOT].get("childIds", [])
    L.append("  [ok] root %s depth 0, k = %d children %s; the complement S5 = root minus %s = %s"
             % (R1_ROOT, len(root_kids), root_kids, R1_DISC, sorted(set(root_kids) - {R1_DISC})))
    return True, L, kid2parent


def cell_of_leaf_fn(tree, kid2parent):
    def cell_of(leaf_id):
        anc = set(ancestry(tree["byid"], kid2parent, leaf_id))
        if R1_D3 in anc: return "S1"
        if R1_D2A in anc: return "S2"
        if R1_D2B in anc: return "S3"
        if R1_DISC in anc: return "S4"
        if R1_ROOT in anc: return "S5"
        return None                                   # a defect under a partition of the root
    return cell_of


# ----------------------------------------------------------------------------------------------- statistics
def mean_sd(v):
    return piu.mean_sd(v)


def spearman(xs, ys):
    return piu.spearman(xs, ys)


def classify(point, lo, n):
    if n < FLOOR: return "UNDETERMINED-by-support"
    if point != point: return "n/a"
    if point >= BAR and lo == lo and lo >= BAR: return "PASS"
    if point >= BAR: return "PASS-WITH-INTERVAL"
    return "FAIL"


def worse(a, b):
    order = {"PASS": 0, "PASS-WITH-INTERVAL": 1, "FAIL": 2, "n/a": 3, "UNDETERMINED-by-support": 4}
    return a if order.get(a, 3) >= order.get(b, 3) else b


def kb_for(K, models):
    """profile_reliability's key_build: per-model mean over the half's questions carrying the model's row."""
    def kb(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if q in K and m in K[q]]
            if v: d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None
    return kb


def r_mean(per_rep, dm, drop=None, min_points=None):
    return mean_sd([pri.r_of(P, dm, drop, min_points) for P in per_rep])


def reliability_leg(cells, qsel, K, models, tag):
    """(4): model-demeaned and interaction-only R on the same 40 halvings (Random(7)); leave-one-cell-out jackknife
    RE-HALVED (primary) and FIXED (beside); halving SD. cells: ordered dict {cell: [qids]}.
    profile_reliability.reliability's 50-point floor is a 14 x 12 board floor (it makes a 4-cell x 12-model object, 48
    points, and every LOCO fold of the 5-cell K12 object undefined); as PROFILE-INTERVAL-ALL-UNION C3b did for 3-stratum
    sources, the fixed-halving mirror (profile_interval_union.halvings_fixed, line-for-line reliability()) is read with the
    floor at 2 x |roster| points. Wherever the full object has >= 50 points the mirror is asserted equal to reliability()."""
    build = kb_for(K, models)
    mp = 2 * len(models)
    per_rep = piu.halvings_fixed(cells, qsel, build, models, random.Random(SEED), min_cell=25)
    out = dict(tag=tag, cells=list(cells), n_cells=len(cells), mirror_checked=False)
    for name, dm in (("model", pr.demean_by_model), ("both", pr.demean_two_way)):
        r, sd, n = r_mean(per_rep, dm, None, mp)
        if len(cells) * len(models) >= 50:
            r_ref, _, _ = pr.reliability(cells, qsel, build, models, random.Random(SEED), demean=dm)
            assert abs(r_ref - r) < 1e-12, "fixed-halving mirror differs from reliability(): %r vs %r" % (r_ref, r)
            out["mirror_checked"] = True
        R = sb(r)
        loo_fx = [sb(r_mean(per_rep, dm, c, mp)[0]) for c in cells]
        loo_re = []
        for c in cells:
            sub = {k: v for k, v in cells.items() if k != c}
            pr_i = piu.halvings_fixed(sub, qsel, build, models, random.Random(SEED), min_cell=25)
            loo_re.append(sb(r_mean(pr_i, dm, None, mp)[0]))
        se_fx, lo_fx, hi_fx = pri.jack(R, loo_fx) if len(loo_fx) >= 2 else (float("nan"),) * 3
        se_re, lo_re, hi_re = pri.jack(R, loo_re) if len(loo_re) >= 2 else (float("nan"),) * 3
        out[name] = dict(r=r, sd=sd, n=n, R=R, halv_sd=(sb(r + sd) - R) if sd == sd else float("nan"),
                         lo_fx=lo_fx, hi_fx=hi_fx, lo_re=lo_re, hi_re=hi_re, loo_fx=dict(zip(cells, loo_fx)), loo_re=dict(zip(cells, loo_re)))
    return out


def null_leg(cells, K, models, n_tables=N_NULL):
    """PROFILE-RELIABILITY-INTERACTION C2: Bernoulli(logistic(a_m - d_c)) with a_m, d_c the additive-logit MLE on the real
    table; 20 tables; the instrument read under both demeanings (fixed halvings, Random(7))."""
    nd = pri.null_tables(cells, K, models, n_tables, list(range(1, n_tables + 1)))
    vd = pri.variance_decomposition(nd["k"], nd["n"])
    m = pri.summarise_null(nd["reads"], 0); b = pri.summarise_null(nd["reads"], 1)
    return dict(model=m, both=b, shares=vd["shares"], iters=nd["iters"], clipped=nd["clipped"], d=dict(zip(cells, nd["d"])), a_range=(float(nd["a"].min()), float(nd["a"].max())))


def undominated(models, K, qs, alpha=0.05):
    """U = models with no ESTABLISHED ORDERED-KEY edge above them (exact two-sided McNemar p < alpha, systematic_budget.
    mcnemar_edge, on qs). Returns (U, established edges [(a, b, p, b_, c_)] with a above b)."""
    aq = {"cell": list(qs)}
    est = []
    dominated = set()
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            p, b_, c_ = sbg.mcnemar_edge({"anchor": "cell", "a": a, "b": b}, K, aq)
            if p < alpha and b_ != c_:
                hi, lo = (a, b) if b_ > c_ else (b, a)
                est.append((hi, lo, p, max(b_, c_), min(b_, c_))); dominated.add(lo)
    return sorted(m for m in models if m not in dominated), est


# ----------------------------------------------------------------------------------------------- the analysis (data-agnostic; --run and --selftest share it)
def analyse(D, L, log=None):
    """D: dict with cells_pool {cell: [q]} (ordered S1..S5), cells_judged, cells_keyed_n, anchors_pool {anchor: [q]},
    anchors_judged, K (q -> {m: 0/1}), models12, models46, f6 (dict or None), train_major {cell: (cat, share, n)},
    migration {cat: Counter(cell)}, n_pool, n_judged, n_keyed. Returns (lines, csv rows, summary)."""
    log = log or (lambda s: None); t0 = time.time(); say = L.append
    cells = D["cells_pool"]; K = D["K"]
    n_of = {c: len(cells[c]) for c in CELLS}
    qsel = set(q for v in cells.values() for q in v)
    summary = {}

    # ---------- (1) SUPPORT ----------
    say("")
    say("=== (1) SUPPORT: held-out questions per cell on the three denominators ===")
    say("  %-4s %-100s %8s %8s %8s" % ("cell", "definition", "pool", "judged", "keyed"))
    for c in CELLS:
        say("  %-4s %-100s %8d %8d %8d" % (c, CELL_DESC[c], n_of[c], len(D["cells_judged"].get(c, [])), D["cells_keyed_n"].get(c, 0)))
    say("  %-4s %-100s %8d %8d %8d" % ("all", "denominators: %d pool of record / %d judged (x12 cache) / %d keyed (F6)" % (D["n_pool"], D["n_judged"], D["n_keyed"]),
                                       sum(n_of.values()), sum(len(v) for v in D["cells_judged"].values()), sum(D["cells_keyed_n"].values())))
    say("  defects (routed leaf with no ancestor among the five sites): pool %d, judged %d, keyed %d" % (D["defects"]["pool"], D["defects"]["judged"], D["defects"]["keyed"]))
    say("  keyed questions on R1's TRAIN side (not pool ids): %d of %d = %.1f%% ('clean' applies to the pool rows only)" % (D["keyed_train"], D["n_keyed"], 100.0 * D["keyed_train"] / max(1, D["n_keyed"])))
    c1 = all(n_of[c] >= FLOOR for c in CELLS)
    under = [c for c in CELLS if n_of[c] < FLOOR]
    summary.update(n_of=n_of, c1=c1, under=under)

    # ---------- (5a) DESCRIPTIVE: majority-train category, migration ----------
    say("")
    say("=== (5) DESCRIPTIVE: majority-train category per cell (a description, not a name) and the migration matrix on the pool ===")
    for c in CELLS:
        cat, share, n = D["train_major"].get(c, ("-", float("nan"), 0))
        say("  %-4s majority-train category '%s' share %.3f of %d train questions routed to the cell%s" % (c, cat, share, n, "  [COMPLEMENT, uncertified]" if c == "S5" else ""))
    mig = D["migration"]
    say("  %-17s" % "category" + "".join("%7s" % c for c in CELLS) + "     n")
    for cat in sorted(mig, key=lambda k: -sum(mig[k].values())):
        say("  %-17s" % cat + "".join("%7d" % mig[cat].get(c, 0) for c in CELLS) + "%6d" % sum(mig[cat].values()))
    say("  %-17s" % "TOTAL" + "".join("%7d" % sum(M.get(c, 0) for M in mig.values()) for c in CELLS) + "%6d" % sum(sum(M.values()) for M in mig.values()))

    # ---------- (2) PROFILE ROWS ----------
    say("")
    say("=== (2) PROFILE ROWS: key accuracy per (cell, model) with a question-bootstrap 95%% interval (B = %d), the model- and cell-demeaned deviation, and the per-cell class ===" % ACC_B)
    say("  key-built rows ONLY (no judge row on any free cell). Denominator per row = the cell's held-out pool questions carrying the model's key row (n_m).")
    rows_csv = []
    prof = {}
    for roster_tag, models in (("K12", D["models12"]), ("K46", D["models46"])):
        acc = np.full((len(models), len(CELLS)), np.nan); n_mc = np.zeros((len(models), len(CELLS)), int)
        lo = np.full_like(acc, np.nan); hi = np.full_like(acc, np.nan)
        rs = np.random.RandomState(2026)
        for j, c in enumerate(CELLS):
            qs = cells[c]
            if not qs: continue
            A = np.array([[K.get(q, {}).get(m, np.nan) for m in models] for q in qs], dtype=float)     # n x M
            acc[:, j] = np.nanmean(A, axis=0); n_mc[:, j] = (~np.isnan(A)).sum(axis=0)
            idx = rs.randint(0, len(qs), size=(ACC_B, len(qs)))
            boots = np.stack([np.nanmean(A[idx[b]], axis=0) for b in range(ACC_B)])
            lo[:, j] = np.percentile(boots, 2.5, axis=0); hi[:, j] = np.percentile(boots, 97.5, axis=0)
        gm = np.nanmean(acc); rm = np.nanmean(acc, axis=1, keepdims=True) - gm; cm = np.nanmean(acc, axis=0, keepdims=True) - gm
        dev = acc - gm - rm - cm
        prof[roster_tag] = dict(acc=acc, dev=dev, lo=lo, hi=hi, n=n_mc, models=models)
    # per-cell class (PROFILE-INTERVAL-ALL / -UNION instrument) on complete-roster rows
    cls = {}
    for roster_tag, models in (("K12", D["models12"]), ("K46", D["models46"])):
        Kc = {q: np.array([K[q][m] for m in models], float) for q in qsel if all(m in K.get(q, {}) for m in models)}
        cells_c = {c: [q for q in cells[c] if q in Kc] for c in CELLS}
        cells_c = {c: v for c, v in cells_c.items() if len(v) >= 2 * 25}
        build = piu.make_key_build(Kc, models)
        qsel_c = set(q for v in cells_c.values() for q in v)
        sides = []
        per_rep = piu.halvings_fixed(cells_c, qsel_c, build, models, random.Random(SEED), min_cell=25, sides=sides)
        pa = defaultdict(lambda: ([], []))
        for P in per_rep:
            for c, (r1, r2) in piu.per_cell_r(P).items():
                pa[c][0].append(r1); pa[c][1].append(r2)
        point = {c: (mean_sd(v[0]), mean_sd(v[1])) for c, v in pa.items()}
        jk = piu.stratum_jackknife(per_rep, sides, Kc, models, [c for c in CELLS if c in point], JACK_H)
        boot, _ = piu.stratum_bootstrap({c: v for c, v in cells_c.items() if c in point}, build, models, BOOT_B, BOOT_H)
        log("(2) %s class instrument done %.0fs" % (roster_tag, time.time() - t0))
        for c in CELLS:
            n = n_of[c]; nc = len(cells_c.get(c, []))
            if c not in point:
                cls[(roster_tag, c)] = dict(n=n, n_complete=nc, R_prof=float("nan"), low_p=float("nan"), cls_p="UNDETERMINED-by-support" if n < FLOOR else "n/a",
                                            R_raw=float("nan"), low_r=float("nan"), cls_r="UNDETERMINED-by-support" if n < FLOOR else "n/a", halv=float("nan"))
                cls[(roster_tag, c)]["cls"] = worse(cls[(roster_tag, c)]["cls_p"], cls[(roster_tag, c)]["cls_r"]); continue
            (rp, sdp, _), (rr, sdr, _) = point[c]
            Rp, Rr = sb(rp), sb(rr)
            plo, phi = piu.pct(boot[c][0], 0.025), piu.pct(boot[c][0], 0.975); pmu = mean_sd(boot[c][0])[0]
            rlo, rhi = piu.pct(boot[c][1], 0.025), piu.pct(boot[c][1], 0.975); rmu = mean_sd(boot[c][1])[0]
            cplo, cphi = plo - (pmu - Rp), phi - (pmu - Rp); crlo, crhi = rlo - (rmu - Rr), rhi - (rmu - Rr)
            se_p, se_r, _ = jk[c]
            jlo_p, jlo_r = Rp - Z * se_p, Rr - Z * se_r
            low_p = min(x for x in (cplo, jlo_p) if x == x) if any(x == x for x in (cplo, jlo_p)) else float("nan")
            low_r = min(x for x in (crlo, jlo_r) if x == x) if any(x == x for x in (crlo, jlo_r)) else float("nan")
            cp, cr = classify(Rp, low_p, n), classify(Rr, low_r, n)
            cls[(roster_tag, c)] = dict(n=n, n_complete=nc, R_prof=Rp, boot_p=(cplo, cphi), jk_p=(jlo_p, Rp + Z * se_p), low_p=low_p, cls_p=cp,
                                        R_raw=Rr, boot_r=(crlo, crhi), jk_r=(jlo_r, Rr + Z * se_r), low_r=low_r, cls_r=cr, cls=worse(cp, cr),
                                        halv=(sb(rp + sdp) - Rp) if sdp == sdp else float("nan"))
    for roster_tag in ("K12", "K46"):
        P_ = prof[roster_tag]; models = P_["models"]
        say("")
        say("  --- %s (%d models) ---" % (roster_tag, len(models)))
        say("  %-4s %5s %6s  %7s %-17s %-17s %-24s | %7s %-17s %-17s %-24s | %s" % ("cell", "n", "n_cmp", "R_prof", "boot95 recentred", "jackknife 95%", "class (profile)", "R_raw", "boot95 recentred", "jackknife 95%", "class (order)", "CLASS OF RECORD (worse)"))
        for c in CELLS:
            d = cls[(roster_tag, c)]
            if d["R_prof"] != d["R_prof"]:
                say("  %-4s %5d %6d  %s" % (c, d["n"], d["n_complete"], d["cls"])); continue
            say("  %-4s %5d %6d  %7.4f [%6.4f, %6.4f] [%6.4f, %6.4f] %-24s | %7.4f [%6.4f, %6.4f] [%6.4f, %6.4f] %-24s | %s%s"
                % (c, d["n"], d["n_complete"], d["R_prof"], d["boot_p"][0], d["boot_p"][1], d["jk_p"][0], d["jk_p"][1], d["cls_p"],
                   d["R_raw"], d["boot_r"][0], d["boot_r"][1], d["jk_r"][0], d["jk_r"][1], d["cls_r"], d["cls"], "  [COMPLEMENT]" if c == "S5" else ""))
        say("  per (cell, model): accuracy [boot95] over n_m; deviation = acc - model mean - cell mean + grand mean (model- and cell-demeaned)")
        hdr = "  %-30s" % "model" + "".join("  %-34s" % c for c in CELLS)
        say(hdr)
        for i, m in enumerate(models):
            say("  %-30s" % m[:30] + "".join("  %.3f [%.3f,%.3f] dev %+.3f n%-4d" % (P_["acc"][i, j], P_["lo"][i, j], P_["hi"][i, j], P_["dev"][i, j], P_["n"][i, j]) for j in range(len(CELLS))))
            for j, c in enumerate(CELLS):
                rows_csv.append(dict(roster=roster_tag, cell=c, complement=int(c == "S5"), model=m, n_m=int(P_["n"][i, j]), n_cell=n_of[c], acc=P_["acc"][i, j], lo=P_["lo"][i, j], hi=P_["hi"][i, j],
                                     dev=P_["dev"][i, j], cell_R_prof=cls[(roster_tag, c)]["R_prof"], cell_cls_profile=cls[(roster_tag, c)]["cls_p"],
                                     cell_R_raw=cls[(roster_tag, c)]["R_raw"], cell_cls_order=cls[(roster_tag, c)]["cls_r"], cell_cls_record=cls[(roster_tag, c)]["cls"]))
    summary["cls"] = cls

    # ---------- (3) KEY INFORMATION ----------
    say("")
    say("=== (3) KEY INFORMATION: F6 key-only LOO Brier improvement over the marginal x 1000 (free_tests_f4_f7.loo_imp; %d models) ===" % len(D["models46"]))
    f6 = D["f6"]
    if f6 is None:
        say("  not computed (no F6 object supplied)"); summary["f6"] = None
    else:
        say("  denominator: %d keyed questions (F6's; %.1f%% on R1's TRAIN side)" % (f6["n"], 100.0 * D["keyed_train"] / max(1, D["n_keyed"])))
        say("  gate: the record's (b) / (c) / (d) reproduce to 3 dp: category %+.3f (record %+.3f) %s | leaves %+.3f (record %+.3f) %s | depth-1 %+.3f (record %+.3f) %s"
            % (f6["category"], F6_RECORD["category"], "ok" if f6["gate"]["category"] else "NO", f6["leaf"], F6_RECORD["leaf"], "ok" if f6["gate"]["leaf"] else "NO",
               f6["depth1"], F6_RECORD["depth1"], "ok" if f6["gate"]["depth1"] else "NO"))
        say("  (a) 5-cell partition    %+.3f" % f6["cells"])
        say("  (b) 14 true categories  %+.3f" % f6["category"])
        say("  (c) R1's %d leaves      %+.3f" % (f6["leaves_n"], f6["leaf"]))
        say("  (d) R1's 2 depth-1      %+.3f" % f6["depth1"])
        say("  paired per-question (a) minus (b): %+.3f, F6 bootstrap 95%% [%+.3f, %+.3f] (n = %d)" % (f6["diff"], f6["diff_lo"], f6["diff_hi"], f6["n"]))
        if f6.get("pool") is not None:
            p = f6["pool"]
            say("  UNREGISTERED, descriptive - the same four on the pool of record's keyed questions only (%d of %d pool ids are keyed; cell statistic built on that subset):" % (p["n"], D["n_pool"]))
            say("     (a) %+.3f  (b) %+.3f  (c) %+.3f  (d) %+.3f | (a) - (b) %+.3f [%+.3f, %+.3f]" % (p["cells"], p["category"], p["leaf"], p["depth1"], p["diff"], p["diff_lo"], p["diff_hi"]))
        summary["f6"] = f6

    # ---------- (4) RELIABILITY ----------
    say("")
    say("=== (4) RELIABILITY: split-half R (Spearman-Brown, %d halvings, Random(%d), profile_reliability.reliability; per-half floor 25) ===" % (REPS, SEED))
    say("  model-demeaned AND interaction-only (model- and cell-demeaned, demean_two_way); leave-one-cell-out jackknife RE-HALVED (primary) / FIXED (beside), z = %.2f; halving SD (SB scale)." % Z)
    say("  a jackknife over 4-5 cells is a RESOLUTION statement, not a confidence statement (L5612). KEY DENOMINATOR: the cell's held-out pool questions (every available key row per model).")
    say("  reliability()'s 50-point floor (a 14 x 12 board floor) is lowered to 2 x |roster| points through the fixed-halving mirror (the PROFILE-INTERVAL-ALL-UNION C3b precedent) so that the")
    say("  4-cell K12 object (48 points) and the LOCO folds of the 5-cell K12 object are defined; wherever the full object has >= 50 points the mirror is asserted equal to reliability().")
    legs = {}
    objects = [("5cells", "5 cells S1-S5 (the registered object)", cells), ("14anchors", "14 anchors of %s on the SAME %d questions (like-for-like comparator)" % (TREE14, D["n_pool"]), D["anchors_pool"]),
               ("4cells", "4 stable cells S1-S4 (discursive spine, without the complement)", {c: cells[c] for c in CELLS[:4]})]
    for roster_tag, models in (("K12", D["models12"]), ("K46", D["models46"])):
        for okey, odesc, ocells in objects:
            usable = {c: v for c, v in ocells.items() if len(v) >= 50}
            if len(usable) < 2:
                legs[(roster_tag, okey)] = None; continue
            legs[(roster_tag, okey)] = reliability_leg(usable, set(q for v in usable.values() for q in v), K, models, "%s/%s" % (roster_tag, okey))
            log("(4) %s %s done %.0fs" % (roster_tag, okey, time.time() - t0))
    say("  %-4s %-9s %-6s %5s %8s %8s %8s  %-18s %-18s" % ("key", "object", "demean", "cells", "r", "R(SB)", "halvSD", "jk RE-HALVED 95%", "jk FIXED 95%"))
    for roster_tag, _ in (("K12", None), ("K46", None)):
        for okey, odesc, _ in objects:
            lg = legs[(roster_tag, okey)]
            if lg is None:
                say("  %-4s %-9s undefined (fewer than 2 cells with >= 50 questions)" % (roster_tag, okey)); continue
            for name in ("model", "both"):
                e = lg[name]
                say("  %-4s %-9s %-6s %5d %8.4f %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]%s"
                    % (roster_tag, okey, name, lg["n_cells"], e["r"], e["R"], e["halv_sd"], e["lo_re"], e["hi_re"], e["lo_fx"], e["hi_fx"],
                       "   <- LEG OF RECORD (C2, P2)" if (roster_tag, okey, name) == ("K12", "5cells", "both") else ""))
    say("  leave-one-cell-out R (interaction-only, re-halved), K12: " + " | ".join("%s: %s" % (okey, ", ".join("-%s %.4f" % (c, v) for c, v in legs[("K12", okey)]["both"]["loo_re"].items())) for okey, _, _ in objects if legs[("K12", okey)]))
    say("  recorded beside, NOT compared by level (different question set: 2,811 judged q): PROFILE-RELIABILITY-INTERACTION K12 interaction-only 0.8665 [0.8000, 0.9330], K46 0.8118 [0.7254, 0.8983] (L6847).")
    say("  (3b) of the R1 readout beside: leaf R 0.786 (22 cells >= 50 q, model-demeaned), depth-1 R nan (2 cells).")
    # the logit-additive null on the 5-cell object (registered) and on the 14-anchor comparator (beside, unregistered)
    say("  logit-additive null (PROFILE-RELIABILITY-INTERACTION C2; %d tables; a_m, d_c fitted on the real table; fixed halvings): the curvature floor beside the real reading" % N_NULL)
    nulls = {}
    for roster_tag, models in (("K12", D["models12"]), ("K46", D["models46"])):
        for okey, odesc, ocells in (objects[0], objects[1]):
            usable = {c: v for c, v in ocells.items() if len(v) >= 50}
            if len(usable) < 2: continue
            nd = null_leg(usable, K, models); nulls[(roster_tag, okey)] = nd
            lg = legs[(roster_tag, okey)]
            say("    %s %-9s null model-only median %.4f [%.4f, %.4f] (real %.4f) | interaction-only median %.4f [%.4f, %.4f] (real %.4f; real - null %+.4f) | variance shares model/cell/inter %.2f/%.2f/%.2f%s"
                % (roster_tag, okey, nd["model"][0], nd["model"][1], nd["model"][2], lg["model"]["R"], nd["both"][0], nd["both"][1], nd["both"][2], lg["both"]["R"], lg["both"]["R"] - nd["both"][0], *nd["shares"],
                   "" if okey == "5cells" else "  [beside, unregistered]"))
            log("(4) null %s %s done %.0fs" % (roster_tag, okey, time.time() - t0))
    summary["legs"] = legs; summary["nulls"] = nulls

    # ---------- (5b) UNDOMINATED SETS ----------
    say("")
    say("=== (5) UNDOMINATED SETS of the K12 key per cell (no ESTABLISHED ORDERED-KEY edge above: exact two-sided McNemar p < 0.05, systematic_budget.mcnemar_edge, integer arithmetic; the wrong(established) rule) ===")
    U = {}; est_n = {}
    for c in CELLS:
        U[c], est = undominated(D["models12"], K, cells[c]); est_n[c] = len(est)
    UA_pool = {}; UA_judged = {}
    for a, qs in D["anchors_pool"].items():
        UA_pool[a], _ = undominated(D["models12"], K, qs)
    for a, qs in D["anchors_judged"].items():
        UA_judged[a], _ = undominated(D["models12"], K, qs)
    overlap = defaultdict(Counter)
    for c in CELLS:
        for q in cells[c]:
            a = D["anchor_of_pool"].get(q)
            if a: overlap[c][a] += 1
    n_pairs = len(D["models12"]) * (len(D["models12"]) - 1) // 2
    differs_any = {}; differs_all = {}
    for c in CELLS:
        say("  %-4s n=%4d  U = %s  (established edges %d of %d pairs)%s" % (c, n_of[c], U[c], est_n[c], n_pairs, "  [COMPLEMENT]" if c == "S5" else ""))
        ov = overlap[c]
        diffs = []
        for a, k in ov.most_common():
            same = (UA_pool[a] == U[c])
            diffs.append(not same)
            say("        overlaps anchor %-18s %4d q (%.0f%% of the cell): U_anchor(pool) = %s %s | U_anchor(judged) = %s"
                % (a, k, 100.0 * k / n_of[c], UA_pool[a], "SAME" if same else "DIFFERS", UA_judged.get(a, "-")))
        differs_any[c] = any(diffs) if diffs else False; differs_all[c] = all(diffs) if diffs else False
        say("        differs from the overlapping anchors' sets: ANY-reading %s, ALL-reading %s" % (differs_any[c], differs_all[c]))
    say("  anchors' undominated sets on their held-out POOL questions (like for like) and on their JUDGED questions (the record's denominator):")
    for a in D["anchors_pool"]:
        say("    %-18s pool n=%4d U = %s | judged n=%4d U = %s" % (a, len(D["anchors_pool"][a]), UA_pool[a], len(D["anchors_judged"].get(a, [])), UA_judged.get(a, "-")))
    summary.update(U=U, differs_any=differs_any, differs_all=differs_all)

    # ---------- CRITERIA, PREDICTIONS, FALSIFIER ----------
    say("")
    say("=== CRITERIA (in the registration's words; scored HELD / FAILED) ===")
    say("  C1 SUPPORT 'every one of the 5 cells has >= %d held-out questions on the %d-question pool of record': %s -> %s"
        % (FLOOR, D["n_pool"], ", ".join("%s %d" % (c, n_of[c]) for c in CELLS), "HELD" if c1 else "FAILED (%s below the floor: UNDETERMINED-by-support)" % under))
    lg = legs.get(("K12", "5cells"))
    R_both = lg["both"]["R"] if lg else float("nan"); R_model = lg["model"]["R"] if lg else float("nan")
    c2 = (R_both == R_both) and R_both >= BAR
    say("  C2 PROFILE 'the K12 interaction-only split-half R over the 5 cells >= %.2f at the point': R = %.4f (re-halved jk [%.4f, %.4f]; fixed [%.4f, %.4f]) -> %s"
        % (BAR, R_both, lg["both"]["lo_re"] if lg else float("nan"), lg["both"]["hi_re"] if lg else float("nan"), lg["both"]["lo_fx"] if lg else float("nan"), lg["both"]["hi_fx"] if lg else float("nan"), "HELD" if c2 else "FAILED"))
    if f6 is not None:
        c3 = f6["cells"] >= F6_RECORD["category"]
        say("  C3 INFORMATION 'F6 of the 5-cell partition >= the 14 categories' +10.791 on the 10,925 keyed questions': %+.3f vs %+.3f (recomputed %+.3f; paired diff %+.3f [%+.3f, %+.3f]) -> %s"
            % (f6["cells"], F6_RECORD["category"], f6["category"], f6["diff"], f6["diff_lo"], f6["diff_hi"], "HELD" if c3 else "FAILED"))
    else:
        c3 = None; say("  C3 INFORMATION: not scored (no F6 object)")
    say("")
    say("=== VERDICT (the registered rule: 'an anchor-free profile home exists at 5 cells' only if C1 AND C2; C3 sets the qualifier) ===")
    if c1 and c2:
        qual = "not qualified (C3 not scored)" if c3 is None else ("with MORE key information than the 14 names" if c3 else "with less key information than the 14 names")
        say("  SENTENCE OF RECORD: an anchor-free profile home exists at 5 cells, %s (C1 HELD, C2 HELD, C3 %s)." % (qual, "HELD" if c3 else ("FAILED" if c3 is not None else "not scored")))
    else:
        say("  SENTENCE OF RECORD: the 5-site spine is STRUCTURAL ONLY (C1 %s, C2 %s): no anchor-free profile home at 5 cells; the paper's profile home is the 14 anchors (or the union strata); the anchor-free line's remaining claim is routing on the union (FW L180)."
            % ("HELD" if c1 else "FAILED", "HELD" if c2 else "FAILED"))
    say("  the complement cell S5 is printed as a COMPLEMENT (n00000004, uncertified 0.746) on every row; it is never a certified site.")

    say("")
    say("=== PREDICTIONS (the plan's R1 P1-P3 and the registrar's blind additions P4-P7, labelled; scored HELD / FAILED) ===")
    p1 = c1; p1f = all(n_of[c] >= 200 for c in CELLS)
    say("  P1 (plan) '5 cells, all >= 120 held-out questions on the pool': %s | cells lead's finer band 'all >= 200': %s" % ("HELD" if p1 else "FAILED", "HELD" if p1f else "FAILED"))
    p2 = R_both == R_both and 0.75 <= R_both <= 0.88
    p2m = R_model == R_model and 0.85 <= R_model <= 0.92
    say("  P2 (plan) 'K12 interaction-only R over the 5 cells in [0.75, 0.88]': %.4f -> %s | cells lead's model-demeaned band [0.85, 0.92] on the model-demeaned line: %.4f -> %s"
        % (R_both, "HELD" if p2 else "FAILED", R_model, "HELD" if p2m else "FAILED"))
    if f6 is not None:
        p3 = (8.0 <= f6["cells"] <= 11.0) and (not c3)
        say("  P3 (plan) 'F6 of the 5-cell partition in [+8, +11] x 1e-3 AND C3 FAILS': %+.3f, C3 %s -> %s" % (f6["cells"], "FAILED" if not c3 else "HELD", "HELD" if p3 else "FAILED"))
    else:
        p3 = None; say("  P3: not scored")
    p4 = (R_model - R_both) >= 0.03 if (R_model == R_model and R_both == R_both) else False
    say("  P4 (registrar) 'model-demeaned R over the 5 cells exceeds the interaction-only R by >= 0.03': %.4f - %.4f = %+.4f -> %s" % (R_model, R_both, R_model - R_both, "HELD" if p4 else "FAILED"))
    share5 = n_of["S5"] / max(1, sum(n_of.values()))
    p5 = share5 >= 0.40
    say("  P5 (registrar) 'the complement cell S5 holds >= 40%% of the pool': %d / %d = %.1f%% -> %s" % (n_of["S5"], sum(n_of.values()), 100 * share5, "HELD" if p5 else "FAILED"))
    lg4 = legs.get(("K12", "4cells"))
    R4 = lg4["both"]["R"] if lg4 else float("nan")
    p6 = (R4 == R4 and R_both == R_both and R4 <= R_both - 0.05)
    say("  P6 (registrar) 'the 4-cell spine-only interaction-only R is LOWER than the 5-cell reading by >= 0.05': 4-cell %.4f vs 5-cell %.4f (diff %+.4f) -> %s" % (R4, R_both, R4 - R_both, "HELD" if p6 else "FAILED"))
    n_any = sum(1 for c in CELLS if differs_any[c]); n_all = sum(1 for c in CELLS if differs_all[c])
    p7_any = n_any <= 1; p7_all = n_all <= 1
    say("  P7 (registrar) 'the undominated set differs from the overlapping anchors' in at most 1 of 5 cells': ANY-reading %d of 5 -> %s | ALL-reading %d of 5 -> %s"
        % (n_any, "HELD" if p7_any else "FAILED", n_all, "HELD" if p7_all else "FAILED"))
    say("")
    say("=== FALSIFIER (the plan's) ===")
    f1 = (not c1) or (not c2)
    say("  F1 'any stable cell below 120 held-out questions (C1 fails) OR K12 interaction-only R < 0.70 (C2 fails)': %s" % ("FIRES" if f1 else "silent"))
    if f1:
        say("  OVERTURNED: plan §1.1(a) / §1.2 CLAIM that the 5-site spine is a candidate 'honest cell for the profile' without labels; the spine is STRUCTURAL ONLY.")
        say("  NOT overturned: REDRAW's certification results (C5, the 5-site set as a structural object), CAP-PRUNE, the trunk axis.")
    elif c3 is not None and not c3:
        say("  C3 fails alone (predicted): nothing is overturned; sentence of record 'an anchor-free profile home exists at 5 cells, with less key information than the 14 names'.")
    say("  McNEMAR-ESTABLISHED RULE: wrong(established) applies to the undominated sets in (5) only; no judge direction exists here (both conventions n/a).")
    say("  runtime %.0fs, zero LLM calls, zero builds" % (time.time() - t0))
    summary.update(c2=c2, c3=c3, R_both=R_both, R_model=R_model, p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, p6=p6, p7_any=p7_any, p7_all=p7_all, f1=f1)
    return L, rows_csv, summary


# ----------------------------------------------------------------------------------------------- data of record
def load_record(say, need_f6=True):
    import anchor_free_readout as ar, free_tests_f4_f7 as F, rejudge_grok as rj, rubric_p8 as p8, rubric_512 as r512, stack_judge as sj
    t0 = time.time()
    # gate 1: the Jaccard table of record
    say("--- GATE 1: the five Jaccard assertions from %s (R1 block (d)) ---" % os.path.relpath(REDRAW_OUT, ROOT))
    for l in assert_jaccard(parse_jaccard_table()): say(l)
    # gate 2: R1's nesting
    say("--- GATE 2: R1 %s nesting from dag_snapshots.jsonl (snapshot %s) ---" % (os.path.relpath(R1_DIR, ROOT), R1_SNAPSHOT))
    tree = ar.load_tree(R1_DIR)
    m = tree["manifest"]
    say("  R1 manifest: commit %s, seed %s, split pool %s, train %s / test %s; snapshot iteration %d; nodes %d, leaves %d, slice dim %d"
        % (str(m.get("commit", "?"))[:8], m.get("seed"), m.get("reserved_pool_id"), m.get("train_size"), m.get("test_size"), tree["iteration"], tree["nodes"], len(tree["leaves"]), tree["dim"]))
    if m.get("reserved_pool_id") != POOL:
        raise SystemExit("[R1] manifest split pool %s is not the pool of record %s" % (m.get("reserved_pool_id"), POOL))
    if (tree["nodes"], len(tree["leaves"]), tree["iteration"]) != (PIN["r1_nodes"], PIN["r1_leaves"], PIN["r1_iter"]):
        raise SystemExit("[R1] tree is not the R1 of record: nodes %d leaves %d iteration %d" % (tree["nodes"], len(tree["leaves"]), tree["iteration"]))
    ok, lines, kid2parent = assert_nesting(tree)
    for l in lines: say(l)
    if not ok:
        say("  PARTITION UNDETERMINED: the nesting does not hold on R1; stopping (no ad-hoc re-cut)."); return None
    cell_of = cell_of_leaf_fn(tree, kid2parent)
    leaf_cell = {lid: cell_of(lid) for lid in tree["leaf_ids"]}
    say("  leaves per cell: %s; leaves with no cell (defect): %d" % (dict(Counter(v for v in leaf_cell.values() if v)), sum(1 for v in leaf_cell.values() if v is None)))

    # the corpus and the routing (anchor_free_readout (1), verbatim)
    train, heldout, cs = ar.corpus(POOL)
    heldout_ids = sorted(pool_guard.eval_ids(POOL))
    if len(heldout_ids) != PIN["pool"] or len(heldout) != PIN["pool"]:
        raise SystemExit("[POOL] %d held-out questions, pinned %d" % (len(heldout), PIN["pool"]))
    vec = ar.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    miss = [t for t, _ in train + heldout if t not in vec]
    if miss: raise SystemExit("[EMB] %d corpus texts have no embedding" % len(miss))
    pur = ar.purity(tree, train, heldout, vec)
    say("  corpus: %d mmlu_pro rows, %d distinct texts; held-out %d; train %d distinct texts; flatLeaf purity on R1 %.3f [%.3f, %.3f] (record 0.727)"
        % (cs["rows"], cs["distinct"], len(heldout), len(train), pur["leaf"]["acc"], pur["leaf"]["lo"], pur["leaf"]["hi"]))
    cells_pool = {c: [] for c in CELLS}; defects = Counter()
    anchor_pool = {}
    for q, leaf in zip(heldout_ids, pur["heldout_cell"]["leaf"]):
        c = leaf_cell[leaf]
        if c is None: defects["pool"] += 1
        else: cells_pool[c].append(q)
    train_cells = defaultdict(Counter)
    for leaf, (_, cat) in zip(pur["train_cell"]["leaf"], train):
        c = leaf_cell[leaf]
        if c: train_cells[c][cat] += 1
    train_major = {c: (cnt.most_common(1)[0][0], cnt.most_common(1)[0][1] / sum(cnt.values()), sum(cnt.values())) for c, cnt in train_cells.items()}
    migration = defaultdict(Counter)
    cat_of_pool = {q: cat for q, (_, cat) in zip(heldout_ids, heldout)}
    for c in CELLS:
        for q in cells_pool[c]: migration[cat_of_pool[q]][c] += 1

    # the key
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    models46 = sorted(mm for (mm,) in ev.execute("SELECT DISTINCT model_name FROM eval_results") if mm != EXCLUDE)
    models12 = sorted(p8.ARENA12)
    if len(models46) != PIN["k46"] or len(models12) != PIN["k12"] or not set(models12) <= set(models46):
        raise SystemExit("[ROSTER] K46 %d, K12 %d" % (len(models46), len(models12)))
    pool_set = set(heldout_ids)
    K = defaultdict(dict)
    for q, mm, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if q in pool_set and mm != EXCLUDE: K[q][mm] = int(c or 0)
    ev.close()
    miss12 = sum(1 for q in heldout_ids if any(mm not in K.get(q, {}) for mm in models12))
    miss46 = sum(1 for q in heldout_ids if any(mm not in K.get(q, {}) for mm in models46))
    say("  key: %d pool questions with >= 1 row; %d lack an ARENA12 row, %d lack a K46 row (%s excluded; K12 = %d, K46 = %d models)" % (len(K), miss12, miss46, EXCLUDE, len(models12), len(models46)))

    # the 14 anchors on the same pool (bareq512_s42 primary routing -> depth-1 anchor), in order of first appearance over sorted ids
    route = r512.primary_routing(TREE14)
    nodes = r512.load_graph(r512.snapshot_id(TREE14)); anc = r512.anchor_fn(nodes)
    anchors_pool = defaultdict(list); anchor_of_pool = {}
    for q in heldout_ids:
        if q in route:
            a = anc(route[q]); anchors_pool[a].append(q); anchor_of_pool[q] = a
    if len(anchors_pool) != PIN["anchors"] or sum(len(v) for v in anchors_pool.values()) != PIN["pool"]:
        raise SystemExit("[ANCHORS] %d anchors, %d routed pool questions" % (len(anchors_pool), sum(len(v) for v in anchors_pool.values())))
    say("  14 anchors of %s on the pool: %s" % (TREE14, ", ".join("%s %d" % (a, len(v)) for a, v in anchors_pool.items())))

    # the judged questions (x12 cache of record, mode=ro; never x20 alone)
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12 = sj.cache_path()
    con = sqlite3.connect("file:%s?mode=ro" % x12.replace("\\", "/"), uri=True)
    n12 = con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=0").fetchone()[0]
    judged = sorted({r[0] for r in con.execute("SELECT DISTINCT qid FROM verdicts WHERE invalid=0")})
    con.close()
    if len(judged) != PIN["judged"] or not set(judged) <= pool_set:
        raise SystemExit("[JUDGED] %d judged questions (pinned %d), outside the pool %d" % (len(judged), PIN["judged"], len(set(judged) - pool_set)))
    say("  judged: x12 cache %s, %d valid verdicts, %d judged questions, all in the pool" % (os.path.basename(x12), n12, len(judged)))
    jset = set(judged)
    cells_judged = {c: [q for q in cells_pool[c] if q in jset] for c in CELLS}
    anchors_judged = {a: [q for q in v if q in jset] for a, v in anchors_pool.items()}

    # F6 (the record's instrument on the 10,925 keyed questions) and the 5-cell partition of the keyed set
    f6 = None; cells_keyed_n = {}; keyed_train = 0; n_keyed = 0
    if need_f6:
        keyed = F.keyed_questions(); kmodels, G, kcat, ktext, kqs = keyed
        if len(kqs) != PIN["keyed"] or len(kmodels) != PIN["k46"]:
            raise SystemExit("[F6] %d keyed questions (pinned %d), %d models" % (len(kqs), PIN["keyed"], len(kmodels)))
        blk = ar.f6_block(R1_DIR, keyed)
        qs = list(blk["per_q"].keys()); n_keyed = len(qs)
        # the routing F6 used (recomputed identically, to map leaf -> cell)
        leaves = F.tree_leaves(R1_DIR); dim = len(leaves[0][1])
        kvec = F.embed_matrix(ar.EMB_DB, [ktext[q] for q in qs], dim)
        Q = np.stack([kvec[ktext[q]] for q in qs]); M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
        idx = np.argmax(Q @ M.T, axis=1)
        leaf_p = {q: leaves[i][0] for q, i in zip(qs, idx)}
        cell_p = {q: leaf_cell[leaf_p[q]] for q in qs}
        defects["keyed"] = sum(1 for q in qs if cell_p[q] is None)
        cells_keyed_n = Counter(cell_p[q] for q in qs if cell_p[q])
        keyed_train = sum(1 for q in qs if q not in pool_set)
        ia = F.loo_imp({q: cell_p[q] or "DEFECT" for q in qs}, qs, kmodels, G)
        ic = F.loo_imp({q: kcat[q] for q in qs}, qs, kmodels, G)
        d = ia - ic; dlo, dhi = F.boot_mean_ci(d)
        gate = {k: ("%.3f" % (1000 * blk[src]) == "%.3f" % F6_RECORD[k]) for k, src in (("category", "category"), ("leaf", "leaf"), ("depth1", "anchor"))}
        f6 = dict(n=len(qs), cells=1000 * float(ia.mean()), category=1000 * blk["category"], leaf=1000 * blk["leaf"], depth1=1000 * blk["anchor"], leaves_n=blk["leaves"],
                  diff=1000 * float(d.mean()), diff_lo=1000 * dlo, diff_hi=1000 * dhi, gate=gate)
        if not all(gate.values()):
            raise SystemExit("[F6] the record's (b)/(c)/(d) did not reproduce to 3 dp: %s (got category %.3f leaf %.3f depth-1 %.3f)" % (gate, f6["category"], f6["leaf"], f6["depth1"]))
        # unregistered, descriptive: the same four on the pool of record's keyed questions only (loo_imp admits a subset: qs = the subset, fit = None)
        qp = [q for q in qs if q in pool_set]
        if len(qp) >= 100:
            anc_p = {q: leaves[i][2].lower() for q, i in zip(qs, idx)}
            pa_ = F.loo_imp({q: cell_p[q] or "DEFECT" for q in qs}, qp, kmodels, G); pc_ = F.loo_imp({q: kcat[q] for q in qs}, qp, kmodels, G)
            pl_ = F.loo_imp(leaf_p, qp, kmodels, G); pd_ = F.loo_imp(anc_p, qp, kmodels, G)
            dd = pa_ - pc_; plo, phi = F.boot_mean_ci(dd)
            f6["pool"] = dict(n=len(qp), cells=1000 * float(pa_.mean()), category=1000 * float(pc_.mean()), leaf=1000 * float(pl_.mean()), depth1=1000 * float(pd_.mean()),
                              diff=1000 * float(dd.mean()), diff_lo=1000 * plo, diff_hi=1000 * phi)
        say("  F6: %d keyed questions (%d models); %d are pool ids, %d on R1's train side; record (b)/(c)/(d) reproduced to 3 dp: %s (%.0fs)" % (n_keyed, len(kmodels), len(qp), keyed_train, all(gate.values()), time.time() - t0))
    return dict(tree=tree, cells_pool=cells_pool, cells_judged=cells_judged, cells_keyed_n=dict(cells_keyed_n), anchors_pool=dict(anchors_pool), anchors_judged=anchors_judged,
                anchor_of_pool=anchor_of_pool, K=K, models12=models12, models46=models46, f6=f6, train_major=train_major, migration=migration,
                n_pool=len(heldout_ids), n_judged=len(judged), n_keyed=n_keyed, keyed_train=keyed_train, defects=dict(pool=defects["pool"], judged=sum(1 for q in judged if q not in {x for v in cells_pool.values() for x in v}), keyed=defects["keyed"]))


# ----------------------------------------------------------------------------------------------- modes
def refuse_if_exists(path):
    if os.path.exists(path):
        raise SystemExit("[ONCE] %s exists; the outcome is written once. Refusing." % path)


def header(mode):
    return ["pool of record: %s" % pool_guard.assert_pool_of_record(POOL),
            "=== STABLE-CELL-SET: does the 5-site re-draw-stable certified set, read as a partition on R1 af_clean_s42, carry a key-built profile on the pool of record? ===",
            "  registered 2026-09-19 (commit 7bd1355, docs/judge_v2_program.md L7765-L7924); zero judge calls, zero builds; key only; every DB mode=ro; %s" % mode,
            "  R1 run dir %s (untracked build dir; dag_snapshots.jsonl of record for snapshot %s); the five cells are R1 ids with the record id in brackets; S5 is a COMPLEMENT, never a certified site." % (os.path.relpath(R1_DIR, ROOT), R1_SNAPSHOT),
            ""]


def dry_run():
    L = header("DRY RUN: gates, denominators and supports only; no outcome number")
    print("\n".join(L)); L2 = []
    D = load_record(L2.append, need_f6=False)
    print("\n".join(L2))
    if D is None: return 1
    n_of = {c: len(D["cells_pool"][c]) for c in CELLS}
    print("")
    print("  %-4s %-100s %8s %8s" % ("cell", "definition", "pool", "judged"))
    for c in CELLS:
        print("  %-4s %-100s %8d %8d  %s" % (c, CELL_DESC[c], n_of[c], len(D["cells_judged"][c]), "" if n_of[c] >= FLOOR else "UNDETERMINED-by-support (< %d)" % FLOOR))
    print("  denominators: %d pool of record / %d judged; the keyed denominator (F6, 10,925) is read under --run only" % (D["n_pool"], D["n_judged"]))
    print("  defects (routed leaf with no site ancestor): pool %d" % D["defects"]["pool"])
    print("  majority-train category per cell (description only): %s" % {c: "%s %.3f (n %d)" % v for c, v in D["train_major"].items()})
    print("  outputs on --run (written once): %s, %s" % (OUT_TXT, OUT_CSV))
    print("  existing outcome file: %s" % ("YES (--run will refuse)" if os.path.exists(OUT_TXT) else "no"))
    print("  DRY-RUN READY (gates 1 and 2 passed; C1 by support %s)" % ("would HOLD" if all(n_of[c] >= FLOOR for c in CELLS) else "would FAIL"))
    return 0


def run():
    L = header("RUN")
    print("\n".join(L), flush=True)
    refuse_if_exists(OUT_TXT)
    D = load_record(lambda s: (L.append(s), print(s, flush=True)), need_f6=True)
    if D is None:
        L.append("  PARTITION UNDETERMINED; nothing written.")
        print("\n".join(L)); return 1
    body, rows, summary = analyse(D, [], log=lambda s: print(s, flush=True))
    L.extend(body)
    txt = "\n".join(L)
    print(txt)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_TXT, "w", encoding="utf-8", newline="\n") as f: f.write(txt + "\n")
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print("wrote %s and %s" % (OUT_TXT, OUT_CSV))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    """Synthetic: a 5-cell table with planted (model x cell) interaction, one cell planted BELOW the 120 floor (C1 must FAIL,
    its row UNDETERMINED-by-support), a nesting assertion on a fake tree that breaks it, a perturbed Jaccard table, the
    undominated-set rule on a planted dominance, and write-once. Nothing of record is opened."""
    print("pool of record (NOT opened by --selftest): %s" % POOL)
    print("=== STABLE-CELL-SET --selftest (synthetic) ===")
    rng = random.Random(3); rs = np.random.RandomState(3)
    models12 = ["m%02d" % i for i in range(12)]; models46 = models12 + ["x%02d" % i for i in range(34)]
    abil = {m: rng.gauss(0, 0.9) for m in models46}
    sizes = {"S1": 300, "S2": 400, "S3": 350, "S4": 90, "S5": 900}          # S4 planted below the floor
    inter = {(m, c): rng.gauss(0, 0.7) for m in models46 for c in CELLS}
    diff = {"S1": 0.3, "S2": -0.2, "S3": 0.0, "S4": 0.5, "S5": -0.4}
    K = {}; cells = {}; qid = 1
    for c in CELLS:
        cells[c] = []
        for _ in range(sizes[c]):
            K[qid] = {m: int(rs.rand() < 1 / (1 + math.exp(-(abil[m] + inter[(m, c)] - diff[c])))) for m in models46}
            cells[c].append(qid); qid += 1
    # a planted dominance: m11 beats everyone in S1 (its rows set to 1 on 95% of S1)
    for q in cells["S1"]:
        K[q]["m11"] = int(rs.rand() < 0.995)
    anchors = {"A%d" % i: [] for i in range(14)}
    anchor_of = {}
    for c in CELLS:
        for q in cells[c]:
            a = "A%d" % rng.randrange(14); anchors[a].append(q); anchor_of[q] = a
    D = dict(cells_pool=cells, cells_judged={c: v[: len(v) // 2] for c, v in cells.items()}, cells_keyed_n={c: 3 * len(v) for c, v in cells.items()},
             anchors_pool=anchors, anchors_judged={a: v[: len(v) // 2] for a, v in anchors.items()}, anchor_of_pool=anchor_of, K=K, models12=models12, models46=models46,
             f6=dict(n=1000, cells=9.5, category=10.791, leaf=12.785, depth1=3.604, leaves_n=82, diff=-1.29, diff_lo=-2.0, diff_hi=-0.5, gate=dict(category=True, leaf=True, depth1=True)),
             train_major={c: ("cat%s" % c, 0.3, 100) for c in CELLS}, migration={"catA": Counter({c: 10 for c in CELLS})},
             n_pool=sum(sizes.values()), n_judged=sum(sizes.values()) // 2, n_keyed=3 * sum(sizes.values()), keyed_train=2 * sum(sizes.values()), defects=dict(pool=0, judged=0, keyed=0))
    L, rows, S = analyse(D, [], log=lambda s: print("  " + s, flush=True))
    print("\n".join(L))
    fails = []
    if S["c1"]: fails.append("C1 should FAIL with a planted 90-question cell")
    if S["under"] != ["S4"]: fails.append("under-floor cells should be ['S4'], got %s" % S["under"])
    if S["cls"][("K12", "S4")]["cls"] != "UNDETERMINED-by-support": fails.append("S4 class should be UNDETERMINED-by-support, got %s" % S["cls"][("K12", "S4")]["cls"])
    if not (S["R_both"] > 0.85): fails.append("planted interaction should read interaction-only R > 0.85, got %.4f" % S["R_both"])
    if not S["f1"]: fails.append("falsifier should FIRE when C1 fails")
    if S["p3"] is not True: fails.append("P3 should HOLD on the planted F6 (9.5 in [8, 11], C3 fails)")
    if "m11" not in S["U"]["S1"] or len(S["U"]["S1"]) != 1: fails.append("planted dominance: U(S1) should be ['m11'], got %s" % S["U"]["S1"])
    # nesting assertion on a fake tree that breaks it
    fake = dict(byid={"n00000001": dict(id="n00000001", depth=0, label="root", childIds=["n00000004", "n00000005"]),
                      "n00000004": dict(id="n00000004", depth=1, label="q", childIds=[]),
                      "n00000005": dict(id="n00000005", depth=1, label="d", childIds=["n00000017"]),
                      "n00000017": dict(id="n00000017", depth=2, label="a", childIds=["n00000042"]),
                      "n00000018": dict(id="n00000018", depth=2, label="b", childIds=[]),      # detached: nesting broken
                      "n00000042": dict(id="n00000042", depth=3, label="c", childIds=[])})
    ok, lines, _ = assert_nesting(fake)
    if ok: fails.append("nesting assertion accepted a tree where n00000018 is not under n00000005")
    else: print("  nesting guard: refused the broken tree -> " + lines[0].strip())
    fake["byid"]["n00000005"]["childIds"].append("n00000018")
    ok2, _, k2p = assert_nesting(fake)
    if not ok2: fails.append("nesting assertion refused the correct nesting")
    cof = cell_of_leaf_fn(fake, k2p)
    if [cof(x) for x in ("n00000042", "n00000018", "n00000004")] != ["S1", "S3", "S5"]: fails.append("cell_of_leaf mapping wrong")
    # Jaccard assertion: the real table must pass the parse (file read only, no DB); a perturbed copy must be refused
    tab = parse_jaccard_table()
    try:
        assert_jaccard(tab)
    except SystemExit as e:
        fails.append("Jaccard assertion failed on the table of record: %s" % e)
    bad = dict(tab); bad["n00000032"] = ("n00000042", 0.700, "reproduces")
    try:
        assert_jaccard(bad); fails.append("Jaccard assertion accepted a perturbed value")
    except SystemExit:
        print("  Jaccard guard: refused a perturbed table (0.700 for n00000032)")
    bad2 = dict(tab); bad2["n00000016"] = ("n00000017", 0.937, "reproduces")
    try:
        assert_jaccard(bad2); fails.append("Jaccard assertion accepted a wrong arm id")
    except SystemExit:
        print("  Jaccard guard: refused a wrong arm id (n00000016 -> n00000017)")
    # write-once (no DB: the ONCE guard alone)
    scratch = os.path.join(os.environ.get("LOCALAPPDATA", ROOT), "Temp", "claude", "stable_cell_set_selftest")
    os.makedirs(scratch, exist_ok=True); tmp = os.path.join(scratch, "outcome.txt"); open(tmp, "w").write("x\n")
    try:
        refuse_if_exists(tmp); fails.append("write-once did not refuse")
    except SystemExit:
        print("  write-once: refused an existing outcome file")
    finally:
        os.remove(tmp)
    print("")
    if fails:
        print("SELFTEST FAILED:"); [print("  - " + f) for f in fails]; return 1
    print("SELFTEST OK: the planted floor cell is UNDETERMINED-by-support and fails C1 (falsifier fires), the planted interaction reads R > 0.85, the planted")
    print("             dominance gives U = ['m11'], the nesting guard refuses a detached site, the Jaccard guard refuses a perturbed value and a wrong id, write-once refuses.")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="STABLE-CELL-SET (zero calls, zero builds)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true"); g.add_argument("--selftest", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest: return selftest()
    if a.dry_run: return dry_run()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
