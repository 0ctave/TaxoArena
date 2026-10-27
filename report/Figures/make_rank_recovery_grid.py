# Generates the rank-recovery grid (V-5 of the figure review): 8 models x 8
# domains, signed displacement of each model's arena rank from its key rank.
#
# The claim: a mostly-white grid IS the result -- one shared ordering,
# recovered eight times. Cells where the model sits in at least one
# key-undecidable pair in that domain carry a small open marker: there the
# key itself does not fully constrain the model's position against its
# neighbours.
#
# REAL DATA ONLY. Published facts asserted before drawing: 64 cells;
# displacements sum to zero per domain; sum of squared displacements per
# domain reproduces the published Spearman rho of tab:settled-recovery
# exactly (rho = 1 - 6*S/504 at M=8); |displacement| never exceeds 2.
#
# Run from anywhere:  python report/Figures/make_rank_recovery_grid.py
import math
import os
import sqlite3
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "rank_recovery_grid.pdf")
CACHE = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
DOMS = [("math", "math."), ("physics", "phys."), ("law", "law"),
        ("engineering", "eng."), ("psychology", "psych."),
        ("philosophy", "phil."), ("history", "hist."), ("cs", "cs")]
SHORT = {
    "gemini-3.1-pro_5-shots": "gemini-3.1-pro (5-shot)",
    "arx_0314": "arx_0314",
    "gpt-4o-2024-08-06": "gpt-4o",
    "Meta-Llama-3_1-70B-Instruct": "Llama-3.1-70B-Inst",
    "Qwen1.5-72B-Chat": "Qwen1.5-72B-Chat",
    "Meta-Llama-3_1-8B": "Llama-3.1-8B",
    "Yi-6b-Chat": "Yi-6B-Chat",
    "Llama-2-7b-hf": "Llama-2-7B (base)",
}


def bt(models, wins, it=900):
    idx = {m: i for i, m in enumerate(models)}
    K = len(models)
    w = [[0.0] * K for _ in range(K)]
    for (a, b), v in wins.items():
        w[idx[a]][idx[b]] += v
    s = [0.0] * K
    for _ in range(it):
        new = list(s)
        for i in range(K):
            Wi = sum(w[i])
            if Wi <= 0:
                continue
            den = sum((w[i][j] + w[j][i]) / (math.exp(s[i]) + math.exp(s[j]))
                      for j in range(K) if j != i and (w[i][j] + w[j][i]) > 0)
            if den > 0:
                new[i] = math.log(Wi / den)
        mean = sum(new) / K
        new = [x - mean for x in new]
        if max(abs(a - b) for a, b in zip(new, s)) < 1e-12:
            return dict(zip(models, new))
        s = new
    return dict(zip(models, s))


cc = sqlite3.connect("file:%s?mode=ro" % CACHE.replace(os.sep, "/"), uri=True)
grid = {}          # (model, domain) -> displacement (key rank - arena rank)
undec = set()      # (model, domain) involved in an undecidable pair
pooled_acc = {}
for slug, lab in DOMS:
    db = os.path.join(ROOT, "experiment_results", "r8", slug,
                      "ratings_r8_%s.db" % slug).replace(os.sep, "/")
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    rs = list(c.execute("select eval_question_id,model_a,model_b,winner,is_tie"
                        " from match_history where condition='MAIN'"))
    ms = sorted({m for r in rs for m in (r[1], r[2])})
    qs = sorted({str(r[0]) for r in rs})
    N = len(qs)
    ph = ",".join("?" * len(ms))
    qh = ",".join("?" * len(qs))
    acc = {m: ok / n for m, n, ok in cc.execute(
        "select model_name,count(*),sum(is_correct) from eval_results"
        " where model_name in (%s) and question_id in (%s)"
        " group by model_name" % (ph, qh), ms + qs)}
    for m in ms:
        pooled_acc[m] = pooled_acc.get(m, 0) + acc[m] / len(DOMS)
    wins = {}
    for q, a, b, w, t in rs:
        if t:
            wins[(a, b)] = wins.get((a, b), 0) + .5
            wins[(b, a)] = wins.get((b, a), 0) + .5
        else:
            lo = b if w == a else a
            wins[(w, lo)] = wins.get((w, lo), 0) + 1.
    th = bt(ms, wins)
    key_rank = {m: i for i, m in enumerate(sorted(ms, key=lambda x: -acc[x]))}
    arena_rank = {m: i for i, m in enumerate(sorted(ms, key=lambda x: -th[x]))}
    for m in ms:
        grid[(m, slug)] = key_rank[m] - arena_rank[m]
    for a, b in itertools.combinations(ms, 2):
        gap = abs(acc[a] - acc[b])
        if gap <= 2 * math.sqrt(acc[a] * (1 - acc[a]) / N
                                + acc[b] * (1 - acc[b]) / N):
            undec.add((a, slug))
            undec.add((b, slug))

models = sorted(pooled_acc, key=lambda m: -pooled_acc[m])
if len(grid) != 64:
    raise SystemExit("MISMATCH: %d cells, expected 64" % len(grid))
if max(abs(v) for v in grid.values()) > 2:
    raise SystemExit("MISMATCH: displacement beyond 2 places")
PUB_RHO = {"math": 1.0000, "physics": 0.9762, "law": 0.9524,
           "engineering": 1.0000, "psychology": 0.9286,
           "philosophy": 0.9762, "history": 0.9524, "cs": 0.9524}
for slug, _ in DOMS:
    ds = [grid[(m, slug)] for m in models]
    if sum(ds) != 0:
        raise SystemExit("MISMATCH: %s displacements sum to %d" % (slug, sum(ds)))
    rho = 1 - 6 * sum(d * d for d in ds) / 504.0
    if abs(rho - PUB_RHO[slug]) > 5e-4:
        raise SystemExit("MISMATCH: %s grid gives rho=%.4f, published %.4f"
                         % (slug, rho, PUB_RHO[slug]))
n_white = sum(1 for v in grid.values() if v == 0)
print("verified: 64 cells, every domain's grid reproduces its published rho;"
      " %d of 64 cells white" % n_white)

plt.rcParams.update({
    "font.size": 9, "font.family": "serif", "pdf.fonttype": 42,
})
fig, ax = plt.subplots(figsize=(6.6, 3.4))
# Diverging fill within the one-accent policy: negative displacement dark
# grey, positive the muted blue (deeper for +2). The signed number is
# printed in every displaced cell, so sign and magnitude survive grayscale.
NEG = "0.25"
POS1 = "#A9C4E0"
POS2 = "#3B6EA5"
for yi, m in enumerate(models):
    for xi, (slug, lab) in enumerate(DOMS):
        d = grid[(m, slug)]
        color = "white" if d == 0 else (NEG if d < 0 else
                                        (POS1 if d == 1 else POS2))
        dark = d < 0 or d >= 2
        ax.add_patch(plt.Rectangle((xi, len(models) - 1 - yi), 1, 1,
                                   facecolor=color, edgecolor="0.8",
                                   lw=0.6))
        if d != 0:
            ax.text(xi + 0.5, len(models) - 1 - yi + 0.5, "%+d" % d,
                    ha="center", va="center", fontsize=8,
                    color="white" if dark else "black")
        if (m, slug) in undec:
            ax.plot(xi + 0.82, len(models) - 1 - yi + 0.19, "o", ms=3.4,
                    mfc="none", mec="white" if dark else "0.45", mew=0.8)
ax.set_xlim(0, len(DOMS))
ax.set_ylim(0, len(models))
ax.set_xticks([i + 0.5 for i in range(len(DOMS))])
ax.set_xticklabels([lab for _, lab in DOMS], fontsize=8)
ax.set_yticks([len(models) - 1 - i + 0.5 for i in range(len(models))])
ax.set_yticklabels([SHORT[m] for m in models], fontsize=8)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xlabel("domain (settled batch)")
ax.annotate("white = arena rank equals key rank;  displaced cells print the "
            "signed offset (blue $+$, dark $-$);  $\\circ$ = in an "
            "undecidable pair there",
            xy=(0.5, -0.30), xycoords="axes fraction", ha="center",
            fontsize=7.5, color="0.25")

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
