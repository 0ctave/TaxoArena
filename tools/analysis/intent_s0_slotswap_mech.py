"""INTENT-S0-SLOTSWAP-MECH: on MASSIVE's 3,222 slot-swap variants of INTENT-TRANSFER-S0 C4, is a label-free cell flip predicted by
the origin's distance to its cell boundary (M1), by the share of tokens swapped (M2), and does the embedder move S (M3, descriptive)?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — INTENT-S0-SLOTSWAP-MECH: ..."
(span L22301-L22330, _as_of b909414, the registrar's commit). Kind zero-call (R-4). Zero judge calls; no build; no Ollama.

INSTRUMENT (verbatim S0): tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271 is imported UNCHANGED
(its LF blob is asserted at import; any other blob REFUSES). Its frozen readers do every read and fit: pin_check / raw_pin_check
(the pins of experiment_configs/intent_transfer_s0_pins.json; strict at --run: a null or different pin REFUSES), load_corpora,
text_set (the 3,222 variants are c4_variants' own, B7), check_meta / expected_meta, load_vectors (complete set; a missing vector
REFUSES), Space (slice 256, renormalised), and c4() itself: qwen3 256, K 60, seed 0, TRAIN-fit spherical k-means (fit_rows: the
TRAIN-ONLY guard). flip = 1 - c4's per-variant same-cell indicator at seed 0 (same0); c4's own S must reproduce the outcome of
record (S 0.75978 over n 3,222; s0_outcome.txt line "S0-C4") within 5e-6, else REFUSES (a different machinery, a failed
precondition). The regenerated variant rows (item id, slots, swapped, swapped slot types) must equal s0_c4_variants.csv row for row.

DEFINITIONS (the registration's; builder's readings SB1-SB5 below where it is silent).
  origin margin = cos(nearest centroid) - cos(second-nearest) of the EVAL ORIGIN against c4's seed-0 TRAIN-fit centroids (Cm0).
  swap share = swapped slot tokens / tokens.
  M1: D_Q = flip rate (lowest origin-margin quintile) - flip rate (highest). HELD iff lower(95% CI) >= 0.10; FAILED iff
      upper < 0.10; UNDETERMINED otherwise.
  M2: D_T = flip rate (top swap-share tercile) - flip rate (bottom). HELD iff lower > 0; FAILED iff upper <= 0; UNDETERMINED
      otherwise.
  M3 (DESCRIPTIVE-ONLY, never scored as a criterion): S_gemma - S_qwen3 and S_nomic - S_qwen3, paired on the same variants (c4 on
      each embedder's own 256 space), with a paired interval, printed against the seed spread 0.0335.
  Intervals: 95% percentile, CK-CLOSE-component cluster bootstrap (S0's comp_weights over the variants' components), B 2,000, ONE
      weight stream shared by M1, M2 and M3 (paired); groups fixed on the full data. F-SM1 fires iff M1 FAILED; F-SM2 iff M2 FAILED.
  Predictions (80% intervals, closed; probabilities with their Brier): D_Q 0.30 [0.20, 0.40], M1 HELD p 0.80; D_T +0.12 [+0.04,
      +0.20], M2 HELD p 0.65; S_gemma - S_qwen3 +0.04 [0.00, +0.08]; S_nomic - S_qwen3 -0.04 [-0.08, 0.00].
  PRINTED, DESCRIPTIVE: the M1 x M2 joint logistic (flip ~ 1 + z(margin) + z(share), IRLS); ceiling-normalised S per embedder,
      (S - co-filing) / (centroid stability - co-filing), all three from c4; S at K 18 / 60 / 120 (qwen3, seed 0); S over the top
      80% of origin margins; slot types with >= 80 variants (flip rate each); the realised group sizes and the Support (d) SE
      re-computed at them (R-1).

PRECONDITION (registrar R-2 of the brief): every one of the 3,222 variant texts has a vector in all three S0 embedding DBs
  (intent_emb_qwen3.db / _nomic / _gemma): printed per DB; a missing one REFUSES (a failed precondition, never an outcome).

BUILDER'S READINGS (printed; the registrar confirms or brackets):
  SB1 quantile groups (R-1, ties kept together): mid-rank rule, group = floor(G x (rank_avg - 0.5) / n), so tied values share a
      group; realised sizes printed. A group left EMPTY by ties gives no interval: the criterion reads UNDETERMINED (no interval:
      empty group) with the reason printed.
  SB2 tokens = whitespace tokens (str.split, S0 D6's tokeniser); swap share on the VARIANT side: tokens of the inserted values of
      the swapped slots / tokens of the variant text. The origin-side share (tokens of the replaced values / tokens of the origin)
      is printed beside as NOT OF RECORD.
  SB3 the swapped values are recovered by re-running c4_variants' draw (SEED_C4, same order); every recovered variant must render
      to c4_variants' text with the same swapped types, else REFUSES.
  SB4 bootstrap seed SEED_MECH = 20261003; a draw with zero weight in a compared group is undefined (dropped; count printed).
  SB5 selective stability: S over the variants in margin quintiles 2-5 (SB1's groups), i.e. the top 80%.

HYGIENE. Reads only S0's pinned DBs (ingest, qwen3, nomic, gemma: sha256-bytes, re-hashed before and after; a change REFUSES and
nothing is written), mode=ro&immutable=1 through S0's readers. No pool of record, no new embedding, no construction; --dry-run and
--run REFUSE while a java.exe runs (one heavy process; never beside a construction or site null). Threads: OMP/OPENBLAS/MKL = 1.

OUTPUT. experiment_results/intent_transfer/slotswap_mech_outcome.txt, WRITE-ONCE (mode "x"; an existing path REFUSES before any
read) and slotswap_mech_variants.csv beside (mode "x"; item ids, numbers, no text). --dry-run writes nothing and reads no flip.

LAUNCH (run-operator; zero calls; nothing else heavy running):
  python tools/analysis/intent_s0_slotswap_mech.py --selftest
  python tools/analysis/intent_s0_slotswap_mech.py --mutants
  python tools/analysis/intent_s0_slotswap_mech.py --dry-run   # pins, census, csv match, R-2 presence, shares, support; no flip
  python tools/analysis/intent_s0_slotswap_mech.py --run       # the file of record (write-once)
  (S0's DBs are read under TAXOARENA_DATA_ROOT, default the repo root; --db / --emb-dir override.)
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import csv             # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile; import scratch_dir        # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import intent_transfer_s0 as ITS      # noqa: E402  (imported unchanged; blob asserted)
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402

II, EA = ITS.II, ITS.EA
TAG = "[SLOTSWAP-MECH]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
EMBEDDERS = ITS.EMBEDDERS
SLICE = ITS.SLICE
BOOT_B = ITS.BOOT_B
SEED_MECH = 20261003
M1_BAR = 0.10
SEED_SPREAD = 0.0335
Q_GROUPS, T_GROUPS = 5, 3
TYPE_MIN = 80
S0_RECORD = {"S": 0.75978, "n": 3222, "components": 3207}
S0_TOL = 5e-6
PRED_DQ, P_M1 = (0.30, 0.20, 0.40), 0.80
PRED_DT, P_M2 = (0.12, 0.04, 0.20), 0.65
PRED_M3 = {"gemma": (0.04, 0.00, 0.08), "nomic": (-0.04, -0.08, 0.00)}
REG_RATES = {"M1": (0.40, 0.10), "M2": 0.21}
OUT_DIR = ITS.OUT_DIR
OUTCOME, VARCSV = "slotswap_mech_outcome.txt", "slotswap_mech_variants.csv"
S0_CSV = os.path.join(OUT_DIR, "s0_c4_variants.csv")
REG = ('docs/judge_v2_program.md "## Registered 2026-10-01 (before any code or call) — INTENT-S0-SLOTSWAP-MECH: ..." L22301-L22330 '
       '_as_of b909414; kind zero-call (R-4)')


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_its_blob():
    got = RO.git_blob_lf(ITS.__file__)
    if got != ITS_BLOB:
        refuse("intent_transfer_s0.py is blob %s, not the registered %s: S0's machinery must be imported unchanged" % (got, ITS_BLOB))
    return got


_foreign_heavy = ITS._foreign_heavy


def heavy_check():
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): never beside a construction or site null (one heavy process)" % heavy[:3])


def k_grid():
    kc, kf = II.GOLD_K["massive"]
    return (kc, kf, 120)


# ------------------------------------------------------------------------------------------------ variants: values, shares
def variant_values(C):
    """SB3: c4_variants' draw re-run (SEED_C4, same order) recording the drawn values. -> {origin row: (values, swapped flags)}."""
    tr = ITS.fit_rows(C, C.idx(SS.TRAIN), (SS.TRAIN,), "SLOTSWAP slot inventory (SB3 replica)")
    inv = {}
    for i in tr:
        for (_s, _e, t, v) in ITS.parse_annot(C.annot[i]):
            inv.setdefault((C.fine[i], t), set()).add(v)
    rng = np.random.default_rng(ITS.SEED_C4)
    out = {}
    for i in C.idx(SS.EVAL):
        slots = ITS.parse_annot(C.annot[i])
        if not slots:
            continue
        if SS.norm(ITS.render_annot(C.annot[i], [v for (_s, _e, _t, v) in slots])) != SS.norm(C.text[i]):
            continue
        vals, sw = [], []
        for (_s, _e, t, v) in slots:
            cands = sorted(x for x in inv.get((C.fine[i], t), ()) if SS.norm(x) != SS.norm(v))
            if cands:
                vals.append(cands[int(rng.integers(len(cands)))])
                sw.append(True)
            else:
                vals.append(v)
                sw.append(False)
        out[int(i)] = (vals, sw)
    return out


def shares(C, variants):
    """-> (share_variant, share_origin, rows) aligned with variants; REFUSES a recovered variant that does not render to c4's text."""
    vv = variant_values(C)
    sv, so, rows = [], [], []
    for i, txt, changed in variants:
        if i not in vv:
            refuse("variant of row %d has no recovered draw (SB3)" % i)
        vals, sw = vv[i]
        slots = ITS.parse_annot(C.annot[i])
        if ITS.render_annot(C.annot[i], vals) != txt or tuple(t for (_s, _e, t, _v), s in zip(slots, sw) if s) != tuple(changed):
            refuse("SB3: the recovered draw of row %d does not reproduce c4_variants' variant" % i)
        sv.append(sum(len(vals[j].split()) for j in range(len(slots)) if sw[j]) / float(len(txt.split())))
        so.append(sum(len(slots[j][3].split()) for j in range(len(slots)) if sw[j]) / float(len(C.text[i].split())))
        rows.append((C.ids[i], len(slots), len(changed), "|".join(changed)))
    return np.array(sv), np.array(so), rows


def csv_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        r = list(csv.reader(f))
    if r[0] != ["item_id", "n_slots", "n_swapped", "swapped_slot_types"]:
        refuse("%s: unexpected header %r" % (path, r[0]))
    return [(a, int(b), int(c), d) for a, b, c, d in r[1:]]


def presence(emb_dir, texts):
    """R-2: every variant text present in each embedding DB. -> {e: present count}; REFUSES any absence."""
    out = {}
    for e in EMBEDDERS:
        have = ITS.present_texts(ITS.emb_path(e, emb_dir))
        miss = [t for t in texts if t not in have]
        out[e] = len(texts) - len(miss)
        print("%s R-2 precondition: %d of %d variants have a vector in intent_emb_%s.db" % (TAG, out[e], len(texts), e))
        if miss:
            refuse("R-2 precondition: %d of %d variants have no vector in intent_emb_%s.db (a failed precondition)" % (len(miss), len(texts), e))
    return out


# ------------------------------------------------------------------------------------------------ statistics
def groups(x, G):
    """SB1: mid-rank groups; ties share a group. -> int array in 0..G-1."""
    from scipy.stats import rankdata
    x = np.asarray(x, dtype=np.float64)
    r = rankdata(x, method="average")
    return np.minimum((G * (r - 0.5) / len(x)).astype(int), G - 1)


def rate(flip, m, w=None):
    w = np.ones(len(flip)) if w is None else w
    den = float((w * m).sum())
    return float((w * m * flip).sum() / den) if den > 0 else float("nan")


def diff_stat(flip, g, hi_group, lo_group, w=None):
    return rate(flip, g == hi_group, w) - rate(flip, g == lo_group, w)


def boot_ci(draws):
    lo, hi = ITS.pct_ci(draws)
    nan = int(sum(1 for d in draws if not np.isfinite(d)))
    return lo, hi, nan


def m1_verdict(lo, hi):
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "UNDETERMINED (no interval: empty group)"
    if bool(lo >= M1_BAR):
        return "HELD"
    if bool(hi < M1_BAR):
        return "FAILED"
    return "UNDETERMINED"


def m2_verdict(lo, hi):
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "UNDETERMINED (no interval: empty group)"
    if bool(lo > 0):
        return "HELD"
    if bool(hi <= 0):
        return "FAILED"
    return "UNDETERMINED"


def in_interval(v, lo, hi):
    return "HELD" if (np.isfinite(v) and bool(lo <= float(v) <= hi)) else "FAILED"


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


def logistic(y, X, iters=50):
    """IRLS logistic regression; -> (beta, naive SE)."""
    X = np.column_stack([np.ones(len(y)), X])
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(X @ b)))
        W = np.clip(p * (1 - p), 1e-9, None)
        H = X.T @ (X * W[:, None])
        step = np.linalg.solve(H, X.T @ (y - p))
        b = b + step
        if np.max(np.abs(step)) < 1e-10:
            break
    p = 1.0 / (1.0 + np.exp(-(X @ b)))
    H = X.T @ (X * np.clip(p * (1 - p), 1e-9, None)[:, None])
    return b, np.sqrt(np.diag(np.linalg.inv(H)))


def z(x):
    x = np.asarray(x, dtype=np.float64)
    s = x.std()
    return (x - x.mean()) / (s if s > 0 else 1.0)


def mech(flip, margin, share, comp, flips_e=None, B=BOOT_B, seed=SEED_MECH):
    """THE deciding computation. flip, margin, share, comp aligned per variant; flips_e = {e: flip array} for M3 (paired)."""
    flip = np.asarray(flip, dtype=np.float64)
    gq, gt = groups(margin, Q_GROUPS), groups(share, T_GROUPS)
    DQ = diff_stat(flip, gq, 0, Q_GROUPS - 1)
    DT = diff_stat(flip, gt, T_GROUPS - 1, 0)
    flips_e = flips_e or {}
    S = {e: 1.0 - float(np.mean(f)) for e, f in flips_e.items()}
    dq, dt, d3 = [], [], {e: [] for e in flips_e if e != "qwen3"}
    for w in ITS.comp_weights(comp, B, np.random.default_rng(seed)):
        dq.append(diff_stat(flip, gq, 0, Q_GROUPS - 1, w))
        dt.append(diff_stat(flip, gt, T_GROUPS - 1, 0, w))
        for e in d3:
            d3[e].append(float((w * (flips_e["qwen3"] - flips_e[e])).sum() / w.sum()))
    qlo, qhi, qnan = boot_ci(dq)
    tlo, thi, tnan = boot_ci(dt)
    R = {"DQ": DQ, "DQ_lo": qlo, "DQ_hi": qhi, "DQ_nan": qnan, "DQ_se": float(np.nanstd(dq, ddof=1)),
         "DT": DT, "DT_lo": tlo, "DT_hi": thi, "DT_nan": tnan, "DT_se": float(np.nanstd(dt, ddof=1)),
         "q_sizes": [int((gq == k).sum()) for k in range(Q_GROUPS)], "t_sizes": [int((gt == k).sum()) for k in range(T_GROUPS)],
         "q_rates": [rate(flip, gq == k) for k in range(Q_GROUPS)], "t_rates": [rate(flip, gt == k) for k in range(T_GROUPS)],
         "gq": gq, "gt": gt, "n": len(flip), "B": B}
    R["M1"] = m1_verdict(qlo, qhi)
    R["M2"] = m2_verdict(tlo, thi)
    R["M3"] = {}
    for e in d3:
        lo, hi, _n = boot_ci(d3[e])
        R["M3"][e] = {"d": S[e] - S["qwen3"], "lo": lo, "hi": hi}
    return R


# ------------------------------------------------------------------------------------------------ lines
def _f(x, fmt="%.4f"):
    return fmt % x if isinstance(x, (float, int, np.floating)) and np.isfinite(x) else str(x)


def support_lines(n, comp, R=None, q_sizes=None, t_sizes=None):
    deff = ITS.kish(comp)
    ncomp = len(np.unique(comp))
    L = ["SUPPORT (a) deciding denominator: %d variants in %d CK-CLOSE components (registered 3,222 / 3,207), Kish mean cluster size "
         "%.4f; (b) DEFF %.4f measured on this cache (registered 1.0093); (c) n_eff = %d / %.4f = %.0f" % (n, ncomp, deff, deff, n, deff, n / deff)]
    if q_sizes is not None:
        p1, p5 = REG_RATES["M1"]
        se1 = np.sqrt(p1 * (1 - p1) / q_sizes[0] + p5 * (1 - p5) / q_sizes[-1]) * np.sqrt(deff)
        L.append("SUPPORT (d) R-1 M1 at the realised quintile sizes %s: SE = sqrt(%.2f/%d + %.2f/%d) x sqrt(DEFF) = %.4f (registered "
                 "0.0228), MDE80 %.4f (bar 0.10)" % (q_sizes, p1 * (1 - p1), q_sizes[0], p5 * (1 - p5), q_sizes[-1], se1, 2.8 * se1))
    if t_sizes is not None:
        v = REG_RATES["M2"]
        if t_sizes[0] > 0 and t_sizes[-1] > 0:
            se2 = np.sqrt(v / t_sizes[-1] + v / t_sizes[0]) * np.sqrt(deff)
            L.append("SUPPORT (d) R-1 M2 at the realised tercile sizes %s: SE = sqrt(%.2f/%d + %.2f/%d) x sqrt(DEFF) = %.4f (registered "
                     "0.0199), MDE80 %.4f (bar 0)" % (t_sizes, v, t_sizes[-1], v, t_sizes[0], se2, 2.8 * se2))
        else:
            L.append("SUPPORT (d) R-1 M2 at the realised tercile sizes %s: an EMPTY compared group (SB1); no SE" % (t_sizes,))
    if R is not None:
        L.append("SUPPORT measured: bootstrap SE(D_Q) %.4f, SE(D_T) %.4f (B %d; undefined draws %d / %d)"
                 % (R["DQ_se"], R["DT_se"], R["B"], R["DQ_nan"], R["DT_nan"]))
    return L


def criteria_lines(R):
    L = ["M1 (margin): D_Q = flip(lowest origin-margin quintile) - flip(highest) = %s, 95%% CI [%s, %s]: %s (HELD iff lower >= 0.10; "
         "FAILED iff upper < 0.10)" % (_f(R["DQ"]), _f(R["DQ_lo"]), _f(R["DQ_hi"]), R["M1"]),
         "M2 (surface share): D_T = flip(top swap-share tercile) - flip(bottom) = %s, 95%% CI [%s, %s]: %s (HELD iff lower > 0; FAILED "
         "iff upper <= 0)" % (_f(R["DT"]), _f(R["DT_lo"]), _f(R["DT_hi"]), R["M2"])]
    for e in ("gemma", "nomic"):
        m = R["M3"].get(e)
        if m is None:
            continue
        inside = bool(abs(m["d"]) <= SEED_SPREAD)
        L.append("M3 (DESCRIPTIVE-ONLY, never scored): S_%s - S_qwen3 = %s, paired 95%% CI [%s, %s]; %s the seed spread %.4f"
                 % (e, _f(m["d"], "%+.4f"), _f(m["lo"], "%+.4f"), _f(m["hi"], "%+.4f"), "inside" if inside else "outside", SEED_SPREAD))
    if R["M1"] == "FAILED":
        L.append("F-SM1: FIRED (M1 FAILED): the reading that margin-gated (selective) filing remedies F4 is overturned; F4's qualifier "
                 "would read \"surface-dominated\" (a reading; the thesis word is the author's, D2 OPEN; R-3)")
    else:
        L.append("F-SM1: NOT FIRED")
    if R["M2"] == "FAILED":
        L.append("F-SM2: FIRED (M2 FAILED): the slot-dominance explanation of S0 D6's short-text deficit is overturned")
    else:
        L.append("F-SM2: NOT FIRED")
    return L


def predictions_lines(R):
    L = ["PREDICTION D_Q %.2f [%.2f, %.2f] (80%%): %s (point %s)" % (PRED_DQ + (in_interval(R["DQ"], PRED_DQ[1], PRED_DQ[2]), _f(R["DQ"]))),
         "PREDICTION M1 HELD p %.2f: event %s, Brier %.4f" % (P_M1, R["M1"], brier(P_M1, R["M1"] == "HELD")),
         "PREDICTION D_T %+.2f [%+.2f, %+.2f] (80%%): %s (point %s)" % (PRED_DT + (in_interval(R["DT"], PRED_DT[1], PRED_DT[2]), _f(R["DT"]))),
         "PREDICTION M2 HELD p %.2f: event %s, Brier %.4f" % (P_M2, R["M2"], brier(P_M2, R["M2"] == "HELD"))]
    for e in ("gemma", "nomic"):
        m = R["M3"].get(e)
        if m is not None:
            pr = PRED_M3[e]
            L.append("PREDICTION S_%s - S_qwen3 %+.2f [%+.2f, %+.2f] (80%%): %s (point %s)" % ((e,) + pr + (in_interval(m["d"], pr[1], pr[2]), _f(m["d"], "%+.4f"))))
    return L


def descriptive_lines(D):
    L = ["DESCRIPTIVE realised groups (R-1, SB1): margin quintiles sizes %s, flip rates %s; swap-share terciles sizes %s, flip rates %s"
         % (D["q_sizes"], [_f(x) for x in D["q_rates"]], D["t_sizes"], [_f(x) for x in D["t_rates"]]),
         "DESCRIPTIVE origin-side swap share (NOT OF RECORD; SB2): D_T' = %s (terciles %s)" % (_f(D["DT_origin"]), D["t_sizes_origin"]),
         "DESCRIPTIVE joint logistic flip ~ 1 + z(margin) + z(share) (n %d): b_margin %s (SE %s), b_share %s (SE %s)"
         % (D["n"], _f(D["logit"][0][1]), _f(D["logit"][1][1]), _f(D["logit"][0][2]), _f(D["logit"][1][2]))]
    for e in EMBEDDERS:
        c = D["c4"][e]
        L.append("DESCRIPTIVE %s: S %.4f; centroid stability %.4f; co-filing %.4f; ceiling-normalised (S - co-filing) / (centroid - "
                 "co-filing) = %s" % (e, c["S"], c["centroid_stab"], c["cofile"], _f(D["ceil"][e])))
    L.append("DESCRIPTIVE qwen3 S at K %s: %s" % ("/".join(str(k) for k in D["kgrid"]), " / ".join(_f(D["S_k"][k]) for k in D["kgrid"])))
    L.append("DESCRIPTIVE selective stability (SB5): S over the top 80%% of origin margins = %s (n %d) vs all %s"
             % (_f(D["S_sel"]), D["n_sel"], _f(D["c4"]["qwen3"]["S"])))
    L.append("DESCRIPTIVE slot types with >= %d variants (flip rate, n): %s" % (TYPE_MIN, "; ".join("%s %s (%d)" % (t, _f(r), k) for t, r, k in D["types"]) or "none"))
    return L


DOES_NOT_SHOW = ("DOES NOT SHOW: anything about a tree leaf (k-means cells only); capability text; natural paraphrase (slot swaps only); "
                 "a causal mechanism (M1 and M2 are associations over fixed variants); embedder parity (M3 descriptive, no TOST); a "
                 "second split draw or k-means seeds beyond seed 0 for M1 / M2")


# ------------------------------------------------------------------------------------------------ assembly
def load_all(db, emb_dir, strict):
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    for e in EMBEDDERS:
        sha0[e] = ITS.pin_check(ITS.emb_path(e, emb_dir), "emb", strict, sub=e, label="intent_emb_%s.db" % e)
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    for e in EMBEDDERS:
        ITS.check_meta(ITS.emb_path(e, emb_dir), ITS.expected_meta(e, set_sha, len(texts), sha0["ingest_db"]))
    return sha0, CS, texts, derived


def census(C, variants, csv_path):
    sv, so, rows = shares(C, variants)
    want = csv_rows(csv_path)
    if rows != want:
        bad = [i for i, (a, b) in enumerate(zip(rows, want)) if a != b]
        refuse("the regenerated variant rows differ from %s (%d vs %d rows; first differing %s)" % (csv_path, len(rows), len(want), bad[:3]))
    comp = C.comp[np.array([i for i, _t, _c in variants], dtype=int)]
    print("%s variants: %d (rows equal to %s); components %d" % (TAG, len(variants), os.path.basename(csv_path), len(np.unique(comp))))
    return sv, so, rows, comp


def dry_run(db=None, emb_dir=None, csv_path=S0_CSV, strict=False):
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    print("%s pool of record: none read (S0's own DBs); zero calls; DRY RUN: nothing written, no flip read" % TAG)
    check_its_blob()
    heavy_check()
    sha0, CS, texts, derived = load_all(db, emb_dir, strict)
    C, variants = CS["massive"], derived["variants"]
    presence(emb_dir, [t for _i, t, _c in variants])
    sv, _so, rows, comp = census(C, variants, csv_path)
    gt = groups(sv, T_GROUPS)
    t_sizes = [int((gt == k).sum()) for k in range(T_GROUPS)]
    for ln in support_lines(len(variants), comp, t_sizes=t_sizes, q_sizes=[len(variants) // Q_GROUPS] * Q_GROUPS):
        print("%s %s" % (TAG, ln))
    print("%s DRY RUN complete: %d variants; swap-share terciles %s; nothing written" % (TAG, len(variants), t_sizes))
    return 0


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, csv_path=S0_CSV, record=S0_RECORD):
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    out, vout = os.path.join(out_dir, OUTCOME), os.path.join(out_dir, VARCSV)
    print("%s pool of record: none read (S0's own DBs); zero calls" % TAG)
    for p in (out, vout):
        if os.path.lexists(p):
            refuse("%s exists: the outcome of record is write-once" % p)
    check_its_blob()
    heavy_check()
    sha0, CS, texts, derived = load_all(db, emb_dir, True)
    C, variants = CS["massive"], derived["variants"]
    presence(emb_dir, [t for _i, t, _c in variants])
    sv, so, rows, comp = census(C, variants, csv_path)
    vecs = {e: ITS.load_vectors(ITS.emb_path(e, emb_dir), e, texts) for e in EMBEDDERS}
    del ITS.FIT_LOG[:]
    sp = {e: ITS.Space(vecs[e], C, SLICE) for e in EMBEDDERS}
    c4 = {e: ITS.c4(C, {"qwen3": sp[e]}, variants) for e in EMBEDDERS}
    q = c4["qwen3"]
    print("%s S0-C4 reproduction: S %.5f over n %d in %d components (record S %s, n %s)" % (TAG, q["S"], q["n"], q["components"],
                                                                                        record and record["S"], record and record["n"]))
    if record is not None and (abs(q["S"] - record["S"]) > S0_TOL or q["n"] != record["n"] or q["components"] != record["components"]):
        refuse("c4 does not reproduce the outcome of record (S %.5f n %d comps %d vs %s): a different machinery" % (q["S"], q["n"], q["components"], record))
    if q["n"] != len(variants):
        refuse("c4 scored %d of %d variants (a vector missing)" % (q["n"], len(variants)))
    oi = np.array([i for i, _t, _c in variants], dtype=int)
    Xo = sp["qwen3"].X[oi]
    top2 = np.sort(Xo @ q["Cm0"].T, axis=1)[:, -2:]
    margin = top2[:, 1] - top2[:, 0]
    flips = {e: 1.0 - c4[e]["same0"] for e in EMBEDDERS}
    flip = flips["qwen3"]
    R = mech(flip, margin, sv, comp, flips)
    # descriptive
    D = {"q_sizes": R["q_sizes"], "q_rates": R["q_rates"], "t_sizes": R["t_sizes"], "t_rates": R["t_rates"], "n": R["n"], "c4": c4}
    go = groups(so, T_GROUPS)
    D["DT_origin"] = diff_stat(flip, go, T_GROUPS - 1, 0)
    D["t_sizes_origin"] = [int((go == k).sum()) for k in range(T_GROUPS)]
    try:
        D["logit"] = logistic(flip, np.column_stack([z(margin), z(sv)]))
    except np.linalg.LinAlgError:
        D["logit"] = (np.full(3, float("nan")), np.full(3, float("nan")))      # not estimable (printed as nan)
    D["ceil"] = {e: (c4[e]["S"] - c4[e]["cofile"]) / (c4[e]["centroid_stab"] - c4[e]["cofile"])
                 if c4[e]["centroid_stab"] != c4[e]["cofile"] else float("nan") for e in EMBEDDERS}
    D["kgrid"] = k_grid()
    Xv = sp["qwen3"].of([t for _i, t, _c in variants])
    D["S_k"] = {}
    for k in D["kgrid"]:
        if k == II.GOLD_K["massive"][1]:
            D["S_k"][k] = q["S"]
            continue
        Cm = ITS.km_fit(C, sp["qwen3"], k, 0, "SLOTSWAP S at K %d" % k)
        D["S_k"][k] = float(np.mean(ITS.assign(Xo, Cm) == ITS.assign(Xv, Cm)))
    sel = R["gq"] >= 1
    D["S_sel"], D["n_sel"] = 1.0 - float(flip[sel].mean()), int(sel.sum())
    types = {}
    for j, (_i, _t, ch) in enumerate(variants):
        for t in set(ch):
            types.setdefault(t, []).append(j)
    D["types"] = sorted(((t, float(flip[js].mean()), len(js)) for t, js in types.items() if len(js) >= TYPE_MIN), key=lambda x: (-x[2], x[0]))
    audit = ITS.fit_audit()
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else ITS.emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))
    L = ["INTENT-S0-SLOTSWAP-MECH outcome (tools/analysis/intent_s0_slotswap_mech.py, blob %s; S0 machinery intent_transfer_s0.py blob %s, "
         "imported unchanged)" % (RO.git_blob_lf(os.path.abspath(__file__)), ITS_BLOB),
         "registration: " + REG,
         "zero judge calls; no build; no Ollama; pool of record: none read; pins re-checked before and after, unchanged: %s"
         % {k: v[:16] for k, v in sha0.items()},
         "builder's readings: SB1 mid-rank groups (ties together; an empty group gives no interval -> UNDETERMINED); SB2 whitespace "
         "tokens, variant-side share (origin side printed, NOT OF RECORD); SB3 values from c4_variants' draw re-run, asserted; SB4 "
         "bootstrap seed %d, undefined draws dropped and counted; SB5 selective = margin quintiles 2-5" % SEED_MECH,
         "R-2 precondition: %d of %d variants present in each of intent_emb_qwen3 / nomic / gemma" % (len(variants), len(variants)),
         "S0-C4 reproduced: S %.5f over n %d variants in %d components (record 0.75978 / 3,222 / 3,207)" % (q["S"], q["n"], q["components"]),
         "R-2 (disclosure): S by slots in the item was in the record before registration (c9c2fed W-5); M2 (token share) is not blind to it"]
    L += support_lines(R["n"], comp, R, R["q_sizes"], R["t_sizes"]) + [audit]
    L += criteria_lines(R) + predictions_lines(R) + descriptive_lines(D) + [DOES_NOT_SHOW]
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(vout, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "component", "margin", "share_variant", "share_origin", "flip_qwen3", "flip_nomic", "flip_gemma"])
        for j, (i, _t, _c) in enumerate(variants):
            w.writerow([C.ids[i], int(comp[j]), "%.6f" % margin[j], "%.6f" % sv[j], "%.6f" % so[j]] + [int(flips[e][j]) for e in EMBEDDERS])
    print("%s wrote %s (write-once, of record)" % (TAG, out))
    return R, D, out


# ------------------------------------------------------------------------------------------------ selftest fixture
FX_INTENTS = 16
FX_PER = 120


def _fx_massive_rows():
    """16 intents x 120 synthetic rows, 1-3 slots of three types; slot values of 1-3 tokens, intent-specific; carriers separated by
    distinct literals so a test can recover the values by regex (independent of the draw)."""
    rows = []
    rng = np.random.default_rng(11)
    for f in range(FX_INTENTS):
        for j in range(FX_PER):
            ns = 1 + j % 3
            parts = ["massive f%02d item %d" % (f, j // 2)]
            for s in range(ns):
                k = int(rng.integers(4))
                val = " ".join(["val%dx%dy%d" % (f, s, k)] + ["tok"] * (k % 3))
                if s == 2:                                # one value per intent: never swapped (a variant "2 of 3")
                    val = "fixed%d tok tok" % f
                parts.append("[slot_%d : %s]" % (s, val))
                parts.append("sep%d" % s + " pad" * int(rng.integers(0, 4)))
            annot = " ".join(parts)
            text = ITS.render_annot(annot, [v for (_a, _b, _t, v) in ITS.parse_annot(annot)])
            rows.append(dict(corpus="massive", orig_split="train", orig_idx="%d_%d" % (f, j), text=text, coarse="c%d" % (f % 4),
                             fine="massive_f%02d" % f, is_oos=0, annot=annot))
    return rows


def build_fixture(td, plant):
    """plant 'A': flips only on LOOSE-cloud origins (low margin), more often at a high swap share; plant 'B': flips only on TIGHT
    origins (high margin), more often at a LOW share. nomic: no flip; gemma: qwen3's flips plus 10% more."""
    raw = [dict((k, r[k]) for k in ("corpus", "orig_split", "orig_idx", "text", "coarse", "fine", "is_oos", "annot"))
           for r in ITS._fixture_rows() if r["corpus"] != "massive"]
    rows = II.assign(raw + _fx_massive_rows())
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    meta = {}
    for C in CS.values():
        for i in np.nonzero(C.kept)[0]:
            meta[C.text[i]] = (C.name, -1 if C.oos[i] else int(C.fine[i][-2:]), "oos" if C.oos[i] else "item")
    C = CS["massive"]
    var = derived["variants"]
    vv = variant_values(C)
    share = {}
    for i, t, _c in var:
        vals, sw = vv[i]
        share[t] = sum(len(vals[j].split()) for j in range(len(vals)) if sw[j]) / float(len(t.split()))
    sh = np.array([share[t] for _i, t, _c in var])
    srank = {t: (np.searchsorted(np.sort(sh), share[t], side="left") + 0.5) / len(sh) for _i, t, _c in var}
    ingest_sha = II.file_sha(db)
    for e in EMBEDDERS:
        dim = EA.EG.NATIVE_DIM[ITS.MODEL[e]]
        V = ITS._planted(meta, dim, e)
        r = np.random.default_rng(99)
        for i, t, _c in var:
            o = C.text[i]
            f = int(C.fine[i][-2:])
            rc = np.random.default_rng(int(ITS.hashlib.sha256(("cloud" + o).encode()).hexdigest()[:8], 16))
            cloud = f - 1 if (f % 2 == 1 and f < 8 and rc.random() < 0.35) else f
            loose = cloud % 2 == 0 and cloud < 8
            u = float(np.random.default_rng(int(ITS.hashlib.sha256(("flip" + t).encode()).hexdigest()[:8], 16)).random())
            if plant == "A":
                p = (0.2 + 0.7 * srank[t]) if loose else 0.0
            else:
                p = (0.9 - 0.7 * srank[t]) if not loose else 0.0
            if e == "gemma":
                p = min(1.0, p + 0.10)
            if e == "nomic":
                p = 0.0
            if u < p:
                tgt = (cloud + 9) % FX_INTENTS
                V[t] = 1.0 * np.eye(dim)[20 + tgt % 4] + 3.0 * np.eye(dim)[tgt] + 0.05 * r.normal(size=dim)
            else:
                V[t] = V[o] + 0.001 * r.normal(size=dim)
        for c, ps in derived["pairs"].items():
            for i, j, t in ps:
                V[t] = V[CS[c].text[i]] + V[CS[c].text[j]]
        p = ITS.emb_path(e, td)
        con = sqlite3.connect(p)
        con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
        con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(ITS.expected_meta(e, set_sha, len(texts), ingest_sha),
                                                                              model_digest="stub").items()))
        con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(V[t], dtype=">f4").tobytes()) for t in texts])
        con.commit()
        con.close()
    cp = os.path.join(td, "s0_c4_variants.csv")
    with open(cp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id", "n_slots", "n_swapped", "swapped_slot_types"])
        for i, _t, ch in var:
            w.writerow([C.ids[i], len(ITS.parse_annot(C.annot[i])), len(ch), "|".join(ch)])
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db),
                   "emb": {e: II.file_sha(ITS.emb_path(e, td)) for e in EMBEDDERS}}, fh)
    return {"td": td, "db": db, "csv": cp, "pins": pins, "n": len(var)}


def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    lines = [ln[len(TAG) + 1:] if ln.startswith(TAG + " ") else ln for ln in out.splitlines()]
    got = [ln for ln in lines if ln.startswith(prefix)]
    return got[0] if got else ""


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K (4 / 16), the fixture's pins file, no heavy process; all restored."""
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0])
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        try:
            yield
        finally:
            g["_foreign_heavy"] = saved[0]
            ITS.PINS_FILE_OVERRIDE[0] = saved[1]


def make_fixtures(td):
    out = {}
    for plant in ("A", "B"):
        d = os.path.join(td, plant)
        os.makedirs(d)
        with ITS.fixture_scope():
            out[plant] = build_fixture(d, plant)
    return out


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if fixture is None:
        with tempfile.TemporaryDirectory() as td:
            _selftest(sel, ok, td, make_fixtures(td))
    else:
        _selftest(sel, ok, fixture[0], fixture[1])
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _independent(fx):
    """An independent recomputation of the deciding numbers on a fixture (own k-means call, own margins, own regex share, own groups)."""
    import re
    CS = ITS.load_corpora(fx["db"])
    C = CS["massive"]
    var = ITS.c4_variants(C)[0]
    vec = {}
    con = sqlite3.connect(fx["db"].replace(II.DB_NAME, "intent_emb_qwen3.db"))
    for t, b in con.execute("SELECT query, vector FROM embeddings"):
        vec[t] = np.frombuffer(b, dtype=">f4")[:SLICE].astype(np.float64)
    con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    tr = [i for i in C.idx(SS.TRAIN)]
    Xtr = U(np.array([vec[C.text[i]] for i in tr]))
    Cm = ITS.skmeans(Xtr, II.GOLD_K["massive"][1], 0)
    Xo = U(np.array([vec[C.text[i]] for i, _t, _c in var]))
    Xv = U(np.array([vec[t] for _i, t, _c in var]))
    flip = (np.argmax(Xo @ Cm.T, 1) != np.argmax(Xv @ Cm.T, 1)).astype(float)
    s = np.sort(Xo @ Cm.T, 1)
    margin = s[:, -1] - s[:, -2]
    share = []
    for i, t, ch in var:
        slots = ITS.parse_annot(C.annot[i])
        lits = re.split(r"\[[^\[\]]*\]", C.annot[i])
        pat = "^" + "(.*?)".join(re.escape(x) for x in lits) + "$"
        got = re.match(pat, t).groups()
        sw = [SS.norm(a) != SS.norm(v) for a, (_s, _e, _ty, v) in zip(got, slots)]
        share.append(sum(len(a.split()) for a, w in zip(got, sw) if w) / float(len(t.split())))
    share = np.array(share)

    def grp(x, G):
        order = np.argsort(x, kind="mergesort")
        r = np.empty(len(x))
        xs = x[order]
        k = 0
        while k < len(x):
            m = k
            while m + 1 < len(x) and xs[m + 1] == xs[k]:
                m += 1
            r[order[k:m + 1]] = (k + m) / 2.0 + 1.0
            k = m + 1
        return np.minimum(np.floor(G * (r - 0.5) / len(x)).astype(int), G - 1)
    gq, gt = grp(margin, 5), grp(share, 3)
    DQ = flip[gq == 0].mean() - flip[gq == 4].mean()
    DT = flip[gt == 2].mean() - flip[gt == 0].mean()
    return {"DQ": DQ, "DT": DT, "flip": flip, "margin": margin, "share": share, "n": len(var), "S": 1 - flip.mean()}


def _run(fx, tag, **kw):
    out_dir = os.path.join(fx["td"], "out_%s_%d" % (tag, len(os.listdir(fx["td"]))))
    args = dict(db=fx["db"], emb_dir=fx["td"], out_dir=out_dir, csv_path=fx["csv"], record=None)
    args.update(kw)
    with _scope(fx):
        o, err, res = _cap(lambda: main_run(**args))
    return o, err, res, out_dir


def _selftest(sel, ok, td, fx):
    g = globals()
    if sel("ST-CONST"):
        ok(check_its_blob() == ITS_BLOB, "ST-CONST intent_transfer_s0.py is the registered blob f662ceb (imported unchanged)")
        ok((M1_BAR, SEED_SPREAD, Q_GROUPS, T_GROUPS, BOOT_B, SLICE, TYPE_MIN) == (0.10, 0.0335, 5, 3, 2000, 256, 80) and
           k_grid() == (18, 60, 120) and II.GOLD_K["massive"] == (18, 60), "ST-CONST registered constants (bar 0.10, seed spread "
           "0.0335, quintiles / terciles, B 2,000, slice 256, K 18 / 60 / 120, slot types >= 80)")
        ok(S0_RECORD == {"S": 0.75978, "n": 3222, "components": 3207} and PRED_DQ == (0.30, 0.20, 0.40) and P_M1 == 0.80 and
           PRED_DT == (0.12, 0.04, 0.20) and P_M2 == 0.65 and PRED_M3 == {"gemma": (0.04, 0.00, 0.08), "nomic": (-0.04, -0.08, 0.00)},
           "ST-CONST the record (S 0.75978 / 3,222 / 3,207) and the registered predictions")
    if sel("ST-STATS"):
        x = np.array([5, 1, 1, 1, 2, 9, 9, 3, 4, 4])
        ok(groups(x, 5).tolist() == [3, 0, 0, 0, 1, 4, 4, 2, 3, 3], "ST-STATS SB1 mid-rank quintiles keep ties together: %s"
           % groups(x, 5).tolist())
        ok(groups(np.zeros(9), 3).tolist() == [1] * 9, "ST-STATS SB1 an all-tied share lands in the middle tercile (both ends empty)")
        flip = np.array([1, 1, 0, 0, 1, 0, 0, 0, 0, 0], dtype=float)
        gq = np.array([0, 0, 1, 1, 2, 3, 3, 4, 4, 4])
        ok(abs(diff_stat(flip, gq, 0, 4) - 1.0) < 1e-12 and abs(diff_stat(flip, gq, 4, 0) + 1.0) < 1e-12, "ST-STATS D = rate(hi "
           "group) - rate(lo group), the sign as registered")
        ok(abs(rate(flip, gq == 2, np.array([1, 1, 1, 1, 3, 1, 1, 1, 1, 1.0])) - 1.0) < 1e-12 and np.isnan(rate(flip, gq == 2, np.zeros(10))),
           "ST-STATS weighted rate; zero weight -> undefined")
        ok(m1_verdict(0.10, 0.30) == "HELD" and m1_verdict(0.0999, 0.30) == "UNDETERMINED" and m1_verdict(-0.2, 0.0999) == "FAILED"
           and m1_verdict(-0.2, 0.10) == "UNDETERMINED" and m1_verdict(float("nan"), 0.2).startswith("UNDETERMINED (no interval"),
           "ST-STATS M1: HELD iff lower >= 0.10 (at 0.10 HELD), FAILED iff upper < 0.10 (at 0.10 UNDETERMINED)")
        ok(m2_verdict(0.0001, 0.3) == "HELD" and m2_verdict(0.0, 0.3) == "UNDETERMINED" and m2_verdict(-0.3, 0.0) == "FAILED" and
           m2_verdict(-0.3, 0.0001) == "UNDETERMINED" and m2_verdict(0.1, float("nan")).startswith("UNDETERMINED (no interval"),
           "ST-STATS M2: HELD iff lower > 0 (at 0 UNDETERMINED), FAILED iff upper <= 0 (at 0 FAILED)")
        ok(m1_verdict(np.float64(0.1), np.float64(0.2)) == "HELD" and m2_verdict(np.float64(-0.1), np.float64(0.0)) == "FAILED",
           "ST-STATS verdicts on numpy scalars")
        ok(in_interval(0.20, 0.20, 0.40) == "HELD" and in_interval(0.40, 0.20, 0.40) == "HELD" and in_interval(0.1999, 0.20, 0.40) == "FAILED"
           and in_interval(float("nan"), 0, 1) == "FAILED", "ST-STATS prediction interval closed at both ends")
        ok(abs(brier(0.80, True) - 0.04) < 1e-12 and abs(brier(0.65, False) - 0.4225) < 1e-12, "ST-STATS Brier 0.04 / 0.4225")
        # mech on synthetic data with a known answer: flips iff margin in the lowest quintile, share irrelevant
        rr = np.random.default_rng(5)
        m = rr.random(1000)
        sh = rr.random(1000)
        fl = (m < np.quantile(m, 0.2)).astype(float)
        R = mech(fl, m, sh, np.arange(1000), {"qwen3": fl, "gemma": fl * 0, "nomic": fl}, B=200, seed=1)
        ok(abs(R["DQ"] - 1.0) < 1e-12 and R["M1"] == "HELD" and R["q_sizes"] == [200] * 5, "ST-STATS mech: flips confined to the "
           "lowest margin quintile -> D_Q 1.0, M1 HELD, quintiles 200 each")
        ok(abs(R["DT"]) < 0.08 and R["M2"] in ("UNDETERMINED", "FAILED") and abs(R["M3"]["gemma"]["d"] - 0.2) < 1e-12 and
           R["M3"]["nomic"]["d"] == 0.0 and R["M3"]["gemma"]["lo"] < 0.2 < R["M3"]["gemma"]["hi"] and R["M3"]["nomic"]["lo"] == R["M3"]["nomic"]["hi"] == 0.0, "ST-STATS mech: share irrelevant -> D_T ~ 0; M3 gemma +0.20 "
           "(paired CI around it), nomic 0 with a degenerate paired CI [0, 0]")
        fl2 = (m > np.quantile(m, 0.8)).astype(float)
        R2 = mech(fl2, m, sh, np.arange(1000), {"qwen3": fl2}, B=200, seed=1)
        ok(abs(R2["DQ"] + 1.0) < 1e-12 and R2["M1"] == "FAILED", "ST-STATS mech: flips in the HIGHEST quintile -> D_Q -1.0, M1 FAILED")
        fl3 = (np.argsort(np.argsort(sh)) >= 667).astype(float)
        R3 = mech(fl3, m, sh, np.arange(1000), {"qwen3": fl3}, B=200, seed=1)
        ok(abs(R3["DT"] - 1.0) < 1e-12 and R3["M2"] == "HELD" and R3["t_sizes"] == [333, 334, 333], "ST-STATS mech: flips in the top "
           "share tercile -> D_T 1.0, M2 HELD, terciles 333/334/333 (mid-rank rule)")
        fl4 = (sh < np.quantile(sh, 1 / 3.0)).astype(float)
        ok(mech(fl4, m, sh, np.arange(1000), {"qwen3": fl4}, B=200, seed=1)["M2"] == "FAILED", "ST-STATS mech: flips in the bottom "
           "tercile -> M2 FAILED")
        comp = np.repeat(np.arange(500), 2)
        Rc = mech(fl, m, sh, comp, {"qwen3": fl}, B=300, seed=2)
        Ri = mech(fl, m, sh, np.arange(1000), {"qwen3": fl}, B=300, seed=2)
        fl5 = np.zeros(1000)
        gq5 = groups(m, 5)
        for k, nf in ((0, 50), (1, 20), (2, 20), (3, 20), (4, 20)):
            fl5[np.nonzero(gq5 == k)[0][:nf]] = 1.0
        R5 = mech(fl5, m, sh, np.arange(1000), {"qwen3": fl5}, B=500, seed=4)
        ok(abs(R5["DQ"] - 0.15) < 1e-12 and R5["DQ_lo"] < 0.10 < R5["DQ"] and R5["M1"] == "UNDETERMINED", "ST-STATS mech: D_Q 0.15 "
           "with lower %.3f < 0.10 reads UNDETERMINED (the INTERVAL decides, never the point)" % R5["DQ_lo"])
        fl6 = np.zeros(1000)
        gt6 = groups(sh, 3)
        for k, nf in ((0, 30), (1, 30), (2, 40)):
            fl6[np.nonzero(gt6 == k)[0][:nf]] = 1.0
        R6 = mech(fl6, m, sh, np.arange(1000), {"qwen3": fl6}, B=500, seed=4)
        ok(abs(R6["DT"] - (40 / 333.0 - 30 / 333.0)) < 1e-12 and R6["DT_lo"] < 0 < R6["DT"] and R6["M2"] == "UNDETERMINED",
           "ST-STATS mech: D_T +0.030 with lower %.3f < 0 reads UNDETERMINED (the INTERVAL decides)" % R6["DT_lo"])
        ok(Rc["DT_se"] != Ri["DT_se"], "ST-STATS mech: the bootstrap resamples COMPONENTS (pairs sharing a component move together)")
        b, se = logistic(np.r_[np.zeros(50), np.ones(50)], np.r_[rr.normal(-1, 1, 50), rr.normal(1, 1, 50)][:, None])
        ok(b[1] > 0.5 and se[1] > 0, "ST-STATS logistic: positive slope on a separated pair of classes")
    # criteria / falsifier print paths on synthetic results (the real printer of the outcome)
    if sel("ST-LINES"):
        base = {"DQ": 0.3, "DQ_lo": 0.2, "DQ_hi": 0.4, "DT": 0.1, "DT_lo": 0.05, "DT_hi": 0.15, "M3": {"gemma": {"d": 0.05, "lo": 0.03, "hi": 0.07},
                                                                                                     "nomic": {"d": -0.01, "lo": -0.02, "hi": 0.0}}}
        for m1, m2 in (("HELD", "HELD"), ("FAILED", "FAILED"), ("UNDETERMINED", "UNDETERMINED"), ("UNDETERMINED (no interval: empty group)", "FAILED")):
            L = criteria_lines(dict(base, M1=m1, M2=m2))
            ok(any(x.startswith("M1 (margin):") and (": %s (HELD iff" % m1) in x for x in L), "ST-LINES M1 line prints %s" % m1)
            ok(any(x.startswith("M2 (surface share):") and (": %s (" % m2) in x for x in L), "ST-LINES M2 line prints %s" % m2)
            ok(("F-SM1: NOT FIRED" in L) == (m1 != "FAILED") and any(x.startswith("F-SM1: FIRED") for x in L) == (m1 == "FAILED"),
               "ST-LINES F-SM1 %s when M1 %s" % ("FIRED" if m1 == "FAILED" else "NOT FIRED", m1))
            ok(("F-SM2: NOT FIRED" in L) == (m2 != "FAILED") and any(x.startswith("F-SM2: FIRED") for x in L) == (m2 == "FAILED"),
               "ST-LINES F-SM2 %s when M2 %s" % ("FIRED" if m2 == "FAILED" else "NOT FIRED", m2))
        L = criteria_lines(dict(base, M1="HELD", M2="HELD"))
        ok("M3 (DESCRIPTIVE-ONLY, never scored): S_gemma - S_qwen3 = +0.0500, paired 95% CI [+0.0300, +0.0700]; outside the seed "
           "spread 0.0335" in L and any("S_nomic - S_qwen3 = -0.0100" in x and "inside the seed spread" in x for x in L),
           "ST-LINES M3 printed against the seed spread (outside / inside)")
        P = predictions_lines(dict(base, M1="HELD", M2="UNDETERMINED"))
        ok("PREDICTION D_Q 0.30 [0.20, 0.40] (80%): HELD (point 0.3000)" in P and "PREDICTION M1 HELD p 0.80: event HELD, Brier 0.0400" in P
           and "PREDICTION D_T +0.12 [+0.04, +0.20] (80%): HELD (point 0.1000)" in P and "PREDICTION M2 HELD p 0.65: event UNDETERMINED, "
           "Brier 0.4225" in P and "PREDICTION S_gemma - S_qwen3 +0.04 [+0.00, +0.08] (80%): HELD (point +0.0500)" in P and
           "PREDICTION S_nomic - S_qwen3 -0.04 [-0.08, +0.00] (80%): HELD (point -0.0100)" in P, "ST-LINES predictions scored with "
           "values (Brier on the HELD event; UNDETERMINED counts as not HELD)")
    if sel("ST-E2E"):
        for plant, want in (("A", ("HELD", "HELD")), ("B", ("FAILED", "FAILED"))):
            f = fx[plant]
            with _scope(f):
                ind = _independent(f)
            o, err, res, od = _run(f, plant)
            ok(err is None and res is not None, "ST-E2E fixture %s: --run completes (%s)" % (plant, err))
            R, D, out = res
            ok(abs(R["DQ"] - ind["DQ"]) < 1e-12 and abs(R["DT"] - ind["DT"]) < 1e-12 and R["n"] == ind["n"] == f["n"],
               "ST-E2E fixture %s: D_Q %.4f and D_T %.4f equal an independent recomputation (own k-means call, margins, regex shares, "
               "groups) over n %d" % (plant, R["DQ"], R["DT"], R["n"]))
            ok(abs(D["c4"]["qwen3"]["S"] - ind["S"]) < 1e-12, "ST-E2E fixture %s: c4's S equals the independent S %.4f" % (plant, ind["S"]))
            ok((R["M1"], R["M2"]) == want, "ST-E2E fixture %s: planted answer M1 %s / M2 %s (got %s / %s; D_Q %.3f [%.3f, %.3f], D_T %.3f "
               "[%.3f, %.3f])" % ((plant,) + want + (R["M1"], R["M2"], R["DQ"], R["DQ_lo"], R["DQ_hi"], R["DT"], R["DT_lo"], R["DT_hi"])))
            ok(_line(o, "M1 (margin):") == "M1 (margin): D_Q = flip(lowest origin-margin quintile) - flip(highest) = %.4f, 95%% CI [%.4f, "
               "%.4f]: %s (HELD iff lower >= 0.10; FAILED iff upper < 0.10)" % (R["DQ"], R["DQ_lo"], R["DQ_hi"], want[0]),
               "ST-E2E fixture %s: the M1 line prints the value and %s" % (plant, want[0]))
            ok((": %s (HELD iff lower > 0" % want[1]) in _line(o, "M2 (surface share):") and ("= %.4f," % R["DT"]) in _line(o, "M2 (surface share):"),
               "ST-E2E fixture %s: the M2 line prints the value and %s" % (plant, want[1]))
            fs = "F-SM1: FIRED" if want[0] == "FAILED" else "F-SM1: NOT FIRED"
            ok(_line(o, "F-SM1:").startswith(fs) and _line(o, "F-SM2:").startswith(fs.replace("SM1", "SM2")), "ST-E2E fixture %s: %s / "
               "F-SM2 printed accordingly" % (plant, fs))
            ok(D["c4"]["nomic"]["S"] == 1.0 and abs(R["M3"]["nomic"]["d"] - (1.0 - ind["S"])) < 1e-12, "ST-E2E fixture %s: M3 nomic "
               "(no planted flip) S 1.0, S_nomic - S_qwen3 = %.4f" % (plant, R["M3"]["nomic"]["d"]))
            ok(R["M3"]["gemma"]["d"] < 0 and ("S_gemma - S_qwen3 = %+.4f" % R["M3"]["gemma"]["d"]) in o, "ST-E2E fixture %s: M3 gemma "
               "(10%% more flips) negative and printed" % plant)
            ok(("PREDICTION M1 HELD p 0.80: event %s, Brier %.4f" % (want[0], 0.04 if want[0] == "HELD" else 0.64)) in o,
               "ST-E2E fixture %s: the M1 prediction's Brier" % plant)
            ok("R-2 precondition: %d of %d variants have a vector in intent_emb_gemma.db" % (f["n"], f["n"]) in o, "ST-E2E fixture %s: "
               "R-2 presence printed per DB" % plant)
            sel_ = ind["margin"] >= np.sort(ind["margin"])[0]
            ok(abs(D["S_sel"] - (1 - ind["flip"][R["gq"] >= 1].mean())) < 1e-12 and D["n_sel"] == int((R["gq"] >= 1).sum()) and sel_.all(),
               "ST-E2E fixture %s: selective stability over margin quintiles 2-5" % plant)
            ok(D["kgrid"] == (4, 16, 120) and D["S_k"][16] == D["c4"]["qwen3"]["S"] and all(0 <= D["S_k"][k] <= 1 for k in D["kgrid"]),
               "ST-E2E fixture %s: S at K 4 / 16 / 120 (the fixture's K_c / K_f / 120)" % plant)
            ok("TRAIN-ONLY:" in o and "0 with an EVAL row" in o, "ST-E2E fixture %s: TRAIN-ONLY audit printed, 0 EVAL rows in fits" % plant)
            with open(os.path.join(od, OUTCOME), encoding="utf-8") as fh:
                body = fh.read()
            with open(os.path.join(od, VARCSV), encoding="utf-8") as fh:
                vrows = list(csv.reader(fh))
            ok(DOES_NOT_SHOW in body and _line(o, "M1 (margin):") in body and len(vrows) == f["n"] + 1 and
               sum(int(r[5]) for r in vrows[1:]) == int(ind["flip"].sum()), "ST-E2E fixture %s: outcome + per-variant csv written (flips %d)"
               % (plant, int(ind["flip"].sum())))
            o2, err2, _r, _od = _run(f, plant, out_dir=od)
            with open(os.path.join(od, OUTCOME), encoding="utf-8") as fh:
                ok(err2 is not None and "write-once" in err2 and fh.read() == body, "ST-E2E fixture %s: a second --run REFUSES; the file "
                   "is unchanged" % plant)
    if sel("ST-REFUSE"):
        f = fx["A"]

        def refused(why, **kw):
            o, err, res, od = _run(f, "ref", **kw)
            return err is not None and why in err and not os.path.exists(os.path.join(od, OUTCOME))
        with _scope(f):
            ind = _independent(f)
        ok(refused("does not reproduce", record={"S": ind["S"] + 1e-4, "n": f["n"], "components": res_comp(f)}), "ST-REFUSE c4 not "
           "reproducing the record S (off by 1e-4, n and components right) REFUSES")
        ok(refused("does not reproduce", record={"S": ind["S"], "n": f["n"] + 1, "components": res_comp(f)}), "ST-REFUSE c4's n "
           "differing from the record REFUSES")
        o, err, res, od = _run(f, "rec", record={"S": ind["S"], "n": f["n"], "components": res_comp(f)})
        ok(err is None, "ST-REFUSE the record check passes on the reproduced S / n / components (%s)" % err)
        bad = os.path.join(f["td"], "bad.csv")
        with open(f["csv"], encoding="utf-8") as a, open(bad, "w", encoding="utf-8", newline="") as b:
            lines = a.read().splitlines()
            lines[3] = lines[3].rsplit(",", 1)[0] + ",zz"
            b.write("\n".join(lines) + "\n")
        ok(refused("differ from", csv_path=bad), "ST-REFUSE a variant row differing from s0_c4_variants.csv REFUSES")
        saved = g["_scope"]

        @contextlib.contextmanager
        def heavy_scope(fx_):
            with saved(fx_):
                g["_foreign_heavy"] = lambda: ['"java.exe","1"']
                yield
        g["_scope"] = heavy_scope
        try:
            ok(refused("foreign heavy"), "ST-REFUSE a running java.exe REFUSES the --run")
            with heavy_scope(f):
                o, err, _r = _cap(lambda: dry_run(f["db"], f["td"], f["csv"]))
            ok(err is not None and "foreign heavy" in err, "ST-REFUSE a running java.exe REFUSES the --dry-run")
        finally:
            g["_scope"] = saved
        # R-2: one variant missing from the gemma DB
        import shutil
        d2 = tempfile.mkdtemp(prefix="miss_", dir=f["td"])
        for e in EMBEDDERS:
            shutil.copy(ITS.emb_path(e, f["td"]), ITS.emb_path(e, d2))
        with _scope(f):
            var = ITS.text_set(ITS.load_corpora(f["db"]))[2]["variants"]
        con = sqlite3.connect(ITS.emb_path("gemma", d2))
        con.execute("DELETE FROM embeddings WHERE query = ?", (var[0][1],))
        con.commit()
        con.close()
        pins2 = os.path.join(d2, "pins2.json")
        with open(f["pins"]) as a:
            pj2 = json.load(a)
        pj2["emb"]["gemma"] = II.file_sha(ITS.emb_path("gemma", d2))
        with open(pins2, "w") as b:
            json.dump(pj2, b)
        o, err, res, od = _run(dict(f, pins=pins2), "miss", emb_dir=d2)
        ok(err is not None and "R-2 precondition: 1 of %d variants have no vector in intent_emb_gemma.db" % f["n"] in err,
           "ST-REFUSE R-2: one variant missing from the gemma DB REFUSES (%s)" % (err or "")[:80])
        with _scope(f):
            o, err, _r = _cap(lambda: presence(d2, [t for _i, t, _c in var]))
        ok(err is not None and "1 of %d variants have no vector in intent_emb_gemma.db" % f["n"] in err and
           "%d of %d variants have a vector in intent_emb_nomic.db" % (f["n"], f["n"]) in o, "ST-REFUSE R-2 presence check itself "
           "(nomic complete, gemma 1 missing)")
        # pins: a null pin refused by --run
        nul = os.path.join(f["td"], "pins_null.json")
        with open(f["pins"]) as a:
            pj = json.load(a)
        pj["emb"]["nomic"] = None
        with open(nul, "w") as b:
            json.dump(pj, b)
        o, err, res, od = _run(dict(f, pins=nul), "nul")
        ok(err is not None and "UNPINNED" in err, "ST-REFUSE a null pin REFUSES the --run")
        pj["emb"]["nomic"] = "0" * 64
        with open(nul, "w") as b:
            json.dump(pj, b)
        o, err, res, od = _run(dict(f, pins=nul), "mis")
        ok(err is not None and "!= the pinned" in err, "ST-REFUSE a different pin REFUSES the --run")
        # a DB changing during the readout
        real = II.file_sha
        calls = {"n": 0}

        def drift(p):
            calls["n"] += 1
            s = real(p)
            return s if calls["n"] <= 6 else "f" * 64
        II.file_sha = drift
        try:
            ok(refused("changed during the readout"), "ST-REFUSE an embedding DB sha changing during the readout REFUSES, nothing written")
        finally:
            II.file_sha = real
        # SB3 replica guard
        real_vv = g["variant_values"]
        g["variant_values"] = lambda C: {i: (["zz"] * len(v[0]), v[1]) for i, v in real_vv(C).items()}
        try:
            ok(refused("SB3"), "ST-REFUSE a recovered draw that does not render to c4's variant REFUSES")
        finally:
            g["variant_values"] = real_vv
        # dry run: nothing written, no flip read
        with _scope(f):
            o, err, _r = _cap(lambda: dry_run(f["db"], f["td"], f["csv"]))
        ok(err is None and ("DRY RUN complete: %d variants" % f["n"]) in o and "M1 (" not in o and "flip" not in o.replace("no flip read", ""),
           "ST-REFUSE --dry-run: census, R-2, shares and support; no flip, no verdict, nothing written")


def res_comp(f):
    with _scope(f):
        CS = ITS.load_corpora(f["db"])
        var = ITS.text_set(CS)[2]["variants"]
    return len(np.unique(CS["massive"].comp[[i for i, _t, _c in var]]))


MUTANTS = (
    ("M1 HELD at lower > 0.10", "    if bool(lo >= M1_BAR):\n", "    if bool(lo > M1_BAR):\n", ("ST-STATS",)),
    ("M1 FAILED at upper <= 0.10", "    if bool(hi < M1_BAR):\n", "    if bool(hi <= M1_BAR):\n", ("ST-STATS",)),
    ("M1 bar 0.05", "M1_BAR = 0.10\n", "M1_BAR = 0.05\n", ("ST-CONST",)),
    ("M2 HELD at lower >= 0", "    if bool(lo > 0):\n", "    if bool(lo >= 0):\n", ("ST-STATS",)),
    ("M2 FAILED at upper < 0", "    if bool(hi <= 0):\n", "    if bool(hi < 0):\n", ("ST-STATS",)),
    ("M1 decided on the point", "    R[\"M1\"] = m1_verdict(qlo, qhi)\n", "    R[\"M1\"] = m1_verdict(DQ, DQ)\n", ("ST-STATS", "ST-E2E")),
    ("M2 decided on the point", "    R[\"M2\"] = m2_verdict(tlo, thi)\n", "    R[\"M2\"] = m2_verdict(DT, DT)\n", ("ST-STATS", "ST-E2E")),
    ("D_Q sign flipped (highest - lowest)", "    DQ = diff_stat(flip, gq, 0, Q_GROUPS - 1)\n", "    DQ = diff_stat(flip, gq, Q_GROUPS - 1, 0)\n", ("ST-STATS", "ST-E2E")),
    ("D_Q lowest vs second-highest quintile", "    DQ = diff_stat(flip, gq, 0, Q_GROUPS - 1)\n", "    DQ = diff_stat(flip, gq, 0, Q_GROUPS - 2)\n", ("ST-STATS", "ST-E2E")),
    ("D_T bottom - top", "    DT = diff_stat(flip, gt, T_GROUPS - 1, 0)\n", "    DT = diff_stat(flip, gt, 0, T_GROUPS - 1)\n", ("ST-STATS", "ST-E2E")),
    ("CI draws of D_Q unweighted", "        dq.append(diff_stat(flip, gq, 0, Q_GROUPS - 1, w))\n", "        dq.append(diff_stat(flip, gq, 0, Q_GROUPS - 1))\n", ("ST-STATS", "ST-E2E")),
    ("bootstrap over variants, not components", "    for w in ITS.comp_weights(comp, B, np.random.default_rng(seed)):\n",
     "    for w in ITS.comp_weights(np.arange(len(flip)), B, np.random.default_rng(seed)):\n", ("ST-STATS",)),
    ("quintiles -> quartiles", "Q_GROUPS, T_GROUPS = 5, 3\n", "Q_GROUPS, T_GROUPS = 4, 3\n", ("ST-CONST",)),
    ("ties split by order (ordinal ranks)", "    r = rankdata(x, method=\"average\")\n", "    r = rankdata(x, method=\"ordinal\")\n", ("ST-STATS",)),
    ("margin from the variant, not the origin", "    top2 = np.sort(Xo @ q[\"Cm0\"].T, axis=1)[:, -2:]\n",
     "    top2 = np.sort(sp[\"qwen3\"].of([t for _i, t, _c in variants]) @ q[\"Cm0\"].T, axis=1)[:, -2:]\n", ("ST-E2E",)),
    ("margin = own cos only", "    margin = top2[:, 1] - top2[:, 0]\n", "    margin = top2[:, 1]\n", ("ST-E2E",)),
    ("margin from seed-1 centroids", "    top2 = np.sort(Xo @ q[\"Cm0\"].T, axis=1)[:, -2:]\n",
     "    top2 = np.sort(Xo @ ITS.km_fit(C, sp[\"qwen3\"], II.GOLD_K[\"massive\"][1], 1, \"m\").T, axis=1)[:, -2:]\n", ("ST-E2E",)),
    ("flip from nomic", "    flip = flips[\"qwen3\"]\n", "    flip = flips[\"nomic\"]\n", ("ST-E2E",)),
    ("share on the origin side decides", "    R = mech(flip, margin, sv, comp, flips)\n", "    R = mech(flip, margin, so, comp, flips)\n", ("ST-E2E",)),
    ("share counts every slot, not the swapped ones", "        sv.append(sum(len(vals[j].split()) for j in range(len(slots)) if sw[j]) / float(len(txt.split())))\n",
     "        sv.append(sum(len(vals[j].split()) for j in range(len(slots))) / float(len(txt.split())))\n", ("ST-E2E",)),
    ("share = swapped slot count / slots", "        sv.append(sum(len(vals[j].split()) for j in range(len(slots)) if sw[j]) / float(len(txt.split())))\n",
     "        sv.append(sum(sw) / float(len(slots)))\n", ("ST-E2E",)),
    ("SB3 replica guard removed", "        if ITS.render_annot(C.annot[i], vals) != txt or", "        if False and ITS.render_annot(C.annot[i], vals) != txt or", ("ST-REFUSE",)),
    ("csv comparison removed", "    if rows != want:\n", "    if False:\n", ("ST-REFUSE",)),
    ("record reproduction unchecked", "    if record is not None and (abs(q[\"S\"] - record[\"S\"]) > S0_TOL", "    if False and (abs(q[\"S\"] - record[\"S\"]) > S0_TOL", ("ST-REFUSE",)),
    ("record tolerance 1e-3", "S0_TOL = 5e-6\n", "S0_TOL = 1e-3\n", ("ST-REFUSE",)),
    ("R-2 presence check removed", "        if miss:\n            refuse(\"R-2", "        if False:\n            refuse(\"R-2", ("ST-REFUSE",)),
    ("R-2 checks the first DB only", "    for e in EMBEDDERS:\n        have = ITS.present_texts", "    for e in EMBEDDERS[:1]:\n        have = ITS.present_texts", ("ST-REFUSE",)),
    ("pins not strict at --run", "    sha0, CS, texts, derived = load_all(db, emb_dir, True)\n", "    sha0, CS, texts, derived = load_all(db, emb_dir, False)\n", ("ST-REFUSE",)),
    ("sha after-check skipped", "        if now != s:\n            refuse(\"%s sha256 changed", "        if False:\n            refuse(\"%s sha256 changed", ("ST-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("ST-REFUSE",)),
    ("outcome not write-once", [("        if os.path.lexists(p):\n            refuse(", "        if False:\n            refuse("),
                                ("    with open(out, \"x\", encoding", "    with open(out, \"w\", encoding"),
                                ("    with open(vout, \"x\", encoding", "    with open(vout, \"w\", encoding")], None, ("ST-E2E",)),
    ("F-SM1 fires on HELD", "    if R[\"M1\"] == \"FAILED\":\n        L.append(\"F-SM1: FIRED", "    if R[\"M1\"] == \"HELD\":\n        L.append(\"F-SM1: FIRED", ("ST-LINES",)),
    ("F-SM2 line never printed", "        L.append(\"F-SM2: FIRED (M2 FAILED)", "        (\"F-SM2: FIRED (M2 FAILED)", ("ST-LINES",)),
    ("M3 unpaired (gemma minus nomic)", "            d3[e].append(float((w * (flips_e[\"qwen3\"] - flips_e[e])).sum() / w.sum()))\n",
     "            d3[e].append(float((w * (flips_e[\"qwen3\"] - flips_e[e][::-1])).sum() / w.sum()))\n", ("ST-STATS",)),
    ("M3 seed spread inside/outside flipped", "        inside = bool(abs(m[\"d\"]) <= SEED_SPREAD)\n", "        inside = bool(abs(m[\"d\"]) > SEED_SPREAD)\n", ("ST-LINES",)),
    ("prediction interval open", "    return \"HELD\" if (np.isfinite(v) and bool(lo <= float(v) <= hi)) else \"FAILED\"",
     "    return \"HELD\" if (np.isfinite(v) and bool(lo < float(v) < hi)) else \"FAILED\"", ("ST-STATS",)),
    ("Brier on UNDETERMINED as HELD", "brier(P_M2, R[\"M2\"] == \"HELD\")", "brier(P_M2, R[\"M2\"] != \"FAILED\")", ("ST-LINES",)),
    ("selective = top 60%", "    sel = R[\"gq\"] >= 1\n", "    sel = R[\"gq\"] >= 2\n", ("ST-E2E",)),
    ("K grid 120 -> 100", "    return (kc, kf, 120)\n", "    return (kc, kf, 100)\n", ("ST-CONST",)),
    ("dry run reads flips and writes", "    print(\"%s DRY RUN complete", "    main_run(db, emb_dir, os.path.join(emb_dir, 'dry'), csv_path, None)\n    print(\"%s DRY RUN complete", ("ST-REFUSE",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="slotswap_mut_")
    fx = make_fixtures(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        pairs = old if isinstance(old, list) else [(old, new)]
        code = head
        for o_, n_ in pairs:
            if code.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, code.count(o_)))
            code = code.replace(o_, n_)
        ns = {"__name__": "slotswap_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
    import shutil
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-S0-SLOTSWAP-MECH (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.db, a.emb_dir)
    main_run(a.db, a.emb_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
