# INTENDED to generate the granularity-flatness figure (between-cell Spearman
# rho of ground-truth model rankings at 14 / 88 / 87 / 152 cells, pilot
# 8-model roster, construction-assignment convention) for the thesis.
#
# STATUS: DOES NOT EMIT A PDF. The verification-before-plot rule is absolute,
# and one published number cannot be reproduced under any single convention
# this script (or the repository) can name: the centred-residual median
# quartet (-0.119, -0.024, -0.024, -0.024). See VERIFICATION NOTE below. The
# script recomputes everything, prints what does and does not reproduce, and
# exits non-zero before any drawing happens.
#
# WHAT REPRODUCES EXACTLY (observed rho, tab:granularity / the prereg table):
#     14 domains  : 14 cells,   91 pairs, median 0.929
#     88 leaves   : 88 cells, 3828 pairs, median 0.922   (biased router)
#     87 leaves   : 87 cells, 3741 pairs, median 0.922   (corrected router)
#     152 leaves  : 152 cells, 11476 pairs, median 0.905 (finer, mcs=30)
#   from: eval_results (mmlu_pro_dataset_cache_v2.db) joined to the corpus by
#   question TEXT via queries.raw_text (embeddings_cache.db) -- never by id,
#   the id spaces differ -- and the snapshot trees in snapshots.db
#   (20260726_040331 = 88 leaves, 20260727_042523 = 87 leaves frozen,
#   20260727_031535 = 152 leaves), leaf membership = the snapshot's own
#   construction assignments (node queryIds), 0 cells dropped, all 8 roster
#   models present in every cell.
#
# VERIFICATION NOTE (why no figure): the published centred-residual medians
# are -0.119 / -0.024 / -0.024 / -0.024. Under the convention the text
# describes ("centring out each model's global mean") this script obtains
# +0.048 / -0.024 / -0.024 / -0.024 -- the 14-domain row disagrees. Under a
# per-model z-score across cells it obtains -0.119 / -0.024 / -0.024 / 0.000
# -- the 152-cell row disagrees (its median falls inside a run of exactly-0
# pair correlations, 23 pairs away from -0.024). No convention that
# reproduces all four observed medians also reproduces all four centred
# medians; the one-off script that produced the prereg table is not in the
# repository. Until the centred convention is pinned down, panel (b) cannot
# be certified, so the figure is not produced.
#
# Run from anywhere:  python report/Figures/make_granularity_flat.py
import json
import math
import os
import sqlite3
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "granularity_flat.pdf")
EVAL_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
QUERIES_DB = os.path.join(ROOT, "embeddings_cache.db")
SNAP_DB = os.path.join(ROOT, "snapshots.db")

ROSTER = ["Llama-2-13b-hf", "Llama-2-70b-hf", "Meta-Llama-3_1-70B-Instruct",
          "Qwen1.5-72B-Chat", "claude-3-5-haiku-20241022",
          "claude-3-5-sonnet-20241022", "deepseek-chat-v2_5",
          "gpt-4o-2024-08-06"]
RSET = set(ROSTER)

SNAPS = [
    ("88 leaves (biased router)", "20260726_040331_Headless_Run_Auto_ge"),
    ("87 leaves (corrected router)", "20260727_042523_Headless_Run_Auto_ge"),
    ("152 leaves (finer, mcs=30)", "20260727_031535_Headless_Run_Auto_ge"),
]

# Published values this script MUST reproduce before plotting.
PUB_OBSERVED = [("14 domains", 14, 91, 0.929),
                ("88 leaves", 88, 3828, 0.922),
                ("87 leaves", 87, 3741, 0.922),
                ("152 leaves", 152, 11476, 0.905)]
PUB_CENTRED = [-0.119, -0.024, -0.024, -0.024]


def spearman(a, b, keys):
    """Spearman rho over `keys`, average ranks for ties."""
    def rk(d):
        vs = sorted(keys, key=lambda k: d[k]); r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]: j += 1
            for k in range(i, j + 1): r[vs[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    n = len(keys)
    ra, rb = rk(a), rk(b)
    ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    nu = sum((ra[k] - ma) * (rb[k] - mb) for k in keys)
    da = math.sqrt(sum((ra[k] - ma) ** 2 for k in keys))
    db = math.sqrt(sum((rb[k] - mb) ** 2 for k in keys))
    return nu / (da * db) if da and db else None


# ------------------------------------------------------------------ load data
E = sqlite3.connect(QUERIES_DB)
qtext = {qid: txt for qid, txt in E.execute("select id, raw_text from queries")}
E.close()

D = sqlite3.connect(EVAL_DB)
rec = defaultdict(dict); cat = {}
norm = {}
for t, m, ic, c in D.execute(
        "select question_text, model_name, is_correct, category from eval_results"):
    rec[t][m] = ic; cat[t] = c
    norm[t.strip()] = t
D.close()


def resolve(t):
    """Exact text join, with a whitespace-normalised fallback (one corpus
    query carries a trailing space; the prereg's 11769/11769 join implies the
    original resolved it too -- the result is identical either way)."""
    return t if t in rec else norm.get(t.strip())


joined = sum(1 for t in qtext.values() if resolve(t))
print(f"text join queries.raw_text -> eval_results.question_text: "
      f"{joined}/{len(qtext)}")
assert joined == len(qtext) == 11769, "join must be exact, 11769/11769"

S = sqlite3.connect(SNAP_DB)


def covered(texts):
    out = []
    for t in texts:
        rt = resolve(t)
        if rt and RSET <= rec[rt].keys():
            out.append(rt)
    return out


partitions = []  # (label, {cell -> [texts]})
corpus = set(covered(qtext.values()))
c14 = defaultdict(list)
for t in corpus:
    c14[cat[t]].append(t)
partitions.append(("14 domains", dict(c14)))

for label, sid in SNAPS:
    graph_json, = S.execute(
        "select graph from snapshots where id = ?", (sid,)).fetchone()
    g = json.loads(graph_json)
    cells = {}
    for n in g["nodes"]:
        if n.get("childIds"):
            continue
        cells[n["id"]] = covered(qtext[q] for q in n["queryIds"]
                                 if q in qtext)
    partitions.append((label.split(" (")[0], cells))
S.close()

# --------------------------------------------------- observed rho + residuals
obs_dists, cen_pooled, cen_zscore = [], [], []
for label, cells in partitions:
    A = {k: {m: sum(rec[t][m] for t in ts) / len(ts) for m in ROSTER}
         for k, ts in cells.items()}
    ks = sorted(A); C = len(ks)
    pop = [t for ts in cells.values() for t in ts]
    gpool = {m: sum(rec[t][m] for t in pop) / len(pop) for m in ROSTER}
    mu = {m: sum(A[k][m] for k in ks) / C for m in ROSTER}
    sd = {m: math.sqrt(sum((A[k][m] - mu[m]) ** 2 for k in ks) / C)
          for m in ROSTER}
    P = {k: {m: A[k][m] - gpool[m] for m in ROSTER} for k in ks}
    Z = {k: {m: (A[k][m] - mu[m]) / sd[m] for m in ROSTER} for k in ks}
    rhos, cp, cz = [], [], []
    for i in range(C):
        for j in range(i + 1, C):
            rhos.append(spearman(A[ks[i]], A[ks[j]], ROSTER))
            cp.append(spearman(P[ks[i]], P[ks[j]], ROSTER))
            cz.append(spearman(Z[ks[i]], Z[ks[j]], ROSTER))
    obs_dists.append((label, C, rhos))
    cen_pooled.append(cp)
    cen_zscore.append(cz)

# ------------------------------------------------- verify observed (this holds)
print("\nobserved between-cell Spearman rho (must match tab:granularity):")
for (label, C, rhos), (plabel, pC, ppairs, pmed) in zip(obs_dists, PUB_OBSERVED):
    med = statistics.median(rhos)
    print(f"  {label:<12} cells={C:>4} pairs={len(rhos):>6} median={med:.3f} "
          f"(published {pmed:.3f})")
    assert C == pC, f"{label}: {C} cells != published {pC}"
    assert len(rhos) == ppairs, f"{label}: {len(rhos)} pairs != {ppairs}"
    assert round(med, 3) == pmed, f"{label}: median {med:.3f} != {pmed}"
print("  -> all four observed rows reproduce exactly.")

# --------------------------------- verify centred residuals (this DOES NOT)
print("\ncentred-residual medians, published: "
      + " / ".join(f"{v:+.3f}" for v in PUB_CENTRED))
med_pooled = [round(statistics.median(v), 3) for v in cen_pooled]
med_zscore = [round(statistics.median(v), 3) for v in cen_zscore]
print("  convention A (subtract each model's global-mean accuracy):  "
      + " / ".join(f"{v:+.3f}" for v in med_pooled))
print("  convention B (per-model z-score across cells):              "
      + " / ".join(f"{v:+.3f}" for v in med_zscore))
mech_null = [-1 / (C - 1) for _, C, _ in obs_dists]
print("  mechanical null -1/(C-1):                                   "
      + " / ".join(f"{v:+.4f}" for v in mech_null))

ok_a = med_pooled == PUB_CENTRED
ok_b = med_zscore == PUB_CENTRED
if not (ok_a or ok_b):
    if os.path.exists(OUT):
        os.remove(OUT)
        print(f"\nremoved stale {OUT}")
    sys.exit(
        "\nVERIFICATION FAILED -- figure NOT produced.\n"
        "The published centred-residual quartet (-0.119, -0.024, -0.024, "
        "-0.024) is not\nreproduced by either convention above: A matches "
        "the three leaf rows but gives\n+0.048 at 14 domains; B matches the "
        "first three rows but gives 0.000 at 152\ncells. All four OBSERVED "
        "medians reproduce exactly, so the data and trees are\nright; the "
        "centring convention of the original (untracked) analysis script "
        "is\nnot recoverable from the repository. Pin the convention down, "
        "update the\nPUB_CENTRED check, and re-run to produce the figure.")

# ------------------------------------------------------------------- plot
# (reached only when every published number above reproduces)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE = "#2a78d6"; ORANGE = "#eb6834"
INK = "#0b0b0b"; MUTED = "#898781"; GRID = "#e1e0d9"; BASELINE = "#c3c2b7"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman",
                   "DejaVu Serif"],
    "font.size": 9, "pdf.fonttype": 42, "text.color": INK,
    "axes.edgecolor": BASELINE, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
})

cen_dists = cen_pooled if ok_a else cen_zscore
fig, (axa, axb) = plt.subplots(1, 2, figsize=(5.9, 3.1),
                               gridspec_kw={"wspace": 0.28})
labels = [f"{C} cells" for _, C, _ in obs_dists]
for ax in (axa, axb):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)

bp = axa.boxplot([r for _, _, r in obs_dists], widths=0.55, whis=(5, 95),
                 showfliers=False, patch_artist=True,
                 medianprops=dict(color=INK, lw=1.2),
                 boxprops=dict(facecolor="#cde2fb", edgecolor=BLUE, lw=1.0),
                 whiskerprops=dict(color=BLUE, lw=1.0),
                 capprops=dict(color=BLUE, lw=1.0))
axa.set_xticklabels(labels, fontsize=8)
axa.set_ylabel("between-cell Spearman $\\rho$")
axa.set_title("(a)  observed", fontsize=9, loc="left", pad=8)
axa.annotate("router control", xy=(2.5, 0.80), ha="center", fontsize=7.5,
             color=MUTED)
axb.axhline(0, color=BASELINE, lw=0.8)
axb.boxplot(cen_dists, widths=0.55, whis=(5, 95), showfliers=False,
            patch_artist=True, medianprops=dict(color=INK, lw=1.2),
            boxprops=dict(facecolor="#f9ddd2", edgecolor=ORANGE, lw=1.0),
            whiskerprops=dict(color=ORANGE, lw=1.0),
            capprops=dict(color=ORANGE, lw=1.0))
for i, nul in enumerate(mech_null):
    axb.plot([i + 0.7, i + 1.3], [nul, nul], color=INK, lw=1.0,
             ls=(0, (4, 3)))
axb.set_xticklabels(labels, fontsize=8)
axb.set_title("(b)  centred residuals", fontsize=9, loc="left", pad=8)
fig.tight_layout(pad=0.4)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
