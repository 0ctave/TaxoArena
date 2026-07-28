# Generates Figure 1.1 (routing micro-example slopegraph) for the thesis.
# Data are the synthetic, declared-illustrative values from Section 1.1.2.
# Run from anywhere:  python report/Figures/make_routing_slopegraph.py
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "routing_slopegraph.pdf")

# Synthetic values as stated in the text (declared illustrative).
DOMAINS = [
    ("Mathematics", 0.91, 0.54),
    ("Physics",     0.88, 0.50),
    ("History",     0.55, 0.92),
    ("Philosophy",  0.51, 0.90),
]
AGGREGATE = 0.72

BLUE = "#2a78d6"    # formal domains (Model A stronger)
ORANGE = "#eb6834"  # humanities domains (Model B stronger)
INK = "#0b0b0b"
MUTED = "#898781"
BASELINE = "#c3c2b7"

COLOR = {"Mathematics": BLUE, "Physics": BLUE,
         "History": ORANGE, "Philosophy": ORANGE}

# Small vertical nudges (data units) so end labels never collide.
NUDGE_L = {"Mathematics": 0.004, "Physics": -0.004,
           "History": 0.004, "Philosophy": -0.004}
NUDGE_R = {"History": 0.008, "Philosophy": -0.008,
           "Mathematics": 0.008, "Physics": -0.008}

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman",
                   "DejaVu Serif"],
    "font.size": 9,
    "pdf.fonttype": 42,
    "text.color": INK,
})

fig, ax = plt.subplots(figsize=(5.6, 3.5))

# Shared-aggregate reference line (recessive, behind the slopes).
ax.plot([0, 1], [AGGREGATE, AGGREGATE], color=BASELINE, lw=1.0,
        ls=(0, (4, 3)), zorder=1)
ax.text(-0.045, AGGREGATE, f"shared aggregate  {AGGREGATE:.2f}",
        ha="right", va="center", fontsize=8, color=MUTED, zorder=1)

for name, a, b in DOMAINS:
    c = COLOR[name]
    ax.plot([0, 1], [a, b], color=c, lw=2, zorder=3,
            solid_capstyle="round")
    ax.plot([0, 1], [a, b], "o", color=c, ms=5.5, zorder=4,
            markeredgecolor="white", markeredgewidth=1.2)
    ax.text(-0.045, a + NUDGE_L[name], f"{name}  {a:.2f}",
            ha="right", va="center", fontsize=9, color=INK)
    ax.text(1.045, b + NUDGE_R[name], f"{b:.2f}",
            ha="left", va="center", fontsize=9, color=INK)

# Column headers.
for x, label in ((0, "Model A"), (1, "Model B")):
    ax.text(x, 0.985, label, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=INK)

# Slopegraph anatomy: no axes, no grid, no box.
ax.set_xlim(-0.62, 1.18)
ax.set_ylim(0.44, 1.01)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

fig.tight_layout(pad=0.3)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
