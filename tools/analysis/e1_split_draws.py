"""E1-SPLIT-DRAWS READOUT: SD1 (per-split paired Wald intervals of G_k = top1(N_k) - top1(Q_k) on each split's OWN held-out, and the
mean gap Gbar against the between-split spread), F-SD, SD2, P1-P5; the E1 pair as the IDENTITY precondition and the descriptive 4th
point; an embedder guard per tree. ZERO calls (no judge, no LLM, no embedding call); CPU only.

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — E1-SPLIT-DRAWS: is E1's
nomic-vs-qwen3 anchor-free tree-filing loss consistently negative, and larger than the between-split spread, across K = 3 freshly
re-drawn CK-CLOSE content-closed MMLU-Pro splits (paired nomic_raw and qwen3 trees per split, af_clean_s42 recipe)? (zero calls; 6
builds; CPU readout)" (L23831-L23859, written at a1c65848): INSTRUMENT, LIKE WITH LIKE, READOUTS AND CRITERIA (SD1, SD2), SUPPORT
(a)-(g), PREDICTIONS P1-P5, FALSIFIER F-SD, WHAT THIS RESULT WILL NOT SHOW. The registration governs; this docstring restates.
  SD1 (DECIDING; INTERVALS AND POINT jointly): G_k = top1(N_k) - top1(Q_k) on split k's held-out, paired; Gbar = mean of G_1..G_3;
  spread_E = max - min over the 3 splits of top1(E_k). WORSE iff each of the three per-split paired Wald 95% intervals lies wholly
  below 0 AND Gbar < -max(spread_N, spread_Q); BETTER symmetric; NEITHER otherwise (never parity).
  F-SD fires iff any split's point G_k >= 0 OR |Gbar| <= max(spread_N, spread_Q).
  IDENTITY PRECONDITION (refuse): E1's af_clean_s42 / N-raw reproduce 0.7269 / 0.6813, b 327 / c 484 (printed beside as the
  descriptive 4th point, never pooled into the criterion).

BUILDER DECLARATIONS (none changes a registered word; for the registrar):
  R1 FILING = flatLeaf top-1 = FLAT M1 per question (E1's D1): each held-out text goes to its tree's nearest leaf vmfMu (cosine, the
     256-d slice of the tree's OWN embedder: N_k in nomic_raw, Q_k in qwen3); hit iff its category == the majority category of the
     split's TRAIN texts filed to that leaf (anchor_free_readout.score_cells through flat_mix_mmlu.m1_block, E1's path; ties to the
     first-seen category in corpus order).
  R2 split k's held-out = the DISTINCT corpus texts whose side under salt e1sd<k> is EVAL (sentinel rows included: filing needs no
     eval link); TRAIN = every other distinct corpus text (GATE + TRAIN, 0.70); category = the text's first row's category (lower-
     cased; 4 corpus texts carry several). Counts 3,598 / 3,522 / 3,500 held-out (e1sd_split_draw.py --check).
  R3 the paired interval is E1's D2: the Wald interval (b - c)/n -/+ 1.96 sqrt(b + c - (b - c)^2/n)/n (e1_readout.mcnemar); the exact
     McNemar p (systematic_budget.mcnemar_edge) and the stem_key-group bootstrap interval are printed beside and never decide.
  R4 SUPPORT is measured per split: n, stem_key groups, DEFF = Kish m-bar of the held-out twin groups (the conservative rho = 1 form),
     n_eff = n / DEFF, discordance (b + c)/n, SE, MDE80 = 2.80 x SE, beside the registered 0.0083 / 0.023; the verdict line (f) is
     printed verbatim with the realised MDE80s; the spread clause stays DESCRIPTIVE-ONLY at the prediction as registered.
  R5 P1 HELD iff all three G_k lie in [-0.065, -0.015] AND Gbar in [-0.060, -0.020] (endpoints inclusive; each component printed);
     P2 HELD iff spread_N in [0.005, 0.035] AND spread_Q in [0.004, 0.030]; P3 (event: all three intervals below 0), P4 (the 3-way
     SD1 verdict, multi-class Brier sum over WORSE / NEITHER / BETTER) and P5 (event: F-SD fires) scored by Brier.
  R6 tie conventions A / B and wrong(established): not applicable (no judge verdicts; hits are 0 / 1; no model pairs), printed.
  R7 EMBEDDER GUARD per tree (8: N_1..3, Q_1..3, and the E1 pair): embedder_guard.guard (the record's arithmetic, unchanged) through
     e1_readout.text_join_guard on a TEXT-JOINED view: snapshot graph (snapshots.db, the row named by the run log's "Snapshot ID",
     never a latest timestamp) -> member q-ids -> texts by "q_" + sha256(text)[:16] (TaxonomyPersistence.hashQuery) over the corpus
     texts (an unresolved member REFUSES) -> the arm's raw blob. Two DISCRIMINATORS per tree, each must REFUSE: the tree on the OTHER
     arm's vectors (dimension) and the tree on its own vectors with the member -> text map permuted (cosine). The run dir's leaves
     must equal the graph's leaves (ids; vmfMu within 1e-5).
  R8 HYGIENE per build: e1sd_split_draw.check_run_dir (pool, embedder, sizes == the split's, closedByContent=0, no [SPLIT-CLOSURE],
     the [TRAIN-ONLY] line, one snapshot id, declared config blob); the tree's member texts (the fit) are all TRAIN texts of its split
     and share no stem_key with its held-out (0 required).

LAUNCH SEQUENCE (run-operator; zero calls; ONE single-threaded python process; a pool reader (rule 7): never inside a construction;
AFTER the six builds and the author's checkpoint CP-1 of the corpus DB, embeddings_cache.db and snapshots.db; see e1sd_launch.py --plan):
  python tools/analysis/e1_split_draws.py --selftest   # synthetic; executes dry_run() and run() end to end on fixtures, VALUE asserts
  python tools/analysis/e1_split_draws.py --mutants    # every declared mutant must be KILLED by the selftest
  python tools/analysis/e1_split_draws.py --dry-run    # pool lines first; pins; identity (E1 pair); builds PRESENT / ABSENT; REFUSES
                                                       # (rc 2) while any build is ABSENT; no SD1 measure, nothing written
  python tools/analysis/e1_split_draws.py --run        # measures + verdicts; outcome of record WRITE-ONCE (mode x)
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree.

OUTPUT: experiment_results/e1_split_draws/e1sd_readout_outcome.txt, --run only, WRITE-ONCE (mode x; --run REFUSES before any work if
it exists). Never committed (pin by sha256; back up to E: with SHA256SUMS.txt).
SELFTEST / MUTANTS: see selftest() and MUTANTS (the table with results is in the commit message).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import io
import sys
import json
import math
import time
import shutil
import struct
import hashlib
import argparse
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import contextlib
import subprocess
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

TAG = "[E1-SPLIT-DRAWS]"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def pins_of(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest(), lf16=hashlib.sha256(d).hexdigest()[:16],
                crlf16=hashlib.sha256(d.replace(b"\n", b"\r\n")).hexdigest()[:16])


def fmt_pins(p):
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"][:8], p["lf16"], p["crlf16"])


# the imported instrument is the pinned one, or nothing runs (LF git blobs)
IMPORT_PINS = {"e1_readout.py": "88f7990c2eee7536a370e47b5f14053802a68ed4",
               "e1sd_split_draw.py": "0c12e9b8442873cdc25548dd4c3323adf708ed89",
               "e1sd_launch.py": "bdbb3fc6dec7396de9ad70d0b375668da7e6e9d1"}
for _f, _b in IMPORT_PINS.items():
    _p = pins_of(os.path.join(HERE, _f))
    if _p["blob"] != _b:
        refuse("pin mismatch on tools/analysis/%s: %s, pinned blob:%s" % (_f, fmt_pins(_p), _b[:8]))
import e1_readout as E1R      # noqa: E402  (its own import pins; installs flat_mix_mmlu's read-only connect guard)
import e1sd_split_draw as SD  # noqa: E402
import e1sd_launch as LA      # noqa: E402  (DECLARED blobs, SPLIT_POOLS / SPLIT_BLOBS; nothing is launched by importing it)
FM, AF, EG, EA = E1R.FM, E1R.AF, E1R.EG, E1R.EA

P2DCA = SD.P2DCA
K = 3
ARMS = ("N", "Q")
ARM_SPACE = {"N": "nomic_raw", "Q": "qwen3_raw"}
MODEL = {"N": "nomic-embed-text:latest", "Q": "qwen3-embedding:latest"}
DIM = 256
Z95 = 1.959963984540054
IDENTITY = dict(af=0.7269, nraw=0.6813, b=327, c=484, n=3445)
E1_NRAW = E1R.E1_ARMS[0]                     # N-raw: run dir, snapshot 20261002_035009, 84 leaves
SUPPORT_PLAN = dict(se=0.0083, mde=0.023, sd_between=0.010, range_exp=0.017, range_ub80=0.025)
P1 = dict(each=(-0.065, -0.015), gbar=(-0.060, -0.020))
P2 = dict(N=(0.005, 0.035), Q=(0.004, 0.030))
P3_PROB = 0.70
P4_PROB = dict(WORSE=0.55, NEITHER=0.43, BETTER=0.02)
P5_PROB = 0.40
OUT_DIR = os.path.join("experiment_results", "e1_split_draws")
OUTCOME = "e1sd_readout_outcome.txt"
VERDICT_F = ("(f) VERDICT LINE (registered): the interval-consistency clause SCOREABLE (prediction -0.040 against MDE80 0.023); the "
             "spread clause DESCRIPTIVE-ONLY at the prediction (|Gbar| 0.040 lies within one planning MDE of the spread's 80% upper bound "
             "0.025, and K = 3 gives a very noisy range); SD1 as a whole is therefore thin, and its WORSE is read with K = 3 named.")
FSD_FIRES = ("F-SD FIRES: the gap is not consistently negative or the mean gap sits inside the between-split spread; the E1 loss is "
             "not separable from split-draw variation: the 'at this split' bracket reads \"at this split only; not stable across 3 "
             "content-closed re-draws\". No recorded number is revised.")
FSD_NOT = ("F-SD did not fire: every G_k < 0 and |Gbar| > max(spread_N, spread_Q).")
WORSE_LINE = ("SD1 WORSE (K = 3 named; one recipe, one corpus): extends E1's F-E1 to 3 content-closed splits; no recorded number is "
              "revised.")
DOES_NOT_SHOW = ("DOES NOT SHOW (fixed before data): another corpus, embedder, prompt (nomic RAW) or recipe; anchored trees; routing "
                 "or judging value; parity (no TOST); the mechanism; anything about the p2dca 3,445 or any arena pool.")


def say(L, s=""):
    print(s)
    L.append(s)


def data_path(rel):
    return os.path.join(pool_guard.DATA_ROOT, rel)


def qid(text):
    return "q_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def unit(v):
    return E1R.unit(v)


# ------------------------------------------------------------------------------------------------ guards and hygiene
def region_fn(byid):
    return lambda s: FM.region_query_ids(s["id"], byid)


def fit_ids(byid, root):
    return FM.region_query_ids(root, byid)


def guard_tree(label, arm, byid, id2text, blobs, model=None):
    """[EMB-GUARD] through e1_readout.text_join_guard (embedder_guard.guard unchanged). -> (admitted, printed lines, min cos line)."""
    sites = EG.split_sites(byid)
    ids = list(dict.fromkeys(q for s in sites for q in FM.region_query_ids(s["id"], byid)))
    sub = {q: id2text[q] for q in ids if q in id2text}
    bl = {t: blobs[t] for t in set(sub.values()) if t in blobs}
    res, err, out = E1R.guard_quiet(lambda: E1R.text_join_guard(byid, region_fn(byid), sub, bl, model or MODEL[arm], label))
    mline = [l.strip() for l in out.splitlines() if "vmfMu cosine" in l]
    return err is None, out, (mline[0] if mline else "-"), err


def check_tree(label, arm, tree, graph, id2text, blobs, other_blobs, L, rng_seed=12345):
    """R7: the run dir's leaves == the graph's; the guard ADMITS on the tree's own vectors; both discriminators REFUSE."""
    byid = graph["byid"]
    gl = {k_: n["vmfMu"] for k_, n in byid.items() if not n.get("childIds")}
    tl = dict(zip(tree["leaf_ids"], [n["vmfMu"] for n in tree["leaves"]]))
    if set(gl) != set(tl):
        refuse("%s: snapshot graph leaves != run dir leaves (%d vs %d)" % (label, len(gl), len(tl)))
    dmax = max(float(np.max(np.abs(np.asarray(tl[k_]) - np.asarray(gl[k_])))) for k_ in tl)
    if dmax > 1e-5:
        refuse("%s: leaf vmfMu differ from the graph's by %.2e" % (label, dmax))
    ids = fit_ids(byid, graph["root"])
    unresolved = [q for q in ids if q not in id2text]
    if unresolved:
        refuse("%s: %d member id(s) resolve to no corpus text (first %s)" % (label, len(unresolved), unresolved[:3]))
    ok_, out, mline, err = guard_tree(label, arm, byid, id2text, blobs)
    for line in out.splitlines():
        say(L, "  " + line)
    if not ok_:
        refuse("[EMB-GUARD] %s on its own %s vectors: %s" % (label, ARM_SPACE[arm], err))
    ok_o, _o, ml_o, _e = guard_tree(label + " x OTHER arm", arm, byid, id2text, other_blobs)
    rng = np.random.default_rng(rng_seed)
    keys = sorted(set(ids))
    perm = list(rng.permutation(len(keys)))
    shuffled = {keys[i]: id2text[keys[j]] for i, j in zip(range(len(keys)), perm)}
    ok_s, _s, ml_s, _e2 = guard_tree(label + " x PERMUTED map", arm, byid, shuffled, blobs)
    say(L, "[EMB-GUARD] %s: own %s vectors ADMIT (%s, leaves == graph, vmfMu max diff %.1e) | DISCRIMINATORS: the other arm's vectors "
           "%s (%s); permuted member->text map %s (%s)" % (label, ARM_SPACE[arm], mline, dmax, "REFUSE (expected)" if not ok_o else "ADMIT",
                                                         ml_o, "REFUSE (expected)" if not ok_s else "ADMIT", ml_s))
    if ok_o or ok_s:
        refuse("[EMB-GUARD] %s: a discriminator was ADMITTED (other arm %s, permuted %s): the guard does not discriminate"
               % (label, "ADMIT" if ok_o else "refuse", "ADMIT" if ok_s else "refuse"))
    return set(id2text[q] for q in ids)


def hygiene(label, fit_texts, train, heldout, L):
    tr = set(t for t, _ in train)
    ho = set(t for t, _ in heldout)
    hk = set(SD.SS.stem_key(t) for t in ho)
    not_train = len(fit_texts - tr)
    in_ho = len(fit_texts & ho)
    keys = sum(1 for t in fit_texts if SD.SS.stem_key(t) in hk)
    say(L, "HYGIENE %s: fit texts %d; not TRAIN texts of the split %d; held-out texts in the fit %d; fit texts sharing a held-out stem_key "
           "%d (all must be 0)" % (label, len(fit_texts), not_train, in_ho, keys))
    if not_train or in_ho or keys:
        refuse("%s: held-out content reaches the tree (or the fit is not this split's TRAIN)" % label)


# ------------------------------------------------------------------------------------------------ measures and verdicts
def filing_hits(tree, vec, train, heldout):
    """R1: flatLeaf top-1 per held-out question (FM.m1_block on e1_readout.tree_fn). -> (hits array, score dict)."""
    fn = E1R.tree_fn(tree)
    sc, hits, _kh = FM.m1_block(fn, E1R.mat(vec, [t for t, _ in train]), E1R.mat(vec, [t for t, _ in heldout]), train, heldout)
    return hits, sc


def paired(hn, hq, heldout):
    mc = E1R.mcnemar(hn, hq)
    groups, G = FM.twin_groups([t for t, _ in heldout])
    lo, hi = FM.twin_boot_ci(np.asarray(hn) - np.asarray(hq), groups)
    mbar = FM.kish_mbar(groups)
    mc.update(boot=(lo, hi), groups=G, mbar=mbar, n_eff=mc["n"] / mbar, mde=2.80 * mc["se"])
    return mc


def spread(vals):
    return float(max(vals) - min(vals))


def sd1_verdict(G, lo, hi, spread_n, spread_q):
    """-> (verdict, dict of clauses). WORSE iff all hi < 0 AND Gbar < -max spread; BETTER iff all lo > 0 AND Gbar > max spread."""
    gbar = float(sum(G) / len(G))
    ms = max(spread_n, spread_q)
    all_below = bool(all(h < 0 for h in hi))
    all_above = bool(all(l_ > 0 for l_ in lo))
    if all_below and gbar < -ms:
        v = "WORSE"
    elif all_above and gbar > ms:
        v = "BETTER"
    else:
        v = "NEITHER"
    return v, dict(gbar=gbar, max_spread=ms, all_below=all_below, all_above=all_above, beyond=bool(abs(gbar) > ms))


def fsd_fires(G, gbar, ms):
    any_nonneg = bool(any(g >= 0 for g in G))
    inside = bool(abs(gbar) <= ms)
    return bool(any_nonneg or inside), any_nonneg, inside


def brier(p, event):
    return (p - (1.0 if event else 0.0)) ** 2


def brier3(probs, outcome):
    return float(sum((p - (1.0 if c == outcome else 0.0)) ** 2 for c, p in probs.items()))


def inside(x, iv):
    return bool(iv[0] <= x <= iv[1])


def compute(W):
    """The deciding path: per split G_k, spreads, SD1, F-SD, predictions (the identity pair re-measured for printing). -> res."""
    I = W["identity"]
    h_af, sc_af = filing_hits(I["trees"]["af"], W["spaces"]["Q"], I["train"], I["heldout"])
    h_nr, sc_nr = filing_hits(I["trees"]["N-raw"], W["spaces"]["N"], I["train"], I["heldout"])
    e1 = paired(h_nr, h_af, I["heldout"])
    ident = dict(af=round(float(h_af.mean()), 4), nraw=round(float(h_nr.mean()), 4), b=e1["b"], c=e1["c"], n=e1["n"])
    res = dict(identity=ident, e1=e1, splits=[])          # enforced by identity_check() before compute() is reached
    for k in range(1, K + 1):
        S = W["splits"][k]
        hn, scn = filing_hits(W["trees"][("N", k)], W["spaces"]["N"], S["train"], S["heldout"])
        hq, scq = filing_hits(W["trees"][("Q", k)], W["spaces"]["Q"], S["train"], S["heldout"])
        mc = paired(hn, hq, S["heldout"])
        res["splits"].append(dict(k=k, pool=S["pool"], n=len(S["heldout"]), n_train=len(S["train"]), topN=float(hn.mean()),
                                  topQ=float(hq.mean()), mc=mc, leavesN=len(W["trees"][("N", k)]["leaf_ids"]),
                                  leavesQ=len(W["trees"][("Q", k)]["leaf_ids"]), near=S.get("near"), cellsN=scn["cells_heldout_untrained"],
                                  cellsQ=scq["cells_heldout_untrained"]))
    G = [s["mc"]["diff"] for s in res["splits"]]
    lo = [s["mc"]["lo"] for s in res["splits"]]
    hi = [s["mc"]["hi"] for s in res["splits"]]
    sN = spread([s["topN"] for s in res["splits"]])
    sQ = spread([s["topQ"] for s in res["splits"]])
    v, cl = sd1_verdict(G, lo, hi, sN, sQ)
    f, any_nonneg, ins = fsd_fires(G, cl["gbar"], cl["max_spread"])
    p1_each = [inside(g, P1["each"]) for g in G]
    res.update(G=G, spread_N=sN, spread_Q=sQ, sd1=v, clauses=cl, fsd=f, fsd_any_nonneg=any_nonneg, fsd_inside=ins,
               p1_each=p1_each, p1_gbar=inside(cl["gbar"], P1["gbar"]), p2_N=inside(sN, P2["N"]), p2_Q=inside(sQ, P2["Q"]),
               p3_event=bool(all(h < 0 for h in hi)))
    res["p1"] = bool(all(p1_each) and res["p1_gbar"])
    res["p2"] = bool(res["p2_N"] and res["p2_Q"])
    return res


def render(res):
    """Every registered criterion, prediction and falsifier line; every branch is executed by the selftest."""
    L = []
    L.append("%s E1-SPLIT-DRAWS readout (zero calls). Registration L23831-L23859 (SD1, SD2, SUPPORT (a)-(g), P1-P5, F-SD)." % TAG)
    i, e = res["identity"], res["e1"]
    L.append("IDENTITY PRECONDITION (HELD): E1 pair on p2dca's held-out n = %d: af_clean_s42 (qwen3) top-1 %.4f, N-raw (nomic_raw) top-1 "
             "%.4f, b %d / c %d (the record: %.4f / %.4f, b %d / c %d)" % (i["n"], i["af"], i["nraw"], i["b"], i["c"], IDENTITY["af"],
                                                                         IDENTITY["nraw"], IDENTITY["b"], IDENTITY["c"]))
    L.append("E1 PAIR = DESCRIPTIVE 4th POINT (never pooled into SD1): G_E1 = %+.4f, paired Wald 95%% [%+.4f, %+.4f], exact McNemar p "
             "%.3g; split af_clean_s42's (p2dca ids, content-closed by the engine's closure)" % (e["diff"], e["lo"], e["hi"], e["p"]))
    L.append("=== PER SPLIT (each split's OWN held-out; N_k in nomic_raw, Q_k in qwen3; majority from the split's TRAIN texts) ===")
    for s in res["splits"]:
        m = s["mc"]
        L.append("  split %d (pool %s): held-out n = %d (TRAIN texts %d); top-1 N_%d %.4f (leaves %d), Q_%d %.4f (leaves %d); b (N right, Q "
                 "wrong) %d, c (N wrong, Q right) %d; G_%d = (b - c) / n = %+.4f; paired Wald 95%% [%+.4f, %+.4f] -> %s"
                 % (s["k"], s["pool"], s["n"], s["n_train"], s["k"], s["topN"], s["leavesN"], s["k"], s["topQ"], s["leavesQ"], m["b"],
                    m["c"], s["k"], m["diff"], m["lo"], m["hi"], "BELOW 0" if m["hi"] < 0 else ("ABOVE 0" if m["lo"] > 0 else "REACHES 0")))
        L.append("    beside (never deciding): exact McNemar p %.3g; stem_key-group bootstrap [%+.4f, %+.4f]" % (m["p"], m["boot"][0], m["boot"][1]))
        L.append("    SUPPORT split %d: n %d; stem_key groups %d; DEFF %.4f (Kish m-bar, measured); n_eff %.1f; discordance %.4f; SE %.5f "
                 "(planned %.4f); MDE80 %.4f (planned %.3f)" % (s["k"], s["n"], m["groups"], m["mbar"], m["n_eff"], m["disc"], m["se"],
                                                                SUPPORT_PLAN["se"], m["mde"], SUPPORT_PLAN["mde"]))
    cl = res["clauses"]
    L.append("=== SD1 (DECIDING; INTERVALS AND POINT jointly) ===")
    L.append("  G = [%s]; Gbar = %+.4f (the three splits only); spread_N = %.4f, spread_Q = %.4f (max - min of top-1 over the 3 splits); "
             "max spread %.4f" % (", ".join("%+.4f" % g for g in res["G"]), cl["gbar"], res["spread_N"], res["spread_Q"], cl["max_spread"]))
    L.append("  clause 1 (all three per-split intervals wholly below 0): %s; (all wholly above 0): %s" % (
        "YES" if cl["all_below"] else "NO", "YES" if cl["all_above"] else "NO"))
    L.append("  clause 2 (|Gbar| > max spread, signed: Gbar %s -max spread / > +max spread): %s" % (
        "<" if cl["gbar"] < -cl["max_spread"] else ">=", "YES" if cl["beyond"] else "NO"))
    L.append("  SD1 VERDICT: %s" % res["sd1"])
    if res["sd1"] == "WORSE":
        L.append("  " + WORSE_LINE)
    elif res["sd1"] == "BETTER":
        L.append("  SD1 BETTER (symmetric; K = 3 named): nomic_raw files BETTER than qwen3 on all three content-closed splits.")
    else:
        L.append("  SD1 NEITHER (never parity): the fail observable held (an interval reaches 0, or |Gbar| <= max spread).")
    L.append("  " + VERDICT_F)
    L.append("  realised MDE80 per split: %s (planned 0.023); range of 3 draws planned E 0.017, 80%% upper bound 0.025" % (
        ", ".join("%.4f" % s["mc"]["mde"] for s in res["splits"])))
    L.append("=== FALSIFIER F-SD ===")
    L.append("  any G_k >= 0: %s; |Gbar| <= max spread: %s" % ("YES" if res["fsd_any_nonneg"] else "NO", "YES" if res["fsd_inside"] else "NO"))
    L.append("  " + (FSD_FIRES if res["fsd"] else FSD_NOT))
    L.append("=== SD2 (DESCRIPTIVE-ONLY) ===")
    for s in res["splits"]:
        L.append("  split %d: G %+.4f [%+.4f, %+.4f]; top-1 N %.4f / Q %.4f; leaves N %d / Q %d; held-out cells with no TRAIN text N %d / Q "
                 "%d; near-copies %s" % (s["k"], s["mc"]["diff"], s["mc"]["lo"], s["mc"]["hi"], s["topN"], s["topQ"], s["leavesN"],
                                         s["leavesQ"], s["cellsN"], s["cellsQ"], "-" if s["near"] is None else s["near"]))
    L.append("  E1 pair beside: G_E1 %+.4f [%+.4f, %+.4f]" % (e["diff"], e["lo"], e["hi"]))
    L.append("WRONG(ESTABLISHED) / TIE CONVENTIONS A, B: not applicable (R6: no judge verdicts, hits are 0 / 1; no model pairs)")
    L.append("=== PREDICTIONS (Brier) ===")
    L.append("  P1 each G_k in [%+.3f, %+.3f]: %s; Gbar in [%+.3f, %+.3f]: %s -> P1 %s" % (
        P1["each"][0], P1["each"][1], ", ".join("G_%d %s" % (i_ + 1, "in" if x else "OUT") for i_, x in enumerate(res["p1_each"])),
        P1["gbar"][0], P1["gbar"][1], "in" if res["p1_gbar"] else "OUT", "HELD" if res["p1"] else "FAILED"))
    L.append("  P2 spread_N %.4f in [%.3f, %.3f]: %s; spread_Q %.4f in [%.3f, %.3f]: %s -> P2 %s" % (
        res["spread_N"], P2["N"][0], P2["N"][1], "in" if res["p2_N"] else "OUT", res["spread_Q"], P2["Q"][0], P2["Q"][1],
        "in" if res["p2_Q"] else "OUT", "HELD" if res["p2"] else "FAILED"))
    L.append("  P3 all three per-split intervals below 0 (prior %.2f): %s; Brier %.4f" % (
        P3_PROB, "occurred" if res["p3_event"] else "did not occur", brier(P3_PROB, res["p3_event"])))
    L.append("  P4 SD1 verdict (WORSE %.2f, NEITHER %.2f, BETTER %.2f): %s; Brier (3-class) %.4f" % (
        P4_PROB["WORSE"], P4_PROB["NEITHER"], P4_PROB["BETTER"], res["sd1"], brier3(P4_PROB, res["sd1"])))
    L.append("  P5 F-SD fires (prior %.2f): %s; Brier %.4f" % (P5_PROB, "FIRED" if res["fsd"] else "did not fire", brier(P5_PROB, res["fsd"])))
    L.append(DOES_NOT_SHOW)
    return L


# ------------------------------------------------------------------------------------------------ the world (real)
def load_real(L):
    """Every real input: pool lines first, pins, splits (re-derived byte-equal), identity world, builds PRESENT / ABSENT, guards,
    hygiene. -> world dict (W["absent"] lists absent builds; trees only for present ones)."""
    pid = pool_guard.assert_pool_of_record(P2DCA)
    say(L, "pool %s (pool_guard.assert_pool_of_record: the IDENTITY pair's held-out; never compared with the splits)" % pid)
    say(L, "[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    say(L, "[SCRIPT] tools/analysis/e1_split_draws.py %s" % fmt_pins(pins_of(os.path.abspath(__file__))))
    for f_ in IMPORT_PINS:
        say(L, "[PIN] tools/analysis/%s %s (verified)" % (f_, fmt_pins(pins_of(os.path.join(HERE, f_)))))
    say(L, "[DATA] DATA_ROOT %s" % pool_guard.DATA_ROOT)
    corpus_db = data_path(SD.CORPUS_DB)
    con = pool_guard.open_ro(corpus_db)
    try:
        rows = SD.corpus_rows(con)
    finally:
        con.close()
    texts = sorted(set(r["text"] for r in rows))
    W = dict(splits={}, trees={}, graphs={}, absent=[], identity_expect=dict(IDENTITY), pool_status={})
    for k in range(1, K + 1):
        d = SD.draw(rows, SD.SALTS[k - 1])
        sp = os.path.join(ROOT, *(SD.SPLIT_REL % k).split("/"))
        if pins_of(sp)["blob"] != LA.SPLIT_BLOBS[k] or d["pool"] != LA.SPLIT_POOLS[k]:
            refuse("split %d: file %s / re-derived pool %s differ from the declared blob:%s / pool %s" % (
                k, sp, d["pool"], LA.SPLIT_BLOBS[k][:8], LA.SPLIT_POOLS[k]))
        with open(sp, "rb") as f:
            if f.read().replace(b"\r\n", b"\n") != SD.file_bytes(d["ids"]):
                refuse("split %d: the committed file is not the re-derived split" % k)
        try:
            pool_guard.assert_pool_of_record(d["pool"], db=corpus_db, id_file=sp)
            st = "RECORDED (pool_guard.assert_pool_of_record passed: id file and reserved_pool rows agree)"
        except SystemExit as e:
            st = "NOT RECORDED (%s)" % str(e)[:120]
        W["pool_status"][k] = st
        say(L, "pool %s (split e1sd%d; NEVER a pool of record): %s" % (d["pool"], k, st))
        W["splits"][k] = dict(pool=d["pool"], draw=d, train=SD.distinct(d["train"]), heldout=SD.distinct(d["held"]))
        say(L, "SPLIT %d: held-out %d distinct texts / TRAIN %d (file blob:%s, re-derived byte-equal)" % (
            k, len(W["splits"][k]["heldout"]), len(W["splits"][k]["train"]), LA.SPLIT_BLOBS[k][:8]))
    id2text = {qid(t): t for t in texts}
    W["id2text"] = id2text
    # identity world (E1's exact inputs)
    E1R.point_eval_db(corpus_db)
    train, heldout, _cs = AF.corpus(P2DCA)
    af = FM.load_T("T")
    nraw = AF.load_tree(data_path(E1_NRAW["run"]))
    if len(nraw["leaves"]) != E1_NRAW["leaves"]:
        refuse("E1 N-raw tree has %d leaves, the record %d" % (len(nraw["leaves"]), E1_NRAW["leaves"]))
    W["identity"] = dict(train=train, heldout=heldout, trees={"af": af, "N-raw": nraw},
                         graphs={"af": FM.load_snapshot_graph(FM.T_SNAPSHOT), "N-raw": FM.load_snapshot_graph(E1_NRAW["snapshot"])})
    say(L, "IDENTITY WORLD: p2dca held-out %d, readout train %d (anchor_free_readout.corpus); af_clean_s42 %d leaves (snapshot %s); "
           "N-raw %d leaves (snapshot %s)" % (len(heldout), len(train), len(af["leaves"]), FM.T_SNAPSHOT, len(nraw["leaves"]),
                                              E1_NRAW["snapshot"]))
    # builds
    pins = json.load(open(EA.ARM_PINS_FILE, encoding="utf-8"))
    for k in range(1, K + 1):
        for arm in ARMS:
            rd = SD.run_dir_of(arm, k, pool_guard.DATA_ROOT)
            name = "%s_e1sd%d" % (arm, k)
            if not os.path.isdir(rd):
                W["absent"].append(name)
                say(L, "BUILD %s: ABSENT (%s)" % (name, rd))
                continue
            got = SD.check_run_dir(rd, arm, k, W["splits"][k]["draw"], LA.DECLARED[name], nomic_pin=pins["arms"]["nomic_raw"]["sha256"])
            tree = AF.load_tree(rd)
            if tree["dim"] != DIM:
                refuse("%s: slice %d" % (name, tree["dim"]))
            W["trees"][(arm, k)] = tree
            W["graphs"][(arm, k)] = FM.load_snapshot_graph(got["snapshot"])
            say(L, "BUILD %s: PRESENT %s | snapshot %s (graph sha256 %s) | %d leaves | [POOL] %s gate %s closedByContent %s | config blob:%s"
                % (name, rd, got["snapshot"], W["graphs"][(arm, k)]["sha"][:16], len(tree["leaves"]), got["pool_line"][0],
                   got["pool_line"][1], got["pool_line"][2], LA.DECLARED[name][:8]))
    # vectors (by text) for every corpus text, both arms
    need = set(texts)
    vq, bq, mq, _iq = E1R.load_space("qwen3_raw", need, L)
    vn, bn, mn, _in = E1R.load_space("nomic_raw", need, L)
    W["spaces"] = {"Q": vq, "N": vn}
    W["blobs"] = {"Q": bq, "N": bn}
    vec512 = {}
    for t, b in bq.items():
        v = np.array(struct.unpack(">%df" % SD.NEAR_DIM, b[:4 * SD.NEAR_DIM]), dtype=np.float64)
        vec512[t] = v / np.linalg.norm(v)
    for k in range(1, K + 1):
        S = W["splits"][k]
        S["near"] = SD.near_copies([t for t, _ in S["heldout"]], [t for t, _ in S["train"]], vec512)[0]
    return W


def admit(W, L):
    """Guards and hygiene for every present split tree (R7, R8). Shared by the real and the fixture worlds."""
    other = {"N": "Q", "Q": "N"}
    for k in range(1, K + 1):
        for arm in ARMS:
            if (arm, k) not in W["trees"]:
                continue
            fit = check_tree("%s_e1sd%d" % (arm, k), arm, W["trees"][(arm, k)], W["graphs"][(arm, k)], W["id2text"], W["blobs"][arm],
                             W["blobs"][other[arm]], L)
            hygiene("%s_e1sd%d" % (arm, k), fit, W["splits"][k]["train"], W["splits"][k]["heldout"], L)


# ------------------------------------------------------------------------------------------------ modes
def identity_check(W, L):
    """The E1 pair: guards on both trees, then the IDENTITY PRECONDITION (refuse). Printed in --dry-run and --run."""
    other = {"N": "Q", "Q": "N"}
    for name, arm in (("af", "Q"), ("N-raw", "N")):
        check_tree("E1 %s" % name, arm, W["identity"]["trees"][name], W["identity"]["graphs"][name], W["id2text"], W["blobs"][arm],
                   W["blobs"][other[arm]], L)
    I = W["identity"]
    h_af, _ = filing_hits(I["trees"]["af"], W["spaces"]["Q"], I["train"], I["heldout"])
    h_nr, _ = filing_hits(I["trees"]["N-raw"], W["spaces"]["N"], I["train"], I["heldout"])
    e1 = paired(h_nr, h_af, I["heldout"])
    ident = dict(af=round(float(h_af.mean()), 4), nraw=round(float(h_nr.mean()), 4), b=e1["b"], c=e1["c"], n=e1["n"])
    held = ident == W["identity_expect"]
    say(L, "IDENTITY: E1 pair %s vs the record %s -> %s; G_E1 %+.4f [%+.4f, %+.4f] (the descriptive 4th point)"
        % (ident, W["identity_expect"], "HELD" if held else "FAILED", e1["diff"], e1["lo"], e1["hi"]))
    if not held:
        refuse("IDENTITY PRECONDITION: the E1 pair reads %s, the record is %s" % (ident, W["identity_expect"]))
    return ident


def dry_run(loader, L=None):
    L = [] if L is None else L
    W = loader(L)
    identity_check(W, L)
    if W["absent"]:
        say(L, "[MODE] --dry-run: builds ABSENT %s; SD1 cannot be assembled" % W["absent"])
        refuse("builds ABSENT (%d of 6): %s; the dry-run of record needs all six builds and the author's checkpoint CP-1"
               % (len(W["absent"]), W["absent"]))
    admit(W, L)
    for k in range(1, K + 1):
        S = W["splits"][k]
        say(L, "PLAN split %d: N_%d vs Q_%d filing on %d held-out with the majority of %d TRAIN texts; paired Wald + exact McNemar + "
               "bootstrap" % (k, k, k, len(S["heldout"]), len(S["train"])))
    say(L, "[MODE] --dry-run: pins, pools, splits, builds, guards, hygiene, identity; NO SD1 measure; nothing written")
    say(L, "%s dry-run complete" % TAG)
    return 0


def write_once(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run(loader, out_dir, L=None):
    L = [] if L is None else L
    oc = os.path.join(out_dir, OUTCOME)
    if os.path.exists(oc):
        refuse("%s exists: the outcome of record is write-once" % oc)
    t0 = time.process_time()
    W = loader(L)
    identity_check(W, L)
    if W["absent"]:
        refuse("builds ABSENT: %s" % W["absent"])
    admit(W, L)
    res = compute(W)
    for line in render(res):
        say(L, line)
    say(L, "%s CPU %.1f s; zero calls" % (TAG, time.process_time() - t0))
    os.makedirs(out_dir, exist_ok=True)
    write_once(oc, "\n".join(L) + "\n")
    say(L, "%s outcome written (write-once): %s" % (TAG, oc))
    return res


# ------------------------------------------------------------------------------------------------ selftest fixtures
SHARES = (0.36, 0.28, 0.20, 0.12, 0.04)
NCAT = len(SHARES)
NAT = {"N": 768, "Q": 4096}


def _fx_corpus(n=1500, seed=4, noise_frac=0.02):
    """1,500 rows over 5 categories (shares 0.36 / 0.28 / 0.20 / 0.12 / 0.04), distinct texts plus 5 exact twins; per-arm raw vectors
    whose 256-d slice is the category centre plus noise; 2% of texts carry the NEXT category's centre (label noise, the same texts in
    both arms) so no tree reaches 1.0 and top-1 varies across splits."""
    rng = np.random.default_rng(seed)
    cats = []
    for c, sh in enumerate(SHARES):
        cats += ["cat%d" % c] * int(round(sh * n))
    rows = [dict(row=i + 1, id=7000 + i, text="fixture question %05d of %s" % (i, c), category=c, domain=c.capitalize())
            for i, c in enumerate(cats)]
    for j in range(5):
        r = dict(rows[j * 37])
        r.update(row=len(cats) + 1 + j, id=90000 + j)
        rows.append(r)
    texts = sorted(set(r["text"] for r in rows))
    cat_of = {}
    for r in rows:
        cat_of.setdefault(r["text"], r["category"])
    noisy = set(t for t in texts if rng.random() < noise_frac)
    cent = {a: FM.unit_rows(np.random.default_rng(seed + (1 if a == "N" else 2)).normal(size=(NCAT, DIM))) for a in ARMS}
    space, blobs = {a: {} for a in ARMS}, {a: {} for a in ARMS}
    for t in texts:
        c = int(cat_of[t][3:])
        c = (c + 1) % NCAT if t in noisy else c
        for a in ARMS:
            v = cent[a][c] + rng.normal(0, 0.05, DIM)
            raw = np.concatenate([v, rng.normal(0, 0.01, NAT[a] - DIM)]).astype(np.float32)
            blobs[a][t] = struct.pack(">%df" % NAT[a], *raw)
            space[a][t] = unit(raw)
    return rows, texts, cat_of, cent, space, blobs


_FX = {}


def _fx_cached():
    if "c" not in _FX:
        _FX["c"] = _fx_corpus()
    return _FX["c"]


def _fx_mus(cent, kind):
    """Leaf centres (5 leaves): 'full' = the 5 category centres; 'm4' = cat4 filed with cat3 (loses ~0.04); 'm3' = cat3 filed with cat2
    (loses ~0.12); 'm34' = cat3 and cat4 filed with cat2 (loses ~0.16). Duplicated centres carry a tiny jitter (both copies' majority is
    the larger category)."""
    tiny = np.random.default_rng(99).normal(0, 1e-4, (NCAT, DIM))
    idx = {"full": [0, 1, 2, 3, 4], "m4": [0, 1, 2, 3, 3], "m3": [0, 1, 2, 2, 4], "m34": [0, 1, 2, 2, 2]}[kind]
    return cent[idx] + (0 if kind == "full" else tiny)


def _fx_tree(mus, train, vec, prefix):
    """root -> D0 (L0, L1), D1 (L2, L3, L4); leaf vmfMu = mus; each leaf's queryIds = the TRAIN texts filed to it; internal vmfMu = the
    normalised mean of its region's unit vectors (so the guard admits). -> nodes (the snapshot graph's shape)."""
    mus = FM.unit_rows(np.asarray(mus, dtype=np.float64))
    ids = ["%s%07d" % (prefix, i) for i in range(1, 9)]
    root, d0, d1 = ids[:3]
    leaves = ids[3:]
    tt = [t for t, _ in train]
    li = FM.nearest_assign(np.stack([vec[t] for t in tt]), mus)
    members = {lf: [tt[j] for j in range(len(tt)) if li[j] == i] for i, lf in enumerate(leaves)}

    def mean_mu(ts):
        m = np.sum(np.stack([vec[t] for t in ts]), axis=0)
        return list(map(float, m / np.linalg.norm(m)))
    reg0 = members[leaves[0]] + members[leaves[1]]
    reg1 = members[leaves[2]] + members[leaves[3]] + members[leaves[4]]
    nodes = [dict(id=root, label=root, depth=0, isLeaf=False, childIds=[d0, d1], parentIds=[], vmfMu=mean_mu(reg0 + reg1), sliceDim=DIM,
                  dasguptaDeltaNorm=0.1, queryIds=[]),
             dict(id=d0, label=d0, depth=1, isLeaf=False, childIds=leaves[:2], parentIds=[root], vmfMu=mean_mu(reg0), sliceDim=DIM,
                  dasguptaDeltaNorm=0.1, queryIds=[]),
             dict(id=d1, label=d1, depth=1, isLeaf=False, childIds=leaves[2:], parentIds=[root], vmfMu=mean_mu(reg1), sliceDim=DIM,
                  dasguptaDeltaNorm=0.1, queryIds=[])]
    for i, lf in enumerate(leaves):
        nodes.append(dict(id=lf, label=lf, depth=2, isLeaf=True, childIds=[], parentIds=[d0 if i < 2 else d1], vmfMu=list(map(float, mus[i])),
                          sliceDim=DIM, queryIds=[qid(t) for t in members[lf]]))
    return nodes


def pins_of_text(t):
    d = t.replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def _fx_world(td, plan, ident_plan=("full", "m34"), ident_expect=None, run_dir_over=None, graph_over=None, absent=()):
    """plan = {k: (N kind, Q kind)}; six run dirs written by e1sd_split_draw.fake_run_dir (checked by check_run_dir), trees loaded by
    anchor_free_readout.load_tree from them; the identity pair on a fixture split (salt 'e1sd-ident'). -> (loader, W)."""
    rows, texts, cat_of, cent, space, blobs = _fx_cached()
    W = dict(splits={}, trees={}, graphs={}, absent=[], identity_expect=None, pool_status={}, spaces=space, blobs=blobs,
             id2text={qid(t): t for t in texts})
    with open(os.path.join(ROOT, *SD.BASE_TOML.split("/")), encoding="utf-8") as f:
        base = f.read()
    for k in range(1, K + 1):
        d = SD.draw(rows, SD.SALTS[k - 1])
        W["splits"][k] = dict(pool=d["pool"], draw=d, train=SD.distinct(d["train"]), heldout=SD.distinct(d["held"]), near=0)
        for arm, kind in zip(ARMS, plan[k]):
            name = "%s_e1sd%d" % (arm, k)
            if name in absent:
                W["absent"].append(name)
                continue
            mus = _fx_mus(cent[arm], kind.rstrip("h"))
            if kind.endswith("h"):                  # leaf 4 AT one held-out text's vector: a held-out cell no TRAIN text reaches
                mus = np.array(mus, dtype=np.float64)
                mus[4] = space[arm][W["splits"][k]["heldout"][0][0]][:DIM]
            nodes = _fx_tree(mus, W["splits"][k]["train"], space[arm], prefix="%s%d" % (arm.lower(), k))
            if graph_over and name in graph_over:
                nodes = graph_over[name](nodes, W)
            cfg = SD.toml_text(arm, k, d["pool"], base)
            rd = os.path.join(td, name, "seed_42")
            SD.fake_run_dir(rd, arm, k, d, cfg, nomic_pin="PIN", snapshot="SNAP_" + name, nodes=[dict(n_, queryIds=None) for n_ in nodes],
                            **dict((run_dir_over or {}).get(name, {})))
            got = SD.check_run_dir(rd, arm, k, d, pins_of_text(cfg), nomic_pin="PIN")
            W["trees"][(arm, k)] = AF.load_tree(rd)
            W["graphs"][(arm, k)] = dict(byid={n_["id"]: n_ for n_ in nodes}, root=nodes[0]["id"], sha="fixture", snapshot=got["snapshot"])
    di = SD.draw(rows, "e1sd-ident")
    itrain, iheld = SD.distinct(di["train"]), SD.distinct(di["held"])
    W["identity"] = dict(train=itrain, heldout=iheld, trees={}, graphs={})
    for name, arm, kind in (("af", "Q", ident_plan[0]), ("N-raw", "N", ident_plan[1])):
        nodes = _fx_tree(_fx_mus(cent[arm], kind), itrain, space[arm], prefix="i%s" % arm.lower())
        rd = os.path.join(td, "ident_" + name)
        os.makedirs(rd, exist_ok=True)
        with open(os.path.join(rd, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"iteration": 1, "nodes": [dict(n_, queryIds=None) for n_ in nodes]}) + "\n")
        W["identity"]["trees"][name] = AF.load_tree(rd)
        W["identity"]["graphs"][name] = dict(byid={n_["id"]: n_ for n_ in nodes}, root=nodes[0]["id"], sha="fixture")
    if ident_expect is None:
        h_af = _indep_hits(W["identity"]["trees"]["af"], space["Q"], itrain, iheld)
        h_nr = _indep_hits(W["identity"]["trees"]["N-raw"], space["N"], itrain, iheld)
        ident_expect = dict(af=round(float(h_af.mean()), 4), nraw=round(float(h_nr.mean()), 4),
                            b=int(((h_nr == 1) & (h_af == 0)).sum()), c=int(((h_nr == 0) & (h_af == 1)).sum()), n=len(iheld))
    W["identity_expect"] = ident_expect

    def loader(L):
        say(L, "pool FIXTURE (selftest; no DB read)")
        for k in range(1, K + 1):
            say(L, "SPLIT %d: held-out %d / TRAIN %d" % (k, len(W["splits"][k]["heldout"]), len(W["splits"][k]["train"])))
        return W
    return loader, W


def _indep_hits(tree, space, train, heldout):
    """Independent flatLeaf top-1 (no m1_block / score_cells): argmax cosine over the leaf vmfMu, majority of the TRAIN texts with
    ties to the first-seen category."""
    mu = FM.unit_rows(np.asarray(tree["leaf_mu"], dtype=np.float64))
    lt = [int(np.argmax(mu @ space[t])) for t, _ in train]
    maj = {}
    for leaf in set(lt):
        seen, cnt = [], Counter()
        for kk, (_, c) in zip(lt, train):
            if kk == leaf:
                cnt[c] += 1
                if c not in seen:
                    seen.append(c)
        maj[leaf] = sorted(cnt, key=lambda c: (-cnt[c], seen.index(c)))[0]
    return np.array([1 if maj.get(int(np.argmax(mu @ space[t]))) == c else 0 for t, c in heldout])


def _indep_split(W, k):
    S = W["splits"][k]
    hn = _indep_hits(W["trees"][("N", k)], W["spaces"]["N"], S["train"], S["heldout"])
    hq = _indep_hits(W["trees"][("Q", k)], W["spaces"]["Q"], S["train"], S["heldout"])
    n = len(hn)
    b = int(((hn == 1) & (hq == 0)).sum())
    c = int(((hn == 0) & (hq == 1)).sum())
    g = (b - c) / n
    se = math.sqrt(b + c - (b - c) ** 2 / n) / n
    return dict(topN=float(hn.mean()), topQ=float(hq.mean()), b=b, c=c, n=n, G=g, lo=g - Z95 * se, hi=g + Z95 * se)


def _indep_all(W):
    ind = [_indep_split(W, k) for k in (1, 2, 3)]
    sN = max(i_["topN"] for i_ in ind) - min(i_["topN"] for i_ in ind)
    sQ = max(i_["topQ"] for i_ in ind) - min(i_["topQ"] for i_ in ind)
    gbar = sum(i_["G"] for i_ in ind) / 3
    ms = max(sN, sQ)
    if all(i_["hi"] < 0 for i_ in ind) and gbar < -ms:
        v = "WORSE"
    elif all(i_["lo"] > 0 for i_ in ind) and gbar > ms:
        v = "BETTER"
    else:
        v = "NEITHER"
    fsd = any(i_["G"] >= 0 for i_ in ind) or abs(gbar) <= ms
    return ind, sN, sQ, gbar, v, fsd


def _go(fn):
    """Run fn with stdout captured. -> (result or 'REFUSED', text, the SystemExit message)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = fn()
        return r, buf.getvalue(), ""
    except SystemExit as e:
        return "REFUSED", buf.getvalue(), str(e)


def _line(text, needle):
    got = [l for l in text.splitlines() if needle in l]
    return got[0] if got else ""


def selftest(quiet=False):
    """Every deciding path EXECUTED through run() or dry_run() on fixtures whose answers are known, with VALUE assertions. The expected
    verdicts are computed INDEPENDENTLY (_indep_all: own argmax, own majority, own Wald, own spreads and rule) AND fixed by design:
    ST-W1 WORSE, P1 / P2 HELD: N = m4 x3 vs Q = full x3 (G_k ~ -0.04, small spreads): per split b, c, n, G_k, interval and top-1s ==
          independent on the split's OWN held-out (n == its held-out count, != TRAIN); spreads, Gbar == independent; SD1 WORSE and
          F-SD not fired printed; P1 HELD, P2 HELD, P3 / P4 / P5 Brier values; the outcome file written once (a second run REFUSES).
    ST-W2 WORSE, P1 / P2 FAILED: N = m3 x3 vs Q = full (G_k ~ -0.12).
    ST-N1 NEITHER by an interval: N = m3, m3, full (G_3 = 0): clause 1 NO; F-SD FIRES on any G_k >= 0 (first-split-only and 'all G_k
          >= 0' rules would read otherwise).
    ST-N2 NEITHER by the spread: N = m4, m34, m4 vs Q = full: every interval below 0 but |Gbar| <= spread_N (> spread_Q): clause 2 NO;
          F-SD FIRES on the spread alone (a min(spread) rule reads WORSE).
    ST-B BETTER: N = full x3 vs Q = m3 x3: SD1 BETTER printed; F-SD FIRES (G_k >= 0).
    ST-BOUND sd1_verdict / fsd_fires at Gbar == -max spread (NEITHER, fires), hi == 0 / lo == 0 on the third split, G_3 == 0.
    ST-I a wrong identity expectation REFUSES before any outcome; the E1 pair's G (~ -0.16) differs from Gbar (never pooled).
    ST-A a build ABSENT: --dry-run prints the identity, then REFUSES naming it; --run REFUSES; all present: dry-run complete, no SD1.
    ST-G a wrong depth-1 vmfMu on the SECOND split's N tree REFUSES; a held-out text in Q_e1sd3 REFUSES (hygiene); a run dir with
          closedByContent 2 REFUSES (check_run_dir); a discriminator that ADMITS REFUSES."""
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)

    td = tempfile.mkdtemp(prefix="e1sd_ro_")

    def scenario(tag, plan, **kw):
        loader, W = _fx_world(os.path.join(td, tag), plan, **kw)
        out = os.path.join(td, tag + "_out")
        res, text, msg = _go(lambda: run(loader, out))
        ok(res != "REFUSED", "%s run admitted (%s)" % (tag, msg[:300]))
        return loader, W, out, res, text, msg

    def common(tag, W, res, text, want_v, want_fsd):
        ind, sN, sQ, gbar, v, fsd = _indep_all(W)
        ok(v == want_v and bool(fsd) == want_fsd, "%s fixture by design: independent verdict %s, F-SD %s (G %s, spreads %.4f / %.4f)"
           % (tag, v, fsd, ["%+.4f" % i_["G"] for i_ in ind], sN, sQ))
        for k in (1, 2, 3):
            s, i_ = res["splits"][k - 1], ind[k - 1]
            ok(s["n"] == len(W["splits"][k]["heldout"]) == i_["n"] and s["n"] != len(W["splits"][k]["train"]),
               "%s split %d n = its held-out %d" % (tag, k, s["n"]))
            ok((s["mc"]["b"], s["mc"]["c"]) == (i_["b"], i_["c"]) and abs(s["mc"]["diff"] - i_["G"]) < 1e-12
               and abs(s["mc"]["lo"] - i_["lo"]) < 1e-12 and abs(s["mc"]["hi"] - i_["hi"]) < 1e-12
               and abs(s["topN"] - i_["topN"]) < 1e-12 and abs(s["topQ"] - i_["topQ"]) < 1e-12,
               "%s split %d: b %d c %d G %+.4f [%+.4f, %+.4f] == independent" % (tag, k, i_["b"], i_["c"], i_["G"], i_["lo"], i_["hi"]))
            ok(("G_%d = (b - c) / n = %+.4f" % (k, i_["G"])) in text, "%s split %d G printed by value" % (tag, k))
        ok(abs(res["spread_N"] - sN) < 1e-12 and abs(res["spread_Q"] - sQ) < 1e-12 and abs(res["clauses"]["gbar"] - gbar) < 1e-12,
           "%s spreads %.4f / %.4f, Gbar %+.4f == independent" % (tag, sN, sQ, gbar))
        ok(res["sd1"] == want_v and ("SD1 VERDICT: %s" % want_v) in text, "%s SD1 %s printed" % (tag, want_v))
        ok(bool(res["fsd"]) == want_fsd and ((FSD_FIRES if want_fsd else FSD_NOT) in text),
           "%s F-SD %s printed" % (tag, "FIRES" if want_fsd else "not fired"))
        p4 = {"WORSE": 0.3878, "NEITHER": 0.6278, "BETTER": 1.4478}[want_v]      # literals: (1-p)^2 + the other two p^2
        ok(("P4 SD1 verdict (WORSE 0.55, NEITHER 0.43, BETTER 0.02): %s; Brier (3-class) %.4f" % (want_v, p4)) in text,
           "%s P4 Brier %.4f" % (tag, p4))
        ok(("P5 F-SD fires (prior 0.40): %s; Brier %.4f" % ("FIRED" if want_fsd else "did not fire", 0.36 if want_fsd else 0.16)) in text,
           "%s P5 Brier" % tag)
        p3 = all(i_["hi"] < 0 for i_ in ind)
        ok(("P3 all three per-split intervals below 0 (prior 0.70): %s; Brier %.4f" % ("occurred" if p3 else "did not occur",
                                                                                      0.09 if p3 else 0.49)) in text, "%s P3 Brier" % tag)
        return ind, sN, sQ, gbar

    try:
        # ST-W1
        loader, W, out, res, text, msg = scenario("w1", {1: ("m4h", "full"), 2: ("m4", "full"), 3: ("m4", "full")})
        ind, sN, sQ, gbar = common("ST-W1", W, res, text, "WORSE", False)
        ok(res["splits"][0]["cellsN"] == 1 and "held-out cells with no TRAIN text N 1 / Q 0" in _line(text, "  split 1: G"),
           "ST-W1 split 1's N tree has one held-out cell no TRAIN text reaches (a miss under the TRAIN majority)")
        ok(WORSE_LINE in text and VERDICT_F in text and "IDENTITY PRECONDITION (HELD)" in text and "E1 PAIR = DESCRIPTIVE 4th POINT" in text,
           "ST-W1 WORSE line, (f), identity, 4th point printed")
        ok("TIE CONVENTIONS A, B: not applicable" in text and DOES_NOT_SHOW in text, "ST-W1 R6 and DOES NOT SHOW printed")
        ok(res["p1"] is True and "-> P1 HELD" in text and res["p2"] is True and "-> P2 HELD" in text,
           "ST-W1 P1 HELD (G %s, Gbar %+.4f), P2 HELD (spreads %.4f / %.4f)" % (["%+.4f" % i_["G"] for i_ in ind], gbar, sN, sQ))
        ok(abs(res["e1"]["diff"] - gbar) > 0.05, "ST-W1 the E1 pair's G %+.4f is not Gbar %+.4f (not pooled)" % (res["e1"]["diff"], gbar))
        ok(os.path.isfile(os.path.join(out, OUTCOME)), "ST-W1 outcome file written")
        r2, t2, m2 = _go(lambda: run(loader, out))
        ok(r2 == "REFUSED" and "write-once" in m2, "ST-W1 a second --run REFUSES (write-once)")
        # ST-W2
        loader, W, out, res, text, msg = scenario("w2", {1: ("m3", "full"), 2: ("m3", "full"), 3: ("m3", "full")})
        common("ST-W2", W, res, text, "WORSE", False)
        ok(res["p1"] is False and "-> P1 FAILED" in text and "OUT" in _line(text, "P1 each"), "ST-W2 P1 FAILED printed")
        ok(("-> P2 %s" % ("HELD" if res["p2"] else "FAILED")) in text, "ST-W2 P2 line printed by value")
        # ST-N1
        loader, W, out, res, text, msg = scenario("n1", {1: ("m3", "full"), 2: ("m3", "full"), 3: ("full", "full")})
        common("ST-N1", W, res, text, "NEITHER", True)
        ok(abs(res["G"][2]) < 1e-12 and res["clauses"]["all_below"] is False and res["fsd_any_nonneg"] is True and "never parity" in text,
           "ST-N1 G_3 = 0: clause 1 NO, F-SD on any G_k >= 0")
        # ST-N2
        loader, W, out, res, text, msg = scenario("n2", {1: ("m4", "full"), 2: ("m34", "full"), 3: ("m4", "full")})
        ind, sN, sQ, gbar = common("ST-N2", W, res, text, "NEITHER", True)
        ok(res["clauses"]["all_below"] is True and res["clauses"]["beyond"] is False and res["fsd_any_nonneg"] is False
           and res["fsd_inside"] is True and min(sN, sQ) < abs(gbar) <= max(sN, sQ),
           "ST-N2 all intervals below 0; min spread %.4f < |Gbar| %.4f <= max spread %.4f: F-SD on the spread alone"
           % (min(sN, sQ), abs(gbar), max(sN, sQ)))
        ok(res["p2_N"] is False and res["p2_Q"] is True and res["p2"] is False and "-> P2 FAILED" in text,
           "ST-N2 P2 FAILED on spread_N %.4f (spread_Q %.4f in)" % (sN, sQ))
        # ST-N3: N = m4, m4, full: G_3 = 0 (NEITHER) while Gbar lies inside P1's Gbar interval: P1 FAILED on a per-split component
        loader, W, out, res, text, msg = scenario("n3", {1: ("m4", "full"), 2: ("m4", "full"), 3: ("full", "full")})
        ind, sN, sQ, gbar = common("ST-N3", W, res, text, "NEITHER", True)
        ok(res["p1_gbar"] is True and res["p1_each"][2] is False and res["p1"] is False and "-> P1 FAILED" in text,
           "ST-N3 Gbar %+.4f in [-0.060, -0.020] but G_3 %+.4f OUT: P1 FAILED" % (gbar, res["G"][2]))
        # ST-B
        loader, W, out, res, text, msg = scenario("b", {1: ("full", "m3"), 2: ("full", "m3"), 3: ("full", "m3")})
        common("ST-B", W, res, text, "BETTER", True)
        ok("SD1 BETTER (symmetric" in text and res["clauses"]["all_above"] is True, "ST-B BETTER line printed")
        # ST-BOUND
        v3, cl3 = sd1_verdict([-0.25, -0.25, -0.25], [-0.3] * 3, [-0.2] * 3, 0.25, 0.0)
        f3, _a3, i3 = fsd_fires([-0.25, -0.25, -0.25], cl3["gbar"], cl3["max_spread"])
        ok(v3 == "NEITHER" and f3 is True and i3 is True, "ST-BOUND Gbar == -max spread: NEITHER and F-SD fires (strict < and <=)")
        v4, _ = sd1_verdict([-0.25, -0.25, -0.25], [-0.3, -0.3, -0.3], [-0.2, -0.2, 0.0], 0.0, 0.0)
        ok(v4 == "NEITHER", "ST-BOUND the third interval's hi == 0: NEITHER (wholly below means < 0; all, not first)")
        v5, _ = sd1_verdict([0.25, 0.25, 0.25], [0.2, 0.2, 0.0], [0.3, 0.3, 0.3], 0.0, 0.0)
        ok(v5 == "NEITHER", "ST-BOUND BETTER needs every lo > 0 (third lo 0.0 -> NEITHER)")
        f6, a6, _i6 = fsd_fires([-0.2, -0.2, 0.0], -0.133, 0.01)
        ok(f6 is True and a6 is True, "ST-BOUND F-SD: G_3 == 0 counts as >= 0")
        # ST-I
        loader, W = _fx_world(os.path.join(td, "i"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")}, ident_expect=dict(IDENTITY))
        r_, t_, m_ = _go(lambda: run(loader, os.path.join(td, "i_out")))
        ok(r_ == "REFUSED" and "IDENTITY PRECONDITION" in m_ and not os.path.exists(os.path.join(td, "i_out", OUTCOME)),
           "ST-I a wrong identity REFUSES before any outcome is written")
        # ST-A
        loader, W = _fx_world(os.path.join(td, "a"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")}, absent=("Q_e1sd3",))
        r_, t_, m_ = _go(lambda: dry_run(loader))
        ok(r_ == "REFUSED" and "builds ABSENT (1 of 6): ['Q_e1sd3']" in m_ and "IDENTITY: E1 pair" in t_ and "-> HELD" in t_,
           "ST-A dry-run prints the identity (HELD), then REFUSES naming the ABSENT build Q_e1sd3")
        r_, t_, m_ = _go(lambda: run(loader, os.path.join(td, "a_out")))
        ok(r_ == "REFUSED" and "ABSENT" in m_, "ST-A --run REFUSES with a build ABSENT")
        loader, W = _fx_world(os.path.join(td, "a2"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")})
        r_, t_, m_ = _go(lambda: dry_run(loader))
        ok(r_ == 0 and "dry-run complete" in t_ and "SD1 VERDICT" not in t_ and not os.path.exists(os.path.join(td, "a2_out")),
           "ST-A dry-run with all six present: complete, no SD1 measure, nothing written")
        # ST-G

        def bad_mu(nodes, W):
            nodes[2]["vmfMu"] = list(map(float, -np.asarray(nodes[2]["vmfMu"])))      # D1 (a depth-1 site), not the root
            return nodes
        loader, W = _fx_world(os.path.join(td, "g1"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")},
                              graph_over={"N_e1sd2": bad_mu})
        r_, t_, m_ = _go(lambda: run(loader, os.path.join(td, "g1_out")))
        ok(r_ == "REFUSED" and "[EMB-GUARD] N_e1sd2 on its own nomic_raw vectors" in m_, "ST-G a wrong depth-1 vmfMu (split 2's N) REFUSES")

        def leak(nodes, W):
            ht = W["splits"][3]["heldout"][0][0]
            for n_ in nodes:
                if n_.get("isLeaf") and n_["queryIds"]:
                    n_["queryIds"] = n_["queryIds"] + [qid(ht)]
                    break
            return nodes
        loader, W = _fx_world(os.path.join(td, "g2"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")},
                              graph_over={"Q_e1sd3": leak})
        r_, t_, m_ = _go(lambda: run(loader, os.path.join(td, "g2_out")))
        ok(r_ == "REFUSED" and "Q_e1sd3: held-out content reaches the tree" in m_, "ST-G a held-out text in Q_e1sd3 REFUSES (hygiene)")
        r_, t_, m_ = _go(lambda: _fx_world(os.path.join(td, "g3"), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")},
                                           run_dir_over={"N_e1sd1": dict(closed=2)}))
        ok(r_ == "REFUSED" and "[POOL] line" in m_, "ST-G a run dir with closedByContent 2 REFUSES (check_run_dir)")
        saved = E1R.text_join_guard
        try:
            for which in ("x OTHER", "x PERMUTED"):
                def lenient(byid, rf, id2text, blobs, model, label, slice_dim=DIM, which=which):
                    if which in label:
                        return dict(admitted=True)
                    return saved(byid, rf, id2text, blobs, model, label, slice_dim)
                E1R.text_join_guard = lenient
                loader, W = _fx_world(os.path.join(td, "g4" + which[2:]), {1: ("m4", "full"), 2: ("m4", "full"), 3: ("m4", "full")})
                r_, t_, m_ = _go(lambda: run(loader, os.path.join(td, "g4_out" + which[2:])))
                ok(r_ == "REFUSED" and "a discriminator was ADMITTED" in m_, "ST-G the '%s' discriminator alone ADMITTING REFUSES" % which)
        finally:
            E1R.text_join_guard = saved
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("%s SELFTEST PASSED (%d checks)" % (TAG, n[0]))
    return 0


MUTANTS = (
    ("R01 spread min<->max (min - max)", "    return float(max(vals) - min(vals))\n\n\ndef sd1_verdict", "    return float(min(vals) - max(vals))\n\n\ndef sd1_verdict"),
    ("R02 max spread -> min spread", "    ms = max(spread_n, spread_q)", "    ms = min(spread_n, spread_q)"),
    ("R03 all intervals -> first split only", "    all_below = bool(all(h < 0 for h in hi))", "    all_below = bool(hi[0] < 0)"),
    ("R04 all intervals -> any", "    all_below = bool(all(h < 0 for h in hi))", "    all_below = bool(any(h < 0 for h in hi))"),
    ("R05 strict Gbar < -spread -> <=", "    if all_below and gbar < -ms:", "    if all_below and gbar <= -ms:"),
    ("R06 BETTER lo > 0 -> lo >= 0", "    all_above = bool(all(l_ > 0 for l_ in lo))", "    all_above = bool(all(l_ >= 0 for l_ in lo))"),
    ("R07 F-SD any G_k >= 0 -> all", "    any_nonneg = bool(any(g >= 0 for g in G))", "    any_nonneg = bool(all(g >= 0 for g in G))"),
    ("R08 F-SD >= 0 -> > 0", "    any_nonneg = bool(any(g >= 0 for g in G))", "    any_nonneg = bool(any(g > 0 for g in G))"),
    ("R09 F-SD inside <= -> <", "    inside = bool(abs(gbar) <= ms)", "    inside = bool(abs(gbar) < ms)"),
    ("R10 hits on TRAIN instead of held-out", "    sc, hits, _kh = FM.m1_block(fn, E1R.mat(vec, [t for t, _ in train]), E1R.mat(vec, [t for t, _ in heldout]), train, heldout)",
     "    sc, hits, _kh = FM.m1_block(fn, E1R.mat(vec, [t for t, _ in train]), E1R.mat(vec, [t for t, _ in train]), train, train)"),
    ("R11 majority from held-out (wrong population)", "    sc, hits, _kh = FM.m1_block(fn, E1R.mat(vec, [t for t, _ in train]), E1R.mat(vec, [t for t, _ in heldout]), train, heldout)",
     "    sc, hits, _kh = FM.m1_block(fn, E1R.mat(vec, [t for t, _ in heldout]), E1R.mat(vec, [t for t, _ in heldout]), heldout, heldout)"),
    ("R12 N tree read in the Q space", "        hn, scn = filing_hits(W[\"trees\"][(\"N\", k)], W[\"spaces\"][\"N\"], S[\"train\"], S[\"heldout\"])",
     "        hn, scn = filing_hits(W[\"trees\"][(\"N\", k)], W[\"spaces\"][\"Q\"], S[\"train\"], S[\"heldout\"])"),
    ("R13 Gbar pools the E1 pair", "    v, cl = sd1_verdict(G, lo, hi, sN, sQ)",
     "    v, cl = sd1_verdict(G + [res[\"e1\"][\"diff\"]], lo + [res[\"e1\"][\"lo\"]], hi + [res[\"e1\"][\"hi\"]], sN, sQ)"),
    ("R14 identity not enforced", "    if not held:\n        refuse(\"IDENTITY PRECONDITION", "    if False:\n        refuse(\"IDENTITY PRECONDITION"),
    ("R15 dry-run ignores ABSENT builds", "    if W[\"absent\"]:\n        say(L, \"[MODE] --dry-run: builds ABSENT", "    if False:\n        say(L, \"[MODE] --dry-run: builds ABSENT"),
    ("R16 outcome not write-once", "    if os.path.exists(oc):\n        refuse(", "    if False:\n        refuse("),
    ("R17 discriminators not enforced", "    if ok_o or ok_s:\n        refuse(", "    if False:\n        refuse("),
    ("R18 hygiene not enforced", "    if not_train or in_ho or keys:\n        refuse(", "    if False:\n        refuse("),
    ("R19 guard on own vectors not enforced", "    if not ok_:\n        refuse(\"[EMB-GUARD] %s on its own", "    if False:\n        refuse(\"[EMB-GUARD] %s on its own"),
    ("R20 P3 event = any interval below 0", "               p3_event=bool(all(h < 0 for h in hi)))", "               p3_event=bool(any(h < 0 for h in hi)))"),
    ("R21 P4 Brier on the realised class only", "    return float(sum((p - (1.0 if c == outcome else 0.0)) ** 2 for c, p in probs.items()))",
     "    return float((probs[outcome] - 1.0) ** 2)"),
    ("R22 run skips the guards (admit)", "    admit(W, L)\n    res = compute(W)", "    res = compute(W)"),
    ("R23 BETTER branch line dropped", "        L.append(\"  SD1 BETTER (symmetric; K = 3 named)", "        L.append(\"  SD1 (symmetric; K = 3 named)"),
    ("R24 F-SD fired line dropped", "    L.append(\"  \" + (FSD_FIRES if res[\"fsd\"] else FSD_NOT))", "    L.append(\"  \" + FSD_NOT)"),
    ("R25 denominator b + c instead of n", "    mc = E1R.mcnemar(hn, hq)\n", "    mc = E1R.mcnemar(hn, hq)\n    mc[\"diff\"] = (mc[\"b\"] - mc[\"c\"]) / max(1, mc[\"b\"] + mc[\"c\"])\n"),
    ("R26 run skips the identity check", "    W = loader(L)\n    identity_check(W, L)\n    if W[\"absent\"]:\n        refuse(\"builds ABSENT: %s\"",
     "    W = loader(L)\n    if W[\"absent\"]:\n        refuse(\"builds ABSENT: %s\""),
    ("R27 P1 per-split component dropped", "    res[\"p1\"] = bool(all(p1_each) and res[\"p1_gbar\"])", "    res[\"p1\"] = bool(res[\"p1_gbar\"])"),
    ("R28 P2 spread_N component dropped", "    res[\"p2\"] = bool(res[\"p2_N\"] and res[\"p2_Q\"])", "    res[\"p2\"] = bool(res[\"p2_Q\"])"),
    ("R29 WORSE line dropped", "        L.append(\"  \" + WORSE_LINE)", "        pass"),
    ("R31 other-arm discriminator removed", "    ok_o, _o, ml_o, _e = guard_tree(label + \" x OTHER arm\", arm, byid, id2text, other_blobs)",
     "    ok_o, _o, ml_o, _e = False, \"\", \"-\", None"),
    ("R30 permuted-map discriminator removed", "    ok_s, _s, ml_s, _e2 = guard_tree(label + \" x PERMUTED map\", arm, byid, shuffled, blobs)",
     "    ok_s, _s, ml_s, _e2 = False, \"\", \"-\", None"),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    head, sep, tail_ = src.partition("\nMUTANTS = (")
    killed = 0
    rows = []
    for name, a, b in MUTANTS:
        if head.count(a) != 1:
            print("%s MUTANT %s: anchor found %d times (must be 1)" % (TAG, name, head.count(a)))
            return 2
        p = os.path.join(HERE, "_mut_e1_split_draws.py")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(head.replace(a, b) + sep + tail_)
        try:
            r = subprocess.run([sys.executable, p, "--selftest", "--quiet"], capture_output=True, text=True)
        finally:
            os.remove(p)
        dead = r.returncode != 0
        killed += dead
        why = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["?"])[-1][:110] if dead else "SURVIVED"
        rows.append((name, dead, why))
        print("%s MUTANT %-48s %s  (%s)" % (TAG, name, "KILLED" if dead else "SURVIVED", why))
    print("%s MUTANTS %d of %d KILLED" % (TAG, killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(quiet=a.quiet)
    if a.mutants:
        return run_mutants()
    try:
        if a.dry_run:
            return dry_run(lambda L: load_real(L))
        run(lambda L: load_real(L), data_path(OUT_DIR))
        return 0
    except SystemExit as e:
        if isinstance(e.code, int):
            return e.code
        return 2


if __name__ == "__main__":
    sys.exit(main())
