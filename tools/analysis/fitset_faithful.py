"""FITSET-FAITHFUL (stage 0 only; lane r2): with B0's 133 leaves and topology held fixed, does re-estimating each split anchor's
leaf means on the TRAIN items of its DECLARED class (class-pure fit sets) file EVAL better than A as built (FF1), and does any
per-anchor gain track the routed fit set's impurity beyond its size (FF2)? ZERO calls: no judge, no LLM, no embedding call, no
build; no DB is opened by the readout (the B0-2 pool check, a reader, runs as its own process first).

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — FITSET-FAITHFUL (stage 0
only): with B0 of lane r2's leaves and topology held fixed, ..." (L23580-L23614, commit c1ed61d5; gates bracket at L23582, commit
111c2dc2: the author's "yes run FITSET-FAITHFUL stage 0" and the C-PB-1 WAL checkpoint); docs/agents/results/FITSET-FAITHFUL.json.
Stage S1 (an engine flag anchorFitSet=declared, an A-gt construction) and A replicates at further construction seeds are NOT
registered and nothing here builds anything.

OBJECTS (as DEEP-SPLIT-COMPARE's; lane r2, commit M 2703f2c2; every path under experiment_results/archv2/rp12_r2/, refused outside
it): read through g13_breakdown.load_objects UNCHANGED (I0 provenance, I2 descent, I3 argmax-vmfMu, I4 structure, I5 support;
check_sides: no EVAL or GATE item in the bundle's TRAIN), the six member snapshots' LAST lines, the flatLeaf CSVs.
Pinned modules (blob, LF), imported UNCHANGED: deep_split_compare.py 31af4cea (load_anchors, name_and_file, cells_kmeans for the B /
B-gt arms, depth2_identity, check_i4, check_r3_support, guard_paths, pins_lines, v_spread, the hooks) and g13_breakdown.py c29fa1c3
(load_objects, identity_arms, check_i1, stat = the whole-component bootstrap B 2,000 seed 20260929, pool_check_v2); their own
pins (g13_comparator 61d83ec7, rp12_pairing 35214b3f, rp12_lane, flat_mix_mmlu) are checked by them at import.
POOL: g13_breakdown.pool_check_v2 (the B0-2 form: every -wal / -journal of the DBs v2_union_pool reads absent or 0 bytes; the engine
pool file's sha256-lf = 79d48f4b...; v2_union_pool.py --dry-run rc 0), its line printed FIRST; a failure REFUSES.

ARM A-refit (deterministic, no seeds; the only new arm): A's 133 leaves and topology unchanged. In each split anchor a (k_a >= 2)
the TRAIN items of a's DECLARED class (B-gt's fit set, A["gt"][a]) are assigned to the nearest A-leaf UNDER a (cosine to the leaf
vmfMu; the bundle's 512-d slice); each leaf's mean = the normalised mean of its assigned items; a leaf receiving none keeps its
vmfMu (count printed). In the 20 unsplit anchors the cell mean = the normalised mean of the class's TRAIN items. Cells named and
EVAL filed exactly as DSC (deep_split_compare.name_and_file: TRAIN-majority naming by the flatLeaf rule over ALL cells, ties to the
smaller class name, a cell with no TRAIN item takes its anchor's class, counted; EVAL argmax over ALL cells). Guards (refuse): every
declared-class item lands on a leaf of its own anchor (assigned count per anchor = class TRAIN count); every fit index is a TRAIN row.

IDENTITY PRECONDITION (refuses before any new number): DSC's I1 (g13 I1 + U-global + NCC) and depth-2 numbers, I2, I3 (item
counts), I4 and the R3 support denominators (DSC's own functions); P_A 0.8119; P(B_0) 0.7985; P(D_0) 0.8334; P(B-gt_0) - P(D_0)
+0.0028 (point, DSC outcome line 221), each to the printed digits; spread_B (B over seeds 0-4) prints 0.0125 [IMPLEMENTATION CHOICE
(i), for the READY: the bar is the exact recomputed spread_B (77 / 6,139 = 0.012543 in DSC), not the rounded 0.0125; the outcome
prints a knife-edge note when D lies between the two]; the routed F-tree's declared-class purity sums to 10,021 of 12,334 (POSTRUN
W2's figure) [IMPLEMENTATION CHOICE (ii): the impurity of FF2 is 1 - (declared-class items in F-tree(a)) / |F-tree(a)|, and its
pooled sum is checked against W2's 10,021 so the definition is the one the registration cites].

CRITERIA (95% percentile intervals; each clause read separately, no family-wise correction):
  FF1 (DECIDING): D = P(A-refit) - P_A on the 6,139 EVAL items, item-paired, CK-CLOSE components resampled. HELD iff the interval
      lies wholly above 0 AND D > spread_B; FAILED (REVERSED) iff wholly below 0 AND D < -spread_B; UNDETERMINED otherwise (never
      parity: no TOST). (DSC.v_spread, the C-AB form.)
  FF2: over the split anchors with >= 30 EVAL items of their declared class (m), the partial Spearman rho between
      Delta_a = P(A-refit)_a - P(A)_a (EVAL items whose true class is a) and the F-tree impurity of a, controlling for
      log |F-tree(a)| (DSC I3's item counts); ranks with average ties; Fisher-z interval, SE 1 / sqrt(m - 4). HELD iff lower > 0;
      FAILED iff upper <= 0; UNDETERMINED otherwise (and when rho is undefined: a constant variable, or m <= 4).
  F-FF (falsifier): fires iff FF1's interval upper end <= 0.
DESCRIPTIVE (never scored): FF1 on the MMLU_PRO_LB stratum (P4 at the point); the same per-anchor partial rho for DSC's bridge
P(B-gt_0) - P(B_0); leaves receiving no item; A-refit's naming changes against A's leaves CSV names; per-anchor assignment table.
SUPPORT printed beside each deciding statistic: denominator, measured SE / DEFF (from the bootstrap and the cache's own component
sizes) / n_eff / MDE80 / discordance against the registered 0.00446 / 1.223 / 5,020 / 0.0125 / 0.10; FF2 m, SE_z, MDE80 in z and rho.
Not applicable (no judge verdicts, no posting): wrong(established), tie conventions A / B, --pilot / truncation guard, call cache.
The outcome header prints the registered LABEL INFORMATION table and the three CONFOUNDS verbatim.

SELFTEST (--selftest; synthetic lane-r2 layouts written by g13_breakdown._fixture_write with this script's geometry (24-d axes),
read through main(), the real entry point; pool check and machine probe stubbed except in `pool`):
  fixture F (seven MMLU_PRO_LB split anchors a-g with leaves p_i and unit(q_i + t_i r_i); foreign z TRAIN items at r_i drag L2
  (t = 1.5 for a, b, c, f; 0.25 for d, e); z has 200 TRAIN items at zz, so its refit cell stays at zz and the w gain comes from the
  L2 refit alone; EVAL w_i = unit(q_i + 0.8 zz) filed to z by A where t = 1.5 and to q_i by A-refit; 25 class-a probes at
  unit(p_b + 0.3 p_a) wrong for both (their cell's TRAIN majority b, EVAL majority a); anchor g's L2 holds only 5 foreign z TRAIN
  items and receives no declared-class item (kept vmfMu; named z by A and A-refit; its 10 g EVAL items wrong for both); unsplit
  BBH/v: 10 TRAIN at unit(e23 + 0.8 e22) move its class mean off its vmfMu e23, so 10 EVAL at unit(e23 + 1.1 e22) go to u under A
  and to v under A-refit; 10 BBH/v items at unit(e23 + 2 e22) wrong for both), BY HAND: n 315 EVAL; P_A 210/315 0.6667;
  P(A-refit) 270/315 0.8571; D +0.1905; MMLU_PRO_LB D 50/255 +0.1961; m 6 (g has 20 EVAL < 30); Delta a 10/55, b 20/40, c 5/30,
  d 0, e 0, f 15/30 (BBH/v 10/40); impurity a 10/50, b 11/61, c 16/56, d 4/54, e 8/53, f 12/52 (g 5/25, excluded); assignment
  a 26/20, g 20/0; 1 leaf receiving no item; 0 naming changes; FF1 HELD; F-FF DOES NOT FIRE; the partial rho and its interval
  checked against an independent residual-regression oracle.
  fixture N (every t = 0.25, no g or BBH/v-shift EVAL probes): A-refit = A item-wise, D +0.0000 [+0.0000, +0.0000]: FF1
  UNDETERMINED, F-FF FIRES (upper end 0 <= 0), FF2 UNDETERMINED (rho undefined: Delta constant).
  branches / boundaries: every FF1 / FF2 / F-FF branch printed with its values (bar = spread_B exactly -> UNDETERMINED; hi = 0 ->
  FIRES; FF2 upper exactly 0 -> FAILED; m = 4 -> undefined); refusals (lane, every identity constant, I1, depth 2, I2/I3, side
  check, the per-anchor assignment guard, write-once); the REAL pool_check_v2 path (7-byte -wal refuses, POOL line first; pass).
MUTANTS (--mutants; one in-memory edit each, the targeted selftest subset re-run; 2026-10-03): 39 of 39 KILLED, control survived;
the table (registered six: EVAL in a refit M01, refit set = routed F-tree M02, nearest leaf outside the anchor M03, naming from EVAL
M04, spread conjunct dropped M05, FF2 without the size covariate M06; plus min<->max, first site only, zero support, boundary,
denominator, skip path, write-once, identity, pool, dry-run, hooks, ...) is in the commit message and printed by --mutants.

LAUNCH SEQUENCE (the run-operator; a pool READER: never beside a construction or site null, rule 7):
  python tools/analysis/fitset_faithful.py --selftest
  python tools/analysis/fitset_faithful.py --mutants
  python tools/analysis/fitset_faithful.py --dry-run --lane r2   # B0-2 pool check first; pins; identity (SEEN numbers); denominators; NO new statistic
  python tools/analysis/fitset_faithful.py --run --lane r2       # the readout; outcome WRITE-ONCE (mode x)
  (from a worktree: --root <checkout holding experiment_results> and TAXOARENA_DATA_ROOT=<that checkout> for the pool child)
Output: experiment_results/archv2/rp12_r2/fitset_faithful_s0_outcome.txt (write-once; never committed). stdout: PYTHONIOENCODING=utf-8.
"""
import os
import sys

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io            # noqa: E402
import json          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import contextlib    # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[FF]"
PINS = (("deep_split_compare.py", "31af4ceaa35fadfaf0bd43acc2a237d85c8ca30e"),
        ("g13_breakdown.py", "c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40"))


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import deep_split_compare as DSC   # noqa: E402  (checks g13_breakdown, g13_comparator, rp12_pairing; they check the rest)
GB = DSC.GB
G, FM, LN = GB.G, GB.FM, GB.LN
SEEDS = G.SEEDS
RES = GB.RES
EMPTY = GB.EMPTY

# ── the registered constants ────────────────────────────────────────────────────────────────────────────────────────────
REG = dict(DSC.REG)
REG.update(
    out=RES + "/fitset_faithful_s0_outcome.txt",
    ff_ident=dict(p_a="0.8119", p_b0="0.7985", p_d0="0.8334", bgt_d0="+0.0028", spread_b="0.0125"),
    purity=(10021, 12334),
    min_eval=30,
)
_CFG = [REG]


def cfg():
    return _CFG[0]


# Registered Support (d)/(e): FF1 (SE, MDE80, planning discordance, transported DEFF, n_eff); FF2 (planning m, SE_z, z MDE80, rho MDE)
SUPPORT_FF1 = (0.00446, 0.0125, 0.10, 1.223, 5020)
SUPPORT_FF2 = (30, 0.196, 0.549, 0.50)
PRED = {"P1 D": (0.015, (-0.005, 0.035)), "P2 FF2 rho": (0.30, (-0.10, 0.65)), "P4 MMLU_PRO_LB D (descriptive)": (0.025, (0.000, 0.050))}
PROB = (("FF1", "HELD 0.30, UNDETERMINED 0.62, REVERSED 0.08"), ("FF2", "HELD 0.20"), ("F-FF", "fires 0.12"))
Z95 = 1.96

# hooks the selftest swaps (nothing else writes them)
_ROOT = [ROOT]
_SIDES = [GB._committed_sides]
_POOL_GUARD = [GB.pool_check_v2]
_MACHINE = [GB._machine_state]


@contextlib.contextmanager
def _hooks(root):
    """DSC's and (through DSC._gb_hooks) g13_breakdown's readers read their own hooks: pointed at this script's for the call."""
    saved = (DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0])
    DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = cfg(), root, _SIDES[0]
    try:
        with DSC._gb_hooks():
            yield
    finally:
        DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = saved


def unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


# ── the new arm ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def assign_leaves(o, X, ks):
    """Nearest A-leaf (cosine to the leaf vmfMu) among the global leaf indices ks -> the global leaf index per row of X."""
    Lmu = np.vstack([o["nodes"][o["leaves"][k]]["mu"] for k in ks])
    return np.asarray(ks)[np.argmax(X @ Lmu.T, axis=1)]


def refit_cells(o, A):
    """A-refit -> (C (133, D), cell anchor (133,), info). One cell per A leaf, in o["leaves"] order."""
    leaves = o["leaves"]
    n_train = len(o["yt"])
    by_anchor = {}
    for k, u in enumerate(leaves):
        by_anchor.setdefault(A["leaf_anchor"][u], []).append(k)
    C = np.zeros((len(leaves), o["Xt"].shape[1]))
    ca = np.array([A["leaf_anchor"][u] for u in leaves])
    assigned = np.zeros(len(leaves), dtype=int)
    for a in range(len(A["anchors"])):
        ks = by_anchor[a]
        fit = np.asarray(A["gt"][a], dtype=int)
        if len(fit) == 0:
            refuse("anchor %s has no TRAIN item of its declared class" % A["label"][A["anchors"][a]])
        if fit.min() < 0 or fit.max() >= n_train:
            refuse("anchor %s: a refit index is not a TRAIN row" % A["label"][A["anchors"][a]])
        X = o["Xt"][fit]
        if len(ks) == 1:
            C[ks[0]] = unit(X.sum(axis=0))
            assigned[ks[0]] = len(fit)
            continue
        kk = assign_leaves(o, X, ks)
        if not set(kk.tolist()) <= set(ks):
            refuse("A-refit: anchor %s: a declared-class item was assigned to a leaf outside the anchor" % A["label"][A["anchors"][a]])
        for k in ks:
            m = kk == k
            assigned[k] = int(m.sum())
            C[k] = unit(X[m].sum(axis=0)) if m.any() else o["nodes"][leaves[k]]["mu"]
    for a in range(len(A["anchors"])):
        got = int(assigned[by_anchor[a]].sum())
        if got != len(A["gt"][a]):
            refuse("A-refit: anchor %s's leaves received %d items, its declared class holds %d TRAIN items"
                   % (A["label"][A["anchors"][a]], got, len(A["gt"][a])))
    none = [leaves[k] for k in range(len(leaves)) if assigned[k] == 0 and A["ka"][ca[k]] > 1]
    return C, ca, dict(assigned=assigned, none=none, by_anchor=by_anchor)


def arm_refit(o, A):
    C, ca, info = refit_cells(o, A)
    ok, names, n_empty, _e = DSC.name_and_file(o, A, C, ca)
    a_names = [o["leaf_dom"][u] for u in o["leaves"]]
    changes = [(u, a_names[k], o["classes"][names[k]]) for k, u in enumerate(o["leaves"]) if a_names[k] != o["classes"][names[k]]]
    info.update(n_empty=n_empty, changes=changes)
    return ok, info


def arm_b(o, A, fitsets, seed):
    C, ca, _t, _d = DSC.cells_kmeans(o, A, fitsets, A["ka"], seed)
    return DSC.name_and_file(o, A, C, ca)[0]


# ── identity (refuses) ──────────────────────────────────────────────────────────────────────────────────────────────────

def anchor_stats(o, A):
    """Per anchor: declared-class EVAL count, F-tree size, declared-class items in F-tree, impurity, FF2 inclusion."""
    na = len(A["anchors"])
    n_ev = np.array([int((A["e_anchor"] == a).sum()) for a in range(na)])
    size = np.array([len(A["ftree"][a]) for a in range(na)])
    pure = np.array([int((o["yt"][A["ftree"][a]] == A["a_cls"][a]).sum()) for a in range(na)])
    imp = np.array([1.0 - pure[a] / size[a] if size[a] else float("nan") for a in range(na)])
    incl = (A["ka"] > 1) & (n_ev >= cfg()["min_eval"])
    return dict(n_ev=n_ev, size=size, pure=pure, imp=imp, incl=incl)


def identity_ff(o, A, ident):
    c = cfg()
    okB = {s: arm_b(o, A, A["ftree"], s) for s in SEEDS}
    okBgt0 = arm_b(o, A, A["gt"], 0)
    sB = max(float(okB[s].mean()) for s in SEEDS) - min(float(okB[s].mean()) for s in SEEDS)
    st = GB.stat(okBgt0 - ident["kc_ok"][0], o["comp"])
    got = dict(p_a="%.4f" % o["fl"].mean(), p_b0="%.4f" % okB[0].mean(), p_d0="%.4f" % ident["kc_ok"][0].mean(),
               bgt_d0="%+.4f" % st["d"], spread_b="%.4f" % sB)
    want = dict(c["ff_ident"])
    want["bgt_d0"] = "%+.4f" % float(want["bgt_d0"])
    bad = [k for k in want if got[k] != want[k]]
    if bad:
        refuse("IDENTITY: %s reproduced as %s, recorded %s" % (bad, [got[k] for k in bad], [want[k] for k in bad]))
    S = anchor_stats(o, A)
    pur = (int(S["pure"].sum()), int(S["size"].sum()))
    if pur != tuple(c["purity"]):
        refuse("IDENTITY: the F-tree's declared-class purity is %d / %d, not POSTRUN W2's %d / %d" % (pur + tuple(c["purity"])))
    return dict(got=got, okB=okB, okBgt0=okBgt0, spread_b=sB, bgt_st=st, S=S, purity=pur)


# ── statistics ──────────────────────────────────────────────────────────────────────────────────────────────────────────

def _ranks(x):
    from scipy.stats import rankdata
    return rankdata(np.asarray(x, dtype=np.float64), method="average")


def _pearson(a, b):
    a, b = a - a.mean(), b - b.mean()
    den = float(np.sqrt((a * a).sum() * (b * b).sum()))
    return float((a * b).sum()) / den if den > 0 else float("nan")


def partial_spearman(x, y, z):
    """-> dict(rho, lo, hi, m, se_z, plain). Partial Pearson on average ranks of (x, y | z); Fisher z with SE 1 / sqrt(m - 4)."""
    m = len(x)
    rx, ry, rz = _ranks(x), _ranks(y), _ranks(z)
    rxy, rxz, ryz = _pearson(rx, ry), _pearson(rx, rz), _pearson(ry, rz)
    den = (1 - rxz ** 2) * (1 - ryz ** 2)
    rho = (rxy - rxz * ryz) / np.sqrt(den) if (den > 1e-15 and rxy == rxy and rxz == rxz and ryz == ryz) else float("nan")
    out = dict(rho=float(rho), m=m, plain=rxy, se_z=(1.0 / np.sqrt(m - 4)) if m > 4 else float("nan"), lo=float("nan"), hi=float("nan"))
    if rho == rho and m > 4:
        r = min(max(rho, -0.999999), 0.999999)
        zc = float(np.arctanh(r))
        out["lo"], out["hi"] = float(np.tanh(zc - Z95 * out["se_z"])), float(np.tanh(zc + Z95 * out["se_z"]))
    return out


def v_ff1(d, lo, hi, bar):
    return DSC.v_spread(d, lo, hi, bar)


def v_ff2(r):
    """HELD iff lower > 0; FAILED iff upper <= 0; UNDETERMINED otherwise or when undefined."""
    if not (r["lo"] == r["lo"] and r["hi"] == r["hi"]):
        return "UNDETERMINED"
    if r["lo"] > 0:
        return "HELD"
    if r["hi"] <= 0:
        return "FAILED"
    return "UNDETERMINED"


def f_ff(hi):
    return bool(hi <= 0)


def verdicts(R):
    """The single site of every verdict: (FF1 word, FF2 word, F-FF fires) from R's ff1 statistic, spread_B and ff2."""
    st = R["ff1"]
    return v_ff1(st["d"], st["lo"], st["hi"], R["spread_b"]), v_ff2(R["ff2"]), f_ff(st["hi"])


def per_anchor_delta(o, A, ok_new, ok_old):
    na = len(A["anchors"])
    out = np.full(na, np.nan)
    pn, po = np.full(na, np.nan), np.full(na, np.nan)
    for a in range(na):
        m = A["e_anchor"] == a
        if m.any():
            pn[a], po[a] = float(ok_new[m].mean()), float(ok_old[m].mean())
            out[a] = pn[a] - po[a]
    return out, pn, po


def compute(o, A, idn):
    c = cfg()
    comp = o["comp"]
    okA = o["fl"].astype(np.int64)
    okR, info = arm_refit(o, A)
    R = {"n": len(okA), "G": len(set(comp.tolist())), "P_A": float(okA.mean()), "P_R": float(okR.mean()), "info": info,
         "spread_b": idn["spread_b"]}
    R["ff1"] = GB.stat(okR - okA, comp)
    mm = o["esrc"] == c["scoreable"]
    R["ff1_m"] = GB.stat((okR - okA)[mm], comp[mm]) if mm.any() else None
    S = idn["S"]
    dl, pn, po = per_anchor_delta(o, A, okR, okA)
    incl = S["incl"]
    R["S"], R["delta"], R["pn"], R["po"] = S, dl, pn, po
    R["ff2"] = partial_spearman(dl[incl], S["imp"][incl], np.log(S["size"][incl]))
    db, _p1, _p2 = per_anchor_delta(o, A, idn["okBgt0"], idn["okB"][0])
    R["bridge"] = partial_spearman(db[incl], S["imp"][incl], np.log(S["size"][incl]))
    R["delta_bridge"] = db
    return R


# ── rendering ───────────────────────────────────────────────────────────────────────────────────────────────────────────

LABEL_INFO = (
    "LABEL INFORMATION PER ARM (the like-with-like lesson, memory anchored-tree-comparisons; registered table, verbatim):",
    " | arm | depth-2 cells | fit sets below depth 2 | partition / leaf geometry below depth 2 | naming |",
    " |---|---|---|---|---|",
    " | A (B0 of lane r2) | B0's anchors, seeded from TRAIN ground truth | routed F-tree (81% class-pure) | label-free vMF splits | TRAIN majority |",
    " | A-refit (deciding) | inherited from A | TRAIN items of the declared class (labels) | A's leaves and topology; means re-estimated | TRAIN majority |",
    " | B (DSC, k-means) | inherited (F-tree) | routed F-tree | label-free k-means, k_a | TRAIN majority |",
    " | B-gt (DSC bridge) | TRAIN class labels | declared class (labels) | label-free k-means, k_a | TRAIN majority |",
    " | D (KC) | TRAIN class labels | declared class (labels) | one class per prototype (labels) | owned class |",
    " A-refit uses MORE TRAIN labels than A (fit-set membership below depth 2): an anchored-tree variant only; never \"label-free\","
    " never evidence about anchor-free trees (RP13).")
CONFOUNDS = (
    "CONFOUNDS (named by the checkpoint; carried by every sentence):",
    " (1) FIT-SET SIZE vs PURITY: the declared-class set differs in size from the routed set (e.g. GPQA Chemistry 114 routed items vs"
    " 130 class items); FF1 does not separate them, FF2 adjusts for log size only.",
    " (2) K-MEANS-ONLY EVIDENCE: the motivating bridge is k-means; FF1 re-estimates the vMF leaves' MEANS on fixed topology, which is"
    " not a construction with declared fit sets (S1, unregistered).",
    " (3) SCOPE: anchored trees only; it ADDS TRAIN-label use below depth 2 (the table above).")
WILL_NOT_SHOW = (
    "WHAT THIS RESULT WILL NOT SHOW (fixed before data): that a construction with declared fit sets would file better (S1,"
    " unregistered); A's construction-seed variance (one build); anything about anchor-free trees, label-free cells or RP13; a"
    " split-rule effect (topology fixed); parity (no TOST); any certificate; another draw, recipe, embedder, slice or member set; that"
    " labels below depth 2 are \"free\" (they are added label use).")


def fmt_ps(r):
    if r["rho"] != r["rho"]:
        return "rho undefined (a constant ranked variable or a perfectly collinear covariate); m %d" % r["m"]
    if r["lo"] != r["lo"]:
        return "rho %+.4f; interval undefined (m %d <= 4: SE 1 / sqrt(m - 4) needs m > 4)" % (r["rho"], r["m"])
    return "rho %+.4f, 95%% [%+.4f, %+.4f] (Fisher z, SE_z %.4f, m %d; plain Spearman %+.4f)" % (r["rho"], r["lo"], r["hi"], r["se_z"],
                                                                                             r["m"], r["plain"])


def support_ff1(st, bar):
    se_r, mde_r, disc_r, deff_r, neff_r = SUPPORT_FF1
    return ("  support FF1: denominator %d EVAL items / %d CK-CLOSE components; SE %.5f (registered %.5f); DEFF %.3f measured from the"
            " components (transported %.3f); n_eff %.0f (registered %d); MDE80 %.4f (registered %.4f); discordance %.4f (planning %.2f);"
            " effective bar max(MDE80, spread_B) %.4f" % (st["n"], st["G"], st["se"], se_r, st["deff"], deff_r, st["n_eff"], neff_r,
                                                         st["mde"], mde_r, st["disc"], disc_r, max(st["mde"], bar)))


def support_ff2(r):
    m_r, sez_r, zmde_r, rmde_r = SUPPORT_FF2
    if r["m"] > 4:
        sez = 1.0 / np.sqrt(r["m"] - 4)
        return ("  support FF2: m %d split anchors with >= %d EVAL items (planning %d of 32); SE_z %.4f (registered %.3f); MDE80 z %.3f"
                " (registered %.3f), rho %.2f (registered about %.2f)" % (r["m"], cfg()["min_eval"], m_r, sez, sez_r, 2.80 * sez, zmde_r,
                                                                        np.tanh(2.80 * sez), rmde_r))
    return "  support FF2: m %d split anchors with >= %d EVAL items (planning %d of 32): SE_z undefined (m <= 4)" % (
        r["m"], cfg()["min_eval"], m_r)


def verdict_lines(R):
    """Every registered criterion and the falsifier with their values (render prints these verbatim)."""
    L = []
    v, v2, fires = verdicts(R)
    st, bar = R["ff1"], R["spread_b"]
    vals = "D %+.4f, interval [%+.4f, %+.4f], spread_B %.4f (exact %.6f)" % (st["d"], st["lo"], st["hi"], bar, bar)
    if v == "HELD":
        L.append("FF1: HELD (re-estimating A's leaf means on class-pure fit sets files EVAL better than A as built): %s; interval wholly"
                 " above 0 and D > spread_B" % vals)
    elif v == "REVERSED":
        L.append("FF1: FAILED (REVERSED) (A as built files EVAL better than its class-pure refit): %s; interval wholly below 0 and"
                 " D < -spread_B" % vals)
    else:
        L.append("FF1: UNDETERMINED: %s; neither clause holds (never read as parity: no TOST registered)" % vals)
    if min(bar, 0.0125) <= abs(st["d"]) <= max(bar, 0.0125):
        L.append("  KNIFE-EDGE: |D| %.6f lies at or between the rounded bar 0.0125 and the exact spread_B %.6f; the verdict reads the"
                 " exact value (implementation choice (i))" % (abs(st["d"]), bar))
    L.append(support_ff1(st, bar))
    r = R["ff2"]
    if v2 == "HELD":
        L.append("FF2: HELD (the per-anchor gain tracks the routed fit set's impurity beyond its size): %s; lower end > 0" % fmt_ps(r))
    elif v2 == "FAILED":
        L.append("FF2: FAILED: %s; upper end <= 0" % fmt_ps(r))
    else:
        L.append("FF2: UNDETERMINED: %s; %s" % (fmt_ps(r), "the interval contains 0" if r["lo"] == r["lo"] else "no interval"))
    L.append(support_ff2(r))
    L.append("FF1 and FF2 are read separately; no family-wise correction (disclosed).")
    if fires:
        L.append("F-FF: FIRES (FF1's interval upper end %+.4f <= 0): purity of the depth-2 fit sets is not the lever for the vMF rule's"
                 " leaves at this n; the DSC bridge is read as a k-means artefact; checkpoint D's #8' is withdrawn. No recorded number is"
                 " revised." % st["hi"])
    else:
        L.append("F-FF: DOES NOT FIRE: FF1's interval upper end %+.4f > 0" % st["hi"])
    return L


def pred_line(label, obs):
    pt, band = PRED[label]
    head = "%s %+.3f [%+.3f, %+.3f]" % (label, pt, band[0], band[1])
    if obs is None or obs != obs:
        return "PREDICTION %s: observed none -> NOT SCORED (no estimate)" % head
    return "PREDICTION %s: observed %+.4f -> %s" % (head, obs, G.in_band(obs, band))


def render(R, o, A, ident, d2, idn):
    c = cfg()
    S = R["S"]
    L = ["%s FITSET-FAITHFUL stage 0 (lane r2) readout; zero calls; A-refit fits on TRAIN only (check_sides passed; every refit index"
         " a TRAIN row); deterministic (no seeds)" % TAG]
    L += list(LABEL_INFO)
    L += list(CONFOUNDS)
    L.append("NOT APPLICABLE: wrong(established), tie conventions A / B, pilot / truncation guard, call cache (no judge verdict here).")
    L.append("== IDENTITY (all PASSED before any new number): I1 %s" % json.dumps(ident["i1_got"], sort_keys=True))
    L.append("  depth 2 (G13-BREAKDOWN): %s" % json.dumps(d2, sort_keys=True))
    L.append("  I2 %d anchors, %d leaves; I3 F-tree covers %d TRAIN items (table matched); I4 B at k_a = 1 = NCC-on-F-tree; R3 support"
             " matched" % (len(A["anchors"]), len(o["leaves"]), sum(len(x) for x in A["ftree"])))
    L.append("  FITSET-FAITHFUL identity: %s; B-gt_0 - D_0 interval [%+.4f, %+.4f]; F-tree declared-class purity %d / %d"
             % (json.dumps(idn["got"], sort_keys=True), idn["bgt_st"]["lo"], idn["bgt_st"]["hi"], idn["purity"][0], idn["purity"][1]))
    L.append("== DENOMINATORS: EVAL %d items in %d CK-CLOSE components; TRAIN %d; split anchors %d holding %d leaves; FF2 m %d (split"
             " anchors with >= %d EVAL items of their declared class)" % (R["n"], R["G"], len(o["yt"]), int((A["ka"] > 1).sum()),
                                                                         int(A["ka"][A["ka"] > 1].sum()), int(S["incl"].sum()),
                                                                         c["min_eval"]))
    info = R["info"]
    L.append("== A-REFIT BOOKKEEPING: leaves receiving no declared-class item %d %s (each keeps its vmfMu); cells named by the no-TRAIN"
             " fallback %d; naming changes against A's leaves CSV %d" % (len(info["none"]), info["none"], info["n_empty"], len(info["changes"])))
    for u, was, now in info["changes"]:
        L.append("  naming change: %s %s -> %s" % (u, was, now))
    L.append("== FF1 OVERALL")
    L.append("  P_A %.4f (B0 as built, the bundle's eval_fl); P(A-refit) %.4f" % (R["P_A"], R["P_R"]))
    L.append("  %-28s %s" % ("D = P(A-refit) - P_A", GB.fs(R["ff1"])))
    L.append("  %-28s %s" % ("MMLU_PRO_LB stratum (desc.)", GB.fs(R["ff1_m"])))
    L.append("== PER ANCHOR (Delta_a on EVAL items of class a; impurity = 1 - declared-class share of the routed F-tree; FF2 uses the"
             " rows marked *; bridge = P(B-gt_0)_a - P(B_0)_a, descriptive)")
    for a in range(len(A["anchors"])):
        lab = A["label"][A["anchors"][a]]
        ks = info["by_anchor"][a]
        L.append("  %s %-58s k_a %d; EVAL %d; F-tree %d (declared %d, impurity %.4f); class TRAIN %d -> leaves %s; P_A %s, P(A-refit) %s,"
                 " Delta %s; bridge %s" % ("*" if S["incl"][a] else " ", lab, int(A["ka"][a]), int(S["n_ev"][a]), int(S["size"][a]),
                                           int(S["pure"][a]), S["imp"][a], len(A["gt"][a]), "/".join(str(int(info["assigned"][k])) for k in ks),
                                           _f(R["po"][a]), _f(R["pn"][a]), _f(R["delta"][a], "%+.4f"), _f(R["delta_bridge"][a], "%+.4f")))
    L.append("== VERDICTS")
    L += verdict_lines(R)
    L.append("== DESCRIPTIVE (never scored)")
    L.append("  bridge partial rho (P(B-gt_0)_a - P(B_0)_a vs impurity | log size, same m anchors): %s" % fmt_ps(R["bridge"]))
    L.append("== PREDICTIONS (priors; a band is HELD iff the point lies in it, endpoints inclusive)")
    obs = {"P1 D": R["ff1"]["d"], "P2 FF2 rho": R["ff2"]["rho"],
           "P4 MMLU_PRO_LB D (descriptive)": R["ff1_m"]["d"] if R["ff1_m"] else None}
    for k in PRED:
        L.append(pred_line(k, obs[k]))
    v1, v2, fires = verdicts(R)
    words = {"FF1": "FAILED (REVERSED)" if v1 == "REVERSED" else v1, "FF2": v2, "F-FF": "FIRES" if fires else "DOES NOT FIRE"}
    for key, txt in PROB:
        L.append("PREDICTION %s verdict probabilities (%s): observed %s" % (key, txt, words[key]))
    L.append(WILL_NOT_SHOW)
    ms = _MACHINE[0]()
    L.append("machine state: free RAM %s GB; admitted PIDs %s; BLAS threads %s" % (
        "%.1f" % ms["free_ram_gb"] if ms.get("free_ram_gb") is not None else "unknown", ms.get("pids"), ms.get("blas")))
    return "\n".join(L) + "\n"


def _f(x, fmt="%.4f"):
    return "n/a" if x != x else fmt % x


def pins_lines(o):
    o_ = ["%s script %s blob:%s (LF); pinned modules: %s" % (TAG, os.path.basename(__file__), blob_lf(os.path.abspath(__file__)),
                                                             ", ".join("%s blob:%s" % (n, p[:8]) for n, p in PINS))]
    return o_ + DSC.pins_lines(o)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--root", default=None, help="checkout holding experiment_results/ (default: this script's checkout)")
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        print("pool %s (selftest: synthetic fixtures only; the pool is not read)" % REG["pool"])
        print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
        print("[SCRIPT] %s blob:%s (LF)" % (os.path.basename(__file__), blob_lf(os.path.abspath(__file__))))
        try:
            selftest()
        except AssertionError:
            return 1
        return 0
    if a.mutants:
        return run_mutants()
    root = a.root or _ROOT[0]
    outp = a.out or GB.P(root, cfg()["out"])
    with _hooks(root):
        DSC.guard_paths(a.lane, root, outp)
        rc, txt = _POOL_GUARD[0](cfg()["pool"])
        first = "POOL %s (B0-2 pool check rc %d): %s" % (cfg()["pool"], rc, txt.replace("\n", " | "))
        out(first)
        if rc != 0:
            refuse("the B0-2 pool check of %s failed: %s" % (cfg()["pool"], txt))
        if a.run and os.path.exists(outp):
            refuse("%s exists; the outcome is write-once" % outp)
        out("%s cost: 0 calls, 0 builds; CPU estimate 5-20 min single thread (I1's KC / U-global x 5 seeds, B x 5 seeds, B-gt, one"
            " refit, 2 bootstraps of B %d); root %s" % (TAG, G.BOOT_B, root))
        o = GB.load_objects(root)
        A = DSC.load_anchors(o)
        DSC.check_r3_support(o, A)
        ident = GB.check_i1(GB.identity_arms(o))
        d2 = DSC.depth2_identity(o, ident)
        DSC.check_i4(o, A)
        idn = identity_ff(o, A, ident)
        if a.dry_run:
            c = cfg()
            for ln in pins_lines(o):
                out(ln)
            out("%s DENOMINATORS: EVAL %d / %d components; TRAIN %d; per source %s" % (
                TAG, len(o["ye"]), len(set(o["comp"].tolist())), len(o["yt"]),
                ", ".join("%s %d/%d/%d" % ((s,) + c["support_eval"][s] + (c["support_train"][s],)) for s in c["sources"])))
            out("%s FF2 m %d (split anchors %d; >= %d EVAL items of the declared class); split anchors below the threshold: %s" % (
                TAG, int(idn["S"]["incl"].sum()), int((A["ka"] > 1).sum()), c["min_eval"],
                ["%s (%d)" % (A["label"][A["anchors"][x]], int(idn["S"]["n_ev"][x])) for x in range(len(A["anchors"]))
                 if A["ka"][x] > 1 and not idn["S"]["incl"][x]]))
            out("%s I0-I5 (g13_breakdown) PASSED; I1 PASSED (SEEN): %s" % (TAG, json.dumps(ident["i1_got"], sort_keys=True)))
            out("%s depth 2 PASSED (SEEN): %s; I2 / I3 / I4 / R3 support PASSED" % (TAG, json.dumps(d2, sort_keys=True)))
            out("%s FITSET-FAITHFUL identity PASSED (SEEN, of record): %s; F-tree declared-class purity %d / %d (POSTRUN W2)" % (
                TAG, json.dumps(idn["got"], sort_keys=True), idn["purity"][0], idn["purity"][1]))
            ms = _MACHINE[0]()
            out("%s machine state: free RAM %s GB; admitted PIDs %s" % (
                TAG, "%.1f" % ms["free_ram_gb"] if ms.get("free_ram_gb") is not None else "unknown", ms.get("pids")))
            out("%s dry-run: NO new statistic computed or printed (A-refit not fitted)" % TAG)
            return 0
        R = compute(o, A, idn)
        body = "\n".join(pins_lines(o)) + "\n" + render(R, o, A, ident, d2, idn)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, "x", encoding="utf-8", newline="\n") as f:
        f.write(first + "\n" + body)
    out(body.rstrip("\n"))
    out("%s wrote %s (write-once)" % (TAG, outp))
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _u(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


# per split anchor: (name, n1 at p, n2 at q, foreign z at r, drag t, EVAL at p, EVAL at w)
_F_ANCHORS = (("a", 20, 20, 10, 1.5, 20, 10), ("b", 30, 20, 5, 1.5, 20, 20), ("c", 20, 20, 16, 1.5, 25, 5),
              ("d", 20, 30, 4, 0.25, 20, 10), ("e", 25, 20, 8, 0.25, 20, 10), ("f", 20, 20, 12, 1.5, 15, 15))


def _ff_spec(variant="F", dim=24):
    """Hand-built geometry (g13_breakdown fixture format; see the module docstring for every expected value)."""
    e = np.eye(dim)
    zz = e[21]
    anchors = [(n, a, b, k, (0.25 if variant == "N" else t), ep, ew) for (n, a, b, k, t, ep, ew) in _F_ANCHORS]
    mm = [("n00000001", 0, None, False, _u(np.ones(dim)), "MMLU_PRO_LB")]
    train, evals = [], []
    nid = [1]

    def new():
        nid[0] += 1
        return "n%08d" % nid[0]
    for i, (n, n1, n2, k, t, ep, ew) in enumerate(anchors):
        p, q, r = e[3 * i], e[3 * i + 1], e[3 * i + 2]
        cl = "MMLU_PRO_LB/" + n
        an = new()
        mm.append((an, 1, "n00000001", False, _u(p + q + 0.5 * r), cl))
        mm.append((new(), 2, an, True, p, "Emergent %s1" % n))
        mm.append((new(), 2, an, True, _u(q + t * r), "Emergent %s2" % n))
        train += [(cl, p, n1), (cl, q, n2), ("MMLU_PRO_LB/z", r, k)]
        evals += [(cl, p, ep), (cl, _u(q + 0.8 * zz), ew)]
    pa, pb = e[0], e[3]
    train.append(("MMLU_PRO_LB/a", _u(pb + 0.3 * pa), 6))
    evals.append(("MMLU_PRO_LB/a", _u(pb + 0.3 * pa), 25))
    pg, qg = e[18], e[19]                      # anchor g: L2 receives no declared-class item
    an = new()
    mm.append((an, 1, "n00000001", False, _u(pg + qg), "MMLU_PRO_LB/g"))
    mm.append((new(), 2, an, True, pg, "Emergent g1"))
    mm.append((new(), 2, an, True, qg, "Emergent g2"))
    train += [("MMLU_PRO_LB/g", pg, 20), ("MMLU_PRO_LB/z", qg, 5)]
    evals.append(("MMLU_PRO_LB/g", pg, 10))
    if variant == "F":
        evals.append(("MMLU_PRO_LB/g", _u(qg + 0.3 * pg), 10))
    mm.append((new(), 1, "n00000001", True, zz, "MMLU_PRO_LB/z"))
    train.append(("MMLU_PRO_LB/z", zz, 200))
    evals.append(("MMLU_PRO_LB/z", zz, 20))
    bbh = [("n00000001", 0, None, False, _u(e[22] + e[23]), "BBH"),
           ("n00000002", 1, "n00000001", True, e[22], "BBH/u"),
           ("n00000003", 1, "n00000001", True, e[23], "BBH/v")]
    train += [("BBH/u", e[22], 20), ("BBH/v", e[23], 20), ("BBH/v", _u(e[23] + 0.8 * e[22]), 10)]
    evals += [("BBH/u", e[22], 20), ("BBH/v", e[23], 20)] + ([("BBH/v", _u(e[23] + 1.1 * e[22]), 10)] if variant == "F" else [])
    evals.append(("BBH/v", _u(e[23] + 2.0 * e[22]), 10))
    return dict(members={"mmlu_pro_lb": ("MMLU_PRO_LB", mm), "bbh": ("BBH", bbh)}, train=train, evals=evals, descent_wrong={},
                noise=0.02, dim=dim)


def _fixture_tables(variant):
    """Hand tables: anchor -> (k_a, max depth, F-tree, B-anc, class TRAIN)."""
    T = {}
    ft = {"a": 50, "b": 61, "c": 56, "d": 54, "e": 53, "f": 52}
    cls = {"a": 46, "b": 50, "c": 40, "d": 50, "e": 45, "f": 40}
    for n in ft:
        T["MMLU_PRO_LB/" + n] = (2, 3, ft[n], ft[n], cls[n])
    T["MMLU_PRO_LB/g"] = (2, 3, 25, 25, 20)
    T["MMLU_PRO_LB/z"] = (1, 2, 200, 200, 260)
    T["BBH/u"] = (1, 2, 20, 20, 20)
    T["BBH/v"] = (1, 2, 30, 30, 30)
    return T


def _groups(variant):
    """EVAL group index (position in the spec's evals) by role."""
    ev = _ff_spec(variant)["evals"]
    names = [c for c, _v, _n in ev]
    g = {"w": {}, "p": {}}
    for i, (n, *_r) in enumerate(_F_ANCHORS):
        g["p"][n], g["w"][n] = 2 * i, 2 * i + 1
    g["probe"] = 12
    g["g_p"] = 13
    g["g_q"] = 14 if variant == "F" else None
    g["bbh_bad"] = len(ev) - 1
    g["v_shift"] = len(ev) - 2 if variant == "F" else None
    assert names[g["probe"]] == "MMLU_PRO_LB/a" and names[g["g_p"]] == "MMLU_PRO_LB/g"
    return g


def _hand_wrong(variant):
    """Hand-derived wrong EVAL groups for A (flatLeaf), A-refit and the depth-2 frontier (tree2)."""
    g = _groups(variant)
    drag = [n for (n, _a, _b, _k, t, _e, _w) in _F_ANCHORS if t > 1 and variant == "F"]
    opt = [x for x in (g["g_q"], g["v_shift"]) if x is not None]
    wA = [g["w"][n] for n in drag] + [g["probe"], g["bbh_bad"]] + opt
    wR = [g["probe"], g["bbh_bad"]] + ([g["g_q"]] if g["g_q"] is not None else [])
    w2 = [g["w"][n] for n in drag] + [g["probe"], g["bbh_bad"]] + ([g["v_shift"]] if g["v_shift"] is not None else [])
    return dict(A=wA, R=wR, tree2=w2)


def _tleaf(tr, variant):
    """The writer's TRAIN routing (argmax over the spec's leaves, sorted uids) -> anchor label per TRAIN item."""
    sp = _ff_spec(variant)
    nodes = {}
    for _m, (src, ns) in sp["members"].items():
        for (nid, dep, par, leaf, mu, lab) in ns:
            nodes["%s:%s" % (src, nid)] = dict(par=("%s:%s" % (src, par)) if par else None, leaf=leaf, mu=mu, lab=lab, dep=dep)
    leaves = sorted(u for u, n in nodes.items() if n["leaf"])
    LM = np.vstack([nodes[u]["mu"] for u in leaves])

    def anchor_of(u):
        return u if nodes[u]["dep"] == 1 else nodes[u]["par"]
    ta = [nodes[anchor_of(leaves[k])]["lab"] for k in np.argmax(tr["Xt"] @ LM.T, axis=1)]
    return np.array(ta), leaves, nodes, anchor_of


def _oracle_b(tr, variant, fit_of, seed):
    """Independent B / B-gt: per anchor spherical k-means at k_a on its fit set; TRAIN-majority naming over all cells; argmax filing."""
    Xt, yt, Xe, ye, classes = FM.unit_rows(tr["Xt"]), tr["yt"], FM.unit_rows(tr["Xe"]), tr["ye"], tr["classes"]
    ta, _l, _n, _a = _tleaf(tr, variant)
    T = _fixture_tables(variant)
    cents, owner = [], []
    for lab in sorted(T):                      # any fixed order: there are no argmax ties
        idx = np.flatnonzero(ta == lab) if fit_of == "ftree" else np.flatnonzero(np.array([classes[y] for y in yt]) == lab)
        k = T[lab][0]
        if k == 1:
            cents.append(_u(Xt[idx].sum(axis=0))[None, :])
        else:
            cents.append(FM.spherical_kmeans(Xt[idx], k, seed, max_iter=G.MAX_ITER)["centers"])
        owner += [classes.index(lab)] * len(cents[-1])
    C = np.vstack(cents)
    tc = np.argmax(Xt @ C.T, axis=1)
    names = []
    for j in range(len(C)):
        m = yt[tc == j]
        if len(m) == 0:
            names.append(owner[j])
            continue
        cnt = np.bincount(m, minlength=len(classes))
        names.append(min(np.flatnonzero(cnt == cnt.max()), key=lambda x: classes[x]))
    return (np.array(names)[np.argmax(Xe @ C.T, axis=1)] == ye).astype(np.int64)


def _ok_from(g, wrong):
    return (~np.isin(g, wrong)).astype(np.int64)


def _patch(variant):
    def p(fc, tr):
        g = tr["egrp"]
        W = _hand_wrong(variant)
        assert np.array_equal(_ok_from(g, W["A"]), tr["fl"]), "fixture %s: A's hand filing disagrees with the writer's" % variant
        Xt, Xe = FM.unit_rows(tr["Xt"]), FM.unit_rows(tr["Xe"])
        kcd = G.k_per_class(tr["classes"], tr["yt"], [d for d in tr["dom"].values() if d])
        kc = {s: G.kc_correct(Xt, tr["yt"], Xe, tr["ye"], kcd, s) for s in SEEDS}
        ncc = G.ncc_correct(Xt, tr["yt"], Xe, tr["ye"])
        lo, hi, _ = G.boot(tr["fl"] - kc[0], G.comp_groups(tr["ecomp"]))
        L = len([u for u in tr["leaves"] if tr["dom"][u]])
        ukm = []
        for s in SEEDS:
            C_, lab = GB._oracle_u(Xt, tr["yt"], Xe, tr["ye"], L, s, tr["classes"])
            ukm.append("%.4f" % (lab[np.argmax(Xe @ C_.T, axis=1)] == tr["ye"]).mean())
        fc["i1"] = dict(p_fl="%.4f" % tr["fl"].mean(), p_kc=tuple("%.4f" % kc[s].mean() for s in SEEDS),
                        d13="%+.4f" % (tr["fl"] - kc[0]).mean(), lo="%+.4f" % lo, hi="%+.4f" % hi, ukm=tuple(ukm), ncc="%.4f" % ncc.mean())
        fc["i2"] = "%.4f" % tr["fl"].mean()
        t2 = _ok_from(g, W["tree2"])
        lo2, hi2, _ = G.boot(t2 - ncc, G.comp_groups(tr["ecomp"]))
        fc["depth2"] = dict(n_f2=10, n_empty=0, p_tree2="%.4f" % t2.mean(), d2="%+.4f" % (t2 - ncc).mean(), lo2="%+.4f" % lo2,
                            hi2="%+.4f" % hi2)
        fc.update(anchors=_fixture_tables(variant), n_anchors=10, children={2: 7}, out=RES + "/fitset_faithful_s0_outcome.txt")
        unsplit = np.array([tr["classes"][y] in ("MMLU_PRO_LB/z", "BBH/u", "BBH/v") for y in tr["ye"]])
        comps = lambda m: len(set(tr["ecomp"][m].tolist()))    # noqa: E731
        fc["r3_ka"] = {(1, 1): (int(unsplit.sum()), comps(unsplit)), (2, 3): (int((~unsplit).sum()), comps(~unsplit)), (4, 7): (0, 0),
                       (8, 99): (0, 0)}
        fc["r3_depth"] = {2: int(unsplit.sum()), 3: int((~unsplit).sum())}
        okB = {s: _oracle_b(tr, variant, "ftree", s) for s in SEEDS}
        okBgt = _oracle_b(tr, variant, "gt", 0)
        pb = [float(okB[s].mean()) for s in SEEDS]
        ta, _l, _n, _a = _tleaf(tr, variant)
        pure = sum(int(sum(1 for j in np.flatnonzero(ta == lab) if tr["classes"][tr["yt"][j]] == lab)) for lab in set(ta.tolist()))
        fc["ff_ident"] = dict(p_a="%.4f" % tr["fl"].mean(), p_b0="%.4f" % pb[0], p_d0="%.4f" % kc[0].mean(),
                              bgt_d0="%+.4f" % (okBgt - kc[0]).mean(), spread_b="%.4f" % (max(pb) - min(pb)))
        fc["purity"] = (pure, len(tr["yt"]))
        tr["_okB"], tr["_okBgt"], tr["_spread_b"] = okB, okBgt, max(pb) - min(pb)
    return p


_FC_KEYS = ("pool", "expect", "members", "sources", "support_eval", "support_train", "leaves_by_source", "n_eval", "n_comp", "n_train",
            "n_leaves", "depths", "leaf_strata")


def _run(tmp, variant="F", argv=None, expect_refusal=None, patch_extra=None, sides_patch=None, pool=None):
    """Writes fixture `variant` with g13_breakdown's writer (this script's geometry) and executes main(), the real entry point."""
    saved_spec = GB._fixture_spec
    GB._fixture_spec = lambda v, dim=12: _ff_spec(variant)
    try:
        fc, sides, tr = GB._fixture_write(tmp, variant)
    finally:
        GB._fixture_spec = saved_spec
    fcd = dict(REG)
    fcd.update({k: v for k, v in fc.items() if k not in REG or k in _FC_KEYS})
    _patch(variant)(fcd, tr)
    if patch_extra:
        patch_extra(fcd, tr)
    if sides_patch:
        sides_patch(sides, tr)
    saved = (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _MACHINE[0])
    _CFG[0], _ROOT[0], _SIDES[0] = fcd, tmp, (lambda: sides)
    _POOL_GUARD[0] = pool if pool is not None else (lambda pool: (0, "[B0-2 stub] %s OK" % pool))
    _MACHINE[0] = lambda: {"free_ram_gb": 32.0, "pids": ["python.exe:4242"], "blas": "1"}
    buf = []
    try:
        res = main(argv or ["--run", "--lane", "r2"], out=buf.append)
    except SystemExit as e:
        res = str(e)
        if expect_refusal is None:
            raise
    finally:
        (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _MACHINE[0]) = saved
    if expect_refusal is not None:
        assert isinstance(res, str) and expect_refusal in res, (expect_refusal, res)
    return res, "\n".join(buf), fcd, tr


def _need(text, *needles):
    for nd in needles:
        assert nd in text, "missing: %r" % nd


def _st(tr, diff, m=None):
    diff = np.asarray(diff, dtype=np.float64)
    comp = tr["ecomp"]
    if m is not None:
        diff, comp = diff[m], comp[m]
    lo, hi, _ = G.boot(diff, G.comp_groups(comp))
    return float(diff.mean()), lo, hi


def _avg_ranks(x):
    """Independent average ranks (no scipy)."""
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def _oracle_partial(x, y, z):
    """Partial correlation of ranks as the correlation of the residuals after regressing each rank vector on (1, rank z)."""
    rx, ry, rz = _avg_ranks(x), _avg_ranks(y), _avg_ranks(z)
    D = np.column_stack([np.ones(len(rz)), rz])
    ex = rx - D @ np.linalg.lstsq(D, rx, rcond=None)[0]
    ey = ry - D @ np.linalg.lstsq(D, ry, rcond=None)[0]
    rho = float((ex * ey).sum() / np.sqrt((ex * ex).sum() * (ey * ey).sum()))
    m = len(x)
    zc, se = np.arctanh(rho), 1.0 / np.sqrt(m - 4)
    return rho, float(np.tanh(zc - 1.96 * se)), float(np.tanh(zc + 1.96 * se))


# hand values of fixture F (module docstring)
_F_DELTA = {"a": 10 / 55, "b": 20 / 40, "c": 5 / 30, "d": 0.0, "e": 0.0, "f": 15 / 30}
_F_IMP = {"a": 10 / 50, "b": 11 / 61, "c": 16 / 56, "d": 4 / 54, "e": 8 / 53, "f": 12 / 52}
_F_SIZE = {"a": 50, "b": 61, "c": 56, "d": 54, "e": 53, "f": 52}


def st_e2e_F(tmp):
    """--run on fixture F: every deciding value by hand (P_A, P(A-refit), D, MMLU D, per-anchor Delta / impurity / size, FF2 m and
    rho against an independent oracle), the bookkeeping, the verdict words, the predictions; write-once."""
    res, text, fc, tr = _run(tmp, "F")
    assert res == 0, res
    outp = GB.P(tmp, fc["out"])
    filed = open(outp, encoding="utf-8").read()
    assert filed.splitlines()[0] == "POOL pv2_fixture (B0-2 pool check rc 0): [B0-2 stub] pv2_fixture OK", filed.splitlines()[0]
    g = tr["egrp"]
    W = _hand_wrong("F")
    okA, okR = _ok_from(g, W["A"]), _ok_from(g, W["R"])
    assert len(g) == 315 and okA.sum() == 210 and okR.sum() == 270
    d, lo, hi = _st(tr, okR - okA)
    mm = tr["esrc"] == "MMLU_PRO_LB"
    dm, lom, him = _st(tr, okR - okA, mm)
    assert abs(d - 60 / 315) < 1e-12 and abs(dm - 50 / 255) < 1e-12
    names = sorted(_F_DELTA)
    x = [_F_DELTA[n] for n in names]
    y = [_F_IMP[n] for n in names]
    z = [np.log(_F_SIZE[n]) for n in names]
    rho, rlo, rhi = _oracle_partial(x, y, z)
    word2 = "HELD" if rlo > 0 else ("FAILED" if rhi <= 0 else "UNDETERMINED")
    _need(filed,
          "== DENOMINATORS: EVAL 315 items in %d CK-CLOSE components; TRAIN %d; split anchors 7 holding 14 leaves; FF2 m 6 (split anchors"
          " with >= 30 EVAL items of their declared class)" % (len(set(tr["ecomp"].tolist())), len(tr["yt"])),
          "  P_A 0.6667 (B0 as built, the bundle's eval_fl); P(A-refit) 0.8571",
          "  %-28s %+.4f  95%% [%+.4f, %+.4f] (n 315," % ("D = P(A-refit) - P_A", d, lo, hi),
          "  %-28s %+.4f  95%% [%+.4f, %+.4f] (n 255," % ("MMLU_PRO_LB stratum (desc.)", dm, lom, him),
          "== A-REFIT BOOKKEEPING: leaves receiving no declared-class item 1 ['MMLU_PRO_LB:n00000022'] (each keeps its vmfMu); cells named"
          " by the no-TRAIN fallback 0; naming changes against A's leaves CSV 0",
          "FF1: HELD (re-estimating A's leaf means on class-pure fit sets files EVAL better than A as built): D %+.4f, interval [%+.4f, %+.4f],"
          " spread_B %.4f (exact %.6f); interval wholly above 0 and D > spread_B" % (d, lo, hi, tr["_spread_b"], tr["_spread_b"]),
          "  support FF1: denominator 315 EVAL items / ",
          "FF2: %s" % word2,
          "rho %+.4f, 95%% [%+.4f, %+.4f] (Fisher z, SE_z 0.7071, m 6;" % (rho, rlo, rhi),
          "  support FF2: m 6 split anchors with >= 30 EVAL items (planning 30 of 32); SE_z 0.7071 (registered 0.196); MDE80 z 1.980"
          " (registered 0.549), rho 0.96 (registered about 0.50)",
          "FF1 and FF2 are read separately; no family-wise correction (disclosed).",
          "F-FF: DOES NOT FIRE: FF1's interval upper end %+.4f > 0" % hi,
          "PREDICTION P1 D +0.015 [-0.005, +0.035]: observed %+.4f -> FAILED" % d,
          "PREDICTION P2 FF2 rho +0.300 [-0.100, +0.650]: observed %+.4f -> %s" % (rho, "HELD" if -0.1 <= rho <= 0.65 else "FAILED"),
          "PREDICTION P4 MMLU_PRO_LB D (descriptive) +0.025 [+0.000, +0.050]: observed %+.4f -> FAILED" % dm,
          "PREDICTION FF1 verdict probabilities (HELD 0.30, UNDETERMINED 0.62, REVERSED 0.08): observed HELD",
          "PREDICTION FF2 verdict probabilities (HELD 0.20): observed %s" % word2,
          "PREDICTION F-FF verdict probabilities (fires 0.12): observed DOES NOT FIRE",
          LABEL_INFO[3], LABEL_INFO[4], LABEL_INFO[-1], CONFOUNDS[1], CONFOUNDS[2], CONFOUNDS[3], WILL_NOT_SHOW,
          "NOT APPLICABLE: wrong(established)")
    for n in names:
        row = [ln for ln in filed.splitlines() if ln.startswith("  * MMLU_PRO_LB/%s " % n)]
        assert len(row) == 1, (n, row)
        _need(row[0], "F-tree %d (" % _F_SIZE[n], "impurity %.4f)" % _F_IMP[n], "Delta %+.4f;" % _F_DELTA[n])
    rg = [ln for ln in filed.splitlines() if ln.startswith("    MMLU_PRO_LB/g ")]
    assert len(rg) == 1 and "EVAL 20;" in rg[0] and "F-tree 25 (declared 20, impurity 0.2000)" in rg[0], rg
    assert "class TRAIN 20 -> leaves 20/0;" in rg[0] and "Delta +0.0000" in rg[0], rg
    assert "naming change:" not in filed
    ra = [ln for ln in filed.splitlines() if ln.startswith("  * MMLU_PRO_LB/a ")][0]
    assert "class TRAIN 46 -> leaves 26/20;" in ra, ra
    rv = [ln for ln in filed.splitlines() if ln.startswith("    BBH/v ")]
    assert len(rv) == 1 and "EVAL 40;" in rv[0] and "P_A 0.5000, P(A-refit) 0.7500, Delta +0.2500;" in rv[0], rv
    # the descriptive bridge against the oracle B / B-gt
    db = []
    for n in names:
        m = np.array([tr["classes"][yy] == "MMLU_PRO_LB/" + n for yy in tr["ye"]])
        db.append(float(tr["_okBgt"][m].mean() - tr["_okB"][0][m].mean()))
    brho = _oracle_partial(db, y, z) if len(set(db)) > 1 else None
    bl = [ln for ln in filed.splitlines() if ln.startswith("  bridge partial rho")][0]
    if brho is None:
        assert "rho undefined" in bl, bl
    else:
        assert ("rho %+.4f, 95%% [%+.4f, %+.4f]" % brho) in bl, (bl, brho)
    assert "KNIFE-EDGE" not in filed
    _run(tmp, "F", expect_refusal="exists; the outcome is write-once")
    assert open(outp, encoding="utf-8").read() == filed
    return text


def st_e2e_N(tmp):
    """--run on fixture N: A-refit = A item-wise: FF1 UNDETERMINED at exactly 0, F-FF FIRES (upper end 0 <= 0), FF2 undefined."""
    res, text, fc, tr = _run(tmp, "N")
    assert res == 0, res
    filed = open(GB.P(tmp, fc["out"]), encoding="utf-8").read()
    _need(filed, "FF1: UNDETERMINED: D +0.0000, interval [+0.0000, +0.0000], spread_B",
          "FF2: UNDETERMINED: rho undefined (a constant ranked variable or a perfectly collinear covariate); m 6; no interval",
          "F-FF: FIRES (FF1's interval upper end +0.0000 <= 0): purity of the depth-2 fit sets is not the lever for the vMF rule's leaves"
          " at this n; the DSC bridge is read as a k-means artefact; checkpoint D's #8' is withdrawn. No recorded number is revised.",
          "PREDICTION P2 FF2 rho +0.300 [-0.100, +0.650]: observed none -> NOT SCORED (no estimate)",
          "PREDICTION F-FF verdict probabilities (fires 0.12): observed FIRES",
          "PREDICTION FF1 verdict probabilities (HELD 0.30, UNDETERMINED 0.62, REVERSED 0.08): observed UNDETERMINED",
          "leaves receiving no declared-class item 1")
    return text


def st_dry_run(tmp):
    res, text, fc, tr = _run(tmp, "F", argv=["--dry-run", "--lane", "r2"])
    assert res == 0, res
    lines = text.splitlines()
    assert lines[0].startswith("POOL pv2_fixture (B0-2 pool check rc 0)"), lines[0]
    _need(text, "[FF] script fitset_faithful.py blob:", "[DSC] script deep_split_compare.py blob:31af4cea",
          "[FF] DENOMINATORS: EVAL 315 / %d components; TRAIN %d; per source" % (len(set(tr["ecomp"].tolist())), len(tr["yt"])),
          "[FF] FF2 m 6 (split anchors 7; >= 30 EVAL items of the declared class); split anchors below the threshold: ['MMLU_PRO_LB/g (20)']",
          "I1 PASSED (SEEN)", "depth 2 PASSED (SEEN)", "FITSET-FAITHFUL identity PASSED (SEEN, of record)",
          "F-tree declared-class purity %d / %d" % fc["purity"], "dry-run: NO new statistic computed or printed", "cost: 0 calls")
    for bad in ("P(A-refit)", "FF1:", "FF2:", "F-FF", "PREDICTION", "Delta"):
        assert bad not in text, bad
    assert not os.path.exists(GB.P(tmp, fc["out"]))
    return text


def st_refusals(factory):
    """Every refusal on the --run path, by its message; no outcome written."""
    def ffp(**kw):
        return lambda fc, tr: fc.update(ff_ident=dict(fc["ff_ident"], **kw))
    cases = [
        (dict(argv=["--run", "--lane", "r1"]), "reads lane r2 objects only"),
        (dict(patch_extra=ffp(p_a="0.1234")), "IDENTITY: ['p_a']"),
        (dict(patch_extra=ffp(p_b0="0.1234")), "IDENTITY: ['p_b0']"),
        (dict(patch_extra=ffp(p_d0="0.1234")), "IDENTITY: ['p_d0']"),
        (dict(patch_extra=ffp(bgt_d0="+0.1234")), "IDENTITY: ['bgt_d0']"),
        (dict(patch_extra=ffp(spread_b="0.1234")), "IDENTITY: ['spread_b']"),
        (dict(patch_extra=lambda fc, tr: fc.update(purity=(fc["purity"][0] - 1, fc["purity"][1]))), "declared-class purity"),
        (dict(patch_extra=lambda fc, tr: fc.update(i1=dict(fc["i1"], p_fl="0.1234"))), "I1:"),
        (dict(patch_extra=lambda fc, tr: fc.update(depth2=dict(fc["depth2"], p_tree2="0.1234"))), "depth 2 (G13-BREAKDOWN)"),
        (dict(patch_extra=lambda fc, tr: fc.update(anchors=dict(fc["anchors"], **{"MMLU_PRO_LB/a": (2, 3, 49, 50, 46)}))), "I2/I3: 1 anchor"),
        (dict(patch_extra=lambda fc, tr: fc.update(r3_depth={**fc["r3_depth"], 3: 1})), "R3: true-anchor subtree depth 3"),
        (dict(sides_patch=lambda sides, tr: sides.update({sorted(k for k, v in sides.items() if v == "TRAIN")[0]: "EVAL"})), "not TRAIN"),
    ]
    for kw, needle in cases:
        tmp = factory()
        res, text, fc, tr = _run(tmp, "F", expect_refusal=needle, **kw)
        assert not os.path.exists(GB.P(tmp, fc["out"])), needle
    # the assignment guard: a declared-class item landing outside its anchor refuses
    g = globals()
    saved = g["assign_leaves"]

    try:
        g["assign_leaves"] = lambda o, X, ks: np.full(len(X), (max(ks) + 1) % len(o["leaves"]))
        tmp = factory()
        _run(tmp, "F", expect_refusal="assigned to a leaf outside the anchor")
    finally:
        g["assign_leaves"] = saved
    # the pool check: its line printed FIRST, then the refusal
    tmp = factory()
    buf = []
    sv = (_CFG[0], _ROOT[0], _POOL_GUARD[0])
    _CFG[0], _ROOT[0] = dict(REG), tmp
    _POOL_GUARD[0] = lambda pool: (1, "stub failure")
    try:
        try:
            main(["--run", "--lane", "r2"], out=buf.append)
            raise AssertionError("pool failure not refused")
        except SystemExit as e:
            assert "the B0-2 pool check" in str(e), str(e)
    finally:
        _CFG[0], _ROOT[0], _POOL_GUARD[0] = sv
    assert buf and buf[0].startswith("POOL pv2_1575de61bb20e977 (B0-2 pool check rc 1): stub failure"), buf
    assert len(buf) == 1, buf
    return True


def st_pool(factory):
    """The REAL g13_breakdown.pool_check_v2 executed through main() under this script's hooks; only v2_union_pool.py's child is
    replaced (argv asserted). A 7-byte -wal refuses with the POOL line first and nothing after it; the pass prints the child lines."""
    import types
    calls = []

    def child(rc, lines):
        def fake(argv, **kw):
            calls.append(list(argv))
            return types.SimpleNamespace(returncode=rc, stdout="\n".join(lines) + "\n", stderr="")
        return types.SimpleNamespace(run=fake)
    good = ["[UNION-POOL] pool pv2_fixture recomputed from 3 DBs; expected pv2_fixture", "[UNION-POOL] every check passed (fixture)"]
    body = b'{"pool": "pv2_fixture"}\n'

    def setup(tmp, wal=0):
        db = os.path.join(tmp, "side_fixture.db")
        open(db, "wb").close()
        if wal:
            with open(db + "-wal", "wb") as f:
                f.write(b"x" * wal)
        with open(os.path.join(tmp, "engine_pool_fixture.json"), "wb") as f:
            f.write(body)

        def patch(fc, tr):
            fc.update(guard_dbs=(db,), pool_file="engine_pool_fixture.json", pool_file_sha256_lf=hashlib.sha256(body).hexdigest())
        return patch
    saved_sp = GB.subprocess
    try:
        tmp = factory()
        GB.subprocess = child(0, good)
        res, text, fc, tr = _run(tmp, "F", argv=["--dry-run", "--lane", "r2"], expect_refusal="the B0-2 pool check of pv2_fixture failed",
                                 patch_extra=setup(tmp, 7), pool=GB.pool_check_v2)
        assert text.splitlines()[0].startswith("POOL pv2_fixture (B0-2 pool check rc 1): ") and "side_fixture.db-wal is 7 bytes" in text
        assert len(text.splitlines()) == 1 and not calls, text
        tmp = factory()
        res, text, fc, tr = _run(tmp, "F", argv=["--dry-run", "--lane", "r2"], patch_extra=setup(tmp, 0), pool=GB.pool_check_v2)
    finally:
        GB.subprocess = saved_sp
    assert res == 0, res
    assert len(calls) == 1 and calls[-1][1].endswith("v2_union_pool.py") and calls[-1][2:5] == ["--dry-run", "--pool", "pv2_fixture"]
    assert text.splitlines()[0].startswith("POOL pv2_fixture (B0-2 pool check rc 0): " + good[0] + " | " + good[1]), text.splitlines()[0]
    _need(text, "FITSET-FAITHFUL identity PASSED", "dry-run: NO new statistic")
    return True


def _synth(d=0.02, lo=0.01, hi=0.03, bar=0.0125, rho=0.3, rlo=-0.1, rhi=0.6, m=30):
    st = dict(d=d, lo=lo, hi=hi, se=0.0045, deff=1.2, n=6139, G=5628, n_eff=5100.0, mde=0.0126, disc=0.1)
    r = dict(rho=rho, lo=rlo, hi=rhi, m=m, se_z=1 / np.sqrt(m - 4) if m > 4 else float("nan"), plain=rho)
    R = {"ff1": st, "spread_b": bar, "ff2": r}
    return "\n".join(verdict_lines(R))


def st_branches():
    """Every FF1 / FF2 / F-FF branch printed with its values; the boundaries of each clause."""
    L = _synth()
    _need(L, "FF1: HELD (re-estimating A's leaf means on class-pure fit sets files EVAL better than A as built): D +0.0200, interval"
             " [+0.0100, +0.0300], spread_B 0.0125 (exact 0.012500); interval wholly above 0 and D > spread_B",
          "  support FF1: denominator 6139 EVAL items / 5628 CK-CLOSE components; SE 0.00450 (registered 0.00446); DEFF 1.200 measured from"
          " the components (transported 1.223); n_eff 5100 (registered 5020); MDE80 0.0126 (registered 0.0125); discordance 0.1000"
          " (planning 0.10); effective bar max(MDE80, spread_B) 0.0126",
          "FF2: UNDETERMINED: rho +0.3000, 95% [-0.1000, +0.6000] (Fisher z, SE_z 0.1961, m 30; plain Spearman +0.3000); the interval"
          " contains 0",
          "  support FF2: m 30 split anchors with >= 30 EVAL items (planning 30 of 32); SE_z 0.1961 (registered 0.196); MDE80 z 0.549"
          " (registered 0.549), rho 0.50 (registered about 0.50)",
          "F-FF: DOES NOT FIRE: FF1's interval upper end +0.0300 > 0")
    # the spread conjunct: interval above 0 but D at the bar exactly -> UNDETERMINED; just above -> HELD
    _need(_synth(d=0.0125, lo=0.004, hi=0.02), "FF1: UNDETERMINED: D +0.0125")
    _need(_synth(d=0.0126, lo=0.004, hi=0.02), "FF1: HELD")
    _need(_synth(d=0.0130, lo=0.004, hi=0.02, bar=0.012543), "FF1: HELD")
    assert "KNIFE-EDGE" not in _synth(d=0.0130, lo=0.004, hi=0.02, bar=0.012543)
    _need(_synth(d=0.01252, lo=0.004, hi=0.02, bar=0.012543), "FF1: UNDETERMINED: D +0.0125", "KNIFE-EDGE")
    assert "KNIFE-EDGE" not in _synth(d=0.0200, lo=0.004, hi=0.03, bar=0.012543)
    # REVERSED needs both: wholly below 0 and D < -bar
    _need(_synth(d=-0.02, lo=-0.03, hi=-0.01), "FF1: FAILED (REVERSED) (A as built files EVAL better than its class-pure refit): D -0.0200",
          "F-FF: FIRES (FF1's interval upper end -0.0100 <= 0)")
    _need(_synth(d=-0.010, lo=-0.03, hi=-0.001), "FF1: UNDETERMINED: D -0.0100", "F-FF: FIRES")
    # F-FF at the boundary: upper end exactly 0 fires; just above does not
    _need(_synth(d=-0.005, lo=-0.01, hi=0.0), "F-FF: FIRES (FF1's interval upper end +0.0000 <= 0)")
    _need(_synth(d=-0.005, lo=-0.01, hi=0.0001), "F-FF: DOES NOT FIRE")
    # FF2 branches: HELD on lower > 0; FAILED on upper <= 0 (including exactly 0); undefined at m <= 4
    _need(_synth(rho=0.6, rlo=0.2, rhi=0.8), "FF2: HELD (the per-anchor gain tracks the routed fit set's impurity beyond its size):"
          " rho +0.6000, 95% [+0.2000, +0.8000]", "; lower end > 0")
    _need(_synth(rho=-0.6, rlo=-0.8, rhi=0.0), "FF2: FAILED: rho -0.6000, 95% [-0.8000, +0.0000]", "upper end <= 0")
    _need(_synth(rho=0.0, rlo=0.0, rhi=0.3), "FF2: UNDETERMINED: rho +0.0000, 95% [+0.0000, +0.3000]")
    r4 = partial_spearman([1, 2, 3, 4], [1, 3, 2, 4], [1, 1, 2, 2])
    assert r4["lo"] != r4["lo"] and v_ff2(r4) == "UNDETERMINED", r4
    L4 = _synth(rho=r4["rho"], rlo=float("nan"), rhi=float("nan"), m=4)
    _need(L4, "FF2: UNDETERMINED: rho %+.4f; interval undefined (m 4 <= 4" % r4["rho"], "SE_z undefined (m <= 4)")
    return True


def st_partial():
    """partial_spearman against hand values and the independent residual oracle; the size covariate matters."""
    r = partial_spearman([1, 2, 3, 4, 5, 6], [2, 1, 4, 3, 6, 5], [1, 2, 3, 4, 5, 6])
    # ranks: rx = rz exactly -> r_xz = 1 -> undefined
    assert r["rho"] != r["rho"]
    x, y, z = [0.1, 0.4, 0.2, 0.9, 0.5, 0.3, 0.7], [3, 1, 2, 7, 4, 6, 5], [10, 30, 20, 40, 70, 50, 60]
    r = partial_spearman(x, y, z)
    o = _oracle_partial(x, y, z)
    assert abs(r["rho"] - o[0]) < 1e-12 and abs(r["lo"] - o[1]) < 1e-12 and abs(r["hi"] - o[2]) < 1e-12, (r, o)
    # hand: ranks x = (1,4,2,7,5,3,6), y = (3,1,2,7,4,6,5), z = (1,3,2,4,7,5,6); r_xy = 1 - 6*sum d^2/(n(n^2-1))
    rxy = 1 - 6 * sum((a - b) ** 2 for a, b in zip((1, 4, 2, 7, 5, 3, 6), (3, 1, 2, 7, 4, 6, 5))) / (7 * 48)
    assert abs(r["plain"] - rxy) < 1e-12, (r["plain"], rxy)
    assert abs(r["rho"] - r["plain"]) > 0.01, "the covariate must matter on this example"
    assert abs(r["se_z"] - 1 / np.sqrt(3)) < 1e-12
    # average ranks on ties
    r = partial_spearman([0, 0, 1, 2, 2, 3], [1, 2, 3, 4, 5, 6], [6, 1, 5, 2, 4, 3])
    o = _oracle_partial([0, 0, 1, 2, 2, 3], [1, 2, 3, 4, 5, 6], [6, 1, 5, 2, 4, 3])
    assert abs(r["rho"] - o[0]) < 1e-12
    # a constant variable is undefined (nan), and its verdict UNDETERMINED
    rc = partial_spearman([0] * 6, [1, 2, 3, 4, 5, 6], [1, 3, 2, 5, 4, 6])
    assert rc["rho"] != rc["rho"] and v_ff2(rc) == "UNDETERMINED", rc
    return True


CASES = (("e2e_F", "fixture F --run: every deciding value by hand; write-once", "tmp"),
         ("e2e_N", "fixture N --run: D = 0, F-FF FIRES, FF2 undefined", "tmp"),
         ("dry_run", "--dry-run: pins, denominators, identity; no statistic, no file", "tmp"),
         ("refusals", "every refusal (identity, I1-I4, sides, guard, pool line first)", "factory"),
         ("pool", "the real B0-2 pool check through main()", "factory"),
         ("branches", "every verdict / falsifier branch and boundary", "plain"),
         ("partial", "partial Spearman vs hand and an independent oracle", "plain"))
_FN = {"e2e_F": st_e2e_F, "e2e_N": st_e2e_N, "dry_run": st_dry_run, "refusals": st_refusals, "pool": st_pool,
       "branches": st_branches, "partial": st_partial}


def selftest(only=None, quiet=False):
    import tempfile
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="ff_")
        made.append(d)
        return d
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(factory()) if kind == "tmp" else fn(factory)
                if not quiet:
                    print("  ok   %-9s %s" % (name, desc))
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    print("  FAIL %-9s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:400]))
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): one temporary edit each (in memory); KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed, base, control_ok = 0, {}, True
    for name, edits, tests in MUTANTS:
        mut = head
        for old, new in edits:
            if mut.count(old) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times (must be exactly 1): %r" % (TAG, name, mut.count(old), old[:80]))
            mut = mut.replace(old, new)
        key = tuple(sorted(tests))
        if key not in base:
            base[key] = _exec_selftest(src, tests)
        res = _exec_selftest(mut + tail, tests)
        k = res is not True and base[key] is True
        if name.startswith("M00"):
            control_ok = res is True and base[key] is True
            print("  %-58s tests %-18s original %-4s control %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "SURVIVED (as it must)" if control_ok else "KILLED (harness broken)"))
            continue
        killed += int(k)
        print("  %-58s tests %-18s original %-4s mutant %-8s %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:80]), flush=True)
    n_real = sum(1 for m in MUTANTS if not m[0].startswith("M00"))
    print("MUTANTS: %d of %d KILLED; control %s" % (killed, n_real, "survived" if control_ok else "KILLED"))
    return 0 if killed == n_real and control_ok else 1


def _exec_selftest(src, tests):
    ns = {"__name__": "fitset_faithful_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


NL = chr(10)
MUTANTS = (
    ("M00 control (no-op edit)", [("def f_ff(hi):", "def f_ff(hi):")], ["branches", "e2e_F"]),
    ("M01 EVAL rows of the class enter the refit (wrong side)", [('        X = o["Xt"][fit]' + NL,
                                                                   '        X = np.vstack([o["Xt"][fit], o["Xe"][o["ye"] == A["a_cls"][a]]])' + NL)],
     ["e2e_F"]),
    ("M02 refit set = routed F-tree (no change of fit set)", [('        fit = np.asarray(A["gt"][a], dtype=int)',
                                                              '        fit = np.asarray(A["ftree"][a], dtype=int)')], ["e2e_F"]),
    ("M03 nearest leaf searched outside the anchor", [("        kk = assign_leaves(o, X, ks)", "        kk = assign_leaves(o, X, list(range(len(leaves))))")],
     ["e2e_F"]),
    ("M04 refit cells named from EVAL", [('    ok, names, n_empty, _e = DSC.name_and_file(o, A, C, ca)',
                                          '    ok, names, n_empty, _e = DSC.name_and_file(dict(o, Xt=o["Xe"], yt=o["ye"]), A, C, ca)')], ["e2e_F"]),
    ("M05 FF1 spread conjunct dropped", [("    return DSC.v_spread(d, lo, hi, bar)", "    return DSC.v_spread(d, lo, hi, 0.0)")], ["branches"]),
    ("M06 FF2 without the size covariate (plain Spearman)", [("    rho = (rxy - rxz * ryz) / np.sqrt(den) if", "    rho = rxy if")],
     ["e2e_F", "partial"]),
    ("M07 spread_B min<->max", [("    sB = max(float(okB[s].mean()) for s in SEEDS) - min(float(okB[s].mean()) for s in SEEDS)",
                                 "    sB = min(float(okB[s].mean()) for s in SEEDS) - max(float(okB[s].mean()) for s in SEEDS)")], ["e2e_F"]),
    ("M08 only the first split anchor refit (first site only)", [('            C[k] = unit(X[m].sum(axis=0)) if m.any() else',
                                                                  '            C[k] = unit(X[m].sum(axis=0)) if (m.any() and a == int(np.flatnonzero(A["ka"] > 1)[0])) else')],
     ["e2e_F"]),
    ("M09 FF2 interval at m <= 4 (zero-support path)", [("    if rho == rho and m > 4:", "    if rho == rho and m > 2:"),
                                                        ('se_z=(1.0 / np.sqrt(m - 4)) if m > 4 else float("nan")', 'se_z=(1.0 / np.sqrt(abs(m - 4) + 1))')],
     ["branches"]),
    ("M10 unsplit anchor cell at its vmfMu, not the class mean (boundary)", [("            C[ks[0]] = unit(X.sum(axis=0))",
                                                                              '            C[ks[0]] = o["nodes"][leaves[ks[0]]]["mu"]')], ["e2e_F"]),
    ("M11 SE_z = 1 / sqrt(m - 3) (registered denominator changed)", [('se_z=(1.0 / np.sqrt(m - 4)) if m > 4', 'se_z=(1.0 / np.sqrt(m - 3)) if m > 4')],
     ["e2e_F", "branches"]),
    ("M12 F-FF silent when it does not fire (skip path)", [("""        L.append("F-FF: DOES NOT FIRE: FF1's interval upper end %+.4f > 0" % st["hi"])""", "        pass")],
     ["branches", "e2e_F"]),
    ("M13 F-FF on the lower end", [('    return v_ff1(st["d"], st["lo"], st["hi"], R["spread_b"]), v_ff2(R["ff2"]), f_ff(st["hi"])',
                                    '    return v_ff1(st["d"], st["lo"], st["hi"], R["spread_b"]), v_ff2(R["ff2"]), f_ff(st["lo"])')], ["branches"]),
    ("M14 F-FF strict (upper < 0)", [("    return bool(hi <= 0)", "    return bool(hi < 0)")], ["e2e_N", "branches"]),
    ("M15 FF2 FAILED on upper < 0, not <= 0", [('    if r["hi"] <= 0:', '    if r["hi"] < 0:')], ["branches"]),
    ("M16 FF2 decided by the point, not the interval", [('    if r["lo"] > 0:', '    if r["rho"] > 0:')], ["branches"]),
    ("M17 FF2 threshold >= 30 read as > 30", [('    incl = (A["ka"] > 1) & (n_ev >= cfg()["min_eval"])', '    incl = (A["ka"] > 1) & (n_ev > cfg()["min_eval"])')],
     ["e2e_F"]),
    ("M18 write-once removed (check and mode x)", [("        if a.run and os.path.exists(outp):", "        if False:"),
                                                   ('with open(outp, "x"', 'with open(outp, "w"')], ["e2e_F"]),
    ("M19 write-once check removed (mode x kept)", [("        if a.run and os.path.exists(outp):", "        if False:")], ["e2e_F"]),
    ("M20 identity refusal removed", [("    if bad:" + NL + '        refuse("IDENTITY:', "    if False:" + NL + '        refuse("IDENTITY:')], ["refusals"]),
    ("M21 purity identity removed", [('    if pur != tuple(c["purity"]):', "    if False:")], ["refusals"]),
    ("M22 pool refusal removed", [("        if rc != 0:" + NL + '            refuse("the B0-2', "        if False:" + NL + '            refuse("the B0-2')],
     ["refusals"]),
    ("M23 pool line not printed before the refusal", [("        out(first)" + NL + "        if rc != 0:" + NL,
                                                       "        if rc != 0:" + NL + "            refuse(txt)" + NL + "        out(first)" + NL + "        if rc != 0:" + NL)],
     ["refusals"]),
    ("M24 dry-run prints a statistic", [('            out("%s dry-run: NO new statistic computed or printed (A-refit not fitted)" % TAG)',
                                         '            out("P(A-refit) %.4f" % arm_refit(o, A)[0].mean())' + NL
                                         + '            out("%s dry-run: NO new statistic computed or printed (A-refit not fitted)" % TAG)')], ["dry_run"]),
    ("M25 identity P(B_0) read from seed 1", [('p_b0="%.4f" % okB[0].mean()', 'p_b0="%.4f" % okB[1].mean()')], ["e2e_F"]),
    ("M26 per-anchor Delta sign reversed", [("    dl, pn, po = per_anchor_delta(o, A, okR, okA)", "    dl, pn, po = per_anchor_delta(o, A, okA, okR)")], ["e2e_F"]),
    ("M27 FF1 D sign reversed", [('    R["ff1"] = GB.stat(okR - okA, comp)', '    R["ff1"] = GB.stat(okA - okR, comp)')], ["e2e_F"]),
    ("M28 MMLU stratum on the overall population", [("GB.stat((okR - okA)[mm], comp[mm]) if mm.any()", "GB.stat(okR - okA, comp) if mm.any()")],
     ["e2e_F"]),
    ("M29 DSC hooks keep DSC's own config", [("    DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = cfg(), root, _SIDES[0]",
                                              "    DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = DSC._CFG[0], root, _SIDES[0]")], ["e2e_F"]),
    ("M30 leaf with no item gets a zero mean (dropped), not its vmfMu", [('if m.any() else o["nodes"][leaves[k]]["mu"]',
                                                                           'if m.any() else 0.0 * o["nodes"][leaves[k]]["mu"]')], ["e2e_F"]),
    ("M31 NOT SCORED skipped on a NaN", [("    if obs is None or obs != obs:" + NL + '        return "PREDICTION %s: observed none',
                                          "    if obs is None:" + NL + '        return "PREDICTION %s: observed none')], ["e2e_N"]),
    ("M32 KNIFE-EDGE note omitted", [('    if min(bar, 0.0125) <= abs(st["d"]) <= max(bar, 0.0125):', "    if False:")], ["branches"]),
    ("M33 FF2 population includes unsplit anchors", [('    incl = (A["ka"] > 1) & (n_ev >= cfg()["min_eval"])', '    incl = (n_ev >= cfg()["min_eval"])')],
     ["e2e_F"]),
    ("M34 FF2 size covariate = class TRAIN count, not F-tree", [('    R["ff2"] = partial_spearman(dl[incl], S["imp"][incl], np.log(S["size"][incl]))',
                                                                '    R["ff2"] = partial_spearman(dl[incl], S["imp"][incl], np.log(np.array([len(x) for x in A["gt"]])[incl]))')],
     ["e2e_F"]),
    ("M35 Fisher interval at 1.645", [("Z95 = 1.96", "Z95 = 1.645")], ["e2e_F", "branches"]),
    ("M36 impurity and size from the declared-class set", [('    pure = np.array([int((o["yt"][A["ftree"][a]] == A["a_cls"][a]).sum()) for a in range(na)])',
                                                            '    size = np.array([len(A["gt"][a]) for a in range(na)])' + NL + '    pure = size.copy()')],
     ["e2e_F"]),
    ("M37 committed side map, not this script's, handed to the readers", [("    DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = cfg(), root, _SIDES[0]",
                                                                           "    DSC._CFG[0], DSC._ROOT[0], DSC._SIDES[0] = cfg(), root, GB._committed_sides")],
     ["refusals"]),
    ("M38 FF2 on the bridge's Delta (B-gt - B) instead of A-refit - A", [('    R["ff2"] = partial_spearman(dl[incl],',
                                                                          '    R["ff2"] = partial_spearman(per_anchor_delta(o, A, idn["okBgt0"], idn["okB"][0])[0][incl],')],
     ["e2e_F"]),
    ("M39 assignment guard removed (outside-anchor search kept)", [("        if not set(kk.tolist()) <= set(ks):", "        if False:"),
                                                                   ("        kk = assign_leaves(o, X, ks)", "        kk = assign_leaves(o, X, list(range(len(leaves))))")],
     ["e2e_F", "refusals"]),
)

if __name__ == "__main__":
    sys.exit(main())
