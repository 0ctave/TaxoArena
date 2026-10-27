"""FITSET-INTENT: does FITSET-FAITHFUL's leaf-mean refit on class-pure TRAIN fit sets also improve fine filing on
INTENT-TRANSFER-S1's anchored trees (M-AN 82 leaves, C-AN 131; known answers), or was stage 0's gain an MMLU-Pro effect?
ZERO calls: no judge, no LLM, no embedding call, no build, no Gradle. Every DB is opened read-only through S1's readers.

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — FITSET-INTENT: does
FITSET-FAITHFUL's leaf-mean refit on class-pure TRAIN fit sets also improve fine filing on INTENT-TRANSFER-S1's anchored trees
..." (L23888-L23899, commit d50c47d4); docs/agents/results/FITSET-INTENT.json.

INSTRUMENT (imported UNCHANGED, blob-pinned, LF): intent_transfer_s1.py 4e9d9d05 (arm_presence, load_world, census, derive_inputs,
load_tree_checked, make_arm, phase_gate (TRAIN / GATE only: leaf fine labels, k-means at k = L seeds 0-19, descent acceptance),
fit_idx (THE TRAIN-ONLY guard, audited in FIT_LOG), eval_rows (refuses before the GATE freeze), fine_correct_flat, flat_leaf,
majority, t_c8, boot (S0.comp_weights percentile, B 2,000), wmean); fitset_faithful.py ed343065 (refit_cells = the A-refit rule,
v_ff1 = DSC.v_spread = FF1's verdict form). intent_s1_export.pretty maps a coarse label to its anchor's engine label.

OBJECTS: S1's M-AN / C-AN snapshots chosen by the run log's single "Snapshot ID:" (S1.arm_presence; never the latest timestamp):
M-AN 20261002_213331_Headless_Run_Auto_ge (82 leaves), C-AN 20261002_214129_Headless_Run_Auto_ge (131 leaves), both at slice
512 (the AN recipe); qwen3 vectors (intent_emb_qwen3.db) and the ingest DB, S0-pinned (strict) and re-hashed after the readout.
Anchors = the root's children; each anchor's label must equal pretty(coarse) of exactly one TRAIN coarse class (bijection, else
REFUSE); a leaf's anchor = its depth-1 ancestor by treeParents (a multi-parent graph REFUSES).

ARMS (per corpus; filing = fine filing precision, S1's R3: a cell's label = the TRAIN-majority FINE intent of the TRAIN items
flatLeaf files to it (ties to the smaller label); an EVAL item filed to a cell with no TRAIN item is WRONG):
  A        = the tree as built: S1.fine_correct_flat (the leaves' vmfMu; S1's own labels; cross-checked by this script's filer).
  A-refit  = FITSET-FAITHFUL's rule through FF.refit_cells UNCHANGED: leaves and topology fixed; in each anchor the TRAIN items of
             the anchor's declared coarse class (S1.fit_idx: TRAIN only, audited) are assigned to the nearest leaf UNDER that
             anchor (cosine to the leaf vmfMu) and each leaf mean re-estimated (normalised mean); a leaf receiving none keeps its
             vmfMu; an unsplit anchor's cell = the normalised mean of its class's TRAIN items. Cells renamed and EVAL filed by
             argmax over ALL refit cells (S1's R3 rule above).
  K_s      = spherical k-means at k = L (S1.phase_gate's own TRAIN fits, seeds 0-4 of its 0-19), named and filed by the same rule.
IDENTITY (refuses before any new number): (i) Snapshot IDs and leaf counts = S1's ARMS line; (ii) S1's outcome of record
(s1_outcome.txt sha256 a25c6227..., s1_items.csv 0c52a9c3...) carries the six lines quoted in REG["s1_lines"]; (iii) the descent
port ACCEPTED on GATE (S1's (a)); (iv) S1's printed descriptive numbers reproduced to their 5 printed digits: T-C8 D_fd (S1.t_c8:
flatLeaf fine precision = P(A) minus descent), T-C1 D1 (the point of S1.t_c1, recomputed with S0.nmi on the same k-means fits) and
delta_c on GATE. [DEVIATION, disclosed for the READY / registrar: the registered identity reads "the as-built trees reproduce S1's
flatLeaf assignments (s1_items.csv)", but s1_items.csv holds M-AF and C-AF rows only (4,946 + 6,672); for M-AN / C-AN rows present
the flat leaves are compared item by item (refuse on any difference); when absent (the record) the identity is read through (iv),
whose D_fd is a function of exactly those flatLeaf assignments and labels.]
EVAL denominators must equal the registered MASSIVE 4,946 items / 4,923 components and CLINC 6,672 / 6,672 exactly (refuse).

CRITERIA (registered; 95% component-bootstrap percentile intervals, item-paired; per corpus):
  FI1 (DECIDING): D = P(A-refit) - P(A) on EVAL. HELD iff the interval lies wholly above 0 AND D > spread_K (max - min over seeds
      0-4 of the k-means fine filing precision, measured in-run); REVERSED iff wholly below 0 AND D < -spread_K; UNDETERMINED
      otherwise (FF.v_ff1 = DSC.v_spread). READING: BEYOND-MMLU iff FI1 HELD on at least one corpus; NOT-SHOWN otherwise.
  F-FI (falsifier): fires iff FI1 is UNDETERMINED or REVERSED on both corpora (= NOT-SHOWN).
  VERDICT LINE (Support (f)): DESCRIPTIVE-ONLY at the prediction (D +0.005 below both planning bars 0.015 / 0.010); printed.
SUPPORT printed beside FI1 per corpus: denominator (items / components), SE (bootstrap SD), DEFF measured (SE^2 over the iid
variance) and Kish (the components' own sizes) beside the transported 1.052, n_eff, MDE80 = 2.8 SE, discordance (planning 0.06),
spread_K beside the planning bar; registered SE 0.00357 / 0.00308, MDE80 0.0100 / 0.0086, n_eff 4,702 / 6,342.
PREDICTIONS: P1 D +0.005 [-0.005, +0.020] per corpus (band inclusive); FI1 HELD on >= 1 corpus p 0.25 (event and Brier);
P2 discordance 0.03 [0.01, 0.08] per corpus. Not applicable (no judge): wrong(established), tie conventions, pilot / truncation
guard, call cache. The outcome prints the registered LIKE-WITH-LIKE (label information) table, the confounds and WILL-NOT-SHOW.

SELFTEST (--selftest; fixtures only, nothing real is read): a hand-built anchored world (2 corpora x 5 anchors: alpha split in
3 leaves with LA2's vmfMu dragged toward foreign zeta TRAIN items, beta split in 2 with mixed b1 items that the refit pulls into
LB2, unsplit gamma whose class mean leaves its vmfMu, unsplit zeta whose vmfMu receives no TRAIN item, unsplit delta), k-means
fits replaced by hand centroid sets per seed, executed through main() (the real entry point; only the DB loader, the java probe
and S0.skmeans are stubbed). Hand values: P(A) = (70 + n_b1mix)/n, P(A-refit) = (70 + n_a2 + n_g1mix)/n, P_K seeds 0-4 =
(70 + n_a2 + n_b1mix)/n except seed 1 (+ n_g1mix), so spread_K = n_g1mix / n and D = (n_a2 + n_g1mix - n_b1mix)/n.
  e2e_UH --run: MASSIVE n 118 (98 components, Kish 1.508475) D 29/118 = +0.2458 with the interval above 0 but D < spread_K
    30/118 -> UNDETERMINED (the spread conjunct decides); CLINC n 114 D 19/114 = +0.1667 > spread_K 12/114 -> HELD; READING
    BEYOND-MMLU; F-FI DOES NOT FIRE; intervals against an independent component-bootstrap oracle; per-anchor rows, refit
    bookkeeping (1 leaf with no item, 2 naming changes), predictions; the outcome is write-once (re-run refuses, file unchanged).
  e2e_RZ --run: MASSIVE n 123 D -36/123 -> REVERSED; CLINC n 79, D 0, interval [0, 0], spread_K 0 -> UNDETERMINED, DEFF n/a;
    NOT-SHOWN; F-FI FIRES; an M-AN row set in s1_items.csv compared item by item.
  dry_run: pins, denominators, the TRAIN-side refit bookkeeping; no D, no FI1, no prediction, no file.
  refusals: write-once before any read, java probe, Snapshot ID, leaf count, s1 outcome sha, a missing s1 line, s1_items AN
    mismatch, each identity constant (D_fd, D1, delta_c), descent not accepted, registered n / G, anchor label off-class, a class
    without anchor, multi-parent, the TRAIN-ONLY guard.
  branches: every FI1 / READING / F-FI print branch with values and boundaries (D = spread_K, lo = 0, hi = 0); predictions
    (inclusive bands, NaN NOT SCORED, Brier).
MUTANTS (--mutants; in-memory edits, the targeted selftest subset re-run; 2026-10-03: 50 of 50 KILLED, control survived; the
table is printed by --mutants and recorded in the commit message). First pass: 46 of 48; M42 (P2 scored on D) and M47 (a
no-TRAIN refit leaf dropped) survived and were killed by a P2 branch where D and discordance straddle the band and by giving the
a1e9 probe a small e0 component. Known limit: on the fixture S1's descent equals flatLeaf, so T-C8 D_fd is +0.00000 there; the
D_fd identity is S1.t_c8 itself (reviewed with S1) and its refusal is exercised by a perturbed constant.

LAUNCH SEQUENCE (the run-operator; reads snapshots.db and the intent DBs: never beside a running java, which REFUSES):
  python tools/analysis/fitset_intent.py --selftest
  python tools/analysis/fitset_intent.py --mutants
  TAXOARENA_DATA_ROOT=<checkout holding the S1 builds and intent DBs> python tools/analysis/fitset_intent.py --dry-run
  TAXOARENA_DATA_ROOT=<same> python tools/analysis/fitset_intent.py --run      # file of record, write-once (mode x)
  (--s1-dir <dir holding s1_outcome.txt / s1_items.csv>, default <this checkout>/experiment_results/intent_transfer;
   --out <path>, default <this checkout>/experiment_results/intent_transfer/fitset_intent_outcome.txt; never committed)
stdout: PYTHONIOENCODING=utf-8. CPU single-threaded (OMP / OPENBLAS / MKL = 1); 20 k-means fits per corpus (S1's phase_gate).
"""
import os
import sys

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse      # noqa: E402
import contextlib    # noqa: E402
import csv           # noqa: E402
import hashlib       # noqa: E402
import io            # noqa: E402
import json          # noqa: E402
import sqlite3       # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[FI]"
PINS = (("intent_transfer_s1.py", "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d"),
        ("fitset_faithful.py", "ed34306596ef63ba2d4b59bc24d54fad0eb8149a"))


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
import intent_transfer_s1 as S1      # noqa: E402  (S1 imports S0, g13_comparator, intent_s1_export, split_side, intent_ingest)
import fitset_faithful as FF         # noqa: E402  (checks deep_split_compare / g13_breakdown pins at import)
if hasattr(sqlite3.connect, "_raw"):  # flat_mix_mmlu's process-wide guard (S1 restores it; restored again if re-applied)
    sqlite3.connect = sqlite3.connect._raw
S0, EX, SS, II = S1.S0, S1.EX, S1.SS, S1.II

ARMS_AN = ("M-AN", "C-AN")
CORPUS_OF = {"M-AN": "massive", "C-AN": "clinc"}
UP = {"massive": "MASSIVE", "clinc": "CLINC"}
SEEDS5 = (0, 1, 2, 3, 4)
SEED_FI = 20261003 + 90                  # this readout's bootstrap seed (+0 MASSIVE, +1 CLINC); S1's offsets end at 80
B_BOOT = S1.BOOT_B

REG = dict(
    out=os.path.join(ROOT, "experiment_results", "intent_transfer", "fitset_intent_outcome.txt"),
    s1_dir=os.path.join(ROOT, "experiment_results", "intent_transfer"),
    sid={"M-AN": "20261002_213331_Headless_Run_Auto_ge", "C-AN": "20261002_214129_Headless_Run_Auto_ge"},
    leaves={"M-AN": 82, "C-AN": 131},
    ident={"M-AN": dict(dfd="+0.02467", d1="+0.00714", delta_c="0.01966"),
           "C-AN": dict(dfd="+0.08019", d1="+0.00706", delta_c="0.01414")},
    s1_sha={"outcome": "a25c6227e67e872ec7c39b30271d856cfa8b4e8e07f7763f221fd8281a807338",
            "items": "0c52a9c3f5ee26ab63fabf778e9347774d433bf06ee91eb5b2420e141d7b29b6"},
    s1_lines=("M-AN snapshot 20261002_213331_Headless_Run_Auto_ge leaves 82 (no-TRAIN leaves 0)",
              "C-AN snapshot 20261002_214129_Headless_Run_Auto_ge leaves 131 (no-TRAIN leaves 0)",
              "M-AN delta_c 0.01966 (NMI sup 0.86729, km mean 0.78865, n_gate 1691)",
              "C-AN delta_c 0.01414 (NMI sup 0.97832, km mean 0.92176, n_gate 2333)",
              "DESCRIPTIVE M-AN: T-C1 D1 +0.00714 [EQUIVALENT]; T-C8 D_fd +0.02467 (never contrasted as a criterion)",
              "DESCRIPTIVE C-AN: T-C1 D1 +0.00706 [EQUIVALENT]; T-C8 D_fd +0.08019 (never contrasted as a criterion)"),
    n_reg={"massive": (4946, 4923), "clinc": (6672, 6672)},
)
_CFG = [REG]


def cfg():
    return _CFG[0]


# registered Support (b)-(e) per corpus: SE, MDE80, n_eff, planning bar; transported DEFF; planning discordance
SUPPORT = {"massive": dict(se=0.00357, mde=0.0100, neff=4702, bar=0.015), "clinc": dict(se=0.00308, mde=0.0086, neff=6342, bar=0.010)}
DEFF_T, DISC_PLAN = 1.052, 0.06
P1_BAND, P1_PT = (-0.005, 0.020), 0.005
P2_BAND, P2_PT = (0.01, 0.08), 0.03
P_HELD_ANY = 0.25

# hooks the selftest swaps (nothing else writes them)
_HEAVY = [S0._foreign_heavy]


# ── loading (real) ──────────────────────────────────────────────────────────────────────────────────────────────────────

def load_real(a):
    """S1's readers, unchanged: run dirs by the run log's Snapshot ID, pinned DBs (strict), the snapshot graphs, the build manifests."""
    data_root = a.data_root or S1.DATA_ROOT
    snap_db = a.snap_db or os.path.join(data_root, "snapshots.db")
    pres = S1.arm_presence(snap_db, data_root)
    absent = [n for n in ARMS_AN if not pres[n]["present"]]
    if absent:
        refuse("builds ABSENT: %s (%s)" % (", ".join(absent), "; ".join(pres[n]["why"] for n in absent)))
    W = S1.load_world(list(ARMS_AN), db=os.path.join(data_root, II.DB_NAME), emb_dir=data_root, strict=True)
    D_ex = S1.derive_inputs(W["db"])
    emb_pins = {e[4:]: s for e, s in W["pins"].items() if e.startswith("emb_")}
    trees = {}
    for n in ARMS_AN:
        T, _g = S1.load_tree_checked(n, pres[n], snap_db, D_ex, emb_pins)
        trees[n] = (T, pres[n]["sid"])
    diag = {n: os.path.join(pres[n]["rd"], "validation", "MAIN_routing_diagnostics.txt") for n in ARMS_AN}

    def recheck():
        S0.pin_check(W["db"], "ingest_db", True, label="ingest (after)")
        S0.pin_check(os.path.join(W["emb_dir"], "intent_emb_qwen3.db"), "emb", True, sub="qwen3", label="intent_emb_qwen3.db (after)")
    return dict(W=W, trees=trees, diag=diag, pins=W["pins"], recheck=recheck,
                src="data root %s; snapshots %s" % (data_root, snap_db))


_LOADER = [load_real]


# ── S1's record (identity input) ────────────────────────────────────────────────────────────────────────────────────────

def s1_record(s1_dir):
    """s1_outcome.txt / s1_items.csv: pinned sha256, the quoted lines present; the M-AN / C-AN rows of s1_items.csv (if any)."""
    c = cfg()
    paths = {"outcome": os.path.join(s1_dir, "s1_outcome.txt"), "items": os.path.join(s1_dir, "s1_items.csv")}
    sha = {}
    for k, p in paths.items():
        if not os.path.isfile(p):
            refuse("IDENTITY: S1's %s %s is absent" % (k, p))
        sha[k] = II.file_sha(p)
        if sha[k] != c["s1_sha"][k]:
            refuse("IDENTITY: S1's %s %s is sha256 %s, not the pinned %s" % (k, p, sha[k], c["s1_sha"][k]))
    txt = open(paths["outcome"], encoding="utf-8").read()
    for ln in c["s1_lines"]:
        if ln not in txt:
            refuse("IDENTITY: S1's outcome lacks the quoted line %r" % ln)
    counts, an = {}, {n: {} for n in ARMS_AN}
    with open(paths["items"], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            counts[r["arm"]] = counts.get(r["arm"], 0) + 1
            if r["arm"] in an:
                an[r["arm"]][r["item_id"]] = r["flat_leaf"]
    return dict(sha=sha, counts=counts, an=an, paths=paths)


# ── anchors ─────────────────────────────────────────────────────────────────────────────────────────────────────────────

def anchor_map(A):
    """Anchors = the root's children, each labelled pretty(coarse) of exactly one TRAIN coarse class; leaf -> anchor index."""
    T, C = A["T"], A["C"]
    root = T["root"]
    if T["multi_parent"]:
        refuse("%s: %d multi-parent nodes: a leaf's anchor is not unique" % (A["name"], T["multi_parent"]))
    anchors = sorted(T["kids"][root])
    classes = sorted(set(C.coarse[A["tr"]].tolist()))
    key = {}
    for cl in classes:
        k = EX.pretty(cl)
        if k in key:
            refuse("%s: coarse classes %r and %r format to one anchor label %r" % (A["name"], key[k], cl, k))
        key[k] = cl
    cls = []
    for a in anchors:
        lab = T["nodes"][a].get("label")
        if lab not in key:
            refuse("%s: anchor %s label %r is not a declared TRAIN coarse class" % (A["name"], a, lab))
        cls.append(key[lab])
    if len(set(cls)) != len(cls) or set(cls) != set(classes):
        refuse("%s: anchors %s do not cover the TRAIN coarse classes %s one to one" % (A["name"], sorted(cls), classes))
    pos = {a: j for j, a in enumerate(anchors)}
    leaf_anchor = {}
    for u in T["leaves"]:
        v = u
        while v is not None and T["tparent"].get(v) != root:
            v = T["tparent"].get(v)
        if v is None:
            refuse("%s: leaf %s has no depth-1 ancestor" % (A["name"], u))
        leaf_anchor[u] = pos[v]
    ka = np.bincount([leaf_anchor[u] for u in T["leaves"]], minlength=len(anchors))
    return dict(anchors=anchors, classes=cls, labels=[T["nodes"][a].get("label") for a in anchors], leaf_anchor=leaf_anchor, ka=ka)


# ── arms ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def refit(A, anc):
    """A-refit through FF.refit_cells (unchanged): adapters for its lane-r2 shapes; every fit set through S1.fit_idx (TRAIN only)."""
    C, X, T, tr = A["C"], A["X"], A["T"], A["tr"]
    gt = []
    for a, cl in enumerate(anc["classes"]):
        pos = np.flatnonzero(C.coarse[tr] == cl)
        S1.fit_idx(C, A["side"], tr[pos], (SS.TRAIN,), "%s A-refit fit set %s" % (A["name"], cl))
        gt.append(pos)
    o = {"leaves": list(T["leaves"]), "Xt": X[tr], "yt": np.zeros(len(tr), dtype=int), "nodes": {u: {"mu": T["mu"][u]} for u in T["leaves"]}}
    Aff = {"leaf_anchor": dict(anc["leaf_anchor"]), "anchors": list(anc["anchors"]), "gt": gt,
           "label": {a: lab for a, lab in zip(anc["anchors"], anc["labels"])}, "ka": anc["ka"]}
    Cm, _ca, info = FF.refit_cells(o, Aff)
    return Cm, info


def name_cells(A, Cm):
    """S1's R3 on any cell set: TRAIN-majority fine label per cell (flatLeaf = argmax cosine), None for a cell with no TRAIN item."""
    tr = A["tr"]
    lab = np.argmax(A["X"][tr] @ Cm.T, axis=1)
    return S1.majority(A["C"].fine[tr].tolist(), lab, len(Cm))


def file_eval(A, Cm, names):
    ev = S1.eval_rows(A)
    lab = np.argmax(A["X"][ev] @ Cm.T, axis=1)
    return np.array([names[j] is not None and names[j] == A["C"].fine[i] for j, i in zip(lab, ev)], dtype=np.int64)


def d1_point(A):
    """The point of S1.t_c1 (no bootstrap): NMI_fine(EVAL, flatLeaf) - mean_s NMI_fine(EVAL, k-means seeds 0-19)."""
    ev = S1.eval_rows(A)
    truth = S0.codes(A["C"].fine[ev])
    n_tree = S0.nmi(truth, S1.flat_leaf(A["T"], A["X"][ev]))
    return n_tree - float(np.mean([S0.nmi(truth, S0.assign(A["X"][ev], Cm)) for Cm in A["km"]]))


def stat(diff, comp, seed):
    diff = np.asarray(diff, dtype=np.float64)
    n = len(diff)
    lo, hi, se, _dr = S1.boot(comp, lambda w: S1.wmean(diff, w), seed, B=B_BOOT)
    var_iid = float(diff.var(ddof=1)) / n if n > 1 else 0.0
    deff = se ** 2 / var_iid if var_iid > 0 else float("nan")
    return dict(d=float(diff.mean()), lo=lo, hi=hi, se=se, deff=deff, kish=S0.kish(comp), n=n, G=int(len(np.unique(comp))),
                n_eff=n / deff if deff == deff and deff > 0 else float("nan"), mde=2.8 * se, disc=float(np.mean(diff != 0)), seed=seed)


def compute_corpus(A, anc, k):
    """FI1's numbers for one arm (EVAL read here, after the GATE freeze)."""
    C = A["C"]
    ev = S1.eval_rows(A)
    okA_s1, _fl = S1.fine_correct_flat(A, ev)
    okA = file_eval(A, A["T"]["leaf_mu"], name_cells(A, A["T"]["leaf_mu"]))
    if not np.array_equal(okA, okA_s1.astype(np.int64)):
        refuse("%s: this script's filer disagrees with S1.fine_correct_flat on A" % A["name"])
    Cr, info = refit(A, anc)
    names_r = name_cells(A, Cr)
    okR = file_eval(A, Cr, names_r)
    pk = []
    for s in SEEDS5:
        Cm = A["km"][s]
        pk.append(float(file_eval(A, Cm, name_cells(A, Cm)).mean()))
    spread = max(pk) - min(pk)
    st = stat(okR - okA, C.comp[ev], SEED_FI + k)
    a_names = [A["leaf_fine"][j] for j in range(A["L"])]
    changes = [(u, a_names[j], names_r[j]) for j, u in enumerate(A["T"]["leaves"]) if a_names[j] != names_r[j]]
    per = []
    for a, cl in enumerate(anc["classes"]):
        m = C.coarse[ev] == cl
        per.append(dict(label=anc["labels"][a], cls=cl, ka=int(anc["ka"][a]), n_tr=int((C.coarse[A["tr"]] == cl).sum()),
                        assigned="/".join(str(int(info["assigned"][j])) for j in info["by_anchor"][a]), n_ev=int(m.sum()),
                        pa=float(okA[m].mean()) if m.any() else float("nan"), pr=float(okR[m].mean()) if m.any() else float("nan")))
    return dict(name=A["name"], corpus=A["corpus"], n=len(ev), P_A=float(okA.mean()), P_R=float(okR.mean()), pk=pk, spread=spread,
                st=st, none=info["none"], changes=changes, unnamed_a=sum(1 for x in a_names if x is None),
                unnamed_r=sum(1 for x in names_r if x is None), per=per, L=A["L"], n_anchor=len(anc["anchors"]),
                n_split=int((anc["ka"] > 1).sum()), okA=okA, okR=okR, ev=ev)


# ── verdicts and rendering ──────────────────────────────────────────────────────────────────────────────────────────────

def v_fi1(r):
    return FF.v_ff1(r["st"]["d"], r["st"]["lo"], r["st"]["hi"], r["spread"])


def verdicts(Rs):
    """The single site of every verdict: per-corpus FI1 words, the READING, F-FI."""
    words = {r["corpus"]: v_fi1(r) for r in Rs}
    held = [c for c in ("massive", "clinc") if words.get(c) == "HELD"]
    reading = "BEYOND-MMLU" if held else "NOT-SHOWN"
    fires = bool(all(words[c] in ("UNDETERMINED", "REVERSED") for c in words) and len(words) == 2)
    return words, reading, fires, held


def _f(x, fmt="%.4f"):
    return "n/a" if x != x else fmt % x


def support_line(r):
    st, sp = r["st"], SUPPORT[r["corpus"]]
    nr = cfg()["n_reg"][r["corpus"]]
    return ("  support FI1 %s: denominator %d EVAL items / %d components (registered %d / %d); SE %.5f (registered %.5f); DEFF %s"
            " measured from the bootstrap, Kish %.6f from the components' sizes (transported %.3f); n_eff %s (registered %d); MDE80 %.4f"
            " (registered %.4f); discordance %.4f (planning %.2f); spread_K %.4f (planning bar %.3f); the registered bar is spread_K"
            " alone (MDE80 printed beside, not a conjunct)"
            % (UP[r["corpus"]], st["n"], st["G"], nr[0], nr[1], st["se"], sp["se"], _f(st["deff"], "%.3f"), st["kish"], DEFF_T,
               _f(st["n_eff"], "%.0f"), sp["neff"], st["mde"], sp["mde"], st["disc"], DISC_PLAN, r["spread"], sp["bar"]))


def verdict_lines(Rs):
    L = []
    words, reading, fires, held = verdicts(Rs)
    for r in Rs:
        st = r["st"]
        up = UP[r["corpus"]]
        vals = "D %+.4f, 95%% [%+.4f, %+.4f], spread_K %.4f (exact %.6f)" % (st["d"], st["lo"], st["hi"], r["spread"], r["spread"])
        w = words[r["corpus"]]
        if w == "HELD":
            L.append("FI1 %s: HELD (the class-pure leaf-mean refit files EVAL fine intents better than %s as built): %s; interval wholly"
                     " above 0 and D > spread_K" % (up, r["name"], vals))
        elif w == "REVERSED":
            L.append("FI1 %s: REVERSED (%s as built files EVAL fine intents better than its class-pure refit): %s; interval wholly"
                     " below 0 and D < -spread_K" % (up, r["name"], vals))
        else:
            L.append("FI1 %s: UNDETERMINED: %s; neither clause holds (interval wholly above 0: %s; D > spread_K: %s; interval wholly"
                     " below 0: %s; D < -spread_K: %s); never read as parity" % (
                         up, vals, "yes" if st["lo"] > 0 else "no", "yes" if st["d"] > r["spread"] else "no",
                         "yes" if st["hi"] < 0 else "no", "yes" if st["d"] < -r["spread"] else "no"))
        L.append(support_line(r))
    if reading == "BEYOND-MMLU":
        L.append("READING: BEYOND-MMLU (FI1 HELD on %s): FITSET-FAITHFUL's stage-0 gain extends to a known-answer intent corpus"
                 " (anchored tree, one draw, qwen3 512)" % " and ".join(UP[c] for c in held))
    else:
        L.append("READING: NOT-SHOWN (FI1 HELD on neither corpus: MASSIVE %s, CLINC %s)" % (words.get("massive"), words.get("clinc")))
    if fires:
        L.append("F-FI: FIRES (FI1 UNDETERMINED or REVERSED on both corpora: MASSIVE %s, CLINC %s): the stage-0 gain is not shown"
                 " beyond MMLU-Pro; FITSET-FAITHFUL's sentence keeps \"mostly MMLU-Pro\" as a scope limit." % (words["massive"], words["clinc"]))
    else:
        L.append("F-FI: DOES NOT FIRE (FI1 HELD on %s): a HELD extends FITSET-FAITHFUL's sentence to that known-answer corpus"
                 % " and ".join(UP[c] for c in held))
    L.append("VERDICT LINE (registered Support (f)): FI1 was DESCRIPTIVE-ONLY at the prediction (D +0.005 below both planning bars"
             " 0.015 / 0.010); the verdicts above are read with that qualifier.")
    return L


def in_band(x, band):
    if x is None or x != x:
        return None
    return "HELD" if band[0] <= x <= band[1] else "FAILED"


def prediction_lines(Rs):
    L = []
    _w, _r, _f2, held = verdicts(Rs)
    for r in Rs:
        b = in_band(r["st"]["d"], P1_BAND)
        L.append("PREDICTION P1 D %s %+.3f [%+.3f, %+.3f]: %s" % (UP[r["corpus"]], P1_PT, P1_BAND[0], P1_BAND[1],
                                                                 "observed none -> NOT SCORED (no estimate)" if b is None else
                                                                 "observed %+.4f -> %s" % (r["st"]["d"], b)))
    ev = bool(held)
    L.append("PREDICTION P1 FI1 HELD on at least one corpus (p %.2f): event %s, Brier %.4f" % (
        P_HELD_ANY, "OCCURRED" if ev else "DID NOT OCCUR", (P_HELD_ANY - (1.0 if ev else 0.0)) ** 2))
    for r in Rs:
        b = in_band(r["st"]["disc"], P2_BAND)
        L.append("PREDICTION P2 discordance %s %.2f [%.2f, %.2f]: %s" % (UP[r["corpus"]], P2_PT, P2_BAND[0], P2_BAND[1],
                                                                       "observed none -> NOT SCORED (no estimate)" if b is None else
                                                                       "observed %.4f -> %s" % (r["st"]["disc"], b)))
    return L


LABEL_INFO = (
    "LABEL INFORMATION PER ARM (LIKE WITH LIKE, the registered table, verbatim; memory anchored-tree-comparisons):",
    " | arm | anchors | fit sets below anchors | partition |",
    " |---|---|---|---|",
    " | A (M-AN / C-AN as built) | gold coarse (labels) | routed | vMF splits |",
    " | A-refit | same | declared-class TRAIN (labels) | same leaves, means re-estimated |",
    " | k-means at k = L (bar only) | none | none | flat |",
    " A-refit uses more TRAIN labels than A. (Builder's note: every arm is named by the TRAIN-majority fine intent, S1's R3; the anchored"
    " trees' filing is never a label-free number.)")
CONFOUNDS = (
    "CONFOUNDS (builder's wording adapted from FITSET-FAITHFUL's three; the registration names none of its own; carried by every sentence):",
    " (1) FIT-SET SIZE vs PURITY: the declared-class TRAIN set differs from the routed set below each anchor in size and in purity; FI1"
    " does not separate them.",
    " (2) MEANS ONLY: A-refit re-estimates the vMF leaves' MEANS on fixed topology; it is not a construction with declared fit sets"
    " (S1 unauthorised).",
    " (3) SCOPE / LABELS: anchored trees only (the anchors ARE the gold coarse classes); A-refit ADDS TRAIN-label use below the anchors;"
    " the k-means bar arm reads no label, so the bar compares a seed spread, not a label-matched arm.")
WILL_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): a construction with declared fit sets (S1 unauthorised); anything about"
                 " anchor-free trees; parity; MMLU-Pro.")


def render(Rs, ident, s1, ld, pins_lines_):
    L = ["%s FITSET-INTENT readout; zero calls; no build; A-refit fit sets are TRAIN rows only (S1.fit_idx audited: %d fits)" % (
        TAG, sum(1 for f in S1.FIT_LOG if "A-refit" in f[0]))]
    L += pins_lines_
    L += list(LABEL_INFO)
    L += list(CONFOUNDS)
    L.append("NOT APPLICABLE: wrong(established), tie conventions A / B, pilot / truncation guard, call cache (no judge verdict here).")
    L.append("== IDENTITY (all PASSED before any new number)")
    L += ident
    L.append("== DENOMINATORS: " + "; ".join(
        "%s (%s) EVAL %d items / %d components, TRAIN %d, %d anchors (%d split), %d leaves" % (
            UP[r["corpus"]], r["name"], r["st"]["n"], r["st"]["G"], r["n_tr"], r["n_anchor"], r["n_split"], r["L"]) for r in Rs))
    for r in Rs:
        st = r["st"]
        L.append("== %s (%s)" % (UP[r["corpus"]], r["name"]))
        L.append("  P(A) %.4f (as built, flatLeaf); P(A-refit) %.4f" % (r["P_A"], r["P_R"]))
        L.append("  D = P(A-refit) - P(A) %+.4f, 95%% [%+.4f, %+.4f] (component bootstrap B %d, seed %d; item-paired; n %d / G %d)" % (
            st["d"], st["lo"], st["hi"], B_BOOT, st["seed"], st["n"], st["G"]))
        L.append("  k-means at k = L = %d (S1's TRAIN fits): fine filing precision seeds 0-4 %s; spread_K %.6f" % (
            r["L"], ", ".join("%.4f" % x for x in r["pk"]), r["spread"]))
        L.append("  A-REFIT BOOKKEEPING: leaves receiving no declared-class item %d %s (each keeps its vmfMu); cells with no TRAIN item"
                 " A %d, A-refit %d (EVAL filed there is wrong); naming changes %d" % (len(r["none"]), r["none"], r["unnamed_a"],
                                                                                       r["unnamed_r"], len(r["changes"])))
        for u, was, now in r["changes"]:
            L.append("    naming change: %s %s -> %s" % (u, was, now))
        L.append("  PER ANCHOR (EVAL items whose gold coarse class is the anchor's; descriptive):")
        for p in r["per"]:
            L.append("    %-28s k_a %d; class TRAIN %d -> leaves %s; EVAL %d; P(A) %s, P(A-refit) %s, Delta %s" % (
                p["label"], p["ka"], p["n_tr"], p["assigned"], p["n_ev"], _f(p["pa"]), _f(p["pr"]),
                _f(p["pr"] - p["pa"], "%+.4f") if p["n_ev"] else "n/a"))
    L.append("== VERDICTS")
    L += verdict_lines(Rs)
    L.append("== PREDICTIONS (priors; a band is HELD iff the point lies in it, endpoints inclusive)")
    L += prediction_lines(Rs)
    L.append(WILL_NOT_SHOW)
    return "\n".join(L) + "\n"


def pins_lines(ld, s1):
    L = ["%s script %s blob:%s (LF); instrument %s" % (TAG, os.path.basename(__file__), blob_lf(os.path.abspath(__file__)),
                                                      ", ".join("%s blob:%s" % (n, p) for n, p in PINS))]
    L.append("%s data pins (sha256-bytes): %s; %s" % (TAG, json.dumps(ld["pins"], sort_keys=True), ld.get("src", "")))
    L.append("%s S1 record: s1_outcome.txt sha256 %s, s1_items.csv sha256 %s; s1_items arms %s" % (
        TAG, s1["sha"]["outcome"], s1["sha"]["items"], json.dumps(s1["counts"], sort_keys=True)))
    return L


# ── main ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def check_tree(name, T, sid):
    c = cfg()
    if sid != c["sid"][name]:
        refuse("IDENTITY: %s Snapshot ID %s != S1's %s" % (name, sid, c["sid"][name]))
    if len(T["leaves"]) != c["leaves"][name]:
        refuse("IDENTITY: %s has %d leaves, S1 printed %d" % (name, len(T["leaves"]), c["leaves"][name]))


def identity(A, s1):
    c = cfg()
    n = A["name"]
    if not A["accept"]["accepted"]:
        refuse("IDENTITY: %s's descent port is NOT ACCEPTED on GATE (%s); S1's printed D_fd presumes acceptance" % (n, A["accept"]))
    t8 = S1.t_c8(A)
    got = dict(dfd="%+.5f" % t8["D"], d1="%+.5f" % d1_point(A), delta_c="%.5f" % A["gate"]["delta_c"])
    bad = [k for k in ("dfd", "d1", "delta_c") if got[k] != c["ident"][n][k]]
    if bad:
        refuse("IDENTITY: %s %s reproduced as %s, S1 printed %s" % (n, bad, [got[k] for k in bad], [c["ident"][n][k] for k in bad]))
    rows = s1["an"].get(n) or {}
    if rows:
        ev = S1.eval_rows(A)
        fl = S1.flat_leaf(A["T"], A["X"][ev])
        mine = {A["C"].ids[i]: A["T"]["leaves"][j] for i, j in zip(ev, fl)}
        diff = sorted(k for k in rows if mine.get(k) != rows[k])
        if diff or set(rows) != set(mine):
            refuse("IDENTITY: %s flat leaves differ from s1_items.csv on %d items (first %s); rows %d vs EVAL %d" % (
                n, len(diff), diff[:3], len(rows), len(mine)))
        how = "s1_items.csv rows compared item by item: %d of %d equal" % (len(rows), len(mine))
    else:
        how = ("s1_items.csv holds no %s rows (DEVIATION, disclosed: the registered s1_items identity is read through S1's printed"
               " D_fd / D1 / delta_c)" % n)
    return ("  %s: snapshot %s, %d leaves; descent ACCEPTED %.5f (%d of %d); T-C8 D_fd %s (P flatLeaf %.5f), T-C1 D1 %s, delta_c %s"
            " = S1's printed values; %s" % (n, A["sid"], A["L"], A["accept"]["agree"], A["accept"]["k"], A["accept"]["n"], got["dfd"],
                                             t8["P_flat"], got["d1"], got["delta_c"], how)), t8


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--s1-dir", default=None)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--snap-db", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        print("POOL n/a (selftest: synthetic fixtures only; nothing real is read)")
        print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
        print("[SCRIPT] %s blob:%s (LF)" % (os.path.basename(__file__), blob_lf(os.path.abspath(__file__))))
        try:
            selftest()
        except AssertionError:
            return 1
        return 0
    if a.mutants:
        return run_mutants()
    c = cfg()
    outp = a.out or c["out"]
    first = ("POOL n/a: FITSET-INTENT reads S1's own intent DBs (S0 hash sides; no engine pool of record; S0 pins strict); zero calls,"
             " 0 builds")
    out(first)
    if a.run and os.path.lexists(outp):
        refuse("%s exists; the outcome is write-once" % outp)
    heavy = _HEAVY[0]()
    if heavy:
        refuse("a foreign heavy process runs (%s): the readout never reads snapshots.db / the embedding DBs beside a java" % heavy)
    s1 = s1_record(a.s1_dir or c["s1_dir"])
    ld = _LOADER[0](a)
    W = ld["W"]
    cen, _bad = S1.census(W)
    for corpus in ("massive", "clinc"):
        if tuple(cen[corpus]) != tuple(c["n_reg"][corpus]):
            refuse("DENOMINATOR: %s EVAL %d / %d != the registered %d / %d" % (UP[corpus], cen[corpus][0], cen[corpus][1],
                                                                             c["n_reg"][corpus][0], c["n_reg"][corpus][1]))
    del S1.FIT_LOG[:]
    S1.STATE["gate_frozen"] = False
    arms, ancs = {}, {}
    for n in ARMS_AN:
        T, sid = ld["trees"][n]
        check_tree(n, T, sid)
        A = S1.make_arm(W, n, T, sid)
        arms[n] = S1.phase_gate(A, False, ld["diag"][n], need_km=bool(a.run))
        ancs[n] = anchor_map(arms[n])
    pl = pins_lines(ld, s1)
    if a.dry_run:
        for ln in pl:
            out(ln)
        for n in ARMS_AN:
            A, anc = arms[n], ancs[n]
            Cr, info = refit(A, anc)          # TRAIN only: bookkeeping, no EVAL row is read (eval_rows refuses before the freeze)
            out("%s %s (%s): snapshot %s = S1's; %d leaves = S1's; slice %d; anchors %d (%d split; labels = pretty(coarse), one to one);"
                " TRAIN %d; descent agreement %.5f (%d of %d) %s" % (
                    TAG, n, UP[A["corpus"]], A["sid"], A["L"], A["T"]["d"], len(anc["anchors"]), int((anc["ka"] > 1).sum()), len(A["tr"]),
                    A["accept"]["agree"], A["accept"]["k"], A["accept"]["n"], "ACCEPTED" if A["accept"]["accepted"] else "NOT ACCEPTED"))
            out("%s %s A-refit (TRAIN side): leaves receiving no declared-class item %d %s; per anchor class TRAIN -> leaves %s" % (
                TAG, n, len(info["none"]), info["none"], "; ".join("%s %d -> %s" % (
                    anc["labels"][x], len(np.flatnonzero(A["C"].coarse[A["tr"]] == anc["classes"][x])),
                    "/".join(str(int(info["assigned"][j])) for j in info["by_anchor"][x])) for x in range(len(anc["anchors"])))))
            out("%s %s s1_items.csv rows: %d (%s)" % (TAG, n, len(s1["an"].get(n) or {}), "compared item by item at --run" if s1["an"].get(n)
                                                     else "none: the identity is read through S1's printed D_fd / D1 / delta_c at --run"))
        out("%s DENOMINATORS: MASSIVE %d / %d, CLINC %d / %d EVAL items / components (= registered); TRAIN M-AN %d, C-AN %d" % (
            TAG, cen["massive"][0], cen["massive"][1], cen["clinc"][0], cen["clinc"][1], len(arms["M-AN"]["tr"]), len(arms["C-AN"]["tr"])))
        out("%s fit audit: %d fits, sides %s" % (TAG, len(S1.FIT_LOG), sorted({f[3] for f in S1.FIT_LOG})))
        out("%s dry-run: NO EVAL row read, NO k-means fitted, NO statistic computed; 0 files written" % TAG)
        return 0
    S1.STATE["gate_frozen"] = True
    ident, Rs = [], []
    for k, n in enumerate(ARMS_AN):
        line, t8 = identity(arms[n], s1)
        ident.append(line)
        r = compute_corpus(arms[n], ancs[n], k)
        if abs(r["P_A"] - t8["P_flat"]) > 1e-12:
            refuse("IDENTITY: %s P(A) %.6f != S1.t_c8's P flatLeaf %.6f" % (n, r["P_A"], t8["P_flat"]))
        if (r["st"]["n"], r["st"]["G"]) != tuple(c["n_reg"][r["corpus"]]):
            refuse("DENOMINATOR: %s FI1 reads %d / %d EVAL items / components, registered %d / %d" % (
                n, r["st"]["n"], r["st"]["G"], c["n_reg"][r["corpus"]][0], c["n_reg"][r["corpus"]][1]))
        r["n_tr"] = len(arms[n]["tr"])
        Rs.append(r)
    ld["recheck"]()
    body = render(Rs, ident, s1, ld, pl)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, "x", encoding="utf-8", newline="\n") as f:
        f.write(first + "\n" + body)
    out(body.rstrip("\n"))
    out("%s wrote %s (write-once)" % (TAG, outp))
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

DIM = 12


def _e(i):
    v = np.zeros(DIM)
    v[i] = 1.0
    return v


def _u(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


V = dict(a1=_e(0), a2=_e(1), z=_e(2), b1=_e(3), b2=_e(4), g1=_e(6), d1=_e(7),
         a1e9=_u(_e(9) + 0.1 * _e(0)), b1mix=_u(_e(3) + 0.9 * _e(4)), g1mix=_u(_e(6) + 1.1 * _e(7)),
         b1tr=_u(_e(4) + 0.5 * _e(3)), g1tr=_u(_e(6) + 0.8 * _e(7)))
G_REFIT = _u(10 * _e(6) + 10 * V["g1tr"])
# EVAL group -> (coarse, fine, vector key, correct under A, correct under A-refit)
GROUPS = (("a1", "alpha", "alpha_a1", "a1", 1, 1), ("a2", "alpha", "alpha_a2", "a2", 0, 1), ("a1e9", "alpha", "alpha_a1", "a1e9", 0, 0),
          ("z", "zeta", "zeta_z", "z", 1, 1), ("b1", "beta", "beta_b1", "b1", 1, 1), ("b2", "beta", "beta_b2", "b2", 1, 1),
          ("b1mix", "beta", "beta_b1", "b1mix", 1, 0), ("b1e4", "beta", "beta_b1", "b2", 0, 0), ("g1", "gamma", "gamma_g1", "g1", 1, 1),
          ("g1mix", "gamma", "gamma_g1", "g1mix", 0, 1), ("d1", "delta", "delta_d1", "d1", 1, 1))
BASE_N = dict(a1=20, a1e9=5, z=10, b1=10, b2=10, b1e4=4, g1=10, d1=10)
# TRAIN: (coarse, fine, vector key, count)
TRAIN = (("alpha", "alpha_a1", "a1", 10), ("alpha", "alpha_a2", "a2", 10), ("zeta", "zeta_z", "z", 12), ("beta", "beta_b1", "b1", 10),
         ("beta", "beta_b2", "b2", 10), ("beta", "beta_b1", "b1tr", 6), ("gamma", "gamma_g1", "g1", 10), ("gamma", "gamma_g1", "g1tr", 10),
         ("delta", "delta_d1", "d1", 10))
GATE = (("alpha", "alpha_a1", "a1"), ("alpha", "alpha_a2", "a2"), ("zeta", "zeta_z", "z"), ("beta", "beta_b1", "b1"), ("beta", "beta_b2", "b2"),
        ("gamma", "gamma_g1", "g1"), ("delta", "delta_d1", "d1"))
# fixture variants: per corpus (n_a2, n_b1mix, n_g1mix, components grouped in threes for g1mix)
FIXTURES = {"UH": {"massive": (4, 5, 30, True), "clinc": (15, 8, 12, False)},
            "RZ": {"massive": (2, 40, 2, False), "clinc": (0, 0, 0, False)}}


def _km_sets():
    base = [_e(0), _e(1), _e(2), _e(3), _e(4), _e(6), _e(7), _e(9)]
    s1 = list(base)
    s1[5] = G_REFIT
    late = list(base)
    late[4] = _u(_e(3) + _e(4))
    return {0: np.vstack(base), 1: np.vstack(s1), 2: np.vstack(base), 3: np.vstack(base), 4: np.vstack(base), "late": np.vstack(late)}


_SK_CALLS = [0]


def _fake_skmeans(X, k, seed, max_iter=300):
    _SK_CALLS[0] += 1
    S = _km_sets()
    C = S[seed] if seed in S else S["late"]
    assert k == len(C), (k, len(C))
    return C.copy()


def _graph(variant=None):
    """root -> Alpha (LA1 e0, LA2 unit(e1 + 2 e2), LA3 e9), Beta (LB1 e3, LB2 e4), Gamma leaf e6, Zeta leaf e5, Delta leaf e7."""
    def node(i, label, kids, par, mu, kappa, q=True):
        qids = ["q_%s_%d" % (i, j) for j in range(3)] if q else []
        return {"id": i, "label": label, "childIds": kids, "parentIds": par, "sliceDim": DIM, "vmfMu": [float(x) for x in mu],
                "vmfKappa": kappa, "queryIds": qids, "queryWeights": {x: 1.0 for x in qids}}
    r = "n00000001"
    labels = {"n00000002": "Alpha", "n00000003": "Beta", "n00000004": "Gamma", "n00000005": "Zeta", "n00000006": "Delta"}
    if variant == "offlabel":
        labels["n00000006"] = "Epsilon"
    if variant == "dupe":
        labels["n00000006"] = "Alpha"
    nodes = [node(r, "INTENT", ["n00000002", "n00000003", "n00000004", "n00000005", "n00000006"], [], _u(np.ones(DIM)), 5.0),
             node("n00000002", labels["n00000002"], ["n00000007", "n00000008", "n00000009"], [r], _u(_e(0) + _e(1) + _e(2)), 15.0),
             node("n00000003", labels["n00000003"], ["n00000010", "n00000011"], [r], _u(_e(3) + _e(4)), 15.0),
             node("n00000004", labels["n00000004"], [], [r], _e(6), 30.0),
             node("n00000005", labels["n00000005"], [], [r], _e(5), 30.0, q=False),
             node("n00000006", labels["n00000006"], [], [r], _e(7), 30.0),
             node("n00000007", "a", [], ["n00000002"], _e(0), 30.0),
             node("n00000008", "b", [], ["n00000002"], _u(_e(1) + 2 * _e(2)), 30.0),
             node("n00000009", "c", [], ["n00000002"], _e(9), 30.0, q=False),
             node("n00000010", "d", [], ["n00000003"], _e(3), 30.0),
             node("n00000011", "e", [], ["n00000003"], _e(4), 30.0)]
    if variant == "multiparent":
        nodes[-1]["parentIds"] = ["n00000003", "n00000002"]
        nodes[1]["childIds"].append("n00000011")
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return {"rootId": r, "nodes": nodes}, settings


def _rows(corpus, spec, drop_class=None):
    """Corpus rows + vectors for one fixture corpus; returns (rows, vecs, eval group of each EVAL item id)."""
    n_a2, n_b1mix, n_g1mix, grouped = spec
    cnt = dict(BASE_N, a2=n_a2, b1mix=n_b1mix, g1mix=n_g1mix)
    rows, vecs, egrp = [], {}, {}
    k = [0]

    def add(side, coarse, fine, vkey, stem, tag):
        k[0] += 1
        iid = "%s:%s:%05d" % (corpus, side.lower(), k[0])
        text = "%s %s %s %d" % (corpus, side, tag, k[0])
        rows.append({"item_id": iid, "corpus": corpus, "text": text, "coarse": coarse, "fine": fine, "is_oos": 0, "annot": None,
                     "stem_key": stem or ("stem " + text), "hash_side": side, "side": side, "drop_reason": None})
        vecs[text] = V[vkey].astype(np.float32)
        return iid
    for coarse, fine, vkey, n in TRAIN:
        if coarse == drop_class:
            continue
        for _j in range(n):
            add(SS.TRAIN, coarse, fine, vkey, None, "train " + vkey)
    for coarse, fine, vkey in GATE:
        for _j in range(3):
            add(SS.GATE, coarse, fine, vkey, None, "gate " + vkey)
    for g, coarse, fine, vkey, _a, _r in GROUPS:
        for j in range(cnt[g]):
            stem = ("%s grp %s %d" % (corpus, g, j // 3)) if (grouped and g == "g1mix") else None
            egrp[add(SS.EVAL, coarse, fine, vkey, stem, "eval " + g)] = g
    return rows, vecs, egrp, cnt


def _world(td, variant="UH", graph_variant=None, drop_class=None):
    W = {"CS": {}, "vecs": {"qwen3": {}}, "variants": [], "db": None, "emb_dir": None, "pins": {"ingest": "fixture-ingest", "emb_qwen3": "fixture-qwen3"}}
    trees, diag, egrp, cnts = {}, {}, {}, {}
    for n in ARMS_AN:
        corpus = CORPUS_OF[n]
        rows, vecs, eg, cnt = _rows(corpus, FIXTURES[variant][corpus], drop_class)
        W["CS"][corpus] = S0.Corpus(corpus, rows)
        W["vecs"]["qwen3"].update(vecs)
        egrp.update(eg)
        cnts[corpus] = cnt
        g, s = _graph(graph_variant)
        T = S1.tree_of(g, s)
        trees[n] = (T, "sid_" + n)
        C = W["CS"][corpus]
        X = S1.sliced(S1.raw_matrix(C, W["vecs"]["qwen3"], DIM)[0], DIM)
        ga = np.nonzero(C.kept & (C.side == SS.GATE))[0]
        seen, texts, idx = set(), [], []
        for i in ga:
            if C.text[i] not in seen:
                seen.add(C.text[i])
                texts.append(C.text[i])
                idx.append(i)
        diag[n] = os.path.join(td, n, "validation", "MAIN_routing_diagnostics.txt")
        S1._write_diag(diag[n], texts, S1.Descent(T).top1(X[np.array(idx, dtype=int)]))
    return W, trees, diag, egrp, cnts


def _boot_oracle(diff, comp, seed, B=2000):
    """Independent component bootstrap: components drawn with replacement, weighted mean, percentile 2.5 / 97.5, SD."""
    _, cc = np.unique(np.asarray(comp), return_inverse=True)
    G_ = int(cc.max()) + 1
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        w = np.bincount(rng.integers(G_, size=G_), minlength=G_)[cc].astype(np.float64)
        d.append(float((diff * w).sum() / w.sum()))
    d = np.array(d)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), float(np.std(d, ddof=1))


def _oracle_identity(W, trees, diag):
    """Expected S1 constants on the fixture through S1's own functions (a fresh arm); the readout must reproduce them."""
    out = {}
    saved = S1.STATE["gate_frozen"]
    try:
        for n in ARMS_AN:
            S1.STATE["gate_frozen"] = False
            A = S1.phase_gate(S1.make_arm(W, n, *trees[n]), False, diag[n], need_km=True)
            S1.STATE["gate_frozen"] = True
            ev = S1.eval_rows(A)
            truth = S0.codes(A["C"].fine[ev])
            d1 = S0.nmi(truth, S1.flat_leaf(A["T"], A["X"][ev])) - float(np.mean([S0.nmi(truth, S0.assign(A["X"][ev], Cm)) for Cm in A["km"]]))
            out[n] = dict(dfd="%+.5f" % S1.t_c8(A)["D"], d1="%+.5f" % d1, delta_c="%.5f" % A["gate"]["delta_c"])
    finally:
        S1.STATE["gate_frozen"] = saved
    return out


def _s1_files(td, lines, items_rows=()):
    d = os.path.join(td, "s1")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "s1_outcome.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("S1 FIXTURE OUTCOME\n" + "\n".join(lines) + "\n")
    with open(os.path.join(d, "s1_items.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("arm,item_id,flat_leaf,descent_leaf\n")
        for r in items_rows:
            f.write("%s,%s,%s,%s\n" % r)
    return d, {"outcome": II.file_sha(os.path.join(d, "s1_outcome.txt")), "items": II.file_sha(os.path.join(d, "s1_items.csv"))}


def _run(td, variant="UH", argv=None, expect_refusal=None, patch=None, graph_variant=None, drop_class=None, items=None,
         heavy=None, lines_patch=None):
    """Builds the fixture world and executes main(), the real entry point (loader, java probe and S0.skmeans stubbed)."""
    saved_sk = S0.skmeans
    S0.skmeans = _fake_skmeans
    try:
        W, trees, diag, egrp, cnts = _world(td, variant, graph_variant, drop_class)
        ident = _oracle_identity(W, trees, diag) if graph_variant is None and drop_class is None else \
            {n: dict(dfd="+0.00000", d1="+0.00000", delta_c="0.00000") for n in ARMS_AN}
        n_reg = {}
        for corpus in ("massive", "clinc"):
            C = W["CS"][corpus]
            m = C.kept & ~C.oos & (C.side == SS.EVAL)
            n_reg[corpus] = (int(m.sum()), int(len(np.unique(C.comp[m]))))
        lines = ["%s snapshot sid_%s leaves 8 (no-TRAIN leaves 0)" % (n, n) for n in ARMS_AN]
        lines += ["DESCRIPTIVE %s: T-C8 D_fd %s" % (n, ident[n]["dfd"]) for n in ARMS_AN]
        if lines_patch:
            lines = lines_patch(lines)
        rows = items(W, trees) if items else ()
        s1d, sha = _s1_files(td, lines, rows)
        fc = dict(REG, out=os.path.join(td, "out", "fitset_intent_outcome.txt"), s1_dir=s1d, sid={n: "sid_" + n for n in ARMS_AN},
                  leaves={n: 8 for n in ARMS_AN}, ident=ident, s1_sha=sha, s1_lines=tuple(lines), n_reg=n_reg)
        if patch:
            patch(fc)
        ld = dict(W=W, trees=trees, diag=diag, pins=W["pins"], recheck=lambda: None, src="fixture")
        saved = (_CFG[0], _LOADER[0], _HEAVY[0])
        _CFG[0], _LOADER[0], _HEAVY[0] = fc, (lambda a: ld), (heavy or (lambda: []))
        buf = []
        sk0 = _SK_CALLS[0]
        try:
            res = main(argv or ["--run"], out=buf.append)
        except SystemExit as e:
            res = str(e)
            if expect_refusal is None:
                raise
        finally:
            _CFG[0], _LOADER[0], _HEAVY[0] = saved
    finally:
        S0.skmeans = saved_sk
    if expect_refusal is not None:
        assert isinstance(res, str) and expect_refusal in res, (expect_refusal, res)
    return res, "\n".join(buf), fc, dict(W=W, egrp=egrp, cnts=cnts, trees=trees, sk_main=_SK_CALLS[0] - sk0)


def _need(text, *needles):
    for nd in needles:
        assert nd in text, "missing: %r" % nd


def _hand(fx, corpus):
    """Hand values of one fixture corpus: (n, okA, okR per EVAL item in corpus row order, P_K seeds 0-4)."""
    W, egrp, cnt = fx["W"], fx["egrp"], fx["cnts"][corpus]
    C = W["CS"][corpus]
    ev = [i for i in np.nonzero(C.kept & ~C.oos & (C.side == SS.EVAL))[0]]
    g = [egrp[C.ids[i]] for i in ev]
    ga = {x[0]: (x[4], x[5]) for x in GROUPS}
    okA = np.array([ga[x][0] for x in g], dtype=np.float64)
    okR = np.array([ga[x][1] for x in g], dtype=np.float64)
    n = len(ev)
    p0 = (70 + cnt["a2"] + cnt["b1mix"]) / n
    pk = [p0, p0 + cnt["g1mix"] / n, p0, p0, p0]
    return n, okA, okR, pk, C.comp[np.array(ev)]


def _check_corpus(filed, fx, corpus, k):
    n, okA, okR, pk, comp = _hand(fx, corpus)
    up = UP[corpus]
    d = float((okR - okA).mean())
    lo, hi, se = _boot_oracle(okR - okA, comp, SEED_FI + k)
    spread = max(pk) - min(pk)
    G_ = len(np.unique(comp))
    diff = okR - okA
    var_iid = float(diff.var(ddof=1)) / n
    deff = "%.3f" % (se ** 2 / var_iid) if var_iid > 0 else "n/a"
    neff = "%.0f" % (n / (se ** 2 / var_iid)) if var_iid > 0 and se > 0 else "n/a"
    _need(filed, "SE %.5f (registered %.5f); DEFF %s measured from the bootstrap" % (se, SUPPORT[corpus]["se"], deff),
          "; n_eff %s (registered %d)" % (neff, SUPPORT[corpus]["neff"]))
    _need(filed, "  P(A) %.4f (as built, flatLeaf); P(A-refit) %.4f" % (okA.mean(), okR.mean()),
          "  D = P(A-refit) - P(A) %+.4f, 95%% [%+.4f, %+.4f] (component bootstrap B 2000, seed %d; item-paired; n %d / G %d)" % (
              d, lo, hi, SEED_FI + k, n, G_),
          "fine filing precision seeds 0-4 %s; spread_K %.6f" % (", ".join("%.4f" % x for x in pk), spread),
          "  support FI1 %s: denominator %d EVAL items / %d components (registered %d / %d); SE %.5f" % (up, n, G_, n, G_, se))
    return dict(n=n, d=d, lo=lo, hi=hi, spread=spread, se=se, okA=okA, okR=okR, G=G_, disc=float(np.mean(okR != okA)))


def st_e2e_UH(td):
    res, text, fc, fx = _run(td, "UH")
    assert res == 0, res
    filed = open(fc["out"], encoding="utf-8").read()
    assert filed.splitlines()[0].startswith("POOL n/a: FITSET-INTENT reads S1's own intent DBs"), filed.splitlines()[0]
    m = _check_corpus(filed, fx, "massive", 0)
    c = _check_corpus(filed, fx, "clinc", 1)
    assert m["n"] == 118 and abs(m["d"] - 29 / 118) < 1e-12 and abs(m["spread"] - 30 / 118) < 1e-12 and m["G"] == 98 and m["lo"] > 0
    assert c["n"] == 114 and abs(c["d"] - 19 / 114) < 1e-12 and abs(c["spread"] - 12 / 114) < 1e-12 and c["G"] == 114 and c["lo"] > 0
    _need(filed,
          "FI1 MASSIVE: UNDETERMINED: D %+.4f, 95%% [%+.4f, %+.4f], spread_K %.4f (exact %.6f); neither clause holds (interval wholly"
          " above 0: yes; D > spread_K: no; interval wholly below 0: no; D < -spread_K: no); never read as parity" % (
              m["d"], m["lo"], m["hi"], m["spread"], m["spread"]),
          "FI1 CLINC: HELD (the class-pure leaf-mean refit files EVAL fine intents better than C-AN as built): D %+.4f, 95%% [%+.4f, %+.4f],"
          " spread_K %.4f (exact %.6f); interval wholly above 0 and D > spread_K" % (c["d"], c["lo"], c["hi"], c["spread"], c["spread"]),
          "Kish 1.508475 from the components' sizes (transported 1.052)",
          "(registered 0.00357); DEFF", "n_eff ", "(registered 4702); MDE80 %.4f (registered 0.0100); discordance %.4f (planning 0.06);"
          " spread_K %.4f (planning bar 0.015)" % (2.8 * m["se"], m["disc"], m["spread"]),
          "(registered 0.00308)", "(registered 6342); MDE80 %.4f (registered 0.0086)" % (2.8 * c["se"]),
          "READING: BEYOND-MMLU (FI1 HELD on CLINC): FITSET-FAITHFUL's stage-0 gain extends",
          "F-FI: DOES NOT FIRE (FI1 HELD on CLINC): a HELD extends FITSET-FAITHFUL's sentence",
          "VERDICT LINE (registered Support (f)): FI1 was DESCRIPTIVE-ONLY at the prediction",
          "PREDICTION P1 D MASSIVE +0.005 [-0.005, +0.020]: observed %+.4f -> FAILED" % m["d"],
          "PREDICTION P1 D CLINC +0.005 [-0.005, +0.020]: observed %+.4f -> FAILED" % c["d"],
          "PREDICTION P1 FI1 HELD on at least one corpus (p 0.25): event OCCURRED, Brier 0.5625",
          "PREDICTION P2 discordance MASSIVE 0.03 [0.01, 0.08]: observed %.4f -> FAILED" % m["disc"],
          "PREDICTION P2 discordance CLINC 0.03 [0.01, 0.08]: observed %.4f -> FAILED" % c["disc"],
          "== DENOMINATORS: MASSIVE (M-AN) EVAL 118 items / 98 components, TRAIN 88, 5 anchors (2 split), 8 leaves; CLINC (C-AN) EVAL 114"
          " items / 114 components, TRAIN 88, 5 anchors (2 split), 8 leaves",
          "A-REFIT BOOKKEEPING: leaves receiving no declared-class item 1 ['n00000009'] (each keeps its vmfMu); cells with no TRAIN item"
          " A 2, A-refit 1 (EVAL filed there is wrong); naming changes 2",
          "    naming change: n00000005 None -> zeta_z", "    naming change: n00000008 zeta_z -> alpha_a2",
          "    Alpha                        k_a 3; class TRAIN 20 -> leaves 10/10/0; EVAL 29; P(A) %.4f, P(A-refit) %.4f, Delta %+.4f" % (
              20 / 29, 24 / 29, 4 / 29),
          "    Beta                         k_a 2; class TRAIN 26 -> leaves 10/16; EVAL 29; P(A) %.4f, P(A-refit) %.4f, Delta %+.4f" % (
              25 / 29, 20 / 29, -5 / 29),
          "    Gamma                        k_a 1; class TRAIN 20 -> leaves 20; EVAL 40; P(A) 0.2500, P(A-refit) 1.0000, Delta +0.7500",
          "    Zeta                         k_a 1; class TRAIN 12 -> leaves 12; EVAL 10; P(A) 1.0000, P(A-refit) 1.0000, Delta +0.0000",
          "IDENTITY (all PASSED before any new number)", "s1_items.csv holds no M-AN rows (DEVIATION, disclosed",
          "fit sets are TRAIN rows only (S1.fit_idx audited: 10 fits)",
          LABEL_INFO[3], LABEL_INFO[4], LABEL_INFO[5], LABEL_INFO[6], CONFOUNDS[1], CONFOUNDS[2], CONFOUNDS[3], WILL_NOT_SHOW,
          "NOT APPLICABLE: wrong(established)")
    for f in S1.FIT_LOG:
        assert f[3] in ((SS.TRAIN,), (SS.GATE,)), f
    _run(td, "UH", expect_refusal="exists; the outcome is write-once")
    assert open(fc["out"], encoding="utf-8").read() == filed
    return True


def st_e2e_RZ(td):
    def items(W, trees):
        C = W["CS"]["massive"]
        T = trees["M-AN"][0]
        X = S1.sliced(S1.raw_matrix(C, W["vecs"]["qwen3"], DIM)[0], DIM)
        ev = np.nonzero(C.kept & ~C.oos & (C.side == SS.EVAL))[0]
        fl = S1.flat_leaf(T, X[ev])
        return [("M-AN", C.ids[i], T["leaves"][j], "x") for i, j in zip(ev, fl)] + [("M-AF", "massive:x:1", "n1", "n1")]
    res, text, fc, fx = _run(td, "RZ", items=items)
    assert res == 0, res
    filed = open(fc["out"], encoding="utf-8").read()
    m = _check_corpus(filed, fx, "massive", 0)
    c = _check_corpus(filed, fx, "clinc", 1)
    assert m["n"] == 123 and abs(m["d"] + 36 / 123) < 1e-12 and m["hi"] < 0 and c["n"] == 79 and c["d"] == 0 and c["spread"] == 0
    _need(filed,
          "FI1 MASSIVE: REVERSED (M-AN as built files EVAL fine intents better than its class-pure refit): D %+.4f, 95%% [%+.4f, %+.4f],"
          " spread_K %.4f (exact %.6f); interval wholly below 0 and D < -spread_K" % (m["d"], m["lo"], m["hi"], m["spread"], m["spread"]),
          "FI1 CLINC: UNDETERMINED: D +0.0000, 95% [+0.0000, +0.0000], spread_K 0.0000 (exact 0.000000); neither clause holds (interval"
          " wholly above 0: no; D > spread_K: no; interval wholly below 0: no; D < -spread_K: no)",
          "SE 0.00000 (registered 0.00308); DEFF n/a measured from the bootstrap, Kish 1.000000",
          "n_eff n/a (registered 6342); MDE80 0.0000 (registered 0.0086); discordance 0.0000 (planning 0.06)",
          "READING: NOT-SHOWN (FI1 HELD on neither corpus: MASSIVE REVERSED, CLINC UNDETERMINED)",
          "F-FI: FIRES (FI1 UNDETERMINED or REVERSED on both corpora: MASSIVE REVERSED, CLINC UNDETERMINED): the stage-0 gain is not shown"
          " beyond MMLU-Pro; FITSET-FAITHFUL's sentence keeps \"mostly MMLU-Pro\" as a scope limit.",
          "PREDICTION P1 FI1 HELD on at least one corpus (p 0.25): event DID NOT OCCUR, Brier 0.0625",
          "PREDICTION P1 D CLINC +0.005 [-0.005, +0.020]: observed +0.0000 -> HELD",
          "PREDICTION P2 discordance CLINC 0.03 [0.01, 0.08]: observed 0.0000 -> FAILED",
          "s1_items.csv rows compared item by item: 123 of 123 equal", "s1_items.csv holds no C-AN rows",
          "    Delta                        k_a 1; class TRAIN 10 -> leaves 10; EVAL 10; P(A) 1.0000, P(A-refit) 1.0000, Delta +0.0000")
    return True


def st_dry_run(td):
    res, text, fc, fx = _run(td, "UH", argv=["--dry-run"])
    assert res == 0, res
    assert text.splitlines()[0].startswith("POOL n/a: FITSET-INTENT"), text.splitlines()[0]
    _need(text, "[FI] script fitset_intent.py blob:", "intent_transfer_s1.py blob:4e9d9d05", "fitset_faithful.py blob:ed343065",
          "[FI] M-AN (MASSIVE): snapshot sid_M-AN = S1's; 8 leaves = S1's; slice 12; anchors 5 (2 split; labels = pretty(coarse), one to"
          " one); TRAIN 88; descent agreement 1.00000 (21 of 21) ACCEPTED",
          "[FI] M-AN A-refit (TRAIN side): leaves receiving no declared-class item 1 ['n00000009']; per anchor class TRAIN -> leaves"
          " Alpha 20 -> 10/10/0; Beta 26 -> 10/16; Gamma 20 -> 20; Zeta 12 -> 12; Delta 10 -> 10",
          "[FI] DENOMINATORS: MASSIVE 118 / 98, CLINC 114 / 114 EVAL items / components (= registered); TRAIN M-AN 88, C-AN 88",
          "[FI] dry-run: NO EVAL row read, NO k-means fitted, NO statistic computed; 0 files written",
          "s1_items.csv rows: 0 (none: the identity is read through")
    for bad in ("P(A", "FI1", "F-FI", "PREDICTION", "D = ", "spread_K"):
        assert bad not in text, bad
    assert not os.path.exists(fc["out"])
    assert fx["sk_main"] == 0, "the dry-run fitted k-means (%d calls)" % fx["sk_main"]
    res, text, fc, fx = _run(td, "UH")
    assert res == 0 and fx["sk_main"] == 40, fx["sk_main"]
    return True


def st_refusals(factory):
    def idp(name, key, val):
        return lambda fc: fc.update(ident={**fc["ident"], name: dict(fc["ident"][name], **{key: val})})

    def bad_items(W, trees):
        C = W["CS"]["clinc"]
        ev = np.nonzero(C.kept & ~C.oos & (C.side == SS.EVAL))[0]
        return [("C-AN", C.ids[i], "n00000004", "x") for i in ev]
    cases = [
        (dict(patch=lambda fc: fc.update(sid={**fc["sid"], "C-AN": "other"})), "IDENTITY: C-AN Snapshot ID sid_C-AN != S1's other"),
        (dict(patch=lambda fc: fc.update(leaves={**fc["leaves"], "M-AN": 9})), "IDENTITY: M-AN has 8 leaves, S1 printed 9"),
        (dict(patch=lambda fc: fc.update(s1_sha={**fc["s1_sha"], "outcome": "0" * 64})), "IDENTITY: S1's outcome"),
        (dict(patch=lambda fc: fc.update(s1_sha={**fc["s1_sha"], "items": "0" * 64})), "IDENTITY: S1's items"),
        (dict(patch=lambda fc: fc.update(s1_lines=fc["s1_lines"] + ("a line S1 never printed",))), "lacks the quoted line"),
        (dict(patch=idp("M-AN", "dfd", "+9.99999")), "IDENTITY: M-AN ['dfd']"),
        (dict(patch=idp("C-AN", "d1", "+9.99999")), "IDENTITY: C-AN ['d1']"),
        (dict(patch=idp("C-AN", "delta_c", "9.99999")), "IDENTITY: C-AN ['delta_c']"),
        (dict(patch=lambda fc: fc.update(n_reg={**fc["n_reg"], "clinc": (fc["n_reg"]["clinc"][0] + 1, fc["n_reg"]["clinc"][1])})),
         "DENOMINATOR: CLINC EVAL 114"),
        (dict(patch=lambda fc: fc.update(n_reg={**fc["n_reg"], "massive": (118, 99)})), "DENOMINATOR: MASSIVE EVAL 118 / 98"),
        (dict(items=bad_items), "IDENTITY: C-AN flat leaves differ from s1_items.csv"),
        (dict(heavy=lambda: ['"java.exe","4242"']), "a foreign heavy process runs"),
        (dict(graph_variant="offlabel"), "label 'Epsilon' is not a declared TRAIN coarse class"),
        (dict(drop_class="delta"), "anchor n00000006 label 'Delta' is not a declared TRAIN coarse class"),
        (dict(graph_variant="dupe"), "do not cover the TRAIN coarse classes"),
        (dict(graph_variant="multiparent"), "multi-parent nodes"),
    ]
    for kw, needle in cases:
        td = factory()
        res, text, fc, fx = _run(td, "UH", expect_refusal=needle, **kw)
        assert not os.path.exists(fc["out"]), needle
    # descent not accepted: the diagnostics name another leaf for every GATE text
    td = factory()
    saved = S1._write_diag
    try:
        S1._write_diag = lambda path, texts, tops: saved(path, texts, ["n00000009"] * len(tops))
        _run(td, "UH", expect_refusal="descent port is NOT ACCEPTED on GATE")
    finally:
        S1._write_diag = saved
    # this script's filer cross-checked against S1.fine_correct_flat on A
    td = factory()
    saved_fcf = S1.fine_correct_flat

    def flip(A, idx):             # only compute_corpus's call is flipped (S1.t_c8's identity call is left intact)
        ok, fl = saved_fcf(A, idx)
        if A["name"] == "C-AN" and sys._getframe(1).f_code.co_name == "compute_corpus":
            ok = ok.copy()
            ok[0] = 1.0 - ok[0]
        return ok, fl
    try:
        S1.fine_correct_flat = flip
        _run(td, "UH", expect_refusal="C-AN: this script's filer disagrees with S1.fine_correct_flat on A")
    finally:
        S1.fine_correct_flat = saved_fcf
    # the TRAIN-ONLY guard: an EVAL row in a refit fit set refuses (S1.fit_idx)
    td = factory()
    saved_fit = S1.fit_idx

    def leaky(C, side_arr, idx, allowed, what):
        if "A-refit" in what:
            idx = np.r_[idx, np.nonzero(side_arr == SS.EVAL)[0][:1]]
        return saved_fit(C, side_arr, idx, allowed, what)
    try:
        S1.fit_idx = leaky
        _run(td, "UH", expect_refusal="TRAIN-ONLY")
    finally:
        S1.fit_idx = saved_fit
    # write-once is checked BEFORE any read: an existing outcome refuses with the POOL line only
    td = factory()
    os.makedirs(os.path.join(td, "out"))
    open(os.path.join(td, "out", "fitset_intent_outcome.txt"), "w").close()
    res, text, fc, fx = _run(td, "UH", expect_refusal="exists; the outcome is write-once",
                             heavy=lambda: (_ for _ in ()).throw(AssertionError("the java probe ran before the write-once check")))
    assert len(text.splitlines()) == 1 and text.startswith("POOL n/a"), text
    return True


def _synth(dm=0.02, lom=0.01, him=0.03, sm=0.01, dc=0.0, loc=-0.01, hic=0.01, sc=0.01, discm=0.05, discc=0.05):
    def r(corpus, name, d, lo, hi, s, disc):
        st = dict(d=d, lo=lo, hi=hi, se=0.004, deff=1.05, kish=1.0, n=1000, G=990, n_eff=950.0, mde=0.0112, disc=disc, seed=1)
        return dict(corpus=corpus, name=name, st=st, spread=s)
    Rs = [r("massive", "M-AN", dm, lom, him, sm, discm), r("clinc", "C-AN", dc, loc, hic, sc, discc)]
    return "\n".join(verdict_lines(Rs) + prediction_lines(Rs))


def st_branches():
    L = _synth()
    _need(L, "FI1 MASSIVE: HELD (the class-pure leaf-mean refit files EVAL fine intents better than M-AN as built): D +0.0200, 95%"
             " [+0.0100, +0.0300], spread_K 0.0100 (exact 0.010000); interval wholly above 0 and D > spread_K",
          "FI1 CLINC: UNDETERMINED: D +0.0000", "READING: BEYOND-MMLU (FI1 HELD on MASSIVE)", "F-FI: DOES NOT FIRE (FI1 HELD on MASSIVE)",
          "PREDICTION P1 D MASSIVE +0.005 [-0.005, +0.020]: observed +0.0200 -> HELD",
          "PREDICTION P1 D CLINC +0.005 [-0.005, +0.020]: observed +0.0000 -> HELD",
          "PREDICTION P2 discordance MASSIVE 0.03 [0.01, 0.08]: observed 0.0500 -> HELD")
    # first corpus not HELD, second HELD: the READING reads both corpora
    L = _synth(dm=0.0, lom=-0.01, him=0.01, dc=0.03, loc=0.02, hic=0.04)
    _need(L, "FI1 CLINC: HELD", "READING: BEYOND-MMLU (FI1 HELD on CLINC)", "F-FI: DOES NOT FIRE (FI1 HELD on CLINC)")
    # both HELD
    L = _synth(dc=0.03, loc=0.02, hic=0.04)
    _need(L, "READING: BEYOND-MMLU (FI1 HELD on MASSIVE and CLINC)", "F-FI: DOES NOT FIRE (FI1 HELD on MASSIVE and CLINC)")
    # REVERSED needs both clauses; REVERSED + HELD reads BEYOND
    L = _synth(dm=-0.02, lom=-0.03, him=-0.01, dc=0.03, loc=0.02, hic=0.04)
    _need(L, "FI1 MASSIVE: REVERSED (M-AN as built files EVAL fine intents better than its class-pure refit): D -0.0200",
          "interval wholly below 0 and D < -spread_K", "READING: BEYOND-MMLU (FI1 HELD on CLINC)")
    L = _synth(dm=-0.005, lom=-0.03, him=-0.001)
    _need(L, "FI1 MASSIVE: UNDETERMINED: D -0.0050", "interval wholly below 0: yes; D < -spread_K: no")
    # the spread conjunct at equality: D = spread_K -> UNDETERMINED; just above -> HELD
    _need(_synth(dm=0.01, lom=0.004, him=0.02, sm=0.01), "FI1 MASSIVE: UNDETERMINED: D +0.0100", "D > spread_K: no")
    _need(_synth(dm=0.0101, lom=0.004, him=0.02, sm=0.01), "FI1 MASSIVE: HELD")
    # lo exactly 0 -> not wholly above 0 (UNDETERMINED); hi exactly 0 -> not wholly below 0
    _need(_synth(dm=0.02, lom=0.0, him=0.03), "FI1 MASSIVE: UNDETERMINED", "interval wholly above 0: no")
    _need(_synth(dm=-0.02, lom=-0.03, him=0.0), "FI1 MASSIVE: UNDETERMINED", "interval wholly below 0: no")
    # NOT-SHOWN and F-FI fire together (both corpora not HELD; one REVERSED, one UNDETERMINED)
    L = _synth(dm=-0.02, lom=-0.03, him=-0.01)
    _need(L, "READING: NOT-SHOWN (FI1 HELD on neither corpus: MASSIVE REVERSED, CLINC UNDETERMINED)",
          "F-FI: FIRES (FI1 UNDETERMINED or REVERSED on both corpora: MASSIVE REVERSED, CLINC UNDETERMINED)",
          "PREDICTION P1 FI1 HELD on at least one corpus (p 0.25): event DID NOT OCCUR, Brier 0.0625")
    _need(_synth(), "PREDICTION P1 FI1 HELD on at least one corpus (p 0.25): event OCCURRED, Brier 0.5625")
    # prediction bands inclusive at both ends; outside -> FAILED; NaN -> NOT SCORED
    _need(_synth(dm=-0.005, lom=-0.01, him=0.0, discm=0.01, discc=0.08), "PREDICTION P1 D MASSIVE +0.005 [-0.005, +0.020]: observed -0.0050 -> HELD",
          "PREDICTION P2 discordance MASSIVE 0.03 [0.01, 0.08]: observed 0.0100 -> HELD",
          "PREDICTION P2 discordance CLINC 0.03 [0.01, 0.08]: observed 0.0800 -> HELD")
    _need(_synth(dm=0.020, lom=0.01, him=0.03), "PREDICTION P1 D MASSIVE +0.005 [-0.005, +0.020]: observed +0.0200 -> HELD")
    _need(_synth(dm=0.0201, lom=0.01, him=0.03, discm=0.0801, discc=0.0099), "observed +0.0201 -> FAILED",
          "PREDICTION P2 discordance MASSIVE 0.03 [0.01, 0.08]: observed 0.0801 -> FAILED",
          "PREDICTION P2 discordance CLINC 0.03 [0.01, 0.08]: observed 0.0099 -> FAILED")
    _need(_synth(dm=float("nan"), lom=float("nan"), him=float("nan"), discm=float("nan")),
          "PREDICTION P1 D MASSIVE +0.005 [-0.005, +0.020]: observed none -> NOT SCORED (no estimate)",
          "PREDICTION P2 discordance MASSIVE 0.03 [0.01, 0.08]: observed none -> NOT SCORED (no estimate)")
    return True


def st_reg():
    """The constants of record agree with the quoted S1 lines (one source of truth checked)."""
    for n in ARMS_AN:
        assert any(("%s snapshot %s leaves %d " % (n, REG["sid"][n], REG["leaves"][n])) in ln for ln in REG["s1_lines"]), n
        assert any(("DESCRIPTIVE %s: T-C1 D1 %s [EQUIVALENT]; T-C8 D_fd %s " % (n, REG["ident"][n]["d1"], REG["ident"][n]["dfd"])) in ln
                   for ln in REG["s1_lines"]), n
        assert any(ln.startswith("%s delta_c %s " % (n, REG["ident"][n]["delta_c"])) for ln in REG["s1_lines"]), n
    assert REG["n_reg"] == {"massive": (4946, 4923), "clinc": (6672, 6672)}
    assert SUPPORT["massive"]["se"] == 0.00357 and SUPPORT["clinc"]["se"] == 0.00308 and SUPPORT["massive"]["neff"] == 4702
    return True


CASES = (("e2e_UH", "fixture UH --run: UNDETERMINED by the spread conjunct / HELD; BEYOND-MMLU; write-once", "tmp"),
         ("e2e_RZ", "fixture RZ --run: REVERSED / zero; NOT-SHOWN; F-FI FIRES; s1_items rows compared", "tmp"),
         ("dry_run", "--dry-run: pins, denominators, TRAIN-side bookkeeping; no statistic, no file", "tmp"),
         ("refusals", "every refusal (identity, record, denominators, anchors, guard, java, write-once first)", "factory"),
         ("branches", "every FI1 / READING / F-FI / prediction branch and boundary", "plain"),
         ("reg", "constants of record vs the quoted S1 lines", "plain"))
_FN = {"e2e_UH": st_e2e_UH, "e2e_RZ": st_e2e_RZ, "dry_run": st_dry_run, "refusals": st_refusals, "branches": st_branches, "reg": st_reg}


def selftest(only=None, quiet=False):
    import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="fi_")
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
                    print("  FAIL %-9s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:600]))
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
            print("  %-62s tests %-18s original %-4s control %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "SURVIVED (as it must)" if control_ok else "KILLED (harness broken)"))
            continue
        killed += int(k)
        print("  %-62s tests %-18s original %-4s mutant %-8s %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:90]), flush=True)
    n_real = sum(1 for m in MUTANTS if not m[0].startswith("M00"))
    print("MUTANTS: %d of %d KILLED; control %s" % (killed, n_real, "survived" if control_ok else "KILLED"))
    return 0 if killed == n_real and control_ok else 1


def _exec_selftest(src, tests):
    ns = {"__name__": "fitset_intent_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


NL = chr(10)
MUTANTS = (
    ("M00 control (no-op edit)", [("def v_fi1(r):", "def v_fi1(r):")], ["branches", "e2e_UH"]),
    ("M01 refit fit sets from GATE (wrong side), guard kept", [('    C, X, T, tr = A["C"], A["X"], A["T"], A["tr"]' + NL + "    gt = []",
                                                                 '    C, X, T, tr = A["C"], A["X"], A["T"], A["ga"]' + NL + "    gt = []")], ["e2e_UH"]),
    ("M02 refit fit sets from GATE with the guard widened", [('    C, X, T, tr = A["C"], A["X"], A["T"], A["tr"]' + NL + "    gt = []",
                                                             '    C, X, T, tr = A["C"], A["X"], A["T"], A["ga"]' + NL + "    gt = []"),
                                                            ('(SS.TRAIN,), "%s A-refit', '(SS.TRAIN, SS.GATE), "%s A-refit')], ["e2e_UH"]),
    ("M03 fit set = routed members of the anchor, not the declared class", [
        ("        pos = np.flatnonzero(C.coarse[tr] == cl)",
         '        pos = np.flatnonzero(np.array([anc["leaf_anchor"][T["leaves"][j]] for j in A["fl_tr"]]) == a)')], ["e2e_UH"]),
    ("M04 refit cells named from EVAL", [("    names_r = name_cells(A, Cr)", '    names_r = name_cells(dict(A, tr=S1.eval_rows(A)), Cr)')], ["e2e_UH"]),
    ("M05 FI1 spread conjunct dropped", [('r["st"]["hi"], r["spread"])', 'r["st"]["hi"], 0.0)')], ["e2e_UH"]),
    ("M06 spread_K min<->max", [("    spread = max(pk) - min(pk)" + NL + "    st = stat(", "    spread = min(pk) - max(pk)" + NL + "    st = stat(")], ["e2e_UH"]),
    ("M07 spread_K over seeds 0-19", [("    for s in SEEDS5:" + NL + '        Cm = A["km"][s]', "    for s in range(20):" + NL + '        Cm = A["km"][s]')],
     ["e2e_UH"]),
    ("M08 spread_K from seeds 1-5", [('        Cm = A["km"][s]' + NL + "        pk.append", '        Cm = A["km"][s + 1]' + NL + "        pk.append")], ["e2e_UH"]),
    ("M09 D sign reversed", [("    st = stat(okR - okA, C.comp[ev], SEED_FI + k)", "    st = stat(okA - okR, C.comp[ev], SEED_FI + k)")], ["e2e_UH"]),
    ("M10 bootstrap over items, components ignored", [("    st = stat(okR - okA, C.comp[ev], SEED_FI + k)",
                                                       "    st = stat(okR - okA, np.arange(len(ev)), SEED_FI + k)")], ["e2e_UH"]),
    ("M11 one bootstrap seed for both corpora", [("    st = stat(okR - okA, C.comp[ev], SEED_FI + k)", "    st = stat(okR - okA, C.comp[ev], SEED_FI)")],
     ["e2e_UH"]),
    ("M12 discordance = mean D", [("disc=float(np.mean(diff != 0))", "disc=float(np.mean(diff))")], ["e2e_UH"]),
    ("M13 DEFF inverted", [("    deff = se ** 2 / var_iid if var_iid > 0", "    deff = var_iid / se ** 2 if var_iid > 0")], ["e2e_UH"]),
    ("M14 READING needs both corpora HELD", [('    reading = "BEYOND-MMLU" if held else', '    reading = "BEYOND-MMLU" if len(held) == 2 else')],
     ["e2e_UH", "branches"]),
    ("M15 F-FI fires iff any corpus is not HELD", [("    fires = bool(all(", "    fires = bool(any(")], ["e2e_UH", "branches"]),
    ("M16 F-FI on the first corpus only", [('all(words[c] in ("UNDETERMINED", "REVERSED") for c in words)',
                                            'all(words[c] in ("UNDETERMINED", "REVERSED") for c in ["massive"])')], ["e2e_UH", "branches"]),
    ("M17 READING from the first corpus only", [('    held = [c for c in ("massive", "clinc") if', '    held = [c for c in ("massive",) if')],
     ["e2e_UH", "branches"]),
    ("M18 F-FI silent when it does not fire (skip path)", [
        ("""        L.append("F-FI: DOES NOT FIRE (FI1 HELD on %s): a HELD extends FITSET-FAITHFUL's sentence to that known-answer corpus\"""" + NL
         + """                 % " and ".join(UP[c] for c in held))""", "        pass")], ["e2e_UH", "branches"]),
    ("M19 write-once removed (check and mode x)", [("    if a.run and os.path.lexists(outp):", "    if False:"),
                                                   ('    with open(outp, "x"', '    with open(outp, "w"')], ["e2e_UH"]),
    ("M20 write-once check removed (mode x kept)", [("    if a.run and os.path.lexists(outp):", "    if False:")], ["e2e_UH"]),
    ("M21 write-once checked only after the reads", [
        ("    if a.run and os.path.lexists(outp):" + NL + '        refuse("%s exists; the outcome is write-once" % outp)' + NL + "    heavy", "    heavy"),
        ('    ld["recheck"]()' + NL, '    ld["recheck"]()' + NL + "    if os.path.lexists(outp):" + NL + '        refuse("%s exists; the outcome is write-once" % outp)' + NL)],
     ["refusals"]),
    ("M22 java probe ignored", [("    if heavy:" + NL + '        refuse("a foreign heavy', "    if False:" + NL + '        refuse("a foreign heavy')], ["refusals"]),
    ("M23 identity constants not enforced", [("    if bad:" + NL + '        refuse("IDENTITY: %s %s reproduced', "    if False:" + NL + '        refuse("IDENTITY: %s %s reproduced')],
     ["refusals"]),
    ("M24 Snapshot ID not checked", [('    if sid != c["sid"][name]:', "    if False:")], ["refusals"]),
    ("M25 leaf count not checked", [('    if len(T["leaves"]) != c["leaves"][name]:', "    if False:")], ["refusals"]),
    ("M26 S1 record sha not checked", [('        if sha[k] != c["s1_sha"][k]:', "        if False:")], ["refusals"]),
    ("M27 S1 quoted lines not checked", [("        if ln not in txt:", "        if False:")], ["refusals"]),
    ("M28 s1_items AN rows not compared", [("        if diff or set(rows) != set(mine):", "        if False:")], ["refusals"]),
    ("M29 descent acceptance not required", [('    if not A["accept"]["accepted"]:', "    if False:")], ["refusals"]),
    ("M30 registered denominators not enforced", [('        if tuple(cen[corpus]) != tuple(c["n_reg"][corpus]):', "        if False:")], ["refusals"]),
    ("M31 off-class anchor label admitted", [("        if lab not in key:", "        if False:")], ["refusals"]),
    ("M32 one-to-one anchor cover not checked", [('    if len(set(cls)) != len(cls) or set(cls) != set(classes):', "    if False:")], ["refusals"]),
    ("M33 multi-parent graph admitted", [('    if T["multi_parent"]:', "    if False:")], ["refusals"]),
    ("M34 unsplit anchors keep their vmfMu (boundary)", [
        ("    Cm, _ca, info = FF.refit_cells(o, Aff)" + NL,
         "    Cm, _ca, info = FF.refit_cells(o, Aff)" + NL
         + '    Cm = np.vstack([T["mu"][u] if anc["ka"][anc["leaf_anchor"][u]] == 1 else Cm[j] for j, u in enumerate(T["leaves"])])' + NL)],
     ["e2e_UH"]),
    ("M35 k-means cells named from EVAL", [("        pk.append(float(file_eval(A, Cm, name_cells(A, Cm)).mean()))",
                                            '        pk.append(float(file_eval(A, Cm, name_cells(dict(A, tr=S1.eval_rows(A)), Cm)).mean()))')],
     ["e2e_UH"]),
    ("M36 per-anchor rows by filed leaf, not gold class", [
        ("        m = C.coarse[ev] == cl" + NL,
         '        m = np.array([anc["leaf_anchor"][A["T"]["leaves"][j]] == a for j in S1.flat_leaf(A["T"], A["X"][ev])])' + NL)], ["e2e_UH"]),
    ("M37 per-anchor Delta sign reversed", [('_f(p["pr"] - p["pa"], "%+.4f")', '_f(p["pa"] - p["pr"], "%+.4f")')], ["e2e_UH"]),
    ("M38 registered support of the other corpus", [('    st, sp = r["st"], SUPPORT[r["corpus"]]',
                                                     '    st, sp = r["st"], SUPPORT["clinc" if r["corpus"] == "massive" else "massive"]')], ["e2e_UH"]),
    ("M39 prediction bands exclusive", [('    return "HELD" if band[0] <= x <= band[1] else "FAILED"', '    return "HELD" if band[0] < x < band[1] else "FAILED"')],
     ["branches"]),
    ("M40 a NaN prediction scored", [("    if x is None or x != x:", "    if x is None:")], ["branches"]),
    ("M41 Brier against p 0.75", [("(P_HELD_ANY - (1.0 if ev else 0.0)) ** 2", "(1 - P_HELD_ANY - (1.0 if ev else 0.0)) ** 2")], ["e2e_UH", "branches"]),
    ("M42 P2 scored on D, not discordance", [('        b = in_band(r["st"]["disc"], P2_BAND)', '        b = in_band(r["st"]["d"], P2_BAND)')], ["e2e_UH", "branches"]),
    ("M43 dry-run reads EVAL and prints a statistic", [
        ("    pl = pins_lines(ld, s1)" + NL + "    if a.dry_run:" + NL,
         "    pl = pins_lines(ld, s1)" + NL + '    S1.STATE["gate_frozen"] = True' + NL + "    if a.dry_run:" + NL
         + '        out("P(A) %.4f" % S1.fine_correct_flat(arms["M-AN"], S1.eval_rows(arms["M-AN"]))[0].mean())' + NL)], ["dry_run"]),
    ("M44 dry-run fits k-means", [("need_km=bool(a.run))", "need_km=True)")], ["dry_run"]),
    ("M45 filer cross-check against S1 removed", [("    if not np.array_equal(okA, okA_s1.astype(np.int64)):", "    if False:")], ["refusals"]),
    ("M46 FI1 filed on TRAIN (wrong population)", [("    ev = S1.eval_rows(A)" + NL + '    lab = np.argmax(A["X"][ev] @ Cm.T, axis=1)',
                                                    '    ev = A["tr"]' + NL + '    lab = np.argmax(A["X"][ev] @ Cm.T, axis=1)')], ["e2e_UH"]),
    ("M47 no-TRAIN refit leaf dropped (zero mean), not kept at vmfMu", [
        ("    Cm, _ca, info = FF.refit_cells(o, Aff)" + NL,
         "    Cm, _ca, info = FF.refit_cells(o, Aff)" + NL + '    Cm = np.vstack([Cm[j] * (0.0 if u in info["none"] else 1.0) for j, u in enumerate(T["leaves"])])' + NL)],
     ["e2e_UH"]),
    ("M48 the anchor of a leaf = the leaf itself (depth-1 walk removed)", [
        ('        while v is not None and T["tparent"].get(v) != root:', "        while False:")], ["e2e_UH"]),
    ("M49 F-FI FIRES line omitted (skip path)", [('    if fires:' + NL + '        L.append("F-FI: FIRES', '    if fires:' + NL + '        pass' + NL + '    if False:' + NL + '        L.append("F-FI: FIRES')],
     ["e2e_RZ"]),
    ("M50 NOT-SHOWN line omitted (skip path)", [('        L.append("READING: NOT-SHOWN', '        pass' + NL + '        0 and L.append("READING: NOT-SHOWN')], ["e2e_RZ"]),
)

if __name__ == "__main__":
    sys.exit(main())
