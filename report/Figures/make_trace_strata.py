# Generates the trace-strata figure (answer-key agreement by trace stratum,
# Run A: pilot 8-model Math arena, frozen run) for the thesis.
#
# REAL DATA ONLY. The script recomputes every plotted number from the primary
# sources and asserts it against the published values before any drawing
# happens; on any mismatch it raises and emits no PDF.
#
# Primary sources:
#   experiment_results/arena_math_frozen/seed_42/judging/MAIN_verdicts.csv
#   experiment_results/arena_math_frozen/seed_42/judging/GENERIC_JUDGE_verdicts.csv
#   mmlu_pro_dataset_cache_v2.db  (eval_results, panel (b) accuracy vector only)
#
# Conventions:
#   - Restrict to rows where exactly one response is correct and the judge did
#     not tie ("decided, one-correct" rows). A hit = the judge picked the side
#     whose answer matched the ground-truth key.
#   - Trace classification is static (4 traced, 4 stub models).
#   - Panel (b): MAIN only, restricted to model pairs whose ground-truth
#     accuracy gap is < 20 percentage points, where each model's accuracy is
#     computed over ALL 241 judged questions (eval_results joined on
#     question_id, which is the verdict CSV's own QueryId space --- these are
#     the same Correct fields the CSV carries, extended to the questions a
#     model was not paired on). NOTE: QueryId is eval question_id, NOT
#     mmlu_pro.id; the two id spaces must never be joined.
#   - Error bars: Wilson score 95% intervals.
#
# Run from anywhere:  python report/Figures/make_trace_strata.py
import csv
import math
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "trace_strata.pdf")
JUDGING = os.path.join(ROOT, "experiment_results", "arena_math_frozen",
                       "seed_42", "judging")
EVAL_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")

TRACED = {"gpt-4o-2024-08-06", "claude-3-5-sonnet-20241022",
          "deepseek-chat-v2_5", "claude-3-5-haiku-20241022"}
STUB = {"Meta-Llama-3_1-70B-Instruct", "Qwen1.5-72B-Chat",
        "Llama-2-70b-hf", "Llama-2-13b-hf"}
STRATA = ("tt", "tn", "nn")

# Published values this script MUST reproduce (hits, n, ties per stratum).
PUBLISHED = {
    "MAIN":    {"tt": (181, 215, 40), "tn": (590, 660, 17), "nn": (143, 154, 74)},
    "GENERIC": {"tt": (174, 211, 44), "tn": (595, 670, 7),  "nn": (144, 152, 76)},
}
PUBLISHED_B = {"tt": (144, 173), "tn": (50, 67), "nn": (32, 33)}   # gap < 20 pp
PUBLISHED_PCT_B = {"tt": 83.2, "tn": 74.6, "nn": 97.0}
N_JUDGED_QUESTIONS = 241


def stratum(a, b):
    return {2: "tt", 1: "tn", 0: "nn"}[(a in TRACED) + (b in TRACED)]


def tobool(s):
    return s.strip().lower() == "true"


def load(fname):
    with open(os.path.join(JUDGING, fname), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tally(rows, keep=lambda r: True):
    """hits / n over decided one-correct rows; ties over one-correct rows."""
    hits = {s: 0 for s in STRATA}
    n = {s: 0 for s in STRATA}
    ties = {s: 0 for s in STRATA}
    for r in rows:
        if not keep(r):
            continue
        a, b = r["ModelA"], r["ModelB"]
        ca, cb = tobool(r["CorrectA"]), tobool(r["CorrectB"])
        if ca == cb:                       # need exactly one correct response
            continue
        s = stratum(a, b)
        if r["Winner"].strip() == "TIE":
            ties[s] += 1
            continue
        n[s] += 1
        winner = a if r["Winner"].strip() == "Model A" else b
        correct = a if ca else b
        if winner == correct:
            hits[s] += 1
    return hits, n, ties


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# ---------------------------------------------------------------- panel (a)
main_rows = load("MAIN_verdicts.csv")
gen_rows = load("GENERIC_JUDGE_verdicts.csv")

results = {}
for cond, rows in (("MAIN", main_rows), ("GENERIC", gen_rows)):
    hits, n, ties = tally(rows)
    for s in STRATA:
        got = (hits[s], n[s], ties[s])
        want = PUBLISHED[cond][s]
        assert got == want, (
            f"{cond}/{s}: recomputed (hits, n, ties) = {got}, published {want}")
    results[cond] = (hits, n, ties)

qids = {int(r["QueryId"]) for r in main_rows}
assert len(qids) == N_JUDGED_QUESTIONS, (
    f"expected {N_JUDGED_QUESTIONS} judged questions, found {len(qids)}")

# ---------------------------------------------------------------- panel (b)
# Per-model ground-truth accuracy over the 241 judged questions.
db = sqlite3.connect(EVAL_DB)
ph = ",".join("?" * len(qids))
acc_num = {}
acc_den = {}
csv_correct = {}          # (question_id, model) -> Correct field from the CSV
for r in main_rows:
    csv_correct[(int(r["QueryId"]), r["ModelA"])] = tobool(r["CorrectA"])
    csv_correct[(int(r["QueryId"]), r["ModelB"])] = tobool(r["CorrectB"])
for q, m, ic in db.execute(
        f"select question_id, model_name, is_correct from eval_results "
        f"where question_id in ({ph})", tuple(qids)):
    if m in TRACED | STUB:
        acc_num[m] = acc_num.get(m, 0) + ic
        acc_den[m] = acc_den.get(m, 0) + 1
        # the CSV's own Correct fields must agree with eval_results
        if (q, m) in csv_correct:
            assert bool(ic) == csv_correct[(q, m)], (
                f"CSV Correct field disagrees with eval_results for q={q}, {m}")
db.close()
ACC = {m: acc_num[m] / acc_den[m] for m in acc_num}
assert all(acc_den[m] == N_JUDGED_QUESTIONS for m in ACC), \
    "every roster model must cover all 241 judged questions in eval_results"

hits_b, n_b, _ = tally(
    main_rows, keep=lambda r: abs(ACC[r["ModelA"]] - ACC[r["ModelB"]]) < 0.20)
for s in STRATA:
    got = (hits_b[s], n_b[s])
    assert got == PUBLISHED_B[s], (
        f"panel (b) {s}: recomputed (hits, n) = {got}, published {PUBLISHED_B[s]}")
    pct = 100 * hits_b[s] / n_b[s]
    assert abs(pct - PUBLISHED_PCT_B[s]) < 0.05, (
        f"panel (b) {s}: {pct:.1f}% != published {PUBLISHED_PCT_B[s]}%")

# ------------------------------------------------------------------- report
print("VERIFIED against published values (Wilson 95% CIs):")
for cond in ("MAIN", "GENERIC"):
    hits, n, ties = results[cond]
    for s in STRATA:
        lo, hi = wilson(hits[s], n[s])
        print(f"  {cond:8s} {s}: {hits[s]}/{n[s]} = {100*hits[s]/n[s]:.1f}% "
              f"[{100*lo:.1f}, {100*hi:.1f}]  ties={ties[s]}")
print("  panel (b), MAIN, ground-truth accuracy gap < 20 pp "
      f"(accuracy over the {N_JUDGED_QUESTIONS} judged questions):")
for s in STRATA:
    lo, hi = wilson(hits_b[s], n_b[s])
    print(f"    {s}: {hits_b[s]}/{n_b[s]} = {100*hits_b[s]/n_b[s]:.1f}% "
          f"[{100*lo:.1f}, {100*hi:.1f}]")

# --------------------------------------------------------------------- plot
BLUE = "#2a78d6"      # MAIN judge
ORANGE = "#eb6834"    # generic judge
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman",
                   "DejaVu Serif"],
    "font.size": 9,
    "pdf.fonttype": 42,
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})

XLBL = ["trace × trace", "trace × no-trace", "no-trace × no-trace"]

fig, (axa, axb) = plt.subplots(
    1, 2, figsize=(5.9, 3.1), sharey=True,
    gridspec_kw={"width_ratios": [1.45, 1.0], "wspace": 0.06})

for ax in (axa, axb):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.set_xlim(-0.55, 2.55)
    ax.set_xticks(range(3))
    ax.tick_params(length=0)

axa.set_ylim(58, 101)
axa.set_ylabel("agreement with answer key (%)")

# panel (a): both judge conditions
series = [("MAIN judge", "MAIN", BLUE, "o", -0.11),
          ("generic judge", "GENERIC", ORANGE, "s", +0.11)]
for label, cond, color, marker, dx in series:
    hits, n, ties = results[cond]
    for i, s in enumerate(STRATA):
        p = 100 * hits[s] / n[s]
        lo, hi = (100 * v for v in wilson(hits[s], n[s]))
        x = i + dx
        axa.plot([x, x], [lo, hi], color=color, lw=1.4,
                 solid_capstyle="round", zorder=3)
        axa.plot([x], [p], marker, color=color, ms=6, zorder=4,
                 markeredgecolor="white", markeredgewidth=1.0)
        va, dy = ("bottom", 1.0) if cond == "MAIN" else ("top", -1.2)
        ha = "right" if cond == "MAIN" else "left"
        axa.text(x - 0.16 if cond == "MAIN" else x + 0.16, p,
                 f"{p:.1f}", ha=ha, va="center", fontsize=7.5, color=INK)

# tie counts as a small secondary row under the axis (74 vs 17 corroboration)
for i, s in enumerate(STRATA):
    t_main = results["MAIN"][2][s]
    t_gen = results["GENERIC"][2][s]
    axa.text(i, 60.4, f"ties {t_main} | {t_gen}",
             ha="center", va="bottom", fontsize=7, color=MUTED)

axa.set_xticklabels([l.replace(" × ", " ×\n") for l in XLBL],
                    fontsize=8)
axa.set_title("(a)  all decided one-correct comparisons", fontsize=9,
              loc="left", pad=8)
leg = axa.legend(
    handles=[plt.Line2D([], [], color=BLUE, marker="o", ls="", ms=6,
                        markeredgecolor="white", label="MAIN judge"),
             plt.Line2D([], [], color=ORANGE, marker="s", ls="", ms=6,
                        markeredgecolor="white", label="generic judge")],
    loc="upper left", frameon=False, fontsize=8, handletextpad=0.3,
    borderaxespad=0.1)

# panel (b): MAIN only, capability-matched pairs
for i, s in enumerate(STRATA):
    p = 100 * hits_b[s] / n_b[s]
    lo, hi = (100 * v for v in wilson(hits_b[s], n_b[s]))
    axb.plot([i, i], [lo, hi], color=BLUE, lw=1.4,
             solid_capstyle="round", zorder=3)
    axb.plot([i], [p], "o", color=BLUE, ms=6, zorder=4,
             markeredgecolor="white", markeredgewidth=1.0)
    axb.text(i + 0.14, p, f"{p:.1f}", ha="left", va="center",
             fontsize=7.5, color=INK)
    axb.text(i, 60.4, f"n = {n_b[s]}", ha="center", va="bottom",
             fontsize=7, color=MUTED)

axb.set_xticklabels([l.replace(" × ", " ×\n") for l in XLBL],
                    fontsize=8)
axb.set_title("(b)  MAIN, accuracy gap < 20 pp", fontsize=9,
              loc="left", pad=8)

fig.subplots_adjust(left=0.085, right=0.985, top=0.90, bottom=0.20)
fig.text(0.005, 0.015,
         "dots: agreement with the answer key; bars: Wilson 95% CI; "
         "decided comparisons where exactly one response is correct",
         fontsize=7, color=MUTED, ha="left")
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
