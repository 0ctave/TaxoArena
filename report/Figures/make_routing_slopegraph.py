# Generates Figure 1.1 (routing micro-example slopegraph) for the thesis.
# Data are the synthetic, declared-illustrative values from the routing
# micro-example (Section 1.1.2) and Table 1.1; figure and table must
# always show the same numbers.
# Run from anywhere:  python report/Figures/make_routing_slopegraph.py
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "routing_slopegraph.pdf")

# Synthetic values, identical to Table 1.1 (declared illustrative).
DOMAINS = ("Mathematics", "History")
MODEL_A = (0.91, 0.55)   # accuracy of Model A on the two domains
MODEL_B = (0.54, 0.92)   # accuracy of Model B on the two domains
AGGREGATE = 0.72         # shared aggregate over all 14 MMLU-Pro domains

# Crossing of the two segments: A(t) = 0.91 - 0.36 t, B(t) = 0.54 + 0.38 t
CROSS_X = (MODEL_A[0] - MODEL_B[0]) / (
    (MODEL_A[0] - MODEL_B[0]) + (MODEL_B[1] - MODEL_A[1]))
CROSS_Y = MODEL_A[0] + (MODEL_A[1] - MODEL_A[0]) * CROSS_X

# CVD-safe pair (validated: protan/deutan/tritan dE >= 24); grayscale
# safety comes from lightness difference + solid-vs-dashed + end labels.
BLUE = "#2a78d6"     # Model A, solid
ORANGE = "#eb6834"   # Model B, dashed
INK = "#0b0b0b"
MUTED = "#898781"
BASELINE = "#b3b2a8"
AXIS = "#c3c2b7"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman",
                   "DejaVu Serif"],
    "font.size": 9,
    "pdf.fonttype": 42,
    "text.color": INK,
})

fig, ax = plt.subplots(figsize=(5.8, 3.6))

# --- shared-aggregate reference line, labeled directly -----------------
ax.plot([-0.02, 1.02], [AGGREGATE, AGGREGATE], color=BASELINE, lw=1.0,
        ls=(0, (4, 3)), zorder=1)
ax.text(1.045, AGGREGATE, f"shared aggregate  {AGGREGATE:.2f}\n(all 14 domains)",
        ha="left", va="center", fontsize=8, color=MUTED, zorder=1,
        linespacing=1.3)

# --- the two model lines ------------------------------------------------
for vals, color, ls, name in (
        (MODEL_A, BLUE, "-", "Model A"),
        (MODEL_B, ORANGE, (0, (5, 2.2)), "Model B")):
    ax.plot([0, 1], vals, color=color, lw=2.2, ls=ls, zorder=3,
            solid_capstyle="round")
    ax.plot([0, 1], vals, "o", color=color, ms=6, zorder=4, ls="none",
            markeredgecolor="white", markeredgewidth=1.2)
    # model name + value at BOTH line ends (identity never color-alone)
    ax.text(-0.045, vals[0], f"{name}   {vals[0]:.2f}",
            ha="right", va="center", fontsize=9, color=INK)
    ax.text(1.045, vals[1], f"{vals[1]:.2f}   {name}",
            ha="left", va="center", fontsize=9, color=INK)

# --- emphasize the crossing --------------------------------------------
ax.scatter([CROSS_X], [CROSS_Y], s=150, facecolor="none", edgecolor=INK,
           linewidth=1.1, zorder=5)
ax.annotate("the lines cross:\na scalar ranking cannot represent this",
            xy=(CROSS_X, CROSS_Y + 0.022), xytext=(CROSS_X, 0.915),
            ha="center", va="bottom", fontsize=8.2, color=INK,
            linespacing=1.35,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9,
                            shrinkA=2, shrinkB=1))

# --- domain column titles ----------------------------------------------
for x, label in ((0, DOMAINS[0]), (1, DOMAINS[1])):
    ax.text(x, 1.015, label, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=INK)
    ax.plot([x, x], [0.46, 1.0], color=AXIS, lw=0.6, zorder=0)

# --- minimal, recessive y-axis with a real axis label -------------------
ax.set_xlim(-0.48, 1.36)
ax.set_ylim(0.44, 1.04)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_position(("data", -0.48))
ax.spines["left"].set_bounds(0.5, 1.0)
ax.spines["left"].set_color(AXIS)
ax.set_xticks([])
ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.tick_params(axis="y", colors=MUTED, labelsize=8, length=3, width=0.6)
ax.set_ylabel("accuracy on held-out questions (synthetic)",
              fontsize=8.5, color=MUTED, labelpad=6)

fig.tight_layout(pad=0.3)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
