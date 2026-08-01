# How far outside its induction pool is each rubric asked to work, and does that
# distance change anything the judge does?
#
# CLAIM, two halves, one figure.
# (a) The premise of the rubric-blindness worry is real. Measured as cosine
#     distance to the centroid of the queries the rubric was induced from, a
#     held-out question routed into a cell sits at 0.511, against 0.353 for a
#     construction query deliberately held out of the centroid fit and 0.607 for
#     a reserved question drawn at random. Routing closes 38% of the gap between
#     chance and construction-grade proximity, and only 6-21% in five domains.
# (b) The consequence does not appear. Within cells, a one-standard-deviation
#     increase in that distance moves the rubric arm's tie rate by +1.02 pp
#     (95% CI -0.23 to +2.26) -- and moves the GENERIC arm, which has no domain
#     criteria at all, by +1.06 pp. The within-triple difference between the two
#     arms is -0.04 pp (95% CI -1.39 to +1.30). Whatever distance does to the
#     judge, it does it with or without a rubric.
#
# REAL DATA ONLY. Everything is recomputed from the frozen snapshot, the taxonomy
# query store, the embedding cache, the eval cache and the eight r8 ratings
# databases. Every published value is asserted before any drawing happens; on
# mismatch the script raises and emits no PDF.
#
# Method notes that belong in the caption, not in a footnote:
#   - Distance is 1 - cos on the 256-dimensional MRL prefix (the slice the
#     taxonomy itself routes on, sliceDim = 256 in the snapshot), against the
#     mean direction of the cell's induction pool.
#   - The induction pool is reconstructed exactly as TaxonomyJudgeService builds
#     it: the cell's region queries, minus the ~20% dropped by the
#     abs(hashCode) % 5 == 0 thinner, minus every text in the reserved split.
#   - "construction, held out of the fit" is a 50/50 split of the induction pool
#     repeated 60 times: centroid from one half, distance measured on the other.
#     It separates a genuine distribution difference from centroid overfitting.
#   - Panel (b) is a linear probability model with cell fixed effects over the
#     2,788 shared key-decidable comparisons, conventional OLS standard errors.
#
# Run from anywhere:  python report/Figures/make_rubric_reach.py
import json
import math
import os
import sqlite3

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "rubric_reach.pdf")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
DOMS = ["math", "physics", "law", "engineering",
        "psychology", "philosophy", "history", "cs"]
PRETTY = {"cs": "computer sci."}
SLICE = 256
SEED = 20260731

def ro(name):
    return sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, name).replace("\\", "/"),
                           uri=True)

INT32 = 0xFFFFFFFF
def jhash(s):
    """java.lang.String.hashCode -- the thinner in TaxonomyJudgeService keys on it."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & INT32
    return h - 0x100000000 if h >= 0x80000000 else h

# ------------------------------------------------------------------ recompute
db = ro("snapshots.db")
graph, = db.execute("select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
db.close()
g = json.loads(graph)
leaves = {n["id"]: n for n in g["nodes"] if not n.get("childIds")}
assert {n.get("sliceDim") for n in leaves.values()} == {SLICE}, "sliceDim is not 256"

ec = ro("embeddings_cache.db")
qtext = {i: t for i, t in ec.execute("select id, raw_text from queries")}
emb = {t: np.frombuffer(b, dtype=">f4")
       for t, b in ec.execute("select query, vector from embeddings")}
ec.close()

def unit(t):
    v = emb.get(t)
    if v is None:
        return None
    v = np.asarray(v[:SLICE], np.float64)
    n = np.linalg.norm(v)
    return v / n if n > 0 else None

cc = ro("mmlu_pro_dataset_cache_v2.db")
reserved = {t for (t,) in cc.execute(
    "select distinct question_text from eval_results where is_reserved = 1")}
qid2txt = {str(q): t for q, t in cc.execute(
    "select distinct question_id, question_text from eval_results")}

# the induction pool of every leaf, exactly as the service builds it
mu, pack = {}, {}
for lid, n in leaves.items():
    ts = [qtext[q] for q in n["queryIds"] if q in qtext]
    ts = [t for t in ts if abs(jhash(t)) % 5 != 0 and t not in reserved]
    V = [unit(t) for t in ts]
    V = [v for v in V if v is not None]
    if len(V) < 3:
        continue
    M = np.stack(V)
    m = M.mean(0)
    mu[lid], pack[lid] = m / np.linalg.norm(m), M

rows = []
for d in DOMS:
    r = ro("experiment_results/r8/%s/ratings_r8_%s.db" % (d, d))
    rows += [(d,) + tuple(x) for x in r.execute(
        "select node_id, eval_question_id, model_a, model_b, winner, is_tie, condition "
        "from match_history")]
    r.close()

allq = sorted({r[2] for r in rows})
allm = sorted({m for r in rows for m in (r[3], r[4])})
corr = {}
ph = ",".join("?" * len(allm))
for i in range(0, len(allq), 500):
    ch = allq[i:i + 500]
    for q, m, ok in cc.execute(
            "select question_id, model_name, is_correct from eval_results "
            "where model_name in (%s) and question_id in (%s)"
            % (ph, ",".join("?" * len(ch))), allm + ch):
        corr[(str(q), m)] = bool(ok)
cc.close()

# ------------------------------------------------ panel (a): the proximity ladder
routed = {}
for dom, nid, q, a, b, w, t, cond in rows:
    if cond == "MAIN":
        routed.setdefault(nid, (dom, set()))[1].add(str(q))

resv_vecs = []
for _, qs in routed.values():
    for q in qs:
        v = unit(qid2txt.get(q, ""))
        if v is not None:
            resv_vecs.append(v)
RV = np.stack(resv_vecs)

rng = np.random.default_rng(SEED)
ladder = []
for lid, (dom, qs) in routed.items():
    if lid not in mu:
        continue
    M, m = pack[lid], mu[lid]
    s = M.sum(0)
    d_in = float(np.mean([1.0 - v @ ((s - v) / np.linalg.norm(s - v)) for v in M]))
    hh = []
    for _ in range(60):
        idx = rng.permutation(len(M))
        h = len(M) // 2
        cA = M[idx[:h]].mean(0)
        cA /= np.linalg.norm(cA)
        hh.append(float(np.mean(1.0 - M[idx[h:]] @ cA)))
    dv = [1.0 - float(v @ m) for v in (unit(qid2txt.get(q, "")) for q in qs) if v is not None]
    if not dv:
        continue
    ladder.append(dict(dom=dom, d_in=d_in, d_held=float(np.mean(hh)),
                       d_rout=float(np.mean(dv)), d_chance=float(np.mean(1.0 - RV @ m))))

def agg(key, sub=None):
    v = [r[key] for r in ladder if sub is None or r["dom"] == sub]
    return float(np.mean(v))

closes = lambda sub=None: ((agg("d_chance", sub) - agg("d_rout", sub))
                           / (agg("d_chance", sub) - agg("d_held", sub)))

# ------------------------------------------------ panel (b): the fixed-effects null
A = {}
for dom, nid, q, a, b, w, t, cond in rows:
    A.setdefault((dom, nid, str(q), a, b), {})[cond] = (w, bool(t))

rec = []
for (dom, nid, q, a, b), d in A.items():
    if "MAIN" not in d or "C5" not in d or nid not in mu:
        continue
    ca, cb = corr.get((q, a)), corr.get((q, b))
    if ca is None or cb is None or ca == cb:
        continue
    v = unit(qid2txt.get(q, ""))
    if v is None:
        continue
    gw = a if ca else b
    wm, tm = d["MAIN"]
    wc, tc = d["C5"]
    rec.append((nid, 1.0 - float(v @ mu[nid]), int(tm), int(tc),
                int((not tm) and wm == gw), int((not tc) and wc == gw)))

cell = np.array([r[0] for r in rec])
dist = np.array([r[1] for r in rec])
mtie, ctie, mok, cok = (np.array([r[i] for r in rec], float) for i in (2, 3, 4, 5))

def demean(x, gp):
    o = np.empty(len(x), float)
    for v in np.unique(gp):
        k = gp == v
        o[k] = x[k] - x[k].mean()
    return o

xd = demean(dist, cell)
sd = xd.std(ddof=0)
dfree = len(xd) - len(np.unique(cell)) - 1

def effect(y):
    yd = demean(y, cell)
    b = float(np.sum(xd * yd) / np.sum(xd ** 2))
    se = math.sqrt(float(np.sum((yd - b * xd) ** 2)) / dfree / float(np.sum(xd ** 2)))
    return 100 * b * sd, 100 * (b - 1.96 * se) * sd, 100 * (b + 1.96 * se) * sd

EFF = [("rubric arm", effect(mtie)),
       ("generic arm", effect(ctie)),
       ("difference", effect(mtie - ctie)),
       ("rubric arm", effect(mok)),
       ("generic arm", effect(cok)),
       ("difference", effect(mok - cok))]

# ---------------------------------------------------------------- verification
assert len(ladder) == 52, "cells with geometry %d != published 52" % len(ladder)
assert len(rec) == 2788, "shared key-decidable comparisons %d != published 2788" % len(rec)
for nm, val, exp in (("d_in", agg("d_in"), 0.3443), ("d_held", agg("d_held"), 0.3534),
                     ("d_routed", agg("d_rout"), 0.5113), ("d_chance", agg("d_chance"), 0.6070)):
    assert abs(val - exp) < 1e-3, "%s %.4f != published %.4f" % (nm, val, exp)
assert abs(closes() - 0.377) < 5e-3, "gap closed %.3f != published 0.377" % closes()
assert abs(sd - 0.1140) < 5e-4, "within-cell SD of distance %.4f != published 0.1140" % sd
for (nm, (b, lo, hi)), exp in zip(EFF, (1.016, 1.060, -0.044, -1.730, -1.624, -0.106)):
    assert abs(b - exp) < 0.02, "%s effect %+.3f != published %+.3f" % (nm, b, exp)
assert closes("law") > 1.0 > closes("engineering"), "domain ordering of gap-closing changed"

print("VERIFIED against published values:")
print("  %d cells, %d shared key-decidable comparisons" % (len(ladder), len(rec)))
print("  distance to the induction-pool centroid:")
print("    construction, in-sample (LOO)     %.4f" % agg("d_in"))
print("    construction, held out of the fit %.4f" % agg("d_held"))
print("    held-out, routed here             %.4f" % agg("d_rout"))
print("    held-out, drawn at random         %.4f" % agg("d_chance"))
print("    routing closes %.0f%% of the chance-to-construction gap" % (100 * closes()))
for d in DOMS:
    print("      %-12s held %.4f  routed %.4f  chance %.4f  closes %3.0f%%"
          % (d, agg("d_held", d), agg("d_rout", d), agg("d_chance", d), 100 * closes(d)))
print("  effect of +1 SD (%.4f) of within-cell distance, percentage points:" % sd)
for nm, (b, lo, hi) in EFF:
    print("    %-28s %+6.2f  [%+.2f, %+.2f]" % (nm, b, lo, hi))

# ---------------------------------------------------------------------- plot
# GREYSCALE ONLY -- the thesis prints in monochrome.
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 9, "pdf.fonttype": 42,
})

fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.1, 3.6),
                               gridspec_kw=dict(width_ratios=[1.12, 1.0]))

# ---- (a) the ladder
order = sorted(DOMS, key=lambda d: -closes(d))
axL.set_axisbelow(True)
axL.grid(axis="x", color="0.91", lw=0.6)
for sp in ("top", "right", "left"):
    axL.spines[sp].set_visible(False)

for i, d in enumerate(order):
    lo, hi, r = agg("d_held", d), agg("d_chance", d), agg("d_rout", d)
    axL.plot([lo, hi], [i, i], color="0.62", lw=1.4, solid_capstyle="butt", zorder=2)
    axL.plot([lo], [i], marker="|", ms=8, mec="black", mew=1.2, zorder=4)
    axL.plot([hi], [i], marker="|", ms=8, mec="0.55", mew=1.2, zorder=4)
    axL.plot([r], [i], marker="o", ms=6.0, mfc="black", mec="white", mew=0.9, zorder=5)

axL.set_yticks(range(len(order)))
axL.set_yticklabels([PRETTY.get(d, d) for d in order])
axL.set_ylim(-0.9, len(order) - 0.4)
axL.invert_yaxis()
axL.set_xlim(0.27, 0.70)
axL.set_xlabel("cosine distance to the rubric's induction pool")
axL.tick_params(length=0)
axL.annotate("construction-\ngrade", xy=(agg("d_held"), -0.82), ha="center", va="bottom",
             fontsize=7.6, color="0.25", linespacing=1.3)
axL.annotate("a random\nheld-out question", xy=(agg("d_chance"), -0.82), ha="center",
             va="bottom", fontsize=7.6, color="0.25", linespacing=1.3)
axL.set_title("(a) the rubric is applied well outside the\nmaterial it was induced from"
              "\n$\\bullet$ = where routing actually puts the judged question",
              fontsize=8.6, loc="left", pad=24, linespacing=1.5)

# ---- (b) the null
axR.set_axisbelow(True)
axR.grid(axis="x", color="0.91", lw=0.6)
for sp in ("top", "right", "left"):
    axR.spines[sp].set_visible(False)
axR.axvline(0, color="black", lw=0.9, zorder=3)

ypos, labels = [], []
slot = 0
for k, (nm, (b, lo, hi)) in enumerate(EFF):
    if k == 3:
        slot += 0.9
    ypos.append(slot)
    labels.append(nm)
    isdiff = nm == "difference"
    if isdiff:
        # the difference row carries the claim: shaded band + heavier rule
        axR.axhspan(slot - 0.34, slot + 0.34, color="0.94", zorder=1)
    axR.plot([lo, hi], [slot, slot], color="0.45" if not isdiff else "black",
             lw=1.1 if not isdiff else 1.7, solid_capstyle="butt", zorder=4)
    axR.plot([b], [slot], marker="s" if isdiff else "o", ms=5.8 if isdiff else 5.0,
             mfc="black" if isdiff else "white", mec="black", mew=1.0, zorder=5)
    slot += 1

axR.set_yticks(ypos)
axR.set_yticklabels(labels, fontsize=8)
axR.set_ylim(-1.0, slot - 0.2)
axR.invert_yaxis()
axR.set_xlim(-4.2, 3.2)
axR.set_xlabel("change per +1 SD of distance (pp)")
axR.tick_params(length=0)
axR.annotate("tie rate", xy=(0.02, -0.88), xycoords=("axes fraction", "data"),
             ha="left", va="center", fontsize=8, style="italic", color="0.30",
             bbox=dict(fc="white", ec="none", pad=1.0), zorder=6)
axR.annotate("agreement with the key", xy=(0.02, 2.58),
             xycoords=("axes fraction", "data"),
             ha="left", va="center", fontsize=8, style="italic", color="0.30",
             bbox=dict(fc="white", ec="none", pad=1.0), zorder=6)
axR.set_title("(b) but distance moves the arm with no\nrubric as much as the arm with one"
              "\n95% CI, cell fixed effects, n = 2,788",
              fontsize=8.6, loc="left", pad=24, linespacing=1.5)

fig.subplots_adjust(left=0.135, right=0.985, top=0.735, bottom=0.135, wspace=0.42)
fig.savefig(OUT)
print("wrote", OUT)
